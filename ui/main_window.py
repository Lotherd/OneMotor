"""
Enhanced main application window with modern buttons and clean header
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

class MinimalistButton(QPushButton):
    """Ultra high-quality minimalist button with crisp PNG icons"""
    
    def __init__(self, icon_path: str, size: int = 24):
        super().__init__()
        self.icon_path = icon_path
        self.icon_size = size
        self.setup_style()
        self.setFixedSize(44, 44)  # Slightly larger for better visual quality
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.load_ultra_high_quality_icon()
    
    def load_ultra_high_quality_icon(self):
        """Load ultra high-quality PNG icon with multiple resolution support"""
        if os.path.exists(self.icon_path):
            try:
                from PyQt6.QtGui import QIcon
                
                # Create QIcon directly from file - this preserves maximum quality
                icon = QIcon(self.icon_path)
                
                # If we need white color, we'll use a different approach
                if not icon.isNull():
                    # Create multiple sizes for different DPI
                    sizes = [16, 20, 24, 32, 48, 64]  # Multiple resolutions
                    
                    # Load original high-res image
                    original = QPixmap(self.icon_path)
                    if original.isNull():
                        logger.warning(f"Could not load original icon: {self.icon_path}")
                        return
                    
                    # Create a new icon with multiple high-quality sizes
                    multi_icon = QIcon()
                    
                    for size in sizes:
                        # Scale with highest quality
                        scaled = original.scaled(
                            size * 2,  # Double size for better quality
                            size * 2,
                            Qt.AspectRatioMode.KeepAspectRatio,
                            Qt.TransformationMode.SmoothTransformation
                        )
                        
                        # Create white version with ultra-high quality
                        white_pixmap = self.create_white_icon(scaled)
                        
                        # Add to multi-resolution icon
                        multi_icon.addPixmap(white_pixmap)
                    
                    # Set the multi-resolution icon
                    self.setIcon(multi_icon)
                    self.setIconSize(QSize(self.icon_size, self.icon_size))
                    
                    logger.info(f"Loaded ultra-high quality icon: {self.icon_path}")
                else:
                    logger.warning(f"Icon is null: {self.icon_path}")
                    self.create_fallback_icon()
                    
            except Exception as e:
                logger.error(f"Error loading ultra-high quality icon {self.icon_path}: {e}")
                self.create_fallback_icon()
        else:
            logger.warning(f"Icon file not found: {self.icon_path}")
            self.create_fallback_icon()
    
    def create_white_icon(self, source_pixmap):
        """Create ultra-crisp white version of icon using advanced techniques"""
        # Create result pixmap with same size and transparency
        result = QPixmap(source_pixmap.size())
        result.fill(Qt.GlobalColor.transparent)
        
        # Ultra-high quality painter setup
        painter = QPainter(result)
        
        # Enable ALL quality hints
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, True)
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing, True)
        
        # Use a mask-based approach for better quality
        # First, create an alpha mask from the original
        painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceOver)
        painter.drawPixmap(0, 0, source_pixmap)
        
        # Then apply white color while preserving alpha
        painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceIn)
        painter.fillRect(result.rect(), QColor(255, 255, 255, 255))
        
        painter.end()
        return result
    
    def create_fallback_icon(self):
        """Create ultra-crisp fallback icon"""
        size = self.icon_size * 2  # Double resolution
        fallback = QPixmap(size, size)
        fallback.fill(Qt.GlobalColor.transparent)
        
        painter = QPainter(fallback)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        
        # Create a crisp geometric shape
        pen = QPen(QColor(255, 255, 255, 200), 3)
        painter.setPen(pen)
        
        # Draw a clean circle
        margin = size // 6
        painter.drawEllipse(margin, margin, size - 2*margin, size - 2*margin)
        painter.end()
        
        from PyQt6.QtGui import QIcon
        icon = QIcon()
        icon.addPixmap(fallback)
        self.setIcon(icon)
        self.setIconSize(QSize(self.icon_size, self.icon_size))
    
    def setup_style(self):
        """Setup ultra-clean button styling"""
        self.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                border-radius: 22px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.08);
                border-radius: 22px;
            }
            QPushButton:pressed {
                background-color: rgba(255, 255, 255, 0.15);
                border-radius: 22px;
            }
        """)

class MainWindow(QMainWindow):
    """Enhanced main application window with modern buttons and clean header"""
    
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
        """Create F1 view with modern clean header"""
        f1_widget = QWidget()
        layout = QVBoxLayout(f1_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Modern clean header
        header = self.create_modern_sub_header("FORMULA 1", "#e10600")
        layout.addWidget(header)
        
        # F1 content
        self.f1_tab = F1TabWidget()
        
        # Connect refresh signal from F1 tab to header refresh button
        # Note: refresh_button will be created in create_modern_sub_header
        
        layout.addWidget(self.f1_tab)
        
        self.stacked_widget.addWidget(f1_widget)
    
    def create_motogp_view(self):
        """Create MotoGP view with modern clean header"""
        motogp_widget = QWidget()
        layout = QVBoxLayout(motogp_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Modern clean header
        header = self.create_modern_sub_header("MOTOGP", "#0066cc")
        layout.addWidget(header)
        
        # MotoGP content
        self.motogp_tab = MotoGPTabWidget()
        layout.addWidget(self.motogp_tab)
        
        self.stacked_widget.addWidget(motogp_widget)
    
    def create_modern_sub_header(self, title: str, color: str) -> QWidget:
        """Create minimalist clean header for sub-views"""
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
        layout.setContentsMargins(30, 0, 30, 0)
        
        # Minimalist Home button with PNG icon
        self.home_button = MinimalistButton("logo/home.png", 20)
        self.home_button.clicked.connect(self.show_home_view)
        layout.addWidget(self.home_button)
        
        layout.addSpacing(20)
        
        # Title - centered
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
        layout.setStretchFactor(title_label, 1)  # Make title expand to center
        
        layout.addSpacing(20)
        
        # Minimalist Refresh button with PNG icon
        self.refresh_button = MinimalistButton("logo/refresh.png", 20)
        self.refresh_button.clicked.connect(self.refresh_current_data)
        layout.addWidget(self.refresh_button)
        
        return header_widget
    
    def refresh_current_data(self):
        """Refresh data for current tab"""
        current_index = self.stacked_widget.currentIndex()
        
        if current_index == 1:  # F1 view
            # Get current tab in F1 widget
            current_tab = self.f1_tab.tab_widget.currentIndex()
            if current_tab == 0:  # Standings tab
                self.f1_tab.standings_tab.load_standings()
            elif current_tab == 1:  # Calendar tab
                self.f1_tab.calendar_tab.load_calendar()
    
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
    
    def closeEvent(self, event):
        """Handle application close"""
        event.accept()