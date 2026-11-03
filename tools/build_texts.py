"""Texts of the added translations -> text/{lang}{book}.json (KJV versification)

Sources:
  es  Reina-Valera 1909    seven1m/open-bibles spa-rv1909.usfx.xml — phrases tagged with Strong's numbers;
                           the numbers of each word go to text/esS{book}.json for the alignment
  it  Riveduta 1927        seven1m/open-bibles ita-riveduta.osis.xml (KJV numbering, apostrophes lost)
                           + BibleNLP/ebible corpus/ita-ita1927.txt (same text with its apostrophes; some
                             verses are missing there) -> its verse when the letters agree, else the words fixed
  ru  Synodal 1876         seven1m/open-bibles rus-synodal.zefania.xml (Hebrew numbering)
                           -> KJV numbering with BibleNLP/ebible metadata/eng.vrs
  ja  口語訳 1954/55        seven1m/open-bibles jpn-kougo.osis.xml (ruby glosses dropped)
  pt  João Ferreira de Almeida     seven1m/open-bibles por-almeida.usfx.xml (public domain)
  tl  Ang Biblia 1905              scrollmapper/bible_databases sources/tl/TagAngBiblia (public domain)
  ceb Ang Biblia (Pinadayag) 1917  scrollmapper/bible_databases sources/ceb/CebPinadayag (public domain)
  id  Alkitab Yang Terbuka (AYT)   BibleNLP/ebible corpus/ind-indayt.txt — © YLSA-AYT, CC BY-NC 4.0
  ig  Baịbụlụ Nsọ (Biblica 2020)   BibleNLP/ebible corpus/ibo-ibo.txt — © Biblica, CC BY-SA 4.0
      (the corpus puts verses at the KJV numbers they carry; where the Hebrew numbering has fewer
       verses in a chapter the last ones are missing there, about 130 verses in each)
Each file is like the other languages: [chapter][verse] = text. Psalm titles go into verse 1; a verse the
KJV grid does not have is added to the last verse of its chapter.
Japanese is split into phrases (a content word with the particles and endings that follow it) with
spaces between them, like the Chinese text; the app hides the spaces. Needs janome (pure Python,
github.com/mocobeta/janome, with ipadic/sysdic.zip unpacked into src/janome).

usage: python3 tools/build_texts.py OPEN_BIBLES_DIR EBIBLE_DIR JANOME_SRC_DIR SCROLLMAPPER_DIR [lang ...]
"""
import difflib, json, os, re, sys
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
TX = os.path.join(HERE, '..', 'text') + '/'
OB, EB, JAN, SM = sys.argv[1:5]
ONLY = set(sys.argv[5:])
want = lambda lang: not ONLY or lang in ONLY
sys.path.insert(0, JAN)
BK = 'GEN EXO LEV NUM DEU JOS JDG RUT 1SA 2SA 1KI 2KI 1CH 2CH EZR NEH EST JOB PSA PRO ECC SNG ISA JER LAM EZK DAN HOS JOL AMO OBA JON MIC NAM HAB ZEP HAG ZEC MAL MAT MRK LUK JHN ACT ROM 1CO 2CO GAL EPH PHP COL 1TH 2TH 1TI 2TI TIT PHM HEB JAS 1PE 2PE 1JN 2JN 3JN JUD REV'.split()
OSIS = 'Gen Exod Lev Num Deut Josh Judg Ruth 1Sam 2Sam 1Kgs 2Kgs 1Chr 2Chr Ezra Neh Esth Job Ps Prov Eccl Song Isa Jer Lam Ezek Dan Hos Joel Amos Obad Jonah Mic Nah Hab Zeph Hag Zech Mal Matt Mark Luke John Acts Rom 1Cor 2Cor Gal Eph Phil Col 1Thess 2Thess 1Tim 2Tim Titus Phlm Heb Jas 1Pet 2Pet 1John 2John 3John Jude Rev'.split()
EN = [json.load(open(f'{TX}en{b:02d}.json', encoding='utf-8')) for b in range(66)]   # the KJV grid
W = re.compile(r'[^\W\d_]+')
tree = lambda: defaultdict(lambda: defaultdict(dict))
def tidy(t): return re.sub(r'\s+', ' ', t or '').strip()

def grid(src, title_sep=' '):
    """{b: {c: {v: text}}} on the KJV grid; verse 0 (a title) joins verse 1, verses past the end join the last"""
    books, miss = [], 0
    for b in range(66):
        chs = []
        for c, vs in enumerate(EN[b], 1):
            got = src.get(b, {}).get(c, {})
            row = [tidy(got.get(v, '')) for v in range(1, len(vs) + 1)]
            if got.get(0): row[0] = tidy(got[0]) + title_sep + row[0]
            extra = [got[v] for v in sorted(got) if v > len(vs)]
            if extra: row[-1] = tidy(' '.join([row[-1]] + extra))
            miss += sum(1 for t in row if not t)
            chs.append(row)
        books.append(chs)
    return books, miss

def attrs(a): return dict(re.findall(r'(\w+)=["\']([^"\']*)["\']', a))

def osis(x):
    """OSIS with <verse>..</verse> or sID/eID milestones; canonical psalm titles -> verse 0; <w gloss> = ruby"""
    out = tree(); cur = None; buf = []; chap = None; intitle = False; tbuf = []
    for m in re.finditer(r'<(/?)(\w+)([^>]*?)(/?)>|([^<]+)', x):
        if m.group(5) is not None:
            if intitle: tbuf.append(m.group(5))
            elif cur: buf.append(m.group(5))
            continue
        close, tag, a = m.group(1), m.group(2), attrs(m.group(3))
        if tag == 'chapter' and not close:
            r = (a.get('osisID') or a.get('sID') or '').split('.')
            if r[0] in OSIS: chap = (OSIS.index(r[0]), int(r[1]))
        elif tag == 'title':
            if not close and a.get('type') == 'psalm': intitle = True; tbuf = []
            elif close and intitle:
                intitle = False
                if chap: out[chap[0]][chap[1]][0] = ''.join(tbuf)
        elif tag == 'verse':
            if close or 'eID' in a:
                if cur: out[cur[0]][cur[1]][cur[2]] = out[cur[0]][cur[1]].get(cur[2], '') + ''.join(buf)
                cur = None; continue
            ref = (a.get('sID') or a.get('osisID')).split()[0].split('!')[0].split('.')
            cur = (OSIS.index(ref[0]), int(ref[1]), int(ref[2])) if ref[0] in OSIS else None; buf = []
    return out

def usfx(x):
    """USFX -> texts, and the Strong's numbers of each word (from <w s="H0776">Y la tierra</w>)"""
    out, st = tree(), tree(); b = c = v = None; cur_s = ''
    for m in re.finditer(r'<book id="(\w+)"|<c id="(\d+)"\s*/>|<v id="(\d+)"\s*/>|<ve\s*/>|<w s="([^"]*)">|</w>|<(?:f|x|toc|h|id)\b.*?</(?:f|x|toc|h|id)>|<[^>]+>|([^<]+)', x, re.S):
        g = m.group
        if g(1): b = BK.index(g(1)) if g(1) in BK else None; v = None
        elif g(2): c = int(g(2)); v = None
        elif g(3):
            v = int(g(3))
            if b is not None: out[b][c][v] = ''; st[b][c][v] = []
        elif g(0).startswith('<ve'): v = None
        elif g(4) is not None: cur_s = '+'.join(re.sub(r'([HG])0*(\d+)', r'\1\2', s) for s in g(4).split())
        elif g(0) == '</w>': cur_s = ''
        elif g(5) and b is not None and v is not None:
            out[b][c][v] += g(5); st[b][c][v] += [cur_s] * len(W.findall(g(5)))
    return out, st

def vrs_map(path):
    """eng.vrs mapping lines ("KJV ref = Hebrew ref") -> {Hebrew (book, c, v): KJV (book, c, v)}"""
    m = {}
    def span(s):
        bk, rest = s.split(); c, vv = rest.split(':'); a, _, z = vv.partition('-')
        return bk, int(c), int(a), int(z or a)
    for line in open(path, encoding='utf-8'):
        if '=' not in line or line.startswith('#') or line.split()[0] not in BK: continue
        l, r = (x.strip() for x in line.split('='))
        lb, lc, la, lz = span(l); rb, rc, ra, rz = span(r)
        for k in range(lz - la + 1): m[(rb, rc, ra + k)] = (lb, lc, la + k)
    return m

def spanish():
    src, st = usfx(open(os.path.join(OB, 'spa-rv1909.usfx.xml'), encoding='utf-8').read())
    # Job 38-40: this edition numbers like the Hebrew Bible and merges the last verses of chapter 39
    for d in (src, st):
        j = d[17]; c39, c40 = dict(j[39]), dict(j[40])
        for v in (39, 40, 41): j[38][v] = c39.get(v - 38, j[38].get(v))
        j[39] = {v - 3: t for v, t in c39.items() if v > 3}
        j[40] = {v + 5: t for v, t in c40.items() if v <= 19}
        for v in range(1, 6): j[40][v] = '' if d is src else []
    return src, st

def italian():
    x = open(os.path.join(OB, 'ita-riveduta.osis.xml'), encoding='utf-8').read().replace('\x92', '’')
    out = tree()
    for ref, t in re.findall(r"<verse osisID='([^']+)'>(.*?)</verse>", x, re.S):
        bk, c, v = ref.split('.')
        out[OSIS.index(bk)][int(c)][int(v)] = re.sub(r'<[^>]+>', '', t)
    eb, words, plain = tree(), {}, set()
    for ref, t in zip(open(os.path.join(EB, 'metadata', 'vref.txt')), open(os.path.join(EB, 'corpus', 'ita-ita1927.txt'), encoding='utf-8')):
        bk, cv = ref.split(); c, v = map(int, cv.split(':')); t = t.strip()
        if bk in BK and t and t != '<range>': eb[BK.index(bk)][c][v] = t
        for w in re.findall(r"\w+(?:’\w+)+", t): words.setdefault(w.replace('’', ''), w)
        plain.update(re.findall(r'\w+', t))
    letters = lambda s: re.sub(r'\W', '', s).lower()
    for b in out:
        for c in out[b]:
            for v, t in out[b][c].items():
                e = eb[b][c].get(v)
                if e and (letters(e) == letters(t) or difflib.SequenceMatcher(None, letters(e), letters(t), autojunk=False).ratio() >= 0.9):
                    out[b][c][v] = e      # the same verse, with its apostrophes (and without the typos of the other copy)
                else:   # "lEterno" -> "l’Eterno", only for spellings that are never a word of their own
                    out[b][c][v] = re.sub(r'\w+', lambda m: words[m.group(0)] if m.group(0) in words and m.group(0) not in plain else m.group(0), t)
    return out

def russian():
    x = open(os.path.join(OB, 'rus-synodal.zefania.xml'), encoding='utf-8').read()
    m = vrs_map(os.path.join(EB, 'metadata', 'eng.vrs'))
    out = tree()
    for bn, body in re.findall(r'<BIBLEBOOK bnumber="(\d+)"[^>]*>(.*?)</BIBLEBOOK>', x, re.S):
        b = int(bn) - 1
        if b >= 66: continue
        for c, cb in re.findall(r'<CHAPTER cnumber="(\d+)"[^>]*>(.*?)</CHAPTER>', body, re.S):
            for v, t in re.findall(r'<VERS vnumber="(\d+)"[^>]*>(.*?)</VERS>', cb, re.S):
                _, kc, kv = m.get((BK[b], int(c), int(v)), (BK[b], int(c), int(v)))
                t = re.sub(r'<[^>]+>', '', t).split(' | ')[0]            # Greek additions in Esther follow a bar
                t = re.sub(r'\(\d+:\d+\)\s*', '', t).replace('[', '').replace(']', '')
                cur = out[b][kc].get(kv)
                out[b][kc][kv] = (cur + ' ' + t) if cur else t
    return out

# ---- Japanese phrases ----
ATTACH = ('助詞', '助動詞', '記号')
def ja_phrases(tok, t):
    out, cur, prev = [], '', None
    for x in tok.tokenize(t):
        p = x.part_of_speech.split(','); s = x.surface
        if not s.strip(): continue
        join = (not cur or p[0] in ATTACH or (p[0] == '動詞' and p[1] in ('非自立', '接尾')) or
                (p[0] == '名詞' and p[1] in ('接尾', '非自立')) or (p[0] == '形容詞' and p[1] == '非自立') or
                prev[0] == '接頭詞' or (prev[0] == '名詞' and prev[1] == 'サ変接続' and x.base_form == 'する') or
                (prev[0] == '名詞' and p[0] == '名詞' and prev[1] != '代名詞' and p[1] not in ('代名詞', '副詞可能')))
        if join: cur += s
        else: out.append(cur); cur = s
        prev = p
    if cur: out.append(cur)
    return ' '.join(out)

def japanese():
    from janome.tokenizer import Tokenizer
    tok = Tokenizer()
    x = open(os.path.join(OB, 'jpn-kougo.osis.xml'), encoding='utf-8').read()
    x = re.sub(r'<note\b.*?</note>', '', x, flags=re.S)
    src = osis(x)
    for b in src:
        for c in src[b]:
            for v, t in src[b][c].items():
                src[b][c][v] = ja_phrases(tok, re.sub(r'\s+', '', t)) if t.strip() else ''
    return src

os.makedirs(TX, exist_ok=True)
def write(lang, books):
    for b, chs in enumerate(books):
        json.dump(chs, open(f'{TX}{lang}{b:02d}.json', 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))

def scroll(path):
    d = json.load(open(path, encoding='utf-8')); out = tree()
    for bi, b in enumerate(d['books'][:66]):
        for ch in b['chapters']:
            for v in ch['verses']: out[bi][v['chapter']][v['verse']] = v['text']
    return out
def ebible(name):
    out = tree()
    for ref, t in zip(open(os.path.join(EB, 'metadata', 'vref.txt')), open(os.path.join(EB, 'corpus', name + '.txt'), encoding='utf-8')):
        bk, cv = ref.split(); c, v = map(int, cv.split(':')); t = t.strip()
        if bk in BK and t and t != '<range>': out[BK.index(bk)][c][v] = t
    return out
import unicodedata
def clean_with(fix):
    def make(src):
        for b in src:
            for c in src[b]:
                for v, t in src[b][c].items(): src[b][c][v] = unicodedata.normalize('NFC', fix(t))
        return src
    return make
MORE = {
 'pt': lambda: usfx(open(os.path.join(OB, 'por-almeida.usfx.xml'), encoding='utf-8').read())[0],
 'tl': lambda: scroll(os.path.join(SM, 'sources', 'tl', 'TagAngBiblia', 'TagAngBiblia.json')),
 'ceb': lambda: clean_with(lambda t: t.replace('`', "'"))(scroll(os.path.join(SM, 'sources', 'ceb', 'CebPinadayag', 'CebPinadayag.json'))),
 'id': lambda: clean_with(lambda t: re.sub(r'\s*\(\d+-\d+\)\s*', ' ', t))(ebible('ind-indayt')),     # "(51-2)": Hebrew verse marks
 'ig': lambda: clean_with(lambda t: t)(ebible('ibo-ibo')),
}

es, es_st = spanish() if want('es') else ({}, {})
for b in es:   # "EN el principio", "¿CAZARÁS tú": the capitals of a chapter's first word, as in print
    for c in es[b]:
        for v, t in es[b][c].items():
            es[b][c][v] = re.sub(r'^((?:[¿¡(]?[A-ZÁÉÍÓÚÑ]?\s)?[¿¡(]?)([A-ZÁÉÍÓÚÑ]{2,})(?![a-záéíóúñ])', lambda m: m.group(1) + m.group(2).capitalize(), t.strip())
if want('es'): books, miss = grid(es); write('es', books); print('es empty verses', miss, file=sys.stderr)
# Strong's numbers per word, on the same grid (a merged verse keeps the numbers of its first part only)
S = []
for b in range(66):
    chs = []
    for c, vs in enumerate(EN[b], 1):
        got = es_st.get(b, {}).get(c, {})
        chs.append([' '.join(s or '-' for s in got.get(v, [])) for v in range(1, len(vs) + 1)])
    S.append(chs)
for b, chs in enumerate(S if want('es') else []):
    json.dump(chs, open(f'{TX}esS{b:02d}.json', 'w', encoding='utf-8'), separators=(',', ':'))
for lang, make in [(l, m) for l, m in (('it', italian), ('ru', russian), ('ja', japanese), *MORE.items()) if want(l)]:
    # a psalm title and verse 1: in Japanese an ideographic space, which stays on screen
    books, miss = grid(make(), '\u3000' if lang == 'ja' else ' '); write(lang, books); print(lang, 'empty verses', miss, file=sys.stderr)
