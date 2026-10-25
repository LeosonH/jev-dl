"""Step 2: hand the URL to yt-dlp."""

from __future__ import annotations

from pathlib import Path

import yt_dlp

PRESETS: dict[str, dict] = {
    "best": {"format": "bv*+ba/b"},
    "720p": {"format": "bv*[height<=720]+ba/b[height<=720]"},
    "audio": {
        "format": "ba",
        "postprocessors": [{"key": "FFmpegExtractAudio", "preferredcodec": "mp3"}],
    },
}


def download(
    url: str,
    preset: str = "best",
    out_dir: Path = Path("~/Downloads"),
    cookies_from: str | None = None,
) -> Path:
    """Download one video and return the final file path."""
    opts = {
        **PRESETS[preset],
        "outtmpl": str(out_dir.expanduser() / "%(title)s [%(id)s].%(ext)s"),
        "noplaylist": True,
    }
    if cookies_from:  # reuse a logged-in browser session instead of typing passwords
        opts["cookiesfrombrowser"] = (cookies_from,)

    with yt_dlp.YoutubeDL(opts) as ydl:
        info = ydl.extract_info(url, download=True)
        files = info.get("requested_downloads") or [{}]
        return Path(files[0].get("filepath") or ydl.prepare_filename(info))
