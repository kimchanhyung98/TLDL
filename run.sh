#!/bin/bash
#############################################################
# TLDL 애플리케이션 실행 스크립트
#############################################################
#
# 설명:
#   이 스크립트는 Docker 컨테이너를 사용하여 data 디렉토리의 파일을 처리하고
#   결과를 outputs 디렉토리에 저장합니다.
#
# 실행 단계:
#   1. 디렉토리 확인 (처리할 파일이 있는지 먼저 확인)
#   2. 기존 컨테이너 종료 (존재하는 경우)
#   3. Docker 이미지 빌드
#   4. 애플리케이션 실행 (data 디렉토리의 파일 처리)
#   5. 결과물 outputs 디렉토리에 저장
#   6. 컨테이너 종료 및 이미지 제거
#
# 사용법:
#   ./run.sh

# 스크립트가 있는 디렉토리로 이동
cd "$(dirname "$0")" || exit

# 색상 정의
GREEN='\033[0;32m' # 성공이나 일반적인 메시지
YELLOW='\033[1;33m' # 경고나 특이사항
RED='\033[0;31m' # 오류
NC='\033[0m' # No Color

# 디렉토리 확인
function check_directories {
    # data 디렉토리에 .gitignore를 제외한 파일이 있는지 확인
    file_count=$(find data -type f -not -name ".gitignore" | wc -l)

    if [ "$file_count" -eq 0 ]; then
        echo -e "${RED}경고: data 디렉토리에 처리할 파일이 없습니다.${NC}"
        echo -e "${YELLOW}처리할 파일을 data 디렉토리에 추가한 후 다시 실행하세요.${NC}"
        exit 1
    fi

    echo -e "${GREEN}data 디렉토리에서 $(($file_count))개의 처리할 파일을 발견했습니다.${NC}"
}

# 기존 컨테이너 종료
function cleanup_containers {
    echo -e "${GREEN}기존 컨테이너 확인 및 정리 중...${NC}"

    # tldl-app 이름의 컨테이너가 실행 중인지 확인
    if [ "$(docker ps -q -f name=tldl-app)" ]; then
        echo -e "${YELLOW}실행 중인 tldl-app 컨테이너를 종료합니다...${NC}"
        docker stop $(docker ps -q -f name=tldl-app)
    fi

    # 중지된 tldl-app 컨테이너 제거
    if [ "$(docker ps -a -q -f name=tldl-app)" ]; then
        echo -e "${YELLOW}중지된 tldl-app 컨테이너를 제거합니다...${NC}"
        docker rm $(docker ps -a -q -f name=tldl-app)
    fi
}

# Docker 이미지 빌드
function build_image {
    echo -e "${GREEN}Docker 이미지 빌드 중...${NC}"
    docker build -t tldl-app .

    if [ $? -eq 0 ]; then
        echo -e "${GREEN}Docker 이미지 빌드 완료${NC}"
    else
        echo -e "${RED}Docker 이미지 빌드 실패${NC}"
        exit 1
    fi
}

# 애플리케이션 실행
function run_app {
    echo -e "${GREEN}TLDL 애플리케이션 실행 중...${NC}"
    echo -e "${GREEN}data 디렉토리의 파일을 처리하여 outputs 디렉토리에 결과를 저장합니다...${NC}"

    docker run --name tldl-app -v "$(pwd)/data:/app/data" -v "$(pwd)/outputs:/app/outputs" tldl-app

    if [ $? -eq 0 ]; then
        echo -e "${GREEN}처리 완료${NC}"
        echo -e "${GREEN}outputs 디렉토리에서 결과를 확인하세요.${NC}"
    else
        echo -e "${RED}처리 실패${NC}"
        cleanup_after_run
        exit 1
    fi
}

# 실행 후 정리
function cleanup_after_run {
    echo -e "${GREEN}컨테이너 및 이미지 정리 중...${NC}"

    # 컨테이너 제거
    if [ "$(docker ps -a -q -f name=tldl-app)" ]; then
        docker rm $(docker ps -a -q -f name=tldl-app)
    fi

    # 이미지 제거
    if [ "$(docker images -q tldl-app 2> /dev/null)" ]; then
        docker rmi tldl-app
    fi

    echo -e "${GREEN}정리 완료${NC}"
}

# 메인 실행 흐름
echo -e "${GREEN}===== TLDL 애플리케이션 실행 시작 =====${NC}"

# 1. 디렉토리 확인 (처리할 파일이 있는지 먼저 확인)
check_directories

# 2. 기존 컨테이너 정리
cleanup_containers

# 3. Docker 이미지 빌드
build_image

# 4. 애플리케이션 실행
run_app

# 5. 실행 후 정리
cleanup_after_run

echo -e "${GREEN}===== TLDL 애플리케이션 실행 완료 =====${NC}"

exit 0
