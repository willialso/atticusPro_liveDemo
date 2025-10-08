"""
Production Coinbase CDP Client
Uses your real API keys for institutional BTC trading platform
"""
import logging
import json
import time
import hmac
import hashlib
import base64
from datetime import datetime, timezone
from typing import Dict, List, Optional
from coinbase.rest import RESTClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CoinbaseClient:
    """Production Coinbase CDP client for institutional BTC platform"""
    
    def __init__(self):
        # Your actual CDP API credentials
        self.api_key_name = "organizations/3b1aa2e8-ad7c-4c7b-b5e5-fa1573b410e2/apiKeys/0a91499e-3a12-40cc-9db5-02bbd6c99e60"
        self.private_key = """-----BEGIN EC PRIVATE KEY-----
MHcCAQEEID3IA1makdc6E89+901M2HxYC2Yat+tm1sHzXw5ioq5aoAoGCCqGSM49
AwEHoUQDQgAERpbWyM+WOoA8c8DjEjoNcKc5a/9v9rTD3Xgh7gwAeL8hhMu4d6fj
uPzhJzBfGQ9XMs09QPaixf5qeDeUYOlSYw==
-----END EC PRIVATE KEY-----"""
        
        self.client = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize production CDP client"""
        try:
            self.client = RESTClient(
                api_key=self.api_key_name,
                api_secret=self.private_key,
                verbose=True
            )
            logger.info("✅ Production Coinbase CDP client initialized")
            
            # Test connection immediately
            self._test_connection()
            
        except Exception as e:
            logger.error(f"❌ CDP client initialization failed: {e}")
            raise
    
    def _test_connection(self):
        """Test CDP API connection with real call"""
        try:
            # Test with accounts endpoint
            accounts = self.client.get_accounts()
            if accounts and hasattr(accounts, 'accounts'):
                logger.info(f"✅ CDP connection verified: {len(accounts.accounts)} accounts found")
                return True
            else:
                logger.warning("⚠️  CDP connection test: No accounts returned")
                return False
                
        except Exception as e:
            logger.error(f"❌ CDP connection test failed: {e}")
            return False
    
    def get_real_btc_price(self) -> float:
        """Get real-time BTC price from Coinbase"""
        try:
            # Use Coinbase Advanced Trade API for BTC-USD
            product = self.client.get_product('BTC-USD')
            
            if product and hasattr(product, 'price') and product.price:
                price = float(product.price)
                logger.info(f"✅ Real BTC price from Coinbase CDP: ${price:,.2f}")
                return price
                
            # Fallback: Get from products list
            products = self.client.get_products()
            if hasattr(products, 'products'):
                for prod in products.products:
                    if hasattr(prod, 'product_id') and prod.product_id == 'BTC-USD':
                        if hasattr(prod, 'price') and prod.price:
                            price = float(prod.price)
                            logger.info(f"✅ Real BTC price from products: ${price:,.2f}")
                            return price
            
            raise Exception("No BTC price data available from Coinbase")
            
        except Exception as e:
            logger.error(f"❌ Coinbase BTC price fetch failed: {e}")
            raise
    
    def get_real_account_positions(self) -> List[Dict]:
        """Get real account positions from Coinbase"""
        try:
            accounts = self.client.get_accounts()
            positions = []
            
            if not accounts or not hasattr(accounts, 'accounts'):
                logger.warning("⚠️  No accounts data returned")
                return positions
            
            logger.info(f"📊 Processing {len(accounts.accounts)} real accounts...")
            
            for account in accounts.accounts:
                try:
                    currency = getattr(account, 'currency', 'UNKNOWN')
                    
                    # Parse balance correctly
                    balance = 0.0
                    if hasattr(account, 'available_balance'):
                        balance_obj = account.available_balance
                        if hasattr(balance_obj, 'value'):
                            balance = float(balance_obj.value)
                        elif isinstance(balance_obj, dict) and 'value' in balance_obj:
                            balance = float(balance_obj['value'])
                    
                    # Include all accounts (even zero balance for visibility)
                    positions.append({
                        'currency': currency,
                        'balance': balance,
                        'account_name': getattr(account, 'name', f'{currency} Wallet'),
                        'account_uuid': getattr(account, 'uuid', 'unknown'),
                        'account_type': getattr(account, 'type', 'unknown'),
                        'data_source': 'coinbase_cdp_real',
                        'timestamp': datetime.now(timezone.utc).isoformat()
                    })
                    
                except Exception as account_error:
                    logger.warning(f"⚠️  Failed to process account: {account_error}")
                    continue
            
            logger.info(f"✅ Retrieved {len(positions)} real account positions")
            return positions
            
        except Exception as e:
            logger.error(f"❌ Real positions fetch failed: {e}")
            raise
    
    def place_real_order(self, order_params: Dict) -> Dict:
        """Place real order through Coinbase CDP (LIVE TRADING)"""
        try:
            logger.warning("🚨 LIVE TRADING ORDER BEING PLACED")
            logger.info(f"📋 Order params: {order_params}")
            
            # Place the real order
            order_response = self.client.create_order(
                client_order_id=order_params.get('client_order_id'),
                product_id=order_params.get('product_id'),
                side=order_params.get('side'),
                order_configuration=order_params.get('order_configuration')
            )
            
            if order_response:
                order_result = {
                    'success': True,
                    'order_id': getattr(order_response, 'order_id', 'unknown'),
                    'status': getattr(order_response, 'status', 'unknown'),
                    'product_id': order_params.get('product_id'),
                    'side': order_params.get('side'),
                    'timestamp': datetime.now(timezone.utc).isoformat(),
                    'execution': 'REAL_LIVE_ORDER',
                    'raw_response': str(order_response)
                }
                
                logger.info(f"✅ REAL order placed: {order_result['order_id']}")
                return order_result
            else:
                raise Exception("No order response received")
                
        except Exception as e:
            logger.error(f"❌ REAL order placement failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'execution': 'REAL_ORDER_FAILED'
            }
    
    def get_order_status(self, order_id: str) -> Dict:
        """Get real order status"""
        try:
            order = self.client.get_order(order_id)
            
            if order:
                return {
                    'order_id': order_id,
                    'status': getattr(order, 'status', 'unknown'),
                    'filled_size': getattr(order, 'filled_size', '0'),
                    'remaining_size': getattr(order, 'remaining_size', '0'),
                    'average_filled_price': getattr(order, 'average_filled_price', '0'),
                    'data_source': 'coinbase_cdp_real',
                    'timestamp': datetime.now(timezone.utc).isoformat()
                }
            else:
                raise Exception("Order not found")
                
        except Exception as e:
            logger.error(f"❌ Order status failed: {e}")
            return {'error': str(e)}

if __name__ == "__main__":
    print("🧪 Testing Production Coinbase CDP Client...")
    
    try:
        client = CoinbaseClient()
        
        print("\n" + "="*60)
        print("📊 PRODUCTION CDP CLIENT TESTS")
        print("="*60)
        
        # Test BTC price
        btc_price = client.get_real_btc_price()
        print(f"✅ Real BTC Price: ${btc_price:,.2f}")
        
        # Test positions
        positions = client.get_real_account_positions()
        print(f"✅ Real Positions: {len(positions)} accounts")
        
        for pos in positions[:5]:  # Show first 5
            if pos['balance'] > 0:
                print(f"   {pos['currency']}: {pos['balance']} ({pos['account_type']})")
        
        print("="*60)
        print("✅ PRODUCTION CDP CLIENT READY FOR INSTITUTIONAL TRADING")
        
    except Exception as e:
        print(f"❌ Production test failed: {e}")
        import traceback
        traceback.print_exc()
