"""
StreamBet POC - AI-Powered Video Recognition for Live Betting
Hackathon Demo: AWS Rekognition + Simple Betting Interface
"""

import os
import json
import boto3
import cv2
import time
import sys
import io
import re
from flask import Flask, render_template, request, jsonify, Response, send_from_directory, stream_with_context
from flask_cors import CORS
from werkzeug.utils import secure_filename
from datetime import datetime
import traceback
from concurrent.futures import ThreadPoolExecutor, as_completed
from io import BytesIO
from PIL import Image
from moviepy.editor import VideoFileClip
import tempfile
import base64
import requests
from elevenlabs import ElevenLabs, VoiceSettings
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
CORS(app)
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10MB max (recommended < 1 min video)

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
    bedrock_client = boto3.client('bedrock-runtime', region_name='us-east-1')
    sagemaker_runtime = boto3.client('sagemaker-runtime', region_name='ap-southeast-2')
    print("✅ AWS clients initialized successfully")
    print("🤖 Bedrock AI available - AI commentary enabled")
    print("🎤 SageMaker Runtime ready for Whisper ASR")
except Exception as e:
    print(f"⚠️  AWS client initialization failed: {e}")
    print("💡 Set AWS credentials: export AWS_ACCESS_KEY_ID=xxx AWS_SECRET_ACCESS_KEY=xxx")
    bedrock_client = None
    sagemaker_runtime = None

# SageMaker Whisper Configuration
WHISPER_ENDPOINT = os.getenv('WHISPER_ENDPOINT_NAME', None)  # Set in .env if you have a deployed endpoint
WHISPER_MODEL_ARN = "arn:aws:sagemaker:ap-southeast-2:aws:hub-content/SageMakerPublicHub/Model/huggingface-asr-whisper-large-v3-turbo/1.1.12"

if WHISPER_ENDPOINT:
    print(f"🎙️ Whisper ASR endpoint configured: {WHISPER_ENDPOINT}")
    print("🎙️ Audio analysis enabled for enhanced commentary")
else:
    print("💡 Set WHISPER_ENDPOINT_NAME in .env to enable audio analysis")
    print(f"📋 Model ARN: {WHISPER_MODEL_ARN}")

# ElevenLabs Configuration
ELEVENLABS_API_KEY = os.getenv('ELEVENLABS_API_KEY', None)
ELEVENLABS_VOICE_ID = os.getenv('ELEVENLABS_VOICE_ID', 'pNInz6obpgDQGcFmaJgB')  # Default: Adam (sports announcer)

if ELEVENLABS_API_KEY:
    try:
        elevenlabs_client = ElevenLabs(api_key=ELEVENLABS_API_KEY)
        print("🎙️ ElevenLabs TTS initialized - Voice commentary enabled!")
        print(f"🗣️ Using voice ID: {ELEVENLABS_VOICE_ID}")
    except Exception as e:
        print(f"⚠️ ElevenLabs initialization failed: {e}")
        elevenlabs_client = None
else:
    print("💡 Set ELEVENLABS_API_KEY in .env to enable voice commentary")
    elevenlabs_client = None

ALLOWED_EXTENSIONS = {'mp4', 'mov', 'avi'}
UPLOAD_FOLDER = 'uploads'
AUDIO_FOLDER = 'audio_commentary'

# Create audio folder if it doesn't exist
if not os.path.exists(AUDIO_FOLDER):
    os.makedirs(AUDIO_FOLDER)

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
    """Serve the main demo page"""
    return render_template('backflip_counter.html')

@app.route('/discover')
def discover():
    """Serve the label discovery page"""
    return render_template('label_discovery.html')

@app.route('/custom')
def custom():
    """Serve the custom AI detector page"""
    return render_template('custom_detector.html')

@app.route('/smart')
def smart():
    """Serve the smart detector with chatbot configurator"""
    return render_template('smart_detector.html')

@app.route('/widget')
def widget():
    """Serve the embeddable counter widget"""
    return render_template('counter_widget.html')

@app.route('/')
@app.route('/counter')
def counter():
    """Serve the simple counter (backflips or roller coasters) - Root path"""
    return render_template('simple_counter.html')

@app.route('/test-stream')
def test_stream():
    """Test page for debugging EventSource"""
    return render_template('test_stream.html')

@app.route('/api/add-face', methods=['POST'])
def add_face():
    """Add a face to the recognition collection"""
    try:
        person_name = request.form.get('person_name', 'unknown')
        image_file = request.files.get('image')
        
        if not image_file:
            return jsonify({'success': False, 'error': 'No image provided'}), 400
        
        image_bytes = image_file.read()
        
        # Create collection if it doesn't exist
        try:
            rek_client.create_collection(CollectionId='streambet-faces')
            print("✅ Created face collection: streambet-faces")
        except rek_client.exceptions.ResourceAlreadyExistsException:
            print("✅ Face collection already exists")
        
        # Add face to collection
        response = rek_client.index_faces(
            CollectionId='streambet-faces',
            Image={'Bytes': image_bytes},
            ExternalImageId=person_name,
            DetectionAttributes=['ALL']
        )
        
        faces_indexed = len(response['FaceRecords'])
        
        return jsonify({
            'success': True,
            'person_name': person_name,
            'faces_indexed': faces_indexed,
            'message': f"Added {faces_indexed} face(s) for {person_name}"
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/list-faces')
def list_faces():
    """List all faces in the collection"""
    try:
        response = rek_client.list_faces(
            CollectionId='streambet-faces',
            MaxResults=100
        )
        
        faces = []
        for face in response.get('Faces', []):
            faces.append({
                'face_id': face['FaceId'],
                'person_name': face.get('ExternalImageId', 'unknown'),
                'confidence': face.get('Confidence', 0)
            })
        
        return jsonify({
            'success': True,
            'count': len(faces),
            'faces': faces
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/analyze-single-frame', methods=['POST'])
def analyze_single_frame():
    """Analyze a single frame and return all labels"""
    try:
        frame_file = request.files['frame']
        frame_bytes = frame_file.read()
        
        # Analyze with Rekognition
        response = rek_client.detect_labels(
            Image={'Bytes': frame_bytes},
            MaxLabels=20,  # Get more labels for discovery
            MinConfidence=60  # Lower threshold to see more options
        )
        
        return jsonify({
            'success': True,
            'labels': response.get('Labels', [])
        })
        
    except Exception as e:
        print(f"Error analyzing frame: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/analyze-with-ai', methods=['POST'])
def analyze_with_ai():
    """Analyze frame with custom AI query using Bedrock (Claude 3 Vision)"""
    try:
        frame_file = request.files['frame']
        frame_bytes = frame_file.read()
        query = request.form.get('query', 'Describe what you see')
        
        if not bedrock_client:
            # Fallback: Use Rekognition labels
            response = rek_client.detect_labels(
                Image={'Bytes': frame_bytes},
                MaxLabels=10,
                MinConfidence=70
            )
            labels = [label['Name'] for label in response.get('Labels', [])]
            answer = f"Rekognition detected: {', '.join(labels[:5])}"
            
            return jsonify({
                'success': True,
                'answer': answer,
                'method': 'rekognition_fallback'
            })
        
        # Use Bedrock Claude 3 Vision
        import base64
        frame_b64 = base64.b64encode(frame_bytes).decode('utf-8')
        
        # Call Bedrock
        bedrock_response = bedrock_client.invoke_model(
            modelId='anthropic.claude-3-sonnet-20240229-v1:0',
            body=json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 200,
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image",
                                "source": {
                                    "type": "base64",
                                    "media_type": "image/jpeg",
                                    "data": frame_b64
                                }
                            },
                            {
                                "type": "text",
                                "text": f"{query}\n\nAnswer concisely and directly."
                            }
                        ]
                    }
                ]
            })
        )
        
        # Parse response
        response_body = json.loads(bedrock_response['body'].read())
        answer = response_body['content'][0]['text'].strip()
        
        print(f"🤖 AI Query: {query}")
        print(f"💡 AI Answer: {answer}")
        
        return jsonify({
            'success': True,
            'answer': answer,
            'method': 'bedrock_claude3'
        })
        
    except Exception as e:
        print(f"❌ Error in AI analysis: {e}")
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/configure-detection', methods=['POST'])
def configure_detection():
    """AI chatbot to configure detection based on natural language intent"""
    try:
        data = request.json
        intent = data.get('intent', '')
        
        print(f"🎯 User Intent: {intent}")
        
        # Use AI to understand intent and generate config
        if not bedrock_client:
            # Fallback: Basic pattern matching
            config = generate_config_fallback(intent)
        else:
            # Use Bedrock to understand intent
            config = generate_config_with_ai(intent)
        
        # Generate response message
        response_message = f"""
✅ Got it! I've configured detection for: <strong>{config['target']}</strong>
<br><br>
📋 <strong>Detection Query:</strong> {config['query']}
<br>
🎯 <strong>Mode:</strong> {config['mode']}
<br><br>
Click "Start Detection" to begin analyzing your video!
        """
        
        print(f"✅ Generated Config: {config}")
        
        return jsonify({
            'success': True,
            'response': response_message,
            'config': config
        })
        
    except Exception as e:
        print(f"❌ Error configuring detection: {e}")
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

def generate_config_with_ai(intent):
    """Use AI to understand intent and generate detection config"""
    try:
        # Ask Claude to generate a detection config
        prompt = f"""The user wants to detect something in a video. Their request: "{intent}"

Generate a JSON detection configuration with these fields:
- target: Short name for what to detect (e.g., "Backflips", "Roller Coasters", "Game Kills")
- query: The exact question to ask about each video frame (e.g., "Is anyone doing a backflip?")
- mode: Either "Detection" or "Counting" (use Counting if user asks "how many")

Examples:
User: "detect ishowspeed backflip"
Output: {{"target": "IShowSpeed Backflips", "query": "Is anyone doing a backflip or acrobatic move?", "mode": "Detection"}}

User: "count roller coasters"
Output: {{"target": "Roller Coasters", "query": "Is a roller coaster visible in this frame?", "mode": "Counting"}}

User: "video game kills"
Output: {{"target": "Game Kills", "query": "Is there a kill notification or elimination indicator visible?", "mode": "Counting"}}

Now generate config for: "{intent}"
Return ONLY the JSON, no other text."""

        response = bedrock_client.invoke_model(
            modelId='anthropic.claude-3-sonnet-20240229-v1:0',
            body=json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 300,
                "messages": [{
                    "role": "user",
                    "content": prompt
                }]
            })
        )
        
        response_body = json.loads(response['body'].read())
        ai_output = response_body['content'][0]['text'].strip()
        
        # Extract JSON from response
        import re
        json_match = re.search(r'\{.*\}', ai_output, re.DOTALL)
        if json_match:
            config = json.loads(json_match.group())
            return config
        else:
            return generate_config_fallback(intent)
            
    except Exception as e:
        print(f"⚠️ AI config failed, using fallback: {e}")
        return generate_config_fallback(intent)

def generate_config_fallback(intent):
    """Fallback config generation using pattern matching"""
    intent_lower = intent.lower()
    
    # Detect counting vs detection
    is_counting = any(word in intent_lower for word in ['count', 'how many', 'number of', 'total'])
    mode = "Counting" if is_counting else "Detection"
    
    # Pattern matching for common requests
    if 'backflip' in intent_lower or 'flip' in intent_lower:
        return {
            'target': 'Backflips',
            'query': 'Is anyone doing a backflip or acrobatic flip?',
            'mode': mode
        }
    elif 'roller coaster' in intent_lower or 'rollercoaster' in intent_lower:
        return {
            'target': 'Roller Coasters',
            'query': 'Is a roller coaster visible in this frame?',
            'mode': mode
        }
    elif 'kill' in intent_lower or 'game' in intent_lower or 'gameplay' in intent_lower:
        return {
            'target': 'Game Kills',
            'query': 'Is there a kill notification, elimination indicator, or death marker visible?',
            'mode': mode
        }
    elif 'dance' in intent_lower or 'dancing' in intent_lower:
        return {
            'target': 'Dancing',
            'query': 'Is anyone dancing or moving rhythmically to music?',
            'mode': mode
        }
    elif 'red' in intent_lower and ('shirt' in intent_lower or 'clothing' in intent_lower):
        return {
            'target': 'Red Shirts',
            'query': 'How many people are wearing red shirts or clothing?',
            'mode': 'Counting'
        }
    elif 'people' in intent_lower or 'person' in intent_lower:
        return {
            'target': 'People Count',
            'query': 'How many people are visible in this frame?',
            'mode': 'Counting'
        }
    else:
        # Generic fallback
        return {
            'target': intent.title(),
            'query': f'Is there any {intent} visible in this frame?',
            'mode': mode
        }

def extract_audio_segment(video_path, start_time, duration=5):
    """Extract audio segment from video for transcription"""
    try:
        with VideoFileClip(video_path) as video:
            # Extract audio segment around the timestamp
            audio_start = max(0, start_time - duration/2)
            audio_end = min(video.duration, start_time + duration/2)
            
            audio_clip = video.subclip(audio_start, audio_end).audio
            if audio_clip is None:
                return None
            
            # Save to temporary file
            temp_audio = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
            audio_clip.write_audiofile(temp_audio.name, fps=16000, verbose=False, logger=None)
            
            return temp_audio.name
    except Exception as e:
        print(f"⚠️ Audio extraction failed: {e}")
        return None

def transcribe_audio_segment(audio_path):
    """Transcribe audio using SageMaker Whisper endpoint"""
    if not sagemaker_runtime or not WHISPER_ENDPOINT or not audio_path:
        # Clean up temp file
        if audio_path and os.path.exists(audio_path):
            os.unlink(audio_path)
        return None
    
    try:
        # Read audio file and encode to base64
        with open(audio_path, 'rb') as audio_file:
            audio_bytes = audio_file.read()
        
        # Prepare payload for SageMaker
        payload = {
            "inputs": base64.b64encode(audio_bytes).decode('utf-8'),
            "parameters": {
                "return_timestamps": False,
                "language": None  # Auto-detect language
            }
        }
        
        # Invoke SageMaker endpoint
        response = sagemaker_runtime.invoke_endpoint(
            EndpointName=WHISPER_ENDPOINT,
            ContentType='application/json',
            Body=json.dumps(payload)
        )
        
        # Parse response
        result = json.loads(response['Body'].read().decode('utf-8'))
        transcription = result.get('text', '').strip()
        
        # Clean up temp file
        if os.path.exists(audio_path):
            os.unlink(audio_path)
        
        return transcription if transcription else None
        
    except Exception as e:
        print(f"⚠️ SageMaker transcription failed: {e}")
        # Clean up temp file on error
        if audio_path and os.path.exists(audio_path):
            os.unlink(audio_path)
        return None

def generate_commentary(labels_text, celebrities, answer, timestamp, query, frame_context=None, audio_text=None):
    """Generate live sports-style commentary for what's happening"""
    import time
    
    try:
        celebrity_name = celebrities[0].split('(')[0].strip() if celebrities else "the athlete"
        
        # Short natural sports commentary prompt
        if "backflip" in query.lower() or "jump" in query.lower():
            prompt = f"""Sports commentator. Describe {celebrity_name}'s action in ONE short sentence (8-12 words max).

Scene: {labels_text[:200]}
Action: {answer}

Style - Keep it natural and brief:
- "Nice flip - good rotation there"
- "{celebrity_name} launches into the backflip"
- "Up he goes with the acrobatic move"
- "There's the flip attempt"
- "Perfect form on that rotation"

One short sentence only:"""
        else:
            prompt = f"""Sports commentary. Describe this in ONE brief sentence (8-12 words): {labels_text[:200]}

Be natural and concise:"""
        
        print(f"🤖 Generating commentary with prompt length: {len(prompt)}")
        
        # Retry logic with exponential backoff for rate limiting
        max_retries = 3
        base_delay = 1
        
        for attempt in range(max_retries):
            try:
                response = bedrock_client.invoke_model(
                    modelId='amazon.titan-text-express-v1',
                    body=json.dumps({
                        "inputText": prompt,
                        "textGenerationConfig": {
                            "maxTokenCount": 50,  # Short commentary (8-12 words)
                            "temperature": 0.7,  # More creative
                            "topP": 0.9,  # More diverse
                            "stopSequences": [".", "!", "?"]  # Stop at sentence end
                        }
                    })
                )
                
                response_body = json.loads(response['body'].read())
                commentary = response_body.get('results', [{}])[0].get('outputText', '').strip()
                
                if commentary:
                    print(f"✅ Commentary generated: {commentary[:50]}...")
                
                return commentary
                
            except Exception as api_error:
                error_str = str(api_error)
                
                # Check if it's a rate limit error
                if 'Too many requests' in error_str or 'ThrottlingException' in error_str:
                    if attempt < max_retries - 1:
                        delay = base_delay * (2 ** attempt)  # Exponential backoff: 1s, 2s, 4s
                        print(f"⏳ Rate limited, waiting {delay}s before retry {attempt + 1}/{max_retries}...")
                        time.sleep(delay)
                        continue
                    else:
                        print(f"❌ Max retries reached, skipping commentary")
                        return None
                else:
                    # Other error, don't retry
                    print(f"⚠️ Commentary API error: {api_error}")
                    return None
        
        return None
        
    except Exception as e:
        print(f"⚠️ Commentary generation failed: {e}")
        return None

def text_to_speech(text, timestamp):
    """Convert commentary text to speech using ElevenLabs"""
    if not elevenlabs_client or not text:
        print(f"⚠️ Voice disabled: client={elevenlabs_client is not None}, text={bool(text)}")
        return None
    
    try:
        print(f"🎤 Converting to speech: {text[:50]}...")
        
        # Generate audio using ElevenLabs (simplified - no signal on macOS)
        audio_generator = elevenlabs_client.text_to_speech.convert(
            voice_id=ELEVENLABS_VOICE_ID,
            optimize_streaming_latency="0",
            output_format="mp3_44100_128",
            text=text,
            model_id="eleven_turbo_v2_5",
            voice_settings=VoiceSettings(
                stability=0.5,
                similarity_boost=0.75,
                style=0.5,
                use_speaker_boost=True
            )
        )
        
        # Save audio to file
        audio_filename = f"commentary_{int(timestamp*1000)}.mp3"
        audio_path = os.path.join(AUDIO_FOLDER, audio_filename)
        
        # Write audio bytes to file
        with open(audio_path, 'wb') as audio_file:
            for chunk in audio_generator:
                audio_file.write(chunk)
        
        print(f"🔊 Voice audio saved: {audio_filename}")
        return f"/audio/{audio_filename}"
        
    except Exception as e:
        print(f"⚠️ Text-to-speech failed: {e}")
        import traceback
        traceback.print_exc()
        return None

def fallback_label_matching(labels_data, query):
    """Fallback label matching when AI is not available"""
    count = 0
    answer = "No"
    
    if 'backflip' in query.lower() or 'flip' in query.lower() or 'acrobatic' in query.lower() or 'ishowspeed' in query.lower():
        # Selective action detection - only clear action keywords
        ACTION_keywords = ['jump', 'jumping', 'flip', 'flipping', 'diving', 'acrobatic', 'gymnastics', 'floating', 'airborne', 'midair', 'flying']
        NOT_ENOUGH_keywords = ['fighting', 'sport', 'dancing', 'activity', 'exercise', 'playing', 'fun']
        person_keywords = ['person', 'human', 'people']
        
        has_person = False
        has_clear_action = False
        has_weak_activity = False
        detected_labels = []
        action_count = 0
        
        print(f"🔍 Selective backflip detection - only clear actions count...")
        
        for label in labels_data:
            label_lower = label['name'].lower()
            instances = label['instances'] if label['instances'] > 0 else 0
            
            # Check for person
            if any(k in label_lower for k in person_keywords):
                has_person = True
                print(f"  ✓ Person detected: {label['name']} ({instances} instances)")
            
            # Check for CLEAR action signals ONLY
            if any(k in label_lower for k in ACTION_keywords):
                has_clear_action = True
                detected_labels.append(label['name'])
                if instances > 0:
                    action_count += instances
                else:
                    action_count += 1
                print(f"  ✓✓ CLEAR ACTION: {label['name']}")
            
            # Not enough alone - log but don't count
            elif any(k in label_lower for k in NOT_ENOUGH_keywords):
                has_weak_activity = True
                print(f"  ⚠️ Weak signal (not enough): {label['name']}")
        
        # Only count if CLEAR action keywords present
        if has_clear_action and has_person and action_count > 0:
            count = action_count
            action_str = ', '.join(detected_labels) if detected_labels else 'Action'
            answer = f"Yes - {action_str} detected"
            print(f"🎯 BACKFLIP DETECTED: {answer}")
        elif has_person and has_weak_activity:
            answer = "No - Person present but only weak activity (Sport/Fighting), no clear jump/flip"
            print(f"  ❌ Weak activity only, no clear action")
        elif has_person:
            answer = "No - Person present but no action"
            print(f"  ❌ No action detected")
        else:
            answer = "No"
            print(f"  ❌ No person detected")
    
    elif 'roller coaster' in query.lower() or 'coaster' in query.lower():
        keywords = ['roller coaster', 'coaster', 'ride', 'amusement']
        for label in labels_data:
            if any(k in label['name'].lower() for k in keywords):
                count = label['instances'] if label['instances'] > 0 else 1
                answer = f"Yes - {count} ({label['name']})"
                break
    
    elif 'people' in query.lower() or 'person' in query.lower():
        for label in labels_data:
            if label['name'].lower() in ['person', 'people', 'human']:
                count = label['instances'] if label['instances'] > 0 else 1
                answer = f"{count} person(s)"
                break
    
    return count, answer

@app.route('/api/stream-counter')
def stream_counter():
    """Stream counting results in real-time (SSE)"""
    video_path = request.args.get('video_path', '')
    query = request.args.get('query', 'What do you see?')
    
    print(f"📊 Stream counter request - Video: {video_path}, Query: {query}")
    if bedrock_client:
        print(f"🤖 AI Mode: Using Amazon Titan Text with context awareness")
    else:
        print(f"⚡ Basic Mode: Using keyword matching")
    
    # Smart response cache to avoid redundant AI calls
    ai_response_cache = {}
    
    def generate():
        # Send initial connection message
        yield f"data: {json.dumps({'type': 'connected', 'message': 'Stream started'})}\n\n"
        
        try:
            # Load video - try multiple path formats
            video_file = None
            possible_paths = [
                video_path.lstrip('/'),
                video_path,
                f"uploads/{video_path.split('/')[-1]}"
            ]
            
            for path in possible_paths:
                if os.path.exists(path):
                    video_file = path
                    print(f"✅ Video found at: {path}")
                    break
            
            if not video_file:
                error_msg = f"Video not found. Tried: {possible_paths}"
                print(f"❌ {error_msg}")
                yield f"data: {json.dumps({'type': 'error', 'message': error_msg})}\n\n"
                return
            
            # Extract frames from video (sample smartly for speed)
            print(f"🎬 Extracting frames from: {video_path}")
            
            # For speed: extract every 2 seconds for long videos, every 1s for short
            video = cv2.VideoCapture(video_file)
            video_fps = video.get(cv2.CAP_PROP_FPS)
            duration = video.get(cv2.CAP_PROP_FRAME_COUNT) / video_fps if video_fps > 0 else 30
            video.release()
            
            # Balanced sampling: enough frames for good coverage
            sample_rate = 3  # Analyze every 3 seconds (good balance)
            print(f"📊 Video duration: {duration:.1f}s, sampling every {sample_rate}s")
            
            frames = extract_frames(video_file, fps=1/sample_rate)
            total_frames = len(frames)
            print(f"✅ Got {total_frames} frames to analyze")
            
            if total_frames == 0:
                error_msg = "No frames extracted from video"
                print(f"❌ {error_msg}")
                yield f"data: {json.dumps({'type': 'error', 'message': error_msg})}\n\n"
                return
            
            # Process frames sequentially but with optimizations
            # (Parallel processing would require refactoring SSE streaming)
            frame_context = []  # Store recent frames for context awareness
            
            for idx, (timestamp, frame_bytes) in enumerate(frames):
                # Send progress
                print(f"🎬 Processing frame {idx + 1}/{total_frames} at {timestamp:.1f}s")
                yield f"data: {json.dumps({'type': 'progress', 'frame': idx + 1, 'total': total_frames, 'timestamp': timestamp})}\n\n"
                
                try:
                    # Use Rekognition to get labels (optimized with fewer labels and higher confidence)
                    rek_response = rek_client.detect_labels(
                        Image={'Bytes': frame_bytes},
                        MaxLabels=10,  # Reduced from 15 for speed
                        MinConfidence=70  # Increased from 60 for accuracy
                    )
                    
                    # Get labels with confidence and instances
                    labels_data = []
                    for label in rek_response.get('Labels', []):
                        instances = label.get('Instances', [])
                        labels_data.append({
                            'name': label['Name'],
                            'confidence': label['Confidence'],
                            'instances': len(instances)
                        })
                    
                    # Detect people/faces in frame
                    recognized_people = []
                    has_person_in_frame = False
                    
                    # Check for Person label (fast)
                    for label in labels_data:
                        if label['name'].lower() in ['person', 'people', 'human']:
                            has_person_in_frame = True
                            # Count how many people
                            person_count = label['instances'] if label['instances'] > 0 else 1
                            print(f"👤 {person_count} person(s) detected in frame")
                            break
                    
                    # Combine labels and recognized people
                    labels_text = ', '.join([f"{l['name']} ({l['instances']} instances)" if l['instances'] > 0 else l['name'] for l in labels_data])
                    
                    if recognized_people:
                        labels_text = f"Recognized: {', '.join(recognized_people)}. Labels: {labels_text}"
                    
                    # Use AI to interpret labels
                    count = 0
                    answer = "No"
                    
                    if bedrock_client:
                        # Create cache key from top 3 labels for speed
                        cache_key = ','.join(sorted([l['name'] for l in labels_data[:3]]))
                        
                        # Check cache first
                        if cache_key in ai_response_cache:
                            ai_answer = ai_response_cache[cache_key]
                            print(f"💨 Using cached response for: {cache_key[:30]}...")
                        else:
                            # Use AI to interpret the labels intelligently
                            # Special handling for backflip detection
                            is_backflip_query = any(word in query.lower() for word in ['backflip', 'flip', 'acrobatic'])
                            
                            if is_backflip_query:
                                prompt = f"""Is someone CLEARLY doing a backflip or jumping acrobatically in this frame?

Labels: {labels_text}
Person in frame: {has_person_in_frame}

COUNT as YES (action keywords):
- Jump, Jumping, Flip, Flipping, Diving, Airborne, Flying, Acrobatic, Gymnast

DO NOT count alone (need action keywords too):
- Fighting, Sport, Dancing, Activity, Exercise, Playing, Fun

Rules:
1. MUST have Person AND at least ONE action keyword (Jump/Flip/Airborne etc)
2. Sport/Fighting/Activity alone WITHOUT Jump/Flip/Airborne → "No"
3. Just Person/People standing → "No"

Be selective. Only "Yes" if clear jumping/flipping action.

Answer (Yes/No only):"""
                            else:
                                prompt = f"""Given these AWS Rekognition labels from a video frame:
{labels_text}

Question: {query}

Respond with:
1. A number if counting (e.g., "3" for 3 people)
2. "Yes" or "No" for detection questions
3. Be specific and accurate

Answer:"""
                            
                            try:
                                response = bedrock_client.invoke_model(
                                    modelId='amazon.titan-text-express-v1',
                                    body=json.dumps({
                                        "inputText": prompt,
                                        "textGenerationConfig": {
                                            "maxTokenCount": 50,
                                            "temperature": 0.1,
                                            "topP": 0.9
                                        }
                                    })
                                )
                            
                                response_body = json.loads(response['body'].read())
                                ai_answer = response_body.get('results', [{}])[0].get('outputText', '').strip()
                                
                                # Cache the response for similar frames
                                ai_response_cache[cache_key] = ai_answer
                                print(f"💾 Cached response for: {cache_key[:30]}...")
                                
                            except Exception as e:
                                print(f"⚠️ AI interpretation failed: {e}, falling back to label matching")
                                # Fallback to simple label matching
                                count, answer = fallback_label_matching(labels_data, query)
                                ai_answer = answer
                        
                        # Extract count from AI response
                        numbers = re.findall(r'\d+', ai_answer)
                        if numbers:
                            count = int(numbers[0])
                        elif 'yes' in ai_answer.lower():
                            count = 1
                        
                        answer = ai_answer
                        print(f"🤖 AI interpretation: {ai_answer}")
                    else:
                        # No Bedrock available, use simple matching
                        count, answer = fallback_label_matching(labels_data, query)
                    
                    print(f"🔍 Frame {idx}: {labels_text[:100]}... → {answer}, COUNT={count}")
                    
                    # Send detection result with count and celebrities
                    result = {
                        'type': 'detection',
                        'timestamp': timestamp,
                        'answer': answer,
                        'count': count
                    }
                    
                    if count > 0:
                        print(f"✅ DETECTION! Frame {idx} at {timestamp:.1f}s: count={count}")
                    
                    # Add celebrity info if detected
                    if recognized_people:
                        result['celebrities'] = recognized_people
                    
                    # Store frame context for better understanding
                    frame_context.append({
                        'timestamp': timestamp,
                        'answer': answer,
                        'labels': [l['name'] for l in labels_data[:3]],  # Top 3 labels only
                        'celebrities': recognized_people
                    })
                    # Keep only last 3 frames for context (memory optimization)
                    if len(frame_context) > 3:
                        frame_context.pop(0)
                    
                    # Generate commentary with voice every 3 frames
                    if idx % 3 == 0 and idx > 0:
                        try:
                            print(f"📝 Generating commentary for frame {idx}...")
                            
                            commentary = None
                            
                            # Try AI commentary with long delay to avoid rate limits
                            if bedrock_client:
                                try:
                                    import time
                                    time.sleep(2)  # 2 second delay between AI calls
                                    
                                    extra_info = ""
                                    if has_person_in_frame:
                                        extra_info = f"Person count: {person_count}. "
                                    
                                    commentary = generate_commentary(
                                        extra_info + labels_text, 
                                        recognized_people, 
                                        answer, 
                                        timestamp, 
                                        query,
                                        frame_context[:-1],
                                        None
                                    )
                                except Exception as e:
                                    print(f"⚠️ AI commentary failed: {e}, using simple fallback")
                                    commentary = None
                            
                            # Fallback: Smart natural behavior narration
                            if not commentary:
                                import random
                                
                                # Get clean scene description (avoid raw labels like "Person", "Adult")
                                scene_labels = [l['name'].lower() for l in labels_data if l['name'].lower() not in ['person', 'people', 'adult', 'male', 'man', 'human', 'face', 'head', 'clothing']]
                                scene = scene_labels[0] if scene_labels else "venue"
                                
                                # Map generic labels to better descriptions
                                scene_map = {
                                    'fun': 'theme park',
                                    'amusement park': 'theme park',
                                    'theme park': 'theme park',
                                    'sport': 'sports venue',
                                    'fighting': 'action area',
                                    'basketball': 'basketball court',
                                    'people': 'venue'
                                }
                                scene = scene_map.get(scene, scene)
                                
                                if has_person_in_frame:
                                    if 'yes' in answer.lower():
                                        # Action detected - short exciting commentary
                                        patterns = [
                                            f"There's the launch - body rotating through the air",
                                            f"Nice flip here - good form on the rotation",
                                            f"Up he goes with the backflip attempt",
                                            f"Launching into the flip - crowd's loving it",
                                            f"Here comes another acrobatic move",
                                            f"Perfect rotation on that flip"
                                        ]
                                        commentary = random.choice(patterns)
                                    else:
                                        # No action - short natural commentary
                                        if person_count == 1:
                                            patterns = [
                                                f"The athlete at the {scene} preparing for the next move",
                                                f"Moving solo through the {scene} setting up position",
                                                f"One athlete working the {scene} here"
                                            ]
                                        elif person_count < 5:
                                            patterns = [
                                                f"Small group at the {scene} getting ready",
                                                f"A few athletes gathering at the {scene}",
                                                f"The {scene} with a handful of people setting up"
                                            ]
                                        else:
                                            patterns = [
                                                f"Crowd building at the {scene} waiting for action",
                                                f"Packed {scene} with everyone watching closely",
                                                f"Lots of energy in the {scene} crowd right now"
                                            ]
                                        commentary = random.choice(patterns)
                                else:
                                    commentary = f"The camera captures the {scene} scene right now, with the atmosphere building as we await the next moment of action"
                                print(f"📝 Using smart natural commentary")
                            
                            result['commentary'] = commentary
                            print(f"🎙️ Commentary: {commentary}")
                            
                            # Generate voice
                            if elevenlabs_client:
                                audio_url = text_to_speech(commentary, timestamp)
                                if audio_url:
                                    result['audio_url'] = audio_url
                                    print(f"✅ Voice generated: {audio_url}")
                                else:
                                    print(f"❌ Voice generation failed")
                            else:
                                print(f"⚠️ ElevenLabs not initialized - no voice")
                        except Exception as e:
                            print(f"⚠️ Commentary failed: {e}")
                            import traceback
                            traceback.print_exc()
                    
                    yield f"data: {json.dumps(result)}\n\n"
                    
                except Exception as e:
                    print(f"❌ Error analyzing frame {idx}: {e}")
                    import traceback
                    traceback.print_exc()
                    # Don't send error to client, just continue
                    continue
            
            # Send completion
            yield f"data: {json.dumps({'type': 'complete'})}\n\n"
            
        except Exception as e:
            print(f"❌ Stream error: {e}")
            traceback.print_exc()
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"
    
    response = Response(generate(), mimetype='text/event-stream')
    response.headers['Cache-Control'] = 'no-cache'
    response.headers['X-Accel-Buffering'] = 'no'
    response.headers['Connection'] = 'keep-alive'
    return response

@app.route('/player')
def player():
    """Serve the enhanced video player demo"""
    return render_template('video_player.html')

@app.route('/old')
def old_index():
    """Serve the old demo frontend"""
    return render_template('index.html')

@app.route('/monitor')
def monitor():
    """Serve the AI detection monitor"""
    return render_template('monitor.html')

@app.route('/demo/twitch')
def fake_twitch():
    """Serve the fake Twitch demo page"""
    return render_template('fake_twitch.html')

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'StreamBet Recognition API',
        'version': '1.0.0-hackathon'
    })

@app.route('/upload', methods=['POST'])
def upload_video():
    """Upload video file with size limit (10MB max, recommended < 1 min)"""
    try:
        # Check if file is in request
        if 'video' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No video file provided'
            }), 400
        
        file = request.files['video']
        
        # Check if file is selected
        if file.filename == '':
            return jsonify({
                'success': False,
                'error': 'No file selected'
            }), 400
        
        # Check file extension
        if not ('.' in file.filename and file.filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS):
            return jsonify({
                'success': False,
                'error': f'Invalid file type. Allowed: {", ".join(ALLOWED_EXTENSIONS)}'
            }), 400
        
        # Check file size (10MB = 10485760 bytes)
        file.seek(0, 2)  # Seek to end
        file_size = file.tell()
        file.seek(0)  # Reset to beginning
        
        if file_size > 10 * 1024 * 1024:
            size_mb = file_size / (1024 * 1024)
            return jsonify({
                'success': False,
                'error': f'File too large ({size_mb:.1f}MB). Maximum size is 10MB (recommended < 1 min video)'
            }), 413
        
        # Save file
        filename = f"{int(time.time())}_{secure_filename(file.filename)}"
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)
        
        file_path = f'/uploads/{filename}'
        
        print(f"✅ Video uploaded successfully: {filename} ({file_size / (1024 * 1024):.2f}MB)")
        
        return jsonify({
            'success': True,
            'file_path': file_path,
            'filename': filename,
            'size_mb': round(file_size / (1024 * 1024), 2)
        })
        
    except Exception as e:
        print(f"❌ Upload error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/uploads/<filename>')
def serve_upload(filename):
    """Serve uploaded files (screenshots)"""
    return send_from_directory(UPLOAD_FOLDER, filename)

@app.route('/audio/<filename>')
def serve_audio(filename):
    """Serve audio commentary files"""
    return send_from_directory(AUDIO_FOLDER, filename)

@app.route('/api/bets', methods=['GET'])
def get_bets():
    """Get available betting markets"""
    return jsonify({'bets': DEMO_BETS})

@app.route('/api/analyze-video-stream', methods=['GET'])
def analyze_video_stream():
    """Stream analysis results in real-time with commentary"""
    video_path = request.args.get('video_path')
    
    if not video_path:
        return jsonify({'error': 'No video_path provided'}), 400
    
    # Convert URL path to filesystem path
    if video_path.startswith('/uploads/'):
        filename = video_path.replace('/uploads/', '')
        filepath = os.path.join(UPLOAD_FOLDER, filename)
    else:
        return jsonify({'error': 'Invalid video path'}), 400
    
    if not os.path.exists(filepath):
        return jsonify({'error': 'Video file not found'}), 404
    
    def generate():
        try:
            import sys
            
            print("🎬 SSE: Starting analysis stream")
            yield f"data: {json.dumps({'type': 'start', 'message': '🎬 Starting analysis...', 'commentary': 'Initializing AI detection system'})}\n\n"
            sys.stdout.flush()
            
            # Extract frames
            print("🎬 SSE: Extracting frames")
            frames = extract_frames(filepath, fps=1)
            if not frames:
                print("❌ SSE: No frames extracted")
                yield f"data: {json.dumps({'type': 'error', 'message': 'Could not extract frames'})}\n\n"
                return
            
            print(f"✅ SSE: Extracted {len(frames)} frames")
            yield f"data: {json.dumps({'type': 'info', 'message': f'📹 Extracted {len(frames)} frames', 'commentary': f'Analyzing {len(frames)} seconds of footage'})}\n\n"
            sys.stdout.flush()
            time.sleep(0.1)  # Small delay to ensure client receives
            
            # Smart Context-Aware Tracking
            backflips = []
            
            # Multi-signal detection (not just keywords!)
            backflip_indicators = ['jump', 'jumping', 'flip', 'flipping', 'backflip', 'acrobatics', 'floating', 'airborne', 'fighting']  # MOVED fighting here!
            weak_indicators = ['sport', 'activity', 'exercise']  # Weak signals
            
            DEBOUNCE_SECONDS = 3.0
            SKIP_SECONDS = 3.0
            last_detection_time = -999
            
            # Context tracking
            frame_history = []  # Track last few frames
            person_detected_frames = []  # Where we see IShowSpeed
            
            i = 0
            frames_analyzed = 0
            frames_skipped = 0
            
            yield f"data: {json.dumps({'type': 'info', 'message': '🧠 Context-aware mode: Tracking IShowSpeed movements', 'commentary': 'Multi-signal analysis with frame context'})}\n\n"
            sys.stdout.flush()
            
            # Warmup: Analyze first frame to establish AWS connection
            if len(frames) > 0:
                yield f"data: {json.dumps({'type': 'info', 'message': '🔥 Warming up AWS connection...', 'commentary': 'First call takes longer, establishing connection'})}\n\n"
                sys.stdout.flush()
                
                _, warmup_frame = frames[0]
                try:
                    _ = analyze_frame_with_rekognition(warmup_frame, rek_client)
                    yield f"data: {json.dumps({'type': 'info', 'message': '✅ AWS connection ready!', 'commentary': 'Subsequent frames will be faster'})}\n\n"
                    sys.stdout.flush()
                except Exception as e:
                    print(f"⚠️  Warmup failed: {e}")
            
            time.sleep(0.1)
            
            while i < len(frames):
                timestamp, frame_bytes = frames[i]
                
                yield f"data: {json.dumps({'type': 'progress', 'message': f'⏳ Analyzing {timestamp:.1f}s', 'commentary': 'Sending frame to AWS...', 'timestamp': timestamp, 'frames_analyzed': frames_analyzed})}\n\n"
                sys.stdout.flush()
                
                try:
                    print(f"📊 SSE: Analyzing frame {i+1}/{len(frames)} at {timestamp:.2f}s")
                    
                    # Send heartbeat during analysis
                    yield f"data: {json.dumps({'type': 'heartbeat', 'message': f'🔄 AWS analyzing {timestamp:.1f}s...', 'commentary': 'Waiting for AI response...'})}\n\n"
                    sys.stdout.flush()
                    
                    frame_result = analyze_frame_with_rekognition(frame_bytes, rek_client)
                    # AWS returns 'Labels' (capital L)
                    labels = frame_result.get('Labels', [])
                    num_labels = len(labels)
                    print(f"✅ SSE: Got {num_labels} labels")
                    frames_analyzed += 1
                    
                    yield f"data: {json.dumps({'type': 'heartbeat', 'message': f'✅ Received {num_labels} labels', 'commentary': 'Processing results...'})}\n\n"
                    sys.stdout.flush()
                    
                except Exception as e:
                    print(f"❌ SSE: Error analyzing frame: {e}")
                    yield f"data: {json.dumps({'type': 'error', 'message': f'Error at {timestamp:.1f}s', 'commentary': str(e)})}\n\n"
                    sys.stdout.flush()
                    i += 1
                    continue
                
                # Multi-signal analysis
                labels_found = []
                has_person = False
                has_strong_activity = False
                has_weak_activity = False
                confidence_score = 0
                
                for label in labels:
                    label_name = label['Name'].lower()
                    confidence = label['Confidence']
                    labels_found.append((label_name, confidence))
                    
                    # Check for person
                    if 'person' in label_name or 'human' in label_name:
                        has_person = True
                        person_detected_frames.append(timestamp)
                    
                    # Check for strong backflip indicators
                    if any(ind in label_name for ind in backflip_indicators):
                        has_strong_activity = True
                        confidence_score = max(confidence_score, confidence)  # Full weight!
                    
                    # Check for weak activity signals
                    elif any(ind in label_name for ind in weak_indicators):
                        has_weak_activity = True
                        confidence_score = max(confidence_score, confidence * 0.7)  # Lower weight
                
                # Store frame context
                frame_context = {
                    'timestamp': timestamp,
                    'has_person': has_person,
                    'has_strong': has_strong_activity,
                    'has_weak': has_weak_activity,
                    'confidence': confidence_score,
                    'labels': labels_found[:5]  # Top 5 labels
                }
                frame_history.append(frame_context)
                if len(frame_history) > 5:  # Keep last 5 frames
                    frame_history.pop(0)
                
                # Log what we found for debugging
                top_labels_str = ', '.join([f"{l[0]}({l[1]:.0f}%)" for l in labels_found[:3]])
                print(f"🏷️  Frame {timestamp:.1f}s: {top_labels_str} | Person:{has_person} Strong:{has_strong_activity} Score:{confidence_score:.0f}")
                
                # Smart detection: Threshold 80%
                is_real_backflip = False
                detected_label = None
                
                if has_strong_activity and confidence_score > 80:
                    # Strong indicator with high confidence
                    # Find which label triggered it
                    for label_name, conf in labels_found:
                        if any(ind in label_name for ind in backflip_indicators):
                            detected_label = label_name.title()
                            break
                    
                    is_real_backflip = True
                    label_name = detected_label or "Activity"
                    yield f"data: {json.dumps({'type': 'context', 'message': f'✅ Strong signal at {timestamp:.1f}s', 'commentary': f'{label_name} detected at {confidence_score:.0f}% confidence!'})}\n\n"
                    sys.stdout.flush()
                
                # Real backflip detection
                if is_real_backflip:
                    if timestamp - last_detection_time >= DEBOUNCE_SECONDS:
                        # Save screenshot of backflip frame
                        screenshot_filename = f"backflip_{timestamp:.2f}s.jpg"
                        screenshot_path = os.path.join(UPLOAD_FOLDER, screenshot_filename)
                        
                        try:
                            # Convert frame bytes to image and save
                            img = Image.open(io.BytesIO(frame_bytes))
                            img.save(screenshot_path, 'JPEG', quality=85)
                            print(f"📸 Saved screenshot: {screenshot_path}")
                        except Exception as e:
                            print(f"⚠️ Screenshot save failed: {e}")
                            screenshot_filename = None
                        
                        backflip_data = {
                            'timestamp': timestamp,
                            'label': detected_label or 'Backflip',
                            'confidence': confidence_score / 100,
                            'time': f"{int(timestamp // 60)}:{int(timestamp % 60):02d}",
                            'screenshot': f'/uploads/{screenshot_filename}' if screenshot_filename else None
                        }
                        backflips.append(backflip_data)
                        last_detection_time = timestamp
                        
                        yield f"data: {json.dumps({'type': 'detection', 'message': f'🎪 BACKFLIP DETECTED!', 'commentary': f'IShowSpeed just landed a backflip at {timestamp:.2f}s with {confidence_score:.1f}% confidence! Incredible athleticism!', 'data': backflip_data})}\n\n"
                        sys.stdout.flush()
                    else:
                        yield f"data: {json.dumps({'type': 'duplicate', 'message': f'⏭️ Same backflip', 'commentary': 'Continuation of same movement', 'timestamp': timestamp})}\n\n"
                        sys.stdout.flush()
                
                # Decide next step - CAREFUL SKIPPING (don't miss action!)
                if has_strong_activity:
                    # Strong activity - keep analyzing frame by frame
                    print(f"🎯 Strong activity - continuing frame by frame")
                    i += 1
                elif has_weak_activity and confidence_score > 50:
                    # Weak activity with decent confidence - check next frame
                    print(f"⚠️  Weak activity - checking next frame")
                    i += 1
                elif has_person:
                    # Person present - check EVERY frame (action could start anytime!)
                    # DON'T SKIP when person is detected
                    print(f"👤 Person present - checking next frame")
                    i += 1
                else:
                    # No person - skip 3 seconds
                    skip_frames = 3
                    if i + skip_frames < len(frames):
                        frames_skipped += skip_frames
                        i += skip_frames + 1
                        print(f"💤 No person - skipping {skip_frames}s")
                        yield f"data: {json.dumps({'type': 'skip', 'message': f'⚡ Skipped {skip_frames}s', 'commentary': 'Empty scene, jumping ahead'})}\n\n"
                        sys.stdout.flush()
                    else:
                        i += 1
            
            # Final results
            speed_gain = int((frames_skipped / len(frames)) * 100) if len(frames) > 0 else 0
            
            final_commentary = ''
            if len(backflips) == 0:
                final_commentary = 'Analysis complete. No backflips detected in this footage.'
            elif len(backflips) == 1:
                final_commentary = f'What a moment! IShowSpeed pulled off an incredible backflip at {backflips[0]["timestamp"]:.2f}s. The crowd goes wild! 🎉'
            else:
                final_commentary = f'Unbelievable! {len(backflips)} backflips detected! IShowSpeed is on fire today! 🔥'
            
            yield f"data: {json.dumps({'type': 'complete', 'message': '✅ Analysis complete!', 'commentary': final_commentary, 'data': {'backflips': backflips, 'count': len(backflips), 'frames_analyzed': frames_analyzed, 'frames_skipped': frames_skipped, 'total_frames': len(frames), 'speed_gain_percent': speed_gain}})}\n\n"
            
        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'message': f'❌ Error: {str(e)}', 'commentary': 'Something went wrong with the analysis'})}\n\n"
    
    return Response(stream_with_context(generate()), content_type='text/event-stream')

@app.route('/api/analyze-video', methods=['POST'])
def analyze_video_simple():
    """Simple video analysis that returns backflip count"""
    data = request.get_json()
    video_path = data.get('video_path')
    
    if not video_path:
        return jsonify({'error': 'No video_path provided'}), 400
    
    # Convert URL path to filesystem path
    if video_path.startswith('/uploads/'):
        filename = video_path.replace('/uploads/', '')
        filepath = os.path.join(UPLOAD_FOLDER, filename)
    else:
        return jsonify({'error': 'Invalid video path'}), 400
    
    if not os.path.exists(filepath):
        return jsonify({'error': 'Video file not found'}), 404
    
    try:
        print(f"🔍 Analyzing video: {filepath}")
        
        # Extract frames (1 per second)
        frames = extract_frames(filepath, fps=1)
        
        if not frames:
            return jsonify({'error': 'Could not extract frames'}), 500
        
        # Analyze frames for backflips with smart windowing
        backflips = []
        backflip_keywords = ['jump', 'jumping', 'flip', 'flipping', 'backflip', 'acrobatics', 
                            'floating', 'airborne', 'fighting', 'sport', 'activity']
        
        # Define action window - NEVER skip frames here
        ACTION_WINDOW_START = 15.0  # Start looking at 15s
        ACTION_WINDOW_END = 25.0    # Stop at 25s
        
        # Debouncing - only count as new backflip if 3+ seconds from last
        DEBOUNCE_SECONDS = 3.0
        last_detection_time = -999  # Start way in the past
        
        i = 0
        frames_analyzed = 0
        frames_skipped = 0
        
        while i < len(frames):
            timestamp, frame_bytes = frames[i]
            
            # Check if we're approaching or in the action window
            in_action_window = ACTION_WINDOW_START <= timestamp <= ACTION_WINDOW_END
            approaching_window = timestamp < ACTION_WINDOW_START and timestamp >= ACTION_WINDOW_START - 2.0
            past_window = timestamp > ACTION_WINDOW_END
            
            if in_action_window or approaching_window:
                # ALWAYS analyze frames in or near action window
                frames_analyzed += 1
                if in_action_window:
                    print(f"⏳ [ACTION] Frame {i+1}/{len(frames)} at {timestamp:.2f}s...", end='\r')
                else:
                    print(f"⏳ Frame {i+1}/{len(frames)} at {timestamp:.2f}s...", end='\r')
                
                frame_result = analyze_frame_with_rekognition(frame_bytes, rek_client)
                
                # Check for backflip indicators
                for label in frame_result['labels']:
                    label_name = label['Name'].lower()
                    confidence = label['Confidence']
                    
                    if any(keyword in label_name for keyword in backflip_keywords):
                        if confidence > 70:
                            # Debounce: only count if 3+ seconds from last detection
                            if timestamp - last_detection_time >= DEBOUNCE_SECONDS:
                                backflips.append({
                                    'timestamp': timestamp,
                                    'label': label['Name'],
                                    'confidence': confidence / 100,
                                    'time': f"{int(timestamp // 60)}:{int(timestamp % 60):02d}"
                                })
                                last_detection_time = timestamp
                                print(f"\n🎪 BACKFLIP at {timestamp:.2f}s: {label['Name']} ({confidence:.1f}%)")
                            else:
                                print(f"\r⏭️  Skipping duplicate at {timestamp:.2f}s (within {DEBOUNCE_SECONDS}s)...", end='\r')
                            break
                
                i += 1  # Move to next frame
                
            else:
                # Outside action window - calculate smart skip
                if past_window:
                    # After action window - skip remaining frames
                    skip_count = len(frames) - i - 1
                else:
                    # Before action window - skip but don't overshoot
                    frames_until_window = 0
                    for j in range(i, len(frames)):
                        if frames[j][0] >= ACTION_WINDOW_START - 2.0:
                            break
                        frames_until_window += 1
                    skip_count = min(10, frames_until_window) if frames_until_window > 0 else 0
                
                if skip_count > 0:
                    frames_skipped += skip_count
                    i += skip_count + 1
                    print(f"\r⚡ Skipping {skip_count} frames...", end='\r')
                else:
                    i += 1
        
        print(f"\n✅ Analysis complete! Found {len(backflips)} backflips")
        print(f"⚡ Performance: Analyzed {frames_analyzed} frames, skipped {frames_skipped} frames")
        print(f"🚀 Speed gain: {int((frames_skipped / len(frames)) * 100)}% faster!")
        
        return jsonify({
            'backflips': backflips,
            'count': len(backflips),
            'frames_analyzed': frames_analyzed,
            'frames_skipped': frames_skipped,
            'total_frames': len(frames),
            'speed_gain_percent': int((frames_skipped / len(frames)) * 100) if len(frames) > 0 else 0,
            'video_duration': frames[-1][0] if frames else 0
        })
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return jsonify({'error': str(e)}), 500

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


def analyze_frame_with_rekognition(frame_bytes, rek_client):
    """Analyze a single frame with AWS Rekognition"""
    response = rek_client.detect_labels(
        Image={'Bytes': frame_bytes},
        MaxLabels=15,
        MinConfidence=70
    )
    return response


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
    # Create required folders
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    os.makedirs(AUDIO_FOLDER, exist_ok=True)
    os.makedirs('templates', exist_ok=True)
    
    print("\n" + "="*60)
    print("🎮 StreamBet Recognition API")
    print("="*60)
    print(f"📁 Upload folder: {UPLOAD_FOLDER}")
    print(f"🎙️ Audio folder: {AUDIO_FOLDER}")
    print(f"☁️  AWS Bucket: {AWS_BUCKET}")
    print(f"🌍 Region: {AWS_REGION}")
    print("="*60 + "\n")
    
    # Use PORT from environment for Railway/Heroku
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV', 'development') != 'production'
    
    app.run(debug=debug, host='0.0.0.0', port=port)
