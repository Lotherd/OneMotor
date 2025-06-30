# Main project __init__.py (root level)
"""
Enhanced Motorsport Dashboard Application

Complete F1 and MotoGP dashboard with real-time data, career statistics,
comprehensive session analysis, and professional user interface.

**Features:**
    - Complete F1 API integration (Jolpica/Ergast + OpenF1)
    - Real-time standings and race calendar
    - Comprehensive career statistics
    - All session types (Qualifying, Race, Sprint, Pit Stops, Lap History)
    - Professional dark theme with enhanced navigation
    - Multilingual support (English/Spanish)

**Version:** 3.0.0
**Author:** Lotherd
"""

import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Version information
__version__ = "3.0.0"
__title__ = "Enhanced Motorsport Dashboard"
__description__ = "Complete F1 and MotoGP dashboard with comprehensive data analysis"
__author__ = "Lotherd"

# Feature availability check
def check_system_status():
    """Check availability of all system components"""
    try:
        from services import get_available_features
        from ui.widgets import get_available_navigation_features  
        from models import get_available_model_features
        from utils import get_available_utility_features
        
        system_status = {
            'version': __version__,
            'services': get_available_features(),
            'navigation': get_available_navigation_features(),
            'models': get_available_model_features(),
            'utilities': get_available_utility_features(),
            'overall_status': 'READY'
        }
        
        # Check if enhanced features are available
        enhanced_available = (
            system_status['services'].get('enhanced_services', False) and
            system_status['navigation'].get('enhanced_navigation', False)
        )
        
        if enhanced_available:
            system_status['feature_level'] = 'COMPLETE'
            system_status['description'] = 'All enhanced features available'
        else:
            system_status['feature_level'] = 'BASIC'
            system_status['description'] = 'Basic features only (enhanced features disabled)'
            
        return system_status
        
    except Exception as e:
        return {
            'version': __version__,
            'overall_status': 'ERROR',
            'feature_level': 'UNKNOWN',
            'description': f'System check failed: {e}',
            'error': str(e)
        }

# Quick system check on import
_system_status = check_system_status()

# Export system information
__all__ = [
    '__version__',
    '__title__', 
    '__description__',
    '__author__',
    'check_system_status'
]

# Print system status (optional, for debugging)
if __name__ == "__main__":
    import json
    print("🏁 MOTORSPORT DASHBOARD SYSTEM STATUS")
    print("=" * 50)
    print(json.dumps(_system_status, indent=2))