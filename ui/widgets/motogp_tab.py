# ui/widgets/motogp_tab.py
"""
Widget for MotoGP tab with multi-language support and development roadmap

This module provides the MotoGP user interface that displays development
status, planned features, and roadmap information. It includes full
internationalization support and interactive elements for user engagement.

**Classes:**
    MotoGPTabWidget - Main widget for MotoGP tab with development information

**Author:** Lotherd
**Version:** 1.0.0
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QPushButton, 
                            QHBoxLayout, QTextEdit, QFrame, QMessageBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QPixmap

from ui.styles.app_styles import AppStyles
from utils.i18n import tr

class MotoGPTabWidget(QWidget):
    """Main widget for MotoGP tab displaying development status and roadmap"""
    
    """
    * Initializes the MotoGP tab widget with complete UI setup
    *
    * This constructor creates the MotoGP interface that informs users about
    * the development status, planned features, and provides navigation options
    * while the MotoGP functionality is being developed.
    *
    * **@return** None
    """
    def __init__(self):
        super().__init__()
        self.setup_ui()
    
    """
    * Sets up the complete user interface for the MotoGP development tab
    *
    * This method creates the entire layout including the title, development
    * status information, feature list, notification section, and action
    * buttons to provide a comprehensive development preview.
    *
    * **@return** None
    """
    def setup_ui(self):
        # Main layout
        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(20)
        
        # Title
        self.title_label = QLabel(tr("motogp_title"))
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label.setStyleSheet(f"""
            QLabel {{
                color: #ff8c00;
                font-size: 24px;
                font-weight: bold;
                margin: 20px;
                padding: 20px;
            }}
        """)
        self.layout.addWidget(self.title_label)
        
        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setStyleSheet("QFrame { color: #ddd; }")
        self.layout.addWidget(separator)
        
        # Description
        self.description_label = QLabel(f"""
        <h3>{tr("motogp_development")}</h3>
        <p>{tr("motogp_description")}</p>
        """)
        self.description_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.description_label.setStyleSheet(f"""
            QLabel {{
                color: #333;
                font-size: 16px;
                margin: 10px;
                padding: 20px;
                background-color: #f8f9fa;
                border-radius: 8px;
                border: 1px solid #e9ecef;
            }}
        """)
        self.layout.addWidget(self.description_label)
        
        # Future features list
        self.setup_features_list()
        
        # Notification button
        self.setup_notification_section()
        
        # Spacer
        self.layout.addStretch()
    
    """
    * Creates and configures the planned features list display
    *
    * This method builds the visual representation of planned MotoGP features
    * using translated text and styled labels to show users what functionality
    * will be available when development is complete.
    *
    * **@return** None
    """
    def setup_features_list(self):
        features_layout = QVBoxLayout()
        
        # Create labels for each feature
        self.feature_labels = []
        features = tr("motogp_features")
        
        for feature in features:
            feature_label = QLabel(feature)
            feature_label.setStyleSheet(f"""
                QLabel {{
                    color: #555;
                    font-size: 14px;
                    padding: 8px 20px;
                    margin: 2px;
                    background-color: white;
                    border-left: 4px solid #ff8c00;
                    border-radius: 4px;
                }}
            """)
            features_layout.addWidget(feature_label)
            self.feature_labels.append(feature_label)
        
        features_widget = QWidget()
        features_widget.setLayout(features_layout)
        features_widget.setMaximumWidth(500)
        
        # Center the widget
        center_layout = QHBoxLayout()
        center_layout.addStretch()
        center_layout.addWidget(features_widget)
        center_layout.addStretch()
        
        self.layout.addLayout(center_layout)
    
    """
    * Sets up the notification section with user engagement elements
    *
    * This method creates the notification area that keeps users informed
    * about development progress and provides action buttons for navigation
    * and additional information access.
    *
    * **@return** None
    """
    def setup_notification_section(self):
        notification_layout = QVBoxLayout()
        
        # Section title
        self.notify_title = QLabel(tr("motogp_notify_title"))
        self.notify_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.notify_title.setStyleSheet(f"""
            QLabel {{
                color: #ff8c00;
                font-size: 18px;
                font-weight: bold;
                margin: 10px;
            }}
        """)
        notification_layout.addWidget(self.notify_title)
        
        # Informative text
        self.info_text = QLabel(tr("motogp_notify_text"))
        self.info_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.info_text.setWordWrap(True)
        self.info_text.setStyleSheet(f"""
            QLabel {{
                color: #666;
                font-size: 14px;
                margin: 10px;
                padding: 15px;
                background-color: #fff8f0;
                border-radius: 6px;
                border: 1px solid #ffe4cc;
            }}
        """)
        notification_layout.addWidget(self.info_text)
        
        # Action buttons
        button_layout = QHBoxLayout()
        
        self.f1_button = QPushButton(tr("motogp_go_f1"))
        self.f1_button.setStyleSheet(AppStyles.get_main_button_style())
        self.f1_button.clicked.connect(self.switch_to_f1)
        
        self.roadmap_button = QPushButton(tr("motogp_roadmap"))
        self.roadmap_button.setStyleSheet(AppStyles.get_secondary_button_style())
        self.roadmap_button.clicked.connect(self.show_roadmap)
        
        button_layout.addStretch()
        button_layout.addWidget(self.f1_button)
        button_layout.addWidget(self.roadmap_button)
        button_layout.addStretch()
        
        notification_layout.addLayout(button_layout)
        
        # Centered container
        notification_widget = QWidget()
        notification_widget.setLayout(notification_layout)
        notification_widget.setMaximumWidth(600)
        
        center_layout = QHBoxLayout()
        center_layout.addStretch()
        center_layout.addWidget(notification_widget)
        center_layout.addStretch()
        
        self.layout.addLayout(center_layout)
    
    """
    * Switches the main application view to the F1 tab
    *
    * This method handles navigation from the MotoGP tab to the F1 tab by
    * finding the parent tab widget and changing the current index to
    * display the F1 functionality.
    *
    * **@return** None
    """
    def switch_to_f1(self):
        # Emit signal to change tab (will be connected from main_window)
        parent_tabs = self.parent()
        if hasattr(parent_tabs, 'setCurrentIndex'):
            parent_tabs.setCurrentIndex(0)  # F1 tab is first (index 0)
    
    """
    * Displays the comprehensive development roadmap in a dialog
    *
    * This method creates and shows a detailed roadmap dialog that outlines
    * the development phases for the MotoGP functionality, providing users
    * with transparency about the planned development timeline.
    *
    * **@return** None
    """
    def show_roadmap(self):
        # Build roadmap text with translations
        roadmap_items = []
        
        # Phase 1
        roadmap_items.append(tr("roadmap_phase1"))
        for item in tr("roadmap_phase1_items"):
            roadmap_items.append(item)
        roadmap_items.append("")
        
        # Phase 2
        roadmap_items.append(tr("roadmap_phase2"))
        for item in tr("roadmap_phase2_items"):
            roadmap_items.append(item)
        roadmap_items.append("")
        
        # Phase 3
        roadmap_items.append(tr("roadmap_phase3"))
        for item in tr("roadmap_phase3_items"):
            roadmap_items.append(item)
        roadmap_items.append("")
        
        # Phase 4
        roadmap_items.append(tr("roadmap_phase4"))
        for item in tr("roadmap_phase4_items"):
            roadmap_items.append(item)
        
        roadmap_text = tr("roadmap_title") + "\n\n" + "\n".join(roadmap_items)
        
        QMessageBox.information(self, tr("roadmap_title"), roadmap_text)
    
    """
    * Updates all translatable text elements when language changes
    *
    * This method refreshes all user-visible text in the MotoGP widget
    * including titles, descriptions, feature lists, and button text to
    * reflect the currently selected language setting.
    *
    * **@return** None
    """
    def update_translations(self):
        # Update title
        self.title_label.setText(tr("motogp_title"))
        
        # Update description
        self.description_label.setText(f"""
        <h3>{tr("motogp_development")}</h3>
        <p>{tr("motogp_description")}</p>
        """)
        
        # Update features
        features = tr("motogp_features")
        for i, feature_label in enumerate(self.feature_labels):
            if i < len(features):
                feature_label.setText(features[i])
        
        # Update notifications
        self.notify_title.setText(tr("motogp_notify_title"))
        self.info_text.setText(tr("motogp_notify_text"))
        
        # Update buttons
        self.f1_button.setText(tr("motogp_go_f1"))
        self.roadmap_button.setText(tr("motogp_roadmap"))