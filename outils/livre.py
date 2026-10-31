#!/usr/bin/env python3
"""
livre.py — fabrique le recueil téléchargeable à partir des mêmes données que le site
(outils/recueil.json) : deux PDF (écran, A5 imprimable) et, hors dépôt, l'EPUB vendu sur Amazon.

    python3 outils/livre.py            # écrit livre/marcher-sur-un-fil.pdf et .epub

Le PDF est mis en page par Chromium (Playwright) à partir d'un HTML : sommaire paginé
en deux passes, pages blanches insérées pour que chaque partie commence à droite,
signets. L'EPUB 3 est assemblé à la main (un fichier par texte, sommaire dans le flux,
NCX, vers en paragraphes à retrait suspendu, aucune police embarquée : voir make_epub). Aucun texte n'est ajouté : tout vient de recueil.json
et des phrases déjà publiées sur le site.
"""
import datetime, io, re, sys, uuid, zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build as B  # réutilise les données et esc()

ROOT = B.ROOT
FRONT, PARTS, ALL = B.FRONT, B.PARTS, B.ALL
esc = B.esc
OUT = ROOT / "livre"
FONTS = ROOT / "outils" / "fonts"
FONT_FILES = {("400", "normal"): "eb-garamond-latin-400-normal.woff",
              ("400", "italic"): "eb-garamond-latin-400-italic.woff",
              ("500", "normal"): "eb-garamond-latin-500-normal.woff",
              ("500", "italic"): "eb-garamond-latin-500-italic.woff"}
ANNEE = datetime.date.today().year
SITE = "https://delideal.art"
TIPEEE = "https://fr.tipeee.com/delidealart"
MODE = {"liens": True, "amazon": False}   # liens : actifs (écran, EPUB) ou non (imprimable) ; amazon : version vendue 0,99 €
PRIX_AMAZON = ('<p>Ce livre coûte 0,99 € : le prix d’un café, pour des heures d’écriture, afin que personne n’ait à choisir entre lire et payer. '
               'Il se lit aussi gratuitement sur delideal.art. Le site, le matériel pour la musique, les heures : tout cela a un coût, et le premier but est de rentrer dans mes frais. '
               'Si vous voulez aider davantage, ce n’est pas en l’achetant deux fois : sur Tipeee, votre don m’arrive presque entier, là où une librairie en ligne en garde les deux tiers. '
               'Chacun fait comme il peut. Lire, c’est déjà beaucoup.</p>')
MOIS = ["janvier", "février", "mars", "avril", "mai", "juin", "juillet", "août",
        "septembre", "octobre", "novembre", "décembre"][datetime.date.today().month - 1]

# ------------------------------------------------------------------ textes communs
# (phrases déjà en ligne sur le site ; rien de nouveau n'est écrit ici)
COLOPHON = (f'<p>{esc(FRONT["title"])} — {esc(FRONT["subtitle"])}</p>'
            '<p>Textes de Delideal, écrits à partir de l’an 2000, publiés entre 2014 et 2023 '
            'sur poeme-france.com. Préface d’Isabelle Jespersen.</p>'
            f'<p>Édition numérique établie par l’auteur à partir du site delideal.art, {MOIS} {ANNEE}. '
            'Caractère : EB Garamond.</p>'
            f'<p>© {ANNEE} Delideal. Tous droits réservés. Lecture libre ; pour soutenir l’auteur : delideal.art/soutenir.html</p>')
def sources_pdf_html():
    """Sources (PDF) : trois paragraphes ; le détail est sous chaque poème et sur delideal.art/credits.html."""
    n_ined = sum(1 for P in PARTS for e in P["poems"] if not e.get("pf"))
    mots = {0: "", 1: " Un texte est inédit.", 2: " Deux textes sont inédits."}.get(n_ined, f" {n_ined} textes sont inédits.")
    lien = f'<a href="{SITE}/credits.html">delideal.art/credits.html</a>' if MODE["liens"] else 'delideal.art/credits.html'
    return ('<p>Tous les textes de ce livre sont de Delideal. Écrits à partir de l’an 2000, ils ont été publiés entre octobre 2014 et décembre 2023 '
            'sur poeme-france.com, un site tiers qui fixe la date de mise en ligne de chaque texte et conserve les commentaires des lecteurs de l’époque. '
            f'Sous chaque texte, une ligne donne sa date de première publication, sa page d’origine et sa copie conservée par Internet Archive.{mots}</p>'
            f'<p>Les mêmes dates et copies d’archive sont réunies sur {lien}.</p>'
            '<p>La préface du recueil, un acrostiche, est d’Isabelle Jespersen.</p>')

def fin_html():
    if MODE.get("amazon"):
        return (PRIX_AMAZON.replace('sur Tipeee', f'sur <a href="{TIPEEE}">Tipeee</a>').replace('sur delideal.art', f'sur <a href="{SITE}">delideal.art</a>')
                + f'<p>Ce recueil cherche un éditeur. Vous pouvez aussi proposer à l’auteur de mettre un texte en musique, ou lui écrire : '
                f'l’adresse est sur <a href="{SITE}/soutenir.html">delideal.art/soutenir.html</a>.</p>'
                f'<p>Toutes les façons d’aider — un don, une maison d’édition, des musiciens, des illustrateurs, des vidéastes — sont réunies sur '
                f'<a href="{SITE}/soutenir.html">delideal.art/soutenir.html</a>.</p>'
                f'<p>Les musiques : <a href="{SITE}/musique.html">delideal.art/musique.html</a>. Les dates, sources et copies d’archive : '
                f'<a href="{SITE}/credits.html">delideal.art/credits.html</a>.</p>')
    if MODE["liens"]:
        return (f'<p>Ce livre se lit gratuitement, texte par texte, sur <a href="{SITE}">delideal.art</a>. Il cherche un éditeur.</p>'
                f'<p>Si quelques textes vous touchent, vous pouvez soutenir l’auteur par un don, ponctuel ou mensuel, sur '
                f'<a href="{TIPEEE}">Tipeee</a>, lui proposer de mettre un texte en musique, ou lui écrire : '
                f'<a href="mailto:sebastien.nadler@gmail.com">sebastien.nadler@gmail.com</a>.</p>'
                f'<p>Toutes les façons d’aider — un don, une maison d’édition, des musiciens, des illustrateurs, des vidéastes — sont réunies sur '
                f'<a href="{SITE}/soutenir.html">delideal.art/soutenir.html</a>.</p>'
                f'<p>Les musiques : <a href="{SITE}/musique.html">delideal.art/musique.html</a>. Les dates, sources et copies d’archive : '
                f'<a href="{SITE}/credits.html">delideal.art/credits.html</a>.</p>')
    return ('<p>Ce livre se lit gratuitement, texte par texte, sur delideal.art. Il cherche un éditeur.</p>'
            '<p>Si quelques textes vous touchent, vous pouvez soutenir l’auteur par un don, ponctuel ou mensuel, sur Tipeee '
            '(fr.tipeee.com/delidealart), lui proposer de mettre un texte en musique, ou lui écrire : sebastien.nadler@gmail.com.</p>'
            '<p>Toutes les façons d’aider — un don, une maison d’édition, des musiciens, des illustrateurs, des vidéastes — sont réunies sur delideal.art/soutenir.html.</p>'
            '<p>Les musiques : delideal.art/musique.html. Les dates, sources et copies d’archive : delideal.art/credits.html.</p>')

def music_html(e):
    """Bloc « En musique » sous un poème : liens actifs en mode écran, mention simple en impression."""
    m = e.get("music")
    if not m:
        return ""
    if MODE["liens"]:
        if m["kind"] == "piano":
            t = (f'{esc(m["label"])} : <a href="{m["yt"]}">écouter sur YouTube</a> · '
                 f'<a href="{SITE}/{m["mp3"]}">télécharger le mp3</a>.')
        elif m["kind"] == "auteur":
            t = f'Ce poème est aussi une chanson, écrite et chantée par l’auteur : <a href="{m["yt"]}">écouter sur YouTube</a>'
            if m.get("yt2"):
                t += f' · <a href="{m["yt2"]}">{esc(m["label2"]).lower()}</a>'
            t += '.'
        elif m.get("mp3") and not m.get("yt"):
            t = (f'{esc(m["label"])} : <a href="{SITE}/musique.html#maquette-{e["slug"]}">écouter sur delideal.art</a>. '
                 'Musique et voix générées par intelligence artificielle ; le texte, mot pour mot, et les consignes de style sont de l’auteur.')
        else:
            t = (f'{esc(m["label"])} : <a href="{m["yt"]}">écouter sur YouTube</a>. '
                 'Musique et voix générées par intelligence artificielle sur le texte de l’auteur : une maquette, pour donner une idée de ce que ce poème pourrait devenir en chanson.')
    else:
        if m["kind"] == "piano":
            t = f'{esc(m["label"])} — à écouter sur delideal.art/musique.html.'
        elif m["kind"] == "auteur":
            t = 'Ce poème est aussi une chanson, écrite et chantée par l’auteur — delideal.art/musique.html.'
        else:
            t = f'{esc(m["label"])}, musique et voix générées par intelligence artificielle sur le texte de l’auteur — delideal.art/musique.html.'
    return f'<p class="musique">♪ {t}</p>'

# ------------------------------------------------------------------ rendu des textes
def verses_html(e, br):
    """Même logique que build.render_blocks, mais chaque vers est un bloc (retrait suspendu)."""
    kind = e.get("kind", "verse")
    out = []
    if kind == "verse":
        acro = bool(e.get("acrostiche"))
        def vers(l):
            if acro and l and l[0].isalpha():
                return '<strong class="acro-l">' + esc(l[0]) + '</strong>' + esc(l[1:])
            return esc(l)
        for b in e["blocks"]:
            out.append('<p class="strophe">' + "".join(f'<span class="v">{vers(l)}</span>' for l in b) + '</p>')
        return '<div class="poeme' + (' acrostiche' if acro else '') + '">' + "".join(out) + '</div>'
    if kind == "prose":
        for b in e["blocks"]:
            for l in b:
                out.append('<p>' + esc(l) + '</p>')
        return '<div class="prose">' + "".join(out) + '</div>'
    if kind == "theatre":
        for b in e["blocks"]:
            for l in b:
                t = l.strip()
                if t.startswith("Acte ") or t in ("Introduction", "Conclusion") or t.startswith("Suite et Fin"):
                    out.append(f'<h3>{esc(t)}</h3>')
                elif t.startswith("Scène "):
                    out.append(f'<h4>{esc(t)}</h4>')
                elif t.startswith("(") and t.endswith(")"):
                    out.append(f'<p class="didascalie">{esc(t)}</p>')
                elif t.endswith(":") and len(t) < 40:
                    out.append(f'<p class="personnage">{esc(t)}</p>')
                else:
                    out.append(f'<p class="replique">{esc(t)}</p>')
        return '<div class="theatre">' + "".join(out) + '</div>'
    raise ValueError(kind)

def poem_html(e, br):
    h = [f'<h2>{esc(e["title"])}</h2><div class="fil"></div>']
    if e.get("dedicace"):
        h.append(f'<p class="sous-titre">{esc(e["dedicace"])}</p>')
    h.append(verses_html(e, br))
    if e.get("note_avant"):
        h.append(f'<p class="note-auteur">{esc(e["note_avant"])}</p>')
    if e.get("note"):
        h.append(f'<p class="note-auteur">{esc(e["note"])}</p>')
    h.append(music_html(e))
    h.append(source_html(e))
    return "".join(h)

def source_html(e):
    """Ligne discrète : date de première publication, page d'origine, copie d'archive (liens actifs en mode écran)."""
    if not e.get("pf"):
        return '<p class="source">Inédit : ce texte ne figure que dans le recueil.</p>'
    d = B.date_longue(e["date"]); u = B.pf_url(e); wb = f'https://web.archive.org/web/2026/{u}'
    if MODE["liens"]:
        return f'<p class="source">Publié le {d} sur <a href="{u}">poème-france</a> · <a href="{wb}">copie d’archive</a></p>'
    return f'<p class="source">Publié le {d} sur poème-france (texte n° {e["pf"]}).</p>'

def preface_html():
    lines = "".join(f'<span class="acro"><strong>{esc(l[0])}</strong>{esc(l[1:])}</span>' for l in FRONT["preface"]["lines"])
    return f'<p class="preface">{lines}</p><p class="signature">{esc(FRONT["preface"]["sign"])}</p>'

def sources_table():
    rows = []
    for P in PARTS:
        rows.append(f'<tr class="partie-row"><td colspan="3">{P["num"]}. {esc(P["title"])}</td></tr>')
        for e in P["poems"]:
            if e.get("pf"):
                if MODE["liens"]:
                    rows.append(f'<tr><td>{esc(e["title"])}</td><td>{e["date"]}</td><td><a href="{B.pf_url(e)}">{e["pf"]}</a> · '
                                f'<a href="https://web.archive.org/web/2026/{B.pf_url(e)}">archive</a></td></tr>')
                else:
                    rows.append(f'<tr><td>{esc(e["title"])}</td><td>{e["date"]}</td><td>{e["pf"]}</td></tr>')
            else:
                rows.append(f'<tr><td>{esc(e["title"])}</td><td>—</td><td>inédit</td></tr>')
    return ('<table><thead><tr><th>Texte</th><th>Première publication</th><th>n° poeme-france</th></tr></thead><tbody>'
            + "".join(rows) + '</tbody></table>')

# ------------------------------------------------------------------ PDF
def font_faces(url_prefix):
    return "".join(f'@font-face{{font-family:"EB Garamond";font-weight:{w};font-style:{s};src:url("{url_prefix}{f}") format("woff")}}'
                   for (w, s), f in FONT_FILES.items())

PDF_CSS = """
@page{size:148mm 210mm; margin:17mm 16mm 19mm 20mm;
  @bottom-center{content:counter(page); font-family:"EB Garamond"; font-size:9.5pt; color:#5b554b}}
@page:left{margin:17mm 20mm 19mm 16mm}

@page vide{ @bottom-center{content:none} }
html{font-size:11pt}
body{margin:0; font-family:"EB Garamond",Garamond,Georgia,serif; line-height:1.45; color:#1a1712; font-kerning:normal; font-variant-ligatures:common-ligatures}
h1,h2,h3,h4{font-weight:400; line-height:1.15; margin:0; color:#15120e}
p{margin:0 0 .8em; orphans:2; widows:2}
a{color:inherit; text-decoration:none}
body.liens a{color:#9a6f0a}
body.liens .sommaire a,body.liens .titre a{color:inherit}
.musique{margin-top:7mm; font-size:9.5pt; color:#5b554b; line-height:1.4}
.page,.poeme-page{break-before:page}
.titre,.colophon,.dedicace,.ouverture,.partie,.blanche{page:vide}
.blanche{height:1px}
.fil{position:relative; height:1px; background:rgba(26,23,18,.22); margin:3mm 0 7mm; width:42mm}
.fil::after{content:""; position:absolute; left:0; top:-3px; width:7px; height:7px; border-radius:50%; background:#9a6f0a}
/* page de titre */
.titre{text-align:center; padding-top:52mm}
.titre .auteur{font-size:12pt; letter-spacing:.16em; text-transform:uppercase; color:#5b554b; margin:0 0 10mm}
.titre h1{font-size:30pt; letter-spacing:-.005em}
.titre .fil{margin:6mm auto; width:50mm}
.titre .fil::after{left:calc(50% - 3.5px)}
.titre .st{font-style:italic; font-size:13.5pt; color:#5b554b; margin:0}
.titre .site{margin-top:62mm; font-size:10.5pt; color:#5b554b; letter-spacing:.04em}
.colophon{padding-top:128mm; font-size:9pt; color:#5b554b; line-height:1.4}
.colophon p{margin:0 0 .5em}
.dedicace{padding-top:58mm; text-align:center; font-style:italic; font-size:12pt; color:#1a1712}
.sous-titre{font-style:italic; color:#5b554b; margin-top:-4mm; margin-bottom:6mm}
/* préface */
.preface{line-height:1.6; font-size:11pt}
.preface .acro{display:block; margin-bottom:.35em; padding-left:1.6em; text-indent:-1.6em}
.preface .acro strong{font-weight:500; color:#9a6f0a}
.signature{text-align:right; font-style:italic; color:#5b554b; margin-top:1.4em}
/* ouverture */
.ouverture{padding-top:58mm}
.citation{font-style:italic; font-size:12pt; margin:0 0 .4em}
.citation + .citation{color:#5b554b; font-style:normal; text-align:right; font-size:11pt}
/* sommaire */
.sommaire h1,.sources h1,.fin h1,.preface-page h1{font-size:20pt; margin-bottom:0}
.sommaire ol{list-style:none; padding:0; margin:0}
.sommaire li{break-inside:avoid}
.sommaire li a{display:flex; align-items:baseline; gap:.35em; color:inherit}
.sommaire li .t{white-space:nowrap; overflow:hidden; text-overflow:ellipsis}
.sommaire li .pts{flex:1; border-bottom:1px dotted rgba(26,23,18,.5); margin:0 .15em; min-width:1.5em; transform:translateY(-.3em)}
.sommaire li .n{font-variant-numeric:tabular-nums; color:#5b554b}
.sommaire li.part{margin-top:.85em; font-size:11.5pt}
.sommaire li.part .n{color:#1a1712}
.sommaire li.poem{padding-left:1.3em; font-size:10.5pt; line-height:1.4}
.sommaire li.autre{margin-top:.85em; font-size:11.5pt}
/* partie */
.partie{padding-top:48mm}
.partie .num{font-size:34pt; color:#9a6f0a; line-height:1; margin:0 0 5mm; font-weight:400}
.partie h1{font-size:23pt}
.partie .chapeau{font-style:italic; color:#5b554b; margin-top:7mm; max-width:100mm; font-size:10.5pt; line-height:1.5}
/* poèmes */
.poeme-page h2{font-size:17pt; break-after:avoid}
.poeme .strophe{margin:0 0 .95em; break-inside:avoid}
.poeme .v{display:block; padding-left:1.6em; text-indent:-1.6em}
.poeme.acrostiche .acro-l{font-weight:500; color:#9a6f0a}
.prose p{margin:0; text-indent:1.4em; text-align:justify; hyphens:auto; -webkit-hyphens:auto}
.prose p:first-child{text-indent:0}
.theatre h3{font-size:13pt; margin:1.5em 0 .5em; break-after:avoid}
.theatre h4{font-size:11.5pt; font-style:italic; margin:1.1em 0 .4em; break-after:avoid}
.theatre .didascalie{font-style:italic; color:#5b554b; font-size:10pt; margin:.5em 0}
.theatre .personnage{margin:.8em 0 .1em; font-weight:500; break-after:avoid}
.theatre .replique{margin:0 0 .3em; padding-left:1.2em}
.note-auteur{color:#5b554b; font-size:9.5pt; border-left:1.5px solid rgba(26,23,18,.25); padding-left:3mm; margin-top:8mm; line-height:1.4}
/* sources */
.sources table{width:100%; border-collapse:collapse; font-size:9.3pt; margin-top:4mm}
.sources th,.sources td{text-align:left; padding:.22em .5em .22em 0; border-bottom:1px solid rgba(26,23,18,.12); vertical-align:top}
.sources th{font-weight:500}
.sources tr.partie-row td{padding-top:.9em; font-style:italic; color:#5b554b; border-bottom:none}
.sources tr{break-inside:avoid}
.sources p,.fin p{font-size:10.5pt}
.fin{padding-top:0}
.source{font-size:8.5pt; color:#5b554b; margin-top:5mm}
.musiques h2{font-size:14pt; margin:6mm 0 2mm; break-after:avoid}
.musiques .mus-item{font-size:10.5pt; margin:3mm 0 1.5mm}
.musiques .paroles{margin:0 0 4mm 6mm; font-size:10pt}
.musiques .paroles .strophe{margin:0 0 2.5mm; break-inside:avoid}
.musiques .paroles .v{display:block; margin:0; padding-left:1.4em; text-indent:-1.4em; line-height:1.4}
.musiques .paroles-label{font-size:8.5pt; letter-spacing:.08em; text-transform:uppercase; color:#5b554b; margin:3mm 0 1mm}
.musiques p{font-size:10.5pt}
"""

RECTO = ["dedicace", "preface", "ouverture", "sommaire"] + [f"partie-{P['num']}" for P in PARTS] + ["musiques"]

ECRAN_CSS = "@page{margin:17mm 18mm 19mm 18mm} @page:left{margin:17mm 18mm 19mm 18mm}"

def book_html(numbers, blanks):
    """numbers : clé -> numéro de page à afficher au sommaire ; blanks : clés précédées d'une page blanche."""
    n = lambda k: numbers.get(k, "")
    def blank(k):
        return '<section class="page blanche"></section>' if k in blanks else ""
    h = ['<!DOCTYPE html><html lang="fr"><head><meta charset="utf-8">',
         f'<title>{esc(FRONT["title"])} — Delideal</title><style>', font_faces(FONTS.as_uri() + "/"), PDF_CSS,
         ECRAN_CSS if MODE["liens"] else "", '</style></head>', '<body class="liens">' if MODE["liens"] else '<body>']
    h.append(f'<section class="titre"><p class="auteur">Delideal</p><h1>{esc(FRONT["title"])}</h1><div class="fil"></div>'
             f'<p class="st">{esc(FRONT["subtitle"])}</p><p class="site">' + (f'<a href="{SITE}">delideal.art</a>' if MODE["liens"] else 'delideal.art') + '</p></section>')
    h.append(f'<section class="page colophon">{COLOPHON}</section>')
    h.append(blank("dedicace") + f'<section class="page dedicace"><p>{esc(FRONT["dedicace"])}</p></section>')
    h.append(blank("preface") + f'<section class="page preface-page" id="preface"><h1>Préface</h1><div class="fil"></div>{preface_html()}</section>')
    h.append(blank("ouverture") + '<section class="page ouverture">' + "".join(f'<p class="citation">{esc(l)}</p>' for l in FRONT["ouverture"]) + '</section>')
    # sommaire
    s = ['<section class="page sommaire"><h1>Sommaire</h1><div class="fil"></div><ol>',
         f'<li class="autre"><a href="#preface"><span class="t">Préface</span><span class="pts"></span><span class="n">{n("preface")}</span></a></li>']
    for P in PARTS:
        k = f'partie-{P["num"]}'
        s.append(f'<li class="part"><a href="#{k}"><span class="t">{P["num"]}. {esc(P["title"])}</span><span class="pts"></span><span class="n">{n(k)}</span></a></li>')
        for e in P["poems"]:
            s.append(f'<li class="poem"><a href="#{e["slug"]}"><span class="t">{esc(e["title"])}</span><span class="pts"></span><span class="n">{n(e["slug"])}</span></a></li>')
    s.append(f'<li class="autre"><a href="#musiques"><span class="t">Les musiques</span><span class="pts"></span><span class="n">{n("musiques")}</span></a></li>')
    s.append(f'<li class="autre"><a href="#sources"><span class="t">Sources</span><span class="pts"></span><span class="n">{n("sources")}</span></a></li>')
    s.append(f'<li class="autre"><a href="#fin"><span class="t">Pour continuer</span><span class="pts"></span><span class="n">{n("fin")}</span></a></li>')
    s.append('</ol></section>')
    h.append(blank("sommaire") + "".join(s))
    # parties et poèmes
    for P in PARTS:
        k = f'partie-{P["num"]}'
        h.append(blank(k) + f'<section class="page partie" id="{k}"><p class="num">{P["num"]}</p><h1>{esc(P["title"])}</h1>'
                 + (f'<p class="chapeau">' + "<br>".join(esc(x) for x in P["chapeau"].split("\n")) + '</p>' if P.get("chapeau") else "") + '</section>')
        for e in P["poems"]:
            h.append(f'<article class="poeme-page" id="{e["slug"]}">{poem_html(e, "<br>")}</article>')
    h.append(f'<section class="page musiques" id="musiques"><h1>Les musiques</h1><div class="fil"></div>{musiques_html(pdf=True)}</section>')
    h.append(f'<section class="page sources" id="sources"><h1>Sources</h1><div class="fil"></div>{sources_pdf_html()}</section>')
    h.append(f'<section class="page fin" id="fin"><h1>Pour continuer</h1><div class="fil"></div>{fin_html()}</section>')
    h.append('</body></html>')
    return "".join(h)

def chromium_pdf(html, scratch):
    from playwright.sync_api import sync_playwright
    src = scratch / "livre.html"
    src.write_text(html, encoding="utf-8")
    pdf = scratch / "livre.pdf"
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page()
        pg.goto(src.as_uri())
        pg.wait_for_load_state("networkidle")
        pg.evaluate("document.fonts.ready")
        pg.pdf(path=str(pdf), prefer_css_page_size=True, print_background=True, outline=True, tagged=True)
        b.close()
    return pdf.read_bytes()

def measure(pdf_bytes):
    """Retourne clé -> numéro de page (1-based) : signets pour les titres, texte pour dédicace/ouverture."""
    from pypdf import PdfReader
    r = PdfReader(io.BytesIO(pdf_bytes))
    expected = [("titre", FRONT["title"]), ("preface", "Préface"), ("sommaire", "Sommaire")]
    for P in PARTS:
        expected.append((f'partie-{P["num"]}', P["title"]))
        for e in P["poems"]:
            expected.append((e["slug"], e["title"]))
    expected += [("musiques", "Les musiques"), ("sources", "Sources"), ("fin", "Pour continuer")]
    flat = []
    def walk(o):
        for x in o:
            if isinstance(x, list): walk(x)
            else: flat.append((re.sub(r"\s+", " ", x.title).strip(), r.get_destination_page_number(x) + 1))
    walk(r.outline)
    pages, i = {}, 0
    for title, pg in flat:
        exp = re.sub(r"\s+", " ", expected[i][1]).strip() if i < len(expected) else None
        if exp is not None and title in (exp, exp + exp):   # Chromium double parfois le texte du signet
            pages[expected[i][0]] = pg
            i += 1
    missing = [k for k, _ in expected if k not in pages]
    if missing:
        raise RuntimeError(f"titres introuvables dans les signets : {missing[:5]}")
    norm = lambda s: re.sub(r"[^a-zà-ÿ]", "", s.lower())
    ded, ouv = norm(FRONT["dedicace"])[:30], norm(FRONT["ouverture"][0])[:30]
    for idx, page in enumerate(r.pages):
        t = norm(page.extract_text() or "")
        if "dedicace" not in pages and t.startswith(ded): pages["dedicace"] = idx + 1
        elif "ouverture" not in pages and t.startswith(ouv): pages["ouverture"] = idx + 1
    if "dedicace" not in pages or "ouverture" not in pages:
        raise RuntimeError("dédicace ou ouverture introuvable dans le texte du PDF")
    return pages, len(r.pages)

def make_pdf(scratch, liens):
    MODE["liens"] = liens
    recto = [] if liens else RECTO          # écran : pas de pages blanches
    order = ["titre", "dedicace", "preface", "ouverture", "sommaire"]
    for P in PARTS:
        order.append(f'partie-{P["num"]}'); order += [e["slug"] for e in P["poems"]]
    order += ["musiques", "sources", "fin"]
    pos = {k: i for i, k in enumerate(order)}
    numbers, blanks = {}, set()
    for it in range(8):
        pdf = chromium_pdf(book_html(numbers, blanks), scratch)
        actual, npages = measure(pdf)
        old_before = lambda k: sum(1 for b in blanks if pos[b] <= pos[k])
        base = {k: actual[k] - old_before(k) for k in actual}
        new_blanks = set()
        for rk in recto:
            if (base[rk] + len(new_blanks)) % 2 == 0:
                new_blanks.add(rk)
        new_numbers = {k: str(base[k] + sum(1 for b in new_blanks if pos[b] <= pos[k])) for k in actual}
        stable = new_blanks == blanks and all(numbers.get(k) == v for k, v in new_numbers.items())
        print(f"  passe {it + 1} : {npages} pages, {len(new_blanks)} pages blanches, {'stable' if stable else 'à refaire'}")
        if stable:
            break
        numbers, blanks = new_numbers, new_blanks
    else:
        raise RuntimeError("le sommaire ne converge pas")
    for rk in recto:
        assert actual[rk] % 2 == 1, f"{rk} n’est pas sur une page de droite (p. {actual[rk]})"
    return pdf, npages

# ------------------------------------------------------------------ EPUB
# ------------------------------------------------------------------ EPUB (Kindle et liseuses)
# Règles suivies (KDP « Kindle Publishing Guidelines » et aide KDP, octobre 2026) :
#  - pas de police embarquée (Kindle n'accepte que OTF/TTF et recommande ses propres polices : le lecteur garde le choix) ;
#  - pas de page de couverture dans le flux (KDP ajoute la couverture envoyée : elle apparaîtrait deux fois) ;
#  - sommaire HTML en début de livre (dans le flux, donc dans l'extrait gratuit) + NCX + nav ;
#  - chaque vers est un paragraphe aligné à gauche, avec retrait suspendu : sur téléphone, un vers trop long
#    se replie sans se confondre avec le suivant, et la justification de Kindle ne l'écartèle pas ;
#  - marges en em (pas en %), couleur réservée aux ornements (lisible en mode sombre), pas de tableau.
def description():
    """Texte de présentation (métadonnées de l'EPUB et fiche Amazon) : l'ouverture, puis la première phrase de chaque partie."""
    parties = " ".join(f'{P["num"]}. {P["title"]} — « {B.premiere_phrase(P["chapeau"].split(chr(10))[0]) if P.get("chapeau") else ""} »' for P in PARTS)
    return ("« Du ciment dans les veines / pour éviter l’hémorragie cérébrale. / Mais lentement les vaisseaux de mon cœur saignent / "
            "de la poudre de brique issue de mon mal. »\n\n"
            f"{B.NOMBRES.get(len(B.ALL), len(B.ALL))} textes écrits à partir de l’an 2000, rassemblés en six parties. {parties}\n\n"
            "Des poèmes écrits au plus près de ce qui était vécu — l’émerveillement, le désir, l’hôpital, la colère, puis un chemin — "
            "et laissés tels quels, avec leurs excès. Préface d’Isabelle Jespersen, en acrostiche.\n\n"
            "Delideal est le nom d’artiste de l’auteur. Plusieurs de ces poèmes sont devenus des chansons, à écouter sur delideal.art, "
            "où le recueil se lit aussi librement.")
MOTS_CLES = ["poésie", "trouble bipolaire", "santé mentale", "recueil de poèmes", "poésie contemporaine française",
             "folie et création", "hôpital psychiatrique"]

EPUB_CSS = """
body{margin:0; padding:0}
h1,h2,h3,h4{font-weight:normal; margin:0 0 .5em; text-align:left; page-break-after:avoid}
h1{font-size:1.6em} h2{font-size:1.4em; margin-top:.5em} h3{font-size:1.15em} h4{font-size:1em}
p{margin:0 0 .8em; text-indent:0}
a{text-decoration:underline}
.sommaire a{text-decoration:none; color:inherit}
hr.fil{border:0; border-top:1px solid #9a6f0a; height:0; width:3em; margin:.5em 0 1.3em 0; text-align:left}
.titre{text-align:center; margin-top:3em}
.titre .auteur{font-size:.85em; letter-spacing:.16em; text-transform:uppercase; margin:0 0 2.5em}
.titre h1{font-size:2.2em; text-align:center; margin:0}
.titre hr.fil{margin:1em auto; text-align:center}
.titre .st{font-style:italic; font-size:1.1em; margin:0}
.titre .site{margin-top:5em; font-size:.9em}
.dedicace{text-align:center; font-style:italic; font-size:1.1em; margin-top:5em}
.preface p.acro{margin:0 0 .4em; padding-left:1.5em; text-indent:-1.5em; text-align:left}
.preface .acro b,.acrostiche .acro-l{font-weight:bold; color:#9a6f0a}
.signature{text-align:right; font-style:italic; margin-top:1.4em}
.ouverture{margin-top:4em}
.citation{font-style:italic; font-size:1.1em; text-align:left; margin:0 0 .4em}
.citation-source{text-align:right; margin:0}
.partie{margin-top:3em}
.partie .num{font-size:2.4em; color:#9a6f0a; margin:0 0 .25em; text-align:left}
.partie h1{font-size:1.8em}
.partie .chapeau{margin-top:1.4em; font-style:italic}
.partie .chapeau p{margin:0; padding-left:1.5em; text-indent:-1.5em; text-align:left}
.sous-titre{font-style:italic; margin-top:-.4em}
div.strophe{margin:0 0 1em; page-break-inside:avoid}
p.v{margin:0; padding-left:1.5em; text-indent:-1.5em; text-align:left}
.prose p{margin:0; text-indent:1.4em; text-align:justify}
.prose p.premier{text-indent:0}
.theatre h3{margin:1.5em 0 .5em} .theatre h4{font-style:italic; margin:1.1em 0 .4em}
.theatre .didascalie{font-style:italic; font-size:.92em; margin:.5em 0}
.theatre .personnage{margin:.8em 0 .1em; font-weight:bold}
.theatre .replique{margin:0 0 .3em; padding-left:1.2em; text-indent:-1.2em; text-align:left}
.note-auteur{font-size:.9em; font-style:italic; margin-top:2em}
.source{font-size:.85em; margin-top:1.6em}
.musique{margin-top:2em; font-size:.9em}
.sources p.src{margin:0 0 .45em; padding-left:1.5em; text-indent:-1.5em; font-size:.9em; text-align:left}
.sources p.src-partie{margin:1.2em 0 .4em; font-style:italic}
.sommaire h1{margin-bottom:.2em}
.sommaire ol{list-style-type:none; margin:0; padding:0}
.sommaire ol ol{margin:.3em 0 .8em 0; padding-left:1.4em}
.sommaire li{margin:.25em 0}
.sommaire li.p{margin-top:1em}
.sommaire .num{color:#9a6f0a}
.credits{font-size:.9em}
.mus-item{margin:1em 0 .4em}
.paroles{margin:0 0 1.4em 1.2em; font-size:.95em}
.paroles-label{font-size:.85em; letter-spacing:.08em; text-transform:uppercase; margin:.8em 0 .3em}
.quatrieme{text-align:center; margin-top:2em}
.quatrieme .auteur{font-size:.85em; letter-spacing:.16em; text-transform:uppercase; margin:0 0 1.5em}
.quatrieme h1{text-align:center; font-size:1.9em}
.quatrieme hr.fil{margin:.8em auto; text-align:center}
.quatrieme .st{font-style:italic; margin:0 0 1.6em}
.quatrieme .ouv{text-align:left; margin:0 auto 1.4em; font-style:italic; display:inline-block}
.quatrieme .ouv p.v{padding-left:0; text-indent:0}
.quatrieme p{text-align:left}
.quatrieme .seuil{margin:.25em 0; padding-left:2.2em; text-indent:-2.2em}
.quatrieme .seuil .num{color:#9a6f0a; display:inline-block; width:2.2em; text-indent:0}
.quatrieme .site{text-align:center; margin-top:2em; font-size:.9em}
"""

def xhtml(title, body, cls=""):
    return ('<?xml version="1.0" encoding="utf-8"?>\n<!DOCTYPE html>\n'
            '<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" xml:lang="fr" lang="fr">'
            f'<head><meta charset="utf-8"/><title>{esc(title)}</title><link rel="stylesheet" type="text/css" href="../style.css"/></head>'
            f'<body class="{cls}">{body}</body></html>')

def epub_verses(e):
    """Chaque vers est un paragraphe (retrait suspendu), chaque strophe un bloc insécable."""
    kind = e.get("kind", "verse")
    out = []
    if kind == "verse":
        acro = bool(e.get("acrostiche"))
        def vers(l):
            if acro and l and l[0].isalpha():
                return '<b class="acro-l">' + esc(l[0]) + '</b>' + esc(l[1:])
            return esc(l)
        for blk in e["blocks"]:
            out.append('<div class="strophe">' + "".join(f'<p class="v">{vers(l)}</p>' for l in blk) + '</div>')
        return '<div class="poeme' + (' acrostiche' if acro else '') + '">' + "".join(out) + '</div>'
    if kind == "prose":
        first = True
        for blk in e["blocks"]:
            for l in blk:
                out.append(('<p class="premier">' if first else '<p>') + esc(l) + '</p>'); first = False
        return '<div class="prose">' + "".join(out) + '</div>'
    return to_xhtml_fragment(verses_html(e, "<br/>"))   # théâtre : même rendu que le PDF

def epub_poem(e):
    h = [f'<h2>{esc(e["title"])}</h2><hr class="fil"/>']
    if e.get("dedicace"):
        h.append(f'<p class="sous-titre">{esc(e["dedicace"])}</p>')
    h.append(epub_verses(e))
    if e.get("note"):
        h.append(f'<p class="note-auteur">{esc(e["note"])}</p>')
    h.append(to_xhtml_fragment(music_html(e)))
    return "".join(h)

def date_longue(d):
    j, m, a = d.split("/")
    return f'{int(j)}{"er" if int(j) == 1 else ""} {["janvier", "février", "mars", "avril", "mai", "juin", "juillet", "août", "septembre", "octobre", "novembre", "décembre"][int(m) - 1]} {a}'

def epub_sources():
    """Version allégée (EPUB v2) : le détail (dates, numéros, copies d'archive) reste sur delideal.art/credits.html."""
    n_ined = sum(1 for P in PARTS for e in P["poems"] if not e.get("pf"))
    mots = {0: "", 1: " Un texte est inédit.", 2: " Deux textes sont inédits."}
    return ('<p>Tous les textes de ce livre sont de Delideal. Écrits à partir de l’an 2000, ils ont été publiés '
            'entre octobre 2014 et décembre 2023 sur poeme-france.com, un site tiers qui fixe la date de mise en ligne '
            f'de chaque texte et conserve les commentaires des lecteurs de l’époque.{mots.get(n_ined, f" {n_ined} textes sont inédits.")}</p>'
            '<p>La date de première publication de chaque texte, son adresse sur poeme-france.com et la copie conservée par '
            f'Internet Archive sont réunies sur <a href="{SITE}/credits.html">delideal.art/credits.html</a>.</p>'
            '<p>La préface du recueil, un acrostiche, est d’Isabelle Jespersen.</p>')

def musiques_html(pdf=False):
    """Page « Les musiques » (PDF et EPUB) : chaque chanson avec son écoute, son origine et ses paroles complètes ;
    pour les chansons dont les paroles sont le poème, renvoi au poème (lien interne)."""
    by_slug = {e["slug"]: e for P in PARTS for e in P["poems"]}
    def lien_poeme(slug):
        e = by_slug.get(slug)
        if not e: return esc(slug)
        href = f"#{slug}" if pdf else f"{slug}.xhtml"
        return f'<a href="{href}">{esc(e["title"])}</a>'
    def ext(u, label):
        return f'<a href="{u}">{label}</a>' if MODE["liens"] else f'{label} ({u.replace("https://", "")})'
    def paroles_html(secs):
        out = []
        for sec in secs:
            suno = sec["label"].split()[0].lower() in ("strophe", "refrain", "pont", "couplet", "intro", "outro", "verse", "chorus", "bridge")
            if not suno and len(secs) > 1:
                out.append(f'<p class="paroles-label">{esc(sec["label"])}</p>')
            strophe = []
            for ln in sec["lines"]:
                if ln.strip() == "":
                    if strophe: out.append('<div class="strophe">' + "".join(strophe) + '</div>'); strophe = []
                else:
                    strophe.append(f'<p class="v">{esc(ln)}</p>')
            if strophe: out.append('<div class="strophe">' + "".join(strophe) + '</div>')
        return "".join(out)
    site_mus = ext(f"{SITE}/musique.html", "delideal.art/musique.html")
    h = ['<p>Plusieurs textes de ce recueil sont devenus des chansons. Les voici toutes, avec leurs paroles quand elles diffèrent du poème, '
         f'et les liens pour les écouter. Elles sont aussi réunies, avec leurs textes, sur {site_mus}.</p>']
    h.append('<h2>Chansons écrites et chantées par l’auteur</h2>')
    for P in PARTS:
        for e in P["poems"]:
            m = e.get("music")
            if m and m["kind"] == "auteur":
                liens = ext(m["yt"], "écouter sur YouTube") + (f' · {ext(m["yt2"], esc(m["label2"]).lower())}' if m.get("yt2") else "")
                h.append(f'<p class="mus-item"><b>{esc(e["title"])}</b> — {liens}. Les paroles sont le poème, mot pour mot : {lien_poeme(e["slug"])}.</p>')
    for c in B.R.get("chansons", []):
        h.append(f'<p class="mus-item"><b>{esc(c["title"])}</b> — {ext(c["yt"], "écouter sur YouTube")}.</p>')
        if c.get("paroles"): h.append('<div class="paroles">' + paroles_html(c["paroles"]) + '</div>')
    h.append('<h2>Maquettes</h2>'
             '<p>Ces chansons ont été produites avec des outils d’intelligence artificielle : les paroles sont celles de l’auteur, '
             'assemblées à partir de ses poèmes, et les consignes de style sont les siennes ; la musique et la voix sont générées. '
             'Ce sont des maquettes : une façon d’entendre ce que ces textes pourraient devenir en chanson.</p>')
    for mq in B.MAQUETTES:
        n = len(mq["sources"]); srcs = ", ".join(lien_poeme(s) for s in mq["sources"])
        lien = ext(mq["yt"], "écouter sur YouTube") if mq.get("yt") else ext(f'{SITE}/musique.html#chanson-{mq["slug"]}', "écouter sur delideal.art")
        base = "sur le texte intégral du poème" if n == 1 else ("à partir de deux textes" if n == 2 else "à partir de trois textes")
        h.append(f'<p class="mus-item"><b>{esc(mq["title"])}</b> — {lien} · {base} : {srcs}.</p>')
        if mq.get("paroles"):
            h.append('<div class="paroles">' + paroles_html(mq["paroles"]) + '</div>')
        elif n == 1:
            h.append('<p class="note-auteur">Les paroles sont le poème, mot pour mot.</p>')
    h.append('<h2>Au piano</h2>')
    for P in PARTS:
        for e in P["poems"]:
            m = e.get("music")
            if m and m["kind"] == "piano":
                h.append(f'<p class="mus-item"><b>{esc(e["title"])}</b> — {esc(m["label"]).lower()} : {ext(m["yt"], "écouter sur YouTube")} · '
                         f'{ext(f"{SITE}/{m["mp3"]}", "télécharger le mp3")}. Le poème du même nom : {lien_poeme(e["slug"])}.</p>')
    h.append('<p class="mus-item"><b>Rage and Hopes</b> — une improvisation au piano, brouillonne et sincère, douze minutes jouées d’une traite : '
             + ext("https://www.youtube.com/watch?v=QFCULzpDsJk", "écouter sur YouTube") + '.</p>')
    return "".join(h)

def epub_musiques():
    return '<h1>Les musiques</h1><hr class="fil"/>' + musiques_html(pdf=False)

def epub_quatrieme():
    """Page de fin, façon quatrième de couverture : l'ouverture et les six seuils (textes de l'auteur)."""
    ouv = "".join(f'<p class="v">{esc(l)}</p>' for l in B.TITRE["blocks"][0]) if B.TITRE else ""
    seuils = "".join(f'<p class="seuil"><span class="num">{P["num"]}</span> {esc(B.premiere_phrase(P["chapeau"].split(chr(10))[0]))}</p>' for P in PARTS if P.get("chapeau"))
    return (f'<section class="quatrieme"><p class="auteur">Delideal</p><h1>{esc(FRONT["title"])}</h1><hr class="fil"/>'
            f'<p class="st">{esc(FRONT["subtitle"])}</p>'
            f'<div class="strophe ouv">{ouv}</div>'
            f'<p>{B.NOMBRES.get(len(B.ALL), len(B.ALL))} textes écrits à partir de l’an 2000, rassemblés en six parties.</p>{seuils}'
            '<p>Des poèmes écrits au plus près de ce qui était vécu, et laissés tels quels, avec leurs excès. Préface d’Isabelle Jespersen, en acrostiche.</p>'
            f'<p class="site">delideal.art</p></section>')

def epub_credits():
    return (f'<h1>Crédits</h1><hr class="fil"/><p>{esc(FRONT["title"])} — {esc(FRONT["subtitle"])}</p>'
            '<p>Textes de Delideal, écrits à partir de l’an 2000, publiés entre 2014 et 2023 sur poeme-france.com. '
            'Préface d’Isabelle Jespersen.</p>'
            f'<p>Édition numérique établie par l’auteur à partir du site <a href="{SITE}">delideal.art</a>, {MOIS} {ANNEE}.</p>'
            f'<p>© {ANNEE} Delideal. Tous droits réservés.</p>')

def to_xhtml_fragment(s):
    """Nos fragments HTML n'utilisent que des balises fermées, sauf <br> et <hr> ; on les ferme."""
    return s.replace("<br>", "<br/>").replace("<hr>", "<hr/>").replace('<div class="fil"></div>', '<hr class="fil"/>')

def cover_jpg(scratch, bordure=False):
    """Couverture typographique 1600 × 2560 (format Kindle) : texte seulement, aucune illustration."""
    from playwright.sync_api import sync_playwright
    html = ('<!DOCTYPE html><html lang="fr"><head><meta charset="utf-8"><style>' + font_faces(FONTS.as_uri() + "/") +
            'html,body{margin:0;width:1600px;height:2560px;background:#fbf7ef;color:#1a1712;font-family:"EB Garamond";position:relative}'
            '.c{position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center;padding:0 140px 120px;text-align:center}'
            '.a{font-size:56px;letter-spacing:.22em;text-transform:uppercase;color:#5b554b;margin:0 0 150px}'
            'h1{font-weight:400;font-size:172px;margin:0;line-height:1.08;letter-spacing:-.005em}'
            '.fil{position:relative;height:4px;background:rgba(26,23,18,.25);width:560px;margin:90px auto 70px}'
            '.fil::after{content:"";position:absolute;left:calc(50% - 16px);top:-15px;width:34px;height:34px;border-radius:50%;background:#9a6f0a}'
            '.st{font-style:italic;font-size:74px;color:#5b554b;margin:0;line-height:1.25}'
            '.pre{position:absolute;bottom:260px;left:0;right:0;text-align:center;font-size:40px;color:#5b554b;font-style:italic}'
            '.site{position:absolute;bottom:150px;left:0;right:0;text-align:center;font-size:40px;color:#5b554b;letter-spacing:.08em}'
            + ('.cadre{position:absolute;inset:0;border:4px solid #b9b2a6;pointer-events:none}' if bordure else '') +
            '</style></head><body><div class="c"><p class="a">Delideal</p>'
            f'<h1>Marcher<br>sur un fil</h1><div class="fil"></div><p class="st">Fragments de<br>sensibilité bipolaire</p></div>'
            '<p class="pre">Poèmes · Préface d’Isabelle Jespersen</p><p class="site">delideal.art</p>'
            + ('<div class="cadre"></div>' if bordure else '') + '</body></html>')
    src = scratch / "couverture.html"; src.write_text(html, encoding="utf-8")
    jpg = scratch / "couverture.jpg"
    with sync_playwright() as p:
        b = p.chromium.launch(); pg = b.new_page(viewport={"width": 1600, "height": 2560})
        pg.goto(src.as_uri()); pg.wait_for_load_state("networkidle"); pg.evaluate("document.fonts.ready")
        pg.screenshot(path=str(jpg), full_page=False, type="jpeg", quality=92); b.close()
    return jpg.read_bytes()

def make_epub(scratch, amazon=True, bordure=False):
    MODE["liens"] = True
    MODE["amazon"] = amazon
    files = []   # (id, href, media-type, bytes, properties)
    spine = []
    nav_items = []  # (href, title, [children])
    def add(href, data, mt="application/xhtml+xml", props=None, in_spine=True):
        fid = re.sub(r"[^a-z0-9]", "-", href.lower())
        files.append((fid, href, mt, data, props))
        if in_spine: spine.append(fid)
        return href
    add("style.css", EPUB_CSS.encode(), "text/css", in_spine=False)
    add("couverture.jpg", cover_jpg(scratch, bordure), "image/jpeg", props="cover-image", in_spine=False)
    # page de titre, dédicace, sommaire, préface, ouverture
    add("text/titre.xhtml", xhtml(FRONT["title"], f'<section class="titre"><p class="auteur">Delideal</p><h1>{esc(FRONT["title"])}</h1><hr class="fil"/>'
                                                 f'<p class="st">{esc(FRONT["subtitle"])}</p><p class="site">delideal.art</p></section>').encode())
    add("text/dedicace.xhtml", xhtml("Dédicace", f'<section class="dedicace"><p>{esc(FRONT["dedicace"])}</p></section>').encode())
    nav_items.append(("text/dedicace.xhtml", "Dédicace", []))
    spine.append("nav-xhtml")   # le sommaire, dans le flux, juste après la dédicace
    pref = "".join(f'<p class="acro"><b>{esc(l[0])}</b>{esc(l[1:])}</p>' for l in FRONT["preface"]["lines"])
    add("text/preface.xhtml", xhtml("Préface", f'<section class="preface"><h1>Préface</h1><hr class="fil"/>{pref}<p class="signature">{esc(FRONT["preface"]["sign"])}</p></section>').encode())
    nav_items.append(("text/preface.xhtml", "Préface", []))
    ouv = FRONT["ouverture"]
    add("text/ouverture.xhtml", xhtml("Exergue", '<section class="ouverture">' + f'<p class="citation">{esc(ouv[0])}</p>'
                                      + "".join(f'<p class="citation-source">{esc(l.lstrip("- ").strip())}</p>' for l in ouv[1:]) + '</section>').encode())
    nav_items.append(("text/ouverture.xhtml", "Exergue", []))
    for P in PARTS:
        href = f'text/partie-{P["num"]}.xhtml'
        chapeau = ('<div class="chapeau">' + "".join(f'<p>{esc(x)}</p>' for x in P["chapeau"].split("\n")) + '</div>') if P.get("chapeau") else ""
        add(href, xhtml(f'{P["num"]}. {P["title"]}', f'<section class="partie"><p class="num">{P["num"]}</p><h1>{esc(P["title"])}</h1>{chapeau}</section>').encode())
        kids = []
        for e in P["poems"]:
            ph = f'text/{e["slug"]}.xhtml'
            add(ph, xhtml(e["title"], f'<article class="poeme-page">{epub_poem(e)}</article>').encode())
            kids.append((ph, e["title"], []))
        nav_items.append((href, f'{P["num"]}. {P["title"]}', kids))
    add("text/musiques.xhtml", xhtml("Les musiques", f'<section class="musiques">{epub_musiques()}</section>').encode())
    nav_items.append(("text/musiques.xhtml", "Les musiques", []))
    add("text/sources.xhtml", xhtml("Sources", f'<section class="sources"><h1>Sources</h1><hr class="fil"/>{epub_sources()}</section>').encode())
    nav_items.append(("text/sources.xhtml", "Sources", []))
    add("text/fin.xhtml", xhtml("Pour continuer", f'<section class="fin"><h1>Pour continuer</h1><hr class="fil"/>{to_xhtml_fragment(fin_html())}</section>').encode())
    nav_items.append(("text/fin.xhtml", "Pour continuer", []))
    add("text/credits.xhtml", xhtml("Crédits", f'<section class="credits">{epub_credits()}</section>').encode())
    nav_items.append(("text/credits.xhtml", "Crédits", []))
    add("text/quatrieme.xhtml", xhtml("Quatrième de couverture", epub_quatrieme()).encode())
    nav_items.append(("text/quatrieme.xhtml", "Quatrième de couverture", []))
    # sommaire (nav EPUB 3, dans le flux) + NCX (anciens lecteurs et Kindle)
    def ol(items, top=False):
        li = []
        for h, t, k in items:
            if top and k:
                num, titre = t.split(". ", 1)
                li.append(f'<li class="p"><a href="{h}"><span class="num">{num}</span> {esc(titre)}</a>{ol(k)}</li>')
            else:
                li.append(f'<li><a href="{h}">{esc(t)}</a>{ol(k) if k else ""}</li>')
        return "<ol>" + "".join(li) + "</ol>"
    nav = ('<?xml version="1.0" encoding="utf-8"?>\n<!DOCTYPE html>\n'
           '<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" xml:lang="fr" lang="fr">'
           '<head><meta charset="utf-8"/><title>Sommaire</title><link rel="stylesheet" type="text/css" href="style.css"/></head><body class="sommaire">'
           '<h1>Sommaire</h1><hr class="fil"/><nav epub:type="toc" id="toc">' + ol(nav_items, top=True) + '</nav>'
           '<nav epub:type="landmarks" hidden="hidden"><ol>'
           '<li><a epub:type="toc" href="nav.xhtml">Sommaire</a></li>'
           '<li><a epub:type="bodymatter" href="text/preface.xhtml">Début de la lecture</a></li>'
           '</ol></nav></body></html>')
    add("nav.xhtml", nav.encode(), props="nav", in_spine=False)
    uid = "https://delideal.art/livre/marcher-sur-un-fil"
    counter = [0]
    def ncx_points(items):
        out = []
        for h, t, k in items:
            counter[0] += 1
            out.append(f'<navPoint id="np{counter[0]}" playOrder="{counter[0]}"><navLabel><text>{esc(t)}</text></navLabel><content src="{h}"/>{ncx_points(k)}</navPoint>')
        return "".join(out)
    ncx_items = [("nav.xhtml", "Sommaire", [])] + nav_items
    ncx = ('<?xml version="1.0" encoding="utf-8"?>\n<ncx xmlns="http://www.daisy.org/z3986/2005/ncx/" version="2005-1" xml:lang="fr">'
           f'<head><meta name="dtb:uid" content="{uid}"/><meta name="dtb:depth" content="2"/><meta name="dtb:totalPageCount" content="0"/><meta name="dtb:maxPageNumber" content="0"/></head>'
           f'<docTitle><text>{esc(FRONT["title"])}</text></docTitle><navMap>{ncx_points(ncx_items)}</navMap></ncx>')
    add("toc.ncx", ncx.encode(), "application/x-dtbncx+xml", in_spine=False)
    modified = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    manifest = "".join(f'<item id="{fid}" href="{href}" media-type="{mt}"' + (f' properties="{props}"' if props else "") + '/>'
                       for fid, href, mt, _, props in files)
    subjects = "".join(f'<dc:subject>{esc(s)}</dc:subject>' for s in MOTS_CLES)
    opf = ('<?xml version="1.0" encoding="utf-8"?>\n'
           '<package xmlns="http://www.idpf.org/2007/opf" version="3.0" unique-identifier="uid" xml:lang="fr" prefix="schema: http://schema.org/">'
           '<metadata xmlns:dc="http://purl.org/dc/elements/1.1/">'
           f'<dc:identifier id="uid">{uid}</dc:identifier>'
           f'<dc:title id="t">{esc(FRONT["title"])}</dc:title><meta refines="#t" property="title-type">main</meta>'
           f'<dc:title id="st">{esc(FRONT["subtitle"])}</dc:title><meta refines="#st" property="title-type">subtitle</meta>'
           '<dc:creator id="a">Delideal</dc:creator><meta refines="#a" property="role" scheme="marc:relators">aut</meta><meta refines="#a" property="file-as">Delideal</meta>'
           '<dc:contributor id="p">Isabelle Jespersen</dc:contributor><meta refines="#p" property="role" scheme="marc:relators">aui</meta>'
           f'<dc:language>fr</dc:language><dc:date>{datetime.date.today().isoformat()}</dc:date>'
           f'<dc:publisher>delideal.art</dc:publisher><dc:rights>© {ANNEE} Delideal. Tous droits réservés.</dc:rights>'
           f'<dc:description>{esc(description())}</dc:description>{subjects}'
           '<meta property="schema:accessMode">textual</meta><meta property="schema:accessModeSufficient">textual</meta>'
           '<meta property="schema:accessibilityFeature">tableOfContents</meta><meta property="schema:accessibilityFeature">readingOrder</meta>'
           '<meta property="schema:accessibilityHazard">none</meta>'
           '<meta property="schema:accessibilitySummary">Texte seul, sans image hors couverture ; sommaire de navigation ; mise en page reflowable.</meta>'
           f'<meta property="dcterms:modified">{modified}</meta><meta name="cover" content="couverture-jpg"/>'
           '</metadata>'
           f'<manifest>{manifest}</manifest>'
           '<spine toc="toc-ncx">' + "".join(f'<itemref idref="{i}"/>' for i in spine) + '</spine>'
           '</package>')
    container = ('<?xml version="1.0" encoding="utf-8"?>\n<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">'
                 '<rootfiles><rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/></rootfiles></container>')
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as z:
        z.writestr(zipfile.ZipInfo("mimetype"), b"application/epub+zip", compress_type=zipfile.ZIP_STORED)
        z.writestr("META-INF/container.xml", container, compress_type=zipfile.ZIP_DEFLATED)
        z.writestr("OEBPS/content.opf", opf, compress_type=zipfile.ZIP_DEFLATED)
        for fid, href, mt, data, _ in files:
            z.writestr("OEBPS/" + href, data, compress_type=zipfile.ZIP_DEFLATED)
    data = buf.getvalue()
    check_epub(data)
    return data, len(files)

def check_epub(data):
    """Vérifications structurelles (à défaut d'epubcheck) : conteneur, manifeste, spine, liens internes, XML."""
    import posixpath
    z = zipfile.ZipFile(io.BytesIO(data))
    names = z.namelist()
    assert names[0] == "mimetype" and z.getinfo("mimetype").compress_type == zipfile.ZIP_STORED, "mimetype"
    assert z.read("mimetype") == b"application/epub+zip"
    ET.fromstring(z.read("META-INF/container.xml"))
    opf = ET.fromstring(z.read("OEBPS/content.opf"))
    ns = {"o": "http://www.idpf.org/2007/opf", "dc": "http://purl.org/dc/elements/1.1/"}
    items = {i.get("id"): i for i in opf.find("o:manifest", ns)}
    hrefs = {i.get("href") for i in items.values()}
    assert len(items) == len(list(opf.find("o:manifest", ns))), "ids en double"
    for i in items.values():
        assert "OEBPS/" + i.get("href") in names, "fichier absent : " + i.get("href")
    assert sum(1 for i in items.values() if i.get("properties") == "nav") == 1, "nav"
    assert sum(1 for i in items.values() if i.get("properties") == "cover-image") == 1, "cover-image"
    for ref in opf.find("o:spine", ns):
        assert ref.get("idref") in items, "spine : " + ref.get("idref")
    uid = opf.get("unique-identifier")
    assert opf.find(f"o:metadata/dc:identifier[@id='{uid}']", ns) is not None, "identifiant"
    n_links = 0
    for n in names:
        if n.endswith(".xhtml") or n.endswith(".ncx"):
            root = ET.fromstring(z.read(n))
            base = posixpath.dirname(n[len("OEBPS/"):])
            for el in root.iter():
                target = el.get("href") or el.get("src")
                if not target or target.startswith(("http:", "https:", "mailto:", "#")):
                    continue
                path = posixpath.normpath(posixpath.join(base, target.split("#")[0]))
                assert path in hrefs, f"lien cassé dans {n} : {target}"
                n_links += 1
    return n_links

# ------------------------------------------------------------------ principal
def main():
    import tempfile
    OUT.mkdir(exist_ok=True)
    scratch = Path(tempfile.mkdtemp(prefix="livre-"))
    if "--amazon" in sys.argv:
        dest = Path(sys.argv[sys.argv.index("--amazon") + 1]) if len(sys.argv) > sys.argv.index("--amazon") + 1 else Path("/tmp/marcher-sur-un-fil-amazon.epub")
        epub, nfiles = make_epub(scratch, amazon=True, bordure="--bordure" in sys.argv)
        dest.write_bytes(epub)
        (dest.parent / "couverture-kindle.jpg").write_bytes(cover_jpg(scratch, "--bordure" in sys.argv))
        print(f"  {dest} : {nfiles} fichiers, {len(epub) / 1e6:.2f} Mo (version Amazon, hors dépôt) + couverture-kindle.jpg")
        return
    print("PDF écran (liens actifs)…")
    pdf, npages = make_pdf(scratch, liens=True)
    (OUT / "marcher-sur-un-fil.pdf").write_bytes(pdf)
    print(f"  livre/marcher-sur-un-fil.pdf : {npages} pages, {len(pdf) / 1e6:.2f} Mo")
    print("PDF imprimable (A5 recto-verso)…")
    pdf, npages = make_pdf(scratch, liens=False)
    (OUT / "marcher-sur-un-fil-impression.pdf").write_bytes(pdf)
    print(f"  livre/marcher-sur-un-fil-impression.pdf : {npages} pages, {len(pdf) / 1e6:.2f} Mo")
    # L'EPUB n'est plus publié sur le site (vendu sur Amazon) : voir l'option --amazon.
    print("brouillons :", scratch)

if __name__ == "__main__":
    main()
