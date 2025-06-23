import requests
from typing import Dict, Any, Optional
import logging
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
    
    def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Hacer GET request"""
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
    """Cliente específico para Ergast API (F1)"""
    
    def __init__(self):
        super().__init__(AppConfig.ERGAST_BASE_URL)
    
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