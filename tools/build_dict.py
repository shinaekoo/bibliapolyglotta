"""Bible dictionaries for people, places and the other named things
-> web/data/dp.json (people), dg.json (places), do.json (gods, angels, months, musical terms)

Sources (public domain, as parsed by NEUU bible-dictionary-dataset, CC BY 4.0, from CCEL):
  EAS Easton's Bible Dictionary (1897) · SMI Smith's Bible Dictionary (1863) ·
  HAS Hastings-type dictionary text on CCEL (1909) · SCH Schaff's Dictionary of the Bible (1880;
      much of it the same text as HAS on CCEL, so it is kept only where it differs) ·
  HIT Hitchcock's Bible Names (1869, meanings)

Each person/place (from pi.json / gi.json and their records) gets
  {"m": [[name, meaning], ...],              Hitchcock's meaning of each of its names
   "d": [[source, text, [[start, end, b, c, v], ...]], ...]}   dictionary text with clickable references
A headword can cover several people or places with the same name. The entry (or the numbered
sense inside it) is chosen by the verses it cites: the one sharing most verses with the person or
place wins; with no shared verse an entry is used only when it is the only one with that name.
usage: python3 tools/build_dict.py NEUU_DATASET_DIR STEP_DIR
"""
import json, os, re, sys, glob
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
D = os.path.join(HERE, '..', 'web', 'data') + '/'
SRC, STEP = sys.argv[1], sys.argv[2]
SC = 'Gen Exo Lev Num Deu Jos Jdg Rut 1Sa 2Sa 1Ki 2Ki 1Ch 2Ch Ezr Neh Est Job Psa Pro Ecc Sng Isa Jer Lam Ezk Dan Hos Jol Amo Oba Jon Mic Nam Hab Zep Hag Zec Mal Mat Mrk Luk Jhn Act Rom 1Co 2Co Gal Eph Php Col 1Th 2Th 1Ti 2Ti Tit Phm Heb Jas 1Pe 2Pe 1Jn 2Jn 3Jn Jud Rev'.split()

# ---- book names as the dictionaries write them ----
NAMES = [
 'genesis gen ge gn', 'exodus exod ex exo', 'leviticus lev le', 'numbers num nu nb', 'deuteronomy deut deu dt',
 'joshua josh jos', 'judges judg jdg jg', 'ruth ru', '1samuel 1sam 1sa', '2samuel 2sam 2sa', '1kings 1kgs 1ki 1kin',
 '2kings 2kgs 2ki 2kin', '1chronicles 1chron 1chr 1ch', '2chronicles 2chron 2chr 2ch', 'ezra ezr', 'nehemiah neh ne',
 'esther esth est', 'job jb', 'psalms psalm ps psa', 'proverbs prov pr pro', 'ecclesiastes eccl ecc eccles',
 'songofsolomon song cant canticles songofsongs sol', 'isaiah isa is', 'jeremiah jer je', 'lamentations lam la',
 'ezekiel ezek eze ezk', 'daniel dan da', 'hosea hos ho', 'joel joe jl', 'amos am', 'obadiah obad ob', 'jonah jon',
 'micah mic mi', 'nahum nah na', 'habakkuk hab', 'zephaniah zeph zep', 'haggai hag', 'zechariah zech zec',
 'malachi mal', 'matthew matt mat mt', 'mark mk mar', 'luke lk luk', 'john jn joh', 'acts ac act', 'romans rom ro',
 '1corinthians 1cor 1co', '2corinthians 2cor 2co', 'galatians gal ga', 'ephesians eph', 'philippians phil php',
 'colossians col', '1thessalonians 1thess 1th', '2thessalonians 2thess 2th', '1timothy 1tim 1ti', '2timothy 2tim 2ti',
 'titus tit', 'philemon philem phm', 'hebrews heb', 'james jas jam', '1peter 1pet 1pe', '2peter 2pet 2pe',
 '1john 1jn 1jo', '2john 2jn 2jo', '3john 3jn 3jo', 'jude jud', 'revelation rev re apoc']
BK = {}
for i, s in enumerate(NAMES):
    for n in s.split(): BK[n] = i
for k, v in list(BK.items()):          # Roman numerals and "I Kings"
    if k[0] in '123': BK[{'1': 'i', '2': 'ii', '3': 'iii'}[k[0]] + k[1:]] = v
BOOK_RE = r'((?:[123]|I{1,3})\s?[A-Z][a-z]+|[A-Z][a-z]+(?:\s+of\s+Solomon|\s+of\s+Songs)?)\.?'
REF_RE = re.compile(BOOK_RE + r'\s+(\d+)\s*:\s*(\d+)')
CONT_RE = re.compile(r'\s*[;,]\s*(?:(\d+)\s*:\s*)?(\d+)(?:\s*[-–]\s*\d+)?')
def book(s):
    return BK.get(re.sub(r'[\s.]', '', s).lower())

def refs_in(text):
    """[[start, end, b, c, v]] for 'Gen. 12:8; 13:3, 4' style references"""
    out = []
    for m in REF_RE.finditer(text):
        b = book(m.group(1))
        if b is None: continue
        c, v = int(m.group(2)), int(m.group(3))
        out.append([m.start(), m.end(), b, c, v])
        pos = m.end()
        while True:                        # "; 13:3,4" continues the same book
            while pos < len(text) and text[pos] in '-–0123456789': pos += 1
            n = CONT_RE.match(text, pos)
            if not n: break
            if n.group(1): c = int(n.group(1))
            v = int(n.group(2))
            s = n.start() + len(n.group(0)) - len(n.group(0).lstrip(' ;,'))
            out.append([s, n.end(), b, c, v]); pos = n.end()
    return out

# ---- the dictionaries ----
DICT = {}
for src in ('easton', 'smith', 'hastings', 'schaff', 'hitchcock'):
    d = {}
    for f in glob.glob(os.path.join(SRC, 'data', '02_sources', src, '[a-z].json')):
        d.update(json.load(open(f, encoding='utf-8')))
    DICT[src] = d
PREFIX = {}
for src, d in DICT.items():
    px = defaultdict(list)
    for k in d:
        m = re.match(r"([A-Z'\-]+)[ ,]+(THE|OF|SON|WIFE|MOTHER|KING|SISTER)\b", k)
        if m: px[m.group(1)].append(k)
    PREFIX[src] = px
CODE = {'easton': 'EAS', 'smith': 'SMI', 'hastings': 'HAS', 'schaff': 'SCH'}
def clean(t): return re.sub(r'\s+', ' ', t or '').strip()
def near(a, b):
    """the same entry text, give or take an editor's touch"""
    if a == b: return True
    import difflib
    return difflib.SequenceMatcher(None, a[:400], b[:400]).ratio() > 0.9

def senses(text):
    """an entry's text split into its numbered senses: '(1.)' (Easton) or '1.' after the head (Hastings)"""
    parts = re.split(r'\s(?=\(\d+\.\)\s)', text)
    if len(parts) == 1: parts = re.split(r'(?<=[.;)])\s(?=(?:[1-9]|1\d)\.\s+[A-Z])', text)
    return parts

def keys_for(names):
    ks = []
    for n in names:
        n = n.strip()
        for v in {n, n.replace('-', ' '), n.replace('-', ''), n.replace(' ', '-')}:
            ks.append(v.upper())
    return list(dict.fromkeys(ks))

def pick(names, refs, strict=False):
    """for each dictionary: the text (whole entry, or one numbered sense of it) that shares most
    verses with the person/place; the main name is preferred over its other names"""
    refs = {tuple(r)[:2] for r in refs}      # compared by chapter: entries cite verses about the person, not only where the name stands
    out = []
    for src in ('easton', 'smith', 'hastings', 'schaff'):
        cands = []
        for ni, n in enumerate(names):
            ks = keys_for([n])
            if ni == 0:   # "JOHN THE APOSTLE", "MARY, THE VIRGIN" ... count as the main name too
                ks += [k for k in PREFIX[src].get(n.upper(), []) if k not in ks]
            for k in ks:
                e = DICT[src].get(k)
                if not e: continue
                for df in e['definitions']:
                    text = clean(df['text']); parts = senses(text)
                    scored = [(len({(b, c) for _, _, b, c, v in refs_in(x)} & refs), x) for x in parts]
                    hit = [x for o, x in scored if o]
                    if len(parts) > 1 and len(hit) == 1:      # one of several people/places with this name
                        body = hit[0]
                        head = parts[0] if not re.match(r'\(?\d+\.', parts[0]) and len(parts[0]) < 200 and parts[0] != body else ''
                        text = (head + ' ' + body).strip() if head else body
                    tr = {(b, c) for _, _, b, c, v in refs_in(text)}
                    ov = len(tr & refs)
                    # share of the entry's own references that belong to this person/place, then how many
                    if ni > 0 and len(text) < 400: continue       # a short note under another name says little about this one
                    qual = ni == 0 and k not in keys_for([n])      # "MARY THE VIRGIN": about one person only
                    cands.append((ov > 0, ni == 0, qual, round(ov / max(1, len(tr)), 1), ov, len(text), text))
        if not cands: continue
        best = max(cands)
        if not best[0] and (strict or len(cands) > 1 or best[5] < 150): continue   # unclear which one, or too thin
        # strict: a same-name entry about something else (Hermes the Christian for Hermes the god) is not it
        text = best[6]
        if len(text) > 6000: text = text[:6000].rsplit(' ', 1)[0] + ' …'
        # CCEL's Hastings and Schaff texts are largely the same book: keep Schaff only where it says something
        # else (another sense of the name, or an entry Hastings has none of), never the same words under two names
        if src == 'schaff' and any(o[0] == 'HAS' and near(o[1], text) for o in out): continue
        out.append([CODE[src], text, [r for r in refs_in(text)]])
    return out

def meanings(names):
    out, seen = [], set()
    for n in names:
        for k in keys_for([n]):
            e = DICT['hitchcock'].get(k)
            if e and e['definitions']:
                t = clean(e['definitions'][0]['text'])
                if t and (n, t) not in seen: out.append([n, t]); seen.add((n, t))
                break
    return out

def b36dec(p, step):
    return [tuple(int(p[j + o:j + o + 2], 36) for o in range(0, step, 2)) for j in range(0, len(p), step)]

def build(index_file, rec_files, out_file, step, strict=False):
    idx = json.load(open(D + index_file, encoding='utf-8'))
    recs = {}
    for f in rec_files: recs.update(json.load(open(D + f, encoding='utf-8')))
    res, n_dic, n_mean = {}, 0, 0
    for pid, e in recs.items():
        names = [idx['n'][pid][0]] + [x[0] for x in e.get('nm', [])]
        names = list(dict.fromkeys(n for n in names if n))
        refs = b36dec(e['cc'][1], step)
        item = {}
        m = meanings(names)
        if m: item['m'] = m; n_mean += 1
        d = pick(names, refs, strict)
        if d: item['d'] = d; n_dic += 1
        if item: res[pid] = item
    json.dump(res, open(D + out_file, 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
    print(out_file, 'records', len(recs), 'with dictionary', n_dic, 'with name meaning', n_mean,
          'KB', os.path.getsize(D + out_file) // 1024, file=sys.stderr)

build('pi.json', ['pp.json'], 'dp.json', 6)
build('gi.json', ['gp.json'], 'dg.json', 6)
build('oi.json', ['oo.json'], 'do.json', 6, strict=True)   # gods, angels, months, musical terms (build_others.py)
