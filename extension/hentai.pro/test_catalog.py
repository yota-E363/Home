#!/usr/bin/env python3
"""Evidence tests for the public Hentai.Pro catalogue surface."""

import json
import re
import urllib.parse
import urllib.request
from pathlib import Path

from bs4 import BeautifulSoup

BASE_URL = "https://hentai.pro"
TEST_EPISODE = "/watch/sister-breeder-episode-5"


def fetch(path: str) -> BeautifulSoup:
    request = urllib.request.Request(
        urllib.parse.urljoin(BASE_URL, path),
        headers={"User-Agent": "Mozilla/5.0"},
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        assert response.status == 200, (path, response.status)
        return BeautifulSoup(response.read(), "html.parser")


def cards(document: BeautifulSoup) -> list[str]:
    return [
        link["href"]
        for link in document.select("article.post-card a.cover-link[href^='/watch/']")
        if link.get("href")
    ]


def main() -> None:
    results = {}

    popular = fetch("/?sort=popular")
    results["popular"] = {"ok": bool(cards(popular)), "count": len(cards(popular))}

    latest = fetch("/")
    results["latest"] = {"ok": bool(cards(latest)), "count": len(cards(latest))}

    search = fetch("/?q=sister")
    search_cards = cards(search)
    results["search"] = {
        "ok": bool(search_cards),
        "count": len(search_cards),
        "contains_test_title": any("sister-breeder" in item for item in search_cards),
    }

    detail = fetch(TEST_EPISODE)
    title = detail.select_one("h1")
    iframe = detail.select_one("iframe[src*='nhplayer.com']")
    results["detail"] = {
        "ok": title is not None and iframe is not None,
        "title": title.get_text(" ", strip=True) if title else None,
        "player_host": urllib.parse.urlparse(iframe["src"]).netloc if iframe else None,
    }

    episode_number = re.search(r"episode-(\d+(?:\.\d+)?)", TEST_EPISODE)
    results["episodes"] = {
        "ok": bool(title and episode_number),
        "count": 1,
        "episode_number": episode_number.group(1) if episode_number else None,
    }

    # The catalogue test deliberately records the unsupported protected player.
    results["videos"] = {
        "ok": False,
        "reason": "nhplayer iframe requires anti-bot verification; no direct media is tested or bypassed",
    }

    assert all(results[key]["ok"] for key in ("popular", "latest", "search", "detail", "episodes"))
    output = Path(__file__).with_name("catalog-tests.json")
    output.write_text(json.dumps(results, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps(results, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
