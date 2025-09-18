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
import os
current_dir = os.path.dirname(os.path.abspath(__file__))
tweet_pipeline_path = os.path.join(current_dir, 'tweet-market-pipeline')
tweet_include_path = os.path.join(current_dir, 'tweet-market-pipeline', 'include')

sys.path.insert(0, tweet_pipeline_path)
sys.path.insert(0, tweet_include_path)

load_dotenv()

# Import tweet analyzer (add error handling for missing dependencies)
TWEET_ANALYSIS_AVAILABLE = False
analyze_tweet = None

try:
    print(f"🔍 [DEBUG] Attempting to import from: {tweet_pipeline_path}")
    print(f"🔍 [DEBUG] Include path: {tweet_include_path}")
    print(f"🔍 [DEBUG] Current working dir: {os.getcwd()}")
    print(f"🔍 [DEBUG] Pipeline path exists: {os.path.exists(tweet_pipeline_path)}")
    print(f"🔍 [DEBUG] tweet_analyzer.py exists: {os.path.exists(os.path.join(tweet_pipeline_path, 'tweet_analyzer.py'))}")
    print(f"🔍 [DEBUG] Python path: {sys.path[:3]}...")
    
    # Test import step by step
    print(f"🔍 [DEBUG] Testing imports...")
    import tweet_analyzer
    print(f"✅ [DEBUG] tweet_analyzer module imported")
    
    from tweet_analyzer import analyze_tweet
    print(f"✅ [DEBUG] analyze_tweet function imported")
    
    # Test if it actually works
    test_result = analyze_tweet("test", save_to_file=False, top_n=1)
    print(f"✅ [DEBUG] Test analysis completed, keys: {list(test_result.keys()) if isinstance(test_result, dict) else type(test_result)}")
    
    TWEET_ANALYSIS_AVAILABLE = True
    print("✅ [DEBUG] Tweet analysis pipeline loaded successfully")
    
except ImportError as e:
    print(f"❌ [DEBUG] IMPORT ERROR: {e}")
    print(f"❌ [DEBUG] Import error type: {type(e).__name__}")
    import traceback
    traceback.print_exc()
    TWEET_ANALYSIS_AVAILABLE = False
    
except Exception as e:
    print(f"❌ [DEBUG] OTHER ERROR: {e}")
    print(f"❌ [DEBUG] Error type: {type(e).__name__}")
    import traceback
    traceback.print_exc()
    TWEET_ANALYSIS_AVAILABLE = False
    
print(f"🔍 TWEET_ANALYSIS_AVAILABLE = {TWEET_ANALYSIS_AVAILABLE}")

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
        print(f"🔍 Converting pipeline result: {pipeline_result.keys() if isinstance(pipeline_result, dict) else type(pipeline_result)}")
        
        # Handle new format (Option 1) with original API objects
        if 'events' in pipeline_result and 'relevance_metadata' in pipeline_result:
            print(f"✅ Processing NEW format with original Polymarket API objects")
            return convert_new_format_to_events(pipeline_result)
        
        # Handle old format (for backward compatibility)
        elif 'top_relevant_markets' in pipeline_result:
            print(f"⚠️ Processing OLD format - consider updating to new format")
            return convert_old_format_to_events(pipeline_result)
        
        else:
            print(f"❌ Unknown pipeline result format")
            print(f"🔍 Available keys: {list(pipeline_result.keys()) if isinstance(pipeline_result, dict) else 'Not a dict'}")
            return None
            
    except Exception as e:
        print(f"❌ Error converting pipeline result: {e}")
        print(f"❌ Pipeline result structure: {pipeline_result}")
        import traceback
        print(f"❌ Full traceback: {traceback.format_exc()}")
        return None

def convert_new_format_to_events(pipeline_result):
    """Return PURE Polymarket events array - UNMODIFIED"""
    try:
        events = pipeline_result['events']  # Original Polymarket API objects
        print(f"🎯 Returning {len(events)} PURE Polymarket events")
        print(f"✅ NO CONVERSION - exact Polymarket API format")
        
        # LOG: Show what we're actually returning
        print(f"\n🔍 [CONVERSION] EVENTS BEING RETURNED:")
        for i, event in enumerate(events[:2]):  # Show first 2 events
            print(f"Event {i+1} keys: {list(event.keys()) if isinstance(event, dict) else type(event)}")
            if isinstance(event, dict):
                # Show critical fields that frontend needs
                critical_fields = ['id', 'title', 'question', 'description', 'markets', 'outcomePrices', 'clobTokenIds']
                for field in critical_fields:
                    if field in event:
                        value = event[field]
                        if isinstance(value, (list, dict)):
                            print(f"  {field}: {type(value).__name__} with {len(value)} items" if hasattr(value, '__len__') else f"  {field}: {type(value).__name__}")
                        else:
                            print(f"  {field}: {value}"[:100] + ("..." if len(str(value)) > 100 else ""))
            print("---")
        
        # Return EXACTLY what the AI pipeline found - pure Polymarket events
        return {
            'success': True,
            'events': events,  # Raw Polymarket API array - ZERO changes
            'total_count': len(events),
            'carousel': True
        }
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def convert_old_format_to_events(pipeline_result):
    """Convert old format (transformed objects) to frontend format - DEPRECATED"""
    try:
        markets = pipeline_result['top_relevant_markets']
        print(f"🎯 Processing {len(markets)} markets from OLD pipeline format")
        
        events = []
        for i, market_data in enumerate(markets):
            print(f"📊 Processing market {i+1}: {market_data.get('title', 'Unknown')}")
            
            # Extract market data from the old pipeline result structure
            market_info = market_data.get('market_data', {})
            
            # Get volume - check various possible fields
            volume = 0
            if 'volume' in market_info:
                try:
                    volume = float(market_info['volume'].replace('$', '').replace(',', '').replace('K', '000').replace('M', '000000'))
                except:
                    volume = 0
            
            # Format volume for display
            if volume >= 1000000:
                volume_display = f"${volume/1000000:.1f}M"
            elif volume >= 1000:
                volume_display = f"${volume/1000:.0f}K"
            else:
                volume_display = f"${volume:,.0f}"
            
            # Extract prices - try different possible structures
            yes_price = 0.5  # default
            no_price = 0.5   # default
            
            # Check if outcome prices are in the market data
            if 'outcomePrices' in market_info:
                try:
                    if isinstance(market_info['outcomePrices'], list):
                        yes_price = float(market_info['outcomePrices'][0])
                        no_price = float(market_info['outcomePrices'][1])
                    elif isinstance(market_info['outcomePrices'], str):
                        # Parse JSON string
                        import json
                        prices = json.loads(market_info['outcomePrices'])
                        yes_price = float(prices[0])
                        no_price = float(prices[1])
                except Exception as parse_error:
                    print(f"⚠️ Could not parse outcome prices: {parse_error}")
                    # Use random but realistic prices for demo
                    import random
                    yes_price = random.uniform(0.3, 0.7)
                    no_price = 1.0 - yes_price
            
            # Convert each market to single market event format
            event = {
                'title': market_data.get('title', 'Unknown Market'),
                'question': market_data.get('title', 'Unknown Market'),
                'description': market_data.get('relevance_explanation', market_info.get('description', 'AI-generated market prediction')),
                'volume': volume_display,
                'yesPrice': yes_price,  # Use camelCase to match frontend expectations
                'noPrice': no_price,    # Use camelCase to match frontend expectations
                'yes_price': yes_price, # Keep snake_case for backward compatibility
                'no_price': no_price,   # Keep snake_case for backward compatibility
                'type': 'single',
                'relevance_score': market_data.get('relevance_score', 0),
                'relevance_explanation': market_data.get('relevance_explanation', 'AI-ranked market relevant to your tweet'),
                'market_id': market_data.get('ticker', f'ai_market_{i+1}'),
                'ticker': market_data.get('ticker', f'ai_market_{i+1}'),
                'rank': market_data.get('rank', i+1),
                'category': market_info.get('category', 'AI Prediction'),
                'end_date': market_info.get('end_date', '2025-12-31'),
                'active': market_info.get('active', True)
            }
            events.append(event)
            print(f"✅ Converted market {i+1}: {event['title']} (Score: {event['relevance_score']:.2f})")

        print(f"🎯 Successfully converted {len(events)} events using OLD format")
        
        return {
            'events': events,
            'total_count': len(events),
            'carousel': True,
            'tweet_analysis': {
                'search_query': pipeline_result.get('sentiment_analysis', {}).get('search_query', ''),
                'sentiment_score': pipeline_result.get('sentiment_analysis', {}).get('sentiment_score', 0),
                'key_topics': pipeline_result.get('sentiment_analysis', {}).get('key_topics', [])
            },
            'source': 'ai_analysis_v1'  # Mark as old format
        }
        
    except Exception as e:
        print(f"❌ Error converting old format: {e}")
        return None

        events = []
        markets = pipeline_result['top_relevant_markets']
        print(f"🎯 Processing {len(markets)} markets from pipeline")

        for i, market_data in enumerate(markets):
            print(f"📊 Processing market {i+1}: {market_data.get('title', 'Unknown')}")
            
            # Extract market data from the pipeline result structure
            market_info = market_data.get('market_data', {})
            
            # Get volume - check various possible fields
            volume = 0
            if 'volume' in market_info:
                try:
                    volume = float(market_info['volume'].replace('$', '').replace(',', '').replace('K', '000').replace('M', '000000'))
                except:
                    volume = 0
            
            # Format volume for display
            if volume >= 1000000:
                volume_display = f"${volume/1000000:.1f}M"
            elif volume >= 1000:
                volume_display = f"${volume/1000:.0f}K"
            else:
                volume_display = f"${volume:,.0f}"
            
            # Extract prices - try different possible structures
            yes_price = 0.5  # default
            no_price = 0.5   # default
            
            # Check if outcome prices are in the market data
            if 'outcomePrices' in market_info:
                try:
                    if isinstance(market_info['outcomePrices'], list):
                        yes_price = float(market_info['outcomePrices'][0])
                        no_price = float(market_info['outcomePrices'][1])
                    elif isinstance(market_info['outcomePrices'], str):
                        # Parse JSON string
                        import json
                        prices = json.loads(market_info['outcomePrices'])
                        yes_price = float(prices[0])
                        no_price = float(prices[1])
                except Exception as parse_error:
                    print(f"⚠️ Could not parse outcome prices: {parse_error}")
                    # Use random but realistic prices for demo
                    import random
                    yes_price = random.uniform(0.3, 0.7)
                    no_price = 1.0 - yes_price
            
            # Convert each market to single market event format
            event = {
                'title': market_data.get('title', 'Unknown Market'),
                'question': market_data.get('title', 'Unknown Market'),
                'description': market_data.get('relevance_explanation', market_info.get('description', 'AI-generated market prediction')),
                'volume': volume_display,
                'yesPrice': yes_price,  # Use camelCase to match frontend expectations
                'noPrice': no_price,    # Use camelCase to match frontend expectations
                'yes_price': yes_price, # Keep snake_case for backward compatibility
                'no_price': no_price,   # Keep snake_case for backward compatibility
                'type': 'single',
                'relevance_score': market_data.get('relevance_score', 0),
                'relevance_explanation': market_data.get('relevance_explanation', 'AI-ranked market relevant to your tweet'),
                'market_id': market_data.get('ticker', f'ai_market_{i+1}'),
                'ticker': market_data.get('ticker', f'ai_market_{i+1}'),
                'rank': market_data.get('rank', i+1),
                'category': market_info.get('category', 'AI Prediction'),
                'end_date': market_info.get('end_date', '2025-12-31'),
                'active': market_info.get('active', True)
            }
            events.append(event)
            print(f"✅ Converted market {i+1}: {event['title']} (Score: {event['relevance_score']:.2f})")

        print(f"🎯 Successfully converted {len(events)} events")
        
        return {
            'events': events,
            'total_count': len(events),
            'carousel': True,
            'tweet_analysis': {
                'search_query': pipeline_result.get('sentiment_analysis', {}).get('search_query', ''),
                'sentiment_score': pipeline_result.get('sentiment_analysis', {}).get('sentiment_score', 0),
                'key_topics': pipeline_result.get('sentiment_analysis', {}).get('key_topics', [])
            },
            'source': 'ai_analysis'  # Mark this as AI-generated content
        }

    except Exception as e:
        print(f"❌ Error converting pipeline result: {e}")
        print(f"❌ Pipeline result structure: {pipeline_result}")
        import traceback
        print(f"❌ Full traceback: {traceback.format_exc()}")
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
        print(f"\n{'='*60}")
        print(f"🚀 TWEET ANALYSIS ENDPOINT CALLED")
        print(f"{'='*60}")
        
        # Check if tweet analysis is available
        print(f"🔍 [DEBUG] TWEET_ANALYSIS_AVAILABLE = {TWEET_ANALYSIS_AVAILABLE}")
        print(f"🔍 [DEBUG] analyze_tweet function = {analyze_tweet}")
        
        if not TWEET_ANALYSIS_AVAILABLE:
            print(f"❌ [DEBUG] Tweet analysis pipeline not available")
            print(f"❌ [DEBUG] This is why the endpoint is returning 503")
            return jsonify({
                'success': False,
                'error': 'Tweet analysis pipeline not available - dependencies may be missing'
            }), 503

        data = request.get_json()
        print(f"📝 Request data: {data}")
        
        if not data or 'tweet_text' not in data:
            print(f"❌ Missing tweet_text in request")
            return jsonify({
                'success': False,
                'error': 'Missing tweet_text in request body'
            }), 400

        tweet_text = data['tweet_text']
        author = data.get('author', 'TwitterUser')
        top_n = data.get('top_n', 5)

        print(f"🔍 Analyzing tweet from @{author}: '{tweet_text[:100]}{'...' if len(tweet_text) > 100 else ''}'")
        print(f"📊 Requesting top {top_n} markets")

        # Run the tweet analysis pipeline
        print(f"🤖 Starting AI analysis pipeline...")
        pipeline_result = analyze_tweet(tweet_text, author, top_n, save_to_file=False)
        print(f"✅ Pipeline analysis complete")
        print(f"📋 Pipeline result keys: {list(pipeline_result.keys()) if isinstance(pipeline_result, dict) else 'Not a dict'}")
        
        # LOG STEP 1: Raw pipeline result
        print(f"\n🔍 [STEP 1] RAW PIPELINE RESULT:")
        print(f"Pipeline type: {type(pipeline_result)}")
        if isinstance(pipeline_result, dict):
            for key in pipeline_result.keys():
                value = pipeline_result[key]
                if key == 'events' and isinstance(value, list):
                    print(f"  {key}: list of {len(value)} items")
                    for i, item in enumerate(value[:2]):  # Show first 2
                        print(f"    Event {i+1}: {json.dumps(item, indent=6, default=str)[:800]}...")
                else:
                    print(f"  {key}: {json.dumps(value, indent=4, default=str)[:500]}...")
        else:
            print(json.dumps(pipeline_result, indent=2, default=str)[:1500] + "...")

        if 'error' in pipeline_result:
            print(f"❌ Pipeline returned error: {pipeline_result['error']}")
            return jsonify({
                'success': False,
                'error': f"Pipeline error: {pipeline_result['error']}"
            }), 500

        # Check if pipeline found any markets - handle both formats
        if 'events' in pipeline_result:  # NEW format
            markets_count = len(pipeline_result['events'])
            print(f"🎯 Pipeline found {markets_count} relevant markets (NEW format)")
            
            if markets_count == 0:
                tweet_analysis = pipeline_result.get('tweet_analysis', {})
                print(f"⚠️ No markets found for this tweet")
                return jsonify({
                    'success': False,
                    'error': 'No relevant markets found for this tweet content',
                    'debug_info': {
                        'search_query': tweet_analysis.get('search_query', 'Unknown'),
                        'sentiment_score': tweet_analysis.get('sentiment_score', 0)
                    }
                }), 404
        elif 'top_relevant_markets' in pipeline_result:  # OLD format
            markets_count = len(pipeline_result['top_relevant_markets'])
            print(f"🎯 Pipeline found {markets_count} relevant markets (OLD format)")
            
            if markets_count == 0:
                print(f"⚠️ No markets found for this tweet")
                return jsonify({
                    'success': False,
                    'error': 'No relevant markets found for this tweet content',
                    'debug_info': {
                        'search_query': pipeline_result.get('sentiment_analysis', {}).get('search_query', 'Unknown'),
                        'sentiment_score': pipeline_result.get('sentiment_analysis', {}).get('sentiment_score', 0)
                    }
                }), 404
        else:
            print(f"❌ Pipeline result missing both 'events' and 'top_relevant_markets' fields")
            return jsonify({
                'success': False,
                'error': 'Invalid pipeline response format',
                'debug_info': {
                    'available_keys': list(pipeline_result.keys())
                }
            }), 500

        # Convert pipeline result to our event format
        print(f"🔄 Converting pipeline result to event format...")
        
        # LOG STEP 2: Before conversion
        print(f"\n🔍 [STEP 2] BEFORE CONVERSION:")
        print(f"Input keys: {list(pipeline_result.keys()) if isinstance(pipeline_result, dict) else 'Not dict'}")
        if 'events' in pipeline_result:
            print(f"Events count: {len(pipeline_result['events'])}")
            print(f"First event structure: {list(pipeline_result['events'][0].keys()) if pipeline_result['events'] else 'No events'}")
        
        events_data = convert_pipeline_to_events(pipeline_result)
        
        # LOG STEP 3: After conversion
        print(f"\n🔍 [STEP 3] AFTER CONVERSION:")
        if events_data:
            print(f"Converted data keys: {list(events_data.keys())}")
            if 'events' in events_data:
                print(f"Converted events count: {len(events_data['events'])}")
                if events_data['events']:
                    first_event = events_data['events'][0]
                    print(f"First converted event keys: {list(first_event.keys()) if isinstance(first_event, dict) else type(first_event)}")
                    print(f"First converted event sample:")
                    print(json.dumps(first_event, indent=4, default=str)[:1000] + "...")
        else:
            print("Conversion returned None")

        if events_data and events_data.get('events'):
            events_count = len(events_data['events'])
            print(f"✅ Successfully converted to {events_count} events")
            print(f"🎯 Returning events for carousel display")
            
            response = {
                'success': True,
                **events_data  # Spread the events data
            }
            
            print(f"📤 Response keys: {list(response.keys())}")
            
            # LOG STEP 4: Final response to frontend
            print(f"\n🔍 [STEP 4] FINAL RESPONSE TO FRONTEND:")
            print(f"Response structure: success={response.get('success')}, total_count={response.get('total_count')}, carousel={response.get('carousel')}")
            print(f"Events array length: {len(response.get('events', []))}")
            if response.get('events'):
                print(f"First response event sample:")
                first_event = response['events'][0]
                print(json.dumps(first_event, indent=4, default=str)[:1200] + "...")
            
            print(f"{'='*60}")
            return jsonify(response)
        else:
            print(f"❌ Event conversion failed or produced no events")
            return jsonify({
                'success': False,
                'error': 'Failed to convert markets to display format',
                'debug_info': {
                    'pipeline_keys': list(pipeline_result.keys()),
                    'conversion_result': 'None' if events_data is None else 'Empty events'
                }
            }), 500

    except Exception as e:
        print(f"❌ CRITICAL ERROR in tweet analysis endpoint: {e}")
        import traceback
        print(f"❌ Full traceback: {traceback.format_exc()}")
        return jsonify({
            'success': False,
            'error': f"Internal server error: {str(e)}",
            'debug_info': {
                'error_type': type(e).__name__,
                'tweet_analysis_available': TWEET_ANALYSIS_AVAILABLE
            }
        }), 500

@app.route('/api/trade', methods=['POST'])
def execute_trade():
    """Execute a REAL trade on Polymarket"""
    try:
        data = request.get_json()
        print(f"\n💵 [TRADE] REAL TRADE REQUEST: {data}")
        
        side = data['side']  # 'YES' or 'NO'
        amount = float(data['amount'])  # USD amount
        market_id = data.get('market_id')  # For multi-market support
        yes_token_id = data.get('yes_token_id')  # Token IDs from frontend
        no_token_id = data.get('no_token_id')
        
        print(f"💵 [TRADE] EXECUTING REAL {side} TRADE for ${amount}")
        print(f"💵 [TRADE] Market ID: {market_id}")
        print(f"💵 [TRADE] Token IDs - YES: {yes_token_id}, NO: {no_token_id}")
        
        # Validate token IDs
        if not yes_token_id or not no_token_id:
            print(f"❌ [TRADE] ERROR: Missing token IDs")
            return jsonify({
                'success': False,
                'error': f'Token IDs required for real trading. YES: {yes_token_id}, NO: {no_token_id}',
                'side': side,
                'amount': amount,
                'market_id': market_id
            }), 400
        
        # Get authenticated client
        client = setup_client()
        print(f"💵 [TRADE] Client setup complete")
        
        # Select the correct token ID based on side
        token_id = yes_token_id if side == 'YES' else no_token_id
        print(f"💵 [TRADE] Using token ID: {token_id} for {side} trade")
        
        # Create and execute the market order
        from py_clob_client.order_builder.constants import BUY
        from py_clob_client.clob_types import OrderType, MarketOrderArgs
        
        order = MarketOrderArgs(
            token_id=token_id,
            amount=amount,
            side=BUY,
            order_type=OrderType.FOK  # Fill or Kill
        )
        
        print(f"💵 [TRADE] Created order: {order}")
        
        # Sign and submit the order
        signed = client.create_market_order(order)
        print(f"💵 [TRADE] Order signed")
        
        resp = client.post_order(signed, OrderType.FOK)
        print(f"💵 [TRADE] Order posted, response: {resp}")
        
        return jsonify({
            'success': True,
            'order_result': resp,
            'side': side,
            'amount': amount,
            'market_id': market_id,
            'token_id': token_id,
            'message': f'Successfully placed {side} order for ${amount}'
        })

    except Exception as e:
        print(f"❌ [TRADE] Trade execution error: {e}")
        import traceback
        print(f"❌ [TRADE] Full traceback: {traceback.format_exc()}")
        return jsonify({
            'success': False,
            'error': f'Trade failed: {str(e)}'
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
        
        # LOG: Show raw API response structure
        print(f"\n🔍 [POSITIONS] RAW API RESPONSE:")
        print(f"Response type: {type(positions)}")
        print(f"Positions count: {len(positions) if isinstance(positions, list) else 'Not a list'}")
        if isinstance(positions, list) and positions:
            print(f"First position keys: {list(positions[0].keys()) if isinstance(positions[0], dict) else type(positions[0])}")
            print(f"First position sample:")
            print(json.dumps(positions[0], indent=4, default=str)[:1000] + "...")
        
        # RETURN RAW API DATA - NO TRANSFORMATION
        print(f"✅ Returning PURE Polymarket positions API data - NO CONVERSION")
        return jsonify({
            'success': True,
            'positions': positions  # EXACT API response
        })
        
    except Exception as e:
        print(f"Error fetching positions: {e}")
        # Fall back to sample data for testing
        try:
            with open('data/sampleoneopenposition.json', 'r') as f:
                sample_positions = json.load(f)
                print("Using sample position data as fallback")
                
                # LOG: Show sample data structure
                print(f"\n🔍 [FALLBACK POSITIONS] SAMPLE DATA:")
                print(f"Sample type: {type(sample_positions)}")
                print(f"Sample count: {len(sample_positions) if isinstance(sample_positions, list) else 'Not a list'}")
                if isinstance(sample_positions, list) and sample_positions:
                    print(f"First sample keys: {list(sample_positions[0].keys()) if isinstance(sample_positions[0], dict) else type(sample_positions[0])}")
                
                # RETURN RAW SAMPLE DATA - NO TRANSFORMATION
                print(f"✅ Returning PURE sample positions data - NO CONVERSION")
                return jsonify({
                    'success': True,
                    'positions': sample_positions  # EXACT sample data
                })
        except FileNotFoundError:
            return jsonify({
                'success': False,
                'error': 'Sample position file not found and API failed'
            }), 500
        except Exception as fallback_error:
            return jsonify({
                'success': False,
                'error': f'API failed and sample data error: {str(fallback_error)}'
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
        
        # LOG: Show raw closed positions API response
        print(f"\n🔍 [CLOSED POSITIONS] RAW API RESPONSE:")
        print(f"Response type: {type(closed_positions)}")
        print(f"Closed positions count: {len(closed_positions) if isinstance(closed_positions, list) else 'Not a list'}")
        if isinstance(closed_positions, list) and closed_positions:
            print(f"First closed position keys: {list(closed_positions[0].keys()) if isinstance(closed_positions[0], dict) else type(closed_positions[0])}")
            print(f"First closed position sample:")
            print(json.dumps(closed_positions[0], indent=4, default=str)[:1000] + "...")
        
        # RETURN RAW API DATA - NO TRANSFORMATION
        print(f"✅ Returning PURE Polymarket closed positions API data - NO CONVERSION")
        return jsonify({
            'success': True,
            'positions': closed_positions  # EXACT API response
        })
        
    except Exception as e:
        print(f"Error fetching closed positions: {e}")
        # Fall back to sample data for testing
        try:
            with open('sample-closed-position.json', 'r') as f:
                sample_position = json.load(f)
                print("Using sample closed position data as fallback")
                
                # Wrap single position in array to match API format
                sample_positions = [sample_position] if not isinstance(sample_position, list) else sample_position
                
                # LOG: Show sample closed position data
                print(f"\n🔍 [FALLBACK CLOSED POSITIONS] SAMPLE DATA:")
                print(f"Sample type: {type(sample_positions)}")
                print(f"Sample count: {len(sample_positions)}")
                if sample_positions:
                    print(f"First sample keys: {list(sample_positions[0].keys()) if isinstance(sample_positions[0], dict) else type(sample_positions[0])}")
                
                # RETURN RAW SAMPLE DATA - NO TRANSFORMATION
                print(f"✅ Returning PURE sample closed positions data - NO CONVERSION")
                return jsonify({
                    'success': True,
                    'positions': sample_positions  # EXACT sample data
                })
        except FileNotFoundError:
            return jsonify({
                'success': False,
                'error': 'Sample closed position file not found and API failed'
            }), 500
        except Exception as fallback_error:
            return jsonify({
                'success': False,
                'error': f'Closed positions API failed and sample data error: {str(fallback_error)}'
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