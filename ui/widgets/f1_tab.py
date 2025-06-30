# ui/widgets/f1_tab.py
"""
Complete F1 widget with enhanced navigation and all session support

This module provides the complete F1 user interface with integrated navigation
that supports all race weekend sessions including Qualifying, Race, Sprint,
Pit Stops, and Lap History data. Features enhanced career statistics and
OpenF1 integration.

**Classes:**
    ClickableTableWidget - Enhanced table with clickable functionality  
    DarkButton - Dark themed button with styling options
    PodiumWidget - Widget for displaying race podium results
    StandingsTab - Enhanced standings tab with clickable drivers
    CalendarTab - Enhanced calendar tab with clickable circuits  
    F1TabWidget - Main F1 widget with complete navigation system

**Author:** Lotherd
**Version:** 3.0.0
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
    QStackedWidget,
    QProgressBar,
    QSplitter
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QFont, QColor, QCursor

from models.driver import DriverStanding
from models.race import Race
from services.data_service import DataService, DataLoader, CalendarLoader
from services.enhanced_data_service import EnhancedDataService
from utils.i18n import tr
from typing import List
import logging

logger = logging.getLogger(__name__)

class ClickableTableWidget(QTableWidget):
    """Enhanced dark table with clickable functionality for drivers and circuits"""
    
    driver_clicked = pyqtSignal(object)  # DriverStanding object
    circuit_clicked = pyqtSignal(object)  # Race object
    
    def __init__(self, table_type="standings"):
        super().__init__()
        self.table_type = table_type  # "standings" or "calendar"
        self.data_objects = {}  # Store row -> data object mapping
        
        # Make table non-editable
        self.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        
        # Setup enhanced dark styling
        self.setup_enhanced_dark_style()
        
        # Connect cell click signal
        self.cellClicked.connect(self.handle_cell_click)
    
    def setup_enhanced_dark_style(self):
        """Applies comprehensive enhanced dark theme styling"""
        self.setStyleSheet("""
            QTableWidget {
                background-color: #0f0f0f;
                gridline-color: #333333;
                color: #ffffff;
                border: 1px solid #333333;
                border-radius: 10px;
                selection-background-color: #e10600;
                selection-color: #ffffff;
                font-size: 14px;
                font-weight: 400;
            }
            QHeaderView::section {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                            stop:0 #e10600, stop:1 #b30500);
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
                padding: 16px 12px;
                border-bottom: 1px solid #2a2a2a;
                border-right: none;
                background-color: #0f0f0f;
            }
            QTableWidget::item:alternate {
                background-color: #1a1a1a;
            }
            QTableWidget::item:selected {
                background-color: #e10600;
                color: #ffffff;
                font-weight: 600;
            }
            QTableWidget::item:hover {
                background-color: #2a2a2a;
            }
            QScrollBar:vertical {
                background-color: #2a2a2a;
                width: 10px;
                border-radius: 5px;
                margin: 0;
            }
            QScrollBar::handle:vertical {
                background-color: #666666;
                border-radius: 5px;
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
        self.setSortingEnabled(False)
        self.verticalHeader().setVisible(False)
    
    def store_data_object(self, row: int, data_object):
        """Store data object for a specific row"""
        self.data_objects[row] = data_object
    
    def handle_cell_click(self, row: int, column: int):
        """Handle cell clicks and emit appropriate signals"""
        if row not in self.data_objects:
            return
        
        data_object = self.data_objects[row]
        
        if self.table_type == "standings":
            # Driver name is in column 1
            if column == 1:  # Driver column
                logger.info(f"🖱️ Driver clicked: {data_object.driver.full_name}")
                self.driver_clicked.emit(data_object)
                
        elif self.table_type == "calendar":
            # Circuit name is in column 3
            if column == 3:  # Circuit column
                logger.info(f"🖱️ Circuit clicked: {data_object.race_name}")
                self.circuit_clicked.emit(data_object)
    
    def set_cell_clickable(self, row: int, column: int, clickable: bool = True):
        """Make specific cells appear clickable"""
        item = self.item(row, column)
        if item and clickable:
            # Make text blue and underlined to indicate it's clickable
            item.setForeground(QColor("#4dabf7"))
            font = item.font()
            font.setUnderline(True)
            item.setFont(font)
            
            # Set tooltip
            item.setToolTip("Click for detailed information")

class DarkButton(QPushButton):
    """Enhanced dark theme button with primary and secondary styling options"""
    
    def __init__(self, text: str, primary: bool = True):
        super().__init__(text)
        self.setup_enhanced_dark_style(primary)
    
    def setup_enhanced_dark_style(self, primary: bool):
        """Applies enhanced dark theme styling based on button type"""
        if primary:
            self.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                stop:0 #e10600, stop:1 #b30500);
                    color: #ffffff;
                    border: none;
                    padding: 14px 28px;
                    font-size: 14px;
                    font-weight: 600;
                    border-radius: 8px;
                    min-width: 140px;
                    text-transform: uppercase;
                    letter-spacing: 1px;
                }
                QPushButton:hover {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                stop:0 #ff1a0a, stop:1 #e10600);
                    transform: translateY(-2px);
                }
                QPushButton:pressed {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                stop:0 #b30500, stop:1 #900400);
                    transform: translateY(1px);
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
                    border: 2px solid #555555;
                    padding: 14px 28px;
                    font-size: 14px;
                    font-weight: 500;
                    border-radius: 8px;
                    min-width: 140px;
                }
                QPushButton:hover {
                    background-color: #2a2a2a;
                    border-color: #e10600;
                    color: #e10600;
                    transform: translateY(-2px);
                }
                QPushButton:pressed {
                    background-color: #1a1a1a;
                    transform: translateY(1px);
                }
                QPushButton:disabled {
                    background-color: #1a1a1a;
                    color: #555555;
                    border-color: #333333;
                }
            """)

class EnhancedPodiumWidget(QWidget):
    """Enhanced widget for displaying race podium results with animations"""
    
    def __init__(self, podium_list: List[str]):
        super().__init__()
        self.podium_list = podium_list
        self.setup_ui()
    
    def setup_ui(self):
        """Sets up the enhanced podium display UI"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)
        
        colors = ['#FFD700', '#C0C0C0', '#CD7F32']  # Gold, Silver, Bronze
        positions = ['🥇', '🥈', '🥉']
        
        for i, driver in enumerate(self.podium_list[:3]):
            if i < len(colors):
                podium_label = QLabel(f"{positions[i]} {driver}")
                podium_label.setStyleSheet(f"""
                    QLabel {{
                        color: {colors[i]};
                        font-weight: 700;
                        font-size: 14px;
                        padding: 8px 12px;
                        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                    stop:0 #2a2a2a, stop:1 #1a1a1a);
                        border-radius: 8px;
                        border-left: 4px solid {colors[i]};
                        border-top: 1px solid {colors[i]};
                    }}
                """)
                layout.addWidget(podium_label)
        
        if len(self.podium_list) == 0:
            tbd_label = QLabel("TBD")
            tbd_label.setStyleSheet("""
                QLabel {
                    color: #666666;
                    font-style: italic;
                    font-size: 14px;
                    padding: 8px 12px;
                    background-color: #2a2a2a;
                    border-radius: 6px;
                }
            """)
            layout.addWidget(tbd_label)

class EnhancedStandingsTab(QWidget):
    """Enhanced dark theme standings tab with clickable drivers"""
    
    status_updated = pyqtSignal(str)
    driver_clicked = pyqtSignal(object)
    
    def __init__(self, data_service):
        super().__init__()
        self.data_service = data_service
        self.enhanced_data_service = EnhancedDataService()
        self.data_loader = None
        self.current_standings = []
        self.has_loaded = False
        self.setup_ui()
    
    def setup_ui(self):
        """Sets up the enhanced UI layout for the standings tab"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(25)
        
        # Enhanced dark background
        self.setStyleSheet("""
            QWidget {
                background-color: #0f0f0f;
                color: #ffffff;
            }
        """)
        
        # Enhanced header
        header_layout = QVBoxLayout()
        
        title_label = QLabel("Championship Standings")
        title_label.setStyleSheet("""
            QLabel {
                font-size: 32px;
                font-weight: 300;
                color: #ffffff;
                margin-bottom: 15px;
                letter-spacing: 2px;
            }
        """)
        header_layout.addWidget(title_label)
        
        subtitle_label = QLabel("2025 Formula 1 World Championship")
        subtitle_label.setStyleSheet("""
            QLabel {
                font-size: 16px;
                color: #e10600;
                margin-bottom: 20px;
                font-weight: 500;
            }
        """)
        header_layout.addWidget(subtitle_label)
        
        layout.addLayout(header_layout)
        
        # Enhanced status bar
        self.status_label = QLabel("Loading standings...")
        self.status_label.setStyleSheet("""
            QLabel {
                color: #ffffff;
                font-size: 15px;
                padding: 15px 20px;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                            stop:0 #2a2a2a, stop:1 #1a1a1a);
                border-radius: 8px;
                border-left: 4px solid #ffc107;
            }
        """)
        layout.addWidget(self.status_label)
        
        # Enhanced standings table - now clickable
        self.standings_table = ClickableTableWidget("standings")
        self.standings_table.driver_clicked.connect(self.driver_clicked.emit)
        self.setup_enhanced_standings_table()
        layout.addWidget(self.standings_table)
        
        # Auto-load when tab becomes visible
        QTimer.singleShot(500, self.auto_load_if_needed)
    
    def auto_load_if_needed(self):
        """Automatically loads standings data if not already loaded"""
        if not self.has_loaded:
            logger.info("🔄 Auto-loading F1 standings...")
            self.load_standings()
    
    def setup_enhanced_standings_table(self):
        """Configures the enhanced standings table structure"""
        self.standings_table.setColumnCount(6)
        
        headers = ["POS", "DRIVER", "TEAM", "POINTS", "WINS", "NATIONALITY"]
        self.standings_table.setHorizontalHeaderLabels(headers)
        
        # Enhanced column behavior
        header = self.standings_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)         # Position
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Interactive)   # Driver
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Interactive)   # Team
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)         # Points
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Fixed)         # Wins
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.Stretch)       # Nationality
        
        # Enhanced column widths
        self.standings_table.setColumnWidth(0, 70)
        self.standings_table.setColumnWidth(1, 220)
        self.standings_table.setColumnWidth(2, 200)
        self.standings_table.setColumnWidth(3, 90)
        self.standings_table.setColumnWidth(4, 70)
    
    def load_standings(self):
        """Initiates background loading of F1 championship standings"""
        if self.data_loader and self.data_loader.isRunning():
            logger.warning("⚠️ Standings already loading, skipping...")
            return
        
        logger.info("🔄 Starting F1 standings load...")
        self.data_loader = DataLoader(self.data_service)
        self.data_loader.loading_started.connect(self.on_loading_started)
        self.data_loader.data_loaded.connect(self.on_standings_loaded)
        self.data_loader.error_occurred.connect(self.on_error_occurred)
        self.data_loader.loading_finished.connect(self.on_loading_finished)
        self.data_loader.start()
    
    def on_loading_started(self):
        """Handles the loading started event with enhanced UI updates"""
        logger.info("📊 F1 standings loading started...")
        self.status_label.setText("🔄 Loading standings...")
        self.status_label.setStyleSheet("""
            QLabel {
                color: #ffffff;
                font-size: 15px;
                padding: 15px 20px;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                            stop:0 #2a2a2a, stop:1 #1a1a1a);
                border-radius: 8px;
                border-left: 4px solid #ffc107;
            }
        """)
        self.status_updated.emit("Loading F1 standings...")
    
    def on_standings_loaded(self, standings: List[DriverStanding]):
        """Processes successfully loaded standings data with enhanced UI updates"""
        try:
            logger.info(f"✅ F1 standings loaded successfully: {len(standings)} drivers")
            self.current_standings = standings
            self.has_loaded = True
            self.update_enhanced_standings_table(standings)
            
            self.status_label.setText(f"✅ Loaded {len(standings)} drivers - Click driver names for details")
            self.status_label.setStyleSheet("""
                QLabel {
                    color: #ffffff;
                    font-size: 15px;
                    padding: 15px 20px;
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                stop:0 #2a2a2a, stop:1 #1a1a1a);
                    border-radius: 8px;
                    border-left: 4px solid #28a745;
                }
            """)
            
            self.status_updated.emit(f"Standings loaded - {len(standings)} drivers")
            
        except Exception as e:
            logger.error(f"❌ Error updating standings table: {e}")
            self.on_error_occurred(f"Error displaying data: {str(e)}")
    
    def on_error_occurred(self, error_message: str):
        """Handles error conditions with enhanced error display"""
        logger.error(f"❌ F1 standings error: {error_message}")
        self.status_label.setText(f"❌ {error_message}")
        self.status_label.setStyleSheet("""
            QLabel {
                color: #ffffff;
                font-size: 15px;
                padding: 15px 20px;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                            stop:0 #2a2a2a, stop:1 #1a1a1a);
                border-radius: 8px;
                border-left: 4px solid #dc3545;
            }
        """)
        self.status_updated.emit(f"Error: {error_message}")
    
    def on_loading_finished(self):
        """Handles the completion of data loading operations"""
        logger.info("🏁 F1 standings loading finished")
    
    def update_enhanced_standings_table(self, standings: List[DriverStanding]):
        """Updates the standings table with enhanced driver championship data"""
        self.standings_table.setRowCount(len(standings))
        
        for row, standing in enumerate(standings):
            # Store the standing object for this row
            self.standings_table.store_data_object(row, standing)
            
            # Enhanced position with podium highlighting
            pos_item = QTableWidgetItem(str(standing.position))
            pos_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            
            # Enhanced podium highlighting
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
            
            # Enhanced driver name - clickable
            driver_item = QTableWidgetItem(standing.driver.full_name)
            if standing.position <= 3:
                font = driver_item.font()
                font.setBold(True)
                driver_item.setFont(font)
            self.standings_table.setItem(row, 1, driver_item)
            # Make driver name clickable
            self.standings_table.set_cell_clickable(row, 1, True)
            
            # Enhanced team
            team_name = standing.constructors[0].name if standing.constructors else "N/A"
            team_item = QTableWidgetItem(team_name)
            self.standings_table.setItem(row, 2, team_item)
            
            # Enhanced points
            points_item = QTableWidgetItem(str(int(standing.points)))
            points_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            if standing.position <= 3:
                font = points_item.font()
                font.setBold(True)
                points_item.setFont(font)
            self.standings_table.setItem(row, 3, points_item)
            
            # Enhanced wins
            wins_item = QTableWidgetItem(str(standing.wins))
            wins_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            if standing.wins > 0:
                wins_item.setForeground(QColor("#ffd700"))
                font = wins_item.font()
                font.setBold(True)
                wins_item.setFont(font)
            self.standings_table.setItem(row, 4, wins_item)
            
            # Enhanced nationality
            nat_item = QTableWidgetItem(standing.driver.nationality)
            self.standings_table.setItem(row, 5, nat_item)
        
        # Enhanced row height
        self.standings_table.verticalHeader().setDefaultSectionSize(55)

class EnhancedCalendarTab(QWidget):
    """Enhanced dark theme calendar tab with clickable circuits"""
    
    status_updated = pyqtSignal(str)
    circuit_clicked = pyqtSignal(object)
    
    def __init__(self, data_service):
        super().__init__()
        self.data_service = data_service
        self.enhanced_data_service = EnhancedDataService()
        self.calendar_loader = None
        self.current_calendar: List[Race] = []
        self.has_loaded = False
        self.setup_ui()
    
    def setup_ui(self):
        """Sets up the enhanced UI layout for the race calendar tab"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(25)
        
        # Enhanced dark background
        self.setStyleSheet("""
            QWidget {
                background-color: #0f0f0f;
                color: #ffffff;
            }
        """)
        
        # Enhanced header
        header_layout = QVBoxLayout()
        
        title_label = QLabel("Race Calendar")
        title_label.setStyleSheet("""
            QLabel {
                font-size: 32px;
                font-weight: 300;
                color: #ffffff;
                margin-bottom: 15px;
                letter-spacing: 2px;
            }
        """)
        header_layout.addWidget(title_label)
        
        subtitle_label = QLabel("2025 Formula 1 Season")
        subtitle_label.setStyleSheet("""
            QLabel {
                font-size: 16px;
                color: #e10600;
                margin-bottom: 20px;
                font-weight: 500;
            }
        """)
        header_layout.addWidget(subtitle_label)
        
        layout.addLayout(header_layout)
        
        # Enhanced status
        self.status_label = QLabel("Loading calendar...")
        self.status_label.setStyleSheet("""
            QLabel {
                color: #ffffff;
                font-size: 15px;
                padding: 15px 20px;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                            stop:0 #2a2a2a, stop:1 #1a1a1a);
                border-radius: 8px;
                border-left: 4px solid #ffc107;
            }
        """)
        layout.addWidget(self.status_label)
        
        # Enhanced calendar table - now clickable
        self.calendar_table = ClickableTableWidget("calendar")
        self.calendar_table.circuit_clicked.connect(self.circuit_clicked.emit)
        self.setup_enhanced_calendar_table()
        layout.addWidget(self.calendar_table)
        
        # Auto-load when tab becomes visible
        QTimer.singleShot(1000, self.auto_load_if_needed)
    
    def auto_load_if_needed(self):
        """Automatically loads calendar data if not already loaded"""
        if not self.has_loaded:
            logger.info("🔄 Auto-loading F1 calendar...")
            self.load_calendar()
    
    def setup_enhanced_calendar_table(self):
        """Configures the enhanced calendar table structure"""
        self.calendar_table.setColumnCount(5)
        
        headers = ["ROUND", "GRAND PRIX", "DATE", "CIRCUIT", "PODIUM"]
        self.calendar_table.setHorizontalHeaderLabels(headers)
        
        # Enhanced calendar table columns
        cal_header = self.calendar_table.horizontalHeader()
        cal_header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)       # Round
        cal_header.setSectionResizeMode(1, QHeaderView.ResizeMode.Interactive) # GP Name
        cal_header.setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)       # Date
        cal_header.setSectionResizeMode(3, QHeaderView.ResizeMode.Interactive) # Circuit
        cal_header.setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)     # Podium
        
        # Enhanced widths
        self.calendar_table.setColumnWidth(0, 90)
        self.calendar_table.setColumnWidth(1, 320)
        self.calendar_table.setColumnWidth(2, 130)
        self.calendar_table.setColumnWidth(3, 300)
    
    def load_calendar(self):
        """Initiates background loading of F1 race calendar for 2025 season"""
        if self.calendar_loader and self.calendar_loader.isRunning():
            logger.warning("⚠️ Calendar already loading, skipping...")
            return
            
        logger.info("🔄 Starting F1 calendar load...")
        season = "2025"
        self.calendar_loader = CalendarLoader(self.data_service, season)
        self.calendar_loader.loading_started.connect(self.on_loading_started)
        self.calendar_loader.calendar_loaded.connect(self.on_calendar_loaded)
        self.calendar_loader.error_occurred.connect(self.on_error_occurred)
        self.calendar_loader.loading_finished.connect(self.on_loading_finished)
        self.calendar_loader.start()
    
    def on_loading_started(self):
        """Handles the calendar loading started event with enhanced UI updates"""
        logger.info("📅 F1 calendar loading started...")
        self.status_label.setText("🔄 Loading race calendar...")
        self.status_label.setStyleSheet("""
            QLabel {
                color: #ffffff;
                font-size: 15px;
                padding: 15px 20px;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                            stop:0 #2a2a2a, stop:1 #1a1a1a);
                border-radius: 8px;
                border-left: 4px solid #ffc107;
            }
        """)
        self.status_updated.emit("Loading race calendar...")
    
    def on_calendar_loaded(self, races: List[Race]):
        """Processes successfully loaded calendar data with enhanced UI updates"""
        try:
            logger.info(f"✅ F1 calendar loaded successfully: {len(races)} races")
            self.current_calendar = races
            self.has_loaded = True
            self.update_enhanced_calendar_table(races)
            
            self.status_label.setText(f"✅ Loaded {len(races)} races - Click circuit names for session details")
            self.status_label.setStyleSheet("""
                QLabel {
                    color: #ffffff;
                    font-size: 15px;
                    padding: 15px 20px;
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                stop:0 #2a2a2a, stop:1 #1a1a1a);
                    border-radius: 8px;
                    border-left: 4px solid #28a745;
                }
            """)
            
            self.status_updated.emit(f"Calendar loaded - {len(races)} races")
            
        except Exception as e:
            logger.error(f"❌ Error updating calendar: {e}")
            self.on_error_occurred(f"Error displaying calendar: {str(e)}")
    
    def on_error_occurred(self, error_message: str):
        """Handles error conditions with enhanced error display"""
        logger.error(f"❌ F1 calendar error: {error_message}")
        self.status_label.setText(f"❌ {error_message}")
        self.status_label.setStyleSheet("""
            QLabel {
                color: #ffffff;
                font-size: 15px;
                padding: 15px 20px;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                            stop:0 #2a2a2a, stop:1 #1a1a1a);
                border-radius: 8px;
                border-left: 4px solid #dc3545;
            }
        """)
        self.status_updated.emit(f"Error: {error_message}")
    
    def on_loading_finished(self):
        """Handles the completion of calendar loading operations"""
        logger.info("🏁 F1 calendar loading finished")
    
    def update_enhanced_calendar_table(self, races: List[Race]):
        """Updates the calendar table with enhanced race data and podium widgets"""
        self.calendar_table.setRowCount(len(races))
        
        for row, race in enumerate(races):
            # Store the race object for this row
            self.calendar_table.store_data_object(row, race)
            
            # Enhanced round
            round_item = QTableWidgetItem(str(race.round))
            round_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            font = round_item.font()
            font.setBold(True)
            round_item.setFont(font)
            self.calendar_table.setItem(row, 0, round_item)
            
            # Enhanced race name
            name_item = QTableWidgetItem(race.race_name)
            font = name_item.font()
            font.setBold(True)
            name_item.setFont(font)
            self.calendar_table.setItem(row, 1, name_item)
            
            # Enhanced date
            date_item = QTableWidgetItem(race.date)
            date_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.calendar_table.setItem(row, 2, date_item)
            
            # Enhanced circuit - clickable
            circuit_item = QTableWidgetItem(race.circuit)
            self.calendar_table.setItem(row, 3, circuit_item)
            # Make circuit name clickable
            self.calendar_table.set_cell_clickable(row, 3, True)
            
            # Enhanced podium widget
            podium_widget = EnhancedPodiumWidget(race.podium)
            self.calendar_table.setCellWidget(row, 4, podium_widget)
        
        # Enhanced row height to accommodate podium widget
        self.calendar_table.verticalHeader().setDefaultSectionSize(65)

class F1TabWidget(QWidget):
    """Enhanced F1 widget container with complete navigation system"""
    
    status_updated = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.data_service = DataService()
        self.enhanced_data_service = EnhancedDataService()
        self.setup_ui()
        
        # Check data availability on startup
        QTimer.singleShot(1000, self.check_api_availability)
    
    def check_api_availability(self):
        """Check API availability and log status"""
        logger.info("🔍 Checking F1 API availability...")
        try:
            availability = self.enhanced_data_service.check_data_availability()
            logger.info(f"📊 API Status: {availability}")
            
            available_endpoints = [k for k, v in availability.items() if v]
            unavailable_endpoints = [k for k, v in availability.items() if not v]
            
            logger.info(f"✅ Available: {', '.join(available_endpoints)}")
            if unavailable_endpoints:
                logger.warning(f"❌ Unavailable: {', '.join(unavailable_endpoints)}")
                
        except Exception as e:
            logger.error(f"❌ Error checking API availability: {e}")
    
    def setup_ui(self):
        """Sets up the complete enhanced navigation system for F1 data"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Enhanced dark background for main widget
        self.setStyleSheet("""
            QWidget {
                background-color: #0f0f0f;
                color: #ffffff;
            }
        """)
        
        # Enhanced navigation stack
        self.navigation_stack = QStackedWidget()
        
        # Enhanced main tabs (standings and calendar)
        self.main_tabs = self.create_enhanced_main_tabs()
        self.navigation_stack.addWidget(self.main_tabs)
        
        layout.addWidget(self.navigation_stack)
    
    def create_enhanced_main_tabs(self) -> QWidget:
        """Create the enhanced main tabbed interface for standings and calendar"""
        main_widget = QWidget()
        layout = QVBoxLayout(main_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Enhanced tab widget
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: none;
                background-color: #0f0f0f;
                border-radius: 10px;
            }
            QTabBar {
                background-color: #1a1a1a;
                border-bottom: 3px solid #333333;
            }
            QTabBar::tab {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                            stop:0 #2a2a2a, stop:1 #1a1a1a);
                color: #cccccc;
                padding: 18px 35px;
                margin-right: 3px;
                border: none;
                font-size: 15px;
                font-weight: 500;
                min-width: 140px;
                border-top-left-radius: 10px;
                border-top-right-radius: 10px;
            }
            QTabBar::tab:selected {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                            stop:0 #e10600, stop:1 #b30500);
                color: #ffffff;
                border-bottom: 4px solid #e10600;
                font-weight: 700;
            }
            QTabBar::tab:hover:!selected {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                            stop:0 #333333, stop:1 #2a2a2a);
                color: #ffffff;
            }
        """)
        
        # Create enhanced tabs
        self.standings_tab = EnhancedStandingsTab(self.data_service)
        self.calendar_tab = EnhancedCalendarTab(self.data_service)
        
        # Connect enhanced signals
        self.standings_tab.status_updated.connect(self.status_updated.emit)
        self.calendar_tab.status_updated.connect(self.status_updated.emit)
        self.standings_tab.driver_clicked.connect(self.show_enhanced_driver_info)
        self.calendar_tab.circuit_clicked.connect(self.show_enhanced_race_results)
        
        # Add enhanced tabs with icons
        self.add_enhanced_tab_with_icon(self.standings_tab, "logo/standing.png", "Standings")
        self.add_enhanced_tab_with_icon(self.calendar_tab, "logo/calendar.png", "Calendar")
        
        layout.addWidget(self.tab_widget)
        return main_widget
    
    def show_enhanced_driver_info(self, driver_standing: DriverStanding):
        """Show enhanced driver information in integrated view"""
        logger.info(f"🏎️ Showing driver info for: {driver_standing.driver.full_name}")
        
        # Import here to avoid circular imports
        from ui.widgets.f1_navigation import EnhancedDriverInfoTab
        
        # Create enhanced driver info widget
        driver_widget = QWidget()
        driver_layout = QVBoxLayout(driver_widget)
        driver_layout.setContentsMargins(0, 0, 0, 0)
        
        # Add enhanced back button
        back_button = QPushButton("← Back to Standings")
        back_button.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                            stop:0 #e10600, stop:1 #b30500);
                color: white;
                border: none;
                padding: 18px 30px;
                font-size: 16px;
                font-weight: bold;
                border-radius: 10px;
                margin: 20px;
                text-align: left;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                            stop:0 #ff1a0a, stop:1 #e10600);
                transform: translateY(-2px);
            }
            QPushButton:pressed {
                transform: translateY(1px);
            }
        """)
        back_button.clicked.connect(self.go_back_to_main)
        driver_layout.addWidget(back_button)
        
        # Add enhanced driver info content
        driver_info = EnhancedDriverInfoTab(driver_standing)
        driver_layout.addWidget(driver_info)
        
        # Add to navigation stack
        self.navigation_stack.addWidget(driver_widget)
        self.navigation_stack.setCurrentWidget(driver_widget)
    
    def show_enhanced_race_results(self, race: Race):
        """Show enhanced race results in integrated view"""
        logger.info(f"🏁 Showing race results for: {race.race_name}")
        
        # Import here to avoid circular imports
        from ui.widgets.f1_navigation import CompleteRaceResultsTab
        
        # Create enhanced race results widget
        race_widget = QWidget()
        race_layout = QVBoxLayout(race_widget)
        race_layout.setContentsMargins(0, 0, 0, 0)
        
        # Add enhanced back button
        back_button = QPushButton("← Back to Calendar")
        back_button.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                            stop:0 #e10600, stop:1 #b30500);
                color: white;
                border: none;
                padding: 18px 30px;
                font-size: 16px;
                font-weight: bold;
                border-radius: 10px;
                margin: 20px;
                text-align: left;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                            stop:0 #ff1a0a, stop:1 #e10600);
                transform: translateY(-2px);
            }
            QPushButton:pressed {
                transform: translateY(1px);
            }
        """)
        back_button.clicked.connect(self.go_back_to_main)
        race_layout.addWidget(back_button)
        
        # Add enhanced race results content
        race_results = CompleteRaceResultsTab(race)
        race_layout.addWidget(race_results)
        
        # Add to navigation stack
        self.navigation_stack.addWidget(race_widget)
        self.navigation_stack.setCurrentWidget(race_widget)
    
    def go_back_to_main(self):
        """Navigate back to enhanced main tabs"""
        logger.info("🔙 Going back to main tabs")
        
        # Remove current widget
        current_widget = self.navigation_stack.currentWidget()
        if current_widget != self.main_tabs:
            self.navigation_stack.removeWidget(current_widget)
            current_widget.deleteLater()
        
        # Go back to main tabs
        self.navigation_stack.setCurrentWidget(self.main_tabs)
    
    def add_enhanced_tab_with_icon(self, widget, icon_path, text):
        """Adds an enhanced tab to the widget with optional PNG icon"""
        import os
        from PyQt6.QtGui import QIcon, QPixmap, QPainter
        from PyQt6.QtCore import QSize
        
        if os.path.exists(icon_path):
            # Load and process icon
            pixmap = QPixmap(icon_path)
            if not pixmap.isNull():
                # Scale icon
                scaled_pixmap = pixmap.scaled(
                    20, 20,
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
    
    def auto_load_initial_data(self):
        """Automatically loads initial F1 data when the widget becomes active"""
        logger.info("🚀 Auto-loading initial F1 data...")
        # The enhanced tabs will auto-load when they become visible
    
    def update_translations(self):
        """Updates all translatable text elements when language changes"""
        # Update enhanced tab titles
        self.tab_widget.setTabText(0, "🏆 Standings")
        self.tab_widget.setTabText(1, "📅 Calendar")
        
        # Update enhanced table headers in both tabs
        standings_headers = ["POS", "DRIVER", "TEAM", "POINTS", "WINS", "NATIONALITY"]
        self.standings_tab.standings_table.setHorizontalHeaderLabels(standings_headers)
        
        calendar_headers = ["ROUND", "GRAND PRIX", "DATE", "CIRCUIT", "PODIUM"]
        self.calendar_tab.calendar_table.setHorizontalHeaderLabels(calendar_headers)