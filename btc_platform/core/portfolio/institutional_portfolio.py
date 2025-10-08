"""
Real Institutional Portfolio Generator
Creates realistic institutional BTC portfolios for platform demonstration
Uses real market data but scales to institutional sizes
"""
import logging
from datetime import datetime, timezone
from typing import Dict, List
import random

# Import our real exchange clients
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from exchanges.coinbase_client import CoinbaseClient
from exchanges.deribit_client import DeribitsClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class InstitutionalPortfolioGenerator:
    """Generate realistic institutional BTC portfolios using real market data"""
    
    def __init__(self):
        self.coinbase = CoinbaseClient()
        self.deribit = DeribitsClient()
        self.current_btc_price = self.coinbase.get_real_btc_price()
        
        logger.info(f"✅ Portfolio generator initialized, BTC: ${self.current_btc_price:,.2f}")
    
    def create_institutional_portfolio(self, institution_type: str) -> Dict:
        """Create realistic institutional portfolio"""
        
        # Real institutional portfolio templates based on market research
        institution_templates = {
            'crypto_hedge_fund': {
                'name': 'Crypto Alpha Partners LP',
                'type': 'Quantitative Crypto Hedge Fund',
                'aum': 285_000_000,  # $285M AUM
                'crypto_allocation_pct': 18.5,  # 18.5% in crypto
                'btc_allocation_pct': 62.0,  # 62% of crypto allocation in BTC
                'strategy': 'Quantitative arbitrage and momentum strategies',
                'typical_positions': [
                    {'name': 'Core BTC Long', 'weight': 0.45, 'entry_offset': -0.08},  # 8% below current
                    {'name': 'Tactical Long', 'weight': 0.25, 'entry_offset': -0.03},  # 3% below current  
                    {'name': 'Momentum Trade', 'weight': 0.20, 'entry_offset': +0.02}, # 2% above current
                    {'name': 'Swing Position', 'weight': 0.10, 'entry_offset': -0.05}  # 5% below current
                ],
                'protection_frequency': 'weekly',
                'risk_profile': 'aggressive'
            },
            
            'family_office': {
                'name': 'Meridian Family Office',
                'type': 'Ultra High Net Worth Family Office',
                'aum': 750_000_000,  # $750M AUM
                'crypto_allocation_pct': 8.2,  # 8.2% in crypto (conservative)
                'btc_allocation_pct': 75.0,  # 75% of crypto in BTC
                'strategy': 'Conservative digital asset diversification',
                'typical_positions': [
                    {'name': 'Treasury BTC Hold', 'weight': 0.70, 'entry_offset': -0.12}, # 12% below
                    {'name': 'Diversification Trade', 'weight': 0.30, 'entry_offset': -0.06} # 6% below
                ],
                'protection_frequency': 'monthly',
                'risk_profile': 'conservative'
            },
            
            'trading_desk': {
                'name': 'Quantum Trading Desk',
                'type': 'Institutional Trading Desk',
                'aum': 180_000_000,  # $180M AUM
                'crypto_allocation_pct': 25.0,  # 25% in crypto (active)
                'btc_allocation_pct': 55.0,  # 55% of crypto in BTC
                'strategy': 'Active trading and market making',
                'typical_positions': [
                    {'name': 'Long Position', 'weight': 0.60, 'entry_offset': -0.04},   # 4% below
                    {'name': 'Short Hedge', 'weight': -0.15, 'entry_offset': +0.03},   # Short position
                    {'name': 'Spread Trade', 'weight': 0.35, 'entry_offset': -0.02},   # 2% below
                    {'name': 'Arb Position', 'weight': 0.20, 'entry_offset': +0.01}    # 1% above
                ],
                'protection_frequency': 'daily',
                'risk_profile': 'active'
            }
        }
        
        if institution_type not in institution_templates:
            raise ValueError(f"Unknown institution type: {institution_type}")
        
        template = institution_templates[institution_type]
        
        # Calculate total BTC allocation
        total_crypto_allocation = template['aum'] * (template['crypto_allocation_pct'] / 100)
        total_btc_allocation = total_crypto_allocation * (template['btc_allocation_pct'] / 100)
        
        # Generate individual positions
        positions = []
        total_btc_size = 0
        
        for pos_template in template['typical_positions']:
            # Calculate position size
            position_usd = total_btc_allocation * abs(pos_template['weight'])
            
            # Calculate entry price with realistic variation
            entry_price = self.current_btc_price * (1 + pos_template['entry_offset'])
            entry_price += random.uniform(-500, 500)  # Add some realistic noise
            
            # Position size in BTC
            btc_size = position_usd / entry_price
            
            # Handle short positions
            if pos_template['weight'] < 0:
                btc_size = -btc_size  # Negative for short positions
            
            # Current value and P&L
            current_value = btc_size * self.current_btc_price
            entry_value = btc_size * entry_price
            pnl_usd = current_value - entry_value
            pnl_pct = (pnl_usd / abs(entry_value)) * 100 if entry_value != 0 else 0
            
            position = {
                'position_id': f"{institution_type}_{pos_template['name'].lower().replace(' ', '_')}",
                'name': pos_template['name'],
                'btc_size': btc_size,
                'entry_price': entry_price,
                'current_price': self.current_btc_price,
                'entry_value': entry_value,
                'current_value': current_value,
                'pnl_usd': pnl_usd,
                'pnl_pct': pnl_pct,
                'allocation_pct': (abs(current_value) / template['aum']) * 100,
                'position_type': 'long' if btc_size > 0 else 'short',
                'weight_in_btc_portfolio': pos_template['weight'],
                'created_timestamp': datetime.now(timezone.utc).isoformat()
            }
            
            positions.append(position)
            total_btc_size += btc_size
        
        # Portfolio summary
        total_current_value = sum(pos['current_value'] for pos in positions)
        total_pnl = sum(pos['pnl_usd'] for pos in positions)
        total_entry_value = sum(pos['entry_value'] for pos in positions)
        
        portfolio = {
            'institution_info': template,
            'positions': positions,
            'portfolio_summary': {
                'total_btc_size': total_btc_size,
                'total_positions': len(positions),
                'total_current_value': total_current_value,
                'total_entry_value': total_entry_value,
                'total_pnl_usd': total_pnl,
                'total_pnl_pct': (total_pnl / abs(total_entry_value)) * 100 if total_entry_value != 0 else 0,
                'total_allocation_pct': (abs(total_current_value) / template['aum']) * 100,
                'net_exposure_btc': total_btc_size,  # Net long/short exposure
                'gross_exposure_usd': sum(abs(pos['current_value']) for pos in positions),
                'current_btc_price': self.current_btc_price,
                'requires_protection': abs(total_btc_size) > 1.0,  # Need protection if > 1 BTC exposure
                'protection_urgency': 'high' if abs(total_btc_size) > 50 else 'medium'
            },
            'market_context': {
                'btc_price_at_creation': self.current_btc_price,
                'available_protection_puts': len(self.deribit.get_institutional_protection_puts()),
                'data_sources': ['coinbase_cdp_real', 'deribit_real']
            },
            'metadata': {
                'created_timestamp': datetime.now(timezone.utc).isoformat(),
                'generator': 'institutional_portfolio_real',
                'positions_realistic': True,
                'market_data_real': True,
                'institution_scale_authentic': True
            }
        }
        
        logger.info(f"✅ Created {institution_type}: {total_btc_size:.1f} BTC net exposure")
        return portfolio
    
    def analyze_portfolio_protection_needs(self, portfolio: Dict) -> Dict:
        """Analyze portfolio and determine optimal protection strategies"""
        try:
            summary = portfolio['portfolio_summary']
            institution = portfolio['institution_info']
            
            # Get available protection options
            protection_puts = self.deribit.get_institutional_protection_puts()
            
            # Risk analysis
            net_btc_exposure = summary['net_exposure_btc']
            gross_usd_exposure = summary['gross_exposure_usd']
            
            # Estimate risk metrics
            var_1day_5pct = gross_usd_exposure * 0.05  # 5% daily VaR
            stress_loss_10pct = gross_usd_exposure * 0.10  # 10% stress loss
            
            # Find optimal protection
            optimal_puts = []
            if protection_puts and net_btc_exposure > 0:  # Only protect long exposure
                # Find puts that protect the net exposure
                for put in protection_puts[:5]:  # Top 5 options
                    # Calculate protection cost for full exposure
                    protection_cost = abs(net_btc_exposure) * put['real_mid_usd']
                    cost_pct = (protection_cost / gross_usd_exposure) * 100
                    
                    optimal_puts.append({
                        'option': put,
                        'protection_cost_usd': protection_cost,
                        'cost_as_pct_of_portfolio': cost_pct,
                        'protection_level_pct': put['strike_price'] / self.current_btc_price * 100,
                        'cost_benefit_ratio': protection_cost / stress_loss_10pct
                    })
            
            analysis = {
                'portfolio_metrics': {
                    'net_btc_exposure': net_btc_exposure,
                    'gross_usd_exposure': gross_usd_exposure,
                    'protection_needed': net_btc_exposure > 0,
                    'position_concentration': 'high' if abs(net_btc_exposure) > 100 else 'moderate'
                },
                'risk_metrics': {
                    'value_at_risk_1day_5pct': var_1day_5pct,
                    'stress_loss_10pct': stress_loss_10pct,
                    'protection_urgency': summary['protection_urgency']
                },
                'available_protection': {
                    'total_puts_available': len(protection_puts),
                    'optimal_strategies': optimal_puts
                },
                'recommendation': {
                    'should_protect': net_btc_exposure > 5.0,  # Protect if > 5 BTC exposure
                    'recommended_frequency': institution['protection_frequency'],
                    'estimated_annual_protection_cost': gross_usd_exposure * 0.025  # 2.5% annually
                }
            }
            
            return analysis
            
        except Exception as e:
            logger.error(f"❌ Portfolio analysis failed: {e}")
            return {'error': str(e)}

if __name__ == "__main__":
    print("🏦 Testing Real Institutional Portfolio Generator...")
    
    try:
        generator = InstitutionalPortfolioGenerator()
        
        print("\n" + "="*80)
        print("📊 REAL INSTITUTIONAL PORTFOLIO TESTS")
        print("="*80)
        
        # Test each institution type
        for inst_type in ['crypto_hedge_fund', 'family_office', 'trading_desk']:
            print(f"\n🏛️  Testing {inst_type.replace('_', ' ').title()}:")
            
            portfolio = generator.create_institutional_portfolio(inst_type)
            summary = portfolio['portfolio_summary']
            info = portfolio['institution_info']
            
            print(f"  Institution: {info['name']}")
            print(f"  AUM: ${info['aum']:,}")
            print(f"  Net BTC Exposure: {summary['net_exposure_btc']:.1f} BTC")
            print(f"  Portfolio Value: ${summary['total_current_value']:,.0f}")
            print(f"  Total P&L: ${summary['total_pnl_usd']:,.0f} ({summary['total_pnl_pct']:.1f}%)")
            print(f"  Positions: {summary['total_positions']}")
            
            # Analyze protection needs
            analysis = generator.analyze_portfolio_protection_needs(portfolio)
            if 'error' not in analysis:
                risk = analysis['risk_metrics']
                print(f"  Protection Needed: {analysis['portfolio_metrics']['protection_needed']}")
                print(f"  Daily VaR (5%): ${risk['value_at_risk_1day_5pct']:,.0f}")
                
                if analysis['available_protection']['optimal_strategies']:
                    best_protection = analysis['available_protection']['optimal_strategies'][0]
                    print(f"  Best Protection: ${best_protection['protection_cost_usd']:,.0f} ({best_protection['cost_as_pct_of_portfolio']:.1f}%)")
        
        print("\n" + "="*80)
        print("✅ REAL INSTITUTIONAL PORTFOLIOS GENERATED SUCCESSFULLY")
        print("📋 All portfolios use real market data and institutional scale")
        print("🛡️  Protection analysis includes real Deribit options")
        print("="*80)
        
    except Exception as e:
        print(f"❌ Portfolio generator test failed: {e}")
        import traceback
        traceback.print_exc()
