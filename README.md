# Too Long; Didn't Listen

Summarize and organize lecture recordings and materials

## Overview

A tool that uses OpenAI API to convert audio files (such as lecture recordings) to text and summarize lecture materials
to extract important content.

## Usage

1. Set up `.env` file

```dotenv
# OpenAI API key
OPENAI_API_KEY=

# OpenAI Model
SUMMARY_MODEL=o1
VISION_MODEL=gpt-4o
WHISPER_MODEL=whisper-1
```

2. Add audio files and lecture materials to the `data` directory

3. Run the application

```bash
# Run with Docker
./run.sh

# Or run with Python
python -m app.main
```

4. Check results in the `outputs` directory

---

<sub><del>과제하기싫다</del></sub>
