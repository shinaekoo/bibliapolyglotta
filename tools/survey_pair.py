# -*- coding: utf-8 -*-
# 한 절에 영어 낱말도 한 번, 한국어 낱말도 한 번만 나오는데 안 걸린 자리를 찾는다.
import json, io, os, unicodedata, collections, sys
def toks(s):
    out,cur=[],[]; s=s or ''
    for i,ch in enumerate(s):
        if unicodedata.category(ch)[0] in ('L','M'): cur.append(ch)
        elif (ch=='–' and cur and i+1<len(s) and unicodedata.category(s[i+1])[0] in ('L','M')): cur.append(ch)
        elif cur: out.append(''.join(cur)); cur=[]
    if cur: out.append(''.join(cur))
    return out
JOSA=set(['','은','는','이','가','을','를','의','에','에서','에게','에게서','에는','에도','에게는',
 '와','과','도','로','으로','로서','으로서','만','까지','부터','께','께서','께로','께는','께서는',
 '이라','이요','이며','이니','이신','이시니','이시며','아','야','여','이여','이시여',
 '들','들은','들이','들을','들의','들에','들에게','들과','들도','들로','들만','들에서',
 '마다','조차','밖에','처럼','같이','보다','이라도','에다','한테','이라는','라는','에게나','이라고','라고',
 '께라','이라하','인','일','임','이냐','이뇨','이온','에서는','으로는','로는','이시라'])
NM="창세기 출애굽기 레위기 민수기 신명기 여호수아 사사기 룻기 사무엘상 사무엘하 열왕기상 열왕기하 역대상 역대하 에스라 느헤미야 에스더 욥기 시편 잠언 전도서 아가 이사야 예레미야 예레미야애가 에스겔 다니엘 호세아 요엘 아모스 오바댜 요나 미가 나훔 하박국 스바냐 학개 스가랴 말라기 마태복음 마가복음 누가복음 요한복음 사도행전 로마서 고린도전서 고린도후서 갈라디아서 에베소서 빌립보서 골로새서 데살로니가전서 데살로니가후서 디모데전서 디모데후서 디도서 빌레몬서 히브리서 야고보서 베드로전서 베드로후서 요한일서 요한이서 요한삼서 유다서 요한계시록".split()

def run(ens, kstem, label):
    ens=set(ens.split(',')); found=[]; stat=collections.Counter()
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
                ei=[i for i,w in enumerate(ET) if w in ens]
                ki=[i for i,w in enumerate(KT)
                      if w.startswith(kstem) and w[len(kstem):] in JOSA]
                if not ei: continue
                pr=(rec or {}).get('ko') or []
                e2k=collections.defaultdict(set)
                for j in range(0,len(pr)-1,2): e2k[pr[j+1]].add(pr[j])
                if len(ei)==1 and len(ki)==1:
                    if ki[0] in e2k.get(ei[0],()): stat['이미 걸림']+=1
                    else:
                        stat['고칠 1:1']+=1
                        found.append((bb,ci+1,vi+1,ei[0],ki[0],ET[ei[0]],KT[ki[0]],
                                      sorted(KT[k] for k in e2k.get(ei[0],()) if k<len(KT))))
                elif len(ki)==0: stat['한국어에 없음']+=1
                else: stat['여러 벌']+=1
    print('[%s] '%label + ' · '.join('%s %d'%(k,v) for k,v in stat.most_common()))
    return found

out={}
for spec in sys.argv[1:]:
    ens,kstem,label=spec.split('|')
    out[label]=run(ens,kstem,label)
json.dump(out, io.open('/tmp/one1.json','w',encoding='utf-8'), ensure_ascii=False)
for label,f in out.items():
    print('\n--- %s: 고칠 %d곳, 앞 8개 ---'%(label,len(f)))
    for x in f[:8]:
        print('   %s %d:%d  %s(%d) ↔ %s(%d)%s'%(NM[x[0]],x[1],x[2],x[5],x[3],x[6],x[4],
              '   지금 영어가 쥔 것: '+'·'.join(x[7]) if x[7] else '   (지금 아무것도 안 쥠)'))
