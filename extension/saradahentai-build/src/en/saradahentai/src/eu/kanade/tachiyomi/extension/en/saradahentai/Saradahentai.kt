package eu.kanade.tachiyomi.extension.en.saradahentai

import eu.kanade.tachiyomi.network.HttpException
import eu.kanade.tachiyomi.source.model.FilterList
import eu.kanade.tachiyomi.source.model.MangasPage
import eu.kanade.tachiyomi.source.model.Page
import eu.kanade.tachiyomi.source.model.SChapter
import eu.kanade.tachiyomi.source.model.SManga
import eu.kanade.tachiyomi.source.model.SMangaUpdate
import keiyoushi.annotation.Source
import keiyoushi.network.Fetch
import keiyoushi.network.get
import keiyoushi.network.rateLimit
import keiyoushi.source.KeiSource
import keiyoushi.utils.asJsoup
import keiyoushi.utils.parseAs
import okhttp3.HttpUrl
import okhttp3.HttpUrl.Companion.toHttpUrl
import okhttp3.OkHttpClient
import org.jsoup.nodes.Document
import java.util.Locale

@Source
abstract class Saradahentai : KeiSource() {

    override fun OkHttpClient.Builder.configureClient() = rateLimit(2) { it.host == baseUrl.toHttpUrl().host }

    override suspend fun getPopularManga(page: Int): MangasPage = fetchPosts(page, null)

    override suspend fun getLatestUpdates(page: Int): MangasPage = fetchPosts(page, null)

    override suspend fun getSearchMangaList(page: Int, query: String, filters: FilterList): MangasPage = fetchPosts(page, query.trim().takeIf { it.isNotEmpty() })

    override suspend fun getMangaByUrl(url: HttpUrl): SManga? {
        if (!isSiteUrl(url)) return null
        val slug = saradaSlugFromUrl(url.encodedPath) ?: return null
        val post = requestPosts(1, slug).firstOrNull { it.slug == slug && postLinkMatchesSlug(it, slug) } ?: return null
        return post.toManga()
    }

    override fun getMangaUrl(manga: SManga): String = manga.url

    override fun getChapterUrl(chapter: SChapter): String = chapter.url

    override suspend fun fetchMangaUpdate(
        manga: SManga,
        chapters: List<SChapter>,
        fetchDetails: Boolean,
        fetchChapters: Boolean,
    ): SMangaUpdate {
        val slug = saradaSlugFromUrl(manga.url)
        val post = slug?.let { requestedSlug ->
            requestPosts(1, requestedSlug).firstOrNull { it.slug == requestedSlug && postLinkMatchesSlug(it, requestedSlug) }
        }
            ?: return SMangaUpdate(manga, chapters)
        val metadata = if (fetchDetails) fetchMetadata(post) else null
        val updated = if (fetchDetails) post.toManga(metadata) else manga
        val updatedChapters = if (fetchChapters) listOf(post.toChapter()) else chapters
        return SMangaUpdate(updated, updatedChapters)
    }

    override suspend fun getPageList(chapter: SChapter): List<Page> {
        val slug = saradaSlugFromUrl(chapter.url.toHttpUrl().encodedPath)
        val mediaPages = slug?.let { requestedSlug ->
            requestPosts(1, requestedSlug).firstOrNull { it.slug == requestedSlug && postLinkMatchesSlug(it, requestedSlug) }
                ?.let { post -> fetchMedia(post.id).filter { it.id != post.featuredMedia && isImageMedia(it) && isAllowedUrl(it.sourceUrl) } }
        }.orEmpty()
        if (mediaPages.isNotEmpty()) {
            return mediaPages.mapIndexed { index, media -> Page(index, imageUrl = media.sourceUrl) }
        }
        val document = client.get(chapter.url, Fetch.DOCUMENT, ensureSuccess = false).use { response ->
            if (!response.isSuccessful) throw HttpException(response.code)
            response.asJsoup()
        }
        return galleryImages(document).mapIndexed { index, url -> Page(index, imageUrl = url) }
    }

    private suspend fun fetchPosts(page: Int, search: String?): MangasPage {
        val response = requestPostsResponse(page, search)
        val totalPages = response.header("X-WP-TotalPages")?.toIntOrNull() ?: page
        val posts = response.parseAs<List<WpPost>>()
        return MangasPage(posts.map { it.toManga() }, page < totalPages)
    }

    private suspend fun requestPosts(page: Int, slug: String?): List<WpPost> = requestPostsResponse(page, null, slug).parseAs()

    private suspend fun requestPostsResponse(page: Int, search: String?, slug: String? = null) = client.get(postsUrl(page, search, slug), Fetch.XHR, ensureSuccess = false).also { response ->
        if (!response.isSuccessful) {
            response.close()
            throw HttpException(response.code)
        }
    }

    private fun postsUrl(page: Int, search: String?, slug: String?): HttpUrl = baseUrl.toHttpUrl().newBuilder()
        .addPathSegments("wp-json/wp/v2/posts")
        .addQueryParameter("per_page", POSTS_PER_PAGE.toString())
        .addQueryParameter("page", page.toString())
        .addQueryParameter("_embed", "1")
        .apply {
            search?.let { addQueryParameter("search", it) }
            slug?.let { addQueryParameter("slug", it) }
        }
        .build()

    private suspend fun fetchMetadata(post: WpPost): SaradaMetadata {
        val terms = post.embedded.terms("post_tag")
        val categories = post.embedded.terms("category")
        val tagNames = terms.ifEmpty { fetchTermNames("tags", post.tags) }
        val categoryNames = categories.ifEmpty { fetchTermNames("categories", post.categories) }
        val cover = post.embedded.featuredMedia.firstOrNull()
            ?: fetchMedia(post.featuredMedia).firstOrNull()
        val gallery = fetchMedia(post.id).filter { it.id != post.featuredMedia && isImageMedia(it) && isAllowedUrl(it.sourceUrl) }
        val document = fetchDocument(post.link)
        val videos = document?.let(::videoUrls).orEmpty()
        val videoUrl = videos.firstOrNull()
        val jsonLdDuration = document?.let(::jsonLdDuration)
        val rangeDuration = if (jsonLdDuration == null && videoUrl != null) readMp4Duration(videoUrl) else null
        val duration = jsonLdDuration ?: rangeDuration
        val explicit = classify(tagNames, categoryNames)
        val author = fetchAuthor(post.link)
        val credits = document?.select(".artist-credit a[href], .artist-credits a[href], .credit a[href], .credits a[href], [data-credit] a[href]")
            ?.mapNotNull { element ->
                val href = element.absUrl("href")
                val label = element.text().trim().replace(Regex("\\s+"), " ")
                val imageLink = IMAGE_EXTENSIONS.any { href.substringBefore('?').lowercase(Locale.ROOT).endsWith(it) }
                if (href.isBlank() || label.isBlank() || label == href || imageLink || isSiteUrl(href.toHttpUrl())) {
                    null
                } else {
                    "${label.take(150)}|$href"
                }
            }
            ?.distinct()
            .orEmpty()
        val ogImage = document?.select("meta[property=og:image], meta[name=og:image]")
            ?.firstOrNull()?.attr("content")
            ?.let { document.baseUri().toHttpUrl().resolve(it)?.toString() }
        return SaradaMetadata(
            post = post,
            cover = cover,
            gallery = gallery,
            author = author,
            ogImage = ogImage,
            videoUrl = videoUrl,
            durationSeconds = duration,
            durationSource = when {
                jsonLdDuration != null -> "jsonld"
                rangeDuration != null -> "mp4_mvhd_range_1mib_max"
                else -> null
            },
            artists = explicit.artists,
            characters = explicit.characters,
            works = explicit.works,
            categories = explicit.categories,
            tags = explicit.tags,
            unclassifiedTags = explicit.unclassifiedTags,
            credits = credits,
        )
    }

    private suspend fun fetchMedia(id: Int): List<WpMedia> {
        if (id <= 0) return emptyList()
        val url = baseUrl.toHttpUrl().newBuilder()
            .addPathSegments("wp-json/wp/v2/media")
            .addQueryParameter("parent", id.toString())
            .addQueryParameter("per_page", "100")
            .build()
        return client.get(url, Fetch.XHR, ensureSuccess = false).use { response ->
            if (!response.isSuccessful) return@use emptyList()
            response.parseAs<List<WpMedia>>()
        }
    }

    private suspend fun fetchTermNames(route: String, ids: List<Int>): List<String> {
        if (ids.isEmpty()) return emptyList()
        val url = baseUrl.toHttpUrl().newBuilder()
            .addPathSegments("wp-json/wp/v2/$route")
            .addQueryParameter("include", ids.joinToString(","))
            .addQueryParameter("per_page", "100")
            .build()
        return client.get(url, Fetch.XHR, ensureSuccess = false).use { response ->
            if (!response.isSuccessful) return@use emptyList()
            response.parseAs<List<NamedTerm>>().map { it.name }
        }
    }

    private suspend fun fetchAuthor(postUrl: String): Oembed? {
        val url = baseUrl.toHttpUrl().newBuilder()
            .addPathSegments("wp-json/oembed/1.0/embed")
            .addQueryParameter("url", postUrl)
            .addQueryParameter("format", "json")
            .build()
        return client.get(url, Fetch.XHR, ensureSuccess = false).use { response ->
            if (!response.isSuccessful) null else response.parseAs<Oembed>()
        }
    }

    private suspend fun fetchDocument(url: String): Document? = client.get(url, Fetch.DOCUMENT, ensureSuccess = false).use { response ->
        if (!response.isSuccessful) null else response.asJsoup()
    }

    private suspend fun readMp4Duration(url: String): Double? {
        val rangeHeaders = headers.newBuilder().set("Range", "bytes=0-1048575").build()
        return client.get(url, rangeHeaders, Fetch.NONE, ensureSuccess = false).use { response ->
            if (!response.isSuccessful) return@use null
            val bytes = response.body.byteStream().use { input ->
                val result = ByteArray(1024 * 1024)
                var offset = 0
                while (offset < result.size) {
                    val read = input.read(result, offset, result.size - offset)
                    if (read <= 0) break
                    offset += read
                }
                result.copyOf(offset)
            }
            mp4Duration(bytes)
        }
    }

    private fun WpPost.toManga(metadata: SaradaMetadata? = null) = SManga.create().apply {
        url = runCatching { link.toHttpUrl().encodedPath }.getOrDefault("/$slug/")
        title = titleText()
        thumbnail_url = metadata?.cover?.sourceUrl ?: embedded.featuredMedia.firstOrNull()?.sourceUrl ?: metadata?.ogImage
        description = metadata?.description() ?: descriptionText()
        author = metadata?.author?.authorName
        artist = metadata?.artists?.joinToString().takeUnless { it.isNullOrBlank() }
        genre = metadata?.let { (it.categories + it.tags).distinct().joinToString() }
        status = SManga.COMPLETED
        initialized = metadata != null
    }

    private fun WpPost.toChapter() = SChapter.create().apply {
        url = link
        name = titleText()
        date_upload = dateMillis()
        chapter_number = 1f
    }

    private fun SaradaMetadata.description(): String? = buildString {
        post.descriptionText()?.let(::appendLine)
        author?.authorName?.let { appendLine("Author: $it") }
        if (artists.isNotEmpty()) appendLine("Artists: ${artists.joinToString()}")
        if (characters.isNotEmpty()) appendLine("Characters: ${characters.joinToString()}")
        if (works.isNotEmpty()) appendLine("Works: ${works.joinToString()}")
        if (categories.isNotEmpty()) appendLine("Categories: ${categories.joinToString()}")
        if (tags.isNotEmpty()) appendLine("Tags: ${tags.joinToString()}")
        if (unclassifiedTags.isNotEmpty()) appendLine("Unclassified tags: ${unclassifiedTags.joinToString()}")
        videoUrl?.let {
            append("Video: $it")
            durationSeconds?.let { seconds -> append(" (${seconds.formatDuration()})") }
            appendLine()
        }
        if (credits.isNotEmpty()) appendLine("Credits: ${credits.joinToString()}")
    }.trim().takeIf { it.isNotEmpty() }

    private fun galleryImages(document: Document): List<String> = document.select("img[src]")
        .mapNotNull { it.absUrl("src").takeIf(::isAllowedUrl) }
        .distinct()

    private fun videoUrls(document: Document): List<String> = (
        document.select("video[src], video source[src]").map { it.absUrl("src") } +
            document.select("meta[property=og:video], meta[property=og:video:url]").map { it.absUrl("content") } +
            VIDEO_REGEX.findAll(document.html()).map { it.value.trimEnd(')', ',', ';', '.') }
        )
        .filter(::isVideoUrl)
        .distinct()

    private fun isVideoUrl(url: String): Boolean = isAllowedUrl(url) &&
        VIDEO_EXTENSIONS.any { url.substringBefore('?').lowercase(Locale.ROOT).endsWith(it) }

    private fun jsonLdDuration(document: Document): Double? = document
        .select("script[type=application/ld+json]")
        .asSequence()
        .mapNotNull { DURATION_REGEX.find(it.data())?.groupValues?.getOrNull(1) }
        .mapNotNull(::parseIsoDuration)
        .firstOrNull()

    private fun classify(tags: List<String>, categories: List<String>): Classification {
        val groups = mapOf(
            "artists" to mutableListOf<String>(),
            "characters" to mutableListOf<String>(),
            "works" to mutableListOf<String>(),
        )
        val classified = mutableSetOf<String>()
        tags.forEach { tag ->
            val explicit = TAG_TYPES[tag]
            val suffix = SUFFIX_REGEX.matchEntire(tag)
            val kind = explicit ?: suffix?.groupValues?.get(2)?.lowercase(Locale.ROOT)
            val value = suffix?.groupValues?.get(1)?.trim() ?: tag
            val group = when (kind) {
                "artist" -> "artists"
                "character" -> "characters"
                "work" -> "works"
                else -> null
            }
            if (group != null) {
                groups.getValue(group).add(value)
                classified.add(tag)
            }
        }
        return Classification(
            groups.getValue("artists").distinct(),
            groups.getValue("characters").distinct(),
            groups.getValue("works").distinct(),
            categories.distinct(),
            tags.distinct(),
            tags.distinct().filterNot(classified::contains),
        )
    }

    private fun isSiteUrl(url: HttpUrl): Boolean = url.host == baseUrl.toHttpUrl().host

    private fun isAllowedUrl(url: String): Boolean = runCatching { isAllowedUrl(url.toHttpUrl()) }.getOrDefault(false)

    private fun isAllowedUrl(url: HttpUrl): Boolean {
        val host = url.host
        val baseHost = baseUrl.toHttpUrl().host
        return host == baseHost || host.endsWith(".$baseHost")
    }

    private data class Classification(
        val artists: List<String>,
        val characters: List<String>,
        val works: List<String>,
        val categories: List<String>,
        val tags: List<String>,
        val unclassifiedTags: List<String>,
    )

    private fun isImageMedia(media: WpMedia): Boolean = media.mimeType.startsWith("image/", ignoreCase = true) ||
        IMAGE_EXTENSIONS.any { media.sourceUrl.substringBefore('?').lowercase(Locale.ROOT).endsWith(it) }

    private fun postLinkMatchesSlug(post: WpPost, requestedSlug: String): Boolean = post.slug == requestedSlug &&
        runCatching {
            val link = post.link.toHttpUrl()
            isSiteUrl(link) && saradaSlugFromUrl(link.encodedPath) == requestedSlug
        }.getOrDefault(false)

    private fun Double.formatDuration(): String {
        val total = toInt()
        return "%02d:%02d".format(Locale.ROOT, total / 60, total % 60)
    }

    private companion object {
        const val POSTS_PER_PAGE = 20
        val VIDEO_EXTENSIONS = listOf(".mp4", ".webm", ".m4v", ".mov", ".m3u8", ".mpd")
        val IMAGE_EXTENSIONS = listOf(".jpg", ".jpeg", ".png", ".gif", ".webp", ".avif", ".svg")
        val TAG_TYPES = emptyMap<String, String>()
        val SUFFIX_REGEX = Regex("(.+?)\\s*\\((artist|character|work)\\)", RegexOption.IGNORE_CASE)
        val VIDEO_REGEX = Regex("https?://[^\\s<>\\\"']+?\\.(?:mp4|webm|m4v|mov|m3u8|mpd)", RegexOption.IGNORE_CASE)
        val DURATION_REGEX = Regex("\\\"duration\\\"\\s*:\\s*\\\"(PT[^\\\"]+)\\\"", RegexOption.IGNORE_CASE)

        fun parseIsoDuration(value: String): Double? {
            val match = Regex("PT(?:(\\d+(?:\\.\\d+)?)H)?(?:(\\d+(?:\\.\\d+)?)M)?(?:(\\d+(?:\\.\\d+)?)S)?").matchEntire(value)
                ?: return null
            val (hours, minutes, seconds) = match.destructured
            return (hours.toDoubleOrNull() ?: 0.0) * 3600 +
                (minutes.toDoubleOrNull() ?: 0.0) * 60 +
                (seconds.toDoubleOrNull() ?: 0.0)
        }

        fun mp4Duration(data: ByteArray): Double? {
            val marker = "mvhd".encodeToByteArray()
            val index = data.indexOfSubarray(marker)
            if (index < 0 || index + 24 > data.size) return null
            val version = data[index + 4].toInt()
            val timescaleOffset = if (version == 0) index + 16 else index + 24
            val durationOffset = if (version == 0) index + 20 else index + 28
            if (durationOffset + (if (version == 0) 4 else 8) > data.size) return null
            val timescale = data.readUInt(timescaleOffset)
            val duration = if (version == 0) data.readUInt(durationOffset).toDouble() else data.readULong(durationOffset).toDouble()
            if (timescale <= 0) return null
            return duration / timescale.toDouble()
        }

        fun ByteArray.indexOfSubarray(needle: ByteArray): Int = (0..size - needle.size).firstOrNull { offset ->
            needle.indices.all { this[offset + it] == needle[it] }
        } ?: -1

        fun ByteArray.readUInt(offset: Int): Long = sliceArray(offset until offset + 4).fold(0L) { result, byte ->
            (result shl 8) or (byte.toLong() and 0xff)
        }

        fun ByteArray.readULong(offset: Int): Long = sliceArray(offset until offset + 8).fold(0L) { result, byte ->
            (result shl 8) or (byte.toLong() and 0xff)
        }
    }
}
