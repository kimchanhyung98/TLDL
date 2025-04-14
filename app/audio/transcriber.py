from pathlib import Path
from openai import OpenAI

from app.config import OPENAI_API_KEY, WHISPER_MODEL

class AudioTranscriber:
    """오디오 파일을 텍스트로 변환하는 클래스"""
    
    def __init__(self, model=WHISPER_MODEL, api_key=OPENAI_API_KEY):
        self.model = model
        self.client = OpenAI(api_key=api_key)
    
    def transcribe(self, audio_file):
        """오디오 파일을 텍스트와 SRT로 변환"""
        print(f"오디오 파일 처리 시작: {Path(audio_file).name}")
        
        # 텍스트 전사본 가져오기
        text_transcript = self._get_text_transcript(audio_file)
        
        # SRT 형식 가져오기
        srt_transcript = self._get_srt_transcript(audio_file)
        
        print(f"오디오 파일 처리 완료: {Path(audio_file).name}")
        return text_transcript, srt_transcript
    
    def _get_text_transcript(self, audio_file):
        """텍스트 형식 전사본 가져오기"""
        with open(audio_file, "rb") as audio:
            return self.client.audio.transcriptions.create(
                model=self.model,
                file=audio,
                response_format="text"
            )
    
    def _get_srt_transcript(self, audio_file):
        """SRT 형식 전사본 가져오기"""
        with open(audio_file, "rb") as audio:
            return self.client.audio.transcriptions.create(
                model=self.model,
                file=audio,
                response_format="srt"
            )
