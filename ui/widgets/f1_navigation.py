# ui/widgets/f1_navigation.py
"""
Complete F1 navigation system with all session types and race history - FIXED

This module provides comprehensive navigation with:
- Qualifying, Race, Sprint results
- Pit stops and lap-by-lap history
- Enhanced driver career statistics
- Integration with OpenF1 and Ergast APIs

**Classes:**
    NavigationTabWidget - Main navigation container
    DriverInfoTab - Complete driver information with career stats
    CompleteRaceResultsTab - All race weekend sessions
    PitStopsTab - Detailed pit stop analysis
    LapHistoryTab - Lap-by-lap race analysis
    SessionResultsTable - Enhanced table for all data types

**Author:** Lotherd
**Version:** 3.0.1 - Fixed data display and formatting
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
    QTableWidget, QTableWidgetItem, QHeaderView, QTabWidget,
    QScrollArea, QFrame, QGridLayout, QStackedWidget, QProgressBar,
    QSplitter, QTextEdit, QSpinBox, QComboBox, QCheckBox
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QFont, QColor, QPalette

from models.driver import DriverStanding
from models.race import Race
from services.enhanced_data_service import EnhancedDataService, CompleteSessionDataLoader, CareerStatsLoader
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)

class DarkTabWidget(QTabWidget):
    """Enhanced dark themed tab widget"""
    
    def __init__(self):
        super().__init__()
        self.setup_dark_style()
    
    def setup_dark_style(self):
        """Apply enhanced dark theme styling"""
        self.setStyleSheet("""
            QTabWidget::pane {
                border: none;
                background-color: #0f0f0f;
                border-radius: 8px;
            }
            QTabBar {
                background-color: #1a1a1a;
                border-bottom: 2px solid #333333;
            }
            QTabBar::tab {
                background-color: #2a2a2a;
                color: #cccccc;
                padding: 15px 25px;
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

class EnhancedDriverInfoTab(QWidget):
    """Enhanced driver information with complete career statistics"""
    
    def __init__(self, driver_standing: DriverStanding):
        super().__init__()
        self.driver_standing = driver_standing
        self.driver = driver_standing.driver
        self.data_service = EnhancedDataService()
        self.career_stats = {}
        self.setup_ui()
        self.load_career_stats()
    
    def setup_ui(self):
        """Setup enhanced driver information UI"""
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
        
        # Enhanced driver header
        header_widget = self.create_enhanced_driver_header()
        layout.addWidget(header_widget)
        
        # Enhanced tabbed content
        self.tab_widget = DarkTabWidget()
        
        # Overview tab
        self.overview_tab = self.create_enhanced_overview_tab()
        self.tab_widget.addTab(self.overview_tab, "📊 Overview")
        
        # Career stats tab (loading initially)
        self.career_tab = self.create_loading_career_tab()
        self.tab_widget.addTab(self.career_tab, "🏆 Career Stats")
        
        # Current season tab
        season_tab = self.create_current_season_tab()
        self.tab_widget.addTab(season_tab, "📅 2025 Season")
        
        # Team history tab
        team_tab = self.create_team_history_tab()
        self.tab_widget.addTab(team_tab, "🏁 Teams")
        
        layout.addWidget(self.tab_widget)
    
    def load_career_stats(self):
        """Load comprehensive career statistics"""
        logger.info(f"🔄 Loading career stats for {self.driver.driver_id}")
        self.career_loader = self.data_service.create_career_stats_loader(self.driver.driver_id)
        self.career_loader.loading_progress.connect(self.on_career_loading_progress)
        self.career_loader.stats_loaded.connect(self.on_career_stats_loaded)
        self.career_loader.error_occurred.connect(self.on_career_stats_error)
        self.career_loader.start()
    
    def on_career_loading_progress(self, status: str):
        """Handle career loading progress"""
        logger.info(f"Career loading: {status}")
        # Update loading tab if it exists
        if hasattr(self, 'loading_label'):
            self.loading_label.setText(status)
    
    def on_career_stats_loaded(self, stats: Dict[str, Any]):
        """Handle successfully loaded career statistics"""
        self.career_stats = stats
        logger.info(f"✅ Career stats loaded for {self.driver.full_name}")
        logger.info(f"Stats: {stats}")
        
        # Update career tab with real data
        new_career_tab = self.create_career_tab_with_data(stats)
        self.tab_widget.removeTab(1)  # Remove loading tab
        self.tab_widget.insertTab(1, new_career_tab, "🏆 Career Stats")
        
        # Also update team history if we have team data
        if stats.get('teams'):
            team_tab = self.create_team_history_tab_with_data(stats)
            self.tab_widget.removeTab(3)  # Remove placeholder team tab
            self.tab_widget.insertTab(3, team_tab, "🏁 Teams")
    
    def on_career_stats_error(self, error: str):
        """Handle career statistics loading error"""
        logger.error(f"❌ Error loading career stats: {error}")
        # Show error tab instead
        error_tab = self.create_error_career_tab(error)
        self.tab_widget.removeTab(1)  # Remove loading tab
        self.tab_widget.insertTab(1, error_tab, "🏆 Career Stats")
    
    def create_enhanced_driver_header(self) -> QWidget:
        """Create enhanced driver header with more information"""
        header = QFrame()
        header.setFixedHeight(160)
        header.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                            stop:0 #1a1a1a, stop:1 #2d2d2d);
                border: 1px solid #333333;
                border-radius: 15px;
                margin-bottom: 10px;
            }
        """)
        
        layout = QHBoxLayout(header)
        layout.setContentsMargins(30, 25, 30, 25)
        
        # Driver photo/initials with enhanced styling
        photo_label = QLabel()
        photo_label.setFixedSize(100, 100)
        photo_label.setStyleSheet("""
            QLabel {
                background-color: #e10600;
                border-radius: 50px;
                color: white;
                font-size: 36px;
                font-weight: bold;
                border: 4px solid #ffffff;
            }
        """)
        photo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        initials = f"{self.driver.given_name[0]}{self.driver.family_name[0]}"
        photo_label.setText(initials)
        layout.addWidget(photo_label)
        
        # Enhanced driver info section
        info_layout = QVBoxLayout()
        
        # Name with enhanced styling
        name_label = QLabel(self.driver.full_name)
        name_label.setStyleSheet("""
            QLabel {
                color: #ffffff;
                font-size: 32px;
                font-weight: bold;
                margin-bottom: 10px;
            }
        """)
        info_layout.addWidget(name_label)
        
        # Enhanced subtitle with more info
        team_name = self.driver_standing.constructors[0].name if self.driver_standing.constructors else "N/A"
        subtitle = f"{team_name} • #{self.driver_standing.position} in Championship • {self.driver.nationality}"
        subtitle_label = QLabel(subtitle)
        subtitle_label.setStyleSheet("""
            QLabel {
                color: #cccccc;
                font-size: 16px;
                margin-bottom: 20px;
            }
        """)
        info_layout.addWidget(subtitle_label)
        
        # Enhanced quick stats row
        stats_layout = QHBoxLayout()
        quick_stats = [
            ("Points", str(int(self.driver_standing.points)), "#e10600"),
            ("Position", f"#{self.driver_standing.position}", "#ffffff"),
            ("Wins", str(self.driver_standing.wins), "#ffd700"),
            ("Code", self.driver.code or "N/A", "#00ff88")
        ]
        
        for label, value, color in quick_stats:
            stat_widget = self.create_enhanced_quick_stat(label, value, color)
            stats_layout.addWidget(stat_widget)
        
        info_layout.addLayout(stats_layout)
        layout.addLayout(info_layout)
        
        layout.addStretch()
        
        return header
    
    def create_enhanced_quick_stat(self, label: str, value: str, color: str) -> QWidget:
        """Create enhanced quick stat widget with colors"""
        widget = QFrame()
        widget.setFixedSize(100, 80)
        widget.setStyleSheet(f"""
            QFrame {{
                background-color: #333333;
                border: 2px solid {color};
                border-radius: 10px;
                margin: 5px;
            }}
        """)
        
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(4)
        
        value_label = QLabel(value)
        value_label.setStyleSheet(f"""
            QLabel {{
                color: {color};
                font-size: 20px;
                font-weight: bold;
            }}
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
    
    def create_enhanced_overview_tab(self) -> QWidget:
        """Create enhanced overview tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # Enhanced details in a professional grid
        details_frame = QFrame()
        details_frame.setStyleSheet("""
            QFrame {
                background-color: #1a1a1a;
                border: 1px solid #333333;
                border-radius: 12px;
                padding: 25px;
            }
        """)
        
        grid_layout = QGridLayout(details_frame)
        grid_layout.setSpacing(25)
        
        # Enhanced driver details
        details = [
            ("Full Name", self.driver.full_name),
            ("Nationality", self.driver.nationality),
            ("Date of Birth", self.driver.date_of_birth or "N/A"),
            ("Driver Code", self.driver.code or "N/A"),
            ("Permanent Number", f"#{self.driver.permanent_number}" if self.driver.permanent_number else "N/A"),
            ("Current Team", self.driver_standing.constructors[0].name if self.driver_standing.constructors else "N/A"),
            ("Championship Position", f"#{self.driver_standing.position}"),
            ("Points This Season", f"{int(self.driver_standing.points)} pts"),
            ("Wins This Season", str(self.driver_standing.wins)),
            ("Driver ID", self.driver.driver_id),
        ]
        
        for i, (label, value) in enumerate(details):
            row = i // 2
            col = (i % 2) * 2
            
            # Enhanced label
            label_widget = QLabel(f"{label}:")
            label_widget.setStyleSheet("""
                QLabel {
                    color: #e10600;
                    font-weight: bold;
                    font-size: 15px;
                }
            """)
            
            # Enhanced value
            value_widget = QLabel(str(value))
            value_widget.setStyleSheet("""
                QLabel {
                    color: #ffffff;
                    font-size: 15px;
                    padding: 12px;
                    background-color: #2a2a2a;
                    border-radius: 8px;
                    border: 1px solid #444444;
                }
            """)
            
            grid_layout.addWidget(label_widget, row, col)
            grid_layout.addWidget(value_widget, row, col + 1)
        
        layout.addWidget(details_frame)
        layout.addStretch()
        
        return widget
    
    def create_loading_career_tab(self) -> QWidget:
        """Create enhanced loading tab for career statistics"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(50, 50, 50, 50)
        
        # Loading indicator
        loading_frame = QFrame()
        loading_frame.setStyleSheet("""
            QFrame {
                background-color: #1a1a1a;
                border: 1px solid #333333;
                border-radius: 12px;
                padding: 50px;
            }
        """)
        
        loading_layout = QVBoxLayout(loading_frame)
        
        self.loading_label = QLabel("🔄 Loading Career Statistics...")
        self.loading_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.loading_label.setStyleSheet("""
            QLabel {
                color: #ffffff;
                font-size: 20px;
                font-weight: bold;
                margin-bottom: 25px;
            }
        """)
        loading_layout.addWidget(self.loading_label)
        
        # Enhanced progress bar
        progress_bar = QProgressBar()
        progress_bar.setRange(0, 0)  # Indeterminate
        progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #333333;
                border-radius: 8px;
                background-color: #2a2a2a;
                height: 12px;
            }
            QProgressBar::chunk {
                background-color: #e10600;
                border-radius: 6px;
            }
        """)
        loading_layout.addWidget(progress_bar)
        
        desc_label = QLabel("Fetching comprehensive career data from F1 archives...")
        desc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc_label.setStyleSheet("""
            QLabel {
                color: #cccccc;
                font-size: 16px;
                margin-top: 20px;
            }
        """)
        loading_layout.addWidget(desc_label)
        
        layout.addWidget(loading_frame)
        layout.addStretch()
        
        return widget
    
    def create_career_tab_with_data(self, stats: Dict[str, Any]) -> QWidget:
        """Create career tab with comprehensive statistics"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # Enhanced career stats frame
        career_frame = QFrame()
        career_frame.setStyleSheet("""
            QFrame {
                background-color: #1a1a1a;
                border: 1px solid #333333;
                border-radius: 12px;
                padding: 30px;
            }
        """)
        
        career_layout = QVBoxLayout(career_frame)
        
        # Enhanced title
        title_label = QLabel("Career Highlights")
        title_label.setStyleSheet("""
            QLabel {
                color: #e10600;
                font-size: 28px;
                font-weight: bold;
                margin-bottom: 30px;
            }
        """)
        career_layout.addWidget(title_label)
        
        # Enhanced stats grid
        stats_grid = QGridLayout()
        stats_grid.setSpacing(20)
        
        # Comprehensive career data
        career_data = [
            ("Total Races", stats.get('total_races', 'N/A'), "#4dabf7"),
            ("Career Wins", stats.get('total_wins', 'N/A'), "#ffd700"),
            ("Podium Finishes", stats.get('total_podiums', 'N/A'), "#ff922b"),
            ("Pole Positions", stats.get('total_poles', 'N/A'), "#51cf66"),
            ("Career Points", stats.get('total_points', 'N/A'), "#e10600"),
            ("Championships", stats.get('championships', 'N/A'), "#9775fa"),
            ("Seasons Active", stats.get('seasons_active', 'N/A'), "#74c0fc"),
            ("Win Rate", f"{stats.get('win_percentage', 0)}%" if stats.get('win_percentage') else 'N/A', "#ffd700"),
            ("Podium Rate", f"{stats.get('podium_percentage', 0)}%" if stats.get('podium_percentage') else 'N/A', "#ff922b"),
            ("Best Finish", f"P{stats.get('best_finish', 'N/A')}" if stats.get('best_finish', 'N/A') != 'N/A' else 'N/A', "#51cf66"),
            ("Points/Race", stats.get('points_per_race', 'N/A'), "#e10600"),
            ("Fastest Laps", stats.get('total_fastest_laps', 'N/A'), "#ff6b6b"),
        ]
        
        for i, (label, value, color) in enumerate(career_data):
            row = i // 4
            col = i % 4
            
            stat_widget = self.create_enhanced_career_stat_widget(label, str(value), color)
            stats_grid.addWidget(stat_widget, row, col)
        
        career_layout.addLayout(stats_grid)
        
        # Enhanced career period info
        if stats.get('career_span'):
            period_label = QLabel(f"Career Span: {stats['career_span']}")
            period_label.setStyleSheet("""
                QLabel {
                    color: #cccccc;
                    font-size: 18px;
                    margin-top: 25px;
                    font-style: italic;
                    text-align: center;
                }
            """)
            career_layout.addWidget(period_label)
        
        layout.addWidget(career_frame)
        layout.addStretch()
        
        return widget
    
    def create_enhanced_career_stat_widget(self, label: str, value: str, color: str) -> QWidget:
        """Create enhanced career statistic widget with colors"""
        widget = QFrame()
        widget.setFixedSize(160, 90)
        widget.setStyleSheet(f"""
            QFrame {{
                background-color: #2a2a2a;
                border: 2px solid {color};
                border-radius: 10px;
                margin: 5px;
            }}
        """)
        
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(6)
        
        value_label = QLabel(value)
        value_label.setStyleSheet(f"""
            QLabel {{
                color: {color};
                font-size: 22px;
                font-weight: bold;
            }}
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
    
    def create_current_season_tab(self) -> QWidget:
        """Create enhanced current season tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # Season performance frame
        season_frame = QFrame()
        season_frame.setStyleSheet("""
            QFrame {
                background-color: #1a1a1a;
                border: 1px solid #333333;
                border-radius: 12px;
                padding: 30px;
            }
        """)
        
        season_layout = QVBoxLayout(season_frame)
        
        title_label = QLabel("2025 Season Performance")
        title_label.setStyleSheet("""
            QLabel {
                color: #e10600;
                font-size: 28px;
                font-weight: bold;
                margin-bottom: 25px;
            }
        """)
        season_layout.addWidget(title_label)
        
        # Enhanced current season stats grid
        season_stats = [
            ("Championship Position", f"#{self.driver_standing.position}", "#e10600"),
            ("Total Points", f"{int(self.driver_standing.points)} pts", "#ffd700"),
            ("Race Wins", str(self.driver_standing.wins), "#51cf66"),
            ("Current Team", self.driver_standing.constructors[0].name if self.driver_standing.constructors else "N/A", "#74c0fc")
        ]
        
        stats_grid = QGridLayout()
        stats_grid.setSpacing(20)
        
        for i, (label, value, color) in enumerate(season_stats):
            row = i // 2
            col = i % 2
            
            stat_widget = self.create_enhanced_season_stat_widget(label, value, color)
            stats_grid.addWidget(stat_widget, row, col)
        
        season_layout.addLayout(stats_grid)
        
        layout.addWidget(season_frame)
        layout.addStretch()
        
        return widget
    
    def create_enhanced_season_stat_widget(self, label: str, value: str, color: str) -> QWidget:
        """Create enhanced season statistic widget"""
        widget = QFrame()
        widget.setFixedHeight(80)
        widget.setStyleSheet(f"""
            QFrame {{
                background-color: #2a2a2a;
                border: 2px solid {color};
                border-radius: 10px;
                margin: 5px;
            }}
        """)
        
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(20, 15, 20, 15)
        
        label_widget = QLabel(label)
        label_widget.setStyleSheet("""
            QLabel {
                color: #cccccc;
                font-size: 16px;
                font-weight: 500;
            }
        """)
        
        value_label = QLabel(value)
        value_label.setStyleSheet(f"""
            QLabel {{
                color: {color};
                font-size: 20px;
                font-weight: bold;
            }}
        """)
        value_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        
        layout.addWidget(label_widget)
        layout.addStretch()
        layout.addWidget(value_label)
        
        return widget
    
    def create_team_history_tab(self) -> QWidget:
        """Create placeholder team history tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(30, 30, 30, 30)
        
        loading_label = QLabel("Loading team history...")
        loading_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        loading_label.setStyleSheet("""
            QLabel {
                color: #cccccc;
                font-size: 16px;
            }
        """)
        layout.addWidget(loading_label)
        
        return widget
    
    def create_team_history_tab_with_data(self, stats: Dict[str, Any]) -> QWidget:
        """Create team history tab with actual data"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(15, 15, 15, 15)
        
        teams_frame = QFrame()
        teams_frame.setStyleSheet("""
            QFrame {
                background-color: #1a1a1a;
                border: 1px solid #333333;
                border-radius: 12px;
                padding: 25px;
            }
        """)
        
        teams_layout = QVBoxLayout(teams_frame)
        
        title_label = QLabel("Team History")
        title_label.setStyleSheet("""
            QLabel {
                color: #e10600;
                font-size: 24px;
                font-weight: bold;
                margin-bottom: 20px;
            }
        """)
        teams_layout.addWidget(title_label)
        
        # Teams list
        if stats.get('teams'):
            teams_list = stats['teams']
            for i, team in enumerate(teams_list[:10]):  # Show first 10 teams
                team_widget = QLabel(f"• {team}")
                team_widget.setStyleSheet("""
                    QLabel {
                        color: #ffffff;
                        font-size: 16px;
                        padding: 8px;
                        margin: 2px;
                        background-color: #2a2a2a;
                        border-radius: 6px;
                        border-left: 4px solid #e10600;
                    }
                """)
                teams_layout.addWidget(team_widget)
        
        layout.addWidget(teams_frame)
        layout.addStretch()
        
        return widget
    
    def create_error_career_tab(self, error: str) -> QWidget:
        """Create enhanced error tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(30, 30, 30, 30)
        
        error_frame = QFrame()
        error_frame.setStyleSheet("""
            QFrame {
                background-color: #1a1a1a;
                border: 2px solid #dc3545;
                border-radius: 12px;
                padding: 40px;
            }
        """)
        
        error_layout = QVBoxLayout(error_frame)
        
        error_title = QLabel("❌ Career Data Unavailable")
        error_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        error_title.setStyleSheet("""
            QLabel {
                color: #dc3545;
                font-size: 24px;
                font-weight: bold;
                margin-bottom: 20px;
            }
        """)
        error_layout.addWidget(error_title)
        
        error_text = QLabel(f"Unable to load career statistics:\n{error}")
        error_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        error_text.setStyleSheet("""
            QLabel {
                color: #cccccc;
                font-size: 16px;
            }
        """)
        error_text.setWordWrap(True)
        error_layout.addWidget(error_text)
        
        layout.addWidget(error_frame)
        layout.addStretch()
        
        return widget

class PitStopsTab(QWidget):
    """Enhanced pit stops analysis tab - FIXED to show driver names"""
    
    def __init__(self, pit_stops_data: List[Dict[str, Any]]):
        super().__init__()
        self.pit_stops_data = pit_stops_data
        self.setup_ui()
    
    def setup_ui(self):
        """Setup pit stops analysis UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # Dark background
        self.setStyleSheet("""
            QWidget {
                background-color: #0f0f0f;
                color: #ffffff;
            }
        """)
        
        # Title
        title_label = QLabel(f"Pit Stop Analysis - {len(self.pit_stops_data)} stops")
        title_label.setStyleSheet("""
            QLabel {
                color: #e10600;
                font-size: 24px;
                font-weight: bold;
                margin-bottom: 20px;
            }
        """)
        layout.addWidget(title_label)
        
        # Pit stops table
        self.pit_table = self.create_pit_stops_table()
        layout.addWidget(self.pit_table)
    
    def create_pit_stops_table(self) -> QTableWidget:
        """Create enhanced pit stops table - FIXED"""
        table = QTableWidget()
        table.setStyleSheet("""
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
        """)
        
        headers = ["DRIVER", "LAP", "STOP #", "TIME", "DURATION"]
        table.setColumnCount(len(headers))
        table.setHorizontalHeaderLabels(headers)
        table.setRowCount(len(self.pit_stops_data))
        
        # Configure columns
        table.setColumnWidth(0, 200)
        table.setColumnWidth(1, 80)
        table.setColumnWidth(2, 80)
        table.setColumnWidth(3, 120)
        table.setColumnWidth(4, 120)
        
        # Populate data
        for row, stop in enumerate(self.pit_stops_data):
            # FIXED: Get driver name properly
            driver_name = "Unknown"
            if 'driver' in stop and isinstance(stop['driver'], dict):
                # If driver is enriched with proper data
                given_name = stop['driver'].get('givenName', '')
                family_name = stop['driver'].get('familyName', '')
                driver_name = f"{given_name} {family_name}".strip()
                if not driver_name:
                    driver_name = stop['driver'].get('full_name', 'Unknown')
            elif 'driverId' in stop:
                # Format driver ID if no enriched data
                driver_id = stop.get('driverId', 'unknown')
                # Capitalize and format the driver ID
                parts = driver_id.split('_')
                driver_name = ' '.join(part.capitalize() for part in parts)
            
            driver_item = QTableWidgetItem(driver_name)
            table.setItem(row, 0, driver_item)
            
            # Lap
            lap_item = QTableWidgetItem(str(stop.get('lap', 'N/A')))
            lap_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            table.setItem(row, 1, lap_item)
            
            # Stop number
            stop_item = QTableWidgetItem(str(stop.get('stop', 'N/A')))
            stop_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            table.setItem(row, 2, stop_item)
            
            # Time
            time_item = QTableWidgetItem(stop.get('time', 'N/A'))
            time_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            table.setItem(row, 3, time_item)
            
            # Duration
            duration = stop.get('duration', 'N/A')
            if duration != 'N/A':
                try:
                    # Try to format duration nicely
                    if isinstance(duration, (int, float)):
                        duration = f"{float(duration):.3f}s"
                    elif isinstance(duration, str) and duration.replace('.', '').isdigit():
                        duration = f"{float(duration):.3f}s"
                except:
                    pass
            
            duration_item = QTableWidgetItem(str(duration))
            duration_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            
            # Color code based on duration
            if duration != 'N/A':
                try:
                    # Extract numeric value
                    duration_val = float(str(duration).replace('s', ''))
                    if duration_val < 3.0:
                        duration_item.setForeground(QColor("#51cf66"))  # Fast (green)
                    elif duration_val > 5.0:
                        duration_item.setForeground(QColor("#ff6b6b"))  # Slow (red)
                    else:
                        duration_item.setForeground(QColor("#ffd700"))  # Average (gold)
                except:
                    pass
            
            table.setItem(row, 4, duration_item)
        
        table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        
        return table

class LapHistoryTab(QWidget):
    """Enhanced lap-by-lap history tab - FIXED to show all laps properly"""
    
    def __init__(self, lap_data: List[Dict[str, Any]]):
        super().__init__()
        self.lap_data = lap_data
        self.all_timings = []  # Store all lap timings
        self.current_lap = "all"  # Current selected lap
        self.setup_ui()
        self.process_lap_data()
    
    def setup_ui(self):
        """Setup lap history UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # Dark background
        self.setStyleSheet("""
            QWidget {
                background-color: #0f0f0f;
                color: #ffffff;
            }
        """)
        
        # Title and controls
        header_layout = QHBoxLayout()
        
        title_label = QLabel(f"Lap-by-Lap History - {len(self.lap_data)} laps")
        title_label.setStyleSheet("""
            QLabel {
                color: #e10600;
                font-size: 24px;
                font-weight: bold;
            }
        """)
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        # Lap selector
        self.lap_selector = QComboBox()
        self.lap_selector.setStyleSheet("""
            QComboBox {
                background-color: #2a2a2a;
                color: #ffffff;
                border: 1px solid #444444;
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 14px;
                min-width: 150px;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                border: none;
            }
            QComboBox QAbstractItemView {
                background-color: #2a2a2a;
                color: #ffffff;
                selection-background-color: #e10600;
                selection-color: #ffffff;
            }
        """)
        
        # Populate lap selector
        if self.lap_data:
            self.lap_selector.addItem("All Laps")
            for lap in self.lap_data:
                lap_number = lap.get('number', '?')
                self.lap_selector.addItem(f"Lap {lap_number}")
        
        self.lap_selector.currentIndexChanged.connect(self.on_lap_selected)
        
        header_layout.addWidget(QLabel("View:"))
        header_layout.addWidget(self.lap_selector)
        
        layout.addLayout(header_layout)
        
        # Lap details table
        self.lap_table = self.create_lap_history_table()
        layout.addWidget(self.lap_table)
    
    def process_lap_data(self):
        """Process and prepare all lap data"""
        self.all_timings = []
        
        # Process each lap
        for lap in self.lap_data:
            lap_number = lap.get('number', '1')
            for timing in lap.get('Timings', []):
                timing_data = {
                    'lap': lap_number,
                    'position': timing.get('position', 'N/A'),
                    'time': timing.get('time', 'N/A'),
                    'driverId': timing.get('driverId', 'N/A')
                }
                self.all_timings.append(timing_data)
        
        # Update table with all data
        self.update_table_data()
    
    def on_lap_selected(self, index):
        """Handle lap selection change"""
        if index == 0:
            self.current_lap = "all"
        else:
            # Get the lap number from the selected item
            lap_text = self.lap_selector.itemText(index)
            lap_number = lap_text.replace("Lap ", "")
            self.current_lap = lap_number
        
        self.update_table_data()
    
    def update_table_data(self):
        """Update table based on selected lap"""
        # Clear current table
        self.lap_table.setRowCount(0)
        
        # Filter timings based on selection
        if self.current_lap == "all":
            timings_to_show = self.all_timings
        else:
            timings_to_show = [t for t in self.all_timings if str(t['lap']) == self.current_lap]
        
        # Update row count
        self.lap_table.setRowCount(len(timings_to_show))
        
        # Populate data
        for row, timing in enumerate(timings_to_show):
            # Lap
            lap_item = QTableWidgetItem(str(timing['lap']))
            lap_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.lap_table.setItem(row, 0, lap_item)
            
            # Position
            pos_item = QTableWidgetItem(str(timing['position']))
            pos_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.lap_table.setItem(row, 1, pos_item)
            
            # Time
            time_item = QTableWidgetItem(timing['time'])
            time_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.lap_table.setItem(row, 2, time_item)
            
            # Driver - FIXED: Format driver name properly
            driver_id = timing['driverId']
            driver_name = self.format_driver_name(driver_id)
            driver_item = QTableWidgetItem(driver_name)
            self.lap_table.setItem(row, 3, driver_item)
    
    def format_driver_name(self, driver_id: str) -> str:
        """Format driver ID into proper name"""
        if driver_id == 'N/A':
            return 'N/A'
        
        # Common driver ID mappings (you can extend this)
        known_drivers = {
            'max_verstappen': 'Max Verstappen',
            'verstappen': 'Max Verstappen',
            'hamilton': 'Lewis Hamilton',
            'russell': 'George Russell',
            'leclerc': 'Charles Leclerc',
            'sainz': 'Carlos Sainz',
            'norris': 'Lando Norris',
            'piastri': 'Oscar Piastri',
            'alonso': 'Fernando Alonso',
            'stroll': 'Lance Stroll',
            'ocon': 'Esteban Ocon',
            'gasly': 'Pierre Gasly',
            'perez': 'Sergio Perez',
            'albon': 'Alexander Albon',
            'sargeant': 'Logan Sargeant',
            'hulkenberg': 'Nico Hulkenberg',
            'magnussen': 'Kevin Magnussen',
            'bottas': 'Valtteri Bottas',
            'zhou': 'Zhou Guanyu',
            'tsunoda': 'Yuki Tsunoda',
            'ricciardo': 'Daniel Ricciardo',
            'de_vries': 'Nyck de Vries',
            'lawson': 'Liam Lawson'
        }
        
        # Check if it's a known driver
        driver_id_lower = driver_id.lower()
        if driver_id_lower in known_drivers:
            return known_drivers[driver_id_lower]
        
        # Otherwise, format the ID nicely
        # Replace underscores with spaces and capitalize each word
        parts = driver_id.split('_')
        formatted_name = ' '.join(part.capitalize() for part in parts)
        
        return formatted_name
    
    def create_lap_history_table(self) -> QTableWidget:
        """Create enhanced lap history table"""
        table = QTableWidget()
        table.setStyleSheet("""
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
        """)
        
        headers = ["LAP", "POSITION", "TIME", "DRIVER"]
        table.setColumnCount(len(headers))
        table.setHorizontalHeaderLabels(headers)
        
        # Configure columns
        table.setColumnWidth(0, 80)
        table.setColumnWidth(1, 100)
        table.setColumnWidth(2, 150)
        table.setColumnWidth(3, 250)
        
        # Configure table behavior
        table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        table.setSortingEnabled(True)
        
        return table

class CompleteRaceResultsTab(QWidget):
    """Complete race results with all session types and history"""
    
    def __init__(self, race: Race):
        super().__init__()
        self.race = race
        self.data_service = EnhancedDataService()
        self.session_data = {}
        self.setup_ui()
        self.load_all_sessions()
    
    def setup_ui(self):
        """Setup complete race results UI"""
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
        
        # Enhanced race header
        header_widget = self.create_enhanced_race_header()
        layout.addWidget(header_widget)
        
        # Loading status
        self.loading_label = QLabel("Loading session data...")
        self.loading_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.loading_label.setStyleSheet("""
            QLabel {
                color: #ffffff;
                font-size: 18px;
                padding: 25px;
                background-color: #1a1a1a;
                border: 1px solid #333333;
                border-radius: 10px;
            }
        """)
        layout.addWidget(self.loading_label)
        
        # Enhanced sessions tab widget
        self.sessions_tab = DarkTabWidget()
        self.sessions_tab.hide()
        layout.addWidget(self.sessions_tab)
    
    def create_enhanced_race_header(self) -> QWidget:
        """Create enhanced race header"""
        header = QFrame()
        header.setFixedHeight(120)
        header.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                            stop:0 #1a1a1a, stop:1 #2d2d2d);
                border: 1px solid #333333;
                border-radius: 12px;
            }
        """)
        
        layout = QVBoxLayout(header)
        layout.setContentsMargins(25, 20, 25, 20)
        
        # Race name
        race_label = QLabel(self.race.race_name)
        race_label.setStyleSheet("""
            QLabel {
                color: #ffffff;
                font-size: 26px;
                font-weight: bold;
                margin-bottom: 8px;
            }
        """)
        layout.addWidget(race_label)
        
        # Enhanced race details
        details_layout = QHBoxLayout()
        
        circuit_label = QLabel(f"📍 {self.race.circuit}")
        circuit_label.setStyleSheet("""
            QLabel {
                color: #cccccc;
                font-size: 16px;
                padding: 6px 12px;
                background-color: #2a2a2a;
                border-radius: 6px;
                border-left: 3px solid #4dabf7;
            }
        """)
        details_layout.addWidget(circuit_label)
        
        details_layout.addStretch()
        
        date_label = QLabel(f"📅 {self.race.date}")
        date_label.setStyleSheet("""
            QLabel {
                color: #cccccc;
                font-size: 16px;
                padding: 6px 12px;
                background-color: #2a2a2a;
                border-radius: 6px;
                border-left: 3px solid #51cf66;
            }
        """)
        details_layout.addWidget(date_label)
        
        round_label = QLabel(f"Round {self.race.round}")
        round_label.setStyleSheet("""
            QLabel {
                color: #e10600;
                font-size: 16px;
                font-weight: bold;
                padding: 6px 12px;
                background-color: #2a2a2a;
                border-radius: 6px;
                border: 2px solid #e10600;
                margin-left: 20px;
            }
        """)
        details_layout.addWidget(round_label)
        
        layout.addLayout(details_layout)
        
        return header
    
    def load_all_sessions(self):
        """Load all available session data including advanced data"""
        self.session_loader = self.data_service.create_complete_session_loader(self.race.season, self.race.round)
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
        logger.info(f"✅ Loaded {session_name}: {len(results)} results")
    
    def on_session_error(self, session_name: str, error: str):
        """Handle session loading error"""
        logger.warning(f"❌ Error loading {session_name}: {error}")
    
    def on_all_sessions_loaded(self, all_data: Dict[str, List[Dict[str, Any]]]):
        """Handle all session data loaded"""
        self.session_data = all_data
        self.loading_label.hide()
        self.create_enhanced_session_tabs()
        self.sessions_tab.show()
    
    def create_enhanced_session_tabs(self):
        """Create enhanced tabs for each available session"""
        if not self.session_data:
            no_data_tab = self.create_no_data_tab()
            self.sessions_tab.addTab(no_data_tab, "ℹ️ No Data")
            return
        
        # Enhanced session order with icons
        session_order = [
            ("Qualifying", "⏱️ Qualifying"),
            ("Race", "🏁 Race"),
            ("Sprint", "⚡ Sprint"),
        ]
        
        # Add standard sessions
        for session_key, tab_label in session_order:
            if session_key in self.session_data and self.session_data[session_key]:
                session_tab = self.create_enhanced_session_tab(session_key, self.session_data[session_key])
                self.sessions_tab.addTab(session_tab, tab_label)
        
        # Add advanced data tabs
        if "Pit Stops" in self.session_data and self.session_data["Pit Stops"]:
            pit_tab = PitStopsTab(self.session_data["Pit Stops"])
            self.sessions_tab.addTab(pit_tab, "🔧 Pit Stops")
        
        if "Lap Times" in self.session_data and self.session_data["Lap Times"]:
            lap_tab = LapHistoryTab(self.session_data["Lap Times"])
            self.sessions_tab.addTab(lap_tab, "📊 Lap History")
        
        # If no sessions were added, show no data tab
        if self.sessions_tab.count() == 0:
            no_data_tab = self.create_no_data_tab()
            self.sessions_tab.addTab(no_data_tab, "ℹ️ No Data")
    
    def create_enhanced_session_tab(self, session_name: str, results: List[Dict[str, Any]]) -> QWidget:
        """Create enhanced tab for a specific session"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # Session info
        info_layout = QHBoxLayout()
        
        info_label = QLabel(f"{len(results)} results")
        info_label.setStyleSheet("""
            QLabel {
                color: #e10600;
                font-size: 16px;
                font-weight: bold;
                padding: 8px 12px;
                background-color: #2a2a2a;
                border-radius: 6px;
            }
        """)
        info_layout.addWidget(info_label)
        info_layout.addStretch()
        
        layout.addLayout(info_layout)
        
        # Enhanced results table
        table = self.create_enhanced_results_table(session_name, results)
        layout.addWidget(table)
        
        return widget
    
    def create_enhanced_results_table(self, session_name: str, results: List[Dict[str, Any]]) -> QTableWidget:
        """Create enhanced results table"""
        table = QTableWidget()
        table.setStyleSheet("""
            QTableWidget {
                background-color: #1a1a1a;
                gridline-color: #333333;
                color: #ffffff;
                border: 1px solid #333333;
                border-radius: 8px;
                selection-background-color: #e10600;
                selection-color: #ffffff;
                font-size: 14px;
            }
            QHeaderView::section {
                background-color: #e10600;
                color: #ffffff;
                padding: 14px 10px;
                border: none;
                font-weight: bold;
                font-size: 12px;
                text-transform: uppercase;
            }
            QTableWidget::item {
                padding: 12px 10px;
                border-bottom: 1px solid #2a2a2a;
            }
        """)
        
        # Configure table based on session type
        if "Practice" in session_name:
            self.setup_practice_table(table, results)
        elif "Sprint" in session_name and session_name != "Sprint Qualifying":
            self.setup_race_table(table, results, is_sprint=True)
        elif "Qualifying" in session_name:
            self.setup_qualifying_table(table, results)
        elif "Race" in session_name:
            self.setup_race_table(table, results)
        
        table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        
        return table
    
    def setup_qualifying_table(self, table: QTableWidget, results: List[Dict[str, Any]]):
        """Setup enhanced qualifying table"""
        headers = ["POS", "DRIVER", "TEAM", "Q1", "Q2", "Q3"]
        table.setColumnCount(len(headers))
        table.setHorizontalHeaderLabels(headers)
        table.setRowCount(len(results))
        
        # Configure column widths
        table.setColumnWidth(0, 70)
        table.setColumnWidth(1, 200)
        table.setColumnWidth(2, 200)
        table.setColumnWidth(3, 120)
        table.setColumnWidth(4, 120)
        table.setColumnWidth(5, 120)
        
        # Populate data
        for row, result in enumerate(results):
            # Enhanced podium highlighting
            position = result.get('position', '0')
            if position in ['1', '2', '3']:
                colors = {'1': "#FFD700", '2': "#C0C0C0", '3': "#CD7F32"}
                color = QColor(colors[position])
                
                for col in range(table.columnCount()):
                    item = table.item(row, col) or QTableWidgetItem()
                    item.setBackground(color)
                    item.setForeground(QColor("#000000"))
                    font = item.font()
                    font.setBold(True)
                    item.setFont(font)
            
            # Position
            pos_item = QTableWidgetItem(position)
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
            for i, q_session in enumerate(['Q1', 'Q2', 'Q3']):
                time_item = QTableWidgetItem(result.get(q_session, 'N/A'))
                time_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                table.setItem(row, 3 + i, time_item)
    
    def setup_race_table(self, table: QTableWidget, results: List[Dict[str, Any]], is_sprint: bool = False):
        """Setup enhanced race table"""
        headers = ["POS", "DRIVER", "TEAM", "LAPS", "TIME/RETIRED", "PTS", "STATUS"]
        table.setColumnCount(len(headers))
        table.setHorizontalHeaderLabels(headers)
        table.setRowCount(len(results))
        
        # Configure column widths
        table.setColumnWidth(0, 70)
        table.setColumnWidth(1, 180)
        table.setColumnWidth(2, 160)
        table.setColumnWidth(3, 80)
        table.setColumnWidth(4, 140)
        table.setColumnWidth(5, 70)
        table.setColumnWidth(6, 120)
        
        # Populate data
        for row, result in enumerate(results):
            # Enhanced podium highlighting
            position = result.get('position', '0')
            if position in ['1', '2', '3']:
                pos_colors = {'1': "#FFD700", '2': "#C0C0C0", '3': "#CD7F32"}
                color = QColor(pos_colors[position])
                
                pos_item = QTableWidgetItem(position)
                pos_item.setBackground(color)
                pos_item.setForeground(QColor("#000000"))
                font = pos_item.font()
                font.setBold(True)
                pos_item.setFont(font)
            else:
                pos_item = QTableWidgetItem(position)
            
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
            
            # Status
            status_item = QTableWidgetItem(result.get('status', 'N/A'))
            # Color code status
            status = result.get('status', 'N/A')
            if 'Finished' in status or '+' in status:
                status_item.setForeground(QColor("#51cf66"))
            elif 'Retired' in status or 'DNF' in status:
                status_item.setForeground(QColor("#ff6b6b"))
            else:
                status_item.setForeground(QColor("#ffd700"))
            
            table.setItem(row, 6, status_item)
    
    def create_no_data_tab(self) -> QWidget:
        """Create enhanced no data tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(40, 40, 40, 40)
        
        info_frame = QFrame()
        info_frame.setStyleSheet("""
            QFrame {
                background-color: #1a1a1a;
                border: 1px solid #333333;
                border-radius: 12px;
                padding: 40px;
            }
        """)
        
        info_layout = QVBoxLayout(info_frame)
        
        title_label = QLabel(f"🏁 {self.race.race_name}")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("""
            QLabel {
                color: #e10600;
                font-size: 28px;
                font-weight: bold;
                margin-bottom: 25px;
            }
        """)
        info_layout.addWidget(title_label)
        
        info_text = f"""
        <div style="text-align: center; color: #ffffff;">
            <p style="font-size: 18px; margin-bottom: 15px;"><strong>Circuit:</strong> {self.race.circuit}</p>
            <p style="font-size: 18px; margin-bottom: 15px;"><strong>Date:</strong> {self.race.date}</p>
            <p style="font-size: 18px; margin-bottom: 25px;"><strong>Round:</strong> {self.race.round}</p>
            
            <div style="background-color: #2a2a2a; padding: 25px; border-radius: 10px; border-left: 5px solid #ffc107;">
                <h3 style="color: #ffffff; margin-top: 0;">Session Results Not Available</h3>
                <p style="color: #cccccc; font-size: 16px;">
                    Session data is not available for this race. This could be because:
                </p>
                <ul style="text-align: left; color: #cccccc; margin: 20px 0; font-size: 16px;">
                    <li>The race hasn't taken place yet</li>
                    <li>Session data is not published in the API</li>
                    <li>Only Qualifying and Race data are available</li>
                    <li>Advanced data (pit stops, laps) may not be available for all races</li>
                </ul>
                <p style="color: #cccccc; margin-bottom: 0; font-size: 16px;">
                    Check back after the race weekend for complete session data.
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