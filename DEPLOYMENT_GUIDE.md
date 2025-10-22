# 🚀 StreamBet Recognition API - Deployment Guide

## Overview
Complete deployment guide for the StreamBet AI-powered video analysis and live commentary system with Claude Anthropic inspired design.

---

## 📋 Prerequisites

### System Requirements
- **Python**: 3.8+ (recommended 3.11)
- **Node.js**: 16+ (for frontend build tools if needed)
- **OS**: Linux (Ubuntu 20.04+), macOS, or Windows with WSL2
- **RAM**: Minimum 2GB, recommended 4GB+
- **Storage**: 5GB+ for dependencies and video storage

### AWS Services Required
1. **AWS Rekognition**: For video analysis
2. **Amazon Bedrock**: For AI commentary (Titan Text)
3. **IAM User**: With appropriate permissions

### API Keys Needed
1. **ElevenLabs API Key**: For text-to-speech voice commentary
2. **AWS Access Key ID & Secret**: For AWS services

---

## 🏗️ Architecture

```
┌─────────────────┐
│   Frontend      │
│  (Flask HTML)   │  → Serves at http://localhost:5000/
└────────┬────────┘
         │
    ┌────▼────┐
    │  Flask  │
    │ Backend │  → Port 5000
    └────┬────┘
         │
    ┌────▼─────────────────────┐
    │  AWS Services            │
    │  - Rekognition (labels)  │
    │  - Bedrock (commentary)  │
    └──────────────────────────┘
         │
    ┌────▼─────────────────────┐
    │  ElevenLabs API          │
    │  - Text-to-Speech        │
    └──────────────────────────┘
```

---

## 🔧 Part 1: Backend Setup

### Step 1: Clone Repository
```bash
cd /Users/sidousan/prediction.chat/rekognitionAPI
# or wherever your project is located
```

### Step 2: Create Virtual Environment
```bash
# Create venv
python3 -m venv venv

# Activate (macOS/Linux)
source venv/bin/activate

# Activate (Windows)
venv\Scripts\activate
```

### Step 3: Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

**Required packages:**
```txt
flask==3.0.0
flask-cors==4.0.0
boto3==1.34.0
opencv-python==4.9.0.80
Pillow==10.2.0
python-dotenv==1.0.0
requests==2.31.0
elevenlabs==0.2.27
```

### Step 4: Configure Environment Variables

Create `.env` file:
```bash
cp .env.example .env
nano .env  # or use your preferred editor
```

Add your credentials:
```bash
# AWS Configuration
AWS_ACCESS_KEY_ID=your_aws_access_key_here
AWS_SECRET_ACCESS_KEY=your_aws_secret_key_here
AWS_REGION=us-east-1

# ElevenLabs Configuration
ELEVENLABS_API_KEY=your_elevenlabs_api_key_here
ELEVENLABS_VOICE_ID=ErXwobaYiN019PkySvjV  # Adam (default)

# Flask Configuration
FLASK_ENV=production
FLASK_DEBUG=False
SECRET_KEY=your_random_secret_key_here
```

**Generate secret key:**
```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

### Step 5: AWS IAM Permissions

Create IAM user with these permissions:
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "rekognition:DetectLabels",
                "rekognition:RecognizeCelebrities",
                "rekognition:DetectFaces",
                "rekognition:CreateCollection",
                "rekognition:SearchFacesByImage"
            ],
            "Resource": "*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "bedrock:InvokeModel"
            ],
            "Resource": "arn:aws:bedrock:*:*:model/*"
        }
    ]
}
```

### Step 6: Create Required Directories
```bash
mkdir -p uploads
mkdir -p audio
chmod 755 uploads audio
```

### Step 7: Test Backend
```bash
# Run development server
python app.py

# Should see:
# ✅ AWS Rekognition client initialized
# ✅ Amazon Bedrock client initialized  
# ✅ ElevenLabs client initialized
# * Running on http://127.0.0.1:5000
```

---

## 🎨 Part 2: Frontend (Already Integrated)

The frontend is **already integrated** into Flask templates. No separate build needed!

### Templates Structure:
```
templates/
├── simple_counter.html    # Main app (root / & /counter)
├── smart_detector.html    # /smart route
├── counter_widget.html    # /widget route  
└── fake_twitch.html       # /fake-twitch route
```

### Static Files:
```
static/
├── css/
│   └── (inline in templates)
├── js/
│   └── (inline in templates)
└── (optional external assets)
```

---

## 🌐 Part 3: Production Deployment

### Option A: Local/Development Deployment

**1. Using start.sh script:**
```bash
chmod +x start.sh
./start.sh
```

**2. Manual start:**
```bash
source venv/bin/activate
export FLASK_ENV=production
python app.py
```

**3. Access:**
- Main app: http://localhost:5000/
- Counter: http://localhost:5000/counter
- Health: http://localhost:5000/api/health

---

### Option B: Production Server (Linux)

#### Using Gunicorn (Recommended)

**1. Install Gunicorn:**
```bash
pip install gunicorn
```

**2. Create systemd service:**
```bash
sudo nano /etc/systemd/system/streambet.service
```

```ini
[Unit]
Description=StreamBet Recognition API
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/prediction.chat/rekognitionAPI
Environment="PATH=/home/ubuntu/prediction.chat/rekognitionAPI/venv/bin"
EnvironmentFile=/home/ubuntu/prediction.chat/rekognitionAPI/.env
ExecStart=/home/ubuntu/prediction.chat/rekognitionAPI/venv/bin/gunicorn \
    --workers 4 \
    --bind 0.0.0.0:5000 \
    --timeout 120 \
    --access-logfile /var/log/streambet/access.log \
    --error-logfile /var/log/streambet/error.log \
    app:app

[Install]
WantedBy=multi-user.target
```

**3. Create log directory:**
```bash
sudo mkdir -p /var/log/streambet
sudo chown ubuntu:ubuntu /var/log/streambet
```

**4. Start service:**
```bash
sudo systemctl daemon-reload
sudo systemctl start streambet
sudo systemctl enable streambet
sudo systemctl status streambet
```

---

### Option C: Docker Deployment

**1. Create Dockerfile:**
```dockerfile
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create directories
RUN mkdir -p uploads audio

# Expose port
EXPOSE 5000

# Run application
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "--timeout", "120", "app:app"]
```

**2. Create docker-compose.yml:**
```yaml
version: '3.8'

services:
  streambet:
    build: .
    ports:
      - "5000:5000"
    env_file:
      - .env
    volumes:
      - ./uploads:/app/uploads
      - ./audio:/app/audio
    restart: unless-stopped
```

**3. Build and run:**
```bash
docker-compose up -d

# Check logs
docker-compose logs -f
```

---

### Option D: Cloud Deployment (AWS EC2)

**1. Launch EC2 instance:**
- Instance type: t3.medium (2 vCPU, 4GB RAM)
- OS: Ubuntu 22.04 LTS
- Security group: Allow ports 22 (SSH), 80 (HTTP), 443 (HTTPS)

**2. Connect and setup:**
```bash
ssh -i your-key.pem ubuntu@your-ec2-ip

# Update system
sudo apt update && sudo apt upgrade -y

# Install Python
sudo apt install python3.11 python3.11-venv python3-pip -y

# Clone your code
git clone https://github.com/yourrepo/prediction.chat.git
cd prediction.chat/rekognitionAPI

# Follow backend setup steps 2-7 above
```

**3. Install Nginx:**
```bash
sudo apt install nginx -y
```

**4. Configure Nginx:**
```bash
sudo nano /etc/nginx/sites-available/streambet
```

```nginx
server {
    listen 80;
    server_name your-domain.com;  # or EC2 public IP

    client_max_body_size 100M;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # For SSE (Server-Sent Events)
        proxy_buffering off;
        proxy_cache off;
        proxy_set_header Connection '';
        proxy_http_version 1.1;
        chunked_transfer_encoding off;
    }
}
```

**5. Enable site:**
```bash
sudo ln -s /etc/nginx/sites-available/streambet /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

**6. Setup SSL (Optional but recommended):**
```bash
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d your-domain.com
```

---

## 🧪 Part 4: Testing Deployment

### Health Check
```bash
curl http://localhost:5000/api/health
```

**Expected response:**
```json
{
    "status": "healthy",
    "service": "StreamBet Recognition API",
    "version": "1.0.0-hackathon"
}
```

### Full System Test
1. **Upload test video:**
   - Go to http://localhost:5000/
   - Use file upload
   - Upload a short video (< 30 seconds recommended)

2. **Start analysis:**
   - Click "Start Counting & Play Video"
   - Watch counter increment in real-time
   - Listen to AI commentary with voice

3. **Check logs:**
   ```bash
   # Development
   # Logs appear in terminal
   
   # Production (systemd)
   sudo journalctl -u streambet -f
   
   # Production (Docker)
   docker-compose logs -f
   ```

---

## 📊 Monitoring & Maintenance

### Log Files
```bash
# Application logs
tail -f /var/log/streambet/access.log
tail -f /var/log/streambet/error.log

# Nginx logs
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log
```

### Storage Management
```bash
# Clean old uploads (run weekly)
find uploads/ -type f -mtime +7 -delete

# Clean old audio (run weekly)
find audio/ -type f -mtime +7 -delete
```

### Backup
```bash
# Backup uploads folder
tar -czf backups/uploads-$(date +%Y%m%d).tar.gz uploads/

# Backup audio folder
tar -czf backups/audio-$(date +%Y%m%d).tar.gz audio/
```

---

## 🔒 Security Best Practices

### 1. Environment Variables
- ✅ Never commit `.env` to git
- ✅ Use strong secret keys
- ✅ Rotate AWS keys regularly

### 2. File Upload Security
- ✅ Validate file types (only .mp4, .mov, .avi)
- ✅ Limit file size (100MB default)
- ✅ Scan for malware if possible

### 3. API Rate Limiting
```python
# Add to app.py
from flask_limiter import Limiter

limiter = Limiter(
    app,
    key_func=lambda: request.remote_addr,
    default_limits=["100 per hour"]
)

@app.route('/api/stream-counter')
@limiter.limit("10 per minute")
def stream_counter():
    # ...
```

### 4. CORS Configuration
```python
# In app.py
CORS(app, resources={
    r"/api/*": {
        "origins": ["https://your-domain.com"],
        "methods": ["GET", "POST"],
        "allow_headers": ["Content-Type"]
    }
})
```

---

## 🐛 Troubleshooting

### Issue: AWS Credentials Not Working
```bash
# Test AWS access
aws sts get-caller-identity

# If fails, reconfigure
aws configure
```

### Issue: ElevenLabs Voice Not Playing
```bash
# Check API key
curl -H "xi-api-key: YOUR_KEY" https://api.elevenlabs.io/v1/voices

# Check audio file generation
ls -la audio/
```

### Issue: Video Upload Fails
```bash
# Check upload directory permissions
ls -ld uploads/
chmod 755 uploads/

# Check disk space
df -h
```

### Issue: Counter Not Updating
```bash
# Check browser console for errors
# Check SSE connection in Network tab
# Verify video plays
```

### Issue: High CPU Usage
```bash
# Reduce frame sampling rate in app.py
# Default: 1 frame/3 seconds
# Change to: 1 frame/5 seconds

SAMPLE_RATE = 5  # Instead of 3
```

---

## 📈 Performance Optimization

### 1. Video Processing
```python
# Reduce frame sample rate for faster processing
SAMPLE_RATE = 5  # 1 frame every 5 seconds

# Reduce image resolution for Rekognition
MAX_WIDTH = 800  # pixels
```

### 2. Caching
```python
# Enable response caching for repeated queries
from flask_caching import Cache

cache = Cache(app, config={'CACHE_TYPE': 'simple'})

@app.route('/api/analyze')
@cache.cached(timeout=300)
def analyze():
    # ...
```

### 3. CDN for Static Assets
- Use CloudFront or Cloudflare
- Serve video files from S3
- Cache audio files

---

## 🎯 Quick Start Commands

### Development:
```bash
source venv/bin/activate
python app.py
# Open http://localhost:5000
```

### Production (systemd):
```bash
sudo systemctl start streambet
sudo systemctl status streambet
```

### Production (Docker):
```bash
docker-compose up -d
docker-compose logs -f
```

### Stop Services:
```bash
# systemd
sudo systemctl stop streambet

# Docker
docker-compose down
```

---

## 📞 Support & Resources

### Documentation
- AWS Rekognition: https://docs.aws.amazon.com/rekognition/
- Amazon Bedrock: https://docs.aws.amazon.com/bedrock/
- ElevenLabs API: https://docs.elevenlabs.io/
- Flask: https://flask.palletsprojects.com/

### Cost Estimation
- **AWS Rekognition**: ~$0.001 per image analyzed
- **Amazon Bedrock (Titan)**: ~$0.0008 per 1K tokens
- **ElevenLabs**: ~$0.30 per 1K characters (paid plan)

**Example:** 100 videos/day (30s each, 10 frames):
- Rekognition: $30/month
- Bedrock: $20/month  
- ElevenLabs: $30/month
- **Total: ~$80/month**

---

## ✅ Deployment Checklist

- [ ] Python 3.8+ installed
- [ ] Virtual environment created
- [ ] Dependencies installed
- [ ] .env file configured
- [ ] AWS credentials configured
- [ ] ElevenLabs API key added
- [ ] Directories created (uploads, audio)
- [ ] Backend tested (health check passes)
- [ ] Frontend loads correctly
- [ ] Video upload works
- [ ] Counter updates in real-time
- [ ] AI commentary generates
- [ ] Voice plays correctly
- [ ] Production server configured (if applicable)
- [ ] Nginx configured (if applicable)
- [ ] SSL certificate installed (if applicable)
- [ ] Monitoring setup
- [ ] Backup strategy in place

---

## 🎉 You're Done!

Your StreamBet Recognition API is now deployed!

**Access your app:**
- Development: http://localhost:5000/
- Production: http://your-domain.com/ or http://your-ec2-ip/

**Need help?** Check the troubleshooting section or review logs for errors.

**Happy streaming! 🚀**
