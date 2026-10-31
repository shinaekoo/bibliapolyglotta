"""Places of the Bible, Bible-wide -> web/data/gi.json, gp0.json, gp1.json

Backbone: STEPBible TIPNR places (CC BY 4.0) - every name a place goes by in the Hebrew/Greek
(Luz|Bethel, Aven|Bethel ...), with Strong's numbers, all verses, a description and map coordinates.
Added: OpenBible.info Bible Geocoding Data (CC BY 4.0) - the modern site(s) and how certain the
identification is, matched through TIPNR's "OpenBible name" and shared verses;
tools/place_notes.json - Korean history notes for some places (to be reviewed).

gi.json  {"d": {dStrong: place id}, "n": {place id: [English, 한국어, Latin, Deutsch, Français, original]}}
gp{0,1}.json {place id: {"nm": [[name, original, dStrong, first ref [b,c,v], verses]], "b","s","a": English text,
              "ll": [lat, lon] (TIPNR map point), "mod": [[modern name, lon, lat, score 0-1000]], "mko": {modern: 한국어},
              "note": {"t": Korean note, "refs": [...]}, "ob": OpenBible slug, "cc": [total, packed refs]}}
usage: python3 tools/build_geo.py STEP_DIR OPENBIBLE_DIR
Run after tools/build_orig_lex.py (names in the translations come from its renderings).
"""
import json, os, re, sys, importlib.util
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
D = os.path.join(HERE, '..', 'web', 'data') + '/'
STEP, OB = sys.argv[1], sys.argv[2]
# shared helpers (name matching by sound, verse text) live in build_persons.py
spec = importlib.util.spec_from_file_location('bp', os.path.join(HERE, 'build_persons.py'))
src = open(os.path.join(HERE, 'build_persons.py'), encoding='utf-8').read()
helpers = src[src.index('# ---- matching a place name across translations by sound ----'):src.index("def ids(field):")]
SC = 'Gen Exo Lev Num Deu Jos Jdg Rut 1Sa 2Sa 1Ki 2Ki 1Ch 2Ch Ezr Neh Est Job Psa Pro Ecc Sng Isa Jer Lam Ezk Dan Hos Jol Amo Oba Jon Mic Nam Hab Zep Hag Zec Mal Mat Mrk Luk Jhn Act Rom 1Co 2Co Gal Eph Php Col 1Th 2Th 1Ti 2Ti Tit Phm Heb Jas 1Pe 2Pe 1Jn 2Jn 3Jn Jud Rev'.split()
BI = {c: i for i, c in enumerate(SC)}
OSIS = 'Gen Exod Lev Num Deut Josh Judg Ruth 1Sam 2Sam 1Kgs 2Kgs 1Chr 2Chr Ezra Neh Esth Job Ps Prov Eccl Song Isa Jer Lam Ezek Dan Hos Joel Amos Obad Jonah Mic Nah Hab Zeph Hag Zech Mal Matt Mark Luke John Acts Rom 1Cor 2Cor Gal Eph Phil Col 1Thess 2Thess 1Tim 2Tim Titus Phlm Heb Jas 1Pet 2Pet 1John 2John 3John Jude Rev'.split()
OBI = {c: i for i, c in enumerate(OSIS)}
CAP = 240
def b36(n): return '0123456789abcdefghijklmnopqrstuvwxyz'[n // 36] + '0123456789abcdefghijklmnopqrstuvwxyz'[n % 36]
def clean(t):
    t = re.sub(r'<br\s*/?>', '\n', t or '', flags=re.I); t = re.sub(r'<[^>]+>', '', t)
    return re.sub(r'[ \t]+', ' ', t).replace(' \n', '\n').strip()
exec(helpers)   # roman, key_ko, key_lat, sim, LAIDX, W, words, by_sound, and OX (below)

# ---- TIPNR places ----
lines = open(os.path.join(STEP, 'TIPNR.txt'), encoding='utf-8-sig').read().split('\n')
P = {}
i = 0
while i < len(lines):
    if not re.match(r'^\$=+ *PLACE', lines[i]): i += 1; continue
    head = lines[i + 1].split('\t'); i += 2
    if len(head) < 5: continue
    un, _, ust = head[0].partition('=')
    m = re.search(r'@(-?[\d.]+),(-?[\d.]+),', head[4] if len(head) > 4 else '')
    rec = {'un': un, 'u': ust.strip(), 'obn': head[1].split('=')[0].strip(), 'nm': [], 'refs': [],
           'll': [float(m.group(1)), float(m.group(2))] if m and float(m.group(1)) else None}
    while i < len(lines) and not lines[i].startswith('$'):
        l = lines[i]; x = l.split('\t')
        if l.startswith('– ') and not l.startswith('– Total') and len(x) >= 5 and 'combined' not in x[0] and 'Mentioned' not in x[0]:
            mm = re.match(r'([HG]\d+[A-Za-z]?)«[^=]*=(.*)', x[2])
            if mm:
                rr = []
                for r in x[4].split(';'):
                    q = re.match(r'\s*([1-3]?[A-Z][a-z]{1,2})\.(\d+)\.(\d+)', r)
                    if q and not r.strip().startswith('LXX') and q.group(1) in BI: rr.append((BI[q.group(1)], int(q.group(2)), int(q.group(3))))
                name = re.split(r'\s*=|;', x[3])[0].strip() or x[1].split('|')[0].split('@')[0]
                if rr:
                    rec['nm'].append([name, re.sub('[\u0591-\u05AF\u05BD]', '', mm.group(2)).strip(), mm.group(1), list(min(rr)), len(set(rr))])
                    rec['refs'] += rr
        elif l.startswith('@Brief='): rec['b'] = clean(l[7:].split('\t')[0])
        elif l.startswith('@Short='): rec['s'] = clean(l[7:].split('\t')[0])
        elif l.startswith('@Article='): rec['a'] = clean(l[9:].split('\t')[0])
        i += 1
    if not rec['nm']: continue
    pid = rec['u'] or rec['nm'][0][2]
    while pid in P: pid += "'"
    P[pid] = rec

# ---- OpenBible: modern sites ----
A = [json.loads(l) for l in open(os.path.join(OB, 'data', 'ancient.jsonl'), encoding='utf-8')]
def ob_refs(p):
    out = set()
    for q in p.get('verses', []):
        bk, c, v = q['osis'].split('.')
        if bk in OBI: out.add((OBI[bk], int(c), int(v)))
    return out
def modern_of(p):
    best = {}
    for idn in p.get('identifications', []):
        for r in idn.get('resolutions', []):
            if not r.get('lonlat'): continue
            mm = re.search(r'>([^<]+)<', r.get('description', '')); name = mm.group(1) if mm else ''
            lon, lat = (float(x) for x in r['lonlat'].split(','))
            s = int(r.get('best_path_score') or 0)
            if name not in best or best[name][3] < s: best[name] = (name, round(lon, 5), round(lat, 5), s)
    return sorted(best.values(), key=lambda x: -x[3])[:3]
OBR = [(p, ob_refs(p)) for p in A]
by_name = defaultdict(list)
for p, rs in OBR: by_name[re.sub(r'\s+\d+$', '', p['friendly_id']).lower()].append((p, rs))
NOTES = json.load(open(os.path.join(HERE, 'place_notes.json'), encoding='utf-8'))

index, names = {}, {}
shards = [{}, {}]
matched = 0
for pid, r in sorted(P.items()):
    refs = set(r['refs'])
    # OpenBible place: same name and most shared verses, else most shared verses overall
    cands = by_name.get(r['obn'].lower(), []) or by_name.get(r['un'].split('@')[0].split('|')[-1].lower(), [])
    best, bo = None, 0
    for p, rs in (cands or OBR):
        o = len(rs & refs)
        if o > bo: best, bo = p, o
    if best and not cands and bo < max(2, 0.5 * len(refs)): best = None
    e = {'nm': r['nm']}
    for k in ('b', 's', 'a'):
        if r.get(k): e[k] = r[k]
    if r['ll']: e['ll'] = r['ll']
    if best:
        matched += 1
        md = modern_of(best)
        if md: e['mod'] = md
        mko = {n: NOTES['modern_ko'][n] for n, *_ in md if n in NOTES['modern_ko']}
        if mko: e['mko'] = mko
        note = NOTES['notes'].get(best['id']) or NOTES['notes'].get(best['friendly_id'])
        if note: e['note'] = note
        e['ob'] = best.get('url_slug', '')
    rl = sorted(refs)
    pick = rl if len(rl) <= CAP else [rl[round(j * (len(rl) - 1) / (CAP - 1))] for j in range(CAP)]
    e['cc'] = [len(rl), ''.join(b36(b) + b36(c) + b36(v) for b, c, v in pick)]
    for _, _, ds, _, _ in r['nm']: index.setdefault(ds, pid)
    main = max(r['nm'], key=lambda x: x[4])
    en = r['un'].split('@')[0].split('|')[-1].replace('_', ' ')
    over = NOTES.get('names', {}).get(en, {})
    def nm_in(k):
        if over.get(k): return over[k]
        cands2 = [w for _, _, d, _, _ in r['nm'] for w, _n in (OX.get(d, {}).get('r', {}).get(k) or [])[:3]]
        scored = [(sim(key_ko(w) if k == 'ko' else key_lat(w), key_lat(main[0])), w) for w in cands2 if ' ' not in w]
        bs = by_sound(main[0], sorted(set(tuple(x) for x in rl)), k)
        if bs: scored.append((sim(key_ko(bs) if k == 'ko' else key_lat(bs), key_lat(main[0])) + 0.01, bs))
        good = [w for sc, w in sorted(scored, reverse=True) if sc >= (0.55 if k == 'ko' else 0.7)]
        return good[0] if good else ''
    names[pid] = [en] + [nm_in(k) for k in ('ko', 'la', 'de', 'fr')] + [main[1]]
    shards[sum(map(ord, pid)) % 2][pid] = e
json.dump({'d': index, 'n': names}, open(f'{D}gi.json', 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
for s in range(2):
    json.dump(shards[s], open(f'{D}gp{s}.json', 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
print('places', len(P), 'with OpenBible', matched, 'dStrongs', len(index), 'KB', os.path.getsize(f'{D}gi.json') // 1024,
      [os.path.getsize(f'{D}gp{s}.json') // 1024 for s in range(2)], file=sys.stderr)
