# Daily Dose of Bible

One page (`index.html`) that shows the newest videos from the Daily Dose of Greek, Hebrew, Latin and Septuagint YouTube channels. A GitHub Action (`.github/workflows/update-feeds.yml`) runs `scripts/fetch_feeds.py` every hour and commits the video list to `feeds.json`, which the page reads (if that fails, the page fetches the channels' feeds through public proxies).

Run locally: `python -m http.server 8000` in this folder, then open http://localhost:8000.

Deploys by GitHub Pages from `main` of SotS1689/Daily-Bible (taylordrummond.org/Daily-Bible). The Action commits every hour, so always `git pull` before changing anything.
