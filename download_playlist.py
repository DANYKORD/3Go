import sys
import subprocess
from pathlib import Path

# Ensure yt-dlp is installed
try:
    import yt_dlp
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "yt-dlp"])
    import yt_dlp

# Playlist URL (provided by user)
PLAYLIST_URL = "https://www.youtube.com/watch?v=QPh8h0hWkg0&list=PLn3ukorJv4vvMwZPLzlajVII2zJd-_BM-&index=3"

# Output directory (current directory)
output_dir = Path.cwd()

def safe_filename(s: str) -> str:
    return "".join(c for c in s if c.isalnum() or c in " _-.").strip()

# yt-dlp common options
ydl_opts_common = {
    "quiet": True,
    "no_warnings": True,
    "ignoreerrors": True,
    "outtmpl": str(output_dir / "%(title)s.%(ext)s"),
    "restrictfilenames": True,
}

# Download whole playlist, merging video+audio into mp4
with yt_dlp.YoutubeDL({**ydl_opts_common, "format": "bestvideo+bestaudio/best", "merge_output_format": "mp4"}) as ydl:
    info = ydl.extract_info(PLAYLIST_URL, download=False)
    entries = info.get("entries", [])
    if not entries:
        print("No videos found in the playlist.")
        sys.exit(1)
    for entry in entries:
        if entry is None:
            continue
        title = safe_filename(entry.get("title", "video"))
        target_path = output_dir / f"{title}.mp4"
        if target_path.exists():
            print(f"{target_path} already exists – skipping")
            continue
        # Download and merge
        ydl.download([entry["webpage_url"]])
        print(f"Downloaded {target_path}")

print("All done.")
