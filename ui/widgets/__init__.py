# ui/widgets/__init__.py
"""
UI widgets package for motorsport dashboard application

This package contains all widget classes for the user interface including
F1 and MotoGP tabs, navigation components, and specialized widgets.

**Modules:**
    f1_tab - Main F1 widget with integrated navigation
    f1_navigation - Navigation components for driver info and race results
    motogp_tab - MotoGP widget (in development)

**Author:** Lotherd
**Version:** 2.0.0
"""

# Import main widgets
from .f1_tab import F1TabWidget
from .motogp_tab import MotoGPTabWidget

# Try to import navigation components (imported as needed to avoid circular imports)
try:
    from .f1_navigation import (
        NavigationTabWidget, 
        DriverInfoTab, 
        RaceResultsTab, 
        SessionResultsTable,
        DarkTabWidget
    )
    NAVIGATION_AVAILABLE = True
except ImportError:
    # Fallback if navigation components are not available
    NavigationTabWidget = None
    DriverInfoTab = None
    RaceResultsTab = None
    SessionResultsTable = None
    DarkTabWidget = None
    NAVIGATION_AVAILABLE = False

# Define what gets imported with "from ui.widgets import *"
if NAVIGATION_AVAILABLE:
    __all__ = [
        # Main widgets
        'F1TabWidget', 
        'MotoGPTabWidget',
        
        # Navigation components
        'NavigationTabWidget',
        'DriverInfoTab',
        'RaceResultsTab',
        'SessionResultsTable',
        'DarkTabWidget'
    ]
else:
    # Fallback if navigation components are not available
    __all__ = [
        'F1TabWidget', 
        'MotoGPTabWidget'
    ]