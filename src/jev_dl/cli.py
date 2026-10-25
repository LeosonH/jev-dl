"""jev-dl "goal"  →  jev finds the page, yt-dlp downloads it."""

from __future__ import annotations

import argparse
from pathlib import Path

from .download import PRESETS, download
from .find import jev_dir_from_env, run_jev, supported, video_url


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="jev-dl", description=__doc__)
    src = p.add_mutually_exclusive_group(required=True)
    src.add_argument("goal", nargs="?", help="plain-English goal for jev")
    src.add_argument("--url", help="skip jev and download this URL")
    src.add_argument("--from-run", type=Path, help="reuse an existing jev run folder")
    p.add_argument("--preset", choices=PRESETS, default="best")
    p.add_argument("--out", type=Path, default=Path("~/Downloads"))
    p.add_argument("--cookies-from", metavar="BROWSER", help="e.g. chrome, for logged-in sites")
    p.add_argument("--steps", type=int, default=40)
    p.add_argument("--dry-run", action="store_true", help="find the URL, don't download")
    a = p.parse_args(argv)

    if a.url:
        url = a.url
    else:
        run_dir = a.from_run or run_jev(a.goal, jev_dir_from_env(), steps=a.steps)
        print(f"run folder: {run_dir}")
        url = video_url(run_dir)

    print(f"url: {url}  ({supported(url) or 'unrecognised'})")
    if a.dry_run:
        return 0

    path = download(url, a.preset, a.out, a.cookies_from)
    print(f"saved: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
