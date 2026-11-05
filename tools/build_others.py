"""The Bible's other named things — gods, angels, months, musical terms (STEPBible TIPNR, CC BY 4.0)
-> web/data/oi.json, oo.json

TIPNR sorts its records as PERSON, PLACE and OTHER. tools/build_persons.py and tools/build_geo.py take the
first two; this takes the third, where the gods and idols are: Baal, Molech, Dagon, Asherah, Ashtoreth,
Chemosh, Artemis, Zeus, and with them the angels (Gabriel, Satan, Abaddon), the month names (Abib, Nisan,
Adar) and the musical terms of the psalm titles (Alamoth, Al-taschith, Selah). None of them could be tapped
in the app before, because they are neither a person nor a place.

oi.json  {"d": {dStrong: id}, "n": {id: [English, 한국어, Latin, Deutsch, Français, original,
                                        Español, Português, Italiano, Indonesia, 日本語, 中文]}}
oo.json  {id: {"k": kind (god/angel/month/music/other), "ds": one line, "b"/"s"/"a": STEPBible's summaries,
               "dsc": that line as a code the app says in its own language,
               "nm": [[name, original form, dStrong]], "cc": [total, packed refs]}}

A name in a translation is the word that translation most often uses for the record's own Strong's number
(web/data/ox*.json), kept only when it sounds like the English name — so Ashtoreth does not take 밀곰 from a
bad alignment, and Asherah does not take the KJV's "grove".
Run after tools/build_orig_lex.py.  usage: python3 tools/build_others.py STEP_DIR
"""
import json, os, re, sys
from collections import defaultdict
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from nameutil import key_ko, key_lat, sim
from ko_names import ko_bare as _ko_bare
from langnorm import zh_n

D = os.path.join(HERE, '..', 'web', 'data') + '/'
STEP = sys.argv[1]
SC = 'Gen Exo Lev Num Deu Jos Jdg Rut 1Sa 2Sa 1Ki 2Ki 1Ch 2Ch Ezr Neh Est Job Psa Pro Ecc Sng Isa Jer Lam Ezk Dan Hos Jol Amo Oba Jon Mic Nam Hab Zep Hag Zec Mal Mat Mrk Luk Jhn Act Rom 1Co 2Co Gal Eph Php Col 1Th 2Th 1Ti 2Ti Tit Phm Heb Jas 1Pe 2Pe 1Jn 2Jn 3Jn Jud Rev'.split()
BI = {c: i for i, c in enumerate(SC)}
CAP = 240
NIX = [('ko', 1), ('la', 2), ('de', 3), ('fr', 4), ('es', 6), ('pt', 7), ('it', 8), ('id', 9), ('ja', 10), ('zh', 11)]
def b36(n): return '0123456789abcdefghijklmnopqrstuvwxyz'[n // 36] + '0123456789abcdefghijklmnopqrstuvwxyz'[n % 36]
def clean(t):
    t = re.sub(r'<br\s*/?>', '\n', t or '', flags=re.I)
    t = re.sub(r'<[^>]+>', '', t)
    return re.sub(r'[ \t]+', ' ', t).replace(' \n', '\n').strip()
def ko_bare(nm, en): return _ko_bare(nm, en, f'{D}../../text', sim, key_ko, key_lat)

# ---- what kind of thing a record is, from TIPNR's own description ----
def kind_of(ds, cat):
    d = (ds or '').lower()
    # TIPNR's own word for the God of Israel (YHWH, Adonai, Elohim). He is not one of the gods and idols this
    # file is about, and marking every "LORD" in the text would be both wrong and unwelcome.
    if d == 'the deity': return 'deity'
    if 'deity' in d and 'angel' in d: return 'god'          # "a male deity/angel": listed as both
    if 'deity' in d or 'god' in d.split(): return 'god'
    if 'angel' in d or 'satan' in d or 'demon' in d: return 'angel'
    if 'month' in d: return 'month'
    if 'musical' in d or 'music' in d: return 'music'
    return 'other'
KEEP = ('god', 'angel', 'month', 'music')      # the rest of OTHER is titles, letters and loose words
def code_of(ds):
    """TIPNR writes its one-line descriptions to a pattern, so the app can say them in the reader's language:
    'A male deity in the Old Testament' -> god.m.ot, 'Name of the 3rd month' -> month.3"""
    d = (ds or '').lower()
    m = re.search(r'name of the (\d+)', d)
    if m: return 'month.' + m.group(1)
    if 'title of a musical' in d: return 'music.title'
    if 'musical' in d: return 'music'
    if 'demon' in d: return 'demons'
    t = '.nt' if 'new testament' in d else ('.ot' if 'old testament' in d else '')
    if 'deity/angel' in d: return 'godangel' + t
    if 'deity' in d: return 'god.' + ('f' if 'female' in d else 'm') + t
    if 'angel' in d: return 'angel' + t
    return ''

lines = open(os.path.join(STEP, 'TIPNR.txt'), encoding='utf-8-sig').read().split('\n')
P, i = {}, 0
while i < len(lines):
    if not re.match(r'^\$=+ *OTHER', lines[i]): i += 1; continue
    i += 1
    while i < len(lines) and not lines[i].startswith('$'):
        head = lines[i].split('\t')
        if '=' not in head[0] or '@' not in head[0] or lines[i].startswith(('–', '‖', '*', '@')):
            i += 1; continue
        un, _, ust = head[0].partition('=')
        rec = {'un': un, 'u': ust.strip(), 'ds': clean(head[1]) if len(head) > 1 else '',
               'cat': head[8].strip() if len(head) > 8 else '', 'nm': [], 'refs': [], 'dss': []}
        i += 1
        while i < len(lines) and not lines[i].startswith('$') and ('=' not in lines[i].split('\t')[0] or '@' not in lines[i].split('\t')[0]):
            l = lines[i]; x = l.split('\t')
            if l.startswith('– ') and not l.startswith('– Total') and len(x) >= 5:
                m = re.match(r'([HG]\d+[A-Za-z]?)«[^=]*=(.*)', x[2])
                if m:
                    ds, form = m.group(1), re.sub('[֑-ֽ֯]', '', m.group(2)).strip()
                    rec['dss'].append(ds); rec['nm'].append([x[3].strip(), form, ds])
                    for r in x[4].split(';'):
                        mm = re.match(r'([1-3]?[A-Z][a-z]{1,2})\.(\d+)\.(\d+)', r.strip())
                        if mm and not r.strip().startswith('LXX') and mm.group(1) in BI:
                            rec['refs'].append((BI[mm.group(1)], int(mm.group(2)), int(mm.group(3))))
            elif l.startswith('@Brief='): rec['b'] = clean(l[7:].split('\t')[0])
            elif l.startswith('@Short='): rec['s'] = clean(l[7:].split('\t')[0])
            elif l.startswith('@Article='): rec['a'] = clean(l[9:].split('\t')[0])
            i += 1
        rec['k'] = kind_of(rec['ds'], rec['cat'])
        rec['dsc'] = code_of(rec['ds'])
        if rec['dss'] and rec['k'] in KEEP:
            pid = rec['u'] or rec['dss'][0]
            while pid in P: pid += "'"
            P[pid] = rec
print('OTHER records kept', len(P), {k: sum(1 for r in P.values() if r['k'] == k) for k in KEEP}, file=sys.stderr)

# ---- the name in each translation: its commonest rendering, when it sounds like the English name ----
OX = {}
for s in range(4): OX.update(json.load(open(f'{D}ox{s}.json', encoding='utf-8')))
def nm_in(dss, k, en):
    cands = []
    for d in dss:
        for w, n in (OX.get(d, {}).get('r', {}).get(k) or [])[:3]:
            if ' ' in w: continue
            w = zh_n(w) if k == 'zh' else (ko_bare(w, en) if k == 'ko' else w)
            if not w: continue
            cands.append((n, w))
    scored = []
    for n, w in sorted(set(cands), reverse=True):
        if k in ('zh', 'ja'):            # another script: the commonest rendering written in it, shortest on a tie
            ok = all('ァ' <= c <= 'ヺ' or c in 'ー・' for c in w) if k == 'ja' else all('一' <= c <= '鿿' for c in w)
            if ok and 2 <= len(w) <= 8: scored.append((n, -len(w), w))
            continue
        a, b = (key_ko(w) if k == 'ko' else key_lat(w)), key_lat(en)
        s = sim(a, b)
        # alike enough, or the same name in another case (Astarthen for Ashtoreth): a shared opening
        if s >= (0.55 if k == 'ko' else 0.7) or (s >= 0.5 and a[:3] == b[:3] and len(b) >= 4):
            scored.append((round(s, 3), n, w))
    return max(scored)[-1] if scored else ''

index, names, recs = {}, {}, {}
for pid, r in sorted(P.items()):
    for ds in r['dss']: index.setdefault(ds, pid)
    en = r['un'].split('@')[0].split('|')[-1].replace('_', ' ')
    main = max(r['dss'], key=lambda d: (OX.get(d, {}).get('cc', [0])[0], d))
    orig = next((f for _, f, d in r['nm'] if d == main), r['nm'][0][1])
    names[pid] = [en] + [nm_in(r['dss'], k, en) for k, _ in NIX[:4]] + [orig] + [nm_in(r['dss'], k, en) for k, _ in NIX[4:]]
    refs = sorted(set(r['refs']))
    pick = refs if len(refs) <= CAP else [refs[round(j * (len(refs) - 1) / (CAP - 1))] for j in range(CAP)]
    e = {'k': r['k'], 'ds': r['ds'], 'dsc': r['dsc'], 'nm': r['nm'],
         'cc': [len(refs), ''.join(b36(b) + b36(c) + b36(v) for b, c, v in pick)]}
    for k in ('b', 's', 'a'):
        if r.get(k): e[k] = r[k]
    recs[pid] = e
json.dump({'d': index, 'n': names}, open(f'{D}oi.json', 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
json.dump(recs, open(f'{D}oo.json', 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
print('things', len(recs), 'dStrongs', len(index), 'KB', os.path.getsize(f'{D}oi.json') // 1024,
      os.path.getsize(f'{D}oo.json') // 1024, file=sys.stderr)
