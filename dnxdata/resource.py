import boto3

# S3
s3_client = boto3.client('s3')
s3_resource = boto3.resource('s3')

# Dynamodb
dynamo_client = boto3.client('dynamodb')
dynamo_resource = boto3.resource('dynamodb')

# Glue
glue_client = boto3.client("glue")

# Lambda
lambda_client = boto3.client('lambda')

# SSM
ssm_client = boto3.client('ssm')
