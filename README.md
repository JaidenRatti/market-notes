# Polymarket Trading Chrome Extension

A Chrome extension that integrates Polymarket prediction market trading directly into X (Twitter), featuring real-time market data, live trading capabilities, and user position tracking.

## 🏗️ Project Structure

```
polymarket-trading-extension/
├── extension/              # Chrome Extension Files
│   ├── manifest.json      # Extension manifest
│   ├── content.js         # Main extension logic (55KB)
│   ├── background.js      # Background service worker
│   ├── styles.css         # Extension styling
│   └── icons/             # Extension icons
├── backend/               # Flask Trading Backend
│   ├── trading_backend.py # Main Flask API server
│   ├── requirements.txt   # Python dependencies
│   └── data/              # Sample Market Data
│       ├── samplein.json  # Single market sample
│       ├── samplemultimarkets.json # Multi-market sample
│       └── sampleoneopenposition.json # Position sample
├── scripts/               # Utility Scripts
│   └── start_trading.sh   # Startup script
├── .env                   # Environment variables (Magic wallet keys)
├── .gitignore
└── README.md
```

## 🚀 Features

### Market Event Carousel
- **Multiple Events**: Navigate through different Polymarket events using ← → arrows
- **Event Counter**: Shows current position (e.g., "3 / 6" events)
- **Mixed Market Types**: Supports both single-market and multi-candidate events
- **Automatic Detection**: Starts in carousel mode when multiple events available

### Market Trading Interface
- **YES/NO Trading**: Click buttons to select position and see real-time pricing
- **Live Calculations**: Profit/payout updates as you type dollar amounts
- **Smart Formatting**: Automatic $ formatting with decimal validation
- **Execute Trades**: Direct integration with Polymarket API for real trading

### Multi-Market Events
- **Candidate Cards**: Visual cards for multi-candidate markets (e.g., NYC Mayor race)
- **Probability Display**: Shows percentage odds (handles <1% edge case)
- **Click to Trade**: Expand any candidate to show trading interface
- **Volume & Images**: Candidate photos and trading volume per market

### Profile Position Tracking
- **Live Positions**: Real positions from your Polymarket account via API
- **Open/Closed Tabs**: Switch between active and closed positions
- **P&L Tracking**: Color-coded profit/loss with detailed breakdowns
- **Position Details**: Shares, average price, current price, total value

## 🛠️ Setup Instructions

### 1. Install Backend Dependencies
```bash
# Run from project root
./scripts/start_trading.sh
```

### 2. Configure Environment
Create `.env` file in project root:
```env
magickey=your_magic_wallet_private_key
funder=your_polymarket_wallet_address
```

### 3. Install Chrome Extension
1. Open Chrome → Extensions → Developer mode
2. Click "Load unpacked"
3. Select the `extension/` folder
4. Extension icon should appear in toolbar

## 🔧 Technical Architecture

### Chrome Extension (Manifest V3)
- **Content Script**: Injects trading UI into Twitter pages
- **Background Worker**: Handles CORS-restricted API calls to localhost
- **Messaging**: Chrome runtime messaging between content/background scripts

### Flask Backend
- **CORS Enabled**: Allows requests from Chrome extension
- **Magic Wallet**: Uses py-clob-client with Magic wallet authentication
- **Real Trading**: Connects to Polymarket CLOB API for live trading
- **Sample Data**: Falls back to JSON files when API unavailable

### Data Flow
```
Twitter Page → Content Script → Background Script → Flask API → Polymarket API
                     ↓
              Trading Interface with Real-time Updates
```

## 🎯 Usage

### Market Trading
1. Open X (Twitter) in Chrome
2. Look for Polymarket icon next to other tweet buttons
3. Click to open trading interface
4. Use ← → arrows to navigate between events
5. Click YES/NO, enter amount, execute trades

### Position Viewing
1. Visit any Twitter profile page
2. Positions section appears above tweet tabs
3. Toggle between Open/Closed positions
4. View real P&L and position details

## 📊 Market Data Sources

- **Live API**: Real-time data from Polymarket CLOB API
- **Sample Data**: JSON files in `backend/data/` for development
- **Fallback Logic**: Gracefully handles API failures

## 🔐 Security

- **Environment Variables**: Sensitive keys stored in `.env`
- **No Key Exposure**: Private keys never sent to frontend
- **Magic Wallet**: Secure wallet integration via py-clob-client
- **CORS Protection**: Backend only accepts requests from extension

## 🧪 Development

### Start Backend Server
```bash
./scripts/start_trading.sh
```

### Load Extension in Chrome
1. Navigate to `chrome://extensions/`
2. Enable "Developer mode"
3. Click "Load unpacked" → select `extension/` folder

### Backend API Endpoints
- `GET /api/market` - Single market data
- `GET /api/events` - Multiple events for carousel
- `GET /api/positions` - User's open positions
- `GET /api/closed-positions` - User's closed positions
- `POST /api/trade` - Execute trades

## 📈 Recent Updates

- **Event Carousel System**: Navigate between multiple markets
- **Position API Integration**: Real position data from Polymarket
- **UI/UX Improvements**: Better button highlighting, profit calculations
- **Code Cleanup**: Organized file structure, removed test files
- **Multi-market Support**: Candidate cards with images and percentages

---

Built with Flask, Chrome Extensions API, and Polymarket CLOB API