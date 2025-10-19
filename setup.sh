#!/bin/bash

# StreamBet POC - Quick Setup Script
# This script helps you set up the demo environment quickly

echo "🎮 StreamBet POC - Setup Script"
echo "================================"
echo ""

# Check Python version
echo "📋 Checking Python version..."
python3 --version

if [ $? -ne 0 ]; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

# Create virtual environment
echo ""
echo "🔧 Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "✅ Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo ""
echo "📦 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "❌ Failed to install dependencies"
    exit 1
fi

# Create necessary directories
echo ""
echo "📁 Creating directories..."
mkdir -p uploads
mkdir -p templates

# Check for AWS credentials
echo ""
echo "🔐 Checking AWS credentials..."
if [ -z "$AWS_ACCESS_KEY_ID" ]; then
    echo "⚠️  AWS_ACCESS_KEY_ID not set"
    echo ""
    echo "Please set your AWS credentials:"
    echo "  export AWS_ACCESS_KEY_ID=your_key"
    echo "  export AWS_SECRET_ACCESS_KEY=your_secret"
    echo "  export AWS_REGION=us-east-1"
    echo "  export AWS_BUCKET=your-bucket-name"
    echo ""
    echo "Or create a .env file from .env.example"
else
    echo "✅ AWS credentials found"
fi

# Check for S3 bucket
echo ""
echo "☁️  Checking S3 bucket..."
if [ ! -z "$AWS_BUCKET" ]; then
    aws s3 ls s3://$AWS_BUCKET 2>/dev/null
    if [ $? -ne 0 ]; then
        echo "⚠️  Bucket $AWS_BUCKET not found or not accessible"
        echo ""
        read -p "Create bucket now? (y/n) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            aws s3 mb s3://$AWS_BUCKET --region ${AWS_REGION:-us-east-1}
            echo "✅ Bucket created"
        fi
    else
        echo "✅ S3 bucket accessible"
    fi
fi

echo ""
echo "================================"
echo "✅ Setup complete!"
echo ""
echo "To start the demo:"
echo "  1. Activate virtual environment: source venv/bin/activate"
echo "  2. Set AWS credentials (if not already set)"
echo "  3. Run: python app.py"
echo "  4. Open: http://localhost:5000"
echo ""
echo "For detailed instructions, see HACKATHON_README.md"
echo "================================"
