from pathlib import Path

# 지원하는 오디오 파일 확장자
SUPPORTED_AUDIO_EXTENSIONS = [".mp3", ".mp4", ".mpeg", ".mpga", ".m4a", ".wav", ".webm"]

def get_audio_files(directory):
    """디렉토리에서 오디오 파일 찾기
    
    Args:
        directory (Path): 오디오 파일을 찾을 디렉토리
        
    Returns:
        list[Path]: 찾은 오디오 파일 경로 목록
    """
    audio_files = []
    for ext in SUPPORTED_AUDIO_EXTENSIONS:
        audio_files.extend(list(directory.glob(f"*{ext}")))
    return audio_files
