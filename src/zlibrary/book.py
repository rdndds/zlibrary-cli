"""
Book data class for Z-Library Search Application
"""
from dataclasses import dataclass
from typing import Optional


@dataclass
class Book:
    """Represents a book with its properties"""
    title: str = "Unknown Title"
    author: str = "Unknown Author"
    year: str = "Unknown"
    url: str = ""
    file_type: str = "Unknown"
    format: str = "Unknown"
    language: str = "Unknown"
    publisher: str = "Unknown"
    isbn: str = "Unknown"
    filesize: str = "Unknown"
    description: str = "No description available"
    download_url: str = "Not available"
    
    def to_dict(self) -> dict:
        """Convert Book instance to dictionary"""
        return {
            'title': self.title,
            'author': self.author,
            'year': self.year,
            'url': self.url,
            'file_type': self.file_type,
            'format': self.format,
            'language': self.language,
            'publisher': self.publisher,
            'isbn': self.isbn,
            'filesize': self.filesize,
            'description': self.description,
            'download_url': self.download_url
        }
    
    def get_clean_title(self) -> str:
        """Get a cleaned version of the title for use in filenames or keys"""
        import re
        # Remove special characters but keep spaces
        clean_title = re.sub(r'[^\w\s-]', '', self.title[:50]).strip()
        return clean_title
    
    def get_clean_author(self) -> str:
        """Get a cleaned version of the author for use in filenames or keys"""
        import re
        # Remove special characters but keep first 20 characters
        clean_author = re.sub(r'[^\w\s-]', '', self.author[:20]).strip()
        return clean_author