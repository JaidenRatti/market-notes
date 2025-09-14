import json
import os
from dotenv import load_dotenv
from py_clob_client.client import ClobClient
from py_clob_client.clob_types import MarketOrderArgs, OrderType
from py_clob_client.order_builder.constants import BUY, SELL

load_dotenv()

HOST = "https://clob.polymarket.com"
CHAIN_ID = 137
PRIVATE_KEY = os.getenv("magickey")
FUNDER_ADDRESS = os.getenv("funder")

def load_market_data(json_file):
    """Load market data from JSON file"""
    with open(json_file, 'r') as f:
        data = json.load(f)

    market = data['events'][0]['markets'][0]  # First market

    # Extract token IDs for YES/NO
    token_ids = json.loads(market['clobTokenIds'])
    prices = json.loads(market['outcomePrices'])

    return {
        'question': market['question'],
        'yes_token_id': token_ids[0],  # First token is YES
        'no_token_id': token_ids[1],   # Second token is NO
        'yes_price': float(prices[0]),
        'no_price': float(prices[1]),
        'outcomes': json.loads(market['outcomes'])
    }

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

def buy_yes(client, yes_token_id, amount_usd):
    """Buy YES shares (betting it will happen)"""
    print(f"🟢 BUYING YES for ${amount_usd}")

    order = MarketOrderArgs(
        token_id=yes_token_id,
        amount=amount_usd,
        side=BUY,
        order_type=OrderType.FOK
    )
    signed = client.create_market_order(order)
    resp = client.post_order(signed, OrderType.FOK)
    print(f"YES order result: {resp}")
    return resp

def buy_no(client, no_token_id, amount_usd):
    """Buy NO shares (betting it won't happen)"""
    print(f"🔴 BUYING NO for ${amount_usd}")

    order = MarketOrderArgs(
        token_id=no_token_id,
        amount=amount_usd,
        side=BUY,
        order_type=OrderType.FOK
    )
    signed = client.create_market_order(order)
    resp = client.post_order(signed, OrderType.FOK)
    print(f"NO order result: {resp}")
    return resp

def sell_yes(client, yes_token_id, amount_usd):
    """Sell YES shares (close long YES position)"""
    print(f"🟢 SELLING YES for ${amount_usd}")

    order = MarketOrderArgs(
        token_id=yes_token_id,
        amount=amount_usd,
        side=SELL,
        order_type=OrderType.FOK
    )
    signed = client.create_market_order(order)
    resp = client.post_order(signed, OrderType.FOK)
    print(f"YES sell result: {resp}")
    return resp

def sell_no(client, no_token_id, amount_usd):
    """Sell NO shares (close long NO position)"""
    print(f"🔴 SELLING NO for ${amount_usd}")

    order = MarketOrderArgs(
        token_id=no_token_id,
        amount=amount_usd,
        side=SELL,
        order_type=OrderType.FOK
    )
    signed = client.create_market_order(order)
    resp = client.post_order(signed, OrderType.FOK)
    print(f"NO sell result: {resp}")
    return resp

def get_current_prices(client, yes_token_id, no_token_id):
    """Get live prices for both tokens"""
    try:
        yes_price_resp = client.get_price(yes_token_id, side="BUY")
        no_price_resp = client.get_price(no_token_id, side="BUY")

        # Extract actual price from response
        yes_price = float(yes_price_resp['price']) if yes_price_resp else 0
        no_price = float(no_price_resp['price']) if no_price_resp else 0

        return yes_price, no_price
    except Exception as e:
        print(f"Error getting prices: {e}")
        return None, None

def get_my_balances(client, yes_token_id, no_token_id):
    """Get your current token balances"""
    try:
        from py_clob_client.clob_types import BalanceAllowanceParams, AssetType

        # Get YES balance
        yes_resp = client.get_balance_allowance(
            params=BalanceAllowanceParams(
                asset_type=AssetType.CONDITIONAL,
                token_id=yes_token_id,
            )
        )
        yes_balance = float(yes_resp['balance']) if yes_resp else 0

        # Get NO balance
        no_resp = client.get_balance_allowance(
            params=BalanceAllowanceParams(
                asset_type=AssetType.CONDITIONAL,
                token_id=no_token_id,
            )
        )
        no_balance = float(no_resp['balance']) if no_resp else 0

        return yes_balance, no_balance
    except Exception as e:
        print(f"Error getting balances: {e}")
        return 0, 0

def sell_all_yes(client, yes_token_id):
    """Sell ALL your YES shares"""
    try:
        from py_clob_client.clob_types import BalanceAllowanceParams, AssetType

        # Get YES balance
        yes_resp = client.get_balance_allowance(
            params=BalanceAllowanceParams(
                asset_type=AssetType.CONDITIONAL,
                token_id=yes_token_id,
            )
        )
        yes_balance = float(yes_resp['balance']) if yes_resp else 0

        if yes_balance == 0:
            print("❌ No YES shares to sell")
            return None

        # Get current sell price
        sell_price = client.get_price(yes_token_id, side="SELL")
        total_value = yes_balance * sell_price

        print(f"🟢 SELLING ALL YES: {yes_balance} shares (${total_value:.2f} value)")

        order = MarketOrderArgs(
            token_id=yes_token_id,
            amount=total_value,
            side=SELL,
            order_type=OrderType.FOK
        )
        signed = client.create_market_order(order)
        resp = client.post_order(signed, OrderType.FOK)
        print(f"Sell all YES result: {resp}")
        return resp

    except Exception as e:
        print(f"Error selling all YES: {e}")
        return None

def sell_all_no(client, no_token_id):
    """Sell ALL your NO shares"""
    try:
        from py_clob_client.clob_types import BalanceAllowanceParams, AssetType

        # Get NO balance
        no_resp = client.get_balance_allowance(
            params=BalanceAllowanceParams(
                asset_type=AssetType.CONDITIONAL,
                token_id=no_token_id,
            )
        )
        no_balance = float(no_resp['balance']) if no_resp else 0

        if no_balance == 0:
            print("❌ No NO shares to sell")
            return None

        # Get current sell price
        sell_price = client.get_price(no_token_id, side="SELL")
        total_value = no_balance * sell_price

        print(f"🔴 SELLING ALL NO: {no_balance} shares (${total_value:.2f} value)")

        order = MarketOrderArgs(
            token_id=no_token_id,
            amount=total_value,
            side=SELL,
            order_type=OrderType.FOK
        )
        signed = client.create_market_order(order)
        resp = client.post_order(signed, OrderType.FOK)
        print(f"Sell all NO result: {resp}")
        return resp

    except Exception as e:
        print(f"Error selling all NO: {e}")
        return None

if __name__ == "__main__":
    # Load market data from JSON
    print("=== Loading Market Data ===")
    market_data = load_market_data('samplein.json')

    print(f"Market: {market_data['question']}")
    print(f"Current YES price: ${market_data['yes_price']}")
    print(f"Current NO price: ${market_data['no_price']}")
    print(f"YES Token ID: {market_data['yes_token_id']}")
    print(f"NO Token ID: {market_data['no_token_id']}")

    # Setup client
    print("\n=== Setting up Client ===")
    client = setup_client()

    # Get live prices
    print("\n=== Live Prices ===")
    live_yes, live_no = get_current_prices(client, market_data['yes_token_id'], market_data['no_token_id'])
    if live_yes and live_no:
        print(f"Live YES price: ${live_yes}")
        print(f"Live NO price: ${live_no}")

    # Get your current balances
    print("\n=== Your Balances ===")
    yes_balance, no_balance = get_my_balances(client, market_data['yes_token_id'], market_data['no_token_id'])
    print(f"YES shares: {yes_balance}")
    print(f"NO shares: {no_balance}")
    if yes_balance > 0:
        print(f"YES value: ${yes_balance * live_yes:.2f}")
    if no_balance > 0:
        print(f"NO value: ${no_balance * live_no:.2f}")

    # EXAMPLE TRADES (uncomment to execute)
    #
    # # Buy $5 worth of YES (betting Russia WILL invade)
    # buy_yes(client, market_data['yes_token_id'], 5.0)
    #
    # # Buy $5 worth of NO (betting Russia will NOT invade)
    # buy_no(client, market_data['no_token_id'], 5.0)
    #
    # # Sell $3 worth of YES shares (partial)
    # sell_yes(client, market_data['yes_token_id'], 3.0)
    #
    # # Sell ALL your YES shares
    sell_all_yes(client, market_data['yes_token_id'])
    #
    # # Sell ALL your NO shares
    # sell_all_no(client, market_data['no_token_id'])

    print("\n✅ Ready to trade! Uncomment the example trades above to execute.")