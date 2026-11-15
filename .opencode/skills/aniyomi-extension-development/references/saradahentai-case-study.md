# SaradaHentai case study

SaradaHentai is a required regression lesson for this skill. It exposed a class of bugs that look like UI or cache problems but originate in source identity.

## Failure

The catalogue stored a URL ending in `/slug/`. Detail refresh extracted the slug with `substringAfterLast('/')`, got an empty string, omitted the WordPress `slug` query parameter, and accepted the first post returned by the API. A different publication then replaced the title, cover, tags, and author.

## Corrective pattern

- normalize the source URL before extracting its key;
- query the exact slug/ID;
- verify the response identity;
- derive all child requests from the verified post;
- keep request state local and keyed, never global;
- regression-test two distinct posts and a trailing slash.

## Metadata lessons

- WordPress author and artist credits are different fields;
- categories and raw tags must remain separate;
- explicit suffix/rule classification is safer than guessing;
- `unclassified_tags` is useful evidence, not a failure;
- cover and gallery media are different roles;
- external links are not automatically credits;
- image/CDN URLs and blank anchors must not become credits;
- video URL/duration must be tied to the same post.

## Validation lessons

The SaradaHentai APK was compiled and linted, and local fixtures passed. That proves the module and fixture paths, not live access. Cloudflare HTTP 403 remained a live-validation limitation. This distinction must appear in future reports.

## Independent audit additions

An independent audit supplied an additional contract check and identified four hardening points:

- exact slug matching must also require that the official permalink's final path segment matches the requested slug;
- derive the stored manga URL from the parsed permalink path, not textually removing `baseUrl`;
- skip detailed metadata requests when `fetchDetails` is false;
- restrict gallery pages to image media on the source domain/subdomains and exclude the featured cover;
- use explicit credit containers such as `.artist-credit`, `.artist-credits`, `.credit`, `.credits`, or `[data-credit]`, not broad substring selectors that can include advertising/partner blocks.

The independent audit itself was not treated as proof of compilation: its sandbox had no Java, Android SDK, or Kotlin compiler. Its static `test_kotlin_contract.py` checks were recovered and added to the SaradaHentai local regression suite.
