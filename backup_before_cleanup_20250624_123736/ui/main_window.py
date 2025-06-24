# ui/main_window.py
"""
Ventana principal de la aplicación con soporte multiidioma
"""

import logging
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QTabWidget, 
                            QStatusBar, QMenuBar, QMessageBox, QApplication)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QAction, QIcon, QActionGroup  # ← CORRECCIÓN: QActionGroup está en QtGui

from config.settings import AppConfig
from ui.widgets.f1_tab import F1TabWidget
from ui.widgets.motogp_tab import MotoGPTabWidget
from ui.styles.app_styles import AppStyles
from utils.i18n import tr, get_translation_manager, set_language

logger = logging.getLogger(__name__)

class MainWindow(QMainWindow):
    """Ventana principal de la aplicación"""
    
    def __init__(self):
        super().__init__()
        self.f1_tab = None
        self.motogp_tab = None
        
        # Configurar idioma inicial
        self.translation_manager = get_translation_manager()
        saved_language = AppConfig.get_language()
        self.translation_manager.set_language(saved_language)
        
        # Conectar señal de cambio de idioma
        self.translation_manager.language_changed.connect(self.on_language_changed)
        
        self.setup_window()
        self.setup_menu_bar()
        self.setup_ui()
        self.setup_status_bar()
        self.connect_signals()
        
        # Auto-cargar datos de F1 al inicio
        QTimer.singleShot(1000, self.auto_load_f1_data)
    
    def setup_window(self):
        """Configurar propiedades de la ventana"""
        self.setWindowTitle(tr("app_title", version=AppConfig.APP_VERSION))
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
        file_menu = menubar.addMenu(tr("menu_file"))
        
        # Acción Actualizar
        self.refresh_action = QAction(tr("menu_refresh"), self)
        self.refresh_action.setShortcut("F5")
        self.refresh_action.setStatusTip(tr("menu_refresh_tooltip"))
        self.refresh_action.triggered.connect(self.refresh_current_tab)
        file_menu.addAction(self.refresh_action)
        
        file_menu.addSeparator()
        
        # Acción Salir
        self.exit_action = QAction(tr("menu_exit"), self)
        self.exit_action.setShortcut("Ctrl+Q")
        self.exit_action.setStatusTip(tr("menu_exit_tooltip"))
        self.exit_action.triggered.connect(self.close)
        file_menu.addAction(self.exit_action)
        
        # Menú Ver
        view_menu = menubar.addMenu(tr("menu_view"))
        
        # Cambiar a F1
        self.f1_action = QAction(tr("menu_f1"), self)
        self.f1_action.setShortcut("Ctrl+1")
        self.f1_action.setStatusTip(tr("menu_f1_tooltip"))
        self.f1_action.triggered.connect(lambda: self.tabs.setCurrentIndex(0))
        view_menu.addAction(self.f1_action)
        
        # Cambiar a MotoGP
        self.motogp_action = QAction(tr("menu_motogp"), self)
        self.motogp_action.setShortcut("Ctrl+2")
        self.motogp_action.setStatusTip(tr("menu_motogp_tooltip"))
        self.motogp_action.triggered.connect(lambda: self.tabs.setCurrentIndex(1))
        view_menu.addAction(self.motogp_action)
        
        view_menu.addSeparator()
        
        # Submenú de idiomas
        language_menu = view_menu.addMenu(tr("menu_language"))
        self.setup_language_menu(language_menu)
        
        # Menú Ayuda
        help_menu = menubar.addMenu(tr("menu_help"))
        
        # Acción Acerca de
        self.about_action = QAction(tr("menu_about"), self)
        self.about_action.setStatusTip(tr("menu_about_tooltip"))
        self.about_action.triggered.connect(self.show_about)
        help_menu.addAction(self.about_action)
    
    def setup_language_menu(self, language_menu):
        """Configurar menú de idiomas"""
        self.language_action_group = QActionGroup(self)
        
        available_languages = self.translation_manager.get_available_languages()
        current_language = self.translation_manager.get_current_language()
        
        for lang_code, lang_name in available_languages.items():
            action = QAction(lang_name, self)
            action.setCheckable(True)
            action.setChecked(lang_code == current_language)
            action.setData(lang_code)
            action.triggered.connect(lambda checked, code=lang_code: self.change_language(code))
            
            self.language_action_group.addAction(action)
            language_menu.addAction(action)
    
    def change_language(self, language_code: str):
        """Cambiar idioma de la aplicación"""
        if self.translation_manager.set_language(language_code):
            # Guardar configuración
            AppConfig.set_language(language_code)
            
            # Mostrar mensaje de confirmación
            QMessageBox.information(
                self,
                tr("language_changed"),
                tr("restart_message")
            )
    
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
        self.tabs.addTab(self.f1_tab, tr("tab_f1"))
        
        # Pestaña MotoGP
        self.motogp_tab = MotoGPTabWidget()
        self.tabs.addTab(self.motogp_tab, tr("tab_motogp"))
        
        layout.addWidget(self.tabs)
    
    def setup_status_bar(self):
        """Configurar barra de estado"""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        # Mensaje inicial
        self.status_bar.showMessage(tr("ready_to_load"))
        
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
        tab_names = [tr("tab_f1").replace("🏎️ ", ""), tr("tab_motogp").replace("🏍️ ", "")]
        if 0 <= index < len(tab_names):
            self.update_status(tr("tab_active", tab=tab_names[index]))
    
    def refresh_current_tab(self):
        """Actualizar datos de la pestaña actual"""
        current_index = self.tabs.currentIndex()
        
        if current_index == 0 and self.f1_tab:
            # Actualizar F1
            self.f1_tab.load_standings()
            self.update_status(tr("f1_updating"))
            
        elif current_index == 1:
            # MotoGP - mostrar mensaje
            QMessageBox.information(
                self, 
                tr("motogp_dialog_title"), 
                tr("motogp_info")
            )
    
    def auto_load_f1_data(self):
        """Cargar automáticamente datos de F1 al inicio"""
        if self.f1_tab:
            self.update_status(tr("f1_loading_initial"))
            self.f1_tab.load_standings()
    
    def show_about(self):
        """Mostrar ventana Acerca de"""
        about_text = f"""
        <h2>{AppConfig.APP_NAME}</h2>
        <p><b>{tr("menu_about")}:</b> {AppConfig.APP_VERSION}</p>
        <p><b>{tr("about_description")}</b></p>
        
        <h3>{tr("about_features")}</h3>
        <ul>
            {"".join([f"<li>{feature}</li>" for feature in tr("about_features_list")])}
        </ul>
        
        <h3>{tr("about_apis")}</h3>
        <ul>
            {"".join([f"<li><b>{api}</b></li>" for api in tr("about_apis_list")])}
        </ul>
        
        <p><small>{tr("about_footer")}</small></p>
        """
        
        QMessageBox.about(self, tr("menu_about"), about_text)
    
    def closeEvent(self, event):
        """Manejar evento de cierre de la aplicación"""
        reply = QMessageBox.question(
            self,
            tr("confirm_exit"),
            tr("confirm_exit_message"),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            logger.info("Application closing")
            event.accept()
        else:
            event.ignore()
    
    def on_language_changed(self, language_code: str):
        """Callback cuando cambia el idioma"""
        logger.info(f"Language changed to: {language_code}")
        
        # Actualizar título de ventana
        self.setWindowTitle(tr("app_title", version=AppConfig.APP_VERSION))
        
        # Actualizar menús
        self.update_menu_texts()
        
        # Actualizar pestañas
        self.tabs.setTabText(0, tr("tab_f1"))
        self.tabs.setTabText(1, tr("tab_motogp"))
        
        # Actualizar barra de estado
        self.status_bar.showMessage(tr("ready_to_load"))
        
        # Actualizar widgets hijos
        if self.f1_tab:
            self.f1_tab.update_translations()
        if self.motogp_tab:
            self.motogp_tab.update_translations()
    
    def update_menu_texts(self):
        """Actualizar textos de los menús"""
        try:
            # Obtener la barra de menús y actualizar
            menubar = self.menuBar()
            
            # Limpiar y recrear menús
            menubar.clear()
            self.setup_menu_bar()
            
        except Exception as e:
            logger.error(f"Error updating menu texts: {e}")