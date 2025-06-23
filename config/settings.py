# config/settings.py
"""
Configuración global de la aplicación
"""

class AppConfig:
    """Configuración principal de la app"""
    
    # Información de la app
    APP_NAME = "F1 & MotoGP Dashboard"
    APP_VERSION = "1.1"  # Incrementamos versión
    WINDOW_TITLE = f"{APP_NAME} - Version {APP_VERSION}"
    
    # Dimensiones de ventana
    WINDOW_WIDTH = 1000
    WINDOW_HEIGHT = 700
    WINDOW_MIN_WIDTH = 800
    WINDOW_MIN_HEIGHT = 600
    
    # URLs de APIs - ACTUALIZADO PARA USAR JOLPICA
    # Ergast API ha sido descontinuado desde 2025
    # Jolpica es el reemplazo oficial con endpoints compatibles
    ERGAST_BASE_URL = "http://api.jolpi.ca/ergast/f1"  # ← CAMBIO PRINCIPAL
    
    # URLs alternativas en caso de problemas
    BACKUP_APIS = {
        "jolpica_https": "https://api.jolpi.ca/ergast/f1",
        "jolpica_http": "http://api.jolpi.ca/ergast/f1"
    }
    
    # Configuración de requests
    REQUEST_TIMEOUT = 30
    MAX_RETRIES = 3
    
    # Rate limiting para Jolpica (200 requests/hora sin autenticación)
    RATE_LIMIT_REQUESTS = 200
    RATE_LIMIT_WINDOW = 3600  # 1 hora en segundos
    
    # Configuración de UI
    TABLE_REFRESH_INTERVAL = 300000  # 5 minutos en ms
    
    # Colores del tema
    COLORS = {
        'f1_red': '#e10600',
        'f1_red_hover': '#c50500',
        'motogp_orange': '#ff8c00',
        'background': '#f8f8f8',
        'text_primary': '#333333',
        'text_secondary': '#666666',
        'border': '#d0d0d0',
        'white': '#ffffff',
        'success': '#28a745',
        'error': '#dc3545',
        'warning': '#ffc107'
    }
    
    # Configuración de logging
    LOG_LEVEL = "INFO"
    LOG_FILE = "app.log"