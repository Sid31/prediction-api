# 🏗️ StreamBet POC - Technical Architecture

## 📊 System Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     StreamBet Platform                       │
│                  AI-Powered Betting Verification             │
└─────────────────────────────────────────────────────────────┘

┌──────────────┐      ┌──────────────┐      ┌──────────────┐
│   Frontend   │ ───▶ │   Flask API  │ ───▶ │  AWS Cloud   │
│  (Browser)   │ ◀─── │   (Python)   │ ◀─── │  (Services)  │
└──────────────┘      └──────────────┘      └──────────────┘
```

## 🔄 Data Flow

### 1. Video Upload Flow
```
User Browser
    │
    ├─ Drag & Drop Video
    │
    ▼
HTML5 File API
    │
    ├─ FormData with video file
    │
    ▼
Flask API (/api/analyze)
    │
    ├─ Save to local uploads/
    │
    ▼
AWS S3 Upload
    │
    ├─ Temporary storage
    │
    ▼
AWS Rekognition
    │
    ├─ Start label detection job
    ├─ Poll for completion (30-60s)
    ├─ Extract labels + timestamps
    │
    ▼
Response Processing
    │
    ├─ Filter activity labels
    ├─ Generate betting suggestions
    ├─ Format results
    │
    ▼
JSON Response to Browser
    │
    ├─ Display results
    ├─ Show betting suggestions
    └─ Cleanup (delete temp files)
```

### 2. Betting Resolution Flow
```
Analysis Results
    │
    ▼
AI Decision Logic
    │
    ├─ Check confidence > 80%
    ├─ Verify timestamps
    ├─ Match against bet criteria
    │
    ▼
Resolution Outcome
    │
    ├─ YES/NO decision
    ├─ Confidence score
    ├─ Payout trigger
    │
    ▼
Mock Payout System
    │
    └─ (Future: Real payment processing)
```

## 🧩 Component Architecture

### Frontend Layer
```
┌─────────────────────────────────────────┐
│          index.html (SPA)               │
├─────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐      │
│  │   Upload    │  │   Betting   │      │
│  │   Zone      │  │   Markets   │      │
│  └─────────────┘  └─────────────┘      │
│  ┌─────────────┐  ┌─────────────┐      │
│  │   Results   │  │  Detailed   │      │
│  │   Display   │  │  Analysis   │      │
│  └─────────────┘  └─────────────┘      │
└─────────────────────────────────────────┘
         │                    │
         ▼                    ▼
    Fetch API          WebSocket (future)
```

### Backend Layer
```
┌─────────────────────────────────────────┐
│           Flask Application             │
├─────────────────────────────────────────┤
│                                         │
│  ┌──────────────────────────────────┐  │
│  │       API Endpoints              │  │
│  ├──────────────────────────────────┤  │
│  │  GET  /                          │  │
│  │  GET  /api/health                │  │
│  │  GET  /api/bets                  │  │
│  │  POST /api/analyze               │  │
│  │  POST /api/resolve               │  │
│  └──────────────────────────────────┘  │
│                                         │
│  ┌──────────────────────────────────┐  │
│  │     Business Logic               │  │
│  ├──────────────────────────────────┤  │
│  │  - Video processing              │  │
│  │  - AWS integration               │  │
│  │  - Betting suggestions           │  │
│  │  - Resolution logic              │  │
│  └──────────────────────────────────┘  │
│                                         │
└─────────────────────────────────────────┘
```

### AWS Layer
```
┌─────────────────────────────────────────┐
│          AWS Services                   │
├─────────────────────────────────────────┤
│                                         │
│  ┌──────────────┐  ┌──────────────┐   │
│  │   S3 Bucket  │  │ Rekognition  │   │
│  │              │  │              │   │
│  │ - Temp store │  │ - Label det. │   │
│  │ - Auto clean │  │ - Timestamps │   │
│  └──────────────┘  └──────────────┘   │
│                                         │
│  ┌──────────────┐  ┌──────────────┐   │
│  │     IAM      │  │   CloudWatch │   │
│  │              │  │   (future)   │   │
│  │ - Access mgmt│  │ - Monitoring │   │
│  └──────────────┘  └──────────────┘   │
│                                         │
└─────────────────────────────────────────┘
```

## 🔐 Security Architecture

```
┌─────────────────────────────────────────┐
│         Security Layers                 │
├─────────────────────────────────────────┤
│                                         │
│  1. Input Validation                    │
│     ├─ File type check (MP4/MOV/AVI)   │
│     ├─ File size limit (100MB)         │
│     └─ Secure filename sanitization    │
│                                         │
│  2. AWS Authentication                  │
│     ├─ IAM credentials                  │
│     ├─ Environment variables            │
│     └─ Least privilege access           │
│                                         │
│  3. CORS Configuration                  │
│     ├─ Allowed origins                  │
│     └─ Method restrictions              │
│                                         │
│  4. Data Cleanup                        │
│     ├─ Auto-delete temp files          │
│     ├─ S3 object deletion               │
│     └─ No persistent storage            │
│                                         │
└─────────────────────────────────────────┘
```

## 📡 API Architecture

### Request/Response Flow
```
Client Request
    │
    ▼
┌─────────────────┐
│  Flask Router   │
└─────────────────┘
    │
    ├─ Route matching
    ├─ Method validation
    │
    ▼
┌─────────────────┐
│  Middleware     │
└─────────────────┘
    │
    ├─ CORS headers
    ├─ Content-type check
    │
    ▼
┌─────────────────┐
│  Handler        │
└─────────────────┘
    │
    ├─ Input validation
    ├─ Business logic
    ├─ AWS calls
    │
    ▼
┌─────────────────┐
│  Response       │
└─────────────────┘
    │
    ├─ JSON formatting
    ├─ Error handling
    │
    ▼
Client Response
```

### Endpoint Details

#### POST /api/analyze
```
Request:
  - Method: POST
  - Content-Type: multipart/form-data
  - Body: file (video)

Processing:
  1. Validate file
  2. Save locally
  3. Upload to S3
  4. Start Rekognition job
  5. Poll for results
  6. Process labels
  7. Generate suggestions
  8. Cleanup files

Response:
  {
    "status": "success",
    "total_labels": 15,
    "labels": [...],
    "activity_labels": [...],
    "betting_suggestion": {...},
    "video_metadata": {...}
  }

Errors:
  - 400: Invalid file
  - 500: Processing error
```

## 🔄 State Management

### Frontend State
```
┌─────────────────────────────────────────┐
│        Application State                │
├─────────────────────────────────────────┤
│                                         │
│  selectedFile: File | null              │
│  analysisResults: Object | null         │
│  isAnalyzing: boolean                   │
│  bets: Array<Bet>                       │
│  error: string | null                   │
│                                         │
└─────────────────────────────────────────┘
```

### Backend State
```
┌─────────────────────────────────────────┐
│         Stateless Design                │
├─────────────────────────────────────────┤
│                                         │
│  - No session storage                   │
│  - No persistent state                  │
│  - Each request independent             │
│  - Cleanup after processing             │
│                                         │
└─────────────────────────────────────────┘
```

## 📊 Data Models

### Video Analysis Result
```python
{
  "status": "success" | "error",
  "job_id": "string",
  "total_labels": int,
  "labels": [
    {
      "label": "string",
      "confidence": float,
      "timestamps": [float],
      "category": "string"
    }
  ],
  "activity_labels": [...],
  "betting_suggestion": {
    "suggestion": "string",
    "detected_activity": "string",
    "confidence": float,
    "timestamps": [float]
  },
  "video_metadata": {
    "duration_seconds": float,
    "format": "string"
  }
}
```

### Betting Market
```python
{
  "id": int,
  "event": "string",
  "odds": {
    "yes": float,
    "no": float
  },
  "pool": int,
  "status": "active" | "resolved"
}
```

### Resolution Result
```python
{
  "status": "resolved" | "failed",
  "outcome": "YES" | "NO",
  "confidence": float,
  "payout_triggered": boolean,
  "detected_at": [float]
}
```

## 🚀 Scalability Architecture

### Current (POC)
```
Single Server
    │
    ├─ Flask (sync)
    ├─ Local file storage
    ├─ Sequential processing
    └─ Single region
```

### Future (Production)
```
┌─────────────────────────────────────────┐
│         Load Balancer                   │
└─────────────────────────────────────────┘
              │
    ┌─────────┼─────────┐
    ▼         ▼         ▼
┌────────┐ ┌────────┐ ┌────────┐
│ Server │ │ Server │ │ Server │
│   1    │ │   2    │ │   3    │
└────────┘ └────────┘ └────────┘
    │         │         │
    └─────────┼─────────┘
              ▼
    ┌─────────────────┐
    │   AWS Services  │
    │                 │
    │ - S3            │
    │ - Rekognition   │
    │ - Bedrock       │
    │ - DynamoDB      │
    │ - Lambda        │
    └─────────────────┘
```

## 🔌 Integration Points

### Current Integrations
```
┌─────────────────┐
│   Flask App     │
└─────────────────┘
        │
        ├─── AWS S3
        ├─── AWS Rekognition
        └─── Local Storage
```

### Future Integrations
```
┌─────────────────┐
│   Flask App     │
└─────────────────┘
        │
        ├─── AWS Bedrock (AI Agents)
        ├─── AWS Kinesis (Streaming)
        ├─── PostgreSQL (Database)
        ├─── Redis (Cache)
        ├─── Stripe (Payments)
        ├─── NOWPayments (Crypto)
        ├─── Twitch API (Streams)
        └─── WebSocket (Real-time)
```

## 📈 Performance Characteristics

### Current Performance
```
┌─────────────────────────────────────────┐
│         Performance Metrics             │
├─────────────────────────────────────────┤
│                                         │
│  Upload:        < 1 second              │
│  S3 Transfer:   2-5 seconds             │
│  Rekognition:   30-60 seconds           │
│  Processing:    < 1 second              │
│  Response:      < 1 second              │
│                                         │
│  Total:         35-70 seconds           │
│                                         │
└─────────────────────────────────────────┘
```

### Optimization Opportunities
```
1. Parallel Processing
   - Multiple videos simultaneously
   - Async job handling

2. Caching
   - Redis for repeated queries
   - CDN for static assets

3. Compression
   - Video preprocessing
   - Response compression

4. Regional Distribution
   - Multi-region deployment
   - Edge computing
```

## 🛠️ Technology Stack

```
┌─────────────────────────────────────────┐
│         Technology Stack                │
├─────────────────────────────────────────┤
│                                         │
│  Frontend:                              │
│    ├─ HTML5                             │
│    ├─ CSS3 (Gradients, Animations)     │
│    └─ Vanilla JavaScript (ES6+)        │
│                                         │
│  Backend:                               │
│    ├─ Python 3.8+                       │
│    ├─ Flask 3.0                         │
│    ├─ Boto3 (AWS SDK)                   │
│    └─ Flask-CORS                        │
│                                         │
│  Cloud:                                 │
│    ├─ AWS S3                            │
│    ├─ AWS Rekognition                   │
│    └─ AWS IAM                           │
│                                         │
│  Development:                           │
│    ├─ Git                               │
│    ├─ Virtual Environment               │
│    └─ Environment Variables             │
│                                         │
└─────────────────────────────────────────┘
```

## 🔄 Deployment Architecture

### Local Development
```
Developer Machine
    │
    ├─ Python Virtual Env
    ├─ Flask Dev Server
    ├─ Local file storage
    └─ AWS API calls
```

### Production Deployment (Future)
```
┌─────────────────────────────────────────┐
│           CloudFront CDN                │
└─────────────────────────────────────────┘
              │
┌─────────────────────────────────────────┐
│         Application Load Balancer       │
└─────────────────────────────────────────┘
              │
    ┌─────────┼─────────┐
    ▼         ▼         ▼
┌────────┐ ┌────────┐ ┌────────┐
│  ECS   │ │  ECS   │ │  ECS   │
│ Task 1 │ │ Task 2 │ │ Task 3 │
└────────┘ └────────┘ └────────┘
    │         │         │
    └─────────┼─────────┘
              ▼
    ┌─────────────────┐
    │   AWS Services  │
    └─────────────────┘
```

## 📊 Monitoring & Observability (Future)

```
┌─────────────────────────────────────────┐
│         Monitoring Stack                │
├─────────────────────────────────────────┤
│                                         │
│  Metrics:                               │
│    ├─ CloudWatch Metrics                │
│    ├─ Request counts                    │
│    ├─ Error rates                       │
│    └─ Processing times                  │
│                                         │
│  Logging:                               │
│    ├─ CloudWatch Logs                   │
│    ├─ Application logs                  │
│    └─ Error tracking                    │
│                                         │
│  Tracing:                               │
│    ├─ X-Ray (future)                    │
│    └─ Request tracing                   │
│                                         │
└─────────────────────────────────────────┘
```

---

## 🎯 Key Architectural Decisions

### 1. Stateless Design
**Why**: Easier to scale, no session management
**Trade-off**: No user context between requests

### 2. Synchronous Processing
**Why**: Simpler for POC, easier to debug
**Trade-off**: Blocks during analysis

### 3. Temporary Storage
**Why**: No persistent data, privacy-friendly
**Trade-off**: Can't review past analyses

### 4. Mock Betting Logic
**Why**: Focus on AI integration first
**Trade-off**: Not production-ready

### 5. Single Region
**Why**: Simpler setup, lower costs
**Trade-off**: Higher latency for distant users

---

**This architecture is designed for rapid prototyping while maintaining a clear path to production scalability.**
