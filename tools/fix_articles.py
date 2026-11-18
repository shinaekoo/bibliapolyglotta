# -*- coding: utf-8 -*-
"""관사(the·a·an)를 바로 뒤 낱말과 같은 한국어에 함께 건다.

한국어에는 관사가 없다. KJV 'the substance' 는 개역한글에서 '실상이요' 한 낱말이고,
'a bullock' 은 '수송아지' 한 낱말이다. 그래서 관사만 짝이 없이 남으면, 화면에서
명사를 눌렀을 때 영어 쪽이 반쪽만 켜진다.

규칙은 하나다 — 관사 바로 뒤 낱말이 걸려 있는 한국어에 관사도 같이 건다.
  * **더하기만 한다.** 관사가 이미 걸고 있던 짝은 건드리지 않는다.
  * 바로 뒤 낱말이 아무 데도 안 걸려 있으면 건너뛴다.
  * 영어가 축이므로 모든 언어에 같이 해 준다 (관사를 쓰는 라틴어·독일어 등은
    제 관사가 따로 있지만, 여기서 손대는 것은 '그 언어 낱말 ↔ 영어 관사' 짝이다).

usage: python3 tools/fix_articles.py [--dry] [--lang ko,la,...]
       build 순서: tools/fix_enders.py 다음, tools/fix_links.py 앞
       (손으로 고친 것이 언제나 마지막에 이기도록)
"""
import json, io, os, sys, unicodedata, collections

HERE = os.path.dirname(os.path.abspath(__file__))
D = os.path.join(HERE, '..', 'web', 'data') + '/'
TX = os.path.join(HERE, '..', 'text') + '/'
ART = {'the', 'a', 'an'}
LAIDX = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,18,19,20,21,22,23,26,27,28,30,31,32,33,34,35,36,37,38,
         39,40,41,42,43,46,47,48,49,50,51,52,53,54,55,56,57,58,59,60,61,62,63,64,65,66,67,68,69,70,71,72]
ALL = ['or', 'la', 'de', 'fr', 'ko', 'zh', 'es', 'it', 'ru', 'ja', 'pt']


def toks(s):
    out, cur = [], []
    s = s or ''
    for i, ch in enumerate(s):
        if unicodedata.category(ch)[0] in ('L', 'M'):
            cur.append(ch)
        elif (ch == '–' and cur and i + 1 < len(s)
              and unicodedata.category(s[i + 1])[0] in ('L', 'M')):
            cur.append(ch)
        elif cur:
            out.append(''.join(cur)); cur = []
    if cur: out.append(''.join(cur))
    return out


def main():
    dry = '--dry' in sys.argv
    langs = ALL
    if '--lang' in sys.argv:
        langs = sys.argv[sys.argv.index('--lang') + 1].split(',')
    added = collections.Counter()
    seen = collections.Counter()
    for bb in range(66):
        ap = f'{D}al{bb:02d}.json'
        al = json.load(io.open(ap, encoding='utf-8'))
        EN = json.load(io.open(f'{TX}en{bb:02d}.json', encoding='utf-8'))
        dirty = False
        for c, chap in enumerate(al['v']):
            if c >= len(EN): continue
            for v, rec in enumerate(chap):
                if not rec or v >= len(EN[c]): continue
                E = toks(EN[c][v])
                arts = [i for i, w in enumerate(E) if w.lower() in ART and i + 1 < len(E)]
                if not arts: continue
                seen['관사'] += len(arts)
                for lg, q in list(rec.items()):
                    if lg not in langs or not q: continue
                    e2k = collections.defaultdict(set)
                    have = set()
                    for i in range(0, len(q), 2):
                        e2k[q[i + 1]].add(q[i]); have.add((q[i], q[i + 1]))
                    new = []
                    for a in arts:
                        for k in sorted(e2k.get(a + 1, ())):
                            if (k, a) in have: continue
                            have.add((k, a)); new.append((k, a)); added[lg] += 1
                    if new:
                        rec[lg] = [x for p in sorted(have) for x in p]
                        dirty = True
        if dirty and not dry:
            json.dump(al, io.open(ap, 'w', encoding='utf-8'),
                      ensure_ascii=False, separators=(',', ':'))
    tot = sum(added.values())
    print(f'{"(시험) " if dry else ""}관사 자리 {seen["관사"]}곳 · 짝 {tot}개 더함')
    for lg, n in added.most_common():
        print(f'   {lg}: {n}')


if __name__ == '__main__':
    main()
