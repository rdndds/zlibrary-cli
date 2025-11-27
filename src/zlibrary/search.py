"""
Search functionality for Z-Library Search Application
"""
import time
from typing import List, Optional

from zlibrary.config import Config
from zlibrary.auth import AuthManager
from zlibrary.http_client import ZLibraryHTTPClient
from zlibrary.book import Book
from zlibrary.parsers import SearchResultParser
from zlibrary.logging_config import get_logger
from zlibrary.exceptions import NetworkException, ParsingException
from zlibrary.constants import BASE_URL, ConfigKeys
from zlibrary.cache import CacheManager, SearchCache


class SearchManager:
    """Handles Z-Library search operations with caching"""

    def __init__(self, config: Config, auth_manager: AuthManager, cache_manager: Optional[CacheManager] = None):
        self.config = config
        self.auth_manager = auth_manager
        self.http_client = ZLibraryHTTPClient(config, auth_manager)
        self.parser = SearchResultParser()
        self.logger = get_logger(__name__)
        
        # Initialize cache
        if cache_manager is None:
            cache_manager = CacheManager()
        self.cache_manager = cache_manager
        self.search_cache = SearchCache(cache_manager)
    
    def _build_search_url(self, query: str) -> str:
        """Build search URL from query."""
        return f"{BASE_URL}/s/{query}"
    
    def search_zlibrary(self, query: str = None, title: str = None, limit: int = 10, use_cache: bool = True) -> List[Book]:
        """
        Search Z-Library for books using the provided query or title parameter

        Args:
            query: General search query
            title: Search by title specifically
            limit: Maximum number of results to return
            use_cache: Whether to use cached results

        Returns:
            List of Book objects containing book information
        """
        # Check cache first
        if use_cache:
            cached_results = self.search_cache.get_search_results(query=query, title=title, limit=limit)
            if cached_results:
                # Convert cached dicts back to Book objects
                return [Book(**book_dict) for book_dict in cached_results]
        
        # Determine search query
        if title:
            search_query = title
        elif query:
            search_query = query
        else:
            search_query = ""

        search_url = self._build_search_url(search_query)
        results = []

        try:
            self.logger.info(f"Starting search with query: {search_query}, limit: {limit}")
            page_num = 1
            max_pages = self.config.get(ConfigKeys.MAX_PAGES, 5)

            while len(results) < limit and page_num <= max_pages:
                self.logger.info(f"Searching page {page_num}/{max_pages}...")

                # Perform the search using HTTP client
                response = self.http_client.get(
                    search_url,
                    params={'page': page_num}
                )

                if response.status_code == 200:
                    # Parse the page using the parser
                    page_books = self.parser.parse(response.text)
                    
                    if not page_books:
                        self.logger.debug(f"No more books found on page {page_num}, stopping search")
                        break

                    # Add books up to the limit
                    for book in page_books:
                        if len(results) >= limit:
                            self.logger.info(f"Reached result limit of {limit}, stopping search")
                            break
                        results.append(book)

                    # Progress update
                    progress_percentage = min(100, int((len(results) / limit) * 100)) if limit > 0 else 0
                    self.logger.info(f"Progress: Found {len(results)}/{limit} books ({progress_percentage}%)")

                    page_num += 1
                    # Add a small delay to be respectful to the server
                    time.sleep(0.5)
                else:
                    self.logger.error(f"Error on page {page_num}: HTTP {response.status_code}")
                    break

            self.logger.info(f"Search completed. Found {len(results)} books")
            
            # Cache the results
            if use_cache and results:
                self.search_cache.cache_search_results(results, query=query, title=title, limit=limit)
            
            return results
            
        except NetworkException as e:
            self.logger.error(f"Network error during search: {e}")
            return []
        except ParsingException as e:
            self.logger.error(f"Parsing error during search: {e}")
            return []
        except Exception as e:
            self.logger.error(f"Error during search: {e}")
            return []
