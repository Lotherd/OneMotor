# services/data_service.py
"""
Data service layer with background threading for non-blocking UI operations

This module provides the main data service for managing F1 data retrieval
and processing. It includes background worker threads to prevent UI blocking
during API calls and data processing operations.

**Classes:**
    DataService - Main service for data management and API coordination
    DataLoader - Background thread worker for loading driver standings
    CalendarLoader - Background thread worker for loading race calendar
    DataParsingException - Custom exception for data processing errors

**Author:** Lotherd
**Version:** 1.0.0
"""

import logging
from typing import List, Optional
from PyQt6.QtCore import QObject, pyqtSignal, QThread

from models.driver import DriverStanding, Driver, Constructor
from models.race import Race
from services.api_client import ErgastAPIClient, APIException

logger = logging.getLogger(__name__)

class DataService(QObject):
    """Main service for coordinating F1 data management and API interactions"""
    
    """
    * Initializes the data service with API client setup
    *
    * This constructor creates the main data service instance and initializes
    * the Ergast API client for F1 data retrieval. It sets up the foundation
    * for all data operations in the application.
    *
    * **@return** None
    """
    def __init__(self):
        super().__init__()
        self.ergast_client = ErgastAPIClient()
    
    """
    * Retrieves and processes current F1 driver championship standings
    *
    * This method fetches the latest F1 driver standings from the API and
    * converts the raw data into structured DriverStanding objects. It handles
    * API errors and data parsing exceptions appropriately.
    *
    * **@return** List of DriverStanding objects ordered by championship position
    * **@throws** APIException for API communication failures
    * **@throws** DataParsingException for data structure parsing errors
    """
    def get_current_f1_standings(self) -> List[DriverStanding]:
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
            raise DataParsingException("Error parsing F1 standings data")

    """
    * Retrieves race calendar with podium results for a specified season
    *
    * This method fetches the complete race calendar for a given season and
    * attempts to load race results for each completed race to display podium
    * information. It gracefully handles missing results data.
    *
    * **@param** season String representing the F1 season year
    * **@return** List of Race objects with available podium information
    * **@throws** APIException for API communication failures
    * **@throws** DataParsingException for data structure parsing errors
    """
    def get_season_race_calendar(self, season: str) -> List[Race]:
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
            raise DataParsingException("Error parsing race calendar")

class DataLoader(QThread):
    """Background worker thread for loading F1 standings without blocking the UI"""
    
    # Signals for communicating with the main thread
    data_loaded = pyqtSignal(list)  # List of DriverStanding
    error_occurred = pyqtSignal(str)  # Error message
    loading_started = pyqtSignal()
    loading_finished = pyqtSignal()
    
    """
    * Initializes the data loader thread with data service reference
    *
    * This constructor sets up the background worker thread that will handle
    * F1 standings data loading operations without blocking the user interface.
    *
    * **@param** data_service DataService instance for API operations
    * **@return** None
    """
    def __init__(self, data_service: DataService):
        super().__init__()
        self.data_service = data_service
    
    """
    * Executes F1 standings data loading in a separate background thread
    *
    * This method runs in a separate thread to load F1 standings data without
    * blocking the UI. It emits appropriate signals to communicate progress
    * and results back to the main thread.
    *
    * **@return** None (Results communicated via signals)
    """
    def run(self):
        try:
            self.loading_started.emit()
            
            # Load F1 standings
            standings = self.data_service.get_current_f1_standings()
            self.data_loaded.emit(standings)
            
        except APIException as e:
            error_msg = f"Connection error: {str(e)}"
            logger.error(error_msg)
            self.error_occurred.emit(error_msg)
            
        except DataParsingException as e:
            error_msg = f"Data processing error: {str(e)}"
            logger.error(error_msg)
            self.error_occurred.emit(error_msg)
            
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            logger.error(error_msg)
            self.error_occurred.emit(error_msg)
            
        finally:
            self.loading_finished.emit()

class CalendarLoader(QThread):
    """Background worker thread for loading F1 race calendar without blocking the UI"""

    # Signals for communicating with the main thread
    calendar_loaded = pyqtSignal(list)  # List of Race
    error_occurred = pyqtSignal(str)
    loading_started = pyqtSignal()
    loading_finished = pyqtSignal()

    """
    * Initializes the calendar loader thread with data service and season
    *
    * This constructor sets up the background worker thread that will handle
    * race calendar data loading operations for a specific season without
    * blocking the user interface.
    *
    * **@param** data_service DataService instance for API operations
    * **@param** season String representing the F1 season year to load
    * **@return** None
    """
    def __init__(self, data_service: DataService, season: str):
        super().__init__()
        self.data_service = data_service
        self.season = season

    """
    * Executes race calendar data loading in a separate background thread
    *
    * This method runs in a separate thread to load race calendar data for
    * the specified season without blocking the UI. It emits appropriate
    * signals to communicate progress and results back to the main thread.
    *
    * **@return** None (Results communicated via signals)
    """
    def run(self):
        try:
            self.loading_started.emit()
            races = self.data_service.get_season_race_calendar(self.season)
            self.calendar_loaded.emit(races)
        except APIException as e:
            err = f"Connection error: {str(e)}"
            logger.error(err)
            self.error_occurred.emit(err)
        except DataParsingException as e:
            err = f"Data processing error: {str(e)}"
            logger.error(err)
            self.error_occurred.emit(err)
        except Exception as e:
            err = f"Unexpected error: {str(e)}"
            logger.error(err)
            self.error_occurred.emit(err)
        finally:
            self.loading_finished.emit()

class DataParsingException(Exception):
    """Custom exception class for data parsing and processing errors"""
    pass