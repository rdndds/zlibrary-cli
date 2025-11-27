"""
HTTP Client for Z-Library Search Application

Centralizes session management, HTTP operations, and retry logic.
"""
import time
import requests
from typing import Optional, Dict, Any
from requests.cookies import RequestsCookieJar

from zlibrary.config import Config
from zlibrary.auth import AuthManager
from zlibrary.logging_config import get_logger
from zlibrary.exceptions import (
    NetworkException, 
    ConnectionException, 
    TimeoutException,
    AuthenticationException
)
from zlibrary.constants import (
    DEFAULT_HEADERS,
    RETRY_STATUS_CODES,
    ConfigKeys
)


class ZLibraryHTTPClient:
    """
    Centralized HTTP client for Z-Library operations.
    
    Handles session management, authentication, retry logic,
    and common HTTP concerns in a single place.
    """
    
    def __init__(self, config: Config, auth_manager: AuthManager):
        """
        Initialize HTTP client with configuration and auth manager.
        
        Args:
            config: Configuration instance
            auth_manager: Authentication manager instance
        """
        self.config = config
        self.auth_manager = auth_manager
        self.logger = get_logger(__name__)
        self._session: Optional[requests.Session] = None
        
    def _get_session(self) -> requests.Session:
        """
        Get or create HTTP session with cookies and configuration.
        
        Returns:
            Configured requests.Session instance
        """
        if self._session is None:
            self._session = requests.Session()
            
            # Load and set cookies
            try:
                cookies = self.auth_manager.load_cookies_from_file(
                    self.config.get(ConfigKeys.COOKIES_FILE)
                )
                self._session.cookies = cookies
                self.logger.debug(f"Loaded {len(cookies)} cookies into session")
            except AuthenticationException as e:
                self.logger.error(f"Failed to load cookies: {e}")
                raise
                
        return self._session
    
    def _get_headers(self, additional_headers: Optional[Dict[str, str]] = None) -> Dict[str, str]:
        """
        Build request headers with user agent and optional additions.
        
        Args:
            additional_headers: Optional additional headers to merge
            
        Returns:
            Complete headers dictionary
        """
        headers = DEFAULT_HEADERS.copy()
        headers['User-Agent'] = self.config.get(ConfigKeys.USER_AGENT)
        
        if additional_headers:
            headers.update(additional_headers)
            
        return headers
    
    def get(
        self, 
        url: str, 
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[int] = None,
        allow_redirects: bool = True
    ) -> requests.Response:
        """
        Perform GET request with retry logic.
        
        Args:
            url: URL to request
            params: Optional query parameters
            headers: Optional additional headers
            timeout: Request timeout (uses config default if None)
            allow_redirects: Whether to follow redirects
            
        Returns:
            Response object
            
        Raises:
            NetworkException: On network errors
            TimeoutException: On timeout
            ConnectionException: On connection errors
        """
        session = self._get_session()
        request_headers = self._get_headers(headers)
        request_timeout = timeout or self.config.get(ConfigKeys.REQUEST_TIMEOUT)
        max_retries = self.config.get(ConfigKeys.MAX_RETRIES)
        retry_delay = self.config.get(ConfigKeys.RETRY_DELAY)
        
        for attempt in range(max_retries):
            try:
                self.logger.debug(
                    f"GET request to {url} (attempt {attempt + 1}/{max_retries})"
                )
                
                response = session.get(
                    url,
                    params=params,
                    headers=request_headers,
                    timeout=request_timeout,
                    allow_redirects=allow_redirects
                )
                
                # Check if we should retry based on status code
                if response.status_code in RETRY_STATUS_CODES:
                    self.logger.warning(
                        f"Received status {response.status_code}, "
                        f"retrying in {retry_delay}s..."
                    )
                    if attempt < max_retries - 1:
                        time.sleep(retry_delay * (attempt + 1))  # Exponential backoff
                        continue
                
                # Log successful request
                self.logger.debug(
                    f"Request successful: {response.status_code} from {url}"
                )
                return response
                
            except requests.exceptions.Timeout as e:
                self.logger.warning(f"Request timeout on attempt {attempt + 1}: {e}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay * (attempt + 1))
                    continue
                raise TimeoutException(
                    f"Request timed out after {max_retries} attempts: {url}"
                ) from e
                
            except requests.exceptions.ConnectionError as e:
                self.logger.warning(f"Connection error on attempt {attempt + 1}: {e}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay * (attempt + 1))
                    continue
                raise ConnectionException(
                    f"Connection failed after {max_retries} attempts: {url}"
                ) from e
                
            except requests.exceptions.RequestException as e:
                self.logger.error(f"Request error: {e}")
                raise NetworkException(f"Request failed: {url}") from e
        
        # Should not reach here, but just in case
        raise NetworkException(f"Failed to complete request after {max_retries} attempts")
    
    def post(
        self,
        url: str,
        data: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[int] = None
    ) -> requests.Response:
        """
        Perform POST request with retry logic.
        
        Args:
            url: URL to request
            data: Form data to send
            json: JSON data to send
            headers: Optional additional headers
            timeout: Request timeout (uses config default if None)
            
        Returns:
            Response object
            
        Raises:
            NetworkException: On network errors
        """
        session = self._get_session()
        request_headers = self._get_headers(headers)
        request_timeout = timeout or self.config.get(ConfigKeys.REQUEST_TIMEOUT)
        max_retries = self.config.get(ConfigKeys.MAX_RETRIES)
        retry_delay = self.config.get(ConfigKeys.RETRY_DELAY)
        
        for attempt in range(max_retries):
            try:
                self.logger.debug(
                    f"POST request to {url} (attempt {attempt + 1}/{max_retries})"
                )
                
                response = session.post(
                    url,
                    data=data,
                    json=json,
                    headers=request_headers,
                    timeout=request_timeout
                )
                
                if response.status_code in RETRY_STATUS_CODES:
                    if attempt < max_retries - 1:
                        time.sleep(retry_delay * (attempt + 1))
                        continue
                
                return response
                
            except requests.exceptions.RequestException as e:
                self.logger.error(f"POST request error on attempt {attempt + 1}: {e}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay * (attempt + 1))
                    continue
                raise NetworkException(f"POST request failed: {url}") from e
        
        raise NetworkException(f"Failed to complete POST request after {max_retries} attempts")
    
    def download_file(
        self,
        url: str,
        destination: str,
        headers: Optional[Dict[str, str]] = None,
        chunk_size: int = 8192
    ) -> bool:
        """
        Download a file with streaming and progress tracking.
        
        Args:
            url: URL to download from
            destination: Local file path to save to
            headers: Optional additional headers
            chunk_size: Size of chunks to download
            
        Returns:
            True if successful, False otherwise
            
        Raises:
            NetworkException: On download errors
        """
        session = self._get_session()
        request_headers = self._get_headers(headers)
        
        try:
            self.logger.info(f"Starting file download from {url}")
            
            response = session.get(
                url,
                headers=request_headers,
                stream=True,
                timeout=self.config.get(ConfigKeys.REQUEST_TIMEOUT)
            )
            response.raise_for_status()
            
            # Get file size if available
            total_size = int(response.headers.get('content-length', 0))
            
            with open(destination, 'wb') as f:
                downloaded = 0
                for chunk in response.iter_content(chunk_size=chunk_size):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        
                        # Log progress for large files
                        if total_size > 0 and downloaded % (chunk_size * 100) == 0:
                            progress = (downloaded / total_size) * 100
                            self.logger.debug(f"Download progress: {progress:.1f}%")
            
            self.logger.info(f"File downloaded successfully to {destination}")
            return True
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"File download failed: {e}")
            raise NetworkException(f"Failed to download file from {url}") from e
    
    def close(self):
        """Close the HTTP session and release resources."""
        if self._session:
            self._session.close()
            self._session = None
            self.logger.debug("HTTP session closed")
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
