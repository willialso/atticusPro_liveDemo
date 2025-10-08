"""
Updated Configuration with Correct Coinbase CDP API Keys
"""
import os
from typing import Dict

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Coinbase Configuration (Using your CDP keys)
COINBASE_CONFIG = {
    'api_key_name': os.getenv('COINBASE_API_KEY_NAME', 'organizations/3b1aa2e8-ad7c-4c7b-b5e5-fa1573b410e2/apiKeys/0a91499e-3a12-40cc-9db5-02bbd6c99e60'),
    'private_key': os.getenv('COINBASE_PRIVATE_KEY', '''-----BEGIN EC PRIVATE KEY-----
MHcCAQEEID3IA1makdc6E89+901M2HxYC2Yat+tm1sHzXw5ioq5aoAoGCCqGSM49
AwEHoUQDQgAERpbWyM+WOoA8c8DjEjoNcKc5a/9v9rTD3Xgh7gwAeL8hhMu4d6fj
uPzhJzBfGQ9XMs09QPaixf5qeDeUYOlSYw==
-----END EC PRIVATE KEY-----'''),
    'environment': 'production',
}

# Deribit Configuration (Options Primary)
DERIBIT_CONFIG = {
    'environment': 'production',
    'enable_rate_limit': True,
}

# Gemini Configuration (When verified)
GEMINI_CONFIG = {
    'api_key': os.getenv('GEMINI_API_KEY', ''),
    'secret': os.getenv('GEMINI_SECRET', ''),
    'environment': 'production',
}

# NYC Compliant Exchanges Only
NYC_EXCHANGES = {
    'coinbase_advanced': {
        'enabled': True,
        'purpose': 'spot_prices_and_futures',
        'config': COINBASE_CONFIG
    },
    'coinbase_prime': {
        'enabled': False,  # Enable when institutional account ready
        'purpose': 'institutional_custody',
        'config': COINBASE_CONFIG
    },
    'deribit': {
        'enabled': True,
        'purpose': 'btc_options_primary',
        'config': DERIBIT_CONFIG
    },
    'gemini': {
        'enabled': False,  # Enable when verified
        'purpose': 'additional_liquidity',
        'config': GEMINI_CONFIG
    }
}

# Platform Settings
PLATFORM_CONFIG = {
    'default_markup': 0.20,  # 20% platform margin
    'min_position_size': 0.01,  # 0.01 BTC minimum
    'max_position_size': 100.0,  # 100 BTC maximum per client
    'default_timeframe': 'weekly',
    'supported_timeframes': ['weekly', 'same_day'],
    'log_level': 'INFO'
}

# Risk Limits
RISK_LIMITS = {
    'max_net_exposure': 500.0,  # 500 BTC max platform exposure
    'max_single_client': 100.0,  # 100 BTC max per client
    'volatility_circuit_breaker': 0.15  # 15% daily vol limit
}
