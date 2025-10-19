#!/usr/bin/env python3
"""
Test AWS Rekognition Person Tracking permissions
"""

import boto3
import os
from dotenv import load_dotenv

load_dotenv()

# AWS Configuration
AWS_REGION = os.getenv('AWS_REGION', 'us-east-1')
AWS_BUCKET = os.getenv('AWS_BUCKET', 'predictionchat')

print("🔍 Testing AWS Rekognition Person Tracking")
print("=" * 60)
print()

# Initialize client
try:
    rek_client = boto3.client('rekognition', region_name=AWS_REGION)
    print("✅ Rekognition client initialized")
except Exception as e:
    print(f"❌ Failed to initialize client: {e}")
    exit(1)

# Test 1: Check credentials
print("\n📋 Test 1: Checking AWS Credentials")
try:
    sts = boto3.client('sts', region_name=AWS_REGION)
    identity = sts.get_caller_identity()
    print(f"✅ Account: {identity['Account']}")
    print(f"✅ User ARN: {identity['Arn']}")
except Exception as e:
    print(f"❌ Credentials error: {e}")
    exit(1)

# Test 2: List S3 files (verify S3 access)
print("\n📋 Test 2: Checking S3 Access")
try:
    s3 = boto3.client('s3', region_name=AWS_REGION)
    response = s3.list_objects_v2(Bucket=AWS_BUCKET, MaxKeys=1)
    print(f"✅ S3 access working (bucket: {AWS_BUCKET})")
except Exception as e:
    print(f"❌ S3 error: {e}")

# Test 3: Try to start person tracking on a test video
print("\n📋 Test 3: Testing StartPersonTracking API")
print("Looking for a test video in S3...")

try:
    # List videos in S3
    response = s3.list_objects_v2(Bucket=AWS_BUCKET, Prefix='videos/', MaxKeys=5)
    
    if 'Contents' in response and len(response['Contents']) > 0:
        test_video = response['Contents'][0]['Key']
        print(f"Found test video: {test_video}")
        
        # Try to start person tracking
        print("\nAttempting to start person tracking...")
        try:
            response = rek_client.start_person_tracking(
                Video={'S3Object': {'Bucket': AWS_BUCKET, 'Name': test_video}}
            )
            job_id = response['JobId']
            print(f"✅ SUCCESS! Person tracking started!")
            print(f"   Job ID: {job_id}")
            print("\n🎉 Person tracking is working! The issue was resolved!")
            
        except rek_client.exceptions.AccessDeniedException as e:
            print(f"❌ AccessDeniedException: {e}")
            print("\n🔍 Diagnosis:")
            print("   - Your IAM user lacks permission to call StartPersonTracking")
            print("   - This is a Rekognition Video API that needs special permissions")
            print("\n💡 Solution:")
            print("   Add this policy to your IAM user:")
            print("""
   {
     "Version": "2012-10-17",
     "Statement": [
       {
         "Effect": "Allow",
         "Action": [
           "rekognition:StartPersonTracking",
           "rekognition:GetPersonTracking"
         ],
         "Resource": "*"
       }
     ]
   }
            """)
            
        except Exception as e:
            print(f"❌ Other error: {e}")
            print(f"   Error type: {type(e).__name__}")
    else:
        print("❌ No videos found in S3 to test with")
        
except Exception as e:
    print(f"❌ Error: {e}")

print("\n" + "=" * 60)
print("🏁 Test Complete")
print()
