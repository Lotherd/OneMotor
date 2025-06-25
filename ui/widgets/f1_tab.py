# ui/widgets/f1_tab.py
"""
Widget for Formula 1 tab with multi-language support - AUTO CALENDAR LOAD
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
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QColor

from models.driver import DriverStanding
from models.race import Race
from ui.styles.app_styles import AppStyles
from services.data_service import DataService, DataLoader, CalendarLoader
from utils.i18n import tr
from typing import List
import logging

logger = logging.getLogger(__name__)

class F1TabWidget(QWidget):
    """Main widget for F1 tab"""
    
    # Signals
    status_updated = pyqtSignal(str)  # To update status bar
    
    def __init__(self):
        super().__init__()
        self.data_service = DataService()
        self.data_loader = None
        self.calendar_loader = None
        self.current_standings = []
        self.current_calendar: List[Race] = []
        
        self.setup_ui()
        self.connect_signals()
    
    def setup_ui(self):
        """Configure user interface"""
        
        # Main layout
        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(16)
        
        # Title
        self.title_label = QLabel(tr("f1_title"))
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label.setStyleSheet(AppStyles.get_title_style(20))
        self.layout.addWidget(self.title_label)
        
        # Action bar
        self.setup_action_bar()
        
        # Loading status
        self.status_label = QLabel(tr("f1_ready"))
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet(AppStyles.get_status_label_style())
        self.layout.addWidget(self.status_label)
        
        # Standings table
        self.setup_standings_table()

        # Calendar table below standings
        self.setup_calendar_table()
    
    def setup_action_bar(self):
        """Configure action bar - REMOVED CALENDAR BUTTON"""
        action_layout = QHBoxLayout()
        
        # Refresh button
        self.refresh_button = QPushButton(tr("f1_refresh_button"))
        self.refresh_button.setStyleSheet(AppStyles.get_main_button_style())
        self.refresh_button.clicked.connect(self.load_all_data)  # CHANGED: Load all data
        action_layout.addWidget(self.refresh_button)
        
        # Export button (future)
        self.export_button = QPushButton(tr("f1_export_button"))
        self.export_button.setStyleSheet(AppStyles.get_secondary_button_style())
        self.export_button.setEnabled(False)  # Disabled for now
        action_layout.addWidget(self.export_button)
        
        # Spacer
        action_layout.addStretch()
        
        # Season info
        self.season_label = QLabel(tr("f1_season"))
        self.season_label.setStyleSheet(f"""
            QLabel {{
                color: #666;
                font-size: 14px;
                font-weight: bold;
                padding: 8px;
            }}
        """)
        action_layout.addWidget(self.season_label)
        
        self.layout.addLayout(action_layout)
    
    def setup_standings_table(self):
        """Configure standings table with improved column handling"""
        self.standings_table = QTableWidget()
        self.standings_table.setColumnCount(7)
        
        # Translated headers
        headers = [
            tr("table_pos"),
            tr("table_driver"),
            tr("table_team"),
            tr("table_points"),
            tr("table_wins"),
            tr("table_nationality"),
            tr("table_code")
        ]
        self.standings_table.setHorizontalHeaderLabels(headers)
        
        # Apply styles
        self.standings_table.setStyleSheet(AppStyles.get_table_style())
        
        # Additional configuration
        self.standings_table.setAlternatingRowColors(True)
        self.standings_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.standings_table.setSortingEnabled(True)
        
        # FIXED: Better header configuration
        header = self.standings_table.horizontalHeader()
        
        # Set specific column widths that work better
        header.setMinimumSectionSize(60)  # Minimum width for any column
        
        # Set resize modes for better column behavior
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)         # Position - Fixed width
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Interactive)   # Driver - User can resize
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Interactive)   # Team - User can resize  
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)         # Points - Fixed width
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Fixed)         # Wins - Fixed width
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.Stretch)       # Nationality - Fill remaining
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.Fixed)         # Code - Fixed width
        
        # Set specific column widths
        self.standings_table.setColumnWidth(0, 60)   # Position - wider for better visibility
        self.standings_table.setColumnWidth(1, 220)  # Driver - wider for full names
        self.standings_table.setColumnWidth(2, 180)  # Team
        self.standings_table.setColumnWidth(3, 80)   # Points
        self.standings_table.setColumnWidth(4, 80)   # Wins
        self.standings_table.setColumnWidth(6, 80)   # Code
        
        self.layout.addWidget(self.standings_table)

    def setup_calendar_table(self):
        """Configure race calendar table with improved column handling"""
        self.calendar_table = QTableWidget()
        self.calendar_table.setColumnCount(5)

        headers = [
            tr("table_round"),
            tr("table_gp"),
            tr("table_date"),
            tr("table_circuit"),
            tr("table_podium"),
        ]
        self.calendar_table.setHorizontalHeaderLabels(headers)
        self.calendar_table.setStyleSheet(AppStyles.get_table_style())
        self.calendar_table.setAlternatingRowColors(True)
        self.calendar_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.calendar_table.setSortingEnabled(False)

        # FIXED: Better calendar table column configuration
        cal_header = self.calendar_table.horizontalHeader()
        cal_header.setMinimumSectionSize(60)
        
        # Set resize modes
        cal_header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)       # Round
        cal_header.setSectionResizeMode(1, QHeaderView.ResizeMode.Interactive) # GP Name
        cal_header.setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)       # Date
        cal_header.setSectionResizeMode(3, QHeaderView.ResizeMode.Interactive) # Circuit
        cal_header.setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)     # Podium
        
        # Set specific widths
        self.calendar_table.setColumnWidth(0, 70)   # Round
        self.calendar_table.setColumnWidth(1, 250)  # GP Name
        self.calendar_table.setColumnWidth(2, 120)  # Date
        self.calendar_table.setColumnWidth(3, 350)  # Circuit

        self.layout.addWidget(self.calendar_table)
    
    def connect_signals(self):
        """Connect signals - REMOVED CALENDAR BUTTON CONNECTION"""
        pass
    
    # NEW METHOD: Load both standings and calendar automatically
    def load_all_data(self):
        """Load both F1 standings and calendar automatically"""
        # First load standings, then calendar will load automatically after standings are done
        self.load_standings()
    
    def load_standings(self):
        """Load F1 standings"""
        if self.data_loader and self.data_loader.isRunning():
            logger.warning("Data loader already running")
            return
        
        # Create and configure loader
        self.data_loader = DataLoader(self.data_service)
        self.data_loader.loading_started.connect(self.on_loading_started)
        self.data_loader.data_loaded.connect(self.on_standings_loaded)
        self.data_loader.error_occurred.connect(self.on_error_occurred)
        self.data_loader.loading_finished.connect(self.on_standings_finished)  # CHANGED: New method
        
        # Start loading
        self.data_loader.start()
    
    def on_loading_started(self):
        """Callback when loading starts"""
        self.status_label.setText(tr("f1_loading"))
        self.status_label.setStyleSheet(AppStyles.get_status_label_style())
        self.refresh_button.setEnabled(False)
        self.refresh_button.setText(tr("f1_loading_button"))
        
        # Emit signal for main status bar
        self.status_updated.emit(tr("f1_loading_standings"))
    
    def on_standings_loaded(self, standings: List[DriverStanding]):
        """Callback when standings are loaded"""
        try:
            self.current_standings = standings
            self.update_standings_table(standings)
            
            success_msg = tr("f1_data_updated", count=len(standings))
            self.status_label.setText(success_msg)
            self.status_label.setStyleSheet(AppStyles.get_success_style())
            
            # Enable export button
            self.export_button.setEnabled(True)
            
            logger.info(f"Successfully loaded {len(standings)} standings")
            self.status_updated.emit(tr("f1_standings_updated", count=len(standings)))
            
        except Exception as e:
            logger.error(f"Error updating table: {e}")
            self.on_error_occurred(tr("show_error_data", error=str(e)))
    
    def on_error_occurred(self, error_message: str):
        """Callback when an error occurs"""
        self.status_label.setText(f"❌ {error_message}")
        self.status_label.setStyleSheet(AppStyles.get_error_style())
        
        # Show error message
        QMessageBox.warning(self, tr("error_title"), tr("error_loading", error=error_message))
        
        self.status_updated.emit(f"Error: {error_message}")
    
    # NEW METHOD: When standings finish, automatically load calendar
    def on_standings_finished(self):
        """Callback when standings loading finishes - AUTO LOAD CALENDAR"""
        # Don't re-enable the refresh button yet, we're loading calendar next
        
        # Auto-load calendar after standings are done
        if not (self.calendar_loader and self.calendar_loader.isRunning()):
            self.load_calendar_auto()
    
    # NEW METHOD: Auto-load calendar (internal method)
    def load_calendar_auto(self):
        """Load race calendar automatically (internal method)"""
        season = "2025"
        self.calendar_loader = CalendarLoader(self.data_service, season)
        self.calendar_loader.loading_started.connect(self.on_calendar_loading)
        self.calendar_loader.calendar_loaded.connect(self.on_calendar_loaded)
        self.calendar_loader.error_occurred.connect(self.on_calendar_error)  # CHANGED: Different error handler
        self.calendar_loader.loading_finished.connect(self.on_all_loading_finished)  # CHANGED: New method
        self.calendar_loader.start()

    def on_calendar_loading(self):
        """Callback when calendar loading starts"""
        self.status_label.setText(tr("f1_calendar_loading"))
        self.status_label.setStyleSheet(AppStyles.get_status_label_style())
        self.status_updated.emit(tr("f1_calendar_loading"))

    def on_calendar_loaded(self, races: List[Race]):
        """Callback when calendar is loaded"""
        try:
            self.current_calendar = races
            self.update_calendar_table(races)
            msg = tr("f1_calendar_loaded", count=len(races))
            self.status_label.setText(msg)
            self.status_label.setStyleSheet(AppStyles.get_success_style())
            self.status_updated.emit(msg)
        except Exception as e:
            logger.error(f"Error updating calendar: {e}")
            self.on_calendar_error(str(e))

    # NEW METHOD: Handle calendar errors without showing popup
    def on_calendar_error(self, error_message: str):
        """Handle calendar loading errors (less intrusive)"""
        logger.warning(f"Calendar loading failed: {error_message}")
        # Don't show popup for calendar errors, just log and update status
        calendar_error_msg = f"Calendar: {error_message}"
        self.status_updated.emit(f"Standings loaded, {calendar_error_msg}")

    # NEW METHOD: When everything is finished loading
    def on_all_loading_finished(self):
        """Callback when all loading (standings + calendar) is finished"""
        self.refresh_button.setEnabled(True)
        self.refresh_button.setText(tr("f1_refresh_button"))

    def update_standings_table(self, standings: List[DriverStanding]):
        """Update table with standings - IMPROVED number display"""
        self.standings_table.setRowCount(len(standings))
        
        for row, standing in enumerate(standings):
            # FIXED: Position with better formatting and alignment
            pos_item = QTableWidgetItem(f"  {standing.position}  ")  # Add padding spaces
            pos_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            pos_item.setFont(QFont("", 12, QFont.Weight.Bold))  # Slightly larger font
            # Set background color for position to make it stand out
            if standing.position <= 3:
                # Podium positions with special colors
                colors = [QColor("#FFD700"), QColor("#C0C0C0"), QColor("#CD7F32")]  # Gold, Silver, Bronze
                pos_item.setBackground(colors[standing.position - 1])
            self.standings_table.setItem(row, 0, pos_item)
            
            # Driver
            driver_item = QTableWidgetItem(standing.driver.full_name)
            driver_item.setFont(QFont("", 10, QFont.Weight.Bold))
            self.standings_table.setItem(row, 1, driver_item)
            
            # Team
            team_name = standing.constructors[0].name if standing.constructors else "N/A"
            team_item = QTableWidgetItem(team_name)
            team_item.setFont(QFont("", 10))
            self.standings_table.setItem(row, 2, team_item)
            
            # Points
            points_item = QTableWidgetItem(f"{int(standing.points)}")
            points_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            points_item.setFont(QFont("", 10, QFont.Weight.Bold))
            self.standings_table.setItem(row, 3, points_item)
            
            # Wins
            wins_item = QTableWidgetItem(str(standing.wins))
            wins_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            wins_item.setFont(QFont("", 10))
            self.standings_table.setItem(row, 4, wins_item)
            
            # Nationality
            nat_item = QTableWidgetItem(standing.driver.nationality)
            nat_item.setFont(QFont("", 10))
            self.standings_table.setItem(row, 5, nat_item)
            
            # Code
            code = standing.driver.code or "N/A"
            code_item = QTableWidgetItem(code)
            code_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            code_item.setFont(QFont("", 10, QFont.Weight.Bold))
            self.standings_table.setItem(row, 6, code_item)
        
        # FIXED: Don't auto-resize after setting data, keep our fixed widths
        # Just adjust the row heights for better readability
        self.standings_table.verticalHeader().setDefaultSectionSize(35)
    
    def update_translations(self):
        """Update translations when language changes"""
        # Update title
        self.title_label.setText(tr("f1_title"))
        
        # Update buttons
        self.refresh_button.setText(tr("f1_refresh_button"))
        self.export_button.setText(tr("f1_export_button"))
        
        # Update season
        self.season_label.setText(tr("f1_season"))
        
        # Update status
        if not self.current_standings:
            self.status_label.setText(tr("f1_ready"))
        
        # Update table headers
        headers = [
            tr("table_pos"),
            tr("table_driver"),
            tr("table_team"),
            tr("table_points"),
            tr("table_wins"),
            tr("table_nationality"),
            tr("table_code")
        ]
        self.standings_table.setHorizontalHeaderLabels(headers)

        # Update calendar headers
        cal_headers = [
            tr("table_round"),
            tr("table_gp"),
            tr("table_date"),
            tr("table_circuit"),
            tr("table_podium"),
        ]
        self.calendar_table.setHorizontalHeaderLabels(cal_headers)

    def update_calendar_table(self, races: List[Race]):
        """Update calendar table with improved formatting"""
        self.calendar_table.setRowCount(len(races))
        
        for row, race in enumerate(races):
            # Round with better formatting
            round_item = QTableWidgetItem(f"  {race.round}  ")
            round_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            round_item.setFont(QFont("", 12, QFont.Weight.Bold))
            self.calendar_table.setItem(row, 0, round_item)

            # Race name
            name_item = QTableWidgetItem(race.race_name)
            name_item.setFont(QFont("", 10, QFont.Weight.Bold))
            self.calendar_table.setItem(row, 1, name_item)
            
            # Date
            date_item = QTableWidgetItem(race.date)
            date_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            date_item.setFont(QFont("", 10))
            self.calendar_table.setItem(row, 2, date_item)
            
            # Circuit
            circuit_item = QTableWidgetItem(race.circuit)
            circuit_item.setFont(QFont("", 10))
            self.calendar_table.setItem(row, 3, circuit_item)

            # Podium
            podium_text = ", ".join(race.podium) if race.podium else "TBD"
            podium_item = QTableWidgetItem(podium_text)
            podium_item.setFont(QFont("", 9))  # Slightly smaller font for podium
            self.calendar_table.setItem(row, 4, podium_item)

        # Set row height for calendar table
        self.calendar_table.verticalHeader().setDefaultSectionSize(35)