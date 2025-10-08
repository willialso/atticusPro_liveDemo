"""
Institutional Portfolio Simulator
Creates realistic institutional BTC positions for demonstration
"""
import logging
from datetime import datetime, timezone
from typing import Dict, List
import random

from ..core.exchanges.coinbase_client import CoinbaseClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class InstitutionalPositionSimulator:
    """Generate realistic institutional portfolios for demo"""
    
    def __init__(self):
        self.coinbase = CoinbaseClient()
        self.current_btc_price = self.coinbase.get_current_btc_price()
    
    def create_institutional_portfolio(self, institution_type: str = 'mid_cap_fund') -> Dict:
        """Create realistic institutional portfolio"""
        
        portfolio_templates = {
            'crypto_hedge_fund': {
                'aum': 180_000_000,
                'crypto_allocation': 0.15,
                'btc_allocation': 0.60,
                'position_types': ['core_long', 'tactical_long', 'momentum_trade']
            },
            'family_office': {
                'aum': 650_000_000,
                'crypto_allocation': 0.08,
                'btc_allocation': 0.75,
                'position_types': ['treasury_holding', 'diversification_trade']
            },
            'trading_desk': {
                'aum': 120_000_000,
                'crypto_allocation': 0.20,
                'btc_allocation': 0.50,
                'position_types': ['long_position', 'short_position', 'spread_trade']
            },
            'mid_cap_fund': {
                'aum': 85_000_000,
                'crypto_allocation': 0.12,
                'btc_allocation': 0.55,
                'position_types': ['core_holding', 'tactical_position']
            }
        }
        
        template = portfolio_templates[institution_type]
        total_crypto_allocation = template['aum'] * template['crypto_allocation']
        total_btc_allocation = total_crypto_allocation * template['btc_allocation']
        
        # Generate positions
        positions = []
        remaining_allocation = total_btc_allocation
        
        for i, position_type in enumerate(template['position_types']):
            if i == len(template['position_types']) - 1:
                # Last position gets remaining allocation
                position_value = remaining_allocation
            else:
                # Random allocation between 20-60% of remaining
                allocation_pct = random.uniform(0.3, 0.6)
                position_value = remaining_allocation * allocation_pct
                remaining_allocation -= position_value
            
            btc_size = position_value / self.current_btc_price
            
            # Add some realistic P&L variation
            pnl_pct = random.uniform(-0.08, 0.12)  # -8% to +12%
            current_value = position_value * (1 + pnl_pct)
            pnl_usd = current_value - position_value
            
            position = {
                'position_id': f'{institution_type}_{position_type}_{i+1}',
                'position_type': position_type,
                'asset': 'BTC',
                'size_btc': btc_size,
                'entry_value_usd': position_value,
                'current_value_usd': current_value,
                'current_btc_price': self.current_btc_price,
                'pnl_usd': pnl_usd,
                'pnl_pct': pnl_pct * 100,
                'allocation_pct': (current_value / template['aum']) * 100,
                'created_timestamp': datetime.now(timezone.utc).isoformat(),
                'is_synthetic': True,
                'synthetic_note': 'Realistic institutional position for demonstration'
            }
            
            positions.append(position)
        
        portfolio = {
            'institution_type': institution_type,
            'institution_profile': template,
            'positions': positions,
            'portfolio_summary': {
                'total_positions': len(positions),
                'total_btc_size': sum(pos['size_btc'] for pos in positions),
                'total_current_value': sum(pos['current_value_usd'] for pos in positions),
                'total_pnl_usd': sum(pos['pnl_usd'] for pos in positions),
                'total_allocation_pct': (sum(pos['current_value_usd'] for pos in positions) / template['aum']) * 100,
                'largest_position_btc': max(pos['size_btc'] for pos in positions),
                'requires_protection': True,
                'protection_priority': 'high' if sum(pos['size_btc'] for pos in positions) > 20 else 'medium'
            },
            'metadata': {
                'created_timestamp': datetime.now(timezone.utc).isoformat(),
                'btc_price_at_creation': self.current_btc_price,
                'data_source': 'institutional_simulator',
                'all_positions_synthetic': True
            }
        }
        
        logger.info(f"✅ Created {institution_type} portfolio: {portfolio['portfolio_summary']['total_btc_size']:.2f} BTC")
        return portfolio
    
    def get_portfolio_risk_analysis(self, portfolio: Dict) -> Dict:
        """Analyze portfolio risk characteristics"""
        
        total_btc = portfolio['portfolio_summary']['total_btc_size']
        total_value = portfolio['portfolio_summary']['total_current_value']
        
        # Risk metrics
        var_5pct = total_value * 0.05  # 5% Value at Risk (1 day, 95% confidence)
        stress_test_loss = total_value * 0.15  # 15% stress scenario
        
        # Protection recommendations
        protection_cost_weekly = total_value * 0.015  # 1.5% for weekly protection
        protection_benefit = stress_test_loss - protection_cost_weekly
        
        risk_analysis = {
            'portfolio_metrics': {
                'total_exposure_btc': total_btc,
                'total_exposure_usd': total_value,
                'concentration_risk': 'high' if total_btc > 50 else 'medium',
                'liquidity_risk': 'low' if total_btc < 100 else 'medium'
            },
            'risk_metrics': {
                'value_at_risk_5pct': var_5pct,
                'stress_test_loss_15pct': stress_test_loss,
                'daily_volatility_estimate': total_value * 0.04  # 4% daily vol
            },
            'protection_analysis': {
                'weekly_protection_cost': protection_cost_weekly,
                'protection_benefit': protection_benefit,
                'roi_of_protection': (protection_benefit / protection_cost_weekly) if protection_cost_weekly > 0 else 0,
                'recommendation': 'weekly_protection_strongly_recommended'
            },
            'analysis_timestamp': datetime.now(timezone.utc).isoformat()
        }
        
        return risk_analysis
