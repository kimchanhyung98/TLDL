#!/bin/bash
#############################################################
# TLDL Application Runner
#############################################################

# Move to script directory
cd "$(dirname "$0")" || exit

# Color definitions
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

# Check for files to process
file_count=$(find data -type f -not -name ".gitignore" | wc -l)
if [ "$file_count" -eq 0 ]; then
    echo -e "${RED}Error: No files in data directory${NC}"
    exit 1
fi
echo -e "${GREEN}Found $file_count files to process${NC}"

# Clean up existing containers
if [ "$(docker ps -a -q -f name=tldl-app)" ]; then
    docker stop $(docker ps -q -f name=tldl-app) 2>/dev/null
    docker rm $(docker ps -a -q -f name=tldl-app) 2>/dev/null
fi

# Build and run
echo -e "${GREEN}Building and running TLDL...${NC}"
docker build -t tldl-app .
docker run --name tldl-app \
    -v "$(pwd)/data:/app/data" \
    -v "$(pwd)/outputs:/app/outputs" \
    tldl-app

# Check result
if [ $? -eq 0 ]; then
    echo -e "${GREEN}Success! Check outputs directory for results${NC}"
else
    echo -e "${RED}Processing failed${NC}"
fi

# Cleanup
docker rm tldl-app 2>/dev/null
docker rmi tldl-app 2>/dev/null

exit 0
