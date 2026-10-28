#!/usr/bin/env python3
"""
livre.py — fabrique le recueil téléchargeable à partir des mêmes données que le site
(outils/recueil.json) : un PDF au format A5 prêt à imprimer et un EPUB pour liseuses.

    python3 outils/livre.py            # écrit livre/marcher-sur-un-fil.pdf et .epub

Le PDF est mis en page par Chromium (Playwright) à partir d'un HTML : sommaire paginé
en deux passes, pages blanches insérées pour que chaque partie commence à droite,
signets. L'EPUB 3 est assemblé à la main (un fichier par texte, police EB Garamond
embarquée, sommaire de navigation). Aucun texte n'est ajouté : tout vient de recueil.json
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
MODE = {"liens": True}          # True : liens actifs (écran, EPUB) ; False : version imprimable
MOIS = ["janvier", "février", "mars", "avril", "mai", "juin", "juillet", "août",
        "septembre", "octobre", "novembre", "décembre"][datetime.date.today().month - 1]

# ------------------------------------------------------------------ textes communs
# (phrases déjà en ligne sur le site ; rien de nouveau n'est écrit ici)
COLOPHON = (f'<p>{esc(FRONT["title"])} — {esc(FRONT["subtitle"])}</p>'
            '<p>Textes de Delideal (Sébastien Nadler), écrits à partir de l’an 2000, publiés entre 2014 et 2023 '
            'sur poeme-france.com. Préface d’Isabelle Jespersen.</p>'
            f'<p>Édition numérique établie par l’auteur à partir du site delideal.art, {MOIS} {ANNEE}. '
            'Caractère : EB Garamond.</p>'
            f'<p>© {ANNEE} Delideal. Tous droits réservés.</p>')
SOURCES_INTRO = ('<p>Tous les textes de ce livre sont de Delideal (Sébastien Nadler). Écrits à partir de l’an 2000, '
                 'ils ont été publiés entre octobre 2014 et décembre 2023 sur poeme-france.com, un site tiers qui fixe '
                 'la date et l’heure de mise en ligne de chaque texte et conserve les commentaires des lecteurs de l’époque. '
                 '</p>'
                 '<p>Pour chaque texte, le tableau donne la date de première publication et son numéro sur poeme-france.com '
                 '(adresse : www.poeme-france.com/auteur/delideal/texte-<em>numéro</em>). Deux textes sont inédits. '
                 'Les copies conservées par Internet Archive sont réunies sur delideal.art/credits.html.</p>')
SOURCES_FIN = ('<p>La préface du recueil, un acrostiche, est d’Isabelle Jespersen.</p>'
               '<p>Plusieurs de ces textes existent aussi en chanson, et une improvisation au piano accompagne '
               '« Concerto pour hall de gare » : delideal.art/musique.html.</p>')

def fin_html():
    if MODE["liens"]:
        return (f'<p>Ce livre se lit gratuitement, texte par texte, sur <a href="{SITE}">delideal.art</a>. Il cherche un éditeur.</p>'
                f'<p>Si quelques textes vous touchent, vous pouvez soutenir l’auteur par un don, ponctuel ou mensuel, sur '
                f'<a href="{TIPEEE}">Tipeee</a>, lui proposer de mettre un texte en musique, ou lui écrire : '
                f'<a href="mailto:sebastien.nadler@gmail.com">sebastien.nadler@gmail.com</a>.</p>'
                f'<p>Les musiques : <a href="{SITE}/musique.html">delideal.art/musique.html</a>. Les dates, sources et copies d’archive : '
                f'<a href="{SITE}/credits.html">delideal.art/credits.html</a>.</p>')
    return ('<p>Ce livre se lit gratuitement, texte par texte, sur delideal.art. Il cherche un éditeur.</p>'
            '<p>Si quelques textes vous touchent, vous pouvez soutenir l’auteur par un don, ponctuel ou mensuel, sur Tipeee '
            '(fr.tipeee.com/delidealart), lui proposer de mettre un texte en musique, ou lui écrire : sebastien.nadler@gmail.com.</p>'
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
    if e.get("note"):
        h.append(f'<p class="note-auteur">{esc(e["note"])}</p>')
    h.append(music_html(e))
    return "".join(h)

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
.partie .chapeau{font-style:italic; color:#5b554b; margin-top:7mm; max-width:92mm; font-size:11pt}
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
"""

RECTO = ["dedicace", "preface", "ouverture", "sommaire"] + [f"partie-{P['num']}" for P in PARTS]

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
    s.append(f'<li class="autre"><a href="#sources"><span class="t">Sources</span><span class="pts"></span><span class="n">{n("sources")}</span></a></li>')
    s.append(f'<li class="autre"><a href="#fin"><span class="t">Pour continuer</span><span class="pts"></span><span class="n">{n("fin")}</span></a></li>')
    s.append('</ol></section>')
    h.append(blank("sommaire") + "".join(s))
    # parties et poèmes
    for P in PARTS:
        k = f'partie-{P["num"]}'
        h.append(blank(k) + f'<section class="page partie" id="{k}"><p class="num">{P["num"]}</p><h1>{esc(P["title"])}</h1>'
                 + (f'<p class="chapeau">{esc(P["chapeau"])}</p>' if P.get("chapeau") else "") + '</section>')
        for e in P["poems"]:
            h.append(f'<article class="poeme-page" id="{e["slug"]}">{poem_html(e, "<br>")}</article>')
    h.append(f'<section class="page sources" id="sources"><h1>Sources</h1><div class="fil"></div>{SOURCES_INTRO}{sources_table()}{SOURCES_FIN}</section>')
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
    expected += [("sources", "Sources"), ("fin", "Pour continuer")]
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
    order += ["sources", "fin"]
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
EPUB_CSS = """
%s
body{font-family:"EB Garamond",Garamond,Georgia,serif; line-height:1.5; margin:0; padding:0 .2em}
h1,h2,h3,h4{font-weight:normal; line-height:1.15; margin:0 0 .5em}
h1{font-size:1.7em} h2{font-size:1.5em; margin-top:1em} p{margin:0 0 .8em}
a{color:inherit; text-decoration:none}
.fil{height:1px; background:#9a6f0a; width:3em; margin:.4em 0 1.4em; border:0}
.titre{text-align:center; margin-top:28%%}
.titre .auteur{font-size:.9em; letter-spacing:.16em; text-transform:uppercase; color:#5b554b; margin-bottom:2em}
.titre h1{font-size:2.2em}
.titre .fil{margin:1em auto}
.titre .st{font-style:italic; color:#5b554b; font-size:1.1em}
.titre .site{margin-top:6em; color:#5b554b; font-size:.9em}
.colophon{font-size:.8em; color:#5b554b; margin-top:50%%}
.dedicace{text-align:center; font-style:italic; font-size:1.1em; margin-top:35%%}
.preface .acro{display:block; margin-bottom:.35em; padding-left:1.6em; text-indent:-1.6em}
.preface .acro strong{font-weight:500; color:#9a6f0a}
.signature{text-align:right; font-style:italic; color:#5b554b; margin-top:1.4em}
.ouverture{margin-top:35%%}
.citation{font-style:italic; font-size:1.1em}
.citation + .citation{color:#5b554b; font-style:normal; text-align:right; font-size:1em}
.partie{margin-top:25%%}
.partie .num{font-size:2.6em; color:#9a6f0a; line-height:1; margin:0 0 .3em}
.partie h1{font-size:1.9em}
.partie .chapeau{font-style:italic; color:#5b554b; margin-top:1.2em}
.sous-titre{font-style:italic; color:#5b554b}
.poeme .strophe{margin:0 0 1em}
.poeme .v{display:block; padding-left:1.6em; text-indent:-1.6em}
.poeme.acrostiche .acro-l{font-weight:500; color:#9a6f0a}
.prose p{margin:0; text-indent:1.4em; text-align:justify}
.prose p:first-child{text-indent:0}
.theatre h3{font-size:1.2em; margin:1.5em 0 .5em}
.theatre h4{font-size:1.05em; font-style:italic; margin:1.1em 0 .4em}
.theatre .didascalie{font-style:italic; color:#5b554b; font-size:.92em; margin:.5em 0}
.theatre .personnage{margin:.8em 0 .1em; font-weight:500}
.theatre .replique{margin:0 0 .3em; padding-left:1.2em}
.note-auteur{color:#5b554b; font-size:.88em; border-left:1.5px solid #bbb; padding-left:.8em; margin-top:2em}
.musique{margin-top:2em; font-size:.9em; color:#5b554b}
.musique a,.fin a,.sources a,.colophon a{color:#9a6f0a; text-decoration:underline}
table{width:100%%; border-collapse:collapse; font-size:.85em; margin-top:1em}
th,td{text-align:left; padding:.25em .4em .25em 0; border-bottom:1px solid #ddd; vertical-align:top}
th{font-weight:500}
tr.partie-row td{padding-top:.9em; font-style:italic; color:#5b554b; border-bottom:none}
nav ol{list-style:none; padding-left:0} nav ol ol{padding-left:1.2em; font-size:.95em}
nav li{margin:.25em 0}
"""

def xhtml(title, body, cls=""):
    return ('<?xml version="1.0" encoding="utf-8"?>\n<!DOCTYPE html>\n'
            '<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" xml:lang="fr" lang="fr">'
            f'<head><meta charset="utf-8"/><title>{esc(title)}</title><link rel="stylesheet" type="text/css" href="../style.css"/></head>'
            f'<body class="{cls}">{body}</body></html>')

def to_xhtml_fragment(s):
    """Nos fragments HTML n'utilisent que des balises fermées, sauf <br> et <hr> ; on les ferme."""
    return s.replace("<br>", "<br/>").replace("<hr>", "<hr/>").replace('<div class="fil"></div>', '<hr class="fil"/>')

def cover_png(scratch):
    """Couverture typographique (titre, sous-titre, nom) : texte seulement, aucune illustration."""
    from playwright.sync_api import sync_playwright
    html = ('<!DOCTYPE html><html lang="fr"><head><meta charset="utf-8"><style>' + font_faces(FONTS.as_uri() + "/") +
            'html,body{margin:0;width:1600px;height:2400px;background:#fbf7ef;color:#1a1712;font-family:"EB Garamond"}'
            '.c{position:absolute;inset:0;text-align:center;padding-top:620px}'
            '.a{font-size:52px;letter-spacing:.18em;text-transform:uppercase;color:#5b554b;margin:0 0 140px}'
            'h1{font-weight:400;font-size:150px;margin:0;line-height:1.1}'
            '.fil{position:relative;height:3px;background:rgba(26,23,18,.25);width:520px;margin:70px auto}'
            '.fil::after{content:"";position:absolute;left:calc(50% - 14px);top:-13px;width:30px;height:30px;border-radius:50%;background:#9a6f0a}'
            '.st{font-style:italic;font-size:64px;color:#5b554b;margin:0}'
            '.site{position:absolute;bottom:160px;left:0;right:0;text-align:center;font-size:44px;color:#5b554b;letter-spacing:.06em}'
            '</style></head><body><div class="c"><p class="a">Delideal</p>'
            f'<h1>{esc(FRONT["title"])}</h1><div class="fil"></div><p class="st">{esc(FRONT["subtitle"])}</p></div>'
            '<p class="site">delideal.art</p></body></html>')
    src = scratch / "couverture.html"; src.write_text(html, encoding="utf-8")
    png = scratch / "couverture.png"
    with sync_playwright() as p:
        b = p.chromium.launch(); pg = b.new_page(viewport={"width": 1600, "height": 2400})
        pg.goto(src.as_uri()); pg.wait_for_load_state("networkidle"); pg.evaluate("document.fonts.ready")
        pg.screenshot(path=str(png), full_page=False); b.close()
    return png.read_bytes()

def make_epub(scratch):
    MODE["liens"] = True
    files = []   # (href, media-type, bytes, properties)
    spine = []   # ids
    nav_items = []  # (href, title, [children])
    def add(href, data, mt="application/xhtml+xml", props=None, in_spine=True):
        fid = re.sub(r"[^a-z0-9]", "-", href.lower())
        files.append((fid, href, mt, data, props))
        if in_spine: spine.append(fid)
        return href
    add("style.css", (EPUB_CSS % font_faces("fonts/")).encode(), "text/css", in_spine=False)
    for (w, s), f in FONT_FILES.items():
        add(f"fonts/{f}", (FONTS / f).read_bytes(), "font/woff", in_spine=False)
    add("couverture.png", cover_png(scratch), "image/png", props="cover-image", in_spine=False)
    add("text/couverture.xhtml", xhtml("Couverture", '<div style="text-align:center"><img src="../couverture.png" alt="Marcher sur un fil — Fragments de sensibilité bipolaire — Delideal" style="max-width:100%;max-height:100%"/></div>').encode())
    add("text/titre.xhtml", xhtml(FRONT["title"], f'<section class="titre"><p class="auteur">Delideal</p><h1>{esc(FRONT["title"])}</h1><hr class="fil"/><p class="st">{esc(FRONT["subtitle"])}</p><p class="site">delideal.art</p></section>').encode())
    add("text/colophon.xhtml", xhtml("Colophon", f'<section class="colophon">{COLOPHON}</section>').encode())
    add("text/dedicace.xhtml", xhtml("Dédicace", f'<section class="dedicace"><p>{esc(FRONT["dedicace"])}</p></section>').encode())
    nav_items.append(("text/dedicace.xhtml", "Dédicace", []))
    add("text/preface.xhtml", xhtml("Préface", f'<section class="preface"><h1>Préface</h1><hr class="fil"/>{preface_html()}</section>').encode())
    nav_items.append(("text/preface.xhtml", "Préface", []))
    add("text/ouverture.xhtml", xhtml("Ouverture", '<section class="ouverture">' + "".join(f'<p class="citation">{esc(l)}</p>' for l in FRONT["ouverture"]) + '</section>').encode())
    for P in PARTS:
        href = f'text/partie-{P["num"]}.xhtml'
        add(href, xhtml(P["title"], f'<section class="partie"><p class="num">{P["num"]}</p><h1>{esc(P["title"])}</h1>' + (f'<p class="chapeau">{esc(P["chapeau"])}</p>' if P.get("chapeau") else "") + '</section>').encode())
        kids = []
        for e in P["poems"]:
            ph = f'text/{e["slug"]}.xhtml'
            add(ph, xhtml(e["title"], f'<article class="poeme-page">{to_xhtml_fragment(poem_html(e, "<br/>"))}</article>').encode())
            kids.append((ph, e["title"], []))
        nav_items.append((href, f'{P["num"]}. {P["title"]}', kids))
    add("text/sources.xhtml", xhtml("Sources", f'<section class="sources"><h1>Sources</h1><hr class="fil"/>{SOURCES_INTRO}{sources_table()}{SOURCES_FIN}</section>').encode())
    nav_items.append(("text/sources.xhtml", "Sources", []))
    add("text/fin.xhtml", xhtml("Pour continuer", f'<section class="fin"><h1>Pour continuer</h1><hr class="fil"/>{fin_html()}</section>').encode())
    nav_items.append(("text/fin.xhtml", "Pour continuer", []))
    # navigation (EPUB 3) + NCX (anciens lecteurs)
    def ol(items):
        return "<ol>" + "".join(f'<li><a href="{h}">{esc(t)}</a>{ol(k) if k else ""}</li>' for h, t, k in items) + "</ol>"
    nav = ('<?xml version="1.0" encoding="utf-8"?>\n<!DOCTYPE html>\n'
           '<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" xml:lang="fr" lang="fr">'
           '<head><meta charset="utf-8"/><title>Sommaire</title><link rel="stylesheet" type="text/css" href="style.css"/></head><body>'
           '<nav epub:type="toc" id="toc"><h1>Sommaire</h1>' + ol(nav_items) + '</nav>'
           '<nav epub:type="landmarks" hidden="hidden"><ol>'
           '<li><a epub:type="cover" href="text/couverture.xhtml">Couverture</a></li>'
           '<li><a epub:type="toc" href="nav.xhtml">Sommaire</a></li>'
           f'<li><a epub:type="bodymatter" href="text/partie-{PARTS[0]["num"]}.xhtml">Début de la lecture</a></li>'
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
    ncx = ('<?xml version="1.0" encoding="utf-8"?>\n<ncx xmlns="http://www.daisy.org/z3986/2005/ncx/" version="2005-1" xml:lang="fr">'
           f'<head><meta name="dtb:uid" content="{uid}"/><meta name="dtb:depth" content="2"/><meta name="dtb:totalPageCount" content="0"/><meta name="dtb:maxPageNumber" content="0"/></head>'
           f'<docTitle><text>{esc(FRONT["title"])}</text></docTitle><navMap>{ncx_points(nav_items)}</navMap></ncx>')
    add("toc.ncx", ncx.encode(), "application/x-dtbncx+xml", in_spine=False)
    modified = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    manifest = "".join(f'<item id="{fid}" href="{href}" media-type="{mt}"' + (f' properties="{props}"' if props else "") + '/>'
                       for fid, href, mt, _, props in files)
    opf = ('<?xml version="1.0" encoding="utf-8"?>\n'
           '<package xmlns="http://www.idpf.org/2007/opf" version="3.0" unique-identifier="uid" xml:lang="fr">'
           '<metadata xmlns:dc="http://purl.org/dc/elements/1.1/">'
           f'<dc:identifier id="uid">{uid}</dc:identifier>'
           f'<dc:title id="t">{esc(FRONT["title"])}</dc:title><meta refines="#t" property="title-type">main</meta>'
           f'<dc:title id="st">{esc(FRONT["subtitle"])}</dc:title><meta refines="#st" property="title-type">subtitle</meta>'
           '<dc:creator id="a">Delideal</dc:creator><meta refines="#a" property="role" scheme="marc:relators">aut</meta>'
           '<dc:contributor id="p">Isabelle Jespersen</dc:contributor><meta refines="#p" property="role" scheme="marc:relators">aui</meta>'
           f'<dc:language>fr</dc:language><dc:date>{datetime.date.today().isoformat()}</dc:date>'
           f'<dc:publisher>delideal.art</dc:publisher><dc:rights>© {ANNEE} Delideal. Tous droits réservés.</dc:rights>'
           f'<dc:description>Recueil de poèmes de Delideal : {esc(FRONT["subtitle"])}. Textes écrits à partir de l’an 2000, publiés entre 2014 et 2023.</dc:description>'
           f'<meta property="dcterms:modified">{modified}</meta><meta name="cover" content="couverture-png"/>'
           '</metadata>'
           f'<manifest>{manifest}</manifest>'
           '<spine toc="toc-ncx">' + "".join(f'<itemref idref="{i}"/>' for i in spine) + '</spine>'
           '</package>')
    container = ('<?xml version="1.0" encoding="utf-8"?>\n<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">'
                 '<rootfiles><rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/></rootfiles></container>')
    # vérification : chaque XML est bien formé
    for fid, href, mt, data, _ in files:
        if mt in ("application/xhtml+xml", "application/x-dtbncx+xml"):
            ET.fromstring(data)
    ET.fromstring(opf.encode()); ET.fromstring(container.encode())
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as z:
        z.writestr(zipfile.ZipInfo("mimetype"), b"application/epub+zip", compress_type=zipfile.ZIP_STORED)
        z.writestr("META-INF/container.xml", container, compress_type=zipfile.ZIP_DEFLATED)
        z.writestr("OEBPS/content.opf", opf, compress_type=zipfile.ZIP_DEFLATED)
        for fid, href, mt, data, _ in files:
            z.writestr("OEBPS/" + href, data, compress_type=zipfile.ZIP_DEFLATED)
    return buf.getvalue(), len(files)

# ------------------------------------------------------------------ principal
def main():
    import tempfile
    OUT.mkdir(exist_ok=True)
    scratch = Path(tempfile.mkdtemp(prefix="livre-"))
    print("PDF écran (liens actifs)…")
    pdf, npages = make_pdf(scratch, liens=True)
    (OUT / "marcher-sur-un-fil.pdf").write_bytes(pdf)
    print(f"  livre/marcher-sur-un-fil.pdf : {npages} pages, {len(pdf) / 1e6:.2f} Mo")
    print("PDF imprimable (A5 recto-verso)…")
    pdf, npages = make_pdf(scratch, liens=False)
    (OUT / "marcher-sur-un-fil-impression.pdf").write_bytes(pdf)
    print(f"  livre/marcher-sur-un-fil-impression.pdf : {npages} pages, {len(pdf) / 1e6:.2f} Mo")
    print("EPUB…")
    epub, nfiles = make_epub(scratch)
    (OUT / "marcher-sur-un-fil.epub").write_bytes(epub)
    print(f"  livre/marcher-sur-un-fil.epub : {nfiles} fichiers, {len(epub) / 1e6:.2f} Mo")
    print("brouillons :", scratch)

if __name__ == "__main__":
    main()
