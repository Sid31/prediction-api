#!/bin/bash

# Setup S3 bucket for StreamBet

echo "🪣 Setting up S3 bucket for StreamBet"
echo "======================================"
echo ""

# Load credentials
set -a
source .env
set +a

# Generate unique bucket name
BUCKET_NAME="streambet-demo-$(date +%s)"

echo "Creating bucket: $BUCKET_NAME"
echo ""

# Try to create bucket using Python boto3
python3 << EOF
import boto3
import os

bucket_name = "$BUCKET_NAME"
region = os.getenv('AWS_REGION', 'us-east-1')

try:
    s3_client = boto3.client('s3', region_name=region)
    
    # Create bucket
    if region == 'us-east-1':
        s3_client.create_bucket(Bucket=bucket_name)
    else:
        s3_client.create_bucket(
            Bucket=bucket_name,
            CreateBucketConfiguration={'LocationConstraint': region}
        )
    
    print(f"✅ Bucket created: {bucket_name}")
    print(f"")
    print(f"Update your .env file:")
    print(f"AWS_BUCKET={bucket_name}")
    
except Exception as e:
    print(f"❌ Error: {e}")
    print(f"")
    print(f"Please create the bucket manually in AWS Console")
    print(f"Or add S3 permissions to your IAM user")

EOF

echo ""
echo "======================================"
