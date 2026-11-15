package eu.kanade.tachiyomi.extension.en.saradahentai

import keiyoushi.utils.tryParse
import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable
import org.jsoup.Jsoup
import org.jsoup.parser.Parser
import kotlin.time.Instant

@Serializable
class WpPost(
    val id: Int,
    val date: String = "",
    val modified: String = "",
    val author: Int = 0,
    val link: String = "",
    val slug: String = "",
    val title: Rendered = Rendered(),
    val excerpt: Rendered = Rendered(),
    val content: Rendered = Rendered(),
    @SerialName("featured_media") val featuredMedia: Int = 0,
    val categories: List<Int> = emptyList(),
    val tags: List<Int> = emptyList(),
    @SerialName("_embedded") val embedded: Embedded = Embedded(),
)

@Serializable
class Rendered(val rendered: String = "")

@Serializable
class Embedded(
    @SerialName("wp:term") val terms: List<List<Term>> = emptyList(),
    @SerialName("wp:featuredmedia") val featuredMedia: List<WpMedia> = emptyList(),
) {
    fun terms(taxonomy: String): List<String> = terms.flatten()
        .filter { it.taxonomy == taxonomy }
        .map { it.name }
}

@Serializable
class Term(
    val taxonomy: String = "",
    val name: String = "",
)

@Serializable
class NamedTerm(
    val name: String = "",
)

@Serializable
class WpMedia(
    val id: Int = 0,
    @SerialName("source_url") val sourceUrl: String = "",
    @SerialName("alt_text") val altText: String = "",
    @SerialName("mime_type") val mimeType: String = "",
    val caption: Rendered = Rendered(),
    val description: Rendered = Rendered(),
    @SerialName("media_details") val mediaDetails: MediaDetails = MediaDetails(),
)

@Serializable
class MediaDetails(
    val width: Int? = null,
    val height: Int? = null,
    val sizes: Map<String, MediaSize> = emptyMap(),
)

@Serializable
class MediaSize(
    @SerialName("source_url") val sourceUrl: String = "",
)

@Serializable
class Oembed(
    @SerialName("author_name") val authorName: String? = null,
    @SerialName("author_url") val authorUrl: String? = null,
)

data class SaradaMetadata(
    val post: WpPost,
    val cover: WpMedia?,
    val gallery: List<WpMedia>,
    val author: Oembed?,
    val ogImage: String?,
    val videoUrl: String?,
    val durationSeconds: Double?,
    val durationSource: String?,
    val artists: List<String>,
    val characters: List<String>,
    val works: List<String>,
    val categories: List<String>,
    val tags: List<String>,
    val unclassifiedTags: List<String>,
    val credits: List<String>,
)

fun WpPost.titleText(): String = Parser.unescapeEntities(title.rendered, false)

fun WpPost.descriptionText(): String? = listOf(
    excerpt.rendered,
    content.rendered,
).map { Jsoup.parse(it).text() }
    .firstOrNull { it.isNotBlank() }

fun WpPost.dateMillis(): Long = Instant.tryParse(date)

fun saradaSlugFromUrl(value: String): String? = value
    .substringBefore('?')
    .substringBefore('#')
    .trimEnd('/')
    .substringAfterLast('/')
    .takeIf { it.isNotBlank() }
