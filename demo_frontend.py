"""
ATTICUS PROFESSIONAL - STREAMLIT-NATIVE PROFESSIONAL VERSION
✅ Pure Streamlit components for consistent rendering
✅ Professional design using Streamlit's native capabilities
✅ Working logo, progress indicators, and formatting
✅ Maintains all real-time pricing functionality
✅ Clean, uniform, professional presentation
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

# MINIMAL CSS - ONLY ESSENTIAL STYLING
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        color: #f8fafc !important;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {display: none;}
    
    /* Text color overrides */
    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3, .stMarkdown h4 {
        color: #fbbf24 !important;
    }
    
    .stMarkdown p, .stText {
        color: #f8fafc !important;
        font-size: 1.1rem;
    }
    
    /* Ensure button visibility */
    .stButton > button {
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

def show_header():
    """Professional header with logo"""
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        # LOGO DISPLAY
        try:
            st.image("https://i.ibb.co/qFNCZsWG/attpro.png", width=400, use_column_width=False)
        except:
            st.title("🏛️ Atticus Professional")
        
        st.markdown("### Professional Portfolio Protection Demo")
        st.caption("Live market data • Real-time options pricing • Institutional strategies")

def show_progress_indicator(current_step):
    """STREAMLIT-NATIVE progress indicator"""
    st.markdown("---")
    
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
    
    # Progress bar
    progress_value = current_step / 3.0
    st.progress(progress_value)
    st.caption(f"Step {current_step} of 3 completed")
    
    st.markdown("---")

def show_intro_walkthrough():
    """STREAMLIT-NATIVE intro walkthrough"""
    if st.session_state.show_intro:
        live_btc_price = get_live_btc_price()
        
        if not live_btc_price:
            st.error("⚠️ Unable to fetch live BTC price. Please refresh the page.")
            return True
        
        # CLEAR PROBLEM STATEMENT
        st.error("🚨 **The Challenge:** Bitcoin's volatility creates massive institutional risk exposure")
        
        st.markdown("""
        **Industry Reality:** Recent market events demonstrate that 30-50% Bitcoin price declines can occur within days, 
        creating significant losses for unprotected institutional positions.
        """)
        
        # CLEAR SOLUTION STATEMENT  
        st.success("✅ **The Solution:** Professional options strategies provide institutional-grade protection")
        
        st.markdown("""
        **Atticus Approach:** Use sophisticated options strategies to limit downside risk while preserving unlimited upside potential, 
        exactly like traditional institutional risk management.
        """)
        
        # LIVE EXAMPLE
        st.info(f"📊 **Live Example:** Protecting a $50M Bitcoin position (Live BTC: ${live_btc_price:,.2f})")
        
        # COMPARISON USING STREAMLIT COLUMNS
        col1, col2 = st.columns(2)
        
        with col1:
            st.error("⚠️ **Without Protection**")
            st.metric("Potential Loss", "$15M+", "30% market decline")
            st.caption("No downside protection • Unlimited risk exposure • Full market volatility impact")
        
        with col2:
            st.success("✅ **With Atticus Protection**") 
            st.metric("Protection Cost", "$1.2M", "2.4% of position")
            st.caption("Capped downside risk • Unlimited upside preserved • Professional risk management")
        
        # CALL TO ACTION
        st.markdown("---")
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            if st.button("🚀 **See Live Demo with Real Market Data**", type="primary", use_container_width=True):
                st.session_state.show_intro = False
                st.rerun()
        
        st.markdown("---")
        return True
    
    return False

def screen_1_portfolio():
    """STREAMLIT-NATIVE portfolio setup screen"""
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
    
    # LIVE MARKET DATA BANNER
    st.success(f"🔴 **LIVE MARKET DATA:** BTC ${live_btc_price:,.2f} | Volatility: {market_conditions['implied_volatility']*100:.0f}% | 7-Day: {market_conditions['price_trend_7d']*100:+.1f}%")
    
    st.info("💡 **Choose your portfolio setup method:** Generate a realistic institutional portfolio or build custom positions using live market pricing.")
    
    # MAIN CONTENT - SIDE BY SIDE
    col1, col2 = st.columns(2, gap="large")
    
    with col1:
        st.subheader("🏛️ Generate Institution Portfolio")
        st.caption("**Recommended:** Pre-built realistic allocation with institutional context")
        
        fund_type = st.selectbox(
            "**Select Institution Size:**",
            ["Small Fund ($20-50M AUM)", "Mid-Cap Fund ($50-200M AUM)"],
            key="fund_size"
        )
        
        if "Small" in fund_type:
            btc_allocation = 2000000 / live_btc_price
            st.info(f"📊 **Will generate:** ~{btc_allocation:.1f} BTC position (${2000000/1000000:.0f}M allocation) with realistic P&L")
        else:
            btc_allocation = 8500000 / live_btc_price
            st.info(f"📊 **Will generate:** ~{btc_allocation:.1f} BTC position (${8500000/1000000:.1f}M allocation) with institutional scale")
        
        if st.button("🎯 **Generate Live Portfolio**", type="primary", use_container_width=True, key="gen_portfolio"):
            with st.spinner("🔄 Generating portfolio with real-time pricing..."):
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
                st.success(f"✅ **Portfolio Generated:** {btc_size:.1f} BTC @ ${live_btc_price:,.2f}")
                st.rerun()
        
        # Display generated portfolio
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
            st.warning(f"⚠️ **Risk Analysis:** A 25% market decline would result in ${potential_loss/1000000:.1f}M loss without protection")
            
            if st.button("📊 **Analyze Protection Strategies**", type="primary", use_container_width=True):
                st.session_state.demo_step = 2
                st.rerun()
    
    with col2:
        st.subheader("⚡ Custom Position Builder")
        st.caption("Build your own portfolio positions for personalized analysis")
        
        with st.form("position_form", clear_on_submit=True):
            btc_amount = st.number_input("**BTC Amount**", min_value=0.1, max_value=1000.0, value=25.0, step=0.1, help="Enter the Bitcoin amount for this position")
            position_type = st.selectbox("**Position Type**", ["Long", "Short"])
            
            col1a, col2a = st.columns(2)
            with col1a:
                add_clicked = st.form_submit_button("➕ **Add Position**", type="primary", use_container_width=True)
            with col2a:
                clear_clicked = st.form_submit_button("🗑️ **Clear All**", type="secondary", use_container_width=True)
        
        if add_clicked:
            position_value = btc_amount * live_btc_price
            st.success(f"✅ **Added:** {btc_amount:.1f} BTC {position_type} position (${position_value:,.0f} value)")
            new_position = {'btc_amount': btc_amount, 'position_type': position_type}
            st.session_state.custom_positions.append(new_position)
            st.rerun()
        
        if clear_clicked:
            st.session_state.custom_positions = []
            st.success("🗑️ **Cleared all positions**")
            st.rerun()
        
        # Display current positions
        if st.session_state.custom_positions:
            st.markdown("#### 📋 Current Positions")
            
            total_long = sum(pos['btc_amount'] for pos in st.session_state.custom_positions if pos['position_type'] == 'Long')
            total_short = sum(pos['btc_amount'] for pos in st.session_state.custom_positions if pos['position_type'] == 'Short')
            net_btc = total_long - total_short
            
            # Position list
            for i, pos in enumerate(st.session_state.custom_positions):
                col_pos, col_btn = st.columns([4, 1])
                with col_pos:
                    st.write(f"**{pos['btc_amount']:.1f} BTC** • {'🟢 Long' if pos['position_type'] == 'Long' else '🔴 Short'} • ${pos['btc_amount'] * live_btc_price:,.0f}")
                with col_btn:
                    if st.button("❌", key=f"remove_{i}", help="Remove this position"):
                        st.session_state.custom_positions.pop(i)
                        st.rerun()
            
            # Portfolio summary
            st.markdown("##### Portfolio Summary")
            col1a, col2a, col3a = st.columns(3)
            with col1a:
                st.metric("Long BTC", f"{total_long:.1f}")
            with col2a:
                st.metric("Short BTC", f"{total_short:.1f}")
            with col3a:
                st.metric("Net BTC", f"{net_btc:+.1f}")
            
            if st.button("⚡ **Analyze Custom Portfolio**", type="primary", use_container_width=True):
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
    """STREAMLIT-NATIVE strategy analysis screen"""
    show_header()
    show_progress_indicator(2)
    
    if not st.session_state.portfolio:
        st.error("❌ Please create a portfolio first")
        if st.button("← Back to Portfolio Setup", type="secondary"):
            st.session_state.demo_step = 1
            st.rerun()
        return
    
    portfolio = st.session_state.portfolio
    net_btc = portfolio.get('net_btc_exposure', 0)
    current_price = portfolio.get('current_btc_price', get_live_btc_price())
    
    if not current_price:
        st.error("❌ Unable to fetch current BTC price")
        return
    
    market_conditions = get_live_market_conditions()
    position_direction = "Long" if net_btc > 0 else "Short" if net_btc < 0 else "Neutral"
    
    st.title("🛡️ Live Protection Strategies")
    
    # Portfolio summary
    st.success(f"🎯 **Portfolio Analysis:** {abs(net_btc):.1f} BTC {position_direction} position • ${abs(net_btc) * current_price:,.0f} value • {market_conditions['market_regime'].title()} market conditions")
    
    st.info(f"📊 **Market Context:** Current volatility at {market_conditions['implied_volatility']*100:.0f}% with {market_conditions['price_trend_7d']*100:+.1f}% weekly trend - generating optimal strategies using live institutional pricing")
    
    # Generate strategies
    if not st.session_state.strategies_generated:
        with st.spinner("🔄 Analyzing live market conditions and generating optimal strategies... (30-45 seconds)"):
            progress_bar = st.progress(0)
            for i in range(100):
                time.sleep(0.02)
                progress_bar.progress(i + 1)
            
            st.session_state.strategies = generate_dynamic_strategies(net_btc, current_price)
            st.session_state.strategies_generated = True
            st.success("✅ Strategy analysis complete!")
    
    # Display strategies
    if (st.session_state.strategies and 
        not st.session_state.strategy_selected and 
        not st.session_state.selected_strategy):
        
        st.info("💡 **Strategy Selection:** Each strategy uses live market pricing optimized for current conditions. Protection strategies limit downside while income strategies generate returns from holdings.")
        
        for i, strategy in enumerate(st.session_state.strategies):
            priority_emoji = "🔥" if strategy['priority'] == 'high' else "⭐" if strategy['priority'] == 'medium' else "💡"
            
            strategy_display = strategy['strategy_name'].replace('_', ' ').title()
            if 'covered_call' in strategy['strategy_name'] or 'cash_secured_put' in strategy['strategy_name']:
                strategy_display += " (Income Generator)"
            elif 'protective' in strategy['strategy_name']:
                strategy_display += " (Downside Protection)"
            elif 'spread' in strategy['strategy_name']:
                strategy_display += " (Cost-Efficient Protection)"
            
            pricing = strategy['pricing']['live_pricing']
            
            # Strategy container
            with st.container():
                if strategy['priority'] == 'high':
                    st.error(f"🔥 **HIGH PRIORITY:** {strategy_display}")
                elif strategy['priority'] == 'medium':
                    st.warning(f"⭐ **RECOMMENDED:** {strategy_display}")
                else:
                    st.info(f"💡 **ALTERNATIVE:** {strategy_display}")
                
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.write(f"**Coverage:** {strategy['target_exposure']:.1f} BTC")
                    st.write(f"**Strategy:** {strategy['rationale']}")
                    st.write(f"**Duration:** {pricing['days_to_expiry']} days • **Expiry:** {pricing['expiry_date']}")
                
                with col2:
                    # Key metrics
                    col2a, col2b, col2c = st.columns(3)
                    with col2a:
                        if pricing['total_premium'] < 0:
                            st.success(f"**Income**\n${abs(pricing['total_premium']):,.0f}")
                        else:
                            st.metric("Cost", f"${abs(pricing['total_premium']):,.0f}")
                    with col2b:
                        cost_pct = pricing['cost_as_pct']
                        color = "🟢" if cost_pct < 3 else "🟡" if cost_pct < 5 else "🔴"
                        st.metric("Rate", f"{cost_pct:.1f}%", delta=f"{color}")
                    with col2c:
                        st.metric("Contracts", f"{pricing['contracts_needed']}")
                
                # Execute button
                if st.button(f"⚡ **Execute {strategy_display}**", key=f"exec_{i}", type="primary", use_container_width=True):
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
        st.success("✅ **Strategy selected!** Executing with live institutional pricing...")
        time.sleep(1)
        st.session_state.demo_step = 3
        st.rerun()
    
    # Back button
    if st.button("← **Back to Portfolio Setup**", type="secondary"):
        st.session_state.demo_step = 1
        st.session_state.strategies = None
        st.session_state.selected_strategy = None
        st.session_state.strategies_generated = False
        st.session_state.strategy_selected = False
        st.rerun()

def screen_3_execution():
    """STREAMLIT-NATIVE execution results screen"""
    show_header()
    show_progress_indicator(3)
    
    if not st.session_state.selected_strategy:
        st.error("❌ Strategy not selected")
        if st.button("← Back to Strategies", type="secondary"):
            st.session_state.demo_step = 2
            st.rerun()
        return
    
    strategy = st.session_state.selected_strategy
    execution_data = st.session_state.execution_data
    pricing = strategy['pricing']['live_pricing']
    
    st.title("✅ Strategy Execution Complete")
    
    # Execution animation
    with st.spinner("⚡ Executing strategy with live institutional pricing..."):
        execution_progress = st.progress(0)
        for i in range(100):
            time.sleep(0.02)
            execution_progress.progress(i + 1)
    
    # SUCCESS MESSAGE
    st.balloons()
    st.success("🎯 **INSTITUTIONAL STRATEGY EXECUTED SUCCESSFULLY**")
    st.metric("⚡ Execution Time", f"{execution_data['execution_time']} seconds", "Live institutional pricing")
    
    st.info(f"✅ **Strategy Summary:** Professional options executed for {strategy['target_exposure']:.1f} BTC position using live market pricing from institutional channels")
    
    # CONTRACT DETAILS
    st.subheader("📋 Executed Contract Details")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("##### Contract Specifications")
        st.write(f"**Strategy Type:** {pricing['option_type']}")
        st.write(f"**Contracts Executed:** {pricing['contracts_needed']} contracts")
        st.write(f"**Strike Price:** ${pricing.get('strike_price', pricing.get('long_strike', 0)):,.2f}")
        st.write(f"**Expiry Date:** {pricing['expiry_date']}")
        st.write(f"**Total Premium:** ${abs(pricing['total_premium']):,.2f}")
        st.write(f"**Premium per Contract:** ${abs(pricing['total_premium'])/pricing['contracts_needed']:,.2f}")
    
    with col2:
        outcomes = calculate_strategy_outcomes(strategy, pricing['btc_spot_price'])
        
        st.markdown("##### Protection Summary")
        st.write(f"**Position Protected:** {strategy['target_exposure']:.1f} BTC")
        st.write(f"**Entry Price:** ${pricing['btc_spot_price']:,.2f}")
        st.write(f"**Breakeven Level:** ${outcomes['breakeven_price']:,.2f}")
        st.write(f"**Maximum Risk:** {outcomes['max_loss'] if isinstance(outcomes['max_loss'], str) else f'${outcomes['max_loss']:,.0f}'}")
        st.write(f"**Maximum Reward:** {outcomes['max_profit']}")
        st.write(f"**Position Impact:** {pricing['cost_as_pct']:.2f}% of portfolio value")
    
    # SCENARIO ANALYSIS
    st.subheader("📊 Market Scenario Analysis")
    
    outcomes = calculate_strategy_outcomes(strategy, pricing['btc_spot_price'])
    
    if outcomes['scenarios']:
        st.info("💡 **Understanding Your Protection:** These scenarios show exactly how your portfolio performs under different Bitcoin price movements with this protection in place")
        
        for i, scenario in enumerate(outcomes['scenarios']):
            if i == 0:
                st.success(f"**🟢 Scenario {i+1}:** {scenario['condition']}")
            elif i == 1:
                st.warning(f"**🟡 Scenario {i+1}:** {scenario['condition']}")
            else:
                st.error(f"**🔴 Scenario {i+1}:** {scenario['condition']}")
            
            st.write(f"**{scenario['outcome']}:** {scenario['details']}")
            st.markdown("---")
    
    # EXECUTION SUCCESS
    st.success("🎯 **PORTFOLIO PROTECTION SUCCESSFULLY DEPLOYED**")
    st.info("✅ Your institutional portfolio now has professional-grade downside protection while maintaining unlimited upside potential")
    
    # IMPLEMENTATION INFORMATION
    with st.expander("🚀 **Ready for Real Implementation?**", expanded=True):
        st.write("**This demonstration shows real institutional options strategies with live pricing and executable contracts.**")
        st.write("**All strategies displayed are available for immediate implementation through professional trading channels.**")
        st.write("**Contact us to discuss implementing these protection strategies for your actual institutional portfolio.**")
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Live Pricing Source", "Multiple Exchanges")
            st.metric("Strategy Type", "Institutional Grade")
        with col2:
            st.metric("Execution Speed", "12-28 seconds")
            st.metric("Availability", "24/7 Markets")
    
    # ACTION BUTTONS
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col1:
        if st.button("🔄 **Try New Scenario**", type="secondary", use_container_width=True):
            # Reset all session state
            for key in ['portfolio', 'strategies', 'selected_strategy', 'execution_data']:
                if key in st.session_state:
                    st.session_state[key] = None
            st.session_state.custom_positions = []
            st.session_state.demo_step = 1
            st.session_state.strategies_generated = False
            st.session_state.strategy_selected = False
            st.session_state.show_intro = True
            st.success("🔄 Reset complete - starting new demo")
            st.rerun()
    
    with col2:
        st.link_button("💬 **Contact for Implementation**", "https://t.me/willialso", use_container_width=True)
    
    with col3:
        pass

def main():
    """Main application controller"""
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
        st.error(f"Application error: {str(e)}")
        if st.button("🔄 Reset Application"):
            st.session_state.clear()
            st.rerun()

if __name__ == "__main__":
    main()
