"""
Base interface for document processing.
This is an abstract class that defines the interface for document processors.
"""


class DocumentInterface:
    """Base interface for document processing"""

    def process(self, file_path):
        """Document processing method"""
        raise NotImplementedError

    def extract_text(self, file_path):
        """Extract text from document"""
        raise NotImplementedError
