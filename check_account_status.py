"""
FIXED: Check REAL Account Status with Correct Balance Parsing
"""
import logging
from coinbase.rest import RESTClient
from config.settings import COINBASE_CONFIG

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_real_account_status():
    """Check real account with fixed balance parsing"""
    logger.info("📊 Checking REAL account with fixed parsing...")
    
    try:
        client = RESTClient(
            api_key=COINBASE_CONFIG['api_key_name'],
            api_secret=COINBASE_CONFIG['private_key']
        )
        
        print("📊 REAL ACCOUNT STATUS (FIXED PARSING):")
        print("="*60)
        
        # Fixed account balance parsing
        try:
            accounts_response = client.get_accounts()
            
            if hasattr(accounts_response, 'accounts'):
                print("💰 Account Balances:")
                
                total_usd = 0
                total_btc = 0
                
                for account in accounts_response.accounts:
                    currency = getattr(account, 'currency', 'UNKNOWN')
                    
                    # Handle nested balance structure properly
                    balance = 0.0
                    if hasattr(account, 'available_balance'):
                        balance_obj = account.available_balance
                        
                        # Handle different balance object types
                        if hasattr(balance_obj, 'value'):
                            balance = float(balance_obj.value)
                        elif isinstance(balance_obj, dict):
                            balance = float(balance_obj.get('value', 0))
                        elif isinstance(balance_obj, (str, int, float)):
                            balance = float(balance_obj)
                    
                    print(f"  {currency}: {balance}")
                    
                    if currency == 'USD':
                        total_usd = balance
                    elif currency == 'BTC':
                        total_btc = balance
                
                print(f"\n🎯 KEY FINDINGS:")
                print(f"  💵 Total USD: ${total_usd:,.2f}")
                print(f"  ₿  Total BTC: {total_btc:.8f} BTC")
                
                if total_btc > 0:
                    current_btc_price = 122100  # Approximate current price
                    btc_value_usd = total_btc * current_btc_price
                    print(f"  💰 BTC Value: ~${btc_value_usd:,.2f}")
                    print(f"  ✅ BTC positions exist!")
                    print(f"  ✅ Premium calculator should work now!")
                else:
                    print(f"  ⚠️  No BTC found despite filled orders")
                
        except Exception as balance_error:
            print(f"❌ Balance parsing error: {balance_error}")
            print("❌ Trying alternative balance method...")
            
            # Alternative approach - raw response inspection
            try:
                accounts_response = client.get_accounts()
                print(f"📋 Raw account response type: {type(accounts_response)}")
                
                if hasattr(accounts_response, '__dict__'):
                    print(f"📋 Response attributes: {list(accounts_response.__dict__.keys())}")
                    
            except Exception as alt_error:
                print(f"❌ Alternative method failed: {alt_error}")
        
        # Check the filled orders details
        try:
            print(f"\n📋 FILLED ORDER DETAILS:")
            orders = client.list_orders(limit=5)
            
            if hasattr(orders, 'orders'):
                btc_orders = [o for o in orders.orders if getattr(o, 'product_id', '') == 'BTC-USD']
                print(f"  BTC Orders Found: {len(btc_orders)}")
                
                total_btc_bought = 0
                for order in btc_orders:
                    status = getattr(order, 'status', 'unknown')
                    filled_size = getattr(order, 'filled_size', '0')
                    
                    if status == 'FILLED' and filled_size:
                        try:
                            btc_amount = float(filled_size)
                            total_btc_bought += btc_amount
                            print(f"  ✅ Bought {btc_amount:.6f} BTC (Status: {status})")
                        except ValueError:
                            print(f"  ⚠️  Order filled but size parsing failed: {filled_size}")
                
                if total_btc_bought > 0:
                    print(f"  🎯 Total BTC from recent orders: {total_btc_bought:.6f} BTC")
                    print(f"  💡 Orders successful - checking settlement...")
                
        except Exception as orders_error:
            print(f"❌ Error checking filled orders: {orders_error}")
        
        print("="*60)
        
    except Exception as e:
        logger.error(f"❌ Critical error: {e}")

if __name__ == "__main__":
    print("🔍 FIXED: Checking REAL Account Status...")
    check_real_account_status()
