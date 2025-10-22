#!/bin/bash
# Start the StreamBet Agent Service

echo "🤖 Starting StreamBet Video Detection Agent"
echo "============================================"
echo ""

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "❌ .env file not found!"
    echo "Please create .env with:"
    echo "  AWS_REGION=us-east-1"
    echo "  AWS_ACCESS_KEY_ID=your_key"
    echo "  AWS_SECRET_ACCESS_KEY=your_secret"
    echo "  WEBHOOK_URL=http://localhost:8000/api/events/detection"
    echo "  COLLECTION_ID=streambet-streamers"
    exit 1
fi

# Check if backend is running
echo "📡 Checking if backend is running on port 8000..."
if ! nc -z localhost 8000 2>/dev/null; then
    echo "⚠️  Backend not detected on port 8000"
    echo "   Please start your backend first:"
    echo "   cd ../newbackend && npm start"
    echo ""
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
else
    echo "✅ Backend is running"
fi

echo ""
echo "🚀 Starting agent on port 8080..."
echo ""

# Start the agent
python3 agent_server.py
