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

### AI-Powered Tweet Analysis 🧠
- **Smart Market Discovery**: Automatically analyzes tweet content to find relevant Polymarket events
- **Cohere AI Integration**: Uses advanced NLP to understand tweet context and sentiment
- **Polymarket Search**: Searches live Polymarket API for active, tradeable markets
- **Relevance Ranking**: AI ranks markets by relevance to the specific tweet content
- **Fallback Support**: Falls back to sample data if tweet analysis fails

### Market Event Carousel
- **AI-Generated Events**: Shows AI-discovered markets relevant to the tweet
- **Navigation Controls**: Use ← → arrows to browse through discovered markets
- **Event Counter**: Shows current position (e.g., "3 / 6" events)
- **Mixed Market Types**: Supports both single-market and multi-candidate events

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
# Required for trading
magickey=your_magic_wallet_private_key
funder=your_polymarket_wallet_address

# Required for AI tweet analysis
COHERE_API_KEY=your_cohere_api_key
```

Get API keys:
- **Magic wallet keys**: From your Polymarket account settings
- **Cohere API key**: From [Cohere Dashboard](https://dashboard.cohere.com/api-keys)

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
Twitter Page → Extract Tweet Text → AI Analysis Pipeline → Relevant Markets
     ↓              ↓                       ↓                    ↓
Content Script → Background Script → Flask API → Cohere + Polymarket APIs
     ↓
Trading Interface with AI-Discovered Markets
```

## 🎯 Usage

### AI-Powered Market Trading
1. Open X (Twitter) in Chrome
2. Look for Polymarket icon next to other tweet buttons
3. Click button on any tweet - AI will analyze the content
4. View AI-discovered markets relevant to the tweet
5. Use ← → arrows to navigate between discovered events
6. Click YES/NO, enter amount, execute trades on relevant markets

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
- `POST /api/analyze-tweet` - **NEW**: AI-powered tweet analysis
- `GET /api/positions` - User's open positions
- `GET /api/closed-positions` - User's closed positions
- `POST /api/trade` - Execute trades

## 📈 Recent Updates

- **🧠 AI-Powered Tweet Analysis**: Automatically discovers relevant markets for any tweet
- **🤖 Cohere Integration**: Advanced NLP for tweet sentiment and context analysis
- **🔍 Smart Market Search**: Live Polymarket API search with AI relevance ranking
- **🎯 Context-Aware Trading**: Show only markets relevant to the specific tweet
- **📊 Pipeline Integration**: Complete tweet-to-market analysis pipeline
- **Position API Integration**: Real position data from Polymarket
- **UI/UX Improvements**: Better button highlighting, profit calculations
- **Code Cleanup**: Organized file structure, removed test files

---

Built with Flask, Chrome Extensions API, Polymarket CLOB API, and Cohere AI