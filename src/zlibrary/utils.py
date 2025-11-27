"""
Utility functions for Z-Library Search Application
"""
import re
from typing import Optional


def clean_filename(filename: str) -> str:
    """
    Clean a filename by removing or replacing invalid characters

    Args:
        filename: Original filename

    Returns:
        str: Cleaned filename
    """
    # Replace invalid characters for most file systems
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    # Remove control characters
    filename = re.sub(r'[\x00-\x1f\x7f]', '_', filename)
    # Remove leading/trailing dots and spaces which are problematic
    filename = filename.strip('. ')
    # Limit length to prevent file system issues
    if len(filename) > 255:
        name, ext = filename.rsplit('.', 1) if '.' in filename else (filename, '')
        if ext:
            filename = name[:250-len(ext)] + '.' + ext
        else:
            filename = name[:250]

    return filename.strip()


def extract_book_id_from_url(url: str) -> Optional[str]:
    """
    Extract book ID from Z-Library URL

    Args:
        url: Z-Library book URL

    Returns:
        str: Book ID or None if not found
    """
    # Example: https://z-library.sk/book/19217997/c84306/metode-penelitian-hukum.html
    # The book ID is the first number after /book/
    import re
    match = re.search(r'/book/(\d+)', url)
    if match:
        return match.group(1)
    return None


def validate_url(url: str) -> bool:
    """
    Validate if a string is a proper URL
    
    Args:
        url: URL string to validate
        
    Returns:
        bool: True if valid URL, False otherwise
    """
    import urllib.parse
    try:
        result = urllib.parse.urlparse(url)
        return all([result.scheme, result.netloc])
    except Exception:
        return False