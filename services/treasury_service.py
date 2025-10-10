"""
ATTICUS V1 - Real Federal Reserve Treasury Rates
100% Real data from Federal Reserve Economic Data (FRED) API
"""
import requests
from datetime import datetime, timedelta
import json

class TreasuryRateService:
    """
    Real-time Treasury rates from Federal Reserve FRED API
    NO FALLBACKS - Raises exceptions if real data unavailable
    """
    
    def __init__(self):
        # FRED API for Federal Reserve Economic Data
        self.fred_api_key = "YOUR_FRED_API_KEY"  # Free registration at fred.stlouisfed.org
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
        NO FALLBACKS - Raises exception if unavailable
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
                'source': 'Federal Reserve FRED API'
            }
            
        except Exception as e:
            # NO FALLBACK - Platform requires real data
            raise Exception(f"Unable to get real Treasury rate: {str(e)}")
    
    def get_yield_curve_data(self):
        """Get complete yield curve from Federal Reserve"""
        try:
            curve_data = {}
            
            for maturity, series_id in self.rate_series.items():
                rate_data = self.get_current_risk_free_rate(maturity.replace('month', 'month').replace('year', 'year'))
                curve_data[maturity] = rate_data
                
            return curve_data
            
        except Exception as e:
            raise Exception(f"Unable to get yield curve: {str(e)}")

# Alternative Treasury Service using Treasury Direct API
class TreasuryDirectService:
    """
    Alternative Treasury rate service using Treasury.gov direct API
    """
    
    def __init__(self):
        self.base_url = "https://api.fiscaldata.treasury.gov/services/api/fiscal_service"
    
    def get_current_risk_free_rate(self):
        """
        Get current Treasury rate from Treasury.gov API
        Uses Daily Treasury Yield Curve Rates
        """
        try:
            # Get most recent daily Treasury yield curve rates
            url = f"{self.base_url}/v1/accounting/od/avg_interest_rates"
            
            params = {
                'filter': 'record_date:gte:2024-01-01',
                'sort': '-record_date',
                'page[size]': 1,
                'fields': 'record_date,avg_interest_rate_amt,security_type_desc'
            }
            
            response = requests.get(url, params=params, timeout=15)
            
            if response.status_code != 200:
                raise Exception(f"Treasury API error: {response.status_code}")
            
            data = response.json()
            
            if not data.get('data'):
                raise Exception("No Treasury rate data available")
            
            # Find 1-month equivalent rate
            for record in data['data']:
                if '1-month' in record.get('security_type_desc', '').lower():
                    rate_percent = float(record['avg_interest_rate_amt'])
                    
                    return {
                        'rate': rate_percent / 100.0,
                        'rate_percent': rate_percent,
                        'date': record['record_date'],
                        'source': 'Treasury Direct API'
                    }
            
            raise Exception("1-month Treasury rate not found in response")
            
        except Exception as e:
            raise Exception(f"Treasury Direct API failed: {str(e)}")
