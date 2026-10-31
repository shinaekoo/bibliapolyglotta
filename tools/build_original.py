"""Hebrew OT and Greek NT (STEPBible TAHOT/TAGNT, CC BY 4.0) -> the app's alignment files.

Adds to web/data/al{book}.json:
  "or": [chapter][verse] original-language text, in KJV verse numbering
        (Hebrew: Leningrad text with qere readings, vowels kept, cantillation removed;
         Greek: the words of the Nestle-Aland text)
  "ow": [chapter][verse] "dStrong|grammar|transliteration" per original word, space separated
  "og": {dStrong: [dictionary form, transliteration, gloss, short definition]} for the book's words
  "v"[c][v]["or"]: [original word, KJV word, ...] links, made by matching Strong's numbers.

usage: python3 tools/build_original.py STEP_DIR KJV_DIR
  STEP_DIR holds TAHOT_*.txt, TAGNT_*.txt, TBESH.txt, TBESG.txt (from github.com/STEPBible/STEPBible-Data)
  KJV_DIR is kaiserlik/kjv (Strong's-tagged KJV)
"""
import json, os, re, sys, glob, difflib, unicodedata
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
D = os.path.join(HERE, '..', 'web', 'data') + '/'
STEP, KJV = sys.argv[1], sys.argv[2]
SC = 'Gen Exo Lev Num Deu Jos Jdg Rut 1Sa 2Sa 1Ki 2Ki 1Ch 2Ch Ezr Neh Est Job Psa Pro Ecc Sng Isa Jer Lam Ezk Dan Hos Jol Amo Oba Jon Mic Nam Hab Zep Hag Zec Mal Mat Mrk Luk Jhn Act Rom 1Co 2Co Gal Eph Php Col 1Th 2Th 1Ti 2Ti Tit Phm Heb Jas 1Pe 2Pe 1Jn 2Jn 3Jn Jud Rev'.split()
KC = 'Gen Exo Lev Num Deu Jos Jdg Rth 1Sa 2Sa 1Ki 2Ki 1Ch 2Ch Ezr Neh Est Job Psa Pro Ecc Sng Isa Jer Lam Eze Dan Hos Joe Amo Oba Jon Mic Nah Hab Zep Hag Zec Mal Mat Mar Luk Jhn Act Rom 1Co 2Co Gal Eph Phl Col 1Th 2Th 1Ti 2Ti Tit Phm Heb Jas 1Pe 2Pe 1Jo 2Jo 3Jo Jde Rev'.split()
BI = {c: i for i, c in enumerate(SC)}
W = re.compile(r'[^\W\d_]+')

def tokens(s):
    """the app's word split: runs of letters and combining marks (JS /[\\p{L}\\p{M}]+/u)"""
    out, cur = [], ''
    for ch in s:
        if unicodedata.category(ch)[0] in 'LM': cur += ch
        elif cur: out.append(cur); cur = ''
    if cur: out.append(cur)
    return out

def snum(s):
    m = re.match(r'([HG])0*(\d+)', s)
    return f'{m.group(1)}{m.group(2)}' if m else None
CANT = re.compile('[֑-ֽ֯]')     # cantillation and meteg

# ---- read the tagged texts ----
REF = re.compile(r'^([1-3]?[A-Z][a-z]{1,2})\.(\d+)\.(\d+)(?:\(([\d.]+)\))?(?:\[([\d.]+)\])?(?:\{([\d.]+)\})?#(\d+)=([^\t]+)\t')
verses = defaultdict(list)          # (b, c, v) -> [(text, dStrong, grammar, translit)]
def add(bk, c, v, *w):
    if bk in BI: verses[(BI[bk], int(c), int(v))].append(w)
for f in sorted(glob.glob(os.path.join(STEP, 'TAHOT_*.txt'))):
    for line in open(f, encoding='utf-8-sig'):
        m = REF.match(line)
        if not m or m.group(8)[0] not in 'LQ': continue
        x = line.rstrip('\n').split('\t')
        heb = CANT.sub('', re.sub(r'\\ \\[\u05e4\u05e1]\s*$', '', x[1]).replace('/', '').replace('\\', ''))   # drop petuha/setuma paragraph marks
        main = re.search(r'\{(H\d+[A-Z]?)\}', x[4]) or re.search(r'(H(?!9\d{3})\d+[A-Z]?)', x[4])
        c, v = int(m.group(2)), int(m.group(3))
        if v == 0: v = 1                      # psalm titles belong to verse 1 in the KJV and 개역
        add(m.group(1), c, v, heb, main.group(1) if main else '', x[5], x[2])
grk, grk_tr = defaultdict(list), defaultdict(list)
for f in sorted(glob.glob(os.path.join(STEP, 'TAGNT_*.txt'))):
    for line in open(f, encoding='utf-8-sig'):
        m = REF.match(line)
        if not m: continue
        na = bool(re.search('[Nn]', m.group(8)))
        if not na and not re.search('[Kk]', m.group(8)): continue
        x = line.rstrip('\n').split('\t')
        g, tr = (re.match(r'(.*?)\s*\((.*)\)\s*$', x[1]) or re.match(r'(.*)()', x[1])).groups()
        ds, gram = (x[3].split('=') + [''])[:2]
        c, v = m.group(2), m.group(3)
        if m.group(5): c, v = m.group(5).split('.')      # KJV numbering where it differs
        (grk if na else grk_tr)[(m.group(1), int(c), int(v))].append((re.sub(r'[¶¬\[\]]', '', g).strip(), ds.strip(), gram.strip(), tr.replace(' ', '')))
# Nestle-Aland words; a verse NA leaves out (e.g. Mat 17:21) is given in the Textus Receptus words
for k in list(grk_tr):
    if k not in grk: grk[k] = grk_tr[k]
for (bk, c, v), ws in grk.items():
    for w in ws: add(bk, c, v, *w)
print('verses', len(verses), 'words', sum(len(w) for w in verses.values()), file=sys.stderr)

# ---- brief lexicons ----
LEX = {}
for f in ('TBESH.txt', 'TBESG.txt'):
    for line in open(os.path.join(STEP, f), encoding='utf-8-sig'):
        x = line.rstrip('\n').split('\t')
        if len(x) < 8 or not re.match(r'^[HG]\d{4}', x[0]): continue
        ds = x[1].split('=')[0].strip()
        if not re.match(r'^[HG]\d', ds): continue
        d = re.sub(r'<[^>]+>', ' ', x[7]); d = re.sub(r'\s+', ' ', d).strip()
        if len(d) > 220: d = d[:220].rsplit(' ', 1)[0] + '…'
        LEX[ds] = [x[3], x[4], x[6], d]
def lex(ds):
    if ds in LEX: return LEX[ds]
    b = re.match(r'[HG]\d+', ds)
    if b:
        base = b.group(0)
        if base in LEX: return LEX[base]
        for k in LEX:
            if k.startswith(base) and not k[len(base):len(base)+1].isdigit(): return LEX[k]
    return None

# ---- Strong's on the app's KJV words ----
TAG = re.compile(r'\[([HG]\d+)\]')
EN_RE = re.compile(r'"((?:[1-3]?[A-Za-z]{2,3})\|(\d+)\|(\d+))"\s*:\s*\{\s*"en"\s*:\s*"((?:[^"\\]|\\.)*)"')
def kjv_tokens(s):
    s = re.sub(r'</?em>', '', s).replace('[[', ' ').replace(']]', ' ')
    out = []
    for m in re.finditer(r'\[([HG]\d+)\]|[^\W\d_]+', s):
        if m.group(1):
            if out: out[-1][1].append(m.group(1))
        else: out.append((m.group(0), []))
    return out
def kjv_book(code):
    out = {}
    for m in EN_RE.finditer(open(os.path.join(KJV, code + '.json'), encoding='utf-8').read()):
        if m.group(1).split('|')[0] != code: continue
        try: t = json.loads('"' + m.group(4) + '"')
        except Exception: t = m.group(4)
        out[(int(m.group(2)), int(m.group(3)))] = t
    return out
def strongs_for(app_words, tagged):
    a = [w.lower() for w in app_words]; b = [w.lower() for w, _ in tagged]
    res = [[] for _ in app_words]
    for blk in difflib.SequenceMatcher(a=a, b=b, autojunk=False).get_matching_blocks():
        for k in range(blk.size): res[blk.a + k] = [snum(t) for t in tagged[blk.b + k][1]]
    return res

def link(ow, est):
    """pairs (original token index, KJV word index) for words sharing a Strong's number;
    repeated numbers are paired in order"""
    occ_o, occ_e = defaultdict(list), defaultdict(list)
    for i, (toks, s) in enumerate(ow):
        if s: occ_o[s].append(toks)
    for j, ss in enumerate(est):
        for s in ss: occ_e[s].append(j)
    pairs = set()
    for s, os_ in occ_o.items():
        es = occ_e.get(s)
        if not es: continue
        if len(os_) == len(es): zipped = zip(os_, ([e] for e in es))
        elif len(os_) == 1: zipped = [(os_[0], es)]
        elif len(es) == 1: zipped = [(t, es) for t in os_]
        else:   # unequal repeats: nearest by relative position
            zipped = [(t, [es[min(len(es) - 1, round(k * len(es) / len(os_)))]]) for k, t in enumerate(os_)]
        for toks, ens in zipped:
            for t in toks:
                for e in ens: pairs.add((t, e))
    return [n for p in sorted(pairs) for n in p]

stat = [0, 0]
for b in range(66):
    alf = f'{D}al{b:02d}.json'; al = json.load(open(alf))
    en = json.load(open(f'{D}en{b:02d}.json'))
    kj = kjv_book(KC[b])
    OR, OW, used = [], [], set()
    for c in range(1, len(en) + 1):
        orc, owc = [], []
        for v in range(1, len(en[c-1]) + 1):
            ws = [w for w in verses.get((b, c, v), []) if tokens(w[0])]   # e.g. a ketiv with no reading
            # text: maqaf joins the next word without a space
            text = ''
            for k, (t, *_r) in enumerate(ws):
                text += t
                if k < len(ws) - 1 and not t.endswith('־'): text += ' '
            # token positions of each original word in that text
            pos, ti = [], 0
            for t, *_r in ws:
                n = len(tokens(t)); pos.append(list(range(ti, ti + n))); ti += n
            assert ti == len(tokens(text)), (b, c, v)
            orc.append(text)
            # one entry per word on screen (a few original words show as two)
            owc.append(' '.join('|'.join([s.replace(' ', ''), g.replace(' ', ''), tr.replace('|', '').replace(' ', '')]) for p, (_t, s, g, tr) in zip(pos, ws) for _ in p))
            for _t, s, *_r in ws:
                if s: used.add(s)
            ew = W.findall(en[c-1][v-1] or '')
            kv = kj.get((c, v))
            est = strongs_for(ew, kjv_tokens(kv)) if kv else [[] for _ in ew]
            pr = link([(p, snum(w[1]) if w[1] else None) for p, w in zip(pos, ws)], est)
            rec = al['v'][c-1][v-1]
            if pr: rec['or'] = pr
            else: rec.pop('or', None)
            stat[0] += len({pr[i+1] for i in range(0, len(pr), 2)}); stat[1] += sum(1 for s in est if s)
        OR.append(orc); OW.append(owc)
    al['or'], al['ow'] = OR, OW
    al['og'] = {s: lex(s) for s in sorted(used) if lex(s)}
    json.dump(al, open(alf, 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
print('KJV tagged words linked to the original:', stat[0], '/', stat[1], file=sys.stderr)
