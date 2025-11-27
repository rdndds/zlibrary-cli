# Z-Library CLI Tool

Command-line tool for searching and downloading books from Z-Library.

## Installation

### With pipx (Recommended)

```bash
pipx install git+https://github.com/rdndds/zlibrary-cli.git
```

### Manual Setup

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

**Requirements:** Python 3.8+

## Authentication

Get cookies from Z-Library in Netscape format and save to `data/cookies.txt`:

```
# Netscape HTTP Cookie File
.z-library.sk	TRUE	/	FALSE	0	sid	<session_id>
.z-library.sk	TRUE	/	FALSE	0	user_id	<user_id>
```

## Usage

```bash
python main.py [command] [options]
```

### Search

```bash
# Basic search
python main.py search "machine learning"

# Search by title with limit
python main.py search --title "Python Programming" --limit 5

# Export results
python main.py search "data science" --export json
```

### Download

```bash
# Single download
python main.py download https://z-library.sk/book/12345/book-title.html

# Bulk download
python main.py download URL1 URL2 URL3

# From file
python main.py download --urls-file book_urls.txt
```

### Account

```bash
# View account info
python main.py account
```

## Configuration

Create `config.json` in project root (optional):

```json
{
  "cookies_file": "data/cookies.txt",
  "download_dir": "books",
  "max_pages": 5,
  "default_search_limit": 10,
  "log_level": "INFO"
}
```

Or use environment variables: `ZLIB_COOKIES_FILE`, `ZLIB_DOWNLOAD_DIR`, `ZLIB_LOG_LEVEL`, etc.

## License

MIT License - see LICENSE file.