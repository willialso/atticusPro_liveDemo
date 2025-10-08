"""
Tests for Perp Position Reader
"""
import pytest
import sys
import os

# Add the parent directory to sys.path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.perp_reader import PerpPositionReader

def test_perp_reader_initialization():
    """Test that PerpPositionReader initializes correctly"""
    reader = PerpPositionReader()
    assert reader is not None
    assert hasattr(reader, 'positions_cache')
    assert hasattr(reader, 'last_update')

def test_get_coinbase_positions():
    """Test Coinbase position reading"""
    reader = PerpPositionReader()
    positions = reader.get_coinbase_positions()
    
    # Should return a list
    assert isinstance(positions, list)
    
    # If positions exist, they should have required fields
    if positions:
        pos = positions[0]
        required_fields = ['symbol', 'size', 'avg_entry_price', 'current_price']
        for field in required_fields:
            assert field in pos

def test_get_all_positions():
    """Test getting positions from all exchanges"""
    reader = PerpPositionReader()
    all_positions = reader.get_all_positions()
    
    # Should return a dict with exchange keys
    assert isinstance(all_positions, dict)
    assert 'coinbase' in all_positions
    assert 'okx' in all_positions
    assert 'timestamp' in all_positions

def test_calculate_total_exposure():
    """Test exposure calculation"""
    reader = PerpPositionReader()
    
    # Mock position data
    mock_positions = {
        'coinbase': [{
            'size': '1.5',
            'current_price': '68000',
            'unrealized_pnl': '1500'
        }],
        'okx': [{
            'size': '0.5',
            'side': 'long',
            'current_price': '68000',
            'unrealized_pnl': '500'
        }]
    }
    
    exposure = reader.calculate_total_exposure(mock_positions)
    
    # Check return structure
    required_fields = [
        'long_exposure_btc', 'short_exposure_btc', 'net_exposure_btc',
        'total_notional_usd', 'total_unrealized_pnl', 'position_count'
    ]
    
    for field in required_fields:
        assert field in exposure
        
    # Check calculations
    assert exposure['position_count'] == 2
    assert exposure['long_exposure_btc'] == 2.0  # 1.5 + 0.5

if __name__ == "__main__":
    print("🧪 Running Perp Position Reader Tests...")
    
    # Run basic tests
    test_perp_reader_initialization()
    print("✅ Initialization test passed")
    
    test_get_coinbase_positions()
    print("✅ Coinbase positions test passed")
    
    test_get_all_positions()
    print("✅ All positions test passed")
    
    test_calculate_total_exposure()
    print("✅ Exposure calculation test passed")
    
    print("\n🎉 All tests passed!")
