"""People of the Bible (STEPBible TIPNR, CC BY 4.0) -> web/data/pi.json, pp.json

pi.json  {"d": {dStrong: person id}, "n": {person id: [English, 한국어, Latin, Deutsch, Français, original, Español, Português, Italiano, Indonesia, 日本語, 中文]}}
         small; loaded on the first tap so any word can be checked for a person
pp.json {person id: {"t": Male/Female, "ds": description, "b": brief, "s": short, "a": article,
              "par": [ids], "sib": [ids], "pt": [ids], "off": [ids], "tr": tribe,
              "nm": [[name, original form, dStrong]], "cc": [total, packed refs]}}

Names in the translations come from web/data/ox*.json (how each translation renders the
person's Strong's number), so run tools/build_orig_lex.py first.
usage: python3 tools/build_persons.py STEP_DIR
"""
import json, os, re, sys
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
D = os.path.join(HERE, '..', 'web', 'data') + '/'
STEP = sys.argv[1]
SC = 'Gen Exo Lev Num Deu Jos Jdg Rut 1Sa 2Sa 1Ki 2Ki 1Ch 2Ch Ezr Neh Est Job Psa Pro Ecc Sng Isa Jer Lam Ezk Dan Hos Jol Amo Oba Jon Mic Nam Hab Zep Hag Zec Mal Mat Mrk Luk Jhn Act Rom 1Co 2Co Gal Eph Php Col 1Th 2Th 1Ti 2Ti Tit Phm Heb Jas 1Pe 2Pe 1Jn 2Jn 3Jn Jud Rev'.split()
BI = {c: i for i, c in enumerate(SC)}
CAP = 240
def b36(n): return '0123456789abcdefghijklmnopqrstuvwxyz'[n // 36] + '0123456789abcdefghijklmnopqrstuvwxyz'[n % 36]
def clean(t):
    t = re.sub(r'<br\s*/?>', '\n', t or '', flags=re.I)
    t = re.sub(r'<[^>]+>', '', t)
    return re.sub(r'[ \t]+', ' ', t).replace(' \n', '\n').strip()

lines = open(os.path.join(STEP, 'TIPNR.txt'), encoding='utf-8-sig').read().split('\n')
P, uniq = {}, {}          # pid -> record; UniqueName (Name@Ref) -> pid
i = 0
while i < len(lines):
    if not re.match(r'^\$=+ *PERSON', lines[i]): i += 1; continue
    head = lines[i + 1].split('\t'); i += 2
    if len(head) < 9 or head[8].strip() not in ('Male', 'Female'): continue
    un, _, ust = head[0].partition('=')
    rec = {'un': un, 'u': ust.strip(), 't': head[8].strip(), 'ds': head[1].strip(), 'par': head[2], 'sib': head[3],
           'pt': head[4], 'off': head[5], 'tr': head[6].strip(), 'nm': [], 'refs': [], 'dss': []}
    while i < len(lines) and not lines[i].startswith('$'):
        l = lines[i]; x = l.split('\t')
        if l.startswith('– ') and not l.startswith('– Total') and len(x) >= 5:
            m = re.match(r'([HG]\d+[A-Za-z]?)«[^=]*=(.*)', x[2])
            if m and 'combined' not in x[0] and 'Mentioned' not in x[0]:
                ds, form = m.group(1), re.sub('[\u0591-\u05AF\u05BD]', '', m.group(2)).strip()
                rec['dss'].append(ds); rec['nm'].append([x[3].strip(), form, ds])
                for r in x[4].split(';'):
                    r = r.strip()
                    mm = re.match(r'([1-3]?[A-Z][a-z]{1,2})\.(\d+)\.(\d+)', r)
                    if mm and not r.startswith('LXX') and mm.group(1) in BI:
                        rec['refs'].append((BI[mm.group(1)], int(mm.group(2)), int(mm.group(3))))
        elif l.startswith('@Brief='): rec['b'] = clean(l[7:].split('\t')[0])
        elif l.startswith('@Short='): rec['s'] = clean(l[7:].split('\t')[0])
        elif l.startswith('@Article='): rec['a'] = clean(l[9:].split('\t')[0])
        i += 1
    if not rec['dss']: continue
    pid = rec['u'] if rec['u'] else rec['dss'][0]
    while pid in P: pid += "'"
    P[pid] = rec; uniq[un] = pid

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


LAIDX = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,18,19,20,21,22,23,26,27,28,30,31,32,33,34,35,36,37,38,39,40,41,42,43,46,47,48,49,50,51,52,53,54,55,56,57,58,59,60,61,62,63,64,65,66,67,68,69,70,71,72]
W = re.compile(r'[^\W\d_]+')
TXT = {}
def words(lang, b, c, v):
    k = (lang, b)
    if k not in TXT: TXT[k] = json.load(open(f"{D}../../text/{'la' if lang == 'la' else lang}{(LAIDX[b] if lang == 'la' else b):02d}.json", encoding='utf-8'))
    try: return W.findall(TXT[k][c-1][v-1] or '')
    except IndexError: return []
def by_sound(en, refs, lang):
    """the word in the translation's verses that sounds most like the English name"""
    R = refs[:40]
    if not R: return ''
    from collections import Counter
    cov = Counter()
    for b, c, v in R:
        ws = words(lang, b, c, v)
        cov.update({w[:k] for w in ws for k in range(1, len(w) + 1)} if lang == 'ko' else set(ws) | {ws[j] + '-' + ws[j+1] for j in range(len(ws) - 1) if ws[j][:1].isupper() and ws[j+1][:1].isupper()})
    target = key_lat(en); best, bs = '', 0
    for w, n in cov.items():
        if lang == 'ko' and len(w) > 8: continue
        if lang != 'ko' and not w[:1].isupper(): continue
        sc = sim(key_ko(w) if lang == 'ko' else key_lat(w), target) + 0.35 * n / len(R)
        if lang == 'ko': sc -= 0.02 * max(0, len(w) - len(en) // 2)
        if sc > bs: best, bs = w, sc
    return best if bs >= (0.6 if lang == 'ko' else 0.75) else ''

# names in the translations: what the translation renders the Strong's number as, if it sounds like the name;
# otherwise the word in the person's verses that sounds most like it
OX = {}
for s in range(4): OX.update(json.load(open(f'{D}ox{s}.json', encoding='utf-8')))
def rendered(ds, lang):
    e = OX.get(ds)
    r = e and e.get('r', {}).get(lang)
    return r[0][0] if r else ''

def ids(field):
    out = []
    for part in re.split(r',|\+', field or ''):
        part = part.strip()
        if part in uniq: out.append(uniq[part])
    return out

from ko_names import ko_bare as _ko_bare
def ko_bare(nm, en): return _ko_bare(nm, en, f'{D}../../text', sim, key_ko, key_lat)

def by_script(dss, k):
    """Chinese and Japanese names (from the person's main word only: a TIPNR record can list other words too):
    the main rendering of the name's own words when it is in the script names take
    (katakana in Japanese, characters in Chinese) and is most of what the word is rendered as"""
    best, bn = '', 0
    for d in dss:
        r = OX.get(d, {}).get('r', {}).get(k) or []
        tot = sum(n for _, n in r)
        if not r or r[0][1] < max(2, tot * 0.5): continue
        w = r[0][0]
        ok = all('\u30a1' <= ch <= '\u30fa' or ch in 'ー・' for ch in w) if k == 'ja' else all('\u4e00' <= ch <= '\u9fff' for ch in w)
        if k == 'zh' and any(ch in '人那王神主子民' for ch in w): ok = False      # 那人 ("the man") for Adam
        if ok and 1 <= len(w) <= 8 and r[0][1] > bn: best, bn = w, r[0][1]
    return best

index, names = {}, {}
shards = [{}]
for n, (pid, r) in enumerate(sorted(P.items())):
    for ds in r['dss']: index.setdefault(ds, pid)
    en = r['un'].split('@')[0].split('|')[-1]
    # the main word: the commonest of those listed under the person's own name (Judah's record also lists "David =ESV,MT")
    own = [d for nm_, _f, d in r['nm'] if nm_.split(' ')[0].split('=')[0].strip().lower() == en.lower()] or r['dss']
    main = max(own, key=lambda d: (OX.get(d, {}).get('cc', [0])[0]))
    refs0 = sorted(set(r['refs']))
    def nm_in(k):
        cands = [w for d in r['dss'] for w, _n in (OX.get(d, {}).get('r', {}).get(k) or [])[:3]]
        scored = [(sim(key_ko(w) if k == 'ko' else key_lat(w), key_lat(en)), w) for w in cands if ' ' not in w]
        good = [w for sc, w in sorted(scored, reverse=True) if sc >= (0.55 if k == 'ko' else 0.7)]
        if good: return good[0]
        r0 = OX.get(main, {}).get('r', {}).get(k) or []          # Gesù for Jesus: not alike in sound, but what the word is rendered as
        if r0 and r0[0][0][:1].isupper() and ' ' not in r0[0][0] and r0[0][1] >= max(3, 0.6 * sum(n for _, n in r0)) \
           and sim(key_lat(r0[0][0]), key_lat(en)) >= 0.4: return r0[0][0]       # (not Josua for Nun, "Josua, der Sohn Nuns")
        return by_sound(en, refs0, k)
    names[pid] = [en] + [ko_bare(nm_in('ko'), en)] + [nm_in(k) for k in ('la', 'de', 'fr')] + [next((f for _, f, d in r['nm'] if d == main), r['nm'][0][1])] + [nm_in(k) for k in ('es', 'pt', 'it', 'id')] + [by_script([main], k) for k in ('ja', 'zh')]
    refs = sorted(set(r['refs']))
    pick = refs if len(refs) <= CAP else [refs[round(j * (len(refs) - 1) / (CAP - 1))] for j in range(CAP)]
    e = {'t': r['t'], 'ds': r['ds'], 'nm': r['nm'], 'cc': [len(refs), ''.join(b36(b) + b36(c) + b36(v) for b, c, v in pick)]}
    for k in ('b', 's', 'a'):
        if r.get(k): e[k] = r[k]
    for k in ('par', 'sib', 'pt', 'off'):
        v = ids(r[k])
        if v: e[k] = v
    if r['tr']: e['tr'] = r['tr']
    shards[0][pid] = e

# Matthew 1's genealogy ("X ἐγέννησεν τὸν Y"): where TIPNR gives no line between the two at all (Matthan and
# Jacob, the father of Joseph), keep it as a line of descent "ln" (used for ancestors and descendants only; it is not
# always a father: Matthew skips generations)
PP = shards[0]
def up_of(x): return set(PP.get(x, {}).get('par', [])) | {y for y in PP if x in PP[y].get('off', [])} | set(PP.get(x, {}).get('ln', []))
def has_line(child, anc, depth=6):
    fr, seen = {child}, {child}
    for _ in range(depth):
        fr = {y for x in fr for y in up_of(x)} - seen
        if anc in fr: return True
        seen |= fr
    return False
mt = json.load(open(f'{D}al39.json', encoding='utf-8'))['ow'][0]
added = []
for v in range(2, 17):
    t = [x.split('|') for x in (mt[v-1] or '').split()]
    for i, x in enumerate(t):
        if x[0] != 'G1080': continue
        su = next((t[j][0] for j in range(i - 1, -1, -1) if t[j][1].startswith('N-NSM-P')), None)
        ob = next((t[j][0] for j in range(i + 1, len(t)) if t[j][1].startswith('N-ASM-P')), None)
        a, c = index.get(su), index.get(ob)
        if a and c and a != c and c in PP and not has_line(c, a):
            PP[c].setdefault('ln', []).append(a); added.append((names[a][0], names[c][0]))
print('Matthew 1 lines added', added, file=sys.stderr)
json.dump({'d': index, 'n': names}, open(f'{D}pi.json', 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
json.dump(shards[0], open(f'{D}pp.json', 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
print('people', len(P), 'dStrongs', len(index), 'sizes KB', os.path.getsize(f'{D}pi.json') // 1024,
      os.path.getsize(f'{D}pp.json') // 1024, file=sys.stderr)
