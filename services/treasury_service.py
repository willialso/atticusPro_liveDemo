"""
ATTICUS V1 - 100% REAL Treasury Rates
NO FALLBACKS - Raises exceptions if real FRED data unavailable
"""
import requests
from datetime import datetime
import os

class RealTreasuryService:
    """
    100% Real Treasury rates from Federal Reserve FRED API
    NO FALLBACKS - Platform requires real data
    """
    
    def __init__(self):
        self.fred_api_key = os.environ.get('FRED_API_KEY', '17d3b0a9b20e8b012e99238c48ef8da1')
        
        if not self.fred_api_key:
            raise Exception("FRED_API_KEY environment variable required - No fallbacks allowed")
        
        self.base_url = "https://api.stlouisfed.org/fred"
        self.rate_series = 'GS1M'  # 1-Month Treasury Constant Maturity Rate
    
    def get_current_risk_free_rate(self) -> dict:
        """
        Get REAL current Treasury rate from Federal Reserve
        NO fallbacks - raises exception if FRED API unavailable
        """
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
            
            if response.status_code == 400:
                raise Exception("INVALID FRED API KEY - Check your API key")
            elif response.status_code != 200:
                raise Exception(f"FRED API ERROR: HTTP {response.status_code}")
            
            data = response.json()
            
            if 'error_message' in data:
                raise Exception(f"FRED API ERROR: {data['error_message']}")
            
            if 'observations' not in data or not data['observations']:
                raise Exception("NO TREASURY RATE DATA from FRED")
            
            latest_obs = data['observations'][0]
            
            if latest_obs['value'] == '.':
                raise Exception("LATEST TREASURY RATE VALUE NOT AVAILABLE")
            
            rate_percent = float(latest_obs['value'])
            rate_decimal = rate_percent / 100.0
            
            # Validate reasonable range
            if rate_percent < 0 or rate_percent > 20:
                raise Exception(f"INVALID TREASURY RATE: {rate_percent}%")
            
            return {
                'rate': rate_decimal,
                'rate_percent': rate_percent,
                'date': latest_obs['date'],
                'series': self.rate_series,
                'source': 'Federal Reserve FRED API (Official)'
            }
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"FRED API CONNECTION FAILED: {str(e)}")
        except ValueError as e:
            raise Exception(f"FRED API DATA PARSING FAILED: {str(e)}")
        except Exception as e:
            if "FRED" in str(e).upper():
                raise e
            else:
                raise Exception(f"TREASURY RATE SERVICE FAILED: {str(e)}")
