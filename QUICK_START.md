# ⚡ StreamBet POC - Ultra Quick Start

**Get from zero to working demo in 5 minutes!**

## 🎯 What You'll Build

A working AI-powered video recognition system that:
- Analyzes videos with AWS Rekognition
- Detects activities with timestamps
- Suggests betting markets automatically
- Shows results in a beautiful web interface

## 📋 Prerequisites

- ✅ Python 3.8+ installed
- ✅ AWS Account (free tier is fine)
- ✅ 5 minutes of time

## 🚀 Step-by-Step Setup

### 1️⃣ Install Dependencies (1 minute)

```bash
cd rekognitionAPI
pip install flask flask-cors boto3 werkzeug python-dotenv
```

### 2️⃣ Configure AWS (2 minutes)

**Get your AWS credentials:**
1. Go to AWS Console → IAM → Users → Your User → Security Credentials
2. Create Access Key
3. Copy the Access Key ID and Secret Access Key

**Set environment variables:**
```bash
export AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
export AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
export AWS_REGION=us-east-1
export AWS_BUCKET=streambet-demo-$(date +%s)
```

**Create S3 bucket:**
```bash
aws s3 mb s3://$AWS_BUCKET
```

### 3️⃣ Run the App (30 seconds)

```bash
python app.py
```

You should see:
```
🎮 StreamBet Recognition API - Hackathon POC
============================================================
📁 Upload folder: uploads
☁️  AWS Bucket: streambet-demo-xxxxx
🌍 Region: us-east-1
============================================================

 * Running on http://0.0.0.0:5000
```

### 4️⃣ Test It (1.5 minutes)

**Option A: Use Web Interface**
1. Open http://localhost:5000
2. Download a test video: `./download_test_video.sh`
3. Drag & drop the video
4. Click "Analyze Video"
5. Wait 30-60 seconds
6. See results! 🎉

**Option B: Use cURL**
```bash
# Download test video
curl -L "https://videos.pexels.com/video-files/4753994/4753994-hd_1920_1080_25fps.mp4" -o test.mp4

# Analyze it
curl -X POST http://localhost:5000/api/analyze -F "file=@test.mp4"
```

## ✅ Success Checklist

You should see:
- ✅ Web interface loads at http://localhost:5000
- ✅ Can upload videos via drag-and-drop
- ✅ Analysis completes in 30-60 seconds
- ✅ Results show detected labels with confidence scores
- ✅ Betting suggestions appear based on detected activities

## 🎬 Record Your Demo (5 minutes)

1. **Open Loom** (or screen recorder)
2. **Start recording**
3. **Show the interface** - "This is StreamBet"
4. **Upload a video** - Drag and drop
5. **Show results** - Point out confidence scores and timestamps
6. **Explain value** - "Enables transparent betting on live streams"
7. **Stop recording** - Keep it under 60 seconds!

## 🐛 Quick Fixes

### "AWS Error: Access Denied"
```bash
# Check credentials
aws sts get-caller-identity

# If it fails, reconfigure
aws configure
```

### "Bucket not found"
```bash
# Create it
aws s3 mb s3://streambet-demo-$(date +%s)
```

### "Module not found"
```bash
# Reinstall dependencies
pip install -r requirements.txt
```

### "Port already in use"
```bash
# Kill existing process
lsof -ti:5000 | xargs kill -9

# Or use different port
python app.py --port 5001
```

## 📊 Expected Results

When you analyze a video, you should get:

```json
{
  "status": "success",
  "total_labels": 15,
  "activity_labels": [
    {
      "label": "Jumping",
      "confidence": 92.5,
      "timestamps": [10.5, 20.1, 30.3]
    }
  ],
  "betting_suggestion": {
    "suggestion": "Bet on number of jumps completed",
    "confidence": 92.5
  }
}
```

## 🎯 What to Demo

1. **Upload Interface** - Show drag-and-drop
2. **Analysis Process** - Show loading state
3. **Results** - Highlight confidence scores
4. **Betting Integration** - Show suggested markets
5. **Business Value** - Explain the opportunity

## 📚 Next Steps

- ✅ Working demo? → Record your video!
- ✅ Need more details? → Read DEMO_GUIDE.md
- ✅ Submitting to hackathon? → Read HACKATHON_README.md
- ✅ Want to customize? → Edit app.py and templates/index.html

## 💡 Pro Tips

1. **Use short videos** (1-3 minutes) for faster testing
2. **Pick videos with clear motion** (exercise, sports, gaming)
3. **Test multiple times** to see different results
4. **Show confidence scores** in your demo - they're impressive!
5. **Explain the timestamps** - that's the killer feature

## 🎉 You're Ready!

If you can:
- ✅ Load the web interface
- ✅ Upload a video
- ✅ See analysis results
- ✅ Get betting suggestions

**You're ready to record your demo and submit!**

---

**Time to hackathon-ready demo: ~5 minutes**

**Questions?** Check the other README files or open an issue!

**Good luck! 🚀**
