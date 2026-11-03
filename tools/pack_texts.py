"""text/{lang}{book}.json -> web/data/{lang}_{group}.json: the books of one language in 11 files

The app loads a whole group when it needs one of its books (web/index.html, GRP has the same groups).
Fewer files keep the published web version under its file limit; the build tools keep using text/.
Latin files are numbered like the Vulgate (with its extra books), so they are grouped through the
book they stand for and keyed by their own number.
usage: python3 tools/pack_texts.py
"""
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
TX = os.path.join(HERE, '..', 'text') + '/'
D = os.path.join(HERE, '..', 'web', 'data') + '/'
GRP = [0, 2, 5, 10, 14, 18, 19, 22, 25, 39, 43]     # first book of each group: Gen-Exo, Lev-Deu, Jos-2Sa, 1Ki-2Ch,
                                                     # Ezr-Job, Psa, Pro-Sng, Isa-Lam, Ezk-Mal, Mat-Jhn, Act-Rev
LAIDX = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,18,19,20,21,22,23,26,27,28,30,31,32,33,34,35,36,37,38,39,40,41,42,43,46,47,48,49,50,51,52,53,54,55,56,57,58,59,60,61,62,63,64,65,66,67,68,69,70,71,72]
LANGS = ['en', 'la', 'de', 'fr', 'ko', 'zh', 'es', 'it', 'ru', 'ja']
def group(b): return max(g for g, first in enumerate(GRP) if b >= first)

for lang in LANGS:
    packs = [{} for _ in GRP]
    for b in range(66):
        n = LAIDX[b] if lang == 'la' else b
        packs[group(b)][str(n)] = json.load(open(f'{TX}{lang}{n:02d}.json', encoding='utf-8'))
    for g, p in enumerate(packs):
        json.dump(p, open(f'{D}{lang}_{g}.json', 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
    print(lang, [os.path.getsize(f'{D}{lang}_{g}.json') // 1024 for g in range(len(GRP))], 'KB', file=sys.stderr)
