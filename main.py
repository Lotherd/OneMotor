# main.py
"""
Punto de entrada principal de la aplicación F1 & MotoGP Dashboard
"""

import sys
import logging
from pathlib import Path
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt

# Configurar logging
def setup_logging():
    """Configurar sistema de logging"""
    
    # Crear directorio de logs si no existe
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Configuración de logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_dir / "app.log", encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # Logger principal
    logger = logging.getLogger(__name__)
    logger.info("Logging system initialized")
    return logger

def setup_application():
    """Configurar la aplicación Qt"""
    
    # Crear aplicación
    app = QApplication(sys.argv)
    
    # Configuraciones de la aplicación
    app.setApplicationName("F1 & MotoGP Dashboard")
    app.setApplicationVersion("1.0")
    app.setOrganizationName("MotorsportApps")
    
    # PyQt6 maneja automáticamente el DPI scaling
    # No necesitamos configuración adicional
    
    return app

def create_directories():
    """Crear directorios necesarios"""
    directories = ["logs", "data", "cache"]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)

def main():
    """Función principal"""
    
    try:
        # Configurar logging
        logger = setup_logging()
        logger.info("Starting F1 & MotoGP Dashboard application")
        
        # Crear directorios necesarios
        create_directories()
        logger.info("Application directories created")
        
        # Configurar aplicación Qt
        app = setup_application()
        logger.info("Qt application configured")
        
        # Importar y crear ventana principal
        from ui.main_window import MainWindow
        
        window = MainWindow()
        window.show()
        
        logger.info("Main window created and shown")
        logger.info("Application ready - entering event loop")
        
        # Ejecutar aplicación
        exit_code = app.exec()
        
        logger.info(f"Application exited with code: {exit_code}")
        return exit_code
        
    except ImportError as e:
        error_msg = f"Error importing required modules: {e}"
        print(error_msg)
        if 'logger' in locals():
            logger.error(error_msg)
        return 1
        
    except Exception as e:
        error_msg = f"Unexpected error: {e}"
        print(error_msg)
        if 'logger' in locals():
            logger.error(error_msg, exc_info=True)
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)