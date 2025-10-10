"""
ATTICUS V1 - ENHANCED Black-Scholes Pricing Engine
ADDED: Cash-secured puts, short strangles, calendar spreads
FIXED: All volatility handling uses decimal internally
"""
import math
from scipy.stats import norm
from typing import Dict

class RealBlackScholesEngine:
    """
    Professional Black-Scholes with expanded strategy support
    """
    
    def __init__(self, treasury_service, market_data_service):
        self.treasury_service = treasury_service
        self.market_data_service = market_data_service
        self.risk_free_rate = None
        self._update_risk_free_rate()
    
    def _update_risk_free_rate(self):
        """Get REAL risk-free rate from Treasury service"""
        try:
            treasury_data = self.treasury_service.get_current_risk_free_rate()
            self.risk_free_rate = treasury_data['rate']
            print(f"✅ Using REAL Treasury rate: {treasury_data['rate_percent']:.3f}%")
        except Exception as e:
            raise Exception(f"CANNOT OPERATE WITHOUT REAL TREASURY RATE: {str(e)}")
    
    def calculate_real_option_price(self, spot_price: float, strike_price: float, 
                                   time_to_expiry: float, real_volatility: float, 
                                   option_type: str = 'put') -> Dict:
        """Calculate option price - volatility input is DECIMAL"""
        if not all([spot_price > 0, strike_price > 0, time_to_expiry > 0, real_volatility > 0]):
            raise Exception("INVALID INPUTS - All parameters must be positive real values")
        
        if not self.risk_free_rate:
            raise Exception("NO REAL RISK-FREE RATE AVAILABLE")
        
        S = float(spot_price)
        K = float(strike_price) 
        T = float(time_to_expiry)
        r = float(self.risk_free_rate)
        sigma = float(real_volatility)  # Input is decimal (0.298)
        
        try:
            # Black-Scholes calculation
            d1 = (math.log(S/K) + (r + sigma**2/2)*T) / (sigma*math.sqrt(T))
            d2 = d1 - sigma*math.sqrt(T)
            
            # Calculate option prices
            if option_type.lower() == 'call':
                theoretical_price = S*norm.cdf(d1) - K*math.exp(-r*T)*norm.cdf(d2)
                delta = norm.cdf(d1)
                theta = (-S*norm.pdf(d1)*sigma/(2*math.sqrt(T)) 
                        - r*K*math.exp(-r*T)*norm.cdf(d2)) / 365
            elif option_type.lower() == 'put':
                theoretical_price = K*math.exp(-r*T)*norm.cdf(-d2) - S*norm.cdf(-d1)
                delta = -norm.cdf(-d1) 
                theta = (-S*norm.pdf(d1)*sigma/(2*math.sqrt(T)) 
                        + r*K*math.exp(-r*T)*norm.cdf(-d2)) / 365
            else:
                raise Exception(f"INVALID OPTION TYPE: {option_type}")
            
            # Calculate Greeks
            gamma = norm.pdf(d1) / (S*sigma*math.sqrt(T))
            vega = S*norm.pdf(d1)*math.sqrt(T) / 100
            rho = (K*T*math.exp(-r*T) * 
                  norm.cdf(d2 if option_type.lower() == 'call' else -d2)) / 100
            
            if theoretical_price < 0:
                raise Exception("NEGATIVE OPTION PRICE - Calculation error")
            
            platform_markup = theoretical_price * 0.025
            platform_price = theoretical_price + platform_markup
            
            return {
                'theoretical_price': theoretical_price,
                'platform_price': platform_price,
                'platform_markup': platform_markup,
                'markup_percentage': 2.5,
                'greeks': {
                    'delta': delta,
                    'gamma': gamma, 
                    'theta': theta,
                    'vega': vega,
                    'rho': rho
                },
                'inputs_used': {
                    'spot_price': S,
                    'strike_price': K,
                    'time_to_expiry_years': T,
                    'risk_free_rate': r,
                    'volatility': sigma,
                    'option_type': option_type
                },
                'calculation_method': 'Real Black-Scholes'
            }
            
        except Exception as e:
            raise Exception(f"BLACK-SCHOLES CALCULATION FAILED: {str(e)}")
    
    def calculate_real_strategy_pricing(self, strategy_name: str, position_size: float,
                                       spot_price: float, real_volatility: float) -> Dict:
        """ENHANCED: Calculate pricing for expanded strategy set"""
        if position_size <= 0:
            raise Exception("INVALID POSITION SIZE")
        
        try:
            contracts_needed = int(abs(position_size))
            
            if strategy_name == 'protective_put':
                return self._price_protective_put(contracts_needed, spot_price, real_volatility)
            
            elif strategy_name == 'put_spread':
                return self._price_put_spread(contracts_needed, spot_price, real_volatility)
            
            elif strategy_name == 'covered_call':
                return self._price_covered_call(contracts_needed, spot_price, real_volatility)
            
            elif strategy_name == 'cash_secured_put':
                return self._price_cash_secured_put(contracts_needed, spot_price, real_volatility)
            
            elif strategy_name == 'short_strangle':
                return self._price_short_strangle(contracts_needed, spot_price, real_volatility)
            
            elif strategy_name == 'calendar_spread':
                return self._price_calendar_spread(contracts_needed, spot_price, real_volatility)
            
            else:
                raise Exception(f"UNSUPPORTED STRATEGY: {strategy_name}")
                
        except Exception as e:
            raise Exception(f"STRATEGY PRICING FAILED: {str(e)}")
    
    def _price_protective_put(self, contracts: int, spot: float, vol: float) -> Dict:
        """Price protective put strategy"""
        strike_price = spot * 0.90
        time_to_expiry = 45 / 365.0
        
        put_pricing = self.calculate_real_option_price(
            spot, strike_price, time_to_expiry, vol, 'put'
        )
        
        return {
            'strategy_name': 'protective_put',
            'contracts_needed': contracts,
            'strike_price': strike_price,
            'premium_per_contract': put_pricing['platform_price'],
            'total_premium': contracts * put_pricing['platform_price'],
            'cost_as_pct': (put_pricing['platform_price'] / spot) * 100,
            'implied_volatility': vol,  # DECIMAL
            'days_to_expiry': 45,
            'greeks': put_pricing['greeks'],
            'option_type': 'Professional Put Options'
        }
    
    def _price_put_spread(self, contracts: int, spot: float, vol: float) -> Dict:
        """Price put spread strategy"""
        long_strike = spot * 0.92
        short_strike = spot * 0.82
        time_to_expiry = 30 / 365.0
        
        long_put = self.calculate_real_option_price(spot, long_strike, time_to_expiry, vol, 'put')
        short_put = self.calculate_real_option_price(spot, short_strike, time_to_expiry, vol, 'put')
        
        net_premium = long_put['platform_price'] - short_put['platform_price']
        
        return {
            'strategy_name': 'put_spread',
            'contracts_needed': contracts,
            'long_strike': long_strike,
            'short_strike': short_strike,
            'total_premium': contracts * net_premium,
            'cost_as_pct': (net_premium / spot) * 100,
            'implied_volatility': vol,  # DECIMAL
            'days_to_expiry': 30,
            'max_protection': (long_strike - short_strike) * contracts
        }
    
    def _price_covered_call(self, contracts: int, spot: float, vol: float) -> Dict:
        """Price covered call strategy"""
        strike_price = spot * 1.10
        time_to_expiry = 35 / 365.0
        
        call_pricing = self.calculate_real_option_price(
            spot, strike_price, time_to_expiry, vol, 'call'
        )
        
        return {
            'strategy_name': 'covered_call',
            'contracts_needed': contracts,
            'strike_price': strike_price,
            'premium_per_contract': call_pricing['platform_price'],
            'total_premium': -contracts * call_pricing['platform_price'],  # Income (negative)
            'cost_as_pct': -(call_pricing['platform_price'] / spot) * 100,  # Income
            'implied_volatility': vol,  # DECIMAL
            'days_to_expiry': 35,
            'greeks': {k: -v for k, v in call_pricing['greeks'].items()},  # Short position
            'upside_cap': strike_price
        }
    
    def _price_cash_secured_put(self, contracts: int, spot: float, vol: float) -> Dict:
        """NEW: Price cash-secured put strategy"""
        strike_price = spot * 0.95  # 5% OTM
        time_to_expiry = 30 / 365.0
        
        put_pricing = self.calculate_real_option_price(
            spot, strike_price, time_to_expiry, vol, 'put'
        )
        
        return {
            'strategy_name': 'cash_secured_put',
            'contracts_needed': contracts,
            'strike_price': strike_price,
            'premium_per_contract': put_pricing['platform_price'],
            'total_premium': -contracts * put_pricing['platform_price'],  # Income
            'cost_as_pct': -(put_pricing['platform_price'] / spot) * 100,
            'implied_volatility': vol,  # DECIMAL
            'days_to_expiry': 30,
            'greeks': {k: -v for k, v in put_pricing['greeks'].items()},
            'cash_required': contracts * strike_price
        }
    
    def _price_short_strangle(self, contracts: int, spot: float, vol: float) -> Dict:
        """NEW: Price short strangle strategy"""
        put_strike = spot * 0.90  # 10% OTM put
        call_strike = spot * 1.10  # 10% OTM call
        time_to_expiry = 30 / 365.0
        
        put_pricing = self.calculate_real_option_price(spot, put_strike, time_to_expiry, vol, 'put')
        call_pricing = self.calculate_real_option_price(spot, call_strike, time_to_expiry, vol, 'call')
        
        total_income = put_pricing['platform_price'] + call_pricing['platform_price']
        
        return {
            'strategy_name': 'short_strangle',
            'contracts_needed': contracts,
            'put_strike': put_strike,
            'call_strike': call_strike,
            'premium_per_contract': total_income,
            'total_premium': -contracts * total_income,  # Income
            'cost_as_pct': -(total_income / spot) * 100,
            'implied_volatility': vol,  # DECIMAL
            'days_to_expiry': 30,
            'profit_range': f'${put_strike:,.0f} - ${call_strike:,.0f}'
        }
    
    def _price_calendar_spread(self, contracts: int, spot: float, vol: float) -> Dict:
        """NEW: Price calendar spread strategy"""
        strike_price = spot  # ATM
        near_expiry = 15 / 365.0  # 15 days
        far_expiry = 45 / 365.0   # 45 days
        
        near_call = self.calculate_real_option_price(spot, strike_price, near_expiry, vol, 'call')
        far_call = self.calculate_real_option_price(spot, strike_price, far_expiry, vol, 'call')
        
        net_cost = far_call['platform_price'] - near_call['platform_price']
        
        return {
            'strategy_name': 'calendar_spread',
            'contracts_needed': contracts,
            'strike_price': strike_price,
            'total_premium': contracts * net_cost,
            'cost_as_pct': (net_cost / spot) * 100,
            'implied_volatility': vol,  # DECIMAL
            'near_expiry_days': 15,
            'far_expiry_days': 45
        }
