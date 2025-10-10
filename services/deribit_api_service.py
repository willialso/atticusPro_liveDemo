"""
ATTICUS V1 - REAL DERIBIT API INTEGRATION
100% Real pricing, instruments, and execution capabilities
NO SYNTHETIC DATA - All hedge pricing from live Deribit API
"""
import requests
import json
import hmac
import hashlib
import time
from datetime import datetime
from typing import Dict, List, Optional

class RealDeribitAPIService:
    """
    100% Real Deribit API integration for professional hedging
    """
    
    def __init__(self, api_key=None, api_secret=None, testnet=True):
        self.api_key = api_key or "YOUR_DERIBIT_API_KEY"  # Set in environment
        self.api_secret = api_secret or "YOUR_DERIBIT_API_SECRET"
        
        # Use testnet for development, mainnet for production
        if testnet:
            self.base_url = "https://test.deribit.com/api/v2"
            print("⚠️  Using Deribit TESTNET - switch to mainnet for production")
        else:
            self.base_url = "https://www.deribit.com/api/v2"
            print("🎯 Using Deribit MAINNET - live trading")
        
        self.session = requests.Session()
        self.access_token = None
        
        # Authenticate immediately
        self._authenticate()
    
    def _authenticate(self):
        """Authenticate with Deribit API"""
        try:
            print("🔐 Authenticating with Deribit API...")
            
            url = f"{self.base_url}/public/auth"
            data = {
                "grant_type": "client_credentials",
                "client_id": self.api_key,
                "client_secret": self.api_secret
            }
            
            response = self.session.post(url, data=data)
            
            if response.status_code != 200:
                raise Exception(f"Deribit auth failed: {response.status_code} - {response.text}")
            
            result = response.json()
            if 'error' in result:
                raise Exception(f"Deribit auth error: {result['error']['message']}")
            
            self.access_token = result['result']['access_token']
            
            # Set authorization header for future requests
            self.session.headers.update({
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/json'
            })
            
            print("✅ Deribit API authentication successful")
            return True
            
        except Exception as e:
            print(f"❌ Deribit API authentication failed: {e}")
            raise Exception(f"CANNOT OPERATE WITHOUT REAL DERIBIT API ACCESS: {str(e)}")
    
    def get_real_btc_perpetual_price(self) -> Dict:
        """Get REAL BTC perpetual futures pricing from Deribit"""
        try:
            print("📊 Fetching REAL BTC perpetual pricing from Deribit...")
            
            url = f"{self.base_url}/public/get_order_book"
            params = {
                'instrument_name': 'BTC-PERPETUAL',
                'depth': 10
            }
            
            response = self.session.get(url, params=params)
            
            if response.status_code != 200:
                raise Exception(f"Deribit API error: {response.status_code}")
            
            result = response.json()
            if 'error' in result:
                raise Exception(f"Deribit API error: {result['error']['message']}")
            
            order_book = result['result']
            
            # Get best bid/ask for perpetual
            best_bid = float(order_book['bids'][0][0]) if order_book['bids'] else 0
            best_ask = float(order_book['asks'][0][0]) if order_book['asks'] else 0
            mid_price = (best_bid + best_ask) / 2
            spread = best_ask - best_bid
            
            return {
                'instrument': 'BTC-PERPETUAL',
                'mid_price': mid_price,
                'best_bid': best_bid,
                'best_ask': best_ask,
                'spread': spread,
                'spread_pct': (spread / mid_price) * 100,
                'timestamp': datetime.now().isoformat(),
                'data_source': 'Real Deribit API',
                'last_price': float(order_book.get('last_price', mid_price)),
                'mark_price': float(order_book.get('mark_price', mid_price)),
                'volume_24h': float(order_book.get('stats', {}).get('volume_usd', 0))
            }
            
        except Exception as e:
            raise Exception(f"REAL DERIBIT PERPETUAL PRICING FAILED: {str(e)}")
    
    def get_real_available_options(self, currency='BTC') -> List[Dict]:
        """Get REAL available BTC options from Deribit"""
        try:
            print(f"📋 Fetching REAL {currency} options from Deribit...")
            
            url = f"{self.base_url}/public/get_instruments"
            params = {
                'currency': currency,
                'kind': 'option',
                'expired': 'false'
            }
            
            response = self.session.get(url, params=params)
            
            if response.status_code != 200:
                raise Exception(f"Deribit instruments API error: {response.status_code}")
            
            result = response.json()
            if 'error' in result:
                raise Exception(f"Deribit instruments error: {result['error']['message']}")
            
            instruments = result['result']
            
            # Filter and format active options
            active_options = []
            for instrument in instruments:
                if instrument['is_active'] and instrument['settlement_currency'] == currency:
                    active_options.append({
                        'instrument_name': instrument['instrument_name'],
                        'strike': float(instrument['strike']),
                        'option_type': instrument['option_type'],
                        'expiration_timestamp': instrument['expiration_timestamp'],
                        'expiration_date': datetime.fromtimestamp(instrument['expiration_timestamp']/1000).strftime('%Y-%m-%d'),
                        'days_to_expiry': (instrument['expiration_timestamp']/1000 - time.time()) / 86400,
                        'min_trade_amount': float(instrument['min_trade_amount']),
                        'contract_size': float(instrument['contract_size']),
                        'tick_size': float(instrument['tick_size'])
                    })
            
            print(f"✅ Found {len(active_options)} active {currency} options on Deribit")
            
            return active_options
            
        except Exception as e:
            raise Exception(f"REAL DERIBIT OPTIONS RETRIEVAL FAILED: {str(e)}")
    
    def get_real_option_pricing(self, instrument_name: str) -> Dict:
        """Get REAL option pricing from Deribit"""
        try:
            print(f"💰 Fetching REAL pricing for {instrument_name}...")
            
            url = f"{self.base_url}/public/get_order_book"
            params = {
                'instrument_name': instrument_name,
                'depth': 5
            }
            
            response = self.session.get(url, params=params)
            
            if response.status_code != 200:
                raise Exception(f"Deribit option pricing error: {response.status_code}")
            
            result = response.json()
            if 'error' in result:
                raise Exception(f"Deribit option pricing error: {result['error']['message']}")
            
            order_book = result['result']
            
            # Get real option pricing
            best_bid = float(order_book['bids'][0][0]) if order_book['bids'] else 0
            best_ask = float(order_book['asks'][0][0]) if order_book['asks'] else 0
            mid_price = (best_bid + best_ask) / 2 if best_bid and best_ask else 0
            
            # Get Greeks from Deribit
            greeks = order_book.get('greeks', {})
            
            return {
                'instrument_name': instrument_name,
                'mid_price': mid_price,
                'best_bid': best_bid,
                'best_ask': best_ask,
                'spread': best_ask - best_bid,
                'last_price': float(order_book.get('last_price', 0)),
                'mark_price': float(order_book.get('mark_price', 0)),
                'implied_volatility': float(order_book.get('mark_iv', 0)),
                'greeks': {
                    'delta': float(greeks.get('delta', 0)),
                    'gamma': float(greeks.get('gamma', 0)),
                    'theta': float(greeks.get('theta', 0)),
                    'vega': float(greeks.get('vega', 0)),
                    'rho': float(greeks.get('rho', 0))
                },
                'open_interest': float(order_book.get('open_interest', 0)),
                'volume_24h': float(order_book.get('stats', {}).get('volume', 0)),
                'data_source': 'Real Deribit API',
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            raise Exception(f"REAL DERIBIT OPTION PRICING FAILED for {instrument_name}: {str(e)}")
    
    def get_real_hedge_costs(self, hedge_amount_btc: float, instrument_type: str = 'perpetual') -> Dict:
        """Get REAL hedge execution costs from Deribit"""
        try:
            if instrument_type == 'perpetual':
                perp_data = self.get_real_btc_perpetual_price()
                
                # Calculate real execution costs
                execution_price = perp_data['best_ask'] if hedge_amount_btc < 0 else perp_data['best_bid']
                notional_value = abs(hedge_amount_btc) * execution_price
                
                # Real Deribit fees for BTC perpetuals
                maker_fee = 0.0001  # 0.01%
                taker_fee = 0.0005  # 0.05%
                
                # Assume market order (taker)
                trading_fee = notional_value * taker_fee
                
                # Real slippage estimate based on spread
                spread = perp_data['spread']
                slippage_cost = abs(hedge_amount_btc) * (spread / 2)
                
                total_cost = trading_fee + slippage_cost
                
                return {
                    'instrument': 'BTC-PERPETUAL',
                    'hedge_amount_btc': hedge_amount_btc,
                    'execution_price': execution_price,
                    'notional_value': notional_value,
                    'trading_fee': trading_fee,
                    'slippage_cost': slippage_cost,
                    'total_cost': total_cost,
                    'cost_as_pct': (total_cost / notional_value) * 100,
                    'fee_structure': {
                        'maker_fee': maker_fee,
                        'taker_fee': taker_fee,
                        'spread': spread,
                        'spread_pct': perp_data['spread_pct']
                    },
                    'real_deribit_data': True,
                    'timestamp': datetime.now().isoformat()
                }
            
            else:
                raise Exception(f"Hedge cost calculation not implemented for {instrument_type}")
                
        except Exception as e:
            raise Exception(f"REAL HEDGE COST CALCULATION FAILED: {str(e)}")
    
    def find_best_hedge_options(self, target_delta: float, target_vega: float = None) -> List[Dict]:
        """Find best real hedge options from available Deribit instruments"""
        try:
            print(f"🔍 Finding best REAL hedge options for delta: {target_delta:.3f}")
            
            # Get all available options
            available_options = self.get_real_available_options('BTC')
            
            # Filter options suitable for hedging
            hedge_candidates = []
            
            for option in available_options:
                # Focus on options expiring in 7-45 days
                if 7 <= option['days_to_expiry'] <= 45:
                    try:
                        # Get real pricing for this option
                        pricing = self.get_real_option_pricing(option['instrument_name'])
                        
                        if pricing['mid_price'] > 0 and abs(pricing['greeks']['delta']) > 0.05:
                            hedge_candidates.append({
                                **option,
                                **pricing,
                                'hedge_effectiveness': abs(pricing['greeks']['delta'] / target_delta),
                                'cost_per_delta': pricing['mid_price'] / abs(pricing['greeks']['delta']),
                                'vega_hedge_ratio': pricing['greeks']['vega'] / target_vega if target_vega else 0
                            })
                            
                    except Exception as pricing_error:
                        print(f"⚠️  Skipping {option['instrument_name']}: {pricing_error}")
                        continue
            
            # Sort by hedge effectiveness and cost
            hedge_candidates.sort(key=lambda x: x['cost_per_delta'])
            
            print(f"✅ Found {len(hedge_candidates)} viable hedge options from Deribit")
            
            return hedge_candidates[:10]  # Return top 10
            
        except Exception as e:
            raise Exception(f"REAL HEDGE OPTION SEARCH FAILED: {str(e)}")
    
    def validate_hedge_execution(self, instrument_name: str, side: str, amount: float) -> Dict:
        """Validate if hedge can be executed on Deribit (read-only)"""
        try:
            print(f"🔍 Validating hedge execution: {side} {amount} {instrument_name}")
            
            # Get current order book
            if 'PERPETUAL' in instrument_name:
                pricing_data = self.get_real_btc_perpetual_price()
            else:
                pricing_data = self.get_real_option_pricing(instrument_name)
            
            # Check liquidity
            execution_price = pricing_data['best_ask'] if side.upper() == 'SELL' else pricing_data['best_bid']
            
            if execution_price == 0:
                return {
                    'executable': False,
                    'reason': 'No liquidity - no bids/asks available',
                    'recommendation': 'Use limit order or smaller size'
                }
            
            # Estimate execution quality
            spread_pct = pricing_data.get('spread_pct', 0)
            
            return {
                'executable': True,
                'instrument': instrument_name,
                'side': side,
                'amount': amount,
                'estimated_execution_price': execution_price,
                'spread_cost_pct': spread_pct,
                'liquidity_assessment': 'Good' if spread_pct < 0.1 else 'Fair' if spread_pct < 0.5 else 'Poor',
                'real_deribit_validation': True,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'executable': False,
                'reason': f'Validation failed: {str(e)}',
                'recommendation': 'Check instrument name and Deribit connectivity'
            }
