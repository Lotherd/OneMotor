# ui/main_window.py
"""
Enhanced main application window with official logos and modern colorful card design
"""

import logging
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QLabel, QPushButton, QFrame, QStackedWidget,
                            QMessageBox, QSizePolicy, QGraphicsDropShadowEffect)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QPropertyAnimation, QEasingCurve, QRect
from PyQt6.QtGui import (QAction, QFont, QPixmap, QPainter, QPainterPath, QBrush, 
                        QColor, QLinearGradient, QPen)
import os

from config.settings import AppConfig
from ui.widgets.f1_tab import F1TabWidget
from ui.widgets.motogp_tab import MotoGPTabWidget
from utils.i18n import tr, get_translation_manager, set_language

logger = logging.getLogger(__name__)

class ModernMotorsportCard(QFrame):
    """Modern colorful card widget with official motorsport branding"""
    
    clicked = pyqtSignal()
    
    def __init__(self, title: str, series_type: str):
        super().__init__()
        self.series_type = series_type
        self.is_hovered = False
        
        # Define colors and gradients for each series
        self.setup_series_colors()
        self.setup_ui(title)
        self.setup_styles()
        self.setup_animations()
        self.add_shadow_effect()
    
    def setup_series_colors(self):
        """Setup colors and gradients for each motorsport series"""
        if self.series_type == "f1":
            self.primary_color = "#e10600"
            self.secondary_color = "#ff0d00"
            self.gradient_start = "#e10600"
            self.gradient_end = "#ff4d4d"
            self.hover_color = "#ff1a0a"
            self.accent_color = "#ffffff"
            self.logo_path = "logo/f1_logo.png"
        else:  # motogp - Changed to BLUE theme
            self.primary_color = "#0066cc"
            self.secondary_color = "#3388ff"
            self.gradient_start = "#0066cc"
            self.gradient_end = "#66aaff"
            self.hover_color = "#3388ff"
            self.accent_color = "#ffffff"
            self.logo_path = "logo/motogp_logo.png"
    
    def setup_ui(self, title: str):
        """Setup modern card UI with official logos"""
        self.setFixedSize(380, 520)  # Taller cards like the reference
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Create main content widget
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(30, 50, 30, 50)
        content_layout.setSpacing(40)
        
        # Logo area - Official logos (moved to top, larger)
        logo_layout = QVBoxLayout()
        logo_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.logo_widget = self.create_official_logo()
        logo_layout.addWidget(self.logo_widget)
        
        content_layout.addLayout(logo_layout)
        
        # Add spacer to push content to center
        content_layout.addStretch(1)
        
        # Title with modern styling (larger and more prominent)
        self.title_label = QLabel(title)
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label.setStyleSheet(f"""
            QLabel {{
                font-size: 32px;
                font-weight: 700;
                color: {self.accent_color};
                background: transparent;
                letter-spacing: 2px;
                padding: 20px 15px;
                margin: 10px 0;
            }}
        """)
        content_layout.addWidget(self.title_label)
        
        # Subtitle/description (smaller, more subtle)
        subtitle_text = "World Championship" if self.series_type == "f1" else "MotoGP Championship"
        self.subtitle_label = QLabel(subtitle_text)
        self.subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.subtitle_label.setStyleSheet(f"""
            QLabel {{
                font-size: 16px;
                font-weight: 300;
                color: {self.accent_color};
                background: transparent;
                opacity: 0.9;
                padding-bottom: 30px;
                letter-spacing: 1px;
            }}
        """)
        content_layout.addWidget(self.subtitle_label)
        
        # Add bottom spacer
        content_layout.addStretch(1)
        
        layout.addWidget(content_widget)
    
    def create_official_logo(self) -> QWidget:
        """Create official logo widget for each series using PNG files"""
        logo_container = QWidget()
        logo_container.setFixedSize(300, 140)  # Slightly larger logo container
        
        # Try to load the PNG logo
        logo_label = QLabel()
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        if os.path.exists(self.logo_path):
            # Load and scale the PNG logo
            pixmap = QPixmap(self.logo_path)
            if not pixmap.isNull():
                # Scale the pixmap to fit the container while maintaining aspect ratio
                scaled_pixmap = pixmap.scaled(280, 120, Qt.AspectRatioMode.KeepAspectRatio, 
                                            Qt.TransformationMode.SmoothTransformation)
                logo_label.setPixmap(scaled_pixmap)
            else:
                # Fallback to text if image loading fails
                self.create_text_logo(logo_label)
        else:
            # Fallback to text if image doesn't exist
            self.create_text_logo(logo_label)
        
        # Clean logo container background - no gradients to avoid visual clutter
        logo_container.setStyleSheet(f"""
            QWidget {{
                background-color: {self.primary_color};
                border-radius: 20px;
                border: 2px solid {self.hover_color};
            }}
        """)
        
        # Layout for logo container
        container_layout = QVBoxLayout(logo_container)
        container_layout.setContentsMargins(10, 10, 10, 10)
        container_layout.addWidget(logo_label)
        
        return logo_container
    
    def create_text_logo(self, logo_label: QLabel):
        """Create text-based logo as fallback"""
        if self.series_type == "f1":
            logo_label.setText("F1")
            logo_label.setStyleSheet(f"""
                QLabel {{
                    font-size: 72px;
                    font-weight: bold;
                    color: {self.accent_color};
                    background: transparent;
                    font-family: 'Arial Black', sans-serif;
                }}
            """)
        else:
            logo_label.setText("MotoGP")
            logo_label.setStyleSheet(f"""
                QLabel {{
                    font-size: 36px;
                    font-weight: bold;
                    color: {self.accent_color};
                    background: transparent;
                    font-family: 'Arial', sans-serif;
                    letter-spacing: 2px;
                }}
            """)
    
    def setup_styles(self):
        """Setup modern gradient styles with dark theme"""
        self.setStyleSheet(f"""
            ModernMotorsportCard {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                            stop:0 #2c2c2c, 
                            stop:1 #1a1a1a);
                border: 2px solid {self.primary_color};
                border-radius: 25px;
            }}
        """)
    
    def add_shadow_effect(self):
        """Add drop shadow effect for dark theme"""
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(25)
        shadow.setXOffset(0)
        shadow.setYOffset(10)
        shadow.setColor(QColor(0, 0, 0, 150))  # Darker shadow for dark theme
        self.setGraphicsEffect(shadow)
    
    def setup_animations(self):
        """Setup smooth animations - FIXED: No infinite movement"""
        # Remove any existing animation
        self.scale_animation = None
        
        # Store original geometry to prevent drift
        self.original_geometry = None
    
    def enterEvent(self, event):
        """Handle mouse enter with modern effects - FIXED: No movement"""
        self.is_hovered = True
        
        # Store original geometry if not already stored
        if self.original_geometry is None:
            self.original_geometry = self.geometry()
        
        # Only change visual effects, no scaling/movement
        self.setStyleSheet(f"""
            ModernMotorsportCard {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                            stop:0 #3c3c3c, 
                            stop:1 #2a2a2a);
                border: 2px solid {self.hover_color};
                border-radius: 25px;
            }}
        """)
        
        # Enhanced shadow on hover
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(35)
        shadow.setXOffset(0)
        shadow.setYOffset(15)
        shadow.setColor(QColor(255, 255, 255, 60))  # White glow for dark theme
        self.setGraphicsEffect(shadow)
        
        super().enterEvent(event)
    
    def leaveEvent(self, event):
        """Handle mouse leave - FIXED: Reset to original state"""
        self.is_hovered = False
        
        # Reset to original visual state
        self.setStyleSheet(f"""
            ModernMotorsportCard {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                            stop:0 #2c2c2c, 
                            stop:1 #1a1a1a);
                border: 2px solid {self.primary_color};
                border-radius: 25px;
            }}
        """)
        
        # Reset shadow
        self.add_shadow_effect()
        super().leaveEvent(event)
    
    def lighten_color(self, color_hex: str) -> str:
        """Lighten a color for hover effects"""
        color = QColor(color_hex)
        h, s, v, a = color.getHsv()
        # Increase brightness
        v = min(255, int(v * 1.2))
        lighter_color = QColor.fromHsv(h, s, v, a)
        return lighter_color.name()
    
    def mousePressEvent(self, event):
        """Handle click with simple press feedback"""
        if event.button() == Qt.MouseButton.LeftButton:
            # Simple visual feedback without movement
            self.setStyleSheet(f"""
                ModernMotorsportCard {{
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                stop:0 #1c1c1c, 
                                stop:1 #0a0a0a);
                    border: 2px solid {self.hover_color};
                    border-radius: 25px;
                }}
            """)
            
            # Reset after short delay
            QTimer.singleShot(100, self.reset_hover_style)
            QTimer.singleShot(150, lambda: self.clicked.emit())
        super().mousePressEvent(event)
    
    def reset_hover_style(self):
        """Reset to hover style after click"""
        if self.is_hovered:
            self.setStyleSheet(f"""
                ModernMotorsportCard {{
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                stop:0 #3c3c3c, 
                                stop:1 #2a2a2a);
                    border: 2px solid {self.hover_color};
                    border-radius: 25px;
                }}
            """)

class MainWindow(QMainWindow):
    """Enhanced main application window with modern design"""
    
    def __init__(self):
        super().__init__()
        
        # Initialize translation manager
        self.translation_manager = get_translation_manager()
        saved_language = AppConfig.get_language()
        self.translation_manager.set_language(saved_language)
        self.translation_manager.language_changed.connect(self.on_language_changed)
        
        self.setup_window()
        self.setup_ui()
        self.setup_minimal_menu()
    
    def setup_window(self):
        """Configure window properties with dark theme"""
        self.setWindowTitle("Motorsport Dashboard")
        self.setGeometry(100, 100, 1400, 900)
        self.setMinimumSize(1200, 800)
        
        # Dark theme background
        self.setStyleSheet("""
            QMainWindow {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                            stop:0 #1a1a1a, stop:1 #2c2c2c);
                color: #ffffff;
            }
        """)
    
    def setup_ui(self):
        """Setup the modern user interface"""
        # Central widget with stacked layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(self.central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Stacked widget for different views
        self.stacked_widget = QStackedWidget()
        main_layout.addWidget(self.stacked_widget)
        
        # Create views
        self.create_home_view()
        self.create_f1_view()
        self.create_motogp_view()
        
        # Start with home view
        self.stacked_widget.setCurrentIndex(0)
    
    def create_home_view(self):
        """Create the modern home view with colorful cards and dark theme"""
        home_widget = QWidget()
        home_layout = QVBoxLayout(home_widget)
        home_layout.setContentsMargins(60, 60, 60, 60)
        home_layout.setSpacing(50)
        
        # Dark theme background
        home_widget.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                            stop:0 #1a1a1a, stop:1 #2c2c2c);
            }
        """)
        
        # Modern header with dark theme
        header_layout = QVBoxLayout()
        header_layout.setSpacing(20)
        
        # Main title with dark theme styling
        title_label = QLabel("MOTORSPORT")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("""
            QLabel {
                font-size: 56px;
                font-weight: 100;
                color: #ffffff;
                background: transparent;
                margin: 30px 0;
                letter-spacing: 12px;
            }
        """)
        header_layout.addWidget(title_label)
        
        # Subtitle with dark theme
        subtitle_label = QLabel("Choose Your Championship")
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle_label.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: 300;
                color: #cccccc;
                background: transparent;
                margin-bottom: 20px;
            }
        """)
        header_layout.addWidget(subtitle_label)
        
        home_layout.addLayout(header_layout)
        home_layout.addStretch()
        
        # Modern cards container
        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(60)
        cards_layout.setContentsMargins(100, 0, 100, 0)
        
        # F1 Card with official styling
        self.f1_card = ModernMotorsportCard(
            title="FORMULA 1",
            series_type="f1"
        )
        self.f1_card.clicked.connect(self.show_f1_view)
        cards_layout.addWidget(self.f1_card)
        
        # MotoGP Card with official styling
        self.motogp_card = ModernMotorsportCard(
            title="MOTOGP",
            series_type="motogp"
        )
        self.motogp_card.clicked.connect(self.show_motogp_view)
        cards_layout.addWidget(self.motogp_card)
        
        home_layout.addLayout(cards_layout)
        home_layout.addStretch()
        
        # Modern footer with dark theme
        footer_label = QLabel("Experience the thrill of motorsport data")
        footer_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        footer_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                color: #888888;
                background: transparent;
                margin: 40px 0;
                font-weight: 300;
                font-style: italic;
            }
        """)
        home_layout.addWidget(footer_label)
        
        self.stacked_widget.addWidget(home_widget)
    
    def create_f1_view(self):
        """Create F1 data view"""
        f1_container = QWidget()
        f1_layout = QVBoxLayout(f1_container)
        f1_layout.setContentsMargins(0, 0, 0, 0)
        
        # Modern header
        header_widget = self.create_modern_header("FORMULA 1", "#e10600")
        f1_layout.addWidget(header_widget)
        
        # F1 content with tabs
        self.f1_tab = F1TabWidget()
        f1_layout.addWidget(self.f1_tab)
        
        self.stacked_widget.addWidget(f1_container)
    
    def create_motogp_view(self):
        """Create MotoGP data view"""
        motogp_container = QWidget()
        motogp_layout = QVBoxLayout(motogp_container)
        motogp_layout.setContentsMargins(0, 0, 0, 0)
        
        # Modern header with BLUE color
        header_widget = self.create_modern_header("MOTOGP", "#0066cc")
        motogp_layout.addWidget(header_widget)
        
        # MotoGP content
        self.motogp_tab = MotoGPTabWidget()
        motogp_layout.addWidget(self.motogp_tab)
        
        self.stacked_widget.addWidget(motogp_container)
    
    def create_modern_header(self, title: str, color: str) -> QWidget:
        """Create modern header for content views with dark theme"""
        header_widget = QWidget()
        header_widget.setFixedHeight(90)
        header_widget.setStyleSheet(f"""
            QWidget {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                            stop:0 #2c2c2c, stop:1 #1a1a1a);
                border-bottom: 3px solid {color};
            }}
        """)
        
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(40, 0, 40, 0)
        
        # Modern back button with dark theme
        back_button = QPushButton("←")
        back_button.setFixedSize(60, 60)
        back_button.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                            stop:0 {color}, stop:1 {self.lighten_color(color)});
                color: white;
                border: none;
                border-radius: 30px;
                font-size: 24px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                            stop:0 {self.lighten_color(color)}, 
                            stop:1 {color});
            }}
            QPushButton:pressed {{
                background: {self.darken_color(color)};
            }}
        """)
        back_button.clicked.connect(self.show_home_view)
        header_layout.addWidget(back_button)
        
        # Modern title with dark theme
        title_label = QLabel(title)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet(f"""
            QLabel {{
                font-size: 36px;
                font-weight: 200;
                color: #ffffff;
                background: transparent;
                letter-spacing: 4px;
            }}
        """)
        header_layout.addWidget(title_label)
        
        # Spacer for symmetry
        spacer = QWidget()
        spacer.setFixedWidth(60)
        header_layout.addWidget(spacer)
        
        return header_widget
    
    def lighten_color(self, color_hex: str) -> str:
        """Lighten a color"""
        color = QColor(color_hex)
        h, s, v, a = color.getHsv()
        v = min(255, int(v * 1.3))
        lighter_color = QColor.fromHsv(h, s, v, a)
        return lighter_color.name()
    
    def darken_color(self, color: str) -> str:
        """Darken a color"""
        color_map = {
            "#e10600": "#b30500",
            "#0066cc": "#004499",  # Updated for blue MotoGP
            "#ff6600": "#cc5200"   # Keep for compatibility
        }
        return color_map.get(color, color)
    
    def setup_minimal_menu(self):
        """Setup modern menu bar with dark theme"""
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
        """Show the home view with animation"""
        self.stacked_widget.setCurrentIndex(0)
    
    def show_f1_view(self):
        """Show F1 view"""
        self.stacked_widget.setCurrentIndex(1)
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
        """Handle language change"""
        logger.info(f"Language changed to: {language_code}")
        self.setWindowTitle("Motorsport Dashboard")
    
    def closeEvent(self, event):
        """Handle application close"""
        event.accept()