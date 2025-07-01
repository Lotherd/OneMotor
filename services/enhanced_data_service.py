# services/enhanced_data_service.py
"""
Complete enhanced data service with all F1 endpoints and OpenF1 integration

This module provides comprehensive F1 data retrieval with support for:
- Race results, Qualifying, Sprint races
- Pit stops and lap-by-lap history
- OpenF1 API integration for additional data
- Real career statistics and session data

**Classes:**
    EnhancedDataService - Main service with all F1 endpoints
    SessionDataLoader - Loads all session types including pit stops and laps
    CareerStatsLoader - Loads complete driver career statistics
    OpenF1Client - Client for OpenF1 API integration

**Author:** Lotherd
**Version:** 3.0.1 - Fixed OpenF1 URL and data display issues
"""

import logging
import requests
from typing import List, Optional, Dict, Any, Tuple
from PyQt6.QtCore import QObject, pyqtSignal, QThread
from datetime import datetime

from models.driver import DriverStanding, Driver, Constructor
from models.race import Race
from services.api_client import ErgastAPIClient, APIException

logger = logging.getLogger(__name__)

class OpenF1Client:
    """Client for OpenF1 API to get additional real-time data"""
    
    def __init__(self):
        # FIXED: Correct OpenF1 API URL
        self.base_url = "https://api.jolpi.ca/ergast"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'F1-Dashboard/1.0',
            'Accept': 'application/json'
        })
    
    def get_sessions(self, year: int = 2025) -> List[Dict[str, Any]]:
        try:
            resp = self.session.get(f"{self.base_url}/sessions", params={'year': year}, timeout=10)
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            logger.error(f"OpenF1 sessions error: {e}")
            return []
    
    def get_drivers(self, session_key: int = None) -> List[Dict[str, Any]]:
        """Get drivers for a session"""
        try:
            params = {}
            if session_key:
                params['session_key'] = session_key
            
            response = self.session.get(f"{self.base_url}/drivers", 
                                      params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"OpenF1 drivers error: {e}")
            return []
    
    def get_car_data(self, session_key: int = None) -> List[Dict[str, Any]]:
        """Get car data from OpenF1"""
        try:
            params = {}
            if session_key:
                params['session_key'] = session_key
            
            response = self.session.get(f"{self.base_url}/car_data", 
                                      params=params, timeout=15)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"OpenF1 car data error: {e}")
            return []
    
    def get_position_data(self, session_key: int) -> List[Dict[str, Any]]:
        """Get position data for a session"""
        try:
            response = self.session.get(f"{self.base_url}/position", 
                                      params={'session_key': session_key}, timeout=15)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"OpenF1 position data error: {e}")
            return []
    
    def get_lap_times(self, session_key: int) -> List[Dict[str, Any]]:
        """Get lap times for a session"""
        try:
            response = self.session.get(f"{self.base_url}/laps", 
                                      params={'session_key': session_key}, timeout=15)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"OpenF1 lap times error: {e}")
            return []

class CareerStatsLoader(QThread):
    """Enhanced career statistics loader with better error handling"""
    stats_loaded = pyqtSignal(dict)
    error_occurred = pyqtSignal(str)
    loading_progress = pyqtSignal(str)
    loading_finished = pyqtSignal()

    def __init__(self, ergast_client: ErgastAPIClient, driver_id: str):
        super().__init__()
        self.ergast_client = ergast_client
        self.driver_id = driver_id
        self.career_stats = {}
    
    def run(self):
        """Load comprehensive career statistics"""
        try:
            self.loading_progress.emit(f"Loading career data for {self.driver_id}...")
            
            # Get all seasons for driver
            seasons_data = self.ergast_client.get(f"drivers/{self.driver_id}/seasons.json?limit=100")
            
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
            best_finish = 999
            worst_finish = 0
            
            if 'MRData' in seasons_data and 'SeasonTable' in seasons_data['MRData']:
                seasons = seasons_data['MRData']['SeasonTable'].get('Seasons', [])
                total_seasons = len(seasons)
                
                for i, season in enumerate(seasons):
                    season_year = season.get('season')
                    if not season_year:
                        continue
                        
                    self.loading_progress.emit(f"Processing season {season_year} ({i+1}/{total_seasons})...")
                    seasons_active.append(season_year)
                    
                    try:
                        # Get driver standings for this season
                        standings_data = self.ergast_client.get(f"{season_year}/drivers/{self.driver_id}/driverStandings.json")
                        
                        if self._has_valid_standings_data(standings_data):
                            driver_standing = standings_data['MRData']['StandingsTable']['StandingsLists'][0]['DriverStandings'][0]
                            
                            # Points and wins
                            points = float(driver_standing.get('points', 0))
                            wins = int(driver_standing.get('wins', 0))
                            total_points += points
                            total_wins += wins
                            
                            # Championships
                            if driver_standing.get('position') == '1':
                                championships += 1
                            
                            # Teams
                            for constructor in driver_standing.get('Constructors', []):
                                teams.add(constructor.get('name', ''))
                        
                        # Get race results for detailed stats
                        results_data = self.ergast_client.get(f"{season_year}/drivers/{self.driver_id}/results.json?limit=100")
                        
                        if self._has_valid_race_data(results_data):
                            races = results_data['MRData']['RaceTable']['Races']
                            season_races = len(races)
                            total_races += season_races
                            
                            for race in races:
                                for result in race.get('Results', []):
                                    position = result.get('position')
                                    if position and position.isdigit():
                                        pos = int(position)
                                        
                                        # Track best and worst finishes
                                        if pos < best_finish:
                                            best_finish = pos
                                        if pos > worst_finish:
                                            worst_finish = pos
                                        
                                        # Podiums
                                        if pos <= 3:
                                            total_podiums += 1
                                        
                                        # Fastest laps
                                        if result.get('FastestLap', {}).get('rank') == '1':
                                            total_fastest_laps += 1
                        
                        # Get qualifying results for pole positions
                        qualifying_data = self.ergast_client.get(f"{season_year}/drivers/{self.driver_id}/qualifying.json?limit=100")
                        
                        if self._has_valid_qualifying_data(qualifying_data):
                            races = qualifying_data['MRData']['RaceTable']['Races']
                            for race in races:
                                for result in race.get('QualifyingResults', []):
                                    if result.get('position') == '1':
                                        total_poles += 1
                    
                    except Exception as e:
                        logger.warning(f"Error processing season {season_year} for {self.driver_id}: {e}")
                        continue
            
            # Calculate percentages and compile stats
            win_percentage = round((total_wins / total_races * 100), 1) if total_races > 0 else 0
            podium_percentage = round((total_podiums / total_races * 100), 1) if total_races > 0 else 0
            points_per_race = round(total_points / total_races, 1) if total_races > 0 else 0
            
            self.career_stats = {
                'total_races': total_races,
                'total_wins': total_wins,
                'total_podiums': total_podiums,
                'total_poles': total_poles,
                'total_fastest_laps': total_fastest_laps,
                'total_points': round(total_points, 1),
                'championships': championships,
                'seasons_active': len(seasons_active),
                'first_season': min(seasons_active) if seasons_active else 'N/A',
                'last_season': max(seasons_active) if seasons_active else 'N/A',
                'teams': list(teams),
                'win_percentage': win_percentage,
                'podium_percentage': podium_percentage,
                'points_per_race': points_per_race,
                'best_finish': best_finish if best_finish != 999 else 'N/A',
                'worst_finish': worst_finish if worst_finish > 0 else 'N/A',
                'career_span': f"{min(seasons_active)}-{max(seasons_active)}" if len(seasons_active) > 1 else seasons_active[0] if seasons_active else 'N/A'
            }
            
            self.loading_progress.emit("Career statistics compiled successfully!")
            self.stats_loaded.emit(self.career_stats)
            
            logger.info(f"✅ Career stats loaded for {self.driver_id}: {total_races} races, {total_wins} wins, {championships} championships")
            
        except Exception as e:
            error_msg = f"Failed to load career statistics: {str(e)}"
            logger.error(f"❌ {error_msg}")
            
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
            self.error_occurred.emit(error_msg)
        
        finally:
            self.loading_finished.emit()
    
    def _has_valid_standings_data(self, data: Dict) -> bool:
        """Check if standings data is valid"""
        return (data and 'MRData' in data and 
                'StandingsTable' in data['MRData'] and
                data['MRData']['StandingsTable'].get('StandingsLists') and
                data['MRData']['StandingsTable']['StandingsLists'][0].get('DriverStandings'))
    
    def _has_valid_race_data(self, data: Dict) -> bool:
        """Check if race data is valid"""
        return (data and 'MRData' in data and 
                'RaceTable' in data['MRData'] and
                data['MRData']['RaceTable'].get('Races'))
    
    def _has_valid_qualifying_data(self, data: Dict) -> bool:
        """Check if qualifying data is valid"""
        return (data and 'MRData' in data and 
                'RaceTable' in data['MRData'] and
                data['MRData']['RaceTable'].get('Races'))

class CompleteSessionDataLoader(QThread):
    """Complete session data loader including pit stops and lap history"""
    session_loaded      = pyqtSignal(str, list)
    all_sessions_loaded = pyqtSignal(dict)
    error_occurred      = pyqtSignal(str, str)
    loading_progress    = pyqtSignal(str)
    loading_finished    = pyqtSignal()

    def __init__(self, ergast_client: ErgastAPIClient, openf1_client: OpenF1Client, season: str, round_num: str):
        super().__init__()
        self.ergast_client = ergast_client
        self.openf1_client = openf1_client
        self.season        = season
        self.round_num     = round_num
        self.session_data  = {}
        self.driver_lookup = {}  # Store driver ID to name mapping
    
    def run(self):
        """Load all available session data including advanced data"""
        # First, load driver information for this season
        self.load_driver_info()
        
       # 2) Primary sessions
        primary = [
            ("Qualifying", f"{self.season}/{self.round_num}/qualifying.json"),
            ("Race",       f"{self.season}/{self.round_num}/results.json"),
            ("Sprint",     f"{self.season}/{self.round_num}/sprint.json"),
        ]

        # 3) Advanced sessions
        advanced = [
            ("Pit Stops",  f"{self.season}/{self.round_num}/pitstops.json"),
            ("Lap Times",  None),  # custom pagination below
        ]

        total = len(primary) + len(advanced)
        idx   = 0

        # Load primary sessions
        for name, endpoint in primary:
            idx += 1
            try:
                self.loading_progress.emit(f"Loading {name}... ({idx}/{total})")
                data    = self.ergast_client.get(endpoint)
                results = self.parse_session_data(data, name.lower())
                if results:
                    self.session_data[name] = results
                    self.session_loaded.emit(name, results)
                    logger.info(f"✅ Loaded {name}: {len(results)} entries")
                else:
                    logger.info(f"ℹ️ No data for {name}")
            except Exception as e:
                logger.error(f"❌ Error loading {name}: {e}")
                self.error_occurred.emit(name, str(e))

        # Load advanced sessions
        for name, endpoint in advanced:
            idx += 1
            try:
                self.loading_progress.emit(f"Loading {name}... ({idx}/{total})")

               # --- LAP TIMES PAGINATION FIX ---
                if name == "Lap Times":
                    all_laps: List[Dict[str, Any]] = []
                    limit = 30

                    # 1) First request to discover the total number of lap entries
                    first_url = f"{self.season}/{self.round_num}/laps.json?limit={limit}"
                    logger.info(f"Fetching first page: {first_url}")
                    first_page = self.ergast_client.get(first_url)

                    # 2) Drill into MRData.total
                    races = (
                        first_page.get("MRData", {})
                                  .get("RaceTable", {})
                                  .get("Races", [])
                    )
                    if races and races[0]:
                        try:
                            total_entries = int(first_page["MRData"].get("total", "0"))
                        except ValueError:
                            total_entries = len(races[0].get("Laps", []))

                        # 3) Compute how many pages we need
                        pages = (total_entries + limit - 1) // limit

                        # 4) Loop through every page
                        for page in range(pages):
                            offset = page * limit
                            url = (
                                f"{self.season}/{self.round_num}/laps.json"
                                f"?limit={limit}&offset={offset}"
                            )
                            logger.info(f"Fetching page {page+1}/{pages}: {url}")
                            page_data = self.ergast_client.get(url)

                            races = (
                                page_data.get("MRData", {})
                                         .get("RaceTable", {})
                                         .get("Races", [])
                            )
                            if not races or not races[0]:
                                continue
                            
                            laps = races[0].get("Laps", [])
                            logger.info(f"Page {page+1}: {len(laps)} laps")
                            all_laps.extend(laps)

                    # 5) Return the full list of laps
                    results = all_laps


                else:
                    # Pit Stops or others
                    data    = self.ergast_client.get(endpoint)
                    results = self.parse_advanced_data(data, name.lower())

                # enrich pit stops
                if name == "Pit Stops" and results:
                    results = self.enrich_pit_stops_data(results)

                # emit if any
                if results:
                    self.session_data[name] = results
                    self.session_loaded.emit(name, results)
                    logger.info(f"✅ Loaded {name}: {len(results)} entries")
                else:
                    logger.info(f"ℹ️ No data for {name}")

            except Exception as e:
                logger.error(f"❌ Error loading {name}: {e}")
                self.error_occurred.emit(name, str(e))

        # 4) OpenF1 extras (unchanged)
        self.load_openf1_data()

        # 5) done
        self.all_sessions_loaded.emit(self.session_data)
        self.loading_finished.emit()
    
    def load_driver_info(self):
        """Load driver information for ID to name mapping"""
        try:
            # Get driver standings to have a driver ID to name mapping
            data = self.ergast_client.get(f"{self.season}/driverStandings.json")
            if data and 'MRData' in data:
                standings_lists = data['MRData']['StandingsTable'].get('StandingsLists', [])
                if standings_lists:
                    for driver_data in standings_lists[0].get('DriverStandings', []):
                        driver = driver_data.get('Driver', {})
                        driver_id = driver.get('driverId', '')
                        if driver_id:
                            self.driver_lookup[driver_id] = {
                                'givenName': driver.get('givenName', ''),
                                'familyName': driver.get('familyName', ''),
                                'full_name': f"{driver.get('givenName', '')} {driver.get('familyName', '')}"
                            }
                    logger.info(f"✅ Loaded driver info: {len(self.driver_lookup)} drivers")
        except Exception as e:
            logger.warning(f"Could not load driver info: {e}")
    
    def enrich_pit_stops_data(self, pit_stops: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Enrich pit stops data with driver names from lookup"""
        enriched_stops = []
        for stop in pit_stops:
            enriched_stop = stop.copy()
            driver_id = stop.get('driverId', '')
            
            if driver_id and driver_id in self.driver_lookup:
                # Add proper driver information
                enriched_stop['driver'] = self.driver_lookup[driver_id]
            else:
                # Fallback: try to format the driver ID
                enriched_stop['driver'] = {
                    'givenName': driver_id.capitalize(),
                    'familyName': '',
                    'full_name': driver_id.capitalize()
                }
            
            enriched_stops.append(enriched_stop)
        
        return enriched_stops
    
    def load_openf1_data(self):
        """Load additional data from OpenF1 API"""
        try:
            self.loading_progress.emit("Loading additional OpenF1 data...")
            
            # Get sessions from OpenF1
            sessions = self.openf1_client.get_sessions(int(self.season))
            
            # Try to get car data
            if sessions:
                logger.info(f"✅ OpenF1 connected: {len(sessions)} sessions available")
                # You can extend this to get car_data
                # car_data = self.openf1_client.get_car_data()
            
        except Exception as e:
            logger.warning(f"OpenF1 data not available: {e}")
    
    def parse_session_data(self, data: Dict[str, Any], session_type: str) -> List[Dict[str, Any]]:
        """Parse standard session data"""
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
            elif session_type == "race":
                return race_data.get('Results', [])
            elif session_type == "sprint":
                return race_data.get('SprintResults', [])
            
            return []
            
        except Exception as e:
            logger.error(f"Error parsing {session_type} data: {e}")
            return []
    
    def parse_advanced_data(self, data: Dict[str, Any], data_type: str) -> List[Dict[str, Any]]:
        """Parse advanced data like pit stops and laps"""
        try:
            if not data or 'MRData' not in data:
                return []
            
            race_table = data['MRData']['RaceTable']
            if 'Races' not in race_table or not race_table['Races']:
                return []
            
            race_data = race_table['Races'][0]
            
            if "pit" in data_type:
                return race_data.get('PitStops', [])
            elif "lap" in data_type:
                return race_data.get('Laps', [])
            
            return []
            
        except Exception as e:
            logger.error(f"Error parsing {data_type} data: {e}")
            return []

class EnhancedDataService(QObject):
    """Enhanced service with complete F1 API integration"""
    def __init__(self):
        super().__init__()
        self.ergast_client = ErgastAPIClient()
        self.openf1_client = OpenF1Client()
    
    def get_current_f1_standings(self) -> List[DriverStanding]:
        """Get current F1 driver standings"""
        try:
            data = self.ergast_client.get_current_driver_standings()
            standings_data = data['MRData']['StandingsTable']['StandingsLists'][0]['DriverStandings']
            
            standings = []
            for standing_data in standings_data:
                standing = DriverStanding.from_ergast_data(standing_data)
                standings.append(standing)
            
            logger.info(f"✅ Loaded {len(standings)} driver standings")
            return standings
            
        except APIException as e:
            logger.error(f"❌ Error getting F1 standings: {e}")
            raise
        except (KeyError, IndexError) as e:
            logger.error(f"❌ Error parsing F1 standings data: {e}")
            raise Exception("Error parsing F1 standings data")
    
    def get_season_race_calendar(self, season: str) -> List[Race]:
        """Get race calendar with enhanced data"""
        try:
            data = self.ergast_client.get(f"{season}.json")
            races_data = data['MRData']['RaceTable']['Races']

            races: List[Race] = []
            for race in races_data:
                try:
                    # Try to get race results
                    results = self.ergast_client.get_race_results(season, race['round'])
                except APIException:
                    results = None

                race_obj = Race.from_ergast_data(season, race, results)
                races.append(race_obj)

            logger.info(f"✅ Loaded {len(races)} races for {season}")
            return races

        except APIException as e:
            logger.error(f"❌ Error getting race calendar: {e}")
            raise
        except Exception as e:
            logger.error(f"❌ Error parsing race calendar: {e}")
            raise Exception("Error parsing race calendar")
    
    def create_complete_session_loader(self, season: str, round_num: str):
        return CompleteSessionDataLoader(self.ergast_client, self.openf1_client, season, round_num)
    
    def create_career_stats_loader(self, driver_id: str):
        return CareerStatsLoader(self.ergast_client, driver_id)
    
    def get_all_2025_data(self) -> Dict[str, Any]:
        """Get comprehensive 2025 season data"""
        try:
            season_data = {}
            
            # Get races
            races_data = self.ergast_client.get("2025.json")
            season_data['races'] = races_data.get('MRData', {}).get('RaceTable', {}).get('Races', [])
            
            # Get all results
            results_data = self.ergast_client.get("2025/results.json")
            season_data['results'] = results_data.get('MRData', {}).get('RaceTable', {}).get('Races', [])
            
            # Get all qualifying
            qualifying_data = self.ergast_client.get("2025/qualifying.json")
            season_data['qualifying'] = qualifying_data.get('MRData', {}).get('RaceTable', {}).get('Races', [])
            
            # Get all sprint results
            try:
                sprint_data = self.ergast_client.get("2025/sprint.json")
                season_data['sprint'] = sprint_data.get('MRData', {}).get('RaceTable', {}).get('Races', [])
            except:
                season_data['sprint'] = []
            
            logger.info(f"✅ Loaded complete 2025 season data")
            return season_data
            
        except Exception as e:
            logger.error(f"❌ Error loading 2025 season data: {e}")
            return {}
    
    def check_data_availability(self, season: str = "2025") -> Dict[str, bool]:
        """Check which data types are available"""
        availability = {}
        
        endpoints_to_check = [
            ("races", f"{season}.json"),
            ("results", f"{season}/results.json"),
            ("qualifying", f"{season}/qualifying.json"),
            ("sprint", f"{season}/sprint.json"),
            ("standings", f"{season}/driverStandings.json"),
        ]
        
        for endpoint_name, endpoint_url in endpoints_to_check:
            try:
                data = self.ergast_client.get(endpoint_url)
                availability[endpoint_name] = bool(data and 'MRData' in data)
                logger.info(f"✅ {endpoint_name} data available")
            except Exception as e:
                availability[endpoint_name] = False
                logger.info(f"❌ {endpoint_name} data not available: {e}")
        
        # Check OpenF1 availability
        try:
            openf1_sessions = self.openf1_client.get_sessions(int(season))
            availability['openf1'] = len(openf1_sessions) > 0
            logger.info(f"✅ OpenF1 data available: {len(openf1_sessions)} sessions")
        except Exception as e:
            availability['openf1'] = False
            logger.info(f"❌ OpenF1 not available: {e}")
        
        return availability