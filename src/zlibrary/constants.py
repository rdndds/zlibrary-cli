"""
Constants for Z-Library Search Application
"""

# Base URLs
BASE_URL = "https://z-library.sk"
SEARCH_URL_TEMPLATE = f"{BASE_URL}/s/{{query}}"

# HTTP Configuration
DEFAULT_USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
DEFAULT_HEADERS = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
}

# Request Configuration
DEFAULT_REQUEST_TIMEOUT = 30
DEFAULT_CONNECT_TIMEOUT = 10  # Fast fail for connection issues
DEFAULT_READ_TIMEOUT = 300  # 5 minutes for large downloads
DEFAULT_MAX_RETRIES = 3
DEFAULT_RETRY_DELAY = 1
RETRY_STATUS_CODES = [429, 500, 502, 503, 504]

# Download Configuration
DEFAULT_CHUNK_SIZE = 65536  # 64KB chunks for better performance
DEFAULT_MAX_WORKERS = 3  # Concurrent downloads in bulk mode
DEFAULT_PROGRESS_UPDATE_INTERVAL = 10  # Update progress every N chunks

# Configuration Keys
class ConfigKeys:
    """Configuration key constants to prevent typos"""
    COOKIES_FILE = 'cookies_file'
    ZLIB_EMAIL = 'zlib_email'
    ZLIB_PASSWORD = 'zlib_password'
    DOWNLOAD_DIR = 'download_dir'
    DOWNLOAD_INDEX_FILE = 'download_index_file'
    MAX_PAGES = 'max_pages'
    DEFAULT_SEARCH_LIMIT = 'default_search_limit'
    USER_AGENT = 'user_agent'
    REQUEST_TIMEOUT = 'request_timeout'
    CONNECT_TIMEOUT = 'connect_timeout'
    READ_TIMEOUT = 'read_timeout'
    MAX_RETRIES = 'max_retries'
    RETRY_DELAY = 'retry_delay'
    CHUNK_SIZE = 'chunk_size'
    MAX_WORKERS = 'max_workers'
    LOG_LEVEL = 'log_level'
    LOG_FILE = 'log_file'
    LOG_FORMAT = 'log_format'
    CONSOLE_LOG_FORMAT = 'console_log_format'
    FILE_LOG_FORMAT = 'file_log_format'
    LOG_MAX_BYTES = 'log_max_bytes'
    LOG_BACKUP_COUNT = 'log_backup_count'
    LOG_TO_CONSOLE = 'log_to_console'
    LOG_TO_FILE = 'log_to_file'

# Default Configuration Values
DEFAULT_CONFIG = {
    ConfigKeys.COOKIES_FILE: 'data/cookies.txt',
    ConfigKeys.ZLIB_EMAIL: None,
    ConfigKeys.ZLIB_PASSWORD: None,
    ConfigKeys.DOWNLOAD_DIR: 'books',
    ConfigKeys.DOWNLOAD_INDEX_FILE: 'data/download_index.json',
    ConfigKeys.MAX_PAGES: 5,
    ConfigKeys.DEFAULT_SEARCH_LIMIT: 10,
    ConfigKeys.USER_AGENT: DEFAULT_USER_AGENT,
    ConfigKeys.REQUEST_TIMEOUT: DEFAULT_REQUEST_TIMEOUT,
    ConfigKeys.CONNECT_TIMEOUT: DEFAULT_CONNECT_TIMEOUT,
    ConfigKeys.READ_TIMEOUT: DEFAULT_READ_TIMEOUT,
    ConfigKeys.MAX_RETRIES: DEFAULT_MAX_RETRIES,
    ConfigKeys.RETRY_DELAY: DEFAULT_RETRY_DELAY,
    ConfigKeys.CHUNK_SIZE: DEFAULT_CHUNK_SIZE,
    ConfigKeys.MAX_WORKERS: DEFAULT_MAX_WORKERS,
    ConfigKeys.LOG_LEVEL: 'WARNING',
    ConfigKeys.LOG_FILE: 'logs/zlibrary.log',
    ConfigKeys.LOG_FORMAT: '[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s',
    ConfigKeys.CONSOLE_LOG_FORMAT: '[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s',
    ConfigKeys.FILE_LOG_FORMAT: '[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s',
    ConfigKeys.LOG_MAX_BYTES: 10485760,  # 10MB
    ConfigKeys.LOG_BACKUP_COUNT: 5,
    ConfigKeys.LOG_TO_CONSOLE: True,
    ConfigKeys.LOG_TO_FILE: True
}

# Environment Variable Mapping
ENV_VAR_PREFIX = 'ZLIB_'
ENV_VAR_MAPPING = {
    f'{ENV_VAR_PREFIX}COOKIES_FILE': ConfigKeys.COOKIES_FILE,
    f'{ENV_VAR_PREFIX}EMAIL': ConfigKeys.ZLIB_EMAIL,
    f'{ENV_VAR_PREFIX}PASSWORD': ConfigKeys.ZLIB_PASSWORD,
    f'{ENV_VAR_PREFIX}DOWNLOAD_DIR': ConfigKeys.DOWNLOAD_DIR,
    f'{ENV_VAR_PREFIX}DOWNLOAD_INDEX_FILE': ConfigKeys.DOWNLOAD_INDEX_FILE,
    f'{ENV_VAR_PREFIX}MAX_PAGES': ConfigKeys.MAX_PAGES,
    f'{ENV_VAR_PREFIX}DEFAULT_SEARCH_LIMIT': ConfigKeys.DEFAULT_SEARCH_LIMIT,
    f'{ENV_VAR_PREFIX}USER_AGENT': ConfigKeys.USER_AGENT,
    f'{ENV_VAR_PREFIX}REQUEST_TIMEOUT': ConfigKeys.REQUEST_TIMEOUT,
    f'{ENV_VAR_PREFIX}CONNECT_TIMEOUT': ConfigKeys.CONNECT_TIMEOUT,
    f'{ENV_VAR_PREFIX}READ_TIMEOUT': ConfigKeys.READ_TIMEOUT,
    f'{ENV_VAR_PREFIX}MAX_RETRIES': ConfigKeys.MAX_RETRIES,
    f'{ENV_VAR_PREFIX}RETRY_DELAY': ConfigKeys.RETRY_DELAY,
    f'{ENV_VAR_PREFIX}CHUNK_SIZE': ConfigKeys.CHUNK_SIZE,
    f'{ENV_VAR_PREFIX}MAX_WORKERS': ConfigKeys.MAX_WORKERS,
    f'{ENV_VAR_PREFIX}LOG_LEVEL': ConfigKeys.LOG_LEVEL,
    f'{ENV_VAR_PREFIX}LOG_FILE': ConfigKeys.LOG_FILE,
    f'{ENV_VAR_PREFIX}LOG_FORMAT': ConfigKeys.LOG_FORMAT,
    f'{ENV_VAR_PREFIX}CONSOLE_LOG_FORMAT': ConfigKeys.CONSOLE_LOG_FORMAT,
    f'{ENV_VAR_PREFIX}FILE_LOG_FORMAT': ConfigKeys.FILE_LOG_FORMAT,
    f'{ENV_VAR_PREFIX}LOG_MAX_BYTES': ConfigKeys.LOG_MAX_BYTES,
    f'{ENV_VAR_PREFIX}LOG_BACKUP_COUNT': ConfigKeys.LOG_BACKUP_COUNT,
    f'{ENV_VAR_PREFIX}LOG_TO_CONSOLE': ConfigKeys.LOG_TO_CONSOLE,
    f'{ENV_VAR_PREFIX}LOG_TO_FILE': ConfigKeys.LOG_TO_FILE,
}

# File System
MAX_FILENAME_LENGTH = 255
EXPORT_DIR = 'export'

# Search Configuration
MAX_SEARCH_LIMIT = 10000
DEFAULT_PAGE_SIZE = 10
