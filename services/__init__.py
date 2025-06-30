# services/__init__.py
"""
Enhanced services package for motorsport dashboard application

This package contains all service classes for data retrieval, API communication,
and background processing including the complete F1 API integration with
OpenF1 support and comprehensive session data loading.

**Modules:**
    api_client - HTTP client classes for API communication with fallback support
    data_service - Main data service for F1 standings and calendar
    enhanced_data_service - Complete service with all session types and OpenF1

**Author:** Lotherd
**Version:** 3.0.0
"""

from .api_client import ErgastAPIClient, NewsAPIClient, APIException
from .data_service import DataService, DataLoader, CalendarLoader, DataParsingException

# Import enhanced services with error handling
try:
    from .enhanced_data_service import (
        EnhancedDataService, 
        CompleteSessionDataLoader, 
        CareerStatsLoader,
        OpenF1Client
    )
    ENHANCED_AVAILABLE = True
    
    # Define complete export list
    __all__ = [
        # API Clients
        'ErgastAPIClient', 
        'NewsAPIClient', 
        'APIException',
        
        # Basic Data Services
        'DataService', 
        'DataLoader', 
        'CalendarLoader',
        'DataParsingException',
        
        # Enhanced Services (Complete F1 Integration)
        'EnhancedDataService',
        'CompleteSessionDataLoader',
        'CareerStatsLoader',
        'OpenF1Client'
    ]
    
except ImportError as e:
    # Fallback if enhanced service dependencies are not available
    import logging
    logger = logging.getLogger(__name__)
    logger.warning(f"Enhanced services not available: {e}")
    
    # Create fallback classes to prevent import errors
    class EnhancedDataService:
        def __init__(self):
            raise NotImplementedError("Enhanced services not available. Install required dependencies.")
    
    class CompleteSessionDataLoader:
        def __init__(self, *args, **kwargs):
            raise NotImplementedError("Enhanced session loader not available.")
    
    class CareerStatsLoader:
        def __init__(self, *args, **kwargs):
            raise NotImplementedError("Career stats loader not available.")
    
    class OpenF1Client:
        def __init__(self):
            raise NotImplementedError("OpenF1 client not available.")
    
    ENHANCED_AVAILABLE = False
    
    # Basic export list without enhanced services
    __all__ = [
        # API Clients
        'ErgastAPIClient', 
        'NewsAPIClient', 
        'APIException',
        
        # Basic Data Services
        'DataService', 
        'DataLoader', 
        'CalendarLoader',
        'DataParsingException'
    ]

# Provide information about available features
def get_available_features():
    """Returns information about available service features"""
    features = {
        'basic_f1_data': True,
        'enhanced_services': ENHANCED_AVAILABLE,
        'openf1_integration': ENHANCED_AVAILABLE,
        'career_statistics': ENHANCED_AVAILABLE,
        'complete_session_data': ENHANCED_AVAILABLE,
        'pit_stops_data': ENHANCED_AVAILABLE,
        'lap_history_data': ENHANCED_AVAILABLE
    }
    return features