#!/usr/bin/env python3
"""
Comprehensive content optimization for all pages:
- Fewer words, larger text, smaller boxes
- Clean display on all platforms
"""
import re

def optimize_all_content():
    # Read template
    with open('templates/index.html', 'r') as f:
        content = f.read()
    
    print("🎯 Optimizing content for cross-platform consistency...")
    
    # ========= CHALLENGE SECTION =========
    print("   📊 Challenge Section - Stat Cards")
    
    # Keep stat card descriptions very short (1 line)
    content = content.replace(
        'Institutional crypto AUM',
        'Institutional AUM'
    )
    
    content = content.replace(
        'BTC annualized volatility',
        'BTC Volatility'
    )
    
    content = content.replace(
        'Typical institutional position',
        'Institutional Position'
    )
    
    content = content.replace(
        'Loss from 30% decline',
        'Loss from Decline'
    )
    
    # ========= PROBLEM CARDS =========
    print("   🔧 Problem Cards - Shorter Headings & Content")
    
    # Super short problem headings (1-2 words)
    content = content.replace(
        'Traditional Hedging Fails',
        'Slow Hedging'
    )
    
    content = content.replace(
        'Limited Institutional Solutions',
        'Limited Solutions'
    )
    
    content = content.replace(
        'Platform Risk Exposure',
        'Risk Exposure'
    )
    
    # Super short problem descriptions (1 line each)
    content = content.replace(
        'Conventional derivatives take hours while Bitcoin moves in minutes',
        'Traditional derivatives too slow for Bitcoin volatility'
    )
    
    content = content.replace(
        'Existing platforms lack institutional-size contracts and transparency',
        'Platforms lack institutional contracts and transparency'
    )
    
    content = content.replace(
        "Most platforms don't hedge their own exposure, creating counterparty risk",
        'Platforms create risk by not hedging own exposure'
    )
    
    # ========= SOLUTION SECTION =========
    print("   💡 Solution Section - Compact Feature Cards")
    
    # Shorter solution headings
    content = content.replace(
        'Real-Time Black-Scholes Pricing',
        'Live Pricing'
    )
    
    content = content.replace(
        'Platform Net Exposure Hedging',
        'Auto Hedging'
    )
    
    content = content.replace(
        'Deep Portfolio Analytics',
        'Risk Analytics'
    )
    
    content = content.replace(
        'Multi-Exchange Routing',
        'Multi-Exchange'
    )
    
    # Shorter solution descriptions (1 line each)
    content = content.replace(
        'Mathematical precision with live market data and transparent 2.5% markup',
        'Live market pricing with 2.5% transparent markup'
    )
    
    content = content.replace(
        'We hedge our own exposure across all clients at a 110% coverage ratio',
        'Platform hedges all exposure at 110% coverage'
    )
    
    content = content.replace(
        'VaR analysis, scenario modeling, Greeks, and institutional risk metrics',
        'VaR analysis, Greeks, and risk metrics'
    )
    
    content = content.replace(
        'Optimal execution across Deribit, OKX, Binance, Coinbase, Kraken',
        'Execution across Deribit, OKX, Binance, Kraken'
    )
    
    # ========= LIVE DEMO SECTION =========
    print("   🔴 Live Demo - Portfolio Types")
    
    # Shorter portfolio headings
    content = content.replace(
        'State Pension Fund',
        'Pension Fund'
    )
    
    content = content.replace(
        'Quantitative Hedge Fund',
        'Hedge Fund'
    )
    
    content = content.replace(
        'UHNW Family Office',
        'Family Office'
    )
    
    content = content.replace(
        'Corporate Treasury',
        'Treasury'
    )
    
    # Shorter portfolio descriptions
    content = content.replace(
        '$2.1B AUM 3% BTC Allocation Conservative Risk',
        '$2.1B AUM, 3% BTC, Conservative'
    )
    
    content = content.replace(
        '$450M AUM 15% BTC Allocation Aggressive Risk',
        '$450M AUM, 15% BTC, Aggressive'
    )
    
    content = content.replace(
        '$180M AUM 8% BTC Allocation Moderate Risk',
        '$180M AUM, 8% BTC, Moderate'
    )
    
    content = content.replace(
        '$500M AUM 5% BTC Allocation Conservative Risk',
        '$500M AUM, 5% BTC, Conservative'
    )
    
    # ========= GENERAL OPTIMIZATIONS =========
    print("   ✨ General Content Polish")
    
    # Shorter section subtitles
    content = content.replace(
        'Bitcoin volatility threatens institutional portfolios',
        'Bitcoin volatility threatens portfolios'
    )
    
    content = content.replace(
        'Real-time hedging with institutional-grade options',
        'Real-time institutional hedging'
    )
    
    content = content.replace(
        'Experience institutional-grade Bitcoin options hedging',
        'Institutional Bitcoin options hedging'
    )
    
    # Write optimized content
    with open('templates/index.html', 'w') as f:
        f.write(content)
    
    print("✅ Content optimization complete!")
    print("📦 All text shortened for cross-platform consistency")

if __name__ == "__main__":
    optimize_all_content()
