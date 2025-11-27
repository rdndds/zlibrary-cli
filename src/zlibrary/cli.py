#!/usr/bin/env python3
"""
Z-Library CLI - Entry Point Module

This module provides the main entry point for the zlibrary CLI application.
"""
import sys
from zlibrary.config import Config
from zlibrary.cli_parser import create_parser
from zlibrary.cli_router import CommandRouter
from zlibrary.logging_config import setup_logging, get_logger


def main():
    """Main entry point for Z-Library CLI."""
    # Initialize configuration and logging
    config = Config()
    setup_logging(config)
    logger = get_logger(__name__)
    logger.info("Z-Library CLI starting")
    
    # Create argument parser
    parser = create_parser()
    
    # Show help if no arguments provided
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(0)
    
    # Parse arguments
    args = parser.parse_args()
    
    try:
        # Route command to appropriate handler
        router = CommandRouter(config)
        router.route(args)
        logger.info("Z-Library CLI completed successfully")
    except KeyboardInterrupt:
        logger.info("Operation cancelled by user")
        sys.exit(130)
    except Exception as e:
        logger.error("Command failed", exc_info=True)
        print(f"\nError: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
