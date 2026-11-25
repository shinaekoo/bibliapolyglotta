# -*- coding: utf-8 -*-
import json, io, os, unicodedata, collections
exec(open('/tmp/one3.py').read().split('def run(')[0])
tot=collections.Counter(); lnk=collections.Counter()
for bb in range(66):
    p='web/data/al%d.json'%bb
    if not os.path.exists(p): continue
    al=json.load(io.open(p,encoding='utf-8'))
    en=json.load(io.open('text/en%d.json'%bb,encoding='utf-8'))
    for ci,ch in enumerate(al.get('v') or []):
        for vi,rec in enumerate(ch or []):
            try: ET=toks(en[ci][vi])
            except Exception: continue
            pr=(rec or {}).get('ko') or []
            got={pr[j+1] for j in range(0,len(pr)-1,2)}
            for i,w in enumerate(ET):
                tot[w]+=1
                if i in got: lnk[w]+=1
z=[(w,n) for w,n in tot.items() if lnk[w]==0]
z.sort(key=lambda x:-x[1])
print('한 번도 안 걸린 영어 낱말 %d가지 (전체 %d가지 중)'%(len(z),len(tot)))
print('잦은 것 40가지:')
for w,n in z[:40]: print('   %-16s %d번' % (w,n))
low=[(w,n,lnk[w]) for w,n in tot.items() if n>=120 and lnk[w]/n<0.35]
low.sort(key=lambda x:x[2]/x[1])
print('\n120번 넘게 나오는데 연결률 35%% 아래인 낱말:')
for w,n,l in low[:30]: print('   %-14s %5d번 중 %4d (%.0f%%)'%(w,n,l,100*l/n))
json.dump(z, io.open('/tmp/zero.json','w',encoding='utf-8'), ensure_ascii=False)
