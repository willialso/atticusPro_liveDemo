"""
ATTICUS V1 - Real Execution Analysis Service
100% Real orderbook analysis and execution feasibility
"""
import requests
from typing import Dict, List, Optional
from datetime import datetime

class ExecutionAnalysisService:
    """
    Real execution analysis using actual Deribit orderbooks
    NO FAKE DATA - All analysis from real market conditions
    """
    
    def __init__(self, market_data_service):
        self.market_data = market_data_service
    
    def analyze_real_execution(self, strategy: Dict) -> Dict:
        """
        Comprehensive real execution analysis
        NO FALLBACKS - Raises exception if real data unavailable
        """
        try:
            instrument_name = strategy['pricing']['deribit_instrument']
            contracts_needed = strategy['pricing']['contracts_needed']
            
            # Get REAL orderbook data
            orderbook = self.market_data.get_option_orderbook(instrument_name)
            
            if not orderbook:
                raise Exception(f"No orderbook data available for {instrument_name}")
            
            # Calculate REAL liquidity metrics
            liquidity_analysis = self._analyze_real_liquidity(orderbook, contracts_needed)
            
            # Calculate REAL slippage estimates
            slippage_analysis = self._calculate_real_slippage(orderbook, contracts_needed)
            
            # Calculate REAL execution timing
            timing_analysis = self._analyze_execution_timing(orderbook, contracts_needed)
            
            # Calculate REAL market impact
            market_impact = self._calculate_real_market_impact(orderbook, contracts_needed)
            
            return {
                'instrument_name': instrument_name,
                'contracts_needed': contracts_needed,
                'execution_feasibility': liquidity_analysis['feasibility'],
                'liquidity_analysis': liquidity_analysis,
                'slippage_analysis': slippage_analysis,
                'timing_analysis': timing_analysis,
                'market_impact': market_impact,
                'execution_recommendation': self._generate_execution_recommendation(
                    liquidity_analysis, slippage_analysis, timing_analysis
                ),
                'analysis_timestamp': datetime.now().isoformat(),
                'data_source': 'Real Deribit Orderbook'
            }
            
        except Exception as e:
            raise Exception(f"Real execution analysis failed: {str(e)}")
    
    def _analyze_real_liquidity(self, orderbook: Dict, contracts_needed: int) -> Dict:
        """
        Analyze real liquidity from Deribit orderbook
        """
        if not orderbook.get('bids') or not orderbook.get('asks'):
            raise Exception("No bid/ask data in orderbook")
        
        bids = orderbook['bids']
        asks = orderbook['asks']
        
        # Calculate total available liquidity at each side
        total_bid_size = sum(bid[1] for bid in bids)
        total_ask_size = sum(ask[1] for ask in asks)
        
        # Calculate liquidity within reasonable price range (top 5 levels)
        top_5_bid_size = sum(bid[1] for bid in bids[:5])
        top_5_ask_size = sum(ask[1] for ask in asks[:5])
        
        # Determine execution feasibility
        if contracts_needed <= top_5_bid_size:
            feasibility = 'immediate'
        elif contracts_needed <= total_bid_size:
            feasibility = 'partial_immediate'
        elif contracts_needed <= total_bid_size * 2:  # Allow for refresh
            feasibility = 'workable'
        else:
            feasibility = 'insufficient'
        
        return {
            'feasibility': feasibility,
            'total_bid_size': total_bid_size,
            'total_ask_size': total_ask_size,
            'top_5_bid_size': top_5_bid_size,
            'top_5_ask_size': top_5_ask_size,
            'liquidity_ratio': contracts_needed / top_5_bid_size if top_5_bid_size > 0 else float('inf'),
            'best_bid': bids[0][0],
            'best_ask': asks[0][0],
            'bid_ask_spread': asks[0][0] - bids[0][0],
            'spread_bps': ((asks[0][0] - bids[0][0]) / asks[0][0]) * 10000
        }
    
    def _calculate_real_slippage(self, orderbook: Dict, contracts_needed: int) -> Dict:
        """
        Calculate real slippage from orderbook depth
        """
        bids = orderbook['bids']
        
        if not bids:
            raise Exception("No bid data for slippage calculation")
        
        best_bid = bids[0][0]
        contracts_remaining = contracts_needed
        weighted_price = 0
        total_filled = 0
        
        # Walk through orderbook levels
        for price, size in bids:
            if contracts_remaining <= 0:
                break
            
            fill_amount = min(contracts_remaining, size)
            weighted_price += price * fill_amount
            total_filled += fill_amount
            contracts_remaining -= fill_amount
        
        if total_filled == 0:
            raise Exception("Cannot fill any contracts at current prices")
        
        average_fill_price = weighted_price / total_filled
        slippage_absolute = best_bid - average_fill_price
        slippage_percent = (slippage_absolute / best_bid) * 100
        
        fill_percentage = (total_filled / contracts_needed) * 100
        
        return {
            'best_bid': best_bid,
            'average_fill_price': average_fill_price,
            'slippage_absolute': slippage_absolute,
            'slippage_percent': slippage_percent,
            'fill_percentage': fill_percentage,
            'contracts_filled': total_filled,
            'contracts_unfilled': contracts_needed - total_filled,
            'price_levels_used': sum(1 for _ in bids if contracts_needed > 0)
        }
    
    def _analyze_execution_timing(self, orderbook: Dict, contracts_needed: int) -> Dict:
        """
        Analyze real execution timing requirements
        """
        liquidity_depth = sum(bid[1] for bid in orderbook.get('bids', [])[:10])  # Top 10 levels
        
        # Estimate execution time based on order size vs available liquidity
        if contracts_needed <= liquidity_depth * 0.1:  # <10% of depth
            estimated_time_seconds = 5
            execution_method = 'immediate_market_order'
        elif contracts_needed <= liquidity_depth * 0.3:  # <30% of depth
            estimated_time_seconds = 30
            execution_method = 'split_market_orders'
        elif contracts_needed <= liquidity_depth:  # Within available depth
            estimated_time_seconds = 120
            execution_method = 'time_weighted_execution'
        else:
            estimated_time_seconds = 600  # 10 minutes for large orders
            execution_method = 'iceberg_order'
        
        return {
            'estimated_execution_time': estimated_time_seconds,
            'execution_method': execution_method,
            'liquidity_depth_ratio': contracts_needed / liquidity_depth if liquidity_depth > 0 else float('inf'),
            'recommended_order_type': self._recommend_order_type(contracts_needed, liquidity_depth)
        }
    
    def _calculate_real_market_impact(self, orderbook: Dict, contracts_needed: int) -> Dict:
        """
        Calculate real market impact from large orders
        """
        total_orderbook_size = sum(bid[1] for bid in orderbook.get('bids', []))
        
        if total_orderbook_size == 0:
            raise Exception("No orderbook depth for market impact calculation")
        
        # Market impact as percentage of total orderbook
        impact_ratio = contracts_needed / total_orderbook_size
        
        # Estimate price impact based on order size
        if impact_ratio < 0.05:  # <5% of orderbook
            price_impact_percent = impact_ratio * 0.5  # Low impact
        elif impact_ratio < 0.20:  # <20% of orderbook
            price_impact_percent = impact_ratio * 1.0  # Moderate impact
        else:
            price_impact_percent = impact_ratio * 2.0  # High impact
        
        return {
            'impact_ratio': impact_ratio,
            'estimated_price_impact_percent': price_impact_percent,
            'total_orderbook_size': total_orderbook_size,
            'impact_category': self._categorize_market_impact(impact_ratio)
        }
    
    def _recommend_order_type(self, contracts_needed: int, liquidity_depth: float) -> str:
        """Recommend optimal order type based on size and liquidity"""
        size_ratio = contracts_needed / liquidity_depth if liquidity_depth > 0 else float('inf')
        
        if size_ratio < 0.1:
            return 'market_order'
        elif size_ratio < 0.3:
            return 'limit_order_aggressive'
        elif size_ratio < 0.7:
            return 'twap_order'
        else:
            return 'iceberg_order'
    
    def _categorize_market_impact(self, impact_ratio: float) -> str:
        """Categorize market impact level"""
        if impact_ratio < 0.05:
            return 'low'
        elif impact_ratio < 0.15:
            return 'moderate'
        elif impact_ratio < 0.30:
            return 'high'
        else:
            return 'very_high'
    
    def _generate_execution_recommendation(self, liquidity_analysis: Dict, 
                                         slippage_analysis: Dict, 
                                         timing_analysis: Dict) -> Dict:
        """Generate comprehensive execution recommendation"""
        
        feasibility = liquidity_analysis['feasibility']
        slippage_percent = slippage_analysis['slippage_percent']
        execution_time = timing_analysis['estimated_execution_time']
        
        # Overall execution score (0-100)
        if feasibility == 'immediate' and slippage_percent < 0.5:
            score = 95
            recommendation = 'execute_immediately'
        elif feasibility == 'immediate' and slippage_percent < 1.0:
            score = 85
            recommendation = 'execute_with_caution'
        elif feasibility == 'partial_immediate':
            score = 70
            recommendation = 'split_execution'
        elif feasibility == 'workable':
            score = 50
            recommendation = 'time_weighted_execution'
        else:
            score = 20
            recommendation = 'reconsider_strategy'
        
        return {
            'overall_score': score,
            'recommendation': recommendation,
            'risk_level': 'low' if score > 80 else 'medium' if score > 50 else 'high',
            'execution_notes': self._generate_execution_notes(
                feasibility, slippage_percent, execution_time
            )
        }
    
    def _generate_execution_notes(self, feasibility: str, slippage: float, time: int) -> List[str]:
        """Generate specific execution notes"""
        notes = []
        
        if feasibility == 'insufficient':
            notes.append("Insufficient liquidity - consider reducing position size")
        
        if slippage > 1.0:
            notes.append(f"High slippage expected: {slippage:.2f}%")
        
        if time > 300:  # >5 minutes
            notes.append("Large order requires time-weighted execution")
        
        if not notes:
            notes.append("Execution conditions favorable")
        
        return notes
