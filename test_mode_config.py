"""
BLGV BTC Mining Pool - Test Mode Configuration
Matches Treasury Intelligence Platform test mode precision
"""

import os
import uuid
from datetime import datetime
from typing import Dict, Any, Optional

class TestModeConfig:
    """Test mode configuration matching Treasury Intelligence Platform"""
    
    def __init__(self):
        self.is_development = os.getenv('NODE_ENV', 'development') == 'development'
        self.is_test_mode = os.getenv('BLGV_TEST_MODE', 'true').lower() == 'true' if self.is_development else False
        self.show_fake_assets = os.getenv('BLGV_SHOW_FAKE_ASSETS', 'true').lower() == 'true' if self.is_test_mode else False
        self.test_session_id = self._generate_session_id()
        
    def _generate_session_id(self) -> str:
        """Generate consistent test session ID"""
        if self.is_test_mode:
            # Use consistent session ID for test mode
            base_id = f"test_{datetime.now().strftime('%Y%m%d')}"
            return f"{base_id}_{str(uuid.uuid4())[:8]}"
        return None
    
    def is_test_mode_active(self) -> bool:
        """Check if test mode is active"""
        return self.is_test_mode
    
    def should_show_fake_assets(self) -> bool:
        """Check if fake assets should be displayed - always False for real test data"""
        return False  # No fake assets, only real test data from database
    
    def get_test_session_id(self) -> Optional[str]:
        """Get current test session ID"""
        return self.test_session_id
    
    def get_fake_mining_data(self) -> Dict[str, Any]:
        """Get real test mining data from database (no fake inflation)"""
        # Return empty dict - no fake data should be added to real stats
        # Test mode should show actual test database records, not artificial inflation
        return {}
    
    def get_config_dict(self) -> Dict[str, Any]:
        """Get complete configuration dictionary"""
        return {
            'environment': 'development' if self.is_development else 'production',
            'platform': 'web',
            'testMode': {
                'isTestMode': self.is_test_mode,
                'showFakeAssets': self.show_fake_assets,
                'isolationLevel': 'session',
                'sessionId': self.test_session_id
            } if self.is_test_mode else False
        }

# Global test mode configuration instance
test_mode_config = TestModeConfig()

# Convenience functions
def is_test_mode() -> bool:
    """Check if test mode is active"""
    return test_mode_config.is_test_mode_active()

def should_show_fake_assets() -> bool:
    """Check if fake assets should be displayed - always False for real test data"""
    return test_mode_config.should_show_fake_assets()

def get_test_session_id() -> Optional[str]:
    """Get current test session ID"""
    return test_mode_config.get_test_session_id()

def get_fake_mining_data() -> Dict[str, Any]:
    """Get fake mining data"""
    return test_mode_config.get_fake_mining_data()

def filter_test_data(data: list, exclude_test: bool = True) -> list:
    """Filter test data from results"""
    if not exclude_test or is_test_mode():
        return data
    
    # Filter out test records
    return [item for item in data if not item.get('is_test_mode', False)]

def add_test_mode_fields(data: Dict[str, Any]) -> Dict[str, Any]:
    """Add test mode fields to data"""
    if is_test_mode():
        data['is_test_mode'] = True
        data['test_session_id'] = get_test_session_id()
    else:
        data['is_test_mode'] = False
        data['test_session_id'] = None
    
    return data