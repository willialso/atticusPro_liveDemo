"""
Optimal Hybrid Hedging Engine
Combines futures + options with smart selection across multiple venues
"""
import logging
from datetime import datetime, timezone
from typing import Dict, List, Tuple
import ccxt

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class HybridHedgingEngine:
    """
    Optimal hedging using futures + options across multiple exchanges
    """
    
    def __init__(self):
        self.exchanges = self._initialize_exchanges()
        self.current_btc_price = 0.0
        self.viable_options = []
        self.futures_prices = {}
        
        self._update_market_data()
    
    def _initialize_exchanges(self) -> Dict:
        """Initialize multiple exchanges for optimal pricing"""
        exchanges = {}
        
        try:
            # Deribit: Best for options, good futures
            exchanges['deribit'] = ccxt.deribit({
                'enableRateLimit': True,
                'sandbox': False
            })
            
            # Binance: Excellent futures liquidity
            exchanges['binance'] = ccxt.binance({
                'enableRateLimit': True,
                'sandbox': False
            })
            
            # OKX: Good options and futures
            exchanges['okx'] = ccxt.okx({
                'enableRateLimit': True,
                'sandbox': False
            })
            
            logger.info(f"✅ Initialized {len(exchanges)} exchanges for hedging")
            
        except Exception as e:
            logger.warning(f"⚠️  Exchange initialization: {e}")
            
        return exchanges
    
    def _update_market_data(self):
        """Update current market data from all venues"""
        try:
            # Get BTC price from multiple sources
            btc_prices = []
            
            for name, exchange in self.exchanges.items():
                try:
                    if name == 'deribit':
                        ticker = exchange.fetch_ticker('BTC-PERPETUAL')
                    else:
                        ticker = exchange.fetch_ticker('BTC/USDT')
                    
                    price = ticker['last']
                    btc_prices.append(price)
                    self.futures_prices[name] = {
                        'price': price,
                        'bid': ticker['bid'],
                        'ask': ticker['ask'],
                        'spread': ticker['ask'] - ticker['bid'] if ticker['bid'] and ticker['ask'] else None
                    }
                    
                except Exception as e:
                    logger.warning(f"⚠️  {name} price fetch failed: {e}")
            
            # Use average price for consistency
            if btc_prices:
                self.current_btc_price = sum(btc_prices) / len(btc_prices)
                logger.info(f"📊 Average BTC price: ${self.current_btc_price:,.2f}")
            
        except Exception as e:
            logger.error(f"❌ Market data update failed: {e}")
            self.current_btc_price = 122000  # Fallback
    
    def get_viable_options(self, target_strike_pct: float = 0.95) -> List[Dict]:
        """Get VIABLE options with proper filtering"""
        try:
            if 'deribit' not in self.exchanges:
                return []
            
            deribit = self.exchanges['deribit']
            markets = deribit.load_markets()
            
            target_strike = self.current_btc_price * target_strike_pct
            viable_options = []
            
            for symbol, market in markets.items():
                if (market['base'] == 'BTC' and 
                    market['type'] == 'option' and 
                    market['active']):
                    
                    try:
                        parts = symbol.split('-')
                        if len(parts) >= 4:
                            strike_price = float(parts[2])
                            option_type = parts[3]
                            
                            # Filter for viable puts near target strike
                            if (option_type == 'P' and 
                                0.90 <= strike_price / self.current_btc_price <= 0.98):
                                
                                # Get market data
                                ticker = deribit.fetch_ticker(symbol)
                                
                                # Viability checks
                                if (ticker['bid'] and ticker['ask'] and 
                                    ticker['baseVolume'] and ticker['baseVolume'] > 0.1):
                                    
                                    spread_pct = (ticker['ask'] - ticker['bid']) / ticker['ask'] * 100
                                    premium_pct = ticker['ask'] / self.current_btc_price * 100
                                    
                                    # Economic viability filters
                                    if (spread_pct < 15 and  # Max 15% bid-ask spread
                                        premium_pct < 8 and   # Max 8% premium
                                        ticker['ask'] < self.current_btc_price * 0.10):  # Reasonable premium
                                        
                                        viable_options.append({
                                            'symbol': symbol,
                                            'strike': strike_price,
                                            'bid': ticker['bid'],
                                            'ask': ticker['ask'],
                                            'volume': ticker['baseVolume'],
                                            'spread_pct': spread_pct,
                                            'premium_pct': premium_pct,
                                            'strike_diff': abs(strike_price - target_strike),
                                            'viability_score': self._calculate_viability_score(
                                                spread_pct, premium_pct, ticker['baseVolume']
                                            )
                                        })
                    except (ValueError, IndexError):
                        continue
            
            # Sort by viability score (best first)
            viable_options.sort(key=lambda x: x['viability_score'], reverse=True)
            self.viable_options = viable_options
            
            logger.info(f"✅ Found {len(viable_options)} viable options")
            return viable_options
            
        except Exception as e:
            logger.error(f"❌ Options filtering failed: {e}")
            return []
    
    def _calculate_viability_score(self, spread_pct: float, premium_pct: float, volume: float) -> float:
        """Calculate option viability score (higher = better)"""
        # Penalize high spreads and premiums, reward high volume
        spread_penalty = max(0, 20 - spread_pct)  # Better score for lower spreads
        premium_penalty = max(0, 10 - premium_pct)  # Better score for lower premiums
        volume_bonus = min(10, volume * 10)  # Bonus for higher volume
        
        return spread_penalty + premium_penalty + volume_bonus
    
    def get_best_futures_hedge(self) -> Dict:
        """Get best futures pricing across exchanges"""
        best_futures = None
        best_cost = float('inf')
        
        for exchange_name, price_data in self.futures_prices.items():
            if price_data['spread']:
                # For shorting (hedging long position), we pay the bid-ask spread
                hedge_cost = price_data['spread']
                
                if hedge_cost < best_cost:
                    best_cost = hedge_cost
                    best_futures = {
                        'exchange': exchange_name,
                        'price': price_data['price'],
                        'bid': price_data['bid'],
                        'ask': price_data['ask'],
                        'spread': price_data['spread'],
                        'hedge_cost_per_btc': hedge_cost
                    }
        
        if best_futures:
            logger.info(f"✅ Best futures: {best_futures['exchange']} (spread: ${best_futures['spread']:.2f})")
        
        return best_futures or {}
    
    def create_optimal_hedge(self, btc_position_size: float) -> Dict:
        """Create optimal hybrid hedge (futures + options)"""
        logger.info(f"📊 Creating optimal hedge for {btc_position_size:.4f} BTC")
        
        # Get market data
        viable_options = self.get_viable_options()
        best_futures = self.get_best_futures_hedge()
        
        position_value = btc_position_size * self.current_btc_price
        
        # Hybrid strategy decision
        if viable_options and best_futures:
            # Optimal: 70% futures + 30% options
            futures_portion = 0.70
            options_portion = 0.30
        elif best_futures:
            # Futures only (still effective)
            futures_portion = 1.00
            options_portion = 0.00
        elif viable_options:
            # Options only (less optimal but possible)
            futures_portion = 0.00
            options_portion = 1.00
        else:
            return {'success': False, 'reason': 'no_viable_hedges'}
        
        # Calculate hedge components
        hedge_components = []
        total_hedge_cost = 0.0
        
        # Futures component
        if futures_portion > 0:
            futures_size = btc_position_size * futures_portion
            futures_cost = futures_size * best_futures['hedge_cost_per_btc']
            
            hedge_components.append({
                'type': 'futures',
                'exchange': best_futures['exchange'],
                'size': futures_size,
                'cost': futures_cost,
                'portion': futures_portion * 100
            })
            total_hedge_cost += futures_cost
        
        # Options component
        if options_portion > 0 and viable_options:
            best_option = viable_options[0]  # Highest viability score
            options_size = btc_position_size * options_portion
            options_cost = options_size * best_option['ask']
            
            hedge_components.append({
                'type': 'option',
                'exchange': 'deribit',
                'symbol': best_option['symbol'],
                'strike': best_option['strike'],
                'size': options_size,
                'cost': options_cost,
                'portion': options_portion * 100
            })
            total_hedge_cost += options_cost
        
        # Platform markup (15% for hybrid strategy)
        platform_markup = 0.15
        client_premium = total_hedge_cost * (1 + platform_markup)
        platform_profit = client_premium - total_hedge_cost
        
        optimal_hedge = {
            'success': True,
            'strategy': 'hybrid_futures_options',
            'position_details': {
                'size_btc': btc_position_size,
                'position_value': position_value,
                'current_btc_price': self.current_btc_price
            },
            'hedge_components': hedge_components,
            'pricing': {
                'total_hedge_cost': total_hedge_cost,
                'platform_markup_pct': platform_markup * 100,
                'client_premium': client_premium,
                'platform_profit': platform_profit,
                'cost_per_btc': client_premium / btc_position_size
            },
            'execution': {
                'venues_used': len(set(comp['exchange'] for comp in hedge_components)),
                'liquidity_rating': 'excellent' if best_futures else 'good',
                'execution_complexity': 'moderate'
            },
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
        
        logger.info(f"✅ Optimal hedge: ${client_premium:.2f} premium ({len(hedge_components)} components)")
        return optimal_hedge

if __name__ == "__main__":
    print("🚀 Testing Optimal Hybrid Hedging Engine...")
    
    try:
        engine = HybridHedgingEngine()
        
        # Test with the previous position size
        test_position = 3.2
        optimal_hedge = engine.create_optimal_hedge(test_position)
        
        if optimal_hedge['success']:
            print("\n" + "="*80)
            print("🎯 OPTIMAL HYBRID HEDGE STRATEGY")
            print("="*80)
            
            pos = optimal_hedge['position_details']
            pricing = optimal_hedge['pricing']
            execution = optimal_hedge['execution']
            
            print(f"📊 Position: {pos['size_btc']:.2f} BTC (${pos['position_value']:,.2f})")
            print(f"💰 Client Premium: ${pricing['client_premium']:,.2f}")
            print(f"💵 Cost per BTC: ${pricing['cost_per_btc']:,.2f}")
            print(f"📈 Platform Profit: ${pricing['platform_profit']:,.2f}")
            print(f"🎯 Venues Used: {execution['venues_used']}")
            
            print(f"\n🔧 HEDGE COMPONENTS:")
            for i, comp in enumerate(optimal_hedge['hedge_components']):
                print(f"  {i+1}. {comp['type'].upper()}: {comp['size']:.2f} BTC on {comp['exchange']}")
                print(f"     Cost: ${comp['cost']:,.2f} ({comp['portion']:.0f}% of hedge)")
            
            print("="*80)
            print("✅ OPTIMAL HYBRID HEDGING WORKING!")
        else:
            print(f"❌ Hedge creation failed: {optimal_hedge['reason']}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
