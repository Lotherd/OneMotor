# ui/__init__.py
"""
UI package for motorsport dashboard application

This package contains all user interface components including the main window,
widgets, styles, and navigation components.

**Modules:**
    main_window - Main application window
    widgets - F1 and MotoGP widget components
    styles - CSS styling definitions

**Author:** Lotherd
**Version:** 2.0.0
"""

from .main_window import MainWindow

# Import widgets
try:
    from .widgets import F1TabWidget, MotoGPTabWidget
    WIDGETS_AVAILABLE = True
except ImportError:
    F1TabWidget = None
    MotoGPTabWidget = None
    WIDGETS_AVAILABLE = False

# Define what gets imported with "from ui import *"
if WIDGETS_AVAILABLE:
    __all__ = [
        'MainWindow',
        'F1TabWidget', 
        'MotoGPTabWidget'
    ]
else:
    __all__ = ['MainWindow']