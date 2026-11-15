# Graph Report - all.mangadraft  (2026-11-06)

## Corpus Check
- 8 files · ~1,172 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 79 nodes · 134 edges · 10 communities (2 shown, 8 thin omitted)
- Extraction: 94% EXTRACTED · 6% INFERRED · 0% AMBIGUOUS · INFERRED: 8 edges (avg confidence: 0.85)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `f8032a66`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- UriPartFilter
- MangaDraft
- Setup Instructions for Mangadraft
- MangaDraftProjectDto
- MangaDraftPageDTO
- MangaDraftCatalogResponseDto
- MangaDraftSearchResponseDto

## God Nodes (most connected - your core abstractions)
1. `MangaDraft` - 17 edges
2. `UriPartFilter` - 11 edges
3. `Setup Instructions for Mangadraft` - 7 edges
4. `MangaDraftProjectDto` - 5 edges
5. `MangaDraftCatalogResponseDto` - 4 edges
6. `MangaDraftPageDTO` - 4 edges
7. `MangaDraftSearchResponseDto` - 4 edges
8. `Build it yourself` - 4 edges
9. `SortFilter` - 3 edges
10. `TypeFilter` - 3 edges

## Surprising Connections (you probably didn't know these)
- `MangaDraft` --inherits--> `KeiSource`  [EXTRACTED]
  src/eu/kanade/tachiyomi/extension/all/mangadraft/MangaDraft.kt →   _Bridges community 2 → community 0_

## Import Cycles
- None detected.

## Communities (10 total, 8 thin omitted)

### Community 1 - "UriPartFilter"
Cohesion: 0.31
Nodes (9): FormatFilter, GenreFilter, LanguageFilter, OrderFilter, SectionFilter, SortFilter, StatusFilter, TypeFilter (+1 more)

### Community 3 - "Setup Instructions for Mangadraft"
Cohesion: 0.18
Nodes (10): 1. Get the extensions-source repository, 2. Copy this extension into the repo, 3. Build the APK, 4. Install on device, 5. Key files to customise, Build it yourself, Detected type: unknown, Easiest: build the APK on GitHub (no local tools) (+2 more)

## Knowledge Gaps
- **8 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `MangaDraft` connect `MangaDraft` to `MangaDraft.kt`, `UriPartFilter`, `MangasPage`, `MangaDraftPageDTO`?**
  _High betweenness centrality (0.267) - this node is a cross-community bridge._
- **Should `MangaDraft.kt` be split into smaller, more focused modules?**
  _Cohesion score 0.13333333333333333 - nodes in this community are weakly interconnected._
- **Why does `MangaDraftProjectDto` connect `MangaDraftProjectDto` to `MangaDraft.kt`?**
  _High betweenness centrality (0.082) - this node is a cross-community bridge._
- **Why does `MangaDraftCatalogResponseDto` connect `MangaDraftCatalogResponseDto` to `MangaDraft.kt`?**
  _High betweenness centrality (0.062) - this node is a cross-community bridge._