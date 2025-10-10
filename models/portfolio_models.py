"""
ATTICUS V1 - Complete Portfolio Risk Models
Real VAR, Expected Shortfall, and risk metrics
"""
import numpy as np
import math
from typing import Dict, List
from datetime import datetime, timedelta
import random

class PortfolioRiskAnalyzer:
    """
    Professional portfolio risk analysis with real calculations
    NO FALLBACKS - Uses real market data for all calculations
    """
    
    def __init__(self, market_conditions_service):
        self.market_conditions = market_conditions_service
    
    def calculate_portfolio_var(self, portfolio: Dict, confidence_level: float = 0.05) -> Dict:
        """
        Calculate real Value at Risk using Monte Carlo simulation
        Based on actual market volatility and returns
        """
        try:
            net_btc_exposure = portfolio['net_btc_exposure']
            current_price = portfolio['current_btc_price']
            
            if net_btc_exposure == 0:
                return {
                    'var_1d_95': 0,
                    'var_1d_99': 0,
                    'expected_shortfall': 0,
                    'max_drawdown': 0,
                    'risk_level': 'minimal'
                }
            
            # Get real market conditions
            market_data = self.market_conditions.calculate_real_market_conditions(current_price)
            realized_vol = market_data['realized_volatility']
            
            # Monte Carlo simulation with real volatility
            num_simulations = 10000
            portfolio_value = abs(net_btc_exposure) * current_price
            
            # Generate price scenarios using real volatility
            price_scenarios = self._generate_price_scenarios(
                current_price, realized_vol, num_simulations
            )
            
            # Calculate P&L for each scenario
            pnl_scenarios = []
            for new_price in price_scenarios:
                pnl = net_btc_exposure * (new_price - current_price)
                pnl_scenarios.append(pnl)
            
            pnl_scenarios.sort()
            
            # Calculate VaR at different confidence levels
            var_95_index = int(confidence_level * num_simulations)
            var_99_index = int(0.01 * num_simulations)
            
            var_1d_95 = abs(pnl_scenarios[var_95_index])
            var_1d_99 = abs(pnl_scenarios[var_99_index])
            
            # Expected Shortfall (Conditional VaR)
            tail_losses = pnl_scenarios[:var_95_index]
            expected_shortfall = abs(sum(tail_losses) / len(tail_losses)) if tail_losses else 0
            
            # Maximum drawdown
            max_drawdown = abs(min(pnl_scenarios))
            
            # Risk level assessment
            var_as_percent = (var_1d_95 / portfolio_value) * 100
            risk_level = self._assess_risk_level(var_as_percent)
            
            return {
                'var_1d_95': var_1d_95,
                'var_1d_99': var_1d_99,
                'var_1d_95_percent': var_as_percent,
                'expected_shortfall': expected_shortfall,
                'max_drawdown': max_drawdown,
                'portfolio_value': portfolio_value,
                'simulations_count': num_simulations,
                'confidence_level': (1 - confidence_level) * 100,
                'risk_level': risk_level,
                'volatility_used': realized_vol,
                'calculation_method': 'Monte Carlo with Real Market Volatility'
            }
            
        except Exception as e:
            raise Exception(f"VAR calculation failed: {str(e)}")
    
    def calculate_strategy_risk_metrics(self, strategy: Dict, portfolio: Dict) -> Dict:
        """
        Calculate risk metrics specific to option strategies
        """
        try:
            strategy_greeks = strategy['pricing'].get('greeks', {})
            net_btc = portfolio['net_btc_exposure']
            current_price = portfolio['current_btc_price']
            
            # Delta risk (price sensitivity)
            delta = strategy_greeks.get('delta', 0)
            dollar_delta = delta * strategy['pricing']['contracts_needed'] * current_price
            
            # Gamma risk (delta sensitivity)  
            gamma = strategy_greeks.get('gamma', 0)
            gamma_risk = gamma * strategy['pricing']['contracts_needed'] * (current_price ** 2) * 0.01  # 1% move
            
            # Theta risk (time decay)
            theta = strategy_greeks.get('theta', 0)
            daily_theta = theta * strategy['pricing']['contracts_needed']
            
            # Vega risk (volatility sensitivity)
            vega = strategy_greeks.get('vega', 0)
            vega_risk = vega * strategy['pricing']['contracts_needed'] * 0.01  # 1% vol move
            
            # Overall strategy risk score
            total_premium = abs(strategy['pricing']['total_premium'])
            portfolio_value = abs(net_btc) * current_price
            strategy_risk_percent = (total_premium / portfolio_value) * 100
            
            return {
                'delta_exposure': dollar_delta,
                'gamma_risk': gamma_risk,
                'daily_theta': daily_theta,
                'vega_risk': vega_risk,
                'strategy_risk_percent': strategy_risk_percent,
                'risk_metrics_summary': {
                    'primary_risk': self._identify_primary_risk(delta, gamma, theta, vega),
                    'risk_level': 'low' if strategy_risk_percent < 5 else 'medium' if strategy_risk_percent < 15 else 'high'
                }
            }
            
        except Exception as e:
            raise Exception(f"Strategy risk metrics calculation failed: {str(e)}")
    
    def calculate_platform_risk_limits(self, platform_exposure: Dict) -> Dict:
        """
        Calculate platform-wide risk limits and warnings
        """
        try:
            total_exposure = platform_exposure['total_net_exposure']
            spot_exposure = platform_exposure['spot_exposure']['net_btc']
            option_exposure = platform_exposure['option_exposure']['net_delta']
            
            # Platform risk limits from config
            from config.settings import Config
            max_exposure = Config.MAX_NET_EXPOSURE_BTC
            var_limit = Config.VAR_LIMIT_PERCENT
            
            # Calculate utilization
            exposure_utilization = (abs(total_exposure) / max_exposure) * 100
            
            # Risk limit warnings
            warnings = []
            if exposure_utilization > 75:
                warnings.append(f"High exposure utilization: {exposure_utilization:.1f}%")
            
            if abs(total_exposure) > max_exposure * 0.9:
                warnings.append("Approaching maximum exposure limit")
            
            # Concentration risk
            spot_concentration = abs(spot_exposure) / abs(total_exposure) if total_exposure != 0 else 0
            option_concentration = abs(option_exposure) / abs(total_exposure) if total_exposure != 0 else 0
            
            return {
                'exposure_utilization': exposure_utilization,
                'max_exposure_btc': max_exposure,
                'current_exposure_btc': total_exposure,
                'remaining_capacity_btc': max_exposure - abs(total_exposure),
                'spot_concentration': spot_concentration,
                'option_concentration': option_concentration,
                'risk_warnings': warnings,
                'overall_risk_level': platform_exposure['risk_level']
            }
            
        except Exception as e:
            raise Exception(f"Platform risk limits calculation failed: {str(e)}")
    
    def _generate_price_scenarios(self, current_price: float, volatility: float, 
                                num_simulations: int) -> List[float]:
        """
        Generate realistic price scenarios using geometric Brownian motion
        """
        scenarios = []
        dt = 1/365  # Daily time step
        
        for _ in range(num_simulations):
            # Random walk with drift
            random_shock = random.gauss(0, 1)  # Standard normal
            
            # Geometric Brownian Motion
            price_change = current_price * (
                0 * dt + volatility * math.sqrt(dt) * random_shock  # No drift for 1-day
            )
            
            new_price = current_price + price_change
            new_price = max(new_price, current_price * 0.1)  # Floor at 10% of current price
            
            scenarios.append(new_price)
        
        return scenarios
    
    def _assess_risk_level(self, var_percent: float) -> str:
        """Assess overall risk level from VAR percentage"""
        if var_percent < 2:
            return 'low'
        elif var_percent < 5:
            return 'medium'
        elif var_percent < 10:
            return 'high'
        else:
            return 'very_high'
    
    def _identify_primary_risk(self, delta: float, gamma: float, theta: float, vega: float) -> str:
        """Identify the primary risk factor for the strategy"""
        risks = {
            'delta': abs(delta),
            'gamma': abs(gamma) * 100,  # Scale gamma
            'theta': abs(theta) * 365,  # Annualized theta
            'vega': abs(vega)
        }
        
        return max(risks.items(), key=lambda x: x[1])[0]
