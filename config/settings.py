"""
ATTICUS V1 - Professional Configuration
Platform profitability and risk management settings
"""
import os
from datetime import timedelta

class Config:
    # Platform Profitability Settings
    OPTION_MARKUP_RATE = 0.025          # 2.5% markup on Deribit pricing
    MIN_SPREAD_BPS = 15                 # Minimum 15 bps spread
    MAX_SINGLE_CLIENT_EXPOSURE = 0.30   # Max 30% of platform capital per client
    
    # Risk Management
    MAX_NET_EXPOSURE_BTC = 100.0        # Maximum platform net exposure
    DELTA_HEDGE_THRESHOLD = 0.1         # Hedge when delta exceeds 10%
    VAR_LIMIT_PERCENT = 0.02            # 2% daily VAR limit
    
    # Market Data
    DERIBIT_API_URL = 'https://www.deribit.com/api/v2'
    FED_TREASURY_URL = 'https://api.fiscaldata.treasury.gov/services/api/fiscal_service'
    CACHE_TTL = 30                      # 30 second price cache
    
    # Hedging Parameters
    MIN_HEDGE_SIZE = 0.1                # Minimum 0.1 BTC hedge
    HEDGE_REBALANCE_THRESHOLD = 0.05    # Rebalance at 5% delta drift
    LIQUIDITY_BUFFER = 0.20             # 20% liquidity buffer
    
    # Development vs Production
    ENVIRONMENT = os.getenv('ENVIRONMENT', 'development')
    DEBUG = ENVIRONMENT == 'development'
    
    @classmethod
    def get_risk_free_rate(cls):
        """Current 1-month Treasury rate for Black-Scholes"""
        return 0.045  # Will be replaced with real Fed API
    
    @classmethod
    def calculate_platform_fee(cls, premium_amount):
        """Calculate platform fee ensuring profitability"""
        base_fee = premium_amount * cls.OPTION_MARKUP_RATE
        return max(base_fee, premium_amount * cls.MIN_SPREAD_BPS / 10000)

