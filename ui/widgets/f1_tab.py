# ui/widgets/f1_tab.py
"""
F1 widget with dark theme and podium display
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
    """Dark theme minimalist table widget"""
    
    def __init__(self):
        super().__init__()
        self.setup_dark_style()
    
    def setup_dark_style(self):
        """Setup dark minimalist table styling"""
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
    """Dark theme minimalist button"""
    
    def __init__(self, text: str, primary: bool = True):
        super().__init__(text)
        self.setup_dark_style(primary)
    
    def setup_dark_style(self, primary: bool):
        """Setup dark button styling"""
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
    """Widget to display podium with gold, silver, bronze colors"""
    
    def __init__(self, podium_list: List[str]):
        super().__init__()
        self.podium_list = podium_list
        self.setup_ui()
    
    def setup_ui(self):
        """Setup podium display"""
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
    """Dark theme standings tab with auto-load"""
    
    status_updated = pyqtSignal(str)
    
    def __init__(self, data_service):
        super().__init__()
        self.data_service = data_service
        self.data_loader = None
        self.current_standings = []
        self.has_loaded = False
        self.setup_ui()
    
    def setup_ui(self):
        """Setup dark standings tab UI"""
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
    
    def auto_load_if_needed(self):
        """Auto-load standings if not already loaded"""
        if not self.has_loaded:
            self.load_standings()
    
    def setup_standings_table(self):
        """Setup dark standings table"""
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
    
    def on_standings_loaded(self, standings: List[DriverStanding]):
        """Handle standings loaded"""
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
    
    def on_error_occurred(self, error_message: str):
        """Handle error"""
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
    
    def on_loading_finished(self):
        """Handle loading finished"""
        pass  # No refresh button to enable
    
    def update_standings_table(self, standings: List[DriverStanding]):
        """Update standings table with dark theme"""
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
    """Dark theme calendar tab with podium display"""
    
    status_updated = pyqtSignal(str)
    
    def __init__(self, data_service):
        super().__init__()
        self.data_service = data_service
        self.calendar_loader = None
        self.current_calendar: List[Race] = []
        self.has_loaded = False
        self.setup_ui()
    
    def setup_ui(self):
        """Setup dark calendar tab UI"""
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
    
    def auto_load_if_needed(self):
        """Auto-load calendar if not already loaded"""
        if not self.has_loaded:
            self.load_calendar()
    
    def setup_calendar_table(self):
        """Setup calendar table"""
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
    
    def on_calendar_loaded(self, races: List[Race]):
        """Handle calendar loaded"""
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
    
    def on_error_occurred(self, error_message: str):
        """Handle error"""
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
    
    def on_loading_finished(self):
        """Handle loading finished"""
        pass  # No refresh button to enable
    
    def update_calendar_table(self, races: List[Race]):
        """Update calendar table with podium display"""
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
    """Dark theme F1 widget with separate tabs and auto-load"""
    
    status_updated = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.data_service = DataService()
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the dark minimalist tabbed interface"""
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
    
    def add_tab_with_icon(self, widget, icon_path, text):
        """Add tab with PNG icon"""
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
        
        calendar_headers = ["ROUND", "GRAND PRIX", "DATE", "CIRCUIT", "PODIUM"]
        self.calendar_tab.calendar_table.setHorizontalHeaderLabels(calendar_headers)