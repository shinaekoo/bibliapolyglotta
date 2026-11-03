"""Hebrew/Greek word study data -> web/data/ox0..3.json (shard = Strong's number % 4)

For each disambiguated Strong's number (dStrong) used in the original text:
  "d":  the full entry of the STEPBible brief lexicon (TBESH for Hebrew, from BDB;
        TBESG for Greek, from Abbott-Smith), CC BY 4.0
  "cc": [total occurrences, packed places] - every place the word is used, at most CAP spread
        evenly; each place is 8 base-36 characters: book, chapter, verse, word on screen
  "r":  {lang: [[rendering, count], ...]} - how each translation renders the word,
        counted through the app's word links (original -> KJV -> other translation)

Run after tools/build_original.py and tools/align_original.py.
usage: python3 tools/build_orig_lex.py STEP_DIR OE_JSON SUBS_JSON
"""
import json, os, re, sys, difflib
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
D = os.path.join(HERE, '..', 'web', 'data') + '/'
STEP = sys.argv[1]
CAP = 240
LAIDX = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,18,19,20,21,22,23,26,27,28,30,31,32,33,34,35,36,37,38,39,40,41,42,43,46,47,48,49,50,51,52,53,54,55,56,57,58,59,60,61,62,63,64,65,66,67,68,69,70,71,72]
PS, DAN = 18, 26
W = re.compile(r'[^\W\d_]+')
LA_END = sorted('ibus ius ae am as em es ia is nt os ud um us a e i o u orum arum ibus erunt erit avit ivit abit ebit ant ent unt it at et'.split(), key=len, reverse=True)
QUE_EX = set('quoque atque itaque neque usque quisque ubique denique undique utique plerumque absque quinque'.split())
def la_n(w):
    w = w.lower().replace('æ', 'ae').replace('œ', 'oe').replace('j', 'i').replace('v', 'u')
    if w.endswith('que') and w not in QUE_EX and len(w) > 5: w = w[:-3]
    for e in LA_END:
        if w.endswith(e) and len(w) - len(e) >= 3: return w[:-len(e)]
    return w
def suf(ends):
    ends = sorted(ends, key=len, reverse=True)
    def f(w):
        w = w.lower()
        for e in ends:
            if w.endswith(e) and len(w) - len(e) >= 3: return w[:-len(e)]
        return w
    return f
en_n = suf(['eth', 'est', 'ing', 'edst', 'ed', 'es', 's', 'ly'])
de_n = suf(['ern', 'em', 'en', 'er', 'es', 'e', 'n', 's', 'st', 't'])
fr_n = suf(['aient', 'ait', 'ent', 'ez', 'ons', 'ées', 'és', 'ée', 'é', 'er', 'es', 's', 'x', 'e'])
KO_SUF = sorted(('이니라 이라 이요 이며 이니 이로다 이시라 이시니 이었더라 이더라 '
 '께서는 께서 에게서 에게는 에게 한테 으로써 으로서 으로는 으로 로써 로서 로는 로 에서는 에서 에는 에도 에 '
 '이나 이든지 이여 이시여 여 아 야 과 와 의 은 는 이 가 을 를 도 만 까지 부터 마다 처럼 같이 보다 조차 '
 '하시니라 하니라 하리라 하시고 하시며 하시매 하시되 하시니 하셨더라 하였더라 하였으니 하였고 하였느니라 하였다 하더라 하고 하여 하며 하매 하니 하되 하라 하사 하심 함 할 한 하는 하신 하시는 하실 '
 '되니라 되리라 되었더라 되고 되어 되며 되매 된 될 되는 '
 '니라 리라 더라 느니라 도다 로다 노라 시니 시고 시며 시매 시되 시라 셨더라 였더라 였고 였으니 었더라 었고 었으니 았더라 았고 '
 '고 며 매 니 되 서 면 거든 려고 러 사 므로 으매 으니 으며 으라 라 다 는 은 을 ㄴ').split(), key=len, reverse=True)
def ko_n(w):
    s = w
    for _ in range(2):
        for e in KO_SUF:
            if s.endswith(e) and len(s) - len(e) >= 1:
                s = s[:-len(e)]; break
    return s or w
sys.path.insert(0, HERE)
from langnorm import es_n, it_n, ru_n, ja_n, pt_n, tl_n, ceb_n, id_n, ig_n, zh_n
import meanings
NORM = {'la': la_n, 'en': en_n, 'de': de_n, 'fr': fr_n, 'ko': ko_n, 'zh': lambda w: w, 'es': es_n, 'it': it_n, 'ru': ru_n, 'ja': ja_n, 'pt': pt_n, 'tl': tl_n, 'ceb': ceb_n, 'id': id_n, 'ig': ig_n}
def snum(x):
    m = re.match(r'([HG])0*(\d+)', x or '')
    return f'{m.group(1)}{m.group(2)}' if m else None
TAG = re.compile(r'\[([HG]\d+)\]')
EN_RE = re.compile(r'"((?:[1-3]?[A-Za-z]{2,3})\|(\d+)\|(\d+))"\s*:\s*\{\s*"en"\s*:\s*"((?:[^"\\]|\\.)*)"')
def kjv_tokens(s):
    s = re.sub(r'</?em>', '', s).replace('[[', ' ').replace(']]', ' ')
    out = []
    for m in re.finditer(r'\[([HG]\d+)\]|[^\W\d_]+', s):
        if m.group(1):
            if out: out[-1][1].append(m.group(1))
        else: out.append((m.group(0), []))
    return out
def kjv_book(code):
    out = {}
    for m in EN_RE.finditer(open(os.path.join(KJV, code + '.json'), encoding='utf-8').read()):
        if m.group(1).split('|')[0] != code: continue
        try: t = json.loads('"' + m.group(4) + '"')
        except Exception: t = m.group(4)
        out[(int(m.group(2)), int(m.group(3)))] = t
    return out
def strongs_for(app_words, tagged):
    a = [w.lower() for w in app_words]; b = [w.lower() for w, _ in tagged]
    res = [[] for _ in app_words]
    for blk in difflib.SequenceMatcher(a=a, b=b, autojunk=False).get_matching_blocks():
        for k in range(blk.size): res[blk.a + k] = [snum(t) for t in tagged[blk.b + k][1]]
    return res

KC = 'Gen Exo Lev Num Deu Jos Jdg Rth 1Sa 2Sa 1Ki 2Ki 1Ch 2Ch Ezr Neh Est Job Psa Pro Ecc Sng Isa Jer Lam Eze Dan Hos Joe Amo Oba Jon Mic Nah Hab Zep Hag Zec Mal Mat Mar Luk Jhn Act Rom 1Co 2Co Gal Eph Phl Col 1Th 2Th 1Ti 2Ti Tit Phm Heb Jas 1Pe 2Pe 1Jo 2Jo 3Jo Jde Rev'.split()
# second argument: OE_JSON from tools/align_original.py (OE_OUT, NOSTRONG mode) — which KJV words belong to which
# original sub-word, so that a word's renderings leave out its prefixes and suffixes. (Before: a KJV Strong's tagging.)
OE = json.load(open(sys.argv[2]))
SUBS = json.load(open(sys.argv[3]))
def b36(n): return '0123456789abcdefghijklmnopqrstuvwxyz'[n // 36] + '0123456789abcdefghijklmnopqrstuvwxyz'[n % 36]

# ---- full brief-lexicon entries ----
DEF = {}
for f in ('TBESH.txt', 'TBESG.txt'):
    for line in open(os.path.join(STEP, f), encoding='utf-8-sig'):
        x = line.rstrip('\n').split('\t')
        if len(x) < 8 or not re.match(r'^[HG]\d{4}', x[0]): continue
        ds = x[1].split('=')[0].strip()
        t = re.sub(r'<br\s*/?>', '\n', x[7], flags=re.I)
        t = re.sub(r'<ref=[^>]*>|</ref>', '', t)
        t = re.sub(r'<[^>]+>', '', t)
        t = re.sub(r'[ \t]+', ' ', t).replace(' \n', '\n').strip()
        if len(t) > 4000: t = t[:4000].rsplit(' ', 1)[0] + ' …'
        DEF[ds] = t

# ---- the app's own text for the translations (same lane shifts as the app) ----
TX = os.path.join(HERE, '..', 'text') + '/'
def load(pre, i): return json.load(open(f'{D if pre == "al" else TX}{pre}{i:02d}.json', encoding='utf-8'))
def ps_map(h):
    if h <= 8 or h >= 148: return [(h, 1, 999)]
    if h == 9: return [(9, 1, 21)]
    if h == 10: return [(9, 22, 999)]
    if h <= 113: return [(h - 1, 1, 999)]
    if h == 114: return [(113, 1, 8)]
    if h == 115: return [(113, 9, 999)]
    if h == 116: return [(114, 1, 999), (115, 1, 999)]
    if h <= 146: return [(h - 1, 1, 999)]
    return [(146, 1, 999), (147, 1, 999)]

occ = defaultdict(list)                       # dStrong -> [(b, c, v, i)]
ren = defaultdict(lambda: defaultdict(Counter))   # dStrong -> lang -> key -> count
surf = defaultdict(Counter)                    # (dStrong, lang, key) -> surface forms (per word: Portuguese 'Deus' and 'deu' share a key)
LANGS = ['en', 'la', 'de', 'fr', 'ko', 'zh', 'es', 'it', 'ru', 'ja', 'pt', 'tl', 'ceb', 'id', 'ig']
STOP = {'zh': set('之 的 了 和 與 与 並 并 就 也 在 於 于 以 而 其 我 你 他 她 它 們 们 我們 你們 他們 這 这 那 是 有 一 為 为 所 者 乃 卻 却 又 都 把 被 將 将 從 从 向 對 对 給 给 使 叫 要 必 不 沒 没 無 无 你們的 他的 我的 你的'.split()),
        'en': set('the a an of and to in that is be it shall unto for with his he him them they their s'.split()),
        'la': set('et in est ad non qui quae quod ut cum de a ab ex e se sunt erat omnes omnis omnia quam quoniam sicut super per pro enim autem vero ergo tuus tua tuum meus mea noster vester eius eorum illis'.split()),
        'de': set('der die das des dem den ein eine einen einem eines und zu in ist sie er es ihr ihm ihn im auf aus von mit für hat haben wird werden nicht auch so da denn wie dein deine mein meine sein seine unser euer ihre uns euch'.split()),
        'fr': set('le la les l de du des d un une et à au aux est il ils elle a en que qui dans sur par pour car ne pas tout tous ce cette ces son sa ses ton ta tes mon ma mes notre votre nos vos leur leurs'.split()),
        'ko': set('그 이 저 그들 너희 우리 네 내 나 너 저희 인 하 대 것 자 때 곳 중 및 또 곧'.split()),
        'es': set('el la los las lo un una unos y e o u de del a al en que se su sus mi mis tu tus por para con no es fué fue como mas pero le les nos os él ella ellos todo todos'.split()),
        'it': set('il lo la i gli le l un una uno e ed o di del della dei delle degli da dal dalla a al alla ai in nel nella che si suo sua suoi sue mio mia tuo tua per con non è come ma gli egli essi tutto tutti'.split()),
        'ru': set('и в во на с со к ко о об от по за из у не но а же ли бы что как он она оно они его ее их мой моя твой твоя свой своя все всё весь это тот та то этот который'.split()),
        'ja': set('その この あの それ これ わたし あなた 彼 彼ら こと もの ため よう'.split()),
        'pt': set('o a os as um uma e de do da dos das em no na nos nas que se seu sua seus suas por para com não é como mas lhe lhes ele ela eles todo todos ao aos'.split()),
        'tl': set('ang ng mga sa at na si ni kay ay ko mo niya nila kanila kaniya kaniyang aking iyong ito iyon siya sila kami tayo hindi'.split()),
        'ceb': set('ang sa mga ug nga si ni kang iyang ilang akong imong kini kana siya sila kami kita dili mao'.split()),
        'id': set('yang dan di ke dari itu ini dengan untuk dalam pada kepada akan tidak dia mereka kamu aku kami kita ia oleh juga'.split()),
        'ig': set('na nke ya ha m gị anyị unu ọ o a e ka n ma bụ dị nʼ'.split())}
KO_P = sorted('께서는 께서 께 에게서 에게는 에게 한테 으로써 으로서 으로는 으로 로써 로서 로는 에서는 에서 에는 에도 이여 이시여 이니라 이라 이요 이며 이니 은 는 이 가 을 를 의 도 만 에 로 과 여 와'.split(), key=len, reverse=True)
def ko_light(w):
    for e in KO_P:
        if w.endswith(e) and len(w) - len(e) >= (2 if e in ('와', '여', '이', '가') else 1): return w[:-len(e)]
    return w
KO_HEAVY = NORM['ko']
def ko_show(stem, forms):
    """label for a group of Korean forms: its most common form, without particles"""
    light = Counter()
    for f, n in forms.items(): light[ko_light(f)] += n
    tot = sum(light.values())
    nouns = [(f, n) for f, n in light.most_common() if len(f) > 1 and not f.endswith('하')]
    best = nouns[0][0] if nouns and nouns[0][1] >= tot * 0.3 else light.most_common(1)[0][0]
    if len(best) == 1 or best.endswith('하'):   # a bare verb stem: show the form as written
        return forms.most_common(1)[0][0]
    return best

GLOSS = {}                                    # STEPBible's short English gloss of each word
for b in range(66):
    al = load('al', b)
    for k_, x_ in (al.get('og') or {}).items(): GLOSS.setdefault(k_, x_[2] if len(x_) > 2 else '')
    tx = {k: load(k, b) for k in ('en', 'de', 'fr', 'ko', 'zh', 'es', 'it', 'ru', 'ja', 'pt', 'tl', 'ceb', 'id', 'ig')}
    la = load('la', LAIDX[b])
    for c in range(1, len(al['v']) + 1):
        lanes = {k: (tx[k][c-1] if c <= len(tx[k]) else []) for k in tx}
        if b == PS:
            L = []
            for ch, a0, z in ps_map(c):
                vs = la[ch-1]; L += vs[a0-1:min(z, len(vs))]
            ref = len(lanes['ko']) or len(lanes['en'])
            L = L[max(0, min(3, len(L) - ref)):]
            G = lanes['de']; lanes['de'] = G[max(0, min(3, len(G) - ref)):]
        else:
            L = la[c-1] if c <= len(la) else []
            if b == DAN and c == 3 and len(L) > 90: L = L[:23] + L[90:]
        lanes['la'] = L
        for v in range(1, len(al['v'][c-1]) + 1):
            ow = al['ow'][c-1][v-1].split(' ') if al['ow'][c-1][v-1] else []
            rec = al['v'][c-1][v-1]
            p = rec.get('or', []); o2e = defaultdict(set)
            for i in range(0, len(p), 2): o2e[p[i]].add(p[i+1])
            e2l = {}
            for k in LANGS[1:]:
                q = rec.get(k, []); m = defaultdict(set)
                for i in range(0, len(q), 2): m[q[i+1]].add(q[i])
                e2l[k] = m
            key = f'{b}:{c}:{v}'; sub = SUBS.get(key, []); core_of = defaultdict(set)
            for k, j in OE.get(key, []):
                if k < len(sub): core_of[(sub[k][0], sub[k][1])].add(j)
            words = {k: W.findall((lanes[k][v-1] if v <= len(lanes[k]) else '') or '') for k in LANGS}
            for i, w in enumerate(ow):
                ds = w.split('|')[0]
                if not ds: continue
                occ[ds].append((b, c, v, i))
                ens = sorted(o2e.get(i, ()))
                base = snum(ds)
                core = [j for j in ens if j in core_of.get((i, base), ())]   # the word itself, not its prefixes or suffixes
                ens = core or ens
                for k in LANGS:
                    if k == 'en': xs = ens
                    else: xs = sorted({x for j in ens for x in e2l[k].get(j, ())})
                    seen = set()
                    for x in xs:
                        if x >= len(words[k]): continue
                        w2 = words[k][x]
                        if k == 'ja': w2 = ja_n(w2)          # "神は" -> "神"
                        elif k == 'zh': w2 = zh_n(w2)        # "神啊", "之地", "神的" -> 神, 地
                        if len(w2) < (1 if k in ('ja', 'zh') else 2) or w2.lower() in STOP[k] or (k == 'ko' and ko_light(w2) in STOP['ko']): continue
                        key = KO_HEAVY(w2) if k == 'ko' else NORM[k](w2)
                        if key in seen: continue
                        seen.add(key); ren[ds][k][key] += 1; surf[(ds, k, key)][w2 if k != 'en' else w2.lower()] += 1

LITTLE = set('the a an and but or nor for if then that this these those which who whom whose what when where why how not no in on at to from by with of '
             'into upon unto through over under after before because since as so also even yet behold indeed truly lest until while than '
             'he she it they we you i me him her them us self himself herself itself thou thee ye my your his its our their'.split())
# people and places (their Korean names are names, never verbs: 스나아, not 스나다)
NAMES = set(json.load(open(f'{D}pi.json', encoding='utf-8'))['d']) | set(json.load(open(f'{D}gi.json', encoding='utf-8'))['d'])
shards = [{} for _ in range(4)]
for ds, places in occ.items():
    n = len(places)
    pick = places if n <= CAP else [places[round(j * (n - 1) / (CAP - 1))] for j in range(CAP)]
    e = {'cc': [n, ''.join(b36(b) + b36(c) + b36(v) + b36(i) for b, c, v, i in pick)]}
    if DEF.get(ds): e['d'] = DEF[ds]
    r = {}
    for k, cnt in ren[ds].items():
        tot = sum(cnt.values())
        top = [[(ko_show(w, surf[(ds, k, w)]) if k == 'ko' else surf[(ds, k, w)].most_common(1)[0][0]) if surf[(ds, k, w)] else w, m] for w, m in cnt.most_common(6) if (m >= 2 and m / tot >= 0.02) or m / tot >= 0.2 or tot <= 3][:5]
        merged = {}
        for w, m in top: merged[w] = merged.get(w, 0) + m
        top = sorted(([w, m] for w, m in merged.items()), key=lambda x: -x[1])
        if top: r[k] = top
    if r: e['r'] = r
    # meaning in each app language, from the renderings grouped under dictionary forms (tools/meanings.py)
    # little words (the, and, in, which ...) have no meaning of their own to show
    g0 = [x for x in re.split(r'[^a-z]+', (GLOSS.get(ds) or '').lower()) if x]
    if g0[:1] == ['to'] and len(g0) > 1: g0 = g0[1:]                 # "to love", "to create": verbs
    little = ds.startswith(('H9', 'H0853')) or not g0 or g0[0] in LITTLE
    m = {} if little else {k: meanings.headwords(k, [(cnt, surf[(ds, k, key)]) for key, cnt in ren[ds][k].items() if surf[(ds, k, key)]], name=ds in NAMES) for k in meanings.UI if ren[ds].get(k)}
    m = {k: v for k, v in m.items() if v}
    if m: e['m'] = m
    shards[int(re.match(r'[HG]0*(\d+)', ds).group(1)) % 4][ds] = e
for s in range(4):
    json.dump(shards[s], open(f'{D}ox{s}.json', 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
print('words', len(occ), 'sizes', [os.path.getsize(f'{D}ox{s}.json') // 1024 for s in range(4)], 'KB', file=sys.stderr)
