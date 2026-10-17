import json, re, sys, math, time
from collections import defaultdict
D = '/home/claude/bible3/data/'
LAIDX = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,18,19,20,21,22,23,26,27,28,30,31,32,33,34,35,36,37,38,39,40,41,42,43,46,47,48,49,50,51,52,53,54,55,56,57,58,59,60,61,62,63,64,65,66,67,68,69,70,71,72]
PS = 18
WORD = re.compile(r'[^\W\d_]+')

def ps_map(h):
    if h <= 8 or h >= 148: return [(h,1,999)]
    if h == 9: return [(9,1,21)]
    if h == 10: return [(9,22,999)]
    if h <= 113: return [(h-1,1,999)]
    if h == 114: return [(113,1,8)]
    if h == 115: return [(113,9,999)]
    if h == 116: return [(114,1,999),(115,1,999)]
    if h <= 146: return [(h-1,1,999)]
    return [(146,1,999),(147,1,999)]

# ---- normalizers ----
LA_END = sorted('ibus ius ae am as em es ia is nt os ud um us a e i o u orum arum ibus erunt erit avit ivit abit ebit ant ent unt it at et'.split(), key=len, reverse=True)
QUE_EX = set('quoque atque itaque neque usque quisque ubique denique undique utique plerumque absque quinque'.split())
def la_norm(w):
    w = w.lower().replace('æ','ae').replace('œ','oe').replace('j','i').replace('v','u')
    if w.endswith('que') and w not in QUE_EX and len(w) > 5: w = w[:-3]
    for e in LA_END:
        if w.endswith(e) and len(w) - len(e) >= 3: return w[:-len(e)]
    return w
EN_END = ['eth','est','ing','edst','ed','es','s','ly']
def en_norm(w):
    w = w.lower()
    for e in EN_END:
        if w.endswith(e) and len(w) - len(e) >= 3 and not w.endswith('ss'): return w[:-len(e)]
    return w
DE_END = ['ern','em','en','er','es','e','n','s','st','t']
def de_norm(w):
    w = w.lower()
    for e in DE_END:
        if w.endswith(e) and len(w) - len(e) >= 3: return w[:-len(e)]
    return w
FR_END = ['aient','ait','ent','ez','ons','ées','és','ée','é','er','es','s','x','e']
def fr_norm(w):
    w = w.lower()
    for e in FR_END:
        if w.endswith(e) and len(w) - len(e) >= 3: return w[:-len(e)]
    return w
KO_SUF = sorted(('이니라 이라 이요 이며 이니 이로다 이시라 이시니 이었더라 이더라 '
 '께서는 께서 에게서 에게는 에게 한테 으로써 으로서 으로는 으로 로써 로서 로는 로 에서는 에서 에는 에도 에 '
 '이나 이든지 이여 이시여 여 아 야 과 와 의 은 는 이 가 을 를 도 만 까지 부터 마다 처럼 같이 보다 조차 '
 '하시니라 하니라 하리라 하시고 하시며 하시매 하시되 하시니 하셨더라 하였더라 하였으니 하였고 하였느니라 하였다 하더라 하고 하여 하며 하매 하니 하되 하라 하사 하심 함 할 한 하는 하신 하시는 하실 '
 '되니라 되리라 되었더라 되고 되어 되며 되매 된 될 되는 '
 '니라 리라 더라 느니라 도다 로다 노라 시니 시고 시며 시매 시되 시라 셨더라 였더라 였고 였으니 었더라 었고 었으니 았더라 았고 '
 '고 며 매 니 되 서 면 거든 려고 러 사 므로 으매 으니 으며 으라 라 다 는 은 을 ㄴ').split(), key=len, reverse=True)
def ko_norm(w):
    s = w
    for _ in range(2):
        for e in KO_SUF:
            if s.endswith(e) and len(s) - len(e) >= 1:
                s = s[:-len(e)]; break
    return s

NORM = {'la': la_norm, 'en': en_norm, 'de': de_norm, 'fr': fr_norm, 'ko': ko_norm}

def toks(lang, text):
    ws = WORD.findall(text)
    out = []
    f = NORM[lang]
    for i, w in enumerate(ws):
        if lang == 'ko':
            out.append([w, '~' + f(w)])
        else:
            out.append([f(w)])
    return out

# ---- load ----
def load(pre, i):
    return json.load(open(f'{D}{pre}{i:02d}.json'))

verses = []  # list of dict lang->text, key (b,c,v)
shifts = {}  # (c)->{'la':k,'de':k}
for b in range(66):
    en = load('en', b); ko = load('ko', b); de = load('de', b); fr = load('fr', b)
    la = load('la', LAIDX[b])
    for c in range(1, len(en) + 1):
        E = en[c-1]
        K = ko[c-1] if c <= len(ko) else []
        G = de[c-1] if c <= len(de) else []
        F = fr[c-1] if c <= len(fr) else []
        if b == PS:
            L = []
            for ch, a, z in ps_map(c):
                vs = la[ch-1]; L += vs[a-1:min(z, len(vs))]
            ref = len(K) or len(E)
            sl = max(0, min(3, len(L) - ref)); sd = max(0, min(3, len(G) - ref))
            shifts[c] = {'la': sl, 'de': sd}
            L = L[sl:]; G = G[sd:]
        else:
            L = la[c-1] if c <= len(la) else []
        for v in range(1, len(E) + 1):
            row = {'b': b, 'c': c, 'v': v, 'en': E[v-1]}
            for k, arr in (('ko', K), ('de', G), ('fr', F), ('la', L)):
                if v <= len(arr): row[k] = arr[v-1]
            # Daniel 3: Vulgate inserts 24-90
            if b == 26 and c == 3 and v >= 24:
                row['la'] = la[2][v + 66] if v + 66 < len(la[2]) else ''
            verses.append(row)
print('verses', len(verses), file=sys.stderr)

# ---- IBM model 1 ----
def model1(src_tok, tgt_tok, iters=5):
    # src_tok/tgt_tok: list of verses, each a list of token strings (flattened)
    t = defaultdict(lambda: 1e-3)
    # init uniform via cooccurrence
    for it in range(iters):
        cnt = defaultdict(float); tot = defaultdict(float)
        for S, T in zip(src_tok, tgt_tok):
            if not S or not T: continue
            S2 = S + ['<null>']
            for tw in T:
                if it == 0:
                    z = len(S2);
                    for sw in S2:
                        cnt[(sw, tw)] += 1.0 / z; tot[sw] += 1.0 / z
                else:
                    ps = [t[(sw, tw)] for sw in S2]; z = sum(ps)
                    for sw, p in zip(S2, ps):
                        q = p / z; cnt[(sw, tw)] += q; tot[sw] += q
        t = defaultdict(lambda: 1e-6, {k: v / tot[k[0]] for k, v in cnt.items()})
        print('  iter', it, len(t), file=sys.stderr)
    return t

LINKS = {}
for lang in ['la', 'ko']:
    t0 = time.time()
    idx = [r for r in verses if r.get(lang) and r.get('en')]
    X = [toks(lang, r[lang]) for r in idx]
    Y = [toks('en', r['en']) for r in idx]
    Xf = [[x for w in s for x in w] for s in X]
    Yf = [[x for w in s for x in w] for s in Y]
    print(lang, len(idx), file=sys.stderr)
    t_ye = model1(Xf, Yf)   # p(en | x)
    t_xe = model1(Yf, Xf)   # p(x | en)
    TH = 0.06
    for r, xs, ys in zip(idx, X, Y):
        if not xs or not ys: continue
        M = [[max(math.sqrt(t_ye.get((xv, y[0]), 1e-6) * t_xe.get((y[0], xv), 1e-6)) for xv in x) for y in ys] for x in xs]
        links = set()
        for i, row in enumerate(M):
            j = max(range(len(ys)), key=lambda j: row[j])
            if row[j] >= TH: links.add((i, j))
        for j in range(len(ys)):
            i = max(range(len(xs)), key=lambda i: M[i][j])
            if M[i][j] >= TH: links.add((i, j))
        key = (r['b'], r['c'], r['v'])
        LINKS.setdefault(key, {})[lang] = [n for p in sorted(links) for n in p]
    print(lang, 'done', round(time.time() - t0), 's', file=sys.stderr)

# ---- write per book ----
for b in range(66):
    en = load('en', b)
    out = {'v': []}
    for c in range(1, len(en) + 1):
        out['v'].append([LINKS.get((b, c, v), {}) for v in range(1, len(en[c-1]) + 1)])
    if b == PS:
        out['sh'] = [shifts[c] for c in range(1, len(en) + 1)]
    json.dump(out, open(f'{D}al{b:02d}.json', 'w'), separators=(',', ':'))
print('written', file=sys.stderr)
