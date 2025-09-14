#!/bin/bash

# Script to start the Polymarket Trading Backend with Tweet Analysis

echo "🚀 Starting Polymarket Trading Backend with Tweet Analysis..."

# Navigate to the backend directory
cd "$(dirname "$0")/../backend"

# Kill any existing processes on port 5000
echo "🔄 Clearing port 5000..."
lsof -ti:5000 | xargs kill -9 2>/dev/null

# Wait a moment for processes to clean up
sleep 2

# Start the backend server
echo "🔧 Starting backend server..."
nohup python3 trading_backend.py > backend.log 2>&1 &

# Wait for server to start
sleep 5

# Test if server is running
echo "🧪 Testing server connection..."
if curl -s http://127.0.0.1:5000/api/market > /dev/null; then
    echo "✅ Backend server is running successfully!"
    echo "🌐 Server available at: http://127.0.0.1:5000"
    echo "📝 Logs available at: $(pwd)/backend.log"
    echo ""
    echo "🎯 Tweet Analysis Integration Ready!"
    echo "   • Press the Polymarket button on any tweet"
    echo "   • The AI will analyze the tweet and find relevant markets"
    echo "   • Markets will be displayed in the popup carousel"
    echo ""
    echo "📊 To view logs in real-time: tail -f $(pwd)/backend.log"
else
    echo "❌ Failed to start backend server"
    echo "🔍 Check logs: cat $(pwd)/backend.log"
    exit 1
fi
