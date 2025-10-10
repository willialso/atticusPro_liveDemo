"""
ATTICUS V1 - INSTITUTIONAL PLATFORM HEDGING SERVICE
Complete real-time delta hedging, risk management, P&L attribution
"""
import requests
from datetime import datetime
from typing import Dict, List
import math

class PlatformHedgingService:
    """
    Professional institutional hedging service
    """
    
    def __init__(self, deribit_credentials=None):
        self.deribit_credentials = deribit_credentials
        self.active_positions = {}
        self.hedge_positions = {}
        self.risk_limits = {
            'max_delta_exposure_btc': 5.0,
            'max_vega_exposure': 1000,
            'max_gamma_exposure': 0.1,
            'hedge_trigger_threshold': 0.1,
            'max_portfolio_var': 50000,
            'max_theta_decay_daily': 1000
        }
        
    def calculate_platform_exposure(self, executed_strategies: List[Dict]) -> Dict:
        """Calculate platform's net risk exposure from all client trades"""
        try:
            total_delta = 0
            total_gamma = 0  
            total_vega = 0
            total_theta = 0
            total_rho = 0
            
            position_details = []
            total_notional = 0
            
            for strategy in executed_strategies:
                pricing = strategy.get('pricing', {})
                contracts = pricing.get('contracts_needed', 0)
                greeks = pricing.get('greeks', {})
                
                # Platform has OPPOSITE exposure to client positions
                strategy_name = strategy.get('strategy_name', '')
                
                if strategy_name == 'protective_put':
                    # Client bought put, platform sold put (short put position)
                    platform_delta = -abs(greeks.get('delta', -0.25)) * contracts
                    platform_gamma = -abs(greeks.get('gamma', 0.003)) * contracts
                    platform_vega = -abs(greeks.get('vega', 45)) * contracts
                    platform_theta = abs(greeks.get('theta', -15)) * contracts  # Platform gains theta
                    platform_rho = -greeks.get('rho', 20) * contracts
                    
                elif strategy_name == 'covered_call':
                    # Client sold call, platform bought call (long call position)
                    platform_delta = abs(greeks.get('delta', 0.17)) * contracts
                    platform_gamma = abs(greeks.get('gamma', 0.002)) * contracts
                    platform_vega = abs(greeks.get('vega', 96)) * contracts
                    platform_theta = greeks.get('theta', -43) * contracts  # Platform loses theta
                    platform_rho = greeks.get('rho', 19) * contracts
                    
                elif strategy_name == 'cash_secured_put':
                    # Client sold put, platform bought put (long put position)
                    platform_delta = greeks.get('delta', -0.25) * contracts
                    platform_gamma = abs(greeks.get('gamma', 0.003)) * contracts
                    platform_vega = abs(greeks.get('vega', 109)) * contracts
                    platform_theta = greeks.get('theta', -50) * contracts
                    platform_rho = greeks.get('rho', -25) * contracts
                    
                elif strategy_name == 'short_strangle':
                    # Complex position - net long options
                    platform_delta = 0  # Roughly neutral
                    platform_gamma = abs(greeks.get('gamma', 0.005)) * contracts * 2  # Two legs
                    platform_vega = abs(greeks.get('vega', 150)) * contracts
                    platform_theta = greeks.get('theta', -70) * contracts
                    platform_rho = 0
                    
                elif strategy_name == 'put_spread':
                    # Net short put spread
                    platform_delta = -abs(greeks.get('delta', -0.15)) * contracts
                    platform_gamma = -abs(greeks.get('gamma', 0.002)) * contracts
                    platform_vega = -abs(greeks.get('vega', 60)) * contracts
                    platform_theta = abs(greeks.get('theta', 25)) * contracts
                    platform_rho = greeks.get('rho', 15) * contracts
                    
                else:
                    platform_delta = 0
                    platform_gamma = 0
                    platform_vega = 0
                    platform_theta = 0
                    platform_rho = 0
                
                total_delta += platform_delta
                total_gamma += platform_gamma
                total_vega += platform_vega
                total_theta += platform_theta
                total_rho += platform_rho
                
                notional = abs(pricing.get('total_premium', 0))
                total_notional += notional
                
                position_details.append({
                    'strategy': strategy_name,
                    'contracts': contracts,
                    'platform_delta': platform_delta,
                    'platform_gamma': platform_gamma,
                    'platform_vega': platform_vega,
                    'platform_theta': platform_theta,
                    'premium_volume': notional,
                    'client_position': self._get_client_position_description(strategy_name),
                    'platform_risk': self._get_platform_risk_description(strategy_name)
                })
            
            return {
                'total_delta_exposure': total_delta,
                'total_gamma_exposure': total_gamma,
                'total_vega_exposure': total_vega,
                'total_theta_exposure': total_theta,
                'total_rho_exposure': total_rho,
                'total_notional': total_notional,
                'position_count': len(executed_strategies),
                'position_details': position_details,
                'hedge_required': abs(total_delta) > self.risk_limits['hedge_trigger_threshold'],
                'hedge_amount_btc': -total_delta,
                'risk_assessment': self._assess_risk_level(total_delta, total_vega, total_gamma),
                'daily_theta_pnl': total_theta,
                'calculation_timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            raise Exception(f"Platform exposure calculation failed: {str(e)}")
    
    def generate_hedge_recommendations(self, exposure_data: Dict, current_btc_price: float) -> Dict:
        """Generate specific institutional hedging recommendations"""
        try:
            hedge_amount = exposure_data['hedge_amount_btc']
            vega_exposure = exposure_data['total_vega_exposure']
            gamma_exposure = exposure_data['total_gamma_exposure']
            
            if abs(hedge_amount) < self.risk_limits['hedge_trigger_threshold']:
                return {
                    'hedge_required': False,
                    'recommendation': 'No hedging required - within risk limits',
                    'risk_level': 'LOW',
                    'current_exposure': exposure_data
                }
            
            hedge_strategies = []
            estimated_total_cost = 0
            
            # Primary Delta Hedge: BTC Perpetual Futures
            if abs(hedge_amount) > 0.05:
                futures_cost = abs(hedge_amount) * current_btc_price * 0.0005
                estimated_total_cost += futures_cost
                
                hedge_strategies.append({
                    'hedge_type': 'PRIMARY_DELTA_HEDGE',
                    'instrument': 'BTC Perpetual Futures',
                    'venue': 'Deribit',
                    'action': 'Buy' if hedge_amount > 0 else 'Sell',
                    'amount_btc': abs(hedge_amount),
                    'notional_usd': abs(hedge_amount) * current_btc_price,
                    'estimated_cost': futures_cost,
                    'effectiveness': 'HIGH - Direct delta neutralization',
                    'execution_priority': 1,
                    'time_sensitivity': 'IMMEDIATE' if abs(hedge_amount) > 1.0 else 'HIGH'
                })
            
            # Vega Hedge: Options-based
            if abs(vega_exposure) > 100:
                vega_hedge_cost = abs(vega_exposure) * 0.008  # $8 per vega point
                estimated_total_cost += vega_hedge_cost
                
                hedge_strategies.append({
                    'hedge_type': 'VEGA_HEDGE',
                    'instrument': 'BTC Options (offsetting)',
                    'venue': 'Deribit',
                    'action': 'Buy options with opposite vega exposure',
                    'vega_amount': -vega_exposure,
                    'estimated_cost': vega_hedge_cost,
                    'effectiveness': 'MEDIUM - Volatility risk reduction',
                    'execution_priority': 2,
                    'time_sensitivity': 'MEDIUM'
                })
            
            # Gamma Hedge: Dynamic hedging plan
            if abs(gamma_exposure) > 0.05:
                hedge_strategies.append({
                    'hedge_type': 'GAMMA_HEDGE',
                    'instrument': 'Dynamic Delta Hedging',
                    'venue': 'Deribit',
                    'action': 'Continuous rebalancing as BTC price moves',
                    'gamma_amount': gamma_exposure,
                    'estimated_cost': abs(gamma_exposure) * current_btc_price * 100 * 0.001,  # Trading costs
                    'effectiveness': 'HIGH - Second-order risk management',
                    'execution_priority': 3,
                    'time_sensitivity': 'ONGOING',
                    'rebalance_threshold': '$500 BTC price move'
                })
            
            # Risk assessment
            urgency = 'CRITICAL' if abs(hedge_amount) > 2.0 else 'HIGH' if abs(hedge_amount) > 0.5 else 'MEDIUM'
            
            return {
                'hedge_required': True,
                'hedge_strategies': hedge_strategies,
                'primary_recommendation': hedge_strategies[0] if hedge_strategies else None,
                'urgency': urgency,
                'estimated_total_cost': estimated_total_cost,
                'cost_as_pct_of_notional': (estimated_total_cost / exposure_data['total_notional']) * 100,
                'risk_reduction_benefit': f'Eliminates ${abs(hedge_amount * current_btc_price * 0.05):,.0f} daily VAR',
                'execution_timeframe': 'Within 15 minutes' if urgency == 'CRITICAL' else 'Within 1 hour',
                'monitoring_requirements': {
                    'delta_rebalance_threshold': 0.1,
                    'price_monitoring_interval': '5 minutes',
                    'risk_reporting_frequency': 'Real-time'
                }
            }
            
        except Exception as e:
            raise Exception(f"Hedge recommendation failed: {str(e)}")
    
    def calculate_platform_pnl_scenarios(self, exposure_data: Dict, current_btc_price: float) -> Dict:
        """Calculate platform P&L under different BTC price scenarios"""
        try:
            delta = exposure_data['total_delta_exposure']
            gamma = exposure_data['total_gamma_exposure']
            vega = exposure_data['total_vega_exposure']
            theta = exposure_data['total_theta_exposure']
            
            # BTC price scenarios
            price_scenarios = [
                {'label': 'Flash Crash', 'price_change': -10000, 'vol_change': 0.3},
                {'label': 'Large Drop', 'price_change': -5000, 'vol_change': 0.15},
                {'label': 'Moderate Drop', 'price_change': -2000, 'vol_change': 0.05},
                {'label': 'Small Drop', 'price_change': -500, 'vol_change': 0.02},
                {'label': 'No Change', 'price_change': 0, 'vol_change': 0},
                {'label': 'Small Rise', 'price_change': 500, 'vol_change': 0.02},
                {'label': 'Moderate Rise', 'price_change': 2000, 'vol_change': 0.05},
                {'label': 'Large Rise', 'price_change': 5000, 'vol_change': 0.15},
                {'label': 'Moon Shot', 'price_change': 10000, 'vol_change': 0.25}
            ]
            
            scenario_results = []
            
            for scenario in price_scenarios:
                price_change = scenario['price_change']
                vol_change = scenario['vol_change']
                
                # First-order (delta) P&L
                delta_pnl = delta * price_change
                
                # Second-order (gamma) P&L
                gamma_pnl = 0.5 * gamma * (price_change ** 2)
                
                # Volatility (vega) P&L
                vega_pnl = vega * vol_change
                
                # Time decay (theta) P&L - daily
                theta_pnl = theta
                
                # Total unhedged P&L
                total_unhedged_pnl = delta_pnl + gamma_pnl + vega_pnl + theta_pnl
                
                # Hedged P&L (delta-neutral)
                hedged_delta_pnl = 0  # Delta hedged
                total_hedged_pnl = hedged_delta_pnl + gamma_pnl + vega_pnl + theta_pnl
                
                # Hedging costs
                hedge_amount = abs(delta)
                hedging_cost = hedge_amount * current_btc_price * 0.0005 if hedge_amount > 0.1 else 0
                
                net_hedged_pnl = total_hedged_pnl - hedging_cost
                
                scenario_results.append({
                    'scenario': scenario['label'],
                    'btc_price': current_btc_price + price_change,
                    'price_change': price_change,
                    'vol_change_pct': vol_change * 100,
                    'unhedged_pnl': total_unhedged_pnl,
                    'hedged_pnl': total_hedged_pnl,
                    'hedging_cost': hedging_cost,
                    'net_hedged_pnl': net_hedged_pnl,
                    'pnl_components': {
                        'delta_pnl': delta_pnl,
                        'gamma_pnl': gamma_pnl,
                        'vega_pnl': vega_pnl,
                        'theta_pnl': theta_pnl
                    },
                    'hedge_effectiveness': abs(net_hedged_pnl) < abs(total_unhedged_pnl) * 0.3
                })
            
            # Risk metrics
            worst_unhedged = min(s['unhedged_pnl'] for s in scenario_results)
            worst_hedged = min(s['net_hedged_pnl'] for s in scenario_results)
            
            return {
                'scenario_analysis': scenario_results,
                'risk_summary': {
                    'worst_case_unhedged': worst_unhedged,
                    'worst_case_hedged': worst_hedged,
                    'max_risk_reduction': worst_unhedged - worst_hedged,
                    'daily_theta_income': theta,
                    'breakeven_hedge_days': hedging_cost / abs(theta) if theta != 0 else float('inf')
                },
                'recommendation': 'HEDGE' if abs(worst_unhedged) > hedging_cost * 10 else 'MONITOR'
            }
            
        except Exception as e:
            raise Exception(f"P&L scenario calculation failed: {str(e)}")
    
    def _assess_risk_level(self, delta: float, vega: float, gamma: float) -> str:
        """Assess overall platform risk level"""
        if (abs(delta) > self.risk_limits['max_delta_exposure_btc'] or 
            abs(vega) > self.risk_limits['max_vega_exposure'] or
            abs(gamma) > self.risk_limits['max_gamma_exposure']):
            return 'CRITICAL - Immediate hedging required'
        elif abs(delta) > self.risk_limits['hedge_trigger_threshold']:
            return 'HIGH - Hedging strongly recommended'
        else:
            return 'ACCEPTABLE - Within risk tolerance'
    
    def _get_client_position_description(self, strategy_name: str) -> str:
        """Get client position description"""
        descriptions = {
            'protective_put': 'Long BTC + Long Put (Protected Position)',
            'covered_call': 'Long BTC + Short Call (Income Generation)',
            'cash_secured_put': 'Cash Position + Short Put (Income + Accumulation)',
            'short_strangle': 'Short Put + Short Call (Premium Collection)',
            'put_spread': 'Long Put Spread (Cost-Efficient Protection)'
        }
        return descriptions.get(strategy_name, 'Complex Options Strategy')
    
    def _get_platform_risk_description(self, strategy_name: str) -> str:
        """Get platform risk exposure description"""
        descriptions = {
            'protective_put': 'Short Put Risk - Negative delta exposure',
            'covered_call': 'Long Call Risk - Positive delta exposure', 
            'cash_secured_put': 'Long Put Risk - Negative delta exposure',
            'short_strangle': 'Long Options Risk - Vega and gamma exposure',
            'put_spread': 'Short Spread Risk - Net negative delta'
        }
        return descriptions.get(strategy_name, 'Complex Risk Profile')
