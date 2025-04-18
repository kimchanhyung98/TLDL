#!/usr/bin/env python3

import argparse
from pathlib import Path

from app.processors.content_processor import ContentProcessor

# Constants
DATA_DIR = Path("data")
OUTPUT_DIR = Path("outputs")


def main():
    """Application main entry point"""
    parser = argparse.ArgumentParser(description="TLDL - Process audio and document files")
    parser.add_argument("--mode", choices=["audio", "documents", "all"], default="all",
                        help="Processing mode: audio, documents, or all (default)")
    args = parser.parse_args()

    print("TLDL (Too Long; Didn't Listen) starting...")

    processor = ContentProcessor(str(OUTPUT_DIR))
    processor.process_all(str(DATA_DIR), args.mode)

    print("\nTLDL processing completed")


if __name__ == "__main__":
    main()
