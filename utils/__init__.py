# utils/__init__.py
"""
Enhanced utilities for the motorsport dashboard application

This package contains utility functions for internationalization,
image processing, and other helper functions with enhanced features.

**Modules:**
    i18n - Internationalization system with enhanced language support
    image_utils - High-quality image processing utilities

**Author:** Lotherd
**Version:** 3.0.0
"""

try:
    from .i18n import tr, set_language, get_translation_manager
    from .image_utils import ImageUtils
    
    UTILS_AVAILABLE = True
    
    __all__ = [
        'tr', 
        'set_language', 
        'get_translation_manager',
        'ImageUtils'
    ]
    
except ImportError as e:
    # Create fallback functions to prevent application crashes
    import logging
    logger = logging.getLogger(__name__)
    logger.warning(f"Some utilities not available: {e}")
    
    # Fallback translation functions
    def tr(key, **kwargs):
        """Fallback translation function"""
        return f"[{key}]"
    
    def set_language(lang):
        """Fallback language setter"""
        return False
    
    def get_translation_manager():
        """Fallback translation manager"""
        return None
    
    # Fallback image utils
    class ImageUtils:
        @staticmethod
        def load_high_quality_pixmap(*args, **kwargs):
            """Fallback image loader"""
            return None
        
        @staticmethod
        def create_fallback_logo(*args, **kwargs):
            """Fallback logo creator"""
            return None
    
    UTILS_AVAILABLE = False
    
    __all__ = [
        'tr', 
        'set_language', 
        'get_translation_manager',
        'ImageUtils'
    ]

# Provide information about available utility features
def get_available_utility_features():
    """Returns information about available utility features"""
    features = {
        'internationalization': UTILS_AVAILABLE,
        'image_processing': UTILS_AVAILABLE,
        'high_quality_rendering': UTILS_AVAILABLE,
        'fallback_translations': True,
        'fallback_image_utils': True
    }
    return features