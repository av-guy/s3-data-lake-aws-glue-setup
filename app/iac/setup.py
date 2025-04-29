"""Setup for AWS resources"""

import logging
import pprint
import pickle

from pathlib import Path
from .s3 import create_and_wait_for_bucket, load_data_to_bucket

from .iam import (
    create_glue_service_role,
    attach_inline_s3_policy,
    attach_glue_general_access_policy,
)

from .vpc import create_vpc_endpoint

from ..config import (
    S3_BUCKET_NAME,
    ROUTE_TABLE_ID,
    VPC_ID,
    GLUE_ROLE_NAME,
    REGION,
)

LOGGER = logging.getLogger(__name__)
PP = pprint.PrettyPrinter(indent=2)


async def run(init_vpc_endpoint: bool = False) -> None:
    """Setup AWS resources for the STEDI project.

    Parameters
    ----------
    init_vpc_endpoint : bool, optional
        Create VPC endpoint after creation. Default is False.
    """
    bucket_response = await create_and_wait_for_bucket(S3_BUCKET_NAME)
    LOGGER.debug("Bucket response: %s", PP.pformat(bucket_response))

    glue_service_role_resp = create_glue_service_role(GLUE_ROLE_NAME)
    LOGGER.debug("Glue service role response: %s", PP.pformat(glue_service_role_resp))

    attach_s3_resp = attach_inline_s3_policy(GLUE_ROLE_NAME, S3_BUCKET_NAME)
    LOGGER.debug("Attach S3 policy response: %s", PP.pformat(attach_s3_resp))

    attach_blue_resp = attach_glue_general_access_policy(GLUE_ROLE_NAME)
    LOGGER.debug(
        "Attach Glue general policy response: %s", PP.pformat(attach_blue_resp)
    )

    if init_vpc_endpoint:
        service_name = f"com.amazonaws.{REGION}.s3"
        vpc_endpoint_resp = create_vpc_endpoint(VPC_ID, ROUTE_TABLE_ID, service_name)
        LOGGER.debug("VPC endpoint response: %s", PP.pformat(vpc_endpoint_resp))

        pickle_path = Path(__file__).resolve().parent / "vpc_endpoint.pkl"

        with open(pickle_path, "wb") as f:
            pickle.dump(vpc_endpoint_resp, f)

        LOGGER.info("VPC endpoint response pickled at %s", pickle_path)

    load_data_to_bucket(S3_BUCKET_NAME)
