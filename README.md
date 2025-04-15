# Too Long; Didn't Listen

강의 녹음과 자료를 정리 및 요약

## 개요

OpenAI API를 활용하여 오디오 파일(강의 녹음 등)을 텍스트로 변환하고 강의 자료를 요약하여 중요 내용을 정리하는 도구입니다.

## 실행

1. `.env` 파일 설정

```dotenv
# OpenAI API key
OPENAI_API_KEY=

# OpenAI Model
SUMMARY_MODEL=o1
WHISPER_MODEL=whisper-1
```

2. `data` 디렉토리에 오디오 파일과 강의 자료 추가

3. 실행

```bash
# Docker로 실행
./run.sh

# 또는 Python으로 실행
python -m app.main 
```

4. `outputs` 디렉토리에서 결과 확인

---


<sub>~~과제가너무많아요~~</sub>
