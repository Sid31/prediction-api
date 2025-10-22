# 🤖 StreamBet AI Video Detection Agent

AWS Bedrock AgentCore compatible agent that monitors videos and sends real-time detections to your backend via webhooks.

## 🏗️ Architecture

```
┌─────────────────┐      ┌──────────────────┐      ┌──────────────────┐
│   Video Source  │ ───▶ │  Agent (Port    │ ───▶ │  NewBackend      │
│   (URL)         │      │  8080)           │      │  (Port 8000)     │
└─────────────────┘      │                  │      │                  │
                         │  - Downloads     │      │  - Receives      │
                         │  - Extracts      │      │    webhooks      │
                         │  - Analyzes      │      │  - Emits via     │
                         │  - Detects       │      │    Socket.IO     │
                         │  - Notifies      │      │  - Resolves bets │
                         └──────────────────┘      └──────────────────┘
                                   │
                                   ▼
                         ┌──────────────────┐
                         │  AWS Rekognition │
                         │  Image API       │
                         └──────────────────┘
```

## 📋 AWS Bedrock AgentCore Contract

### Endpoints

#### `POST /invocations`
Main endpoint for video analysis requests.

**Request:**
```json
{
  "video_url": "https://example.com/video.mp4",
  "video_id": "abc123",
  "labels": ["person", "fighting", "sport"],
  "confidence": 0.6,
  "fps_sample": 1
}
```

**Response:**
```json
{
  "status": "success",
  "video_id": "abc123",
  "total_frames": 1723,
  "frames_analyzed": 30,
  "detections_count": 5,
  "detections": [...]
}
```

#### `GET /ping`
Health check endpoint.

**Response:**
```json
{
  "status": "Healthy",  // or "HealthyBusy"
  "time_of_last_update": 1729412345.12,
  "active_tasks": 0
}
```

## 🚀 Quick Start

### 1. Set Environment Variables

Create `.env` in the rekognitionAPI folder:
```bash
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret
WEBHOOK_URL=http://localhost:8000/api/events/detection
COLLECTION_ID=streambet-streamers
```

### 2. Start the Agent

```bash
cd /Users/sidousan/prediction.chat/rekognitionAPI

# Install dependencies (if not already done)
pip3 install -r requirements.txt

# Start agent on port 8080
python3 agent_server.py
```

You should see:
```
============================================================
🎮 StreamBet Video Detection Agent
============================================================
📍 Listening on: 0.0.0.0:8080
🔗 Webhook URL: http://localhost:8000/api/events/detection
☁️  AWS Region: us-east-1
👤 Collection ID: streambet-streamers
============================================================
```

### 3. Start Your Backend

In another terminal:
```bash
cd /Users/sidousan/prediction.chat/newbackend
npm start
```

### 4. Test the Agent

```bash
cd /Users/sidousan/prediction.chat/rekognitionAPI
chmod +x test_agent.sh
./test_agent.sh
```

## 📡 Webhook Notifications

When the agent detects something, it sends this to your backend:

```json
{
  "event": "detection",
  "video_id": "abc123",
  "frame_id": 420,
  "timestamp": 19.69,
  "label": "fighting",
  "confidence": 0.999,
  "bbox": [0.25, 0.30, 0.40, 0.50],
  "ts": 1729412345.12
}
```

Your backend receives it at `POST /api/events/detection` and:
1. Stores the detection
2. Broadcasts via Socket.IO to all connected clients
3. Checks if it should resolve any bets

## 🔌 Socket.IO Events

Clients connected to your backend will receive:

### Event: `ai_detection`
Broadcast to all clients:
```javascript
socket.on('ai_detection', (data) => {
  console.log('Detection:', data);
  // data.event === "detection"
  // data.data contains full detection object
});
```

### Event: `video_detection`
Sent to clients watching specific video:
```javascript
socket.on('video_detection', (data) => {
  console.log('Video detection:', data);
});
```

## 🎯 Example: Frontend Integration

```javascript
// Connect to your backend
const socket = io('http://localhost:8000');

// Listen for AI detections
socket.on('ai_detection', (event) => {
  const { video_id, label, timestamp, confidence } = event.data;
  
  console.log(`🚨 ${label} detected at ${timestamp}s (${confidence*100}%)`);
  
  // Update UI
  showNotification(`${label} detected!`);
  updateBetStatus(video_id);
});

// Request video analysis
fetch('http://localhost:8080/invocations', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    video_url: 'https://example.com/stream.mp4',
    video_id: 'live_stream_123',
    labels: ['person', 'fighting', 'backflip'],
    confidence: 0.7,
    fps_sample: 2
  })
});
```

## 🐳 Docker Deployment (ARM64)

### Build Image
```bash
cd /Users/sidousan/prediction.chat/rekognitionAPI
docker build -f Dockerfile.agent -t streambet-agent:latest .
```

### Run Container
```bash
docker run -d \
  --name streambet-agent \
  -p 8080:8080 \
  --env-file .env \
  streambet-agent:latest
```

### Check Health
```bash
curl http://localhost:8080/ping
```

## 📊 Monitoring

### Check Agent Status
```bash
curl http://localhost:8080/ping
```

### View Recent Detections
```bash
curl http://localhost:8000/api/events/recent
```

### View Video Detections
```bash
curl http://localhost:8000/api/events/video/abc123
```

## 🎮 Betting Integration

The agent automatically checks if detections should trigger bet resolution:

```javascript
// In event.controller.js
function shouldResolveBet(detection) {
  // High confidence threshold
  if (detection.confidence < 0.8) return false;
  
  // Critical events that resolve bets
  const criticalLabels = ['fighting', 'backflip', 'goal'];
  return criticalLabels.includes(detection.label.toLowerCase());
}
```

When a detection triggers bet resolution:
1. Agent sends webhook to backend
2. Backend checks active bets for matching video/event
3. Determines winners based on detection
4. Updates bet status
5. Triggers payouts via Socket.IO notification

## 🔧 Configuration

### Agent Environment Variables
```bash
AWS_REGION=us-east-1               # AWS region
AWS_ACCESS_KEY_ID=xxx              # AWS credentials
AWS_SECRET_ACCESS_KEY=xxx
WEBHOOK_URL=http://localhost:8000/api/events/detection  # Webhook endpoint
COLLECTION_ID=streambet-streamers  # Face collection
```

### Detection Parameters
```javascript
{
  "labels": [            // What to detect
    "person",
    "fighting",
    "sport",
    "backflip"
  ],
  "confidence": 0.6,     // Minimum confidence (0-1)
  "fps_sample": 1        // Frames per second to analyze
}
```

## 🎪 Supported Detections

Based on AWS Rekognition Image API:

### Actions
- Fighting, Sport, Activity
- Jumping, Floating, Flip
- Acrobatics, Gymnastics

### Objects
- Person, People
- Equipment, Gear

### Scenes
- Amusement Park, Indoor, Outdoor
- Stage, Arena

### Custom (via face collection)
- IShowSpeed, Streamer names

## ⚡ Performance

- **Processing:** ~1 frame per second
- **Latency:** <1 second per frame
- **Cost:** $0.001 per frame analyzed
- **Example:** 30-second video @ 1fps = 30 frames = $0.03

## 🚨 Troubleshooting

### Agent won't start
```bash
# Check port 8080 is available
lsof -ti:8080

# Check AWS credentials
aws rekognition describe-collection --collection-id streambet-streamers
```

### Webhooks not received
```bash
# Check backend is running
curl http://localhost:8000/

# Check webhook URL in .env
echo $WEBHOOK_URL

# Test webhook manually
curl -X POST http://localhost:8000/api/events/detection \
  -H 'Content-Type: application/json' \
  -d '{"event":"detection","video_id":"test","label":"person"}'
```

### Socket.IO not working
```bash
# Check Socket.IO connection in browser console
socket.on('connect', () => console.log('Connected!'));

# Check backend logs for Socket.IO events
```

## 📝 API Reference

### Backend Endpoints (Port 8000)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/events/detection` | POST | Receive detection webhook |
| `/api/events/recent` | GET | Get recent detections |
| `/api/events/video/:videoId` | GET | Get video detections |

### Agent Endpoints (Port 8080)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/ping` | GET | Health check |
| `/invocations` | POST | Analyze video |
| `/invocations/stream` | POST | Stream analysis (SSE) |

## 🎯 Next Steps

1. ✅ Set up agent and backend
2. ✅ Test with sample video
3. ✅ Connect frontend to Socket.IO
4. TODO: Add bet resolution logic
5. TODO: Add real-time stream capture
6. TODO: Deploy to production (AWS/Docker)

## 💡 Pro Tips

- Use `fps_sample: 2` for faster real-time detection
- Set `confidence: 0.8` for high-precision bets
- Add cooldown to prevent spam notifications
- Cache video downloads for repeated analysis
- Use Redis for production detection storage

---

**Your AI betting resolution system is now fully event-driven!** 🎉
