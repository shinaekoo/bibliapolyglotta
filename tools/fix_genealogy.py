#!/usr/bin/env python3
"""족보의 되풀이되는 틀을 보고 낱말을 잇는다.

족보는 한 절 안에서 같은 틀이 서너 번씩 되풀이된다. 통계로 만든 연결은
되풀이되는 자리를 첫 번째 것에 몰아 버려서, 누가복음 3장은 성경에서
연결이 가장 적은 장이 되었다(59.3%).

틀이 규칙적이라 자리로 맞출 수 있다.

  눅 3:24  which was the son of Matthat | which was the son of Levi | …
           그    이상은                맛닷이요 | 그 이상은 레위요 | …

  마 1:2   Abraham begat Isaac | and Isaac begat Jacob | …
           아브라함이 이삭을 낳고 | 이삭은 야곱을 낳고 | …

  대상 1:5 The sons of Japheth | Gomer and Magog and Madai …
           야벳의 아들은        | 고멜과 마곡과 마대와 …

어느 틀이든 '영어 토막 수 == 한국어 토막 수'일 때만 손댄다. 하나라도
어긋나면 그 절은 건드리지 않는다. 연결을 더하기만 하고 지우지 않는다.

usage: python3 tools/fix_genealogy.py [--dry]
"""
import json, io, os, re, sys, unicodedata

HERE = os.path.dirname(os.path.abspath(__file__))
D = os.path.join(HERE, '..', 'web', 'data') + '/'
TX = os.path.join(HERE, '..', 'text') + '/'
DRY = '--dry' in sys.argv


def toks(s):
    r"""앱(web/index.html의 WORD)과 똑같이 낱말을 가른다.

    글자·결합기호가 이어진 덩어리를 한 낱말로 보되, 글자 사이에 낀 엔대시(–)는
    낱말 속 글자로 친다. KJV가 고유명사를 엔대시로 잇고(Beth–el, Beer–sheba),
    러시아어도 что–нибудь처럼 쓰기 때문이다. 파이썬 re에는 \p{}가 없고
    [^\W\d_]는 결합 기호를 빼므로, 그걸 쓰면 니쿠드가 찍힌 히브리어가
    글자 하나하나로 쪼개져 자리가 어긋난다."""
    out, cur = [], []
    s = s or ''
    for i, ch in enumerate(s):
        if unicodedata.category(ch)[0] in ('L', 'M'):
            cur.append(ch)
        elif (ch == '\u2013' and cur and i + 1 < len(s)
              and unicodedata.category(s[i + 1])[0] in ('L', 'M')):
            cur.append(ch)        # 낱말 속 엔대시 — Beth–el, Abed–nego, что–нибудь
        elif cur:
            out.append(''.join(cur)); cur = []
    if cur: out.append(''.join(cur))
    return out
def chunks(words, is_head):
    """머리 낱말이 나올 때마다 끊는다. 머리 앞의 것은 버리지 않고 첫 토막에 붙인다."""
    out, cur = [], []
    for i, w in enumerate(words):
        if is_head(w, i) and cur:
            out.append(cur); cur = []
        cur.append(i)
    if cur:
        out.append(cur)
    return out


# ---- 틀 1. '…의 아들/이상은' (누가복음 3장) ----
def luke_son(E, K):
    """which was the son of NAME  ↔  그 이상은 NAME이요"""
    if not any(w.lower() == 'son' for w in E):
        return None
    ec = chunks(E, lambda w, i: w.lower() == 'which')
    kc = chunks(K, lambda w, i: w == '그')
    # 첫 토막에 머리말이 섞여 있으면(3:23) 그 토막은 건너뛰고 뒤만 맞춘다
    n = min(len(ec), len(kc))
    if n < 2 or abs(len(ec) - len(kc)) > 1:
        return None
    ec, kc = ec[len(ec) - n:], kc[len(kc) - n:]
    pairs = []
    for eidx, kidx in zip(ec, kc):
        ew = [E[i].lower() for i in eidx]
        kw = [K[i] for i in kidx]
        if 'son' not in ew or len(kidx) < 2:
            return None
        if kw[0] != '그' or not kw[1].startswith('이상'):
            return None
        name_e = [i for i in eidx if E[i].lower() not in
                  ('which', 'was', 'the', 'son', 'of', 'and')]
        name_k = kidx[2:]
        if len(name_e) != 1 or len(name_k) != 1:
            return None
        for i in eidx:
            w = E[i].lower()
            if w == 'which':
                pairs.append((kidx[0], i))
            elif w in ('was', 'the', 'son', 'of'):
                pairs.append((kidx[1], i))
        pairs.append((name_k[0], name_e[0]))
    return pairs


# ---- 틀 2. 'A begat B' (마태복음 1장) ----
def begat(E, K):
    """A begat B  ↔  A가 B를 낳고

    영어는 'A begat B' 차례지만 한국어는 'A가 B를 낳고' 라서, 한 토막의
    주어는 '낳고' 앞 영어 이름이고 목적어는 '낳고' 뒤 영어 이름이다.
    'of'가 끼면 차례가 뒤바뀌므로(마 1:3 '베레스와 세라를 다말에게서')
    그 토막은 손대지 않는다.
    """
    el = [w.lower() for w in E]
    eb = [i for i, w in enumerate(el) if w.startswith('begat')]
    kb = [i for i, w in enumerate(K) if w.startswith('낳')]
    if not eb or len(eb) != len(kb):
        return None
    pairs = []
    ep = kp = 0                       # 앞 토막이 끝난 자리
    for n, (e, k) in enumerate(zip(eb, kb)):
        nxt = eb[n + 1] if n + 1 < len(eb) else len(E)
        before = [i for i in range(ep, e) if el[i] not in ('and', 'the')]
        after = [i for i in range(e + 1, nxt) if el[i] not in ('and', 'the')]
        kw = list(range(kp, k))
        ep, kp = e + 1, k + 1
        if not before or not kw:
            continue
        if any(el[i] == 'of' for i in after):     # 차례가 뒤바뀐 토막
            continue
        subj, obj = before[-1:], after
        if n + 1 < len(eb):                       # 가운데 토막은 목적어가 다음 'begat' 앞까지
            obj = [i for i in after if i < nxt]
            obj = obj[:-1] if obj and obj[-1] == nxt - 1 and len(obj) > 1 else obj
        if len(subj) + len(obj) != len(kw):
            continue
        pairs.append((k, e))                      # 낳고 ↔ begat
        for ki, ei in zip(kw, subj + obj):
            pairs.append((ki, ei))
    return pairs or None


# ---- 틀 3. '…의 아들은 A와 B와 C라' (역대상 등) ----
def sons_of(E, K):
    el = [w.lower() for w in E]
    if 'sons' not in el or len(K) < 3:
        return None
    s = el.index('sons')
    if s + 1 >= len(el) or el[s + 1] != 'of':
        return None
    # 영어: 'sons of' 뒤의 머리 이름 하나, 그 뒤가 자식들
    head_e = s + 2
    kids_e = [i for i in range(head_e + 1, len(E))
              if E[i][:1].isupper() and el[i] != 'and']
    # 한국어: '…의 아들은' 다음이 자식들
    ki = next((i for i, w in enumerate(K) if w.startswith('아들')), None)
    if ki is None or ki + 1 >= len(K):
        return None
    kids_k = list(range(ki + 1, len(K)))
    if not kids_e or len(kids_e) != len(kids_k):
        return None
    pairs = [(ki - 1, head_e), (ki, s), (ki, s + 1)] if ki else []
    pairs += list(zip(kids_k, kids_e))
    return pairs


RULES = [('아들 족보', luke_son), ('낳고 족보', begat), ('아들은 족보', sons_of)]


def main():
    tot = {n: 0 for n, _ in RULES}
    verses = {n: 0 for n, _ in RULES}
    for b in range(66):
        p = D + f'al{b:02d}.json'
        al = json.load(io.open(p, encoding='utf-8'))
        EN = json.load(io.open(TX + f'en{b:02d}.json', encoding='utf-8'))
        KO = json.load(io.open(TX + f'ko{b:02d}.json', encoding='utf-8'))
        dirty = False
        for c in range(len(al['v'])):
            for v, rec in enumerate(al['v'][c]):
                if not rec or c >= len(EN) or v >= len(EN[c]):
                    continue
                E, K = toks(EN[c][v]), toks(KO[c][v])
                if not E or not K:
                    continue
                for name, fn in RULES:
                    try:
                        got = fn(E, K)
                    except Exception:
                        got = None
                    if not got:
                        continue
                    pr = rec.get('ko') or []
                    have = {(pr[i], pr[i + 1]) for i in range(0, len(pr), 2)}
                    new = [x for x in got
                           if x not in have and x[0] < len(K) and x[1] < len(E)]
                    if new:
                        rec['ko'] = pr + [x for pair in new for x in pair]
                        tot[name] += len(new)
                        verses[name] += 1
                        dirty = True
                    break
        if dirty and not DRY:
            json.dump(al, io.open(p, 'w', encoding='utf-8'),
                      ensure_ascii=False, separators=(',', ':'))
    for name, _ in RULES:
        print(f'  {name}: {tot[name]:,}곳 · {verses[name]:,}절')
    print(f'족보에서 이은 연결 {sum(tot.values()):,}곳'
          + (' (적어 보기만 함)' if DRY else ''))


if __name__ == '__main__':
    main()
