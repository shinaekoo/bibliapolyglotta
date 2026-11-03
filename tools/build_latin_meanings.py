"""Meanings of Latin dictionary words in the app's languages -> 6th column of web/data/lxL.json

For every Latin word on screen (data/al*.json "lx"), the words of the KJV, 개역한글, Luther, Segond and the other app-language translations linked
to it in that verse (Latin -> KJV -> other translation, the links of tools/align_original.py) are counted per
dictionary word, then grouped under headwords by tools/meanings.py: {"ko": [...], "en": [...], ...} for each app language (meanings.UI).
Run after tools/build_latin.py.  usage: WN_DIR=... python3 tools/build_latin_meanings.py
"""
import json, os, re, sys
from collections import Counter, defaultdict
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import meanings
from langnorm import suf, es_n, pt_n, it_n, id_n, ja_n, zh_n
TX = os.path.join(HERE, '..', 'text') + '/'; D = os.path.join(HERE, '..', 'web', 'data') + '/'
W = re.compile(r'[^\W\d_]+')
PS = 18
KO_SUF = sorted('께서는 께서 에게서 에게는 에게 으로써 으로서 으로는 으로 로써 로서 로는 에서는 에서 에는 에도 이여 은 는 이 가 을 를 의 도 만 에 로 과 와'.split(), key=len, reverse=True)
def ko_key(w):
    for e in KO_SUF:
        if w.endswith(e) and len(w) - len(e) >= 1: return w[:-len(e)]
    return w
KEY = {'ko': ko_key, 'en': lambda w: w.lower(), 'de': suf(['ern', 'em', 'en', 'er', 'es', 'e', 'n', 's', 'st', 't']),
       'fr': suf(['aient', 'ait', 'ent', 'ez', 'ons', 'ées', 'és', 'ée', 'é', 'er', 'es', 's', 'x', 'e']),
       'zh': lambda w: w, 'ja': lambda w: w, 'es': es_n, 'pt': pt_n, 'it': it_n, 'id': id_n}
LANGS = list(meanings.UI)
cnt = defaultdict(lambda: defaultdict(Counter))      # lemma -> lang -> key -> n
surf = defaultdict(Counter)                          # (lang, key) -> surface forms
for b in range(66):
    al = json.load(open(f'{D}al{b:02d}.json'))
    tx = {k: json.load(open(f'{TX}{k}{b:02d}.json', encoding='utf-8')) for k in LANGS}
    for c, chap in enumerate(al['v'], 1):
        lx = al.get('lx', {}).get(str(c), {})
        lanes = {k: (tx[k][c-1] if c <= len(tx[k]) else []) for k in LANGS}
        if b == PS:     # German counts psalm titles as verses, like the Latin: the same shift as the app
            ref = len(lanes['ko']) or len(lanes['en'])
            G = lanes['de']; lanes['de'] = G[max(0, min(3, len(G) - ref)):]
        for v, rec in enumerate(chap, 1):
            toks = lx.get(f'v{v}')
            if not toks or 'la' not in rec: continue
            la2en = defaultdict(set); p = rec['la']
            for i in range(0, len(p), 2): la2en[p[i]].add(p[i+1])
            e2 = {}
            for k in LANGS:
                if k == 'en': continue
                q = rec.get(k, []); m = defaultdict(set)
                for i in range(0, len(q), 2): m[q[i+1]].add(q[i])
                e2[k] = m
            words = {k: W.findall((lanes[k][v-1] if v <= len(lanes[k]) else '') or '') for k in LANGS}
            for i, t in enumerate(toks):
                lem = t[0]; ens = la2en.get(i)
                if not ens: continue
                for k in LANGS:
                    xs = sorted(ens) if k == 'en' else sorted({x for j in ens for x in e2[k].get(j, ())})
                    seen = set()
                    for x in xs:
                        if x >= len(words[k]): continue
                        w = words[k][x]
                        if k == 'ja': w = ja_n(w)              # "神は" -> 神, "愛して" -> 愛する
                        elif k == 'zh': w = zh_n(w)
                        key = KEY[k](w)
                        if key in seen: continue
                        seen.add(key); cnt[lem][k][key] += 1; surf[(k, key)][w] += 1
L = json.load(open(D + 'lxL.json', encoding='utf-8'))
n = 0
for i, row in enumerate(L):
    if not row: continue
    while len(row) < 6: row.append('')
    m = {}
    if row[3] in ('PRON', 'CONJ', 'PREP', 'INTERJ', 'PACK'): row[4] = ''; row[5] = ''; continue   # little words: no meaning of their own
    for k in LANGS:
        g = cnt.get(i, {}).get(k)
        if g:
            h = meanings.headwords(k, [(c, surf[(k, key)]) for key, c in g.items()])
            if h: m[k] = h
    row[4] = ''                      # (was the Lewis & Short key)
    row[5] = m or ''
    n += bool(m)
json.dump(L, open(D + 'lxL.json', 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
print('lemmas', len(L), 'with meanings', n, 'KB', os.path.getsize(D + 'lxL.json') // 1024, file=sys.stderr)
