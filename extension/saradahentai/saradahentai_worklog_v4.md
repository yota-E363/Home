# Fiche de travail — SaradaHentai / extension Mihon-Aniyomi
Version : 15 novembre 2026

## Objectif
Préparer un catalogue fiable des publications autonomes : métadonnées, auteur public, classification, couverture, galerie et vidéo principale.

## Résultats déjà obtenus

### Cartographie / WordPress
- V1 : 378 URL de sitemap, 45 pages HTML et 90 références média.
- V2 : 400 publications, 6 pages, 351 pièces jointes, 100 pages HTML ; export JSON d'environ 3,6 Mo.
- Un test de recherche a retourné 300 résultats sur 3 pages alors que l'interface annonçait 42 pages : la pagination complète doit être parcourue et vérifiée.
- API REST des publications et médias exploitable lors des tests précédents.

### Échantillon de 8 publications
- 8/8 : titre, date, catégories, tags, média mis en avant et couverture embarquée.
- 8/8 : image OG cohérente avec la couverture et tags SEO disponibles.
- Les descriptions SEO ne sont pas des synopsis fiables.
- L'extrait éditorial était vide dans l'échantillon initial ; le texte rendu HTML était parfois présent sans texte visible exploitable.
- Auteur WordPress ID 1 sur les huit fiches.

### Auteur public
- API users : HTTP 401 ; sitemap utilisateurs : HTTP 404 ; archive via paramètre author numérique : HTTP 500.
- Archive auteur : HTTP 200 une fois, puis HTTP 403 lors d'une répétition.
- oEmbed : 8/8 réponses HTTP 200 avec nom public admin et URL publique d'archive auteur.
- Nom et URL publics via oEmbed retenus ; bio/avatar non validés.

### Couverture / galerie
- API media par identifiant exploitable ; métadonnées disponibles : alt, caption, description, MIME, dimensions, tailles et URL source.
- Sur trois publications, la recherche des médias enfants a renvoyé 2, 1 et 1 pièces jointes.
- Séparer couverture et galerie ; galerie longue encore à tester.

### Vidéos
- Six vidéos vérifiées par lecture partielle des métadonnées MP4, sans téléchargement complet : 42,475 s ; 180,267 s ; 123,200 s ; 193,814 s ; 366,571 s ; 256,560 s.
- Deux durées JSON-LD concordaient avec les durées MP4 à l'arrondi près.
- Exemple Himeno : URL MP4 principale, taille antérieurement annoncée ~35,8 Mio ; le CDN a répondu 403 à une requête Range lors d'un test ultérieur.
- L'utilisateur confirme une seule qualité vidéo publiée par contenu : aucune recherche de variantes multi-résolution à poursuivre.

### Artistes et tags
- Tags et liens externes d'artistes observés sur trois fiches.
- Ne pas confondre artistes/crédits et auteur WordPress.
- Les tags peuvent mélanger artistes, personnages, œuvres et autres termes ; classification prudente obligatoire.

## Décisions confirmées
1. Chaque publication est autonome : pas de séries, saisons ou relations d'épisodes.
2. Une vidéo principale par publication ; une seule qualité publiée.
3. Conserver tous les tags WordPress bruts.
4. En plus, séparer artists, characters, works et categories.
5. Ne classer que sur preuve ou règle explicite validée. Sinon, garder le terme dans tags et unclassified_tags.
6. Distinguer cover et gallery.
7. Distinguer auteur WordPress et crédits artistiques.
8. Ne jamais présenter une description SEO comme synopsis sans preuve.

## Schéma V4
metadata : id, titre, slug, URL, dates, extrait éditorial vérifié.
author : ID WordPress, nom et URL publics oEmbed.
classification : artists[], characters[], works[], categories[], tags[], unclassified_tags[].
media : cover, gallery[], video (URL principale, durée si disponible, MIME/taille si vérifiés).
credits : liens externes explicitement trouvés sur la fiche.
extraction : date, sources, avertissements et erreurs.

## État des validations
| Élément | État |
|---|---|
| REST / pagination | exploitable ; exhaustivité à revalider |
| Couverture | validée sur échantillon |
| Galerie courte | partiellement validée |
| Galerie longue | à tester |
| URL vidéo principale | validée sur plusieurs exemples |
| Durée vidéo | validée sur 6 fichiers |
| Auteur public oEmbed | 8/8 |
| Bio/avatar auteur | non validés |
| Synopsis | non validé |
| Classification fine | règles explicites / validation humaine nécessaires |
| Séries et qualités multiples | sans objet, confirmé par l'utilisateur |

## Sécurité et méthode
Requêtes publiques en lecture seule, faible débit, domaine autorisé uniquement. Respecter 401/403/404/429/5xx ; ne pas contourner les protections. Ne jamais télécharger une vidéo complète. Distinguer absent, non observé et inaccessible.

## Livrables
- saradahentai_worklog_v4.md
- saradahentai_catalogue_v4.py
- saradahentai_v4_classification_rules.example.json
- saradahentai_v4_bundle.zip
