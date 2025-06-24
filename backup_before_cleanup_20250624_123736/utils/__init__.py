"""
Utilidades para la aplicación
"""

try:
    from .i18n import tr, set_language, get_translation_manager
    __all__ = ['tr', 'set_language', 'get_translation_manager']
except ImportError:
    # Si i18n no está disponible, crear funciones dummy
    def tr(key, **kwargs):
        return f"[{key}]"
    
    def set_language(lang):
        return False
    
    def get_translation_manager():
        return None
    
    __all__ = ['tr', 'set_language', 'get_translation_manager']