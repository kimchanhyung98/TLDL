#!/usr/bin/env python3

import json
from datetime import datetime
from pathlib import Path

from openai import OpenAI

from app.config import OPENAI_API_KEY

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
        openai.types.Transcription: API에서 반환한 전사 결과

    Raises:
        Exception: API 호출 중 오류 발생 시
    """
    print(f"전사 시작: {audio_file.name}")

    with open(audio_file, "rb") as audio:
        transcript = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio,
            response_format="verbose_json"
        )

    print(f"전사 완료: {audio_file.name}")
    return transcript


def save_transcription(transcript, audio_file):
    """전사 결과를 파일로 저장합니다.

    다음 세 가지 파일을 저장합니다:
    1. 전체 전사 내용이 포함된 텍스트 파일
    2. 각 세그먼트별 타임스태프가 포함된 대본 파일
    3. API 응답 전체가 포함된 JSON 파일

    Args:
        transcript (openai.types.Transcription): API에서 반환한 전사 결과
        audio_file (Path): 원본 오디오 파일 경로

    Returns:
        tuple[Path, Path, Path]: 저장된 파일 경로들 (text_file, transcript_file, json_file)

    Raises:
        IOError: 파일 저장 중 오류 발생 시
    """
    base_name = audio_file.stem
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # 기본 텍스트 파일로 저장 (전체 내용)
    text_file = OUTPUT_DIR / f"{base_name}_{timestamp}.txt"
    with open(text_file, "w", encoding="utf-8") as f:
        f.write(transcript.text)

    # 타임스탬프가 포함된 대본 형식으로 저장
    transcript_file = OUTPUT_DIR / f"{base_name}_{timestamp}_transcript.txt"
    with open(transcript_file, "w", encoding="utf-8") as f:
        # 세그먼트가 있는 경우
        if hasattr(transcript, 'segments') and transcript.segments:
            for i, segment in enumerate(transcript.segments):
                start_time = format_timestamp(segment.start)
                end_time = format_timestamp(segment.end)

                # 세그먼트 번호, 시작/종료 시간, 텍스트 형식으로 출력
                f.write(f"[{i + 1}] [{start_time} --> {end_time}]\n{segment.text}\n\n")
        else:
            # 세그먼트가 없는 경우 전체 텍스트만 출력
            f.write(transcript.text)

    # JSON 파일로 저장
    json_file = OUTPUT_DIR / f"{base_name}_{timestamp}.json"
    with open(json_file, "w", encoding="utf-8") as f:
        json.dump(transcript.model_dump(), f, ensure_ascii=False, indent=2)

    print(f"텍스트 파일 저장 완료: {text_file}")
    print(f"타임스탬프 포함 대본 저장 완료: {transcript_file}")
    return text_file, transcript_file, json_file


def format_timestamp(seconds):
    """초 단위 시간을 HH:MM:SS 형식으로 변환합니다.

    Args:
        seconds (float): 초 단위 시간

    Returns:
        str: HH:MM:SS 형식의 시간 문자열 (00:00:00)
    """
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds = int(seconds % 60)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"


def process_all_files():
    """data 디렉토리의 모든 오디오 파일을 처리합니다.

    Returns:
        list[tuple[Path, tuple[Path, Path, Path]]]: 처리된 파일 목록. 각 항목은 (오디오 파일, 출력 파일들) 형태

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
            transcript = transcribe_audio(audio_file)
            output_files = save_transcription(transcript, audio_file)
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
