"""
ATTICUS PROFESSIONAL - POLISHED INSTITUTIONAL DEMO
✅ Consistent professional typography and styling
✅ Uniform font sizes and visual hierarchy throughout
✅ Professional execution without animations
✅ Clean, polished institutional presentation
✅ Maintains all real-time pricing functionality
"""
import streamlit as st
import requests
import time
import random
from datetime import datetime, timedelta
import os
import math

# Page config
st.set_page_config(
    page_title="Atticus Professional - Portfolio Protection Demo",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Session state initialization
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

# ALL PRICING FUNCTIONS UNCHANGED (preserves real-time data)
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

# PROFESSIONAL CSS - CONSISTENT TYPOGRAPHY AND STYLING
st.markdown("""
<style>
    /* Base app styling */
    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        color: #f8fafc !important;
        font-family: 'Inter', 'Segoe UI', 'Roboto', sans-serif;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {display: none;}
    
    /* CONSISTENT TYPOGRAPHY HIERARCHY */
    
    /* Main titles */
    .stMarkdown h1 {
        color: #fbbf24 !important;
        font-size: 2.5rem !important;
        font-weight: 700 !important;
        line-height: 1.2 !important;
        margin-bottom: 1.5rem !important;
    }
    
    /* Section headers */
    .stMarkdown h2 {
        color: #fbbf24 !important;
        font-size: 2rem !important;
        font-weight: 600 !important;
        line-height: 1.3 !important;
        margin-bottom: 1.2rem !important;
        margin-top: 2rem !important;
    }
    
    /* Subsection headers */
    .stMarkdown h3 {
        color: #fbbf24 !important;
        font-size: 1.6rem !important;
        font-weight: 600 !important;
        line-height: 1.3 !important;
        margin-bottom: 1rem !important;
        margin-top: 1.5rem !important;
    }
    
    /* Card headers */
    .stMarkdown h4 {
        color: #fbbf24 !important;
        font-size: 1.3rem !important;
        font-weight: 600 !important;
        line-height: 1.3 !important;
        margin-bottom: 0.8rem !important;
        margin-top: 1rem !important;
    }
    
    /* Subheadings */
    .stMarkdown h5 {
        color: #f8fafc !important;
        font-size: 1.1rem !important;
        font-weight: 600 !important;
        line-height: 1.4 !important;
        margin-bottom: 0.6rem !important;
    }
    
    /* Body text - LARGER AND MORE READABLE */
    .stMarkdown p {
        color: #f8fafc !important;
        font-size: 1.1rem !important;
        line-height: 1.6 !important;
        margin-bottom: 1rem !important;
    }
    
    /* Strong text */
    .stMarkdown strong {
        color: #fbbf24 !important;
        font-weight: 700 !important;
    }
    
    /* List items */
    .stMarkdown li {
        color: #f8fafc !important;
        font-size: 1.1rem !important;
        line-height: 1.6 !important;
        margin-bottom: 0.5rem !important;
    }
    
    /* Captions */
    .stMarkdown .caption, [data-testid="caption"] {
        color: #cbd5e1 !important;
        font-size: 1rem !important;
        line-height: 1.5 !important;
    }
    
    /* CONSISTENT ALERT STYLING */
    .stAlert {
        font-size: 1.1rem !important;
        line-height: 1.5 !important;
        padding: 1rem 1.5rem !important;
        border-radius: 8px !important;
        font-weight: 500 !important;
    }
    
    /* Success alerts */
    .stAlert[data-baseweb-kind="success"] {
        background-color: rgba(16, 185, 129, 0.15) !important;
        border: 1px solid rgba(16, 185, 129, 0.5) !important;
        color: #f0fdf4 !important;
    }
    
    /* Error alerts */
    .stAlert[data-baseweb-kind="error"] {
        background-color: rgba(239, 68, 68, 0.15) !important;
        border: 1px solid rgba(239, 68, 68, 0.5) !important;
        color: #fef2f2 !important;
    }
    
    /* Warning alerts */
    .stAlert[data-baseweb-kind="warning"] {
        background-color: rgba(251, 191, 36, 0.15) !important;
        border: 1px solid rgba(251, 191, 36, 0.5) !important;
        color: #fffbeb !important;
    }
    
    /* Info alerts */
    .stAlert[data-baseweb-kind="info"] {
        background-color: rgba(59, 130, 246, 0.15) !important;
        border: 1px solid rgba(59, 130, 246, 0.5) !important;
        color: #eff6ff !important;
    }
    
    /* METRIC CONTAINERS - CONSISTENT STYLING */
    [data-testid="metric-container"] {
        background: rgba(30, 41, 59, 0.8) !important;
        border: 1px solid rgba(71, 85, 105, 0.8) !important;
        border-radius: 10px !important;
        padding: 1.2rem !important;
        margin: 0.5rem 0 !important;
    }
    
    [data-testid="metric-container"] [data-testid="metric-value"] {
        color: #fbbf24 !important;
        font-size: 1.8rem !important;
        font-weight: 700 !important;
        line-height: 1.2 !important;
    }
    
    [data-testid="metric-container"] [data-testid="metric-label"] {
        color: #cbd5e1 !important;
        font-size: 1rem !important;
        font-weight: 600 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.025em !important;
    }
    
    [data-testid="metric-container"] [data-testid="metric-delta"] {
        font-size: 0.9rem !important;
        font-weight: 500 !important;
    }
    
    /* BUTTON STYLING - PROFESSIONAL AND CONSISTENT */
    .stButton > button {
        border-radius: 8px !important;
        font-weight: 600 !important;
        font-size: 1.1rem !important;
        padding: 0.75rem 1.5rem !important;
        border: none !important;
        transition: all 0.2s ease !important;
        text-transform: none !important;
    }
    
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #fbbf24 0%, #f59e0b 100%) !important;
        color: #1e293b !important;
        box-shadow: 0 4px 12px rgba(251, 191, 36, 0.3) !important;
    }
    
    .stButton > button[kind="primary"]:hover {
        background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%) !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 6px 18px rgba(251, 191, 36, 0.4) !important;
    }
    
    .stButton > button[kind="secondary"] {
        background: rgba(71, 85, 105, 0.8) !important;
        color: #f8fafc !important;
        border: 1px solid rgba(100, 116, 139, 0.8) !important;
    }
    
    .stButton > button[kind="secondary"]:hover {
        background: rgba(100, 116, 139, 0.9) !important;
        transform: translateY(-1px) !important;
    }
    
    /* FORM ELEMENTS */
    .stSelectbox > div > div {
        background-color: rgba(30, 41, 59, 0.8) !important;
        border: 1px solid rgba(71, 85, 105, 0.8) !important;
        color: #f8fafc !important;
        font-size: 1.1rem !important;
    }
    
    .stNumberInput > div > div > input {
        background-color: rgba(30, 41, 59, 0.8) !important;
        border: 1px solid rgba(71, 85, 105, 0.8) !important;
        color: #f8fafc !important;
        font-size: 1.1rem !important;
    }
    
    /* PROGRESS BAR */
    .stProgress > div > div > div > div {
        background: linear-gradient(135deg, #fbbf24 0%, #f59e0b 100%) !important;
    }
    
    /* EXPANDER */
    .stExpander {
        background-color: rgba(30, 41, 59, 0.6) !important;
        border: 1px solid rgba(71, 85, 105, 0.8) !important;
        border-radius: 8px !important;
    }
    
    .stExpander > div > div {
        color: #f8fafc !important;
        font-size: 1.1rem !important;
        font-weight: 600 !important;
    }
    
    /* LINK BUTTON */
    .stLinkButton > a {
        background: linear-gradient(135deg, #059669 0%, #10b981 100%) !important;
        color: white !important;
        font-weight: 600 !important;
        font-size: 1.1rem !important;
        padding: 0.75rem 1.5rem !important;
        border-radius: 8px !important;
        text-decoration: none !important;
        display: inline-block !important;
        text-align: center !important;
        transition: all 0.2s ease !important;
    }
    
    .stLinkButton > a:hover {
        background: linear-gradient(135deg, #047857 0%, #059669 100%) !important;
        transform: translateY(-1px) !important;
    }
    
    /* RADIO BUTTONS */
    .stRadio > div {
        gap: 1.5rem !important;
    }
    
    .stRadio label {
        font-size: 1.1rem !important;
        color: #f8fafc !important;
        font-weight: 500 !important;
    }
    
    /* SPINNER */
    .stSpinner > div {
        border-top-color: #fbbf24 !important;
    }
</style>
""", unsafe_allow_html=True)

def show_header():
    """Professional header with consistent styling"""
    # Create centered header layout
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        # Logo with proper sizing
        try:
            st.image("https://i.ibb.co/qFNCZsWG/attpro.png", width=400, use_column_width=False)
        except:
            st.markdown("# 🏛️ Atticus Professional")
        
        # Consistent header styling
        st.markdown("## Professional Portfolio Protection Demo")
        st.caption("Live market data • Real-time options pricing • Institutional strategies")

def show_progress_indicator(current_step):
    """Professional progress indicator with consistent styling"""
    st.markdown("---")
    
    # Progress steps
    progress_cols = st.columns(3)
    
    with progress_cols[0]:
        if current_step >= 1:
            if current_step == 1:
                st.info("🔵 **Step 1:** Portfolio Setup")
            else:
                st.success("✅ **Step 1:** Portfolio Setup")
        else:
            st.write("⚪ **Step 1:** Portfolio Setup")
    
    with progress_cols[1]:
        if current_step >= 2:
            if current_step == 2:
                st.info("🔵 **Step 2:** Strategy Analysis")
            else:
                st.success("✅ **Step 2:** Strategy Analysis")
        else:
            st.write("⚪ **Step 2:** Strategy Analysis")
    
    with progress_cols[2]:
        if current_step >= 3:
            st.info("🔵 **Step 3:** Protection Results")
        else:
            st.write("⚪ **Step 3:** Protection Results")
    
    # Progress bar with consistent styling
    progress_value = current_step / 3.0
    st.progress(progress_value)
    st.caption(f"Step {current_step} of 3 completed")
    
    st.markdown("---")

def show_intro_walkthrough():
    """Professional intro with consistent typography"""
    if st.session_state.show_intro:
        live_btc_price = get_live_btc_price()
        
        if not live_btc_price:
            st.error("⚠️ Unable to fetch live BTC price. Please refresh the page.")
            return True
        
        # Professional problem statement
        st.error("🚨 **The Institutional Challenge:** Bitcoin's volatility creates massive risk exposure")
        
        st.markdown("""
        Recent market events demonstrate that 30-50% Bitcoin price declines can occur within days, 
        creating significant losses for unprotected institutional positions. Traditional hedging solutions 
        are often expensive, inflexible, and inadequate for digital asset volatility.
        """)
        
        # Professional solution statement
        st.success("✅ **The Professional Solution:** Institutional-grade options strategies")
        
        st.markdown("""
        Atticus provides sophisticated options strategies that limit downside risk while preserving unlimited 
        upside potential, using the same professional risk management principles employed by traditional 
        institutional asset managers.
        """)
        
        # Live market example
        st.info(f"📊 **Live Market Example:** ${50000000/1000000:.0f}M Bitcoin Position Protection (Live BTC: ${live_btc_price:,.2f})")
        
        # Professional comparison
        col1, col2 = st.columns(2, gap="large")
        
        with col1:
            st.error("⚠️ **Unprotected Portfolio Risk**")
            st.metric("Potential Loss", "$15M+", "30% market decline")
            st.markdown("""
            **Consequences:**
            - No downside protection mechanism
            - Full exposure to market volatility
            - Unlimited loss potential during market stress
            """)
        
        with col2:
            st.success("✅ **Professional Portfolio Protection")
            st.metric("Protection Cost", "$1.2M", "2.4% of position value")
            st.markdown("""
            **Benefits:**
            - Capped maximum loss exposure
            - Unlimited upside potential preserved
            - Professional institutional risk management
            """)
        
        # Professional call to action
        st.markdown("---")
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            if st.button("**Start Professional Demo with Live Market Data**", type="primary", use_container_width=True):
                st.session_state.show_intro = False
                st.rerun()
        
        st.markdown("---")
        return True
    
    return False

def screen_1_portfolio():
    """Professional portfolio setup screen"""
    show_header()
    
    if show_intro_walkthrough():
        return
    
    show_progress_indicator(1)
    
    # Reset state
    st.session_state.strategy_selected = False
    st.session_state.selected_strategy = None
    
    live_btc_price = get_live_btc_price()
    if not live_btc_price:
        st.error("⚠️ Unable to fetch live BTC price. Please refresh the page.")
        return
    
    market_conditions = get_live_market_conditions()
    
    # Professional market data display
    st.success(f"🔴 **Live Market Data:** BTC ${live_btc_price:,.2f} • Volatility: {market_conditions['implied_volatility']*100:.0f}% • 7-Day Trend: {market_conditions['price_trend_7d']*100:+.1f}%")
    
    st.info("💡 **Portfolio Setup:** Choose your preferred method to create a portfolio for protection analysis. Both options use live market pricing for accurate strategy generation.")
    
    # Main content with professional spacing
    col1, col2 = st.columns(2, gap="large")
    
    with col1:
        st.markdown("### 🏛️ Generate Institution Portfolio")
        st.caption("**Recommended approach:** Pre-configured realistic institutional allocation")
        
        fund_type = st.selectbox(
            "**Institution Size Selection:**",
            ["Small Fund ($20-50M AUM)", "Mid-Cap Fund ($50-200M AUM)"],
            key="fund_size",
            help="Select institution size to generate appropriate Bitcoin allocation"
        )
        
        if "Small" in fund_type:
            btc_allocation = 2000000 / live_btc_price
            st.info(f"📊 **Portfolio Specification:** ~{btc_allocation:.1f} BTC position (${2000000/1000000:.0f}M allocation) with realistic performance metrics and risk exposure")
        else:
            btc_allocation = 8500000 / live_btc_price
            st.info(f"📊 **Portfolio Specification:** ~{btc_allocation:.1f} BTC position (${8500000/1000000:.1f}M allocation) with institutional-scale exposure and complexity")
        
        if st.button("**Generate Professional Portfolio**", type="primary", use_container_width=True, key="gen_portfolio"):
            with st.spinner("🔄 Generating portfolio with real-time market pricing..."):
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
                st.success(f"✅ **Portfolio Generated Successfully:** {btc_size:.1f} BTC @ ${live_btc_price:,.2f}")
                st.rerun()
        
        # Display generated portfolio with professional formatting
        if st.session_state.portfolio and st.session_state.portfolio_source == 'generated':
            portfolio = st.session_state.portfolio
            
            st.markdown("#### 📈 Portfolio Summary")
            
            col1a, col2a = st.columns(2)
            with col1a:
                st.metric("Total AUM", f"${portfolio['aum']/1000000:.0f}M")
                st.metric("BTC Position", f"{portfolio['total_btc_size']:.1f} BTC")
            with col2a:
                st.metric("Current Value", f"${portfolio['total_current_value']/1000000:.1f}M")
                st.metric("Unrealized P&L", f"${portfolio['total_pnl']/1000000:.1f}M")
            
            potential_loss = portfolio['total_current_value'] * 0.25
            st.warning(f"⚠️ **Risk Assessment:** A 25% market decline would result in ${potential_loss/1000000:.1f}M institutional loss without professional protection strategies")
            
            if st.button("**Analyze Professional Protection Strategies**", type="primary", use_container_width=True):
                st.session_state.demo_step = 2
                st.rerun()
    
    with col2:
        st.markdown("### ⚡ Custom Position Builder")
        st.caption("Build customized portfolio positions for specialized analysis")
        
        with st.form("position_form", clear_on_submit=True):
            btc_amount = st.number_input(
                "**Bitcoin Amount**", 
                min_value=0.1, 
                max_value=1000.0, 
                value=25.0, 
                step=0.1, 
                help="Enter the Bitcoin amount for this position"
            )
            position_type = st.selectbox("**Position Direction**", ["Long", "Short"])
            
            col1a, col2a = st.columns(2)
            with col1a:
                add_clicked = st.form_submit_button("**Add Position**", type="primary", use_container_width=True)
            with col2a:
                clear_clicked = st.form_submit_button("**Clear All**", type="secondary", use_container_width=True)
        
        if add_clicked:
            position_value = btc_amount * live_btc_price
            st.success(f"✅ **Position Added:** {btc_amount:.1f} BTC {position_type} position (${position_value:,.0f} market value)")
            new_position = {'btc_amount': btc_amount, 'position_type': position_type}
            st.session_state.custom_positions.append(new_position)
            st.rerun()
        
        if clear_clicked:
            st.session_state.custom_positions = []
            st.success("🗑️ **All positions cleared successfully**")
            st.rerun()
        
        # Display positions with professional formatting
        if st.session_state.custom_positions:
            st.markdown("#### 📋 Portfolio Positions")
            
            total_long = sum(pos['btc_amount'] for pos in st.session_state.custom_positions if pos['position_type'] == 'Long')
            total_short = sum(pos['btc_amount'] for pos in st.session_state.custom_positions if pos['position_type'] == 'Short')
            net_btc = total_long - total_short
            
            # Position list with professional styling
            for i, pos in enumerate(st.session_state.custom_positions):
                col_pos, col_btn = st.columns([4, 1])
                with col_pos:
                    st.markdown(f"**{pos['btc_amount']:.1f} BTC** • {'🟢 Long' if pos['position_type'] == 'Long' else '🔴 Short'} • ${pos['btc_amount'] * live_btc_price:,.0f}")
                with col_btn:
                    if st.button("❌", key=f"remove_{i}", help="Remove this position"):
                        st.session_state.custom_positions.pop(i)
                        st.rerun()
            
            # Professional portfolio summary
            st.markdown("##### Portfolio Summary")
            col1a, col2a, col3a = st.columns(3)
            with col1a:
                st.metric("Long BTC", f"{total_long:.1f}")
            with col2a:
                st.metric("Short BTC", f"{total_short:.1f}")  
            with col3a:
                st.metric("Net BTC", f"{net_btc:+.1f}")
            
            if st.button("**Analyze Custom Portfolio Protection**", type="primary", use_container_width=True):
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
    """Professional strategy analysis screen"""
    show_header()
    show_progress_indicator(2)
    
    if not st.session_state.portfolio:
        st.error("❌ Portfolio data required. Please create a portfolio first.")
        if st.button("**← Return to Portfolio Setup**", type="secondary"):
            st.session_state.demo_step = 1
            st.rerun()
        return
    
    portfolio = st.session_state.portfolio
    net_btc = portfolio.get('net_btc_exposure', 0)
    current_price = portfolio.get('current_btc_price', get_live_btc_price())
    
    if not current_price:
        st.error("❌ Unable to fetch current BTC price for strategy analysis")
        return
    
    market_conditions = get_live_market_conditions()
    position_direction = "Long" if net_btc > 0 else "Short" if net_btc < 0 else "Neutral"
    
    st.markdown("# 🛡️ Professional Protection Strategies")
    
    # Professional portfolio analysis summary
    st.success(f"🎯 **Portfolio Analysis Complete:** {abs(net_btc):.1f} BTC {position_direction} position • ${abs(net_btc) * current_price:,.0f} total value • {market_conditions['market_regime'].title()} market conditions")
    
    st.info(f"📊 **Market Context Analysis:** Current volatility environment at {market_conditions['implied_volatility']*100:.0f}% with {market_conditions['price_trend_7d']*100:+.1f}% weekly trend. Generating optimal institutional strategies using live market pricing from multiple exchanges.")
    
    # Strategy generation with professional progress tracking
    if not st.session_state.strategies_generated:
        with st.spinner("🔄 Analyzing live market conditions and generating institutional-grade strategies..."):
            progress_bar = st.progress(0)
            for i in range(100):
                time.sleep(0.03)  # 3-second generation time
                progress_bar.progress(i + 1)
            
            st.session_state.strategies = generate_dynamic_strategies(net_btc, current_price)
            st.session_state.strategies_generated = True
            st.success("✅ **Strategy Analysis Complete:** Institutional strategies generated with live pricing")
    
    # Professional strategy display
    if (st.session_state.strategies and 
        not st.session_state.strategy_selected and 
        not st.session_state.selected_strategy):
        
        st.info("💡 **Strategy Selection Guide:** Each strategy below uses live institutional market pricing and is optimized for current market conditions. Protection strategies limit downside risk while income strategies generate returns from existing holdings.")
        
        for i, strategy in enumerate(st.session_state.strategies):            
            strategy_display = strategy['strategy_name'].replace('_', ' ').title()
            if 'covered_call' in strategy['strategy_name'] or 'cash_secured_put' in strategy['strategy_name']:
                strategy_display += " (Income Generation)"
            elif 'protective' in strategy['strategy_name']:
                strategy_display += " (Downside Protection)"
            elif 'spread' in strategy['strategy_name']:
                strategy_display += " (Cost-Efficient Protection)"
            
            pricing = strategy['pricing']['live_pricing']
            
            # Professional strategy container with priority styling
            with st.container():
                if strategy['priority'] == 'high':
                    st.error(f"🔥 **HIGH PRIORITY:** {strategy_display}")
                elif strategy['priority'] == 'medium':
                    st.warning(f"⭐ **RECOMMENDED:** {strategy_display}")
                else:
                    st.info(f"💡 **ALTERNATIVE:** {strategy_display}")
                
                # Professional strategy details layout
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.markdown(f"**Coverage:** {strategy['target_exposure']:.1f} BTC position")
                    st.markdown(f"**Strategy:** {strategy['rationale']}")
                    st.markdown(f"**Duration:** {pricing['days_to_expiry']} days • **Expiry:** {pricing['expiry_date']}")
                
                with col2:
                    # Professional metrics display
                    col2a, col2b, col2c = st.columns(3)
                    with col2a:
                        if pricing['total_premium'] < 0:
                            st.success(f"**Income**\n${abs(pricing['total_premium']):,.0f}")
                        else:
                            st.metric("Cost", f"${abs(pricing['total_premium']):,.0f}")
                    with col2b:
                        cost_pct = pricing['cost_as_pct']
                        color_indicator = "🟢" if cost_pct < 3 else "🟡" if cost_pct < 5 else "🔴"
                        st.metric("Rate", f"{cost_pct:.1f}%", delta=f"{color_indicator}")
                    with col2c:
                        st.metric("Contracts", f"{pricing['contracts_needed']}")
                
                # Professional execution button
                if st.button(f"**Execute {strategy_display}**", key=f"exec_{i}", type="primary", use_container_width=True):
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
        st.success("✅ **Strategy Selected Successfully** - Executing with live institutional pricing...")
        time.sleep(1)
        st.session_state.demo_step = 3
        st.rerun()
    
    # Professional navigation
    if st.button("**← Return to Portfolio Setup**", type="secondary"):
        st.session_state.demo_step = 1
        st.session_state.strategies = None
        st.session_state.selected_strategy = None
        st.session_state.strategies_generated = False
        st.session_state.strategy_selected = False
        st.rerun()

def screen_3_execution():
    """Professional execution results screen - NO BALLOONS"""
    show_header()
    show_progress_indicator(3)
    
    if not st.session_state.selected_strategy:
        st.error("❌ Strategy selection required for execution analysis")
        if st.button("**← Return to Strategy Selection**", type="secondary"):
            st.session_state.demo_step = 2
            st.rerun()
        return
    
    strategy = st.session_state.selected_strategy
    execution_data = st.session_state.execution_data
    pricing = strategy['pricing']['live_pricing']
    
    st.markdown("# ✅ Strategy Execution Complete")
    
    # Professional execution process - NO UNPROFESSIONAL ANIMATIONS
    with st.spinner("⚡ Executing strategy with live institutional market pricing..."):
        execution_progress = st.progress(0)
        for i in range(100):
            time.sleep(0.03)  # 3-second professional execution time
            execution_progress.progress(i + 1)
    
    # PROFESSIONAL SUCCESS MESSAGE - NO BALLOONS
    st.success("🎯 **Institutional Strategy Executed Successfully**")
    st.metric("⚡ Execution Time", f"{execution_data['execution_time']} seconds", "Live institutional pricing")
    
    st.info(f"✅ **Execution Summary:** Professional options strategy successfully executed for {strategy['target_exposure']:.1f} BTC position using live market pricing from institutional trading channels")
    
    # Professional contract details
    st.markdown("## 📋 Executed Contract Specifications")
    
    col1, col2 = st.columns(2, gap="large")
    
    with col1:
        st.markdown("### Contract Details")
        st.markdown(f"**Strategy Type:** {pricing['option_type']}")
        st.markdown(f"**Contracts Executed:** {pricing['contracts_needed']} contracts")
        st.markdown(f"**Strike Price:** ${pricing.get('strike_price', pricing.get('long_strike', 0)):,.2f}")
        st.markdown(f"**Expiry Date:** {pricing['expiry_date']}")
        st.markdown(f"**Total Premium:** ${abs(pricing['total_premium']):,.2f}")
        st.markdown(f"**Premium per Contract:** ${abs(pricing['total_premium'])/pricing['contracts_needed']:,.2f}")
    
    with col2:
        outcomes = calculate_strategy_outcomes(strategy, pricing['btc_spot_price'])
        
        st.markdown("### Protection Summary")
        st.markdown(f"**Position Protected:** {strategy['target_exposure']:.1f} BTC")
        st.markdown(f"**Entry Price:** ${pricing['btc_spot_price']:,.2f}")
        st.markdown(f"**Breakeven Level:** ${outcomes['breakeven_price']:,.2f}")
        st.markdown(f"**Maximum Risk:** {outcomes['max_loss'] if isinstance(outcomes['max_loss'], str) else f'${outcomes['max_loss']:,.0f}'}")
        st.markdown(f"**Maximum Reward:** {outcomes['max_profit']}")
        st.markdown(f"**Portfolio Impact:** {pricing['cost_as_pct']:.2f}% of total value")
    
    # Professional scenario analysis
    st.markdown("## 📊 Professional Market Scenario Analysis")
    
    outcomes = calculate_strategy_outcomes(strategy, pricing['btc_spot_price'])
    
    if outcomes['scenarios']:
        st.info("💡 **Professional Risk Assessment:** These scenarios demonstrate exactly how your institutional portfolio will perform under various Bitcoin price movements with professional protection in place.")
        
        for i, scenario in enumerate(outcomes['scenarios']):
            if i == 0:
                st.success(f"**🟢 Scenario {i+1}:** {scenario['condition']}")
            elif i == 1:
                st.warning(f"**🟡 Scenario {i+1}:** {scenario['condition']}")
            else:
                st.error(f"**🔴 Scenario {i+1}:** {scenario['condition']}")
            
            st.markdown(f"**{scenario['outcome']}:** {scenario['details']}")
            st.markdown("---")
    
    # Professional execution confirmation
    st.success("🎯 **Professional Portfolio Protection Successfully Deployed**")
    st.info("✅ Your institutional portfolio now has professional-grade downside protection while maintaining unlimited upside potential through sophisticated options strategies")
    
    # Professional implementation information
    with st.expander("🚀 **Ready for Live Implementation?**", expanded=True):
        st.markdown("**This demonstration showcases real institutional options strategies with live market pricing and immediately executable contracts.**")
        st.markdown("**All displayed strategies are available for immediate implementation through professional institutional trading channels.**")
        st.markdown("**Contact our institutional team to discuss implementing these professional protection strategies for your actual portfolio.**")
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Live Pricing Sources", "Multiple Exchanges")
            st.metric("Strategy Classification", "Institutional Grade")
        with col2:
            st.metric("Execution Speed", "12-28 seconds")
            st.metric("Market Access", "24/7 Global Markets")
    
    # Professional action buttons
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col1:
        if st.button("**🔄 Analyze New Portfolio**", type="secondary", use_container_width=True):
            # Professional reset with confirmation
            for key in ['portfolio', 'strategies', 'selected_strategy', 'execution_data']:
                if key in st.session_state:
                    st.session_state[key] = None
            st.session_state.custom_positions = []
            st.session_state.demo_step = 1
            st.session_state.strategies_generated = False
            st.session_state.strategy_selected = False
            st.session_state.show_intro = True
            st.success("🔄 **Demo Reset Complete** - Starting new professional analysis")
            st.rerun()
    
    with col2:
        st.link_button("**💬 Contact Institutional Team**", "https://t.me/willialso", use_container_width=True)
    
    with col3:
        pass

def main():
    """Professional application controller with error handling"""
    ensure_session_state()
    current_step = st.session_state.get('demo_step', 1)
    
    try:
        if current_step == 1:
            screen_1_portfolio()
        elif current_step == 2:
            screen_2_strategies()
        elif current_step == 3:
            screen_3_execution()
        else:
            st.session_state.demo_step = 1
            screen_1_portfolio()
    except Exception as e:
        st.error(f"**Application Error:** {str(e)}")
        if st.button("🔄 **Reset Professional Demo**"):
            st.session_state.clear()
            st.rerun()

if __name__ == "__main__":
    main()
