"""
ATTICUS V1 - 100% REAL Market Data Service - NYC Compliant
FIXED: All volatility calculations, price validation, historical data
"""
import requests
import time
import math
from datetime import datetime, timedelta
from typing import Dict, List, Optional

class RealMarketDataService:
    """
    100% Real market data from NYC-compliant sources ONLY
    FIXED: Proper volatility calculations throughout
    """
    
    def __init__(self):
        self.cache = {}
        self.last_price_update = None
        
        # NYC-COMPLIANT EXCHANGES ONLY
        self.price_sources = [
            {
                'name': 'Coinbase',
                'url': 'https://api.coinbase.com/v2/exchange-rates?currency=BTC',
                'parser': self._parse_coinbase_price
            },
            {
                'name': 'CoinGecko', 
                'url': 'https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd',
                'parser': self._parse_coingecko_price
            },
            {
                'name': 'Kraken',
                'url': 'https://api.kraken.com/0/public/Ticker?pair=XBTUSD',
                'parser': self._parse_kraken_price
            }
        ]
    
    def get_live_btc_price(self) -> Optional[float]:
        """Get REAL BTC price from NYC-compliant exchanges with validation"""
        prices = []
        
        for source in self.price_sources:
            try:
                response = requests.get(source['url'], timeout=8)
                if response.status_code == 200:
                    price = source['parser'](response.json())
                    
                    # Validate reasonable BTC price range for Oct 2025
                    if price and 50000 <= price <= 250000:
                        prices.append(price)
                        print(f"✅ {source['name']}: ${price:,.2f}")
                    else:
                        print(f"⚠️  {source['name']}: Invalid price ${price}")
            except Exception as e:
                print(f"❌ {source['name']} failed: {e}")
                continue
        
        if not prices:
            raise Exception("NO VALID BTC PRICE - All NYC-compliant sources failed validation")
        
        # Use median price from available sources
        prices.sort()
        median_price = prices[len(prices)//2]
        
        print(f"🎯 Final BTC Price: ${median_price:,.2f} (from {len(prices)} sources)")
        
        self.last_price_update = datetime.now()
        self._cache_price(median_price)
        
        return median_price
    
    def get_real_historical_prices(self, days: int) -> List[Dict]:
        """Get REAL historical BTC prices from Coinbase Pro"""
        try:
            end_time = datetime.now()
            start_time = end_time - timedelta(days=days)
            
            # Coinbase Pro historical data (NYC compliant)
            url = "https://api.exchange.coinbase.com/products/BTC-USD/candles"
            params = {
                'start': start_time.isoformat(),
                'end': end_time.isoformat(),
                'granularity': 86400  # Daily candles
            }
            
            response = requests.get(url, params=params, timeout=15)
            
            if response.status_code != 200:
                raise Exception(f"Coinbase Pro API failed: {response.status_code}")
            
            data = response.json()
            
            if not data or len(data) < days//2:
                raise Exception(f"Insufficient historical data: got {len(data)} days")
            
            historical_prices = []
            for candle in reversed(data):  # Coinbase returns newest first
                timestamp, low, high, open_price, close, volume = candle
                historical_prices.append({
                    'timestamp': timestamp,
                    'date': datetime.fromtimestamp(timestamp),
                    'price': float(close),
                    'volume': float(volume),
                    'source': 'Coinbase Pro'
                })
            
            return historical_prices
            
        except Exception as e:
            raise Exception(f"REAL HISTORICAL DATA UNAVAILABLE: {str(e)}")
    
    def calculate_real_volatility(self, historical_prices: List[Dict]) -> float:
        """Calculate REAL volatility from actual price returns - RETURNS DECIMAL"""
        if len(historical_prices) < 10:
            raise Exception("Insufficient price data for real volatility calculation")
        
        # Calculate daily returns from real prices
        returns = []
        for i in range(1, len(historical_prices)):
            prev_price = historical_prices[i-1]['price']
            curr_price = historical_prices[i]['price']
            
            if prev_price <= 0 or curr_price <= 0:
                continue
                
            daily_return = math.log(curr_price / prev_price)  # Log returns
            returns.append(daily_return)
        
        if len(returns) < 7:
            raise Exception("Insufficient valid returns for volatility calculation")
        
        # Calculate standard deviation of returns
        mean_return = sum(returns) / len(returns)
        variance = sum((r - mean_return) ** 2 for r in returns) / (len(returns) - 1)
        
        if variance <= 0:
            raise Exception("Invalid variance calculation from real data")
        
        daily_volatility = math.sqrt(variance)
        annualized_volatility = daily_volatility * math.sqrt(365)
        
        print(f"🔢 Calculated volatility: {annualized_volatility:.4f} decimal ({annualized_volatility*100:.1f}%)")
        
        return annualized_volatility  # Returns decimal (e.g., 0.298)
    
    def get_real_market_conditions(self, current_price: float) -> Dict:
        """Calculate REAL market conditions - RETURNS DECIMAL VOLATILITY"""
        try:
            # Get real 30-day price history
            historical_prices = self.get_real_historical_prices(30)
            
            # Calculate real volatility (returns decimal)
            real_volatility = self.calculate_real_volatility(historical_prices)
            
            # Calculate real 7-day trend
            if len(historical_prices) < 7:
                raise Exception("Insufficient data for 7-day trend")
            
            week_ago_price = historical_prices[-7]['price']
            price_trend_7d = (current_price - week_ago_price) / week_ago_price
            
            # Calculate real momentum
            if len(historical_prices) >= 14:
                two_weeks_ago = historical_prices[-14]['price']
                one_week_ago = historical_prices[-7]['price']
                
                week1_change = (one_week_ago - two_weeks_ago) / two_weeks_ago
                week2_change = (current_price - one_week_ago) / one_week_ago
                
                momentum = 'accelerating' if week2_change > week1_change else 'decelerating'
            else:
                momentum = 'insufficient_data'
            
            # Real market regime assessment
            if price_trend_7d > 0.05:
                regime = 'strong_bullish'
            elif price_trend_7d > 0.02:
                regime = 'bullish' 
            elif price_trend_7d < -0.05:
                regime = 'strong_bearish'
            elif price_trend_7d < -0.02:
                regime = 'bearish'
            else:
                regime = 'neutral'
            
            return {
                'annualized_volatility': real_volatility,  # DECIMAL FORMAT (0.298)
                'price_trend_7d': price_trend_7d,
                'realized_volatility': real_volatility / math.sqrt(365),
                'market_regime': regime,
                'momentum': {'trend': momentum},
                'data_points': len(historical_prices),
                'source': 'Real Coinbase Pro Historical Data',
                'calculation_method': 'Log returns volatility (annualized)'
            }
            
        except Exception as e:
            raise Exception(f"REAL MARKET CONDITIONS UNAVAILABLE: {str(e)}")
    
    # Price parsers
    def _parse_coinbase_price(self, data: dict) -> Optional[float]:
        try:
            return float(data['data']['rates']['USD'])
        except:
            return None
    
    def _parse_coingecko_price(self, data: dict) -> Optional[float]:
        try:
            return float(data['bitcoin']['usd'])
        except:
            return None
    
    def _parse_kraken_price(self, data: dict) -> Optional[float]:
        try:
            return float(data['result']['XXBTZUSD']['c'][0])
        except:
            return None
    
    def _cache_price(self, price: float):
        self.cache['btc_price'] = {
            'price': price,
            'timestamp': time.time()
        }
