#!/bin/bash

# Download a test video for demo purposes
# This script downloads a free sample video from Pexels

echo "🎥 Downloading test video for StreamBet demo..."
echo ""

# Create uploads directory if it doesn't exist
mkdir -p uploads

# Option 1: Small test video (recommended for quick testing)
echo "Downloading small test video (exercise/fitness)..."
curl -L "https://videos.pexels.com/video-files/4753994/4753994-hd_1920_1080_25fps.mp4" \
  -o uploads/test_exercise.mp4 \
  --progress-bar

if [ $? -eq 0 ]; then
    echo "✅ Downloaded: uploads/test_exercise.mp4"
    echo ""
    echo "Video info:"
    ls -lh uploads/test_exercise.mp4
    echo ""
    echo "You can now:"
    echo "1. Run: python app.py"
    echo "2. Open: http://localhost:5000"
    echo "3. Upload: uploads/test_exercise.mp4"
else
    echo "❌ Download failed. You can manually download a test video from:"
    echo "   https://www.pexels.com/search/videos/exercise/"
    echo ""
    echo "Save it as: uploads/test_video.mp4"
fi

echo ""
echo "Alternative test videos:"
echo "- Pexels: https://www.pexels.com/search/videos/exercise/"
echo "- Pixabay: https://pixabay.com/videos/search/sports/"
echo ""
echo "Look for videos with:"
echo "✓ Clear motion (jumping, running, sports)"
echo "✓ Good lighting"
echo "✓ 1-5 minutes duration"
echo "✓ MP4 format"
