#!/bin/bash
echo "🧪 Quick Person Tracking Test"
python3 << 'PYTHON'
import boto3
import os
from dotenv import load_dotenv

load_dotenv()

rek = boto3.client('rekognition', region_name='us-east-1')
try:
    response = rek.start_person_tracking(
        Video={'S3Object': {'Bucket': 'predictionchat', 'Name': 'test-video.mp4'}}
    )
    print(f'✅ SUCCESS! Job ID: {response["JobId"]}')
    print('🎉 Person tracking is now working!')
except Exception as e:
    print(f'❌ Still failing: {e}')
    print(f'   Error type: {type(e).__name__}')
PYTHON
