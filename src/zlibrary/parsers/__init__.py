"""
HTML Parsers for Z-Library

This module contains parser classes for extracting data from Z-Library HTML pages.
"""

from zlibrary.parsers.base import BaseParser
from zlibrary.parsers.search_parser import SearchResultParser
from zlibrary.parsers.book_parser import BookDetailsParser

__all__ = [
    'BaseParser',
    'SearchResultParser',
    'BookDetailsParser',
]
