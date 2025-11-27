## ADDED Requirements

### Requirement: Parallel Download of Search Results
When using the `--download` flag with search results, the system SHALL support parallel downloads using the number of threads specified by the `--threads` option.

#### Scenario: Search with parallel download
- **WHEN** user runs `python main.py search "query" --download --threads 3`
- **AND** search returns multiple results
- **THEN** up to 3 books SHALL be downloaded concurrently
- **AND** the application SHALL continue downloading remaining books as each completes

### Requirement: Search Command Arguments with Threads Option
The search command SHALL accept a `--threads` option that controls parallel execution when downloading search results with the `--download` flag.

#### Scenario: Search command accepts threads argument
- **WHEN** user runs `python main.py search --help`
- **THEN** the help SHALL include `-t/--threads` option with appropriate description
- **AND** the description SHALL indicate this affects parallel downloads when using `--download`

#### Scenario: Threads argument affects search download behavior
- **WHEN** user specifies `--threads N` with `--download` flag
- **THEN** up to N search result downloads SHALL be processed concurrently
- **AND** the application SHALL manage resources appropriately for the specified thread count