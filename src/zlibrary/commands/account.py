"""
Account command handler for Z-Library Search Application
"""
from zlibrary.config import Config
from zlibrary.auth import AuthManager
from zlibrary.account import AccountManager
from zlibrary.commands.base import BaseCommandHandler
from zlibrary.formatters import AccountInfoFormatter
from zlibrary.error_handler import ErrorHandler, UserFeedback
from zlibrary.logging_config import get_logger
from zlibrary.exceptions import NetworkException


class AccountCommandHandler(BaseCommandHandler):
    """Handles the account command with error handling"""
    
    def __init__(self, config: Config):
        super().__init__(config)
        self.logger = get_logger(__name__)
        self.auth_manager = AuthManager(config.get('cookies_file'))
        self.account_manager = AccountManager(config, self.auth_manager)
        self.error_handler = ErrorHandler()

    def handle(self, args) -> bool:
        """Handle the account command with error handling"""
        try:
            UserFeedback.info("Fetching account information from Z-Library...")
            
            account_info = self.account_manager.get_daily_limits()
            
            if not account_info:
                error_msg = self.error_handler.handle_authentication_error("fetching account information")
                UserFeedback.error(error_msg)
                return False
            
            # Format and display
            if args.simple:
                print(AccountInfoFormatter.format_simple(account_info))
            else:
                print(AccountInfoFormatter.format_detailed(account_info))
            
            # Provide helpful context
            remaining = account_info.get('downloads_remaining', 0)
            if remaining == 0:
                UserFeedback.warning("You have no downloads remaining today")
                UserFeedback.info("Limit will reset tomorrow or upgrade to premium for more downloads")
            elif remaining < 3:
                UserFeedback.warning(f"Only {remaining} download(s) remaining today")
            
            return True
            
        except NetworkException as e:
            error_msg = self.error_handler.handle_network_error(e, "fetching account information")
            UserFeedback.error(error_msg)
            return False
        except Exception as e:
            UserFeedback.error(f"Unexpected error: {e}")
            self.logger.exception("Account command error")
            return False
