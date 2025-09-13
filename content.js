// Fake Polymarket data for testing
const FAKE_MARKET_DATA = [
  {
    id: 1,
    title: "Will Bitcoin reach $100,000 by end of 2024?",
    yesPrice: 0.67,
    noPrice: 0.33,
    volume: "$2.5M",
    description: "Market resolves YES if Bitcoin (BTC) trades at or above $100,000 on any major exchange before January 1, 2025.",
    chart: "📈"
  },
  {
    id: 2,
    title: "Will Donald Trump win the 2024 Presidential Election?",
    yesPrice: 0.52,
    noPrice: 0.48,
    volume: "$15.2M",
    description: "Market resolves YES if Donald Trump is elected President in the 2024 US Presidential Election.",
    chart: "📊"
  },
  {
    id: 3,
    title: "Will OpenAI release GPT-5 in 2024?",
    yesPrice: 0.23,
    noPrice: 0.77,
    volume: "$1.8M",
    description: "Market resolves YES if OpenAI officially releases a model named GPT-5 before January 1, 2025.",
    chart: "📉"
  }
];

// Mock user position data
const MOCK_USER_POSITIONS = [
  {
    id: 1,
    title: "Bitcoin reaches $100k by 2024",
    position: "YES",
    shares: 250,
    avgPrice: 0.64,
    currentPrice: 0.67,
    pnl: 7.5,
    status: "open",
    volume: "$2.5M"
  },
  {
    id: 2,
    title: "Trump wins 2024 Election",
    position: "NO",
    shares: 180,
    avgPrice: 0.51,
    currentPrice: 0.48,
    pnl: 5.4,
    status: "open",
    volume: "$15.2M"
  },
  {
    id: 3,
    title: "GPT-5 released in 2024",
    position: "NO",
    shares: 320,
    avgPrice: 0.82,
    currentPrice: 0.77,
    pnl: 16.0,
    status: "open",
    volume: "$1.8M"
  },
  {
    id: 4,
    title: "Tesla stock above $300",
    position: "YES",
    shares: 150,
    avgPrice: 0.45,
    currentPrice: 0.62,
    pnl: 25.5,
    status: "closed",
    volume: "$890K"
  },
  {
    id: 5,
    title: "Fed cuts rates in Q1 2024",
    position: "NO",
    shares: 200,
    avgPrice: 0.73,
    currentPrice: 0.15,
    pnl: -116.0,
    status: "closed",
    volume: "$3.1M"
  }
];

let marketNotesPopup = null;

// Function to create position card
function createPositionCard(position) {
  const pnlClass = position.pnl >= 0 ? 'positive' : 'negative';
  const pnlSign = position.pnl >= 0 ? '+' : '';
  const statusBadge = position.status === 'open' ? 'OPEN' : 'CLOSED';
  const positionColor = position.position === 'YES' ? 'yes-position' : 'no-position';

  return `
    <div class="position-card" data-position-id="${position.id}">
      <div class="position-header">
        <div class="position-badges">
          <span class="position-badge ${positionColor}">${position.position}</span>
          <span class="status-badge ${position.status}">${statusBadge}</span>
        </div>
        <div class="position-pnl ${pnlClass}">${pnlSign}$${Math.abs(position.pnl)}</div>
      </div>
      <h4 class="position-title">${position.title}</h4>
      <div class="position-stats">
        <div class="stat-item">
          <span class="stat-label">Shares</span>
          <span class="stat-value">${position.shares}</span>
        </div>
        <div class="stat-item">
          <span class="stat-label">Avg Price</span>
          <span class="stat-value">${Math.round(position.avgPrice * 100)}¢</span>
        </div>
        <div class="stat-item">
          <span class="stat-label">Current</span>
          <span class="stat-value">${Math.round(position.currentPrice * 100)}¢</span>
        </div>
      </div>
      <div class="position-volume">Volume: ${position.volume}</div>
    </div>
  `;
}

// Function to create positions carousel
function createPositionsCarousel() {
  const openPositions = MOCK_USER_POSITIONS.filter(p => p.status === 'open');
  const closedPositions = MOCK_USER_POSITIONS.filter(p => p.status === 'closed');

  return `
    <div class="polymarket-positions-section">
      <div class="positions-header">
        <h3>Polymarket Positions</h3>
        <div class="positions-tabs">
          <button class="tab-button active" data-tab="open">Open (${openPositions.length})</button>
          <button class="tab-button" data-tab="closed">Closed (${closedPositions.length})</button>
        </div>
      </div>
      <div class="positions-carousel">
        <button class="carousel-nav prev" aria-label="Previous">‹</button>
        <div class="positions-container">
          <div class="positions-track" data-tab-content="open">
            ${openPositions.map(position => createPositionCard(position)).join('')}
          </div>
          <div class="positions-track hidden" data-tab-content="closed">
            ${closedPositions.map(position => createPositionCard(position)).join('')}
          </div>
        </div>
        <button class="carousel-nav next" aria-label="Next">›</button>
      </div>
    </div>
  `;
}

// Function to inject positions section on profile pages
function injectPositionsSection() {
  // Check if we're on a profile page (not home, explore, notifications, etc.)
  const path = window.location.pathname;
  if (path === '/' || path === '/home' || path === '/explore' || path === '/notifications' ||
      path === '/messages' || path === '/bookmarks' || path === '/lists' ||
      path === '/communities' || path === '/premium' || path === '/jobs' ||
      path.startsWith('/i/') || path.startsWith('/settings') ||
      path.includes('/status/') || path.includes('/photo/') ||
      !path.match(/^\/[a-zA-Z0-9_]+$/)) {
    return;
  }

  // Check if already injected globally
  if (document.querySelector('.polymarket-positions-section')) return;

  // Find the tabs section (Posts, Replies, Media, etc.)
  const tabsList = document.querySelector('[role="tablist"]');
  if (!tabsList) return;

  // Create and insert positions section
  const positionsContainer = document.createElement('div');
  positionsContainer.innerHTML = createPositionsCarousel();

  // Insert before the tabs
  tabsList.parentElement.insertBefore(positionsContainer.firstElementChild, tabsList);

  // Add event listeners for carousel functionality
  setupCarouselListeners();
}

// Function to setup carousel event listeners
function setupCarouselListeners() {
  const positionsSection = document.querySelector('.polymarket-positions-section');
  if (!positionsSection) return;

  const tabButtons = positionsSection.querySelectorAll('.tab-button');
  const prevBtn = positionsSection.querySelector('.carousel-nav.prev');
  const nextBtn = positionsSection.querySelector('.carousel-nav.next');
  let currentTab = 'open';
  let scrollPosition = 0;

  // Tab switching
  tabButtons.forEach(button => {
    button.addEventListener('click', () => {
      const tab = button.dataset.tab;

      // Update active tab
      tabButtons.forEach(btn => btn.classList.remove('active'));
      button.classList.add('active');

      // Show/hide content
      const tracks = positionsSection.querySelectorAll('.positions-track');
      tracks.forEach(track => {
        if (track.dataset.tabContent === tab) {
          track.classList.remove('hidden');
        } else {
          track.classList.add('hidden');
        }
      });

      currentTab = tab;
      scrollPosition = 0;
      updateCarouselPosition();
    });
  });

  // Carousel navigation
  prevBtn.addEventListener('click', () => {
    scrollPosition = Math.max(0, scrollPosition - 300);
    updateCarouselPosition();
  });

  nextBtn.addEventListener('click', () => {
    const container = positionsSection.querySelector(`[data-tab-content="${currentTab}"]`);
    const maxScroll = container.scrollWidth - container.parentElement.clientWidth;
    scrollPosition = Math.min(maxScroll, scrollPosition + 300);
    updateCarouselPosition();
  });

  function updateCarouselPosition() {
    const activeTrack = positionsSection.querySelector(`[data-tab-content="${currentTab}"]:not(.hidden)`);
    if (activeTrack) {
      activeTrack.style.transform = `translateX(-${scrollPosition}px)`;
    }
  }

  // Add click handlers for position cards
  const positionCards = positionsSection.querySelectorAll('.position-card');
  positionCards.forEach(card => {
    card.addEventListener('click', () => {
      const positionId = parseInt(card.dataset.positionId);
      const position = MOCK_USER_POSITIONS.find(p => p.id === positionId);

      if (position) {
        // Convert position to market data format
        const marketData = {
          title: position.title,
          yesPrice: position.position === 'YES' ? position.currentPrice : 1 - position.currentPrice,
          noPrice: position.position === 'NO' ? position.currentPrice : 1 - position.currentPrice,
          volume: position.volume,
          description: `Market for "${position.title}". Current position: ${position.position} at ${Math.round(position.currentPrice * 100)}¢`,
          chart: position.pnl >= 0 ? "📈" : "📉"
        };

        // Close existing popup
        if (marketNotesPopup) {
          marketNotesPopup.remove();
          marketNotesPopup = null;
        }

        // Create and show popup (same as tweet context for navigation controls)
        marketNotesPopup = createMarketNotesPopup(marketData, 'tweet');
        document.body.appendChild(marketNotesPopup);

        // Position popup to the right side of screen
        marketNotesPopup.style.position = 'fixed';
        marketNotesPopup.style.right = '20px';
        marketNotesPopup.style.top = '100px';
        marketNotesPopup.style.zIndex = '10000';

        // Add event handlers (same as tweet popups)
        setupMarketNotesHandlers();
      }
    });
  });
}

// Function to create Polymarket button
function createPolymarketButton() {
  const button = document.createElement('button');
  const logoUrl = chrome.runtime.getURL('icons/pmarket.png');
  button.innerHTML = `
    <div class="polymarket-button-content">
      <img src="${logoUrl}" alt="Polymarket" width="16" height="16" />
    </div>
  `;
  button.className = 'polymarket-note-button';
  button.title = 'View Market Notes';
  button.setAttribute('data-testid', 'polymarket-note');

  return button;
}

// Function to create Polymarket button styled like Grok button
function createPolymarketButtonForHeader() {
  const logoUrl = chrome.runtime.getURL('icons/pmarket.png');

  const buttonContainer = document.createElement('div');
  buttonContainer.className = 'css-175oi2r r-18u37iz r-1h0z5md';

  buttonContainer.innerHTML = `
    <button aria-label="Polymarket actions" role="button" class="css-175oi2r r-1777fci r-bt1l66 r-bztko3 r-lrvibr r-1loqt21 r-1ny4l3l polymarket-grok-button" type="button">
      <div dir="ltr" class="css-146c3p1 r-bcqeeo r-1ttztb7 r-qvutc0 r-37j5jr r-a023e6 r-rjixqe r-16dba41 r-1awozwy r-6koalj r-1h0z5md r-o7ynqc r-clp7b1 r-3s2u2q" style="color: rgb(113, 118, 123);">
        <div class="css-175oi2r r-xoduu5">
          <div class="css-175oi2r r-xoduu5 r-1p0dtai r-1d2f490 r-u8s1d r-zchlnj r-ipm5af r-1niwhzg r-sdzlij r-xf4iuw r-o7ynqc r-6416eg r-1ny4l3l"></div>
          <img src="${logoUrl}" alt="Polymarket" width="20" height="20" style="border-radius: 2px; opacity: 0.8;" />
        </div>
      </div>
    </button>
  `;

  return buttonContainer;
}

// Function to create market notes popup
function createMarketNotesPopup(marketData, context = 'tweet') {
  const popup = document.createElement('div');
  popup.className = 'market-notes-popup';

  const headerControls = context === 'tweet' ? `
    <div class="market-controls">
      <button class="all-markets-btn">All Markets</button>
      <button class="next-market-btn" title="Next Market">→</button>
    </div>
  ` : '';

  const carouselDots = context === 'tweet' ? `
    <div class="carousel-dots">
      ${FAKE_MARKET_DATA.map((_, index) => {
        const currentIndex = FAKE_MARKET_DATA.findIndex(m => m.title === marketData.title);
        const isActive = index === currentIndex;
        return `<button class="carousel-dot ${isActive ? 'active' : ''}" data-market-index="${index}"></button>`;
      }).join('')}
    </div>
  ` : '';

  popup.innerHTML = `
    <div class="market-notes-header draggable-header">
      <div class="header-left">
        <button class="close-popup">×</button>
        <h3>Market Notes</h3>
      </div>
      <div class="header-right">
        ${headerControls}
      </div>
    </div>
    <div class="market-notes-content">
      <div class="market-info">
        <h4>${marketData.title}</h4>
        <div class="market-chart">${marketData.chart}</div>
        <div class="market-prices">
          <div class="price-item yes">
            <span class="price-label">YES</span>
            <span class="price-value">${Math.round(marketData.yesPrice * 100)}¢</span>
          </div>
          <div class="price-item no">
            <span class="price-label">NO</span>
            <span class="price-value">${Math.round(marketData.noPrice * 100)}¢</span>
          </div>
        </div>
        <div class="market-volume">Volume: ${marketData.volume}</div>
        <p class="market-description">${marketData.description}</p>
      </div>
      ${carouselDots}
    </div>
  `;

  // Make popup draggable
  makeDraggable(popup);

  return popup;
}

// Function to make popup draggable
function makeDraggable(popup) {
  const header = popup.querySelector('.draggable-header');
  let isDragging = false;
  let dragOffset = { x: 0, y: 0 };

  header.addEventListener('mousedown', (e) => {
    // Don't start drag if clicking on close button
    if (e.target.classList.contains('close-popup')) return;

    isDragging = true;
    const rect = popup.getBoundingClientRect();
    dragOffset.x = e.clientX - rect.left;
    dragOffset.y = e.clientY - rect.top;

    header.style.cursor = 'grabbing';
    document.addEventListener('mousemove', handleMouseMove);
    document.addEventListener('mouseup', handleMouseUp);

    e.preventDefault();
  });

  function handleMouseMove(e) {
    if (!isDragging) return;

    const x = e.clientX - dragOffset.x;
    const y = e.clientY - dragOffset.y;

    // Keep popup within viewport bounds
    const popupRect = popup.getBoundingClientRect();
    const maxX = window.innerWidth - popupRect.width;
    const maxY = window.innerHeight - popupRect.height;

    const clampedX = Math.max(0, Math.min(x, maxX));
    const clampedY = Math.max(0, Math.min(y, maxY));

    popup.style.left = `${clampedX}px`;
    popup.style.top = `${clampedY}px`;
  }

  function handleMouseUp() {
    isDragging = false;
    header.style.cursor = 'grab';
    document.removeEventListener('mousemove', handleMouseMove);
    document.removeEventListener('mouseup', handleMouseUp);
  }
}

// Function to setup market notes popup handlers
function setupMarketNotesHandlers() {
  if (!marketNotesPopup) return;

  const closeBtn = marketNotesPopup.querySelector('.close-popup');
  const allMarketsBtn = marketNotesPopup.querySelector('.all-markets-btn');
  const nextMarketBtn = marketNotesPopup.querySelector('.next-market-btn');
  const carouselDots = marketNotesPopup.querySelectorAll('.carousel-dot');

  // Close handler
  if (closeBtn) {
    closeBtn.addEventListener('click', () => {
      marketNotesPopup.remove();
      marketNotesPopup = null;
    });
  }

  // All Markets handler - show list of related markets
  if (allMarketsBtn) {
    allMarketsBtn.addEventListener('click', () => {
      showAllMarketsModal();
    });
  }

  // Next Market handler - cycle to next related market
  if (nextMarketBtn) {
    nextMarketBtn.addEventListener('click', () => {
      showNextMarket();
    });
  }

  // Carousel dots handlers
  carouselDots.forEach(dot => {
    dot.addEventListener('click', () => {
      const marketIndex = parseInt(dot.dataset.marketIndex);
      const selectedMarket = FAKE_MARKET_DATA[marketIndex];

      if (selectedMarket) {
        updateMarketNotesContent(selectedMarket);
        updateCarouselDots(marketIndex);
      }
    });
  });
}

// Function to show all markets modal
function showAllMarketsModal() {
  const modal = document.createElement('div');
  modal.className = 'all-markets-modal';
  modal.innerHTML = `
    <div class="modal-overlay">
      <div class="modal-content">
        <div class="modal-header">
          <h3>Related Markets</h3>
          <button class="modal-close">×</button>
        </div>
        <div class="markets-list">
          ${FAKE_MARKET_DATA.map(market => `
            <div class="market-item" data-market-id="${market.id}">
              <h4>${market.title}</h4>
              <div class="market-prices-mini">
                <span class="yes-price">YES ${Math.round(market.yesPrice * 100)}¢</span>
                <span class="no-price">NO ${Math.round(market.noPrice * 100)}¢</span>
              </div>
              <div class="market-volume-mini">Volume: ${market.volume}</div>
            </div>
          `).join('')}
        </div>
      </div>
    </div>
  `;

  document.body.appendChild(modal);

  // Add event handlers
  const closeModal = () => {
    modal.remove();
  };

  modal.querySelector('.modal-close').addEventListener('click', closeModal);
  modal.querySelector('.modal-overlay').addEventListener('click', (e) => {
    if (e.target === modal.querySelector('.modal-overlay')) {
      closeModal();
    }
  });

  // Market selection handlers
  modal.querySelectorAll('.market-item').forEach(item => {
    item.addEventListener('click', () => {
      const marketId = parseInt(item.dataset.marketId);
      const selectedMarket = FAKE_MARKET_DATA.find(m => m.id === marketId);

      if (selectedMarket) {
        // Close modal
        closeModal();

        // Update current popup with selected market
        updateMarketNotesContent(selectedMarket);
      }
    });
  });
}

// Function to show next market
function showNextMarket() {
  const currentTitle = marketNotesPopup.querySelector('h4').textContent;
  const currentIndex = FAKE_MARKET_DATA.findIndex(m => m.title === currentTitle);
  const nextIndex = (currentIndex + 1) % FAKE_MARKET_DATA.length;
  const nextMarket = FAKE_MARKET_DATA[nextIndex];

  updateMarketNotesContent(nextMarket);
  updateCarouselDots(nextIndex);
}

// Function to update market notes content
function updateMarketNotesContent(marketData) {
  if (!marketNotesPopup) return;

  const content = marketNotesPopup.querySelector('.market-info');
  content.innerHTML = `
    <h4>${marketData.title}</h4>
    <div class="market-chart">${marketData.chart}</div>
    <div class="market-prices">
      <div class="price-item yes">
        <span class="price-label">YES</span>
        <span class="price-value">${Math.round(marketData.yesPrice * 100)}¢</span>
      </div>
      <div class="price-item no">
        <span class="price-label">NO</span>
        <span class="price-value">${Math.round(marketData.noPrice * 100)}¢</span>
      </div>
    </div>
    <div class="market-volume">Volume: ${marketData.volume}</div>
    <p class="market-description">${marketData.description}</p>
  `;
}

// Function to update carousel dots
function updateCarouselDots(activeIndex) {
  if (!marketNotesPopup) return;

  const dots = marketNotesPopup.querySelectorAll('.carousel-dot');
  dots.forEach((dot, index) => {
    if (index === activeIndex) {
      dot.classList.add('active');
    } else {
      dot.classList.remove('active');
    }
  });
}

// Function to position popup
function positionPopup(popup, buttonRect) {
  const viewportWidth = window.innerWidth;
  const viewportHeight = window.innerHeight;
  const popupWidth = 350;
  const popupHeight = 500; // max height from CSS

  // Find the tweet container to get its right edge
  const tweet = document.querySelector('[data-testid="tweet"]');
  let tweetRightEdge = viewportWidth * 0.6; // fallback

  if (tweet) {
    const tweetRect = tweet.getBoundingClientRect();
    tweetRightEdge = tweetRect.right;
  }

  // Position at right edge of tweet with small margin
  let left = tweetRightEdge + 20;
  let top = buttonRect.top;

  // If popup would go off screen horizontally, position to the left
  if (left + popupWidth > viewportWidth) {
    left = tweetRightEdge - popupWidth - 20;
  }

  // If still off screen, position based on button
  if (left < 0) {
    left = buttonRect.left - popupWidth - 10;
    if (left < 0) {
      left = buttonRect.right + 10;
    }
  }

  // If popup would go off screen vertically, adjust position
  if (top + popupHeight > viewportHeight) {
    top = Math.max(10, viewportHeight - popupHeight - 10);
  }

  // Ensure popup doesn't go above viewport
  if (top < 10) {
    top = 10;
  }

  popup.style.position = 'fixed';
  popup.style.left = `${left}px`;
  popup.style.top = `${top}px`;
  popup.style.zIndex = '10000';
}

// Function to inject Polymarket buttons
function injectPolymarketButtons() {
  // Find all tweets that don't already have a Polymarket button
  const tweets = document.querySelectorAll('[data-testid="tweet"]:not([data-polymarket-injected])');

  tweets.forEach((tweet) => {
    // Mark as processed
    tweet.setAttribute('data-polymarket-injected', 'true');

    // Find the main button container that contains both Grok and More buttons
    const mainButtonContainer = tweet.querySelector('.css-175oi2r.r-1kkk96v .css-175oi2r.r-1awozwy.r-18u37iz.r-1cmwbt1.r-1wtj0ep');
    if (!mainButtonContainer) return;

    // Create just the inner button structure (no parent wrapper)
    const polyButton = createPolymarketButtonForHeader();

    // Add click handler to the actual button inside the container
    const actualButton = polyButton.querySelector('button');
    actualButton.addEventListener('click', (e) => {
      e.preventDefault();
      e.stopPropagation();

      // Close existing popup if open
      if (marketNotesPopup) {
        marketNotesPopup.remove();
        marketNotesPopup = null;
      }

      // Get random market data for demo
      const randomMarket = FAKE_MARKET_DATA[Math.floor(Math.random() * FAKE_MARKET_DATA.length)];

      // Create and show popup
      marketNotesPopup = createMarketNotesPopup(randomMarket, 'tweet');
      document.body.appendChild(marketNotesPopup);

      // Position popup
      const buttonRect = actualButton.getBoundingClientRect();
      positionPopup(marketNotesPopup, buttonRect);

      // Add event handlers
      setupMarketNotesHandlers();
    });

    // Insert the Polymarket button as the first child in the main container
    mainButtonContainer.insertBefore(polyButton, mainButtonContainer.firstChild);
  });
}

// Close popup when clicking outside
document.addEventListener('click', (e) => {
  if (marketNotesPopup && !marketNotesPopup.contains(e.target) && !e.target.closest('.polymarket-note-button')) {
    marketNotesPopup.remove();
    marketNotesPopup = null;
  }
});

// Initial injection
setTimeout(() => {
  injectPolymarketButtons();
  injectPositionsSection();
}, 1000);

// Set up mutation observer to handle dynamic content
const observer = new MutationObserver((mutations) => {
  let shouldInject = false;

  mutations.forEach((mutation) => {
    mutation.addedNodes.forEach((node) => {
      if (node.nodeType === Node.ELEMENT_NODE) {
        // Check if new tweets were added
        if (node.matches && (node.matches('[data-testid="tweet"]') || node.querySelector('[data-testid="tweet"]'))) {
          shouldInject = true;
        }
      }
    });
  });

  if (shouldInject) {
    setTimeout(() => {
      injectPolymarketButtons();
      injectPositionsSection();
    }, 500);
  }
});

// Start observing
observer.observe(document.body, {
  childList: true,
  subtree: true
});

console.log('Polymarket Notes extension loaded');