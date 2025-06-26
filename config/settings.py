# config/settings.py
"""
Enhanced application configuration with high-quality rendering settings
"""

import os
import json
from pathlib import Path
from typing import Dict, Any

class AppConfig:
    """Enhanced application configuration"""
    
    # Application Info
    APP_NAME = "Motorsport Dashboard"  
    APP_VERSION = "1.0.0"
    ORGANIZATION_NAME = "MotorsportApps"
    
    # API Configuration - Updated for 2025
    ERGAST_BASE_URL = "http://api.jolpi.ca/ergast/f1"  # Updated working endpoint
    REQUEST_TIMEOUT = 15  # Increased timeout
    
    # Working F1 API Endpoints for 2025
    F1_API_ENDPOINTS = [
        "http://api.jolpi.ca/ergast/f1",      # Jolpica F1 (primary)
        "https://api.jolpi.ca/ergast/f1",     # Jolpica F1 HTTPS
        "https://openf1.org/v1"               # OpenF1 alternative
    ]
    
    # Legacy backup APIs (likely not working)
    BACKUP_APIS = {
        "jolpica_http": "http://api.jolpi.ca/ergast/f1",
        "jolpica_https": "https://api.jolpi.ca/ergast/f1",
        "openf1": "https://openf1.org/v1"
    }
    
    # UI Colors
    COLORS = {
        # F1 Theme
        'f1_red': '#e10600',
        'f1_red_hover': '#ff1a0a',
        'f1_red_dark': '#b30500',
        
        # MotoGP Theme (Blue)
        'motogp_blue': '#0066cc',
        'motogp_blue_hover': '#3388ff',
        'motogp_blue_dark': '#004499',
        
        # General UI
        'white': '#ffffff',
        'black': '#000000',
        'background': '#f8f9fa',
        'text_primary': '#333333',
        'text_secondary': '#666666',
        'border': '#e0e0e0',
        'success': '#28a745',
        'error': '#dc3545',
        'warning': '#ffc107'
    }
    
    # High-Quality Rendering Settings
    RENDERING = {
        'high_dpi_scaling': True,
        'antialiasing': True,
        'smooth_pixmap_transform': True,
        'text_antialiasing': True,
        'logo_quality': 'high',  # 'high', 'medium', 'low'
        'device_pixel_ratio_auto': True
    }
    
    # Logo Configuration
    LOGO_CONFIG = {
        'f1_logo_path': 'logo/f1_logo.png',
        'motogp_logo_path': 'logo/motogp_logo.png',
        'logo_container_size': (400, 180),  # Width, Height
        'logo_max_size': (360, 140),  # Max logo size within container
        'logo_background_blur': 15,
        'logo_border_radius': 25,
        'logo_border_width': 3
    }
    
    # Card Configuration
    CARD_CONFIG = {
         # Larger sizing for a more prominent look
        'card_size': (600, 780),  # Width, Height
        'card_border_radius': 40,
        'card_border_width': 3,
        'card_shadow_blur': 40,
        'card_shadow_offset': (0, 12),  # X, Y
        'card_hover_shadow_blur': 50,
        'card_hover_shadow_offset': (0, 18),
        'card_spacing': 100,  # Space between cards
        'card_margins': (90, 90, 90, 90)  # Top, Right, Bottom, Left
    }
    
    # Window Configuration
    WINDOW_CONFIG = {
        'default_size': (1600, 1000),
        'minimum_size': (1400, 900),
        'header_height': 100,
        'home_margins': (80, 80, 80, 80),
        'home_spacing': 60
    }
    
    # Font Configuration
    FONTS = {
        'title_size': 68,
        'subtitle_size': 22,
        'card_title_size': 38,
        'card_subtitle_size': 20,
        'header_title_size': 42,
        'button_size': 14,
        'table_size': 14,
        'menu_size': 14
    }
    
    # Data Configuration
    DATA_CONFIG = {
        'auto_refresh_interval': 300,  # 5 minutes
        'max_retries': 3,
        'cache_duration': 60,  # 1 minute
        'default_season': '2025'
    }
    
    # Settings file path
    SETTINGS_FILE = Path("settings.json")
    
    # Default language
    DEFAULT_LANGUAGE = "en"
    
    @classmethod
    def get_language(cls) -> str:
        """Get saved language preference"""
        try:
            if cls.SETTINGS_FILE.exists():
                with open(cls.SETTINGS_FILE, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                    return settings.get('language', cls.DEFAULT_LANGUAGE)
        except Exception:
            pass
        return cls.DEFAULT_LANGUAGE
    
    @classmethod
    def set_language(cls, language_code: str):
        """Save language preference"""
        try:
            settings = {}
            if cls.SETTINGS_FILE.exists():
                with open(cls.SETTINGS_FILE, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
            
            settings['language'] = language_code
            
            with open(cls.SETTINGS_FILE, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=2)
        except Exception as e:
            print(f"Error saving language setting: {e}")
    
    @classmethod
    def get_logo_path(cls, series_type: str) -> str:
        """Get logo path for specific series"""
        if series_type == "f1":
            return cls.LOGO_CONFIG['f1_logo_path']
        elif series_type == "motogp":
            return cls.LOGO_CONFIG['motogp_logo_path']
        else:
            return ""
    
    @classmethod
    def get_card_size(cls) -> tuple:
        """Get card size configuration"""
        return cls.CARD_CONFIG['card_size']
    
    @classmethod
    def get_logo_container_size(cls) -> tuple:
        """Get logo container size"""
        return cls.LOGO_CONFIG['logo_container_size']
    
    @classmethod
    def get_logo_max_size(cls) -> tuple:
        """Get maximum logo size"""
        return cls.LOGO_CONFIG['logo_max_size']
    
    @classmethod
    def is_high_quality_rendering(cls) -> bool:
        """Check if high quality rendering is enabled"""
        return cls.RENDERING['logo_quality'] == 'high'
    
    @classmethod
    def get_window_config(cls) -> Dict[str, Any]:
        """Get window configuration"""
        return cls.WINDOW_CONFIG
    
    @classmethod
    def get_font_config(cls) -> Dict[str, int]:
        """Get font configuration"""
        return cls.FONTS