FROM python:3-slim AS base

# 환경 변수 설정
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PYTHONPATH=/app

# 작업 디렉토리 설정
WORKDIR /app

# 시스템 패키지 설치 (빌드 시간 단축을 위해 필요한 패키지만 설치)
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    git \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 프로젝트 파일 복사 (환경 변수 및 설정 파일 포함)
COPY . .

# PyTorch CPU 버전 및 기본 의존성 설치
RUN pip install --no-cache-dir \
    torch==2.0.1 \
    torchvision==0.15.2 \
    torchaudio==2.0.2 \
    --extra-index-url https://download.pytorch.org/whl/cpu \
    && pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir git+https://github.com/openai/whisper.git

# 데이터와 결과물 디렉토리는 .dockerignore에 의해 이미지에 포함되지 않음
# 볼륨 마운트를 위한 디렉토리 생성
RUN mkdir -p /app/data /app/outputs \
    && chmod 777 /app/data /app/outputs

# 볼륨 마운트 포인트 명시
VOLUME ["/app/data", "/app/outputs"]

# 비루트 사용자 생성 및 권한 설정 (보안 강화)
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

# 컨테이너 실행 시 실행할 명령어
CMD ["python", "app/main.py"]

# 이 컨테이너는 data 디렉토리의 파일을 처리하여 outputs 디렉토리에 결과를 저장합니다.
# run.sh 스크립트를 사용하여 실행하세요.
