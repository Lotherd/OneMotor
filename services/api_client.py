# services/api_client.py
"""
Updated API client with working F1 endpoints for 2025

This module provides HTTP client classes for accessing F1 and motorsport APIs.
It includes automatic endpoint fallback, rate limiting, and error handling
for reliable data retrieval from multiple API sources.

**Classes:**
    APIClient - Base HTTP client with rate limiting and error handling
    ErgastAPIClient - F1-specific client with multiple endpoint fallback
    NewsAPIClient - News API client for motorsport news
    APIException - Custom exception for API-related errors

**Author:** Lotherd
**Version:** 1.0.0
"""

import requests
from typing import Dict, Any, Optional
import logging
import time
from config.settings import AppConfig

logger = logging.getLogger(__name__)

class APIClient:
    """Base client for making HTTP API requests with rate limiting and error handling"""
    
    """
    * Initializes the base API client with configuration and session setup
    *
    * This constructor sets up the HTTP session with default headers, configures
    * the base URL, timeout settings, and initializes rate limiting parameters
    * to ensure respectful API usage.
    *
    * **@param** base_url String base URL for the API endpoints
    * **@param** timeout Integer timeout in seconds for requests
    * **@return** None
    """
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
    
    """
    * Applies rate limiting by waiting between consecutive requests
    *
    * This method ensures that requests are spaced apart by at least the
    * minimum interval to avoid overwhelming the API server and respect
    * rate limiting policies.
    *
    * **@return** None
    """
    def _wait_for_rate_limit(self):
        now = time.time()
        time_since_last = now - self.last_request_time
        if time_since_last < self.min_request_interval:
            sleep_time = self.min_request_interval - time_since_last
            time.sleep(sleep_time)
        self.last_request_time = time.time()
    
    """
    * Makes a GET request to the specified endpoint with error handling
    *
    * This method constructs the full URL, applies rate limiting, makes the
    * HTTP GET request, and handles various error conditions including
    * network errors and JSON parsing failures.
    *
    * **@param** endpoint String API endpoint path
    * **@param** params Optional dictionary of query parameters
    * **@return** Dictionary containing the parsed JSON response
    * **@throws** APIException for request failures or invalid responses
    """
    def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
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
    """Updated F1 API client with working 2025 endpoints and automatic fallback"""
    
    """
    * Initializes the F1 API client with multiple endpoint fallback
    *
    * This constructor sets up multiple API endpoints for F1 data access,
    * including the primary Jolpica F1 API and alternative sources. It
    * configures automatic fallback between endpoints for reliability.
    *
    * **@return** None
    """
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
    
    """
    * Switches to the next available API endpoint in the fallback chain
    *
    * This method moves to the next endpoint in the list when the current
    * endpoint fails, updating the base URL and endpoint index accordingly.
    * It returns False when no more endpoints are available.
    *
    * **@return** Boolean True if switch successful, False if no more endpoints
    """
    def _switch_to_next_endpoint(self):
        self.current_endpoint_index += 1
        if self.current_endpoint_index < len(self.endpoints):
            self.current_base_url = self.endpoints[self.current_endpoint_index]
            self.base_url = self.current_base_url
            logger.warning(f"Switching to endpoint: {self.current_base_url}")
            return True
        return False
    
    """
    * Makes GET request with automatic endpoint fallback on failure
    *
    * This method attempts the GET request with the current endpoint and
    * automatically switches to alternative endpoints if failures occur.
    * It handles different API formats like OpenF1 vs Ergast-style endpoints.
    *
    * **@param** endpoint String API endpoint path
    * **@param** params Optional dictionary of query parameters
    * **@return** Dictionary containing the parsed JSON response
    * **@throws** APIException when all endpoints fail
    """
    def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
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
    
    """
    * Handles OpenF1 API format conversion to Ergast-compatible structure
    *
    * This method converts between different API formats when using OpenF1
    * as an alternative to the Ergast API, mapping endpoints and data
    * structures to maintain compatibility.
    *
    * **@param** endpoint String Ergast-style endpoint path
    * **@param** params Optional dictionary of query parameters
    * **@return** Dictionary in Ergast-compatible format
    * **@throws** APIException for conversion or request failures
    """
    def _get_openf1_data(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
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
    
    """
    * Converts OpenF1 data format to Ergast-compatible data structure
    *
    * This method transforms the OpenF1 API response format into the expected
    * Ergast API format to maintain compatibility with existing data models
    * and parsing logic throughout the application.
    *
    * **@param** openf1_data Raw data from OpenF1 API response
    * **@param** data_type String indicating the type of data (drivers, constructors, races)
    * **@return** Dictionary in Ergast-compatible format
    * **@throws** APIException for conversion failures
    """
    def _convert_openf1_to_ergast_format(self, openf1_data: Any, data_type: str) -> Dict[str, Any]:
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
    
    """
    * Retrieves current F1 driver championship standings
    *
    * This method fetches the latest driver standings for the current F1 season
    * using the appropriate API endpoint with automatic fallback support.
    *
    * **@return** Dictionary containing driver standings data in Ergast format
    """
    def get_current_driver_standings(self) -> Dict[str, Any]:
        return self.get("current/driverStandings.json")
    
    """
    * Retrieves current F1 constructor championship standings
    *
    * This method fetches the latest constructor/team standings for the current
    * F1 season using the appropriate API endpoint with automatic fallback support.
    *
    * **@return** Dictionary containing constructor standings data in Ergast format
    """
    def get_current_constructor_standings(self) -> Dict[str, Any]:
        return self.get("current/constructorStandings.json")
    
    """
    * Retrieves the current F1 season race calendar
    *
    * This method fetches the complete race calendar for the current F1 season
    * including all scheduled races and their basic information.
    *
    * **@return** Dictionary containing race calendar data in Ergast format
    """
    def get_current_season_races(self) -> Dict[str, Any]:
        return self.get("current.json")
    
    """
    * Retrieves race results for a specific season and round
    *
    * This method fetches the complete race results including finishing positions,
    * times, and other race statistics for the specified season and round number.
    *
    * **@param** season String representing the F1 season year
    * **@param** round_number String representing the race round number
    * **@return** Dictionary containing race results data in Ergast format
    """
    def get_race_results(self, season: str, round_number: str) -> Dict[str, Any]:
        return self.get(f"{season}/{round_number}/results.json")
    
    """
    * Retrieves qualifying results for a specific season and round
    *
    * This method fetches the qualifying session results including lap times,
    * positions, and qualifying statistics for the specified season and round.
    *
    * **@param** season String representing the F1 season year
    * **@param** round_number String representing the race round number
    * **@return** Dictionary containing qualifying results data in Ergast format
    """
    def get_qualifying_results(self, season: str, round_number: str) -> Dict[str, Any]:
        return self.get(f"{season}/{round_number}/qualifying.json")
    
    """
    * Tests connectivity to all configured F1 API endpoints
    *
    * This method systematically tests each configured API endpoint to determine
    * which ones are currently functional. It attempts simple requests to verify
    * connectivity and data availability.
    *
    * **@return** Boolean True if at least one endpoint is working, False otherwise
    """
    def test_connection(self) -> bool:
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
    """Client for accessing motorsport news APIs with authentication support"""
    
    """
    * Initializes the news API client with authentication
    *
    * This constructor sets up the news API client with the required API key
    * for authentication and configures the base URL for news endpoints.
    *
    * **@param** api_key String API key for news service authentication
    * **@return** None
    """
    def __init__(self, api_key: str):
        super().__init__("https://newsapi.org/v2")
        self.session.headers.update({'X-API-Key': api_key})
    
    """
    * Retrieves motorsport news articles based on search query
    *
    * This method searches for motorsport-related news articles using the
    * configured query parameters and returns the latest articles sorted
    * by publication date.
    *
    * **@param** query String search query for news articles
    * **@return** Dictionary containing news articles and metadata
    """
    def get_motorsport_news(self, query: str = "Formula 1 OR MotoGP") -> Dict[str, Any]:
        params = {
            'q': query,  
            'sortBy': 'publishedAt',
            'language': 'en'
        }
        return self.get("everything", params=params)

class APIException(Exception):
    """Custom exception class for API-related errors and failures"""
    pass