import json
import os
from dotenv import load_dotenv
from py_clob_client.client import ClobClient
from py_clob_client.clob_types import MarketOrderArgs, OrderType, OpenOrderParams
from py_clob_client.order_builder.constants import BUY, SELL

load_dotenv()

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

def show_all_available_methods(client):
    """Debug: show all available methods"""
    methods = [method for method in dir(client) if not method.startswith('_')]
    print("Available client methods:")
    for method in methods:
        print(f"  - {method}")

def get_my_orders(client):
    """Get all your orders"""
    try:
        orders = client.get_orders(OpenOrderParams())
        print(f"You have {len(orders)} orders")
        return orders
    except Exception as e:
        print(f"Error getting orders: {e}")
        return []

def get_my_trades(client):
    """Get your trades"""
    try:
        trades = client.get_trades()
        print(f"You have {len(trades)} trades")
        return trades
    except Exception as e:
        print(f"Error getting trades: {e}")
        return []

def explore_positions(client):
    """Try different methods to find positions"""
    print("\n=== Exploring Position Methods ===")

    # Try various methods
    methods_to_try = [
        'get_positions',
        'get_balance',
        'get_balances',
        'get_portfolio',
        'get_user_positions',
        'get_open_positions'
    ]

    for method_name in methods_to_try:
        if hasattr(client, method_name):
            try:
                method = getattr(client, method_name)
                result = method()
                print(f"✅ {method_name}(): {result}")
            except Exception as e:
                print(f"❌ {method_name}(): {e}")
        else:
            print(f"⚠️  {method_name}: method doesn't exist")

if __name__ == "__main__":
    client = setup_client()

    # Show available methods
    show_all_available_methods(client)

    print("\n" + "="*50)

    # Explore different ways to get positions
    explore_positions(client)

    print("\n" + "="*50)

    # Try orders and trades
    get_my_orders(client)
    get_my_trades(client)