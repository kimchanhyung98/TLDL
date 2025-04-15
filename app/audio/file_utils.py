from pathlib import Path

# Supported audio file extensions
SUPPORTED_AUDIO_EXTENSIONS = [".mp3", ".mp4", ".mpeg", ".mpga", ".m4a", ".wav", ".webm"]


def get_audio_files(directory):
    """Find audio files in the directory

    Args:
        directory (Path): Directory to search for audio files

    Returns:
        list[Path]: List of found audio file paths
    """
    audio_files = []
    for ext in SUPPORTED_AUDIO_EXTENSIONS:
        audio_files.extend(list(directory.glob(f"*{ext}")))
    return audio_files
