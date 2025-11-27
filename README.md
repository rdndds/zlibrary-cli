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

You can authenticate with Z-Library in two ways:

### Method 1: Login with Email & Password (Recommended)

```bash
# Login interactively (will prompt for credentials)
python main.py login

# Login with command-line arguments
python main.py login --email your_email@example.com --password your_password

# Use environment variables (recommended for automation)
export ZLIB_EMAIL=your_email@example.com
export ZLIB_PASSWORD=your_password
python main.py login

# Or use .env file
cp .env.example .env
# Edit .env with your credentials
python main.py login
```

This will authenticate and save cookies to `data/cookies.txt` automatically.

### Method 2: Manual Cookie File

Get cookies from Z-Library in Netscape format and save to `data/cookies.txt`:

```
# Netscape HTTP Cookie File
.z-library.sk	TRUE	/	FALSE	0	remix_userkey	<session_key>
.z-library.sk	TRUE	/	FALSE	0	remix_userid	<user_id>
```

Note: The app also supports older cookie names (`sid` and `user_id`) for backward compatibility.

## Usage

```bash
python main.py [command] [options]

# Use -v or --verbose for detailed debug output
python main.py -v [command] [options]
```

### Login

```bash
# Interactive login (prompts for email/password)
python main.py login

# Login with credentials
python main.py login --email your@email.com --password yourpass

# Save to custom location
python main.py login --save-to /path/to/cookies.txt

# Verbose mode (shows detailed debug information)
python main.py -v login
```

### Search

```bash
# Basic search
python main.py search "machine learning"

# Search by title with limit
python main.py search --title "Python Programming" --limit 5

# Export results
python main.py search "data science" --export json

# Verbose mode for debugging
python main.py -v search "python"
```

### Download

```bash
# Single download
python main.py download https://z-library.sk/book/12345/book-title.html

# Bulk download
python main.py download URL1 URL2 URL3

# From file
python main.py download --urls-file book_urls.txt

# Verbose mode shows detailed progress
python main.py -v download https://z-library.sk/book/12345/book-title.html
```

### Account

```bash
# View account info
python main.py account
```

## Configuration

### Option 1: Environment Variables (.env file)

Copy `.env.example` to `.env` and customize:

```bash
cp .env.example .env
```

Example `.env` file:

```bash
# Authentication
ZLIB_EMAIL=your_email@example.com
ZLIB_PASSWORD=your_password

# Paths
ZLIB_COOKIES_FILE=data/cookies.txt
ZLIB_DOWNLOAD_DIR=books

# Settings
ZLIB_MAX_PAGES=5
ZLIB_DEFAULT_SEARCH_LIMIT=10
ZLIB_LOG_LEVEL=INFO
```

### Option 2: config.json

Create `config.json` in project root:

```json
{
  "zlib_email": "your_email@example.com",
  "zlib_password": "your_password",
  "cookies_file": "data/cookies.txt",
  "download_dir": "books",
  "max_pages": 5,
  "default_search_limit": 10,
  "log_level": "INFO"
}
```

### Option 3: Environment Variables (direct)

```bash
export ZLIB_EMAIL=your_email@example.com
export ZLIB_PASSWORD=your_password
export ZLIB_COOKIES_FILE=data/cookies.txt
export ZLIB_DOWNLOAD_DIR=books
export ZLIB_LOG_LEVEL=INFO
```

See `.env.example` for all available configuration options.

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