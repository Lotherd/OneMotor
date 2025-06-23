# ui/main_window.py
"""
Ventana principal de la aplicación
"""

import logging
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QTabWidget, 
                            QStatusBar, QMenuBar, QMessageBox, QApplication)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QAction, QIcon

from config.settings import AppConfig
from ui.widgets.f1_tab import F1TabWidget
from ui.widgets.motogp_tab import MotoGPTabWidget
from ui.styles.app_styles import AppStyles

logger = logging.getLogger(__name__)

class MainWindow(QMainWindow):
    """Ventana principal de la aplicación"""
    
    def __init__(self):
        super().__init__()
        self.f1_tab = None
        self.motogp_tab = None
        
        self.setup_window()
        self.setup_menu_bar()
        self.setup_ui()
        self.setup_status_bar()
        self.connect_signals()
        
        # Auto-cargar datos de F1 al inicio
        QTimer.singleShot(1000, self.auto_load_f1_data)
    
    def setup_window(self):
        """Configurar propiedades de la ventana"""
        self.setWindowTitle(AppConfig.WINDOW_TITLE)
        self.setGeometry(100, 100, AppConfig.WINDOW_WIDTH, AppConfig.WINDOW_HEIGHT)
        self.setMinimumSize(AppConfig.WINDOW_MIN_WIDTH, AppConfig.WINDOW_MIN_HEIGHT)
        
        # Configurar ícono (si existe)
        try:
            self.setWindowIcon(QIcon("assets/icon.png"))
        except:
            pass  # No hay problema si no existe el ícono
    
    def setup_menu_bar(self):
        """Configurar barra de menús"""
        menubar = self.menuBar()
        
        # Menú Archivo
        file_menu = menubar.addMenu("&Archivo")
        
        # Acción Actualizar
        refresh_action = QAction("&Actualizar Datos", self)
        refresh_action.setShortcut("F5")
        refresh_action.setStatusTip("Actualizar datos de la pestaña actual")
        refresh_action.triggered.connect(self.refresh_current_tab)
        file_menu.addAction(refresh_action)
        
        file_menu.addSeparator()
        
        # Acción Salir
        exit_action = QAction("&Salir", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.setStatusTip("Salir de la aplicación")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Menú Ver
        view_menu = menubar.addMenu("&Ver")
        
        # Cambiar a F1
        f1_action = QAction("Fórmula &1", self)
        f1_action.setShortcut("Ctrl+1")
        f1_action.setStatusTip("Cambiar a la pestaña de Fórmula 1")
        f1_action.triggered.connect(lambda: self.tabs.setCurrentIndex(0))
        view_menu.addAction(f1_action)
        
        # Cambiar a MotoGP
        motogp_action = QAction("&MotoGP", self)
        motogp_action.setShortcut("Ctrl+2")
        motogp_action.setStatusTip("Cambiar a la pestaña de MotoGP")
        motogp_action.triggered.connect(lambda: self.tabs.setCurrentIndex(1))
        view_menu.addAction(motogp_action)
        
        # Menú Ayuda
        help_menu = menubar.addMenu("&Ayuda")
        
        # Acción Acerca de
        about_action = QAction("&Acerca de", self)
        about_action.setStatusTip("Información sobre la aplicación")
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def setup_ui(self):
        """Configurar la interfaz de usuario"""
        
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout principal
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Pestañas principales
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet(AppStyles.get_tab_style())
        
        # Pestaña F1
        self.f1_tab = F1TabWidget()
        self.tabs.addTab(self.f1_tab, "🏎️ Fórmula 1")
        
        # Pestaña MotoGP
        self.motogp_tab = MotoGPTabWidget()
        self.tabs.addTab(self.motogp_tab, "🏍️ MotoGP")
        
        layout.addWidget(self.tabs)
    
    def setup_status_bar(self):
        """Configurar barra de estado"""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        # Mensaje inicial
        self.status_bar.showMessage("Aplicación iniciada - Listo para cargar datos")
        
        # Estilo de la barra de estado
        self.status_bar.setStyleSheet(f"""
            QStatusBar {{
                background-color: {AppConfig.COLORS['background']};
                color: {AppConfig.COLORS['text_secondary']};
                border-top: 1px solid {AppConfig.COLORS['border']};
                padding: 4px;
            }}
        """)
    
    def connect_signals(self):
        """Conectar señales entre componentes"""
        
        # Conectar señales del tab F1 con la barra de estado
        if self.f1_tab:
            self.f1_tab.status_updated.connect(self.update_status)
        
        # Conectar cambio de pestañas
        self.tabs.currentChanged.connect(self.on_tab_changed)
    
    def update_status(self, message: str):
        """Actualizar mensaje en la barra de estado"""
        self.status_bar.showMessage(message)
        logger.info(f"Status updated: {message}")
    
    def on_tab_changed(self, index: int):
        """Callback cuando se cambia de pestaña"""
        tab_names = ["Fórmula 1", "MotoGP"]
        if 0 <= index < len(tab_names):
            self.update_status(f"Pestaña activa: {tab_names[index]}")
    
    def refresh_current_tab(self):
        """Actualizar datos de la pestaña actual"""
        current_index = self.tabs.currentIndex()
        
        if current_index == 0 and self.f1_tab:
            # Actualizar F1
            self.f1_tab.load_standings()
            self.update_status("Actualizando datos de F1...")
            
        elif current_index == 1:
            # MotoGP - mostrar mensaje
            QMessageBox.information(
                self, 
                "MotoGP", 
                "La sección de MotoGP está en desarrollo.\nPróximamente disponible."
            )
    
    def auto_load_f1_data(self):
        """Cargar automáticamente datos de F1 al inicio"""
        if self.f1_tab:
            self.update_status("Cargando datos iniciales de F1...")
            self.f1_tab.load_standings()
    
    def show_about(self):
        """Mostrar ventana Acerca de"""
        about_text = f"""
        <h2>{AppConfig.APP_NAME}</h2>
        <p><b>Versión:</b> {AppConfig.APP_VERSION}</p>
        <p><b>Descripción:</b> Aplicación de escritorio para seguir Fórmula 1 y MotoGP</p>
        
        <h3>Características:</h3>
        <ul>
            <li>📊 Standings en tiempo real de F1</li>
            <li>📅 Calendario de carreras</li>
            <li>📰 Noticias de motorsport</li>
            <li>📈 Análisis de datos (próximamente)</li>
            <li>🏍️ MotoGP (en desarrollo)</li>
        </ul>
        
        <h3>APIs utilizadas:</h3>
        <ul>
            <li><b>Ergast API:</b> Datos históricos y standings de F1</li>
            <li><b>News API:</b> Noticias de motorsport</li>
        </ul>
        
        <p><small>Desarrollado con Python y PyQt6</small></p>
        """
        
        QMessageBox.about(self, "Acerca de", about_text)
    
    def closeEvent(self, event):
        """Manejar evento de cierre de la aplicación"""
        reply = QMessageBox.question(
            self,
            "Confirmar Salida",
            "¿Estás seguro que quieres salir de la aplicación?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            logger.info("Application closing")
            event.accept()
        else:
            event.ignore()