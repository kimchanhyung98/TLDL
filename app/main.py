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
    """data 디렉토리의 모든 오디오 파일을 처리합니다.

    Returns:
        list[tuple[Path, tuple]]: 처리된 파일 목록. 각 항목은 (오디오 파일, 출력 파일들) 형태
        출력 파일들은 (text_file, srt_file, important_file, summary_file) 형태

    Raises:
        Exception: 파일 처리 중 오류 발생 시
    """
    # 필요한 객체 초기화
    transcriber = AudioTranscriber()
    analyzer = TextAnalyzer()
    file_handler = FileHandler(OUTPUT_DIR)

    # 오디오 파일 찾기
    audio_files = get_audio_files(DATA_DIR)

    if not audio_files:
        print("처리할 오디오 파일이 없습니다.")
        return

    print(f"총 {len(audio_files)}개의 오디오 파일을 처리합니다.")

    results = []
    for audio_file in audio_files:
        try:
            # 1. 오디오 전사
            transcripts = transcriber.transcribe(audio_file)

            # 2. 텍스트 분석
            text_transcript = transcripts[0]
            important_content = analyzer.extract_important_content(text_transcript)
            summary = analyzer.summarize_text(text_transcript)

            # 3. 파일 저장
            output_files = file_handler.save_transcription(
                transcripts,
                audio_file,
                analysis_results=(important_content, summary)
            )

            results.append((audio_file, output_files))
            print(f"{audio_file.name} 처리 완료")

        except Exception as e:
            print(f"오류 발생: {audio_file.name} - {e}")

    print(f"모든 파일 처리 완료. 총 {len(results)}개 파일 처리됨.")
    return results


def main():
    """애플리케이션 메인 진입점"""
    print("TLDL (Too Long; Didn't Listen) 시작...")
    process_all_files()
    print("TLDL 처리 완료")


if __name__ == "__main__":
    main()
