"""Setup methods for VPC"""

import logging
import boto3

from mypy_boto3_ec2 import EC2Client

LOGGER = logging.getLogger(__name__)


def create_vpc_endpoint(vpc_id: str, route_table_id: str, service_name: str) -> dict:
    """
    Create a VPC Endpoint for a service like S3.

    Parameters
    ----------
    vpc_id : str
        Your VPC ID (e.g., 'vpc-0abc123def456ghij')
    route_table_id : str
        Your Route Table ID (e.g., 'rtb-0123456789abcdef0')
    service_name : str
        The AWS Service name (e.g., 'com.amazonaws.us-west-2.s3')

    Returns
    -------
    dict
        The API response from AWS.
    """
    client: EC2Client = boto3.client("ec2")

    response = client.create_vpc_endpoint(
        VpcEndpointType="Gateway",
        VpcId=vpc_id,
        ServiceName=service_name,
        RouteTableIds=[route_table_id],
    )

    return response


def delete_vpc_endpoint(vpc_endpoint_id: str) -> dict:
    """
    Delete the specified VPC Endpoint.

    Parameters:
    ----------
    vpc_endpoint_id : str
        The ID of the VPC Endpoint to delete.

    Returns
    -------
    dict
        The API response from AWS.
    """
    client: EC2Client = boto3.client("ec2")
    response = client.delete_vpc_endpoints(VpcEndpointIds=[vpc_endpoint_id])

    return response
