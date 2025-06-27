# ui/main_window.py
"""
Enhanced main application window with modern buttons and clean header design

This module provides the main application window that serves as the primary
interface for the motorsport dashboard. It includes navigation between F1 and
MotoGP sections, language management, and modern card-based home interface.

**Classes:**
    ExactMotorsportCard - High-quality motorsport series selection card
    MinimalistButton - Ultra high-quality minimalist button with PNG icons
    MainWindow - Main application window with navigation and language support

**Author:** Lotherd
**Version:** 1.0.0
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
    """Exact recreation of the motorsport card design with high-quality rendering"""
    
    clicked = pyqtSignal()
    
    """
    * Initializes a motorsport selection card with series-specific styling
    *
    * This constructor creates a high-quality card widget for motorsport series
    * selection with gradient backgrounds, logos, and interactive hover effects
    * designed to provide an engaging user experience.
    *
    * **@param** title String main title text for the card
    * **@param** subtitle String subtitle text for the card
    * **@param** series_type String type of series ('f1' or 'motogp')
    * **@return** None
    """
    def __init__(self, title: str, subtitle: str, series_type: str):
        super().__init__()
        self.series_type = series_type
        self.is_hovered = False
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedSize(500, 600)  # Increased from 400x500 to 500x600
        
        self._build_ui(title, subtitle)
        self._apply_styles()
        self._add_shadow()
    
    """
    * Builds the complete UI structure for the motorsport card
    *
    * This method creates the card layout including accent lines, logo area,
    * separator, and text sections with proper spacing and alignment for
    * a professional appearance.
    *
    * **@param** title String main title text to display
    * **@param** subtitle String subtitle text to display
    * **@return** None
    """
    def _build_ui(self, title: str, subtitle: str):
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
    
    """
    * Returns the accent color for the specific motorsport series
    *
    * This method provides the theme-appropriate accent color based on the
    * motorsport series type, using F1 red for Formula 1 and blue for MotoGP.
    *
    * **@return** String hex color code for the series accent color
    """
    def _accent_color(self) -> str:
        return '#e10600' if self.series_type == 'f1' else '#1e88e5'
    
    """
    * Returns the gradient color stops for the card background
    *
    * This method provides the gradient colors used for the card background
    * based on the motorsport series, creating distinct visual themes for
    * F1 and MotoGP cards.
    *
    * **@return** Tuple of (start_color, end_color) hex strings
    """
    def _gradient_stops(self) -> tuple:
        if self.series_type == 'f1':
            return ('#7d1414', '#a01e1e')  # F1 red gradient
        else:
            return ('#1e3a5f', '#2e4a6f')  # MotoGP blue gradient
    
    """
    * Creates the logo display area with high-quality rendering
    *
    * This method builds the logo section of the card with support for both
    * image logos and text fallbacks, using high-quality rendering techniques
    * for crisp display on all screen types.
    *
    * **@return** QWidget containing the logo display area
    """
    def _create_logo_widget(self) -> QWidget:
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
    
    """
    * Creates a text-based logo fallback when image loading fails
    *
    * This method generates styled text logos as fallbacks when image logos
    * are not available, ensuring the cards always display appropriately
    * styled branding for each motorsport series.
    *
    * **@param** label QLabel widget to apply the text logo styling to
    * **@return** None
    """
    def _create_text_logo(self, label: QLabel):
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
    
    """
    * Creates the text display area with title and subtitle
    *
    * This method builds the text section of the card with properly styled
    * title and subtitle labels that maintain visual hierarchy and readability
    * against the card's gradient background.
    *
    * **@param** title String main title text to display
    * **@param** subtitle String subtitle text to display
    * **@return** QWidget containing the text display area
    """
    def _create_text_widget(self, title: str, subtitle: str) -> QWidget:
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
    
    """
    * Applies gradient background styling to the card
    *
    * This method sets up the CSS gradient background styling for the card
    * using the appropriate colors for the motorsport series to create
    * visually distinct and appealing card designs.
    *
    * **@return** None
    """
    def _apply_styles(self):
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
    
    """
    * Adds drop shadow effect to enhance card visual depth
    *
    * This method applies a subtle drop shadow effect to the card to create
    * visual depth and separation from the background, enhancing the overall
    * professional appearance of the interface.
    *
    * **@return** None
    """
    def _add_shadow(self):
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setOffset(0, 10)
        shadow.setColor(QColor(0, 0, 0, 100))
        self.setGraphicsEffect(shadow)
    
    """
    * Handles mouse enter events for enhanced hover effects
    *
    * This method creates an enhanced hover effect by changing the shadow
    * properties when the mouse cursor enters the card area, providing
    * immediate visual feedback to the user.
    *
    * **@param** event QEvent object containing event information
    * **@return** None
    """
    def enterEvent(self, event):
        self.is_hovered = True
        hover_shadow = QGraphicsDropShadowEffect()
        hover_shadow.setBlurRadius(30)
        hover_shadow.setOffset(0, 15)
        hover_shadow.setColor(QColor(0, 0, 0, 200))
        self.setGraphicsEffect(hover_shadow)
        super().enterEvent(event)
    
    """
    * Handles mouse leave events to reset shadow to normal state
    *
    * This method resets the card's shadow effect back to the normal state
    * when the mouse cursor leaves the card area, completing the hover
    * interaction cycle.
    *
    * **@param** event QEvent object containing event information
    * **@return** None
    """
    def leaveEvent(self, event):
        self.is_hovered = False
        self._add_shadow()
        super().leaveEvent(event)
    
    """
    * Handles mouse press events with visual feedback and click emission
    *
    * This method processes mouse clicks on the card by providing immediate
    * visual feedback through shadow changes and emitting the clicked signal
    * after a brief delay for better user experience.
    *
    * **@param** event QMouseEvent object containing click information
    * **@return** None
    """
    def mousePressEvent(self, event):
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
    
    """
    * Resets shadow state based on current hover status
    *
    * This method restores the appropriate shadow effect based on whether
    * the mouse is currently hovering over the card, ensuring consistent
    * visual feedback throughout the interaction cycle.
    *
    * **@return** None
    """
    def _reset_shadow_state(self):
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
    """Ultra high-quality minimalist button with crisp PNG icons and smooth interactions"""
    
    """
    * Initializes a minimalist button with ultra high-quality icon rendering
    *
    * This constructor creates a button with minimalist design and ultra-crisp
    * icon rendering that supports multiple DPI levels and includes smooth
    * hover and press animations for premium user experience.
    *
    * **@param** icon_path String path to the PNG icon file
    * **@param** size Integer icon size in pixels
    * **@return** None
    """
    def __init__(self, icon_path: str, size: int = 24):
        super().__init__()
        self.icon_path = icon_path
        self.icon_size = size
        self.setup_style()
        self.setFixedSize(44, 44)  # Slightly larger for better visual quality
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.load_ultra_high_quality_icon()
    
    """
    * Loads ultra high-quality PNG icon with multiple resolution support
    *
    * This method implements advanced icon loading with support for multiple
    * resolutions, high-DPI displays, and automatic white color conversion
    * for dark theme compatibility.
    *
    * **@return** None
    """
    def load_ultra_high_quality_icon(self):
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
    
    """
    * Creates ultra-crisp white version of icon using advanced rendering techniques
    *
    * This method converts colored icons to white versions using advanced
    * composition techniques while preserving alpha transparency and
    * maintaining ultra-crisp rendering quality.
    *
    * **@param** source_pixmap QPixmap source icon to convert
    * **@return** QPixmap white version of the icon
    """
    def create_white_icon(self, source_pixmap):
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
    
    """
    * Creates ultra-crisp fallback icon when image loading fails
    *
    * This method generates a geometric fallback icon with clean lines and
    * appropriate styling when the specified icon file cannot be loaded,
    * ensuring buttons always display properly.
    *
    * **@return** None
    """
    def create_fallback_icon(self):
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
    
    """
    * Sets up ultra-clean button styling with hover and press effects
    *
    * This method applies minimalist styling to the button with subtle
    * transparency effects for hover and press states, creating a clean
    * and modern interface element.
    *
    * **@return** None
    """
    def setup_style(self):
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
    """Enhanced main application window with modern navigation and language support"""
    
    """
    * Initializes the main application window with complete setup
    *
    * This constructor creates the main window with translation system
    * initialization, UI setup, and menu configuration for the complete
    * motorsport dashboard application experience.
    *
    * **@return** None
    """
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
    
    """
    * Configures main window properties and styling
    *
    * This method sets up the window title, size, minimum dimensions, and
    * applies the main background gradient styling to create an attractive
    * and professional application appearance.
    *
    * **@return** None
    """
    def setup_window(self):
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
    
    """
    * Sets up the complete main user interface structure
    *
    * This method creates the central widget, stacked widget for navigation,
    * and all the main views including home, F1, and MotoGP interfaces
    * with proper layout and initialization.
    *
    * **@return** None
    """
    def setup_ui(self):
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
    
    """
    * Creates the home view with motorsport series selection cards
    *
    * This method builds the main home interface featuring large, interactive
    * cards for F1 and MotoGP selection with proper spacing, typography,
    * and visual hierarchy for an engaging user experience.
    *
    * **@return** None
    """
    def create_home_view(self):
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
    
    """
    * Creates the F1 view with modern clean header and content area
    *
    * This method builds the F1 interface including the navigation header
    * and the F1 tab widget with proper layout and styling for a cohesive
    * user experience within the F1 section.
    *
    * **@return** None
    """
    def create_f1_view(self):
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
    
    """
    * Creates the MotoGP view with modern clean header and content area
    *
    * This method builds the MotoGP interface including the navigation header
    * and the MotoGP tab widget with proper layout and styling consistent
    * with the overall application design.
    *
    * **@return** None
    """
    def create_motogp_view(self):
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
    
    """
    * Creates minimalist clean header for sub-views with navigation and actions
    *
    * This method builds the header bar for F1 and MotoGP views featuring
    * minimalist home and refresh buttons, centered title, and series-specific
    * color accent for visual consistency.
    *
    * **@param** title String title text to display in the header
    * **@param** color String hex color for the accent border
    * **@return** QWidget containing the complete header interface
    """
    def create_modern_sub_header(self, title: str, color: str) -> QWidget:
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
    
    """
    * Refreshes data for the currently active tab and section
    *
    * This method determines which view and tab are currently active and
    * triggers the appropriate data refresh operation for F1 standings
    * or calendar as needed.
    *
    * **@return** None
    """
    def refresh_current_data(self):
        current_index = self.stacked_widget.currentIndex()
        
        if current_index == 1:  # F1 view
            # Get current tab in F1 widget
            current_tab = self.f1_tab.tab_widget.currentIndex()
            if current_tab == 0:  # Standings tab
                self.f1_tab.standings_tab.load_standings()
            elif current_tab == 1:  # Calendar tab
                self.f1_tab.calendar_tab.load_calendar()
    
    """
    * Sets up the application menu bar with language selection
    *
    * This method creates the menu bar with language selection options and
    * applies dark theme styling consistent with the overall application
    * design for a cohesive user experience.
    *
    * **@return** None
    """
    def setup_menu(self):
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
    
    """
    * Navigates to the home view and resets the interface
    *
    * This method switches the stacked widget to display the home view
    * with the motorsport series selection cards, providing easy navigation
    * back to the main interface.
    *
    * **@return** None
    """
    def show_home_view(self):
        self.stacked_widget.setCurrentIndex(0)
    
    """
    * Navigates to F1 view and triggers automatic data loading
    *
    * This method switches to the F1 interface and initiates automatic
    * data loading after a brief delay to ensure smooth UI transitions
    * and optimal user experience.
    *
    * **@return** None
    """
    def show_f1_view(self):
        self.stacked_widget.setCurrentIndex(1)
        # Auto-load F1 data after a short delay
        QTimer.singleShot(300, self.f1_tab.auto_load_initial_data)
    
    """
    * Navigates to the MotoGP view interface
    *
    * This method switches the stacked widget to display the MotoGP view
    * with development information and planned features for the MotoGP
    * functionality.
    *
    * **@return** None
    """
    def show_motogp_view(self):
        self.stacked_widget.setCurrentIndex(2)
    
    """
    * Changes the application language and saves the preference
    *
    * This method updates the application language through the translation
    * manager, saves the preference to settings, and displays a confirmation
    * message to the user.
    *
    * **@param** language_code String language code (e.g., 'en', 'es')
    * **@return** None
    """
    def change_language(self, language_code: str):
        if self.translation_manager.set_language(language_code):
            AppConfig.set_language(language_code)
            QMessageBox.information(
                self,
                "Language Changed",
                "Language updated successfully."
            )
    
    """
    * Handles language change events from the translation manager
    *
    * This method responds to language change events by updating the window
    * title and logging the language change for debugging and monitoring
    * purposes.
    *
    * **@param** language_code String new language code that was set
    * **@return** None
    """
    def on_language_changed(self, language_code: str):
        logger.info(f"Language changed to: {language_code}")
        self.setWindowTitle("Motorsport Dashboard")
    
    """
    * Handles application close events with graceful shutdown
    *
    * This method processes the application close event and accepts it
    * to allow the application to shut down gracefully, ensuring proper
    * cleanup of resources and settings.
    *
    * **@param** event QCloseEvent object containing close event information
    * **@return** None
    """
    def closeEvent(self, event):
        event.accept()