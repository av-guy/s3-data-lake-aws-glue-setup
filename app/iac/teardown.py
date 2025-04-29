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
from .glue import delete_glue_database, delete_all_tables_in_database

from ..config import S3_BUCKET_NAME, GLUE_ROLE_NAME, DB_NAME

LOGGER = logging.getLogger(__name__)


def run(
    remove_vpc_endpoint: bool = False,
    remove_iam_roles: bool = True,
    remove_glue_database: bool = True,
    remove_glue_tables: bool = True,
    remove_bucket: bool = True,
) -> None:
    """
    Teardown AWS resources.

    Parameters
    ----------
    remove_vpc_endpoint : bool, optional
        Remove the VPC endpoint if created. Default is False.
    remove_iam_roles : bool, optional
        Remove IAM roles and policies. Default is True.
    remove_glue_database : bool, optional
        Remove the Glue database. Default is True.
    remove_glue_tables : bool, optional
        Remove Glue tables inside the database. Default is True.
    remove_bucket : bool, optional
        Remove the S3 bucket. Default is True.
    """
    if remove_vpc_endpoint:
        pickle_path = Path(__file__).resolve().parent / "vpc_endpoint.pkl"

        if pickle_path.is_file():
            with open(pickle_path, "rb") as f:
                vpc_endpoint_resp = pickle.load(f)

            vpc_endpoint = vpc_endpoint_resp["VpcEndpoint"]["VpcEndpointId"]
            del_vpc_resp = delete_vpc_endpoint(vpc_endpoint)

            LOGGER.debug(
                "Delete VPC endpoint response: %s", pprint.pformat(del_vpc_resp)
            )
        else:
            LOGGER.warning(
                "VPC endpoint pickle file not found, skipping VPC endpoint removal."
            )

    if remove_iam_roles:
        del_il_resp = delete_inline_s3_policy(GLUE_ROLE_NAME)
        LOGGER.debug(
            "Delete inline S3 policy response: %s", pprint.pformat(del_il_resp)
        )

        del_gap_resp = delete_glue_general_access_policy(GLUE_ROLE_NAME)
        LOGGER.debug(
            "Delete Glue general policy response: %s", pprint.pformat(del_gap_resp)
        )

        del_role_resp = delete_glue_service_role(GLUE_ROLE_NAME)
        LOGGER.debug(
            "Delete Glue service role response: %s", pprint.pformat(del_role_resp)
        )

    if remove_glue_tables:
        delete_all_tables_in_database(DB_NAME)
        LOGGER.debug("Delete all tables in database success")

    if remove_glue_database:
        delete_glue_database(DB_NAME)
        LOGGER.debug("Delete Glue database success")

    if remove_bucket:
        delete_bucket(S3_BUCKET_NAME)
        LOGGER.debug("Delete bucket success")
