"""Step 1: run jev (clicker) toward a goal, then pull the video URL out of its run folder."""

from __future__ import annotations

import json
import os
import re
import subprocess
from pathlib import Path

from yt_dlp.extractor import gen_extractor_classes

# The generic extractor claims almost any URL, so it would match every page.
_EXTRACTORS = [ie for ie in gen_extractor_classes() if ie.ie_key() != "Generic"]
_URL_RE = re.compile(r"https?://[^\s'\"<>)\]]+")

GOAL_SUFFIX = " Stop once the video's own page is open in the browser."


def supported(url: str) -> str | None:
    """Name of the yt-dlp extractor that handles this URL, or None. No network call."""
    for ie in _EXTRACTORS:
        if ie.suitable(url):
            return ie.ie_key()
    return None


def run_jev(goal: str, jev_dir: Path, act: bool = True, steps: int = 40) -> Path:
    """Run clicker in jev's repo and return the run folder it created."""
    runs = jev_dir / "runs"
    before = set(runs.iterdir()) if runs.exists() else set()

    cmd = ["uv", "run", "clicker", goal + GOAL_SUFFIX, "--steps", str(steps)]
    if act:
        cmd.append("--act")
    subprocess.run(cmd, cwd=jev_dir, check=False)  # jev exits non-zero on some stops

    new = sorted(set(runs.iterdir()) - before) if runs.exists() else []
    if not new:
        raise RuntimeError(f"jev wrote no run folder under {runs}")
    return new[-1]


def _urls_in(obj) -> list[str]:
    """Every URL in a JSON value, in document order."""
    if isinstance(obj, str):
        return _URL_RE.findall(obj)
    if isinstance(obj, dict):
        return [u for v in obj.values() for u in _urls_in(v)]
    if isinstance(obj, list):
        return [u for v in obj for u in _urls_in(v)]
    return []


def candidate_urls(run_dir: Path) -> list[str]:
    """URLs the run saw, newest first: last step's payload, earlier payloads, then run.json."""
    found: list[str] = []
    for payload in sorted(run_dir.glob("step-*-payload.txt"), reverse=True):
        found += _URL_RE.findall(payload.read_text(errors="ignore"))
    run_json = run_dir / "run.json"
    if run_json.exists():
        found += reversed(_urls_in(json.loads(run_json.read_text())))
    seen: set[str] = set()
    return [u.rstrip(".,;") for u in found if not (u in seen or seen.add(u))]


_LISTING = ("Search", "Tab", "Playlist", "Channel", "User", "Feed")


def is_listing(extractor: str) -> bool:
    """Search results, channels and playlists: pages that list videos rather than are one."""
    return any(word in extractor for word in _LISTING)


def video_url(run_dir: Path) -> str:
    """The newest single-video URL from the run; a listing page only if nothing else matched."""
    matches = [(u, ie) for u in candidate_urls(run_dir) if (ie := supported(u))]
    for url, ie in matches:
        if not is_listing(ie):
            return url
    if matches:
        raise LookupError(
            f"jev stopped on a listing page ({matches[0][0]}), not a video. "
            "Rerun with a more specific goal, or pass --url."
        )
    raise LookupError(f"no yt-dlp-supported URL in {run_dir}")


def jev_dir_from_env() -> Path:
    path = os.environ.get("JEV_DIR")
    if not path:
        raise SystemExit("Set JEV_DIR to your typesafe-computer-use checkout.")
    return Path(path).expanduser()
