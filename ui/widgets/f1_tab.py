# ui/widgets/f1_tab.py
"""
F1 widget with dark theme and podium display functionality

This module provides the complete F1 user interface including standings
and calendar tabs with dark theming, podium visualization, and automatic
data loading capabilities for a modern motorsport dashboard experience.

**Classes:**
    DarkTable - Dark themed table widget for data display
    DarkButton - Dark themed button with primary/secondary styling
    PodiumWidget - Widget for displaying race podium results
    StandingsTab - Tab for displaying F1 championship standings
    CalendarTab - Tab for displaying F1 race calendar with results
    F1TabWidget - Main F1 widget container with tabbed interface

**Author:** Lotherd
**Version:** 1.0.0
"""

from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QTableWidget,
    QTableWidgetItem,
    QMessageBox,
    QHeaderView,
    QTabWidget,
    QFrame,
    QApplication,
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QFont, QColor

from models.driver import DriverStanding
from models.race import Race
from services.data_service import DataService, DataLoader, CalendarLoader
from utils.i18n import tr
from typing import List
import logging

logger = logging.getLogger(__name__)

class DarkTable(QTableWidget):
    """Dark theme minimalist table widget for motorsport data display"""
    
    """
    * Initializes the dark themed table widget with styling
    *
    * This constructor creates a table widget with dark theme styling optimized
    * for motorsport data display including alternating row colors, custom
    * scroll bars, and F1-themed selection colors.
    *
    * **@return** None
    """
    def __init__(self):
        super().__init__()
        self.setup_dark_style()
    
    """
    * Applies comprehensive dark theme styling to the table widget
    *
    * This method configures all visual aspects of the table including background
    * colors, grid lines, headers, selection highlighting, and scroll bar styling
    * to create a cohesive dark theme experience.
    *
    * **@return** None
    """
    def setup_dark_style(self):
        self.setStyleSheet("""
            QTableWidget {
                background-color: #1a1a1a;
                gridline-color: #333333;
                color: #ffffff;
                border: 1px solid #333333;
                border-radius: 8px;
                selection-background-color: #e10600;
                selection-color: #ffffff;
                font-size: 14px;
                font-weight: 400;
            }
            QHeaderView::section {
                background-color: #e10600;
                color: #ffffff;
                padding: 16px 12px;
                border: none;
                border-bottom: 2px solid #333333;
                font-weight: 700;
                font-size: 12px;
                text-transform: uppercase;
                letter-spacing: 1px;
            }
            QTableWidget::item {
                padding: 14px 12px;
                border-bottom: 1px solid #2a2a2a;
                border-right: none;
                background-color: #1a1a1a;
            }
            QTableWidget::item:alternate {
                background-color: #1f1f1f;
            }
            QTableWidget::item:selected {
                background-color: #e10600;
                color: #ffffff;
                font-weight: 500;
            }
            QTableWidget::item:hover {
                background-color: #2a2a2a;
            }
            QScrollBar:vertical {
                background-color: #2a2a2a;
                width: 8px;
                border-radius: 4px;
                margin: 0;
            }
            QScrollBar::handle:vertical {
                background-color: #666666;
                border-radius: 4px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #e10600;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)
        
        self.setAlternatingRowColors(True)
        self.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.setSortingEnabled(False)
        self.verticalHeader().setVisible(False)

class DarkButton(QPushButton):
    """Dark theme minimalist button with primary and secondary styling options"""
    
    """
    * Initializes a dark themed button with specified styling type
    *
    * This constructor creates a button with dark theme styling that can be
    * configured as either a primary (filled) or secondary (outlined) button
    * based on the design requirements.
    *
    * **@param** text String text to display on the button
    * **@param** primary Boolean indicating if this is a primary button
    * **@return** None
    """
    def __init__(self, text: str, primary: bool = True):
        super().__init__(text)
        self.setup_dark_style(primary)
    
    """
    * Applies dark theme styling based on button type (primary or secondary)
    *
    * This method configures the button's visual appearance including colors,
    * borders, padding, and hover effects based on whether it's designated
    * as a primary or secondary button.
    *
    * **@param** primary Boolean indicating primary (True) or secondary (False) styling
    * **@return** None
    """
    def setup_dark_style(self, primary: bool):
        if primary:
            self.setStyleSheet("""
                QPushButton {
                    background-color: #e10600;
                    color: #ffffff;
                    border: none;
                    padding: 12px 24px;
                    font-size: 14px;
                    font-weight: 600;
                    border-radius: 6px;
                    min-width: 120px;
                    text-transform: uppercase;
                    letter-spacing: 0.5px;
                }
                QPushButton:hover {
                    background-color: #ff1a0a;
                }
                QPushButton:pressed {
                    background-color: #b30500;
                }
                QPushButton:disabled {
                    background-color: #555555;
                    color: #888888;
                }
            """)
        else:
            self.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    color: #ffffff;
                    border: 1px solid #555555;
                    padding: 12px 24px;
                    font-size: 14px;
                    font-weight: 500;
                    border-radius: 6px;
                    min-width: 120px;
                }
                QPushButton:hover {
                    background-color: #2a2a2a;
                    border-color: #e10600;
                    color: #e10600;
                }
                QPushButton:pressed {
                    background-color: #1a1a1a;
                }
                QPushButton:disabled {
                    background-color: #1a1a1a;
                    color: #555555;
                    border-color: #333333;
                }
            """)

class PodiumWidget(QWidget):
    """Widget for displaying race podium results with gold, silver, bronze styling"""
    
    """
    * Initializes the podium display widget with driver names
    *
    * This constructor creates a widget that displays the race podium (top 3
    * finishers) with appropriate gold, silver, and bronze styling to
    * clearly indicate the finishing positions.
    *
    * **@param** podium_list List of driver names in finishing order
    * **@return** None
    """
    def __init__(self, podium_list: List[str]):
        super().__init__()
        self.podium_list = podium_list
        self.setup_ui()
    
    """
    * Sets up the podium display UI with colored position indicators
    *
    * This method creates the visual layout for the podium display including
    * colored labels for each position (gold for 1st, silver for 2nd, bronze
    * for 3rd) and handles cases where podium data is not available.
    *
    * **@return** None
    """
    def setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        
        colors = ['#FFD700', '#C0C0C0', '#CD7F32']  # Gold, Silver, Bronze
        positions = ['🥇', '🥈', '🥉']
        
        for i, driver in enumerate(self.podium_list[:3]):
            if i < len(colors):
                podium_label = QLabel(f"{positions[i]} {driver}")
                podium_label.setStyleSheet(f"""
                    QLabel {{
                        color: {colors[i]};
                        font-weight: 600;
                        font-size: 13px;
                        padding: 4px 8px;
                        background-color: #2a2a2a;
                        border-radius: 4px;
                        border-left: 3px solid {colors[i]};
                    }}
                """)
                layout.addWidget(podium_label)
        
        if len(self.podium_list) == 0:
            tbd_label = QLabel("TBD")
            tbd_label.setStyleSheet("""
                QLabel {
                    color: #666666;
                    font-style: italic;
                    font-size: 13px;
                    padding: 4px 8px;
                }
            """)
            layout.addWidget(tbd_label)

class StandingsTab(QWidget):
    """Dark theme standings tab with automatic data loading capabilities"""
    
    status_updated = pyqtSignal(str)
    
    """
    * Initializes the F1 standings tab with data service integration
    *
    * This constructor sets up the standings tab with dark theme styling and
    * prepares the data loading infrastructure for automatic F1 championship
    * standings retrieval and display.
    *
    * **@param** data_service DataService instance for API operations
    * **@return** None
    """
    def __init__(self, data_service):
        super().__init__()
        self.data_service = data_service
        self.data_loader = None
        self.current_standings = []
        self.has_loaded = False
        self.setup_ui()
    
    """
    * Sets up the complete UI layout for the standings tab
    *
    * This method creates the dark themed user interface including the title,
    * status display, and standings table. It also initiates automatic data
    * loading when the tab becomes visible.
    *
    * **@return** None
    """
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(20)
        
        # Dark background
        self.setStyleSheet("""
            QWidget {
                background-color: #0f0f0f;
                color: #ffffff;
            }
        """)
        
        # Header without refresh button
        header_layout = QVBoxLayout()
        
        title_label = QLabel("Championship Standings")
        title_label.setStyleSheet("""
            QLabel {
                font-size: 28px;
                font-weight: 300;
                color: #ffffff;
                margin-bottom: 10px;
                letter-spacing: 1px;
            }
        """)
        header_layout.addWidget(title_label)
        
        layout.addLayout(header_layout)
        
        # Status bar with dark theme
        self.status_label = QLabel("Loading standings...")
        self.status_label.setStyleSheet("""
            QLabel {
                color: #ffffff;
                font-size: 14px;
                padding: 12px 16px;
                background-color: #2a2a2a;
                border-radius: 6px;
                border-left: 4px solid #ffc107;
            }
        """)
        layout.addWidget(self.status_label)
        
        # Standings table
        self.standings_table = DarkTable()
        self.setup_standings_table()
        layout.addWidget(self.standings_table)
        
        # Auto-load when tab becomes visible
        QTimer.singleShot(500, self.auto_load_if_needed)
    
    """
    * Automatically loads standings data if not already loaded
    *
    * This method checks if standings data has been loaded and initiates
    * the loading process if needed. It prevents redundant API calls while
    * ensuring data is available when the tab is accessed.
    *
    * **@return** None
    """
    def auto_load_if_needed(self):
        if not self.has_loaded:
            self.load_standings()
    
    """
    * Configures the standings table structure and column behavior
    *
    * This method sets up the table headers, column widths, and resize behavior
    * for optimal display of F1 championship standings data including position,
    * driver, team, points, wins, and nationality information.
    *
    * **@return** None
    """
    def setup_standings_table(self):
        self.standings_table.setColumnCount(6)
        
        headers = ["POS", "DRIVER", "TEAM", "POINTS", "WINS", "NATIONALITY"]
        self.standings_table.setHorizontalHeaderLabels(headers)
        
        # Configure column behavior
        header = self.standings_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)         # Position
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Interactive)   # Driver
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Interactive)   # Team
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)         # Points
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Fixed)         # Wins
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.Stretch)       # Nationality
        
        # Set column widths
        self.standings_table.setColumnWidth(0, 60)
        self.standings_table.setColumnWidth(1, 200)
        self.standings_table.setColumnWidth(2, 180)
        self.standings_table.setColumnWidth(3, 80)
        self.standings_table.setColumnWidth(4, 60)
    
    """
    * Initiates background loading of F1 championship standings
    *
    * This method starts the background data loading process using a separate
    * thread to prevent UI blocking. It sets up signal connections for
    * progress updates and result handling.
    *
    * **@return** None
    """
    def load_standings(self):
        if self.data_loader and self.data_loader.isRunning():
            return
        
        self.data_loader = DataLoader(self.data_service)
        self.data_loader.loading_started.connect(self.on_loading_started)
        self.data_loader.data_loaded.connect(self.on_standings_loaded)
        self.data_loader.error_occurred.connect(self.on_error_occurred)
        self.data_loader.loading_finished.connect(self.on_loading_finished)
        self.data_loader.start()
    
    """
    * Handles the loading started event with UI status updates
    *
    * This method updates the UI to indicate that data loading has begun,
    * changing the status label appearance and emitting progress signals
    * for other components that may need to respond.
    *
    * **@return** None
    """
    def on_loading_started(self):
        self.status_label.setText("🔄 Loading standings...")
        self.status_label.setStyleSheet("""
            QLabel {
                color: #ffffff;
                font-size: 14px;
                padding: 12px 16px;
                background-color: #2a2a2a;
                border-radius: 6px;
                border-left: 4px solid #ffc107;
            }
        """)
        self.status_updated.emit("Loading F1 standings...")
    
    """
    * Processes successfully loaded standings data and updates the UI
    *
    * This method receives the loaded standings data, stores it locally,
    * updates the table display, and changes the status to indicate
    * successful completion of the loading operation.
    *
    * **@param** standings List of DriverStanding objects to display
    * **@return** None
    """
    def on_standings_loaded(self, standings: List[DriverStanding]):
        try:
            self.current_standings = standings
            self.has_loaded = True
            self.update_standings_table(standings)
            
            self.status_label.setText(f"✅ Loaded {len(standings)} drivers")
            self.status_label.setStyleSheet("""
                QLabel {
                    color: #ffffff;
                    font-size: 14px;
                    padding: 12px 16px;
                    background-color: #2a2a2a;
                    border-radius: 6px;
                    border-left: 4px solid #28a745;
                }
            """)
            
            self.status_updated.emit(f"Standings loaded - {len(standings)} drivers")
            
        except Exception as e:
            logger.error(f"Error updating table: {e}")
            self.on_error_occurred(f"Error displaying data: {str(e)}")
    
    """
    * Handles error conditions during data loading with appropriate UI feedback
    *
    * This method updates the UI to display error information when data loading
    * fails, changing the status label to use error styling and logging the
    * error for debugging purposes.
    *
    * **@param** error_message String description of the error that occurred
    * **@return** None
    """
    def on_error_occurred(self, error_message: str):
        self.status_label.setText(f"❌ {error_message}")
        self.status_label.setStyleSheet("""
            QLabel {
                color: #ffffff;
                font-size: 14px;
                padding: 12px 16px;
                background-color: #2a2a2a;
                border-radius: 6px;
                border-left: 4px solid #dc3545;
            }
        """)
        self.status_updated.emit(f"Error: {error_message}")
    
    """
    * Handles the completion of data loading operations
    *
    * This method is called when data loading finishes, regardless of success
    * or failure. It can be used for cleanup operations or final UI updates.
    *
    * **@return** None
    """
    def on_loading_finished(self):
        pass  # No refresh button to enable
    
    """
    * Updates the standings table with driver championship data and podium highlighting
    *
    * This method populates the table with standings data and applies special
    * highlighting for podium positions (1st, 2nd, 3rd) using gold, silver,
    * and bronze colors to make the championship leaders stand out.
    *
    * **@param** standings List of DriverStanding objects to display in the table
    * **@return** None
    """
    def update_standings_table(self, standings: List[DriverStanding]):
        self.standings_table.setRowCount(len(standings))
        
        for row, standing in enumerate(standings):
            # Position with podium highlighting
            pos_item = QTableWidgetItem(str(standing.position))
            pos_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            
            # Highlight podium positions
            if standing.position == 1:
                pos_item.setBackground(QColor("#FFD700"))
                pos_item.setForeground(QColor("#000000"))
                font = pos_item.font()
                font.setBold(True)
                pos_item.setFont(font)
            elif standing.position == 2:
                pos_item.setBackground(QColor("#C0C0C0"))
                pos_item.setForeground(QColor("#000000"))
                font = pos_item.font()
                font.setBold(True)
                pos_item.setFont(font)
            elif standing.position == 3:
                pos_item.setBackground(QColor("#CD7F32"))
                pos_item.setForeground(QColor("#000000"))
                font = pos_item.font()
                font.setBold(True)
                pos_item.setFont(font)
            
            self.standings_table.setItem(row, 0, pos_item)
            
            # Driver name
            driver_item = QTableWidgetItem(standing.driver.full_name)
            if standing.position <= 3:
                font = driver_item.font()
                font.setBold(True)
                driver_item.setFont(font)
            self.standings_table.setItem(row, 1, driver_item)
            
            # Team
            team_name = standing.constructors[0].name if standing.constructors else "N/A"
            team_item = QTableWidgetItem(team_name)
            self.standings_table.setItem(row, 2, team_item)
            
            # Points
            points_item = QTableWidgetItem(str(int(standing.points)))
            points_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            if standing.position <= 3:
                font = points_item.font()
                font.setBold(True)
                points_item.setFont(font)
            self.standings_table.setItem(row, 3, points_item)
            
            # Wins
            wins_item = QTableWidgetItem(str(standing.wins))
            wins_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.standings_table.setItem(row, 4, wins_item)
            
            # Nationality
            nat_item = QTableWidgetItem(standing.driver.nationality)
            self.standings_table.setItem(row, 5, nat_item)
        
        # Set row height
        self.standings_table.verticalHeader().setDefaultSectionSize(50)

class CalendarTab(QWidget):
    """Dark theme calendar tab with podium display and automatic data loading"""
    
    status_updated = pyqtSignal(str)
    
    """
    * Initializes the F1 race calendar tab with data service integration
    *
    * This constructor sets up the calendar tab with dark theme styling and
    * prepares the data loading infrastructure for automatic F1 race calendar
    * retrieval and podium results display.
    *
    * **@param** data_service DataService instance for API operations
    * **@return** None
    """
    def __init__(self, data_service):
        super().__init__()
        self.data_service = data_service
        self.calendar_loader = None
        self.current_calendar: List[Race] = []
        self.has_loaded = False
        self.setup_ui()
    
    """
    * Sets up the complete UI layout for the race calendar tab
    *
    * This method creates the dark themed user interface including the title,
    * status display, and calendar table with podium results. It also initiates
    * automatic data loading when the tab becomes visible.
    *
    * **@return** None
    """
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(20)
        
        # Dark background
        self.setStyleSheet("""
            QWidget {
                background-color: #0f0f0f;
                color: #ffffff;
            }
        """)
        
        # Header without refresh button
        header_layout = QVBoxLayout()
        
        title_label = QLabel("Race Calendar")
        title_label.setStyleSheet("""
            QLabel {
                font-size: 28px;
                font-weight: 300;
                color: #ffffff;
                margin-bottom: 10px;
                letter-spacing: 1px;
            }
        """)
        header_layout.addWidget(title_label)
        
        layout.addLayout(header_layout)
        
        # Status
        self.status_label = QLabel("Loading calendar...")
        self.status_label.setStyleSheet("""
            QLabel {
                color: #ffffff;
                font-size: 14px;
                padding: 12px 16px;
                background-color: #2a2a2a;
                border-radius: 6px;
                border-left: 4px solid #ffc107;
            }
        """)
        layout.addWidget(self.status_label)
        
        # Calendar table
        self.calendar_table = DarkTable()
        self.setup_calendar_table()
        layout.addWidget(self.calendar_table)
        
        # Auto-load when tab becomes visible
        QTimer.singleShot(1000, self.auto_load_if_needed)
    
    """
    * Automatically loads calendar data if not already loaded
    *
    * This method checks if calendar data has been loaded and initiates
    * the loading process if needed. It prevents redundant API calls while
    * ensuring data is available when the tab is accessed.
    *
    * **@return** None
    """
    def auto_load_if_needed(self):
        if not self.has_loaded:
            self.load_calendar()
    
    """
    * Configures the calendar table structure and column behavior
    *
    * This method sets up the table headers, column widths, and resize behavior
    * for optimal display of F1 race calendar data including round number,
    * race name, date, circuit, and podium results.
    *
    * **@return** None
    """
    def setup_calendar_table(self):
        self.calendar_table.setColumnCount(5)
        
        headers = ["ROUND", "GRAND PRIX", "DATE", "CIRCUIT", "PODIUM"]
        self.calendar_table.setHorizontalHeaderLabels(headers)
        
        # Configure calendar table columns
        cal_header = self.calendar_table.horizontalHeader()
        cal_header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)       # Round
        cal_header.setSectionResizeMode(1, QHeaderView.ResizeMode.Interactive) # GP Name
        cal_header.setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)       # Date
        cal_header.setSectionResizeMode(3, QHeaderView.ResizeMode.Interactive) # Circuit
        cal_header.setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)     # Podium
        
        # Set widths
        self.calendar_table.setColumnWidth(0, 80)
        self.calendar_table.setColumnWidth(1, 280)
        self.calendar_table.setColumnWidth(2, 120)
        self.calendar_table.setColumnWidth(3, 280)
    
    """
    * Initiates background loading of F1 race calendar for 2025 season
    *
    * This method starts the background data loading process using a separate
    * thread to prevent UI blocking. It sets up signal connections for
    * progress updates and result handling.
    *
    * **@return** None
    """
    def load_calendar(self):
        if self.calendar_loader and self.calendar_loader.isRunning():
            return
            
        season = "2025"
        self.calendar_loader = CalendarLoader(self.data_service, season)
        self.calendar_loader.loading_started.connect(self.on_loading_started)
        self.calendar_loader.calendar_loaded.connect(self.on_calendar_loaded)
        self.calendar_loader.error_occurred.connect(self.on_error_occurred)
        self.calendar_loader.loading_finished.connect(self.on_loading_finished)
        self.calendar_loader.start()
    
    """
    * Handles the calendar loading started event with UI status updates
    *
    * This method updates the UI to indicate that calendar loading has begun,
    * changing the status label appearance and emitting progress signals
    * for other components that may need to respond.
    *
    * **@return** None
    """
    def on_loading_started(self):
        self.status_label.setText("🔄 Loading race calendar...")
        self.status_label.setStyleSheet("""
            QLabel {
                color: #ffffff;
                font-size: 14px;
                padding: 12px 16px;
                background-color: #2a2a2a;
                border-radius: 6px;
                border-left: 4px solid #ffc107;
            }
        """)
        self.status_updated.emit("Loading race calendar...")
    
    """
    * Processes successfully loaded calendar data and updates the UI
    *
    * This method receives the loaded calendar data, stores it locally,
    * updates the table display with race information and podium results,
    * and changes the status to indicate successful completion.
    *
    * **@param** races List of Race objects containing calendar and results data
    * **@return** None
    """
    def on_calendar_loaded(self, races: List[Race]):
        try:
            self.current_calendar = races
            self.has_loaded = True
            self.update_calendar_table(races)
            
            self.status_label.setText(f"✅ Loaded {len(races)} races")
            self.status_label.setStyleSheet("""
                QLabel {
                    color: #ffffff;
                    font-size: 14px;
                    padding: 12px 16px;
                    background-color: #2a2a2a;
                    border-radius: 6px;
                    border-left: 4px solid #28a745;
                }
            """)
            
            self.status_updated.emit(f"Calendar loaded - {len(races)} races")
            
        except Exception as e:
            logger.error(f"Error updating calendar: {e}")
            self.on_error_occurred(f"Error displaying calendar: {str(e)}")
    
    """
    * Handles error conditions during calendar loading with appropriate UI feedback
    *
    * This method updates the UI to display error information when calendar
    * loading fails, changing the status label to use error styling and
    * logging the error for debugging purposes.
    *
    * **@param** error_message String description of the error that occurred
    * **@return** None
    """
    def on_error_occurred(self, error_message: str):
        self.status_label.setText(f"❌ {error_message}")
        self.status_label.setStyleSheet("""
            QLabel {
                color: #ffffff;
                font-size: 14px;
                padding: 12px 16px;
                background-color: #2a2a2a;
                border-radius: 6px;
                border-left: 4px solid #dc3545;
            }
        """)
        self.status_updated.emit(f"Error: {error_message}")
    
    """
    * Handles the completion of calendar loading operations
    *
    * This method is called when calendar loading finishes, regardless of
    * success or failure. It can be used for cleanup operations or final
    * UI updates.
    *
    * **@return** None
    """
    def on_loading_finished(self):
        pass  # No refresh button to enable
    
    """
    * Updates the calendar table with race data and embedded podium widgets
    *
    * This method populates the table with race calendar information and
    * creates embedded podium widgets for each race to display the top 3
    * finishers when results are available.
    *
    * **@param** races List of Race objects containing race and results information
    * **@return** None
    """
    def update_calendar_table(self, races: List[Race]):
        self.calendar_table.setRowCount(len(races))
        
        for row, race in enumerate(races):
            # Round
            round_item = QTableWidgetItem(str(race.round))
            round_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.calendar_table.setItem(row, 0, round_item)
            
            # Race name
            name_item = QTableWidgetItem(race.race_name)
            self.calendar_table.setItem(row, 1, name_item)
            
            # Date
            date_item = QTableWidgetItem(race.date)
            date_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.calendar_table.setItem(row, 2, date_item)
            
            # Circuit
            circuit_item = QTableWidgetItem(race.circuit)
            self.calendar_table.setItem(row, 3, circuit_item)
            
            # Podium widget
            podium_widget = PodiumWidget(race.podium)
            self.calendar_table.setCellWidget(row, 4, podium_widget)
        
        # Set row height to accommodate podium widget
        self.calendar_table.verticalHeader().setDefaultSectionSize(60)

class F1TabWidget(QWidget):
    """Main F1 widget container with dark themed tabbed interface and auto-loading"""
    
    status_updated = pyqtSignal(str)
    
    """
    * Initializes the main F1 widget with data service and tab structure
    *
    * This constructor creates the main F1 interface container with tabbed
    * navigation between standings and calendar views, dark theme styling,
    * and integrated data service for API operations.
    *
    * **@return** None
    """
    def __init__(self):
        super().__init__()
        self.data_service = DataService()
        self.setup_ui()
    
    """
    * Sets up the complete dark themed tabbed interface for F1 data
    *
    * This method creates the main UI structure including the dark styled
    * tab widget, individual tabs for standings and calendar, and connects
    * the status update signals for coordinated UI feedback.
    *
    * **@return** None
    """
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Dark background for main widget
        self.setStyleSheet("""
            QWidget {
                background-color: #0f0f0f;
                color: #ffffff;
            }
        """)
        
        # Dark tab widget
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: none;
                background-color: #0f0f0f;
            }
            QTabBar {
                background-color: #1a1a1a;
            }
            QTabBar::tab {
                background-color: #2a2a2a;
                color: #cccccc;
                padding: 15px 30px;
                margin-right: 2px;
                border: none;
                font-size: 14px;
                font-weight: 500;
                min-width: 120px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
            }
            QTabBar::tab:selected {
                background-color: #0f0f0f;
                color: #e10600;
                border-bottom: 3px solid #e10600;
                font-weight: 600;
            }
            QTabBar::tab:hover:!selected {
                background-color: #333333;
                color: #ffffff;
            }
        """)
        
        # Create tabs
        self.standings_tab = StandingsTab(self.data_service)
        self.calendar_tab = CalendarTab(self.data_service)
        
        # Connect status signals
        self.standings_tab.status_updated.connect(self.status_updated.emit)
        self.calendar_tab.status_updated.connect(self.status_updated.emit)
        
        # Add tabs with icons
        self.add_tab_with_icon(self.standings_tab, "logo/standing.png", "Standings")
        self.add_tab_with_icon(self.calendar_tab, "logo/calendar.png", "Calendar")
        
        layout.addWidget(self.tab_widget)
    
    """
    * Adds a tab to the widget with an optional PNG icon
    *
    * This method attempts to load and display a PNG icon for the tab while
    * gracefully falling back to text-only display if the icon cannot be
    * loaded. It processes the icon to create a white version for dark theme.
    *
    * **@param** widget QWidget to be added as tab content
    * **@param** icon_path String path to the PNG icon file
    * **@param** text String display text for the tab
    * **@return** None
    """
    def add_tab_with_icon(self, widget, icon_path, text):
        import os
        from PyQt6.QtGui import QIcon, QPixmap, QPainter
        from PyQt6.QtCore import QSize
        
        if os.path.exists(icon_path):
            # Load and process icon
            pixmap = QPixmap(icon_path)
            if not pixmap.isNull():
                # Scale icon
                scaled_pixmap = pixmap.scaled(
                    16, 16,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )
                
                # Create white version
                white_pixmap = QPixmap(scaled_pixmap.size())
                white_pixmap.fill(Qt.GlobalColor.transparent)
                
                painter = QPainter(white_pixmap)
                painter.setRenderHint(QPainter.RenderHint.Antialiasing)
                painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceOver)
                painter.drawPixmap(0, 0, scaled_pixmap)
                painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceIn)
                painter.fillRect(white_pixmap.rect(), QColor(255, 255, 255))
                painter.end()
                
                # Set tab with icon
                icon = QIcon(white_pixmap)
                self.tab_widget.addTab(widget, icon, text)
            else:
                # Fallback without icon
                self.tab_widget.addTab(widget, text)
        else:
            # Fallback without icon
            self.tab_widget.addTab(widget, text)
    
    """
    * Automatically loads initial F1 data when the widget becomes active
    *
    * This method is called to trigger automatic data loading for the F1
    * tabs. The actual loading is handled by individual tabs when they
    * become visible to optimize performance.
    *
    * **@return** None
    """
    def auto_load_initial_data(self):
        # The standings tab will auto-load when it becomes visible
        pass
    
    """
    * Updates all translatable text elements when language changes
    *
    * This method refreshes all user-visible text in the F1 widget including
    * tab titles and table headers to reflect the currently selected language
    * setting in the application.
    *
    * **@return** None
    """
    def update_translations(self):
        # Update tab titles
        self.tab_widget.setTabText(0, "Standings")
        self.tab_widget.setTabText(1, "Calendar")
        
        # Update table headers in both tabs
        standings_headers = ["POS", "DRIVER", "TEAM", "POINTS", "WINS", "NATIONALITY"]
        self.standings_tab.standings_table.setHorizontalHeaderLabels(standings_headers)
        
        calendar_headers = ["ROUND", "GRAND PRIX", "DATE", "CIRCUIT", "PODIUM"]
        self.calendar_tab.calendar_table.setHorizontalHeaderLabels(calendar_headers)