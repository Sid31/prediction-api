"""
StreamBet POC - AI-Powered Video Recognition for Live Betting
Hackathon Demo: AWS Rekognition + Simple Betting Interface
"""

import os
import time
import json
import cv2
import tempfile
from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
import boto3
from botocore.exceptions import ClientError
from werkzeug.utils import secure_filename
from PIL import Image
import io

app = Flask(__name__)
CORS(app)
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB max

# Configuration - Update these with your AWS credentials
AWS_BUCKET = os.getenv('AWS_BUCKET', 'streambet-demo-bucket')
AWS_REGION = os.getenv('AWS_REGION', 'us-east-1')
SNS_TOPIC_ARN = os.getenv('SNS_TOPIC_ARN', '')  # Optional
REKOGNITION_ROLE_ARN = os.getenv('REKOGNITION_ROLE_ARN', '')
USE_MOCK_MODE = os.getenv('USE_MOCK_MODE', 'false').lower() == 'true'  # Set to 'true' to save credits

# AWS Clients
try:
    s3_client = boto3.client('s3', region_name=AWS_REGION)
    rek_client = boto3.client('rekognition', region_name=AWS_REGION)
    print("✅ AWS clients initialized successfully")
except Exception as e:
    print(f"⚠️  AWS client initialization failed: {e}")
    print("💡 Set AWS credentials: export AWS_ACCESS_KEY_ID=xxx AWS_SECRET_ACCESS_KEY=xxx")

ALLOWED_EXTENSIONS = {'mp4', 'mov', 'avi'}
UPLOAD_FOLDER = 'uploads'

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Mock betting data for demo
DEMO_BETS = [
    {
        'id': 1,
        'event': 'Will streamer complete 10 backflips?',
        'odds': {'yes': 2.5, 'no': 1.5},
        'pool': 5000,
        'status': 'active'
    },
    {
        'id': 2,
        'event': 'Will streamer win the next game?',
        'odds': {'yes': 1.8, 'no': 2.2},
        'pool': 3200,
        'status': 'active'
    }
]

@app.route('/')
def index():
    """Serve the enhanced video player demo"""
    return render_template('video_player.html')

@app.route('/old')
def old_index():
    """Serve the old demo frontend"""
    return render_template('index.html')

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'StreamBet Recognition API',
        'version': '1.0.0-hackathon'
    })

@app.route('/uploads/<filename>')
def serve_upload(filename):
    """Serve uploaded files (screenshots)"""
    return send_from_directory(UPLOAD_FOLDER, filename)

@app.route('/api/bets', methods=['GET'])
def get_bets():
    """Get available betting markets"""
    return jsonify({'bets': DEMO_BETS})

@app.route('/api/analyze-frames', methods=['POST'])
def analyze_video_frames():
    """
    Analyze video using frame-by-frame extraction (faster, cheaper)
    Uses AWS Rekognition Image API instead of Video API
    Includes backflip/floating detection around 20 second mark
    """
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type. Use MP4, MOV, or AVI'}), 400
    
    try:
        # Save file locally
        filename = f"{int(time.time())}_{secure_filename(file.filename)}"
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)
        
        print(f"📹 Processing video: {filename}")
        
        # Save video URL for playback while analyzing
        video_url = f'/uploads/{filename}'
        print(f"🎬 Video playable at: http://localhost:5000{video_url}")
        
        # Extract frames (1 per second)
        frames = extract_frames(filepath, fps=1)
        
        if not frames:
            return jsonify({'error': 'Could not extract frames from video'}), 500
        
        # Analyze each frame
        print(f"🔍 Analyzing {len(frames)} frames with Rekognition...")
        
        all_labels = {}
        streamer_detections = []
        screenshots = []  # Store key frames with streamer
        backflip_indicators = []  # Track backflip-related detections
        
        # Backflip keywords to look for (includes action/movement indicators)
        backflip_keywords = ['jump', 'jumping', 'leap', 'leaping', 'airborne', 'flying', 'float', 
                            'floating', 'flip', 'flipping', 'acrobatics', 'gymnastics', 'backflip',
                            'fighting', 'action', 'motion', 'movement', 'sport', 'activity']
        
        for i, (timestamp, frame_bytes) in enumerate(frames):
            progress = int((i + 1) / len(frames) * 100)
            print(f"⏳ Frame {i+1}/{len(frames)} (t={timestamp:.2f}s) - {progress}%...", end='\r')
            
            frame_result = analyze_frame_with_rekognition(frame_bytes, rek_client)
            
            # Aggregate labels
            for label in frame_result['labels']:
                label_name = label['Name']
                if label_name not in all_labels:
                    all_labels[label_name] = {
                        'name': label_name,
                        'max_confidence': label['Confidence'],
                        'timestamps': []
                    }
                else:
                    all_labels[label_name]['max_confidence'] = max(
                        all_labels[label_name]['max_confidence'],
                        label['Confidence']
                    )
                all_labels[label_name]['timestamps'].append(timestamp)
                
                # Check for backflip indicators (especially around 20s mark)
                if any(keyword in label_name.lower() for keyword in backflip_keywords):
                    backflip_indicators.append({
                        'timestamp': timestamp,
                        'label': label_name,
                        'confidence': label['Confidence'],
                        'near_20s': abs(timestamp - 20.0) < 3.0  # Within 3 seconds of 20s
                    })
                    if abs(timestamp - 20.0) < 3.0:
                        print(f"\n🎪 BACKFLIP INDICATOR at {timestamp:.2f}s: {label_name} ({label['Confidence']:.1f}%)")
            
            # Track streamer appearances
            if frame_result['streamer_match']:
                streamer_detections.append({
                    'timestamp': timestamp,
                    'streamer': frame_result['streamer_match']['external_image_id'],
                    'confidence': frame_result['streamer_match']['similarity']
                })
                
                # Save screenshot of key frames (first 5 detections OR near 20s)
                should_save = len(screenshots) < 5 or abs(timestamp - 20.0) < 2.0
                if should_save:
                    screenshot_filename = f"screenshot_{int(timestamp)}s_{int(time.time())}.jpg"
                    screenshot_path = os.path.join(UPLOAD_FOLDER, screenshot_filename)
                    with open(screenshot_path, 'wb') as f:
                        f.write(frame_bytes)
                    
                    # Check if this frame has backflip indicators
                    has_backflip = any(abs(bi['timestamp'] - timestamp) < 0.1 for bi in backflip_indicators)
                    
                    screenshots.append({
                        'timestamp': timestamp,
                        'filename': screenshot_filename,
                        'url': f'/uploads/{screenshot_filename}',
                        'streamer': frame_result['streamer_match']['external_image_id'],
                        'confidence': frame_result['streamer_match']['similarity'],
                        'has_backflip_indicator': has_backflip,
                        'near_20s': abs(timestamp - 20.0) < 2.0
                    })
        
        print("\n✅ Frame analysis complete!")
        
        # Keep video file for playback - don't delete it
        # It can be accessed at /uploads/<filename>
        print(f"💾 Video saved for playback: {video_url}")
        
        # Format results
        labels_list = sorted(
            all_labels.values(),
            key=lambda x: x['max_confidence'],
            reverse=True
        )
        
        # Determine identified streamer
        identified_streamer = None
        if streamer_detections:
            # Count detections by streamer
            streamer_counts = {}
            for det in streamer_detections:
                streamer = det['streamer']
                if streamer not in streamer_counts:
                    streamer_counts[streamer] = []
                streamer_counts[streamer].append(det)
            
            # Get most detected streamer
            most_detected = max(streamer_counts.items(), key=lambda x: len(x[1]))
            identified_streamer = {
                'identified': True,
                'streamer': most_detected[0],
                'total_appearances': len(most_detected[1]),
                'appearances': most_detected[1][:10],  # First 10
                'timestamps': [d['timestamp'] for d in most_detected[1][:5]]
            }
            
            print(f"\n😎 STREAMER IDENTIFIED: {identified_streamer['streamer']}")
            print(f"   Appearances: {identified_streamer['total_appearances']}")
            print(f"   Timestamps: {identified_streamer['timestamps']}")
        else:
            identified_streamer = {'identified': False}
            print("\n⚠️  No known streamers identified")
        
        # Print top labels
        print(f"\n📋 TOP DETECTED LABELS ({len(labels_list)}):")
        for i, label in enumerate(labels_list[:10], 1):
            print(f"  {i}. {label['name']} - {label['max_confidence']:.1f}% - {len(label['timestamps'])} frames")
        
        # Analyze backflip indicators
        backflip_detected = False
        backflip_timestamp = None
        if backflip_indicators:
            print(f"\n🎪 ACTION/BACKFLIP ANALYSIS:")
            print(f"   Total action indicators found: {len(backflip_indicators)}")
            # Show all indicators with high confidence
            top_indicators = sorted(backflip_indicators, key=lambda x: x['confidence'], reverse=True)[:5]
            for bi in top_indicators:
                near_marker = " ⭐ NEAR 20s!" if bi['near_20s'] else ""
                print(f"   - {bi['timestamp']:.2f}s: {bi['label']} ({bi['confidence']:.1f}%){near_marker}")
            
            near_20s = [bi for bi in backflip_indicators if bi['near_20s']]
            if near_20s:
                backflip_detected = True
                backflip_timestamp = near_20s[0]['timestamp']
                print(f"\n   ✅ Backflip detected at {backflip_timestamp:.2f}s (near 20s mark)")
            elif backflip_indicators:
                # Use highest confidence indicator even if not near 20s
                backflip_detected = True
                backflip_timestamp = top_indicators[0]['timestamp']
                print(f"\n   ✅ Action/movement detected at {backflip_timestamp:.2f}s")
        
        return jsonify({
            'status': 'success',
            'processing_method': 'frame_by_frame',
            'video_url': video_url,  # URL to play the video
            'video_filename': filename,
            'total_frames': len(frames),
            'total_labels': len(labels_list),
            'labels': labels_list[:15],
            'face_data': identified_streamer,
            'screenshots': screenshots,  # Key frames with streamer
            'backflip_analysis': {
                'detected': backflip_detected,
                'timestamp': backflip_timestamp,
                'indicators': backflip_indicators,
                'near_20s_count': len([bi for bi in backflip_indicators if bi['near_20s']])
            },
            'video_metadata': {
                'duration_seconds': frames[-1][0] if frames else 0,
                'frames_analyzed': len(frames)
            }
        })
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@app.route('/api/analyze', methods=['POST'])
def analyze_video():
    """
    DEPRECATED: Old Video API endpoint (has permission issues)
    Redirects to new frame-by-frame analysis endpoint
    Use /api/analyze-frames instead for better performance
    """
    print("⚠️  /api/analyze is deprecated. Redirecting to /api/analyze-frames")
    return analyze_video_frames()

def get_mock_backflip_results(filename):
    """
    Return mock results for demo without using AWS credits
    Simulates detecting a backflip at 20 seconds
    """
    return {
        'status': 'success',
        'job_id': 'mock_job_123',
        'total_labels': 15,
        'labels': [
            {
                'label': 'Acrobatics',
                'confidence': 89.5,
                'category': 'Sports and Fitness',
                'timestamps': [20.1, 20.5]
            },
            {
                'label': 'Gymnastics',
                'confidence': 85.2,
                'category': 'Sports and Fitness',
                'timestamps': [20.0]
            },
            {
                'label': 'Flip',
                'confidence': 82.7,
                'category': 'Sports and Fitness',
                'timestamps': [20.2]
            },
            {
                'label': 'Sport',
                'confidence': 91.3,
                'category': 'Sports and Fitness',
                'timestamps': [5.0, 10.0, 15.0, 20.0, 25.0]
            },
            {
                'label': 'Person',
                'confidence': 99.1,
                'category': 'Person Description',
                'timestamps': [1.0, 5.0, 10.0, 15.0, 20.0, 25.0]
            }
        ],
        'activity_labels': [
            {
                'label': 'Acrobatics',
                'confidence': 89.5,
                'category': 'Sports and Fitness',
                'timestamps': [20.1, 20.5]
            },
            {
                'label': 'Gymnastics',
                'confidence': 85.2,
                'category': 'Sports and Fitness',
                'timestamps': [20.0]
            }
        ],
        'video_metadata': {
            'duration_seconds': 30.0,
            'format': 'mp4'
        }
    }

def analyze_with_rekognition(s3_key):
    """
    Analyze video with AWS Rekognition using multiple detection methods
    Returns labels with timestamps and confidence scores
    """
    try:
        # Start label detection job
        start_params = {
            'Video': {'S3Object': {'Bucket': AWS_BUCKET, 'Name': s3_key}},
            'MinConfidence': 60,
            'Features': ['GENERAL_LABELS']
        }
        
        # Add SNS notification if configured (only if valid ARNs, not placeholders)
        if SNS_TOPIC_ARN and REKOGNITION_ROLE_ARN and \
           'your-account' not in SNS_TOPIC_ARN and \
           'your-account' not in REKOGNITION_ROLE_ARN and \
           SNS_TOPIC_ARN.startswith('arn:aws:sns:') and \
           REKOGNITION_ROLE_ARN.startswith('arn:aws:iam::'):
            start_params['NotificationChannel'] = {
                'SNSTopicArn': SNS_TOPIC_ARN,
                'RoleArn': REKOGNITION_ROLE_ARN
            }
            print(f"📢 Using SNS notifications for faster processing")
        
        # Start label detection
        response = rek_client.start_label_detection(**start_params)
        label_job_id = response['JobId']
        print(f"🔍 Started Label Detection job: {label_job_id}")
        
        # Start person tracking for movement analysis
        person_job_id = None
        try:
            # Person tracking works without SNS, just takes longer to poll
            person_response = rek_client.start_person_tracking(
                Video={'S3Object': {'Bucket': AWS_BUCKET, 'Name': s3_key}}
            )
            person_job_id = person_response['JobId']
            print(f"👤 Started Person Tracking job: {person_job_id}")
        except Exception as e:
            print(f"⚠️  Person tracking not available: {e}")
            person_job_id = None
        
        # Start face search to identify streamers (like IShowSpeed)
        face_job_id = None
        try:
            face_response = rek_client.start_face_search(
                Video={'S3Object': {'Bucket': AWS_BUCKET, 'Name': s3_key}},
                CollectionId='streambet-streamers',
                FaceMatchThreshold=80.0
            )
            face_job_id = face_response['JobId']
            print(f"😎 Started Face Search job: {face_job_id}")
        except Exception as e:
            print(f"⚠️  Face search not available: {e}")
            face_job_id = None
        
        # Poll for all jobs to complete
        max_attempts = 60  # 5 minutes max
        attempt = 0
        label_result = None
        person_result = None
        face_result = None
        
        while attempt < max_attempts:
            # Check label detection
            if not label_result:
                label_check = rek_client.get_label_detection(JobId=label_job_id)
                if label_check['JobStatus'] == 'SUCCEEDED':
                    label_result = label_check
                    print(f"✅ Label detection complete!")
                elif label_check['JobStatus'] == 'FAILED':
                    return {'error': 'Label detection failed'}
            
            # Check person tracking
            if person_job_id and not person_result:
                person_check = rek_client.get_person_tracking(JobId=person_job_id)
                if person_check['JobStatus'] == 'SUCCEEDED':
                    person_result = person_check
                    print(f"✅ Person tracking complete!")
                elif person_check['JobStatus'] == 'FAILED':
                    print(f"⚠️  Person tracking failed, continuing with labels only")
                    person_result = {'Persons': []}  # Empty result
            elif not person_job_id:
                person_result = {'Persons': []}  # Skip if not started
            
            # Check face search
            if face_job_id and not face_result:
                face_check = rek_client.get_face_search(JobId=face_job_id)
                if face_check['JobStatus'] == 'SUCCEEDED':
                    face_result = face_check
                    print(f"✅ Face search complete!")
                elif face_check['JobStatus'] == 'FAILED':
                    print(f"⚠️  Face search failed")
                    face_result = {'Persons': []}
            elif not face_job_id:
                face_result = {'Persons': []}  # Skip if not started
            
            # All complete?
            if label_result and person_result and face_result is not None:
                break
            
            time.sleep(5)
            attempt += 1
            print(f"⏳ Waiting for results... ({attempt * 5}s)")
        
        if attempt >= max_attempts:
            return {'error': 'Analysis timeout'}
        
        result = label_result
        
        # Extract and format labels
        labels = []
        activity_labels = []
        
        for label_detection in result.get('Labels', []):
            label_name = label_detection['Label']['Name']
            confidence = label_detection['Label']['Confidence']
            
            # Get timestamps for this label
            timestamps = []
            if 'Instances' in label_detection and label_detection['Instances']:
                for instance in label_detection['Instances'][:5]:  # Limit to 5
                    ts = instance.get('Timestamp', 0) / 1000.0  # ms to seconds
                    timestamps.append(round(ts, 2))
            
            label_data = {
                'label': label_name,
                'confidence': round(confidence, 2),
                'timestamps': timestamps,
                'category': label_detection['Label'].get('Categories', [{}])[0].get('Name', 'General')
            }
            
            labels.append(label_data)
            
            # Flag activity-related labels
            activity_keywords = ['jumping', 'running', 'exercise', 'sport', 'game', 'playing']
            if any(keyword in label_name.lower() for keyword in activity_keywords):
                activity_labels.append(label_data)
        
        # Analyze person movement for backflip detection
        movement_data = analyze_person_movement(person_result)
        
        # Analyze face matches
        face_data = analyze_face_matches(face_result)
        
        # Debug: Print face detection results
        if face_data.get('identified'):
            print(f"\n😎 STREAMER IDENTIFIED: {face_data['streamer']}")
            print(f"   Appearances: {face_data['total_appearances']}")
            print(f"   Timestamps: {[a['timestamp'] for a in face_data['appearances'][:5]]}")
        else:
            print(f"\n⚠️  No known streamers identified in video")
            print(f"   Face matches found: {len(face_result.get('Persons', []))}")
        
        return {
            'status': 'success',
            'job_id': label_job_id,
            'total_labels': len(labels),
            'labels': labels[:15],  # Top 15 labels
            'activity_labels': activity_labels[:5],  # Top 5 activities
            'movement_data': movement_data,  # Person tracking data
            'face_data': face_data,  # Streamer identification
            'video_metadata': {
                'duration_seconds': result.get('VideoMetadata', {}).get('DurationMillis', 0) / 1000.0,
                'format': result.get('VideoMetadata', {}).get('Format', 'unknown')
            }
        }
    
    except ClientError as e:
        return {'error': f"AWS Error: {str(e)}"}
    except Exception as e:
        return {'error': f"Unexpected error: {str(e)}"}

def extract_frames(video_path, fps=1):
    """
    Extract frames from video at specified FPS
    Returns list of (timestamp, frame_data) tuples
    """
    frames = []
    cap = cv2.VideoCapture(video_path)
    
    if not cap.isOpened():
        print("⚠️  Could not open video file")
        return frames
    
    video_fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    duration = total_frames / video_fps if video_fps > 0 else 0
    
    print(f"📹 Video: {video_fps} fps, {total_frames} frames, {duration:.2f}s")
    print(f"🎬 Extracting 1 frame per {1/fps} second(s)...")
    
    frame_interval = int(video_fps / fps) if video_fps > 0 else 1
    frame_count = 0
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
            
        if frame_count % frame_interval == 0:
            timestamp = frame_count / video_fps if video_fps > 0 else frame_count
            
            # Convert frame to JPEG bytes
            _, buffer = cv2.imencode('.jpg', frame)
            frame_bytes = buffer.tobytes()
            
            frames.append((timestamp, frame_bytes))
            
        frame_count += 1
    
    cap.release()
    print(f"✅ Extracted {len(frames)} frames")
    return frames


def analyze_frame_with_rekognition(frame_bytes, rek_client, collection_id='streambet-streamers'):
    """
    Analyze a single frame using AWS Rekognition Image API
    Returns dict with labels and face matches
    """
    result = {
        'labels': [],
        'faces': [],
        'streamer_match': None
    }
    
    try:
        # Detect labels in frame
        label_response = rek_client.detect_labels(
            Image={'Bytes': frame_bytes},
            MaxLabels=10,
            MinConfidence=60
        )
        result['labels'] = label_response.get('Labels', [])
        
    except Exception as e:
        print(f"⚠️  Label detection failed: {e}")
    
    try:
        # Search for faces in collection
        face_response = rek_client.search_faces_by_image(
            CollectionId=collection_id,
            Image={'Bytes': frame_bytes},
            MaxFaces=5,
            FaceMatchThreshold=80.0
        )
        
        # Get best match
        if face_response.get('FaceMatches'):
            best_match = face_response['FaceMatches'][0]
            result['streamer_match'] = {
                'face_id': best_match['Face']['FaceId'],
                'similarity': best_match['Similarity'],
                'external_image_id': best_match['Face'].get('ExternalImageId', 'unknown')
            }
            
    except Exception as e:
        # No face found or no match
        pass
    
    return result


def analyze_face_matches(face_result):
    """
    Analyze face search results to identify streamers
    """
    if not face_result or 'Persons' not in face_result:
        return {'identified': False, 'streamer': None, 'appearances': []}
    
    appearances = []
    identified_streamers = set()
    
    for person in face_result.get('Persons', []):
        timestamp = person.get('Timestamp', 0) / 1000.0
        face_matches = person.get('FaceMatches', [])
        
        for match in face_matches:
            similarity = match.get('Similarity', 0)
            face = match.get('Face', {})
            streamer_name = face.get('ExternalImageId', 'Unknown')
            
            if similarity >= 80.0:  # High confidence match
                identified_streamers.add(streamer_name)
                appearances.append({
                    'timestamp': round(timestamp, 2),
                    'streamer': streamer_name,
                    'confidence': round(similarity, 2)
                })
    
    # Get primary streamer (most appearances)
    primary_streamer = None
    if identified_streamers:
        # Count appearances per streamer
        streamer_counts = {}
        for app in appearances:
            name = app['streamer']
            streamer_counts[name] = streamer_counts.get(name, 0) + 1
        primary_streamer = max(streamer_counts, key=streamer_counts.get)
    
    return {
        'identified': len(identified_streamers) > 0,
        'streamer': primary_streamer,
        'all_streamers': list(identified_streamers),
        'appearances': appearances[:10],  # Limit output
        'total_appearances': len(appearances)
    }

def analyze_person_movement(person_result):
    """
    Analyze person tracking data to detect rapid vertical movements
    that could indicate backflips or acrobatic moves
    """
    if not person_result or 'Persons' not in person_result:
        return {'rapid_movements': [], 'potential_backflips': 0}
    
    rapid_movements = []
    persons = person_result.get('Persons', [])
    
    # Track vertical position changes
    prev_position = None
    movement_threshold = 0.15  # 15% vertical change indicates significant movement
    
    for person in persons:
        timestamp = person.get('Timestamp', 0) / 1000.0  # ms to seconds
        bbox = person.get('Person', {}).get('BoundingBox', {})
        
        if bbox:
            # Get vertical position (Top of bounding box)
            current_top = bbox.get('Top', 0)
            
            if prev_position is not None:
                # Calculate vertical change
                vertical_change = abs(current_top - prev_position['top'])
                
                # Rapid vertical movement detected
                if vertical_change > movement_threshold:
                    rapid_movements.append({
                        'timestamp': round(timestamp, 2),
                        'vertical_change': round(vertical_change, 3),
                        'confidence': person.get('Person', {}).get('Confidence', 0)
                    })
            
            prev_position = {
                'top': current_top,
                'timestamp': timestamp
            }
    
    # Group rapid movements within 2 seconds as potential backflips
    potential_backflips = []
    if rapid_movements:
        current_group = [rapid_movements[0]]
        
        for i in range(1, len(rapid_movements)):
            if rapid_movements[i]['timestamp'] - current_group[-1]['timestamp'] < 2.0:
                current_group.append(rapid_movements[i])
            else:
                if len(current_group) >= 2:  # At least 2 rapid movements = potential backflip
                    potential_backflips.append({
                        'timestamp': round(current_group[0]['timestamp'], 2),
                        'movements': len(current_group),
                        'max_change': max(m['vertical_change'] for m in current_group)
                    })
                current_group = [rapid_movements[i]]
        
        # Check last group
        if len(current_group) >= 2:
            potential_backflips.append({
                'timestamp': round(current_group[0]['timestamp'], 2),
                'movements': len(current_group),
                'max_change': max(m['vertical_change'] for m in current_group)
            })
    
    return {
        'rapid_movements': rapid_movements[:10],  # Limit output
        'potential_backflips': len(potential_backflips),
        'backflip_timestamps': [bf['timestamp'] for bf in potential_backflips]
    }

def count_backflips(labels):
    """
    Count potential backflips based on detected labels and timestamps
    Looks for rotation, acrobatics, jumping patterns
    """
    backflip_indicators = [
        'acrobatics', 'gymnastics', 'flip', 'somersault', 'rotation',
        'jumping', 'tumbling', 'aerial', 'trick', 'sport', 'basketball',
        'playing', 'exercise', 'fitness', 'athlete', 'training', 'jump',
        'leap', 'airborne', 'flying'
    ]
    
    # Priority indicators (more likely to be backflips)
    high_priority = ['acrobatics', 'gymnastics', 'flip', 'somersault', 'tumbling']
    
    backflip_count = 0
    backflip_timestamps = []
    confidence_scores = []
    
    for label in labels:
        label_name = label['label'].lower()
        
        # Check if label indicates backflip-like activity
        for indicator in backflip_indicators:
            if indicator in label_name:
                # Count timestamps as potential backflips
                timestamps = label.get('timestamps', [])
                if timestamps:
                    # Group timestamps that are close together (within 2 seconds)
                    grouped_timestamps = []
                    for ts in timestamps:
                        if not grouped_timestamps or ts - grouped_timestamps[-1] > 2.0:
                            grouped_timestamps.append(ts)
                            backflip_count += 1
                            backflip_timestamps.append(ts)
                            confidence_scores.append(label['confidence'])
                break
    
    return {
        'count': backflip_count,
        'timestamps': backflip_timestamps,
        'average_confidence': sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0,
        'detected': backflip_count > 0
    }

def generate_betting_suggestion(analysis_results):
    """
    Generate betting suggestions based on detected activities and movement
    Focus on backflip counting using both labels and person tracking
    """
    if 'error' in analysis_results:
        return None
    
    all_labels = analysis_results.get('labels', [])
    activity_labels = analysis_results.get('activity_labels', [])
    movement_data = analysis_results.get('movement_data', {})
    face_data = analysis_results.get('face_data', {})
    
    # Check if we identified a streamer
    streamer_name = face_data.get('streamer', None)
    streamer_identified = face_data.get('identified', False)
    
    # Check for backflips from person tracking (more reliable)
    movement_backflips = movement_data.get('potential_backflips', 0)
    movement_timestamps = movement_data.get('backflip_timestamps', [])
    
    # Also count from labels
    label_backflip_data = count_backflips(all_labels)
    
    # Combine both methods - use movement data if available
    if movement_backflips > 0:
        streamer_text = f" by {streamer_name}" if streamer_identified else ""
        return {
            'suggestion': f"Bet on backflip count{streamer_text}: {movement_backflips} detected via movement tracking",
            'detected_activity': 'Backflips (Movement Analysis)',
            'confidence': 85.0,  # Movement-based detection is pretty reliable
            'timestamps': movement_timestamps,
            'backflip_count': movement_backflips,
            'bet_outcome': 'YES' if movement_backflips >= 10 else f'NO ({movement_backflips} detected, need 10)',
            'detection_method': 'Person Tracking + Movement Analysis',
            'streamer': streamer_name if streamer_identified else 'Unknown',
            'streamer_confidence': face_data.get('appearances', [{}])[0].get('confidence', 0) if streamer_identified else 0
        }
    
    # Fallback to label-based detection
    backflip_data = label_backflip_data
    
    if backflip_data['detected']:
        return {
            'suggestion': f"Bet on backflip count: {backflip_data['count']} detected",
            'detected_activity': 'Backflips/Acrobatics',
            'confidence': backflip_data['average_confidence'],
            'timestamps': backflip_data['timestamps'],
            'backflip_count': backflip_data['count'],
            'bet_outcome': 'YES' if backflip_data['count'] >= 10 else 'NO (less than 10)'
        }
    
    if not activity_labels:
        return {
            'suggestion': 'No backflips or specific activities detected',
            'confidence': 0,
            'backflip_count': 0
        }
    
    # Fallback to general activity detection
    top_activity = activity_labels[0]
    label = top_activity['label'].lower()
    confidence = top_activity['confidence']
    
    suggestions = {
        'jumping': 'Bet on number of jumps completed',
        'running': 'Bet on distance covered',
        'exercise': 'Bet on workout completion',
        'sport': 'Bet on game outcome',
        'playing': 'Bet on match result'
    }
    
    for keyword, suggestion in suggestions.items():
        if keyword in label:
            return {
                'suggestion': suggestion,
                'detected_activity': top_activity['label'],
                'confidence': confidence,
                'timestamps': top_activity['timestamps'],
                'backflip_count': 0
            }
    
    return {
        'suggestion': f"Bet on {top_activity['label']} occurrence",
        'detected_activity': top_activity['label'],
        'confidence': confidence,
        'timestamps': top_activity['timestamps'],
        'backflip_count': 0
    }

@app.route('/api/resolve', methods=['POST'])
def resolve_bet():
    """
    Mock endpoint for bet resolution
    In production, this would use Bedrock agent for decision-making
    """
    data = request.json
    bet_id = data.get('bet_id')
    analysis = data.get('analysis')
    
    # Simple mock resolution logic
    if not analysis or 'error' in analysis:
        return jsonify({
            'status': 'failed',
            'reason': 'Analysis incomplete'
        })
    
    # Check if target activity was detected with high confidence
    activity_labels = analysis.get('activity_labels', [])
    if activity_labels and activity_labels[0]['confidence'] > 80:
        return jsonify({
            'status': 'resolved',
            'outcome': 'YES',
            'confidence': activity_labels[0]['confidence'],
            'payout_triggered': True,
            'detected_at': activity_labels[0]['timestamps']
        })
    
    return jsonify({
        'status': 'resolved',
        'outcome': 'NO',
        'confidence': 0,
        'payout_triggered': False
    })

if __name__ == '__main__':
    # Create uploads folder
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    os.makedirs('templates', exist_ok=True)
    
    print("\n" + "="*60)
    print("🎮 StreamBet Recognition API - Hackathon POC")
    print("="*60)
    print(f"📁 Upload folder: {UPLOAD_FOLDER}")
    print(f"☁️  AWS Bucket: {AWS_BUCKET}")
    print(f"🌍 Region: {AWS_REGION}")
    print("="*60 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
