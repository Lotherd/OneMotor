# ui/widgets/motogp_tab.py
"""
Widget para la pestaña de MotoGP
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QPushButton, 
                            QHBoxLayout, QTextEdit, QFrame)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QPixmap

from ui.styles.app_styles import AppStyles

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
        self.title_label = QLabel("🏍️ MotoGP - Próximamente")
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
        self.description_label = QLabel("""
        <h3>🚧 En Desarrollo</h3>
        <p>La sección de MotoGP está siendo desarrollada y incluirá:</p>
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
        
        features = [
            "📊 Standings del Campeonato Mundial",
            "📅 Calendario de Carreras 2025",
            "🏁 Resultados de Carreras en Tiempo Real",
            "⏱️ Tiempos de Clasificación",
            "🏆 Estadísticas de Pilotos y Equipos",
            "📰 Noticias de MotoGP",
            "📈 Análisis de Rendimiento"
        ]
        
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
        notify_title = QLabel("🔔 Mantente Informado")
        notify_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        notify_title.setStyleSheet(f"""
            QLabel {{
                color: #ff8c00;
                font-size: 18px;
                font-weight: bold;
                margin: 10px;
            }}
        """)
        notification_layout.addWidget(notify_title)
        
        # Texto informativo
        info_text = QLabel("""
        Mientras desarrollamos la sección de MotoGP, puedes seguir disfrutando 
        de todas las funcionalidades de Fórmula 1. Te notificaremos cuando 
        MotoGP esté disponible.
        """)
        info_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        info_text.setWordWrap(True)
        info_text.setStyleSheet(f"""
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
        notification_layout.addWidget(info_text)
        
        # Botones de acción
        button_layout = QHBoxLayout()
        
        self.f1_button = QPushButton("🏎️ Ir a Fórmula 1")
        self.f1_button.setStyleSheet(AppStyles.get_main_button_style())
        self.f1_button.clicked.connect(self.switch_to_f1)
        
        self.roadmap_button = QPushButton("🗺️ Ver Roadmap")
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
        from PyQt6.QtWidgets import QMessageBox
        
        roadmap_text = """
        🗺️ ROADMAP DE DESARROLLO
        
        📅 FASE 1 (Actual):
        ✅ Estructura base de la aplicación
        ✅ Integración con Ergast API (F1)
        ✅ Standings en tiempo real de F1
        
        📅 FASE 2 (Próxima):
        🔲 Calendario de carreras F1
        🔲 Resultados históricos F1
        🔲 Noticias de motorsport
        
        📅 FASE 3 (Futuro):
        🔲 API de MotoGP
        🔲 Standings de MotoGP
        🔲 Datos en tiempo real
        
        📅 FASE 4 (Avanzado):
        🔲 Telemetría detallada
        🔲 Análisis de performance
        🔲 Predicciones con ML
        """
        
        QMessageBox.information(self, "Roadmap de Desarrollo", roadmap_text)