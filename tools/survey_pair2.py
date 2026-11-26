# -*- coding: utf-8 -*-
# 넓힌 그물: 한국어 낱말이 줄기로 시작하면 합성어도 받아들인다(놋그릇·놋문·다윗성).
import json, io, os, unicodedata, collections, sys
exec(open('/tmp/one3.py').read().split('def run(')[0])
def label_(T,i):
    w=T[i]; n=sum(1 for j in range(i+1) if T[j]==w)
    return w if sum(1 for x in T if x==w)==1 else '%s#%d'%(w,n)
out=[]
for spec in sys.argv[1:]:
    ens,kstem,name=spec.split('|'); ens=set(ens.split(','))
    got=[]
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
                ei=[i for i,w in enumerate(ET) if w in ens]
                ki=[i for i,w in enumerate(KT) if w.startswith(kstem)]
                if len(ei)!=1 or len(ki)!=1: continue
                pr=(rec or {}).get('ko') or []
                e2k=collections.defaultdict(set)
                for j in range(0,len(pr)-1,2): e2k[pr[j+1]].add(pr[j])
                if ki[0] in e2k.get(ei[0],()): continue
                got.append((bb,ci+1,vi+1,label_(ET,ei[0]),label_(KT,ki[0]),
                            KT[ki[0]], sorted(KT[k] for k in e2k.get(ei[0],()) if k<len(KT))))
    print('[%s] 넓힌 그물로 고칠 1:1 %d곳'%(name,len(got)))
    for x in got:
        print('   %s %d:%d  %s → %s%s'%(NM[x[0]],x[1],x[2],x[3],x[5],
              '   (빼앗김: '+'·'.join(x[6])+')' if x[6] else ''))
    out+= [(x[0],x[1],x[2],x[3],x[4]) for x in got]
json.dump(out, io.open('/tmp/one2.json','w',encoding='utf-8'), ensure_ascii=False)
