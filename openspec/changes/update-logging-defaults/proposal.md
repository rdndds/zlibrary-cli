# Change: Update Default Logging Behavior

## Why
The Z-Library CLI currently has a default log level of INFO, which shows all informational messages during normal operation. Now that there's a dedicated `-v/--verbose` flag for enabling detailed output (DEBUG level), the default behavior should be more minimal to reduce console noise during normal usage. Users should be able to see only important messages (warnings and errors) by default, with more detailed information available through the verbose flag.

## What Changes
- Change default log level from INFO to WARNING to reduce console noise during normal operations
- Keep the `-v/--verbose` flag to enable full DEBUG level logging
- Update help text and documentation to reflect that verbose mode provides detailed logging
- Ensure important user-facing information is still displayed even with reduced logging (through print statements rather than log messages)
- Update configuration defaults in constants

## Impact
- **Affected specs**: logging capability
- **Affected code**:
  - `src/zlibrary/constants.py` - Update default LOG_LEVEL
  - `src/zlibrary/logging_config.py` - Ensure user-facing messages are still shown appropriately
  - `src/zlibrary/cli_help.py` - Update documentation about logging behavior
  - Documentation will be updated to clarify that verbose mode enables detailed logging
- **Breaking changes**: None - this changes the default experience but maintains the same verbose behavior
- **User experience impact**: Reduced console noise during normal operation, with verbose option for detailed debugging