from pathlib import Path
from typing import List, Dict, Any

from app.services.audio.file_utils import get_audio_files
from app.services.audio.transcriber import AudioTranscriber
from app.services.text.analyzer import TextAnalyzer
from app.utils.file_handler import FileHandler


class AudioProcessor:
    """Main class for processing audio files"""

    def __init__(self, output_dir: str = "outputs"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

        self.transcriber = AudioTranscriber()
        self.text_analyzer = TextAnalyzer()
        self.file_handler = FileHandler(output_dir)

    def process_audio(self, audio_file: str) -> Dict[str, Any]:
        """Process a single audio file
        
        Args:
            audio_file: Path to the audio file
            
        Returns:
            Dict containing processing results
        """
        audio_file = Path(audio_file)

        if not audio_file.exists():
            raise FileNotFoundError(f"Audio file not found: {audio_file}")

        # 1. Transcribe audio
        transcripts = self.transcriber.transcribe(audio_file)

        # 2. Analyze text
        text_transcript = transcripts[0]
        important_content = self.text_analyzer.extract_important_content(text_transcript)
        summary = self.text_analyzer.summarize_text(text_transcript)

        # 3. Save files
        output_files = self.file_handler.save_transcription(
            transcripts,
            audio_file,
            analysis_results=(important_content, summary)
        )

        return {
            "audio_file": audio_file,
            "output_files": output_files
        }

    def process_all_files(self, directory: str = "data") -> List[Dict[str, Any]]:
        """Process all audio files in a directory
        
        Args:
            directory: Directory containing audio files
            
        Returns:
            List of processing results
        """
        directory = Path(directory)

        if not directory.exists():
            raise FileNotFoundError(f"Directory not found: {directory}")

        # Get audio files
        audio_files = get_audio_files(directory)

        if not audio_files:
            print("No audio files to process.")
            return []

        print(f"Processing {len(audio_files)} audio files.")

        results = []
        for audio_file in audio_files:
            try:
                result = self.process_audio(audio_file)
                results.append(result)
                print(f"Processing completed: {audio_file.name}")
            except Exception as e:
                print(f"Error occurred: {audio_file.name} - {e}")

        print(f"All audio files processed. Total: {len(results)} files.")
        return results
