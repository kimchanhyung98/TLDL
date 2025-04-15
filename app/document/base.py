class DocumentProcessor:
    """Base interface for document processing"""

    def process(self, file_path):
        """Document processing method"""
        raise NotImplementedError

    def extract_text(self, file_path):
        """Extract text from document"""
        raise NotImplementedError
