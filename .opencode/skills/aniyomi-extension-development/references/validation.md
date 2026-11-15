# Tests, compilation, and device validation

## Fixture strategy

Build fixtures from observed responses, not invented “ideal” responses. Cover at least:

- two distinct catalogue posts with different IDs/slugs/URLs/titles/covers;
- search result and pagination metadata;
- detail JSON whose identity must match the requested slug/ID;
- media list containing cover plus gallery images;
- representative HTML with a real credit container, an image CDN link, an advertisement, and a blank anchor;
- video element/OG video and optional JSON-LD duration;
- malformed/missing optional fields;
- 401, 403, 404, 429, and 5xx behavior where the source handles them differently.

The crucial regression is not “parser returns a title”; it is:

```text
open A -> detail is A
open B -> detail is B
refresh A -> detail remains A
```

Run parser tests from their actual directory. A passing Python fixture test does not prove the Kotlin extension compiles.

## Current Keiyoushi commands

For a focused checkout:

```bash
./gradlew :src:<lang>:<source>:assembleDebug
./gradlew :src:<lang>:<source>:lintRelease
```

If SDK licenses or packages are missing, resolve the SDK explicitly with `sdkmanager` and record the exact package/version. Do not hide a failed build behind a generic “validated” claim.

## APK checks

```bash
find src/<lang>/<source>/build/outputs -name '*.apk' -print
$ANDROID_HOME/cmdline-tools/latest/bin/apkanalyzer manifest print path/to/extension.apk
unzip -l path/to/extension.apk | grep -E 'classes.dex|AndroidManifest.xml'
sha256sum path/to/extension.apk
```

Confirm the manifest has the extension feature, expected package, source metadata/entry class, language, content warning, and deep-link configuration when applicable.

## Runtime verification

Install the debug APK only on a test device/emulator with the matching Aniyomi/Mihon family. Use Logcat and, when available, host verbose network logging. Verify list, search, detail, update, page/video loading, and error behavior. Attach a debugger to the host app process; do not launch the extension APK as if it were a standalone app.

When live access is blocked, record that separately. Do not replace it with a claim based on fixtures.

## Evidence report

Report:

```text
Source/API generation:
Fixture tests:
Gradle assemble:
Release lint:
APK path + SHA-256:
Manifest/package check:
Runtime/device test:
Live network status:
Known unknowns:
```
