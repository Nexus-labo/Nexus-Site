#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Construit le site NexusLab à partir des templates et des contenus par langue.

Usage : python3 build.py
Sortie : le dossier ../site, prêt à être zippé et déposé sur Netlify.

Ajouter une langue : créer content/xx.py sur le modèle de content/fr.py,
puis l'ajouter à LANGS ci-dessous. Les balises hreflang, le sélecteur de
langue et le sitemap se mettent à jour tout seuls.
"""
import html
import importlib
import json
import os
import re
import sys
from datetime import date

HERE = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.normpath(os.path.join(HERE, "..", "site"))
SITE_URL = "https://nexus-lab.ch"
LANGS = ["fr"]  # ordre d'affichage dans le sélecteur ; "fr" doit rester la racine
import hashlib


def _version():
    """Empreinte du CSS et du JS : change à chaque modification, ce qui force les navigateurs à recharger."""
    h = hashlib.sha1()
    for rel in ("assets/css/style.css", "assets/js/main.js"):
        with open(os.path.join(SITE, rel), "rb") as f:
            h.update(f.read())
    return h.hexdigest()[:10]


VERSION = _version()

sys.path.insert(0, HERE)

DEFAULT_SLUGS = {
    "fr": {"legal": "mentions-legales", "privacy": "protection-donnees", "thanks": "merci"},
    "de": {"legal": "impressum", "privacy": "datenschutz", "thanks": "danke"},
    "en": {"legal": "legal-notice", "privacy": "privacy", "thanks": "thank-you"},
}

LOGO_SVG = (
    '<svg class="logo-mark" viewBox="0 0 48 22" aria-hidden="true" focusable="false">'
    '<rect class="link" x="18" y="7.9" width="10" height="6.2" rx="1"/>'
    '<circle class="dot-a" cx="11" cy="11" r="10.5"/>'
    '<circle class="dot-b" cx="36.5" cy="11" r="10.5"/>'
    '</svg>'
)

HERO_ART = """<svg viewBox="0 0 520 440" fill="none" xmlns="http://www.w3.org/2000/svg">
  <g stroke="#14213D" stroke-width="2" stroke-linecap="round" opacity="0.28">
    <path d="M78 128 L206 68"/><path d="M206 68 L326 156"/><path d="M326 156 L462 96"/>
    <path d="M78 128 L152 300"/><path d="M152 300 L298 328"/><path d="M298 328 L326 156"/>
    <path d="M326 156 L430 262"/><path d="M430 262 L462 96"/><path d="M430 262 L392 388"/><path d="M298 328 L392 388"/>
  </g>
  <g class="float">
    <circle cx="78" cy="128" r="11" fill="#14213D"/>
    <circle cx="206" cy="68" r="8" fill="#14213D" opacity="0.7"/>
    <circle cx="462" cy="96" r="7" fill="#14213D" opacity="0.5"/>
    <circle cx="152" cy="300" r="9" fill="#14213D" opacity="0.8"/>
  </g>
  <g class="float delay">
    <circle cx="298" cy="328" r="7" fill="#14213D" opacity="0.6"/>
    <circle cx="430" cy="262" r="12" fill="#14213D"/>
    <circle cx="392" cy="388" r="6" fill="#14213D" opacity="0.5"/>
  </g>
  <g class="float">
    <circle cx="326" cy="156" r="34" fill="#FF6B57" opacity="0.14"/>
    <circle cx="326" cy="156" r="16" fill="#FF6B57"/>
  </g>
</svg>"""

# ---------------------------------------------------------------------------
# Montagnes : silhouettes des Alpes générées une fois pour toutes (SVG léger, pas de photo).
# Bruit « en crêtes » pour des sommets pointus, plus un sommet en pyramide inspiré du Cervin.
import math
import random


def _ridge(width, base, amp, seed, freqs=(0.004, 0.009, 0.021, 0.047), step=8, peak=None):
    rnd = random.Random(seed)
    phases = [rnd.uniform(0, 6.283) for _ in freqs]
    weights = [1.0, 0.55, 0.28, 0.12]
    pts = []
    for x in range(0, width + step, step):
        h = 0.0
        for f, ph, w in zip(freqs, phases, weights):
            h += w * (1 - abs(math.sin(x * f + ph))) ** 1.6
        h = h / sum(weights)
        y = base - amp * h + rnd.uniform(-1.6, 1.6)
        if peak:
            y = min(y, peak(x))
        pts.append((x, round(y, 1)))
    return pts


def _cervin(cx, top, half):
    """Profil inspiré du Cervin : arête gauche longue et concave, sommet au nez légèrement penché,
    face droite plus raide. Points relatifs (dx, dy) en unités de « half », interpolés en x."""
    prof = [(-5.0, 4.2), (-2.2, 1.9), (-1.5, 1.35), (-1.0, 0.95), (-0.62, 0.62), (-0.36, 0.36), (-0.2, 0.17),
            (-0.1, 0.05), (-0.03, 0.0), (0.04, 0.02), (0.08, 0.07), (0.12, 0.06), (0.2, 0.22),
            (0.34, 0.5), (0.52, 0.86), (0.78, 1.25), (1.2, 1.7), (1.8, 2.1), (4.0, 3.6)]
    pts = [(cx + dx * half, top + dy * half) for dx, dy in prof]

    def f(x):
        if x <= pts[0][0] or x >= pts[-1][0]:
            return 10 ** 6
        for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
            if x0 <= x <= x1:
                return y0 + (y1 - y0) * (x - x0) / (x1 - x0)
        return 10 ** 6
    return f


def _path(pts, width, height):
    d = "M0 %d " % height + " ".join("L%s %s" % (x, y) for x, y in pts) + " L%d %d Z" % (width, height)
    return d


def _rim(pts):
    return "M" + " L".join("%s %s" % (x, y) for x, y in pts)


def _cervin_shade(cx, top, half, height):
    """Face à l'ombre du sommet (côté droit) : donne le relief de la pyramide."""
    right = [(0.04, 0.02), (0.08, 0.07), (0.12, 0.06), (0.2, 0.22), (0.34, 0.5), (0.52, 0.86),
             (0.78, 1.25), (1.2, 1.7), (1.8, 2.1), (4.0, 3.6)]
    pts = [(cx - 0.03 * half, top)] + [(cx + dx * half, top + dy * half) for dx, dy in right]
    pts = [(x, min(y, height)) for x, y in pts]
    pts += [(cx + 0.9 * half, height), (cx + 0.05 * half, top + 1.2 * half), (cx - 0.02 * half, top + 0.3 * half)]
    return "M" + " L".join("%s %s" % (round(x, 1), round(y, 1)) for x, y in pts) + " Z"


def _snow(pts, snowline, seed):
    """Calotte de neige : la partie de la crête au-dessus d'une limite irrégulière."""
    rnd = random.Random(seed)
    top = [(x, y) for x, y in pts]
    bottom = []
    for x, y in reversed(pts):
        line = snowline + 14 * math.sin(x * 0.03 + rnd.uniform(0, 0.4)) + rnd.uniform(-6, 6)
        bottom.append((x, max(y, line)))
    return "M" + " L".join("%s %s" % (x, round(y, 1)) for x, y in top + bottom) + " Z"


def matterhorn(cx, base_y, scale, night=False):
    """Cervin vu de Zermatt, en aplats : arête du Hörnli au centre (face est éclairée à gauche,
    face nord à l'ombre à droite), épaule sur l'arête droite, double sommet au nez penché,
    calotte de neige, couloirs enneigés, bancs de roche et glacier au pied."""
    def T(pts):
        return " L".join("%.1f %.1f" % (cx + x * scale, base_y - (380 - y) * scale) for x, y in pts)

    def poly(pts):
        return "M" + T(pts) + " Z"

    outline = [(-300, 380), (-232, 300), (-176, 232), (-134, 176), (-100, 128), (-72, 88), (-50, 56),
               (-32, 30), (-18, 12), (-9, 3), (-3, -1), (4, -4), (9, -3), (13, 1), (17, 0), (22, 3),
               (30, 13), (42, 33), (55, 58), (66, 76), (82, 87), (100, 94), (116, 104), (130, 122),
               (154, 162), (192, 222), (240, 296), (306, 380)]
    shadow = [(4, -4), (9, -3), (13, 1), (17, 0), (22, 3), (30, 13), (42, 33), (55, 58), (66, 76),
              (82, 87), (100, 94), (116, 104), (130, 122), (154, 162), (192, 222), (240, 296), (306, 380),
              (72, 380), (56, 300), (40, 222), (28, 150), (18, 88), (10, 36)]
    snow = [(-50, 56), (-32, 30), (-18, 12), (-9, 3), (-3, -1), (4, -4), (9, -3), (13, 1), (17, 0), (22, 3),
            (30, 13), (42, 33), (55, 58), (49, 61), (44, 74), (39, 63), (33, 68), (28, 90), (23, 70),
            (17, 64), (12, 84), (7, 66), (1, 62), (-5, 79), (-10, 60), (-17, 58), (-22, 71), (-28, 57),
            (-36, 62), (-42, 55)]
    shoulder = [(60, 70), (80, 84), (100, 92), (118, 104), (108, 112), (92, 106), (80, 112), (70, 98)]
    couloirs = [  # couloirs de neige effilés sur la face nord, plus larges vers le bas
        [(40, 104), (43, 103), (50, 150), (58, 204), (62, 236), (54, 238), (49, 200), (43, 150)],
        [(78, 128), (81, 127), (92, 180), (106, 240), (114, 272), (105, 274), (96, 236), (86, 182)],
        [(118, 170), (121, 170), (134, 220), (150, 280), (156, 306), (148, 308), (140, 278), (127, 222)],
        [(26, 150), (28, 150), (33, 196), (38, 238), (33, 240), (29, 198)],
    ]
    ledges = [  # petites vires enneigées sur la face éclairée
        [(-70, 112), (-46, 104), (-30, 108), (-48, 114)],
        [(-112, 168), (-80, 158), (-62, 162), (-86, 172)],
        [(-150, 226), (-112, 214), (-96, 220), (-126, 230)],
        [(-46, 150), (-28, 144), (-20, 148), (-36, 154)],
    ]
    strata = [[(-128, 216), (-40, 196)], [(-162, 262), (-34, 236)], [(-204, 318), (-30, 286)],
              [(-92, 168), (-26, 154)], [(-236, 360), (-20, 336)]]
    glacier = [(150, 380), (178, 336), (214, 318), (252, 322), (282, 344), (306, 380)]
    if night:
        body, rock_shadow, snow_c, snow_o, line_c, rim_o = "#1A2950", "#0B1430", "#DCE4F5", 0.55, "#0B1430", 0.4
    else:
        body, rock_shadow, snow_c, snow_o, line_c, rim_o = "url(#mh-body)", "#14213D", "#FFFFFF", 0.95, "#14213D", 0.75
    out = []
    if not night:
        out.append('<defs><linearGradient id="mh-body" x1="0" y1="0" x2="0" y2="1">'
                   '<stop offset="0" stop-color="#AEB5C3"/><stop offset="1" stop-color="#E6E2DC"/></linearGradient></defs>')
    out.append('<path d="%s" fill="%s"/>' % (poly(outline), body))
    out += ['<path d="M%s" fill="none" stroke="%s" stroke-opacity="0.09" stroke-width="%.1f" stroke-linecap="round"/>'
            % (T(l), line_c, 1.6 * scale) for l in strata]
    out.append('<path d="%s" fill="%s" fill-opacity="%.2f"/>' % (poly(snow), snow_c, snow_o))
    out.append('<path d="%s" fill="%s" fill-opacity="%.2f"/>' % (poly(shoulder), snow_c, snow_o * 0.9))
    out += ['<path d="%s" fill="%s" fill-opacity="%.2f"/>' % (poly(c), snow_c, snow_o * 0.42) for c in couloirs]
    out += ['<path d="%s" fill="%s" fill-opacity="%.2f"/>' % (poly(c), snow_c, snow_o * 0.7) for c in ledges]
    out.append('<path d="%s" fill="%s" fill-opacity="%.2f"/>' % (poly(glacier), snow_c, snow_o * 0.6))
    out.append('<path d="%s" fill="%s" fill-opacity="%.2f"/>' % (poly(shadow), rock_shadow, 0.17 if not night else 0.45))
    out.append('<path d="M%s" fill="none" stroke="#FFFFFF" stroke-opacity="%.2f" stroke-width="%.1f" stroke-linejoin="round"/>'
               % (T(outline[1:-1]), rim_o, 1.3 * max(scale, 0.8)))
    return '<g class="matterhorn">%s</g>' % "".join(out)


def alps_hero():
    W, H = 1600, 520
    far = _ridge(W, 330, 190, 3)
    mid = _ridge(W, 430, 150, 7)
    near = _ridge(W, 480, 105, 11, freqs=(0.006, 0.013, 0.03, 0.06))
    front = _ridge(W, 518, 50, 19, freqs=(0.003, 0.008, 0.02, 0.05))
    grad = lambda i, a, b: (
        '<linearGradient id="alps-g%d" x1="0" y1="0" x2="0" y2="1">'
        '<stop offset="0" stop-color="%s"/><stop offset="1" stop-color="%s"/></linearGradient>' % (i, a, b))
    return (
        '<svg class="hero-alps" viewBox="0 0 %d %d" preserveAspectRatio="xMidYMax meet" aria-hidden="true" focusable="false">'
        '<defs>%s%s%s</defs>'
        '<g class="alps-layer" data-depth="0.25"><path d="%s" fill="url(#alps-g1)"/>'
        '<path d="%s" fill="#FFFFFF" fill-opacity="0.85"/></g>'
        '<g class="alps-layer" data-depth="0.5"><path d="%s" fill="url(#alps-g2)"/>'
        '<path d="%s" fill="#FFFFFF" fill-opacity="0.92"/>'
        '<path d="%s" fill="none" stroke="#FFFFFF" stroke-opacity="0.7" stroke-width="1.3"/>'
        '%s</g>'
        '<g class="alps-layer" data-depth="0.8"><path d="%s" fill="url(#alps-g3)"/>'
        '<path d="%s" fill="none" stroke="#FFFFFF" stroke-opacity="0.45" stroke-width="1.1"/></g>'
        '<g class="alps-layer" data-depth="1.1"><path d="%s" fill="#F6F2EC"/></g>'
        '</svg>'
    ) % (W, H,
         grad(1, "#D9D7D6", "#EEEAE4"), grad(2, "#B9BFCB", "#E9E5DF"), grad(3, "#98A1B3", "#E3DFD9"),
         _path(far, W, H), _snow(far, 186, 31),
         _path(mid, W, H), _snow(mid, 128, 37), _rim(mid), matterhorn(1230, 470, 1.0),
         _path(near, W, H), _rim(near),
         _path(front, W, H))


def alps_footer():
    W, H = 1600, 110
    back = _ridge(W, 96, 70, 23)
    front = _ridge(W, 110, 52, 29, peak=_cervin(320, 30, 40))
    return (
        '<svg class="footer-alps" viewBox="0 0 %d %d" preserveAspectRatio="none" aria-hidden="true" focusable="false">'
        '<path d="%s" fill="#14213D" fill-opacity="0.45"/><path d="%s" fill="#14213D"/></svg>'
    ) % (W, H, _path(back, W, H), _path(front, W, H))


def alps_night():
    """Paysage nocturne : crêtes éclairées par la lune, neige pâle, lumières de villages en corail."""
    W, H = 1600, 300
    far = _ridge(W, 190, 150, 41)
    mid = _ridge(W, 240, 150, 43)
    near = _ridge(W, 278, 95, 47, freqs=(0.006, 0.013, 0.03, 0.06))
    front = _ridge(W, 300, 48, 53, freqs=(0.003, 0.008, 0.02, 0.05))
    rnd = random.Random(59)
    lights = []
    # villages : petits groupes de lumières sur les pentes du plan proche
    for cx in (180, 520, 860, 1130, 1420):
        base_y = dict(near).get(cx - cx % 8, 260)
        for _ in range(rnd.randint(3, 7)):
            x = cx + rnd.uniform(-38, 38)
            y = base_y + rnd.uniform(14, 34)
            if y < H - 4:
                lights.append('<circle class="village" cx="%.1f" cy="%.1f" r="%.1f" style="animation-delay:-%.1fs"/>'
                              % (x, y, rnd.uniform(1.1, 2.0), rnd.uniform(0, 6)))
    return (
        '<svg class="night-alps" viewBox="0 0 %d %d" preserveAspectRatio="xMidYMax meet" aria-hidden="true" focusable="false">'
        '<defs><radialGradient id="glow-v"><stop offset="0" stop-color="#FFB37A" stop-opacity="0.55"/>'
        '<stop offset="1" stop-color="#FFB37A" stop-opacity="0"/></radialGradient></defs>'
        '<path d="%s" fill="#24365F"/><path d="%s" fill="#DCE4F5" fill-opacity="0.16"/>'
        '<path d="%s" fill="none" stroke="#C9D1E0" stroke-opacity="0.22" stroke-width="1"/>'
        '<path d="%s" fill="#1A2950"/><path d="%s" fill="#DCE4F5" fill-opacity="0.22"/>'
        '<path d="%s" fill="none" stroke="#C9D1E0" stroke-opacity="0.38" stroke-width="1.2"/>'
        '%s'
        '<path d="%s" fill="#121F3F"/>'
        '<path d="%s" fill="#0D1730"/>'
        '<g class="villages">%s</g>'
        '</svg>'
    ) % (W, H,
         _path(far, W, H), _snow(far, 92, 61), _rim(far),
         _path(mid, W, H), _snow(mid, 76, 67), _rim(mid), matterhorn(420, 292, 0.68, night=True),
         _path(near, W, H), _path(front, W, H), "".join(lights))


SWISS_FLAG = (
    '<svg class="swiss-flag" viewBox="0 0 32 32" aria-hidden="true" focusable="false">'
    '<rect width="32" height="32" rx="5" fill="#DA291C"/>'
    '<path d="M13 6h6v7h7v6h-7v7h-6v-7H6v-6h7z" fill="#FFFFFF"/></svg>'
)


ICONS = {
    "arrow": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 12h14M13 6l6 6-6 6"/></svg>',
    "target": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="4.5"/><circle cx="12" cy="12" r="1" fill="currentColor"/></svg>',
    "home": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M3 11l9-8 9 8"/><path d="M5 10v10h14V10"/><path d="M10 20v-6h4v6"/></svg>',
    "phone": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M22 16.9v3a2 2 0 0 1-2.2 2 19.8 19.8 0 0 1-8.6-3.1 19.5 19.5 0 0 1-6-6A19.8 19.8 0 0 1 2.1 4.2 2 2 0 0 1 4.1 2h3a2 2 0 0 1 2 1.7c.1.9.4 1.8.7 2.6a2 2 0 0 1-.5 2.1L8.1 9.7a16 16 0 0 0 6 6l1.3-1.3a2 2 0 0 1 2.1-.4c.8.3 1.7.5 2.6.7a2 2 0 0 1 1.7 2z"/></svg>',
}
PRINCIPLE_ICONS = ["target", "home", "phone"]


def esc(text):
    return html.escape(str(text), quote=True)


def read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def write(rel, content):
    path = os.path.join(SITE, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(content)
    print("  écrit", rel)


def render(template, mapping):
    out = template
    for key, value in mapping.items():
        out = out.replace("{{" + key + "}}", str(value))
    leftover = re.findall(r"{{\w+}}", out)
    if leftover:
        raise SystemExit("Jetons non remplacés : " + ", ".join(sorted(set(leftover))))
    return out


def load(lang):
    mod = importlib.import_module("content." + lang)
    mod.slugs = getattr(mod, "slugs", DEFAULT_SLUGS[lang])
    return mod


def page_path(lang, kind):
    """Chemin absolu (sur le site) d'une page pour une langue."""
    prefix = "" if lang == "fr" else "/" + lang
    if kind == "home":
        return prefix + "/"
    return prefix + "/" + DEFAULT_SLUGS[lang][kind] + "/"


def hreflang_tags(kind, langs):
    tags = []
    for lang in langs:
        tags.append('<link rel="alternate" hreflang="%s" href="%s%s">' % (lang, SITE_URL, page_path(lang, kind)))
    tags.append('<link rel="alternate" hreflang="x-default" href="%s%s">' % (SITE_URL, page_path("fr", kind)))
    return "\n".join(tags)


def lang_switch(current, kind, langs, mods):
    parts = []
    for lang in langs:
        short = mods[lang].meta["lang_short"]
        label = mods[lang].meta["lang_label"]
        if lang == current:
            parts.append('<span aria-current="true" lang="%s" title="%s">%s</span>' % (lang, esc(label), short))
        else:
            parts.append('<a href="%s" lang="%s" hreflang="%s" title="%s">%s</a>' % (page_path(lang, kind), lang, lang, esc(label), short))
    return "".join(parts)


def footer_lang_links(current, kind, langs, mods):
    parts = []
    for lang in langs:
        label = mods[lang].meta["lang_label"]
        if lang == current:
            parts.append('<li><span aria-current="true">%s</span></li>' % esc(label))
        else:
            parts.append('<li><a href="%s" lang="%s" hreflang="%s">%s</a></li>' % (page_path(lang, kind), lang, lang, esc(label)))
    return "".join(parts)


def common_mapping(c, kind, langs, mods):
    lang = c.LANG
    home = page_path(lang, "home")
    nav_links = "".join('<a href="%s%s">%s</a>' % (home if kind != "home" else "", href, esc(label)) for href, label in c.nav["links"])
    footer_nav = "".join('<li><a href="%s%s">%s</a></li>' % (home, href, esc(label)) for href, label in c.nav["links"])
    footer_legal = "".join(
        '<li><a href="%s">%s</a></li>' % (page_path(lang, k), esc(label))
        for k, label in (("legal", c.legal["title"]), ("privacy", c.privacy["title"]))
    )
    return {
        "lang": lang,
        "locale": c.LOCALE,
        "site_url": SITE_URL,
        "version": VERSION,
        "home": home,
        "home_label": esc(c.nav.get("home_label", "accueil")),
        "wordmark": esc(c.brand["wordmark"]),
        "logo_svg": LOGO_SVG,
        "skip": esc(c.nav["skip"]),
        "nav_label": esc(c.nav.get("nav_label", "Navigation")),
        "nav_links": nav_links,
        "nav_cta": esc(c.nav["cta"]),
        "lang_title": esc(c.nav["lang_title"]),
        "lang_switch": lang_switch(lang, kind, langs, mods),
        "menu_open": esc(c.nav["menu_open"]),
        "menu_close": esc(c.nav["menu_close"]),
        "footer_signature": esc(c.footer["signature"]),
        "footer_about": esc(c.footer["about"]),
        "footer_nav_title": esc(c.footer["nav_title"]),
        "footer_nav_links": footer_nav,
        "footer_legal_title": esc(c.footer["legal_title"]),
        "footer_legal_links": footer_legal,
        "footer_lang_title": esc(c.footer["lang_title"]),
        "footer_lang_links": footer_lang_links(lang, kind, langs, mods),
        "footer_copyright": esc(c.footer["copyright"]),
        "footer_made": SWISS_FLAG + "<span>" + esc(c.footer["made"]) + "</span>",
        "footer_alps": alps_footer(),
    }


def jsonld(c):
    home = SITE_URL + page_path(c.LANG, "home")
    data = {
        "@context": "https://schema.org",
        "@graph": [
            {
                "@type": "ProfessionalService",
                "@id": SITE_URL + "/#organisation",
                "name": c.brand["name"],
                "url": home,
                "logo": SITE_URL + "/favicon-512x512.png",
                "image": SITE_URL + "/assets/img/og-image.png",
                "description": c.meta["description"],
                "slogan": c.brand["signature"],
                "telephone": c.brand["phone_tel"],
                "priceRange": "CHF 690+",
                "areaServed": [
                    {"@type": "AdministrativeArea", "name": "Valais"},
                    {"@type": "AdministrativeArea", "name": "Suisse romande"},
                ],
                "address": {"@type": "PostalAddress", "addressRegion": "Valais", "addressCountry": "CH"},
                "member": [{"@type": "Person", "name": m[0], "jobTitle": r} for m, r in zip(c.team["members"], c.team["roles"])],
            },
            {
                "@type": "WebSite",
                "@id": SITE_URL + "/#site",
                "url": home,
                "name": c.brand["name"],
                "inLanguage": c.LOCALE.replace("_", "-"),
                "publisher": {"@id": SITE_URL + "/#organisation"},
            },
            {
                "@type": "FAQPage",
                "mainEntity": [
                    {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}}
                    for q, a in c.faq["items"]
                ],
            },
        ],
    }
    return json.dumps(data, ensure_ascii=False, separators=(",", ":"))


def hero_title_html(c):
    title = esc(c.hero["title"])
    pair = c.hero.get("title_glitch")
    if not pair:
        return title
    word, alt = (esc(x) for x in pair)
    span = ('<span class="glitch" tabindex="0" data-word="%s" data-alt="%s">'
            '<span class="glitch-text">%s</span></span>' % (word, alt, word))
    return title.replace(word, span, 1)


def middle_sections(c):
    """Sections entre l'accueil et le contact. Volontairement différentes les unes des autres :
    grille de prix, nuit étoilée, équipe sans cartes, étude de cas asymétrique, terminal, FAQ en deux colonnes."""
    def tag(t):
        return '<p class="tag">%s</p>' % esc(t) if t else ""

    H = []
    # Formules : en-tête en deux colonnes, cartes de prix
    cards = []
    for card in c.offers["cards"]:
        cls = "card offer reveal" + (" featured" if card["featured"] else "")
        badge = '<span class="offer-badge">%s</span>' % esc(c.offers["featured_label"]) if card["featured"] else ""
        period = '<span class="period">%s</span>' % esc(card["period"]) if card["period"] else ""
        items = "".join("<li>%s</li>" % esc(i) for i in card["items"])
        cards.append(
            '<article class="%s">%s<h3 class="offer-name">%s</h3>'
            '<p class="offer-price"><span class="from">%s</span><span class="amount">%s</span>%s</p>'
            '<p class="offer-text">%s</p><ul class="offer-list">%s</ul></article>'
            % (cls, badge, esc(card["name"]), esc(c.offers["from"]), esc(card["price"]), period, esc(card["text"]), items))
    H.append(
        '<section class="section" id="offres" aria-labelledby="offres-title"><div class="container">'
        '<div class="split-head reveal"><div>%s<h2 id="offres-title">%s</h2></div><p class="lede">%s</p></div>'
        '<div class="grid-3">%s</div><p class="offers-note reveal">%s</p>'
        '<div class="more reveal"><div><h3>%s</h3><p>%s</p></div><a class="btn btn-ghost" href="#outils">%s</a></div>'
        '</div></section>'
        % (tag(c.offers["tag"]), esc(c.offers["title"]), esc(c.offers["intro"]), "".join(cards), esc(c.offers["note"]),
           esc(c.offers["more_title"]), esc(c.offers["more_text"]), esc(c.offers["more_cta"])))

    # Outils sur mesure : texte et exemples à gauche, maquette d'interface dessinée en code à droite
    t = c.tools
    ex = "".join('<li class="tool reveal"><h3>%s</h3><p>%s</p></li>' % (esc(a), esc(b)) for a, b in t["examples"])
    nav = "".join('<li%s>%s</li>' % (' class="on"' if n == t["mock_title"] else "", esc(n)) for n in t["mock_nav"])
    rows = "".join(
        '<tr><td class="mono">%s</td><td>%s</td><td class="mono num">%s</td><td><span class="chip %s">%s</span></td></tr>'
        % (esc(a), esc(b), esc(cc), st, esc(t["mock_status"][st])) for a, b, cc, st in t["mock_rows"])
    mock = (
        '<figure class="mock reveal" aria-label="%s">'
        '<div class="mock-win"><div class="mock-top"><span class="term-lights" aria-hidden="true"><i></i><i></i><i></i></span><span>outil.votre-entreprise.ch</span></div>'
        '<div class="mock-app"><ul class="mock-nav">%s</ul><div class="mock-main">'
        '<div class="mock-head"><h4>%s</h4><span class="mock-btn">+ %s</span></div>'
        '<div class="mock-kpi"><span>%s</span><b>%s</b><i class="mock-spark" aria-hidden="true"></i></div>'
        '<table class="mock-table"><tbody>%s</tbody></table></div></div></div>'
        '<figcaption>%s</figcaption></figure>'
        % (esc(t["mock_note"]), nav, esc(t["mock_title"]), esc(t["mock_new"]), esc(t["mock_total"]), esc(t["mock_total_value"]), rows, esc(t["mock_note"])))
    H.append(
        '<section class="section tools-sec" id="outils" aria-labelledby="outils-title"><div class="container">'
        '<div class="tools-grid"><div><div class="reveal">%s<h2 id="outils-title">%s</h2><p class="lede">%s</p></div>'
        '<ul class="tools-list">%s</ul>'
        '<p class="tools-proof reveal">%s</p>'
        '<div class="tools-cta reveal"><a class="btn btn-primary" href="#contact">%s</a><span>%s</span></div></div>'
        '%s</div></div></section>'
        % (tag(t["tag"]), esc(t["title"]), esc(t["intro"]), ex, esc(t["proof"]), esc(t["cta"]), esc(t["price"]), mock))

    # Méthode : paysage de nuit, étapes reliées, règles en liste (sans cartes)
    steps = "".join(
        '<li class="card step reveal"><span class="step-num" aria-hidden="true">%d</span><h3>%s</h3><p>%s</p></li>' % (i + 1, esc(t), esc(d))
        for i, (t, d) in enumerate(c.method["steps"]))
    rules = "".join(
        '<li class="rule reveal"><span class="rule-num" aria-hidden="true">0%d</span><h3>%s</h3><p>%s</p></li>' % (i + 1, esc(t), esc(d))
        for i, (t, d) in enumerate(c.method["principles"]))
    H.append(
        '<section class="section section-dark night" id="methode" aria-labelledby="methode-title">'
        '<canvas class="night-sky" aria-hidden="true"></canvas><div class="night-moon" aria-hidden="true"></div>%s'
        '<div class="container night-content"><div class="section-head reveal">%s<h2 id="methode-title">%s</h2></div>'
        '<ol class="grid-4 steps">%s</ol><p class="aside reveal">%s</p>'
        '<div class="rules"><h3 class="rules-title reveal">%s</h3><ol class="rules-list">%s</ol></div>'
        '</div></section>'
        % (alps_night(), tag(c.method["tag"]), esc(c.method["title"]), steps, esc(c.method["aside"]),
           esc(c.method["principles_title"]), rules))

    # Équipe : grande photo si elle existe, puis texte et liste, sans cartes
    photo = ""
    if os.path.exists(os.path.join(SITE, "assets", "img", "equipe-1400.webp")):
        photo = ('<figure class="team-photo reveal"><img src="/assets/img/equipe-800.webp" '
                 'srcset="/assets/img/equipe-800.webp 800w, /assets/img/equipe-1400.webp 1400w" sizes="(max-width: 1180px) 100vw, 1180px" '
                 'width="1400" height="788" loading="lazy" decoding="async" alt="%s"></figure>' % esc(c.team["photo_alt"]))
    members = "".join(
        '<li class="person reveal"><span class="avatar" aria-hidden="true">%s</span><p><strong>%s</strong> %s</p></li>'
        % (esc(ini), esc(name), esc(role)) for name, role, ini in c.team["members"])
    H.append(
        '<section class="section team" id="equipe" aria-labelledby="equipe-title"><div class="container">%s'
        '<div class="team-grid"><div class="reveal">%s<h2 id="equipe-title">%s</h2><p class="team-text">%s</p></div>'
        '<ul class="people">%s</ul></div></div></section>'
        % (photo, tag(c.team["tag"]), esc(c.team["title"]), esc(c.team["text"]), members))

    # Réalisation : étude de cas asymétrique
    k = c.work["case"]
    blocks = "".join('<div class="case-block reveal"><h3>%s</h3><p>%s</p></div>' % (esc(t), esc(d)) for t, d in k["blocks"])
    figure = ""
    if k.get("figure"):
        figure = '<p class="case-figure reveal"><b>%s</b> %s</p>' % (esc(k["figure"][0]), esc(k["figure"][1]))
    shot = ('<figure class="case-shot project reveal" tabindex="0"><img src="/assets/img/%s-800.webp" '
            'srcset="/assets/img/%s-800.webp 800w, /assets/img/%s-1400.webp 1400w" sizes="(max-width: 920px) 100vw, 700px" '
            'width="1400" height="875" loading="lazy" decoding="async" alt="%s"></figure>'
            % (k["image"], k["image"], k["image"], esc(k["image_alt"])))
    H.append(
        '<section class="section case" id="realisations" aria-labelledby="realisations-title"><div class="container">'
        '<div class="case-head reveal">%s<h2 id="realisations-title">%s</h2>'
        '<p class="case-meta">%s · <a href="%s" rel="noopener" target="_blank">%s %s</a></p></div>'
        '<div class="case-grid">%s<div class="case-text"><p class="case-intro reveal">%s</p>%s%s</div></div>'
        '<p class="case-next reveal">%s <span>%s</span> <a href="#contact">%s %s</a></p>'
        '</div></section>'
        % (tag(c.work["tag"]), esc(k["name"]), esc(k["meta"]), esc(k["url"]), esc(k["url_label"]), ICONS["arrow"],
           shot, esc(k["intro"]), blocks, figure, esc(c.work["next"]), esc(c.work["yours"]), esc(c.work["yours_cta"]), ICONS["arrow"]))

    # Preuve : terminal
    pr = c.proof
    def row(label, metric, unit=""):
        return ('<div class="term-row"><span class="term-key">%s</span><span class="term-dots" aria-hidden="true"></span>'
                '<span class="term-val"><b data-metric="%s">…</b>%s</span></div>' % (esc(label), metric, (" " + unit) if unit else ""))
    H.append(
        '<section class="section proof" id="preuve" aria-labelledby="preuve-title" data-median-desktop="%s" data-median-mobile="%s">'
        '<div class="container proof-grid2"><div class="reveal">%s<h2 id="preuve-title">%s</h2><p class="lede">%s</p>'
        '<p class="compare-source"><a href="%s" rel="noopener" target="_blank">%s</a></p></div>'
        '<div class="term reveal" role="group" aria-label="%s">'
        '<div class="term-bar"><span class="term-lights" aria-hidden="true"><i></i><i></i><i></i></span><span>%s</span></div>'
        '<div class="term-body"><p class="term-cmd"><span class="term-prompt">$</span> %s</p>%s%s%s%s'
        '<div class="term-compare">'
        '<div class="term-bar-row"><span class="term-key">%s</span><span class="bar"><span class="bar-fill bar-us" data-bar="us"></span></span><span class="term-val" data-metric="kb-label"></span></div>'
        '<div class="term-bar-row"><span class="term-key">%s</span><span class="bar"><span class="bar-fill bar-web" data-bar="web"></span></span><span class="term-val" data-metric="web-label"></span></div>'
        '</div><p class="term-out"><span class="term-prompt">&gt;</span> <b data-metric="ratio">…</b> %s<span class="term-caret" aria-hidden="true"></span></p>'
        '<p class="term-na"><span class="term-prompt">!</span> %s</p>'
        '</div></div></div></section>'
        % (pr["median_desktop_kb"], pr["median_mobile_kb"], tag(pr["tag"]), esc(pr["title"]), esc(pr["intro"]),
           esc(pr["source_url"]), esc(pr["source"]), esc(pr["term_title"]), esc(pr["term_title"]), esc(pr["command"]),
           row(pr["weight"], "kb", "Ko"), row(pr["time"], "time", "s"), row(pr["requests"], "req"), row(pr["cookies"], "cookies"),
           esc(pr["compare_us"]), esc(pr["compare_web"]), esc(pr["ratio"]), esc(pr["unavailable"])))

    # FAQ : deux colonnes
    faq_items = "".join(
        '<details class="faq-item reveal"><summary>%s</summary><div class="faq-body"><p>%s</p></div></details>' % (esc(q), esc(a))
        for q, a in c.faq["items"])
    H.append(
        '<section class="section" id="faq" aria-labelledby="faq-title"><div class="container faq-grid">'
        '<div class="faq-side reveal">%s<h2 id="faq-title">%s</h2><p class="muted">%s <a href="tel:%s">%s</a></p></div>'
        '<div class="faq-list">%s</div></div></section>'
        % (tag(c.faq["tag"]), esc(c.faq["title"]), esc(c.faq["aside"]), esc(c.brand["phone_tel"]), esc(c.brand["phone_display"]), faq_items))
    return "\n".join(H)


def build_index(c, langs, mods, templates):
    m = common_mapping(c, "home", langs, mods)
    home = page_path(c.LANG, "home")

    hero_facts = "".join("<li class=\"fact\"><strong>%s</strong><span>%s</span></li>" % (esc(a), esc(b)) for a, b in c.hero["facts"])

    contact_questions = "".join("<li>%s</li>" % esc(q) for q in c.contact["questions"])

    m.update({
        "middle_sections": middle_sections(c),
        "meta_title": esc(c.meta["title"]),
        "meta_description": esc(c.meta["description"]),
        "canonical": SITE_URL + home,
        "hreflang": hreflang_tags("home", langs),
        "og_title": esc(c.meta["og_title"]),
        "og_description": esc(c.meta["og_description"]),
        "og_image_alt": esc(c.brand["name"] + ", " + c.brand["signature"]),
        "jsonld": jsonld(c),
        "hero_eyebrow": esc(c.hero["eyebrow"]),
        "hero_title": hero_title_html(c),
        "hero_alps": alps_hero(),
        "night_alps": alps_night(),
        "hero_lede": esc(c.hero["lede"]),
        "hero_cta_primary": esc(c.hero["cta_primary"]),
        "hero_cta_secondary": esc(c.hero["cta_secondary"]),
        "hero_facts": hero_facts,
        "contact_tag": esc(c.contact["tag"]),
        "contact_title": esc(c.contact["title"]),
        "contact_questions": contact_questions,
        "contact_no_answers": esc(c.contact["no_answers"]),
        "contact_whatsapp": esc(c.contact["whatsapp"]),
        "contact_call": esc(c.contact["call"]),
        "contact_reply": esc(c.contact["reply_time"]),
        "whatsapp_url": esc(c.brand["whatsapp"]),
        "phone_tel": esc(c.brand["phone_tel"]),
        "phone_display": esc(c.brand["phone_display"]),
        "form_title": esc(c.contact["form"]["title"]),
        "form_email": esc(c.brand["form_email"]),
        "form_subject": esc(c.brand["form_subject"]),
        "form_next": SITE_URL + page_path(c.LANG, "thanks"),
        "form_autoresponse": esc(c.brand["form_autoresponse"]),
        "form_name": esc(c.contact["form"]["name"]),
        "form_company": esc(c.contact["form"]["company"]),
        "form_optional": esc(c.contact["form"]["optional"]),
        "form_email_label": esc(c.contact["form"]["email"]),
        "form_phone": esc(c.contact["form"]["phone"]),
        "form_message": esc(c.contact["form"]["message"]),
        "form_message_placeholder": esc(c.contact["form"]["message_placeholder"]),
        "form_privacy": esc(c.contact["form"]["privacy"]),
        "form_privacy_link": esc(c.contact["form"]["privacy_link"]),
        "privacy_url": page_path(c.LANG, "privacy"),
        "form_submit": esc(c.contact["form"]["submit"]),
    })
    out = render(templates["index"], m)
    write(page_path(c.LANG, "home").lstrip("/") + "index.html", out)


def build_simple(c, kind, langs, mods, templates, body, meta_title, page_class="", noindex=False, description=None):
    m = common_mapping(c, kind if kind in DEFAULT_SLUGS["fr"] else "home", langs, mods)
    path = page_path(c.LANG, kind) if kind in DEFAULT_SLUGS["fr"] else page_path(c.LANG, "home")
    m.update({
        "meta_title": esc(meta_title + " · NexusLab"),
        "meta_description": esc(description or c.meta["description"]),
        "canonical": SITE_URL + path,
        "hreflang": hreflang_tags(kind, langs) if kind in DEFAULT_SLUGS["fr"] else "",
        "robots_meta": '<meta name="robots" content="noindex">' if noindex else "",
        "page_class": page_class,
        "page_body": body,
    })
    return render(templates["page"], m)


def legal_body(section, c):
    parts = ['<h1>%s</h1>' % esc(section["title"]), '<p class="updated">%s</p>' % esc(section["updated"])]
    if "intro" in section:
        parts.append('<div class="intro">%s</div>' % section["intro"])
    for title, body_html in section["sections"]:
        parts.append("<h2>%s</h2>%s" % (esc(title), body_html))
    parts.append('<a class="btn btn-primary" href="%s">%s</a>' % (page_path(c.LANG, "home"), esc(section["back"])))
    return "".join(parts)


def build_lang(lang, langs, mods, templates):
    c = mods[lang]
    print("Langue :", lang)
    build_index(c, langs, mods, templates)

    write(page_path(lang, "legal").lstrip("/") + "index.html",
          build_simple(c, "legal", langs, mods, templates, legal_body(c.legal, c), c.legal["meta_title"]))
    write(page_path(lang, "privacy").lstrip("/") + "index.html",
          build_simple(c, "privacy", langs, mods, templates, legal_body(c.privacy, c), c.privacy["meta_title"]))

    thanks = (
        '<h1>%s</h1><p class="lede">%s</p>'
        '<p><a class="btn btn-primary" href="%s">%s</a> <a class="btn btn-ghost" href="%s" rel="noopener" target="_blank">%s</a></p>'
        % (esc(c.thanks["title"]), esc(c.thanks["text"]), page_path(lang, "home"), esc(c.thanks["back"]),
           esc(c.brand["whatsapp"]), esc(c.contact["whatsapp"]))
    )
    write(page_path(lang, "thanks").lstrip("/") + "index.html",
          build_simple(c, "thanks", langs, mods, templates, thanks, c.thanks["meta_title"], "page-center", noindex=True))

    if lang == "fr":
        nf = (
            '<h1>%s</h1><p class="lede">%s</p><p><a class="btn btn-primary" href="/">%s</a></p>'
            % (esc(c.notfound["title"]), esc(c.notfound["text"]), esc(c.notfound["back"]))
        )
        write("404.html", build_simple(c, "notfound", langs, mods, templates, nf, c.notfound["meta_title"], "page-center", noindex=True))


def build_sitemap(langs):
    today = date.today().isoformat()
    urls = []
    for kind in ("home", "legal", "privacy"):
        for lang in langs:
            alts = "".join(
                '<xhtml:link rel="alternate" hreflang="%s" href="%s%s"/>' % (l2, SITE_URL, page_path(l2, kind)) for l2 in langs
            ) + '<xhtml:link rel="alternate" hreflang="x-default" href="%s%s"/>' % (SITE_URL, page_path("fr", kind))
            prio = "1.0" if kind == "home" else "0.3"
            urls.append("<url><loc>%s%s</loc><lastmod>%s</lastmod><priority>%s</priority>%s</url>" % (SITE_URL, page_path(lang, kind), today, prio, alts))
    xml = ('<?xml version="1.0" encoding="UTF-8"?>\n'
           '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">\n'
           + "\n".join(urls) + "\n</urlset>\n")
    write("sitemap.xml", xml)
    write("robots.txt", "User-agent: *\nAllow: /\nDisallow: /merci/\nDisallow: /de/danke/\nDisallow: /en/thank-you/\n\nSitemap: %s/sitemap.xml\n" % SITE_URL)
    write("site.webmanifest", json.dumps({
        "name": "NexusLab", "short_name": "NexusLab",
        "icons": [{"src": "/favicon-512x512.png", "sizes": "512x512", "type": "image/png"}],
        "theme_color": "#F6F2EC", "background_color": "#F6F2EC", "display": "browser",
    }, indent=2) + "\n")
    write("_headers",
          "/*\n  X-Content-Type-Options: nosniff\n  X-Frame-Options: DENY\n  Referrer-Policy: strict-origin-when-cross-origin\n"
          "  Permissions-Policy: camera=(), microphone=(), geolocation=()\n\n"
          "/assets/*\n  Cache-Control: public, max-age=2592000\n")


def main():
    templates = {
        "index": read(os.path.join(HERE, "templates", "index.html")),
        "page": read(os.path.join(HERE, "templates", "page.html")),
    }
    mods = {lang: load(lang) for lang in LANGS}
    for lang in LANGS:
        build_lang(lang, LANGS, mods, templates)
    build_sitemap(LANGS)
    print("Terminé. Version", VERSION)


if __name__ == "__main__":
    main()
