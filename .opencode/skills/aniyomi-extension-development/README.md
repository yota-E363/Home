# Aniyomi extension development skill

Install this directory as an OpenCode skill named `aniyomi-extension-development`.

## Invocation

Use the skill when the task mentions an Aniyomi/Mihon extension, source module, catalogue/detail parser, episode/video extraction, extension APK, or extension debugging. It is also appropriate for legacy `aniyomi-extensions` repositories, but it requires generation detection before code changes.

The main entry point is `SKILL.md`. It routes to the modular references instead of loading every document for every task.

## Contents

- `SKILL.md`: execution workflow and completion gate.
- `references/`: architecture, call flow, network/parsing, Kotlin, validation, compatibility, presentation/WebView, and SaradaHentai case study.
- `references/presentation-and-webview.md`: native detail-field mapping and HTML-page versus video-stream rules.
- `examples/`: current Keiyoushi snippets and a fixture-test pattern.
- `scripts/validate_skill.py`: structural validation for the skill package.

## Source of truth

The current Keiyoushi guidance is based on the checked-out `extensions-source/CONTRIBUTING.md` and the current source tree. The legacy guidance is based on the archived AniYomi `aniyomi-extensions/CONTRIBUTING.md`. The skill explicitly treats these as different generations.

## Transfer

Run from the skill directory:

```bash
python3 scripts/validate_skill.py
zip -r ../aniyomi-extension-development.zip .
```

The ZIP contains only the skill documentation, examples, and validator; it does not contain a repository, APK, credentials, or site data.
