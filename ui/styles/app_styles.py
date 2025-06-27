# ui/styles/app_styles.py
"""
Centralized CSS styles for consistent application theming

This module provides centralized styling definitions for all UI components
in the motorsport dashboard application. It ensures consistent visual
appearance across different widgets and components.

**Classes:**
    AppStyles - Static methods for generating CSS style strings

**Author:** Lotherd
**Version:** 1.0.0
"""

from config.settings import AppConfig

class AppStyles:
    """Centralized CSS style definitions for consistent application theming"""
    
    
    """
    * Generates CSS styling for primary action buttons
    *
    * This method creates the CSS style string for main action buttons using
    * the F1 red color theme. It includes hover and pressed states for
    * interactive feedback and disabled state styling.
    *
    * **@return** String containing complete CSS styling for main buttons
    """
    @staticmethod
    def get_main_button_style() -> str:
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
    
    
    """
    * Generates CSS styling for secondary action buttons
    *
    * This method creates the CSS style string for secondary buttons with
    * a white background and border styling. It includes hover effects
    * that change the border color to the F1 red theme.
    *
    * **@return** String containing complete CSS styling for secondary buttons
    """
    @staticmethod
    def get_secondary_button_style() -> str:
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
    
    
    """
    * Generates CSS styling for data table widgets
    *
    * This method creates comprehensive CSS styling for table widgets including
    * grid lines, selection colors, header styling, and scroll bar appearance.
    * It uses the F1 red theme for selections and headers.
    *
    * **@return** String containing complete CSS styling for table widgets
    """
    def get_table_style() -> str:
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
    
    
    """
    * Generates CSS styling for title labels with customizable size
    *
    * This method creates CSS styling for title labels using the F1 red color
    * theme. The font size can be customized while maintaining consistent
    * styling for margins, padding, and font weight.
    *
    * **@param** size Integer font size in pixels (default: 18)
    * **@return** String containing complete CSS styling for title labels
    """
    @staticmethod
    def get_title_style(size: int = 18) -> str:
        return f"""
            QLabel {{
                color: {AppConfig.COLORS['f1_red']};
                font-size: {size}px;
                font-weight: bold;
                margin: 10px;
                padding: 10px;
            }}
        """
    
    
    """
    * Generates CSS styling for status information labels
    *
    * This method creates CSS styling for status labels that display information
    * messages to users. It uses a subtle background color and secondary text
    * color for a non-intrusive appearance.
    *
    * **@return** String containing complete CSS styling for status labels
    """
    @staticmethod
    def get_status_label_style() -> str:
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
    
   
    """
    * Generates CSS styling for tab widget components
    *
    * This method creates comprehensive CSS styling for tab widgets including
    * the tab bar, individual tabs, and the main content pane. It uses the
    * F1 red theme for active tabs and includes hover effects.
    *
    * **@return** String containing complete CSS styling for tab widgets
    """
    @staticmethod
    def get_tab_style() -> str:
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
    
    
    """
    * Generates CSS styling for success message labels
    *
    * This method creates CSS styling for labels that display success messages
    * using green colors and appropriate background styling to clearly indicate
    * successful operations to the user.
    *
    * **@return** String containing complete CSS styling for success messages
    """
    @staticmethod
    def get_success_style() -> str:
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
    
    
    """
    * Generates CSS styling for error message labels
    *
    * This method creates CSS styling for labels that display error messages
    * using red colors and appropriate background styling to clearly indicate
    * error conditions to the user.
    *
    * **@return** String containing complete CSS styling for error messages
    """
    @staticmethod
    def get_error_style() -> str:
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