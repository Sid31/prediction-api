#!/bin/bash

# Load environment variables from .env file and start the server

echo "🎮 StreamBet - Starting Server"
echo "==============================="
echo ""

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "❌ .env file not found!"
    echo "Please create .env with your AWS credentials"
    exit 1
fi

echo "📋 Loading credentials from .env..."

# Load environment variables
set -a
source .env
set +a

echo "✅ Credentials loaded"
echo "   Region: ${AWS_REGION}"
echo "   Bucket: ${AWS_BUCKET}"
echo ""

# Create uploads directory
mkdir -p uploads

echo "🚀 Starting Flask server..."
echo "🌐 Open http://localhost:5000 in your browser"
echo ""
echo "To test:"
echo "  1. Drag tets.mp4 to the upload zone"
echo "  2. Click 'Analyze Video'"
echo "  3. Wait 30-60 seconds for results"
echo ""
echo "Press Ctrl+C to stop the server"
echo "==============================="
echo ""

# Start the server
python3 app.py
