#!/usr/bin/env python3

import json
import os
import sys
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from py_clob_client.client import ClobClient
from py_clob_client.clob_types import MarketOrderArgs, OrderType
from py_clob_client.order_builder.constants import BUY, SELL

# Add tweet-market-pipeline to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'tweet-market-pipeline'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'tweet-market-pipeline', 'include'))

load_dotenv()

# Import tweet analyzer (add error handling for missing dependencies)
try:
    from tweet_analyzer import analyze_tweet
    TWEET_ANALYSIS_AVAILABLE = True
    print("✅ Tweet analysis pipeline loaded successfully")
except ImportError as e:
    print(f"⚠️ Tweet analysis pipeline not available: {e}")
    TWEET_ANALYSIS_AVAILABLE = False

app = Flask(__name__)
CORS(app, resources={
    r"/api/*": {
        "origins": ["chrome-extension://*", "http://localhost:*", "https://x.com", "https://twitter.com"],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

HOST = "https://clob.polymarket.com"
CHAIN_ID = 137
PRIVATE_KEY = os.getenv("magickey")
FUNDER_ADDRESS = os.getenv("funder")

def setup_client():
    """Setup authenticated Magic wallet client"""
    client = ClobClient(
        HOST,
        key=PRIVATE_KEY,
        chain_id=CHAIN_ID,
        signature_type=1,  # Magic wallet
        funder=FUNDER_ADDRESS
    )
    client.set_api_creds(client.create_or_derive_api_creds())
    return client

def load_single_market_data():
    """Load single market data from samplein.json"""
    try:
        with open('data/samplein.json', 'r') as f:
            data = json.load(f)

        market = data['events'][0]['markets'][0]
        token_ids = json.loads(market['clobTokenIds'])
        prices = json.loads(market['outcomePrices'])

        return {
            'question': market['question'],
            'yes_token_id': token_ids[0],
            'no_token_id': token_ids[1],
            'yes_price': float(prices[0]),
            'no_price': float(prices[1]),
            'volume': f"${float(market['volume']):,.0f}",
            'description': market['description'],
            'title': market['question'],  # For compatibility with frontend
            'type': 'single'
        }
    except Exception as e:
        print(f"Error loading samplein.json: {e}")
        return None

def load_multi_market_data():
    """Load multi-market data from samplemultimarkets.json"""
    try:
        with open('data/samplemultimarkets.json', 'r') as f:
            data = json.load(f)

        event = data['events'][0]
        markets = []

        for market in event['markets']:
            # Skip inactive markets
            if not market.get('active', True):
                continue

            token_ids = json.loads(market['clobTokenIds'])
            prices = json.loads(market['outcomePrices'])

            # Format volume nicely
            volume_num = float(market.get('volume', 0))
            if volume_num >= 1000000:
                volume_display = f"${volume_num/1000000:.1f}M"
            elif volume_num >= 1000:
                volume_display = f"${volume_num/1000:.0f}K"
            else:
                volume_display = f"${volume_num:,.0f}"

            markets.append({
                'id': market['id'],
                'question': market['question'],
                'candidate': market.get('groupItemTitle', 'Unknown'),
                'yes_token_id': token_ids[0],
                'no_token_id': token_ids[1],
                'yes_price': float(prices[0]),
                'no_price': float(prices[1]),
                'volume': volume_display,
                'volume_raw': float(market.get('volume', 0)),
                'image': market.get('image', ''),
                'icon': market.get('icon', ''),
                'description': market['description']
            })

        # Sort markets by YES percentage (highest probability first)
        markets.sort(key=lambda x: x['yes_price'], reverse=True)

        # Format total volume nicely
        total_volume = float(event.get('volume', 0))
        if total_volume >= 1000000:
            volume_display = f"${total_volume/1000000:.1f}M"
        elif total_volume >= 1000:
            volume_display = f"${total_volume/1000:.0f}K"
        else:
            volume_display = f"${total_volume:,.0f}"

        return {
            'title': event['title'],
            'description': event['description'],
            'volume': volume_display,
            'markets': markets,
            'type': 'multi',
            'event_id': event['id']
        }
    except Exception as e:
        print(f"Error loading samplemultimarkets.json: {e}")
        return None

def load_market_data():
    """Load market data - try multi-market first, then single market"""
    # Try multi-market first
    multi_data = load_multi_market_data()
    if multi_data:
        return multi_data

    # Fall back to single market
    return load_single_market_data()

def load_all_events():
    """Load all available events for carousel display"""
    events = []

    # Load multi-market event
    multi_data = load_multi_market_data()
    if multi_data:
        events.append(multi_data)

    # Load single market event
    single_data = load_single_market_data()
    if single_data:
        events.append(single_data)

    # For testing, duplicate the events to simulate multiple events
    if len(events) > 0:
        # Create variations for testing carousel
        test_events = []
        for i, event in enumerate(events):
            for j in range(3):  # Create 3 copies of each event type
                test_event = event.copy()
                if test_event['type'] == 'multi':
                    test_event['title'] = f"{test_event['title']} (Event {i*3 + j + 1})"
                    test_event['event_id'] = f"{test_event['event_id']}_{j}"
                else:
                    test_event['title'] = f"{test_event['title']} (Event {i*3 + j + 1})"
                    test_event['question'] = f"{test_event['question']} (Event {i*3 + j + 1})"
                test_events.append(test_event)
        events = test_events

    return {
        'events': events,
        'total_count': len(events),
        'carousel': True
    }

def convert_pipeline_to_events(pipeline_result):
    """Convert tweet pipeline result to event format compatible with frontend"""
    try:
        if 'top_relevant_markets' not in pipeline_result:
            return None

        events = []
        markets = pipeline_result['top_relevant_markets']

        for market_data in markets:
            # Convert each market to single market event format
            event = {
                'title': market_data.get('title', 'Unknown Market'),
                'question': market_data.get('title', 'Unknown Market'),
                'description': market_data.get('description', 'No description available'),
                'volume': f"${float(market_data.get('volume', 0)):,.0f}" if market_data.get('volume') else '$0',
                'yes_price': float(market_data.get('outcomePrices', ['0.5', '0.5'])[0]) if isinstance(market_data.get('outcomePrices'), list) else 0.5,
                'no_price': float(market_data.get('outcomePrices', ['0.5', '0.5'])[1]) if isinstance(market_data.get('outcomePrices'), list) else 0.5,
                'type': 'single',
                'relevance_score': market_data.get('relevance_score', 0),
                'relevance_explanation': market_data.get('relevance_explanation', 'AI-ranked market')
            }
            events.append(event)

        return {
            'events': events,
            'total_count': len(events),
            'carousel': True,
            'tweet_analysis': {
                'search_query': pipeline_result.get('sentiment_analysis', {}).get('search_query', ''),
                'sentiment_score': pipeline_result.get('sentiment_analysis', {}).get('sentiment_score', 0),
                'key_topics': pipeline_result.get('sentiment_analysis', {}).get('key_topics', [])
            }
        }

    except Exception as e:
        print(f"Error converting pipeline result: {e}")
        return None

@app.route('/api/market', methods=['GET'])
def get_market():
    """Get market data"""
    try:
        # Check if requesting carousel data
        carousel_mode = request.args.get('carousel', 'false').lower() == 'true'
        event_index = request.args.get('event_index', 0, type=int)

        if carousel_mode:
            # Return all events for carousel
            all_events = load_all_events()
            return jsonify({
                'success': True,
                'data': all_events
            })
        else:
            # Return single market data (backwards compatibility)
            market_data = load_market_data()
            return jsonify({
                'success': True,
                'market': market_data
            })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/events', methods=['GET'])
def get_all_events():
    """Get all events for carousel display"""
    try:
        all_events = load_all_events()
        # Return the carousel data directly in the success response
        response = {
            'success': True,
            **all_events  # Spread the carousel data at root level
        }
        return jsonify(response)
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/analyze-tweet', methods=['POST'])
def analyze_tweet_endpoint():
    """Analyze tweet text and return relevant markets"""
    try:
        # Check if tweet analysis is available
        if not TWEET_ANALYSIS_AVAILABLE:
            return jsonify({
                'success': False,
                'error': 'Tweet analysis pipeline not available'
            }), 503

        data = request.get_json()
        if not data or 'tweet_text' not in data:
            return jsonify({
                'success': False,
                'error': 'Missing tweet_text in request body'
            }), 400

        tweet_text = data['tweet_text']
        author = data.get('author', 'TwitterUser')
        top_n = data.get('top_n', 5)

        print(f"🔍 Analyzing tweet: {tweet_text}")

        # Run the tweet analysis pipeline
        pipeline_result = analyze_tweet(tweet_text, author, top_n, save_to_file=False)

        if 'error' in pipeline_result:
            return jsonify({
                'success': False,
                'error': f"Pipeline error: {pipeline_result['error']}"
            }), 500

        # Convert pipeline result to our event format
        events_data = convert_pipeline_to_events(pipeline_result)

        if events_data:
            return jsonify({
                'success': True,
                **events_data  # Spread the events data
            })
        else:
            return jsonify({
                'success': False,
                'error': 'No relevant markets found'
            }), 404

    except Exception as e:
        print(f"Error in tweet analysis endpoint: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/trade', methods=['POST'])
def execute_trade():
    """Execute a trade"""
    try:
        data = request.get_json()
        side = data['side']  # 'YES' or 'NO'
        amount = float(data['amount'])  # USD amount
        market_id = data.get('market_id')  # For multi-market support

        market_data = load_market_data()
        client = setup_client()

        # Handle different market types
        if market_data['type'] == 'multi':
            # Find the specific market
            if not market_id:
                return jsonify({'success': False, 'error': 'Market ID required for multi-market trades'}), 400

            target_market = None
            for market in market_data['markets']:
                if market['id'] == market_id:
                    target_market = market
                    break

            if not target_market:
                return jsonify({'success': False, 'error': 'Market not found'}), 400

            token_id = target_market['yes_token_id'] if side == 'YES' else target_market['no_token_id']
        else:
            # Single market
            token_id = market_data['yes_token_id'] if side == 'YES' else market_data['no_token_id']

        # Create market order
        order = MarketOrderArgs(
            token_id=token_id,
            amount=amount,
            side=BUY,
            order_type=OrderType.FOK
        )

        signed = client.create_market_order(order)
        resp = client.post_order(signed, OrderType.FOK)

        return jsonify({
            'success': True,
            'order_result': resp,
            'side': side,
            'amount': amount,
            'market_id': market_id
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/positions', methods=['GET'])
def get_positions():
    """Get user's positions from Polymarket"""
    try:
        import requests
        
        # Use the authenticated client to get positions
        client = setup_client()
        
        # Get positions using the authenticated client
        print(f"Fetching positions for user: {FUNDER_ADDRESS}")
        
        # Use the correct positions API endpoint
        try:
            # Get API credentials from the authenticated client
            api_creds = client.creds
            headers = {
                'Authorization': f'Bearer {api_creds.api_key}',
                'Content-Type': 'application/json'
            }
            
            # Use the correct data-api.polymarket.com endpoint
            positions_url = f"https://data-api.polymarket.com/positions?user={FUNDER_ADDRESS}"
            print(f"Calling positions API: {positions_url}")
            
            # Try with authentication first
            response = requests.get(positions_url, headers=headers)
            print(f"Response status: {response.status_code}")
            
            if response.ok:
                positions = response.json()
                print(f"✅ Got {len(positions)} positions from Polymarket Data API")
            else:
                # Try without authentication as data-api might be public
                print(f"Auth failed ({response.status_code}), trying without auth...")
                response = requests.get(positions_url)
                if response.ok:
                    positions = response.json()
                    print(f"✅ Got {len(positions)} positions from public Data API")
                else:
                    print(f"❌ Both auth and public API failed: {response.status_code} - {response.text[:200]}")
                    raise Exception(f"API call failed with status {response.status_code}")
                    
        except Exception as e:
            print(f"❌ API call failed: {e}")
            print(f"⚠️ Falling back to sample data for testing")
            with open('data/sampleoneopenposition.json', 'r') as f:
                positions = json.load(f)
                print(f"Using sample data: {len(positions)} positions")
        
        # Transform positions data to match frontend expectations
        formatted_positions = []
        
        for pos in positions:
            # Calculate P&L values
            pnl_dollar = pos.get('cashPnl', 0)
            pnl_percent = pos.get('percentPnl', 0) * 100 if pos.get('percentPnl') else 0
            
            # Determine position status (open/closed based on size)
            position_size = pos.get('size', 0)
            status = 'open' if position_size > 0 else 'closed'
            
            # Format volume
            current_value = pos.get('currentValue', 0)
            if current_value >= 1000000:
                volume_display = f"${current_value/1000000:.1f}M"
            elif current_value >= 1000:
                volume_display = f"${current_value/1000:.0f}K"
            else:
                volume_display = f"${current_value:,.2f}"
            
            formatted_position = {
                'id': hash(pos.get('asset', '')) % 10000,  # Generate a simple ID
                'title': pos.get('title', 'Unknown Market'),
                'position': pos.get('outcome', 'Unknown'),  # YES or NO
                'shares': pos.get('totalBought', 0),
                'avgPrice': pos.get('avgPrice', 0),
                'currentPrice': pos.get('curPrice', 0),
                'pnl': pnl_dollar,
                'pnl_percent': pnl_percent,
                'status': status,
                'volume': volume_display,
                'initialValue': pos.get('initialValue', 0),
                'currentValue': pos.get('currentValue', 0),
                'redeemable': pos.get('redeemable', False),
                'endDate': pos.get('endDate', ''),
                'icon': pos.get('icon', ''),
                'slug': pos.get('slug', '')
            }
            
            formatted_positions.append(formatted_position)
        
        return jsonify({
            'success': True,
            'positions': formatted_positions
        })
        
    except Exception as e:
        print(f"Error fetching positions: {e}")
        # Fall back to sample data for testing
        try:
            with open('data/sampleoneopenposition.json', 'r') as f:
                sample_positions = json.load(f)
                print("Using sample position data as fallback")
                
                formatted_positions = []
                for pos in sample_positions:
                    pnl_dollar = pos.get('cashPnl', 0)
                    position_size = pos.get('size', 0)
                    status = 'open' if position_size > 0 else 'closed'
                    current_value = pos.get('currentValue', 0)
                    
                    if current_value >= 1000000:
                        volume_display = f"${current_value/1000000:.1f}M"
                    elif current_value >= 1000:
                        volume_display = f"${current_value/1000:.0f}K"
                    else:
                        volume_display = f"${current_value:,.2f}"
                    
                    formatted_position = {
                        'id': hash(pos.get('asset', '')) % 10000,
                        'title': pos.get('title', 'Unknown Market'),
                        'position': pos.get('outcome', 'Unknown'),
                        'shares': pos.get('totalBought', 0),
                        'avgPrice': pos.get('avgPrice', 0),
                        'currentPrice': pos.get('curPrice', 0),
                        'pnl': pnl_dollar,
                        'pnl_percent': pos.get('percentPnl', 0) * 100,
                        'status': status,
                        'volume': volume_display,
                        'initialValue': pos.get('initialValue', 0),
                        'currentValue': pos.get('currentValue', 0),
                        'redeemable': pos.get('redeemable', False),
                        'endDate': pos.get('endDate', ''),
                        'icon': pos.get('icon', ''),
                        'slug': pos.get('slug', '')
                    }
                    formatted_positions.append(formatted_position)
                
                return jsonify({
                    'success': True,
                    'positions': formatted_positions
                })
        except:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500

@app.route('/api/closed-positions', methods=['GET'])
def get_closed_positions():
    """Get user's closed positions from Polymarket"""
    try:
        import requests
        
        # Use the authenticated client to get closed positions
        client = setup_client()
        
        print(f"Fetching closed positions for user: {FUNDER_ADDRESS}")
        
        try:
            # Use the authenticated client to get closed positions
            api_creds = client.creds
            headers = {
                'Authorization': f'Bearer {api_creds.api_key}',
                'Content-Type': 'application/json'
            }
            
            # Use the dedicated closed-positions endpoint
            closed_positions_url = f"https://data-api.polymarket.com/closed-positions?user={FUNDER_ADDRESS}"
            print(f"Calling closed positions API: {closed_positions_url}")
            
            # Try with authentication first
            response = requests.get(closed_positions_url, headers=headers)
            
            if response.ok:
                closed_positions = response.json()
                print(f"✅ Got {len(closed_positions)} closed positions from Polymarket Data API")
            else:
                # Try without auth as data-api might be public
                print(f"Auth failed ({response.status_code}), trying without auth...")
                response = requests.get(closed_positions_url)
                if response.ok:
                    closed_positions = response.json()
                    print(f"✅ Got {len(closed_positions)} closed positions from public Data API")
                else:
                    print(f"❌ Both auth and public API failed: {response.status_code} {response.text[:200]}")
                    raise Exception(f"API call failed with status {response.status_code}")
            
            if closed_positions is None:
                raise Exception("All closed positions endpoints failed")
                
        except Exception as e:
            print(f"❌ Closed positions API call failed: {e}")
            print(f"⚠️ Falling back to sample closed position data")
            with open('sample-closed-position.json', 'r') as f:
                sample_position = json.load(f)
                closed_positions = [sample_position]
                print(f"Using sample data: {len(closed_positions)} closed positions")
        
        # Transform closed positions data to match frontend expectations
        formatted_positions = []
        
        for pos in closed_positions:
            # For closed positions, use realizedPnl instead of cashPnl
            pnl_dollar = pos.get('realizedPnl', 0)
            pnl_percent = (pnl_dollar / pos.get('totalBought', 1)) * 100 if pos.get('totalBought', 0) > 0 else 0
            
            # Closed positions always have status 'closed'
            status = 'closed'
            
            # Calculate final value for closed positions
            total_bought = pos.get('totalBought', 0)
            final_value = total_bought + pnl_dollar  # totalBought + realized P&L
            
            if final_value >= 1000000:
                volume_display = f"${final_value/1000000:.1f}M"
            elif final_value >= 1000:
                volume_display = f"${final_value/1000:.0f}K"
            else:
                volume_display = f"${final_value:,.2f}"
            
            formatted_position = {
                'id': hash(pos.get('asset', '')) % 10000,  # Generate a simple ID
                'title': pos.get('title', 'Unknown Market'),
                'position': pos.get('outcome', 'Unknown'),  # YES or NO
                'shares': pos.get('totalBought', 0),
                'avgPrice': pos.get('avgPrice', 0),
                'currentPrice': pos.get('curPrice', 0),
                'pnl': pnl_dollar,
                'pnl_percent': pnl_percent,
                'status': status,
                'volume': volume_display,
                'initialValue': pos.get('totalBought', 0),  # For closed positions
                'currentValue': final_value,
                'redeemable': False,  # Closed positions are not redeemable
                'endDate': pos.get('endDate', ''),
                'icon': pos.get('icon', ''),
                'slug': pos.get('slug', ''),
                'realizedPnl': pnl_dollar  # Keep the original realized P&L
            }
            
            formatted_positions.append(formatted_position)
        
        return jsonify({
            'success': True,
            'positions': formatted_positions
        })
        
    except Exception as e:
        print(f"Error fetching closed positions: {e}")
        # Fall back to sample data for testing
        try:
            with open('sample-closed-position.json', 'r') as f:
                sample_position = json.load(f)
                print("Using sample closed position data as fallback")
                
                # Format the sample position
                pnl_dollar = sample_position.get('realizedPnl', 0)
                total_bought = sample_position.get('totalBought', 0)
                pnl_percent = (pnl_dollar / total_bought * 100) if total_bought > 0 else 0
                final_value = total_bought + pnl_dollar
                
                if final_value >= 1000000:
                    volume_display = f"${final_value/1000000:.1f}M"
                elif final_value >= 1000:
                    volume_display = f"${final_value/1000:.0f}K"
                else:
                    volume_display = f"${final_value:,.2f}"
                
                formatted_position = {
                    'id': hash(sample_position.get('asset', '')) % 10000,
                    'title': sample_position.get('title', 'Unknown Market'),
                    'position': sample_position.get('outcome', 'Unknown'),
                    'shares': sample_position.get('totalBought', 0),
                    'avgPrice': sample_position.get('avgPrice', 0),
                    'currentPrice': sample_position.get('curPrice', 0),
                    'pnl': pnl_dollar,
                    'pnl_percent': pnl_percent,
                    'status': 'closed',
                    'volume': volume_display,
                    'initialValue': sample_position.get('totalBought', 0),
                    'currentValue': final_value,
                    'redeemable': False,
                    'endDate': sample_position.get('endDate', ''),
                    'icon': sample_position.get('icon', ''),
                    'slug': sample_position.get('slug', ''),
                    'realizedPnl': pnl_dollar
                }
                
                return jsonify({
                    'success': True,
                    'positions': [formatted_position]
                })
        except:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500

@app.route('/api/prices', methods=['GET'])
def get_live_prices():
    """Get live market prices"""
    try:
        market_data = load_market_data()
        client = setup_client()
        market_id = request.args.get('market_id')  # For multi-market support

        if market_data['type'] == 'multi':
            if not market_id:
                # Return prices for all markets
                all_prices = []
                for market in market_data['markets']:
                    try:
                        yes_price_resp = client.get_price(market['yes_token_id'], side="BUY")
                        no_price_resp = client.get_price(market['no_token_id'], side="BUY")

                        yes_price = float(yes_price_resp['price']) if yes_price_resp else market['yes_price']
                        no_price = float(no_price_resp['price']) if no_price_resp else market['no_price']

                        all_prices.append({
                            'market_id': market['id'],
                            'candidate': market['candidate'],
                            'yes_price': yes_price,
                            'no_price': no_price
                        })
                    except:
                        # Use fallback prices if API fails
                        all_prices.append({
                            'market_id': market['id'],
                            'candidate': market['candidate'],
                            'yes_price': market['yes_price'],
                            'no_price': market['no_price']
                        })

                return jsonify({
                    'success': True,
                    'type': 'multi',
                    'prices': all_prices
                })
            else:
                # Get prices for specific market
                target_market = None
                for market in market_data['markets']:
                    if market['id'] == market_id:
                        target_market = market
                        break

                if not target_market:
                    return jsonify({'success': False, 'error': 'Market not found'}), 400

                yes_price_resp = client.get_price(target_market['yes_token_id'], side="BUY")
                no_price_resp = client.get_price(target_market['no_token_id'], side="BUY")

                yes_price = float(yes_price_resp['price']) if yes_price_resp else target_market['yes_price']
                no_price = float(no_price_resp['price']) if no_price_resp else target_market['no_price']

                return jsonify({
                    'success': True,
                    'type': 'single',
                    'market_id': market_id,
                    'yes_price': yes_price,
                    'no_price': no_price
                })
        else:
            # Single market
            yes_price_resp = client.get_price(market_data['yes_token_id'], side="BUY")
            no_price_resp = client.get_price(market_data['no_token_id'], side="BUY")

            yes_price = float(yes_price_resp['price']) if yes_price_resp else market_data['yes_price']
            no_price = float(no_price_resp['price']) if no_price_resp else market_data['no_price']

            return jsonify({
                'success': True,
                'type': 'single',
                'yes_price': yes_price,
                'no_price': no_price
            })

    except Exception as e:
        market_data = load_market_data()
        fallback_data = {
            'success': False,
            'error': str(e)
        }

        if market_data['type'] == 'single':
            fallback_data['fallback_prices'] = {
                'yes_price': market_data['yes_price'],
                'no_price': market_data['no_price']
            }

        return jsonify(fallback_data), 500

if __name__ == '__main__':
    print("🚀 Starting Polymarket Trading Backend...")
    market_data = load_market_data()
    if market_data:
        if market_data['type'] == 'multi':
            print(f"📊 Multi-Market Event: {market_data['title']}")
            print(f"📈 Total Volume: {market_data['volume']}")
            print(f"🗳️ {len(market_data['markets'])} candidates/markets:")
            for market in market_data['markets'][:5]:  # Show first 5
                print(f"   • {market['candidate']}: YES {market['yes_price']*100:.1f}¢ | NO {market['no_price']*100:.1f}¢")
            if len(market_data['markets']) > 5:
                print(f"   ... and {len(market_data['markets']) - 5} more")
        else:
            print(f"📊 Single Market: {market_data['question']}")
            print(f"💰 YES: {market_data['yes_price']*100:.1f}¢ | NO: {market_data['no_price']*100:.1f}¢")
            print(f"📈 Volume: {market_data['volume']}")
    else:
        print("❌ Failed to load market data - check files exist!")

    print(f"🌐 Backend running on http://127.0.0.1:5000")
    app.run(debug=True, host='127.0.0.1', port=5000)