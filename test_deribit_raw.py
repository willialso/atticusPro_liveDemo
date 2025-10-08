"""
Debug Deribit Options Discovery
Find out what options are actually available
"""
import ccxt
from datetime import datetime, timezone

def debug_deribit_options():
    print("🔍 Debugging Deribit Options Discovery...")
    
    try:
        client = ccxt.deribit({'enableRateLimit': True, 'sandbox': False})
        
        # Get current BTC price
        ticker = client.fetch_ticker('BTC-PERPETUAL')
        btc_price = float(ticker['last'])
        print(f"📊 Current BTC Price: ${btc_price:,.2f}")
        
        # Load all markets
        markets = client.load_markets()
        
        # Find BTC options
        btc_options = []
        for symbol, market in markets.items():
            if (market['base'] == 'BTC' and 
                market['type'] == 'option' and 
                market['active']):
                btc_options.append(symbol)
        
        print(f"📋 Found {len(btc_options)} active BTC options")
        
        # Show first 10 option symbols
        print("\n🎯 Sample Option Symbols:")
        for i, symbol in enumerate(btc_options[:10]):
            print(f"  {i+1}. {symbol}")
        
        # Test ticker data for first few options
        print(f"\n💰 Testing Ticker Data:")
        for symbol in btc_options[:3]:
            try:
                option_ticker = client.fetch_ticker(symbol)
                print(f"  {symbol}:")
                print(f"    Bid: {option_ticker.get('bid', 'N/A')}")
                print(f"    Ask: {option_ticker.get('ask', 'N/A')}")
                print(f"    Volume: {option_ticker.get('baseVolume', 'N/A')}")
            except Exception as e:
                print(f"    Error: {e}")
        
        return btc_options
        
    except Exception as e:
        print(f"❌ Debug failed: {e}")
        return []

if __name__ == "__main__":
    options = debug_deribit_options()
