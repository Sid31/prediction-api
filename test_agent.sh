#!/bin/bash
# Test the agent server

echo "🧪 Testing StreamBet Video Detection Agent"
echo "=========================================="
echo ""

# Test 1: Health check
echo "1️⃣  Testing health endpoint..."
curl -s http://localhost:8080/ping | python3 -m json.tool
echo ""

# Test 2: Root endpoint
echo "2️⃣  Testing root endpoint..."
curl -s http://localhost:8080/ | python3 -m json.tool
echo ""

# Test 3: Invoke with test video
echo "3️⃣  Testing video analysis (this will take ~15 seconds)..."
curl -X POST http://localhost:8080/invocations \
  -H 'Content-Type: application/json' \
  -d '{
    "video_url": "http://localhost:5000/uploads/1760892120_tets.mp4",
    "video_id": "test_video_001",
    "labels": ["person", "fighting", "sport"],
    "confidence": 0.6,
    "fps_sample": 1
  }' | python3 -m json.tool

echo ""
echo "✅ Agent tests complete!"
echo ""
echo "To watch live detections, check your newbackend logs:"
echo "  cd ../newbackend && npm start"
