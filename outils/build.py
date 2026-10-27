#!/usr/bin/env python3
"""Générateur des pages de delideal.art.

Un seul gabarit (head, navbar, footer) pour toutes les pages, comme le
navbar-sync.py du site d'Ana : on ne touche jamais la navbar dans les HTML,
on modifie PAGES / NAV ci-dessous puis on lance :  python3 outils/build.py

Les poèmes ne sont PAS dans ce fichier : ils vivront dans poemes/*.html
(une page par poème, texte reproduit à l'identique, date + lien poeme-france).
"""
from pathlib import Path
from datetime import date

ROOT = Path(__file__).resolve().parent.parent
VERSION = "20261028a"          # à changer à chaque modification de css/ ou js/
SITE = "https://delideal.art"
NAV = [("index.html", "Accueil"), ("poemes.html", "Poèmes"), ("le-livre.html", "Le livre"),
       ("musique.html", "Musique"), ("soutenir.html", "Soutenir"), ("a-propos.html", "À propos")]

HEAD = """<!DOCTYPE html>
<html data-theme="light" lang="fr">
<head>
<meta charset="utf-8">
<script>(function(){{try{{var t=localStorage.getItem("delideal-theme");if(t==="dark"||t==="light"){{document.documentElement.setAttribute("data-theme",t);}}}}catch(e){{}}}})();</script>
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{description}">
<meta name="robots" content="{robots}">
<meta name="author" content="Delideal">
<meta name="theme-color" content="#fbf7ef" media="(prefers-color-scheme: light)">
<meta name="theme-color" content="#151516" media="(prefers-color-scheme: dark)">
<link rel="canonical" href="{canonical}">
<meta property="og:site_name" content="Delideal — poèmes">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{description}">
<meta property="og:type" content="website">
<meta property="og:url" content="{canonical}">
<meta property="og:locale" content="fr_FR">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=EB+Garamond:ital,wght@0,400;0,500;1,400;1,500&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{rel}css/style.css?v={v}">
<script defer src="{rel}js/site.js?v={v}"></script>
</head>
<body>
<a class="skip-link" href="#main">Aller au contenu</a>
<!-- ===== Barre de navigation commune (générée par outils/build.py : ne pas modifier à la main) ===== -->
<nav class="navbar">
<div class="navbar-container">
<span class="site-brand">Delideal <small>poèmes</small></span>
<ul class="nav-links" id="primary-nav">
{nav}
</ul>
<div class="nav-actions">
<button aria-label="Changer le thème" class="theme-toggle" id="theme-toggle" type="button"><span class="theme-icon">☀︎</span></button>
<button aria-controls="primary-nav" aria-expanded="false" aria-label="Ouvrir le menu" class="hamburger" id="menu-toggle" type="button">☰</button>
</div>
</div>
</nav>
<main id="main">
"""

FOOT = """</main>
<footer>
<p>© {year} Delideal — textes écrits et publiés depuis 2014. Tous droits réservés.</p>
<p><a href="{rel}mentions-legales.html">Mentions légales</a> · <a href="https://www.poeme-france.com/auteur/delideal/" rel="noopener">Ma page sur poeme-france.com</a></p>
</footer>
</body>
</html>
"""

PAGES = {
"index.html": dict(
  title="Delideal — Marcher sur un fil, poèmes",
  description="Les poèmes de Delideal, écrits et publiés depuis 2014. Texte brut, sans image.",
  body="""
<h1 class="titre-fil">Marcher sur un fil</h1>
<div class="fil" aria-hidden="true"></div>
<p class="sous-titre">Chronique des cimes et des gouffres</p>

<section class="panel">
<blockquote class="poeme">
<p>Du ciment dans les veines
Pour éviter l’hémorragie cérébrale.
Mais lentement les vaisseaux de mon cœur saignent
De la poudre de brique issue de mon mal.</p>
</blockquote>
<p class="source">Extrait de « Marcher sur un fil », publié le 5 avril 2019 sur <a href="https://www.poeme-france.com/auteur/delideal/texte-178903" rel="noopener">poeme-france.com</a>.</p>
</section>

<h2>Le site se construit</h2>
<p>Il réunira, par thème, les poèmes écrits depuis 2014 et déjà publiés sur <a href="https://www.poeme-france.com/auteur/delideal/" rel="noopener">ma page poeme-france.com</a> : cent quinze textes datés, en accès libre. Chaque poème y renverra à sa page d’origine, avec sa date de première publication.</p>
<p>Viendront ensuite le recueil, quelques mises en musique et une page pour soutenir ce travail.</p>

<section class="panel">
<h2>Des textes écrits avant l’intelligence artificielle</h2>
<p>Tous les poèmes de ce site ont été publiés sur <a href="https://www.poeme-france.com/auteur/delideal/" rel="noopener">poeme-france.com</a> entre 2014 et 2023, sous le nom Delideal. Chaque texte y porte sa date et son heure de mise en ligne, fixées par le site et non modifiables par l’auteur : le plus ancien date de novembre 2014, le plus récent de décembre 2023.</p>
<p>Une copie indépendante de cette page, conservée par Internet Archive, est consultable <a href="https://web.archive.org/web/20250914075727/https://www.poeme-france.com/auteur/delideal/" rel="noopener">ici</a>. Sur ce site, chaque poème renvoie à sa page d’origine.</p>
<p>Aucun texte n’a été écrit, réécrit ou retouché par une intelligence artificielle. Ce site lui-même ne contient aucune image.</p>
</section>
<ul class="liens">
<li><a href="poemes.html">Les poèmes</a></li>
<li><a href="le-livre.html">Le livre</a></li>
<li><a href="musique.html">Mises en musique</a></li>
<li><a href="soutenir.html">Soutenir</a></li>
</ul>
"""),
"poemes.html": dict(
  title="Les poèmes — Delideal",
  description="Tous les poèmes de Delideal, classés par thème, avec leur date de première publication.",
  body="""
<h1 class="titre-fil">Les poèmes</h1>
<div class="fil" aria-hidden="true"></div>
<p class="note">Page en préparation : le classement par thème est en cours.</p>
<p>En attendant, les cent quinze textes sont lisibles, datés, sur <a href="https://www.poeme-france.com/auteur/delideal/" rel="noopener">ma page poeme-france.com</a>.</p>
"""),
"le-livre.html": dict(
  title="Le livre — Marcher sur un fil",
  description="Marcher sur un fil, chronique des cimes et des gouffres : le recueil de Delideal.",
  body="""
<h1 class="titre-fil">Le livre</h1>
<div class="fil" aria-hidden="true"></div>
<p class="sous-titre">Marcher sur un fil — Chronique des cimes et des gouffres</p>
<p class="note">Page en préparation.</p>
"""),
"musique.html": dict(
  title="Mises en musique — Delideal",
  description="Les poèmes de Delideal mis en musique. Textes de l’auteur ; musique et voix générées par intelligence artificielle.",
  body="""
<h1 class="titre-fil">Mises en musique</h1>
<div class="fil" aria-hidden="true"></div>
<p>Les textes sont les miens, écrits bien avant. La musique et la voix de ces enregistrements ont été produites avec des outils d’intelligence artificielle : ce sont des <strong>maquettes</strong>, une façon d’entendre ce que ces poèmes pourraient devenir en chanson.</p>
<p>Elles sont une porte ouverte : si vous êtes musicienne ou musicien et qu’un de ces textes vous parle, <a href="soutenir.html">écrivez-moi</a>. L’idée est qu’un jour ces chansons soient jouées et chantées par des humains.</p>
<ul class="liens">
<li><a href="https://www.youtube.com/watch?v=gunECfrHhX0" rel="noopener">Concerto pour hall de gare</a> <span class="etiquette">musique IA</span></li>
<li><a href="https://www.youtube.com/watch?v=0cXd1CGXFjQ" rel="noopener">Le cœur assoiffé</a> <span class="etiquette">musique IA</span></li>
<li><a href="https://youtu.be/a-SMOUOUEdY" rel="noopener">Re-pas-sage</a> <span class="etiquette">musique IA</span></li>
</ul>
<p class="note">À venir : « Ma muse onirique », « Marcher sur un fil », « Méditations ».</p>
"""),
"soutenir.html": dict(
  title="Soutenir — Delideal",
  description="Soutenir le travail de Delideal : contributions, éditeurs, musiciens.",
  body="""
<h1 class="titre-fil">Soutenir</h1>
<div class="fil" aria-hidden="true"></div>
<h2>Contribuer</h2>
<p>Ce site est gratuit et sans publicité. Si ces textes vous ont touché, vous pouvez soutenir leur publication par un don, ponctuel ou mensuel, sur Tipeee, plateforme française dédiée aux créateurs.</p>
<p class="note">Le lien Tipeee sera ajouté dès l’ouverture de la page.</p>
<h2>Éditeurs, musiciens</h2>
<p>Je cherche une maison d’édition pour le recueil <em>Marcher sur un fil</em>, et des musiciennes et musiciens pour mettre certains poèmes en chanson : les maquettes de la page <a href="musique.html">Musique</a> montrent la direction. Écrivez-moi : <a class="courriel" data-u="sebastien.nadler" data-d="gmail.com" href="#">sebastien.nadler [at] gmail.com</a>.</p>
"""),
"a-propos.html": dict(
  title="À propos — Delideal",
  description="Qui est Delideal.",
  body="""
<h1 class="titre-fil">À propos</h1>
<div class="fil" aria-hidden="true"></div>
<p class="note">Page en préparation : ce texte sera écrit par l’auteur.</p>
"""),
"mentions-legales.html": dict(
  title="Mentions légales — Delideal", robots="noindex,follow",
  description="Mentions légales du site delideal.art.",
  body="""
<h1 class="titre-fil">Mentions légales</h1>
<div class="fil" aria-hidden="true"></div>
<h2>Éditeur</h2>
<p>Ce site est édité par Sébastien Nadler, auteur publiant sous le nom de Delideal. Contact : <a class="courriel" data-u="sebastien.nadler" data-d="gmail.com" href="#">sebastien.nadler [at] gmail.com</a>.</p>
<h2>Hébergement</h2>
<p>GitHub Pages — GitHub, Inc., 88 Colin P. Kelly Jr. Street, San Francisco, CA 94107, États-Unis.</p>
<h2>Propriété intellectuelle</h2>
<p>Tous les textes sont l’œuvre de leur auteur et protégés par le droit d’auteur. Toute reproduction sans accord écrit est interdite.</p>
<h2>Données personnelles</h2>
<p>Ce site ne dépose aucun cookie et ne collecte aucune donnée. Le choix du thème clair ou sombre est mémorisé dans votre navigateur uniquement.</p>
"""),
}

def nav_html(rel):
    return "\n".join(f'<li><a href="{rel}{href}">{label}</a></li>' for href, label in NAV)

def build():
    written = []
    for name, p in PAGES.items():
        rel = ""   # toutes les pages à la racine pour l'instant ; poemes/ utilisera rel="../"
        canonical = SITE + "/" + ("" if name == "index.html" else name)
        html = HEAD.format(title=p["title"], description=p["description"], robots=p.get("robots", "index,follow"),
                           canonical=canonical, rel=rel, v=VERSION, nav=nav_html(rel)) \
               + p["body"].strip("\n") + "\n" + FOOT.format(year=date.today().year, rel=rel)
        (ROOT / name).write_text(html, encoding="utf-8"); written.append(name)
    urls = [SITE + "/" + ("" if n == "index.html" else n) for n in PAGES if PAGES[n].get("robots", "index") .startswith("index")]
    sm = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + \
         "".join(f"  <url><loc>{u}</loc></url>\n" for u in urls) + "</urlset>\n"
    (ROOT / "sitemap.xml").write_text(sm, encoding="utf-8")
    print("Pages générées :", ", ".join(written), "+ sitemap.xml")

if __name__ == "__main__":
    build()
