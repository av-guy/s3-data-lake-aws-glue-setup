"""Setup for AWS resources"""

import logging
import pprint
import pickle

from pathlib import Path
from typing import List
from json import load

from .s3 import create_and_wait_for_bucket, load_data_to_bucket

from .iam import (
    create_glue_service_role,
    attach_inline_s3_policy,
    attach_glue_general_access_policy,
)

from .vpc import create_vpc_endpoint
from .glue import GlueTableConfig, create_glue_table, create_and_wait_for_glue_database

from ..config import (
    S3_BUCKET_NAME,
    ROUTE_TABLE_ID,
    VPC_ID,
    GLUE_ROLE_NAME,
    REGION,
    DB_NAME,
)

LOGGER = logging.getLogger(__name__)
PP = pprint.PrettyPrinter(indent=2)


def load_glue_table_configs(database_name: str) -> List[GlueTableConfig]:
    """
    Dynamically load GlueTableConfig objects from schema files organized under 'schemas' directory.

    Assumes:
    - Directory structure: schemas/<entity>/<subfolder>/schema.json
    - Each subfolder contains a schema.json and no further nesting.

    Parameters
    ----------
    database_name : str
        Name of the Glue database to assign tables to.

    Returns
    -------
    List[GlueTableConfig]
        A list of GlueTableConfig objects ready to create tables.
    """

    configs = []
    base_schema_dir = Path(__file__).resolve().parents[1] / "schemas"

    for entity_dir in base_schema_dir.iterdir():
        if not entity_dir.is_dir():
            continue

        for subfolder in entity_dir.iterdir():
            if not subfolder.is_dir():
                continue

            schema_file = subfolder / "schema.json"

            if not schema_file.is_file():
                LOGGER.warning("No schema.json found in %s", subfolder)
                continue

            with open(schema_file, "r", encoding="utf-8") as f:
                columns = load(f)

            entity = entity_dir.name
            sub = subfolder.name
            table_name = f"{entity}_{sub}"
            folder_prefix = f"{entity}/{sub}/"

            config = GlueTableConfig(
                database_name=database_name,
                table_name=table_name,
                bucket_name=S3_BUCKET_NAME,
                folder_prefix=folder_prefix,
                columns=columns,
            )

            configs.append(config)

    return configs


async def run(
    init_bucket: bool = True,
    init_iam_roles: bool = True,
    init_vpc_endpoint: bool = False,
    load_sample_data: bool = True,
    init_glue_database: bool = True,
    init_glue_tables: bool = True,
) -> None:
    """
    Setup AWS resources for the STEDI project.

    Parameters
    ----------
    init_bucket : bool, optional
        Create S3 bucket. Default is True.
    init_iam_roles : bool, optional
        Create IAM roles and attach policies. Default is True.
    init_vpc_endpoint : bool, optional
        Create VPC endpoint. Default is False.
    load_sample_data : bool, optional
        Load sample data into S3. Default is True.
    init_glue_database : bool, optional
        Create Glue database. Default is True.
    init_glue_tables : bool, optional
        Create Glue tables. Default is True.
    """
    if init_bucket:
        bucket_response = await create_and_wait_for_bucket(S3_BUCKET_NAME)
        LOGGER.debug("Bucket response: %s", PP.pformat(bucket_response))

    if init_iam_roles:
        glue_service_role_resp = create_glue_service_role(GLUE_ROLE_NAME)
        LOGGER.debug(
            "Glue service role response: %s", PP.pformat(glue_service_role_resp)
        )

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

    if load_sample_data:
        load_data_to_bucket(S3_BUCKET_NAME)

    if init_glue_database:
        glue_db_resp = await create_and_wait_for_glue_database(DB_NAME)
        LOGGER.debug("Glue database response: %s", PP.pformat(glue_db_resp))

    if init_glue_tables:
        glue_table_configs = load_glue_table_configs(DB_NAME)

        for config in glue_table_configs:
            create_response = create_glue_table(config)
            LOGGER.debug("Create Glue table response: %s", PP.pformat(create_response))
