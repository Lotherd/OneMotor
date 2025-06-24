# quick_fix.py
"""
Script de corrección rápida para problemas de importación
"""

import os
import sys
from pathlib import Path

def check_and_fix():
    """Verificar y corregir problemas comunes"""
    
    print("🔧 Verificando instalación...")
    
    # 1. Verificar estructura de directorios
    dirs_to_check = ["utils", "translations", "ui", "ui/widgets", "config", "services"]
    
    for dir_name in dirs_to_check:
        dir_path = Path(dir_name)
        if dir_path.exists():
            print(f"✅ {dir_name}/ existe")
        else:
            print(f"❌ {dir_name}/ NO existe - creando...")
            dir_path.mkdir(parents=True, exist_ok=True)
    
    # 2. Verificar archivos críticos
    files_to_check = [
        "utils/__init__.py",
        "config/settings.py",
        "ui/main_window.py",
        "ui/widgets/f1_tab.py",
        "ui/widgets/motogp_tab.py"
    ]
    
    for file_name in files_to_check:
        file_path = Path(file_name)
        if file_path.exists():
            print(f"✅ {file_name} existe")
        else:
            print(f"❌ {file_name} NO existe")
    
    # 3. Crear utils/__init__.py básico si no existe
    utils_init = Path("utils/__init__.py")
    if not utils_init.exists():
        utils_init.write_text("""# utils/__init__.py
try:
    from .i18n import tr, set_language, get_translation_manager
    __all__ = ['tr', 'set_language', 'get_translation_manager']
except ImportError:
    def tr(key, **kwargs):
        return f"[{key}]"
    def set_language(lang):
        return False
    def get_translation_manager():
        return None
    __all__ = ['tr', 'set_language', 'get_translation_manager']
""")
        print("✅ Creado utils/__init__.py básico")
    
    # 4. Probar importaciones básicas
    print("\n🧪 Probando importaciones...")
    
    try:
        from PyQt6.QtWidgets import QMainWindow
        print("✅ PyQt6.QtWidgets importa correctamente")
    except ImportError as e:
        print(f"❌ Error con PyQt6.QtWidgets: {e}")
    
    try:
        from PyQt6.QtGui import QActionGroup
        print("✅ QActionGroup importa correctamente desde QtGui")
    except ImportError as e:
        print(f"❌ Error con QActionGroup: {e}")
    
    try:
        from config.settings import AppConfig
        print("✅ AppConfig importa correctamente")
    except ImportError as e:
        print(f"❌ Error con AppConfig: {e}")
    
    # 5. Crear archivo i18n básico si no existe
    i18n_file = Path("utils/i18n.py")
    if not i18n_file.exists():
        print("❌ utils/i18n.py no existe")
        print("📋 Por favor, crea este archivo con el código del artifact 'Sistema de Internacionalización'")
    else:
        print("✅ utils/i18n.py existe")
    
    print("\n📋 Próximos pasos:")
    print("1. Copia el código de 'Ventana Principal con Importaciones Corregidas' a ui/main_window.py")
    print("2. Si no existe utils/i18n.py, créalo con el código del sistema I18n")
    print("3. Ejecuta: python main.py")

def create_minimal_i18n():
    """Crear un sistema i18n mínimo para testing"""
    
    i18n_file = Path("utils/i18n.py")
    if i18n_file.exists():
        print("✅ utils/i18n.py ya existe")
        return
    
    minimal_i18n = '''# utils/i18n.py - Versión mínima para testing
"""
Sistema de internacionalización mínimo
"""

class MinimalTranslationManager:
    def __init__(self):
        self.current_language = "es"
        self.translations = {
            "es": {
                "app_title": "F1 & MotoGP Dashboard - Versión {version}",
                "menu_file": "&Archivo",
                "menu_refresh": "&Actualizar Datos",
                "menu_refresh_tooltip": "Actualizar datos de la pestaña actual",
                "menu_exit": "&Salir",
                "menu_exit_tooltip": "Salir de la aplicación",
                "menu_view": "&Ver",
                "menu_f1": "Fórmula &1",
                "menu_f1_tooltip": "Cambiar a la pestaña de Fórmula 1",
                "menu_motogp": "&MotoGP",
                "menu_motogp_tooltip": "Cambiar a la pestaña de MotoGP",
                "menu_help": "&Ayuda",
                "menu_about": "&Acerca de",
                "menu_about_tooltip": "Información sobre la aplicación",
                "menu_language": "&Idioma",
                "tab_f1": "🏎️ Fórmula 1",
                "tab_motogp": "🏍️ MotoGP",
                "ready_to_load": "Aplicación iniciada - Listo para cargar datos",
                "language_changed": "Idioma cambiado",
                "restart_message": "Reinicia la aplicación para aplicar cambios",
                "f1_updating": "Actualizando datos de F1...",
                "f1_loading_initial": "Cargando datos iniciales de F1...",
                "motogp_dialog_title": "MotoGP",
                "motogp_info": "MotoGP en desarrollo",
                "confirm_exit": "Confirmar Salida",
                "confirm_exit_message": "¿Seguro que quieres salir?",
                "about_description": "Dashboard de F1 y MotoGP",
                "about_features": "Características:",
                "about_features_list": ["F1 Standings", "Calendario", "Noticias"],
                "about_apis": "APIs:",
                "about_apis_list": ["Ergast API", "News API"],
                "about_footer": "Hecho con Python y PyQt6",
                "tab_active": "Pestaña activa: {tab}"
            },
            "en": {
                "app_title": "F1 & MotoGP Dashboard - Version {version}",
                "menu_file": "&File",
                "menu_refresh": "&Refresh Data",
                "menu_refresh_tooltip": "Refresh current tab data",
                "menu_exit": "&Exit",
                "menu_exit_tooltip": "Exit application",
                "menu_view": "&View",
                "menu_f1": "Formula &1",
                "menu_f1_tooltip": "Switch to Formula 1 tab",
                "menu_motogp": "&MotoGP",
                "menu_motogp_tooltip": "Switch to MotoGP tab",
                "menu_help": "&Help",
                "menu_about": "&About",
                "menu_about_tooltip": "Application information",
                "menu_language": "&Language",
                "tab_f1": "🏎️ Formula 1",
                "tab_motogp": "🏍️ MotoGP",
                "ready_to_load": "Application started - Ready to load data",
                "language_changed": "Language changed",
                "restart_message": "Restart application to apply changes",
                "f1_updating": "Updating F1 data...",
                "f1_loading_initial": "Loading initial F1 data...",
                "motogp_dialog_title": "MotoGP",
                "motogp_info": "MotoGP under development",
                "confirm_exit": "Confirm Exit",
                "confirm_exit_message": "Are you sure you want to exit?",
                "about_description": "F1 and MotoGP Dashboard",
                "about_features": "Features:",
                "about_features_list": ["F1 Standings", "Calendar", "News"],
                "about_apis": "APIs:",
                "about_apis_list": ["Ergast API", "News API"],
                "about_footer": "Made with Python and PyQt6",
                "tab_active": "Active tab: {tab}"
            }
        }
    
    def set_language(self, lang):
        if lang in self.translations:
            self.current_language = lang
            return True
        return False
    
    def get_current_language(self):
        return self.current_language
    
    def get_available_languages(self):
        return {"es": "Español", "en": "English"}
    
    def tr(self, key, **kwargs):
        text = self.translations.get(self.current_language, {}).get(key, f"[{key}]")
        try:
            return text.format(**kwargs) if kwargs else text
        except:
            return text

# Instancia global
_manager = MinimalTranslationManager()

def tr(key, **kwargs):
    return _manager.tr(key, **kwargs)

def set_language(lang):
    return _manager.set_language(lang)

def get_translation_manager():
    return _manager
'''
    
    i18n_file.write_text(minimal_i18n, encoding='utf-8')
    print("✅ Creado utils/i18n.py mínimo para testing")

if __name__ == "__main__":
    print("🚀 Iniciando corrección rápida...\n")
    
    check_and_fix()
    
    print("\n🛠️ ¿Quieres crear un sistema i18n mínimo? (s/n): ", end="")
    if input().lower().startswith('s'):
        create_minimal_i18n()
    
    print("\n✅ Corrección completada!")
    print("Ahora ejecuta: python main.py")