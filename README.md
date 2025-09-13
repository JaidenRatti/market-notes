# Polymarket Notes - Chrome Extension

A Chrome extension that integrates Polymarket prediction markets with X (Twitter) to provide "Market Notes" - showing relevant market data as a source of truth alongside tweets.

## 🚀 Features

### Market Notes on Tweets
- **Polymarket Button**: Added next to Grok button on every tweet
- **Market Popup**: Shows related Polymarket events with:
  - Market title and description
  - Current YES/NO prices
  - Trading volume
  - Interactive chart visualization
  - Navigation controls (All Markets, Next Market)
  - Carousel dots for market switching

### Profile Position Tracking
- **User Positions**: View Polymarket positions on user profiles
- **Interactive Carousel**: Browse through open and closed positions
- **Detailed Cards**: Show position type, P&L, shares, prices
- **Click to View**: Click position cards to open market details

### Enhanced User Experience
- **Draggable Popups**: Move market notes anywhere on screen
- **Smart Positioning**: Auto-adjusts to stay within viewport
- **Theme Support**: Works with both light and dark X themes
- **Native Integration**: Seamlessly blends with X's interface

## 📦 Installation

### For Development
1. Clone this repository:
   ```bash
   git clone https://github.com/YOUR_USERNAME/polymarket-notes-extension.git
   cd polymarket-notes-extension
   ```

2. Open Chrome and navigate to `chrome://extensions/`

3. Enable "Developer mode" (toggle in top right)

4. Click "Load unpacked" and select the project folder

5. The extension should now be active on X.com!

### For Users
*Coming soon to Chrome Web Store*

## 🛠️ Development

### Project Structure
```
├── manifest.json          # Extension configuration
├── content.js             # Main content script
├── styles.css             # Extension styles
├── icons/
│   └── pmarket.png        # Polymarket logo
└── README.md              # This file
```

### Key Components

#### Content Script (`content.js`)
- **Button Injection**: Adds Polymarket buttons to tweets and profiles
- **Popup Management**: Creates and manages market notes popups
- **Event Handling**: Manages clicks, navigation, and interactions
- **Data Management**: Handles mock market and position data

#### Styling (`styles.css`)
- **Native Integration**: Matches X's design system
- **Theme Support**: Dark/light theme compatibility
- **Responsive Design**: Works across different screen sizes
- **Interactive Elements**: Hover states and transitions

## 🔧 Technical Details

### Manifest v3 Compatibility
- Uses modern Chrome extension APIs
- Content script injection for X.com domains
- Web accessible resources for assets

### DOM Manipulation
- Targets specific X interface elements
- Maintains compatibility with X's dynamic loading
- Uses mutation observers for real-time updates

### Features Implementation
- **Market Notes**: Dynamic popup with navigation controls
- **Position Cards**: Interactive carousel with real-time data
- **Drag & Drop**: Custom draggable implementation
- **Smart Positioning**: Viewport-aware popup placement

## 📊 Mock Data

Currently uses mock data for demonstration:
- **Market Data**: 3 sample prediction markets (Bitcoin, Election, GPT-5)
- **User Positions**: 5 sample positions (3 open, 2 closed)
- **Real API Integration**: Coming in future releases

## 🎯 Roadmap

- [ ] **Real Polymarket API Integration**
- [ ] **Account Linking System**
- [ ] **Tweet-to-Market Matching Algorithm**
- [ ] **Historical Position Tracking**
- [ ] **Market Notifications**
- [ ] **Advanced Analytics**

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit your changes: `git commit -m 'Add amazing feature'`
4. Push to the branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Polymarket](https://polymarket.com) for the prediction market platform
- [X (Twitter)](https://x.com) for the social media integration
- Chrome Extensions team for the development platform

---

**Note**: This extension is currently in development and uses mock data. Real Polymarket integration coming soon!