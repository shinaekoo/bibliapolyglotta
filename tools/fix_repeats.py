"""한 절에 같은 영어 낱말이 되풀이될 때 둘째부터 비는 연결을 채운다.

자동 정렬(fast_align)은 같은 낱말이 한 절에 두 번 나오면 번역 쪽 낱말을 첫 자리로
몰아 놓는 성질이 있다. 그래서 시편 1:6 "의인의 **길은** … 악인의 **길은**"에서 앞의
'길은'만 way에 걸리고 뒤의 '길은'은 아무 데도 걸리지 않는다. 읽는 사람에게는 끊어진
것으로 보인다.

겉모습이 똑같은 낱말이 영어 쪽 횟수와 딱 맞아떨어질 때만 순서대로 채운다.
이미 있는 연결은 손대지 않고, 이미 걸린 자리가 순서와 어긋나면(짝이 꼬여 있으면)
그 묶음은 건드리지 않는다. 기능어(the, of, and …)는 뜻을 비추는 의미가 없고 화면만
어지러워지므로 넣지 않는다.

fix_links.py 다음에 돌린다.
"""
import json, os, sys, unicodedata
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
R = os.path.join(HERE, '..')
D = os.path.join(R, 'web', 'data')
TX = os.path.join(R, 'text')

VULG = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,18,19,20,21,22,23,26,27,28,30,31,32,33,34,
        35,36,37,38,39,40,41,42,43,46,47,48,49,50,51,52,53,54,55,56,57,58,59,60,61,62,63,
        64,65,66,67,68,69,70,71,72]
LANGS = ['ko','la','de','fr','zh','ja','es','pt','it','ru','id','tl','ceb','ig']

# 뜻을 비추는 의미가 없는 기능어. 되풀이되는 'the'를 서로 이어 봐야 화면만 어지럽다.
STOP = set("""a an the of and or but if then so as at by for from in into on to unto upon with
within without that this these those there here which who whom whose what when where while
because be is am are was were been being have has had hath having do did doth does done
shall will would should may might can could must let i me my mine we us our ours thou thee
thy thine ye you your yours he him his she her hers it its they them their theirs not no nor
none all any every some such other another same own one also even yet still up out down off
over under again more most much many very o lo now ever never thus therefore how than
against before after between among through about""".split())


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
def main():
    added = defaultdict(int)
    verses = 0
    for b in range(66):
        p = os.path.join(D, f'al{b:02d}.json')
        al = json.load(open(p, encoding='utf-8'))
        en = json.load(open(os.path.join(TX, f'en{b:02d}.json'), encoding='utf-8'))
        txt = {}
        for L in LANGS:
            n = VULG[b] if L == 'la' else b
            f = os.path.join(TX, f'{L}{n:02d}.json')
            if os.path.exists(f):
                txt[L] = json.load(open(f, encoding='utf-8'))
        touched = False
        for ci, chv in enumerate(al['v']):
            for vi, rec in enumerate(chv):
                if ci >= len(en) or vi >= len(en[ci]):
                    continue
                et = toks(en[ci][vi])
                grp = defaultdict(list)
                for i, w in enumerate(et):
                    grp[w.lower()].append(i)
                rep = {w: ix for w, ix in grp.items()
                       if len(ix) > 1 and w not in STOP and len(w) >= 3}
                if not rep:
                    continue
                hit = False
                for L, book in txt.items():
                    if ci >= len(book) or vi >= len(book[ci]):
                        continue
                    pr = rec.get(L)
                    if not pr:
                        continue
                    lt = toks(book[ci][vi])
                    by = defaultdict(list)
                    for j in range(0, len(pr) - 1, 2):
                        by[pr[j + 1]].append(pr[j])
                    for w, ix in rep.items():
                        empty = [e for e in ix if not by.get(e)]
                        filled = [e for e in ix if by.get(e)]
                        if not filled or not empty:
                            continue
                        # 걸려 있는 낱말들의 겉모습이 하나로 모여야 한다
                        surf = {lt[k] for e in filled for k in by[e] if k < len(lt)}
                        if len(surf) != 1:
                            continue
                        F = next(iter(surf))
                        cand = [i for i, x in enumerate(lt) if x == F]
                        if len(cand) != len(ix):
                            continue
                        # 이미 걸린 자리가 순서와 어긋나면(짝이 꼬였으면) 건드리지 않는다
                        if any(cand[i] not in by[e] for i, e in enumerate(ix) if by.get(e)):
                            continue
                        for i, e in enumerate(ix):
                            if by.get(e):
                                continue
                            rec[L].extend([cand[i], e])
                            by[e].append(cand[i])
                            added[L] += 1
                            hit = True
                if hit:
                    verses += 1
                    touched = True
        if touched:
            json.dump(al, open(p, 'w', encoding='utf-8'),
                      ensure_ascii=False, separators=(',', ':'))
    tot = sum(added.values())
    print(f'되풀이되는 낱말에 채운 연결 {tot:,}개 · 절 {verses:,}개')
    for L in LANGS:
        if added[L]:
            print(f'  {L:<4} {added[L]:>6,}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
