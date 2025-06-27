# utils/image_utils.py
"""
High-quality image loading and processing utilities for optimal display

This module provides advanced image processing capabilities optimized for
high-DPI displays and professional visual quality. It includes support for
multiple resolution scaling, color conversion, and fallback generation.

**Classes:**
    ImageUtils - Static utility methods for image processing and optimization

**Author:** Lotherd
**Version:** 1.0.0
"""

import os
import logging
from pathlib import Path
from typing import Optional, Tuple
from PyQt6.QtGui import QPixmap, QPainter, QColor, QBrush, QPen
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtWidgets import QWidget, QLabel

logger = logging.getLogger(__name__)

class ImageUtils:
    """Static utilities for high-quality image loading and processing operations"""
    
    
    """
    * Loads a high-quality pixmap with proper scaling and anti-aliasing
    *
    * This method loads an image file and scales it to the target size using
    * high-quality rendering techniques. It supports high-DPI displays and
    * optional background color application for transparent images.
    *
    * **@param** image_path String path to the image file to load
    * **@param** target_size Tuple of (width, height) for target dimensions
    * **@param** device_pixel_ratio Float device pixel ratio for high-DPI support
    * **@param** background_color Optional QColor for transparent image backgrounds
    * **@return** QPixmap high-quality scaled image or None if loading fails
    """
    @staticmethod
    def load_high_quality_pixmap(
        image_path: str,
        target_size: Tuple[int, int],
        device_pixel_ratio: float = 1.0,
        background_color: Optional[QColor] = None
    ) -> Optional[QPixmap]:
        try:
            if not os.path.exists(image_path):
                logger.warning(f"Image file not found: {image_path}")
                return None
            
            # Load original image
            original_pixmap = QPixmap(image_path)
            if original_pixmap.isNull():
                logger.error(f"Failed to load image: {image_path}")
                return None
            
            # Calculate target size with device pixel ratio
            target_width, target_height = target_size
            scaled_width = int(target_width * device_pixel_ratio)
            scaled_height = int(target_height * device_pixel_ratio)
            
            # Create high-quality scaled pixmap
            scaled_pixmap = original_pixmap.scaled(
                scaled_width,
                scaled_height,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            
            # Set device pixel ratio for crisp rendering on high-DPI displays
            scaled_pixmap.setDevicePixelRatio(device_pixel_ratio)
            
            # Add background if specified (useful for transparent images)
            if background_color:
                final_pixmap = QPixmap(scaled_width, scaled_height)
                final_pixmap.setDevicePixelRatio(device_pixel_ratio)
                final_pixmap.fill(background_color)
                
                painter = QPainter(final_pixmap)
                painter.setRenderHint(QPainter.RenderHint.Antialiasing)
                painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
                
                # Center the image
                x = (scaled_width - scaled_pixmap.width()) // 2
                y = (scaled_height - scaled_pixmap.height()) // 2
                painter.drawPixmap(x, y, scaled_pixmap)
                painter.end()
                
                return final_pixmap
            
            logger.info(f"Successfully loaded high-quality image: {image_path}")
            return scaled_pixmap
            
        except Exception as e:
            logger.error(f"Error loading image {image_path}: {e}")
            return None
    
    
    """
    * Creates a high-quality fallback logo when image loading fails
    *
    * This method generates a professional-looking fallback logo with series-
    * specific styling and typography when the actual logo image cannot be
    * loaded, ensuring consistent visual presentation.
    *
    * **@param** series_type String type of series ('f1' or 'motogp')
    * **@param** size Tuple of (width, height) for logo dimensions
    * **@param** device_pixel_ratio Float device pixel ratio for scaling
    * **@param** text_color QColor for text rendering
    * **@param** background_color QColor for background fill
    * **@return** QPixmap high-quality fallback logo
    """
    @staticmethod
    def create_fallback_logo(
        series_type: str,
        size: Tuple[int, int],
        device_pixel_ratio: float = 1.0,
        text_color: QColor = QColor("#ffffff"),
        background_color: QColor = QColor("#e10600")
    ) -> QPixmap:
        try:
            width, height = size
            scaled_width = int(width * device_pixel_ratio)
            scaled_height = int(height * device_pixel_ratio)
            
            # Create pixmap
            pixmap = QPixmap(scaled_width, scaled_height)
            pixmap.setDevicePixelRatio(device_pixel_ratio)
            pixmap.fill(Qt.GlobalColor.transparent)
            
            # Setup painter with high-quality rendering
            painter = QPainter(pixmap)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            painter.setRenderHint(QPainter.RenderHint.TextAntialiasing)
            painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
            
            # Set background
            painter.fillRect(pixmap.rect(), background_color)
            
            # Configure text
            painter.setPen(QPen(text_color))
            
            if series_type == "f1":
                # F1 logo styling
                font = painter.font()
                font.setFamily("Arial Black")
                font.setPointSize(int(90 * device_pixel_ratio))
                font.setBold(True)
                painter.setFont(font)
                painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, "F1")
            else:
                # MotoGP logo styling
                font = painter.font()
                font.setFamily("Arial")
                font.setPointSize(int(48 * device_pixel_ratio))
                font.setBold(True)
                font.setLetterSpacing(font.LetterSpacingType.AbsoluteSpacing, 3 * device_pixel_ratio)
                painter.setFont(font)
                painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, "MotoGP")
            
            painter.end()
            
            logger.info(f"Created fallback logo for {series_type}")
            return pixmap
            
        except Exception as e:
            logger.error(f"Error creating fallback logo: {e}")
            # Return a basic colored rectangle as last resort
            fallback = QPixmap(width, height)
            fallback.fill(background_color)
            return fallback
    
    
    """
    * Configures a QLabel for optimal high-quality pixmap display
    *
    * This method sets up a QLabel widget with the optimal configuration
    * for displaying high-quality pixmaps including scaling behavior,
    * alignment, and size policies for professional presentation.
    *
    * **@param** label QLabel widget to configure for image display
    * **@param** pixmap QPixmap image to display in the label
    * **@param** maintain_aspect_ratio Boolean whether to preserve aspect ratio
    * **@return** None
    """
    @staticmethod
    def setup_high_quality_label(
        label: QLabel,
        pixmap: QPixmap,
        maintain_aspect_ratio: bool = True
    ):
        try:
            label.setPixmap(pixmap)
            label.setScaledContents(False)  # Prevent Qt from scaling
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            if maintain_aspect_ratio:
                label.setMinimumSize(1, 1)  # Allow shrinking
                label.setSizePolicy(
                    label.sizePolicy().horizontalPolicy(),
                    label.sizePolicy().verticalPolicy()
                )
            
            logger.debug("Configured label for high-quality display")
            
        except Exception as e:
            logger.error(f"Error setting up high-quality label: {e}")
    
    
    """
    * Calculates optimal logo size to fit within container while maintaining aspect ratio
    *
    * This method determines the best size for a logo to fit within a given
    * container while preserving the original aspect ratio and accounting
    * for padding around the edges.
    *
    * **@param** original_size Tuple of (width, height) for original image
    * **@param** container_size Tuple of (width, height) for container
    * **@param** padding Integer padding to leave around the logo
    * **@return** Tuple of (width, height) for optimal logo size
    """
    @staticmethod
    def get_optimal_logo_size(
        original_size: Tuple[int, int],
        container_size: Tuple[int, int],
        padding: int = 20
    ) -> Tuple[int, int]:
        try:
            orig_width, orig_height = original_size
            container_width, container_height = container_size
            
            # Account for padding
            available_width = container_width - (2 * padding)
            available_height = container_height - (2 * padding)
            
            # Calculate scale factors
            width_scale = available_width / orig_width
            height_scale = available_height / orig_height
            
            # Use the smaller scale to ensure logo fits
            scale = min(width_scale, height_scale)
            
            # Calculate new size
            new_width = int(orig_width * scale)
            new_height = int(orig_height * scale)
            
            logger.debug(f"Calculated optimal logo size: {new_width}x{new_height}")
            return (new_width, new_height)
            
        except Exception as e:
            logger.error(f"Error calculating optimal logo size: {e}")
            return (200, 100)  # Fallback size
    
    
    """
    * Ensures the logo directory exists and creates it if necessary
    *
    * This method checks for the existence of the logo directory and creates
    * it if it doesn't exist, ensuring the application can store and access
    * logo files properly.
    *
    * **@return** Path object pointing to the logo directory
    """
    @staticmethod
    def ensure_logo_directory():
        logo_dir = Path("logo")
        logo_dir.mkdir(exist_ok=True)
        return logo_dir
    
    
    """
    * Checks which logo files exist and validates their properties
    *
    * This method scans the logo directory for F1 and MotoGP logo files,
    * validates that they can be loaded properly, and returns a comprehensive
    * status report for diagnostic and troubleshooting purposes.
    *
    * **@return** Dictionary containing status information for each logo file
    """
    @staticmethod
    def check_logo_files() -> dict:
        logo_dir = ImageUtils.ensure_logo_directory()
        
        logo_files = {
            "f1": logo_dir / "f1_logo.png",
            "motogp": logo_dir / "motogp_logo.png"
        }
        
        status = {}
        for series, path in logo_files.items():
            if path.exists():
                try:
                    pixmap = QPixmap(str(path))
                    if not pixmap.isNull():
                        status[series] = {
                            "exists": True,
                            "path": str(path),
                            "size": (pixmap.width(), pixmap.height()),
                            "valid": True
                        }
                    else:
                        status[series] = {
                            "exists": True,
                            "path": str(path),
                            "size": (0, 0),
                            "valid": False
                        }
                except Exception as e:
                    status[series] = {
                        "exists": True,
                        "path": str(path),
                        "size": (0, 0),
                        "valid": False,
                        "error": str(e)
                    }
            else:
                status[series] = {
                    "exists": False,
                    "path": str(path),
                    "size": (0, 0),
                    "valid": False
                }
        
        return status