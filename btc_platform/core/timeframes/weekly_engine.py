"""
Weekly BTC Options Engine
Primary institutional timeframe focus
"""
import logging
from datetime import datetime, timezone
from typing import Dict, List
import math

from ..core.exchanges.coinbase_client import CoinbaseClient
from ..core.exchanges.deribit_client import DeribitsClient
from .config.settings import PLATFORM_CONFIG

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WeeklyOptionsEngine:
    """Weekly options engine optimized for institutional clients"""
    
    def __init__(self):
        self.coinbase = CoinbaseClient()
        self.deribit = DeribitsClient()
        self.current_btc_price = 0.0
        self.weekly_options = []
        
        self._update_market_data()
    
    def _update_market_data(self):
        """Update current market data"""
        self.current_btc_price = self.coinbase.get_current_btc_price()
        self.weekly_options = self.deribit.get_weekly_btc_options()
        logger.info(f"📊 Market data updated: BTC ${self.current_btc_price:,.2f}")
    
    def calculate_weekly_protection_cost(self, btc_size: float, target_days: int) -> Dict:
        """Calculate weekly protection cost with institutional focus"""
        
        if btc_size < PLATFORM_CONFIG['min_position_size']:
            return {
                'success': False, 
                'reason': f'Minimum position size: {PLATFORM_CONFIG["min_position_size"]} BTC'
            }
        
        position_value = btc_size * self.current_btc_price
        
        # Weekly cost structure (more efficient than same-day)
        weekly_cost_factors = {
            1: 0.018,  # Monday (high time decay)
            2: 0.014,  # Tuesday  
            3: 0.011,  # Wednesday
            4: 0.009,  # Thursday
            5: 0.008,  # Weekly (Friday, most efficient)
        }
        
        # Use closest available expiry
        available_days = [opt['days_to_expiry'] for opt in self.weekly_options if opt['option_type'] == 'P']
        if not available_days:
            return {'success': False, 'reason': 'No weekly put options available'}
        
        closest_days = min(available_days, key=lambda x: abs(x - target_days))
        base_cost_pct = weekly_cost_factors.get(closest_days, 0.010)
        
        # Market factors
        volatility_factor = self._get_volatility_factor()
        liquidity_discount = 0.90  # Weekly options more liquid = 10% discount
        size_discount = min(0.95, 0.98 - (btc_size / 100) * 0.02)  # Larger size = better pricing
        
        # Option premium calculation
        option_premium = position_value * base_cost_pct * volatility_factor * liquidity_discount * size_discount
        
        # NYC-compliant hedge cost
        hedge_cost = self._calculate_hedge_cost(btc_size, closest_days)
        
        total_cost = option_premium + hedge_cost
        
        # Platform markup
        markup = PLATFORM_CONFIG['default_markup']
        client_premium = total_cost * (1 + markup)
        platform_profit = client_premium - total_cost
        
        # Find best option for this strategy
        best_option = self._find_best_weekly_option(closest_days)
        
        return {
            'success': True,
            'strategy_type': 'weekly_protection',
            'position_details': {
                'btc_size': btc_size,
                'position_value': position_value,
                'current_btc_price': self.current_btc_price
            },
            'timing': {
                'target_days': target_days,
                'actual_days': closest_days,
                'expiry_type': 'weekly_friday'
            },
            'option_details': best_option,
            'cost_breakdown': {
                'option_premium': option_premium,
                'hedge_cost': hedge_cost,
                'total_cost': total_cost,
                'platform_markup_pct': markup * 100,
                'client_premium': client_premium,
                'platform_profit': platform_profit,
                'cost_as_pct_of_position': (client_premium / position_value) * 100
            },
            'market_factors': {
                'volatility_factor': volatility_factor,
                'liquidity_discount': liquidity_discount,
                'size_discount': size_discount,
                'base_cost_pct': base_cost_pct * 100
            }
        }
    
    def _find_best_weekly_option(self, days_to_expiry: int) -> Dict:
        """Find best weekly option for protection"""
        target_strike = self.current_btc_price * 0.95  # 95% protection
        
        best_option = None
        best_score = 0
        
        for option in self.weekly_options:
            if (option['days_to_expiry'] == days_to_expiry and 
                option['option_type'] == 'P'):
                
                # Score based on strike proximity and spread
                strike_score = 1 - abs(option['strike_price'] - target_strike) / target_strike
                spread_score = 1 - (option['spread_pct'] / 100)
                volume_score = min(1.0, option['volume'] / 1.0)  # Normalize volume
                
                total_score = (strike_score * 0.5) + (spread_score * 0.3) + (volume_score * 0.2)
                
                if total_score > best_score:
                    best_score = total_score
                    best_option = option
        
        return best_option or {}
    
    def _get_volatility_factor(self) -> float:
        """Get current BTC volatility factor"""
        # Simplified volatility factor (can enhance with real IV later)
        return 1.1  # 10% premium for current market conditions
    
    def _calculate_hedge_cost(self, btc_size: float, days: int) -> float:
        """Calculate NYC-compliant hedge cost"""
        # Use Coinbase for hedging (futures when available, or simulate cost)
        daily_cost_pct = 0.0002  # 0.02% daily hedge cost
        return btc_size * self.current_btc_price * daily_cost_pct * days
    
    def get_weekly_strategy_menu(self, btc_size: float) -> List[Dict]:
        """Get menu of weekly protection options"""
        strategies = []
        
        for days in [1, 2, 3, 5]:  # Monday through Friday
            strategy = self.calculate_weekly_protection_cost(btc_size, days)
            if strategy['success']:
                strategies.append({
                    'days_to_expiry': days,
                    'expiry_day': ['Monday', 'Tuesday', 'Wednesday', 'Friday'][days-1] if days <= 4 else 'Friday',
                    'premium': strategy['cost_breakdown']['client_premium'],
                    'premium_pct': strategy['cost_breakdown']['cost_as_pct_of_position'],
                    'platform_profit': strategy['cost_breakdown']['platform_profit'],
                    'description': self._get_strategy_description(days)
                })
        
        return sorted(strategies, key=lambda x: x['premium_pct'])
    
    def _get_strategy_description(self, days: int) -> str:
        """Get description for strategy"""
        descriptions = {
            1: 'Urgent protection until tomorrow',
            2: 'Short-term protection (2 days)',
            3: 'Mid-week protection (3 days)', 
            5: 'Full weekly protection (most efficient)'
        }
        return descriptions.get(days, f'{days}-day protection')
