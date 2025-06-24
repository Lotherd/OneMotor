# update_app.py
"""
Script de actualización automática para migrar de Ergast a Jolpica API
"""

import os
import shutil
import sys
from datetime import datetime
from pathlib import Path

def backup_files():
    """Crear backup de archivos importantes"""
    print("📁 Creando backup de archivos...")
    
    backup_dir = Path(f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
    backup_dir.mkdir(exist_ok=True)
    
    files_to_backup = [
        "config/settings.py",
        "services/api_client.py"
    ]
    
    for file_path in files_to_backup:
        if Path(file_path).exists():
            dest = backup_dir / file_path
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(file_path, dest)
            print(f"   ✅ {file_path} -> {dest}")
    
    print(f"✅ Backup creado en: {backup_dir}")
    return backup_dir

def update_config():
    """Actualizar archivo de configuración"""
    print("⚙️  Actualizando configuración...")
    
    config_content = '''"""
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
    LOG_FILE = "app.log"'''
    
    with open("config/settings.py", "w", encoding="utf-8") as f:
        f.write(config_content)
    
    print("   ✅ config/settings.py actualizado")

def update_api_client():
    """Actualizar cliente de API"""
    print("🔌 Actualizando cliente de API...")
    
    api_client_content = '''import requests
from typing import Dict, Any, Optional
import logging
import time
from config.settings import AppConfig

logger = logging.getLogger(__name__)

class APIClient:
    """Cliente base para hacer requests a APIs"""
    
    def __init__(self, base_url: str, timeout: int = AppConfig.REQUEST_TIMEOUT):
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.session = requests.Session()
        
        # Configurar headers por defecto
        self.session.headers.update({
            'User-Agent': f'{AppConfig.APP_NAME}/{AppConfig.APP_VERSION}',
            'Accept': 'application/json'
        })
        
        # Rate limiting simple
        self.last_request_time = 0
        self.min_request_interval = 1.0  # Mínimo 1 segundo entre requests
    
    def _wait_for_rate_limit(self):
        """Aplicar rate limiting básico"""
        now = time.time()
        time_since_last = now - self.last_request_time
        if time_since_last < self.min_request_interval:
            sleep_time = self.min_request_interval - time_since_last
            time.sleep(sleep_time)
        self.last_request_time = time.time()
    
    def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Hacer GET request"""
        self._wait_for_rate_limit()
        
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        
        try:
            logger.info(f"GET request to: {url}")
            response = self.session.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            
            data = response.json()
            logger.info(f"Successful response from {url}")
            return data
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed for {url}: {e}")
            raise APIException(f"Error accessing {url}: {e}")
        
        except ValueError as e:
            logger.error(f"Invalid JSON response from {url}: {e}")
            raise APIException(f"Invalid JSON response from {url}")

class ErgastAPIClient(APIClient):
    """Cliente específico para Jolpica F1 API (reemplazo de Ergast)"""
    
    def __init__(self):
        # Intentar primera opción (HTTP)
        self.current_base_url = AppConfig.ERGAST_BASE_URL
        super().__init__(self.current_base_url)
        
        # URLs de respaldo
        self.backup_urls = [
            AppConfig.BACKUP_APIS["jolpica_https"],
            AppConfig.BACKUP_APIS["jolpica_http"]
        ]
        self.backup_index = 0
        
        logger.info(f"Initialized ErgastAPIClient with base URL: {self.current_base_url}")
    
    def _switch_to_backup(self):
        """Cambiar a URL de respaldo en caso de fallo"""
        if self.backup_index < len(self.backup_urls):
            self.current_base_url = self.backup_urls[self.backup_index]
            self.base_url = self.current_base_url
            self.backup_index += 1
            logger.warning(f"Switching to backup URL: {self.current_base_url}")
            return True
        return False
    
    def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """GET request con soporte para URLs de respaldo"""
        max_attempts = len(self.backup_urls) + 1
        
        for attempt in range(max_attempts):
            try:
                return super().get(endpoint, params)
            
            except APIException as e:
                logger.warning(f"Attempt {attempt + 1} failed: {e}")
                
                if attempt < max_attempts - 1:  # No es el último intento
                    if self._switch_to_backup():
                        logger.info(f"Retrying with backup URL: {self.current_base_url}")
                        continue
                
                # Si llegamos aquí, todos los intentos fallaron
                raise APIException(f"All API endpoints failed. Last error: {e}")
    
    def get_current_driver_standings(self) -> Dict[str, Any]:
        """Obtener standings actuales de pilotos"""
        return self.get("current/driverStandings.json")
    
    def get_current_constructor_standings(self) -> Dict[str, Any]:
        """Obtener standings actuales de constructores"""
        return self.get("current/constructorStandings.json")
    
    def get_current_season_races(self) -> Dict[str, Any]:
        """Obtener calendario de la temporada actual"""
        return self.get("current.json")
    
    def get_race_results(self, season: str, round_number: str) -> Dict[str, Any]:
        """Obtener resultados de una carrera específica"""
        return self.get(f"{season}/{round_number}/results.json")
    
    def get_qualifying_results(self, season: str, round_number: str) -> Dict[str, Any]:
        """Obtener resultados de clasificación"""
        return self.get(f"{season}/{round_number}/qualifying.json")
    
    def test_connection(self) -> bool:
        """Probar conectividad con la API"""
        try:
            # Hacer una request simple para probar
            data = self.get("current.json", params={"limit": 1})
            logger.info("API connection test successful")
            return True
        except APIException as e:
            logger.error(f"API connection test failed: {e}")
            return False

class NewsAPIClient(APIClient):
    """Cliente para APIs de noticias (futuro)"""
    
    def __init__(self, api_key: str):
        super().__init__("https://newsapi.org/v2")
        self.session.headers.update({'X-API-Key': api_key})
    
    def get_motorsport_news(self, query: str = "Formula 1 OR MotoGP") -> Dict[str, Any]:
        """Obtener noticias de motorsport"""
        params = {
            'q': query,  
            'sortBy': 'publishedAt',
            'language': 'es'
        }
        return self.get("everything", params=params)

class APIException(Exception):
    """Excepción personalizada para errores de API"""
    pass'''
    
    with open("services/api_client.py", "w", encoding="utf-8") as f:
        f.write(api_client_content)
    
    print("   ✅ services/api_client.py actualizado")

def test_updated_api():
    """Probar la API actualizada"""
    print("🧪 Probando API actualizada...")
    
    try:
        # Importar después de actualizar los archivos
        sys.path.insert(0, '.')
        from services.api_client import ErgastAPIClient
        
        client = ErgastAPIClient()
        
        if client.test_connection():
            print("   ✅ API funciona correctamente")
            return True
        else:
            print("   ❌ Error al conectar con la API")
            return False
            
    except Exception as e:
        print(f"   ❌ Error al probar la API: {e}")
        return False

def main():
    """Función principal de actualización"""
    print("🏎️" * 20)
    print("F1 & MotoGP Dashboard - Script de Actualización")
    print("Migrando de Ergast API a Jolpica API")
    print("🏎️" * 20)
    print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    try:
        # Paso 1: Crear backup
        backup_dir = backup_files()
        print()
        
        # Paso 2: Actualizar archivos
        update_config()
        update_api_client()
        print()
        
        # Paso 3: Probar API
        if test_updated_api():
            print()
            print("🎉 ACTUALIZACIÓN COMPLETADA EXITOSAMENTE!")
            print()
            print("✅ Cambios realizados:")
            print("   • config/settings.py -> Jolpica API URL")
            print("   • services/api_client.py -> Soporte para fallback")
            print("   • Rate limiting implementado")
            print("   • Backup creado en:", backup_dir)
            print()
            print("🚀 Tu aplicación ahora debería funcionar correctamente.")
            print("   Ejecuta: python main.py")
            
        else:
            print()
            print("⚠️  ACTUALIZACIÓN COMPLETADA CON ADVERTENCIAS")
            print()
            print("Los archivos se actualizaron pero hay problemas de conectividad.")
            print("Esto puede deberse a:")
            print("• Problemas temporales de red")
            print("• API de Jolpica temporalmente inaccesible")
            print()
            print("Prueba ejecutar la aplicación de todas formas:")
            print("   python main.py")
        
    except Exception as e:
        print(f"❌ ERROR durante la actualización: {e}")
        print()
        print("Para restaurar el backup:")
        print(f"   • Copia los archivos desde {backup_dir if 'backup_dir' in locals() else 'backup_*'}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = main()
    print()
    print("📋 PRÓXIMOS PASOS:")
    print("1. Ejecuta: python main.py")
    print("2. Si hay problemas, revisa los logs en logs/app.log")
    print("3. Para soporte: https://github.com/jolpica/jolpica-f1")
    print()
    print("¡Disfruta de tu dashboard actualizado! 🏁")
    sys.exit(exit_code)