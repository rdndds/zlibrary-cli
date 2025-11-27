# Z-Library CLI Tool

Command-line tool for searching and downloading books from Z-Library.

## Installation

### Method 1: Direct from GitHub (Recommended)

```bash
# Clone the repository
git clone https://github.com/rdndds/zlibrary-cli.git
cd zlibrary-cli

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the tool
python main.py --help
```

### Method 2: With pipx

If you prefer isolated installation with pipx:

```bash
# Install system dependencies (Ubuntu/Debian)
sudo apt install python3-venv python3-pip

# Install pipx
python3 -m pip install --user pipx
python3 -m pipx ensurepath

# Install zlibrary-cli
pipx install git+https://github.com/rdndds/zlibrary-cli.git
```

**Requirements:** Python 3.8+

**Note:** For pipx to work, you need `python3-venv` installed on your system.

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

## Troubleshooting

### pipx Installation Fails

If you get an error like `Command 'python3 -m venv' failed`:

```bash
# Ubuntu/Debian
sudo apt install python3-venv python3-pip

# Fedora/RHEL
sudo dnf install python3-pip

# Then try pipx installation again
```

### Alternative: Use pip directly

```bash
pip install git+https://github.com/rdndds/zlibrary-cli.git
```

### Manual Installation

If all else fails, clone and run directly:

```bash
git clone https://github.com/rdndds/zlibrary-cli.git
cd zlibrary-cli
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py --help
```

## License

MIT License - see LICENSE file.