# HTTP, parsing, and media

## Current request helpers

Use the current `keiyoushi.network` suspend extensions and close responses:

```kotlin
val document = client
    .get("$baseUrl/series/$slug", Fetch.DOCUMENT)
    .asJsoup()

val result = client
    .get(apiUrl, Fetch.XHR, ensureSuccess = false)
    .use { response ->
        if (!response.isSuccessful) return@use null
        response.parseAs<MyDto>()
    }
```

Select `Fetch.DOCUMENT`, `Fetch.XHR`, `Fetch.SCRIPT`, `Fetch.IMAGE`, or `Fetch.NONE` based on the actual request. Prefer `parseAs<T>()`, `asJsoup()`, and `toJsonRequestBody()` over manual body strings and local `Json` instances.

Rate-limit the source client with `configureClient()` and `rateLimit`. Do not make unbounded parallel requests for every card in a catalogue.

## Status handling

Use `ensureSuccess = false` only when the code intentionally handles status. Then distinguish:

- `401`: authentication is required or no longer valid; do not invent credentials;
- `403`: access denied, permission, or anti-bot challenge; report/propagate it, do not bypass;
- `404`: missing post/media/route; return an explicit empty/missing result where appropriate;
- `429`: rate limited; respect server signals and source rate limits;
- `5xx`: upstream failure; do not misparse an error page as valid JSON/HTML.

Do not silently turn all failures into “no results” if that hides a broken source. Use `HttpException` or the repository's established error path when the host should display a failure.

## HTML and JSON

- Define `@Serializable` regular DTO classes for JSON; map only fields used.
- Use `@SerialName` only when the JSON key differs or is not a Kotlin identifier.
- Make mandatory identity fields mandatory where the current API permits it; do not default a missing ID to zero just to keep parsing.
- Use precise selectors scoped to the content container. Avoid selecting every `<a>` or `<img>` on a page.
- Resolve relative links with `element.absUrl("href")` or `attr("abs:href")`.
- Treat JSON-LD as supplementary metadata; validate duration formats and ignore malformed nodes.

## Covers, gallery, and video

Keep these separate:

- **cover:** one thumbnail for the catalogue/detail card;
- **gallery/pages:** reader images, ideally from the verified post/chapter ID;
- **video:** media URL(s), MIME/extension, and duration only when observed.

Never use every page `<img>` as the cover. Never classify a CDN image link as an artist credit. Filter video URLs by observed media type/extension and allowed host policy.

If reading an MP4 header for duration, use a bounded `Range` request and state the maximum read. A Range response may be refused or ignored; that is an unknown duration, not permission to download the full file.

## Credits and external links

Links are not automatically credits. Accept a link only when there is positive evidence:

- it is inside an explicit credit/artist/source container;
- it has a meaningful visible label;
- it is not an image/CDN/media URL, navigation link, advertisement, or blank anchor;
- its URL is resolved and retained with the label.

If the site does not expose enough evidence, leave credits empty and preserve the raw tag/metadata as unclassified rather than guessing.

## WebView and anti-bot boundary

Use the repository's `runWebView` only for a legitimate browser-dependent site flow that the host supports. It is not a license to defeat Cloudflare or an authentication wall. Do not add TLS-disabling proxy code to production extensions. Debug proxies must be temporary, local, and never committed.
