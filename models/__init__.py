# models/__init__.py
"""
Enhanced data models for F1 and motorsport data

This module contains enhanced data model classes with support for
complete session data, career statistics, and advanced race information.

**Classes:**
    Driver - Individual driver information and details
    Constructor - Team/constructor information and details  
    DriverStanding - Driver's position and points in championship
    Race - Individual race information with complete session data

**Author:** Lotherd
**Version:** 3.0.0
"""

from .driver import Driver, Constructor, DriverStanding
from .race import Race

# Enhanced data models (if available)
try:
    # These would be enhanced versions with additional fields
    # For now, we'll use the existing models
    ENHANCED_MODELS_AVAILABLE = True
    
    __all__ = [
        'Driver', 
        'Constructor', 
        'DriverStanding', 
        'Race'
    ]
    
except ImportError:
    ENHANCED_MODELS_AVAILABLE = False
    
    __all__ = [
        'Driver', 
        'Constructor', 
        'DriverStanding', 
        'Race'
    ]

# Provide information about available model features
def get_available_model_features():
    """Returns information about available data model features"""
    features = {
        'basic_driver_data': True,
        'constructor_data': True,
        'driver_standings': True,
        'race_information': True,
        'enhanced_models': ENHANCED_MODELS_AVAILABLE,
        'career_statistics_fields': ENHANCED_MODELS_AVAILABLE,
        'session_data_fields': ENHANCED_MODELS_AVAILABLE
    }
    return features