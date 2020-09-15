import boto3
import os


_session = boto3.session.Session()
region_name = _session.region_name

AWS_REGION = os.getenv("AWS_REGION", region_name)
S3_ENDPOINT_URL = os.getenv("S3_ENDPOINT_URL", None)
DYNAMODB_ENDPOINT_URL = os.getenv("DYNAMODB_ENDPOINT_URL", None)

# S3
s3_client = boto3.client('s3', region_name=AWS_REGION, endpoint_url=S3_ENDPOINT_URL)
s3_resource = boto3.resource('s3', region_name=AWS_REGION, endpoint_url=S3_ENDPOINT_URL)

# Dynamodb
dynamo_client = boto3.client('dynamodb', region_name=AWS_REGION, endpoint_url=DYNAMODB_ENDPOINT_URL)
dynamo_resource = boto3.resource('dynamodb', region_name=AWS_REGION, endpoint_url=DYNAMODB_ENDPOINT_URL)

# Glue
glue_client = boto3.client("glue", region_name=AWS_REGION)

# Lambda
lambda_client = boto3.client('lambda', region_name=AWS_REGION)

# SSM
ssm_client = boto3.client('ssm', region_name=AWS_REGION)
