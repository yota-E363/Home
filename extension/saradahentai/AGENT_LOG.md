# Journal de l'agent — Saradahentai

## Phase 1 — Préparation

- URL reçue : `https://saradahentai.com/`
- Dossier de travail : `/workspaces/Home/extension/saradahentai`
- Python détecté : `Python 3.14.2`
- Java détecté : `OpenJDK 25.0.4.1 LTS`
- Git détecté : `2.55.0`
- Espace libre initial constaté : `1.7G`
- Le site a répondu `HTTP 403` avec `cf-mitigated: challenge` lors d'une requête HEAD avec User-Agent normal. Aucun contournement effectué.
- Builder cloné : `/workspaces/Home/mihon-ext-builder`
- Dépôt de référence non cloné à ce stade, en raison de l'espace disque limité et de la dépendance manquante du Builder.

## Erreur — Builder CLI

Commande exécutée :
```text
python3 /workspaces/Home/mihon-ext-builder/main.py --help
python3 /workspaces/Home/mihon-ext-builder/main.py analyze --help
python3 /workspaces/Home/mihon-ext-builder/main.py scaffold --help
python3 /workspaces/Home/mihon-ext-builder/main.py check --help
```

Message exact :
```text
Traceback (most recent call last):
  File "/workspaces/Home/mihon-ext-builder/main.py", line 13, in <module>
    import click
ModuleNotFoundError: No module named 'click'
```

Hypothèse avant correction : la dépendance Python `click` (et potentiellement les autres dépendances déclarées par le Builder) n'est pas installée dans l'environnement courant.

Action suivante bloquée : demander l'autorisation d'installer les dépendances du Builder dans un environnement virtuel isolé.

## Erreur — Checkout du dépôt de référence

Commande exécutée :
```text
git clone --depth=1 --filter=blob:none --no-checkout https://github.com/keiyoushi/extensions-source /workspaces/Home/extensions-source
git -C /workspaces/Home/extensions-source sparse-checkout set CONTRIBUTING.md
git -C /workspaces/Home/extensions-source checkout --depth=1 HEAD
```

Message exact :
```text
error: unknown option `depth=1'
usage: git checkout [<options>] [<branch>]
```

Hypothèse avant correction : l'option `--depth` a été appliquée à `git checkout`, alors qu'elle s'applique au clonage/fetch. Le clone filtré a néanmoins créé le dépôt partiel.

Correction prévue : configurer le sparse-checkout puis exécuter `git checkout HEAD` sans `--depth`.

## Phase 2 — Faisabilité

Commande Builder :
```text
.venv/bin/python main.py analyze https://saradahentai.com/ --json
```

Résultat sauvegardé dans `analyze.json` :
- type : `unknown`
- health : `cloudflare_blocked`
- HTTP : `403`
- cloudflare : `true`
- template proposé : `http_source`
- CMS : non identifié
- `covered_by` : vide

Test Chrome DevTools MCP réel :
- navigation vers `https://saradahentai.com/` : page `Just a moment...`
- titre : `Performing security verification`
- iframe : `Widget containing a Cloudflare security challenge`
- réponse document : `403`
- présence de Cloudflare Turnstile confirmée

Verdict : **NO-GO**.

Motif : le site exige une vérification anti-bot Cloudflare/Turnstile avant de fournir le contenu. La procédure interdit tout contournement. Les fonctions Mihon (listes, recherche, détails, chapitres et pages) sont donc non testables et non implémentables de façon fiable depuis cet environnement.

## Nouvelle demande — analyse des quatre fichiers V4

Les quatre fichiers ont été lus individuellement, sans ouvrir le ZIP :
- `saradahentai_catalogue_v4.py`
- `saradahentai_worklog_v4.md`
- `README_V4.txt`
- `saradahentai_v4_classification_rules.example.json`

Références retenues :
- WordPress REST `wp-json/wp/v2/posts`, médias enfants et taxonomies.
- oEmbed public pour le nom/URL publics de l'auteur.
- HTML public pour OG/meta, galerie, liens externes et vidéos visibles.
- Durée : JSON-LD, sinon lecture partielle maximale de 1 MiB du header MP4.
- Classification explicite uniquement ; tags bruts et `unclassified_tags` conservés.
- Publications autonomes, pas de séries/épisodes ni de variantes vidéo inventées.
- Respect strict des 401/403/404/429/5xx, sans contournement ni téléchargement complet.

Tests actuels des endpoints documentés :
```text
curl -A 'SaradaHentaiCatalogue/4.0 (public read-only metadata)' \
  'https://saradahentai.com/wp-json/wp/v2/posts?per_page=1&_embed=1'
```
Résultat : `HTTP/2 403`, `cf-mitigated: challenge`, contenu `Just a moment...`.

```text
curl -A 'SaradaHentaiCatalogue/4.0 (public read-only metadata)' \
  'https://saradahentai.com/wp-json/oembed/1.0/embed?url=https%3A%2F%2Fsaradahentai.com%2F&format=json'
```
Résultat : `HTTP/2 403`, `cf-mitigated: challenge`, contenu `Just a moment...`.

Verdict maintenu : **NO-GO actuel**. Les fichiers V4 décrivent un accès antérieur, mais les endpoints essentiels ne sont pas actuellement accessibles depuis l'environnement. Aucun code d'extension n'a été généré.

## Erreur — compilation Gradle, tentative 1

Commande :
```text
./gradlew :src:en:saradahentai:assembleDebug --stacktrace
```

Message exact :
```text
SDK location not found. Define a valid SDK location with an ANDROID_HOME environment variable or by setting the sdk.dir path in your project's local properties file at '/workspaces/Home/extension/saradahentai-build/local.properties'.
```

Hypothèse avant correction : le SDK Android existe peut-être dans le workspace mais n'est pas référencé par ce worktree Gradle.

## Erreur — compilation Gradle, tentative 2

Commande :
```text
./gradlew :src:en:saradahentai:assembleDebug --stacktrace
```

Message exact :
```text
Failed to install the following Android SDK packages as some licences have not been accepted.
build-tools;36.0.0 Android SDK Build-Tools 36
platforms;android-37.0 Android SDK Platform 37.0
```

Hypothèse avant correction : les composants sont présents ou téléchargeables dans le SDK local, mais leurs licences n'ont pas été acceptées.

## Audit des ressources V4 — 15 novembre 2026

### Ressources effectivement exploitées

- `saradahentai_catalogue_v4.py` : transposition native des routes REST posts/pages, `_embed`, recherche, pagination, taxonomies, média mis en avant, médias enfants, oEmbed, lecture HTML, vidéos `video/source`, URLs vidéo dans le HTML, JSON-LD `duration`, lecture MP4 bornée à 1 MiB via Range, classification explicite/suffixe, crédits externes et gestion domaine/erreurs HTTP.
- `saradahentai_worklog_v4.md` : intégration des décisions vérifiées (publication autonome, chapitre unique, une vidéo principale, couverture séparée de la galerie, distinction auteur WordPress/crédits artistiques, absence de synopsis SEO fiable et prudence de classification). Les valeurs historiques de durée servent de référence de test, pas de données inventées dans l'extension.
- `README_V4.txt` : respect des limites de taille, du débit, du mode lecture seule, de l'absence de contournement Cloudflare et de l'absence de téléchargement vidéo complet.
- `saradahentai_v4_classification_rules.example.json` : le fichier fourni ne contient aucune correspondance (`tag_types` vide). L'extension conserve donc les tags bruts et applique seulement les suffixes `(Artist)`, `(Character)` et `(Work)` ; aucune correspondance non fournie n'a été ajoutée.
- `analyze.json` et les fichiers du dossier : `cloudflare_blocked`/HTTP 403 est traité comme indisponibilité HTTP normale. La recommandation historique d'intercepteur Cloudflare n'a pas été suivie car elle entrerait en conflit avec la consigne de ne pas contourner l'anti-bot.

### Éléments volontairement non intégrés

- Bio/avatar et API utilisateurs : le worklog les donne comme non validés ; seuls les champs publics oEmbed nom/URL sont utilisés.
- Séries, épisodes, saisons et variantes de qualité : explicitement sans objet selon le worklog.
- Options CLI du script (`--no-gallery`, `--no-oembed`, délais configurables) : elles sont des options d'exécution Python, pas des fonctionnalités utilisateur pertinentes pour une source Mihon ; le débit est limité dans le client et les appels gallery/oEmbed sont intégrés au chargement des détails.
- Le ZIP mentionné par le worklog n'a pas été ouvert, conformément à la décision d'audit précédente ; les quatre fichiers demandés et `analyze.json` ont été lus directement.

### Tests locaux ajoutés

Fixtures ajoutées dans `fixtures/` : post WordPress embarqué, médias enfants, oEmbed et page HTML avec OG image, OG vidéo, source vidéo, crédit externe et JSON-LD.

Commande :
```text
python3 -m unittest -v test_fixtures.py
```

Résultat : `Ran 3 tests ... OK`.

Ces tests valident les comportements de référence V4 (classification, extraction HTML/durée et en-tête MP4). Ils ne remplacent pas une compilation Kotlin ni une validation réseau live.

### Écarts corrigés pendant l'audit

- ajout des champs WordPress `modified` et `author`, ainsi que des métadonnées média caption/description/sizes ;
- ajout des vidéos OG et filtrage par extensions V4 ;
- ajout du fallback `og:image` pour la couverture ;
- conservation du libellé et de l'URL des crédits externes ;
- utilisation prioritaire des médias enfants WordPress comme pages de lecture, avec fallback HTML ;
- normalisation du slug avec slash final pour les liens profonds.

### Vérification restant à faire

- compilation `assembleDebug` et `lintRelease` : bloquées avant compilation Kotlin par les licences SDK non acceptées (`build-tools;36.0.0`, `platforms;android-37.0`) ; aucun APK n'est donc revendiqué ;
- tests live REST/oEmbed/media/HTML/Range : actuellement bloqués par Cloudflare HTTP 403 challenge ;
- validation de l'intégration Kotlin elle-même : les fixtures Python sont vertes, mais ne constituent pas une preuve de compilation ou d'exécution Android.

## Validation technique finale — 15 novembre 2026

### SDK Android

Les Command-line Tools Linux 19.0 ont été installés dans :
`/workspaces/Home/extension/android-sdk/cmdline-tools/latest`.

Commande exécutée :
```text
yes | /workspaces/Home/extension/android-sdk/cmdline-tools/latest/bin/sdkmanager --sdk_root=/workspaces/Home/extension/android-sdk --licenses
```

Résultat : `All SDK package licenses accepted`.

### Compilation

Première compilation après acceptation des licences : échec Kotlin unique :
```text
Saradahentai.kt:232:56 Return type mismatch: expected 'String', actual 'String?'.
```

Correction : `SaradaMetadata.description()` retourne désormais `String?`.

Commande finale :
```text
./gradlew :src:en:saradahentai:assembleDebug :src:en:saradahentai:lintRelease
```

Résultat : `BUILD SUCCESSFUL`.

### Tests locaux finaux

Commande :
```text
cd /workspaces/Home/extension/saradahentai
python3 -m unittest -v test_fixtures.py
```

Résultat : `Ran 5 tests ... OK`.

Les cinq tests couvrent le post/catalogue, la classification, le détail, les médias/galeries, l'oEmbed, l'HTML vidéo/OG/JSON-LD, la durée MP4 bornée et le traitement HTTP 403 sans contournement.

### Artefact et format

APK généré :
`/workspaces/Home/extension/saradahentai-build/src/en/saradahentai/build/outputs/apk/debug/tachiyomi-en.saradahentai-v1.6.1.apk`

SHA-256 : `79e0e0aca3cacbbb8a7bd737376b0f8e3a45ae67a83521e7cf8d64b8642ffa09`.

Vérification manifeste : package `eu.kanade.tachiyomi.extension.en.saradahentai`, feature `tachiyomi.extension`, classe générée `keiyoushi.source.Generated`, lib `1.6`, avertissement NSFW et deep link `saradahentai.com`. L'artefact est donc une extension Mihon/Aniyomi générée par le builder, pas une APK Android générique.

Les validations live restent explicitement non effectuées à cause du challenge Cloudflare HTTP 403.

## Régression d'identité catalogue/fiche — correction

Symptôme reproduit : une fiche ouverte depuis une URL se terminant par `/` était ensuite remplacée par le premier post REST de la page 1.

Cause exacte : `fetchMangaUpdate()` utilisait `manga.url.substringAfterLast('/')`. Pour une URL de catalogue `/slug/`, cette expression renvoyait une chaîne vide. Le paramètre REST `slug` était donc absent, et la réponse WordPress n'était plus liée à la publication demandée.

Correction dans `Saradahentai.kt` et `Dto.kt` :

- ajout de `saradaSlugFromUrl`, qui retire query, fragment et slash final ;
- recherche par slug normalisé dans `getMangaByUrl`, `fetchMangaUpdate` et `getPageList` ;
- refus d'utiliser une réponse REST dont `post.slug` ne correspond pas au slug demandé ;
- toutes les métadonnées, médias enfants, oEmbed, HTML et durée sont ensuite dérivés du même `WpPost.id`.

Les crédits ne prennent plus tous les liens externes de la page. Ils sont limités aux ancres placées dans des conteneurs explicitement identifiables `credit`/`artist`, avec libellé non vide, URL non-image et URL externe. Les tags non classifiés restent dans `unclassifiedTags`.

Tests de non-régression :
```text
python3 -m unittest -v test_fixtures.py
Ran 6 tests ... OK
```

Compilation après correction :
```text
./gradlew :src:en:saradahentai:assembleDebug :src:en:saradahentai:lintRelease
BUILD SUCCESSFUL
```

## Référence audit indépendant reçue ultérieurement

L'archive `saradahentai-independent-audit` a apporté des vérifications supplémentaires. Elle a été examinée sans être considérée comme une preuve de compilation, car son environnement ne possédait ni Java, ni SDK Android, ni compilateur Kotlin.

Éléments récupérés et intégrés :

- le permalink officiel doit être cohérent avec le slug WordPress, pas seulement le champ `slug` ;
- l'URL locale de `SManga` est dérivée du chemin parsé du permalink, et non d'une suppression textuelle de `baseUrl` ;
- `fetchMetadata` n'est appelé que lorsque `fetchDetails` est demandé ;
- la galerie exclut la couverture, les médias non-image et les URLs hors domaine autorisé ;
- les crédits utilisent uniquement des conteneurs explicites (`.artist-credit`, `.artist-credits`, `.credit`, `.credits`, `[data-credit]`) ;
- le test de contrat statique Kotlin de l'audit a été adapté dans `test_kotlin_contract.py`.

Après intégration :
```text
python3 -m unittest -v test_fixtures.py test_kotlin_contract.py
Ran 13 tests ... OK

./gradlew :src:en:saradahentai:assembleDebug :src:en:saradahentai:lintRelease
BUILD SUCCESSFUL
```
