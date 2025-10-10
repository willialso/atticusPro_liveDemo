"""
ATTICUS V1 - Platform Hedging & Profitability Service
Manages net exposure and ensures platform profitability
"""
from typing import List, Dict, Tuple
from datetime import datetime, timedelta
from models.pricing_engine import BlackScholesEngine
from config.settings import Config
import numpy as np

class HedgingService:
    """
    Platform-level hedging to ensure profitability
    Manages net exposure across all clients
    """
    
    def __init__(self, market_data_service, pricing_engine):
        self.market_data = market_data_service
        self.pricing_engine = pricing_engine
        self.max_net_exposure = Config.MAX_NET_EXPOSURE_BTC
        self.hedge_threshold = Config.DELTA_HEDGE_THRESHOLD
    
    def calculate_platform_exposure(self, client_portfolios: List[Dict]) -> Dict:
        """
        Calculate total platform exposure across all clients
        Critical for profitability and risk management
        """
        total_long_btc = 0
        total_short_btc = 0
        total_option_positions = []
        
        for portfolio in client_portfolios:
            # Aggregate spot BTC positions
            total_long_btc += portfolio.get('long_btc_positions', 0)
            total_short_btc += portfolio.get('short_btc_positions', 0)
            
            # Aggregate option positions
            if 'option_positions' in portfolio:
                total_option_positions.extend(portfolio['option_positions'])
        
        net_btc_exposure = total_long_btc - total_short_btc
        
        # Calculate option Greeks exposure
        option_greeks = self.pricing_engine.calculate_portfolio_greeks(total_option_positions)
        
        # Total platform exposure including option delta
        total_net_exposure = net_btc_exposure + option_greeks['net_delta']
        
        return {
            'spot_exposure': {
                'long_btc': total_long_btc,
                'short_btc': total_short_btc,
                'net_btc': net_btc_exposure
            },
            'option_exposure': option_greeks,
            'total_net_exposure': total_net_exposure,
            'exposure_percentage': (abs(total_net_exposure) / self.max_net_exposure) * 100,
            'hedge_required': abs(total_net_exposure) > Config.MAX_NET_EXPOSURE_BTC * 0.1,
            'risk_level': self._assess_risk_level(total_net_exposure)
        }
    
    def generate_hedge_strategy(self, platform_exposure: Dict) -> Dict:
        """
        Generate optimal hedge strategy for platform profitability
        Uses real Deribit options for actual executable hedges
        """
        net_exposure = platform_exposure['total_net_exposure']
        
        if abs(net_exposure) < Config.MIN_HEDGE_SIZE:
            return {'hedge_needed': False, 'reason': 'Exposure below minimum threshold'}
        
        current_price = self.market_data.get_live_btc_price()
        available_options = self.market_data.get_available_options()
        
        if net_exposure > 0:  # Platform is net long - need downside protection
            hedge_strategy = self._find_optimal_puts(
                exposure=net_exposure, 
                current_price=current_price,
                available_options=available_options
            )
        else:  # Platform is net short - need upside protection
            hedge_strategy = self._find_optimal_calls(
                exposure=abs(net_exposure),
                current_price=current_price, 
                available_options=available_options
            )
        
        # Add profitability analysis
        hedge_strategy['profitability_analysis'] = self._analyze_hedge_profitability(
            hedge_strategy, platform_exposure
        )
        
        return hedge_strategy
    
    def _find_optimal_puts(self, exposure: float, current_price: float, 
                          available_options: List[Dict]) -> Dict:
        """
        Find optimal put options for hedging long exposure
        Prioritizes cost-effectiveness and liquidity
        """
        suitable_puts = []
        
        # Filter for put options
        for option in available_options:
            if (option['option_type'].lower() == 'put' and
                option['days_to_expiry'] >= 7 and
                option['days_to_expiry'] <= 30 and
                option['strike'] >= current_price * 0.85 and  # Not too far OTM
                option['strike'] <= current_price * 0.98):    # Not too far ITM
                
                # Calculate hedge effectiveness
                strike = option['strike']
                time_to_expiry = option['days_to_expiry'] / 365.0
                
                # Get IV from market data
                iv_surface = self.market_data.get_implied_volatility_surface()
                surface_key = (strike, datetime.now() + timedelta(days=option['days_to_expiry']), 'put')
                
                if surface_key in iv_surface:
                    iv_data = iv_surface[surface_key]
                    implied_vol = iv_data['implied_volatility']
                    
                    # Calculate theoretical price and Greeks
                    pricing = self.pricing_engine.calculate_option_price(
                        spot_price=current_price,
                        strike_price=strike,
                        time_to_expiry=time_to_expiry,
                        implied_volatility=implied_vol,
                        option_type='put'
                    )
                    
                    # Calculate hedge ratio and cost
                    contracts_needed = exposure / abs(pricing['greeks']['delta'])
                    total_cost = contracts_needed * pricing['platform_price']
                    hedge_effectiveness = abs(pricing['greeks']['delta'])
                    
                    suitable_puts.append({
                        'option': option,
                        'pricing': pricing,
                        'contracts_needed': contracts_needed,
                        'total_cost': total_cost,
                        'hedge_effectiveness': hedge_effectiveness,
                        'cost_per_btc_hedged': total_cost / exposure,
                        'breakeven_decline': (pricing['platform_price'] / current_price) * 100
                    })
        
        if not suitable_puts:
            return {'hedge_available': False, 'reason': 'No suitable put options found'}
        
        # Sort by cost-effectiveness (best hedge effectiveness per dollar)
        suitable_puts.sort(key=lambda x: x['cost_per_btc_hedged'])
        
        optimal_hedge = suitable_puts[0]
        
        return {
            'hedge_available': True,
            'hedge_type': 'protective_puts',
            'recommended_option': optimal_hedge['option'],
            'contracts_needed': optimal_hedge['contracts_needed'],
            'total_cost': optimal_hedge['total_cost'],
            'hedge_ratio': optimal_hedge['hedge_effectiveness'],
            'cost_analysis': {
                'cost_per_btc': optimal_hedge['cost_per_btc_hedged'],
                'cost_percentage': (optimal_hedge['total_cost'] / (exposure * current_price)) * 100,
                'breakeven_decline_percent': optimal_hedge['breakeven_decline']
            },
            'alternatives': suitable_puts[1:3]  # Show alternatives
        }
    
    def _find_optimal_calls(self, exposure: float, current_price: float,
                           available_options: List[Dict]) -> Dict:
        """
        Find optimal call options for hedging short exposure
        Similar logic to puts but for upside protection
        """
        # Similar implementation to puts but for calls
        # Filters for call options with appropriate strikes and expires
        # Returns optimal call hedge strategy
        
        suitable_calls = []
        
        for option in available_options:
            if (option['option_type'].lower() == 'call' and
                option['days_to_expiry'] >= 7 and
                option['days_to_expiry'] <= 30 and
                option['strike'] >= current_price * 1.02 and  # Slightly OTM
                option['strike'] <= current_price * 1.15):    # Not too far OTM
                
                # Calculate call hedge (similar to puts logic)
                strike = option['strike']
                time_to_expiry = option['days_to_expiry'] / 365.0
                
                # Get IV and calculate pricing
                iv_surface = self.market_data.get_implied_volatility_surface()
                surface_key = (strike, datetime.now() + timedelta(days=option['days_to_expiry']), 'call')
                
                if surface_key in iv_surface:
                    iv_data = iv_surface[surface_key]
                    implied_vol = iv_data['implied_volatility']
                    
                    pricing = self.pricing_engine.calculate_option_price(
                        spot_price=current_price,
                        strike_price=strike, 
                        time_to_expiry=time_to_expiry,
                        implied_volatility=implied_vol,
                        option_type='call'
                    )
                    
                    contracts_needed = exposure / abs(pricing['greeks']['delta'])
                    total_cost = contracts_needed * pricing['platform_price']
                    
                    suitable_calls.append({
                        'option': option,
                        'pricing': pricing,
                        'contracts_needed': contracts_needed,
                        'total_cost': total_cost,
                        'hedge_effectiveness': abs(pricing['greeks']['delta']),
                        'cost_per_btc_hedged': total_cost / exposure
                    })
        
        if not suitable_calls:
            return {'hedge_available': False, 'reason': 'No suitable call options found'}
        
        suitable_calls.sort(key=lambda x: x['cost_per_btc_hedged'])
        optimal_hedge = suitable_calls[0]
        
        return {
            'hedge_available': True,
            'hedge_type': 'protective_calls',
            'recommended_option': optimal_hedge['option'],
            'contracts_needed': optimal_hedge['contracts_needed'],
            'total_cost': optimal_hedge['total_cost'],
            'hedge_ratio': optimal_hedge['hedge_effectiveness'],
            'alternatives': suitable_calls[1:3]
        }
    
    def _analyze_hedge_profitability(self, hedge_strategy: Dict, platform_exposure: Dict) -> Dict:
        """
        Analyze if hedge maintains platform profitability
        Critical business logic for sustainable operations
        """
        if not hedge_strategy.get('hedge_available'):
            return {'profitable': True, 'reason': 'No hedge needed'}
        
        hedge_cost = hedge_strategy['total_cost']
        exposure_value = abs(platform_exposure['total_net_exposure']) * self.market_data.get_live_btc_price()
        
        # Calculate cost as percentage of exposure
        hedge_cost_percentage = (hedge_cost / exposure_value) * 100
        
        # Platform profitability thresholds
        max_hedge_cost_percentage = 5.0  # Max 5% of exposure value for hedging
        
        profitable = hedge_cost_percentage <= max_hedge_cost_percentage
        
        # Calculate expected P&L scenarios with hedge
        scenarios = self._calculate_hedge_scenarios(hedge_strategy, platform_exposure)
        
        return {
            'profitable': profitable,
            'hedge_cost_percentage': hedge_cost_percentage,
            'max_acceptable_cost': max_hedge_cost_percentage,
            'expected_scenarios': scenarios,
            'recommendation': 'execute' if profitable else 'review_alternatives'
        }
    
    def _calculate_hedge_scenarios(self, hedge_strategy: Dict, platform_exposure: Dict) -> List[Dict]:
        """Calculate P&L under different market scenarios with hedge"""
        current_price = self.market_data.get_live_btc_price()
        scenarios = []
        
        # Test scenarios: -30%, -15%, 0%, +15%, +30%
        price_changes = [-0.30, -0.15, 0.00, 0.15, 0.30]
        
        for change in price_changes:
            new_price = current_price * (1 + change)
            
            # Calculate unhedged P&L
            spot_pnl = platform_exposure['total_net_exposure'] * (new_price - current_price)
            
            # Calculate hedge P&L (simplified)
            if hedge_strategy['hedge_type'] == 'protective_puts':
                hedge_pnl = self._calculate_put_pnl(hedge_strategy, current_price, new_price)
            else:
                hedge_pnl = self._calculate_call_pnl(hedge_strategy, current_price, new_price)
            
            total_pnl = spot_pnl + hedge_pnl - hedge_strategy['total_cost']
            
            scenarios.append({
                'price_change_percent': change * 100,
                'new_price': new_price,
                'spot_pnl': spot_pnl,
                'hedge_pnl': hedge_pnl,
                'total_pnl': total_pnl
            })
        
        return scenarios
    
    def _calculate_put_pnl(self, hedge_strategy: Dict, old_price: float, new_price: float) -> float:
        """Simplified put P&L calculation"""
        strike = hedge_strategy['recommended_option']['strike']
        contracts = hedge_strategy['contracts_needed']
        
        # Simplified: only intrinsic value change
        old_intrinsic = max(0, strike - old_price)
        new_intrinsic = max(0, strike - new_price)
        
        return contracts * (new_intrinsic - old_intrinsic)
    
    def _calculate_call_pnl(self, hedge_strategy: Dict, old_price: float, new_price: float) -> float:
        """Simplified call P&L calculation"""
        strike = hedge_strategy['recommended_option']['strike']  
        contracts = hedge_strategy['contracts_needed']
        
        old_intrinsic = max(0, old_price - strike)
        new_intrinsic = max(0, new_price - strike)
        
        return contracts * (new_intrinsic - old_intrinsic)
    
    def _assess_risk_level(self, net_exposure: float) -> str:
        """Assess platform risk level based on exposure"""
        exposure_ratio = abs(net_exposure) / self.max_net_exposure
        
        if exposure_ratio < 0.25:
            return 'low'
        elif exposure_ratio < 0.50:
            return 'medium'
        elif exposure_ratio < 0.75:
            return 'high'
        else:
            return 'critical'

class PlatformPnLCalculator:
    """
    Calculate platform P&L from client strategies
    Ensures sustainable business model
    """
    
    def __init__(self):
        self.markup_rate = Config.OPTION_MARKUP_RATE
    
    def calculate_daily_pnl(self, client_transactions: List[Dict], market_data: Dict) -> Dict:
        """
        Calculate platform daily P&L from all sources
        """
        # Revenue from markups on client transactions
        markup_revenue = sum(
            tx['premium_amount'] * self.markup_rate 
            for tx in client_transactions 
            if tx['type'] == 'option_purchase'
        )
        
        # Hedging costs
        hedging_costs = sum(
            tx['amount'] 
            for tx in client_transactions 
            if tx['type'] == 'platform_hedge'
        )
        
        # Net P&L
        net_pnl = markup_revenue - hedging_costs
        
        return {
            'markup_revenue': markup_revenue,
            'hedging_costs': hedging_costs,
            'net_pnl': net_pnl,
            'profit_margin': (net_pnl / markup_revenue * 100) if markup_revenue > 0 else 0
        }
