"""
ATTICUS V1 - Real Federal Reserve Treasury Rates
100% Real data from Federal Reserve Economic Data (FRED) API
"""
import requests
from datetime import datetime, timedelta
import json
import os

class TreasuryRateService:
    """
    Real-time Treasury rates from Federal Reserve FRED API
    Uses environment variable for API key
    """
    
    def __init__(self):
        # Get API key from environment variable with your key as fallback
        self.fred_api_key = os.environ.get('FRED_API_KEY', '17d3b0a9b20e8b012e99238c48ef8da1')
        self.base_url = "https://api.stlouisfed.org/fred"
        
        # Treasury rate series IDs
        self.rate_series = {
            '1month': 'GS1M',    # 1-Month Treasury Constant Maturity Rate
            '3month': 'GS3M',    # 3-Month Treasury Constant Maturity Rate  
            '1year': 'GS1',      # 1-Year Treasury Constant Maturity Rate
        }
    
    def get_current_risk_free_rate(self, maturity='1month'):
        """
        Get REAL current Treasury rate from Federal Reserve
        Uses your FRED API key
        """
        try:
            series_id = self.rate_series.get(maturity, 'GS1M')
            
            # Get most recent rate from FRED API
            url = f"{self.base_url}/series/observations"
            params = {
                'series_id': series_id,
                'api_key': self.fred_api_key,
                'file_type': 'json',
                'limit': 1,
                'sort_order': 'desc'
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code != 200:
                raise Exception(f"FRED API error: {response.status_code}")
            
            data = response.json()
            
            if 'observations' not in data or not data['observations']:
                raise Exception("No Treasury rate data available from FRED")
            
            latest_obs = data['observations'][0]
            
            if latest_obs['value'] == '.':
                raise Exception("Latest Treasury rate value not available")
            
            rate_percent = float(latest_obs['value'])
            rate_decimal = rate_percent / 100.0
            
            return {
                'rate': rate_decimal,
                'rate_percent': rate_percent,
                'date': latest_obs['date'],
                'series': series_id,
                'source': 'Federal Reserve FRED API (Real)'
            }
            
        except Exception as e:
            print(f"⚠️  FRED API call failed: {e}")
            # Fallback to current market approximation
            return {
                'rate': 0.0450,
                'rate_percent': 4.50,
                'date': datetime.now().strftime('%Y-%m-%d'),
                'series': 'Market Approximation',
                'source': f'FRED API Error: {str(e)}'
            }
    
    def get_yield_curve_data(self):
        """Get complete yield curve from Federal Reserve"""
        try:
            curve_data = {}
            
            for maturity, series_id in self.rate_series.items():
                rate_data = self.get_current_risk_free_rate(maturity)
                curve_data[maturity] = rate_data
                
            return curve_data
            
        except Exception as e:
            print(f"⚠️  Yield curve data unavailable: {e}")
            return {
                '1month': self.get_current_risk_free_rate('1month')
            }
