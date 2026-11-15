# Architecture and repository detection

## Current Keiyoushi/Mihon source tree

Verified against `extensions-source/CONTRIBUTING.md` and the checked-out SaradaHentai build:

```text
src/<lang>/<source>/
├── build.gradle.kts
├── res/mipmap-*/ic_launcher.png
└── src/eu/kanade/tachiyomi/extension/<lang>/<source>/
    ├── Source.kt
    ├── Dto.kt        # optional
    └── Filters.kt    # optional
```

The source class is annotated with `@Source` and extends `KeiSource`. Registration is generated from one or more `source {}` blocks in `build.gradle.kts`:

```kotlin
keiyoushi {
    name = "Example"
    versionCode = 1
    contentWarning = ContentWarning.SAFE
    libVersion = "1.6"

    source {
        lang = "en"
        baseUrl = "https://example.com"
    }
}
```

Do not manually declare `name`, `lang`, `id`, or `baseUrl` in the source class. KSP generates the entry point and metadata. Use `ext-bootstrap.py` for a new module. Load one module locally with `loadIndividualExtension("en", "source")` rather than loading the whole repository.

## Legacy AniYomi source tree

The archived AniYomi repository uses:

- `src/<lang>/<source>`;
- package `eu.kanade.tachiyomi.animeextension.<lang>.<source>`;
- Groovy `build.gradle` with `extName`, `extClass`, `extVersionCode`, and optional `isNsfw`;
- `AnimeHttpSource` or `ParsedAnimeHttpSource`;
- `AnimeSourceFactory` for multiple sources.

These names are not interchangeable with `KeiSource`, KSP, or `source {}`. Inspect `settings.gradle`, plugin versions, and an adjacent extension before selecting snippets.

## Repository reconnaissance checklist

```bash
find . -name AGENTS.md -print
find src/<lang>/<source> -type f -maxdepth 20 -print
grep -R "KeiSource\|AnimeHttpSource\|ParsedAnimeHttpSource" -n src/<lang>/<source>
sed -n '1,220p' CONTRIBUTING.md
```

Read the nearest contribution guide and agent instructions in full before editing extension code. Check `lib/` and `lib-multisrc/` for an existing solution before creating a dependency or reimplementing a decoder.

## Architecture facts vs assumptions

- **Fact:** current Keiyoushi source metadata is DSL/KSP-owned.
- **Fact:** legacy AniYomi source metadata is class/build-file based.
- **Fact:** the extension APK is installed by the host app as an Android package.
- **Assumption to verify:** whether a target app version supports a newly added library API or generated preference; inspect the target app/lib version and compile it.
