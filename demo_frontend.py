"""
ATTICUS PROFESSIONAL - STREAMLIT-NATIVE PROFESSIONAL VERSION
✅ Works with Streamlit's layout system instead of fighting it
✅ Uses Streamlit components properly for consistent rendering
✅ Professional presentation within Streamlit constraints
✅ Maintains all real-time pricing functionality
"""
import streamlit as st
import requests
import time
import random
from datetime import datetime, timedelta
import os
import math

# Page config with wide layout
st.set_page_config(
    page_title="Atticus Professional - Portfolio Protection Demo",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Session state initialization (UNCHANGED)
def ensure_session_state():
    required_keys = {
        'demo_step': 1,
        'portfolio': None,
        'strategies': None,
        'selected_strategy': None,
        'execution_data': None,
        'custom_positions': [],
        'portfolio_source': None,
        'current_page': 'portfolio',
        'strategies_generated': False,
        'strategy_selected': False,
        'show_intro': True
    }
    
    for key, default_value in required_keys.items():
        if key not in st.session_state:
            st.session_state[key] = default_value

ensure_session_state()

# ALL PRICING FUNCTIONS UNCHANGED
@st.cache_data(ttl=30)
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

@st.cache_data(ttl=300)
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
    pricing = strategy['pricing']['live_pricing']
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
    
    if net_btc > 0:
        put_data = calculate_live_options_pricing(current_price, 0.95, 7, 'put')
        strategies.append({
            'strategy_name': 'protective_put',
            'target_exposure': abs(net_btc),
            'priority': 'high',
            'rationale': f'Complete downside protection for {abs(net_btc):.1f} BTC long position',
            'pricing': {
                'live_pricing': {
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
            }
        })
    
    if net_btc > 0:
        long_put = calculate_live_options_pricing(current_price, 0.95, 14, 'put')
        short_put = calculate_live_options_pricing(current_price, 0.85, 14, 'put')
        net_premium = long_put['premium'] - short_put['premium']
        
        strategies.append({
            'strategy_name': 'put_spread',
            'target_exposure': abs(net_btc),
            'priority': 'medium',
            'rationale': f'Cost-efficient protection with limited downside coverage',
            'pricing': {
                'live_pricing': {
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
            }
        })
    
    if net_btc > 0:
        call_data = calculate_live_options_pricing(current_price, 1.10, 30, 'call')
        strategies.append({
            'strategy_name': 'covered_call',
            'target_exposure': abs(net_btc),
            'priority': 'medium' if market_conditions['market_regime'] == 'neutral' else 'low',
            'rationale': f'Generate income from {abs(net_btc):.1f} BTC long position - collect premium',
            'pricing': {
                'live_pricing': {
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
            }
        })
    
    if market_conditions['market_regime'] in ['neutral', 'bullish']:
        put_data = calculate_live_options_pricing(current_price, 0.90, 21, 'put')
        
        strategies.append({
            'strategy_name': 'cash_secured_put',
            'target_exposure': abs(net_btc),
            'priority': 'medium' if market_conditions['market_regime'] == 'bullish' else 'low',
            'rationale': f'Generate income by selling puts - ready to buy BTC at discount',
            'pricing': {
                'live_pricing': {
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
            }
        })
    
    if net_btc < 0:
        call_data = calculate_live_options_pricing(current_price, 1.05, 7, 'call')
        strategies.append({
            'strategy_name': 'protective_call',
            'target_exposure': abs(net_btc),
            'priority': 'high',
            'rationale': f'Protect {abs(net_btc):.1f} BTC short position against price increases',
            'pricing': {
                'live_pricing': {
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
            }
        })
    
    priority_order = {'high': 3, 'medium': 2, 'low': 1}
    strategies.sort(key=lambda x: priority_order[x['priority']], reverse=True)
    
    return strategies

# STREAMLIT-COMPATIBLE CSS - HIGH SPECIFICITY
st.markdown("""
<style>
    /* NUCLEAR CSS - MAXIMUM SPECIFICITY TO OVERRIDE STREAMLIT */
    body > div > div > div > div > section.main > div.block-container {
        padding: 1rem 1rem !important;
        max-width: none !important;
    }
    
    /* Override Streamlit's default styling */
    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%) !important;
    }
    
    .stApp .main .block-container {
        background: transparent !important;
    }
    
    /* Custom components with high specificity */
    .custom-header {
        background: linear-gradient(135deg, #1e293b 0%, #475569 100%);
        padding: 1rem;
        border-radius: 15px;
        text-align: center;
        margin: 2rem 0;
        border: 2px solid #fbbf24;
    }
    
    .custom-header h1 {
        color: #fbbf24 !important;
        font-size: 2.5rem !important;
        margin-bottom: 1rem;
        font-weight: 700;
    }
    
    .custom-header p {
        color: #f8fafc !important;
        font-size: 1.3rem !important;
        margin: 0;
    }
    
    /* Step indicators using Streamlit columns */
    .step-indicator {
        background: rgba(30, 41, 59, 0.8);
        border: 2px solid #475569;
        border-radius: 50%;
        width: 60px;
        height: 60px;
        display: flex;
        align-items: center;
        justify-content: center;
        margin: 0 auto 10px auto;
        font-size: 1.5rem;
        font-weight: 700;
        color: #cbd5e1;
    }
    
    .step-indicator.active {
        background: linear-gradient(135deg, #fbbf24 0%, #f59e0b 100%);
        color: #1e293b;
        border-color: #fbbf24;
    }
    
    .step-indicator.completed {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        color: white;
        border-color: #10b981;
    }
    
    .step-label {
        text-align: center;
        color: #f8fafc !important;
        font-size: 0.9rem;
        font-weight: 600;
    }
    
    /* Professional cards */
    .risk-card {
        background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
        border: 3px solid #ef4444;
        border-radius: 15px;
        padding: 2rem;
        text-align: center;
        margin: 1rem 0;
    }
    
    .protection-card {
        background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
        border: 3px solid #10b981;
        border-radius: 15px;
        padding: 2rem;
        text-align: center;
        margin: 1rem 0;
    }
    
    .card-icon {
        font-size: 3rem;
        margin-bottom: 1rem;
    }
    
    .card-title {
        font-size: 1.5rem !important;
        font-weight: 700;
        margin-bottom: 1rem;
        color: #f8fafc !important;
    }
    
    .card-amount {
        font-size: 2rem !important;
        font-weight: 800;
        margin-bottom: 1rem;
    }
    
    .risk-card .card-amount {
        color: #ef4444 !important;
    }
    
    .protection-card .card-amount {
        color: #10b981 !important;
    }
    
    .card-subtitle {
        font-size: 1rem !important;
        color: #cbd5e1 !important;
        line-height: 1.4;
    }
    
    /* Strategy cards */
    .strategy-card {
        background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
        border: 2px solid #fbbf24;
        border-radius: 15px;
        padding: 2rem;
        margin: 1.5rem 0;
    }
    
    .strategy-card.high-priority {
        border-color: #ef4444;
        box-shadow: 0 0 20px rgba(239, 68, 68, 0.3);
    }
    
    .strategy-card.medium-priority {
        border-color: #fbbf24;
        box-shadow: 0 0 20px rgba(251, 191, 36, 0.3);
    }
    
    .strategy-card h3 {
        color: #fbbf24 !important;
        font-size: 1.4rem !important;
        margin-bottom: 1rem;
        font-weight: 700;
    }
    
    .strategy-card p {
        color: #f8fafc !important;
        font-size: 1rem !important;
        margin-bottom: 0.5rem;
    }
    
    /* Execution styling */
    .execution-success {
        background: linear-gradient(135deg, #059669 0%, #10b981 100%);
        padding: 2rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin: 2rem 0;
    }
    
    .execution-success h2 {
        font-size: 2rem !important;
        margin-bottom: 1rem;
    }
    
    /* Info boxes */
    .info-box {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        border-left: 5px solid #10b981;
        border-radius: 10px;
        padding: 1.5rem;
        margin: 1.5rem 0;
    }
    
    .info-box h4 {
        color: #10b981 !important;
        font-size: 1.1rem !important;
        margin-bottom: 0.8rem;
        font-weight: 700;
    }
    
    .info-box p {
        color: #cbd5e1 !important;
        font-size: 1rem !important;
        margin: 0;
        line-height: 1.5;
    }
    
    /* Live price banner */
    .live-price {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        color: white;
        padding: 1rem 2rem;
        border-radius: 25px;
        font-size: 1.2rem;
        font-weight: 700;
        text-align: center;
        margin: 1rem 0;
    }
    
    /* Override Streamlit metric styling */
    [data-testid="metric-container"] {
        background: linear-gradient(135deg, #1e293b 0%, #334155 100%) !important;
        border: 2px solid #475569 !important;
        border-radius: 10px !important;
        padding: 1rem !important;
    }
    
    [data-testid="metric-container"] [data-testid="metric-value"] {
        color: #fbbf24 !important;
        font-size: 1.3rem !important;
        font-weight: 700 !important;
    }
    
    [data-testid="metric-container"] [data-testid="metric-label"] {
        color: #cbd5e1 !important;
        font-size: 0.9rem !important;
        font-weight: 600 !important;
    }
    
    /* Button improvements */
    .stButton > button {
        border-radius: 10px !important;
        font-weight: 700 !important;
        font-size: 1rem !important;
        padding: 0.75rem 1.5rem !important;
    }
    
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #fbbf24 0%, #f59e0b 100%) !important;
        color: #1e293b !important;
        border: none !important;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {display: none;}
    
    /* Force text colors */
    .stMarkdown p, .stMarkdown div, .stText {
        color: #f8fafc !important;
    }
    
    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
        color: #fbbf24 !important;
    }
</style>
""", unsafe_allow_html=True)

def show_progress_indicators(current_step):
    """STREAMLIT-NATIVE progress indicators using columns"""
    st.markdown("---")
    
    col1, col2, col3, col4, col5 = st.columns([1, 2, 1, 2, 1])
    
    with col2:
        if current_step >= 1:
            class_name = "active" if current_step == 1 else "completed" if current_step > 1 else ""
            st.markdown(f"""
            <div class="step-indicator {class_name}">1</div>
            <div class="step-label">Portfolio Setup</div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="step-indicator">1</div>
            <div class="step-label">Portfolio Setup</div>
            """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("<div style='text-align: center; font-size: 2rem; color: #475569; margin-top: 20px;'>→</div>", unsafe_allow_html=True)
    
    with col4:
        if current_step >= 2:
            class_name = "active" if current_step == 2 else "completed" if current_step > 2 else ""
            st.markdown(f"""
            <div class="step-indicator {class_name}">2</div>
            <div class="step-label">Strategy Analysis</div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="step-indicator">2</div>
            <div class="step-label">Strategy Analysis</div>
            """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("<div style='text-align: center; font-size: 2rem; color: #475569; margin-top: 20px;'>→</div>", unsafe_allow_html=True)
    
    if current_step >= 3:
        with col1:
            pass
        with col2:
            pass
        with col3:
            st.markdown("<div style='text-align: center; font-size: 2rem; color: #475569; margin-top: 20px;'>→</div>", unsafe_allow_html=True)
        with col4:
            class_name = "active" if current_step == 3 else "completed"
            st.markdown(f"""
            <div class="step-indicator {class_name}">3</div>
            <div class="step-label">Protection Results</div>
            """, unsafe_allow_html=True)
        with col5:
            pass
    
    st.markdown("---")

def show_header():
    """STREAMLIT-NATIVE header"""
    st.markdown("""
    <div class="custom-header">
        <h1>🏛️ Atticus Professional</h1>
        <p>Portfolio Protection Walkthrough Demo</p>
    </div>
    """, unsafe_allow_html=True)

def show_intro_section():
    """REDESIGNED: Clear intro with integrated comparison"""
    if st.session_state.show_intro:
        live_btc_price = get_live_btc_price()
        if not live_btc_price:
            st.error("Unable to fetch live BTC price")
            return True
        
        # CLEAR HEADER AND INDUSTRY STATEMENT
        st.markdown("""
        <div class="info-box">
            <h4>🏛️ The Institutional Challenge</h4>
            <p>Bitcoin's volatility creates massive risk exposure for institutional portfolios. Recent market events demonstrate that 30-50% price declines can happen within days, creating significant losses for unprotected positions.</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("### 💼 Real-World Example: $50M Bitcoin Allocation")
        st.markdown("**Scenario:** Your institution holds a $50M Bitcoin position as part of your digital asset allocation.")
        
        # INTEGRATED COMPARISON USING STREAMLIT COLUMNS
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            <div class="risk-card">
                <div class="card-icon">⚠️</div>
                <div class="card-title">Without Protection</div>
                <div class="card-amount">$15M+ at Risk</div>
                <div class="card-subtitle">A 30% market decline would result in $15M+ institutional loss with no downside protection mechanism in place.</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="protection-card">
                <div class="card-icon">✅</div>
                <div class="card-title">With Atticus Protection</div>
                <div class="card-amount">$1.2M Cost</div>
                <div class="card-subtitle">Professional options strategies limit maximum loss to ~$1.2M while preserving unlimited upside potential.</div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="info-box">
            <h4>🚀 Live Demonstration</h4>
            <p>This demo shows how institutional-grade options strategies work using real-time market data and live pricing from major exchanges. You'll see exactly how portfolio protection works in practice.</p>
        </div>
        """, unsafe_allow_html=True)
        
        # CENTER THE BUTTON
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🎯 Start Live Demo", type="primary", use_container_width=True):
                st.session_state.show_intro = False
                st.rerun()
        
        return True
    return False

def screen_1_portfolio():
    show_header()
    
    if show_intro_section():
        return
    
    show_progress_indicators(1)
    
    # Reset state
    st.session_state.strategy_selected = False
    st.session_state.selected_strategy = None
    
    live_btc_price = get_live_btc_price()
    if not live_btc_price:
        st.error("⚠️ Unable to fetch live BTC price. Please refresh the page.")
        return
    
    market_conditions = get_live_market_conditions()
    
    # LIVE PRICE BANNER
    st.markdown(f"""
    <div class="live-price">
        🔴 LIVE MARKET DATA: BTC ${live_btc_price:,.2f} | 
        Volatility: {market_conditions['implied_volatility']*100:.0f}% | 
        7-Day: {market_conditions['price_trend_7d']*100:+.1f}%
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="info-box">
        <h4>💡 Portfolio Setup</h4>
        <p>Choose how to create your portfolio for analysis. You can generate a realistic institutional portfolio or build a custom position set. Both options use live market pricing for accurate analysis.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # STREAMLIT NATIVE SIDE-BY-SIDE LAYOUT
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 🏛️ Generate Institution Portfolio")
        st.markdown("**Recommended:** Pre-built realistic portfolio with institutional context")
        
        fund_type = st.selectbox(
            "Select Institution Size:",
            ["Small Fund ($20-50M AUM)", "Mid-Cap Fund ($50-200M AUM)"],
            key="fund_size"
        )
        
        if "Small" in fund_type:
            btc_allocation = 2000000 / live_btc_price
            st.info(f"📊 Will generate: ~{btc_allocation:.1f} BTC position (${2000000/1000000:.0f}M allocation)")
        else:
            btc_allocation = 8500000 / live_btc_price
            st.info(f"📊 Will generate: ~{btc_allocation:.1f} BTC position (${8500000/1000000:.1f}M allocation)")
        
        if st.button("🎯 Generate Portfolio", type="primary", use_container_width=True, key="gen_portfolio"):
            with st.spinner("Generating with live pricing..."):
                time.sleep(1)
                if "Small" in fund_type:
                    btc_size = 2000000 / live_btc_price
                    portfolio = {
                        'aum': 38000000,
                        'total_btc_size': btc_size,
                        'net_btc_exposure': btc_size,
                        'total_current_value': btc_size * live_btc_price,
                        'total_pnl': btc_size * live_btc_price * 0.15,
                        'current_btc_price': live_btc_price
                    }
                else:
                    btc_size = 8500000 / live_btc_price
                    portfolio = {
                        'aum': 128000000,
                        'total_btc_size': btc_size,
                        'net_btc_exposure': btc_size,
                        'total_current_value': btc_size * live_btc_price,
                        'total_pnl': btc_size * live_btc_price * 0.18,
                        'current_btc_price': live_btc_price
                    }
                
                st.session_state.portfolio = portfolio
                st.session_state.portfolio_source = 'generated'
                st.session_state.strategies = None
                st.session_state.strategies_generated = False
                st.success(f"✅ Generated: {btc_size:.1f} BTC @ ${live_btc_price:,.2f}")
                st.rerun()
        
        # Show generated portfolio
        if st.session_state.portfolio and st.session_state.portfolio_source == 'generated':
            portfolio = st.session_state.portfolio
            
            st.markdown("**📈 Portfolio Summary:**")
            
            col1a, col2a = st.columns(2)
            with col1a:
                st.metric("AUM", f"${portfolio['aum']/1000000:.0f}M")
                st.metric("BTC Position", f"{portfolio['total_btc_size']:.1f}")
            with col2a:
                st.metric("Current Value", f"${portfolio['total_current_value']/1000000:.1f}M")
                st.metric("P&L", f"${portfolio['total_pnl']/1000000:.1f}M")
            
            potential_loss = portfolio['total_current_value'] * 0.25
            st.warning(f"⚠️ Risk: 25% decline = ${potential_loss/1000000:.1f}M loss")
            
            if st.button("📊 Analyze Strategies", type="primary", use_container_width=True):
                st.session_state.demo_step = 2
                st.rerun()
    
    with col2:
        st.markdown("#### ⚡ Custom Position Builder")
        st.markdown("Build your own portfolio positions for analysis")
        
        with st.form("add_position", clear_on_submit=True):
            btc_amount = st.number_input("BTC Amount", min_value=0.1, value=25.0, step=0.1)
            position_type = st.selectbox("Position Type", ["Long", "Short"])
            
            col1a, col2a = st.columns(2)
            with col1a:
                add_clicked = st.form_submit_button("Add Position", type="primary", use_container_width=True)
            with col2a:
                clear_clicked = st.form_submit_button("Clear All", type="secondary", use_container_width=True)
        
        if add_clicked:
            position_value = btc_amount * live_btc_price
            st.success(f"➕ Added: {btc_amount:.1f} BTC {position_type} (${position_value:,.0f})")
            new_position = {'btc_amount': btc_amount, 'position_type': position_type}
            st.session_state.custom_positions.append(new_position)
            st.rerun()
        
        if clear_clicked:
            st.session_state.custom_positions = []
            st.rerun()
        
        # Show positions
        if st.session_state.custom_positions:
            st.markdown("**📋 Current Positions:**")
            
            total_long = sum(pos['btc_amount'] for pos in st.session_state.custom_positions if pos['position_type'] == 'Long')
            total_short = sum(pos['btc_amount'] for pos in st.session_state.custom_positions if pos['position_type'] == 'Short')
            net_btc = total_long - total_short
            
            for i, pos in enumerate(st.session_state.custom_positions):
                col_pos, col_remove = st.columns([3, 1])
                with col_pos:
                    st.write(f"**{pos['btc_amount']:.1f} BTC** • {'🟢 Long' if pos['position_type'] == 'Long' else '🔴 Short'} • ${pos['btc_amount'] * live_btc_price:,.0f}")
                with col_remove:
                    if st.button("❌", key=f"remove_{i}"):
                        st.session_state.custom_positions.pop(i)
                        st.rerun()
            
            col1a, col1b, col1c = st.columns(3)
            with col1a:
                st.metric("Long", f"{total_long:.1f}")
            with col1b:
                st.metric("Short", f"{total_short:.1f}")
            with col1c:
                st.metric("Net", f"{net_btc:+.1f}")
            
            if st.button("⚡ Analyze Portfolio", type="primary", use_container_width=True):
                total_value = (total_long + total_short) * live_btc_price
                custom_portfolio = {
                    'aum': abs(net_btc) * live_btc_price * 4,
                    'total_btc_size': abs(net_btc),
                    'net_btc_exposure': net_btc,
                    'total_current_value': total_value,
                    'total_pnl': total_value * 0.08,
                    'current_btc_price': live_btc_price
                }
                st.session_state.portfolio = custom_portfolio
                st.session_state.portfolio_source = 'custom'
                st.session_state.strategies = None
                st.session_state.strategies_generated = False
                st.session_state.demo_step = 2
                st.rerun()

def screen_2_strategies():
    show_header()
    show_progress_indicators(2)
    
    if not st.session_state.portfolio:
        st.error("Please create a portfolio first")
        return
    
    portfolio = st.session_state.portfolio
    net_btc = portfolio.get('net_btc_exposure', 0)
    current_price = portfolio.get('current_btc_price', get_live_btc_price())
    
    if not current_price:
        st.error("Unable to fetch current BTC price")
        return
    
    market_conditions = get_live_market_conditions()
    position_direction = "Long" if net_btc > 0 else "Short" if net_btc < 0 else "Neutral"
    
    st.markdown("# 🛡️ Live Protection Strategies")
    
    st.markdown(f"""
    <div class="live-price">
        🎯 Portfolio: {abs(net_btc):.1f} BTC {position_direction} | 
        🔴 Live: ${current_price:,.2f} | 
        📈 Market: {market_conditions['market_regime'].title()}
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown(f"""
    <div class="info-box">
        <h4>📊 Portfolio Analysis</h4>
        <p>Analyzing {abs(net_btc):.1f} BTC {position_direction} position worth ${abs(net_btc) * current_price:,.0f}. 
        Market conditions: {market_conditions['market_regime'].title()} with {market_conditions['implied_volatility']*100:.0f}% volatility. 
        Generating optimal strategies using live institutional pricing.</p>
    </div>
    """, unsafe_allow_html=True)
    
    if not st.session_state.strategies_generated:
        with st.spinner("Analyzing live market conditions... (30-45 seconds)"):
            time.sleep(2)
            st.session_state.strategies = generate_dynamic_strategies(net_btc, current_price)
            st.session_state.strategies_generated = True
    
    if (st.session_state.strategies and 
        not st.session_state.strategy_selected and 
        not st.session_state.selected_strategy):
        
        st.markdown("""
        <div class="info-box">
            <h4>💡 Strategy Selection</h4>
            <p>Each strategy uses live market pricing optimized for current conditions. Protection strategies limit downside while income strategies generate returns.</p>
        </div>
        """, unsafe_allow_html=True)
        
        for i, strategy in enumerate(st.session_state.strategies):
            priority_emoji = "🔥" if strategy['priority'] == 'high' else "⭐" if strategy['priority'] == 'medium' else "💡"
            
            strategy_display = strategy['strategy_name'].replace('_', ' ').title()
            if 'covered_call' in strategy['strategy_name'] or 'cash_secured_put' in strategy['strategy_name']:
                strategy_display += " (Income Generator)"
            elif 'protective' in strategy['strategy_name']:
                strategy_display += " (Protection)"
            elif 'spread' in strategy['strategy_name']:
                strategy_display += " (Cost-Efficient)"
            
            pricing = strategy['pricing']['live_pricing']
            priority_class = strategy['priority'] + "-priority"
            
            st.markdown(f"""
            <div class="strategy-card {priority_class}">
                <h3>{priority_emoji} {strategy_display}</h3>
                <p><strong>Coverage:</strong> {strategy['target_exposure']:.1f} BTC</p>
                <p><strong>Strategy:</strong> {strategy['rationale']}</p>
                <p><strong>Duration:</strong> {pricing['days_to_expiry']} days | <strong>Expiry:</strong> {pricing['expiry_date']}</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Metrics in columns
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                if pricing['total_premium'] < 0:
                    st.success(f"**Income**\n${abs(pricing['total_premium']):,.0f}")
                else:
                    st.info(f"**Cost**\n${abs(pricing['total_premium']):,.0f}")
            with col2:
                cost_pct = pricing['cost_as_pct']
                color = "🟢" if cost_pct < 3 else "🟡" if cost_pct < 5 else "🔴"
                st.info(f"**Rate**\n{color} {cost_pct:.1f}%")
            with col3:
                st.info(f"**Contracts**\n{pricing['contracts_needed']}")
            with col4:
                if st.button("Execute Strategy", key=f"exec_{i}", type="primary", use_container_width=True):
                    st.session_state.selected_strategy = strategy
                    st.session_state.strategy_selected = True
                    st.session_state.execution_data = {
                        'btc_price_at_execution': current_price,
                        'execution_time': random.randint(12, 28),
                        'timestamp': datetime.now().isoformat()
                    }
                    st.session_state.demo_step = 3
                    st.rerun()
            
            st.markdown("---")
    
    elif st.session_state.strategy_selected:
        st.info("✅ Strategy selected! Executing...")
        time.sleep(1)
        st.session_state.demo_step = 3
        st.rerun()
    
    if st.button("← Back to Portfolio", type="secondary"):
        st.session_state.demo_step = 1
        st.session_state.strategies = None
        st.session_state.selected_strategy = None
        st.session_state.strategies_generated = False
        st.session_state.strategy_selected = False
        st.rerun()

def screen_3_execution():
    show_header()
    show_progress_indicators(3)
    
    if not st.session_state.selected_strategy:
        st.error("Strategy not selected")
        return
    
    strategy = st.session_state.selected_strategy
    execution_data = st.session_state.execution_data
    pricing = strategy['pricing']['live_pricing']
    
    st.markdown("# ✅ Strategy Execution")
    
    with st.spinner("Executing with live pricing..."):
        time.sleep(2)
    
    st.markdown("""
    <div class="execution-success">
        <h2>🎯 Execution Complete</h2>
        <p>Professional options strategy executed with live market pricing</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.metric("Execution Time", f"{execution_data['execution_time']} seconds")
    
    st.markdown(f"""
    <div class="info-box">
        <h4>🎯 Contract Details</h4>
        <p>Professional strategy executed for {strategy['target_exposure']:.1f} BTC position using live institutional pricing.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Contract details in columns
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 📋 Executed Contracts")
        st.write(f"**Strategy:** {pricing['option_type']}")
        st.write(f"**Contracts:** {pricing['contracts_needed']}")
        st.write(f"**Strike:** ${pricing.get('strike_price', pricing.get('long_strike', 0)):,.2f}")
        st.write(f"**Expiry:** {pricing['expiry_date']}")
        st.write(f"**Premium:** ${abs(pricing['total_premium']):,.2f}")
    
    with col2:
        outcomes = calculate_strategy_outcomes(strategy, pricing['btc_spot_price'])
        
        st.markdown("#### 🛡️ Protection Summary")
        st.write(f"**Entry Price:** ${pricing['btc_spot_price']:,.2f}")
        st.write(f"**Breakeven:** ${outcomes['breakeven_price']:,.2f}")
        st.write(f"**Max Risk:** {outcomes['max_loss'] if isinstance(outcomes['max_loss'], str) else f'${outcomes['max_loss']:,.0f}'}")
        st.write(f"**Max Reward:** {outcomes['max_profit']}")
        st.write(f"**Impact:** {pricing['cost_as_pct']:.2f}% of portfolio")
    
    # Scenario analysis
    outcomes = calculate_strategy_outcomes(strategy, pricing['btc_spot_price'])
    
    if outcomes['scenarios']:
        st.markdown("### 📊 Market Scenarios")
        
        st.markdown("""
        <div class="info-box">
            <h4>💡 Outcome Analysis</h4>
            <p>These scenarios show exactly how your portfolio performs under different Bitcoin price movements with protection in place.</p>
        </div>
        """, unsafe_allow_html=True)
        
        for i, scenario in enumerate(outcomes['scenarios']):
            st.markdown(f"""
            **Scenario {i+1}: {scenario['condition']}**
            - **{scenario['outcome']}:** {scenario['details']}
            """)
    
    st.markdown("""
    <div class="execution-success">
        <h2>✅ Portfolio Protection Deployed</h2>
        <p>Institutional options strategy executed with live pricing. Your portfolio is now protected.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Action buttons
    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        if st.button("🔄 New Demo", type="secondary", use_container_width=True):
            for key in ['portfolio', 'strategies', 'selected_strategy', 'execution_data']:
                if key in st.session_state:
                    st.session_state[key] = None
            st.session_state.custom_positions = []
            st.session_state.demo_step = 1
            st.session_state.strategies_generated = False
            st.session_state.strategy_selected = False
            st.session_state.show_intro = True
            st.rerun()
    
    with col2:
        st.link_button("💬 Contact for Implementation", "https://t.me/willialso", use_container_width=True)
    
    with col3:
        pass

def main():
    ensure_session_state()
    current_step = st.session_state.get('demo_step', 1)
    
    if current_step == 1:
        screen_1_portfolio()
    elif current_step == 2:
        screen_2_strategies()
    elif current_step == 3:
        screen_3_execution()
    else:
        st.session_state.demo_step = 1
        screen_1_portfolio()

if __name__ == "__main__":
    main()
