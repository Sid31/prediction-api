# 🎥 AWS Rekognition Video Setup Guide

## Problem
Person Tracking and Face Search are failing with `AccessDeniedException` even though you have full Rekognition permissions.

## Root Cause
Rekognition Video features require an **IAM Service Role** that allows Rekognition to:
1. Access your S3 bucket
2. Publish completion notifications to SNS (optional but recommended)

## ✅ Quick Fix: Create Service Role

### Step 1: Create IAM Role via AWS Console

1. **Go to IAM Console**: https://console.aws.amazon.com/iam/home#/roles
2. **Click "Create role"**
3. **Select trusted entity**: 
   - Choose "AWS service"
   - Select "Rekognition" from the service list
4. **Add permissions**:
   - Search and attach: `AmazonRekognitionServiceRole`
   - Search and attach: `AmazonS3ReadOnlyAccess` (or use your existing S3 policy)
5. **Name the role**: `RekognitionServiceRole`
6. **Click "Create role"**

### Step 2: Get the Role ARN

After creating, you'll see something like:
```
arn:aws:iam::123456789012:role/RekognitionServiceRole
```

Copy this ARN.

### Step 3: Update .env File

Add to your `.env`:
```bash
REKOGNITION_ROLE_ARN=arn:aws:iam::YOUR-ACCOUNT-ID:role/RekognitionServiceRole
```

### Step 4: Restart Server

```bash
./start.sh
```

---

## 🚀 Alternative: Use Without Service Role (Simpler)

AWS Rekognition Video CAN work without SNS notifications, but requires different permissions.

### Option A: Add This Policy to Your IAM User

Create a custom policy with:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "rekognition:*"
            ],
            "Resource": "*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "iam:PassRole"
            ],
            "Resource": "arn:aws:iam::*:role/RekognitionServiceRole"
        }
    ]
}
```

### Option B: Simplify Code (Remove Video Features)

For your hackathon demo, you can:
1. Use **Label Detection only** (already working)
2. Use **Mock Mode** to simulate backflip detection
3. Show face recognition as "future feature"

---

## 💡 Recommended for Hackathon Demo

### Quick Demo Strategy:

1. **Enable Mock Mode** (instant, free, shows concept)
   ```bash
   echo "USE_MOCK_MODE=true" >> .env
   ./start.sh
   ```

2. **Show Real Label Detection** (working now)
   - Detects: Person, Face, Activities
   - Real AWS AI in action

3. **Explain Future Features**
   - "For production, we'll add Person Tracking for movement analysis"
   - "Face recognition will identify specific streamers"
   - "Custom models will detect specific tricks like backflips"

This way you have:
- ✅ Working demo (mock mode)
- ✅ Real AI (label detection)
- ✅ Clear roadmap (video features + custom models)

---

## 🎯 Choose Your Path:

### Path 1: Full Setup (30 minutes)
- Create IAM service role
- Configure SNS (optional)
- Get all features working
- **Best for**: Production deployment

### Path 2: Mock Mode (1 minute)
- Enable mock mode
- Show simulated results
- Explain production approach
- **Best for**: Hackathon demo

### Path 3: Label Detection Only (current)
- Use what's working now
- Focus on other features
- Add video features later
- **Best for**: MVP iteration

---

**For your hackathon, I recommend Path 2 (Mock Mode) to save time and AWS credits while still demonstrating the concept!**
