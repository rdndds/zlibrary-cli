"""
Authentication and cookie handling for Z-Library Search Application
"""
import os
from pathlib import Path
from requests.cookies import RequestsCookieJar
from typing import Optional

from zlibrary.logging_config import get_logger
from zlibrary.exceptions import AuthenticationException


class AuthManager:
    """Handles cookie loading and authentication"""

    def __init__(self, cookies_file: str = 'cookies.txt'):
        self.cookies_file = cookies_file
        self.logger = get_logger(__name__)

    def load_cookies_from_file(self, cookie_file_path: Optional[str] = None) -> RequestsCookieJar:
        """
        Load cookies from Netscape cookie file format
        Checks current directory first, then falls back to configured path

        Args:
            cookie_file_path: Path to cookies file (defaults to instance value)

        Returns:
            RequestsCookieJar: Loaded cookies
        """
        if cookie_file_path is None:
            cookie_file_path = self.cookies_file

        # Check current working directory first
        cwd_cookies = Path.cwd() / 'cookies.txt'
        if cwd_cookies.exists():
            cookie_file_path = str(cwd_cookies)
            self.logger.debug(f"Found cookies.txt in current directory: {cookie_file_path}")
        
        self.logger.debug(f"Loading cookies from file: {cookie_file_path}")

        try:
            cookie_jar = RequestsCookieJar()

            with open(cookie_file_path, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    if line.startswith('#') or line.strip() == '':
                        continue

                    fields = line.strip().split('\t')
                    if len(fields) >= 7:
                        domain, flag, path, secure, expiration, name, value = fields
                        cookie_jar.set(name, value, domain=domain.lstrip('.'), path=path)
                    else:
                        self.logger.warning(f"Invalid cookie format in {cookie_file_path} at line {line_num}")

            self.logger.info(f"Successfully loaded {len(cookie_jar)} cookies from {cookie_file_path}")
            return cookie_jar
        except FileNotFoundError:
            self.logger.error(f"Cookies file not found: {cookie_file_path}")
            raise AuthenticationException(f"Authentication failed: cookies file not found at {cookie_file_path}")
        except Exception as e:
            self.logger.error(f"Error loading cookies from {cookie_file_path}: {str(e)}")
            raise AuthenticationException(f"Authentication failed: error loading cookies - {str(e)}")