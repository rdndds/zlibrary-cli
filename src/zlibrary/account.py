"""
Account information management for Z-Library Search Application
"""
from bs4 import BeautifulSoup
import re
from typing import Dict, Any, Tuple, Optional

from zlibrary.config import Config
from zlibrary.auth import AuthManager
from zlibrary.http_client import ZLibraryHTTPClient
from zlibrary.logging_config import get_logger
from zlibrary.exceptions import NetworkException, ParsingException
from zlibrary.constants import BASE_URL


class AccountManager:
    """Handles account-related functionality like limits and premium status"""

    def __init__(self, config: Config, auth_manager: AuthManager):
        self.config = config
        self.auth_manager = auth_manager
        self.http_client = ZLibraryHTTPClient(config, auth_manager)
        self.logger = get_logger(__name__)
    
    def _parse_daily_limit(self, soup: BeautifulSoup) -> str:
        """
        Parse daily download limit from HTML.
        
        Args:
            soup: BeautifulSoup object of the page
            
        Returns:
            Formatted daily limit string
        """
        daily_limit_elem = soup.find('div', class_=re.compile(r'caret-scroll__title'))
        if daily_limit_elem:
            daily_limit_text = daily_limit_elem.get_text().strip()
            # Extract the format "X/Y" where X is used and Y is total
            limit_match = re.search(r'(\d+)/(\d+)', daily_limit_text)
            if limit_match:
                used = limit_match.group(1)
                total = limit_match.group(2)
                return f"{used} used / {total} total"
            return daily_limit_text
        return "Unknown"
    
    def _parse_premium_status(self, soup: BeautifulSoup) -> str:
        """
        Parse premium account status from HTML.
        
        Args:
            soup: BeautifulSoup object of the page
            
        Returns:
            Premium status string
        """
        premium_elem = soup.find(string=re.compile(r'Premium account|Till', re.IGNORECASE))
        if premium_elem:
            parent = premium_elem.parent if premium_elem.parent else None
            if parent:
                premium_text = parent.get_text().strip()
                date_match = re.search(r'Till\s+([A-Za-z]+\s+\d{1,2},?\s+\d{4})', premium_text, re.IGNORECASE)
                if date_match:
                    return f"Premium account till {date_match.group(1)}"
                return "Premium account active"
        return "Not premium"
    
    def _parse_donation_amount(self, soup: BeautifulSoup) -> str:
        """
        Parse donation amount from HTML.
        
        Args:
            soup: BeautifulSoup object of the page
            
        Returns:
            Donation amount string
        """
        # Find all potential donation elements
        donation_elements = soup.find_all('div', class_=re.compile(r'caret-scroll__title'))
        for elem in donation_elements:
            elem_text = elem.get_text().strip()
            if '$' in elem_text:
                return elem_text
        
        # Look for donation information more specifically
        for elem in soup.find_all(['div', 'span'], class_=re.compile(r'caret-scroll__title|donation', re.IGNORECASE)):
            elem_text = elem.get_text().strip()
            if elem_text.startswith('$') and any(char.isdigit() for char in elem_text):
                return elem_text
        
        return "Unknown"
    
    def _extract_limit_numbers(self, daily_limit: str) -> Tuple[int, int]:
        """
        Extract numerical values from daily limit string.
        
        Args:
            daily_limit: Daily limit string (e.g., "5 used / 10 total")
            
        Returns:
            Tuple of (used, total) downloads
        """
        if daily_limit and daily_limit != "Unknown":
            limit_match = re.search(r'(\d+)\s*(?:used)?\s*/\s*(\d+)', daily_limit)
            if limit_match:
                used = int(limit_match.group(1))
                total = int(limit_match.group(2))
                return used, total
        return 0, 0
    
    def get_daily_limits(self) -> Optional[Dict[str, Any]]:
        """
        Fetch user's daily limits and account information from Z-Library

        Returns:
            dict: Dictionary containing daily limits and account info, or None on error
        """
        try:
            # Get the main page or profile page to extract user information
            response = self.http_client.get(BASE_URL)

            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')

                # Parse different account information sections
                daily_limit = self._parse_daily_limit(soup)
                premium_info = self._parse_premium_status(soup)
                donation_amount = self._parse_donation_amount(soup)

                # Extract numerical values from daily limit
                used, total = self._extract_limit_numbers(daily_limit)
                downloads_remaining = max(0, total - used)

                account_info = {
                    'daily_limit': daily_limit,
                    'premium_status': premium_info,
                    'donation_amount': donation_amount,
                    'downloads_used': used,
                    'downloads_remaining': downloads_remaining,
                    'daily_limit_total': total
                }

                return account_info
            else:
                self.logger.error(f"Error fetching account info: HTTP {response.status_code}")
                return None
                
        except NetworkException as e:
            self.logger.error(f"Network error getting daily limits: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Error getting daily limits: {e}")
            return None

    def check_download_limit(self, verbose: bool = True) -> Tuple[bool, Dict[str, Any]]:
        """
        Check the account's download limit before downloading

        Args:
            verbose (bool): Whether to print information

        Returns:
            tuple: (bool: can_download, dict: limit_info)
        """
        try:
            self.logger.info("Checking download limits...")
            account_info = self.get_daily_limits()

            if not account_info:
                if verbose:
                    self.logger.warning("Could not fetch account information, proceeding with download...")
                return True, {}

            # Parse the limits data
            daily_limit = account_info.get('daily_limit', 0)
            downloads_used = account_info.get('downloads_used', 0)
            downloads_remaining = account_info.get('downloads_remaining', 0)

            if verbose:
                print(f"Daily Limit: {daily_limit}")
                print(f"Downloads Used: {downloads_used}")
                print(f"Downloads Remaining: {downloads_remaining}")

            # Determine if we can download
            can_download = downloads_remaining > 0

            self.logger.info(f"Download limit check result: can_download={can_download}, {downloads_remaining} remaining")

            if verbose and not can_download:
                print("Daily download limit reached. Cannot download more books today.")
            elif verbose and can_download:
                print(f"You can still download {downloads_remaining} book(s) today.")

            return can_download, account_info
        except Exception as e:
            if verbose:
                self.logger.warning(f"Error checking download limit: {e}, proceeding with download...")
            return True, {}  # Allow download if check fails
            return True, {}