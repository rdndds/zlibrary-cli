# Change: Implement Parallel Download Threads

## Why
The Z-Library CLI currently defines a `-t/--threads` command-line option for both search and download commands, but this functionality is not actually implemented in the code. Users expect to be able to download multiple books in parallel to improve download speeds and efficiency, but the current implementation downloads books sequentially. This change will implement the threads functionality using the existing configuration and concurrent processing infrastructure.

## What Changes
- Implement parallel download functionality using the existing `ConcurrentProcessor` class
- Modify the download command to accept and use the `--threads` parameter for bulk downloads
- Modify the search command to use threads when downloading search results with the `--download` flag
- Update the download configuration to respect the threads parameter from command line
- Update documentation to reflect the new functionality

## Impact
- **Affected specs**: download capability, search capability
- **Affected code**: 
  - `src/zlibrary/commands/download.py` - Update bulk download implementation
  - `src/zlibrary/commands/search.py` - Update download after search functionality
  - `src/zlibrary/download.py` - Add parallel download functionality
  - `src/zlibrary/concurrent.py` - Use for parallel processing
- **Breaking changes**: None - this is a new feature that extends existing functionality
- **Performance impact**: Expected performance improvement when downloading multiple books in parallel