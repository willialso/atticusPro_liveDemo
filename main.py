"""
Institutional BTC Options Platform - Main Application
"""
import sys
import json
from core.perp_reader import PerpPositionReader

def main():
    print("🏦 Institutional BTC Options Platform - Phase 1")
    print("=" * 50)
    
    try:
        # Initialize position reader
        print("📊 Initializing position reader...")
        reader = PerpPositionReader()
        
        # Get position summary
        print("🔍 Fetching position summary...")
        summary = reader.get_position_summary()
        
        # Display results
        print("\n📈 POSITION SUMMARY:")
        print("-" * 30)
        
        exposure = summary['exposure_summary']
        print(f"Net BTC Exposure: {exposure['net_exposure_btc']:.4f} BTC")
        print(f"Long Positions: {exposure['long_exposure_btc']:.4f} BTC")
        print(f"Short Positions: {exposure['short_exposure_btc']:.4f} BTC")
        print(f"Total Notional: ${exposure['total_notional_usd']:,.2f}")
        print(f"Unrealized P&L: ${exposure['total_unrealized_pnl']:,.2f}")
        print(f"Position Count: {exposure['position_count']}")
        
        print(f"\n🕐 Last Updated: {summary['last_updated']}")
        print(f"📊 Status: {summary['status'].upper()}")
        
        print("\n✅ Phase 1 Step 1 completed successfully!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
