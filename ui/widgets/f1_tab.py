# ui/widgets/f1_tab.py
"""
Fixed minimalist F1 widget with auto-load and font fixes
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

class MinimalistTable(QTableWidget):
    """Clean minimalist table widget"""
    
    def __init__(self):
        super().__init__()
        self.setup_style()
    
    def setup_style(self):
        """Setup clean minimalist table styling"""
        self.setStyleSheet("""
            QTableWidget {
                background-color: #ffffff;
                gridline-color: #f0f0f0;
                color: #333333;
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                selection-background-color: #f8f9fa;
                selection-color: #333333;
                font-size: 14px;
            }
            QHeaderView::section {
                background-color: #f8f9fa;
                color: #555555;
                padding: 16px 12px;
                border: none;
                border-bottom: 2px solid #e0e0e0;
                font-weight: 600;
                font-size: 13px;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }
            QTableWidget::item {
                padding: 16px 12px;
                border-bottom: 1px solid #f5f5f5;
                border-right: none;
            }
            QTableWidget::item:selected {
                background-color: #f0f7ff;
                color: #333333;
            }
            QScrollBar:vertical {
                background-color: #f8f9fa;
                width: 6px;
                border-radius: 3px;
                margin: 0;
            }
            QScrollBar::handle:vertical {
                background-color: #cccccc;
                border-radius: 3px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #999999;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)
        
        self.setAlternatingRowColors(False)
        self.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.setSortingEnabled(False)
        self.verticalHeader().setVisible(False)

class MinimalistButton(QPushButton):
    """Clean minimalist button"""
    
    def __init__(self, text: str, primary: bool = True):
        super().__init__(text)
        self.setup_style(primary)
    
    def setup_style(self, primary: bool):
        """Setup button styling"""
        if primary:
            self.setStyleSheet("""
                QPushButton {
                    background-color: #e10600;
                    color: white;
                    border: none;
                    padding: 12px 24px;
                    font-size: 14px;
                    font-weight: 500;
                    border-radius: 6px;
                    min-width: 120px;
                }
                QPushButton:hover {
                    background-color: #c50500;
                }
                QPushButton:pressed {
                    background-color: #a10400;
                }
                QPushButton:disabled {
                    background-color: #cccccc;
                    color: #666666;
                }
            """)
        else:
            self.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    color: #666666;
                    border: 1px solid #e0e0e0;
                    padding: 12px 24px;
                    font-size: 14px;
                    font-weight: 500;
                    border-radius: 6px;
                    min-width: 120px;
                }
                QPushButton:hover {
                    background-color: #f8f9fa;
                    border-color: #cccccc;
                }
                QPushButton:pressed {
                    background-color: #f0f0f0;
                }
                QPushButton:disabled {
                    background-color: #f8f9fa;
                    color: #cccccc;
                    border-color: #f0f0f0;
                }
            """)

class StandingsTab(QWidget):
    """Clean standings tab with auto-load"""
    
    status_updated = pyqtSignal(str)
    
    def __init__(self, data_service):
        super().__init__()
        self.data_service = data_service
        self.data_loader = None
        self.current_standings = []
        self.has_loaded = False
        self.setup_ui()
    
    def setup_ui(self):
        """Setup standings tab UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(25)
        
        # Header with refresh button
        header_layout = QHBoxLayout()
        
        title_label = QLabel("Championship Standings")
        title_label.setStyleSheet("""
            QLabel {
                font-size: 24px;
                font-weight: 300;
                color: #333333;
                margin-bottom: 10px;
            }
        """)
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        self.refresh_button = MinimalistButton("Refresh", primary=True)
        self.refresh_button.clicked.connect(self.load_standings)
        header_layout.addWidget(self.refresh_button)
        
        layout.addLayout(header_layout)
        
        # Status
        self.status_label = QLabel("Loading standings...")
        self.status_label.setStyleSheet("""
            QLabel {
                color: #666666;
                font-size: 14px;
                padding: 12px;
                background-color: #fff3cd;
                border-radius: 6px;
                border: 1px solid #ffeaa7;
            }
        """)
        layout.addWidget(self.status_label)
        
        # Standings table
        self.standings_table = MinimalistTable()
        self.setup_standings_table()
        layout.addWidget(self.standings_table)
        
        # Auto-load when tab becomes visible
        QTimer.singleShot(500, self.auto_load_if_needed)
    
    def auto_load_if_needed(self):
        """Auto-load standings if not already loaded"""
        if not self.has_loaded:
            self.load_standings()
    
    def setup_standings_table(self):
        """Setup standings table"""
        self.standings_table.setColumnCount(6)  # Simplified columns
        
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
    
    def load_standings(self):
        """Load F1 standings"""
        if self.data_loader and self.data_loader.isRunning():
            return
        
        self.data_loader = DataLoader(self.data_service)
        self.data_loader.loading_started.connect(self.on_loading_started)
        self.data_loader.data_loaded.connect(self.on_standings_loaded)
        self.data_loader.error_occurred.connect(self.on_error_occurred)
        self.data_loader.loading_finished.connect(self.on_loading_finished)
        self.data_loader.start()
    
    def on_loading_started(self):
        """Handle loading start"""
        self.status_label.setText("Loading standings...")
        self.status_label.setStyleSheet("""
            QLabel {
                color: #666666;
                font-size: 14px;
                padding: 12px;
                background-color: #fff3cd;
                border-radius: 6px;
                border: 1px solid #ffeaa7;
            }
        """)
        self.refresh_button.setEnabled(False)
        self.refresh_button.setText("Loading...")
        self.status_updated.emit("Loading F1 standings...")
    
    def on_standings_loaded(self, standings: List[DriverStanding]):
        """Handle standings loaded"""
        try:
            self.current_standings = standings
            self.has_loaded = True
            self.update_standings_table(standings)
            
            self.status_label.setText(f"✓ Loaded {len(standings)} drivers")
            self.status_label.setStyleSheet("""
                QLabel {
                    color: #155724;
                    font-size: 14px;
                    padding: 12px;
                    background-color: #d4edda;
                    border-radius: 6px;
                    border: 1px solid #c3e6cb;
                }
            """)
            
            self.status_updated.emit(f"Standings loaded - {len(standings)} drivers")
            
        except Exception as e:
            logger.error(f"Error updating table: {e}")
            self.on_error_occurred(f"Error displaying data: {str(e)}")
    
    def on_error_occurred(self, error_message: str):
        """Handle error"""
        self.status_label.setText(f"✗ {error_message}")
        self.status_label.setStyleSheet("""
            QLabel {
                color: #721c24;
                font-size: 14px;
                padding: 12px;
                background-color: #f8d7da;
                border-radius: 6px;
                border: 1px solid #f5c6cb;
            }
        """)
        self.status_updated.emit(f"Error: {error_message}")
    
    def on_loading_finished(self):
        """Handle loading finished"""
        self.refresh_button.setEnabled(True)
        self.refresh_button.setText("Refresh")
    
    def update_standings_table(self, standings: List[DriverStanding]):
        """Update standings table with clean styling - FIXED FONTS"""
        self.standings_table.setRowCount(len(standings))
        
        for row, standing in enumerate(standings):
            # Position - FIXED: Use default font
            pos_item = QTableWidgetItem(str(standing.position))
            pos_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            
            # Highlight podium positions with background color only
            if standing.position <= 3:
                pos_item.setBackground(QColor("#f8f9fa"))
                pos_item.setForeground(QColor("#e10600"))
            
            self.standings_table.setItem(row, 0, pos_item)
            
            # Driver - FIXED: Use default font
            driver_item = QTableWidgetItem(standing.driver.full_name)
            self.standings_table.setItem(row, 1, driver_item)
            
            # Team
            team_name = standing.constructors[0].name if standing.constructors else "N/A"
            team_item = QTableWidgetItem(team_name)
            self.standings_table.setItem(row, 2, team_item)
            
            # Points
            points_item = QTableWidgetItem(str(int(standing.points)))
            points_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.standings_table.setItem(row, 3, points_item)
            
            # Wins
            wins_item = QTableWidgetItem(str(standing.wins))
            wins_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.standings_table.setItem(row, 4, wins_item)
            
            # Nationality
            nat_item = QTableWidgetItem(standing.driver.nationality)
            self.standings_table.setItem(row, 5, nat_item)
        
        # Set row height without custom fonts
        self.standings_table.verticalHeader().setDefaultSectionSize(50)

class CalendarTab(QWidget):
    """Clean calendar tab with auto-load"""
    
    status_updated = pyqtSignal(str)
    
    def __init__(self, data_service):
        super().__init__()
        self.data_service = data_service
        self.calendar_loader = None
        self.current_calendar: List[Race] = []
        self.has_loaded = False
        self.setup_ui()
    
    def setup_ui(self):
        """Setup calendar tab UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(25)
        
        # Header with refresh button
        header_layout = QHBoxLayout()
        
        title_label = QLabel("Race Calendar")
        title_label.setStyleSheet("""
            QLabel {
                font-size: 24px;
                font-weight: 300;
                color: #333333;
                margin-bottom: 10px;
            }
        """)
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        self.refresh_button = MinimalistButton("Refresh", primary=True)
        self.refresh_button.clicked.connect(self.load_calendar)
        header_layout.addWidget(self.refresh_button)
        
        layout.addLayout(header_layout)
        
        # Status
        self.status_label = QLabel("Loading calendar...")
        self.status_label.setStyleSheet("""
            QLabel {
                color: #666666;
                font-size: 14px;
                padding: 12px;
                background-color: #fff3cd;
                border-radius: 6px;
                border: 1px solid #ffeaa7;
            }
        """)
        layout.addWidget(self.status_label)
        
        # Calendar table
        self.calendar_table = MinimalistTable()
        self.setup_calendar_table()
        layout.addWidget(self.calendar_table)
        
        # Auto-load when tab becomes visible
        QTimer.singleShot(1000, self.auto_load_if_needed)
    
    def auto_load_if_needed(self):
        """Auto-load calendar if not already loaded"""
        if not self.has_loaded:
            self.load_calendar()
    
    def setup_calendar_table(self):
        """Setup calendar table"""
        self.calendar_table.setColumnCount(5)
        
        headers = ["ROUND", "GRAND PRIX", "DATE", "CIRCUIT", "WINNER"]
        self.calendar_table.setHorizontalHeaderLabels(headers)
        
        # Configure calendar table columns
        cal_header = self.calendar_table.horizontalHeader()
        cal_header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)       # Round
        cal_header.setSectionResizeMode(1, QHeaderView.ResizeMode.Interactive) # GP Name
        cal_header.setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)       # Date
        cal_header.setSectionResizeMode(3, QHeaderView.ResizeMode.Interactive) # Circuit
        cal_header.setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)     # Winner
        
        # Set widths
        self.calendar_table.setColumnWidth(0, 80)
        self.calendar_table.setColumnWidth(1, 300)
        self.calendar_table.setColumnWidth(2, 120)
        self.calendar_table.setColumnWidth(3, 300)
    
    def load_calendar(self):
        """Load race calendar"""
        if self.calendar_loader and self.calendar_loader.isRunning():
            return
            
        season = "2025"
        self.calendar_loader = CalendarLoader(self.data_service, season)
        self.calendar_loader.loading_started.connect(self.on_loading_started)
        self.calendar_loader.calendar_loaded.connect(self.on_calendar_loaded)
        self.calendar_loader.error_occurred.connect(self.on_error_occurred)
        self.calendar_loader.loading_finished.connect(self.on_loading_finished)
        self.calendar_loader.start()
    
    def on_loading_started(self):
        """Handle loading start"""
        self.status_label.setText("Loading race calendar...")
        self.status_label.setStyleSheet("""
            QLabel {
                color: #666666;
                font-size: 14px;
                padding: 12px;
                background-color: #fff3cd;
                border-radius: 6px;
                border: 1px solid #ffeaa7;
            }
        """)
        self.refresh_button.setEnabled(False)
        self.refresh_button.setText("Loading...")
        self.status_updated.emit("Loading race calendar...")
    
    def on_calendar_loaded(self, races: List[Race]):
        """Handle calendar loaded"""
        try:
            self.current_calendar = races
            self.has_loaded = True
            self.update_calendar_table(races)
            
            self.status_label.setText(f"✓ Loaded {len(races)} races")
            self.status_label.setStyleSheet("""
                QLabel {
                    color: #155724;
                    font-size: 14px;
                    padding: 12px;
                    background-color: #d4edda;
                    border-radius: 6px;
                    border: 1px solid #c3e6cb;
                }
            """)
            
            self.status_updated.emit(f"Calendar loaded - {len(races)} races")
            
        except Exception as e:
            logger.error(f"Error updating calendar: {e}")
            self.on_error_occurred(f"Error displaying calendar: {str(e)}")
    
    def on_error_occurred(self, error_message: str):
        """Handle error"""
        self.status_label.setText(f"✗ {error_message}")
        self.status_label.setStyleSheet("""
            QLabel {
                color: #721c24;
                font-size: 14px;
                padding: 12px;
                background-color: #f8d7da;
                border-radius: 6px;
                border: 1px solid #f5c6cb;
            }
        """)
        self.status_updated.emit(f"Error: {error_message}")
    
    def on_loading_finished(self):
        """Handle loading finished"""
        self.refresh_button.setEnabled(True)
        self.refresh_button.setText("Refresh")
    
    def update_calendar_table(self, races: List[Race]):
        """Update calendar table - FIXED FONTS"""
        self.calendar_table.setRowCount(len(races))
        
        for row, race in enumerate(races):
            # Round - FIXED: Use default font
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
            
            # Winner (first from podium)
            winner_text = race.podium[0] if race.podium else "TBD"
            winner_item = QTableWidgetItem(winner_text)
            if race.podium:  # Highlight completed races
                winner_item.setForeground(QColor("#e10600"))
            self.calendar_table.setItem(row, 4, winner_item)
        
        # Set row height without custom fonts
        self.calendar_table.verticalHeader().setDefaultSectionSize(50)

class F1TabWidget(QWidget):
    """Minimalist F1 widget with separate tabs and auto-load"""
    
    status_updated = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.data_service = DataService()
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the minimalist tabbed interface"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Clean tab widget
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: none;
                background-color: #ffffff;
            }
            QTabBar::tab {
                background-color: #f8f9fa;
                color: #666666;
                padding: 15px 30px;
                margin-right: 2px;
                border: none;
                font-size: 14px;
                font-weight: 500;
                min-width: 120px;
            }
            QTabBar::tab:selected {
                background-color: #ffffff;
                color: #e10600;
                border-bottom: 3px solid #e10600;
            }
            QTabBar::tab:hover:!selected {
                background-color: #f0f0f0;
                color: #333333;
            }
        """)
        
        # Create tabs
        self.standings_tab = StandingsTab(self.data_service)
        self.calendar_tab = CalendarTab(self.data_service)
        
        # Connect status signals
        self.standings_tab.status_updated.connect(self.status_updated.emit)
        self.calendar_tab.status_updated.connect(self.status_updated.emit)
        
        # Add tabs
        self.tab_widget.addTab(self.standings_tab, "Standings")
        self.tab_widget.addTab(self.calendar_tab, "Calendar")
        
        layout.addWidget(self.tab_widget)
    
    def auto_load_initial_data(self):
        """Auto-load initial data - standings will load automatically"""
        # The standings tab will auto-load when it becomes visible
        pass
    
    def update_translations(self):
        """Update translations when language changes"""
        # Update tab titles
        self.tab_widget.setTabText(0, "Standings")
        self.tab_widget.setTabText(1, "Calendar")
        
        # Update table headers in both tabs
        standings_headers = ["POS", "DRIVER", "TEAM", "POINTS", "WINS", "NATIONALITY"]
        self.standings_tab.standings_table.setHorizontalHeaderLabels(standings_headers)
        
        calendar_headers = ["ROUND", "GRAND PRIX", "DATE", "CIRCUIT", "WINNER"]
        self.calendar_tab.calendar_table.setHorizontalHeaderLabels(calendar_headers)