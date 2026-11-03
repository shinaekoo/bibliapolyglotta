"""Test: Latin word analysis from Whitaker's Words alone, choosing among its readings with the grammar of
the aligned Hebrew/Greek word (STEPBible TAHOT/TAGNT), instead of PROIEL. Gen 1 and John 1."""
import sys, json, re
sys.path.insert(0, '/tmp/claude-0/-home-claude/a31ef8c1-bdb9-5849-acf2-9254bcc7b397/scratchpad')
import full_lx as F
from words import ENTRIES, nz
R = '/home/claude/bibliapolyglotta/'
TX = R + 'text/'; D = R + 'web/data/'
W = re.compile(r'[^\W\d_]+')
LAIDX = F.LAIDX
SUB = json.load(open('/tmp/claude-0/orig_subs.json'))
LAORIG = json.load(open('/tmp/claude-0/fa_cache2/la-orig.json'))
# row index of each verse in the alignment cache (same order as align_original.py)
ROW = {}; n = 0
for b in range(66):
    en = json.load(open(f'{TX}en{b:02d}.json'))
    for c, vs in enumerate(en, 1):
        for v in range(1, len(vs) + 1): ROW[(b, c, v)] = n; n += 1
LXL = json.load(open(D + 'lxL.json'))
BYD = {}
for i, r in enumerate(LXL):
    if r: BYD.setdefault(r[0], i)

# ---- grammar of the original word -> the Latin features it suggests ----
GCASE = {'N': 'NOM', 'G': 'GEN', 'D': 'DAT', 'A': 'ACC', 'V': 'VOC'}
GTENSE = {'P': 'PRES', 'I': 'IMPF', 'F': 'FUT', 'A': 'PERF', 'R': 'PERF', 'L': 'PLUP', '2': 'PERF'}
GMOOD = {'I': 'IND', 'S': 'SUB', 'O': 'SUB', 'M': 'IMP', 'N': 'INF', 'P': 'PPL'}
def greek(m):
    """'N-NSM' / 'V-IAI-3S' / 'V-PAP-NSM' -> {pos, case, num, gen, tense, mood, voice, pers}"""
    p = m.split('-'); f = {'pos': p[0]}
    if p[0] == 'V' and len(p) > 1:
        t = p[1]
        tense, voice, mood = (t[0], t[1], t[2]) if len(t) >= 3 else (t[0], '', t[-1])
        if t[0] == '2': tense, voice, mood = t[1], t[2], t[3] if len(t) > 3 else ''
        f.update(tense=GTENSE.get(tense), mood=GMOOD.get(mood), voice='PASSIVE' if voice in 'P' and voice else 'ACTIVE' if voice == 'A' else None)
        if len(p) > 2:
            x = p[2]
            if x[0] in '123': f.update(pers=x[0], num=x[1:2])
            elif len(x) >= 3: f.update(case=GCASE.get(x[0]), num=x[1], gen=x[2])
    elif len(p) > 1 and len(p[1]) >= 2:
        x = p[1]
        if x[0] in GCASE: f.update(case=GCASE[x[0]], num=x[1] if len(x) > 1 else None, gen=x[2] if len(x) > 2 else None)
        elif x[0] in '123' and len(x) >= 4: f.update(pers=x[0], case=GCASE.get(x[1]), num=x[2], gen=x[3])
    return f
HTENSE = {'p': ('PERF', 'IND'), 'q': ('FUT', 'IND'), 'i': ('FUT', 'IND'), 'w': ('PERF', 'IND'), 'h': ('FUT', 'SUB'), 'j': ('PRES', 'SUB'),
          'v': (None, 'IMP'), 'a': (None, 'INF'), 'c': (None, 'INF'), 'r': ('PRES', 'PPL'), 's': ('PERF', 'PPL')}
def hebrew_(seg):
    """'Ncfsa' / 'Vqp3ms' / 'Aampa' / 'Sp3ms' -> features (Hebrew has no case; number, gender, person, tense)"""
    s = seg.lstrip('HA') if seg[:1] == 'H' and len(seg) > 1 and seg[1].isupper() else seg
    f = {'pos': s[:1]}
    if s[:1] == 'V' and len(s) >= 3:
        t = HTENSE.get(s[2], (None, None)); f.update(tense=t[0], mood=t[1])
        rest = s[3:]
        if rest[:1] in '123': f.update(pers=rest[0], gen=rest[1:2].upper(), num=rest[2:3].upper())
        elif t[1] == 'PPL': f.update(gen=rest[:1].upper(), num=rest[1:2].upper())
    elif s[:1] in 'NAP' and len(s) >= 4:
        g = s[2:3] if s[:1] == 'N' else s[1:2] if s[:1] == 'A' else ''
        nm = s[3:4] if s[:1] == 'N' else s[2:3] if s[:1] == 'A' else ''
        f.update(gen=g.upper() if g in 'mfb' else None, num={'s': 'S', 'p': 'P', 'd': 'P'}.get(nm))
    return f

def hebrew(seg):
    """Hebrew number and tense do not carry over to Latin (שָׁמַיִם, אֱלֹהִים are plural; wayyiqtol of אמר is Latin ait):
    keep only the part of speech, and for verbs the mood (imperative, infinitive, participle) and person"""
    f = hebrew_(seg); f.pop('num', None); f.pop('gen', None)
    if f.get('mood') == 'IND': f.pop('mood'); f.pop('tense', None)
    else: f.pop('tense', None)
    if f.get('pos') not in ('V',): f = {'pos': f.get('pos')}
    return f
def orig_feats(b, c, v):
    """per original sub-token: features from STEPBible grammar"""
    al = AL[b]; ow = (al['ow'][c-1][v-1] or '').split(' ')
    subs = SUB.get(f'{b}:{c}:{v}', [])
    out = []; seen = {}
    for wi, strong in subs:
        g = ow[wi].split('|')[1] if wi < len(ow) and '|' in ow[wi] else ''
        k = seen.get(wi, 0); seen[wi] = k + 1
        if b < 39:
            segs = g.split('/')
            seg = segs[k] if k < len(segs) else segs[-1]
            out.append(hebrew(('H' if k == 0 else '') + seg if not seg.startswith('H') else seg))
        else: out.append(greek(g))
    return out
AL = {0: json.load(open(D + 'al00.json')), 42: json.load(open(D + 'al42.json'))}
NEWAL = {b: json.load(open(f'/tmp/claude-0/repl/al_new/al{b:02d}.json')) for b in (0, 42)}
OEN = json.load(open('/tmp/claude-0/repl/oe_new.json'))

def bonus(c, fs):
    """how well a Whitaker reading agrees with the aligned original words"""
    if not fs: return 0
    ip, g = c['ipos'], c['gram']; best = 0
    dpos = ENTRIES[c['idx']]['pos']
    for f in fs:
        s = 0; pos = f.get('pos')
        # the dictionary word's part of speech: a Greek/Hebrew noun is a Latin noun (mundus "world", not mundus "clean")
        if pos == 'N' and dpos == 'N': s += 1.5
        elif pos == 'N' and dpos in ('V', 'ADJ') and ip not in ('VPAR',): s -= 0.8
        elif pos in ('A',) and dpos == 'ADJ': s += 0.8
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
        elif ip in ('V',) and g:
            t, vo, m = g[0], g[1], g[2]
            if pos == 'V':
                s += 1
                if f.get('mood'):
                    if f['mood'] == m: s += 2
                    elif f['mood'] == 'PPL': s -= 1.5
                    elif m in ('SUB', 'IMP', 'INF') : s -= 1.5
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

def analyse(text, feats_of, use_orig):
    toks = W.findall(text); out = []; prev_prep = None; since = 9
    for i, w in enumerate(toks):
        lw = nz(w); prev = nz(toks[i-1]) if i else None; nxt = nz(toks[i+1]) if i + 1 < len(toks) else None
        cap = w[0].isupper() and i > 0; cs = F.cands(w)
        if lw == 'ut': cs = [c for c in cs if c['ipos'] in ('CONJ', 'ADV')] or cs        # never utor
        if not cs: out.append((w, 'PN' if w[0].isupper() else 'X', w if w[0].isupper() else None)); since += 1; continue
        pp = prev_prep if since <= 3 else None; nraw = toks[i+1] if i + 1 < len(toks) else None
        fs = feats_of(i) if use_orig else []
        best = max(cs, key=lambda c: F.score(c, lw, cap, prev, nxt, pp, nraw) + bonus(c, fs))
        code = F.gcode(best)
        if best['ipos'] == 'PREP':
            pc = F.prep_case(w, best, nraw); code = 'PREP.' + (pc or ''); prev_prep = (lw, pc); since = 0
        else:
            since += 1
            if best['ipos'] == 'V': prev_prep = None
        out.append((w, code, F.dict_form(ENTRIES[best['idx']]), best))
    return out

def coarse(code):
    p = [x for x in code.split('.') if not re.match(r'^k\d+$', x) and x != 'D']
    if p and p[0] in ('N', 'ADJ', 'PRON', 'NUM') : p = ['NOM'] + p[1:3]       # case, number (gender labels differ: X/C/M)
    if p and p[0] == 'VPAR': p = p[:3] + p[4:6]                              # case, number, tense, voice
    return '.'.join(p)
def run(b, c):
    la = json.load(open(f'{TX}la{LAIDX[b]:02d}.json'))[c-1]
    gold = AL[b]['lx'][str(c)]
    res = []
    for v, text in enumerate(la, 1):
        pairs = LAORIG[ROW[(b, c, v)]]
        inter, gdfa = pairs
        of = orig_feats(b, c, v)
        lp = NEWAL[b]['v'][c-1][v-1].get('la', []); la2en = {}
        for q in range(0, len(lp), 2): la2en.setdefault(lp[q], set()).add(lp[q+1])
        en2k = {}
        for k, j in OEN.get(f'{b}:{c}:{v}', []): en2k.setdefault(j, set()).add(k)
        def feats_of(i):
            ks = {k for ii, k in inter if ii == i}
            ks |= {k for j in la2en.get(i, ()) for k in en2k.get(j, ())}      # through the English (Strong's-free links)
            if not ks: ks = {k for ii, k in gdfa if ii == i}
            return [of[k] for k in sorted(ks) if k < len(of)]
        base = analyse(text, feats_of, False); new = analyse(text, feats_of, True)
        g = gold.get(f'v{v}', [])
        for j, (bt, nt) in enumerate(zip(base, new)):
            if nt[2] == 'a' : nt = (nt[0], nt[1], 'ab') + tuple(nt[3:])
            gt = g[j] if j < len(g) else None
            gl = ((LXL[gt[0]] or ['?'])[0], coarse(gt[3]), gt[4]) if gt else None
            if gl and gl[0] == 'a': gl = ('ab',) + gl[1:]
            res.append({'v': v, 'w': bt[0], 'gold': gl, 'base': (bt[2], coarse(bt[1])), 'new': (nt[2], coarse(nt[1])), 'orig': feats_of(j)})
    return res
if __name__ == '__main__':
    out = {}
    for name, (b, c) in {'gen1': (0, 1), 'jhn1': (42, 1)}.items():
        r = run(b, c); out[name] = r
        ok = lambda k, part: sum(1 for x in r if x['gold'] and x[k][part] == x['gold'][part]) / max(1, sum(1 for x in r if x['gold']))
        both = lambda k: sum(1 for x in r if x['gold'] and x[k][0] == x['gold'][0] and x[k][1] == x['gold'][1]) / max(1, sum(1 for x in r if x['gold']))
        src = sorted({x['gold'][2] for x in r if x['gold']})
        print(name, 'tokens', len(r), 'gold src', src,
              '| lemma base %.1f new %.1f' % (100 * ok('base', 0), 100 * ok('new', 0)),
              '| grammar base %.1f new %.1f' % (100 * ok('base', 1), 100 * ok('new', 1)),
              '| both base %.1f new %.1f' % (100 * both('base'), 100 * both('new')))
    json.dump(out, open('/tmp/claude-0/repl/latin_test.json', 'w'), ensure_ascii=False, default=str)
