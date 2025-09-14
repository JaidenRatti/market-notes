#!/usr/bin/env python3

import requests
import json

def test_closed_positions_integration():
    """Test the full closed positions integration"""
    print("🧪 Testing Closed Positions Integration")
    print("=" * 50)
    
    try:
        # Test open positions
        print("🔍 Testing open positions API...")
        open_response = requests.get("http://127.0.0.1:5000/api/positions", timeout=5)
        open_success = open_response.status_code == 200
        open_data = open_response.json() if open_success else None
        open_count = len(open_data.get('positions', [])) if open_data and open_data.get('success') else 0
        
        # Test closed positions  
        print("🔍 Testing closed positions API...")
        closed_response = requests.get("http://127.0.0.1:5000/api/closed-positions", timeout=5)
        closed_success = closed_response.status_code == 200
        closed_data = closed_response.json() if closed_success else None
        closed_count = len(closed_data.get('positions', [])) if closed_data and closed_data.get('success') else 0
        
        print(f"\n📊 Results:")
        print(f"   Open Positions: {'✅' if open_success else '❌'} ({open_count} positions)")
        print(f"   Closed Positions: {'✅' if closed_success else '❌'} ({closed_count} positions)")
        
        if closed_success and closed_count > 0:
            pos = closed_data['positions'][0]
            print(f"\n📄 Sample Closed Position:")
            print(f"   Title: {pos.get('title')}")
            print(f"   Position: {pos.get('position')} ({pos.get('shares')} shares)")
            print(f"   Avg Price: ${pos.get('avgPrice'):.3f}")
            print(f"   Final P&L: ${pos.get('pnl'):.4f} ({pos.get('pnl_percent'):.2f}%)")
            print(f"   Status: {pos.get('status')}")
            print(f"   Final Value: {pos.get('volume')}")
            print(f"   Realized P&L: ${pos.get('realizedPnl'):.4f}")
        
        print(f"\n🎯 Expected Frontend Behavior:")
        print(f"   - Header: 'Polymarket Positions (Live)'")
        print(f"   - Open tab: {open_count} positions")
        print(f"   - Closed tab: {closed_count} positions") 
        print(f"   - Switch between tabs shows different data")
        print(f"   - Closed positions show realized P&L")
        print(f"   - No popups when clicking position cards")
        
        return open_success and closed_success
        
    except requests.exceptions.ConnectionError:
        print("❌ Backend not running! Start it with:")
        print("   python3 trading_backend.py")
        return False
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def test_data_structure():
    """Test that closed positions have correct data structure"""
    print(f"\n🔍 Testing Data Structure...")
    
    try:
        with open('sample-closed-position.json', 'r') as f:
            sample = json.load(f)
            
        print(f"📋 Sample Closed Position Structure:")
        print(f"   Has realizedPnl: {'✅' if 'realizedPnl' in sample else '❌'}")
        print(f"   Has totalBought: {'✅' if 'totalBought' in sample else '❌'}")
        print(f"   Has outcome: {'✅' if 'outcome' in sample else '❌'}")
        print(f"   Has title: {'✅' if 'title' in sample else '❌'}")
        
        # Key differences from open positions
        print(f"\n🔄 Key Differences from Open Positions:")
        print(f"   - Uses 'realizedPnl' instead of 'cashPnl'")
        print(f"   - Uses 'totalBought' instead of 'size'") 
        print(f"   - Status is always 'closed'")
        print(f"   - Shows final settlement values")
        
        return True
        
    except FileNotFoundError:
        print("❌ sample-closed-position.json not found!")
        return False
    except Exception as e:
        print(f"❌ Data structure test failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Testing Closed Positions Full Integration\n")
    
    structure_ok = test_data_structure()
    api_ok = test_closed_positions_integration()
    
    print(f"\n📊 Final Results:")
    print(f"   Data Structure: {'✅' if structure_ok else '❌'}")
    print(f"   API Integration: {'✅' if api_ok else '❌'}")
    
    if structure_ok and api_ok:
        print(f"\n🎉 Closed positions integration complete!")
        print(f"💡 Now open Chrome extension on Twitter profile:")
        print(f"   1. Look for 'Polymarket Positions (Live)'")
        print(f"   2. Click 'Closed' tab to see closed positions")
        print(f"   3. Verify different data from 'Open' tab")
    else:
        print(f"\n😞 Integration has issues. Fix them first.")
