"""
Error Handler for Z-Library CLI

Provides user-friendly error messages and suggestions.
"""
from typing import Optional
import requests
from zlibrary.logging_config import get_logger


class ErrorHandler:
    """Handles errors with user-friendly messages"""
    
    def __init__(self):
        self.logger = get_logger(__name__)
    
    def handle_network_error(self, error: Exception, context: str = None) -> str:
        """
        Handle network-related errors.
        
        Args:
            error: The exception that occurred
            context: Optional context about what was being done
            
        Returns:
            User-friendly error message
        """
        context_prefix = f"While {context}: " if context else ""
        
        if isinstance(error, requests.exceptions.ConnectionError):
            return (
                f"{context_prefix}Cannot connect to Z-Library.\n"
                "Possible causes:\n"
                "  • No internet connection\n"
                "  • Z-Library may be temporarily down\n"
                "  • Firewall or proxy blocking connection\n"
                "Solution: Check your internet connection and try again."
            )
        
        elif isinstance(error, requests.exceptions.Timeout):
            return (
                f"{context_prefix}Request timed out.\n"
                "Possible causes:\n"
                "  • Slow internet connection\n"
                "  • Z-Library is slow to respond\n"
                "Solution: Try again or increase timeout in configuration."
            )
        
        elif isinstance(error, requests.exceptions.HTTPError):
            status_code = getattr(error.response, 'status_code', None)
            
            if status_code == 403:
                return (
                    f"{context_prefix}Access forbidden (403).\n"
                    "Possible causes:\n"
                    "  • Invalid or expired cookies\n"
                    "  • IP address blocked\n"
                    "  • Authentication required\n"
                    "Solution: Update your cookies.txt file from browser."
                )
            
            elif status_code == 404:
                return (
                    f"{context_prefix}Resource not found (404).\n"
                    "Possible causes:\n"
                    "  • Book URL is invalid or outdated\n"
                    "  • Book was removed from Z-Library\n"
                    "Solution: Check the URL and try searching for the book again."
                )
            
            elif status_code == 429:
                return (
                    f"{context_prefix}Too many requests (429).\n"
                    "You've been rate-limited by Z-Library.\n"
                    "Solution: Wait a few minutes before trying again."
                )
            
            elif status_code >= 500:
                return (
                    f"{context_prefix}Z-Library server error ({status_code}).\n"
                    "Z-Library is experiencing technical difficulties.\n"
                    "Solution: Try again later."
                )
            
            else:
                return f"{context_prefix}HTTP error {status_code}: {error}"
        
        else:
            return f"{context_prefix}Network error: {error}"
    
    def handle_authentication_error(self, context: str = None) -> str:
        """Handle authentication-related errors."""
        context_prefix = f"While {context}: " if context else ""
        
        return (
            f"{context_prefix}Authentication failed.\n"
            "Possible causes:\n"
            "  • Cookies file is missing or empty\n"
            "  • Cookies are invalid or expired\n"
            "  • Not logged into Z-Library\n"
            "Solution:\n"
            "  1. Log into Z-Library in your browser\n"
            "  2. Export cookies using a browser extension\n"
            "  3. Save cookies to data/cookies.txt\n"
            "  4. Try again"
        )
    
    def handle_parsing_error(self, context: str = None) -> str:
        """Handle parsing-related errors."""
        context_prefix = f"While {context}: " if context else ""
        
        return (
            f"{context_prefix}Failed to parse page content.\n"
            "Possible causes:\n"
            "  • Z-Library page structure changed\n"
            "  • Received unexpected page format\n"
            "  • Connection interrupted during download\n"
            "Solution: This may require an update to the application. Please report the issue."
        )
    
    def handle_file_error(self, error: Exception, operation: str, file_path: str) -> str:
        """Handle file-related errors."""
        if isinstance(error, FileNotFoundError):
            return (
                f"Cannot {operation}: File not found '{file_path}'.\n"
                "Solution: Check that the file path is correct."
            )
        
        elif isinstance(error, PermissionError):
            return (
                f"Cannot {operation}: Permission denied '{file_path}'.\n"
                "Solution: Check file/directory permissions."
            )
        
        elif isinstance(error, IOError):
            return (
                f"Cannot {operation}: I/O error for '{file_path}'.\n"
                f"Details: {error}\n"
                "Solution: Check disk space and file system."
            )
        
        else:
            return f"Cannot {operation} '{file_path}': {error}"
    
    def handle_download_limit_error(self, limit_info: dict = None) -> str:
        """Handle download limit errors."""
        if limit_info:
            used = limit_info.get('downloads_used', 'unknown')
            total = limit_info.get('daily_limit_total', 'unknown')
            
            return (
                f"Download limit reached: {used}/{total} downloads used today.\n"
                "Solutions:\n"
                "  • Wait until tomorrow for limit to reset\n"
                "  • Upgrade to premium account for more downloads\n"
                "  • Use 'account' command to check current limits"
            )
        else:
            return (
                "Download limit reached.\n"
                "Solution: Check limits with 'account' command or wait until tomorrow."
            )
    
    def handle_validation_error(self, validation_message: str, field: str = None) -> str:
        """Handle validation errors."""
        field_prefix = f"Invalid {field}: " if field else "Validation error: "
        return f"{field_prefix}{validation_message}"
    
    def suggest_alternative(self, failed_action: str, alternatives: list) -> str:
        """Suggest alternative actions."""
        suggestions = "\n".join(f"  • {alt}" for alt in alternatives)
        return f"Cannot {failed_action}.\n\nTry instead:\n{suggestions}"
    
    def format_error_with_context(
        self, 
        error_message: str, 
        context: dict = None,
        suggestions: list = None
    ) -> str:
        """
        Format comprehensive error message with context and suggestions.
        
        Args:
            error_message: Main error message
            context: Dictionary with contextual information
            suggestions: List of suggested solutions
            
        Returns:
            Formatted error message
        """
        lines = [f"Error: {error_message}"]
        
        if context:
            lines.append("\nContext:")
            for key, value in context.items():
                lines.append(f"  {key}: {value}")
        
        if suggestions:
            lines.append("\nSuggestions:")
            for suggestion in suggestions:
                lines.append(f"  • {suggestion}")
        
        return "\n".join(lines)


class ProgressIndicator:
    """Shows progress for long-running operations"""
    
    def __init__(self, total: int, description: str = "Processing"):
        self.total = total
        self.current = 0
        self.description = description
    
    def update(self, increment: int = 1, item_name: str = None):
        """Update progress."""
        self.current += increment
        percentage = (self.current / self.total * 100) if self.total > 0 else 0
        
        if item_name:
            print(f"\r[{self.current}/{self.total}] {self.description}: {item_name} ({percentage:.0f}%)", end='', flush=True)
        else:
            print(f"\r[{self.current}/{self.total}] {self.description} ({percentage:.0f}%)", end='', flush=True)
    
    def complete(self, message: str = "Complete"):
        """Mark as complete."""
        print(f"\r{message} ({self.total} items)                    ")
    
    def error(self, message: str = "Failed"):
        """Mark as failed."""
        print(f"\r{message}                    ")


class UserFeedback:
    """Provides user feedback for operations"""
    
    @staticmethod
    def success(message: str):
        """Show success message."""
        print(f"[SUCCESS] {message}")
    
    @staticmethod
    def warning(message: str):
        """Show warning message."""
        print(f"[WARNING] {message}")
    
    @staticmethod
    def error(message: str):
        """Show error message."""
        print(f"[ERROR] {message}")
    
    @staticmethod
    def info(message: str):
        """Show info message."""
        print(f"[INFO] {message}")
    
    @staticmethod
    def ask_confirmation(question: str, default: bool = True) -> bool:
        """
        Ask user for confirmation.
        
        Args:
            question: Question to ask
            default: Default answer if user just presses enter
            
        Returns:
            True if user confirmed, False otherwise
        """
        suffix = "[Y/n]" if default else "[y/N]"
        response = input(f"{question} {suffix}: ").strip().lower()
        
        if not response:
            return default
        
        return response in ['y', 'yes']
