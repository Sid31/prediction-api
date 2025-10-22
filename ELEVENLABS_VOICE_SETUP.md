# 🎙️ ElevenLabs Voice Commentary Setup

## Overview
Transform your AI-generated text commentary into **professional sports announcer voice** using ElevenLabs text-to-speech!

## Features
- ✅ **Real-time voice generation** from text commentary
- ✅ **Sports announcer style** voice (default: Adam)
- ✅ **Auto-play** in browser as video plays
- ✅ **High quality MP3** audio files
- ✅ **Synchronized** with video timestamps
- ✅ **Cached audio files** for efficiency

---

## Quick Setup (5 minutes)

### Step 1: Get ElevenLabs API Key

1. **Sign up** at https://elevenlabs.io/
2. **Free tier includes:**
   - 10,000 characters/month
   - High-quality voices
   - Commercial use

3. **Get your API key:**
   - Go to: https://elevenlabs.io/app/settings/api-keys
   - Click **"Create API Key"**
   - Copy the key

### Step 2: Add to .env

```bash
# Add to your .env file
ELEVENLABS_API_KEY=sk_your_api_key_here

# Optional: Choose a different voice
ELEVENLABS_VOICE_ID=pNInz6obpgDQGcFmaJgB
```

### Step 3: Install Dependencies

```bash
pip install elevenlabs>=1.0.0
```

### Step 4: Restart Server

```bash
python3 app.py
```

You should see:
```
🎙️ ElevenLabs TTS initialized - Voice commentary enabled!
🗣️ Using voice ID: pNInz6obpgDQGcFmaJgB
```

---

## How It Works

### Complete Flow:
```
Video Frame
    ↓
Rekognition (visual analysis)
    ↓
Whisper (audio transcription) [optional]
    ↓
Bedrock (generate commentary text)
    ↓
ElevenLabs (text → speech) 🎙️
    ↓
MP3 audio file
    ↓
Browser auto-plays commentary
```

### Example Output:
```
📝 Generating commentary...
🎙️ Commentary: "IShowSpeed is hyping up the crowd - something big is coming!"
🎤 Converting to speech: IShowSpeed is hyping up the crowd...
🔊 Voice audio saved: commentary_3000.mp3
🔊 Audio URL: /audio/commentary_3000.mp3
```

**Result:** Professional sports announcer voice plays in sync with video! 🎯

---

## Voice Options

### Pre-made Voices (Recommended for StreamBet)

| Voice Name | Voice ID | Style | Best For |
|------------|----------|-------|----------|
| **Adam** (Default) | `pNInz6obpgDQGcFmaJgB` | Deep, confident | Sports commentary |
| **Antoni** | `ErXwobaYiN019PkySvjV` | Well-rounded | General narration |
| **Arnold** | `VR6AewLTigWG4xSOukaG` | Strong, crisp | Action scenes |
| **Josh** | `TxGEqnHWrfWFTfGW9XjX` | Deep, resonant | Dramatic moments |
| **Sam** | `yoZ06aMxZJJ28mfd3POQ` | Raspy, dynamic | Energetic commentary |

### Browse More Voices:
- Visit: https://elevenlabs.io/voice-library
- Filter by: Language, Gender, Accent, Age
- Copy the Voice ID for your favorite

### How to Change Voice:

1. **Find voice ID** from voice library
2. **Update .env:**
   ```bash
   ELEVENLABS_VOICE_ID=your_chosen_voice_id
   ```
3. **Restart server**

---

## Voice Settings (Advanced)

Current settings (in `app.py`):
```python
VoiceSettings(
    stability=0.5,        # Consistency (0-1)
    similarity_boost=0.75, # Voice clarity (0-1)
    style=0.5,            # Expressiveness (0-1)
    use_speaker_boost=True # Enhance clarity
)
```

### Customize for Different Styles:

**More Dramatic:**
```python
stability=0.3,
style=0.8
```

**More Stable/Calm:**
```python
stability=0.8,
style=0.3
```

**Maximum Energy:**
```python
stability=0.4,
similarity_boost=0.8,
style=0.7
```

---

## Cost Breakdown

### ElevenLabs Pricing:

| Tier | Cost | Characters/Month | Use Case |
|------|------|------------------|----------|
| **Free** | $0 | 10,000 chars | Testing |
| **Starter** | $5/month | 30,000 chars | Light use |
| **Creator** | $22/month | 100,000 chars | Regular use |
| **Pro** | $99/month | 500,000 chars | Production |

### Character Count Estimates:
- Average commentary: **50-100 characters**
- 30-second video: **~5 commentary lines = 400 chars**
- 100 videos/day: **40,000 chars/day**

**Recommendation:** Creator plan ($22/month) for production use

### Cost Per Video:
- **Free tier:** ~25 videos/month
- **Starter:** ~75 videos/month  
- **Creator:** ~250 videos/month
- **Pro:** ~1,250 videos/month

---

## Audio File Management

### Storage Location:
```
/rekognitionAPI/audio_commentary/
└── commentary_*.mp3
```

### File Naming:
```
commentary_[timestamp_ms].mp3

Example: commentary_3000.mp3 (at 3.0 seconds)
```

### Cleanup Strategy:

**Option 1: Manual cleanup**
```bash
# Delete all audio files older than 24 hours
find audio_commentary -name "*.mp3" -mtime +1 -delete
```

**Option 2: Auto-cleanup (add to app.py)**
```python
import glob
import time

def cleanup_old_audio(hours=24):
    cutoff = time.time() - (hours * 3600)
    for file in glob.glob(f"{AUDIO_FOLDER}/*.mp3"):
        if os.path.getmtime(file) < cutoff:
            os.remove(file)
            
# Call on server start
cleanup_old_audio()
```

---

## Performance Impact

### Speed:
- **Text generation:** 1-2s (Bedrock)
- **Voice generation:** 0.5-1s (ElevenLabs)
- **Total added latency:** ~1.5s per commentary

### Optimization:
- Commentary generated **every 3 frames** (every ~3 seconds)
- Audio files **cached** and reused
- **Async generation** doesn't block video processing

---

## Troubleshooting

### ⚠️ "ElevenLabs initialization failed"

**Check:**
1. API key is correct in `.env`
2. API key is active (not expired)
3. `elevenlabs` package installed:
   ```bash
   pip install elevenlabs
   ```

### ⚠️ "Text-to-speech failed"

**Common causes:**
1. **Quota exceeded** - Check usage at elevenlabs.io
2. **Invalid voice ID** - Verify from voice library
3. **Network issues** - Check internet connection

**Solution:**
- Upgrade plan if quota exceeded
- Use default voice ID: `pNInz6obpgDQGcFmaJgB`

### ⚠️ Audio not playing in browser

**Check:**
1. Commentary toggle is **enabled** (✅ Enable Live Commentary)
2. Browser allows **autoplay** (check console for errors)
3. Audio file exists in `/audio/` folder
4. File permissions are correct

**Fix autoplay issues:**
- Chrome: chrome://settings/content/sound
- Allow sound for localhost

### ⚠️ Voice sounds robotic/weird

**Adjust settings** in `app.py`:
```python
VoiceSettings(
    stability=0.6,  # Increase for more consistency
    similarity_boost=0.8,  # Increase for better voice match
)
```

---

## Frontend Integration

### HTML Structure:
```html
<div id="commentary-box">
    <div id="commentary-text"></div>
</div>
```

### JavaScript (already implemented):
```javascript
if (data.commentary) {
    commentaryText.textContent = `"${data.commentary}"`;
    
    // Auto-play voice
    if (data.audio_url) {
        const audio = new Audio(data.audio_url);
        audio.volume = 0.8;
        audio.play();
    }
}
```

### Customize Audio:
```javascript
const audio = new Audio(data.audio_url);
audio.volume = 0.6;      // Adjust volume (0.0 - 1.0)
audio.playbackRate = 1.1; // Speed up slightly
audio.play();
```

---

## Production Best Practices

### 1. **Error Handling**
✅ Graceful fallback if TTS fails
✅ Show text commentary even without voice
✅ Log errors for monitoring

### 2. **Caching**
- Cache audio files for duplicate commentary
- Use Redis for distributed systems
- Clean up old files regularly

### 3. **Rate Limiting**
- Monitor ElevenLabs usage
- Implement client-side cooldown
- Queue requests during high traffic

### 4. **Quality Control**
- Test different voices for your use case
- A/B test voice settings
- Collect user feedback

---

## API Reference

### Backend Function:
```python
def text_to_speech(text, timestamp):
    """
    Convert text to speech using ElevenLabs
    
    Args:
        text (str): Commentary text to convert
        timestamp (float): Video timestamp in seconds
        
    Returns:
        str: Audio file URL or None if failed
    """
```

### Response Format:
```json
{
    "type": "detection",
    "timestamp": 3.5,
    "commentary": "IShowSpeed at the theme park!",
    "audio_url": "/audio/commentary_3500.mp3"
}
```

---

## Examples

### Use Case 1: Sports Betting
```
Commentary: "He's lining up the shot... and GOAL!"
Voice: Energetic sports announcer
Settings: stability=0.4, style=0.8
```

### Use Case 2: Gaming Stream
```
Commentary: "IShowSpeed just hit an insane clutch!"
Voice: Hype caster
Settings: stability=0.3, style=0.9
```

### Use Case 3: Educational Content
```
Commentary: "Notice the technique here - perfect form"
Voice: Professional narrator
Settings: stability=0.7, style=0.4
```

---

## Next Steps

1. ✅ **Get ElevenLabs API key**
2. ✅ **Add to .env file**
3. ✅ **Install elevenlabs package**
4. ✅ **Restart server and test!**
5. 🎯 **Choose your favorite voice**
6. 🎯 **Customize voice settings**
7. 🎯 **Deploy to production**

---

## Resources

- **ElevenLabs Dashboard:** https://elevenlabs.io/app
- **Voice Library:** https://elevenlabs.io/voice-library
- **API Docs:** https://elevenlabs.io/docs
- **Python SDK:** https://github.com/elevenlabs/elevenlabs-python

---

**Your AI commentary now speaks! 🎙️🚀**

Experience the future of live sports betting with professional voice commentary powered by ElevenLabs!
