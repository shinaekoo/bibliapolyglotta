"""Final export: per-book token files, lemma table, Lewis & Short shards."""
import sys, json, re, os, unicodedata
import xml.etree.ElementTree as ET
from collections import defaultdict
sys.path.insert(0, '/tmp/claude-0/-home-claude/a31ef8c1-bdb9-5849-acf2-9254bcc7b397/scratchpad')
import full_lx as F
from words import ENTRIES
from gen1_annot import LEMMA as G1LEMMA, MANUAL as G1MANUAL

OUT = '/home/claude/bible3/data/'
raw = json.load(open(F.OUT + 'nt_raw.json'))
books = raw['books']; LROWS = raw['lemmas']; LKEYS = [tuple(k) for k in raw['lemkeys']]
F.LEMROWS[:] = LROWS
LROWS = F.LEMROWS
for i, k in enumerate(LKEYS): F.LEM[k] = i

# ---- refresh dictionary forms (fixed generator) ----
for i, k in enumerate(LKEYS):
    if k[0] == 'E':
        LROWS[i]['d'] = F.dict_form(ENTRIES[k[1]])

# ---- Korean glosses ----
groups = json.load(open(F.OUT + 'groups.json'))
ko = {}
for fn in sorted(os.listdir(F.OUT)):
    if fn.startswith('ko_') and fn.endswith('.tsv'):
        for ln in open(F.OUT + fn, encoding='utf-8'):
            p = ln.rstrip('\n').split('\t')
            if len(p) >= 2 and p[0].isdigit(): ko[int(p[0])] = p[1]
for gi, (g, ids, n) in enumerate(groups):
    if gi in ko:
        for i in ids: LROWS[i]['ko'] = ko[gi]
print('glossed groups', len(ko), file=sys.stderr)

# ---- Genesis 1: hand-reviewed readings ----
man = json.load(open('/tmp/claude-0/lx_draft.json'))
text = json.load(open(F.DATA + 'la00.json'))[0]
W = re.compile(r'[^\W\d_]+')
g1 = books['0']['1']
for vi, row in enumerate(man['v'], 1):
    toks = W.findall(text[vi - 1])
    out = []
    for w, m in zip(toks, row):
        lem, split, pos, gram, note = m[:5]
        if len(m) >= 9:
            idx, code = m[6], m[7]
            lid = F.entry_lemma(idx)
            d, k, _, _, _, en = G1LEMMA[lem]
            LROWS[lid]['ko'] = k
            if en: LROWS[lid]['en'] = en
            sl = len(split[0]); el = len(split[1]) if len(split) > 1 else 0
            tok = [lid, sl, el, code, 2]
            if note: tok.append(note)
        else:   # manual entries (semetipso etc.)
            d, k, _, _, _, en = G1LEMMA[lem]
            lid = F.lemma_id(('G', lem), {'d': d, 'ko': k, 'en': en or '', 'pos': 'MAN', 'freq': 'X'})
            parts = m[5]
            tok = [lid, len(w), 0, 'MAN', 2, note or '', parts]
        out.append(tok)
    g1[f'v{vi}'] = out

# ---- Lewis & Short matching ----
def strip(s):
    s = unicodedata.normalize('NFD', s)
    s = ''.join(ch for ch in s if unicodedata.category(ch) != 'Mn')
    return s.lower().replace('j', 'i').replace('v', 'u').replace('-', '').replace('^', '')
LSF = '/tmp/claude-0/lx/CTS_XML_TEI/perseus/pdllex/lat/ls/lat.ls.perseus-eng2.xml'
lsidx = defaultdict(list)
JUNK = re.compile(r'\b(cf\.|et saep\.|id\.|ib\.|al\.|Müll\.|P\.|v\. h\. v\.|l\. l\.|v\. infra|v\. supra|saep\.|freq\.)')
MORPH = re.compile(r'^(gen|abl|dat|acc|voc|nom|inf|perf|pluperf|subj|praes|tempp|sync|imp|fin|init|v\. infra|\)|,|;|also gen|sing)\b', re.I)
def text_of(el, skip=('bibl', 'cit', 'quote', 'author')):
    out = []
    def walk(e):
        if e.tag in skip:
            if e.tail: out.append(e.tail)
            return
        if e.text: out.append(e.text)
        for c in e: walk(c)
        if e.tail: out.append(e.tail)
    if el.text: out.append(el.text)
    for c in el: walk(c)
    return re.sub(r'\s+', ' ', ''.join(out)).strip()
def clean(t):
    t = JUNK.sub('', t)
    t = re.sub(r'(\s*[:;,.]\s*){2,}', lambda m: m.group(0).strip()[:1] + ' ', t)
    t = re.sub(r'\s*—\s*', ' — ', t); t = re.sub(r'\s+', ' ', t).strip(' .;:,—')
    return t
for ev, el in ET.iterparse(LSF, events=('end',)):
    if el.tag != 'entryFree': continue
    key = el.get('key', '')
    orth = [o.text or '' for o in el.findall('orth')]
    pos = ' '.join((x.text or '') for x in el.findall('pos')) or ' '.join((x.text or '') for x in el.findall('gen'))
    itype = ' '.join((x.text or '') for x in el.findall('itype'))
    senses = []
    for s in el.findall('sense'):
        t = clean(text_of(s)[:240])
        if len(re.findall(r'[A-Za-z]{3,}', t)) < 3 or MORPH.match(t): continue
        senses.append(t[:170])
        if len(senses) >= 5: break
    if not senses:
        h = clean(text_of(el, skip=('sense', 'bibl', 'cit', 'quote', 'author')))
        if len(re.findall(r'[A-Za-z]{3,}', h)) >= 3: senses = [h[:170]]
    rec = [key, orth[0] if orth else key, pos.strip(), itype.strip(), senses]
    for o in set([re.sub(r'\d+$', '', key)] + orth[:1]):
        lsidx[strip(o)].append(rec)
    el.clear()
print('LS index', len(lsidx), file=sys.stderr)

POSOK = {'V': ('v.',), 'N': ('m.', 'f.', 'n.', 'comm.'), 'ADJ': ('adj', 'P. a.', 'num'), 'NUM': ('num', 'adj'), 'ADV': ('adv',),
         'PREP': ('prep',), 'CONJ': ('conj',), 'INTERJ': ('interj',), 'PRON': ('pron',)}
def ls_for(row):
    head = row['d'].split(',')[0].split(' (')[0].strip()
    cands = lsidx.get(strip(head), [])
    if not cands: return None
    ok = POSOK.get(row['pos'], ())
    for c in cands:
        if any(o in (c[2] + ' ' + c[3]) for o in ok) and c[4]: return c
    for c in cands:
        if c[4]: return c
    return None

# ---- write lemma table + LS shards ----
used = set()
for bk in books.values():
    for ch in bk.values():
        for toks in ch.values():
            for t in toks: used.add(t[0])
NSH = 64
shards = defaultdict(dict)
lemtab = []
nls = 0
for i, r in enumerate(LROWS):
    if i not in used:
        lemtab.append(None); continue
    en = re.sub(r'\s+', ' ', r.get('en', ''))
    if len(en) > 150: en = en[:150].rsplit(';', 1)[0] + ';…'
    lk = ''
    if r['pos'] not in ('PN', 'X', 'MAN'):
        c = ls_for(r)
        if c:
            shards[i % NSH][str(i)] = [c[0], c[1], c[2], c[4]]; lk = c[0]; nls += 1
    lemtab.append([r['d'], r.get('ko', ''), en, r['pos'], lk])
json.dump(lemtab, open(OUT + 'lxL.json', 'w'), ensure_ascii=False, separators=(',', ':'))
for s in range(NSH):
    json.dump(shards.get(s, {}), open(OUT + f'ls{s:02d}.json', 'w'), ensure_ascii=False, separators=(',', ':'))
print('lemmas used', len(used), 'with LS', nls, file=sys.stderr)

# ---- per-book token files ----
tot = 0
for bi in range(66):
    bk = books[str(bi)]
    json.dump({'c': bk}, open(OUT + f'lx{bi:02d}.json', 'w'), ensure_ascii=False, separators=(',', ':'))
    tot += os.path.getsize(OUT + f'lx{bi:02d}.json')
print('token files MB', round(tot / 1e6, 1), file=sys.stderr)
