# Skill validation report

Validation date: 2026-11-15

## Inputs inspected

- OpenCode skill format: existing `.opencode/skills/*/SKILL.md` files in the workspace.
- Current source guidance: `extensions-source/CONTRIBUTING.md`, current `core`, `lib`, and `src` trees.
- Legacy guidance: archived AniYomi `aniyomi-extensions/CONTRIBUTING.md` fetched from the official GitHub repository.
- SaradaHentai implementation, fixtures, audit log, and compiled APK.

## Checks run

```text
python3 scripts/validate_skill.py
OK

python3 -m unittest -v examples/fixture_test.py
Ran 1 test ... OK
```

The validator checks required files, required concepts, and the identity regression fixture. It does not compile Kotlin or pretend to be an Android build.

## Verified contents

- current `KeiSource`/KSP/DSL workflow;
- legacy `AnimeHttpSource`/`ParsedAnimeHttpSource` workflow kept separate;
- exact URL/slug/ID identity and async-state rules;
- `parseAs`, `asJsoup`, `Fetch`, `rateLimit`, DTO, date, URL, WebView, and media guidance based on current repository documentation;
- pagination/search/filter/detail/page flow;
- explicit HTTP 401/403/404/429/5xx handling;
- no anti-bot bypass or full media download guidance;
- fixture and APK validation gate;
- SaradaHentai identity and credit-extraction regression lessons.
- independent SaradaHentai contract checks for slug/permalink agreement, parsed URLs, conditional detail fetching, image-only galleries, and explicit credit containers.
- detail presentation and WebView/video URL separation are documented against the inspected current `KeiSource` API (`getMangaUrl`/`getChapterUrl`) and legacy anime API naming.

## Remaining validation

- The Kotlin snippet is a repository-aware example, not a standalone module and is not compiled by this package validator.
- The skill cannot certify a future extension without running that extension's own Gradle build, lint, fixtures, and host-app/device checks.
- Runtime and live-site behavior always remain task-specific.
