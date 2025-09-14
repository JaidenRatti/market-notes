#!/usr/bin/env python3

import json
import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from py_clob_client.client import ClobClient
from py_clob_client.clob_types import MarketOrderArgs, OrderType
from py_clob_client.order_builder.constants import BUY, SELL

load_dotenv()

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
        with open('samplein.json', 'r') as f:
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
        with open('samplemultimarkets.json', 'r') as f:
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

@app.route('/api/market', methods=['GET'])
def get_market():
    """Get market data"""
    try:
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