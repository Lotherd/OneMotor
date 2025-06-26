"""
Enhanced main application window with exact card design integration
"""

import logging
import os
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QPushButton, QFrame, QStackedWidget,
    QMessageBox, QSizePolicy, QGraphicsDropShadowEffect,
    QApplication
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QPropertyAnimation, QEasingCurve, QRect, QSize
from PyQt6.QtGui import (
    QAction, QFont, QPixmap, QPainter, QPainterPath, QBrush, 
    QColor, QLinearGradient, QPen
)

from config.settings import AppConfig
from ui.widgets.f1_tab import F1TabWidget
from ui.widgets.motogp_tab import MotoGPTabWidget
from utils.i18n import tr, get_translation_manager, set_language
from utils.image_utils import ImageUtils

logger = logging.getLogger(__name__)

class ExactMotorsportCard(QFrame):
    """Exact recreation of the motorsport card design"""
    
    clicked = pyqtSignal()
    
    def __init__(self, title: str, subtitle: str, series_type: str):
        super().__init__()
        self.series_type = series_type
        self.is_hovered = False
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedSize(500, 600)  # Increased from 400x500 to 500x600
        
        self._build_ui(title, subtitle)
        self._apply_styles()
        self._add_shadow()
    
    def _build_ui(self, title: str, subtitle: str):
        """Build the exact card UI structure"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Main container
        container = QWidget()
        container.setStyleSheet("background: transparent;")
        vbox = QVBoxLayout(container)
        vbox.setContentsMargins(40, 35, 40, 35)  # Increased margins
        vbox.setSpacing(0)
        
        # Top accent line
        top_line = QFrame()
        top_line.setFixedHeight(4)
        top_line.setStyleSheet(f"background-color: {self._accent_color()}; border: none; border-radius: 2px;")
        vbox.addWidget(top_line)
        vbox.addStretch(1)
        
        # Logo area
        logo_widget = self._create_logo_widget()
        vbox.addWidget(logo_widget)
        
        # Middle separator with adjusted margins for larger cards
        separator = QFrame()
        separator.setFixedHeight(3)
        separator.setStyleSheet(f"background-color: {self._accent_color()}; border: none; margin: 25px 50px;")  # Increased margins
        vbox.addWidget(separator)
        
        # Text area
        text_widget = self._create_text_widget(title, subtitle)
        vbox.addWidget(text_widget)
        
        # Bottom accent line
        bottom_line = QFrame()
        bottom_line.setFixedHeight(4)
        bottom_line.setStyleSheet(f"background-color: {self._accent_color()}; border: none; border-radius: 2px;")
        vbox.addWidget(bottom_line)
        vbox.addStretch(1)
        
        layout.addWidget(container)
    
    def _accent_color(self) -> str:
        """Get accent color for the series"""
        return '#e10600' if self.series_type == 'f1' else '#1e88e5'
    
    def _gradient_stops(self) -> tuple:
        """Get gradient colors for the series"""
        if self.series_type == 'f1':
            return ('#7d1414', '#a01e1e')  # F1 red gradient
        else:
            return ('#1e3a5f', '#2e4a6f')  # MotoGP blue gradient
    
    def _create_logo_widget(self) -> QWidget:
        """Create the logo area with high-quality rendering and better centering"""
        widget = QWidget()
        widget.setStyleSheet("background: transparent;")
        widget.setFixedHeight(200)  # Increased from 160 to 200
        
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Logo label with larger size and better centering
        logo_label = QLabel()
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo_label.setFixedSize(420, 150)  # Increased from 340x120 to 420x150
        
        # Try to load high-quality logo
        logo_path = AppConfig.get_logo_path(self.series_type)
        if os.path.exists(logo_path):
            device_pixel_ratio = self.devicePixelRatio() or QApplication.instance().devicePixelRatio()
            pixmap = ImageUtils.load_high_quality_pixmap(logo_path, (400, 130), device_pixel_ratio)  # Increased target size
            
            if pixmap and not pixmap.isNull():
                ImageUtils.setup_high_quality_label(logo_label, pixmap)
                logger.info(f"Loaded logo for {self.series_type}")
            else:
                self._create_text_logo(logo_label)
        else:
            self._create_text_logo(logo_label)
        
        layout.addWidget(logo_label)
        return widget
    
    def _create_text_logo(self, label: QLabel):
        """Create text-based logo fallback with larger size"""
        if self.series_type == 'f1':
            label.setText("F1")
            label.setStyleSheet("""
                QLabel {
                    font-size: 110px;
                    font-weight: bold;
                    color: #ffffff;
                    background: transparent;
                    font-family: 'Arial Black', sans-serif;
                }
            """)
        else:
            label.setText("MotoGP")
            label.setStyleSheet("""
                QLabel {
                    font-size: 58px;
                    font-weight: bold;
                    color: #ffffff;
                    background: transparent;
                    font-family: 'Arial', sans-serif;
                    letter-spacing: 3px;
                }
            """)
    
    def _create_text_widget(self, title: str, subtitle: str) -> QWidget:
        """Create the text area with title and subtitle"""
        widget = QWidget()
        widget.setStyleSheet("background: transparent;")
        widget.setFixedHeight(140)  # Increased from 120 to 140
        
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)  # Increased spacing
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Main title with larger font
        title_label = QLabel(title)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("""
            QLabel {
                font-size: 48px;
                font-weight: 700;
                color: #ffffff;
                background: transparent;
                letter-spacing: 3px;
                margin: 0;
            }
        """)
        layout.addWidget(title_label)
        
        # Subtitle lines (split for better formatting)
        subtitle_parts = subtitle.split(' ', 1)
        for part in subtitle_parts:
            subtitle_label = QLabel(part)
            subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            subtitle_label.setStyleSheet("""
                QLabel {
                    font-size: 20px;
                    font-weight: 400;
                    color: #ffffff;
                    background: transparent;
                    letter-spacing: 2px;
                    margin: 0;
                }
            """)
            layout.addWidget(subtitle_label)
        
        return widget
    
    def _apply_styles(self):
        """Apply the gradient background styles"""
        gradient_start, gradient_end = self._gradient_stops()
        self.setStyleSheet(f"""
            ExactMotorsportCard {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                            stop:0 {gradient_start}, 
                            stop:1 {gradient_end});
                border: none;
                border-radius: 25px;
            }}
        """)
    
    def _add_shadow(self):
        """Add the drop shadow effect"""
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setOffset(0, 10)
        shadow.setColor(QColor(0, 0, 0, 100))
        self.setGraphicsEffect(shadow)
    
    def enterEvent(self, event):
        """Enhanced hover effect"""
        self.is_hovered = True
        hover_shadow = QGraphicsDropShadowEffect()
        hover_shadow.setBlurRadius(30)
        hover_shadow.setOffset(0, 15)
        hover_shadow.setColor(QColor(0, 0, 0, 200))
        self.setGraphicsEffect(hover_shadow)
        super().enterEvent(event)
    
    def leaveEvent(self, event):
        """Reset to normal shadow"""
        self.is_hovered = False
        self._add_shadow()
        super().leaveEvent(event)
    
    def mousePressEvent(self, event):
        """Handle click with visual feedback"""
        if event.button() == Qt.MouseButton.LeftButton:
            # Press effect
            press_shadow = QGraphicsDropShadowEffect()
            press_shadow.setBlurRadius(15)
            press_shadow.setOffset(0, 5)
            press_shadow.setColor(QColor(0, 0, 0, 100))
            self.setGraphicsEffect(press_shadow)
            
            # Reset after short delay
            QTimer.singleShot(100, self._reset_shadow_state)
            QTimer.singleShot(150, lambda: self.clicked.emit())
        
        super().mousePressEvent(event)
    
    def _reset_shadow_state(self):
        """Reset shadow to appropriate state based on hover"""
        if self.is_hovered:
            # Apply hover shadow
            hover_shadow = QGraphicsDropShadowEffect()
            hover_shadow.setBlurRadius(30)
            hover_shadow.setOffset(0, 15)
            hover_shadow.setColor(QColor(0, 0, 0, 200))
            self.setGraphicsEffect(hover_shadow)
        else:
            # Apply normal shadow
            self._add_shadow()

class MainWindow(QMainWindow):
    """Enhanced main application window with the new card design"""
    
    def __init__(self):
        super().__init__()
        
        # Initialize translation system
        self.translation_manager = get_translation_manager()
        saved_language = AppConfig.get_language()
        self.translation_manager.set_language(saved_language)
        self.translation_manager.language_changed.connect(self.on_language_changed)
        
        self.setup_window()
        self.setup_ui()
        self.setup_menu()
    
    def setup_window(self):
        """Configure main window properties"""
        self.setWindowTitle("Motorsport Dashboard")
        self.setGeometry(100, 100, 1400, 900)
        self.setMinimumSize(1200, 800)
        
        # Main window gradient background
        self.setStyleSheet("""
            QMainWindow {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                            stop:0 #1a1a1a, stop:1 #2d2d2d);
                color: #ffffff;
            }
        """)
    
    def setup_ui(self):
        """Setup the main user interface"""
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Stacked widget for different views
        self.stacked_widget = QStackedWidget()
        self.stacked_widget.setStyleSheet("background: transparent;")
        main_layout.addWidget(self.stacked_widget)
        
        # Create all views
        self.create_home_view()
        self.create_f1_view()
        self.create_motogp_view()
        
        # Start with home view
        self.stacked_widget.setCurrentIndex(0)
    
    def create_home_view(self):
        """Create the home view with the new card design"""
        home_widget = QWidget()
        home_widget.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        home_widget.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                            stop:0 #1a1a1a, stop:1 #2d2d2d);
            }
        """)
        
        layout = QVBoxLayout(home_widget)
        layout.setContentsMargins(60, 50, 60, 50)
        layout.setSpacing(0)
        
        # Header section
        header_layout = QVBoxLayout()
        header_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Main title
        title_label = QLabel("MOTORSPORT")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("""
            QLabel {
                background-color: transparent;
                font-size: 80px;
                font-weight: 300;
                color: #ffffff;
                letter-spacing: 25px;
                margin: 30px 0;
            }
        """)
        header_layout.addWidget(title_label)
        
        # Subtitle
        subtitle_label = QLabel("Choose Your Championship")
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle_label.setStyleSheet("""
            QLabel {
                background-color: transparent;
                font-size: 22px;
                font-weight: 300;
                color: #cccccc;
                letter-spacing: 2px;
                margin-bottom: 40px;
            }
        """)
        header_layout.addWidget(subtitle_label)
        
        layout.addLayout(header_layout)
        layout.addStretch(1)
        
        # Cards section with adjusted spacing for larger cards
        cards_widget = QWidget()
        cards_widget.setStyleSheet("background: transparent;")
        cards_layout = QHBoxLayout(cards_widget)
        cards_layout.setContentsMargins(60, 0, 60, 0)  # Reduced side margins to accommodate larger cards
        cards_layout.setSpacing(80)  # Reduced spacing between cards
        cards_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # F1 Card
        self.f1_card = ExactMotorsportCard("FORMULA 1", "WORLD CHAMPIONSHIP", "f1")
        self.f1_card.clicked.connect(self.show_f1_view)
        cards_layout.addWidget(self.f1_card)
        
        # MotoGP Card
        self.motogp_card = ExactMotorsportCard("MOTOGP", "MOTOGP CHAMPIONSHIP", "motogp")
        self.motogp_card.clicked.connect(self.show_motogp_view)
        cards_layout.addWidget(self.motogp_card)
        
        layout.addWidget(cards_widget)
        layout.addStretch(1)
        
        # Footer
        footer_label = QLabel("Experience the thrill of motorsport data")
        footer_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        footer_label.setStyleSheet("""
            QLabel {
                background-color: transparent;
                font-size: 18px;
                color: #999999;
                font-style: italic;
                margin: 40px 0;
                letter-spacing: 1px;
            }
        """)
        layout.addWidget(footer_label)
        
        self.stacked_widget.addWidget(home_widget)
    
    def create_f1_view(self):
        """Create F1 view with modern header"""
        f1_widget = QWidget()
        layout = QVBoxLayout(f1_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Header
        header = self.create_sub_header("FORMULA 1", "#e10600")
        layout.addWidget(header)
        
        # F1 content
        self.f1_tab = F1TabWidget()
        layout.addWidget(self.f1_tab)
        
        self.stacked_widget.addWidget(f1_widget)
    
    def create_motogp_view(self):
        """Create MotoGP view with modern header"""
        motogp_widget = QWidget()
        layout = QVBoxLayout(motogp_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Header
        header = self.create_sub_header("MOTOGP", "#0066cc")
        layout.addWidget(header)
        
        # MotoGP content
        self.motogp_tab = MotoGPTabWidget()
        layout.addWidget(self.motogp_tab)
        
        self.stacked_widget.addWidget(motogp_widget)
    
    def create_sub_header(self, title: str, color: str) -> QWidget:
        """Create modern header for sub-views"""
        header_widget = QWidget()
        header_widget.setFixedHeight(80)
        header_widget.setStyleSheet(f"""
            QWidget {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                            stop:0 #2c2c2c, stop:1 #1a1a1a);
                border-bottom: 3px solid {color};
            }}
        """)
        
        layout = QHBoxLayout(header_widget)
        layout.setContentsMargins(40, 0, 40, 0)
        
        # Back button
        back_button = QPushButton("←")
        back_button.setFixedSize(60, 60)
        back_button.setStyleSheet(f"""
            QPushButton {{
                background: {color};
                color: #ffffff;
                border: none;
                border-radius: 30px;
                font-size: 24px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background: {self.lighten_color(color)};
            }}
            QPushButton:pressed {{
                background: {self.darken_color(color)};
            }}
        """)
        back_button.clicked.connect(self.show_home_view)
        layout.addWidget(back_button)
        
        # Title
        title_label = QLabel(title)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("""
            QLabel {
                font-size: 32px;
                font-weight: 200;
                color: #ffffff;
                background: transparent;
                letter-spacing: 4px;
            }
        """)
        layout.addWidget(title_label)
        
        # Spacer for symmetry
        spacer = QWidget()
        spacer.setFixedWidth(60)
        layout.addWidget(spacer)
        
        return header_widget
    
    def setup_menu(self):
        """Setup the application menu"""
        menubar = self.menuBar()
        menubar.setStyleSheet("""
            QMenuBar {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                            stop:0 #2c2c2c, stop:1 #1a1a1a);
                color: #ffffff;
                border-bottom: 1px solid #444444;
                font-size: 14px;
                padding: 5px;
            }
            QMenuBar::item {
                padding: 10px 20px;
                background: transparent;
                border-radius: 8px;
                margin: 2px;
            }
            QMenuBar::item:selected {
                background-color: #404040;
            }
            QMenu {
                background-color: #2c2c2c;
                border: 1px solid #444444;
                border-radius: 10px;
                padding: 8px;
                color: #ffffff;
            }
            QMenu::item {
                padding: 10px 20px;
                border-radius: 6px;
            }
            QMenu::item:selected {
                background-color: #404040;
            }
        """)
        
        # Language menu
        lang_menu = menubar.addMenu("🌐 Language")
        
        en_action = QAction("🇺🇸 English", self)
        en_action.triggered.connect(lambda: self.change_language("en"))
        lang_menu.addAction(en_action)
        
        es_action = QAction("🇪🇸 Español", self)
        es_action.triggered.connect(lambda: self.change_language("es"))
        lang_menu.addAction(es_action)
    
    def show_home_view(self):
        """Show the home view"""
        self.stacked_widget.setCurrentIndex(0)
    
    def show_f1_view(self):
        """Show F1 view and trigger data loading"""
        self.stacked_widget.setCurrentIndex(1)
        # Auto-load F1 data after a short delay
        QTimer.singleShot(300, self.f1_tab.auto_load_initial_data)
    
    def show_motogp_view(self):
        """Show MotoGP view"""
        self.stacked_widget.setCurrentIndex(2)
    
    def change_language(self, language_code: str):
        """Change application language"""
        if self.translation_manager.set_language(language_code):
            AppConfig.set_language(language_code)
            QMessageBox.information(
                self,
                "Language Changed",
                "Language updated successfully."
            )
    
    def on_language_changed(self, language_code: str):
        """Handle language change event"""
        logger.info(f"Language changed to: {language_code}")
        self.setWindowTitle("Motorsport Dashboard")
    
    def lighten_color(self, color_hex: str) -> str:
        """Lighten a color for hover effects"""
        color = QColor(color_hex)
        h, s, v, a = color.getHsv()
        v = min(255, int(v * 1.3))
        lighter_color = QColor.fromHsv(h, s, v, a)
        return lighter_color.name()
    
    def darken_color(self, color: str) -> str:
        """Darken a color for press effects"""
        color_map = {
            "#e10600": "#b30500",
            "#0066cc": "#004499",
        }
        return color_map.get(color, color)
    
    def closeEvent(self, event):
        """Handle application close"""
        event.accept()