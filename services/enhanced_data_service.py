# services/enhanced_data_service.py
"""
Enhanced data service with working F1 endpoints and real career statistics

This module provides enhanced F1 data retrieval with working API endpoints
and real career statistics calculation for drivers.

**Classes:**
    EnhancedDataService - Extended service with career stats and working endpoints
    SessionDataLoader - Background loader for session data with fallback
    CareerStatsLoader - Background loader for driver career statistics

**Author:** Lotherd
**Version:** 2.0.0
"""

import logging
from typing import List, Optional, Dict, Any
from PyQt6.QtCore import QObject, pyqtSignal, QThread

from models.driver import DriverStanding, Driver, Constructor
from models.race import Race
from services.api_client import ErgastAPIClient, APIException

logger = logging.getLogger(__name__)

class CareerStatsLoader(QThread):
    """Background thread for loading driver career statistics"""
    
    stats_loaded = pyqtSignal(dict)  # Career stats dictionary
    error_occurred = pyqtSignal(str)  # Error message
    loading_finished = pyqtSignal()
    
    def __init__(self, ergast_client: ErgastAPIClient, driver_id: str):
        super().__init__()
        self.ergast_client = ergast_client
        self.driver_id = driver_id
        self.career_stats = {}
    
    def run(self):
        """Load comprehensive career statistics for a driver"""
        try:
            # Get all seasons for this driver
            driver_seasons_data = self.ergast_client.get(f"drivers/{self.driver_id}/seasons.json?limit=100")
            
            # Initialize stats
            total_races = 0
            total_wins = 0
            total_podiums = 0
            total_poles = 0
            total_fastest_laps = 0
            total_points = 0.0
            championships = 0
            seasons_active = []
            teams = set()
            
            if 'MRData' in driver_seasons_data and 'SeasonTable' in driver_seasons_data['MRData']:
                seasons = driver_seasons_data['MRData']['SeasonTable'].get('Seasons', [])
                
                for season in seasons:
                    season_year = season.get('season')
                    if season_year:
                        seasons_active.append(season_year)
                        
                        try:
                            # Get driver standings for this season
                            standings_data = self.ergast_client.get(f"{season_year}/drivers/{self.driver_id}/driverStandings.json")
                            
                            if ('MRData' in standings_data and 
                                'StandingsTable' in standings_data['MRData'] and
                                standings_data['MRData']['StandingsTable'].get('StandingsLists')):
                                
                                standings_list = standings_data['MRData']['StandingsTable']['StandingsLists'][0]
                                if standings_list.get('DriverStandings'):
                                    driver_standing = standings_list['DriverStandings'][0]
                                    
                                    # Add points
                                    points = float(driver_standing.get('points', 0))
                                    total_points += points
                                    
                                    # Add wins
                                    wins = int(driver_standing.get('wins', 0))
                                    total_wins += wins
                                    
                                    # Check if champion (position 1)
                                    if driver_standing.get('position') == '1':
                                        championships += 1
                                    
                                    # Get constructors for teams list
                                    for constructor in driver_standing.get('Constructors', []):
                                        teams.add(constructor.get('name', ''))
                            
                            # Get race results for this season to count podiums, poles, etc.
                            results_data = self.ergast_client.get(f"{season_year}/drivers/{self.driver_id}/results.json?limit=100")
                            
                            if ('MRData' in results_data and 
                                'RaceTable' in results_data['MRData'] and
                                results_data['MRData']['RaceTable'].get('Races')):
                                
                                races = results_data['MRData']['RaceTable']['Races']
                                total_races += len(races)
                                
                                for race in races:
                                    for result in race.get('Results', []):
                                        position = result.get('position')
                                        if position and position.isdigit():
                                            pos = int(position)
                                            if pos <= 3:  # Podium
                                                total_podiums += 1
                            
                            # Get qualifying results for pole positions
                            qualifying_data = self.ergast_client.get(f"{season_year}/drivers/{self.driver_id}/qualifying.json?limit=100")
                            
                            if ('MRData' in qualifying_data and 
                                'RaceTable' in qualifying_data['MRData'] and
                                qualifying_data['MRData']['RaceTable'].get('Races')):
                                
                                races = qualifying_data['MRData']['RaceTable']['Races']
                                for race in races:
                                    for result in race.get('QualifyingResults', []):
                                        if result.get('position') == '1':
                                            total_poles += 1
                        
                        except Exception as e:
                            logger.warning(f"Error loading data for {driver_id} season {season_year}: {e}")
                            continue
            
            # Compile final stats
            self.career_stats = {
                'total_races': total_races,
                'total_wins': total_wins,
                'total_podiums': total_podiums,
                'total_poles': total_poles,
                'total_points': round(total_points, 1),
                'championships': championships,
                'seasons_active': len(seasons_active),
                'first_season': min(seasons_active) if seasons_active else 'N/A',
                'last_season': max(seasons_active) if seasons_active else 'N/A',
                'teams': list(teams),
                'win_percentage': round((total_wins / total_races * 100), 1) if total_races > 0 else 0,
                'podium_percentage': round((total_podiums / total_races * 100), 1) if total_races > 0 else 0
            }
            
            self.stats_loaded.emit(self.career_stats)
            logger.info(f"Loaded career stats for {self.driver_id}: {total_races} races, {total_wins} wins")
            
        except Exception as e:
            logger.error(f"Error loading career stats for {self.driver_id}: {e}")
            # Return basic fallback stats
            self.career_stats = {
                'total_races': 'N/A',
                'total_wins': 'N/A', 
                'total_podiums': 'N/A',
                'total_poles': 'N/A',
                'total_points': 'N/A',
                'championships': 'N/A',
                'seasons_active': 'N/A',
                'teams': ['N/A'],
                'error': str(e)
            }
            self.error_occurred.emit(str(e))
        
        finally:
            self.loading_finished.emit()

class SessionDataLoader(QThread):
    """Background thread for loading race weekend session data with working endpoints"""
    
    session_loaded = pyqtSignal(str, list)  # session_type, results
    all_sessions_loaded = pyqtSignal(dict)  # All sessions data
    error_occurred = pyqtSignal(str, str)  # session_type, error_message
    loading_progress = pyqtSignal(str)  # Current loading status
    loading_finished = pyqtSignal()
    
    def __init__(self, ergast_client: ErgastAPIClient, season: str, round_num: str):
        super().__init__()
        self.ergast_client = ergast_client
        self.season = season
        self.round_num = round_num
        self.session_data = {}
    
    def run(self):
        """Load all available session data using working endpoints"""
        # Only use endpoints that are known to work with Ergast API
        sessions_to_check = [
            ("Qualifying", "qualifying"),
            ("Race", "results")
        ]
        
        total_sessions = len(sessions_to_check)
        
        for i, (session_name, endpoint_type) in enumerate(sessions_to_check):
            try:
                self.loading_progress.emit(f"Loading {session_name}... ({i+1}/{total_sessions})")
                
                # Use only working Ergast endpoints
                if endpoint_type == "qualifying":
                    data = self.ergast_client.get(f"{self.season}/{self.round_num}/qualifying.json")
                elif endpoint_type == "results":
                    data = self.ergast_client.get(f"{self.season}/{self.round_num}/results.json")
                else:
                    continue
                
                # Parse results using the correct endpoint response structure
                results = self.parse_session_data(data, endpoint_type)
                
                if results:
                    self.session_data[session_name] = results
                    self.session_loaded.emit(session_name, results)
                    logger.info(f"Loaded {session_name}: {len(results)} results")
                else:
                    logger.info(f"No data available for {session_name}")
                    
            except Exception as e:
                logger.error(f"Error loading {session_name}: {e}")
                self.error_occurred.emit(session_name, str(e))
        
        # Try to get additional data that might be available
        self.try_additional_sessions()
        
        # Emit all collected data
        self.all_sessions_loaded.emit(self.session_data)
        self.loading_finished.emit()
    
    def try_additional_sessions(self):
        """Try to load additional session types that may be available"""
        additional_sessions = [
            ("Practice 1", f"{self.season}/{self.round_num}/practice/1.json"),
            ("Practice 2", f"{self.season}/{self.round_num}/practice/2.json"), 
            ("Practice 3", f"{self.season}/{self.round_num}/practice/3.json"),
            ("Sprint", f"{self.season}/{self.round_num}/sprint.json")
        ]
        
        for session_name, endpoint in additional_sessions:
            try:
                self.loading_progress.emit(f"Checking {session_name}...")
                data = self.ergast_client.get(endpoint)
                
                # Parse based on session type
                if "practice" in endpoint:
                    results = self.parse_practice_data(data)
                elif "sprint" in endpoint:
                    results = self.parse_sprint_data(data)
                else:
                    results = []
                
                if results:
                    self.session_data[session_name] = results
                    self.session_loaded.emit(session_name, results)
                    logger.info(f"Found additional session {session_name}: {len(results)} results")
                    
            except Exception as e:
                # These are optional, so just log and continue
                logger.debug(f"Optional session {session_name} not available: {e}")
                continue
    
    def parse_session_data(self, data: Dict[str, Any], session_type: str) -> List[Dict[str, Any]]:
        """Parse API response data based on session type"""
        try:
            if not data or 'MRData' not in data:
                return []
            
            race_table = data['MRData']['RaceTable']
            if 'Races' not in race_table or not race_table['Races']:
                return []
            
            race_data = race_table['Races'][0]
            
            # Different session types have different result structures
            if session_type == "qualifying":
                return race_data.get('QualifyingResults', [])
            elif session_type == "results":
                return race_data.get('Results', [])
            
            return []
            
        except Exception as e:
            logger.error(f"Error parsing {session_type} data: {e}")
            return []
    
    def parse_practice_data(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Parse practice session data"""
        try:
            if not data or 'MRData' not in data:
                return []
            
            race_table = data['MRData']['RaceTable']
            if 'Races' not in race_table or not race_table['Races']:
                return []
            
            race_data = race_table['Races'][0]
            return race_data.get('PracticeResults', [])
            
        except Exception as e:
            logger.error(f"Error parsing practice data: {e}")
            return []
    
    def parse_sprint_data(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Parse sprint session data"""
        try:
            if not data or 'MRData' not in data:
                return []
            
            race_table = data['MRData']['RaceTable']
            if 'Races' not in race_table or not race_table['Races']:
                return []
            
            race_data = race_table['Races'][0]
            return race_data.get('SprintResults', [])
            
        except Exception as e:
            logger.error(f"Error parsing sprint data: {e}")
            return []

class EnhancedDataService(QObject):
    """Enhanced service for F1 data management with career statistics and working endpoints"""
    
    def __init__(self):
        super().__init__()
        self.ergast_client = ErgastAPIClient()
    
    def get_current_f1_standings(self) -> List[DriverStanding]:
        """Retrieves and processes current F1 driver championship standings"""
        try:
            data = self.ergast_client.get_current_driver_standings()
            standings_data = data['MRData']['StandingsTable']['StandingsLists'][0]['DriverStandings']
            
            standings = []
            for standing_data in standings_data:
                standing = DriverStanding.from_ergast_data(standing_data)
                standings.append(standing)
            
            logger.info(f"Loaded {len(standings)} driver standings")
            return standings
            
        except APIException as e:
            logger.error(f"Error getting F1 standings: {e}")
            raise
        except (KeyError, IndexError) as e:
            logger.error(f"Error parsing F1 standings data: {e}")
            raise Exception("Error parsing F1 standings data")
    
    def get_season_race_calendar(self, season: str) -> List[Race]:
        """Retrieves race calendar with podium results for a specified season"""
        try:
            data = self.ergast_client.get(f"{season}.json")
            races_data = data['MRData']['RaceTable']['Races']

            races: List[Race] = []
            for race in races_data:
                try:
                    results = self.ergast_client.get_race_results(season, race['round'])
                except APIException:
                    results = None

                race_obj = Race.from_ergast_data(season, race, results)
                races.append(race_obj)

            logger.info(f"Loaded {len(races)} races for {season}")
            return races

        except APIException as e:
            logger.error(f"Error getting race calendar: {e}")
            raise
        except Exception as e:
            logger.error(f"Error parsing race calendar: {e}")
            raise Exception("Error parsing race calendar")
    
    def create_session_loader(self, season: str, round_num: str) -> SessionDataLoader:
        """Creates a session data loader for a specific race"""
        return SessionDataLoader(self.ergast_client, season, round_num)
    
    def create_career_stats_loader(self, driver_id: str) -> CareerStatsLoader:
        """Creates a career statistics loader for a specific driver"""
        return CareerStatsLoader(self.ergast_client, driver_id)
    
    def test_session_endpoints(self, season: str = "2024", round_num: str = "1") -> Dict[str, bool]:
        """Test which session endpoints are working"""
        endpoints_status = {}
        
        test_endpoints = [
            ("qualifying", f"{season}/{round_num}/qualifying.json"),
            ("results", f"{season}/{round_num}/results.json"),
            ("practice1", f"{season}/{round_num}/practice/1.json"),
            ("practice2", f"{season}/{round_num}/practice/2.json"),
            ("practice3", f"{season}/{round_num}/practice/3.json"),
            ("sprint", f"{season}/{round_num}/sprint.json")
        ]
        
        for endpoint_name, endpoint_url in test_endpoints:
            try:
                data = self.ergast_client.get(endpoint_url)
                if data and 'MRData' in data:
                    endpoints_status[endpoint_name] = True
                    logger.info(f"✅ {endpoint_name} endpoint working")
                else:
                    endpoints_status[endpoint_name] = False
            except Exception as e:
                endpoints_status[endpoint_name] = False
                logger.info(f"❌ {endpoint_name} endpoint not available: {e}")
        
        return endpoints_status