# 🎤 Audio Analysis with Whisper Setup Guide

## Overview
Your StreamBet counter now includes **audio transcription** using AWS SageMaker's Whisper Large V3 Turbo model. This adds audio context to AI commentary for more engaging live updates!

## Features Added
✅ **Audio extraction** from video at commentary timestamps  
✅ **Speech-to-text** using Whisper Large V3 Turbo  
✅ **Context-aware commentary** that references what was said  
✅ **Efficient SageMaker inference** (no local GPU needed)  

---

## Setup Options

### Option 1: Quick Deploy via AWS Console (Recommended)

1. **Go to SageMaker Console:**
   ```
   https://ap-southeast-2.console.aws.amazon.com/sagemaker/home?region=ap-southeast-2#/jumpstart
   ```

2. **Search for Whisper:**
   - In JumpStart search bar, type: `whisper-large-v3-turbo`
   - Click on the model card

3. **Deploy the Model:**
   - Click **"Deploy"** button
   - Choose instance type: `ml.g5.xlarge` (recommended for speed)
   - Click **"Deploy"**
   - Wait 5-10 minutes for deployment

4. **Copy Endpoint Name:**
   - Once deployed, go to: **Inference > Endpoints**
   - Copy your endpoint name (e.g., `huggingface-asr-whisper-xxx`)

5. **Update .env file:**
   ```bash
   WHISPER_ENDPOINT_NAME=your-endpoint-name-here
   ```

6. **Restart server:**
   ```bash
   python3 app.py
   ```

---

### Option 2: Deploy via Python Script

```bash
# Edit the script to add your SageMaker execution role
python3 deploy_whisper_endpoint.py
```

**Note:** This requires proper IAM setup. Use Console method if unsure.

---

### Option 3: Skip Audio (Commentary still works!)

If you don't want audio analysis, just **don't set `WHISPER_ENDPOINT_NAME`** in .env. The system will work fine without it using visual analysis only.

---

## How It Works

### 1. Video Processing Flow
```
Video Frame → Rekognition Labels
     ↓
Audio Segment → Whisper Transcription
     ↓
Combined Context → Bedrock Commentary
```

### 2. Audio Extraction
- Extracts **5-second audio clips** around commentary timestamps
- Converts to WAV format for Whisper
- Temporary files cleaned up automatically

### 3. Transcription
- Sends audio to SageMaker Whisper endpoint
- Returns text transcription
- Auto-detects language

### 4. Enhanced Commentary
The AI now sees:
- Visual labels (from Rekognition)
- Who's in frame (celebrity detection)
- What was said (from Whisper)
- Previous context (last 3 frames)

---

## Example Output

**Without Audio:**
```
🎙️ Commentary: "IShowSpeed at the theme park! Exciting action happening!"
```

**With Audio:**
```
🎤 Heard: "Let's go! I'm about to do something crazy!"
🎙️ Commentary: "IShowSpeed is hyping up the crowd - something big is about to happen!"
```

---

## Cost Breakdown

### SageMaker Endpoint Costs
| Instance Type | Cost/Hour | Use Case |
|--------------|-----------|----------|
| `ml.g5.xlarge` | ~$1.00 | Production (fast) |
| `ml.g5.2xlarge` | ~$2.00 | High volume |
| `ml.m5.xlarge` | ~$0.23 | Testing (CPU only, slower) |

**Cost Saving Tips:**
- ✅ Delete endpoint when not in use
- ✅ Use `ml.g5.xlarge` (best price/performance)
- ✅ Only transcribe every 3rd frame (already implemented)

**Monthly estimate:** 
- 8 hours/day usage = ~$240/month
- On-demand only = Pay per use

---

## IAM Permissions Required

Add to your IAM user/role:
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "sagemaker:InvokeEndpoint",
        "sagemaker:DescribeEndpoint"
      ],
      "Resource": "arn:aws:sagemaker:ap-southeast-2:*:endpoint/*whisper*"
    }
  ]
}
```

---

## Troubleshooting

### ⚠️ "Whisper endpoint not configured"
- Add `WHISPER_ENDPOINT_NAME` to .env
- Check endpoint is deployed and "InService"

### ⚠️ "Audio extraction failed"
- Install moviepy: `pip install moviepy`
- Check video has audio track
- Check FFmpeg is installed

### ⚠️ "SageMaker transcription failed"
- Verify endpoint name is correct
- Check IAM permissions for SageMaker
- Verify endpoint is in `ap-southeast-2` region

### ⚠️ Endpoint costs too high
- Delete endpoint when not in use:
  ```bash
  aws sagemaker delete-endpoint --endpoint-name YOUR_ENDPOINT_NAME
  ```
- Re-deploy when needed (takes 5-10 min)

---

## Performance Impact

### Speed
- **Without audio:** ~0.5s per frame
- **With audio:** ~1.5s per frame (transcription adds 1s)
- **Overall:** +50% processing time, but much better commentary!

### Frequency
- Audio transcribed every **3 frames** (every ~3 seconds)
- Adjustable in code: `if idx % 3 == 0`

---

## Model Details

**Whisper Large V3 Turbo**
- 🏢 Provider: OpenAI via Hugging Face
- 📦 Model Size: 1.5B parameters
- 🌍 Languages: 99+ languages
- ⚡ Speed: ~5x faster than Whisper V3
- 🎯 Accuracy: State-of-the-art ASR

**Model ARN:**
```
arn:aws:sagemaker:ap-southeast-2:aws:hub-content/SageMakerPublicHub/Model/huggingface-asr-whisper-large-v3-turbo/1.1.12
```

---

## Next Steps

1. ✅ Deploy Whisper endpoint (Option 1 recommended)
2. ✅ Add endpoint name to .env
3. ✅ Install moviepy: `pip install moviepy`
4. ✅ Restart server and test!

**Your commentary will now be audio-aware!** 🎙️🚀
