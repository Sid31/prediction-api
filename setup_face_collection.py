#!/usr/bin/env python3
"""
Setup AWS Rekognition Face Collection for IShowSpeed recognition
"""

import boto3
import os
from dotenv import load_dotenv

load_dotenv()

# AWS Configuration
AWS_REGION = os.getenv('AWS_REGION', 'us-east-1')
AWS_BUCKET = os.getenv('AWS_BUCKET', 'predictionchat')
COLLECTION_ID = 'streambet-streamers'

# Initialize clients
rekognition = boto3.client('rekognition', region_name=AWS_REGION)
s3 = boto3.client('s3', region_name=AWS_REGION)

def create_collection():
    """Create a face collection for streamer recognition"""
    try:
        print(f"📦 Creating face collection: {COLLECTION_ID}")
        rekognition.create_collection(CollectionId=COLLECTION_ID)
        print(f"✅ Collection created successfully!")
    except rekognition.exceptions.ResourceAlreadyExistsException:
        print(f"ℹ️  Collection already exists")
    except Exception as e:
        print(f"❌ Error creating collection: {e}")
        return False
    return True

def upload_reference_image(image_path, streamer_name):
    """Upload reference image to S3 and index face"""
    try:
        # Upload to S3
        s3_key = f"faces/{streamer_name}.jpeg"
        print(f"☁️  Uploading {image_path} to S3...")
        s3.upload_file(image_path, AWS_BUCKET, s3_key)
        print(f"✅ Uploaded to s3://{AWS_BUCKET}/{s3_key}")
        
        # Index face in collection
        print(f"🔍 Indexing face for {streamer_name}...")
        response = rekognition.index_faces(
            CollectionId=COLLECTION_ID,
            Image={'S3Object': {'Bucket': AWS_BUCKET, 'Name': s3_key}},
            ExternalImageId=streamer_name,
            MaxFaces=1,
            QualityFilter='AUTO',
            DetectionAttributes=['ALL']
        )
        
        if response['FaceRecords']:
            face_id = response['FaceRecords'][0]['Face']['FaceId']
            print(f"✅ Face indexed successfully!")
            print(f"   Face ID: {face_id}")
            print(f"   Streamer: {streamer_name}")
            return True
        else:
            print(f"❌ No face detected in image")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def list_faces():
    """List all faces in the collection"""
    try:
        response = rekognition.list_faces(CollectionId=COLLECTION_ID)
        print(f"\n📋 Faces in collection:")
        for face in response['Faces']:
            print(f"   - {face.get('ExternalImageId', 'Unknown')}: {face['FaceId']}")
        return response['Faces']
    except Exception as e:
        print(f"❌ Error listing faces: {e}")
        return []

def main():
    print("🎮 StreamBet Face Collection Setup")
    print("=" * 50)
    print()
    
    # Step 1: Create collection
    if not create_collection():
        return
    
    # Step 2: Check if reference image exists
    image_path = 'ishowspeed.jpeg'
    if not os.path.exists(image_path):
        print(f"❌ Reference image not found: {image_path}")
        print(f"   Please place ishowspeed.jpeg in the current directory")
        return
    
    # Step 3: Upload and index IShowSpeed's face
    print()
    if upload_reference_image(image_path, 'ishowspeed'):
        print()
        print("✅ Setup complete!")
        print()
        list_faces()
        print()
        print("🎯 Next steps:")
        print("   1. Run the server: ./start.sh")
        print("   2. Upload tets.mp4")
        print("   3. System will detect IShowSpeed + backflips!")
    else:
        print("❌ Setup failed")

if __name__ == '__main__':
    main()
