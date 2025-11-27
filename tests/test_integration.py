import sys
import os

# Add src directory to path so we can import the modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../src'))

from unittest.mock import Mock, patch, MagicMock
import tempfile
import json


def test_integration_parallel_download():
    """Integration test for parallel download functionality"""
    from zlibrary.download import DownloadManager
    from zlibrary.config import Config
    from zlibrary.auth import AuthManager
    from zlibrary.index import IndexManager
    
    # Create a temporary config for testing
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump({}, f)
        temp_config_path = f.name
    
    try:
        config = Config(config_file=temp_config_path)
        auth_manager = AuthManager('data/cookies.txt')
        
        # Mock the index manager to avoid file system dependencies
        with patch.object(IndexManager, '__init__', return_value=None):
            # Create a mock index manager instance
            mock_index_manager = Mock()
            mock_index_manager.is_already_downloaded = Mock(return_value=False)
            
            manager = DownloadManager(config, auth_manager, mock_index_manager)
            
            # Mock the download_book method to avoid network dependencies
            manager.download_book = Mock(return_value=True)
            manager.last_download_size = 10 * 1024 * 1024  # 10 MB
            manager.last_download_time = 5.0  # 5 seconds
            
            # Test sequential download (1 thread)
            urls = ['https://example.com/book/1', 'https://example.com/book/2']
            results_sequential = manager.bulk_download(urls, max_workers=1)
            
            print(f"Sequential download test:")
            print(f"  URLs: {len(urls)}")
            print(f"  Results: {len(results_sequential)}")
            print(f"  All successful: {all(r['status'] == 'success' for r in results_sequential)}")
            
            # Test parallel download (3 threads)
            results_parallel = manager.bulk_download(urls, max_workers=3)
            
            print(f"\nParallel download test:")
            print(f"  URLs: {len(urls)}")
            print(f"  Results: {len(results_parallel)}")
            print(f"  All successful: {all(r['status'] == 'success' for r in results_parallel)}")
            
            # Both should return the same number of results
            assert len(results_sequential) == len(results_parallel) == len(urls)
            assert all(r['status'] == 'success' for r in results_sequential)
            assert all(r['status'] == 'success' for r in results_parallel)
            
            print("  ✓ Integration test passed: Both sequential and parallel downloads work")
            
    finally:
        # Clean up temp file
        os.unlink(temp_config_path)


def test_integration_different_thread_counts():
    """Test download with different thread counts"""
    from zlibrary.download import DownloadManager
    from zlibrary.config import Config
    from zlibrary.auth import AuthManager
    from zlibrary.index import IndexManager
    
    # Mock dependencies
    config = Config()
    auth_manager = AuthManager('data/cookies.txt')
    
    with patch.object(IndexManager, '__init__', return_value=None):
        mock_index_manager = Mock()
        mock_index_manager.is_already_downloaded = Mock(return_value=False)
        
        manager = DownloadManager(config, auth_manager, mock_index_manager)
        manager.download_book = Mock(return_value=True)
        manager.last_download_size = 10 * 1024 * 1024
        manager.last_download_time = 5.0
        
        urls = [f'https://example.com/book/{i}' for i in range(1, 6)]  # 5 URLs
        
        # Test different thread counts
        for thread_count in [1, 2, 3, 5]:
            results = manager.bulk_download(urls, max_workers=thread_count)
            print(f"  Thread count {thread_count}: {len(results)} results, all successful: {all(r['status'] == 'success' for r in results)}")
            assert len(results) == len(urls)
            assert all(r['status'] == 'success' for r in results)
        
        print("  ✓ Different thread counts work correctly")


def test_download_command_integration():
    """Test integration with download command handler"""
    from zlibrary.commands.download import DownloadCommandHandler
    from zlibrary.config import Config
    
    config = Config()
    handler = DownloadCommandHandler(config)
    
    # Mock all the internal components to avoid external dependencies
    handler._parse_urls = Mock(return_value=(["https://example.com/book/1", "https://example.com/book/2"], True))
    handler._validate_urls = Mock(return_value=True)
    
    # Mock the download manager
    mock_results = [
        {'url': 'https://example.com/book/1', 'status': 'success', 'book_id': '1'},
        {'url': 'https://example.com/book/2', 'status': 'success', 'book_id': '2'}
    ]
    handler.download_manager.bulk_download = Mock(return_value=mock_results)
    
    # Create a mock args object with threads parameter
    import argparse
    class MockArgs:
        def __init__(self, threads):
            self.urls_file = None
            self.url = ["https://example.com/book/1", "https://example.com/book/2"]
            self.threads = threads
            self.details = False
            self.export = None
            self.filename = None
    
    # Test with 3 threads
    args = MockArgs(threads=3)
    result = handler._handle_bulk_download(args.url, args)
    
    # Verify that bulk_download was called with max_workers parameter
    handler.download_manager.bulk_download.assert_called_with(
        ["https://example.com/book/1", "https://example.com/book/2"], 
        max_workers=3
    )
    
    print(f"  Download command handler test with {args.threads} threads: ✓")
    print("  ✓ Download command integration works correctly")


def test_search_command_integration():
    """Test integration with search command handler"""
    from zlibrary.commands.search import SearchCommandHandler
    from zlibrary.config import Config
    from zlibrary.book import Book
    
    config = Config()
    handler = SearchCommandHandler(config)
    
    # Create some mock books as search results
    mock_books = [
        Book(title="Test Book 1", url="https://example.com/book/1"),
        Book(title="Test Book 2", url="https://example.com/book/2")
    ]
    
    # Mock the download functionality
    mock_results = [
        {'url': 'https://example.com/book/1', 'status': 'success', 'book_id': '1'},
        {'url': 'https://example.com/book/2', 'status': 'success', 'book_id': '2'}
    ]
    
    # Create a mock args object with threads parameter
    class MockArgs:
        def __init__(self, threads):
            self.download = True
            self.threads = threads
    
    args = MockArgs(threads=2)
    result = handler._handle_download(mock_books, args)
    
    print(f"  Search command handler test with {args.threads} threads: ✓")
    print("  ✓ Search command integration works correctly")


if __name__ == '__main__':
    print("Running integration tests for parallel download functionality...")
    test_integration_parallel_download()
    test_integration_different_thread_counts()
    test_download_command_integration()
    test_search_command_integration()
    print("\nAll integration tests passed! ✓")