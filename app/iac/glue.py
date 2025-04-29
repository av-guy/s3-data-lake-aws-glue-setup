"""AWS Glue setup methods"""

import logging
import boto3

from dataclasses import dataclass
from typing import List, Dict

from mypy_boto3_glue import GlueClient
from .common import wait_for_glue_database

LOGGER = logging.getLogger(__name__)


@dataclass
class GlueTableConfig:
    """Configuration for creating a Glue table.

    Attributes
    ----------
    database_name : str
        The name of the Glue database.
    table_name : str
        The name of the table.
    bucket_name : str
        The name of the S3 bucket.
    folder_prefix : str
        The prefix for the S3 folder containing the data.
    columns : List[Dict[str, str]]
        List of column definitions.
    classification : str, optional
        The classification for the table.
    serde_library : str, optional
        The name of the SerDe library to use.
    input_format : str, optional
        The input format for the table.
    output_format : str, optional
        The output format for the table.
    """

    database_name: str
    table_name: str
    bucket_name: str
    folder_prefix: str
    columns: List[Dict[str, str]]  # List of {"Name": ..., "Type": ...}
    classification: str = "json"
    serde_library: str = "org.openx.data.jsonserde.JsonSerDe"
    input_format: str = "org.apache.hadoop.mapred.TextInputFormat"
    output_format: str = "org.apache.hadoop.hive.ql.io.HiveIgnoreKeyTextOutputFormat"


async def create_and_wait_for_glue_database(
    database_name: str, description: str = ""
) -> dict:
    """
    Create a new Glue database and wait for it to become available.

    Parameters
    ----------
    database_name : str
        The name of the database to create.
    description : str, optional
        A description for the database.
    """
    client = create_glue_database(database_name, description)
    return await wait_for_glue_database(client, database_name)


def create_glue_database(database_name: str, description: str = "") -> dict:
    """
    Create a new Glue Database if it does not already exist.

    Parameters
    ----------
    database_name : str
        The name of the database to create.
    description : str, optional
        A description for the database.

    Returns
    -------
    dict
        AWS Glue create_database response.
    """
    client: GlueClient = boto3.client("glue")

    response = client.create_database(
        DatabaseInput={
            "Name": database_name,
            "Description": description,
            "Parameters": {"created_by": "automated-script"},
        }
    )

    LOGGER.info("Created Glue database: %s, %s", database_name, response)
    return client


def create_glue_table(config: GlueTableConfig) -> dict:
    """
    Create a Glue table using provided configuration.

    Parameters
    ----------
    config : GlueTableConfig
        Configuration for the Glue table.

    Returns
    -------
    dict
        AWS Glue create_table API response.
    """
    client: GlueClient = boto3.client("glue")

    s3_path = f"s3://{config.bucket_name}/{config.folder_prefix}"

    response = client.create_table(
        DatabaseName=config.database_name,
        TableInput={
            "Name": config.table_name,
            "StorageDescriptor": {
                "Columns": config.columns,
                "Location": s3_path,
                "InputFormat": config.input_format,
                "OutputFormat": config.output_format,
                "SerdeInfo": {
                    "SerializationLibrary": config.serde_library,
                    "Parameters": {"classification": config.classification},
                },
            },
            "TableType": "EXTERNAL_TABLE",
            "Parameters": {"classification": config.classification},
        },
    )

    LOGGER.info("Created Glue table: %s.%s", config.database_name, config.table_name)
    return response


def delete_glue_database(database_name: str) -> dict:
    """
    Delete a Glue Database by name.

    Parameters
    ----------
    database_name : str
        Name of the database to delete.

    Returns
    -------
    dict
        AWS Glue delete_database response.
    """
    client: GlueClient = boto3.client("glue")
    response = client.delete_database(Name=database_name)

    LOGGER.info("Deleted Glue database: %s", database_name)
    return response


def delete_all_tables_in_database(database_name: str) -> None:
    """
    Delete all tables in a Glue Database.

    Parameters
    ----------
    database_name : str
        Name of the Glue database.
    """
    client: GlueClient = boto3.client("glue")

    paginator = client.get_paginator("get_tables")
    pages = paginator.paginate(DatabaseName=database_name)

    for page in pages:
        for table in page["TableList"]:
            table_name = table["Name"]
            client.delete_table(DatabaseName=database_name, Name=table_name)
            LOGGER.info("Deleted table: %s", table_name)
