# -*- coding: utf-8 -*-
# 한글 낱말을 거친 로마자로 풀어, 안 걸린 영어 이름과 소리를 맞춘다.
import json, io, os, unicodedata, collections, difflib
exec(open('/tmp/one3.py').read().split('def run(')[0])
CHO='g kk n d tt r m b pp s ss  j jj ch k t p h'.split(' ')
CHO=['g','kk','n','d','tt','r','m','b','pp','s','ss','','j','jj','ch','k','t','p','h']
JUNG=['a','ae','ya','yae','eo','e','yeo','ye','o','wa','wae','oe','yo','u','weo','we','wi','yu','eu','yi','i']
JONG=['','g','kk','gs','n','nj','nh','d','l','lg','lm','lb','ls','lt','lp','lh','m','b','bs','s','ss','ng','j','ch','k','t','p','h']
def rom(s):
    o=[]
    for ch in s:
        c=ord(ch)-0xAC00
        if 0<=c<11172:
            o.append(CHO[c//588]+JUNG[(c%588)//28]+JONG[c%28])
        elif ch.isalpha(): o.append(ch.lower())
    return ''.join(o)
def norm(e):
    e=e.lower().replace('–','').replace('-','')
    for a,b in (('ph','p'),('th','t'),('ch','k'),('sh','s'),('ck','k'),('x','ks'),
                ('v','b'),('f','p'),('z','j'),('c','k'),('y','i'),('w','u')):
        e=e.replace(a,b)
    return e
def sim(a,b):
    a,b=norm(a),norm(b).replace('eu','').replace('ae','a').replace('eo','o')
    return difflib.SequenceMatcher(None,a,b).ratio()
zero={w for w,n in json.load(io.open('/tmp/zero.json',encoding='utf-8')) if w[:1].isupper()}
def lab(T,i):
    w=T[i]; n=sum(1 for j in range(i+1) if T[j]==w)
    return w if sum(1 for x in T if x==w)==1 else '%s#%d'%(w,n)
cand=collections.defaultdict(list)
for bb in range(66):
    p='web/data/al%d.json'%bb
    if not os.path.exists(p): continue
    al=json.load(io.open(p,encoding='utf-8'))
    en=json.load(io.open('text/en%d.json'%bb,encoding='utf-8'))
    ko=json.load(io.open('text/ko%d.json'%bb,encoding='utf-8'))
    for ci,ch in enumerate(al.get('v') or []):
        for vi,rec in enumerate(ch or []):
            try: ET=toks(en[ci][vi]); KT=toks(ko[ci][vi])
            except Exception: continue
            hit=[i for i,w in enumerate(ET) if w in zero]
            if not hit: continue
            pr=(rec or {}).get('ko') or []
            gk={pr[j] for j in range(0,len(pr)-1,2)}
            free=[k for k in range(len(KT)) if k not in gk and len(KT[k])>=2]
            if not free: continue
            for i in hit:
                if sum(1 for x in ET if x==ET[i])!=1: continue
                best=max(((sim(ET[i],rom(KT[k])),k) for k in free), default=(0,None))
                if best[0]>=0.62:
                    cand[(ET[i],KT[best[1]].rstrip('과와의을를이가은는에도로'))].append(
                        (bb,ci+1,vi+1,lab(ET,i),lab(KT,best[1]),round(best[0],2)))
print('소리가 맞는 짝 %d가지 (%d곳)'%(len(cand),sum(len(v) for v in cand.values())))
for (w,k),r in sorted(cand.items(), key=lambda x:-len(x[1])):
    print('   %-18s ↔ %-12s %2d곳  닮음 %.2f  %s'%(w,k,len(r),r[0][5],
          ' '.join('%s %d:%d'%(NM[x[0]],x[1],x[2]) for x in r[:2])))
json.dump([[k[0],k[1],v] for k,v in cand.items()], io.open('/tmp/roman.json','w',encoding='utf-8'), ensure_ascii=False)
