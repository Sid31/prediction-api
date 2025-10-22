# ⚡ Quick Reference Card

## 🚀 Start Everything (3 Terminals)

### Terminal 1: Backend
```bash
cd /Users/sidousan/prediction.chat/newbackend
npm start
```

### Terminal 2: Agent
```bash
cd /Users/sidousan/prediction.chat/rekognitionAPI
./start_agent.sh
```

### Terminal 3: Recognition API
```bash
cd /Users/sidousan/prediction.chat/rekognitionAPI
./start.sh
```

---

## 🌐 URLs

| Service | URL | Purpose |
|---------|-----|---------|
| **Monitor** | http://localhost:5000/monitor | Real-time detection dashboard |
| **Video Demo** | http://localhost:5000 | Video upload & playback |
| **Backend** | http://localhost:8000 | REST API |
| **Agent** | http://localhost:8080 | AWS AgentCore endpoint |

---

## 📡 API Endpoints

### Agent (Port 8080)
```bash
# Health check
GET /ping

# Analyze video
POST /invocations
{
  "video_url": "https://example.com/video.mp4",
  "video_id": "abc123",
  "labels": ["person", "fighting", "sport"],
  "confidence": 0.6,
  "fps_sample": 1
}
```

### Backend (Port 8000)
```bash
# Webhook (called by agent)
POST /api/events/detection

# Get recent detections
GET /api/events/recent?limit=10

# Get video detections
GET /api/events/video/:videoId
```

---

## 🔥 Quick Test

```bash
# 1. Open monitor
open http://localhost:5000/monitor

# 2. Trigger analysis (in another terminal)
curl -X POST http://localhost:8080/invocations \
  -H 'Content-Type: application/json' \
  -d '{
    "video_url": "http://localhost:5000/uploads/1760892120_tets.mp4",
    "video_id": "test_001",
    "labels": ["person", "fighting"],
    "confidence": 0.6,
    "fps_sample": 1
  }'

# 3. Watch detections appear in real-time!
```

---

## 🎯 Expected Results

When analyzing `tets.mp4`:
- ✅ **IShowSpeed:** Detected 6 times
- ✅ **Fighting:** Detected at 19.69s (99.9%)
- ✅ **Sport:** Multiple detections
- ✅ **Amusement Park:** 98.7% confidence
- ✅ **Processing:** ~15 seconds
- ✅ **Frames:** 30 analyzed

---

## 📊 Socket.IO Events

### Listen for Detections
```javascript
// In browser console or frontend
const socket = io('http://localhost:8000');

socket.on('ai_detection', (event) => {
  console.log('🚨 Detection:', event.data);
  // {
  //   video_id: "test_001",
  //   label: "fighting",
  //   timestamp: 19.69,
  //   confidence: 0.999
  // }
});
```

---

## 🛠️ Troubleshooting

### Ports in Use
```bash
# Kill stuck processes
lsof -ti:8080 | xargs kill -9  # Agent
lsof -ti:8000 | xargs kill -9  # Backend
lsof -ti:5000 | xargs kill -9  # Recognition API
```

### Check Health
```bash
# Agent
curl http://localhost:8080/ping

# Backend
curl http://localhost:8000/

# Recognition API
curl http://localhost:5000/api/health
```

### Test Webhook
```bash
curl -X POST http://localhost:8000/api/events/detection \
  -H 'Content-Type: application/json' \
  -d '{"event":"detection","video_id":"test","label":"person","timestamp":10.5,"confidence":0.9}'
```

---

## 📁 Project Structure

```
prediction.chat/
├── rekognitionAPI/          # Recognition & Agent
│   ├── agent_server.py      # AWS AgentCore agent
│   ├── app.py               # Flask API (port 5000)
│   ├── start_agent.sh       # Start agent
│   ├── start.sh             # Start Flask
│   └── templates/
│       ├── monitor.html     # Real-time monitor
│       └── video_player.html
│
└── newbackend/              # Backend (port 8000)
    ├── server.js
    ├── app/
    │   ├── controllers/
    │   │   └── event.controller.js  # NEW
    │   └── routes/
    │       └── event.routes.js      # NEW
    └── package.json
```

---

## ⚙️ Configuration

### .env (rekognitionAPI)
```bash
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret
WEBHOOK_URL=http://localhost:8000/api/events/detection
COLLECTION_ID=streambet-streamers
```

### Detection Labels
Common labels to detect:
- `person`, `people`
- `fighting`, `sport`, `activity`
- `jumping`, `floating`, `flip`
- `backflip`, `acrobatics`
- `fun`, `amusement park`

---

## 🎬 Demo Flow

1. **User uploads video** → Recognition API (5000)
2. **Agent analyzes** → Extracts frames (8080)
3. **AWS Rekognition** → Detects labels
4. **Agent sends webhook** → Backend (8000)
5. **Backend emits Socket.IO** → All connected clients
6. **Monitor updates** → Real-time UI

---

## 🚀 Production Checklist

- [ ] Update `WEBHOOK_URL` to production URL
- [ ] Use Redis for detection storage
- [ ] Add authentication to webhooks
- [ ] Set up CloudWatch monitoring
- [ ] Deploy as Docker containers
- [ ] Configure load balancer
- [ ] Add rate limiting
- [ ] Set up error tracking (Sentry)

---

## 📞 Support

**Documentation:**
- Full Setup: `/COMPLETE_SETUP.md`
- Agent Details: `/rekognitionAPI/AGENT_SETUP.md`
- Backflip Detection: `/rekognitionAPI/BACKFLIP_DETECTION.md`

**Quick Help:**
```bash
# View agent logs
tail -f /tmp/agent.log

# View backend logs
cd /newbackend && npm start

# Test analysis
cd /rekognitionAPI && ./test_agent.sh
```

---

**Ready to detect events in real-time!** 🎉
