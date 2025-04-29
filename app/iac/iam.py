"""Setup methods for IAM"""

import logging
import boto3

from json import dumps
from mypy_boto3_iam import IAMClient
from ..config import GLUE_ROLE_POLICY_NAME, S3_ROLE_POLICY_NAME

LOGGER = logging.getLogger(__name__)


def attach_glue_general_access_policy(role_name: str) -> dict:
    """
    Attach a general access policy needed by AWS Glue to an IAM role.

    Parameters
    ----------
    role_name : str
        Name of the IAM role.

    Returns
    -------
    dict
        AWS response from put_role_policy.
    """
    iam_client: IAMClient = boto3.client("iam")

    glue_policy_document = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": [
                    "glue:*",
                    "s3:GetBucketLocation",
                    "s3:ListBucket",
                    "s3:ListAllMyBuckets",
                    "s3:GetBucketAcl",
                    "ec2:DescribeVpcEndpoints",
                    "ec2:DescribeRouteTables",
                    "ec2:CreateNetworkInterface",
                    "ec2:DeleteNetworkInterface",
                    "ec2:DescribeNetworkInterfaces",
                    "ec2:DescribeSecurityGroups",
                    "ec2:DescribeSubnets",
                    "ec2:DescribeVpcAttribute",
                    "iam:ListRolePolicies",
                    "iam:GetRole",
                    "iam:GetRolePolicy",
                    "cloudwatch:PutMetricData",
                ],
                "Resource": ["*"],
            },
            {
                "Effect": "Allow",
                "Action": ["s3:CreateBucket", "s3:PutBucketPublicAccessBlock"],
                "Resource": ["arn:aws:s3:::aws-glue-*"],
            },
            {
                "Effect": "Allow",
                "Action": ["s3:GetObject", "s3:PutObject", "s3:DeleteObject"],
                "Resource": [
                    "arn:aws:s3:::aws-glue-*/*",
                    "arn:aws:s3:::*/*aws-glue-*/*",
                ],
            },
            {
                "Effect": "Allow",
                "Action": ["s3:GetObject"],
                "Resource": ["arn:aws:s3:::crawler-public*", "arn:aws:s3:::aws-glue-*"],
            },
            {
                "Effect": "Allow",
                "Action": [
                    "logs:CreateLogGroup",
                    "logs:CreateLogStream",
                    "logs:PutLogEvents",
                    "logs:AssociateKmsKey",
                ],
                "Resource": ["arn:aws:logs:*:*:/aws-glue/*"],
            },
            {
                "Effect": "Allow",
                "Action": ["ec2:CreateTags", "ec2:DeleteTags"],
                "Condition": {
                    "ForAllValues:StringEquals": {
                        "aws:TagKeys": ["aws-glue-service-resource"]
                    }
                },
                "Resource": [
                    "arn:aws:ec2:*:*:network-interface/*",
                    "arn:aws:ec2:*:*:security-group/*",
                    "arn:aws:ec2:*:*:instance/*",
                ],
            },
        ],
    }

    response = iam_client.put_role_policy(
        RoleName=role_name,
        PolicyName=GLUE_ROLE_POLICY_NAME,
        PolicyDocument=dumps(glue_policy_document),
    )

    LOGGER.info("Attached Glue general access policy to role %s", role_name)
    return response


def attach_inline_s3_policy(role_name: str, bucket_name: str) -> dict:
    """
    Attach an inline S3 access policy to a role.

    Parameters
    ----------
    role_name : str
        Name of the IAM role.
    bucket_name : str
        Name of the S3 bucket to grant access to.

    Returns
    -------
    dict
        AWS response from put_role_policy.
    """
    iam_client: IAMClient = boto3.client("iam")

    policy_document = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Sid": "ListObjectsInBucket",
                "Effect": "Allow",
                "Action": ["s3:ListBucket"],
                "Resource": [f"arn:aws:s3:::{bucket_name}"],
            },
            {
                "Sid": "AllObjectActions",
                "Effect": "Allow",
                "Action": "s3:*Object",
                "Resource": [f"arn:aws:s3:::{bucket_name}/*"],
            },
        ],
    }

    response = iam_client.put_role_policy(
        RoleName=role_name,
        PolicyName=S3_ROLE_POLICY_NAME,
        PolicyDocument=dumps(policy_document),
    )

    LOGGER.info(
        "Attached inline S3 policy to role %s for bucket %s", role_name, bucket_name
    )
    return response


def create_glue_service_role(role_name: str) -> dict:
    """
    Create an IAM Role for AWS Glue service.

    Parameters
    ----------
    role_name : str
        Name of the IAM role to create.

    Returns
    -------
    dict
        AWS response from create_role.
    """
    iam_client: IAMClient = boto3.client("iam")

    assume_role_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {"Service": "glue.amazonaws.com"},
                "Action": "sts:AssumeRole",
            }
        ],
    }

    response = iam_client.create_role(
        RoleName=role_name,
        AssumeRolePolicyDocument=dumps(assume_role_policy),
        Description="IAM role for AWS Glue service to access AWS resources.",
    )

    LOGGER.info("Created IAM role %s", role_name)
    return response


def delete_glue_general_access_policy(role_name: str) -> dict:
    """
    Delete the inline Glue general access policy attached to the IAM role.

    Parameters
    ----------
    role_name : str
        Name of the IAM role.

    Returns
    -------
    dict
        AWS response from delete_role_policy.
    """
    iam_client: IAMClient = boto3.client("iam")

    response = iam_client.delete_role_policy(
        RoleName=role_name,
        PolicyName=GLUE_ROLE_POLICY_NAME,
    )

    LOGGER.info("Deleted Glue general access policy from role %s", role_name)
    return response


def delete_glue_service_role(role_name: str) -> dict:
    """
    Delete the specified IAM Role for AWS Glue service.

    Parameters:
    ----------
    role_name : str
        Name of the IAM role to delete.

    Returns
    -------
    dict
        AWS response from delete_role.
    """
    iam_client: IAMClient = boto3.client("iam")
    response = iam_client.delete_role(RoleName=role_name)

    LOGGER.info("Deleted IAM role %s", role_name)
    return response


def delete_inline_s3_policy(role_name: str) -> dict:
    """
    Delete the inline S3 access policy attached to the IAM role.

    Parameters
    ----------
    role_name : str
        Name of the IAM role.

    Returns
    -------
    dict
        AWS response from delete_role_policy.
    """
    iam_client: IAMClient = boto3.client("iam")

    response = iam_client.delete_role_policy(
        RoleName=role_name,
        PolicyName=S3_ROLE_POLICY_NAME,
    )

    LOGGER.info("Deleted inline S3 policy from role %s", role_name)
    return response
