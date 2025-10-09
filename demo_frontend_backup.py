"""
ATTICUS PROFESSIONAL - FINAL POLISHED VERSION  
✅ Strategy doubling completely eliminated
✅ Exchange field removed from execution
✅ IV removed (kept in backend only)
✅ Detailed price scenario outcomes
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
    page_title="Atticus Professional",
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
        'strategy_selected': False  # NEW: Track strategy selection
    }
    
    for key, default_value in required_keys.items():
        if key not in st.session_state:
            st.session_state[key] = default_value

ensure_session_state()

# Live pricing functions (same as before)
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
    """Calculate detailed outcome scenarios for different price ranges"""
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
                    'details': f'Long position profits minus ${premium:,.0f} premium cost'
                },
                {
                    'condition': f'BTC between ${breakeven:,.0f} - ${strike:,.0f}',
                    'outcome': 'Partial loss',
                    'details': f'Loss limited to premium paid: ${premium:,.0f}'
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
        max_spread_profit = (long_strike - short_strike) * target_btc - premium
        
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
        enhanced_return_price = current_price + (income / target_btc)
        
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
                    'details': f'BTC called away, total return capped at ${strike - current_price:,.0f}/BTC + income'
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
                    'details': f'Short position profits minus ${premium:,.0f} premium cost'
                },
                {
                    'condition': f'BTC between ${breakeven:,.0f} - ${strike:,.0f}',
                    'outcome': 'Partial loss',
                    'details': f'Loss limited to premium paid: ${premium:,.0f}'
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
    
    # Fallback for unknown strategies
    return {
        'scenarios': [],
        'max_loss': abs(pricing['total_premium']),
        'max_profit': 'Strategy dependent',
        'breakeven_price': current_price
    }

def generate_dynamic_strategies(net_btc, current_price):
    """Generate strategies dynamically based on live market conditions"""
    if not current_price:
        return []
    
    market_conditions = get_live_market_conditions()
    contracts_needed = int(abs(net_btc))
    
    strategies = []
    
    # Strategy 1: Protective Put
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
                    'implied_volatility': put_data['implied_volatility'],  # Keep for backend
                    'days_to_expiry': 7,
                    'expiry_date': (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d"),
                    'option_type': 'European Put Options',
                    'cost_as_pct': (contracts_needed * put_data['premium']) / (abs(net_btc) * current_price) * 100
                }
            }
        })
    
    # Strategy 2: Put Spread
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
    
    # Strategy 3: Covered Call (Profit Generator)
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
    
    # Strategy 4: Cash-Secured Put (Profit Generator)
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
    
    # Strategy 5: Protective Call (For short positions)
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

# CSS (same as before)
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        color: #f1f5f9 !important;
    }
    
    .top-disclaimer {
        background: linear-gradient(135deg, #1e293b 0%, #475569 100%);
        border-bottom: 2px solid #fbbf24;
        padding: 0.8rem 2rem;
        margin: 0;
        width: 100%;
        position: fixed;
        top: 0;
        left: 0;
        z-index: 1000;
        text-align: center;
    }
    
    .top-disclaimer p {
        color: #fbbf24 !important;
        font-size: 0.95rem;
        margin: 0;
        line-height: 1.3;
        font-weight: 500;
    }
    
    .main .block-container {
        padding-top: 4rem !important;
        max-width: 1200px !important;
    }
    
    .main-header {
        text-align: center;
        margin: 2rem 0 3rem 0;
        padding: 1rem;
    }
    
    .portfolio-sections {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 2.5rem;
        margin: 2rem 0;
    }
    
    @media (max-width: 768px) {
        .portfolio-sections {
            grid-template-columns: 1fr;
            gap: 1.5rem;
        }
    }
    
    .atticus-card {
        background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
        border: 1px solid #475569;
        border-radius: 12px;
        padding: 2rem;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        height: fit-content;
        min-height: 350px;
    }
    
    .atticus-card h4 {
        color: #fbbf24 !important;
        font-size: 1.5rem;
        margin-bottom: 1.5rem;
        text-align: center;
    }
    
    .position-item {
        background: #0f172a;
        border: 1px solid #475569;
        border-radius: 8px;
        padding: 0.8rem;
        margin: 0.5rem 0;
        display: flex;
        align-items: center;
        justify-content: space-between;
    }
    
    .position-item p {
        margin: 0;
        color: #f8fafc !important;
    }
    
    .position-summary {
        background: #1e293b;
        border: 1px solid #fbbf24;
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
        display: grid;
        grid-template-columns: 1fr 1fr 1fr;
        gap: 0.5rem;
        text-align: center;
    }
    
    .metric-item {
        padding: 0.5rem;
    }
    
    .metric-label {
        color: #cbd5e1 !important;
        font-size: 0.85rem;
        margin-bottom: 0.2rem;
    }
    
    .metric-value {
        color: #fbbf24 !important;
        font-size: 1rem;
        font-weight: 600;
    }
    
    [data-testid="metric-container"] {
        background: #1e293b;
        border: 1px solid #475569;
        border-radius: 8px;
        padding: 0.8rem;
        margin: 0.3rem 0;
    }
    
    [data-testid="metric-container"] [data-testid="metric-value"] {
        color: #fbbf24 !important;
        font-size: 1.1rem !important;
        font-weight: 600;
        line-height: 1.2;
    }
    
    [data-testid="metric-container"] [data-testid="metric-label"] {
        color: #cbd5e1 !important;
        font-size: 0.85rem !important;
    }
    
    .live-price {
        background: #10b981;
        color: white;
        padding: 0.4rem 1rem;
        border-radius: 20px;
        font-size: 1rem;
        font-weight: 600;
        display: inline-block;
        margin: 0.5rem 0 1.5rem 0;
    }
    
    .strategy-card {
        background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
        border: 2px solid #fbbf24;
        border-radius: 12px;
        padding: 2rem;
        margin: 1.5rem 0;
    }
    
    .options-detail-box {
        background: #0f172a;
        border: 2px solid #10b981;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
    }
    
    .options-detail-box h5 {
        color: #10b981 !important;
        font-size: 1.3rem;
        margin-bottom: 1rem;
    }
    
    .options-detail-box p {
        color: #f8fafc !important;
        font-size: 1rem;
        margin-bottom: 0.5rem;
        line-height: 1.4;
    }
    
    .scenario-box {
        background: #1e293b;
        border: 1px solid #475569;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
    }
    
    .scenario-box h6 {
        color: #fbbf24 !important;
        margin: 0 0 0.5rem 0;
        font-size: 1rem;
    }
    
    .scenario-box p {
        color: #f8fafc !important;
        margin: 0;
        font-size: 0.9rem;
    }
    
    .execution-success {
        background: linear-gradient(135deg, #059669 0%, #10b981 100%);
        padding: 2rem;
        border-radius: 12px;
        color: white;
        text-align: center;
        margin: 2rem 0;
    }
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

def show_disclaimer_and_header():
    st.markdown("""
    <div class="top-disclaimer">
        <p><strong>Live Demo Platform</strong> • Real-time BTC pricing • Dynamic options strategies • Live market conditions</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="main-header">
        <img src="https://i.ibb.co/qFNCZsWG/attpro.png" width="400" alt="Atticus Professional">
        <p style="color: #e2e8f0; font-size: 1.2rem; text-align: center; margin-top: 1rem;">Professional Options Strategies for Institutional Portfolios</p>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")

def screen_1_portfolio():
    show_disclaimer_and_header()
    
    # RESET strategy selection state completely
    st.session_state.strategy_selected = False
    st.session_state.selected_strategy = None
    
    live_btc_price = get_live_btc_price()
    
    if live_btc_price is None:
        st.error("⚠️ Unable to fetch live BTC price from any exchange. Please check your internet connection.")
        return
    
    market_conditions = get_live_market_conditions()
    
    st.markdown(f'''
    <div class="live-price">
        🔴 LIVE: BTC ${live_btc_price:,.2f} | 
        📊 Vol: {market_conditions['implied_volatility']*100:.0f}% | 
        📈 7D: {market_conditions['price_trend_7d']*100:+.1f}%
    </div>
    ''', unsafe_allow_html=True)
    
    st.markdown('<div class="portfolio-sections">', unsafe_allow_html=True)
    
    # LEFT SECTION
    st.markdown("""
    <div class="atticus-card">
        <h4>📊 Institutional BTC Portfolio Options</h4>
    """, unsafe_allow_html=True)
    
    fund_type = st.radio("Institution Type:", ["Small Fund ($20-50M)", "Mid-Cap Fund ($50-200M)"], horizontal=True)
    
    if st.button("🎯 Generate Portfolio", type="primary", use_container_width=True, key="gen_inst"):
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
            st.success(f"✅ Portfolio Generated | {btc_size:.1f} BTC @ ${live_btc_price:,.2f}")
            time.sleep(1)
            st.rerun()
    
    if st.session_state.portfolio and st.session_state.portfolio_source == 'generated':
        portfolio = st.session_state.portfolio
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("AUM", f"${portfolio['aum']/1000000:.0f}M")
            st.metric("BTC Exposure", f"{portfolio['total_btc_size']:.1f}")
        with col2:
            st.metric("Position Value", f"${portfolio['total_current_value']/1000000:.1f}M")
            st.metric("P&L", f"${portfolio['total_pnl']/1000000:.1f}M")
        
        if st.button("📊 Analyze Portfolio", type="primary", use_container_width=True, key="analyze_gen"):
            st.session_state.demo_step = 2
            st.session_state.current_page = 'strategies'
            st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # RIGHT SECTION
    st.markdown("""
    <div class="atticus-card">
        <h4>⚡ Custom BTC Position Builder</h4>
    """, unsafe_allow_html=True)
    
    with st.form("position_entry", clear_on_submit=True):
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            btc_amount = st.number_input("BTC Amount", min_value=0.1, max_value=1000.0, value=25.0, step=0.1)
        with col2:
            position_type = st.selectbox("Position", ["Long", "Short"])
        with col3:
            st.write("") 
            add_position = st.form_submit_button("Add Position", type="primary")
    
    col1, col2 = st.columns(2)
    with col2:
        if st.button("🗑️ Clear All", type="secondary", use_container_width=True):
            st.session_state.custom_positions = []
            st.rerun()
    
    if add_position and btc_amount > 0:
        new_position = {'btc_amount': btc_amount, 'position_type': position_type}
        st.session_state.custom_positions.append(new_position)
        st.rerun()
    
    if st.session_state.custom_positions:
        st.markdown("**📋 Current Positions**")
        
        total_long = sum(pos['btc_amount'] for pos in st.session_state.custom_positions if pos['position_type'] == 'Long')
        total_short = sum(pos['btc_amount'] for pos in st.session_state.custom_positions if pos['position_type'] == 'Short')
        
        for i, pos in enumerate(st.session_state.custom_positions):
            st.markdown(f"""
            <div class="position-item">
                <p><strong>{pos['btc_amount']:.1f} BTC</strong> • {'🟢 Long' if pos['position_type'] == 'Long' else '🔴 Short'} • ${pos['btc_amount'] * live_btc_price:,.0f}</p>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("Remove", key=f"remove_{i}", type="secondary"):
                st.session_state.custom_positions.pop(i)
                st.rerun()
        
        net_btc = total_long - total_short
        total_value = (total_long + total_short) * live_btc_price
        
        st.markdown(f"""
        <div class="position-summary">
            <div class="metric-item">
                <div class="metric-label">Long BTC</div>
                <div class="metric-value">{total_long:.1f}</div>
            </div>
            <div class="metric-item">
                <div class="metric-label">Short BTC</div>
                <div class="metric-value">{total_short:.1f}</div>
            </div>
            <div class="metric-item">
                <div class="metric-label">Net BTC</div>
                <div class="metric-value">{net_btc:+.1f}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("⚡ Analyze Positions", type="primary", use_container_width=True):
            custom_portfolio = {
                'aum': abs(net_btc) * live_btc_price * 4,
                'total_btc_size': abs(net_btc),
                'net_btc_exposure': net_btc,
                'gross_btc_exposure': total_long + total_short,
                'total_current_value': total_value,
                'total_pnl': total_value * 0.08,
                'current_btc_price': live_btc_price
            }
            st.session_state.portfolio = custom_portfolio
            st.session_state.portfolio_source = 'custom'
            st.session_state.strategies = None
            st.session_state.strategies_generated = False
            st.session_state.demo_step = 2
            st.session_state.current_page = 'strategies'
            st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

def screen_2_strategies():
    show_disclaimer_and_header()
    
    ensure_session_state()
    
    if not st.session_state.portfolio:
        st.error("Please create a portfolio first")
        return
    
    portfolio = st.session_state.portfolio
    net_btc = portfolio.get('net_btc_exposure', 0)
    current_price = portfolio.get('current_btc_price', get_live_btc_price())
    
    if current_price is None:
        st.error("Unable to fetch current BTC price")
        return
    
    market_conditions = get_live_market_conditions()
    position_direction = "Long" if net_btc > 0 else "Short" if net_btc < 0 else "Neutral"
    
    st.info(f"📊 Portfolio: {abs(net_btc):.1f} BTC {position_direction} | 🔴 ${current_price:,.2f} | 📈 {market_conditions['market_regime'].title()} Market")
    st.markdown(f"### Dynamic Options Strategies - {abs(net_btc):.1f} BTC")
    
    if not st.session_state.strategies_generated:
        with st.spinner("Generating live strategies based on current market conditions... (30-45 seconds)"):
            time.sleep(2)
            st.session_state.strategies = generate_dynamic_strategies(net_btc, current_price)
            st.session_state.strategies_generated = True
    
    # FIXED: Only show strategies if not selected
    if (st.session_state.strategies and 
        not st.session_state.strategy_selected and 
        not st.session_state.selected_strategy):
        
        for i, strategy in enumerate(st.session_state.strategies):
            priority_emoji = "🔥" if strategy['priority'] == 'high' else "⭐" if strategy['priority'] == 'medium' else "💡"
            
            strategy_display = strategy['strategy_name'].replace('_', ' ').title()
            if 'covered_call' in strategy['strategy_name'] or 'cash_secured_put' in strategy['strategy_name']:
                strategy_display += " (Profit Generator)"
            
            st.markdown(f"""
            <div class="strategy-card">
                <h4>{priority_emoji} {strategy_display}</h4>
                <p><strong>Coverage:</strong> {strategy['target_exposure']:.1f} BTC</p>
                <p><strong>Purpose:</strong> {strategy['rationale']}</p>
            </div>
            """, unsafe_allow_html=True)
            
            pricing = strategy['pricing']['live_pricing']
            
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
                st.info(f"**Expiry**\n{pricing['days_to_expiry']} days")
            with col4:
                if st.button("Execute Strategy", key=f"exec_{i}", type="primary"):
                    # FIXED: Immediately set flags and transition
                    st.session_state.selected_strategy = strategy
                    st.session_state.strategy_selected = True
                    st.session_state.execution_data = {
                        'btc_price_at_execution': current_price,
                        'execution_time': random.randint(12, 28),
                        'timestamp': datetime.now().isoformat()
                    }
                    st.session_state.demo_step = 3
                    st.session_state.current_page = 'execution'
                    # Force immediate transition
                    st.rerun()
            
            st.markdown("---")
    
    # Show transition message if strategy selected
    elif st.session_state.strategy_selected:
        st.info("✅ Strategy selected! Proceeding to execution...")
        time.sleep(1)
        st.session_state.demo_step = 3
        st.rerun()
    
    if st.button("← Back to Portfolio", type="secondary"):
        st.session_state.demo_step = 1
        st.session_state.current_page = 'portfolio'
        st.session_state.strategies = None
        st.session_state.selected_strategy = None
        st.session_state.strategies_generated = False
        st.session_state.strategy_selected = False
        st.rerun()

def screen_3_execution():
    show_disclaimer_and_header()
    
    ensure_session_state()
    
    if not st.session_state.selected_strategy:
        st.error("Strategy not selected")
        return
    
    strategy = st.session_state.selected_strategy
    execution_data = st.session_state.execution_data
    pricing = strategy['pricing']['live_pricing']
    
    st.markdown("### Strategy Execution")
    
    with st.spinner("Executing with live institutional pricing..."):
        time.sleep(2)
    
    st.success("✅ EXECUTION COMPLETE")
    st.metric("Execution Time", f"{execution_data['execution_time']} seconds")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # FIXED: Removed Exchange field and IV field
        st.markdown(f"""
        <div class="options-detail-box">
            <h5>📋 Contract Details</h5>
            <p><strong>Contracts:</strong> {pricing['contracts_needed']} × {pricing['option_type']}</p>
            <p><strong>Strike:</strong> ${pricing.get('strike_price', pricing.get('long_strike', 0)):,.2f}</p>
            <p><strong>Expiry:</strong> {pricing['expiry_date']}</p>
            <p><strong>Premium:</strong> ${abs(pricing['total_premium']):,.2f}</p>
            <p><strong>Market:</strong> Live institutional pricing</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        # FIXED: Detailed price scenarios instead of generic outcomes
        outcomes = calculate_strategy_outcomes(strategy, pricing['btc_spot_price'])
        
        st.markdown(f"""
        <div class="options-detail-box">
            <h5>📈 Strategy Outcomes</h5>
            <p><strong>Entry Price:</strong> ${pricing['btc_spot_price']:,.2f}</p>
            <p><strong>Breakeven:</strong> ${outcomes['breakeven_price']:,.2f}</p>
            <p><strong>Max Loss:</strong> {outcomes['max_loss'] if isinstance(outcomes['max_loss'], str) else f"${outcomes['max_loss']:,.0f}"}</p>
            <p><strong>Max Profit:</strong> {outcomes['max_profit']}</p>
        </div>
        """, unsafe_allow_html=True)
    
    # FIXED: Detailed price scenario breakdown
    st.markdown("### 📊 Price Scenarios")
    
    outcomes = calculate_strategy_outcomes(strategy, pricing['btc_spot_price'])
    
    for i, scenario in enumerate(outcomes['scenarios']):
        st.markdown(f"""
        <div class="scenario-box">
            <h6>💹 {scenario['condition']}</h6>
            <p><strong>{scenario['outcome']}:</strong> {scenario['details']}</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="execution-success">
        <h3>✅ INSTITUTIONAL STRATEGY EXECUTED</h3>
        <p>Professional options executed with live market pricing and detailed outcome scenarios</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 New Analysis", type="primary", use_container_width=True):
            for key in ['portfolio', 'strategies', 'selected_strategy', 'execution_data']:
                if key in st.session_state:
                    st.session_state[key] = None
            st.session_state.custom_positions = []
            st.session_state.demo_step = 1
            st.session_state.current_page = 'portfolio'
            st.session_state.strategies_generated = False
            st.session_state.strategy_selected = False
            st.rerun()
    
    with col2:
        st.link_button("💬 Contact Telegram", "https://t.me/willialso", use_container_width=True)

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
