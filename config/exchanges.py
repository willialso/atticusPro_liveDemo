"""
Exchange API Configuration for Multi-Venue Pricing
"""

EXCHANGES = {
    'deribit': {
        'name': 'Deribit',
        'base_url': 'https://www.deribit.com/api/v2',
        'endpoints': {
            'btc_index': '/public/get_index?currency=BTC',
            'options': '/public/get_instruments?currency=BTC&kind=option&expired=false',
            'orderbook': '/public/get_order_book',
            'ticker': '/public/ticker'
        },
        'rate_limit': 20,  # requests per second
        'priority': 1      # Primary exchange
    },
    'okx': {
        'name': 'OKX',
        'base_url': 'https://www.okx.com/api/v5',
        'endpoints': {
            'btc_price': '/market/ticker?instId=BTC-USDT',
            'options': '/public/instruments?instType=OPTION&uly=BTC-USD'
        },
        'rate_limit': 10,
        'priority': 2      # Secondary for comparison
    }
}
