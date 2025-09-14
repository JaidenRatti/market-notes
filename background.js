// Background script to handle API calls (bypasses CORS/blocking issues)

chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  console.log('🔍 [BACKGROUND] Received message:', request);

  if (request.action === 'fetchMarketData') {
    fetchMarketDataBackground(request.marketType)
      .then(data => {
        console.log('✅ [BACKGROUND] Got market data:', data);
        sendResponse({ success: true, data });
      })
      .catch(error => {
        console.error('❌ [BACKGROUND] Error:', error);
        sendResponse({ success: false, error: error.message });
      });
    return true; // Keep message channel open for async response
  }

  if (request.action === 'fetchPrices') {
    fetchPricesBackground()
      .then(data => {
        console.log('✅ [BACKGROUND] Got prices:', data);
        sendResponse({ success: true, data });
      })
      .catch(error => {
        console.error('❌ [BACKGROUND] Error fetching prices:', error);
        sendResponse({ success: false, error: error.message });
      });
    return true;
  }

  if (request.action === 'executeTrade') {
    executeTradeBackground(request.side, request.amount, request.market_id)
      .then(data => {
        console.log('✅ [BACKGROUND] Trade executed:', data);
        sendResponse({ success: true, data });
      })
      .catch(error => {
        console.error('❌ [BACKGROUND] Trade error:', error);
        sendResponse({ success: false, error: error.message });
      });
    return true;
  }

  if (request.action === 'fetchPositions') {
    fetchPositionsBackground()
      .then(data => {
        console.log('✅ [BACKGROUND] Got positions:', data);
        sendResponse({ success: true, data });
      })
      .catch(error => {
        console.error('❌ [BACKGROUND] Positions error:', error);
        sendResponse({ success: false, error: error.message });
      });
    return true;
  }

  if (request.action === 'fetchClosedPositions') {
    fetchClosedPositionsBackground()
      .then(data => {
        console.log('✅ [BACKGROUND] Got closed positions:', data);
        sendResponse({ success: true, data });
      })
      .catch(error => {
        console.error('❌ [BACKGROUND] Closed positions error:', error);
        sendResponse({ success: false, error: error.message });
      });
    return true;
  }
});

async function fetchMarketDataBackground(marketType = 'single') {
  // Choose endpoint based on market type
  let endpoint = '/api/market';
  if (marketType === 'carousel') {
    endpoint = '/api/events'; // Use events endpoint for carousel
  }

  const urls = [`http://127.0.0.1:5000${endpoint}`, `http://localhost:5000${endpoint}`];

  for (const url of urls) {
    try {
      console.log(`🔍 [BACKGROUND] Trying ${url} with marketType: ${marketType}`);

      let queryParams = '';
      if (marketType && marketType !== 'single') {
        queryParams = `?marketType=${marketType}`;
      }

      const response = await fetch(url + queryParams, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        }
      });

      console.log(`🔍 [BACKGROUND] Response status: ${response.status} for ${url}`);
      console.log(`🔍 [BACKGROUND] Response ok: ${response.ok}`);

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      console.log(`🔍 [BACKGROUND] Got data:`, data);

      // Handle carousel data format
      if (marketType === 'carousel' && data.success && data.events) {
        console.log(`✅ [BACKGROUND] Success! Returning carousel data with ${data.events.length} events`);
        return data;
      }
      // Handle single/multi market data format
      else if (data.success && data.market) {
        console.log(`✅ [BACKGROUND] Success! Returning market data`);
        return data.market;
      } else {
        console.log(`❌ [BACKGROUND] Data format wrong:`, data);
      }
    } catch (error) {
      console.error(`❌ [BACKGROUND] Failed ${url}:`, error.message);
      console.error(`❌ [BACKGROUND] Full error:`, error);
    }
  }

  console.error('❌ [BACKGROUND] All URLs failed');
  throw new Error('All backend URLs failed');
}

async function fetchPricesBackground() {
  const urls = ['http://127.0.0.1:5000/api/prices', 'http://localhost:5000/api/prices'];

  for (const url of urls) {
    try {
      const response = await fetch(url);
      if (response.ok) {
        const data = await response.json();
        if (data.success) {
          return { yes_price: data.yes_price, no_price: data.no_price };
        } else if (data.fallback_prices) {
          return data.fallback_prices;
        }
      }
    } catch (error) {
      console.error(`❌ [BACKGROUND] Price fetch failed ${url}:`, error);
    }
  }

  throw new Error('Failed to fetch prices');
}

async function executeTradeBackground(side, amount, marketId = null) {
  const urls = ['http://127.0.0.1:5000/api/trade', 'http://localhost:5000/api/trade'];

  for (const url of urls) {
    try {
      const payload = { side, amount };
      if (marketId) {
        payload.market_id = marketId;
      }

      const response = await fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      if (response.ok) {
        return await response.json();
      }
    } catch (error) {
      console.error(`❌ [BACKGROUND] Trade failed ${url}:`, error);
    }
  }

  throw new Error('Failed to execute trade');
}

async function fetchPositionsBackground() {
  const urls = ['http://127.0.0.1:5000/api/positions', 'http://localhost:5000/api/positions'];

  for (const url of urls) {
    try {
      console.log(`🔍 [BACKGROUND] Fetching positions from ${url}`);
      const response = await fetch(url, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        }
      });

      console.log(`🔍 [BACKGROUND] Positions response status: ${response.status}`);

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      console.log(`🔍 [BACKGROUND] Got positions data:`, data);

      if (data.success && data.positions) {
        console.log(`✅ [BACKGROUND] Success! Returning ${data.positions.length} positions`);
        return data.positions;
      } else {
        console.log(`❌ [BACKGROUND] Positions data format wrong:`, data);
      }
    } catch (error) {
      console.error(`❌ [BACKGROUND] Failed ${url}:`, error.message);
      console.error(`❌ [BACKGROUND] Full error:`, error);
    }
  }

  console.error('❌ [BACKGROUND] All positions URLs failed');
  throw new Error('All backend URLs failed');
}

async function fetchClosedPositionsBackground() {
  const urls = ['http://127.0.0.1:5000/api/closed-positions', 'http://localhost:5000/api/closed-positions'];

  for (const url of urls) {
    try {
      console.log(`🔍 [BACKGROUND] Fetching closed positions from ${url}`);
      const response = await fetch(url, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        }
      });

      console.log(`🔍 [BACKGROUND] Closed positions response status: ${response.status}`);

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      console.log(`🔍 [BACKGROUND] Got closed positions data:`, data);

      if (data.success && data.positions) {
        console.log(`✅ [BACKGROUND] Success! Returning ${data.positions.length} closed positions`);
        return data.positions;
      } else {
        console.log(`❌ [BACKGROUND] Closed positions data format wrong:`, data);
      }
    } catch (error) {
      console.error(`❌ [BACKGROUND] Failed ${url}:`, error.message);
      console.error(`❌ [BACKGROUND] Full error:`, error);
    }
  }

  console.error('❌ [BACKGROUND] All closed positions URLs failed');
  throw new Error('All backend URLs failed');
}
