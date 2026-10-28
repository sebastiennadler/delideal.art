# delideal.art — site des poèmes de Delideal

Ce README est la **source de vérité** des choix du site. Si une nouvelle instruction le contredit, on met le README à jour d'abord, puis le code.

## Le site en bref
- Adresse : https://delideal.art (domaine OVH, zone DNS → GitHub Pages ; CNAME `www` → sebastiennadler.github.io)
- Hébergement : GitHub Pages, dépôt `sebastiennadler/delideal.art`, branche `main`, racine `/`
- Type : site statique (HTML, CSS, un seul script pour le thème), sans base de données
- Langue : français uniquement pour commencer
- Thèmes : clair (défaut) et sombre, bouton sur chaque page, mémorisé (`delideal-theme`), appliqué avant le rendu

## Principes éditoriaux
1. **Texte brut** : aucune illustration, aucune image, aucune transition générée par IA.
2. Les poèmes sont reproduits **à l'identique** ; jamais réécrits, jamais corrigés sans accord explicite de l'auteur.
3. Les textes sont **écrits depuis l'an 2000** et **publiés entre 2014 et 2023** sur poeme-france.com : ne jamais écrire « écrits entre 2014 et 2023 ».
3 bis. Les pages de poèmes ne portent **aucune mention de date ni de source** (le lecteur ne doit pas être interrompu) : dates, liens poeme-france et copies Internet Archive sont réunis sur une seule page **Crédits** (credits.html), liée en pied de page.
4. Tout texte qui n'est pas un poème (présentations, transitions) est de la main de l'auteur ou validé par lui mot à mot.
5. La préface d'Isabelle Jespersen (acrostiche BIPOLAIRE) est conservée telle quelle.
6. Les créations mises en musique par IA (« Ma muse onirique », « Marcher sur un fil », « Méditations »…) sont présentées à part, clairement étiquetées, en second plan par rapport aux textes.

## Structure
```
index.html             accueil : mot d'accueil de l'auteur (validé mot à mot), les six parties, téléchargements, soutenir
poemes.html            sommaire : 6 parties (titres choisis par l'auteur dans ses vers, chapeaux validés)
poemes/<slug>.html     une page par texte (56) : texte à l'identique, musique si elle existe ; rien d'autre
credits.html           dates, sources (poeme-france) et copies Internet Archive de tous les textes ; préface ; musiques
le-livre.html          dédicace, préface d'Isabelle (acrostiche), ouverture, les six parties
musique.html           Concerto (piano, mp3), chansons de l'auteur (YouTube @delideal), maquettes IA
soutenir.html          Tipeee (lien à venir), éditeurs, musiciens, contact
mentions-legales.html
outils/build.py        GÉNÈRE toutes les pages ; outils/recueil.json = les textes et leur ordre
outils/livre.py        GÉNÈRE livre/marcher-sur-un-fil.pdf (A5, prêt à imprimer) et .epub à partir des mêmes données
                       (Chromium/Playwright + pypdf ; polices EB Garamond dans outils/fonts/, licence OFL)
livre/                 le recueil téléchargeable : PDF et EPUB, régénérés à chaque changement de texte
css/style.css  js/site.js  audio/  CNAME  .nojekyll  robots.txt  sitemap.xml
```

## Règles de travail (comme pour le site d'Ana)
1. Claude explique ce qu'il va faire et attend l'accord avant d'agir sur les fichiers.
2. Aucune suppression sans double confirmation explicite ; on déplace dans `Historique/`.
3. Sauvegarde datée dans `../Sauvegardes/` avant tout gros chantier.
4. Chaque modification de `css/` ou `js/` change le numéro de version `?v=AAAAMMJJx` dans les pages.
5. Le push vers GitHub se fait avec l'accord explicite de Sébastien.

## Journal
- 2026-10-28 : zone DNS OVH reconstituée (4 A + CNAME www), dépôt créé, page d'accueil provisoire ; site en ligne en HTTPS.
- 2026-10-29 : recueil complet en ligne (54 textes, 6 parties). Titres de parties choisis par l'auteur : Un jour commence / Éclaire mes nuits / Marcher sur un fil / Enfer, mais dans une poésie / Un chemin / Un espace pour aimer et respirer. Sous-titre : « Fragments de sensibilité bipolaire ». Chapeaux validés. Retirés du site : Conclusion, Postface, 4e de couverture, Note au lecteur. « Ma dernière hospitalisation » conservé, une phrase modifiée à la demande de l'auteur (« Le tout dans un secteur sensible. »). Strophes : découpe de poeme-france.com, alignée sur la version du manuscrit.
- 2026-10-29 (soir) : phase 2 (« moins et mieux ») : 56 textes ; page À propos retirée ; références retirées des pages de poèmes au profit d'une page Crédits unique.
- 2026-10-28 (v14) : mot d'accueil de l'auteur en haut de l'accueil (corrigé par lui) ; recueil téléchargeable en PDF (136 p., A5) et EPUB, générés par outils/livre.py depuis recueil.json — même contenu que le site, aucun texte ajouté ; extrait et paragraphes redondants de l'accueil retirés.
