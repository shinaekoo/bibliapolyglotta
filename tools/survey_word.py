# -*- coding: utf-8 -*-
import json, io, os, unicodedata, collections, sys
def toks(s):
    out,cur=[],[]; s=s or ''
    for i,ch in enumerate(s):
        if unicodedata.category(ch)[0] in ('L','M'): cur.append(ch)
        elif (ch=='–' and cur and i+1<len(s) and unicodedata.category(s[i+1])[0] in ('L','M')): cur.append(ch)
        elif cur: out.append(''.join(cur)); cur=[]
    if cur: out.append(''.join(cur))
    return out
TARGET=set(sys.argv[1].split(','))
rows=[]; tot=0; linked=0
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
            hit=[i for i,w in enumerate(ET) if w in TARGET]
            if not hit: continue
            pr=(rec or {}).get('ko') or []
            e2k=collections.defaultdict(set)
            for j in range(0,len(pr)-1,2): e2k[pr[j+1]].add(pr[j])
            tot+=len(hit)
            empty=[i for i in hit if not e2k.get(i)]
            linked+=len(hit)-len(empty)
            if empty: rows.append((bb,ci+1,vi+1,len(empty),len(hit)))
print('%s 나온 자리 %d개 · 걸린 자리 %d개 · 빈 자리 %d개'%('/'.join(sorted(TARGET)),tot,linked,tot-linked))
print('빈 자리가 있는 절 %d개'%len(rows))
NM="창세기 출애굽기 레위기 민수기 신명기 여호수아 사사기 룻기 사무엘상 사무엘하 열왕기상 열왕기하 역대상 역대하 에스라 느헤미야 에스더 욥기 시편 잠언 전도서 아가 이사야 예레미야 예레미야애가 에스겔 다니엘 호세아 요엘 아모스 오바댜 요나 미가 나훔 하박국 스바냐 학개 스가랴 말라기 마태복음 마가복음 누가복음 요한복음 사도행전 로마서 고린도전서 고린도후서 갈라디아서 에베소서 빌립보서 골로새서 데살로니가전서 데살로니가후서 디모데전서 디모데후서 디도서 빌레몬서 히브리서 야고보서 베드로전서 베드로후서 요한일서 요한이서 요한삼서 유다서 요한계시록".split()
c=collections.Counter(r[0] for r in rows)
print('책별 상위:', ', '.join('%s %d'%(NM[b],n) for b,n in c.most_common(12)))
json.dump(rows, io.open('/tmp/wrows.json','w',encoding='utf-8'))
