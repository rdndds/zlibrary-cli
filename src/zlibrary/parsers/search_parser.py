"""
Parser for Z-Library search results
"""
import re
from typing import List
from bs4 import BeautifulSoup

from zlibrary.parsers.base import BaseParser
from zlibrary.book import Book
from zlibrary.constants import BASE_URL


class SearchResultParser(BaseParser):
    """Parser for search result pages"""
    
    def _parse_soup(self, soup: BeautifulSoup) -> List[Book]:
        """
        Parse search results page.
        
        Args:
            soup: BeautifulSoup object of search page
            
        Returns:
            List of Book objects
        """
        books = []
        
        # Find all book containers
        containers = self._safe_find_all(
            soup, 
            'div', 
            class_=re.compile(r'book-item.*resItemBox', re.IGNORECASE)
        )
        
        self.logger.debug(f"Found {len(containers)} book containers")
        
        for container in containers:
            book = self._parse_book_container(container)
            if book:
                books.append(book)
        
        return books
    
    def _parse_book_container(self, container) -> Book:
        """
        Parse a single book container.
        
        Args:
            container: BeautifulSoup element
            
        Returns:
            Book object or None
        """
        try:
            bookcard = self._safe_find(container, 'z-bookcard')
            
            # Extract book information
            title = self._extract_title(container, bookcard)
            author = self._extract_author(container, bookcard)
            year = self._extract_year(container, bookcard)
            url = self._extract_url(container, bookcard)
            file_type = self._extract_file_type(container, bookcard)
            
            return Book(
                title=title,
                author=author,
                year=year,
                url=url,
                file_type=file_type
            )
        except Exception as e:
            self.logger.warning(f"Failed to parse book container: {e}")
            return None
    
    def _extract_title(self, container, bookcard) -> str:
        """Extract book title."""
        # Try bookcard slot
        if bookcard:
            title_slot = self._safe_find(bookcard, 'div', attrs={'slot': 'title'})
            if title_slot:
                return self._safe_get_text(title_slot, 'Unknown Title')
        
        return 'Unknown Title'
    
    def _extract_author(self, container, bookcard) -> str:
        """Extract book author."""
        # Try bookcard slot
        if bookcard:
            author_slot = self._safe_find(bookcard, 'div', attrs={'slot': 'author'})
            if author_slot:
                author = self._safe_get_text(author_slot, 'Unknown Author')
                # Clean up author text (remove brackets)
                author = re.sub(r'\s*\[.*\]', '', author)
                return author
        
        return 'Unknown Author'
    
    def _extract_year(self, container, bookcard) -> str:
        """Extract publication year."""
        # Try bookcard attribute
        if bookcard:
            year = self._safe_get_attribute(bookcard, 'year')
            if year and year.isdigit() and 1000 < int(year) < 2030:
                return year
        
        # Try to find in container text
        text = self._safe_get_text(container)
        year = self._extract_with_regex(text, r'\b(19|20)\d{2}\b')
        return year if year else 'Unknown'
    
    def _extract_url(self, container, bookcard) -> str:
        """Extract book URL."""
        # Try bookcard href
        if bookcard:
            url = self._safe_get_attribute(bookcard, 'href')
            if url:
                if not url.startswith('http'):
                    return BASE_URL + url
                return url
        
        # Try to find link element
        link_elem = self._safe_find(container, 'a', href=re.compile(r'/book/'))
        if link_elem:
            url = self._safe_get_attribute(link_elem, 'href')
            if url and not url.startswith('http'):
                return BASE_URL + url
            return url
        
        return ''
    
    def _extract_file_type(self, container, bookcard) -> str:
        """Extract file type."""
        # Try bookcard extension
        if bookcard:
            extension = self._safe_get_attribute(bookcard, 'extension')
            if extension:
                return extension
        
        # Look for file type in text
        text = self._safe_get_text(container)
        file_type = self._extract_with_regex(
            text, 
            r'\b(pdf|epub|mobi|djvu|fb2)\b',
            'Unknown'
        )
        return file_type
