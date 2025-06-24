# utils/i18n.py
"""
Sistema de internacionalización para la aplicación
"""

import os
import json
import logging
from typing import Dict, Any, Optional
from pathlib import Path
from PyQt6.QtCore import QObject, pyqtSignal

logger = logging.getLogger(__name__)

class TranslationManager(QObject):
    """Gestor de traducciones para la aplicación"""
    
    # Señal emitida cuando cambia el idioma
    language_changed = pyqtSignal(str)  # Nuevo código de idioma
    
    def __init__(self):
        super().__init__()
        self.current_language = "es"  # Idioma por defecto
        self.translations = {}
        self.fallback_language = "en"
        
        # Crear directorio de traducciones si no existe
        self.translations_dir = Path("translations")
        self.translations_dir.mkdir(exist_ok=True)
        
        # Cargar traducciones
        self._load_all_translations()
        
    def _load_all_translations(self):
        """Cargar todas las traducciones disponibles"""
        try:
            # Cargar traducciones desde archivos JSON
            for lang_file in self.translations_dir.glob("*.json"):
                lang_code = lang_file.stem
                with open(lang_file, 'r', encoding='utf-8') as f:
                    self.translations[lang_code] = json.load(f)
                logger.info(f"Loaded translations for: {lang_code}")
            
            # Si no hay archivos, crear traducciones por defecto
            if not self.translations:
                self._create_default_translations()
                
        except Exception as e:
            logger.error(f"Error loading translations: {e}")
            self._create_default_translations()
    
    def _create_default_translations(self):
        """Crear traducciones por defecto si no existen"""
        logger.info("Creating default translations...")
        
        # Traducciones en español
        spanish_translations = {
            # Ventana principal
            "app_title": "F1 & MotoGP Dashboard - Versión {version}",
            "ready_to_load": "Aplicación iniciada - Listo para cargar datos",
            
            # Menús
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
            
            # Pestañas
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
            
            # Tabla F1
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
            
            # Diálogos
            "confirm_exit": "Confirmar Salida",
            "confirm_exit_message": "¿Estás seguro que quieres salir de la aplicación?",
            "error_title": "Error",
            "error_loading": "Error cargando datos:\\n{error}",
            "motogp_dialog_title": "MotoGP",
            
            # Acerca de
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
            
            # Estados y errores
            "connection_error": "Error de conexión: {error}",
            "parsing_error": "Error procesando datos: {error}",
            "unexpected_error": "Error inesperado: {error}",
            "show_error_data": "Error mostrando datos: {error}",
            
            # Configuración
            "language_changed": "Idioma cambiado a Español",
            "restart_required": "Reinicio Requerido",
            "restart_message": "Algunos cambios requieren reiniciar la aplicación.\\n¿Deseas reiniciar ahora?"
        }
        
        # Traducciones en inglés
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
        
        # Guardar traducciones
        self.translations = {
            "es": spanish_translations,
            "en": english_translations
        }
        
        # Crear archivos JSON
        for lang_code, translations in self.translations.items():
            file_path = self.translations_dir / f"{lang_code}.json"
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(translations, f, ensure_ascii=False, indent=2)
            logger.info(f"Created translation file: {file_path}")
    
    def set_language(self, language_code: str) -> bool:
        """Cambiar idioma activo"""
        if language_code in self.translations:
            old_language = self.current_language
            self.current_language = language_code
            logger.info(f"Language changed from {old_language} to {language_code}")
            self.language_changed.emit(language_code)
            return True
        else:
            logger.warning(f"Language {language_code} not available")
            return False
    
    def get_available_languages(self) -> Dict[str, str]:
        """Obtener idiomas disponibles"""
        return {
            "es": "Español",
            "en": "English"
        }
    
    def tr(self, key: str, **kwargs) -> str:
        """Traducir una clave"""
        # Intentar obtener de idioma actual
        translations = self.translations.get(self.current_language, {})
        text = translations.get(key)
        
        # Si no existe, intentar con idioma de respaldo
        if text is None:
            fallback_translations = self.translations.get(self.fallback_language, {})
            text = fallback_translations.get(key)
        
        # Si aún no existe, devolver la clave
        if text is None:
            logger.warning(f"Translation not found for key: {key}")
            return f"[{key}]"
        
        # Formatear con argumentos si los hay
        try:
            if kwargs:
                return text.format(**kwargs)
            return text
        except KeyError as e:
            logger.error(f"Error formatting translation '{key}': {e}")
            return text
    
    def get_current_language(self) -> str:
        """Obtener idioma actual"""
        return self.current_language


# Instancia global del gestor de traducciones
_translation_manager = TranslationManager()

def tr(key: str, **kwargs) -> str:
    """Función de conveniencia para traducir"""
    return _translation_manager.tr(key, **kwargs)

def set_language(language_code: str) -> bool:
    """Función de conveniencia para cambiar idioma"""
    return _translation_manager.set_language(language_code)

def get_translation_manager() -> TranslationManager:
    """Obtener instancia del gestor de traducciones"""
    return _translation_manager