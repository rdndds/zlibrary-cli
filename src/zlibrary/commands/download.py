"""
Download command handler for Z-Library Search Application
"""
import os
from typing import List, Tuple
from zlibrary.config import Config
from zlibrary.auth import AuthManager
from zlibrary.download import DownloadManager
from zlibrary.book_details import BookDetailsManager
from zlibrary.export import ExportManager
from zlibrary.index import IndexManager
from zlibrary.commands.base import BaseCommandHandler
from zlibrary.formatters import DownloadResultFormatter, BookFormatter
from zlibrary.validators import URLValidator, FileValidator, ExportValidator
from zlibrary.error_handler import ErrorHandler, ProgressIndicator, UserFeedback
from zlibrary.logging_config import get_logger
from zlibrary.exceptions import NetworkException


class DownloadCommandHandler(BaseCommandHandler):
    """Handles the download command with validation and error handling"""
    
    def __init__(self, config: Config):
        super().__init__(config)
        self.logger = get_logger(__name__)
        self.auth_manager = AuthManager(config.get('cookies_file'))
        self.index_manager = IndexManager(config)
        self.download_manager = DownloadManager(config, self.auth_manager, self.index_manager)
        self.book_details_manager = BookDetailsManager(config, self.auth_manager)
        self.export_manager = ExportManager()
        self.error_handler = ErrorHandler()

    def handle(self, args) -> bool:
        """Handle the download command with validation"""
        try:
            # Parse URLs and determine mode
            book_urls, is_bulk = self._parse_urls(args)
            if not book_urls:
                return False
            
            # Validate URLs
            if not self._validate_urls(book_urls):
                return False
            
            # Validate export format if provided
            if hasattr(args, 'export') and args.export:
                result = ExportValidator.validate_format(args.export)
                if not result.is_valid:
                    UserFeedback.error(self.error_handler.handle_validation_error(result.error_message, "export format"))
                    return False
            
            # Handle bulk or single download
            if is_bulk:
                return self._handle_bulk_download(book_urls, args)
            else:
                return self._handle_single_download(book_urls[0], args)
                
        except NetworkException as e:
            error_msg = self.error_handler.handle_network_error(e, "downloading books")
            UserFeedback.error(error_msg)
            return False
        except Exception as e:
            UserFeedback.error(f"Unexpected error during download: {e}")
            self.logger.exception("Download error")
            return False
    
    def _parse_urls(self, args) -> Tuple[List[str], bool]:
        """Parse URLs from arguments and determine if bulk mode."""
        # Explicit file provided
        if args.urls_file:
            result = FileValidator.validate_readable_file(args.urls_file)
            if not result.is_valid:
                UserFeedback.error(self.error_handler.handle_validation_error(result.error_message, "URLs file"))
                return [], False
            
            urls = self._read_urls_from_file(args.urls_file)
            return urls, True
        
        # Single argument that's a file
        if len(args.url) == 1 and (args.url[0].startswith('@') or os.path.isfile(args.url[0])):
            file_path = args.url[0].lstrip('@')
            
            result = FileValidator.validate_readable_file(file_path)
            if not result.is_valid:
                UserFeedback.error(self.error_handler.handle_validation_error(result.error_message, "URLs file"))
                return [], False
            
            urls = self._read_urls_from_file(file_path)
            return urls, True
        
        # Multiple URLs
        if len(args.url) > 1:
            return args.url, True
        
        # Single URL
        if len(args.url) == 1:
            return args.url, False
        
        UserFeedback.error("URL or file is required for download")
        UserFeedback.info("Example: python main.py download https://z-library.sk/book/12345/example")
        return [], False
    
    def _read_urls_from_file(self, file_path: str) -> List[str]:
        """Read URLs from file with error handling."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                urls = [line.strip() for line in f if line.strip() and not line.startswith('#')]
            
            if not urls:
                UserFeedback.warning(f"No URLs found in file: {file_path}")
                UserFeedback.info("File should contain one URL per line")
                return []
            
            UserFeedback.info(f"Read {len(urls)} URLs from {file_path}")
            return urls
            
        except Exception as e:
            error_msg = self.error_handler.handle_file_error(e, "read", file_path)
            UserFeedback.error(error_msg)
            return []
    
    def _validate_urls(self, urls: List[str]) -> bool:
        """Validate all URLs with detailed feedback."""
        UserFeedback.info(f"Validating {len(urls)} URL(s)...")
        
        valid_urls, invalid_urls = URLValidator.validate_batch(urls)
        
        if invalid_urls:
            UserFeedback.error(f"Found {len(invalid_urls)} invalid URL(s):")
            for url, error in invalid_urls[:5]:  # Show first 5
                print(f"  • {url[:60]}...")
                print(f"    Error: {error}")
            
            if len(invalid_urls) > 5:
                print(f"  ... and {len(invalid_urls) - 5} more")
            
            return False
        
        UserFeedback.success("All URLs are valid")
        return True
    
    def _handle_bulk_download(self, urls: List[str], args) -> bool:
        """Handle bulk download with progress indicator."""
        UserFeedback.info(f"Starting bulk download of {len(urls)} books...")
        
        try:
            results = self.download_manager.bulk_download(urls)
            
            # Handle export if requested
            if hasattr(args, 'export') and args.export:
                self._export_downloaded_books(urls, args.export)
            
            # Count successes
            successful = sum(1 for r in results if r.get('status') == 'success')
            
            # Return success if any downloads succeeded
            return successful > 0
                
        except Exception as e:
            UserFeedback.error(f"Bulk download failed: {e}")
            self.logger.exception("Bulk download error")
            return False
    
    def _handle_single_download(self, url: str, args) -> bool:
        """Handle single download with detailed feedback."""
        # Show details if requested
        if args.details:
            UserFeedback.info("Fetching book details...")
            book_details = self.book_details_manager.get_book_details(url)
            
            if book_details:
                print("\n" + BookFormatter.format_detailed(book_details))
                print()
            else:
                UserFeedback.warning("Could not fetch book details")
        
        # Perform download
        UserFeedback.info(f"Downloading from: {url[:60]}...")
        
        try:
            success = self.download_manager.download_book(
                url,
                filename=args.filename if hasattr(args, 'filename') else None
            )
            
            if not success:
                UserFeedback.error("Download failed")
                return False
            
            # Handle export if requested
            if hasattr(args, 'export') and args.export:
                self._export_downloaded_books([url], args.export)
            
            UserFeedback.success("Download completed")
            return True
            
        except Exception as e:
            UserFeedback.error(f"Download failed: {e}")
            self.logger.exception("Single download error")
            return False
    
    def _export_downloaded_books(self, urls: List[str], export_format: str):
        """Export details of downloaded books."""
        UserFeedback.info(f"Exporting book details in {export_format} format...")
        
        try:
            progress = ProgressIndicator(len(urls), "Fetching details for export")
            books = []
            
            for url in urls:
                progress.update(1)
                book_details = self.book_details_manager.get_book_details(url)
                if book_details:
                    books.append(book_details)
            
            progress.complete("Export data prepared")
            
            if books:
                self.export_manager.export_results(books, "downloaded_books", export_format)
                UserFeedback.success(f"Exported {len(books)} book(s)")
            else:
                UserFeedback.warning("No book details to export")
                
        except Exception as e:
            UserFeedback.error(f"Export failed: {e}")
            self.logger.exception("Export error")
