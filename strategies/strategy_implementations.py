"""
ATTICUS V1 - Complete Professional Strategy Implementations
100% Real strategies using actual Deribit options
"""
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
import math

class StrategyImplementations:
    """
    Complete implementations of professional option strategies
    Uses ONLY real Deribit instruments and pricing
    """
    
    def __init__(self, pricing_engine, market_data_service):
        self.pricing_engine = pricing_engine
        self.market_data = market_data_service
    
    def find_protective_puts(self, net_btc: float, current_price: float, 
                           available_options: List[Dict], iv_surface: Dict) -> List[Dict]:
        """
        COMPLETE protective puts implementation
        Returns ONLY executable strategies with real Deribit instruments
        """
        if net_btc <= 0:
            raise Exception("Protective puts only applicable for long BTC positions")
        
        suitable_puts = []
        
        # Filter for institutional-grade protective puts
        for option in available_options:
            if not self._is_suitable_protective_put(option, current_price):
                continue
            
            try:
                # Get REAL implied volatility from Deribit
                expiry_date = datetime.fromtimestamp(option['expiration_timestamp'] / 1000)
                surface_key = (option['strike'], expiry_date, 'put')
                
                if surface_key not in iv_surface:
                    continue  # Skip if no real IV data
                
                iv_data = iv_surface[surface_key]
                
                # Verify this is a liquid, tradeable option
                if not self._verify_option_liquidity(option['instrument_name'], iv_data):
                    continue
                
                # Calculate REAL Black-Scholes pricing
                time_to_expiry = (expiry_date - datetime.now()).days / 365.0
                
                pricing = self.pricing_engine.calculate_option_price(
                    spot_price=current_price,
                    strike_price=option['strike'],
                    time_to_expiry=time_to_expiry,
                    implied_volatility=iv_data['implied_volatility'],
                    option_type='put'
                )
                
                # Calculate position sizing
                contracts_needed = int(net_btc)  # 1 contract per BTC
                
                # Calculate protection effectiveness
                protection_metrics = self._calculate_protection_effectiveness(
                    pricing, option, net_btc, current_price
                )
                
                suitable_puts.append({
                    'strategy_name': 'protective_put',
                    'display_name': f'Protective Put - {option["strike"]} Strike',
                    'target_exposure': net_btc,
                    'priority': self._assess_strategy_priority(protection_metrics),
                    'rationale': f'Professional downside protection using {option["instrument_name"]}',
                    'pricing': {
                        'btc_spot_price': current_price,
                        'contracts_needed': contracts_needed,
                        'strike_price': option['strike'],
                        'premium_per_contract': pricing['platform_price'],
                        'total_premium': contracts_needed * pricing['platform_price'],
                        'theoretical_premium': contracts_needed * pricing['theoretical_price'],
                        'platform_markup': contracts_needed * pricing['markup_amount'],
                        'implied_volatility': iv_data['implied_volatility'],
                        'days_to_expiry': (expiry_date - datetime.now()).days,
                        'expiry_date': expiry_date.strftime("%Y-%m-%d"),
                        'option_type': f'Deribit Put Option',
                        'cost_as_pct': (contracts_needed * pricing['platform_price']) / (net_btc * current_price) * 100,
                        'greeks': pricing['greeks'],
                        'deribit_instrument': option['instrument_name']
                    },
                    'protection_analysis': protection_metrics,
                    'market_data': {
                        'deribit_mark_price': iv_data.get('mark_price', 0),
                        'deribit_bid': iv_data.get('bid_price', 0),
                        'deribit_ask': iv_data.get('ask_price', 0),
                        'open_interest': iv_data.get('open_interest', 0)
                    }
                })
                
            except Exception as e:
                print(f"Error processing protective put {option['instrument_name']}: {e}")
                continue
        
        if not suitable_puts:
            raise Exception("No suitable protective puts available with sufficient liquidity")
        
        # Sort by cost-effectiveness (protection per dollar spent)
        suitable_puts.sort(key=lambda x: x['protection_analysis']['cost_effectiveness'], reverse=True)
        
        return suitable_puts[:3]  # Return top 3 strategies
    
    def find_put_spreads(self, net_btc: float, current_price: float,
                        available_options: List[Dict], iv_surface: Dict) -> List[Dict]:
        """
        COMPLETE put spread implementation
        Creates REAL bear put spreads using Deribit options
        """
        if net_btc <= 0:
            return []
        
        put_spreads = []
        
        # Group puts by expiry for spread creation
        puts_by_expiry = self._group_options_by_expiry(available_options, 'put')
        
        for expiry_days, puts in puts_by_expiry.items():
            if len(puts) < 2:
                continue
            
            # Find optimal spread combinations
            spreads = self._find_optimal_put_spread_combinations(
                puts, current_price, iv_surface, net_btc
            )
            put_spreads.extend(spreads)
        
        if not put_spreads:
            return []  # No spreads available
        
        # Sort by cost-effectiveness
        put_spreads.sort(key=lambda x: x['spread_analysis']['risk_reward_ratio'], reverse=True)
        
        return put_spreads[:2]  # Return top 2 spreads
    
    def find_covered_calls(self, net_btc: float, current_price: float,
                          available_options: List[Dict], iv_surface: Dict) -> List[Dict]:
        """
        COMPLETE covered call implementation
        Uses REAL Deribit call options for income generation
        """
        if net_btc <= 0:
            return []
        
        covered_calls = []
        
        # Filter for suitable covered call strikes (OTM calls)
        for option in available_options:
            if not self._is_suitable_covered_call(option, current_price):
                continue
            
            try:
                expiry_date = datetime.fromtimestamp(option['expiration_timestamp'] / 1000)
                surface_key = (option['strike'], expiry_date, 'call')
                
                if surface_key not in iv_surface:
                    continue
                
                iv_data = iv_surface[surface_key]
                
                # Verify liquidity for covered call writing
                if not self._verify_option_liquidity(option['instrument_name'], iv_data):
                    continue
                
                time_to_expiry = (expiry_date - datetime.now()).days / 365.0
                
                pricing = self.pricing_engine.calculate_option_price(
                    spot_price=current_price,
                    strike_price=option['strike'],
                    time_to_expiry=time_to_expiry,
                    implied_volatility=iv_data['implied_volatility'],
                    option_type='call'
                )
                
                # Calculate covered call metrics
                contracts_to_write = int(net_btc)
                income_metrics = self._calculate_covered_call_metrics(
                    pricing, option, contracts_to_write, current_price, net_btc
                )
                
                covered_calls.append({
                    'strategy_name': 'covered_call',
                    'display_name': f'Covered Call - {option["strike"]} Strike',
                    'target_exposure': net_btc,
                    'priority': 'medium',
                    'rationale': f'Generate income by writing calls against BTC position using {option["instrument_name"]}',
                    'pricing': {
                        'btc_spot_price': current_price,
                        'contracts_needed': contracts_to_write,
                        'strike_price': option['strike'],
                        'premium_per_contract': pricing['platform_price'],
                        'total_premium': -contracts_to_write * pricing['platform_price'],  # Negative = income
                        'theoretical_premium': -contracts_to_write * pricing['theoretical_price'],
                        'platform_markup': contracts_to_write * pricing['markup_amount'],  # Platform keeps markup
                        'implied_volatility': iv_data['implied_volatility'],
                        'days_to_expiry': (expiry_date - datetime.now()).days,
                        'expiry_date': expiry_date.strftime("%Y-%m-%d"),
                        'option_type': f'Deribit Call Option (Short)',
                        'cost_as_pct': (contracts_to_write * pricing['platform_price']) / (net_btc * current_price) * 100,
                        'greeks': {k: -v for k, v in pricing['greeks'].items()},  # Negative for short position
                        'deribit_instrument': option['instrument_name']
                    },
                    'income_analysis': income_metrics,
                    'market_data': {
                        'deribit_mark_price': iv_data.get('mark_price', 0),
                        'deribit_bid': iv_data.get('bid_price', 0),
                        'deribit_ask': iv_data.get('ask_price', 0),
                        'open_interest': iv_data.get('open_interest', 0)
                    }
                })
                
            except Exception as e:
                print(f"Error processing covered call {option['instrument_name']}: {e}")
                continue
        
        if not covered_calls:
            return []
        
        # Sort by income potential
        covered_calls.sort(key=lambda x: x['income_analysis']['annualized_yield'], reverse=True)
        
        return covered_calls[:2]  # Return top 2 income strategies
    
    def _is_suitable_protective_put(self, option: Dict, current_price: float) -> bool:
        """Check if put option is suitable for institutional protection"""
        if option['option_type'].lower() != 'put':
            return False
        
        days_to_expiry = (datetime.fromtimestamp(option['expiration_timestamp'] / 1000) - datetime.now()).days
        
        return (
            option.get('is_active', False) and
            7 <= days_to_expiry <= 90 and  # 1 week to 3 months
            current_price * 0.85 <= option['strike'] <= current_price * 0.98  # Reasonable protection range
        )
    
    def _is_suitable_covered_call(self, option: Dict, current_price: float) -> bool:
        """Check if call option is suitable for covered call writing"""
        if option['option_type'].lower() != 'call':
            return False
        
        days_to_expiry = (datetime.fromtimestamp(option['expiration_timestamp'] / 1000) - datetime.now()).days
        
        return (
            option.get('is_active', False) and
            14 <= days_to_expiry <= 60 and  # 2 weeks to 2 months for income
            current_price * 1.02 <= option['strike'] <= current_price * 1.20  # OTM calls
        )
    
    def _verify_option_liquidity(self, instrument_name: str, iv_data: Dict) -> bool:
        """Verify option has sufficient liquidity for institutional use"""
        try:
            # Get real orderbook data
            orderbook = self.market_data.get_option_orderbook(instrument_name)
            
            if not orderbook or not orderbook.get('bids') or not orderbook.get('asks'):
                return False
            
            # Check bid-ask spread
            best_bid = orderbook['bids'][0][0] if orderbook['bids'] else 0
            best_ask = orderbook['asks'][0][0] if orderbook['asks'] else 0
            
            if best_bid <= 0 or best_ask <= 0:
                return False
            
            spread_percent = ((best_ask - best_bid) / best_ask) * 100
            
            # Liquidity requirements
            min_open_interest = 10  # Minimum open interest
            max_spread_percent = 5.0  # Maximum 5% bid-ask spread
            
            return (
                iv_data.get('open_interest', 0) >= min_open_interest and
                spread_percent <= max_spread_percent and
                len(orderbook.get('bids', [])) >= 3  # At least 3 bid levels
            )
            
        except:
            return False
    
    def _calculate_protection_effectiveness(self, pricing: Dict, option: Dict, 
                                          net_btc: float, current_price: float) -> Dict:
        """Calculate real protection effectiveness metrics"""
        strike_price = option['strike']
        total_premium = pricing['platform_price'] * int(net_btc)
        
        # Maximum loss with protection (premium + any loss below strike)
        max_loss_protected = total_premium
        
        # Maximum loss without protection (if BTC goes to zero)
        max_loss_unprotected = net_btc * current_price
        
        # Protection effectiveness
        protection_ratio = 1.0 - (max_loss_protected / max_loss_unprotected)
        
        # Cost-effectiveness (protection gained per dollar spent)
        cost_effectiveness = protection_ratio / (total_premium / (net_btc * current_price))
        
        # Breakeven point
        breakeven_price = current_price - (total_premium / net_btc)
        
        return {
            'max_loss_protected': max_loss_protected,
            'max_loss_unprotected': max_loss_unprotected,
            'protection_ratio': protection_ratio,
            'cost_effectiveness': cost_effectiveness,
            'breakeven_price': breakeven_price,
            'protection_range': f'${strike_price:,.0f} - ${current_price:,.0f}'
        }
    
    def _calculate_covered_call_metrics(self, pricing: Dict, option: Dict,
                                      contracts: int, current_price: float, net_btc: float) -> Dict:
        """Calculate covered call income metrics"""
        strike_price = option['strike']
        premium_income = pricing['platform_price'] * contracts
        days_to_expiry = (datetime.fromtimestamp(option['expiration_timestamp'] / 1000) - datetime.now()).days
        
        # Yield calculations
        position_value = net_btc * current_price
        yield_if_unchanged = (premium_income / position_value) * 100
        annualized_yield = yield_if_unchanged * (365 / days_to_expiry)
        
        # Maximum return if called away
        max_return = ((strike_price - current_price) * net_btc + premium_income) / position_value * 100
        
        # Upside cap
        upside_cap_price = strike_price
        upside_cap_percent = ((upside_cap_price / current_price) - 1) * 100
        
        return {
            'premium_income': premium_income,
            'yield_if_unchanged': yield_if_unchanged,
            'annualized_yield': annualized_yield,
            'max_return': max_return,
            'upside_cap_price': upside_cap_price,
            'upside_cap_percent': upside_cap_percent,
            'breakeven_price': current_price - (premium_income / net_btc)
        }
    
    def _group_options_by_expiry(self, available_options: List[Dict], option_type: str) -> Dict:
        """Group options by expiry date for spread construction"""
        grouped = {}
        
        for option in available_options:
            if option['option_type'].lower() == option_type.lower():
                days_to_expiry = (datetime.fromtimestamp(option['expiration_timestamp'] / 1000) - datetime.now()).days
                
                if days_to_expiry not in grouped:
                    grouped[days_to_expiry] = []
                
                grouped[days_to_expiry].append(option)
        
        return grouped
    
    def _find_optimal_put_spread_combinations(self, puts: List[Dict], current_price: float,
                                            iv_surface: Dict, net_btc: float) -> List[Dict]:
        """Find optimal put spread combinations"""
        spreads = []
        
        # Sort puts by strike price
        puts.sort(key=lambda x: x['strike'])
        
        # Find spread combinations (long higher strike, short lower strike)
        for i, long_put in enumerate(puts):
            for short_put in puts:
                if (short_put['strike'] < long_put['strike'] and
                    long_put['strike'] >= current_price * 0.90 and
                    short_put['strike'] >= current_price * 0.75):
                    
                    try:
                        spread_data = self._calculate_put_spread_data(
                            long_put, short_put, current_price, iv_surface, net_btc
                        )
                        
                        if spread_data['net_cost'] > 0:  # Only profitable spreads
                            spreads.append({
                                'strategy_name': 'put_spread',
                                'display_name': f'Put Spread {long_put["strike"]}/{short_put["strike"]}',
                                'target_exposure': net_btc,
                                'priority': 'medium',
                                'rationale': f'Cost-efficient protection using put spread',
                                'pricing': spread_data['pricing'],
                                'spread_analysis': spread_data['analysis']
                            })
                            
                    except Exception as e:
                        print(f"Error calculating put spread: {e}")
                        continue
        
        return spreads
    
    def _calculate_put_spread_data(self, long_put: Dict, short_put: Dict,
                                  current_price: float, iv_surface: Dict, net_btc: float) -> Dict:
        """Calculate complete put spread pricing and analysis"""
        
        # Get IV data for both puts
        long_expiry = datetime.fromtimestamp(long_put['expiration_timestamp'] / 1000)
        short_expiry = datetime.fromtimestamp(short_put['expiration_timestamp'] / 1000)
        
        long_key = (long_put['strike'], long_expiry, 'put')
        short_key = (short_put['strike'], short_expiry, 'put')
        
        if long_key not in iv_surface or short_key not in iv_surface:
            raise Exception("Missing IV data for spread components")
        
        long_iv = iv_surface[long_key]['implied_volatility']
        short_iv = iv_surface[short_key]['implied_volatility']
        
        # Calculate pricing for both legs
        long_time = (long_expiry - datetime.now()).days / 365.0
        short_time = (short_expiry - datetime.now()).days / 365.0
        
        long_pricing = self.pricing_engine.calculate_option_price(
            current_price, long_put['strike'], long_time, long_iv, 'put'
        )
        
        short_pricing = self.pricing_engine.calculate_option_price(
            current_price, short_put['strike'], short_time, short_iv, 'put'
        )
        
        # Spread calculations
        contracts = int(net_btc)
        net_premium = long_pricing['platform_price'] - short_pricing['platform_price']
        net_cost = contracts * net_premium
        
        max_profit = contracts * (long_put['strike'] - short_put['strike']) - net_cost
        max_loss = net_cost
        
        return {
            'net_cost': net_cost,
            'pricing': {
                'btc_spot_price': current_price,
                'contracts_needed': contracts,
                'long_strike': long_put['strike'],
                'short_strike': short_put['strike'],
                'long_premium': long_pricing['platform_price'],
                'short_premium': short_pricing['platform_price'],
                'total_premium': net_cost,
                'cost_as_pct': net_cost / (net_btc * current_price) * 100,
                'days_to_expiry': (long_expiry - datetime.now()).days,
                'expiry_date': long_expiry.strftime("%Y-%m-%d"),
                'option_type': f'Put Spread',
                'long_instrument': long_put['instrument_name'],
                'short_instrument': short_put['instrument_name']
            },
            'analysis': {
                'max_profit': max_profit,
                'max_loss': max_loss,
                'risk_reward_ratio': max_profit / max_loss if max_loss > 0 else 0,
                'breakeven_price': long_put['strike'] - (net_cost / contracts),
                'protection_range': f'${short_put["strike"]:,.0f} - ${long_put["strike"]:,.0f}'
            }
        }
    
    def _assess_strategy_priority(self, protection_metrics: Dict) -> str:
        """Assess strategy priority based on protection effectiveness"""
        cost_effectiveness = protection_metrics.get('cost_effectiveness', 0)
        protection_ratio = protection_metrics.get('protection_ratio', 0)
        
        if cost_effectiveness > 15 and protection_ratio > 0.8:
            return 'high'
        elif cost_effectiveness > 8 and protection_ratio > 0.6:
            return 'medium'
        else:
            return 'low'
