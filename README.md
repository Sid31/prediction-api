# 🎮 StreamBet - AI Video Recognition POC

> **Hackathon-Ready Demo**: AI-powered live betting verification using AWS Rekognition

[![AWS](https://img.shields.io/badge/AWS-Rekognition-orange)](https://aws.amazon.com/rekognition/)
[![Python](https://img.shields.io/badge/Python-3.8+-blue)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-3.0-green)](https://flask.palletsprojects.com/)
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

# 5. Run the app
python app.py

# 6. Open browser
open http://localhost:5000
```

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
├── app.py                      # Main Flask application
├── templates/
│   └── index.html             # Beautiful web interface
├── requirements.txt           # Python dependencies
├── .env.example              # Environment variables template
├── setup.sh                  # Automated setup script
├── test_api.py              # API testing script
├── download_test_video.sh   # Get sample videos
├── README.md                # This file
├── HACKATHON_README.md      # Detailed hackathon guide
└── DEMO_GUIDE.md            # Demo recording guide
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

- **Backend**: Flask (Python)
- **AI/ML**: AWS Rekognition
- **Storage**: AWS S3
- **Frontend**: Vanilla JavaScript + Modern CSS
- **Future**: AWS Bedrock for AI agents

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

## 🚀 Ready to Demo?

1. **Setup**: `./setup.sh` (2 minutes)
2. **Configure**: Set AWS credentials (1 minute)
3. **Run**: `python app.py` (30 seconds)
4. **Test**: Upload a video (1 minute)
5. **Record**: Make your demo video (5 minutes)

**Total time to hackathon-ready demo: ~10 minutes**

---

**Built with ❤️ for the AWS AI Agent Global Hackathon 2025**

Questions? Issues? Open a GitHub issue or reach out!

**Good luck with your demo! 🎉**
