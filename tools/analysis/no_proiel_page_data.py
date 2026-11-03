import sys, json, re
sys.path.insert(0, '/tmp/claude-0/repl')
import latin_test as T
from latin_test import F, ENTRIES, W, LXL, BYD, AL, NEWAL, OEN, LAORIG, ROW, LAIDX, TX, D
SUB = T.SUB
K_CASE = {'NOM': '주격', 'GEN': '속격', 'DAT': '여격', 'ACC': '대격', 'ABL': '탈격', 'VOC': '호격', 'LOC': '처격'}
K_NUM = {'S': '단수', 'P': '복수'}; K_GEN = {'M': '남성', 'F': '여성', 'N': '중성'}
K_TENSE = {'PRES': '현재', 'IMPF': '미완료', 'FUT': '미래', 'PERF': '완료', 'PLUP': '과거완료', 'FUTP': '미래완료'}
K_VOICE = {'ACTIVE': '능동', 'PASSIVE': '수동'}; K_MOOD = {'IND': '직설법', 'SUB': '접속법', 'IMP': '명령법', 'INF': '부정사', 'PPL': '분사'}
K_POS = {'N': '명사', 'ADJ': '형용사', 'V': '동사', 'VPAR': '분사', 'PREP': '전치사', 'CONJ': '접속사', 'ADV': '부사', 'PRON': '대명사',
         'NUM': '수사', 'INTERJ': '감탄사', 'PN': '고유명사', 'X': '미상', 'MAN': '수동 검토'}
def label(code):
    p = [x for x in code.split('.') if not re.match(r'^k\d+$', x) and x != 'D']
    if not p: return ''
    pos = K_POS.get(p[0], p[0]); r = p[1:]
    if p[0] == 'PREP': return pos + (f' (+{K_CASE.get(r[0], r[0])})' if r and r[0] else '')
    if p[0] in ('N', 'ADJ', 'PRON', 'NUM'):
        return ' · '.join([pos] + [K_CASE.get(r[0], '')] * bool(r and r[0] in K_CASE) + [K_NUM.get(r[1], '')] * bool(len(r) > 1 and r[1] in K_NUM) + [K_GEN.get(r[2], '')] * bool(len(r) > 2 and r[2] in K_GEN))
    if p[0] == 'V':
        t, vo, m = (r + ['', '', ''])[:3]
        pn = f'{r[3]}인칭 {K_NUM.get(r[4], "")}' if len(r) > 4 and r[3] in '123' else ''
        return ' · '.join(x for x in [pos, K_TENSE.get(t, ''), K_VOICE.get(vo, ''), K_MOOD.get(m, ''), pn] if x)
    if p[0] == 'VPAR':
        cs, nm, g, t, vo = (r + [''] * 5)[:5]
        return ' · '.join(x for x in [pos, K_TENSE.get(t, ''), K_VOICE.get(vo, ''), K_CASE.get(cs, ''), K_NUM.get(nm, ''), K_GEN.get(g, '')] if x)
    return pos
def clean_en(s): return re.sub(r'\s+', ' ', (s or '')).strip()[:110]
LANGS = ['or', 'la', 'en', 'ko', 'es', 'ja']
def chapter(b, c):
    tx = {k: json.load(open(f'{TX}{k}{(LAIDX[b] if k == "la" else b):02d}.json'))[c-1] for k in ('la', 'en', 'ko', 'es', 'ja')}
    al_o, al_n = AL[b], NEWAL[b]
    gold = al_o['lx'][str(c)]
    ver = []
    for v in range(1, len(tx['en']) + 1):
        texts = {k: tx[k][v-1] if v <= len(tx[k]) else '' for k in tx}
        texts['or'] = al_o['or'][c-1][v-1]
        ow = (al_o['ow'][c-1][v-1] or '').split(' ')
        owords = W.findall(texts['or'])
        lk = lambda rec: {k: rec.get(k, []) for k in LANGS if k != 'en'}
        old_links, new_links = lk(al_o['v'][c-1][v-1]), lk(al_n['v'][c-1][v-1])
        # Latin analysis
        inter, gdfa = LAORIG[ROW[(b, c, v)]]
        of = T.orig_feats(b, c, v)
        lp = al_n['v'][c-1][v-1].get('la', []); la2en = {}
        for q in range(0, len(lp), 2): la2en.setdefault(lp[q], set()).add(lp[q+1])
        en2k = {}
        for k, j in OEN.get(f'{b}:{c}:{v}', []): en2k.setdefault(j, set()).add(k)
        def ks_of(i):
            ks = {k for ii, k in inter if ii == i} | {k for j in la2en.get(i, ()) for k in en2k.get(j, ())}
            return sorted(ks or {k for ii, k in gdfa if ii == i})
        feats_of = lambda i: [of[k] for k in ks_of(i) if k < len(of)]
        new = T.analyse(texts['la'], feats_of, True)
        g = gold.get(f'v{v}', [])
        subs = SUB.get(f'{b}:{c}:{v}', [])
        toks = []
        for i, nt in enumerate(new):
            gt = g[i] if i < len(g) else None
            od = (LXL[gt[0]] or ['?', '', '', '', ''])[0] if gt else ''
            nd = nt[2] or nt[0]
            row = LXL[BYD[nd]] if nd in BYD else None
            wh = clean_en(ENTRIES[nt[3]['idx']]['mean']) if len(nt) > 3 and nt[3] else ''
            ko = row[1] if row else ''
            # the original words this Latin word stands for (Strong's-free links), with STEPBible's lexicon
            orig = []
            for k in ks_of(i):
                if k >= len(subs): continue
                wi, st = subs[k]
                ds = ow[wi].split('|')[0] if wi < len(ow) else ''
                lx = al_o['og'].get(ds) or al_o['og'].get(re.sub(r'[A-Z]$', '', ds) if ds else '', None)
                if lx and (wi < len(owords)):
                    item = [owords[wi], lx[0], lx[1], lx[2]]
                    if item not in orig: orig.append(item)
            toks.append({'w': nt[0], 'old': [od, label(gt[3]) if gt else '', gt[4] if gt else None], 'new': [nd, label(nt[1])],
                         'ko': ko, 'wh': wh, 'orig': orig[:2]})
        ver.append({'v': v, 'tx': texts, 'old': old_links, 'new': new_links, 'lat': toks})
    return ver
out = {'gen1': chapter(0, 1), 'jhn1': chapter(42, 1)}
json.dump(out, open('/tmp/claude-0/repl/page_data.json', 'w'), ensure_ascii=False, separators=(',', ':'))
import os; print(os.path.getsize('/tmp/claude-0/repl/page_data.json') // 1024, 'KB')
v = out['jhn1'][0]; print(v['lat'][:4]); print({k: v['old'][k][:10] for k in v['old']}); print({k: v['new'][k][:10] for k in v['new']})
