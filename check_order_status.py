"""
Check REAL Order Status - No Fake Data
"""
import logging
from coinbase.rest import RESTClient
from config.settings import COINBASE_CONFIG

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_real_order_status():
    """Check status of real orders placed"""
    logger.info("📊 Checking REAL order status...")
    
    try:
        client = RESTClient(
            api_key=COINBASE_CONFIG['api_key_name'],
            api_secret=COINBASE_CONFIG['private_key']
        )
        
        # These are the REAL order IDs from your successful placement
        real_order_ids = [
            '1071ea8b-19ca-4458-afe2-6c8c42463e34',
            '882f9eb6-88cb-407f-ae9f-4cdfd6688ce1', 
            'fb69218e-b050-44e0-929d-21c87f08da7d'
        ]
        
        print("📋 REAL ORDER STATUS CHECK:")
        print("="*60)
        
        for i, order_id in enumerate(real_order_ids):
            try:
                # Get order details
                order = client.get_order(order_id)
                
                print(f"\nOrder {i+1}: {order_id}")
                
                if hasattr(order, 'order'):
                    order_details = order.order
                    print(f"  Status: {getattr(order_details, 'status', 'unknown')}")
                    print(f"  Side: {getattr(order_details, 'side', 'unknown')}")
                    print(f"  Product: {getattr(order_details, 'product_id', 'unknown')}")
                    print(f"  Filled Size: {getattr(order_details, 'filled_size', '0')}")
                    print(f"  Filled Value: {getattr(order_details, 'filled_value', '0')}")
                    
                    # Check if order is filled
                    status = getattr(order_details, 'status', '').upper()
                    if status == 'FILLED':
                        print(f"  ✅ Order FILLED successfully")
                    elif status in ['PENDING', 'OPEN']:
                        print(f"  ⏳ Order still {status}")
                    elif status == 'CANCELLED':
                        print(f"  ❌ Order was CANCELLED")
                    else:
                        print(f"  ❓ Order status: {status}")
                else:
                    print(f"  ❌ Could not get order details")
                    
            except Exception as order_error:
                print(f"  ❌ Error checking order: {order_error}")
        
        # Check account balances
        print(f"\n📊 CURRENT ACCOUNT BALANCES:")
        print("="*40)
        
        try:
            accounts = client.get_accounts()
            if hasattr(accounts, 'accounts'):
                for account in accounts.accounts:
                    balance = float(account.available_balance.value) if hasattr(account, 'available_balance') and account.available_balance else 0
                    if balance > 0 or account.currency in ['BTC', 'USD']:
                        print(f"  {account.currency}: {balance}")
        except Exception as balance_error:
            print(f"  ❌ Error getting balances: {balance_error}")
        
        print("="*60)
        
    except Exception as e:
        logger.error(f"❌ Error checking order status: {e}")

if __name__ == "__main__":
    print("🔍 Checking REAL Order Status...")
    check_real_order_status()
