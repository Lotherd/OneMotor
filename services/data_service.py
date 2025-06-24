import logging
from typing import List, Optional
from PyQt6.QtCore import QObject, pyqtSignal, QThread

from models.driver import DriverStanding, Driver, Constructor
from models.race import Race
from services.api_client import ErgastAPIClient, APIException

logger = logging.getLogger(__name__)

class DataService(QObject):
    """Main service for data management"""
    
    def __init__(self):
        super().__init__()
        self.ergast_client = ErgastAPIClient()
    
    def get_current_f1_standings(self) -> List[DriverStanding]:
        """Get current F1 standings"""
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

    def get_season_race_calendar(self, season: str) -> List[Race]:
        """Get race calendar with podium results for a season"""
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
    """Worker thread to load data without blocking the UI"""
    
    # Signals
    data_loaded = pyqtSignal(list)  # List of DriverStanding
    error_occurred = pyqtSignal(str)  # Error message
    loading_started = pyqtSignal()
    loading_finished = pyqtSignal()
    
    def __init__(self, data_service: DataService):
        super().__init__()
        self.data_service = data_service
    
    def run(self):
        """Execute data loading in separate thread"""
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

class DataParsingException(Exception):
    """Exception for data parsing errors"""
    pass


class CalendarLoader(QThread):
    """Thread to load race calendar"""

    calendar_loaded = pyqtSignal(list)  # List of Race
    error_occurred = pyqtSignal(str)
    loading_started = pyqtSignal()
    loading_finished = pyqtSignal()

    def __init__(self, data_service: DataService, season: str):
        super().__init__()
        self.data_service = data_service
        self.season = season

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