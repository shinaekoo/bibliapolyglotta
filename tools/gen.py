# -*- coding: utf-8 -*-
import json, io, unicodedata, collections
def toks(s):
    out,cur=[],[]; s=s or ''
    for i,ch in enumerate(s):
        if unicodedata.category(ch)[0] in ('L','M'): cur.append(ch)
        elif (ch=='–' and cur and i+1<len(s) and unicodedata.category(s[i+1])[0] in ('L','M')): cur.append(ch)
        elif cur: out.append(''.join(cur)); cur=[]
    if cur: out.append(''.join(cur))
    return out
def label(T,i):
    w=T[i]; n=sum(1 for j in range(i+1) if T[j]==w)
    return w if sum(1 for x in T if x==w)==1 else '%s#%d'%(w,n)
strict=json.load(io.open('/tmp/sweep_strict.json',encoding='utf-8'))
by=collections.defaultdict(list)
for h in strict: by[h[0]].append(h)
out=[]; later=[]; flip=0
for bb in sorted(by):
    en=json.load(io.open('text/en%d.json'%bb,encoding='utf-8'))
    ko=json.load(io.open('text/ko%d.json'%bb,encoding='utf-8'))
    al=json.load(io.open('web/data/al%d.json'%bb,encoding='utf-8'))
    for bb_,c,v,w,i,ks,empty in by[bb]:
        ET=toks(en[c-1][v-1]); KT=toks(ko[c-1][v-1])
        pr=al['v'][c-1][v-1]['ko']
        e2k=collections.defaultdict(list)
        for j in range(0,len(pr)-1,2): e2k[pr[j+1]].append(pr[j])
        held=sorted(set(e2k[i]))
        occ=[j for j,x in enumerate(ET) if x==w]
        if len(held)!=2 or len(occ)!=2:
            later.append((bb,c,v,w)); continue
        # 주변에 이미 걸린 영어 낱말로 기대 위치를 잡는다 — 어순이 뒤집힌 절 대비
        def anchor(e):
            best=None
            for d in range(1,6):
                for q in (e-d,e+d):
                    if q in e2k and q not in occ and e2k[q]:
                        m=sum(e2k[q])/len(e2k[q])
                        if best is None: best=m
                if best is not None: return best
            return None
        a0,a1=anchor(occ[0]),anchor(occ[1])
        pair=[(occ[0],held[0]),(occ[1],held[1])]
        if a0 is not None and a1 is not None:
            d1=abs(a0-held[0])+abs(a1-held[1]); d2=abs(a0-held[1])+abs(a1-held[0])
            if d2<d1: pair=[(occ[0],held[1]),(occ[1],held[0])]; flip+=1
        for e,k in pair:
            out.append("    dict(ref=(%d, %d, %d), lang='ko', en=%r, words=[%r]),"%(bb,c,v,label(ET,e),label(KT,k)))
print('적용 %d곳 (%d항목), 어순 뒤집힘 감지 %d곳, 편집기로 넘김 %d곳'%(len(out)//2,len(out),flip,len(later)))
io.open('/tmp/blk.txt','w',encoding='utf-8').write(
  "    # ---- 같은 영어 낱말 두 벌이 한국어 두 자리를 나눠 갖게 쪼갬 (일괄) ----\n"
  "    # 첫째 벌이 두 자리를 다 쥐고 뒤쪽 벌이 통째로 비어 있던 곳.\n"
  "    # 줄기가 같고 꼬리만 조사/어미로 다른 짝만 골랐고, 주변에 이미 걸린\n"
  "    # 영어 낱말로 기대 위치를 잡아 어순이 뒤집힌 절은 자리를 맞바꿨다.\n"+'\n'.join(out)+'\n')
json.dump(later, io.open('/tmp/sweep_later.json','w',encoding='utf-8'), ensure_ascii=False)
