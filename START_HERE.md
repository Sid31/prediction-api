# 🚀 START HERE - Test Your Video!

## ⚡ Super Quick Start (3 Steps)

You have `tets.mp4` ready to test! Here's how:

### Step 1: Set AWS Credentials (1 minute)

```bash
export AWS_ACCESS_KEY_ID=your_access_key_here
export AWS_SECRET_ACCESS_KEY=your_secret_key_here
export AWS_REGION=us-east-1
export AWS_BUCKET=streambet-test-bucket
```

**Don't have AWS credentials?**
1. Go to [AWS Console](https://console.aws.amazon.com/)
2. IAM → Users → Your User → Security Credentials
3. Create Access Key
4. Copy the keys

### Step 2: Run the Quick Test Script

```bash
./quick_test.sh
```

This will:
- ✅ Check everything is set up
- ✅ Install any missing dependencies
- ✅ Start the server
- ✅ Open your browser automatically

### Step 3: Upload and Analyze

1. Drag `tets.mp4` to the upload zone
2. Click "Analyze Video"
3. Wait 30-60 seconds
4. See the results! 🎉

---

## 🎯 Alternative: Manual Testing

### Start Server
```bash
python3 app.py
```

### Open Browser
Go to: http://localhost:5000

### Or Use cURL
```bash
# In another terminal
./test_video.sh
```

---

## 📊 What You'll See

After analysis, you'll get:
- 🏷️ **Detected Labels** - What's in the video
- 📍 **Timestamps** - When things happen
- 💯 **Confidence Scores** - How sure the AI is
- 🎯 **Betting Suggestions** - Auto-generated markets

---

## 🐛 Quick Fixes

### "AWS credentials not set"
```bash
export AWS_ACCESS_KEY_ID=xxx
export AWS_SECRET_ACCESS_KEY=xxx
```

### "Bucket not found"
Create it in AWS Console or:
```bash
aws s3 mb s3://streambet-test-bucket
```

### "Module not found"
```bash
pip3 install -r requirements.txt
```

---

## 📚 More Help

- **Detailed Setup**: See `TEST_INSTRUCTIONS.md`
- **Demo Recording**: See `DEMO_GUIDE.md`
- **Full Documentation**: See `README.md`

---

## 🎬 Ready to Record Demo?

Once testing works:
1. ✅ Start screen recording
2. ✅ Upload tets.mp4
3. ✅ Show the results
4. ✅ Highlight confidence scores
5. ✅ Submit to hackathon!

**Good luck! 🚀**
