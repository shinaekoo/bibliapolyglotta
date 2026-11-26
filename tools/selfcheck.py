# -*- coding: utf-8 -*-
"""자료 자체점검 — 사람 없이 오류를 모은다.

밀어 올릴 때마다 돌려서, 자료가 깨졌는지와 맞댄 품질이 나빠졌는지 본다.
숫자를 tools/selfcheck.json(기준선)과 견주어 **나빠지면 알려 준다**.

    python3 tools/selfcheck.py              # 점검하고 기준선과 견준다
    python3 tools/selfcheck.py --save       # 지금 숫자를 기준선으로 삼는다
    python3 tools/selfcheck.py --json       # 숫자만 JSON 으로

돌려주는 값
    0  이상 없음(또는 좋아짐)
    1  나빠졌다 — 사람이 봐야 한다
    2  자료가 깨졌다 — 반드시 고쳐야 한다

깨짐(반드시 0이어야 하는 것)
    bad_range   짝 번호가 낱말 수를 넘음
    bad_parse   al*.json 을 못 읽음
    bad_shape   장·절 수가 본문과 어긋남
품질(늘거나 줄기를 지켜보는 것)
    ko_empty    짝이 없는 한국어 낱말 수
    en_zero     성경 전체에서 한 번도 안 걸린 영어 낱말 가지 수
    low30       맞댄 비율 30% 이하인 절 수
    twin        같은 영어 낱말 한 벌이 한국어 둘을 쥐고 다른 벌이 빈 곳
    neg         되풀이 부정문에서 부정어가 뭉친 곳
"""
import collections
import io
import json
import os
import re
import sys
import unicodedata

D = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
BASE = os.path.join(D, 'tools/selfcheck.json')
# 품질 숫자가 이만큼 넘게 나빠지면 알린다(낱말 몇 개 손보다 생기는 흔들림은 넘긴다)
SLACK = {'ko_empty': 200, 'en_zero': 20, 'low30': 3, 'twin': 50, 'neg': 20}
ENEG = {'not', 'neither', 'nor', 'never', 'cannot'}
KNEG = re.compile(r'(아니하|아니할|아니함|아니|않|못하|못할|않으|없으|없거|없나|없느|없어|없음'
                  r'|말라|말지|말고|말며|말아|마시|마소|마라|마옵)')
STOP = set('''the a an and or but of to in on at for with by from as that this these those
i me my mine we us our ours thou thee thy thine ye you your yours he him his she her hers
it its they them their theirs who whom whose which what
is am are was were be been being shall will may might can could would should do did does done
have has had not no nor so then there here all any every some such unto into upon out up down
o yea verily also even now when where while if because therefore thus one two'''.split())


def toks(s):
    """앱·fix_links 와 같은 낱말 끊기."""
    out, cur = [], []
    s = s or ''
    for i, ch in enumerate(s):
        if unicodedata.category(ch)[0] in ('L', 'M'):
            cur.append(ch)
        elif (ch == '–' and cur and i + 1 < len(s)
              and unicodedata.category(s[i + 1])[0] in ('L', 'M')):
            cur.append(ch)
        elif cur:
            out.append(''.join(cur))
            cur = []
    if cur:
        out.append(''.join(cur))
    return out


LAIDX = ([i for i in range(16)] + [18, 19, 20, 21, 22, 23, 26, 27, 28]
         + list(range(30, 44)) + list(range(46, 73)))


def run():
    m = collections.Counter()
    notes = []
    etot, elnk = collections.Counter(), collections.Counter()
    for bb in range(66):
        ap = os.path.join(D, 'web/data/al%02d.json' % bb)
        if not os.path.exists(ap):
            m['bad_parse'] += 1
            notes.append('al%02d.json 이 없습니다' % bb)
            continue
        try:
            al = json.load(io.open(ap, encoding='utf-8'))
            ko = json.load(io.open(os.path.join(D, 'text/ko%02d.json' % bb), encoding='utf-8'))
            en = json.load(io.open(os.path.join(D, 'text/en%02d.json' % bb), encoding='utf-8'))
        except Exception as e:
            m['bad_parse'] += 1
            notes.append('al%02d.json 을 못 읽음: %s' % (bb, e))
            continue
        V = al.get('v') or []
        if len(V) != len(en):
            m['bad_shape'] += 1
            notes.append('al%d: 장 수 %d, 영어 본문 %d' % (bb, len(V), len(en)))
        for ci, ch in enumerate(V):
            if ci >= len(ko) or ci >= len(en):
                break
            # 짝 번호는 영어를 가리키므로 영어 절 수와 맞아야 한다.
            # 한국어가 한 절 더 많은 곳이 있다(요삼 1:15, 계 12:18) — 번역본 차이다.
            if len(ch or []) != len(en[ci] or []):
                m['bad_shape'] += 1
                notes.append('al%d %d장: 절 수 %d, 영어 본문 %d'
                             % (bb, ci + 1, len(ch or []), len(en[ci] or [])))
            for vi, rec in enumerate(ch or []):
                if vi >= len(ko[ci]):
                    break
                KT, ET = toks(ko[ci][vi]), toks(en[ci][vi])
                if not ET:
                    continue
                pr = (rec or {}).get('ko') or []
                gk, ge = set(), set()
                for j in range(0, len(pr) - 1, 2):
                    x, y = pr[j], pr[j + 1]
                    if x >= len(KT) or y >= len(ET):
                        m['bad_range'] += 1
                        if len(notes) < 40:
                            notes.append('al%d %d:%d 짝 (%d,%d) 가 낱말 수(%d,%d)를 넘음'
                                         % (bb, ci + 1, vi + 1, x, y, len(KT), len(ET)))
                        continue
                    gk.add(x)
                    ge.add(y)
                if len(KT) >= 3:
                    m['ko_empty'] += len(KT) - len(gk)
                    if len(gk) / len(KT) <= 0.30:
                        m['low30'] += 1
                for i, w in enumerate(ET):
                    etot[w] += 1
                    if i in ge:
                        elnk[w] += 1
                # 같은 낱말 한 벌이 둘을 쥐고 다른 벌은 빈 곳
                e2k = collections.defaultdict(set)
                for j in range(0, len(pr) - 1, 2):
                    if pr[j] < len(KT) and pr[j + 1] < len(ET):
                        e2k[pr[j + 1]].add(pr[j])
                form = collections.defaultdict(list)
                for i, w in enumerate(ET):
                    form[w].append(i)
                for w, idxs in form.items():
                    if len(idxs) < 2 or w.lower() in STOP:
                        continue
                    if (any(len(e2k.get(i, ())) >= 2 for i in idxs)
                            and any(not e2k.get(i) for i in idxs)):
                        m['twin'] += 1
                # 되풀이 부정문에서 부정어가 뭉친 곳
                ei = [i for i, w in enumerate(ET) if w.lower() in ENEG]
                ki = [k for k, w in enumerate(KT) if KNEG.search(w)]
                if len(ei) >= 2 and len(ki) >= 2:
                    if (any(len(e2k.get(i, set()) & set(ki)) >= 2 for i in ei)
                            and any(not (e2k.get(i, set()) & set(ki)) for i in ei)):
                        m['neg'] += 1
    m['en_zero'] = sum(1 for w, n in etot.items() if not elnk[w])
    return dict(m), notes


def main(argv):
    cur, notes = run()
    order = ['bad_parse', 'bad_shape', 'bad_range',
             'ko_empty', 'en_zero', 'low30', 'twin', 'neg']
    if '--json' in argv:
        print(json.dumps({k: cur.get(k, 0) for k in order}, ensure_ascii=False, indent=1))
        return 0
    old = {}
    if os.path.exists(BASE):
        try:
            old = json.load(io.open(BASE, encoding='utf-8'))
        except Exception:
            old = {}
    if '--save' in argv:
        json.dump({k: cur.get(k, 0) for k in order},
                  io.open(BASE, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
        print('기준선을 지금 숫자로 삼았습니다 → tools/selfcheck.json')

    broke = sum(cur.get(k, 0) for k in ('bad_parse', 'bad_shape', 'bad_range'))
    worse = []
    print('%-12s %10s %10s  %s' % ('항목', '지금', '기준선', '견줌'))
    for k in order:
        n, o = cur.get(k, 0), old.get(k)
        if o is None:
            d = '(기준선 없음)'
        elif n == o:
            d = '그대로'
        elif n < o:
            d = '좋아짐 %+d' % (n - o)
        else:
            d = '나빠짐 %+d' % (n - o)
            if k in SLACK and n - o > SLACK[k]:
                worse.append((k, o, n))
            elif k not in SLACK:
                worse.append((k, o, n))
        print('%-12s %10d %10s  %s' % (k, n, '—' if o is None else o, d))

    if notes:
        print('\n깨진 자리 (앞 %d개):' % min(len(notes), 20))
        for x in notes[:20]:
            print('  ', x)

    if broke:
        print('\n자료가 깨졌습니다 — 반드시 고쳐야 합니다 (%d곳).' % broke)
        return 2
    if worse:
        print('\n나빠진 항목이 있습니다 — 사람이 봐야 합니다:')
        for k, o, n in worse:
            print('   %s  %d → %d' % (k, o, n))
        return 1
    print('\n이상 없습니다.')
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
