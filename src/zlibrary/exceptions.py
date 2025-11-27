"""
Custom exception hierarchy for Z-Library Search Application
"""
from typing import Optional, Dict, Any


class ZLibraryException(Exception):
    """Base exception class for Z-Library application"""
    
    def __init__(self, message: str, context: Optional[Dict[str, Any]] = None):
        """
        Initialize exception with message and optional context.
        
        Args:
            message: Error message
            context: Optional dictionary with additional context (URL, book_id, etc.)
        """
        super().__init__(message)
        self.message = message
        self.context = context or {}
    
    def __str__(self):
        """String representation with context."""
        if self.context:
            context_str = ", ".join(f"{k}={v}" for k, v in self.context.items())
            return f"{self.message} [{context_str}]"
        return self.message


class NetworkException(ZLibraryException):
    """Exception for network-related errors"""
    pass


class ConnectionException(NetworkException):
    """Exception for connection errors"""
    pass


class TimeoutException(NetworkException):
    """Exception for timeout errors"""
    pass


class AuthenticationException(NetworkException):
    """Exception for authentication errors"""
    pass


class ValidationException(ZLibraryException):
    """Exception for validation errors"""
    pass


class ProcessingException(ZLibraryException):
    """Exception for processing errors"""
    pass


class StorageException(ZLibraryException):
    """Exception for storage-related errors"""
    pass


class BookNotFoundException(ZLibraryException):
    """Exception when a book is not found"""
    pass


class DownloadLimitExceededException(ZLibraryException):
    """Exception when daily download limit is exceeded"""
    pass


class ParsingException(ProcessingException):
    """Exception for HTML parsing errors"""
    pass


class ConfigurationException(ZLibraryException):
    """Exception for configuration errors"""
    pass