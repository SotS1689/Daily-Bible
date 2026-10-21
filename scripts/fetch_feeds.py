"""Fetch the latest videos for each channel and save them to feeds.json.

Run by .github/workflows/update-feeds.yml so the page can read the feeds
from its own site instead of relying on third-party CORS proxies.
Keep CHANNELS in sync with the CHANNELS list in index.html.
"""
import json
import sys
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path

CHANNELS = [
    {"name": "Daily Dose of Greek", "id": "UCRSbS2XhqOhnSUzWfGHUkLg"},
    {"name": "Daily Dose of Hebrew", "id": "UC0fRqEfY1ZaiWiJWTj7HQng"},
    {"name": "Daily Dose of Latin", "id": "UCMldVrQ8rKkWyevvQonijoA"},
    {"name": "Daily Dose of Septuagint", "id": "UC5SB4egyj9-RNdjL-VxcDRw"},
]

OUT_FILE = Path(__file__).resolve().parent.parent / "feeds.json"
NS = {
    "atom": "http://www.w3.org/2005/Atom",
    "yt": "http://www.youtube.com/xml/schemas/2015",
}


def fetch_entries(channel_id):
    url = f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Daily-Bible feed updater)"})
    with urllib.request.urlopen(req, timeout=30) as res:
        root = ET.fromstring(res.read())
    entries = []
    for entry in root.findall("atom:entry", NS):
        video_id = entry.findtext("yt:videoId", default="", namespaces=NS).strip()
        title = entry.findtext("atom:title", default="", namespaces=NS).strip()
        published = entry.findtext("atom:published", default="", namespaces=NS).strip()
        if video_id:
            entries.append({"id": video_id, "title": title, "published": published})
    return entries


def main():
    try:
        old = json.loads(OUT_FILE.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        old = {}
    old_feeds = old.get("feeds", {})

    feeds = {}
    failures = 0
    for channel in CHANNELS:
        try:
            entries = fetch_entries(channel["id"])
            if not entries:
                raise ValueError("feed had no entries")
            feeds[channel["id"]] = {"name": channel["name"], "entries": entries}
            print(f"{channel['name']}: {len(entries)} videos, latest '{entries[0]['title']}'")
        except Exception as err:
            failures += 1
            print(f"{channel['name']}: FAILED ({err})", file=sys.stderr)
            # Keep the last good copy so one bad fetch doesn't blank the page
            if channel["id"] in old_feeds:
                feeds[channel["id"]] = old_feeds[channel["id"]]

    if failures == len(CHANNELS):
        sys.exit("Every channel failed; leaving feeds.json unchanged.")

    # Only touch the file when the videos changed, so the workflow doesn't commit every hour
    if feeds == old_feeds:
        print("No new videos.")
        return

    data = {"updated": datetime.now(timezone.utc).isoformat(timespec="seconds"), "feeds": feeds}
    OUT_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote {OUT_FILE.name}")


if __name__ == "__main__":
    main()
