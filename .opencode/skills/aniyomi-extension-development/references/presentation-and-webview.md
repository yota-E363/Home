# Detail presentation and WebView/video separation

Use this reference when a request concerns a fiche/detail screen, duplicated metadata, the “Open in WebView” action, or video playback.

## Field mapping before implementation

Inspect the actual host model and UI for the target API generation. Build a mapping table before changing a mapper:

| Site fact | Native field when available | Rule |
|---|---|---|
| publication title | `SManga.title` / `SAnime.title` | title only |
| WordPress/publication author | `author` | never merge with artist |
| creator/artist | `artist` | only from explicit evidence or validated rules |
| reliable categories/genres | `genre` / native genre field | use only relevant, observed values |
| reliable status | `status` | leave unknown/default when the site does not prove it |
| synopsis/editorial text | `description` | synopsis/text only; no metadata dump |
| raw tags | native tag field if the target host has one | preserve all raw tags |
| unclassified tags | native field or clearly labeled fallback | never silently discard or guess |
| credits | native field or clearly labeled fallback | retain meaningful label + URL only |

Current Keiyoushi manga models expose title, author, artist, genre, status, and description, but do not automatically provide arbitrary `tags` or `credits` fields. If the target app has no native custom field, decide explicitly whether a compact labeled fallback in description is acceptable for that app/version. Do not duplicate author, artists, categories, or tags in multiple fields merely because the UI has no custom section.

Do not invent studio, synopsis, status, episode count, source label, library state, or other values from a presentation example. An example layout is not source evidence.

## Description rule

The description mapper must answer one question: “What descriptive text did the source publish for this item?” It must not append a block such as:

```text
Author: ...
Artists: ...
Categories: ...
Tags: ...
Credits: ...
```

Those values belong in native fields where available. If a fallback is unavoidable, document the UI limitation and use clearly separated, non-duplicated sections only for values that cannot be represented otherwise. A missing synopsis stays missing.

## WebView URL versus media URL

Always keep these concepts separate:

```text
reader/detail HTML page  -> WebView/open/share URL
video MP4/HLS stream     -> player Video URL only
extension APK             -> installation artifact, never a content URL
```

For current `KeiSource`, the verified hooks are:

- `getMangaUrl(manga)`: absolute web URL used by the host for WebView and sharing;
- `getChapterUrl(chapter)`: absolute web URL used by the host for the chapter/reader WebView and sharing;
- `getPageList(chapter)`: reader page extraction;
- video/player APIs depend on the current host model and must be checked in the target repository.

The current `KeiSource` API does **not** use `getAnimeUrl()` or `getEpisodeUrl()`. Those names belong to legacy AniYomi anime extensions, where they map `SAnime` and `SEpisode` to page URLs. Confirm the generation before editing either method.

For a legacy anime source:

- `getAnimeUrl(anime)` must return the HTML anime/detail page;
- `getEpisodeUrl(episode)` must return the HTML episode/watch page;
- `Video.videoUrl` or the equivalent parser result must contain the actual MP4/HLS stream;
- do not return the stream from the WebView URL method.

If the site has distinct page and stream URLs, store/use both. The page URL is the one for WebView; the stream URL is the one for playback. Reject URLs ending in `.mp4`, `.m3u8`, `.mpd`, `.apk`, or a download route when assigning a page/WebView URL unless the repository's verified host flow explicitly defines that route as an HTML page.

## Required regression checks

For at least two publications/episodes:

1. open the detail and verify title, cover, author, artist, genres, and description all belong to the same remote ID;
2. refresh/update with both detail and chapter/episode flags;
3. verify metadata is not duplicated in description;
4. verify raw and unclassified tags remain available according to the host UI contract;
5. verify credits exclude ads, image/CDN URLs, blank links, and unrelated navigation;
6. trigger WebView and verify the loaded URL is the HTML page, not a stream or APK;
7. play the video and verify the player still receives the independent stream URL;
8. run the fixture, compile, lint, and device checks, reporting live limitations separately.
