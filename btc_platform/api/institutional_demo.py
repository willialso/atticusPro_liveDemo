"""
Clean Institutional Demo Interface
Simple 4-button institutional experience
"""
import logging
from datetime import datetime, timezone
from typing import Dict, List

from ..core.portfolio.position_simulator import InstitutionalPositionSimulator
from ..core.timeframes.weekly_engine import WeeklyOptionsEngine
from .config.settings import PLATFORM_CONFIG

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class InstitutionalDemo:
    """Clean institutional demo interface"""
    
    def __init__(self):
        self.position_simulator = InstitutionalPositionSimulator()
        self.weekly_engine = WeeklyOptionsEngine()
        self.current_portfolio = None
    
    def create_institutional_portfolio(self, institution_type: str = 'mid_cap_fund') -> Dict:
        """Create realistic institutional portfolio"""
        logger.info(f"🏦 Creating {institution_type} portfolio...")
        
        portfolio = self.position_simulator.create_institutional_portfolio(institution_type)
        risk_analysis = self.position_simulator.get_portfolio_risk_analysis(portfolio)
        
        self.current_portfolio = {
            'portfolio': portfolio,
            'risk_analysis': risk_analysis,
            'created_timestamp': datetime.now(timezone.utc).isoformat()
        }
        
        return self.current_portfolio
    
    def show_strategy_menu(self) -> Dict:
        """Show 4-button strategy menu"""
        if not self.current_portfolio:
            return {'error': 'No portfolio created. Please create portfolio first.'}
        
        portfolio_summary = self.current_portfolio['portfolio']['portfolio_summary']
        total_btc = portfolio_summary['total_btc_size']
        
        strategies = {
            'protection': {
                'title': '🛡️  PROTECTION',
                'description': 'Downside protection for positions',
                'weekly_cost_range': '1.2-2.8% of exposure',
                'use_case': 'Protect against market downturns',
                'available': True
            },
            'income': {
                'title': '📈 INCOME GENERATION',
                'description': 'Generate income from holdings',
                'weekly_income_range': '0.8-2.1% of exposure', 
                'use_case': 'Covered calls and premium collection',
                'available': True
            },
            'rebalancing': {
                'title': '⚖️  REBALANCING',
                'description': 'Portfolio optimization strategies',
                'cost_range': '0.5-1.5% execution cost',
                'use_case': 'Efficient portfolio adjustments',
                'available': False,  # Phase 2 feature
                'note': 'Available in Phase 2'
            },
            'volatility': {
                'title': '🎯 VOLATILITY CAPTURE',
                'description': 'Advanced volatility strategies',
                'target_return': '15-25% annual returns',
                'use_case': 'Professional volatility trading',
                'available': False,  # Phase 2 feature
                'note': 'Available in Phase 2'
            }
        }
        
        return {
            'portfolio_summary': portfolio_summary,
            'available_strategies': strategies,
            'recommended': 'protection',  # Default recommendation
            'menu_generated': datetime.now(timezone.utc).isoformat()
        }
    
    def execute_protection_strategy(self) -> Dict:
        """Execute weekly protection strategy"""
        if not self.current_portfolio:
            return {'error': 'No portfolio available'}
        
        logger.info("🛡️  Executing protection strategy...")
        
        total_btc = self.current_portfolio['portfolio']['portfolio_summary']['total_btc_size']
        
        # Get weekly protection options
        weekly_strategies = self.weekly_engine.get_weekly_strategy_menu(total_btc)
        
        if not weekly_strategies:
            return {'error': 'No weekly protection strategies available'}
        
        # Select optimal strategy (usually 5-day Friday expiry)
        optimal_strategy = min(weekly_strategies, key=lambda x: x['premium_pct'])
        
        # Get detailed strategy calculation
        detailed_strategy = self.weekly_engine.calculate_weekly_protection_cost(
            total_btc, 
            optimal_strategy['days_to_expiry']
        )
        
        if not detailed_strategy['success']:
            return {'error': detailed_strategy['reason']}
        
        # Execute paper trade
        execution_result = self._execute_paper_protection(detailed_strategy)
        
        return {
            'strategy_selected': optimal_strategy,
            'detailed_strategy': detailed_strategy,
            'execution_result': execution_result,
            'institutional_benefits': self._calculate_institutional_benefits(detailed_strategy),
            'execution_timestamp': datetime.now(timezone.utc).isoformat()
        }
    
    def _execute_paper_protection(self, strategy: Dict) -> Dict:
        """Execute paper protection trade"""
        logger.info("📋 Executing paper protection trade...")
        
        option_details = strategy['option_details']
        if not option_details:
            return {'success': False, 'reason': 'No suitable option found'}
        
        # Simulate option purchase
        option_trade = {
            'action': 'buy_put_option',
            'symbol': option_details['symbol'],
            'strike': option_details['strike_price'],
            'size_btc': strategy['position_details']['btc_size'],
            'premium_paid': strategy['cost_breakdown']['option_premium'],
            'execution_price': option_details['real_mid'],
            'trade_id': f"paper_protection_{int(datetime.now().timestamp())}",
            'status': 'paper_executed'
        }
        
        # Simulate platform hedge
        hedge_trade = {
            'action': 'hedge_platform_exposure',
            'method': 'coinbase_futures_short',
            'size_btc': strategy['position_details']['btc_size'],
            'hedge_cost': strategy['cost_breakdown']['hedge_cost'],
            'trade_id': f"paper_hedge_{int(datetime.now().timestamp())}",
            'status': 'paper_executed'
        }
        
        return {
            'success': True,
            'option_trade': option_trade,
            'hedge_trade': hedge_trade,
            'total_premium_paid': strategy['cost_breakdown']['client_premium'],
            'platform_profit': strategy['cost_breakdown']['platform_profit'],
            'protection_active_until': self._calculate_expiry_time(strategy['timing']['actual_days']),
            'note': 'Paper trades executed with real market pricing'
        }
    
    def _calculate_institutional_benefits(self, strategy: Dict) -> Dict:
        """Calculate benefits vs traditional approaches"""
        
        position_value = strategy['position_details']['position_value']
        premium = strategy['cost_breakdown']['client_premium']
        
        # Compare to traditional options desk
        traditional_cost = {
            'options_trader_salary': 25000,  # Monthly allocation
            'trading_system_cost': 5000,     # Monthly allocation
            'execution_slippage': position_value * 0.002,  # 0.2% slippage
            'time_cost': 15000  # 40 hours @ $375/hour (loaded cost)
        }
        
        total_traditional_cost = sum(traditional_cost.values())
        
        savings = total_traditional_cost - premium
        time_savings = '2-3 days vs 45 seconds'
        
        return {
            'platform_cost': premium,
            'traditional_cost': total_traditional_cost,
            'cost_savings': savings,
            'savings_percentage': (savings / total_traditional_cost) * 100,
            'time_savings': time_savings,
            'additional_benefits': [
                'Professional execution at mid-price',
                'Automatic hedge management',
                'No internal infrastructure needed',
                'Transparent all-in pricing',
                'Instant execution capability'
            ]
        }
    
    def _calculate_expiry_time(self, days: int) -> str:
        """Calculate protection expiry time"""
        expiry = datetime.now(timezone.utc) + datetime.timedelta(days=days)
        return expiry.isoformat()

if __name__ == "__main__":
    print("🏦 Testing Clean Institutional Demo...")
    
    try:
        demo = InstitutionalDemo()
        
        # Step 1: Create portfolio
        print("\n" + "="*80)
        print("STEP 1: CREATE INSTITUTIONAL PORTFOLIO")
        print("="*80)
        
        portfolio_result = demo.create_institutional_portfolio('crypto_hedge_fund')
        portfolio_summary = portfolio_result['portfolio']['portfolio_summary']
        
        print(f"✅ Created crypto hedge fund portfolio:")
        print(f"   Total BTC: {portfolio_summary['total_btc_size']:.2f} BTC")
        print(f"   Total Value: ${portfolio_summary['total_current_value']:,.0f}")
        print(f"   Total P&L: ${portfolio_summary['total_pnl_usd']:,.0f}")
        
        # Step 2: Show strategy menu
        print("\n" + "="*80)
        print("STEP 2: STRATEGY MENU")
        print("="*80)
        
        menu = demo.show_strategy_menu()
        for strategy_name, strategy in menu['available_strategies'].items():
            status = "✅" if strategy['available'] else "🚧"
            print(f"{status} {strategy['title']}")
            print(f"    {strategy['description']}")
            if not strategy['available']:
                print(f"    Note: {strategy.get('note', 'Coming soon')}")
            print()
        
        # Step 3: Execute protection
        print("\n" + "="*80)
        print("STEP 3: EXECUTE PROTECTION STRATEGY")
        print("="*80)
        
        protection_result = demo.execute_protection_strategy()
        
        if 'error' not in protection_result:
            strategy = protection_result['detailed_strategy']
            benefits = protection_result['institutional_benefits']
            
            print(f"✅ Protection strategy executed:")
            print(f"   Premium: ${strategy['cost_breakdown']['client_premium']:,.0f}")
            print(f"   Platform Profit: ${strategy['cost_breakdown']['platform_profit']:,.0f}")
            print(f"   Cost as % of Position: {strategy['cost_breakdown']['cost_as_pct_of_position']:.2f}%")
            print(f"   Protection until: {protection_result['execution_result']['protection_active_until']}")
            
            print(f"\n💡 Institutional Benefits:")
            print(f"   Cost Savings: ${benefits['cost_savings']:,.0f} ({benefits['savings_percentage']:.1f}%)")
            print(f"   Time Savings: {benefits['time_savings']}")
            
        else:
            print(f"❌ Protection execution failed: {protection_result['error']}")
        
        print("\n" + "="*80)
        print("✅ CLEAN INSTITUTIONAL DEMO COMPLETE")
        print("="*80)
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()
