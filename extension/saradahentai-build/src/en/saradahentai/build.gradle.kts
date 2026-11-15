import io.github.keiyoushi.gradle.api.ContentWarning

plugins {
    alias(kei.plugins.extension)
}

keiyoushi {
    name = "SaradaHentai"
    versionCode = 1
    contentWarning = ContentWarning.NSFW
    libVersion = "1.6"

    source {
        name = "SaradaHentai"
        baseUrl = "https://saradahentai.com"
        lang = "en"
    }

    deeplink {
        path("/..*")
    }
}
