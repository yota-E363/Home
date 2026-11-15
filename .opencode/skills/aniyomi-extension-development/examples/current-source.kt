package eu.kanade.tachiyomi.extension.en.example

import eu.kanade.tachiyomi.source.model.FilterList
import eu.kanade.tachiyomi.source.model.MangasPage
import keiyoushi.annotation.Source
import keiyoushi.network.Fetch
import keiyoushi.network.get
import keiyoushi.source.KeiSource
import keiyoushi.utils.parseAs
import okhttp3.HttpUrl.Companion.toHttpUrl
import okhttp3.OkHttpClient
import kotlinx.serialization.Serializable

@Source
abstract class Example : KeiSource() {
    override fun OkHttpClient.Builder.configureClient() = this

    override suspend fun getPopularManga(page: Int): MangasPage = fetchPosts(page, null)

    override suspend fun getLatestUpdates(page: Int): MangasPage = fetchPosts(page, null)

    override suspend fun getSearchMangaList(page: Int, query: String, filters: FilterList): MangasPage =
        fetchPosts(page, query.trim().takeIf { it.isNotEmpty() })

    private suspend fun fetchPosts(page: Int, query: String?): MangasPage {
        val url = baseUrl.toHttpUrl().newBuilder()
            .addPathSegments("api/posts")
            .addQueryParameter("page", page.toString())
            .apply { query?.let { addQueryParameter("search", it) } }
            .build()
        val response = client.get(url, Fetch.XHR, ensureSuccess = false)
        val result = response.use {
            if (!it.isSuccessful) throw IllegalStateException("HTTP ${it.code}")
            it.parseAs<PostPage>()
        }
        return MangasPage(result.posts.map { it.toManga() }, result.hasNext)
    }

    private fun Post.toManga() = eu.kanade.tachiyomi.source.model.SManga.create().apply {
        url = link.removePrefix(baseUrl)
        title = title.rendered
        thumbnail_url = coverUrl
    }
}

@Serializable
class PostPage(val posts: List<Post>, val hasNext: Boolean)

@Serializable
class Post(
    val slug: String,
    val link: String,
    val title: Rendered,
    val coverUrl: String,
)

@Serializable
class Rendered(val rendered: String)
