"""Bible place names (OpenBible.info Bible Geocoding Data, CC BY 4.0) -> web/data/pl.json

For each place: names in each translation (found through the app's own word alignment),
other names, every KJV verse that mentions it, and the most likely modern location.
Marks (which KJV words are the place) are written only for the chapters given.

usage: python3 build_places.py OPENBIBLE_DIR NOTES_JSON book:chapter [book:chapter ...]
"""
import json, os, re, sys
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
D = os.path.join(HERE, '..', 'web', 'data') + '/'
OB, NOTES = sys.argv[1], sys.argv[2]
TARGET = [tuple(int(x) for x in a.split(':')) for a in sys.argv[3:]]
OSIS = 'Gen Exod Lev Num Deut Josh Judg Ruth 1Sam 2Sam 1Kgs 2Kgs 1Chr 2Chr Ezra Neh Esth Job Ps Prov Eccl Song Isa Jer Lam Ezek Dan Hos Joel Amos Obad Jonah Mic Nah Hab Zeph Hag Zech Mal Matt Mark Luke John Acts Rom 1Cor 2Cor Gal Eph Phil Col 1Thess 2Thess 1Tim 2Tim Titus Phlm Heb Jas 1Pet 2Pet 1John 2John 3John Jude Rev'.split()
BI = {c: i for i, c in enumerate(OSIS)}
LAIDX = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,18,19,20,21,22,23,26,27,28,30,31,32,33,34,35,36,37,38,39,40,41,42,43,46,47,48,49,50,51,52,53,54,55,56,57,58,59,60,61,62,63,64,65,66,67,68,69,70,71,72]
W = re.compile(r'[^\W\d_]+')
KO_SUF = sorted('께서는 께서 에게서 에게 으로부터 로부터 에서는 에서 에는 에도 으로 로 에 과 와 의 은 는 이 가 을 를 도 만 까지 부터 이요 이니 이라 이며 이니라 사람 족속 지경 땅 성 산 들 골짜기'.split(), key=len, reverse=True)
def ko_base(w):
    for e in KO_SUF:
        if w.endswith(e) and len(w) - len(e) >= 2: return w[:-len(e)]
    return w

A = {}
for l in open(os.path.join(OB, 'data', 'ancient.jsonl'), encoding='utf-8'):
    d = json.loads(l); A[d['id']] = d
notes = json.load(open(NOTES, encoding='utf-8'))
cache = {}
def load(pre, i):
    k = f'{pre}{i:02d}'
    if k not in cache: cache[k] = json.load(open(f'{D}{k}.json', encoding='utf-8'))
    return cache[k]
def words(lang, b, c, v):
    arr = load('la', LAIDX[b]) if lang == 'la' else load(lang, b)
    try: return W.findall(arr[c-1][v-1] or '')
    except IndexError: return []

def kjv_refs(p):
    out = []
    for q in p.get('verses', []):
        if 'kjv' not in q.get('translations', []): continue
        bk, c, v = q['osis'].split('.')
        if bk in BI: out.append((BI[bk], int(c), int(v)))
    return out

def find_tokens(p, b, c, v):
    """KJV word positions that spell this place in the verse"""
    en = words('en', b, c, v)
    seqs = sorted({tuple(W.findall(n)) for n in p.get('translation_name_counts', {})} | {tuple(W.findall(re.sub(r'\s+\d+$', '', p['friendly_id'])))}, key=len, reverse=True)
    hits, used = [], set()
    for s in seqs:
        if not s: continue
        for i in range(len(en) - len(s) + 1):
            if tuple(en[i:i+len(s)]) == s and not (set(range(i, i+len(s))) & used):
                hits.append(list(range(i, i+len(s)))); used |= set(range(i, i+len(s)))
    return hits

# ---- matching a place name across translations by sound ----
CHO = ['g','kk','n','d','tt','r','m','b','pp','s','ss','','j','jj','ch','k','t','p','h']
JUNG = ['a','ae','ya','yae','eo','e','yeo','ye','o','wa','wae','oe','yo','u','wo','we','wi','yu','eu','ui','i']
JONG = ['','k','k','k','n','n','n','t','l','k','m','l','l','l','p','l','m','p','p','t','t','ng','t','t','k','t','p','t']
def roman(s):
    out = []
    for ch in s:
        o = ord(ch) - 0xAC00
        if 0 <= o < 11172: out.append(CHO[o // 588] + JUNG[(o % 588) // 28] + JONG[o % 28])
    return ''.join(out)
def key_ko(s):
    r = roman(s)
    for a, b in (('eo', 'o'), ('eu', ''), ('ae', 'e'), ('oe', 'e'), ('ya', 'ia'), ('yo', 'io'), ('yu', 'iu'), ('ye', 'ie'), ('ng', 'n'), ('ch', 's'), ('j', 's'), ('kk', 'k'), ('tt', 't'), ('pp', 'p'), ('ss', 's')):
        r = r.replace(a, b)
    return r.translate(str.maketrans('gdbr', 'ktpl')).replace('h', '')
def key_lat(s):
    r = s.lower().replace('-', '').replace(' ', '')
    for a, b in (('th', 't'), ('ph', 'p'), ('ch', 'k'), ('sh', 's'), ('ck', 'k'), ('qu', 'k'), ('x', 'ks'), ('j', 'i'), ('y', 'i'), ('ee', 'e'), ('oo', 'u')):
        r = r.replace(a, b)
    r = r.translate(str.maketrans('cqzvfwgdbr', 'kksbpuktpl'))
    return re.sub(r'(.)\1', r'\1', r).replace('h', '')
def sim(a, b):
    import difflib
    return difflib.SequenceMatcher(None, a, b).ratio() if a and b else 0

def names_in(p, refs):
    """Each translation's spelling of the place: words that sound like the KJV name and recur in its verses"""
    forms = Counter()
    for b, c, v in refs:
        en = words('en', b, c, v)
        for toks in find_tokens(p, b, c, v): forms[' '.join(en[i] for i in toks)] += 1
    if not forms: return {}
    kjv = forms.most_common(1)[0][0]
    out = {'en': kjv}
    R = refs[:60]
    for lang in ('ko', 'la', 'de', 'fr'):
        cov = Counter()
        for b, c, v in R:
            ws = words(lang, b, c, v)
            cand = {w[:k] for w in ws for k in range(1, len(w) + 1)} if lang == 'ko' else set(ws) | {ws[i] + '-' + ws[i+1] for i in range(len(ws) - 1)}
            cov.update(cand)
        target = key_lat(kjv)
        best, bs = None, 0
        for w, n in cov.items():
            if lang == 'ko' and len(w) > 8: continue
            if lang != 'ko' and not all(x[:1].isupper() for x in w.split('-')): continue   # names are capitalized
            s = sim(key_ko(w) if lang == 'ko' else key_lat(w), target) + 0.35 * n / len(R)
            if lang == 'ko': s -= 0.02 * max(0, len(w) - len(kjv) // 2)   # a shorter word start drops particles
            if s > bs: best, bs = w, s
        if best and bs >= (0.6 if lang == 'ko' else 0.75): out[lang] = best
    return out

def modern_of(p, depth=0):
    """[(modern name, lon, lat, score 0-1000)] best first"""
    out = []
    for idn in p.get('identifications', []):
        for r in idn.get('resolutions', []):
            if not r.get('lonlat'): continue
            m = re.search(r'>([^<]+)<', r.get('description', '')); name = m.group(1) if m else ''
            lon, lat = (float(x) for x in r['lonlat'].split(','))
            out.append((name, round(lon, 5), round(lat, 5), int(r.get('best_path_score') or 0)))
    best = {}
    for n, lo, la, s in out:
        if n not in best or best[n][3] < s: best[n] = (n, lo, la, s)
    return sorted(best.values(), key=lambda x: -x[3])[:3]

def other_names(p):
    """places this one is 'another name for', and places that are another name for this one"""
    res = []
    for idn in p.get('identifications', []):
        if idn.get('id_source') == 'ancient' and 'another name' in idn.get('description', ''):
            res.append(idn['id'])
    for q in A.values():
        for idn in q.get('identifications', []):
            if idn.get('id_source') == 'ancient' and idn.get('id') == p['id'] and 'another name' in idn.get('description', ''):
                res.append(q['id'])
    return list(dict.fromkeys(res))

# ---- which places appear in the target chapters ----
marks = defaultdict(lambda: defaultdict(list))
used = set()
for pid, p in A.items():
    for b, c, v in kjv_refs(p):
        if (b, c) in TARGET:
            for toks in find_tokens(p, b, c, v):
                marks[f'{b}:{c}'][f'v{v}'].append([toks, pid]); used.add(pid)
# also describe the places named as their other names
extra = set()
for pid in used: extra |= set(other_names(A[pid]))
places = {}
for pid in sorted(used | extra):
    p = A[pid]; refs = kjv_refs(p)
    places[pid] = {
        'en': re.sub(r'\s+\d+$', '', p['friendly_id']),
        'types': p['types'],
        'names': {**names_in(p, refs), **(notes.get('names', {}).get(pid) or notes.get('names', {}).get(p['friendly_id']) or {})},
        'variants': sorted(n for n in p.get('translation_name_counts', {}) if n not in (p['friendly_id'],)),
        'refs': refs,
        'modern': modern_of(p),
        'other': other_names(p),
        'slug': p.get('url_slug', ''),
        'note': notes.get('notes', {}).get(pid) or notes.get('notes', {}).get(p['friendly_id']),
    }
for pid, pl in places.items():
    for n, *_ in pl['modern']:
        if n in notes.get('modern_ko', {}): pl.setdefault('modern_ko', {})[n] = notes['modern_ko'][n]
out = {'marks': {k: dict(v) for k, v in marks.items()}, 'places': places}
json.dump(out, open(D + 'pl.json', 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
print('places in target chapters', len(used), 'with other names', len(places), 'marks', sum(len(x) for v in marks.values() for x in v.values()), file=sys.stderr)
print(json.dumps({pid: [pl['en'], pl['names'].get('ko'), [m[0] for m in pl['modern']], len(pl['refs'])] for pid, pl in places.items()}, ensure_ascii=False))
