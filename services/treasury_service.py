"""
ATTICUS V1 - Real Treasury Service
100% Real FRED API integration
"""
import requests
from datetime import datetime
import os

class RealTreasuryService:
    """100% Real Treasury rates from Federal Reserve"""
    
    def __init__(self):
        self.fred_api_key = os.environ.get('FRED_API_KEY', '17d3b0a9b20e8b012e99238c48ef8da1')
        
        if not self.fred_api_key:
            raise Exception("FRED_API_KEY required")
        
        self.base_url = "https://api.stlouisfed.org/fred"
        self.rate_series = 'GS1M'
    
    def get_current_risk_free_rate(self) -> dict:
        """Get REAL Treasury rate"""
        try:
            url = f"{self.base_url}/series/observations"
            params = {
                'series_id': self.rate_series,
                'api_key': self.fred_api_key,
                'file_type': 'json',
                'limit': 1,
                'sort_order': 'desc'
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code != 200:
                raise Exception(f"FRED API ERROR: {response.status_code}")
            
            data = response.json()
            
            if 'error_message' in data:
                raise Exception(f"FRED ERROR: {data['error_message']}")
            
            if 'observations' not in data or not data['observations']:
                raise Exception("NO TREASURY DATA")
            
            latest_obs = data['observations'][0]
            
            if latest_obs['value'] == '.':
                raise Exception("TREASURY VALUE UNAVAILABLE")
            
            rate_percent = float(latest_obs['value'])
            rate_decimal = rate_percent / 100.0
            
            if rate_percent < 0 or rate_percent > 20:
                raise Exception(f"INVALID RATE: {rate_percent}%")
            
            return {
                'rate': rate_decimal,
                'rate_percent': rate_percent,
                'date': latest_obs['date'],
                'series': self.rate_series,
                'source': 'Federal Reserve FRED API (Official)'
            }
            
        except Exception as e:
            raise Exception(f"TREASURY SERVICE FAILED: {str(e)}")
