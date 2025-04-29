"""Application wide configuration variables"""

from configparser import ConfigParser
from pathlib import Path

config_path = Path(__file__).resolve().parents[1] / "dwh.cfg"
config = ConfigParser()
config.read(str(config_path))

S3_BUCKET_NAME = config.get("S3", "S3_BUCKET_NAME")
ROUTE_TABLE_ID = config.get("EC2", "ROUTE_TABLE_ID")
VPC_ID = config.get("EC2", "VPC_ID")
REGION = config.get("AWS", "REGION")
GLUE_ROLE_NAME = config.get("IAM", "GLUE_ROLE_NAME")
GLUE_ROLE_POLICY_NAME = config.get("IAM", "GLUE_ROLE_POLICY_NAME")
S3_ROLE_POLICY_NAME = config.get("IAM", "S3_ROLE_POLICY_NAME")
DB_NAME = config.get("GLUE", "DB_NAME")
