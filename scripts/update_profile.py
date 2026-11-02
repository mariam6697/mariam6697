"""Refresh generated sections while preserving the last successful daily pick."""
import html
import json
from pathlib import Path
import re
from urllib.error import URLError
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[1]
MUSIC_API = "https://mariam.sh/api/discogs"


def replace_section(text, name, content):
    start, end = f"<!-- {name}:start -->", f"<!-- {name}:end -->"
    if text.count(start) != 1 or text.count(end) != 1:
        raise ValueError(f"Expected one pair of {name} markers")
    before, remainder = text.split(start)
    old, after = remainder.split(end)
    return f"{before}{start}\n{content}\n{end}{after}"


def release_markup(payload):
    if payload.get("ok") is not True:
        raise ValueError("No release available")
    release = payload["release"]
    url = release["url"]
    if not re.fullmatch(r"https://www\.discogs\.com/release/[0-9]+", url):
        raise ValueError("Unexpected release URL")
    date = payload["date"]
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", date):
        raise ValueError("Unexpected release date")
    artist, title = (html.escape(release[key], quote=True) for key in ("artist", "title"))
    return f'<a href="{url}">{artist} — {title}</a>\n\n<sub>Picked {date} · America/Santiago</sub>'


def update_readme(text, payload=None, metrics_available=False):
    if metrics_available:
        text = replace_section(text, "metrics", "![GitHub activity and languages](github-metrics.svg)")
    if payload is not None:
        text = replace_section(text, "release", release_markup(payload))
    return text


def main():
    readme = ROOT / "README.md"
    text = readme.read_text(encoding="utf-8")
    payload = None
    try:
        with urlopen(MUSIC_API, timeout=20) as response:
            payload = json.load(response)
        release_markup(payload)
    except (URLError, TimeoutError, ValueError, KeyError, TypeError):
        print("Music unavailable; keeping the previous daily pick.")
        payload = None
    updated = update_readme(text, payload, (ROOT / "github-metrics.svg").is_file())
    if updated != text:
        readme.write_text(updated, encoding="utf-8")


if __name__ == "__main__":
    main()
