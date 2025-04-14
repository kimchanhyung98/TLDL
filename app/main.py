#!/usr/bin/env python3

from datetime import datetime
from pathlib import Path

from openai import OpenAI

from app.config import OPENAI_API_KEY, WHISPER_MODEL, SUMMARY_MODEL

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
    3. 중요 내용 추출 파일
    4. 요약 파일

    Args:
        transcripts (tuple): (text_transcript, srt_transcript) - 텍스트 전사본과 SRT 형식의 대본
        audio_file (Path): 원본 오디오 파일 경로

    Returns:
        tuple[Path, Path, Path, Path]: 저장된 파일 경로들 (text_file, srt_file, important_file, summary_file)

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

    # 중요 내용 추출 및 저장
    important_content = extract_important_content(text_transcript)
    important_file = OUTPUT_DIR / f"{base_name}_{timestamp}_important.txt"
    with open(important_file, "w", encoding="utf-8") as f:
        f.write("# 강의 중요 내용 추출\n\n")
        f.write(important_content)
    print(f"중요 내용 추출 파일 저장 완료: {important_file}")

    # 요약 생성 및 저장
    summary = summarize_transcript(text_transcript)
    summary_file = OUTPUT_DIR / f"{base_name}_{timestamp}_summary.txt"
    with open(summary_file, "w", encoding="utf-8") as f:
        f.write("# 강의 요약\n\n")
        f.write(summary)
    print(f"요약 파일 저장 완료: {summary_file}")

    return text_file, srt_file, important_file, summary_file


def extract_important_content(transcript_text):
    """대본에서 중요 내용을 추출합니다.

    시험, 과제, 중요 공지사항 등 학업에 중요한 정보를 추출합니다.

    Args:
        transcript_text (str): 전사된 대본 텍스트

    Returns:
        str: 추출된 중요 내용
    """
    print("중요 내용 추출 시작...")

    # 중요 내용 추출을 위한 프롬프트
    prompt = """
    다음은 강의 대본입니다. 이 대본에서 다음과 같은 중요한 내용을 추출해주세요:

    1. 시험 관련 정보 (시험 날짜, 범위, 형식, 주의사항 등)
    2. 과제 관련 정보 (제출 기한, 형식, 주제, 요구사항 등)
    3. 중요한 공지사항이나 특이사항
    4. 교수가 특별히 강조한 개념이나 내용
    5. 수업 참여나 출석에 관한 중요 정보

    각 항목별로 정리하고, 해당 내용이 없으면 '해당 정보 없음'이라고 표시해주세요.
    정보를 추출할 때 가능한 원문의 표현을 유지하고, 시간 정보나 구체적인 지시사항이 있다면 반드시 포함해주세요.

    강의 대본:
    {transcript_text}
    """

    # OpenAI API를 사용하여 중요 내용 추출
    response = client.chat.completions.create(
        model=SUMMARY_MODEL,
        messages=[
            {"role": "system", "content": "당신은 학생들을 위한 강의 내용 분석 도우미입니다. 강의 대본에서 학업에 중요한 정보를 정확하게 추출하는 역할을 합니다."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3,  # 낮은 temperature로 일관된 결과 유도
    )

    important_content = response.choices[0].message.content.strip()
    print("중요 내용 추출 완료")
    return important_content


def summarize_transcript(transcript_text):
    """대본 내용을 요약합니다.

    Args:
        transcript_text (str): 전사된 대본 텍스트

    Returns:
        str: 요약된 내용
    """
    print("대본 요약 시작...")

    # 요약을 위한 프롬프트
    prompt = """
    다음은 강의 대본입니다. 이 대본의 주요 내용을 간결하게 요약해주세요.
    요약은 다음 형식을 따라주세요:

    1. 강의 주제 및 목표
    2. 주요 논의 내용 (핵심 개념, 이론, 사례 등)
    3. 결론 및 핵심 메시지

    요약은 원래 내용의 10~15% 정도 분량으로 작성하고, 중요한 용어나 개념은 그대로 유지해주세요.

    강의 대본:
    {transcript_text}
    """

    # OpenAI API를 사용하여 요약 생성
    response = client.chat.completions.create(
        model=SUMMARY_MODEL,
        messages=[
            {"role": "system", "content": "당신은 학술 내용을 명확하고 간결하게 요약하는 전문가입니다. 강의 내용의 핵심을 유지하면서 불필요한 세부사항은 제외하여 요약합니다."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3,  # 낮은 temperature로 일관된 결과 유도
    )

    summary = response.choices[0].message.content.strip()
    print("대본 요약 완료")
    return summary


def process_all_files():
    """data 디렉토리의 모든 오디오 파일을 처리합니다.

    Returns:
        list[tuple[Path, tuple[Path, Path, Path, Path]]]: 처리된 파일 목록. 각 항목은 (오디오 파일, 출력 파일들) 형태
        출력 파일들은 (text_file, srt_file, important_file, summary_file) 형태

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
