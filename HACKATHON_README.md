# 🎮 StreamBet - AI Video Recognition POC

**Hackathon Submission: AWS AI Agent Global Hackathon 2025**

## 🎯 Project Overview

StreamBet is an AI-powered live betting platform that uses AWS Rekognition to analyze video streams in real-time, detect specific events (like backflips, game wins, etc.), and automatically resolve bets with high accuracy. This POC demonstrates the core video recognition and betting resolution pipeline.

### The Problem
Traditional betting platforms rely on manual verification, which is slow, expensive, and prone to disputes. Live streamers want to engage their audience with real-time predictions, but lack trustworthy, automated verification systems.

### Our Solution
- **AWS Rekognition** analyzes video streams to detect activities with timestamps and confidence scores
- **AI Agent Logic** (Bedrock-ready) processes detection results to auto-resolve bets
- **Transparent Verification** shows exact timestamps and confidence levels to all participants
- **Instant Payouts** triggered automatically when events are verified

## 🏗️ Architecture

```
User Uploads Video → Flask API → AWS S3 → Rekognition Analysis
                                              ↓
                                    Labels + Timestamps + Confidence
                                              ↓
                                    AI Decision Logic (Mock Bedrock Agent)
                                              ↓
                                    Bet Resolution → Payout Trigger
```

## ✨ Features Demonstrated

- ✅ **Video Upload & Processing**: Drag-and-drop interface for video analysis
- ✅ **AWS Rekognition Integration**: Real-time label detection with confidence scores
- ✅ **Activity Detection**: Identifies jumping, running, sports, and other activities
- ✅ **Timestamp Tracking**: Frame-accurate event detection
- ✅ **Betting Interface**: Mock betting markets with odds calculation
- ✅ **Auto-Resolution**: AI-powered bet settlement based on analysis
- ✅ **Beautiful UI**: Modern, responsive interface with real-time updates

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- AWS Account (Free Tier works!)
- AWS CLI configured OR environment variables set

### 1. Install Dependencies
```bash
cd rekognitionAPI
pip install -r requirements.txt
```

### 2. Configure AWS Credentials

**Option A: Environment Variables**
```bash
export AWS_ACCESS_KEY_ID=your_access_key
export AWS_SECRET_ACCESS_KEY=your_secret_key
export AWS_REGION=us-east-1
export AWS_BUCKET=your-s3-bucket-name
```

**Option B: AWS CLI**
```bash
aws configure
```

**Option C: .env File**
```bash
cp .env.example .env
# Edit .env with your credentials
```

### 3. Create S3 Bucket
```bash
aws s3 mb s3://streambet-demo-bucket --region us-east-1
```

### 4. Set Up IAM Permissions
Your AWS user needs these permissions:
- `AmazonRekognitionFullAccess`
- `AmazonS3FullAccess`

### 5. Run the Application
```bash
python app.py
```

Open browser to: **http://localhost:5000**

## 📹 Testing the Demo

### Option 1: Use Sample Video
1. Download a test video (5-min workout, sports, or gaming clip)
2. Visit http://localhost:5000
3. Drag & drop the video or click to upload
4. Click "Analyze Video"
5. Wait 30-60 seconds for results
6. See detected activities with timestamps and confidence scores

### Option 2: Quick Test with cURL
```bash
curl -X POST http://localhost:5000/api/analyze \
  -F "file=@test.mp4"
```

### Expected Output
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

## 🎬 Demo Video Script

**For Hackathon Submission (30-60 seconds):**

1. **Opening (5s)**: "StreamBet uses AWS Rekognition to verify live betting events automatically"
2. **Upload (10s)**: Show drag-and-drop video upload interface
3. **Analysis (15s)**: Show loading state, then results appearing with labels and timestamps
4. **Betting (10s)**: Show betting interface with suggested markets based on detected activities
5. **Resolution (10s)**: Show auto-resolution with confidence score and payout trigger
6. **Closing (10s)**: "Transparent, instant, AI-powered betting verification"

## 🔧 Technical Stack

- **Backend**: Flask (Python)
- **AI/ML**: AWS Rekognition for video analysis
- **Storage**: AWS S3 for temporary video storage
- **Frontend**: Vanilla JavaScript with modern CSS
- **Future**: AWS Bedrock for AI agent decision-making

## 📊 API Endpoints

### `GET /api/health`
Health check endpoint

### `GET /api/bets`
Get available betting markets

### `POST /api/analyze`
Upload and analyze video
- **Input**: Multipart form with video file
- **Output**: Labels, timestamps, confidence scores, betting suggestions

### `POST /api/resolve`
Resolve bet based on analysis results
- **Input**: `{ bet_id, analysis }`
- **Output**: Resolution outcome and payout status

## 🎯 Use Cases

1. **Twitch Streamers**: "Will I complete 10 backflips in 5 minutes?"
2. **Gaming**: "Will I win this match?"
3. **Sports**: "Will I score a goal in this game?"
4. **Fitness**: "Will I do 100 pushups?"
5. **Creative**: "Will I finish this drawing in 30 minutes?"

## 🔮 Future Enhancements

- [ ] **AWS Bedrock Integration**: Replace mock resolution with AI agent
- [ ] **Real-time Streaming**: Use Kinesis Video Streams for live analysis
- [ ] **Custom Models**: Train Rekognition for specific activities (backflips, tricks)
- [ ] **Multi-chain Payments**: Integrate crypto wallets (Solana, Base, Ethereum)
- [ ] **Mobile App**: iOS/Android apps for streamers and bettors
- [ ] **Dispute Resolution**: Human review queue for low-confidence detections
- [ ] **Analytics Dashboard**: Track betting patterns and popular events

## 💡 Why This Matters

- **$200B+ Global Betting Market**: Massive opportunity for innovation
- **200M+ Twitch Users**: Built-in audience of engaged viewers
- **Creator Economy**: Streamers earn 5% commission on bets
- **Trust & Transparency**: AI verification eliminates disputes
- **Instant Settlement**: No more waiting 24-48 hours for payouts

## 🏆 Hackathon Submission Checklist

- [x] Working POC with AWS Rekognition
- [x] Clean, documented code
- [x] Beautiful UI/UX
- [x] README with setup instructions
- [x] Demo-ready in <5 minutes
- [ ] Record demo video (30-60s)
- [ ] Deploy to public URL (optional)
- [ ] Submit to Devpost

## 📝 AWS Services Used

1. **Amazon Rekognition**: Video label detection with confidence scores
2. **Amazon S3**: Temporary video storage for processing
3. **Future: Amazon Bedrock**: AI agent for decision-making and bet resolution

## 🤝 Team & Contact

**Project**: StreamBet  
**Category**: AI Agents for Real-time Decision Making  
**Hackathon**: AWS AI Agent Global Hackathon 2025  
**Submission Deadline**: October 20, 2025

## 📄 License

MIT License - Feel free to use this POC for learning and hackathons!

---

## 🎥 Sample Test Videos

Download free test videos from:
- **Pexels**: https://www.pexels.com/search/videos/exercise/
- **Pixabay**: https://pixabay.com/videos/search/sports/
- **YouTube**: Download short clips with `yt-dlp`

Look for videos with:
- Clear motion (jumping, running, sports)
- Good lighting and camera angles
- 1-5 minutes duration
- MP4 format

## 🐛 Troubleshooting

### "AWS Error: Access Denied"
- Check your AWS credentials are correct
- Verify IAM permissions include Rekognition and S3 access
- Make sure S3 bucket exists and is in the same region

### "Analysis Timeout"
- Video might be too long (>10 minutes)
- Check AWS service status
- Increase timeout in code if needed

### "No Labels Detected"
- Video quality might be too low
- Try a video with clearer motion/activities
- Lower `MinConfidence` threshold in code (currently 60)

### "Import Error: boto3"
- Run `pip install -r requirements.txt`
- Make sure you're in the correct virtual environment

## 🎓 Learning Resources

- [AWS Rekognition Documentation](https://docs.aws.amazon.com/rekognition/)
- [AWS Bedrock Agent Guide](https://docs.aws.amazon.com/bedrock/)
- [Flask Documentation](https://flask.palletsprojects.com/)

---

**Built with ❤️ for the AWS AI Agent Global Hackathon 2025**
