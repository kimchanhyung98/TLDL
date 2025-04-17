from pathlib import Path

from openai import OpenAI

from app.config import OPENAI_API_KEY, WHISPER_MODEL


class AudioTranscriber:
    """Class for transcribing audio files to text"""

    def __init__(self, model=WHISPER_MODEL, api_key=OPENAI_API_KEY):
        self.model = model
        self.client = OpenAI(api_key=api_key)

    def transcribe(self, audio_file):
        """Transcribe audio file to text and SRT format"""
        print(f"Processing audio file: {Path(audio_file).name}")

        # Get text transcript
        text_transcript = self._get_text_transcript(audio_file)

        # Get SRT format
        srt_transcript = self._get_srt_transcript(audio_file)

        print(f"Audio file processing completed: {Path(audio_file).name}")
        return text_transcript, srt_transcript

    def _get_text_transcript(self, audio_file):
        """Get transcript in text format"""
        with open(audio_file, "rb") as audio:
            return self.client.audio.transcriptions.create(
                model=self.model,
                file=audio,
                response_format="text"
            )

    def _get_srt_transcript(self, audio_file):
        """Get transcript in SRT format"""
        with open(audio_file, "rb") as audio:
            return self.client.audio.transcriptions.create(
                model=self.model,
                file=audio,
                response_format="srt"
            )
