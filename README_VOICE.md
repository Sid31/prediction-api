# 🎙️ StreamBet Voice Commentary - Complete Setup

## ✅ What's Been Added

Your StreamBet counter now features **professional sports announcer voice** powered by ElevenLabs!

```
Text Commentary → ElevenLabs AI Voice → Auto-play in Browser 🔊
```

---

## 🚀 Quick Start (2 Minutes)

### Step 1: Get Free API Key

1. Visit: **https://elevenlabs.io/**
2. Sign up (Free: 10,000 chars/month = ~25 videos)
3. Go to: **https://elevenlabs.io/app/settings/api-keys**
4. Click "Create API Key"
5. Copy your key

### Step 2: Add to .env

```bash
# Open your .env file and add:
ELEVENLABS_API_KEY=sk_your_actual_api_key_here

# Optional: Change voice (default is Adam - sports announcer)
ELEVENLABS_VOICE_ID=pNInz6obpgDQGcFmaJgB
```

### Step 3: Restart

```bash
# Stop current server (Ctrl+C)
python3 app.py

# Look for this output:
# 🎙️ ElevenLabs TTS initialized - Voice commentary enabled!
# 🗣️ Using voice ID: pNInz6obpgDQGcFmaJgB
```

### Step 4: Test!

```bash
# 1. Open browser
http://localhost:5000/counter

# 2. Check the box
✅ 🎙️ Enable Live Commentary

# 3. Upload a video

# 4. Listen! 🔊
Professional voice announces the action!
```

---

## 🎯 What You'll Experience

### Without Voice (Before):
```
[Text appears on screen]
"IShowSpeed at the theme park! Something exciting!"
```

### With Voice (Now):
```
[Professional sports announcer speaks]
🔊 "IShowSpeed at the theme park! Something exciting!"
```

**It's like ESPN commentary for your streams!** 🏆

---

## 💰 Cost: FREE to Start

### Free Tier (Perfect for Testing):
- ✅ 10,000 characters/month
- ✅ ~25 videos (30 seconds each)
- ✅ High-quality voices
- ✅ Commercial use allowed

### Paid Plans (When You Scale):
- **$5/month:** 75 videos
- **$22/month:** 250 videos (recommended)
- **$99/month:** 1,250 videos

**Test for free, upgrade when ready!**

---

## 🎤 Voice Options

### Current Default: Adam
- **Style:** Deep, confident sports commentator
- **Perfect for:** Action commentary, sports betting
- **ID:** `pNInz6obpgDQGcFmaJgB`

### Try These Popular Voices:

| Voice Name | Style | Best For |
|------------|-------|----------|
| **Sam** | Raspy, dynamic | Hype moments |
| **Josh** | Deep, dramatic | Intense action |
| **Antoni** | Professional | General narration |

**Browse 100+ voices:** https://elevenlabs.io/voice-library

**To change voice:**
```bash
# In .env, update:
ELEVENLABS_VOICE_ID=your_chosen_voice_id
```

---

## 📊 System Architecture

```
┌─────────────────┐
│  Video Upload   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Frame Analysis  │ (OpenCV + Rekognition)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Audio Transcr.  │ (Whisper - Optional)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Text Commentary │ (Bedrock AI)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ 🎙️ VOICE GEN   │ ← NEW! (ElevenLabs)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  MP3 Audio      │ → Auto-play in Browser 🔊
└─────────────────┘
```

---

## ⚡ Performance

### Speed Impact:
- Voice generation: **+0.5-1 second** per commentary
- Generated every **3 frames** (~3 seconds)
- **Doesn't block** video processing

### File Size:
- Each MP3: ~50KB
- 30-second video: ~250KB total audio
- Auto-cleanup after 24 hours

---

## 🐛 Troubleshooting

### ❌ No voice playing?

**Check Console Output:**
```bash
# Should see:
🎤 Converting to speech: IShowSpeed at...
🔊 Voice audio saved: commentary_3000.mp3

# If you see:
💡 Set ELEVENLABS_API_KEY in .env to enable voice commentary
# → You need to add API key to .env
```

**Check Browser Console:**
```javascript
// Should see:
🔊 Playing voice commentary: /audio/commentary_3000.mp3

// If "Audio play failed":
// → Enable autoplay in browser settings
```

### ❌ "ElevenLabs initialization failed"

**Solutions:**
1. Verify API key is correct (no extra spaces)
2. Check API key is active at elevenlabs.io
3. Ensure elevenlabs package installed: `pip3 install elevenlabs`

### ❌ Voice sounds weird/robotic

**Adjust settings in `app.py`:**
```python
VoiceSettings(
    stability=0.6,         # Increase for consistency
    similarity_boost=0.8,  # Increase for clarity
)
```

### ❌ "Quota exceeded"

**Solutions:**
1. Check usage: https://elevenlabs.io/app/usage
2. Upgrade plan or wait for monthly reset
3. Reduce frequency: Change `idx % 3` to `idx % 5` in app.py

---

## 📁 Project Structure

```
/rekognitionAPI/
├── app.py                           ← ElevenLabs integration
├── audio_commentary/                ← NEW! MP3 files stored here
│   ├── commentary_1000.mp3
│   └── commentary_4500.mp3
├── requirements.txt                 ← Added: elevenlabs>=1.0.0
├── .env                             ← Add: ELEVENLABS_API_KEY
├── templates/
│   └── simple_counter.html          ← Auto-play functionality
├── ELEVENLABS_VOICE_SETUP.md       ← Detailed setup guide
├── VOICE_COMMENTARY_SUMMARY.md     ← Feature overview
└── README_VOICE.md                  ← This file
```

---

## 🎓 Advanced Tips

### 1. Customize Voice Character

**More Dramatic/Hype:**
```python
# In app.py, text_to_speech function:
VoiceSettings(
    stability=0.3,  # Less consistent = more varied
    style=0.9       # Maximum expressiveness
)
```

**More Calm/Professional:**
```python
VoiceSettings(
    stability=0.8,  # Very consistent
    style=0.2       # Subdued tone
)
```

### 2. Adjust Browser Volume

```javascript
// In simple_counter.html:
const audio = new Audio(data.audio_url);
audio.volume = 0.6;  // 60% volume
audio.play();
```

### 3. Speed Up Voice

```javascript
audio.playbackRate = 1.2;  // 20% faster
```

### 4. Add Volume Controls

```html
<!-- Add slider to page -->
<input type="range" id="volume" min="0" max="100" value="80">

<script>
const volumeSlider = document.getElementById('volume');
volumeSlider.addEventListener('change', (e) => {
    audio.volume = e.target.value / 100;
});
</script>
```

---

## 📚 Documentation Files

| File | Purpose |
|------|---------|
| **README_VOICE.md** | This quick start guide |
| **ELEVENLABS_VOICE_SETUP.md** | Complete setup & customization |
| **VOICE_COMMENTARY_SUMMARY.md** | Technical implementation details |
| **AUDIO_SETUP.md** | Whisper audio transcription setup |
| **AUDIO_INTEGRATION_SUMMARY.md** | Full audio analysis overview |

---

## 🎯 Use Cases

### StreamBet Live Betting:
```
🎬 Video: Streamer attempting backflip
🎤 Audio: "Let's go!"
🗣️ Voice: "He's going for it... and he NAILED IT! Incredible!"
```

### Gaming Highlights:
```
🎬 Video: IShowSpeed detected, crowd visible
🎤 Audio: Crowd cheering
🗣️ Voice: "IShowSpeed is absolutely losing his mind! The crowd goes wild!"
```

### Sports Analysis:
```
🎬 Video: Basketball court, person jumping
🎤 Audio: Ball bouncing
🗣️ Voice: "He's lining up the shot... from downtown... SWISH!"
```

---

## ✅ Final Checklist

- [ ] **Get API key** from elevenlabs.io
- [ ] **Add to .env** file
- [ ] **Restart server** and check logs
- [ ] **Test with video** upload
- [ ] **Hear voice** commentary
- [ ] **Try different voices** (optional)
- [ ] **Adjust settings** to your preference
- [ ] **Deploy to production** 🚀

---

## 🤝 Support

### Resources:
- **ElevenLabs Dashboard:** https://elevenlabs.io/app
- **Voice Library:** https://elevenlabs.io/voice-library  
- **API Documentation:** https://elevenlabs.io/docs
- **Usage Tracking:** https://elevenlabs.io/app/usage

### Need Help?
1. Check console logs (server & browser)
2. Read ELEVENLABS_VOICE_SETUP.md for details
3. Verify API key at elevenlabs.io

---

## 🎉 You're Ready!

**Steps to go live:**

1. ✅ Dependencies installed (`pip3 install elevenlabs`)
2. ✅ Code updated (app.py + simple_counter.html)
3. ✅ Audio folder created
4. ⏳ **Just need YOUR API key!**

**Get your key now:** https://elevenlabs.io/app/settings/api-keys

**Then add to .env and restart!** 🚀

---

**Your StreamBet platform now speaks with a professional voice! 🎙️🔥**

Experience the future of live stream betting with AI-powered visual analysis + voice commentary!
