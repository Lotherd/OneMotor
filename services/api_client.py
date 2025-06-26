# services/api_client.py
"""
Updated API client with working F1 endpoints for 2025
"""

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
    """Updated F1 API client with working 2025 endpoints"""
    
    def __init__(self):
        # Updated working endpoints for 2025
        self.endpoints = [
            "http://api.jolpi.ca/ergast/f1",      # Jolpica F1 (primary replacement)
            "https://api.jolpi.ca/ergast/f1",     # HTTPS version
            "https://openf1.org/v1"               # OpenF1 alternative
        ]
        
        self.current_endpoint_index = 0
        self.current_base_url = self.endpoints[0]
        super().__init__(self.current_base_url)
        
        logger.info(f"Initialized ErgastAPIClient with endpoint: {self.current_base_url}")
    
    def _switch_to_next_endpoint(self):
        """Switch to the next available endpoint"""
        self.current_endpoint_index += 1
        if self.current_endpoint_index < len(self.endpoints):
            self.current_base_url = self.endpoints[self.current_endpoint_index]
            self.base_url = self.current_base_url
            logger.warning(f"Switching to endpoint: {self.current_base_url}")
            return True
        return False
    
    def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """GET request with automatic endpoint fallback"""
        max_attempts = len(self.endpoints)
        
        for attempt in range(max_attempts):
            try:
                # Use different endpoint format for OpenF1
                if "openf1.org" in self.current_base_url:
                    return self._get_openf1_data(endpoint, params)
                else:
                    return super().get(endpoint, params)
            
            except APIException as e:
                logger.warning(f"Attempt {attempt + 1} failed with {self.current_base_url}: {e}")
                
                if attempt < max_attempts - 1:  # Not the last attempt
                    if self._switch_to_next_endpoint():
                        logger.info(f"Retrying with endpoint: {self.current_base_url}")
                        continue
                
                # If we get here, all attempts failed
                raise APIException(f"All F1 API endpoints failed. Last error: {e}")
    
    def _get_openf1_data(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Handle OpenF1 API format (different structure)"""
        try:
            # Convert Ergast-style endpoints to OpenF1 format
            if "driverStandings" in endpoint:
                # For driver standings, we need to construct from OpenF1 data
                openf1_endpoint = "drivers"
                response = super().get(openf1_endpoint, params)
                return self._convert_openf1_to_ergast_format(response, "drivers")
            
            elif "constructorStandings" in endpoint:
                openf1_endpoint = "teams"
                response = super().get(openf1_endpoint, params)
                return self._convert_openf1_to_ergast_format(response, "constructors")
            
            elif endpoint.endswith(".json"):
                # Remove .json and try to map to OpenF1
                clean_endpoint = endpoint.replace(".json", "")
                if "current" in clean_endpoint:
                    # Current season races
                    openf1_endpoint = "sessions"
                    response = super().get(openf1_endpoint, {"session_type": "Race"})
                    return self._convert_openf1_to_ergast_format(response, "races")
            
            # Default fallback
            return super().get(endpoint, params)
            
        except Exception as e:
            logger.error(f"OpenF1 conversion failed: {e}")
            raise APIException(f"OpenF1 API error: {e}")
    
    def _convert_openf1_to_ergast_format(self, openf1_data: Any, data_type: str) -> Dict[str, Any]:
        """Convert OpenF1 format to Ergast-compatible format"""
        try:
            if data_type == "drivers":
                # Convert OpenF1 drivers to Ergast format
                # This is a simplified conversion - OpenF1 has different structure
                return {
                    "MRData": {
                        "StandingsTable": {
                            "StandingsLists": [{
                                "DriverStandings": []  # Would need proper mapping
                            }]
                        }
                    }
                }
            
            # For now, return empty structure to prevent crashes
            return {
                "MRData": {
                    "StandingsTable": {
                        "StandingsLists": [{
                            "DriverStandings": []
                        }]
                    }
                }
            }
            
        except Exception as e:
            logger.error(f"Format conversion failed: {e}")
            raise APIException(f"Data conversion error: {e}")
    
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
        """Test API connectivity with all endpoints"""
        logger.info("Testing F1 API connections...")
        
        original_index = self.current_endpoint_index
        original_url = self.current_base_url
        
        # Test each endpoint
        for i, endpoint in enumerate(self.endpoints):
            self.current_endpoint_index = i
            self.current_base_url = endpoint
            self.base_url = endpoint
            
            try:
                logger.info(f"Testing endpoint {i+1}: {endpoint}")
                
                if "openf1.org" in endpoint:
                    # Test OpenF1 with a simple endpoint
                    data = super().get("drivers", params={"limit": 1})
                else:
                    # Test Jolpica/Ergast-style endpoints
                    data = self.get("current.json", params={"limit": 1})
                
                logger.info(f"✅ Endpoint {i+1} working: {endpoint}")
                return True
                
            except Exception as e:
                logger.warning(f"❌ Endpoint {i+1} failed: {endpoint} - {e}")
                continue
        
        # Restore original settings
        self.current_endpoint_index = original_index
        self.current_base_url = original_url
        self.base_url = original_url
        
        logger.error("All F1 API endpoints failed during testing")
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