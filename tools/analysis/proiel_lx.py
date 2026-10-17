"""Overlay PROIEL (hand-annotated Vulgate NT) context readings onto the automatic analysis."""
import sys, json, re, difflib
from collections import defaultdict
import xml.etree.ElementTree as ET
sys.path.insert(0, '/tmp/claude-0/-home-claude/a31ef8c1-bdb9-5849-acf2-9254bcc7b397/scratchpad')
import full_lx as F
from words import ENTRIES, nz

raw = json.load(open(F.OUT + 'auto_raw.json'))
books = {int(k): v for k, v in raw['books'].items()}
F.LEMROWS[:] = raw['lemmas']
for i, k in enumerate(raw['lemkeys']):
    F.LEM[tuple(k)] = i

CODE = {'MATT': 39, 'MARK': 40, 'LUKE': 41, 'JOHN': 42, 'ACTS': 43, 'ROM': 44, '1COR': 45, '2COR': 46, 'GAL': 47, 'EPH': 48,
        'PHIL': 49, 'COL': 50, '1THESS': 51, '2THESS': 52, '1TIM': 53, '2TIM': 54, 'TIT': 55, 'PHILEM': 56, 'HEB': 57,
        'JAS': 58, '1PET': 59, '2PET': 60, '1JOHN': 61, '2JOHN': 62, '3JOHN': 63, 'JUDE': 64, 'REV': 65}
CASE = dict(n='NOM', a='ACC', g='GEN', d='DAT', b='ABL', v='VOC', l='LOC', i='ABL')
NUM = dict(s='S', p='P')
GEN = dict(m='M', f='F', n='N')
TENSE = dict(p='PRES', i='IMPF', r='PERF', l='PLUP', t='FUTP', f='FUT')
VOICE = dict(a='ACTIVE', p='PASSIVE')
DEG = dict(p='POS', c='COMP', s='SUPER')

def feats(pos, m):
    m = (m + '----------')[:10]
    f = {'pers': m[0] if m[0] in '123' else None, 'num': NUM.get(m[1]), 'tense': TENSE.get(m[2]), 'mood': m[3],
         'voice': VOICE.get(m[4]), 'gen': GEN.get(m[5]), 'case': CASE.get(m[6]), 'deg': DEG.get(m[7])}
    if pos == 'V-':
        if m[3] in ('p',): ip = 'VPAR'
        elif m[3] in ('d', 'g'): ip = 'VPAR'
        elif m[3] == 'u': ip = 'SUPINE'
        else: ip = 'V'
    elif pos in ('Nb', 'Ne'): ip = 'N'
    elif pos == 'A-': ip = 'ADJ'
    elif pos in ('Ps', 'Pt'): ip = 'ADJ'
    elif pos.startswith('P'): ip = 'PRON'
    elif pos in ('Ma', 'Mo'): ip = 'NUM'
    elif pos == 'R-': ip = 'PREP'
    elif pos in ('C-', 'G-'): ip = 'CONJ'
    elif pos.startswith('D'): ip = 'ADV'
    elif pos == 'I-': ip = 'INTERJ'
    else: ip = 'X'
    f['ip'] = ip
    return f

IPOK = {'VPAR': {'VPAR'}, 'SUPINE': {'SUPINE'}, 'V': {'V'}, 'N': {'N'}, 'ADJ': {'ADJ', 'PRON', 'NUM'}, 'PRON': {'PRON', 'ADJ'},
        'NUM': {'NUM', 'ADJ'}, 'PREP': {'PREP'}, 'CONJ': {'CONJ', 'ADV'}, 'ADV': {'ADV', 'CONJ'}, 'INTERJ': {'INTERJ'}}

def cand_feats(c):
    ip, g = c['ipos'], c['gram']
    d = {'ip': ip}
    if ip in ('N', 'ADJ', 'PRON', 'NUM', 'SUPINE'):
        d.update(case=g[0] if g else None, num=g[1] if len(g) > 1 else None, gen=g[2] if len(g) > 2 else None)
        if ip == 'ADJ' and len(g) > 3: d['deg'] = g[3]
    elif ip == 'V':
        d.update(tense=g[0], voice=g[1], moodw=g[2], pers=g[3] if g[3] != '0' else None, num=g[4] if g[4] in 'SP' else None)
    elif ip == 'VPAR':
        d.update(case=g[0], num=g[1], gen=g[2], tense=g[3], voice=g[4])
    elif ip == 'PREP':
        d['case'] = g[0] if g else None
    return d

MOODW = dict(i='IND', s='SUB', m='IMP', n='INF')
def head_norm(s):
    return re.sub(r'[^a-z]', '', nz(s.split(',')[0].split(' ')[0]))

def pick(word, f, lemma):
    cs = F.cands(word)
    if not cs: return None, -99
    ln = head_norm(lemma.split('#')[0])
    best, bs = None, -99
    for c in cs:
        e = ENTRIES[c['idx']]
        s = 0
        if head_norm(F.dict_form(e)) == ln: s += 6
        elif ln and head_norm(F.dict_form(e))[:max(3, len(ln) - 2)] == ln[:max(3, len(ln) - 2)]: s += 2
        if c['ipos'] in IPOK.get(f['ip'], set()): s += 3
        cf = cand_feats(c)
        for k in ('case', 'num', 'tense', 'voice', 'pers'):
            if f.get(k) and cf.get(k):
                if f[k] == cf[k] or (k == 'num' and cf[k] == 'X'): s += 1
                else: s -= 1
        if f.get('gen') and cf.get('gen') and cf['gen'] not in ('X', 'C'):
            s += 0.5 if f['gen'] == cf['gen'] else -0.5
        if f['ip'] == 'V' and cf.get('moodw'):
            s += 1 if MOODW.get(f['mood']) == cf['moodw'] else -1
        s += F.FREQ.get(e['freq'], 1) * 0.05
        if s > bs: best, bs = c, s
    return best, bs

def code_from(f, c):
    """Gram code from PROIEL features (keeps the Whitaker key / deponent flag where available)."""
    ip = f['ip']
    key = f"k{c.get('key', 0)}" if c else 'k0'
    dep = ['D'] if (c and 'DEP' in c['info']) else []
    if ip == 'V':
        if f['mood'] == 'n':
            return '.'.join(['V', f['tense'] or 'PRES', f['voice'] or 'ACTIVE', 'INF', '0', 'X', key] + dep)
        return '.'.join(['V', f['tense'] or 'PRES', f['voice'] or 'ACTIVE', MOODW.get(f['mood'], 'IND'), f['pers'] or '3', f['num'] or 'S', key] + dep)
    if ip == 'VPAR':
        if f['mood'] in ('d', 'g'):
            return '.'.join(['VPAR', f['case'] or 'ACC', f['num'] or 'S', f['gen'] or 'N', 'FUT', 'PASSIVE', 'PPL', key] + dep)
        return '.'.join(['VPAR', f['case'] or 'NOM', f['num'] or 'S', f['gen'] or 'X', f['tense'] or 'PRES', f['voice'] or 'ACTIVE', 'PPL', key] + dep)
    if ip == 'SUPINE':
        return '.'.join(['SUPINE', f['case'] or 'ACC', 'S', 'N', key])
    if ip in ('N', 'PRON'):
        return '.'.join([ip, f['case'] or 'X', f['num'] or 'X', f['gen'] or 'X'])
    if ip == 'ADJ':
        return '.'.join(['ADJ', f['case'] or 'X', f['num'] or 'X', f['gen'] or 'X', f['deg'] or 'POS'])
    if ip == 'NUM':
        return '.'.join(['NUM', f['case'] or 'X', f['num'] or 'X', f['gen'] or 'X', 'CARD'])
    if ip == 'PREP':
        return 'PREP.' + (c['gram'][0] if c and c.get('gram') else '')
    return ip if ip in ('CONJ', 'ADV', 'INTERJ') else 'X'

# ---- read PROIEL tokens grouped by verse ----
verses = defaultdict(list)
for ev, el in ET.iterparse('/tmp/claude-0/pt/latin-nt.xml', events=('end',)):
    if el.tag == 'token' and el.get('form'):
        cp = el.get('citation-part', '')
        m = re.match(r'(\S+) (\d+)\.(\d+)', cp)
        if m and m.group(1) in CODE:
            verses[(CODE[m.group(1)], int(m.group(2)), int(m.group(3)))].append(
                (el.get('form'), el.get('lemma', ''), el.get('part-of-speech', ''), el.get('morphology', '')))
    if el.tag in ('token',):
        el.clear()
print('proiel verses', len(verses), file=sys.stderr)

W = re.compile(r'[^\W\d_]+')
def n2(s): return re.sub(r'[^a-z]', '', nz(s))
changed = matched = total = 0
for (bi, c, v), ptoks in verses.items():
    ch = books.get(bi, {}).get(str(c))
    if not ch or f'v{v}' not in ch: continue
    rows = dict(F.latin_rows(bi, c))
    text = rows.get(f'v{v}')
    if not text: continue
    toks = W.findall(text)
    our = ch[f'v{v}']
    if len(our) != len(toks): continue
    pforms = [n2(p[0]) for p in ptoks]
    sm = difflib.SequenceMatcher(a=[n2(t) for t in toks], b=pforms, autojunk=False)
    pairs_ij = [(blk.a + k, blk.b + k) for blk in sm.get_matching_blocks() for k in range(blk.size)]
    ui = {i for i, _ in pairs_ij}; uj = {j for _, j in pairs_ij}
    for i in range(len(toks)):          # same word in a different word order
        if i in ui: continue
        for j in range(len(pforms)):
            if j not in uj and pforms[j] == n2(toks[i]):
                pairs_ij.append((i, j)); ui.add(i); uj.add(j); break
    for i, j in pairs_ij:
        if True:
            total += 1
            form, lemma, pos, morph = ptoks[j]
            f = feats(pos, morph)
            w = toks[i]
            c, s = pick(w, f, lemma)
            ln = head_norm(lemma.split('#')[0])
            if c is not None and head_norm(F.dict_form(ENTRIES[c['idx']])) == ln:
                lid = F.entry_lemma(c['idx'])
                stem, end = len(c['stem']), len(c['ending'])
            elif c is not None and s >= 5:
                lid = F.entry_lemma(c['idx'])
                stem, end = len(c['stem']), len(c['ending'])
            else:
                lid = F.lemma_id(('P', lemma), {'d': lemma.split('#')[0], 'ko': '', 'en': '', 'pos': 'PN' if pos == 'Ne' else f['ip'], 'freq': 'X'})
                stem, end = (len(c['stem']), len(c['ending'])) if c is not None else (len(w), 0)
            code = 'PN' if (pos == 'Ne' and c is None) else code_from(f, c)
            new = [lid, stem, end, code, 1]
            if our[i][:4] != new[:4]: changed += 1
            our[i] = new
            matched += 1
print('proiel matched', matched, 'changed', changed, file=sys.stderr)
json.dump({'books': {str(k): v for k, v in books.items()}, 'lemmas': F.LEMROWS, 'lemkeys': [list(k) for k in F.LEM]},
          open(F.OUT + 'nt_raw.json', 'w'), ensure_ascii=False)
print('written', file=sys.stderr)
