# delideal.art — site des poèmes de Delideal

Ce README est la **source de vérité** des choix du site. Si une nouvelle instruction le contredit, on met le README à jour d'abord, puis le code.

## Le site en bref
- Adresse : https://delideal.art (domaine OVH, zone DNS → GitHub Pages ; CNAME `www` → sebastiennadler.github.io)
- Hébergement : GitHub Pages, dépôt `sebastiennadler/delideal.art`, branche `main`, racine `/`
- Type : site statique (HTML, CSS, un seul script pour le thème), sans base de données
- Langue : français uniquement pour commencer
- Thèmes : clair (défaut) et sombre, bouton sur chaque page, mémorisé (`delideal-theme`), appliqué avant le rendu

## Principes éditoriaux
1. **Texte brut** : aucune illustration, aucune image. Les textes sont de l'auteur ; le site n'affirme PAS « sans IA » (décision de l'auteur du 28/10/2026 : certains textes ont été retouchés, l'affirmation n'était pas tout à fait vraie). Seules les maquettes musicales IA sont étiquetées comme telles.
2. Les poèmes sont reproduits **à l'identique** ; jamais réécrits, jamais corrigés sans accord explicite de l'auteur.
3. Les textes sont **écrits depuis l'an 2000** et **publiés entre 2014 et 2023** sur poeme-france.com : ne jamais écrire « écrits entre 2014 et 2023 ».
3 bis. Les pages de poèmes ne portent **aucune mention de date ni de source** (le lecteur ne doit pas être interrompu) : dates, liens poeme-france et copies Internet Archive sont réunis sur une seule page **Crédits** (credits.html), liée en pied de page.
4. Tout texte qui n'est pas un poème (présentations, transitions) est de la main de l'auteur ou validé par lui mot à mot.
5. La préface d'Isabelle Jespersen (acrostiche BIPOLAIRE) est conservée telle quelle.
6. Les créations mises en musique par IA (« Ma muse onirique », « Marcher sur un fil », « Méditations »…) sont présentées à part, clairement étiquetées, en second plan par rapport aux textes.

## Structure
```
index.html             accueil « page de titre » : préface d'Isabelle (acrostiche), ouverture (1re strophe du poème-titre), les six parties avec la 1re phrase de leur introduction, cartes PDF/EPUB, soutenir
poemes.html            sommaire : 6 parties (titres choisis par l'auteur dans ses vers, chapeaux validés)
poemes/<slug>.html     une page par texte (50) : texte à l'identique, musique si elle existe ; rien d'autre
credits.html           dates, sources (poeme-france) et copies Internet Archive de tous les textes ; préface ; musiques
le-livre.html          dédicace, préface d'Isabelle (acrostiche), ouverture, les six parties
musique.html           Concerto (piano, mp3), chansons de l'auteur (YouTube @delideal), maquettes IA
soutenir.html          Tipeee (fr.tipeee.com/delidealart), éditeurs, musiciens, contact
mentions-legales.html
outils/build.py        GÉNÈRE toutes les pages ; outils/recueil.json = les textes et leur ordre
partage/carte.png      carte d'aperçu (typographique, 1200×630) pour les partages Facebook/réseaux ; og:image dans chaque page
outils/livre.py        GÉNÈRE livre/marcher-sur-un-fil.pdf (écran, liens actifs), -impression.pdf (A5 recto-verso) et .epub
                       (Chromium/Playwright + pypdf ; polices EB Garamond dans outils/fonts/, licence OFL)
livre/                 le recueil téléchargeable : PDF écran, PDF imprimable, EPUB — régénérés à chaque changement de texte
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
- 2026-10-28 (v15) : partie II renommée « Le désir » (choix de l'auteur) ; PDF/EPUB régénérés.
- 2026-10-28 (v16) : six introductions de partie (première personne, faites des vers de l'auteur, validées mot à mot par lui) remplacent les chapeaux sur la page Poèmes et dans le livre ; anciens chapeaux conservés dans recueil.json (chapeau_court). PDF/EPUB régénérés.
- 2026-10-28 (v17) : deux PDF (écran avec liens actifs vers YouTube, mp3, sources, Tipeee ; imprimable A5 recto-verso) + EPUB avec liens ; page Tipeee ouverte (fr.tipeee.com/delidealart) : lien sur l'accueil, Soutenir (bouton), pied de page et dans le livre.
- 2026-10-28 (v18) : « L'Aube » retirée à la demande de l'auteur (55 textes) ; livre régénéré.
- 2026-10-28 (v19) : carte d'aperçu typographique pour les partages (og:image), à la demande de l'auteur ; Tipeee active (IBAN + PayPal).
- 2026-10-28 (v20) : retrait de toute affirmation « sans IA » (accueil, crédits, livre, carte de partage) à la demande de l'auteur ; les mentions « musique IA » des maquettes restent.
- 2026-10-28 (v21) : refonte visuelle à la demande de l'auteur (« brouillon, pas séduisant ») : accueil en page de titre centrée, préface d'Isabelle et ouverture par le poème-titre à la place du mot d'accueil (jugé « banal » par l'auteur : le texte reste dans l'historique git), sommaire de livre (chiffres romains or, teaser), cartes de téléchargement, liens discrets dans la prose, mesure 36rem, vers en romain, « En musique » en simple ligne ; sommaire des poèmes sur deux colonnes.
- 2026-10-28 (v22) : sommaire des PDF cliquable (liens internes vers chaque texte) ; Soutenir : partenariats illustrations et clips.
- 2026-10-28 (v23) : « À toi » retiré à la demande de l'auteur (54 textes) ; fin de l'introduction VI ajustée ; livre régénéré. L'auteur veut revoir les 6 textes ajoutés le 29/10 (src pf-site-2026-10-29).
- 2026-10-28 (v24) : retour au manuscrit : les 5 textes ajoutés par Claude le 29/10 retirés (Savante indolence, Civilisé ?, Garçon perdu, La vérité des masques, Confiance) ; « Cieux d'été » remis (auteur : « j'aime bien »). 50 textes. Introduction VI ajustée. Livre régénéré.
- 2026-10-28 (v27) : six introductions de partie refaites en vers courts (écrites par Claude avec les images de l'auteur, validées par lui « C'est beaucoup mieux ») ; affichées en vers sur Poèmes et dans le livre ; l'accueil montre le premier vers. Version prose précédente conservée dans recueil.json.
- 2026-10-28 (v28) : liens de partage (Facebook, WhatsApp, X, courriel, copier le lien) sous chaque poème, sur l'accueil, Le livre et Soutenir — simples adresses de partage, aucun script tiers ni traceur.
- 2026-10-28 (v30) : partage « boule de neige » (un mot d'invitation avec les liens) ; livres : page « Pour continuer » et colophon renvoient explicitement vers delideal.art/soutenir.html ; Tipeee renommée « Delideal », bannière en place.
- 2026-10-28 (v31) : maquettes IA référencées précisément (auteur) : « Ma muse onirique » = Ma Muse Onirique + Emporté par le vent ; « Marcher sur un fil » = Marcher sur un fil + Du diable à l'homme ; « Méditations » = les trois méditations. Paroles finales à ajouter quand l'auteur les fournit.
- 2026-10-28 (v32) : paroles des maquettes (données « maquettes » dans recueil.json, fournies par l'auteur) affichées sur la page Musique dans un bloc dépliable, avec les poèmes d'origine ; lien « lire les paroles » sous les poèmes concernés. Ma muse onirique faite ; Marcher sur un fil et Méditations en attente des paroles.
