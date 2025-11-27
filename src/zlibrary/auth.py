"""
Authentication and cookie handling for Z-Library Search Application
"""
import os
from pathlib import Path
from requests.cookies import RequestsCookieJar
from typing import Optional, Tuple
import requests

from zlibrary.logging_config import get_logger
from zlibrary.exceptions import AuthenticationException


class AuthManager:
    """Handles cookie loading and authentication"""

    LOGIN_URL = "https://z-library.sk/login"
    RPC_URL = "https://z-library.sk/rpc.php"

    def __init__(self, cookies_file: str = 'cookies.txt'):
        self.cookies_file = cookies_file
        self.logger = get_logger(__name__)

    def load_cookies_from_file(self, cookie_file_path: Optional[str] = None) -> RequestsCookieJar:
        """
        Load cookies from Netscape cookie file format
        Checks current directory first, then falls back to configured path

        Args:
            cookie_file_path: Path to cookies file (defaults to instance value)

        Returns:
            RequestsCookieJar: Loaded cookies
        """
        if cookie_file_path is None:
            cookie_file_path = self.cookies_file

        # Check current working directory first
        cwd_cookies = Path.cwd() / 'cookies.txt'
        if cwd_cookies.exists():
            cookie_file_path = str(cwd_cookies)
            self.logger.debug(f"Found cookies.txt in current directory: {cookie_file_path}")
        
        self.logger.debug(f"Loading cookies from file: {cookie_file_path}")

        try:
            cookie_jar = RequestsCookieJar()

            with open(cookie_file_path, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    if line.startswith('#') or line.strip() == '':
                        continue

                    fields = line.strip().split('\t')
                    if len(fields) >= 7:
                        domain, flag, path, secure, expiration, name, value = fields
                        cookie_jar.set(name, value, domain=domain.lstrip('.'), path=path)
                    else:
                        self.logger.warning(f"Invalid cookie format in {cookie_file_path} at line {line_num}")

            self.logger.info(f"Successfully loaded {len(cookie_jar)} cookies from {cookie_file_path}")
            return cookie_jar
        except FileNotFoundError:
            self.logger.error(f"Cookies file not found: {cookie_file_path}")
            raise AuthenticationException(f"Authentication failed: cookies file not found at {cookie_file_path}")
        except Exception as e:
            self.logger.error(f"Error loading cookies from {cookie_file_path}: {str(e)}")
            raise AuthenticationException(f"Authentication failed: error loading cookies - {str(e)}")

    def login_with_credentials(self, email: str, password: str) -> Tuple[str, str]:
        """
        Login with email and password to get session cookies.
        
        Args:
            email: User email
            password: User password
            
        Returns:
            Tuple of (sid, user_id) cookie values
            
        Raises:
            AuthenticationException: If login fails
        """
        self.logger.info(f"Attempting login for email: {email}")
        
        session = requests.Session()
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Referer': self.LOGIN_URL,
            'Origin': 'https://z-library.sk'
        })
        
        try:
            # Step 1: Get initial session cookies
            self.logger.debug(f"Getting initial session from {self.LOGIN_URL}")
            session.get(self.LOGIN_URL, timeout=30)
            
            # Step 2: Submit login credentials to RPC endpoint
            login_data = {
                'functionName': 'login',
                'email': email,
                'password': password,
                'site_mode': 'books',
                'action': 'login',
                'redirectUrl': ''
            }
            
            self.logger.debug(f"Submitting credentials to {self.RPC_URL}")
            response = session.post(
                self.RPC_URL,
                data=login_data,
                timeout=30,
                allow_redirects=True
            )
            
            # Step 3: Check for errors in response
            if response.status_code != 200:
                raise AuthenticationException(f"Login failed with status code: {response.status_code}")
            
            response_text = response.text.lower()
            if 'incorrect email or password' in response_text:
                raise AuthenticationException("Incorrect email or password")
            
            if 'error' in response_text and 'alert' in response_text:
                # Try to extract error message
                import re
                match = re.search(r'alert\(["\']([^"\']+)["\']\)', response.text)
                if match:
                    raise AuthenticationException(f"Login failed: {match.group(1)}")
                raise AuthenticationException("Login failed with unknown error")
            
            # Step 4: Extract authentication cookies
            # Z-Library uses different cookie names: remix_userkey and remix_userid
            sid = session.cookies.get('remix_userkey') or session.cookies.get('sid')
            user_id = session.cookies.get('remix_userid') or session.cookies.get('user_id')
            
            if not sid or not user_id:
                self.logger.error(f"Login response did not contain expected cookies. Available cookies: {list(session.cookies.keys())}")
                raise AuthenticationException("Login failed: authentication cookies not received")
            
            self.logger.info(f"Login successful for user ID: {user_id}")
            return sid, user_id
            
        except requests.RequestException as e:
            self.logger.error(f"Network error during login: {str(e)}")
            raise AuthenticationException(f"Login failed due to network error: {str(e)}")
        except AuthenticationException:
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error during login: {str(e)}")
            raise AuthenticationException(f"Login failed: {str(e)}")

    def save_cookies_to_file(self, sid: str, user_id: str, cookie_file_path: Optional[str] = None):
        """
        Save authentication cookies to Netscape format file.
        
        Args:
            sid: Session ID cookie value
            user_id: User ID cookie value
            cookie_file_path: Path to save cookies (defaults to instance value)
        """
        if cookie_file_path is None:
            cookie_file_path = self.cookies_file
        
        # Ensure directory exists
        cookie_path = Path(cookie_file_path)
        cookie_path.parent.mkdir(parents=True, exist_ok=True)
        
        self.logger.debug(f"Saving cookies to {cookie_file_path}")
        
        try:
            with open(cookie_file_path, 'w', encoding='utf-8') as f:
                f.write("# Netscape HTTP Cookie File\n")
                f.write("# This file was generated by zlibrary-cli\n")
                f.write("# Edit at your own risk.\n\n")
                
                # Write cookies in Netscape format
                # Format: domain	flag	path	secure	expiration	name	value
                # Write both new (remix_*) and old (sid/user_id) formats for compatibility
                f.write(f".z-library.sk\tTRUE\t/\tFALSE\t0\tremix_userkey\t{sid}\n")
                f.write(f".z-library.sk\tTRUE\t/\tFALSE\t0\tremix_userid\t{user_id}\n")
                f.write(f".z-library.sk\tTRUE\t/\tFALSE\t0\tsid\t{sid}\n")
                f.write(f".z-library.sk\tTRUE\t/\tFALSE\t0\tuser_id\t{user_id}\n")
            
            self.logger.info(f"Cookies saved successfully to {cookie_file_path}")
            
        except Exception as e:
            self.logger.error(f"Error saving cookies to {cookie_file_path}: {str(e)}")
            raise AuthenticationException(f"Failed to save cookies: {str(e)}")

    def login_and_save(self, email: str, password: str, cookie_file_path: Optional[str] = None) -> RequestsCookieJar:
        """
        Login with credentials and save cookies to file, then return as RequestsCookieJar.
        
        Args:
            email: User email
            password: User password
            cookie_file_path: Path to save cookies (defaults to instance value)
            
        Returns:
            RequestsCookieJar with authentication cookies
        """
        # Login to get cookies
        sid, user_id = self.login_with_credentials(email, password)
        
        # Save to file
        self.save_cookies_to_file(sid, user_id, cookie_file_path)
        
        # Return as cookie jar with both cookie name formats
        cookie_jar = RequestsCookieJar()
        cookie_jar.set('remix_userkey', sid, domain='z-library.sk', path='/')
        cookie_jar.set('remix_userid', user_id, domain='z-library.sk', path='/')
        cookie_jar.set('sid', sid, domain='z-library.sk', path='/')
        cookie_jar.set('user_id', user_id, domain='z-library.sk', path='/')
        
        return cookie_jar