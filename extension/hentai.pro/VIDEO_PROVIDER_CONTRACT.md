# Video provider contract

`anime-build/src/en/hentaipro/.../VideoProvider.kt` defines the extension seam.

## Adding an official provider

1. Implement `VideoProvider` in its own file.
2. In `discover`, return `ProviderDiscovery.Available` only for a documented endpoint that the owner authorizes for the app.
3. Store only non-secret provider state in `Hoster.internalData`. Do not embed long-lived credentials or user tokens.
4. In `resolve`, validate the endpoint response and return `ProviderResolution.Available` only when every returned media URL is HTTPS and has a supported video or HLS content type.
5. Construct videos with the named `Video` API:

```kotlin
Video(
    videoUrl = manifestUrl,
    videoTitle = "English 1080p",
    headers = requestHeaders,
    subtitleTracks = listOf(Track(subtitleUrl, "English")),
)
```

6. Return `ProviderResolution.Unavailable` with a user-safe reason for HTTP errors, expired URLs, invalid playlists, missing subtitles, or an unavailable provider.
7. Add the provider to `videoProviders` in `HentaiPro` and add a live test that uses an authorized fixture.

The current `NhPlayerProvider` stops at the public iframe and intentionally returns unavailable. `OfficialVideoApiProvider` is the placeholder for the future authenticated contract.
