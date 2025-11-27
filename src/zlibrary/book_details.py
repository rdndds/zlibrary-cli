"""
Book details functionality for Z-Library Search Application
"""
from typing import Optional

from zlibrary.config import Config
from zlibrary.auth import AuthManager
from zlibrary.http_client import ZLibraryHTTPClient
from zlibrary.book import Book
from zlibrary.parsers import BookDetailsParser
from zlibrary.logging_config import get_logger
from zlibrary.exceptions import NetworkException, ParsingException
from zlibrary.cache import CacheManager, BookDetailsCache


class BookDetailsManager:
    """Handles fetching detailed information for specific books with caching"""

    def __init__(self, config: Config, auth_manager: AuthManager, cache_manager: Optional[CacheManager] = None):
        self.config = config
        self.auth_manager = auth_manager
        self.http_client = ZLibraryHTTPClient(config, auth_manager)
        self.parser = BookDetailsParser()
        self.logger = get_logger(__name__)
        
        # Initialize cache
        if cache_manager is None:
            cache_manager = CacheManager()
        self.cache_manager = cache_manager
        self.details_cache = BookDetailsCache(cache_manager)
    
    def get_book_details(self, book_url: str, use_cache: bool = True) -> Optional[Book]:
        """
        Fetch detailed information for a specific book URL

        Args:
            book_url: URL of the book page
            use_cache: Whether to use cached details

        Returns:
            Book object containing detailed information, or None on error
        """
        # Check cache first
        if use_cache:
            cached_details = self.details_cache.get_book_details(book_url)
            if cached_details:
                return Book(**cached_details)
        
        try:
            # Fetch the book page using HTTP client
            response = self.http_client.get(book_url)

            if response.status_code == 200:
                # Parse using the parser
                book = self.parser.parse(response.text)
                # Set the URL
                book.url = book_url
                
                # Cache the details
                if use_cache:
                    self.details_cache.cache_book_details(book_url, book)
                
                return book
            else:
                self.logger.error(f"Error fetching book details: HTTP {response.status_code}")
                return None
                
        except NetworkException as e:
            self.logger.error(f"Network error fetching book details: {e}")
            return None
        except ParsingException as e:
            self.logger.error(f"Parsing error fetching book details: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Error fetching book details: {e}")
            return None
