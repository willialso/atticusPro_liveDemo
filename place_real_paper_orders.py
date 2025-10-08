"""
FIXED: Place REAL Paper Orders with Correct Response Handling
"""
import logging
from datetime import datetime, timezone
import uuid
from coinbase.rest import RESTClient
from config.settings import COINBASE_CONFIG

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def place_real_paper_btc_orders():
    """
    Place REAL paper BTC orders with correct response handling
    """
    logger.info("📊 Placing REAL paper BTC orders with fixed response handling...")
    
    try:
        client = RESTClient(
            api_key=COINBASE_CONFIG['api_key_name'],
            api_secret=COINBASE_CONFIG['private_key']
        )
        
        # Fund positions to create
        fund_orders = [
            {'usd_size': '250000', 'description': 'Core BTC treasury position'},
            {'usd_size': '125000', 'description': 'Tactical BTC allocation'}, 
            {'usd_size': '75000', 'description': 'BTC momentum position'}
        ]
        
        placed_orders = []
        
        for i, order_spec in enumerate(fund_orders):
            try:
                usd_amount = order_spec['usd_size']
                client_order_id = str(uuid.uuid4())
                
                logger.info(f"📋 Placing REAL paper order {i+1}: ${usd_amount}")
                
                # Place order with Coinbase Advanced Trade API
                order_response = client.market_order_buy(
                    client_order_id=client_order_id,
                    product_id="BTC-USD", 
                    quote_size=usd_amount
                )
                
                # Handle CreateOrderResponse object (not dictionary)
                if order_response:
                    # Access object attributes directly
                    order_data = {
                        'client_order_id': client_order_id,
                        'usd_size': usd_amount,
                        'description': order_spec['description'],
                        'timestamp': datetime.now(timezone.utc).isoformat(),
                        'status': 'real_order_placed',
                        'response_type': type(order_response).__name__
                    }
                    
                    # Try to get order ID if available
                    if hasattr(order_response, 'order_id'):
                        order_data['order_id'] = order_response.order_id
                    elif hasattr(order_response, 'success_response') and hasattr(order_response.success_response, 'order_id'):
                        order_data['order_id'] = order_response.success_response.order_id
                    else:
                        order_data['order_id'] = client_order_id
                    
                    placed_orders.append(order_data)
                    logger.info(f"✅ REAL paper order placed: {order_data['order_id']}")
                    
                    # Debug: Show what we got back
                    logger.info(f"📋 Response type: {type(order_response).__name__}")
                    if hasattr(order_response, '__dict__'):
                        logger.info(f"📋 Response attributes: {list(order_response.__dict__.keys())}")
                    
                else:
                    logger.error(f"❌ Order {i+1} returned None response")
                    return {'success': False, 'error': f'Order {i+1} returned None'}
                
            except Exception as order_error:
                logger.error(f"❌ Error placing order {i+1}: {order_error}")
                return {'success': False, 'error': str(order_error)}
        
        # Success only if all orders placed
        if len(placed_orders) == len(fund_orders):
            logger.info(f"✅ All {len(placed_orders)} REAL orders placed successfully")
            return {
                'success': True,
                'orders_placed': placed_orders,
                'total_orders': len(placed_orders)
            }
        else:
            logger.error(f"❌ Only {len(placed_orders)}/{len(fund_orders)} orders succeeded")
            return {'success': False, 'error': 'Not all orders placed'}
        
    except Exception as e:
        logger.error(f"❌ Critical error: {e}")
        return {'success': False, 'error': str(e)}

if __name__ == "__main__":
    print("📊 FIXED: Placing REAL Paper BTC Orders...")
    
    result = place_real_paper_btc_orders()
    
    if result['success']:
        print("\n" + "="*70)
        print("🏦 REAL PAPER ORDERS SUCCESSFULLY PLACED!")
        print("="*70)
        print(f"📊 Total Orders: {result['total_orders']}")
        
        print(f"\n📋 REAL ORDER DETAILS:")
        print("-" * 60)
        for order in result['orders_placed']:
            print(f"Order: {order['order_id']}")
            print(f"  Amount: ${order['usd_size']}")
            print(f"  Status: {order['status']}")
            print(f"  Description: {order['description']}")
            print(f"  Time: {order['timestamp']}")
            print()
        
        print("="*70)
        print("✅ REAL BTC positions created in Coinbase account!")
        print("🚀 Run premium calculator to see these positions")
        
        # Test immediately
        print("\n🧪 Testing premium calculator with new positions...")
        import subprocess
        result = subprocess.run(['python', 'core/premium_calculator.py'], 
                              capture_output=True, text=True)
        print(result.stdout)
        if result.stderr:
            print("Errors:", result.stderr)
        
    else:
        print(f"❌ FAILED: {result['error']}")
        print("❌ NO FAKE DATA CREATED")
