"""
Input Validators for Z-Library CLI

Provides validation for user inputs with clear error messages.
"""
import re
import os
from typing import Tuple, Optional, List
from urllib.parse import urlparse


class ValidationResult:
    """Result of a validation operation"""
    
    def __init__(self, is_valid: bool, error_message: str = None):
        self.is_valid = is_valid
        self.error_message = error_message
    
    def __bool__(self):
        return self.is_valid
    
    def __str__(self):
        return self.error_message if not self.is_valid else "Valid"


class URLValidator:
    """Validates Z-Library URLs"""
    
    VALID_DOMAINS = [
        'z-library.sk',
        'z-lib.org',
        'zlibrary.to',
        'singlelogin.re',
        'singlelogin.se',
    ]
    
    @staticmethod
    def validate(url: str) -> ValidationResult:
        """
        Validate a Z-Library URL.
        
        Args:
            url: URL to validate
            
        Returns:
            ValidationResult with is_valid and error_message
        """
        if not url:
            return ValidationResult(False, "URL cannot be empty")
        
        if not url.startswith(('http://', 'https://')):
            return ValidationResult(
                False, 
                f"Invalid URL format: '{url}'. Must start with http:// or https://"
            )
        
        try:
            parsed = urlparse(url)
            domain = parsed.netloc
            
            # Check if it's a valid Z-Library domain
            is_valid_domain = any(valid_domain in domain for valid_domain in URLValidator.VALID_DOMAINS)
            
            if not is_valid_domain:
                return ValidationResult(
                    False,
                    f"Not a valid Z-Library URL: '{url}'. Must be from domains like z-library.sk"
                )
            
            # Check if it looks like a book URL (has /book/ in path)
            if '/book/' not in url:
                return ValidationResult(
                    False,
                    f"URL does not appear to be a book page: '{url}'. Should contain /book/"
                )
            
            return ValidationResult(True)
            
        except Exception as e:
            return ValidationResult(False, f"Invalid URL: {e}")
    
    @staticmethod
    def validate_batch(urls: List[str]) -> Tuple[List[str], List[Tuple[str, str]]]:
        """
        Validate multiple URLs.
        
        Args:
            urls: List of URLs to validate
            
        Returns:
            Tuple of (valid_urls, invalid_urls_with_errors)
        """
        valid = []
        invalid = []
        
        for url in urls:
            result = URLValidator.validate(url)
            if result.is_valid:
                valid.append(url)
            else:
                invalid.append((url, result.error_message))
        
        return valid, invalid


class FileValidator:
    """Validates file paths and permissions"""
    
    @staticmethod
    def validate_readable_file(file_path: str) -> ValidationResult:
        """Validate that file exists and is readable."""
        if not file_path:
            return ValidationResult(False, "File path cannot be empty")
        
        if not os.path.exists(file_path):
            return ValidationResult(False, f"File not found: '{file_path}'")
        
        if not os.path.isfile(file_path):
            return ValidationResult(False, f"Path is not a file: '{file_path}'")
        
        if not os.access(file_path, os.R_OK):
            return ValidationResult(False, f"File is not readable: '{file_path}'")
        
        return ValidationResult(True)
    
    @staticmethod
    def validate_writable_directory(dir_path: str) -> ValidationResult:
        """Validate that directory exists and is writable."""
        if not dir_path:
            return ValidationResult(False, "Directory path cannot be empty")
        
        if not os.path.exists(dir_path):
            # Try to create it
            try:
                os.makedirs(dir_path, exist_ok=True)
                return ValidationResult(True)
            except Exception as e:
                return ValidationResult(False, f"Cannot create directory '{dir_path}': {e}")
        
        if not os.path.isdir(dir_path):
            return ValidationResult(False, f"Path is not a directory: '{dir_path}'")
        
        if not os.access(dir_path, os.W_OK):
            return ValidationResult(False, f"Directory is not writable: '{dir_path}'")
        
        return ValidationResult(True)
    
    @staticmethod
    def validate_filename(filename: str) -> ValidationResult:
        """Validate filename (no path separators, no invalid characters)."""
        if not filename:
            return ValidationResult(False, "Filename cannot be empty")
        
        # Check for path separators
        if '/' in filename or '\\' in filename:
            return ValidationResult(False, f"Filename cannot contain path separators: '{filename}'")
        
        # Check for invalid characters (varies by OS, using common set)
        invalid_chars = '<>:"|?*'
        if any(char in filename for char in invalid_chars):
            return ValidationResult(
                False, 
                f"Filename contains invalid characters: '{filename}'. Avoid: {invalid_chars}"
            )
        
        return ValidationResult(True)


class SearchValidator:
    """Validates search parameters"""
    
    @staticmethod
    def validate_query(query: str) -> ValidationResult:
        """Validate search query."""
        if not query:
            return ValidationResult(False, "Search query cannot be empty")
        
        if len(query.strip()) < 2:
            return ValidationResult(False, "Search query must be at least 2 characters long")
        
        if len(query) > 500:
            return ValidationResult(False, "Search query is too long (max 500 characters)")
        
        return ValidationResult(True)
    
    @staticmethod
    def validate_limit(limit: int) -> ValidationResult:
        """Validate search result limit."""
        if limit < 1:
            return ValidationResult(False, "Limit must be at least 1")
        
        if limit > 1000:
            return ValidationResult(
                False, 
                "Limit is too high (max 1000). Use --no-limit for unlimited results."
            )
        
        return ValidationResult(True)


class ExportValidator:
    """Validates export parameters"""
    
    VALID_FORMATS = ['json', 'bibtex', 'both']
    
    @staticmethod
    def validate_format(format_str: str) -> ValidationResult:
        """Validate export format."""
        if not format_str:
            return ValidationResult(False, "Export format cannot be empty")
        
        if format_str not in ExportValidator.VALID_FORMATS:
            return ValidationResult(
                False,
                f"Invalid export format: '{format_str}'. Valid formats: {', '.join(ExportValidator.VALID_FORMATS)}"
            )
        
        return ValidationResult(True)


class ConfigValidator:
    """Validates configuration values"""
    
    @staticmethod
    def validate_cookies_file(file_path: str) -> ValidationResult:
        """Validate cookies file."""
        result = FileValidator.validate_readable_file(file_path)
        if not result.is_valid:
            return ValidationResult(
                False,
                f"Invalid cookies file: {result.error_message}. "
                "Please ensure your cookies.txt file exists and is readable."
            )
        
        # Check if file has content
        try:
            if os.path.getsize(file_path) == 0:
                return ValidationResult(
                    False,
                    f"Cookies file is empty: '{file_path}'. Please export cookies from your browser."
                )
        except Exception as e:
            return ValidationResult(False, f"Cannot read cookies file: {e}")
        
        return ValidationResult(True)
    
    @staticmethod
    def validate_timeout(timeout: int) -> ValidationResult:
        """Validate timeout value."""
        if timeout < 1:
            return ValidationResult(False, "Timeout must be at least 1 second")
        
        if timeout > 300:
            return ValidationResult(
                False, 
                "Timeout is too high (max 300 seconds = 5 minutes)"
            )
        
        return ValidationResult(True)
    
    @staticmethod
    def validate_max_retries(retries: int) -> ValidationResult:
        """Validate max retries value."""
        if retries < 0:
            return ValidationResult(False, "Max retries cannot be negative")
        
        if retries > 10:
            return ValidationResult(
                False,
                "Max retries is too high (max 10)"
            )
        
        return ValidationResult(True)


class InputSanitizer:
    """Sanitizes user inputs"""
    
    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """
        Sanitize filename by removing invalid characters.
        
        Args:
            filename: Original filename
            
        Returns:
            Sanitized filename
        """
        # Remove invalid characters
        sanitized = re.sub(r'[<>:"|?*]', '_', filename)
        
        # Remove path separators
        sanitized = sanitized.replace('/', '_').replace('\\', '_')
        
        # Trim whitespace
        sanitized = sanitized.strip()
        
        # Limit length
        if len(sanitized) > 200:
            name, ext = os.path.splitext(sanitized)
            sanitized = name[:200-len(ext)] + ext
        
        return sanitized if sanitized else 'untitled'
    
    @staticmethod
    def sanitize_search_query(query: str) -> str:
        """
        Sanitize search query.
        
        Args:
            query: Original query
            
        Returns:
            Sanitized query
        """
        # Trim whitespace
        sanitized = query.strip()
        
        # Collapse multiple spaces
        sanitized = re.sub(r'\s+', ' ', sanitized)
        
        # Limit length
        if len(sanitized) > 500:
            sanitized = sanitized[:500]
        
        return sanitized
