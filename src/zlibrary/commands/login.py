"""
Login command handler for Z-Library Search Application
"""
import getpass
from zlibrary.config import Config
from zlibrary.auth import AuthManager
from zlibrary.commands.base import BaseCommandHandler
from zlibrary.error_handler import UserFeedback
from zlibrary.logging_config import get_logger
from zlibrary.exceptions import AuthenticationException
from zlibrary.constants import ConfigKeys


class LoginCommandHandler(BaseCommandHandler):
    """Handles the login command"""
    
    def __init__(self, config: Config):
        super().__init__(config)
        self.logger = get_logger(__name__)
        self.auth_manager = AuthManager(config.get(ConfigKeys.COOKIES_FILE))

    def handle(self, args) -> bool:
        """Handle the login command"""
        try:
            # Get credentials from args, config, or prompt
            email = self._get_email(args)
            password = self._get_password(args)
            
            if not email or not password:
                UserFeedback.error("Email and password are required for login")
                UserFeedback.info("Use --email and --password flags, set ZLIB_EMAIL/ZLIB_PASSWORD environment variables,")
                UserFeedback.info("or you will be prompted to enter them interactively.")
                return False
            
            # Perform login
            UserFeedback.info("Logging in to Z-Library...")
            sid, user_id = self.auth_manager.login_with_credentials(email, password)
            
            # Save cookies
            save_path = args.save_to if hasattr(args, 'save_to') else self.config.get(ConfigKeys.COOKIES_FILE)
            self.auth_manager.save_cookies_to_file(sid, user_id, save_path)
            
            UserFeedback.success(f"Login successful!")
            UserFeedback.info(f"Cookies saved to: {save_path}")
            UserFeedback.info(f"User ID: {user_id}")
            
            return True
            
        except AuthenticationException as e:
            UserFeedback.error(f"Login failed: {str(e)}")
            return False
        except Exception as e:
            UserFeedback.error(f"Unexpected error during login: {str(e)}")
            self.logger.exception("Login error")
            return False
    
    def _get_email(self, args) -> str:
        """Get email from args, config, or prompt."""
        # Check command line args
        if hasattr(args, 'email') and args.email:
            return args.email
        
        # Check config/environment
        email = self.config.get(ConfigKeys.ZLIB_EMAIL)
        if email:
            return email
        
        # Prompt user
        try:
            email = input("Z-Library Email: ").strip()
            return email
        except (KeyboardInterrupt, EOFError):
            return None
    
    def _get_password(self, args) -> str:
        """Get password from args, config, or prompt."""
        # Check command line args
        if hasattr(args, 'password') and args.password:
            return args.password
        
        # Check config/environment
        password = self.config.get(ConfigKeys.ZLIB_PASSWORD)
        if password:
            return password
        
        # Prompt user (hidden input)
        try:
            password = getpass.getpass("Z-Library Password: ").strip()
            return password
        except (KeyboardInterrupt, EOFError):
            return None
