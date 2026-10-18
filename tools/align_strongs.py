"""Word alignment through the original languages (Strong's numbers).

Each KJV word carries a Hebrew/Greek Strong's number (kaiserlik/kjv). Every other
translation is aligned with fast_align to the verse's sequence of Strong's numbers,
and also directly to the English words. A word's English partners are then the KJV
words that carry the same Strong's number (plus direct links for untagged words).
The result keeps the app's format: al{book}.json "v"[chapter][verse][lang] = [x, en, x, en, ...].

usage: python3 align_strongs.py KJV_DIR FAST_ALIGN_BUILD_DIR OUT_DIR [book:chapter ...]
       (no book:chapter = write every chapter)
"""
import json, os, re, subprocess, sys, difflib, tempfile
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, 'analysis'))
D = os.path.join(HERE, '..', 'web', 'data') + '/'
KJV, FA, OUT = sys.argv[1], sys.argv[2], sys.argv[3]
ONLY = {tuple(int(x) for x in a.split(':')) for a in sys.argv[4:]}

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

# ---- fast_align, both directions, symmetrized ----
def align(src, tgt, tag):
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

LINKS = defaultdict(dict)
EN = [[en_n(w) for w in r['en']] for r in rows]
for lang in LANGS:
    # Chinese words are phrase-sized, so align character by character and map back
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
    # Strong's side: one token per tagged English word occurrence (a word with two numbers yields two)
    S, Smap = [], []
    for r in rows:
        toks, mp = [], []
        for j, ss in enumerate(r['st']):
            for s in ss: toks.append(s); mp.append(j)
        S.append(toks); Smap.append(mp)
    viaS = align(X, S, lang + '-strongs')
    direct = align(X, EN, lang + '-en')
    stS, stE = assoc(X, S), assoc(X, EN)
    for r, x, (vs_i, vs_g), (dr_i, dr_g), mp, stoks, etoks, cm in zip(rows, X, viaS, direct, Smap, S, EN, CM):
        # strict links always; generous ones only when the pair also co-occurs elsewhere in the Bible
        enw = r['en']
        alike = lambda i, j: lang != 'zh' and j < len(enw) and len(x[i]) >= 3 and difflib.SequenceMatcher(None, r[lang][i].lower(), enw[j].lower()).ratio() >= 0.7
        vs = {(i, k) for i, k in vs_i if i < len(x) and k < len(stoks) and (ok(stS, x[i], stoks[k], 1) or alike(i, mp[k]))} | \
             {(i, k) for i, k in vs_g if i < len(x) and k < len(stoks) and (ok(stS, x[i], stoks[k], 3) or alike(i, mp[k]))}
        dr = {(i, j) for i, j in dr_i if i < len(x) and j < len(etoks) and (ok(stE, x[i], etoks[j], 1) or alike(i, j))} | \
             {(i, j) for i, j in dr_g if i < len(x) and j < len(etoks) and (ok(stE, x[i], etoks[j], 4) or alike(i, j))}
        if not x or not r['en']: continue
        st = r['st']
        pairs = set()
        for i, k in vs:   # the aligned Strong's token points at one specific English word
            if i < len(x) and k < len(mp): pairs.add((i, mp[k]))
        got = {i for i, _ in pairs}
        for i, j in dr:   # direct links fill words the original-language route left out
            if i < len(x) and j < len(r['en']) and (i not in got or not st[j]):
                pairs.add((i, j))
        if lang in ('ko', 'zh'):   # no articles in Korean or Chinese
            pairs = {(i, j) for i, j in pairs if r['en'][j].lower() not in ('the', 'a', 'an')}
        pairs = {(cm[i], j) for i, j in pairs}   # back to the app's word units
        LINKS[r['key']][lang] = [n for p in sorted(pairs) for n in p]

# ---- write ----
os.makedirs(OUT, exist_ok=True)
for b in sorted({k[0] for k in LINKS}):
    if ONLY and b not in {x[0] for x in ONLY}: continue
    al = load('al', b)
    for c in range(1, len(al['v']) + 1):
        if ONLY and (b, c) not in ONLY: continue
        for v in range(1, len(al['v'][c-1]) + 1):
            new = LINKS.get((b, c, v))
            if new is not None: al['v'][c-1][v-1] = new
    json.dump(al, open(os.path.join(OUT, f'al{b:02d}.json'), 'w'), ensure_ascii=False, separators=(',', ':'))
    print('wrote', b, file=sys.stderr)
