# Project Context

## Purpose
Z-Library CLI is a command-line tool for searching and downloading books from Z-Library. The application allows users to authenticate with Z-Library using email/password, search for books by title or keywords, and manage their downloads. It provides both individual book download capabilities and bulk downloading features with support for multiple file formats.

## Tech Stack
- Python 3.8+
- requests (HTTP requests)
- beautifulsoup4 (HTML parsing)
- argparse (command-line argument parsing)
- dataclasses (for structured data representation)
- typing (type hints)

## Project Conventions

### Code Style
- Follow PEP 8 Python style guide
- Use type hints for all function parameters and return values
- Use docstrings for all modules, classes, and functions
- Use descriptive variable and function names
- Class names should be CamelCase
- Function and variable names should be snake_case
- Use constants for configuration values
- Use logging instead of print statements for debugging and info messages

### Architecture Patterns
- Modular design with separate modules for different concerns (config, commands, HTTP client, parsers)
- Dependency injection for configuration and services
- Separation of concerns: CLI parsing, business logic, HTTP operations, and data models are in distinct modules
- Use of dataclasses for structured data (Book, Config)
- Command pattern for CLI routing (CommandRouter)
- Centralized configuration management through Config class
- HTTP client abstraction layer for network operations
- Parser classes for handling HTML content parsing
- Caching system for search results to avoid redundant requests

### Testing Strategy
- Unit tests for individual functions and classes
- Integration tests for CLI commands and HTTP operations
- Mocking external dependencies for isolated testing
- Test coverage for all major functionality paths

### Git Workflow
- Feature branches for new functionality
- Pull request reviews for code quality and security
- Conventional commit messages with type (feat, fix, docs, etc.)
- Branch names should be descriptive (feature/feature-name, bugfix/issue-description)

## Domain Context
- Z-Library is a shadow library providing access to academic and general books
- The application works by scraping Z-Library web pages and extracting book information
- Authentication is handled through cookies after login
- The application must respect server resources with appropriate delays between requests
- Book downloads happen through direct URLs obtained from search results
- HTML parsing is required to extract book metadata from Z-Library pages

## Important Constraints
- Must handle network errors gracefully with retries
- Needs to respect rate limiting and server resources
- Cookie-based authentication required for access
- File download validation and progress tracking
- Command-line interface must be intuitive and well-documented
- Configuration should support multiple sources (config file, environment variables, .env file)

## External Dependencies
- Z-Library website (z-library.sk) - primary data source
- Python standard library modules (json, os, sys, typing, dataclasses)
- Third-party Python packages: requests, beautifulsoup4
- Cookie storage for authentication persistence
- Local file system for storing downloads, configuration, and logs
