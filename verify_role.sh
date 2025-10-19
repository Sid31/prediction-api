#!/bin/bash

echo "🔍 Verifying IAM Role Setup"
echo "======================================"
echo ""

ROLE_NAME="RekognitionVideoRole"

echo "📋 Checking if role exists..."
aws iam get-role --role-name $ROLE_NAME 2>/dev/null

if [ $? -eq 0 ]; then
    echo "✅ Role exists!"
    echo ""
    echo "📋 Trust Policy:"
    aws iam get-role --role-name $ROLE_NAME --query 'Role.AssumeRolePolicyDocument' 2>/dev/null
    echo ""
    echo "📋 Attached Policies:"
    aws iam list-attached-role-policies --role-name $ROLE_NAME 2>/dev/null
else
    echo "❌ Role not found or AWS CLI not configured"
fi

echo ""
echo "======================================"
echo "💡 If AWS CLI is not installed, verify in console:"
echo "   https://console.aws.amazon.com/iam/home#/roles/RekognitionVideoRole"
