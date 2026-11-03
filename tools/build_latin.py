"""Latin word analysis for the whole Bible without PROIEL -> the "lx" part of web/data/al{book}.json, lxL.json

Whitaker's Words (free for any use) gives every possible reading of a Latin word; the reading is chosen by
the old context rules (tools/analysis/full_lx.py) plus the grammar of the Hebrew/Greek word the Latin word is
tied to (STEPBible TAHOT/TAGNT, CC BY 4.0): case, number and person of the Greek, part of speech and verb mood
of both. Ties come from fast_align between Latin and the original and from the Latin-English-original links
of tools/align_original.py (NOSTRONG mode), so no Strong's tagging of a translation is used.
Tokens: [lemma id, stem length, ending length, grammar code, source]; source 0 = context rules only,
1 = checked against the original's grammar, 2 = reviewed by hand (Genesis 1, kept as it is).
usage: WW_DIR=... python3 tools/build_latin.py SUBS_JSON LA_ORIG_CACHE_JSON OE_JSON
  LA_ORIG_CACHE_JSON: FA_CACHE/la-orig.json and OE_JSON: OE_OUT from tools/align_original.py
"""
import json, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, 'analysis'))
import full_lx as F
from words import ENTRIES, nz
TX = os.path.join(HERE, '..', 'text') + '/'; D = os.path.join(HERE, '..', 'web', 'data') + '/'
F.DATA = TX
SUB = json.load(open(sys.argv[1])); LAORIG = json.load(open(sys.argv[2])); OEN = json.load(open(sys.argv[3]))
W = re.compile(r'[^\W\d_]+')
ROW = {}; n = 0
for b in range(66):
    for c, vs in enumerate(json.load(open(f'{TX}en{b:02d}.json')), 1):
        for v in range(1, len(vs) + 1): ROW[(b, c, v)] = n; n += 1
LXL = json.load(open(D + 'lxL.json'))
BYD = {}
for i, r in enumerate(LXL):
    if r: BYD.setdefault(r[0], i)

# ---- the original word's grammar as Latin features ----
GCASE = {'N': 'NOM', 'G': 'GEN', 'D': 'DAT', 'A': 'ACC', 'V': 'VOC'}
GTENSE = {'P': 'PRES', 'I': 'IMPF', 'F': 'FUT', 'A': 'PERF', 'R': 'PERF', 'L': 'PLUP'}
GMOOD = {'I': 'IND', 'S': 'SUB', 'O': 'SUB', 'M': 'IMP', 'N': 'INF', 'P': 'PPL'}
def greek(m):
    p = m.split('-'); f = {'pos': p[0]}
    if p[0] == 'V' and len(p) > 1:
        t = p[1]
        if t[:1] == '2': t = t[1:]
        if len(t) >= 3: f.update(tense=GTENSE.get(t[0]), mood=GMOOD.get(t[2]), voice='PASSIVE' if t[1] == 'P' else 'ACTIVE' if t[1] == 'A' else None)
        if len(p) > 2:
            x = p[2]
            if x[:1] in '123': f.update(pers=x[0], num=x[1:2])
            elif len(x) >= 3: f.update(case=GCASE.get(x[0]), num=x[1], gen=x[2])
    elif len(p) > 1 and len(p[1]) >= 2:
        x = p[1]
        if x[0] in GCASE: f.update(case=GCASE[x[0]], num=x[1], gen=x[2] if len(x) > 2 else None)
        elif x[0] in '123' and len(x) >= 4: f.update(pers=x[0], case=GCASE.get(x[1]), num=x[2], gen=x[3])
    return f
HMOOD = {'v': 'IMP', 'a': 'INF', 'c': 'INF', 'r': 'PPL', 's': 'PPL'}
def hebrew(seg):
    """Hebrew number and tense do not carry over to Latin (שָׁמַיִם, אֱלֹהִים are plural; wayyiqtol of אמר is ait):
    only the part of speech, and for verbs the mood (imperative, infinitive, participle) and person"""
    s = seg[1:] if seg[:1] in 'HA' and len(seg) > 1 and seg[1].isupper() else seg
    f = {'pos': s[:1]}
    if s[:1] == 'V' and len(s) >= 3:
        if s[2] in HMOOD: f['mood'] = HMOOD[s[2]]
        if s[3:4] in ('1', '2', '3'): f['pers'] = s[3]
    return f
def orig_feats(al, b, c, v):
    ow = (al['ow'][c-1][v-1] or '').split(' ') if c - 1 < len(al['ow']) and v - 1 < len(al['ow'][c-1]) else []
    out, seen = [], {}
    for wi, strong in SUB.get(f'{b}:{c}:{v}', []):
        g = ow[wi].split('|')[1] if wi < len(ow) and '|' in ow[wi] else ''
        k = seen.get(wi, 0); seen[wi] = k + 1
        if b < 39:
            segs = g.split('/'); f = hebrew(segs[k] if k < len(segs) else segs[-1])
        else: f = greek(g)
        f['st'] = strong; out.append(f)
    return out
# Latin in / sub / super take the accusative for motion, the ablative for place: the Greek says which
PREP_CASE = {'G1519': 'ACC', 'G4314': 'ACC', 'G1722': 'ABL', 'G1537': 'ABL', 'G575': 'ABL', 'G3844': None}
def bonus(c, fs):
    if not fs: return 0
    ip, g = c['ipos'], c['gram']; dpos = ENTRIES[c['idx']]['pos']; best = 0
    for f in fs:
        s = 0; pos = f.get('pos')
        if pos == 'N' and dpos == 'N': s += 1.5          # a noun in the original: a Latin noun (mundus "world", not "clean")
        elif pos == 'N' and dpos in ('V', 'ADJ') and ip != 'VPAR': s -= 0.8
        elif pos == 'A' and dpos == 'ADJ': s += 0.8
        elif pos == 'V' and dpos == 'V': s += 0.8
        if ip in ('N', 'ADJ', 'PRON', 'NUM') and g:
            cs, nm = g[0], g[1] if len(g) > 1 else None
            if f.get('case'):
                if f['case'] == cs: s += 3
                elif f['case'] == 'DAT' and cs == 'ABL': s += 1.5
                elif f['case'] == 'GEN' and cs == 'ABL': s += 0.5
                else: s -= 1.5
            if f.get('num') and nm: s += 1.2 if f['num'] == nm else -1
            if pos == 'V' and f.get('mood') != 'PPL' and f.get('case'): s -= 1.5
        elif ip == 'V' and g:
            t, vo, m = g[0], g[1], g[2]
            if pos == 'V':
                s += 1
                if f.get('mood'):
                    if f['mood'] == m: s += 2
                    elif f['mood'] == 'PPL': s -= 1.5
                elif m in ('SUB', 'IMP', 'INF') and b_is_nt(f): s -= 1.5
                if f.get('tense') and t: s += 0.6 if f['tense'] == t else 0
                if f.get('pers') and len(g) > 3: s += 1 if f['pers'] == g[3] else -0.8
                if f.get('num') and len(g) > 4: s += 0.6 if f['num'] == g[4] else -0.6
                if f.get('voice') and vo: s += 0.5 if f['voice'] == vo else 0
            elif pos in ('N', 'A') and f.get('case'): s -= 1.5
        elif ip == 'VPAR' and g:
            if f.get('mood') == 'PPL': s += 2.5
            if f.get('case') and f['case'] == g[0]: s += 2
            if f.get('num') and len(g) > 1 and f['num'] == g[1]: s += 0.8
        elif ip == 'PREP' and pos in ('PREP', 'R'): s += 1
        elif ip == 'CONJ' and pos in ('CONJ', 'C'): s += 1
        best = max(best, s)
    return best
b_is_nt = lambda f: 'tense' in f            # Greek features carry a tense; Hebrew ones here do not

def lemma(e_idx, d):
    if d not in BYD:
        e = ENTRIES[e_idx]; BYD[d] = len(LXL); LXL.append([d, '', e['mean'], e['pos'], ''])
    return BYD[d]
def name_lemma(w):
    if w not in BYD: BYD[w] = len(LXL); LXL.append([w, '', '', 'PN', ''])
    return BYD[w]
def analyse(text, feats_of):
    toks = W.findall(text); out = []; prev_prep = None; since = 9
    for i, w in enumerate(toks):
        lw = nz(w); prev = nz(toks[i-1]) if i else None; nxt = nz(toks[i+1]) if i + 1 < len(toks) else None
        cap = w[0].isupper() and i > 0; cs = F.cands(w)
        if lw == 'ut': cs = [c for c in cs if c['ipos'] in ('CONJ', 'ADV')] or cs
        if not cs:
            out.append([name_lemma(w) if w[0].isupper() else lemma_unknown(lw), len(w), 0, 'PN' if w[0].isupper() else 'X', 0]); since += 1; continue
        pp = prev_prep if since <= 3 else None; nraw = toks[i+1] if i + 1 < len(toks) else None
        fs = feats_of(i)
        best = max(cs, key=lambda c: F.score(c, lw, cap, prev, nxt, pp, nraw) + bonus(c, fs))
        code = F.gcode(best)
        if best['ipos'] == 'PREP':
            pc = F.prep_case(w, best, nraw)
            if lw in F.BOTH_PREP:
                gc = [PREP_CASE.get(f.get('st')) for f in fs if PREP_CASE.get(f.get('st'))]
                nf = feats_of(i + 1) if i + 1 < len(toks) else []
                nc = [f.get('case') for f in nf if f.get('case')]
                both = bool(nraw) and {'ACC', 'ABL'} <= F.cases_of(nraw)     # the next word could be either
                if both and nc: pc = 'ACC' if nc[0] == 'ACC' else 'ABL' if nc[0] in ('DAT', 'GEN') else pc
                elif both and gc: pc = gc[0]
            code = 'PREP.' + (pc or ''); prev_prep = (lw, pc); since = 0
        else:
            since += 1
            if best['ipos'] == 'V': prev_prep = None
        out.append([lemma(best['idx'], F.dict_form(ENTRIES[best['idx']])), len(best['stem']), len(best['ending']), code, 1 if fs else 0])
    return out
def lemma_unknown(lw):
    if lw not in BYD: BYD[lw] = len(LXL); LXL.append([lw, '', '', 'X', ''])
    return BYD[lw]

stat = {'tokens': 0, 'checked': 0, 'kept': 0}
for b in range(66):
    f = f'{D}al{b:02d}.json'; al = json.load(open(f))
    lx = al.get('lx', {})
    for c in range(1, len(al['v']) + 1):
        old = lx.get(str(c), {}); new = {}
        for a, text in F.latin_rows(b, c):
            if old.get(a) and all(t[4] == 2 for t in old[a]): new[a] = old[a]; stat['kept'] += len(old[a]); continue
            v = int(a[1:]) if a[0] == 'v' else 0
            if v and (b, c, v) in ROW:
                inter, gdfa = LAORIG[ROW[(b, c, v)]]
                of = orig_feats(al, b, c, v)
                rec = al['v'][c-1][v-1] if v <= len(al['v'][c-1]) else {}
                lp = rec.get('la', []); la2en = {}
                for q in range(0, len(lp), 2): la2en.setdefault(lp[q], set()).add(lp[q+1])
                en2k = {}
                for k, j in OEN.get(f'{b}:{c}:{v}', []): en2k.setdefault(j, set()).add(k)
                def feats_of(i, inter=inter, gdfa=gdfa, of=of, la2en=la2en, en2k=en2k):
                    ks = {k for ii, k in inter if ii == i} | {k for j in la2en.get(i, ()) for k in en2k.get(j, ())}
                    if not ks: ks = {k for ii, k in gdfa if ii == i}
                    return [of[k] for k in sorted(ks) if k < len(of)]
            else: feats_of = lambda i: []
            toks = analyse(text, feats_of)
            stat['tokens'] += len(toks); stat['checked'] += sum(1 for t in toks if t[4] == 1)
            new[a] = toks
        lx[str(c)] = new
    al['lx'] = lx
    json.dump(al, open(f, 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
    print(b, stat, file=sys.stderr) if b % 11 == 10 else None
json.dump(LXL, open(D + 'lxL.json', 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
print('done', stat, 'lemmas', len(LXL), file=sys.stderr)
