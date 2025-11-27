"""
Command Router for Z-Library CLI

Routes commands to their respective handlers.
"""
import sys
from typing import Any

from zlibrary.config import Config
from zlibrary.logging_config import get_logger


class CommandRouter:
    """Routes CLI commands to appropriate handlers"""
    
    def __init__(self, config: Config):
        self.config = config
        self.logger = get_logger(__name__)
    
    def route(self, args: Any) -> bool:
        """
        Route command to appropriate handler.
        
        Args:
            args: Parsed command-line arguments
            
        Returns:
            True if command succeeded, False otherwise
        """
        command = args.command
        
        if command == 'search':
            return self._handle_search(args)
        elif command == 'download':
            return self._handle_download(args)
        elif command == 'account':
            return self._handle_account(args)
        else:
            self.logger.error(f"Unknown command: {command}")
            return False
    
    def _handle_search(self, args: Any) -> bool:
        """Handle search command."""
        from zlibrary.commands.search import SearchCommandHandler
        handler = SearchCommandHandler(self.config)
        return handler.handle(args)
    
    def _handle_download(self, args: Any) -> bool:
        """Handle download command."""
        from zlibrary.commands.download import DownloadCommandHandler
        handler = DownloadCommandHandler(self.config)
        return handler.handle(args)
    
    def _handle_account(self, args: Any) -> bool:
        """Handle account command."""
        from zlibrary.commands.account import AccountCommandHandler
        handler = AccountCommandHandler(self.config)
        return handler.handle(args)
