"""Build the data of the original-language comparison app (원어 대조 성경).

Inputs
  ORIG      orig.json from parse_step.py (Hebrew OT / Greek TR, KJV verse numbering)
  BASE      the Polyglotta web/data folder (ko*.json = 개역한글, en*.json = KJV)
  KJV       kaiserlik/kjv folder (KJV with Strong's numbers)
  STEP      STEPBible-Data folder (TBESH / TBESG brief lexicons)
  FA        fast_align build folder
  OUT       output data folder

Outputs (OUT/)
  ko##.json, en##.json   copies of 개역한글 and KJV
  or##.json              original words per chapter/verse: [text, translit, dStrongs, grammar, main]
  al##.json              word links per chapter/verse: [ko pairs, en pairs], each flat [ko_or_en_index, original_index, ...]
  cc#.json (16 shards)   dStrong -> [count, packed places]  (place = book2 chapter2 verse2 word2, base 36)
  lx#.json (16 shards)   dStrong -> [lemma, translit, pos, gloss, definition, count, ko renderings, KJV renderings]

usage: python3 build_original.py ORIG BASE KJV STEP FA OUT
"""
import json, os, re, shutil, subprocess, sys, tempfile, difflib, html
from collections import defaultdict, Counter

ORIG, BASE, KJV, STEP, FA, OUT = sys.argv[1:7]
os.makedirs(OUT, exist_ok=True)
CODES = 'Gen Exo Lev Num Deu Jos Jdg Rth 1Sa 2Sa 1Ki 2Ki 1Ch 2Ch Ezr Neh Est Job Psa Pro Ecc Sng Isa Jer Lam Eze Dan Hos Joe Amo Oba Jon Mic Nah Hab Zep Hag Zec Mal Mat Mar Luk Jhn Act Rom 1Co 2Co Gal Eph Phl Col 1Th 2Th 1Ti 2Ti Tit Phm Heb Jas 1Pe 2Pe 1Jo 2Jo 3Jo Jde Rev'.split()
STEPCODES = ('Gen Exo Lev Num Deu Jos Jdg Rut 1Sa 2Sa 1Ki 2Ki 1Ch 2Ch Ezr Neh Est Job Psa Pro Ecc Sng Isa Jer Lam Ezk Dan Hos Jol Amo Oba Jon Mic Nam Hab Zep Hag Zec Mal '
             'Mat Mrk Luk Jhn Act Rom 1Co 2Co Gal Eph Php Col 1Th 2Th 1Ti 2Ti Tit Phm Heb Jas 1Pe 2Pe 1Jn 2Jn 3Jn Jud Rev').split()
SBI = {c: i for i, c in enumerate(STEPCODES)}
W = re.compile(r'[^\W\d_]+')
KOCUT = int(os.environ.get('KOCUT', '2'))   # first two syllables of the Korean stem align best
NOLINK = {'H853', 'G3588'}     # object marker, Greek article: no word of their own in Korean
B36 = '0123456789abcdefghijklmnopqrstuvwxyz'
def b2(n):
    assert 0 <= n < 1296, n
    return B36[n // 36] + B36[n % 36]
def base(s): return re.sub(r'[A-Za-z]$', '', s)

orig = json.load(open(ORIG))
def load(pre, i): return json.load(open(os.path.join(BASE, f'{pre}{i:02d}.json')))
KO = [load('ko', b) for b in range(66)]
EN = [load('en', b) for b in range(66)]

# ---- Korean stems (same normalizer as the Polyglotta alignment) ----
KO_SUF = sorted(('께로 께서도 께는 께 이니라 이라 이요 이며 이니 이로다 이시라 이시니 이었더라 이더라 '
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

# ---- original words: the key that stands for the word (its own morpheme) ----
def main_key(w): return w[2].split('/')[w[4]] if '/' in w[2] else w[2]
def match_keys(w):
    k = {base(main_key(w))} | {base(a) for a in w[5]}
    return k

# ---- KJV Strong's tags on the app's KJV words ----
EN_RE = re.compile(r'"((?:[1-3]?[A-Za-z]{2,3})\|(\d+)\|(\d+))"\s*:\s*\{\s*"en"\s*:\s*"((?:[^"\\]|\\.)*)"')
def kjv_book(code):
    out = {}
    for m in EN_RE.finditer(open(os.path.join(KJV, code + '.json'), encoding='utf-8').read()):
        if m.group(1).split('|')[0] != code: continue
        try: t = json.loads('"' + m.group(4) + '"')
        except Exception: t = m.group(4)
        out[(int(m.group(2)), int(m.group(3)))] = t
    return out
def kjv_tokens(s):
    """[(word, [strongs])]; a tag covers the untagged words just before it (up to 4), e.g. 'the heaven[H8064]'."""
    s = re.sub(r'</?em>', '', s).replace('[[', ' ').replace(']]', ' ')
    out, pend = [], []
    for m in re.finditer(r'\[([HG])0*(\d+)\]|[^\W\d_]+', s):
        if m.group(1):
            tag = m.group(1) + m.group(2)
            if pend:
                for j in pend[-4:]: out[j][1].append(tag)
                pend = []
            elif out: out[-1][1].append(tag)
        else:
            out.append((m.group(0), [])); pend.append(len(out) - 1)
    return out
def strongs_for(app_words, tagged):
    a = [w.lower() for w in app_words]; b = [w.lower() for w, _ in tagged]
    res = [[] for _ in app_words]
    for blk in difflib.SequenceMatcher(a=a, b=b, autojunk=False).get_matching_blocks():
        for k in range(blk.size): res[blk.a + k] = tagged[blk.b + k][1]
    return res

def en_links(en_words, en_tags, ow):
    """KJV word index <-> original word index through shared Strong's numbers."""
    pairs = set()
    okeys = [match_keys(w) for w in ow]
    nums = set(t for ts in en_tags for t in ts)
    for n in nums:
        if n in NOLINK: continue
        E = [i for i, ts in enumerate(en_tags) if n in ts]
        O = [j for j, ks in enumerate(okeys) if n in ks]
        if not O: continue
        # group runs of neighbouring English words (one phrase = one original word)
        groups = []
        for i in E:
            if groups and i == groups[-1][-1] + 1: groups[-1].append(i)
            else: groups.append([i])
        if len(groups) == len(O):
            for g, j in zip(groups, O):
                for i in g: pairs.add((i, j))
        else:
            for g in groups:
                for i in g:
                    for j in O: pairs.add((i, j))
    return sorted(pairs)

rows = []   # (b, c, v, ko words, en words, original words, en pairs)
missing_kjv = 0
for b in range(66):
    kj = kjv_book(CODES[b])
    for c in range(1, len(EN[b]) + 1):
        for v in range(1, len(EN[b][c-1]) + 1):
            ew = W.findall(EN[b][c-1][v-1] or '')
            kw = W.findall((KO[b][c-1][v-1] if c <= len(KO[b]) and v <= len(KO[b][c-1]) else '') or '')
            ow = orig[b][c-1][v-1] if c <= len(orig[b]) and v <= len(orig[b][c-1]) else []
            kv = kj.get((c, v))
            if kv is None: missing_kjv += 1
            et = strongs_for(ew, kjv_tokens(kv)) if kv else [[] for _ in ew]
            rows.append((b, c, v, kw, ew, ow, en_links(ew, et, ow)))
print('verses', len(rows), 'no tagged KJV', missing_kjv, file=sys.stderr)
print('KJV words linked', sum(len(set(i for i, _ in r[6])) for r in rows), '/', sum(len(r[4]) for r in rows), file=sys.stderr)

# ---- Korean <-> original with fast_align (both directions, symmetrized) ----
def run_align(src, tgt, how):
    tmp = tempfile.mkdtemp()
    f = os.path.join(tmp, 'in.txt')
    with open(f, 'w') as fh:
        for s, t in zip(src, tgt):
            fh.write((' '.join(s) or '<e>') + ' ||| ' + (' '.join(t) or '<e>') + '\n')
    def run(*a, out):
        subprocess.run([os.path.join(FA, 'fast_align'), '-i', f, *FAOPT, *a], stdout=open(out, 'w'), stderr=subprocess.DEVNULL, check=True)
    run(out=f + '.fwd'); run('-r', out=f + '.rev')
    lines = subprocess.run([os.path.join(FA, 'atools'), '-i', f + '.fwd', '-j', f + '.rev', '-c', how], capture_output=True, text=True, check=True).stdout.splitlines()
    shutil.rmtree(tmp, ignore_errors=True)
    return [[tuple(map(int, p.split('-'))) for p in line.split()] for line in lines]

src, tgt, tmap = [], [], []
for r in rows:
    src.append([ko_n(w)[:KOCUT] for w in r[3]])
    keep = [j for j, w in enumerate(r[5]) if base(main_key(w)) not in NOLINK]
    tgt.append([main_key(r[5][j]) for j in keep]); tmap.append(keep)
SYM = os.environ.get('SYM', 'grow-diag-final-and')
FAOPT = os.environ.get('FAOPT', '-d -o -v -I 8').split()
ko_al = run_align(src, tgt, SYM)
ko_pairs = [sorted((i, tmap[n][j]) for i, j in al if i < len(src[n]) and j < len(tgt[n])) for n, al in enumerate(ko_al)]
print('Korean words linked', sum(len(set(i for i, _ in p)) for p in ko_pairs), '/', sum(len(r[3]) for r in rows), file=sys.stderr)

# ---- write text, links ----
for b in range(66):
    shutil.copy(os.path.join(BASE, f'ko{b:02d}.json'), os.path.join(OUT, f'ko{b:02d}.json'))
    shutil.copy(os.path.join(BASE, f'en{b:02d}.json'), os.path.join(OUT, f'en{b:02d}.json'))
    json.dump([[[([w[0], w[1], w[2], w[3], w[4]] if w[4] else [w[0], w[1], w[2], w[3]]) for w in vs] for vs in ch] for ch in orig[b]],
              open(os.path.join(OUT, f'or{b:02d}.json'), 'w'), ensure_ascii=False, separators=(',', ':'))
AL = [[[None] * len(EN[b][c]) for c in range(len(EN[b]))] for b in range(66)]
for n, r in enumerate(rows):
    b, c, v = r[:3]
    AL[b][c-1][v-1] = [[x for p in ko_pairs[n] for x in p], [x for p in r[6] for x in p]]
for b in range(66):
    json.dump(AL[b], open(os.path.join(OUT, f'al{b:02d}.json'), 'w'), separators=(',', ':'))

# ---- renderings: how 개역한글 and KJV translate each original word ----
KOR, ENR = defaultdict(Counter), defaultdict(Counter)
KOSURF = defaultdict(Counter)
ENSURF = defaultdict(Counter)
LEADW = set(('and but the a an of thy thine my his her your our their its unto to which that for in with from by o upon at as '
  'is was are be been am were i he she it we ye you they there no not let shall will should would may might must have hath had do did doth when even then them him me us all these this those according out into against through thou').split())
KO_PART = sorted('께서는 께서 에게서 에게는 에게 으로써 으로서 으로는 으로 로써 로서 로는 에서는 에서 에는 에도 이여 이시여 께 에 로 의 은 는 이 가 을 를 과 와 도 만 여'.split(), key=len, reverse=True)
def ko_disp(w):
    """One particle off the end, for showing how 개역한글 renders a word ('여호와는' -> '여호와')."""
    for e in KO_PART:
        if w.endswith(e) and len(w) > len(e) and not (len(e) == 1 and len(w) == 2 and e in '이가여'):
            return w[:-len(e)]
    return w
def is_verb(w):
    g = w[3].split('/')
    m = g[w[4]] if w[4] < len(g) else g[-1]
    if w[4] == 0 and m[:1] in 'HA' and w[2].startswith('H'): m = m[1:]
    return m.startswith('V')
def runs(idx):
    out = []
    for i in sorted(idx):
        if out and i == out[-1][-1] + 1: out[-1].append(i)
        else: out.append([i])
    return out
for n, r in enumerate(rows):
    kw, ew, ow = r[3], r[4], r[5]
    byo = defaultdict(set)
    for i, j in ko_pairs[n]: byo[j].add(i)
    for j, idx in byo.items():
        key = main_key(ow[j])
        for g in runs(idx)[:2]:
            word = kw[g[-1]] if is_verb(ow[j]) else ko_disp(kw[g[-1]])   # verbs keep their ending: '죽은', '믿으라'
            KOR[key][word[:2]] += 1; KOSURF[(key, word[:2])][word] += 1
    bye = defaultdict(set)
    for i, j in r[6]: bye[j].add(i)
    for j, idx in bye.items():
        key = main_key(ow[j])
        for g in runs(idx)[:2]:
            ws = [ew[i] for i in g if ew[i] != 's']
            if not ws: continue
            while len(ws) > 1 and ws[0].lower() in LEADW: ws = ws[1:]
            if len(ws) > 3: continue          # long runs come from repeated numbers in one verse: noise
            ph = ' '.join(ws)
            low = ph.lower()
            ENR[key][low] += 1; ENSURF[(key, low)][ph] += 1

# ---- concordance ----
OCC = defaultdict(list)
for b in range(66):
    for c, ch in enumerate(orig[b], 1):
        for v, ws in enumerate(ch, 1):
            for j, w in enumerate(ws):
                k = main_key(w)
                if re.match(r'H9\d{3}$', k): continue
                OCC[k].append((b, c, v, j))
NSH = 16
def shard(k): return int(re.sub(r'\D', '', k) or 0) % NSH
cc = [dict() for _ in range(NSH)]
for k, lst in OCC.items():
    cc[shard(k)][k] = [len(lst), ''.join(b2(b) + b2(c) + b2(v) + b2(j) for b, c, v, j in lst)]
for s in range(NSH):
    json.dump(cc[s], open(os.path.join(OUT, f'cc{s}.json'), 'w'), separators=(',', ':'), ensure_ascii=False)

# ---- lexicon (STEPBible TBESH / TBESG, CC BY) ----
LEXF = [os.path.join(STEP, 'Lexicons', f) for f in os.listdir(os.path.join(STEP, 'Lexicons')) if f.startswith('TBES')]
lex = {}
def nk(s):
    m = re.match(r'([HG])0*(\d+)([A-Za-z]?)', s.strip())
    return m.group(1) + m.group(2) + m.group(3) if m else s.strip()
def ref_tokens(attr):
    """'Mrk.5.36; 7.29' -> ['41.5.36', '41.7.29'] (book index . chapter . verse)"""
    out, book, chap = [], None, None
    for part in re.split(r'[;,]\s*', attr):
        part = part.strip()
        m = re.match(r'([1-3]?[A-Z][a-z]+)\.(\d+)(?:\.(\d+))?', part)
        if m and m.group(1) in SBI:
            book, chap = SBI[m.group(1)], int(m.group(2)); v = int(m.group(3) or 1)
        else:
            m2 = re.match(r'(\d+)\.(\d+)', part) or re.match(r'(\d+)$', part)
            if book is None or not m2: continue
            if m2.lastindex == 2: chap, v = int(m2.group(1)), int(m2.group(2))
            else: v = int(m2.group(1))
        out.append(f'{book}.{chap}.{v}')
    return out
def clean_def(h):
    h = re.sub(r"<ref='([^']*)'>(.*?)</ref>", lambda m: ' '.join('⟦' + t + '⟧' for t in ref_tokens(m.group(1))) or m.group(2), h)
    h = re.sub(r'<br\s*/?>', '\n', h, flags=re.I)
    h = re.sub(r'</?(?!b>|/b>|i>|/i>)[^>]*>', '', h)
    h = h.replace('__', '').replace('&nbsp;', ' ')
    h = re.sub(r'[ \t]+', ' ', h)
    h = re.sub(r'\n\s*', '\n', h).strip()
    return h
for fn in LEXF:
    for line in open(fn, encoding='utf-8'):
        f = line.rstrip('\n').split('\t')
        if len(f) < 8 or not re.match(r'^[HG]\d', f[0]): continue
        key = nk(f[1].split('=')[0])
        if key in lex: continue
        lex[key] = [f[3].strip(), f[4].strip(), f[5].strip(), f[6].strip(), clean_def(f[7])]
        b = nk(f[0])
        lex.setdefault('~' + b, lex[key])
used = set()
for b in range(66):
    for ch in orig[b]:
        for ws in ch:
            for w in ws:
                for p in w[2].split('/'): used.add(p)
lx = [dict() for _ in range(NSH)]
miss = []
for k in sorted(used):
    e = lex.get(k) or lex.get(base(k)) or lex.get('~' + base(k))
    if not e: miss.append(k); e = ['', '', '', '', '']
    kc = Counter(KOR[k])
    for g in list(kc):   # '땅이' joins '땅'
        if len(g) == 2 and g[1] in '이가여' and g[0] in kc: kc[g[0]] += kc.pop(g)
    kr = [[(KOSURF[(k, s)] + KOSURF[(k, s + '이')] + KOSURF[(k, s + '가')]).most_common(1)[0][0] if KOSURF[(k, s)] else s, n] for s, n in kc.most_common(8) if n >= 2 or len(kc) < 4][:8]
    er = [[ENSURF[(k, s)].most_common(1)[0][0], n] for s, n in ENR[k].most_common(8)][:8]
    lx[shard(k)][k] = e + [len(OCC.get(k, [])), kr, er]
for s in range(NSH):
    json.dump(lx[s], open(os.path.join(OUT, f'lx{s}.json'), 'w'), ensure_ascii=False, separators=(',', ':'))
print('lexicon entries', len(used), 'missing', len(miss), miss[:20], file=sys.stderr)
