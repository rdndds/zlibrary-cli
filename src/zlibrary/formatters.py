"""
Output Formatters for Z-Library CLI

Handles formatting and displaying output to the user.
"""
from typing import List
from zlibrary.book import Book


class BookFormatter:
    """Formats book information for display"""
    
    @staticmethod
    def format_basic(book: Book, index: int = None) -> str:
        """
        Format book with basic information.
        
        Args:
            book: Book object to format
            index: Optional index number
            
        Returns:
            Formatted string
        """
        lines = []
        if index is not None:
            lines.append(f"{index}. {book.title}")
        else:
            lines.append(f"{book.title}")
        
        lines.append(f"   Author: {book.author}")
        lines.append(f"   Year: {book.year}")
        lines.append(f"   Format: {book.file_type if hasattr(book, 'file_type') else book.format}")
        lines.append(f"   URL: {book.url}")
        
        return '\n'.join(lines)
    
    @staticmethod
    def format_detailed(book: Book, index: int = None) -> str:
        """
        Format book with detailed information.
        
        Args:
            book: Book object to format
            index: Optional index number
            
        Returns:
            Formatted string
        """
        lines = []
        if index is not None:
            lines.append(f"{index}. {book.title}")
        else:
            lines.append(f"{book.title}")
        
        lines.append(f"   Author: {book.author}")
        lines.append(f"   Year: {book.year}")
        lines.append(f"   Format: {book.file_type if hasattr(book, 'file_type') else book.format}")
        
        # Add detailed fields if available
        if hasattr(book, 'language') and book.language:
            lines.append(f"   Language: {book.language}")
        if hasattr(book, 'publisher') and book.publisher:
            lines.append(f"   Publisher: {book.publisher}")
        if hasattr(book, 'isbn') and book.isbn:
            lines.append(f"   ISBN: {book.isbn}")
        if hasattr(book, 'filesize') and book.filesize:
            lines.append(f"   File Size: {book.filesize}")
        if hasattr(book, 'download_url') and book.download_url:
            lines.append(f"   Download URL: {book.download_url}")
        
        lines.append(f"   URL: {book.url}")
        
        # Add description if available (truncated)
        if hasattr(book, 'description') and book.description:
            desc = book.description[:200] + '...' if len(book.description) > 200 else book.description
            lines.append(f"   Description: {desc}")
        
        return '\n'.join(lines)
    
    @staticmethod
    def format_list(books: List[Book], detailed: bool = False) -> str:
        """
        Format a list of books.
        
        Args:
            books: List of Book objects
            detailed: Whether to show detailed information
            
        Returns:
            Formatted string
        """
        if not books:
            return "No books to display."
        
        formatter = BookFormatter.format_detailed if detailed else BookFormatter.format_basic
        lines = []
        
        for i, book in enumerate(books, 1):
            lines.append(formatter(book, i))
            lines.append('')  # Empty line between books
        
        return '\n'.join(lines)


class SearchResultFormatter:
    """Formats search results for display"""
    
    @staticmethod
    def format_header(count: int, search_term: str) -> str:
        """Format search results header."""
        return f"\nFound {count} results for '{search_term}':\n"
    
    @staticmethod
    def format_summary(results: List[Book], search_term: str, detailed: bool = False) -> str:
        """
        Format complete search results.
        
        Args:
            results: List of Book objects
            search_term: Search term used
            detailed: Whether to show detailed information
            
        Returns:
            Formatted string
        """
        lines = []
        lines.append(SearchResultFormatter.format_header(len(results), search_term))
        
        if results:
            lines.append(BookFormatter.format_list(results, detailed))
        else:
            lines.append("No results found.")
        
        return '\n'.join(lines)


class DownloadResultFormatter:
    """Formats download results for display"""
    
    @staticmethod
    def format_summary(results: List[dict]) -> str:
        """
        Format bulk download summary.
        
        Args:
            results: List of download result dictionaries
            
        Returns:
            Formatted string
        """
        successful = sum(1 for r in results if r.get('status') == 'success')
        skipped = sum(1 for r in results if r.get('status') == 'skipped')
        failed = sum(1 for r in results if r.get('status') in ['failed', 'error'])
        
        lines = [
            "\nBulk download completed:",
            f"  Successful: {successful}",
            f"  Skipped: {skipped}",
            f"  Failed: {failed}",
            f"  Total: {len(results)}"
        ]
        
        return '\n'.join(lines)
    
    @staticmethod
    def format_progress(current: int, total: int, book_title: str = None) -> str:
        """
        Format download progress.
        
        Args:
            current: Current download number
            total: Total downloads
            book_title: Optional book title
            
        Returns:
            Formatted string
        """
        if book_title:
            return f"\n[{current}/{total}] Downloading: {book_title}"
        return f"\n[{current}/{total}] Downloading..."


class AccountInfoFormatter:
    """Formats account information for display"""
    
    @staticmethod
    def format_simple(account_info: dict) -> str:
        """
        Format account info in simple mode.
        
        Args:
            account_info: Account information dictionary
            
        Returns:
            Formatted string
        """
        lines = [
            f"Download Count: {account_info['downloads_used']} used / {account_info['daily_limit_total']} total",
            f"You can download {account_info['downloads_remaining']} more book(s) today."
        ]
        return '\n'.join(lines)
    
    @staticmethod
    def format_detailed(account_info: dict) -> str:
        """
        Format account info in detailed mode.
        
        Args:
            account_info: Account information dictionary
            
        Returns:
            Formatted string
        """
        lines = [
            "\nAccount Information:",
            f"Daily Limit: {account_info['daily_limit']}",
            f"Premium Status: {account_info['premium_status']}",
            f"Donation Amount: {account_info['donation_amount']}",
            f"Download Count: {account_info['downloads_used']} used / {account_info['daily_limit_total']} total",
            f"You can download {account_info['downloads_remaining']} more book(s) today."
        ]
        return '\n'.join(lines)
