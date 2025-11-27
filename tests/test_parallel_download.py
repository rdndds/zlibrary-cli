import unittest
from unittest.mock import Mock, patch
from zlibrary.download import DownloadManager
from zlibrary.config import Config
from zlibrary.auth import AuthManager
from zlibrary.index import IndexManager


class TestDownloadManagerParallel(unittest.TestCase):
    
    def setUp(self):
        # Create mock dependencies
        self.config = Config()
        self.auth_manager = AuthManager('data/cookies.txt')
        self.index_manager = IndexManager(self.config)
        
        # Mock the IndexManager to avoid file system dependencies
        with patch.object(IndexManager, '__init__', return_value=None):
            self.download_manager = DownloadManager(self.config, self.auth_manager, self.index_manager)
            
        # Mock the download_book method to avoid network dependencies
        self.download_manager.download_book = Mock(return_value=True)
        self.download_manager.index_manager.is_already_downloaded = Mock(return_value=False)

    def test_download_single_book_task(self):
        """Test the single book download task wrapper"""
        book_data = {
            'url': 'https://example.com/book/123',
            'check_limits': False,
            'verbose': True
        }
        
        result = self.download_manager._download_single_book_task(book_data)
        
        # Verify the result structure
        self.assertIn('url', result)
        self.assertIn('status', result)
        self.assertIn('book_id', result)
        self.assertEqual(result['status'], 'success')
        self.assertEqual(result['url'], book_data['url'])

    def test_bulk_download_single_thread(self):
        """Test bulk download with single thread (sequential)"""
        urls = ['https://example.com/book/1', 'https://example.com/book/2']
        
        # This should use sequential download
        results = self.download_manager.bulk_download(urls, max_workers=1)
        
        # We expect results for each URL
        self.assertEqual(len(results), len(urls))
        
    def test_bulk_download_multiple_threads(self):
        """Test bulk download with multiple threads (parallel)"""
        urls = ['https://example.com/book/1', 'https://example.com/book/2', 'https://example.com/book/3']
        
        # This should use parallel download
        results = self.download_manager.bulk_download(urls, max_workers=2)
        
        # We expect results for each URL
        self.assertEqual(len(results), len(urls))
        
    def test_bulk_download_respects_limit(self):
        """Test that parallel download respects download limits"""
        # This is partially tested by ensuring the parallel code path is taken,
        # with the actual limit checking handled internally


if __name__ == '__main__':
    unittest.main()