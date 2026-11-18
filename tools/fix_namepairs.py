# -*- coding: utf-8 -*-
"""한 절에 같은 이름이 두 번 이상 나와 짝이 한쪽에 몰린 자리를 순서대로 나눠 준다.

tools/fix_pairs.py 가 제자/disciples, 아들/son 같은 뚜렷한 짝에 하는 일을,
사람·지명 이름(web/data/pi.json, gi.json)에 대해 한다. 통계 정렬기는 같은 낱말이
한 절에 되풀이되면 첫 자리만 걸고 나머지를 버린다 — 고유명사 누락 481회 가운데
375회가 이 탓이다 (David 41, Jacob 24, Babylon 19, Israel 17, Moses 13 …).

안전 규칙 (fix_pairs.py 와 같은 생각):
  * 영어 쪽 개수와 한국어 쪽 개수가 **같을 때만** 손댄다. 다르면 어느 자리가
    짝인지 알 수 없으므로 세어만 보고 넘어간다 (--csv 로 받아볼 수 있다).
  * 이미 걸려 있는 짝은 **빼앗지도 지우지도 않는다**. n번째 영어가 비어 있을 때
    n번째 한국어에 짝을 더해 줄 뿐이다. 한국어 한 낱말이 영어 여러 낱말에
    걸리는 것은 정상이다.
  * 한국어 이름은 한 글자짜리를 쓰지 않는다 (롯·옥·온·돌 — '돌'이 stone 과
    겹치는 식으로 엉뚱한 낱말을 잡는다).

usage: python3 tools/fix_namepairs.py [--dry] [--csv 파일]
       build 순서: tools/fix_pairs.py 다음, tools/fix_enders.py 앞
"""
import json, io, os, sys, csv, unicodedata, collections

HERE = os.path.dirname(os.path.abspath(__file__))
D = os.path.join(HERE, '..', 'web', 'data') + '/'
TX = os.path.join(HERE, '..', 'text') + '/'


def toks(s):
    out, cur = [], []
    s = s or ''
    for i, ch in enumerate(s):
        if unicodedata.category(ch)[0] in ('L', 'M'):
            cur.append(ch)
        elif (ch == '–' and cur and i + 1 < len(s)
              and unicodedata.category(s[i + 1])[0] in ('L', 'M')):
            cur.append(ch)        # 낱말 속 엔대시 — Beth–el, Abed–nego
        elif cur:
            out.append(''.join(cur)); cur = []
    if cur: out.append(''.join(cur))
    return out


def names():
    """영어 이름 -> 한국어 이름. 영어는 대문자로 시작하는 것만, 한국어는 두 글자 이상."""
    out = {}
    for f in ('pi', 'gi'):
        for row in json.load(io.open(D + f + '.json', encoding='utf-8'))['n'].values():
            e, ko = (row[0] or '').strip(), (row[1] or '').strip()
            if e and ko and e[:1].isupper() and len(ko) >= 2:
                out.setdefault(e, ko)
    return out


def main():
    dry = '--dry' in sys.argv
    out_csv = None
    if '--csv' in sys.argv: out_csv = sys.argv[sys.argv.index('--csv') + 1]
    NM = names()
    added = 0
    left = []                       # 개수가 안 맞아 못 고친 자리
    for bb in range(66):
        ap = f'{D}al{bb:02d}.json'
        al = json.load(io.open(ap, encoding='utf-8'))
        EN = json.load(io.open(f'{TX}en{bb:02d}.json', encoding='utf-8'))
        KO = json.load(io.open(f'{TX}ko{bb:02d}.json', encoding='utf-8'))
        dirty = False
        for c, chap in enumerate(al['v']):
            for v, rec in enumerate(chap):
                if not rec or c >= len(EN) or v >= len(EN[c]): continue
                E = toks(EN[c][v])
                K = toks(KO[c][v]) if c < len(KO) and v < len(KO[c]) else []
                if not E or not K: continue
                q = rec.get('ko') or []
                have = {(q[i], q[i + 1]) for i in range(0, len(q), 2)}
                enlinked = {y for _, y in have}
                for e in sorted({w for w in E if w in NM}):
                    ko = NM[e]
                    ei = [i for i, w in enumerate(E) if w == e]
                    ki = [i for i, w in enumerate(K) if w.startswith(ko)]
                    if not ki: continue
                    if all(i in enlinked for i in ei): continue     # 빈 자리 없음
                    if len(ei) != len(ki):
                        left.append((bb, c + 1, v + 1, e, ko, len(ei), len(ki),
                                     sum(1 for i in ei if i not in enlinked)))
                        continue
                    for a, b in zip(ei, ki):
                        if a in enlinked: continue                  # 이미 걸린 건 그대로
                        if (b, a) in have: continue
                        have.add((b, a)); added += 1; dirty = True
                if dirty:
                    rec['ko'] = [x for p in sorted(have) for x in p]
        if dirty and not dry:
            json.dump(al, io.open(ap, 'w', encoding='utf-8'),
                      ensure_ascii=False, separators=(',', ':'))
    print(f'{"(시험) " if dry else ""}이름 짝 {added}개 더함 · 개수가 안 맞아 넘긴 자리 {len(left)}곳')
    if out_csv:
        with io.open(out_csv, 'w', encoding='utf-8-sig', newline='') as f:
            w = csv.writer(f)
            w.writerow(['책번호', '장', '절', '영어이름', '한국어이름', '영어수', '한국어수', '빈자리'])
            w.writerows(sorted(left))
        print('  못 고친 자리를', out_csv, '에 적었다')


if __name__ == '__main__':
    main()
