# Kotlin patterns for current extensions

## Source skeleton

```kotlin
@Source
abstract class Example : KeiSource() {
    override fun OkHttpClient.Builder.configureClient() =
        rateLimit(permits = 2) { it.host == baseUrl.toHttpUrl().host }

    override suspend fun getPopularManga(page: Int): MangasPage =
        fetchPosts(page, search = null)

    override suspend fun getLatestUpdates(page: Int): MangasPage =
        fetchPosts(page, search = null)

    override suspend fun getSearchMangaList(
        page: Int,
        query: String,
        filters: FilterList,
    ): MangasPage = fetchPosts(page, query.trim().takeIf { it.isNotEmpty() })
}
```

The actual source needs its repository's imports and response model. Do not copy a legacy class name into a current `KeiSource` module.

## DTO pattern

```kotlin
@Serializable
class Post(
    val id: Int,
    val slug: String,
    val link: String,
    val title: Rendered,
    @SerialName("featured_media") val featuredMedia: Int,
)

@Serializable
class Rendered(val rendered: String)
```

Use a regular `class`, not `data class`, for ordinary serialized DTOs in current Keiyoushi sources. Keep fields private when they are only used by a mapper. Do not create a source-local `Json` object for standard parsing.

## Stable mapping

```kotlin
private fun Post.toManga() = SManga.create().apply {
    url = link.removePrefix(baseUrl)
    title = title.rendered
    thumbnail_url = verifiedCoverUrl
}
```

In real code, `verifiedCoverUrl` must be derived from this same `Post`; it must not come from a mutable property populated by another request.

## Models and API generations

Current models use `SManga`, `SChapter`, `MangasPage`, `Page`, and `SMangaUpdate`. Legacy AniYomi uses anime-prefixed models and methods. Read the actual dependency/API before porting a snippet.
