"""
This module is deprecated and will be removed in a future version.
Please use app.services.document.pdf_processor instead.
"""

from app.services.document.pdf_processor import PDFProcessor

# Re-export for backward compatibility
__all__ = ['PDFProcessor']
