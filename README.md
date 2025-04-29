# STEDI Human Balance Analytics

Automated AWS resource management for the STEDI Human Balance Analytics project.

This project sets up and manages the foundational AWS infrastructure required to collect, transform, and analyze human balance sensor data using a data lake architecture. It prepares the AWS environment for Visual ETL assignment questions.

It includes:

- S3 bucket creation and sample data loading
- IAM role and policy management for AWS Glue access
- Optional creation of VPC endpoints for private S3 connectivity
- AWS Glue database and table creation from JSON schema definitions
- Flexible, modular CLI for setting up and tearing down specific AWS resources

---

## Project Structure

### 📁 File Tree

```
app/
├── data/
│   ├── accelerometer/
│   │   ├── landing/
│   │   └── schema.json
│   ├── customer/
│   │   ├── landing/
│   │   └── schema.json
│   └── step_trainer/
├── schemas/
│   ├── accelerometer/
│   │   ├── landing/
│   │   └── schema.json
│   │   ├── trusted/
│   │   └── schema.json
│   ├── customer/
│   │   ├── curated/
│   │   └── schema.json
│   │   ├── landing/
│   │   └── schema.json
│   │   ├── trusted/
│   │   └── schema.json
│   ├── machine_learning/
│   │   ├── curated/
│   │   └── schema.json
│   └── step_trainer/
│   │   ├── landing/
│   │   └── schema.json
│   │   ├── trusted/
│   │   └── schema.json
├── iac/
│   ├── __init__.py
│   ├── common.py
│   ├── config.py
│   ├── glue.py
│   ├── iam.py
│   ├── logger.py
│   ├── s3.py
│   ├── setup.py
│   ├── teardown.py
│   └── vpc.py
└── __main__.py
```

### 📘 Description of Key Files

| Path             | Description                                          |
| ---------------- | ---------------------------------------------------- |
| `data/`          | Sample raw data Glue tables                          |
| `accelerometer/` | Accelerometer JSON data and schema file              |
| `customer/`      | Customer JSON data and schema file                   |
| `step_trainer/`  | Placeholder for future Step Trainer data             |
| `schemas/`       | Schema definitions for Glue tables                   |
| `iac/`           | Infrastructure-as-Code logic for AWS setup/teardown  |
| `config.py`      | Constants like S3 bucket name, region, VPC ID, etc.  |
| `common.py`      | Shared decorators and helper methods (e.g., waiters) |
| `glue.py`        | Glue database and table creation                     |
| `iam.py`         | IAM role and inline policy creation for Glue         |
| `logger.py`      | Colorized logging configuration                      |
| `s3.py`          | S3 bucket creation, deletion, and data loading       |
| `vpc.py`         | VPC endpoint creation/removal                        |
| `setup.py`       | Orchestrates full setup flow                         |
| `teardown.py`    | Orchestrates full teardown flow                      |
| `__main__.py`    | CLI entry point using argparse                       |

---

## Installation

To set up this project and provision the required AWS infrastructure, follow the steps below.

### 1. Clone the repository

```bash
git clone <your-repo-url>
cd <project-root>
```

### 2. Create a virtual environment and install dependencies

```bash
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```

### 3. Create a `dwh.cfg` configuration file

Create a file named `dwh.cfg` in the project root with the following structure:

```ini
[AWS]
REGION=<region>

[S3]
S3_BUCKET_NAME=<bucket_name>

[EC2]
ROUTE_TABLE_ID=<route_table_id>
VPC_ID=<vpc_id>

[IAM]
GLUE_ROLE_NAME=stediGlueServiceRole
S3_ROLE_POLICY_NAME=stediS3Access
GLUE_ROLE_POLICY_NAME=stediGlueAccess

[GLUE]
DB_NAME=stedi_tracker
```

> ⚠️ **Note:** The names and IDs shown above are specific to this STEDI project and its testing environment. Your project may require different naming conventions, database/table names, or tighter IAM policies depending on your organization's security requirements.

### 4. Configure AWS CLI

You must authenticate using the [AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-quickstart.html):

```bash
aws configure
```

Use the Access Key and Secret Key from your IAM user. This user should have the following permissions (minimum for testing):

- `AmazonEC2FullAccess`
- `AmazonS3FullAccess`
- `AWSGlueConsoleFullAccess`
- `IAMFullAccess`

> 🔐 **Important:** Amazon recommends avoiding the use of long-term IAM access keys. For production use, consider configuring federated access via IAM Identity Center (formerly AWS SSO), or use environment credentials via roles or session tokens. See [AWS best practices for credentials](https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html) for more info.

### 5. Run setup and teardown from the CLI

The project exposes a CLI to provision and tear down AWS resources.

**To run a full setup:**

```bash
python -m app --setup
```

**To tear down everything:**

```bash
python -m app --teardown
```

**To customize setup/teardown behavior:**

Use flags such as:

```bash
python -m app --setup --init-vpc-endpoint --skip-load-data
python -m app --teardown --remove-vpc-endpoint --skip-bucket-removal
```

> 💡 Flags allow you to re-run partial setups or teardowns in case of failure. This is especially useful during iterative development or testing in constrained AWS environments.

## Academic Honesty

This application was developed for the Visual ETL assignments in the Udacity AWS Nanodegree program. You are welcome to use this code as a reference for your own project; however, Udacity has strict guidelines regarding academic honesty. It is essential that you do not copy this work and present it as your own. If you choose to use any part of this work for your assignment, you must provide proper attribution.

For more details, please refer to Udacity's Honor Code: https://www.udacity.com/legal/honor-code