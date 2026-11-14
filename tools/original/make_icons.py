"""Launcher icons, splash icon and launch logo for the 원어 대조 성경 Android app.

Emblem: Hebrew aleph (rubric red) and Greek omega (gold) on parchment.
usage: python3 make_icons.py RES_DIR [FONT.ttf]
"""
import os, sys
from PIL import Image, ImageDraw, ImageFont

RES = sys.argv[1]
FONT = sys.argv[2] if len(sys.argv) > 2 else '/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf'
PARCH, RUBRIC, GOLD, INK = (251, 247, 238, 255), (163, 32, 47, 255), (138, 106, 30, 255), (29, 34, 41, 255)
DENS = {'mdpi': 1, 'hdpi': 1.5, 'xhdpi': 2, 'xxhdpi': 3, 'xxxhdpi': 4}

def emblem(size, mono=False, scale=1.0):
    """Transparent square with the two letters centred; scale = share of the side the pair may take."""
    S = size * 4
    im = Image.new('RGBA', (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    fa = ImageFont.truetype(FONT, int(S * 0.56 * scale))
    fo = ImageFont.truetype(FONT, int(S * 0.40 * scale))
    a, o = 'א', 'Ω'
    ba, bo = d.textbbox((0, 0), a, font=fa), d.textbbox((0, 0), o, font=fo)
    wa, ha = ba[2] - ba[0], ba[3] - ba[1]
    wo, ho = bo[2] - bo[0], bo[3] - bo[1]
    gap = int(S * 0.03 * scale)
    tw = wa + gap + wo
    x0 = (S - tw) // 2
    base = (S + ha) // 2
    d.text((x0 - ba[0] + wo + gap, base - ba[3]), a, font=fa, fill=(255, 255, 255, 255) if mono else RUBRIC)   # Hebrew reads right to left: aleph on the right
    d.text((x0 - bo[0], base - bo[3]), o, font=fo, fill=(255, 255, 255, 255) if mono else GOLD)
    # thin rule under the letters
    y = base + int(S * 0.06 * scale)
    d.rounded_rectangle((x0, y, x0 + tw, y + max(2, int(S * 0.018 * scale))), radius=4, fill=(255, 255, 255, 255) if mono else INK)
    return im.resize((size, size), Image.LANCZOS)

def save(im, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    im.save(path)

for name, k in DENS.items():
    n = round(48 * k)
    full = Image.new('RGBA', (n * 4, n * 4), (0, 0, 0, 0))
    ImageDraw.Draw(full).rounded_rectangle((0, 0, n * 4 - 1, n * 4 - 1), radius=int(n * 4 * 0.2), fill=PARCH)
    full = full.resize((n, n), Image.LANCZOS)
    full.alpha_composite(emblem(n, scale=0.95))
    save(full, f'{RES}/mipmap-{name}/ic_launcher.png')
    rnd = Image.new('RGBA', (n * 4, n * 4), (0, 0, 0, 0))
    ImageDraw.Draw(rnd).ellipse((0, 0, n * 4 - 1, n * 4 - 1), fill=PARCH)
    rnd = rnd.resize((n, n), Image.LANCZOS)
    rnd.alpha_composite(emblem(n, scale=0.85))
    save(rnd, f'{RES}/mipmap-{name}/ic_launcher_round.png')
    f = round(108 * k)   # adaptive layer: keep the emblem in the central 66dp
    save(emblem(f, scale=0.6), f'{RES}/mipmap-{name}/ic_launcher_foreground.png')
    save(emblem(f, mono=True, scale=0.6), f'{RES}/mipmap-{name}/ic_launcher_monochrome.png')
    s = round(288 * k)   # Android 12+ splash: icon inside a 2/3 circle
    save(emblem(s, scale=0.55), f'{RES}/drawable-{name}/splash_icon.png')
    w = round(120 * k)
    save(emblem(w, scale=1.0), f'{RES}/drawable-{name}/launch_logo.png')
print('icons written to', RES)
