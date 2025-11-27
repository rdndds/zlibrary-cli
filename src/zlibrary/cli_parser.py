"""
Argument Parser for Z-Library CLI

Handles command-line argument parsing.
"""
import argparse
from zlibrary.cli_help import MAIN_DESCRIPTION, SEARCH_HELP, DOWNLOAD_HELP, ACCOUNT_HELP


def create_parser() -> argparse.ArgumentParser:
    """
    Create and configure the main argument parser.
    
    Returns:
        Configured ArgumentParser
    """
    parser = argparse.ArgumentParser(
        description='Z-Library CLI - Search and Download Tool',
        epilog=MAIN_DESCRIPTION,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        add_help=True
    )
    
    # Add global verbose flag
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose output (DEBUG level logging)'
    )
    
    subparsers = parser.add_subparsers(
        dest='command',
        help='Available commands (use --help after command name for detailed help)'
    )
    
    # Add subcommands
    _add_search_parser(subparsers)
    _add_download_parser(subparsers)
    _add_account_parser(subparsers)
    _add_login_parser(subparsers)
    
    return parser


def _add_search_parser(subparsers):
    """Add search command parser."""
    search_parser = subparsers.add_parser(
        'search',
        help='Search for books by keywords or title in Z-Library',
        description='Search for books by keywords or title in Z-Library.',
        epilog=SEARCH_HELP,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    search_parser.add_argument(
        'query',
        nargs='?',
        help='Search query (keywords to search for)'
    )
    search_parser.add_argument(
        '--title',
        help='Search specifically by book title'
    )
    search_parser.add_argument(
        '--limit',
        type=int,
        default=10,
        help='Maximum number of results (default: 10)'
    )
    search_parser.add_argument(
        '--no-limit',
        action='store_true',
        help='Return all matching books'
    )
    search_parser.add_argument(
        '--download',
        action='store_true',
        help='Download all books from search results'
    )
    search_parser.add_argument(
        '--export',
        choices=['json', 'bibtex', 'both'],
        default=argparse.SUPPRESS,
        const='bibtex',
        nargs='?',
        help='Export search results (default: bibtex)'
    )
    search_parser.add_argument(
        '--details',
        action='store_true',
        help='Show detailed information for each result'
    )


def _add_download_parser(subparsers):
    """Add download command parser."""
    download_parser = subparsers.add_parser(
        'download',
        help='Download books from Z-Library using their URLs',
        description='Download books from Z-Library using their URLs.',
        epilog=DOWNLOAD_HELP,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    download_parser.add_argument(
        'url',
        nargs='+',
        help='Z-Library book URL(s) to download'
    )
    download_parser.add_argument(
        '--filename',
        help='Custom filename for the downloaded book'
    )
    download_parser.add_argument(
        '--bulk',
        action='store_true',
        help='Force bulk download mode'
    )
    download_parser.add_argument(
        '--urls-file',
        help='Path to file containing URLs (one per line)'
    )
    download_parser.add_argument(
        '--export',
        choices=['json', 'bibtex', 'both'],
        default=argparse.SUPPRESS,
        const='bibtex',
        nargs='?',
        help='Export book details (default: bibtex)'
    )
    download_parser.add_argument(
        '--details',
        action='store_true',
        help='Display detailed book information before download'
    )


def _add_account_parser(subparsers):
    """Add account command parser."""
    account_parser = subparsers.add_parser(
        'account',
        help='View your Z-Library account information',
        description='View your Z-Library account information including download limits.',
        epilog=ACCOUNT_HELP,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    account_parser.add_argument(
        '--simple',
        action='store_true',
        help='Display only basic account information'
    )


def _add_login_parser(subparsers):
    """Add login command parser."""
    login_parser = subparsers.add_parser(
        'login',
        help='Login to Z-Library with email and password',
        description='Login to Z-Library using email and password credentials. Saves cookies for future use.',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    login_parser.add_argument(
        '--email',
        help='Z-Library account email'
    )
    login_parser.add_argument(
        '--password',
        help='Z-Library account password'
    )
    login_parser.add_argument(
        '--save-to',
        default='data/cookies.txt',
        help='Path to save cookies file (default: data/cookies.txt)'
    )
