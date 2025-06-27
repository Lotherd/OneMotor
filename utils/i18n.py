# utils/i18n.py
"""
Internationalization system for multi-language application support

This module provides comprehensive internationalization capabilities for the
motorsport dashboard application, including translation management, language
switching, and automatic translation file generation for supported languages.

**Classes:**
    TranslationManager - Main class for handling translations and language switching

**Functions:**
    tr - Convenience function for translating text keys
    set_language - Convenience function for changing application language
    get_translation_manager - Getter function for translation manager instance

**Author:** Motorsport Apps Team
**Version:** 1.0.0
"""

import os
import json
import logging
from typing import Dict, Any, Optional
from pathlib import Path
from PyQt6.QtCore import QObject, pyqtSignal

logger = logging.getLogger(__name__)

class TranslationManager(QObject):
    """Translation manager for handling multi-language support and text localization"""
    
    # Signal emitted when language changes
    language_changed = pyqtSignal(str)  # New language code
    
    """
    * Initializes the translation manager with default settings and file loading
    *
    * This constructor sets up the translation system with default language
    * settings, creates necessary directories, and loads all available
    * translation files for the application.
    *
    * **@return** None
    """
    def __init__(self):
        super().__init__()
        self.current_language = "en"  # Default language
        self.translations = {}
        self.fallback_language = "en"
        
        # Create translations directory if it doesn't exist
        self.translations_dir = Path("translations")
        self.translations_dir.mkdir(exist_ok=True)
        
        # Load translations
        self._load_all_translations()
        
    """
    * Loads all available translation files from the translations directory
    *
    * This method scans the translations directory for JSON files and loads
    * each one as a language translation set. If no files exist, it creates
    * default translation files for supported languages.
    *
    * **@return** None
    """
    def _load_all_translations(self):
        try:
            # Load translations from JSON files
            for lang_file in self.translations_dir.glob("*.json"):
                lang_code = lang_file.stem
                with open(lang_file, 'r', encoding='utf-8') as f:
                    self.translations[lang_code] = json.load(f)
                logger.info(f"Loaded translations for: {lang_code}")
            
            # If no files exist, create default translations
            if not self.translations:
                self._create_default_translations()
                
        except Exception as e:
            logger.error(f"Error loading translations: {e}")
            self._create_default_translations()
    
    """
    * Creates default translation files for English and Spanish if they don't exist
    *
    * This method generates comprehensive default translation dictionaries for
    * both English and Spanish languages, covering all UI elements, messages,
    * and user-facing text in the application.
    *
    * **@return** None
    """
    def _create_default_translations(self):
        logger.info("Creating default translations...")
        
        # Spanish translations
        spanish_translations = {
            # Main window
            "app_title": "F1 & MotoGP Dashboard - Versión {version}",
            "ready_to_load": "Aplicación iniciada - Listo para cargar datos",
            
            # Menus
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
            "menu_spanish": "&Español",
            "menu_english": "&English",
            
            # Tabs
            "tab_f1": "🏎️ Fórmula 1",
            "tab_motogp": "🏍️ MotoGP",
            "tab_active": "Pestaña activa: {tab}",
            
            # F1 Tab
            "f1_title": "🏎️ Fórmula 1 - Campeonato Mundial",
            "f1_refresh_button": "🔄 Actualizar Standings",
            "f1_export_button": "📊 Exportar Datos",
            "f1_season": "Temporada 2025",
            "f1_loading": "⏳ Cargando datos de F1...",
            "f1_loading_button": "🔄 Cargando...",
            "f1_ready": "Listo para cargar datos...",
            "f1_updating": "Actualizando datos de F1...",
            "f1_data_updated": "✅ Datos actualizados - {count} pilotos cargados",
            "f1_standings_updated": "F1 standings actualizados ({count} pilotos)",
            "f1_loading_initial": "Cargando datos iniciales de F1...",
            "f1_loading_standings": "Cargando standings de F1...",
            
            # F1 Table
            "table_pos": "POS",
            "table_driver": "PILOTO",
            "table_team": "EQUIPO", 
            "table_points": "PTS",
            "table_wins": "VICTORIAS",
            "table_nationality": "NACIONALIDAD",
            "table_code": "CÓDIGO",
            
            # MotoGP Tab
            "motogp_title": "🏍️ MotoGP - Próximamente",
            "motogp_development": "🚧 En Desarrollo",
            "motogp_description": "La sección de MotoGP está siendo desarrollada y incluirá:",
            "motogp_features": [
                "📊 Standings del Campeonato Mundial",
                "📅 Calendario de Carreras 2025",
                "🏁 Resultados de Carreras en Tiempo Real",
                "⏱️ Tiempos de Clasificación",
                "🏆 Estadísticas de Pilotos y Equipos",
                "📰 Noticias de MotoGP",
                "📈 Análisis de Rendimiento"
            ],
            "motogp_notify_title": "🔔 Mantente Informado",
            "motogp_notify_text": "Mientras desarrollamos la sección de MotoGP, puedes seguir disfrutando de todas las funcionalidades de Fórmula 1. Te notificaremos cuando MotoGP esté disponible.",
            "motogp_go_f1": "🏎️ Ir a Fórmula 1",
            "motogp_roadmap": "🗺️ Ver Roadmap",
            "motogp_info": "La sección de MotoGP está en desarrollo.\\nPróximamente disponible.",
            
            # Roadmap
            "roadmap_title": "🗺️ ROADMAP DE DESARROLLO",
            "roadmap_phase1": "📅 FASE 1 (Actual):",
            "roadmap_phase1_items": [
                "✅ Estructura base de la aplicación",
                "✅ Integración con Ergast API (F1)",
                "✅ Standings en tiempo real de F1"
            ],
            "roadmap_phase2": "📅 FASE 2 (Próxima):",
            "roadmap_phase2_items": [
                "🔲 Calendario de carreras F1",
                "🔲 Resultados históricos F1",
                "🔲 Noticias de motorsport"
            ],
            "roadmap_phase3": "📅 FASE 3 (Futuro):",
            "roadmap_phase3_items": [
                "🔲 API de MotoGP",
                "🔲 Standings de MotoGP",
                "🔲 Datos en tiempo real"
            ],
            "roadmap_phase4": "📅 FASE 4 (Avanzado):",
            "roadmap_phase4_items": [
                "🔲 Telemetría detallada",
                "🔲 Análisis de performance",
                "🔲 Predicciones con ML"
            ],
            
            # Dialogs
            "confirm_exit": "Confirmar Salida",
            "confirm_exit_message": "¿Estás seguro que quieres salir de la aplicación?",
            "error_title": "Error",
            "error_loading": "Error cargando datos:\\n{error}",
            "motogp_dialog_title": "MotoGP",
            
            # About
            "about_description": "Aplicación de escritorio para seguir Fórmula 1 y MotoGP",
            "about_features": "Características:",
            "about_features_list": [
                "📊 Standings en tiempo real de F1",
                "📅 Calendario de carreras",
                "📰 Noticias de motorsport",
                "📈 Análisis de datos (próximamente)",
                "🏍️ MotoGP (en desarrollo)"
            ],
            "about_apis": "APIs utilizadas:",
            "about_apis_list": [
                "Ergast API: Datos históricos y standings de F1",
                "News API: Noticias de motorsport"
            ],
            "about_footer": "Desarrollado con Python y PyQt6",
            
            # States and errors
            "connection_error": "Error de conexión: {error}",
            "parsing_error": "Error procesando datos: {error}",
            "unexpected_error": "Error inesperado: {error}",
            "show_error_data": "Error mostrando datos: {error}",
            
            # Settings
            "language_changed": "Idioma cambiado a Español",
            "restart_required": "Reinicio Requerido",
            "restart_message": "Algunos cambios requieren reiniciar la aplicación.\\n¿Deseas reiniciar ahora?"
        }
        
        # English translations
        english_translations = {
            # Main window
            "app_title": "F1 & MotoGP Dashboard - Version {version}",
            "ready_to_load": "Application started - Ready to load data",
            
            # Menus
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
            "menu_spanish": "&Español",
            "menu_english": "&English",
            
            # Tabs
            "tab_f1": "🏎️ Formula 1",
            "tab_motogp": "🏍️ MotoGP",
            "tab_active": "Active tab: {tab}",
            
            # F1 Tab
            "f1_title": "🏎️ Formula 1 - World Championship",
            "f1_refresh_button": "🔄 Refresh Standings",
            "f1_export_button": "📊 Export Data",
            "f1_season": "Season 2025",
            "f1_loading": "⏳ Loading F1 data...",
            "f1_loading_button": "🔄 Loading...",
            "f1_ready": "Ready to load data...",
            "f1_updating": "Updating F1 data...",
            "f1_data_updated": "✅ Data updated - {count} drivers loaded",
            "f1_standings_updated": "F1 standings updated ({count} drivers)",
            "f1_loading_initial": "Loading initial F1 data...",
            "f1_loading_standings": "Loading F1 standings...",
            
            # F1 Table
            "table_pos": "POS",
            "table_driver": "DRIVER",
            "table_team": "TEAM",
            "table_points": "PTS",
            "table_wins": "WINS",
            "table_nationality": "NATIONALITY",
            "table_code": "CODE",
            
            # MotoGP Tab
            "motogp_title": "🏍️ MotoGP - Coming Soon",
            "motogp_development": "🚧 In Development",
            "motogp_description": "The MotoGP section is being developed and will include:",
            "motogp_features": [
                "📊 World Championship Standings",
                "📅 2025 Race Calendar",
                "🏁 Real-time Race Results",
                "⏱️ Qualifying Times",
                "🏆 Driver and Team Statistics",
                "📰 MotoGP News",
                "📈 Performance Analysis"
            ],
            "motogp_notify_title": "🔔 Stay Informed",
            "motogp_notify_text": "While we develop the MotoGP section, you can continue enjoying all Formula 1 features. We'll notify you when MotoGP becomes available.",
            "motogp_go_f1": "🏎️ Go to Formula 1",
            "motogp_roadmap": "🗺️ View Roadmap",
            "motogp_info": "MotoGP section is under development.\\nComing soon.",
            
            # Roadmap
            "roadmap_title": "🗺️ DEVELOPMENT ROADMAP",
            "roadmap_phase1": "📅 PHASE 1 (Current):",
            "roadmap_phase1_items": [
                "✅ Application base structure",
                "✅ Ergast API integration (F1)",
                "✅ Real-time F1 standings"
            ],
            "roadmap_phase2": "📅 PHASE 2 (Next):",
            "roadmap_phase2_items": [
                "🔲 F1 race calendar",
                "🔲 F1 historical results",
                "🔲 Motorsport news"
            ],
            "roadmap_phase3": "📅 PHASE 3 (Future):",
            "roadmap_phase3_items": [
                "🔲 MotoGP API",
                "🔲 MotoGP standings",
                "🔲 Real-time data"
            ],
            "roadmap_phase4": "📅 PHASE 4 (Advanced):",
            "roadmap_phase4_items": [
                "🔲 Detailed telemetry",
                "🔲 Performance analysis",
                "🔲 ML predictions"
            ],
            
            # Dialogs
            "confirm_exit": "Confirm Exit",
            "confirm_exit_message": "Are you sure you want to exit the application?",
            "error_title": "Error",
            "error_loading": "Error loading data:\\n{error}",
            "motogp_dialog_title": "MotoGP",
            
            # About
            "about_description": "Desktop application for following Formula 1 and MotoGP",
            "about_features": "Features:",
            "about_features_list": [
                "📊 Real-time F1 standings",
                "📅 Race calendar",
                "📰 Motorsport news",
                "📈 Data analysis (coming soon)",
                "🏍️ MotoGP (in development)"
            ],
            "about_apis": "APIs used:",
            "about_apis_list": [
                "Ergast API: Historical data and F1 standings",
                "News API: Motorsport news"
            ],
            "about_footer": "Developed with Python and PyQt6",
            
            # States and errors
            "connection_error": "Connection error: {error}",
            "parsing_error": "Data processing error: {error}",
            "unexpected_error": "Unexpected error: {error}",
            "show_error_data": "Error displaying data: {error}",
            
            # Settings
            "language_changed": "Language changed to English",
            "restart_required": "Restart Required",
            "restart_message": "Some changes require restarting the application.\\nDo you want to restart now?"
        }
        
        # Save translations
        self.translations = {
            "es": spanish_translations,
            "en": english_translations
        }
        
        # Create JSON files
        for lang_code, translations in self.translations.items():
            file_path = self.translations_dir / f"{lang_code}.json"
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(translations, f, ensure_ascii=False, indent=2)
            logger.info(f"Created translation file: {file_path}")
    
    """
    * Changes the active language and emits language change signal
    *
    * This method updates the current language setting if the requested
    * language is available in the loaded translations and emits a signal
    * to notify other components of the language change.
    *
    * **@param** language_code String language code to switch to
    * **@return** Boolean True if language change successful, False otherwise
    """
    def set_language(self, language_code: str) -> bool:
        if language_code in self.translations:
            old_language = self.current_language
            self.current_language = language_code
            logger.info(f"Language changed from {old_language} to {language_code}")
            self.language_changed.emit(language_code)
            return True
        else:
            logger.warning(f"Language {language_code} not available")
            return False
    
    """
    * Returns a dictionary of available languages with display names
    *
    * This method provides a mapping of language codes to their display
    * names for use in language selection interfaces and menus.
    *
    * **@return** Dictionary mapping language codes to display names
    """
    def get_available_languages(self) -> Dict[str, str]:
        return {
            "es": "Español",
            "en": "English"
        }
    
    """
    * Translates a text key to the current language with parameter substitution
    *
    * This method looks up the translation for a given key in the current
    * language, falls back to the default language if not found, and supports
    * parameter substitution for dynamic text generation.
    *
    * **@param** key String translation key to look up
    * **@param** kwargs Additional keyword arguments for text formatting
    * **@return** String translated text or key in brackets if not found
    """
    def tr(self, key: str, **kwargs) -> str:
        # Try to get from current language
        translations = self.translations.get(self.current_language, {})
        text = translations.get(key)
        
        # If not found, try fallback language
        if text is None:
            fallback_translations = self.translations.get(self.fallback_language, {})
            text = fallback_translations.get(key)
        
        # If still not found, return the key
        if text is None:
            logger.warning(f"Translation not found for key: {key}")
            return f"[{key}]"
        
        # Format with arguments if any
        try:
            if kwargs:
                return text.format(**kwargs)
            return text
        except KeyError as e:
            logger.error(f"Error formatting translation '{key}': {e}")
            return text
    
    """
    * Returns the currently active language code
    *
    * This method provides access to the current language setting for
    * components that need to know which language is currently active
    * for conditional behavior or display purposes.
    *
    * **@return** String current language code
    """
    def get_current_language(self) -> str:
        return self.current_language


# Global translation manager instance
_translation_manager = TranslationManager()

"""
* Convenience function for translating text keys with the global manager
*
* This function provides easy access to translation functionality without
* requiring direct access to the translation manager instance, supporting
* parameter substitution for dynamic text generation.
*
* **@param** key String translation key to translate
* **@param** kwargs Additional keyword arguments for text formatting
* **@return** String translated text
"""
def tr(key: str, **kwargs) -> str:
    return _translation_manager.tr(key, **kwargs)

"""
* Convenience function for changing language with the global manager
*
* This function provides easy access to language switching functionality
* without requiring direct access to the translation manager instance.
*
* **@param** language_code String language code to switch to
* **@return** Boolean True if language change successful, False otherwise
"""
def set_language(language_code: str) -> bool:
    return _translation_manager.set_language(language_code)

"""
* Returns the global translation manager instance
*
* This function provides access to the global translation manager for
* components that need direct access to advanced translation features
* like signal connections or language availability checking.
*
* **@return** TranslationManager global translation manager instance
"""
def get_translation_manager() -> TranslationManager:
    return _translation_manager