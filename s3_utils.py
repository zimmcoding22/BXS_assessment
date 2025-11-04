import os
from pathlib import Path
import boto3
from botocore.exceptions import ClientError
from dotenv import load_dotenv

load_dotenv()

def get_s3_client():
    """Create and return a boto3 S3 client using environment credentials."""
    return boto3.client(
        "s3",
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        region_name=os.getenv("AWS_DEFAULT_REGION", "us-east-1"),
    )


def upload_file_to_s3(file_path: Path, bucket_name: str, prefix: str = "") -> str:
    """
    Upload a local file to an S3 bucket.
    Args:
        file_path (Path): The path to the local file.
        bucket_name (str): Name of the target S3 bucket.
        prefix (str): Optional folder path within the bucket.

    Returns:
        str: The S3 URI of the uploaded file.
    """
    s3_client = get_s3_client()
    key = f"{prefix.rstrip('/')}/{file_path.name}" if prefix else file_path.name

    try:
        s3_client.upload_file(str(file_path), bucket_name, key)
        uri = f"s3://{bucket_name}/{key}"
        print(f"Uploaded {file_path} → {uri}")
        return uri
    except ClientError as e:
        print(f"Upload failed for {file_path}: {e}")
        raise


def list_objects_in_prefix(bucket_name: str, prefix: str = "") -> list[str]:
    """
    List all objects under a given bucket/prefix.
    Args:
        bucket_name (str): S3 bucket name.
        prefix (str): Prefix (folder path) within the bucket.

    Returns:
        list[str]: List of object keys in the prefix.
    """
    s3_client = get_s3_client()
    try:
        response = s3_client.list_objects_v2(Bucket=bucket_name, Prefix=prefix)
        contents = response.get("Contents", [])
        keys = [obj["Key"] for obj in contents]
        print(f"Found {len(keys)} object(s) in s3://{bucket_name}/{prefix}")
        return keys
    except ClientError as e:
        print(f"Failed to list objects in s3://{bucket_name}/{prefix}: {e}")
        raise


# Example local test execution
if __name__ == "__main__":
    bucket = os.getenv("S3_BUCKET_NAME")
    test_file = Path("output/order_summary.csv")

    if not bucket:
        print("No S3 bucket configured in environment (.env).")
    elif not test_file.exists():
        print(f"Test file not found at {test_file}")
    else:
        upload_file_to_s3(test_file, bucket, prefix="etl-test/")
        list_objects_in_prefix(bucket, prefix="etl-test/")

"""
Example IAM Policy (minimum permissions)
--------------------------------------------
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:PutObject",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::your-bucket-name",
        "arn:aws:s3:::your-bucket-name/*"
      ]
    }
  ]
}
"""
