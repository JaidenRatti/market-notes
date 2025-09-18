#!/bin/bash

# Script to check the status of the Polymarket Trading Backend

echo "🔍 Checking Polymarket Trading Backend Status..."
echo ""

# Check if any trading_backend processes are running
BACKEND_PIDS=$(ps aux | grep trading_backend.py | grep -v grep | awk '{print $2}')

if [ ! -z "$BACKEND_PIDS" ]; then
    echo "✅ Backend server is running!"
    echo "🔢 Process IDs: $BACKEND_PIDS"
    
    # Test API connection
    if curl -s http://127.0.0.1:5000/api/market > /dev/null; then
        echo "🌐 API is responding at http://127.0.0.1:5000"
        
        # Test tweet analysis endpoint
        echo "🧪 Testing tweet analysis..."
        RESPONSE=$(curl -s -X POST http://127.0.0.1:5000/api/analyze-tweet \
          -H "Content-Type: application/json" \
          -d '{"tweet_text": "Bitcoin is going up!", "author": "TestUser", "top_n": 1}')
        
        if echo "$RESPONSE" | grep -q '"success": true'; then
            echo "✅ Tweet analysis is working!"
            EVENTS_COUNT=$(echo "$RESPONSE" | grep -o '"total_count": [0-9]*' | cut -d' ' -f2)
            echo "📊 Found $EVENTS_COUNT relevant markets"
        else
            echo "❌ Tweet analysis is not working"
            echo "🔍 Response: $RESPONSE"
        fi
    else
        echo "❌ API is not responding"
    fi
    
    # Show log location
    BACKEND_DIR="$(dirname "$0")/../backend"
    if [ -f "$BACKEND_DIR/backend.log" ]; then
        echo "📝 Logs: $BACKEND_DIR/backend.log"
        echo "💡 View logs: tail -f $BACKEND_DIR/backend.log"
    fi
    
else
    echo "❌ Backend server is not running"
    echo "💡 Start it with: ./scripts/start_backend.sh"
fi

echo ""
echo "🎯 If everything is working, the Polymarket button on tweets should:"
echo "   1. Extract tweet text"
echo "   2. Send it to AI analysis pipeline"
echo "   3. Get relevant markets"
echo "   4. Display them in the popup carousel"
