"""
ATTICUS V1 - Professional Black-Scholes Pricing Engine
Real institutional-grade option pricing with Greeks
"""
import numpy as np
import math
from scipy.stats import norm
from datetime import datetime, timedelta
from config.settings import Config

class BlackScholesEngine:
    """
    Professional Black-Scholes implementation with Greeks
    Ensures platform profitability through accurate pricing + markup
    """
    
    def __init__(self):
        self.risk_free_rate = Config.get_risk_free_rate()
        self.markup_rate = Config.OPTION_MARKUP_RATE
    
    def calculate_option_price(self, spot_price, strike_price, time_to_expiry, 
                             implied_volatility, option_type='put'):
        """
        Professional Black-Scholes pricing with platform markup
        
        Args:
            spot_price: Current BTC price
            strike_price: Option strike
            time_to_expiry: Years to expiration
            implied_volatility: IV from Deribit
            option_type: 'call' or 'put'
            
        Returns:
            Dict with price, greeks, and platform pricing
        """
        
        S = spot_price
        K = strike_price
        T = time_to_expiry
        r = self.risk_free_rate
        sigma = implied_volatility
        
        # Black-Scholes calculation
        d1 = (math.log(S/K) + (r + sigma**2/2)*T) / (sigma*math.sqrt(T))
        d2 = d1 - sigma*math.sqrt(T)
        
        if option_type.lower() == 'call':
            theoretical_price = S*norm.cdf(d1) - K*math.exp(-r*T)*norm.cdf(d2)
            delta = norm.cdf(d1)
            theta = (-S*norm.pdf(d1)*sigma/(2*math.sqrt(T)) 
                    - r*K*math.exp(-r*T)*norm.cdf(d2)) / 365
        else:  # put
            theoretical_price = K*math.exp(-r*T)*norm.cdf(-d2) - S*norm.cdf(-d1)
            delta = -norm.cdf(-d1)
            theta = (-S*norm.pdf(d1)*sigma/(2*math.sqrt(T)) 
                    + r*K*math.exp(-r*T)*norm.cdf(-d2)) / 365
        
        # Common Greeks
        gamma = norm.pdf(d1) / (S*sigma*math.sqrt(T))
        vega = S*norm.pdf(d1)*math.sqrt(T) / 100  # Per 1% vol change
        rho = (K*T*math.exp(-r*T)*norm.cdf(d2 if option_type.lower() == 'call' else -d2)) / 100
        
        # Platform pricing with profitability markup
        platform_markup = Config.calculate_platform_fee(theoretical_price)
        platform_price = theoretical_price + platform_markup
        
        return {
            'theoretical_price': theoretical_price,
            'platform_price': platform_price,
            'markup_amount': platform_markup,
            'markup_percentage': (platform_markup / theoretical_price) * 100,
            'greeks': {
                'delta': delta,
                'gamma': gamma,
                'theta': theta,
                'vega': vega,
                'rho': rho
            },
            'risk_metrics': {
                'intrinsic_value': max(0, S-K if option_type.lower() == 'call' else K-S),
                'time_value': theoretical_price - max(0, S-K if option_type.lower() == 'call' else K-S),
                'moneyness': S/K if option_type.lower() == 'call' else K/S
            }
        }
    
    def calculate_portfolio_greeks(self, positions):
        """
        Calculate aggregate Greeks for portfolio risk management
        Critical for platform hedging decisions
        """
        total_delta = sum(pos['quantity'] * pos['greeks']['delta'] for pos in positions)
        total_gamma = sum(pos['quantity'] * pos['greeks']['gamma'] for pos in positions)
        total_theta = sum(pos['quantity'] * pos['greeks']['theta'] for pos in positions)
        total_vega = sum(pos['quantity'] * pos['greeks']['vega'] for pos in positions)
        
        return {
            'net_delta': total_delta,
            'net_gamma': total_gamma,
            'net_theta': total_theta,
            'net_vega': total_vega,
            'hedge_required': abs(total_delta) > Config.DELTA_HEDGE_THRESHOLD
        }

class VolatilityEngine:
    """
    Professional volatility calculations for accurate pricing
    Uses Deribit implied volatility surface
    """
    
    def __init__(self):
        self.iv_surface = {}
        self.last_updated = None
    
    def get_implied_volatility(self, strike_price, expiry_date, option_type, spot_price):
        """
        Get implied volatility from Deribit surface
        Falls back to calculated volatility if not available
        """
        # Primary: Use Deribit IV if available
        surface_key = (strike_price, expiry_date, option_type)
        if surface_key in self.iv_surface:
            return self.iv_surface[surface_key]
        
        # Fallback: Calculate from historical volatility with adjustments
        moneyness = strike_price / spot_price
        time_to_expiry = (expiry_date - datetime.now()).days / 365.0
        
        # Base volatility adjusted for moneyness and time
        base_vol = 0.70  # 70% base BTC volatility
        moneyness_adj = 1.0 + abs(1.0 - moneyness) * 0.1  # Volatility smile
        time_adj = 1.0 + (0.5 - time_to_expiry) * 0.05 if time_to_expiry < 0.5 else 1.0
        
        adjusted_iv = base_vol * moneyness_adj * time_adj
        
        return min(max(adjusted_iv, 0.30), 2.0)  # Bounded between 30%-200%
    
    def update_iv_surface(self, deribit_data):
        """Update IV surface from Deribit market data"""
        self.iv_surface = deribit_data
        self.last_updated = datetime.now()
