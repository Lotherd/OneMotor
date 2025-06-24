import requests
from typing import Dict, Any, Optional
import logging
import time
from config.settings import AppConfig

logger = logging.getLogger(__name__)

class APIClient:
    """Base client for making API requests"""
    
    def __init__(self, base_url: str, timeout: int = AppConfig.REQUEST_TIMEOUT):
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.session = requests.Session()
        
        # Configure default headers
        self.session.headers.update({
            'User-Agent': f'{AppConfig.APP_NAME}/{AppConfig.APP_VERSION}',
            'Accept': 'application/json'
        })
        
        # Simple rate limiting
        self.last_request_time = 0
        self.min_request_interval = 1.0  # Minimum 1 second between requests
    
    def _wait_for_rate_limit(self):
        """Apply basic rate limiting"""
        now = time.time()
        time_since_last = now - self.last_request_time
        if time_since_last < self.min_request_interval:
            sleep_time = self.min_request_interval - time_since_last
            time.sleep(sleep_time)
        self.last_request_time = time.time()
    
    def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make GET request"""
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
    """Specific client for Jolpica F1 API (Ergast replacement)"""
    
    def __init__(self):
        # Try first option (HTTP)
        self.current_base_url = AppConfig.ERGAST_BASE_URL
        super().__init__(self.current_base_url)
        
        # Backup URLs
        self.backup_urls = [
            AppConfig.BACKUP_APIS["jolpica_https"],
            AppConfig.BACKUP_APIS["jolpica_http"]
        ]
        self.backup_index = 0
        
        logger.info(f"Initialized ErgastAPIClient with base URL: {self.current_base_url}")
    
    def _switch_to_backup(self):
        """Switch to backup URL in case of failure"""
        if self.backup_index < len(self.backup_urls):
            self.current_base_url = self.backup_urls[self.backup_index]
            self.base_url = self.current_base_url
            self.backup_index += 1
            logger.warning(f"Switching to backup URL: {self.current_base_url}")
            return True
        return False
    
    def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """GET request with backup URL support"""
        max_attempts = len(self.backup_urls) + 1
        
        for attempt in range(max_attempts):
            try:
                return super().get(endpoint, params)
            
            except APIException as e:
                logger.warning(f"Attempt {attempt + 1} failed: {e}")
                
                if attempt < max_attempts - 1:  # Not the last attempt
                    if self._switch_to_backup():
                        logger.info(f"Retrying with backup URL: {self.current_base_url}")
                        continue
                
                # If we get here, all attempts failed
                raise APIException(f"All API endpoints failed. Last error: {e}")
    
    def get_current_driver_standings(self) -> Dict[str, Any]:
        """Get current driver standings"""
        return self.get("current/driverStandings.json")
    
    def get_current_constructor_standings(self) -> Dict[str, Any]:
        """Get current constructor standings"""
        return self.get("current/constructorStandings.json")
    
    def get_current_season_races(self) -> Dict[str, Any]:
        """Get current season calendar"""
        return self.get("current.json")
    
    def get_race_results(self, season: str, round_number: str) -> Dict[str, Any]:
        """Get results for a specific race"""
        return self.get(f"{season}/{round_number}/results.json")
    
    def get_qualifying_results(self, season: str, round_number: str) -> Dict[str, Any]:
        """Get qualifying results"""
        return self.get(f"{season}/{round_number}/qualifying.json")
    
    def test_connection(self) -> bool:
        """Test API connectivity"""
        try:
            # Make a simple request to test
            data = self.get("current.json", params={"limit": 1})
            logger.info("API connection test successful")
            return True
        except APIException as e:
            logger.error(f"API connection test failed: {e}")
            return False

class NewsAPIClient(APIClient):
    """Client for news APIs (future use)"""
    
    def __init__(self, api_key: str):
        super().__init__("https://newsapi.org/v2")
        self.session.headers.update({'X-API-Key': api_key})
    
    def get_motorsport_news(self, query: str = "Formula 1 OR MotoGP") -> Dict[str, Any]:
        """Get motorsport news"""
        params = {
            'q': query,  
            'sortBy': 'publishedAt',
            'language': 'en'
        }
        return self.get("everything", params=params)

class APIException(Exception):
    """Custom exception for API errors"""
    pass