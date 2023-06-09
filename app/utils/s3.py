from app.init import get_env, get_path
import boto3
from botocore.client import Config
import logging

logging.info(f'Setting up S3 bucket: {get_env("S3_Url")}')
s3 = boto3.resource(
    's3',
    endpoint_url=get_env('S3_Url'),
    aws_access_key_id=get_env('S3_Username'),
    aws_secret_access_key=get_env('S3_Password'),
    config=Config(signature_version='s3v4')
)

# try: 
#     s3.list_buckets()
# except Exception:
#     logging.error('Could not connect to S3')

# Create bucket if it does not exist
bucket_name = get_env('S3_Bucket')
#logging.info(f'Creating bucket {bucket_name} if it does not exist')
try:
    s3.meta.client.head_bucket(Bucket=bucket_name)
except:
    try:
        s3.create_bucket(Bucket=bucket_name)
    except:
        logging.exception('Could not connect to S3')

s3_bucket = s3.Bucket(bucket_name)