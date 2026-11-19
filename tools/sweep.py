# -*- coding: utf-8 -*-
# 같은 영어 낱말이 한 절에 두 번 이상 나오는데, 그 중 한 벌이 한국어 두 자리 이상을
# 쥐고 있고 다른 벌은 아무것도 쥐지 않은 곳 — 되풀이되는 뒤틀림의 기계적 흔적.
import json, io, os, sys, unicodedata, collections

def toks(s):
    out, cur = [], []
    s = s or ''
    for i, ch in enumerate(s):
        if unicodedata.category(ch)[0] in ('L','M'):
            cur.append(ch)
        elif (ch=='–' and cur and i+1<len(s)
              and unicodedata.category(s[i+1])[0] in ('L','M')):
            cur.append(ch)
        elif cur:
            out.append(''.join(cur)); cur=[]
    if cur: out.append(''.join(cur))
    return out

BOOKS=json.load(io.open('text/books.json',encoding='utf-8')) if os.path.exists('text/books.json') else None
hits=[]
for bb in range(66):
    ap='web/data/al%d.json'%bb
    if not os.path.exists(ap): continue
    al=json.load(io.open(ap,encoding='utf-8'))
    try:
        ko=json.load(io.open('text/ko%d.json'%bb,encoding='utf-8'))
        en=json.load(io.open('text/en%d.json'%bb,encoding='utf-8'))
    except Exception: continue
    V=al.get('v') or []
    for ci,ch in enumerate(V):
        for vi,rec in enumerate(ch or []):
            pr=(rec or {}).get('ko')
            if not pr: continue
            try:
                ET=toks(en[ci][vi]); KT=toks(ko[ci][vi])
            except Exception: continue
            c,v=ci+1,vi+1
            e2k=collections.defaultdict(set)
            for i in range(0,len(pr)-1,2):
                e2k[pr[i+1]].add(pr[i])
            form=collections.defaultdict(list)
            for i,w in enumerate(ET): form[w].append(i)
            for w,idxs in form.items():
                if len(idxs)<2: continue
                multi=[i for i in idxs if len(e2k.get(i,()))>=2]
                empty=[i for i in idxs if not e2k.get(i)]
                if multi and empty:
                    hits.append((bb,c,v,w,
                        [(i,sorted(KT[k] for k in e2k[i] if k<len(KT))) for i in multi],
                        empty))
print('흔적 %d곳'%len(hits))
cnt=collections.Counter(h[3] for h in hits)
print('잦은 낱말:', ', '.join('%s(%d)'%(w,n) for w,n in cnt.most_common(25)))
bk=collections.Counter(h[0] for h in hits)
print('책별 상위:', ', '.join('%d권:%d'%(b+1,n) for b,n in bk.most_common(12)))
json.dump(hits, io.open('/tmp/sweep.json','w',encoding='utf-8'), ensure_ascii=False)
