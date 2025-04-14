from datetime import datetime
from pathlib import Path

class FileHandler:
    """파일 입출력 처리 클래스"""
    
    def __init__(self, output_dir):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
    
    def save_transcription(self, transcripts, audio_file, analysis_results=None):
        """전사 결과 및 분석 결과 저장
        
        Args:
            transcripts (tuple): (text_transcript, srt_transcript) - 텍스트 전사본과 SRT 형식의 대본
            audio_file (Path): 원본 오디오 파일 경로
            analysis_results (tuple, optional): (important_content, summary) - 중요 내용과 요약
            
        Returns:
            tuple: 저장된 파일 경로들
        """
        text_transcript, srt_transcript = transcripts
        base_name = Path(audio_file).stem
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 텍스트 파일 저장
        text_file = self._save_text_file(text_transcript, base_name, timestamp)
        
        # SRT 파일 저장
        srt_file = self._save_srt_file(srt_transcript, base_name, timestamp)
        
        result_files = [text_file, srt_file]
        
        # 분석 결과가 있으면 저장
        if analysis_results:
            important_content, summary = analysis_results
            
            # 중요 내용 파일 저장
            important_file = self._save_important_file(important_content, base_name, timestamp)
            
            # 요약 파일 저장
            summary_file = self._save_summary_file(summary, base_name, timestamp)
            
            result_files.extend([important_file, summary_file])
        
        return tuple(result_files)
    
    def _save_text_file(self, content, base_name, timestamp):
        """텍스트 파일 저장"""
        file_path = self.output_dir / f"{base_name}_{timestamp}.txt"
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"텍스트 파일 저장 완료: {file_path}")
        return file_path
    
    def _save_srt_file(self, content, base_name, timestamp):
        """SRT 파일 저장"""
        file_path = self.output_dir / f"{base_name}_{timestamp}.srt"
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"SRT 형식 대본 파일 저장 완료: {file_path}")
        return file_path
    
    def _save_important_file(self, content, base_name, timestamp):
        """중요 내용 파일 저장"""
        file_path = self.output_dir / f"{base_name}_{timestamp}_important.txt"
        with open(file_path, "w", encoding="utf-8") as f:
            f.write("# 강의 중요 내용 추출\n\n")
            f.write(content)
        print(f"중요 내용 추출 파일 저장 완료: {file_path}")
        return file_path
    
    def _save_summary_file(self, content, base_name, timestamp):
        """요약 파일 저장"""
        file_path = self.output_dir / f"{base_name}_{timestamp}_summary.txt"
        with open(file_path, "w", encoding="utf-8") as f:
            f.write("# 강의 요약\n\n")
            f.write(content)
        print(f"요약 파일 저장 완료: {file_path}")
        return file_path
