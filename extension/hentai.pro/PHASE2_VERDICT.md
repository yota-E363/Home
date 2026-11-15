# Phase 2 — Hentai.Pro

## Verdict

**GO PARTIEL, bloqué pour la validation vidéo et la livraison fonctionnelle.**

## Site

- URL : `https://hentai.pro/`
- Type : catalogue public d’anime hentai
- Langue détectée : anglais, avec des tags indiquant notamment du contenu sous-titré
- NSFW : oui, l’extension devra être déclarée NSFW
- Accès au catalogue : public, sans connexion observée

## Fonctions publiques observées

- Accueil et catalogue : accessibles
- Séries/tags : `/series/<slug>` et `/tags`
- Derniers épisodes : liens `/watch/<slug>-episode-<n>` présents sur l’accueil
- Détail d’un épisode : titre, tags, description et liens d’exploration accessibles
- Recherche : interface disponible dans l’application web, endpoint exact à confirmer depuis le bundle Next.js

## Lecteur vidéo

- Le détail d’un épisode contient un iframe vers `nhplayer.com`.
- L’iframe affiche une vérification « not a robot » avant la lecture.
- Le clic sur le lecteur produit des erreurs console et laisse le lecteur à `0 seconds of 0 seconds` dans l’environnement de test.
- L’URL média publique observée dans la page du lecteur répond `403 Forbidden` depuis l’environnement de test.
- Aucun fichier vidéo ou playlist `.m3u8` valide n’a donc été vérifié avec HTTP 200.

## Limite appliquée

La vérification anti-robot, les jetons signés et les protections du lecteur ne seront pas contournés. Une extension ne sera pas livrée comme opérationnelle tant qu’une URL vidéo publique et lisible, ou un environnement de test autorisé, ne permettra pas de prouver la fonction vidéo.

## Références

- Aucune extension `Hentai.Pro` trouvée dans `aniyomiorg/aniyomi-extensions`.
- Aucune extension `Hentai.Pro` trouvée dans `yuzono/anime-extensions`.
- Référence de structure et de bibliothèque consultée dans `yuzono/anime-extensions` : `libVersion = "16"`.
