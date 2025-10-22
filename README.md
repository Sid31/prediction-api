# 🎬 StreamBet Recognition API

> **AI-powered video analysis with real-time live commentary** - Now with Claude Anthropic inspired design

[![AWS](https://img.shields.io/badge/AWS-Rekognition-orange)](https://aws.amazon.com/rekognition/)
[![Bedrock](https://img.shields.io/badge/AWS-Bedrock-purple)](https://aws.amazon.com/bedrock/)
[![Python](https://img.shields.io/badge/Python-3.8+-blue)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-3.0-green)](https://flask.palletsprojects.com/)
[![ElevenLabs](https://img.shields.io/badge/ElevenLabs-TTS-blueviolet)](https://elevenlabs.io/)
[![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)

## 🎯 What is StreamBet?

StreamBet is an AI-powered platform that automatically verifies betting events on live streams using computer vision. Upload a video, and AWS Rekognition analyzes it to detect activities, provide timestamps, and suggest betting markets - all in under 60 seconds.

### The Problem We Solve
- ❌ Manual bet verification is slow and expensive
- ❌ Disputes are common in traditional betting
- ❌ Streamers can't easily monetize predictions
- ❌ Fans wait days for payouts

### Our Solution
- ✅ AI analyzes videos in real-time with 90%+ confidence
- ✅ Transparent verification with exact timestamps
- ✅ Automated bet resolution - no disputes
- ✅ Instant payouts triggered by AI

### ✨ NEW: Live Commentary System
- 🎙️ **AI-Generated Commentary**: Amazon Bedrock creates natural sports commentary
- 🔊 **Text-to-Speech**: ElevenLabs brings commentary to life
- ⏱️ **Real-Time Updates**: Counter updates as video plays
- 🎨 **Claude-Inspired Design**: Clean, minimal, professional aesthetic

## 🚀 Quick Start (5 Minutes)

### Prerequisites
- Python 3.8+
- AWS Account (Free Tier works!)
- 5 minutes of your time

### Installation

```bash
# 1. Navigate to the project
cd rekognitionAPI

# 2. Run setup script
./setup.sh

# 3. Set AWS credentials
export AWS_ACCESS_KEY_ID=your_key
export AWS_SECRET_ACCESS_KEY=your_secret
export AWS_REGION=us-east-1
export AWS_BUCKET=streambet-demo-bucket

# 4. Create S3 bucket
aws s3 mb s3://streambet-demo-bucket

# 5. Set ElevenLabs API key (for voice commentary)
export ELEVENLABS_API_KEY=your_elevenlabs_key

# 6. Run the app
python app.py

# 7. Open browser - Main counter is now at root!
open http://localhost:5000/
```

**Routes:**
- `/` or `/counter` - Main live counter with commentary (Claude design)
- `/smart` - Smart detector
- `/widget` - Embeddable widget
- `/fake-twitch` - Demo page

### First Test

```bash
# Download a test video
./download_test_video.sh

# Or use the web interface:
# 1. Go to http://localhost:5000
# 2. Drag & drop any MP4 video
# 3. Click "Analyze Video"
# 4. See results in 30-60 seconds!
```

## 📁 Project Structure

```
rekognitionAPI/
├── app.py                          # Main Flask application
├── templates/
│   ├── simple_counter.html        # Main counter (Claude design) ✨ NEW
│   ├── smart_detector.html        # Smart detector interface
│   ├── counter_widget.html        # Embeddable widget
│   └── fake_twitch.html          # Demo page
├── requirements.txt               # Python dependencies
├── .env.example                   # Environment variables template
├── setup.sh                       # Automated setup script
├── start.sh                       # Quick start script
├── README.md                      # This file (main docs)
├── DEPLOYMENT_GUIDE.md            # Complete deployment guide ✨ NEW
├── CLAUDE_DESIGN_SYSTEM.md        # Design system documentation ✨ NEW
├── HACKATHON_README.md           # Hackathon submission guide
└── DEMO_GUIDE.md                 # Demo recording guide
```

## ✨ Features

### 🎥 Video Analysis
- Upload videos via drag-and-drop or file picker
- Supports MP4, MOV, AVI formats
- Real-time progress tracking
- Beautiful results visualization

### 🤖 AI Detection
- AWS Rekognition label detection
- Activity recognition (jumping, running, sports, etc.)
- Confidence scores for each detection
- Frame-accurate timestamps

### 🎯 Betting Integration
- Mock betting markets
- Auto-generated betting suggestions
- Odds calculation
- Resolution logic based on AI analysis

### 🎨 Modern UI
- Responsive design
- Gradient backgrounds
- Smooth animations
- Mobile-friendly

## 🔧 API Endpoints

### `GET /api/health`
Health check endpoint
```json
{
  "status": "healthy",
  "service": "StreamBet Recognition API",
  "version": "1.0.0-hackathon"
}
```

### `GET /api/bets`
Get available betting markets
```json
{
  "bets": [
    {
      "id": 1,
      "event": "Will streamer complete 10 backflips?",
      "odds": {"yes": 2.5, "no": 1.5},
      "pool": 5000,
      "status": "active"
    }
  ]
}
```

### `POST /api/analyze`
Analyze uploaded video
```bash
curl -X POST http://localhost:5000/api/analyze \
  -F "file=@test.mp4"
```

Response:
```json
{
  "status": "success",
  "total_labels": 15,
  "activity_labels": [
    {
      "label": "Jumping",
      "confidence": 92.5,
      "timestamps": [10.5, 20.1, 30.3],
      "category": "Sports and Fitness"
    }
  ],
  "betting_suggestion": {
    "suggestion": "Bet on number of jumps completed",
    "detected_activity": "Jumping",
    "confidence": 92.5
  }
}
```

### `POST /api/resolve`
Resolve bet based on analysis
```bash
curl -X POST http://localhost:5000/api/resolve \
  -H "Content-Type: application/json" \
  -d '{"bet_id": 1, "analysis": {...}}'
```

## 🧪 Testing

### Test the API
```bash
# Make sure server is running
python app.py

# In another terminal
python test_api.py
```

### Test with Video
```bash
# Download test video
./download_test_video.sh

# Upload via web interface
open http://localhost:5000
```

### Manual cURL Test
```bash
curl -X POST http://localhost:5000/api/analyze \
  -F "file=@uploads/test_exercise.mp4"
```

## 🎬 Demo Video Guide

See [DEMO_GUIDE.md](DEMO_GUIDE.md) for:
- Recording tips
- Script template
- Common issues
- Presentation talking points

## 🏆 Hackathon Submission

See [HACKATHON_README.md](HACKATHON_README.md) for:
- Detailed setup instructions
- Architecture overview
- AWS services used
- Submission checklist
- Future roadmap

## 💡 Use Cases

1. **Twitch Streamers**: "Will I complete 10 backflips?"
2. **Gaming**: "Will I win this match?"
3. **Sports**: "Will I score a goal?"
4. **Fitness**: "Will I do 100 pushups?"
5. **Creative**: "Will I finish this drawing in 30 minutes?"

## 🔮 Future Enhancements

- [ ] AWS Bedrock integration for AI agent decisions
- [ ] Real-time streaming with Kinesis Video Streams
- [ ] Custom Rekognition models for specific activities
- [ ] Multi-chain crypto payments (Solana, Base, Ethereum)
- [ ] Mobile apps (iOS/Android)
- [ ] Dispute resolution with human review
- [ ] Analytics dashboard

## 📊 Technical Stack

- **Backend**: Flask (Python 3.8+)
- **AI Vision**: AWS Rekognition (label detection, celebrity recognition)
- **AI Commentary**: Amazon Bedrock (Titan Text Express)
- **Text-to-Speech**: ElevenLabs API (voice synthesis)
- **Storage**: AWS S3 + Local file system
- **Frontend**: Vanilla JavaScript + Claude-inspired CSS
- **Design**: Claude Anthropic aesthetic (warm minimalism)

## 🐛 Troubleshooting

### AWS Credentials Error
```bash
# Check credentials
aws sts get-caller-identity

# Set environment variables
export AWS_ACCESS_KEY_ID=xxx
export AWS_SECRET_ACCESS_KEY=xxx
```

### Bucket Not Found
```bash
# Create bucket
aws s3 mb s3://your-bucket-name --region us-east-1

# Update environment
export AWS_BUCKET=your-bucket-name
```

### No Labels Detected
- Use videos with clear motion
- Try exercise/sports videos
- Lower confidence threshold in code (line 239)

### Analysis Timeout
- Use shorter videos (1-5 minutes)
- Check AWS service status
- Verify region settings

## 📚 Resources

- [AWS Rekognition Documentation](https://docs.aws.amazon.com/rekognition/)
- [AWS Bedrock Guide](https://docs.aws.amazon.com/bedrock/)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [AWS AI Agent Hackathon](https://awsaiagent.devpost.com/)

## 📈 Market Opportunity

- **$200B+** Global betting market
- **200M+** Twitch users
- **5%** Commission for streamers
- **Instant** Payouts for users

## 🤝 Contributing

This is a hackathon POC, but contributions are welcome!

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📄 License

MIT License - See LICENSE file for details

## 🎓 Learning Outcomes

Building this POC teaches:
- AWS Rekognition video analysis
- Flask API development
- Serverless architecture
- Computer vision applications
- Real-time data processing

## 🌟 Acknowledgments

- AWS for Rekognition and Bedrock services
- Pexels for free test videos
- The open-source community

---

## 📚 Documentation

### Main Guides
- **[README.md](README.md)** - Overview and quick start (you are here)
- **[DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)** - Complete deployment instructions
- **[CLAUDE_DESIGN_SYSTEM.md](CLAUDE_DESIGN_SYSTEM.md)** - Design system documentation

### Additional Resources
- **[HACKATHON_README.md](HACKATHON_README.md)** - Hackathon submission guide
- **[DEMO_GUIDE.md](DEMO_GUIDE.md)** - Demo recording tips
- `.env.example` - Environment variables template

### Quick Links
```bash
# View deployment guide
cat DEPLOYMENT_GUIDE.md

# View design system
cat CLAUDE_DESIGN_SYSTEM.md

# Check environment setup
cat .env.example
```

---

## 🚀 Ready to Deploy?

### Development
```bash
./start.sh
# Opens at http://localhost:5000/
```

### Production
See **[DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)** for:
- ✅ Local/Development deployment
- ✅ Production server setup (Gunicorn + systemd)
- ✅ Docker deployment
- ✅ AWS EC2 deployment with Nginx
- ✅ SSL certificate setup
- ✅ Monitoring and maintenance

---

## 🎨 Design System

The interface uses **Claude Anthropic inspired design**:
- 🎨 Warm beige/cream color palette (#F5F3EE background)
- ✨ Clean, minimal aesthetic
- 📝 Excellent typography (system fonts)
- 🎯 Subtle shadows and borders
- ⚡ Smooth, natural transitions

See **[CLAUDE_DESIGN_SYSTEM.md](CLAUDE_DESIGN_SYSTEM.md)** for complete design documentation.

---

**Built with ❤️ for the AWS AI Agent Global Hackathon 2025**

Questions? Issues? Check the documentation or open a GitHub issue!

**Good luck with your deployment! 🚀**
