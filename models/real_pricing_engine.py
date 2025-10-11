"""
Real Black-Scholes Pricing Engine - Live Demo
Repository: https://github.com/willialso/atticusPro_liveDemo
"""
import numpy as np
from scipy.stats import norm
from datetime import datetime, timedelta
import math

class RealBlackScholesEngine:
    def __init__(self, treasury_service, market_data_service):
        self.treasury_service = treasury_service
        self.market_data_service = market_data_service
    
    def calculate_real_strategy_pricing(self, strategy_type, position_size, current_price, volatility):
        """Calculate real strategy pricing using Black-Scholes"""
        try:
            treasury_data = self.treasury_service.get_current_risk_free_rate()
            risk_free_rate = treasury_data['rate_decimal']
            
            # Default parameters
            time_to_expiry = 45 / 365.0  # 45 days in years
            
            if strategy_type == 'protective_put':
                strike_price = current_price * 0.90  # 10% OTM put
                put_price = self._black_scholes_put(current_price, strike_price, time_to_expiry, risk_free_rate, volatility)
                
                total_premium = put_price * position_size
                
                greeks = self._calculate_greeks(current_price, strike_price, time_to_expiry, risk_free_rate, volatility, 'put')
                
                return {
                    'strategy_name': strategy_type,
                    'btc_spot_price': current_price,
                    'strike_price': strike_price,
                    'total_premium': total_premium,
                    'premium_per_contract': put_price,
                    'contracts_needed': position_size,
                    'days_to_expiry': 45,
                    'implied_volatility': volatility,
                    'risk_free_rate': risk_free_rate,
                    'cost_as_pct': (total_premium / (position_size * current_price)) * 100,
                    'greeks': greeks,
                    'option_type': 'Professional Put Options'
                }
            
            elif strategy_type == 'long_straddle':
                call_price = self._black_scholes_call(current_price, current_price, time_to_expiry, risk_free_rate, volatility)
                put_price = self._black_scholes_put(current_price, current_price, time_to_expiry, risk_free_rate, volatility)
                
                straddle_price = call_price + put_price
                total_premium = straddle_price * position_size
                
                # Combined Greeks for straddle
                call_greeks = self._calculate_greeks(current_price, current_price, time_to_expiry, risk_free_rate, volatility, 'call')
                put_greeks = self._calculate_greeks(current_price, current_price, time_to_expiry, risk_free_rate, volatility, 'put')
                
                combined_greeks = {
                    'delta': call_greeks['delta'] + put_greeks['delta'],
                    'gamma': call_greeks['gamma'] + put_greeks['gamma'],
                    'vega': call_greeks['vega'] + put_greeks['vega'],
                    'theta': call_greeks['theta'] + put_greeks['theta'],
                    'rho': call_greeks['rho'] + put_greeks['rho']
                }
                
                return {
                    'strategy_name': strategy_type,
                    'btc_spot_price': current_price,
                    'strike_price': current_price,
                    'total_premium': total_premium,
                    'premium_per_contract': straddle_price,
                    'contracts_needed': position_size,
                    'days_to_expiry': 45,
                    'implied_volatility': volatility,
                    'cost_as_pct': (total_premium / (position_size * current_price)) * 100,
                    'greeks': combined_greeks,
                    'option_type': 'Professional Straddle'
                }
            
            elif strategy_type == 'collar':
                put_strike = current_price * 0.90  # Protective put
                call_strike = current_price * 1.10  # Covered call
                
                put_price = self._black_scholes_put(current_price, put_strike, time_to_expiry, risk_free_rate, volatility)
                call_price = self._black_scholes_call(current_price, call_strike, time_to_expiry, risk_free_rate, volatility)
                
                # Net premium (put cost - call premium received)
                net_premium = (put_price - call_price) * position_size
                
                return {
                    'strategy_name': strategy_type,
                    'btc_spot_price': current_price,
                    'strike_price': put_strike,  # Primary strike (put)
                    'call_strike_price': call_strike,
                    'total_premium': net_premium,
                    'premium_per_contract': put_price - call_price,
                    'contracts_needed': position_size,
                    'days_to_expiry': 45,
                    'implied_volatility': volatility,
                    'option_type': 'Professional Collar'
                }
            
            else:
                # Generic strategy fallback
                estimated_premium = position_size * current_price * 0.015  # 1.5% of notional
                
                return {
                    'strategy_name': strategy_type,
                    'btc_spot_price': current_price,
                    'strike_price': current_price * 0.90,
                    'total_premium': estimated_premium,
                    'contracts_needed': position_size,
                    'days_to_expiry': 45,
                    'implied_volatility': volatility,
                    'option_type': 'Professional Options'
                }
                
        except Exception as e:
            print(f"Pricing engine error: {e}")
            
            # Fallback pricing
            estimated_premium = position_size * current_price * 0.015
            
            return {
                'strategy_name': strategy_type,
                'btc_spot_price': current_price,
                'strike_price': current_price * 0.90,
                'total_premium': estimated_premium,
                'contracts_needed': position_size,
                'pricing_error': str(e),
                'fallback_pricing': True
            }
    
    def _black_scholes_call(self, S, K, T, r, sigma):
        """Black-Scholes call option pricing"""
        d1 = (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
        d2 = d1 - sigma * np.sqrt(T)
        
        call_price = S * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)
        return max(call_price, 0)
    
    def _black_scholes_put(self, S, K, T, r, sigma):
        """Black-Scholes put option pricing"""
        d1 = (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
        d2 = d1 - sigma * np.sqrt(T)
        
        put_price = K * np.exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1)
        return max(put_price, 0)
    
    def _calculate_greeks(self, S, K, T, r, sigma, option_type):
        """Calculate option Greeks"""
        try:
            d1 = (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
            d2 = d1 - sigma * np.sqrt(T)
            
            # Common calculations
            nd1 = norm.cdf(d1)
            nd2 = norm.cdf(d2)
            pdf_d1 = norm.pdf(d1)
            
            if option_type == 'call':
                delta = nd1
                rho = K * T * np.exp(-r * T) * nd2
            else:  # put
                delta = nd1 - 1
                rho = -K * T * np.exp(-r * T) * norm.cdf(-d2)
            
            gamma = pdf_d1 / (S * sigma * np.sqrt(T))
            vega = S * pdf_d1 * np.sqrt(T)
            theta = -(S * pdf_d1 * sigma) / (2 * np.sqrt(T)) - r * K * np.exp(-r * T) * nd2
            
            if option_type == 'put':
                theta = theta + r * K * np.exp(-r * T)
            
            return {
                'delta': float(delta),
                'gamma': float(gamma),
                'vega': float(vega / 100),  # Vega per 1% vol change
                'theta': float(theta / 365),  # Theta per day
                'rho': float(rho / 100)  # Rho per 1% rate change
            }
            
        except Exception as e:
            return {
                'delta': 0.0,
                'gamma': 0.0,
                'vega': 0.0,
                'theta': 0.0,
                'rho': 0.0,
                'error': str(e)
            }
