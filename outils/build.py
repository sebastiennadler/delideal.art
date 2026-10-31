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
VERSION = "20261031c"          # à changer à chaque modification de css/ ou js/
SITE = "https://delideal.art"
NAV = [("index.html", "Accueil"), ("poemes.html", "Poèmes"), ("le-livre.html", "Le livre"),
       ("musique.html", "Musique"), ("soutenir.html", "Soutenir")]
# ("a-propos.html", "À propos") : page retirée du menu le 29/10/2026 à la demande de l'auteur, à réécrire par lui.
PF_AUTEUR = "https://www.poeme-france.com/auteur/delideal/"
TIPEEE = "https://fr.tipeee.com/delidealart"
AMAZON = "https://www.amazon.fr/dp/B0HPXCFGB5"   # fiche Amazon de l’EPUB (0,99 €), en ligne depuis le 31/10/2026 (ASIN B0HPXCFGB5)
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
<meta property="og:image" content="https://delideal.art/partage/carte-2026-10-28.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="Marcher sur un fil — Fragments de sensibilité bipolaire — Delideal, poèmes">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:image" content="https://delideal.art/partage/carte-2026-10-28.png">
<link rel="icon" href="{rel}favicon.svg" type="image/svg+xml">
<link rel="icon" href="{rel}favicon-32.png" sizes="32x32" type="image/png">
<link rel="apple-touch-icon" href="{rel}apple-touch-icon.png">
<link rel="preload" href="{rel}fonts/eb-garamond-latin-400-normal.woff" as="font" type="font/woff" crossorigin>
{head_extra}<link rel="stylesheet" href="{rel}css/style.css?v={v}">
<script defer src="{rel}js/site.js?v={v}"></script>
<script data-goatcounter="https://delideal.goatcounter.com/count" async src="https://gc.zgo.at/count.js"></script>
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
<p>© {year} Delideal — textes écrits depuis 2000, publiés depuis 2014. Tous droits réservés.</p>
<p><a href="{rel}credits.html">Crédits</a> · <a href="{rel}soutenir.html">Soutenir</a> · <a href="{TIPEEE}" rel="noopener">Tipeee</a> · <a href="{rel}mentions-legales.html">Mentions légales</a></p>
</footer>
</body>
</html>
"""

def esc(s):
    return html.escape(s, quote=False)

def nav_html(rel):
    return "\n".join(f'<li><a href="{rel}{href}">{label}</a></li>' for href, label in NAV)

def jsonld_livre():
    """Données structurées (schema.org/Book) pour les moteurs de recherche ; l'offre Amazon s'ajoute dès que le lien existe."""
    import json as _json
    d = {"@context": "https://schema.org", "@type": "Book", "name": FRONT["title"], "alternateName": f'{FRONT["title"]} — {FRONT["subtitle"]}',
         "author": {"@type": "Person", "name": "Delideal", "url": SITE + "/"}, "inLanguage": "fr", "genre": "Poésie",
         "bookFormat": "https://schema.org/EBook", "url": SITE + "/le-livre.html", "image": SITE + "/partage/carte-2026-10-28.png",
         "contributor": {"@type": "Person", "name": "Isabelle Jespersen", "jobTitle": "Préface"},
         "isAccessibleForFree": True, "numberOfPages": pages_pdf("livre/marcher-sur-un-fil.pdf")}
    if AMAZON:
        d["offers"] = {"@type": "Offer", "url": AMAZON, "price": "0.99", "priceCurrency": "EUR", "availability": "https://schema.org/InStock"}
    return '<script type="application/ld+json">' + _json.dumps(d, ensure_ascii=False) + '</script>\n'

def page(name, title, description, body, rel="", robots="index,follow", ogtype="website"):
    canonical = SITE + "/" + ("" if name == "index.html" else name)
    head_extra = jsonld_livre() if name in ("index.html", "le-livre.html") else ""
    return (HEAD.format(title=esc(title), description=esc(description), robots=robots, ogtype=ogtype,
                        canonical=canonical, rel=rel, v=VERSION, nav=nav_html(rel), head_extra=head_extra)
            + body.strip("\n") + "\n"
            + FOOT.format(year=date.today().year, rel=rel, pf=PF_AUTEUR, TIPEEE=TIPEEE))

# ---------------------------------------------------------------- recueil
R = json.loads((ROOT / "outils" / "recueil.json").read_text(encoding="utf-8"))
FRONT, PARTS = R["front"], R["parts"]
for _P in PARTS:                       # les textes marqués "retired" restent dans les données mais ne sont pas publiés
    _P["poems"] = [e for e in _P["poems"] if not e.get("retired")]
ALL = [(P, e) for P in PARTS for e in P["poems"]]
NOMBRES = {49: "Quarante-neuf", 50: "Cinquante", 51: "Cinquante et un", 52: "Cinquante-deux", 53: "Cinquante-trois", 54: "Cinquante-quatre", 55: "Cinquante-cinq", 56: "Cinquante-six", 57: "Cinquante-sept", 58: "Cinquante-huit"}

def pf_url(e):
    return f"https://www.poeme-france.com/auteur/delideal/texte-{e['pf']}" if e.get("pf") else None

MOIS_FR = ["janvier", "février", "mars", "avril", "mai", "juin", "juillet", "août", "septembre", "octobre", "novembre", "décembre"]

def date_longue(d):
    j, m, a = d.split("/")
    return f'{int(j)}{"er" if int(j) == 1 else ""} {MOIS_FR[int(m) - 1]} {a}'

def source_line(e, rel=""):
    """Une ligne discrète sous le poème : la date de première publication, la page d'origine, la copie d'archive."""
    if e.get("pf"):
        wb = f'https://web.archive.org/web/2026/{pf_url(e)}'
        return (f'<p class="source">Publié le {date_longue(e["date"])} sur <a href="{pf_url(e)}" rel="noopener">poème-france</a> · '
                f'<a href="{wb}" rel="noopener">copie d’archive</a></p>')
    return '<p class="source">Inédit : ce texte ne figure que dans le recueil.</p>'

def render_blocks(e):
    kind = e.get("kind", "verse")
    out = []
    if kind == "verse":
        acro = bool(e.get("acrostiche"))
        def vers(l):
            if acro and l and l[0].isalpha():
                return '<strong class="acro-l">' + esc(l[0]) + '</strong>' + esc(l[1:])
            return esc(l)
        for b in e["blocks"]:
            out.append('<p class="strophe">' + "<br>\n".join(vers(l) for l in b) + "</p>")
        return '<div class="poeme' + (' acrostiche' if acro else '') + '">\n' + "\n".join(out) + "\n</div>"
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

NOTE_IA = "Musique et voix générées par intelligence artificielle (Suno). Le texte est intégralement celui de l’auteur, mot pour mot ; les consignes de style et de musique données à l’outil sont aussi les siennes."

def music_block(e, rel=""):
    m = e.get("music")
    if not m:
        return ""
    if m["kind"] == "piano":
        t = (f'{esc(m["label"])} : <a href="{m["yt"]}" rel="noopener">écouter sur YouTube</a> · <a href="{rel}{m["mp3"]}" download>télécharger le mp3</a>.'
             f'<br><audio controls preload="none" src="{rel}{m["mp3"]}" style="width:100%; margin-top:.6rem">Votre navigateur ne lit pas l’audio.</audio>')
    elif m["kind"] == "auteur":
        t = f'Ce poème est aussi une chanson, écrite et chantée par l’auteur : <a href="{m["yt"]}" rel="noopener">{esc(m["label"])}</a>'
        if m.get("yt2"):
            t += f' · <a href="{m["yt2"]}" rel="noopener">{esc(m["label2"])}</a>'
        t += ' (YouTube).'
    else:
        if m.get("mp3") and not m.get("yt"):
            t = (f'{esc(m["label"])}. <span class="etiquette">musique IA</span> {NOTE_IA} '
                 f'<a href="{rel}musique.html#chanson-{e["slug"]}">Les autres musiques</a>.'
                 f'<br><audio controls preload="none" src="{rel}{m["mp3"]}" style="width:100%; margin-top:.6rem">Votre navigateur ne lit pas l’audio.</audio>')
        elif m.get("yt"):
            par = next((mq for mq in MAQUETTES if mq.get("paroles") and e["slug"] in mq["sources"]), None)
            lien_par = f' · <a href="{rel}musique.html#chanson-{par["slug"]}">lire les paroles</a>' if par else ""
            t = (f'{esc(m["label"])} : <a href="{m["yt"]}" rel="noopener">écouter sur YouTube</a>{lien_par}. <span class="etiquette">musique IA</span> '
                 'Texte de l’auteur ; musique et voix générées par intelligence artificielle, pour donner une idée de ce que ce poème pourrait devenir en chanson.')
        else:
            t = f'{esc(m["label"])}. <span class="etiquette">musique IA</span>'
    return f'<p class="musique-ligne">♪ {t}</p>'

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
    if e.get("note_avant"):
        body.append(f'<p class="note-auteur" id="note">{esc(e["note_avant"])}</p>')
    if e.get("note"):
        body.append(f'<p class="note-auteur" id="note">{esc(e["note"])}</p>')
    body.append(music_block(e, rel))
    body.append(source_line(e, rel))
    body.append(partage_html(f'{SITE}/poemes/{e["slug"]}.html', f'« {e["title"]} », un poème de Delideal', "Partager", "Un poème, ça se donne. Si celui-ci vous a touché, passez-le à quelqu’un."))
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
            f'<p class="note">{NOMBRES.get(len(ALL), len(ALL))} textes en six parties, dans l’ordre du recueil.</p>']
    for P in PARTS:
        body.append(f'<section class="partie" id="partie-{P["num"]}">')
        body.append(f'<p class="num-partie">{P["num"]}</p><h2>{esc(P["title"])}</h2>')
        if P.get("chapeau"):
            body.append(f'<p class="chapeau vers">{chapeau_html(P)}</p>')
        body.append('<ol class="liste-poemes deux">')
        for e in P["poems"]:
            tag = ""
            if e.get("music"):
                tag = ' <span class="etiquette">musique</span>' if e["music"]["kind"] != "ia" else ' <span class="etiquette">musique IA</span>'
            body.append(f'<li><a href="poemes/{e["slug"]}.html">{esc(e["title"])}</a>{tag}</li>')
        body.append("</ol></section>")
    return page("poemes.html", "Les poèmes — Delideal",
                "Tous les poèmes du recueil Marcher sur un fil, en six parties, avec leur date de première publication.", "\n".join(body))

def credits_page():
    n_ined = sum(1 for _, e in ALL if not e.get("pf"))
    ined = {0: "", 1: " Un texte est inédit : il ne figure que dans le recueil.", 2: " Deux textes sont inédits : ils ne figurent que dans le recueil."}.get(n_ined, f" {n_ined} textes sont inédits.")
    body = ['<h1 class="titre-fil">Crédits</h1>', '<div class="fil" aria-hidden="true"></div>',
            '<h2>Les textes</h2>',
            '<p>Tous les textes de ce site sont de Delideal. Écrits à partir de l’an 2000, ils ont été publiés entre octobre 2014 et décembre 2023 sur '
            f'<a href="{PF_AUTEUR}" rel="noopener">poeme-france.com</a>, un site tiers qui fixe la date et l’heure de mise en ligne de chaque texte et conserve '
            f'les commentaires des lecteurs de l’époque. Sous chaque poème, une ligne donne sa date de première publication, le lien vers la page d’origine et le lien '
            f'vers sa copie conservée par Internet Archive.{ined}</p>',
            f'<p class="note">La première page de la liste de l’auteur sur poeme-france.com est conservée par Internet Archive depuis <a href="{ARCHIVE}" rel="noopener">septembre 2025</a> ; les pages des textes sont archivées depuis octobre 2026.</p>',
            '<h2>La préface</h2>', '<p>La préface du recueil, un acrostiche, est d’Isabelle Jespersen.</p>',
            '<h2>Les musiques</h2>',
            '<p>« Le cœur assoiffé » et « Re-Pas-Sage » sont des chansons écrites, jouées et chantées par l’auteur, mises en ligne sur YouTube à partir de 2015 ; « Concerto pour hall de gare » et « Rage and Hopes » sont des improvisations au piano jouées et enregistrées par lui. '
            'Les maquettes « Marcher sur un fil », « Ma muse onirique », « Méditations » et « Âme rebelle » (2026) ont été produites avec des outils d’intelligence artificielle sur ses textes, mot pour mot, à partir de consignes de style écrites par lui : elles sont présentées comme telles. '
            'Toutes sont réunies, avec leurs textes, sur la page <a href="musique.html">Musique</a>.</p>',
            '<h2>Le livre</h2>',
            f'<p>Le recueil existe en PDF (à lire, à imprimer) sur <a href="le-livre.html">la page du livre</a>, et en EPUB <a href="{AMAZON}" rel="noopener">sur Amazon</a>.</p>']
    return page("credits.html", "Crédits — Delideal", "Crédits des textes, de la préface et des musiques de Delideal ; dates et sources de chaque texte.", "\n".join(body))

def taille(path):
    f = ROOT / path
    return (f"{f.stat().st_size / 1e6:.1f} Mo").replace(".", ",") if f.exists() else ""

def pages_pdf(path):
    try:
        from pypdf import PdfReader
        return len(PdfReader(str(ROOT / path)).pages)
    except Exception:
        return None

def telecharger_html(rel=""):
    pdf, imp, epub = "livre/marcher-sur-un-fil.pdf", "livre/marcher-sur-un-fil-impression.pdf", "livre/marcher-sur-un-fil.epub"
    n = pages_pdf(pdf)
    return (f'<p>Le recueil complet, tel qu’il se lit ici :</p><ul class="liens">'
            f'<li><a href="{rel}{pdf}">PDF à lire sur écran</a> — {n} pages, liens actifs vers les chansons, les musiques et les sources ({taille(pdf)})</li>'
            f'<li><a href="{rel}{imp}">PDF à imprimer</a> — format A5, recto-verso, prêt pour l’impression ({taille(imp)})</li>'
            f'</ul>')

def chapeau_html(P):
    return "<br>\n".join(esc(l) for l in P.get("chapeau", "").split("\n"))

MAQUETTES = R.get("maquettes", [])
TITRES = {e["slug"]: e["title"] for _, e in ALL}

CHANSONS = R.get("chansons", [])

def paroles_blocs(secs):
    """Paroles en strophes ; les marqueurs Suno (Verse, Chorus…) ne sont pas affichés, les titres des méditations le sont."""
    out = []
    for sec in secs:
        suno = sec["label"].split()[0].lower() in ("strophe", "refrain", "pont", "couplet", "intro", "outro", "verse", "chorus", "bridge")
        if not suno and len(secs) > 1:
            out.append(f'<p class="paroles-label">{esc(sec["label"])}</p>')
        strophe = []
        for ln in sec["lines"]:
            if ln.strip() == "":
                if strophe: out.append('<p class="strophe">' + "<br>".join(strophe) + '</p>'); strophe = []
            else:
                strophe.append(esc(ln))
        if strophe: out.append('<p class="strophe">' + "<br>".join(strophe) + '</p>')
    return "".join(out)

def chanson_bloc(slug, titre, etiquette, ecoute, origine, paroles_html=None, renvoi=None, note=None, audio=None):
    """Un bloc par chanson : titre, nature, écoute, origine, puis le texte complet (ou le renvoi au poème)."""
    h = [f'<article class="chanson" id="chanson-{slug}"><h3>{esc(titre)}</h3>',
         f'<p class="chanson-meta">{etiquette} · {ecoute}' + (f' · {origine}' if origine else "") + '</p>']
    if audio:
        h.append(f'<audio controls preload="none" src="{audio}" style="width:100%; margin:.4rem 0 .6rem">Votre navigateur ne lit pas l’audio : <a href="{audio}">télécharger le mp3</a>.</audio>')
    if note:
        h.append(f'<p class="note-auteur">{esc(note)}</p>')
    if paroles_html:
        h.append(f'<details class="paroles" open><summary>Le texte</summary><div class="paroles-texte">{paroles_html}</div></details>')
    elif renvoi:
        h.append(f'<p class="chanson-texte-renvoi">Le texte : {renvoi}</p>')
    h.append('</article>')
    return "".join(h)

def musique_blocs():
    by = {e["slug"]: e for _, e in ALL}
    def lien(sl):
        e = by.get(sl); return f'<a href="poemes/{sl}.html">{esc(e["title"])}</a>' if e else esc(sl)
    yt = lambda u, t="écouter sur YouTube": f'<a href="{u}" rel="noopener">{t}</a>'
    out = []
    # 1. chansons de l'auteur
    out.append('<h2 id="chansons">Chansons</h2><p>Écrites, jouées et chantées par moi, en amateur, sur <a href="https://www.youtube.com/@delideal" rel="noopener">ma chaîne YouTube</a>. Les paroles sont les poèmes, mot pour mot.</p>')
    for _, e in ALL:
        m = e.get("music")
        if m and m["kind"] == "auteur":
            ecoute = yt(m["yt"]) + (f' · {yt(m["yt2"], esc(m["label2"]).lower())}' if m.get("yt2") else "")
            out.append(chanson_bloc(e["slug"], e["title"], "Chanson de l’auteur", ecoute, "", paroles_html=render_blocks(e).replace('class="poeme', 'class="poeme paroles-poeme'), note=None))
    for c in CHANSONS:
        origine = "texte inédit" if c.get("inedit") else f'texte publié sur <a href="{PF_AUTEUR}texte-{c["pf"]}" rel="noopener">poème-france</a> le {date_longue(c["date"])}'
        out.append(chanson_bloc(c["slug"], c["title"], "Chanson de l’auteur", yt(c["yt"]), origine,
                                paroles_html=paroles_blocs(c["paroles"]) if c.get("paroles") else None, note=c.get("note")))
    # 2. maquettes IA
    out.append('<h2 id="maquettes">Maquettes <span class="etiquette">musique IA</span></h2>'
               '<p>Ces chansons ont été produites avec des outils d’intelligence artificielle : les paroles sont les miennes, assemblées à partir de mes poèmes, '
               'et les consignes de style aussi ; la musique et la voix sont générées. Ce sont des maquettes, une façon d’entendre ce que ces textes pourraient devenir en chanson. '
               'Si vous êtes musicienne ou musicien et qu’un de ces textes vous parle, <a href="soutenir.html">écrivez-moi</a> : l’idée est qu’un jour elles soient jouées et chantées par des humains.</p>')
    for mq in MAQUETTES:
        n = len(mq["sources"])
        origine = ("sur le texte intégral de " if n == 1 else "à partir de deux textes : " if n == 2 else "à partir de trois textes : ") + ", ".join(lien(sl) for sl in mq["sources"])
        ecoute = yt(mq["yt"]) if mq.get("yt") else "à écouter ci-dessous"
        src_e = by.get(mq["sources"][0]) if n == 1 else None
        paroles = paroles_blocs(mq["paroles"]) if mq.get("paroles") else (render_blocks(src_e).replace('class="poeme', 'class="poeme paroles-poeme') if src_e else None)
        note = None
        if mq.get("note") and src_e and src_e.get("note"):
            note = src_e["note"]
        out.append(chanson_bloc(mq["slug"], mq["title"], 'Maquette <span class="etiquette">musique IA</span>', ecoute, origine, paroles_html=paroles, note=note,
                                audio=mq.get("mp3")))
        if mq.get("mp3"):
            out[-1] = out[-1].replace('</article>', f'<p class="source"><a href="{mq["mp3"]}" download>Télécharger le mp3</a> ({mq.get("duree", "")}, {taille(mq["mp3"])}).</p></article>')
    # 3. piano
    out.append('<h2 id="piano">Au piano</h2>')
    for _, e in ALL:
        m = e.get("music")
        if m and m["kind"] == "piano":
            out.append(f'<article class="chanson" id="chanson-{e["slug"]}"><h3>{esc(e["title"])}</h3>'
                       f'<p class="chanson-meta">Improvisation au piano, jouée et enregistrée par moi-même · {yt(m["yt"])} · <a href="{m["mp3"]}" download>télécharger le mp3</a> (5 min 34, {taille(m["mp3"])})</p>'
                       f'<audio controls preload="none" src="{m["mp3"]}" style="width:100%; margin:.4rem 0 .6rem">Votre navigateur ne lit pas l’audio.</audio>'
                       f'<p class="chanson-texte-renvoi">Le poème du même nom raconte ce moment : {lien(e["slug"])}.</p></article>')
    out.append('<article class="chanson" id="chanson-rage-and-hopes"><h3>Rage and Hopes</h3>'
               '<p class="chanson-meta">Improvisation au piano, brouillonne et sincère, douze minutes jouées d’une traite · <a href="https://www.youtube.com/watch?v=QFCULzpDsJk" rel="noopener">écouter sur YouTube</a></p></article>')
    return "".join(out)

def chansons_accueil():
    """Liste courte des chansons pour l'accueil : titre, nature, écoute."""
    by = {e["slug"]: e for _, e in ALL}
    items = []
    for _, e in ALL:
        m = e.get("music")
        if m and m["kind"] == "auteur":
            items.append(f'<li><a href="musique.html#chanson-{e["slug"]}">{esc(e["title"])}</a> <span class="annee">chanson de l’auteur</span></li>')
    for c in CHANSONS:
        items.append(f'<li><a href="musique.html#chanson-{c["slug"]}">{esc(c["title"])}</a> <span class="annee">chanson de l’auteur</span></li>')
    for mq in MAQUETTES:
        items.append(f'<li><a href="musique.html#chanson-{mq["slug"]}">{esc(mq["title"])}</a> <span class="etiquette">musique IA</span></li>')
    items.append('<li><a href="musique.html#piano">Concerto pour hall de gare</a> <span class="annee">improvisation au piano</span></li>')
    return '<ul class="liste-poemes deux chansons-accueil">' + "".join(items) + '</ul>'

def partage_html(url, texte, label="Partager", mot=""):
    """Liens de partage sans script tiers ni traceur : simples adresses de partage des réseaux."""
    from urllib.parse import quote
    u, t = quote(url, safe=""), quote(texte, safe="")
    intro = f'<span class="partage-mot">{mot}</span> ' if mot else ""
    return (f'<p class="partage">{intro}<span class="partage-label">{label} :</span> '
            f'<a href="https://www.facebook.com/sharer/sharer.php?u={u}" rel="noopener" target="_blank">Facebook</a> · '
            f'<a href="https://wa.me/?text={t}%20{u}" rel="noopener" target="_blank">WhatsApp</a> · '
            f'<a href="https://twitter.com/intent/tweet?text={t}&url={u}" rel="noopener" target="_blank">X</a> · '
            f'<a href="mailto:?subject={t}&body={t}%0A{u}">courriel</a> · '
            f'<a href="#" class="copier" data-url="{esc(url)}">copier le lien</a></p>')

def premiere_phrase(t):
    import re as _re
    m = _re.match(r"(.+?[.!?])(\s|$)", t)
    return m.group(1) if m else t

def preface_html():
    return "".join(f'<span class="acro"><strong>{esc(l[0])}</strong>{esc(l[1:])}</span>' for l in FRONT["preface"]["lines"])

def sommaire_livre_html(rel=""):
    out = ['<ol class="sommaire-livre">']
    for P in PARTS:
        out.append(f'<li><span class="num">{P["num"]}</span><span class="titre"><a href="{rel}poemes.html#partie-{P["num"]}">{esc(P["title"])}</a></span>'
                   f'<span class="teaser">{esc(P.get("chapeau", "").split(chr(10))[0])}</span></li>')
    out.append('</ol>')
    return "".join(out)

def cartes_html(rel=""):
    pdf, imp = "livre/marcher-sur-un-fil.pdf", "livre/marcher-sur-un-fil-impression.pdf"
    n = pages_pdf(pdf)
    if AMAZON:
        epub = f'<a class="carte" href="{AMAZON}" rel="noopener"><strong>EPUB · 0,99 €</strong><span>Le prix d’un café, pour des heures d’écriture · Kindle, liseuses et téléphones, sur Amazon</span></a>'
    else:
        epub = '<span class="carte carte-attente"><strong>EPUB · 0,99 €</strong><span>Bientôt sur Amazon, pour Kindle, liseuses et téléphones</span></span>'
    return (f'<div class="cartes">'
            f'<a class="carte" href="{rel}{pdf}"><strong>PDF à lire</strong><span>{n} pages, liens vers les chansons, les musiques et les sources · {taille(pdf)}</span></a>'
            f'<a class="carte" href="{rel}{imp}"><strong>PDF à imprimer</strong><span>Format A5, recto-verso, prêt pour l’impression · {taille(imp)}</span></a>'
            f'{epub}</div>')

def livre_page():
    pref = preface_html()
    body = [f'<h1 class="titre-fil">{esc(FRONT["title"])}</h1>', '<div class="fil" aria-hidden="true"></div>',
            f'<p class="sous-titre">{esc(FRONT["subtitle"])}</p>',
            '<p>Des textes écrits depuis l’an 2000, publiés entre 2014 et 2023, rassemblés en six parties. Il cherche un éditeur ; en attendant, il se lit ici en entier, se télécharge en PDF, et existe en EPUB pour liseuses, <a href="' + AMAZON + '" rel="noopener">sur Amazon à 0,99 €</a> — le prix d’un café, pour des heures d’écriture.</p>', cartes_html(),
            '<section class="panel"><h2>Dédicace</h2>', f'<p class="dedicace">{esc(FRONT["dedicace"])}</p>', '</section>',
            '<section class="panel"><h2>Préface</h2>', f'<p class="preface">{pref}</p>', f'<p class="signature">{esc(FRONT["preface"]["sign"])}</p>', '</section>',
            '<section class="panel"><h2>Exergue</h2>']
    for l in FRONT["ouverture"]:
        body.append(f'<p class="citation">{esc(l)}</p>')
    body.append('</section>')
    body.append('<h2>Les six parties</h2><ol class="liste-poemes parties">')
    for P in PARTS:
        body.append(f'<li><a href="poemes.html#partie-{P["num"]}">{P["num"]}. {esc(P["title"])}</a> <span class="annee">{len(P["poems"])} textes</span></li>')
    body.append('</ol>')
    body.append('<p><a href="poemes.html">Commencer la lecture</a> · <a href="soutenir.html">Soutenir l’édition du livre</a></p>')
    body.append(partage_html(f'{SITE}/le-livre.html', "Marcher sur un fil, le recueil de Delideal", "Partager", "Un livre qui n’est pas encore imprimé se transmet comme ça : de main en main."))
    return page("le-livre.html", "Le livre — Marcher sur un fil",
                "Marcher sur un fil, fragments de sensibilité bipolaire : le recueil de Delideal, préface d’Isabelle Jespersen.", "\n".join(body))

# ---------------------------------------------------------------- pages fixes
first = ALL[0][1]
TITRE = [e for _, e in ALL if e["slug"] == "marcher-sur-un-fil"][0]
PAGES = {
"index.html": dict(
  title="Delideal — Marcher sur un fil, poèmes",
  description="Marcher sur un fil, fragments de sensibilité bipolaire : les poèmes de Delideal, écrits depuis 2000, en lecture libre, à télécharger en PDF ; en EPUB sur Amazon.",
  body=f"""
<header class="couv">
<p class="marque">Delideal · poèmes</p>
<h1>Marcher sur un fil</h1>
<div class="fil" aria-hidden="true"></div>
<p class="sous-titre">{esc(FRONT["subtitle"])}</p>
</header>

<section class="ouverture-poeme">
<p class="etiquette-section">Préface</p>
<p class="preface">{preface_html()}</p>
<p class="signature">{esc(FRONT["preface"]["sign"])}, préface</p>
</section>

<section class="ouverture-poeme">
<p class="etiquette-section">Ouverture</p>
<div class="poeme">
<p class="strophe">{"<br>".join(esc(l) for l in TITRE["blocks"][0])}</p>
</div>
<p class="source">Début de « <a href="poemes/marcher-sur-un-fil.html">Marcher sur un fil</a> », le poème qui donne son titre au recueil.</p>
</section>

<p class="intro-site">Des poèmes écrits à partir de l’an 2000, publiés entre 2014 et 2023, rassemblés en six parties. À lire ici, librement, ou à emporter.</p>

<h2>Les six parties</h2>
{sommaire_livre_html()}
<p class="entrees">Pour entrer par le début : <a href="poemes/{first["slug"]}.html">{esc(first["title"])}</a>. Par le cœur : <a href="poemes/marcher-sur-un-fil.html">Marcher sur un fil</a> ou <a href="poemes/dsm-story.html">DSM Story</a>. Par la musique : <a href="musique.html">les chansons et leurs textes</a>.</p>

<h2>Les chansons</h2>
<p>Plusieurs de ces poèmes se chantent. Leurs textes et les liens pour les écouter sont sur la page <a href="musique.html">Musique</a>.</p>
{chansons_accueil()}

<h2>Emporter</h2>
{cartes_html()}

<h2>Soutenir</h2>
<p>Ce site est gratuit et le restera. Le recueil existe aussi en livre numérique, <a href="{AMAZON}" rel="noopener">sur Amazon à 0,99 €</a> : le prix d’un café, pour des heures d’écriture, afin que personne n’ait à choisir entre lire et payer. Le site, le matériel pour la musique, les heures : tout cela a un coût, et le premier but est de rentrer dans mes frais. Si quelques textes vous touchent, vous pouvez aider, proposer de les mettre en musique ou en images, ou simplement m’écrire.</p>
<p class="soutien"><a class="bouton" href="{TIPEEE}" rel="noopener">Soutenir sur Tipeee</a> <a href="soutenir.html">Éditeurs, musiciens, illustrateurs, vidéastes, contact</a></p>
{partage_html(SITE, "Marcher sur un fil, les poèmes de Delideal", "Partager", "Ce site n’a ni publicité ni algorithme : il va de main en main. Si ces poèmes vous ont touché, envoyez-les à une personne.")}
"""),
"musique.html": dict(
  title="Musique — Delideal",
  description="Les chansons et musiques de Delideal, avec leurs textes : chansons écrites et chantées par l’auteur, maquettes, improvisations au piano.",
  body=f"""
<h1 class="titre-fil">Musique</h1>
<div class="fil" aria-hidden="true"></div>
<p class="intro-site">Plusieurs textes de <em>Marcher sur un fil</em> sont devenus des chansons. Les voici toutes, avec leurs textes et les liens pour les écouter : <a href="#chansons">les chansons</a>, <a href="#maquettes">les maquettes</a>, <a href="#piano">le piano</a>.</p>
{musique_blocs()}
"""),
"soutenir.html": dict(
  title="Soutenir — Delideal",
  description="Soutenir le travail de Delideal : contributions, éditeurs, musiciens, illustrateurs, vidéastes.",
  body=f"""
<h1 class="titre-fil">Soutenir</h1>
<div class="fil" aria-hidden="true"></div>
<p>Écrire, publier, mettre en musique : tout cela prend du temps et un peu d’argent — le site et son nom de domaine, le matériel pour enregistrer, les heures. Ce site est gratuit et sans publicité, et il le restera. Le premier but est simple : rentrer dans mes frais. Voici cinq façons d’aider.</p>
<h2>Contribuer</h2>
<p>Un don, ponctuel ou mensuel, sur Tipeee, plateforme française dédiée aux créateurs. Il sert à faire vivre ce site, à continuer d’écrire, et à réunir les moyens de publier le recueil <em>Marcher sur un fil</em> en vrai livre.</p>
<p><a class="bouton" href="{TIPEEE}" rel="noopener">Soutenir Delideal sur Tipeee</a></p>
<p>Le recueil existe aussi en livre numérique, <a href="{AMAZON}" rel="noopener">sur Amazon à 0,99 €</a> : le prix d’un café, pour des heures d’écriture, afin que personne n’ait à choisir entre lire et payer. Si vous voulez aider davantage, ce n’est pas en l’achetant deux fois : sur Tipeee, votre don m’arrive presque entier, là où une librairie en ligne en garde les deux tiers.</p>
<h2>Éditer</h2>
<p>Je cherche une maison d’édition pour le recueil. Le manuscrit est prêt, préfacé, et se lit en entier sur ce site. Écrivez-moi : <a class="courriel" data-u="sebastien.nadler" data-d="gmail.com" href="#">sebastien.nadler [at] gmail.com</a>.</p>
<h2>Mettre en musique</h2>
<p>Plusieurs poèmes sont déjà des chansons, d’autres n’existent qu’en maquette : la page <a href="musique.html">Musique</a> montre la direction. Si vous êtes musicienne ou musicien et qu’un texte vous parle, même adresse.</p>
<h2>Faire connaître</h2>
<p>Le plus simple, et ce qui compte le plus : faire lire. Un lien envoyé à une personne vaut mieux qu’une publicité.</p>
{partage_html(SITE, "Marcher sur un fil, les poèmes de Delideal", "Partager", "Une personne à qui vous l’envoyez, c’est déjà beaucoup.")}
<h2>Illustrer, filmer</h2>
<p>Ce site est volontairement sans image. Le livre, lui, pourrait en avoir : dessin, peinture, gravure, photographie. Et les chansons mériteraient des clips. Si vous illustrez, si vous filmez ou montez des images, et qu’un texte ou une musique vous inspire, écrivez-moi, même adresse — on en parle, sans engagement de part et d’autre.</p>
"""),
"404.html": dict(
  title="Page introuvable — Delideal", robots="noindex,nofollow",
  description="Cette page n’existe pas ou plus.",
  body="""
<h1 class="titre-fil">Page introuvable</h1>
<div class="fil" aria-hidden="true"></div>
<p>Cette page n’existe pas, ou n’existe plus : quelques textes ont changé de place quand le recueil a retrouvé sa forme.</p>
<p>Pour retrouver votre chemin : <a href="/">l’accueil</a>, <a href="/poemes.html">le sommaire des poèmes</a>, <a href="/le-livre.html">le livre</a>, <a href="/musique.html">la musique</a>.</p>
"""),
"mentions-legales.html": dict(
  title="Mentions légales — Delideal", robots="noindex,follow",
  description="Mentions légales du site delideal.art.",
  body="""
<h1 class="titre-fil">Mentions légales</h1>
<div class="fil" aria-hidden="true"></div>
<h2>Éditeur</h2>
<p>Ce site est édité à titre non professionnel par son auteur, qui publie sous le nom de Delideal ; comme la loi le permet pour un éditeur non professionnel, son identité est connue de l’hébergeur. Contact : <a class="courriel" data-u="sebastien.nadler" data-d="gmail.com" href="#">sebastien.nadler [at] gmail.com</a>.</p>
<h2>Hébergement</h2>
<p>GitHub Pages — GitHub, Inc., 88 Colin P. Kelly Jr. Street, San Francisco, CA 94107, États-Unis.</p>
<h2>Propriété intellectuelle</h2>
<p>Tous les textes et musiques sont l’œuvre de leur auteur et protégés par le droit d’auteur. Toute reproduction sans accord écrit est interdite, à l’exception de la citation courte avec mention de la source.</p>
<h2>Données personnelles</h2>
<p>Ce site ne dépose aucun cookie. Les polices, les musiques et les images sont servies par le site lui-même. La seule ressource extérieure est un compteur de fréquentation, <a href="https://www.goatcounter.com/" rel="noopener">GoatCounter</a>, qui compte les pages vues sans cookie ni identifiant, sans suivre les visiteurs d’un site à l’autre et sans conserver d’adresse IP : il n’y a donc pas de bandeau de consentement à afficher. Le choix du thème clair ou sombre est mémorisé dans votre navigateur uniquement. Les liens vers YouTube, Tipeee, Amazon ou les réseaux sociaux mènent vers ces services, qui appliquent leurs propres règles.</p>
"""),
}

def build():
    written = []
    for name, p in PAGES.items():
        (ROOT / name).write_text(page(name, p["title"], p["description"], p["body"], robots=p.get("robots", "index,follow")), encoding="utf-8")
        written.append(name)
    (ROOT / "poemes.html").write_text(sommaire_page(), encoding="utf-8"); written.append("poemes.html")
    (ROOT / "le-livre.html").write_text(livre_page(), encoding="utf-8"); written.append("le-livre.html")
    (ROOT / "credits.html").write_text(credits_page(), encoding="utf-8"); written.append("credits.html")
    (ROOT / "poemes").mkdir(exist_ok=True)
    for i, (P, e) in enumerate(ALL):
        (ROOT / "poemes" / f'{e["slug"]}.html').write_text(poem_page(i), encoding="utf-8")
    # pages orphelines (textes retirés) : supprimées si possible, sinon signalées
    keep = {f'{e["slug"]}.html' for _, e in ALL}
    for f in (ROOT / "poemes").glob("*.html"):
        if f.name not in keep:
            try:
                f.unlink(); print("page retirée :", f.name)
            except OSError:
                print("page orpheline à déplacer à la main :", f.name)
    urls = [SITE + "/" + ("" if n == "index.html" else n) for n in written if PAGES.get(n, {}).get("robots", "index").startswith("index")]
    urls += [f'{SITE}/poemes/{e["slug"]}.html' for _, e in ALL]
    sm = ('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
          + "".join(f"  <url><loc>{u}</loc></url>\n" for u in urls) + "</urlset>\n")
    (ROOT / "sitemap.xml").write_text(sm, encoding="utf-8")
    print(f"Pages générées : {len(written)} pages fixes + {len(ALL)} poèmes + sitemap.xml")

if __name__ == "__main__":
    build()
