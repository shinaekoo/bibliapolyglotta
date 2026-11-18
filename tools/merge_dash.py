# -*- coding: utf-8 -*-
"""엔대시(–)로 이어진 낱말을 한 낱말로 합치는 1회성 이행 도구.

KJV 본문은 고유명사를 ASCII 하이픈이 아니라 엔대시로 잇는다 (Beth–el, Abed–nego,
Beer–sheba …). 러시아어 시노드역도 что–нибудь, из–за 처럼 낱말 속에 엔대시를 쓴다.
낱말 가르기가 /[\\p{L}\\p{M}]+/ 였던 탓에 이런 이름이 두 낱말로 쪼개져서
한국어 '벧엘' 한 낱말과 짝이 맞지 않았다 (영어 775곳, 러시아어 739곳).

낱말 가르기를 /[\\p{L}\\p{M}]+(?:–[\\p{L}\\p{M}]+)*/ 로 바꾸면 영어 낱말 번호가
밀리므로, 이미 쌓아 둔 al*.json 의 짝 번호를 여기서 새 번호로 옮겨 준다.
영어가 축이라 모든 언어의 짝에서 뒷번호(영어 쪽)를 손봐야 하고,
러시아어는 제 쪽 앞번호도 손봐야 한다.

한 번만 돌리면 되고, 두 번 돌려도 결과는 같다 (이미 합쳐져 있으면 map 이 항등).
"""
import json, io, os, sys, unicodedata, collections

DASH = '–'
LANGS = ["or", "la", "en", "de", "fr", "ko", "zh", "es", "it", "ru", "ja", "pt"]


def spans_old(s):
    """옛 방식: 글자·결합기호가 이어진 덩어리."""
    out, st = [], None
    for i, ch in enumerate(s or ''):
        if unicodedata.category(ch)[0] in ('L', 'M'):
            if st is None: st = i
        elif st is not None:
            out.append((st, i)); st = None
    if st is not None: out.append((st, len(s)))
    return out


def spans_new(s):
    """새 방식: 글자 사이에 낀 엔대시는 낱말 속 글자로 친다."""
    old = spans_old(s)
    out = []
    for sp in old:
        if out and sp[0] - out[-1][1] == 1 and s[out[-1][1]] == DASH:
            out[-1] = (out[-1][0], sp[1])
        else:
            out.append(list(sp) if False else (sp[0], sp[1]))
        out[-1] = tuple(out[-1])
    # 위 루프가 튜플을 못 바꾸므로 다시 한 번 정리
    merged = []
    for sp in old:
        if merged and sp[0] - merged[-1][1] == 1 and s[merged[-1][1]] == DASH:
            merged[-1] = (merged[-1][0], sp[1])
        else:
            merged.append(sp)
    return merged


def idxmap(s):
    """옛 낱말번호 -> 새 낱말번호. 바뀔 게 없으면 None."""
    old, new = spans_old(s), spans_new(s)
    if len(old) == len(new): return None
    m, j = [], 0
    for a, b in old:
        while not (new[j][0] <= a and b <= new[j][1]): j += 1
        m.append(j)
    return m


def main():
    dry = '--dry' in sys.argv
    tot_v = tot_p = 0
    for bb in range(66):
        ap = f'web/data/al{bb:02d}.json'
        al = json.load(io.open(ap, encoding='utf-8'))
        TX = {}
        for lg in LANGS:
            p = f'text/{lg}{bb:02d}.json'
            if os.path.exists(p): TX[lg] = json.load(io.open(p, encoding='utf-8'))
        dirty = False
        for c, chap in enumerate(al['v']):
            for v, rec in enumerate(chap):
                if not rec: continue
                def mp(lg):
                    T = TX.get(lg)
                    if not T or c >= len(T) or v >= len(T[c]): return None
                    return idxmap(T[c][v])
                me = mp('en')
                maps = {lg: mp(lg) for lg in rec}
                if me is None and not any(maps.values()): continue
                for lg, q in list(rec.items()):
                    mo = maps.get(lg)
                    if me is None and mo is None: continue
                    seen, out = set(), []
                    for i in range(0, len(q), 2):
                        x, y = q[i], q[i + 1]
                        if mo and x < len(mo): x = mo[x]
                        if me and y < len(me): y = me[y]
                        if (x, y) in seen: continue
                        seen.add((x, y)); out += [x, y]
                    if out != q:
                        rec[lg] = out; dirty = True; tot_p += (len(q) - len(out)) // 2
                tot_v += 1
        if dirty and not dry:
            json.dump(al, io.open(ap, 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
    print(f'{"(시험) " if dry else ""}낱말번호를 옮긴 절 {tot_v}곳, 겹쳐서 없앤 짝 {tot_p}개')


if __name__ == '__main__':
    main()
