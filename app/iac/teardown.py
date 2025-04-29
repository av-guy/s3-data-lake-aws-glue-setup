"""Teardown for AWS resources"""

import logging
import pickle
import pprint

from pathlib import Path

from .iam import (
    delete_glue_service_role,
    delete_inline_s3_policy,
    delete_glue_general_access_policy,
)

from .s3 import delete_bucket
from .vpc import delete_vpc_endpoint

from ..config import S3_BUCKET_NAME, GLUE_ROLE_NAME

LOGGER = logging.getLogger(__name__)


def run(remove_vpc_endpoint: bool = False) -> None:
    """Teardown the AWS resources

    Parameters:
    ----------
    remove_vpc_endpoint : bool, optional
         Remove VPC endpoint after deletion. Default is False.
    """
    if remove_vpc_endpoint:
        pickle_path = Path(__file__).resolve().parent / "vpc_endpoint.pkl"

        with open(pickle_path, "rb") as f:
            vpc_endpoint_resp = pickle.load(f)

        vpc_endpoint = vpc_endpoint_resp["VpcEndpoint"]["VpcEndpointId"]
        del_vpc_resp = delete_vpc_endpoint(vpc_endpoint)

        LOGGER.debug("Delete VPC endpoint response: %s", pprint.pformat(del_vpc_resp))

    del_il_resp = delete_inline_s3_policy(GLUE_ROLE_NAME)
    LOGGER.debug("Delete inline S3 policy response: %s", pprint.pformat(del_il_resp))

    del_gap_resp = delete_glue_general_access_policy(GLUE_ROLE_NAME)
    LOGGER.debug(
        "Delete Glue general policy response: %s", pprint.pformat(del_gap_resp)
    )

    del_role_resp = delete_glue_service_role(GLUE_ROLE_NAME)
    LOGGER.debug("Delete Glue service role response: %s", pprint.pformat(del_role_resp))

    delete_bucket(S3_BUCKET_NAME)
    LOGGER.debug("Delete bucket success")
