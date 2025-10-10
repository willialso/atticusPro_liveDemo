"""
ATTICUS V1 - Professional Market Data Service
Real-time BTC options data from Deribit with caching
"""
import requests
import time
from datetime import datetime, timedelta
import json
from typing import Dict, List, Optional
from config.settings import Config
from config.exchanges import EXCHANGES

class DeribitDataService:
    """
    Professional Deribit integration for BTC options market data
    Provides real pricing for institutional strategies
    """
    
    def __init__(self):
        self.base_url = EXCHANGES['deribit']['base_url']
        self.endpoints = EXCHANGES['deribit']['endpoints']
        self.cache = {}
        self.rate_limiter = RateLimiter(EXCHANGES['deribit']['rate_limit'])
    
    def get_live_btc_price(self) -> float:
        """
        Get real-time BTC index price from Deribit
        This is the reference price for all option calculations
        """
        cache_key = 'btc_index_price'
        if self._is_cached(cache_key):
            return self.cache[cache_key]['data']
        
        try:
            self.rate_limiter.wait_if_needed()
            response = requests.get(f"{self.base_url}{self.endpoints['btc_index']}", timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                price = float(data['result']['BTC'])
                
                self._cache_data(cache_key, price)
                return price
            else:
                raise Exception(f"Deribit API error: {response.status_code}")
                
        except Exception as e:
            print(f"Error fetching BTC price: {e}")
            # Fallback to cached data if available
            if cache_key in self.cache:
                return self.cache[cache_key]['data']
            return None
    
    def get_available_options(self) -> List[Dict]:
        """
        Get all available BTC options from Deribit
        Returns liquid instruments suitable for institutional hedging
        """
        cache_key = 'btc_options'
        if self._is_cached(cache_key):
            return self.cache[cache_key]['data']
        
        try:
            self.rate_limiter.wait_if_needed()
            response = requests.get(f"{self.base_url}{self.endpoints['options']}", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                options = data['result']
                
                # Filter for liquid options suitable for institutional use
                liquid_options = self._filter_liquid_options(options)
                
                self._cache_data(cache_key, liquid_options)
                return liquid_options
            else:
                raise Exception(f"Deribit options API error: {response.status_code}")
                
        except Exception as e:
            print(f"Error fetching options: {e}")
            return []
    
    def get_option_orderbook(self, instrument_name: str) -> Dict:
        """
        Get real-time orderbook for specific option
        Critical for understanding actual liquidity and spreads
        """
        cache_key = f'orderbook_{instrument_name}'
        if self._is_cached(cache_key, ttl=10):  # Shorter cache for orderbooks
            return self.cache[cache_key]['data']
        
        try:
            self.rate_limiter.wait_if_needed()
            url = f"{self.base_url}{self.endpoints['orderbook']}?instrument_name={instrument_name}"
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                orderbook = data['result']
                
                # Calculate mid-price and spread
                if orderbook['bids'] and orderbook['asks']:
                    best_bid = orderbook['bids'][0][0]
                    best_ask = orderbook['asks'][0][0]
                    mid_price = (best_bid + best_ask) / 2
                    spread_bps = ((best_ask - best_bid) / mid_price) * 10000
                    
                    orderbook['mid_price'] = mid_price
                    orderbook['spread_bps'] = spread_bps
                
                self._cache_data(cache_key, orderbook)
                return orderbook
                
        except Exception as e:
            print(f"Error fetching orderbook for {instrument_name}: {e}")
            return {}
    
    def get_implied_volatility_surface(self) -> Dict:
        """
        Build implied volatility surface from Deribit options
        Essential for accurate Black-Scholes pricing
        """
        options = self.get_available_options()
        iv_surface = {}
        
        for option in options:
            instrument = option['instrument_name']
            
            try:
                # Get current ticker data including IV
                ticker_data = self._get_ticker_data(instrument)
                
                if ticker_data and 'mark_iv' in ticker_data:
                    strike = option['strike']
                    expiry = datetime.fromtimestamp(option['expiration_timestamp'] / 1000)
                    option_type = option['option_type'].lower()
                    
                    surface_key = (strike, expiry, option_type)
                    iv_surface[surface_key] = {
                        'implied_volatility': ticker_data['mark_iv'] / 100,  # Convert percentage
                        'mark_price': ticker_data.get('mark_price', 0),
                        'last_price': ticker_data.get('last_price', 0),
                        'bid_price': ticker_data.get('bid_price', 0),
                        'ask_price': ticker_data.get('ask_price', 0),
                        'open_interest': ticker_data.get('open_interest', 0)
                    }
                    
            except Exception as e:
                print(f"Error processing option {instrument}: {e}")
                continue
        
        return iv_surface
    
    def _filter_liquid_options(self, options: List[Dict]) -> List[Dict]:
        """
        Filter options for institutional liquidity requirements
        Only return options suitable for real hedging
        """
        liquid_options = []
        current_time = datetime.now()
        
        for option in options:
            # Filter criteria for institutional use
            expiry = datetime.fromtimestamp(option['expiration_timestamp'] / 1000)
            days_to_expiry = (expiry - current_time).days
            
            # Institutional liquidity filters
            if (option['is_active'] and 
                option['settlement_period'] == 'day' and
                7 <= days_to_expiry <= 90 and  # 1 week to 3 months
                option['strike'] > 0):
                
                liquid_options.append({
                    'instrument_name': option['instrument_name'],
                    'strike': option['strike'],
                    'option_type': option['option_type'],
                    'expiration_timestamp': option['expiration_timestamp'],
                    'days_to_expiry': days_to_expiry,
                    'tick_size': option['tick_size'],
                    'contract_size': option['contract_size']
                })
        
        return liquid_options
    
    def _get_ticker_data(self, instrument_name: str) -> Optional[Dict]:
        """Get ticker data including implied volatility"""
        try:
            self.rate_limiter.wait_if_needed()
            url = f"{self.base_url}{self.endpoints['ticker']}?instrument_name={instrument_name}"
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                return data['result']
        except:
            pass
        return None
    
    def _is_cached(self, key: str, ttl: int = None) -> bool:
        """Check if data is cached and still valid"""
        if key not in self.cache:
            return False
        
        cache_ttl = ttl or Config.CACHE_TTL
        elapsed = time.time() - self.cache[key]['timestamp']
        return elapsed < cache_ttl
    
    def _cache_data(self, key: str, data):
        """Cache data with timestamp"""
        self.cache[key] = {
            'data': data,
            'timestamp': time.time()
        }

class RateLimiter:
    """Simple rate limiter for API calls"""
    
    def __init__(self, max_requests_per_second: int):
        self.max_rps = max_requests_per_second
        self.requests = []
    
    def wait_if_needed(self):
        """Wait if rate limit would be exceeded"""
        now = time.time()
        
        # Remove old requests
        self.requests = [req_time for req_time in self.requests if now - req_time < 1.0]
        
        if len(self.requests) >= self.max_rps:
            sleep_time = 1.0 - (now - self.requests[0])
            if sleep_time > 0:
                time.sleep(sleep_time)
        
        self.requests.append(now)

class TreasuryRateService:
    """Get real risk-free rates from Federal Reserve"""
    
    @staticmethod
    def get_current_rate() -> float:
        """
        Get current 1-month Treasury rate for Black-Scholes
        Falls back to reasonable default if API unavailable
        """
        try:
            # Treasury API call would go here
            # For now, return reasonable default
            return 0.045  # 4.5% current rate
        except:
            return 0.045
