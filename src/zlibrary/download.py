"""
Download functionality for Z-Library Search Application
"""
import os
import sys
import time
import urllib.parse
import re
import shutil
from typing import Optional, List, Tuple

from zlibrary.config import Config
from zlibrary.auth import AuthManager
from zlibrary.http_client import ZLibraryHTTPClient
from zlibrary.book import Book
from zlibrary.index import IndexManager
from zlibrary.utils import clean_filename, extract_book_id_from_url
from zlibrary.account import AccountManager
from zlibrary.book_details import BookDetailsManager
from zlibrary.logging_config import get_logger
from zlibrary.exceptions import (
    DownloadLimitExceededException,
    NetworkException,
    StorageException,
    AuthenticationException
)
from zlibrary.constants import ConfigKeys


class DownloadManager:
    """Handles book downloading functionality"""

    def __init__(self, config: Config, auth_manager: AuthManager, index_manager: IndexManager):
        self.config = config
        self.auth_manager = auth_manager
        self.index_manager = index_manager
        self.http_client = ZLibraryHTTPClient(config, auth_manager)
        self.logger = get_logger(__name__)
        self.terminal_width = self._get_terminal_width()
    
    def _get_terminal_width(self) -> int:
        """Get terminal width, with fallback to 80 columns."""
        try:
            return shutil.get_terminal_size().columns
        except:
            return 80
    
    def _print_separator(self, char: str = '-'):
        """Print a separator line that adapts to terminal width."""
        print(char * self.terminal_width)
    
    def _print_header(self, text: str):
        """Print a centered header."""
        self._print_separator('=')
        padding = (self.terminal_width - len(text)) // 2
        print(' ' * padding + text)
        self._print_separator('=')
    
    def _print_section(self, text: str):
        """Print a section separator with text."""
        self._print_separator('-')
        print(text)
        self._print_separator('-')
    
    def _check_download_limit(self, verbose: bool = True) -> bool:
        """
        Check if user can download more books.
        
        Args:
            verbose: Whether to print information
            
        Returns:
            True if can download, False otherwise
        """
        account_manager = AccountManager(self.config, self.auth_manager)
        can_download, limit_info = account_manager.check_download_limit(verbose=verbose)
        
        if not can_download:
            self.logger.error("Download limit reached.")
            if verbose:
                print("Download limit reached. Cannot proceed with download.")
        
        return can_download
    
    def _resolve_download_url(self, book_url: str) -> Optional[str]:
        """
        Resolve book page URL to actual download URL.
        
        Args:
            book_url: Book page URL or direct download URL
            
        Returns:
            Download URL or None if not found
        """
        # If already a download URL, return it
        if '/dl/' in book_url:
            return book_url
        
        # If it's a book page, get download URL from book details
        if '/book/' in book_url:
            book_details_manager = BookDetailsManager(self.config, self.auth_manager)
            book_details = book_details_manager.get_book_details(book_url)
            
            if not book_details or book_details.download_url == 'Not available':
                self.logger.error("Could not find download URL for the book.")
                return None
            
            download_url = book_details.download_url
            
            # If it's a reader URL, extract the direct download location
            if '/read/' in download_url:
                parsed_url = urllib.parse.urlparse(download_url)
                query_params = urllib.parse.parse_qs(parsed_url.query)
                if 'download_location' in query_params:
                    return urllib.parse.unquote(query_params['download_location'][0])
            
            return download_url
        
        # Default: assume it's a direct URL
        return book_url
    
    def _determine_filename(self, response, book_url: str, custom_filename: Optional[str] = None) -> str:
        """
        Determine filename for downloaded book.
        
        Args:
            response: HTTP response object
            book_url: Original book URL
            custom_filename: Custom filename if provided
            
        Returns:
            Clean filename with extension
        """
        if custom_filename:
            # Ensure it has an extension
            if '.' not in custom_filename:
                ext = self._extract_file_extension(response, book_url)
                return clean_filename(f"{custom_filename}.{ext}")
            return clean_filename(custom_filename)
        
        # Try to get filename from content-disposition header
        content_disposition = response.headers.get('content-disposition', '')
        if content_disposition:
            filename = self._parse_content_disposition(content_disposition)
            if filename:
                return clean_filename(filename)
        
        # Generate filename from URL and content-type
        file_ext = self._extract_file_extension(response, book_url)
        base_name = self._extract_base_name_from_url(book_url)
        filename = f"{base_name}.{file_ext}"
        
        return clean_filename(filename)
    
    def _parse_content_disposition(self, content_disposition: str) -> Optional[str]:
        """Parse filename from content-disposition header."""
        # Try regular filename
        filename_match = re.search(
            r'filename[^;]=*\s*"?([^"]+)"?',
            content_disposition,
            re.IGNORECASE
        )
        if filename_match:
            return urllib.parse.unquote(filename_match.group(1))
        
        # Try filename* format
        filename_match = re.search(
            r"filename\*[^;]*=[^']*'[^']*'([^']+)",
            content_disposition,
            re.IGNORECASE
        )
        if filename_match:
            return urllib.parse.unquote(filename_match.group(1))
        
        return None
    
    def _extract_file_extension(self, response, book_url: str) -> str:
        """Extract file extension from response or URL."""
        # Try query parameters first
        parsed_url = urllib.parse.urlparse(book_url)
        query_params = urllib.parse.parse_qs(parsed_url.query)
        if 'extension' in query_params:
            return query_params['extension'][0].lower()
        
        # Try content-type header
        content_type = response.headers.get('content-type', '').lower()
        if 'application/pdf' in content_type:
            return 'pdf'
        elif 'application/epub' in content_type:
            return 'epub'
        elif 'application/x-mobipocket-ebook' in content_type:
            return 'mobi'
        
        # Default
        return 'pdf'
    
    def _extract_base_name_from_url(self, book_url: str) -> str:
        """Extract base filename from book URL."""
        parsed_url = urllib.parse.urlparse(book_url)
        path_parts = parsed_url.path.split('/')
        
        # Look for a part with a dot (e.g., book-title.html)
        for part in reversed(path_parts):
            if part and '.' in part:
                return part.split('.')[0]  # Remove extension
        
        # Fallback: use timestamp
        return f"zlibrary_book_{int(time.time())}"
    
    def _ensure_download_dir(self, download_dir: str, verbose: bool = False):
        """Ensure download directory exists."""
        if not os.path.exists(download_dir):
            os.makedirs(download_dir, exist_ok=True)
            self.logger.debug(f"Created download directory: {download_dir}")
            if verbose:
                print(f"Created download directory: {download_dir}")
    
    def _format_size_mb(self, size_bytes: int) -> float:
        """Convert bytes to MB."""
        return size_bytes / (1024 * 1024)
    
    def _download_with_progress(
        self,
        response,
        filepath: str,
        verbose: bool = True
    ) -> int:
        """
        Download file with progress tracking.
        
        Args:
            response: HTTP response with stream=True
            filepath: Path to save file
            verbose: Whether to show progress
            
        Returns:
            Total bytes downloaded
            
        Raises:
            StorageException: On write errors
        """
        total_size = None
        content_length = response.headers.get('Content-Length')
        if content_length:
            total_size = int(content_length)
        
        downloaded_size = 0
        
        try:
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded_size += len(chunk)
                        
                        if verbose:
                            self._show_progress(downloaded_size, total_size)
            
            if verbose:
                self._show_final_status(downloaded_size, total_size)
            
            return downloaded_size
            
        except OSError as e:
            self.logger.error(f"Error writing file {filepath}: {e}")
            raise StorageException(f"Failed to write file {filepath}: {e}")
    
    def _show_progress(self, downloaded: int, total: Optional[int]):
        """Show download progress."""
        if total:
            progress = (downloaded / total) * 100
            downloaded_mb = self._format_size_mb(downloaded)
            total_mb = self._format_size_mb(total)
            
            # Create progress bar
            bar_width = min(40, self.terminal_width - 50)
            filled = int(bar_width * progress / 100)
            bar = '#' * filled + '-' * (bar_width - filled)
            
            print(
                f"\r[{bar}] {progress:.1f}% | {downloaded_mb:.2f} MB / {total_mb:.2f} MB",
                end='',
                flush=True
            )
            sys.stdout.flush()
        else:
            downloaded_mb = self._format_size_mb(downloaded)
            print(f"\rDownloaded: {downloaded_mb:.2f} MB", end='', flush=True)
            sys.stdout.flush()
    
    def _show_final_status(self, downloaded: int, total: Optional[int]):
        """Show final download status."""
        downloaded_mb = self._format_size_mb(downloaded)
        if total:
            total_mb = self._format_size_mb(total)
            print(f"\nCompleted: {downloaded_mb:.2f} MB / {total_mb:.2f} MB")
        else:
            print(f"\nCompleted: {downloaded_mb:.2f} MB")
    
    def _add_to_index(self, book_url: str, verbose: bool = False):
        """Add downloaded book to index."""
        if '/book/' in book_url and '/dl/' not in book_url:
            book_details_manager = BookDetailsManager(self.config, self.auth_manager)
            book_details = book_details_manager.get_book_details(book_url)
            
            if book_details:
                book_id = extract_book_id_from_url(book_url)
                if book_id and book_id not in ['book', 'dl']:
                    self.index_manager.add_to_download_index(book_id, book_details.title)
                    if verbose:
                        print(f"  Indexed: {book_details.title}")
    
    def download_book(
        self,
        book_url: str,
        filename: Optional[str] = None,
        verbose: bool = True,
        download_dir: str = "books",
        check_limits: bool = True
    ) -> bool:
        """
        Download a book from Z-Library using the provided URL

        Args:
            book_url: URL to the book page or direct download link
            filename: Optional filename to save the book as
            verbose: Whether to show progress information
            download_dir: Directory to save the downloaded file
            check_limits: Whether to check download limits

        Returns:
            True if download was successful, False otherwise
        """
        try:
            # Check download limits if required
            if check_limits and not self._check_download_limit(verbose):
                return False
            
            # Resolve download URL
            download_url = self._resolve_download_url(book_url)
            if not download_url:
                if verbose:
                    print("ERROR: Could not find download URL")
                return False
            
            self.logger.info(f"Downloading from: {download_url}")
            
            # Get the file with streaming
            response = self.http_client.get(
                download_url,
                headers={'Referer': book_url},
                allow_redirects=True
            )
            
            if response.status_code != 200:
                self.logger.error(f"Download failed. HTTP {response.status_code}")
                if verbose:
                    print(f"ERROR: Download failed with HTTP status {response.status_code}")
                return False
            
            # Determine filename
            final_filename = self._determine_filename(response, book_url, filename)
            
            # Ensure download directory exists
            self._ensure_download_dir(download_dir, verbose)
            
            # Download file with progress
            filepath = os.path.join(download_dir, final_filename)
            
            if verbose:
                print(f"Downloading: {final_filename}")
            
            # Get file with streaming enabled for progress tracking
            response = self.http_client.get(
                download_url,
                headers={'Referer': book_url},
                allow_redirects=True,
                stream=True
            )
            
            if response.status_code != 200:
                self.logger.error(f"Download failed. HTTP {response.status_code}")
                if verbose:
                    print(f"ERROR: Download failed with HTTP status {response.status_code}")
                return False
            
            # Download with real-time progress
            downloaded_size = self._download_with_progress(response, filepath, verbose)
            
            self.logger.info(f"Book downloaded successfully as: {filepath}")
            if verbose:
                print(f"SUCCESS: Saved as {os.path.basename(filepath)}")

            
            # Add to download index
            self._add_to_index(book_url, verbose=False)
            
            return True
            
        except NetworkException as e:
            self.logger.error(f"Network error during download: {e}")
            if verbose:
                print(f"ERROR: Network error - {e}")
            return False
        except StorageException as e:
            self.logger.error(f"Storage error: {e}")
            if verbose:
                print(f"ERROR: Storage error - {e}")
            return False
        except Exception as e:
            self.logger.error(f"Error downloading book: {e}")
            if verbose:
                print(f"ERROR: {e}")
            return False
    
    def bulk_download(
        self,
        book_urls: List[str],
        create_index: bool = True
    ) -> List[dict]:
        """
        Download multiple books in bulk with duplicate prevention

        Args:
            book_urls: List of book URLs to download
            create_index: Whether to create index file if it doesn't exist

        Returns:
            List of download results with success/failure status
        """
        # Print initial header
        self._print_header("BULK DOWNLOAD SESSION")
        print()
        
        # Check download limits
        account_manager = AccountManager(self.config, self.auth_manager)
        can_download, limit_info = account_manager.check_download_limit(verbose=True)
        
        if not can_download:
            self.logger.error("Download limit reached.")
            print("\nERROR: Download limit reached. Cannot proceed.")
            return []
        
        # Limit to remaining downloads
        downloads_remaining = limit_info.get('downloads_remaining', 0)
        if downloads_remaining > 0 and len(book_urls) > downloads_remaining:
            self.logger.info(f"Truncating to {downloads_remaining} books to respect daily limit.")
            print(f"\nWARNING: Limiting to {downloads_remaining} books to respect daily limit.")
            book_urls = book_urls[:downloads_remaining]
        
        # Create index if needed
        if create_index:
            self.index_manager.create_download_index()
        
        # Track overall progress
        total_books = len(book_urls)
        successful = 0
        failed = 0
        skipped = 0
        
        print(f"\nTotal books to process: {total_books}")
        print()
        
        # Download each book
        results = []
        for i, url in enumerate(book_urls, 1):
            # Print progress header
            self._print_separator('=')
            print(f"Book {i} of {total_books}")
            print(f"Status - Success: {successful} | Failed: {failed} | Skipped: {skipped}")
            self._print_separator('=')
            
            # Show URL (truncated if too long)
            max_url_len = self.terminal_width - 10
            display_url = url if len(url) <= max_url_len else url[:max_url_len-3] + '...'
            print(f"URL: {display_url}")
            print()
            
            # Check if already downloaded
            book_id = extract_book_id_from_url(url)
            if book_id and self.index_manager.is_already_downloaded(book_id):
                print("SKIPPED: Already downloaded")
                results.append({'url': url, 'status': 'skipped', 'reason': 'already_downloaded'})
                skipped += 1
                print()
                continue
            
            # Download
            success = self.download_book(url, verbose=True, check_limits=False)
            
            if success:
                successful += 1
            else:
                failed += 1
            
            results.append({
                'url': url,
                'status': 'success' if success else 'failed',
                'book_id': book_id
            })
            
            print()
            # Small delay between downloads
            if i < len(book_urls):
                time.sleep(1)
        
        # Print final summary
        self._print_header("DOWNLOAD COMPLETE")
        print()
        print(f"Total Books:     {total_books}")
        print(f"Successful:      {successful}")
        print(f"Failed:          {failed}")
        print(f"Skipped:         {skipped}")
        print()
        self._print_separator('=')
        print()
        
        return results
