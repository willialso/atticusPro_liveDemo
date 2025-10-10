"""
ATTICUS V1 - Real Market Conditions Calculator
100% Real calculations from historical price data
"""
import requests
import numpy as np
import math
from datetime import datetime, timedelta
from typing import List, Dict

class MarketConditionsService:
    """
    Real market conditions calculated from actual BTC price history
    NO HARDCODED VALUES - All calculations from real data
    """
    
    def __init__(self, deribit_service):
        self.deribit = deribit_service
    
    def calculate_real_market_conditions(self, current_price: float) -> Dict:
        """
        Calculate real market conditions from actual price data
        NO FALLBACKS - Raises exception if real data unavailable
        """
        try:
            # Get real 30-day price history from Deribit
            historical_prices = self._get_real_price_history(30)
            
            if len(historical_prices) < 7:
                raise Exception("Insufficient historical price data for market conditions")
            
            # Calculate real 7-day price trend
            week_ago_price = historical_prices[-7]['price']  # 7 days ago
            price_trend_7d = (current_price - week_ago_price) / week_ago_price
            
            # Calculate real realized volatility from returns
            returns = self._calculate_real_returns(historical_prices)
            realized_volatility = self._calculate_real_volatility(returns)
            
            # Calculate real market regime from price action
            market_regime = self._determine_real_market_regime(returns, price_trend_7d)
            
            # Calculate real momentum indicators
            momentum_data = self._calculate_real_momentum(historical_prices, current_price)
            
            return {
                'price_trend_7d': price_trend_7d,
                'realized_volatility': realized_volatility,
                'annualized_volatility': realized_volatility * math.sqrt(365),
                'market_regime': market_regime,
                'momentum': momentum_data,
                'data_points': len(historical_prices),
                'last_updated': datetime.now().isoformat(),
                'source': 'Real Deribit Historical Data'
            }
            
        except Exception as e:
            raise Exception(f"Unable to calculate real market conditions: {str(e)}")
    
    def _get_real_price_history(self, days: int) -> List[Dict]:
        """
        Get real historical BTC prices from Deribit
        """
        try:
            # Deribit historical data API
            end_timestamp = int(datetime.now().timestamp() * 1000)
            start_timestamp = int((datetime.now() - timedelta(days=days)).timestamp() * 1000)
            
            url = f"{self.deribit.base_url}/public/get_tradingview_chart_data"
            params = {
                'instrument_name': 'BTC-PERPETUAL',
                'start_timestamp': start_timestamp,
                'end_timestamp': end_timestamp,
                'resolution': '1D'  # Daily data
            }
            
            response = requests.get(url, params=params, timeout=15)
            
            if response.status_code != 200:
                raise Exception(f"Deribit historical data API error: {response.status_code}")
            
            data = response.json()
            
            if 'result' not in data:
                raise Exception("No historical data in Deribit response")
            
            result = data['result']
            
            # Convert to price history format
            historical_prices = []
            
            if (result.get('t') and result.get('c')):  # timestamps and close prices
                timestamps = result['t']
                close_prices = result['c']
                
                for i, timestamp in enumerate(timestamps):
                    if i < len(close_prices):
                        historical_prices.append({
                            'timestamp': timestamp,
                            'date': datetime.fromtimestamp(timestamp / 1000),
                            'price': float(close_prices[i])
                        })
            
            if len(historical_prices) < days // 2:  # At least half the requested days
                raise Exception(f"Insufficient historical data: got {len(historical_prices)} days")
            
            return sorted(historical_prices, key=lambda x: x['timestamp'])
            
        except Exception as e:
            raise Exception(f"Failed to get real historical prices: {str(e)}")
    
    def _calculate_real_returns(self, price_history: List[Dict]) -> List[float]:
        """Calculate real log returns from price history"""
        if len(price_history) < 2:
            raise Exception("Insufficient price data for return calculation")
        
        returns = []
        for i in range(1, len(price_history)):
            prev_price = price_history[i-1]['price']
            curr_price = price_history[i]['price']
            
            if prev_price <= 0 or curr_price <= 0:
                raise Exception(f"Invalid price data: {prev_price} -> {curr_price}")
            
            log_return = math.log(curr_price / prev_price)
            returns.append(log_return)
        
        return returns
    
    def _calculate_real_volatility(self, returns: List[float]) -> float:
        """Calculate real volatility from returns"""
        if len(returns) < 2:
            raise Exception("Insufficient returns for volatility calculation")
        
        mean_return = sum(returns) / len(returns)
        variance = sum((r - mean_return) ** 2 for r in returns) / (len(returns) - 1)
        
        if variance < 0:
            raise Exception("Negative variance in volatility calculation")
        
        daily_volatility = math.sqrt(variance)
        return daily_volatility
    
    def _determine_real_market_regime(self, returns: List[float], price_trend_7d: float) -> str:
        """
        Determine market regime from real price action
        """
        # Calculate trend strength
        positive_returns = sum(1 for r in returns[-7:] if r > 0)  # Last 7 days
        total_recent_returns = len(returns[-7:])
        
        trend_strength = positive_returns / total_recent_returns if total_recent_returns > 0 else 0.5
        
        # Calculate volatility regime
        recent_vol = self._calculate_real_volatility(returns[-7:]) if len(returns) >= 7 else 0
        overall_vol = self._calculate_real_volatility(returns)
        vol_ratio = recent_vol / overall_vol if overall_vol > 0 else 1
        
        # Determine regime based on real metrics
        if price_trend_7d > 0.05 and trend_strength > 0.6:
            return 'strong_bullish'
        elif price_trend_7d > 0.02 and trend_strength > 0.5:
            return 'bullish'
        elif price_trend_7d < -0.05 and trend_strength < 0.4:
            return 'strong_bearish'
        elif price_trend_7d < -0.02 and trend_strength < 0.5:
            return 'bearish'
        elif vol_ratio > 1.5:
            return 'high_volatility'
        else:
            return 'neutral'
    
    def _calculate_real_momentum(self, price_history: List[Dict], current_price: float) -> Dict:
        """Calculate real momentum indicators"""
        if len(price_history) < 5:
            return {'momentum': 'insufficient_data'}
        
        # Simple momentum: current vs 5-day average
        recent_prices = [p['price'] for p in price_history[-5:]]
        avg_5day = sum(recent_prices) / len(recent_prices)
        
        momentum = (current_price - avg_5day) / avg_5day
        
        # Price acceleration (second derivative)
        if len(price_history) >= 3:
            p1 = price_history[-3]['price']
            p2 = price_history[-2]['price'] 
            p3 = price_history[-1]['price']
            
            acceleration = (p3 - p2) - (p2 - p1)
            acceleration_percent = (acceleration / p2) * 100
        else:
            acceleration_percent = 0
        
        return {
            'momentum_5d': momentum,
            'acceleration': acceleration_percent,
            'trend': 'positive' if momentum > 0.01 else 'negative' if momentum < -0.01 else 'flat'
        }
