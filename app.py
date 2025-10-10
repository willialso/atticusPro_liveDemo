"""
ATTICUS PROFESSIONAL - COMPLETE FLASK BACKEND
✅ All pricing logic and strategy generation complete
✅ Professional API endpoints for frontend
✅ Complete institutional options strategies
"""
from flask import Flask, render_template, jsonify, request, session
import requests
import time
import random
import math
from datetime import datetime, timedelta
import os

app = Flask(__name__)
app.secret_key = 'atticus_professional_demo_key_2025'

# COMPLETE PRICING FUNCTIONS
def get_live_btc_price():
    prices = []
    
    try:
        response = requests.get("https://api.coinbase.com/v2/exchange-rates?currency=BTC", timeout=5)
        if response.status_code == 200:
            data = response.json()
            price = float(data['data']['rates']['USD'])
            if 10000 < price < 500000:
                prices.append(price)
    except:
        pass
    
    try:
        response = requests.get("https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd", timeout=5)
        if response.status_code == 200:
            data = response.json()
            price = float(data['bitcoin']['usd'])
            if 10000 < price < 500000:
                prices.append(price)
    except:
        pass
    
    try:
        response = requests.get("https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT", timeout=5)
        if response.status_code == 200:
            data = response.json()
            price = float(data['price'])
            if 10000 < price < 500000:
                prices.append(price)
    except:
        pass
    
    if prices:
        return sum(prices) / len(prices)
    else:
        return None

def get_live_market_conditions():
    try:
        response = requests.get("https://api.coingecko.com/api/v3/coins/bitcoin/market_chart?vs_currency=usd&days=30&interval=daily", timeout=10)
        if response.status_code == 200:
            data = response.json()
            prices = [price[1] for price in data['prices']]
            
            returns = []
            for i in range(1, len(prices)):
                returns.append(math.log(prices[i] / prices[i-1]))
            
            if returns:
                volatility = math.sqrt(sum(r**2 for r in returns) / len(returns)) * math.sqrt(365)
            else:
                volatility = 0.65
        else:
            volatility = 0.65
    except:
        volatility = 0.65
    
    current_price = get_live_btc_price()
    if current_price:
        try:
            response = requests.get("https://api.coingecko.com/api/v3/coins/bitcoin/market_chart?vs_currency=usd&days=7&interval=daily", timeout=5)
            if response.status_code == 200:
                data = response.json()
                week_ago_price = data['prices'][0][1]
                price_change_7d = (current_price - week_ago_price) / week_ago_price
            else:
                price_change_7d = 0
        except:
            price_change_7d = 0
    else:
        price_change_7d = 0
    
    return {
        'implied_volatility': volatility,
        'price_trend_7d': price_change_7d,
        'market_regime': 'bullish' if price_change_7d > 0.05 else 'bearish' if price_change_7d < -0.05 else 'neutral',
        'high_volatility': volatility > 0.8
    }

def calculate_live_options_pricing(current_price, strike_ratio, days_to_expiry, option_type='put'):
    market_conditions = get_live_market_conditions()
    risk_free_rate = 0.045
    base_iv = market_conditions['implied_volatility']
    if market_conditions['high_volatility']:
        base_iv *= 1.1
    
    T = days_to_expiry / 365.0
    K = current_price * strike_ratio
    
    if option_type == 'put':
        moneyness = K / current_price
        time_value = current_price * base_iv * math.sqrt(T) * 0.4
        intrinsic_value = max(K - current_price, 0)
        premium = intrinsic_value + time_value * moneyness
    else:
        moneyness = current_price / K
        time_value = current_price * base_iv * math.sqrt(T) * 0.4
        intrinsic_value = max(current_price - K, 0)
        premium = intrinsic_value + time_value * moneyness
    
    return {
        'premium': premium,
        'strike_price': K,
        'implied_volatility': base_iv,
        'time_to_expiry': T,
        'intrinsic_value': intrinsic_value,
        'time_value': premium - intrinsic_value
    }

def calculate_strategy_outcomes(strategy, current_price):
    pricing = strategy['pricing']
    strategy_name = strategy['strategy_name']
    target_btc = strategy['target_exposure']
    
    if strategy_name == 'protective_put':
        strike = pricing['strike_price']
        premium = abs(pricing['total_premium'])
        breakeven = current_price - (premium / target_btc)
        
        return {
            'scenarios': [
                {
                    'condition': f'BTC above ${breakeven:,.0f}',
                    'outcome': 'Profitable position',
                    'details': f'Long position profits minus ${premium:,.0f} insurance cost'
                },
                {
                    'condition': f'BTC between ${breakeven:,.0f} - ${strike:,.0f}',
                    'outcome': 'Partial loss',
                    'details': f'Loss limited to insurance cost: ${premium:,.0f}'
                },
                {
                    'condition': f'BTC below ${strike:,.0f}',
                    'outcome': 'Full protection active',
                    'details': f'Maximum loss capped at ${premium:,.0f}'
                }
            ],
            'max_loss': premium,
            'max_profit': 'Unlimited upside potential',
            'breakeven_price': breakeven
        }
    
    elif strategy_name == 'put_spread':
        long_strike = pricing['long_strike']
        short_strike = pricing['short_strike']
        premium = abs(pricing['total_premium'])
        breakeven = current_price - (premium / target_btc)
        
        return {
            'scenarios': [
                {
                    'condition': f'BTC above ${breakeven:,.0f}',
                    'outcome': 'Profitable position',
                    'details': f'Long position profits minus spread cost'
                },
                {
                    'condition': f'BTC between ${long_strike:,.0f} - ${breakeven:,.0f}',
                    'outcome': 'Limited protection',
                    'details': f'Protected down to ${long_strike:,.0f}'
                },
                {
                    'condition': f'BTC below ${short_strike:,.0f}',
                    'outcome': 'Maximum protection',
                    'details': f'Loss capped at ${premium + (current_price - long_strike) * target_btc:,.0f}'
                }
            ],
            'max_loss': premium,
            'max_profit': 'Unlimited upside potential',
            'breakeven_price': breakeven
        }
    
    elif strategy_name == 'covered_call':
        strike = pricing['strike_price']
        income = abs(pricing['total_premium'])
        
        return {
            'scenarios': [
                {
                    'condition': f'BTC below ${current_price:,.0f}',
                    'outcome': 'Enhanced returns',
                    'details': f'Keep ${income:,.0f} income + any BTC appreciation'
                },
                {
                    'condition': f'BTC between ${current_price:,.0f} - ${strike:,.0f}',
                    'outcome': 'Best case scenario',
                    'details': f'Maximum profit: BTC gains + ${income:,.0f} income'
                },
                {
                    'condition': f'BTC above ${strike:,.0f}',
                    'outcome': 'Capped upside',
                    'details': f'BTC called away, total return capped'
                }
            ],
            'max_loss': 'Unlimited downside (offset by income)',
            'max_profit': f'${(strike - current_price) * target_btc + income:,.0f}',
            'breakeven_price': current_price - (income / target_btc)
        }
    
    elif strategy_name == 'cash_secured_put':
        strike = pricing['strike_price']
        income = abs(pricing['total_premium'])
        
        return {
            'scenarios': [
                {
                    'condition': f'BTC above ${strike:,.0f}',
                    'outcome': 'Keep premium income',
                    'details': f'Collect ${income:,.0f} income, no BTC purchase required'
                },
                {
                    'condition': f'BTC at ${strike:,.0f}',
                    'outcome': 'Break-even assignment',
                    'details': f'Buy BTC at ${strike:,.0f}, effective cost ${strike - income/target_btc:,.0f}/BTC'
                },
                {
                    'condition': f'BTC below ${strike:,.0f}',
                    'outcome': 'Assigned at discount',
                    'details': f'Buy BTC below market, net cost ${strike - income/target_btc:,.0f}/BTC'
                }
            ],
            'max_loss': f'${strike * target_btc - income:,.0f} if BTC goes to zero',
            'max_profit': f'${income:,.0f} if BTC stays above ${strike:,.0f}',
            'breakeven_price': strike - (income / target_btc)
        }
    
    elif strategy_name == 'protective_call':
        strike = pricing['strike_price']
        premium = abs(pricing['total_premium'])
        breakeven = current_price + (premium / target_btc)
        
        return {
            'scenarios': [
                {
                    'condition': f'BTC below ${breakeven:,.0f}',
                    'outcome': 'Profitable short',
                    'details': f'Short position profits minus ${premium:,.0f} insurance cost'
                },
                {
                    'condition': f'BTC between ${breakeven:,.0f} - ${strike:,.0f}',
                    'outcome': 'Partial loss',
                    'details': f'Loss limited to insurance cost: ${premium:,.0f}'
                },
                {
                    'condition': f'BTC above ${strike:,.0f}',
                    'outcome': 'Full protection active',
                    'details': f'Maximum loss capped at ${premium:,.0f}'
                }
            ],
            'max_loss': premium,
            'max_profit': 'Unlimited downside potential',
            'breakeven_price': breakeven
        }
    
    return {
        'scenarios': [],
        'max_loss': abs(pricing['total_premium']),
        'max_profit': 'Strategy dependent',
        'breakeven_price': current_price
    }

def generate_dynamic_strategies(net_btc, current_price):
    if not current_price:
        return []
    
    market_conditions = get_live_market_conditions()
    contracts_needed = int(abs(net_btc))
    
    strategies = []
    
    # PROTECTIVE PUT STRATEGY - HIGH PRIORITY FOR LONG POSITIONS
    if net_btc > 0:
        put_data = calculate_live_options_pricing(current_price, 0.95, 7, 'put')
        strategies.append({
            'strategy_name': 'protective_put',
            'display_name': 'Protective Put (Downside Protection)',
            'target_exposure': abs(net_btc),
            'priority': 'high',
            'rationale': f'Complete downside protection for {abs(net_btc):.1f} BTC long position',
            'pricing': {
                'btc_spot_price': current_price,
                'contracts_needed': contracts_needed,
                'strike_price': put_data['strike_price'],
                'premium_per_contract': put_data['premium'],
                'total_premium': contracts_needed * put_data['premium'],
                'implied_volatility': put_data['implied_volatility'],
                'days_to_expiry': 7,
                'expiry_date': (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d"),
                'option_type': 'European Put Options',
                'cost_as_pct': (contracts_needed * put_data['premium']) / (abs(net_btc) * current_price) * 100
            }
        })
    
    # PUT SPREAD STRATEGY - MEDIUM PRIORITY FOR LONG POSITIONS
    if net_btc > 0:
        long_put = calculate_live_options_pricing(current_price, 0.95, 14, 'put')
        short_put = calculate_live_options_pricing(current_price, 0.85, 14, 'put')
        net_premium = long_put['premium'] - short_put['premium']
        
        strategies.append({
            'strategy_name': 'put_spread',
            'display_name': 'Put Spread (Cost-Efficient Protection)',
            'target_exposure': abs(net_btc),
            'priority': 'medium',
            'rationale': f'Cost-efficient protection with limited downside coverage',
            'pricing': {
                'btc_spot_price': current_price,
                'contracts_needed': contracts_needed,
                'long_strike': long_put['strike_price'],
                'short_strike': short_put['strike_price'],
                'long_premium': long_put['premium'],
                'short_premium': short_put['premium'],
                'total_premium': contracts_needed * net_premium,
                'implied_volatility': long_put['implied_volatility'],
                'days_to_expiry': 14,
                'expiry_date': (datetime.now() + timedelta(days=14)).strftime("%Y-%m-%d"),
                'option_type': 'Put Spread (Long 95% / Short 85%)',
                'cost_as_pct': (contracts_needed * net_premium) / (abs(net_btc) * current_price) * 100
            }
        })
    
    # COVERED CALL STRATEGY - INCOME GENERATION FOR LONG POSITIONS
    if net_btc > 0:
        call_data = calculate_live_options_pricing(current_price, 1.10, 30, 'call')
        strategies.append({
            'strategy_name': 'covered_call',
            'display_name': 'Covered Call (Income Generation)',
            'target_exposure': abs(net_btc),
            'priority': 'medium' if market_conditions['market_regime'] == 'neutral' else 'low',
            'rationale': f'Generate income from {abs(net_btc):.1f} BTC long position - collect premium',
            'pricing': {
                'btc_spot_price': current_price,
                'contracts_needed': contracts_needed,
                'strike_price': call_data['strike_price'],
                'premium_per_contract': call_data['premium'],
                'total_premium': -contracts_needed * call_data['premium'],
                'implied_volatility': call_data['implied_volatility'],
                'days_to_expiry': 30,
                'expiry_date': (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d"),
                'option_type': 'Covered Call (Sell 110% Calls)',
                'cost_as_pct': abs(contracts_needed * call_data['premium']) / (abs(net_btc) * current_price) * 100
            }
        })
    
    # CASH SECURED PUT STRATEGY - INCOME GENERATION
    if market_conditions['market_regime'] in ['neutral', 'bullish']:
        put_data = calculate_live_options_pricing(current_price, 0.90, 21, 'put')
        
        strategies.append({
            'strategy_name': 'cash_secured_put',
            'display_name': 'Cash Secured Put (Income Generation)',
            'target_exposure': abs(net_btc),
            'priority': 'medium' if market_conditions['market_regime'] == 'bullish' else 'low',
            'rationale': f'Generate income by selling puts - ready to buy BTC at discount',
            'pricing': {
                'btc_spot_price': current_price,
                'contracts_needed': contracts_needed,
                'strike_price': put_data['strike_price'],
                'premium_per_contract': put_data['premium'],
                'total_premium': -contracts_needed * put_data['premium'],
                'cash_required': abs(net_btc) * put_data['strike_price'],
                'implied_volatility': put_data['implied_volatility'],
                'days_to_expiry': 21,
                'expiry_date': (datetime.now() + timedelta(days=21)).strftime("%Y-%m-%d"),
                'option_type': 'Cash-Secured Put (Sell 90% Puts)',
                'cost_as_pct': abs(contracts_needed * put_data['premium']) / (abs(net_btc) * current_price) * 100
            }
        })
    
    # PROTECTIVE CALL STRATEGY - HIGH PRIORITY FOR SHORT POSITIONS
    if net_btc < 0:
        call_data = calculate_live_options_pricing(current_price, 1.05, 7, 'call')
        strategies.append({
            'strategy_name': 'protective_call',
            'display_name': 'Protective Call (Short Protection)',
            'target_exposure': abs(net_btc),
            'priority': 'high',
            'rationale': f'Protect {abs(net_btc):.1f} BTC short position against price increases',
            'pricing': {
                'btc_spot_price': current_price,
                'contracts_needed': contracts_needed,
                'strike_price': call_data['strike_price'],
                'premium_per_contract': call_data['premium'],
                'total_premium': contracts_needed * call_data['premium'],
                'implied_volatility': call_data['implied_volatility'],
                'days_to_expiry': 7,
                'expiry_date': (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d"),
                'option_type': 'European Call Options',
                'cost_as_pct': (contracts_needed * call_data['premium']) / (abs(net_btc) * current_price) * 100
            }
        })
    
    # SORT BY PRIORITY
    priority_order = {'high': 3, 'medium': 2, 'low': 1}
    strategies.sort(key=lambda x: priority_order[x['priority']], reverse=True)
    
    return strategies

# FLASK ROUTES
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/market-data')
def market_data():
    current_price = get_live_btc_price()
    market_conditions = get_live_market_conditions()
    
    if current_price:
        return jsonify({
            'success': True,
            'btc_price': current_price,
            'market_conditions': market_conditions
        })
    else:
        return jsonify({'success': False, 'error': 'Unable to fetch price'})

@app.route('/api/generate-portfolio', methods=['POST'])
def generate_portfolio():
    fund_type = request.json.get('fund_type')
    current_price = get_live_btc_price()
    
    if not current_price:
        return jsonify({'success': False, 'error': 'Unable to fetch BTC price'})
    
    if "Small" in fund_type:
        btc_size = 2000000 / current_price
        portfolio = {
            'aum': 38000000,
            'total_btc_size': btc_size,
            'net_btc_exposure': btc_size,
            'total_current_value': btc_size * current_price,
            'total_pnl': btc_size * current_price * 0.15,
            'current_btc_price': current_price
        }
    else:
        btc_size = 8500000 / current_price
        portfolio = {
            'aum': 128000000,
            'total_btc_size': btc_size,
            'net_btc_exposure': btc_size,
            'total_current_value': btc_size * current_price,
            'total_pnl': btc_size * current_price * 0.18,
            'current_btc_price': current_price
        }
    
    session['portfolio'] = portfolio
    
    return jsonify({
        'success': True,
        'portfolio': portfolio
    })

@app.route('/api/create-custom-portfolio', methods=['POST'])
def create_custom_portfolio():
    positions = request.json.get('positions', [])
    current_price = get_live_btc_price()
    
    if not current_price or not positions:
        return jsonify({'success': False, 'error': 'Invalid data'})
    
    total_long = sum(pos['btc_amount'] for pos in positions if pos['position_type'] == 'Long')
    total_short = sum(pos['btc_amount'] for pos in positions if pos['position_type'] == 'Short')
    net_btc = total_long - total_short
    total_value = (total_long + total_short) * current_price
    
    portfolio = {
        'aum': abs(net_btc) * current_price * 4,
        'total_btc_size': abs(net_btc),
        'net_btc_exposure': net_btc,
        'gross_btc_exposure': total_long + total_short,
        'total_current_value': total_value,
        'total_pnl': total_value * 0.08,
        'current_btc_price': current_price,
        'custom_positions': positions
    }
    
    session['portfolio'] = portfolio
    
    return jsonify({
        'success': True,
        'portfolio': portfolio
    })

@app.route('/api/generate-strategies', methods=['POST'])
def generate_strategies_api():
    portfolio = session.get('portfolio')
    if not portfolio:
        return jsonify({'success': False, 'error': 'No portfolio found'})
    
    net_btc = portfolio['net_btc_exposure']
    current_price = portfolio['current_btc_price']
    
    strategies = generate_dynamic_strategies(net_btc, current_price)
    session['strategies'] = strategies
    
    return jsonify({
        'success': True,
        'strategies': strategies
    })

@app.route('/api/execute-strategy', methods=['POST'])
def execute_strategy():
    strategy_index = request.json.get('strategy_index')
    strategies = session.get('strategies', [])
    portfolio = session.get('portfolio')
    
    if not portfolio or strategy_index >= len(strategies):
        return jsonify({'success': False, 'error': 'Invalid strategy or portfolio'})
    
    selected_strategy = strategies[strategy_index]
    
    # Calculate outcomes
    outcomes = calculate_strategy_outcomes(selected_strategy, portfolio['current_btc_price'])
    
    # Simulate execution
    execution_data = {
        'execution_time': random.randint(12, 28),
        'timestamp': datetime.now().isoformat(),
        'status': 'executed',
        'strategy': selected_strategy,
        'outcomes': outcomes
    }
    
    return jsonify({
        'success': True,
        'execution': execution_data
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=False)
