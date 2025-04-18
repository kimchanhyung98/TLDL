from pathlib import Path
from typing import List, Dict, Any

from app.processors.audio_processor import AudioProcessor
from app.processors.document_processor import DocumentProcessor


class ContentProcessor:
    """Main class for processing and integrating all content types"""

    def __init__(self, output_dir: str = "outputs"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

        self.audio_processor = AudioProcessor(output_dir)
        self.document_processor = DocumentProcessor(output_dir)

    def process_all(self, directory: str = "data", mode: str = "all") -> Dict[str, List[Dict[str, Any]]]:
        """Process all content in a directory
        
        Args:
            directory: Directory containing files to process
            mode: Processing mode ('audio', 'documents', or 'all')
            
        Returns:
            Dict containing processing results by type
        """
        results = {
            "audio": [],
            "documents": []
        }

        if mode in ["audio", "all"]:
            print("\n=== Processing Audio Files ===")
            results["audio"] = self.audio_processor.process_all_files(directory)

        if mode in ["documents", "all"]:
            print("\n=== Processing Document Files ===")
            results["documents"] = self.document_processor.process_all_files(directory)

        return results

    def integrate_content(self, lecture_id: str) -> Dict[str, Any]:
        """Integrate audio and document content for a lecture
        
        This is a placeholder for future functionality that will integrate
        audio transcripts with document content for a comprehensive analysis.
        
        Args:
            lecture_id: Identifier for the lecture
            
        Returns:
            Dict containing integrated results
        """
        # This is a placeholder for future functionality
        return {
            "lecture_id": lecture_id,
            "status": "Not implemented yet",
            "message": "Content integration will be implemented in a future update"
        }
