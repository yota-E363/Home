# Hentai.Pro — APK catalogue-only

## Livraison

- APK : `artifacts/HentaiPro-v16.1-catalogue.apk`
- SHA-256 : `b71de6722c355c4487d72890b028631e17c34bcf846737ed2fd71ce6dd1751e3`
- NSFW : activé via `ContentWarning.NSFW` dans la configuration `libVersion 16`
- Package : `eu.kanade.tachiyomi.animeextension.en.hentaipro`

## Tests réels

- Populaire : PASS, 24 entrées
- Derniers épisodes : PASS, 24 entrées
- Recherche `sister` : PASS, résultat `Sister Breeder Episode 5` présent
- Détail : PASS, titre, tags/description et iframe détectés
- Épisodes : PASS, épisode de test numéro 5 détecté
- Vidéo : NON DISPONIBLE, iframe `nhplayer.com` protégé par vérification anti-robot

## Architecture vidéo

- `VideoProvider` : contrat de découverte et de résolution
- `VideoProviderRegistry` : sélection des fournisseurs et journalisation des erreurs
- `NhPlayerProvider` : détecte l’iframe public puis s’arrête proprement à la protection anti-bot
- `OfficialVideoApiProvider` : interface prête pour un endpoint authentifié du propriétaire
- Sous-titres : support prévu via `Video.subtitleTracks` et `Track` dans le contrat d’intégration
- Contrat détaillé : `VIDEO_PROVIDER_CONTRACT.md`

Preuve détaillée : `catalog-tests.json`.

## Limite connue

Cette version est volontairement catalogue-only. Elle ne contourne pas l’anti-bot, les jetons signés ou les protections du lecteur et ne déclare donc pas la lecture vidéo opérationnelle.

## Sécurité

Les contrôles publics ont confirmé les observations du rapport initial : en-têtes contradictoires, absence de HSTS observée, CSP avec `unsafe-inline`, allowlist iframe large et cookie de session du lecteur sans attributs `Secure`, `HttpOnly` ou `SameSite` visibles. Détails et corrections : `SECURITY_AUDIT_INITIAL.md`. Résultats bruts : `security-checks.json`.
