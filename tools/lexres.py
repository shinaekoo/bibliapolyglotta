"""Lexical resources for the word links (all allow any use, commercial included):

  Princeton WordNet 3.0 (WordNet 3.0 license, any purpose with the copyright notice) — English synonyms,
      so that STEPBible's modern gloss ("emptiness", "authority") meets the KJV's word ("void", "power").
      WN_DIR = folder with data.noun, data.verb, data.adj, data.adv and *.exc (nltk_data corpora/wordnet).
  UniDic (unidic-mecab, UniDic Consortium; GPL/LGPL/BSD, here under BSD) — the dictionary form of a Japanese
      word ("愛して" -> 愛する, "わたし" -> 私), so that forms of one word count together.
      UNIDIC_LEX = lex.csv(.gz) of unidic-mecab.
Both are optional: without the environment variable the function falls back to plain matching.
"""
import gzip, os, re
from collections import defaultdict

# ---------------- WordNet ----------------
_WN = None
def _load_wn():
    global _WN
    d = os.environ.get('WN_DIR')
    if not d: _WN = False; return
    syn = defaultdict(set)          # lemma -> synset ids
    members = {}                    # synset id -> lemmas
    for pos in ('noun', 'verb', 'adj', 'adv'):
        for line in open(os.path.join(d, 'data.' + pos), encoding='latin-1'):
            if line.startswith('  '): continue
            p = line.split(' ')
            sid = pos[0] + p[0]; n = int(p[3], 16)
            ws = [p[4 + 2 * i].lower().replace('_', ' ') for i in range(n)]
            ws = [re.sub(r'\(.*\)$', '', w) for w in ws]
            members[sid] = set(ws)
            for w in ws: syn[w].add(sid)
    exc = defaultdict(set)
    for pos in ('noun', 'verb', 'adj', 'adv'):
        for line in open(os.path.join(d, pos + '.exc'), encoding='latin-1'):
            x = line.split()
            if len(x) >= 2: exc[x[0]].update(x[1:])
    _WN = (syn, members, exc)
RULES = [('ies', 'y'), ('ses', 's'), ('xes', 'x'), ('zes', 'z'), ('ches', 'ch'), ('shes', 'sh'), ('men', 'man'), ('s', ''),
         ('ied', 'y'), ('ed', 'e'), ('ed', ''), ('ing', 'e'), ('ing', ''), ('eth', 'e'), ('eth', ''), ('est', 'e'), ('est', ''),
         ('edst', 'e'), ('edst', ''), ('er', ''), ('er', 'e')]
def lemmas(w):
    """WordNet base forms of an English word, KJV endings (-eth, -est) included"""
    if _WN is None: _load_wn()
    if not _WN: return {w}
    syn, _, exc = _WN
    w = w.lower(); out = {w} | exc.get(w, set())
    for a, b in RULES:
        if w.endswith(a) and len(w) - len(a) >= 2:
            c = w[:-len(a)] + b
            if c in syn: out.add(c)
            if a in ('ed', 'ing', 'eth', 'est', 'edst', 'er') and len(c) >= 3 and c[-1] == c[-2] and c[:-1] in syn: out.add(c[:-1])   # "planned"
    return {x for x in out if x in syn} or {w}
def is_noun(w):
    if _WN is None: _load_wn()
    return bool(_WN) and any(x.startswith('n') for x in _WN[0].get(w.lower(), ()))
_REL = {}
def related(a, b):
    """True when two English words share a WordNet synset (are synonyms in one of their senses)"""
    if _WN is None: _load_wn()
    if not _WN: return False
    k = (a, b) if a < b else (b, a)
    if k in _REL: return _REL[k]
    syn = _WN[0]
    sa = set().union(*(syn.get(x, set()) for x in lemmas(a))); sb = set().union(*(syn.get(x, set()) for x in lemmas(b)))
    r = bool(sa & sb); _REL[k] = r
    return r

# ---------------- UniDic ----------------
_UD = None
CONTENT = ('名詞', '動詞', '形容詞', '形状詞', '副詞', '代名詞', '連体詞')
def _load_ud():
    global _UD
    f = os.environ.get('UNIDIC_LEX')
    if not f: _UD = False; return
    best = {}
    op = gzip.open if f.endswith('.gz') else open
    with op(f, 'rt', encoding='utf-8') as fh:
        for line in fh:
            x = line.rstrip('\n').split(',')
            if len(x) < 12 or x[4] not in CONTENT: continue
            s, cost, lem = x[0], int(x[3]), x[11]
            if s not in best or cost < best[s][0]: best[s] = (cost, lem)
    _UD = ({s: l for s, (c, l) in best.items()}, max(len(s) for s in best))
def ja_lemma(chunk):
    """dictionary form of the content word at the start of a Japanese phrase, or None"""
    if _UD is None: _load_ud()
    if not _UD: return None
    d, mx = _UD
    for n in range(min(len(chunk), mx), 0, -1):
        l = d.get(chunk[:n])
        if l: return re.sub(r'-.*$', '', l)
    return None
