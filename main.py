#!/usr/bin/env python3
"""
Z-Library CLI - Main Module

Command-line tool for searching and downloading books from Z-Library.
"""
import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

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
        return
    
    # Parse arguments
    args = parser.parse_args()
    
    # Show header
    print("=" * 50)
    logger.info("Z-Library CLI using your cookies")
    
    # Route command to handler
    router = CommandRouter(config)
    success = router.route(args)
    
    if not success:
        logger.error("Command failed")
        sys.exit(1)
    
    logger.info("Command completed successfully")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\nError: {e}")
        sys.exit(1)
