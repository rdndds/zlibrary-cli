"""
Concurrent Operations for Z-Library CLI

Provides parallel processing capabilities for improved performance.
"""
import concurrent.futures
from typing import List, Callable, Any, Optional, Tuple
from zlibrary.logging_config import get_logger


class ConcurrentProcessor:
    """Handles concurrent execution of tasks"""
    
    def __init__(self, max_workers: int = 5):
        """
        Initialize concurrent processor.
        
        Args:
            max_workers: Maximum number of concurrent workers
        """
        self.max_workers = max_workers
        self.logger = get_logger(__name__)
    
    def process_batch(
        self, 
        items: List[Any], 
        process_func: Callable[[Any], Any],
        progress_callback: Optional[Callable[[int, Any], None]] = None
    ) -> List[Tuple[Any, Optional[Exception]]]:
        """
        Process items concurrently.
        
        Args:
            items: List of items to process
            process_func: Function to apply to each item
            progress_callback: Optional callback for progress updates
            
        Returns:
            List of (result, exception) tuples
        """
        results = []
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all tasks
            future_to_item = {
                executor.submit(process_func, item): item 
                for item in items
            }
            
            # Collect results as they complete
            for i, future in enumerate(concurrent.futures.as_completed(future_to_item), 1):
                item = future_to_item[future]
                
                try:
                    result = future.result()
                    results.append((result, None))
                    
                    if progress_callback:
                        progress_callback(i, result)
                
                except Exception as e:
                    self.logger.warning(f"Error processing item: {e}")
                    results.append((None, e))
                    
                    if progress_callback:
                        progress_callback(i, None)
        
        return results
    
    def process_with_timeout(
        self,
        items: List[Any],
        process_func: Callable[[Any], Any],
        timeout: int = 30,
        progress_callback: Optional[Callable[[int, Any], None]] = None
    ) -> List[Tuple[Any, Optional[Exception]]]:
        """
        Process items concurrently with timeout.
        
        Args:
            items: List of items to process
            process_func: Function to apply to each item
            timeout: Timeout per item in seconds
            progress_callback: Optional callback for progress updates
            
        Returns:
            List of (result, exception) tuples
        """
        results = []
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all tasks
            future_to_item = {
                executor.submit(process_func, item): item 
                for item in items
            }
            
            # Collect results with timeout
            for i, (future, item) in enumerate(future_to_item.items(), 1):
                try:
                    result = future.result(timeout=timeout)
                    results.append((result, None))
                    
                    if progress_callback:
                        progress_callback(i, result)
                
                except concurrent.futures.TimeoutError:
                    self.logger.warning(f"Timeout processing item: {item}")
                    results.append((None, TimeoutError(f"Timeout after {timeout}s")))
                    
                    if progress_callback:
                        progress_callback(i, None)
                
                except Exception as e:
                    self.logger.warning(f"Error processing item: {e}")
                    results.append((None, e))
                    
                    if progress_callback:
                        progress_callback(i, None)
        
        return results
    
    def map_parallel(
        self,
        items: List[Any],
        process_func: Callable[[Any], Any]
    ) -> List[Any]:
        """
        Simple parallel map operation.
        
        Args:
            items: List of items to process
            process_func: Function to apply to each item
            
        Returns:
            List of results
        """
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            return list(executor.map(process_func, items))


class BatchProcessor:
    """Processes items in batches for better performance"""
    
    def __init__(self, batch_size: int = 10):
        """
        Initialize batch processor.
        
        Args:
            batch_size: Number of items per batch
        """
        self.batch_size = batch_size
        self.logger = get_logger(__name__)
    
    def process_in_batches(
        self,
        items: List[Any],
        batch_func: Callable[[List[Any]], List[Any]],
        progress_callback: Optional[Callable[[int, int], None]] = None
    ) -> List[Any]:
        """
        Process items in batches.
        
        Args:
            items: List of items to process
            batch_func: Function that processes a batch of items
            progress_callback: Optional callback(processed, total)
            
        Returns:
            List of all results
        """
        results = []
        total = len(items)
        
        for i in range(0, total, self.batch_size):
            batch = items[i:i + self.batch_size]
            
            try:
                batch_results = batch_func(batch)
                results.extend(batch_results)
                
                if progress_callback:
                    progress_callback(min(i + self.batch_size, total), total)
            
            except Exception as e:
                self.logger.error(f"Error processing batch: {e}")
                # Continue with next batch
        
        return results
    
    def create_batches(self, items: List[Any]) -> List[List[Any]]:
        """
        Split items into batches.
        
        Args:
            items: List of items
            
        Returns:
            List of batches
        """
        return [
            items[i:i + self.batch_size]
            for i in range(0, len(items), self.batch_size)
        ]


class RateLimiter:
    """Rate limiter for API calls"""
    
    def __init__(self, calls_per_second: float = 2.0):
        """
        Initialize rate limiter.
        
        Args:
            calls_per_second: Maximum calls per second
        """
        self.calls_per_second = calls_per_second
        self.min_interval = 1.0 / calls_per_second
        self.last_call_time = 0.0
        self.logger = get_logger(__name__)
    
    def wait_if_needed(self):
        """Wait if needed to respect rate limit."""
        import time
        
        current_time = time.time()
        time_since_last_call = current_time - self.last_call_time
        
        if time_since_last_call < self.min_interval:
            sleep_time = self.min_interval - time_since_last_call
            self.logger.debug(f"Rate limiting: sleeping {sleep_time:.2f}s")
            time.sleep(sleep_time)
        
        self.last_call_time = time.time()
    
    def execute_with_rate_limit(self, func: Callable[[], Any]) -> Any:
        """
        Execute function with rate limiting.
        
        Args:
            func: Function to execute
            
        Returns:
            Function result
        """
        self.wait_if_needed()
        return func()


class ResourcePool:
    """Manages a pool of reusable resources"""
    
    def __init__(self, resource_factory: Callable[[], Any], pool_size: int = 5):
        """
        Initialize resource pool.
        
        Args:
            resource_factory: Function to create new resources
            pool_size: Maximum pool size
        """
        self.resource_factory = resource_factory
        self.pool_size = pool_size
        self.available_resources = []
        self.in_use_resources = set()
        self.logger = get_logger(__name__)
    
    def acquire(self) -> Any:
        """Acquire a resource from the pool."""
        if self.available_resources:
            resource = self.available_resources.pop()
            self.logger.debug("Reusing resource from pool")
        else:
            resource = self.resource_factory()
            self.logger.debug("Created new resource")
        
        self.in_use_resources.add(id(resource))
        return resource
    
    def release(self, resource: Any):
        """Release a resource back to the pool."""
        resource_id = id(resource)
        
        if resource_id in self.in_use_resources:
            self.in_use_resources.remove(resource_id)
            
            if len(self.available_resources) < self.pool_size:
                self.available_resources.append(resource)
                self.logger.debug("Resource returned to pool")
            else:
                self.logger.debug("Pool full, resource discarded")
    
    def clear(self):
        """Clear the resource pool."""
        self.available_resources.clear()
        self.in_use_resources.clear()
        self.logger.debug("Resource pool cleared")
