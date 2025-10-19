# 🧪 Testing Instructions for tets.mp4

## ⚡ Quick Test (3 Steps)

### Step 1: Configure AWS Credentials (2 minutes)

You need AWS credentials to use Rekognition. Choose one option:

#### Option A: Environment Variables (Recommended for Testing)
```bash
export AWS_ACCESS_KEY_ID=your_access_key_here
export AWS_SECRET_ACCESS_KEY=your_secret_key_here
export AWS_REGION=us-east-1
export AWS_BUCKET=streambet-test-bucket
```

#### Option B: Create .env file
```bash
cp .env.example .env
# Edit .env with your credentials
nano .env
```

#### Where to Get AWS Credentials:
1. Go to [AWS Console](https://console.aws.amazon.com/)
2. Navigate to IAM → Users → Your User → Security Credentials
3. Click "Create Access Key"
4. Copy the Access Key ID and Secret Access Key

### Step 2: Create S3 Bucket

If you have AWS CLI installed:
```bash
aws s3 mb s3://streambet-test-bucket --region us-east-1
```

Or create manually in AWS Console:
1. Go to S3 in AWS Console
2. Click "Create bucket"
3. Name: `streambet-test-bucket`
4. Region: `us-east-1`
5. Click "Create"

### Step 3: Run the Test

#### Option A: Use the Web Interface (Recommended)
```bash
# Start the server
python3 app.py

# Open browser to http://localhost:5000
# Drag and drop tets.mp4
# Click "Analyze Video"
```

#### Option B: Use cURL Script
```bash
# Terminal 1: Start server
python3 app.py

# Terminal 2: Run test
./test_video.sh
```

#### Option C: Direct cURL Command
```bash
# Start server first
python3 app.py

# In another terminal
curl -X POST http://localhost:5000/api/analyze \
  -F "file=@tets.mp4"
```

## 📊 Expected Output

You should see:
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
  },
  "video_metadata": {
    "duration_seconds": 120.5,
    "format": "mp4"
  }
}
```

## ⏱️ Processing Time

- Upload: < 1 second
- S3 Transfer: 2-5 seconds
- Rekognition Analysis: 30-60 seconds
- **Total: ~35-70 seconds**

## 🐛 Troubleshooting

### "AWS Error: Access Denied"
```bash
# Check if credentials are set
echo $AWS_ACCESS_KEY_ID

# If empty, set them:
export AWS_ACCESS_KEY_ID=your_key
export AWS_SECRET_ACCESS_KEY=your_secret
```

### "Bucket not found"
```bash
# Create the bucket
# Replace with your bucket name from AWS_BUCKET
aws s3 mb s3://streambet-test-bucket
```

### "Module not found"
```bash
# Reinstall dependencies
pip3 install -r requirements.txt
```

### "Port already in use"
```bash
# Kill existing process
lsof -ti:5000 | xargs kill -9
```

### "Connection refused"
```bash
# Make sure server is running
python3 app.py
```

## 💡 Tips

1. **Use the web interface** - It's much nicer than cURL!
2. **Keep terminal open** - You'll see processing logs
3. **Wait patiently** - Analysis takes 30-60 seconds
4. **Check AWS costs** - Free tier covers 5,000 minutes/month

## 🎯 What to Look For

When testing, verify:
- ✅ Video uploads successfully
- ✅ Processing starts (see logs)
- ✅ Results appear in 30-60 seconds
- ✅ Confidence scores are shown
- ✅ Timestamps are accurate
- ✅ Betting suggestions make sense

## 📸 For Demo Video

If recording for hackathon:
1. Open http://localhost:5000
2. Start screen recording
3. Drag tets.mp4 to upload zone
4. Click "Analyze Video"
5. Show the loading state
6. Point out results when they appear
7. Highlight confidence scores and timestamps

## 🚀 Next Steps After Testing

Once it works:
1. ✅ Test with different videos
2. ✅ Record your demo video
3. ✅ Take screenshots
4. ✅ Submit to hackathon!

---

**Need help?** Check the other README files or the logs in the terminal where you ran `python3 app.py`
