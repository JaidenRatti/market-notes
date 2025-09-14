// Real market data will be fetched from backend
// All position data now comes from live Polymarket API

let marketNotesPopup = null;
let currentEventData = null;
let currentEventIndex = 0;
let allEvents = [];

// Helper functions for price validation
function validatePrice(price, fallback = 0.01) {
  if (isNaN(price) || !isFinite(price) || price <= 0) {
    return fallback;
  }
  // Ensure price is between 1¢ and 99¢
  return Math.max(0.01, Math.min(0.99, price));
}

function formatCentPrice(price) {
  const validPrice = validatePrice(price);
  const cents = Math.round(validPrice * 100);
  return `${cents}¢`;
}

function validatePayout(payout) {
  if (isNaN(payout) || !isFinite(payout) || payout < 0) {
    return 0;
  }
  return payout;
}

// Function to create position card
function createPositionCard(position) {
  const pnlClass = position.pnl >= 0 ? 'positive' : 'negative';
  const pnlSign = position.pnl >= 0 ? '+' : '';
  const statusBadge = position.status === 'open' ? 'OPEN' : 'CLOSED';
  const positionColor = position.position === 'YES' || position.position === 'Yes' ? 'yes-position' : 'no-position';
  
  // Handle both old mock data and new real data formats
  const shares = position.shares || position.totalBought || 0;
  const avgPrice = position.avgPrice || 0;
  const currentPrice = position.currentPrice || position.curPrice || 0;
  const volume = position.volume || position.currentValue || 0;
  
  // Format shares to show reasonable precision
  const formattedShares = shares < 1 ? shares.toFixed(4) : shares.toFixed(2);
  
  return `
    <div class="position-card" data-position-id="${position.id}">
      <div class="position-header">
        <div class="position-badges">
          <span class="position-badge ${positionColor}">${position.position}</span>
          <span class="status-badge ${position.status}">${statusBadge}</span>
        </div>
        <div class="position-pnl ${pnlClass}">${pnlSign}$${Math.abs(position.pnl).toFixed(2)}</div>
      </div>
      <h4 class="position-title">${position.title}</h4>
      <div class="position-stats">
        <div class="stat-item">
          <span class="stat-label">Shares</span>
          <span class="stat-value">${formattedShares}</span>
        </div>
        <div class="stat-item">
          <span class="stat-label">Avg Price</span>
          <span class="stat-value">${Math.round(avgPrice * 100)}¢</span>
        </div>
        <div class="stat-item">
          <span class="stat-label">Current</span>
          <span class="stat-value">${Math.round(currentPrice * 100)}¢</span>
        </div>
      </div>
      <div class="position-volume">Value: ${typeof volume === 'string' ? volume : `$${volume.toFixed(2)}`}</div>
    </div>
  `;
}

// Function to create positions carousel with real data
async function createPositionsCarousel() {
  console.log('🔍 [DEBUG] Creating positions carousel with real data...');
  
  // Fetch both open and closed positions separately
  const [realOpenPositions, realClosedPositions] = await Promise.all([
    fetchPositions(),
    fetchClosedPositions()
  ]);
  
  let openPositions = [];
  let closedPositions = [];
  let isLiveData = false;
  
  // Process open positions
  if (realOpenPositions && realOpenPositions.length > 0) {
    console.log('✅ [DEBUG] Using real open positions data:', realOpenPositions.length, 'positions');
    openPositions = realOpenPositions;
    isLiveData = true;
  } else if (realOpenPositions && realOpenPositions.length === 0) {
    console.log('⚠️ [DEBUG] No open positions found in account');
    openPositions = [];
    isLiveData = true;
  }
  
  // Process closed positions
  if (realClosedPositions && realClosedPositions.length > 0) {
    console.log('✅ [DEBUG] Using real closed positions data:', realClosedPositions.length, 'positions');
    closedPositions = realClosedPositions;
    isLiveData = true;
  } else if (realClosedPositions && realClosedPositions.length === 0) {
    console.log('⚠️ [DEBUG] No closed positions found in account');
    closedPositions = [];
    isLiveData = true;
  }
  
  // If neither API worked, mark as not live
  if (!realOpenPositions && !realClosedPositions) {
    console.log('❌ [DEBUG] Failed to fetch positions, showing connection error');
    isLiveData = false;
  }

  // Create open positions HTML
  const openStateHTML = openPositions.length === 0 ? `
    <div class="positions-track empty-state" data-tab-content="open">
      <div class="empty-state-content">
        <div class="empty-icon">📊</div>
        <div class="empty-title">${isLiveData ? 'No Active Positions' : 'Loading Positions...'}</div>
        <div class="empty-subtitle">${isLiveData ? 'Start trading on Polymarket to see your positions here' : 'Connecting to Polymarket API...'}</div>
      </div>
    </div>
  ` : `
    <div class="positions-track" data-tab-content="open">
      ${openPositions.map(position => createPositionCard(position)).join('')}
    </div>
  `;

  // Create closed positions HTML
  const closedStateHTML = closedPositions.length === 0 ? `
    <div class="positions-track hidden empty-state" data-tab-content="closed">
      <div class="empty-state-content">
        <div class="empty-icon">📊</div>
        <div class="empty-title">${isLiveData ? 'No Closed Positions' : 'Loading Closed Positions...'}</div>
        <div class="empty-subtitle">${isLiveData ? 'Closed positions will appear here after you exit trades' : 'Connecting to Polymarket API...'}</div>
      </div>
    </div>
  ` : `
    <div class="positions-track hidden" data-tab-content="closed">
      ${closedPositions.map(position => createPositionCard(position)).join('')}
    </div>
  `;

  return `
    <div class="polymarket-positions-section">
      <div class="positions-header">
        <h3>Polymarket Positions ${isLiveData ? '(Live)' : '(Connecting...)'}</h3>
        <div class="positions-tabs">
          <button class="tab-button active" data-tab="open">Open (${openPositions.length})</button>
          <button class="tab-button" data-tab="closed">Closed (${closedPositions.length})</button>
        </div>
      </div>
      <div class="positions-carousel">
        <button class="carousel-nav prev" aria-label="Previous">‹</button>
        <div class="positions-container">
          ${openStateHTML}
          ${closedStateHTML}
        </div>
        <button class="carousel-nav next" aria-label="Next">›</button>
      </div>
    </div>
  `;
}

// Function to inject positions section on profile pages
async function injectPositionsSection() {
  // Check if we're on a profile page - must be exactly /@username or /username format
  const path = window.location.pathname;

  // Exclude specific known pages
  if (path === '/' || path === '/home' || path === '/explore' || path === '/notifications' ||
      path === '/messages' || path === '/bookmarks' || path === '/lists' ||
      path === '/communities' || path === '/premium' || path === '/jobs' ||
      path === '/search' || path.startsWith('/search?') ||
      path.startsWith('/i/') || path.startsWith('/settings') ||
      path.includes('/status/') || path.includes('/photo/') ||
      path.includes('/with_replies') || path.includes('/media') ||
      path.includes('/likes') || path.includes('/following') || path.includes('/followers')) {
    return;
  }

  // Profile pages should match exactly /@username or /username (no additional paths)
  if (!path.match(/^\/[a-zA-Z0-9_]+$/)) {
    return;
  }

  // Check if already injected - more comprehensive check
  const existingSection = document.querySelector('.polymarket-positions-section');
  if (existingSection) {
    console.log('⚠️ [DEBUG] Positions section already exists, skipping injection');
    return;
  }

  // Find the tabs section (Posts, Replies, Media, etc.)
  const tabsList = document.querySelector('[role="tablist"]');
  if (!tabsList) return;

  // Mark that we're injecting to prevent race conditions
  document.body.setAttribute('data-positions-injecting', 'true');

  try {
    // Create and insert positions section
    const positionsContainer = document.createElement('div');
    const carouselHTML = await createPositionsCarousel();
    positionsContainer.innerHTML = carouselHTML;

    // Insert before the tabs list (original working method)
    tabsList.parentElement.insertBefore(positionsContainer.firstElementChild, tabsList);

    // Add event listeners for carousel functionality
    setupCarouselListeners();
    
    console.log('✅ [DEBUG] Positions section injected successfully');
  } catch (error) {
    console.error('❌ [DEBUG] Error injecting positions:', error);
  } finally {
    // Remove the injecting flag
    document.body.removeAttribute('data-positions-injecting');
  }
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

  // Add click handlers for position cards (now just for visual feedback)
  const positionCards = positionsSection.querySelectorAll('.position-card');
  positionCards.forEach(card => {
    card.addEventListener('click', () => {
      console.log('🔄 [DEBUG] Position card clicked');
      // Just provide visual feedback - no popup
      card.style.transform = 'scale(0.98)';
      setTimeout(() => {
        card.style.transform = 'scale(1)';
      }, 150);
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

// Function to create market notes popup with trading
function createMarketNotesPopup(marketData, context = 'tweet') {
  const popup = document.createElement('div');
  popup.className = 'market-notes-popup';

  // Check if this is carousel data
  const isCarousel = marketData.carousel && marketData.events && allEvents.length > 0;
  const eventToDisplay = isCarousel ? currentEventData : marketData;

  // Show carousel controls if we have multiple events or if we're in carousel mode
  const carouselControls = (isCarousel || (allEvents && allEvents.length > 1)) ? `
    <div class="event-carousel-controls">
      <button class="event-nav-btn prev-event-btn" title="Previous Event">‹</button>
      <span class="event-counter">${currentEventIndex + 1} / ${allEvents && allEvents.length > 0 ? allEvents.length : 1}</span>
      <button class="event-nav-btn next-event-btn" title="Next Event">›</button>
    </div>
  ` : '';

  // Always show carousel controls if we have multiple events available
  let headerControls = '';
  if (context === 'tweet') {
    if (isCarousel || (allEvents && allEvents.length > 1)) {
      // Show carousel controls
      headerControls = '';  // Carousel controls are in carouselControls, not headerControls
    } else {
      // Show switch button only for single events
      headerControls = `
        <div class="market-controls">
          <button class="switch-market-btn" title="Switch Market Type">➡️</button>
        </div>
      `;
    }
  }

  // Check if this is a multi-market event
  if (eventToDisplay.type === 'multi') {
    popup.innerHTML = createMultiMarketPopupHTML(eventToDisplay, headerControls, carouselControls);
  } else {
    popup.innerHTML = createSingleMarketPopupHTML(eventToDisplay, headerControls, carouselControls);
  }

  // Add carousel event listeners if this is carousel data
  if (isCarousel) {
    setupCarouselEventListeners(popup);
  }

  // Make popup draggable
  makeDraggable(popup);

  return popup;
}

// Function to create single market popup HTML
function createSingleMarketPopupHTML(marketData, headerControls, carouselControls = '') {
  return `
    <div class="market-notes-header draggable-header">
      <div class="header-left">
        <button class="close-popup">×</button>
        <h3>Market Notes</h3>
      </div>
      <div class="header-right">
        ${headerControls}
        ${carouselControls}
      </div>
    </div>
    <div class="market-notes-content">
      <div class="market-info">
        <h4>${marketData.title || marketData.question}</h4>

        <div class="market-volume">Volume: ${marketData.volume}</div>

        <h4>Place Trade</h4>
        <div class="trade-form">
          <div class="side-selector">
            <button class="side-btn yes-side-btn active" data-side="YES">YES ${formatCentPrice(marketData.yesPrice || marketData.yes_price)}</button>
            <button class="side-btn no-side-btn" data-side="NO">NO ${formatCentPrice(marketData.noPrice || marketData.no_price)}</button>
          </div>
          <div class="amount-input-group">
            <label>Amount (USD):</label>
            <input type="text" class="amount-input" placeholder="$0" inputmode="decimal">
            <div class="potential-winnings">
              <span class="winnings-text">Potential payout: <span class="winnings-amount">$0.00</span></span>
              <span class="profit-text">Profit: <span class="profit-amount">$0.00</span></span>
            </div>
          </div>
          <div class="trade-buttons">
            <button class="execute-trade-btn">Execute Trade</button>
          </div>
        </div>
        <div class="trade-status"></div>

        <div class="market-description-section">
          <h5>Market Details</h5>
          <p class="market-description">${marketData.description}</p>
        </div>
      </div>
    </div>
  `;
}


// Function to create multi-market popup HTML
function createMultiMarketPopupHTML(marketData, headerControls, carouselControls = '') {
  const marketsHTML = marketData.markets.map((market, index) => {
    // No default selection - user must click to activate
    const candidateImage = market.image || market.icon || '';

    // Convert YES price to percentage (e.g., 0.81 -> 81%)
    const rawPercentage = market.yes_price * 100;
    const oddsPercentage = rawPercentage < 1 && rawPercentage > 0 ? '<1' : Math.round(rawPercentage);

    return `
      <div class="multi-market-item" data-market-id="${market.id}">
        <div class="market-candidate-header">
          <div class="candidate-info">
            ${candidateImage ? `<img src="${candidateImage}" alt="${market.candidate}" class="candidate-image">` : ''}
            <div class="candidate-details">
              <h5>${market.candidate}</h5>
              <div class="market-volume">Volume: ${market.volume}</div>
            </div>
          </div>
          <div class="market-probability">
            <span class="probability-percentage">${oddsPercentage}%</span>
          </div>
        </div>
        <!-- Trading interface will be dynamically added when user clicks -->
      </div>
    `;
  }).join('');

  return `
    <div class="market-notes-header draggable-header">
      <div class="header-left">
        <button class="close-popup">×</button>
        <h3>Market Notes</h3>
      </div>
      <div class="header-right">
        ${headerControls}
        ${carouselControls}
      </div>
    </div>
    <div class="market-notes-content">
      <div class="market-info">
        <h4>${marketData.title}</h4>
        <div class="market-volume">Total Volume: ${marketData.volume}</div>

        <div class="multi-markets-container">
          ${marketsHTML}
        </div>

        <div class="market-description-section">
          <h5>Event Details</h5>
          <p class="market-description">${marketData.description}</p>
        </div>
      </div>
    </div>
  `;
}

// Function to setup carousel event listeners for event navigation
function setupCarouselEventListeners(popup) {
  const prevBtn = popup.querySelector('.prev-event-btn');
  const nextBtn = popup.querySelector('.next-event-btn');

  if (prevBtn && nextBtn) {
    prevBtn.addEventListener('click', (e) => {
      e.preventDefault();
      e.stopPropagation();
      navigateToEvent(-1);
    });

    nextBtn.addEventListener('click', (e) => {
      e.preventDefault();
      e.stopPropagation();
      navigateToEvent(1);
    });
  }
}

// Function to navigate between events in carousel
function navigateToEvent(direction) {
  if (allEvents.length === 0) return;

  // Update index with wraparound
  currentEventIndex = (currentEventIndex + direction + allEvents.length) % allEvents.length;
  currentEventData = allEvents[currentEventIndex];

  console.log('🎠 [DEBUG] Navigated to event', currentEventIndex + 1, 'of', allEvents.length);

  // Update the popup content
  updatePopupContent();
}

// Function to update popup content with new event
function updatePopupContent() {
  if (!marketNotesPopup || !currentEventData) return;

  const carouselControls = `
    <div class="event-carousel-controls">
      <button class="event-nav-btn prev-event-btn" title="Previous Event">‹</button>
      <span class="event-counter">${currentEventIndex + 1} / ${allEvents.length}</span>
      <button class="event-nav-btn next-event-btn" title="Next Event">›</button>
    </div>
  `;

  const headerControls = ``; // No header controls needed in carousel mode

  // Generate new content based on event type
  let newContent;
  if (currentEventData.type === 'multi') {
    newContent = createMultiMarketPopupHTML(currentEventData, headerControls, carouselControls);
  } else {
    newContent = createSingleMarketPopupHTML(currentEventData, headerControls, carouselControls);
  }

  // Update popup content
  marketNotesPopup.innerHTML = newContent;

  // Re-setup all event listeners
  setupCarouselEventListeners(marketNotesPopup);
  setupMarketNotesHandlers();
  makeDraggable(marketNotesPopup);
}

// Function to make popup draggable
function makeDraggable(popup) {
  const header = popup.querySelector('.draggable-header');
  let isDragging = false;
  let dragOffset = { x: 0, y: 0 };

  header.addEventListener('mousedown', (e) => {
    // Don't start drag if clicking on close button or any button in header
    if (e.target.classList.contains('close-popup') ||
        e.target.classList.contains('switch-market-btn') ||
        e.target.classList.contains('refresh-prices-btn') ||
        e.target.classList.contains('all-markets-btn') ||
        e.target.classList.contains('event-nav-btn') ||
        e.target.classList.contains('prev-event-btn') ||
        e.target.classList.contains('next-event-btn')) return;

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

// Global variable to track current market type
let currentMarketType = 'multi'; // Start with multi-market by default

// Function to switch between market types
async function switchMarketType() {
  console.log('🔄 [DEBUG] Current market type:', currentMarketType);

  // Cycle through market types: single -> multi -> carousel -> single
  let newMarketType;
  if (currentMarketType === 'single') {
    newMarketType = 'multi';
  } else if (currentMarketType === 'multi') {
    newMarketType = 'carousel';
  } else {
    newMarketType = 'single';
  }

  currentMarketType = newMarketType;

  console.log('🔄 [DEBUG] Switching to:', newMarketType);

  // Fetch new market data
  const newMarketData = await fetchMarketDataWithType(newMarketType);

  if (newMarketData && marketNotesPopup) {
    // Get the current popup position
    const currentRect = marketNotesPopup.getBoundingClientRect();

    // Remove old popup
    marketNotesPopup.remove();

    // Create new popup with new data
    marketNotesPopup = createMarketNotesPopup(newMarketData, 'tweet');
    document.body.appendChild(marketNotesPopup);

    // Restore position
    marketNotesPopup.style.position = 'fixed';
    marketNotesPopup.style.left = `${currentRect.left}px`;
    marketNotesPopup.style.top = `${currentRect.top}px`;
    marketNotesPopup.style.zIndex = '10000';

    // Setup handlers for new popup
    setupMarketNotesHandlers();

    console.log('✅ [DEBUG] Successfully switched to', newMarketType, 'market type');
  } else {
    console.error('❌ [DEBUG] Failed to switch market type');
    alert('Failed to switch market type. Please try again.');
  }
}

// API functions using Chrome messaging (bypasses CORS/blocking)
async function fetchMarketData() {
  return fetchMarketDataWithType(currentMarketType);
}

// Enhanced function to fetch specific market type or all events for carousel
async function fetchMarketDataWithType(marketType) {
  console.log('🔍 [DEBUG] Starting fetchMarketData via Chrome messaging...');

  return new Promise((resolve, reject) => {
    chrome.runtime.sendMessage({
      action: 'fetchMarketData',
      marketType: marketType
    }, (response) => {
      if (chrome.runtime.lastError) {
        console.error('❌ [DEBUG] Chrome runtime error:', chrome.runtime.lastError);
        resolve(null);
        return;
      }

      console.log('🔍 [DEBUG] Got response from background:', response);

      if (response && response.success && response.data) {
        console.log('✅ [DEBUG] Successfully got market data!');

        // Check if this is carousel data
        if (response.data.carousel && response.data.events) {
          console.log('🎠 [DEBUG] Received carousel data with', response.data.events.length, 'events');
          allEvents = response.data.events;
          currentEventIndex = 0;
          currentEventData = allEvents[0];
          resolve(response.data);
        } else {
          // Single event data
          resolve(response.data);
        }
      } else {
        console.error('❌ [DEBUG] Background script failed:', response?.error);
        resolve(null);
      }
    });
  });
}

async function fetchLivePrices() {
  console.log('🔍 [DEBUG] Fetching live prices via Chrome messaging...');

  return new Promise((resolve, reject) => {
    chrome.runtime.sendMessage({ action: 'fetchPrices' }, (response) => {
      if (chrome.runtime.lastError) {
        console.error('❌ [DEBUG] Chrome runtime error for prices:', chrome.runtime.lastError);
        resolve(null);
        return;
      }

      if (response && response.success && response.data) {
        console.log('✅ [DEBUG] Got live prices!');
        resolve(response.data);
      } else {
        console.error('❌ [DEBUG] Failed to get prices:', response?.error);
        resolve(null);
      }
    });
  });
}

async function executeTrade(side, amount, marketId = null) {
  console.log(`🔍 [DEBUG] Executing trade: ${side} $${amount} ${marketId ? `for market ${marketId}` : ''} via Chrome messaging...`);

  return new Promise((resolve, reject) => {
    const message = {
      action: 'executeTrade',
      side: side,
      amount: amount
    };

    if (marketId) {
      message.market_id = marketId;
    }

    chrome.runtime.sendMessage(message, (response) => {
      if (chrome.runtime.lastError) {
        console.error('❌ [DEBUG] Chrome runtime error for trade:', chrome.runtime.lastError);
        resolve({ success: false, error: 'Chrome messaging failed' });
        return;
      }

      console.log('🔍 [DEBUG] Trade response:', response);

      if (response && response.success) {
        console.log('✅ [DEBUG] Trade executed successfully!');
        resolve(response.data || { success: true });
      } else {
        console.error('❌ [DEBUG] Trade failed:', response?.error);
        resolve({ success: false, error: response?.error || 'Unknown error' });
      }
    });
  });
}

async function fetchPositions() {
  console.log('🔍 [DEBUG] Fetching positions via Chrome messaging...');

  return new Promise((resolve, reject) => {
    chrome.runtime.sendMessage({ action: 'fetchPositions' }, (response) => {
      if (chrome.runtime.lastError) {
        console.error('❌ [DEBUG] Chrome runtime error for positions:', chrome.runtime.lastError);
        resolve(null);
        return;
      }

      if (response && response.success && response.data) {
        console.log('✅ [DEBUG] Got positions!');
        resolve(response.data);
      } else {
        console.error('❌ [DEBUG] Failed to get positions:', response?.error);
        resolve(null);
      }
    });
  });
}

async function fetchClosedPositions() {
  console.log('🔍 [DEBUG] Fetching closed positions via Chrome messaging...');

  return new Promise((resolve, reject) => {
    chrome.runtime.sendMessage({ action: 'fetchClosedPositions' }, (response) => {
      if (chrome.runtime.lastError) {
        console.error('❌ [DEBUG] Chrome runtime error for closed positions:', chrome.runtime.lastError);
        resolve(null);
        return;
      }

      if (response && response.success && response.data) {
        console.log('✅ [DEBUG] Got closed positions!');
        resolve(response.data);
      } else {
        console.error('❌ [DEBUG] Failed to get closed positions:', response?.error);
        resolve(null);
      }
    });
  });
}

// Function to setup market notes popup handlers
function setupMarketNotesHandlers() {
  if (!marketNotesPopup) return;

  const closeBtn = marketNotesPopup.querySelector('.close-popup');
  const allMarketsBtn = marketNotesPopup.querySelector('.all-markets-btn');
  const refreshPricesBtn = marketNotesPopup.querySelector('.refresh-prices-btn');
  const tradingPanel = marketNotesPopup.querySelector('.trading-panel');
  const executeTradeBtnEl = marketNotesPopup.querySelector('.execute-trade-btn');

  // Check if this is a multi-market popup
  const isMultiMarket = marketNotesPopup.querySelector('.multi-markets-container');

  if (isMultiMarket) {
    setupMultiMarketHandlers();
  } else {
    setupSingleMarketHandlers();
  }

  // Common handlers

  // Close handler
  if (closeBtn) {
    closeBtn.addEventListener('click', () => {
      marketNotesPopup.remove();
      marketNotesPopup = null;
    });
  }

  // Switch market type handler
  const switchMarketBtn = marketNotesPopup.querySelector('.switch-market-btn');
  if (switchMarketBtn) {
    switchMarketBtn.addEventListener('click', async () => {
      console.log('🔄 [DEBUG] Switching market type...');

      // Show loading state
      switchMarketBtn.disabled = true;
      switchMarketBtn.innerHTML = '⏳';

      // Switch to the other market type
      await switchMarketType();

      // Reset button
      switchMarketBtn.disabled = false;
      switchMarketBtn.innerHTML = '➡️';
    });
  }
}

// Function to setup single market handlers
function setupSingleMarketHandlers() {
  const allMarketsBtn = marketNotesPopup.querySelector('.all-markets-btn');
  const refreshPricesBtn = marketNotesPopup.querySelector('.refresh-prices-btn');

  // All Markets handler
  if (allMarketsBtn) {
    allMarketsBtn.addEventListener('click', () => {
      alert('📊 Market information loaded from data files.\n\nShowing current market data with real-time trading capabilities.');
    });
  }

  // Refresh prices handler
  if (refreshPricesBtn) {
    refreshPricesBtn.addEventListener('click', async () => {
      refreshPricesBtn.disabled = true;
      refreshPricesBtn.innerHTML = '⏳';

      const prices = await fetchLivePrices();
      if (prices) {
        if (prices.type === 'single') {
          // Update single market prices
          updateSingleMarketPrices(prices);
        } else if (prices.type === 'multi') {
          // Update multi-market prices
          updateMultiMarketPrices(prices);
        }
      }

      refreshPricesBtn.disabled = false;
      refreshPricesBtn.innerHTML = '🔄';
    });
  }

  // Setup trading handlers for single market (YES/NO buttons, payout calculation, etc.)
  setupTradingHandlers();
}

function updateSingleMarketPrices(prices) {
  const yesBtn = marketNotesPopup.querySelector('.yes-side-btn');
  const noBtn = marketNotesPopup.querySelector('.no-side-btn');

  if (yesBtn && noBtn) {
    yesBtn.textContent = `YES ${formatCentPrice(prices.yes_price)}`;
    noBtn.textContent = `NO ${formatCentPrice(prices.no_price)}`;
    updateWinningsCalculation();
  }
}

function updateMultiMarketPrices(prices) {
  prices.prices.forEach(marketPrice => {
    const marketItem = marketNotesPopup.querySelector(`[data-market-id="${marketPrice.market_id}"]`);
    if (marketItem) {
      // Update the probability percentage in the collapsed view
      const probabilityEl = marketItem.querySelector('.probability-percentage');
      if (probabilityEl) {
        const rawPercentage = marketPrice.yes_price * 100;
        const oddsPercentage = rawPercentage < 1 && rawPercentage > 0 ? '<1' : Math.round(rawPercentage);
        probabilityEl.textContent = `${oddsPercentage}%`;
      }

      // Update the trading buttons if they exist (when market is expanded)
      const yesBtn = marketItem.querySelector('.yes-side-btn');
      const noBtn = marketItem.querySelector('.no-side-btn');
      if (yesBtn) yesBtn.textContent = `YES ${formatCentPrice(marketPrice.yes_price)}`;
      if (noBtn) noBtn.textContent = `NO ${formatCentPrice(marketPrice.no_price)}`;
    }
  });
  updateWinningsCalculation();
}

// Function to setup multi-market handlers
function setupMultiMarketHandlers() {
  // Market item click handlers
  const marketItems = marketNotesPopup.querySelectorAll('.multi-market-item');

  marketItems.forEach(item => {
    const header = item.querySelector('.market-candidate-header');
    header.addEventListener('click', () => {
      const isCurrentlyActive = item.classList.contains('active');

      // Remove active class from all items
      marketItems.forEach(otherItem => otherItem.classList.remove('active'));

      // If this item wasn't active, make it active and show trading interface
      if (!isCurrentlyActive) {
        item.classList.add('active');
        showTradingInterface(item);
      }
      // If it was active, clicking again closes it (no active market)
    });
  });

  // No default trading handlers setup since no market is active initially
}

// Function to show trading interface for selected market
function showTradingInterface(marketItem) {
  // Remove existing trading interfaces
  const existingForms = marketNotesPopup.querySelectorAll('.trade-form');
  existingForms.forEach(form => form.remove());

  const existingStatus = marketNotesPopup.querySelectorAll('.trade-status');
  existingStatus.forEach(status => status.remove());

  const marketId = marketItem.dataset.marketId;

  // Get the percentage value to calculate the prices
  const percentageEl = marketItem.querySelector('.probability-percentage');
  const percentage = percentageEl ? parseInt(percentageEl.textContent) : 50;
  const yesPrice = percentage / 100; // Convert percentage to decimal
  const noPrice = (100 - percentage) / 100; // Calculate NO price as decimal

  // Add trading interface to the active market
  const tradingHTML = `
    <div class="trade-form">
      <div class="side-selector">
        <button class="side-btn yes-side-btn active" data-side="YES" data-market-id="${marketId}">YES ${formatCentPrice(yesPrice)}</button>
        <button class="side-btn no-side-btn" data-side="NO" data-market-id="${marketId}">NO ${formatCentPrice(noPrice)}</button>
      </div>
      <div class="amount-input-group">
        <label>Amount (USD):</label>
        <input type="text" class="amount-input" placeholder="$0" inputmode="decimal">
        <div class="potential-winnings">
          <span class="winnings-text">Potential payout: <span class="winnings-amount">$0.00</span></span>
          <span class="profit-text">Profit: <span class="profit-amount">$0.00</span></span>
        </div>
      </div>
      <div class="trade-buttons">
        <button class="execute-trade-btn" data-market-id="${marketId}">Execute Trade</button>
      </div>
    </div>
    <div class="trade-status"></div>
  `;

  marketItem.insertAdjacentHTML('beforeend', tradingHTML);

  // Setup handlers for the new trading interface
  setupTradingHandlers();
}

// Function to setup trading handlers (works for both single and multi-market)
function setupTradingHandlers() {
  // Remove existing handlers to avoid duplicates
  const existingHandlers = marketNotesPopup.querySelectorAll('[data-handler-added]');
  existingHandlers.forEach(element => {
    element.removeAttribute('data-handler-added');
  });

  // Side selector button handlers - FIXED version
  const sideBtns = marketNotesPopup.querySelectorAll('.side-btn:not([data-handler-added])');
  console.log('🔍 [DEBUG] Found side buttons:', sideBtns.length);

  sideBtns.forEach((btn, index) => {
    btn.setAttribute('data-handler-added', 'true');
    console.log(`🔍 [DEBUG] Setting up button ${index}:`, btn.dataset.side, btn.className);

    btn.addEventListener('click', (e) => {
      e.preventDefault();
      e.stopPropagation();

      console.log('🔍 [DEBUG] Button clicked:', btn.dataset.side);

      // For multi-market, only affect buttons in the same market
      const marketId = btn.dataset.marketId;
      let buttonsToUpdate;

      if (marketId) {
        // Multi-market: only update buttons in the same market
        buttonsToUpdate = marketNotesPopup.querySelectorAll(`.side-btn[data-market-id="${marketId}"]`);
      } else {
        // Single market: update all side buttons
        buttonsToUpdate = marketNotesPopup.querySelectorAll('.side-btn');
      }

      buttonsToUpdate.forEach((b, i) => {
        console.log(`🔍 [DEBUG] Before: button ${i} classes:`, b.className);
        b.classList.remove('active');
        console.log(`🔍 [DEBUG] After: button ${i} classes:`, b.className);
      });

      // Add active to clicked button
      btn.classList.add('active');
      console.log('🔍 [DEBUG] Final: clicked button classes:', btn.className);

      // Clear trade status (find the right one for multi-market)
      let tradeStatus;
      if (marketId) {
        const marketItem = marketNotesPopup.querySelector(`[data-market-id="${marketId}"]`);
        tradeStatus = marketItem ? marketItem.querySelector('.trade-status') : null;
      } else {
        tradeStatus = marketNotesPopup.querySelector('.trade-status');
      }
      if (tradeStatus) tradeStatus.innerHTML = '';

      // Recalculate winnings
      updateWinningsCalculation();
    });
  });

  // Dollar sign formatting functions
  function formatDollarInput(value) {
    // Remove all non-digit and non-decimal characters
    let cleanValue = value.replace(/[^\d.]/g, '');

    // Handle multiple decimal points - keep only the first one
    const parts = cleanValue.split('.');
    if (parts.length > 2) {
      cleanValue = parts[0] + '.' + parts.slice(1).join('');
    }

    // Limit to 2 decimal places
    if (cleanValue.includes('.')) {
      const [whole, decimal] = cleanValue.split('.');
      cleanValue = whole + '.' + decimal.substring(0, 2);
    }

    // Add dollar sign if there's a value
    return cleanValue ? '$' + cleanValue : '';
  }

  function extractNumericValue(dollarString) {
    // Remove dollar sign and parse as float
    return parseFloat(dollarString.replace('$', '')) || 0;
  }

  // Amount input handler - real-time updates with dollar formatting
  const amountInputs = marketNotesPopup.querySelectorAll('.amount-input:not([data-handler-added])');
  amountInputs.forEach(amountInput => {
    amountInput.setAttribute('data-handler-added', 'true');
    console.log('🔍 [DEBUG] Setting up real-time input handlers with dollar formatting');

    // Set initial value if empty
    if (!amountInput.value) {
      amountInput.value = '';
    }

    amountInput.addEventListener('input', (e) => {
      const cursorPosition = e.target.selectionStart;
      const oldValue = e.target.value;
      const formatted = formatDollarInput(oldValue);

      console.log('🔍 [DEBUG] Input formatting:', oldValue, '->', formatted);

      if (formatted !== oldValue) {
        e.target.value = formatted;
        // Maintain cursor position, accounting for added/removed characters
        const newPosition = Math.min(cursorPosition + (formatted.length - oldValue.length), formatted.length);
        e.target.setSelectionRange(newPosition, newPosition);
      }

      updateWinningsCalculation();
    });

    amountInput.addEventListener('keydown', (e) => {
      // Allow: backspace, delete, tab, escape, enter
      if ([8, 9, 27, 13, 46].indexOf(e.keyCode) !== -1 ||
          // Allow: Ctrl+A, Ctrl+C, Ctrl+V, Ctrl+X
          (e.keyCode === 65 && e.ctrlKey === true) ||
          (e.keyCode === 67 && e.ctrlKey === true) ||
          (e.keyCode === 86 && e.ctrlKey === true) ||
          (e.keyCode === 88 && e.ctrlKey === true) ||
          // Allow: home, end, left, right
          (e.keyCode >= 35 && e.keyCode <= 39)) {
        return;
      }
      // Ensure that it is a number or decimal point and stop the keypress
      if ((e.shiftKey || (e.keyCode < 48 || e.keyCode > 57)) &&
          (e.keyCode < 96 || e.keyCode > 105) &&
          e.keyCode !== 190 && e.keyCode !== 110) {
        e.preventDefault();
      }
    });

    amountInput.addEventListener('focus', () => {
      // If placeholder is showing, clear it and add $
      if (amountInput.value === '' || amountInput.value === '$0') {
        amountInput.value = '$';
        // Position cursor after $
        setTimeout(() => {
          amountInput.setSelectionRange(1, 1);
        }, 0);
      }
    });

    amountInput.addEventListener('blur', () => {
      // If only $ is left, clear the field
      if (amountInput.value === '$') {
        amountInput.value = '';
      }
      updateWinningsCalculation();
    });

    amountInput.addEventListener('paste', (e) => {
      // Handle paste events
      e.preventDefault();
      const paste = (e.clipboardData || window.clipboardData).getData('text');
      const formatted = formatDollarInput(paste);
      amountInput.value = formatted;
      updateWinningsCalculation();
    });
  });

  // Enhanced winnings calculation function
  function updateWinningsCalculation() {
    // Find the active market (for multi-market support)
    const activeMarketItem = marketNotesPopup.querySelector('.multi-market-item.active');
    let activeSideBtn, amountInput, winningsAmount, profitAmount;

    if (activeMarketItem) {
      // Multi-market: get elements from active market
      activeSideBtn = activeMarketItem.querySelector('.side-btn.active');
      amountInput = activeMarketItem.querySelector('.amount-input');
      winningsAmount = activeMarketItem.querySelector('.winnings-amount');
      profitAmount = activeMarketItem.querySelector('.profit-amount');
    } else {
      // Single market: get elements globally
      activeSideBtn = marketNotesPopup.querySelector('.side-btn.active');
      amountInput = marketNotesPopup.querySelector('.amount-input');
      winningsAmount = marketNotesPopup.querySelector('.winnings-amount');
      profitAmount = marketNotesPopup.querySelector('.profit-amount');
    }

    // If no active elements found (no market selected), don't calculate
    if (!activeSideBtn || !amountInput || !winningsAmount || !profitAmount) {
      console.log('🔍 [DEBUG] No active market selected or elements missing for calculation');
      return;
    }

    console.log('🔍 [DEBUG] === Starting winnings calculation ===');
    console.log('🔍 [DEBUG] Active side btn:', activeSideBtn?.dataset.side, activeSideBtn?.className);
    console.log('🔍 [DEBUG] Amount input value:', amountInput?.value);
    console.log('🔍 [DEBUG] Winnings/profit elements found:', !!winningsAmount, !!profitAmount);

    if (!activeSideBtn || !amountInput || !winningsAmount || !profitAmount) {
      console.log('❌ [DEBUG] Missing required elements for calculation');
      console.log('❌ [DEBUG] activeSideBtn:', !!activeSideBtn);
      console.log('❌ [DEBUG] amountInput:', !!amountInput);
      console.log('❌ [DEBUG] winningsAmount:', !!winningsAmount);
      console.log('❌ [DEBUG] profitAmount:', !!profitAmount);
      return;
    }

    const side = activeSideBtn.dataset.side;
    const inputValue = amountInput.value.trim();
    const amount = extractNumericValue(inputValue);

    console.log('🔍 [DEBUG] Side:', side, 'Raw input:', inputValue, 'Parsed amount:', amount);

    if (amount <= 0) {
      winningsAmount.textContent = '$0.00';
      profitAmount.textContent = '$0.00';
      profitAmount.style.color = 'rgb(139, 152, 165)';
      console.log('🔍 [DEBUG] Amount is 0 or invalid, showing $0.00');
      return;
    }

    // Get current prices from side buttons
    let yesPrice = 0.0665, noPrice = 0.9335; // fallback prices

    const yesBtn = marketNotesPopup.querySelector('.yes-side-btn');
    const noBtn = marketNotesPopup.querySelector('.no-side-btn');

    if (yesBtn && noBtn) {
      const yesText = yesBtn.textContent.match(/(\d+)¢/);
      const noText = noBtn.textContent.match(/(\d+)¢/);

      if (yesText && noText) {
        yesPrice = parseFloat(yesText[1]) / 100;
        noPrice = parseFloat(noText[1]) / 100;
        console.log('🔍 [DEBUG] Extracted prices from buttons - YES:', yesPrice, 'NO:', noPrice);
      } else {
        console.log('🔍 [DEBUG] Could not parse prices from button text, using fallbacks');
      }
    } else {
      console.log('🔍 [DEBUG] Side buttons not found, using fallback prices');
    }

    // Validate and ensure price is safe for calculation
    let price = side === 'YES' ? yesPrice : noPrice;
    price = validatePrice(price); // Ensure price is between 1¢ and 99¢
    console.log(`🔍 [DEBUG] Using validated ${side} price: ${price}`);

    // Calculate shares you'd get for your USD amount
    const shares = amount / price;

    // If you win, each share is worth $1, so total payout is number of shares
    const rawTotalPayout = shares;
    const rawProfit = rawTotalPayout - amount;

    // Validate payouts to prevent Infinity/NaN
    const totalPayout = validatePayout(rawTotalPayout);
    const profit = validatePayout(rawProfit) || (rawProfit < 0 ? rawProfit : 0); // Allow negative profit

    console.log(`🔍 [DEBUG] Final calculation: Shares=${shares.toFixed(4)}, Payout=$${totalPayout.toFixed(2)}, Profit=$${profit.toFixed(2)}`);

    // Update display
    winningsAmount.textContent = `$${totalPayout.toFixed(2)}`;
    profitAmount.textContent = `$${profit.toFixed(2)}`;

    // Update profit color based on positive/negative
    if (profit >= 0) {
      profitAmount.style.color = 'rgb(0, 186, 124)'; // green for profit
    } else {
      profitAmount.style.color = 'rgb(249, 24, 128)'; // red for loss
    }

    console.log('🔍 [DEBUG] === Calculation complete ===\n');
  }

  // Execute trade handlers
  const executeTradeBtns = marketNotesPopup.querySelectorAll('.execute-trade-btn:not([data-handler-added])');
  executeTradeBtns.forEach(executeTradeBtnEl => {
    executeTradeBtnEl.setAttribute('data-handler-added', 'true');

    executeTradeBtnEl.addEventListener('click', async () => {
      const marketId = executeTradeBtnEl.dataset.marketId;

      // Find the right elements based on whether this is single or multi-market
      let activeSideBtn, amountInput, statusEl, profitAmountEl;

      if (marketId) {
        // Multi-market: find elements within the specific market
        const marketItem = marketNotesPopup.querySelector(`[data-market-id="${marketId}"]`);
        if (!marketItem) return;

        activeSideBtn = marketItem.querySelector('.side-btn.active');
        amountInput = marketItem.querySelector('.amount-input');
        statusEl = marketItem.querySelector('.trade-status');
        profitAmountEl = marketItem.querySelector('.profit-amount');
      } else {
        // Single market: find elements globally
        activeSideBtn = marketNotesPopup.querySelector('.side-btn.active');
        amountInput = marketNotesPopup.querySelector('.amount-input');
        statusEl = marketNotesPopup.querySelector('.trade-status');
        profitAmountEl = marketNotesPopup.querySelector('.profit-amount');
      }

      if (!activeSideBtn) {
        statusEl.innerHTML = '<div class="error">Please select YES or NO</div>';
        return;
      }

      const side = activeSideBtn.dataset.side;
      const amount = extractNumericValue(amountInput.value);

      if (!amount || amount <= 0) {
        statusEl.innerHTML = '<div class="error">Please enter a valid amount</div>';
        return;
      }

      executeTradeBtnEl.disabled = true;
      executeTradeBtnEl.textContent = 'Executing...';
      statusEl.innerHTML = '<div class="loading">Placing order...</div>';

      const result = await executeTrade(side, amount, marketId);

      if (result.success) {
        const profitAmount = profitAmountEl ? profitAmountEl.textContent : '$0.00';
        const candidate = marketId ? ` for ${activeSideBtn.closest('[data-market-id]').querySelector('h5').textContent}` : '';
        statusEl.innerHTML = `<div class="success">✅ Trade executed! Bought ${side}${candidate} for $${amount}<br/>Potential profit: ${profitAmount}</div>`;

        // Clear the form after successful trade
        amountInput.value = '';
        updateWinningsCalculation();
      } else {
        statusEl.innerHTML = `<div class="error">❌ Trade failed: ${result.error}</div>`;
      }

      executeTradeBtnEl.disabled = false;
      executeTradeBtnEl.textContent = 'Execute Trade';
    });
  });
}

// All fake market functions removed - only using real samplein.json data

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
    actualButton.addEventListener('click', async (e) => {
      console.log('🎯 [DEBUG] Polymarket button clicked!');
      e.preventDefault();
      e.stopPropagation();

      // Close existing popup if open
      if (marketNotesPopup) {
        console.log('🔍 [DEBUG] Closing existing popup');
        marketNotesPopup.remove();
        marketNotesPopup = null;
      }

      // Show loading state
      console.log('🔍 [DEBUG] Setting loading state');
      actualButton.innerHTML = '<div style="color: rgb(139, 152, 165);">⏳</div>';
      actualButton.disabled = true;

      // First, always try to fetch carousel data to see how many events we have
      console.log('🔍 [DEBUG] Checking for available events...');
      let carouselData = await fetchMarketDataWithType('carousel');
      let marketData;

      if (carouselData && carouselData.events && carouselData.events.length > 1) {
        // We have multiple events, use carousel mode from start
        console.log('🎠 [DEBUG] Found multiple events, starting in carousel mode');
        currentMarketType = 'carousel';
        marketData = carouselData;
      } else {
        // Single event, fetch based on current market type
        console.log('🔍 [DEBUG] Single event available, fetching normal market data...');
        marketData = await fetchMarketData();
      }

      if (!marketData) {
        console.error('❌ [DEBUG] No market data received - showing error');
        // Show detailed error
        alert('❌ Trading backend not available.\n\nDebugging info:\n- Check Chrome DevTools console for detailed errors\n- Ensure backend is running: ./start_trading.sh\n- Backend should be at http://127.0.0.1:5000');
        actualButton.innerHTML = `<img src="${chrome.runtime.getURL('icons/pmarket.png')}" alt="Polymarket" width="20" height="20" style="border-radius: 2px; opacity: 0.8;" />`;
        actualButton.disabled = false;
        return;
      }

      console.log('✅ [DEBUG] Got market data, creating popup...');
      console.log('🔍 [DEBUG] Market data:', marketData);

      // Create and show popup with real market data
      marketNotesPopup = createMarketNotesPopup(marketData, 'tweet');
      document.body.appendChild(marketNotesPopup);

      // Position popup
      const buttonRect = actualButton.getBoundingClientRect();
      positionPopup(marketNotesPopup, buttonRect);

      // Add event handlers
      setupMarketNotesHandlers();

      // Reset button
      actualButton.innerHTML = `<img src="${chrome.runtime.getURL('icons/pmarket.png')}" alt="Polymarket" width="20" height="20" style="border-radius: 2px; opacity: 0.8;" />`;
      actualButton.disabled = false;

      console.log('✅ [DEBUG] Popup created and displayed successfully!');
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
}, 500);

// Set up mutation observer to handle dynamic content
const observer = new MutationObserver((mutations) => {
  let shouldInjectButtons = false;
  let shouldInjectPositions = false;

  mutations.forEach((mutation) => {
    mutation.addedNodes.forEach((node) => {
      if (node.nodeType === Node.ELEMENT_NODE) {
        // Check if new tweets were added (for buttons only)
        if (node.matches && (node.matches('[data-testid="tweet"]') || node.querySelector('[data-testid="tweet"]'))) {
          shouldInjectButtons = true;
        }
        
        // Check if tablist was added (for positions - only once per page)
        if (node.matches && (node.matches('[role="tablist"]') || node.querySelector('[role="tablist"]'))) {
          // Only inject if we don't already have a positions section
          if (!document.querySelector('.polymarket-positions-section')) {
            shouldInjectPositions = true;
          }
        }
      }
    });
  });

  // Inject buttons when tweets are found
  if (shouldInjectButtons) {
    setTimeout(() => {
      injectPolymarketButtons();
    }, 100);
  }
  
  // Inject positions only once when tablist is found
  if (shouldInjectPositions) {
    setTimeout(() => {
      injectPositionsSection();
    }, 300);
  }
});

// Start observing
observer.observe(document.body, {
  childList: true,
  subtree: true
});


console.log('🚀 Polymarket Notes extension loaded with debugging');

// Test function to check backend connectivity
async function testBackendConnection() {
  console.log('🧪 [TEST] Testing backend connection...');
  const result = await fetchMarketData();
  if (result) {
    console.log('✅ [TEST] Backend is working! Market:', result.question);
  } else {
    console.error('❌ [TEST] Backend connection failed');
  }
}

// Test backend connection on load
setTimeout(() => {
  console.log('🔍 [DEBUG] Running automatic backend test in 3 seconds...');
  testBackendConnection();
}, 3000);