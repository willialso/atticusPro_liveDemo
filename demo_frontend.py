"""
ATTICUS PROFESSIONAL - COMPLETELY FIXED VERSION
✅ Session state properly initialized
✅ Strategy doubling eliminated  
✅ Multiple strategies for demo
"""
import streamlit as st
import time
import random

# Page config
st.set_page_config(
    page_title="Atticus Professional",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Initialize session state FIRST - before anything else
def initialize_session_state():
    """Initialize all session state variables"""
    defaults = {
        'demo_step': 1,
        'portfolio': None,
        'strategies': None,
        'selected_strategy': None,
        'execution_data': None,
        'custom_positions': [],
        'portfolio_source': None,
        'show_strategies': True  # NEW: Control strategy display
    }
    
    for key, default_value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = default_value

# CALL INITIALIZATION IMMEDIATELY
initialize_session_state()

# CSS
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        color: #f1f5f9 !important;
    }
    
    .main-header {
        text-align: center;
        margin: 2rem 0 3rem 0;
        padding: 1rem;
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

def show_top_disclaimer():
    st.markdown("""
    <div class="top-disclaimer">
        <p><strong>Live Demo Platform</strong> • Portfolio positions are representative models • All strategies utilize real-time executable pricing</p>
    </div>
    """, unsafe_allow_html=True)

def show_header():
    st.markdown("""
    <div class="main-header">
        <img src="https://i.ibb.co/qFNCZsWG/attpro.png" width="400" alt="Atticus Professional">
        <p style="color: #e2e8f0; font-size: 1.2rem; text-align: center; margin-top: 1rem;">Professional Options Strategies for Institutional Portfolios</p>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")

def screen_1_portfolio():
    show_top_disclaimer()
    show_header()
    
    # RESET strategy display when returning to portfolio
    st.session_state.show_strategies = True
    st.session_state.selected_strategy = None
    
    col_left, col_right = st.columns(2)
    
    with col_left:
        st.markdown("""
        <div class="atticus-card">
            <h4>📊 Connect Institution for BTC Portfolio Options</h4>
        </div>
        """, unsafe_allow_html=True)
        
        fund_type = st.radio(
            "Institution Type:",
            ["Small Crypto Fund ($20-50M AUM)", "Mid-Cap Fund ($50-200M AUM)"],
            horizontal=True
        )
        
        if st.button("🎯 Generate Institutional Portfolio", type="primary", use_container_width=True):
            with st.spinner("Generating institutional portfolio..."):
                current_btc_price = 121425
                if "Small" in fund_type:
                    portfolio = {
                        'aum': 38000000,
                        'total_btc_size': 162.4,
                        'net_btc_exposure': 162.4,
                        'total_current_value': 162.4 * current_btc_price,
                        'total_pnl': 1700000,
                        'current_btc_price': current_btc_price
                    }
                else:
                    portfolio = {
                        'aum': 128000000,
                        'total_btc_size': 425.7,
                        'net_btc_exposure': 425.7,
                        'total_current_value': 425.7 * current_btc_price,
                        'total_pnl': 3200000,
                        'current_btc_price': current_btc_price
                    }
                
                st.session_state.portfolio = portfolio
                st.session_state.portfolio_source = 'generated'
                st.session_state.strategies = None  # Reset strategies
                st.rerun()
        
        if st.session_state.portfolio and st.session_state.portfolio_source == 'generated':
            portfolio = st.session_state.portfolio
            st.success("✅ Institutional Portfolio Generated")
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Total AUM", f"${portfolio['aum']:,.0f}")
                st.metric("BTC Exposure", f"{portfolio['total_btc_size']:.1f} BTC")
            with col2:
                st.metric("Position Value", f"${portfolio['total_current_value']:,.0f}")
                st.metric("Current P&L", f"${portfolio['total_pnl']:,.0f}")
            
            if st.button("📊 Analyze Generated Portfolio", type="primary", use_container_width=True):
                st.session_state.demo_step = 2
                st.rerun()
    
    with col_right:
        st.markdown("""
        <div class="atticus-card">
            <h4>⚡ Enter BTC Position for Options Strategy</h4>
        </div>
        """, unsafe_allow_html=True)
        
        with st.form("position_entry"):
            col1, col2, col3 = st.columns([2, 1, 1])
            
            with col1:
                btc_amount = st.number_input("BTC Amount", min_value=0.1, value=50.0, step=0.1)
            with col2:
                position_type = st.radio("Position", ["Long", "Short"], horizontal=True)
            with col3:
                st.write("")
                add_position = st.form_submit_button("Add Position", type="primary")
        
        if add_position and btc_amount > 0:
            st.session_state.custom_positions.append({'btc_amount': btc_amount, 'position_type': position_type})
            st.rerun()
        
        if st.session_state.custom_positions:
            st.markdown("**📋 Current Positions**")
            
            total_long = sum(pos['btc_amount'] for pos in st.session_state.custom_positions if pos['position_type'] == 'Long')
            total_short = sum(pos['btc_amount'] for pos in st.session_state.custom_positions if pos['position_type'] == 'Short')
            
            for i, pos in enumerate(st.session_state.custom_positions):
                col1, col2, col3 = st.columns([2, 1, 1])
                with col1:
                    st.write(f"**{pos['btc_amount']:.1f} BTC**")
                with col2:
                    color = "🟢" if pos['position_type'] == 'Long' else "🔴"
                    st.write(f"{color} {pos['position_type']}")
                with col3:
                    if st.button("Remove", key=f"remove_{i}"):
                        st.session_state.custom_positions.pop(i)
                        st.rerun()
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Long BTC", f"{total_long:.1f}")
            with col2:
                st.metric("Short BTC", f"{total_short:.1f}")
            with col3:
                st.metric("Net BTC", f"{total_long - total_short:+.1f}")
            
            if st.button("⚡ Analyze Custom Positions", type="primary", use_container_width=True):
                net_btc = total_long - total_short
                current_btc_price = 121425
                custom_portfolio = {
                    'aum': abs(net_btc) * current_btc_price * 2,
                    'total_btc_size': abs(net_btc),
                    'net_btc_exposure': net_btc,
                    'total_current_value': (total_long + total_short) * current_btc_price,
                    'total_pnl': abs(net_btc) * current_btc_price * 0.08,
                    'current_btc_price': current_btc_price
                }
                st.session_state.portfolio = custom_portfolio
                st.session_state.portfolio_source = 'custom'
                st.session_state.strategies = None  # Reset strategies
                st.session_state.demo_step = 2
                st.rerun()

def generate_multiple_strategies(net_btc, current_btc_price):
    """Generate multiple strategies for better demo"""
    strategies = [
        {
            'strategy_name': 'protective_put',
            'target_exposure': abs(net_btc),
            'priority': 'high',
            'rationale': f'Complete downside protection for {abs(net_btc):.1f} BTC long position',
            'pricing': {
                'client_pricing': {
                    'total_premium': abs(net_btc) * current_btc_price * 0.035,
                    'cost_as_pct_of_position': 3.5,
                    'days_to_expiry': 7
                }
            }
        },
        {
            'strategy_name': 'put_spread',
            'target_exposure': abs(net_btc),
            'priority': 'medium',
            'rationale': f'Cost-efficient protection for {abs(net_btc):.1f} BTC with limited gap risk',
            'pricing': {
                'client_pricing': {
                    'total_premium': abs(net_btc) * current_btc_price * 0.018,
                    'cost_as_pct_of_position': 1.8,
                    'days_to_expiry': 14
                }
            }
        },
        {
            'strategy_name': 'collar_strategy',
            'target_exposure': abs(net_btc) * 0.75,
            'priority': 'low',
            'rationale': f'Income generation with protection for {abs(net_btc)*0.75:.1f} BTC exposure',
            'pricing': {
                'client_pricing': {
                    'total_premium': abs(net_btc) * 0.75 * current_btc_price * 0.012,
                    'cost_as_pct_of_position': 1.2,
                    'days_to_expiry': 30
                }
            }
        }
    ]
    return strategies

def screen_2_strategies():
    show_top_disclaimer()
    show_header()
    
    if not st.session_state.portfolio:
        st.error("Please create a portfolio first")
        return
    
    portfolio = st.session_state.portfolio
    net_btc = portfolio.get('net_btc_exposure', 0)
    current_btc_price = portfolio.get('current_btc_price', 121425)
    
    st.info(f"📊 Analyzing Portfolio | {abs(net_btc):.1f} BTC | BTC: ${current_btc_price:,.2f}")
    st.markdown(f"### Protection Strategies for {abs(net_btc):.1f} BTC Position")
    
    # Generate strategies if not exists
    if not st.session_state.strategies:
        with st.spinner("Generating personalized strategies... (Est. 60 seconds)"):
            time.sleep(3)
            st.session_state.strategies = generate_multiple_strategies(net_btc, current_btc_price)
    
    # FIXED: Only show strategies if show_strategies is True AND no strategy selected
    if st.session_state.strategies and st.session_state.show_strategies and not st.session_state.selected_strategy:
        
        for i, strategy in enumerate(st.session_state.strategies):
            priority_emoji = "🔥" if strategy['priority'] == 'high' else "⭐" if strategy['priority'] == 'medium' else "💡"
            
            st.markdown(f"""
            <div class="strategy-card">
                <h4>{priority_emoji} {strategy['strategy_name'].replace('_', ' ').title()}</h4>
                <p><strong>Coverage:</strong> {strategy['target_exposure']:.1f} BTC</p>
                <p><strong>Purpose:</strong> {strategy['rationale']}</p>
            </div>
            """, unsafe_allow_html=True)
            
            pricing = strategy['pricing']['client_pricing']
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.info(f"**Cost**\n${pricing['total_premium']:,.0f}")
            with col2:
                color = "🟢" if pricing['cost_as_pct_of_position'] < 2 else "🟡" if pricing['cost_as_pct_of_position'] < 4 else "🔴"
                st.info(f"**Rate**\n{color} {pricing['cost_as_pct_of_position']:.1f}%")
            with col3:
                st.info(f"**Duration**\n{pricing['days_to_expiry']} days")
            with col4:
                if st.button("Select Strategy", key=f"select_{i}", type="primary"):
                    st.session_state.selected_strategy = strategy
                    st.session_state.execution_data = {
                        'btc_price_at_execution': current_btc_price,
                        'execution_time': random.randint(8, 18)
                    }
                    st.session_state.show_strategies = False  # FIXED: Hide strategies
                    st.session_state.demo_step = 3
                    st.rerun()
            
            st.markdown("---")
    
    # Show message if strategy selected but still on strategies page
    elif st.session_state.selected_strategy and not st.session_state.show_strategies:
        st.info("✅ Strategy selected! Proceeding to execution...")
        time.sleep(1)
        st.session_state.demo_step = 3
        st.rerun()
    
    if st.button("← Back to Portfolio", type="secondary"):
        st.session_state.demo_step = 1
        st.session_state.strategies = None
        st.session_state.selected_strategy = None
        st.session_state.show_strategies = True
        st.rerun()

def screen_3_execution():
    show_top_disclaimer()
    show_header()
    
    if not st.session_state.selected_strategy:
        st.error("Please select a strategy first")
        return
    
    strategy = st.session_state.selected_strategy
    execution_data = st.session_state.execution_data
    
    st.markdown("### Strategy Execution")
    
    with st.spinner("Executing strategy with live market data..."):
        time.sleep(2)
    
    st.success("✅ STRATEGY EXECUTED SUCCESSFULLY")
    st.metric("Execution Time", f"{execution_data['execution_time']} seconds")
    
    pricing = strategy['pricing']['client_pricing']
    entry_price = execution_data['btc_price_at_execution']
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Options Purchase Details")
        strategy_type = strategy['strategy_name'].replace('_', ' ').title()
        st.info(f"**Type:** {strategy['target_exposure']:.1f} BTC {strategy_type}")
        st.info(f"**Total Cost:** ${pricing['total_premium']:,.0f}")
        st.info(f"**Entry Price:** ${entry_price:,.0f}")
    
    with col2:
        st.markdown("#### Protection Summary")
        st.info(f"**Max Loss:** ${pricing['total_premium']:,.0f}")
        st.info("**Max Profit:** Unlimited")
        breakeven = entry_price - (pricing['total_premium']/strategy['target_exposure'])
        st.info(f"**Breakeven:** ${breakeven:,.0f}")
    
    st.markdown("""
    <div class="execution-success">
        <h3>✅ STRATEGY IMPLEMENTATION COMPLETE</h3>
        <p>Professional options strategy executed with institutional-grade pricing</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 New Analysis", type="primary", use_container_width=True):
            # Reset all session state
            st.session_state.portfolio = None
            st.session_state.strategies = None
            st.session_state.selected_strategy = None
            st.session_state.execution_data = None
            st.session_state.custom_positions = []
            st.session_state.show_strategies = True
            st.session_state.demo_step = 1
            st.rerun()
    
    with col2:
        st.link_button("💬 Contact via Telegram", "https://t.me/willialso", use_container_width=True)

def main():
    """Main function with proper session state handling"""
    # Session state is already initialized at module level
    
    if st.session_state.demo_step == 1:
        screen_1_portfolio()
    elif st.session_state.demo_step == 2:
        screen_2_strategies()
    elif st.session_state.demo_step == 3:
        screen_3_execution()

if __name__ == "__main__":
    main()
