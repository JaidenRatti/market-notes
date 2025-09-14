import os
from dotenv import load_dotenv
from py_clob_client.client import ClobClient
from py_clob_client.clob_types import MarketOrderArgs, OrderArgs, OrderType
from py_clob_client.order_builder.constants import BUY, SELL

load_dotenv()

HOST = "https://clob.polymarket.com"
CHAIN_ID = 137  # Polygon

# Magic wallet configuration
PRIVATE_KEY = os.getenv("magickey")
FUNDER_ADDRESS = os.getenv("funder")

def test_connection():
    """Test basic read-only connection"""
    client = ClobClient(HOST)
    ok = client.get_ok()
    time = client.get_server_time()
    print(f"Connection test - OK: {ok}, Server time: {time}")
    return client

def setup_authenticated_client():
    """Setup authenticated client for Magic wallet"""
    client = ClobClient(
        HOST,
        key=PRIVATE_KEY,
        chain_id=CHAIN_ID,
        signature_type=1,  # Magic wallet signatures
        funder=FUNDER_ADDRESS
    )
    client.set_api_creds(client.create_or_derive_api_creds())
    print("Authenticated client setup complete")
    return client

def get_markets(client):
    """Get available markets"""
    markets = client.get_simplified_markets()
    print(f"Found {len(markets['data'])} markets")
    return markets

def get_market_info(client, token_id):
    """Get pricing info for a specific token"""
    try:
        mid = client.get_midpoint(token_id)
        buy_price = client.get_price(token_id, side="BUY")
        sell_price = client.get_price(token_id, side="SELL")
        book = client.get_order_book(token_id)

        print(f"Token {token_id}:")
        print(f"  Midpoint: {mid}")
        print(f"  Buy price: {buy_price}")
        print(f"  Sell price: {sell_price}")
        print(f"  Market: {book.market}")

        return mid, buy_price, sell_price
    except Exception as e:
        print(f"Error getting market info: {e}")
        return None

def place_market_order(client, token_id, amount, side=BUY):
    """Place a market order (buy/sell by dollar amount)"""
    try:
        order = MarketOrderArgs(
            token_id=token_id,
            amount=amount,
            side=side,
            order_type=OrderType.FOK
        )
        signed = client.create_market_order(order)
        resp = client.post_order(signed, OrderType.FOK)
        print(f"Market order placed: {resp}")
        return resp
    except Exception as e:
        print(f"Error placing market order: {e}")
        return None

def place_limit_order(client, token_id, price, size, side=BUY):
    """Place a limit order (specific price and size)"""
    try:
        order = OrderArgs(
            token_id=token_id,
            price=price,
            size=size,
            side=side
        )
        signed = client.create_order(order)
        resp = client.post_order(signed, OrderType.GTC)
        print(f"Limit order placed: {resp}")
        return resp
    except Exception as e:
        print(f"Error placing limit order: {e}")
        return None

def get_user_orders(client):
    """Get your open orders"""
    try:
        from py_clob_client.clob_types import OpenOrderParams
        orders = client.get_orders(OpenOrderParams())
        print(f"You have {len(orders)} open orders")
        return orders
    except Exception as e:
        print(f"Error getting orders: {e}")
        return []

def cancel_all_orders(client):
    """Cancel all your open orders"""
    try:
        client.cancel_all()
        print("All orders cancelled")
    except Exception as e:
        print(f"Error cancelling orders: {e}")

if __name__ == "__main__":
    # Test basic connection
    print("=== Testing Connection ===")
    basic_client = test_connection()

    # Setup authenticated client
    print("\n=== Setting up Authenticated Client ===")
    auth_client = setup_authenticated_client()

    # Get markets
    print("\n=== Getting Markets ===")
    markets = get_markets(basic_client)

    # Find a market with active orderbook
    if markets and markets['data']:
        print("\n=== Finding Active Market ===")
        active_token_id = None

        # Try first 10 markets to find one with orderbook
        for i, market in enumerate(markets['data'][:10]):
            print(f"Checking market {i+1}: {market.get('question', 'Unknown')[:50]}...")

            tokens = market.get('tokens', [])
            if tokens:
                token_id = tokens[0]['token_id']
                try:
                    # Test if orderbook exists
                    basic_client.get_order_book(token_id)
                    active_token_id = token_id
                    print(f"✅ Found active market: {market.get('question', 'Unknown')}")
                    break
                except:
                    continue

        if active_token_id:
            print(f"\n=== Market Info for Token {active_token_id} ===")
            get_market_info(basic_client, active_token_id)

            # Uncomment to place actual orders (use small amounts!)
            # print(f"\n=== Placing Test Market Order ===")
            # place_market_order(auth_client, active_token_id, 1.0, BUY)  # $1 buy order

            # print(f"\n=== Placing Test Limit Order ===")
            # place_limit_order(auth_client, active_token_id, 0.01, 5.0, BUY)  # 5 shares at $0.01
        else:
            print("❌ No active markets found in first 10 results")

    # Check your orders
    print("\n=== Your Orders ===")
    get_user_orders(auth_client)