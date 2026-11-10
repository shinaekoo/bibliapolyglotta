"""Latin and German verse numbers -> the KJV's, in text/la{book}.json and text/de{book}.json

Every other translation here sits on the KJV grid. Two did not:

  Latin   the Clementine Vulgate counts verses the way the Greek Bible does. Vulgate 9 is Hebrew 9+10, so
          Vulgate 10-112 are Hebrew 11-113; a psalm's title is a verse of its own; Daniel 3 carries the
          Prayer of Azariah and the Song of the Three (100 verses) with Hebrew 4:1-3 at Vulgate 3:98-100;
          Esther 10 runs to verse 13 with the additions as chapters 11-16; and a hundred further chapters
          split or join one verse differently, which moves that chapter's tail.
  German  Luther 1912 follows the Hebrew: a psalm's title is verse 1 (verses 1-2 in four psalms), so 63
          psalms sit a verse low, and 20 more books differ in a chapter apiece.

Both used to be patched at render time instead -- psMap and autoShift in web/index.html, and a copy of the
same psalm table with a "trim the leading verses until the counts match" rule in six of the tools here --
so the one table was written out seven times, the trim was a guess, and what it did not cover (Daniel 4,
Esther 10, the single-verse tails) stayed wrong. This moves the text itself, once, and those are gone.

The chapter and verse correspondences come from the versification files BibleNLP/ebible ships, so none of
it is hand-written:
  metadata/vul.vrs   Vulgate <-> BHS ("org")      Latin:  Vulgate -> org -> KJV
  metadata/eng.vrs   KJV <-> BHS                  German: org -> KJV
Verse 0 of a chapter is its title, which the KJV prints above verse 1, so verses 0 and 1 land together.

vul.vrs describes a Vulgate, though, and not exactly ours: our text agrees with it in the psalms, Daniel
and Mark 9, and with the KJV in Genesis 49 and Acts 7. No file we have says which chapter is which, so
each chapter is settled by the text -- see chapter_moves below.

A verse the KJV has no room for (the Song of the Three, Susanna, Bel, the additions to Esther) is kept as
a chapter after the last KJV one, so the Latin column can still be read on its own.
usage: python3 tools/verse_map.py EBIBLE_DIR [--dry]
"""
import json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
TX = os.path.join(HERE, '..', 'text') + '/'
EB = sys.argv[1]
DRY = '--dry' in sys.argv
BK = 'GEN EXO LEV NUM DEU JOS JDG RUT 1SA 2SA 1KI 2KI 1CH 2CH EZR NEH EST JOB PSA PRO ECC SNG ISA JER LAM EZK DAN HOS JOL AMO OBA JON MIC NAM HAB ZEP HAG ZEC MAL MAT MRK LUK JHN ACT ROM 1CO 2CO GAL EPH PHP COL 1TH 2TH 1TI 2TI TIT PHM HEB JAS 1PE 2PE 1JN 2JN 3JN JUD REV'.split()
# the Vulgate's book number for each KJV book, so la{n}.json keeps the name the app looks for
VULG_BOOK = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 18, 19, 20, 21, 22, 23, 26, 27, 28, 30, 31,
             32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57,
             58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72]

# Running this twice would move an already-moved text a second time and scramble it, so a run leaves a
# stamp beside the text and a later one stops unless --force says the text has been restored.
STAMP = os.path.join(TX, '.verse_map')
if os.path.exists(STAMP) and not DRY and '--force' not in sys.argv:
    sys.exit(f'본문은 이미 KJV 번호로 옮겨져 있습니다 ({open(STAMP).read().strip()}).\n'
             'tools/build_texts.py로 본문을 다시 만든 뒤에 실행하거나, --force를 주십시오.')

def own2org(path):
    """a .vrs file's mapping lines -> {that file's own (book, c, v): the Hebrew's (book, c, v)}

    A line reads "own = org", as `MAL 4:1-6 = MAL 3:19-24` in eng.vrs does, and reading it in this
    direction is what makes it a function: a versification may put two of the Hebrew's verses in one of
    its own, but never one of the Hebrew's in two places. Keyed the other way round it is not -- vul.vrs
    splits the Hebrew's Psalm 2:12 into the Vulgate's 2:12 and 2:13 -- and one branch would be lost."""
    m = {}
    def span(s):
        bk, rest = s.split(); c, vv = rest.split(':'); a, _, z = vv.partition('-')
        return bk, int(c), int(a), int(z or a)
    for line in open(path, encoding='utf-8'):
        if '=' not in line or line.startswith('#') or line.split()[0] not in BK: continue
        l, r = (x.strip() for x in line.split('='))
        lb, lc, la, lz = span(l); rb, rc, ra, rz = span(r)
        for k in range(lz - la + 1):
            key, val = (lb, lc, la + k), (rb, rc, ra + k)
            # A version can cover two of the Hebrew's verses with one of its own -- the Vulgate's Mark
            # 4:40 is the Hebrew's 4:40 and 4:41 -- and the first of the two is where it belongs, so the
            # lower reference wins rather than whichever line the file happens to list second.
            if val < m.get(key, val): m[key] = val
            else: m.setdefault(key, val)
    return m

LO = own2org(os.path.join(EB, 'metadata', 'vul.vrs'))     # Vulgate -> org
EO = own2org(os.path.join(EB, 'metadata', 'eng.vrs'))     # KJV -> org
NV = {bk: [len(ch) for ch in json.load(open(f'{TX}en{b:02d}.json', encoding='utf-8'))]
      for b, bk in enumerate(BK)}                         # the KJV's own verse count per chapter

# org -> KJV, the other way about. Where the KJV splits one of the Hebrew's verses in two, the first of
# the two is the target and remap joins whatever else lands there onto it.
OK = {}
for k, o in sorted(EO.items()): OK.setdefault(o, k)

def exists(ref):
    """whether the KJV has such a verse. A book it carries none of -- Susanna, Bel, the Song of the Three,
    the additions to Esther -- counts as existing: remap shows those after the chapter's KJV verses."""
    bk, c, v = ref
    return bk not in NV or (0 < c <= len(NV[bk]) and v <= NV[bk][c-1])

def to_kjv(org):
    """a verse numbered as the Hebrew is -> the KJV verse that carries it, or None if it has none

    None happens where the two files disagree: vul.vrs records the Vulgate's Numbers 26:1 as the Hebrew's
    25:19, eng.vrs says nothing about it, and so the Hebrew's 25:19 would fall through to a KJV 25:19 that
    does not exist. remap then leaves that verse wherever the source put it."""
    k = OK.get(org, org)
    return k if exists(k) else None

def path_of(lang, b): return f'{TX}{lang}{(VULG_BOOK[b] if lang == "la" else b):02d}.json'

def latin_map():
    """Vulgate ref -> KJV ref, for every verse our Latin text actually has

    Where vul.vrs says nothing about a reference, it is read as a Hebrew one, which is what the Vulgate's
    numbering is outside the psalms and Daniel 3: vul.vrs has no Daniel 4 line at all, and leaving those
    verses alone would strand the whole chapter three verses out. That reading is a guess in the narrative
    books, though, and chapter_moves below is what keeps a wrong guess from being used."""
    m = {}
    for b in range(66):
        f = path_of('la', b)
        if not os.path.exists(f): continue
        for ci, ch in enumerate(json.load(open(f, encoding='utf-8')), 1):
            for vi in range(len(ch or []) + 1):
                ref = (BK[b], ci, vi + 1)
                if (k := to_kjv(LO.get(ref, ref))): m[ref] = k
    for la, o in LO.items():
        if (k := to_kjv(o)): m[la] = k
    return m

LA_MAP = latin_map()
DE_MAP = {o: k for o in set(EO.values()) if (k := to_kjv(o))}   # Luther follows the Hebrew throughout

def continuations(lang, spans):
    """Where a psalm is the second half of a Hebrew one, vul.vrs keeps the Hebrew numbers running (Vulgate
    115 is numbered 10-19, Vulgate 147 is 12-20) while our text starts every psalm at 1. Spot it by the
    chapter holding exactly that run: Vulgate Daniel 3 is numbered from 1 even though its mapped verses
    start at 24, because 1-23 are Daniel's own and 24-90 are the inserted Song."""
    span = {}
    for b, c, v in spans:
        lo, hi = span.get((b, c), (v, v))
        span[(b, c)] = (min(lo, v), max(hi, v))
    out = {}
    for (bk, c), (lo, hi) in span.items():
        if lo < 2 or bk not in BK: continue
        f = path_of(lang, BK.index(bk))
        if not os.path.exists(f): continue
        src = json.load(open(f, encoding='utf-8'))
        if c <= len(src) and len(src[c - 1]) == hi - lo + 1: out[(bk, c)] = lo - 1
    return out

# ---------- which chapters the map may touch ----------
# Neither file describes our texts exactly. vul.vrs is right about our Clementine in the psalms, Daniel
# and Mark 9 and wrong about it in Genesis 49 and Acts 7, where it already counts as the KJV does; and
# eng.vrs is right about Luther except in 1 Chronicles 12, which also counts as the KJV does. Moving a
# chapter that was already right scrambles its tail, so each chapter is put to the text: every verse's
# names and numbers are matched against the English verse it would land on and against the English verse
# it already sits at, and the chapter moves only where that is the better fit.
FOLD = str.maketrans('áàâãäåéèêëíìîïóòôõöúùûüýÿñçæœ', 'aaaaaaeeeeiiiiooooouuuuyyncao')
# The names the Bible says most often are the ones a four-letter stem cannot match: Dominus and HERR
# against Lord, Deus and Gott against God -- and "God" is three letters, so it was not even looked at.
# Without these, a chapter like Joshua 4, which names no person or place for verses on end, has nothing
# to measure at all.
SAME = {w: c for c, ws in {
    'lord': 'dominus domini domino dominum herr herrn hern lord',
    'god': 'deus dei deo deum gott gottes god',
    'jesus': 'jesus jesu jesum jesui jesus',
    'christ': 'christus christi christo christum christ christi',
    'spirit': 'spiritus spiritu spiritui spiritum geist geistes spirit',
}.items() for w in ws.split()}

def keys(t):
    """the names and numbers of a verse, as stems a Latin and an English spelling can share"""
    out = set()
    for w in re.findall(r'[0-9]+|[^\W\d_]+', t or ''):
        if w[0].isdigit(): out.add(w)
        elif w[0].isupper():
            f = w.lower().translate(FOLD)
            if f in SAME: out.add(SAME[f])
            elif len(w) > 3: out.add(f[:4])
    return out

def chapter_moves(b, src, MAP, shift, lang):
    """{source chapter: whether to follow the map rather than leave the chapter where it is}"""
    # Luther's text is mixed the same way the Clementine is -- our 1 Chronicles 12 counts as the KJV does,
    # not as the Hebrew -- so it is measured too. Its spellings share less with the KJV's (Sebulon against
    # Zebulun matches nothing), but the names that do carry (David, Juda, Israel, Mose) and every numeral
    # are enough, and a chapter with no signal falls to the tie-break below.
    #
    # The psalms are exempt in both, and Daniel and Esther in Latin. There the .vrs files describe exactly
    # what our texts do -- a psalm's title is what eng.vrs's verse 0 is for -- those chapters are checked
    # against the English by hand, and a wrong guess costs most: a rejected psalm is a whole psalm shown
    # against the wrong one. It is also where both measures go blind. A psalm verse rarely carries a name
    # ("HERR, höre meine Worte" against "Hearken unto the voice of my cry" shares nothing), and a psalm
    # whose title is a verse of its own is a clean one-verse shift, which leaves no KJV verse blank either
    # way, so the tie-break below cannot see it. Luther's psalms 5, 6, 8 and 13 all sat a verse out.
    if BK[b] == 'PSA' or (lang == 'la' and BK[b] in ('DAN', 'EST')): return {}
    en = json.load(open(f'{TX}en{b:02d}.json', encoding='utf-8'))
    def enk(ref):
        bk, c, v = ref
        v = max(1, v)                   # verse 0 is a chapter's title, which remap joins onto verse 1
        return keys(en[c-1][v-1]) if bk == BK[b] and 0 < c <= len(en) and v <= len(en[c-1]) else set()
    out = {}
    for ci, ch in enumerate(src, 1):
        stay = move = 0
        for vi, t in enumerate(ch or [], 1):
            k = keys(t)
            if not k: continue
            here = (BK[b], ci, vi)
            # resolved the way remap does it: a verse the map says nothing about does not move, so it
            # must score the same both ways, or a sparse map (eng.vrs names only the chapters that
            # differ) would read as an argument for leaving every chapter alone
            tgt = MAP.get((BK[b], ci, vi + shift.get((BK[b], ci), 0))) or here
            stay += len(k & enk(here))
            # a verse the Vulgate alone has belongs in no KJV verse, so moving it is always the better fit
            move += len(k) if tgt[0] != BK[b] else len(k & enk(tgt))
        out[ci] = (stay, move)
    # Names settle a chapter only where there are names. Job 39 is thirty-five verses of wild goats and
    # ostriches without one, and Mark 8 scores level because thirty-eight of its thirty-nine verses map to
    # themselves either way -- yet both spill into the next chapter, and moving one without the other
    # leaves the seam empty. So a tie is settled by the thing that actually matters: which reading leaves
    # fewer of the KJV's verses in this book with no Latin or German beside them at all.
    def blanks(move_all):
        filled = set()
        for ci, ch in enumerate(src, 1):
            for vi, t in enumerate(ch or [], 1):
                if not t: continue
                here = (BK[b], ci, vi)
                r = (MAP.get((BK[b], ci, vi + shift.get((BK[b], ci), 0))) or here) if move_all else here
                if r[0] == BK[b]: filled.add((r[1], max(1, r[2])))
        return sum(1 for c in range(1, len(en) + 1) for v in range(1, len(en[c-1]) + 1)
                   if en[c-1][v-1] and (c, v) not in filled)
    tie = blanks(True) < blanks(False)
    return {c: (m > s if m != s else tie) for c, (s, m) in out.items()}

def remap(lang, MAP, spans):
    SHIFT = continuations(lang, spans)
    changed, kept = {}, []
    for b in range(66):
        f = path_of(lang, b)
        if not os.path.exists(f): continue
        src = json.load(open(f, encoding='utf-8'))
        nch = len(json.load(open(f'{TX}en{b:02d}.json', encoding='utf-8')))
        MOVE = chapter_moves(b, src, MAP, SHIFT, lang)

        def unknown_to_kjv(ci, ch):
            """whether a chapter past the KJV's last is one the KJV has nothing of, rather than one of its
            own under another number

            Daniel 13 and 14 are Susanna and Bel, Esther 11-16 the additions: part of such a chapter maps
            away to a book of its own and part falls through, and mixing the two scatters it, so it is
            copied as it stands. Luther's Joel 4 is the KJV's Joel 3, though, and copying that one leaves
            Joel 3 blank -- so what settles it is whether any verse lands in a chapter the KJV has."""
            for vi, t in enumerate(ch or [], 1):
                if not t: continue
                r = MAP.get((BK[b], ci, vi + SHIFT.get((BK[b], ci), 0)))
                if r and r[0] == BK[b] and r[1] <= nch: return False
            return True

        out, extra, moved = {}, {}, 0
        for ci, ch in enumerate(src):
            if ci >= nch and unknown_to_kjv(ci + 1, ch):
                extra[ci + 1] = {vi: t for vi, t in enumerate(ch or []) if t}
                continue
            for vi, t in enumerate(ch or []):
                if not t: continue
                vv = vi + 1 + SHIFT.get((BK[b], ci + 1), 0)
                here = (BK[b], ci + 1, vi + 1)
                kb, kc, kv = (MAP.get((BK[b], ci + 1, vv)) or here) if MOVE.get(ci + 1, True) else here
                if kb != BK[b]:                    # no KJV verse of its own: keep it past the last chapter
                    extra.setdefault(ci + 1, {})[vi] = t
                    moved += 1
                    continue
                if (kc, kv) != (ci + 1, vi + 1): moved += 1
                cur = out.setdefault(kc, {}).get(max(0, kv - 1))
                out[kc][max(0, kv - 1)] = (cur + ' ' + t) if cur else t
        # A chapter that is both: Vulgate Daniel 3 holds the Song of the Three as well as Daniel's own 30
        # verses, Vulgate Esther 10 its additions. The KJV verses come first and the rest follow them, so
        # the app can tell them apart by where the English lane ends and still show them.
        res = []
        for kc in range(1, max(list(out) + list(extra) + [0]) + 1):
            d = dict(out.get(kc) or {})
            ex = extra.get(kc) or {}
            if ex:
                at = (max(d) + 1) if d else 0
                for j, vi in enumerate(sorted(ex)): d[at + j] = ex[vi]
            res.append([d.get(i, '') for i in range(max(d) + 1)] if d else [])
        while res and not any(res[-1]): res.pop()
        if moved: changed[BK[b]] = moved
        kept += [f'{BK[b]}{c}' for c in range(1, nch + 1)
                 if not MOVE.get(c, True) and any(MAP.get((BK[b], c, v + 1 + SHIFT.get((BK[b], c), 0)), (BK[b], c, v + 1))
                                            != (BK[b], c, v + 1) for v in range(len(src[c-1]) if c <= len(src) else 0))]
        if not DRY: json.dump(res, open(f, 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
    print(f'{lang}: 번호가 이어지는 장 {len(SHIFT)} · 옮긴 절이 있는 책 {len(changed)} · 옮긴 절 {sum(changed.values())}',
          file=sys.stderr)
    for k, n in sorted(changed.items(), key=lambda kv: -kv[1])[:6]: print(f'   {k} {n}', file=sys.stderr)
    print(f'   본문이 이미 맞아서 지도를 쓰지 않은 장 {len(kept)}: {" ".join(kept[:40])}', file=sys.stderr)

# the spans that reveal a continuation psalm are the ones vul.vrs itself numbers
remap('la', LA_MAP, set(LO))
remap('de', DE_MAP, set(DE_MAP))
if not DRY:
    import datetime
    open(STAMP, 'w').write(datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%d %H:%M UTC'))
