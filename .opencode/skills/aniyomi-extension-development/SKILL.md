---
name: aniyomi-extension-development
description: Build, analyze, debug, test, compile, and maintain Aniyomi/Mihon extensions with repository-aware Kotlin and HTTP scraping workflows. Distinguishes legacy AniYomi APIs from current Keiyoushi KeiSource architecture and requires evidence before claiming success.
---

# Aniyomi extension development

Use this skill for any task involving an Aniyomi, Mihon, or related source extension: creation, parser work, catalogue/detail bugs, media extraction, HTTP failures, compatibility, APK generation, or maintenance.

This is an execution skill, not a generic scraping guide. Inspect the actual repository and its current API before editing.

## Non-negotiable rules

1. **Identify the generation first.** Do not mix legacy AniYomi classes with current Keiyoushi classes.
   - Current Keiyoushi: `KeiSource`, `@Source`, `keiyoushi { source { ... } }`, KSP, `libVersion = "1.6"`, package `eu.kanade.tachiyomi.extension...`.
   - Legacy AniYomi: `AnimeHttpSource`/`ParsedAnimeHttpSource`, `AnimeSourceFactory`, Groovy `ext {}`, package `eu.kanade.tachiyomi.animeextension...`.
   - If both are present, follow the module's own build logic and document the compatibility boundary.
2. **Read local instructions before source edits.** Find the nearest `AGENTS.md`, then read the repository contribution guide in full enough to locate scaffolding, source declaration, call flow, debugging, and build rules.
3. **Analyze before modifying.** Map the module, entry class, build registration, DTOs, request methods, URL identity, cache/update path, and tests. Use graph/index tools when the workspace provides them.
4. **Preserve content identity.** A catalogue item, detail request, update response, chapter/episode, page list, cover, and video must all be tied to the same canonical URL/slug/remote ID. Never use “first result” as an unverified detail fallback.
5. **Do not invent APIs.** Verify symbols in the checked-out `core`, `extensions-lib`, app source, or current repository examples. A historical document is not proof that the current API still exists.
6. **No anti-bot bypass.** Never harvest challenge cookies, rotate proxies, disable TLS verification, spoof authentication, or automate a protection in order to defeat it. Report 401/403/429/5xx accurately and use only an explicitly authorized browser/WebView flow when the host project permits it.
7. **No full media downloads for metadata.** Use bounded reads or Range only when the site and task justify it; never claim duration/quality is known when it was not observed.
8. **Test before conclusion.** Run fixture/parser tests, targeted Gradle compilation, and release lint. A successful parser test is not proof of Kotlin compilation; a compiled APK is not proof of live-site behavior.

## Operating workflow

### Phase 0 — classify the task and repository

Run, adapt paths to the workspace:

```bash
find .. -name AGENTS.md -print
find . -maxdepth 3 -name 'settings.gradle*' -o -name 'build.gradle*'
grep -R "KeiSource\|AnimeHttpSource\|libVersion\|extClass" -n --include='*.kt' --include='*.gradle*' . | head -100
```

Record:

- repository/project and module root;
- current vs legacy API generation;
- language/source directory and package;
- build tool, SDK/JDK requirements, and target app family;
- existing fixture/unit/instrumentation tests;
- whether the task is source code, shared library, theme, or build infrastructure.

For current Keiyoushi work, prefer `ext-bootstrap.py` and load only the target module in `settings.gradle.kts` during local development. Do not restructure an existing project merely to match a template.

### Phase 1 — establish the contract

Before writing code, write a short contract table:

| Concern | Evidence | Implementation | Test | Unknown |
|---|---|---|---|---|
| list/search | network fixture or observed request | request + parser | fixture | live status |
| details | canonical URL/ID | exact lookup | identity test | missing fields |
| media | MIME/selector/API | cover/gallery/video separation | media fixture | variants |
| errors | observed status or API contract | explicit handling | status fixture | retry policy |

Use facts from the current source and upstream docs. Label hypotheses as hypotheses.

### Phase 2 — implement the smallest correct flow

Implement in this order:

1. source registration and package;
2. one catalogue/list endpoint with deterministic identity;
3. search and pagination;
4. exact detail/update lookup;
5. chapter/episode or autonomous publication model;
6. page/gallery/video extraction;
7. optional filters, mirrors, preferences, or special libraries;
8. error reporting and tests.

Do not add series/episode relationships, quality variants, classifications, or “helpful” fallbacks unless the site contract proves them.

### Phase 3 — validate in layers

Run the narrowest relevant checks first, then the full module checks:

```bash
python3 -m unittest discover -v tests
./gradlew :src:<lang>:<source>:assembleDebug
./gradlew :src:<lang>:<source>:lintRelease
```

For a legacy repository use its documented equivalent, usually `./gradlew assemble...` or the source module task. Never substitute an unrelated Android app build.

Inspect the APK manifest and class registration. An extension APK should expose the extension feature and generated/source entry class, not just compile as a generic Android application.

## Routing to references

Read only the references needed for the task, then return to this delivery gate.

- Repository detection and source skeleton: `references/architecture.md`
- Catalogue, detail identity, pagination, filters, and update flow: `references/call-flow-and-identity.md`
- HTTP, JSON, HTML, WebView, media, and status handling: `references/network-and-parsing.md`
- Kotlin/DTO patterns: `references/kotlin-patterns.md`
- Fixtures, regression tests, build, APK, and device verification: `references/validation.md`
- Current vs legacy compatibility: `references/compatibility.md`
- Detail-field presentation and WebView/video URL separation: `references/presentation-and-webview.md`
- Lessons from SaradaHentai: `references/saradahentai-case-study.md`
- Reusable snippets: `examples/`

## Identity invariant

For every source, define one canonical key before implementing details:

```text
catalogue entry -> canonical source URL -> stable slug or remote ID
                 -> exact detail request -> same remote ID
                 -> same ID for cover, gallery, video, credits, and update
```

Required checks:

- normalize trailing slashes, query strings, fragments, and URL encoding deliberately;
- preserve the source URL in `SManga.url`/`SAnime.url` as the lookup key;
- when using a slug or ID endpoint, verify the returned slug/ID before mapping;
- never omit an identity query and then accept page 1's first result;
- keep all request-local values local to the suspend call; do not use mutable global “current item” state;
- distinguish “missing”, “not observed”, and “request failed”.

## Completion gate

Do not say “working”, “operational”, or “installable” until the evidence exists:

- source/module registration inspected;
- no invented or cross-generation APIs;
- identity regression covered;
- representative JSON/HTML/media fixtures pass;
- HTTP error behavior tested;
- targeted `assembleDebug` or equivalent succeeds;
- `lintRelease` or repository-required lint succeeds;
- APK/package manifest checked;
- live validation explicitly reported as passed, blocked, or not attempted;
- exact commands and artifact path recorded.

When a live site is blocked, continue with local fixtures but never upgrade fixture evidence into live evidence.
