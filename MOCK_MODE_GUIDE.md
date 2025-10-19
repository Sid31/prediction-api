# 🎭 Mock Mode - Save AWS Credits!

## 💰 Problem
AWS Rekognition costs ~$0.10 per video analysis. During testing and demos, this adds up quickly!

## ✅ Solution: Mock Mode

Mock mode simulates backflip detection without calling AWS Rekognition, saving you credits.

## 🚀 How to Enable

### Option 1: Add to .env file
```bash
USE_MOCK_MODE=true
```

### Option 2: Set environment variable
```bash
export USE_MOCK_MODE=true
./start.sh
```

## 🎯 What Mock Mode Does

Returns simulated results showing:
- ✅ **1 Backflip detected** at 20 seconds (matching your video!)
- ✅ **Acrobatics** label (89.5% confidence)
- ✅ **Gymnastics** label (85.2% confidence)  
- ✅ **Flip** label (82.7% confidence)
- ✅ **Timestamps**: 20.0s, 20.1s, 20.2s, 20.5s

## 📊 Mock vs Real Comparison

| Feature | Mock Mode | Real AWS |
|---------|-----------|----------|
| Cost | **FREE** | ~$0.10/video |
| Speed | **Instant** | 30-60 seconds |
| Accuracy | Simulated | Real AI |
| Credits Used | **0** | Yes |

## 🎬 Perfect For:

- ✅ **Testing** - Iterate quickly without costs
- ✅ **Demos** - Show the concept without waiting
- ✅ **Development** - Build features without AWS bills
- ✅ **Screenshots** - Get consistent results

## 🔄 When to Use Real AWS:

- ❌ **Final demo** - Show real AI in action
- ❌ **Different videos** - Test various content
- ❌ **Validation** - Verify actual detection works

## 💡 Recommended Workflow

1. **Development**: `USE_MOCK_MODE=true` (save credits)
2. **Testing**: `USE_MOCK_MODE=true` (iterate fast)
3. **Final Demo**: `USE_MOCK_MODE=false` (show real AI)

## 🎯 Example Usage

```bash
# Enable mock mode in .env
echo "USE_MOCK_MODE=true" >> .env

# Restart server
./start.sh

# Upload tets.mp4 - instant results, no AWS costs!
```

## 📈 Expected Mock Results

```
🤸 Backflip Detection Result

1 Backflip Detected!

Bet Outcome: NO (less than 10)
Confidence: 89%
⏱️ Detected at: 20.0s, 20.1s, 20.2s
```

## 🔧 Toggle Anytime

```bash
# Disable mock mode (use real AWS)
export USE_MOCK_MODE=false

# Enable mock mode (save credits)
export USE_MOCK_MODE=true
```

---

**Pro Tip**: Use mock mode for 99% of testing, then do 1-2 real AWS runs for your final demo video! 💰
