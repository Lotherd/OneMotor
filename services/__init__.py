# services/__init__.py
"""
Services package for motorsport dashboard application

This package contains all service classes for data retrieval, API communication,
and background processing for the motorsport dashboard.

**Modules:**
    api_client - HTTP client classes for API communication
    data_service - Main data service for F1 standings and calendar
    enhanced_data_service - Extended service with full session support

**Author:** Lotherd
**Version:** 2.0.0
"""

from .api_client import ErgastAPIClient, NewsAPIClient, APIException
from .data_service import DataService, DataLoader, CalendarLoader, DataParsingException

# Import enhanced services
try:
    from .enhanced_data_service import EnhancedDataService, SessionDataLoader
    ENHANCED_AVAILABLE = True
except ImportError:
    # Fallback if enhanced service is not available
    EnhancedDataService = None
    SessionDataLoader = None
    ENHANCED_AVAILABLE = False

# Define what gets imported with "from services import *"
if ENHANCED_AVAILABLE:
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
        
        # Enhanced Services
        'EnhancedDataService',
        'SessionDataLoader'
    ]
else:
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