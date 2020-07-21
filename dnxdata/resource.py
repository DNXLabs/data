import boto3
import os


_session = boto3.session.Session()
region_name = _session.region_name

AWS_REGION = os.getenv("AWS_REGION", region_name)

# S3
s3_client = boto3.client('s3', region_name=AWS_REGION)
s3_resource = boto3.resource('s3', region_name=AWS_REGION)

# Dynamodb
dynamo_client = boto3.client('dynamodb', region_name=AWS_REGION)
dynamo_resource = boto3.resource('dynamodb', region_name=AWS_REGION)

# Glue
glue_client = boto3.client("glue", region_name=AWS_REGION)

# Lambda
lambda_client = boto3.client('lambda', region_name=AWS_REGION)

# SSM
ssm_client = boto3.client('ssm', region_name=AWS_REGION)
