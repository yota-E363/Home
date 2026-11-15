#!/usr/bin/env python3
"""Low-impact confirmation checks for the initial public security observations."""

import json
import urllib.request
from urllib.error import HTTPError
from pathlib import Path


def get(url: str) -> tuple[int, object]:
    request = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 security-audit"})
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            return response.status, response.headers
    except HTTPError as error:
        return error.code, error.headers


def main() -> None:
    status, headers = get("https://hentai.pro/")
    values = {key.lower(): headers.get_all(key) or [] for key in headers.keys()}
    csp = "\n".join(values.get("content-security-policy", []))
    result = {
        "homepage_status": status,
        "duplicate_x_frame_options": len(values.get("x-frame-options", [])) > 1,
        "duplicate_referrer_policy": len(values.get("referrer-policy", [])) > 1,
        "hsts_present": bool(values.get("strict-transport-security")),
        "unsafe_inline_script": "script-src" in csp and "'unsafe-inline'" in csp,
        "unsafe_inline_style": "style-src" in csp and "'unsafe-inline'" in csp,
        "frame_src_present": "frame-src" in csp,
    }

    player_status, player_headers = get("https://nhplayer.com/v/7cFGJrgtgYIGV1a/")
    cookies = player_headers.get_all("set-cookie") or []
    result.update(
        {
            "player_status": player_status,
            "player_session_cookie_secure": any("secure" in value.lower() for value in cookies),
            "player_session_cookie_httponly": any("httponly" in value.lower() for value in cookies),
            "player_session_cookie_samesite": any("samesite" in value.lower() for value in cookies),
        },
    )

    Path(__file__).with_name("security-checks.json").write_text(
        json.dumps(result, indent=2) + "\n",
    )
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
