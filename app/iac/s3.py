"""Setup methods for S3"""

import logging
import boto3

from mypy_boto3_s3 import S3Client, S3ServiceResource

from pathlib import Path
from .common import wait_for_resource
from ..config import S3_BUCKET_NAME

LOGGER = logging.getLogger(__name__)


def apply_bucket_access_block(bucket_name: str, client: S3Client) -> None:
    """
    Apply an access block policy to the specified S3 bucket.

    Parameters:
    ----------
    bucket_name : str
        Name of the S3 bucket to apply the policy to.
    client : S3Client
        Boto3 client for S3 operations.
    """
    client.put_public_access_block(
        Bucket=bucket_name,
        PublicAccessBlockConfiguration={
            "BlockPublicAcls": True,
            "IgnorePublicAcls": True,
            "BlockPublicPolicy": True,
            "RestrictPublicBuckets": True,
        },
    )

    LOGGER.info("Access block policy applied to bucket: %s", bucket_name)


@wait_for_resource(
    waiter_name="bucket_exists",
    waiter_kwargs={
        "Bucket": S3_BUCKET_NAME,
        "WaiterConfig": {"Delay": 2, "MaxAttempts": 10},
    },
)
async def create_and_wait_for_bucket(bucket_name: str):
    """
    Create a new S3 bucket and wait for it to become available.

    Parameters:
    ----------
    bucket_name : str
        Name of the S3 bucket to create.
    """
    return await create_bucket(bucket_name)


async def create_bucket(bucket_name: str) -> None:
    """
    Create a new S3 bucket with the given name.

    Parameters:
    ----------
    bucket_name : str
        Name of the S3 bucket to create.
    """
    client: S3Client = boto3.client("s3")

    response = client.create_bucket(
        Bucket=bucket_name,
        CreateBucketConfiguration={"LocationConstraint": "us-west-2"},
    )

    LOGGER.info("Bucket %s created: %s", bucket_name, response)
    return client


def delete_bucket(bucket_name: str) -> None:
    """
    Empty and delete the specified S3 bucket.

    Parameters
    ----------
    bucket_name : str
        Name of the S3 bucket to delete.
    """
    s3: S3ServiceResource = boto3.resource("s3")

    bucket = s3.Bucket(bucket_name)
    bucket.objects.all().delete()

    bucket.delete()
    LOGGER.info("Bucket '%s' emptied and deleted successfully.", bucket_name)


def load_data_to_bucket(bucket_name: str) -> None:
    """
    Upload all files from each 'landing' subfolder inside the local 'data' directory to S3.

    Parameters
    ----------
    bucket_name : str
        Name of the S3 bucket.
    """
    s3_client: S3Client = boto3.client("s3")

    script_dir = Path(__file__).resolve().parent
    data_dir = script_dir.parent / "data"

    if not data_dir.exists():
        raise FileNotFoundError(f"Data directory not found at: {data_dir}")

    for folder in data_dir.iterdir():
        if folder.is_dir():
            landing_dir = folder / "landing"

            if not landing_dir.exists():
                LOGGER.info("Skipping %s: No landing/ directory found.", folder.name)
                continue

            for file_path in landing_dir.glob("*"):
                if file_path.is_file():
                    s3_key = f"{folder.name}/landing/{file_path.name}"

                    s3_client.upload_file(
                        Filename=str(file_path), Bucket=bucket_name, Key=s3_key
                    )

                    LOGGER.info(
                        "Uploaded %s to s3://%s/%s", file_path, bucket_name, s3_key
                    )
