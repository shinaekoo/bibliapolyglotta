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
TX = os.path.join(HERE, '..', 'text') + '/'      # the texts, one file per language and book
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
from langnorm import es_n, it_n, ru_n, ja_n, pt_n, tl_n, ceb_n, id_n, ig_n
NORM = {'la': la_n, 'en': en_n, 'de': de_n, 'fr': fr_n, 'ko': ko_n, 'zh': lambda w: w, 'es': es_n, 'it': it_n, 'ru': ru_n, 'ja': ja_n, 'pt': pt_n, 'tl': tl_n, 'ceb': ceb_n, 'id': id_n, 'ig': ig_n}
LANGS = ['la', 'de', 'fr', 'ko', 'zh', 'es', 'it', 'ru', 'ja', 'pt', 'tl', 'ceb', 'id', 'ig']
NEW = ['es', 'it', 'ru', 'ja', 'pt', 'tl', 'ceb', 'id', 'ig']
SYM = os.environ.get('SYM', 'grow-diag')   # symmetrization of the two directions

def load(pre, i): return json.load(open(f'{D if pre == "al" else TX}{pre}{i:02d}.json', encoding='utf-8'))
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
    nw = {k: load(k, b) for k in NEW}; esS = load('esS', b)
    la = load('la', LAIDX[b])
    kj = kjv_book(CODES[b])
    for c in range(1, len(en) + 1):
        cols = {'ko': ko[c-1] if c <= len(ko) else [], 'de': de[c-1] if c <= len(de) else [],
                'fr': fr[c-1] if c <= len(fr) else [], 'zh': zh[c-1] if c <= len(zh) else []}
        for k in NEW: cols[k] = nw[k][c-1] if c <= len(nw[k]) else []
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
            ss = esS[c-1][v-1] if c <= len(esS) and v <= len(esS[c-1]) else ''
            r['esS'] = [set() if x == '-' else set(x.split('+')) for x in ss.split()]
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
    # word order: the diagonal prior helps close pairs (Latin, German, French with English) and hurts
    # distant ones (Hebrew/Greek, Korean, Chinese), so it is used only for the close pairs
    diag = ['-d', '-o'] if tag in ('la-en', 'de-en', 'fr-en', 'es-en', 'it-en', 'pt-en') else []
    run = lambda *a, out: subprocess.run([os.path.join(FA, 'fast_align'), '-i', f, *diag, '-v', '-I', '6', *a], stdout=open(out, 'w'), stderr=subprocess.DEVNULL, check=True)
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
# NOSTRONG=GLOSS_JSON: no Strong's tagging of the KJV (or of the Reina-Valera) is used. KJV words are tied to
# the original by the English that STEPBible gives for each Hebrew/Greek word (tools/orig_glosses.py), then
# by fast_align for the rest.
NOSTRONG = os.environ.get('NOSTRONG')
GL = json.load(open(NOSTRONG)) if NOSTRONG else {}
GSTOP = {'obj'}
HELPER = set('one ones someone something who whom whose has have had having will would shall should may might can could let '
             'being been be is are am was were does did do i you we she her its me my your our us thou thee'.split())
FUNC = set('the a an of and to in that is it for with his he him them they their unto by on at as be was were shall will not but or from which who this these'.split())
# STEPBible's English is modern; the KJV's is not ("you" = thee, thou, ye, thy)
EQ = {'you': 'thee thou ye thy thine your yourselves', 'your': 'thy thine ye thee thou yours', 'yourself': 'thyself', 'yourselves': 'ye',
      'him': 'his he himself', 'he': 'his him', 'his': 'him he', 'them': 'their they themselves', 'they': 'their them', 'their': 'them they',
      'us': 'our we ourselves', 'we': 'us our', 'our': 'us we', 'me': 'my mine i myself', 'i': 'me my mine', 'my': 'me mine i',
      'she': 'her', 'her': 'she', 'it': 'its itself', 'its': 'it his her', 'is': 'are be', 'are': 'is be art', 'was': 'were been be wast',
      'were': 'was been', 'has': 'hath', 'have': 'hast hath', 'does': 'doth', 'do': 'doth dost', 'says': 'saith', 'said': 'saith',
      'who': 'which that whom', 'which': 'that who whom what', 'that': 'which who', 'whom': 'which who', 'children': 'sons', 'sons': 'children'}
EQ = {k: set(v.split()) for k, v in EQ.items()}
import lexres          # WordNet synonyms (WN_DIR), UniDic forms (UNIDIC_LEX)
def gmatch(a, b):
    if a == b or en_n(a) == en_n(b) or a in EQ.get(b, ()): return True
    if len(a) >= 3 and len(b) >= 3 and a not in FUNC and b not in FUNC and lexres.related(a, b): return True     # void ~ emptiness
    return len(a) >= 4 and len(b) >= 4 and a[:4] == b[:4] and difflib.SequenceMatcher(None, a, b).ratio() >= 0.7
def gloss_links(enw, o, gl, stats=None):
    """(sub-word, en word) pairs where the KJV word is one of STEPBible's English words for that sub-word
    (a repeated word goes to the occurrence nearest in relative position); then, for sub-words still
    without a KJV word, the unlinked KJV word most associated with it across the Bible (KJV "void" for
    STEPBible "emptiness")"""
    out, used = set(), set()
    low = [w.lower() for w in enw]; n, m = max(1, len(enw)), max(1, len(o))
    for k, gs in enumerate(gl):
        if k >= len(o) or o[k] in NOFUNC: continue
        content = [g for g in gs if g not in FUNC and g not in GSTOP]
        core = [g for g in content if g not in HELPER]
        # "one who plots": "one" and "who" only say that the word is a participle; when the gloss has a word of its
        # own (plots), that alone is matched, so that the KJV "one" of "one ... that imagineth" is not taken for it
        for g in (core or content or gs):      # "the/surface/of": only "surface" (the little words are other sub-words' or none)
            if g in GSTOP: continue
            js = [j for j, w in enumerate(low) if gmatch(w, g)]
            if not js: continue
            free = [j for j in js if (j, g) not in used] or js
            j = min(free, key=lambda j: abs(j / n - k / m))
            if g in FUNC and abs(j / n - k / m) > 0.3: continue      # a little word far away: probably another one
            out.add((k, j)); used.add((j, g))
    if stats:
        cx, cy, cxy = stats; got_j = {j for _, j in out}
        got_k = {k for k, j in out if not (k < len(gl) and any(g not in FUNC and g not in HELPER for g in gl[k]) and low[j] in FUNC | HELPER)}
        for k in range(len(o)):
            if k in got_k or o[k] in NOFUNC or k >= len(gl): continue
            func = all(g in FUNC or g in GSTOP for g in gl[k])
            best, bj = 0, None
            for j, w in enumerate(low):
                if j in got_j or (w in FUNC and not func): continue
                x = en_n(w); c = cxy.get((x, o[k]), 0)
                if not c: continue
                d = 2 * c / (cx[x] + cy[o[k]])
                if (c >= 3 or d >= 0.3) and d > best: best, bj = d, j      # rare words: only when nearly always together
            if bj is not None and best >= 0.08:
                out = {(k2, j2) for k2, j2 in out if k2 != k}      # its helper-word links give way to its own word
                out.add((k, bj)); got_j.add(bj); got_k.add(k)
    return out
if NOSTRONG:
    for r in rows: r['st'] = [[] for _ in r['en']]; r['esS'] = []
eo = align(EN, O, 'en-orig'); stEO = assoc(EN, O)
OE = []
for r, en, o, (ii, gg) in zip(rows, EN, O, eo):
    ex = gloss_links(r['en'], o, GL.get('%d:%d:%d' % r['key'], []), stEO) if NOSTRONG else exact(r['st'], o)
    lk, lj = {k for k, _ in ex}, {j for _, j in ex}
    add = set()
    for j, k in ii:   # untagged English words (the, of, and, his ...) by alignment
        if j < len(en) and k < len(o) and o[k] not in NOFUNC and j not in lj and (k not in lk or not r['st'][j]) and ok(stEO, en[j], o[k], 2): add.add((k, j))
    for j, k in gg:
        if j < len(en) and k < len(o) and o[k] not in NOFUNC and j not in lj and k not in lk and ok(stEO, en[j], o[k], 5): add.add((k, j))
    if NOSTRONG:   # a content word and a sub-word both still alone, paired by fast_align: take it
        lk2 = lk | {k for k, _ in add}; lj2 = lj | {j for _, j in add}
        for j, k in gg:
            if j < len(en) and k < len(o) and o[k] not in NOFUNC and j not in lj2 and k not in lk2 and r['en'][j].lower() not in FUNC:
                add.add((k, j)); lj2.add(j); lk2.add(k)
    OE.append(ex | add)

# ---- the original <-> Latin, by dictionary forms ----
# The Vulgate was translated from the Hebrew and Greek, so its words follow the original more closely than the
# KJV's do. Each Latin word has its dictionary form (Whitaker's Words, data/al*.json "lx" from tools/build_latin.py):
# across the Bible, a dictionary form and an original word (Strong's number) that keep appearing in the same verses
# belong together (cogito ~ H2803 "to think, plot"), whatever the case or tense. These pairs, one Latin word to one
# original word in each verse, nearest in position, are
#   - the Latin word's link: it goes to the English word(s) of its original word, replacing what fast_align gave it
#   - a check on the original -> KJV link: an original word that got no English word of its own (only "one", "the")
#     takes the English word the Latin word is aligned to directly (cogitans -> imagineth, so H2803 -> imagineth)
LEM = {}
for b in range(66):
    alx = load('al', b).get('lx', {})
    for c, vs in alx.items():
        for vk, toks in vs.items(): LEM[(b, int(c), int(vk[1:]))] = [t[0] if t and t[3] != 'X' else None for t in toks]
LXL = json.load(open(D + 'lxL.json', encoding='utf-8'))
LITTLE_POS = ('PRON', 'CONJ', 'PREP', 'INTERJ', 'PACK')
def lem_ok(l): return l is not None and l < len(LXL) and LXL[l] and LXL[l][3] not in LITTLE_POS
LA_LEM = [[(l if lem_ok(l) else None) for l in LEM.get(r['key'], [])][:len(r['la'])] for r in rows]
OSN = [[t if t not in NOFUNC else None for t in o] for o in O]
cl, co, clo = defaultdict(int), defaultdict(int), defaultdict(int)
for ls, os_ in zip(LA_LEM, OSN):
    sl, so = {l for l in ls if l is not None}, {t for t in os_ if t}
    for l in sl: cl[l] += 1
    for t in so: co[t] += 1
    for l in sl:
        for t in so: clo[(l, t)] += 1
def lo_dice(l, t):
    c = clo.get((l, t), 0)
    return (2 * c / (cl[l] + co[t]), c) if c else (0, 0)
LO = []
for r, ls, os_ in zip(rows, LA_LEM, OSN):
    n, m = max(1, len(ls)), max(1, len(os_)); cand = []
    for i, l in enumerate(ls):
        if l is None: continue
        for k, t in enumerate(os_):
            if not t: continue
            d, c = lo_dice(l, t)
            if (c >= 3 and d >= 0.2) or (c >= 1 and d >= 0.5):
                cand.append((d - 0.3 * abs(i / n - k / m), i, k))
    cand.sort(reverse=True); gi, gk, pr = set(), set(), set()
    for sc, i, k in cand:
        if i in gi or k in gk: continue
        pr.add((i, k)); gi.add(i); gk.add(k)
    LO.append(pr)
print('Latin words paired with the original by dictionary form', sum(len(x) for x in LO), file=sys.stderr)
XLA = [[NORM['la'](w) for w in r['la']] for r in rows]
la_direct = align(XLA, EN, 'la-en'); stLE = assoc(XLA, EN)
n_fix = 0
for r, oe, lo, (di, dg), x, o in zip(rows, OE, LO, la_direct, XLA, O):
    enw = r['en']; low = [w.lower() for w in enw]
    gl = GL.get('%d:%d:%d' % r['key'], [])
    own = lambda k, j: not (low[j] in FUNC or low[j] in HELPER)
    linked_j = {j for _, j in oe}
    for i, k in lo:
        if k >= len(o) or i >= len(x): continue
        mine = {j for k2, j in oe if k2 == k}
        if any(own(k, j) for j in mine): continue                      # it has an English word of its own
        if k < len(gl) and not any(g not in FUNC and g not in HELPER for g in gl[k]): continue   # a little word itself
        js = [j for i2, j in di if i2 == i and j < len(enw) and own(k, j) and j not in linked_j and ok(stLE, x[i], en_n(enw[j]), 1)]
        if js:
            for j in mine: oe.discard((k, j))
            for j in js: oe.add((k, j)); linked_j.add(j)
            n_fix += 1
print('original words given their English word through the Latin', n_fix, file=sys.stderr)
LO_BY = {r['key']: lo for r, lo in zip(rows, LO)}

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
        alike = lambda i, j: lang not in ('zh', 'ja', 'ru') and j < len(enw) and len(x[i]) >= 3 and difflib.SequenceMatcher(None, r[lang][i].lower(), enw[j].lower()).ratio() >= 0.7
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
        got = {i for i, _ in pairs}
        pairs |= {(i, j) for i, j in D_gen if i not in got and ((i, j) in Bg or ok(stE, x[i], en_n(enw[j]), 8))}
        if lang == 'es' and len(r['esS']) == len(x):
            # Reina-Valera 1909 is tagged with Strong's numbers, phrase by phrase ("la tierra" H776):
            # a content word and an English word with different numbers are not a pair; with the same, they are
            es_st = r['esS']
            sp = {(i, j) for i in range(len(x)) for j in range(len(enw)) if es_st[i] & set(r['st'][j])}
            content = lambda i: len(r[lang][i]) >= 4
            pairs = {(i, j) for i, j in pairs if not (content(i) and es_st[i] and r['st'][j] and not (es_st[i] & set(r['st'][j])))}
            got = {i for i, _ in pairs}
            pairs |= {(i, j) for i, j in sp if content(i) and i not in got and len(enw[j]) >= 3}
        if lang == 'la':
            # a Latin word paired with an original word by dictionary form takes that word's English words
            lo = LO_BY[r['key']]
            for i, k in lo:
                if i < len(x) and to_en.get(k):
                    pairs = {(i2, j) for i2, j in pairs if i2 != i} | {(i, j) for j in to_en[k]}
        if lang in ('ko', 'zh', 'ja', 'ru'):
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
if os.environ.get('OE_OUT'):
    json.dump({'%d:%d:%d' % r['key']: sorted(oe) for r, oe in zip(rows, OE)}, open(os.environ['OE_OUT'], 'w'))

os.makedirs(OUT, exist_ok=True)
for b in sorted({k[0] for k in LINKS}):
    al = load('al', b)
    for c in range(1, len(al['v']) + 1):
        for v in range(1, len(al['v'][c-1]) + 1):
            new = LINKS.get((b, c, v))
            if new is not None: al['v'][c-1][v-1] = {k: x for k, x in new.items() if x}
    json.dump(al, open(os.path.join(OUT, f'al{b:02d}.json'), 'w'), ensure_ascii=False, separators=(',', ':'))
print('written', file=sys.stderr)
