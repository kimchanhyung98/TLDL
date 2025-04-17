"""
This module is deprecated and will be removed in a future version.
Please use app.services.image.image_analyzer instead.
"""

from app.services.image.image_analyzer import ImageAnalyzer

# Re-export for backward compatibility
__all__ = ['ImageAnalyzer']
