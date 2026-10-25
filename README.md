# jev-dl

Find a video by describing it, then download it.
[typesafe-computer-use](https://github.com/awlevin/typesafe-computer-use) (jev) drives the browser to the video's page; [yt-dlp](https://github.com/yt-dlp/yt-dlp) downloads it. jev never touches a download button, and yt-dlp never needs the screen.

```
jev-dl "open the most recent NeurIPS 2025 keynote on YouTube"
```

## Layout

```
jev-dl/
├── pyproject.toml
├── src/jev_dl/
│   ├── find.py       # run jev, read runs/<ts>/, pick the URL yt-dlp supports
│   ├── download.py   # yt-dlp presets: best, 720p, audio (mp3)
│   └── cli.py        # jev-dl entry point
└── tests/
    └── test_find.py  # fake run folders, no screen or network needed
```

## Setup

macOS, Python 3.12+, [uv](https://docs.astral.sh/uv/), and `ffmpeg` (`brew install ffmpeg`) for merging streams and mp3.

1. Set up jev by following its README: keys in its `.env`, plus Screen Recording and Accessibility permissions for your terminal.
2. Install this tool and point it at jev:

```
git clone <this repo> && cd jev-dl
uv sync --extra dev
export JEV_DIR=~/code/typesafe-computer-use
```

## Use

```
jev-dl "find the Vimeo upload of Big Buck Bunny" --dry-run   # find only, print the URL
jev-dl "…" --preset audio --out ~/Music                       # mp3
jev-dl "…" --cookies-from chrome                              # logged-in sites, no password typing
jev-dl --from-run $JEV_DIR/runs/<ts>                          # reuse a finished jev run
jev-dl --url https://vimeo.com/76979871                       # skip jev entirely
```

## How the URL is chosen

jev doesn't output a URL directly, so `find.py` reads the run folder:

1. It collects every URL it can find in the folder: step payloads first, newest step first, then `run.json`.
2. It keeps the URLs that a yt-dlp extractor claims. The `Generic` extractor is excluded, because it claims almost any page.
3. It prefers a single-video page. If jev stopped on search results, a channel or a playlist, the tool stops and asks for a sharper goal instead of downloading a whole list.

The goal sent to jev ends with "Stop once the video's own page is open in the browser", so the run ends on the right page.

## Tests

```
uv run pytest -q
```

Use this for content you have the right to download, and check each site's terms.
