"""
ATTICUS PROFESSIONAL V17.2 - MULTI-STRATEGY INSTITUTIONAL PLATFORM
Enhanced with multiple smart strategy recommendations
"""

import os
import math
import json
import time
import traceback
from datetime import datetime, timedelta
from flask import Flask, render_template, jsonify, request, session
from typing import Dict, List, Optional, Any

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'atticus_professional_v17_2025')

# Platform Configuration
PLATFORM_CONFIG = {
    'markup_percentage': 2.5,
    'min_markup_dollars': 50,
    'execution_fee': 25,
    'hedge_reserve_ratio': 1.1,
    'max_single_institution_btc': 10000,
    'platform_hedge_threshold': 5.0
}

# Global platform state
platform_state = {
    'total_client_exposure_btc': 0.0,
    'total_platform_hedges_btc': 0.0,
    'net_platform_exposure_btc': 0.0,
    'active_institutions': [],
    'total_premium_collected': 0.0,
    'total_hedge_cost': 0.0
}

class MarketDataService:
    """Live market data service"""
    
    def __init__(self):
        self.price_cache = 111500.0
        self.cache_time = datetime.now()
        print("✅ MarketDataService initialized")
        
    def get_live_btc_price(self):
        """Get live BTC price with robust fallback"""
        if self.price_cache and self.cache_time:
            age = (datetime.now() - self.cache_time).total_seconds()
            if age < 300:
                return self.price_cache
        
        try:
            import requests
            response = requests.get('https://api.coinbase.com/v2/exchange-rates?currency=BTC', timeout=3)
            if response.status_code == 200:
                data = response.json()
                price = float(data['data']['rates']['USD'])
                if price > 10000:
                    self.price_cache = price
                    self.cache_time = datetime.now()
                    print(f"📊 Live BTC price: ${price:,.2f}")
                    return price
        except Exception as e:
            print(f"⚠️ Coinbase API error: {e}")
        
        try:
            import requests
            response = requests.get('https://api.coindesk.com/v1/bpi/currentprice/USD.json', timeout=3)
            if response.status_code == 200:
                data = response.json()
                price_str = data['bpi']['USD']['rate'].replace(',', '').replace('$', '')
                price = float(price_str)
                if price > 10000:
                    self.price_cache = price
                    self.cache_time = datetime.now()
                    print(f"📊 CoinDesk BTC price: ${price:,.2f}")
                    return price
        except Exception as e:
            print(f"⚠️ CoinDesk API error: {e}")
        
        fallback_price = self.price_cache if self.price_cache else 111500.0
        print(f"📊 Using fallback BTC price: ${fallback_price:,.2f}")
        return fallback_price
    
    def get_volatility(self):
        return 0.65
    
    def get_risk_free_rate(self):
        return 0.0475

class PortfolioAnalyzer:
    """Portfolio analysis service"""
    
    def __init__(self, market_service):
        self.market = market_service
        self.profiles = {
            'pension_fund': {
                'name': 'State Pension Fund',
                'aum': 2100000000,
                'btc_allocation_pct': 3.0,
                'risk_tolerance': 'conservative',
                'hedge_ratio_target': 0.85,
                'preferred_strategies': ['protective_put', 'collar', 'put_spread']
            },
            'hedge_fund': {
                'name': 'Quantitative Hedge Fund',
                'aum': 450000000,
                'btc_allocation_pct': 15.0,
                'risk_tolerance': 'aggressive',
                'hedge_ratio_target': 0.60,
                'preferred_strategies': ['collar', 'put_spread', 'protective_put']
            },
            'family_office': {
                'name': 'UHNW Family Office',
                'aum': 180000000,
                'btc_allocation_pct': 8.0,
                'risk_tolerance': 'moderate',
                'hedge_ratio_target': 0.75,
                'preferred_strategies': ['protective_put', 'collar', 'covered_call']
            },
            'corporate_treasury': {
                'name': 'Corporate Treasury',
                'aum': 500000000,
                'btc_allocation_pct': 5.0,
                'risk_tolerance': 'conservative',
                'hedge_ratio_target': 0.90,
                'preferred_strategies': ['protective_put', 'put_spread', 'collar']
            }
        }
        print("✅ PortfolioAnalyzer initialized")
    
    def analyze(self, portfolio_type=None, custom_params=None):
        """Analyze portfolio with multiple strategy recommendations"""
        try:
            if custom_params:
                return self._analyze_custom(custom_params)
            
            profile = self.profiles.get(portfolio_type, self.profiles['pension_fund'])
            btc_price = self.market.get_live_btc_price()
            vol = self.market.get_volatility()
            
            btc_allocation = profile['aum'] * (profile['btc_allocation_pct'] / 100)
            btc_size = btc_allocation / btc_price
            
            var_1d = self._safe_var_calculation(btc_size, btc_price, vol, 1)
            var_30d = self._safe_var_calculation(btc_size, btc_price, vol, 30)
            scenarios = self._generate_scenarios(btc_size, btc_price)
            
            result = {
                'profile': profile,
                'positions': {
                    'btc_size': round(btc_size, 4),
                    'btc_value': round(btc_allocation, 2),
                    'current_price': round(btc_price, 2)
                },
                'risk_metrics': {
                    'var_1d_95': round(var_1d, 2),
                    'var_30d_95': round(var_30d, 2),
                    'volatility': vol,
                    'max_drawdown_30pct': round(btc_allocation * 0.30, 2)
                },
                'scenarios': scenarios,
                'hedge_recommendation': {
                    'hedge_ratio': profile['hedge_ratio_target'],
                    'hedge_size_btc': round(btc_size * profile['hedge_ratio_target'], 4),
                    'preferred_strategies': profile['preferred_strategies']
                }
            }
            
            print(f"✅ Analyzed {profile['name']}: {btc_size:.2f} BTC (${btc_allocation:,.0f})")
            return result
            
        except Exception as e:
            print(f"❌ Portfolio analysis error: {e}")
            raise Exception(f"Analysis failed: {str(e)}")
    
    def _analyze_custom(self, params):
        """Analyze custom position"""
        try:
            btc_price = self.market.get_live_btc_price()
            vol = self.market.get_volatility()
            position_size = float(params.get('size', 1.0))
            institution_type = params.get('type', 'hedge_fund')
            
            if position_size <= 0:
                position_size = 1.0
            
            position_value = position_size * btc_price
            
            # Use institution type preferences for custom positions
            base_profile = self.profiles.get(institution_type, self.profiles['hedge_fund'])
            
            var_1d = self._safe_var_calculation(position_size, btc_price, vol, 1)
            var_30d = self._safe_var_calculation(position_size, btc_price, vol, 30)
            scenarios = self._generate_scenarios(position_size, btc_price)
            
            result = {
                'profile': {
                    'name': 'Custom Position', 
                    'risk_tolerance': base_profile['risk_tolerance'],
                    'preferred_strategies': base_profile['preferred_strategies']
                },
                'positions': {
                    'btc_size': round(position_size, 4),
                    'btc_value': round(position_value, 2),
                    'current_price': round(btc_price, 2)
                },
                'risk_metrics': {
                    'var_1d_95': round(var_1d, 2),
                    'var_30d_95': round(var_30d, 2),
                    'volatility': vol,
                    'max_drawdown_30pct': round(position_value * 0.30, 2)
                },
                'scenarios': scenarios,
                'hedge_recommendation': {
                    'hedge_ratio': base_profile['hedge_ratio_target'],
                    'hedge_size_btc': round(position_size * base_profile['hedge_ratio_target'], 4),
                    'preferred_strategies': base_profile['preferred_strategies']
                }
            }
            
            print(f"✅ Custom analysis: {position_size} BTC (${position_value:,.0f})")
            return result
            
        except Exception as e:
            print(f"❌ Custom analysis error: {e}")
            raise Exception(f"Custom analysis failed: {str(e)}")
    
    def _safe_var_calculation(self, size, price, vol, days):
        try:
            if size <= 0 or price <= 0 or vol <= 0 or days <= 0:
                return 0.0
            value = size * price
            z_score = 1.645
            var = value * vol * z_score * math.sqrt(days / 365)
            return abs(var)
        except Exception as e:
            print(f"⚠️ VaR calculation error: {e}")
            return 0.0
    
    def _generate_scenarios(self, size, price):
        scenarios = []
        try:
            value = size * price
            for pct in [-30, -20, -10, 0, 10, 20, 30]:
                try:
                    new_price = price * (1 + pct/100)
                    new_value = size * new_price
                    scenarios.append({
                        'change_pct': pct,
                        'btc_price': round(new_price, 2),
                        'value': round(new_value, 2),
                        'pnl': round(new_value - value, 2),
                        'type': 'stress' if pct <= -20 else 'normal' if -10 <= pct <= 10 else 'favorable'
                    })
                except:
                    continue
        except Exception as e:
            print(f"⚠️ Scenario generation error: {e}")
        
        return scenarios

class MultiStrategyPricingEngine:
    """Enhanced pricing engine with multiple strategy support"""
    
    def __init__(self, market_service):
        self.market = market_service
        self.risk_free_rate = 0.0475
        print("✅ MultiStrategyPricingEngine initialized")
    
    def price_all_strategies(self, analysis_data):
        """Price all suitable strategies for the given analysis"""
        try:
            positions = analysis_data['positions']
            hedge_rec = analysis_data['hedge_recommendation']
            profile = analysis_data['profile']
            
            current_price = positions['current_price']
            hedge_size = hedge_rec['hedge_size_btc']
            preferred_strategies = hedge_rec.get('preferred_strategies', ['protective_put'])
            risk_tolerance = profile.get('risk_tolerance', 'moderate')
            
            strategies = []
            
            # Price each preferred strategy
            for i, strategy_type in enumerate(preferred_strategies):
                try:
                    strategy = self._price_single_strategy(
                        strategy_type, hedge_size, current_price, risk_tolerance
                    )
                    strategy['recommended'] = (i == 0)  # First strategy is recommended
                    strategy['risk_tolerance_match'] = risk_tolerance
                    strategies.append(strategy)
                except Exception as e:
                    print(f"❌ Error pricing {strategy_type}: {e}")
                    continue
            
            # Ensure we have at least one strategy
            if not strategies:
                fallback = self._price_single_strategy('protective_put', hedge_size, current_price, risk_tolerance)
                fallback['recommended'] = True
                strategies.append(fallback)
            
            return strategies
            
        except Exception as e:
            print(f"❌ Multi-strategy pricing error: {e}")
            raise Exception(f"Strategy pricing failed: {str(e)}")
    
    def _price_single_strategy(self, strategy_type, size, current_price, risk_tolerance):
        """Price a single strategy"""
        vol = self.market.get_volatility()
        T = 45 / 365.0
        
        if strategy_type == 'protective_put':
            return self._price_protective_put(size, current_price, vol, T, -5, risk_tolerance)
        elif strategy_type == 'collar':
            return self._price_collar(size, current_price, vol, T, -5, risk_tolerance)
        elif strategy_type == 'put_spread':
            return self._price_put_spread(size, current_price, vol, T, -5, risk_tolerance)
        elif strategy_type == 'covered_call':
            return self._price_covered_call(size, current_price, vol, T, 10, risk_tolerance)
        else:
            return self._price_protective_put(size, current_price, vol, T, -5, risk_tolerance)
    
    def _price_protective_put(self, size, S, vol, T, offset, risk_tolerance):
        """Price protective put strategy"""
        try:
            # Adjust strike based on risk tolerance
            strike_adj = {'conservative': -3, 'moderate': -5, 'aggressive': -8}
            actual_offset = strike_adj.get(risk_tolerance, -5)
            
            K = S * (1 + actual_offset/100)
            put_price = self._safe_bs_put(S, K, T, self.risk_free_rate, vol)
            
            base_premium = size * put_price
            markup_amount = max(
                base_premium * (PLATFORM_CONFIG['markup_percentage'] / 100),
                PLATFORM_CONFIG['min_markup_dollars'] * size
            )
            
            total_premium = base_premium + markup_amount
            exec_fee = PLATFORM_CONFIG['execution_fee']
            total_cost = total_premium + exec_fee
            
            return {
                'strategy_type': 'protective_put',
                'strategy_name': 'Protective Put Strategy',
                'strategy_description': 'Maximum downside protection with full upside participation. Ideal for conservative portfolios seeking capital preservation.',
                'position_size': size,
                'strike_price': round(K, 2),
                'premium_per_contract_base': round(put_price, 2),
                'base_premium_total': round(base_premium, 2),
                'platform_markup': round(markup_amount, 2),
                'execution_fee': exec_fee,
                'total_client_cost': round(total_cost, 2),
                'platform_revenue': round(markup_amount + exec_fee, 2),
                'cost_percentage': round((total_cost / (size * S)) * 100, 2),
                'max_loss': round(max(0, (S - K) * size) + total_cost, 2),
                'breakeven': round(K - (total_cost / size), 2),
                'protection_level': round(K, 2),
                'upside_participation': '100%',
                'time_to_expiry_days': 45,
                'key_benefits': [
                    'Full downside protection below strike price',
                    'Unlimited upside potential',
                    'Clear maximum loss amount',
                    'Professional execution and pricing'
                ],
                'risk_profile': risk_tolerance,
                'complexity': 'Low'
            }
        except Exception as e:
            print(f"❌ Put pricing error: {e}")
            return self._create_fallback_strategy(size, S, 'protective_put')
    
    def _price_collar(self, size, S, vol, T, offset, risk_tolerance):
        """Price collar strategy"""
        try:
            # Adjust strikes based on risk tolerance
            put_adj = {'conservative': -3, 'moderate': -5, 'aggressive': -8}
            call_adj = {'conservative': 20, 'moderate': 15, 'aggressive': 12}
            
            put_strike = S * (1 + put_adj.get(risk_tolerance, -5)/100)
            call_strike = S * (1 + call_adj.get(risk_tolerance, 15)/100)
            
            put_price = self._safe_bs_put(S, put_strike, T, self.risk_free_rate, vol)
            call_price = self._safe_bs_call(S, call_strike, T, self.risk_free_rate, vol)
            
            net_premium = size * (put_price - call_price)
            markup_amount = abs(net_premium) * (PLATFORM_CONFIG['markup_percentage'] / 100)
            total_premium = net_premium + markup_amount if net_premium >= 0 else net_premium - markup_amount
            exec_fee = PLATFORM_CONFIG['execution_fee']
            total_cost = abs(total_premium) + exec_fee
            
            return {
                'strategy_type': 'collar',
                'strategy_name': 'Collar Strategy',
                'strategy_description': 'Cost-effective protection with capped upside. Reduces premium cost by selling upside above call strike.',
                'position_size': size,
                'put_strike': round(put_strike, 2),
                'call_strike': round(call_strike, 2),
                'net_premium_base': round(net_premium, 2),
                'platform_markup': round(markup_amount, 2),
                'execution_fee': exec_fee,
                'total_client_cost': round(total_cost, 2),
                'platform_revenue': round(markup_amount + exec_fee, 2),
                'cost_percentage': round((total_cost / (size * S)) * 100, 2),
                'max_loss': round(max(0, (S - put_strike) * size) + total_cost, 2),
                'max_upside': round(call_strike, 2),
                'upside_participation': f"100% up to ${call_strike:,.0f}",
                'protection_level': round(put_strike, 2),
                'time_to_expiry_days': 45,
                'key_benefits': [
                    'Lower cost than outright put protection',
                    'Downside protection below put strike',
                    'Participates in upside to call strike',
                    'Self-funding in favorable conditions'
                ],
                'risk_profile': risk_tolerance,
                'complexity': 'Medium'
            }
        except Exception as e:
            print(f"❌ Collar pricing error: {e}")
            return self._create_fallback_strategy(size, S, 'collar')
    
    def _price_put_spread(self, size, S, vol, T, offset, risk_tolerance):
        """Price put spread strategy"""
        try:
            # Adjust strikes based on risk tolerance
            long_adj = {'conservative': -3, 'moderate': -5, 'aggressive': -8}
            short_adj = {'conservative': -8, 'moderate': -12, 'aggressive': -15}
            
            long_strike = S * (1 + long_adj.get(risk_tolerance, -5)/100)
            short_strike = S * (1 + short_adj.get(risk_tolerance, -12)/100)
            
            long_put = self._safe_bs_put(S, long_strike, T, self.risk_free_rate, vol)
            short_put = self._safe_bs_put(S, short_strike, T, self.risk_free_rate, vol)
            
            net_premium = size * (long_put - short_put)
            markup_amount = net_premium * (PLATFORM_CONFIG['markup_percentage'] / 100)
            total_premium = net_premium + markup_amount
            exec_fee = PLATFORM_CONFIG['execution_fee']
            total_cost = total_premium + exec_fee
            
            max_payout = size * (long_strike - short_strike)
            
            return {
                'strategy_type': 'put_spread',
                'strategy_name': 'Put Spread Strategy',
                'strategy_description': 'Cost-efficient protection for moderate declines. Lower premium than outright puts with defined risk.',
                'position_size': size,
                'long_strike': round(long_strike, 2),
                'short_strike': round(short_strike, 2),
                'net_premium_base': round(net_premium, 2),
                'platform_markup': round(markup_amount, 2),
                'execution_fee': exec_fee,
                'total_client_cost': round(total_cost, 2),
                'platform_revenue': round(markup_amount + exec_fee, 2),
                'cost_percentage': round((total_cost / (size * S)) * 100, 2),
                'max_loss': round(total_cost, 2),
                'max_payout': round(max_payout, 2),
                'breakeven': round(long_strike - (total_cost / size), 2),
                'protection_level': round(long_strike, 2),
                'upside_participation': '100%',
                'time_to_expiry_days': 45,
                'key_benefits': [
                    'Lower premium cost than outright puts',
                    'Protection against moderate declines',
                    'Defined maximum risk and reward',
                    'Efficient capital utilization'
                ],
                'risk_profile': risk_tolerance,
                'complexity': 'Medium'
            }
        except Exception as e:
            print(f"❌ Put spread pricing error: {e}")
            return self._create_fallback_strategy(size, S, 'put_spread')
    
    def _price_covered_call(self, size, S, vol, T, offset, risk_tolerance):
        """Price covered call strategy"""
        try:
            # Adjust call strike based on risk tolerance
            call_adj = {'conservative': 15, 'moderate': 10, 'aggressive': 5}
            call_strike = S * (1 + call_adj.get(risk_tolerance, 10)/100)
            
            call_price = self._safe_bs_call(S, call_strike, T, self.risk_free_rate, vol)
            
            gross_premium = size * call_price
            markup_amount = gross_premium * (PLATFORM_CONFIG['markup_percentage'] / 100)
            net_premium_received = gross_premium - markup_amount
            exec_fee = PLATFORM_CONFIG['execution_fee']
            total_net_received = net_premium_received - exec_fee
            
            return {
                'strategy_type': 'covered_call',
                'strategy_name': 'Covered Call Strategy',
                'strategy_description': 'Generate income from existing BTC position with capped upside. Ideal for range-bound markets.',
                'position_size': size,
                'call_strike': round(call_strike, 2),
                'premium_received_gross': round(gross_premium, 2),
                'platform_markup': round(markup_amount, 2),
                'execution_fee': exec_fee,
                'total_net_received': round(total_net_received, 2),
                'platform_revenue': round(markup_amount + exec_fee, 2),
                'income_percentage': round((total_net_received / (size * S)) * 100, 2),
                'max_upside': round(call_strike, 2),
                'breakeven': round(S - (total_net_received / size), 2),
                'upside_participation': f"100% up to ${call_strike:,.0f}",
                'time_to_expiry_days': 45,
                'key_benefits': [
                    'Generate income from BTC holdings',
                    'Reduce cost basis of position',
                    'Profit in sideways or moderately up markets',
                    'Professional execution and management'
                ],
                'risk_profile': risk_tolerance,
                'complexity': 'Low-Medium'
            }
        except Exception as e:
            print(f"❌ Covered call pricing error: {e}")
            return self._create_fallback_strategy(size, S, 'covered_call')
    
    def _safe_bs_put(self, S, K, T, r, sigma):
        try:
            if T <= 0 or S <= 0 or K <= 0 or sigma <= 0:
                return max(0, K - S)
            
            d1 = (math.log(S/K) + (r + 0.5*sigma**2)*T) / (sigma*math.sqrt(T))
            d2 = d1 - sigma*math.sqrt(T)
            
            put_price = K*math.exp(-r*T)*self._norm_cdf(-d2) - S*self._norm_cdf(-d1)
            return max(0, put_price)
        except Exception as e:
            print(f"⚠️ BS put calculation error: {e}")
            return max(0, K - S)
    
    def _safe_bs_call(self, S, K, T, r, sigma):
        try:
            if T <= 0 or S <= 0 or K <= 0 or sigma <= 0:
                return max(0, S - K)
            
            d1 = (math.log(S/K) + (r + 0.5*sigma**2)*T) / (sigma*math.sqrt(T))
            d2 = d1 - sigma*math.sqrt(T)
            
            call_price = S*self._norm_cdf(d1) - K*math.exp(-r*T)*self._norm_cdf(d2)
            return max(0, call_price)
        except Exception as e:
            print(f"⚠️ BS call calculation error: {e}")
            return max(0, S - K)
    
    def _norm_cdf(self, x):
        try:
            return 0.5 * (1 + math.erf(x / math.sqrt(2)))
        except:
            return 0.5 if x >= 0 else 0.0
    
    def _create_fallback_strategy(self, size, price, strategy_type):
        """Create fallback strategy when pricing fails"""
        strike = price * 0.95
        premium_estimate = price * 0.03 * size
        markup = premium_estimate * 0.025
        total_cost = premium_estimate + markup + 25
        
        return {
            'strategy_type': strategy_type,
            'strategy_name': f'{strategy_type.replace("_", " ").title()} Strategy (Estimated)',
            'strategy_description': 'Estimated pricing due to calculation error. Please contact support for accurate pricing.',
            'position_size': size,
            'strike_price': round(strike, 2),
            'base_premium_total': round(premium_estimate, 2),
            'platform_markup': round(markup, 2),
            'execution_fee': 25,
            'total_client_cost': round(total_cost, 2),
            'platform_revenue': round(markup + 25, 2),
            'cost_percentage': round((total_cost / (size * price)) * 100, 2),
            'max_loss': round((price - strike) * size + total_cost, 2),
            'breakeven': round(strike - (total_cost / size), 2),
            'protection_level': round(strike, 2),
            'time_to_expiry_days': 45,
            'key_benefits': ['Estimated pricing', 'Contact for accurate quotes'],
            'risk_profile': 'moderate',
            'complexity': 'Low'
        }

class ExchangeManager:
    """Exchange management service"""
    
    def __init__(self):
        self.exchanges = {
            'deribit': {'status': 'active', 'liquidity': 'high'},
            'okx': {'status': 'active', 'liquidity': 'medium'},
            'binance': {'status': 'active', 'liquidity': 'high'}
        }
        print("✅ ExchangeManager initialized")
    
    def calculate_optimal_execution(self, total_size, instrument_type='btc_options'):
        try:
            return [
                {
                    'exchange': 'deribit',
                    'size': round(total_size * 0.6, 4),
                    'cost': total_size * 0.6 * 0.0005,
                    'liquidity': 'high'
                },
                {
                    'exchange': 'okx',
                    'size': round(total_size * 0.4, 4),
                    'cost': total_size * 0.4 * 0.0005,
                    'liquidity': 'medium'
                }
            ]
        except:
            return [{'exchange': 'deribit', 'size': total_size, 'cost': total_size * 0.0005, 'liquidity': 'high'}]

class PlatformRiskManager:
    """Platform risk management"""
    
    def __init__(self, exchange_mgr):
        self.exchange_mgr = exchange_mgr
        print("✅ PlatformRiskManager initialized")
    
    def calculate_net_exposure(self):
        try:
            return {
                'total_client_long_btc': platform_state['total_client_exposure_btc'],
                'total_platform_hedges_btc': platform_state['total_platform_hedges_btc'],
                'net_exposure_btc': platform_state['net_platform_exposure_btc'],
                'hedge_coverage_ratio': (
                    platform_state['total_platform_hedges_btc'] / platform_state['total_client_exposure_btc']
                    if platform_state['total_client_exposure_btc'] > 0 else 0
                ),
                'requires_hedging': abs(platform_state['net_platform_exposure_btc']) > PLATFORM_CONFIG['platform_hedge_threshold'],
                'active_institutions': len(platform_state['active_institutions']),
                'total_premium_collected': platform_state['total_premium_collected'],
                'total_hedge_cost': platform_state['total_hedge_cost'],
                'net_revenue': platform_state['total_premium_collected'] - platform_state['total_hedge_cost']
            }
        except Exception as e:
            print(f"⚠️ Exposure calculation error: {e}")
            return {
                'total_client_long_btc': 0.0,
                'total_platform_hedges_btc': 0.0,
                'net_exposure_btc': 0.0,
                'hedge_coverage_ratio': 0.0,
                'requires_hedging': False,
                'active_institutions': 0,
                'total_premium_collected': 0.0,
                'total_hedge_cost': 0.0,
                'net_revenue': 0.0
            }

# Initialize services
print("🏛️ Initializing Atticus Professional v17.2...")

market_service = MarketDataService()
exchange_manager = ExchangeManager()
portfolio_analyzer = PortfolioAnalyzer(market_service)
multi_strategy_engine = MultiStrategyPricingEngine(market_service)
platform_risk_manager = PlatformRiskManager(exchange_manager)

print("🎯 All services initialized successfully!")

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/health')
def health():
    try:
        return jsonify({
            'status': 'healthy',
            'version': 'v17.2',
            'timestamp': datetime.now().isoformat(),
            'services': {
                'market_data': 'operational',
                'portfolio_analyzer': 'operational',
                'multi_strategy_engine': 'operational',
                'exchange_manager': 'operational',
                'platform_risk_manager': 'operational'
            },
            'btc_price': market_service.get_live_btc_price()
        })
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/market-data')
def market_data():
    try:
        price = market_service.get_live_btc_price()
        vol = market_service.get_volatility()
        rate = market_service.get_risk_free_rate()
        
        return jsonify({
            'btc_price': round(price, 2),
            'volatility': round(vol * 100, 1),
            'risk_free_rate': round(rate * 100, 2),
            'timestamp': datetime.now().isoformat(),
            'status': 'live'
        })
    except Exception as e:
        print(f"❌ Market data error: {e}")
        return jsonify({
            'btc_price': 111500.0,
            'volatility': 65.0,
            'risk_free_rate': 4.75,
            'timestamp': datetime.now().isoformat(),
            'status': 'fallback',
            'error': str(e)
        }), 500

@app.route('/api/analyze-portfolio', methods=['POST'])
def analyze_portfolio():
    try:
        data = request.get_json() or {}
        portfolio_type = data.get('type', 'pension_fund')
        custom_params = data.get('custom_params')
        
        print(f"📊 Analyzing: {portfolio_type}, custom: {bool(custom_params)}")
        
        analysis = portfolio_analyzer.analyze(portfolio_type, custom_params)
        session['portfolio_analysis'] = analysis
        
        return jsonify({'success': True, 'analysis': analysis})
    except Exception as e:
        error_msg = str(e)
        print(f"❌ Analysis error: {error_msg}")
        return jsonify({'success': False, 'error': error_msg}), 500

@app.route('/api/generate-strategies', methods=['POST'])
def generate_strategies():
    """Generate multiple strategy options"""
    try:
        analysis = session.get('portfolio_analysis')
        if not analysis:
            return jsonify({'success': False, 'error': 'No portfolio analysis found'}), 400
        
        print(f"💰 Generating multiple strategies for {analysis['profile']['name']}")
        
        strategies = multi_strategy_engine.price_all_strategies(analysis)
        session['available_strategies'] = strategies
        
        return jsonify({
            'success': True, 
            'strategies': strategies,
            'analysis_context': {
                'institution': analysis['profile']['name'],
                'position_size': analysis['positions']['btc_size'],
                'risk_tolerance': analysis['profile'].get('risk_tolerance', 'moderate')
            }
        })
    except Exception as e:
        error_msg = str(e)
        print(f"❌ Strategy generation error: {error_msg}")
        return jsonify({'success': False, 'error': error_msg}), 500

@app.route('/api/select-strategy', methods=['POST'])
def select_strategy():
    """Select a specific strategy for execution"""
    try:
        data = request.get_json() or {}
        strategy_type = data.get('strategy_type')
        
        available_strategies = session.get('available_strategies', [])
        selected_strategy = None
        
        for strategy in available_strategies:
            if strategy['strategy_type'] == strategy_type:
                selected_strategy = strategy
                break
        
        if not selected_strategy:
            return jsonify({'success': False, 'error': 'Strategy not found'}), 400
        
        # Add portfolio context
        analysis = session.get('portfolio_analysis')
        if analysis:
            selected_strategy['portfolio_context'] = {
                'institution': analysis['profile']['name'],
                'position_size_btc': analysis['positions']['btc_size'],
                'var_before': analysis['risk_metrics']['var_30d_95'],
                'var_after_estimated': analysis['risk_metrics']['var_30d_95'] * 0.25
            }
        
        session['selected_strategy'] = selected_strategy
        return jsonify({'success': True, 'strategy': selected_strategy})
    except Exception as e:
        error_msg = str(e)
        print(f"❌ Strategy selection error: {error_msg}")
        return jsonify({'success': False, 'error': error_msg}), 500

@app.route('/api/execute-strategy', methods=['POST'])
def execute_strategy():
    try:
        strategy = session.get('selected_strategy')
        if not strategy:
            return jsonify({'success': False, 'error': 'No strategy selected'}), 400
        
        size = strategy['position_size']
        execution_plan = exchange_manager.calculate_optimal_execution(size)
        
        # Update platform state
        platform_state['total_client_exposure_btc'] += size
        platform_state['total_premium_collected'] += strategy.get('platform_revenue', 0)
        
        net_exposure = platform_state['total_client_exposure_btc'] - platform_state['total_platform_hedges_btc']
        platform_state['net_platform_exposure_btc'] = net_exposure
        
        platform_hedge = {'status': 'no_hedge_needed'}
        if abs(net_exposure) > PLATFORM_CONFIG['platform_hedge_threshold']:
            hedge_size = abs(net_exposure) * 1.1
            platform_state['total_platform_hedges_btc'] += hedge_size
            platform_state['net_platform_exposure_btc'] = (
                platform_state['total_client_exposure_btc'] - platform_state['total_platform_hedges_btc']
            )
            platform_hedge = {
                'status': 'hedged',
                'hedge_size_btc': hedge_size,
                'coverage': '110%'
            }
        
        results = {
            'execution_summary': {
                'status': 'completed',
                'strategy_name': strategy['strategy_name'],
                'contracts_filled': size,
                'total_premium_client': strategy.get('total_client_cost', strategy.get('total_net_received', 0)),
                'platform_revenue': strategy.get('platform_revenue', 0),
                'execution_venues': execution_plan
            },
            'portfolio_impact': {
                'institution': strategy['portfolio_context']['institution'],
                'var_reduction': {
                    'before': strategy['portfolio_context']['var_before'],
                    'after': strategy['portfolio_context']['var_after_estimated'],
                    'reduction_pct': 75
                },
                'protection_active': True
            },
            'platform_exposure': {
                'client_positions_btc': platform_state['total_client_exposure_btc'],
                'platform_hedges_btc': platform_state['total_platform_hedges_btc'],
                'net_exposure_btc': platform_state['net_platform_exposure_btc'],
                'platform_hedge_action': platform_hedge
            }
        }
        
        return jsonify({'success': True, 'execution': results})
    except Exception as e:
        error_msg = str(e)
        print(f"❌ Execution error: {error_msg}")
        return jsonify({'success': False, 'error': error_msg}), 500

@app.route('/api/platform-exposure')
def platform_exposure():
    try:
        exposure = platform_risk_manager.calculate_net_exposure()
        return jsonify({'success': True, 'exposure': exposure})
    except Exception as e:
        error_msg = str(e)
        print(f"❌ Exposure error: {error_msg}")
        return jsonify({'success': False, 'exposure': {
            'total_client_long_btc': 0.0,
            'total_platform_hedges_btc': 0.0,
            'net_exposure_btc': 0.0,
            'hedge_coverage_ratio': 0.0
        }}), 500

if __name__ == '__main__':
    print("🎯 Atticus Professional v17.2 Starting...")
    print("   ✓ Multi-strategy pricing engine")
    print("   ✓ Smart strategy recommendations")
    print("   ✓ Risk tolerance matching")
    print("   ✓ Enhanced UI layout")
    
    port = int(os.environ.get('PORT', 5000))
    debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    
    app.run(host='0.0.0.0', port=port, debug=debug_mode)
