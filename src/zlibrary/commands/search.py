"""
Search command handler for Z-Library Search Application
"""
from zlibrary.config import Config
from zlibrary.auth import AuthManager
from zlibrary.search import SearchManager
from zlibrary.book_details import BookDetailsManager
from zlibrary.export import ExportManager
from zlibrary.account import AccountManager
from zlibrary.download import DownloadManager
from zlibrary.index import IndexManager
from zlibrary.commands.base import BaseCommandHandler
from zlibrary.formatters import SearchResultFormatter, BookFormatter, DownloadResultFormatter
from zlibrary.validators import SearchValidator, ExportValidator, InputSanitizer
from zlibrary.error_handler import ErrorHandler, ProgressIndicator, UserFeedback
from zlibrary.logging_config import get_logger
from zlibrary.exceptions import NetworkException, ParsingException
import re


class SearchCommandHandler(BaseCommandHandler):
    """Handles the search command with validation and error handling"""
    
    def __init__(self, config: Config):
        super().__init__(config)
        self.logger = get_logger(__name__)
        self.auth_manager = AuthManager(config.get('cookies_file'))
        self.search_manager = SearchManager(config, self.auth_manager)
        self.book_details_manager = BookDetailsManager(config, self.auth_manager)
        self.export_manager = ExportManager()
        self.account_manager = AccountManager(config, self.auth_manager)
        self.error_handler = ErrorHandler()

    def handle(self, args) -> bool:
        """Handle the search command with validation"""
        try:
            # Validate and sanitize search parameters
            if not self._validate_and_sanitize_params(args):
                return False
            
            # Perform search
            results, search_term = self._perform_search(args)
            if results is None:
                return False
            
            # Display results
            self._display_results(results, search_term, args.details)
            
            # Handle export if requested
            if hasattr(args, 'export') and args.export:
                if not self._handle_export(results, args.export, search_term):
                    return False
            
            # Handle download if requested
            if args.download:
                if not self._handle_download(results):
                    return False
            
            UserFeedback.success(f"Search completed: {len(results)} results found")
            return True
            
        except NetworkException as e:
            error_msg = self.error_handler.handle_network_error(e, "searching Z-Library")
            UserFeedback.error(error_msg)
            return False
        except ParsingException as e:
            error_msg = self.error_handler.handle_parsing_error("parsing search results")
            UserFeedback.error(error_msg)
            return False
        except Exception as e:
            UserFeedback.error(f"Unexpected error during search: {e}")
            self.logger.exception("Search error")
            return False
    
    def _validate_and_sanitize_params(self, args) -> bool:
        """Validate and sanitize search parameters."""
        # Check that at least one search parameter is provided
        if not args.query and not args.title:
            UserFeedback.error("You must provide either a query or --title")
            UserFeedback.info("Example: python main.py search 'machine learning'")
            return False
        
        # Validate and sanitize query
        if args.query:
            result = SearchValidator.validate_query(args.query)
            if not result.is_valid:
                UserFeedback.error(self.error_handler.handle_validation_error(result.error_message, "query"))
                return False
            args.query = InputSanitizer.sanitize_search_query(args.query)
        
        # Validate and sanitize title
        if args.title:
            result = SearchValidator.validate_query(args.title)
            if not result.is_valid:
                UserFeedback.error(self.error_handler.handle_validation_error(result.error_message, "title"))
                return False
            args.title = InputSanitizer.sanitize_search_query(args.title)
        
        # Validate limit
        if not args.no_limit:
            result = SearchValidator.validate_limit(args.limit)
            if not result.is_valid:
                UserFeedback.error(self.error_handler.handle_validation_error(result.error_message, "limit"))
                return False
        
        # Validate export format if provided
        if hasattr(args, 'export') and args.export:
            result = ExportValidator.validate_format(args.export)
            if not result.is_valid:
                UserFeedback.error(self.error_handler.handle_validation_error(result.error_message, "export format"))
                return False
        
        return True
    
    def _perform_search(self, args):
        """Perform the search and return results."""
        limit = 10000 if args.no_limit else args.limit
        limit_display = "no limit" if args.no_limit else str(args.limit)
        
        UserFeedback.info(f"Searching with limit: {limit_display}")
        
        try:
            if args.query:
                self.logger.info(f"Searching for: {args.query}")
                results = self.search_manager.search_zlibrary(query=args.query, limit=limit)
                search_term = args.query
            else:
                self.logger.info(f"Searching for title: {args.title}")
                results = self.search_manager.search_zlibrary(title=args.title, limit=limit)
                search_term = f"title: {args.title}"
            
            return results, search_term
            
        except Exception as e:
            self.logger.error(f"Search failed: {e}")
            raise
    
    def _display_results(self, results, search_term, show_details):
        """Display search results with progress indicator."""
        if not results:
            UserFeedback.warning("No results found")
            return
        
        if show_details:
            UserFeedback.info(f"Fetching detailed information for {len(results)} books...")
            progress = ProgressIndicator(len(results), "Fetching details")
            
            for i, book in enumerate(results, 1):
                progress.update(1, book.title[:40])
                detailed_info = self.book_details_manager.get_book_details(book.url)
                display_book = detailed_info if detailed_info else book
                print(f"\n{BookFormatter.format_detailed(display_book, i)}")
            
            progress.complete("Details fetched")
        else:
            print(SearchResultFormatter.format_summary(results, search_term, False))
    
    def _handle_export(self, results, export_format, search_term) -> bool:
        """Handle export functionality."""
        if not results:
            UserFeedback.warning("No results to export")
            return False
        
        UserFeedback.info(f"Exporting {len(results)} results in {export_format} format...")
        
        try:
            # Fetch detailed info for export with progress
            progress = ProgressIndicator(len(results), "Preparing export")
            detailed_results = []
            
            for book in results:
                progress.update(1, book.title[:40])
                detailed_info = self.book_details_manager.get_book_details(book.url)
                detailed_results.append(detailed_info if detailed_info else book)
            
            progress.complete("Export data prepared")
            
            # Generate clean filename
            clean_query = re.sub(r'[^\w\s-]', '_', search_term).strip()[:50]
            clean_query = re.sub(r'[-_\s]+', '_', clean_query)
            filename_base = f"search_results_{clean_query}"
            
            self.export_manager.export_results(detailed_results, filename_base, export_format)
            UserFeedback.success(f"Results exported to {filename_base}")
            return True
            
        except Exception as e:
            UserFeedback.error(f"Export failed: {e}")
            self.logger.exception("Export error")
            return False
    
    def _handle_download(self, results) -> bool:
        """Handle download functionality."""
        if not results:
            UserFeedback.warning("No results to download")
            return False
        
        # Check download limits
        UserFeedback.info("Checking download limits...")
        can_download, limit_info = self.account_manager.check_download_limit(verbose=False)
        
        if not can_download:
            error_msg = self.error_handler.handle_download_limit_error(limit_info)
            UserFeedback.error(error_msg)
            return False
        
        # Perform bulk download
        index_manager = IndexManager(self.config)
        download_manager = DownloadManager(self.config, self.auth_manager, index_manager)
        
        book_urls = [book.url for book in results]
        UserFeedback.info(f"Starting bulk download of {len(book_urls)} books...")
        
        try:
            bulk_results = download_manager.bulk_download(book_urls)
            print(DownloadResultFormatter.format_summary(bulk_results))
            return True
            
        except Exception as e:
            UserFeedback.error(f"Download failed: {e}")
            self.logger.exception("Download error")
            return False
