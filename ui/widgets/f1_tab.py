# ui/widgets/f1_tab.py
"""
Widget para la pestaña de Fórmula 1
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                            QLabel, QTableWidget, QTableWidgetItem, QMessageBox)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

from models.driver import DriverStanding
from ui.styles.app_styles import AppStyles
from services.data_service import DataService, DataLoader
from typing import List
import logging

logger = logging.getLogger(__name__)

class F1TabWidget(QWidget):
    """Widget principal para la pestaña de F1"""
    
    # Señales
    status_updated = pyqtSignal(str)  # Para actualizar la barra de estado
    
    def __init__(self):
        super().__init__()
        self.data_service = DataService()
        self.data_loader = None
        self.current_standings = []
        
        self.setup_ui()
        self.connect_signals()
    
    def setup_ui(self):
        """Configurar la interfaz de usuario"""
        
        # Layout principal
        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(16)
        
        # Título
        self.title_label = QLabel("🏎️ Fórmula 1 - Campeonato Mundial")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label.setStyleSheet(AppStyles.get_title_style(20))
        self.layout.addWidget(self.title_label)
        
        # Barra de acciones
        self.setup_action_bar()
        
        # Estado de carga
        self.status_label = QLabel("Listo para cargar datos...")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet(AppStyles.get_status_label_style())
        self.layout.addWidget(self.status_label)
        
        # Tabla de standings
        self.setup_standings_table()
    
    def setup_action_bar(self):
        """Configurar barra de acciones"""
        action_layout = QHBoxLayout()
        
        # Botón de actualizar
        self.refresh_button = QPushButton("🔄 Actualizar Standings")
        self.refresh_button.setStyleSheet(AppStyles.get_main_button_style())
        self.refresh_button.clicked.connect(self.load_standings)
        action_layout.addWidget(self.refresh_button)
        
        # Botón de exportar (futuro)
        self.export_button = QPushButton("📊 Exportar Datos")
        self.export_button.setStyleSheet(AppStyles.get_secondary_button_style())
        self.export_button.setEnabled(False)  # Deshabilitado por ahora
        action_layout.addWidget(self.export_button)
        
        # Espaciador
        action_layout.addStretch()
        
        # Info de temporada
        self.season_label = QLabel("Temporada 2025")
        self.season_label.setStyleSheet(f"""
            QLabel {{
                color: #666;
                font-size: 14px;
                font-weight: bold;
                padding: 8px;
            }}
        """)
        action_layout.addWidget(self.season_label)
        
        self.layout.addLayout(action_layout)
    
    def setup_standings_table(self):
        """Configurar tabla de standings"""
        self.standings_table = QTableWidget()
        self.standings_table.setColumnCount(7)
        self.standings_table.setHorizontalHeaderLabels([
            "POS", "PILOTO", "EQUIPO", "PTS", "VICTORIAS", "NACIONALIDAD", "CÓDIGO"
        ])
        
        # Aplicar estilos
        self.standings_table.setStyleSheet(AppStyles.get_table_style())
        
        # Configuración adicional
        self.standings_table.setAlternatingRowColors(True)
        self.standings_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.standings_table.setSortingEnabled(True)
        
        self.layout.addWidget(self.standings_table)
    
    def connect_signals(self):
        """Conectar señales"""
        pass
    
    def load_standings(self):
        """Cargar standings de F1"""
        if self.data_loader and self.data_loader.isRunning():
            logger.warning("Data loader already running")
            return
        
        # Crear y configurar loader
        self.data_loader = DataLoader(self.data_service)
        self.data_loader.loading_started.connect(self.on_loading_started)
        self.data_loader.data_loaded.connect(self.on_standings_loaded)
        self.data_loader.error_occurred.connect(self.on_error_occurred)
        self.data_loader.loading_finished.connect(self.on_loading_finished)
        
        # Iniciar carga
        self.data_loader.start()
    
    def on_loading_started(self):
        """Callback cuando inicia la carga"""
        self.status_label.setText("⏳ Cargando datos de F1...")
        self.status_label.setStyleSheet(AppStyles.get_status_label_style())
        self.refresh_button.setEnabled(False)
        self.refresh_button.setText("🔄 Cargando...")
        
        # Emitir señal para barra de estado principal
        self.status_updated.emit("Cargando standings de F1...")
    
    def on_standings_loaded(self, standings: List[DriverStanding]):
        """Callback cuando se cargan los standings"""
        try:
            self.current_standings = standings
            self.update_standings_table(standings)
            
            success_msg = f"✅ Datos actualizados - {len(standings)} pilotos cargados"
            self.status_label.setText(success_msg)
            self.status_label.setStyleSheet(AppStyles.get_success_style())
            
            # Habilitar botón de exportar
            self.export_button.setEnabled(True)
            
            logger.info(f"Successfully loaded {len(standings)} standings")
            self.status_updated.emit(f"F1 standings actualizados ({len(standings)} pilotos)")
            
        except Exception as e:
            logger.error(f"Error updating table: {e}")
            self.on_error_occurred(f"Error mostrando datos: {str(e)}")
    
    def on_error_occurred(self, error_message: str):
        """Callback cuando ocurre un error"""
        self.status_label.setText(f"❌ {error_message}")
        self.status_label.setStyleSheet(AppStyles.get_error_style())
        
        # Mostrar mensaje de error
        QMessageBox.warning(self, "Error", f"Error cargando datos:\n{error_message}")
        
        self.status_updated.emit(f"Error: {error_message}")
    
    def on_loading_finished(self):
        """Callback cuando termina la carga"""
        self.refresh_button.setEnabled(True)
        self.refresh_button.setText("🔄 Actualizar Standings")
    
    def update_standings_table(self, standings: List[DriverStanding]):
        """Actualizar tabla con los standings"""
        self.standings_table.setRowCount(len(standings))
        
        for row, standing in enumerate(standings):
            # Posición
            pos_item = QTableWidgetItem(str(standing.position))
            pos_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            pos_item.setFont(QFont("", 0, QFont.Weight.Bold))
            self.standings_table.setItem(row, 0, pos_item)
            
            # Piloto
            driver_item = QTableWidgetItem(standing.driver.full_name)
            driver_item.setFont(QFont("", 0, QFont.Weight.Bold))
            self.standings_table.setItem(row, 1, driver_item)
            
            # Equipo
            team_name = standing.constructors[0].name if standing.constructors else "N/A"
            self.standings_table.setItem(row, 2, QTableWidgetItem(team_name))
            
            # Puntos
            points_item = QTableWidgetItem(str(int(standing.points)))
            points_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            points_item.setFont(QFont("", 0, QFont.Weight.Bold))
            self.standings_table.setItem(row, 3, points_item)
            
            # Victorias
            wins_item = QTableWidgetItem(str(standing.wins))
            wins_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.standings_table.setItem(row, 4, wins_item)
            
            # Nacionalidad
            self.standings_table.setItem(row, 5, QTableWidgetItem(standing.driver.nationality))
            
            # Código
            code = standing.driver.code or "N/A"
            code_item = QTableWidgetItem(code)
            code_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.standings_table.setItem(row, 6, code_item)
        
        # Ajustar columnas
        self.standings_table.resizeColumnsToContents()
        
        # Establecer ancho mínimo para columnas importantes
        self.standings_table.setColumnWidth(0, 50)   # Posición
        self.standings_table.setColumnWidth(1, 200)  # Piloto
        self.standings_table.setColumnWidth(2, 180)  # Equipo
        self.standings_table.setColumnWidth(3, 80)   # Puntos
        self.standings_table.setColumnWidth(4, 80)   # Victorias
        self.standings_table.setColumnWidth(6, 80)   # Código