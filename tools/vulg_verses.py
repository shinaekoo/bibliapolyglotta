"""The Vulgate's verse numbers -> the KJV's, for text/la{book}.json

The Clementine Vulgate counts verses the way the Greek Bible does, and in places that is a long way from the
KJV grid every other translation here sits on:
  Psalms   the Greek numbering. Vulgate 9 is Hebrew 9+10, so Vulgate 10-112 are Hebrew 11-113, and a psalm's
           title is a verse of its own instead of the opening of verse 1.
  Daniel   chapter 3 carries the Prayer of Azariah and the Song of the Three (100 verses), and Hebrew 4:1-3
           is Vulgate 3:98-100, so the whole of Hebrew 4 sits three verses back.
  Esther   chapter 10 runs to verse 13 and the additions follow as chapters 11-16.
  26 more  one chapter apiece where a verse is split or joined differently, which moves that chapter's tail.
Left alone, the app shows the wrong Latin verse for about 2,400 verses, the psalms worst of all.

The map is composed from the two versification files BibleNLP/ebible ships, so nothing here is guessed:
  metadata/vul.vrs   Vulgate <-> BHS ("org")
  metadata/eng.vrs   KJV <-> BHS
Chaining them gives Vulgate -> KJV. Verse 0 of a chapter is its title, which the KJV prints above verse 1 and
these files keep as the first verse, so verses 0 and 1 land together.

Verses the KJV grid has no room for (Daniel 13-14, Esther 11-16) stay where they are, as chapters after the
last KJV one, so the Latin column can still be read on its own.
usage: python3 tools/vulg_verses.py EBIBLE_DIR [--dry]
"""
import json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
TX = os.path.join(HERE, '..', 'text') + '/'
EB = sys.argv[1]
DRY = '--dry' in sys.argv
BK = 'GEN EXO LEV NUM DEU JOS JDG RUT 1SA 2SA 1KI 2KI 1CH 2CH EZR NEH EST JOB PSA PRO ECC SNG ISA JER LAM EZK DAN HOS JOL AMO OBA JON MIC NAM HAB ZEP HAG ZEC MAL MAT MRK LUK JHN ACT ROM 1CO 2CO GAL EPH PHP COL 1TH 2TH 1TI 2TI TIT PHM HEB JAS 1PE 2PE 1JN 2JN 3JN JUD REV'.split()
# the Vulgate's book number for each KJV book (the app's own table), so la{n}.json keeps its name
VULG_BOOK = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 18, 19, 20, 21, 22, 23, 26, 27, 28, 30, 31,
             32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57,
             58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72]
OF_VULG = {v: i for i, v in enumerate(VULG_BOOK)}

def vrs_map(path):
    """the file's own numbering <-> org, as {org (book, c, v): this file's (book, c, v)}"""
    m = {}
    def span(s):
        bk, rest = s.split(); c, vv = rest.split(':'); a, _, z = vv.partition('-')
        return bk, int(c), int(a), int(z or a)
    for line in open(path, encoding='utf-8'):
        if '=' not in line or line.startswith('#') or line.split()[0] not in BK: continue
        l, r = (x.strip() for x in line.split('='))
        lb, lc, la, lz = span(l); rb, rc, ra, rz = span(r)
        for k in range(lz - la + 1): m[(rb, rc, ra + k)] = (lb, lc, la + k)
    return m

V = vrs_map(os.path.join(EB, 'metadata', 'vul.vrs'))      # org -> Vulgate
E = vrs_map(os.path.join(EB, 'metadata', 'eng.vrs'))      # org -> KJV
MAP = {}                                                  # Vulgate -> KJV
for org in set(V) | set(E):
    MAP[V.get(org, org)] = E.get(org, org)
# Where a psalm is the second half of a Hebrew one, vul.vrs keeps the Hebrew verse numbers running (Vulgate
# 115 is numbered 10-19, Vulgate 147 is 12-20) while the text here starts each psalm at 1. The lowest number
# vul.vrs uses for a chapter says how far to shift ours before looking it up.
SPAN = {}
for b, c, v in MAP:
    k = (b, c)
    lo, hi = SPAN.get(k, (v, v))
    SPAN[k] = (min(lo, v), max(hi, v))
# only where the chapter holds exactly that run and nothing before it: Vulgate Daniel 3 is numbered from 1
# even though its mapped verses start at 24, because 1-23 are Daniel's own and 24-90 are the inserted Song
SHIFT = {}
for k, (lo, hi) in SPAN.items():
    if lo < 2: continue
    b, c = k
    bi = BK.index(b)
    f = f'{TX}la{VULG_BOOK[bi]:02d}.json'
    if not os.path.exists(f): continue
    src = json.load(open(f, encoding='utf-8'))
    if c <= len(src) and len(src[c - 1]) == hi - lo + 1: SHIFT[k] = lo - 1
print('옮길 절', len(MAP), '개 · 번호가 이어지는 장', len(SHIFT), file=sys.stderr)

CHANGED = {}
for b, vb in enumerate(VULG_BOOK):
    f = f'{TX}la{vb:02d}.json'
    if not os.path.exists(f): continue
    src = json.load(open(f, encoding='utf-8'))
    out, extra, moved = {}, {}, 0
    for ci, ch in enumerate(src):
        for vi, t in enumerate(ch or []):
            if not t: continue
            vv = vi + 1 + SHIFT.get((BK[b], ci + 1), 0)
            kb, kc, kv = MAP.get((BK[b], ci + 1, vv), (BK[b], ci + 1, vi + 1))
            if kb != BK[b]:
                # the map sends it to a book the KJV has none of (Daniel 3:24-90 is the Song of the Three,
                # 13-14 are Susanna and Bel): it has no verse of its own here, so it stays where it was,
                # after the last KJV chapter, instead of landing on a KJV verse and burying it
                extra.setdefault(ci + 1, {})[vi] = t
                moved += 1
                continue
            if (kc, kv) != (ci + 1, vi + 1): moved += 1
            slot = max(0, kv - 1)                  # verse 0 is the title: it opens verse 1
            cur = out.setdefault(kc, {}).get(slot)
            out[kc][slot] = (cur + ' ' + t) if cur else t
    # 장 안의 빈 칸은 그대로 두고, 불가타에만 있는 장은 뒤에 붙인다
    res = []
    for kc in range(1, max(list(out) + list(extra) + [0]) + 1):
        d = dict(extra.get(kc) or {}) if kc not in out else dict(out[kc])
        res.append([d.get(i, '') for i in range(max(d) + 1)] if d else [])
    while res and not any(res[-1]): res.pop()
    if moved: CHANGED[BK[b]] = moved
    if not DRY: json.dump(res, open(f, 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
print('옮긴 절이 있는 책', len(CHANGED), file=sys.stderr)
for k, n in sorted(CHANGED.items(), key=lambda kv: -kv[1]): print(f'  {k} {n}', file=sys.stderr)
