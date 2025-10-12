"""
ATTICUS PROFESSIONAL V17.0 - INSTITUTIONAL PORTFOLIO HEDGING PLATFORM
Fixed version with proper error handling and service initialization
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
    """Live market data with robust error handling"""
    
    def __init__(self):
        self.price_cache = None
        self.cache_time = None
        
    def get_live_btc_price(self):
        """Get live BTC price with fallback"""
        if self.price_cache and self.cache_time:
            if (datetime.now() - self.cache_time).seconds < 300:  # 5 min cache
                return self.price_cache
        
        try:
            import requests
            response = requests.get('https://api.coinbase.com/v2/exchange-rates?currency=BTC', timeout=5)
            if response.status_code == 200:
                price = float(response.json()['data']['rates']['USD'])
                if price > 0:
                    self.price_cache = price
                    self.cache_time = datetime.now()
                    return price
        except Exception as e:
            print(f"⚠️ Coinbase API error: {e}")
        
        try:
            import requests
            response = requests.get('https://api.coindesk.com/v1/bpi/currentprice/USD.json', timeout=5)
            if response.status_code == 200:
                data = response.json()
                price = float(data['bpi']['USD']['rate'].replace(',', ''))
                if price > 0:
                    self.price_cache = price
                    self.cache_time = datetime.now()
                    return price
        except Exception as e:
            print(f"⚠️ CoinDesk API error: {e}")
        
        # Fallback price
        fallback = self.price_cache if self.price_cache else 111500.0
        print(f"📊 Using fallback BTC price: ${fallback:,.2f}")
        return fallback
    
    def get_volatility(self):
        """Get BTC volatility"""
        return 0.65  # 65% annualized
    
    def get_risk_free_rate(self):
        """Get risk-free rate"""
        return 0.0475  # 4.75%

class ExchangeManager:
    """Multi-exchange integration"""
    
    def __init__(self):
        self.exchanges = {
            'deribit': {'status': 'active', 'btc_options': True, 'liquidity': 'high', 'max_order_btc': 500},
            'okx': {'status': 'active', 'btc_options': True, 'liquidity': 'medium', 'max_order_btc': 200},
            'binance': {'status': 'active', 'btc_futures': True, 'liquidity': 'high', 'max_order_btc': 1000},
            'coinbase': {'status': 'active', 'btc_futures': True, 'liquidity': 'high', 'max_order_btc': 500},
            'kraken': {'status': 'active', 'btc_futures': True, 'liquidity': 'medium', 'max_order_btc': 300}
        }
        
    def get_available_venues(self, instrument_type='btc_options'):
        """Get available exchanges for instrument type"""
        available = []
        for exchange, info in self.exchanges.items():
            if info['status'] == 'active' and info.get(instrument_type, False):
                available.append({
                    'exchange': exchange,
                    'liquidity': info['liquidity'],
                    'fees': self._get_fees(exchange),
                    'max_order': info['max_order_btc']
                })
        return available
    
    def _get_fees(self, exchange):
        """Get fee structure for exchange"""
        fees = {
            'deribit': {'maker': 0.0003, 'taker': 0.0005},
            'okx': {'maker': 0.0002, 'taker': 0.0005},
            'binance': {'maker': 0.0002, 'taker': 0.0004},
            'coinbase': {'maker': 0.004, 'taker': 0.006},
            'kraken': {'maker': 0.0002, 'taker': 0.0005}
        }
        return fees.get(exchange, {'maker': 0.001, 'taker': 0.001})
    
    def calculate_optimal_execution(self, total_size, instrument_type='btc_options'):
        """Calculate optimal execution across exchanges"""
        venues = self.get_available_venues(instrument_type)
        if not venues:
            venues = self.get_available_venues('btc_futures')
        if not venues:
            return [{'exchange': 'deribit', 'size': total_size, 'cost': total_size * 0.0005, 'liquidity': 'high'}]
        
        execution_plan = []
        remaining = total_size
        
        # Sort by liquidity then fees
        venues_sorted = sorted(venues, key=lambda x: (0 if x['liquidity'] == 'high' else 1, x['fees']['taker']))
        
        for venue in venues_sorted:
            if remaining <= 0:
                break
            
            # Allocate based on liquidity
            allocation = min(remaining, total_size * (0.6 if venue['liquidity'] == 'high' else 0.3), venue['max_order'])
            
            if allocation > 0.01:  # Minimum size
                execution_plan.append({
                    'exchange': venue['exchange'],
                    'size': round(allocation, 4),
                    'cost': allocation * venue['fees']['taker'],
                    'liquidity': venue['liquidity']
                })
                remaining -= allocation
        
        # Handle remaining size
        if remaining > 0 and execution_plan:
            execution_plan[0]['size'] += remaining
            execution_plan[0]['cost'] += remaining * venues_sorted[0]['fees']['taker']
        
        return execution_plan

class PortfolioAnalyzer:
    """Advanced portfolio analysis"""
    
    def __init__(self, market_service):
        self.market = market_service
        self.profiles = {
            'pension_fund': {
                'name': 'State Pension Fund',
                'aum': 2100000000,
                'btc_allocation_pct': 3.0,
                'risk_tolerance': 'conservative',
                'hedge_ratio_target': 0.85
            },
            'hedge_fund': {
                'name': 'Quantitative Hedge Fund',
                'aum': 450000000,
                'btc_allocation_pct': 15.0,
                'risk_tolerance': 'aggressive',
                'hedge_ratio_target': 0.60
            },
            'family_office': {
                'name': 'UHNW Family Office',
                'aum': 180000000,
                'btc_allocation_pct': 8.0,
                'risk_tolerance': 'moderate',
                'hedge_ratio_target': 0.75
            },
            'corporate_treasury': {
                'name': 'Corporate Treasury',
                'aum': 500000000,
                'btc_allocation_pct': 5.0,
                'risk_tolerance': 'conservative',
                'hedge_ratio_target': 0.90
            }
        }
    
    def analyze(self, portfolio_type=None, custom_params=None):
        """Analyze portfolio with error handling"""
        try:
            if custom_params:
                return self._analyze_custom(custom_params)
            
            profile = self.profiles.get(portfolio_type, self.profiles['pension_fund'])
            btc_price = self.market.get_live_btc_price()
            vol = self.market.get_volatility()
            
            btc_allocation = profile['aum'] * (profile['btc_allocation_pct'] / 100)
            btc_size = btc_allocation / btc_price
            
            var_1d = self._calculate_var(btc_size, btc_price, vol, 1)
            var_30d = self._calculate_var(btc_size, btc_price, vol, 30)
            
            scenarios = self._generate_scenarios(btc_size, btc_price)
            
            return {
                'profile': profile,
                'positions': {
                    'btc_size': round(btc_size, 4),
                    'btc_value': round(btc_allocation, 2),
                    'current_price': round(btc_price, 2)
                },
                'risk_metrics': {
                    'var_1d_95': round(abs(var_1d), 2),
                    'var_30d_95': round(abs(var_30d), 2),
                    'volatility': vol,
                    'max_drawdown_30pct': round(btc_allocation * 0.30, 2)
                },
                'scenarios': scenarios,
                'hedge_recommendation': {
                    'hedge_ratio': profile['hedge_ratio_target'],
                    'hedge_size_btc': round(btc_size * profile['hedge_ratio_target'], 4),
                    'strategy': 'protective_put' if profile['risk_tolerance'] == 'conservative' else 'collar'
                }
            }
        except Exception as e:
            print(f"❌ Portfolio analysis error: {e}")
            raise Exception(f"Portfolio analysis failed: {str(e)}")
    
    def _analyze_custom(self, params):
        """Analyze custom position"""
        try:
            btc_price = self.market.get_live_btc_price()
            vol = self.market.get_volatility()
            position_size = float(params.get('size', 1.0))
            position_value = position_size * btc_price
            
            var_1d = self._calculate_var(position_size, btc_price, vol, 1)
            var_30d = self._calculate_var(position_size, btc_price, vol, 30)
            scenarios = self._generate_scenarios(position_size, btc_price)
            
            return {
                'profile': {'name': 'Custom Position', 'risk_tolerance': 'moderate'},
                'positions': {
                    'btc_size': round(position_size, 4),
                    'btc_value': round(position_value, 2),
                    'current_price': round(btc_price, 2)
                },
                'risk_metrics': {
                    'var_1d_95': round(abs(var_1d), 2),
                    'var_30d_95': round(abs(var_30d), 2),
                    'volatility': vol,
                    'max_drawdown_30pct': round(position_value * 0.30, 2)
                },
                'scenarios': scenarios,
                'hedge_recommendation': {
                    'hedge_ratio': 0.80,
                    'hedge_size_btc': round(position_size * 0.80, 4),
                    'strategy': 'protective_put'
                }
            }
        except Exception as e:
            print(f"❌ Custom analysis error: {e}")
            raise Exception(f"Custom analysis failed: {str(e)}")
    
    def _calculate_var(self, size, price, vol, days):
        """Calculate Value at Risk"""
        try:
            value = size * price
            z_score = 1.645  # 95% confidence
            return value * vol * z_score * math.sqrt(days / 365)
        except:
            return 0.0
    
    def _generate_scenarios(self, size, price):
        """Generate scenario analysis"""
        try:
            value = size * price
            scenarios = []
            for pct in [-30, -20, -10, 0, 10, 20, 30]:
                new_price = price * (1 + pct/100)
                new_value = size * new_price
                scenarios.append({
                    'change_pct': pct,
                    'btc_price': round(new_price, 2),
                    'value': round(new_value, 2),
                    'pnl': round(new_value - value, 2),
                    'type': self._classify_scenario(pct)
                })
            return scenarios
        except:
            return []
    
    def _classify_scenario(self, pct):
        """Classify scenario type"""
        if pct <= -20:
            return 'stress'
        elif pct <= -10:
            return 'adverse'
        elif -10 < pct < 10:
            return 'normal'
        elif pct >= 20:
            return 'favorable'
        return 'positive'

class PricingEngine:
    """Black-Scholes pricing with platform markup"""
    
    def __init__(self, market_service):
        self.market = market_service
        self.risk_free_rate = 0.0475
    
    def price_strategy(self, strategy_type, size, current_price, strike_offset=-5):
        """Price strategy with error handling"""
        try:
            vol = self.market.get_volatility()
            T = 45 / 365.0  # 45 days to expiry
            
            if strategy_type == 'protective_put':
                return self._price_protective_put(size, current_price, vol, T, strike_offset)
            elif strategy_type == 'collar':
                return self._price_collar(size, current_price, vol, T, strike_offset)
            elif strategy_type == 'put_spread':
                return self._price_put_spread(size, current_price, vol, T, strike_offset)
            else:
                return self._price_protective_put(size, current_price, vol, T, strike_offset)
        except Exception as e:
            print(f"❌ Pricing error: {e}")
            raise Exception(f"Strategy pricing failed: {str(e)}")
    
    def _price_protective_put(self, size, S, vol, T, offset):
        """Price protective put strategy"""
        K = S * (1 + offset/100)
        put_price = self._bs_put(S, K, T, self.risk_free_rate, vol)
        
        # Calculate premium before markup
        base_premium = size * put_price
        
        # Apply platform markup
        markup_amount = base_premium * (PLATFORM_CONFIG['markup_percentage'] / 100)
        markup_amount = max(markup_amount, PLATFORM_CONFIG['min_markup_dollars'] * size)
        
        total_premium_with_markup = base_premium + markup_amount
        exec_fee = PLATFORM_CONFIG['execution_fee']
        
        greeks = self._calc_greeks(S, K, T, self.risk_free_rate, vol, 'put')
        
        return {
            'strategy_type': 'protective_put',
            'strategy_name': 'Protective Put Strategy',
            'position_size': size,
            'strike_price': round(K, 2),
            'premium_per_contract_base': round(put_price, 2),
            'premium_per_contract_client': round((total_premium_with_markup + exec_fee) / size, 2),
            'base_premium_total': round(base_premium, 2),
            'platform_markup': round(markup_amount, 2),
            'execution_fee': exec_fee,
            'total_client_cost': round(total_premium_with_markup + exec_fee, 2),
            'platform_revenue': round(markup_amount + exec_fee, 2),
            'cost_percentage': round(((total_premium_with_markup + exec_fee) / (size * S)) * 100, 2),
            'max_loss': round(abs(S - K) * size + total_premium_with_markup + exec_fee, 2),
            'breakeven': round(K - ((total_premium_with_markup + exec_fee) / size), 2),
            'protection_level': round(K, 2),
            'time_to_expiry_days': 45,
            'greeks': greeks
        }
    
    def _price_collar(self, size, S, vol, T, offset):
        """Price collar strategy"""
        put_strike = S * (1 + offset/100)
        call_strike = S * 1.15  # 15% OTM call
        
        put_price = self._bs_put(S, put_strike, T, self.risk_free_rate, vol)
        call_price = self._bs_call(S, call_strike, T, self.risk_free_rate, vol)
        
        base_premium = size * (put_price - call_price)
        markup_amount = abs(base_premium) * (PLATFORM_CONFIG['markup_percentage'] / 100)
        total_premium = base_premium + markup_amount if base_premium >= 0 else base_premium - markup_amount
        exec_fee = PLATFORM_CONFIG['execution_fee']
        
        return {
            'strategy_type': 'collar',
            'strategy_name': 'Collar Strategy',
            'position_size': size,
            'put_strike': round(put_strike, 2),
            'call_strike': round(call_strike, 2),
            'net_premium_base': round(base_premium, 2),
            'platform_markup': round(markup_amount, 2),
            'execution_fee': exec_fee,
            'total_client_cost': round(abs(total_premium) + exec_fee, 2),
            'platform_revenue': round(markup_amount + exec_fee, 2),
            'cost_percentage': round(((abs(total_premium) + exec_fee) / (size * S)) * 100, 2),
            'max_loss': round(abs(S - put_strike) * size + abs(total_premium) + exec_fee, 2),
            'upside_cap': round(call_strike, 2),
            'protection_level': round(put_strike, 2),
            'time_to_expiry_days': 45
        }
    
    def _price_put_spread(self, size, S, vol, T, offset):
        """Price put spread strategy"""
        long_strike = S * (1 + offset/100)
        short_strike = S * 0.90  # 10% OTM short put
        
        long_put = self._bs_put(S, long_strike, T, self.risk_free_rate, vol)
        short_put = self._bs_put(S, short_strike, T, self.risk_free_rate, vol)
        
        base_premium = size * (long_put - short_put)
        markup_amount = base_premium * (PLATFORM_CONFIG['markup_percentage'] / 100)
        total_premium = base_premium + markup_amount
        exec_fee = PLATFORM_CONFIG['execution_fee']
        
        return {
            'strategy_type': 'put_spread',
            'strategy_name': 'Put Spread Strategy',
            'position_size': size,
            'long_strike': round(long_strike, 2),
            'short_strike': round(short_strike, 2),
            'net_premium_base': round(base_premium, 2),
            'platform_markup': round(markup_amount, 2),
            'execution_fee': exec_fee,
            'total_client_cost': round(total_premium + exec_fee, 2),
            'platform_revenue': round(markup_amount + exec_fee, 2),
            'cost_percentage': round(((total_premium + exec_fee) / (size * S)) * 100, 2),
            'max_loss': round(total_premium + exec_fee, 2),
            'breakeven': round(long_strike - ((total_premium + exec_fee) / size), 2),
            'protection_level': round(long_strike, 2),
            'time_to_expiry_days': 45
        }
    
    def _bs_put(self, S, K, T, r, sigma):
        """Black-Scholes put option price"""
        try:
            if T <= 0:
                return max(0, K - S)
            d1 = (math.log(S/K) + (r + 0.5*sigma**2)*T) / (sigma*math.sqrt(T))
            d2 = d1 - sigma*math.sqrt(T)
            return K*math.exp(-r*T)*self._norm_cdf(-d2) - S*self._norm_cdf(-d1)
        except:
            return max(0, K - S)
    
    def _bs_call(self, S, K, T, r, sigma):
        """Black-Scholes call option price"""
        try:
            if T <= 0:
                return max(0, S - K)
            d1 = (math.log(S/K) + (r + 0.5*sigma**2)*T) / (sigma*math.sqrt(T))
            d2 = d1 - sigma*math.sqrt(T)
            return S*self._norm_cdf(d1) - K*math.exp(-r*T)*self._norm_cdf(d2)
        except:
            return max(0, S - K)
    
    def _calc_greeks(self, S, K, T, r, sigma, opt_type):
        """Calculate option Greeks"""
        try:
            if T <= 0:
                return {'delta': 0, 'gamma': 0, 'vega': 0, 'theta': 0}
            d1 = (math.log(S/K) + (r + 0.5*sigma**2)*T) / (sigma*math.sqrt(T))
            delta = -self._norm_cdf(-d1) if opt_type == 'put' else self._norm_cdf(d1)
            gamma = self._norm_pdf(d1) / (S*sigma*math.sqrt(T))
            vega = S * self._norm_pdf(d1) * math.sqrt(T)
            theta = -S*self._norm_pdf(d1)*sigma/(2*math.sqrt(T))
            return {
                'delta': round(delta, 4),
                'gamma': round(gamma, 6),
                'vega': round(vega, 2),
                'theta': round(theta, 2)
            }
        except:
            return {'delta': 0, 'gamma': 0, 'vega': 0, 'theta': 0}
    
    def _norm_cdf(self, x):
        """Standard normal cumulative distribution function"""
        return 0.5 * (1 + math.erf(x / math.sqrt(2)))
    
    def _norm_pdf(self, x):
        """Standard normal probability density function"""
        return math.exp(-0.5*x*x) / math.sqrt(2*math.pi)

class PlatformRiskManager:
    """Manages platform's own risk exposure"""
    
    def __init__(self, exchange_mgr):
        self.exchange_mgr = exchange_mgr
    
    def calculate_net_exposure(self):
        """Calculate platform's net exposure across all clients"""
        try:
            return {
                'total_client_long_btc': platform_state['total_client_exposure_btc'],
                'total_platform_hedges_btc': platform_state['total_platform_hedges_btc'],
                'net_exposure_btc': platform_state['net_platform_exposure_btc'],
                'hedge_coverage_ratio': (platform_state['total_platform_hedges_btc'] / platform_state['total_client_exposure_btc'] 
                                        if platform_state['total_client_exposure_btc'] > 0 else 0),
                'requires_hedging': abs(platform_state['net_platform_exposure_btc']) > PLATFORM_CONFIG['platform_hedge_threshold'],
                'active_institutions': len(platform_state['active_institutions']),
                'total_premium_collected': platform_state['total_premium_collected'],
                'total_hedge_cost': platform_state['total_hedge_cost'],
                'net_revenue': platform_state['total_premium_collected'] - platform_state['total_hedge_cost']
            }
        except Exception as e:
            print(f"❌ Platform exposure calculation error: {e}")
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

# Initialize services globally
market_service = None
portfolio_analyzer = None
pricing_engine = None
exchange_manager = None
platform_risk_manager = None

def initialize_services():
    """Initialize all services with error handling"""
    global market_service, portfolio_analyzer, pricing_engine, exchange_manager, platform_risk_manager
    try:
        print("🏛️ Initializing Atticus Professional v17.0...")
        
        market_service = MarketDataService()
        print("✅ Market data service initialized")
        
        exchange_manager = ExchangeManager()
        print("✅ Exchange manager initialized")
        
        portfolio_analyzer = PortfolioAnalyzer(market_service)
        print("✅ Portfolio analyzer initialized")
        
        pricing_engine = PricingEngine(market_service)
        print("✅ Pricing engine initialized")
        
        platform_risk_manager = PlatformRiskManager(exchange_manager)
        print("✅ Platform risk manager initialized")
        
        print("🎯 All services ready!")
        return True
    except Exception as e:
        print(f"❌ Service initialization failed: {e}")
        traceback.print_exc()
        return False

# Routes with error handling
@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')

@app.route('/api/health')
def health():
    """Health check endpoint"""
    try:
        return jsonify({
            'status': 'healthy',
            'version': 'v17.0',
            'timestamp': datetime.now().isoformat(),
            'services': {
                'market_data': 'operational' if market_service else 'offline',
                'portfolio_analyzer': 'operational' if portfolio_analyzer else 'offline',
                'pricing_engine': 'operational' if pricing_engine else 'offline',
                'exchange_manager': 'operational' if exchange_manager else 'offline',
                'platform_risk_manager': 'operational' if platform_risk_manager else 'offline'
            }
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/market-data')
def market_data():
    """Get current market conditions"""
    try:
        if not market_service:
            return jsonify({'error': 'Market service not initialized'}), 500
            
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
        print(f"❌ Market data API error: {e}")
        traceback.print_exc()
        return jsonify({'error': f'Market data error: {str(e)}'}), 500

@app.route('/api/analyze-portfolio', methods=['POST'])
def analyze_portfolio():
    """Analyze portfolio endpoint"""
    try:
        if not portfolio_analyzer:
            return jsonify({'success': False, 'error': 'Portfolio analyzer not initialized'}), 500
        
        data = request.get_json() or {}
        portfolio_type = data.get('type', 'pension_fund')
        custom_params = data.get('custom_params')
        
        print(f"📊 Analyzing portfolio: {portfolio_type}, custom: {custom_params}")
        
        analysis = portfolio_analyzer.analyze(portfolio_type, custom_params)
        session['portfolio_analysis'] = analysis
        
        print(f"✅ Analysis completed for {analysis['profile']['name']}")
        
        return jsonify({'success': True, 'analysis': analysis})
    except Exception as e:
        error_msg = f"Portfolio analysis error: {str(e)}"
        print(f"❌ {error_msg}")
        traceback.print_exc()
        return jsonify({'success': False, 'error': error_msg}), 500

@app.route('/api/generate-strategy', methods=['POST'])
def generate_strategy():
    """Generate strategy endpoint"""
    try:
        if not pricing_engine:
            return jsonify({'success': False, 'error': 'Pricing engine not initialized'}), 500
            
        analysis = session.get('portfolio_analysis')
        if not analysis:
            return jsonify({'success': False, 'error': 'No portfolio analysis found'}), 400
        
        data = request.get_json() or {}
        strategy_type = data.get('strategy_type', analysis['hedge_recommendation']['strategy'])
        
        positions = analysis['positions']
        hedge_rec = analysis['hedge_recommendation']
        
        print(f"💰 Pricing strategy: {strategy_type} for {hedge_rec['hedge_size_btc']} BTC")
        
        strategy = pricing_engine.price_strategy(
            strategy_type,
            hedge_rec['hedge_size_btc'],
            positions['current_price'],
            -5  # 5% OTM
        )
        
        # Add portfolio context
        strategy['portfolio_context'] = {
            'institution': analysis['profile']['name'],
            'position_size_btc': positions['btc_size'],
            'var_before': analysis['risk_metrics']['var_30d_95'],
            'var_after_estimated': analysis['risk_metrics']['var_30d_95'] * 0.25  # 75% reduction
        }
        
        session['selected_strategy'] = strategy
        print(f"✅ Strategy priced: {strategy['strategy_name']}")
        
        return jsonify({'success': True, 'strategy': strategy})
    except Exception as e:
        error_msg = f"Strategy generation error: {str(e)}"
        print(f"❌ {error_msg}")
        traceback.print_exc()
        return jsonify({'success': False, 'error': error_msg}), 500

@app.route('/api/execute-strategy', methods=['POST'])
def execute_strategy():
    """Execute strategy endpoint"""
    try:
        if not exchange_manager or not platform_risk_manager:
            return jsonify({'success': False, 'error': 'Services not initialized'}), 500
            
        strategy = session.get('selected_strategy')
        if not strategy:
            return jsonify({'success': False, 'error': 'No strategy selected'}), 400
        
        # Get execution plan
        size = strategy['position_size']
        print(f"🔄 Executing {size} BTC strategy")
        
        execution_plan = exchange_manager.calculate_optimal_execution(size, 'btc_options')
        
        # Simulate execution delay
        time.sleep(1)
        
        # Update platform state
        platform_state['total_client_exposure_btc'] += size
        platform_state['total_premium_collected'] += strategy.get('platform_revenue', 0)
        platform_state['net_platform_exposure_btc'] = (
            platform_state['total_client_exposure_btc'] - platform_state['total_platform_hedges_btc']
        )
        
        # Platform hedges its own exposure
        net_exposure = platform_state['net_platform_exposure_btc']
        platform_hedge = {'status': 'no_hedge_needed', 'exposure': net_exposure}
        
        if abs(net_exposure) > PLATFORM_CONFIG['platform_hedge_threshold']:
            hedge_size = abs(net_exposure) * PLATFORM_CONFIG['hedge_reserve_ratio']
            hedge_plan = exchange_manager.calculate_optimal_execution(hedge_size, 'btc_futures')
            hedge_cost = sum(venue['cost'] for venue in hedge_plan)
            
            platform_state['total_platform_hedges_btc'] += hedge_size
            platform_state['total_hedge_cost'] += hedge_cost
            platform_state['net_platform_exposure_btc'] = (
                platform_state['total_client_exposure_btc'] - platform_state['total_platform_hedges_btc']
            )
            
            platform_hedge = {
                'status': 'hedged',
                'hedge_size_btc': round(hedge_size, 4),
                'execution_plan': hedge_plan,
                'estimated_cost': round(hedge_cost, 4),
                'coverage': f"{PLATFORM_CONFIG['hedge_reserve_ratio']*100}%"
            }
        
        results = {
            'execution_summary': {
                'status': 'completed',
                'contracts_filled': size,
                'total_premium_client': strategy.get('total_client_cost', 0),
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
        
        print(f"✅ Strategy executed successfully")
        return jsonify({'success': True, 'execution': results})
    except Exception as e:
        error_msg = f"Strategy execution error: {str(e)}"
        print(f"❌ {error_msg}")
        traceback.print_exc()
        return jsonify({'success': False, 'error': error_msg}), 500

@app.route('/api/platform-exposure')
def platform_exposure():
    """Get platform exposure metrics"""
    try:
        if not platform_risk_manager:
            return jsonify({'success': False, 'error': 'Platform risk manager not initialized'}), 500
            
        exposure = platform_risk_manager.calculate_net_exposure()
        return jsonify({'success': True, 'exposure': exposure})
    except Exception as e:
        error_msg = f"Platform exposure error: {str(e)}"
        print(f"❌ {error_msg}")
        traceback.print_exc()
        return jsonify({'success': False, 'error': error_msg}), 500

if __name__ == '__main__':
    if initialize_services():
        print("🎯 Atticus Professional v17.0 Ready!")
        print("   ✓ Portfolio Analysis with VaR")
        print("   ✓ Real Black-Scholes Pricing + 2.5% Markup")
        print("   ✓ Platform Net Exposure Hedging")
        print("   ✓ Multi-Exchange Routing")
        print("   ✓ Comprehensive Error Handling")
        port = int(os.environ.get('PORT', 5000))
        app.run(host='0.0.0.0', port=port, debug=True)
    else:
        print("❌ Failed to initialize services. Check logs above.")
