import sys
import os

# Add src directory to path so we can import the modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../src'))

from zlibrary.concurrent import ConcurrentProcessor
from unittest.mock import Mock, patch


def test_concurrent_processor():
    """Test the concurrent processor functionality."""
    def square(x):
        return x * x

    processor = ConcurrentProcessor(max_workers=3)
    items = [1, 2, 3, 4, 5]

    results_with_exceptions = processor.process_batch(
        items=items,
        process_func=square
    )

    # Extract results
    results = [result for result, exception in results_with_exceptions if result is not None]
    expected = [1, 4, 9, 16, 25]

    print(f"Concurrent processor test:")
    print(f"  Input: {items}")
    print(f"  Expected: {expected} (order may vary due to parallel processing)")

    actual = [r for r, _ in results_with_exceptions if r is not None]
    # Since parallel processing doesn't preserve order, we just check that all results are there
    actual_set = set(actual)
    expected_set = set(expected)
    assert actual_set == expected_set, f"Expected {expected_set}, got {actual_set}"
    print(f"  Got: {actual} (order may vary)")
    print("  ✓ Concurrent processor works correctly")


def test_download_manager_interface():
    """Test that the download manager bulk_download interface works properly."""
    from zlibrary.download import DownloadManager
    from zlibrary.config import Config
    from zlibrary.auth import AuthManager
    from zlibrary.index import IndexManager

    # Create instances
    config = Config()
    auth_manager = AuthManager('data/cookies.txt')

    # Mock the index manager to avoid file system dependencies
    with patch.object(IndexManager, '__init__', return_value=None):
        manager = DownloadManager(config, auth_manager, None)
        manager.index_manager = Mock()
        manager.index_manager.is_already_downloaded = Mock(return_value=False)

        # Mock the download_book method
        manager.download_book = Mock(return_value=True)

        # Test with max_workers=None (should use config default)
        urls = ['https://example.com/book/1']
        try:
            results = manager.bulk_download(urls, max_workers=None)
            print("✓ DownloadManager bulk_download interface works")
        except Exception as e:
            print(f"✗ DownloadManager bulk_download interface failed: {e}")
            raise


if __name__ == '__main__':
    print("Running basic functionality tests...")
    test_concurrent_processor()
    test_download_manager_interface()
    print("All basic tests passed!")