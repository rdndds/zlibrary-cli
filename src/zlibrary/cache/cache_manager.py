"""
Cache Manager for Z-Library CLI

Provides caching for search results, book details, and other data to improve performance.
"""
import json
import os
import time
import hashlib
from typing import Any, Optional, Dict
from datetime import datetime, timedelta
from zlibrary.logging_config import get_logger


class CacheManager:
    """Manages caching of data with TTL support"""
    
    def __init__(self, cache_dir: str = "data/cache", default_ttl: int = 3600):
        """
        Initialize cache manager.
        
        Args:
            cache_dir: Directory to store cache files
            default_ttl: Default time-to-live in seconds (1 hour)
        """
        self.cache_dir = cache_dir
        self.default_ttl = default_ttl
        self.logger = get_logger(__name__)
        self.memory_cache: Dict[str, tuple[Any, float]] = {}
        
        # Create cache directory
        os.makedirs(cache_dir, exist_ok=True)
    
    def _get_cache_key(self, key: str) -> str:
        """Generate cache key hash."""
        return hashlib.md5(key.encode()).hexdigest()
    
    def _get_cache_path(self, key: str) -> str:
        """Get file path for cache key."""
        cache_key = self._get_cache_key(key)
        return os.path.join(self.cache_dir, f"{cache_key}.json")
    
    def _is_expired(self, timestamp: float, ttl: int) -> bool:
        """Check if cache entry is expired."""
        return time.time() - timestamp > ttl
    
    def get(self, key: str, use_memory: bool = True) -> Optional[Any]:
        """
        Get value from cache.
        
        Args:
            key: Cache key
            use_memory: Whether to use memory cache
            
        Returns:
            Cached value or None if not found/expired
        """
        # Try memory cache first
        if use_memory and key in self.memory_cache:
            value, timestamp = self.memory_cache[key]
            if not self._is_expired(timestamp, self.default_ttl):
                self.logger.debug(f"Memory cache hit: {key}")
                return value
            else:
                # Remove expired entry
                del self.memory_cache[key]
        
        # Try file cache
        cache_path = self._get_cache_path(key)
        if os.path.exists(cache_path):
            try:
                with open(cache_path, 'r', encoding='utf-8') as f:
                    cache_data = json.load(f)
                
                timestamp = cache_data.get('timestamp', 0)
                ttl = cache_data.get('ttl', self.default_ttl)
                
                if not self._is_expired(timestamp, ttl):
                    value = cache_data.get('value')
                    self.logger.debug(f"File cache hit: {key}")
                    
                    # Store in memory cache
                    if use_memory:
                        self.memory_cache[key] = (value, timestamp)
                    
                    return value
                else:
                    # Remove expired file
                    os.remove(cache_path)
                    self.logger.debug(f"Cache expired: {key}")
            
            except Exception as e:
                self.logger.warning(f"Error reading cache: {e}")
        
        return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None, use_memory: bool = True):
        """
        Set value in cache.
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Time-to-live in seconds (None = use default)
            use_memory: Whether to use memory cache
        """
        ttl = ttl if ttl is not None else self.default_ttl
        timestamp = time.time()
        
        # Store in memory cache
        if use_memory:
            self.memory_cache[key] = (value, timestamp)
        
        # Store in file cache
        cache_path = self._get_cache_path(key)
        try:
            cache_data = {
                'key': key,
                'value': value,
                'timestamp': timestamp,
                'ttl': ttl,
                'created': datetime.now().isoformat()
            }
            
            with open(cache_path, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, indent=2, ensure_ascii=False)
            
            self.logger.debug(f"Cached: {key} (ttl={ttl}s)")
        
        except Exception as e:
            self.logger.warning(f"Error writing cache: {e}")
    
    def delete(self, key: str):
        """Delete value from cache."""
        # Remove from memory cache
        if key in self.memory_cache:
            del self.memory_cache[key]
        
        # Remove from file cache
        cache_path = self._get_cache_path(key)
        if os.path.exists(cache_path):
            try:
                os.remove(cache_path)
                self.logger.debug(f"Deleted cache: {key}")
            except Exception as e:
                self.logger.warning(f"Error deleting cache: {e}")
    
    def clear(self, max_age: Optional[int] = None):
        """
        Clear cache entries.
        
        Args:
            max_age: If provided, only clear entries older than this (seconds)
        """
        # Clear memory cache
        if max_age is None:
            self.memory_cache.clear()
            self.logger.info("Cleared memory cache")
        else:
            cutoff = time.time() - max_age
            keys_to_delete = [
                key for key, (_, timestamp) in self.memory_cache.items()
                if timestamp < cutoff
            ]
            for key in keys_to_delete:
                del self.memory_cache[key]
            self.logger.info(f"Cleared {len(keys_to_delete)} expired memory cache entries")
        
        # Clear file cache
        try:
            deleted_count = 0
            for filename in os.listdir(self.cache_dir):
                if filename.endswith('.json'):
                    filepath = os.path.join(self.cache_dir, filename)
                    
                    if max_age is None:
                        os.remove(filepath)
                        deleted_count += 1
                    else:
                        # Check file age
                        file_mtime = os.path.getmtime(filepath)
                        if file_mtime < cutoff:
                            os.remove(filepath)
                            deleted_count += 1
            
            self.logger.info(f"Cleared {deleted_count} file cache entries")
        
        except Exception as e:
            self.logger.warning(f"Error clearing cache: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        stats = {
            'memory_entries': len(self.memory_cache),
            'file_entries': 0,
            'total_size_bytes': 0,
            'cache_dir': self.cache_dir
        }
        
        try:
            for filename in os.listdir(self.cache_dir):
                if filename.endswith('.json'):
                    stats['file_entries'] += 1
                    filepath = os.path.join(self.cache_dir, filename)
                    stats['total_size_bytes'] += os.path.getsize(filepath)
        except Exception as e:
            self.logger.warning(f"Error getting cache stats: {e}")
        
        return stats


class SearchCache:
    """Specialized cache for search results"""
    
    def __init__(self, cache_manager: CacheManager):
        self.cache_manager = cache_manager
        self.logger = get_logger(__name__)
    
    def _make_key(self, query: str = None, title: str = None, limit: int = None) -> str:
        """Generate cache key for search parameters."""
        parts = []
        if query:
            parts.append(f"q:{query}")
        if title:
            parts.append(f"t:{title}")
        if limit:
            parts.append(f"l:{limit}")
        return "search:" + "|".join(parts)
    
    def get_search_results(self, query: str = None, title: str = None, limit: int = None) -> Optional[list]:
        """Get cached search results."""
        key = self._make_key(query, title, limit)
        results = self.cache_manager.get(key)
        
        if results:
            self.logger.info(f"Using cached search results ({len(results)} items)")
        
        return results
    
    def cache_search_results(self, results: list, query: str = None, title: str = None, limit: int = None, ttl: int = 1800):
        """
        Cache search results.
        
        Args:
            results: Search results to cache
            query: Query string
            title: Title string
            limit: Result limit
            ttl: Time-to-live (default: 30 minutes)
        """
        key = self._make_key(query, title, limit)
        
        # Convert Book objects to dicts for JSON serialization
        serializable_results = []
        for book in results:
            book_dict = {
                'title': book.title,
                'author': book.author,
                'year': book.year,
                'url': book.url,
                'format': getattr(book, 'format', None),
                'file_type': getattr(book, 'file_type', None)
            }
            serializable_results.append(book_dict)
        
        self.cache_manager.set(key, serializable_results, ttl=ttl)
        self.logger.info(f"Cached {len(results)} search results")


class BookDetailsCache:
    """Specialized cache for book details"""
    
    def __init__(self, cache_manager: CacheManager):
        self.cache_manager = cache_manager
        self.logger = get_logger(__name__)
    
    def _make_key(self, url: str) -> str:
        """Generate cache key for book URL."""
        return f"book:{url}"
    
    def get_book_details(self, url: str) -> Optional[Dict]:
        """Get cached book details."""
        key = self._make_key(url)
        details = self.cache_manager.get(key)
        
        if details:
            self.logger.debug(f"Using cached book details for {url}")
        
        return details
    
    def cache_book_details(self, url: str, details: Any, ttl: int = 3600):
        """
        Cache book details.
        
        Args:
            url: Book URL
            details: Book details object
            ttl: Time-to-live (default: 1 hour)
        """
        key = self._make_key(url)
        
        # Convert Book object to dict for JSON serialization
        if hasattr(details, '__dict__'):
            details_dict = vars(details).copy()
        else:
            details_dict = details
        
        self.cache_manager.set(key, details_dict, ttl=ttl)
        self.logger.debug(f"Cached book details for {url}")
