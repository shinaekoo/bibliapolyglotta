# 개역한글이 직접 인용문을 닫을 때 쓰는 어미(…하고, …하니라, …하며, …하라)에
# 억지로 붙은 낱말 대응을 지운다.
#
# KJV는 인용을 닫는 말을 쓰지 않는다. 그래서 이 어미들에는 대응할 영어 낱말이
# 아예 없는데, 정렬이 남은 영어 기능어(to·that·unto·of…)를 끌어와 붙여 놓았다.
#   창 27:22  "손은 에서의 손이로다 하며"  ← but
#   창 21:7   "내가 아들을 낳았도다 하니라" ← unto
#
# 뜻이 있는 영어 낱말(동사·명사 등)이 하나라도 붙어 있으면 건드리지 않는다.
# "그 눈을 어둡게 하니" 의 하니처럼 어미가 실제로 동사인 자리를 지키기 위해서다.
#
# fix_bridge 다음, fix_links 앞에 돌린다. 손으로 고친 연결이 언제나 이긴다.

import glob, io, json, os, re, unicodedata

DT = os.path.join(os.path.dirname(__file__), '..', 'web', 'data') + os.sep
TX = os.path.join(os.path.dirname(__file__), '..', 'text') + os.sep

# 지울 어미
ENDERS = {'하고', '하니라', '하며', '하라',
          '하시고', '하시니', '하시며', '하시니라'}   # 높임말 형태

# '하니'는 넣지 않는다. 창 19:11 "그 눈을 어둡게 하니"처럼 어미가 실제 동사(smote)인
# 자리가 섞여 있어서, 지우는 것보다 올바른 낱말로 옮기는 쪽이 맞다.

# 뜻이 없는 영어 낱말 — 이것만 붙어 있으면 억지 대응으로 본다
FUNC = {'and', 'to', 'the', 'of', 'a', 'an', 'that', 'for', 'in', 'with', 'as', 'but',
        'or', 'so', 'then', 'unto', 'upon', 'by', 'not', 'all', 'which', 'this',
        'he', 'his', 'him', 'her', 'them', 'their', 'it', 'its', 'on', 'at', 'from'}


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
    gone = 0
    per = {}
    for f in sorted(glob.glob(DT + 'al*.json')):
        bb = re.search(r'al(\d+)\.json', f).group(1)
        kp, ep = f'{TX}ko{bb}.json', f'{TX}en{bb}.json'
        if not (os.path.exists(kp) and os.path.exists(ep)):
            continue
        al = json.load(io.open(f, encoding='utf-8'))
        KO = json.load(io.open(kp, encoding='utf-8'))
        EN = json.load(io.open(ep, encoding='utf-8'))
        hit = False
        for c, chp in enumerate(al['v']):
            for v, rec in enumerate(chp or []):
                if not rec or not rec.get('ko'):
                    continue
                K, E = toks(KO[c][v]), toks(EN[c][v])
                q = rec['ko']
                # 어미 자리마다 붙은 영어 낱말을 모아 본다
                at = {}
                for i in range(0, len(q), 2):
                    if q[i] < len(K) and K[q[i]] in ENDERS and q[i + 1] < len(E):
                        at.setdefault(q[i], []).append(E[q[i + 1]].lower())
                drop = {i for i, ws in at.items() if ws and all(w in FUNC for w in ws)}
                if not drop:
                    continue
                new = []
                for i in range(0, len(q), 2):
                    if q[i] not in drop:
                        new += [q[i], q[i + 1]]
                rec['ko'] = new
                for i in drop:
                    per[K[i]] = per.get(K[i], 0) + 1
                gone += len(drop)
                hit = True
        if hit:
            json.dump(al, io.open(f, 'w', encoding='utf-8'),
                      ensure_ascii=False, separators=(',', ':'))
    print('어미 억지 대응 지움 %d곳 — %s' % (
        gone, ', '.join(f'{w} {n}' for w, n in sorted(per.items(), key=lambda x: -x[1]))))


if __name__ == '__main__':
    main()
