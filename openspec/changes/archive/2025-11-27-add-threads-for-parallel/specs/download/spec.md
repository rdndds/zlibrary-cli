## ADDED Requirements

### Requirement: Parallel Download with Thread Control
The download command SHALL support parallel downloads when multiple URLs are provided, using the number of threads specified by the `--threads` option.

#### Scenario: Bulk download with multiple threads
- **WHEN** user runs `python main.py download URL1 URL2 URL3 --threads 3`
- **AND** all URLs are valid
- **THEN** the application SHALL initiate up to 3 concurrent downloads
- **AND** the application SHALL manage resources to prevent exceeding the thread limit

#### Scenario: Bulk download with threads from file
- **WHEN** user runs `python main.py download --urls-file urls.txt --threads 2`
- **AND** the file contains valid URLs
- **THEN** the application SHALL download up to 2 books concurrently
- **AND** the application SHALL continue processing remaining URLs as downloads complete

### Requirement: Download Rate Limiting with Parallel Downloads
The application SHALL respect download limits even when performing parallel downloads.

#### Scenario: Parallel download respecting daily limits
- **WHEN** user attempts parallel download with remaining daily downloads less than thread count
- **THEN** the application SHALL limit the number of concurrent downloads to remaining daily allowance
- **AND** any excess download requests SHALL be queued or rejected appropriately

### Requirement: Download Command Arguments with Threads Option
The download command SHALL accept a `--threads` option that controls parallel execution when downloading multiple books.

#### Scenario: Download command accepts threads argument
- **WHEN** user runs `python main.py download --help`
- **THEN** the help SHALL include `-t/--threads` option with appropriate description
- **AND** the default value SHALL be 1 for backward compatibility

#### Scenario: Threads argument affects download behavior
- **WHEN** user specifies `--threads N` for bulk download
- **THEN** up to N downloads SHALL be processed concurrently
- **AND** the application SHALL manage resources appropriately to prevent system overload