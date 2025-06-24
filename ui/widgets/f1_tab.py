# ui/widgets/f1_tab.py
"""
Widget for Formula 1 tab with multi-language support
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
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

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
        """Configure action bar"""
        action_layout = QHBoxLayout()
        
        # Refresh button
        self.refresh_button = QPushButton(tr("f1_refresh_button"))
        self.refresh_button.setStyleSheet(AppStyles.get_main_button_style())
        self.refresh_button.clicked.connect(self.load_standings)
        action_layout.addWidget(self.refresh_button)
        
        # Export button (future)
        self.export_button = QPushButton(tr("f1_export_button"))
        self.export_button.setStyleSheet(AppStyles.get_secondary_button_style())
        self.export_button.setEnabled(False)  # Disabled for now
        action_layout.addWidget(self.export_button)


        # Calendar button
        self.calendar_button = QPushButton(tr("f1_calendar_button"))
        self.calendar_button.setStyleSheet(AppStyles.get_secondary_button_style())
        action_layout.addWidget(self.calendar_button)
        
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
        """Configure standings table"""
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
        
        self.layout.addWidget(self.standings_table)

    def setup_calendar_table(self):
        """Configure race calendar table"""
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

        self.layout.addWidget(self.calendar_table)
    
    def connect_signals(self):
        """Connect signals"""
        self.calendar_button.clicked.connect(self.load_calendar)
    
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
        self.data_loader.loading_finished.connect(self.on_loading_finished)
        
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
    
    def on_loading_finished(self):
        """Callback when loading finishes"""
        self.refresh_button.setEnabled(True)
        self.refresh_button.setText(tr("f1_refresh_button"))
    
    def update_standings_table(self, standings: List[DriverStanding]):
        """Update table with standings"""
        self.standings_table.setRowCount(len(standings))
        
        for row, standing in enumerate(standings):
            # Position
            pos_item = QTableWidgetItem(str(standing.position))
            pos_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            pos_item.setFont(QFont("", 0, QFont.Weight.Bold))
            self.standings_table.setItem(row, 0, pos_item)
            
            # Driver
            driver_item = QTableWidgetItem(standing.driver.full_name)
            driver_item.setFont(QFont("", 0, QFont.Weight.Bold))
            self.standings_table.setItem(row, 1, driver_item)
            
            # Team
            team_name = standing.constructors[0].name if standing.constructors else "N/A"
            self.standings_table.setItem(row, 2, QTableWidgetItem(team_name))
            
            # Points
            points_item = QTableWidgetItem(str(int(standing.points)))
            points_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            points_item.setFont(QFont("", 0, QFont.Weight.Bold))
            self.standings_table.setItem(row, 3, points_item)
            
            # Wins
            wins_item = QTableWidgetItem(str(standing.wins))
            wins_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.standings_table.setItem(row, 4, wins_item)
            
            # Nationality
            self.standings_table.setItem(row, 5, QTableWidgetItem(standing.driver.nationality))
            
            # Code
            code = standing.driver.code or "N/A"
            code_item = QTableWidgetItem(code)
            code_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.standings_table.setItem(row, 6, code_item)
        
        # Resize columns
        self.standings_table.resizeColumnsToContents()
        
        # Set minimum width for important columns
        self.standings_table.setColumnWidth(0, 50)   # Position
        self.standings_table.setColumnWidth(1, 200)  # Driver
        self.standings_table.setColumnWidth(2, 180)  # Team
        self.standings_table.setColumnWidth(3, 80)   # Points
        self.standings_table.setColumnWidth(4, 80)   # Wins
        self.standings_table.setColumnWidth(6, 80)   # Code
    
    def update_translations(self):
        """Update translations when language changes"""
        # Update title
        self.title_label.setText(tr("f1_title"))
        
        # Update buttons
        self.refresh_button.setText(tr("f1_refresh_button"))
        self.export_button.setText(tr("f1_export_button"))
        self.calendar_button.setText(tr("f1_calendar_button"))
        
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

    def load_calendar(self):
        """Load race calendar"""
        if self.calendar_loader and self.calendar_loader.isRunning():
            logger.warning("Calendar loader already running")
            return

        season = "2025"
        self.calendar_loader = CalendarLoader(self.data_service, season)
        self.calendar_loader.loading_started.connect(self.on_calendar_loading)
        self.calendar_loader.calendar_loaded.connect(self.on_calendar_loaded)
        self.calendar_loader.error_occurred.connect(self.on_error_occurred)
        self.calendar_loader.loading_finished.connect(self.on_calendar_finished)
        self.calendar_loader.start()
        self.calendar_button.setEnabled(False)

    def on_calendar_loading(self):
        self.status_label.setText(tr("f1_calendar_loading"))
        self.status_label.setStyleSheet(AppStyles.get_status_label_style())
        self.status_updated.emit(tr("f1_calendar_loading"))

    def on_calendar_loaded(self, races: List[Race]):
        try:
            self.current_calendar = races
            self.update_calendar_table(races)
            msg = tr("f1_calendar_loaded", count=len(races))
            self.status_label.setText(msg)
            self.status_label.setStyleSheet(AppStyles.get_success_style())
            self.status_updated.emit(msg)
        except Exception as e:
            logger.error(f"Error updating calendar: {e}")
            self.on_error_occurred(str(e))

    def on_calendar_finished(self):
        self.calendar_button.setEnabled(True)

    def update_calendar_table(self, races: List[Race]):
        self.calendar_table.setRowCount(len(races))
        for row, race in enumerate(races):
            round_item = QTableWidgetItem(str(race.round))
            round_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.calendar_table.setItem(row, 0, round_item)

            self.calendar_table.setItem(row, 1, QTableWidgetItem(race.race_name))
            self.calendar_table.setItem(row, 2, QTableWidgetItem(race.date))
            self.calendar_table.setItem(row, 3, QTableWidgetItem(race.circuit))

            podium_text = ", ".join(race.podium) if race.podium else "TBD"
            self.calendar_table.setItem(row, 4, QTableWidgetItem(podium_text))

        self.calendar_table.resizeColumnsToContents()