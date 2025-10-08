"""
Updated configuration to properly handle PEM private key file
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Function to load PEM private key from file
def load_private_key():
    pem_file = os.getenv('COINBASE_PRIVATE_KEY_FILE', '')
    
    if pem_file and os.path.exists(pem_file):
        try:
            with open(pem_file, 'r') as f:
                return f.read()
        except Exception as e:
            print(f"❌ Error reading PEM file: {e}")
            return ''
    else:
        print(f"❌ PEM file not found: {pem_file}")
        return ''

# Coinbase Advanced Trade API Configuration
COINBASE_CONFIG = {
    'api_key_name': os.getenv('COINBASE_API_KEY_NAME', ''),
    'private_key': load_private_key(),
}

# General Settings
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
REFRESH_INTERVAL = int(os.getenv('REFRESH_INTERVAL', '5'))

# Supported symbols
SUPPORTED_PERP_SYMBOLS = [
    'BTC-USD-PERP',
    'ETH-USD-PERP',
    'SOL-USD-PERP'
]
