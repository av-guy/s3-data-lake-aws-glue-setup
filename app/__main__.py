"""Application entry point"""

import asyncio
import logging
import sys
import argparse

from .iac import run_setup, run_teardown
from .logger import configure_logging

configure_logging(debug=True)
logger = logging.getLogger(__name__)


async def main():
    """Main entry point for the AWS resource management script."""

    parser = argparse.ArgumentParser(
        description="Manage AWS resources for the STEDI project."
    )

    parser.add_argument(
        "--setup",
        action="store_true",
        help="Run the setup process to create AWS resources.",
    )

    parser.add_argument(
        "--teardown",
        action="store_true",
        help="Run the teardown process to destroy AWS resources.",
    )

    args = parser.parse_args()

    if args.setup and args.teardown:
        logger.error("You cannot specify both --setup and --teardown at the same time.")
        sys.exit(1)

    if args.setup:
        logger.info("Running setup...")
        await run_setup()
    elif args.teardown:
        logger.info("Running teardown...")
        run_teardown()
    else:
        logger.warning("No action specified. Please use --setup or --teardown.")
        parser.print_help()


if __name__ == "__main__":
    asyncio.run(main())
