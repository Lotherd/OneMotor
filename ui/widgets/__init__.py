# ui/widgets/__init__.py
"""
Enhanced UI widgets package for motorsport dashboard application

This package contains all widget classes for the user interface including
enhanced F1 and MotoGP tabs, complete navigation components, and specialized
widgets for session data display.

**Modules:**
    f1_tab - Enhanced F1 widget with complete navigation integration
    f1_navigation - Complete navigation components with all session types
    motogp_tab - MotoGP widget (in development)

**Author:** Lotherd  
**Version:** 3.0.0
"""

# Import main widgets
from .f1_tab import F1TabWidget
from .motogp_tab import MotoGPTabWidget

# Try to import enhanced navigation components
try:
    from .f1_navigation import (
        NavigationTabWidget,
        EnhancedDriverInfoTab,
        CompleteRaceResultsTab,
        PitStopsTab,
        LapHistoryTab,
        SessionResultsTable,
        DarkTabWidget
    )
    ENHANCED_NAVIGATION_AVAILABLE = True
    
    # Complete export list with enhanced navigation
    __all__ = [
        # Main widgets
        'F1TabWidget', 
        'MotoGPTabWidget',
        
        # Enhanced navigation components
        'NavigationTabWidget',
        'EnhancedDriverInfoTab',
        'CompleteRaceResultsTab',
        'PitStopsTab',
        'LapHistoryTab',
        'SessionResultsTable',
        'DarkTabWidget'
    ]
    
except ImportError as e:
    # Fallback if enhanced navigation components are not available
    import logging
    logger = logging.getLogger(__name__)
    logger.warning(f"Enhanced navigation components not available: {e}")
    
    # Create fallback classes
    class NavigationTabWidget:
        def __init__(self, *args, **kwargs):
            raise NotImplementedError("Enhanced navigation not available.")
    
    class EnhancedDriverInfoTab:
        def __init__(self, *args, **kwargs):
            raise NotImplementedError("Enhanced driver info not available.")
    
    class CompleteRaceResultsTab:
        def __init__(self, *args, **kwargs):
            raise NotImplementedError("Complete race results not available.")
    
    class PitStopsTab:
        def __init__(self, *args, **kwargs):
            raise NotImplementedError("Pit stops tab not available.")
    
    class LapHistoryTab:
        def __init__(self, *args, **kwargs):
            raise NotImplementedError("Lap history tab not available.")
    
    class SessionResultsTable:
        def __init__(self, *args, **kwargs):
            raise NotImplementedError("Session results table not available.")
    
    class DarkTabWidget:
        def __init__(self, *args, **kwargs):
            from PyQt6.QtWidgets import QTabWidget
            return QTabWidget()  # Fallback to basic tab widget
    
    ENHANCED_NAVIGATION_AVAILABLE = False
    
    # Basic export list without enhanced navigation
    __all__ = [
        'F1TabWidget', 
        'MotoGPTabWidget'
    ]

# Provide information about available navigation features
def get_available_navigation_features():
    """Returns information about available navigation features"""
    features = {
        'basic_f1_tabs': True,
        'motogp_tabs': True,
        'enhanced_navigation': ENHANCED_NAVIGATION_AVAILABLE,
        'driver_career_stats': ENHANCED_NAVIGATION_AVAILABLE,
        'complete_race_sessions': ENHANCED_NAVIGATION_AVAILABLE,
        'pit_stops_analysis': ENHANCED_NAVIGATION_AVAILABLE,
        'lap_history_analysis': ENHANCED_NAVIGATION_AVAILABLE,
        'integrated_back_navigation': ENHANCED_NAVIGATION_AVAILABLE
    }
    return features