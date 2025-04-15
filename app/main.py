#!/usr/bin/env python3

from pathlib import Path

from app.audio.file_utils import get_audio_files
from app.audio.transcriber import AudioTranscriber
from app.text.analyzer import TextAnalyzer
from app.utils.file_handler import FileHandler

# 상수 정의
DATA_DIR = Path("data")
OUTPUT_DIR = Path("outputs")


def process_all_files():
    """Process all audio files in the data directory.

    Returns:
        list[tuple[Path, tuple]]: List of processed files. Each item is (audio_file, output_files)
        output_files is in the format (text_file, srt_file, important_file, summary_file)

    Raises:
        Exception: If an error occurs during file processing
    """
    # Initialize required objects
    transcriber = AudioTranscriber()
    analyzer = TextAnalyzer()
    file_handler = FileHandler(OUTPUT_DIR)

    # Find audio files
    audio_files = get_audio_files(DATA_DIR)

    if not audio_files:
        print("No audio files to process.")
        return

    print(f"Processing {len(audio_files)} audio files.")

    results = []
    for audio_file in audio_files:
        try:
            # 1. Transcribe audio
            transcripts = transcriber.transcribe(audio_file)

            # 2. Analyze text
            text_transcript = transcripts[0]
            important_content = analyzer.extract_important_content(text_transcript)
            summary = analyzer.summarize_text(text_transcript)

            # 3. Save files
            output_files = file_handler.save_transcription(
                transcripts,
                audio_file,
                analysis_results=(important_content, summary)
            )

            results.append((audio_file, output_files))
            print(f"Processing completed: {audio_file.name}")

        except Exception as e:
            print(f"Error occurred: {audio_file.name} - {e}")

    print(f"All files processed. Total: {len(results)} files.")
    return results


def main():
    """Application main entry point"""
    print("TLDL (Too Long; Didn't Listen) starting...")
    process_all_files()
    print("TLDL processing completed")


if __name__ == "__main__":
    main()
