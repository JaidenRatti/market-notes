#!/bin/bash

echo "🚀 Starting Polymarket Chrome Extension Trading Backend..."

# Get script directory and navigate to project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_ROOT"

# Install dependencies if needed
if [ ! -d "venv" ]; then
    echo "📦 Setting up Python virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
    pip install -r backend/requirements.txt
else
    echo "📦 Activating existing virtual environment..."
    source venv/bin/activate
fi

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "❗️ Please create .env file with your Magic wallet credentials:"
    echo "magickey=your_magic_private_key"
    echo "funder=your_polymarket_address"
    echo ""
    echo "Exiting..."
    exit 1
fi

echo "🎯 Market: Multiple events available in carousel"
echo "💰 Starting Flask trading backend on http://127.0.0.1:5000"
echo ""
echo "📖 How to use:"
echo "1. Open X (Twitter) in Chrome"
echo "2. Look for Polymarket button on tweets"
echo "3. Click button to see trading interface with carousel"
echo "4. Use ← → arrows to navigate between events"
echo "5. Press YES/NO buttons and enter amount to trade"
echo ""

cd backend && python3 trading_backend.py