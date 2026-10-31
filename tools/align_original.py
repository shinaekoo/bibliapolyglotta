"""Word alignment checked across all languages through the original text.

Every translation (KJV, Vulgate, Luther, Segond, 개역한글, 和合本) is aligned with fast_align to the
same sequence: the Hebrew/Greek sub-words of the verse (prefixes, stems and pronoun suffixes, as
Strong's numbers, from STEPBible TAHOT/TAGNT). KJV words are tied to the original first by their
own Strong's tags, then by fast_align for the untagged little words (the, of, and, his ...).

A link between a word of language L and a KJV word is then kept when
  - both are tied to the same original sub-word (the route through the original), and either
    fast_align was sure of the L link (both directions agree) or the direct L-English
    alignment says the same thing (cross-check), or
  - the word has no link through the original and the direct L-English alignment is sure of it.
The result keeps the app's format: al{book}.json "v"[chapter][verse][lang] = [x, en, x, en, ...],
plus "or" = [original word, en word, ...].

usage: python3 tools/align_original.py KJV_DIR FAST_ALIGN_BUILD_DIR SUBS_JSON OUT_DIR
  SUBS_JSON comes from tools/build_original.py (SUBS_OUT=...); run that script first.
"""
import json, os, re, subprocess, sys, difflib, tempfile
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
D = os.path.join(HERE, '..', 'web', 'data') + '/'
KJV, FA, SUBS, OUT = sys.argv[1:5]
ONLY = set()
CODES = 'Gen Exo Lev Num Deu Jos Jdg Rth 1Sa 2Sa 1Ki 2Ki 1Ch 2Ch Ezr Neh Est Job Psa Pro Ecc Sng Isa Jer Lam Eze Dan Hos Joe Amo Oba Jon Mic Nah Hab Zep Hag Zec Mal Mat Mar Luk Jhn Act Rom 1Co 2Co Gal Eph Phl Col 1Th 2Th 1Ti 2Ti Tit Phm Heb Jas 1Pe 2Pe 1Jo 2Jo 3Jo Jde Rev'.split()
LAIDX = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,18,19,20,21,22,23,26,27,28,30,31,32,33,34,35,36,37,38,39,40,41,42,43,46,47,48,49,50,51,52,53,54,55,56,57,58,59,60,61,62,63,64,65,66,67,68,69,70,71,72]
PS, DAN = 18, 26
W = re.compile(r'[^\W\d_]+')
SKIP = {'H853'}          # Hebrew object marker: never a word of its own in translation

# ---- normalizers (same as the first alignment) ----
LA_END = sorted('ibus ius ae am as em es ia is nt os ud um us a e i o u orum arum ibus erunt erit avit ivit abit ebit ant ent unt it at et'.split(), key=len, reverse=True)
QUE_EX = set('quoque atque itaque neque usque quisque ubique denique undique utique plerumque absque quinque'.split())
def la_n(w):
    w = w.lower().replace('æ', 'ae').replace('œ', 'oe').replace('j', 'i').replace('v', 'u')
    if w.endswith('que') and w not in QUE_EX and len(w) > 5: w = w[:-3]
    for e in LA_END:
        if w.endswith(e) and len(w) - len(e) >= 3: return w[:-len(e)]
    return w
def suf(ends):
    ends = sorted(ends, key=len, reverse=True)
    def f(w):
        w = w.lower()
        for e in ends:
            if w.endswith(e) and len(w) - len(e) >= 3: return w[:-len(e)]
        return w
    return f
en_n = suf(['eth', 'est', 'ing', 'edst', 'ed', 'es', 's', 'ly'])
de_n = suf(['ern', 'em', 'en', 'er', 'es', 'e', 'n', 's', 'st', 't'])
fr_n = suf(['aient', 'ait', 'ent', 'ez', 'ons', 'ées', 'és', 'ée', 'é', 'er', 'es', 's', 'x', 'e'])
KO_SUF = sorted(('이니라 이라 이요 이며 이니 이로다 이시라 이시니 이었더라 이더라 '
 '께서는 께서 에게서 에게는 에게 한테 으로써 으로서 으로는 으로 로써 로서 로는 로 에서는 에서 에는 에도 에 '
 '이나 이든지 이여 이시여 여 아 야 과 와 의 은 는 이 가 을 를 도 만 까지 부터 마다 처럼 같이 보다 조차 '
 '하시니라 하니라 하리라 하시고 하시며 하시매 하시되 하시니 하셨더라 하였더라 하였으니 하였고 하였느니라 하였다 하더라 하고 하여 하며 하매 하니 하되 하라 하사 하심 함 할 한 하는 하신 하시는 하실 '
 '되니라 되리라 되었더라 되고 되어 되며 되매 된 될 되는 '
 '니라 리라 더라 느니라 도다 로다 노라 시니 시고 시며 시매 시되 시라 셨더라 였더라 였고 였으니 었더라 었고 었으니 았더라 았고 '
 '고 며 매 니 되 서 면 거든 려고 러 사 므로 으매 으니 으며 으라 라 다 는 은 을 ㄴ').split(), key=len, reverse=True)
def ko_n(w):
    s = w
    for _ in range(2):
        for e in KO_SUF:
            if s.endswith(e) and len(s) - len(e) >= 1:
                s = s[:-len(e)]; break
    return s or w
NORM = {'la': la_n, 'en': en_n, 'de': de_n, 'fr': fr_n, 'ko': ko_n, 'zh': lambda w: w}
LANGS = ['la', 'de', 'fr', 'ko', 'zh']
SYM = os.environ.get('SYM', 'grow-diag')   # symmetrization of the two directions

def load(pre, i): return json.load(open(f'{D}{pre}{i:02d}.json'))
def ps_map(h):
    if h <= 8 or h >= 148: return [(h, 1, 999)]
    if h == 9: return [(9, 1, 21)]
    if h == 10: return [(9, 22, 999)]
    if h <= 113: return [(h - 1, 1, 999)]
    if h == 114: return [(113, 1, 8)]
    if h == 115: return [(113, 9, 999)]
    if h == 116: return [(114, 1, 999), (115, 1, 999)]
    if h <= 146: return [(h - 1, 1, 999)]
    return [(146, 1, 999), (147, 1, 999)]

# ---- Strong's numbers on the app's own KJV tokens ----
TAG = re.compile(r'\[([HG]\d+)\]')
def kjv_tokens(s):
    """[(word, [strongs...])] from a tagged KJV verse; tags belong to the word before them."""
    s = re.sub(r'</?em>', '', s).replace('[[', ' ').replace(']]', ' ')
    out = []
    for m in re.finditer(r'\[([HG]\d+)\]|[^\W\d_]+', s):
        if m.group(1):
            if out: out[-1][1].append(m.group(1))
        else:
            out.append((m.group(0), []))
    return out
def strongs_for(app_words, tagged):
    a = [w.lower() for w in app_words]; b = [w.lower() for w, _ in tagged]
    res = [[] for _ in app_words]
    for blk in difflib.SequenceMatcher(a=a, b=b, autojunk=False).get_matching_blocks():
        for k in range(blk.size):
            res[blk.a + k] = [t for t in tagged[blk.b + k][1] if t not in SKIP]
    return res

EN_RE = re.compile(r'"((?:[1-3]?[A-Za-z]{2,3})\|(\d+)\|(\d+))"\s*:\s*\{\s*"en"\s*:\s*"((?:[^"\\]|\\.)*)"')
def kjv_book(code):
    """{'Gen|1': {'Gen|1|1': {'en': ...}}} — read with a pattern, since a few files have broken quotes in other languages."""
    out = defaultdict(dict)
    for m in EN_RE.finditer(open(os.path.join(KJV, code + '.json'), encoding='utf-8').read()):
        if m.group(1).split('|')[0] != code: continue
        try: t = json.loads('"' + m.group(4) + '"')
        except Exception: t = m.group(4)
        out[f'{code}|{m.group(2)}'][m.group(1)] = {'en': t}
    return out

rows = []   # one per verse: {key, en words, strong per en word, lang -> words}
for b in range(66):
    en, ko, de, fr, zh = (load(p, b) for p in ('en', 'ko', 'de', 'fr', 'zh'))
    la = load('la', LAIDX[b])
    kj = kjv_book(CODES[b])
    for c in range(1, len(en) + 1):
        cols = {'ko': ko[c-1] if c <= len(ko) else [], 'de': de[c-1] if c <= len(de) else [],
                'fr': fr[c-1] if c <= len(fr) else [], 'zh': zh[c-1] if c <= len(zh) else []}
        if b == PS:   # Latin (Septuagint numbering) and German titles: same shifts as the app
            L = []
            for ch, a0, z in ps_map(c):
                vs = la[ch-1]; L += vs[a0-1:min(z, len(vs))]
            ref = len(cols['ko']) or len(en[c-1])
            L = L[max(0, min(3, len(L) - ref)):]
            G = cols['de']; cols['de'] = G[max(0, min(3, len(G) - ref)):]
        else:
            L = la[c-1] if c <= len(la) else []
            if b == DAN and c == 3 and len(L) > 90: L = L[:23] + L[90:]
        cols['la'] = L
        kch = kj.get(f'{CODES[b]}|{c}', {})
        for v in range(1, len(en[c-1]) + 1):
            ew = W.findall(en[c-1][v-1] or '')
            kv = kch.get(f'{CODES[b]}|{c}|{v}')
            st = strongs_for(ew, kjv_tokens(kv['en'])) if kv else [[] for _ in ew]
            r = {'key': (b, c, v), 'en': ew, 'st': st}
            for k in LANGS:
                t = cols[k][v-1] if v <= len(cols[k]) else ''
                r[k] = W.findall(t or '')
            rows.append(r)
print('verses', len(rows), 'tagged words', sum(1 for r in rows for s in r['st'] if s), '/', sum(len(r['en']) for r in rows), file=sys.stderr)

CACHE = os.environ.get('FA_CACHE')
def align(src, tgt, tag):
    if CACHE and os.path.exists(os.path.join(CACHE, tag + '.json')):
        return [tuple(map(lambda z: [tuple(p) for p in z], x)) for x in json.load(open(os.path.join(CACHE, tag + '.json')))]
    res = _align(src, tgt, tag)
    if CACHE:
        os.makedirs(CACHE, exist_ok=True); json.dump(res, open(os.path.join(CACHE, tag + '.json'), 'w'))
    return res
def _align(src, tgt, tag):
    tmp = tempfile.mkdtemp()
    f = os.path.join(tmp, 'in.txt')
    with open(f, 'w') as fh:
        for s, t in zip(src, tgt):
            fh.write((' '.join(s) or '<e>') + ' ||| ' + (' '.join(t) or '<e>') + '\n')
    run = lambda *a, out: subprocess.run([os.path.join(FA, 'fast_align'), '-i', f, '-d', '-o', '-v', '-I', '6', *a], stdout=open(out, 'w'), stderr=subprocess.DEVNULL, check=True)
    run(out=f + '.fwd'); run('-r', out=f + '.rev')
    def sym(how):
        lines = subprocess.run([os.path.join(FA, 'atools'), '-i', f + '.fwd', '-j', f + '.rev', '-c', how], capture_output=True, text=True, check=True).stdout.splitlines()
        return [[tuple(map(int, p.split('-'))) for p in line.split()] for line in lines]
    print('  aligned', tag, file=sys.stderr)
    return list(zip(sym('intersect'), sym('grow-diag-final-and')))

def assoc(src, tgt):
    """Bible-wide verse co-occurrence counts, for checking the generous links."""
    cx, cy, cxy = defaultdict(int), defaultdict(int), defaultdict(int)
    for a, b in zip(src, tgt):
        sa, sb = set(a), set(b)
        for x in sa: cx[x] += 1
        for y in sb: cy[y] += 1
        for x in sa:
            for y in sb: cxy[(x, y)] += 1
    return cx, cy, cxy
def ok(stats, x, y, minc):
    """co-occurs often enough, or both words are rare and always appear together"""
    cx, cy, cxy = stats; c = cxy.get((x, y), 0)
    if not c: return False
    d = 2 * c / (cx[x] + cy[y])
    return (c >= minc and d >= 0.05) or d >= 0.3


def snum(s):
    m = re.match(r'([HG])0*(\d+)', s or '')
    return f'{m.group(1)}{m.group(2)}' if m else None

SUB = json.load(open(SUBS))
NOFUNC = {'H853'}   # object marker: carries no word in translation
O, OMAP = [], []    # per verse: original sub-word tokens, and the on-screen original word of each
for r in rows:
    b, c, v = r['key']; s = SUB.get(f'{b}:{c}:{v}', [])
    O.append([t for _, t in s]); OMAP.append([w for w, _ in s])
    r['st'] = [[snum(t) for t in ss if snum(t)] for ss in r['st']]
EN = [[en_n(w) for w in r['en']] for r in rows]

# ---- KJV <-> original ----
def exact(st, otoks):
    """(sub-word, en word) pairs for the same Strong's number; repeats paired in order"""
    oo, ee = defaultdict(list), defaultdict(list)
    for k, t in enumerate(otoks):
        if t not in NOFUNC: oo[t].append(k)
    for j, ss in enumerate(st):
        for t in ss: ee[t].append(j)
    out = set()
    for t, ks in oo.items():
        js = ee.get(t)
        if not js: continue
        if len(ks) == len(js): out |= set(zip(ks, js))
        elif len(ks) == 1: out |= {(ks[0], j) for j in js}
        elif len(js) == 1: out |= {(k, js[0]) for k in ks}
        else: out |= {(k, js[min(len(js) - 1, round(n * len(js) / len(ks)))]) for n, k in enumerate(ks)}
    return out
eo = align(EN, O, 'en-orig'); stEO = assoc(EN, O)
OE = []
for r, en, o, (ii, gg) in zip(rows, EN, O, eo):
    ex = exact(r['st'], o)
    lk, lj = {k for k, _ in ex}, {j for _, j in ex}
    add = set()
    for j, k in ii:   # untagged English words (the, of, and, his ...) by alignment
        if j < len(en) and k < len(o) and o[k] not in NOFUNC and j not in lj and (k not in lk or not r['st'][j]) and ok(stEO, en[j], o[k], 2): add.add((k, j))
    for j, k in gg:
        if j < len(en) and k < len(o) and o[k] not in NOFUNC and j not in lj and k not in lk and ok(stEO, en[j], o[k], 5): add.add((k, j))
    OE.append(ex | add)

LINKS = defaultdict(dict)
stat = {}
for lang in LANGS:
    if lang == 'zh':
        X, CM = [], []
        for r in rows:
            xs, cm = [], []
            for wi, w in enumerate(r[lang]):
                for ch in w: xs.append(ch); cm.append(wi)
            X.append(xs); CM.append(cm)
    else:
        X = [[NORM[lang](w) for w in r[lang]] for r in rows]
        CM = [list(range(len(x))) for x in X]
    viaO = align(X, O, lang + '-orig'); direct = align(X, EN, lang + '-en')
    stO, stE = assoc(X, O), assoc(X, EN)
    n_words = n_linked = n_agree = n_links = 0
    for r, x, o, oe, (oi, og), (di, dg), cm in zip(rows, X, O, OE, viaO, direct, CM):
        if not x or not r['en']: continue
        enw = r['en']
        alike = lambda i, j: lang != 'zh' and j < len(enw) and len(x[i]) >= 3 and difflib.SequenceMatcher(None, r[lang][i].lower(), enw[j].lower()).ratio() >= 0.7
        to_en = defaultdict(set)
        for k, j in oe: to_en[k].add(j)
        D_sure = {(i, j) for i, j in di if i < len(x) and j < len(enw) and (ok(stE, x[i], en_n(enw[j]), 1) or alike(i, j))}
        D_gen = {(i, j) for i, j in dg if i < len(x) and j < len(enw) and (ok(stE, x[i], en_n(enw[j]), 4) or alike(i, j))}
        DD = D_sure | D_gen
        # through the original
        Bs, Bg = set(), set()
        for i, k in oi:
            if i < len(x) and k < len(o) and o[k] not in NOFUNC and ok(stO, x[i], o[k], 1):
                Bs |= {(i, j) for j in to_en.get(k, ())}
        for i, k in og:
            if i < len(x) and k < len(o) and o[k] not in NOFUNC and ok(stO, x[i], o[k], 3):
                Bg |= {(i, j) for j in to_en.get(k, ())}
        pairs = set(Bs)                      # both directions agree on the original
        pairs |= {p for p in Bg if p in DD}   # generous original link, confirmed by the direct alignment
        pairs |= {p for p in Bg if p not in DD and alike(*p)}
        got = {i for i, _ in pairs}
        pairs |= {(i, j) for i, j in D_sure if i not in got}   # words the original route left out
        pairs |= {(i, j) for i, j in D_gen if i not in got and (i, j) in Bg}
        if lang in ('ko', 'zh'):
            pairs = {(i, j) for i, j in pairs if enw[j].lower() not in ('the', 'a', 'an')}
        n_links += len(pairs); n_agree += len(pairs & DD & (Bs | Bg))
        pairs = {(cm[i], j) for i, j in pairs}
        n_words += len(r[lang]); n_linked += len({i for i, _ in pairs})
        LINKS[r['key']][lang] = [n for p in sorted(pairs) for n in p]
    stat[lang] = (round(100 * n_linked / max(1, n_words), 1), round(100 * n_agree / max(1, n_links), 1))
    print(lang, 'coverage %', stat[lang][0], 'links confirmed by both routes %', stat[lang][1], file=sys.stderr)
# original word -> en word, on screen
for r, oe, om in zip(rows, OE, OMAP):
    LINKS[r['key']]['or'] = [n for p in sorted({(om[k], j) for k, j in oe if k < len(om)}) for n in p]
cov_en = sum(len({j for _, j in oe}) for oe in OE) / max(1, sum(len(r['en']) for r in rows))
print('en coverage through the original %', round(100 * cov_en, 1), file=sys.stderr)

os.makedirs(OUT, exist_ok=True)
for b in sorted({k[0] for k in LINKS}):
    al = load('al', b)
    for c in range(1, len(al['v']) + 1):
        for v in range(1, len(al['v'][c-1]) + 1):
            new = LINKS.get((b, c, v))
            if new is not None: al['v'][c-1][v-1] = {k: x for k, x in new.items() if x}
    json.dump(al, open(os.path.join(OUT, f'al{b:02d}.json'), 'w'), ensure_ascii=False, separators=(',', ':'))
print('written', file=sys.stderr)
