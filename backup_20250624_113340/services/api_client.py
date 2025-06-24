# services/api_client.py
import requests
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
    pass