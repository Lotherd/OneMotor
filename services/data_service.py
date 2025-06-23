import logging
from typing import List, Optional
from PyQt6.QtCore import QObject, pyqtSignal, QThread

from models.driver import DriverStanding, Driver, Constructor
from services.api_client import ErgastAPIClient, APIException

logger = logging.getLogger(__name__)

class DataService(QObject):
    """Servicio principal para manejo de datos"""
    
    def __init__(self):
        super().__init__()
        self.ergast_client = ErgastAPIClient()
    
    def get_current_f1_standings(self) -> List[DriverStanding]:
        """Obtener standings actuales de F1"""
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

class DataLoader(QThread):
    """Worker thread para cargar datos sin bloquear la UI"""
    
    # Señales
    data_loaded = pyqtSignal(list)  # Lista de DriverStanding
    error_occurred = pyqtSignal(str)  # Mensaje de error
    loading_started = pyqtSignal()
    loading_finished = pyqtSignal()
    
    def __init__(self, data_service: DataService):
        super().__init__()
        self.data_service = data_service
    
    def run(self):
        """Ejecutar carga de datos en hilo separado"""
        try:
            self.loading_started.emit()
            
            # Cargar standings de F1
            standings = self.data_service.get_current_f1_standings()
            self.data_loaded.emit(standings)
            
        except APIException as e:
            error_msg = f"Error de conexión: {str(e)}"
            logger.error(error_msg)
            self.error_occurred.emit(error_msg)
            
        except DataParsingException as e:
            error_msg = f"Error procesando datos: {str(e)}"
            logger.error(error_msg)
            self.error_occurred.emit(error_msg)
            
        except Exception as e:
            error_msg = f"Error inesperado: {str(e)}"
            logger.error(error_msg)
            self.error_occurred.emit(error_msg)
            
        finally:
            self.loading_finished.emit()

class DataParsingException(Exception):
    """Excepción para errores de parsing de datos"""
    pass