import os
from pathlib import Path

# allow to use the local 'ffmpeg.exe' and 'ffprobe.exe' stored in ffmpeg/bin folder, instead of global
ffmpeg_path = Path(__file__).resolve().parent.parent / "ffmpeg" / "bin"

# path to ffmpeg executable
os.environ["PATH"] += os.pathsep + str(ffmpeg_path)