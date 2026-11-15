# SaradaHentai Catalogue Extractor V4

## Requirements
- Python 3.9+
- No third-party package required.

## Quick start
Run from this directory:

    python saradahentai_catalogue_v4.py --max-posts 100 --delay 1.2 --output saradahentai_v4_catalogue.json

Use the explicit classification file:

    python saradahentai_catalogue_v4.py --max-posts 100 --delay 1.2 --rules saradahentai_v4_classification_rules.example.json

The default run collects public WordPress posts, featured media, associated media attachments, public oEmbed author name/URL, page metadata, external links, and video URLs visible in the page source. If an MP4 duration is not exposed through JSON-LD, it requests at most the first 1 MiB using HTTP Range to inspect the MP4 movie header. It never downloads a complete video.

## Classification
WordPress categories are mapped to classification.categories.
All WordPress tag names are preserved in classification.tags.
Only explicit tag rules or clear suffixes such as (Artist), (Character), (Work) are normalized into artists, characters, works. Other tags remain in unclassified_tags.

Edit a copy of the rules JSON by adding exact tag names:

    {
      "tag_types": {
        "Exact tag name": "artists",
        "Another exact tag": "characters"
      }
    }

Allowed values: artists, characters, works.

## Useful options
- --max-posts N: maximum number of posts (default 100)
- --per-page N: REST page size (1–100; default 20)
- --delay SECONDS: minimum delay between requests (default 0.8)
- --timeout SECONDS: request timeout (default 20)
- --no-gallery: skip media attachment lookup
- --no-oembed: skip public author metadata lookup

## Safety / limitations
Read-only public requests. No authentication, anti-bot bypass, cookie harvesting, proxy rotation, or full media download. HTTP errors such as 401/403/429 are logged and not bypassed. A missing video URL means only that none was observed by this extractor on that page. Long galleries and editorial synopsis availability still require broader validation.
