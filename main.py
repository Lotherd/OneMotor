# main.py
"""
Main entry point for the F1 & MotoGP Dashboard application

This module serves as the application's entry point, handling initialization,
logging setup, and the main event loop for the PyQt6 motorsport dashboard.

**Classes:**
    None (Module contains standalone functions)

**Author:** Motorsport Apps Team
**Version:** 1.0.0
"""

import sys
import logging
from pathlib import Path
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt


"""
* Configures the application's logging system with file and console output
*
* This function sets up a comprehensive logging system that writes to both
* a log file and the console. It creates the logs directory if it doesn't exist
* and configures formatters for readable log messages.
*
* **@return** Logger instance for the main module
"""
def setup_logging():
    # Create logs directory if it doesn't exist
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Logging configuration
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_dir / "app.log", encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # Main logger
    logger = logging.getLogger(__name__)
    logger.info("Logging system initialized")
    return logger


"""
* Configures and creates the main Qt application instance
*
* This function creates the QApplication instance and sets basic application
* metadata including name, version, and organization. PyQt6 automatically
* handles DPI scaling, so no additional configuration is needed.
*
* **@return** Configured QApplication instance
"""
def setup_application():
    # Create application
    app = QApplication(sys.argv)
    
    # Application settings
    app.setApplicationName("F1 & MotoGP Dashboard")
    app.setApplicationVersion("1.0")
    app.setOrganizationName("MotorsportApps")
    
    # PyQt6 automatically handles DPI scaling
    # No additional configuration needed
    
    return app


"""
* Creates necessary application directories if they don't exist
*
* This function ensures that all required directories for the application
* are present, including logs, data cache, and temporary storage directories.
*
* **@return** None
"""
def create_directories():
    directories = ["logs", "data", "cache"]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)


"""
* Main application entry point and execution controller
*
* This function orchestrates the entire application startup process including
* logging initialization, directory creation, Qt application setup, and the
* main window creation. It handles all exceptions and returns appropriate
* exit codes.
*
* **@return** Integer exit code (0 for success, 1 for error)
"""
def main():
    try:
        # Configure logging
        logger = setup_logging()
        logger.info("Starting F1 & MotoGP Dashboard application")
        
        # Create necessary directories
        create_directories()
        logger.info("Application directories created")
        
        # Configure Qt application
        app = setup_application()
        logger.info("Qt application configured")
        
        # Import and create main window
        from ui.main_window import MainWindow
        
        window = MainWindow()
        window.show()
        
        logger.info("Main window created and shown")
        logger.info("Application ready - entering event loop")
        
        # Run application
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