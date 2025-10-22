# 📦 S3 Video Setup Guide

## 🎯 Goal
Host your betting videos on AWS S3 for better performance and scalability.

---

## 🚀 Quick Setup (5 minutes)

### **Step 1: Create S3 Bucket**

```bash
# Using AWS CLI
aws s3 mb s3://streambet-videos --region us-east-1

# Or use AWS Console:
# https://s3.console.aws.amazon.com/s3/
```

### **Step 2: Upload Video**

```bash
# Upload test.mp4
aws s3 cp /path/to/test.mp4 s3://streambet-videos/test.mp4

# Or drag & drop in AWS Console
```

### **Step 3: Make Video Public**

#### Option A: Bucket Policy (Recommended)
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "PublicReadGetObject",
      "Effect": "Allow",
      "Principal": "*",
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::streambet-videos/*"
    }
  ]
}
```

Apply via:
```bash
# Save above JSON to policy.json
aws s3api put-bucket-policy --bucket streambet-videos --policy file://policy.json
```

#### Option B: Make Object Public
```bash
aws s3api put-object-acl --bucket streambet-videos --key test.mp4 --acl public-read
```

### **Step 4: Configure CORS**

Required for video playback in browser:

```json
[
  {
    "AllowedHeaders": ["*"],
    "AllowedMethods": ["GET", "HEAD"],
    "AllowedOrigins": ["*"],
    "ExposeHeaders": []
  }
]
```

Apply via:
```bash
# Save above JSON to cors.json
aws s3api put-bucket-cors --bucket streambet-videos --cors-configuration file://cors.json
```

### **Step 5: Update Environment**

Edit `.env`:
```bash
S3_BUCKET=streambet-videos
S3_VIDEO_URL=https://streambet-videos.s3.amazonaws.com/test.mp4
```

### **Step 6: Restart Server**

```bash
cd /Users/sidousan/prediction.chat/rekognitionAPI
./start.sh
```

---

## ✅ Verify Setup

### Test S3 URL:
```bash
curl -I https://streambet-videos.s3.amazonaws.com/test.mp4
```

Expected response:
```
HTTP/1.1 200 OK
Content-Type: video/mp4
Content-Length: 12345678
...
```

### Test in Browser:
```
http://localhost:5000/
```

Video should load from S3!

---

## 🔧 Troubleshooting

### **403 Forbidden**
```bash
# Check bucket policy
aws s3api get-bucket-policy --bucket streambet-videos

# Make object public
aws s3api put-object-acl --bucket streambet-videos --key test.mp4 --acl public-read
```

### **CORS Error**
```bash
# Check CORS configuration
aws s3api get-bucket-cors --bucket streambet-videos

# Reapply CORS
aws s3api put-bucket-cors --bucket streambet-videos --cors-configuration file://cors.json
```

### **Video Won't Play**
1. Check Content-Type is `video/mp4`
2. Try CloudFront CDN for better performance
3. Check browser console for errors

---

## 🚀 Production Setup

### **Use CloudFront CDN:**

1. **Create CloudFront Distribution:**
```bash
aws cloudfront create-distribution \
  --origin-domain-name streambet-videos.s3.amazonaws.com
```

2. **Update .env:**
```bash
S3_VIDEO_URL=https://d1234567890.cloudfront.net/test.mp4
```

**Benefits:**
- ✅ Faster global delivery
- ✅ HTTPS by default
- ✅ Caching reduces S3 costs
- ✅ DDoS protection

### **Use Signed URLs (Optional):**

For premium content:

```python
import boto3
from botocore.signers import CloudFrontSigner
from datetime import datetime, timedelta

def generate_signed_url(video_key):
    s3_client = boto3.client('s3')
    url = s3_client.generate_presigned_url(
        'get_object',
        Params={'Bucket': 'streambet-videos', 'Key': video_key},
        ExpiresIn=3600  # 1 hour
    )
    return url
```

---

## 💰 Cost Estimate

### **S3 Storage:**
- $0.023 per GB/month
- 1 GB video = $0.023/month

### **S3 Data Transfer:**
- First 100GB/month: Free
- Next 10TB: $0.09/GB
- 1000 views × 1GB = $90

### **CloudFront (Recommended):**
- First 1TB: $0.085/GB
- 1000 views × 1GB = $85
- **Plus caching savings!**

---

## 📁 File Structure

```
streambet-videos/
├── test.mp4              # Demo video
├── ishowspeed/
│   ├── backflip.mp4
│   ├── challenge.mp4
│   └── highlights.mp4
└── streamers/
    ├── streamer1/
    └── streamer2/
```

---

## 🔐 Security Best Practices

### **1. Separate Buckets:**
```
streambet-videos-public/   # Public betting videos
streambet-videos-private/  # Premium content
```

### **2. Block Public Access (For Private Bucket):**
```bash
aws s3api put-public-access-block \
  --bucket streambet-videos-private \
  --public-access-block-configuration \
  "BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true"
```

### **3. Enable Versioning:**
```bash
aws s3api put-bucket-versioning \
  --bucket streambet-videos \
  --versioning-configuration Status=Enabled
```

### **4. Enable Encryption:**
```bash
aws s3api put-bucket-encryption \
  --bucket streambet-videos \
  --server-side-encryption-configuration '{
    "Rules": [{
      "ApplyServerSideEncryptionByDefault": {
        "SSEAlgorithm": "AES256"
      }
    }]
  }'
```

---

## 🎬 Upload Script

Create `upload_video.sh`:

```bash
#!/bin/bash
VIDEO_FILE=$1
VIDEO_NAME=$(basename "$VIDEO_FILE")

echo "📤 Uploading $VIDEO_NAME to S3..."

aws s3 cp "$VIDEO_FILE" \
  s3://streambet-videos/"$VIDEO_NAME" \
  --content-type video/mp4 \
  --acl public-read

echo "✅ Uploaded!"
echo "🔗 URL: https://streambet-videos.s3.amazonaws.com/$VIDEO_NAME"
```

Usage:
```bash
chmod +x upload_video.sh
./upload_video.sh path/to/video.mp4
```

---

## 🌐 For Vercel Deployment

In your Vercel project:

### **Environment Variables:**
```bash
# Add in Vercel Dashboard → Settings → Environment Variables
S3_VIDEO_URL=https://streambet-videos.s3.amazonaws.com/test.mp4
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret
```

### **In `vercel.json`:**
```json
{
  "env": {
    "S3_VIDEO_URL": "@s3-video-url"
  }
}
```

---

## ✅ Success Checklist

- [ ] S3 bucket created
- [ ] Video uploaded
- [ ] Bucket policy applied (public read)
- [ ] CORS configured
- [ ] .env updated with S3 URL
- [ ] Server restarted
- [ ] Video plays on http://localhost:5000/
- [ ] Extension detects betting opportunity
- [ ] CloudFront CDN configured (optional)

---

## 🚀 Next Steps

1. **Upload more videos**
2. **Set up CloudFront CDN**
3. **Configure signed URLs for premium content**
4. **Set up lifecycle policies for old videos**
5. **Add video transcoding (HLS/DASH)**

---

**Your videos are now hosted on S3 for production-ready performance!** 📦✨
