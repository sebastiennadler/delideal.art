#!/usr/bin/env python3
"""Générateur des pages de delideal.art.

Un seul gabarit (head, navbar, footer) pour toutes les pages, comme le
navbar-sync.py du site d'Ana. On ne touche jamais la navbar dans les HTML :
on modifie ce fichier (pages fixes) ou outils/recueil.json (les poèmes),
puis on lance :  python3 outils/build.py

Les textes des poèmes vivent dans outils/recueil.json, reproduits à
l'identique depuis le manuscrit de l'auteur ; chaque poème porte la date de
sa première publication sur poeme-france.com et le lien vers sa page.
"""
import html
import json
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
VERSION = "20261029a"          # à changer à chaque modification de css/ ou js/
SITE = "https://delideal.art"
NAV = [("index.html", "Accueil"), ("poemes.html", "Poèmes"), ("le-livre.html", "Le livre"),
       ("musique.html", "Musique"), ("soutenir.html", "Soutenir"), ("a-propos.html", "À propos")]
PF_AUTEUR = "https://www.poeme-france.com/auteur/delideal/"
ARCHIVE = "https://web.archive.org/web/20250914075727/https://www.poeme-france.com/auteur/delideal/"

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
<meta property="og:type" content="{ogtype}">
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
<p><a href="{rel}mentions-legales.html">Mentions légales</a> · <a href="{pf}" rel="noopener">Ma page sur poeme-france.com</a> · <a href="{rel}soutenir.html">Soutenir</a></p>
</footer>
</body>
</html>
"""

def esc(s):
    return html.escape(s, quote=False)

def nav_html(rel):
    return "\n".join(f'<li><a href="{rel}{href}">{label}</a></li>' for href, label in NAV)

def page(name, title, description, body, rel="", robots="index,follow", ogtype="website"):
    canonical = SITE + "/" + ("" if name == "index.html" else name)
    return (HEAD.format(title=esc(title), description=esc(description), robots=robots, ogtype=ogtype,
                        canonical=canonical, rel=rel, v=VERSION, nav=nav_html(rel))
            + body.strip("\n") + "\n"
            + FOOT.format(year=date.today().year, rel=rel, pf=PF_AUTEUR))

# ---------------------------------------------------------------- recueil
R = json.loads((ROOT / "outils" / "recueil.json").read_text(encoding="utf-8"))
FRONT, PARTS = R["front"], R["parts"]
ALL = [(P, e) for P in PARTS for e in P["poems"]]

def pf_url(e):
    return f"https://www.poeme-france.com/auteur/delideal/texte-{e['pf']}" if e.get("pf") else None

def source_line(e, rel=""):
    if e.get("pf"):
        wb = f'https://web.archive.org/web/2026/{pf_url(e)}'
        out = (f'<p class="source">Première publication le {e["date"]} sur '
               f'<a href="{pf_url(e)}" rel="noopener">poeme-france.com</a> (texte n° {e["pf"]}) : '
               f'la date et l’heure de mise en ligne, et les commentaires de lecteurs de l’époque, y sont visibles. '
               f'<a href="{wb}" rel="noopener">Copie Internet Archive</a>.</p>')
        if e.get("corroboration"):
            out += f'\n<p class="source">{esc(e["corroboration"])}</p>'
        return out
    return '<p class="source">Inédit : ce texte ne figure que dans le recueil.</p>'

def render_blocks(e):
    kind = e.get("kind", "verse")
    out = []
    if kind == "verse":
        for b in e["blocks"]:
            out.append('<p class="strophe">' + "<br>\n".join(esc(l) for l in b) + "</p>")
        return '<div class="poeme">\n' + "\n".join(out) + "\n</div>"
    if kind == "prose":
        for b in e["blocks"]:
            for l in b:
                out.append("<p>" + esc(l) + "</p>")
        return '<div class="prose">\n' + "\n".join(out) + "\n</div>"
    if kind == "theatre":
        for b in e["blocks"]:
            for l in b:
                t = l.strip()
                if t.startswith("Acte ") or t in ("Introduction", "Conclusion") or t.startswith("Suite et Fin"):
                    out.append(f"<h2>{esc(t)}</h2>")
                elif t.startswith("Scène "):
                    out.append(f"<h3>{esc(t)}</h3>")
                elif t.startswith("(") and t.endswith(")"):
                    out.append(f'<p class="didascalie">{esc(t)}</p>')
                elif t.endswith(":") and len(t) < 40:
                    out.append(f'<p class="personnage">{esc(t)}</p>')
                else:
                    out.append(f'<p class="replique">{esc(t)}</p>')
        return '<div class="theatre">\n' + "\n".join(out) + "\n</div>"
    raise ValueError(kind)

def music_block(e, rel=""):
    m = e.get("music")
    if not m:
        return ""
    parts = []
    if m["kind"] == "piano":
        parts.append(f'<p>{esc(m["label"])}.</p>')
        parts.append(f'<audio controls preload="none" src="{rel}{m["mp3"]}" style="width:100%">Votre navigateur ne lit pas l’audio : <a href="{rel}{m["mp3"]}">télécharger le mp3</a>.</audio>')
        parts.append(f'<p class="source"><a href="{rel}{m["mp3"]}" download>Télécharger le mp3</a> · <a href="{m["yt"]}" rel="noopener">Voir sur YouTube</a></p>')
    elif m["kind"] == "auteur":
        links = f'<a href="{m["yt"]}" rel="noopener">{esc(m["label"])}</a>'
        if m.get("yt2"):
            links += f' · <a href="{m["yt2"]}" rel="noopener">{esc(m["label2"])}</a>'
        parts.append(f'<p>Ce poème est aussi une chanson, écrite et chantée par l’auteur : {links} (YouTube).</p>')
    elif m["kind"] == "ia":
        if m.get("yt"):
            parts.append(f'<p>{esc(m["label"])} : <a href="{m["yt"]}" rel="noopener">écouter sur YouTube</a>. <span class="etiquette">musique IA</span> Texte de l’auteur ; musique et voix générées par intelligence artificielle, pour donner une idée de ce que ce poème pourrait devenir en chanson.</p>')
        else:
            parts.append(f'<p class="note">{esc(m["label"])}. <span class="etiquette">musique IA</span></p>')
    return '<section class="panel musique"><h2>En musique</h2>\n' + "\n".join(parts) + "\n</section>"

def poem_page(i):
    P, e = ALL[i]
    rel = "../"
    prev_ = ALL[i - 1] if i > 0 else None
    next_ = ALL[i + 1] if i + 1 < len(ALL) else None
    body = [f'<p class="partie-label"><a href="{rel}poemes.html#partie-{P["num"]}">{P["num"]} · {esc(P["title"])}</a></p>',
            f'<h1 class="titre-fil">{esc(e["title"])}</h1>', '<div class="fil" aria-hidden="true"></div>']
    if e.get("dedicace"):
        body.append(f'<p class="sous-titre">{esc(e["dedicace"])}</p>')
    body.append(render_blocks(e))
    if e.get("note"):
        body.append(f'<p class="note-auteur">{esc(e["note"])}</p>')
    body.append(source_line(e, rel))
    body.append(music_block(e, rel))
    nav = ['<nav class="poeme-nav" aria-label="Poème précédent et suivant">']
    nav.append(f'<a class="prec" href="{rel}poemes/{prev_[1]["slug"]}.html">← {esc(prev_[1]["title"])}</a>' if prev_ else "<span></span>")
    nav.append(f'<a class="sommaire" href="{rel}poemes.html">Sommaire</a>')
    nav.append(f'<a class="suiv" href="{rel}poemes/{next_[1]["slug"]}.html">{esc(next_[1]["title"])} →</a>' if next_ else "<span></span>")
    nav.append("</nav>")
    body.append("\n".join(nav))
    desc = f'« {e["title"]} », poème de Delideal' + (f' publié le {e["date"]}' if e.get("date") else "") + f' — {P["title"]}.'
    return page(f'poemes/{e["slug"]}.html', f'{e["title"]} — Delideal', desc, "\n".join(body), rel=rel, ogtype="article")

def sommaire_page():
    body = ['<h1 class="titre-fil">Les poèmes</h1>', '<div class="fil" aria-hidden="true"></div>',
            f'<p class="sous-titre">{esc(FRONT["title"])} — {esc(FRONT["subtitle"])}</p>',
            '<p>Cinquante-quatre textes en six parties, dans l’ordre du recueil. Chaque page indique la date de première publication et renvoie à la page d’origine sur poeme-france.com.</p>']
    for P in PARTS:
        body.append(f'<section class="partie" id="partie-{P["num"]}">')
        body.append(f'<h2>{P["num"]}. {esc(P["title"])}</h2>')
        if P.get("chapeau"):
            body.append(f'<p class="chapeau">{esc(P["chapeau"])}</p>')
        body.append('<ol class="liste-poemes">')
        for e in P["poems"]:
            meta = e["date"][-4:] if e.get("date") else "inédit"
            tag = ""
            if e.get("music"):
                tag = ' <span class="etiquette">musique</span>' if e["music"]["kind"] != "ia" else ' <span class="etiquette">musique IA</span>'
            body.append(f'<li><a href="poemes/{e["slug"]}.html">{esc(e["title"])}</a>{tag} <span class="annee">{meta}</span></li>')
        body.append("</ol></section>")
    return page("poemes.html", "Les poèmes — Delideal",
                "Tous les poèmes du recueil Marcher sur un fil, en six parties, avec leur date de première publication.", "\n".join(body))

def livre_page():
    pref = "\n".join(f'<span class="acro"><strong>{esc(l[0])}</strong>{esc(l[1:])}</span>' for l in FRONT["preface"]["lines"])
    body = [f'<h1 class="titre-fil">{esc(FRONT["title"])}</h1>', '<div class="fil" aria-hidden="true"></div>',
            f'<p class="sous-titre">{esc(FRONT["subtitle"])}</p>',
            '<p>Un recueil écrit entre 2014 et 2023, composé en six parties. Il cherche un éditeur ; en attendant, il se lit ici en entier, et il existe en version PDF prête à imprimer.</p>',
            '<section class="panel"><h2>Dédicace</h2>', f'<p class="dedicace">{esc(FRONT["dedicace"])}</p>', '</section>',
            '<section class="panel"><h2>Préface</h2>', f'<p class="preface">{pref}</p>', f'<p class="signature">{esc(FRONT["preface"]["sign"])}</p>', '</section>',
            '<section class="panel"><h2>Ouverture</h2>']
    for l in FRONT["ouverture"]:
        body.append(f'<p class="citation">{esc(l)}</p>')
    body.append('</section>')
    body.append('<h2>Les six parties</h2><ol class="liste-poemes parties">')
    for P in PARTS:
        body.append(f'<li><a href="poemes.html#partie-{P["num"]}">{P["num"]}. {esc(P["title"])}</a> <span class="annee">{len(P["poems"])} textes</span></li>')
    body.append('</ol>')
    body.append('<p><a href="poemes.html">Commencer la lecture</a> · <a href="soutenir.html">Soutenir l’édition du livre</a></p>')
    return page("le-livre.html", "Le livre — Marcher sur un fil",
                "Marcher sur un fil, fragments de sensibilité bipolaire : le recueil de Delideal, préface d’Isabelle Jespersen.", "\n".join(body))

# ---------------------------------------------------------------- pages fixes
first = ALL[0][1]
PAGES = {
"index.html": dict(
  title="Delideal — Marcher sur un fil, poèmes",
  description="Les poèmes de Delideal, écrits et publiés depuis 2014. Un recueil en six parties, des chansons, et un livre à faire naître.",
  body=f"""
<h1 class="titre-fil">Marcher sur un fil</h1>
<div class="fil" aria-hidden="true"></div>
<p class="sous-titre">{esc(FRONT["subtitle"])}</p>

<section class="panel">
<blockquote class="poeme">
<p class="strophe">Du ciment dans les veines<br>
pour éviter l’hémorragie cérébrale.<br>
Mais lentement les vaisseaux de mon cœur saignent<br>
de la poudre de brique issue de mon mal.</p>
</blockquote>
<p class="source">Extrait de « <a href="poemes/marcher-sur-un-fil.html">Marcher sur un fil</a> », publié le 5 avril 2019 sur <a href="https://www.poeme-france.com/auteur/delideal/texte-178903" rel="noopener">poeme-france.com</a>.</p>
</section>

<h2>Entrer</h2>
<p>Ces poèmes racontent une vie vécue à nu : l’enfance qui s’émerveille, le désir qui déborde, la folie qui blesse et révèle, puis les chemins qu’on se trace pour tenir debout. Ils ont été écrits entre 2014 et 2023, publiés au fur et à mesure, et rassemblés en un recueil de six parties.</p>
<ol class="liste-poemes parties">
{"".join(f'<li><a href="poemes.html#partie-{P["num"]}">{P["num"]}. {esc(P["title"])}</a> <span class="annee">{len(P["poems"])} textes</span></li>' for P in PARTS)}
</ol>
<p>Pour entrer par le début : <a href="poemes/{first["slug"]}.html">{esc(first["title"])}</a>. Pour entrer par le cœur : <a href="poemes/marcher-sur-un-fil.html">Marcher sur un fil</a> ou <a href="poemes/dsm-story.html">DSM Story</a>. Pour entrer par la musique : <a href="musique.html">Concerto pour hall de gare</a>, une improvisation au piano.</p>

<section class="panel">
<h2>Des textes écrits avant l’intelligence artificielle</h2>
<p>Tous les poèmes de ce site ont été publiés sur <a href="{PF_AUTEUR}" rel="noopener">poeme-france.com</a> entre 2014 et 2023, sous le nom Delideal. Chaque texte y porte sa date et son heure de mise en ligne, fixées par le site et non modifiables par l’auteur : le plus ancien date de novembre 2014, le plus récent de décembre 2023.</p>
<p>Sur ce site, chaque poème renvoie à sa page d’origine, où l’on peut vérifier la date, et souvent lire des commentaires de lecteurs datés de l’époque. Pour certains textes, la chanson mise en ligne sur YouTube dès 2015 apporte une seconde date indépendante. Enfin, des copies de ces pages sont conservées par Internet Archive (la première page de la liste depuis <a href="{ARCHIVE}" rel="noopener">septembre 2025</a>, chaque page de poème à partir d’octobre 2026) : elles figent ce que le site d’origine affiche, au cas où il disparaîtrait.</p>
<p>Aucun texte n’a été écrit par une intelligence artificielle. Ce site lui-même ne contient aucune image.</p>
</section>

<h2>Continuer</h2>
<p>Ce site est gratuit et le restera. Si ces textes vous ont touché, vous pouvez aider à ce que l’activité continue : un don, ponctuel ou mensuel, sur <a href="soutenir.html">Tipeee</a> ; et pour aller plus loin, une maison d’édition pour faire du recueil un vrai livre, ou des musiciennes et musiciens pour transformer les maquettes en chansons. <a href="soutenir.html">Tout est expliqué ici</a>.</p>
"""),
"musique.html": dict(
  title="Musique — Delideal",
  description="Les musiques de Delideal : improvisation au piano, chansons sur ses poèmes, et maquettes.",
  body="""
<h1 class="titre-fil">Musique</h1>
<div class="fil" aria-hidden="true"></div>

<section class="panel">
<h2>Concerto pour hall de gare</h2>
<p>Une improvisation au piano, jouée et enregistrée par moi-même. Pas d’intelligence artificielle ici : juste un piano et un moment. Le <a href="poemes/concerto-pour-hall-de-gare.html">poème du même nom</a> raconte ce moment.</p>
<audio controls preload="none" src="audio/concerto-pour-hall-de-gare.mp3" style="width:100%">Votre navigateur ne lit pas l’audio : <a href="audio/concerto-pour-hall-de-gare.mp3">télécharger le mp3</a>.</audio>
<p class="source"><a href="audio/concerto-pour-hall-de-gare.mp3" download>Télécharger le mp3</a> (5 min 34, 4,5 Mo) · <a href="https://www.youtube.com/watch?v=gunECfrHhX0" rel="noopener">Voir sur YouTube</a> · à partager librement en me citant.</p>
</section>

<h2>Chansons</h2>
<p>Des poèmes que j’ai mis en musique et chantés moi-même, en amateur, sur <a href="https://www.youtube.com/@delideal" rel="noopener">ma chaîne YouTube</a>.</p>
<ul class="liens">
<li><a href="https://www.youtube.com/watch?v=0cXd1CGXFjQ" rel="noopener">Le cœur assoiffé</a> · <a href="poemes/le-coeur-assoiffe.html">le poème</a></li>
<li><a href="https://www.youtube.com/watch?v=a-SMOUOUEdY" rel="noopener">Re-Pas-Sage</a> · <a href="https://www.youtube.com/watch?v=oufArkLT7kM" rel="noopener">version acoustique</a> · <a href="poemes/re-pas-sage.html">le poème</a></li>
<li><a href="https://www.youtube.com/watch?v=zSsJ_OX-HS8" rel="noopener">Éclaire mes nuits</a> · <a href="poemes/eclaire-mes-nuits.html">le poème</a></li>
<li><a href="https://www.youtube.com/watch?v=fShhj3QWdk8" rel="noopener">Noir et Blanc</a> · <a href="poemes/noir-et-blanc.html">le poème</a></li>
<li><a href="https://www.youtube.com/watch?v=ymVq2wLCgnw" rel="noopener">Chanson de mes démons</a> · <a href="https://www.poeme-france.com/auteur/delideal/texte-162480" rel="noopener">le texte sur poeme-france</a></li>
<li><a href="https://www.youtube.com/watch?v=jWdzEa7Qd-0" rel="noopener">Si ton tableau est noir</a> <span class="annee">texte inédit</span></li>
</ul>
<h2>Autre improvisation</h2>
<ul class="liens">
<li><a href="https://www.youtube.com/watch?v=QFCULzpDsJk" rel="noopener">Rage and Hopes</a> — une improvisation au piano, brouillonne et sincère, douze minutes sans intelligence artificielle.</li>
</ul>

<h2>Maquettes</h2>
<p>D’autres textes ont été mis en musique avec des outils d’intelligence artificielle : ce sont des <strong>maquettes</strong>, une façon d’entendre ce que ces poèmes pourraient devenir en chanson. Elles sont une porte ouverte : si vous êtes musicienne ou musicien et qu’un de ces textes vous parle, <a href="soutenir.html">écrivez-moi</a>. L’idée est qu’un jour ces chansons soient jouées et chantées par des humains.</p>
<ul class="liens">
<li><a href="https://www.youtube.com/watch?v=EJr4KC2jq6E" rel="noopener">Marcher sur un fil</a> <span class="etiquette">musique IA</span> · inspirée de deux textes : <a href="poemes/marcher-sur-un-fil.html">Marcher sur un fil</a> et <a href="poemes/du-diable-a-lhomme.html">Du diable à l’homme</a></li>
<li><a href="https://www.youtube.com/watch?v=W0gOmmTVj7o" rel="noopener">Ma muse onirique</a> <span class="etiquette">musique IA</span> · <a href="poemes/ma-muse-onirique.html">le poème</a></li>
<li><a href="https://www.youtube.com/watch?v=U1Ou6cdE1Zc" rel="noopener">Méditations</a> <span class="etiquette">musique IA</span> · <a href="poemes/meditation-1-sur-le-silence.html">les trois méditations</a></li>
</ul>
"""),
"soutenir.html": dict(
  title="Soutenir — Delideal",
  description="Soutenir le travail de Delideal : contributions, éditeurs, musiciens.",
  body="""
<h1 class="titre-fil">Soutenir</h1>
<div class="fil" aria-hidden="true"></div>
<p>Écrire, publier, mettre en musique : tout cela prend du temps et un peu d’argent. Ce site est gratuit et sans publicité, et il le restera. Voici trois façons d’aider.</p>
<h2>Contribuer</h2>
<p>Un don, ponctuel ou mensuel, sur Tipeee, plateforme française dédiée aux créateurs. Il sert à faire vivre ce site, à continuer d’écrire, et à réunir les moyens de publier le recueil <em>Marcher sur un fil</em> en vrai livre et en ebook.</p>
<p class="note">Le lien Tipeee sera ajouté dès l’ouverture de la page.</p>
<h2>Éditer</h2>
<p>Je cherche une maison d’édition pour le recueil. Le manuscrit est prêt, préfacé, et se lit en entier sur ce site. Écrivez-moi : <a class="courriel" data-u="sebastien.nadler" data-d="gmail.com" href="#">sebastien.nadler [at] gmail.com</a>.</p>
<h2>Mettre en musique</h2>
<p>Plusieurs poèmes sont déjà des chansons, d’autres n’existent qu’en maquette : la page <a href="musique.html">Musique</a> montre la direction. Si vous êtes musicienne ou musicien et qu’un texte vous parle, même adresse.</p>
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
<p>Tous les textes et musiques sont l’œuvre de leur auteur et protégés par le droit d’auteur. Toute reproduction sans accord écrit est interdite, à l’exception de la citation courte avec mention de la source.</p>
<h2>Données personnelles</h2>
<p>Ce site ne dépose aucun cookie et ne collecte aucune donnée. Le choix du thème clair ou sombre est mémorisé dans votre navigateur uniquement.</p>
"""),
}

def build():
    written = []
    for name, p in PAGES.items():
        (ROOT / name).write_text(page(name, p["title"], p["description"], p["body"], robots=p.get("robots", "index,follow")), encoding="utf-8")
        written.append(name)
    (ROOT / "poemes.html").write_text(sommaire_page(), encoding="utf-8"); written.append("poemes.html")
    (ROOT / "le-livre.html").write_text(livre_page(), encoding="utf-8"); written.append("le-livre.html")
    (ROOT / "poemes").mkdir(exist_ok=True)
    for i, (P, e) in enumerate(ALL):
        (ROOT / "poemes" / f'{e["slug"]}.html').write_text(poem_page(i), encoding="utf-8")
    urls = [SITE + "/" + ("" if n == "index.html" else n) for n in written if PAGES.get(n, {}).get("robots", "index").startswith("index")]
    urls += [f'{SITE}/poemes/{e["slug"]}.html' for _, e in ALL]
    sm = ('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
          + "".join(f"  <url><loc>{u}</loc></url>\n" for u in urls) + "</urlset>\n")
    (ROOT / "sitemap.xml").write_text(sm, encoding="utf-8")
    print(f"Pages générées : {len(written)} pages fixes + {len(ALL)} poèmes + sitemap.xml")

if __name__ == "__main__":
    build()
