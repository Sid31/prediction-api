#!/bin/bash

# Test script for analyzing tets.mp4

echo "🎮 StreamBet Video Analysis Test"
echo "=================================="
echo ""

# Check if server is running
echo "📡 Checking if server is running..."
SERVER_RUNNING=$(curl -s http://localhost:5000/api/health 2>/dev/null)

if [ -z "$SERVER_RUNNING" ]; then
    echo "❌ Server is not running!"
    echo ""
    echo "Please start the server first:"
    echo "  python3 app.py"
    echo ""
    echo "Then run this script again."
    exit 1
fi

echo "✅ Server is running!"
echo ""

# Check if video exists
if [ ! -f "tets.mp4" ]; then
    echo "❌ tets.mp4 not found!"
    exit 1
fi

echo "📹 Video found: tets.mp4"
echo "📊 File size: $(ls -lh tets.mp4 | awk '{print $5}')"
echo ""

# Analyze the video
echo "🔍 Analyzing video with AWS Rekognition..."
echo "⏳ This will take 30-60 seconds..."
echo ""

curl -X POST http://localhost:5000/api/analyze \
  -F "file=@tets.mp4" \
  -w "\n\n⏱️  Total time: %{time_total}s\n" \
  2>/dev/null | python3 -m json.tool

echo ""
echo "=================================="
echo "✅ Analysis complete!"
echo ""
echo "💡 Tip: Open http://localhost:5000 in your browser"
echo "    for a better visual experience!"
