"""Minimal Python re-implementation of Whitaker's WORDS stem+ending analysis."""
import re
from collections import defaultdict
WW = '/tmp/claude-0/ww/'

def nz(s):
    return s.lower().replace('æ', 'ae').replace('œ', 'oe').replace('j', 'i').replace('v', 'u')

DLINE = re.compile(r'^(.{19})(.{19})(.{19})(.{19})(\S+)\s+(.*?)\s+([A-Z]) ([A-Z]) ([A-Z]) ([A-Z]) ([A-Z]) (.*)$')
ENTRIES = []          # list of dict
STEMS = defaultdict(list)   # (normalized stem) -> [(entry_idx, key)]
prev = None
for ln in open(WW + 'DICTLINE.GEN', encoding='latin-1'):
    ln = ln.rstrip('\n')
    m = DLINE.match(ln.ljust(120))
    if not m:
        continue
    stems = [m.group(i).strip() for i in range(1, 5)]
    stems = ['' if x == '.' else x for x in stems]
    raw_dot = [m.group(i).strip() == '.' for i in range(1, 5)]
    pos = m.group(5)
    info = m.group(6).split()
    mean = m.group(12).strip()
    sig = (tuple(stems), pos, tuple(info))
    if prev and prev['sig'] == sig:      # continuation lines of the same entry
        prev['mean'] += ' ' + mean.lstrip('|')
        continue
    e = {'sig': sig, 'stems': stems, 'pos': pos, 'info': info, 'mean': mean,
         'age': m.group(7), 'freq': m.group(10)}
    ENTRIES.append(e); prev = e
    idx = len(ENTRIES) - 1
    for k, s in enumerate(stems, 1):
        if (s and s != 'zzz') or raw_dot[k-1]:
            STEMS[nz(s)].append((idx, k))
    if pos in ('ADV', 'PREP', 'CONJ', 'INTERJ') and stems[0]:
        pass

# 'sum, esse' is built into the WORDS program rather than DICTLINE
ENTRIES.append({'sig': None, 'stems': ['s', '', 'fu', 'fut'], 'pos': 'V', 'info': ['5', '1', 'TO_BEING'],
                'mean': 'be; exist; (also used to form verb perfect passive tenses) with NOM PERF PPL', 'age': 'X', 'freq': 'A'})
for k, st in enumerate(['s', '', 'fu', 'fut'], 1):
    STEMS[st].append((len(ENTRIES) - 1, k))

INFL = defaultdict(list)   # ending -> list of dict
for ln in open(WW + 'INFLECTS.LAT', encoding='latin-1'):
    ln = ln.split('--')[0].strip()
    if not ln:
        continue
    t = ln.split()
    pos = t[0]
    if t[-3].isdigit():
        end, ln_, key, gram = '', t[-3], t[-4], t[3:-4]
    else:
        end, ln_, key, gram = t[-3], t[-4], t[-5], t[3:-5]
    try:
        which, var = int(t[1]), int(t[2])
    except ValueError:
        which, var, gram = 0, 0, t[1:-4] if not end else t[1:-5]
    INFL[nz(end)].append({'pos': pos, 'which': which, 'var': var, 'gram': gram,
                         'key': int(key), 'end': end, 'age': t[-2], 'freq': t[-1]})

UNIQ = {}
lines = [l.rstrip('\n') for l in open(WW + 'UNIQUES.LAT', encoding='latin-1')]
for i in range(0, len(lines) - 2, 3):
    UNIQ.setdefault(nz(lines[i].strip()), []).append({'pos_line': lines[i + 1].strip(), 'mean': lines[i + 2].strip()})

DPOS = {'N': ('N',), 'ADJ': ('ADJ',), 'V': ('V',), 'VPAR': ('V',), 'SUPINE': ('V',),
        'PRON': ('PRON', 'PACK'), 'NUM': ('NUM',), 'ADV': ('ADV',)}

def entry_wv(e):
    i = e['info']
    try:
        return int(i[0]), int(i[1])
    except (ValueError, IndexError):
        return None, None

def gender_ok(ig, dg):
    return ig in ('X', 'C') or ig == dg or (dg == 'C' and ig in ('M', 'F'))

def analyze(word):
    w = nz(word)
    out = []
    for u in UNIQ.get(w, []):
        out.append({'kind': 'unique', 'form': word, 'pos_line': u['pos_line'], 'mean': u['mean']})
    # map normalized positions back to the original spelling (æ -> ae is two letters)
    pos_map = []
    for i, ch in enumerate(word):
        pos_map += [i] * len(nz(ch))
    pos_map.append(len(word))
    def orig(a, b):
        return word[pos_map[a]:pos_map[b]] if a < b else ''
    for cut in range(0, min(len(w), 9) + 1):
        end = w[len(w) - cut:] if cut else ''
        stem = w[:len(w) - cut]
        for inf in INFL.get(end, []):
            for idx, key in STEMS.get(stem, []):
                e = ENTRIES[idx]
                if e['pos'] not in DPOS.get(inf['pos'], ()):
                    continue
                if inf['key'] != key:
                    continue
                dw, dv = entry_wv(e)
                if inf['pos'] in ('N', 'ADJ', 'V', 'VPAR', 'SUPINE', 'PRON', 'NUM'):
                    if dw is None:
                        continue
                    if inf['which'] not in (0, dw) or inf['var'] not in (0, dv):
                        continue
                if inf['pos'] == 'N' and len(e['info']) > 2 and len(inf['gram']) >= 3 and not gender_ok(inf['gram'][2], e['info'][2]):
                    continue
                out.append({'kind': 'infl', 'idx': idx, 'key': inf['key'], 'ifreq': inf['freq'], 'stem': orig(0, len(w) - cut),
                            'ending': orig(len(w) - cut, len(w)), 'ipos': inf['pos'], 'gram': inf['gram'],
                            'mean': e['mean'], 'dpos': e['pos'], 'info': e['info'], 'stems': e['stems']})
    # invariant words (prep, conj, adv, interj)
    for idx, key in STEMS.get(w, []):
        e = ENTRIES[idx]
        if e['pos'] in ('PREP', 'CONJ', 'INTERJ', 'ADV') and key == 1:
            out.append({'kind': 'inv', 'idx': idx, 'stem': word, 'ending': '', 'ipos': e['pos'], 'gram': e['info'],
                        'mean': e['mean'], 'dpos': e['pos'], 'info': e['info'], 'stems': e['stems']})
    # enclitic -que / -ne / -ve
    if not out:
        for enc in ('que', 'ne', 've'):
            if w.endswith(enc) and len(w) > len(enc) + 1:
                sub = analyze(word[:-len(enc)])
                for s in sub:
                    s = dict(s); s['enclitic'] = word[-len(enc):]
                    out.append(s)
                if sub:
                    break
    # dedupe
    seen = set(); res = []
    for o in out:
        k = (o.get('idx'), o.get('stem'), o.get('ending'), tuple(o.get('gram', ())), o.get('kind'))
        if k in seen:
            continue
        seen.add(k); res.append(o)
    return res

if __name__ == '__main__':
    import sys
    for w in sys.argv[1:]:
        for a in analyze(w):
            print(w, '|', a.get('stem'), '+', a.get('ending'), a.get('ipos'), ' '.join(a.get('gram', [])) if a['kind'] != 'unique' else a['pos_line'], '|', a['mean'][:70])
        print()
