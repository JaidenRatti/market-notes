#!/usr/bin/env python3

import requests
import json

def test_positions_api():
    """Test the positions API endpoint"""
    print("🧪 Testing Full Integration")
    print("=" * 50)
    
    try:
        print("🔍 Testing positions API...")
        response = requests.get("http://127.0.0.1:5000/api/positions", timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                positions = data.get('positions', [])
                print(f"✅ API Success: {len(positions)} positions")
                
                if positions:
                    pos = positions[0]
                    print(f"📊 Sample Position:")
                    print(f"   Title: {pos.get('title')}")
                    print(f"   Position: {pos.get('position')} ({pos.get('shares')} shares)")
                    print(f"   P&L: ${pos.get('pnl'):.4f} ({pos.get('pnl_percent'):.2f}%)")
                    print(f"   Status: {pos.get('status')}")
                    print(f"   Value: {pos.get('volume')}")
                    
                    print(f"\n🎯 Expected Frontend Display:")
                    print(f"   - Header: 'Polymarket Positions (Live)'")
                    print(f"   - Open positions: {len([p for p in positions if p['status'] == 'open'])}")
                    print(f"   - Closed positions: {len([p for p in positions if p['status'] == 'closed'])}")
                    print(f"   - No popup when clicking position cards")
                    print(f"   - No duplicate sections when scrolling")
                    
                else:
                    print("⚠️ No positions found - will show empty state")
                    
            else:
                print(f"❌ API Error: {data.get('error')}")
        else:
            print(f"❌ HTTP {response.status_code}: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Backend not running! Start it with:")
        print("   python3 trading_backend.py")
        return False
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False
        
    print(f"\n💡 Testing Steps:")
    print(f"   1. ✅ Backend API working")
    print(f"   2. 📱 Open Chrome extension on your Twitter profile")
    print(f"   3. 👀 Look for 'Polymarket Positions (Live)' section")
    print(f"   4. 🖱️ Click position cards - should NOT open popup")
    print(f"   5. 📜 Scroll down/up - should NOT create duplicates")
    
    return True

if __name__ == "__main__":
    success = test_positions_api()
    if success:
        print(f"\n🎉 Integration test passed! Extension should work properly.")
    else:
        print(f"\n😞 Integration test failed. Fix backend issues first.")
