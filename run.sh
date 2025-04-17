#!/bin/bash
# TLDL Application Runner

# Move to script directory
cd "$(dirname "$0")" || exit

# Color definitions
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

# Define supported file extensions
AUDIO_EXTENSIONS=(".mp3" ".mp4" ".mpeg" ".mpga" ".m4a" ".wav" ".webm")
DOCUMENT_EXTENSIONS=(".pdf")
IMAGE_EXTENSIONS=(".jpg" ".jpeg" ".png" ".gif" ".bmp")

# Check for files with specific extensions
check_files_exist() {
    find "$1" -type f -name "*.$2" 2>/dev/null | grep -q .
    return $?
}

# Ask user for confirmation
ask_confirmation() {
    echo -e "${GREEN}$1${NC}"
    read -p "Continue? (y/n): " response
    [[ "$response" =~ ^[Yy]$ ]]
}

# Check data directory
if [ ! -d "data" ]; then
    echo -e "${RED}Error: 'data' directory not found${NC}"
    exit 1
fi

# Check for any files
file_count=$(find data -type f -not -name ".gitignore" | wc -l)
if [ "$file_count" -eq 0 ]; then
    echo -e "${RED}Error: No files in data directory${NC}"
    exit 1
fi
echo -e "${GREEN}Found $file_count files to process${NC}"

# Check for audio files
has_audio=false
for ext in "${AUDIO_EXTENSIONS[@]}"; do
    if find "data" -type f -name "*${ext}" 2>/dev/null | grep -q .; then
        has_audio=true
        echo -e "${GREEN}Found audio files${NC}"
        break
    fi
done

# Check for document files
has_documents=false
for ext in "${DOCUMENT_EXTENSIONS[@]}" "${IMAGE_EXTENSIONS[@]}"; do
    if find "data" -type f -name "*${ext}" 2>/dev/null | grep -q .; then
        has_documents=true
        echo -e "${GREEN}Found document files${NC}"
        break
    fi
done

# Handle missing file types
mode="all"
if [ "$has_audio" = false ] && [ "$has_documents" = false ]; then
    echo -e "${RED}Error: No supported files found${NC}"
    exit 1
elif [ "$has_audio" = false ]; then
    if ! ask_confirmation "No audio files found. Continue with document processing only?"; then
        echo -e "Processing cancelled"
        exit 0
    fi
    mode="documents"
elif [ "$has_documents" = false ]; then
    if ! ask_confirmation "No document files found. Continue with audio processing only?"; then
        echo -e "Processing cancelled"
        exit 0
    fi
    mode="audio"
fi

# Clean up existing containers
docker stop $(docker ps -q -f name=tldl-app) 2>/dev/null
docker rm $(docker ps -a -q -f name=tldl-app) 2>/dev/null

# Build and run
echo -e "${GREEN}Building and running TLDL...${NC}"
docker build -t tldl-app .

# Run with appropriate mode - FIXED: pass mode as CMD argument
docker run --name tldl-app \
    -v "$(pwd)/data:/app/data" \
    -v "$(pwd)/outputs:/app/outputs" \
    tldl-app python -m app.main --mode "$mode"

# Check result and cleanup
if [ $? -eq 0 ]; then
    echo -e "${GREEN}Success! Check outputs directory for results${NC}"
else
    echo -e "${RED}Processing failed${NC}"
fi

docker rm tldl-app 2>/dev/null
docker rmi tldl-app 2>/dev/null

exit 0
