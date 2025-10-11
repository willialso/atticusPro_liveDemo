"""
Real Treasury Service - Render Deployment
"""
import requests
from datetime import datetime

class RealTreasuryService:
    def __init__(self):
        self.session = requests.Session()
    
    def get_current_risk_free_rate(self):
        """Get current risk-free rate"""
        try:
            url = "https://api.stlouisfed.org/fred/series/observations"
            params = {
                'series_id': 'DGS10',
                'api_key': 'demo',
                'limit': 1,
                'sort_order': 'desc',
                'file_type': 'json'
            }
            
            response = self.session.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if 'observations' in data and len(data['observations']) > 0:
                    rate = float(data['observations'][0]['value'])
                    return {
                        'rate_percent': rate,
                        'rate_decimal': rate / 100,
                        'date': data['observations'][0]['date'],
                        'source': 'Federal Reserve Economic Data (FRED)'
                    }
        except Exception as e:
            print(f"Treasury rate error: {e}")
        
        return {
            'rate_percent': 4.25,
            'rate_decimal': 0.0425,
            'date': datetime.now().strftime('%Y-%m-%d'),
            'source': 'RENDER_FALLBACK'
        }
