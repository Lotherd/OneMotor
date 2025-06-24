# ui/widgets/motogp_tab.py
"""
Widget para la pestaña de MotoGP con soporte multiidioma
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QPushButton, 
                            QHBoxLayout, QTextEdit, QFrame, QMessageBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QPixmap

from ui.styles.app_styles import AppStyles
from utils.i18n import tr

class MotoGPTabWidget(QWidget):
    """Widget principal para la pestaña de MotoGP"""
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
    
    def setup_ui(self):
        """Configurar la interfaz de usuario"""
        
        # Layout principal
        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(20)
        
        # Título
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
        
        # Separador
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setStyleSheet("QFrame { color: #ddd; }")
        self.layout.addWidget(separator)
        
        # Descripción
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
        
        # Lista de características futuras
        self.setup_features_list()
        
        # Botón de notificaciones
        self.setup_notification_section()
        
        # Espaciador
        self.layout.addStretch()
    
    def setup_features_list(self):
        """Configurar lista de características futuras"""
        features_layout = QVBoxLayout()
        
        # Crear labels para cada característica
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
        
        # Centrar el widget
        center_layout = QHBoxLayout()
        center_layout.addStretch()
        center_layout.addWidget(features_widget)
        center_layout.addStretch()
        
        self.layout.addLayout(center_layout)
    
    def setup_notification_section(self):
        """Configurar sección de notificaciones"""
        notification_layout = QVBoxLayout()
        
        # Título de la sección
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
        
        # Texto informativo
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
        
        # Botones de acción
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
        
        # Contenedor centrado
        notification_widget = QWidget()
        notification_widget.setLayout(notification_layout)
        notification_widget.setMaximumWidth(600)
        
        center_layout = QHBoxLayout()
        center_layout.addStretch()
        center_layout.addWidget(notification_widget)
        center_layout.addStretch()
        
        self.layout.addLayout(center_layout)
    
    def switch_to_f1(self):
        """Cambiar a la pestaña de F1"""
        # Emitir señal para cambiar pestaña (se conectará desde main_window)
        parent_tabs = self.parent()
        if hasattr(parent_tabs, 'setCurrentIndex'):
            parent_tabs.setCurrentIndex(0)  # Pestaña F1 es la primera (índice 0)
    
    def show_roadmap(self):
        """Mostrar roadmap de desarrollo"""
        
        # Construir texto del roadmap con traducciones
        roadmap_items = []
        
        # Fase 1
        roadmap_items.append(tr("roadmap_phase1"))
        for item in tr("roadmap_phase1_items"):
            roadmap_items.append(item)
        roadmap_items.append("")
        
        # Fase 2
        roadmap_items.append(tr("roadmap_phase2"))
        for item in tr("roadmap_phase2_items"):
            roadmap_items.append(item)
        roadmap_items.append("")
        
        # Fase 3
        roadmap_items.append(tr("roadmap_phase3"))
        for item in tr("roadmap_phase3_items"):
            roadmap_items.append(item)
        roadmap_items.append("")
        
        # Fase 4
        roadmap_items.append(tr("roadmap_phase4"))
        for item in tr("roadmap_phase4_items"):
            roadmap_items.append(item)
        
        roadmap_text = tr("roadmap_title") + "\n\n" + "\n".join(roadmap_items)
        
        QMessageBox.information(self, tr("roadmap_title"), roadmap_text)
    
    def update_translations(self):
        """Actualizar traducciones cuando cambia el idioma"""
        # Actualizar título
        self.title_label.setText(tr("motogp_title"))
        
        # Actualizar descripción
        self.description_label.setText(f"""
        <h3>{tr("motogp_development")}</h3>
        <p>{tr("motogp_description")}</p>
        """)
        
        # Actualizar características
        features = tr("motogp_features")
        for i, feature_label in enumerate(self.feature_labels):
            if i < len(features):
                feature_label.setText(features[i])
        
        # Actualizar notificaciones
        self.notify_title.setText(tr("motogp_notify_title"))
        self.info_text.setText(tr("motogp_notify_text"))
        
        # Actualizar botones
        self.f1_button.setText(tr("motogp_go_f1"))
        self.roadmap_button.setText(tr("motogp_roadmap"))