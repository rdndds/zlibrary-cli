"""
Help text and usage examples for Z-Library CLI
"""

MAIN_DESCRIPTION = """Z-Library CLI - Search and Download Tool

DESCRIPTION:
  Z-Library CLI is a command-line tool for searching and downloading books from Z-Library.
  It uses your stored cookies for authentication to access Z-Library content.

INSTALLATION:
  Install with pipx (recommended):
    pipx install git+https://github.com/yourusername/zlibrary-cli.git
  
  Or with pip:
    pip install git+https://github.com/yourusername/zlibrary-cli.git

COMMANDS:
  search    Search for books by keywords or title
  download  Download books by providing their Z-Library URLs
  account   View your account information and download limits

GLOBAL OPTIONS:
  -h, --help  Show this help message and exit

USAGE EXAMPLES:
  Search for books:
    zlib search "machine learning"
    zlib search --title "Python Programming" --limit 5

  Download books:
    zlib download https://z-library.sk/book/12345/example-book.html
    zlib download URL1 URL2 URL3
    zlib download @book_urls.txt --details
    zlib download URL --export --details

  View account info:
    zlib account
    zlib account --simple

For detailed help on any command, use: zlib <command> --help
"""

SEARCH_HELP = """
DESCRIPTION:
  Search for books by keywords or title in Z-Library.
  Use various flags to refine your search and control output.

OPTIONS:
  query                         Search query (keywords to search for)
  --title TITLE                 Search by book title
  --limit LIMIT                 Number of results to return (default: 10)
  --no-limit                    Return all matching books
  --download                    Download found books after search
  --export [json|bibtex|both]   Export search results (default: bibtex)
  --details                     Show detailed information for each result
  -t, --threads N               Number of parallel download threads when using --download (default: 1)

EXAMPLES:
  zlib search "machine learning"
  zlib search --title "Python Programming" --limit 5
  zlib search "deep learning" --details --export
  zlib search "statistics" --download
  zlib search "python" --no-limit --download --threads 3
"""

DOWNLOAD_HELP = """
DESCRIPTION:
  Download books from Z-Library using their URLs.
  Supports single downloads, bulk downloads, and reading URLs from files.
  Use -t/--threads to specify the number of parallel downloads (default: 1).

OPTIONS:
  url [url ...]                 Book URL(s) to download
  --filename FILENAME           Custom filename for single download
  --bulk                        Force bulk download mode (auto-detected)
  --urls-file URLS_FILE         File containing URLs (one per line)
  --export [json|bibtex|both]   Export book details (default: bibtex)
  --details                     Show detailed book information before download
  -t, --threads N               Number of parallel download threads (default: 1)

EXAMPLES:
  Single download:
    zlib download https://z-library.sk/book/12345/example-book.html
    zlib download URL --filename "MyBook.pdf"
    zlib download URL --details --export

  Multiple downloads:
    zlib download URL1 URL2 URL3
    zlib download URL1 URL2 URL3 --threads 3
    zlib download URL1 URL2 URL3 --details --export

  Download from file:
    zlib download @book_urls.txt
    zlib download --urls-file book_urls.txt --threads 3 --details
"""

ACCOUNT_HELP = """
DESCRIPTION:
  View your Z-Library account information including download limits and quotas.

OPTIONS:
  --simple    Show only download limits and daily quota

EXAMPLES:
  zlib account
  zlib account --simple
"""
