"""Names of people and places linked by their sound (run after tools/align_original.py and tools/fix_jehovah.py,
before tools/build_orig_lex.py; then build_persons, build_geo, build_orig_lex again for the renderings).

The statistical alignment links rare words badly: 엘고스 (Elkoshite) came out as "Nahum" in Nahum 1:1, and 나훔의
was left unlinked. Names need no statistics: for every Hebrew/Greek word that is a person or a place (TIPNR, in
web/data/pi.json, gi.json), we know what the name looks like in each language (the names there, and the commonest
renderings of the word in web/data/ox*.json). So in each verse:

  1. the KJV: the word(s) spelled like the English name take the original word's link ("The" of "the Elkoshite" is
     dropped); when a name occurs twice, the n-th original occurrence goes with the n-th English one
  2. each translation: the word that starts with, or sounds like, the name in that language is linked to those
     English words, and every other link to them, or from that word to other English words, is removed

Where the KJV renders the name by other words (Adam as "the man"), both steps are skipped. Where a translation does
not have the name (Korean often says 그가), only its wrong links to another name or to a number are dropped.
usage: python3 tools/fix_names.py          (rewrites web/data/al*.json; prints how many links changed)
"""
import json, os, re, sys, difflib, unicodedata
from collections import defaultdict, Counter
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
D = os.path.join(HERE, '..', 'web', 'data') + '/'; TX = os.path.join(HERE, '..', 'text') + '/'
W = re.compile(r'[^\W\d_]+')
LAIDX = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,18,19,20,21,22,23,26,27,28,30,31,32,33,34,35,36,37,38,39,40,41,42,43,46,47,48,49,50,51,52,53,54,55,56,57,58,59,60,61,62,63,64,65,66,67,68,69,70,71,72]
LANGS = ['la', 'de', 'fr', 'ko', 'zh', 'es', 'it', 'ru', 'ja', 'pt', 'tl', 'ceb', 'id', 'ig']
NIX = {'ko': 1, 'la': 2, 'de': 3, 'fr': 4, 'es': 6, 'pt': 7, 'it': 8, 'id': 9, 'ja': 10, 'zh': 11}   # pi/gi name columns

# ---- sound keys (as in build_persons.py) ----
CHO = ['g','kk','n','d','tt','r','m','b','pp','s','ss','','j','jj','ch','k','t','p','h']
JUNG = ['a','ae','ya','yae','eo','e','yeo','ye','o','wa','wae','oe','yo','u','wo','we','wi','yu','eu','ui','i']
JONG = ['','k','k','k','n','n','n','t','l','k','m','l','l','l','p','l','m','p','p','t','t','ng','t','t','k','t','p','t']
def key_ko(s):
    r = ''.join(CHO[(ord(ch) - 0xAC00) // 588] + JUNG[((ord(ch) - 0xAC00) % 588) // 28] + JONG[(ord(ch) - 0xAC00) % 28]
                for ch in s if 0 <= ord(ch) - 0xAC00 < 11172)
    for a, b in (('eo', 'o'), ('eu', ''), ('ae', 'e'), ('oe', 'e'), ('ya', 'ia'), ('yo', 'io'), ('yu', 'iu'), ('ye', 'ie'), ('ng', 'n'), ('ch', 's'), ('j', 's'), ('kk', 'k'), ('tt', 't'), ('pp', 'p'), ('ss', 's')):
        r = r.replace(a, b)
    return r.translate(str.maketrans('gdbr', 'ktpl')).replace('h', '')
def key_lat(s):
    s = ''.join(c for c in unicodedata.normalize('NFD', s) if not unicodedata.combining(c)).replace('æ', 'ae').replace('œ', 'oe')
    r = s.lower().replace('-', '').replace(' ', '')
    for a, b in (('th', 't'), ('ph', 'p'), ('ch', 'k'), ('sh', 's'), ('ck', 'k'), ('qu', 'k'), ('x', 'ks'), ('j', 'i'), ('y', 'i'), ('ee', 'e'), ('oo', 'u')):
        r = r.replace(a, b)
    r = r.translate(str.maketrans('cqzvfwgdbr', 'kksbpuktpl'))
    return re.sub(r'(.)\1', r'\1', r).replace('h', '')
def sim(a, b): return difflib.SequenceMatcher(None, a, b).ratio() if a and b else 0

def fold(s): return ''.join(c for c in unicodedata.normalize('NFD', s.lower()) if not unicodedata.combining(c))

def matches(lang, w, names):
    """does word w (as written in the verse) carry one of the names?"""
    if not w: return False
    if lang == 'ko':
        return any(len(n) >= 1 and w.startswith(n) and (len(n) >= 2 or len(w) <= len(n) + 2) for n in names)
    if lang == 'ja':
        return any(w.startswith(n) for n in names if len(n) >= 2)
    if lang == 'zh':
        return any(n in w for n in names if len(n) >= 2) or any(w == n for n in names)
    if lang == 'ru':
        return any(fold(w).startswith(fold(n)[:max(3, len(n) - 2)]) and abs(len(w) - len(n)) <= 3 for n in names if len(n) >= 3)
    if not w[:1].isupper(): return False
    fw = fold(w)
    for n in names:
        fn = fold(n)
        if len(fn) >= 3 and fw.startswith(fn[:max(3, len(fn) - 2)]) and abs(len(fw) - len(fn)) <= 3: return True   # Moyses, Moysi
        if sim(key_lat(w), key_lat(n)) >= 0.8: return True
    return False

# ---- names: people and places, and their commonest renderings ----
PI = json.load(open(D + 'pi.json', encoding='utf-8')); GI = json.load(open(D + 'gi.json', encoding='utf-8'))
PP = json.load(open(D + 'pp.json', encoding='utf-8')); GP = json.load(open(D + 'gp.json', encoding='utf-8'))
WHO = {}
for idx, recs in ((PI, PP), (GI, GP)):
    for ds, pid in idx['d'].items():
        # only the words listed under the person's or place's own name: Jesus's record also lists "Christ", Judah's
        # "Jew" and "David"; those are other words, not this name
        en = idx['n'][pid][0].split('_')[0].lower()
        own = any(x[2] == ds and x[0].split(' ')[0].split('=')[0].strip().lower() == en for x in recs.get(pid, {}).get('nm', []))
        if own: WHO.setdefault(ds, idx['n'][pid])
OX = {}
for s in range(4): OX.update(json.load(open(f'{D}ox{s}.json', encoding='utf-8')))
def names_of(ds, lang):
    """(the name in pi/gi.json, the other common renderings of the word) in that language"""
    n = WHO[ds]; prim = set(); out = set()
    if lang in NIX and len(n) > NIX[lang] and n[NIX[lang]]: prim.add(n[NIX[lang]])
    r = OX.get(ds, {}).get('r', {}).get(lang) or []
    tot = sum(c for _, c in r)
    for w, c in r[:3]:
        if c >= 2 and c >= tot * 0.15 and ' ' not in w and (lang in ('ko', 'ja', 'zh', 'ru') or w[:1].isupper()):
            if lang == 'ko' and len(w) < 2: continue
            out.add(w)
    if lang == 'ko': out = {re.sub(r'(이|가|은|는|을|를|의|과|와|에게)$', '', w) if len(w) > 2 else w for w in out}
    return {w for w in prim if w}, {w for w in out if w} - prim

KO_TAIL = re.compile(r'(이|가|은|는|을|를|의|과|와|에게|에게서|에서|에|로|으로|이라|라|이요|요|이며|며|야|아|여|이여|더라|였더라|이었더라|도|만|까지|부터|께서|께)?$')
def score(lang, w, prim, rend):
    """how surely word w carries the name: 0 none; the pi/gi name counts more than a rendering, a word that is the
    name plus a particle more than one that only starts with it"""
    best = 0
    for names, base in ((prim, 2.0), (rend, 1.0)):
        for n in names:
            if not matches(lang, w, {n}): continue
            sc = base + min(len(n), 8) / 10
            if lang == 'ko' and KO_TAIL.fullmatch(w[len(n):]): sc += 0.5
            elif lang not in ('ko', 'ja', 'zh') and fold(w) == fold(n): sc += 0.5
            best = max(best, sc)
    return best

KO_NUM = set('일이삼사오육칠팔구십백천만')
NUM = defaultdict(lambda: (lambda w: False))
NUM['ko'] = lambda w: len(w) >= 2 and all(ch in KO_NUM for ch in re.sub(r'(세|년|명|인|이요|이며|이라|에|을|를|은|는)$', '', w))
NUM['de'] = lambda w: bool(re.fullmatch(r'(ein|zwei|drei|vier|fünf|fünz|sechs|sieben|acht|neun|zehn|zwanzig|dreißig|vierzig|fünfzig|sechzig|siebzig|achtzig|neunzig|hundert|tausend|und|zig)+(e|en|er|es)?', w.lower())) and len(w) > 6

def load(pre, i): return json.load(open(f'{TX}{pre}{i:02d}.json', encoding='utf-8'))
def pairs(p): return [(p[i], p[i+1]) for i in range(0, len(p), 2)]
def flat(ps): return [x for pr in sorted(set(ps)) for x in pr]

stat = Counter()
for b in range(66):
    fn = f'{D}al{b:02d}.json'; al = json.load(open(fn, encoding='utf-8'))
    tx = {k: load(k, b) for k in ['en'] + [l for l in LANGS if l != 'la']}
    la = load('la', LAIDX[b])
    for c in range(1, len(al['v']) + 1):
        lanes = {k: (tx[k][c-1] if c <= len(tx[k]) else []) for k in tx}
        # tools/verse_map.py has already put the Latin and German texts on the KJV grid, so the psalm
        # and Daniel shifts that used to sit here are gone. A chapter's verses past the KJV's own are the
        # Vulgate's alone (Daniel 3's Song of the Three, Esther 10's additions) and have nothing to link to.
        lanes['la'] = (la[c-1] if c <= len(la) else [])[:len(lanes['en'])]
        for v in range(1, len(al['v'][c-1]) + 1):
            ow = (al['ow'][c-1][v-1] or '').split()
            rec = al['v'][c-1][v-1]
            words = {k: W.findall((lanes[k][v-1] if v <= len(lanes[k]) else '') or '') for k in lanes}
            en = words['en']
            hits = [(i, w.split('|')[0]) for i, w in enumerate(ow) if w.split('|')[0] in WHO]
            if not hits: continue
            OR = pairs(rec.get('or', []))
            # --- 1. the KJV side
            used_en = defaultdict(int)
            name_en = {}                      # original position -> English positions of the name
            name_ok = set()                   # ... where the KJV spells the name
            ecands = []
            for i, ds in hits:
                ename = WHO[ds][0].split('_')[0]
                k = sum(1 for i2, d2 in hits if d2 == ds and i2 < i)            # n-th occurrence of this word
                cand = [j for j, w in enumerate(en) if w[:1].isupper() and (fold(w).startswith(fold(ename)[:max(3, len(ename) - 1)]) or sim(key_lat(w), key_lat(ename)) >= 0.75)]
                for r_, j in enumerate(cand):
                    ecands.append((sim(key_lat(en[j]), key_lat(ename)) + (0.5 if fold(en[j]) == fold(ename) else 0) - 0.01 * abs(r_ - k), i, j))
            ecands.sort(reverse=True); eg, eu = {}, set()
            for sc, i, j in ecands:
                if i in eg or j in eu: continue
                eg[i] = j; eu.add(j)
            for i, ds in hits:
                if i in eg:
                    js = [eg[i]]
                    old = {j for o, j in OR if o == i}
                    if set(js) != old:
                        # keep the words around it that belong to the name itself (Tubal-cain: two words), drop "The", "of"
                        OR = [(o, j) for o, j in OR if o != i] + [(i, j) for j in js]
                        stat['en'] += 1
                    name_en[i] = js
                    name_ok.add(i)
                else:
                    name_en[i] = sorted({j for o, j in OR if o == i})
            rec['or'] = flat(OR)
            # --- 2. each translation
            for lang in LANGS:
                if lang not in rec and not words.get(lang): continue
                ws = words.get(lang) or []
                P = pairs(rec.get(lang, []))
                changed = False
                done_x = set()
                # every (name, word) pair that fits, best first; each word goes to one name, each name to one word,
                # the n-th occurrence of a name preferring the n-th word that carries it
                cands = []
                for i, ds in hits:
                    prim, rend = names_of(ds, lang)
                    if not (prim or rend): continue
                    k = sum(1 for i2, d2 in hits if d2 == ds and i2 < i)
                    xs = [(score(lang, w, prim, rend), x) for x, w in enumerate(ws)]
                    xs = [(sc, x) for sc, x in xs if sc > 0]
                    for r_, (sc, x) in enumerate(sorted(xs, key=lambda t: t[1])):
                        cands.append((sc - 0.01 * abs(r_ - k), i, x))
                cands.sort(reverse=True)
                got, used = {}, set()
                for sc, i, x in cands:
                    if i in got or x in used: continue
                    got[i] = x; used.add(x)
                anywhere = {x for _, _, x in cands}
                for i, ds in hits:
                    js = name_en.get(i)
                    if not js or i not in name_ok: continue      # the KJV does not spell the name here (Adam: "the man")
                    if i not in got:
                        # the name is not in this verse (Korean often says 그가 for it): still drop links of its English
                        # word to another name or to a number (므드사엘 for Mehujael, 구백오 for Enos)
                        bad = {(a, j) for a, j in P if j in js and a < len(ws) and (a in anywhere or NUM[lang](ws[a]))}
                        if bad: P = [pr for pr in P if pr not in bad]; changed = True; stat[lang + '_dropped'] += len(bad)
                        stat[lang + '_notfound'] += 1; continue
                    x = got[i]
                    cur = {(a, j) for a, j in P if a == x or j in js}
                    want = {(x, j) for j in js}
                    if cur != want:
                        P = [(a, j) for a, j in P if a != x and j not in js] + sorted(want)
                        changed = True; stat[lang] += 1
                    else: stat[lang + '_same'] += 1
                if changed: rec[lang] = flat(P)
    json.dump(al, open(fn, 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
print('links changed', dict(sorted(stat.items())), file=sys.stderr)
