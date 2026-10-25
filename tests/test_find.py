import json

from jev_dl.cli import main
from jev_dl.find import candidate_urls, supported, video_url


def make_run(tmp_path):
    run = tmp_path / "runs" / "2026-10-25T18-30-00"
    run.mkdir(parents=True)
    (run / "step-001-payload.txt").write_text(
        "app: Google Chrome\nurl: https://www.youtube.com/results?search_query=keynote\n"
    )
    (run / "step-002-payload.txt").write_text(
        "app: Google Chrome\nurl: https://www.youtube.com/watch?v=dQw4w9WgXcQ\n"
    )
    (run / "run.json").write_text(
        json.dumps({"goal": "find it", "outcome": "done", "answer": "Opened https://example.com/x."})
    )
    return run


def test_supported_skips_generic():
    assert supported("https://www.youtube.com/watch?v=dQw4w9WgXcQ") == "Youtube"
    assert supported("https://example.com/some/page") is None


def test_newest_payload_first(tmp_path):
    urls = candidate_urls(make_run(tmp_path))
    assert urls[0] == "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    assert "https://example.com/x" in urls  # trailing '.' stripped


def test_video_url_picks_watch_page(tmp_path):
    assert video_url(make_run(tmp_path)) == "https://www.youtube.com/watch?v=dQw4w9WgXcQ"


def test_listing_page_is_not_a_video(tmp_path):
    run = make_run(tmp_path)
    (run / "step-002-payload.txt").unlink()  # run ended on search results
    try:
        video_url(run)
    except LookupError as e:
        assert "listing page" in str(e)
    else:
        raise AssertionError("search results should not count as a video")


def test_cli_dry_run_from_run(tmp_path, capsys):
    assert main(["--from-run", str(make_run(tmp_path)), "--dry-run"]) == 0
    assert "watch?v=dQw4w9WgXcQ  (Youtube)" in capsys.readouterr().out
