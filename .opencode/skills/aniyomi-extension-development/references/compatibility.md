# AniYomi, Mihon, and Keiyoushi compatibility

## Do not collapse names into one API

| Generation | Registration | Main base | Models/methods | Build metadata |
|---|---|---|---|---|
| Legacy AniYomi | `extClass`, factory/class | `AnimeHttpSource`, `ParsedAnimeHttpSource` | `SAnime`, `AnimesPage`, `fetchAnimeDetails`, `fetchEpisodeList` | Groovy `ext {}` |
| Current Keiyoushi/Mihon | `@Source` + KSP DSL | `KeiSource` | `SManga`, `MangasPage`, `fetchMangaUpdate`, `getPageList` | Kotlin `keiyoushi {}` + `libVersion = "1.6"` |

The host application and extension library may be forked, renamed, or versioned independently. Verify the checked-out source and dependency versions instead of assuming an app's current API matches the old Aniyomi documentation.

## Porting checklist

1. Translate the host lifecycle and model names.
2. Translate source registration/build metadata.
3. Check HTTP helper signatures and response ownership.
4. Check date units: current chapter uploads use epoch milliseconds in the documented model.
5. Recheck filters, page/video models, and generated metadata.
6. Compile against the target repository; static translation is insufficient.

## Historical examples

The archived AniYomi documentation remains useful for conceptual call flow and device debugging, but its `Anime*` APIs are historical. The current Keiyoushi guide is authoritative for `KeiSource`, KSP, `source {}`, `parseAs`, `Fetch`, and `rateLimit`.
