"""
Parser for Z-Library book details pages
"""
import re
from typing import Dict, Any
from bs4 import BeautifulSoup

from zlibrary.parsers.base import BaseParser
from zlibrary.book import Book
from zlibrary.constants import BASE_URL


class BookDetailsParser(BaseParser):
    """Parser for book details pages"""
    
    def _parse_soup(self, soup: BeautifulSoup) -> Book:
        """
        Parse book details page.
        
        Args:
            soup: BeautifulSoup object of book details page
            
        Returns:
            Book object with detailed information
        """
        bookcard = self._safe_find(soup, 'z-bookcard')
        
        # Extract all book details
        details = {
            'title': self._extract_title(soup, bookcard),
            'author': self._extract_author(soup, bookcard),
            'year': self._extract_year(soup, bookcard),
            'language': self._extract_language(soup, bookcard),
            'publisher': self._extract_publisher(soup, bookcard),
            'isbn': self._extract_isbn(soup, bookcard),
            'format': self._extract_format(soup, bookcard),
            'filesize': self._extract_filesize(soup, bookcard),
            'description': self._extract_description(soup),
            'download_url': self._extract_download_url(soup, bookcard),
        }
        
        return Book(**details)
    
    def _extract_title(self, soup: BeautifulSoup, bookcard) -> str:
        """Extract book title."""
        # Try bookcard attribute
        if bookcard:
            title = self._safe_get_attribute(bookcard, 'title')
            if title:
                return title
        
        # Try common title elements
        for tag in ['h1', 'h2', 'h3']:
            elem = self._safe_find(soup, tag)
            if elem:
                return self._safe_get_text(elem, 'Unknown Title')
        
        # Try title element with class
        elem = self._safe_find(soup, class_=re.compile(r'.*title.*', re.IGNORECASE))
        if elem:
            return self._safe_get_text(elem, 'Unknown Title')
        
        # Try page title tag
        title_tag = self._safe_find(soup, 'title')
        if title_tag:
            full_title = self._safe_get_text(title_tag)
            parts = full_title.split(' | ')
            if parts:
                return parts[0]
        
        return 'Unknown Title'
    
    def _extract_author(self, soup: BeautifulSoup, bookcard) -> str:
        """Extract book author."""
        # Try bookcard attributes
        if bookcard:
            for attr in ['writer', 'author']:
                author = self._safe_get_attribute(bookcard, attr)
                if author:
                    return author
        
        # Try page title
        title_tag = self._safe_find(soup, 'title')
        if title_tag:
            full_title = self._safe_get_text(title_tag)
            parts = full_title.split(' | ')
            if len(parts) >= 2 and 'Z-Library' not in parts[1]:
                return parts[1]
        
        # Try author element
        elem = self._safe_find(soup, class_=re.compile(r'.*author.*', re.IGNORECASE))
        if elem:
            author = self._safe_get_text(elem, 'Unknown Author')
            # Remove "by" prefix
            author = re.sub(r'^by\s+', '', author, flags=re.IGNORECASE)
            return author
        
        return 'Unknown Author'
    
    def _extract_year(self, soup: BeautifulSoup, bookcard) -> str:
        """Extract publication year."""
        # Try bookcard
        if bookcard:
            year = self._safe_get_attribute(bookcard, 'year')
            if year and year != 'Unknown':
                return year
        
        # Try property element
        elem = self._safe_find(soup, class_=re.compile(r'.*property_year.*', re.IGNORECASE))
        if elem:
            text = self._safe_get_text(elem)
            year = self._extract_with_regex(text, r'\b(19|20)\d{2}\b')
            if year:
                return year
        
        return 'Unknown'
    
    def _extract_language(self, soup: BeautifulSoup, bookcard) -> str:
        """Extract language."""
        # Try bookcard
        if bookcard:
            lang = self._safe_get_attribute(bookcard, 'language')
            if lang and lang != 'Unknown':
                return lang
        
        # Try property element
        elem = self._safe_find(soup, class_=re.compile(r'.*property_language.*', re.IGNORECASE))
        if elem:
            text = self._safe_get_text(elem)
            if ':' in text:
                return text.split(':')[1].strip()
            return re.sub(r'^Language\s*', '', text, flags=re.IGNORECASE).strip()
        
        return 'Unknown'
    
    def _extract_publisher(self, soup: BeautifulSoup, bookcard) -> str:
        """Extract publisher."""
        # Try bookcard
        if bookcard:
            pub = self._safe_get_attribute(bookcard, 'publisher')
            if pub and pub != 'Unknown':
                return pub
        
        # Try property element
        elem = self._safe_find(soup, class_=re.compile(r'.*property_publisher.*', re.IGNORECASE))
        if elem:
            text = self._safe_get_text(elem)
            if ':' in text:
                return text.split(':')[1].strip()
            return re.sub(r'^Publisher\s*', '', text, flags=re.IGNORECASE).strip()
        
        return 'Unknown'
    
    def _extract_isbn(self, soup: BeautifulSoup, bookcard) -> str:
        """Extract ISBN."""
        # Try bookcard
        if bookcard:
            isbn = self._safe_get_attribute(bookcard, 'isbn')
            if isbn and isbn != 'Unknown':
                return isbn
        
        # Try property elements (may be multiple ISBNs)
        elems = self._safe_find_all(soup, class_=re.compile(r'.*property_isbn.*', re.IGNORECASE))
        isbns = []
        for elem in elems:
            text = self._safe_get_text(elem)
            if ':' in text:
                isbn = text.split(':')[1].strip()
                isbns.append(isbn)
        
        return ', '.join(isbns) if isbns else 'Unknown'
    
    def _extract_format(self, soup: BeautifulSoup, bookcard) -> str:
        """Extract file format."""
        # Try bookcard
        if bookcard:
            fmt = self._safe_get_attribute(bookcard, 'extension')
            if fmt and fmt != 'Unknown':
                return fmt
        
        # Try property elements
        elems = self._safe_find_all(soup, class_=re.compile(r'.*book-property__extension.*', re.IGNORECASE))
        for elem in elems:
            text = self._safe_get_text(elem)
            if text:
                return text.lower()
        
        return 'Unknown'
    
    def _extract_filesize(self, soup: BeautifulSoup, bookcard) -> str:
        """Extract file size."""
        # Try bookcard
        if bookcard:
            size = self._safe_get_attribute(bookcard, 'filesize')
            if size and size != 'Unknown':
                return size
        
        # Try to find size in page text
        text = soup.get_text()
        size = self._extract_with_regex(text, r'(\d+\.?\d*\s*(?:MB|KB|GB))')
        if size:
            return size
        
        # Try download link text
        elem = self._safe_find(soup, 'a', string=re.compile(r'MB|KB|GB', re.IGNORECASE))
        if elem:
            text = self._safe_get_text(elem)
            size = self._extract_with_regex(text, r'(\d+\.?\d*\s*(?:MB|KB|GB))')
            if size:
                return size
        
        return 'Unknown'
    
    def _extract_description(self, soup: BeautifulSoup) -> str:
        """Extract book description."""
        elem = self._safe_find(soup, class_=re.compile(r'.*description.*|.*annotation.*', re.IGNORECASE))
        if elem:
            desc = self._safe_get_text(elem)
            # Truncate if too long
            if len(desc) > 500:
                return desc[:500] + '...'
            return desc
        
        return 'No description available'
    
    def _extract_download_url(self, soup: BeautifulSoup, bookcard) -> str:
        """Extract download URL."""
        # Try bookcard download attribute
        if bookcard:
            url = self._safe_get_attribute(bookcard, 'download')
            if url:
                if not url.startswith('http'):
                    return BASE_URL + url
                return url
        
        # Try download link element
        elem = self._safe_find(soup, 'a', class_=re.compile(r'download|dl', re.IGNORECASE))
        if not elem:
            elem = self._safe_find(soup, 'a', href=re.compile(r'/dl/|/download'))
        
        if elem:
            url = self._safe_get_attribute(elem, 'href')
            if url:
                if not url.startswith('http'):
                    return BASE_URL + url
                return url
        
        return 'Not available'
