"""Read STEPBible TAHOT (Hebrew OT) and TAGNT (Greek NT) into the app's original-language columns.

- Verses follow the English (KJV) numbering that both files give first, so they line up with KJV and 개역한글.
- Hebrew: the translators' text (Leningrad with Qere readings); words found only in other manuscripts (type X) are left out.
- Greek: the Textus Receptus (Scrivener 1894). Words in TR are kept; where TR reads differently, the TR reading
  given in the variant columns replaces the word.
- Cantillation marks are removed from Hebrew (vowel points stay).

Each word: [text, transliteration, dStrongs, grammar, main]
  text/dStrongs/grammar keep '/' between Hebrew morphemes (prefix/word/suffix); main = index of the word's own morpheme.

usage: python3 parse_step.py STEP_DIR OUT.json
"""
import json, os, re, sys, unicodedata
from collections import defaultdict

STEP, OUT = sys.argv[1], sys.argv[2]
TA = os.path.join(STEP, 'Translators Amalgamated OT+NT')
CODES = ('Gen Exo Lev Num Deu Jos Jdg Rut 1Sa 2Sa 1Ki 2Ki 1Ch 2Ch Ezr Neh Est Job Psa Pro Ecc Sng Isa Jer Lam Ezk Dan Hos Jol Amo Oba Jon Mic Nam Hab Zep Hag Zec Mal '
         'Mat Mrk Luk Jhn Act Rom 1Co 2Co Gal Eph Php Col 1Th 2Th 1Ti 2Ti Tit Phm Heb Jas 1Pe 2Pe 1Jn 2Jn 3Jn Jud Rev').split()
BI = {c: i for i, c in enumerate(CODES)}
REF = re.compile(r'^([1-3]?[A-Z][a-z]+)\.(\d+)\.(\d+)[a-z]?((?:\([^)]*\)|\[[^\]]*\]|\{[^}]*\})*)#(\d+)=(\S+)')
def eng_ref(m):
    # English (KJV) chapter and verse: the plain reference, or the one in [square brackets] when given
    k = re.search(r'\[(\d+)\.(\d+)\]', m.group(4))
    c, v = (int(k.group(1)), int(k.group(2))) if k else (int(m.group(2)), int(m.group(3)))
    return c, max(v, 1)   # psalm titles (verse 0) are part of verse 1 in KJV and 개역한글

def norm_strong(s):
    """'H0430G' -> 'H430G', '{H7225G}' -> 'H7225G'"""
    m = re.match(r'\{?([HG])0*(\d+)([A-Za-z]?)\}?\+?$', s.strip())
    return f'{m.group(1)}{m.group(2)}{m.group(3)}' if m else s.strip('{} ')

def heb_clean(t):
    t = t.replace('\\', '')
    out = []
    for ch in unicodedata.normalize('NFC', t):
        o = ord(ch)
        if 0x0591 <= o <= 0x05AF or o in (0x05BD, 0x05C0, 0x05C4, 0x05C5): continue   # accents, meteg, paseq, dots
        out.append(ch)
    return ''.join(out).strip()

def tr_clean(t):
    return t.replace('\\', '').strip()

def put(store, bi, c, v, w):
    store[bi][c][v].append(w)

store = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
stats = defaultdict(int)

# ---------------- Hebrew ----------------
for fn in sorted(os.listdir(TA)):
    if not fn.startswith('TAHOT'): continue
    for line in open(os.path.join(TA, fn), encoding='utf-8'):
        m = REF.match(line)
        if not m: continue
        typ = m.group(6)
        if typ.startswith('X'): stats['heb_X'] += 1; continue
        f = line.rstrip('\n').split('\t')
        bi = BI[m.group(1)]; c, v = eng_ref(m)
        text = heb_clean(f[1]); tl = tr_clean(f[2])
        ds = f[4].split('\\')[0].replace('//', '/')
        f[1] = f[1].replace('//', '/'); f[2] = f[2].replace('//', '/'); f[5] = f[5].replace('//', '/')          # drop punctuation tags (\H9014 maqaf, \H9016 sof pasuq)
        parts = ds.split('/')
        main = next((i for i, p in enumerate(parts) if p.startswith('{')), len(parts) - 1)
        strongs = '/'.join(norm_strong(p) for p in parts)
        gram = f[5].strip()
        nseg = len(text.split('/'))
        if nseg != len(parts):            # keep morphemes in step with their numbers
            stats['heb_seg_mismatch'] += 1
            text = text.replace('/', ''); tl = tl.replace('/', '')
            strongs = norm_strong(parts[main]); gram = gram.split('/')[main] if '/' in gram else gram
            if gram and gram[0] not in 'HA': gram = f[5][0] + gram
            main = 0
        alt = [norm_strong(x.split('_')[0]) for x in re.split(r'[,;\s]+', f[9]) if re.match(r'^\{?[HG]\d', x)] if len(f) > 9 else []
        put(store, bi, c, v, [text, tl, strongs, gram, main, alt])
        stats['heb_words'] += 1

# ---------------- Greek (TR) ----------------
VAR = re.compile(r'(\S+)\s+\([Tt]=([^)]*)\)[^¦;]*?-\s*(G\d+[A-Za-z]?)=([\w-]+)\s+in:\s*([\w+]+)')
for fn in sorted(os.listdir(TA)):
    if not fn.startswith('TAGNT'): continue
    for line in open(os.path.join(TA, fn), encoding='utf-8'):
        m = REF.match(line)
        if not m: continue
        typ = m.group(6)
        if 'K' not in typ.upper(): stats['grk_notTR'] += 1; continue
        f = line.rstrip('\n').split('\t')
        bi = BI[m.group(1)]; c, v = eng_ref(m)
        g = re.match(r'(.*?)\s*\(([^)]*)\)\s*$', f[1].strip())
        text, tl = (g.group(1), g.group(2)) if g else (f[1].strip(), '')
        st, _, gram = f[3].partition('=')
        alt = [norm_strong(x) for x in re.findall(r'G\d+[A-Za-z]?', f[12] if len(f) > 12 else '')]
        in_parens = re.search(r'\([Kk]\)', typ)
        if in_parens:
            hit = None
            for col in (f[6], f[7]):
                for vm in VAR.finditer(col):
                    if 'TR' in vm.group(5).split('+'): hit = vm; break
                if hit: break
            if hit:
                punct = re.search(r'[,.;·:!?·;]+$', text)
                text = hit.group(1) + (punct.group(0) if punct and not re.search(r'[,.;·:!?·;]$', hit.group(1)) else '')
                tl, st, gram, alt = hit.group(2), hit.group(3), hit.group(4), []
                stats['grk_TRvariant'] += 1
            else:
                stats['grk_TRvariant_missing'] += 1
        text = text.replace('[[', '').replace(']]', '').replace('¶', '').strip()
        if st.startswith('G1722') and text.startswith('ἕν'): text = 'ἐν' + text[2:]; tl = 'en'   # 1Jn 5:7 accent slip in the source
        put(store, bi, c, v, [unicodedata.normalize('NFC', text), tl, norm_strong(st), gram.strip(), 0, alt])
        stats['grk_words'] += 1

out = []
for bi in range(66):
    ch = store[bi]
    nchap = max(ch) if ch else 0
    book = []
    for c in range(1, nchap + 1):
        vs = ch.get(c, {})
        nv = max(vs) if vs else 0
        book.append([vs.get(v, []) for v in range(1, nv + 1)])
    out.append(book)
json.dump(out, open(OUT, 'w'), ensure_ascii=False, separators=(',', ':'))
print(dict(stats), file=sys.stderr)
