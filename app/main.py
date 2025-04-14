#!/usr/bin/env python3

from datetime import datetime
from pathlib import Path

from openai import OpenAI

from app.config import OPENAI_API_KEY, WHISPER_MODEL

client = OpenAI(api_key=OPENAI_API_KEY)
DATA_DIR = Path("/app/data")
OUTPUT_DIR = Path("/app/outputs")
SUPPORTED_AUDIO_EXTENSIONS = [".mp3", ".mp4", ".mpeg", ".mpga", ".m4a", ".wav", ".webm"]


def get_audio_files():
    """data 디렉토리에서 오디오 파일을 찾습니다.

    Returns:
        list[Path]: 찾은 오디오 파일의 경로 목록
    """
    audio_files = []
    for ext in SUPPORTED_AUDIO_EXTENSIONS:
        audio_files.extend(list(DATA_DIR.glob(f"*{ext}")))
    return audio_files


def transcribe_audio(audio_file):
    """OpenAI Whisper API를 사용하여 오디오 파일을 전사합니다.

    Args:
        audio_file (Path): 전사할 오디오 파일 경로

    Returns:
        tuple: (text_transcript, srt_transcript) - 텍스트 전사본과 SRT 형식의 대본

    Raises:
        Exception: API 호출 중 오류 발생 시
    """
    print(f"오디오 파일 처리 시작: {audio_file.name}")

    # 텍스트 전사본 가져오기
    with open(audio_file, "rb") as audio:
        text_transcript = client.audio.transcriptions.create(
            model=WHISPER_MODEL,
            file=audio,
            response_format="text"
        )

    # 시간이 표기된 SRT 형식 가져오기
    with open(audio_file, "rb") as audio:
        srt_transcript = client.audio.transcriptions.create(
            model=WHISPER_MODEL,
            file=audio,
            response_format="srt"
        )

    print(f"오디오 파일 처리 완료: {audio_file.name}")
    return text_transcript, srt_transcript


def save_transcription(transcripts, audio_file):
    """전사 결과를 파일로 저장합니다.

    다음 파일들을 저장합니다:
    1. 전체 전사 내용이 포함된 텍스트 파일
    2. 시간이 표기된 SRT 형식의 대본 파일

    Args:
        transcripts (tuple): (text_transcript, srt_transcript) - 텍스트 전사본과 SRT 형식의 대본
        audio_file (Path): 원본 오디오 파일 경로

    Returns:
        tuple[Path, Path]: 저장된 파일 경로들 (text_file, srt_file)

    Raises:
        IOError: 파일 저장 중 오류 발생 시
    """
    text_transcript, srt_transcript = transcripts
    base_name = audio_file.stem
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # 기본 텍스트 파일로 저장 (전체 내용)
    text_file = OUTPUT_DIR / f"{base_name}_{timestamp}.txt"
    with open(text_file, "w", encoding="utf-8") as f:
        f.write(text_transcript)
    print(f"텍스트 파일 저장 완료: {text_file}")

    # SRT 형식의 대본 파일 저장
    srt_file = OUTPUT_DIR / f"{base_name}_{timestamp}.srt"
    with open(srt_file, "w", encoding="utf-8") as f:
        f.write(srt_transcript)
    print(f"SRT 형식 대본 파일 저장 완료: {srt_file}")

    return text_file, srt_file


def process_all_files():
    """data 디렉토리의 모든 오디오 파일을 처리합니다.

    Returns:
        list[tuple[Path, tuple[Path, Path]]]: 처리된 파일 목록. 각 항목은 (오디오 파일, 출력 파일들) 형태
        출력 파일들은 (text_file, srt_file) 형태

    Raises:
        Exception: 파일 처리 중 오류 발생 시
    """
    audio_files = get_audio_files()

    if not audio_files:
        print("처리할 오디오 파일이 없습니다.")
        return

    print(f"총 {len(audio_files)}개의 오디오 파일을 처리합니다.")

    results = []
    for audio_file in audio_files:
        try:
            transcripts = transcribe_audio(audio_file)
            output_files = save_transcription(transcripts, audio_file)
            results.append((audio_file, output_files))
            print(f"{audio_file.name} 처리 완료")
        except Exception as e:
            print(f"오류 발생: {audio_file.name} - {e}")

    print(f"모든 파일 처리 완료. 총 {len(results)}개 파일 처리됨.")
    return results


def main():
    """애플리케이션의 메인 진입점입니다.

    data 디렉토리의 모든 오디오 파일을 처리합니다.

    Raises:
        Exception: 파일 처리 중 오류 발생 시
    """
    print("TLDL (Too Long; Didn't Listen) 시작...")

    process_all_files()

    print("TLDL 처리 완료")


if __name__ == "__main__":
    main()
