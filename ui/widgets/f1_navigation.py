# ui/widgets/f1_navigation.py
"""
Improved F1 navigation system with real career data and working session results

This module provides a complete navigation system with real career statistics
and properly working session data loading for all F1 weekend sessions.

**Classes:**
    NavigationTabWidget - Main navigation container with back functionality
    DriverInfoTab - Integrated driver information with real career stats
    RaceResultsTab - Integrated race results with working session data
    SessionResultsTab - Individual session results display

**Author:** Lotherd
**Version:** 2.0.0
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
    QTableWidget, QTableWidgetItem, QHeaderView, QTabWidget,
    QScrollArea, QFrame, QGridLayout, QStackedWidget, QProgressBar
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QFont, QColor

from models.driver import DriverStanding
from models.race import Race
from services.enhanced_data_service import EnhancedDataService, SessionDataLoader, CareerStatsLoader
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)

class DarkTabWidget(QTabWidget):
    """Dark themed tab widget with consistent styling"""
    
    def __init__(self):
        super().__init__()
        self.setup_dark_style()
    
    def setup_dark_style(self):
        """Apply consistent dark theme styling"""
        self.setStyleSheet("""
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
                padding: 15px 25px;
                margin-right: 2px;
                border: none;
                font-size: 14px;
                font-weight: 500;
                min-width: 100px;
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

class DriverInfoTab(QWidget):
    """Integrated driver information tab with real career statistics"""
    
    def __init__(self, driver_standing: DriverStanding):
        super().__init__()
        self.driver_standing = driver_standing
        self.driver = driver_standing.driver
        self.data_service = EnhancedDataService()
        self.career_stats = {}
        self.setup_ui()
        self.load_career_stats()
    
    def setup_ui(self):
        """Set up the driver information UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Dark background
        self.setStyleSheet("""
            QWidget {
                background-color: #0f0f0f;
                color: #ffffff;
            }
        """)
        
        # Driver header
        header_widget = self.create_driver_header()
        layout.addWidget(header_widget)
        
        # Tabbed content
        self.tab_widget = DarkTabWidget()
        
        # Overview tab
        self.overview_tab = self.create_overview_tab()
        self.tab_widget.addTab(self.overview_tab, "📊 Overview")
        
        # Career stats tab (will be populated when data loads)
        self.career_tab = self.create_loading_career_tab()
        self.tab_widget.addTab(self.career_tab, "🏆 Career Stats")
        
        # Season tab
        season_tab = self.create_season_tab()
        self.tab_widget.addTab(season_tab, "📅 2025 Season")
        
        layout.addWidget(self.tab_widget)
    
    def load_career_stats(self):
        """Load real career statistics for the driver"""
        self.career_loader = self.data_service.create_career_stats_loader(self.driver.driver_id)
        self.career_loader.stats_loaded.connect(self.on_career_stats_loaded)
        self.career_loader.error_occurred.connect(self.on_career_stats_error)
        self.career_loader.start()
    
    def on_career_stats_loaded(self, stats: Dict[str, Any]):
        """Handle loaded career statistics"""
        self.career_stats = stats
        # Update career tab with real data
        new_career_tab = self.create_career_tab_with_data(stats)
        self.tab_widget.removeTab(1)  # Remove loading tab
        self.tab_widget.insertTab(1, new_career_tab, "🏆 Career Stats")
        logger.info(f"Career stats loaded for {self.driver.full_name}")
    
    def on_career_stats_error(self, error: str):
        """Handle career statistics loading error"""
        logger.error(f"Error loading career stats: {error}")
        # Show error tab instead
        error_tab = self.create_error_career_tab(error)
        self.tab_widget.removeTab(1)  # Remove loading tab
        self.tab_widget.insertTab(1, error_tab, "🏆 Career Stats")
    
    def create_driver_header(self) -> QWidget:
        """Create the driver header section with enhanced styling"""
        header = QFrame()
        header.setFixedHeight(140)
        header.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                            stop:0 #1a1a1a, stop:1 #2d2d2d);
                border: 1px solid #333333;
                border-radius: 12px;
                margin-bottom: 10px;
            }
        """)
        
        layout = QHBoxLayout(header)
        layout.setContentsMargins(25, 20, 25, 20)
        
        # Driver photo placeholder with team colors
        photo_label = QLabel()
        photo_label.setFixedSize(90, 90)
        photo_label.setStyleSheet("""
            QLabel {
                background-color: #e10600;
                border-radius: 45px;
                color: white;
                font-size: 32px;
                font-weight: bold;
                border: 3px solid #ffffff;
            }
        """)
        photo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        initials = f"{self.driver.given_name[0]}{self.driver.family_name[0]}"
        photo_label.setText(initials)
        layout.addWidget(photo_label)
        
        # Driver info section
        info_layout = QVBoxLayout()
        
        # Name
        name_label = QLabel(self.driver.full_name)
        name_label.setStyleSheet("""
            QLabel {
                color: #ffffff;
                font-size: 28px;
                font-weight: bold;
                margin-bottom: 8px;
            }
        """)
        info_layout.addWidget(name_label)
        
        # Team and position
        team_name = self.driver_standing.constructors[0].name if self.driver_standing.constructors else "N/A"
        subtitle = f"{team_name} • #{self.driver_standing.position} in Championship"
        subtitle_label = QLabel(subtitle)
        subtitle_label.setStyleSheet("""
            QLabel {
                color: #cccccc;
                font-size: 16px;
                margin-bottom: 15px;
            }
        """)
        info_layout.addWidget(subtitle_label)
        
        # Quick stats row
        stats_layout = QHBoxLayout()
        quick_stats = [
            ("Points", str(int(self.driver_standing.points))),
            ("Wins", str(self.driver_standing.wins)),
            ("Position", f"#{self.driver_standing.position}")
        ]
        
        for label, value in quick_stats:
            stat_widget = self.create_quick_stat(label, value)
            stats_layout.addWidget(stat_widget)
        
        info_layout.addLayout(stats_layout)
        layout.addLayout(info_layout)
        
        layout.addStretch()
        
        return header
    
    def create_quick_stat(self, label: str, value: str) -> QWidget:
        """Create a quick stat widget"""
        widget = QFrame()
        widget.setFixedSize(90, 70)
        widget.setStyleSheet("""
            QFrame {
                background-color: #333333;
                border: 1px solid #555555;
                border-radius: 8px;
                margin: 5px;
            }
        """)
        
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(4)
        
        value_label = QLabel(value)
        value_label.setStyleSheet("""
            QLabel {
                color: #e10600;
                font-size: 18px;
                font-weight: bold;
            }
        """)
        value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        label_widget = QLabel(label)
        label_widget.setStyleSheet("""
            QLabel {
                color: #cccccc;
                font-size: 11px;
                font-weight: 500;
            }
        """)
        label_widget.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        layout.addWidget(value_label)
        layout.addWidget(label_widget)
        
        return widget
    
    def create_overview_tab(self) -> QWidget:
        """Create the overview tab with basic information"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # Driver details in a professional grid
        details_frame = QFrame()
        details_frame.setStyleSheet("""
            QFrame {
                background-color: #1a1a1a;
                border: 1px solid #333333;
                border-radius: 10px;
                padding: 20px;
            }
        """)
        
        grid_layout = QGridLayout(details_frame)
        grid_layout.setSpacing(20)
        
        # Driver details
        details = [
            ("Full Name", self.driver.full_name),
            ("Nationality", self.driver.nationality),
            ("Date of Birth", self.driver.date_of_birth or "N/A"),
            ("Driver Code", self.driver.code or "N/A"),
            ("Permanent Number", self.driver.permanent_number or "N/A"),
            ("Current Team", self.driver_standing.constructors[0].name if self.driver_standing.constructors else "N/A"),
            ("Championship Position", f"#{self.driver_standing.position}"),
            ("Points This Season", str(int(self.driver_standing.points))),
            ("Wins This Season", str(self.driver_standing.wins)),
        ]
        
        for i, (label, value) in enumerate(details):
            row = i // 2
            col = (i % 2) * 2
            
            # Label
            label_widget = QLabel(f"{label}:")
            label_widget.setStyleSheet("""
                QLabel {
                    color: #e10600;
                    font-weight: bold;
                    font-size: 14px;
                }
            """)
            
            # Value
            value_widget = QLabel(str(value))
            value_widget.setStyleSheet("""
                QLabel {
                    color: #ffffff;
                    font-size: 14px;
                    padding: 10px;
                    background-color: #2a2a2a;
                    border-radius: 6px;
                    border: 1px solid #444444;
                }
            """)
            
            grid_layout.addWidget(label_widget, row, col)
            grid_layout.addWidget(value_widget, row, col + 1)
        
        layout.addWidget(details_frame)
        layout.addStretch()
        
        return widget
    
    def create_loading_career_tab(self) -> QWidget:
        """Create a loading tab for career statistics"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(50, 50, 50, 50)
        
        # Loading indicator
        loading_frame = QFrame()
        loading_frame.setStyleSheet("""
            QFrame {
                background-color: #1a1a1a;
                border: 1px solid #333333;
                border-radius: 10px;
                padding: 40px;
            }
        """)
        
        loading_layout = QVBoxLayout(loading_frame)
        
        loading_label = QLabel("🔄 Loading Career Statistics...")
        loading_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        loading_label.setStyleSheet("""
            QLabel {
                color: #ffffff;
                font-size: 18px;
                font-weight: bold;
                margin-bottom: 20px;
            }
        """)
        loading_layout.addWidget(loading_label)
        
        # Progress bar
        progress_bar = QProgressBar()
        progress_bar.setRange(0, 0)  # Indeterminate
        progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #333333;
                border-radius: 6px;
                background-color: #2a2a2a;
                height: 8px;
            }
            QProgressBar::chunk {
                background-color: #e10600;
                border-radius: 4px;
            }
        """)
        loading_layout.addWidget(progress_bar)
        
        desc_label = QLabel("Fetching career data from F1 archives...")
        desc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc_label.setStyleSheet("""
            QLabel {
                color: #cccccc;
                font-size: 14px;
                margin-top: 15px;
            }
        """)
        loading_layout.addWidget(desc_label)
        
        layout.addWidget(loading_frame)
        layout.addStretch()
        
        return widget
    
    def create_career_tab_with_data(self, stats: Dict[str, Any]) -> QWidget:
        """Create career tab with real statistics data"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # Career stats frame
        career_frame = QFrame()
        career_frame.setStyleSheet("""
            QFrame {
                background-color: #1a1a1a;
                border: 1px solid #333333;
                border-radius: 10px;
                padding: 25px;
            }
        """)
        
        career_layout = QVBoxLayout(career_frame)
        
        # Title
        title_label = QLabel("Career Highlights")
        title_label.setStyleSheet("""
            QLabel {
                color: #e10600;
                font-size: 24px;
                font-weight: bold;
                margin-bottom: 25px;
            }
        """)
        career_layout.addWidget(title_label)
        
        # Stats grid
        stats_grid = QGridLayout()
        stats_grid.setSpacing(15)
        
        # Prepare stats for display
        career_data = [
            ("Total Races", stats.get('total_races', 'N/A')),
            ("Career Wins", stats.get('total_wins', 'N/A')),
            ("Podium Finishes", stats.get('total_podiums', 'N/A')),
            ("Pole Positions", stats.get('total_poles', 'N/A')),
            ("Career Points", stats.get('total_points', 'N/A')),
            ("World Championships", stats.get('championships', 'N/A')),
            ("Seasons Active", stats.get('seasons_active', 'N/A')),
            ("Win Percentage", f"{stats.get('win_percentage', 0)}%" if stats.get('win_percentage') else 'N/A'),
            ("Podium Percentage", f"{stats.get('podium_percentage', 0)}%" if stats.get('podium_percentage') else 'N/A'),
        ]
        
        for i, (label, value) in enumerate(career_data):
            row = i // 3
            col = i % 3
            
            stat_widget = self.create_career_stat_widget(label, str(value))
            stats_grid.addWidget(stat_widget, row, col)
        
        career_layout.addLayout(stats_grid)
        
        # Career period info
        if stats.get('first_season') and stats.get('last_season'):
            period_label = QLabel(f"Career: {stats['first_season']} - {stats['last_season']}")
            period_label.setStyleSheet("""
                QLabel {
                    color: #cccccc;
                    font-size: 16px;
                    margin-top: 20px;
                    font-style: italic;
                }
            """)
            career_layout.addWidget(period_label)
        
        # Teams list
        if stats.get('teams'):
            teams_label = QLabel(f"Teams: {', '.join(stats['teams'][:5])}")  # Show first 5 teams
            teams_label.setStyleSheet("""
                QLabel {
                    color: #cccccc;
                    font-size: 14px;
                    margin-top: 10px;
                }
            """)
            teams_label.setWordWrap(True)
            career_layout.addWidget(teams_label)
        
        layout.addWidget(career_frame)
        layout.addStretch()
        
        return widget
    
    def create_career_stat_widget(self, label: str, value: str) -> QWidget:
        """Create a career statistic widget"""
        widget = QFrame()
        widget.setFixedSize(140, 80)
        widget.setStyleSheet("""
            QFrame {
                background-color: #2a2a2a;
                border: 1px solid #444444;
                border-radius: 8px;
                margin: 5px;
            }
        """)
        
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(5)
        
        value_label = QLabel(value)
        value_label.setStyleSheet("""
            QLabel {
                color: #e10600;
                font-size: 20px;
                font-weight: bold;
            }
        """)
        value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        label_widget = QLabel(label)
        label_widget.setStyleSheet("""
            QLabel {
                color: #cccccc;
                font-size: 11px;
                font-weight: 500;
            }
        """)
        label_widget.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label_widget.setWordWrap(True)
        
        layout.addWidget(value_label)
        layout.addWidget(label_widget)
        
        return widget
    
    def create_error_career_tab(self, error: str) -> QWidget:
        """Create error tab when career data loading fails"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(30, 30, 30, 30)
        
        error_frame = QFrame()
        error_frame.setStyleSheet("""
            QFrame {
                background-color: #1a1a1a;
                border: 1px solid #dc3545;
                border-radius: 10px;
                padding: 30px;
            }
        """)
        
        error_layout = QVBoxLayout(error_frame)
        
        error_title = QLabel("❌ Career Data Unavailable")
        error_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        error_title.setStyleSheet("""
            QLabel {
                color: #dc3545;
                font-size: 20px;
                font-weight: bold;
                margin-bottom: 15px;
            }
        """)
        error_layout.addWidget(error_title)
        
        error_text = QLabel(f"Unable to load career statistics:\n{error}")
        error_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        error_text.setStyleSheet("""
            QLabel {
                color: #cccccc;
                font-size: 14px;
            }
        """)
        error_text.setWordWrap(True)
        error_layout.addWidget(error_text)
        
        layout.addWidget(error_frame)
        layout.addStretch()
        
        return widget
    
    def create_season_tab(self) -> QWidget:
        """Create the 2025 season tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # Season performance frame
        season_frame = QFrame()
        season_frame.setStyleSheet("""
            QFrame {
                background-color: #1a1a1a;
                border: 1px solid #333333;
                border-radius: 10px;
                padding: 25px;
            }
        """)
        
        season_layout = QVBoxLayout(season_frame)
        
        title_label = QLabel("2025 Season Performance")
        title_label.setStyleSheet("""
            QLabel {
                color: #e10600;
                font-size: 24px;
                font-weight: bold;
                margin-bottom: 20px;
            }
        """)
        season_layout.addWidget(title_label)
        
        # Current season stats grid
        season_stats = [
            ("Championship Position", f"#{self.driver_standing.position}"),
            ("Total Points", f"{int(self.driver_standing.points)} pts"),
            ("Race Wins", str(self.driver_standing.wins)),
            ("Current Team", self.driver_standing.constructors[0].name if self.driver_standing.constructors else "N/A")
        ]
        
        stats_grid = QGridLayout()
        stats_grid.setSpacing(15)
        
        for i, (label, value) in enumerate(season_stats):
            row = i // 2
            col = i % 2
            
            stat_widget = self.create_season_stat_widget(label, value)
            stats_grid.addWidget(stat_widget, row, col)
        
        season_layout.addLayout(stats_grid)
        
        layout.addWidget(season_frame)
        layout.addStretch()
        
        return widget
    
    def create_season_stat_widget(self, label: str, value: str) -> QWidget:
        """Create a season statistic widget"""
        widget = QFrame()
        widget.setFixedHeight(70)
        widget.setStyleSheet("""
            QFrame {
                background-color: #2a2a2a;
                border: 1px solid #444444;
                border-radius: 8px;
                margin: 5px;
            }
        """)
        
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(15, 10, 15, 10)
        
        label_widget = QLabel(label)
        label_widget.setStyleSheet("""
            QLabel {
                color: #cccccc;
                font-size: 14px;
                font-weight: 500;
            }
        """)
        
        value_label = QLabel(value)
        value_label.setStyleSheet("""
            QLabel {
                color: #e10600;
                font-size: 18px;
                font-weight: bold;
            }
        """)
        value_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        
        layout.addWidget(label_widget)
        layout.addStretch()
        layout.addWidget(value_label)
        
        return widget

class SessionResultsTable(QTableWidget):
    """Dark themed table for session results with proper formatting"""
    
    def __init__(self):
        super().__init__()
        self.setup_dark_style()
        self.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
    
    def setup_dark_style(self):
        """Apply dark theme styling to the table"""
        self.setStyleSheet("""
            QTableWidget {
                background-color: #1a1a1a;
                gridline-color: #333333;
                color: #ffffff;
                border: 1px solid #333333;
                border-radius: 8px;
                selection-background-color: #e10600;
                selection-color: #ffffff;
                font-size: 13px;
            }
            QHeaderView::section {
                background-color: #e10600;
                color: #ffffff;
                padding: 12px 8px;
                border: none;
                font-weight: bold;
                font-size: 11px;
                text-transform: uppercase;
            }
            QTableWidget::item {
                padding: 10px 8px;
                border-bottom: 1px solid #2a2a2a;
            }
            QTableWidget::item:alternate {
                background-color: #1f1f1f;
            }
            QTableWidget::item:selected {
                background-color: #e10600;
                color: #ffffff;
            }
            QTableWidget::item:hover {
                background-color: #2a2a2a;
            }
        """)
        
        self.setAlternatingRowColors(True)
        self.verticalHeader().setVisible(False)

class RaceResultsTab(QWidget):
    """Improved race results tab with working session data"""
    
    def __init__(self, race: Race):
        super().__init__()
        self.race = race
        self.data_service = EnhancedDataService()
        self.session_data = {}
        self.setup_ui()
        self.load_all_sessions()
    
    def setup_ui(self):
        """Set up the race results UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Dark background
        self.setStyleSheet("""
            QWidget {
                background-color: #0f0f0f;
                color: #ffffff;
            }
        """)
        
        # Race header
        header_widget = self.create_race_header()
        layout.addWidget(header_widget)
        
        # Loading status
        self.loading_label = QLabel("Loading session data...")
        self.loading_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.loading_label.setStyleSheet("""
            QLabel {
                color: #ffffff;
                font-size: 16px;
                padding: 20px;
                background-color: #1a1a1a;
                border: 1px solid #333333;
                border-radius: 8px;
            }
        """)
        layout.addWidget(self.loading_label)
        
        # Sessions tab widget (initially hidden)
        self.sessions_tab = DarkTabWidget()
        self.sessions_tab.hide()
        layout.addWidget(self.sessions_tab)
    
    def create_race_header(self) -> QWidget:
        """Create the race header section"""
        header = QFrame()
        header.setFixedHeight(100)
        header.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                            stop:0 #1a1a1a, stop:1 #2d2d2d);
                border: 1px solid #333333;
                border-radius: 10px;
            }
        """)
        
        layout = QVBoxLayout(header)
        layout.setContentsMargins(20, 15, 20, 15)
        
        # Race name
        race_label = QLabel(self.race.race_name)
        race_label.setStyleSheet("""
            QLabel {
                color: #ffffff;
                font-size: 22px;
                font-weight: bold;
                margin-bottom: 5px;
            }
        """)
        layout.addWidget(race_label)
        
        # Race details
        details_layout = QHBoxLayout()
        
        circuit_label = QLabel(f"📍 {self.race.circuit}")
        circuit_label.setStyleSheet("""
            QLabel {
                color: #cccccc;
                font-size: 14px;
            }
        """)
        details_layout.addWidget(circuit_label)
        
        details_layout.addStretch()
        
        date_label = QLabel(f"📅 {self.race.date}")
        date_label.setStyleSheet("""
            QLabel {
                color: #cccccc;
                font-size: 14px;
            }
        """)
        details_layout.addWidget(date_label)
        
        round_label = QLabel(f"Round {self.race.round}")
        round_label.setStyleSheet("""
            QLabel {
                color: #e10600;
                font-size: 14px;
                font-weight: bold;
                margin-left: 20px;
            }
        """)
        details_layout.addWidget(round_label)
        
        layout.addLayout(details_layout)
        
        return header
    
    def load_all_sessions(self):
        """Load all available session data"""
        self.session_loader = self.data_service.create_session_loader(self.race.season, self.race.round)
        self.session_loader.session_loaded.connect(self.on_session_loaded)
        self.session_loader.loading_progress.connect(self.on_loading_progress)
        self.session_loader.all_sessions_loaded.connect(self.on_all_sessions_loaded)
        self.session_loader.error_occurred.connect(self.on_session_error)
        self.session_loader.start()
    
    def on_loading_progress(self, status: str):
        """Update loading progress"""
        self.loading_label.setText(status)
    
    def on_session_loaded(self, session_name: str, results: List[Dict[str, Any]]):
        """Handle individual session data loaded"""
        logger.info(f"Loaded {session_name}: {len(results)} results")
    
    def on_session_error(self, session_name: str, error: str):
        """Handle session loading error"""
        logger.warning(f"Error loading {session_name}: {error}")
    
    def on_all_sessions_loaded(self, all_data: Dict[str, List[Dict[str, Any]]]):
        """Handle all session data loaded"""
        self.session_data = all_data
        self.loading_label.hide()
        self.create_session_tabs()
        self.sessions_tab.show()
    
    def create_session_tabs(self):
        """Create tabs for each available session"""
        if not self.session_data:
            # No data available
            no_data_tab = self.create_no_data_tab()
            self.sessions_tab.addTab(no_data_tab, "ℹ️ No Data")
            return
        
        # Session order for tabs (only show available sessions)
        session_order = [
            ("Practice 1", "🏃 Practice 1"),
            ("Practice 2", "🏃 Practice 2"), 
            ("Practice 3", "🏃 Practice 3"),
            ("Sprint", "⚡ Sprint Race"),
            ("Qualifying", "⏱️ Qualifying"),
            ("Race", "🏁 Race")
        ]
        
        for session_key, tab_label in session_order:
            if session_key in self.session_data and self.session_data[session_key]:
                session_tab = self.create_session_tab(session_key, self.session_data[session_key])
                self.sessions_tab.addTab(session_tab, tab_label)
        
        # If no sessions were added, show no data tab
        if self.sessions_tab.count() == 0:
            no_data_tab = self.create_no_data_tab()
            self.sessions_tab.addTab(no_data_tab, "ℹ️ No Data")
    
    def create_session_tab(self, session_name: str, results: List[Dict[str, Any]]) -> QWidget:
        """Create a tab for a specific session"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Results table
        table = SessionResultsTable()
        
        # Configure table based on session type
        if "Practice" in session_name:
            self.setup_practice_table(table, results)
        elif "Sprint" in session_name and session_name != "Sprint Qualifying":
            self.setup_race_table(table, results, is_sprint=True)
        elif "Qualifying" in session_name:
            self.setup_qualifying_table(table, results)
        elif "Race" in session_name:
            self.setup_race_table(table, results)
        
        layout.addWidget(table)
        return widget
    
    def setup_practice_table(self, table: SessionResultsTable, results: List[Dict[str, Any]]):
        """Set up table for practice session"""
        headers = ["POS", "DRIVER", "TEAM", "BEST TIME", "LAPS"]
        table.setColumnCount(len(headers))
        table.setHorizontalHeaderLabels(headers)
        table.setRowCount(len(results))
        
        # Configure column widths
        table.setColumnWidth(0, 60)
        table.setColumnWidth(1, 180)
        table.setColumnWidth(2, 180)
        table.setColumnWidth(3, 120)
        table.setColumnWidth(4, 80)
        
        # Populate data
        for row, result in enumerate(results):
            # Position
            pos_item = QTableWidgetItem(result.get('position', 'N/A'))
            pos_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            table.setItem(row, 0, pos_item)
            
            # Driver
            driver = result.get('Driver', {})
            driver_name = f"{driver.get('givenName', '')} {driver.get('familyName', '')}"
            table.setItem(row, 1, QTableWidgetItem(driver_name))
            
            # Team
            constructor = result.get('Constructor', {})
            table.setItem(row, 2, QTableWidgetItem(constructor.get('name', 'N/A')))
            
            # Best time
            best_time = result.get('BestTime', {}).get('time', 'N/A')
            time_item = QTableWidgetItem(best_time)
            time_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            table.setItem(row, 3, time_item)
            
            # Laps
            laps_item = QTableWidgetItem(result.get('laps', 'N/A'))
            laps_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            table.setItem(row, 4, laps_item)
    
    def setup_qualifying_table(self, table: SessionResultsTable, results: List[Dict[str, Any]]):
        """Set up table for qualifying session"""
        headers = ["POS", "DRIVER", "TEAM", "Q1", "Q2", "Q3"]
        table.setColumnCount(len(headers))
        table.setHorizontalHeaderLabels(headers)
        table.setRowCount(len(results))
        
        # Configure column widths
        table.setColumnWidth(0, 60)
        table.setColumnWidth(1, 180)
        table.setColumnWidth(2, 180)
        
        # Populate data
        for row, result in enumerate(results):
            # Highlight top 3
            if result.get('position') in ['1', '2', '3']:
                colors = {'1': "#FFD700", '2': "#C0C0C0", '3': "#CD7F32"}
                color = QColor(colors[result.get('position')])
                
                for col in range(table.columnCount()):
                    item = table.item(row, col) or QTableWidgetItem()
                    item.setBackground(color)
                    item.setForeground(QColor("#000000"))
                    font = item.font()
                    font.setBold(True)
                    item.setFont(font)
            
            # Position
            pos_item = QTableWidgetItem(result.get('position', 'N/A'))
            pos_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            table.setItem(row, 0, pos_item)
            
            # Driver
            driver = result.get('Driver', {})
            driver_name = f"{driver.get('givenName', '')} {driver.get('familyName', '')}"
            table.setItem(row, 1, QTableWidgetItem(driver_name))
            
            # Team
            constructor = result.get('Constructor', {})
            table.setItem(row, 2, QTableWidgetItem(constructor.get('name', 'N/A')))
            
            # Q1, Q2, Q3 times
            q1_item = QTableWidgetItem(result.get('Q1', 'N/A'))
            q1_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            table.setItem(row, 3, q1_item)
            
            q2_item = QTableWidgetItem(result.get('Q2', 'N/A'))
            q2_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            table.setItem(row, 4, q2_item)
            
            q3_item = QTableWidgetItem(result.get('Q3', 'N/A'))
            q3_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            table.setItem(row, 5, q3_item)
    
    def setup_race_table(self, table: SessionResultsTable, results: List[Dict[str, Any]], is_sprint: bool = False):
        """Set up table for race session"""
        headers = ["POS", "DRIVER", "TEAM", "LAPS", "TIME/RETIRED", "PTS"]
        table.setColumnCount(len(headers))
        table.setHorizontalHeaderLabels(headers)
        table.setRowCount(len(results))
        
        # Configure column widths
        table.setColumnWidth(0, 60)
        table.setColumnWidth(1, 180)
        table.setColumnWidth(2, 180)
        table.setColumnWidth(3, 80)
        table.setColumnWidth(5, 60)
        
        # Populate data
        for row, result in enumerate(results):
            # Highlight podium positions
            if result.get('position') in ['1', '2', '3']:
                pos_colors = {'1': "#FFD700", '2': "#C0C0C0", '3': "#CD7F32"}
                color = QColor(pos_colors[result.get('position')])
                
                pos_item = QTableWidgetItem(result.get('position'))
                pos_item.setBackground(color)
                pos_item.setForeground(QColor("#000000"))
                font = pos_item.font()
                font.setBold(True)
                pos_item.setFont(font)
            else:
                pos_item = QTableWidgetItem(result.get('position', 'N/A'))
            
            pos_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            table.setItem(row, 0, pos_item)
            
            # Driver
            driver = result.get('Driver', {})
            driver_name = f"{driver.get('givenName', '')} {driver.get('familyName', '')}"
            table.setItem(row, 1, QTableWidgetItem(driver_name))
            
            # Team
            constructor = result.get('Constructor', {})
            table.setItem(row, 2, QTableWidgetItem(constructor.get('name', 'N/A')))
            
            # Laps
            laps_item = QTableWidgetItem(result.get('laps', 'N/A'))
            laps_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            table.setItem(row, 3, laps_item)
            
            # Time/Status
            time_data = result.get('Time', {}).get('time', result.get('status', 'N/A'))
            table.setItem(row, 4, QTableWidgetItem(time_data))
            
            # Points
            points_item = QTableWidgetItem(result.get('points', '0'))
            points_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            table.setItem(row, 5, points_item)
    
    def create_no_data_tab(self) -> QWidget:
        """Create tab when no session data is available"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(30, 30, 30, 30)
        
        info_frame = QFrame()
        info_frame.setStyleSheet("""
            QFrame {
                background-color: #1a1a1a;
                border: 1px solid #333333;
                border-radius: 8px;
                padding: 30px;
            }
        """)
        
        info_layout = QVBoxLayout(info_frame)
        
        title_label = QLabel(f"🏁 {self.race.race_name}")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("""
            QLabel {
                color: #e10600;
                font-size: 24px;
                font-weight: bold;
                margin-bottom: 20px;
            }
        """)
        info_layout.addWidget(title_label)
        
        info_text = f"""
        <div style="text-align: center; color: #ffffff;">
            <p style="font-size: 16px; margin-bottom: 10px;"><strong>Circuit:</strong> {self.race.circuit}</p>
            <p style="font-size: 16px; margin-bottom: 10px;"><strong>Date:</strong> {self.race.date}</p>
            <p style="font-size: 16px; margin-bottom: 20px;"><strong>Round:</strong> {self.race.round}</p>
            
            <div style="background-color: #2a2a2a; padding: 20px; border-radius: 8px; border-left: 4px solid #ffc107;">
                <h3 style="color: #ffffff; margin-top: 0;">Session Results Not Available</h3>
                <p style="color: #cccccc;">
                    Session data is not available for this race. This could be because:
                </p>
                <ul style="text-align: left; color: #cccccc; margin: 15px 0;">
                    <li>The race hasn't taken place yet</li>
                    <li>Session data is not published in the API</li>
                    <li>Only Qualifying and Race data are available</li>
                </ul>
                <p style="color: #cccccc; margin-bottom: 0;">
                    Try again later or check if Qualifying/Race tabs have data.
                </p>
            </div>
        </div>
        """
        
        info_label = QLabel(info_text)
        info_label.setWordWrap(True)
        info_layout.addWidget(info_label)
        
        layout.addWidget(info_frame)
        layout.addStretch()
        
        return widget