# -*- coding: utf-8 -*-
# 한 번도 안 걸린 영어 이름 꼴마다, 그 절들에서 늘 함께 비어 있는 한국어 낱말을 찾는다.
import json, io, os, unicodedata, collections
exec(open('/tmp/one3.py').read().split('def run(')[0])
zero={w for w,n in json.load(io.open('/tmp/zero.json',encoding='utf-8')) if n>=3 and w[:1].isupper()}
box=collections.defaultdict(list)
for bb in range(66):
    p='web/data/al%02d.json'%bb
    if not os.path.exists(p): continue
    al=json.load(io.open(p,encoding='utf-8'))
    en=json.load(io.open('text/en%02d.json'%bb,encoding='utf-8'))
    ko=json.load(io.open('text/ko%02d.json'%bb,encoding='utf-8'))
    for ci,ch in enumerate(al.get('v') or []):
        for vi,rec in enumerate(ch or []):
            try: ET=toks(en[ci][vi]); KT=toks(ko[ci][vi])
            except Exception: continue
            hit=zero & set(ET)
            if not hit: continue
            pr=(rec or {}).get('ko') or []
            gk={pr[j] for j in range(0,len(pr)-1,2)}
            free=[KT[k] for k in range(len(KT)) if k not in gk]
            for w in hit:
                if sum(1 for x in ET if x==w)==1: box[w].append((bb,ci+1,vi+1,free))
res=[]
for w,rows in box.items():
    c=collections.Counter()
    for _,_,_,free in rows:
        for k in set(x.rstrip('과와의을를이가은는에서도로') or x for x in free): c[k]+=1
    if not c: continue
    k,n=c.most_common(1)[0]
    if n>=3 and n/len(rows)>=0.6 and len(k)>=2:
        res.append((w,k,n,len(rows)))
res.sort(key=lambda x:-x[3])
print('이름 뒷말로 보이는 짝 %d가지:'%len(res))
for w,k,n,t in res: print('   %-16s ↔ %-10s  %d/%d절'%(w,k,n,t))
json.dump(res, io.open('/tmp/guess.json','w',encoding='utf-8'), ensure_ascii=False)
