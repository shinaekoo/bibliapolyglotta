"""English renderings of each Hebrew/Greek sub-word, from STEPBible TAHOT/TAGNT (CC BY 4.0).

The word-by-word English column of STEPBible ("in/ beginning", "he created", "In [the]") is split like
the Strong's column, so that every sub-word that tools/build_original.py writes to SUBS_OUT gets its own
English words. tools/align_original.py uses them (NOSTRONG=1) to tie KJV words to the original without
any Strong's tagging of the KJV itself.
Output (same keys and order as SUBS_OUT): {"b:c:v": [[english words of sub-word 1], ...]}
usage: python3 tools/orig_glosses.py STEP_DIR SUBS_JSON OUT_JSON
"""
import glob, json, os, re, sys
from collections import defaultdict
STEP, SUBS, OUT = sys.argv[1:4]
SC = 'Gen Exo Lev Num Deu Jos Jdg Rut 1Sa 2Sa 1Ki 2Ki 1Ch 2Ch Ezr Neh Est Job Psa Pro Ecc Sng Isa Jer Lam Ezk Dan Hos Jol Amo Oba Jon Mic Nam Hab Zep Hag Zec Mal Mat Mrk Luk Jhn Act Rom 1Co 2Co Gal Eph Php Col 1Th 2Th 1Ti 2Ti Tit Phm Heb Jas 1Pe 2Pe 1Jn 2Jn 3Jn Jud Rev'.split()
BI = {c: i for i, c in enumerate(SC)}
REF = re.compile(r'^([1-3]?[A-Z][a-z]{1,2})\.(\d+)\.(\d+)(?:\(([\d.]+)\))?(?:\[([\d.]+)\])?(?:\{([\d.]+)\})?#(\d+)=([^\t]+)\t')
WORDS = lambda s: [w.lower() for w in re.findall(r"[A-Za-z]+", s.replace('[', ' ').replace(']', ' '))]
verses = defaultdict(list)     # (b, c, v) -> [[english words per sub-word]]   (one item per original word)
for f in sorted(glob.glob(os.path.join(STEP, 'TAHOT_*.txt'))):
    for line in open(f, encoding='utf-8-sig'):
        m = REF.match(line)
        if not m or m.group(8)[0] not in 'LQ' or m.group(1) not in BI: continue
        x = line.rstrip('\n').split('\t')
        c, v = int(m.group(2)), int(m.group(3)) or 1
        segs, eng = x[4].split('/'), x[3].split('/')
        out = []
        for i, sg in enumerate(segs):
            for t in re.findall(r'H\d+', sg):
                if 9014 <= int(t[1:]) <= 9019: continue
                e = eng[i] if len(eng) == len(segs) else x[3]
                out.append(WORDS(e))
        verses[(BI[m.group(1)], c, v)].append(out)
for f in sorted(glob.glob(os.path.join(STEP, 'TAGNT_*.txt'))):
    for line in open(f, encoding='utf-8-sig'):
        m = REF.match(line)
        if not m or not re.search('[Kk]', m.group(8)) or m.group(1) not in BI: continue
        x = line.rstrip('\n').split('\t')
        c, v = m.group(2), m.group(3)
        if m.group(5): c, v = m.group(5).split('.')
        verses[(BI[m.group(1)], int(c), int(v))].append([WORDS(x[2])] * max(1, len(re.findall(r'G\d+', x[3]))))
SUB = json.load(open(SUBS))
res, bad = {}, 0
for key, subs in SUB.items():
    b, c, v = map(int, key.split(':'))
    flat = [g for w in verses.get((b, c, v), []) for g in w]
    if len(flat) != len(subs): bad += 1; flat = (flat + [[]] * len(subs))[:len(subs)]
    res[key] = flat
json.dump(res, open(OUT, 'w'), separators=(',', ':'))
print('verses', len(res), 'with a count mismatch', bad, file=sys.stderr)
