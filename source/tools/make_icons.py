#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Génère les icônes (favicon, apple-touch-icon) et l'image de partage (og-image.png)."""
import os
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.normpath(os.path.join(HERE, "..", "..", "site"))
FONT = os.path.join(HERE, "manrope-var.ttf")

NAVY = (20, 33, 61)
CREAM = (246, 242, 236)
CORAL = (255, 107, 87)
NAVY2 = (201, 209, 224)


def mark(size, bg, dot, link, scale=4):
    """Le logo : deux points reliés, celui de droite en corail."""
    s = size * scale
    im = Image.new("RGBA", (s, s), bg + (255,))
    d = ImageDraw.Draw(im)
    r = s * 0.21
    cy = s / 2
    ax, bx = s * 0.26, s * 0.74
    d.rectangle([ax, cy - r * 0.29, bx, cy + r * 0.29], fill=link + (255,))
    d.ellipse([ax - r, cy - r, ax + r, cy + r], fill=dot + (255,))
    d.ellipse([bx - r, cy - r, bx + r, cy + r], fill=CORAL + (255,))
    return im.resize((size, size), Image.LANCZOS)


def swiss_cross(d, cx, cy, span, fill=(255, 255, 255, 255)):
    """Croix suisse : bras un sixième plus longs que larges (largeur = 3/10 de l'envergure)."""
    w = span * 0.3
    d.rectangle([cx - w / 2, cy - span / 2, cx + w / 2, cy + span / 2], fill=fill)
    d.rectangle([cx - span / 2, cy - w / 2, cx + span / 2, cy + w / 2], fill=fill)


def rounded(im, radius_ratio=0.22):
    s = im.size[0]
    mask = Image.new("L", (s * 4, s * 4), 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, s * 4 - 1, s * 4 - 1], radius=int(s * 4 * radius_ratio), fill=255)
    mask = mask.resize((s, s), Image.LANCZOS)
    out = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    out.paste(im, (0, 0), mask)
    return out


def font(size, weight=800):
    f = ImageFont.truetype(FONT, size)
    try:
        f.set_variation_by_axes([weight])
    except Exception as e:  # noqa: BLE001
        print("Variation de police indisponible :", e)
    return f


def og_image():
    W, H = 1200, 630
    im = Image.new("RGB", (W, H), NAVY)
    d = ImageDraw.Draw(im)
    # Logo : points reliés + mot-logo
    x, y = 96, 110
    r = 20
    d.rectangle([x, y - 6, x + 48, y + 6], fill=CREAM)
    d.ellipse([x - r, y - r, x + r, y + r], fill=CREAM)
    d.ellipse([x + 48 - r, y - r, x + 48 + r, y + r], fill=CORAL)
    d.text((x + 92, y - 26), "nexus", font=font(48, 800), fill=CREAM)
    # Titre
    f_title = font(84, 800)
    lines = ["Le lien entre votre", "métier et le digital."]
    yy = 220
    for line in lines:
        d.text((96, yy), line, font=f_title, fill=CREAM)
        yy += 96
    d.text((96, 450), "Sites web et outils digitaux pour les PME de Suisse romande", font=font(30, 500), fill=NAVY2)
    d.text((96, 540), "nexus-lab.ch", font=font(28, 700), fill=CORAL)
    # Motif de points à droite
    pts = [(1000, 110), (1120, 190), (1050, 310), (1140, 430), (985, 520)]
    for a, b in [(0, 1), (1, 2), (2, 3), (2, 4), (0, 2)]:
        d.line([pts[a], pts[b]], fill=(60, 76, 110), width=3)
    for i, (px, py) in enumerate(pts):
        rr = 22 if i == 2 else 11
        d.ellipse([px - rr, py - rr, px + rr, py + rr], fill=CORAL if i == 2 else NAVY2)
    path = os.path.join(SITE, "assets", "img", "og-image.png")
    im.save(path, optimize=True)
    print("écrit", path, os.path.getsize(path), "octets")


def main():
    os.makedirs(os.path.join(SITE, "assets", "img"), exist_ok=True)
    big = mark(512, CREAM, NAVY, NAVY)
    big.save(os.path.join(SITE, "favicon-512x512.png"), optimize=True)
    mark(180, CREAM, NAVY, NAVY).save(os.path.join(SITE, "apple-touch-icon.png"), optimize=True)
    small = mark(32, CREAM, NAVY, NAVY)
    small.save(os.path.join(SITE, "favicon-32x32.png"), optimize=True)
    ico = mark(64, CREAM, NAVY, NAVY)
    ico.save(os.path.join(SITE, "favicon.ico"), format="ICO", sizes=[(16, 16), (32, 32), (48, 48)])
    og_image()
    for name in ("favicon-512x512.png", "apple-touch-icon.png", "favicon-32x32.png", "favicon.ico"):
        print("écrit", name, os.path.getsize(os.path.join(SITE, name)), "octets")


if __name__ == "__main__":
    main()
