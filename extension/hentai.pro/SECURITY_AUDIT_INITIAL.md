# Audit de sécurité initial — Hentai.Pro

Périmètre : contrôles publics, non destructifs et à faible volume. Aucun contournement d’anti-bot, aucune tentative d’accès à des comptes tiers et aucune extraction de jeton privé.

## Observations vérifiées le 2026-11-12

### SEC-001 — En-têtes HTTP contradictoires

- **Sévérité : moyenne à confirmer**
- Les réponses publiques renvoient deux valeurs `X-Frame-Options` (`DENY` et `SAMEORIGIN`) et deux valeurs `Referrer-Policy` (`no-referrer` et `same-origin`).
- Selon le navigateur et la chaîne de proxies, le comportement retenu peut être ambigu.
- **Recommandation :** ne conserver qu’une valeur explicite par en-tête, idéalement `X-Frame-Options: DENY` pour les pages principales et une politique de référent choisie selon le besoin du lecteur.

### SEC-002 — HSTS non observé

- **Sévérité : faible à moyenne**
- `Strict-Transport-Security` n’a pas été observé sur les réponses testées.
- **Recommandation :** activer HSTS après vérification de tous les sous-domaines HTTPS, par exemple avec `includeSubDomains` et une durée progressive.

### SEC-003 — CSP permissive sur les scripts

- **Sévérité : moyenne à confirmer**
- La CSP autorise `script-src 'unsafe-inline'` et `style-src 'unsafe-inline'`.
- **Recommandation :** migrer vers des nonces ou hashes pour les scripts inline et réduire progressivement les exceptions.

### SEC-004 — Surface iframe vidéo large

- **Sévérité : faible à moyenne à confirmer**
- `frame-src` autorise plusieurs domaines de lecteurs et de publicité.
- **Recommandation :** limiter la liste aux domaines réellement nécessaires, utiliser une allowlist maintenue et vérifier les politiques de chaque lecteur tiers.

### SEC-005 — Cookie de session du lecteur sans attributs visibles

- **Sévérité : à confirmer**
- Le lecteur renvoie un cookie `PHPSESSID` sans attributs `Secure`, `HttpOnly` ou `SameSite` visibles dans la réponse observée.
- **Recommandation :** définir explicitement `Secure; HttpOnly; SameSite=Lax` ou `Strict` selon les flux iframe nécessaires. Vérifier le comportement cross-site avant de choisir `None`.

## Contrôles positifs

- HTTPS actif avec Cloudflare.
- `object-src 'none'`, `base-uri 'none'`, `form-action 'self'` et `frame-ancestors 'none'` présents dans la CSP.
- Permissions caméra, microphone, géolocalisation et paiement désactivées.
- Aucun accès privé n’a été tenté.

## Limites

Les contrôles d’autorisation du lecteur, l’expiration des URLs signées et les contrôles serveur de contenu nécessitent des données de test administratives. Ils ne doivent pas être validés en contournant les protections de production.
