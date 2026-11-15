# Call flow, identity, and concurrency

## Current KeiSource flow

Current `KeiSource` exposes suspend methods for:

- `getPopularManga(page)`;
- `getLatestUpdates(page)`;
- `getSearchMangaList(page, query, filters)`;
- `getMangaByUrl(url)` for URL search/deep-link resolution;
- `fetchMangaUpdate(manga, chapters, fetchDetails, fetchChapters)`;
- `getPageList(chapter)`.

The host identifies a cached manga primarily by its `SManga.url`. A detail/update request can happen later, including after backup restore, so the URL must be sufficient to resolve the same source object again.

## Safe list-to-detail mapping

Bad:

```kotlin
val post = requestPosts(page = 1, slug = null).firstOrNull()
```

Good:

```kotlin
private fun slugFromSourceUrl(value: String): String? = value
    .substringBefore('?')
    .substringBefore('#')
    .trimEnd('/')
    .substringAfterLast('/')
    .takeIf { it.isNotBlank() }

val requestedSlug = slugFromSourceUrl(manga.url)
val post = requestedSlug?.let { slug ->
    requestPosts(page = 1, slug = slug)
        .firstOrNull { it.slug == slug }
}
    ?: return SMangaUpdate(manga, chapters)
```

If the API uses IDs, use the ID and verify the returned ID. If the URL has a date prefix or nested route, use a canonical path helper rather than assuming the last segment is the slug.

## No shared “current item” state

Do not store the selected post, current slug, current document, or current metadata in a mutable property. A user can open two details, refresh, rotate the device, or trigger an update while an earlier request is still running. Keep identity in function arguments and local values. If a cache is needed, key it by canonical URL/ID and use a concurrency-safe cache with an explicit invalidation policy.

## Response ownership checks

Every multi-request detail flow should follow this shape:

```text
requested URL/slug/ID
  -> exact post request
  -> verify returned identity
  -> derive all child requests from verified post.id/link
  -> map cover/gallery/video/credits from that post only
```

Never combine a cover from the catalogue item with metadata fetched from an unverified first REST result. Never let an async callback mutate a screen/global object belonging to another request.

## Pagination and search

- Start page numbering from the repository/site contract, commonly `1`.
- Preserve server pagination headers when available (`X-WP-TotalPages`, cursors, or explicit next links).
- `hasNextPage` must be false when the server says there is no next page or the returned batch is empty.
- Search must encode the query through `HttpUrl` builders or the repository helper; do not concatenate raw user input.
- Filters should map one UI state to one request parameter and be tested with default, include, exclude, and empty states where supported.

## Legacy flow

Legacy AniYomi calls are named differently (`fetchPopularAnime`, `fetchSearchAnime`, `fetchAnimeDetails`, `fetchEpisodeList`, `fetchVideoList`). The same identity rules apply; only the host interfaces and model names change.
