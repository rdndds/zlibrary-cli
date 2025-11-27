"""
Base parser class for Z-Library HTML parsing
"""
from abc import ABC, abstractmethod
from bs4 import BeautifulSoup
from typing import Any, Optional
import re

from zlibrary.logging_config import get_logger
from zlibrary.exceptions import ParsingException


class BaseParser(ABC):
    """Base class for HTML parsers"""
    
    def __init__(self):
        self.logger = get_logger(self.__class__.__name__)
    
    def parse(self, html: str) -> Any:
        """
        Parse HTML content.
        
        Args:
            html: HTML string to parse
            
        Returns:
            Parsed data
            
        Raises:
            ParsingException: On parsing errors
        """
        try:
            soup = BeautifulSoup(html, 'html.parser')
            return self._parse_soup(soup)
        except Exception as e:
            self.logger.error(f"Parsing error: {e}")
            raise ParsingException(f"Failed to parse HTML: {e}")
    
    @abstractmethod
    def _parse_soup(self, soup: BeautifulSoup) -> Any:
        """
        Parse BeautifulSoup object.
        
        Args:
            soup: BeautifulSoup object
            
        Returns:
            Parsed data
        """
        pass
    
    def _safe_find(self, soup, *args, **kwargs) -> Optional[Any]:
        """Safely find element, return None on error."""
        try:
            return soup.find(*args, **kwargs)
        except Exception as e:
            self.logger.debug(f"Find failed: {e}")
            return None
    
    def _safe_find_all(self, soup, *args, **kwargs) -> list:
        """Safely find all elements, return empty list on error."""
        try:
            return soup.find_all(*args, **kwargs)
        except Exception as e:
            self.logger.debug(f"Find all failed: {e}")
            return []
    
    def _safe_get_text(self, element, default: str = '') -> str:
        """Safely extract text from element."""
        try:
            if element:
                return element.get_text(strip=True)
            return default
        except Exception as e:
            self.logger.debug(f"Get text failed: {e}")
            return default
    
    def _safe_get_attribute(self, element, attr: str, default: str = '') -> str:
        """Safely get attribute from element."""
        try:
            if element and element.get(attr):
                return element.get(attr)
            return default
        except Exception as e:
            self.logger.debug(f"Get attribute failed: {e}")
            return default
    
    def _extract_with_regex(self, text: str, pattern: str, default: str = '') -> str:
        """Extract text using regex pattern."""
        try:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1) if match.groups() else match.group(0)
            return default
        except Exception as e:
            self.logger.debug(f"Regex extraction failed: {e}")
            return default
