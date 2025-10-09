"""
ATTICUS PROFESSIONAL - RENDER PRODUCTION OPTIMIZED
✅ Guaranteed session state initialization
✅ Production-ready error handling
✅ Live pricing with proper caching
"""
import streamlit as st
import requests
import time
import random
from datetime import datetime, timedelta
import os

# Page config FIRST
st.set_page_config(
    page_title="Atticus Professional",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# GUARANTEED session state initialization
def ensure_session_state():
    """PRODUCTION: Ensure all session state variables exist"""
    required_keys = {
        'demo_step': 1,
        'portfolio': None,
        'strategies': None,
        'selected_strategy': None,
        'execution_data': None,
        'custom_positions': [],
        'portfolio_source': None,
        'current_page': 'portfolio',
        'strategies_generated': False
    }
    
    for key, default_value in required_keys.items():
        if key not in st.session_state:
            st.session_state[key] = default_value

# CRITICAL: Call immediately
ensure_session_state()

# PRODUCTION: Live pricing with robust error handling
@st.cache_data(ttl=30)
def get_live_btc_price():
    """PRODUCTION: Get live BTC price with multiple fallbacks"""
    try:
        # Primary: Coinbase
        response = requests.get("https://api.coinbase.com/v2/exchange-rates?currency=BTC", timeout=5)
        if response.status_code == 200:
            data = response.json()
            price = float(data['data']['rates']['USD'])
            if price > 10000:  # Sanity check
                return price
    except Exception as e:
        st.write(f"Coinbase API: {str(e)}")
    
    try:
        # Fallback: CoinGecko
        response = requests.get("https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd", timeout=5)
        if response.status_code == 200:
            data = response.json()
            price = float(data['bitcoin']['usd'])
            if price > 10000:  # Sanity check
                return price
    except Exception as e:
        st.write(f"CoinGecko API: {str(e)}")
    
    # Production fallback
    return 95420.0

def calculate_live_options_pricing(current_price, days_to_expiry=7):
    """Calculate realistic options pricing"""
    volatility = 0.65  # 65% IV for BTC
    time_factor = (days_to_expiry / 365.0) ** 0.5
    
    return {
        'atm_put_premium': current_price * volatility * time_factor * 0.08,
        'otm_put_premium': current_price * volatility * time_factor * 0.055,
        'atm_call_premium': current_price * volatility * time_factor * 0.082,
        'implied_volatility': volatility
    }

def generate_professional_strategies(net_btc, current_price):
    """Generate institutional-grade strategies with live pricing"""
    options_data = calculate_live_options_pricing(current_price)
    contracts_needed = int(abs(net_btc))
    
    expiry_date = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
    
    strategies = [
        {
            'strategy_name': 'protective_put',
            'target_exposure': abs(net_btc),
            'priority': 'high',
            'rationale': f'Complete downside protection for {abs(net_btc):.1f} BTC long position',
            'pricing': {
                'live_pricing': {
                    'btc_spot_price': current_price,
                    'contracts_needed': contracts_needed,
                    'strike_price': current_price * 0.95,
                    'premium_per_contract': options_data['otm_put_premium'],
                    'total_premium': contracts_needed * options_data['otm_put_premium'],
                    'implied_volatility': options_data['implied_volatility'],
                    'days_to_expiry': 7,
                    'expiry_date': expiry_date,
                    'option_type': 'European Put Options',
                    'exchange': 'Deribit / Institutional OTC',
                    'cost_as_pct': (contracts_needed * options_data['otm_put_premium']) / (abs(net_btc) * current_price) * 100
                }
            }
        },
        {
            'strategy_name': 'put_spread',
            'target_exposure': abs(net_btc),
            'priority': 'medium',
            'rationale': f'Cost-efficient protection via put spread for {abs(net_btc):.1f} BTC',
            'pricing': {
                'live_pricing': {
                    'btc_spot_price': current_price,
                    'contracts_needed': contracts_needed,
                    'long_strike': current_price * 0.95,
                    'short_strike': current_price * 0.85,
                    'long_premium': options_data['otm_put_premium'],
                    'short_premium': options_data['otm_put_premium'] * 0.4,
                    'net_premium': contracts_needed * (options_data['otm_put_premium'] - options_data['otm_put_premium'] * 0.4),
                    'total_premium': contracts_needed * (options_data['otm_put_premium'] - options_data['otm_put_premium'] * 0.4),
                    'implied_volatility': options_data['implied_volatility'],
                    'days_to_expiry': 14,
                    'expiry_date': (datetime.now() + timedelta(days=14)).strftime("%Y-%m-%d"),
                    'option_type': 'Put Spread (95%-85%)',
                    'exchange': 'Deribit / Institutional OTC',
                    'cost_as_pct': (contracts_needed * (options_data['otm_put_premium'] - options_data['otm_put_premium'] * 0.4)) / (abs(net_btc) * current_price) * 100
                }
            }
        }
    ]
    
    return strategies

# CSS
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
    }
    
    .main-header {
        text-align: center;
        margin: 2rem 0 3rem 0;
        padding: 1rem;
    }
    
    .atticus-card {
        background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
        border: 1px solid #475569;
        border-radius: 12px;
        padding: 2rem;
        margin: 1rem 0;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
    }
    
    .atticus-card h4 {
        color: #fbbf24 !important;
        font-size: 1.5rem;
        margin-bottom: 1rem;
        text-align: center;
    }
    
    .strategy-card {
        background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
        border: 2px solid #fbbf24;
        border-radius: 12px;
        padding: 2rem;
        margin: 1.5rem 0;
    }
    
    .live-price {
        background: #10b981;
        color: white;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-size: 0.9rem;
        font-weight: 600;
        display: inline-block;
        margin: 0.5rem;
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
        <p><strong>Live Demo Platform</strong> • Real-time BTC pricing • Institutional options strategies • Live market data</p>
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
    
    # Get live price
    live_btc_price = get_live_btc_price()
    
    st.markdown(f'<div class="live-price">🔴 LIVE: BTC ${live_btc_price:,.2f}</div>', unsafe_allow_html=True)
    
    col_left, col_right = st.columns(2)
    
    with col_left:
        st.markdown("""
        <div class="atticus-card">
            <h4>📊 Institutional BTC Portfolio Options</h4>
        </div>
        """, unsafe_allow_html=True)
        
        fund_type = st.radio("Institution Type:", ["Small Fund ($20-50M)", "Mid-Cap Fund ($50-200M)"], horizontal=True)
        
        if st.button("🎯 Generate Portfolio", type="primary", use_container_width=True):
            with st.spinner("Generating with live pricing..."):
                if "Small" in fund_type:
                    portfolio = {
                        'aum': 38000000,
                        'total_btc_size': 125.5,
                        'net_btc_exposure': 125.5,
                        'total_current_value': 125.5 * live_btc_price,
                        'total_pnl': 1400000,
                        'current_btc_price': live_btc_price
                    }
                else:
                    portfolio = {
                        'aum': 128000000,
                        'total_btc_size': 285.7,
                        'net_btc_exposure': 285.7,
                        'total_current_value': 285.7 * live_btc_price,
                        'total_pnl': 2800000,
                        'current_btc_price': live_btc_price
                    }
                
                st.session_state.portfolio = portfolio
                st.session_state.portfolio_source = 'generated'
                st.session_state.strategies = None
                st.session_state.strategies_generated = False
                st.success(f"✅ Portfolio Generated | BTC: ${live_btc_price:,.2f}")
                time.sleep(1)
                st.rerun()
        
        if st.session_state.portfolio and st.session_state.portfolio_source == 'generated':
            portfolio = st.session_state.portfolio
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("AUM", f"${portfolio['aum']:,.0f}")
                st.metric("BTC Exposure", f"{portfolio['total_btc_size']:.1f} BTC")
            with col2:
                st.metric("Position Value", f"${portfolio['total_current_value']:,.0f}")
                st.metric("P&L", f"${portfolio['total_pnl']:,.0f}")
            
            if st.button("📊 Analyze Portfolio", type="primary", use_container_width=True):
                st.session_state.demo_step = 2
                st.session_state.current_page = 'strategies'
                st.rerun()
    
    with col_right:
        st.markdown("""
        <div class="atticus-card">
            <h4>⚡ Custom BTC Position</h4>
        </div>
        """, unsafe_allow_html=True)
        
        with st.form("custom_position"):
            btc_amount = st.number_input("BTC Amount", min_value=0.1, value=25.0, step=0.1)
            position_type = st.radio("Position", ["Long", "Short"], horizontal=True)
            
            if st.form_submit_button("Analyze Position", type="primary"):
                custom_portfolio = {
                    'aum': btc_amount * live_btc_price * 3,
                    'total_btc_size': btc_amount,
                    'net_btc_exposure': btc_amount if position_type == 'Long' else -btc_amount,
                    'total_current_value': btc_amount * live_btc_price,
                    'total_pnl': btc_amount * live_btc_price * 0.12,
                    'current_btc_price': live_btc_price
                }
                st.session_state.portfolio = custom_portfolio
                st.session_state.portfolio_source = 'custom'
                st.session_state.strategies = None
                st.session_state.strategies_generated = False
                st.session_state.demo_step = 2
                st.session_state.current_page = 'strategies'
                st.rerun()

def screen_2_strategies():
    show_disclaimer_and_header()
    
    ensure_session_state()  # Extra safety
    
    if not st.session_state.portfolio:
        st.error("Please create a portfolio first")
        return
    
    portfolio = st.session_state.portfolio
    net_btc = portfolio.get('net_btc_exposure', 0)
    current_price = portfolio.get('current_btc_price', get_live_btc_price())
    
    st.info(f"📊 Portfolio: {abs(net_btc):.1f} BTC | 🔴 ${current_price:,.2f}")
    st.markdown(f"### Live Options Strategies - {abs(net_btc):.1f} BTC")
    
    if not st.session_state.strategies_generated:
        with st.spinner("Generating live strategies... (30-45 seconds)"):
            time.sleep(2)
            st.session_state.strategies = generate_professional_strategies(net_btc, current_price)
            st.session_state.strategies_generated = True
    
    if st.session_state.strategies and not st.session_state.selected_strategy:
        for i, strategy in enumerate(st.session_state.strategies):
            priority_emoji = "🔥" if strategy['priority'] == 'high' else "⭐"
            
            st.markdown(f"""
            <div class="strategy-card">
                <h4>{priority_emoji} {strategy['strategy_name'].replace('_', ' ').title()}</h4>
                <p><strong>Coverage:</strong> {strategy['target_exposure']:.1f} BTC</p>
                <p><strong>Purpose:</strong> {strategy['rationale']}</p>
            </div>
            """, unsafe_allow_html=True)
            
            pricing = strategy['pricing']['live_pricing']
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.info(f"**Cost**\n${abs(pricing['total_premium']):,.0f}")
            with col2:
                cost_pct = pricing['cost_as_pct']
                color = "🟢" if cost_pct < 3 else "🟡"
                st.info(f"**Rate**\n{color} {cost_pct:.1f}%")
            with col3:
                st.info(f"**Expiry**\n{pricing['days_to_expiry']} days")
            with col4:
                if st.button("Execute Strategy", key=f"exec_{i}", type="primary"):
                    st.session_state.selected_strategy = strategy
                    st.session_state.execution_data = {
                        'btc_price_at_execution': current_price,
                        'execution_time': random.randint(12, 28),
                        'timestamp': datetime.now().isoformat()
                    }
                    st.session_state.demo_step = 3
                    st.session_state.current_page = 'execution'
                    st.rerun()
            
            st.markdown("---")
    
    if st.button("← Back to Portfolio", type="secondary"):
        st.session_state.demo_step = 1
        st.session_state.current_page = 'portfolio'
        st.session_state.strategies = None
        st.session_state.selected_strategy = None
        st.session_state.strategies_generated = False
        st.rerun()

def screen_3_execution():
    show_disclaimer_and_header()
    
    ensure_session_state()  # Extra safety
    
    if not st.session_state.selected_strategy:
        st.error("Strategy not selected")
        return
    
    strategy = st.session_state.selected_strategy
    execution_data = st.session_state.execution_data
    pricing = strategy['pricing']['live_pricing']
    
    st.markdown("### Strategy Execution")
    
    with st.spinner("Executing with live pricing..."):
        time.sleep(2)
    
    st.success("✅ EXECUTION COMPLETE")
    st.metric("Execution Time", f"{execution_data['execution_time']} seconds")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"""
        <div class="options-detail-box">
            <h5>📋 Contract Details</h5>
            <p><strong>Contracts:</strong> {pricing['contracts_needed']} × {pricing['option_type']}</p>
            <p><strong>Strike:</strong> ${pricing.get('strike_price', pricing.get('long_strike', 0)):,.2f}</p>
            <p><strong>Expiry:</strong> {pricing['expiry_date']}</p>
            <p><strong>Premium:</strong> ${abs(pricing['total_premium']):,.2f}</p>
            <p><strong>IV:</strong> {pricing['implied_volatility']*100:.1f}%</p>
            <p><strong>Exchange:</strong> {pricing['exchange']}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        strike = pricing.get('strike_price', pricing.get('long_strike', pricing['btc_spot_price'] * 0.95))
        premium_per_btc = abs(pricing['total_premium']) / strategy['target_exposure']
        breakeven = strike - premium_per_btc if pricing['total_premium'] > 0 else strike + premium_per_btc
        
        st.markdown(f"""
        <div class="options-detail-box">
            <h5>🛡️ Protection Analysis</h5>
            <p><strong>Protected:</strong> {strategy['target_exposure']:.1f} BTC</p>
            <p><strong>Entry:</strong> ${pricing['btc_spot_price']:,.2f}</p>
            <p><strong>Protection:</strong> ${strike:,.2f}</p>
            <p><strong>Breakeven:</strong> ${breakeven:,.2f}</p>
            <p><strong>Max Loss:</strong> ${abs(pricing['total_premium']):,.2f}</p>
            <p><strong>Coverage:</strong> {pricing['cost_as_pct']:.2f}% of position</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="execution-success">
        <h3>✅ PROFESSIONAL EXECUTION COMPLETE</h3>
        <p>Institutional options strategy executed with live market pricing</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 New Analysis", type="primary", use_container_width=True):
            # Complete reset
            for key in ['portfolio', 'strategies', 'selected_strategy', 'execution_data', 'custom_positions']:
                if key in st.session_state:
                    st.session_state[key] = None
            st.session_state.demo_step = 1
            st.session_state.current_page = 'portfolio'
            st.session_state.strategies_generated = False
            st.rerun()
    
    with col2:
        st.link_button("💬 Contact Telegram", "https://t.me/willialso", use_container_width=True)

def main():
    """PRODUCTION: Main with guaranteed session state"""
    # Ensure session state exists before any access
    ensure_session_state()
    
    # Safe access to demo_step
    current_step = st.session_state.get('demo_step', 1)
    
    if current_step == 1:
        screen_1_portfolio()
    elif current_step == 2:
        screen_2_strategies()
    elif current_step == 3:
        screen_3_execution()
    else:
        # Fallback
        st.session_state.demo_step = 1
        screen_1_portfolio()

# For production deployment
if __name__ == "__main__":
    main()
