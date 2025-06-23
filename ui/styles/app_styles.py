from config.settings import AppConfig

class AppStyles:
    """Estilos CSS centralizados"""
    
    @staticmethod
    def get_main_button_style() -> str:
        """Estilo para botones principales"""
        return f"""
            QPushButton {{
                background-color: {AppConfig.COLORS['f1_red']};
                color: {AppConfig.COLORS['white']};
                border: none;
                padding: 12px 20px;
                font-size: 14px;
                font-weight: bold;
                border-radius: 6px;
                min-height: 20px;
            }}
            QPushButton:hover {{
                background-color: {AppConfig.COLORS['f1_red_hover']};
            }}
            QPushButton:pressed {{
                background-color: #a10400;
            }}
            QPushButton:disabled {{
                background-color: {AppConfig.COLORS['text_secondary']};
                color: #999999;
            }}
        """
    
    @staticmethod
    def get_secondary_button_style() -> str:
        """Estilo para botones secundarios"""
        return f"""
            QPushButton {{
                background-color: {AppConfig.COLORS['white']};
                color: {AppConfig.COLORS['text_primary']};
                border: 2px solid {AppConfig.COLORS['border']};
                padding: 10px 16px;
                font-size: 13px;
                border-radius: 6px;
                min-height: 16px;
            }}
            QPushButton:hover {{
                border-color: {AppConfig.COLORS['f1_red']};
                color: {AppConfig.COLORS['f1_red']};
            }}
            QPushButton:pressed {{
                background-color: {AppConfig.COLORS['background']};
            }}
        """
    
    @staticmethod
    def get_table_style() -> str:
        """Estilo para tablas"""
        return f"""
            QTableWidget {{
                gridline-color: {AppConfig.COLORS['border']};
                background-color: {AppConfig.COLORS['white']};
                alternate-background-color: {AppConfig.COLORS['background']};
                selection-background-color: {AppConfig.COLORS['f1_red']};
                selection-color: {AppConfig.COLORS['white']};
                border: 1px solid {AppConfig.COLORS['border']};
                border-radius: 4px;
            }}
            QHeaderView::section {{
                background-color: {AppConfig.COLORS['f1_red']};
                color: {AppConfig.COLORS['white']};
                padding: 12px 8px;
                border: none;
                font-weight: bold;
                font-size: 13px;
            }}
            QTableWidget::item {{
                padding: 8px;
                border-bottom: 1px solid {AppConfig.COLORS['border']};
            }}
            QTableWidget::item:selected {{
                background-color: {AppConfig.COLORS['f1_red']};
                color: {AppConfig.COLORS['white']};
            }}
        """
    
    @staticmethod
    def get_title_style(size: int = 18) -> str:
        """Estilo para títulos"""
        return f"""
            QLabel {{
                color: {AppConfig.COLORS['f1_red']};
                font-size: {size}px;
                font-weight: bold;
                margin: 10px;
                padding: 10px;
            }}
        """
    
    @staticmethod
    def get_status_label_style() -> str:
        """Estilo para etiquetas de estado"""
        return f"""
            QLabel {{
                color: {AppConfig.COLORS['text_secondary']};
                font-size: 13px;
                padding: 8px;
                margin: 4px;
                background-color: {AppConfig.COLORS['background']};
                border-radius: 4px;
            }}
        """
    
    @staticmethod
    def get_tab_style() -> str:
        """Estilo para pestañas"""
        return f"""
            QTabWidget::pane {{
                border: 1px solid {AppConfig.COLORS['border']};
                background-color: {AppConfig.COLORS['white']};
                border-radius: 4px;
            }}
            QTabBar::tab {{
                background-color: {AppConfig.COLORS['background']};
                color: {AppConfig.COLORS['text_primary']};
                padding: 12px 20px;
                margin-right: 2px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                font-weight: bold;
            }}
            QTabBar::tab:selected {{
                background-color: {AppConfig.COLORS['f1_red']};
                color: {AppConfig.COLORS['white']};
            }}
            QTabBar::tab:hover:!selected {{
                background-color: {AppConfig.COLORS['border']};
            }}
        """
    
    @staticmethod
    def get_success_style() -> str:
        """Estilo para mensajes de éxito"""
        return f"""
            QLabel {{
                color: {AppConfig.COLORS['success']};
                font-weight: bold;
                padding: 8px;
                background-color: #d4edda;
                border: 1px solid #c3e6cb;
                border-radius: 4px;
            }}
        """
    
    @staticmethod
    def get_error_style() -> str:
        """Estilo para mensajes de error"""
        return f"""
            QLabel {{
                color: {AppConfig.COLORS['error']};
                font-weight: bold;
                padding: 8px;
                background-color: #f8d7da;
                border: 1px solid #f5c6cb;
                border-radius: 4px;
            }}
        """