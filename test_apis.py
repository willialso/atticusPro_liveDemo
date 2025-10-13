#!/usr/bin/env python3
"""
Test script to verify API connectivity with real keys
"""

import requests
import json

# Real API Keys
FRED_KEY = "17d3b0a9b20e8b012e99238c48ef8da1"
COINGECKO_KEY = "CG-fkJcvVk4rakjCLAbo6ygiqGQ"

print("🔍 Testing API connectivity with real keys...")

# Test 1: Basic HTTP
print("\n1. Testing basic HTTP connectivity...")
try:
    response = requests.get('https://httpbin.org/status/200', timeout=5)
    print(f"✅ Basic HTTP: {response.status_code}")
except Exception as e:
    print(f"❌ Basic HTTP failed: {e}")

# Test 2: Coinbase Pro
print("\n2. Testing Coinbase Pro API...")
try:
    response = requests.get('https://api.exchange.coinbase.com/products/BTC-USD/ticker', timeout=10)
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Coinbase Pro: ${float(data['price']):,.2f}")
    else:
        print(f"❌ Coinbase Pro failed: {response.status_code}")
except Exception as e:
    print(f"❌ Coinbase Pro error: {e}")

# Test 3: Binance
print("\n3. Testing Binance API...")
try:
    response = requests.get('https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT', timeout=10)
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Binance: ${float(data['price']):,.2f}")
    else:
        print(f"❌ Binance failed: {response.status_code}")
except Exception as e:
    print(f"❌ Binance error: {e}")

# Test 4: CoinGecko with real key
print("\n4. Testing CoinGecko API with authentication...")
try:
    headers = {'X-CG-Demo-API-Key': COINGECKO_KEY}
    response = requests.get('https://api.coingecko.com/api/v3/ping', headers=headers, timeout=10)
    if response.status_code == 200:
        print(f"✅ CoinGecko authenticated: {response.json()}")
    else:
        print(f"❌ CoinGecko failed: {response.status_code} - {response.text}")
except Exception as e:
    print(f"❌ CoinGecko error: {e}")

# Test 5: FRED API with real key
print("\n5. Testing FRED API with real key...")
try:
    response = requests.get(
        'https://api.stlouisfed.org/fred/series/observations',
        params={
            'series_id': 'DGS3MO',
            'api_key': FRED_KEY,
            'file_type': 'json',
            'limit': '1'
        },
        timeout=10
    )
    if response.status_code == 200:
        data = response.json()
        print(f"✅ FRED API authenticated: {len(data.get('observations', []))} observations")
        if data.get('observations'):
            obs = data['observations'][0]
            print(f"   Latest rate: {obs.get('value')}% on {obs.get('date')}")
    else:
        print(f"❌ FRED failed: {response.status_code} - {response.text}")
except Exception as e:
    print(f"❌ FRED error: {e}")

print("\n🎯 API connectivity test completed!")
