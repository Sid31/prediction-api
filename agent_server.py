#!/usr/bin/env python3
"""
AWS Bedrock AgentCore Compatible Video Detection Agent
Monitors videos and sends real-time notifications to your backend
"""

import os
import time
import json
import cv2
import requests
from flask import Flask, request, jsonify, Response
from dotenv import load_dotenv
import boto3
from threading import Thread
from datetime import datetime

load_dotenv()

# Configuration
AWS_REGION = os.getenv('AWS_REGION', 'us-east-1')
WEBHOOK_URL = os.getenv('WEBHOOK_URL', 'http://localhost:8000/api/events/detection')
COLLECTION_ID = os.getenv('COLLECTION_ID', 'streambet-streamers')

# Initialize Flask app
app = Flask(__name__)

# Initialize AWS Rekognition
rek_client = boto3.client('rekognition', region_name=AWS_REGION)

# Health status
health_status = {
    'status': 'Healthy',
    'time_of_last_update': time.time(),
    'active_tasks': 0
}


def extract_and_analyze_frames(video_url, video_id, labels, confidence_threshold, fps_sample):
    """
    Download video, extract frames, detect labels, and send notifications
    """
    global health_status
    
    try:
        health_status['status'] = 'HealthyBusy'
        health_status['active_tasks'] += 1
        
        # Download video
        print(f"📥 Downloading video: {video_url}")
        response = requests.get(video_url, stream=True)
        temp_video = f"/tmp/{video_id}.mp4"
        
        with open(temp_video, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        print(f"✅ Video downloaded to {temp_video}")
        
        # Open video
        cap = cv2.VideoCapture(temp_video)
        if not cap.isOpened():
            raise Exception("Could not open video")
        
        video_fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = total_frames / video_fps if video_fps > 0 else 0
        
        print(f"📹 Video: {video_fps} fps, {total_frames} frames, {duration:.2f}s")
        print(f"🎬 Analyzing {fps_sample} frames per second...")
        
        frame_interval = int(video_fps / fps_sample) if video_fps > 0 else 1
        frame_count = 0
        detections = []
        last_notification_time = {}  # Cooldown per label
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            if frame_count % frame_interval == 0:
                timestamp = frame_count / video_fps if video_fps > 0 else frame_count
                
                # Convert frame to JPEG
                _, buffer = cv2.imencode('.jpg', frame)
                frame_bytes = buffer.tobytes()
                
                # Detect labels with Rekognition
                try:
                    response = rek_client.detect_labels(
                        Image={'Bytes': frame_bytes},
                        MaxLabels=10,
                        MinConfidence=confidence_threshold * 100
                    )
                    
                    detected_labels = response.get('Labels', [])
                    
                    # Check for target labels
                    for label in detected_labels:
                        label_name = label['Name'].lower()
                        label_confidence = label['Confidence'] / 100
                        
                        # If this label matches our filter
                        if label_name in [l.lower() for l in labels]:
                            # Check cooldown (don't spam same label)
                            last_time = last_notification_time.get(label_name, 0)
                            if time.time() - last_time > 5.0:  # 5 second cooldown
                                
                                # Get bounding boxes if available
                                bbox = None
                                if label.get('Instances'):
                                    instance = label['Instances'][0]
                                    box = instance.get('BoundingBox', {})
                                    bbox = [
                                        box.get('Left', 0),
                                        box.get('Top', 0),
                                        box.get('Width', 0),
                                        box.get('Height', 0)
                                    ]
                                
                                # Send webhook notification
                                event_data = {
                                    'event': 'detection',
                                    'video_id': video_id,
                                    'frame_id': frame_count,
                                    'timestamp': timestamp,
                                    'label': label_name,
                                    'confidence': label_confidence,
                                    'bbox': bbox,
                                    'ts': time.time()
                                }
                                
                                print(f"🚨 DETECTION: {label_name} at {timestamp:.2f}s ({label_confidence*100:.1f}%)")
                                send_webhook(event_data)
                                
                                detections.append(event_data)
                                last_notification_time[label_name] = time.time()
                
                except Exception as e:
                    print(f"⚠️  Frame analysis error: {e}")
            
            frame_count += 1
        
        cap.release()
        
        # Clean up
        os.remove(temp_video)
        
        print(f"✅ Analysis complete! Found {len(detections)} detections")
        
        return {
            'status': 'success',
            'video_id': video_id,
            'total_frames': frame_count,
            'frames_analyzed': frame_count // frame_interval,
            'detections_count': len(detections),
            'detections': detections
        }
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return {
            'status': 'error',
            'error': str(e),
            'video_id': video_id
        }
    finally:
        health_status['active_tasks'] -= 1
        if health_status['active_tasks'] == 0:
            health_status['status'] = 'Healthy'
        health_status['time_of_last_update'] = time.time()


def send_webhook(data):
    """Send detection event to webhook"""
    try:
        response = requests.post(
            WEBHOOK_URL,
            json=data,
            headers={'Content-Type': 'application/json'},
            timeout=5
        )
        if response.status_code == 200:
            print(f"✅ Webhook sent: {data['label']} at {data['timestamp']:.2f}s")
        else:
            print(f"⚠️  Webhook failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Webhook error: {e}")


@app.route('/ping', methods=['GET'])
def ping():
    """
    AWS Bedrock AgentCore health check endpoint
    Returns: Healthy | HealthyBusy
    """
    return jsonify({
        'status': health_status['status'],
        'time_of_last_update': health_status['time_of_last_update'],
        'active_tasks': health_status['active_tasks']
    })


@app.route('/invocations', methods=['POST'])
def invocations():
    """
    AWS Bedrock AgentCore invocation endpoint
    Accepts video analysis requests and returns results
    """
    try:
        data = request.json
        
        # Extract parameters
        video_url = data.get('video_url')
        video_id = data.get('video_id', f"video_{int(time.time())}")
        labels = data.get('labels', ['person', 'fighting', 'sport'])
        confidence = data.get('confidence', 0.6)
        fps_sample = data.get('fps_sample', 1)
        
        if not video_url:
            return jsonify({'error': 'video_url is required'}), 400
        
        print(f"\n{'='*60}")
        print(f"🎬 NEW VIDEO ANALYSIS REQUEST")
        print(f"{'='*60}")
        print(f"Video ID: {video_id}")
        print(f"Video URL: {video_url}")
        print(f"Labels: {labels}")
        print(f"Confidence: {confidence}")
        print(f"FPS Sample: {fps_sample}")
        print(f"{'='*60}\n")
        
        # Process video (blocking mode for now)
        result = extract_and_analyze_frames(
            video_url=video_url,
            video_id=video_id,
            labels=labels,
            confidence_threshold=confidence,
            fps_sample=fps_sample
        )
        
        return jsonify(result)
        
    except Exception as e:
        print(f"❌ Invocation error: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/invocations/stream', methods=['POST'])
def invocations_stream():
    """
    Streaming version using Server-Sent Events (SSE)
    Returns incremental updates as video is analyzed
    """
    def generate():
        try:
            data = request.json
            video_url = data.get('video_url')
            video_id = data.get('video_id', f"video_{int(time.time())}")
            labels = data.get('labels', ['person', 'fighting', 'sport'])
            confidence = data.get('confidence', 0.6)
            fps_sample = data.get('fps_sample', 1)
            
            yield f"data: {json.dumps({'status': 'started', 'video_id': video_id})}\n\n"
            
            # Download video
            response = requests.get(video_url, stream=True)
            temp_video = f"/tmp/{video_id}.mp4"
            with open(temp_video, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            yield f"data: {json.dumps({'status': 'downloading_complete'})}\n\n"
            
            # Process frames
            cap = cv2.VideoCapture(temp_video)
            video_fps = cap.get(cv2.CAP_PROP_FPS)
            frame_interval = int(video_fps / fps_sample)
            frame_count = 0
            
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                if frame_count % frame_interval == 0:
                    progress = (frame_count / int(cap.get(cv2.CAP_PROP_FRAME_COUNT))) * 100
                    yield f"data: {json.dumps({'status': 'processing', 'progress': progress})}\n\n"
                
                frame_count += 1
            
            cap.release()
            os.remove(temp_video)
            
            yield f"data: {json.dumps({'status': 'complete', 'video_id': video_id})}\n\n"
            
        except Exception as e:
            yield f"data: {json.dumps({'status': 'error', 'error': str(e)})}\n\n"
    
    return Response(generate(), mimetype='text/event-stream')


@app.route('/', methods=['GET'])
def root():
    """Root endpoint"""
    return jsonify({
        'service': 'StreamBet Video Detection Agent',
        'version': '1.0.0',
        'endpoints': {
            'health': '/ping',
            'invoke': '/invocations',
            'stream': '/invocations/stream'
        }
    })


if __name__ == '__main__':
    print("\n" + "="*60)
    print("🎮 StreamBet Video Detection Agent")
    print("="*60)
    print(f"📍 Listening on: 0.0.0.0:8080")
    print(f"🔗 Webhook URL: {WEBHOOK_URL}")
    print(f"☁️  AWS Region: {AWS_REGION}")
    print(f"👤 Collection ID: {COLLECTION_ID}")
    print("="*60 + "\n")
    
    # Run Flask app on port 8080 (AWS Bedrock AgentCore standard)
    app.run(host='0.0.0.0', port=8080, debug=False)
