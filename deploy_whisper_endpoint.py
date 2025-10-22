#!/usr/bin/env python3
"""
Deploy Whisper Large V3 Turbo from SageMaker JumpStart
This script creates a SageMaker endpoint for audio transcription
"""

import boto3
import time
from datetime import datetime

# Configuration
REGION = 'ap-southeast-2'
MODEL_ARN = 'arn:aws:sagemaker:ap-southeast-2:aws:hub-content/SageMakerPublicHub/Model/huggingface-asr-whisper-large-v3-turbo/1.1.12'
ENDPOINT_NAME = f'whisper-large-v3-turbo-{int(time.time())}'
INSTANCE_TYPE = 'ml.g5.xlarge'  # GPU instance for faster inference

# Initialize SageMaker client
sagemaker = boto3.client('sagemaker', region_name=REGION)

print("🚀 Deploying Whisper Large V3 Turbo to SageMaker...")
print(f"📍 Region: {REGION}")
print(f"🎯 Endpoint Name: {ENDPOINT_NAME}")
print(f"💻 Instance Type: {INSTANCE_TYPE}")
print()

try:
    # Create model from JumpStart ARN
    print("1️⃣ Creating SageMaker model from JumpStart...")
    model_name = f'whisper-model-{int(time.time())}'
    
    # Note: For JumpStart models, you typically need to use create_model with container image
    # This is a simplified example - actual deployment may require additional setup
    
    response = sagemaker.create_model(
        ModelName=model_name,
        PrimaryContainer={
            'ModelDataUrl': MODEL_ARN,
            'Environment': {
                'SAGEMAKER_PROGRAM': 'inference.py',
                'SAGEMAKER_SUBMIT_DIRECTORY': MODEL_ARN
            }
        },
        ExecutionRoleArn='arn:aws:iam::YOUR_ACCOUNT:role/SageMakerExecutionRole'  # Update this
    )
    print(f"✅ Model created: {model_name}")
    
    # Create endpoint configuration
    print("2️⃣ Creating endpoint configuration...")
    config_name = f'whisper-config-{int(time.time())}'
    
    sagemaker.create_endpoint_config(
        EndpointConfigName=config_name,
        ProductionVariants=[{
            'VariantName': 'AllTraffic',
            'ModelName': model_name,
            'InstanceType': INSTANCE_TYPE,
            'InitialInstanceCount': 1
        }]
    )
    print(f"✅ Endpoint config created: {config_name}")
    
    # Create endpoint
    print("3️⃣ Creating endpoint (this takes 5-10 minutes)...")
    sagemaker.create_endpoint(
        EndpointName=ENDPOINT_NAME,
        EndpointConfigName=config_name
    )
    
    # Wait for endpoint to be in service
    print("⏳ Waiting for endpoint to deploy...")
    waiter = sagemaker.get_waiter('endpoint_in_service')
    waiter.wait(EndpointName=ENDPOINT_NAME)
    
    print()
    print("=" * 60)
    print("✅ DEPLOYMENT SUCCESSFUL!")
    print("=" * 60)
    print()
    print(f"🎙️ Whisper Endpoint Name: {ENDPOINT_NAME}")
    print()
    print("📝 Add this to your .env file:")
    print(f"WHISPER_ENDPOINT_NAME={ENDPOINT_NAME}")
    print()
    print("💰 Cost Estimate:")
    print(f"   Instance: {INSTANCE_TYPE}")
    print(f"   Cost: ~$1.00/hour while running")
    print(f"   Recommendation: Delete when not in use")
    print()
    print("🗑️ To delete the endpoint later:")
    print(f"   aws sagemaker delete-endpoint --endpoint-name {ENDPOINT_NAME}")
    print()

except Exception as e:
    print(f"❌ Deployment failed: {e}")
    print()
    print("💡 Note: This is a simplified deployment script.")
    print("   For production, use SageMaker JumpStart UI or boto3 deploy_model() method")
    print()
    print("🔧 Alternative: Deploy via AWS Console:")
    print("   1. Go to SageMaker Console > JumpStart")
    print("   2. Search: 'whisper-large-v3-turbo'")
    print("   3. Click 'Deploy'")
    print("   4. Copy endpoint name to .env")
