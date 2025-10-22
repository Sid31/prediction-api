"""
Advanced AWS Rekognition Tracking for StreamBet
Uses person tracking + face recognition for better accuracy
"""

import boto3
import time
import json

class AdvancedStreamTracker:
    def __init__(self):
        self.rekognition = boto3.client('rekognition', region_name='us-east-1')
        self.s3 = boto3.client('s3')
        self.bucket_name = 'predictionchat'
        self.face_collection = 'streamers'
        
    def setup_face_collection(self):
        """Create face collection for streamers"""
        try:
            self.rekognition.create_collection(
                CollectionId=self.face_collection
            )
            print(f"✅ Created face collection: {self.face_collection}")
        except self.rekognition.exceptions.ResourceAlreadyExistsException:
            print(f"✅ Face collection already exists: {self.face_collection}")
    
    def add_streamer_face(self, image_bytes, streamer_name):
        """Add streamer's face to collection"""
        try:
            response = self.rekognition.index_faces(
                CollectionId=self.face_collection,
                Image={'Bytes': image_bytes},
                ExternalImageId=streamer_name,
                DetectionAttributes=['ALL']
            )
            
            if response['FaceRecords']:
                print(f"✅ Added {streamer_name} to face collection")
                return True
            return False
        except Exception as e:
            print(f"❌ Error adding face: {e}")
            return False
    
    def analyze_frame_with_tracking(self, frame_bytes):
        """
        Advanced frame analysis with:
        1. Person detection
        2. Face recognition
        3. Activity detection
        4. Pose estimation
        """
        results = {
            'person_detected': False,
            'face_match': None,
            'labels': [],
            'poses': []
        }
        
        # 1. Detect labels (activities)
        try:
            label_response = self.rekognition.detect_labels(
                Image={'Bytes': frame_bytes},
                MaxLabels=15,
                MinConfidence=70
            )
            results['labels'] = label_response.get('Labels', [])
        except Exception as e:
            print(f"❌ Label detection error: {e}")
        
        # 2. Detect people with pose estimation
        try:
            person_response = self.rekognition.detect_labels(
                Image={'Bytes': frame_bytes},
                MaxLabels=15,
                Features=['GENERAL_LABELS']
            )
            
            # Check for person labels
            for label in person_response.get('Labels', []):
                if label['Name'].lower() in ['person', 'human']:
                    results['person_detected'] = True
                    
                    # Get instances (bounding boxes)
                    if 'Instances' in label:
                        for instance in label['Instances']:
                            if 'BoundingBox' in instance:
                                results['poses'].append({
                                    'box': instance['BoundingBox'],
                                    'confidence': instance.get('Confidence', 0)
                                })
        except Exception as e:
            print(f"❌ Person detection error: {e}")
        
        # 3. Search for known faces
        if results['person_detected']:
            try:
                face_response = self.rekognition.search_faces_by_image(
                    CollectionId=self.face_collection,
                    Image={'Bytes': frame_bytes},
                    MaxFaces=1,
                    FaceMatchThreshold=80
                )
                
                if face_response.get('FaceMatches'):
                    match = face_response['FaceMatches'][0]
                    results['face_match'] = {
                        'streamer': match['Face']['ExternalImageId'],
                        'confidence': match['Similarity']
                    }
                    print(f"✅ Recognized: {match['Face']['ExternalImageId']} ({match['Similarity']:.1f}%)")
            except Exception as e:
                # Face not found or collection doesn't exist
                pass
        
        return results
    
    def track_person_in_video(self, video_path, s3_key):
        """
        Use AWS Video API for advanced person tracking
        (Async - requires S3 upload and SNS)
        """
        # Upload to S3 first
        with open(video_path, 'rb') as f:
            self.s3.upload_fileobj(f, self.bucket_name, s3_key)
        
        # Start person tracking
        response = self.rekognition.start_person_tracking(
            Video={
                'S3Object': {
                    'Bucket': self.bucket_name,
                    'Name': s3_key
                }
            },
            NotificationChannel={
                'SNSTopicArn': 'arn:aws:sns:us-east-1:123456789:RekognitionTopic',
                'RoleArn': 'arn:aws:iam::123456789:role/RekognitionRole'
            }
        )
        
        job_id = response['JobId']
        print(f"🎬 Started person tracking job: {job_id}")
        
        # Wait for completion (in production, use SNS callback)
        return self.wait_for_tracking_job(job_id)
    
    def wait_for_tracking_job(self, job_id, max_wait=60):
        """Wait for person tracking job to complete"""
        start_time = time.time()
        
        while time.time() - start_time < max_wait:
            try:
                response = self.rekognition.get_person_tracking(JobId=job_id)
                status = response['JobStatus']
                
                if status == 'SUCCEEDED':
                    print("✅ Person tracking complete!")
                    return self.process_tracking_results(response)
                elif status == 'FAILED':
                    print(f"❌ Tracking failed: {response.get('StatusMessage')}")
                    return None
                else:
                    print(f"⏳ Job status: {status}")
                    time.sleep(2)
            except Exception as e:
                print(f"❌ Error checking job: {e}")
                return None
        
        print("⏰ Timeout waiting for job")
        return None
    
    def process_tracking_results(self, response):
        """Process person tracking results"""
        persons = response.get('Persons', [])
        
        # Group by person ID
        person_tracks = {}
        for person in persons:
            person_id = person['Person']['Index']
            timestamp = person['Timestamp']
            
            if person_id not in person_tracks:
                person_tracks[person_id] = []
            
            person_tracks[person_id].append({
                'timestamp': timestamp / 1000,  # Convert to seconds
                'box': person['Person']['BoundingBox'],
                'confidence': person['Person'].get('Confidence', 0)
            })
        
        return person_tracks
    
    def detect_backflip_with_tracking(self, frame_sequence):
        """
        Detect backflip using motion tracking
        
        Backflip characteristics:
        1. Person vertical position changes dramatically
        2. Upside down (bounding box flips)
        3. Rapid movement
        4. Activity labels confirm (jumping, acrobatics)
        """
        backflips = []
        
        for i in range(1, len(frame_sequence)):
            prev_frame = frame_sequence[i-1]
            curr_frame = frame_sequence[i]
            
            # Check if person moved significantly
            if prev_frame['poses'] and curr_frame['poses']:
                prev_box = prev_frame['poses'][0]['box']
                curr_box = curr_frame['poses'][0]['box']
                
                # Calculate vertical movement
                prev_y = prev_box['Top'] + prev_box['Height'] / 2
                curr_y = curr_box['Top'] + curr_box['Height'] / 2
                vertical_change = abs(curr_y - prev_y)
                
                # Check for backflip indicators
                has_jump_label = any(
                    'jump' in l['Name'].lower() or 'flip' in l['Name'].lower()
                    for l in curr_frame['labels']
                )
                
                if vertical_change > 0.3 and has_jump_label:
                    backflips.append({
                        'timestamp': curr_frame['timestamp'],
                        'vertical_change': vertical_change,
                        'confidence': 0.9
                    })
                    print(f"🎪 Backflip detected at {curr_frame['timestamp']:.2f}s")
        
        return backflips


# Example usage
if __name__ == '__main__':
    tracker = AdvancedStreamTracker()
    
    # Setup (one-time)
    tracker.setup_face_collection()
    
    # Add IShowSpeed's face (from reference image)
    # with open('ishowspeed_face.jpg', 'rb') as f:
    #     tracker.add_streamer_face(f.read(), 'ishowspeed')
    
    print("✅ Advanced tracking system ready!")
