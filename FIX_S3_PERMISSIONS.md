# 🔧 Fix S3 Access Denied Error

## Problem
Your IAM user `sid` doesn't have permission to upload to the `predictionchat` bucket.

## Quick Fix (Choose One)

### ✅ Option 1: Add S3 Permissions (Easiest)

1. Go to [AWS IAM Console](https://console.aws.amazon.com/iam/)
2. Click **Users** → **sid**
3. Click **Add permissions** → **Attach policies directly**
4. Search for and select: **`AmazonS3FullAccess`**
5. Click **Next** → **Add permissions**
6. Refresh the page and try uploading again!

### ✅ Option 2: Create Your Own Bucket

1. Go to [AWS S3 Console](https://s3.console.aws.amazon.com/s3/)
2. Click **Create bucket**
3. Bucket name: `streambet-sid-demo` (must be globally unique)
4. Region: **us-east-1**
5. Keep all default settings
6. Click **Create bucket**
7. Update your `.env` file:
   ```bash
   AWS_BUCKET=streambet-sid-demo
   ```
8. Restart the server: `./start.sh`

### ✅ Option 3: Use Existing Bucket with Permissions

If you want to use the `predictionchat` bucket:

1. Go to [AWS S3 Console](https://s3.console.aws.amazon.com/s3/)
2. Click on **predictionchat** bucket
3. Go to **Permissions** tab
4. Scroll to **Bucket policy**
5. Add this policy (replace with your user ARN):

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": {
                "AWS": "arn:aws:iam::328764941593:user/sid"
            },
            "Action": [
                "s3:PutObject",
                "s3:GetObject",
                "s3:DeleteObject"
            ],
            "Resource": "arn:aws:s3:::predictionchat/*"
        }
    ]
}
```

## Recommended: Option 1 (Add S3 Permissions)

This is the simplest and will work for any bucket you create.

**Steps:**
1. AWS Console → IAM → Users → sid
2. Add permissions → Attach policies
3. Select: `AmazonS3FullAccess`
4. Save
5. Try uploading again!

---

## After Fixing

Once you've added permissions or created a new bucket:

1. **Refresh the browser** (http://localhost:5000)
2. **Upload tets.mp4** again
3. **Click "Analyze Video"**
4. **See the backflip count!** 🤸

---

**Need help?** The error shows you need `s3:PutObject` permission. Adding `AmazonS3FullAccess` policy is the quickest fix!
