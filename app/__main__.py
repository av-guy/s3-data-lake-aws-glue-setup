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

    parser.add_argument(
        "--skip-bucket",
        action="store_true",
        help="Skip creating S3 bucket during setup.",
    )

    parser.add_argument(
        "--skip-iam",
        action="store_true",
        help="Skip creating IAM roles/policies during setup.",
    )
    parser.add_argument(
        "--init-vpc-endpoint",
        action="store_true",
        help="Create VPC endpoint during setup.",
    )

    parser.add_argument(
        "--skip-load-data",
        action="store_true",
        help="Skip loading sample data into S3 during setup.",
    )

    parser.add_argument(
        "--skip-glue-database",
        action="store_true",
        help="Skip creating Glue database during setup.",
    )

    parser.add_argument(
        "--skip-glue-tables",
        action="store_true",
        help="Skip creating Glue tables during setup.",
    )

    parser.add_argument(
        "--remove-vpc-endpoint",
        action="store_true",
        help="Remove the VPC endpoint during teardown.",
    )

    args = parser.parse_args()

    if args.setup and args.teardown:
        logger.error("You cannot specify both --setup and --teardown at the same time.")
        sys.exit(1)

    if args.setup:
        logger.info("Running setup...")

        await run_setup(
            init_bucket=not args.skip_bucket,
            init_iam_roles=not args.skip_iam,
            init_vpc_endpoint=args.init_vpc_endpoint,
            load_sample_data=not args.skip_load_data,
            init_glue_database=not args.skip_glue_database,
            init_glue_tables=not args.skip_glue_tables,
        )

    elif args.teardown:
        logger.info("Running teardown...")

        run_teardown(
            remove_vpc_endpoint=args.remove_vpc_endpoint,
            remove_iam_roles=not args.skip_iam,
            remove_glue_database=not args.skip_glue_database,
            remove_glue_tables=not args.skip_glue_tables,
            remove_bucket=not args.skip_bucket,
        )

    else:
        logger.warning("No action specified. Please use --setup or --teardown.")
        parser.print_help()


if __name__ == "__main__":
    asyncio.run(main())
