#!/usr/bin/env python3
"""
Quick test script for StreamBet API
Tests the API endpoints without needing a video file
"""

import requests
import json

BASE_URL = "http://localhost:5000"

def test_health():
    """Test health check endpoint"""
    print("🏥 Testing health endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/api/health")
        print(f"✅ Status: {response.status_code}")
        print(f"📊 Response: {json.dumps(response.json(), indent=2)}")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_bets():
    """Test bets endpoint"""
    print("\n🎯 Testing bets endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/api/bets")
        print(f"✅ Status: {response.status_code}")
        data = response.json()
        print(f"📊 Found {len(data['bets'])} betting markets:")
        for bet in data['bets']:
            print(f"  - {bet['event']}")
            print(f"    Odds: YES {bet['odds']['yes']}x, NO {bet['odds']['no']}x")
            print(f"    Pool: ${bet['pool']}")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_resolve():
    """Test resolve endpoint with mock data"""
    print("\n⚖️  Testing resolve endpoint...")
    try:
        mock_analysis = {
            'status': 'success',
            'activity_labels': [
                {
                    'label': 'Jumping',
                    'confidence': 92.5,
                    'timestamps': [10.5, 20.1, 30.3]
                }
            ]
        }
        
        response = requests.post(
            f"{BASE_URL}/api/resolve",
            json={
                'bet_id': 1,
                'analysis': mock_analysis
            }
        )
        print(f"✅ Status: {response.status_code}")
        print(f"📊 Response: {json.dumps(response.json(), indent=2)}")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    print("🎮 StreamBet API Test Suite")
    print("=" * 50)
    print("Make sure the server is running: python app.py")
    print("=" * 50)
    print()
    
    results = []
    results.append(("Health Check", test_health()))
    results.append(("Bets Endpoint", test_bets()))
    results.append(("Resolve Endpoint", test_resolve()))
    
    print("\n" + "=" * 50)
    print("📊 Test Results:")
    print("=" * 50)
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    all_passed = all(result[1] for result in results)
    if all_passed:
        print("\n🎉 All tests passed! API is working correctly.")
        print("\nNext steps:")
        print("1. Open http://localhost:5000 in your browser")
        print("2. Upload a test video (MP4, MOV, or AVI)")
        print("3. Watch the AI analyze and detect activities")
    else:
        print("\n⚠️  Some tests failed. Check if the server is running.")

if __name__ == "__main__":
    main()
