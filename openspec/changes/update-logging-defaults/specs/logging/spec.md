## MODIFIED Requirements

### Requirement: Application Logging Level
The application SHALL use WARNING level as the default logging level to minimize console noise during normal operation.

#### Scenario: Default execution shows minimal logs
- **WHEN** user runs any command without the verbose flag
- **THEN** the application SHALL only show warnings and errors in the console
- **AND** informational messages SHALL NOT appear by default

#### Scenario: Verbose execution shows detailed logs
- **WHEN** user runs any command with the -v/--verbose flag
- **THEN** the application SHALL show detailed DEBUG level logging
- **AND** all HTTP requests, responses, and processing details SHALL be logged

### Requirement: User Feedback Display
The application SHALL continue to provide important user feedback via print statements even with reduced logging levels.

#### Scenario: Critical information displayed regardless of log level
- **WHEN** important user information needs to be conveyed (download progress, success/failure, account status)
- **THEN** the information SHALL be displayed using print statements
- **AND** the information SHALL be visible even when using default logging level