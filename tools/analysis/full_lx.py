"""Whole-Bible Latin word analysis -> compact per-book data for the viewer.

Output (in OUT dir):
  lx{bi:02d}.json : {"c": {chap: {anchor: [token, ...]}}}
        token = [lemma_id, stem_len, end_len, gram_code, src, note?]
        (stem/end lengths count characters of the surface word; the rest is an enclitic)
        src: 0 automatic, 1 PROIEL (context, NT), 2 reviewed by hand (Gen 1)
  lemmas.json   : {lemma_id: [dict_form, korean, english, ls_key, pos]}
"""
import sys, json, re, unicodedata
from collections import Counter, defaultdict
sys.path.insert(0, '/tmp/claude-0/-home-claude/a31ef8c1-bdb9-5849-acf2-9254bcc7b397/scratchpad')
import words
from words import ENTRIES, nz

DATA = '/home/claude/bible3/data/'
OUT = '/tmp/claude-0/lxout/'
W = re.compile(r'[^\W\d_]+')

# ---------- book table (same order as the page) ----------
LAIDX = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,18,19,20,21,22,23,26,27,28,30,31,32,33,34,35,36,37,38,39,40,41,42,43,46,47,48,49,50,51,52,53,54,55,56,57,58,59,60,61,62,63,64,65,66,67,68,69,70,71,72]
PS, DAN, NT0 = 18, 26, 39

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

_cache = {}
def load(pre, i):
    k = (pre, i)
    if k not in _cache:
        _cache[k] = json.load(open(f'{DATA}{pre}{i:02d}.json'))
    return _cache[k]

def latin_rows(bi, c):
    """Mirror of the page's laneOf/rowsOf for Latin: yields (anchor, text)."""
    la = load('la', LAIDX[bi])
    if bi == PS:
        arr = []
        for ch, a, z in ps_map(c):
            vs = la[ch-1] if ch-1 < len(la) else []
            arr += vs[a-1:min(z, len(vs))]
        ko = load('ko', bi); en = load('en', bi)
        ref = len(ko[c-1]) if c-1 < len(ko) else 0
        ref = ref or (len(en[c-1]) if c-1 < len(en) else 0)
        s = max(0, min(3, len(arr) - ref)) if ref else 0
    else:
        arr = la[c-1] if c-1 < len(la) else []
        s = 0
    title = ' '.join(arr[:s]); main = arr[s:]; extra = None
    if bi == DAN and c == 3 and len(arr) > 90:
        extra = arr[23:90]; main = arr[:23] + arr[90:]
    if title: yield 't', title
    for i, t in enumerate(main):
        if t: yield f'v{i+1}', t
        if extra and i == 22:
            for j, x in enumerate(extra):
                if x: yield f'L{24+j}', x

# ---------- dictionary form from a Whitaker entry ----------
DICT_FIX = {('vol', 'vel'): 'volo, velle, volui', ('nol', 'nol'): 'nolo, nolle, nolui', ('mal', 'mal'): 'malo, malle, malui',
            ('poss', 'pot'): 'possum, posse, potui', ('fi', 'f'): 'fio, fieri, factus sum', ('a', 'a'): 'aio'}
PRON_STEM = {('PRON', 'i'): 'is, ea, id', ('PRON', 'qu'): 'qui, quae, quod', ('PRON', 'h'): 'hic, haec, hoc', ('PRON', 'ill'): 'ille, illa, illud',
             ('PRON', 'ips'): 'ipse, ipsa, ipsum', ('PRON', 'ist'): 'iste, ista, istud', ('PRON', 'v'): 'vos (너희)', ('PRON', 'n'): 'nos (우리)',
             ('PRON', 'zzz'): 'sui, sibi, se', ('PRON', 'ego'): 'ego, mei', ('PRON', 'tu'): 'tu, tui', ('NUM', 'un'): 'unus, una, unum',
             ('NUM', 'du'): 'duo, duae, duo', ('NUM', 'tr'): 'tres, tria', ('ADJ', 'ali'): 'alius, alia, aliud', ('PRON', 'id'): 'idem, eadem, idem',
             ('PRON', 'quis'): 'quis, quid', ('PRON', 'qui'): 'qui, quae, quod', ('ADJ', 'alter'): 'alter, altera, alterum', ('ADJ', 'null'): 'nullus, nulla, nullum',
             ('ADJ', 'tot'): 'totus, tota, totum', ('ADJ', 'sol'): 'solus, sola, solum', ('ADJ', 'ull'): 'ullus, ulla, ullum', ('ADJ', 'neutr'): 'neuter, neutra, neutrum'}
def dict_form(e):
    s = e['stems']; pos = e['pos']; info = e['info']
    k = (pos if pos != 'PACK' else 'PRON', s[0])
    if k in PRON_STEM: return PRON_STEM[k]
    if pos == 'V' and tuple(s[:2]) in DICT_FIX: return DICT_FIX[tuple(s[:2])]
    if pos == 'V' and s[0] == 's' and s[1] == '' : return 'sum, esse, fui, futurus'
    return _dict_form(e)

def _dict_form(e):
    s = e['stems']; pos = e['pos']; info = e['info']
    s1, s2, s3, s4 = (s + ['', '', '', ''])[:4]
    try: wh, var = int(info[0]), int(info[1])
    except (ValueError, IndexError): wh, var = None, None
    if pos == 'V':
        dep = 'DEP' in info or 'SEMIDEP' in info
        if wh == 1:
            return f"{s1}or, {s2}ari, {s4}us sum" if dep else f"{s1}o, {s2}are, {s3}i, {s4}um"
        if wh == 2:
            return f"{s1}eor, {s2}eri, {s4}us sum" if dep else f"{s1}eo, {s2}ere, {s3}i, {s4}um"
        if wh == 3 and var == 4:
            return f"{s1}or, {s2}iri, {s4}us sum" if dep else f"{s1}o, {s2}ire, {s3}i, {s4}um"
        if wh == 3:
            if dep: return f"{s1}or, {s2}i, {s4}us sum"
            return f"{s1}o, {s2}ere, {s3}i, {s4}um"
        if wh == 4:
            return f"{s1}or, {s2}iri, {s4}us sum" if dep else f"{s1}o, {s2}ire, {s3}i, {s4}um"
        if wh == 5:
            return f"{s1}um, {s2}esse, {s3}i"
        if wh == 6 and var == 1:
            return f"{s1}o, {s2}re, {s3}vi, {s4}um"
        if wh == 6 and var == 2:
            return f"{s1}o, {s2}re, {s3}i, {s4}um"
        return ', '.join(x for x in (s1, s2, s3, s4) if x and x != 'zzz')
    if pos == 'N':
        g = {'M': 'm.', 'F': 'f.', 'N': 'n.', 'C': 'm./f.'}.get(info[2] if len(info) > 2 else '', '')
        if wh == 1: return f"{s1}a, {s2}ae {g}"
        if wh == 2:
            if var == 1: return f"{s1}us, {s2}i {g}"
            if var == 2: return f"{s1}um, {s2}i {g}"
            if var == 3: return f"{s1}, {s2}i {g}"
            if var == 4: return f"{s1}us, {s2}i {g}" if g != 'n.' else f"{s1}um, {s2}i {g}"
            return f"{s1}us, {s2}i {g}"
        if wh == 3: return f"{s1}, {s2}is {g}"
        if wh == 4: return f"{s1}us, {s2}us {g}" if var != 2 else f"{s1}u, {s2}us {g}"
        if wh == 5: return f"{s1}es, {s2}ei {g}"
        return f"{s1} {g}".strip()
    if pos == 'ADJ':
        if wh == 1 and var == 1: return f"{s1}us, {s2}a, {s2}um"
        if wh == 1 and var == 2: return f"{s1}, {s2}a, {s2}um"
        if wh == 1 and var == 3: return f"{s1}us, {s2}a, {s2}um"
        if wh == 3 and var == 1: return f"{s1}, {s2}is"
        if wh == 3 and var == 2: return f"{s1}is, {s2}e"
        if wh == 3 and var == 3: return f"{s1}, {s2}is, {s2}e"
        return s1
    return s1 or s2

PRON_DICT = {'is': 'is, ea, id', 'hic': 'hic, haec, hoc', 'ille': 'ille, illa, illud', 'qui': 'qui, quae, quod',
             'quis': 'quis, quid', 'ipse': 'ipse, ipsa, ipsum', 'iste': 'iste, ista, istud', 'idem': 'idem, eadem, idem',
             'ego': 'ego, mei', 'tu': 'tu, tui', 'nos': 'nos, nostri', 'vos': 'vos, vestri', 'se': 'sui, sibi, se'}

# ---------- lemma registry ----------
LEM = {}        # key -> id
LEMROWS = []    # id -> dict
def lemma_id(key, row):
    if key not in LEM:
        LEM[key] = len(LEMROWS); LEMROWS.append(row)
    return LEM[key]

def entry_lemma(idx):
    e = ENTRIES[idx]
    d = dict_form(e)
    if e['pos'] in ('PRON', 'PACK'):
        m = e['mean'].lower()
        for k, v in PRON_DICT.items():
            pass
    return lemma_id(('E', idx), {'d': d, 'ko': '', 'en': e['mean'], 'pos': e['pos'], 'freq': e['freq']})

# ---------- gram code ----------
def gcode(c):
    ip = c['ipos']; g = list(c['gram'])
    dep = 'D' if ('DEP' in c['info']) else ''
    if ip in ('V', 'VPAR', 'SUPINE'):
        return '.'.join([ip] + g + [f"k{c.get('key', 0)}"] + ([dep] if dep else []))
    if ip == 'PREP':
        return 'PREP.' + (g[0] if g else '')
    if ip in ('CONJ', 'INTERJ'):
        return ip
    if ip == 'ADV':
        return 'ADV'
    return '.'.join([ip] + g)

# ---------- automatic scoring ----------
FREQ = {'A': 5, 'B': 4, 'C': 3, 'D': 2, 'E': 1, 'F': 0, 'X': 2}
IFREQ = {'A': 2, 'B': 1.5, 'C': 1, 'D': 0.5}
SUBJ_TRIG = {'ut', 'ne', 'cum', 'utinam', 'si', 'nisi', 'quatenus', 'donec', 'priusquam', 'antequam', 'quasi', 'tamquam', 'quin', 'licet'}
ABL_PREP = {'a', 'ab', 'abs', 'e', 'ex', 'de', 'cum', 'sine', 'pro', 'prae', 'coram', 'absque', 'tenus'}
ACC_PREP = {'ad', 'per', 'ante', 'post', 'propter', 'inter', 'contra', 'apud', 'circa', 'circum', 'juxta', 'iuxta', 'secundum',
            'trans', 'ultra', 'usque', 'adversus', 'adversum', 'erga', 'extra', 'intra', 'infra', 'praeter', 'ob', 'versus', 'citra', 'penes'}
BOTH_PREP = {'in', 'sub', 'super'}
BAD = [({'est', 'esse', 'esset', 'essent', 'estis', 'es', 'este', 'esto', 'essem', 'essemus', 'essetis', 'esses', 'edit', 'edunt'}, 'eat/consume'),
       (None, 'kind of beer'), (None, 'venom (sg.)'), (None, 'chisel; engraving tool'), (None, 'car-light')]

def bad(c, w):
    for forms, sub in BAD:
        if (forms is None or w in forms) and sub in c['mean']:
            return True
    return False

def score(c, w, cap, prev, nxt, prev_prep, nxt_raw=None):
    if c['kind'] == 'unique':
        return -99
    e = ENTRIES[c['idx']]
    s = FREQ.get(e['freq'], 1) + IFREQ.get(c.get('ifreq', 'C'), 0.5)
    if e['age'] in ('G', 'H'): s -= 2
    if e['age'] == 'E': s += 0.5          # ecclesiastical Latin
    ip, g = c['ipos'], c['gram']
    info = c['info']
    kind = info[3] if (c['dpos'] == 'N' and len(info) > 3) else ''
    if c['dpos'] == 'N' and kind == 'N' and not cap: s -= 3
    if cap and c['dpos'] == 'N' and kind in ('N', 'L'): s += 1
    if ip in ('N', 'ADJ', 'PRON', 'NUM', 'VPAR') and g:
        cs = g[0]
        if cs in ('VOC', 'LOC'): s -= 2.5
        if prev_prep:
            p, pcs = prev_prep
            if pcs == cs: s += 3
            elif cs in ('ACC', 'ABL'): s -= 1.5
    if ip == 'V':
        t, v, m = g[0], g[1], g[2]
        if m == 'SUB':
            s += 2 if prev in SUBJ_TRIG else -1
        if m == 'IMP': s -= 0.8
        if m == 'INF': s -= 0.2
        if len(g) > 3 and g[3] == '3': s += 0.3
    if ip == 'VPAR' and len(g) > 3 and g[3] == 'PERF' and nxt in SUM_FORMS:
        s += 2.5
        if g[0] == 'NOM': s += 1.5
        if 'happen, come about' in c['mean']: s += 1.2
    if ip == 'PREP' and nxt_raw is not None:
        nc = cases_of(nxt_raw)
        gov = 'ACC' if w in ACC_PREP else 'ABL' if w in ABL_PREP else (g[0] if g else None)
        if w in BOTH_PREP and nc & {'ACC', 'ABL'}: s += 2.5
        elif gov in nc: s += 2.5
    if ip == 'CONJ' and w == 'quod' and prev in PERCEIVE: s += 4
    if w == 'qui' and ip == 'ADV': s -= 3
    if ip == 'N' and g and len(g) > 1 and g[1] == 'S' and '(pl.)' in c['mean'][:40]: s -= 2
    if c['dpos'] == 'ADJ': s += 0.6
    if ip == 'N' and g and g[0] == 'NOM' and g[1] == 'P' and w.endswith(('ae', 'æ')): s += 0.3
    if ip in ('CONJ', 'ADV', 'PREP', 'INTERJ'): s += 0.5
    return s

def prep_case(word, c, nraw):
    """For a preposition token, which case does it govern here?"""
    lw = nz(word)
    if lw in ACC_PREP: return 'ACC'
    if lw in ABL_PREP: return 'ABL'
    if lw in BOTH_PREP and nraw:
        nc = cases_of(nraw)
        if 'ACC' in nc and 'ABL' not in nc: return 'ACC'
        if 'ABL' in nc and 'ACC' not in nc: return 'ABL'
        return 'ACC' if lw == 'super' else 'ABL'
    return c['gram'][0] if c.get('gram') else None

# ---------- analysis cache per surface form ----------
ACACHE = {}
def cands(w):
    if w not in ACACHE:
        allc = [c for c in words.analyze(w) if c['kind'] != 'unique']
        good = [c for c in allc if not bad(c, nz(w))]
        ACACHE[w] = good or allc
    return ACACHE[w]
CASES_OF = {}
def cases_of(w):
    if w not in CASES_OF:
        CASES_OF[w] = {c['gram'][0] for c in cands(w) if c['ipos'] in ('N', 'ADJ', 'PRON', 'NUM', 'VPAR') and c['gram']}
    return CASES_OF[w]
SUM_FORMS = {'est', 'sunt', 'erat', 'erant', 'fuit', 'fuerunt', 'sit', 'esset', 'essent', 'es', 'sum', 'sumus', 'estis', 'erit', 'erunt', 'fuerat', 'fuerant', 'sint', 'esse'}
PERCEIVE = {'vidit', 'viderunt', 'videns', 'videntes', 'scio', 'scit', 'scitis', 'sciens', 'scientes', 'scimus', 'audistis', 'audivit', 'audierunt',
            'cognovit', 'cognovi', 'cognoscens', 'credo', 'credimus', 'creditis', 'dico', 'dicit', 'dixit', 'dicens', 'nuntiatum', 'putatis', 'ait', 'nescitis', 'videte', 'videtis'}

def analyse_row(text):
    toks = W.findall(text)
    out = []
    prev_prep = None; since = 9
    for i, w in enumerate(toks):
        lw = nz(w)
        prev = nz(toks[i-1]) if i else None
        nxt = nz(toks[i+1]) if i + 1 < len(toks) else None
        cap = w[0].isupper() and i > 0
        cs = cands(w)
        if not cs:
            # unknown word: most are proper names
            lid = lemma_id(('U', w if cap or w[0].isupper() else lw), {'d': w, 'ko': '', 'en': '', 'pos': 'PN' if w[0].isupper() else 'X', 'freq': 'X'})
            out.append([lid, len(w), 0, 'PN' if w[0].isupper() else 'X', 0])
            since += 1
            continue
        pp = prev_prep if since <= 3 else None
        nraw = toks[i+1] if i + 1 < len(toks) else None
        best = max(cs, key=lambda c: score(c, lw, cap, prev, nxt, pp, nraw))
        stem = best['stem']; end = best['ending']
        lid = entry_lemma(best['idx'])
        code = gcode(best)
        if best['ipos'] == 'PREP':
            pc = prep_case(w, best, nraw)
            code = 'PREP.' + (pc or '')
            prev_prep = (lw, pc); since = 0
        else:
            since += 1
            if best['ipos'] == 'V': prev_prep = None
        out.append([lid, len(stem), len(end), code, 0])
    return out

if __name__ == '__main__':
    import os, time
    os.makedirs(OUT, exist_ok=True)
    t0 = time.time()
    total = 0; unknown = 0
    books = {}
    for bi in range(66):
        ko = load('ko', bi)
        bk = {}
        for c in range(1, len(ko) + 1):
            ch = {}
            for a, t in latin_rows(bi, c):
                toks = analyse_row(t)
                total += len(toks); unknown += sum(1 for x in toks if x[3] in ('PN', 'X'))
                ch[a] = toks
            bk[str(c)] = ch
        books[bi] = bk
        print(bi, round(time.time() - t0), 's', total, 'tokens', len(LEMROWS), 'lemmas', len(ACACHE), 'forms', file=sys.stderr)
    json.dump({'books': books, 'lemmas': LEMROWS, 'lemkeys': [list(k) if isinstance(k, tuple) else k for k in LEM]}, open(OUT + 'auto_raw.json', 'w'), ensure_ascii=False)
    print('done', total, unknown, file=sys.stderr)
