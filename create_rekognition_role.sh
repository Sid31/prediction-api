#!/bin/bash

# Create IAM Role for AWS Rekognition Video

echo "🎥 Creating IAM Role for Rekognition Video"
echo "=========================================="
echo ""

ROLE_NAME="RekognitionVideoRole"
ACCOUNT_ID="328764941593"

# Step 1: Create trust policy
echo "📝 Creating trust policy..."
cat > /tmp/rekognition-trust-policy.json <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "rekognition.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
EOF

# Step 2: Create the role
echo "🔧 Creating IAM role: $ROLE_NAME..."
aws iam create-role \
  --role-name $ROLE_NAME \
  --assume-role-policy-document file:///tmp/rekognition-trust-policy.json \
  --description "Service role for AWS Rekognition Video operations" \
  2>/dev/null

if [ $? -eq 0 ]; then
    echo "✅ Role created successfully!"
else
    echo "ℹ️  Role might already exist, continuing..."
fi

# Step 3: Attach policies
echo "📎 Attaching policies..."

aws iam attach-role-policy \
  --role-name $ROLE_NAME \
  --policy-arn arn:aws:iam::aws:policy/AmazonRekognitionServiceRole

aws iam attach-role-policy \
  --role-name $ROLE_NAME \
  --policy-arn arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess

echo "✅ Policies attached!"
echo ""

# Step 4: Get role ARN
ROLE_ARN="arn:aws:iam::${ACCOUNT_ID}:role/${ROLE_NAME}"
echo "🎯 Role ARN:"
echo "   $ROLE_ARN"
echo ""

# Step 5: Update .env file
echo "📝 Updating .env file..."
if grep -q "REKOGNITION_ROLE_ARN=" .env; then
    # Update existing line
    sed -i '' "s|REKOGNITION_ROLE_ARN=.*|REKOGNITION_ROLE_ARN=$ROLE_ARN|" .env
else
    # Add new line
    echo "REKOGNITION_ROLE_ARN=$ROLE_ARN" >> .env
fi

echo "✅ .env file updated!"
echo ""
echo "=========================================="
echo "✅ Setup Complete!"
echo ""
echo "🎯 Next steps:"
echo "   1. Wait 10 seconds for IAM to propagate"
echo "   2. Restart server: ./start.sh"
echo "   3. Upload tets.mp4"
echo "   4. Face search & person tracking will work!"
echo ""
