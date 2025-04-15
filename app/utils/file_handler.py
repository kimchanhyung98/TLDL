from datetime import datetime
from pathlib import Path


class FileHandler:
    """File input/output handling class"""

    def __init__(self, output_dir):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

    def save_transcription(self, transcripts, audio_file, analysis_results=None):
        """Save transcription results and analysis results

        Args:
            transcripts (tuple): (text_transcript, srt_transcript) - Text transcript and SRT format transcript
            audio_file (Path): Original audio file path
            analysis_results (tuple, optional): (important_content, summary) - Important content and summary

        Returns:
            tuple: Saved file paths
        """
        text_transcript, srt_transcript = transcripts
        base_name = Path(audio_file).stem
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Save text file
        text_file = self._save_text_file(text_transcript, base_name, timestamp)

        # Save SRT file
        srt_file = self._save_srt_file(srt_transcript, base_name, timestamp)

        result_files = [text_file, srt_file]

        # Save analysis results if available
        if analysis_results:
            important_content, summary = analysis_results

            # Save important content file
            important_file = self._save_important_file(important_content, base_name, timestamp)

            # Save summary file
            summary_file = self._save_summary_file(summary, base_name, timestamp)

            result_files.extend([important_file, summary_file])

        return tuple(result_files)

    def _save_text_file(self, content, base_name, timestamp):
        """Save text file"""
        file_path = self.output_dir / f"{base_name}_{timestamp}.txt"
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Text file saved: {file_path}")
        return file_path

    def _save_srt_file(self, content, base_name, timestamp):
        """Save SRT file"""
        file_path = self.output_dir / f"{base_name}_{timestamp}.srt"
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"SRT format transcript file saved: {file_path}")
        return file_path

    def _save_important_file(self, content, base_name, timestamp):
        """Save important content file"""
        file_path = self.output_dir / f"{base_name}_{timestamp}_important.txt"
        with open(file_path, "w", encoding="utf-8") as f:
            f.write("# Important Lecture Content\n\n")
            f.write(content)
        print(f"Important content file saved: {file_path}")
        return file_path

    def _save_summary_file(self, content, base_name, timestamp):
        """Save summary file"""
        file_path = self.output_dir / f"{base_name}_{timestamp}_summary.txt"
        with open(file_path, "w", encoding="utf-8") as f:
            f.write("# Lecture Summary\n\n")
            f.write(content)
        print(f"Summary file saved: {file_path}")
        return file_path
