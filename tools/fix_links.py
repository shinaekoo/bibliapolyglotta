"""손으로 고친 낱말 연결.  usage: python3 tools/fix_links.py

tools/align_original.py로 정렬을 다시 만든 뒤 fix_jehovah.py·fix_names.py와 나란히 실행한다.
자동 정렬이 놓친 자리를 한 줄씩 적어 둔다.

자리를 번호가 아니라 낱말로 적는다. 본문이 한 번이라도 바뀌면 -- tools/verse_map.py가 라틴어·독일어
절을 옮긴 것처럼 -- 번호는 조용히 어긋나지만, 낱말은 못 찾으면 소리를 낸다. 한 항목은 "이 영어
낱말은 그 번역의 이 낱말들에 걸린다"는 뜻이고, 그 영어 낱말에 걸려 있던 기존 연결은 지우고 여기
적은 것만 남긴다. 같은 낱말이 그 절에 두 번 나오면 '그가#2'처럼 몇 번째인지 적는다.
"""
import json, os, sys, unicodedata

HERE = os.path.dirname(os.path.abspath(__file__))
D = os.path.join(HERE, '..', 'web', 'data') + '/'
TX = os.path.join(HERE, '..', 'text') + '/'
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
# 라틴어 본문 파일은 불가타 책 번호를 쓴다 (tools/verse_map.py와 같은 표)
VULG = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 18, 19, 20, 21, 22, 23, 26, 27, 28, 30, 31,
        32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57,
        58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72]

FIX = [
    # 창세기 5:24 — '동행하더니'에 연결이 없었다. walked with 두 낱말이 이 한 낱말에 들어 있다.
    dict(ref=(0, 5, 24), lang='ko', en='walked', words=['동행하더니']),
    dict(ref=(0, 5, 24), lang='ko', en='with', words=['동행하더니']),
    # 히브리서 11:5 — pleased에 한국어가 비어 있었다. '하는'은 이 절에 두 번 나오므로 앞의 것.
    dict(ref=(57, 11, 5), lang='ko', en='pleased', words=['기쁘시게', '하는#1']),
    # 같은 절: this가 '하는'에 걸려 있었다. 'this testimony'는 '증거를'에 함께 간다.
    dict(ref=(57, 11, 5), lang='ko', en='this', words=['증거를']),
    # 'was not found'는 '다시 보이지 아니하니라'. found가 앞 절의 '보지'(죽음을 보지 않고)에,
    # 뒤의 not이 같은 앞 절 '않고'에 걸려 있었다.
    dict(ref=(57, 11, 5), lang='ko', en='found', words=['보이지']),
    dict(ref=(57, 11, 5), lang='ko', en='not#2', words=['아니하니라']),
    # '자라'는 앞 절의 that('that he should not see death')에 걸려 있었다. 맞는 자리가 없어 뗀다.
    dict(ref=(57, 11, 5), lang='ko', en='that#1', words=[]),
    # 히브리서 11:6 — rewarder는 '상 주시는 이'인데 '이심을' 하나에만 걸려 있었다.
    # '이'는 '이심을' 안에 붙어 있어 따로 떼어낼 수 없으므로 세 낱말을 함께 건다.
    dict(ref=(57, 11, 6), lang='ko', en='rewarder', words=['상', '주시는', '이심을']),
    # 같은 절 라틴어: rewarder에 remunerator와 함께 inquirentibus가 걸려 있었다.
    dict(ref=(57, 11, 6), lang='la', en='rewarder', words=['remunerator']),
    # inquirentibus는 '찾는 자들'. 명사처럼 쓰인 분사라 영어로는 them that seek 전체를 받으므로
    # 두 낱말에 걸고, 한국어 '자들에게'도 them에 이어 '찾는 자들에게'가 함께 켜지게 한다.
    dict(ref=(57, 11, 6), lang='la', en='seek', words=['inquirentibus']),
    dict(ref=(57, 11, 6), lang='la', en='them', words=['inquirentibus']),
    dict(ref=(57, 11, 6), lang='ko', en='seek', words=['찾는']),
    dict(ref=(57, 11, 6), lang='ko', en='them', words=['자들에게']),
    # 헬라어도 같다: 관사 τοῖς가 'them that', 분사 ἐκζητοῦσιν이 'seek'를 받는다.
    dict(ref=(57, 11, 6), lang='or', en='them', words=['τοῖς']),
    dict(ref=(57, 11, 6), lang='or', en='seek', words=['ἐκζητοῦσιν']),
    # 같은 절에서 rewarder 연결이 비어 있던 나머지 언어들
    dict(ref=(57, 11, 6), lang='de', en='rewarder', words=['Vergelter']),
    dict(ref=(57, 11, 6), lang='zh', en='rewarder', words=['賞賜']),
    dict(ref=(57, 11, 6), lang='ru', en='rewarder', words=['воздает']),
    dict(ref=(57, 11, 6), lang='ja', en='rewarder', words=['報いて下さることとを']),
    dict(ref=(57, 11, 6), lang='id', en='rewarder', words=['memberi', 'pahala']),
    # 창세기 5·11장에 되풀이되는 '자녀를 낳았으며' — 한국어가 daughters에만 걸리고 sons가 빠져
    # 있었다. '자녀'는 한 낱말이라 자/녀로 가를 수 없으므로 두 영어 낱말을 이 한 낱말에 건다
    # (라틴어 filios·filias는 이미 맞게 걸려 있다).
    dict(ref=(0, 5, [4, 7, 10, 13, 16, 19, 22, 26, 30]), lang='ko', en='sons', words=['자녀를']),
    dict(ref=(0, 5, [4, 7, 10, 13, 16, 19, 22, 26, 30]), lang='ko', en='daughters', words=['자녀를']),
    dict(ref=(0, 11, [11, 13, 15, 17, 19, 21, 23, 25]), lang='ko', en='sons', words=['자녀를']),
    dict(ref=(0, 11, [11, 13, 15, 17, 19, 21, 23, 25]), lang='ko', en='daughters', words=['자녀를']),
    # 히브리서 12:2 — '믿음의 주요 또 온전케 하시는 이인'. author와 finisher가 뒤바뀌어 있었다.
    # 라틴어도 마찬가지로 auctorem('주')과 consummatorem('온전케 하시는 이')이 서로 바뀌었다.
    dict(ref=(57, 12, 2), lang='ko', en='author', words=['주요']),
    dict(ref=(57, 12, 2), lang='ko', en='finisher', words=['온전케', '하시는', '이인']),
    dict(ref=(57, 12, 2), lang='la', en='author', words=['auctorem']),
    dict(ref=(57, 12, 2), lang='la', en='finisher', words=['consummatorem']),
    # 헬라어도 같이 바뀌어 있었다: ἀρχηγός가 '주', τελειωτής가 '온전케 하시는 이'.
    dict(ref=(57, 12, 2), lang='or', en='author', words=['ἀρχηγὸν']),
    dict(ref=(57, 12, 2), lang='or', en='finisher', words=['τελειωτὴν']),
    # 같은 절 뒷부분: 'is set down'이 '앉으셨느니라'·sedet인데, 한국어는 앞 절의 '있는'에,
    # 라틴어 sedet은 throne에 걸려 있었다 (throne은 sedis).
    dict(ref=(57, 12, 2), lang='ko', en='is', words=['앉으셨느니라']),
    dict(ref=(57, 12, 2), lang='ko', en='set#2', words=['앉으셨느니라']),
    dict(ref=(57, 12, 2), lang='ko', en='down', words=['앉으셨느니라']),
    dict(ref=(57, 12, 2), lang='la', en='throne', words=['sedis']),
    dict(ref=(57, 12, 2), lang='la', en='set#2', words=['sedet']),
    dict(ref=(57, 12, 2), lang='la', en='down', words=['sedet']),
    # 히브리서 1:2 — made에 한국어가 비어 있었다. 짓다는 ㅅ-불규칙이라 어간이 '짓'·'지으'·'지'로
    # 쪼개지는데 '지' 뭉치에는 '지면에'처럼 남의 말이 섞여 있어, 어미를 떼는 것만으로는 묶이지 않는다.
    dict(ref=(57, 1, 2), lang='ko', en='made', words=['지으셨느니라']),
    # 같은 절: heir도 비어 있었다 ('만유의 후사로 세우시고').
    dict(ref=(57, 1, 2), lang='ko', en='heir', words=['후사로']),
    # 히브리서 1:3 — '하나님의 영광의 광채시요 그 본체의 형상이시라'.
    # brightness가 비어 있고 '광채시요'가 express에 걸려 있었다. express·image는 둘 다 '형상이시라'다
    # ('the express image of his person' = 형상 하나를 가리키는 두 낱말).
    dict(ref=(57, 1, 3), lang='ko', en='brightness', words=['광채시요']),
    dict(ref=(57, 1, 3), lang='ko', en='express', words=['형상이시라']),
    dict(ref=(57, 1, 3), lang='ko', en='image', words=['형상이시라']),

    # ---- '아무 사람'(족속 이름)이 사람 이름 쪽으로 붙어 버린 자리 ----
    # 히브리어는 지역·조상 이름에 -이(-i)를 붙여 '그곳 사람'을 만든다 (길르앗 → 길르앗 사람).
    # 영어는 Gilead / Gileadite로 갈라 적지만 한국어는 '길르앗 사람'이라 두 쪽 다 '길르앗'으로
    # 보인다. 한 절에 둘이 같이 나오면 자동 정렬이 둘을 맞바꿔 걸어, 지역이어야 할 '길르앗'이
    # 인물 길르앗으로 표시됐다. 용사 명단(삼하 23장·대상 11장)에 같은 일이 몰려 있다.
    # 사사기 11:1 — 앞의 '길르앗 사람'은 지역, 뒤의 '길르앗에게'는 입다의 아버지다.
    dict(ref=(6, 11, 1), lang='ko', en='Gileadite', words=['길르앗', '사람']),
    dict(ref=(6, 11, 1), lang='ko', en='Gilead', words=['길르앗에게']),
    # 사사기 12:12 — 앞은 '스불론 사람'(족속), 뒤는 '스불론 땅'(지역)
    dict(ref=(6, 12, 12), lang='ko', en='Zebulonite', words=['스불론#1', '사람']),
    dict(ref=(6, 12, 12), lang='ko', en='Zebulun', words=['스불론#2']),
    # 사무엘하 23:31
    dict(ref=(9, 23, 31), lang='ko', en='Arbathite', words=['아르바', '사람#1']),
    dict(ref=(9, 23, 31), lang='ko', en='Abi–albon', words=['아비알본과']),
    dict(ref=(9, 23, 31), lang='ko', en='Barhumite', words=['바르훔', '사람#2']),
    dict(ref=(9, 23, 31), lang='ko', en='Azmaveth', words=['아스마웻과']),
    # 사무엘하 23:33 — '하랄 사람'이 두 번 나온다
    dict(ref=(9, 23, 33), lang='ko', en='Hararite#1', words=['하랄', '사람#1']),
    dict(ref=(9, 23, 33), lang='ko', en='Hararite#2', words=['아랄', '사람#2']),
    dict(ref=(9, 23, 33), lang='ko', en='Sharar', words=['사랄의']),
    # 사무엘하 23:35
    dict(ref=(9, 23, 35), lang='ko', en='Carmelite', words=['갈멜', '사람#1']),
    dict(ref=(9, 23, 35), lang='ko', en='Hezrai', words=['헤스래와']),
    dict(ref=(9, 23, 35), lang='ko', en='Arbite', words=['아랍', '사람#2']),
    dict(ref=(9, 23, 35), lang='ko', en='Paarai', words=['바아래와']),
    # 역대상 11:27
    dict(ref=(12, 11, 27), lang='ko', en='Harorite', words=['하롤', '사람#1']),
    dict(ref=(12, 11, 27), lang='ko', en='Shammoth', words=['삼훗과']),
    dict(ref=(12, 11, 27), lang='ko', en='Pelonite', words=['블론', '사람#2']),
    # 역대상 11:29
    dict(ref=(12, 11, 29), lang='ko', en='Hushathite', words=['후삿', '사람#1']),
    dict(ref=(12, 11, 29), lang='ko', en='Ilai', words=['일래와']),
    dict(ref=(12, 11, 29), lang='ko', en='Ahohite', words=['아호아', '사람#2']),

    # 사사기 11:2 — 불가타는 "상속자가 될 수 없다"(Hæres esse non poteris)로 적는다.
    # 명사 하나가 영어 동사 inherit을 받는데 연결이 비어 있었고, 한국어도 '기업을'만
    # 걸려 '잇지'가 비어 있었다. '기업을'에 엉뚱하게 붙어 있던 Thou는 '너는'으로 옮긴다.
    dict(ref=(6, 11, 2), lang='la', en='inherit', words=['Hæres']),
    dict(ref=(6, 11, 2), lang='ko', en='inherit', words=['기업을', '잇지']),
    dict(ref=(6, 11, 2), lang='ko', en='Thou', words=['너는']),

    # ---- 불가타의 hæres/hæreditas 계열에 연결이 비어 있던 자리 ----
    # 영어가 inherit·inheritance·heir로 적은 자리인데 라틴어 쪽이 비어 있었다.
    dict(ref=(2, 25, 46), lang='la', en='inheritance', words=['hæreditario']),
    dict(ref=(2, 25, 46), lang='la', en='inherit', words=['possidebitis']),
    dict(ref=(4, 4, 20), lang='la', en='inheritance', words=['hæreditarium']),
    dict(ref=(14, 9, 12), lang='la', en='inheritance', words=['hæredes']),
    # 시편 16:5 — 뒤의 hæreditatem meam 은 영어 'my lot'에 해당한다
    dict(ref=(18, 16, 5), lang='la', en='lot', words=['hæreditatem']),
    dict(ref=(19, 13, 22), lang='la', en='inheritance', words=['hæredes']),
    dict(ref=(22, 57, 13), lang='la', en='inherit', words=['hæreditabit']),
    dict(ref=(23, 8, 10), lang='la', en='inherit', words=['hæredibus']),
    # 에스겔 46:16 — inheritance가 두 번 나온다. 앞은 hæreditas, 뒤는 hæreditarie.
    dict(ref=(25, 46, 16), lang='la', en='inheritance#2', words=['hæreditarie']),
    # 히브리서 1:4 — 라틴어 동사 하나가 'by inheritance obtained' 두 쪽을 받는다
    dict(ref=(57, 1, 4), lang='la', en='inheritance', words=['hæreditavit']),
    dict(ref=(57, 1, 4), lang='la', en='obtained', words=['hæreditavit']),
    dict(ref=(57, 1, 14), lang='la', en='heirs', words=['hæreditatem']),

    # ---- 한국어 '기업'이 영어 inheritance 여러 자리 가운데 첫째에만 몰려 있던 자리 ----
    # 한 절에 inheritance가 두 번 이상 나오면 한국어 '기업'이 모두 첫째에만 걸려 있었다.
    # 수가 같은 절은 나오는 순서대로 짝지었다.
    dict(ref=(0, 21, 10), lang='ko', en='heir', words=['얻지', '기업을']),
    dict(ref=(3, 18, 20), lang='ko', en='inheritance#1', words=['기업도']),
    dict(ref=(3, 18, 20), lang='ko', en='inheritance#2', words=['기업이니라']),
    dict(ref=(3, 26, 54), lang='ko', en='inheritance#1', words=['기업을#1']),
    dict(ref=(3, 26, 54), lang='ko', en='inheritance#2', words=['기업을#2']),
    dict(ref=(3, 26, 54), lang='ko', en='inheritance#3', words=['기업을#3']),
    dict(ref=(3, 27, 7), lang='ko', en='inheritance#1', words=['기업을']),
    dict(ref=(3, 27, 7), lang='ko', en='inheritance#2', words=['기업으로']),
    dict(ref=(3, 34, 14), lang='ko', en='inheritance#1', words=['기업을#1']),
    dict(ref=(3, 34, 14), lang='ko', en='inheritance#2', words=['기업을#2']),
    dict(ref=(3, 36, 2), lang='ko', en='inheritance#1', words=['기업의']),
    dict(ref=(3, 36, 2), lang='ko', en='inheritance#2', words=['기업으로']),
    dict(ref=(3, 36, 3), lang='ko', en='inheritance#1', words=['기업은']),
    dict(ref=(3, 36, 3), lang='ko', en='inheritance#2', words=['기업에서#1']),
    dict(ref=(3, 36, 3), lang='ko', en='inheritance#3', words=['기업에']),
    dict(ref=(3, 36, 3), lang='ko', en='inheritance#4', words=['기업에서#2']),
    dict(ref=(3, 36, 7), lang='ko', en='inheritance#1', words=['기업이']),
    dict(ref=(3, 36, 7), lang='ko', en='inheritance#2', words=['기업을']),
    dict(ref=(3, 36, 8), lang='ko', en='inheritance#1', words=['기업을#1']),
    dict(ref=(3, 36, 8), lang='ko', en='inheritance#2', words=['기업을#2']),
    dict(ref=(3, 36, 9), lang='ko', en='inheritance#1', words=['기업으로']),
    dict(ref=(3, 36, 9), lang='ko', en='inheritance#2', words=['기업을']),
    dict(ref=(4, 9, 29), lang='ko', en='inheritance', words=['기업이로소이다']),
    dict(ref=(4, 10, 9), lang='ko', en='inheritance#1', words=['기업이']),
    dict(ref=(4, 10, 9), lang='ko', en='inheritance#2', words=['기업이시니라']),
    dict(ref=(4, 18, 1), lang='ko', en='inheritance#1', words=['기업도']),
    dict(ref=(4, 18, 1), lang='ko', en='inheritance#2', words=['기업을']),
    dict(ref=(4, 18, 2), lang='ko', en='inheritance#1', words=['기업이#1']),
    dict(ref=(4, 18, 2), lang='ko', en='inheritance#2', words=['기업이#2']),
    dict(ref=(5, 13, 14), lang='ko', en='inheritance#1', words=['기업으로']),
    dict(ref=(5, 13, 14), lang='ko', en='inheritance#2', words=['기업이']),
    dict(ref=(5, 13, 33), lang='ko', en='inheritance#1', words=['기업을']),
    dict(ref=(5, 13, 33), lang='ko', en='inheritance#2', words=['기업이']),
    dict(ref=(5, 14, 3), lang='ko', en='inheritance#1', words=['기업은']),
    dict(ref=(5, 14, 3), lang='ko', en='inheritance#2', words=['기업을']),
    dict(ref=(5, 17, 4), lang='ko', en='inheritance#1', words=['기업을#1']),
    dict(ref=(5, 17, 4), lang='ko', en='inheritance#2', words=['기업을#2']),
    dict(ref=(5, 18, 7), lang='ko', en='inheritance#1', words=['기업이']),
    dict(ref=(5, 18, 7), lang='ko', en='inheritance#2', words=['기업을']),
    dict(ref=(5, 19, 1), lang='ko', en='inheritance#1', words=['기업은']),
    dict(ref=(5, 19, 1), lang='ko', en='inheritance#2', words=['기업']),
    dict(ref=(5, 19, 49), lang='ko', en='inheritance#1', words=['기업의']),
    dict(ref=(5, 19, 49), lang='ko', en='inheritance#2', words=['기업을']),
    dict(ref=(6, 18, 1), lang='ko', en='inheritance#1', words=['기업의#1']),
    dict(ref=(6, 18, 1), lang='ko', en='inheritance#2', words=['기업의#2']),
    dict(ref=(18, 135, 12), lang='ko', en='heritage#1', words=['기업으로#1']),
    dict(ref=(18, 135, 12), lang='ko', en='heritage#2', words=['기업으로#2']),
    dict(ref=(19, 19, 14), lang='ko', en='inheritance', words=['상속하거니와']),
    dict(ref=(25, 33, 24), lang='ko', en='inherited', words=['얻었나니', '기업으로#1']),
    dict(ref=(25, 33, 24), lang='ko', en='inheritance', words=['기업으로#2']),
    dict(ref=(25, 44, 28), lang='ko', en='inheritance#1', words=['기업이']),
    dict(ref=(25, 44, 28), lang='ko', en='inheritance#2', words=['기업이라']),
    dict(ref=(25, 46, 16), lang='ko', en='inheritance#1', words=['기업이']),
    dict(ref=(25, 46, 16), lang='ko', en='inheritance#2', words=['기업을']),
    dict(ref=(25, 46, 17), lang='ko', en='inheritance#1', words=['기업으로']),
    dict(ref=(25, 46, 17), lang='ko', en='inheritance#2', words=['기업은']),
    dict(ref=(25, 46, 18), lang='ko', en='inheritance#1', words=['기업을']),
    dict(ref=(25, 46, 18), lang='ko', en='inheritance#2', words=['기업으로']),
    dict(ref=(25, 47, 14), lang='ko', en='inherit', words=['기업을']),
    dict(ref=(25, 47, 14), lang='ko', en='inheritance', words=['기업이']),
    dict(ref=(25, 47, 22), lang='ko', en='inheritance#1', words=['기업이']),
    dict(ref=(25, 47, 22), lang='ko', en='inheritance#2', words=['기업을']),
    dict(ref=(57, 6, 17), lang='ko', en='heirs', words=['기업으로']),

    # ---- 영어·한국어 어순이 어긋나 순서로 짝지을 수 없던 절 ----
    # 민수기 33:54 — 영어는 inheritance가 네 번, 한국어는 '기업을'이 세 번이다.
    dict(ref=(3, 33, 54), lang='ko', en='inheritance#1', words=[]),
    dict(ref=(3, 33, 54), lang='ko', en='inheritance#2', words=['기업을#1']),
    dict(ref=(3, 33, 54), lang='ko', en='inheritance#3', words=['기업을#2']),
    dict(ref=(3, 33, 54), lang='ko', en='inherit', words=['얻을', '기업을#3']),
    # 민수기 36:4 — 둘째 inheritance는 한국어가 '지파에'로 삼켰다
    dict(ref=(3, 36, 4), lang='ko', en='inheritance#1', words=['기업이']),
    dict(ref=(3, 36, 4), lang='ko', en='inheritance#3', words=['기업은']),
    dict(ref=(3, 36, 4), lang='ko', en='inheritance#4', words=['기업에서']),
    # 여호수아 19:9 — 첫 '기업'은 영어 portion 쪽이다
    dict(ref=(5, 19, 9), lang='ko', en='portion', words=['기업#1']),
    dict(ref=(5, 19, 9), lang='ko', en='inheritance#2', words=['기업을']),
    dict(ref=(5, 19, 9), lang='ko', en='inheritance#3', words=['기업#2']),
    # 룻기 4:6 — 앞의 '기업 무를 자'는 사람(kinsman)이고, 상속 재산은 '기업에'다
    dict(ref=(7, 4, 6), lang='ko', en='kinsman', words=['기업', '무를#1', '자가']),
    dict(ref=(7, 4, 6), lang='ko', en='inheritance', words=['기업에']),
    dict(ref=(7, 4, 6), lang='ko', en='own', words=['기업에']),
    # 시편 106:5 — 'thine inheritance'는 뒤의 '주의 기업과'다
    dict(ref=(18, 106, 5), lang='ko', en='inheritance', words=['기업과']),
    # 예레미야 32:8 — 'the right of inheritance'가 '기업의 상속권이' 두 낱말이다
    dict(ref=(23, 32, 8), lang='ko', en='inheritance', words=['기업의', '상속권이']),
    dict(ref=(23, 32, 8), lang='ko', en='right', words=['상속권이']),

    # ---- 짝이 드물어 자동 정렬이 포기한 자리 ----
    # 시편 2:1 — KJV의 'rage'는 성경 전체에 18번뿐이고 그때마다 한국어가 다른 꼴
    # (분한·분노를·분노와·진노로·분노하여)이라, 되풀이되는 짝이 없어 통계가 서지 않는다.
    dict(ref=(18, 2, 1), lang='ko', en='rage', words=['분노하며']),
    dict(ref=(18, 2, 1), lang='ko', en='imagine', words=['경영하는고']),
    dict(ref=(18, 2, 1), lang='ko', en='thing', words=['허사를']),
    # 시편 2:2 — 'kings'는 334번 나오지만 거의 다 '왕/왕들…'이고 '군왕'은 성경 전체에
    # 여섯 번뿐이라, 흔한 번역어에 밀려 한 번도 걸리지 못했다.
    dict(ref=(18, 2, 2), lang='ko', en='kings', words=['군왕들이']),
    dict(ref=(18, 2, 2), lang='ko', en='set', words=['나서며']),
    dict(ref=(18, 2, 2), lang='ko', en='themselves', words=['나서며']),
    dict(ref=(18, 2, 2), lang='ko', en='take', words=['꾀하여']),
    dict(ref=(18, 2, 2), lang='ko', en='counsel', words=['꾀하여']),
    dict(ref=(18, 2, 2), lang='ko', en='together', words=['서로']),
    dict(ref=(18, 2, 2), lang='ko', en='anointed', words=['기름', '받은', '자를']),

    # ---- 시편 4-5편. 한국어가 영어 여러 낱말을 한 낱말로 받는 자리들이다 ----
    # 시편 4:4 — 'Stand in awe'(히브리어 רִגְזוּ, 떨라)는 '떨며' 하나가 받는다.
    # '잠잠할지어다'는 'be still' 쪽이고, '말하고'는 commune 이다.
    dict(ref=(18, 4, 4), lang='ko', en='Stand', words=['떨며']),
    dict(ref=(18, 4, 4), lang='ko', en='in', words=['떨며']),
    dict(ref=(18, 4, 4), lang='ko', en='awe', words=['떨며']),
    dict(ref=(18, 4, 4), lang='ko', en='commune', words=['말하고']),
    dict(ref=(18, 4, 4), lang='ko', en='upon', words=['자리에']),
    dict(ref=(18, 4, 4), lang='ko', en='bed', words=['자리에', '누워']),
    dict(ref=(18, 4, 4), lang='ko', en='be', words=['잠잠할지어다']),
    dict(ref=(18, 4, 4), lang='ko', en='still', words=['잠잠할지어다']),
    # 시편 4:5 — 'put your trust in'이 '의뢰할지어다' 하나다
    dict(ref=(18, 4, 5), lang='ko', en='put', words=['의뢰할지어다']),
    dict(ref=(18, 4, 5), lang='ko', en='trust', words=['의뢰할지어다']),
    dict(ref=(18, 4, 5), lang='ko', en='in', words=['의뢰할지어다']),
    dict(ref=(18, 4, 5), lang='ko', en='your', words=[]),
    dict(ref=(18, 4, 5), lang='ko', en='Lord', words=['여호와를']),
    # 시편 4:8
    dict(ref=(18, 4, 8), lang='ko', en='sleep', words=['자기도']),
    dict(ref=(18, 4, 8), lang='ko', en='will', words=['하리니']),
    dict(ref=(18, 4, 8), lang='ko', en='makest', words=['거하게', '하시는']),
    # 시편 5:1
    dict(ref=(18, 5, 1), lang='ko', en='consider', words=['통촉하소서']),
    dict(ref=(18, 5, 1), lang='ko', en='meditation', words=['심사를']),
    dict(ref=(18, 5, 1), lang='ko', en='ear', words=['귀를', '기울이사']),
    dict(ref=(18, 5, 1), lang='ko', en='upon', words=['맞춘']),
    dict(ref=(18, 5, 1), lang='ko', en='Lord', words=['여호와여']),
    dict(ref=(18, 5, 1), lang='ko', en='my#2', words=['나의#2']),
    # 시편 5:2 — 한국어 어순이 영어와 달라 '나의' 셋이 거꾸로 짝지어야 한다.
    # 나의 왕(my King) · 나의 하나님이여(my God) 가 먼저 오고, 나의 부르짖는(my cry)이 뒤다.
    dict(ref=(18, 5, 2), lang='ko', en='my#1', words=['나의#3']),
    dict(ref=(18, 5, 2), lang='ko', en='my#2', words=['나의#1']),
    dict(ref=(18, 5, 2), lang='ko', en='my#3', words=['나의#2']),
    dict(ref=(18, 5, 2), lang='ko', en='cry', words=['부르짖는']),
    dict(ref=(18, 5, 2), lang='ko', en='pray', words=['기도하나이다']),
    # 시편 5:5 — 'workers of iniquity'가 '행악자를' 하나다
    dict(ref=(18, 5, 5), lang='ko', en='workers', words=['행악자를']),
    dict(ref=(18, 5, 5), lang='ko', en='of', words=['행악자를']),
    dict(ref=(18, 5, 5), lang='ko', en='iniquity', words=['행악자를']),
    dict(ref=(18, 5, 5), lang='ko', en='not', words=['못하리이다']),
    dict(ref=(18, 5, 5), lang='ko', en='thou', words=['주는']),
    dict(ref=(18, 5, 5), lang='ko', en='thy', words=['주의']),
    dict(ref=(18, 5, 5), lang='ko', en='hatest', words=['미워하시며']),
    # 시편 5:7 — 'come into'가 '들어가', 'toward'가 '향하여'
    dict(ref=(18, 5, 7), lang='ko', en='come', words=['들어가']),
    dict(ref=(18, 5, 7), lang='ko', en='into', words=['들어가']),
    dict(ref=(18, 5, 7), lang='ko', en='toward', words=['향하여']),
    dict(ref=(18, 5, 7), lang='ko', en='in#1', words=['힘입어']),
    dict(ref=(18, 5, 7), lang='ko', en='holy', words=['성전을']),

    # 시편 5:9 — '저희'가 네 번, their 가 네 번이다. 나오는 순서대로 짝지었다.
    dict(ref=(18, 5, 9), lang='ko', en='their#1', words=['저희#1']),
    dict(ref=(18, 5, 9), lang='ko', en='their#2', words=['저희#2']),
    dict(ref=(18, 5, 9), lang='ko', en='their#3', words=['저희#3']),
    dict(ref=(18, 5, 9), lang='ko', en='their#4', words=['저희#4']),
    dict(ref=(18, 5, 9), lang='ko', en='faithfulness', words=['신실함이']),
    dict(ref=(18, 5, 9), lang='ko', en='in', words=['입에']),
    dict(ref=(18, 5, 9), lang='ko', en='mouth', words=['입에']),
    dict(ref=(18, 5, 9), lang='ko', en='inward', words=['심중이']),
    dict(ref=(18, 5, 9), lang='ko', en='part', words=['심중이']),
    dict(ref=(18, 5, 9), lang='ko', en='is#1', words=['없고']),
    dict(ref=(18, 5, 9), lang='ko', en='is#2', words=['악하며']),
    dict(ref=(18, 5, 9), lang='ko', en='is#3', words=['같고']),
    dict(ref=(18, 5, 9), lang='ko', en='they', words=['아첨하나이다']),
    dict(ref=(18, 5, 9), lang='ko', en='flatter', words=['아첨하나이다']),
    dict(ref=(18, 5, 9), lang='ko', en='with', words=['혀로는']),
    # 시편 5:11 — 기뻐하며(rejoice) · 기뻐(joy) · 외치며(shout) · 즐거워하리이다(be joyful)
    dict(ref=(18, 5, 11), lang='ko', en='rejoice', words=['기뻐하며']),
    dict(ref=(18, 5, 11), lang='ko', en='joy', words=['기뻐']),
    dict(ref=(18, 5, 11), lang='ko', en='shout', words=['외치며']),
    dict(ref=(18, 5, 11), lang='ko', en='be', words=['즐거워하리이다']),
    dict(ref=(18, 5, 11), lang='ko', en='joyful', words=['즐거워하리이다']),
    dict(ref=(18, 5, 11), lang='ko', en='let#2', words=[]),
    dict(ref=(18, 5, 11), lang='ko', en='in#2', words=['주를']),
    dict(ref=(18, 5, 11), lang='ko', en='thee#2', words=['주를']),
    dict(ref=(18, 5, 11), lang='ko', en='in#1', words=['주에게']),
    dict(ref=(18, 5, 11), lang='ko', en='thee#1', words=['주에게']),
    dict(ref=(18, 5, 11), lang='ko', en='put', words=['피하는']),
    dict(ref=(18, 5, 11), lang='ko', en='trust', words=['피하는']),
    dict(ref=(18, 5, 11), lang='ko', en='those', words=['자는']),
    dict(ref=(18, 5, 11), lang='ko', en='that#1', words=['자는']),
    dict(ref=(18, 5, 11), lang='ko', en='that#2', words=['자들은']),
    dict(ref=(18, 5, 11), lang='ko', en='thou', words=['주의#1']),
    # 시편 5:12 — 'the righteous'를 '의인에게' 하나로 묶는다
    dict(ref=(18, 5, 12), lang='ko', en='the', words=['의인에게']),
    dict(ref=(18, 5, 12), lang='ko', en='righteous', words=['의인에게']),
    dict(ref=(18, 5, 12), lang='ko', en='For', words=[]),
    dict(ref=(18, 5, 12), lang='ko', en='bless', words=['복을', '주시고']),
    dict(ref=(18, 5, 12), lang='ko', en='wilt#1', words=['주시고']),
    dict(ref=(18, 5, 12), lang='ko', en='wilt#2', words=['호위하시리이다']),
    dict(ref=(18, 5, 12), lang='ko', en='compass', words=['호위하시리이다']),
    dict(ref=(18, 5, 12), lang='ko', en='thou#1', words=['주는']),
    dict(ref=(18, 5, 12), lang='ko', en='thou#2', words=['주는']),
    dict(ref=(18, 5, 12), lang='ko', en='with#1', words=['은혜로']),
    dict(ref=(18, 5, 12), lang='ko', en='with#2', words=['방패로', '함']),
    dict(ref=(18, 5, 12), lang='ko', en='a', words=['함']),

    # 오바댜 1:1 — '우리가'가 두 번 나오는데 첫째가 뒤의 us 에 걸리고 둘째가 비어 있었다.
    # 앞은 We(들었나니), 뒤는 let us(일어나서)다.
    dict(ref=(30, 1, 1), lang='ko', en='We', words=['우리가#1']),
    dict(ref=(30, 1, 1), lang='ko', en='us', words=['우리가#2']),
    dict(ref=(30, 1, 1), lang='ko', en='have', words=['들었나니']),
    dict(ref=(30, 1, 1), lang='ko', en='heard', words=['들었나니']),
    # 'the Lord GOD' = 주 여호와께서, 'from the LORD' = 여호와께로 말미암아
    dict(ref=(30, 1, 1), lang='ko', en='Lord#1', words=['주']),
    dict(ref=(30, 1, 1), lang='ko', en='God', words=['여호와께서']),
    dict(ref=(30, 1, 1), lang='ko', en='Lord#2', words=['여호와께로']),
    dict(ref=(30, 1, 1), lang='ko', en='from', words=['여호와께로', '말미암아']),
    dict(ref=(30, 1, 1), lang='ko', en='among', words=['중에']),
    dict(ref=(30, 1, 1), lang='ko', en='ambassador', words=['사자가']),
    dict(ref=(30, 1, 1), lang='ko', en='Arise', words=['일어날지어다']),
    dict(ref=(30, 1, 1), lang='ko', en='rise', words=['일어나서']),
    dict(ref=(30, 1, 1), lang='ko', en='up', words=['일어나서']),
    dict(ref=(30, 1, 1), lang='ko', en='against', words=['그로', '더불어']),
    dict(ref=(30, 1, 1), lang='ko', en='her', words=['그로']),
    dict(ref=(30, 1, 1), lang='ko', en='of', words=['오바댜의']),
    dict(ref=(30, 1, 1), lang='ko', en='Thus', words=['이같이']),
    dict(ref=(30, 1, 1), lang='ko', en='saith', words=['말씀하시니라']),
    # 원어→영어에 엉뚱한 것이 붙어 있었다. 에돔(לֶאֱדוֹם)이 of·an 에도 걸려서,
    # 그 영어 낱말에 이어진 한국어 낱말('하는')까지 지명 표시를 받았다.
    # 표시는 원어 → 영어 → 번역 순서로 번지므로 원어 쪽을 바로잡아야 한다.
    dict(ref=(30, 1, 1), lang='or', en='The', words=['חֲזוֹן']),
    dict(ref=(30, 1, 1), lang='or', en='of', words=[]),
    dict(ref=(30, 1, 1), lang='or', en='an', words=['וְצִיר']),
    dict(ref=(30, 1, 1), lang='or', en='in', words=['לַמִּלְחָמָה']),
    dict(ref=(30, 1, 1), lang='or', en='the#3', words=['בַּגּוֹיִם']),
    # 오바댜 1:3 — heart 둘이 꼬여 있었다. 앞의 'thine heart'가 뒤의 '중심의'다.
    dict(ref=(30, 1, 3), lang='ko', en='heart#1', words=['중심의']),
    dict(ref=(30, 1, 3), lang='ko', en='heart#2', words=['중심에']),
    dict(ref=(30, 1, 3), lang='ko', en='bring', words=['끌어내리겠느냐']),
    dict(ref=(30, 1, 3), lang='ko', en='down', words=['끌어내리겠느냐']),
    dict(ref=(30, 1, 3), lang='ko', en='habitation', words=['높은', '곳에']),
    dict(ref=(30, 1, 3), lang='ko', en='is', words=['사는']),
    dict(ref=(30, 1, 3), lang='ko', en='thou', words=['자여']),
    dict(ref=(30, 1, 3), lang='ko', en='to', words=['땅에']),
    # 오바댜 1:4 — '깃들일지라도'가 nest 다. '독수리처럼'이 eagle 과 nest 를 함께 받고 있었다.
    dict(ref=(30, 1, 4), lang='ko', en='nest', words=['깃들일지라도']),
    dict(ref=(30, 1, 4), lang='ko', en='set', words=['깃들일지라도']),
    dict(ref=(30, 1, 4), lang='ko', en='eagle', words=['독수리처럼']),
    dict(ref=(30, 1, 4), lang='ko', en='exalt', words=['높이', '오르며']),
    dict(ref=(30, 1, 4), lang='ko', en='thyself', words=['네가']),
    dict(ref=(30, 1, 4), lang='ko', en='bring', words=['끌어내리리라']),
    dict(ref=(30, 1, 4), lang='ko', en='down', words=['끌어내리리라']),
    dict(ref=(30, 1, 4), lang='ko', en='thence', words=['거기서']),
    dict(ref=(30, 1, 4), lang='ko', en='Lord', words=['나', '여호와가']),
    # 오바댜 1:5 — '포도를 따는 자가'가 grapegatherers 하나다
    dict(ref=(30, 1, 5), lang='ko', en='grapegatherers', words=['포도를', '따는', '자가']),
    dict(ref=(30, 1, 5), lang='ko', en='came#1', words=['이르렀으며']),
    dict(ref=(30, 1, 5), lang='ko', en='came#2', words=['이르렀을지라도#2']),
    dict(ref=(30, 1, 5), lang='ko', en='thee#1', words=['네게#1']),
    dict(ref=(30, 1, 5), lang='ko', en='thee#2', words=['네게#3']),
    dict(ref=(30, 1, 5), lang='ko', en='stolen', words=['취하면']),
    dict(ref=(30, 1, 5), lang='ko', en='enough', words=['그', '마음에', '만족하게']),
    dict(ref=(30, 1, 5), lang='ko', en='not#1', words=['아니하였겠느냐#1']),
    dict(ref=(30, 1, 5), lang='ko', en='not#2', words=['아니하였겠느냐#2']),
    dict(ref=(30, 1, 5), lang='ko', en='grapes', words=['그것을']),
    dict(ref=(30, 1, 5), lang='ko', en='off', words=['망하였는고']),
    dict(ref=(30, 1, 5), lang='ko', en='If', words=['혹시#1']),
    dict(ref=(30, 1, 5), lang='ko', en='if#2', words=['혹시#2']),
    dict(ref=(30, 1, 5), lang='ko', en='would#1', words=['그치지']),
    # 오바댜 1:9 — '산의'가 mount 다
    dict(ref=(30, 1, 9), lang='ko', en='mount', words=['산의']),
    dict(ref=(30, 1, 9), lang='ko', en='one', words=['거민이']),
    dict(ref=(30, 1, 9), lang='ko', en='Teman', words=['드만아']),
    dict(ref=(30, 1, 9), lang='ko', en='O', words=['드만아']),
    dict(ref=(30, 1, 9), lang='ko', en='men', words=['용사들이']),
    dict(ref=(30, 1, 9), lang='ko', en='end', words=['이로', '인하여']),
    # 오바댜 1:19 — '사람은'이 Philistines 에 걸려 블레셋 지명 표시를 물려받고 있었다
    dict(ref=(30, 1, 19), lang='ko', en='Philistines', words=['블레셋을']),
    dict(ref=(30, 1, 19), lang='ko', en='they#1', words=['사람은#1']),
    dict(ref=(30, 1, 19), lang='ko', en='they#2', words=['사람은#2']),
    dict(ref=(30, 1, 19), lang='ko', en='they#3', words=['그들이']),
    dict(ref=(30, 1, 19), lang='ko', en='possess#1', words=['얻을#1']),
    dict(ref=(30, 1, 19), lang='ko', en='possess#2', words=['얻을#2']),
    dict(ref=(30, 1, 19), lang='ko', en='possess#3', words=['얻을#3']),
    # 오바댜 1:13 — '환난을 당하는 날에'가 세 번 되풀이되는데 calamity 셋이 모두 비어
    # 있었다. 되풀이 보완은 한쪽이라도 걸려 있어야 채우므로 이 절은 손으로 맞춘다.
    dict(ref=(30, 1, 13), lang='ko', en='calamity#1', words=['환난을#1']),
    dict(ref=(30, 1, 13), lang='ko', en='calamity#2', words=['환난을#2']),
    dict(ref=(30, 1, 13), lang='ko', en='calamity#3', words=['환난을#3']),
    dict(ref=(30, 1, 13), lang='ko', en='their#1', words=['당하는#1']),
    dict(ref=(30, 1, 13), lang='ko', en='their#3', words=['당하는#2']),
    dict(ref=(30, 1, 13), lang='ko', en='their#5', words=['당하는#3']),
    dict(ref=(30, 1, 13), lang='ko', en='their#2', words=['그#2']),
    dict(ref=(30, 1, 13), lang='ko', en='their#4', words=['그#3']),
    dict(ref=(30, 1, 13), lang='ko', en='the#2', words=['그#1']),
    dict(ref=(30, 1, 13), lang='ko', en='not#1', words=['않을#1']),
    dict(ref=(30, 1, 13), lang='ko', en='not#2', words=['않을#2']),
    dict(ref=(30, 1, 13), lang='ko', en='nor', words=['않을#3']),
    dict(ref=(30, 1, 13), lang='ko', en='entered', words=['들어가지']),
    dict(ref=(30, 1, 13), lang='ko', en='looked', words=['방관하지']),
    dict(ref=(30, 1, 13), lang='ko', en='laid', words=['대지']),
    # 오바댜 1:15 — '만국을'이 'all the heathen' 세 낱말을 받는다
    dict(ref=(30, 1, 15), lang='ko', en='all', words=['만국을']),
    dict(ref=(30, 1, 15), lang='ko', en='the#3', words=['만국을']),
    dict(ref=(30, 1, 15), lang='ko', en='heathen', words=['만국을']),
    dict(ref=(30, 1, 15), lang='ko', en='upon#1', words=['벌할']),
    dict(ref=(30, 1, 15), lang='ko', en='unto', words=['너도']),
    dict(ref=(30, 1, 15), lang='ko', en='shall#1', words=['받을']),
    dict(ref=(30, 1, 15), lang='ko', en='be', words=['받을']),
    dict(ref=(30, 1, 15), lang='ko', en='done#2', words=['받을']),
    dict(ref=(30, 1, 15), lang='ko', en='reward', words=['너의#2', '행한#2']),
    dict(ref=(30, 1, 15), lang='ko', en='thy', words=['너의#2']),
    dict(ref=(30, 1, 15), lang='ko', en='thine', words=['네']),
    dict(ref=(30, 1, 15), lang='ko', en='shall#2', words=['돌아갈']),
    dict(ref=(30, 1, 15), lang='ko', en='upon#2', words=['머리로']),
    # 오바댜 1:16 — '만국인이'도 'all the heathen' 하나다. drink 가 두 번 나온다.
    dict(ref=(30, 1, 16), lang='ko', en='all', words=['만국인이']),
    dict(ref=(30, 1, 16), lang='ko', en='the', words=['만국인이']),
    dict(ref=(30, 1, 16), lang='ko', en='heathen', words=['만국인이']),
    dict(ref=(30, 1, 16), lang='ko', en='drink#1', words=['마시리니']),
    dict(ref=(30, 1, 16), lang='ko', en='drink#2', words=['마시고']),
    dict(ref=(30, 1, 16), lang='ko', en='swallow', words=['삼켜서']),
    dict(ref=(30, 1, 16), lang='ko', en='down', words=['삼켜서']),
    dict(ref=(30, 1, 16), lang='ko', en='drunk', words=['마신']),
    dict(ref=(30, 1, 16), lang='ko', en='have', words=['마신']),
    dict(ref=(30, 1, 16), lang='ko', en='ye', words=['너희가']),
    dict(ref=(30, 1, 16), lang='ko', en='shall#1', words=['마시리니']),
    dict(ref=(30, 1, 16), lang='ko', en='yea', words=['곧']),
    dict(ref=(30, 1, 16), lang='ko', en='though', words=['본래']),
    dict(ref=(30, 1, 16), lang='ko', en='been', words=['없던']),
    dict(ref=(30, 1, 16), lang='ko', en='as#2', words=['같이#2']),
    # 나훔 1:2 — '투기하시며'가 jealous, 'God is'가 '하나님이시니라'다
    dict(ref=(33, 1, 2), lang='ko', en='jealous', words=['투기하시며']),
    dict(ref=(33, 1, 2), lang='ko', en='God', words=['하나님이시니라']),
    dict(ref=(33, 1, 2), lang='ko', en='is#1', words=['하나님이시니라']),
    dict(ref=(33, 1, 2), lang='ko', en='Lord#1', words=['여호와는#1']),
    dict(ref=(33, 1, 2), lang='ko', en='Lord#2', words=['여호와는#2']),
    dict(ref=(33, 1, 2), lang='ko', en='revengeth#1', words=['보복하시는']),
    dict(ref=(33, 1, 2), lang='ko', en='revengeth#2', words=['보복하시며']),
    dict(ref=(33, 1, 2), lang='ko', en='take', words=['보복하시며']),
    dict(ref=(33, 1, 2), lang='ko', en='vengeance', words=['보복하시며']),
    dict(ref=(33, 1, 2), lang='ko', en='furious', words=['진노를']),
    dict(ref=(33, 1, 2), lang='ko', en='wrath', words=['진노를']),
    dict(ref=(33, 1, 2), lang='ko', en='reserveth', words=['품으시며']),
    dict(ref=(33, 1, 2), lang='ko', en='on', words=['자에게']),
    dict(ref=(33, 1, 2), lang='ko', en='enemies', words=['자에게']),
    # 나훔 1:3 — '노하기를'은 anger 만 받는다(slow 은 '더디하시며'다).
    # 'the wicked'가 '죄인을', 'acquit'(וְנַקֵּה)이 '사하지', 'feet'가 '발의'다.
    dict(ref=(33, 1, 3), lang='ko', en='anger', words=['노하기를']),
    dict(ref=(33, 1, 3), lang='ko', en='slow', words=['더디하시며']),
    dict(ref=(33, 1, 3), lang='ko', en='the#1', words=['죄인을']),
    dict(ref=(33, 1, 3), lang='ko', en='wicked', words=['죄인을']),
    dict(ref=(33, 1, 3), lang='ko', en='acquit', words=['사하지']),
    dict(ref=(33, 1, 3), lang='ko', en='at', words=['결코']),
    dict(ref=(33, 1, 3), lang='ko', en='all', words=['결코']),
    dict(ref=(33, 1, 3), lang='ko', en='will', words=['아니하시느니라']),
    dict(ref=(33, 1, 3), lang='ko', en='not', words=['아니하시느니라']),
    dict(ref=(33, 1, 3), lang='ko', en='feet', words=['발의']),
    dict(ref=(33, 1, 3), lang='ko', en='Lord#2', words=['여호와의']),
    dict(ref=(33, 1, 3), lang='ko', en='hath', words=['여호와의']),
    dict(ref=(33, 1, 3), lang='ko', en='his#1', words=['여호와의']),
    dict(ref=(33, 1, 3), lang='ko', en='his#2', words=['그']),
    dict(ref=(33, 1, 3), lang='ko', en='whirlwind', words=['회리바람과']),
    dict(ref=(33, 1, 3), lang='ko', en='storm', words=['광풍에']),
    # 나훔 1:15 — 히브리어 מְבַשֵּׂר(보하고) / מַשְׁמִיעַ(전하는) 둘이 영어 bringeth /
    # publisheth 로 갈라지는데 '전하는'이 비어 있었다. 'utterly cut off'는 '진멸되었으니'
    # 하나가 받고, 뒤의 is 가 엉뚱하게 '있도다'에 걸려 있었다.
    dict(ref=(33, 1, 15), lang='ko', en='publisheth', words=['전하는']),
    dict(ref=(33, 1, 15), lang='ko', en='bringeth', words=['보하고']),
    dict(ref=(33, 1, 15), lang='ko', en='him', words=['자의']),
    dict(ref=(33, 1, 15), lang='ko', en='of', words=['자의']),
    dict(ref=(33, 1, 15), lang='ko', en='Behold', words=['볼지어다']),
    dict(ref=(33, 1, 15), lang='ko', en='perform', words=['갚을지어다']),
    dict(ref=(33, 1, 15), lang='ko', en='pass', words=['통행하지']),
    dict(ref=(33, 1, 15), lang='ko', en='through', words=['가운데로']),
    dict(ref=(33, 1, 15), lang='ko', en='thee', words=['네#3']),
    dict(ref=(33, 1, 15), lang='ko', en='utterly', words=['진멸되었으니']),
    dict(ref=(33, 1, 15), lang='ko', en='cut', words=['진멸되었으니']),
    dict(ref=(33, 1, 15), lang='ko', en='off', words=['진멸되었으니']),
    dict(ref=(33, 1, 15), lang='ko', en='is', words=['진멸되었으니']),
    dict(ref=(33, 1, 15), lang='ko', en='solemn', words=['절기를']),
    dict(ref=(33, 1, 15), lang='ko', en='thy#1', words=['네#1']),
    dict(ref=(33, 1, 15), lang='ko', en='thy#2', words=['네#2']),
    # 나훔 2:2 — 히브리어 בֹּקְקִים(약탈자들이) / בְקָקוּם(약탈하였고)이 영어 emptiers /
    # have emptied 로 갈라지는데 '약탈자들이'가 emptied 를 받고 '약탈하였고'가 비어 있었다.
    dict(ref=(33, 2, 2), lang='ko', en='emptiers', words=['약탈자들이']),
    dict(ref=(33, 2, 2), lang='ko', en='emptied', words=['약탈하였고']),
    dict(ref=(33, 2, 2), lang='ko', en='have', words=['약탈하였고']),
    dict(ref=(33, 2, 2), lang='ko', en='them', words=['약탈하였고']),
    dict(ref=(33, 2, 2), lang='ko', en='out', words=['약탈하였고']),
    dict(ref=(33, 2, 2), lang='ko', en='marred', words=['없이', '하였음이라']),
    dict(ref=(33, 2, 2), lang='ko', en='excellency#1', words=['영광을']),
    dict(ref=(33, 2, 2), lang='ko', en='of#1', words=['영광을']),
    dict(ref=(33, 2, 2), lang='ko', en='excellency#2', words=['영광']),
    dict(ref=(33, 2, 2), lang='ko', en='of#2', words=['영광']),
    dict(ref=(33, 2, 2), lang='ko', en='hath', words=['회복하시되']),
    dict(ref=(33, 2, 2), lang='ko', en='turned', words=['회복하시되']),
    dict(ref=(33, 2, 2), lang='ko', en='away', words=['회복하시되']),
    dict(ref=(33, 2, 2), lang='ko', en='as', words=['같게']),
    dict(ref=(33, 2, 2), lang='ko', en='for', words=['이는']),
    # 나훔 2:4 — '대로에서'가 'in the broad ways'를 받아야 하는데 seem 에 걸려 있었고,
    # 그 바람에 절 뒷부분이 줄줄이 어긋나 있었다(run → '달리며', justle → '빠르기').
    dict(ref=(33, 2, 4), lang='ko', en='in#2', words=['대로에서']),
    dict(ref=(33, 2, 4), lang='ko', en='the#2', words=['대로에서']),
    dict(ref=(33, 2, 4), lang='ko', en='broad', words=['대로에서']),
    dict(ref=(33, 2, 4), lang='ko', en='ways', words=['대로에서']),
    dict(ref=(33, 2, 4), lang='ko', en='The', words=['그#1']),
    dict(ref=(33, 2, 4), lang='ko', en='in#1', words=['거리에']),
    dict(ref=(33, 2, 4), lang='ko', en='the#1', words=['거리에']),
    dict(ref=(33, 2, 4), lang='ko', en='streets', words=['거리에']),
    dict(ref=(33, 2, 4), lang='ko', en='rage', words=['미치게', '달리며']),
    dict(ref=(33, 2, 4), lang='ko', en='shall#1', words=['달리며']),
    dict(ref=(33, 2, 4), lang='ko', en='one', words=['이리']),
    dict(ref=(33, 2, 4), lang='ko', en='against', words=['이리', '저리']),
    dict(ref=(33, 2, 4), lang='ko', en='another', words=['저리']),
    dict(ref=(33, 2, 4), lang='ko', en='justle', words=['빨리']),
    dict(ref=(33, 2, 4), lang='ko', en='they#1', words=['가니']),
    dict(ref=(33, 2, 4), lang='ko', en='shall#2', words=['가니']),
    dict(ref=(33, 2, 4), lang='ko', en='they#2', words=['그#2']),
    dict(ref=(33, 2, 4), lang='ko', en='seem', words=['모양이']),
    dict(ref=(33, 2, 4), lang='ko', en='shall#3', words=['모양이']),
    dict(ref=(33, 2, 4), lang='ko', en='like#1', words=['같고']),
    dict(ref=(33, 2, 4), lang='ko', en='run', words=['빠르기']),
    dict(ref=(33, 2, 4), lang='ko', en='they#3', words=['빠르기']),
    dict(ref=(33, 2, 4), lang='ko', en='shall#4', words=['빠르기']),
    dict(ref=(33, 2, 4), lang='ko', en='the#3', words=['번개']),
    dict(ref=(33, 2, 4), lang='ko', en='like#2', words=['같도다']),
    # 나훔 2:5
    dict(ref=(33, 2, 5), lang='ko', en='defence', words=['막을']),
    dict(ref=(33, 2, 5), lang='ko', en='the#2', words=['막을']),
    dict(ref=(33, 2, 5), lang='ko', en='He', words=['그가']),
    dict(ref=(33, 2, 5), lang='ko', en='his', words=['그']),
    dict(ref=(33, 2, 5), lang='ko', en='worthies', words=['존귀한', '자를']),
    dict(ref=(33, 2, 5), lang='ko', en='recount', words=['생각해', '내니']),
    dict(ref=(33, 2, 5), lang='ko', en='shall#1', words=['내니']),
    dict(ref=(33, 2, 5), lang='ko', en='they#1', words=['그들이']),
    dict(ref=(33, 2, 5), lang='ko', en='walk', words=['듯이']),
    dict(ref=(33, 2, 5), lang='ko', en='their', words=['듯이']),
    dict(ref=(33, 2, 5), lang='ko', en='make', words=['달려서']),
    dict(ref=(33, 2, 5), lang='ko', en='to', words=['이르러']),
    dict(ref=(33, 2, 5), lang='ko', en='the#1', words=['성에']),
    dict(ref=(33, 2, 5), lang='ko', en='thereof', words=['성에']),
    dict(ref=(33, 2, 5), lang='ko', en='shall#4', words=['예비하도다']),
    # 나훔 2:6 — '강들의 수문이'가 'The gates of the rivers'다
    dict(ref=(33, 2, 6), lang='ko', en='The', words=['수문이']),
    dict(ref=(33, 2, 6), lang='ko', en='gates', words=['수문이']),
    dict(ref=(33, 2, 6), lang='ko', en='of', words=['강들의']),
    dict(ref=(33, 2, 6), lang='ko', en='the#1', words=['강들의']),
    dict(ref=(33, 2, 6), lang='ko', en='shall#1', words=['열리고']),
    dict(ref=(33, 2, 6), lang='ko', en='be#1', words=['열리고']),
    dict(ref=(33, 2, 6), lang='ko', en='the#2', words=['왕궁이']),
    dict(ref=(33, 2, 6), lang='ko', en='shall#2', words=['소멸되며']),
    dict(ref=(33, 2, 6), lang='ko', en='be#2', words=['소멸되며']),
    # 나훔 2:11 — '젊은 사자의'가 'the young lions'다
    dict(ref=(33, 2, 11), lang='ko', en='young', words=['젊은']),
    dict(ref=(33, 2, 11), lang='ko', en='the#4', words=['젊은']),
    dict(ref=(33, 2, 11), lang='ko', en='lions#2', words=['사자의#2']),
    dict(ref=(33, 2, 11), lang='ko', en='lions#1', words=['사자의#1']),
    dict(ref=(33, 2, 11), lang='ko', en='dwelling', words=['굴이']),
    dict(ref=(33, 2, 11), lang='ko', en='Where', words=['어디뇨#1']),
    dict(ref=(33, 2, 11), lang='ko', en='is', words=['어디뇨#1']),
    dict(ref=(33, 2, 11), lang='ko', en='where', words=['어디뇨#2']),
    dict(ref=(33, 2, 11), lang='ko', en='feedingplace', words=['먹는', '곳이']),
    dict(ref=(33, 2, 11), lang='ko', en='lion#1', words=['수사자']),
    dict(ref=(33, 2, 11), lang='ko', en='old', words=['암사자가']),
    dict(ref=(33, 2, 11), lang='ko', en='lion#2', words=['암사자가']),
    dict(ref=(33, 2, 11), lang='ko', en='whelp', words=['새끼']),
    dict(ref=(33, 2, 11), lang='ko', en='lion#3', words=['사자와']),
    dict(ref=(33, 2, 11), lang='ko', en='made', words=['할']),
    dict(ref=(33, 2, 11), lang='ko', en='even', words=['전에는']),
    # 나훔 2:12 — '충분히'가 enough. filled 하나가 '채웠고'와 '채웠었도다' 둘을 받는다.
    dict(ref=(33, 2, 12), lang='ko', en='enough', words=['충분히']),
    dict(ref=(33, 2, 12), lang='ko', en='filled', words=['채웠고', '채웠었도다']),
    dict(ref=(33, 2, 12), lang='ko', en='pieces', words=['식물을']),
    dict(ref=(33, 2, 12), lang='ko', en='in', words=['식물을']),
    dict(ref=(33, 2, 12), lang='ko', en='did', words=['찢고']),
    dict(ref=(33, 2, 12), lang='ko', en='strangled', words=['무엇을', '움켜서는']),
    dict(ref=(33, 2, 12), lang='ko', en='ravin', words=['취한', '것으로#1']),
    dict(ref=(33, 2, 12), lang='ko', en='with#2', words=['것으로#1']),
    dict(ref=(33, 2, 12), lang='ko', en='prey', words=['찢은', '것으로#2']),
    dict(ref=(33, 2, 12), lang='ko', en='with#1', words=['것으로#2']),
    dict(ref=(33, 2, 12), lang='ko', en='for#2', words=['위하여#2']),
    dict(ref=(33, 2, 12), lang='ko', en='for#1', words=['위하여#1']),
    dict(ref=(33, 2, 12), lang='ko', en='his#2', words=['그#2']),
    dict(ref=(33, 2, 12), lang='ko', en='his#3', words=['그#4']),
    dict(ref=(33, 2, 12), lang='ko', en='his#4', words=['그#3']),
    # 나훔 3:1 — '강포가'가 robbery, 뒤의 '늑탈이'가 the prey 다
    dict(ref=(33, 3, 1), lang='ko', en='robbery', words=['강포가']),
    dict(ref=(33, 3, 1), lang='ko', en='prey', words=['늑탈이']),
    dict(ref=(33, 3, 1), lang='ko', en='the#2', words=['늑탈이']),
    dict(ref=(33, 3, 1), lang='ko', en='to', words=['있을진저']),
    dict(ref=(33, 3, 1), lang='ko', en='the#1', words=['피']),
    dict(ref=(33, 3, 1), lang='ko', en='is', words=['가득하며']),
    dict(ref=(33, 3, 1), lang='ko', en='all', words=['가득하며']),
    dict(ref=(33, 3, 1), lang='ko', en='of', words=['궤휼과']),
    # 나훔 3:2 — '병거바퀴'가 the wheels(אוֹפָן), '뛰는'이 pransing 이다
    dict(ref=(33, 3, 2), lang='ko', en='wheels', words=['병거바퀴']),
    dict(ref=(33, 3, 2), lang='ko', en='the#3', words=['병거바퀴']),
    dict(ref=(33, 3, 2), lang='ko', en='pransing', words=['뛰는']),
    dict(ref=(33, 3, 2), lang='ko', en='rattling', words=['굉굉하는']),
    dict(ref=(33, 3, 2), lang='ko', en='noise#1', words=['소리#1']),
    dict(ref=(33, 3, 2), lang='ko', en='noise#2', words=['소리#2']),
    dict(ref=(33, 3, 2), lang='ko', en='jumping', words=['달리는']),
    dict(ref=(33, 3, 2), lang='ko', en='a', words=['채찍']),
    # 나훔 3:4 — טוֹבַת(아리따운)·הַמֹּכֶרֶת(미혹하고)·כְּשָׁפִים(마술)이 모두 비어 있었다.
    # 한국어는 '미혹하고 … 미혹하느니라'로 동사를 두 번 쓰는데 영어는 selleth 하나다.
    dict(ref=(33, 3, 4), lang='ko', en='wellfavoured', words=['아리따운']),
    dict(ref=(33, 3, 4), lang='ko', en='selleth', words=['미혹하고', '미혹하느니라']),
    dict(ref=(33, 3, 4), lang='ko', en='that', words=['미혹하고']),
    dict(ref=(33, 3, 4), lang='ko', en='witchcrafts#1', words=['마술의']),
    dict(ref=(33, 3, 4), lang='ko', en='of#4', words=['마술의']),
    dict(ref=(33, 3, 4), lang='ko', en='mistress', words=['주인된']),
    dict(ref=(33, 3, 4), lang='ko', en='the#4', words=['주인된']),
    dict(ref=(33, 3, 4), lang='ko', en='witchcrafts#2', words=['마술로']),
    dict(ref=(33, 3, 4), lang='ko', en='through#2', words=['마술로']),
    dict(ref=(33, 3, 4), lang='ko', en='her#2', words=['그#2']),
    dict(ref=(33, 3, 4), lang='ko', en='her#1', words=['그#1']),
    dict(ref=(33, 3, 4), lang='ko', en='whoredoms#2', words=['음행으로']),
    dict(ref=(33, 3, 4), lang='ko', en='through#1', words=['음행으로']),
    dict(ref=(33, 3, 4), lang='ko', en='whoredoms#1', words=['음행을']),
    dict(ref=(33, 3, 4), lang='ko', en='Because', words=['이는', '인함이라']),
    dict(ref=(33, 3, 4), lang='ko', en='of#1', words=['인함이라']),
    dict(ref=(33, 3, 4), lang='ko', en='of#2', words=['함을']),
    dict(ref=(33, 3, 4), lang='ko', en='the#3', words=['기생이']),
    dict(ref=(33, 3, 4), lang='ko', en='families', words=['여러', '족속을']),
    # 나훔 3:4 — טוֹבַת חֵן(아리따운)이 영어 wellfavoured 에 이어져 있지 않았다
    dict(ref=(33, 3, 4), lang='or', en='wellfavoured', words=['טוֹבַת', 'חֵן']),
    # 나훔 3:5 — '열국에'와 '열방에'가 서로 바뀌어 있었다.
    # nations 는 벌거벗은 것을 보이는 쪽(열국에), kingdoms 는 부끄러운 곳 쪽(열방에)이다.
    dict(ref=(33, 3, 5), lang='ko', en='discover', words=['걷어쳐', '이르게']),
    dict(ref=(33, 3, 5), lang='ko', en='nakedness', words=['벌거벗은', '것을']),
    dict(ref=(33, 3, 5), lang='ko', en='nations', words=['열국에']),
    dict(ref=(33, 3, 5), lang='ko', en='the#1', words=['열국에']),
    dict(ref=(33, 3, 5), lang='ko', en='kingdoms', words=['열방에']),
    dict(ref=(33, 3, 5), lang='ko', en='the#2', words=['열방에']),
    dict(ref=(33, 3, 5), lang='ko', en='shame', words=['부끄러운', '곳을']),
    dict(ref=(33, 3, 5), lang='ko', en='shew', words=['보이며', '보일']),
    dict(ref=(33, 3, 5), lang='ko', en='am', words=['되어서']),
    dict(ref=(33, 3, 5), lang='ko', en='upon', words=['얼굴에']),
    dict(ref=(33, 3, 5), lang='ko', en='thy#3', words=['네#3']),
    dict(ref=(33, 3, 5), lang='ko', en='thy#4', words=['네#4']),
    # 나훔 3:6
    dict(ref=(33, 3, 6), lang='ko', en='filth', words=['더러운', '것을']),
    dict(ref=(33, 3, 6), lang='ko', en='vile', words=['능욕하여']),
    dict(ref=(33, 3, 6), lang='ko', en='set', words=['되게']),
    dict(ref=(33, 3, 6), lang='ko', en='make', words=['하리니']),
    # 나훔 3:7 — '위하여 애곡하며'가 bemoan 이다
    dict(ref=(33, 3, 7), lang='ko', en='bemoan', words=['위하여', '애곡하며']),
    dict(ref=(33, 3, 7), lang='ko', en='that#1', words=['자가']),
    dict(ref=(33, 3, 7), lang='ko', en='from', words=['네게서']),
    dict(ref=(33, 3, 7), lang='ko', en='thee#2', words=['네게서']),
    dict(ref=(33, 3, 7), lang='ko', en='thee#3', words=['너를#2']),
    dict(ref=(33, 3, 7), lang='ko', en='that#2', words=['자를']),
    dict(ref=(33, 3, 7), lang='ko', en='upon', words=['보는']),
    dict(ref=(33, 3, 7), lang='ko', en='come', words=['그', '때에']),
    # 나훔 3:8
    dict(ref=(33, 3, 8), lang='ko', en='situate', words=['있으므로']),
    dict(ref=(33, 3, 8), lang='ko', en='was#1', words=['있으므로']),
    dict(ref=(33, 3, 8), lang='ko', en='round', words=['둘렸으니']),
    dict(ref=(33, 3, 8), lang='ko', en='about', words=['둘렸으니']),
    dict(ref=(33, 3, 8), lang='ko', en='rampart', words=['성루가']),
    dict(ref=(33, 3, 8), lang='ko', en='whose', words=['성루가']),
    dict(ref=(33, 3, 8), lang='ko', en='among', words=['사이에']),
    dict(ref=(33, 3, 8), lang='ko', en='was#2', words=['되었고']),
    dict(ref=(33, 3, 8), lang='ko', en='was#3', words=['되었으며']),
    dict(ref=(33, 3, 8), lang='ko', en='her', words=['성벽이']),
    dict(ref=(33, 3, 8), lang='ko', en='that#1', words=['그는']),
    dict(ref=(33, 3, 8), lang='ko', en='sea#1', words=['바다가#1']),
    dict(ref=(33, 3, 8), lang='ko', en='sea#2', words=['바다가#2']),
    dict(ref=(33, 3, 8), lang='ko', en='from', words=['바다가#2']),
    # 나훔 3:10 — '자들은'이 honourable men 의 men, '결박되었나니'가 were bound in
    dict(ref=(33, 3, 10), lang='ko', en='men#1', words=['자들은']),
    dict(ref=(33, 3, 10), lang='ko', en='bound', words=['결박되었나니']),
    dict(ref=(33, 3, 10), lang='ko', en='in#2', words=['결박되었나니']),
    dict(ref=(33, 3, 10), lang='ko', en='were#2', words=['결박되었나니']),
    dict(ref=(33, 3, 10), lang='ko', en='great', words=['대인은']),
    dict(ref=(33, 3, 10), lang='ko', en='men#2', words=['대인은']),
    dict(ref=(33, 3, 10), lang='ko', en='captivity', words=['포로가']),
    dict(ref=(33, 3, 10), lang='ko', en='into', words=['되어']),
    dict(ref=(33, 3, 10), lang='ko', en='carried', words=['사로잡혀']),
    dict(ref=(33, 3, 10), lang='ko', en='away', words=['사로잡혀']),
    dict(ref=(33, 3, 10), lang='ko', en='went', words=['갔고']),
    dict(ref=(33, 3, 10), lang='ko', en='top', words=['모퉁이', '모퉁이에']),
    dict(ref=(33, 3, 10), lang='ko', en='streets', words=['길']),
    dict(ref=(33, 3, 10), lang='ko', en='pieces', words=['부숴졌으며']),
    dict(ref=(33, 3, 10), lang='ko', en='dashed', words=['메어침을', '당하여']),
    dict(ref=(33, 3, 10), lang='ko', en='lots', words=['제비']),
    dict(ref=(33, 3, 10), lang='ko', en='cast', words=['뽑혀', '나뉘었고']),
    dict(ref=(33, 3, 10), lang='ko', en='all#2', words=['모든']),
    # 나훔 3:11
    dict(ref=(33, 3, 11), lang='ko', en='drunken', words=['취한바']),
    dict(ref=(33, 3, 11), lang='ko', en='be#1', words=['취한바']),
    dict(ref=(33, 3, 11), lang='ko', en='because', words=['인하여']),
    dict(ref=(33, 3, 11), lang='ko', en='of', words=['인하여']),
    dict(ref=(33, 3, 11), lang='ko', en='seek', words=['찾아보리라']),
    dict(ref=(33, 3, 11), lang='ko', en='shalt#3', words=['찾아보리라']),
    dict(ref=(33, 3, 11), lang='ko', en='Thou', words=['너도#1']),
    dict(ref=(33, 3, 11), lang='ko', en='also#1', words=['너도#1']),
    dict(ref=(33, 3, 11), lang='ko', en='thou#2', words=['너도#2']),
    dict(ref=(33, 3, 11), lang='ko', en='also#2', words=['너도#2']),
    dict(ref=(33, 3, 11), lang='ko', en='shalt#1', words=['되어']),
    dict(ref=(33, 3, 11), lang='ko', en='hid', words=['숨으리라']),
    dict(ref=(33, 3, 11), lang='ko', en='be#2', words=['숨으리라']),
    # 나훔 3:12 — '산성은'이 strong holds
    dict(ref=(33, 3, 12), lang='ko', en='holds', words=['산성은']),
    dict(ref=(33, 3, 12), lang='ko', en='strong', words=['산성은']),
    dict(ref=(33, 3, 12), lang='ko', en='fig', words=['무화과나무의']),
    dict(ref=(33, 3, 12), lang='ko', en='trees', words=['무화과나무의']),
    dict(ref=(33, 3, 12), lang='ko', en='figs', words=['열매가']),
    dict(ref=(33, 3, 12), lang='ko', en='eater', words=['먹는', '자의']),
    dict(ref=(33, 3, 12), lang='ko', en='like', words=['같으리라']),
    dict(ref=(33, 3, 12), lang='ko', en='be#2', words=['하면']),
    dict(ref=(33, 3, 12), lang='ko', en='if', words=['하면']),
    dict(ref=(33, 3, 12), lang='ko', en='fall', words=['떨어짐과']),
    dict(ref=(33, 3, 12), lang='ko', en='into', words=['떨어짐과']),
    dict(ref=(33, 3, 12), lang='ko', en='mouth', words=['입에']),
    # 나훔 3:13 — '여인'이 women, '같고'가 are
    dict(ref=(33, 3, 13), lang='ko', en='women', words=['여인']),
    dict(ref=(33, 3, 13), lang='ko', en='are', words=['같고']),
    dict(ref=(33, 3, 13), lang='ko', en='people', words=['장정들은']),
    dict(ref=(33, 3, 13), lang='ko', en='thy#1', words=['너의#1']),
    dict(ref=(33, 3, 13), lang='ko', en='thy#2', words=['너의#2']),
    dict(ref=(33, 3, 13), lang='ko', en='thine', words=['너의#3']),
    dict(ref=(33, 3, 13), lang='ko', en='thy#3', words=['빗장들은']),
    dict(ref=(33, 3, 13), lang='ko', en='midst', words=['중']),
    dict(ref=(33, 3, 13), lang='ko', en='open', words=['열리고']),
    dict(ref=(33, 3, 13), lang='ko', en='set', words=['열리고']),
    dict(ref=(33, 3, 13), lang='ko', en='devour', words=['타도다']),
    dict(ref=(33, 3, 13), lang='ko', en='fire', words=['불에']),
    # 나훔 3:14 — '산성들을'이 thy strong holds, '흙을'이 the morter(בַחֹמֶר)
    dict(ref=(33, 3, 14), lang='ko', en='holds', words=['산성들을']),
    dict(ref=(33, 3, 14), lang='ko', en='strong#1', words=['산성들을']),
    dict(ref=(33, 3, 14), lang='ko', en='thy', words=['너의']),
    dict(ref=(33, 3, 14), lang='ko', en='morter', words=['흙을']),
    dict(ref=(33, 3, 14), lang='ko', en='the#2', words=['흙을']),
    dict(ref=(33, 3, 14), lang='ko', en='fortify', words=['견고케', '하며']),
    dict(ref=(33, 3, 14), lang='ko', en='make', words=['수리하라']),
    dict(ref=(33, 3, 14), lang='ko', en='strong#2', words=['수리하라']),
    dict(ref=(33, 3, 14), lang='ko', en='brickkiln', words=['벽돌', '가마를']),
    dict(ref=(33, 3, 14), lang='ko', en='for', words=['예비하며']),
    dict(ref=(33, 3, 14), lang='ko', en='the#1', words=['것을']),
    # 나훔 3:15 — '베기를'이 cut off, '늣 같이'가 as the cankerworm,
    # '많게 할지어다'가 make … many 다. cankerworm 과 locusts 가 뒤섞여 있었다.
    dict(ref=(33, 3, 15), lang='ko', en='cut', words=['베기를']),
    dict(ref=(33, 3, 15), lang='ko', en='off', words=['베기를']),
    dict(ref=(33, 3, 15), lang='ko', en='cankerworm#1', words=['늣의']),
    dict(ref=(33, 3, 15), lang='ko', en='the#3', words=['늣의']),
    dict(ref=(33, 3, 15), lang='ko', en='cankerworm#2', words=['늣']),
    dict(ref=(33, 3, 15), lang='ko', en='the#4', words=['늣']),
    dict(ref=(33, 3, 15), lang='ko', en='as#1', words=['같이#2']),
    dict(ref=(33, 3, 15), lang='ko', en='as#2', words=['같이#3']),
    dict(ref=(33, 3, 15), lang='ko', en='like', words=['같이#1']),
    dict(ref=(33, 3, 15), lang='ko', en='many#1', words=['많게#1']),
    dict(ref=(33, 3, 15), lang='ko', en='many#2', words=['많게#2']),
    dict(ref=(33, 3, 15), lang='ko', en='make#1', words=['할지어다#1']),
    dict(ref=(33, 3, 15), lang='ko', en='make#2', words=['할지어다#2']),
    dict(ref=(33, 3, 15), lang='ko', en='thyself#1', words=['스스로#1']),
    dict(ref=(33, 3, 15), lang='ko', en='thyself#2', words=['스스로#2']),
    dict(ref=(33, 3, 15), lang='ko', en='locusts', words=['메뚜기']),
    dict(ref=(33, 3, 15), lang='ko', en='the#5', words=['메뚜기']),
    dict(ref=(33, 3, 15), lang='ko', en='thee#1', words=['너를#1']),
    dict(ref=(33, 3, 15), lang='ko', en='thee#2', words=['너를#2']),
    dict(ref=(33, 3, 15), lang='ko', en='thee#3', words=['먹는']),
    dict(ref=(33, 3, 15), lang='ko', en='eat', words=['먹는']),
    dict(ref=(33, 3, 15), lang='ko', en='up', words=['하리라']),
    # 나훔 3:16 — וַיָּעֹף(날아감과 같고)이 flieth away 다
    dict(ref=(33, 3, 16), lang='ko', en='flieth', words=['날아감과', '같고']),
    dict(ref=(33, 3, 16), lang='ko', en='away', words=['날아감과']),
    dict(ref=(33, 3, 16), lang='ko', en='spoileth', words=['날개를', '펴서']),
    dict(ref=(33, 3, 16), lang='ko', en='multiplied', words=['많게']),
    dict(ref=(33, 3, 16), lang='ko', en='hast', words=['하였으나']),
    dict(ref=(33, 3, 16), lang='ko', en='Thou', words=['네가']),
    dict(ref=(33, 3, 16), lang='ko', en='thy', words=['네']),
    dict(ref=(33, 3, 16), lang='or', en='flieth', words=['וַיָּעֹף']),
    # 나훔 3:17 — 여기도 '날아감과 같으니'가 flee away 다
    dict(ref=(33, 3, 17), lang='ko', en='flee', words=['날아감과', '같으니']),
    dict(ref=(33, 3, 17), lang='ko', en='away', words=['날아감과']),
    dict(ref=(33, 3, 17), lang='ko', en='captains', words=['대장은']),
    dict(ref=(33, 3, 17), lang='ko', en='crowned', words=['방백은']),
    dict(ref=(33, 3, 17), lang='ko', en='as#1', words=['같고']),
    dict(ref=(33, 3, 17), lang='ko', en='camp', words=['깃들였다가']),
    dict(ref=(33, 3, 17), lang='ko', en='Thy', words=['너의#1']),
    dict(ref=(33, 3, 17), lang='ko', en='thy', words=['너의#2']),
    dict(ref=(33, 3, 17), lang='ko', en='known', words=['알', '수']),
    dict(ref=(33, 3, 5), lang='ko', en='against', words=['대적이']),
    dict(ref=(33, 3, 10), lang='ko', en='were#1', words=['메어침을']),
    # 나훔 3:18 — נָמוּ(자고)가 slumber 다. '누워 쉬며'는 'shall dwell in the dust' 쪽인데
    # '누워'가 slumber 를 받고 있었다.
    dict(ref=(33, 3, 18), lang='ko', en='slumber', words=['자고']),
    dict(ref=(33, 3, 18), lang='ko', en='dwell', words=['누워', '쉬며']),
    dict(ref=(33, 3, 18), lang='ko', en='shall', words=['누워']),
    dict(ref=(33, 3, 18), lang='ko', en='dust', words=['쉬며']),
    dict(ref=(33, 3, 18), lang='ko', en='in', words=['쉬며']),
    dict(ref=(33, 3, 18), lang='ko', en='Thy', words=['네#1']),
    dict(ref=(33, 3, 18), lang='ko', en='thy#1', words=['네#2']),
    dict(ref=(33, 3, 18), lang='ko', en='thy#2', words=['네#3']),
    dict(ref=(33, 3, 18), lang='ko', en='upon', words=['산들에']),
    dict(ref=(33, 3, 18), lang='ko', en='is', words=['흩어지나']),
    # 나훔 3:19 — '다친 것은'이 thy bruise 다. 'thy'와 'thee'가 다섯 번 나와 모두 어긋나 있었다.
    dict(ref=(33, 3, 19), lang='ko', en='bruise', words=['다친', '것은']),
    dict(ref=(33, 3, 19), lang='ko', en='healing', words=['고칠', '수']),
    dict(ref=(33, 3, 19), lang='ko', en='There', words=['없고']),
    dict(ref=(33, 3, 19), lang='ko', en='no', words=['없고']),
    dict(ref=(33, 3, 19), lang='ko', en='is#1', words=['없고']),
    dict(ref=(33, 3, 19), lang='ko', en='thy#1', words=['너의']),
    dict(ref=(33, 3, 19), lang='ko', en='thy#2', words=['네#1']),
    dict(ref=(33, 3, 19), lang='ko', en='thee#1', words=['네#2']),
    dict(ref=(33, 3, 19), lang='ko', en='thee#2', words=['너를']),
    dict(ref=(33, 3, 19), lang='ko', en='thy#3', words=['네#3']),
    dict(ref=(33, 3, 19), lang='ko', en='bruit', words=['소식을']),
    dict(ref=(33, 3, 19), lang='ko', en='is#2', words=['중하도다']),
    dict(ref=(33, 3, 19), lang='ko', en='hands', words=['손뼉을']),
    dict(ref=(33, 3, 19), lang='ko', en='clap', words=['치나니']),
    dict(ref=(33, 3, 19), lang='ko', en='shall', words=['치나니']),
    dict(ref=(33, 3, 19), lang='ko', en='over', words=['인하여']),
    dict(ref=(33, 3, 19), lang='ko', en='for', words=['이는']),
    dict(ref=(33, 3, 19), lang='ko', en='passed', words=['받지']),
    dict(ref=(33, 3, 19), lang='ko', en='upon', words=['받지']),
    dict(ref=(33, 3, 19), lang='ko', en='not', words=['않은']),
    dict(ref=(33, 3, 19), lang='ko', en='whom', words=['자가#2']),
    dict(ref=(33, 3, 19), lang='ko', en='continually', words=['늘']),
    dict(ref=(33, 3, 19), lang='ko', en='that', words=['자가#1']),
    # ---- 하박국 ----
    # 1:2 — cry 가 두 번, thou·wilt·not 도 두 번씩인데 앞 짝만 걸리고 뒤가 비어 있었다.
    # '주께서'가 O 에, '인하여'가 shall 에 걸려 있던 것도 바로잡는다.
    dict(ref=(34, 1, 2), lang='ko', en='cry#1', words=['부르짖어도']),
    dict(ref=(34, 1, 2), lang='ko', en='shall', words=['부르짖어도']),
    dict(ref=(34, 1, 2), lang='ko', en='cry#2', words=['외쳐도']),
    dict(ref=(34, 1, 2), lang='ko', en='out', words=['외쳐도']),
    dict(ref=(34, 1, 2), lang='ko', en='unto', words=['외쳐도']),
    dict(ref=(34, 1, 2), lang='ko', en='thee', words=['외쳐도']),
    dict(ref=(34, 1, 2), lang='ko', en='thou#1', words=['주께서#1']),
    dict(ref=(34, 1, 2), lang='ko', en='thou#2', words=['주께서#2']),
    dict(ref=(34, 1, 2), lang='ko', en='of', words=['인하여']),
    dict(ref=(34, 1, 2), lang='ko', en='save', words=['구원치']),
    dict(ref=(34, 1, 2), lang='ko', en='wilt#2', words=['아니하시나이다']),
    dict(ref=(34, 1, 2), lang='ko', en='not#2', words=['아니하시나이다']),
    dict(ref=(34, 1, 2), lang='ko', en='hear', words=['듣지']),
    dict(ref=(34, 1, 2), lang='ko', en='wilt#1', words=['아니하시니']),
    dict(ref=(34, 1, 2), lang='ko', en='not#1', words=['아니하시니']),
    dict(ref=(34, 1, 2), lang='ko', en='O', words=['여호와여']),
    dict(ref=(34, 1, 2), lang='ko', en='Lord', words=['여호와여']),
    dict(ref=(34, 1, 2), lang='ko', en='how', words=['어느']),
    dict(ref=(34, 1, 2), lang='ko', en='long', words=['때까지리이까']),
    dict(ref=(34, 1, 2), lang='ko', en='I', words=['내가#1']),
    # 2:2 — '너는'이 make 를 받고 '새기되'가 비어 있었다
    dict(ref=(34, 2, 2), lang='ko', en='make', words=['명백히', '새기되']),
    dict(ref=(34, 2, 2), lang='ko', en='plain', words=['새기되']),
    dict(ref=(34, 2, 2), lang='ko', en='may', words=['달려가면서도']),
    dict(ref=(34, 2, 2), lang='ko', en='that#2', words=['읽을']),
    dict(ref=(34, 2, 2), lang='ko', en='it#2', words=['읽을']),
    dict(ref=(34, 2, 2), lang='ko', en='it#1', words=['이']),
    # 하박국 1:3 — '보게 하시며'(shew)와 '목도하게 하시나이까'(cause to behold)가
    # 둘 다 비어 있었다. me 가 세 번, are 가 두 번 나오는 절이다.
    dict(ref=(34, 1, 3), lang='ko', en='shew', words=['보게', '하시며']),
    dict(ref=(34, 1, 3), lang='ko', en='dost', words=['보게']),
    dict(ref=(34, 1, 3), lang='ko', en='thou', words=['보게']),
    dict(ref=(34, 1, 3), lang='ko', en='grievance', words=['패역을']),
    dict(ref=(34, 1, 3), lang='ko', en='behold', words=['목도하게', '하시나이까']),
    dict(ref=(34, 1, 3), lang='ko', en='cause', words=['목도하게']),
    dict(ref=(34, 1, 3), lang='ko', en='to', words=['목도하게']),
    dict(ref=(34, 1, 3), lang='ko', en='me#2', words=['목도하게']),
    dict(ref=(34, 1, 3), lang='ko', en='me#1', words=['나로']),
    dict(ref=(34, 1, 3), lang='ko', en='me#3', words=['내']),
    dict(ref=(34, 1, 3), lang='ko', en='for', words=['대저']),
    dict(ref=(34, 1, 3), lang='ko', en='are#1', words=['있고']),
    dict(ref=(34, 1, 3), lang='ko', en='are#2', words=['일어났나이다']),
    dict(ref=(34, 1, 3), lang='ko', en='there', words=['일어났나이다']),
    dict(ref=(34, 1, 3), lang='ko', en='raise', words=['일어났나이다']),
    dict(ref=(34, 1, 3), lang='ko', en='up', words=['일어났나이다']),
    dict(ref=(34, 1, 3), lang='ko', en='that', words=['일어났나이다']),
    # 하박국 2:6 — '무리가'(복수)가 him(단수)에, 라틴어 super 가 that 에 걸려 있었다.
    # him 이 네 번, against·to·not 이 두 번씩, that 이 세 번, and 가 세 번 나오는 절이라
    # 앞뒤가 통째로 어긋나 있었다. 라틴어도 parabolam/ænigmatum 이 뒤바뀌어 있었다.
    dict(ref=(34, 2, 6), lang='ko', en='these', words=['그', '무리가']),
    dict(ref=(34, 2, 6), lang='ko', en='all', words=['다']),
    dict(ref=(34, 2, 6), lang='ko', en='parable', words=['속담으로']),
    dict(ref=(34, 2, 6), lang='ko', en='against#1', words=['그를#1', '평론하며']),
    dict(ref=(34, 2, 6), lang='ko', en='him#1', words=['그를#1']),
    dict(ref=(34, 2, 6), lang='ko', en='taunting', words=['조롱하는']),
    dict(ref=(34, 2, 6), lang='ko', en='proverb', words=['시로']),
    dict(ref=(34, 2, 6), lang='ko', en='against#2', words=['그를#2', '풍자하지']),
    dict(ref=(34, 2, 6), lang='ko', en='him#2', words=['그를#2']),
    dict(ref=(34, 2, 6), lang='ko', en='Shall', words=['않겠느냐']),
    dict(ref=(34, 2, 6), lang='ko', en='not#1', words=['않겠느냐']),
    dict(ref=(34, 2, 6), lang='ko', en='and#2', words=['곧']),
    dict(ref=(34, 2, 6), lang='ko', en='his', words=['자기', '소유']),
    dict(ref=(34, 2, 6), lang='ko', en='not#2', words=['아닌']),
    dict(ref=(34, 2, 6), lang='ko', en='is', words=['아닌']),
    dict(ref=(34, 2, 6), lang='ko', en='which', words=['것을']),
    dict(ref=(34, 2, 6), lang='ko', en='that#2', words=['것을']),
    dict(ref=(34, 2, 6), lang='ko', en='increaseth', words=['모으는']),
    dict(ref=(34, 2, 6), lang='ko', en='him#3', words=['자여#1']),
    dict(ref=(34, 2, 6), lang='ko', en='to#1', words=['자여#1']),
    dict(ref=(34, 2, 6), lang='ko', en='that#1', words=['자여#1']),
    dict(ref=(34, 2, 6), lang='ko', en='how', words=['언제까지']),
    dict(ref=(34, 2, 6), lang='ko', en='long', words=['언제까지']),
    dict(ref=(34, 2, 6), lang='ko', en='clay', words=['볼모잡은', '것으로']),
    dict(ref=(34, 2, 6), lang='ko', en='with', words=['것으로']),
    dict(ref=(34, 2, 6), lang='ko', en='thick', words=['무겁게']),
    dict(ref=(34, 2, 6), lang='ko', en='ladeth', words=['짐진']),
    dict(ref=(34, 2, 6), lang='ko', en='himself', words=['짐진']),
    dict(ref=(34, 2, 6), lang='ko', en='him#4', words=['자여#2']),
    dict(ref=(34, 2, 6), lang='ko', en='to#2', words=['자여#2']),
    dict(ref=(34, 2, 6), lang='ko', en='that#3', words=['자여#2']),
    dict(ref=(34, 2, 6), lang='ko', en='say', words=['이르기를']),
    dict(ref=(34, 2, 6), lang='ko', en='take', words=['평론하며']),
    dict(ref=(34, 2, 6), lang='ko', en='up', words=['평론하며']),
    # 라틴어
    dict(ref=(34, 2, 6), lang='la', en='Shall', words=['Numquid']),
    dict(ref=(34, 2, 6), lang='la', en='not#1', words=['non#1']),
    dict(ref=(34, 2, 6), lang='la', en='all', words=['omnes']),
    dict(ref=(34, 2, 6), lang='la', en='these', words=['isti']),
    dict(ref=(34, 2, 6), lang='la', en='against#1', words=['super']),
    dict(ref=(34, 2, 6), lang='la', en='him#1', words=['eum']),
    dict(ref=(34, 2, 6), lang='la', en='parable', words=['parabolam']),
    dict(ref=(34, 2, 6), lang='la', en='take', words=['sument']),
    dict(ref=(34, 2, 6), lang='la', en='up', words=['sument']),
    dict(ref=(34, 2, 6), lang='la', en='taunting', words=['ænigmatum']),
    dict(ref=(34, 2, 6), lang='la', en='proverb', words=['loquelam']),
    dict(ref=(34, 2, 6), lang='la', en='him#2', words=['ejus']),
    dict(ref=(34, 2, 6), lang='la', en='and#1', words=['et#1']),
    dict(ref=(34, 2, 6), lang='la', en='and#2', words=['et#2']),
    dict(ref=(34, 2, 6), lang='la', en='and#3', words=['et#3']),
    dict(ref=(34, 2, 6), lang='la', en='say', words=['dicetur']),
    dict(ref=(34, 2, 6), lang='la', en='Woe', words=['Væ']),
    dict(ref=(34, 2, 6), lang='la', en='him#3', words=['ei']),
    dict(ref=(34, 2, 6), lang='la', en='to#1', words=['ei']),
    dict(ref=(34, 2, 6), lang='la', en='that#1', words=['qui']),
    dict(ref=(34, 2, 6), lang='la', en='increaseth', words=['multiplicat']),
    dict(ref=(34, 2, 6), lang='la', en='not#2', words=['non#2']),
    dict(ref=(34, 2, 6), lang='la', en='his', words=['sua']),
    dict(ref=(34, 2, 6), lang='la', en='how', words=['usquequo']),
    dict(ref=(34, 2, 6), lang='la', en='long', words=['usquequo']),
    dict(ref=(34, 2, 6), lang='la', en='ladeth', words=['aggravat']),
    dict(ref=(34, 2, 6), lang='la', en='with', words=['contra']),
    dict(ref=(34, 2, 6), lang='la', en='himself', words=['se']),
    dict(ref=(34, 2, 6), lang='la', en='thick', words=['densum']),
    dict(ref=(34, 2, 6), lang='la', en='clay', words=['lutum']),

    # 하박국 2장 — 사용자 교정
    dict(ref=(34, 2, 5), lang='ko', en='unto#1', words=['자기에게로']),
    dict(ref=(34, 2, 5), lang='ko', en='him#1', words=['자기에게로']),
    dict(ref=(34, 2, 5), lang='ko', en='his', words=['그']),
    dict(ref=(34, 2, 7), lang='ko', en='rise', words=['일어나지']),
    dict(ref=(34, 2, 7), lang='ko', en='up', words=['일어나지']),
    dict(ref=(34, 2, 8), lang='ko', en='all#1', words=['모든#1']),
    dict(ref=(34, 2, 8), lang='ko', en='all#2', words=['모든#2']),
    dict(ref=(34, 2, 8), lang='ko', en='shall#1', words=[]),
    dict(ref=(34, 2, 9), lang='ko', en='set', words=['깃들이려']),
    dict(ref=(34, 2, 9), lang='ko', en='nest', words=['깃들이려']),
    dict(ref=(34, 2, 10), lang='ko', en='Thou', words=['네가']),
    dict(ref=(34, 2, 10), lang='ko', en='cutting', words=['멸한']),
    dict(ref=(34, 2, 10), lang='ko', en='off', words=['멸한']),
    dict(ref=(34, 2, 10), lang='ko', en='thy#1', words=['네#1']),
    dict(ref=(34, 2, 10), lang='ko', en='thy#2', words=['네#2']),
    dict(ref=(34, 2, 12), lang='ko', en='buildeth', words=['건설하며']),
    dict(ref=(34, 2, 12), lang='ko', en='town', words=['읍을']),
    dict(ref=(34, 2, 12), lang='ko', en='stablisheth', words=['건축하는']),
    dict(ref=(34, 2, 13), lang='ko', en='of#1', words=['여호와께로서']),
    dict(ref=(34, 2, 13), lang='ko', en='Lord', words=['여호와께로서']),
    dict(ref=(34, 2, 13), lang='ko', en='of#2', words=['만군의']),
    dict(ref=(34, 2, 13), lang='ko', en='hosts', words=['만군의']),
    dict(ref=(34, 2, 13), lang='ko', en='shall#1', words=[]),
    dict(ref=(34, 2, 13), lang='ko', en='shall#2', words=[]),
    dict(ref=(34, 2, 14), lang='ko', en='knowledge', words=['인정하는', '것이']),
    dict(ref=(34, 2, 14), lang='ko', en='shall', words=[]),
    dict(ref=(34, 2, 16), lang='ko', en='filled', words=['가득한즉']),
    dict(ref=(34, 2, 16), lang='ko', en='with', words=['가득한즉']),
    dict(ref=(34, 2, 16), lang='ko', en='the#2', words=['여호와의']),
    dict(ref=(34, 2, 16), lang='ko', en='Lord', words=['여호와의']),
    dict(ref=(34, 2, 16), lang='ko', en='unto', words=['네게로']),
    dict(ref=(34, 2, 16), lang='ko', en='thee', words=['네게로']),
    dict(ref=(34, 2, 16), lang='ko', en='shameful', words=['더러운']),
    dict(ref=(34, 2, 16), lang='ko', en='thou#1', words=['너도']),
    # '할례 아니한 것을'은 할례받지 않은 상태를 가리키는 한 덩어리다.
    # '할례'에만 붙이면 뜻이 정반대가 된다.
    dict(ref=(34, 2, 16), lang='ko', en='foreskin', words=['할례', '아니한', '것을']),
    dict(ref=(34, 2, 16), lang='ko', en='spewing', words=['욕이']),
    dict(ref=(34, 2, 16), lang='ko', en='thy#2', words=['네']),
    dict(ref=(34, 2, 16), lang='ko', en='glory#2', words=['영광을']),
    dict(ref=(34, 2, 16), lang='la', en='thou', words=['tu']),
    dict(ref=(34, 2, 16), lang='la', en='Lord', words=['Domini']),
    dict(ref=(34, 2, 16), lang='la', en='let', words=['consopire']),
    dict(ref=(34, 2, 16), lang='la', en='foreskin', words=['consopire']),
    dict(ref=(34, 2, 16), lang='la', en='be#1', words=['consopire']),
    dict(ref=(34, 2, 16), lang='la', en='uncovered', words=['consopire']),
    dict(ref=(34, 2, 16), lang='la', en='spewing', words=['vomitus']),
    dict(ref=(34, 2, 16), lang='la', en='shameful', words=['ignominiæ']),
    dict(ref=(34, 2, 16), lang='la', en='on', words=['super']),
    dict(ref=(34, 2, 16), lang='ko', en='Thou', words=['네게']),
    dict(ref=(34, 2, 16), lang='ko', en='for', words=['아니요']),
    dict(ref=(34, 2, 16), lang='ko', en='thy#1', words=['너의']),
    dict(ref=(34, 2, 16), lang='ko', en='be#3', words=['가리우리라']),
    dict(ref=(34, 2, 16), lang='la', en='thy#1', words=[]),
    dict(ref=(34, 2, 16), lang='la', en='shame', words=['ignominia']),
    dict(ref=(34, 2, 16), lang='la', en='the#1', words=['calix']),
    dict(ref=(34, 2, 16), lang='la', en='the#2', words=['Domini']),
    dict(ref=(34, 2, 5), lang='ko', en='he#1', words=['그는#1']),
    dict(ref=(34, 2, 5), lang='ko', en='transgresseth', words=['궤휼하며']),
    dict(ref=(34, 2, 5), lang='ko', en='by', words=['술을']),
    dict(ref=(34, 2, 5), lang='ko', en='wine', words=['술을', '즐기며']),
    dict(ref=(34, 2, 5), lang='ko', en='he#2', words=['그는#2']),
    dict(ref=(34, 2, 5), lang='ko', en='neither', words=['아니하고']),
    dict(ref=(34, 2, 5), lang='ko', en='at', words=['가만히', '있지']),
    dict(ref=(34, 2, 5), lang='ko', en='home', words=['가만히', '있지']),
    dict(ref=(34, 2, 5), lang='ko', en='who', words=['아니하고']),
    dict(ref=(34, 2, 5), lang='ko', en='desire', words=['욕심을']),
    dict(ref=(34, 2, 5), lang='ko', en='as#1', words=['음부처럼']),
    dict(ref=(34, 2, 5), lang='ko', en='as#2', words=['같아서']),
    dict(ref=(34, 2, 5), lang='ko', en='cannot', words=['줄을', '모르고']),
    dict(ref=(34, 2, 5), lang='ko', en='be', words=['줄을', '모르고']),
    dict(ref=(34, 2, 5), lang='ko', en='satisfied', words=['족한']),
    dict(ref=(34, 2, 5), lang='ko', en='all#1', words=['만국을']),
    dict(ref=(34, 2, 5), lang='ko', en='nations', words=['만국을']),
    dict(ref=(34, 2, 5), lang='ko', en='all#2', words=['만민을']),
    dict(ref=(34, 2, 5), lang='ko', en='people', words=['만민을']),
    dict(ref=(34, 2, 5), lang='ko', en='heapeth', words=['모으나니']),

    dict(ref=(34, 2, 8), lang='ko', en='of#1', words=['그#1', '모든#1', '민족의']),
    dict(ref=(34, 2, 8), lang='ko', en='people', words=['민족의']),
    dict(ref=(34, 2, 8), lang='ko', en='remnant', words=['남은', '자가']),
    dict(ref=(34, 2, 8), lang='ko', en='spoil', words=['노략하리니']),
    dict(ref=(34, 2, 8), lang='ko', en='thee', words=['너를']),
    dict(ref=(34, 2, 8), lang='ko', en='therein', words=['그#2', '안의']),
    dict(ref=(34, 2, 8), lang='ko', en='because', words=['이는']),
    dict(ref=(34, 2, 8), lang='ko', en='for', words=[]),

    dict(ref=(34, 2, 13), lang='ko', en='in', words=['불탈']),
    dict(ref=(34, 2, 13), lang='ko', en='the#3', words=['불탈']),
    dict(ref=(34, 2, 13), lang='ko', en='very#1', words=['불탈']),
    dict(ref=(34, 2, 13), lang='ko', en='fire', words=['불탈']),
    dict(ref=(34, 2, 13), lang='ko', en='the#4', words=['열국이']),
    dict(ref=(34, 2, 13), lang='ko', en='people#2', words=['열국이']),
    dict(ref=(34, 2, 13), lang='ko', en='very#2', words=['헛된']),
    dict(ref=(34, 2, 13), lang='ko', en='for', words=['일로']),
    dict(ref=(34, 2, 13), lang='ko', en='is', words=['말미암음이']),

    dict(ref=(34, 2, 17), lang='ko', en='spoil', words=['잔해한']),
    dict(ref=(34, 2, 17), lang='ko', en='For', words=['대저']),
    dict(ref=(34, 2, 17), lang='ko', en='cover', words=['돌아오리라']),
    # 2:1 은 개역한글이 의역한 데가 많아 낱말이 일대일로 맞지 않는다.
    # 분명한 것만 잇고 나머지는 비워 둔다.
    dict(ref=(34, 2, 1), lang='ko', en='I#1', words=['내가']),
    dict(ref=(34, 2, 1), lang='ko', en='my', words=['내']),
    dict(ref=(34, 2, 1), lang='ko', en='watch#1', words=['파수하는', '곳에']),
    dict(ref=(34, 2, 1), lang='ko', en='upon#1', words=['곳에']),
    dict(ref=(34, 2, 1), lang='ko', en='stand', words=['서며', '서리라']),
    dict(ref=(34, 2, 1), lang='ko', en='upon#2', words=['성루에']),
    dict(ref=(34, 2, 1), lang='ko', en='tower', words=['성루에']),
    dict(ref=(34, 2, 1), lang='ko', en='watch#2', words=['기다리고']),
    dict(ref=(34, 2, 1), lang='ko', en='see', words=['바라보며']),
    dict(ref=(34, 2, 1), lang='ko', en='what#2', words=['어떻게']),
    dict(ref=(34, 2, 1), lang='ko', en='I#3', words=['나의']),
    # 히브리어 תּוֹכַחְתִּי 를 KJV 는 'reproved', 개역한글은 '나의 질문'으로 읽었다.
    dict(ref=(34, 2, 1), lang='ko', en='reproved', words=['질문에', '대하여']),

    # ---- 이사야 53장 ----
    dict(ref=(22, 53, 1), lang='ko', en='our', words=['우리의']),
    dict(ref=(22, 53, 1), lang='ko', en='report', words=['전한', '것을']),
    dict(ref=(22, 53, 1), lang='ko', en='is', words=[]),
    dict(ref=(22, 53, 1), lang='ko', en='to', words=['뉘게']),
    dict(ref=(22, 53, 1), lang='ko', en='whom', words=['뉘게']),
    dict(ref=(22, 53, 1), lang='ko', en='of', words=['여호와의']),
    dict(ref=(22, 53, 1), lang='ko', en='the#2', words=['여호와의']),

    dict(ref=(22, 53, 4), lang='ko', en='yet', words=[]),
    dict(ref=(22, 53, 4), lang='ko', en='our#1', words=['우리의#1']),
    dict(ref=(22, 53, 4), lang='ko', en='griefs', words=['질고를']),
    dict(ref=(22, 53, 4), lang='ko', en='carried', words=['당하였거늘']),
    dict(ref=(22, 53, 4), lang='ko', en='our#2', words=['우리의#2']),
    dict(ref=(22, 53, 4), lang='ko', en='sorrows', words=['슬픔을']),
    dict(ref=(22, 53, 4), lang='ko', en='we', words=['우리는']),
    dict(ref=(22, 53, 4), lang='ko', en='him', words=['그는#2']),
    dict(ref=(22, 53, 4), lang='ko', en='stricken', words=['징벌을', '받아서']),
    dict(ref=(22, 53, 4), lang='ko', en='smitten', words=['맞으며']),
    dict(ref=(22, 53, 4), lang='ko', en='afflicted', words=['고난을', '당한다']),

    dict(ref=(22, 53, 5), lang='ko', en='But', words=[]),
    dict(ref=(22, 53, 5), lang='ko', en='he#1', words=['그가#1']),
    dict(ref=(22, 53, 5), lang='ko', en='was#1', words=[]),
    dict(ref=(22, 53, 5), lang='ko', en='wounded', words=['찔림은']),
    dict(ref=(22, 53, 5), lang='ko', en='for#1', words=['인함이요']),
    dict(ref=(22, 53, 5), lang='ko', en='our#1', words=['우리의#1']),
    dict(ref=(22, 53, 5), lang='ko', en='he#2', words=['그가#2']),
    dict(ref=(22, 53, 5), lang='ko', en='was#2', words=[]),
    dict(ref=(22, 53, 5), lang='ko', en='bruised', words=['상함은']),
    dict(ref=(22, 53, 5), lang='ko', en='for#2', words=['인함이라']),
    dict(ref=(22, 53, 5), lang='ko', en='our#2', words=['우리의#2']),
    dict(ref=(22, 53, 5), lang='ko', en='our#3', words=['우리가#1']),
    dict(ref=(22, 53, 5), lang='ko', en='was#3', words=[]),
    dict(ref=(22, 53, 5), lang='ko', en='upon', words=['받음으로']),
    dict(ref=(22, 53, 5), lang='ko', en='him', words=['그가#3', '받음으로']),
    dict(ref=(22, 53, 5), lang='ko', en='with', words=['맞음으로']),
    dict(ref=(22, 53, 5), lang='ko', en='his', words=['그가#4']),
    dict(ref=(22, 53, 5), lang='ko', en='we', words=['우리가#2']),
    dict(ref=(22, 53, 5), lang='ko', en='are', words=['입었도다']),
    dict(ref=(22, 53, 5), lang='ko', en='healed', words=['나음을', '입었도다']),

    dict(ref=(22, 53, 6), lang='ko', en='own', words=['제']),
    dict(ref=(22, 53, 6), lang='ko', en='turned', words=['갔거늘']),
    dict(ref=(22, 53, 6), lang='ko', en='us', words=['우리']),
    dict(ref=(22, 53, 6), lang='ko', en='all', words=['무리의']),
    dict(ref=(22, 53, 6), lang='ko', en='laid', words=['담당시키셨도다']),

    dict(ref=(22, 53, 8), lang='ko', en='declare', words=['생각하기를']),
    dict(ref=(22, 53, 8), lang='ko', en='taken', words=['끌려', '갔으니']),
    dict(ref=(22, 53, 8), lang='ko', en='prison', words=['곤욕과']),
    dict(ref=(22, 53, 8), lang='ko', en='judgment', words=['심문을']),
    dict(ref=(22, 53, 8), lang='ko', en='he#2', words=['그가#2']),
    dict(ref=(22, 53, 8), lang='ko', en='stricken', words=['마땅히', '형벌', '받을']),
    dict(ref=(22, 53, 8), lang='ko', en='who', words=['누가', '하였으리요']),

    dict(ref=(22, 53, 10), lang='ko', en='him#1', words=['그로']),
    dict(ref=(22, 53, 10), lang='ko', en='bruise', words=['상함을', '받게']),
    dict(ref=(22, 53, 8), lang='ko', en='generation', words=['세대', '중에']),
    dict(ref=(22, 53, 8), lang='ko', en='for#2', words=['인함이라']),
    dict(ref=(22, 53, 8), lang='ko', en='living', words=['산', '자의']),
    dict(ref=(22, 53, 8), lang='ko', en='was#1', words=['당하고']),
    dict(ref=(22, 53, 10), lang='ko', en='put', words=['당케', '하셨은즉']),
    dict(ref=(22, 53, 10), lang='ko', en='when', words=['이르면']),
    dict(ref=(22, 53, 10), lang='ko', en='his#1', words=['그#1']),
    dict(ref=(22, 53, 10), lang='ko', en='he#2', words=['그가']),
    dict(ref=(22, 53, 10), lang='ko', en='his#2', words=['그#2']),
    dict(ref=(22, 53, 10), lang='ko', en='his#3', words=['그#3']),
    dict(ref=(22, 53, 10), lang='ko', en='prolong', words=['길']),
    dict(ref=(22, 53, 10), lang='ko', en='and', words=['또']),
    dict(ref=(22, 53, 10), lang='ko', en='his#4', words=['그의']),
    dict(ref=(22, 53, 10), lang='ko', en='prosper', words=['성취하리로다']),

    dict(ref=(22, 53, 12), lang='ko', en='him', words=['그로']),
    dict(ref=(22, 53, 12), lang='ko', en='divide#1', words=['얻게', '하며#1']),
    dict(ref=(22, 53, 12), lang='ko', en='portion', words=['분깃을']),
    dict(ref=(22, 53, 12), lang='ko', en='with#1', words=['함께#1']),
    dict(ref=(22, 53, 12), lang='ko', en='the#1', words=['존귀한']),
    dict(ref=(22, 53, 12), lang='ko', en='great', words=['존귀한', '자와#1']),
    dict(ref=(22, 53, 12), lang='ko', en='divide#2', words=['나누게']),
    dict(ref=(22, 53, 12), lang='ko', en='the#2', words=['탈취한']),
    dict(ref=(22, 53, 12), lang='ko', en='spoil', words=['탈취한', '것을']),
    dict(ref=(22, 53, 12), lang='ko', en='with#2', words=['함께#2']),
    dict(ref=(22, 53, 12), lang='ko', en='the#3', words=['강한']),
    dict(ref=(22, 53, 12), lang='ko', en='strong', words=['강한', '자와#2']),
    dict(ref=(22, 53, 12), lang='ko', en='because', words=['이는']),
    dict(ref=(22, 53, 12), lang='ko', en='he#2', words=['그가#1']),
    dict(ref=(22, 53, 12), lang='ko', en='poured', words=['버려']),
    dict(ref=(22, 53, 12), lang='ko', en='out', words=['버려']),
    dict(ref=(22, 53, 12), lang='ko', en='his', words=['자기']),
    dict(ref=(22, 53, 12), lang='ko', en='soul', words=['영혼을']),
    dict(ref=(22, 53, 12), lang='ko', en='unto', words=['이르게', '하며#2']),
    dict(ref=(22, 53, 12), lang='ko', en='death', words=['사망에']),
    dict(ref=(22, 53, 12), lang='ko', en='he#3', words=['하나로']),
    dict(ref=(22, 53, 12), lang='ko', en='was', words=['헤아림을', '입었음이라']),
    dict(ref=(22, 53, 12), lang='ko', en='numbered', words=['헤아림을', '입었음이라']),
    dict(ref=(22, 53, 12), lang='ko', en='with#3', words=['중']),
    dict(ref=(22, 53, 12), lang='ko', en='the#4', words=['범죄자']),
    dict(ref=(22, 53, 12), lang='ko', en='transgressors#1', words=['범죄자', '중']),
    dict(ref=(22, 53, 12), lang='ko', en='he#4', words=['그가#2']),
    dict(ref=(22, 53, 12), lang='ko', en='bare', words=['지며']),
    dict(ref=(22, 53, 12), lang='ko', en='the#5', words=['죄를']),
    dict(ref=(22, 53, 12), lang='ko', en='sin', words=['죄를']),
    dict(ref=(22, 53, 12), lang='ko', en='of', words=['사람의']),
    dict(ref=(22, 53, 12), lang='ko', en='many', words=['많은']),
    dict(ref=(22, 53, 12), lang='ko', en='made', words=['기도하였느니라']),
    dict(ref=(22, 53, 12), lang='ko', en='intercession', words=['기도하였느니라']),
    dict(ref=(22, 53, 12), lang='ko', en='for', words=['위하여']),
    dict(ref=(22, 53, 12), lang='ko', en='the#6', words=['범죄자를']),
    dict(ref=(22, 53, 12), lang='ko', en='transgressors#2', words=['범죄자를']),

    # ---- 역대상 16장 (16:12-13 묶인 절) ----
    dict(ref=(12, 16, 12), lang='ko', en='Remember', words=['기억할지어다']),
    dict(ref=(12, 16, 12), lang='ko', en='his#1', words=['그#2']),
    dict(ref=(12, 16, 12), lang='ko', en='marvellous', words=['기사와']),
    dict(ref=(12, 16, 12), lang='ko', en='works', words=['기사와']),
    dict(ref=(12, 16, 12), lang='ko', en='that', words=['행하신']),
    dict(ref=(12, 16, 12), lang='ko', en='he', words=['행하신']),
    dict(ref=(12, 16, 12), lang='ko', en='hath', words=['행하신']),
    dict(ref=(12, 16, 12), lang='ko', en='done', words=['행하신']),
    dict(ref=(12, 16, 12), lang='ko', en='his#2', words=['그#3']),
    dict(ref=(12, 16, 12), lang='ko', en='wonders', words=['이적과']),
    dict(ref=(12, 16, 12), lang='ko', en='judgments', words=['판단을']),
    dict(ref=(12, 16, 12), lang='ko', en='of#1', words=['입의']),
    dict(ref=(12, 16, 12), lang='ko', en='his#3', words=['그#4']),
    dict(ref=(12, 16, 12), lang='ko', en='mouth', words=['입의']),
    dict(ref=(12, 16, 12), lang='ko', en='O', words=['곧']),
    dict(ref=(12, 16, 12), lang='ko', en='ye#1', words=['너희는']),
    dict(ref=(12, 16, 12), lang='ko', en='ye#2', words=['너희는']),
    dict(ref=(12, 16, 12), lang='ko', en='seed', words=['후손']),
    dict(ref=(12, 16, 12), lang='ko', en='of#2', words=['이스라엘의']),
    dict(ref=(12, 16, 12), lang='ko', en='Israel', words=['이스라엘의']),
    dict(ref=(12, 16, 12), lang='ko', en='his#4', words=['그#1']),
    dict(ref=(12, 16, 12), lang='ko', en='servant', words=['종']),
    dict(ref=(12, 16, 12), lang='ko', en='children', words=['자손']),
    dict(ref=(12, 16, 12), lang='ko', en='of#3', words=['야곱의']),
    dict(ref=(12, 16, 12), lang='ko', en='Jacob', words=['야곱의']),
    dict(ref=(12, 16, 12), lang='ko', en='his#5', words=['택하신']),
    dict(ref=(12, 16, 12), lang='ko', en='chosen', words=['택하신']),
    dict(ref=(12, 16, 12), lang='ko', en='ones', words=['자손']),

    # ---- 욥기 31장 (31:33-34 묶인 절) ----
    dict(ref=(17, 31, 33), lang='ko', en='If', words=['가리었었던가']),
    dict(ref=(17, 31, 33), lang='ko', en='I#1', words=['가리었었던가']),
    dict(ref=(17, 31, 33), lang='ko', en='covered', words=['가리었었던가']),
    dict(ref=(17, 31, 33), lang='ko', en='my#1', words=['허물을']),
    dict(ref=(17, 31, 33), lang='ko', en='transgressions', words=['허물을']),
    dict(ref=(17, 31, 33), lang='ko', en='as', words=['타인처럼']),
    dict(ref=(17, 31, 33), lang='ko', en='Adam', words=['타인처럼']),
    dict(ref=(17, 31, 33), lang='ko', en='by', words=['숨겨']),
    dict(ref=(17, 31, 33), lang='ko', en='hiding', words=['숨겨']),
    dict(ref=(17, 31, 33), lang='ko', en='mine', words=['죄악을']),
    dict(ref=(17, 31, 33), lang='ko', en='iniquity', words=['죄악을']),
    dict(ref=(17, 31, 33), lang='ko', en='in', words=['품에']),
    dict(ref=(17, 31, 33), lang='ko', en='my#2', words=['내']),
    dict(ref=(17, 31, 33), lang='ko', en='bosom', words=['품에']),
    dict(ref=(17, 31, 33), lang='ko', en='Did', words=['언제']),
    dict(ref=(17, 31, 33), lang='ko', en='I#2', words=['내가']),
    dict(ref=(17, 31, 33), lang='ko', en='fear', words=['두려워하며']),
    dict(ref=(17, 31, 33), lang='ko', en='a', words=['큰']),
    dict(ref=(17, 31, 33), lang='ko', en='great', words=['큰']),
    dict(ref=(17, 31, 33), lang='ko', en='multitude', words=['무리를']),
    dict(ref=(17, 31, 33), lang='ko', en='or', words=[]),
    dict(ref=(17, 31, 33), lang='ko', en='did', words=['무서워함으로']),
    dict(ref=(17, 31, 33), lang='ko', en='contempt', words=['멸시를']),
    dict(ref=(17, 31, 33), lang='ko', en='of#1', words=['족속의']),
    dict(ref=(17, 31, 33), lang='ko', en='families', words=['족속의']),
    dict(ref=(17, 31, 33), lang='ko', en='terrify', words=['무서워함으로']),
    dict(ref=(17, 31, 33), lang='ko', en='me', words=['무서워함으로']),
    dict(ref=(17, 31, 33), lang='ko', en='that', words=['잠잠하고']),
    dict(ref=(17, 31, 33), lang='ko', en='I#3', words=['잠잠하고']),
    dict(ref=(17, 31, 33), lang='ko', en='kept', words=['잠잠하고']),
    dict(ref=(17, 31, 33), lang='ko', en='silence', words=['잠잠하고']),
    dict(ref=(17, 31, 33), lang='ko', en='and', words=[]),
    dict(ref=(17, 31, 33), lang='ko', en='went', words=['나가지']),
    dict(ref=(17, 31, 33), lang='ko', en='not', words=['아니하여']),
    dict(ref=(17, 31, 33), lang='ko', en='out', words=['나가지']),
    dict(ref=(17, 31, 33), lang='ko', en='of#2', words=['나가지']),
    dict(ref=(17, 31, 33), lang='ko', en='the#2', words=['문에']),
    dict(ref=(17, 31, 33), lang='ko', en='door', words=['문에']),

    # ---- 욥기 35장 ----
    dict(ref=(17, 35, 1), lang='ko', en='moreover', words=['이어']),

    dict(ref=(17, 35, 2), lang='ko', en='Thinkest', words=['여기느냐']),
    dict(ref=(17, 35, 2), lang='ko', en='thou#1', words=['네가#1']),
    dict(ref=(17, 35, 2), lang='ko', en='to', words=[]),
    dict(ref=(17, 35, 2), lang='ko', en='be', words=['합리하게']),
    dict(ref=(17, 35, 2), lang='ko', en='right', words=['합리하게']),
    dict(ref=(17, 35, 2), lang='ko', en='that', words=['네']),
    dict(ref=(17, 35, 2), lang='ko', en='thou#2', words=['네가#2']),
    dict(ref=(17, 35, 2), lang='ko', en='saidst', words=['생각에']),
    dict(ref=(17, 35, 2), lang='ko', en='is', words=['하나님보다']),
    dict(ref=(17, 35, 2), lang='ko', en='more', words=['하나님보다']),
    dict(ref=(17, 35, 2), lang='ko', en='than', words=['하나님보다']),

    dict(ref=(17, 35, 3), lang='ko', en='and', words=[]),
    dict(ref=(17, 35, 3), lang='ko', en='What#1', words=['무엇인고#1']),
    dict(ref=(17, 35, 3), lang='ko', en='advantage', words=['유익이']),
    dict(ref=(17, 35, 3), lang='ko', en='will', words=['무엇인고#1']),
    dict(ref=(17, 35, 3), lang='ko', en='it', words=['무엇인고#1']),
    dict(ref=(17, 35, 3), lang='ko', en='be#1', words=['무엇인고#1']),
    dict(ref=(17, 35, 3), lang='ko', en='What#2', words=['무엇인고#2']),
    dict(ref=(17, 35, 3), lang='ko', en='profit', words=['이익이']),
    dict(ref=(17, 35, 3), lang='ko', en='shall', words=['무엇인고#2']),
    dict(ref=(17, 35, 3), lang='ko', en='I#1', words=['내게']),
    dict(ref=(17, 35, 3), lang='ko', en='have', words=['내게']),
    dict(ref=(17, 35, 3), lang='ko', en='if', words=['것보다']),
    dict(ref=(17, 35, 3), lang='ko', en='from', words=['것보다']),
    dict(ref=(17, 35, 3), lang='ko', en='I#2', words=['범죄한']),
    dict(ref=(17, 35, 3), lang='ko', en='be#2', words=['범죄한']),
    dict(ref=(17, 35, 3), lang='ko', en='cleansed', words=['범죄한']),
    dict(ref=(17, 35, 3), lang='ko', en='my', words=['범죄한']),

    dict(ref=(17, 35, 5), lang='ko', en='Look', words=['우러러', '보라']),
    dict(ref=(17, 35, 5), lang='ko', en='unto', words=['우러러', '보라']),
    dict(ref=(17, 35, 5), lang='ko', en='see', words=['보라']),
    dict(ref=(17, 35, 5), lang='ko', en='behold', words=['바라보라']),
    dict(ref=(17, 35, 5), lang='ko', en='which', words=['높은']),
    dict(ref=(17, 35, 5), lang='ko', en='than', words=['위의']),

    dict(ref=(17, 35, 6), lang='ko', en='thou#1', words=['네가']),
    dict(ref=(17, 35, 6), lang='ko', en='thy', words=['네']),
    dict(ref=(17, 35, 6), lang='ko', en='or', words=[]),
    dict(ref=(17, 35, 6), lang='ko', en='what#1', words=['무슨#1']),
    dict(ref=(17, 35, 6), lang='ko', en='doest#1', words=['영향이', '있겠으며#1']),
    dict(ref=(17, 35, 6), lang='ko', en='against', words=['하나님께#1']),
    dict(ref=(17, 35, 6), lang='ko', en='him#1', words=['하나님께#1']),
    dict(ref=(17, 35, 6), lang='ko', en='be', words=['관영한들']),
    dict(ref=(17, 35, 6), lang='ko', en='multiplied', words=['관영한들']),
    dict(ref=(17, 35, 6), lang='ko', en='what#2', words=['무슨#2']),
    dict(ref=(17, 35, 6), lang='ko', en='doest#2', words=['관계가', '있겠으며#2']),
    dict(ref=(17, 35, 6), lang='ko', en='unto', words=['하나님께#2']),
    dict(ref=(17, 35, 6), lang='ko', en='him#2', words=['하나님께#2']),

    dict(ref=(17, 35, 7), lang='ko', en='thou#1', words=['네가']),
    dict(ref=(17, 35, 7), lang='ko', en='be', words=[]),
    dict(ref=(17, 35, 7), lang='ko', en='righteous', words=['의로운들']),
    dict(ref=(17, 35, 7), lang='ko', en='what#1', words=['무엇을#1']),
    dict(ref=(17, 35, 7), lang='ko', en='givest', words=['드리겠으며']),
    dict(ref=(17, 35, 7), lang='ko', en='thou#2', words=['드리겠으며']),
    dict(ref=(17, 35, 7), lang='ko', en='him', words=['하나님께']),
    dict(ref=(17, 35, 7), lang='ko', en='or', words=[]),
    dict(ref=(17, 35, 7), lang='ko', en='what#2', words=['무엇을#2']),
    dict(ref=(17, 35, 7), lang='ko', en='he', words=['그가']),
    dict(ref=(17, 35, 7), lang='ko', en='of', words=['손에서']),
    dict(ref=(17, 35, 7), lang='ko', en='thine', words=['네']),

    dict(ref=(17, 35, 9), lang='ko', en='By', words=['많으므로']),
    dict(ref=(17, 35, 9), lang='ko', en='reason#1', words=['많으므로']),
    dict(ref=(17, 35, 9), lang='ko', en='of#1', words=['많으므로']),
    dict(ref=(17, 35, 9), lang='ko', en='multitude', words=['많으므로']),
    dict(ref=(17, 35, 9), lang='ko', en='of#2', words=['많으므로']),
    dict(ref=(17, 35, 9), lang='ko', en='they#1', words=['사람은']),
    dict(ref=(17, 35, 9), lang='ko', en='they#2', words=['사람은']),
    dict(ref=(17, 35, 9), lang='ko', en='make', words=['부르짖으며']),
    dict(ref=(17, 35, 9), lang='ko', en='to', words=['부르짖으며']),
    dict(ref=(17, 35, 9), lang='ko', en='cry#1', words=['부르짖으며']),
    dict(ref=(17, 35, 9), lang='ko', en='cry#2', words=['부르짖으나']),
    dict(ref=(17, 35, 9), lang='ko', en='out', words=['부르짖으나']),
    dict(ref=(17, 35, 9), lang='ko', en='by', words=['눌리므로']),
    dict(ref=(17, 35, 9), lang='ko', en='reason#2', words=['눌리므로']),
    dict(ref=(17, 35, 9), lang='ko', en='of#3', words=['눌리므로']),
    dict(ref=(17, 35, 9), lang='ko', en='of#4', words=['자의']),
    dict(ref=(17, 35, 9), lang='ko', en='mighty', words=['세력', '있는']),

    # 35:10-11 — tools/fix_bridge.py 로 두 절을 한 줄로 묶은 뒤의 번호
    dict(ref=(17, 35, 10), lang='ko', en='none', words=['자가', '한', '사람도', '없구나']),
    dict(ref=(17, 35, 10), lang='ko', en='who', words=['하시며#1']),
    dict(ref=(17, 35, 10), lang='ko', en='giveth', words=['노래하게', '하시며#1']),
    dict(ref=(17, 35, 10), lang='ko', en='in', words=['밤중에']),
    dict(ref=(17, 35, 10), lang='ko', en='the#1', words=['밤중에']),
    dict(ref=(17, 35, 10), lang='ko', en='Who', words=['하시며#2']),
    dict(ref=(17, 35, 10), lang='ko', en='teacheth', words=['교육하시기를']),
    dict(ref=(17, 35, 10), lang='ko', en='us#1', words=['우리를']),
    dict(ref=(17, 35, 10), lang='ko', en='more', words=['더하게']),
    dict(ref=(17, 35, 10), lang='ko', en='than#1', words=['하심보다']),
    dict(ref=(17, 35, 10), lang='ko', en='the#2', words=['짐승에게']),
    dict(ref=(17, 35, 10), lang='ko', en='beasts', words=['짐승에게']),
    dict(ref=(17, 35, 10), lang='ko', en='of#1', words=['땅의']),
    dict(ref=(17, 35, 10), lang='ko', en='earth', words=['땅의']),
    dict(ref=(17, 35, 10), lang='ko', en='maketh', words=['더하시는']),
    dict(ref=(17, 35, 10), lang='ko', en='us#2', words=['우리에게']),
    dict(ref=(17, 35, 10), lang='ko', en='wiser', words=['지혜', '주시기를']),
    dict(ref=(17, 35, 10), lang='ko', en='than#2', words=['주심보다']),
    dict(ref=(17, 35, 10), lang='ko', en='fowls', words=['새에게']),
    dict(ref=(17, 35, 10), lang='ko', en='of#2', words=['공중의']),
    dict(ref=(17, 35, 10), lang='ko', en='heaven', words=['공중의']),

    dict(ref=(17, 35, 12), lang='ko', en='giveth', words=['응락하는']),
    dict(ref=(17, 35, 12), lang='ko', en='answer', words=['응락하는']),
    dict(ref=(17, 35, 12), lang='ko', en='evil', words=['악인의']),
    dict(ref=(17, 35, 12), lang='ko', en='men', words=['악인의']),

    dict(ref=(17, 35, 13), lang='ko', en='Surely', words=['결코']),
    dict(ref=(17, 35, 13), lang='ko', en='will#1', words=['아니하시며']),
    dict(ref=(17, 35, 13), lang='ko', en='not', words=['아니하시며']),
    dict(ref=(17, 35, 13), lang='ko', en='hear', words=['듣지']),
    dict(ref=(17, 35, 13), lang='ko', en='vanity', words=['헛된', '부르짖음은']),
    dict(ref=(17, 35, 13), lang='ko', en='neither', words=['아니']),
    dict(ref=(17, 35, 13), lang='ko', en='will#2', words=['아니']),

    dict(ref=(17, 35, 14), lang='ko', en='Although', words=['하물며']),
    dict(ref=(17, 35, 14), lang='ko', en='thou#1', words=['너랴']),
    dict(ref=(17, 35, 14), lang='ko', en='sayest', words=['말하기를']),
    dict(ref=(17, 35, 14), lang='ko', en='thou#2', words=['너랴']),
    dict(ref=(17, 35, 14), lang='ko', en='shalt', words=['수']),
    dict(ref=(17, 35, 14), lang='ko', en='see', words=['뵈올']),
    dict(ref=(17, 35, 14), lang='ko', en='him#1', words=['하나님은']),
    dict(ref=(17, 35, 14), lang='ko', en='yet', words=['일의']),
    dict(ref=(17, 35, 14), lang='ko', en='judgment', words=['시비는']),
    dict(ref=(17, 35, 14), lang='ko', en='him#2', words=['그']),
    dict(ref=(17, 35, 14), lang='ko', en='therefore', words=['뿐이라']),
    dict(ref=(17, 35, 14), lang='ko', en='trust', words=['기다릴']),
    dict(ref=(17, 35, 14), lang='ko', en='thou#3', words=['나는']),
    dict(ref=(17, 35, 14), lang='ko', en='in', words=['그를']),
    dict(ref=(17, 35, 14), lang='ko', en='him#3', words=['그를']),

    # ---- 요한복음 1장 ----
    dict(ref=(42, 1, 1), lang='ko', en='the#1', words=['태초에']),
    dict(ref=(42, 1, 1), lang='ko', en='In', words=['태초에']),
    dict(ref=(42, 1, 1), lang='ko', en='was#1', words=['계시니라']),
    dict(ref=(42, 1, 1), lang='ko', en='the#2', words=['말씀이#1']),
    dict(ref=(42, 1, 1), lang='ko', en='Word#1', words=['말씀이#1']),
    dict(ref=(42, 1, 1), lang='ko', en='the#3', words=['이#1']),
    dict(ref=(42, 1, 1), lang='ko', en='Word#2', words=['말씀이#2']),
    dict(ref=(42, 1, 1), lang='ko', en='was#2', words=['계셨으니']),
    dict(ref=(42, 1, 1), lang='ko', en='and#2', words=['곧']),
    dict(ref=(42, 1, 1), lang='ko', en='the#4', words=['이#2']),
    dict(ref=(42, 1, 1), lang='ko', en='Word#3', words=['말씀은']),
    dict(ref=(42, 1, 1), lang='ko', en='was#3', words=['하나님이시니라']),
    dict(ref=(42, 1, 1), lang='ko', en='God#2', words=['하나님이시니라']),

    dict(ref=(42, 1, 2), lang='ko', en='The', words=['그가']),
    dict(ref=(42, 1, 2), lang='ko', en='same', words=['그가']),
    dict(ref=(42, 1, 2), lang='ko', en='was', words=['계셨고']),
    dict(ref=(42, 1, 2), lang='ko', en='in', words=['태초에']),

    dict(ref=(42, 1, 3), lang='ko', en='were', words=['되었으니']),
    dict(ref=(42, 1, 3), lang='ko', en='made#1', words=['지은#1', '바']),
    dict(ref=(42, 1, 3), lang='ko', en='him#2', words=['그가']),
    dict(ref=(42, 1, 3), lang='ko', en='was#1', words=['없느니라']),
    dict(ref=(42, 1, 3), lang='ko', en='any', words=['하나도']),
    dict(ref=(42, 1, 3), lang='ko', en='thing', words=['하나도', '것이#1']),
    dict(ref=(42, 1, 3), lang='ko', en='made#2', words=['지은#2']),
    dict(ref=(42, 1, 3), lang='ko', en='that', words=['것이#2']),
    dict(ref=(42, 1, 3), lang='ko', en='was#2', words=['된']),
    dict(ref=(42, 1, 3), lang='ko', en='made#3', words=['된']),

    dict(ref=(42, 1, 4), lang='ko', en='was#1', words=['있었으니']),
    dict(ref=(42, 1, 4), lang='ko', en='life#1', words=['생명이']),
    dict(ref=(42, 1, 4), lang='ko', en='the#1', words=['이', '생명은']),
    dict(ref=(42, 1, 4), lang='ko', en='life#2', words=['이', '생명은']),
    dict(ref=(42, 1, 4), lang='ko', en='was#2', words=['빛이라']),
    dict(ref=(42, 1, 4), lang='ko', en='the#2', words=['빛이라']),

    dict(ref=(42, 1, 5), lang='ko', en='the#1', words=['빛이']),
    dict(ref=(42, 1, 5), lang='ko', en='in', words=['어두움에']),
    dict(ref=(42, 1, 5), lang='ko', en='darkness#1', words=['어두움에']),
    dict(ref=(42, 1, 5), lang='ko', en='the#2', words=['어두움이']),
    dict(ref=(42, 1, 5), lang='ko', en='darkness#2', words=['어두움이']),
    dict(ref=(42, 1, 5), lang='ko', en='comprehended', words=['깨닫지']),

    dict(ref=(42, 1, 9), lang='ko', en='the#1', words=['빛']),
    dict(ref=(42, 1, 9), lang='ko', en='Light', words=['빛', '빛이']),
    dict(ref=(42, 1, 9), lang='ko', en='lighteth', words=['비취는']),
    dict(ref=(42, 1, 9), lang='ko', en='that', words=['와서']),
    dict(ref=(42, 1, 9), lang='ko', en='into', words=['세상에']),
    dict(ref=(42, 1, 9), lang='ko', en='the#2', words=['세상에']),

    dict(ref=(42, 1, 10), lang='ko', en='He', words=['그가']),
    dict(ref=(42, 1, 10), lang='ko', en='was#1', words=['계셨으며']),
    dict(ref=(42, 1, 10), lang='ko', en='in', words=['세상에']),
    dict(ref=(42, 1, 10), lang='ko', en='the#1', words=['세상에']),
    dict(ref=(42, 1, 10), lang='ko', en='the#2', words=['세상은']),
    dict(ref=(42, 1, 10), lang='ko', en='world#2', words=['세상은']),
    dict(ref=(42, 1, 10), lang='ko', en='was#2', words=['되었으되']),
    dict(ref=(42, 1, 10), lang='ko', en='made', words=['지은', '바', '되었으되']),
    dict(ref=(42, 1, 10), lang='ko', en='him#1', words=['그로']),
    dict(ref=(42, 1, 10), lang='ko', en='the#3', words=['세상이']),
    dict(ref=(42, 1, 10), lang='ko', en='world#3', words=['세상이']),
    dict(ref=(42, 1, 10), lang='ko', en='him#2', words=['그를']),

    dict(ref=(42, 1, 11), lang='ko', en='He', words=['오매']),
    dict(ref=(42, 1, 11), lang='ko', en='came', words=['오매']),
    dict(ref=(42, 1, 11), lang='ko', en='unto', words=['땅에']),
    dict(ref=(42, 1, 11), lang='ko', en='his#1', words=['자기#1', '땅에']),
    dict(ref=(42, 1, 11), lang='ko', en='own#1', words=['자기#1', '땅에']),
    dict(ref=(42, 1, 11), lang='ko', en='and', words=[]),
    dict(ref=(42, 1, 11), lang='ko', en='his#2', words=['자기#2', '백성이']),
    dict(ref=(42, 1, 11), lang='ko', en='own#2', words=['자기#2', '백성이']),
    dict(ref=(42, 1, 11), lang='ko', en='received', words=['영접지']),
    dict(ref=(42, 1, 11), lang='ko', en='not', words=['아니하였으나']),

    dict(ref=(42, 1, 18), lang='or', en='man', words=['\u03bf\u1f50\u03b4\u03b5\u1f76\u03c2']),

    dict(ref=(42, 1, 13), lang='ko', en='Which', words=['이는', '자들이니라']),
    dict(ref=(42, 1, 13), lang='ko', en='were', words=['나지']),
    dict(ref=(42, 1, 13), lang='ko', en='born', words=['혈통으로나', '나지', '난']),
    dict(ref=(42, 1, 13), lang='ko', en='not', words=['아니하고']),
    dict(ref=(42, 1, 13), lang='ko', en='of#1', words=['혈통으로나']),
    dict(ref=(42, 1, 13), lang='ko', en='blood', words=['혈통으로나']),
    dict(ref=(42, 1, 13), lang='ko', en='nor#1', words=['아니하고']),
    dict(ref=(42, 1, 13), lang='ko', en='of#2', words=['육정으로나']),
    dict(ref=(42, 1, 13), lang='ko', en='the#1', words=['육정으로나']),
    dict(ref=(42, 1, 13), lang='ko', en='will#1', words=['육정으로나']),
    dict(ref=(42, 1, 13), lang='ko', en='of#3', words=['육정으로나']),
    dict(ref=(42, 1, 13), lang='ko', en='the#2', words=['육정으로나']),
    dict(ref=(42, 1, 13), lang='ko', en='flesh', words=['육정으로나']),
    dict(ref=(42, 1, 13), lang='ko', en='nor#2', words=['아니하고']),
    dict(ref=(42, 1, 13), lang='ko', en='of#4', words=['뜻으로']),
    dict(ref=(42, 1, 13), lang='ko', en='the#3', words=['뜻으로']),
    dict(ref=(42, 1, 13), lang='ko', en='will#2', words=['뜻으로']),
    dict(ref=(42, 1, 13), lang='ko', en='of#5', words=['사람의']),
    dict(ref=(42, 1, 13), lang='ko', en='man', words=['사람의']),
    dict(ref=(42, 1, 13), lang='ko', en='of#6', words=['하나님께로서']),

    dict(ref=(42, 1, 14), lang='ko', en='the#1', words=['말씀이']),
    dict(ref=(42, 1, 14), lang='ko', en='among', words=['우리', '가운데']),
    dict(ref=(42, 1, 14), lang='ko', en='us', words=['우리', '가운데']),
    dict(ref=(42, 1, 14), lang='ko', en='we', words=['우리가']),
    dict(ref=(42, 1, 14), lang='ko', en='glory#1', words=['영광을']),
    dict(ref=(42, 1, 14), lang='ko', en='the#2', words=['영광이요']),
    dict(ref=(42, 1, 14), lang='ko', en='glory#2', words=['영광이요']),
    dict(ref=(42, 1, 14), lang='ko', en='as', words=['영광이요']),
    dict(ref=(42, 1, 14), lang='ko', en='of#2', words=['아버지의']),
    dict(ref=(42, 1, 14), lang='ko', en='the#4', words=['아버지의']),
    dict(ref=(42, 1, 14), lang='ko', en='of#3', words=['충만하더라']),
    dict(ref=(42, 1, 14), lang='ko', en='and#3', words=['은혜와']),

    dict(ref=(42, 1, 15), lang='ko', en='bare', words=['증거하여']),
    dict(ref=(42, 1, 15), lang='ko', en='of#1', words=['대하여']),
    dict(ref=(42, 1, 15), lang='ko', en='This', words=['이']),
    dict(ref=(42, 1, 15), lang='ko', en='was#1', words=['가리킴이라']),
    dict(ref=(42, 1, 15), lang='ko', en='he#1', words=['사람을']),
    dict(ref=(42, 1, 15), lang='ko', en='of#2', words=['사람을']),
    dict(ref=(42, 1, 15), lang='ko', en='I', words=['내가']),
    dict(ref=(42, 1, 15), lang='ko', en='spake', words=['전에', '말하기를']),
    dict(ref=(42, 1, 15), lang='ko', en='He', words=['이가']),
    dict(ref=(42, 1, 15), lang='ko', en='that', words=['이가']),
    dict(ref=(42, 1, 15), lang='ko', en='after', words=['내', '뒤에']),
    dict(ref=(42, 1, 15), lang='ko', en='me#1', words=['내', '뒤에']),
    dict(ref=(42, 1, 15), lang='ko', en='is', words=['것은']),
    dict(ref=(42, 1, 15), lang='ko', en='preferred', words=['앞선']),
    dict(ref=(42, 1, 15), lang='ko', en='before#1', words=['나보다#1', '앞선', '것은']),
    dict(ref=(42, 1, 15), lang='ko', en='me#2', words=['나보다#1', '앞선', '것은']),
    dict(ref=(42, 1, 15), lang='ko', en='was#2', words=['계심이니라']),
    dict(ref=(42, 1, 15), lang='ko', en='before#2', words=['나보다#2', '먼저', '계심이니라']),
    dict(ref=(42, 1, 15), lang='ko', en='me#3', words=['나보다#2', '먼저', '계심이니라']),

    dict(ref=(42, 1, 16), lang='ko', en='And', words=[]),
    dict(ref=(42, 1, 16), lang='ko', en='of', words=['데서']),
    dict(ref=(42, 1, 16), lang='ko', en='have', words=['받으니']),
    dict(ref=(42, 1, 16), lang='ko', en='we', words=['우리가']),
    dict(ref=(42, 1, 16), lang='ko', en='for', words=['위에']),
    dict(ref=(42, 1, 16), lang='ko', en='grace#1', words=['은혜']),
    dict(ref=(42, 1, 16), lang='ko', en='grace#2', words=['은혜러라']),

    dict(ref=(42, 1, 17), lang='ko', en='by#1', words=['말미암아#1']),
    dict(ref=(42, 1, 17), lang='ko', en='by#2', words=['말미암아#2']),
    dict(ref=(42, 1, 17), lang='ko', en='Christ', words=['그리스도로']),
    dict(ref=(42, 1, 17), lang='ko', en='came', words=['온', '것이라']),

    dict(ref=(42, 1, 18), lang='ko', en='man', words=['사람이']),
    dict(ref=(42, 1, 18), lang='ko', en='hath#1', words=['없으되']),
    dict(ref=(42, 1, 18), lang='ko', en='at', words=['본래']),
    dict(ref=(42, 1, 18), lang='ko', en='any', words=['본래']),
    dict(ref=(42, 1, 18), lang='ko', en='time', words=['본래']),
    dict(ref=(42, 1, 18), lang='ko', en='only', words=['독생하신']),
    dict(ref=(42, 1, 18), lang='ko', en='begotten', words=['독생하신']),
    dict(ref=(42, 1, 18), lang='ko', en='Son', words=['하나님이']),
    dict(ref=(42, 1, 18), lang='ko', en='which', words=['있는']),
    dict(ref=(42, 1, 18), lang='ko', en='in', words=['속에']),
    dict(ref=(42, 1, 18), lang='ko', en='the#2', words=['속에']),
    dict(ref=(42, 1, 18), lang='ko', en='of', words=['아버지']),
    dict(ref=(42, 1, 18), lang='ko', en='the#3', words=['아버지']),
    dict(ref=(42, 1, 18), lang='ko', en='he', words=['하나님이']),
    dict(ref=(42, 1, 18), lang='ko', en='hath#2', words=['나타내셨느니라']),
    dict(ref=(42, 1, 18), lang='ko', en='declared', words=['나타내셨느니라']),

    dict(ref=(42, 1, 19), lang='ko', en='is', words=['이러하니라']),
    dict(ref=(42, 1, 19), lang='ko', en='the#1', words=['증거가']),
    dict(ref=(42, 1, 19), lang='ko', en='of', words=['요한의']),
    dict(ref=(42, 1, 19), lang='ko', en='John', words=['요한에게', '요한의']),
    dict(ref=(42, 1, 19), lang='ko', en='from', words=['예루살렘에서']),
    dict(ref=(42, 1, 19), lang='ko', en='to', words=['물을']),
    dict(ref=(42, 1, 19), lang='ko', en='ask', words=['물을']),
    dict(ref=(42, 1, 19), lang='ko', en='him', words=['요한에게']),
    dict(ref=(42, 1, 19), lang='ko', en='art', words=['누구냐']),

    dict(ref=(42, 1, 20), lang='ko', en='he', words=['요한이']),
    dict(ref=(42, 1, 20), lang='ko', en='confessed#1', words=['드러내어#1', '말하고']),
    dict(ref=(42, 1, 20), lang='ko', en='denied', words=['숨기지']),
    dict(ref=(42, 1, 20), lang='ko', en='not#1', words=['아니하니']),
    dict(ref=(42, 1, 20), lang='ko', en='confessed#2', words=['드러내어#2', '하는', '말이']),
    dict(ref=(42, 1, 20), lang='ko', en='I', words=['나는']),
    dict(ref=(42, 1, 20), lang='ko', en='not#2', words=['아니라']),
    dict(ref=(42, 1, 20), lang='ko', en='the', words=['그리스도가']),
    dict(ref=(42, 1, 20), lang='ko', en='Christ', words=['그리스도가']),

    dict(ref=(42, 1, 21), lang='ko', en='they', words=[]),
    dict(ref=(42, 1, 21), lang='ko', en='then', words=['그러면']),
    dict(ref=(42, 1, 21), lang='ko', en='Art#1', words=['엘리야냐']),
    dict(ref=(42, 1, 21), lang='ko', en='thou#1', words=['네가#1']),
    dict(ref=(42, 1, 21), lang='ko', en='Elias', words=['엘리야냐']),
    dict(ref=(42, 1, 21), lang='ko', en='And#2', words=['또#2']),
    dict(ref=(42, 1, 21), lang='ko', en='he#1', words=['가로되']),
    dict(ref=(42, 1, 21), lang='ko', en='saith', words=['가로되']),
    dict(ref=(42, 1, 21), lang='ko', en='I', words=['나는']),
    dict(ref=(42, 1, 21), lang='ko', en='Art#2', words=['묻되#2', '선지자냐']),
    dict(ref=(42, 1, 21), lang='ko', en='thou#2', words=['네가#2']),
    dict(ref=(42, 1, 21), lang='ko', en='that', words=['그']),
    dict(ref=(42, 1, 21), lang='ko', en='prophet', words=['선지자냐']),
    dict(ref=(42, 1, 21), lang='ko', en='And#3', words=['대답하되']),
    dict(ref=(42, 1, 21), lang='ko', en='he#2', words=['대답하되']),
    dict(ref=(42, 1, 21), lang='ko', en='No', words=['아니라#2']),

    dict(ref=(42, 1, 22), lang='ko', en='Then', words=['또']),
    dict(ref=(42, 1, 22), lang='ko', en='said', words=['말하되']),
    dict(ref=(42, 1, 22), lang='ko', en='art', words=['누구냐']),
    dict(ref=(42, 1, 22), lang='ko', en='thou#1', words=['너는']),
    dict(ref=(42, 1, 22), lang='ko', en='may', words=['하라']),
    dict(ref=(42, 1, 22), lang='ko', en='give', words=['대답하게']),
    dict(ref=(42, 1, 22), lang='ko', en='an', words=['대답하게']),
    dict(ref=(42, 1, 22), lang='ko', en='to', words=['이들에게']),
    dict(ref=(42, 1, 22), lang='ko', en='them', words=['이들에게']),
    dict(ref=(42, 1, 22), lang='ko', en='that#2', words=['보낸']),
    dict(ref=(42, 1, 22), lang='ko', en='sayest', words=['하느냐']),
    dict(ref=(42, 1, 22), lang='ko', en='thou#2', words=['너는']),
    dict(ref=(42, 1, 22), lang='ko', en='of', words=['대하여']),

    dict(ref=(42, 1, 23), lang='ko', en='said#1', words=['가로되', '하니라']),
    dict(ref=(42, 1, 23), lang='ko', en='I', words=['나는']),
    dict(ref=(42, 1, 23), lang='ko', en='am', words=['나는']),
    dict(ref=(42, 1, 23), lang='ko', en='the#1', words=['소리로라']),
    dict(ref=(42, 1, 23), lang='ko', en='of#1', words=['자의']),
    dict(ref=(42, 1, 23), lang='ko', en='one', words=['자의']),
    dict(ref=(42, 1, 23), lang='ko', en='in', words=['광야에서']),
    dict(ref=(42, 1, 23), lang='ko', en='the#2', words=['광야에서']),
    dict(ref=(42, 1, 23), lang='ko', en='Make', words=['하라고']),
    dict(ref=(42, 1, 23), lang='ko', en='the#3', words=['길을']),
    dict(ref=(42, 1, 23), lang='ko', en='of#2', words=['주의']),
    dict(ref=(42, 1, 23), lang='ko', en='the#4', words=['주의']),
    dict(ref=(42, 1, 23), lang='ko', en='said#2', words=['말과']),
    dict(ref=(42, 1, 23), lang='ko', en='the#5', words=['선지자']),
    dict(ref=(42, 1, 23), lang='ko', en='Esaias', words=['이사야의']),

    dict(ref=(42, 1, 24), lang='ko', en='And', words=[]),
    dict(ref=(42, 1, 24), lang='ko', en='they', words=['저희는']),
    dict(ref=(42, 1, 24), lang='ko', en='which', words=['저희는']),
    dict(ref=(42, 1, 24), lang='ko', en='were#1', words=['보낸자라']),
    dict(ref=(42, 1, 24), lang='ko', en='sent', words=['보낸자라']),
    dict(ref=(42, 1, 24), lang='ko', en='were#2', words=['보낸자라']),
    dict(ref=(42, 1, 24), lang='ko', en='of', words=['바리새인들에게서']),
    dict(ref=(42, 1, 24), lang='ko', en='the', words=['바리새인들에게서']),
    dict(ref=(42, 1, 24), lang='la', en='they', words=['\u0071\u0075\u0069']),
    dict(ref=(42, 1, 24), lang='or', en='they', words=['\u03bf\u1f31']),

    dict(ref=(42, 1, 24), lang='ko', en='which', words=['보낸자라']),

    dict(ref=(42, 1, 25), lang='ko', en='him#1', words=[]),
    dict(ref=(42, 1, 25), lang='ko', en='him#2', words=[]),
    dict(ref=(42, 1, 25), lang='ko', en='thou#1', words=['네가']),
    dict(ref=(42, 1, 25), lang='ko', en='thou#2', words=['네가']),
    dict(ref=(42, 1, 25), lang='ko', en='baptizest', words=['침례를', '주느냐']),
    dict(ref=(42, 1, 25), lang='ko', en='be', words=['아니요#1']),
    dict(ref=(42, 1, 25), lang='ko', en='not', words=['아니요#1']),
    dict(ref=(42, 1, 25), lang='ko', en='that#1', words=['그리스도도']),
    dict(ref=(42, 1, 25), lang='ko', en='nor', words=['아니요#2']),
    dict(ref=(42, 1, 25), lang='ko', en='neither', words=['아닐진대']),
    dict(ref=(42, 1, 25), lang='ko', en='that#2', words=['그']),

    dict(ref=(42, 1, 26), lang='ko', en='saying', words=['대답하되']),
    dict(ref=(42, 1, 26), lang='ko', en='baptize', words=['침례를', '주거니와']),
    dict(ref=(42, 1, 26), lang='ko', en='with', words=['물로']),
    dict(ref=(42, 1, 26), lang='ko', en='there', words=['섰으니']),
    dict(ref=(42, 1, 26), lang='ko', en='you', words=['너희']),
    dict(ref=(42, 1, 26), lang='ko', en='ye', words=['너희가']),

    dict(ref=(42, 1, 27), lang='ko', en='He', words=['그이라']),
    dict(ref=(42, 1, 27), lang='ko', en='it', words=['그이라']),
    dict(ref=(42, 1, 27), lang='ko', en='is#1', words=['그이라']),
    dict(ref=(42, 1, 27), lang='ko', en='who', words=['곧']),
    dict(ref=(42, 1, 27), lang='ko', en='after', words=['내', '뒤에']),
    dict(ref=(42, 1, 27), lang='ko', en='me#1', words=['내', '뒤에']),
    dict(ref=(42, 1, 27), lang='ko', en='whose', words=['그의']),
    dict(ref=(42, 1, 27), lang='ko', en='I', words=['나는']),
    dict(ref=(42, 1, 27), lang='ko', en='am', words=['나는']),
    dict(ref=(42, 1, 27), lang='ko', en='not', words=['못하겠노라']),
    dict(ref=(42, 1, 27), lang='ko', en='to', words=['풀기도']),

    dict(ref=(42, 1, 29), lang='ko', en='The', words=['이튿날']),
    dict(ref=(42, 1, 29), lang='ko', en='coming', words=['자기에게', '나아오심을']),
    dict(ref=(42, 1, 29), lang='ko', en='unto', words=['자기에게', '나아오심을']),
    dict(ref=(42, 1, 29), lang='ko', en='him', words=['자기에게', '나아오심을']),
    dict(ref=(42, 1, 29), lang='ko', en='the#1', words=['어린', '양이로다']),
    dict(ref=(42, 1, 29), lang='ko', en='of#1', words=['하나님의']),
    dict(ref=(42, 1, 29), lang='ko', en='taketh', words=['지고', '가는']),
    dict(ref=(42, 1, 29), lang='ko', en='away', words=['지고', '가는']),
    dict(ref=(42, 1, 29), lang='ko', en='the#2', words=['죄를']),
    dict(ref=(42, 1, 29), lang='ko', en='of#2', words=['세상']),
    dict(ref=(42, 1, 29), lang='ko', en='the#3', words=['세상']),

    dict(ref=(42, 1, 30), lang='ko', en='This', words=['이']),
    dict(ref=(42, 1, 30), lang='ko', en='is#1', words=['가리킴이라']),
    dict(ref=(42, 1, 30), lang='ko', en='he#1', words=['사람을']),
    dict(ref=(42, 1, 30), lang='ko', en='of', words=['사람을']),
    dict(ref=(42, 1, 30), lang='ko', en='I', words=['내가']),
    dict(ref=(42, 1, 30), lang='ko', en='said', words=['전에', '말하기를']),
    dict(ref=(42, 1, 30), lang='ko', en='After', words=['내', '뒤에']),
    dict(ref=(42, 1, 30), lang='ko', en='me#1', words=['내', '뒤에']),
    dict(ref=(42, 1, 30), lang='ko', en='a', words=['사람이']),
    dict(ref=(42, 1, 30), lang='ko', en='which', words=['있는데']),
    dict(ref=(42, 1, 30), lang='ko', en='is#2', words=['것은']),
    dict(ref=(42, 1, 30), lang='ko', en='preferred', words=['앞선']),
    dict(ref=(42, 1, 30), lang='ko', en='before#1', words=['나보다#1', '앞선', '것은']),
    dict(ref=(42, 1, 30), lang='ko', en='me#2', words=['나보다#1', '앞선', '것은']),
    dict(ref=(42, 1, 30), lang='ko', en='he#2', words=['그가']),
    dict(ref=(42, 1, 30), lang='ko', en='was', words=['계심이라']),
    dict(ref=(42, 1, 30), lang='ko', en='before#2', words=['나보다#2', '먼저', '계심이라']),
    dict(ref=(42, 1, 30), lang='ko', en='me#3', words=['나보다#2', '먼저', '계심이라']),

    dict(ref=(42, 1, 31), lang='ko', en='I#1', words=['나도']),
    dict(ref=(42, 1, 31), lang='ko', en='not', words=['못하였으나']),
    dict(ref=(42, 1, 31), lang='ko', en='he', words=['그를#2']),
    dict(ref=(42, 1, 31), lang='ko', en='should', words=['함이라']),
    dict(ref=(42, 1, 31), lang='ko', en='made', words=['나타내려']),
    dict(ref=(42, 1, 31), lang='ko', en='to', words=['이스라엘에게']),
    dict(ref=(42, 1, 31), lang='ko', en='therefore', words=['것은']),
    dict(ref=(42, 1, 31), lang='ko', en='am', words=['내가']),
    dict(ref=(42, 1, 31), lang='ko', en='I#2', words=['내가']),
    dict(ref=(42, 1, 31), lang='ko', en='baptizing', words=['침례를', '주는']),

    dict(ref=(42, 1, 33), lang='ko', en='I', words=['나도']),
    dict(ref=(42, 1, 33), lang='ko', en='not', words=['못하였으나']),
    dict(ref=(42, 1, 33), lang='ko', en='he#1', words=['그이가']),
    dict(ref=(42, 1, 33), lang='ko', en='that', words=['그이가', '하신']),
    dict(ref=(42, 1, 33), lang='ko', en='me#1', words=['나를']),
    dict(ref=(42, 1, 33), lang='ko', en='to', words=['침례를#1', '주라']),
    dict(ref=(42, 1, 33), lang='ko', en='baptize', words=['침례를#1', '주라']),
    dict(ref=(42, 1, 33), lang='ko', en='the#1', words=['그이가']),
    dict(ref=(42, 1, 33), lang='ko', en='same#1', words=['그이가']),
    dict(ref=(42, 1, 33), lang='ko', en='said', words=['말씀하시되']),
    dict(ref=(42, 1, 33), lang='ko', en='unto', words=['나에게']),
    dict(ref=(42, 1, 33), lang='ko', en='me#2', words=['나에게']),
    dict(ref=(42, 1, 33), lang='ko', en='Upon', words=['위에든지']),
    dict(ref=(42, 1, 33), lang='ko', en='thou', words=['보거든']),
    dict(ref=(42, 1, 33), lang='ko', en='shalt', words=['보거든']),
    dict(ref=(42, 1, 33), lang='ko', en='see', words=['보거든']),
    dict(ref=(42, 1, 33), lang='ko', en='the#2', words=['성령이']),
    dict(ref=(42, 1, 33), lang='ko', en='remaining', words=['머무는', '것을']),
    dict(ref=(42, 1, 33), lang='ko', en='on', words=['위에든지']),
    dict(ref=(42, 1, 33), lang='ko', en='him#2', words=['위에든지']),
    dict(ref=(42, 1, 33), lang='ko', en='the#3', words=['그가']),
    dict(ref=(42, 1, 33), lang='ko', en='same#2', words=['그가']),
    dict(ref=(42, 1, 33), lang='ko', en='is', words=['곧']),
    dict(ref=(42, 1, 33), lang='ko', en='he#2', words=['이인줄', '알라']),
    dict(ref=(42, 1, 33), lang='ko', en='which', words=['이인줄']),
    dict(ref=(42, 1, 33), lang='ko', en='baptizeth', words=['침례를#2', '주는']),
    dict(ref=(42, 1, 33), lang='ko', en='with#2', words=['성령으로']),
    dict(ref=(42, 1, 33), lang='ko', en='the#4', words=['성령으로']),
    dict(ref=(42, 1, 33), lang='ko', en='Holy', words=['성령으로']),
    dict(ref=(42, 1, 33), lang='ko', en='Ghost', words=['성령으로']),

    dict(ref=(42, 1, 34), lang='ko', en='And', words=[]),
    dict(ref=(42, 1, 34), lang='ko', en='saw', words=['보고']),
    dict(ref=(42, 1, 34), lang='ko', en='bare', words=['증거하였노라']),
    dict(ref=(42, 1, 34), lang='ko', en='record', words=['증거하였노라']),
    dict(ref=(42, 1, 34), lang='ko', en='this', words=['그가']),
    dict(ref=(42, 1, 34), lang='ko', en='is', words=['아들이심을']),
    dict(ref=(42, 1, 34), lang='ko', en='the', words=['아들이심을']),
    dict(ref=(42, 1, 34), lang='ko', en='Son', words=['아들이심을']),
    dict(ref=(42, 1, 34), lang='ko', en='of', words=['하나님의']),
    dict(ref=(42, 1, 34), lang='or', en='saw', words=['\u1f11\u1f7d\u03c1\u03b1\u03ba\u03b1']),

    dict(ref=(42, 1, 35), lang='ko', en='two', words=['두', '사람과']),
    dict(ref=(42, 1, 35), lang='ko', en='of', words=['중']),

    dict(ref=(42, 1, 38), lang='ko', en='following', words=['좇는', '것을']),
    dict(ref=(42, 1, 38), lang='ko', en='saith', words=['물어', '가라사대']),
    dict(ref=(42, 1, 38), lang='ko', en='unto#1', words=['가라사대']),
    dict(ref=(42, 1, 38), lang='ko', en='They', words=['가로되']),
    dict(ref=(42, 1, 38), lang='ko', en='said', words=['가로되']),
    dict(ref=(42, 1, 38), lang='ko', en='Rabbi', words=['랍비여', '랍비는']),
    dict(ref=(42, 1, 38), lang='ko', en='which', words=['번역하면']),
    dict(ref=(42, 1, 38), lang='ko', en='is', words=['선생이라']),
    dict(ref=(42, 1, 38), lang='ko', en='to', words=['번역하면']),
    dict(ref=(42, 1, 38), lang='ko', en='say', words=['번역하면']),
    dict(ref=(42, 1, 38), lang='ko', en='being', words=['번역하면']),
    dict(ref=(42, 1, 38), lang='ko', en='dwellest', words=['계시오니이까']),
    dict(ref=(42, 1, 38), lang='ko', en='thou', words=['계시오니이까']),

    dict(ref=(42, 1, 39), lang='ko', en='He', words=['예수께서']),
    dict(ref=(42, 1, 39), lang='ko', en='them', words=[]),
    dict(ref=(42, 1, 39), lang='ko', en='They', words=['그러므로', '저희가']),
    dict(ref=(42, 1, 39), lang='ko', en='where', words=['데를']),
    dict(ref=(42, 1, 39), lang='ko', en='he', words=['계신']),
    dict(ref=(42, 1, 39), lang='ko', en='dwelt', words=['계신']),
    dict(ref=(42, 1, 39), lang='ko', en='him', words=['함께']),
    dict(ref=(42, 1, 39), lang='ko', en='that', words=['그날']),
    dict(ref=(42, 1, 39), lang='ko', en='day', words=['그날']),
    dict(ref=(42, 1, 39), lang='ko', en='for', words=['때가']),
    dict(ref=(42, 1, 39), lang='ko', en='it', words=['때가']),
    dict(ref=(42, 1, 39), lang='ko', en='about', words=['제십시쯤']),
    dict(ref=(42, 1, 39), lang='ko', en='the', words=['제십시쯤']),
    dict(ref=(42, 1, 39), lang='ko', en='tenth', words=['제십시쯤']),
    dict(ref=(42, 1, 39), lang='ko', en='hour', words=['제십시쯤']),

    dict(ref=(42, 1, 40), lang='ko', en='the#1', words=['사람']),
    dict(ref=(42, 1, 40), lang='ko', en='which', words=['좇는']),
    dict(ref=(42, 1, 40), lang='ko', en='followed', words=['좇는']),
    dict(ref=(42, 1, 40), lang='ko', en='him', words=['예수를']),
    dict(ref=(42, 1, 40), lang='ko', en='was', words=['안드레라']),
    dict(ref=(42, 1, 40), lang='ko', en='s', words=['베드로의']),

    dict(ref=(42, 1, 41), lang='ko', en='He', words=['그가']),
    dict(ref=(42, 1, 41), lang='ko', en='his', words=['자기의']),
    dict(ref=(42, 1, 41), lang='ko', en='have', words=['만났다']),
    dict(ref=(42, 1, 41), lang='ko', en='the#1', words=['메시야를']),
    dict(ref=(42, 1, 41), lang='ko', en='which', words=['번역하면']),
    dict(ref=(42, 1, 41), lang='ko', en='the#2', words=['그리스도라']),

    dict(ref=(42, 1, 42), lang='ko', en='he#1', words=['데리고']),
    dict(ref=(42, 1, 42), lang='ko', en='brought', words=['데리고', '오니']),
    dict(ref=(42, 1, 42), lang='ko', en='to', words=['예수께로']),
    dict(ref=(42, 1, 42), lang='ko', en='when', words=['보시고']),
    dict(ref=(42, 1, 42), lang='ko', en='him#2', words=['보시고']),
    dict(ref=(42, 1, 42), lang='ko', en='he#2', words=['가라사대']),
    dict(ref=(42, 1, 42), lang='ko', en='art', words=['시몬이니']),
    dict(ref=(42, 1, 42), lang='ko', en='the#1', words=['아들']),
    dict(ref=(42, 1, 42), lang='ko', en='of', words=['요한의']),
    dict(ref=(42, 1, 42), lang='ko', en='thou', words=['장차']),
    dict(ref=(42, 1, 42), lang='ko', en='shalt', words=['장차']),
    dict(ref=(42, 1, 42), lang='ko', en='be', words=['하리라']),
    dict(ref=(42, 1, 42), lang='ko', en='called', words=['하리라']),
    dict(ref=(42, 1, 42), lang='ko', en='Cephas', words=['게바라', '게바는']),
    dict(ref=(42, 1, 42), lang='ko', en='which', words=['번역하면']),
    dict(ref=(42, 1, 42), lang='ko', en='by', words=['번역하면']),
    dict(ref=(42, 1, 42), lang='ko', en='A', words=['베드로라']),
    dict(ref=(42, 1, 42), lang='ko', en='stone', words=['베드로라']),

    dict(ref=(42, 1, 43), lang='ko', en='would', words=['하시다가']),
    dict(ref=(42, 1, 43), lang='ko', en='into', words=['갈릴리로']),
    dict(ref=(42, 1, 43), lang='ko', en='saith', words=['이르시되']),

    dict(ref=(42, 1, 45), lang='ko', en='findeth', words=['찾아']),
    dict(ref=(42, 1, 45), lang='ko', en='saith', words=['이르되']),
    dict(ref=(42, 1, 45), lang='ko', en='found', words=['만났으니']),
    dict(ref=(42, 1, 45), lang='ko', en='him#2', words=['그이를']),
    dict(ref=(42, 1, 45), lang='ko', en='of#1', words=['그이를']),
    dict(ref=(42, 1, 45), lang='ko', en='whom', words=['그이를']),
    dict(ref=(42, 1, 45), lang='ko', en='in', words=['율법에']),
    dict(ref=(42, 1, 45), lang='ko', en='the#1', words=['율법에']),
    dict(ref=(42, 1, 45), lang='ko', en='the#2', words=['여러']),
    dict(ref=(42, 1, 45), lang='ko', en='did', words=['기록한']),
    dict(ref=(42, 1, 45), lang='ko', en='write', words=['기록하였고', '기록한']),
    dict(ref=(42, 1, 45), lang='ko', en='of#2', words=['나사렛']),
    dict(ref=(42, 1, 45), lang='ko', en='the#3', words=['아들']),
    dict(ref=(42, 1, 45), lang='ko', en='of#3', words=['요셉의']),

    dict(ref=(42, 1, 46), lang='ko', en='Can', words=['수']),
    dict(ref=(42, 1, 46), lang='ko', en='thing', words=['것이']),
    dict(ref=(42, 1, 46), lang='ko', en='come', words=['날']),
    dict(ref=(42, 1, 46), lang='ko', en='out', words=['나사렛에서']),
    dict(ref=(42, 1, 46), lang='ko', en='of', words=['나사렛에서']),
    dict(ref=(42, 1, 46), lang='ko', en='saith', words=['가로되#2']),

    dict(ref=(42, 1, 47), lang='ko', en='coming', words=['오는', '것을']),
    dict(ref=(42, 1, 47), lang='ko', en='to', words=['자기에게']),
    dict(ref=(42, 1, 47), lang='ko', en='of', words=['그를', '가리켜']),
    dict(ref=(42, 1, 47), lang='ko', en='him#2', words=['그를', '가리켜']),
    dict(ref=(42, 1, 47), lang='ko', en='an', words=['이는']),
    dict(ref=(42, 1, 47), lang='ko', en='Israelite', words=['이스라엘', '사람이라']),
    dict(ref=(42, 1, 47), lang='ko', en='whom', words=['그']),

    dict(ref=(42, 1, 48), lang='ko', en='saith', words=['가로되']),
    dict(ref=(42, 1, 48), lang='ko', en='Whence', words=['어떻게']),
    dict(ref=(42, 1, 48), lang='ko', en='knowest', words=['아시나이까']),
    dict(ref=(42, 1, 48), lang='ko', en='thou#1', words=[]),
    dict(ref=(42, 1, 48), lang='ko', en='that', words=['전에']),
    dict(ref=(42, 1, 48), lang='ko', en='thou#2', words=['네가']),
    dict(ref=(42, 1, 48), lang='ko', en='wast', words=['있을']),
    dict(ref=(42, 1, 48), lang='ko', en='the', words=['무화과나무']),
    dict(ref=(42, 1, 48), lang='ko', en='thee#2', words=['보았노라']),

    dict(ref=(42, 1, 49), lang='ko', en='saith', words=['대답하되']),
    dict(ref=(42, 1, 49), lang='ko', en='thou#1', words=['당신은#1']),
    dict(ref=(42, 1, 49), lang='ko', en='art#1', words=['당신은#1']),
    dict(ref=(42, 1, 49), lang='ko', en='the#1', words=['아들이시요']),
    dict(ref=(42, 1, 49), lang='ko', en='Son', words=['아들이시요']),
    dict(ref=(42, 1, 49), lang='ko', en='of#1', words=['하나님의']),
    dict(ref=(42, 1, 49), lang='ko', en='thou#2', words=['당신은#2']),
    dict(ref=(42, 1, 49), lang='ko', en='art#2', words=['당신은#2']),
    dict(ref=(42, 1, 49), lang='ko', en='the#2', words=['임금이로소이다']),
    dict(ref=(42, 1, 49), lang='ko', en='King', words=['임금이로소이다']),
    dict(ref=(42, 1, 49), lang='ko', en='of#2', words=['이스라엘의']),

    dict(ref=(42, 1, 50), lang='ko', en='Because', words=['하므로']),
    dict(ref=(42, 1, 50), lang='ko', en='said#2', words=['하므로']),
    dict(ref=(42, 1, 50), lang='ko', en='unto#2', words=['너를']),
    dict(ref=(42, 1, 50), lang='ko', en='thee#1', words=['너를']),
    dict(ref=(42, 1, 50), lang='ko', en='thee#2', words=['너를']),
    dict(ref=(42, 1, 50), lang='ko', en='I#2', words=['보았다']),
    dict(ref=(42, 1, 50), lang='ko', en='shalt', words=['보리라']),

    dict(ref=(42, 1, 51), lang='ko', en='him', words=[]),
    dict(ref=(42, 1, 51), lang='ko', en='unto#1', words=['가라사대']),
    dict(ref=(42, 1, 51), lang='ko', en='Verily', words=['진실로#1']),
    dict(ref=(42, 1, 51), lang='ko', en='verily', words=['진실로#2']),
    dict(ref=(42, 1, 51), lang='ko', en='I', words=['이르노니']),
    dict(ref=(42, 1, 51), lang='ko', en='say', words=['이르노니']),
    dict(ref=(42, 1, 51), lang='ko', en='unto#2', words=['이르노니']),
    dict(ref=(42, 1, 51), lang='ko', en='ye', words=['보리라']),
    dict(ref=(42, 1, 51), lang='ko', en='shall', words=['보리라']),
    dict(ref=(42, 1, 51), lang='ko', en='the#1', words=['사자들이']),
    dict(ref=(42, 1, 51), lang='ko', en='of#1', words=['하나님의']),
    dict(ref=(42, 1, 51), lang='ko', en='descending', words=['내리락', '것을']),
    dict(ref=(42, 1, 51), lang='ko', en='the#2', words=['인자']),
    dict(ref=(42, 1, 51), lang='ko', en='Son', words=['인자']),
    dict(ref=(42, 1, 51), lang='ko', en='of#2', words=['인자']),
    dict(ref=(42, 1, 51), lang='ko', en='man', words=['인자']),

    # ---- 요한복음 2장 ----
    dict(ref=(42, 2, 1), lang='ko', en='the#1', words=['날에']),
    dict(ref=(42, 2, 1), lang='ko', en='there#1', words=[]),
    dict(ref=(42, 2, 1), lang='ko', en='a', words=['혼인이']),
    dict(ref=(42, 2, 1), lang='ko', en='in', words=['가나에']),
    dict(ref=(42, 2, 1), lang='ko', en='of#1', words=['갈릴리']),
    dict(ref=(42, 2, 1), lang='ko', en='the#2', words=['어머니도']),
    dict(ref=(42, 2, 1), lang='ko', en='of#2', words=['예수의']),
    dict(ref=(42, 2, 1), lang='ko', en='was#2', words=['계시고']),

    dict(ref=(42, 2, 3), lang='ko', en='when', words=['모자란지라']),
    dict(ref=(42, 2, 3), lang='ko', en='wanted', words=['모자란지라']),
    dict(ref=(42, 2, 3), lang='ko', en='wine#1', words=['포도주가#1']),
    dict(ref=(42, 2, 3), lang='ko', en='saith', words=['이르되']),
    dict(ref=(42, 2, 3), lang='ko', en='unto', words=['예수에게']),
    dict(ref=(42, 2, 3), lang='ko', en='him', words=['예수에게']),
    dict(ref=(42, 2, 3), lang='ko', en='They', words=['저희에게']),
    dict(ref=(42, 2, 3), lang='ko', en='wine#2', words=['포도주가#2']),

    dict(ref=(42, 2, 4), lang='ko', en='I', words=['나와']),
    dict(ref=(42, 2, 4), lang='ko', en='have', words=['상관이']),
    dict(ref=(42, 2, 4), lang='ko', en='to', words=['상관이']),
    dict(ref=(42, 2, 4), lang='ko', en='do', words=['상관이']),
    dict(ref=(42, 2, 4), lang='ko', en='with', words=['나와']),
    dict(ref=(42, 2, 4), lang='ko', en='thee', words=['나와']),
    dict(ref=(42, 2, 4), lang='ko', en='mine', words=['내']),
    dict(ref=(42, 2, 4), lang='ko', en='hour', words=['때가']),
    dict(ref=(42, 2, 4), lang='ko', en='is', words=['있나이까', '못하였나이다']),
    dict(ref=(42, 2, 4), lang='ko', en='not', words=['못하였나이다']),
    dict(ref=(42, 2, 4), lang='ko', en='come', words=['이르지']),

    dict(ref=(42, 2, 5), lang='ko', en='saith#1', words=['이르되']),
    dict(ref=(42, 2, 5), lang='ko', en='unto#1', words=['하인들에게', '이르되']),
    dict(ref=(42, 2, 5), lang='ko', en='the', words=['하인들에게']),
    dict(ref=(42, 2, 5), lang='ko', en='servants', words=['하인들에게']),
    dict(ref=(42, 2, 5), lang='ko', en='saith#2', words=['말씀을', '하시든지']),
    dict(ref=(42, 2, 5), lang='ko', en='unto#2', words=['너희에게']),
    dict(ref=(42, 2, 5), lang='ko', en='do', words=['하라']),
    dict(ref=(42, 2, 5), lang='ko', en='it', words=['그대로']),

    dict(ref=(42, 2, 6), lang='ko', en='there#1', words=['놓였는지라']),
    dict(ref=(42, 2, 6), lang='ko', en='were', words=['놓였는지라']),
    dict(ref=(42, 2, 6), lang='ko', en='of#1', words=['돌항아리']),
    dict(ref=(42, 2, 6), lang='ko', en='stone', words=['돌항아리']),
    dict(ref=(42, 2, 6), lang='ko', en='the#1', words=['결례를']),
    dict(ref=(42, 2, 6), lang='ko', en='manner', words=['결례를']),
    dict(ref=(42, 2, 6), lang='ko', en='of#2', words=['결례를']),
    dict(ref=(42, 2, 6), lang='ko', en='the#2', words=['결례를']),
    dict(ref=(42, 2, 6), lang='ko', en='purifying', words=['결례를']),
    dict(ref=(42, 2, 6), lang='ko', en='of#3', words=['유대인의']),
    dict(ref=(42, 2, 6), lang='ko', en='the#3', words=['유대인의']),
    dict(ref=(42, 2, 6), lang='ko', en='containing', words=['드는']),
    dict(ref=(42, 2, 6), lang='ko', en='two', words=['두세']),
    dict(ref=(42, 2, 6), lang='ko', en='or', words=['두세']),
    dict(ref=(42, 2, 6), lang='ko', en='three', words=['두세']),
    dict(ref=(42, 2, 6), lang='ko', en='firkins', words=['통']),
    dict(ref=(42, 2, 6), lang='ko', en='apiece', words=['통']),

    dict(ref=(42, 2, 7), lang='ko', en='saith', words=['이르시되']),
    dict(ref=(42, 2, 7), lang='ko', en='unto', words=['이르시되']),
    dict(ref=(42, 2, 7), lang='ko', en='Fill', words=['채우라']),
    dict(ref=(42, 2, 7), lang='ko', en='the#1', words=['항아리에']),
    dict(ref=(42, 2, 7), lang='ko', en='waterpots', words=['항아리에']),
    dict(ref=(42, 2, 7), lang='ko', en='with', words=['물을']),
    dict(ref=(42, 2, 7), lang='ko', en='filled', words=['채우니']),
    dict(ref=(42, 2, 7), lang='ko', en='up', words=['아구까지']),
    dict(ref=(42, 2, 7), lang='ko', en='to', words=['아구까지']),
    dict(ref=(42, 2, 7), lang='ko', en='the#2', words=['아구까지']),
    dict(ref=(42, 2, 7), lang='ko', en='brim', words=['아구까지']),

    dict(ref=(42, 2, 25), lang='ko', en='not', words=['없음이니라']),
    dict(ref=(42, 2, 25), lang='ko', en='any', words=['아무의']),
    dict(ref=(42, 2, 25), lang='ko', en='of', words=['대하여']),
    dict(ref=(42, 2, 25), lang='ko', en='man#1', words=['사람에']),
    dict(ref=(42, 2, 25), lang='ko', en='he', words=['친히']),
    dict(ref=(42, 2, 25), lang='ko', en='what', words=['것을']),
    dict(ref=(42, 2, 25), lang='ko', en='man#2', words=['사람의']),

    dict(ref=(42, 2, 24), lang='ko', en='did', words=['아니하셨으니']),
    dict(ref=(42, 2, 24), lang='ko', en='commit', words=['의탁지']),
    dict(ref=(42, 2, 24), lang='ko', en='himself', words=['그', '몸을']),
    dict(ref=(42, 2, 24), lang='ko', en='unto', words=['저희에게']),
    dict(ref=(42, 2, 24), lang='ko', en='he', words=['친히']),
    dict(ref=(42, 2, 24), lang='ko', en='knew', words=['아심이요']),
    dict(ref=(42, 2, 24), lang='ko', en='men', words=['사람을']),

    dict(ref=(42, 2, 19), lang='ko', en='unto', words=[]),
    dict(ref=(42, 2, 19), lang='ko', en='them', words=['너희가']),
    dict(ref=(42, 2, 19), lang='ko', en='Destroy', words=['헐라']),
    dict(ref=(42, 2, 19), lang='ko', en='in', words=['동안에']),
    dict(ref=(42, 2, 19), lang='ko', en='days', words=['사흘']),
    dict(ref=(42, 2, 19), lang='ko', en='I', words=['내가']),
    dict(ref=(42, 2, 19), lang='ko', en='will', words=['일으키리라']),
    dict(ref=(42, 2, 19), lang='ko', en='it', words=['일으키리라']),

    dict(ref=(42, 2, 20), lang='ko', en='the#1', words=['유대인들이']),
    dict(ref=(42, 2, 20), lang='ko', en='Forty', words=['사십육']),
    dict(ref=(42, 2, 20), lang='ko', en='and#1', words=['사십육']),
    dict(ref=(42, 2, 20), lang='ko', en='six', words=['사십육']),
    dict(ref=(42, 2, 20), lang='ko', en='was', words=['지었거늘']),
    dict(ref=(42, 2, 20), lang='ko', en='in#1', words=['동안에#1']),
    dict(ref=(42, 2, 20), lang='ko', en='wilt', words=['일으키겠느뇨']),
    dict(ref=(42, 2, 20), lang='ko', en='it', words=['일으키겠느뇨']),
    dict(ref=(42, 2, 20), lang='ko', en='in#2', words=['동안에#2']),

    dict(ref=(42, 2, 22), lang='ko', en='therefore', words=['후에야']),
    dict(ref=(42, 2, 22), lang='ko', en='he#1', words=['살아나신']),
    dict(ref=(42, 2, 22), lang='ko', en='was', words=['살아나신']),
    dict(ref=(42, 2, 22), lang='ko', en='from', words=['가운데서']),
    dict(ref=(42, 2, 22), lang='ko', en='the#1', words=['죽은', '자']),
    dict(ref=(42, 2, 22), lang='ko', en='dead', words=['죽은', '자']),
    dict(ref=(42, 2, 22), lang='ko', en='that', words=['것을']),
    dict(ref=(42, 2, 22), lang='ko', en='had#1', words=['말씀하신']),
    dict(ref=(42, 2, 22), lang='ko', en='said#1', words=['말씀하신']),
    dict(ref=(42, 2, 22), lang='ko', en='the#2', words=['성경과']),
    dict(ref=(42, 2, 22), lang='ko', en='and#2', words=['및']),
    dict(ref=(42, 2, 22), lang='ko', en='the#3', words=['말씀을']),
    dict(ref=(42, 2, 22), lang='ko', en='word', words=['말씀을']),
    dict(ref=(42, 2, 22), lang='ko', en='which', words=['말씀을']),
    dict(ref=(42, 2, 22), lang='ko', en='had#2', words=['하신']),
    dict(ref=(42, 2, 22), lang='ko', en='said#2', words=['하신']),

    dict(ref=(42, 2, 8), lang='ko', en='Draw', words=['떠서']),
    dict(ref=(42, 2, 8), lang='ko', en='out', words=['떠서']),
    dict(ref=(42, 2, 8), lang='ko', en='bear', words=['갖다#1', '주라']),
    dict(ref=(42, 2, 8), lang='ko', en='unto#2', words=['연회장에게']),
    dict(ref=(42, 2, 8), lang='ko', en='the#1', words=['연회장에게']),
    dict(ref=(42, 2, 8), lang='ko', en='governor', words=['연회장에게']),
    dict(ref=(42, 2, 8), lang='ko', en='of', words=['연회장에게']),
    dict(ref=(42, 2, 8), lang='ko', en='the#2', words=['연회장에게']),
    dict(ref=(42, 2, 8), lang='ko', en='bare', words=['갖다#2', '주었더니']),

    dict(ref=(42, 2, 9), lang='ko', en='the#1', words=['연회장은']),
    dict(ref=(42, 2, 9), lang='ko', en='ruler', words=['연회장은']),
    dict(ref=(42, 2, 9), lang='ko', en='of#1', words=['연회장은']),
    dict(ref=(42, 2, 9), lang='ko', en='the#2', words=['연회장은']),
    dict(ref=(42, 2, 9), lang='ko', en='feast#1', words=['연회장은']),
    dict(ref=(42, 2, 9), lang='ko', en='the#3', words=['물로']),
    dict(ref=(42, 2, 9), lang='ko', en='that', words=['된']),
    dict(ref=(42, 2, 9), lang='ko', en='it', words=['났는지']),
    dict(ref=(42, 2, 9), lang='ko', en='was#2', words=['났는지']),
    dict(ref=(42, 2, 9), lang='ko', en='the#4', words=['하인들은']),
    dict(ref=(42, 2, 9), lang='ko', en='servants', words=['하인들은']),
    dict(ref=(42, 2, 9), lang='ko', en='which', words=['떠온']),
    dict(ref=(42, 2, 9), lang='ko', en='drew', words=['떠온']),
    dict(ref=(42, 2, 9), lang='ko', en='the#5', words=['물']),
    dict(ref=(42, 2, 9), lang='ko', en='water#2', words=['물']),
    dict(ref=(42, 2, 9), lang='ko', en='knew#2', words=['알더라']),
    dict(ref=(42, 2, 9), lang='ko', en='the#6', words=['연회장이']),
    dict(ref=(42, 2, 9), lang='ko', en='governor', words=['연회장이']),
    dict(ref=(42, 2, 9), lang='ko', en='of#2', words=['연회장이']),
    dict(ref=(42, 2, 9), lang='ko', en='the#7', words=['연회장이']),
    dict(ref=(42, 2, 9), lang='ko', en='feast#2', words=['연회장이']),
    dict(ref=(42, 2, 9), lang='ko', en='the#8', words=['신랑을']),

    dict(ref=(42, 2, 10), lang='ko', en='at', words=['먼저']),
    dict(ref=(42, 2, 10), lang='ko', en='the#1', words=['먼저']),
    dict(ref=(42, 2, 10), lang='ko', en='doth', words=['내고']),
    dict(ref=(42, 2, 10), lang='ko', en='set', words=['내고']),
    dict(ref=(42, 2, 10), lang='ko', en='well', words=['취한']),
    dict(ref=(42, 2, 10), lang='ko', en='is', words=['내거늘']),
    dict(ref=(42, 2, 10), lang='ko', en='worse', words=['낮은']),
    dict(ref=(42, 2, 10), lang='ko', en='thou', words=['그대는']),
    dict(ref=(42, 2, 10), lang='ko', en='hast', words=['두었도다']),
    dict(ref=(42, 2, 10), lang='ko', en='kept', words=['두었도다']),
    dict(ref=(42, 2, 10), lang='ko', en='the#2', words=['좋은#2']),
    dict(ref=(42, 2, 10), lang='ko', en='until', words=['지금까지']),

    dict(ref=(42, 2, 15), lang='ko', en='had', words=['만드사']),
    dict(ref=(42, 2, 15), lang='ko', en='made', words=['만드사']),
    dict(ref=(42, 2, 15), lang='ko', en='a', words=['채찍을']),
    dict(ref=(42, 2, 15), lang='ko', en='scourge', words=['채찍을']),
    dict(ref=(42, 2, 15), lang='ko', en='of#1', words=['노끈으로']),
    dict(ref=(42, 2, 15), lang='ko', en='small', words=['노끈으로']),
    dict(ref=(42, 2, 15), lang='ko', en='of#2', words=['성전에서']),
    dict(ref=(42, 2, 15), lang='ko', en='the#1', words=['성전에서']),
    dict(ref=(42, 2, 15), lang='ko', en='the#2', words=['양이나']),
    dict(ref=(42, 2, 15), lang='ko', en='the#3', words=['소를']),
    dict(ref=(42, 2, 15), lang='ko', en='the#4', words=['돈']),
    dict(ref=(42, 2, 15), lang='ko', en='changers', words=['바꾸는', '사람들의']),
    dict(ref=(42, 2, 15), lang='ko', en='money', words=['돈', '돈을']),
    dict(ref=(42, 2, 15), lang='ko', en='overthrew', words=['엎으시고']),
    dict(ref=(42, 2, 15), lang='ko', en='the#5', words=['상을']),

    dict(ref=(42, 2, 16), lang='ko', en='unto', words=['사람들에게']),
    dict(ref=(42, 2, 16), lang='ko', en='them', words=['사람들에게']),
    dict(ref=(42, 2, 16), lang='ko', en='that', words=['사람들에게']),
    dict(ref=(42, 2, 16), lang='ko', en='make', words=['만들지']),
    dict(ref=(42, 2, 16), lang='ko', en='s', words=['아버지의']),
    dict(ref=(42, 2, 16), lang='ko', en='an', words=['집을']),
    dict(ref=(42, 2, 16), lang='ko', en='house#2', words=['집을']),
    dict(ref=(42, 2, 16), lang='ko', en='of', words=['장사하는']),
    dict(ref=(42, 2, 16), lang='ko', en='merchandise', words=['장사하는']),

    dict(ref=(42, 2, 12), lang='ko', en='After', words=['후에']),
    dict(ref=(42, 2, 12), lang='ko', en='this', words=['그#1', '후에']),
    dict(ref=(42, 2, 12), lang='ko', en='he#1', words=['예수께서']),
    dict(ref=(42, 2, 12), lang='ko', en='he#2', words=['함께']),
    dict(ref=(42, 2, 12), lang='ko', en='and#1', words=['함께']),
    dict(ref=(42, 2, 12), lang='ko', en='his#1', words=['그#2']),
    dict(ref=(42, 2, 12), lang='ko', en='they', words=['계시지']),
    dict(ref=(42, 2, 12), lang='ko', en='continued', words=['계시지']),

    dict(ref=(42, 2, 14), lang='ko', en='the#1', words=['성전']),
    dict(ref=(42, 2, 14), lang='ko', en='those', words=['사람들과']),
    dict(ref=(42, 2, 14), lang='ko', en='that', words=['사람들과']),
    dict(ref=(42, 2, 14), lang='ko', en='the#2', words=['바꾸는']),
    dict(ref=(42, 2, 14), lang='ko', en='changers', words=['바꾸는', '사람들의']),
    dict(ref=(42, 2, 14), lang='ko', en='of', words=['돈']),
    dict(ref=(42, 2, 14), lang='ko', en='sitting', words=['앉은', '것을']),

    # ---- 마태복음 9장 ----
    dict(ref=(39, 9, 15), lang='ko', en='Can', words=['수', '있느뇨']),
    dict(ref=(39, 9, 15), lang='ko', en='the#1', words=['손님들이']),
    dict(ref=(39, 9, 15), lang='ko', en='children', words=['손님들이']),
    dict(ref=(39, 9, 15), lang='ko', en='of', words=['혼인집']),
    dict(ref=(39, 9, 15), lang='ko', en='the#2', words=['혼인집']),
    dict(ref=(39, 9, 15), lang='ko', en='bridechamber', words=['혼인집']),
    dict(ref=(39, 9, 15), lang='ko', en='as#1', words=['동안에']),
    dict(ref=(39, 9, 15), lang='ko', en='as#2', words=['동안에']),
    dict(ref=(39, 9, 15), lang='ko', en='the#3', words=['신랑과']),
    dict(ref=(39, 9, 15), lang='ko', en='bridegroom#1', words=['신랑과']),
    dict(ref=(39, 9, 15), lang='ko', en='them#2', words=['함께']),
    dict(ref=(39, 9, 15), lang='ko', en='the#4', words=['날이']),
    dict(ref=(39, 9, 15), lang='ko', en='will', words=['이르리니']),
    dict(ref=(39, 9, 15), lang='ko', en='come', words=['이르리니']),
    dict(ref=(39, 9, 15), lang='ko', en='the#5', words=['신랑을']),
    dict(ref=(39, 9, 15), lang='ko', en='bridegroom#2', words=['신랑을']),
    dict(ref=(39, 9, 15), lang='ko', en='shall#1', words=['빼앗길']),
    dict(ref=(39, 9, 15), lang='ko', en='be', words=['빼앗길']),
    dict(ref=(39, 9, 15), lang='ko', en='from', words=['빼앗길']),
    dict(ref=(39, 9, 15), lang='ko', en='them#3', words=['빼앗길']),
    dict(ref=(39, 9, 15), lang='ko', en='then', words=['그', '때에는']),
    dict(ref=(39, 9, 15), lang='ko', en='shall#2', words=['것이니라']),
    dict(ref=(39, 9, 15), lang='ko', en='they', words=['금식할']),

    # ---- 요한복음 3장 ----
    dict(ref=(42, 3, 2), lang='ko', en='The', words=['그가']),
    dict(ref=(42, 3, 2), lang='ko', en='same', words=['그가']),
    dict(ref=(42, 3, 2), lang='ko', en='to', words=['예수께']),
    dict(ref=(42, 3, 2), lang='ko', en='him#1', words=[]),
    dict(ref=(42, 3, 2), lang='ko', en='know', words=['아나이다']),
    dict(ref=(42, 3, 2), lang='ko', en='thou#1', words=['당신은']),
    dict(ref=(42, 3, 2), lang='ko', en='a', words=['선생인']),
    dict(ref=(42, 3, 2), lang='ko', en='teacher', words=['선생인']),
    dict(ref=(42, 3, 2), lang='ko', en='come', words=['오신']),
    dict(ref=(42, 3, 2), lang='ko', en='from', words=['하나님께로서']),
    dict(ref=(42, 3, 2), lang='ko', en='no', words=['없음이니이다']),
    dict(ref=(42, 3, 2), lang='ko', en='man', words=['아무라도']),
    dict(ref=(42, 3, 2), lang='ko', en='do', words=['할']),
    dict(ref=(42, 3, 2), lang='ko', en='these', words=['이', '표적을']),
    dict(ref=(42, 3, 2), lang='ko', en='miracles', words=['이', '표적을']),
    dict(ref=(42, 3, 2), lang='ko', en='that#2', words=['행하시는']),
    dict(ref=(42, 3, 2), lang='ko', en='thou#2', words=['당신의']),
    dict(ref=(42, 3, 2), lang='ko', en='doest', words=['행하시는']),
    dict(ref=(42, 3, 2), lang='ko', en='God#2', words=['하나님이']),
    dict(ref=(42, 3, 2), lang='ko', en='be', words=['함께', '하시지']),
    dict(ref=(42, 3, 2), lang='ko', en='with', words=['함께', '하시지']),
    dict(ref=(42, 3, 2), lang='ko', en='him#2', words=['함께']),

    dict(ref=(42, 3, 18), lang='ko', en='that#1', words=['자는#1']),
    dict(ref=(42, 3, 18), lang='ko', en='is#1', words=['것이요']),
    dict(ref=(42, 3, 18), lang='ko', en='not#1', words=['아니하는#1']),
    dict(ref=(42, 3, 18), lang='ko', en='condemned#1', words=['심판을#1', '받지']),
    dict(ref=(42, 3, 18), lang='ko', en='he#2', words=['자는#2']),
    dict(ref=(42, 3, 18), lang='ko', en='that#2', words=['자는#2']),
    dict(ref=(42, 3, 18), lang='ko', en='believeth#2', words=['믿지#1']),
    dict(ref=(42, 3, 18), lang='ko', en='not#2', words=['아니하는#2']),
    dict(ref=(42, 3, 18), lang='ko', en='is#2', words=['것이니라']),
    dict(ref=(42, 3, 18), lang='ko', en='condemned#2', words=['심판을#2', '받은']),
    dict(ref=(42, 3, 18), lang='ko', en='hath', words=['믿지#2']),
    dict(ref=(42, 3, 18), lang='ko', en='not#3', words=['아니하므로']),
    dict(ref=(42, 3, 18), lang='ko', en='believed', words=['믿지#2']),
    dict(ref=(42, 3, 18), lang='ko', en='in', words=['이름을']),
    dict(ref=(42, 3, 18), lang='ko', en='the#1', words=['이름을']),
    dict(ref=(42, 3, 18), lang='ko', en='of#1', words=['독생자의']),
    dict(ref=(42, 3, 18), lang='ko', en='the#2', words=['독생자의']),
    dict(ref=(42, 3, 18), lang='ko', en='of#2', words=['하나님의']),

    dict(ref=(42, 3, 26), lang='ko', en='they', words=['저희가']),
    dict(ref=(42, 3, 26), lang='ko', en='unto#1', words=['요한에게']),
    dict(ref=(42, 3, 26), lang='ko', en='unto#2', words=[]),
    dict(ref=(42, 3, 26), lang='ko', en='him#1', words=[]),
    dict(ref=(42, 3, 26), lang='ko', en='he', words=['자']),
    dict(ref=(42, 3, 26), lang='ko', en='that', words=['자']),
    dict(ref=(42, 3, 26), lang='ko', en='thee', words=['선생님과']),
    dict(ref=(42, 3, 26), lang='ko', en='Jordan', words=['요단', '강']),
    dict(ref=(42, 3, 26), lang='ko', en='to#1', words=['자']),
    dict(ref=(42, 3, 26), lang='ko', en='thou', words=['선생님이']),
    dict(ref=(42, 3, 26), lang='ko', en='barest', words=['증거하시던']),
    dict(ref=(42, 3, 26), lang='ko', en='behold', words=['곧']),
    dict(ref=(42, 3, 26), lang='ko', en='the', words=['자가']),
    dict(ref=(42, 3, 26), lang='ko', en='same', words=['자가']),
    dict(ref=(42, 3, 26), lang='ko', en='baptizeth', words=['침례를', '주매']),
    dict(ref=(42, 3, 26), lang='ko', en='come', words=['가더이다']),
    dict(ref=(42, 3, 26), lang='ko', en='to#2', words=['그에게로']),
    dict(ref=(42, 3, 26), lang='ko', en='him#2', words=['그에게로']),

    dict(ref=(42, 3, 31), lang='ko', en='He', words=['이는#1']),
    dict(ref=(42, 3, 31), lang='ko', en='that#1', words=['이는#1']),
    dict(ref=(42, 3, 31), lang='ko', en='from#1', words=['위로부터']),
    dict(ref=(42, 3, 31), lang='ko', en='above#1', words=['위로부터']),
    dict(ref=(42, 3, 31), lang='ko', en='is#1', words=['위에#1', '계시고']),
    dict(ref=(42, 3, 31), lang='ko', en='above#2', words=['위에#1', '계시고']),
    dict(ref=(42, 3, 31), lang='ko', en='all#1', words=['만물#1']),
    dict(ref=(42, 3, 31), lang='ko', en='he#1', words=['이는#2']),
    dict(ref=(42, 3, 31), lang='ko', en='that#2', words=['이는#2']),
    dict(ref=(42, 3, 31), lang='ko', en='is#2', words=['난']),
    dict(ref=(42, 3, 31), lang='ko', en='of#1', words=['땅에서']),
    dict(ref=(42, 3, 31), lang='ko', en='the#1', words=['땅에서']),
    dict(ref=(42, 3, 31), lang='ko', en='earth#1', words=['땅에서']),
    dict(ref=(42, 3, 31), lang='ko', en='is#3', words=['땅에#1', '속하여']),
    dict(ref=(42, 3, 31), lang='ko', en='earthly', words=['땅에#1', '속하여']),
    dict(ref=(42, 3, 31), lang='ko', en='speaketh', words=['것을', '말하느니라']),
    dict(ref=(42, 3, 31), lang='ko', en='of#2', words=['땅에#2']),
    dict(ref=(42, 3, 31), lang='ko', en='the#2', words=['땅에#2']),
    dict(ref=(42, 3, 31), lang='ko', en='earth#2', words=['땅에#2', '속한']),
    dict(ref=(42, 3, 31), lang='ko', en='he#2', words=['이는#3']),
    dict(ref=(42, 3, 31), lang='ko', en='that#3', words=['이는#3']),
    dict(ref=(42, 3, 31), lang='ko', en='from#2', words=['하늘로서']),
    dict(ref=(42, 3, 31), lang='ko', en='heaven', words=['하늘로서']),
    dict(ref=(42, 3, 31), lang='ko', en='is#4', words=['위에#2', '계시나니']),
    dict(ref=(42, 3, 31), lang='ko', en='above#3', words=['위에#2', '계시나니']),
    dict(ref=(42, 3, 31), lang='ko', en='all#2', words=['만물#2']),

    dict(ref=(42, 3, 3), lang='ko', en='unto#1', words=[]),
    dict(ref=(42, 3, 3), lang='ko', en='Verily', words=['진실로#1']),
    dict(ref=(42, 3, 3), lang='ko', en='verily', words=['진실로#2']),
    dict(ref=(42, 3, 3), lang='ko', en='I', words=['이르노니']),
    dict(ref=(42, 3, 3), lang='ko', en='say', words=['이르노니']),
    dict(ref=(42, 3, 3), lang='ko', en='unto#2', words=['이르노니']),
    dict(ref=(42, 3, 3), lang='ko', en='a', words=['사람이']),
    dict(ref=(42, 3, 3), lang='ko', en='man', words=['사람이']),
    dict(ref=(42, 3, 3), lang='ko', en='be', words=['거듭나지']),
    dict(ref=(42, 3, 3), lang='ko', en='born', words=['거듭나지']),
    dict(ref=(42, 3, 3), lang='ko', en='again', words=['거듭나지']),
    dict(ref=(42, 3, 3), lang='ko', en='the', words=['나라를']),
    dict(ref=(42, 3, 3), lang='ko', en='of', words=['하나님']),

    dict(ref=(42, 3, 4), lang='ko', en='can#1', words=['수#1', '있삽나이까#1']),
    dict(ref=(42, 3, 4), lang='ko', en='be#1', words=['날#1']),
    dict(ref=(42, 3, 4), lang='ko', en='born#1', words=['날#1']),
    dict(ref=(42, 3, 4), lang='ko', en='is', words=['늙으면']),
    dict(ref=(42, 3, 4), lang='ko', en='old', words=['늙으면']),
    dict(ref=(42, 3, 4), lang='ko', en='can#2', words=['수#2', '있삽나이까#2']),
    dict(ref=(42, 3, 4), lang='ko', en='the', words=['두번째']),
    dict(ref=(42, 3, 4), lang='ko', en='second', words=['두번째']),
    dict(ref=(42, 3, 4), lang='ko', en='time', words=['두번째']),
    dict(ref=(42, 3, 4), lang='ko', en='into', words=['모태에']),
    dict(ref=(42, 3, 4), lang='ko', en='his', words=['모태에']),
    dict(ref=(42, 3, 4), lang='ko', en='s', words=['모태에']),
    dict(ref=(42, 3, 4), lang='ko', en='be#2', words=['날#2']),
    dict(ref=(42, 3, 4), lang='ko', en='born#2', words=['날#2']),

    dict(ref=(42, 3, 8), lang='ko', en='The', words=['바람이']),
    dict(ref=(42, 3, 8), lang='ko', en='wind', words=['바람이']),
    dict(ref=(42, 3, 8), lang='ko', en='bloweth', words=['불매']),
    dict(ref=(42, 3, 8), lang='ko', en='it#1', words=['임의로']),
    dict(ref=(42, 3, 8), lang='ko', en='thou', words=['네가']),
    dict(ref=(42, 3, 8), lang='ko', en='the#1', words=['소리를']),
    dict(ref=(42, 3, 8), lang='ko', en='canst', words=['못하나니']),
    dict(ref=(42, 3, 8), lang='ko', en='not', words=['못하나니']),
    dict(ref=(42, 3, 8), lang='ko', en='tell', words=['알지']),
    dict(ref=(42, 3, 8), lang='ko', en='whence', words=['어디서']),
    dict(ref=(42, 3, 8), lang='ko', en='it#2', words=['오며']),
    dict(ref=(42, 3, 8), lang='ko', en='whither', words=['어디로']),
    dict(ref=(42, 3, 8), lang='ko', en='it#3', words=['가는지']),
    dict(ref=(42, 3, 8), lang='ko', en='goeth', words=['가는지']),
    dict(ref=(42, 3, 8), lang='ko', en='so', words=['이러하니라']),
    dict(ref=(42, 3, 8), lang='ko', en='is#1', words=['이러하니라']),
    dict(ref=(42, 3, 8), lang='ko', en='one', words=['사람은']),
    dict(ref=(42, 3, 8), lang='ko', en='that', words=['사람은']),
    dict(ref=(42, 3, 8), lang='ko', en='is#2', words=['난']),
    dict(ref=(42, 3, 8), lang='ko', en='born', words=['난']),
    dict(ref=(42, 3, 8), lang='ko', en='of', words=['성령으로']),
    dict(ref=(42, 3, 8), lang='ko', en='the#2', words=['성령으로']),
    dict(ref=(42, 3, 8), lang='ko', en='Spirit', words=['성령으로']),

    dict(ref=(42, 3, 19), lang='ko', en='is#1', words=['것이니라']),
    dict(ref=(42, 3, 19), lang='ko', en='the#1', words=['그']),
    dict(ref=(42, 3, 19), lang='ko', en='that', words=['곧']),
    dict(ref=(42, 3, 19), lang='ko', en='is#2', words=['왔으되']),
    dict(ref=(42, 3, 19), lang='ko', en='into', words=['세상에']),
    dict(ref=(42, 3, 19), lang='ko', en='the#2', words=['세상에']),
    dict(ref=(42, 3, 19), lang='ko', en='rather', words=['빛보다', '더']),
    dict(ref=(42, 3, 19), lang='ko', en='than', words=['빛보다']),
    dict(ref=(42, 3, 19), lang='ko', en='light#2', words=['빛보다']),
    dict(ref=(42, 3, 19), lang='ko', en='were', words=['악하므로']),

    dict(ref=(42, 3, 34), lang='ko', en='he', words=['이는#1']),
    dict(ref=(42, 3, 34), lang='ko', en='whom', words=['이는#1']),
    dict(ref=(42, 3, 34), lang='ko', en='God#1', words=['하나님의#1']),
    dict(ref=(42, 3, 34), lang='ko', en='hath', words=['보내신']),
    dict(ref=(42, 3, 34), lang='ko', en='speaketh', words=['하나니']),
    dict(ref=(42, 3, 34), lang='ko', en='the#1', words=['하나님의#2', '말씀을']),
    dict(ref=(42, 3, 34), lang='ko', en='words', words=['하나님의#2', '말씀을']),
    dict(ref=(42, 3, 34), lang='ko', en='of', words=['하나님의#2']),
    dict(ref=(42, 3, 34), lang='ko', en='God#2', words=['하나님의#2']),
    dict(ref=(42, 3, 34), lang='ko', en='for', words=['이는#2']),
    dict(ref=(42, 3, 34), lang='ko', en='God#3', words=['하나님이']),
    dict(ref=(42, 3, 34), lang='ko', en='giveth', words=['주심이니라']),
    dict(ref=(42, 3, 34), lang='ko', en='not', words=['없이']),
    dict(ref=(42, 3, 34), lang='ko', en='the#2', words=['성령을']),
    dict(ref=(42, 3, 34), lang='ko', en='by', words=['한량']),
    dict(ref=(42, 3, 34), lang='ko', en='unto', words=['주심이니라']),
    dict(ref=(42, 3, 34), lang='ko', en='him', words=['주심이니라']),

    dict(ref=(42, 3, 36), lang='ko', en='on#1', words=['아들을#1']),
    dict(ref=(42, 3, 36), lang='ko', en='the#1', words=['아들을#1']),
    dict(ref=(42, 3, 36), lang='ko', en='hath', words=['있고']),
    dict(ref=(42, 3, 36), lang='ko', en='everlasting', words=['영생이']),
    dict(ref=(42, 3, 36), lang='ko', en='life#1', words=['영생이']),
    dict(ref=(42, 3, 36), lang='ko', en='he', words=['자는#2']),
    dict(ref=(42, 3, 36), lang='ko', en='that#2', words=['자는#2']),
    dict(ref=(42, 3, 36), lang='ko', en='believeth#2', words=['순종치']),
    dict(ref=(42, 3, 36), lang='ko', en='not#1', words=['아니하는']),
    dict(ref=(42, 3, 36), lang='ko', en='the#2', words=['아들을#2']),
    dict(ref=(42, 3, 36), lang='ko', en='shall', words=['보지']),
    dict(ref=(42, 3, 36), lang='ko', en='not#2', words=['못하고']),
    dict(ref=(42, 3, 36), lang='ko', en='life#2', words=['영생을']),
    dict(ref=(42, 3, 36), lang='ko', en='the#3', words=['하나님의']),
    dict(ref=(42, 3, 36), lang='ko', en='of', words=['하나님의']),
    dict(ref=(42, 3, 36), lang='ko', en='abideth', words=['머물러', '있느니라']),

    dict(ref=(42, 3, 6), lang='ko', en='That', words=['것은#1']),
    dict(ref=(42, 3, 6), lang='ko', en='which#1', words=['것은#1']),
    dict(ref=(42, 3, 6), lang='ko', en='is#1', words=['난#1']),
    dict(ref=(42, 3, 6), lang='ko', en='born#1', words=['난#1']),
    dict(ref=(42, 3, 6), lang='ko', en='of#1', words=['육으로']),
    dict(ref=(42, 3, 6), lang='ko', en='the#1', words=['육으로']),
    dict(ref=(42, 3, 6), lang='ko', en='flesh#1', words=['육으로']),
    dict(ref=(42, 3, 6), lang='ko', en='is#2', words=['육이요']),
    dict(ref=(42, 3, 6), lang='ko', en='flesh#2', words=['육이요']),
    dict(ref=(42, 3, 6), lang='ko', en='that', words=['것은#2']),
    dict(ref=(42, 3, 6), lang='ko', en='which#2', words=['것은#2']),
    dict(ref=(42, 3, 6), lang='ko', en='is#3', words=['난#2']),
    dict(ref=(42, 3, 6), lang='ko', en='born#2', words=['난#2']),
    dict(ref=(42, 3, 6), lang='ko', en='of#2', words=['성령으로']),
    dict(ref=(42, 3, 6), lang='ko', en='the#2', words=['성령으로']),
    dict(ref=(42, 3, 6), lang='ko', en='Spirit', words=['성령으로']),
    dict(ref=(42, 3, 6), lang='ko', en='is#4', words=['영이니']),
    dict(ref=(42, 3, 6), lang='ko', en='spirit', words=['영이니']),

    dict(ref=(42, 3, 20), lang='ko', en='the#1', words=['빛을']),
    dict(ref=(42, 3, 20), lang='ko', en='light#1', words=['빛을']),
    dict(ref=(42, 3, 20), lang='ko', en='neither', words=['아니하나니']),
    dict(ref=(42, 3, 20), lang='ko', en='to', words=['빛으로']),
    dict(ref=(42, 3, 20), lang='ko', en='the#2', words=['빛으로']),
    dict(ref=(42, 3, 20), lang='ko', en='light#2', words=['빛으로']),
    dict(ref=(42, 3, 20), lang='ko', en='lest', words=['함이요']),
    dict(ref=(42, 3, 20), lang='ko', en='be', words=['드러날까']),
    dict(ref=(42, 3, 20), lang='ko', en='reproved', words=['드러날까']),

    dict(ref=(42, 3, 27), lang='ko', en='A', words=['사람이']),
    dict(ref=(42, 3, 27), lang='ko', en='nothing', words=['아무', '것도', '없느니라']),
    dict(ref=(42, 3, 27), lang='ko', en='except', words=['만일', '아니면']),
    dict(ref=(42, 3, 27), lang='ko', en='it', words=['주신바']),
    dict(ref=(42, 3, 27), lang='ko', en='be', words=['주신바']),
    dict(ref=(42, 3, 27), lang='ko', en='given', words=['주신바']),
    dict(ref=(42, 3, 27), lang='ko', en='from', words=['하늘에서']),

    dict(ref=(42, 3, 17), lang='ko', en='not', words=['아니요']),
    dict(ref=(42, 3, 17), lang='ko', en='his', words=['그']),
    dict(ref=(42, 3, 17), lang='ko', en='sent', words=['보내신', '것은']),
    dict(ref=(42, 3, 17), lang='ko', en='the#1', words=['세상에']),
    dict(ref=(42, 3, 17), lang='ko', en='world#1', words=['세상에']),
    dict(ref=(42, 3, 17), lang='ko', en='to', words=['심판하려']),
    dict(ref=(42, 3, 17), lang='ko', en='the#2', words=['세상을']),
    dict(ref=(42, 3, 17), lang='ko', en='world#2', words=['세상을']),
    dict(ref=(42, 3, 17), lang='ko', en='the#3', words=['세상이']),
    dict(ref=(42, 3, 17), lang='ko', en='world#3', words=['세상이']),
    dict(ref=(42, 3, 17), lang='ko', en='him', words=['저로']),
    dict(ref=(42, 3, 17), lang='ko', en='might', words=['하려', '하심이라']),

    dict(ref=(42, 3, 11), lang='ko', en='Verily', words=['진실로#1']),
    dict(ref=(42, 3, 11), lang='ko', en='verily', words=['진실로#2']),
    dict(ref=(42, 3, 11), lang='ko', en='I', words=['이르노니']),
    dict(ref=(42, 3, 11), lang='ko', en='say', words=['이르노니']),
    dict(ref=(42, 3, 11), lang='ko', en='unto', words=['이르노니']),
    dict(ref=(42, 3, 11), lang='ko', en='thee', words=['네게']),
    dict(ref=(42, 3, 11), lang='ko', en='We', words=['말하고']),
    dict(ref=(42, 3, 11), lang='ko', en='that#1', words=['것을#1']),
    dict(ref=(42, 3, 11), lang='ko', en='we#1', words=['우리#1', '아는']),
    dict(ref=(42, 3, 11), lang='ko', en='testify', words=['증거하노라']),
    dict(ref=(42, 3, 11), lang='ko', en='that#2', words=['것을#2']),
    dict(ref=(42, 3, 11), lang='ko', en='we#2', words=['본']),
    dict(ref=(42, 3, 11), lang='ko', en='and#2', words=['그러나']),
    dict(ref=(42, 3, 11), lang='ko', en='ye', words=['그러나', '너희가']),
    dict(ref=(42, 3, 11), lang='ko', en='receive', words=['받지']),
    dict(ref=(42, 3, 11), lang='ko', en='not', words=['아니하는도다']),
    dict(ref=(42, 3, 11), lang='ko', en='our', words=['우리#2', '증거를']),
    dict(ref=(42, 3, 11), lang='ko', en='witness', words=['우리#2', '증거를']),

    dict(ref=(42, 3, 23), lang='ko', en='was#1', words=['주니']),
    dict(ref=(42, 3, 23), lang='ko', en='baptizing', words=['침례를#1', '주니']),
    dict(ref=(42, 3, 23), lang='ko', en='in', words=['애논에서']),
    dict(ref=(42, 3, 23), lang='ko', en='to', words=['살렘']),
    dict(ref=(42, 3, 23), lang='ko', en='Salim', words=['살렘']),
    dict(ref=(42, 3, 23), lang='ko', en='there#1', words=['많음이라']),
    dict(ref=(42, 3, 23), lang='ko', en='was#2', words=['많음이라']),
    dict(ref=(42, 3, 23), lang='ko', en='much', words=['많음이라']),
    dict(ref=(42, 3, 23), lang='ko', en='they', words=['사람들이']),
    dict(ref=(42, 3, 23), lang='ko', en='were', words=['침례를#2', '받더라']),
    dict(ref=(42, 3, 23), lang='ko', en='baptized', words=['침례를#2', '받더라']),

    dict(ref=(42, 3, 28), lang='ko', en='Ye', words=['자는', '너희니라']),
    dict(ref=(42, 3, 28), lang='ko', en='said', words=['말한', '바']),
    dict(ref=(42, 3, 28), lang='ko', en='that#1', words=['것을']),
    dict(ref=(42, 3, 28), lang='ko', en='am#1', words=['아니요']),
    dict(ref=(42, 3, 28), lang='ko', en='the', words=['그리스도가']),
    dict(ref=(42, 3, 28), lang='ko', en='that#2', words=['자라고']),
    dict(ref=(42, 3, 28), lang='ko', en='I#3', words=['한']),
    dict(ref=(42, 3, 28), lang='ko', en='am#2', words=['한']),
    dict(ref=(42, 3, 28), lang='ko', en='sent', words=['보내심을', '받은']),

    dict(ref=(42, 3, 29), lang='ko', en='He', words=['자는']),
    dict(ref=(42, 3, 29), lang='ko', en='that', words=['자는']),
    dict(ref=(42, 3, 29), lang='ko', en='hath', words=['취하는']),
    dict(ref=(42, 3, 29), lang='ko', en='the#1', words=['신부를']),
    dict(ref=(42, 3, 29), lang='ko', en='is#1', words=['신랑이나']),
    dict(ref=(42, 3, 29), lang='ko', en='the#2', words=['신랑이나']),
    dict(ref=(42, 3, 29), lang='ko', en='bridegroom#1', words=['신랑이나']),
    dict(ref=(42, 3, 29), lang='ko', en='the#3', words=['친구가']),
    dict(ref=(42, 3, 29), lang='ko', en='of#1', words=['신랑의']),
    dict(ref=(42, 3, 29), lang='ko', en='the#4', words=['신랑의']),
    dict(ref=(42, 3, 29), lang='ko', en='bridegroom#2', words=['신랑의']),
    dict(ref=(42, 3, 29), lang='ko', en='which', words=['서서']),
    dict(ref=(42, 3, 29), lang='ko', en='him', words=['신랑의']),
    dict(ref=(42, 3, 29), lang='ko', en='rejoiceth', words=['기뻐하나니']),
    dict(ref=(42, 3, 29), lang='ko', en='because', words=['기뻐하나니']),
    dict(ref=(42, 3, 29), lang='ko', en='of#2', words=['신랑의']),
    dict(ref=(42, 3, 29), lang='ko', en='the#5', words=['신랑의']),
    dict(ref=(42, 3, 29), lang='ko', en='bridegroom#3', words=['신랑의']),
    dict(ref=(42, 3, 29), lang='ko', en='s', words=['신랑의']),
    dict(ref=(42, 3, 29), lang='ko', en='joy', words=['기쁨이']),
    dict(ref=(42, 3, 29), lang='ko', en='therefore', words=['충만하였노라']),
    dict(ref=(42, 3, 29), lang='ko', en='is#2', words=['충만하였노라']),

    # ---- 요한복음 4장 ----
    dict(ref=(42, 4, 2), lang='ko', en='Though', words=['것이']),
    dict(ref=(42, 4, 2), lang='ko', en='baptized', words=['침례를', '주신', '준']),
    dict(ref=(42, 4, 2), lang='ko', en='not', words=['아니요']),
    dict(ref=(42, 4, 2), lang='ko', en='but', words=['것이라']),
    dict(ref=(42, 4, 2), lang='ko', en='his', words=['제자들이']),

    # ---- Jews ↔ 유대인 끊어진 곳 (성경 전체 점검) ----
    dict(ref=(42, 4, 9), lang='ko', en='Jews', words=['유대인이']),
    dict(ref=(42, 4, 9), lang='ko', en='dealings', words=['상종치']),
    dict(ref=(42, 4, 9), lang='ko', en='no', words=['아니함이러라']),

    dict(ref=(42, 7, 1), lang='ko', en='Jewry', words=['유대에서']),
    dict(ref=(42, 7, 1), lang='ko', en='the', words=['유대인들이']),
    dict(ref=(42, 7, 1), lang='ko', en='Jews', words=['유대인들이']),
    dict(ref=(42, 7, 1), lang='ko', en='walk', words=['다니려']),
    dict(ref=(42, 7, 1), lang='ko', en='not', words=['아니하심은']),

    dict(ref=(42, 18, 35), lang='ko', en='a', words=['유대인이냐']),
    dict(ref=(42, 18, 35), lang='ko', en='Jew', words=['유대인이냐']),
    dict(ref=(42, 18, 35), lang='ko', en='own', words=['사람과']),
    dict(ref=(42, 18, 35), lang='ko', en='thou', words=['네가']),

    dict(ref=(43, 6, 1), lang='ko', en='the#3', words=['유대인들이']),
    dict(ref=(43, 6, 1), lang='ko', en='Grecians', words=['헬라파', '유대인들이']),
    dict(ref=(43, 6, 1), lang='ko', en='the#4', words=['히브리파']),
    dict(ref=(43, 6, 1), lang='ko', en='Hebrews', words=['히브리파', '사람을']),
    dict(ref=(43, 6, 1), lang='ko', en='those', words=['그#1']),
    dict(ref=(43, 6, 1), lang='ko', en='ministration', words=['구제에']),
    dict(ref=(43, 6, 1), lang='ko', en='neglected', words=['빠지므로']),
    dict(ref=(43, 6, 1), lang='ko', en='multiplied', words=['많아졌는데']),
    dict(ref=(43, 6, 1), lang='ko', en='there', words=['더']),

    dict(ref=(43, 9, 29), lang='ko', en='the#2', words=['유대인들과']),
    dict(ref=(43, 9, 29), lang='ko', en='Grecians', words=['헬라파', '유대인들과']),
    dict(ref=(43, 9, 29), lang='ko', en='of', words=['이름으로']),
    dict(ref=(43, 9, 29), lang='ko', en='they', words=['사람들이']),
    dict(ref=(43, 9, 29), lang='ko', en='went', words=['힘쓰거늘']),
    dict(ref=(43, 9, 29), lang='ko', en='about', words=['힘쓰거늘']),
    dict(ref=(43, 9, 29), lang='ko', en='against', words=['함께']),
    dict(ref=(43, 9, 29), lang='ko', en='disputed', words=['말하며', '변론하니']),

    dict(ref=(43, 18, 2), lang='ko', en='Jew', words=['유대인']),
    dict(ref=(43, 18, 2), lang='ko', en='Jews', words=['유대인을']),
    dict(ref=(43, 18, 2), lang='ko', en='named', words=['하는']),
    dict(ref=(43, 18, 2), lang='ko', en='born', words=['난']),
    dict(ref=(43, 18, 2), lang='ko', en='certain', words=['하나를']),
    dict(ref=(43, 18, 2), lang='ko', en='depart', words=['떠나라']),
    dict(ref=(43, 18, 2), lang='ko', en='because', words=['고로']),
    dict(ref=(43, 18, 2), lang='ko', en='lately', words=['새로']),
    dict(ref=(43, 18, 2), lang='ko', en='come', words=['온지라']),
    dict(ref=(43, 18, 2), lang='ko', en='them', words=['그들에게']),
    dict(ref=(43, 18, 2), lang='ko', en='came', words=['가매']),

    dict(ref=(43, 18, 14), lang='ko', en='Jews#1', words=['유대인들에게']),
    dict(ref=(43, 18, 14), lang='ko', en='ye', words=['너희#1']),
    dict(ref=(43, 18, 14), lang='ko', en='Jews#2', words=['유대인들아']),
    dict(ref=(43, 18, 14), lang='ko', en='wrong', words=['부정한']),
    dict(ref=(43, 18, 14), lang='ko', en='wicked', words=['괴악한']),
    dict(ref=(43, 18, 14), lang='ko', en='lewdness', words=['행동이었으면']),
    dict(ref=(43, 18, 14), lang='ko', en='you', words=['너희#2']),
    dict(ref=(43, 18, 14), lang='ko', en='bear', words=['들어주는']),
    dict(ref=(43, 18, 14), lang='ko', en='would', words=['것이', '가하거니와']),

    dict(ref=(43, 19, 34), lang='ko', en='a', words=['유대인인']),
    dict(ref=(43, 19, 34), lang='ko', en='Jew', words=['유대인인']),
    dict(ref=(43, 19, 34), lang='ko', en='of#2', words=['사람의']),
    dict(ref=(43, 19, 34), lang='ko', en='was', words=['하더니']),

    dict(ref=(43, 23, 28), lang='ko', en='they', words=['유대인들이']),
    dict(ref=(43, 23, 28), lang='ko', en='the', words=['무슨']),
    dict(ref=(43, 23, 28), lang='ko', en='cause', words=['일로']),
    dict(ref=(43, 23, 28), lang='ko', en='him#1', words=['그를']),
    dict(ref=(43, 23, 28), lang='ko', en='forth', words=['내려갔더니']),

    dict(ref=(45, 9, 20), lang='ko', en='the#1', words=['유대인들에게는']),
    dict(ref=(45, 9, 20), lang='ko', en='Jews#1', words=['유대인들에게는']),
    dict(ref=(45, 9, 20), lang='ko', en='a', words=['유대인과']),
    dict(ref=(45, 9, 20), lang='ko', en='Jew', words=['유대인과']),
    dict(ref=(45, 9, 20), lang='ko', en='the#2', words=['유대인들을']),
    dict(ref=(45, 9, 20), lang='ko', en='Jews#2', words=['유대인들을']),
    dict(ref=(45, 9, 20), lang='ko', en='gain#1', words=['얻고자#1']),
    dict(ref=(45, 9, 20), lang='ko', en='gain#2', words=['얻고자#2']),

    dict(ref=(47, 2, 14), lang='ko', en='But', words=['그러므로']),
    dict(ref=(47, 2, 14), lang='ko', en='walked', words=['행하지']),
    dict(ref=(47, 2, 14), lang='ko', en='uprightly', words=['바로']),
    dict(ref=(47, 2, 14), lang='ko', en='I#2', words=['이르되']),
    dict(ref=(47, 2, 14), lang='ko', en='said', words=['이르되']),
    dict(ref=(47, 2, 14), lang='ko', en='livest', words=['좇고']),
    dict(ref=(47, 2, 14), lang='ko', en='after', words=['좇고']),
    dict(ref=(47, 2, 14), lang='ko', en='manner', words=['좇고']),
    dict(ref=(47, 2, 14), lang='ko', en='of#2', words=['이방을']),
    dict(ref=(47, 2, 14), lang='ko', en='Gentiles#1', words=['이방을']),
    dict(ref=(47, 2, 14), lang='ko', en='not#2', words=['아니하면서']),
    dict(ref=(47, 2, 14), lang='ko', en='as#1', words=['유대인답게#1']),
    dict(ref=(47, 2, 14), lang='ko', en='do#1', words=['살지']),
    dict(ref=(47, 2, 14), lang='ko', en='the#5', words=['유대인답게#1']),
    dict(ref=(47, 2, 14), lang='ko', en='Jews#1', words=['유대인답게#1']),
    dict(ref=(47, 2, 14), lang='ko', en='compellest', words=['억지로', '하려느냐']),
    dict(ref=(47, 2, 14), lang='ko', en='the#4', words=['이방인을']),
    dict(ref=(47, 2, 14), lang='ko', en='Gentiles#2', words=['이방인을']),
    dict(ref=(47, 2, 14), lang='ko', en='to#2', words=['살게']),
    dict(ref=(47, 2, 14), lang='ko', en='live', words=['살게']),
    dict(ref=(47, 2, 14), lang='ko', en='as#2', words=['유대인답게#2']),
    dict(ref=(47, 2, 14), lang='ko', en='do#2', words=['유대인답게#2']),
    dict(ref=(47, 2, 14), lang='ko', en='the#6', words=['유대인답게#2']),
    dict(ref=(47, 2, 14), lang='ko', en='Jews#2', words=['유대인답게#2']),

    dict(ref=(51, 2, 14), lang='ko', en='the#2', words=['유대인들에게']),
    dict(ref=(51, 2, 14), lang='ko', en='Jews', words=['유대인들에게']),
    dict(ref=(51, 2, 14), lang='ko', en='followers', words=['본받은', '자']),
    dict(ref=(51, 2, 14), lang='ko', en='also', words=['너희도']),
    dict(ref=(51, 2, 14), lang='ko', en='your', words=['너희']),
    dict(ref=(51, 2, 14), lang='ko', en='own', words=['나라']),
    dict(ref=(51, 2, 14), lang='ko', en='countrymen', words=['사람들에게']),
    dict(ref=(51, 2, 14), lang='ko', en='like', words=['동일한']),
    dict(ref=(51, 2, 14), lang='ko', en='have#1', words=['받았느니라']),

    dict(ref=(51, 2, 15), lang='ko', en='Who', words=['유대인은']),
    dict(ref=(51, 2, 15), lang='ko', en='persecuted', words=['쫓아내고']),
    dict(ref=(51, 2, 15), lang='ko', en='contrary', words=['대적이']),

    dict(ref=(55, 1, 14), lang='ko', en='Jewish', words=['유대인의']),
    dict(ref=(55, 1, 14), lang='ko', en='fables', words=['허탄한', '이야기와']),
    dict(ref=(55, 1, 14), lang='ko', en='turn', words=['배반하는']),
    dict(ref=(55, 1, 14), lang='ko', en='from', words=['배반하는']),

    dict(ref=(65, 2, 9), lang='ko', en='Jews', words=['유대인이라', '유대인이']),
    dict(ref=(65, 2, 9), lang='ko', en='say', words=['자칭', '하는']),
    dict(ref=(65, 2, 9), lang='ko', en='but#1', words=['실상은#1']),
    dict(ref=(65, 2, 9), lang='ko', en='thou', words=['네가']),
    dict(ref=(65, 2, 9), lang='ko', en='but#2', words=['실상은#2']),
    dict(ref=(65, 2, 9), lang='ko', en='the#2', words=['회라']),
    dict(ref=(65, 2, 9), lang='ko', en='synagogue', words=['회라']),

    dict(ref=(42, 4, 23), lang='ko', en='the#1', words=['때가']),
    dict(ref=(42, 4, 23), lang='ko', en='hour', words=['때가']),
    dict(ref=(42, 4, 23), lang='ko', en='and#1', words=['곧']),
    dict(ref=(42, 4, 23), lang='ko', en='now', words=['이']),
    dict(ref=(42, 4, 23), lang='ko', en='is', words=['때라']),
    dict(ref=(42, 4, 23), lang='ko', en='the#2', words=['예배하는#1']),
    dict(ref=(42, 4, 23), lang='ko', en='true', words=['참으로']),
    dict(ref=(42, 4, 23), lang='ko', en='worshippers', words=['예배하는#1', '자들은']),
    dict(ref=(42, 4, 23), lang='ko', en='shall', words=['예배할']),
    dict(ref=(42, 4, 23), lang='ko', en='worship#1', words=['예배할']),
    dict(ref=(42, 4, 23), lang='ko', en='the#3', words=['아버지께']),
    dict(ref=(42, 4, 23), lang='ko', en='Father#1', words=['아버지께']),
    dict(ref=(42, 4, 23), lang='ko', en='in#1', words=['신령과']),
    dict(ref=(42, 4, 23), lang='ko', en='spirit', words=['신령과']),
    dict(ref=(42, 4, 23), lang='ko', en='in#2', words=['진정으로']),
    dict(ref=(42, 4, 23), lang='ko', en='truth', words=['진정으로']),
    dict(ref=(42, 4, 23), lang='ko', en='for', words=['찾으시느니라']),
    dict(ref=(42, 4, 23), lang='ko', en='the#4', words=['아버지께서는']),
    dict(ref=(42, 4, 23), lang='ko', en='Father#2', words=['아버지께서는']),
    dict(ref=(42, 4, 23), lang='ko', en='seeketh', words=['찾으시느니라']),
    dict(ref=(42, 4, 23), lang='ko', en='such', words=['이렇게', '자들을']),
    dict(ref=(42, 4, 23), lang='ko', en='to', words=['예배하는#2']),
    dict(ref=(42, 4, 23), lang='ko', en='worship#2', words=['예배하는#2']),

    # ---- 인자·바리새인이 한국어에서 한 번 더 반복되는 절 ----
    dict(ref=(42, 6, 27), lang='ko', en='him', words=['인자는']),
    dict(ref=(42, 6, 27), lang='ko', en='Labour', words=['일하지', '하라']),
    dict(ref=(42, 6, 27), lang='ko', en='perisheth', words=['썩는']),
    dict(ref=(42, 6, 27), lang='ko', en='for#2', words=['위하여#2']),
    dict(ref=(42, 6, 27), lang='ko', en='that', words=['이']),
    dict(ref=(42, 6, 27), lang='ko', en='meat#2', words=['양식은']),
    dict(ref=(42, 6, 27), lang='ko', en='sealed', words=['인치신']),

    dict(ref=(42, 6, 53), lang='ko', en='his', words=['인자의#2']),
    dict(ref=(42, 6, 53), lang='ko', en='say', words=['이르노니']),
    dict(ref=(42, 6, 53), lang='ko', en='Except', words=['아니하고', '아니하면']),

    dict(ref=(42, 13, 31), lang='ko', en='him', words=['인자를']),
    dict(ref=(42, 13, 31), lang='ko', en='he', words=['저가']),
    dict(ref=(42, 13, 31), lang='ko', en='glorified#1', words=['영광을#1', '얻었고']),
    dict(ref=(42, 13, 31), lang='ko', en='glorified#2', words=['영광을#2', '얻으셨도다']),

    dict(ref=(43, 23, 6), lang='ko', en='Pharisees', words=['바리새인인']),
    dict(ref=(43, 23, 6), lang='ko', en='Pharisee#1', words=['바리새인이요']),
    dict(ref=(43, 23, 6), lang='ko', en='Pharisee#2', words=['바리새인의']),
    dict(ref=(43, 23, 6), lang='ko', en='the#2', words=['한#2', '부분은#2']),
    dict(ref=(43, 23, 6), lang='ko', en='other', words=['한#2', '부분은#2']),
    dict(ref=(43, 23, 6), lang='ko', en='dead', words=['죽은', '자의']),
    dict(ref=(43, 23, 6), lang='ko', en='question', words=['심문을']),

    # ---- 어머니·어미 끊어진 곳 (성경 전체 점검) ----
    dict(ref=(6, 17, 2), lang='ko', en='thee', words=['어머니께서']),
    dict(ref=(6, 17, 2), lang='ko', en='thou#1', words=['어머니께서']),

    dict(ref=(7, 1, 10), lang='ko', en='thee', words=['어머니와']),
    dict(ref=(7, 1, 10), lang='ko', en='thy', words=['어머니의']),

    dict(ref=(7, 1, 16), lang='ko', en='thee#1', words=['어머니를#1']),
    dict(ref=(7, 1, 16), lang='ko', en='thee#2', words=['어머니를#2']),
    dict(ref=(7, 1, 16), lang='ko', en='thou#1', words=['어머니께서#1']),
    dict(ref=(7, 1, 16), lang='ko', en='thou#2', words=['어머니께서#2']),
    dict(ref=(7, 1, 16), lang='ko', en='thy#1', words=['어머니의#1']),
    dict(ref=(7, 1, 16), lang='ko', en='thy#2', words=['어머니의#2']),

    dict(ref=(7, 1, 17), lang='ko', en='thou', words=['어머니께서']),
    dict(ref=(7, 1, 17), lang='ko', en='thee', words=['어머니와']),

    dict(ref=(7, 3, 5), lang='ko', en='thou', words=['어머니의']),

    dict(ref=(10, 2, 20), lang='ko', en='mother', words=['어머니여']),
    dict(ref=(10, 2, 20), lang='ko', en='thee#3', words=['어머니의']),

    dict(ref=(39, 27, 56), lang='ko', en='mother#1', words=['어머니']),
    dict(ref=(39, 27, 56), lang='ko', en='mother#2', words=['어머니도']),

    dict(ref=(44, 16, 13), lang='ko', en='mother', words=['어머니에게', '어머니는']),
    dict(ref=(44, 16, 13), lang='ko', en='mine', words=['어머니니라']),

    dict(ref=(40, 6, 24), lang='ko', en='she#2', words=['어미가']),

    dict(ref=(41, 12, 53), lang='ko', en='mother#1', words=['어미가']),
    dict(ref=(41, 12, 53), lang='ko', en='mother#2', words=['어미와']),
    dict(ref=(41, 12, 53), lang='ko', en='mother#3', words=['시어미가']),
    dict(ref=(41, 12, 53), lang='ko', en='in#1', words=['시어미가']),
    dict(ref=(41, 12, 53), lang='ko', en='law#1', words=['시어미가']),
    dict(ref=(41, 12, 53), lang='ko', en='mother#4', words=['시어미와']),
    dict(ref=(41, 12, 53), lang='ko', en='in#4', words=['시어미와']),
    dict(ref=(41, 12, 53), lang='ko', en='law#4', words=['시어미와']),
    dict(ref=(41, 12, 53), lang='ko', en='daughter#1', words=['딸과']),
    dict(ref=(41, 12, 53), lang='ko', en='daughter#2', words=['딸이']),
    dict(ref=(41, 12, 53), lang='ko', en='daughter#3', words=['며느리와']),
    dict(ref=(41, 12, 53), lang='ko', en='in#2', words=['며느리와']),
    dict(ref=(41, 12, 53), lang='ko', en='law#2', words=['며느리와']),
    dict(ref=(41, 12, 53), lang='ko', en='daughter#4', words=['며느리가']),
    dict(ref=(41, 12, 53), lang='ko', en='in#3', words=['며느리가']),
    dict(ref=(41, 12, 53), lang='ko', en='law#3', words=['며느리가']),

    dict(ref=(2, 22, 28), lang='ko', en='it#2', words=['어미와']),
    dict(ref=(4, 22, 6), lang='ko', en='dam#1', words=['어미새가']),
    dict(ref=(4, 22, 6), lang='ko', en='dam#2', words=['어미새와']),
    dict(ref=(10, 3, 26), lang='ko', en='whose', words=['어미되는']),
    dict(ref=(10, 3, 26), lang='ko', en='was', words=['어미되는']),
    dict(ref=(11, 4, 21), lang='ko', en='she', words=['어미가']),
    dict(ref=(11, 8, 5), lang='ko', en='woman#1', words=['어미가']),
    dict(ref=(17, 3, 11), lang='ko', en='belly', words=['어미가']),
    dict(ref=(17, 24, 9), lang='ko', en='breast', words=['어미']),
    dict(ref=(19, 17, 25), lang='ko', en='her', words=['어미의']),
    dict(ref=(19, 17, 25), lang='ko', en='bare', words=['어미의']),
    dict(ref=(22, 45, 10), lang='ko', en='the', words=['어미에게']),
    dict(ref=(22, 45, 10), lang='ko', en='woman', words=['어미에게']),

    # ---- 선지자 끊어진 곳 (성경 전체 점검) ----
    dict(ref=(11, 17, 13), lang='ko', en='prophets#1', words=['선지자와']),
    dict(ref=(13, 24, 19), lang='ko', en='prophets', words=['선지자를']),
    dict(ref=(13, 24, 19), lang='ko', en='they#1', words=['선지자들이']),
    dict(ref=(13, 25, 16), lang='ko', en='he', words=['선지자가#1']),
    dict(ref=(13, 25, 16), lang='ko', en='prophet', words=['선지자가#2']),
    dict(ref=(13, 29, 25), lang='ko', en='prophet', words=['선지자']),
    dict(ref=(23, 23, 15), lang='ko', en='prophets#1', words=['선지자에']),
    dict(ref=(23, 28, 5), lang='ko', en='prophet#1', words=['선지자#1']),
    dict(ref=(23, 28, 5), lang='ko', en='prophet#2', words=['선지자#2']),
    dict(ref=(23, 28, 9), lang='ko', en='prophet#1', words=['선지자는']),
    dict(ref=(23, 28, 9), lang='ko', en='prophet#2', words=['예언자의']),
    dict(ref=(23, 28, 9), lang='ko', en='prophet#3', words=['선지자로']),
    dict(ref=(23, 28, 12), lang='ko', en='prophet#1', words=['예레미야에게']),
    dict(ref=(23, 28, 12), lang='ko', en='prophet#2', words=['선지자#1']),
    dict(ref=(23, 28, 12), lang='ko', en='prophet#3', words=['선지자#2']),
    dict(ref=(23, 29, 1), lang='ko', en='prophet', words=['선지자']),
    dict(ref=(25, 13, 5), lang='ko', en='Ye', words=['너희', '선지자들이']),
    dict(ref=(27, 11, 2), lang='ko', en='they#1', words=['선지자들이']),
    dict(ref=(27, 12, 10), lang='ko', en='prophets#1', words=['선지자에게']),
    dict(ref=(27, 12, 10), lang='ko', en='prophets#2', words=['선지자들을']),
    dict(ref=(32, 3, 5), lang='ko', en='prophets', words=['선지자는', '선지자에']),
    dict(ref=(43, 13, 27), lang='ko', en='prophets', words=['선지자들의#1']),
    dict(ref=(43, 13, 27), lang='ko', en='them', words=['선지자들의#2', '말을#2']),

    # ---- 히브리서 1장 ----
    dict(ref=(57, 1, 2), lang='ko', en='these', words=['이#1', '모든#1']),
    dict(ref=(57, 1, 2), lang='ko', en='last', words=['마지막에']),
    dict(ref=(57, 1, 2), lang='ko', en='days', words=['날']),
    dict(ref=(57, 1, 2), lang='ko', en='by#1', words=['아들로']),
    dict(ref=(57, 1, 2), lang='ko', en='whom#1', words=['이#2', '아들을']),
    dict(ref=(57, 1, 2), lang='ko', en='he#1', words=['세우시고']),
    dict(ref=(57, 1, 2), lang='ko', en='all', words=['만유의']),
    dict(ref=(57, 1, 2), lang='ko', en='things', words=['만유의']),
    dict(ref=(57, 1, 2), lang='ko', en='by#2', words=['저로', '말미암아']),
    dict(ref=(57, 1, 2), lang='ko', en='whom#2', words=['저로', '말미암아']),
    dict(ref=(57, 1, 2), lang='ko', en='he#2', words=['지으셨느니라']),
    dict(ref=(57, 1, 2), lang='ko', en='the', words=['모든#2']),

    dict(ref=(57, 1, 3), lang='ko', en='Who', words=['이는']),
    dict(ref=(57, 1, 3), lang='ko', en='the#1', words=['광채시요']),
    dict(ref=(57, 1, 3), lang='ko', en='brightness', words=['광채시요']),
    dict(ref=(57, 1, 3), lang='ko', en='of#1', words=['광채시요']),
    dict(ref=(57, 1, 3), lang='ko', en='his#1', words=['하나님의']),
    dict(ref=(57, 1, 3), lang='ko', en='glory', words=['영광의']),
    dict(ref=(57, 1, 3), lang='ko', en='his#2', words=['그']),
    dict(ref=(57, 1, 3), lang='ko', en='person', words=['본체의']),
    dict(ref=(57, 1, 3), lang='ko', en='by#1', words=['말씀으로']),
    dict(ref=(57, 1, 3), lang='ko', en='the#2', words=['말씀으로']),
    dict(ref=(57, 1, 3), lang='ko', en='word', words=['말씀으로']),
    dict(ref=(57, 1, 3), lang='ko', en='of#3', words=['말씀으로']),
    dict(ref=(57, 1, 3), lang='ko', en='his#3', words=['그의']),
    dict(ref=(57, 1, 3), lang='ko', en='power', words=['능력의']),
    dict(ref=(57, 1, 3), lang='ko', en='had', words=['하는', '일을']),
    dict(ref=(57, 1, 3), lang='ko', en='by#2', words=['하시고']),
    dict(ref=(57, 1, 3), lang='ko', en='himself', words=['하시고']),
    dict(ref=(57, 1, 3), lang='ko', en='purged', words=['정결케']),
    dict(ref=(57, 1, 3), lang='ko', en='our', words=['죄를']),
    dict(ref=(57, 1, 3), lang='ko', en='on#2', words=['계신']),

    dict(ref=(57, 1, 4), lang='ko', en='he', words=['저가']),
    dict(ref=(57, 1, 4), lang='ko', en='so', words=['얼마큼']),
    dict(ref=(57, 1, 4), lang='ko', en='much', words=['얼마큼']),
    dict(ref=(57, 1, 4), lang='ko', en='better', words=['뛰어남은']),
    dict(ref=(57, 1, 4), lang='ko', en='than#1', words=['천사보다']),
    dict(ref=(57, 1, 4), lang='ko', en='more', words=['더욱']),
    dict(ref=(57, 1, 4), lang='ko', en='excellent', words=['아름다운']),
    dict(ref=(57, 1, 4), lang='ko', en='obtained', words=['얻으심이니']),
    dict(ref=(57, 1, 4), lang='ko', en='than#2', words=['저희보다']),
    dict(ref=(57, 1, 4), lang='ko', en='they', words=['저희보다']),

    dict(ref=(57, 1, 5), lang='ko', en='he#1', words=['하나님께서']),
    dict(ref=(57, 1, 5), lang='ko', en='at', words=['어느', '때에']),
    dict(ref=(57, 1, 5), lang='ko', en='any', words=['어느', '때에']),
    dict(ref=(57, 1, 5), lang='ko', en='time', words=['어느', '때에']),
    dict(ref=(57, 1, 5), lang='ko', en='art', words=['아들이라']),
    dict(ref=(57, 1, 5), lang='ko', en='my', words=['내']),
    dict(ref=(57, 1, 5), lang='ko', en='Son#1', words=['아들이라']),
    dict(ref=(57, 1, 5), lang='ko', en='this', words=['오늘날']),
    dict(ref=(57, 1, 5), lang='ko', en='day', words=['오늘날']),
    dict(ref=(57, 1, 5), lang='ko', en='I#1', words=['내가']),
    dict(ref=(57, 1, 5), lang='ko', en='I#2', words=['나는']),
    dict(ref=(57, 1, 5), lang='ko', en='be#1', words=['되고']),
    dict(ref=(57, 1, 5), lang='ko', en='to#1', words=['그에게']),
    dict(ref=(57, 1, 5), lang='ko', en='him', words=['그에게']),
    dict(ref=(57, 1, 5), lang='ko', en='and', words=['그는']),
    dict(ref=(57, 1, 5), lang='ko', en='he#2', words=['그는']),
    dict(ref=(57, 1, 5), lang='ko', en='shall', words=['되리라']),
    dict(ref=(57, 1, 5), lang='ko', en='be#2', words=['되리라']),
    dict(ref=(57, 1, 5), lang='ko', en='to#2', words=['내게']),
    dict(ref=(57, 1, 5), lang='ko', en='me', words=['내게']),
    dict(ref=(57, 1, 5), lang='ko', en='Son#2', words=['아들이']),

    dict(ref=(57, 1, 1), lang='ko', en='God', words=['하나님이']),
    dict(ref=(57, 1, 1), lang='ko', en='who', words=['하나님이']),
    dict(ref=(57, 1, 1), lang='ko', en='at', words=['여러#1']),
    dict(ref=(57, 1, 1), lang='ko', en='sundry', words=['여러#1', '부분과']),
    dict(ref=(57, 1, 1), lang='ko', en='times', words=['여러#1', '부분과']),
    dict(ref=(57, 1, 1), lang='ko', en='in#1', words=['여러#2']),
    dict(ref=(57, 1, 1), lang='ko', en='divers', words=['여러#2', '모양으로']),
    dict(ref=(57, 1, 1), lang='ko', en='manners', words=['여러#2', '모양으로']),
    dict(ref=(57, 1, 1), lang='ko', en='in#2', words=['옛적에']),
    dict(ref=(57, 1, 1), lang='ko', en='time', words=['옛적에']),
    dict(ref=(57, 1, 1), lang='ko', en='past', words=['옛적에']),
    dict(ref=(57, 1, 1), lang='ko', en='the#1', words=['우리']),
    dict(ref=(57, 1, 1), lang='ko', en='fathers', words=['조상들에게']),
    dict(ref=(57, 1, 1), lang='ko', en='by', words=['선지자들로']),
    dict(ref=(57, 1, 1), lang='ko', en='the#2', words=['선지자들로']),

    dict(ref=(57, 1, 7), lang='ko', en='of#1', words=['천사들에', '관하여는']),
    dict(ref=(57, 1, 7), lang='ko', en='the', words=['천사들에']),
    dict(ref=(57, 1, 7), lang='ko', en='angels#1', words=['천사들에', '관하여는']),
    dict(ref=(57, 1, 7), lang='ko', en='he', words=['그는']),
    dict(ref=(57, 1, 7), lang='ko', en='saith', words=['하셨으되']),
    dict(ref=(57, 1, 7), lang='ko', en='Who', words=['그는']),
    dict(ref=(57, 1, 7), lang='ko', en='maketh', words=['삼으시느니라']),
    dict(ref=(57, 1, 7), lang='ko', en='his#1', words=['그의#1']),
    dict(ref=(57, 1, 7), lang='ko', en='angels#2', words=['천사들을']),
    dict(ref=(57, 1, 7), lang='ko', en='spirits', words=['바람으로']),
    dict(ref=(57, 1, 7), lang='ko', en='his#2', words=['그의#2']),
    dict(ref=(57, 1, 7), lang='ko', en='ministers', words=['사역자들을']),
    dict(ref=(57, 1, 7), lang='ko', en='a', words=['불꽃으로']),
    dict(ref=(57, 1, 7), lang='ko', en='flame', words=['불꽃으로']),
    dict(ref=(57, 1, 7), lang='ko', en='of#2', words=['불꽃으로']),
    dict(ref=(57, 1, 7), lang='ko', en='fire', words=['불꽃으로']),

    dict(ref=(57, 1, 9), lang='ko', en='Thou', words=['네가']),
    dict(ref=(57, 1, 9), lang='ko', en='God#1', words=['하나님']),
    dict(ref=(57, 1, 9), lang='ko', en='even', words=['곧']),
    dict(ref=(57, 1, 9), lang='ko', en='thy#1', words=['너의']),
    dict(ref=(57, 1, 9), lang='ko', en='God#2', words=['하나님이']),
    dict(ref=(57, 1, 9), lang='ko', en='hath', words=['하셨도다']),
    dict(ref=(57, 1, 9), lang='ko', en='thee', words=['네게']),
    dict(ref=(57, 1, 9), lang='ko', en='above', words=['승하게']),
    dict(ref=(57, 1, 9), lang='ko', en='thy#2', words=['네']),
    dict(ref=(57, 1, 9), lang='ko', en='fellows', words=['동류들보다']),

    dict(ref=(57, 1, 12), lang='ko', en='as', words=['의복처럼', '같이']),
    dict(ref=(57, 1, 12), lang='ko', en='a', words=['의복처럼']),
    dict(ref=(57, 1, 12), lang='ko', en='vesture', words=['의복처럼', '옷과']),
    dict(ref=(57, 1, 12), lang='ko', en='shalt', words=['것이요']),
    dict(ref=(57, 1, 12), lang='ko', en='fold', words=['갈아', '입을']),
    dict(ref=(57, 1, 12), lang='ko', en='up', words=['갈아', '입을']),
    dict(ref=(57, 1, 12), lang='ko', en='them', words=['그것들이']),
    dict(ref=(57, 1, 12), lang='ko', en='they', words=['그것들이']),
    dict(ref=(57, 1, 12), lang='ko', en='shall#1', words=['것이나']),
    dict(ref=(57, 1, 12), lang='ko', en='be', words=['변할']),
    dict(ref=(57, 1, 12), lang='ko', en='changed', words=['변할']),
    dict(ref=(57, 1, 12), lang='ko', en='thou#2', words=['주는']),
    dict(ref=(57, 1, 12), lang='ko', en='art', words=['여전하여']),
    dict(ref=(57, 1, 12), lang='ko', en='the', words=['여전하여']),
    dict(ref=(57, 1, 12), lang='ko', en='same', words=['여전하여']),
    dict(ref=(57, 1, 12), lang='ko', en='thy', words=['연대가']),
    dict(ref=(57, 1, 12), lang='ko', en='years', words=['연대가']),
    dict(ref=(57, 1, 12), lang='ko', en='shall#2', words=['다함이']),
    dict(ref=(57, 1, 12), lang='ko', en='not', words=['없으리라']),
    dict(ref=(57, 1, 12), lang='ko', en='fail', words=['다함이']),

    dict(ref=(57, 1, 13), lang='ko', en='which', words=['누구에게']),
    dict(ref=(57, 1, 13), lang='ko', en='of', words=['중']),
    dict(ref=(57, 1, 13), lang='ko', en='angels', words=['천사']),
    dict(ref=(57, 1, 13), lang='ko', en='said', words=['하셨느뇨']),
    dict(ref=(57, 1, 13), lang='ko', en='he', words=['하셨느뇨']),
    dict(ref=(57, 1, 13), lang='ko', en='at', words=['어느', '때에']),
    dict(ref=(57, 1, 13), lang='ko', en='any', words=['어느', '때에']),
    dict(ref=(57, 1, 13), lang='ko', en='time', words=['어느', '때에']),
    dict(ref=(57, 1, 13), lang='ko', en='Sit', words=['너는', '앉았으라']),
    dict(ref=(57, 1, 13), lang='ko', en='on', words=['우편에']),
    dict(ref=(57, 1, 13), lang='ko', en='my', words=['내']),
    dict(ref=(57, 1, 13), lang='ko', en='right', words=['우편에']),
    dict(ref=(57, 1, 13), lang='ko', en='hand', words=['우편에']),
    dict(ref=(57, 1, 13), lang='ko', en='until', words=['하기까지']),
    dict(ref=(57, 1, 13), lang='ko', en='I', words=['내가']),
    dict(ref=(57, 1, 13), lang='ko', en='make', words=['되게', '하기까지']),
    dict(ref=(57, 1, 13), lang='ko', en='thine', words=['네#1']),
    dict(ref=(57, 1, 13), lang='ko', en='enemies', words=['원수로']),
    dict(ref=(57, 1, 13), lang='ko', en='thy', words=['네#2']),
    dict(ref=(57, 1, 13), lang='ko', en='footstool', words=['발등상']),

    dict(ref=(57, 1, 8), lang='ko', en='unto', words=['관하여는']),
    dict(ref=(57, 1, 8), lang='ko', en='he', words=['관하여는']),
    dict(ref=(57, 1, 8), lang='ko', en='saith', words=['관하여는']),
    dict(ref=(57, 1, 8), lang='ko', en='the#1', words=['아들에']),
    dict(ref=(57, 1, 8), lang='ko', en='Son', words=['아들에']),
    dict(ref=(57, 1, 8), lang='ko', en='of#1', words=['공평한']),
    dict(ref=(57, 1, 8), lang='ko', en='righteousness', words=['공평한']),

    dict(ref=(57, 1, 10), lang='ko', en='works', words=['지으신', '바라']),

    dict(ref=(57, 1, 11), lang='ko', en='remainest', words=['영존할']),

    dict(ref=(57, 1, 14), lang='ko', en='they', words=['천사들은']),
    dict(ref=(57, 1, 14), lang='ko', en='all', words=['모든']),
    dict(ref=(57, 1, 14), lang='ko', en='ministering', words=['부리는']),
    dict(ref=(57, 1, 14), lang='ko', en='spirits', words=['영으로서']),
    dict(ref=(57, 1, 14), lang='ko', en='to', words=['섬기라고']),
    dict(ref=(57, 1, 14), lang='ko', en='minister', words=['섬기라고']),

    dict(ref=(57, 1, 8), lang='ko', en='sceptre#1', words=['홀이니이다']),
    dict(ref=(57, 1, 8), lang='ko', en='of#2', words=['나라의']),
    dict(ref=(57, 1, 8), lang='ko', en='thy', words=['주의#2', '나라의']),
    dict(ref=(57, 1, 8), lang='ko', en='kingdom', words=['주의#2', '나라의']),
    dict(ref=(57, 1, 8), lang='ko', en='Thy', words=['주의#1']),
    dict(ref=(57, 1, 8), lang='ko', en='sceptre#2', words=['홀은']),
    dict(ref=(57, 1, 11), lang='ko', en='wax', words=['낡아지리니']),
    dict(ref=(57, 1, 11), lang='ko', en='old', words=['낡아지리니']),
    dict(ref=(57, 1, 14), lang='ko', en='sent', words=['보내심이']),
    dict(ref=(57, 1, 14), lang='ko', en='forth', words=['보내심이']),

    # ---- 성령 끊어진 곳 (성경 전체 점검) ----
    dict(ref=(39, 10, 20), lang='ko', en='Spirit', words=['성령이시니라']),
    dict(ref=(40, 13, 11), lang='ko', en='Holy', words=['성령이시니라']),
    dict(ref=(40, 13, 11), lang='ko', en='Ghost', words=['성령이시니라']),
    dict(ref=(41, 4, 1), lang='ko', en='Holy', words=['성령의']),
    dict(ref=(41, 4, 1), lang='ko', en='Ghost', words=['성령의']),
    dict(ref=(41, 4, 1), lang='ko', en='Spirit', words=['성령에게']),
    dict(ref=(43, 2, 4), lang='ko', en='Holy', words=['성령의']),
    dict(ref=(43, 2, 4), lang='ko', en='Ghost', words=['성령의']),
    dict(ref=(43, 2, 4), lang='ko', en='Spirit', words=['성령이']),
    dict(ref=(43, 8, 16), lang='ko', en='he', words=['성령']),
    dict(ref=(44, 8, 27), lang='ko', en='Spirit', words=['성령의']),
    dict(ref=(44, 8, 27), lang='ko', en='he#2', words=['성령이']),
    dict(ref=(47, 5, 17), lang='ko', en='Spirit#1', words=['성령을']),
    dict(ref=(47, 5, 17), lang='ko', en='Spirit#2', words=['성령의']),
    dict(ref=(55, 3, 6), lang='ko', en='Which', words=['성령을']),

    # ---- 영광·영화 끊어진 곳 (성경 전체 점검) ----
    # KJV 가 glory 말고 다른 낱말을 쓴 자리
    dict(ref=(4, 33, 29), lang='ko', en='excellency', words=['영광의']),
    dict(ref=(9, 1, 19), lang='ko', en='beauty', words=['영광이']),
    dict(ref=(16, 8, 16), lang='ko', en='light', words=['영광과']),
    dict(ref=(17, 30, 15), lang='ko', en='soul', words=['영광을']),
    dict(ref=(18, 103, 15), lang='ko', en='flourisheth', words=['영화가']),
    dict(ref=(19, 14, 34), lang='ko', en='exalteth', words=['영화롭게']),
    dict(ref=(19, 25, 2), lang='ko', en='glory', words=['영화요']),
    dict(ref=(19, 25, 2), lang='ko', en='honour', words=['영화니라']),
    dict(ref=(22, 4, 2), lang='ko', en='glorious', words=['영화로울']),
    dict(ref=(22, 4, 2), lang='ko', en='excellent', words=['영화롭고']),
    dict(ref=(22, 24, 15), lang='ko', en='glorify', words=['영화롭게#1', '영화롭게#2']),
    dict(ref=(24, 2, 15), lang='ko', en='beauty', words=['영광이라']),
    dict(ref=(25, 10, 4), lang='ko', en='glory#2', words=['영화로운']),
    dict(ref=(25, 24, 21), lang='ko', en='excellency', words=['영광이요']),
    dict(ref=(25, 28, 7), lang='ko', en='brightness', words=['영화를']),
    dict(ref=(25, 28, 17), lang='ko', en='brightness', words=['영화로우므로']),
    dict(ref=(26, 8, 9), lang='ko', en='pleasant', words=['영화로운']),
    dict(ref=(29, 6, 8), lang='ko', en='excellency', words=['영광을']),
    dict(ref=(29, 8, 7), lang='ko', en='excellency', words=['영광을']),
    dict(ref=(36, 2, 9), lang='ko', en='than', words=['영광보다']),
    dict(ref=(36, 2, 9), lang='ko', en='of#2', words=['영광보다']),
    dict(ref=(41, 14, 10), lang='ko', en='worship', words=['영광이']),
    dict(ref=(42, 5, 44), lang='ko', en='honour#1', words=['영광을']),
    dict(ref=(42, 5, 44), lang='ko', en='honour#2', words=['영광은']),
    dict(ref=(42, 8, 54), lang='ko', en='honour#1', words=['영광을#1']),
    dict(ref=(42, 8, 54), lang='ko', en='honour#2', words=['영광이']),
    dict(ref=(42, 8, 54), lang='ko', en='honoureth', words=['영광을#2']),
    dict(ref=(42, 12, 43), lang='ko', en='praise#1', words=['영광을']),
    dict(ref=(42, 12, 43), lang='ko', en='praise#2', words=['영광보다']),
    dict(ref=(42, 13, 32), lang='ko', en='glorified', words=['영광을#1', '얻으셨으면']),
    dict(ref=(42, 13, 32), lang='ko', en='glorify#1', words=['영광을#2', '주시리니']),
    dict(ref=(42, 13, 32), lang='ko', en='glorify#2', words=['주시리라']),
    dict(ref=(43, 2, 20), lang='ko', en='notable', words=['영화로운']),
    dict(ref=(45, 15, 40), lang='ko', en='glory#1', words=['영광이#1']),
    dict(ref=(45, 15, 40), lang='ko', en='glory#2', words=['영광이#2']),
    dict(ref=(46, 3, 7), lang='ko', en='glorious', words=['영광이']),
    dict(ref=(46, 3, 7), lang='ko', en='glory#2', words=['영광을']),
    dict(ref=(46, 3, 10), lang='ko', en='glorious', words=['영광되었던']),
    dict(ref=(46, 3, 10), lang='ko', en='glory#1', words=['영광될']),
    dict(ref=(46, 3, 10), lang='ko', en='glory#2', words=['영광을']),
    dict(ref=(52, 1, 12), lang='ko', en='glorified', words=['영광을#1', '영광을#2']),
    dict(ref=(59, 4, 11), lang='ko', en='glorified', words=['영광을', '받으시게']),
    dict(ref=(59, 4, 11), lang='ko', en='dominion', words=['권능이']),
    dict(ref=(59, 4, 11), lang='ko', en='praise', words=['영광과']),
    dict(ref=(60, 2, 10), lang='ko', en='dignities', words=['영광']),
    dict(ref=(64, 1, 8), lang='ko', en='dignities', words=['영광을']),

    # ---- 히브리서 2장 ----
    dict(ref=(57, 2, 1), lang='ko', en='we#1', words=['우리가']),
    dict(ref=(57, 2, 1), lang='ko', en='ought', words=['삼갈지니']),
    dict(ref=(57, 2, 1), lang='ko', en='to#1', words=['삼갈지니']),
    dict(ref=(57, 2, 1), lang='ko', en='give', words=['삼갈지니']),
    dict(ref=(57, 2, 1), lang='ko', en='more', words=['더욱']),
    dict(ref=(57, 2, 1), lang='ko', en='earnest', words=['간절히']),
    dict(ref=(57, 2, 1), lang='ko', en='heed', words=['삼갈지니']),
    dict(ref=(57, 2, 1), lang='ko', en='things', words=['모든', '것을']),
    dict(ref=(57, 2, 1), lang='ko', en='we#2', words=['들은']),
    dict(ref=(57, 2, 1), lang='ko', en='lest', words=['염려하노라']),
    dict(ref=(57, 2, 1), lang='ko', en='at', words=['혹']),
    dict(ref=(57, 2, 1), lang='ko', en='any', words=['혹']),
    dict(ref=(57, 2, 1), lang='ko', en='time', words=['혹']),
    dict(ref=(57, 2, 1), lang='ko', en='we#3', words=['갈까']),
    dict(ref=(57, 2, 1), lang='ko', en='should', words=['갈까']),
    dict(ref=(57, 2, 1), lang='ko', en='let', words=['갈까']),
    dict(ref=(57, 2, 1), lang='ko', en='them', words=['갈까']),
    dict(ref=(57, 2, 1), lang='ko', en='slip', words=['흘러', '떠내려', '갈까']),

    dict(ref=(57, 2, 2), lang='ko', en='the#1', words=['말씀이']),
    dict(ref=(57, 2, 2), lang='ko', en='by', words=['천사들로']),
    dict(ref=(57, 2, 2), lang='ko', en='was', words=['되어']),
    dict(ref=(57, 2, 2), lang='ko', en='stedfast', words=['견고하게']),
    dict(ref=(57, 2, 2), lang='ko', en='disobedience', words=['순종치', '아니함이']),
    dict(ref=(57, 2, 2), lang='ko', en='a', words=['공변된']),
    dict(ref=(57, 2, 2), lang='ko', en='just', words=['공변된']),
    dict(ref=(57, 2, 2), lang='ko', en='recompence', words=['공변된']),
    dict(ref=(57, 2, 2), lang='ko', en='of', words=['공변된']),
    dict(ref=(57, 2, 2), lang='ko', en='reward', words=['보응을']),

    dict(ref=(57, 2, 3), lang='ko', en='we#1', words=['우리가']),
    dict(ref=(57, 2, 3), lang='ko', en='neglect', words=['등한히', '여기면']),
    dict(ref=(57, 2, 3), lang='ko', en='which', words=['이', '구원은']),
    dict(ref=(57, 2, 3), lang='ko', en='began', words=['바요']),
    dict(ref=(57, 2, 3), lang='ko', en='by#1', words=['주로']),
    dict(ref=(57, 2, 3), lang='ko', en='the#2', words=['주로']),
    dict(ref=(57, 2, 3), lang='ko', en='Lord', words=['주로']),
    dict(ref=(57, 2, 3), lang='ko', en='was', words=['바니']),
    dict(ref=(57, 2, 3), lang='ko', en='confirmed', words=['확증한']),
    dict(ref=(57, 2, 3), lang='ko', en='unto', words=['우리에게']),
    dict(ref=(57, 2, 3), lang='ko', en='us', words=['우리에게']),
    dict(ref=(57, 2, 3), lang='ko', en='by#2', words=['자들이']),
    dict(ref=(57, 2, 3), lang='ko', en='them', words=['자들이']),
    dict(ref=(57, 2, 3), lang='ko', en='him', words=['들은']),

    dict(ref=(57, 2, 8), lang='ko', en='put#1', words=['복종케#1', '하셨느니라']),
    dict(ref=(57, 2, 8), lang='ko', en='all#1', words=['만물을']),
    dict(ref=(57, 2, 8), lang='ko', en='things#1', words=['만물을']),
    dict(ref=(57, 2, 8), lang='ko', en='in#1', words=['복종케#1']),
    dict(ref=(57, 2, 8), lang='ko', en='subjection#1', words=['복종케#1']),
    dict(ref=(57, 2, 8), lang='ko', en='under#1', words=['아래']),
    dict(ref=(57, 2, 8), lang='ko', en='his', words=['그']),
    dict(ref=(57, 2, 8), lang='ko', en='feet', words=['발']),
    dict(ref=(57, 2, 8), lang='ko', en='For', words=['하였으니']),
    dict(ref=(57, 2, 8), lang='ko', en='in#2', words=['하였으니']),
    dict(ref=(57, 2, 8), lang='ko', en='that#1', words=['하였으니']),
    dict(ref=(57, 2, 8), lang='ko', en='put#2', words=['복종케#2', '하셨은즉']),
    dict(ref=(57, 2, 8), lang='ko', en='all#2', words=['만물로']),
    dict(ref=(57, 2, 8), lang='ko', en='subjection#2', words=['복종케#2']),
    dict(ref=(57, 2, 8), lang='ko', en='under#2', words=['저에게#1']),
    dict(ref=(57, 2, 8), lang='ko', en='him#1', words=['저에게#1']),
    dict(ref=(57, 2, 8), lang='ko', en='he#2', words=['없으나']),
    dict(ref=(57, 2, 8), lang='ko', en='left', words=['없으나']),
    dict(ref=(57, 2, 8), lang='ko', en='nothing', words=['하나도']),
    dict(ref=(57, 2, 8), lang='ko', en='that#2', words=['것이']),
    dict(ref=(57, 2, 8), lang='ko', en='is', words=['것이']),
    dict(ref=(57, 2, 8), lang='ko', en='not#1', words=['않은']),
    dict(ref=(57, 2, 8), lang='ko', en='put#3', words=['복종치']),
    dict(ref=(57, 2, 8), lang='ko', en='under#3', words=['복종치']),
    dict(ref=(57, 2, 8), lang='ko', en='him#2', words=['복종치']),
    dict(ref=(57, 2, 8), lang='ko', en='But', words=['지금']),
    dict(ref=(57, 2, 8), lang='ko', en='now', words=['지금']),
    dict(ref=(57, 2, 8), lang='ko', en='we', words=['우리가']),
    dict(ref=(57, 2, 8), lang='ko', en='see', words=['보지']),
    dict(ref=(57, 2, 8), lang='ko', en='not#2', words=['못하고']),
    dict(ref=(57, 2, 8), lang='ko', en='yet', words=['아직']),
    dict(ref=(57, 2, 8), lang='ko', en='all#3', words=['만물이']),
    dict(ref=(57, 2, 8), lang='ko', en='things#2', words=['만물이']),
    dict(ref=(57, 2, 8), lang='ko', en='put#4', words=['복종한', '것을']),
    dict(ref=(57, 2, 8), lang='ko', en='under#4', words=['저에게#2']),
    dict(ref=(57, 2, 8), lang='ko', en='him#3', words=['저에게#2']),

    dict(ref=(57, 2, 9), lang='ko', en='a', words=['잠간', '동안']),
    dict(ref=(57, 2, 9), lang='ko', en='little', words=['잠간', '동안']),
    dict(ref=(57, 2, 9), lang='ko', en='lower', words=['못하게', '하심을']),
    dict(ref=(57, 2, 9), lang='ko', en='who', words=['자']),
    dict(ref=(57, 2, 9), lang='ko', en='was', words=['입은']),
    dict(ref=(57, 2, 9), lang='ko', en='made', words=['입은']),
    dict(ref=(57, 2, 9), lang='ko', en='for#1', words=['인하여']),
    dict(ref=(57, 2, 9), lang='ko', en='suffering', words=['고난', '받으심을']),
    dict(ref=(57, 2, 9), lang='ko', en='death#1', words=['죽음의']),
    dict(ref=(57, 2, 9), lang='ko', en='that', words=['이를', '행하심은']),
    dict(ref=(57, 2, 9), lang='ko', en='he', words=['행하심은']),
    dict(ref=(57, 2, 9), lang='ko', en='should', words=['하심이라']),
    dict(ref=(57, 2, 9), lang='ko', en='taste', words=['맛보려']),
    dict(ref=(57, 2, 9), lang='ko', en='death#2', words=['죽음을']),
    dict(ref=(57, 2, 9), lang='ko', en='for#2', words=['위하여']),
    dict(ref=(57, 2, 9), lang='ko', en='every', words=['모든']),
    dict(ref=(57, 2, 9), lang='ko', en='man', words=['사람을']),

    dict(ref=(57, 2, 10), lang='ko', en='became', words=['합당하도다']),
    dict(ref=(57, 2, 10), lang='ko', en='him', words=['자에게는']),
    dict(ref=(57, 2, 10), lang='ko', en='bringing', words=['이끌어', '하시는']),
    dict(ref=(57, 2, 10), lang='ko', en='unto', words=['들어가게']),
    dict(ref=(57, 2, 10), lang='ko', en='to', words=['일에']),
    dict(ref=(57, 2, 10), lang='ko', en='make', words=['하심이']),
    dict(ref=(57, 2, 10), lang='ko', en='perfect', words=['온전케']),

    dict(ref=(57, 2, 13), lang='ko', en='And#1', words=['또#1']),
    dict(ref=(57, 2, 13), lang='ko', en='again#1', words=['다시#1']),
    dict(ref=(57, 2, 13), lang='ko', en='And#2', words=['또#2']),
    dict(ref=(57, 2, 13), lang='ko', en='again#2', words=['다시#2']),
    dict(ref=(57, 2, 13), lang='ko', en='Behold', words=['볼지어다']),
    dict(ref=(57, 2, 13), lang='ko', en='I#2', words=['나와']),
    dict(ref=(57, 2, 13), lang='ko', en='and', words=['및']),
    dict(ref=(57, 2, 13), lang='ko', en='God', words=['하나님께서']),
    dict(ref=(57, 2, 13), lang='ko', en='me', words=['내게']),

    dict(ref=(57, 2, 14), lang='ko', en='the#1', words=['자녀들은']),
    dict(ref=(57, 2, 14), lang='ko', en='children', words=['자녀들은']),
    dict(ref=(57, 2, 14), lang='ko', en='are', words=['속하였으매']),
    dict(ref=(57, 2, 14), lang='ko', en='partakers', words=['함께#1', '속하였으매']),
    dict(ref=(57, 2, 14), lang='ko', en='flesh', words=['혈육에#1']),
    dict(ref=(57, 2, 14), lang='ko', en='blood', words=['혈육에#1']),
    dict(ref=(57, 2, 14), lang='ko', en='he#1', words=['그도']),
    dict(ref=(57, 2, 14), lang='ko', en='also', words=['또한']),
    dict(ref=(57, 2, 14), lang='ko', en='himself', words=['그도']),
    dict(ref=(57, 2, 14), lang='ko', en='likewise', words=['한', '모양으로']),
    dict(ref=(57, 2, 14), lang='ko', en='took', words=['함께#2', '속하심은']),
    dict(ref=(57, 2, 14), lang='ko', en='part', words=['함께#2', '속하심은']),
    dict(ref=(57, 2, 14), lang='ko', en='the#2', words=['혈육에#2']),
    dict(ref=(57, 2, 14), lang='ko', en='same', words=['혈육에#2']),
    dict(ref=(57, 2, 14), lang='ko', en='through', words=['사망으로', '말미암아']),
    dict(ref=(57, 2, 14), lang='ko', en='death#1', words=['사망으로']),
    dict(ref=(57, 2, 14), lang='ko', en='he#2', words=['하시며']),
    dict(ref=(57, 2, 14), lang='ko', en='might', words=['하시며']),
    dict(ref=(57, 2, 14), lang='ko', en='destroy', words=['없이', '하시며']),
    dict(ref=(57, 2, 14), lang='ko', en='him', words=['자']),
    dict(ref=(57, 2, 14), lang='ko', en='that#2', words=['자']),
    dict(ref=(57, 2, 14), lang='ko', en='had', words=['잡은']),
    dict(ref=(57, 2, 14), lang='ko', en='the#3', words=['세력을']),
    dict(ref=(57, 2, 14), lang='ko', en='power', words=['세력을']),
    dict(ref=(57, 2, 14), lang='ko', en='death#2', words=['사망의']),
    dict(ref=(57, 2, 14), lang='ko', en='that#3', words=['곧']),
    dict(ref=(57, 2, 14), lang='ko', en='is', words=['곧']),
    dict(ref=(57, 2, 14), lang='ko', en='the#4', words=['마귀를']),
    dict(ref=(57, 2, 14), lang='ko', en='devil', words=['마귀를']),

    dict(ref=(57, 2, 16), lang='ko', en='For', words=['이는']),
    dict(ref=(57, 2, 16), lang='ko', en='verily', words=['실로']),
    dict(ref=(57, 2, 16), lang='ko', en='took#1', words=['붙들어#1', '주려#1', '하심이']),
    dict(ref=(57, 2, 16), lang='ko', en='not', words=['아니요']),
    dict(ref=(57, 2, 16), lang='ko', en='on#1', words=['붙들어#1']),
    dict(ref=(57, 2, 16), lang='ko', en='him#1', words=['붙들어#1']),
    dict(ref=(57, 2, 16), lang='ko', en='of#1', words=['천사들을']),
    dict(ref=(57, 2, 16), lang='ko', en='angels', words=['천사들을']),
    dict(ref=(57, 2, 16), lang='ko', en='but', words=['오직']),
    dict(ref=(57, 2, 16), lang='ko', en='took#2', words=['붙들어#2', '주려#2', '하심이라']),
    dict(ref=(57, 2, 16), lang='ko', en='on#2', words=['붙들어#2']),
    dict(ref=(57, 2, 16), lang='ko', en='him#2', words=['붙들어#2']),
    dict(ref=(57, 2, 16), lang='ko', en='the#2', words=['자손을']),
    dict(ref=(57, 2, 16), lang='ko', en='seed', words=['자손을']),
    dict(ref=(57, 2, 16), lang='ko', en='of#2', words=['아브라함의']),
    dict(ref=(57, 2, 16), lang='ko', en='Abraham', words=['아브라함의']),

    dict(ref=(57, 2, 4), lang='ko', en='bearing', words=['증거하셨느니라']),
    dict(ref=(57, 2, 4), lang='ko', en='them', words=['저희와', '함께']),
    dict(ref=(57, 2, 4), lang='ko', en='witness', words=['증거하셨느니라']),
    dict(ref=(57, 2, 4), lang='ko', en='with#1', words=['표적들과']),
    dict(ref=(57, 2, 4), lang='ko', en='with#2', words=['여러가지']),
    dict(ref=(57, 2, 4), lang='ko', en='divers', words=['여러가지']),
    dict(ref=(57, 2, 4), lang='ko', en='gifts', words=['나눠', '주신', '것으로써']),
    dict(ref=(57, 2, 4), lang='ko', en='of', words=['성령의']),
    dict(ref=(57, 2, 4), lang='ko', en='the', words=['성령의']),
    dict(ref=(57, 2, 4), lang='ko', en='according', words=['따라']),
    dict(ref=(57, 2, 4), lang='ko', en='to', words=['따라']),
    dict(ref=(57, 2, 4), lang='ko', en='his', words=['자기', '뜻을']),
    dict(ref=(57, 2, 4), lang='ko', en='own', words=['자기', '뜻을']),
    dict(ref=(57, 2, 4), lang='ko', en='will', words=['자기', '뜻을']),

    dict(ref=(57, 2, 6), lang='ko', en='one', words=['누가']),
    dict(ref=(57, 2, 6), lang='ko', en='in', words=['어디']),
    dict(ref=(57, 2, 6), lang='ko', en='a', words=['어디']),
    dict(ref=(57, 2, 6), lang='ko', en='certain', words=['어디']),
    dict(ref=(57, 2, 6), lang='ko', en='place', words=['어디']),
    dict(ref=(57, 2, 6), lang='ko', en='What', words=['무엇이관대#1', '무엇이관대#2']),
    dict(ref=(57, 2, 6), lang='ko', en='is', words=['무엇이관대#1', '무엇이관대#2']),
    dict(ref=(57, 2, 6), lang='ko', en='man#1', words=['사람이']),
    dict(ref=(57, 2, 6), lang='ko', en='thou#1', words=['주께서#1']),
    dict(ref=(57, 2, 6), lang='ko', en='art', words=['생각하시며']),
    dict(ref=(57, 2, 6), lang='ko', en='mindful', words=['생각하시며']),
    dict(ref=(57, 2, 6), lang='ko', en='of#1', words=['저를#1']),
    dict(ref=(57, 2, 6), lang='ko', en='him#1', words=['저를#1']),
    dict(ref=(57, 2, 6), lang='ko', en='the', words=['인자가']),
    dict(ref=(57, 2, 6), lang='ko', en='son', words=['인자가']),
    dict(ref=(57, 2, 6), lang='ko', en='of#2', words=['인자가']),
    dict(ref=(57, 2, 6), lang='ko', en='man#2', words=['인자가']),
    dict(ref=(57, 2, 6), lang='ko', en='thou#2', words=['주께서#2']),
    dict(ref=(57, 2, 6), lang='ko', en='visitest', words=['권고하시나이까']),
    dict(ref=(57, 2, 6), lang='ko', en='him#2', words=['저를#2']),

    dict(ref=(57, 2, 7), lang='ko', en='madest', words=['하시며']),
    dict(ref=(57, 2, 7), lang='ko', en='him#1', words=['저를']),
    dict(ref=(57, 2, 7), lang='ko', en='a', words=['잠간', '동안']),
    dict(ref=(57, 2, 7), lang='ko', en='little', words=['잠간', '동안']),
    dict(ref=(57, 2, 7), lang='ko', en='lower', words=['못하게']),
    dict(ref=(57, 2, 7), lang='ko', en='than', words=['천사보다']),
    dict(ref=(57, 2, 7), lang='ko', en='the#1', words=['천사보다']),

    # ---- 죽음·죽은·죽고 끊어지거나 자리가 바뀐 곳 ----
    dict(ref=(8, 17, 51), lang='ko', en='dead', words=['죽음을']),
    dict(ref=(8, 17, 51), lang='ko', en='slew', words=['죽이고']),
    dict(ref=(9, 3, 33), lang='ko', en='Died', words=['죽음이']),
    dict(ref=(9, 3, 33), lang='ko', en='dieth', words=['죽음']),
    dict(ref=(11, 20, 1), lang='ko', en='death', words=['죽게']),
    dict(ref=(11, 20, 1), lang='ko', en='die', words=['죽고']),
    dict(ref=(22, 38, 1), lang='ko', en='death', words=['죽게']),
    dict(ref=(22, 38, 1), lang='ko', en='die', words=['죽고']),
    dict(ref=(7, 1, 17), lang='ko', en='diest', words=['죽으시는']),
    dict(ref=(7, 1, 17), lang='ko', en='die', words=['죽어']),
    dict(ref=(7, 1, 17), lang='ko', en='death', words=['죽는']),
    dict(ref=(25, 18, 32), lang='ko', en='dieth', words=['죽는#1']),
    dict(ref=(25, 18, 32), lang='ko', en='death', words=['죽는#2']),
    dict(ref=(25, 33, 11), lang='ko', en='death', words=['죽는']),
    dict(ref=(25, 33, 11), lang='ko', en='die', words=['죽고자']),
    dict(ref=(40, 9, 26), lang='ko', en='dead#1', words=['죽은']),
    dict(ref=(40, 9, 26), lang='ko', en='dead#2', words=['죽었다']),
    dict(ref=(45, 15, 32), lang='ko', en='dead', words=['죽은']),
    dict(ref=(45, 15, 32), lang='ko', en='die', words=['죽을']),
    dict(ref=(45, 15, 54), lang='ko', en='mortal', words=['죽을']),
    dict(ref=(45, 15, 54), lang='ko', en='Death', words=['사망이']),
    dict(ref=(46, 5, 14), lang='ko', en='died', words=['죽었은즉']),
    dict(ref=(46, 5, 14), lang='ko', en='for', words=['대신하여']),
    dict(ref=(46, 5, 14), lang='ko', en='dead', words=['죽은']),
    dict(ref=(46, 5, 15), lang='ko', en='died#1', words=['죽으심은']),
    dict(ref=(46, 5, 15), lang='ko', en='for#1', words=['대신하여#1']),
    dict(ref=(46, 5, 15), lang='ko', en='died#2', words=['죽었다가']),
    dict(ref=(46, 5, 15), lang='ko', en='for#2', words=['대신하여#2']),
    dict(ref=(59, 3, 18), lang='ko', en='suffered', words=['죽으사']),

    dict(ref=(57, 2, 11), lang='ko', en='For', words=[]),
    dict(ref=(57, 2, 11), lang='ko', en='sanctifieth', words=['거룩하게#1', '하시는']),
    dict(ref=(57, 2, 11), lang='ko', en='they', words=['자들이']),
    dict(ref=(57, 2, 11), lang='ko', en='who', words=['자들이']),
    dict(ref=(57, 2, 11), lang='ko', en='are#1', words=['거룩하게#2', '함을', '입은']),
    dict(ref=(57, 2, 11), lang='ko', en='sanctified', words=['거룩하게#2', '함을', '입은']),
    dict(ref=(57, 2, 11), lang='ko', en='are#2', words=['난지라']),

    dict(ref=(57, 2, 15), lang='ko', en='And', words=['또']),
    dict(ref=(57, 2, 15), lang='ko', en='deliver', words=['놓아주려', '하심이니']),
    dict(ref=(57, 2, 15), lang='ko', en='them', words=['자들을']),
    dict(ref=(57, 2, 15), lang='ko', en='who', words=['자들을']),
    dict(ref=(57, 2, 15), lang='ko', en='through', words=['무서워하므로']),
    dict(ref=(57, 2, 15), lang='ko', en='of', words=['죽기를']),
    dict(ref=(57, 2, 15), lang='ko', en='lifetime', words=['일생에']),
    dict(ref=(57, 2, 15), lang='ko', en='subject', words=['매여']),
    dict(ref=(57, 2, 15), lang='ko', en='bondage', words=['종', '노릇']),

    dict(ref=(57, 2, 17), lang='ko', en='in#1', words=['범사에']),
    dict(ref=(57, 2, 17), lang='ko', en='all', words=['범사에']),
    dict(ref=(57, 2, 17), lang='ko', en='things#1', words=['범사에']),
    dict(ref=(57, 2, 17), lang='ko', en='to#1', words=['되심이']),
    dict(ref=(57, 2, 17), lang='ko', en='unto', words=['같이']),
    dict(ref=(57, 2, 17), lang='ko', en='that', words=['이는']),
    dict(ref=(57, 2, 17), lang='ko', en='be#2', words=['되어']),
    dict(ref=(57, 2, 17), lang='ko', en='a', words=['자비하고']),
    dict(ref=(57, 2, 17), lang='ko', en='in#2', words=['일에']),
    dict(ref=(57, 2, 17), lang='ko', en='things#2', words=['일에']),
    dict(ref=(57, 2, 17), lang='ko', en='pertaining', words=['일에']),
    dict(ref=(57, 2, 17), lang='ko', en='to#2', words=['하나님의']),
    dict(ref=(57, 2, 17), lang='ko', en='to#3', words=['구속하려']),
    dict(ref=(57, 2, 17), lang='ko', en='make', words=['구속하려']),
    dict(ref=(57, 2, 17), lang='ko', en='reconciliation', words=['구속하려']),
    dict(ref=(57, 2, 17), lang='ko', en='for', words=['죄를']),
    dict(ref=(57, 2, 17), lang='ko', en='the#1', words=['죄를']),
    dict(ref=(57, 2, 17), lang='ko', en='of', words=['백성의']),
    dict(ref=(57, 2, 17), lang='ko', en='the#2', words=['백성의']),

    dict(ref=(57, 2, 18), lang='ko', en='he#1', words=['자기가']),
    dict(ref=(57, 2, 18), lang='ko', en='himself', words=['자기가']),
    dict(ref=(57, 2, 18), lang='ko', en='hath', words=['당하셨은즉']),
    dict(ref=(57, 2, 18), lang='ko', en='suffered', words=['고난을', '당하셨은즉']),
    dict(ref=(57, 2, 18), lang='ko', en='being', words=['시험을', '받아']),
    dict(ref=(57, 2, 18), lang='ko', en='tempted#1', words=['시험을', '받아']),
    dict(ref=(57, 2, 18), lang='ko', en='he#2', words=['능히']),
    dict(ref=(57, 2, 18), lang='ko', en='is', words=['능히']),
    dict(ref=(57, 2, 18), lang='ko', en='able', words=['능히']),
    dict(ref=(57, 2, 18), lang='ko', en='succour', words=['도우시느니라']),
    dict(ref=(57, 2, 18), lang='ko', en='them', words=['자들을']),
    dict(ref=(57, 2, 18), lang='ko', en='that#2', words=['시험', '받는']),
    dict(ref=(57, 2, 18), lang='ko', en='are', words=['시험', '받는']),
    dict(ref=(57, 2, 18), lang='ko', en='tempted#2', words=['시험', '받는']),

    dict(ref=(57, 2, 5), lang='ko', en='he', words=['하나님이']),
    dict(ref=(57, 2, 5), lang='ko', en='hath', words=['하심이']),
    dict(ref=(57, 2, 5), lang='ko', en='whereof', words=['바']),
    dict(ref=(57, 2, 10), lang='ko', en='the', words=['주를']),
    dict(ref=(57, 2, 10), lang='ko', en='captain', words=['주를']),
    dict(ref=(57, 2, 12), lang='ko', en='I#1', words=['내가#1']),
    dict(ref=(57, 2, 12), lang='ko', en='my', words=['내']),
    dict(ref=(57, 2, 12), lang='ko', en='I#2', words=['내가#2']),

    dict(ref=(57, 2, 18), lang='la', en='succour', words=['\u0061\u0075\u0078\u0069\u006c\u0069\u0061\u0072\u0069']),
    dict(ref=(57, 2, 18), lang='la', en='that#2', words=['\u0071\u0075\u0069']),
    dict(ref=(57, 2, 18), lang='la', en='being', words=['\u0074\u0065\u006e\u0074\u0061\u0074\u0075\u0073']),
    dict(ref=(57, 2, 18), lang='la', en='tempted#1', words=['\u0074\u0065\u006e\u0074\u0061\u0074\u0075\u0073']),
    dict(ref=(57, 2, 18), lang='la', en='suffered', words=['\u0070\u0061\u0073\u0073\u0075\u0073']),

    # ---- 히브리서 3장 ----
    dict(ref=(57, 3, 1), lang='ko', en='partakers', words=['함께', '입은']),
    dict(ref=(57, 3, 1), lang='ko', en='of#1', words=['부르심을']),
    dict(ref=(57, 3, 1), lang='ko', en='the#1', words=['부르심을']),
    dict(ref=(57, 3, 1), lang='ko', en='consider', words=['깊이', '생각하라']),
    dict(ref=(57, 3, 1), lang='ko', en='the#2', words=['사도시며']),
    dict(ref=(57, 3, 1), lang='ko', en='High', words=['대제사장이신']),
    dict(ref=(57, 3, 1), lang='ko', en='Priest', words=['대제사장이신']),
    dict(ref=(57, 3, 1), lang='ko', en='of#2', words=['우리의']),
    dict(ref=(57, 3, 1), lang='ko', en='profession', words=['믿는', '도리의']),
    dict(ref=(57, 3, 1), lang='ko', en='Christ', words=['예수를']),
    dict(ref=(57, 3, 1), lang='ko', en='Jesus', words=['예수를']),

    dict(ref=(57, 3, 3), lang='ko', en='this', words=['저는']),
    dict(ref=(57, 3, 3), lang='ko', en='man', words=['저는']),
    dict(ref=(57, 3, 3), lang='ko', en='was', words=['것이']),
    dict(ref=(57, 3, 3), lang='ko', en='counted', words=['것이']),
    dict(ref=(57, 3, 3), lang='ko', en='worthy', words=['받을', '만한']),
    dict(ref=(57, 3, 3), lang='ko', en='of', words=['영광을']),
    dict(ref=(57, 3, 3), lang='ko', en='more#1', words=['더욱#1']),
    dict(ref=(57, 3, 3), lang='ko', en='than#1', words=['모세보다']),
    dict(ref=(57, 3, 3), lang='ko', en='inasmuch', words=['마치']),
    dict(ref=(57, 3, 3), lang='ko', en='as', words=['마치', '같으니라']),
    dict(ref=(57, 3, 3), lang='ko', en='who', words=['자가']),
    dict(ref=(57, 3, 3), lang='ko', en='hath#1', words=['지은']),
    dict(ref=(57, 3, 3), lang='ko', en='the#1', words=['집']),
    dict(ref=(57, 3, 3), lang='ko', en='hath#2', words=['존귀함']),
    dict(ref=(57, 3, 3), lang='ko', en='more#2', words=['더욱#2']),
    dict(ref=(57, 3, 3), lang='ko', en='than#2', words=['집보다']),
    dict(ref=(57, 3, 3), lang='ko', en='the#2', words=['그']),
    dict(ref=(57, 3, 3), lang='ko', en='house#2', words=['집보다']),

    dict(ref=(57, 3, 4), lang='ko', en='For', words=[]),
    dict(ref=(57, 3, 4), lang='ko', en='every', words=['집마다']),
    dict(ref=(57, 3, 4), lang='ko', en='house', words=['집마다']),
    dict(ref=(57, 3, 4), lang='ko', en='is#1', words=['있으니']),
    dict(ref=(57, 3, 4), lang='ko', en='builded', words=['지은']),
    dict(ref=(57, 3, 4), lang='ko', en='by', words=['이가']),
    dict(ref=(57, 3, 4), lang='ko', en='some', words=['이가']),
    dict(ref=(57, 3, 4), lang='ko', en='man', words=['이가']),
    dict(ref=(57, 3, 4), lang='ko', en='he', words=['이는']),
    dict(ref=(57, 3, 4), lang='ko', en='that', words=['이는']),
    dict(ref=(57, 3, 4), lang='ko', en='built', words=['지으신']),
    dict(ref=(57, 3, 4), lang='ko', en='all', words=['만물을']),
    dict(ref=(57, 3, 4), lang='ko', en='things', words=['만물을']),
    dict(ref=(57, 3, 4), lang='ko', en='is#2', words=['하나님이시라']),

    dict(ref=(57, 3, 5), lang='ko', en='And', words=['또한']),
    dict(ref=(57, 3, 5), lang='ko', en='in', words=['집에서']),
    dict(ref=(57, 3, 5), lang='ko', en='his', words=['하나님의']),
    dict(ref=(57, 3, 5), lang='ko', en='a#1', words=['사환으로']),
    dict(ref=(57, 3, 5), lang='ko', en='for', words=['위하여']),
    dict(ref=(57, 3, 5), lang='ko', en='a#2', words=['증거하기']),
    dict(ref=(57, 3, 5), lang='ko', en='of', words=['것을']),
    dict(ref=(57, 3, 5), lang='ko', en='those', words=['것을']),
    dict(ref=(57, 3, 5), lang='ko', en='things', words=['것을']),
    dict(ref=(57, 3, 5), lang='ko', en='which', words=['말할']),
    dict(ref=(57, 3, 5), lang='ko', en='to', words=['말할']),
    dict(ref=(57, 3, 5), lang='ko', en='be', words=['말할']),
    dict(ref=(57, 3, 5), lang='ko', en='after', words=['장래의']),

    dict(ref=(57, 3, 6), lang='ko', en='as', words=['충성하였으니']),
    dict(ref=(57, 3, 6), lang='ko', en='a', words=['아들로']),
    dict(ref=(57, 3, 6), lang='ko', en='over', words=['맡은']),
    dict(ref=(57, 3, 6), lang='ko', en='his', words=['그의#1']),
    dict(ref=(57, 3, 6), lang='ko', en='own', words=['그의#1']),
    dict(ref=(57, 3, 6), lang='ko', en='house#1', words=['집']),
    dict(ref=(57, 3, 6), lang='ko', en='whose', words=['그의#2', '집이라']),
    dict(ref=(57, 3, 6), lang='ko', en='house#2', words=['그의#2', '집이라']),
    dict(ref=(57, 3, 6), lang='ko', en='are', words=['집이라']),
    dict(ref=(57, 3, 6), lang='ko', en='we#1', words=['우리가']),
    dict(ref=(57, 3, 6), lang='ko', en='if', words=['우리가']),
    dict(ref=(57, 3, 6), lang='ko', en='we#2', words=['우리가']),
    dict(ref=(57, 3, 6), lang='ko', en='fast', words=['잡으면']),
    dict(ref=(57, 3, 6), lang='ko', en='the#1', words=['담대함과']),
    dict(ref=(57, 3, 6), lang='ko', en='the#2', words=['자랑을']),
    dict(ref=(57, 3, 6), lang='ko', en='of', words=['소망의']),
    dict(ref=(57, 3, 6), lang='ko', en='the#3', words=['소망의']),
    dict(ref=(57, 3, 6), lang='ko', en='firm', words=['견고히']),
    dict(ref=(57, 3, 6), lang='ko', en='unto', words=['끝까지']),
    dict(ref=(57, 3, 6), lang='ko', en='the#4', words=['끝까지']),

    dict(ref=(57, 3, 7), lang='ko', en='the', words=['성령이']),
    dict(ref=(57, 3, 7), lang='ko', en='saith', words=['이르신']),
    dict(ref=(57, 3, 7), lang='ko', en='To', words=['오늘날']),
    dict(ref=(57, 3, 7), lang='ko', en='day', words=['오늘날']),
    dict(ref=(57, 3, 7), lang='ko', en='if', words=['듣거든']),
    dict(ref=(57, 3, 7), lang='ko', en='ye', words=['너희가']),
    dict(ref=(57, 3, 7), lang='ko', en='will', words=['듣거든']),

    dict(ref=(57, 3, 9), lang='or', en='When', words=['\u03bf\u1f57']),
    dict(ref=(57, 3, 9), lang='or', en='years', words=['\u1f14\u03c4\u03b7']),

    dict(ref=(57, 3, 8), lang='ko', en='not', words=['하지', '말라']),
    dict(ref=(57, 3, 8), lang='ko', en='as', words=['같이']),
    dict(ref=(57, 3, 8), lang='ko', en='in#1', words=['격동하여']),
    dict(ref=(57, 3, 8), lang='ko', en='the#1', words=['노하심을']),
    dict(ref=(57, 3, 8), lang='ko', en='provocation', words=['노하심을', '격동하여']),
    dict(ref=(57, 3, 8), lang='ko', en='in#2', words=['때와', '같이']),
    dict(ref=(57, 3, 8), lang='ko', en='the#2', words=['때와', '같이']),
    dict(ref=(57, 3, 8), lang='ko', en='day', words=['때와', '같이']),
    dict(ref=(57, 3, 8), lang='ko', en='of', words=['때와', '같이']),
    dict(ref=(57, 3, 8), lang='ko', en='temptation', words=['시험하던']),
    dict(ref=(57, 3, 8), lang='ko', en='in#3', words=['광야에서']),
    dict(ref=(57, 3, 8), lang='ko', en='the#3', words=['광야에서']),

    dict(ref=(57, 3, 9), lang='ko', en='When', words=['거기서']),
    dict(ref=(57, 3, 9), lang='ko', en='tempted', words=['시험하여']),
    dict(ref=(57, 3, 9), lang='ko', en='me#1', words=['나를']),
    dict(ref=(57, 3, 9), lang='ko', en='proved', words=['증험하고']),
    dict(ref=(57, 3, 9), lang='ko', en='me#2', words=['나를']),
    dict(ref=(57, 3, 9), lang='ko', en='and', words=[]),
    dict(ref=(57, 3, 9), lang='ko', en='forty', words=['사십', '년', '동안에']),
    dict(ref=(57, 3, 9), lang='ko', en='years', words=['사십', '년', '동안에']),

    dict(ref=(57, 3, 10), lang='or', en='I', words=['\u03c0\u03c1\u03bf\u03c3\u1f7d\u03c7\u03b8\u03b9\u03c3\u03b1']),
    dict(ref=(57, 3, 10), lang='or', en='They', words=['\u03b1\u1f50\u03c4\u03bf\u1f76']),
    dict(ref=(57, 3, 10), lang='or', en='they', words=['\u03b1\u1f50\u03c4\u03bf\u1f76']),

    dict(ref=(57, 3, 10), lang='ko', en='I', words=['내가']),
    dict(ref=(57, 3, 10), lang='ko', en='was', words=['노하여']),
    dict(ref=(57, 3, 10), lang='ko', en='grieved', words=['노하여']),
    dict(ref=(57, 3, 10), lang='ko', en='that', words=['이']),
    dict(ref=(57, 3, 10), lang='ko', en='They', words=['저희가']),
    dict(ref=(57, 3, 10), lang='ko', en='do', words=['미혹되어']),
    dict(ref=(57, 3, 10), lang='ko', en='in', words=['마음이']),
    dict(ref=(57, 3, 10), lang='ko', en='their', words=['마음이']),
    dict(ref=(57, 3, 10), lang='ko', en='they', words=['저희가']),
    dict(ref=(57, 3, 10), lang='ko', en='have', words=['알지']),
    dict(ref=(57, 3, 10), lang='ko', en='my', words=['내']),

    dict(ref=(57, 3, 12), lang='ko', en='Take', words=['삼가', '염려할', '것이요']),
    dict(ref=(57, 3, 12), lang='ko', en='heed', words=['삼가', '염려할', '것이요']),
    dict(ref=(57, 3, 12), lang='ko', en='lest', words=['혹']),
    dict(ref=(57, 3, 12), lang='ko', en='be', words=['품고']),
    dict(ref=(57, 3, 12), lang='ko', en='in#1', words=['중에']),
    dict(ref=(57, 3, 12), lang='ko', en='of#1', words=['중에']),
    dict(ref=(57, 3, 12), lang='ko', en='an', words=['악심을']),
    dict(ref=(57, 3, 12), lang='ko', en='evil', words=['악심을']),
    dict(ref=(57, 3, 12), lang='ko', en='heart', words=['악심을', '품고']),
    dict(ref=(57, 3, 12), lang='ko', en='of#2', words=['믿지']),
    dict(ref=(57, 3, 12), lang='ko', en='unbelief', words=['믿지', '아니하는']),
    dict(ref=(57, 3, 12), lang='ko', en='in#2', words=['떨어질까']),
    dict(ref=(57, 3, 12), lang='ko', en='departing', words=['떨어질까']),
    dict(ref=(57, 3, 12), lang='ko', en='from', words=['하나님에게서']),
    dict(ref=(57, 3, 12), lang='ko', en='the', words=['하나님에게서']),
    dict(ref=(57, 3, 12), lang='ko', en='living', words=['살아', '계신']),

    dict(ref=(57, 3, 16), lang='ko', en='For', words=['자가']),
    dict(ref=(57, 3, 16), lang='ko', en='some', words=['자가']),
    dict(ref=(57, 3, 16), lang='ko', en='they', words=['누구뇨']),
    dict(ref=(57, 3, 16), lang='ko', en='did', words=['하던']),
    dict(ref=(57, 3, 16), lang='ko', en='all', words=['모든']),
    dict(ref=(57, 3, 16), lang='ko', en='that', words=['이가']),
    dict(ref=(57, 3, 16), lang='ko', en='out', words=['애굽에서']),
    dict(ref=(57, 3, 16), lang='ko', en='of', words=['애굽에서']),
    dict(ref=(57, 3, 16), lang='ko', en='by', words=['좇아']),

    dict(ref=(57, 3, 18), lang='ko', en='to#1', words=['누구에게']),
    dict(ref=(57, 3, 18), lang='ko', en='he', words=['하나님이']),
    dict(ref=(57, 3, 18), lang='ko', en='that#1', words=['아니냐']),
    dict(ref=(57, 3, 18), lang='ko', en='should', words=['못하리라']),
    dict(ref=(57, 3, 18), lang='ko', en='but', words=['곧']),
    dict(ref=(57, 3, 18), lang='ko', en='to#2', words=['자에게가']),
    dict(ref=(57, 3, 18), lang='ko', en='them', words=['자에게가']),
    dict(ref=(57, 3, 18), lang='ko', en='that#2', words=['순종치']),
    dict(ref=(57, 3, 18), lang='ko', en='not#2', words=['아니하던']),

    dict(ref=(57, 3, 19), lang='ko', en='not', words=['못한']),
    dict(ref=(57, 3, 19), lang='ko', en='in', words=['들어가지']),
    dict(ref=(57, 3, 19), lang='ko', en='because', words=['아니하므로']),
    dict(ref=(57, 3, 19), lang='ko', en='of', words=['아니하므로']),
    dict(ref=(57, 3, 19), lang='ko', en='unbelief', words=['믿지', '아니하므로']),

    dict(ref=(57, 3, 11), lang='ko', en='So', words=['바와', '같이']),
    dict(ref=(57, 3, 11), lang='ko', en='I', words=['내가']),
    dict(ref=(57, 3, 11), lang='ko', en='sware', words=['맹세한']),
    dict(ref=(57, 3, 11), lang='ko', en='in', words=['노하여']),
    dict(ref=(57, 3, 11), lang='ko', en='my#1', words=['노하여']),
    dict(ref=(57, 3, 11), lang='ko', en='wrath', words=['노하여']),
    dict(ref=(57, 3, 11), lang='ko', en='shall', words=['못하리라']),
    dict(ref=(57, 3, 11), lang='ko', en='into', words=['들어오지']),
    dict(ref=(57, 3, 11), lang='ko', en='my#2', words=['내']),

    dict(ref=(57, 3, 17), lang='ko', en='But', words=['또']),
    dict(ref=(57, 3, 17), lang='ko', en='with#1', words=['누구에게']),
    dict(ref=(57, 3, 17), lang='ko', en='was#1', words=['노하셨느뇨']),
    dict(ref=(57, 3, 17), lang='ko', en='grieved', words=['노하셨느뇨']),
    dict(ref=(57, 3, 17), lang='ko', en='with#2', words=['자에게가']),
    dict(ref=(57, 3, 17), lang='ko', en='that', words=['자에게가']),
    dict(ref=(57, 3, 17), lang='ko', en='whose', words=['그']),
    dict(ref=(57, 3, 17), lang='ko', en='fell', words=['엎드러진']),
    dict(ref=(57, 3, 17), lang='ko', en='in', words=['광야에']),
    dict(ref=(57, 3, 17), lang='ko', en='the', words=['광야에']),

    dict(ref=(57, 4, 1), lang='ko', en='Let', words=['우리는']),
    dict(ref=(57, 4, 1), lang='ko', en='us#1', words=['우리는']),
    dict(ref=(57, 4, 1), lang='ko', en='fear', words=['두려워할지니']),
    dict(ref=(57, 4, 1), lang='ko', en='lest', words=['혹']),
    dict(ref=(57, 4, 1), lang='ko', en='being', words=['있을지라도']),
    dict(ref=(57, 4, 1), lang='ko', en='us#2', words=['우리는']),
    dict(ref=(57, 4, 1), lang='ko', en='of#1', words=['들어갈']),
    dict(ref=(57, 4, 1), lang='ko', en='of#2', words=['너희', '중에']),
    dict(ref=(57, 4, 1), lang='ko', en='you', words=['너희', '중에']),
    dict(ref=(57, 4, 1), lang='ko', en='seem', words=['있을까']),
    dict(ref=(57, 4, 1), lang='ko', en='to', words=['못할']),
    dict(ref=(57, 4, 1), lang='ko', en='come', words=['못할']),
    dict(ref=(57, 4, 1), lang='ko', en='short', words=['미치지']),
    dict(ref=(57, 4, 1), lang='ko', en='of#3', words=['미치지']),
    dict(ref=(57, 4, 1), lang='ko', en='it', words=['미치지']),

    # ---- 히브리서 4장 ----
    dict(ref=(57, 4, 2), lang='ko', en='unto#1', words=['우리도']),
    dict(ref=(57, 4, 2), lang='ko', en='was', words=['받은', '자이나']),
    dict(ref=(57, 4, 2), lang='ko', en='the#1', words=['복음']),
    dict(ref=(57, 4, 2), lang='ko', en='as#1', words=['같이']),
    dict(ref=(57, 4, 2), lang='ko', en='well', words=['같이']),
    dict(ref=(57, 4, 2), lang='ko', en='as#2', words=['같이']),
    dict(ref=(57, 4, 2), lang='ko', en='unto#2', words=['저희와']),
    dict(ref=(57, 4, 2), lang='ko', en='them#1', words=['저희와']),
    dict(ref=(57, 4, 2), lang='ko', en='the#2', words=['그']),
    dict(ref=(57, 4, 2), lang='ko', en='preached#2', words=['들은', '바']),
    dict(ref=(57, 4, 2), lang='ko', en='not#1', words=['못한']),
    dict(ref=(57, 4, 2), lang='ko', en='them#2', words=['저희에게']),
    dict(ref=(57, 4, 2), lang='ko', en='not#2', words=['아니함이라']),
    dict(ref=(57, 4, 2), lang='ko', en='being', words=['아니함이라']),
    dict(ref=(57, 4, 2), lang='ko', en='mixed', words=['화합지']),
    dict(ref=(57, 4, 2), lang='ko', en='with', words=['화합지']),
    dict(ref=(57, 4, 2), lang='ko', en='in', words=['듣는']),
    dict(ref=(57, 4, 2), lang='ko', en='them#3', words=['자가']),

    dict(ref=(57, 4, 3), lang='ko', en='we', words=['우리들은']),
    dict(ref=(57, 4, 3), lang='ko', en='which', words=['우리들은']),
    dict(ref=(57, 4, 3), lang='ko', en='do', words=['이미']),
    dict(ref=(57, 4, 3), lang='ko', en='as#1', words=['바와#1', '같으니']),
    dict(ref=(57, 4, 3), lang='ko', en='said', words=['그#1', '말씀하신']),
    dict(ref=(57, 4, 3), lang='ko', en='As', words=['바와#2', '같이']),
    dict(ref=(57, 4, 3), lang='ko', en='I', words=['내가']),
    dict(ref=(57, 4, 3), lang='ko', en='have#2', words=['맹세한']),
    dict(ref=(57, 4, 3), lang='ko', en='in', words=['노하여']),
    dict(ref=(57, 4, 3), lang='ko', en='my#1', words=['노하여']),
    dict(ref=(57, 4, 3), lang='ko', en='if', words=['못하리라']),
    dict(ref=(57, 4, 3), lang='ko', en='shall', words=['못하리라']),
    dict(ref=(57, 4, 3), lang='ko', en='enter#2', words=['들어오지']),
    dict(ref=(57, 4, 3), lang='ko', en='into#2', words=['들어오지']),
    dict(ref=(57, 4, 3), lang='ko', en='my#2', words=['내']),
    dict(ref=(57, 4, 3), lang='ko', en='although', words=['하였으나']),
    dict(ref=(57, 4, 3), lang='ko', en='the#1', words=['그#2']),
    dict(ref=(57, 4, 3), lang='ko', en='were', words=['이루었느니라']),
    dict(ref=(57, 4, 3), lang='ko', en='finished', words=['이루었느니라']),
    dict(ref=(57, 4, 3), lang='ko', en='from', words=['때부터']),
    dict(ref=(57, 4, 3), lang='ko', en='foundation', words=['창조할']),
    dict(ref=(57, 4, 3), lang='ko', en='of', words=['세상을']),

    dict(ref=(57, 4, 4), lang='ko', en='spake', words=['일렀으되']),
    dict(ref=(57, 4, 4), lang='ko', en='in', words=['관하여는']),
    dict(ref=(57, 4, 4), lang='ko', en='a', words=['어디']),
    dict(ref=(57, 4, 4), lang='ko', en='certain', words=['어디']),
    dict(ref=(57, 4, 4), lang='ko', en='place', words=['어디']),
    dict(ref=(57, 4, 4), lang='ko', en='of', words=['관하여는']),
    dict(ref=(57, 4, 4), lang='ko', en='this', words=['이렇게']),
    dict(ref=(57, 4, 4), lang='ko', en='And', words=['하였으며']),
    dict(ref=(57, 4, 4), lang='ko', en='did', words=['쉬셨다']),
    dict(ref=(57, 4, 4), lang='ko', en='from', words=['일을']),

    dict(ref=(57, 4, 6), lang='ko', en='Seeing', words=['그러면']),
    dict(ref=(57, 4, 6), lang='ko', en='remaineth', words=['남아', '있거니와']),
    dict(ref=(57, 4, 6), lang='ko', en='it#1', words=['있거니와']),
    dict(ref=(57, 4, 6), lang='ko', en='some', words=['자들이']),
    dict(ref=(57, 4, 6), lang='ko', en='must', words=['들어갈']),
    dict(ref=(57, 4, 6), lang='ko', en='they', words=['자들은']),
    dict(ref=(57, 4, 6), lang='ko', en='to', words=['자들은']),
    dict(ref=(57, 4, 6), lang='ko', en='whom', words=['자들은']),
    dict(ref=(57, 4, 6), lang='ko', en='it#2', words=['복음']),
    dict(ref=(57, 4, 6), lang='ko', en='was', words=['받은']),
    dict(ref=(57, 4, 6), lang='ko', en='and', words=['받은']),
    dict(ref=(57, 4, 6), lang='ko', en='entered', words=['들어가지']),
    dict(ref=(57, 4, 6), lang='ko', en='in', words=['들어가지']),
    dict(ref=(57, 4, 6), lang='ko', en='not', words=['못하였으므로']),
    dict(ref=(57, 4, 6), lang='ko', en='of', words=['인하여']),
    dict(ref=(57, 4, 6), lang='ko', en='unbelief', words=['순종치', '아니함을']),

    dict(ref=(57, 4, 7), lang='ko', en='in', words=['글에']),
    dict(ref=(57, 4, 7), lang='ko', en='David', words=['다윗의', '글에']),
    dict(ref=(57, 4, 7), lang='ko', en='a#1', words=['어느']),
    dict(ref=(57, 4, 7), lang='ko', en='certain', words=['어느']),
    dict(ref=(57, 4, 7), lang='ko', en='limiteth', words=['정하여']),
    dict(ref=(57, 4, 7), lang='ko', en='day#1', words=['날을']),
    dict(ref=(57, 4, 7), lang='ko', en='saying', words=['일렀으되']),
    dict(ref=(57, 4, 7), lang='ko', en='To#1', words=['오늘날이라고']),
    dict(ref=(57, 4, 7), lang='ko', en='day#2', words=['오늘날이라고']),
    dict(ref=(57, 4, 7), lang='ko', en='long', words=['오랜']),
    dict(ref=(57, 4, 7), lang='ko', en='as', words=['이같이']),
    dict(ref=(57, 4, 7), lang='ko', en='it', words=['미리']),
    dict(ref=(57, 4, 7), lang='ko', en='is', words=['미리']),
    dict(ref=(57, 4, 7), lang='ko', en='To#2', words=['오늘날']),
    dict(ref=(57, 4, 7), lang='ko', en='day#3', words=['오늘날']),
    dict(ref=(57, 4, 7), lang='ko', en='ye', words=['너희가']),
    dict(ref=(57, 4, 7), lang='ko', en='hear', words=['듣거든']),
    dict(ref=(57, 4, 7), lang='ko', en='your', words=['너희']),

    dict(ref=(57, 4, 8), lang='ko', en='Jesus', words=['여호수아가']),
    dict(ref=(57, 4, 8), lang='ko', en='then', words=['그']),
    dict(ref=(57, 4, 8), lang='ko', en='would', words=['아니하셨으리라']),
    dict(ref=(57, 4, 8), lang='ko', en='not', words=['아니하셨으리라']),
    dict(ref=(57, 4, 8), lang='ko', en='have', words=['말씀하지']),
    dict(ref=(57, 4, 8), lang='ko', en='of', words=['날을']),

    dict(ref=(57, 4, 9), lang='ko', en='a', words=['때가']),
    dict(ref=(57, 4, 9), lang='ko', en='rest', words=['안식할', '때가']),
    dict(ref=(57, 4, 9), lang='ko', en='to', words=['백성에게']),
    dict(ref=(57, 4, 9), lang='ko', en='the', words=['백성에게']),
    dict(ref=(57, 4, 9), lang='ko', en='of', words=['하나님의']),

    dict(ref=(57, 4, 10), lang='ko', en='he#1', words=['자는']),
    dict(ref=(57, 4, 10), lang='ko', en='is', words=['이미']),
    dict(ref=(57, 4, 10), lang='ko', en='he#2', words=['쉬느니라']),
    dict(ref=(57, 4, 10), lang='ko', en='also', words=['쉬느니라']),
    dict(ref=(57, 4, 10), lang='ko', en='hath', words=['쉬느니라']),
    dict(ref=(57, 4, 10), lang='ko', en='ceased', words=['쉬느니라']),
    dict(ref=(57, 4, 10), lang='ko', en='from#1', words=['일을#2']),
    dict(ref=(57, 4, 10), lang='ko', en='his#2', words=['자기#2']),
    dict(ref=(57, 4, 10), lang='ko', en='own', words=['자기#2']),
    dict(ref=(57, 4, 10), lang='ko', en='works', words=['일을#2']),
    dict(ref=(57, 4, 10), lang='ko', en='as', words=['같이']),
    dict(ref=(57, 4, 10), lang='ko', en='God', words=['하나님이']),
    dict(ref=(57, 4, 10), lang='ko', en='did', words=['쉬심과']),
    dict(ref=(57, 4, 10), lang='ko', en='from#2', words=['일을#1']),
    dict(ref=(57, 4, 10), lang='ko', en='his#3', words=['자기#1']),

    dict(ref=(57, 4, 11), lang='ko', en='Let', words=['우리가']),
    dict(ref=(57, 4, 11), lang='ko', en='labour', words=['힘쓸지니']),
    dict(ref=(57, 4, 11), lang='ko', en='to', words=['하려']),
    dict(ref=(57, 4, 11), lang='ko', en='that', words=['저#1']),
    dict(ref=(57, 4, 11), lang='ko', en='lest', words=['이는', '함이라']),
    dict(ref=(57, 4, 11), lang='ko', en='any', words=['않게']),
    dict(ref=(57, 4, 11), lang='ko', en='man', words=['누구든지']),
    dict(ref=(57, 4, 11), lang='ko', en='after', words=['본에']),
    dict(ref=(57, 4, 11), lang='ko', en='the', words=['본에']),
    dict(ref=(57, 4, 11), lang='ko', en='same', words=['저#2']),
    dict(ref=(57, 4, 11), lang='ko', en='of', words=['아니하는']),
    dict(ref=(57, 4, 11), lang='ko', en='unbelief', words=['순종치', '아니하는']),

    dict(ref=(57, 4, 12), lang='ko', en='the#1', words=['말씀은']),
    dict(ref=(57, 4, 12), lang='ko', en='is#1', words=['있어']),
    dict(ref=(57, 4, 12), lang='ko', en='quick', words=['살았고']),
    dict(ref=(57, 4, 12), lang='ko', en='and#1', words=['운동력이']),
    dict(ref=(57, 4, 12), lang='ko', en='powerful', words=['운동력이', '있어']),
    dict(ref=(57, 4, 12), lang='ko', en='and#2', words=['예리하여']),
    dict(ref=(57, 4, 12), lang='ko', en='sharper', words=['예리하여']),
    dict(ref=(57, 4, 12), lang='ko', en='than', words=['검보다도']),
    dict(ref=(57, 4, 12), lang='ko', en='any', words=['어떤']),
    dict(ref=(57, 4, 12), lang='ko', en='twoedged', words=['죄우에', '날선']),
    dict(ref=(57, 4, 12), lang='ko', en='even', words=['쪼개기까지']),
    dict(ref=(57, 4, 12), lang='ko', en='to', words=['쪼개기까지']),
    dict(ref=(57, 4, 12), lang='ko', en='the#2', words=['쪼개기까지']),
    dict(ref=(57, 4, 12), lang='ko', en='dividing', words=['쪼개기까지']),
    dict(ref=(57, 4, 12), lang='ko', en='asunder', words=['쪼개기까지', '하며']),
    dict(ref=(57, 4, 12), lang='ko', en='of#2', words=['혼과']),
    dict(ref=(57, 4, 12), lang='ko', en='and#3', words=['영과']),
    dict(ref=(57, 4, 12), lang='ko', en='spirit', words=['영과']),
    dict(ref=(57, 4, 12), lang='ko', en='and#4', words=['및']),
    dict(ref=(57, 4, 12), lang='ko', en='of#3', words=['관절과']),
    dict(ref=(57, 4, 12), lang='ko', en='the#3', words=['관절과']),
    dict(ref=(57, 4, 12), lang='ko', en='joints', words=['관절과']),
    dict(ref=(57, 4, 12), lang='ko', en='and#5', words=['골수를']),
    dict(ref=(57, 4, 12), lang='ko', en='and#6', words=['또']),
    dict(ref=(57, 4, 12), lang='ko', en='is#2', words=['감찰하나니']),
    dict(ref=(57, 4, 12), lang='ko', en='a', words=['감찰하나니']),
    dict(ref=(57, 4, 12), lang='ko', en='discerner', words=['감찰하나니']),
    dict(ref=(57, 4, 12), lang='ko', en='of#4', words=['생각과']),
    dict(ref=(57, 4, 12), lang='ko', en='thoughts', words=['생각과']),
    dict(ref=(57, 4, 12), lang='ko', en='and#7', words=['뜻을']),
    dict(ref=(57, 4, 12), lang='ko', en='intents', words=['뜻을']),
    dict(ref=(57, 4, 12), lang='ko', en='of#5', words=['마음의']),
    dict(ref=(57, 4, 12), lang='ko', en='the#5', words=['마음의']),
    dict(ref=(57, 4, 12), lang='ko', en='the#4', words=['마음의']),

    dict(ref=(57, 4, 13), lang='ko', en='Neither', words=['없고']),
    dict(ref=(57, 4, 13), lang='ko', en='is#1', words=['없고']),
    dict(ref=(57, 4, 13), lang='ko', en='any', words=['하나라도']),
    dict(ref=(57, 4, 13), lang='ko', en='creature', words=['지으신', '것이']),
    dict(ref=(57, 4, 13), lang='ko', en='that', words=['것이']),
    dict(ref=(57, 4, 13), lang='ko', en='is#2', words=['나타나지']),
    dict(ref=(57, 4, 13), lang='ko', en='manifest', words=['나타나지']),
    dict(ref=(57, 4, 13), lang='ko', en='sight', words=['앞에#1']),
    dict(ref=(57, 4, 13), lang='ko', en='are', words=['드러나느니라']),
    dict(ref=(57, 4, 13), lang='ko', en='and', words=['것', '같이']),
    dict(ref=(57, 4, 13), lang='ko', en='opened', words=['드러나느니라']),
    dict(ref=(57, 4, 13), lang='ko', en='unto', words=['앞에#2']),
    dict(ref=(57, 4, 13), lang='ko', en='the', words=['눈']),
    dict(ref=(57, 4, 13), lang='ko', en='of', words=['자의']),
    dict(ref=(57, 4, 13), lang='ko', en='him', words=['자의']),
    dict(ref=(57, 4, 13), lang='ko', en='with', words=['상관하시는']),
    dict(ref=(57, 4, 13), lang='ko', en='whom', words=['상관하시는']),
    dict(ref=(57, 4, 13), lang='ko', en='have', words=['상관하시는']),
    dict(ref=(57, 4, 13), lang='ko', en='to', words=['상관하시는']),
    dict(ref=(57, 4, 13), lang='ko', en='do', words=['상관하시는']),

    dict(ref=(57, 4, 14), lang='ko', en='Seeing', words=['그러므로']),
    dict(ref=(57, 4, 14), lang='ko', en='that#1', words=['우리에게']),
    dict(ref=(57, 4, 14), lang='ko', en='we', words=['우리에게']),
    dict(ref=(57, 4, 14), lang='ko', en='a', words=['있으니']),
    dict(ref=(57, 4, 14), lang='ko', en='that#2', words=['자']),
    dict(ref=(57, 4, 14), lang='ko', en='is', words=['자']),
    dict(ref=(57, 4, 14), lang='ko', en='passed', words=['승천하신']),
    dict(ref=(57, 4, 14), lang='ko', en='into', words=['승천하신']),
    dict(ref=(57, 4, 14), lang='ko', en='the#1', words=['승천하신']),
    dict(ref=(57, 4, 14), lang='ko', en='heavens', words=['승천하신']),
    dict(ref=(57, 4, 14), lang='ko', en='let', words=['우리가']),
    dict(ref=(57, 4, 14), lang='ko', en='us', words=['우리가']),
    dict(ref=(57, 4, 14), lang='ko', en='our', words=['우리가']),
    dict(ref=(57, 4, 14), lang='ko', en='hold', words=['잡을지어다']),
    dict(ref=(57, 4, 14), lang='ko', en='profession', words=['믿는', '도리를']),

    dict(ref=(57, 4, 15), lang='ko', en='which', words=['자가']),
    dict(ref=(57, 4, 15), lang='ko', en='cannot', words=['아니하는']),
    dict(ref=(57, 4, 15), lang='ko', en='be', words=['체휼하지']),
    dict(ref=(57, 4, 15), lang='ko', en='touched', words=['체휼하지']),
    dict(ref=(57, 4, 15), lang='ko', en='with', words=['체휼하지']),
    dict(ref=(57, 4, 15), lang='ko', en='feeling', words=['체휼하지']),
    dict(ref=(57, 4, 15), lang='ko', en='of', words=['연약함을']),
    dict(ref=(57, 4, 15), lang='ko', en='but', words=['자로되']),
    dict(ref=(57, 4, 15), lang='ko', en='yet', words=['자로되']),
    dict(ref=(57, 4, 15), lang='ko', en='was', words=['받은']),
    dict(ref=(57, 4, 15), lang='ko', en='in', words=['일에']),
    dict(ref=(57, 4, 15), lang='ko', en='points', words=['일에']),
    dict(ref=(57, 4, 15), lang='ko', en='tempted', words=['시험을', '받은']),
    dict(ref=(57, 4, 15), lang='ko', en='like', words=['한결']),
    dict(ref=(57, 4, 15), lang='ko', en='we#2', words=['우리와']),
    dict(ref=(57, 4, 15), lang='ko', en='are', words=['우리와']),

    dict(ref=(57, 4, 16), lang='ko', en='come', words=['나아갈']),
    dict(ref=(57, 4, 16), lang='ko', en='unto', words=['앞에']),
    dict(ref=(57, 4, 16), lang='ko', en='the', words=['보좌']),
    dict(ref=(57, 4, 16), lang='ko', en='of#1', words=['은혜의']),
    dict(ref=(57, 4, 16), lang='ko', en='grace#1', words=['은혜의']),
    dict(ref=(57, 4, 16), lang='ko', en='and', words=['얻기']),
    dict(ref=(57, 4, 16), lang='ko', en='find', words=['얻기']),
    dict(ref=(57, 4, 16), lang='ko', en='grace#2', words=['은혜를']),
    dict(ref=(57, 4, 16), lang='ko', en='to', words=['돕는']),
    dict(ref=(57, 4, 16), lang='ko', en='help', words=['돕는']),
    dict(ref=(57, 4, 16), lang='ko', en='in', words=['따라']),
    dict(ref=(57, 4, 16), lang='ko', en='of#2', words=['따라']),
    dict(ref=(57, 4, 16), lang='ko', en='need', words=['따라']),

    # ---- 사무엘상 1장 ----
    dict(ref=(8, 1, 2), lang='ko', en='had#1', words=['있으니']),
    dict(ref=(8, 1, 2), lang='ko', en='was', words=['있으니']),
    dict(ref=(8, 1, 2), lang='ko', en='one', words=['하나의#1']),
    dict(ref=(8, 1, 2), lang='ko', en='other', words=['하나의#2']),
    dict(ref=(8, 1, 2), lang='ko', en='had#2', words=['있고']),
    dict(ref=(8, 1, 2), lang='ko', en='children#1', words=['자식이']),
    dict(ref=(8, 1, 2), lang='ko', en='but', words=['한나는']),
    dict(ref=(8, 1, 2), lang='ko', en='had#3', words=['무자하더라']),
    dict(ref=(8, 1, 2), lang='ko', en='no', words=['무자하더라']),
    dict(ref=(8, 1, 2), lang='ko', en='children#2', words=['무자하더라']),

    # ---- 해마다·매년 / yearly·year by year ----
    dict(ref=(1, 13, 10), lang='ko', en='from', words=['연년이']),
    dict(ref=(1, 13, 10), lang='ko', en='year#1', words=['연년이']),
    dict(ref=(1, 13, 10), lang='ko', en='to', words=['연년이']),
    dict(ref=(1, 13, 10), lang='ko', en='year#2', words=['연년이']),

    dict(ref=(1, 23, 14), lang='ko', en='in', words=['매년']),
    dict(ref=(1, 23, 14), lang='ko', en='the', words=['매년']),
    dict(ref=(1, 23, 14), lang='ko', en='year', words=['매년']),

    dict(ref=(1, 23, 17), lang='ko', en='in', words=['매년']),
    dict(ref=(1, 23, 17), lang='ko', en='the#1', words=['매년']),
    dict(ref=(1, 23, 17), lang='ko', en='year', words=['매년']),

    dict(ref=(1, 34, 23), lang='ko', en='in', words=['매년']),
    dict(ref=(1, 34, 23), lang='ko', en='the#1', words=['매년']),
    dict(ref=(1, 34, 23), lang='ko', en='year', words=['매년']),

    dict(ref=(1, 34, 24), lang='ko', en='in', words=['매년']),
    dict(ref=(1, 34, 24), lang='ko', en='the#3', words=['매년']),
    dict(ref=(1, 34, 24), lang='ko', en='year', words=['매년']),

    dict(ref=(2, 23, 41), lang='ko', en='in#1', words=['매년에']),
    dict(ref=(2, 23, 41), lang='ko', en='the#2', words=['매년에']),
    dict(ref=(2, 23, 41), lang='ko', en='year', words=['매년에']),

    dict(ref=(2, 25, 53), lang='ko', en='yearly', words=['매년의']),

    dict(ref=(4, 14, 22), lang='ko', en='year#1', words=['매년에']),
    dict(ref=(4, 14, 22), lang='ko', en='by', words=['매년에']),
    dict(ref=(4, 14, 22), lang='ko', en='year#2', words=['매년에']),

    dict(ref=(4, 15, 20), lang='ko', en='year#1', words=['매년에']),
    dict(ref=(4, 15, 20), lang='ko', en='by', words=['매년에']),
    dict(ref=(4, 15, 20), lang='ko', en='year#2', words=['매년에']),

    dict(ref=(6, 21, 19), lang='ko', en='yearly', words=['매년']),

    dict(ref=(8, 1, 3), lang='ko', en='yearly', words=['매년에']),

    dict(ref=(8, 1, 7), lang='ko', en='year#1', words=['매년에']),
    dict(ref=(8, 1, 7), lang='ko', en='by', words=['매년에']),
    dict(ref=(8, 1, 7), lang='ko', en='year#2', words=['매년에']),

    dict(ref=(8, 1, 21), lang='ko', en='the#3', words=['매년제와']),
    dict(ref=(8, 1, 21), lang='ko', en='yearly', words=['매년제와']),
    dict(ref=(8, 1, 21), lang='ko', en='sacrifice', words=['매년제와']),

    dict(ref=(8, 2, 19), lang='ko', en='from', words=['때마다']),
    dict(ref=(8, 2, 19), lang='ko', en='year#1', words=['때마다']),
    dict(ref=(8, 2, 19), lang='ko', en='to#2', words=['때마다']),
    dict(ref=(8, 2, 19), lang='ko', en='year#2', words=['때마다']),
    dict(ref=(8, 2, 19), lang='ko', en='the', words=['매년제를']),
    dict(ref=(8, 2, 19), lang='ko', en='yearly', words=['매년제를']),
    dict(ref=(8, 2, 19), lang='ko', en='sacrifice', words=['매년제를']),

    dict(ref=(8, 20, 6), lang='ko', en='yearly', words=['매년제를']),
    dict(ref=(8, 20, 6), lang='ko', en='sacrifice', words=['매년제를']),

    # ---- 사무엘상 1:5 ----
    # 원어-영어 연결이 먼저 틀어져 있었다: וַיהוָה(and the LORD)가 he·up 에,
    # סָגַר(shut)이 had·shut 에만 걸려 있어서, 영어를 축으로 삼는 한국어가
    # 여호와께서→up, Lord→하시니 처럼 통째로 밀렸다. 원어 쪽부터 바로잡는다.
    dict(ref=(8, 1, 5), lang='or', en='he#1', words=['\u05d9\u05b4\u05ea\u05bc\u05b5\u05df']),
    dict(ref=(8, 1, 5), lang='or', en='gave', words=['\u05d9\u05b4\u05ea\u05bc\u05b5\u05df']),
    dict(ref=(8, 1, 5), lang='or', en='a', words=['\u05d0\u05b7\u05d7\u05b7\u05ea']),
    dict(ref=(8, 1, 5), lang='or', en='worthy', words=['\u05d0\u05b7\u05e4\u05bc\u05b8\u05d9\u05b4\u05dd']),
    dict(ref=(8, 1, 5), lang='or', en='portion', words=['\u05de\u05b8\u05e0\u05b8\u05d4']),
    dict(ref=(8, 1, 5), lang='or', en='Hannah#2', words=['\u05d0\u05b6\u05ea', '\u05d7\u05b7\u05e0\u05bc\u05b8\u05d4']),
    dict(ref=(8, 1, 5), lang='or', en='the', words=['\u05d5\u05b7\u05d9\u05d4\u05d5\u05b8\u05d4']),
    dict(ref=(8, 1, 5), lang='or', en='Lord', words=['\u05d5\u05b7\u05d9\u05d4\u05d5\u05b8\u05d4']),
    dict(ref=(8, 1, 5), lang='or', en='had', words=['\u05e1\u05b8\u05d2\u05b7\u05e8']),
    dict(ref=(8, 1, 5), lang='or', en='shut', words=['\u05e1\u05b8\u05d2\u05b7\u05e8']),
    dict(ref=(8, 1, 5), lang='or', en='up', words=['\u05e1\u05b8\u05d2\u05b7\u05e8']),

    # 한국어: KJV 'unto Hannah he gave a worthy portion' 과 개역한글
    # '한나에게는 갑절을 주니' 는 어순이 뒤집혀 있다
    dict(ref=(8, 1, 5), lang='ko', en='But', words=['한나에게는']),
    dict(ref=(8, 1, 5), lang='ko', en='unto', words=['한나에게는']),
    dict(ref=(8, 1, 5), lang='ko', en='Hannah#1', words=['한나에게는']),
    dict(ref=(8, 1, 5), lang='ko', en='he#1', words=['주니']),
    dict(ref=(8, 1, 5), lang='ko', en='gave', words=['주니']),
    dict(ref=(8, 1, 5), lang='ko', en='a', words=['갑절을']),
    dict(ref=(8, 1, 5), lang='ko', en='worthy', words=['갑절을']),
    dict(ref=(8, 1, 5), lang='ko', en='portion', words=['갑절을']),
    dict(ref=(8, 1, 5), lang='ko', en='for', words=['이는']),
    dict(ref=(8, 1, 5), lang='ko', en='he#2', words=['사랑함이라']),
    dict(ref=(8, 1, 5), lang='ko', en='loved', words=['사랑함이라']),
    dict(ref=(8, 1, 5), lang='ko', en='Hannah#2', words=['그를']),
    dict(ref=(8, 1, 5), lang='ko', en='but', words=['그러나']),
    dict(ref=(8, 1, 5), lang='ko', en='the', words=['여호와께서']),
    dict(ref=(8, 1, 5), lang='ko', en='Lord', words=['여호와께서']),
    dict(ref=(8, 1, 5), lang='ko', en='had', words=['하시니']),
    dict(ref=(8, 1, 5), lang='ko', en='shut', words=['못하게']),
    dict(ref=(8, 1, 5), lang='ko', en='up', words=['못하게']),
    dict(ref=(8, 1, 5), lang='ko', en='her', words=['그로']),
    dict(ref=(8, 1, 5), lang='ko', en='womb', words=['성태치']),

    # ---- 날마다·매일·일일이 / every day · day by day ----
    dict(ref=(1, 29, 36), lang='ko', en='every', words=['매일']),
    dict(ref=(1, 29, 36), lang='ko', en='day', words=['매일']),

    dict(ref=(3, 28, 3), lang='ko', en='day#1', words=['매일']),
    dict(ref=(3, 28, 3), lang='ko', en='by#2', words=['매일']),
    dict(ref=(3, 28, 3), lang='ko', en='day#2', words=['매일']),

    dict(ref=(8, 23, 14), lang='ko', en='every', words=['매일']),
    dict(ref=(8, 23, 14), lang='ko', en='day', words=['매일']),

    dict(ref=(9, 13, 4), lang='ko', en='from', words=['나날이']),
    dict(ref=(9, 13, 4), lang='ko', en='day#1', words=['나날이']),
    dict(ref=(9, 13, 4), lang='ko', en='to', words=['나날이']),
    dict(ref=(9, 13, 4), lang='ko', en='day#2', words=['나날이']),

    dict(ref=(12, 26, 17), lang='ko', en='a#1', words=['매일#1']),
    dict(ref=(12, 26, 17), lang='ko', en='day#1', words=['매일#1']),
    dict(ref=(12, 26, 17), lang='ko', en='a#2', words=['매일#2']),
    dict(ref=(12, 26, 17), lang='ko', en='day#2', words=['매일#2']),

    dict(ref=(13, 8, 13), lang='ko', en='every', words=['매일에']),
    dict(ref=(13, 8, 13), lang='ko', en='day', words=['매일에']),

    dict(ref=(13, 8, 14), lang='ko', en='every#1', words=['매일에']),
    dict(ref=(13, 8, 14), lang='ko', en='day', words=['매일에']),

    dict(ref=(18, 7, 11), lang='ko', en='every', words=['매일']),
    dict(ref=(18, 7, 11), lang='ko', en='day', words=['매일']),

    dict(ref=(22, 27, 12), lang='ko', en='one#1', words=['일일이']),
    dict(ref=(22, 27, 12), lang='ko', en='by', words=['일일이']),
    dict(ref=(22, 27, 12), lang='ko', en='one#2', words=['일일이']),

    dict(ref=(25, 43, 25), lang='ko', en='every', words=['매일']),
    dict(ref=(25, 43, 25), lang='ko', en='day', words=['매일']),

    dict(ref=(41, 13, 14), lang='ko', en='sabbath#2', words=['안식일에는']),
    dict(ref=(41, 13, 14), lang='ko', en='day#2', words=['안식일에는']),

    # ---- 각기·각각·사람마다 / every man · every one ----
    # 구약은 개역한글이 의역한 자리가 많아 건너뛰고, 민 29:14 와 신약만 맞춘다.
    dict(ref=(3, 29, 14), lang='ko', en='every', words=['각기#1']),
    dict(ref=(3, 29, 14), lang='ko', en='each', words=['각기#2']),

    dict(ref=(44, 14, 12), lang='ko', en='every', words=['각인이']),
    dict(ref=(44, 14, 12), lang='ko', en='one', words=['각인이']),

    dict(ref=(49, 2, 4), lang='ko', en='every#2', words=['각각#2']),
    dict(ref=(49, 2, 4), lang='ko', en='man#2', words=['각각#2']),

    dict(ref=(57, 8, 11), lang='ko', en='every#2', words=['각각#2']),
    dict(ref=(57, 8, 11), lang='ko', en='man#2', words=['각각#2']),

    dict(ref=(65, 1, 7), lang='ko', en='every', words=['각인의']),
    # 'every' 를 각인의로 옮기면서 '모든'(all kindreds) 이 비게 되므로 같이 걸어 준다
    dict(ref=(65, 1, 7), lang='ko', en='all', words=['모든']),
    dict(ref=(65, 1, 7), lang='ko', en='kindreds', words=['족속이']),
    dict(ref=(65, 1, 7), lang='ko', en='see', words=['보겠고']),

    dict(ref=(65, 22, 18), lang='ko', en='every', words=['각인에게']),
    dict(ref=(65, 22, 18), lang='ko', en='man#1', words=['각인에게']),

    # ---- 히브리서 11:1 ----
    dict(ref=(57, 11, 1), lang='ko', en='Now', words=['믿음은']),
    dict(ref=(57, 11, 1), lang='ko', en='faith', words=['믿음은']),
    dict(ref=(57, 11, 1), lang='ko', en='is', words=[]),   # KJV 의 is 에 맞는 한국어가 없다
    dict(ref=(57, 11, 1), lang='ko', en='the#1', words=['실상이요']),
    dict(ref=(57, 11, 1), lang='ko', en='substance', words=['실상이요']),
    dict(ref=(57, 11, 1), lang='ko', en='of#1', words=['것들의#1']),
    dict(ref=(57, 11, 1), lang='ko', en='things#1', words=['것들의#1']),
    dict(ref=(57, 11, 1), lang='ko', en='hoped', words=['바라는']),
    dict(ref=(57, 11, 1), lang='ko', en='for', words=['바라는']),
    dict(ref=(57, 11, 1), lang='ko', en='the#2', words=['증거니']),
    dict(ref=(57, 11, 1), lang='ko', en='evidence', words=['증거니']),
    dict(ref=(57, 11, 1), lang='ko', en='of#2', words=['것들의#2']),
    dict(ref=(57, 11, 1), lang='ko', en='things#2', words=['것들의#2']),
    dict(ref=(57, 11, 1), lang='ko', en='not', words=['못하는']),
    dict(ref=(57, 11, 1), lang='ko', en='seen', words=['보지']),

    # ---- 그리스도 / Christ 가 조사 자리에 걸려 있던 17곳 ----
    # 'in Christ Jesus' → '그리스도 예수 안에서' 처럼 어순이 뒤집히면서
    # Christ 가 그리스도 대신 안에서·말미암아 같은 뒤쪽 조사에 붙어 있었다.
    dict(ref=(43, 4, 10), lang='ko', en='Be', words=['알라']),
    dict(ref=(43, 4, 10), lang='ko', en='known', words=['알라']),
    dict(ref=(43, 4, 10), lang='ko', en='Christ', words=['그리스도의']),
    dict(ref=(43, 4, 10), lang='ko', en='whole', words=['건강하게', '되어']),

    dict(ref=(44, 5, 21), lang='ko', en='unto#1', words=['안에서']),
    dict(ref=(44, 5, 21), lang='ko', en='even', words=['또한']),
    dict(ref=(44, 5, 21), lang='ko', en='reign', words=['왕#2', '노릇#2', '하여']),
    dict(ref=(44, 5, 21), lang='ko', en='Christ', words=['그리스도로']),
    dict(ref=(44, 5, 21), lang='ko', en='by', words=['말미암아#2']),

    dict(ref=(44, 6, 11), lang='ko', en='Likewise', words=['이와', '같이']),
    dict(ref=(44, 6, 11), lang='ko', en='through', words=['안에서']),
    dict(ref=(44, 6, 11), lang='ko', en='Christ', words=['그리스도']),

    dict(ref=(44, 6, 23), lang='ko', en='is#2', words=['있는']),
    dict(ref=(44, 6, 23), lang='ko', en='through', words=['안에']),
    dict(ref=(44, 6, 23), lang='ko', en='Christ', words=['그리스도']),

    dict(ref=(45, 8, 6), lang='ko', en='to#1', words=['우리에게는']),
    dict(ref=(45, 8, 6), lang='ko', en='is', words=['계시니#1']),
    dict(ref=(45, 8, 6), lang='ko', en='in', words=['그를', '위하여']),
    dict(ref=(45, 8, 6), lang='ko', en='and#1', words=['또한']),
    dict(ref=(45, 8, 6), lang='ko', en='one#2', words=['한#2']),
    dict(ref=(45, 8, 6), lang='ko', en='Christ', words=['그리스도께서']),

    dict(ref=(46, 1, 1), lang='ko', en='Christ', words=['그리스도']),
    dict(ref=(46, 1, 1), lang='ko', en='by', words=['말미암아']),
    dict(ref=(46, 1, 1), lang='ko', en='is', words=['있는#1']),

    dict(ref=(48, 1, 1), lang='ko', en='Christ#1', words=['그리스도#1']),
    dict(ref=(48, 1, 1), lang='ko', en='by', words=['말미암아']),
    dict(ref=(48, 1, 1), lang='ko', en='in', words=['안에']),
    dict(ref=(48, 1, 1), lang='ko', en='Christ#2', words=['그리스도#2']),

    dict(ref=(48, 1, 5), lang='ko', en='by', words=['말미암아']),
    dict(ref=(48, 1, 5), lang='ko', en='Christ', words=['그리스도로']),

    dict(ref=(49, 1, 11), lang='ko', en='by', words=['말미암아']),
    dict(ref=(49, 1, 11), lang='ko', en='Christ', words=['그리스도로']),

    dict(ref=(49, 1, 26), lang='ko', en='in', words=['안에서']),
    dict(ref=(49, 1, 26), lang='ko', en='Christ', words=['그리스도']),

    dict(ref=(49, 3, 8), lang='ko', en='Christ#1', words=['그리스도']),
    dict(ref=(49, 3, 8), lang='ko', en='for#2', words=['위하여']),
    dict(ref=(49, 3, 8), lang='ko', en='Christ#2', words=['그리스도를']),

    dict(ref=(50, 1, 1), lang='ko', en='Christ', words=['그리스도']),
    dict(ref=(50, 1, 1), lang='ko', en='by', words=['말미암아']),

    dict(ref=(53, 1, 12), lang='ko', en='thank', words=['감사함은']),
    dict(ref=(53, 1, 12), lang='ko', en='Christ', words=['그리스도']),

    dict(ref=(53, 4, 6), lang='ko', en='Christ', words=['그리스도']),
    dict(ref=(53, 4, 6), lang='ko', en='nourished', words=['양육을', '받으리라']),
    dict(ref=(53, 4, 6), lang='ko', en='up', words=['양육을']),

    dict(ref=(55, 1, 4), lang='ko', en='Christ', words=['그리스도']),
    dict(ref=(55, 1, 4), lang='ko', en='Saviour', words=['구주로']),

    dict(ref=(59, 4, 11), lang='ko', en='through', words=['말미암아']),
    dict(ref=(59, 4, 11), lang='ko', en='Christ', words=['그리스도로']),
    dict(ref=(59, 4, 11), lang='ko', en='that', words=['함이니']),

    dict(ref=(62, 1, 3), lang='ko', en='with', words=['우리와', '함께']),
    dict(ref=(62, 1, 3), lang='ko', en='Christ', words=['그리스도께로부터']),

    # ---- 히브리서 11:2 ----
    dict(ref=(57, 11, 2), lang='ko', en='For', words=['이로써']),
    dict(ref=(57, 11, 2), lang='ko', en='by', words=['이로써']),
    dict(ref=(57, 11, 2), lang='ko', en='it', words=['이로써']),
    dict(ref=(57, 11, 2), lang='ko', en='the', words=['선진들이']),
    dict(ref=(57, 11, 2), lang='ko', en='elders', words=['선진들이']),
    dict(ref=(57, 11, 2), lang='ko', en='obtained', words=['얻었으니라']),
    dict(ref=(57, 11, 2), lang='ko', en='a', words=['증거를']),
    dict(ref=(57, 11, 2), lang='ko', en='good', words=['증거를']),
    dict(ref=(57, 11, 2), lang='ko', en='report', words=['증거를']),

    # ---- 확실한 짝이 엉뚱한 데 걸려 있던 자리 (뒤틀림 교정) ----
    # 생명 / life
    dict(ref=(0, 3, 22), lang='ko', en='lest', words=['하노라']),
    dict(ref=(0, 3, 22), lang='ko', en='take', words=['따']),
    dict(ref=(0, 3, 22), lang='ko', en='of#2', words=['실과도']),
    dict(ref=(0, 3, 22), lang='ko', en='tree', words=['생명나무']),
    dict(ref=(0, 3, 22), lang='ko', en='of#3', words=['생명나무']),
    dict(ref=(0, 3, 22), lang='ko', en='life', words=['생명나무']),
    dict(ref=(0, 3, 22), lang='ko', en='live', words=['영생할까']),
    dict(ref=(0, 3, 22), lang='ko', en='for', words=['영생할까']),
    dict(ref=(0, 3, 22), lang='ko', en='ever', words=['영생할까']),

    dict(ref=(19, 2, 19), lang='ko', en='None', words=['누구든지']),
    dict(ref=(19, 2, 19), lang='ko', en='again', words=['못하며']),
    dict(ref=(19, 2, 19), lang='ko', en='neither', words=['못하느니라']),
    dict(ref=(19, 2, 19), lang='ko', en='take', words=['얻지']),
    dict(ref=(19, 2, 19), lang='ko', en='hold', words=['얻지']),
    dict(ref=(19, 2, 19), lang='ko', en='paths', words=['생명길을']),
    dict(ref=(19, 2, 19), lang='ko', en='of#2', words=['생명길을']),
    dict(ref=(19, 2, 19), lang='ko', en='life', words=['생명길을']),

    dict(ref=(9, 19, 5), lang='ko', en='Thou', words=['왕께서']),
    dict(ref=(9, 19, 5), lang='ko', en='shamed', words=['부끄럽게', '하시니']),
    dict(ref=(9, 19, 5), lang='ko', en='life', words=['생명과#1']),
    dict(ref=(9, 19, 5), lang='ko', en='thy#3', words=['왕의#2']),
    dict(ref=(9, 19, 5), lang='ko', en='sons', words=['자녀의']),
    dict(ref=(9, 19, 5), lang='ko', en='daughters', words=['자녀의']),
    dict(ref=(9, 19, 5), lang='ko', en='lives#1', words=['생명과#2']),
    dict(ref=(9, 19, 5), lang='ko', en='lives#2', words=['생명을']),
    dict(ref=(9, 19, 5), lang='ko', en='lives#3', words=['생명을']),
    dict(ref=(9, 19, 5), lang='ko', en='wives', words=['처첩들의']),

    # 빛 / light
    dict(ref=(19, 4, 18), lang='ko', en='shining', words=['돋는', '햇볕']),
    dict(ref=(19, 4, 18), lang='ko', en='light', words=['햇볕']),
    dict(ref=(19, 4, 18), lang='ko', en='shineth', words=['빛나서']),
    dict(ref=(19, 4, 18), lang='ko', en='more#1', words=['점점']),
    dict(ref=(19, 4, 18), lang='ko', en='more#2', words=['점점']),
    dict(ref=(19, 4, 18), lang='ko', en='perfect', words=['원만한']),
    dict(ref=(19, 4, 18), lang='ko', en='day', words=['광명에']),

    # 은혜 / gracious
    dict(ref=(1, 34, 6), lang='ko', en='Lord#1', words=['여호와께서']),
    dict(ref=(1, 34, 6), lang='ko', en='Lord#2', words=['여호와로라#1']),
    dict(ref=(1, 34, 6), lang='ko', en='Lord#3', words=['여호와로라#2']),
    dict(ref=(1, 34, 6), lang='ko', en='gracious', words=['은혜롭고']),
    dict(ref=(1, 34, 6), lang='ko', en='longsuffering', words=['노하기를', '더디하고']),

    # 사랑 / love · charity · beloved
    dict(ref=(54, 3, 10), lang='ko', en='known', words=[]),
    dict(ref=(54, 3, 10), lang='ko', en='manner', words=['행실과']),
    dict(ref=(54, 3, 10), lang='ko', en='of', words=['행실과']),
    dict(ref=(54, 3, 10), lang='ko', en='life', words=['행실과']),
    dict(ref=(54, 3, 10), lang='ko', en='purpose', words=['의향과']),
    dict(ref=(54, 3, 10), lang='ko', en='charity', words=['사랑과']),
    dict(ref=(54, 3, 10), lang='ko', en='patience', words=['인내와']),

    dict(ref=(21, 2, 10), lang='ko', en='My', words=['나의#1']),
    dict(ref=(21, 2, 10), lang='ko', en='beloved', words=['사랑하는', '자가']),
    dict(ref=(21, 2, 10), lang='ko', en='my#1', words=['나의#2']),
    dict(ref=(21, 2, 10), lang='ko', en='love', words=['사랑']),
    dict(ref=(21, 2, 10), lang='ko', en='my#2', words=['나의#3']),
    dict(ref=(21, 2, 10), lang='ko', en='fair', words=['어여쁜']),
    dict(ref=(21, 2, 10), lang='ko', en='one', words=['자야']),

    dict(ref=(21, 5, 2), lang='ko', en='my#1', words=['마음은']),
    dict(ref=(21, 5, 2), lang='ko', en='my#2', words=['나의#1']),
    dict(ref=(21, 5, 2), lang='ko', en='beloved', words=['사랑하는', '자의']),
    dict(ref=(21, 5, 2), lang='ko', en='knocketh', words=['문을', '두드려']),
    dict(ref=(21, 5, 2), lang='ko', en='Open', words=['문', '열어']),
    dict(ref=(21, 5, 2), lang='ko', en='my#3', words=['나의#2']),
    dict(ref=(21, 5, 2), lang='ko', en='my#4', words=['나의#3']),
    dict(ref=(21, 5, 2), lang='ko', en='love', words=['사랑']),
    dict(ref=(21, 5, 2), lang='ko', en='my#5', words=['나의#4']),
    dict(ref=(21, 5, 2), lang='ko', en='my#6', words=['나의#5']),
    dict(ref=(21, 5, 2), lang='ko', en='undefiled', words=['완전한', '자야']),
    dict(ref=(21, 5, 2), lang='ko', en='my#7', words=['내#1']),
    dict(ref=(21, 5, 2), lang='ko', en='my#8', words=['내#2']),

    dict(ref=(61, 4, 11), lang='ko', en='Beloved', words=['사랑하는#1', '자들아']),
    dict(ref=(61, 4, 11), lang='ko', en='ought', words=['마땅하도다']),
    dict(ref=(61, 4, 11), lang='ko', en='to', words=['것이']),
    dict(ref=(61, 4, 11), lang='ko', en='love', words=['사랑하는#2']),

    dict(ref=(46, 2, 4), lang='ko', en='know', words=['알게']),
    dict(ref=(46, 2, 4), lang='ko', en='the', words=['사랑이']),
    dict(ref=(46, 2, 4), lang='ko', en='love', words=['사랑이']),

    # 제사장 / priest — '직분'은 office 쪽이다
    dict(ref=(1, 35, 19), lang='ko', en='cloths', words=['공교히', '만든', '옷']),
    dict(ref=(1, 35, 19), lang='ko', en='service#1', words=['위하여']),
    dict(ref=(1, 35, 19), lang='ko', en='service#2', words=['섬기기']),
    dict(ref=(1, 35, 19), lang='ko', en='place', words=['성소에서']),
    dict(ref=(1, 35, 19), lang='ko', en='minister', words=['행할', '입는']),
    dict(ref=(1, 35, 19), lang='ko', en='priest#2', words=['제사']),
    dict(ref=(1, 35, 19), lang='ko', en='office', words=['직분을']),
    dict(ref=(1, 35, 19), lang='ko', en='priest#1', words=['제사장']),
    dict(ref=(1, 35, 19), lang='ko', en='garments#1', words=['옷과']),

    dict(ref=(1, 39, 41), lang='ko', en='cloths', words=['정교한', '옷']),
    dict(ref=(1, 39, 41), lang='ko', en='service#1', words=['섬기기']),
    dict(ref=(1, 39, 41), lang='ko', en='service#2', words=['행할']),
    dict(ref=(1, 39, 41), lang='ko', en='priest#1', words=['제사장']),
    dict(ref=(1, 39, 41), lang='ko', en='garments#1', words=['옷과']),
    dict(ref=(1, 39, 41), lang='ko', en='garments#2', words=['옷이라']),
    dict(ref=(1, 39, 41), lang='ko', en='minister', words=['입는']),
    dict(ref=(1, 39, 41), lang='ko', en='priest#2', words=['제사']),
    dict(ref=(1, 39, 41), lang='ko', en='office', words=['직분을']),

    dict(ref=(2, 16, 32), lang='ko', en='priest#1', words=['제사장은']),
    dict(ref=(2, 16, 32), lang='ko', en='minister', words=['행하는']),
    dict(ref=(2, 16, 32), lang='ko', en='priest#2', words=['제사장의']),
    dict(ref=(2, 16, 32), lang='ko', en='office', words=['직분을']),

    dict(ref=(3, 3, 3), lang='ko', en='priests', words=['제사장들이라']),
    dict(ref=(3, 3, 3), lang='ko', en='anointed', words=['기름을', '발리우고']),
    dict(ref=(3, 3, 3), lang='ko', en='consecrated', words=['거룩히', '구별되어']),
    dict(ref=(3, 3, 3), lang='ko', en='minister', words=['위임받은']),
    dict(ref=(3, 3, 3), lang='ko', en='priest', words=['제사장']),
    dict(ref=(3, 3, 3), lang='ko', en='office', words=['직분을']),

    # ---- 뒤틀림 교정 2차: 기도·하나님·소망·진리·빛 ----
    # 기도 / prayer — '부르짖음'은 cry 쪽이다
    dict(ref=(10, 8, 28), lang='ko', en='prayer#1', words=['기도와']),
    dict(ref=(10, 8, 28), lang='ko', en='supplication', words=['간구를']),
    dict(ref=(10, 8, 28), lang='ko', en='cry', words=['부르짖음과']),
    dict(ref=(10, 8, 28), lang='ko', en='prayer#2', words=['기도를']),

    dict(ref=(13, 6, 19), lang='ko', en='prayer#1', words=['기도와']),
    dict(ref=(13, 6, 19), lang='ko', en='supplication', words=['간구를']),
    dict(ref=(13, 6, 19), lang='ko', en='cry', words=['부르짖음과']),
    dict(ref=(13, 6, 19), lang='ko', en='prayer#2', words=['기도를']),

    dict(ref=(18, 17, 1), lang='ko', en='Prayer', words=['기도']),
    dict(ref=(18, 17, 1), lang='ko', en='cry', words=['부르짖음에']),
    dict(ref=(18, 17, 1), lang='ko', en='prayer', words=['기도에']),

    dict(ref=(18, 102, 1), lang='ko', en='Prayer', words=['기도']),
    dict(ref=(18, 102, 1), lang='ko', en='prayer', words=['기도를']),

    dict(ref=(13, 30, 27), lang='ko', en='prayer', words=['기도가']),
    dict(ref=(13, 30, 27), lang='ko', en='came', words=['상달하였더라']),
    dict(ref=(13, 30, 27), lang='ko', en='up', words=['상달하였더라']),

    dict(ref=(23, 7, 16), lang='ko', en='pray', words=['기도하지']),
    dict(ref=(23, 7, 16), lang='ko', en='cry', words=['부르짖어']),
    dict(ref=(23, 7, 16), lang='ko', en='prayer', words=['구하지']),

    # 하나님 / God
    dict(ref=(9, 7, 28), lang='ko', en='Lord', words=['주']),
    dict(ref=(9, 7, 28), lang='ko', en='God#1', words=['여호와여']),
    dict(ref=(9, 7, 28), lang='ko', en='thou#1', words=['주는']),
    dict(ref=(9, 7, 28), lang='ko', en='that#1', words=['오직']),
    dict(ref=(9, 7, 28), lang='ko', en='God#2', words=['하나님이시며']),

    dict(ref=(25, 14, 11), lang='ko', en='be#3', words=['되려']),
    dict(ref=(25, 14, 11), lang='ko', en='God#1', words=['하나님이']),
    dict(ref=(25, 14, 11), lang='ko', en='Lord', words=['여호와의']),
    dict(ref=(25, 14, 11), lang='ko', en='God#2', words=['여호와의']),

    dict(ref=(29, 6, 8), lang='ko', en='Lord#1', words=['주']),
    dict(ref=(29, 6, 8), lang='ko', en='God#1', words=['여호와가']),
    dict(ref=(29, 6, 8), lang='ko', en='saith', words=['가라사대']),
    dict(ref=(29, 6, 8), lang='ko', en='Lord#2', words=['여호와께서']),
    dict(ref=(29, 6, 8), lang='ko', en='God#2', words=['하나님']),
    dict(ref=(29, 6, 8), lang='ko', en='hosts', words=['만군의']),

    dict(ref=(34, 1, 12), lang='ko', en='Lord#1', words=['여호와']),
    dict(ref=(34, 1, 12), lang='ko', en='my', words=['나의#1']),
    dict(ref=(34, 1, 12), lang='ko', en='God#1', words=['하나님']),
    dict(ref=(34, 1, 12), lang='ko', en='mine', words=['나의#2']),
    dict(ref=(34, 1, 12), lang='ko', en='Holy', words=['거룩한']),
    dict(ref=(34, 1, 12), lang='ko', en='One', words=['자시여']),
    dict(ref=(34, 1, 12), lang='ko', en='mighty', words=['반석이시여']),
    dict(ref=(34, 1, 12), lang='ko', en='God#2', words=['반석이시여']),

    # 사랑 / love
    dict(ref=(20, 9, 1), lang='ko', en='man', words=['사람이']),
    dict(ref=(20, 9, 1), lang='ko', en='knoweth', words=['알지']),
    dict(ref=(20, 9, 1), lang='ko', en='love', words=['사랑을']),
    dict(ref=(20, 9, 1), lang='ko', en='hatred', words=['미움을']),

    # 소망 / hope
    dict(ref=(43, 26, 7), lang='ko', en='hope#1', words=['바라는']),
    dict(ref=(43, 26, 7), lang='ko', en='come', words=['얻기를']),
    dict(ref=(43, 26, 7), lang='ko', en='hope#2', words=['소망을']),

    dict(ref=(44, 8, 24), lang='ko', en='hope#1', words=['소망으로']),
    dict(ref=(44, 8, 24), lang='ko', en='hope#2', words=['소망이#1']),
    dict(ref=(44, 8, 24), lang='ko', en='hope#3', words=['소망이#2']),
    dict(ref=(44, 8, 24), lang='ko', en='hope#4', words=['바라리요']),

    # 진리 / truth
    dict(ref=(19, 22, 21), lang='ko', en='certainty', words=['확실한']),
    dict(ref=(19, 22, 21), lang='ko', en='truth#1', words=['진리의#1']),
    dict(ref=(19, 22, 21), lang='ko', en='truth#2', words=['진리의#2']),

    # 빛 / light
    dict(ref=(22, 60, 19), lang='ko', en='light#1', words=['빛이#1']),
    dict(ref=(22, 60, 19), lang='ko', en='give', words=['비취지']),
    dict(ref=(22, 60, 19), lang='ko', en='light#2', words=['빛을']),
    dict(ref=(22, 60, 19), lang='ko', en='everlasting', words=['영영한']),
    dict(ref=(22, 60, 19), lang='ko', en='light#3', words=['빛이#2']),
    dict(ref=(22, 60, 19), lang='ko', en='God', words=['하나님이']),
    dict(ref=(22, 60, 19), lang='ko', en='glory', words=['영광이']),

    dict(ref=(37, 14, 6), lang='ko', en='light', words=['빛이']),
    dict(ref=(37, 14, 6), lang='ko', en='not', words=['없겠고']),
    dict(ref=(37, 14, 6), lang='ko', en='clear', words=['광명한']),

    # ---- 히브리서 11:3-4 ----
    dict(ref=(57, 11, 3), lang='ko', en='Through', words=['믿음으로']),
    dict(ref=(57, 11, 3), lang='ko', en='faith', words=['믿음으로']),
    dict(ref=(57, 11, 3), lang='ko', en='we', words=['우리가']),
    dict(ref=(57, 11, 3), lang='ko', en='understand', words=['아나니']),
    dict(ref=(57, 11, 3), lang='ko', en='that#1', words=['줄을']),
    dict(ref=(57, 11, 3), lang='ko', en='the#1', words=['모든', '세계가']),
    dict(ref=(57, 11, 3), lang='ko', en='worlds', words=['모든', '세계가']),
    dict(ref=(57, 11, 3), lang='ko', en='were#1', words=['지어진']),
    dict(ref=(57, 11, 3), lang='ko', en='framed', words=['지어진']),
    dict(ref=(57, 11, 3), lang='ko', en='by', words=['말씀으로']),
    dict(ref=(57, 11, 3), lang='ko', en='the#2', words=['말씀으로']),
    dict(ref=(57, 11, 3), lang='ko', en='word', words=['말씀으로']),
    dict(ref=(57, 11, 3), lang='ko', en='of#1', words=['하나님의']),
    dict(ref=(57, 11, 3), lang='ko', en='God', words=['하나님의']),
    dict(ref=(57, 11, 3), lang='ko', en='things#1', words=['것은']),
    dict(ref=(57, 11, 3), lang='ko', en='which#1', words=['것은']),
    dict(ref=(57, 11, 3), lang='ko', en='are', words=['보이는']),
    dict(ref=(57, 11, 3), lang='ko', en='seen', words=['보이는']),
    dict(ref=(57, 11, 3), lang='ko', en='were#2', words=['아니니라']),
    dict(ref=(57, 11, 3), lang='ko', en='not', words=['아니니라']),
    dict(ref=(57, 11, 3), lang='ko', en='made', words=['말미암아', '된', '것이']),
    dict(ref=(57, 11, 3), lang='ko', en='of#2', words=['것으로']),
    dict(ref=(57, 11, 3), lang='ko', en='things#2', words=['것으로']),
    dict(ref=(57, 11, 3), lang='ko', en='which#2', words=['것으로']),
    dict(ref=(57, 11, 3), lang='ko', en='do', words=['나타난']),
    dict(ref=(57, 11, 3), lang='ko', en='appear', words=['나타난']),

    dict(ref=(57, 11, 4), lang='ko', en='By', words=['믿음으로']),
    dict(ref=(57, 11, 4), lang='ko', en='faith', words=['믿음으로']),
    dict(ref=(57, 11, 4), lang='ko', en='Abel', words=['아벨은']),
    dict(ref=(57, 11, 4), lang='ko', en='offered', words=['드림으로']),
    dict(ref=(57, 11, 4), lang='ko', en='unto', words=['하나님께']),
    dict(ref=(57, 11, 4), lang='ko', en='God#1', words=['하나님께']),
    dict(ref=(57, 11, 4), lang='ko', en='more', words=['더']),
    dict(ref=(57, 11, 4), lang='ko', en='excellent', words=['나은']),
    dict(ref=(57, 11, 4), lang='ko', en='sacrifice', words=['제사를']),
    dict(ref=(57, 11, 4), lang='ko', en='than', words=['가인보다']),
    dict(ref=(57, 11, 4), lang='ko', en='Cain', words=['가인보다']),
    dict(ref=(57, 11, 4), lang='ko', en='by#1', words=['얻었으니']),
    dict(ref=(57, 11, 4), lang='ko', en='which', words=['증거를']),
    dict(ref=(57, 11, 4), lang='ko', en='he#1', words=['얻었으니']),
    dict(ref=(57, 11, 4), lang='ko', en='obtained', words=['얻었으니']),
    dict(ref=(57, 11, 4), lang='ko', en='witness', words=['증거를']),
    dict(ref=(57, 11, 4), lang='ko', en='that', words=['자라']),
    dict(ref=(57, 11, 4), lang='ko', en='he#2', words=['자라']),
    dict(ref=(57, 11, 4), lang='ko', en='was', words=['하시는']),
    dict(ref=(57, 11, 4), lang='ko', en='righteous', words=['의로운']),
    dict(ref=(57, 11, 4), lang='ko', en='God#2', words=['하나님이']),
    dict(ref=(57, 11, 4), lang='ko', en='testifying', words=['증거하심이라']),
    dict(ref=(57, 11, 4), lang='ko', en='of', words=['대하여']),
    dict(ref=(57, 11, 4), lang='ko', en='his', words=['그#1']),
    dict(ref=(57, 11, 4), lang='ko', en='gifts', words=['예물에']),
    dict(ref=(57, 11, 4), lang='ko', en='by#2', words=['그#2', '믿음으로써']),
    dict(ref=(57, 11, 4), lang='ko', en='it', words=['그#2', '믿음으로써']),
    dict(ref=(57, 11, 4), lang='ko', en='he#3', words=['저가']),
    dict(ref=(57, 11, 4), lang='ko', en='dead', words=['죽었으나']),
    dict(ref=(57, 11, 4), lang='ko', en='yet', words=['오히려']),
    dict(ref=(57, 11, 4), lang='ko', en='speaketh', words=['말하느니라']),

    # ---- 믿음으로 / by·through·of faith — 앞의 전치사까지 한 낱말에 묶음 ----
    # 전치사가 이미 걸고 있던 말미암아·인하여 는 그대로 두고 믿음으로를 더한다.
    dict(ref=(43, 15, 9), lang='ko', en='by', words=['믿음으로']),   # 사도행전 15:9
    dict(ref=(44, 1, 17), lang='ko', en='from', words=['믿음으로#1']),   # 로마서 1:17
    dict(ref=(44, 3, 22), lang='ko', en='by', words=['말미암아', '믿음으로']),   # 로마서 3:22
    dict(ref=(44, 3, 25), lang='ko', en='through#1', words=['인하여', '말미암는', '믿음으로']),   # 로마서 3:25
    dict(ref=(44, 3, 28), lang='ko', en='by', words=['믿음으로']),   # 로마서 3:28
    dict(ref=(44, 3, 30), lang='ko', en='by', words=['말미암아#1', '믿음으로#1']),   # 로마서 3:30
    dict(ref=(44, 3, 30), lang='ko', en='through', words=['말미암아#1', '믿음으로#2']),   # 로마서 3:30
    dict(ref=(44, 3, 31), lang='ko', en='through', words=['말미암아', '믿음으로']),   # 로마서 3:31
    dict(ref=(44, 4, 16), lang='ko', en='of#1', words=['사람의', '믿음으로']),   # 로마서 4:16
    dict(ref=(44, 5, 1), lang='ko', en='by', words=['믿음으로']),   # 로마서 5:1
    dict(ref=(44, 5, 2), lang='ko', en='by', words=['믿음으로']),   # 로마서 5:2
    dict(ref=(44, 10, 6), lang='ko', en='of', words=['믿음으로']),   # 로마서 10:6
    dict(ref=(44, 14, 23), lang='ko', en='of#1', words=['믿음으로#1']),   # 로마서 14:23
    dict(ref=(44, 14, 23), lang='ko', en='of#2', words=['믿음으로#2']),   # 로마서 14:23
    dict(ref=(46, 5, 7), lang='ko', en='by#1', words=['믿음으로']),   # 고린도후서 5:7
    dict(ref=(47, 3, 7), lang='ko', en='of#1', words=['믿음으로']),   # 갈라디아서 3:7
    dict(ref=(47, 3, 8), lang='ko', en='through', words=['말미암아', '믿음으로']),   # 갈라디아서 3:8
    dict(ref=(47, 3, 9), lang='ko', en='of', words=['믿음으로']),   # 갈라디아서 3:9
    dict(ref=(47, 3, 11), lang='ko', en='by#2', words=['믿음으로']),   # 갈라디아서 3:11
    dict(ref=(47, 3, 14), lang='ko', en='through#2', words=['말미암아', '믿음으로']),   # 갈라디아서 3:14
    dict(ref=(47, 3, 22), lang='ko', en='by', words=['말미암은', '믿음으로']),   # 갈라디아서 3:22
    dict(ref=(47, 3, 24), lang='ko', en='by', words=['말미암아', '믿음으로']),   # 갈라디아서 3:24
    dict(ref=(47, 3, 26), lang='ko', en='by', words=['말미암아', '믿음으로']),   # 갈라디아서 3:26
    dict(ref=(48, 2, 8), lang='ko', en='through', words=['인하여', '말미암아', '믿음으로']),   # 에베소서 2:8
    dict(ref=(48, 3, 17), lang='ko', en='by', words=['말미암아', '믿음으로']),   # 에베소서 3:17
    dict(ref=(49, 3, 9), lang='ko', en='by', words=['믿음으로#2']),   # 빌립보서 3:9
    dict(ref=(53, 1, 5), lang='ko', en='of#4', words=['믿음으로']),   # 디모데전서 1:5
    dict(ref=(54, 3, 15), lang='ko', en='through', words=['말미암아', '믿음으로']),   # 디모데후서 3:15
    dict(ref=(57, 10, 22), lang='ko', en='of', words=['믿음으로']),   # 히브리서 10:22
    dict(ref=(57, 10, 38), lang='ko', en='by', words=['말미암아', '믿음으로']),   # 히브리서 10:38
    dict(ref=(57, 11, 5), lang='ko', en='By', words=['믿음으로']),   # 히브리서 11:5
    dict(ref=(57, 11, 7), lang='ko', en='By', words=['말미암아', '믿음으로']),   # 히브리서 11:7
    dict(ref=(57, 11, 8), lang='ko', en='By', words=['믿음으로']),   # 히브리서 11:8
    dict(ref=(57, 11, 9), lang='ko', en='By', words=['믿음으로']),   # 히브리서 11:9
    dict(ref=(57, 11, 11), lang='ko', en='Through', words=['믿음으로']),   # 히브리서 11:11
    dict(ref=(57, 11, 17), lang='ko', en='By', words=['믿음으로']),   # 히브리서 11:17
    dict(ref=(57, 11, 20), lang='ko', en='By', words=['믿음으로']),   # 히브리서 11:20
    dict(ref=(57, 11, 21), lang='ko', en='By', words=['믿음으로']),   # 히브리서 11:21
    dict(ref=(57, 11, 22), lang='ko', en='By', words=['믿음으로']),   # 히브리서 11:22
    dict(ref=(57, 11, 23), lang='ko', en='By', words=['믿음으로']),   # 히브리서 11:23
    dict(ref=(57, 11, 24), lang='ko', en='By', words=['믿음으로']),   # 히브리서 11:24
    dict(ref=(57, 11, 27), lang='ko', en='By', words=['믿음으로']),   # 히브리서 11:27
    dict(ref=(57, 11, 28), lang='ko', en='Through', words=['믿음으로']),   # 히브리서 11:28
    dict(ref=(57, 11, 29), lang='ko', en='By', words=['믿음으로']),   # 히브리서 11:29
    dict(ref=(57, 11, 30), lang='ko', en='By', words=['믿음으로']),   # 히브리서 11:30
    dict(ref=(57, 11, 31), lang='ko', en='By', words=['믿음으로']),   # 히브리서 11:31
    dict(ref=(57, 11, 39), lang='ko', en='through', words=['말미암아', '믿음으로']),   # 히브리서 11:39
    dict(ref=(59, 1, 5), lang='ko', en='through', words=['말미암아', '믿음으로']),   # 베드로전서 1:5

    # 믿음으로가 두 번 나오거나 faith 가 안 걸려 있던 자리 — 손으로
    dict(ref=(44, 1, 17), lang='ko', en='from', words=['믿음으로#1']),
    dict(ref=(44, 1, 17), lang='ko', en='faith#1', words=['믿음으로#1']),
    dict(ref=(44, 1, 17), lang='ko', en='to', words=['이르게', '함과']),
    dict(ref=(44, 1, 17), lang='ko', en='faith#2', words=['믿음에']),
    dict(ref=(44, 1, 17), lang='ko', en='by', words=['믿음으로#2', '말미암아']),
    dict(ref=(44, 1, 17), lang='ko', en='faith#3', words=['믿음으로#2']),

    dict(ref=(52, 2, 13), lang='ko', en='bound', words=['마땅히']),
    dict(ref=(52, 2, 13), lang='ko', en='through', words=['거룩하게', '하심과']),
    dict(ref=(52, 2, 13), lang='ko', en='sanctification', words=['거룩하게', '하심과']),
    dict(ref=(52, 2, 13), lang='ko', en='of#2', words=['성령의']),
    dict(ref=(52, 2, 13), lang='ko', en='Spirit', words=['성령의']),
    dict(ref=(52, 2, 13), lang='ko', en='and', words=['믿음으로']),
    dict(ref=(52, 2, 13), lang='ko', en='belief', words=['믿음으로']),
    dict(ref=(52, 2, 13), lang='ko', en='of#3', words=['진리를']),
    dict(ref=(52, 2, 13), lang='ko', en='you#2', words=['너희를#2']),
    dict(ref=(52, 2, 13), lang='ko', en='to#3', words=['얻게', '하심이니']),

    # 엡 2:8 — 'by grace' 의 by 가 인하여를 되찾는다
    dict(ref=(48, 2, 8), lang='ko', en='by', words=['인하여']),
    dict(ref=(48, 2, 8), lang='ko', en='through', words=['믿음으로', '말미암아']),

    # 전치사와 faith 사이에 the·his·your 가 끼어 있던 자리
    dict(ref=(34, 2, 4), lang='ko', en='by', words=['말미암아']),
    dict(ref=(34, 2, 4), lang='ko', en='his#2', words=['믿음으로']),

    dict(ref=(44, 4, 11), lang='ko', en='of#3', words=['믿음으로']),
    dict(ref=(44, 4, 11), lang='ko', en='the#3', words=['믿음으로']),

    dict(ref=(47, 2, 16), lang='ko', en='by#2', words=['믿음으로', '말미암는']),
    dict(ref=(47, 2, 16), lang='ko', en='the#3', words=['믿음으로']),

    dict(ref=(48, 3, 12), lang='ko', en='by', words=['믿음으로', '말미암아']),
    dict(ref=(48, 3, 12), lang='ko', en='the', words=['믿음으로']),

    dict(ref=(49, 3, 9), lang='ko', en='through', words=['믿음으로#1', '말미암은']),
    dict(ref=(49, 3, 9), lang='ko', en='the#2', words=['믿음으로#1']),
    dict(ref=(49, 3, 9), lang='ko', en='faith#1', words=['믿음으로#1']),
    dict(ref=(49, 3, 9), lang='ko', en='by', words=['믿음으로#2']),
    dict(ref=(49, 3, 9), lang='ko', en='faith#2', words=['믿음으로#2']),

    dict(ref=(50, 2, 12), lang='ko', en='through', words=['믿음으로', '말미암아']),
    dict(ref=(50, 2, 12), lang='ko', en='the#1', words=['믿음으로']),

    dict(ref=(51, 3, 7), lang='ko', en='by', words=['믿음으로', '말미암아']),
    dict(ref=(51, 3, 7), lang='ko', en='your', words=['너희']),
    dict(ref=(51, 3, 7), lang='ko', en='over', words=['너희에게']),

    dict(ref=(58, 1, 6), lang='ko', en='in#1', words=['믿음으로']),

    # ---- 히브리서 11:5-13 (편집기에서 올라온 교정) ----
    # ---- 히브리서 11:5 ----
    dict(ref=(57, 11, 5), lang='ko', en='was#1', words=[]),
    dict(ref=(57, 11, 5), lang='ko', en='he#1', words=['저를']),
    dict(ref=(57, 11, 5), lang='ko', en='translated#2', words=['옮기심으로']),
    dict(ref=(57, 11, 5), lang='ko', en='his', words=['저는']),
    dict(ref=(57, 11, 5), lang='ko', en='translation', words=['옮기우기']),
    dict(ref=(57, 11, 5), lang='ko', en='had#2', words=['받았느니라']),
    dict(ref=(57, 11, 5), lang='ko', en='that#2', words=['하는#2']),
    dict(ref=(57, 11, 5), lang='ko', en='he#3', words=['자라']),
    dict(ref=(57, 11, 5), lang='ko', en='God#2', words=['하나님을']),

    # ---- 히브리서 11:6 ----
    dict(ref=(57, 11, 6), lang='ko', en='But', words=[]),
    dict(ref=(57, 11, 6), lang='ko', en='impossible', words=['못하나니']),
    dict(ref=(57, 11, 6), lang='ko', en='he#1', words=[]),
    dict(ref=(57, 11, 6), lang='ko', en='cometh', words=['나아가는']),
    dict(ref=(57, 11, 6), lang='ko', en='he#2', words=['그가#1']),
    dict(ref=(57, 11, 6), lang='ko', en='is#2', words=['계신']),
    dict(ref=(57, 11, 6), lang='ko', en='and', words=['것과']),
    dict(ref=(57, 11, 6), lang='ko', en='he#3', words=['그가#2']),
    dict(ref=(57, 11, 6), lang='ko', en='is#3', words=['이심을']),

    # ---- 히브리서 11:7 ----
    dict(ref=(57, 11, 7), lang='ko', en='By', words=['믿음으로']),
    dict(ref=(57, 11, 7), lang='ko', en='God', words=[]),
    dict(ref=(57, 11, 7), lang='ko', en='things', words=['일에']),
    dict(ref=(57, 11, 7), lang='ko', en='fear', words=['경외함으로']),
    dict(ref=(57, 11, 7), lang='ko', en='saving', words=['구원하였으니']),
    dict(ref=(57, 11, 7), lang='ko', en='by#1', words=['말미암아']),
    dict(ref=(57, 11, 7), lang='ko', en='which#1', words=['이로']),
    dict(ref=(57, 11, 7), lang='ko', en='of#4', words=['의의']),
    dict(ref=(57, 11, 7), lang='ko', en='the#4', words=['의의']),
    dict(ref=(57, 11, 7), lang='ko', en='righteousness', words=['의의']),
    dict(ref=(57, 11, 7), lang='ko', en='is', words=[]),
    dict(ref=(57, 11, 7), lang='ko', en='by#2', words=['좇는']),
    dict(ref=(57, 11, 7), lang='ko', en='faith#2', words=['믿음을']),

    # ---- 히브리서 11:8 ----
    dict(ref=(57, 11, 8), lang='ko', en='was', words=['받았을']),
    dict(ref=(57, 11, 8), lang='ko', en='called', words=['부르심을', '받았을']),
    dict(ref=(57, 11, 8), lang='ko', en='receive', words=['받을']),
    dict(ref=(57, 11, 8), lang='ko', en='went#1', words=['나갔으며']),
    dict(ref=(57, 11, 8), lang='ko', en='out#2', words=['나갔으며']),
    dict(ref=(57, 11, 8), lang='ko', en='whither', words=['바를']),

    # ---- 히브리서 11:9 ----
    dict(ref=(57, 11, 9), lang='ko', en='he', words=['저가']),
    dict(ref=(57, 11, 9), lang='ko', en='the#1', words=['땅에']),
    dict(ref=(57, 11, 9), lang='ko', en='in#2', words=['있는', '것']),
    dict(ref=(57, 11, 9), lang='ko', en='strange', words=['외방에']),
    dict(ref=(57, 11, 9), lang='ko', en='country', words=['외방에']),
    dict(ref=(57, 11, 9), lang='ko', en='dwelling', words=['거하였으니']),
    dict(ref=(57, 11, 9), lang='ko', en='in#3', words=['장막에']),
    dict(ref=(57, 11, 9), lang='ko', en='same', words=['동일한']),
    dict(ref=(57, 11, 9), lang='ko', en='promise#2', words=['약속을']),

    # ---- 히브리서 11:10 ----
    # 지으실·바랐음이니라는 일부러 비워 둔다. 개역한글이 'he looked for a city
    # which hath foundations, whose builder and maker is God' 를 '하나님의 경영하시고
    # 지으실 터가 있는 성을 바랐음이니라' 로 크게 풀어 옮겨서, 낱말끼리 바로
    # 맞댈 수 없다. 빈 자리를 메우는 일괄 작업은 여기를 건드리지 말아야 한다.
    dict(ref=(57, 11, 10), lang='ko', en='he', words=['하나님의']),
    dict(ref=(57, 11, 10), lang='ko', en='looked', words=[]),
    dict(ref=(57, 11, 10), lang='ko', en='maker', words=[]),

    # ---- 히브리서 11:11 ----
    dict(ref=(57, 11, 11), lang='ko', en='herself', words=['자신도']),
    dict(ref=(57, 11, 11), lang='ko', en='to', words=[]),
    dict(ref=(57, 11, 11), lang='ko', en='conceive', words=['잉태하는']),
    dict(ref=(57, 11, 11), lang='ko', en='seed', words=['잉태하는']),
    # 단산하였으나는 일부러 비워 둔다 — 뜻이 반대다.
    # KJV 'was delivered of a child'(아이를 낳았다) ↔ 개역한글 '단산하였으나'
    # (아이를 못 낳게 되었으나). 붙이면 틀린 연결이 된다.
    dict(ref=(57, 11, 11), lang='ko', en='was#1', words=[]),
    dict(ref=(57, 11, 11), lang='ko', en='child', words=[]),
    dict(ref=(57, 11, 11), lang='ko', en='was#2', words=['늙어']),
    dict(ref=(57, 11, 11), lang='ko', en='past', words=['늙어']),
    dict(ref=(57, 11, 11), lang='ko', en='age', words=['나이', '늙어']),
    dict(ref=(57, 11, 11), lang='ko', en='judged', words=['앎이라']),
    dict(ref=(57, 11, 11), lang='ko', en='him', words=['이를']),
    dict(ref=(57, 11, 11), lang='ko', en='who', words=['이를']),

    # ---- 히브리서 11:13 ----
    dict(ref=(57, 11, 13), lang='ko', en='These', words=['이', '사람들은']),
    dict(ref=(57, 11, 13), lang='ko', en='not', words=['못하였으되']),
    dict(ref=(57, 11, 13), lang='ko', en='having#1', words=['받지']),
    dict(ref=(57, 11, 13), lang='ko', en='were#1', words=[]),
    dict(ref=(57, 11, 13), lang='ko', en='embraced', words=['환영하며']),
    dict(ref=(57, 11, 13), lang='ko', en='them#3', words=['그것들을']),
    dict(ref=(57, 11, 13), lang='ko', en='confessed', words=['증거하였으니']),

    # ---- 히브리서 11:14 ----
    # '자들은'은 일부러 비워 둔다. For·they·that·say 에 바로 맞댈 자리가 아니다.
    # 빈 자리를 메우는 일괄 작업은 여기를 건드리지 말아야 한다.
    dict(ref=(57, 11, 14), lang='ko', en='For', words=[]),
    dict(ref=(57, 11, 14), lang='ko', en='they#1', words=[]),
    dict(ref=(57, 11, 14), lang='ko', en='that#1', words=[]),
    dict(ref=(57, 11, 14), lang='ko', en='say', words=[]),
    dict(ref=(57, 11, 14), lang='ko', en='such', words=['이같이']),
    dict(ref=(57, 11, 14), lang='ko', en='things', words=['이같이']),
    dict(ref=(57, 11, 14), lang='ko', en='declare', words=['말하는']),
    dict(ref=(57, 11, 14), lang='ko', en='a', words=['본향']),
    dict(ref=(57, 11, 14), lang='ko', en='country', words=['본향']),

    # ---- 히브리서 11:15 ----
    dict(ref=(57, 11, 15), lang='ko', en='mindful', words=['생각하였더면']),
    dict(ref=(57, 11, 15), lang='ko', en='that', words=['바']),
    dict(ref=(57, 11, 15), lang='ko', en='country', words=['본향을']),
    dict(ref=(57, 11, 15), lang='ko', en='came', words=['나온']),
    dict(ref=(57, 11, 15), lang='ko', en='out', words=['나온']),
    dict(ref=(57, 11, 15), lang='ko', en='to', words=[]),
    dict(ref=(57, 11, 15), lang='ko', en='have#2', words=[]),
    dict(ref=(57, 11, 15), lang='ko', en='returned', words=['돌아갈']),

    # ---- 히브리서 11:16 ----
    dict(ref=(57, 11, 16), lang='ko', en='they', words=['저희가']),
    dict(ref=(57, 11, 16), lang='ko', en='country', words=['본향을']),
    dict(ref=(57, 11, 16), lang='ko', en='is#1', words=['곧']),
    dict(ref=(57, 11, 16), lang='ko', en='be', words=['받으심을']),
    dict(ref=(57, 11, 16), lang='ko', en='called', words=['일컬음', '받으심을']),
    dict(ref=(57, 11, 16), lang='ko', en='their', words=['저희']),
    dict(ref=(57, 11, 16), lang='ko', en='God#2', words=['하나님이라']),
    dict(ref=(57, 11, 16), lang='ko', en='for#2', words=['위하여']),
    dict(ref=(57, 11, 16), lang='ko', en='them', words=['저희를']),
    dict(ref=(57, 11, 16), lang='ko', en='a#2', words=['한']),

    # ---- 히브리서 11:17 ----
    dict(ref=(57, 11, 17), lang='ko', en='he#2', words=['자로되']),
    dict(ref=(57, 11, 17), lang='ko', en='had', words=['받은']),
    dict(ref=(57, 11, 17), lang='ko', en='received', words=['받은']),
    dict(ref=(57, 11, 17), lang='ko', en='offered#2', words=['드렸느니라']),
    dict(ref=(57, 11, 17), lang='ko', en='up#2', words=['드렸느니라']),

    # ---- 히브리서 11:19 ----
    dict(ref=(57, 11, 19), lang='ko', en='was', words=['능히']),
    dict(ref=(57, 11, 19), lang='ko', en='raise', words=['살리실']),
    dict(ref=(57, 11, 19), lang='ko', en='him#1', words=['죽은#1', '자#1']),
    dict(ref=(57, 11, 19), lang='ko', en='up', words=['살리실']),
    dict(ref=(57, 11, 19), lang='ko', en='the', words=['자#1']),
    dict(ref=(57, 11, 19), lang='ko', en='dead', words=['죽은#1', '자#1']),

    # ---- 히브리서 11:20 ----
    dict(ref=(57, 11, 20), lang='ko', en='things', words=['일에']),
    dict(ref=(57, 11, 20), lang='ko', en='to', words=[]),

    # ---- 히브리서 11:21 ----
    dict(ref=(57, 11, 21), lang='ko', en='when', words=['때에']),
    dict(ref=(57, 11, 21), lang='ko', en='both', words=['각']),
    dict(ref=(57, 11, 21), lang='ko', en='the#1', words=['각']),
    dict(ref=(57, 11, 21), lang='ko', en='leaning', words=['의지하여']),
    dict(ref=(57, 11, 21), lang='ko', en='upon', words=[]),
    dict(ref=(57, 11, 21), lang='ko', en='his', words=[]),

    # ---- 히브리서 11:22 ----
    dict(ref=(57, 11, 22), lang='ko', en='when', words=['임종시에']),
    dict(ref=(57, 11, 22), lang='ko', en='he', words=['임종시에']),
    dict(ref=(57, 11, 22), lang='ko', en='died', words=['임종시에']),
    dict(ref=(57, 11, 22), lang='ko', en='made', words=['말하고']),
    dict(ref=(57, 11, 22), lang='ko', en='mention', words=['말하고']),
    dict(ref=(57, 11, 22), lang='ko', en='the#1', words=['것을']),
    dict(ref=(57, 11, 22), lang='ko', en='departing', words=['떠날', '것을']),
    dict(ref=(57, 11, 22), lang='ko', en='concerning', words=['위하여']),

    # ---- 히브리서 11:23 ----
    dict(ref=(57, 11, 23), lang='ko', en='three', words=['석']),
    dict(ref=(57, 11, 23), lang='ko', en='months', words=['달']),
    dict(ref=(57, 11, 23), lang='ko', en='a', words=['아름다운']),
    dict(ref=(57, 11, 23), lang='ko', en='proper', words=['아름다운']),
    dict(ref=(57, 11, 23), lang='ko', en='child', words=['아이임을']),
    dict(ref=(57, 11, 23), lang='ko', en='the', words=['임금의']),
    dict(ref=(57, 11, 23), lang='ko', en='s', words=['임금의']),

    # ---- 히브리서 11:24 ----
    dict(ref=(57, 11, 24), lang='ko', en='come', words=['장성하여']),
    dict(ref=(57, 11, 24), lang='ko', en='to#1', words=['장성하여']),
    dict(ref=(57, 11, 24), lang='ko', en='daughter', words=['공주의']),

    # ---- 히브리서 11:25 ----
    dict(ref=(57, 11, 25), lang='ko', en='Choosing', words=['좋아하고']),
    dict(ref=(57, 11, 25), lang='ko', en='to#1', words=['고난', '받기를']),
    dict(ref=(57, 11, 25), lang='ko', en='suffer', words=['고난', '받기를']),
    dict(ref=(57, 11, 25), lang='ko', en='affliction', words=['낙을']),
    dict(ref=(57, 11, 25), lang='ko', en='pleasures', words=['낙을']),
    dict(ref=(57, 11, 25), lang='ko', en='for', words=['잠시']),
    dict(ref=(57, 11, 25), lang='ko', en='a', words=['잠시']),
    dict(ref=(57, 11, 25), lang='ko', en='season', words=['잠시']),

    # ---- 히브리서 11:26 ----
    dict(ref=(57, 11, 26), lang='ko', en='of#1', words=['위하여']),
    dict(ref=(57, 11, 26), lang='ko', en='greater', words=['더', '큰']),
    dict(ref=(57, 11, 26), lang='ko', en='than', words=['모든']),
    dict(ref=(57, 11, 26), lang='ko', en='in', words=['애굽의']),
    dict(ref=(57, 11, 26), lang='ko', en='for', words=[]),
    dict(ref=(57, 11, 26), lang='ko', en='had', words=[]),

    # ---- 히브리서 11:27 ----
    dict(ref=(57, 11, 27), lang='ko', en='forsook', words=['떠나']),
    dict(ref=(57, 11, 27), lang='ko', en='of', words=[]),
    dict(ref=(57, 11, 27), lang='ko', en='for', words=[]),
    dict(ref=(57, 11, 27), lang='ko', en='seeing', words=['보는', '것']),
    dict(ref=(57, 11, 27), lang='ko', en='invisible', words=['보이지', '아니하는']),

    # ---- 히브리서 11:28 ----
    dict(ref=(57, 11, 28), lang='ko', en='the#2', words=['예를']),
    dict(ref=(57, 11, 28), lang='ko', en='sprinkling', words=['뿌리는', '예를']),
    dict(ref=(57, 11, 28), lang='ko', en='blood', words=['피']),
    dict(ref=(57, 11, 28), lang='ko', en='lest', words=['않게']),
    dict(ref=(57, 11, 28), lang='ko', en='he#2', words=['자로']),
    dict(ref=(57, 11, 28), lang='ko', en='touch', words=['건드리지']),

    # ---- 히브리서 11:29 ----
    dict(ref=(57, 11, 29), lang='ko', en='the#1', words=['홍해를']),
    dict(ref=(57, 11, 29), lang='ko', en='Red', words=['홍해를']),
    dict(ref=(57, 11, 29), lang='ko', en='sea', words=[]),
    dict(ref=(57, 11, 29), lang='ko', en='as', words=['같이']),
    dict(ref=(57, 11, 29), lang='ko', en='by', words=['같이']),
    dict(ref=(57, 11, 29), lang='ko', en='dry', words=['육지']),
    dict(ref=(57, 11, 29), lang='ko', en='land', words=['육지']),
    dict(ref=(57, 11, 29), lang='ko', en='which', words=[]),
    dict(ref=(57, 11, 29), lang='ko', en='assaying', words=['시험하다가']),
    dict(ref=(57, 11, 29), lang='ko', en='drowned', words=['빠져', '죽었으며']),

    # ---- 히브리서 11:30 ----
    dict(ref=(57, 11, 30), lang='ko', en='were', words=[]),
    dict(ref=(57, 11, 30), lang='ko', en='compassed', words=['다니매']),
    dict(ref=(57, 11, 30), lang='ko', en='about', words=[]),
    dict(ref=(57, 11, 30), lang='ko', en='seven', words=['칠']),

    # ---- 히브리서 11:31 ----
    dict(ref=(57, 11, 31), lang='ko', en='not#2', words=['아니한']),
    dict(ref=(57, 11, 31), lang='ko', en='had', words=[]),
    dict(ref=(57, 11, 31), lang='ko', en='with#2', words=[]),

    # ---- 히브리서 11:32 ----
    dict(ref=(57, 11, 32), lang='ko', en='shall', words=['하리요']),
    dict(ref=(57, 11, 32), lang='ko', en='the#1', words=['시간이']),
    dict(ref=(57, 11, 32), lang='ko', en='time', words=['시간이']),
    dict(ref=(57, 11, 32), lang='ko', en='fail', words=['부족하리로다']),
    dict(ref=(57, 11, 32), lang='ko', en='to', words=['말하려면']),
    dict(ref=(57, 11, 32), lang='ko', en='tell', words=['말하려면']),

    # ---- 히브리서 11:33 ----
    dict(ref=(57, 11, 33), lang='ko', en='subdued', words=['이기기도', '하며#1']),
    dict(ref=(57, 11, 33), lang='ko', en='wrought', words=['행하기도', '하며#2']),
    dict(ref=(57, 11, 33), lang='ko', en='obtained', words=['받기도', '하며#3']),

    # ---- 히브리서 11:34 ----
    dict(ref=(57, 11, 34), lang='ko', en='Quenched', words=['멸하기도', '하며#1']),
    dict(ref=(57, 11, 34), lang='ko', en='the#1', words=['세력을']),
    dict(ref=(57, 11, 34), lang='ko', en='violence', words=['세력을']),
    dict(ref=(57, 11, 34), lang='ko', en='fire', words=['불의']),
    dict(ref=(57, 11, 34), lang='ko', en='escaped', words=['피하기도', '하며#2']),
    dict(ref=(57, 11, 34), lang='ko', en='out', words=['가운데서']),
    dict(ref=(57, 11, 34), lang='ko', en='of#3', words=['가운데서']),
    dict(ref=(57, 11, 34), lang='ko', en='in', words=['전쟁에']),
    dict(ref=(57, 11, 34), lang='ko', en='turned', words=[]),
    dict(ref=(57, 11, 34), lang='ko', en='flight', words=['물리치기도', '하며#4']),
    dict(ref=(57, 11, 34), lang='ko', en='the#5', words=['이방', '사람들의']),
    dict(ref=(57, 11, 34), lang='ko', en='aliens', words=['이방', '사람들의']),

    # 11:27·29·30 — 위 교정으로 비게 된 한국어를 채움
    # (올려 주신 for·which·about 의 words=[] 는 그대로 두고 다른 낱말에 건다)
    dict(ref=(57, 11, 27), lang='ko', en='he#2', words=['곧']),
    dict(ref=(57, 11, 27), lang='ko', en='is', words=['하여']),
    dict(ref=(57, 11, 29), lang='ko', en='Egyptians', words=['애굽', '사람들은']),
    dict(ref=(57, 11, 29), lang='ko', en='do', words=['이것을']),
    dict(ref=(57, 11, 30), lang='ko', en='days', words=['일', '동안']),
    dict(ref=(57, 11, 30), lang='ko', en='compassed', words=['두루', '다니매']),

    # months 를 '달'로 옮기면서 비게 된 '동안' (three months = 석 달 동안)
    dict(ref=(57, 11, 23), lang='ko', en='hid', words=['숨겨', '동안']),

    # his 를 떼면서 비게 된 '그'를 of 에 건다 (the top of his staff = 그 지팡이 머리에)
    dict(ref=(57, 11, 21), lang='ko', en='of#2', words=['그']),

    # 위 교정으로 비게 된 한국어를 채움 (11:14-17)
    dict(ref=(57, 11, 14), lang='ko', en='plainly', words=['나타냄이라']),
    dict(ref=(57, 11, 14), lang='ko', en='that#2', words=['것을']),
    dict(ref=(57, 11, 16), lang='ko', en='that', words=['있는', '것이라']),
    dict(ref=(57, 11, 17), lang='ko', en='was', words=['받을']),

    # 위 교정으로 비게 된 한국어를 채움 (더하기만, 올려 주신 words=[] 는 그대로 둠)
    dict(ref=(57, 11, 5), lang='ko', en='not#2', words=['다시', '아니하니라']),

    dict(ref=(57, 11, 6), lang='ko', en='must', words=['반드시', '할지니라']),
    dict(ref=(57, 11, 6), lang='ko', en='and', words=['것과', '또한']),

    dict(ref=(57, 11, 8), lang='ko', en='into', words=['땅에']),
    dict(ref=(57, 11, 8), lang='ko', en='a', words=['땅에']),
    dict(ref=(57, 11, 8), lang='ko', en='place', words=['땅에']),

    dict(ref=(57, 11, 9), lang='ko', en='heirs', words=['유업으로', '받은']),

    dict(ref=(57, 11, 10), lang='ko', en='builder', words=['경영하시고']),

    dict(ref=(57, 11, 11), lang='ko', en='because', words=['이는']),
    dict(ref=(57, 11, 11), lang='ko', en='faithful', words=['미쁘신', '줄']),

    # ---- 편집기 묶음: 말·말씀 (왕상 22:13 ~ 잠 22:21) ----
 # ---- 열왕기상 22:13 ----
    dict(ref=(10, 22, 13), lang='ko', en='gone', words=['간']),
    dict(ref=(10, 22, 13), lang='ko', en='to', words=['부르러']),
    dict(ref=(10, 22, 13), lang='ko', en='spake', words=['일러']),
    dict(ref=(10, 22, 13), lang='ko', en='saying', words=['가로되']),
    dict(ref=(10, 22, 13), lang='ko', en='the#2', words=['말이']),
    dict(ref=(10, 22, 13), lang='ko', en='words', words=['말이']),
    dict(ref=(10, 22, 13), lang='ko', en='of#1', words=['선지자들의']),
    dict(ref=(10, 22, 13), lang='ko', en='declare', words=['여출']),
    dict(ref=(10, 22, 13), lang='ko', en='good#1', words=['길하게#2']),
    dict(ref=(10, 22, 13), lang='ko', en='one#1', words=['일구하여']),
    dict(ref=(10, 22, 13), lang='ko', en='mouth', words=['일구하여']),
    dict(ref=(10, 22, 13), lang='ko', en='thy', words=['당신의']),
    dict(ref=(10, 22, 13), lang='ko', en='word#1', words=['말도']),
    dict(ref=(10, 22, 13), lang='ko', en='pray', words=['청컨대']),
    dict(ref=(10, 22, 13), lang='ko', en='the#5', words=['말처럼']),
    dict(ref=(10, 22, 13), lang='ko', en='word#2', words=['말처럼']),
    dict(ref=(10, 22, 13), lang='ko', en='of#3', words=['중']),
    dict(ref=(10, 22, 13), lang='ko', en='good#2', words=['길하게#1']),

    # ---- 열왕기하 3:7 ----
    dict(ref=(11, 3, 7), lang='ko', en='he#1', words=[]),
    dict(ref=(11, 3, 7), lang='ko', en='to#1', words=['여호사밧에게']),
    dict(ref=(11, 3, 7), lang='ko', en='saying', words=['이르되']),
    dict(ref=(11, 3, 7), lang='ko', en='The', words=['왕이']),
    dict(ref=(11, 3, 7), lang='ko', en='king#2', words=['왕이']),
    dict(ref=(11, 3, 7), lang='ko', en='against#1', words=['배반하였으니']),
    dict(ref=(11, 3, 7), lang='ko', en='thou#1', words=['당신은']),
    dict(ref=(11, 3, 7), lang='ko', en='me#2', words=['나와']),
    dict(ref=(11, 3, 7), lang='ko', en='against#2', words=['치시겠느뇨']),
    dict(ref=(11, 3, 7), lang='ko', en='he#2', words=['저가']),
    dict(ref=(11, 3, 7), lang='ko', en='said', words=['가로되']),
    dict(ref=(11, 3, 7), lang='ko', en='I#1', words=['내가']),
    dict(ref=(11, 3, 7), lang='ko', en='will', words=['올라가리이다']),
    dict(ref=(11, 3, 7), lang='ko', en='I#2', words=['올라가리이다', '나는']),
    dict(ref=(11, 3, 7), lang='ko', en='as#1', words=['일반이요#1']),
    dict(ref=(11, 3, 7), lang='ko', en='thou#2', words=['당신과']),
    dict(ref=(11, 3, 7), lang='ko', en='my#1', words=['내#1']),
    dict(ref=(11, 3, 7), lang='ko', en='as#2', words=['일반이요#2']),
    dict(ref=(11, 3, 7), lang='ko', en='thy#1', words=['당신의#1']),
    dict(ref=(11, 3, 7), lang='ko', en='people#2', words=['백성과']),
    dict(ref=(11, 3, 7), lang='ko', en='my#2', words=['내#2']),
    dict(ref=(11, 3, 7), lang='ko', en='horses#1', words=['말들도']),
    dict(ref=(11, 3, 7), lang='ko', en='as#3', words=['일반이니이다']),
    dict(ref=(11, 3, 7), lang='ko', en='thy#2', words=['당신의#2']),
    dict(ref=(11, 3, 7), lang='ko', en='horses#2', words=['말들과']),

    # ---- 열왕기하 14:6 ----
    dict(ref=(11, 14, 6), lang='ko', en='of#1', words=['죽인', '자의']),
    dict(ref=(11, 14, 6), lang='ko', en='the#2', words=['죽인', '자의']),
    dict(ref=(11, 14, 6), lang='ko', en='murderers', words=['죽인', '자의']),
    dict(ref=(11, 14, 6), lang='ko', en='slew', words=['죽이지#1']),
    dict(ref=(11, 14, 6), lang='ko', en='unto', words=['대로']),
    dict(ref=(11, 14, 6), lang='ko', en='that', words=['대로']),
    dict(ref=(11, 14, 6), lang='ko', en='which', words=['대로']),
    dict(ref=(11, 14, 6), lang='ko', en='is', words=['기록된']),
    dict(ref=(11, 14, 6), lang='ko', en='in', words=['율법책에']),
    dict(ref=(11, 14, 6), lang='ko', en='of#2', words=['율법책에']),
    dict(ref=(11, 14, 6), lang='ko', en='the#4', words=['율법책에']),
    dict(ref=(11, 14, 6), lang='ko', en='law', words=['율법책에']),
    dict(ref=(11, 14, 6), lang='ko', en='of#3', words=['모세의']),
    dict(ref=(11, 14, 6), lang='ko', en='the#5', words=['여호와께서']),
    dict(ref=(11, 14, 6), lang='ko', en='Lord', words=['여호와께서']),
    dict(ref=(11, 14, 6), lang='ko', en='The', words=['아비를']),
    dict(ref=(11, 14, 6), lang='ko', en='fathers#1', words=['아비를']),
    dict(ref=(11, 14, 6), lang='ko', en='not#2', words=['말#1']),
    dict(ref=(11, 14, 6), lang='ko', en='be#1', words=['죽이지#2']),
    dict(ref=(11, 14, 6), lang='ko', en='put#1', words=['죽이지#2']),
    dict(ref=(11, 14, 6), lang='ko', en='to#1', words=['죽이지#2']),
    dict(ref=(11, 14, 6), lang='ko', en='death#1', words=['죽이지#2']),
    dict(ref=(11, 14, 6), lang='ko', en='for#1', words=['인하여#1']),
    dict(ref=(11, 14, 6), lang='ko', en='the#6', words=['자녀로']),
    dict(ref=(11, 14, 6), lang='ko', en='children#2', words=['자녀로']),
    dict(ref=(11, 14, 6), lang='ko', en='nor', words=['말#2']),
    dict(ref=(11, 14, 6), lang='ko', en='the#7', words=['자녀를']),
    dict(ref=(11, 14, 6), lang='ko', en='children#3', words=['자녀를']),
    dict(ref=(11, 14, 6), lang='ko', en='be#2', words=['죽이지#3']),
    dict(ref=(11, 14, 6), lang='ko', en='put#2', words=['죽이지#3']),
    dict(ref=(11, 14, 6), lang='ko', en='to#2', words=['죽이지#3']),
    dict(ref=(11, 14, 6), lang='ko', en='death#2', words=['죽이지#3']),
    dict(ref=(11, 14, 6), lang='ko', en='for#2', words=['인하여#2']),
    dict(ref=(11, 14, 6), lang='ko', en='the#8', words=['아비로']),
    dict(ref=(11, 14, 6), lang='ko', en='fathers#2', words=['아비로']),
    dict(ref=(11, 14, 6), lang='ko', en='every', words=['사람마다']),
    dict(ref=(11, 14, 6), lang='ko', en='shall#2', words=['것이니라']),
    dict(ref=(11, 14, 6), lang='ko', en='be#3', words=['죽을']),
    dict(ref=(11, 14, 6), lang='ko', en='put#3', words=['죽을']),
    dict(ref=(11, 14, 6), lang='ko', en='to#3', words=['죽을']),
    dict(ref=(11, 14, 6), lang='ko', en='death#3', words=['죽을']),
    dict(ref=(11, 14, 6), lang='ko', en='for#3', words=['인하여#3']),
    dict(ref=(11, 14, 6), lang='ko', en='own', words=['자기의']),

    # ---- 열왕기하 19:10 ----
    dict(ref=(11, 19, 10), lang='ko', en='speak', words=['말하여']),
    dict(ref=(11, 19, 10), lang='ko', en='to', words=['히스기야에게']),
    dict(ref=(11, 19, 10), lang='ko', en='not#1', words=['말라']),
    dict(ref=(11, 19, 10), lang='ko', en='thy', words=['네']),
    dict(ref=(11, 19, 10), lang='ko', en='whom', words=[]),
    dict(ref=(11, 19, 10), lang='ko', en='deceive', words=['속지']),
    dict(ref=(11, 19, 10), lang='ko', en='thee', words=[]),
    dict(ref=(11, 19, 10), lang='ko', en='saying#2', words=['하는', '말에']),
    dict(ref=(11, 19, 10), lang='ko', en='into', words=['손에']),
    dict(ref=(11, 19, 10), lang='ko', en='the#1', words=['손에']),
    dict(ref=(11, 19, 10), lang='ko', en='hand', words=['손에']),
    dict(ref=(11, 19, 10), lang='ko', en='of#2', words=['왕의']),
    dict(ref=(11, 19, 10), lang='ko', en='the#2', words=['왕의']),
    dict(ref=(11, 19, 10), lang='ko', en='king#2', words=['왕의']),

    # ---- 열왕기하 22:13 ----
    dict(ref=(11, 22, 13), lang='ko', en='enquire', words=['물으라']),
    dict(ref=(11, 22, 13), lang='ko', en='of#1', words=['물으라']),
    dict(ref=(11, 22, 13), lang='ko', en='for#2', words=['위하여#1']),
    dict(ref=(11, 22, 13), lang='ko', en='for#3', words=['위하여#1']),
    dict(ref=(11, 22, 13), lang='ko', en='concerning#1', words=['대하여']),
    dict(ref=(11, 22, 13), lang='ko', en='book#1', words=['책의#1']),
    dict(ref=(11, 22, 13), lang='ko', en='the#5', words=['여호와께서']),
    dict(ref=(11, 22, 13), lang='ko', en='Lord#2', words=['여호와께서']),
    dict(ref=(11, 22, 13), lang='ko', en='against', words=['우리에게']),
    dict(ref=(11, 22, 13), lang='ko', en='us#1', words=['우리에게']),
    dict(ref=(11, 22, 13), lang='ko', en='not', words=['아니하며', '아니하였으므로']),
    dict(ref=(11, 22, 13), lang='ko', en='unto#1', words=['이#2', '말씀을']),
    dict(ref=(11, 22, 13), lang='ko', en='the#6', words=['이#2', '말씀을']),
    dict(ref=(11, 22, 13), lang='ko', en='words#2', words=['이#2', '말씀을']),
    dict(ref=(11, 22, 13), lang='ko', en='of#4', words=['책의#2']),
    dict(ref=(11, 22, 13), lang='ko', en='this#2', words=['책의#2']),
    dict(ref=(11, 22, 13), lang='ko', en='book#2', words=['책의#2']),
    dict(ref=(11, 22, 13), lang='ko', en='do', words=['준행치']),
    dict(ref=(11, 22, 13), lang='ko', en='according', words=['준행치']),
    dict(ref=(11, 22, 13), lang='ko', en='all#2', words=['모든', '것을']),
    dict(ref=(11, 22, 13), lang='ko', en='concerning#2', words=['위하여#2']),
    dict(ref=(11, 22, 13), lang='ko', en='us#2', words=['우리를']),

    # ---- 역대하 10:7 ----
    dict(ref=(13, 10, 7), lang='ko', en='And', words=[]),
    dict(ref=(13, 10, 7), lang='ko', en='spake', words=['대답하여']),
    dict(ref=(13, 10, 7), lang='ko', en='him', words=[]),
    dict(ref=(13, 10, 7), lang='ko', en='thou', words=[]),
    dict(ref=(13, 10, 7), lang='ko', en='be#1', words=['후대하여']),
    dict(ref=(13, 10, 7), lang='ko', en='kind', words=['후대하여']),
    dict(ref=(13, 10, 7), lang='ko', en='them#1', words=[]),
    dict(ref=(13, 10, 7), lang='ko', en='speak', words=['하시면']),
    dict(ref=(13, 10, 7), lang='ko', en='words', words=['말을']),
    dict(ref=(13, 10, 7), lang='ko', en='they#2', words=['저희가']),
    dict(ref=(13, 10, 7), lang='ko', en='will', words=['되리이다']),
    dict(ref=(13, 10, 7), lang='ko', en='be#2', words=['되리이다']),
    dict(ref=(13, 10, 7), lang='ko', en='for', words=['영영히']),

    # ---- 역대하 11:4 ----
    dict(ref=(13, 11, 4), lang='ko', en='Thus', words=[]),
    dict(ref=(13, 11, 4), lang='ko', en='Ye', words=['너희는']),
    dict(ref=(13, 11, 4), lang='ko', en='nor', words=['말고']),
    dict(ref=(13, 11, 4), lang='ko', en='fight', words=['싸우지']),
    dict(ref=(13, 11, 4), lang='ko', en='against#1', words=['형제와']),
    dict(ref=(13, 11, 4), lang='ko', en='your', words=['너희']),
    dict(ref=(13, 11, 4), lang='ko', en='to', words=['집으로']),
    dict(ref=(13, 11, 4), lang='ko', en='his', words=['집으로']),
    dict(ref=(13, 11, 4), lang='ko', en='house', words=[]),
    dict(ref=(13, 11, 4), lang='ko', en='of#1', words=['내게로']),
    dict(ref=(13, 11, 4), lang='ko', en='the#2', words=['말씀을']),
    dict(ref=(13, 11, 4), lang='ko', en='words', words=['말씀을']),
    dict(ref=(13, 11, 4), lang='ko', en='the#3', words=['여호와의#2']),
    dict(ref=(13, 11, 4), lang='ko', en='Lord#2', words=['여호와의#2']),
    dict(ref=(13, 11, 4), lang='ko', en='returned', words=['돌아가고']),
    dict(ref=(13, 11, 4), lang='ko', en='going', words=['가지']),
    dict(ref=(13, 11, 4), lang='ko', en='against#2', words=['여로보암을']),

    # ---- 역대하 18:12 ----
    dict(ref=(13, 18, 12), lang='ko', en='went', words=['간']),
    dict(ref=(13, 18, 12), lang='ko', en='to#1', words=['부르러']),
    dict(ref=(13, 18, 12), lang='ko', en='call', words=['부르러']),
    dict(ref=(13, 18, 12), lang='ko', en='spake', words=['일러']),
    dict(ref=(13, 18, 12), lang='ko', en='saying', words=['가로되']),
    dict(ref=(13, 18, 12), lang='ko', en='the#2', words=['말이']),
    dict(ref=(13, 18, 12), lang='ko', en='words', words=['말이']),
    dict(ref=(13, 18, 12), lang='ko', en='of#1', words=[]),
    dict(ref=(13, 18, 12), lang='ko', en='declare', words=['여출일구하여']),
    dict(ref=(13, 18, 12), lang='ko', en='good#1', words=['길하게#1']),
    dict(ref=(13, 18, 12), lang='ko', en='to#3', words=['왕에게']),
    dict(ref=(13, 18, 12), lang='ko', en='with', words=['여출일구하여']),
    dict(ref=(13, 18, 12), lang='ko', en='one#1', words=['여출일구하여']),
    dict(ref=(13, 18, 12), lang='ko', en='assent', words=['여출일구하여']),
    dict(ref=(13, 18, 12), lang='ko', en='thy', words=['당신의']),
    dict(ref=(13, 18, 12), lang='ko', en='word', words=['말도']),
    dict(ref=(13, 18, 12), lang='ko', en='pray', words=['청컨대']),
    dict(ref=(13, 18, 12), lang='ko', en='like', words=['사람처럼']),
    dict(ref=(13, 18, 12), lang='ko', en='of#2', words=['중']),
    dict(ref=(13, 18, 12), lang='ko', en='speak', words=['하소서']),
    dict(ref=(13, 18, 12), lang='ko', en='good#2', words=['길하게#2']),

    # ---- 역대하 25:4 ----
    dict(ref=(13, 25, 4), lang='ko', en='But', words=[]),
    dict(ref=(13, 25, 4), lang='ko', en='as', words=['대로']),
    dict(ref=(13, 25, 4), lang='ko', en='the#3', words=['여호와께서']),
    dict(ref=(13, 25, 4), lang='ko', en='The', words=['아비를']),
    dict(ref=(13, 25, 4), lang='ko', en='fathers#1', words=['아비를']),
    dict(ref=(13, 25, 4), lang='ko', en='not#2', words=['말#1']),
    dict(ref=(13, 25, 4), lang='ko', en='die#1', words=['죽이지#2']),
    dict(ref=(13, 25, 4), lang='ko', en='the#4', words=['자녀를']),
    dict(ref=(13, 25, 4), lang='ko', en='children#2', words=['자녀를']),
    dict(ref=(13, 25, 4), lang='ko', en='neither', words=['아니하였으니', '말#2']),
    dict(ref=(13, 25, 4), lang='ko', en='shall#2', words=['것이라']),
    dict(ref=(13, 25, 4), lang='ko', en='the#5', words=['자녀를']),
    dict(ref=(13, 25, 4), lang='ko', en='children#3', words=['자녀를']),
    dict(ref=(13, 25, 4), lang='ko', en='die#2', words=['죽이지#3']),
    dict(ref=(13, 25, 4), lang='ko', en='for#2', words=['인하여#2']),
    dict(ref=(13, 25, 4), lang='ko', en='the#6', words=['아비로']),
    dict(ref=(13, 25, 4), lang='ko', en='fathers#2', words=['아비로']),
    dict(ref=(13, 25, 4), lang='ko', en='shall#3', words=['것이니라']),
    dict(ref=(13, 25, 4), lang='ko', en='die#3', words=['죽을']),
    dict(ref=(13, 25, 4), lang='ko', en='for#3', words=['인하여#3']),
    dict(ref=(13, 25, 4), lang='ko', en='own', words=['자기의']),

    # ---- 역대하 34:21 ----
    dict(ref=(13, 34, 21), lang='ko', en='enquire', words=['물으라']),
    dict(ref=(13, 34, 21), lang='ko', en='of#1', words=['대하여']),
    dict(ref=(13, 34, 21), lang='ko', en='the#1', words=['여호와께']),
    dict(ref=(13, 34, 21), lang='ko', en='Lord#1', words=['여호와께']),
    dict(ref=(13, 34, 21), lang='ko', en='and#1', words=['및']),
    dict(ref=(13, 34, 21), lang='ko', en='for#2', words=['위하여']),
    dict(ref=(13, 34, 21), lang='ko', en='them', words=['남은', '자를']),
    dict(ref=(13, 34, 21), lang='ko', en='that#1', words=['자를']),
    dict(ref=(13, 34, 21), lang='ko', en='are', words=[]),
    dict(ref=(13, 34, 21), lang='ko', en='left', words=['남은']),
    dict(ref=(13, 34, 21), lang='ko', en='concerning', words=['대하여']),
    dict(ref=(13, 34, 21), lang='ko', en='the#3', words=['책의']),
    dict(ref=(13, 34, 21), lang='ko', en='book#1', words=['책의']),
    dict(ref=(13, 34, 21), lang='ko', en='the#5', words=['여호와께서']),
    dict(ref=(13, 34, 21), lang='ko', en='Lord#2', words=['여호와께서']),
    dict(ref=(13, 34, 21), lang='ko', en='upon', words=['우리에게']),
    dict(ref=(13, 34, 21), lang='ko', en='us', words=['우리에게']),
    dict(ref=(13, 34, 21), lang='ko', en='not', words=['아니하고', '아니하였으므로']),
    dict(ref=(13, 34, 21), lang='ko', en='kept', words=['지키지']),
    dict(ref=(13, 34, 21), lang='ko', en='the#6', words=['말씀을']),
    dict(ref=(13, 34, 21), lang='ko', en='word', words=['말씀을']),
    dict(ref=(13, 34, 21), lang='ko', en='the#7', words=['여호와의']),
    dict(ref=(13, 34, 21), lang='ko', en='Lord#3', words=['여호와의']),
    dict(ref=(13, 34, 21), lang='ko', en='do', words=['준행치']),
    dict(ref=(13, 34, 21), lang='ko', en='after', words=['준행치']),
    dict(ref=(13, 34, 21), lang='ko', en='all', words=['모든']),
    dict(ref=(13, 34, 21), lang='ko', en='book#2', words=['책에']),

    # ---- 욥기 8:2 ----
    dict(ref=(17, 8, 2), lang='ko', en='How', words=['어느#1', '때까지#1']),
    dict(ref=(17, 8, 2), lang='ko', en='long#1', words=['어느#1', '때까지#1']),
    dict(ref=(17, 8, 2), lang='ko', en='thou', words=['네가']),
    dict(ref=(17, 8, 2), lang='ko', en='speak', words=['말을', '하겠으며']),
    dict(ref=(17, 8, 2), lang='ko', en='how', words=['어느#2', '때까지#2']),
    dict(ref=(17, 8, 2), lang='ko', en='long#2', words=['어느#2', '때까지#2']),
    dict(ref=(17, 8, 2), lang='ko', en='the', words=['말이']),
    dict(ref=(17, 8, 2), lang='ko', en='words', words=['말이']),
    dict(ref=(17, 8, 2), lang='ko', en='thy', words=['네']),
    dict(ref=(17, 8, 2), lang='ko', en='a', words=['광풍과']),
    dict(ref=(17, 8, 2), lang='ko', en='strong', words=['광풍과']),

    # ---- 욥기 24:25 ----
    dict(ref=(17, 24, 25), lang='ko', en='if', words=['가령']),
    dict(ref=(17, 24, 25), lang='ko', en='so', words=['그렇지']),
    dict(ref=(17, 24, 25), lang='ko', en='me', words=['내#1', '말을']),
    dict(ref=(17, 24, 25), lang='ko', en='nothing', words=['헛되다']),
    dict(ref=(17, 24, 25), lang='ko', en='worth', words=['헛되다']),

    # ---- 욥기 29:22 ----
    dict(ref=(17, 29, 22), lang='ko', en='my#1', words=['내가']),
    dict(ref=(17, 29, 22), lang='ko', en='words', words=['말한']),
    dict(ref=(17, 29, 22), lang='ko', en='they', words=['그들이']),
    dict(ref=(17, 29, 22), lang='ko', en='spake', words=['말을']),
    dict(ref=(17, 29, 22), lang='ko', en='not', words=['내지', '못하였었나니']),
    dict(ref=(17, 29, 22), lang='ko', en='again', words=['내지', '못하였었나니']),
    dict(ref=(17, 29, 22), lang='ko', en='my#2', words=['나의']),
    dict(ref=(17, 29, 22), lang='ko', en='speech', words=['말이']),
    dict(ref=(17, 29, 22), lang='ko', en='dropped', words=['이슬', '같이', '됨이니라']),
    dict(ref=(17, 29, 22), lang='ko', en='upon', words=['그들에게']),
    dict(ref=(17, 29, 22), lang='ko', en='them', words=['그들에게']),

    # ---- 욥기 33:1 ----
    dict(ref=(17, 33, 1), lang='ko', en='pray', words=['원하노라']),
    dict(ref=(17, 33, 1), lang='ko', en='my#1', words=['내']),
    dict(ref=(17, 33, 1), lang='ko', en='speeches', words=['말을']),
    dict(ref=(17, 33, 1), lang='ko', en='my#2', words=['나의']),
    dict(ref=(17, 33, 1), lang='ko', en='words', words=['말에']),

    # ---- 잠언 1:6 ----
    dict(ref=(19, 1, 6), lang='ko', en='To', words=['깨달으리라']),
    dict(ref=(19, 1, 6), lang='ko', en='the#1', words=['비유와']),
    dict(ref=(19, 1, 6), lang='ko', en='interpretation', words=['비유와']),
    dict(ref=(19, 1, 6), lang='ko', en='of', words=['지혜있는', '자의']),
    dict(ref=(19, 1, 6), lang='ko', en='the#3', words=['지혜있는', '자의']),
    dict(ref=(19, 1, 6), lang='ko', en='wise', words=['지혜있는', '자의']),
    dict(ref=(19, 1, 6), lang='ko', en='sayings', words=['말을']),

    # ---- 잠언 4:20 ----
    dict(ref=(19, 4, 20), lang='ko', en='My', words=['내#1']),
    dict(ref=(19, 4, 20), lang='ko', en='attend', words=['주의하며']),
    dict(ref=(19, 4, 20), lang='ko', en='to', words=['말에']),
    dict(ref=(19, 4, 20), lang='ko', en='my#1', words=['내#2']),
    dict(ref=(19, 4, 20), lang='ko', en='words', words=['말에']),
    dict(ref=(19, 4, 20), lang='ko', en='thine', words=['네']),
    dict(ref=(19, 4, 20), lang='ko', en='unto', words=['것에']),
    dict(ref=(19, 4, 20), lang='ko', en='my#2', words=['나의']),
    dict(ref=(19, 4, 20), lang='ko', en='sayings', words=['이르는']),

    # ---- 잠언 6:2 ----
    dict(ref=(19, 6, 2), lang='ko', en='Thou', words=['네#1', '잡히게']),
    dict(ref=(19, 6, 2), lang='ko', en='with#1', words=['말로#1']),
    dict(ref=(19, 6, 2), lang='ko', en='the#1', words=['말로#1']),
    dict(ref=(19, 6, 2), lang='ko', en='words#1', words=['말로#1']),
    dict(ref=(19, 6, 2), lang='ko', en='of#1', words=['입의#1']),
    dict(ref=(19, 6, 2), lang='ko', en='thou', words=['네가']),
    dict(ref=(19, 6, 2), lang='ko', en='taken', words=['잡히게']),
    dict(ref=(19, 6, 2), lang='ko', en='with#2', words=['인하여']),
    dict(ref=(19, 6, 2), lang='ko', en='the#2', words=['말로#2']),
    dict(ref=(19, 6, 2), lang='ko', en='words#2', words=['말로#2']),
    dict(ref=(19, 6, 2), lang='ko', en='of#2', words=['입의#2']),
    dict(ref=(19, 6, 2), lang='ko', en='thy#2', words=['네#2']),

    # ---- 잠언 7:21 ----
    dict(ref=(19, 7, 21), lang='ko', en='much', words=['여러가지']),
    dict(ref=(19, 7, 21), lang='ko', en='fair', words=['고운']),
    dict(ref=(19, 7, 21), lang='ko', en='speech', words=['말로#1']),
    dict(ref=(19, 7, 21), lang='ko', en='caused', words=['하며']),
    dict(ref=(19, 7, 21), lang='ko', en='to', words=['혹하게']),
    dict(ref=(19, 7, 21), lang='ko', en='yield', words=['혹하게']),
    dict(ref=(19, 7, 21), lang='ko', en='with', words=['호리는', '말로#2']),
    dict(ref=(19, 7, 21), lang='ko', en='the', words=['호리는', '말로#2']),
    dict(ref=(19, 7, 21), lang='ko', en='flattering', words=['호리는', '말로#2']),

    # ---- 잠언 22:21 ----
    dict(ref=(19, 22, 21), lang='ko', en='make', words=['하며']),
    dict(ref=(19, 22, 21), lang='ko', en='mightest', words=['하려']),
    dict(ref=(19, 22, 21), lang='ko', en='answer', words=['회답하게']),
    dict(ref=(19, 22, 21), lang='ko', en='the#3', words=['말씀으로']),
    dict(ref=(19, 22, 21), lang='ko', en='words#2', words=['말씀으로']),
    dict(ref=(19, 22, 21), lang='ko', en='unto', words=['너를']),
    dict(ref=(19, 22, 21), lang='ko', en='thee#2', words=['너를']),

    # 위 교정으로 비게 된 자리를 채움 — 올려 주신 항목 뒤에 와야 적용된다.
    # 인용을 닫는 어미(하니·하셨다·하라·하신지라·하셨더라)는 비워 둔다.
    dict(ref=(11, 14, 6), lang='ko', en='But', words=['이는']),
    dict(ref=(11, 14, 6), lang='ko', en='according', words=['대로', '함이라']),
    dict(ref=(11, 14, 6), lang='ko', en='wherein', words=['곧']),
    dict(ref=(11, 14, 6), lang='ko', en='nor', words=['말#2', '것이라']),
    dict(ref=(11, 14, 6), lang='ko', en='but', words=['오직']),

    dict(ref=(11, 19, 10), lang='ko', en='Thus', words=['이같이']),

    dict(ref=(11, 22, 13), lang='ko', en='book#2', words=['책의#2', '책에']),

    dict(ref=(13, 11, 4), lang='ko', en='done', words=['말미암아', '난']),
    dict(ref=(13, 11, 4), lang='ko', en='against#2', words=['여로보암을', '치러']),

    dict(ref=(13, 25, 4), lang='ko', en='But', words=['이는']),
    dict(ref=(13, 25, 4), lang='ko', en='where', words=['곧']),
    dict(ref=(13, 25, 4), lang='ko', en='but#2', words=['오직']),
    # children 두 벌이 둘 다 '자녀를'로 가 있어서 '자녀로'가 비었다 — 갈라 준다
    dict(ref=(13, 25, 4), lang='ko', en='the#4', words=['자녀로']),
    dict(ref=(13, 25, 4), lang='ko', en='children#2', words=['자녀로']),
    dict(ref=(13, 25, 4), lang='ko', en='the#5', words=['자녀를']),
    dict(ref=(13, 25, 4), lang='ko', en='children#3', words=['자녀를']),

    # ---- 전도서 12:10 ----
    dict(ref=(20, 12, 10), lang='ko', en='sought', words=['힘써']),
    dict(ref=(20, 12, 10), lang='ko', en='to', words=['힘써']),
    dict(ref=(20, 12, 10), lang='ko', en='find', words=['구하였나니']),
    dict(ref=(20, 12, 10), lang='ko', en='out', words=['구하였나니']),
    dict(ref=(20, 12, 10), lang='ko', en='acceptable', words=['아름다운']),
    dict(ref=(20, 12, 10), lang='ko', en='words#1', words=['말을']),
    dict(ref=(20, 12, 10), lang='ko', en='that', words=['것은']),
    dict(ref=(20, 12, 10), lang='ko', en='which', words=['것은']),
    dict(ref=(20, 12, 10), lang='ko', en='was#1', words=['것은']),
    dict(ref=(20, 12, 10), lang='ko', en='even', words=[]),
    dict(ref=(20, 12, 10), lang='ko', en='words#2', words=['말씀이니라']),
    dict(ref=(20, 12, 10), lang='ko', en='of', words=['진리의']),

    # ---- 전도서 5:2 ----
    dict(ref=(20, 5, 2), lang='ko', en='Be', words=['말며']),
    dict(ref=(20, 5, 2), lang='ko', en='not#1', words=['말며']),
    dict(ref=(20, 5, 2), lang='ko', en='rash', words=['함부로', '열지']),
    dict(ref=(20, 5, 2), lang='ko', en='let#1', words=['말라']),
    dict(ref=(20, 5, 2), lang='ko', en='not#2', words=['말라']),
    dict(ref=(20, 5, 2), lang='ko', en='hasty', words=[]),
    dict(ref=(20, 5, 2), lang='ko', en='to', words=['말을#1', '내지']),
    dict(ref=(20, 5, 2), lang='ko', en='utter', words=['말을#1', '내지']),
    dict(ref=(20, 5, 2), lang='ko', en='thing', words=['것이라']),
    dict(ref=(20, 5, 2), lang='ko', en='for', words=['하나님은']),
    dict(ref=(20, 5, 2), lang='ko', en='God#2', words=['하나님은']),
    dict(ref=(20, 5, 2), lang='ko', en='is', words=['계시고']),
    dict(ref=(20, 5, 2), lang='ko', en='in', words=['하늘에']),
    dict(ref=(20, 5, 2), lang='ko', en='thou', words=['너는#2']),
    dict(ref=(20, 5, 2), lang='ko', en='upon', words=['땅에']),
    dict(ref=(20, 5, 2), lang='ko', en='let#2', words=['할', '것이라']),
    dict(ref=(20, 5, 2), lang='ko', en='words', words=['말을#2']),
    # thou 를 '너는'(2)로 옮기면서 비게 된 첫째 '너는'은 thy(1)에 건다
    # (Be not rash with thy mouth = 너는 … 함부로 입을 열지 말며)
    dict(ref=(20, 5, 2), lang='ko', en='thy#1', words=['너는#1']),
    # '마땅히'는 일부러 비워 둔다 — be 에 맞댈 자리가 아니다.
    # 빈 자리를 메우는 일괄 작업은 여기를 건드리지 말아야 한다.
    dict(ref=(20, 5, 2), lang='ko', en='be#2', words=[]),
    # '있음이니라'(thou upon earth 의 서술) — KJV 에 따로 된 동사가 없어 and 에 건다
    dict(ref=(20, 5, 2), lang='ko', en='and#2', words=['있음이니라']),

    # ---- 열왕기상 21:19 ----
    dict(ref=(10, 21, 19), lang='ko', en='thou#1', words=['너는']),
    dict(ref=(10, 21, 19), lang='ko', en='unto#1', words=['저에게#1']),
    dict(ref=(10, 21, 19), lang='ko', en='saying#1', words=['이르기를#1']),
    dict(ref=(10, 21, 19), lang='ko', en='Thus#1', words=[]),
    dict(ref=(10, 21, 19), lang='ko', en='saith#1', words=['말씀이#1']),
    dict(ref=(10, 21, 19), lang='ko', en='possession', words=['빼앗았느냐']),
    dict(ref=(10, 21, 19), lang='ko', en='saying#2', words=['이르기를#2']),
    dict(ref=(10, 21, 19), lang='ko', en='saith#2', words=['말씀이#2']),
    dict(ref=(10, 21, 19), lang='ko', en='dogs#1', words=['개들이#1']),
    dict(ref=(10, 21, 19), lang='ko', en='lick', words=['핥으리라']),
    dict(ref=(10, 21, 19), lang='ko', en='thy', words=['네#2']),
    dict(ref=(10, 21, 19), lang='ko', en='blood#2', words=['피도']),
    dict(ref=(10, 21, 19), lang='ko', en='thine', words=[]),
    # 비게 된 자리 중 다툼 없는 셋 — And(2)=또, him(2)=저에게(2), even=곧
    dict(ref=(10, 21, 19), lang='ko', en='And#2', words=['또#2']),
    dict(ref=(10, 21, 19), lang='ko', en='him#2', words=['저에게#2']),
    dict(ref=(10, 21, 19), lang='ko', en='even', words=['곧']),

    # ---- 열왕기상 13:26 ----
    dict(ref=(10, 13, 26), lang='ko', en='from', words=['길에서']),
    dict(ref=(10, 13, 26), lang='ko', en='is', words=[]),
    # is·the man 을 옮기면서 비게 된 자리 — '이는'은 It, '그 사람을'은 him(1)
    dict(ref=(10, 13, 26), lang='ko', en='It', words=['이는']),
    dict(ref=(10, 13, 26), lang='ko', en='him#1', words=['사람을']),
    dict(ref=(10, 13, 26), lang='ko', en='the#3', words=['사람이로다']),
    dict(ref=(10, 13, 26), lang='ko', en='man', words=['사람이로다']),
    dict(ref=(10, 13, 26), lang='ko', en='of#1', words=['하나님의']),
    dict(ref=(10, 13, 26), lang='ko', en='disobedient', words=['어긴']),
    dict(ref=(10, 13, 26), lang='ko', en='unto#1', words=['말씀을']),
    dict(ref=(10, 13, 26), lang='ko', en='the#4', words=['말씀을']),
    dict(ref=(10, 13, 26), lang='ko', en='the#5', words=['여호와의']),
    dict(ref=(10, 13, 26), lang='ko', en='Lord#1', words=['여호와의']),
    dict(ref=(10, 13, 26), lang='ko', en='the#6', words=['여호와께서#2']),
    dict(ref=(10, 13, 26), lang='ko', en='Lord#2', words=['여호와께서#2']),
    dict(ref=(10, 13, 26), lang='ko', en='him#2', words=['그를#1']),
    dict(ref=(10, 13, 26), lang='ko', en='unto#2', words=['사자에게']),
    dict(ref=(10, 13, 26), lang='ko', en='torn', words=['찢어']),
    dict(ref=(10, 13, 26), lang='ko', en='him#3', words=['그를#2']),
    dict(ref=(10, 13, 26), lang='ko', en='him#4', words=['그를#2']),
    dict(ref=(10, 13, 26), lang='ko', en='to', words=['같이']),
    dict(ref=(10, 13, 26), lang='ko', en='the#8', words=['말씀과']),
    dict(ref=(10, 13, 26), lang='ko', en='word#2', words=['말씀과']),
    dict(ref=(10, 13, 26), lang='ko', en='the#9', words=['여호와께서#1']),
    dict(ref=(10, 13, 26), lang='ko', en='Lord#3', words=['여호와께서#1']),
    dict(ref=(10, 13, 26), lang='ko', en='which#2', words=['말씀과']),
    dict(ref=(10, 13, 26), lang='ko', en='spake', words=['하신']),
    dict(ref=(10, 13, 26), lang='ko', en='unto#3', words=['그에게']),
    dict(ref=(10, 13, 26), lang='ko', en='him#5', words=['그에게']),
    # '사자가'는 which(1)에 건다 (the lion which hath torn him = 사자가 그를 찢어)
    dict(ref=(10, 13, 26), lang='ko', en='which#1', words=['사자가']),

    # ---- 열왕기상 13:21 ----
    dict(ref=(10, 13, 21), lang='ko', en='from', words=['유다에서부터']),
    dict(ref=(10, 13, 21), lang='ko', en='Thus', words=[]),
    dict(ref=(10, 13, 21), lang='ko', en='saith', words=['말씀에']),
    dict(ref=(10, 13, 21), lang='ko', en='the#2', words=['여호와의#1']),
    dict(ref=(10, 13, 21), lang='ko', en='Lord#1', words=['여호와의#1']),
    dict(ref=(10, 13, 21), lang='ko', en='thou', words=['네가']),
    dict(ref=(10, 13, 21), lang='ko', en='disobeyed', words=['어기며']),
    dict(ref=(10, 13, 21), lang='ko', en='the#3', words=['말씀을']),
    dict(ref=(10, 13, 21), lang='ko', en='mouth', words=['말씀을']),
    dict(ref=(10, 13, 21), lang='ko', en='the#4', words=['여호와의#2']),
    dict(ref=(10, 13, 21), lang='ko', en='Lord#2', words=['여호와의#2']),
    dict(ref=(10, 13, 21), lang='ko', en='the#5', words=['명령을']),
    dict(ref=(10, 13, 21), lang='ko', en='commandment', words=['명령을']),
    dict(ref=(10, 13, 21), lang='ko', en='the#6', words=['여호와가']),
    dict(ref=(10, 13, 21), lang='ko', en='Lord#3', words=['여호와가']),
    dict(ref=(10, 13, 21), lang='ko', en='thy', words=['네']),
    dict(ref=(10, 13, 21), lang='ko', en='God#2', words=['하나님']),
    dict(ref=(10, 13, 21), lang='ko', en='commanded', words=['명한']),
    dict(ref=(10, 13, 21), lang='ko', en='thee', words=['네가', '네게']),

    # ---- 열왕기상 12:24 ----
    dict(ref=(10, 12, 24), lang='ko', en='Thus', words=[]),
    dict(ref=(10, 12, 24), lang='ko', en='Ye', words=['너희는']),
    dict(ref=(10, 12, 24), lang='ko', en='nor', words=['말고']),
    dict(ref=(10, 12, 24), lang='ko', en='against', words=[]),
    dict(ref=(10, 12, 24), lang='ko', en='your', words=['너희']),
    dict(ref=(10, 12, 24), lang='ko', en='every', words=['각기']),
    dict(ref=(10, 12, 24), lang='ko', en='to#1', words=['집으로']),
    dict(ref=(10, 12, 24), lang='ko', en='his', words=['집으로']),
    dict(ref=(10, 12, 24), lang='ko', en='house', words=['집으로']),
    dict(ref=(10, 12, 24), lang='ko', en='thing', words=['일이']),
    dict(ref=(10, 12, 24), lang='ko', en='from', words=['말미암아']),
    dict(ref=(10, 12, 24), lang='ko', en='me', words=['내게로']),
    dict(ref=(10, 12, 24), lang='ko', en='hearkened', words=[]),
    dict(ref=(10, 12, 24), lang='ko', en='to#2', words=['듣고']),
    dict(ref=(10, 12, 24), lang='ko', en='the#3', words=['말씀을#1']),
    dict(ref=(10, 12, 24), lang='ko', en='word#1', words=['말씀을#1']),
    dict(ref=(10, 12, 24), lang='ko', en='the#4', words=['여호와의#2']),
    dict(ref=(10, 12, 24), lang='ko', en='Lord#2', words=['여호와의#2']),
    dict(ref=(10, 12, 24), lang='ko', en='returned', words=['돌아갔더라']),
    dict(ref=(10, 12, 24), lang='ko', en='according', words=['좇아']),
    dict(ref=(10, 12, 24), lang='ko', en='to#4', words=['그', '말씀을#2']),
    dict(ref=(10, 12, 24), lang='ko', en='the#5', words=['그', '말씀을#2']),
    dict(ref=(10, 12, 24), lang='ko', en='word#2', words=['그', '말씀을#2']),
    dict(ref=(10, 12, 24), lang='ko', en='of#3', words=['그', '말씀을#2']),
    dict(ref=(10, 12, 24), lang='ko', en='the#6', words=['그', '말씀을#2']),
    dict(ref=(10, 12, 24), lang='ko', en='Lord#3', words=['그', '말씀을#2']),
    # to(1)·the(4)·Lord(2)·me 를 옮기면서 비게 된 '난·것이라'는 is 에 건다
    # (this thing is from me = 이 일이 내게로 말미암아 난 것이라)
    dict(ref=(10, 12, 24), lang='ko', en='is', words=['난', '것이라']),

    # ---- 열왕기상 2:4 ----
    dict(ref=(10, 2, 4), lang='ko', en='continue', words=['확실히', '이루게']),
    dict(ref=(10, 2, 4), lang='ko', en='his', words=['말씀을']),
    dict(ref=(10, 2, 4), lang='ko', en='word', words=['말씀을']),
    dict(ref=(10, 2, 4), lang='ko', en='spake', words=['말씀하시기를']),
    # spake 를 옮기면서 비게 된 '하신'은 뒤쪽 said 에 건다 (said he = 하신 말씀을)
    dict(ref=(10, 2, 4), lang='ko', en='said', words=['하신']),
    dict(ref=(10, 2, 4), lang='ko', en='concerning', words=['대하여']),
    dict(ref=(10, 2, 4), lang='ko', en='me#1', words=['내#1', '일에']),
    dict(ref=(10, 2, 4), lang='ko', en='take', words=['삼가']),
    dict(ref=(10, 2, 4), lang='ko', en='me#2', words=['내#2']),
    dict(ref=(10, 2, 4), lang='ko', en='in', words=['진실히']),
    dict(ref=(10, 2, 4), lang='ko', en='with#1', words=['마음을']),
    dict(ref=(10, 2, 4), lang='ko', en='all#1', words=['마음을', '다하고']),
    dict(ref=(10, 2, 4), lang='ko', en='their#2', words=['마음을', '다하고']),
    dict(ref=(10, 2, 4), lang='ko', en='heart', words=['마음을']),
    dict(ref=(10, 2, 4), lang='ko', en='with#2', words=['성품을', '다하여']),
    dict(ref=(10, 2, 4), lang='ko', en='all#2', words=['성품을', '다하여']),
    dict(ref=(10, 2, 4), lang='ko', en='their#3', words=['성품을', '다하여']),
    dict(ref=(10, 2, 4), lang='ko', en='soul', words=['성품을']),
    dict(ref=(10, 2, 4), lang='ko', en='on', words=['오를']),

    # ---- 사무엘하 19:11 ----
    dict(ref=(9, 19, 11), lang='ko', en='sent', words=['기별하여']),
    dict(ref=(9, 19, 11), lang='ko', en='Speak', words=['이르기를']),
    dict(ref=(9, 19, 11), lang='ko', en='unto', words=['고하여']),
    dict(ref=(9, 19, 11), lang='ko', en='saying#2', words=['말이']),
    # ye 는 '너희는' 두 자리를 같이 받는다 (같은 '너희'를 두 번 쓴 자리)
    dict(ref=(9, 19, 11), lang='ko', en='ye', words=['너희는#1', '너희는#2']),
    dict(ref=(9, 19, 11), lang='ko', en='are', words=['되느냐']),
    dict(ref=(9, 19, 11), lang='ko', en='is', words=['하는']),
    dict(ref=(9, 19, 11), lang='ko', en='to#3', words=[]),
    dict(ref=(9, 19, 11), lang='ko', en='bring', words=['모시는']),
    dict(ref=(9, 19, 11), lang='ko', en='the#4', words=['왕을']),
    dict(ref=(9, 19, 11), lang='ko', en='king#2', words=['왕을']),
    # 첫째 'to his house'(왕을 모시러 가는 쪽)는 뒤쪽 궁으로다
    dict(ref=(9, 19, 11), lang='ko', en='to#4', words=['궁으로#2']),
    dict(ref=(9, 19, 11), lang='ko', en='his#1', words=['궁으로#2']),
    dict(ref=(9, 19, 11), lang='ko', en='house#1', words=['궁으로#2']),
    dict(ref=(9, 19, 11), lang='ko', en='come', words=['모셔오자']),
    dict(ref=(9, 19, 11), lang='ko', en='the#6', words=['왕을']),
    dict(ref=(9, 19, 11), lang='ko', en='king#3', words=['왕을']),
    dict(ref=(9, 19, 11), lang='ko', en='even', words=['도로']),
    dict(ref=(9, 19, 11), lang='ko', en='to#6', words=['궁으로#1']),
    dict(ref=(9, 19, 11), lang='ko', en='his#2', words=['궁으로#1']),
    dict(ref=(9, 19, 11), lang='ko', en='house#2', words=['궁으로#1']),

    # ---- 사무엘하 19:43 ----
    dict(ref=(9, 19, 43), lang='ko', en='the#1', words=['사람이']),
    dict(ref=(9, 19, 43), lang='ko', en='men#1', words=['사람이']),
    dict(ref=(9, 19, 43), lang='ko', en='the#2', words=['사람에게']),
    dict(ref=(9, 19, 43), lang='ko', en='men#2', words=['사람에게']),
    dict(ref=(9, 19, 43), lang='ko', en='We', words=['우리는']),
    dict(ref=(9, 19, 43), lang='ko', en='parts', words=['십분을']),
    # parts·right 를 옮기면서 비게 된 '가졌으니·있거늘'은 have 두 벌에 건다
    dict(ref=(9, 19, 43), lang='ko', en='have#1', words=['가졌으니']),
    dict(ref=(9, 19, 43), lang='ko', en='have#2', words=['있거늘']),
    dict(ref=(9, 19, 43), lang='ko', en='in#1', words=['대하여#1']),
    dict(ref=(9, 19, 43), lang='ko', en='right', words=['관계가']),
    dict(ref=(9, 19, 43), lang='ko', en='in#2', words=['대하여#2']),
    dict(ref=(9, 19, 43), lang='ko', en='than#1', words=['너희보다']),
    dict(ref=(9, 19, 43), lang='ko', en='ye#1', words=['너희보다']),
    dict(ref=(9, 19, 43), lang='ko', en='ye#2', words=['너희가']),
    dict(ref=(9, 19, 43), lang='ko', en='us', words=['우리를']),
    dict(ref=(9, 19, 43), lang='ko', en='our#1', words=['우리는', '우리와']),
    dict(ref=(9, 19, 43), lang='ko', en='advice', words=['의논하지']),
    dict(ref=(9, 19, 43), lang='ko', en='not', words=['아니하였느냐']),
    dict(ref=(9, 19, 43), lang='ko', en='be', words=[]),
    dict(ref=(9, 19, 43), lang='ko', en='in#3', words=['일에']),
    dict(ref=(9, 19, 43), lang='ko', en='bringing', words=['모셔', '오는']),
    dict(ref=(9, 19, 43), lang='ko', en='back', words=['모셔', '오는']),
    dict(ref=(9, 19, 43), lang='ko', en='our#2', words=['우리']),
    dict(ref=(9, 19, 43), lang='ko', en='king#2', words=['왕을']),
    dict(ref=(9, 19, 43), lang='ko', en='of#3', words=['사람의#1']),
    dict(ref=(9, 19, 43), lang='ko', en='the#5', words=['사람의#1']),
    dict(ref=(9, 19, 43), lang='ko', en='men#3', words=['사람의#1']),
    dict(ref=(9, 19, 43), lang='ko', en='fiercer', words=['더', '강경하였더라']),
    dict(ref=(9, 19, 43), lang='ko', en='than#2', words=['말보다']),
    dict(ref=(9, 19, 43), lang='ko', en='the#6', words=['말보다']),
    dict(ref=(9, 19, 43), lang='ko', en='words#2', words=['말보다']),
    dict(ref=(9, 19, 43), lang='ko', en='of#5', words=['사람의#2']),

    # ---- 신명기 32:46 ----
    dict(ref=(4, 32, 46), lang='ko', en='unto#1', words=['그들에게']),
    dict(ref=(4, 32, 46), lang='ko', en='your#1', words=['너희#1']),
    dict(ref=(4, 32, 46), lang='ko', en='the#1', words=['말을']),
    dict(ref=(4, 32, 46), lang='ko', en='this#1', words=['오늘날']),
    dict(ref=(4, 32, 46), lang='ko', en='shall', words=['하라']),
    dict(ref=(4, 32, 46), lang='ko', en='your#2', words=['너희#2', '명하여']),
    dict(ref=(4, 32, 46), lang='ko', en='to#2', words=['행하게']),
    dict(ref=(4, 32, 46), lang='ko', en='do', words=['행하게']),
    dict(ref=(4, 32, 46), lang='ko', en='all#2', words=['모든#2']),
    dict(ref=(4, 32, 46), lang='ko', en='the#2', words=['말씀을']),
    dict(ref=(4, 32, 46), lang='ko', en='words#2', words=['말씀을']),

    # ---- 신명기 5:28 ----
    dict(ref=(4, 5, 28), lang='ko', en='heard#1', words=['들으신지라', '들은즉']),
    dict(ref=(4, 5, 28), lang='ko', en='of#1', words=['너희의', '말하는#1']),
    dict(ref=(4, 5, 28), lang='ko', en='your', words=['너희의']),
    dict(ref=(4, 5, 28), lang='ko', en='words#1', words=['말하는#1']),
    dict(ref=(4, 5, 28), lang='ko', en='ye', words=['너희가']),
    dict(ref=(4, 5, 28), lang='ko', en='spake', words=['말할']),
    dict(ref=(4, 5, 28), lang='ko', en='unto#1', words=[]),
    dict(ref=(4, 5, 28), lang='ko', en='me#1', words=['내게#1']),
    dict(ref=(4, 5, 28), lang='ko', en='said#1', words=['이르시되']),
    dict(ref=(4, 5, 28), lang='ko', en='unto#2', words=['내게#2']),
    dict(ref=(4, 5, 28), lang='ko', en='me#2', words=['내게#2']),
    dict(ref=(4, 5, 28), lang='ko', en='have#1', words=['들은즉']),
    dict(ref=(4, 5, 28), lang='ko', en='heard#2', words=['들은즉']),
    dict(ref=(4, 5, 28), lang='ko', en='the#4', words=['그#1', '말소리를']),
    dict(ref=(4, 5, 28), lang='ko', en='voice#2', words=['그#1', '말소리를']),
    dict(ref=(4, 5, 28), lang='ko', en='of#2', words=['그#1', '말소리를']),
    dict(ref=(4, 5, 28), lang='ko', en='the#5', words=['그#1', '말소리를']),
    dict(ref=(4, 5, 28), lang='ko', en='words#2', words=['그#1', '말소리를']),
    dict(ref=(4, 5, 28), lang='ko', en='they#1', words=[]),
    dict(ref=(4, 5, 28), lang='ko', en='have#2', words=['말하는#2']),
    dict(ref=(4, 5, 28), lang='ko', en='spoken#1', words=['말하는#2']),
    dict(ref=(4, 5, 28), lang='ko', en='unto#3', words=['네게']),
    dict(ref=(4, 5, 28), lang='ko', en='said#2', words=['말이']),
    dict(ref=(4, 5, 28), lang='ko', en='spoken#2', words=['말이']),
    # 둘째 '그'는 that 에 건다 (all that they have spoken = 그 말이 다)
    dict(ref=(4, 5, 28), lang='ko', en='that', words=['그#2']),

    # ---- 민수기 36:5 ----
    dict(ref=(3, 36, 5), lang='ko', en='the#2', words=['말씀으로']),
    dict(ref=(3, 36, 5), lang='ko', en='word', words=['말씀으로']),
    dict(ref=(3, 36, 5), lang='ko', en='of#2', words=['여호와의']),
    dict(ref=(3, 36, 5), lang='ko', en='saying', words=['가로되']),
    dict(ref=(3, 36, 5), lang='ko', en='said', words=['말이']),
    dict(ref=(3, 36, 5), lang='ko', en='hath', words=['자손']),

    # ---- 출애굽기 34:27 ----
    dict(ref=(1, 34, 27), lang='ko', en='said', words=['이르시되']),
    dict(ref=(1, 34, 27), lang='ko', en='these#1', words=['이#1']),
    dict(ref=(1, 34, 27), lang='ko', en='after', words=['뜻대로']),
    dict(ref=(1, 34, 27), lang='ko', en='the#2', words=[]),
    dict(ref=(1, 34, 27), lang='ko', en='tenor', words=[]),
    dict(ref=(1, 34, 27), lang='ko', en='these#2', words=['이#2']),
    dict(ref=(1, 34, 27), lang='ko', en='words#2', words=['말들의']),
    dict(ref=(1, 34, 27), lang='ko', en='have', words=['세웠음이니라']),
    dict(ref=(1, 34, 27), lang='ko', en='made', words=['세웠음이니라']),
    dict(ref=(1, 34, 27), lang='ko', en='thee', words=['너와']),

    # ---- 출애굽기 24:3 ----
    dict(ref=(1, 24, 3), lang='ko', en='And', words=[]),
    # And 를 떼면서 비게 된 '그'는 the(4)에 건다 (all the judgments = 그 모든 율례를)
    dict(ref=(1, 24, 3), lang='ko', en='the#4', words=['그', '율례를']),
    dict(ref=(1, 24, 3), lang='ko', en='all#2', words=['모든#2']),
    dict(ref=(1, 24, 3), lang='ko', en='the#5', words=['그들이']),
    dict(ref=(1, 24, 3), lang='ko', en='people#2', words=['그들이']),
    dict(ref=(1, 24, 3), lang='ko', en='All', words=['모든#3']),
    dict(ref=(1, 24, 3), lang='ko', en='the#6', words=['말씀을']),
    dict(ref=(1, 24, 3), lang='ko', en='hath', words=['명하신']),
    dict(ref=(1, 24, 3), lang='ko', en='will', words=['준행하리이다']),
    dict(ref=(1, 24, 3), lang='ko', en='do', words=['준행하리이다']),

    # ---- 창세기 39:19 ----
    dict(ref=(0, 39, 19), lang='ko', en='his#1', words=[]),
    dict(ref=(0, 39, 19), lang='ko', en='master', words=['주인이']),
    dict(ref=(0, 39, 19), lang='ko', en='words', words=['말을']),
    dict(ref=(0, 39, 19), lang='ko', en='his#2', words=['그']),
    dict(ref=(0, 39, 19), lang='ko', en='spake', words=['고하기를']),
    dict(ref=(0, 39, 19), lang='ko', en='unto', words=['자기에게']),
    dict(ref=(0, 39, 19), lang='ko', en='him', words=['자기에게']),
    dict(ref=(0, 39, 19), lang='ko', en='was', words=[]),
    # was 를 떼면서 비게 된 '심히'는 kindled 에 건다 (wrath was kindled = 심히 노한지라)
    dict(ref=(0, 39, 19), lang='ko', en='kindled', words=['심히']),

    # ---- 뚜렷한 짝의 1:1 끊어짐 (여호와·하나님·사람·왕·땅·아들·말씀·백성·자손·
    #      손·집·마음·이름·날·길·물·인자 …) — 한 절에 한 번씩만 나오는 자리만 이었다.
    #      영어가 이미 걸고 있던 한국어는 지키고 더하기만 한다.
    dict(ref=(0, 2, 5), lang='ko', en='Lord', words=['여호와']),   # 창세기 2:5 여호와 / LORD
    dict(ref=(0, 4, 4), lang='ko', en='Lord', words=['여호와께서']),   # 창세기 4:4 여호와 / LORD
    dict(ref=(0, 4, 16), lang='ko', en='Lord', words=['앞을', '여호와의']),   # 창세기 4:16 여호와 / LORD
    dict(ref=(0, 4, 23), lang='ko', en='speech', words=['말을']),   # 창세기 4:23 말 / word
    dict(ref=(0, 5, 29), lang='ko', en='Lord', words=['이', '여호와께서']),   # 창세기 5:29 여호와 / LORD
    dict(ref=(0, 12, 4), lang='ko', en='Lord', words=['여호와의']),   # 창세기 12:4 여호와 / LORD
    dict(ref=(0, 14, 22), lang='ko', en='Lord', words=['여호와께']),   # 창세기 14:22 여호와 / LORD
    dict(ref=(0, 16, 5), lang='ko', en='Lord', words=['여호와께서']),   # 창세기 16:5 여호와 / LORD
    dict(ref=(0, 17, 1), lang='ko', en='Lord', words=['여호와께서']),   # 창세기 17:1 여호와 / LORD
    dict(ref=(0, 19, 22), lang='ko', en='name', words=['불렀더라', '이름을']),   # 창세기 19:22 이름 / name
    dict(ref=(0, 22, 14), lang='ko', en='Lord', words=['땅', '여호와의']),   # 창세기 22:14 여호와 / LORD
    dict(ref=(0, 23, 8), lang='ko', en='saying', words=['가로되', '말을']),   # 창세기 23:8 말 / word
    dict(ref=(0, 23, 13), lang='ko', en='saying', words=['가로되', '말을']),   # 창세기 23:13 말 / word
    dict(ref=(0, 24, 3), lang='ko', en='Lord', words=['여호와를']),   # 창세기 24:3 여호와 / LORD
    dict(ref=(0, 24, 12), lang='ko', en='Lord', words=['주인#1', '여호와여']),   # 창세기 24:12 여호와 / LORD
    dict(ref=(0, 24, 21), lang='ko', en='Lord', words=['알고자', '여호와께서']),   # 창세기 24:21 여호와 / LORD
    dict(ref=(0, 24, 42), lang='ko', en='Lord', words=['주인', '여호와여']),   # 창세기 24:42 여호와 / LORD
    dict(ref=(0, 24, 51), lang='ko', en='Lord', words=['여호와의']),   # 창세기 24:51 여호와 / LORD
    dict(ref=(0, 24, 52), lang='ko', en='Lord', words=['여호와께']),   # 창세기 24:52 여호와 / LORD
    dict(ref=(0, 25, 22), lang='ko', en='Lord', words=['여호와께']),   # 창세기 25:22 여호와 / LORD
    dict(ref=(0, 26, 4), lang='ko', en='earth', words=['천하', '땅을']),   # 창세기 26:4 땅 / land·earth
    dict(ref=(0, 26, 12), lang='ko', en='Lord', words=['여호와께서']),   # 창세기 26:12 여호와 / LORD
    dict(ref=(0, 27, 20), lang='ko', en='Lord', words=['여호와께서']),   # 창세기 27:20 여호와 / LORD
    dict(ref=(0, 27, 27), lang='ko', en='Lord', words=['여호와의']),   # 창세기 27:27 여호와 / LORD
    dict(ref=(0, 28, 21), lang='ko', en='Lord', words=['여호와께서']),   # 창세기 28:21 여호와 / LORD
    dict(ref=(0, 29, 32), lang='ko', en='Lord', words=['여호와께서']),   # 창세기 29:32 여호와 / LORD
    dict(ref=(0, 30, 30), lang='ko', en='Lord', words=['여호와께서']),   # 창세기 30:30 여호와 / LORD
    dict(ref=(0, 31, 1), lang='ko', en='sons', words=['아들들의']),   # 창세기 31:1 아들 / son
    dict(ref=(0, 31, 48), lang='ko', en='name', words=['이름을']),   # 창세기 31:48 이름 / name
    dict(ref=(0, 31, 49), lang='ko', en='Lord', words=['있을', '여호와께서']),   # 창세기 31:49 여호와 / LORD
    dict(ref=(0, 32, 9), lang='ko', en='Lord', words=['여호와여']),   # 창세기 32:9 여호와 / LORD
    dict(ref=(0, 33, 17), lang='ko', en='name', words=['부르더라', '이름을']),   # 창세기 33:17 이름 / name
    dict(ref=(0, 35, 8), lang='ko', en='name', words=['불렀더라', '이름을']),   # 창세기 35:8 이름 / name
    dict(ref=(0, 36, 6), lang='ko', en='house', words=['집의']),   # 창세기 36:6 집 / house
    dict(ref=(0, 36, 10), lang='ko', en='sons', words=['아들은#1', '자손의']),   # 창세기 36:10 자손 / children·seed
    dict(ref=(0, 36, 12), lang='ko', en='sons', words=['자손이며']),   # 창세기 36:12 자손 / children·seed
    dict(ref=(0, 41, 54), lang='ko', en='land', words=['땅에는']),   # 창세기 41:54 땅 / land·earth
    dict(ref=(0, 42, 19), lang='ko', en='men', words=['사람만']),   # 창세기 42:19 사람 / man
    dict(ref=(0, 45, 8), lang='ko', en='house', words=['집의']),   # 창세기 45:8 집 / house
    dict(ref=(0, 47, 12), lang='ko', en='household', words=['식구를', '집에']),   # 창세기 47:12 집 / house
    dict(ref=(0, 47, 20), lang='ko', en='man', words=['사람이']),   # 창세기 47:20 사람 / man
    dict(ref=(0, 49, 4), lang='ko', en='water', words=['물의']),   # 창세기 49:4 물 / water
    dict(ref=(0, 49, 18), lang='ko', en='Lord', words=['여호와여']),   # 창세기 49:18 여호와 / LORD
    dict(ref=(1, 4, 1), lang='ko', en='Lord', words=['여호와께서']),   # 출애굽기 4:1 여호와 / LORD
    dict(ref=(1, 4, 10), lang='ko', en='speech', words=['말에']),   # 출애굽기 4:10 말 / word
    dict(ref=(1, 4, 15), lang='ko', en='words', words=['말을']),   # 출애굽기 4:15 말 / word
    dict(ref=(1, 4, 24), lang='ko', en='way', words=['길의']),   # 출애굽기 4:24 길 / way·path
    dict(ref=(1, 5, 10), lang='ko', en='saying', words=['일러', '말씀에']),   # 출애굽기 5:10 말씀 / word
    dict(ref=(1, 6, 14), lang='ko', en='houses', words=['집의']),   # 출애굽기 6:14 집 / house
    dict(ref=(1, 7, 13), lang='ko', en='Lord', words=['같더라', '여호와의']),   # 출애굽기 7:13 여호와 / LORD
    dict(ref=(1, 7, 18), lang='ko', en='water', words=['물에서는', '물']),   # 출애굽기 7:18 물 / water
    dict(ref=(1, 7, 20), lang='ko', en='Lord', words=['여호와의']),   # 출애굽기 7:20 여호와 / LORD
    dict(ref=(1, 7, 22), lang='ko', en='Lord', words=['아니하니', '여호와의']),   # 출애굽기 7:22 여호와 / LORD
    dict(ref=(1, 8, 15), lang='ko', en='Lord', words=['있음을', '여호와의']),   # 출애굽기 8:15 여호와 / LORD
    dict(ref=(1, 8, 19), lang='ko', en='Lord', words=['같더라', '여호와의']),   # 출애굽기 8:19 여호와 / LORD
    dict(ref=(1, 8, 30), lang='ko', en='Lord', words=['여호와께']),   # 출애굽기 8:30 여호와 / LORD
    dict(ref=(1, 9, 28), lang='ko', en='Lord', words=['여호와께']),   # 출애굽기 9:28 여호와 / LORD
    dict(ref=(1, 9, 30), lang='ko', en='Lord', words=['여호와']),   # 출애굽기 9:30 여호와 / LORD
    dict(ref=(1, 10, 10), lang='ko', en='Lord', words=['여호와를']),   # 출애굽기 10:10 여호와 / LORD
    dict(ref=(1, 10, 16), lang='ko', en='Lord', words=['여호와와']),   # 출애굽기 10:16 여호와 / LORD
    dict(ref=(1, 10, 17), lang='ko', en='Lord', words=['여호와께']),   # 출애굽기 10:17 여호와 / LORD
    dict(ref=(1, 10, 18), lang='ko', en='Lord', words=['여호와께']),   # 출애굽기 10:18 여호와 / LORD
    dict(ref=(1, 11, 7), lang='ko', en='Lord', words=['여호와가']),   # 출애굽기 11:7 여호와 / LORD
    dict(ref=(1, 11, 7), lang='ko', en='man', words=['사람에게나', '사람과']),   # 출애굽기 11:7 사람 / man
    dict(ref=(1, 12, 4), lang='ko', en='man', words=['사람의']),   # 출애굽기 12:4 사람 / man
    dict(ref=(1, 12, 14), lang='ko', en='Lord', words=['여호와의']),   # 출애굽기 12:14 여호와 / LORD
    dict(ref=(1, 12, 25), lang='ko', en='Lord', words=['여호와께서']),   # 출애굽기 12:25 여호와 / LORD
    dict(ref=(1, 12, 41), lang='ko', en='Lord', words=['여호와의']),   # 출애굽기 12:41 여호와 / LORD
    dict(ref=(1, 12, 48), lang='ko', en='Lord', words=['여호와의']),   # 출애굽기 12:48 여호와 / LORD
    dict(ref=(1, 12, 50), lang='ko', en='Lord', words=['같이', '여호와께서']),   # 출애굽기 12:50 여호와 / LORD
    dict(ref=(1, 12, 51), lang='ko', en='Lord', words=['여호와께서']),   # 출애굽기 12:51 여호와 / LORD
    dict(ref=(1, 12, 51), lang='ko', en='children', words=['여호와께서', '자손을']),   # 출애굽기 12:51 자손 / children·seed
    dict(ref=(1, 13, 2), lang='ko', en='children', words=['자손']),   # 출애굽기 13:2 자손 / children·seed
    dict(ref=(1, 13, 3), lang='ko', en='Lord', words=['여호와께서']),   # 출애굽기 13:3 여호와 / LORD
    dict(ref=(1, 13, 5), lang='ko', en='Lord', words=['여호와께서']),   # 출애굽기 13:5 여호와 / LORD
    dict(ref=(1, 13, 8), lang='ko', en='Lord', words=['이', '여호와께서']),   # 출애굽기 13:8 여호와 / LORD
    dict(ref=(1, 13, 11), lang='ko', en='Lord', words=['여호와께서']),   # 출애굽기 13:11 여호와 / LORD
    dict(ref=(1, 13, 14), lang='ko', en='Lord', words=['여호와께서']),   # 출애굽기 13:14 여호와 / LORD
    dict(ref=(1, 14, 25), lang='ko', en='Lord', words=['그', '여호와가']),   # 출애굽기 14:25 여호와 / LORD
    dict(ref=(1, 15, 1), lang='ko', en='saying', words=['일렀으되', '말과']),   # 출애굽기 15:1 말 / word
    dict(ref=(1, 15, 16), lang='ko', en='Lord', words=['같이', '여호와여']),   # 출애굽기 15:16 여호와 / LORD
    dict(ref=(1, 16, 3), lang='ko', en='Lord', words=['주려', '여호와의']),   # 출애굽기 16:3 여호와 / LORD
    dict(ref=(1, 16, 4), lang='ko', en='Lord', words=['여호와께서']),   # 출애굽기 16:4 여호와 / LORD
    dict(ref=(1, 16, 10), lang='ko', en='Lord', words=['여호와의']),   # 출애굽기 16:10 여호와 / LORD
    dict(ref=(1, 16, 15), lang='ko', en='Lord', words=['알지', '여호와께서']),   # 출애굽기 16:15 여호와 / LORD
    dict(ref=(1, 16, 34), lang='ko', en='Lord', words=['여호와께서']),   # 출애굽기 16:34 여호와 / LORD
    dict(ref=(1, 17, 2), lang='ko', en='Lord', words=['여호와를']),   # 출애굽기 17:2 여호와 / LORD
    dict(ref=(1, 19, 3), lang='ko', en='children', words=['자손에게']),   # 출애굽기 19:3 자손 / children·seed
    dict(ref=(1, 19, 6), lang='ko', en='words', words=['말을']),   # 출애굽기 19:6 말 / word
    dict(ref=(1, 19, 8), lang='ko', en='words', words=['말로']),   # 출애굽기 19:8 말 / word
    dict(ref=(1, 19, 9), lang='ko', en='words', words=['말로']),   # 출애굽기 19:9 말 / word
    dict(ref=(1, 19, 18), lang='ko', en='Lord', words=['여호와께서']),   # 출애굽기 19:18 여호와 / LORD
    dict(ref=(1, 23, 17), lang='ko', en='Lord', words=['주', '여호와께']),   # 출애굽기 23:17 여호와 / LORD
    dict(ref=(1, 24, 2), lang='ko', en='Lord', words=['여호와에게']),   # 출애굽기 24:2 여호와 / LORD
    dict(ref=(1, 24, 7), lang='ko', en='Lord', words=['말씀을', '여호와의']),   # 출애굽기 24:7 여호와 / LORD
    dict(ref=(1, 29, 28), lang='ko', en='Lord', words=['여호와께']),   # 출애굽기 29:28 여호와 / LORD
    dict(ref=(1, 30, 12), lang='ko', en='man', words=['계수할', '사람은']),   # 출애굽기 30:12 사람 / man
    dict(ref=(1, 30, 13), lang='ko', en='Lord', words=['여호와께']),   # 출애굽기 30:13 여호와 / LORD
    dict(ref=(1, 30, 15), lang='ko', en='Lord', words=['여호와께']),   # 출애굽기 30:15 여호와 / LORD
    dict(ref=(1, 30, 16), lang='ko', en='Lord', words=['되어서', '여호와']),   # 출애굽기 30:16 여호와 / LORD
    dict(ref=(1, 30, 37), lang='ko', en='Lord', words=['여호와를']),   # 출애굽기 30:37 여호와 / LORD
    dict(ref=(1, 30, 38), lang='ko', en='people', words=['백성']),   # 출애굽기 30:38 백성 / people
    dict(ref=(1, 32, 7), lang='ko', en='Lord', words=['여호와께서']),   # 출애굽기 32:7 여호와 / LORD
    dict(ref=(1, 32, 26), lang='ko', en='Lord', words=['여호와의']),   # 출애굽기 32:26 여호와 / LORD
    dict(ref=(1, 32, 29), lang='ko', en='Lord', words=['여호와께']),   # 출애굽기 32:29 여호와 / LORD
    dict(ref=(1, 33, 1), lang='ko', en='Lord', words=['여호와께서']),   # 출애굽기 33:1 여호와 / LORD
    dict(ref=(1, 33, 5), lang='ko', en='children', words=['자손에게']),   # 출애굽기 33:5 자손 / children·seed
    dict(ref=(1, 33, 7), lang='ko', en='Lord', words=['다', '여호와를']),   # 출애굽기 33:7 여호와 / LORD
    dict(ref=(1, 34, 4), lang='ko', en='Lord', words=['여호와의']),   # 출애굽기 34:4 여호와 / LORD
    dict(ref=(1, 34, 23), lang='ko', en='Lord', words=['주', '여호와']),   # 출애굽기 34:23 여호와 / LORD
    dict(ref=(1, 34, 32), lang='ko', en='Lord', words=['여호와께서']),   # 출애굽기 34:32 여호와 / LORD
    dict(ref=(1, 35, 24), lang='ko', en='Lord', words=['무릇#1', '여호와께']),   # 출애굽기 35:24 여호와 / LORD
    dict(ref=(1, 36, 2), lang='ko', en='Lord', words=['여호와께로']),   # 출애굽기 36:2 여호와 / LORD
    dict(ref=(1, 39, 21), lang='ko', en='Lord', words=['여호와께서']),   # 출애굽기 39:21 여호와 / LORD
    dict(ref=(1, 39, 43), lang='ko', en='Lord', words=['여호와께서']),   # 출애굽기 39:43 여호와 / LORD
    dict(ref=(1, 40, 19), lang='ko', en='Lord', words=['여호와께서']),   # 출애굽기 40:19 여호와 / LORD
    dict(ref=(1, 40, 29), lang='ko', en='Lord', words=['여호와께서']),   # 출애굽기 40:29 여호와 / LORD
    dict(ref=(1, 40, 32), lang='ko', en='Lord', words=['여호와께서']),   # 출애굽기 40:32 여호와 / LORD
    dict(ref=(2, 1, 2), lang='ko', en='Lord', words=['여호와께']),   # 레위기 1:2 여호와 / LORD
    dict(ref=(2, 1, 5), lang='ko', en='Lord', words=['자손', '여호와']),   # 레위기 1:5 여호와 / LORD
    dict(ref=(2, 1, 13), lang='ko', en='Lord', words=['여호와께']),   # 레위기 1:13 여호와 / LORD
    dict(ref=(2, 2, 3), lang='ko', en='Lord', words=['여호와의']),   # 레위기 2:3 여호와 / LORD
    dict(ref=(2, 2, 10), lang='ko', en='Lord', words=['여호와의']),   # 레위기 2:10 여호와 / LORD
    dict(ref=(2, 3, 7), lang='ko', en='Lord', words=['여호와']),   # 레위기 3:7 여호와 / LORD
    dict(ref=(2, 3, 12), lang='ko', en='Lord', words=['여호와']),   # 레위기 3:12 여호와 / LORD
    dict(ref=(2, 3, 16), lang='ko', en='Lord', words=['여호와의']),   # 레위기 3:16 여호와 / LORD
    dict(ref=(2, 4, 2), lang='ko', en='Lord', words=['여호와의']),   # 레위기 4:2 여호와 / LORD
    dict(ref=(2, 4, 3), lang='ko', en='Lord', words=['여호와께']),   # 레위기 4:3 여호와 / LORD
    dict(ref=(2, 4, 22), lang='ko', en='Lord', words=['여호와의']),   # 레위기 4:22 여호와 / LORD
    dict(ref=(2, 5, 7), lang='ko', en='Lord', words=['여호와께로']),   # 레위기 5:7 여호와 / LORD
    dict(ref=(2, 5, 17), lang='ko', en='Lord', words=['여호와의']),   # 레위기 5:17 여호와 / LORD
    dict(ref=(2, 6, 7), lang='ko', en='Lord', words=['여호와']),   # 레위기 6:7 여호와 / LORD
    dict(ref=(2, 6, 15), lang='ko', en='Lord', words=['여호와']),   # 레위기 6:15 여호와 / LORD
    dict(ref=(2, 7, 14), lang='ko', en='Lord', words=['여호와께']),   # 레위기 7:14 여호와 / LORD
    dict(ref=(2, 7, 20), lang='ko', en='Lord', words=['여호와께']),   # 레위기 7:20 여호와 / LORD
    dict(ref=(2, 7, 20), lang='ko', en='people', words=['여호와께', '백성']),   # 레위기 7:20 백성 / people
    dict(ref=(2, 7, 21), lang='ko', en='Lord', words=['여호와께']),   # 레위기 7:21 여호와 / LORD
    dict(ref=(2, 7, 23), lang='ko', en='saying', words=['말']),   # 레위기 7:23 말 / word
    dict(ref=(2, 7, 25), lang='ko', en='Lord', words=['여호와께']),   # 레위기 7:25 여호와 / LORD
    dict(ref=(2, 7, 25), lang='ko', en='people', words=['백성']),   # 레위기 7:25 백성 / people
    dict(ref=(2, 8, 9), lang='ko', en='Lord', words=['여호와께서']),   # 레위기 8:9 여호와 / LORD
    dict(ref=(2, 8, 13), lang='ko', en='Lord', words=['같았더라', '여호와께서']),   # 레위기 8:13 여호와 / LORD
    dict(ref=(2, 8, 27), lang='ko', en='Lord', words=['여호와']),   # 레위기 8:27 여호와 / LORD
    dict(ref=(2, 8, 28), lang='ko', en='Lord', words=['여호와께']),   # 레위기 8:28 여호와 / LORD
    dict(ref=(2, 8, 34), lang='ko', en='Lord', words=['여호와께서']),   # 레위기 8:34 여호와 / LORD
    dict(ref=(2, 9, 3), lang='ko', en='children', words=['자손에게']),   # 레위기 9:3 자손 / children·seed
    dict(ref=(2, 9, 7), lang='ko', en='Lord', words=['여호와의']),   # 레위기 9:7 여호와 / LORD
    dict(ref=(2, 9, 10), lang='ko', en='Lord', words=['같았고', '여호와께서']),   # 레위기 9:10 여호와 / LORD
    dict(ref=(2, 10, 3), lang='ko', en='saying', words=['하는', '말씀이라']),   # 레위기 10:3 말씀 / word
    dict(ref=(2, 10, 13), lang='ko', en='Lord', words=['여호와의']),   # 레위기 10:13 여호와 / LORD
    dict(ref=(2, 14, 11), lang='ko', en='Lord', words=['그', '여호와']),   # 레위기 14:11 여호와 / LORD
    dict(ref=(2, 14, 18), lang='ko', en='Lord', words=['여호와']),   # 레위기 14:18 여호와 / LORD
    dict(ref=(2, 14, 31), lang='ko', en='Lord', words=['여호와']),   # 레위기 14:31 여호와 / LORD
    dict(ref=(2, 16, 30), lang='ko', en='Lord', words=['이', '여호와']),   # 레위기 16:30 여호와 / LORD
    dict(ref=(2, 17, 3), lang='ko', en='house', words=['집의']),   # 레위기 17:3 집 / house
    dict(ref=(2, 17, 10), lang='ko', en='man', words=['사람이나', '사람에게']),   # 레위기 17:10 사람 / man
    dict(ref=(2, 19, 4), lang='ko', en='God', words=['하나님']),   # 레위기 19:4 하나님 / God
    dict(ref=(2, 19, 8), lang='ko', en='Lord', words=['여호와의']),   # 레위기 19:8 여호와 / LORD
    dict(ref=(2, 19, 8), lang='ko', en='people', words=['여호와의', '백성']),   # 레위기 19:8 백성 / people
    dict(ref=(2, 20, 22), lang='ko', en='land', words=['땅이']),   # 레위기 20:22 땅 / land·earth
    dict(ref=(2, 21, 21), lang='ko', en='Lord', words=['여호와의']),   # 레위기 21:21 여호와 / LORD
    dict(ref=(2, 22, 24), lang='ko', en='Lord', words=['여호와께']),   # 레위기 22:24 여호와 / LORD
    dict(ref=(2, 22, 27), lang='ko', en='Lord', words=['나거든', '여호와께']),   # 레위기 22:27 여호와 / LORD
    dict(ref=(2, 22, 29), lang='ko', en='Lord', words=['여호와께']),   # 레위기 22:29 여호와 / LORD
    dict(ref=(2, 23, 5), lang='ko', en='Lord', words=['여호와의']),   # 레위기 23:5 여호와 / LORD
    dict(ref=(2, 23, 8), lang='ko', en='Lord', words=['여호와께']),   # 레위기 23:8 여호와 / LORD
    dict(ref=(2, 23, 13), lang='ko', en='Lord', words=['그', '여호와께']),   # 레위기 23:13 여호와 / LORD
    dict(ref=(2, 23, 16), lang='ko', en='Lord', words=['여호와께']),   # 레위기 23:16 여호와 / LORD
    dict(ref=(2, 23, 24), lang='ko', en='day', words=['날이요']),   # 레위기 23:24 날 / day
    dict(ref=(2, 23, 25), lang='ko', en='Lord', words=['여호와께']),   # 레위기 23:25 여호와 / LORD
    dict(ref=(2, 23, 27), lang='ko', en='Lord', words=['여호와께']),   # 레위기 23:27 여호와 / LORD
    dict(ref=(2, 23, 28), lang='ko', en='Lord', words=['여호와']),   # 레위기 23:28 여호와 / LORD
    dict(ref=(2, 23, 29), lang='ko', en='people', words=['백성']),   # 레위기 23:29 백성 / people
    dict(ref=(2, 23, 44), lang='ko', en='Lord', words=['여호와의']),   # 레위기 23:44 여호와 / LORD
    dict(ref=(2, 23, 44), lang='ko', en='children', words=['여호와의', '자손에게']),   # 레위기 23:44 자손 / children·seed
    dict(ref=(2, 24, 6), lang='ko', en='Lord', words=['여호와']),   # 레위기 24:6 여호와 / LORD
    dict(ref=(2, 24, 7), lang='ko', en='Lord', words=['여호와께']),   # 레위기 24:7 여호와 / LORD
    dict(ref=(2, 24, 8), lang='ko', en='Lord', words=['여호와']),   # 레위기 24:8 여호와 / LORD
    dict(ref=(2, 24, 9), lang='ko', en='Lord', words=['여호와의']),   # 레위기 24:9 여호와 / LORD
    dict(ref=(2, 24, 10), lang='ko', en='man', words=['사람된', '자가', '사람과']),   # 레위기 24:10 사람 / man
    dict(ref=(2, 25, 2), lang='ko', en='Lord', words=['여호와']),   # 레위기 25:2 여호와 / LORD
    dict(ref=(2, 25, 4), lang='ko', en='Lord', words=['여호와께']),   # 레위기 25:4 여호와 / LORD
    dict(ref=(2, 27, 14), lang='ko', en='Lord', words=['여호와께']),   # 레위기 27:14 여호와 / LORD
    dict(ref=(2, 27, 21), lang='ko', en='Lord', words=['여호와께']),   # 레위기 27:21 여호와 / LORD
    dict(ref=(2, 27, 23), lang='ko', en='Lord', words=['여호와께']),   # 레위기 27:23 여호와 / LORD
    dict(ref=(3, 1, 19), lang='ko', en='Lord', words=['여호와께서']),   # 민수기 1:19 여호와 / LORD
    dict(ref=(3, 2, 14), lang='ko', en='sons', words=['아들', '자손의']),   # 민수기 2:14 자손 / children·seed
    dict(ref=(3, 2, 17), lang='ko', en='man', words=['따라', '사람은']),   # 민수기 2:17 사람 / man
    dict(ref=(3, 2, 18), lang='ko', en='sons', words=['자손의']),   # 민수기 2:18 자손 / children·seed
    dict(ref=(3, 2, 22), lang='ko', en='sons', words=['아들', '자손의']),   # 민수기 2:22 자손 / children·seed
    dict(ref=(3, 3, 42), lang='ko', en='Lord', words=['여호와께서']),   # 민수기 3:42 여호와 / LORD
    dict(ref=(3, 3, 42), lang='ko', en='children', words=['모든', '자손']),   # 민수기 3:42 자손 / children·seed
    dict(ref=(3, 4, 28), lang='ko', en='sons', words=['아들', '자손의']),   # 민수기 4:28 자손 / children·seed
    dict(ref=(3, 4, 33), lang='ko', en='sons', words=['아들', '자손의']),   # 민수기 4:33 자손 / children·seed
    dict(ref=(3, 5, 4), lang='ko', en='Lord', words=['그같이', '여호와께서']),   # 민수기 5:4 여호와 / LORD
    dict(ref=(3, 5, 8), lang='ko', en='Lord', words=['여호와께']),   # 민수기 5:8 여호와 / LORD
    dict(ref=(3, 5, 19), lang='ko', en='water', words=['물의']),   # 민수기 5:19 물 / water
    dict(ref=(3, 5, 25), lang='ko', en='Lord', words=['여호와']),   # 민수기 5:25 여호와 / LORD
    dict(ref=(3, 5, 30), lang='ko', en='Lord', words=['여호와']),   # 민수기 5:30 여호와 / LORD
    dict(ref=(3, 6, 2), lang='ko', en='Lord', words=['여호와께']),   # 민수기 6:2 여호와 / LORD
    dict(ref=(3, 8, 13), lang='ko', en='Lord', words=['여호와께']),   # 민수기 8:13 여호와 / LORD
    dict(ref=(3, 8, 18), lang='ko', en='children', words=['중', '자손']),   # 민수기 8:18 자손 / children·seed
    dict(ref=(3, 9, 13), lang='ko', en='Lord', words=['여호와께']),   # 민수기 9:13 여호와 / LORD
    dict(ref=(3, 9, 22), lang='ko', en='children', words=['자손이']),   # 민수기 9:22 자손 / children·seed
    dict(ref=(3, 11, 3), lang='ko', en='Lord', words=['여호와의']),   # 민수기 11:3 여호와 / LORD
    dict(ref=(3, 11, 18), lang='ko', en='saying', words=['말이']),   # 민수기 11:18 말 / word
    dict(ref=(3, 12, 4), lang='ko', en='Lord', words=['여호와께서']),   # 민수기 12:4 여호와 / LORD
    dict(ref=(3, 12, 6), lang='ko', en='words', words=['말을']),   # 민수기 12:6 말 / word
    dict(ref=(3, 13, 2), lang='ko', en='children', words=['자손에게']),   # 민수기 13:2 자손 / children·seed
    dict(ref=(3, 14, 10), lang='ko', en='Lord', words=['여호와의']),   # 민수기 14:10 여호와 / LORD
    dict(ref=(3, 14, 37), lang='ko', en='Lord', words=['여호와']),   # 민수기 14:37 여호와 / LORD
    dict(ref=(3, 14, 38), lang='ko', en='men', words=['사람들']),   # 민수기 14:38 사람 / man
    dict(ref=(3, 14, 39), lang='ko', en='sayings', words=['말로']),   # 민수기 14:39 말 / word
    dict(ref=(3, 14, 39), lang='ko', en='children', words=['말로', '자손에게']),   # 민수기 14:39 자손 / children·seed
    dict(ref=(3, 14, 40), lang='ko', en='Lord', words=['여호와의']),   # 민수기 14:40 여호와 / LORD
    dict(ref=(3, 14, 41), lang='ko', en='Lord', words=['이', '여호와의']),   # 민수기 14:41 여호와 / LORD
    dict(ref=(3, 15, 8), lang='ko', en='Lord', words=['여호와께']),   # 민수기 15:8 여호와 / LORD
    dict(ref=(3, 15, 14), lang='ko', en='Lord', words=['여호와께']),   # 민수기 15:14 여호와 / LORD
    dict(ref=(3, 15, 15), lang='ko', en='Lord', words=['여호와']),   # 민수기 15:15 여호와 / LORD
    dict(ref=(3, 15, 21), lang='ko', en='Lord', words=['여호와께']),   # 민수기 15:21 여호와 / LORD
    dict(ref=(3, 15, 24), lang='ko', en='Lord', words=['여호와께']),   # 민수기 15:24 여호와 / LORD
    dict(ref=(3, 15, 30), lang='ko', en='Lord', words=['여호와를']),   # 민수기 15:30 여호와 / LORD
    dict(ref=(3, 15, 31), lang='ko', en='Lord', words=['여호와의']),   # 민수기 15:31 여호와 / LORD
    dict(ref=(3, 15, 39), lang='ko', en='Lord', words=['여호와의']),   # 민수기 15:39 여호와 / LORD
    dict(ref=(3, 16, 5), lang='ko', en='Lord', words=['여호와께서']),   # 민수기 16:5 여호와 / LORD
    dict(ref=(3, 16, 11), lang='ko', en='Lord', words=['여호와를']),   # 민수기 16:11 여호와 / LORD
    dict(ref=(3, 16, 14), lang='ko', en='land', words=['땅으로']),   # 민수기 16:14 땅 / land·earth
    dict(ref=(3, 16, 29), lang='ko', en='Lord', words=['여호와께서']),   # 민수기 16:29 여호와 / LORD
    dict(ref=(3, 16, 31), lang='ko', en='words', words=['말을']),   # 민수기 16:31 말 / word
    dict(ref=(3, 16, 42), lang='ko', en='Lord', words=['여호와의']),   # 민수기 16:42 여호와 / LORD
    dict(ref=(3, 16, 46), lang='ko', en='Lord', words=['여호와께서']),   # 민수기 16:46 여호와 / LORD
    dict(ref=(3, 17, 11), lang='ko', en='Lord', words=['그같이', '여호와께서']),   # 민수기 17:11 여호와 / LORD
    dict(ref=(3, 18, 8), lang='ko', en='sons', words=['아들들에게']),   # 민수기 18:8 아들 / son
    dict(ref=(3, 18, 11), lang='ko', en='house', words=['집의']),   # 민수기 18:11 집 / house
    dict(ref=(3, 18, 12), lang='ko', en='Lord', words=['주었은즉', '여호와께']),   # 민수기 18:12 여호와 / LORD
    dict(ref=(3, 18, 20), lang='ko', en='Lord', words=['여호와께서']),   # 민수기 18:20 여호와 / LORD
    dict(ref=(3, 18, 24), lang='ko', en='Lord', words=['여호와께']),   # 민수기 18:24 여호와 / LORD
    dict(ref=(3, 18, 26), lang='ko', en='Lord', words=['내가', '여호와께']),   # 민수기 18:26 여호와 / LORD
    dict(ref=(3, 19, 13), lang='ko', en='Lord', words=['여호와의']),   # 민수기 19:13 여호와 / LORD
    dict(ref=(3, 19, 20), lang='ko', en='Lord', words=['여호와의']),   # 민수기 19:20 여호와 / LORD
    dict(ref=(3, 20, 3), lang='ko', en='Lord', words=['여호와']),   # 민수기 20:3 여호와 / LORD
    dict(ref=(3, 20, 12), lang='ko', en='Lord', words=['여호와께서']),   # 민수기 20:12 여호와 / LORD
    dict(ref=(3, 20, 12), lang='ko', en='children', words=['여호와께서', '자손의']),   # 민수기 20:12 자손 / children·seed
    dict(ref=(3, 20, 27), lang='ko', en='Lord', words=['여호와의']),   # 민수기 20:27 여호와 / LORD
    dict(ref=(3, 21, 2), lang='ko', en='Lord', words=['여호와께']),   # 민수기 21:2 여호와 / LORD
    dict(ref=(3, 22, 18), lang='ko', en='Lord', words=['여호와']),   # 민수기 22:18 여호와 / LORD
    dict(ref=(3, 22, 19), lang='ko', en='Lord', words=['이', '여호와께서']),   # 민수기 22:19 여호와 / LORD
    dict(ref=(3, 22, 20), lang='ko', en='word', words=['말만']),   # 민수기 22:20 말 / word
    dict(ref=(3, 22, 35), lang='ko', en='word', words=['말만']),   # 민수기 22:35 말 / word
    dict(ref=(3, 23, 3), lang='ko', en='Lord', words=['여호와께서']),   # 민수기 23:3 여호와 / LORD
    dict(ref=(3, 23, 8), lang='ko', en='Lord', words=['여호와께서']),   # 민수기 23:8 여호와 / LORD
    dict(ref=(3, 23, 19), lang='ko', en='son', words=['인자가']),   # 민수기 23:19 인자 / son of man
    dict(ref=(3, 24, 6), lang='ko', en='Lord', words=['여호와의']),   # 민수기 24:6 여호와 / LORD
    dict(ref=(3, 24, 11), lang='ko', en='Lord', words=['여호와가']),   # 민수기 24:11 여호와 / LORD
    dict(ref=(3, 25, 15), lang='ko', en='people', words=['백성']),   # 민수기 25:15 백성 / people
    dict(ref=(3, 27, 23), lang='ko', en='Lord', words=['여호와께서']),   # 민수기 27:23 여호와 / LORD
    dict(ref=(3, 28, 7), lang='ko', en='Lord', words=['그', '여호와께']),   # 민수기 28:7 여호와 / LORD
    dict(ref=(3, 28, 8), lang='ko', en='Lord', words=['같이', '여호와께']),   # 민수기 28:8 여호와 / LORD
    dict(ref=(3, 28, 24), lang='ko', en='Lord', words=['여호와께']),   # 민수기 28:24 여호와 / LORD
    dict(ref=(3, 29, 6), lang='ko', en='Lord', words=['여호와께']),   # 민수기 29:6 여호와 / LORD
    dict(ref=(3, 29, 12), lang='ko', en='Lord', words=['여호와']),   # 민수기 29:12 여호와 / LORD
    dict(ref=(3, 30, 5), lang='ko', en='Lord', words=['여호와께서']),   # 민수기 30:5 여호와 / LORD
    dict(ref=(3, 30, 8), lang='ko', en='Lord', words=['여호와께서']),   # 민수기 30:8 여호와 / LORD
    dict(ref=(3, 31, 3), lang='ko', en='Lord', words=['여호와의']),   # 민수기 31:3 여호와 / LORD
    dict(ref=(3, 31, 7), lang='ko', en='Lord', words=['여호와께서']),   # 민수기 31:7 여호와 / LORD
    dict(ref=(3, 31, 38), lang='ko', en='Lord', words=['여호와께']),   # 민수기 31:38 여호와 / LORD
    dict(ref=(3, 32, 20), lang='ko', en='Lord', words=['여호와']),   # 민수기 32:20 여호와 / LORD
    dict(ref=(3, 32, 23), lang='ko', en='Lord', words=['여호와께']),   # 민수기 32:23 여호와 / LORD
    dict(ref=(3, 32, 31), lang='ko', en='Lord', words=['대로', '여호와께서']),   # 민수기 32:31 여호와 / LORD
    dict(ref=(3, 33, 38), lang='ko', en='Lord', words=['여호와의']),   # 민수기 33:38 여호와 / LORD
    dict(ref=(3, 33, 38), lang='ko', en='children', words=['여호와의', '자손이']),   # 민수기 33:38 자손 / children·seed
    dict(ref=(3, 34, 29), lang='ko', en='Lord', words=['여호와께서']),   # 민수기 34:29 여호와 / LORD
    dict(ref=(3, 34, 29), lang='ko', en='children', words=['여호와께서', '자손에게']),   # 민수기 34:29 자손 / children·seed
    dict(ref=(3, 36, 10), lang='ko', en='Lord', words=['여호와께서']),   # 민수기 36:10 여호와 / LORD
    dict(ref=(3, 36, 12), lang='ko', en='sons', words=['아들', '자손의']),   # 민수기 36:12 자손 / children·seed
    dict(ref=(4, 1, 19), lang='ko', en='Lord', words=['여호와께서']),   # 신명기 1:19 여호와 / LORD
    dict(ref=(4, 1, 32), lang='ko', en='Lord', words=['여호와를']),   # 신명기 1:32 여호와 / LORD
    dict(ref=(4, 1, 36), lang='ko', en='Lord', words=['여호와를']),   # 신명기 1:36 여호와 / LORD
    dict(ref=(4, 2, 1), lang='ko', en='Lord', words=['대로', '여호와께서']),   # 신명기 2:1 여호와 / LORD
    dict(ref=(4, 2, 12), lang='ko', en='Lord', words=['여호와의']),   # 신명기 2:12 여호와 / LORD
    dict(ref=(4, 2, 14), lang='ko', en='Lord', words=['대로', '여호와께서']),   # 신명기 2:14 여호와 / LORD
    dict(ref=(4, 2, 21), lang='ko', en='Lord', words=['같이', '여호와께서']),   # 신명기 2:21 여호와 / LORD
    dict(ref=(4, 3, 23), lang='ko', en='Lord', words=['여호와께']),   # 신명기 3:23 여호와 / LORD
    dict(ref=(4, 4, 5), lang='ko', en='Lord', words=['여호와의']),   # 신명기 4:5 여호와 / LORD
    dict(ref=(4, 4, 7), lang='ko', en='Lord', words=['여호와께서']),   # 신명기 4:7 여호와 / LORD
    dict(ref=(4, 4, 15), lang='ko', en='Lord', words=['여호와께서']),   # 신명기 4:15 여호와 / LORD
    dict(ref=(4, 4, 25), lang='ko', en='Lord', words=['여호와']),   # 신명기 4:25 여호와 / LORD
    dict(ref=(4, 4, 30), lang='ko', en='Lord', words=['여호와께로']),   # 신명기 4:30 여호와 / LORD
    dict(ref=(4, 4, 34), lang='ko', en='Lord', words=['여호와께서']),   # 신명기 4:34 여호와 / LORD
    dict(ref=(4, 4, 39), lang='ko', en='Lord', words=['여호와는']),   # 신명기 4:39 여호와 / LORD
    dict(ref=(4, 5, 12), lang='ko', en='Lord', words=['여호와']),   # 신명기 5:12 여호와 / LORD
    dict(ref=(4, 5, 25), lang='ko', en='Lord', words=['여호와의']),   # 신명기 5:25 여호와 / LORD
    dict(ref=(4, 5, 32), lang='ko', en='Lord', words=['여호와께서']),   # 신명기 5:32 여호와 / LORD
    dict(ref=(4, 6, 3), lang='ko', en='Lord', words=['같이', '여호와께서']),   # 신명기 6:3 여호와 / LORD
    dict(ref=(4, 6, 10), lang='ko', en='Lord', words=['여호와께서']),   # 신명기 6:10 여호와 / LORD
    dict(ref=(4, 6, 12), lang='ko', en='Lord', words=['너는', '여호와를']),   # 신명기 6:12 여호와 / LORD
    dict(ref=(4, 6, 20), lang='ko', en='Lord', words=['여호와의']),   # 신명기 6:20 여호와 / LORD
    dict(ref=(4, 6, 21), lang='ko', en='Lord', words=['여호와께서']),   # 신명기 6:21 여호와 / LORD
    dict(ref=(4, 6, 22), lang='ko', en='Lord', words=['여호와께서']),   # 신명기 6:22 여호와 / LORD
    dict(ref=(4, 6, 25), lang='ko', en='Lord', words=['여호와']),   # 신명기 6:25 여호와 / LORD
    dict(ref=(4, 7, 1), lang='ko', en='Lord', words=['여호와께서']),   # 신명기 7:1 여호와 / LORD
    dict(ref=(4, 7, 9), lang='ko', en='Lord', words=['여호와는']),   # 신명기 7:9 여호와 / LORD
    dict(ref=(4, 7, 21), lang='ko', en='Lord', words=['여호와']),   # 신명기 7:21 여호와 / LORD
    dict(ref=(4, 7, 25), lang='ko', en='God', words=['하나님']),   # 신명기 7:25 하나님 / God
    dict(ref=(4, 8, 3), lang='ko', en='Lord', words=['여호와의']),   # 신명기 8:3 여호와 / LORD
    dict(ref=(4, 8, 5), lang='ko', en='Lord', words=['같이', '여호와께서']),   # 신명기 8:5 여호와 / LORD
    dict(ref=(4, 8, 18), lang='ko', en='Lord', words=['여호와를']),   # 신명기 8:18 여호와 / LORD
    dict(ref=(4, 9, 6), lang='ko', en='Lord', words=['여호와께서']),   # 신명기 9:6 여호와 / LORD
    dict(ref=(4, 9, 23), lang='ko', en='saying', words=['이르시를', '말씀을']),   # 신명기 9:23 말씀 / word
    dict(ref=(4, 9, 28), lang='ko', en='Lord', words=['여호와께서']),   # 신명기 9:28 여호와 / LORD
    dict(ref=(4, 10, 14), lang='ko', en='Lord', words=['여호와께']),   # 신명기 10:14 여호와 / LORD
    dict(ref=(4, 11, 6), lang='ko', en='sons', words=['아들', '자손']),   # 신명기 11:6 자손 / children·seed
    dict(ref=(4, 11, 23), lang='ko', en='Lord', words=['여호와께서']),   # 신명기 11:23 여호와 / LORD
    dict(ref=(4, 11, 28), lang='ko', en='Lord', words=['여호와의']),   # 신명기 11:28 여호와 / LORD
    dict(ref=(4, 11, 29), lang='ko', en='Lord', words=['여호와께서']),   # 신명기 11:29 여호와 / LORD
    dict(ref=(4, 11, 29), lang='ko', en='land', words=['땅으로']),   # 신명기 11:29 땅 / land·earth
    dict(ref=(4, 12, 5), lang='ko', en='Lord', words=['여호와께서']),   # 신명기 12:5 여호와 / LORD
    dict(ref=(4, 12, 20), lang='ko', en='Lord', words=['여호와께서']),   # 신명기 12:20 여호와 / LORD
    dict(ref=(4, 12, 25), lang='ko', en='Lord', words=['여호와께서']),   # 신명기 12:25 여호와 / LORD
    dict(ref=(4, 12, 26), lang='ko', en='Lord', words=['여호와께서']),   # 신명기 12:26 여호와 / LORD
    dict(ref=(4, 12, 29), lang='ko', en='Lord', words=['여호와께서']),   # 신명기 12:29 여호와 / LORD
    dict(ref=(4, 13, 10), lang='ko', en='Lord', words=['여호와에게서']),   # 신명기 13:10 여호와 / LORD
    dict(ref=(4, 14, 25), lang='ko', en='Lord', words=['여호와의']),   # 신명기 14:25 여호와 / LORD
    dict(ref=(4, 14, 29), lang='ko', en='Lord', words=['여호와께서']),   # 신명기 14:29 여호와 / LORD
    dict(ref=(4, 15, 2), lang='ko', en='Lord', words=['여호와의']),   # 신명기 15:2 여호와 / LORD
    dict(ref=(4, 15, 9), lang='ko', en='Lord', words=['너는', '여호와께']),   # 신명기 15:9 여호와 / LORD
    dict(ref=(4, 15, 10), lang='ko', en='Lord', words=['여호와께서']),   # 신명기 15:10 여호와 / LORD
    dict(ref=(4, 15, 21), lang='ko', en='Lord', words=['여호와께']),   # 신명기 15:21 여호와 / LORD
    dict(ref=(4, 17, 8), lang='ko', en='Lord', words=['여호와의']),   # 신명기 17:8 여호와 / LORD
    dict(ref=(4, 17, 10), lang='ko', en='Lord', words=['여호와께서']),   # 신명기 17:10 여호와 / LORD
    dict(ref=(4, 17, 14), lang='ko', en='Lord', words=['여호와께서']),   # 신명기 17:14 여호와 / LORD
    dict(ref=(4, 18, 1), lang='ko', en='Lord', words=['것이라', '여호와의']),   # 신명기 18:1 여호와 / LORD
    dict(ref=(4, 18, 2), lang='ko', en='Lord', words=['여호와께서']),   # 신명기 18:2 여호와 / LORD
    dict(ref=(4, 18, 9), lang='ko', en='Lord', words=['여호와께서']),   # 신명기 18:9 여호와 / LORD
    dict(ref=(4, 18, 14), lang='ko', en='Lord', words=['여호와께서']),   # 신명기 18:14 여호와 / LORD
    dict(ref=(4, 18, 15), lang='ko', en='Lord', words=['여호와께서']),   # 신명기 18:15 여호와 / LORD
    dict(ref=(4, 18, 18), lang='ko', en='words', words=['말을']),   # 신명기 18:18 말 / word
    dict(ref=(4, 18, 19), lang='ko', en='words', words=['말을']),   # 신명기 18:19 말 / word
    dict(ref=(4, 18, 20), lang='ko', en='word', words=['말을']),   # 신명기 18:20 말 / word
    dict(ref=(4, 18, 21), lang='ko', en='word', words=['말이']),   # 신명기 18:21 말 / word
    dict(ref=(4, 19, 9), lang='ko', en='Lord', words=['여호와를']),   # 신명기 19:9 여호와 / LORD
    dict(ref=(4, 20, 1), lang='ko', en='Lord', words=['여호와께서']),   # 신명기 20:1 여호와 / LORD
    dict(ref=(4, 20, 14), lang='ko', en='Lord', words=['여호와께서']),   # 신명기 20:14 여호와 / LORD
    dict(ref=(4, 20, 17), lang='ko', en='Lord', words=['여호와께서']),   # 신명기 20:17 여호와 / LORD
    dict(ref=(4, 20, 18), lang='ko', en='Lord', words=['여호와께']),   # 신명기 20:18 여호와 / LORD
    dict(ref=(4, 20, 18), lang='ko', en='God', words=['하나님']),   # 신명기 20:18 하나님 / God
    dict(ref=(4, 21, 8), lang='ko', en='Lord', words=['여호와여']),   # 신명기 21:8 여호와 / LORD
    dict(ref=(4, 21, 9), lang='ko', en='Lord', words=['이와', '여호와의']),   # 신명기 21:9 여호와 / LORD
    dict(ref=(4, 21, 10), lang='ko', en='Lord', words=['여호와께서']),   # 신명기 21:10 여호와 / LORD
    dict(ref=(4, 21, 15), lang='ko', en='son', words=['아들을']),   # 신명기 21:15 아들 / son
    dict(ref=(4, 22, 26), lang='ko', en='man', words=['사람이']),   # 신명기 22:26 사람 / man
    dict(ref=(4, 22, 28), lang='ko', en='man', words=['남자가', '사람이']),   # 신명기 22:28 사람 / man
    dict(ref=(4, 24, 3), lang='ko', en='hand', words=['손에']),   # 신명기 24:3 손 / hand
    dict(ref=(4, 24, 13), lang='ko', en='Lord', words=['여호와']),   # 신명기 24:13 여호와 / LORD
    dict(ref=(4, 24, 15), lang='ko', en='Lord', words=['여호와께']),   # 신명기 24:15 여호와 / LORD
    dict(ref=(4, 24, 19), lang='ko', en='Lord', words=['여호와께서']),   # 신명기 24:19 여호와 / LORD
    dict(ref=(4, 25, 15), lang='ko', en='Lord', words=['여호와께서']),   # 신명기 25:15 여호와 / LORD
    dict(ref=(4, 26, 1), lang='ko', en='Lord', words=['여호와께서']),   # 신명기 26:1 여호와 / LORD
    dict(ref=(4, 26, 11), lang='ko', en='Lord', words=['모든', '여호와께서']),   # 신명기 26:11 여호와 / LORD
    dict(ref=(4, 28, 10), lang='ko', en='name', words=['일컬음을', '이름으로']),   # 신명기 28:10 이름 / name
    dict(ref=(4, 28, 36), lang='ko', en='Lord', words=['여호와께서']),   # 신명기 28:36 여호와 / LORD
    dict(ref=(4, 28, 36), lang='ko', en='king', words=['임금을']),   # 신명기 28:36 임금 / king
    dict(ref=(4, 28, 45), lang='ko', en='Lord', words=['여호와의']),   # 신명기 28:45 여호와 / LORD
    dict(ref=(4, 28, 47), lang='ko', en='Lord', words=['여호와를']),   # 신명기 28:47 여호와 / LORD
    dict(ref=(4, 28, 52), lang='ko', en='Lord', words=['여호와께서']),   # 신명기 28:52 여호와 / LORD
    dict(ref=(4, 28, 62), lang='ko', en='Lord', words=['말씀을', '것이라', '여호와의']),   # 신명기 28:62 여호와 / LORD
    dict(ref=(4, 28, 65), lang='ko', en='Lord', words=['여호와께서']),   # 신명기 28:65 여호와 / LORD
    dict(ref=(4, 29, 4), lang='ko', en='Lord', words=['여호와께서']),   # 신명기 29:4 여호와 / LORD
    dict(ref=(4, 29, 6), lang='ko', en='Lord', words=['주는', '여호와이신']),   # 신명기 29:6 여호와 / LORD
    dict(ref=(4, 29, 24), lang='ko', en='Lord', words=['여호와께서']),   # 신명기 29:24 여호와 / LORD
    dict(ref=(4, 29, 25), lang='ko', en='Lord', words=['여호와께서']),   # 신명기 29:25 여호와 / LORD
    dict(ref=(4, 30, 1), lang='ko', en='Lord', words=['여호와께']),   # 신명기 30:1 여호와 / LORD
    dict(ref=(4, 31, 6), lang='ko', en='Lord', words=['앞에서', '여호와']),   # 신명기 31:6 여호와 / LORD
    dict(ref=(4, 31, 7), lang='ko', en='Lord', words=['여호와께서']),   # 신명기 31:7 여호와 / LORD
    dict(ref=(4, 31, 27), lang='ko', en='Lord', words=['여호와를']),   # 신명기 31:27 여호와 / LORD
    dict(ref=(4, 31, 29), lang='ko', en='Lord', words=['여호와의']),   # 신명기 31:29 여호와 / LORD
    dict(ref=(4, 32, 1), lang='ko', en='words', words=['입의', '말을']),   # 신명기 32:1 말 / word
    dict(ref=(4, 32, 2), lang='ko', en='speech', words=['말은']),   # 신명기 32:2 말 / word
    dict(ref=(4, 32, 3), lang='ko', en='Lord', words=['내가', '여호와의']),   # 신명기 32:3 여호와 / LORD
    dict(ref=(4, 32, 30), lang='ko', en='Lord', words=['아니하였고', '여호와께서']),   # 신명기 32:30 여호와 / LORD
    dict(ref=(4, 33, 21), lang='ko', en='Lord', words=['여호와의']),   # 신명기 33:21 여호와 / LORD
    dict(ref=(4, 34, 1), lang='ko', en='Lord', words=['여호와께서']),   # 신명기 34:1 여호와 / LORD
    dict(ref=(5, 1, 11), lang='ko', en='Lord', words=['여호와께서']),   # 여호수아 1:11 여호와 / LORD
    dict(ref=(5, 1, 17), lang='ko', en='Lord', words=['것#1', '여호와께서']),   # 여호수아 1:17 여호와 / LORD
    dict(ref=(5, 2, 2), lang='ko', en='men', words=['사람이']),   # 여호수아 2:2 사람 / man
    dict(ref=(5, 2, 11), lang='ko', en='Lord', words=['여호와는']),   # 여호수아 2:11 여호와 / LORD
    dict(ref=(5, 2, 11), lang='ko', en='hearts', words=['마음이']),   # 여호수아 2:11 마음 / heart
    dict(ref=(5, 2, 14), lang='ko', en='Lord', words=['이르되', '여호와께서']),   # 여호수아 2:14 여호와 / LORD
    dict(ref=(5, 4, 1), lang='ko', en='Lord', words=['여호와께서']),   # 여호수아 4:1 여호와 / LORD
    dict(ref=(5, 4, 7), lang='ko', en='Lord', words=['이르기를', '여호와의']),   # 여호수아 4:7 여호와 / LORD
    dict(ref=(5, 4, 7), lang='ko', en='children', words=['자손에게']),   # 여호수아 4:7 자손 / children·seed
    dict(ref=(5, 4, 8), lang='ko', en='Lord', words=['여호와께서']),   # 여호수아 4:8 여호와 / LORD
    dict(ref=(5, 4, 11), lang='ko', en='Lord', words=['여호와의']),   # 여호수아 4:11 여호와 / LORD
    dict(ref=(5, 4, 18), lang='ko', en='Lord', words=['여호와의']),   # 여호수아 4:18 여호와 / LORD
    dict(ref=(5, 6, 2), lang='ko', en='hand', words=['붙였으니', '손에']),   # 여호수아 6:2 손 / hand
    dict(ref=(5, 6, 26), lang='ko', en='Lord', words=['여호와']),   # 여호수아 6:26 여호와 / LORD
    dict(ref=(5, 7, 15), lang='ko', en='Lord', words=['여호와의']),   # 여호수아 7:15 여호와 / LORD
    dict(ref=(5, 8, 1), lang='ko', en='hand', words=['주었노니', '손에']),   # 여호수아 8:1 손 / hand
    dict(ref=(5, 8, 8), lang='ko', en='Lord', words=['말씀대로', '여호와의']),   # 여호수아 8:8 여호와 / LORD
    dict(ref=(5, 9, 18), lang='ko', en='Lord', words=['여호와로']),   # 여호수아 9:18 여호와 / LORD
    dict(ref=(5, 9, 24), lang='ko', en='Lord', words=['여호와께서']),   # 여호수아 9:24 여호와 / LORD
    dict(ref=(5, 10, 4), lang='ko', en='children', words=['자손으로']),   # 여호수아 10:4 자손 / children·seed
    dict(ref=(5, 10, 11), lang='ko', en='Lord', words=['여호와께서']),   # 여호수아 10:11 여호와 / LORD
    dict(ref=(5, 10, 11), lang='ko', en='children', words=['자손의']),   # 여호수아 10:11 자손 / children·seed
    dict(ref=(5, 11, 12), lang='ko', en='Lord', words=['같이', '여호와의']),   # 여호수아 11:12 여호와 / LORD
    dict(ref=(5, 11, 23), lang='ko', en='Lord', words=['말씀대로', '여호와께서']),   # 여호수아 11:23 여호와 / LORD
    dict(ref=(5, 13, 1), lang='ko', en='Lord', words=['여호와께서']),   # 여호수아 13:1 여호와 / LORD
    dict(ref=(5, 13, 14), lang='ko', en='Lord', words=['없었으니', '여호와께']),   # 여호수아 13:14 여호와 / LORD
    dict(ref=(5, 14, 5), lang='ko', en='Lord', words=['같이', '여호와께서']),   # 여호수아 14:5 여호와 / LORD
    dict(ref=(5, 14, 5), lang='ko', en='children', words=['여호와께서', '자손이']),   # 여호수아 14:5 자손 / children·seed
    dict(ref=(5, 14, 6), lang='ko', en='Lord', words=['말하되', '여호와께서']),   # 여호수아 14:6 여호와 / LORD
    dict(ref=(5, 14, 9), lang='ko', en='Lord', words=['여호와를']),   # 여호수아 14:9 여호와 / LORD
    dict(ref=(5, 17, 14), lang='ko', en='Lord', words=['여호와께서']),   # 여호수아 17:14 여호와 / LORD
    dict(ref=(5, 18, 6), lang='ko', en='Lord', words=['여호와']),   # 여호수아 18:6 여호와 / LORD
    dict(ref=(5, 18, 8), lang='ko', en='Lord', words=['여호와']),   # 여호수아 18:8 여호와 / LORD
    dict(ref=(5, 21, 26), lang='ko', en='children', words=['자손의']),   # 여호수아 21:26 자손 / children·seed
    dict(ref=(5, 21, 45), lang='ko', en='Lord', words=['여호와께서']),   # 여호수아 21:45 여호와 / LORD
    dict(ref=(5, 22, 9), lang='ko', en='Lord', words=['여호와께서']),   # 여호수아 22:9 여호와 / LORD
    dict(ref=(5, 22, 17), lang='ko', en='Lord', words=['여호와의']),   # 여호수아 22:17 여호와 / LORD
    dict(ref=(5, 22, 30), lang='ko', en='words', words=['말을']),   # 여호수아 22:30 말 / word
    dict(ref=(5, 23, 11), lang='ko', en='Lord', words=['여호와를']),   # 여호수아 23:11 여호와 / LORD
    dict(ref=(5, 23, 14), lang='ko', en='Lord', words=['가는', '여호와께서']),   # 여호수아 23:14 여호와 / LORD
    dict(ref=(5, 24, 19), lang='ko', en='Lord', words=['아니하실', '여호와를']),   # 여호수아 24:19 여호와 / LORD
    dict(ref=(5, 24, 27), lang='ko', en='words', words=['말씀을']),   # 여호수아 24:27 말씀 / word
    dict(ref=(6, 1, 17), lang='ko', en='name', words=['이름을']),   # 사사기 1:17 이름 / name
    dict(ref=(6, 5, 9), lang='ko', en='Lord', words=['여호와를']),   # 사사기 5:9 여호와 / LORD
    dict(ref=(6, 6, 2), lang='ko', en='children', words=['자손이']),   # 사사기 6:2 자손 / children·seed
    dict(ref=(6, 6, 7), lang='ko', en='Lord', words=['여호와께']),   # 사사기 6:7 여호와 / LORD
    dict(ref=(6, 6, 14), lang='ko', en='Lord', words=['여호와께서']),   # 사사기 6:14 여호와 / LORD
    dict(ref=(6, 6, 27), lang='ko', en='Lord', words=['대로', '여호와의']),   # 사사기 6:27 여호와 / LORD
    dict(ref=(6, 7, 15), lang='ko', en='Lord', words=['이르되', '여호와께서']),   # 사사기 7:15 여호와 / LORD
    dict(ref=(6, 8, 5), lang='ko', en='men', words=['종자가', '사람들에게']),   # 사사기 8:5 사람 / man
    dict(ref=(6, 8, 31), lang='ko', en='name', words=['하였더라', '이름을']),   # 사사기 8:31 이름 / name
    dict(ref=(6, 9, 3), lang='ko', en='words', words=['말을']),   # 사사기 9:3 말 / word
    dict(ref=(6, 10, 18), lang='ko', en='children', words=['자손과']),   # 사사기 10:18 자손 / children·seed
    dict(ref=(6, 11, 24), lang='ko', en='Lord', words=['여호와께서']),   # 사사기 11:24 여호와 / LORD
    dict(ref=(6, 11, 31), lang='ko', en='Lord', words=['여호와께']),   # 사사기 11:31 여호와 / LORD
    dict(ref=(6, 11, 35), lang='ko', en='Lord', words=['여호와를']),   # 사사기 11:35 여호와 / LORD
    dict(ref=(6, 12, 2), lang='ko', en='children', words=['자손과']),   # 사사기 12:2 자손 / children·seed
    dict(ref=(6, 13, 17), lang='ko', en='sayings', words=['말씀이']),   # 사사기 13:17 말씀 / word
    dict(ref=(6, 13, 19), lang='ko', en='Lord', words=['이에', '여호와께']),   # 사사기 13:19 여호와 / LORD
    dict(ref=(6, 13, 23), lang='ko', en='Lord', words=['여호와께서']),   # 사사기 13:23 여호와 / LORD
    dict(ref=(6, 15, 18), lang='ko', en='Lord', words=['여호와께']),   # 사사기 15:18 여호와 / LORD
    dict(ref=(6, 16, 20), lang='ko', en='Lord', words=['여호와께서']),   # 사사기 16:20 여호와 / LORD
    dict(ref=(6, 18, 2), lang='ko', en='children', words=['자손이']),   # 사사기 18:2 자손 / children·seed
    dict(ref=(6, 18, 19), lang='ko', en='house', words=['집의']),   # 사사기 18:19 집 / house
    dict(ref=(6, 20, 1), lang='ko', en='Lord', words=['여호와']),   # 사사기 20:1 여호와 / LORD
    dict(ref=(6, 21, 3), lang='ko', en='Lord', words=['중에', '여호와여']),   # 사사기 21:3 여호와 / LORD
    dict(ref=(7, 1, 6), lang='ko', en='Lord', words=['함을', '여호와께서']),   # 룻기 1:6 여호와 / LORD
    dict(ref=(7, 1, 13), lang='ko', en='Lord', words=['여호와의']),   # 룻기 1:13 여호와 / LORD
    dict(ref=(7, 1, 17), lang='ko', en='Lord', words=['여호와께서']),   # 룻기 1:17 여호와 / LORD
    dict(ref=(8, 1, 12), lang='ko', en='Lord', words=['여호와']),   # 사무엘상 1:12 여호와 / LORD
    dict(ref=(8, 1, 20), lang='ko', en='Lord', words=['여호와께']),   # 사무엘상 1:20 여호와 / LORD
    dict(ref=(8, 1, 22), lang='ko', en='Lord', words=['여호와']),   # 사무엘상 1:22 여호와 / LORD
    dict(ref=(8, 1, 23), lang='ko', en='Lord', words=['이에', '여호와께서']),   # 사무엘상 1:23 여호와 / LORD
    dict(ref=(8, 1, 27), lang='ko', en='Lord', words=['여호와께서']),   # 사무엘상 1:27 여호와 / LORD
    dict(ref=(8, 2, 11), lang='ko', en='Lord', words=['여호와를']),   # 사무엘상 2:11 여호와 / LORD
    dict(ref=(8, 3, 9), lang='ko', en='Lord', words=['여호와여']),   # 사무엘상 3:9 여호와 / LORD
    dict(ref=(8, 4, 2), lang='ko', en='men', words=['사람']),   # 사무엘상 4:2 사람 / man
    dict(ref=(8, 4, 6), lang='ko', en='Lord', words=['줄을', '여호와의']),   # 사무엘상 4:6 여호와 / LORD
    dict(ref=(8, 4, 10), lang='ko', en='man', words=['각기', '사람이']),   # 사무엘상 4:10 사람 / man
    dict(ref=(8, 6, 18), lang='ko', en='Lord', words=['여호와의']),   # 사무엘상 6:18 여호와 / LORD
    dict(ref=(8, 7, 2), lang='ko', en='Lord', words=['날부터', '여호와를']),   # 사무엘상 7:2 여호와 / LORD
    dict(ref=(8, 7, 6), lang='ko', en='children', words=['자손을']),   # 사무엘상 7:6 자손 / children·seed
    dict(ref=(8, 7, 10), lang='ko', en='Lord', words=['때에', '여호와께서']),   # 사무엘상 7:10 여호와 / LORD
    dict(ref=(8, 10, 1), lang='ko', en='Lord', words=['여호와께서']),   # 사무엘상 10:1 여호와 / LORD
    dict(ref=(8, 10, 19), lang='ko', en='Lord', words=['여호와']),   # 사무엘상 10:19 여호와 / LORD
    dict(ref=(8, 10, 25), lang='ko', en='Lord', words=['말하고', '여호와']),   # 사무엘상 10:25 여호와 / LORD
    dict(ref=(8, 11, 7), lang='ko', en='Lord', words=['여호와의']),   # 사무엘상 11:7 여호와 / LORD
    dict(ref=(8, 11, 13), lang='ko', en='Lord', words=['여호와께서']),   # 사무엘상 11:13 여호와 / LORD
    dict(ref=(8, 12, 12), lang='ko', en='Lord', words=['여호와께서는']),   # 사무엘상 12:12 여호와 / LORD
    dict(ref=(8, 13, 12), lang='ko', en='Lord', words=['이르기를', '여호와께']),   # 사무엘상 13:12 여호와 / LORD
    dict(ref=(8, 14, 10), lang='ko', en='Lord', words=['여호와께서']),   # 사무엘상 14:10 여호와 / LORD
    dict(ref=(8, 14, 12), lang='ko', en='Lord', words=['여호와께서']),   # 사무엘상 14:12 여호와 / LORD
    dict(ref=(8, 14, 23), lang='ko', en='Lord', words=['여호와께서']),   # 사무엘상 14:23 여호와 / LORD
    dict(ref=(8, 14, 33), lang='ko', en='Lord', words=['여호와께']),   # 사무엘상 14:33 여호와 / LORD
    dict(ref=(8, 14, 34), lang='ko', en='Lord', words=['여호와께']),   # 사무엘상 14:34 여호와 / LORD
    dict(ref=(8, 14, 45), lang='ko', en='Lord', words=['여호와의']),   # 사무엘상 14:45 여호와 / LORD
    dict(ref=(8, 15, 11), lang='ko', en='Lord', words=['여호와께']),   # 사무엘상 15:11 여호와 / LORD
    dict(ref=(8, 15, 15), lang='ko', en='Lord', words=['것을', '여호와께']),   # 사무엘상 15:15 여호와 / LORD
    dict(ref=(8, 15, 16), lang='ko', en='Lord', words=['여호와께서']),   # 사무엘상 15:16 여호와 / LORD
    dict(ref=(8, 15, 24), lang='ko', en='words', words=['말씀을', '말을']),   # 사무엘상 15:24 말 / word
    dict(ref=(8, 15, 25), lang='ko', en='Lord', words=['여호와께']),   # 사무엘상 15:25 여호와 / LORD
    dict(ref=(8, 15, 31), lang='ko', en='Lord', words=['여호와께']),   # 사무엘상 15:31 여호와 / LORD
    dict(ref=(8, 15, 33), lang='ko', en='Lord', words=['같이', '여호와']),   # 사무엘상 15:33 여호와 / LORD
    dict(ref=(8, 15, 35), lang='ko', en='Lord', words=['가서', '여호와께서는']),   # 사무엘상 15:35 여호와 / LORD
    dict(ref=(8, 16, 8), lang='ko', en='Lord', words=['여호와께서']),   # 사무엘상 16:8 여호와 / LORD
    dict(ref=(8, 16, 9), lang='ko', en='Lord', words=['이도', '여호와께서']),   # 사무엘상 16:9 여호와 / LORD
    dict(ref=(8, 16, 18), lang='ko', en='Lord', words=['알고', '여호와께서']),   # 사무엘상 16:18 여호와 / LORD
    dict(ref=(8, 17, 23), lang='ko', en='words', words=['말을']),   # 사무엘상 17:23 말 / word
    dict(ref=(8, 18, 17), lang='ko', en='Lord', words=['여호와의']),   # 사무엘상 18:17 여호와 / LORD
    dict(ref=(8, 20, 8), lang='ko', en='Lord', words=['여호와']),   # 사무엘상 20:8 여호와 / LORD
    dict(ref=(8, 20, 14), lang='ko', en='Lord', words=['여호와의']),   # 사무엘상 20:14 여호와 / LORD
    dict(ref=(8, 20, 21), lang='ko', en='Lord', words=['여호와께서']),   # 사무엘상 20:21 여호와 / LORD
    dict(ref=(8, 20, 22), lang='ko', en='Lord', words=['여호와께서']),   # 사무엘상 20:22 여호와 / LORD
    dict(ref=(8, 21, 2), lang='ko', en='man', words=['소년들을', '사람에게']),   # 사무엘상 21:2 사람 / man
    dict(ref=(8, 21, 6), lang='ko', en='Lord', words=['앞에서', '여호와']),   # 사무엘상 21:6 여호와 / LORD
    dict(ref=(8, 22, 22), lang='ko', en='house', words=['집의']),   # 사무엘상 22:22 집 / house
    dict(ref=(8, 23, 10), lang='ko', en='Lord', words=['여호와여']),   # 사무엘상 23:10 여호와 / LORD
    dict(ref=(8, 24, 15), lang='ko', en='Lord', words=['되어', '여호와께서']),   # 사무엘상 24:15 여호와 / LORD
    dict(ref=(8, 24, 18), lang='ko', en='Lord', words=['여호와께서']),   # 사무엘상 24:18 여호와 / LORD
    dict(ref=(8, 24, 19), lang='ko', en='Lord', words=['여호와께서']),   # 사무엘상 24:19 여호와 / LORD
    dict(ref=(8, 25, 9), lang='ko', en='words', words=['말을']),   # 사무엘상 25:9 말 / word
    dict(ref=(8, 25, 24), lang='ko', en='words', words=['말을']),   # 사무엘상 25:24 말 / word
    dict(ref=(8, 26, 12), lang='ko', en='Lord', words=['여호와께서']),   # 사무엘상 26:12 여호와 / LORD
    dict(ref=(8, 26, 24), lang='ko', en='Lord', words=['같이', '여호와께서']),   # 사무엘상 26:24 여호와 / LORD
    dict(ref=(8, 28, 16), lang='ko', en='Lord', words=['여호와께서']),   # 사무엘상 28:16 여호와 / LORD
    dict(ref=(8, 30, 6), lang='ko', en='Lord', words=['여호와를']),   # 사무엘상 30:6 여호와 / LORD
    dict(ref=(8, 30, 23), lang='ko', en='Lord', words=['여호와께서']),   # 사무엘상 30:23 여호와 / LORD
    dict(ref=(8, 30, 26), lang='ko', en='Lord', words=['여호와의']),   # 사무엘상 30:26 여호와 / LORD
    dict(ref=(9, 2, 6), lang='ko', en='Lord', words=['여호와께서']),   # 사무엘하 2:6 여호와 / LORD
    dict(ref=(9, 3, 9), lang='ko', en='Lord', words=['여호와께서']),   # 사무엘하 3:9 여호와 / LORD
    dict(ref=(9, 3, 17), lang='ko', en='king', words=['임금']),   # 사무엘하 3:17 임금 / king
    dict(ref=(9, 3, 28), lang='ko', en='Lord', words=['여호와']),   # 사무엘하 3:28 여호와 / LORD
    dict(ref=(9, 5, 12), lang='ko', en='Lord', words=['여호와께서']),   # 사무엘하 5:12 여호와 / LORD
    dict(ref=(9, 5, 24), lang='ko', en='Lord', words=['여호와가']),   # 사무엘하 5:24 여호와 / LORD
    dict(ref=(9, 6, 6), lang='ko', en='hand', words=['들어', '손을']),   # 사무엘하 6:6 손 / hand
    dict(ref=(9, 6, 8), lang='ko', en='Lord', words=['여호와께서']),   # 사무엘하 6:8 여호와 / LORD
    dict(ref=(9, 6, 10), lang='ko', en='Lord', words=['자기에게로', '여호와의']),   # 사무엘하 6:10 여호와 / LORD
    dict(ref=(9, 7, 1), lang='ko', en='Lord', words=['여호와께서']),   # 사무엘하 7:1 여호와 / LORD
    dict(ref=(9, 7, 5), lang='ko', en='Lord', words=['여호와의']),   # 사무엘하 7:5 여호와 / LORD
    dict(ref=(9, 7, 8), lang='ko', en='Lord', words=['여호와께서']),   # 사무엘하 7:8 여호와 / LORD
    dict(ref=(9, 7, 24), lang='ko', en='Lord', words=['여호와여']),   # 사무엘하 7:24 여호와 / LORD
    dict(ref=(9, 7, 25), lang='ko', en='Lord', words=['대하여', '여호와']),   # 사무엘하 7:25 여호와 / LORD
    dict(ref=(9, 7, 27), lang='ko', en='Lord', words=['여호와']),   # 사무엘하 7:27 여호와 / LORD
    dict(ref=(9, 7, 28), lang='ko', en='Lord', words=['주', '여호와여']),   # 사무엘하 7:28 여호와 / LORD
    dict(ref=(9, 8, 6), lang='ko', en='Lord', words=['여호와께서']),   # 사무엘하 8:6 여호와 / LORD
    dict(ref=(9, 8, 14), lang='ko', en='Lord', words=['되니라', '여호와께서']),   # 사무엘하 8:14 여호와 / LORD
    dict(ref=(9, 10, 10), lang='ko', en='children', words=['자손을']),   # 사무엘하 10:10 자손 / children·seed
    dict(ref=(9, 12, 9), lang='ko', en='Lord', words=['말씀을', '여호와의']),   # 사무엘하 12:9 여호와 / LORD
    dict(ref=(9, 12, 14), lang='ko', en='Lord', words=['여호와의']),   # 사무엘하 12:14 여호와 / LORD
    dict(ref=(9, 12, 17), lang='ko', en='house', words=['집의']),   # 사무엘하 12:17 집 / house
    dict(ref=(9, 12, 27), lang='ko', en='waters', words=['물들의']),   # 사무엘하 12:27 물 / water
    dict(ref=(9, 12, 31), lang='ko', en='children', words=['자손의']),   # 사무엘하 12:31 자손 / children·seed
    dict(ref=(9, 14, 3), lang='ko', en='words', words=['말을']),   # 사무엘하 14:3 말 / word
    dict(ref=(9, 14, 19), lang='ko', en='words', words=['말씀을', '말을']),   # 사무엘하 14:19 말 / word
    dict(ref=(9, 15, 3), lang='ko', en='man', words=['사람을']),   # 사무엘하 15:3 사람 / man
    dict(ref=(9, 15, 7), lang='ko', en='Lord', words=['여호와께']),   # 사무엘하 15:7 여호와 / LORD
    dict(ref=(9, 15, 22), lang='ko', en='men', words=['종자들과', '사람']),   # 사무엘하 15:22 사람 / man
    dict(ref=(9, 15, 23), lang='ko', en='king', words=['왕도']),   # 사무엘하 15:23 왕 / king
    dict(ref=(9, 16, 10), lang='ko', en='Lord', words=['여호와께서']),   # 사무엘하 16:10 여호와 / LORD
    dict(ref=(9, 16, 11), lang='ko', en='Lord', words=['여호와께서']),   # 사무엘하 16:11 여호와 / LORD
    dict(ref=(9, 16, 18), lang='ko', en='Lord', words=['여호와와']),   # 사무엘하 16:18 여호와 / LORD
    dict(ref=(9, 19, 7), lang='ko', en='Lord', words=['여호와를']),   # 사무엘하 19:7 여호와 / LORD
    dict(ref=(9, 21, 17), lang='ko', en='men', words=['종자들이', '사람을']),   # 사무엘하 21:17 사람 / man
    dict(ref=(9, 22, 7), lang='ko', en='Lord', words=['여호와께']),   # 사무엘하 22:7 여호와 / LORD
    dict(ref=(9, 22, 25), lang='ko', en='Lord', words=['여호와께서']),   # 사무엘하 22:25 여호와 / LORD
    dict(ref=(9, 22, 50), lang='ko', en='Lord', words=['이러므로', '여호와여']),   # 사무엘하 22:50 여호와 / LORD
    dict(ref=(9, 23, 16), lang='ko', en='Lord', words=['여호와께']),   # 사무엘하 23:16 여호와 / LORD
    dict(ref=(9, 23, 16), lang='ko', en='men', words=['사람의']),   # 사무엘하 23:16 사람 / man
    dict(ref=(9, 23, 17), lang='ko', en='Lord', words=['여호와여']),   # 사무엘하 23:17 여호와 / LORD
    dict(ref=(9, 24, 15), lang='ko', en='Lord', words=['여호와께서']),   # 사무엘하 24:15 여호와 / LORD
    dict(ref=(9, 24, 19), lang='ko', en='Lord', words=['여호와의']),   # 사무엘하 24:19 여호와 / LORD
    dict(ref=(9, 24, 23), lang='ko', en='Lord', words=['여호와께서']),   # 사무엘하 24:23 여호와 / LORD
    dict(ref=(9, 24, 24), lang='ko', en='Lord', words=['여호와께']),   # 사무엘하 24:24 여호와 / LORD
    dict(ref=(10, 1, 14), lang='ko', en='words', words=['말씀할', '말씀을']),   # 열왕기상 1:14 말씀 / word
    dict(ref=(10, 1, 30), lang='ko', en='Lord', words=['여호와를']),   # 열왕기상 1:30 여호와 / LORD
    dict(ref=(10, 2, 8), lang='ko', en='saying', words=['이르기를', '말로']),   # 열왕기상 2:8 말 / word
    dict(ref=(10, 2, 15), lang='ko', en='Lord', words=['되었음은', '여호와께로']),   # 열왕기상 2:15 여호와 / LORD
    dict(ref=(10, 2, 23), lang='ko', en='Lord', words=['여호와를']),   # 열왕기상 2:23 여호와 / LORD
    dict(ref=(10, 2, 29), lang='ko', en='Lord', words=['여호와의']),   # 열왕기상 2:29 여호와 / LORD
    dict(ref=(10, 2, 33), lang='ko', en='Lord', words=['여호와께로']),   # 열왕기상 2:33 여호와 / LORD
    dict(ref=(10, 3, 1), lang='ko', en='Lord', words=['여호와의']),   # 열왕기상 3:1 여호와 / LORD
    dict(ref=(10, 3, 2), lang='ko', en='Lord', words=['여호와의']),   # 열왕기상 3:2 여호와 / LORD
    dict(ref=(10, 4, 7), lang='ko', en='man', words=['사람들이']),   # 열왕기상 4:7 사람 / man
    dict(ref=(10, 5, 5), lang='ko', en='saying', words=['말씀에']),   # 열왕기상 5:5 말씀 / word
    dict(ref=(10, 5, 8), lang='ko', en='saying', words=['가로되', '말씀을']),   # 열왕기상 5:8 말씀 / word
    dict(ref=(10, 6, 12), lang='ko', en='word', words=['말을']),   # 열왕기상 6:12 말 / word
    dict(ref=(10, 8, 9), lang='ko', en='Lord', words=['여호와께서']),   # 열왕기상 8:9 여호와 / LORD
    dict(ref=(10, 8, 9), lang='ko', en='children', words=['여호와께서', '자손이']),   # 열왕기상 8:9 자손 / children·seed
    dict(ref=(10, 8, 25), lang='ko', en='saying', words=['말씀하시기를', '말씀을']),   # 열왕기상 8:25 말씀 / word
    dict(ref=(10, 8, 44), lang='ko', en='Lord', words=['여호와께']),   # 열왕기상 8:44 여호와 / LORD
    dict(ref=(10, 9, 10), lang='ko', en='Lord', words=['여호와의']),   # 열왕기상 9:10 여호와 / LORD
    dict(ref=(10, 10, 1), lang='ko', en='name', words=['이름으로']),   # 열왕기상 10:1 이름 / name
    dict(ref=(10, 11, 4), lang='ko', en='God', words=['하나님']),   # 열왕기상 11:4 하나님 / God
    dict(ref=(10, 12, 15), lang='ko', en='saying', words=['말을', '말씀을']),   # 열왕기상 12:15 말씀 / word
    dict(ref=(10, 12, 16), lang='ko', en='saying', words=['말을']),   # 열왕기상 12:16 말 / word
    dict(ref=(10, 13, 3), lang='ko', en='Lord', words=['하매', '여호와의']),   # 열왕기상 13:3 여호와 / LORD
    dict(ref=(10, 14, 21), lang='ko', en='Lord', words=['여호와께서']),   # 열왕기상 14:21 여호와 / LORD
    dict(ref=(10, 15, 5), lang='ko', en='Lord', words=['행하고', '여호와']),   # 열왕기상 15:5 여호와 / LORD
    dict(ref=(10, 15, 30), lang='ko', en='Lord', words=['여호와의']),   # 열왕기상 15:30 여호와 / LORD
    dict(ref=(10, 16, 7), lang='ko', en='word', words=['말씀이']),   # 열왕기상 16:7 말씀 / word
    dict(ref=(10, 17, 1), lang='ko', en='Lord', words=['여호와의']),   # 열왕기상 17:1 여호와 / LORD
    dict(ref=(10, 18, 18), lang='ko', en='Lord', words=['대답하되', '여호와의']),   # 열왕기상 18:18 여호와 / LORD
    dict(ref=(10, 18, 21), lang='ko', en='Lord', words=['여호와가']),   # 열왕기상 18:21 여호와 / LORD
    dict(ref=(10, 18, 22), lang='ko', en='Lord', words=['여호와의']),   # 열왕기상 18:22 여호와 / LORD
    dict(ref=(10, 18, 36), lang='ko', en='Lord', words=['중에서', '여호와여']),   # 열왕기상 18:36 여호와 / LORD
    dict(ref=(10, 18, 37), lang='ko', en='God', words=['하나님이신']),   # 열왕기상 18:37 하나님 / God
    dict(ref=(10, 19, 4), lang='ko', en='Lord', words=['하고', '여호와여']),   # 열왕기상 19:4 여호와 / LORD
    dict(ref=(10, 19, 9), lang='ko', en='Lord', words=['이르시되', '여호와의']),   # 열왕기상 19:9 여호와 / LORD
    dict(ref=(10, 20, 13), lang='ko', en='saying', words=['가로되', '말씀이']),   # 열왕기상 20:13 말씀 / word
    dict(ref=(10, 20, 20), lang='ko', en='man', words=['각각', '사람이']),   # 열왕기상 20:20 사람 / man
    dict(ref=(10, 20, 31), lang='ko', en='house', words=['집의']),   # 열왕기상 20:31 집 / house
    dict(ref=(10, 20, 35), lang='ko', en='Lord', words=['중', '여호와의']),   # 열왕기상 20:35 여호와 / LORD
    dict(ref=(10, 20, 36), lang='ko', en='Lord', words=['여호와의']),   # 열왕기상 20:36 여호와 / LORD
    dict(ref=(10, 21, 20), lang='ko', en='Lord', words=['여호와']),   # 열왕기상 21:20 여호와 / LORD
    dict(ref=(10, 21, 25), lang='ko', en='Lord', words=['자가', '여호와']),   # 열왕기상 21:25 여호와 / LORD
    dict(ref=(10, 21, 26), lang='ko', en='Lord', words=['여호와께서']),   # 열왕기상 21:26 여호와 / LORD
    dict(ref=(10, 22, 11), lang='ko', en='Lord', words=['여호와의']),   # 열왕기상 22:11 여호와 / LORD
    dict(ref=(10, 22, 16), lang='ko', en='Lord', words=['고하겠느냐', '여호와의']),   # 열왕기상 22:16 여호와 / LORD
    dict(ref=(10, 22, 17), lang='ko', en='Lord', words=['여호와의']),   # 열왕기상 22:17 여호와 / LORD
    dict(ref=(10, 22, 21), lang='ko', en='Lord', words=['여호와']),   # 열왕기상 22:21 여호와 / LORD
    dict(ref=(10, 22, 43), lang='ko', en='Lord', words=['행하며', '여호와']),   # 열왕기상 22:43 여호와 / LORD
    dict(ref=(11, 1, 4), lang='ko', en='Lord', words=['하셨다', '여호와의']),   # 열왕기하 1:4 여호와 / LORD
    dict(ref=(11, 1, 15), lang='ko', en='Lord', words=['말고', '여호와의']),   # 열왕기하 1:15 여호와 / LORD
    dict(ref=(11, 1, 16), lang='ko', en='Lord', words=['여호와의']),   # 열왕기하 1:16 여호와 / LORD
    dict(ref=(11, 1, 16), lang='ko', en='word', words=['말씀이', '말을']),   # 열왕기하 1:16 말 / word
    dict(ref=(11, 2, 16), lang='ko', en='Lord', words=['여호와의']),   # 열왕기하 2:16 여호와 / LORD
    dict(ref=(11, 2, 22), lang='ko', en='saying', words=['말과']),   # 열왕기하 2:22 말 / word
    dict(ref=(11, 3, 10), lang='ko', en='Lord', words=['여호와께서']),   # 열왕기하 3:10 여호와 / LORD
    dict(ref=(11, 5, 1), lang='ko', en='Lord', words=['앞에서', '여호와께서']),   # 열왕기하 5:1 여호와 / LORD
    dict(ref=(11, 5, 17), lang='ko', en='Lord', words=['여호와께']),   # 열왕기하 5:17 여호와 / LORD
    dict(ref=(11, 7, 10), lang='ko', en='saying', words=['가로되', '말과']),   # 열왕기하 7:10 말 / word
    dict(ref=(11, 8, 1), lang='ko', en='Lord', words=['여호와께서']),   # 열왕기하 8:1 여호와 / LORD
    dict(ref=(11, 8, 10), lang='ko', en='Lord', words=['여호와께서']),   # 열왕기하 8:10 여호와 / LORD
    dict(ref=(11, 8, 13), lang='ko', en='Lord', words=['여호와께서']),   # 열왕기하 8:13 여호와 / LORD
    dict(ref=(11, 9, 12), lang='ko', en='saying', words=['말씀이']),   # 열왕기하 9:12 말씀 / word
    dict(ref=(11, 9, 12), lang='ko', en='saying', words=['말이라']),   # 열왕기하 9:12 말 / word
    dict(ref=(11, 9, 18), lang='ko', en='saying', words=['말을', '말씀이']),   # 열왕기하 9:18 말씀 / word
    dict(ref=(11, 10, 6), lang='ko', en='saying', words=['일렀으되', '말을']),   # 열왕기하 10:6 말 / word
    dict(ref=(11, 10, 17), lang='ko', en='Lord', words=['여호와께서']),   # 열왕기하 10:17 여호와 / LORD
    dict(ref=(11, 10, 23), lang='ko', en='Lord', words=['중에', '여호와의']),   # 열왕기하 10:23 여호와 / LORD
    dict(ref=(11, 11, 7), lang='ko', en='Lord', words=['여호와의']),   # 열왕기하 11:7 여호와 / LORD
    dict(ref=(11, 11, 10), lang='ko', en='Lord', words=['여호와의']),   # 열왕기하 11:10 여호와 / LORD
    dict(ref=(11, 11, 13), lang='ko', en='Lord', words=['전에', '여호와의']),   # 열왕기하 11:13 여호와 / LORD
    dict(ref=(11, 11, 15), lang='ko', en='Lord', words=['여호와의']),   # 열왕기하 11:15 여호와 / LORD
    dict(ref=(11, 13, 6), lang='ko', en='house', words=['집의']),   # 열왕기하 13:6 집 / house
    dict(ref=(11, 17, 12), lang='ko', en='Lord', words=['여호와께서']),   # 열왕기하 17:12 여호와 / LORD
    dict(ref=(11, 17, 23), lang='ko', en='Lord', words=['여호와께서']),   # 열왕기하 17:23 여호와 / LORD
    dict(ref=(11, 17, 28), lang='ko', en='Lord', words=['여호와']),   # 열왕기하 17:28 여호와 / LORD
    dict(ref=(11, 17, 34), lang='ko', en='children', words=['자손에게']),   # 열왕기하 17:34 자손 / children·seed
    dict(ref=(11, 17, 39), lang='ko', en='Lord', words=['여호와를']),   # 열왕기하 17:39 여호와 / LORD
    dict(ref=(11, 18, 32), lang='ko', en='Lord', words=['여호와께서']),   # 열왕기하 18:32 여호와 / LORD
    dict(ref=(11, 18, 35), lang='ko', en='Lord', words=['여호와가']),   # 열왕기하 18:35 여호와 / LORD
    dict(ref=(11, 19, 6), lang='ko', en='words', words=['말씀이', '말을']),   # 열왕기하 19:6 말 / word
    dict(ref=(11, 19, 20), lang='ko', en='saying', words=['가로되', '말씀이']),   # 열왕기하 19:20 말씀 / word
    dict(ref=(11, 20, 3), lang='ko', en='Lord', words=['여호와여']),   # 열왕기하 20:3 여호와 / LORD
    dict(ref=(11, 20, 4), lang='ko', en='Lord', words=['여호와의']),   # 열왕기하 20:4 여호와 / LORD
    dict(ref=(11, 21, 13), lang='ko', en='man', words=['같이', '사람이']),   # 열왕기하 21:13 사람 / man
    dict(ref=(11, 22, 4), lang='ko', en='Lord', words=['여호와의']),   # 열왕기하 22:4 여호와 / LORD
    dict(ref=(11, 22, 18), lang='ko', en='words', words=['말씀이', '말을']),   # 열왕기하 22:18 말 / word
    dict(ref=(11, 23, 10), lang='ko', en='son', words=['아들']),   # 열왕기하 23:10 아들 / son
    dict(ref=(11, 23, 11), lang='ko', en='Lord', words=['들어가는', '여호와의']),   # 열왕기하 23:11 여호와 / LORD
    dict(ref=(11, 23, 25), lang='ko', en='king', words=['임금은']),   # 열왕기하 23:25 임금 / king
    dict(ref=(12, 2, 50), lang='ko', en='sons', words=['아들은', '자손']),   # 역대상 2:50 자손 / children·seed
    dict(ref=(12, 4, 21), lang='ko', en='sons', words=['아들', '자손은']),   # 역대상 4:21 자손 / children·seed
    dict(ref=(12, 5, 18), lang='ko', en='sons', words=['자손과']),   # 역대상 5:18 자손 / children·seed
    dict(ref=(12, 6, 3), lang='ko', en='sons', words=['아들들은']),   # 역대상 6:3 아들 / son
    dict(ref=(12, 6, 26), lang='ko', en='sons', words=['아들은#1', '자손은']),   # 역대상 6:26 자손 / children·seed
    dict(ref=(12, 6, 31), lang='ko', en='Lord', words=['여호와의']),   # 역대상 6:31 여호와 / LORD
    dict(ref=(12, 6, 44), lang='ko', en='sons', words=['아들이요#1', '자손']),   # 역대상 6:44 자손 / children·seed
    dict(ref=(12, 6, 50), lang='ko', en='sons', words=['아들은#2', '자손들은']),   # 역대상 6:50 자손 / children·seed
    dict(ref=(12, 7, 7), lang='ko', en='house', words=['집의']),   # 역대상 7:7 집 / house
    dict(ref=(12, 7, 9), lang='ko', en='house', words=['집의']),   # 역대상 7:9 집 / house
    dict(ref=(12, 7, 11), lang='ko', en='sons', words=['아들들은', '자손']),   # 역대상 7:11 자손 / children·seed
    dict(ref=(12, 9, 7), lang='ko', en='sons', words=['아들', '자손']),   # 역대상 9:7 자손 / children·seed
    dict(ref=(12, 9, 9), lang='ko', en='house', words=['집의']),   # 역대상 9:9 집 / house
    dict(ref=(12, 9, 14), lang='ko', en='sons', words=['자손']),   # 역대상 9:14 자손 / children·seed
    dict(ref=(12, 9, 20), lang='ko', en='Lord', words=['여호와께서']),   # 역대상 9:20 여호와 / LORD
    dict(ref=(12, 9, 23), lang='ko', en='Lord', words=['여호와의']),   # 역대상 9:23 여호와 / LORD
    dict(ref=(12, 11, 9), lang='ko', en='Lord', words=['여호와께서']),   # 역대상 11:9 여호와 / LORD
    dict(ref=(12, 11, 10), lang='ko', en='Lord', words=['여호와께서']),   # 역대상 11:10 여호와 / LORD
    dict(ref=(12, 11, 10), lang='ko', en='men', words=['용사의', '사람들이']),   # 역대상 11:10 사람 / man
    dict(ref=(12, 11, 11), lang='ko', en='men', words=['용사의', '사람의']),   # 역대상 11:11 사람 / man
    dict(ref=(12, 11, 18), lang='ko', en='Lord', words=['그', '여호와께']),   # 역대상 11:18 여호와 / LORD
    dict(ref=(12, 11, 26), lang='ko', en='men', words=['용사는', '사람']),   # 역대상 11:26 사람 / man
    dict(ref=(12, 12, 2), lang='ko', en='hand', words=['손을']),   # 역대상 12:2 손 / hand
    dict(ref=(12, 13, 11), lang='ko', en='Lord', words=['여호와께서']),   # 역대상 13:11 여호와 / LORD
    dict(ref=(12, 14, 2), lang='ko', en='Lord', words=['줄을', '여호와께서']),   # 역대상 14:2 여호와 / LORD
    dict(ref=(12, 14, 10), lang='ko', en='Lord', words=['여호와께서']),   # 역대상 14:10 여호와 / LORD
    dict(ref=(12, 15, 15), lang='ko', en='Lord', words=['여호와의']),   # 역대상 15:15 여호와 / LORD
    dict(ref=(12, 15, 17), lang='ko', en='sons', words=['자손']),   # 역대상 15:17 자손 / children·seed
    dict(ref=(12, 15, 25), lang='ko', en='Lord', words=['여호와의']),   # 역대상 15:25 여호와 / LORD
    dict(ref=(12, 15, 26), lang='ko', en='Lord', words=['여호와의']),   # 역대상 15:26 여호와 / LORD
    dict(ref=(12, 16, 33), lang='ko', en='Lord', words=['앞에서', '여호와']),   # 역대상 16:33 여호와 / LORD
    dict(ref=(12, 16, 41), lang='ko', en='Lord', words=['여호와의']),   # 역대상 16:41 여호와 / LORD
    dict(ref=(12, 17, 4), lang='ko', en='Lord', words=['여호와의']),   # 역대상 17:4 여호와 / LORD
    dict(ref=(12, 17, 7), lang='ko', en='Lord', words=['여호와께서']),   # 역대상 17:7 여호와 / LORD
    dict(ref=(12, 17, 19), lang='ko', en='Lord', words=['여호와여']),   # 역대상 17:19 여호와 / LORD
    dict(ref=(12, 17, 20), lang='ko', en='Lord', words=['여호와여']),   # 역대상 17:20 여호와 / LORD
    dict(ref=(12, 17, 23), lang='ko', en='Lord', words=['여호와여']),   # 역대상 17:23 여호와 / LORD
    dict(ref=(12, 17, 24), lang='ko', en='Lord', words=['여호와는']),   # 역대상 17:24 여호와 / LORD
    dict(ref=(12, 19, 1), lang='ko', en='son', words=['아들이']),   # 역대상 19:1 아들 / son
    dict(ref=(12, 19, 7), lang='ko', en='children', words=['자손이']),   # 역대상 19:7 자손 / children·seed
    dict(ref=(12, 19, 11), lang='ko', en='children', words=['자손을']),   # 역대상 19:11 자손 / children·seed
    dict(ref=(12, 19, 18), lang='ko', en='men', words=['사람이']),   # 역대상 19:18 사람 / man
    dict(ref=(12, 20, 3), lang='ko', en='children', words=['자손의']),   # 역대상 20:3 자손 / children·seed
    dict(ref=(12, 21, 10), lang='ko', en='Lord', words=['여호와의']),   # 역대상 21:10 여호와 / LORD
    dict(ref=(12, 21, 10), lang='ko', en='saying', words=['말씀이']),   # 역대상 21:10 말씀 / word
    dict(ref=(12, 21, 14), lang='ko', en='Lord', words=['여호와께서']),   # 역대상 21:14 여호와 / LORD
    dict(ref=(12, 21, 17), lang='ko', en='Lord', words=['여호와여']),   # 역대상 21:17 여호와 / LORD
    dict(ref=(12, 21, 22), lang='ko', en='Lord', words=['여호와를']),   # 역대상 21:22 여호와 / LORD
    dict(ref=(12, 21, 28), lang='ko', en='Lord', words=['여호와께서']),   # 역대상 21:28 여호와 / LORD
    dict(ref=(12, 21, 30), lang='ko', en='Lord', words=['여호와의']),   # 역대상 21:30 여호와 / LORD
    dict(ref=(12, 22, 13), lang='ko', en='Lord', words=['행하면', '여호와께서']),   # 역대상 22:13 여호와 / LORD
    dict(ref=(12, 22, 16), lang='ko', en='Lord', words=['여호와께서']),   # 역대상 22:16 여호와 / LORD
    dict(ref=(12, 23, 4), lang='ko', en='Lord', words=['여호와의']),   # 역대상 23:4 여호와 / LORD
    dict(ref=(12, 23, 24), lang='ko', en='Lord', words=['자손이니', '여호와의']),   # 역대상 23:24 여호와 / LORD
    dict(ref=(12, 23, 24), lang='ko', en='sons', words=['자손이니']),   # 역대상 23:24 자손 / children·seed
    dict(ref=(12, 23, 28), lang='ko', en='Lord', words=['여호와의']),   # 역대상 23:28 여호와 / LORD
    dict(ref=(12, 26, 1), lang='ko', en='sons', words=['자손']),   # 역대상 26:1 자손 / children·seed
    dict(ref=(12, 26, 10), lang='ko', en='sons', words=['아들들이']),   # 역대상 26:10 아들 / son
    dict(ref=(12, 26, 12), lang='ko', en='Lord', words=['여호와의']),   # 역대상 26:12 여호와 / LORD
    dict(ref=(12, 26, 29), lang='ko', en='sons', words=['아들들은', '자손']),   # 역대상 26:29 자손 / children·seed
    dict(ref=(12, 27, 23), lang='ko', en='Lord', words=['여호와께서']),   # 역대상 27:23 여호와 / LORD
    dict(ref=(12, 28, 10), lang='ko', en='Lord', words=['여호와께서']),   # 역대상 28:10 여호와 / LORD
    dict(ref=(12, 28, 12), lang='ko', en='Lord', words=['여호와의']),   # 역대상 28:12 여호와 / LORD
    dict(ref=(12, 29, 9), lang='ko', en='king', words=['왕도']),   # 역대상 29:9 왕 / king
    dict(ref=(12, 29, 16), lang='ko', en='Lord', words=['여호와여']),   # 역대상 29:16 여호와 / LORD
    dict(ref=(13, 1, 9), lang='ko', en='Lord', words=['하신', '여호와']),   # 역대하 1:9 여호와 / LORD
    dict(ref=(13, 2, 11), lang='ko', en='Lord', words=['가로되', '여호와께서']),   # 역대하 2:11 여호와 / LORD
    dict(ref=(13, 5, 10), lang='ko', en='Lord', words=['여호와께서']),   # 역대하 5:10 여호와 / LORD
    dict(ref=(13, 5, 10), lang='ko', en='children', words=['여호와께서', '자손이']),   # 역대하 5:10 자손 / children·seed
    dict(ref=(13, 5, 14), lang='ko', en='Lord', words=['여호와의']),   # 역대하 5:14 여호와 / LORD
    dict(ref=(13, 6, 5), lang='ko', en='man', words=['사람도']),   # 역대하 6:5 사람 / man
    dict(ref=(13, 6, 14), lang='ko', en='Lord', words=['여호와여']),   # 역대하 6:14 여호와 / LORD
    dict(ref=(13, 6, 16), lang='ko', en='Lord', words=['여호와여']),   # 역대하 6:16 여호와 / LORD
    dict(ref=(13, 6, 16), lang='ko', en='saying', words=['말씀하시기를', '말씀을']),   # 역대하 6:16 말씀 / word
    dict(ref=(13, 6, 17), lang='ko', en='Lord', words=['주는', '여호와여']),   # 역대하 6:17 여호와 / LORD
    dict(ref=(13, 7, 1), lang='ko', en='Lord', words=['여호와의']),   # 역대하 7:1 여호와 / LORD
    dict(ref=(13, 7, 10), lang='ko', en='Lord', words=['인하여', '여호와께서']),   # 역대하 7:10 여호와 / LORD
    dict(ref=(13, 7, 21), lang='ko', en='Lord', words=['여호와께서']),   # 역대하 7:21 여호와 / LORD
    dict(ref=(13, 7, 22), lang='ko', en='land', words=['숭배하여', '땅에서']),   # 역대하 7:22 땅 / land·earth
    dict(ref=(13, 8, 1), lang='ko', en='Lord', words=['여호와의']),   # 역대하 8:1 여호와 / LORD
    dict(ref=(13, 8, 2), lang='ko', en='children', words=['준', '자손으로']),   # 역대하 8:2 자손 / children·seed
    dict(ref=(13, 8, 11), lang='ko', en='Lord', words=['여호와의']),   # 역대하 8:11 여호와 / LORD
    dict(ref=(13, 8, 14), lang='ko', en='man', words=['사람에게도', '사람']),   # 역대하 8:14 사람 / man
    dict(ref=(13, 10, 15), lang='ko', en='word', words=['말씀을', '말을']),   # 역대하 10:15 말 / word
    dict(ref=(13, 11, 14), lang='ko', en='Lord', words=['여호와께']),   # 역대하 11:14 여호와 / LORD
    dict(ref=(13, 12, 1), lang='ko', en='Lord', words=['여호와의']),   # 역대하 12:1 여호와 / LORD
    dict(ref=(13, 12, 2), lang='ko', en='Lord', words=['여호와께']),   # 역대하 12:2 여호와 / LORD
    dict(ref=(13, 12, 11), lang='ko', en='Lord', words=['여호와의']),   # 역대하 12:11 여호와 / LORD
    dict(ref=(13, 12, 13), lang='ko', en='Lord', words=['여호와께서']),   # 역대하 12:13 여호와 / LORD
    dict(ref=(13, 12, 14), lang='ko', en='Lord', words=['여호와를']),   # 역대하 12:14 여호와 / LORD
    dict(ref=(13, 13, 5), lang='ko', en='Lord', words=['여호와께서']),   # 역대하 13:5 여호와 / LORD
    dict(ref=(13, 13, 8), lang='ko', en='Lord', words=['여호와의']),   # 역대하 13:8 여호와 / LORD
    dict(ref=(13, 13, 8), lang='ko', en='sons', words=['여호와의', '자손의']),   # 역대하 13:8 자손 / children·seed
    dict(ref=(13, 13, 12), lang='ko', en='Lord', words=['여호와와']),   # 역대하 13:12 여호와 / LORD
    dict(ref=(13, 13, 18), lang='ko', en='Lord', words=['여호와를']),   # 역대하 13:18 여호와 / LORD
    dict(ref=(13, 13, 20), lang='ko', en='Lord', words=['못하고', '여호와의']),   # 역대하 13:20 여호와 / LORD
    dict(ref=(13, 13, 22), lang='ko', en='sayings', words=['말은']),   # 역대하 13:22 말 / word
    dict(ref=(13, 14, 4), lang='ko', en='Lord', words=['여호와를']),   # 역대하 14:4 여호와 / LORD
    dict(ref=(13, 14, 6), lang='ko', en='Lord', words=['여호와께서']),   # 역대하 14:6 여호와 / LORD
    dict(ref=(13, 14, 7), lang='ko', en='Lord', words=['여호와를']),   # 역대하 14:7 여호와 / LORD
    dict(ref=(13, 14, 13), lang='ko', en='Lord', words=['여호와']),   # 역대하 14:13 여호와 / LORD
    dict(ref=(13, 15, 9), lang='ko', en='Lord', words=['여호와께서']),   # 역대하 15:9 여호와 / LORD
    dict(ref=(13, 18, 10), lang='ko', en='Lord', words=['여호와의']),   # 역대하 18:10 여호와 / LORD
    dict(ref=(13, 18, 16), lang='ko', en='Lord', words=['같이', '여호와의']),   # 역대하 18:16 여호와 / LORD
    dict(ref=(13, 19, 8), lang='ko', en='Lord', words=['여호와께']),   # 역대하 19:8 여호와 / LORD
    dict(ref=(13, 19, 10), lang='ko', en='Lord', words=['무릇', '여호와께']),   # 역대하 19:10 여호와 / LORD
    dict(ref=(13, 20, 14), lang='ko', en='sons', words=['자손']),   # 역대하 20:14 자손 / children·seed
    dict(ref=(13, 20, 20), lang='ko', en='Lord', words=['여호와를']),   # 역대하 20:20 여호와 / LORD
    dict(ref=(13, 20, 37), lang='ko', en='Lord', words=['여호와께서']),   # 역대하 20:37 여호와 / LORD
    dict(ref=(13, 21, 6), lang='ko', en='Lord', words=['여호와']),   # 역대하 21:6 여호와 / LORD
    dict(ref=(13, 21, 10), lang='ko', en='Lord', words=['여호와를']),   # 역대하 21:10 여호와 / LORD
    dict(ref=(13, 21, 12), lang='ko', en='saying', words=['말씀이']),   # 역대하 21:12 말씀 / word
    dict(ref=(13, 22, 10), lang='ko', en='house', words=['집의']),   # 역대하 22:10 집 / house
    dict(ref=(13, 23, 3), lang='ko', en='sons', words=['자손에게']),   # 역대하 23:3 자손 / children·seed
    dict(ref=(13, 23, 14), lang='ko', en='Lord', words=['여호와의']),   # 역대하 23:14 여호와 / LORD
    dict(ref=(13, 23, 16), lang='ko', en='Lord', words=['자기와', '여호와의']),   # 역대하 23:16 여호와 / LORD
    dict(ref=(13, 23, 20), lang='ko', en='Lord', words=['여호와의']),   # 역대하 23:20 여호와 / LORD
    dict(ref=(13, 24, 6), lang='ko', en='Lord', words=['여호와의']),   # 역대하 24:6 여호와 / LORD
    dict(ref=(13, 24, 8), lang='ko', en='Lord', words=['하고', '여호와의']),   # 역대하 24:8 여호와 / LORD
    dict(ref=(13, 24, 19), lang='ko', en='Lord', words=['여호와께서']),   # 역대하 24:19 여호와 / LORD
    dict(ref=(13, 24, 22), lang='ko', en='Lord', words=['여호와는']),   # 역대하 24:22 여호와 / LORD
    dict(ref=(13, 25, 4), lang='ko', en='Lord', words=['여호와께서']),   # 역대하 25:4 여호와 / LORD
    dict(ref=(13, 25, 5), lang='ko', en='men', words=['사람을']),   # 역대하 25:5 사람 / man
    dict(ref=(13, 25, 9), lang='ko', en='Lord', words=['여호와께서']),   # 역대하 25:9 여호와 / LORD
    dict(ref=(13, 26, 10), lang='ko', en='country', words=['땅에']),   # 역대하 26:10 땅 / land·earth
    dict(ref=(13, 26, 19), lang='ko', en='Lord', words=['여호와의']),   # 역대하 26:19 여호와 / LORD
    dict(ref=(13, 26, 20), lang='ko', en='Lord', words=['여호와께서']),   # 역대하 26:20 여호와 / LORD
    dict(ref=(13, 26, 23), lang='ko', en='kings', words=['열왕의', '왕이']),   # 역대하 26:23 왕 / king
    dict(ref=(13, 27, 6), lang='ko', en='Lord', words=['여호와']),   # 역대하 27:6 여호와 / LORD
    dict(ref=(13, 28, 3), lang='ko', en='Lord', words=['여호와께서']),   # 역대하 28:3 여호와 / LORD
    dict(ref=(13, 28, 10), lang='ko', en='Lord', words=['여호와께']),   # 역대하 28:10 여호와 / LORD
    dict(ref=(13, 28, 27), lang='ko', en='kings', words=['열왕의', '왕이']),   # 역대하 28:27 왕 / king
    dict(ref=(13, 29, 5), lang='ko', en='Lord', words=['여호와의']),   # 역대하 29:5 여호와 / LORD
    dict(ref=(13, 29, 11), lang='ko', en='Lord', words=['분향하게', '여호와께서']),   # 역대하 29:11 여호와 / LORD
    dict(ref=(13, 29, 21), lang='ko', en='Lord', words=['여호와의']),   # 역대하 29:21 여호와 / LORD
    dict(ref=(13, 29, 27), lang='ko', en='Lord', words=['여호와의']),   # 역대하 29:27 여호와 / LORD
    dict(ref=(13, 29, 30), lang='ko', en='Lord', words=['여호와를']),   # 역대하 29:30 여호와 / LORD
    dict(ref=(13, 30, 5), lang='ko', en='Lord', words=['여호와의']),   # 역대하 30:5 여호와 / LORD
    dict(ref=(13, 30, 17), lang='ko', en='Lord', words=['여호와']),   # 역대하 30:17 여호와 / LORD
    dict(ref=(13, 30, 18), lang='ko', en='Lord', words=['여호와여']),   # 역대하 30:18 여호와 / LORD
    dict(ref=(13, 31, 3), lang='ko', en='Lord', words=['대로', '여호와의']),   # 역대하 31:3 여호와 / LORD
    dict(ref=(13, 31, 4), lang='ko', en='Lord', words=['여호와의']),   # 역대하 31:4 여호와 / LORD
    dict(ref=(13, 31, 11), lang='ko', en='Lord', words=['여호와의']),   # 역대하 31:11 여호와 / LORD
    dict(ref=(13, 31, 20), lang='ko', en='Lord', words=['여호와']),   # 역대하 31:20 여호와 / LORD
    dict(ref=(13, 32, 6), lang='ko', en='saying', words=['가로되', '말로']),   # 역대하 32:6 말 / word
    dict(ref=(13, 32, 14), lang='ko', en='God', words=['하나님이']),   # 역대하 32:14 하나님 / God
    dict(ref=(13, 32, 16), lang='ko', en='Lord', words=['여호와']),   # 역대하 32:16 여호와 / LORD
    dict(ref=(13, 32, 33), lang='ko', en='sons', words=['아들', '자손의']),   # 역대하 32:33 자손 / children·seed
    dict(ref=(13, 33, 18), lang='ko', en='Lord', words=['여호와의']),   # 역대하 33:18 여호와 / LORD
    dict(ref=(13, 34, 26), lang='ko', en='words', words=['말씀이', '말을']),   # 역대하 34:26 말 / word
    dict(ref=(13, 34, 27), lang='ko', en='Lord', words=['여호와가']),   # 역대하 34:27 여호와 / LORD
    dict(ref=(13, 34, 27), lang='ko', en='words', words=['말을']),   # 역대하 34:27 말 / word
    dict(ref=(13, 35, 12), lang='ko', en='Lord', words=['여호와께']),   # 역대하 35:12 여호와 / LORD
    dict(ref=(13, 35, 26), lang='ko', en='Lord', words=['여호와의']),   # 역대하 35:26 여호와 / LORD
    dict(ref=(13, 36, 7), lang='ko', en='Lord', words=['여호와의']),   # 역대하 36:7 여호와 / LORD
    dict(ref=(14, 1, 3), lang='ko', en='Lord', words=['된', '여호와의']),   # 에스라 1:3 여호와 / LORD
    dict(ref=(14, 3, 3), lang='ko', en='Lord', words=['여호와께']),   # 에스라 3:3 여호와 / LORD
    dict(ref=(14, 4, 3), lang='ko', en='Lord', words=['여호와를']),   # 에스라 4:3 여호와 / LORD
    dict(ref=(14, 4, 15), lang='ko', en='kings', words=['열왕과', '왕은']),   # 에스라 4:15 왕 / king
    dict(ref=(14, 6, 8), lang='ko', en='king', words=['왕의']),   # 에스라 6:8 왕 / king
    dict(ref=(14, 7, 28), lang='ko', en='Lord', words=['여호와의']),   # 에스라 7:28 여호와 / LORD
    dict(ref=(14, 8, 4), lang='ko', en='sons', words=['아들', '자손']),   # 에스라 8:4 자손 / children·seed
    dict(ref=(14, 8, 5), lang='ko', en='sons', words=['아들이니', '자손']),   # 에스라 8:5 자손 / children·seed
    dict(ref=(14, 8, 6), lang='ko', en='sons', words=['아들', '자손']),   # 에스라 8:6 자손 / children·seed
    dict(ref=(14, 8, 7), lang='ko', en='sons', words=['아들', '자손']),   # 에스라 8:7 자손 / children·seed
    dict(ref=(14, 8, 8), lang='ko', en='sons', words=['아들', '자손']),   # 에스라 8:8 자손 / children·seed
    dict(ref=(14, 8, 9), lang='ko', en='sons', words=['아들', '자손']),   # 에스라 8:9 자손 / children·seed
    dict(ref=(14, 8, 10), lang='ko', en='sons', words=['아들이니', '자손']),   # 에스라 8:10 자손 / children·seed
    dict(ref=(14, 8, 11), lang='ko', en='sons', words=['아들', '자손']),   # 에스라 8:11 자손 / children·seed
    dict(ref=(14, 8, 12), lang='ko', en='sons', words=['아들', '자손']),   # 에스라 8:12 자손 / children·seed
    dict(ref=(14, 8, 15), lang='ko', en='sons', words=['중에', '자손이']),   # 에스라 8:15 자손 / children·seed
    dict(ref=(14, 9, 8), lang='ko', en='Lord', words=['같게', '여호와께서']),   # 에스라 9:8 여호와 / LORD
    dict(ref=(14, 9, 15), lang='ko', en='Lord', words=['여호와여']),   # 에스라 9:15 여호와 / LORD
    dict(ref=(14, 10, 2), lang='ko', en='sons', words=['자손']),   # 에스라 10:2 자손 / children·seed
    dict(ref=(15, 1, 5), lang='ko', en='Lord', words=['여호와']),   # 느헤미야 1:5 여호와 / LORD
    dict(ref=(15, 2, 18), lang='ko', en='words', words=['말씀을', '말이']),   # 느헤미야 2:18 말 / word
    dict(ref=(15, 5, 13), lang='ko', en='Lord', words=['여호와를']),   # 느헤미야 5:13 여호와 / LORD
    dict(ref=(15, 6, 6), lang='ko', en='words', words=['말하기를', '말과']),   # 느헤미야 6:6 말 / word
    dict(ref=(15, 8, 1), lang='ko', en='Lord', words=['여호와께서']),   # 느헤미야 8:1 여호와 / LORD
    dict(ref=(15, 9, 30), lang='ko', en='hand', words=['붙이시고도', '손에']),   # 느헤미야 9:30 손 / hand
    dict(ref=(15, 10, 9), lang='ko', en='sons', words=['자손']),   # 느헤미야 10:9 자손 / children·seed
    dict(ref=(15, 11, 7), lang='ko', en='sons', words=['아들이요', '자손은']),   # 느헤미야 11:7 자손 / children·seed
    dict(ref=(15, 11, 22), lang='ko', en='sons', words=['자손']),   # 느헤미야 11:22 자손 / children·seed
    dict(ref=(15, 12, 23), lang='ko', en='sons', words=['아들', '자손의']),   # 느헤미야 12:23 자손 / children·seed
    dict(ref=(15, 13, 16), lang='ko', en='men', words=['사람이']),   # 느헤미야 13:16 사람 / man
    dict(ref=(15, 13, 24), lang='ko', en='speech', words=['말이']),   # 느헤미야 13:24 말 / word
    dict(ref=(16, 1, 18), lang='ko', en='king', words=['왕후의', '왕의']),   # 에스더 1:18 왕 / king
    dict(ref=(17, 1, 6), lang='ko', en='Lord', words=['여호와']),   # 욥기 1:6 여호와 / LORD
    dict(ref=(17, 1, 9), lang='ko', en='Lord', words=['여호와께']),   # 욥기 1:9 여호와 / LORD
    dict(ref=(17, 2, 13), lang='ko', en='word', words=['말도']),   # 욥기 2:13 말 / word
    dict(ref=(17, 3, 14), lang='ko', en='kings', words=['임금들과']),   # 욥기 3:14 임금 / king
    dict(ref=(17, 5, 25), lang='ko', en='seed', words=['자손이']),   # 욥기 5:25 자손 / children·seed
    dict(ref=(17, 8, 19), lang='ko', en='way', words=['길의']),   # 욥기 8:19 길 / way·path
    dict(ref=(17, 12, 9), lang='ko', en='Lord', words=['중에', '여호와의']),   # 욥기 12:9 여호와 / LORD
    dict(ref=(17, 12, 20), lang='ko', en='speech', words=['말을']),   # 욥기 12:20 말 / word
    dict(ref=(17, 13, 17), lang='ko', en='speech', words=['말을']),   # 욥기 13:17 말 / word
    dict(ref=(17, 16, 4), lang='ko', en='words', words=['말을']),   # 욥기 16:4 말 / word
    dict(ref=(17, 18, 2), lang='ko', en='words', words=['말을']),   # 욥기 18:2 말 / word
    dict(ref=(17, 21, 2), lang='ko', en='speech', words=['말을']),   # 욥기 21:2 말 / word
    dict(ref=(17, 21, 8), lang='ko', en='seed', words=['씨가', '자손이']),   # 욥기 21:8 자손 / children·seed
    dict(ref=(17, 23, 13), lang='ko', en='mind', words=['뜻이', '마음에']),   # 욥기 23:13 마음 / heart
    dict(ref=(17, 30, 5), lang='ko', en='men', words=['사람']),   # 욥기 30:5 사람 / man
    dict(ref=(17, 31, 7), lang='ko', en='heart', words=['눈을', '마음이']),   # 욥기 31:7 마음 / heart
    dict(ref=(17, 34, 3), lang='ko', en='words', words=['말을']),   # 욥기 34:3 말 / word
    dict(ref=(17, 34, 35), lang='ko', en='words', words=['말하니', '말이']),   # 욥기 34:35 말 / word
    dict(ref=(17, 37, 10), lang='ko', en='waters', words=['물의']),   # 욥기 37:10 물 / water
    dict(ref=(17, 37, 19), lang='ko', en='speech', words=['말을']),   # 욥기 37:19 말 / word
    dict(ref=(17, 38, 20), lang='ko', en='house', words=['집의']),   # 욥기 38:20 집 / house
    dict(ref=(17, 41, 3), lang='ko', en='words', words=['유순한', '말로']),   # 욥기 41:3 말 / word
    dict(ref=(17, 42, 7), lang='ko', en='words', words=['말씀을', '말']),   # 욥기 42:7 말 / word
    dict(ref=(17, 42, 11), lang='ko', en='Lord', words=['알던', '여호와께서']),   # 욥기 42:11 여호와 / LORD
    dict(ref=(18, 1, 2), lang='ko', en='Lord', words=['여호와의']),   # 시편 1:2 여호와 / LORD
    dict(ref=(18, 2, 7), lang='ko', en='Lord', words=['이르시되', '여호와께서']),   # 시편 2:7 여호와 / LORD
    dict(ref=(18, 3, 1), lang='ko', en='Lord', words=['여호와여']),   # 시편 3:1 여호와 / LORD
    dict(ref=(18, 4, 6), lang='ko', en='Lord', words=['얼굴을', '여호와여']),   # 시편 4:6 여호와 / LORD
    dict(ref=(18, 5, 3), lang='ko', en='Lord', words=['여호와여']),   # 시편 5:3 여호와 / LORD
    dict(ref=(18, 6, 1), lang='ko', en='Lord', words=['여호와여']),   # 시편 6:1 여호와 / LORD
    dict(ref=(18, 6, 3), lang='ko', en='Lord', words=['여호와여']),   # 시편 6:3 여호와 / LORD
    dict(ref=(18, 9, 10), lang='ko', en='Lord', words=['여호와여']),   # 시편 9:10 여호와 / LORD
    dict(ref=(18, 9, 19), lang='ko', en='Lord', words=['여호와여']),   # 시편 9:19 여호와 / LORD
    dict(ref=(18, 10, 1), lang='ko', en='Lord', words=['여호와여']),   # 시편 10:1 여호와 / LORD
    dict(ref=(18, 12, 7), lang='ko', en='Lord', words=['여호와여']),   # 시편 12:7 여호와 / LORD
    dict(ref=(18, 14, 4), lang='ko', en='Lord', words=['여호와를']),   # 시편 14:4 여호와 / LORD
    dict(ref=(18, 14, 6), lang='ko', en='Lord', words=['여호와는']),   # 시편 14:6 여호와 / LORD
    dict(ref=(18, 14, 7), lang='ko', en='Lord', words=['여호와께서']),   # 시편 14:7 여호와 / LORD
    dict(ref=(18, 17, 6), lang='ko', en='speech', words=['말을']),   # 시편 17:6 말 / word
    dict(ref=(18, 17, 13), lang='ko', en='Lord', words=['여호와여']),   # 시편 17:13 여호와 / LORD
    dict(ref=(18, 18, 1), lang='ko', en='words', words=['말로']),   # 시편 18:1 말 / word
    dict(ref=(18, 18, 6), lang='ko', en='Lord', words=['여호와께']),   # 시편 18:6 여호와 / LORD
    dict(ref=(18, 18, 11), lang='ko', en='waters', words=['물의']),   # 시편 18:11 물 / water
    dict(ref=(18, 18, 49), lang='ko', en='Lord', words=['이러므로', '여호와여']),   # 시편 18:49 여호와 / LORD
    dict(ref=(18, 19, 14), lang='ko', en='Lord', words=['앞에', '여호와여']),   # 시편 19:14 여호와 / LORD
    dict(ref=(18, 22, 8), lang='ko', en='Lord', words=['여호와께']),   # 시편 22:8 여호와 / LORD
    dict(ref=(18, 22, 19), lang='ko', en='Lord', words=['여호와여']),   # 시편 22:19 여호와 / LORD
    dict(ref=(18, 24, 1), lang='ko', en='Lord', words=['여호와의']),   # 시편 24:1 여호와 / LORD
    dict(ref=(18, 25, 4), lang='ko', en='Lord', words=['여호와여']),   # 시편 25:4 여호와 / LORD
    dict(ref=(18, 25, 11), lang='ko', en='Lord', words=['여호와여']),   # 시편 25:11 여호와 / LORD
    dict(ref=(18, 26, 6), lang='ko', en='Lord', words=['여호와여']),   # 시편 26:6 여호와 / LORD
    dict(ref=(18, 27, 6), lang='ko', en='Lord', words=['여호와를']),   # 시편 27:6 여호와 / LORD
    dict(ref=(18, 27, 7), lang='ko', en='Lord', words=['여호와여']),   # 시편 27:7 여호와 / LORD
    dict(ref=(18, 27, 8), lang='ko', en='Lord', words=['하실', '여호와여']),   # 시편 27:8 여호와 / LORD
    dict(ref=(18, 27, 10), lang='ko', en='Lord', words=['여호와는']),   # 시편 27:10 여호와 / LORD
    dict(ref=(18, 28, 4), lang='ko', en='hands', words=['손의']),   # 시편 28:4 손 / hand
    dict(ref=(18, 31, 1), lang='ko', en='Lord', words=['여호와여']),   # 시편 31:1 여호와 / LORD
    dict(ref=(18, 31, 6), lang='ko', en='Lord', words=['여호와를']),   # 시편 31:6 여호와 / LORD
    dict(ref=(18, 31, 9), lang='ko', en='Lord', words=['여호와여']),   # 시편 31:9 여호와 / LORD
    dict(ref=(18, 31, 14), lang='ko', en='Lord', words=['여호와여']),   # 시편 31:14 여호와 / LORD
    dict(ref=(18, 33, 22), lang='ko', en='Lord', words=['여호와여']),   # 시편 33:22 여호와 / LORD
    dict(ref=(18, 35, 6), lang='ko', en='Lord', words=['여호와의']),   # 시편 35:6 여호와 / LORD
    dict(ref=(18, 36, 8), lang='ko', en='house', words=['집의']),   # 시편 36:8 집 / house
    dict(ref=(18, 37, 20), lang='ko', en='Lord', words=['여호와의']),   # 시편 37:20 여호와 / LORD
    dict(ref=(18, 37, 24), lang='ko', en='Lord', words=['여호와께서']),   # 시편 37:24 여호와 / LORD
    dict(ref=(18, 37, 34), lang='ko', en='Lord', words=['여호와를']),   # 시편 37:34 여호와 / LORD
    dict(ref=(18, 39, 12), lang='ko', en='Lord', words=['여호와여']),   # 시편 39:12 여호와 / LORD
    dict(ref=(18, 40, 3), lang='ko', en='Lord', words=['여호와를']),   # 시편 40:3 여호와 / LORD
    dict(ref=(18, 41, 10), lang='ko', en='Lord', words=['여호와여']),   # 시편 41:10 여호와 / LORD
    dict(ref=(18, 48, 8), lang='ko', en='Lord', words=['대로', '여호와의']),   # 시편 48:8 여호와 / LORD
    dict(ref=(18, 49, 13), lang='ko', en='sayings', words=['말을']),   # 시편 49:13 말 / word
    dict(ref=(18, 54, 6), lang='ko', en='Lord', words=['여호와여']),   # 시편 54:6 여호와 / LORD
    dict(ref=(18, 55, 16), lang='ko', en='Lord', words=['여호와께서']),   # 시편 55:16 여호와 / LORD
    dict(ref=(18, 59, 8), lang='ko', en='Lord', words=['여호와여']),   # 시편 59:8 여호와 / LORD
    dict(ref=(18, 69, 31), lang='ko', en='Lord', words=['여호와를']),   # 시편 69:31 여호와 / LORD
    dict(ref=(18, 70, 5), lang='ko', en='Lord', words=['여호와여']),   # 시편 70:5 여호와 / LORD
    dict(ref=(18, 78, 2), lang='ko', en='sayings', words=['말을']),   # 시편 78:2 말 / word
    dict(ref=(18, 79, 6), lang='ko', en='name', words=['부르지', '이름을']),   # 시편 79:6 이름 / name
    dict(ref=(18, 80, 17), lang='ko', en='son', words=['인자의']),   # 시편 80:17 인자 / son of man
    dict(ref=(18, 80, 18), lang='ko', en='name', words=['부르리이다', '이름을']),   # 시편 80:18 이름 / name
    dict(ref=(18, 80, 19), lang='ko', en='Lord', words=['여호와여']),   # 시편 80:19 여호와 / LORD
    dict(ref=(18, 83, 16), lang='ko', en='Lord', words=['여호와여']),   # 시편 83:16 여호와 / LORD
    dict(ref=(18, 84, 3), lang='ko', en='Lord', words=['여호와여']),   # 시편 84:3 여호와 / LORD
    dict(ref=(18, 85, 7), lang='ko', en='Lord', words=['여호와여']),   # 시편 85:7 여호와 / LORD
    dict(ref=(18, 86, 17), lang='ko', en='Lord', words=['여호와여']),   # 시편 86:17 여호와 / LORD
    dict(ref=(18, 88, 13), lang='ko', en='Lord', words=['여호와여']),   # 시편 88:13 여호와 / LORD
    dict(ref=(18, 88, 14), lang='ko', en='Lord', words=['여호와여']),   # 시편 88:14 여호와 / LORD
    dict(ref=(18, 89, 5), lang='ko', en='Lord', words=['여호와여']),   # 시편 89:5 여호와 / LORD
    dict(ref=(18, 89, 15), lang='ko', en='Lord', words=['얼굴', '여호와여']),   # 시편 89:15 여호와 / LORD
    dict(ref=(18, 89, 18), lang='ko', en='Lord', words=['여호와께']),   # 시편 89:18 여호와 / LORD
    dict(ref=(18, 89, 51), lang='ko', en='Lord', words=['여호와여']),   # 시편 89:51 여호와 / LORD
    dict(ref=(18, 90, 13), lang='ko', en='Lord', words=['여호와여']),   # 시편 90:13 여호와 / LORD
    dict(ref=(18, 91, 9), lang='ko', en='Lord', words=['여호와는']),   # 시편 91:9 여호와 / LORD
    dict(ref=(18, 93, 5), lang='ko', en='Lord', words=['여호와여']),   # 시편 93:5 여호와 / LORD
    dict(ref=(18, 95, 6), lang='ko', en='Lord', words=['지으신', '여호와']),   # 시편 95:6 여호와 / LORD
    dict(ref=(18, 99, 6), lang='ko', en='Lord', words=['여호와께']),   # 시편 99:6 여호와 / LORD
    dict(ref=(18, 99, 8), lang='ko', en='Lord', words=['여호와']),   # 시편 99:8 여호와 / LORD
    dict(ref=(18, 100, 3), lang='ko', en='God', words=['하나님이신']),   # 시편 100:3 하나님 / God
    dict(ref=(18, 102, 12), lang='ko', en='Lord', words=['여호와여']),   # 시편 102:12 여호와 / LORD
    dict(ref=(18, 102, 16), lang='ko', en='Lord', words=['여호와께서']),   # 시편 102:16 여호와 / LORD
    dict(ref=(18, 105, 21), lang='ko', en='house', words=['집의']),   # 시편 105:21 집 / house
    dict(ref=(18, 106, 34), lang='ko', en='Lord', words=['여호와의']),   # 시편 106:34 여호와 / LORD
    dict(ref=(18, 113, 2), lang='ko', en='Lord', words=['여호와의']),   # 시편 113:2 여호와 / LORD
    dict(ref=(18, 113, 3), lang='ko', en='Lord', words=['여호와의']),   # 시편 113:3 여호와 / LORD
    dict(ref=(18, 115, 1), lang='ko', en='Lord', words=['여호와여']),   # 시편 115:1 여호와 / LORD
    dict(ref=(18, 115, 15), lang='ko', en='Lord', words=['지으신', '여호와께']),   # 시편 115:15 여호와 / LORD
    dict(ref=(18, 116, 1), lang='ko', en='Lord', words=['여호와께서']),   # 시편 116:1 여호와 / LORD
    dict(ref=(18, 116, 13), lang='ko', en='name', words=['부르며', '이름을']),   # 시편 116:13 이름 / name
    dict(ref=(18, 116, 16), lang='ko', en='Lord', words=['여호와여']),   # 시편 116:16 여호와 / LORD
    dict(ref=(18, 118, 9), lang='ko', en='Lord', words=['방백들을', '여호와께']),   # 시편 118:9 여호와 / LORD
    dict(ref=(18, 118, 20), lang='ko', en='Lord', words=['여호와의']),   # 시편 118:20 여호와 / LORD
    dict(ref=(18, 119, 1), lang='ko', en='Lord', words=['여호와의']),   # 시편 119:1 여호와 / LORD
    dict(ref=(18, 119, 33), lang='ko', en='Lord', words=['여호와여']),   # 시편 119:33 여호와 / LORD
    dict(ref=(18, 119, 42), lang='ko', en='word', words=['말씀을', '말이']),   # 시편 119:42 말 / word
    dict(ref=(18, 119, 65), lang='ko', en='Lord', words=['여호와여']),   # 시편 119:65 여호와 / LORD
    dict(ref=(18, 119, 126), lang='ko', en='Lord', words=['여호와의']),   # 시편 119:126 여호와 / LORD
    dict(ref=(18, 119, 159), lang='ko', en='Lord', words=['여호와여']),   # 시편 119:159 여호와 / LORD
    dict(ref=(18, 122, 5), lang='ko', en='house', words=['집의']),   # 시편 122:5 집 / house
    dict(ref=(18, 123, 2), lang='ko', en='Lord', words=['같이', '여호와']),   # 시편 123:2 여호와 / LORD
    dict(ref=(18, 124, 8), lang='ko', en='Lord', words=['지으신', '여호와의']),   # 시편 124:8 여호와 / LORD
    dict(ref=(18, 125, 4), lang='ko', en='hearts', words=['마음이']),   # 시편 125:4 마음 / heart
    dict(ref=(18, 125, 5), lang='ko', en='Lord', words=['여호와께서']),   # 시편 125:5 여호와 / LORD
    dict(ref=(18, 126, 4), lang='ko', en='Lord', words=['같이', '여호와여']),   # 시편 126:4 여호와 / LORD
    dict(ref=(18, 128, 4), lang='ko', en='Lord', words=['이같이', '여호와를']),   # 시편 128:4 여호와 / LORD
    dict(ref=(18, 132, 2), lang='ko', en='Lord', words=['여호와께']),   # 시편 132:2 여호와 / LORD
    dict(ref=(18, 133, 3), lang='ko', en='Lord', words=['같도다', '여호와께서']),   # 시편 133:3 여호와 / LORD
    dict(ref=(18, 136, 2), lang='ko', en='God', words=['신에', '하나님께']),   # 시편 136:2 하나님 / God
    dict(ref=(18, 138, 4), lang='ko', en='Lord', words=['여호와여']),   # 시편 138:4 여호와 / LORD
    dict(ref=(18, 140, 4), lang='ko', en='Lord', words=['여호와여']),   # 시편 140:4 여호와 / LORD
    dict(ref=(18, 140, 12), lang='ko', en='Lord', words=['여호와는']),   # 시편 140:12 여호와 / LORD
    dict(ref=(18, 141, 3), lang='ko', en='Lord', words=['여호와여']),   # 시편 141:3 여호와 / LORD
    dict(ref=(18, 143, 11), lang='ko', en='Lord', words=['여호와여']),   # 시편 143:11 여호와 / LORD
    dict(ref=(18, 144, 5), lang='ko', en='Lord', words=['여호와여']),   # 시편 144:5 여호와 / LORD
    dict(ref=(18, 145, 1), lang='ko', en='king', words=['왕이신']),   # 시편 145:1 왕 / king
    dict(ref=(19, 4, 10), lang='ko', en='sayings', words=['말을']),   # 잠언 4:10 말 / word
    dict(ref=(19, 5, 7), lang='ko', en='words', words=['입의', '말을']),   # 잠언 5:7 말 / word
    dict(ref=(19, 16, 11), lang='ko', en='Lord', words=['여호와의']),   # 잠언 16:11 여호와 / LORD
    dict(ref=(19, 17, 7), lang='ko', en='speech', words=['말을']),   # 잠언 17:7 말 / word
    dict(ref=(19, 19, 3), lang='ko', en='Lord', words=['여호와를']),   # 잠언 19:3 여호와 / LORD
    dict(ref=(19, 21, 30), lang='ko', en='Lord', words=['여호와를']),   # 잠언 21:30 여호와 / LORD
    dict(ref=(19, 21, 31), lang='ko', en='Lord', words=['여호와께']),   # 잠언 21:31 여호와 / LORD
    dict(ref=(19, 22, 11), lang='ko', en='king', words=['임금이']),   # 잠언 22:11 임금 / king
    dict(ref=(19, 23, 9), lang='ko', en='words', words=['말을']),   # 잠언 23:9 말 / word
    dict(ref=(19, 25, 11), lang='ko', en='word', words=['말은']),   # 잠언 25:11 말 / word
    dict(ref=(19, 27, 8), lang='ko', en='man', words=['같으니라', '사람은']),   # 잠언 27:8 사람 / man
    dict(ref=(19, 29, 26), lang='ko', en='Lord', words=['여호와께로']),   # 잠언 29:26 여호와 / LORD
    dict(ref=(20, 3, 14), lang='ko', en='men', words=['사람으로']),   # 전도서 3:14 사람 / man
    dict(ref=(20, 4, 6), lang='ko', en='hands', words=['손에']),   # 전도서 4:6 손 / hand
    dict(ref=(20, 5, 9), lang='ko', en='king', words=['왕도']),   # 전도서 5:9 왕 / king
    dict(ref=(20, 7, 7), lang='ko', en='man', words=['사람의']),   # 전도서 7:7 사람 / man
    dict(ref=(20, 7, 21), lang='ko', en='words', words=['말을']),   # 전도서 7:21 말 / word
    dict(ref=(20, 9, 3), lang='ko', en='men', words=['인생의', '사람의']),   # 전도서 9:3 사람 / man
    dict(ref=(20, 9, 14), lang='ko', en='king', words=['임금이']),   # 전도서 9:14 임금 / king
    dict(ref=(20, 10, 13), lang='ko', en='words', words=['말의']),   # 전도서 10:13 말 / word
    dict(ref=(22, 1, 18), lang='ko', en='Lord', words=['여호와께서']),   # 이사야 1:18 여호와 / LORD
    dict(ref=(22, 2, 5), lang='ko', en='Lord', words=['여호와의']),   # 이사야 2:5 여호와 / LORD
    dict(ref=(22, 2, 10), lang='ko', en='Lord', words=['여호와의']),   # 이사야 2:10 여호와 / LORD
    dict(ref=(22, 2, 12), lang='ko', en='Lord', words=['여호와의']),   # 이사야 2:12 여호와 / LORD
    dict(ref=(22, 2, 19), lang='ko', en='Lord', words=['여호와께서']),   # 이사야 2:19 여호와 / LORD
    dict(ref=(22, 2, 21), lang='ko', en='Lord', words=['여호와께서']),   # 이사야 2:21 여호와 / LORD
    dict(ref=(22, 3, 8), lang='ko', en='Lord', words=['여호와를']),   # 이사야 3:8 여호와 / LORD
    dict(ref=(22, 4, 2), lang='ko', en='Lord', words=['여호와의']),   # 이사야 4:2 여호와 / LORD
    dict(ref=(22, 5, 12), lang='ko', en='Lord', words=['여호와의']),   # 이사야 5:12 여호와 / LORD
    dict(ref=(22, 5, 24), lang='ko', en='Lord', words=['여호와의']),   # 이사야 5:24 여호와 / LORD
    dict(ref=(22, 6, 5), lang='ko', en='Lord', words=['여호와이신']),   # 이사야 6:5 여호와 / LORD
    dict(ref=(22, 7, 12), lang='ko', en='Lord', words=['여호와를']),   # 이사야 7:12 여호와 / LORD
    dict(ref=(22, 8, 10), lang='ko', en='word', words=['말을']),   # 이사야 8:10 말 / word
    dict(ref=(22, 8, 11), lang='ko', en='saying', words=['가라사대', '말']),   # 이사야 8:11 말 / word
    dict(ref=(22, 12, 1), lang='ko', en='Lord', words=['전에는', '여호와여']),   # 이사야 12:1 여호와 / LORD
    dict(ref=(22, 12, 2), lang='ko', en='Lord', words=['주', '여호와는']),   # 이사야 12:2 여호와 / LORD
    dict(ref=(22, 12, 4), lang='ko', en='Lord', words=['여호와께']),   # 이사야 12:4 여호와 / LORD
    dict(ref=(22, 13, 13), lang='ko', en='Lord', words=['여호와가']),   # 이사야 13:13 여호와 / LORD
    dict(ref=(22, 13, 18), lang='ko', en='men', words=['사람이']),   # 이사야 13:18 사람 / man
    dict(ref=(22, 14, 2), lang='ko', en='land', words=['본토에', '땅에서']),   # 이사야 14:2 땅 / land·earth
    dict(ref=(22, 14, 23), lang='ko', en='Lord', words=['여호와의']),   # 이사야 14:23 여호와 / LORD
    dict(ref=(22, 17, 3), lang='ko', en='Lord', words=['같이', '여호와의']),   # 이사야 17:3 여호와 / LORD
    dict(ref=(22, 17, 12), lang='ko', en='waters', words=['물의']),   # 이사야 17:12 물 / water
    dict(ref=(22, 17, 13), lang='ko', en='waters', words=['물의']),   # 이사야 17:13 물 / water
    dict(ref=(22, 19, 12), lang='ko', en='Lord', words=['여호와께서']),   # 이사야 19:12 여호와 / LORD
    dict(ref=(22, 19, 16), lang='ko', en='Lord', words=['여호와의']),   # 이사야 19:16 여호와 / LORD
    dict(ref=(22, 19, 17), lang='ko', en='Lord', words=['되리니', '여호와께서']),   # 이사야 19:17 여호와 / LORD
    dict(ref=(22, 21, 10), lang='ko', en='Lord', words=['여호와께']),   # 이사야 21:10 여호와 / LORD
    dict(ref=(22, 21, 14), lang='ko', en='land', words=['땅의']),   # 이사야 21:14 땅 / land·earth
    dict(ref=(22, 22, 21), lang='ko', en='house', words=['힘', '집의']),   # 이사야 22:21 집 / house
    dict(ref=(22, 22, 24), lang='ko', en='house', words=['집의']),   # 이사야 22:24 집 / house
    dict(ref=(22, 24, 23), lang='ko', en='Lord', words=['것임이니라', '여호와께서']),   # 이사야 24:23 여호와 / LORD
    dict(ref=(22, 26, 13), lang='ko', en='Lord', words=['여호와']),   # 이사야 26:13 여호와 / LORD
    dict(ref=(22, 26, 17), lang='ko', en='Lord', words=['앞에', '여호와여']),   # 이사야 26:17 여호와 / LORD
    dict(ref=(22, 27, 13), lang='ko', en='Lord', words=['여호와께']),   # 이사야 27:13 여호와 / LORD
    dict(ref=(22, 28, 2), lang='ko', en='waters', words=['물의']),   # 이사야 28:2 물 / water
    dict(ref=(22, 28, 14), lang='ko', en='Lord', words=['이러므로', '여호와의']),   # 이사야 28:14 여호와 / LORD
    dict(ref=(22, 28, 21), lang='ko', en='Lord', words=['같이#1', '여호와께서']),   # 이사야 28:21 여호와 / LORD
    dict(ref=(22, 28, 23), lang='ko', en='speech', words=['말을']),   # 이사야 28:23 말 / word
    dict(ref=(22, 30, 9), lang='ko', en='Lord', words=['여호와의']),   # 이사야 30:9 여호와 / LORD
    dict(ref=(22, 30, 12), lang='ko', en='word', words=['말씀하시되', '말을']),   # 이사야 30:12 말 / word
    dict(ref=(22, 30, 29), lang='ko', en='Lord', words=['같이#1', '여호와의']),   # 이사야 30:29 여호와 / LORD
    dict(ref=(22, 31, 1), lang='ko', en='Lord', words=['여호와를']),   # 이사야 31:1 여호와 / LORD
    dict(ref=(22, 32, 7), lang='ko', en='words', words=['거짓말로', '말을']),   # 이사야 32:7 말 / word
    dict(ref=(22, 33, 19), lang='ko', en='speech', words=['방언이', '말이']),   # 이사야 33:19 말 / word
    dict(ref=(22, 34, 2), lang='ko', en='Lord', words=['하셨은즉', '여호와께서']),   # 이사야 34:2 여호와 / LORD
    dict(ref=(22, 36, 7), lang='ko', en='Lord', words=['여호와를']),   # 이사야 36:7 여호와 / LORD
    dict(ref=(22, 36, 20), lang='ko', en='Lord', words=['여호와가']),   # 이사야 36:20 여호와 / LORD
    dict(ref=(22, 37, 6), lang='ko', en='words', words=['말씀하시되', '말을']),   # 이사야 37:6 말 / word
    dict(ref=(22, 37, 9), lang='ko', en='saying', words=['말을']),   # 이사야 37:9 말 / word
    dict(ref=(22, 37, 19), lang='ko', en='men', words=['손으로', '사람의']),   # 이사야 37:19 사람 / man
    dict(ref=(22, 38, 2), lang='ko', en='Lord', words=['여호와께']),   # 이사야 38:2 여호와 / LORD
    dict(ref=(22, 38, 3), lang='ko', en='Lord', words=['여호와여']),   # 이사야 38:3 여호와 / LORD
    dict(ref=(22, 39, 6), lang='ko', en='Lord', words=['말이니라', '여호와의']),   # 이사야 39:6 여호와 / LORD
    dict(ref=(22, 40, 2), lang='ko', en='Lord', words=['여호와의']),   # 이사야 40:2 여호와 / LORD
    dict(ref=(22, 40, 7), lang='ko', en='Lord', words=['여호와의']),   # 이사야 40:7 여호와 / LORD
    dict(ref=(22, 41, 8), lang='ko', en='seed', words=['자손아']),   # 이사야 41:8 자손 / children·seed
    dict(ref=(22, 41, 20), lang='ko', en='Lord', words=['여호와의']),   # 이사야 41:20 여호와 / LORD
    dict(ref=(22, 42, 19), lang='ko', en='Lord', words=['같이#1', '여호와의']),   # 이사야 42:19 여호와 / LORD
    dict(ref=(22, 44, 3), lang='ko', en='seed', words=['후손에게', '자손에게']),   # 이사야 44:3 자손 / children·seed
    dict(ref=(22, 44, 15), lang='ko', en='man', words=['사람이']),   # 이사야 44:15 사람 / man
    dict(ref=(22, 45, 8), lang='ko', en='Lord', words=['여호와가']),   # 이사야 45:8 여호와 / LORD
    dict(ref=(22, 45, 24), lang='ko', en='men', words=['사람들은']),   # 이사야 45:24 사람 / man
    dict(ref=(22, 49, 4), lang='ko', en='Lord', words=['여호와께']),   # 이사야 49:4 여호와 / LORD
    dict(ref=(22, 49, 15), lang='ko', en='son', words=['아들을']),   # 이사야 49:15 아들 / son
    dict(ref=(22, 49, 26), lang='ko', en='Lord', words=['같이', '여호와는']),   # 이사야 49:26 여호와 / LORD
    dict(ref=(22, 51, 12), lang='ko', en='son', words=['인자를']),   # 이사야 51:12 인자 / son of man
    dict(ref=(22, 54, 6), lang='ko', en='Lord', words=['같이', '여호와께서']),   # 이사야 54:6 여호와 / LORD
    dict(ref=(22, 54, 8), lang='ko', en='Lord', words=['여호와의']),   # 이사야 54:8 여호와 / LORD
    dict(ref=(22, 55, 13), lang='ko', en='Lord', words=['되며', '여호와의']),   # 이사야 55:13 여호와 / LORD
    dict(ref=(22, 58, 8), lang='ko', en='Lord', words=['같이', '여호와의']),   # 이사야 58:8 여호와 / LORD
    dict(ref=(22, 58, 13), lang='ko', en='Lord', words=['행치#1', '여호와의']),   # 이사야 58:13 여호와 / LORD
    dict(ref=(22, 58, 13), lang='ko', en='words', words=['말을']),   # 이사야 58:13 말 / word
    dict(ref=(22, 59, 21), lang='ko', en='words', words=['말씀이니라', '말이']),   # 이사야 59:21 말 / word
    dict(ref=(22, 62, 4), lang='ko', en='Lord', words=['여호와께서']),   # 이사야 62:4 여호와 / LORD
    dict(ref=(22, 62, 9), lang='ko', en='Lord', words=['여호와를']),   # 이사야 62:9 여호와 / LORD
    dict(ref=(22, 63, 14), lang='ko', en='Lord', words=['같이', '여호와의']),   # 이사야 63:14 여호와 / LORD
    dict(ref=(22, 63, 16), lang='ko', en='Lord', words=['여호와여']),   # 이사야 63:16 여호와 / LORD
    dict(ref=(22, 64, 9), lang='ko', en='Lord', words=['여호와여']),   # 이사야 64:9 여호와 / LORD
    dict(ref=(22, 64, 12), lang='ko', en='Lord', words=['여호와여']),   # 이사야 64:12 여호와 / LORD
    dict(ref=(22, 65, 25), lang='ko', en='Lord', words=['여호와의']),   # 이사야 65:25 여호와 / LORD
    dict(ref=(22, 66, 2), lang='ko', en='word', words=['말을']),   # 이사야 66:2 말 / word
    dict(ref=(22, 66, 17), lang='ko', en='Lord', words=['들어가서', '여호와의']),   # 이사야 66:17 여호와 / LORD
    dict(ref=(22, 66, 22), lang='ko', en='Lord', words=['같이', '여호와가']),   # 이사야 66:22 여호와 / LORD
    dict(ref=(23, 1, 8), lang='ko', en='Lord', words=['여호와의']),   # 예레미야 1:8 여호와 / LORD
    dict(ref=(23, 1, 15), lang='ko', en='Lord', words=['여호와가']),   # 예레미야 1:15 여호와 / LORD
    dict(ref=(23, 2, 9), lang='ko', en='Lord', words=['말이니라', '여호와의']),   # 예레미야 2:9 여호와 / LORD
    dict(ref=(23, 2, 17), lang='ko', en='Lord', words=['여호와가']),   # 예레미야 2:17 여호와 / LORD
    dict(ref=(23, 2, 37), lang='ko', en='Lord', words=['이는', '여호와가']),   # 예레미야 2:37 여호와 / LORD
    dict(ref=(23, 3, 10), lang='ko', en='Lord', words=['여호와의']),   # 예레미야 3:10 여호와 / LORD
    dict(ref=(23, 4, 17), lang='ko', en='Lord', words=['같이', '여호와의']),   # 예레미야 4:17 여호와 / LORD
    dict(ref=(23, 5, 10), lang='ko', en='Lord', words=['여호와의']),   # 예레미야 5:10 여호와 / LORD
    dict(ref=(23, 5, 13), lang='ko', en='word', words=['말씀이']),   # 예레미야 5:13 말씀 / word
    dict(ref=(23, 5, 16), lang='ko', en='men', words=['사람들은']),   # 예레미야 5:16 사람 / man
    dict(ref=(23, 6, 15), lang='ko', en='Lord', words=['여호와의']),   # 예레미야 6:15 여호와 / LORD
    dict(ref=(23, 6, 30), lang='ko', en='Lord', words=['될', '여호와가']),   # 예레미야 6:30 여호와 / LORD
    dict(ref=(23, 7, 27), lang='ko', en='words', words=['말을']),   # 예레미야 7:27 말 / word
    dict(ref=(23, 7, 28), lang='ko', en='Lord', words=['여호와의']),   # 예레미야 7:28 여호와 / LORD
    dict(ref=(23, 7, 32), lang='ko', en='Lord', words=['말하노라', '여호와가']),   # 예레미야 7:32 여호와 / LORD
    dict(ref=(23, 8, 3), lang='ko', en='Lord', words=['여호와의']),   # 예레미야 8:3 여호와 / LORD
    dict(ref=(23, 8, 6), lang='ko', en='saying', words=['말']),   # 예레미야 8:6 말 / word
    dict(ref=(23, 8, 12), lang='ko', en='Lord', words=['여호와의']),   # 예레미야 8:12 여호와 / LORD
    dict(ref=(23, 9, 20), lang='ko', en='Lord', words=['여호와의']),   # 예레미야 9:20 여호와 / LORD
    dict(ref=(23, 10, 6), lang='ko', en='Lord', words=['인하여', '여호와여']),   # 예레미야 10:6 여호와 / LORD
    dict(ref=(23, 10, 23), lang='ko', en='Lord', words=['여호와여']),   # 예레미야 10:23 여호와 / LORD
    dict(ref=(23, 10, 25), lang='ko', en='name', words=['이름으로']),   # 예레미야 10:25 이름 / name
    dict(ref=(23, 11, 2), lang='ko', en='words', words=['말을']),   # 예레미야 11:2 말 / word
    dict(ref=(23, 11, 3), lang='ko', en='words', words=['말씀하시되', '말을']),   # 예레미야 11:3 말 / word
    dict(ref=(23, 11, 4), lang='ko', en='land', words=['되겠고', '땅에서']),   # 예레미야 11:4 땅 / land·earth
    dict(ref=(23, 11, 5), lang='ko', en='Lord', words=['여호와여']),   # 예레미야 11:5 여호와 / LORD
    dict(ref=(23, 12, 1), lang='ko', en='Lord', words=['자가', '여호와여']),   # 예레미야 12:1 여호와 / LORD
    dict(ref=(23, 12, 6), lang='ko', en='words', words=['말을']),   # 예레미야 12:6 말 / word
    dict(ref=(23, 13, 5), lang='ko', en='Lord', words=['여호와께서']),   # 예레미야 13:5 여호와 / LORD
    dict(ref=(23, 13, 11), lang='ko', en='Lord', words=['같이', '여호와가']),   # 예레미야 13:11 여호와 / LORD
    dict(ref=(23, 13, 12), lang='ko', en='word', words=['말씀에', '말로']),   # 예레미야 13:12 말 / word
    dict(ref=(23, 13, 14), lang='ko', en='Lord', words=['하라', '여호와의']),   # 예레미야 13:14 여호와 / LORD
    dict(ref=(23, 13, 17), lang='ko', en='Lord', words=['인하여#1', '여호와의']),   # 예레미야 13:17 여호와 / LORD
    dict(ref=(23, 14, 7), lang='ko', en='Lord', words=['여호와여']),   # 예레미야 14:7 여호와 / LORD
    dict(ref=(23, 14, 9), lang='ko', en='Lord', words=['같으시며', '여호와여']),   # 예레미야 14:9 여호와 / LORD
    dict(ref=(23, 14, 9), lang='ko', en='name', words=['일컬음을', '이름으로']),   # 예레미야 14:9 이름 / name
    dict(ref=(23, 14, 22), lang='ko', en='Lord', words=['여호와여']),   # 예레미야 14:22 여호와 / LORD
    dict(ref=(23, 15, 15), lang='ko', en='Lord', words=['여호와여']),   # 예레미야 15:15 여호와 / LORD
    dict(ref=(23, 15, 20), lang='ko', en='Lord', words=['여호와의']),   # 예레미야 15:20 여호와 / LORD
    dict(ref=(23, 16, 10), lang='ko', en='words', words=['말로']),   # 예레미야 16:10 말 / word
    dict(ref=(23, 16, 11), lang='ko', en='Lord', words=['여호와께서']),   # 예레미야 16:11 여호와 / LORD
    dict(ref=(23, 16, 19), lang='ko', en='Lord', words=['여호와']),   # 예레미야 16:19 여호와 / LORD
    dict(ref=(23, 17, 14), lang='ko', en='Lord', words=['여호와여']),   # 예레미야 17:14 여호와 / LORD
    dict(ref=(23, 18, 6), lang='ko', en='Lord', words=['같이#1', '여호와가']),   # 예레미야 18:6 여호와 / LORD
    dict(ref=(23, 18, 11), lang='ko', en='saying', words=['이르기를', '말씀에']),   # 예레미야 18:11 말씀 / word
    dict(ref=(23, 19, 2), lang='ko', en='words', words=['말을']),   # 예레미야 19:2 말 / word
    dict(ref=(23, 19, 12), lang='ko', en='Lord', words=['여호와가']),   # 예레미야 19:12 여호와 / LORD
    dict(ref=(23, 19, 15), lang='ko', en='words', words=['말씀하시되', '말을']),   # 예레미야 19:15 말 / word
    dict(ref=(23, 20, 7), lang='ko', en='Lord', words=['되니', '여호와여']),   # 예레미야 20:7 여호와 / LORD
    dict(ref=(23, 20, 8), lang='ko', en='Lord', words=['여호와의']),   # 예레미야 20:8 여호와 / LORD
    dict(ref=(23, 21, 7), lang='ko', en='Lord', words=['말씀하시되', '여호와께서']),   # 예레미야 21:7 여호와 / LORD
    dict(ref=(23, 22, 9), lang='ko', en='Lord', words=['대답하기는', '여호와의']),   # 예레미야 22:9 여호와 / LORD
    dict(ref=(23, 23, 9), lang='ko', en='Lord', words=['여호와와']),   # 예레미야 23:9 여호와 / LORD
    dict(ref=(23, 23, 12), lang='ko', en='Lord', words=['되고', '여호와의']),   # 예레미야 23:12 여호와 / LORD
    dict(ref=(23, 23, 16), lang='ko', en='words', words=['말씀하시되', '말을']),   # 예레미야 23:16 말 / word
    dict(ref=(23, 23, 25), lang='ko', en='saying', words=['말에']),   # 예레미야 23:25 말 / word
    dict(ref=(23, 23, 29), lang='ko', en='Lord', words=['말하노라', '여호와가']),   # 예레미야 23:29 여호와 / LORD
    dict(ref=(23, 23, 29), lang='ko', en='word', words=['말하노라', '말이']),   # 예레미야 23:29 말 / word
    dict(ref=(23, 23, 30), lang='ko', en='words', words=['말을']),   # 예레미야 23:30 말 / word
    dict(ref=(23, 24, 8), lang='ko', en='Lord', words=['같이', '여호와가']),   # 예레미야 24:8 여호와 / LORD
    dict(ref=(23, 25, 8), lang='ko', en='words', words=['말하노라', '말을']),   # 예레미야 25:8 말 / word
    dict(ref=(23, 25, 28), lang='ko', en='Lord', words=['여호와의']),   # 예레미야 25:28 여호와 / LORD
    dict(ref=(23, 25, 30), lang='ko', en='Lord', words=['여호와께서']),   # 예레미야 25:30 여호와 / LORD
    dict(ref=(23, 25, 36), lang='ko', en='Lord', words=['인도자들의', '여호와가']),   # 예레미야 25:36 여호와 / LORD
    dict(ref=(23, 26, 7), lang='ko', en='words', words=['말을']),   # 예레미야 26:7 말 / word
    dict(ref=(23, 26, 8), lang='ko', en='saying', words=['말씀을']),   # 예레미야 26:8 말씀 / word
    dict(ref=(23, 26, 12), lang='ko', en='Lord', words=['여호와께서']),   # 예레미야 26:12 여호와 / LORD
    dict(ref=(23, 26, 15), lang='ko', en='words', words=['말을']),   # 예레미야 26:15 말 / word
    dict(ref=(23, 26, 16), lang='ko', en='Lord', words=['여호와의']),   # 예레미야 26:16 여호와 / LORD
    dict(ref=(23, 27, 13), lang='ko', en='Lord', words=['같이', '여호와께서']),   # 예레미야 27:13 여호와 / LORD
    dict(ref=(23, 27, 22), lang='ko', en='Lord', words=['후에', '여호와의']),   # 예레미야 27:22 여호와 / LORD
    dict(ref=(23, 28, 3), lang='ko', en='Lord', words=['여호와의']),   # 예레미야 28:3 여호와 / LORD
    dict(ref=(23, 28, 4), lang='ko', en='Lord', words=['여호와의']),   # 예레미야 28:4 여호와 / LORD
    dict(ref=(23, 28, 13), lang='ko', en='Lord', words=['이르기를', '여호와의']),   # 예레미야 28:13 여호와 / LORD
    dict(ref=(23, 28, 13), lang='ko', en='saying', words=['이르기를', '말씀에']),   # 예레미야 28:13 말씀 / word
    dict(ref=(23, 29, 7), lang='ko', en='Lord', words=['한', '여호와께']),   # 예레미야 29:7 여호와 / LORD
    dict(ref=(23, 29, 9), lang='ko', en='Lord', words=['여호와의']),   # 예레미야 29:9 여호와 / LORD
    dict(ref=(23, 29, 10), lang='ko', en='word', words=['말하노라', '말을']),   # 예레미야 29:10 말 / word
    dict(ref=(23, 29, 15), lang='ko', en='Lord', words=['여호와께서']),   # 예레미야 29:15 여호와 / LORD
    dict(ref=(23, 29, 16), lang='ko', en='Lord', words=['여호와께서']),   # 예레미야 29:16 여호와 / LORD
    dict(ref=(23, 29, 19), lang='ko', en='words', words=['말을']),   # 예레미야 29:19 말 / word
    dict(ref=(23, 29, 23), lang='ko', en='Lord', words=['여호와의']),   # 예레미야 29:23 여호와 / LORD
    dict(ref=(23, 31, 6), lang='ko', en='Lord', words=['여호와께로']),   # 예레미야 31:6 여호와 / LORD
    dict(ref=(23, 31, 12), lang='ko', en='Lord', words=['여호와의']),   # 예레미야 31:12 여호와 / LORD
    dict(ref=(23, 31, 20), lang='ko', en='Lord', words=['위하여', '여호와의']),   # 예레미야 31:20 여호와 / LORD
    dict(ref=(23, 31, 23), lang='ko', en='speech', words=['말하노라', '말을']),   # 예레미야 31:23 말 / word
    dict(ref=(23, 31, 32), lang='ko', en='Lord', words=['여호와가']),   # 예레미야 31:32 여호와 / LORD
    dict(ref=(23, 32, 3), lang='ko', en='saying', words=['말하고', '말씀에']),   # 예레미야 32:3 말씀 / word
    dict(ref=(23, 32, 30), lang='ko', en='Lord', words=['여호와가']),   # 예레미야 32:30 여호와 / LORD
    dict(ref=(23, 32, 34), lang='ko', en='name', words=['더럽게', '이름으로']),   # 예레미야 32:34 이름 / name
    dict(ref=(23, 32, 43), lang='ko', en='man', words=['사람이나', '사람들이']),   # 예레미야 32:43 사람 / man
    dict(ref=(23, 33, 24), lang='ko', en='Lord', words=['여호와께서']),   # 예레미야 33:24 여호와 / LORD
    dict(ref=(23, 34, 14), lang='ko', en='man', words=['각기', '사람이']),   # 예레미야 34:14 사람 / man
    dict(ref=(23, 35, 6), lang='ko', en='sons', words=['자손은']),   # 예레미야 35:6 자손 / children·seed
    dict(ref=(23, 35, 13), lang='ko', en='words', words=['말씀에', '말을']),   # 예레미야 35:13 말 / word
    dict(ref=(23, 35, 14), lang='ko', en='sons', words=['자손에게']),   # 예레미야 35:14 자손 / children·seed
    dict(ref=(23, 35, 16), lang='ko', en='sons', words=['아들', '자손은']),   # 예레미야 35:16 자손 / children·seed
    dict(ref=(23, 36, 2), lang='ko', en='words', words=['말을']),   # 예레미야 36:2 말 / word
    dict(ref=(23, 36, 4), lang='ko', en='words', words=['말씀을']),   # 예레미야 36:4 말씀 / word
    dict(ref=(23, 36, 5), lang='ko', en='Lord', words=['여호와의']),   # 예레미야 36:5 여호와 / LORD
    dict(ref=(23, 36, 6), lang='ko', en='words', words=['말씀을']),   # 예레미야 36:6 말씀 / word
    dict(ref=(23, 38, 16), lang='ko', en='hand', words=['손에']),   # 예레미야 38:16 손 / hand
    dict(ref=(23, 39, 17), lang='ko', en='hand', words=['그#1', '손에']),   # 예레미야 39:17 손 / hand
    dict(ref=(23, 39, 18), lang='ko', en='Lord', words=['되리니', '여호와의']),   # 예레미야 39:18 여호와 / LORD
    dict(ref=(23, 42, 19), lang='ko', en='Lord', words=['말씀에', '여호와께서']),   # 예레미야 42:19 여호와 / LORD
    dict(ref=(23, 44, 16), lang='ko', en='word', words=['말을']),   # 예레미야 44:16 말 / word
    dict(ref=(23, 44, 29), lang='ko', en='words', words=['말이']),   # 예레미야 44:29 말 / word
    dict(ref=(23, 46, 15), lang='ko', en='Lord', words=['여호와께서']),   # 예레미야 46:15 여호와 / LORD
    dict(ref=(23, 46, 26), lang='ko', en='Lord', words=['여호와의']),   # 예레미야 46:26 여호와 / LORD
    dict(ref=(23, 47, 7), lang='ko', en='Lord', words=['여호와께서']),   # 예레미야 47:7 여호와 / LORD
    dict(ref=(23, 48, 8), lang='ko', en='Lord', words=['여호와의']),   # 예레미야 48:8 여호와 / LORD
    dict(ref=(23, 48, 42), lang='ko', en='Lord', words=['여호와를']),   # 예레미야 48:42 여호와 / LORD
    dict(ref=(23, 48, 44), lang='ko', en='Lord', words=['여호와의']),   # 예레미야 48:44 여호와 / LORD
    dict(ref=(23, 49, 1), lang='ko', en='sons', words=['자손에']),   # 예레미야 49:1 자손 / children·seed
    dict(ref=(23, 49, 5), lang='ko', en='man', words=['사람이']),   # 예레미야 49:5 사람 / man
    dict(ref=(23, 49, 6), lang='ko', en='Lord', words=['말이니라', '여호와의']),   # 예레미야 49:6 여호와 / LORD
    dict(ref=(23, 49, 16), lang='ko', en='Lord', words=['여호와의']),   # 예레미야 49:16 여호와 / LORD
    dict(ref=(23, 49, 18), lang='ko', en='Lord', words=['같이', '여호와가']),   # 예레미야 49:18 여호와 / LORD
    dict(ref=(23, 49, 18), lang='ko', en='son', words=['여호와가', '인자가']),   # 예레미야 49:18 인자 / son of man
    dict(ref=(23, 49, 31), lang='ko', en='Lord', words=['여호와가']),   # 예레미야 49:31 여호와 / LORD
    dict(ref=(23, 49, 32), lang='ko', en='Lord', words=['여호와의']),   # 예레미야 49:32 여호와 / LORD
    dict(ref=(23, 49, 33), lang='ko', en='son', words=['인자가']),   # 예레미야 49:33 인자 / son of man
    dict(ref=(23, 50, 10), lang='ko', en='Lord', words=['여호와의']),   # 예레미야 50:10 여호와 / LORD
    dict(ref=(23, 50, 14), lang='ko', en='Lord', words=['여호와께']),   # 예레미야 50:14 여호와 / LORD
    dict(ref=(23, 50, 24), lang='ko', en='Lord', words=['깨닫지', '여호와와']),   # 예레미야 50:24 여호와 / LORD
    dict(ref=(23, 50, 40), lang='ko', en='Lord', words=['같이', '여호와가']),   # 예레미야 50:40 여호와 / LORD
    dict(ref=(23, 51, 43), lang='ko', en='son', words=['되었으니', '인자가']),   # 예레미야 51:43 인자 / son of man
    dict(ref=(23, 51, 51), lang='ko', en='Lord', words=['여호와의']),   # 예레미야 51:51 여호와 / LORD
    dict(ref=(23, 51, 52), lang='ko', en='Lord', words=['여호와께서']),   # 예레미야 51:52 여호와 / LORD
    dict(ref=(23, 51, 55), lang='ko', en='Lord', words=['여호와께서']),   # 예레미야 51:55 여호와 / LORD
    dict(ref=(23, 51, 55), lang='ko', en='waters', words=['물의']),   # 예레미야 51:55 물 / water
    dict(ref=(23, 51, 56), lang='ko', en='Lord', words=['여호와는']),   # 예레미야 51:56 여호와 / LORD
    dict(ref=(23, 51, 62), lang='ko', en='Lord', words=['여호와여']),   # 예레미야 51:62 여호와 / LORD
    dict(ref=(24, 1, 9), lang='ko', en='Lord', words=['여호와여']),   # 예레미야애가 1:9 여호와 / LORD
    dict(ref=(24, 1, 12), lang='ko', en='Lord', words=['없는가', '여호와께서']),   # 예레미야애가 1:12 여호와 / LORD
    dict(ref=(24, 1, 17), lang='ko', en='Lord', words=['여호와께서']),   # 예레미야애가 1:17 여호와 / LORD
    dict(ref=(24, 1, 20), lang='ko', en='Lord', words=['여호와여']),   # 예레미야애가 1:20 여호와 / LORD
    dict(ref=(24, 2, 6), lang='ko', en='Lord', words=['같이', '여호와께서']),   # 예레미야애가 2:6 여호와 / LORD
    dict(ref=(24, 2, 22), lang='ko', en='Lord', words=['같이', '여호와께서']),   # 예레미야애가 2:22 여호와 / LORD
    dict(ref=(24, 5, 1), lang='ko', en='Lord', words=['것을', '여호와여']),   # 예레미야애가 5:1 여호와 / LORD
    dict(ref=(24, 5, 19), lang='ko', en='Lord', words=['여호와여']),   # 예레미야애가 5:19 여호와 / LORD
    dict(ref=(24, 5, 21), lang='ko', en='Lord', words=['여호와여']),   # 예레미야애가 5:21 여호와 / LORD
    dict(ref=(25, 1, 28), lang='ko', en='Lord', words=['같으니', '여호와의']),   # 에스겔 1:28 여호와 / LORD
    dict(ref=(25, 2, 1), lang='ko', en='Son', words=['인자야']),   # 에스겔 2:1 인자 / son of man
    dict(ref=(25, 2, 3), lang='ko', en='Son', words=['자손', '인자야']),   # 에스겔 2:3 인자 / son of man
    dict(ref=(25, 2, 6), lang='ko', en='son', words=['인자야']),   # 에스겔 2:6 인자 / son of man
    dict(ref=(25, 2, 8), lang='ko', en='son', words=['인자야']),   # 에스겔 2:8 인자 / son of man
    dict(ref=(25, 3, 1), lang='ko', en='Son', words=['인자야']),   # 에스겔 3:1 인자 / son of man
    dict(ref=(25, 3, 3), lang='ko', en='Son', words=['인자야']),   # 에스겔 3:3 인자 / son of man
    dict(ref=(25, 3, 4), lang='ko', en='Son', words=['인자야']),   # 에스겔 3:4 인자 / son of man
    dict(ref=(25, 3, 5), lang='ko', en='speech', words=['어려운', '말이']),   # 에스겔 3:5 말 / word
    dict(ref=(25, 3, 10), lang='ko', en='words', words=['말을']),   # 에스겔 3:10 말 / word
    dict(ref=(25, 3, 10), lang='ko', en='Son', words=['인자야']),   # 에스겔 3:10 인자 / son of man
    dict(ref=(25, 3, 17), lang='ko', en='Son', words=['인자야']),   # 에스겔 3:17 인자 / son of man
    dict(ref=(25, 3, 23), lang='ko', en='Lord', words=['여호와의']),   # 에스겔 3:23 여호와 / LORD
    dict(ref=(25, 3, 25), lang='ko', en='son', words=['인자야']),   # 에스겔 3:25 인자 / son of man
    dict(ref=(25, 4, 1), lang='ko', en='son', words=['인자야']),   # 에스겔 4:1 인자 / son of man
    dict(ref=(25, 4, 16), lang='ko', en='Son', words=['인자야']),   # 에스겔 4:16 인자 / son of man
    dict(ref=(25, 5, 1), lang='ko', en='son', words=['인자야']),   # 에스겔 5:1 인자 / son of man
    dict(ref=(25, 6, 2), lang='ko', en='Son', words=['인자야']),   # 에스겔 6:2 인자 / son of man
    dict(ref=(25, 7, 9), lang='ko', en='Lord', words=['여호와가']),   # 에스겔 7:9 여호와 / LORD
    dict(ref=(25, 7, 19), lang='ko', en='Lord', words=['여호와']),   # 에스겔 7:19 여호와 / LORD
    dict(ref=(25, 8, 5), lang='ko', en='Son', words=['인자야']),   # 에스겔 8:5 인자 / son of man
    dict(ref=(25, 8, 6), lang='ko', en='Son', words=['인자야']),   # 에스겔 8:6 인자 / son of man
    dict(ref=(25, 8, 8), lang='ko', en='Son', words=['인자야']),   # 에스겔 8:8 인자 / son of man
    dict(ref=(25, 8, 12), lang='ko', en='Son', words=['인자야']),   # 에스겔 8:12 인자 / son of man
    dict(ref=(25, 8, 15), lang='ko', en='son', words=['인자야']),   # 에스겔 8:15 인자 / son of man
    dict(ref=(25, 8, 17), lang='ko', en='son', words=['인자야']),   # 에스겔 8:17 인자 / son of man
    dict(ref=(25, 11, 2), lang='ko', en='Son', words=['인자야']),   # 에스겔 11:2 인자 / son of man
    dict(ref=(25, 11, 4), lang='ko', en='son', words=['인자야']),   # 에스겔 11:4 인자 / son of man
    dict(ref=(25, 11, 15), lang='ko', en='Son', words=['인자야']),   # 에스겔 11:15 인자 / son of man
    dict(ref=(25, 12, 2), lang='ko', en='Son', words=['인자야']),   # 에스겔 12:2 인자 / son of man
    dict(ref=(25, 12, 3), lang='ko', en='son', words=['인자야']),   # 에스겔 12:3 인자 / son of man
    dict(ref=(25, 12, 9), lang='ko', en='Son', words=['인자야']),   # 에스겔 12:9 인자 / son of man
    dict(ref=(25, 12, 18), lang='ko', en='Son', words=['인자야']),   # 에스겔 12:18 인자 / son of man
    dict(ref=(25, 12, 27), lang='ko', en='Son', words=['인자야']),   # 에스겔 12:27 인자 / son of man
    dict(ref=(25, 13, 2), lang='ko', en='Son', words=['인자야']),   # 에스겔 13:2 인자 / son of man
    dict(ref=(25, 14, 3), lang='ko', en='Son', words=['인자야']),   # 에스겔 14:3 인자 / son of man
    dict(ref=(25, 14, 13), lang='ko', en='Son', words=['인자야']),   # 에스겔 14:13 인자 / son of man
    dict(ref=(25, 15, 2), lang='ko', en='Son', words=['인자야']),   # 에스겔 15:2 인자 / son of man
    dict(ref=(25, 16, 2), lang='ko', en='Son', words=['인자야']),   # 에스겔 16:2 인자 / son of man
    dict(ref=(25, 16, 35), lang='ko', en='Lord', words=['그러므로', '여호와의']),   # 에스겔 16:35 여호와 / LORD
    dict(ref=(25, 16, 58), lang='ko', en='Lord', words=['여호와의']),   # 에스겔 16:58 여호와 / LORD
    dict(ref=(25, 17, 2), lang='ko', en='Son', words=['인자야']),   # 에스겔 17:2 인자 / son of man
    dict(ref=(25, 17, 18), lang='ko', en='hand', words=['손을']),   # 에스겔 17:18 손 / hand
    dict(ref=(25, 20, 4), lang='ko', en='son', words=['인자야']),   # 에스겔 20:4 인자 / son of man
    dict(ref=(25, 20, 5), lang='ko', en='saying', words=['말씀에']),   # 에스겔 20:5 말씀 / word
    dict(ref=(25, 20, 5), lang='ko', en='house', words=['집의']),   # 에스겔 20:5 집 / house
    dict(ref=(25, 20, 20), lang='ko', en='Lord', words=['되어', '여호와']),   # 에스겔 20:20 여호와 / LORD
    dict(ref=(25, 20, 46), lang='ko', en='Son', words=['인자야']),   # 에스겔 20:46 인자 / son of man
    dict(ref=(25, 21, 2), lang='ko', en='Son', words=['인자야']),   # 에스겔 21:2 인자 / son of man
    dict(ref=(25, 21, 9), lang='ko', en='Son', words=['인자야']),   # 에스겔 21:9 인자 / son of man
    dict(ref=(25, 21, 12), lang='ko', en='son', words=['인자야']),   # 에스겔 21:12 인자 / son of man
    dict(ref=(25, 21, 19), lang='ko', en='son', words=['인자야']),   # 에스겔 21:19 인자 / son of man
    dict(ref=(25, 21, 28), lang='ko', en='son', words=['인자야']),   # 에스겔 21:28 인자 / son of man
    dict(ref=(25, 21, 32), lang='ko', en='Lord', words=['될', '여호와가']),   # 에스겔 21:32 여호와 / LORD
    dict(ref=(25, 22, 2), lang='ko', en='son', words=['인자야']),   # 에스겔 22:2 인자 / son of man
    dict(ref=(25, 22, 14), lang='ko', en='Lord', words=['여호와가']),   # 에스겔 22:14 여호와 / LORD
    dict(ref=(25, 22, 18), lang='ko', en='Son', words=['인자야']),   # 에스겔 22:18 인자 / son of man
    dict(ref=(25, 22, 22), lang='ko', en='Lord', words=['같이', '여호와가']),   # 에스겔 22:22 여호와 / LORD
    dict(ref=(25, 22, 24), lang='ko', en='Son', words=['인자야']),   # 에스겔 22:24 인자 / son of man
    dict(ref=(25, 22, 28), lang='ko', en='saying', words=['말하지', '말씀이라']),   # 에스겔 22:28 말씀 / word
    dict(ref=(25, 23, 2), lang='ko', en='Son', words=['인자야']),   # 에스겔 23:2 인자 / son of man
    dict(ref=(25, 23, 12), lang='ko', en='men', words=['소년이었느니라', '사람을']),   # 에스겔 23:12 사람 / man
    dict(ref=(25, 23, 36), lang='ko', en='Son', words=['인자야']),   # 에스겔 23:36 인자 / son of man
    dict(ref=(25, 24, 2), lang='ko', en='Son', words=['인자야']),   # 에스겔 24:2 인자 / son of man
    dict(ref=(25, 24, 16), lang='ko', en='Son', words=['인자야']),   # 에스겔 24:16 인자 / son of man
    dict(ref=(25, 24, 25), lang='ko', en='minds', words=['생각하는', '마음의']),   # 에스겔 24:25 마음 / heart
    dict(ref=(25, 24, 25), lang='ko', en='son', words=['인자야']),   # 에스겔 24:25 인자 / son of man
    dict(ref=(25, 25, 2), lang='ko', en='Son', words=['인자야']),   # 에스겔 25:2 인자 / son of man
    dict(ref=(25, 26, 2), lang='ko', en='Son', words=['인자야']),   # 에스겔 26:2 인자 / son of man
    dict(ref=(25, 27, 11), lang='ko', en='men', words=['용사들은', '사람과']),   # 에스겔 27:11 사람 / man
    dict(ref=(25, 28, 2), lang='ko', en='Son', words=['인자야']),   # 에스겔 28:2 인자 / son of man
    dict(ref=(25, 28, 21), lang='ko', en='Son', words=['인자야']),   # 에스겔 28:21 인자 / son of man
    dict(ref=(25, 28, 25), lang='ko', en='land', words=['열방에', '고토', '땅에']),   # 에스겔 28:25 땅 / land·earth
    dict(ref=(25, 29, 2), lang='ko', en='Son', words=['인자야']),   # 에스겔 29:2 인자 / son of man
    dict(ref=(25, 30, 2), lang='ko', en='Son', words=['인자야']),   # 에스겔 30:2 인자 / son of man
    dict(ref=(25, 30, 21), lang='ko', en='Son', words=['인자야']),   # 에스겔 30:21 인자 / son of man
    dict(ref=(25, 31, 2), lang='ko', en='Son', words=['인자야']),   # 에스겔 31:2 인자 / son of man
    dict(ref=(25, 32, 2), lang='ko', en='Son', words=['인자야']),   # 에스겔 32:2 인자 / son of man
    dict(ref=(25, 33, 2), lang='ko', en='Son', words=['인자야']),   # 에스겔 33:2 인자 / son of man
    dict(ref=(25, 33, 7), lang='ko', en='son', words=['인자야']),   # 에스겔 33:7 인자 / son of man
    dict(ref=(25, 33, 12), lang='ko', en='son', words=['인자야']),   # 에스겔 33:12 인자 / son of man
    dict(ref=(25, 33, 24), lang='ko', en='man', words=['인자야', '사람이라도']),   # 에스겔 33:24 사람 / man
    dict(ref=(25, 33, 24), lang='ko', en='Son', words=['인자야']),   # 에스겔 33:24 인자 / son of man
    dict(ref=(25, 33, 30), lang='ko', en='son', words=['인자야']),   # 에스겔 33:30 인자 / son of man
    dict(ref=(25, 34, 2), lang='ko', en='Son', words=['인자야']),   # 에스겔 34:2 인자 / son of man
    dict(ref=(25, 35, 2), lang='ko', en='Son', words=['인자야']),   # 에스겔 35:2 인자 / son of man
    dict(ref=(25, 35, 12), lang='ko', en='saying', words=['말을']),   # 에스겔 35:12 말 / word
    dict(ref=(25, 36, 17), lang='ko', en='Son', words=['인자야']),   # 에스겔 36:17 인자 / son of man
    dict(ref=(25, 37, 3), lang='ko', en='Son', words=['인자야']),   # 에스겔 37:3 인자 / son of man
    dict(ref=(25, 37, 4), lang='ko', en='Lord', words=['여호와의']),   # 에스겔 37:4 여호와 / LORD
    dict(ref=(25, 37, 9), lang='ko', en='son', words=['인자야']),   # 에스겔 37:9 인자 / son of man
    dict(ref=(25, 37, 11), lang='ko', en='Son', words=['인자야']),   # 에스겔 37:11 인자 / son of man
    dict(ref=(25, 37, 16), lang='ko', en='son', words=['자손이라', '인자야']),   # 에스겔 37:16 인자 / son of man
    dict(ref=(25, 38, 2), lang='ko', en='Son', words=['인자야']),   # 에스겔 38:2 인자 / son of man
    dict(ref=(25, 38, 14), lang='ko', en='son', words=['인자야']),   # 에스겔 38:14 인자 / son of man
    dict(ref=(25, 39, 1), lang='ko', en='son', words=['인자야']),   # 에스겔 39:1 인자 / son of man
    dict(ref=(25, 40, 4), lang='ko', en='Son', words=['인자야']),   # 에스겔 40:4 인자 / son of man
    dict(ref=(25, 40, 46), lang='ko', en='Lord', words=['여호와께']),   # 에스겔 40:46 여호와 / LORD
    dict(ref=(25, 43, 7), lang='ko', en='Son', words=['인자야']),   # 에스겔 43:7 인자 / son of man
    dict(ref=(25, 43, 18), lang='ko', en='Son', words=['인자야']),   # 에스겔 43:18 인자 / son of man
    dict(ref=(25, 44, 5), lang='ko', en='Son', words=['인자야']),   # 에스겔 44:5 인자 / son of man
    dict(ref=(25, 45, 4), lang='ko', en='Lord', words=['여호와께']),   # 에스겔 45:4 여호와 / LORD
    dict(ref=(25, 45, 18), lang='ko', en='Lord', words=['여호와가']),   # 에스겔 45:18 여호와 / LORD
    dict(ref=(25, 46, 12), lang='ko', en='Lord', words=['여호와께']),   # 에스겔 46:12 여호와 / LORD
    dict(ref=(25, 46, 13), lang='ko', en='Lord', words=['여호와께']),   # 에스겔 46:13 여호와 / LORD
    dict(ref=(25, 47, 6), lang='ko', en='Son', words=['인자야']),   # 에스겔 47:6 인자 / son of man
    dict(ref=(25, 47, 22), lang='ko', en='country', words=['땅을']),   # 에스겔 47:22 땅 / land·earth
    dict(ref=(25, 48, 10), lang='ko', en='Lord', words=['여호와의']),   # 에스겔 48:10 여호와 / LORD
    dict(ref=(26, 1, 2), lang='ko', en='hand', words=['손에']),   # 다니엘 1:2 손 / hand
    dict(ref=(26, 3, 20), lang='ko', en='men', words=['사람을']),   # 다니엘 3:20 사람 / man
    dict(ref=(26, 3, 22), lang='ko', en='king', words=['왕의']),   # 다니엘 3:22 왕 / king
    dict(ref=(26, 3, 27), lang='ko', en='king', words=['왕의']),   # 다니엘 3:27 왕 / king
    dict(ref=(26, 3, 28), lang='ko', en='king', words=['왕의']),   # 다니엘 3:28 왕 / king
    dict(ref=(26, 5, 22), lang='ko', en='heart', words=['마음을']),   # 다니엘 5:22 마음 / heart
    dict(ref=(26, 5, 23), lang='ko', en='God', words=['하나님께는']),   # 다니엘 5:23 하나님 / God
    dict(ref=(26, 6, 10), lang='ko', en='God', words=['하나님께']),   # 다니엘 6:10 하나님 / God
    dict(ref=(26, 7, 13), lang='ko', en='Son', words=['인자']),   # 다니엘 7:13 인자 / son of man
    dict(ref=(26, 7, 25), lang='ko', en='words', words=['말로']),   # 다니엘 7:25 말 / word
    dict(ref=(26, 9, 18), lang='ko', en='name', words=['이름으로']),   # 다니엘 9:18 이름 / name
    dict(ref=(26, 10, 15), lang='ko', en='words', words=['말로']),   # 다니엘 10:15 말 / word
    dict(ref=(26, 11, 11), lang='ko', en='hand', words=['손에']),   # 다니엘 11:11 손 / hand
    dict(ref=(26, 11, 42), lang='ko', en='land', words=['것이므로', '땅도']),   # 다니엘 11:42 땅 / land·earth
    dict(ref=(27, 2, 20), lang='ko', en='Lord', words=['여호와를']),   # 호세아 2:20 여호와 / LORD
    dict(ref=(27, 3, 4), lang='ko', en='king', words=['왕도']),   # 호세아 3:4 왕 / king
    dict(ref=(27, 4, 16), lang='ko', en='Lord', words=['같이', '여호와께서']),   # 호세아 4:16 여호와 / LORD
    dict(ref=(27, 5, 4), lang='ko', en='Lord', words=['여호와를']),   # 호세아 5:4 여호와 / LORD
    dict(ref=(27, 8, 1), lang='ko', en='Lord', words=['여호와의']),   # 호세아 8:1 여호와 / LORD
    dict(ref=(27, 8, 10), lang='ko', en='king', words=['임금의']),   # 호세아 8:10 임금 / king
    dict(ref=(27, 9, 14), lang='ko', en='Lord', words=['여호와여']),   # 호세아 9:14 여호와 / LORD
    dict(ref=(27, 10, 3), lang='ko', en='Lord', words=['위하여', '여호와를']),   # 호세아 10:3 여호와 / LORD
    dict(ref=(27, 11, 5), lang='ko', en='king', words=['임금이']),   # 호세아 11:5 임금 / king
    dict(ref=(27, 11, 11), lang='ko', en='Lord', words=['같이#1', '여호와의']),   # 호세아 11:11 여호와 / LORD
    dict(ref=(27, 12, 2), lang='ko', en='Lord', words=['여호와께서']),   # 호세아 12:2 여호와 / LORD
    dict(ref=(27, 13, 15), lang='ko', en='Lord', words=['여호와의']),   # 호세아 13:15 여호와 / LORD
    dict(ref=(28, 2, 32), lang='ko', en='name', words=['이름을']),   # 요엘 2:32 이름 / name
    dict(ref=(28, 3, 11), lang='ko', en='Lord', words=['여호와여']),   # 요엘 3:11 여호와 / LORD
    dict(ref=(28, 3, 21), lang='ko', en='Lord', words=['여호와가']),   # 요엘 3:21 여호와 / LORD
    dict(ref=(29, 2, 11), lang='ko', en='Lord', words=['중에서#1', '여호와의']),   # 아모스 2:11 여호와 / LORD
    dict(ref=(29, 2, 11), lang='ko', en='men', words=['청년', '사람을']),   # 아모스 2:11 사람 / man
    dict(ref=(29, 4, 8), lang='ko', en='Lord', words=['여호와의']),   # 아모스 4:8 여호와 / LORD
    dict(ref=(29, 5, 14), lang='ko', en='Lord', words=['여호와께서']),   # 아모스 5:14 여호와 / LORD
    dict(ref=(29, 6, 10), lang='ko', en='Lord', words=['여호와의']),   # 아모스 6:10 여호와 / LORD
    dict(ref=(29, 6, 10), lang='ko', en='man', words=['사람의']),   # 아모스 6:10 사람 / man
    dict(ref=(29, 6, 14), lang='ko', en='Lord', words=['여호와께서']),   # 아모스 6:14 여호와 / LORD
    dict(ref=(29, 9, 7), lang='ko', en='Lord', words=['같지', '여호와께서']),   # 아모스 9:7 여호와 / LORD
    dict(ref=(29, 9, 15), lang='ko', en='Lord', words=['여호와의']),   # 아모스 9:15 여호와 / LORD
    dict(ref=(30, 1, 18), lang='ko', en='Lord', words=['여호와께서']),   # 오바댜 1:18 여호와 / LORD
    dict(ref=(30, 1, 21), lang='ko', en='Lord', words=['여호와께']),   # 오바댜 1:21 여호와 / LORD
    dict(ref=(31, 1, 10), lang='ko', en='Lord', words=['여호와의']),   # 요나 1:10 여호와 / LORD
    dict(ref=(31, 4, 2), lang='ko', en='God', words=['하나님이신']),   # 요나 4:2 하나님 / God
    dict(ref=(32, 1, 14), lang='ko', en='houses', words=['집들이']),   # 미가 1:14 집 / house
    dict(ref=(32, 2, 3), lang='ko', en='Lord', words=['하셨느니라', '여호와의']),   # 미가 2:3 여호와 / LORD
    dict(ref=(32, 2, 5), lang='ko', en='Lord', words=['자가', '여호와의']),   # 미가 2:5 여호와 / LORD
    dict(ref=(32, 2, 7), lang='ko', en='Lord', words=['이르기를', '여호와의']),   # 미가 2:7 여호와 / LORD
    dict(ref=(32, 6, 16), lang='ko', en='house', words=['집의']),   # 미가 6:16 집 / house
    dict(ref=(32, 7, 8), lang='ko', en='Lord', words=['되실', '여호와께서']),   # 미가 7:8 여호와 / LORD
    dict(ref=(32, 7, 17), lang='ko', en='Lord', words=['돌아와서', '여호와께로']),   # 미가 7:17 여호와 / LORD
    dict(ref=(34, 1, 13), lang='ko', en='man', words=['사람을']),   # 하박국 1:13 사람 / man
    dict(ref=(34, 3, 15), lang='ko', en='waters', words=['물의']),   # 하박국 3:15 물 / water
    dict(ref=(35, 1, 2), lang='ko', en='Lord', words=['여호와께서']),   # 스바냐 1:2 여호와 / LORD
    dict(ref=(35, 1, 3), lang='ko', en='Lord', words=['여호와의']),   # 스바냐 1:3 여호와 / LORD
    dict(ref=(35, 1, 17), lang='ko', en='Lord', words=['이는', '여호와께']),   # 스바냐 1:17 여호와 / LORD
    dict(ref=(35, 2, 7), lang='ko', en='Lord', words=['여호와가']),   # 스바냐 2:7 여호와 / LORD
    dict(ref=(35, 2, 8), lang='ko', en='children', words=['자손의']),   # 스바냐 2:8 자손 / children·seed
    dict(ref=(35, 2, 9), lang='ko', en='children', words=['자손은']),   # 스바냐 2:9 자손 / children·seed
    dict(ref=(35, 2, 10), lang='ko', en='Lord', words=['여호와의']),   # 스바냐 2:10 여호와 / LORD
    dict(ref=(35, 3, 20), lang='ko', en='Lord', words=['여호와의']),   # 스바냐 3:20 여호와 / LORD
    dict(ref=(36, 1, 9), lang='ko', en='Lord', words=['여호와가']),   # 학개 1:9 여호와 / LORD
    dict(ref=(36, 2, 14), lang='ko', en='Lord', words=['여호와의']),   # 학개 2:14 여호와 / LORD
    dict(ref=(36, 2, 15), lang='ko', en='Lord', words=['여호와의']),   # 학개 2:15 여호와 / LORD
    dict(ref=(36, 2, 18), lang='ko', en='Lord', words=['너희는', '여호와의']),   # 학개 2:18 여호와 / LORD
    dict(ref=(37, 1, 14), lang='ko', en='Lord', words=['여호와의']),   # 스가랴 1:14 여호와 / LORD
    dict(ref=(37, 1, 14), lang='ko', en='saying', words=['말씀에']),   # 스가랴 1:14 말씀 / word
    dict(ref=(37, 1, 17), lang='ko', en='saying', words=['이르기를', '말씀에']),   # 스가랴 1:17 말씀 / word
    dict(ref=(37, 7, 2), lang='ko', en='men', words=['사람이']),   # 스가랴 7:2 사람 / man
    dict(ref=(37, 7, 3), lang='ko', en='Lord', words=['여호와의']),   # 스가랴 7:3 여호와 / LORD
    dict(ref=(37, 7, 13), lang='ko', en='Lord', words=['여호와가']),   # 스가랴 7:13 여호와 / LORD
    dict(ref=(37, 8, 9), lang='ko', en='words', words=['말하노라', '말을']),   # 스가랴 8:9 말 / word
    dict(ref=(37, 9, 5), lang='ko', en='king', words=['임금이']),   # 스가랴 9:5 임금 / king
    dict(ref=(37, 10, 3), lang='ko', en='Lord', words=['여호와가']),   # 스가랴 10:3 여호와 / LORD
    dict(ref=(37, 10, 5), lang='ko', en='Lord', words=['같이', '여호와가']),   # 스가랴 10:5 여호와 / LORD
    dict(ref=(37, 11, 6), lang='ko', en='men', words=['각각', '사람을']),   # 스가랴 11:6 사람 / man
    dict(ref=(37, 11, 6), lang='ko', en='king', words=['임금의']),   # 스가랴 11:6 임금 / king
    dict(ref=(37, 12, 7), lang='ko', en='house', words=['집의']),   # 스가랴 12:7 집 / house
    dict(ref=(37, 13, 9), lang='ko', en='Lord', words=['여호와는']),   # 스가랴 13:9 여호와 / LORD
    dict(ref=(37, 14, 17), lang='ko', en='Lord', words=['여호와께']),   # 스가랴 14:17 여호와 / LORD
    dict(ref=(37, 14, 18), lang='ko', en='Lord', words=['그에게', '여호와께서']),   # 스가랴 14:18 여호와 / LORD
    dict(ref=(38, 1, 8), lang='ko', en='Lord', words=['여호와가']),   # 말라기 1:8 여호와 / LORD
    dict(ref=(38, 1, 9), lang='ko', en='Lord', words=['여호와가']),   # 말라기 1:9 여호와 / LORD
    dict(ref=(38, 1, 10), lang='ko', en='Lord', words=['여호와가']),   # 말라기 1:10 여호와 / LORD
    dict(ref=(38, 1, 11), lang='ko', en='Lord', words=['여호와가']),   # 말라기 1:11 여호와 / LORD
    dict(ref=(38, 1, 14), lang='ko', en='King', words=['임금이요']),   # 말라기 1:14 임금 / king
    dict(ref=(38, 2, 11), lang='ko', en='Lord', words=['행하였고', '여호와의']),   # 말라기 2:11 여호와 / LORD
    dict(ref=(38, 2, 14), lang='ko', en='Lord', words=['여호와께서']),   # 말라기 2:14 여호와 / LORD
    dict(ref=(38, 3, 3), lang='ko', en='Lord', words=['같이#1', '여호와께']),   # 말라기 3:3 여호와 / LORD
    dict(ref=(38, 3, 7), lang='ko', en='Lord', words=['여호와가']),   # 말라기 3:7 여호와 / LORD
    dict(ref=(38, 3, 10), lang='ko', en='Lord', words=['여호와가']),   # 말라기 3:10 여호와 / LORD
    dict(ref=(38, 3, 17), lang='ko', en='Lord', words=['여호와가']),   # 말라기 3:17 여호와 / LORD
    dict(ref=(38, 4, 1), lang='ko', en='Lord', words=['같은', '여호와가']),   # 말라기 4:1 여호와 / LORD
    dict(ref=(39, 1, 18), lang='ko', en='Christ', words=['그리스도의']),   # 마태복음 1:18 그리스도 / Christ
    dict(ref=(39, 1, 22), lang='ko', en='saying', words=['가라사대', '말씀을']),   # 마태복음 1:22 말씀 / word
    dict(ref=(39, 4, 14), lang='ko', en='saying', words=['일렀으되', '말씀을']),   # 마태복음 4:14 말씀 / word
    dict(ref=(39, 8, 17), lang='ko', en='saying', words=['말씀에']),   # 마태복음 8:17 말씀 / word
    dict(ref=(39, 9, 18), lang='ko', en='saying', words=['가로되', '말씀을']),   # 마태복음 9:18 말씀 / word
    dict(ref=(39, 12, 36), lang='ko', en='word', words=['말을']),   # 마태복음 12:36 말 / word
    dict(ref=(39, 16, 28), lang='ko', en='man', words=['사람']),   # 마태복음 16:28 사람 / man
    dict(ref=(39, 17, 12), lang='ko', en='man', words=['사람들이']),   # 마태복음 17:12 사람 / man
    dict(ref=(39, 20, 28), lang='ko', en='man', words=['사람의']),   # 마태복음 20:28 사람 / man
    dict(ref=(39, 21, 4), lang='ko', en='saying', words=['일렀으되', '말씀을']),   # 마태복음 21:4 말씀 / word
    dict(ref=(39, 21, 26), lang='ko', en='men', words=['사람에게로서라', '사람이']),   # 마태복음 21:26 사람 / man
    dict(ref=(39, 24, 45), lang='ko', en='household', words=['집']),   # 마태복음 24:45 집 / house
    dict(ref=(39, 27, 9), lang='ko', en='saying', words=['일렀으되', '말씀이']),   # 마태복음 27:9 말씀 / word
    dict(ref=(40, 5, 36), lang='ko', en='word', words=['말을']),   # 마가복음 5:36 말 / word
    dict(ref=(40, 8, 38), lang='ko', en='man', words=['사람을']),   # 마가복음 8:38 사람 / man
    dict(ref=(40, 9, 32), lang='ko', en='saying', words=['말씀을']),   # 마가복음 9:32 말씀 / word
    dict(ref=(40, 10, 45), lang='ko', en='man', words=['사람의']),   # 마가복음 10:45 사람 / man
    dict(ref=(40, 12, 26), lang='ko', en='saying', words=['말씀을']),   # 마가복음 12:26 말씀 / word
    dict(ref=(40, 13, 26), lang='ko', en='man', words=['사람들이']),   # 마가복음 13:26 사람 / man
    dict(ref=(41, 1, 65), lang='ko', en='sayings', words=['말이']),   # 누가복음 1:65 말 / word
    dict(ref=(41, 2, 51), lang='ko', en='sayings', words=['말을']),   # 누가복음 2:51 말 / word
    dict(ref=(41, 5, 21), lang='ko', en='saying', words=['가로되', '말을']),   # 누가복음 5:21 말 / word
    dict(ref=(41, 6, 17), lang='ko', en='people', words=['무리와', '백성도']),   # 누가복음 6:17 백성 / people
    dict(ref=(41, 7, 1), lang='ko', en='sayings', words=['말씀을']),   # 누가복음 7:1 말씀 / word
    dict(ref=(41, 8, 15), lang='ko', en='ground', words=['땅에']),   # 누가복음 8:15 땅 / land·earth
    dict(ref=(41, 8, 26), lang='ko', en='country', words=['땅에']),   # 누가복음 8:26 땅 / land·earth
    dict(ref=(41, 9, 26), lang='ko', en='man', words=['사람을']),   # 누가복음 9:26 사람 / man
    dict(ref=(41, 11, 30), lang='ko', en='man', words=['사람들에게']),   # 누가복음 11:30 사람 / man
    dict(ref=(41, 12, 10), lang='ko', en='word', words=['말로']),   # 누가복음 12:10 말 / word
    dict(ref=(41, 12, 42), lang='ko', en='household', words=['집']),   # 누가복음 12:42 집 / house
    dict(ref=(41, 18, 34), lang='ko', en='saying', words=['저희가', '이르신', '말씀이']),   # 누가복음 18:34 말씀 / word
    dict(ref=(41, 23, 3), lang='ko', en='saying', words=['가라사대', '말이']),   # 누가복음 23:3 말 / word
    dict(ref=(41, 24, 44), lang='ko', en='words', words=['말한', '말이']),   # 누가복음 24:44 말 / word
    dict(ref=(42, 3, 5), lang='ko', en='man', words=['사람이']),   # 요한복음 3:5 사람 / man
    dict(ref=(42, 5, 3), lang='ko', en='water', words=['물의']),   # 요한복음 5:3 물 / water
    dict(ref=(42, 6, 51), lang='ko', en='man', words=['사람이']),   # 요한복음 6:51 사람 / man
    dict(ref=(42, 6, 63), lang='ko', en='words', words=['말이']),   # 요한복음 6:63 말 / word
    dict(ref=(42, 7, 4), lang='ko', en='man', words=['사람이']),   # 요한복음 7:4 사람 / man
    dict(ref=(42, 7, 17), lang='ko', en='God', words=['하나님께로서', '하나님의']),   # 요한복음 7:17 하나님 / God
    dict(ref=(42, 7, 17), lang='ko', en='man', words=['사람이']),   # 요한복음 7:17 사람 / man
    dict(ref=(42, 8, 20), lang='ko', en='words', words=['말씀은']),   # 요한복음 8:20 말씀 / word
    dict(ref=(42, 8, 30), lang='ko', en='words', words=['말씀을']),   # 요한복음 8:30 말씀 / word
    dict(ref=(42, 8, 51), lang='ko', en='saying', words=['아니하리라', '말을']),   # 요한복음 8:51 말 / word
    dict(ref=(42, 8, 55), lang='ko', en='saying', words=['말씀을']),   # 요한복음 8:55 말씀 / word
    dict(ref=(42, 10, 35), lang='ko', en='God', words=['하나님의']),   # 요한복음 10:35 하나님 / God
    dict(ref=(42, 11, 9), lang='ko', en='man', words=['사람이']),   # 요한복음 11:9 사람 / man
    dict(ref=(42, 11, 10), lang='ko', en='man', words=['사람']),   # 요한복음 11:10 사람 / man
    dict(ref=(42, 12, 38), lang='ko', en='saying', words=['가로되', '말씀을']),   # 요한복음 12:38 말씀 / word
    dict(ref=(42, 14, 10), lang='ko', en='words', words=['말이']),   # 요한복음 14:10 말 / word
    dict(ref=(42, 15, 3), lang='ko', en='word', words=['말로']),   # 요한복음 15:3 말 / word
    dict(ref=(42, 16, 30), lang='ko', en='man', words=['사람의']),   # 요한복음 16:30 사람 / man
    dict(ref=(42, 17, 1), lang='ko', en='words', words=['말씀을']),   # 요한복음 17:1 말씀 / word
    dict(ref=(42, 18, 1), lang='ko', en='words', words=['말씀을']),   # 요한복음 18:1 말씀 / word
    dict(ref=(42, 18, 22), lang='ko', en='saying', words=['가로되', '하니', '말씀을']),   # 요한복음 18:22 말씀 / word
    dict(ref=(43, 2, 36), lang='ko', en='Christ', words=['그리스도가']),   # 사도행전 2:36 그리스도 / Christ
    dict(ref=(43, 9, 2), lang='ko', en='men', words=['사람을']),   # 사도행전 9:2 사람 / man
    dict(ref=(43, 11, 17), lang='ko', en='Christ', words=['그리스도를']),   # 사도행전 11:17 그리스도 / Christ
    dict(ref=(43, 13, 41), lang='ko', en='man', words=['사람들아', '사람이']),   # 사도행전 13:41 사람 / man
    dict(ref=(43, 14, 2), lang='ko', en='minds', words=['품게', '마음을']),   # 사도행전 14:2 마음 / heart
    dict(ref=(43, 20, 7), lang='ko', en='speech', words=['말을']),   # 사도행전 20:7 말 / word
    dict(ref=(43, 20, 21), lang='ko', en='Christ', words=['그리스도께']),   # 사도행전 20:21 그리스도 / Christ
    dict(ref=(43, 26, 25), lang='ko', en='words', words=['말을']),   # 사도행전 26:25 말 / word
    dict(ref=(43, 28, 15), lang='ko', en='God', words=['하나님께']),   # 사도행전 28:15 하나님 / God
    dict(ref=(43, 28, 25), lang='ko', en='word', words=['말씀하신', '말로']),   # 사도행전 28:25 말 / word
    dict(ref=(43, 28, 31), lang='ko', en='Christ', words=['그리스도께']),   # 사도행전 28:31 그리스도 / Christ
    dict(ref=(44, 1, 1), lang='ko', en='Christ', words=['그리스도의']),   # 로마서 1:1 그리스도 / Christ
    dict(ref=(44, 1, 8), lang='ko', en='God', words=['하나님께']),   # 로마서 1:8 하나님 / God
    dict(ref=(44, 3, 22), lang='ko', en='Christ', words=['그리스도를']),   # 로마서 3:22 그리스도 / Christ
    dict(ref=(44, 5, 15), lang='ko', en='Christ', words=['그리스도의']),   # 로마서 5:15 그리스도 / Christ
    dict(ref=(44, 12, 2), lang='ko', en='mind', words=['마음을']),   # 로마서 12:2 마음 / heart
    dict(ref=(44, 15, 16), lang='ko', en='Christ', words=['그리스도']),   # 로마서 15:16 그리스도 / Christ
    dict(ref=(44, 15, 18), lang='ko', en='word', words=['말과']),   # 로마서 15:18 말 / word
    dict(ref=(44, 16, 5), lang='ko', en='Christ', words=['그리스도께']),   # 로마서 16:5 그리스도 / Christ
    dict(ref=(44, 16, 18), lang='ko', en='Christ', words=['그리스도를']),   # 로마서 16:18 그리스도 / Christ
    dict(ref=(44, 16, 27), lang='ko', en='Christ', words=['그리스도로']),   # 로마서 16:27 그리스도 / Christ
    dict(ref=(45, 1, 4), lang='ko', en='Christ', words=['그리스도']),   # 고린도전서 1:4 그리스도 / Christ
    dict(ref=(45, 1, 9), lang='ko', en='Christ', words=['그리스도']),   # 고린도전서 1:9 그리스도 / Christ
    dict(ref=(45, 1, 10), lang='ko', en='mind', words=['마음과']),   # 고린도전서 1:10 마음 / heart
    dict(ref=(45, 1, 17), lang='ko', en='words', words=['하려#1', '말의']),   # 고린도전서 1:17 말 / word
    dict(ref=(45, 1, 30), lang='ko', en='Christ', words=['그리스도']),   # 고린도전서 1:30 그리스도 / Christ
    dict(ref=(45, 2, 13), lang='ko', en='words', words=['말로']),   # 고린도전서 2:13 말 / word
    dict(ref=(45, 14, 9), lang='ko', en='words', words=['듣기', '말을']),   # 고린도전서 14:9 말 / word
    dict(ref=(45, 14, 18), lang='ko', en='God', words=['하나님께']),   # 고린도전서 14:18 하나님 / God
    dict(ref=(45, 15, 31), lang='ko', en='Christ', words=['그리스도']),   # 고린도전서 15:31 그리스도 / Christ
    dict(ref=(45, 16, 24), lang='ko', en='Christ', words=['그리스도']),   # 고린도전서 16:24 그리스도 / Christ
    dict(ref=(46, 4, 5), lang='ko', en='Christ', words=['그리스도']),   # 고린도후서 4:5 그리스도 / Christ
    dict(ref=(46, 7, 4), lang='ko', en='speech', words=['말이']),   # 고린도후서 7:4 말 / word
    dict(ref=(46, 11, 2), lang='ko', en='Christ', words=['그리스도께']),   # 고린도후서 11:2 그리스도 / Christ
    dict(ref=(46, 12, 4), lang='ko', en='words', words=['말을']),   # 고린도후서 12:4 말 / word
    dict(ref=(46, 13, 5), lang='ko', en='Christ', words=['그리스도께서']),   # 고린도후서 13:5 그리스도 / Christ
    dict(ref=(47, 3, 14), lang='ko', en='Christ', words=['그리스도']),   # 갈라디아서 3:14 그리스도 / Christ
    dict(ref=(47, 3, 29), lang='ko', en='Christ', words=['그리스도께']),   # 갈라디아서 3:29 그리스도 / Christ
    dict(ref=(47, 5, 6), lang='ko', en='Christ', words=['그리스도']),   # 갈라디아서 5:6 그리스도 / Christ
    dict(ref=(48, 5, 20), lang='ko', en='God', words=['하나님께']),   # 에베소서 5:20 하나님 / God
    dict(ref=(48, 6, 5), lang='ko', en='Christ', words=['그리스도께']),   # 에베소서 6:5 그리스도 / Christ
    dict(ref=(49, 1, 6), lang='ko', en='Christ', words=['그리스도']),   # 빌립보서 1:6 그리스도 / Christ
    dict(ref=(49, 1, 8), lang='ko', en='Christ', words=['그리스도의']),   # 빌립보서 1:8 그리스도 / Christ
    dict(ref=(49, 2, 3), lang='ko', en='mind', words=['마음으로']),   # 빌립보서 2:3 마음 / heart
    dict(ref=(49, 3, 3), lang='ko', en='Christ', words=['그리스도']),   # 빌립보서 3:3 그리스도 / Christ
    dict(ref=(50, 2, 4), lang='ko', en='words', words=['속이지', '말로']),   # 골로새서 2:4 말 / word
    dict(ref=(51, 1, 8), lang='ko', en='word', words=['말씀이', '말도']),   # 데살로니가전서 1:8 말 / word
    dict(ref=(51, 5, 23), lang='ko', en='Christ', words=['그리스도']),   # 데살로니가전서 5:23 그리스도 / Christ
    dict(ref=(53, 5, 21), lang='ko', en='Christ', words=['그리스도']),   # 디모데전서 5:21 그리스도 / Christ
    dict(ref=(53, 6, 5), lang='ko', en='minds', words=['마음이']),   # 디모데전서 6:5 마음 / heart
    dict(ref=(54, 1, 10), lang='ko', en='Christ', words=['그리스도']),   # 디모데후서 1:10 그리스도 / Christ
    dict(ref=(54, 2, 3), lang='ko', en='Christ', words=['그리스도']),   # 디모데후서 2:3 그리스도 / Christ
    dict(ref=(54, 3, 12), lang='ko', en='Christ', words=['그리스도']),   # 디모데후서 3:12 그리스도 / Christ
    dict(ref=(54, 4, 1), lang='ko', en='Christ', words=['그리스도']),   # 디모데후서 4:1 그리스도 / Christ
    dict(ref=(54, 4, 19), lang='ko', en='household', words=['집에']),   # 디모데후서 4:19 집 / house
    dict(ref=(56, 1, 4), lang='ko', en='God', words=['하나님께']),   # 빌레몬서 1:4 하나님 / God
    dict(ref=(56, 1, 6), lang='ko', en='Christ', words=['그리스도께']),   # 빌레몬서 1:6 그리스도 / Christ
    dict(ref=(57, 13, 21), lang='ko', en='Christ', words=['그리스도로']),   # 히브리서 13:21 그리스도 / Christ
    dict(ref=(58, 1, 1), lang='ko', en='Christ', words=['그리스도의']),   # 야고보서 1:1 그리스도 / Christ
    dict(ref=(59, 1, 2), lang='ko', en='Christ', words=['그리스도의']),   # 베드로전서 1:2 그리스도 / Christ
    dict(ref=(59, 3, 8), lang='ko', en='mind', words=['체휼하며', '겸손하며', '마음을']),   # 베드로전서 3:8 마음 / heart
    dict(ref=(59, 3, 21), lang='ko', en='Christ', words=['그리스도의']),   # 베드로전서 3:21 그리스도 / Christ
    dict(ref=(59, 5, 10), lang='ko', en='Christ', words=['그리스도']),   # 베드로전서 5:10 그리스도 / Christ
    dict(ref=(60, 1, 8), lang='ko', en='Christ', words=['그리스도를']),   # 베드로후서 1:8 그리스도 / Christ
    dict(ref=(60, 2, 18), lang='ko', en='words', words=['말을']),   # 베드로후서 2:18 말 / word
    dict(ref=(60, 3, 1), lang='ko', en='minds', words=['마음을']),   # 베드로후서 3:1 마음 / heart
    dict(ref=(60, 3, 6), lang='ko', en='water', words=['물의']),   # 베드로후서 3:6 물 / water
    dict(ref=(60, 3, 18), lang='ko', en='Christ', words=['그리스도의']),   # 베드로후서 3:18 그리스도 / Christ
    dict(ref=(61, 5, 20), lang='ko', en='Christ', words=['그리스도']),   # 요한일서 5:20 그리스도 / Christ
    dict(ref=(64, 1, 16), lang='ko', en='words', words=['말을']),   # 유다서 1:16 말 / word
    dict(ref=(64, 1, 17), lang='ko', en='words', words=['말을']),   # 유다서 1:17 말 / word
    dict(ref=(65, 1, 1), lang='ko', en='Christ', words=['그리스도의']),   # 요한계시록 1:1 그리스도 / Christ
    dict(ref=(65, 14, 7), lang='ko', en='waters', words=['물들의']),   # 요한계시록 14:7 물 / water
    dict(ref=(65, 14, 15), lang='ko', en='earth', words=['땅에']),   # 요한계시록 14:15 땅 / land·earth
    dict(ref=(65, 22, 6), lang='ko', en='sayings', words=['말하기를', '말은']),   # 요한계시록 22:6 말 / word
    dict(ref=(65, 22, 7), lang='ko', en='sayings', words=['말씀을']),   # 요한계시록 22:7 말씀 / word
    dict(ref=(65, 22, 9), lang='ko', en='sayings', words=['말하기를', '말을']),   # 요한계시록 22:9 말 / word
    dict(ref=(65, 22, 10), lang='ko', en='sayings', words=['말씀을']),   # 요한계시록 22:10 말씀 / word

    # ---- 시편 131편 ----
    dict(ref=(18, 131, 1), lang='ko', en='my', words=['내#1']),
    dict(ref=(18, 131, 1), lang='ko', en='mine', words=['내#2']),
    dict(ref=(18, 131, 1), lang='ko', en='not', words=['아니하고']),
    dict(ref=(18, 131, 1), lang='ko', en='nor', words=['아니하오며']),
    dict(ref=(18, 131, 1), lang='ko', en='neither', words=['아니하나이다']),
    dict(ref=(18, 131, 1), lang='ko', en='I', words=['내가']),
    dict(ref=(18, 131, 1), lang='ko', en='exercise', words=['힘쓰지']),
    dict(ref=(18, 131, 1), lang='ko', en='myself', words=['힘쓰지']),
    dict(ref=(18, 131, 1), lang='ko', en='great', words=['큰']),
    dict(ref=(18, 131, 1), lang='ko', en='matters', words=['일과']),
    dict(ref=(18, 131, 1), lang='ko', en='things', words=['기이한', '일을']),
    dict(ref=(18, 131, 1), lang='ko', en='too', words=['미치지', '못할']),
    dict(ref=(18, 131, 1), lang='ko', en='high', words=['미치지', '못할']),
    dict(ref=(18, 131, 1), lang='ko', en='for', words=['내가']),
    dict(ref=(18, 131, 1), lang='ko', en='me', words=['내가']),

    dict(ref=(18, 131, 2), lang='ko', en='Surely', words=['실로']),
    dict(ref=(18, 131, 2), lang='ko', en='have', words=['하기를']),
    dict(ref=(18, 131, 2), lang='ko', en='behaved', words=['고요하고']),
    dict(ref=(18, 131, 2), lang='ko', en='myself', words=['내#1', '심령으로']),
    dict(ref=(18, 131, 2), lang='ko', en='I', words=['내가']),
    dict(ref=(18, 131, 2), lang='ko', en='child#1', words=['아이가']),
    dict(ref=(18, 131, 2), lang='ko', en='of', words=['품에']),
    dict(ref=(18, 131, 2), lang='ko', en='my', words=['내#2']),
    dict(ref=(18, 131, 2), lang='ko', en='soul', words=['중심이']),
    dict(ref=(18, 131, 2), lang='ko', en='is#2', words=['같도다']),
    dict(ref=(18, 131, 2), lang='ko', en='even', words=['같도다']),
    dict(ref=(18, 131, 2), lang='ko', en='as#2', words=['같도다']),
    dict(ref=(18, 131, 2), lang='ko', en='weaned#2', words=['젖#2', '뗀#2']),
    dict(ref=(18, 131, 2), lang='ko', en='child#2', words=['아이와']),

    dict(ref=(18, 131, 3), lang='ko', en='Let', words=['바랄지어다']),
    dict(ref=(18, 131, 3), lang='ko', en='the', words=['여호와를']),
    dict(ref=(18, 131, 3), lang='ko', en='Lord', words=['여호와를']),
    dict(ref=(18, 131, 3), lang='ko', en='in', words=['바랄지어다']),
    dict(ref=(18, 131, 3), lang='ko', en='from', words=['지금부터']),
    dict(ref=(18, 131, 3), lang='ko', en='ever', words=['영원까지']),

    # ---- 이사야 46장 ----
    dict(ref=(22, 46, 1), lang='ko', en='boweth', words=['엎드러졌고']),
    dict(ref=(22, 46, 1), lang='ko', en='down', words=['엎드러졌고']),
    dict(ref=(22, 46, 1), lang='ko', en='stoopeth', words=['구부러졌도다']),
    dict(ref=(22, 46, 1), lang='ko', en='were#1', words=['실리웠으니']),
    dict(ref=(22, 46, 1), lang='ko', en='upon#1', words=['실리웠으니']),
    dict(ref=(22, 46, 1), lang='ko', en='upon#2', words=['실리웠으니']),
    dict(ref=(22, 46, 1), lang='ko', en='beasts', words=['짐승과']),
    dict(ref=(22, 46, 1), lang='ko', en='cattle', words=['가축에게']),
    dict(ref=(22, 46, 1), lang='ko', en='carriages', words=['떠메고', '다니던']),
    dict(ref=(22, 46, 1), lang='ko', en='were#2', words=['되었도다']),
    dict(ref=(22, 46, 1), lang='ko', en='heavy', words=['무거운']),
    dict(ref=(22, 46, 1), lang='ko', en='loaden', words=['짐이']),
    dict(ref=(22, 46, 1), lang='ko', en='are', words=['되었도다']),
    dict(ref=(22, 46, 1), lang='ko', en='burden', words=['짐이']),
    dict(ref=(22, 46, 1), lang='ko', en='to', words=['짐승의']),
    dict(ref=(22, 46, 1), lang='ko', en='weary', words=['피곤한']),
    dict(ref=(22, 46, 1), lang='ko', en='beast', words=['짐승의']),

    dict(ref=(22, 46, 1), lang='or', en='down', words=['\u05db\u05bc\u05b8\u05e8\u05b7\u05e2']),
    dict(ref=(22, 46, 1), lang='or', en='stoopeth', words=['\u05e7\u05b9\u05e8\u05b5\u05e1']),
    dict(ref=(22, 46, 1), lang='or', en='your', words=['\u05e0\u05b0\u05e9\u05c2\u05bb\u05d0\u05b9\u05ea\u05b5\u05d9\u05db\u05b6\u05dd']),
    dict(ref=(22, 46, 1), lang='or', en='carriages', words=['\u05e0\u05b0\u05e9\u05c2\u05bb\u05d0\u05b9\u05ea\u05b5\u05d9\u05db\u05b6\u05dd']),
    dict(ref=(22, 46, 1), lang='or', en='loaden', words=['\u05e2\u05b2\u05de\u05d5\u05bc\u05e1\u05d5\u05b9\u05ea']),
    dict(ref=(22, 46, 1), lang='or', en='burden', words=['\u05de\u05b7\u05e9\u05c2\u05bc\u05b8\u05d0']),

    dict(ref=(22, 46, 4), lang='ko', en='even#1', words=['이르기까지']),
    dict(ref=(22, 46, 4), lang='ko', en='to#1', words=['이르기까지']),
    dict(ref=(22, 46, 4), lang='ko', en='I#1', words=['내가#1']),
    dict(ref=(22, 46, 4), lang='ko', en='am', words=['그리하겠고']),
    dict(ref=(22, 46, 4), lang='ko', en='he', words=['그리하겠고']),
    dict(ref=(22, 46, 4), lang='ko', en='even#2', words=['되기까지']),
    dict(ref=(22, 46, 4), lang='ko', en='to#2', words=['되기까지']),
    dict(ref=(22, 46, 4), lang='ko', en='I#2', words=['내가#2']),
    dict(ref=(22, 46, 4), lang='ko', en='will#1', words=['것이라']),
    dict(ref=(22, 46, 4), lang='ko', en='carry#1', words=['품을#1']),
    dict(ref=(22, 46, 4), lang='ko', en='you#1', words=['너희를']),
    dict(ref=(22, 46, 4), lang='ko', en='I#3', words=['내가#3']),
    dict(ref=(22, 46, 4), lang='ko', en='have', words=['지었은즉']),
    dict(ref=(22, 46, 4), lang='ko', en='made', words=['지었은즉']),
    dict(ref=(22, 46, 4), lang='ko', en='will#2', words=['것이요#1']),
    dict(ref=(22, 46, 4), lang='ko', en='bear', words=['안을']),
    dict(ref=(22, 46, 4), lang='ko', en='will#3', words=['것이요#2']),
    dict(ref=(22, 46, 4), lang='ko', en='carry#2', words=['품을#2']),
    dict(ref=(22, 46, 4), lang='ko', en='will#4', words=['내리라']),
    dict(ref=(22, 46, 4), lang='ko', en='deliver', words=['구하여', '내리라']),
    dict(ref=(22, 46, 4), lang='ko', en='you#2', words=['너희를']),

    dict(ref=(22, 46, 10), lang='ko', en='Declaring', words=['고하며', '보이고']),
    dict(ref=(22, 46, 10), lang='ko', en='from#1', words=['처음부터']),
    dict(ref=(22, 46, 10), lang='ko', en='from#2', words=['옛적부터']),
    dict(ref=(22, 46, 10), lang='ko', en='times', words=['옛적부터']),
    dict(ref=(22, 46, 10), lang='ko', en='not', words=['아니한']),
    dict(ref=(22, 46, 10), lang='ko', en='done', words=['이루지']),
    dict(ref=(22, 46, 10), lang='ko', en='saying', words=['이르기를', '하였노라']),
    dict(ref=(22, 46, 10), lang='ko', en='shall', words=['것이니']),
    dict(ref=(22, 46, 10), lang='ko', en='stand', words=['설']),
    dict(ref=(22, 46, 10), lang='ko', en='I', words=['내가#1', '내가#2']),
    dict(ref=(22, 46, 10), lang='ko', en='do', words=['이루리라']),
    dict(ref=(22, 46, 10), lang='ko', en='my', words=['나의#2']),
    dict(ref=(22, 46, 10), lang='ko', en='pleasure', words=['기뻐하는', '것을']),

    dict(ref=(22, 46, 11), lang='ko', en='Calling', words=['부르며', '부를']),
    dict(ref=(22, 46, 11), lang='ko', en='ravenous', words=['독수리를']),
    dict(ref=(22, 46, 11), lang='ko', en='bird', words=['독수리를']),
    dict(ref=(22, 46, 11), lang='ko', en='from#1', words=['동방에서']),
    dict(ref=(22, 46, 11), lang='ko', en='from#2', words=['나라에서']),
    dict(ref=(22, 46, 11), lang='ko', en='country', words=['나라에서']),
    dict(ref=(22, 46, 11), lang='ko', en='executeth', words=['이룰#1']),
    dict(ref=(22, 46, 11), lang='ko', en='my', words=['나의']),
    dict(ref=(22, 46, 11), lang='ko', en='I#1', words=['내가#1', '내가#2']),
    dict(ref=(22, 46, 11), lang='ko', en='have#1', words=['말하였은즉']),
    dict(ref=(22, 46, 11), lang='ko', en='spoken', words=['말하였은즉']),
    dict(ref=(22, 46, 11), lang='ko', en='also#1', words=['정녕#1']),
    dict(ref=(22, 46, 11), lang='ko', en='bring', words=['이룰#2']),
    dict(ref=(22, 46, 11), lang='ko', en='to', words=['이룰#2']),
    dict(ref=(22, 46, 11), lang='ko', en='pass', words=['이룰#2']),
    dict(ref=(22, 46, 11), lang='ko', en='will#1', words=['것이요']),
    dict(ref=(22, 46, 11), lang='ko', en='have#2', words=['경영하였은즉']),
    dict(ref=(22, 46, 11), lang='ko', en='purposed', words=['경영하였은즉']),
    dict(ref=(22, 46, 11), lang='ko', en='also#2', words=['정녕#2']),
    dict(ref=(22, 46, 11), lang='ko', en='will#2', words=['행하리라']),
    dict(ref=(22, 46, 11), lang='ko', en='do', words=['행하리라']),

    dict(ref=(22, 46, 13), lang='ko', en='shall#1', words=['것인즉']),
    dict(ref=(22, 46, 13), lang='ko', en='it', words=['상거가']),
    dict(ref=(22, 46, 13), lang='ko', en='be', words=['멀지']),
    dict(ref=(22, 46, 13), lang='ko', en='not#1', words=['아니하니']),
    dict(ref=(22, 46, 13), lang='ko', en='my#2', words=['나의#2']),
    dict(ref=(22, 46, 13), lang='ko', en='salvation#1', words=['구원이']),
    dict(ref=(22, 46, 13), lang='ko', en='not#2', words=['아니할']),
    dict(ref=(22, 46, 13), lang='ko', en='shall#2', words=['것이라']),
    dict(ref=(22, 46, 13), lang='ko', en='I#2', words=['내가#2']),
    dict(ref=(22, 46, 13), lang='ko', en='will', words=['베풀리라']),
    dict(ref=(22, 46, 13), lang='ko', en='place', words=['베풀리라']),
    dict(ref=(22, 46, 13), lang='ko', en='salvation#2', words=['구원을']),
    dict(ref=(22, 46, 13), lang='ko', en='in', words=['시온에']),
    dict(ref=(22, 46, 13), lang='ko', en='my#3', words=['나의#3']),
    dict(ref=(22, 46, 13), lang='ko', en='glory', words=['영광인']),

    dict(ref=(22, 46, 2), lang='ko', en='They', words=['그들은#1']),
    dict(ref=(22, 46, 2), lang='ko', en='they#1', words=['그들은#2']),
    dict(ref=(22, 46, 2), lang='ko', en='they#2', words=['그들은#2']),
    dict(ref=(22, 46, 2), lang='ko', en='bow', words=['엎드러졌으므로']),
    dict(ref=(22, 46, 2), lang='ko', en='down', words=['엎드러졌으므로']),
    dict(ref=(22, 46, 2), lang='ko', en='not', words=['못하고']),
    dict(ref=(22, 46, 2), lang='ko', en='deliver', words=['구하여', '내지']),
    dict(ref=(22, 46, 2), lang='ko', en='the', words=['그']),
    dict(ref=(22, 46, 2), lang='ko', en='themselves', words=['자기도']),
    dict(ref=(22, 46, 2), lang='ko', en='are', words=['갔느니라']),
    dict(ref=(22, 46, 2), lang='ko', en='into', words=['잡혀']),
    dict(ref=(22, 46, 2), lang='ko', en='captivity', words=['잡혀']),

    dict(ref=(22, 46, 3), lang='ko', en='house#2', words=['집의']),
    dict(ref=(22, 46, 3), lang='ko', en='remnant', words=['남은', '자여']),
    dict(ref=(22, 46, 3), lang='ko', en='which#1', words=['너희여']),
    dict(ref=(22, 46, 3), lang='ko', en='which#2', words=['너희여']),
    dict(ref=(22, 46, 3), lang='ko', en='borne', words=['안겼고']),
    dict(ref=(22, 46, 3), lang='ko', en='by', words=['내게#1']),
    dict(ref=(22, 46, 3), lang='ko', en='me#2', words=['내게#1']),
    dict(ref=(22, 46, 3), lang='ko', en='from#1', words=['남으로부터#1']),
    dict(ref=(22, 46, 3), lang='ko', en='belly', words=['배에서']),
    dict(ref=(22, 46, 3), lang='ko', en='carried', words=['내게#2', '품기운']),
    dict(ref=(22, 46, 3), lang='ko', en='from#2', words=['남으로부터#2']),
    dict(ref=(22, 46, 3), lang='ko', en='womb', words=['태에서']),

    dict(ref=(22, 46, 7), lang='ko', en='bear', words=['들어']),
    dict(ref=(22, 46, 7), lang='ko', en='him#1', words=['그것을']),
    dict(ref=(22, 46, 7), lang='ko', en='him#2', words=['그것을']),
    dict(ref=(22, 46, 7), lang='ko', en='him#3', words=['그것을']),
    dict(ref=(22, 46, 7), lang='ko', en='upon', words=['어깨에']),
    dict(ref=(22, 46, 7), lang='ko', en='carry', words=['메어다가']),
    dict(ref=(22, 46, 7), lang='ko', en='his#1', words=['그의']),
    dict(ref=(22, 46, 7), lang='ko', en='place#1', words=['처소에']),
    dict(ref=(22, 46, 7), lang='ko', en='he#1', words=['그것이']),
    dict(ref=(22, 46, 7), lang='ko', en='he#2', words=['그것이']),
    dict(ref=(22, 46, 7), lang='ko', en='he#3', words=['그것이']),
    dict(ref=(22, 46, 7), lang='ko', en='standeth', words=['서서', '있고']),
    dict(ref=(22, 46, 7), lang='ko', en='from', words=['거기서']),
    dict(ref=(22, 46, 7), lang='ko', en='his#2', words=['거기서']),
    dict(ref=(22, 46, 7), lang='ko', en='place#2', words=['거기서']),
    dict(ref=(22, 46, 7), lang='ko', en='shall#1', words=['능히#1']),
    dict(ref=(22, 46, 7), lang='ko', en='can', words=['능히#1', '능히#2']),
    dict(ref=(22, 46, 7), lang='ko', en='remove', words=['움직이지']),
    dict(ref=(22, 46, 7), lang='ko', en='not#1', words=['못하며#1']),
    dict(ref=(22, 46, 7), lang='ko', en='unto', words=['그에게']),
    dict(ref=(22, 46, 7), lang='ko', en='him#4', words=['그에게']),
    dict(ref=(22, 46, 7), lang='ko', en='one', words=['부르짖어도']),
    dict(ref=(22, 46, 7), lang='ko', en='shall#2', words=['부르짖어도']),
    dict(ref=(22, 46, 7), lang='ko', en='yet', words=['능히#2']),
    dict(ref=(22, 46, 7), lang='ko', en='answer', words=['응답지']),
    dict(ref=(22, 46, 7), lang='ko', en='not#2', words=['못하며#2']),
    dict(ref=(22, 46, 7), lang='ko', en='nor', words=['못하느니라']),
    dict(ref=(22, 46, 7), lang='ko', en='save', words=['구하여', '내지도']),
    dict(ref=(22, 46, 7), lang='ko', en='him#5', words=['그것을']),
    dict(ref=(22, 46, 7), lang='ko', en='out', words=['고난에서']),
    dict(ref=(22, 46, 7), lang='ko', en='of', words=['고난에서']),
    dict(ref=(22, 46, 7), lang='ko', en='his#3', words=['고난에서']),

    dict(ref=(22, 46, 9), lang='ko', en='Remember', words=['너희는', '기억하라']),
    dict(ref=(22, 46, 9), lang='ko', en='former', words=['옛적']),
    dict(ref=(22, 46, 9), lang='ko', en='for', words=[]),
    dict(ref=(22, 46, 9), lang='ko', en='I#1', words=['나는#1']),
    dict(ref=(22, 46, 9), lang='ko', en='am#1', words=['나는#1']),
    dict(ref=(22, 46, 9), lang='ko', en='God#1', words=['하나님이라#1']),
    dict(ref=(22, 46, 9), lang='ko', en='there#1', words=['없느니라#1']),
    dict(ref=(22, 46, 9), lang='ko', en='is#1', words=['없느니라#1']),
    dict(ref=(22, 46, 9), lang='ko', en='none#1', words=['이가#1', '없느니라#1']),
    dict(ref=(22, 46, 9), lang='ko', en='me', words=['나#1', '나#2']),
    dict(ref=(22, 46, 9), lang='ko', en='I#2', words=['나는#2']),
    dict(ref=(22, 46, 9), lang='ko', en='am#2', words=['나는#2']),
    dict(ref=(22, 46, 9), lang='ko', en='God#2', words=['하나님이라#2']),
    dict(ref=(22, 46, 9), lang='ko', en='there#2', words=['없느니라#2']),
    dict(ref=(22, 46, 9), lang='ko', en='is#2', words=['없느니라#2']),
    dict(ref=(22, 46, 9), lang='ko', en='none#2', words=['이가#2', '없느니라#2']),

    # ---- 이사야 18장 ----
    dict(ref=(22, 18, 2), lang='ko', en='ambassadors', words=['사자를']),
    dict(ref=(22, 18, 2), lang='ko', en='by', words=['수로로']),
    dict(ref=(22, 18, 2), lang='ko', en='the#1', words=['수로로']),
    dict(ref=(22, 18, 2), lang='ko', en='sea', words=['수로로']),
    dict(ref=(22, 18, 2), lang='ko', en='vessels', words=['배를']),
    dict(ref=(22, 18, 2), lang='ko', en='bulrushes', words=['갈대']),
    dict(ref=(22, 18, 2), lang='ko', en='waters', words=['물에']),
    dict(ref=(22, 18, 2), lang='ko', en='sendeth', words=['보내며']),
    dict(ref=(22, 18, 2), lang='ko', en='saying', words=['이르기를']),
    dict(ref=(22, 18, 2), lang='ko', en='Go', words=['가되', '가라']),
    dict(ref=(22, 18, 2), lang='ko', en='ye', words=['너희', '너희는']),
    dict(ref=(22, 18, 2), lang='ko', en='swift', words=['경첩한']),
    dict(ref=(22, 18, 2), lang='ko', en='messengers', words=['사자들아']),
    dict(ref=(22, 18, 2), lang='ko', en='rivers', words=['강들이']),
    dict(ref=(22, 18, 2), lang='ko', en='have', words=['흘러']),
    dict(ref=(22, 18, 2), lang='ko', en='spoiled', words=['나누인']),
    dict(ref=(22, 18, 2), lang='ko', en='nation#1', words=['나라로']),
    dict(ref=(22, 18, 2), lang='ko', en='scattered', words=['장대하고']),
    dict(ref=(22, 18, 2), lang='ko', en='peeled', words=['준수한']),
    dict(ref=(22, 18, 2), lang='ko', en='people', words=['백성']),
    dict(ref=(22, 18, 2), lang='ko', en='from', words=['시초부터']),
    dict(ref=(22, 18, 2), lang='ko', en='their', words=['시초부터']),
    dict(ref=(22, 18, 2), lang='ko', en='beginning', words=['시초부터']),
    dict(ref=(22, 18, 2), lang='ko', en='hitherto', words=['시초부터']),
    dict(ref=(22, 18, 2), lang='ko', en='terrible', words=['두려움이', '되며']),
    dict(ref=(22, 18, 2), lang='ko', en='meted', words=['강성하여', '대적을', '밟는']),
    dict(ref=(22, 18, 2), lang='ko', en='out', words=['강성하여', '대적을', '밟는']),
    dict(ref=(22, 18, 2), lang='ko', en='trodden', words=['밟는']),
    dict(ref=(22, 18, 2), lang='ko', en='down', words=['밟는']),
    dict(ref=(22, 18, 2), lang='ko', en='nation#2', words=['백성에게로']),

    dict(ref=(22, 18, 3), lang='ko', en='All', words=['모든']),
    dict(ref=(22, 18, 3), lang='ko', en='inhabitants', words=['거민']),
    dict(ref=(22, 18, 3), lang='ko', en='world', words=['세상의']),
    dict(ref=(22, 18, 3), lang='ko', en='dwellers', words=['거하는', '너희여']),
    dict(ref=(22, 18, 3), lang='ko', en='on#1', words=['지상에']),
    dict(ref=(22, 18, 3), lang='ko', en='the#2', words=['지상에']),
    dict(ref=(22, 18, 3), lang='ko', en='earth', words=['지상에']),
    dict(ref=(22, 18, 3), lang='ko', en='see', words=['보고']),
    dict(ref=(22, 18, 3), lang='ko', en='ye#2', words=['너희는#1']),
    dict(ref=(22, 18, 3), lang='ko', en='lifteth', words=['세우거든']),
    dict(ref=(22, 18, 3), lang='ko', en='up', words=['세우거든']),
    dict(ref=(22, 18, 3), lang='ko', en='ensign', words=['기호를']),
    dict(ref=(22, 18, 3), lang='ko', en='on#2', words=['위에']),
    dict(ref=(22, 18, 3), lang='ko', en='mountains', words=['산들']),
    dict(ref=(22, 18, 3), lang='ko', en='trumpet', words=['나팔을']),
    dict(ref=(22, 18, 3), lang='ko', en='bloweth', words=['불거든']),
    dict(ref=(22, 18, 3), lang='ko', en='hear', words=['들을지니라']),
    dict(ref=(22, 18, 3), lang='ko', en='ye#3', words=['너희는#2']),

    dict(ref=(22, 18, 4), lang='ko', en='Lord', words=['여호와께서']),
    dict(ref=(22, 18, 4), lang='ko', en='said', words=['이르시되']),
    dict(ref=(22, 18, 4), lang='ko', en='me', words=['내게']),
    dict(ref=(22, 18, 4), lang='ko', en='I#1', words=['내가']),
    dict(ref=(22, 18, 4), lang='ko', en='rest', words=['종용히']),
    dict(ref=(22, 18, 4), lang='ko', en='my#2', words=['나의']),
    dict(ref=(22, 18, 4), lang='ko', en='dwelling', words=['처소에서']),
    dict(ref=(22, 18, 4), lang='ko', en='place', words=['처소에서']),
    dict(ref=(22, 18, 4), lang='ko', en='consider', words=['감찰함이']),
    dict(ref=(22, 18, 4), lang='ko', en='like#1', words=['같고']),
    dict(ref=(22, 18, 4), lang='ko', en='clear', words=['쬐이는']),
    dict(ref=(22, 18, 4), lang='ko', en='heat#1', words=['일광']),
    dict(ref=(22, 18, 4), lang='ko', en='like#2', words=['같도다']),
    dict(ref=(22, 18, 4), lang='ko', en='a#2', words=['운무']),
    dict(ref=(22, 18, 4), lang='ko', en='cloud', words=['운무']),
    dict(ref=(22, 18, 4), lang='ko', en='of#1', words=['운무']),
    dict(ref=(22, 18, 4), lang='ko', en='dew', words=['운무']),
    dict(ref=(22, 18, 4), lang='ko', en='heat#2', words=['더위에']),
    dict(ref=(22, 18, 4), lang='ko', en='harvest', words=['가을']),

    dict(ref=(22, 18, 6), lang='ko', en='be', words=['끼쳐주리니']),
    dict(ref=(22, 18, 6), lang='ko', en='left', words=['끼쳐주리니']),
    dict(ref=(22, 18, 6), lang='ko', en='mountains', words=['산의#1', '산의#2']),
    dict(ref=(22, 18, 6), lang='ko', en='fowls#2', words=['독수리들이']),
    dict(ref=(22, 18, 6), lang='ko', en='summer', words=['과하하며']),
    dict(ref=(22, 18, 6), lang='ko', en='beasts#2', words=['들짐승들이']),
    dict(ref=(22, 18, 6), lang='ko', en='upon#1', words=['그것으로#1']),
    dict(ref=(22, 18, 6), lang='ko', en='them#1', words=['그것으로#1']),
    dict(ref=(22, 18, 6), lang='ko', en='upon#2', words=['그것으로#2']),
    dict(ref=(22, 18, 6), lang='ko', en='them#2', words=['그것으로#2']),

    dict(ref=(22, 18, 5), lang='ko', en='afore', words=['전에']),
    dict(ref=(22, 18, 5), lang='ko', en='is#1', words=['떨어지고']),
    dict(ref=(22, 18, 5), lang='ko', en='perfect', words=['떨어지고']),
    dict(ref=(22, 18, 5), lang='ko', en='flower', words=['꽃이']),
    dict(ref=(22, 18, 5), lang='ko', en='is#2', words=['맺혀']),
    dict(ref=(22, 18, 5), lang='ko', en='ripening', words=['익어', '갈']),
    dict(ref=(22, 18, 5), lang='ko', en='with', words=['낫으로']),
    dict(ref=(22, 18, 5), lang='ko', en='hooks', words=['낫으로']),
    dict(ref=(22, 18, 5), lang='ko', en='sprigs', words=['연한', '가지를#1']),
    dict(ref=(22, 18, 5), lang='ko', en='branches', words=['퍼진', '가지를#2']),
    dict(ref=(22, 18, 5), lang='ko', en='take', words=['찍어버려서']),
    dict(ref=(22, 18, 5), lang='ko', en='away', words=['찍어버려서']),
    dict(ref=(22, 18, 5), lang='ko', en='cut#2', words=['찍어버려서']),
    dict(ref=(22, 18, 5), lang='ko', en='down', words=['찍어버려서']),

    dict(ref=(22, 18, 7), lang='ko', en='that', words=['그']),
    dict(ref=(22, 18, 7), lang='ko', en='be', words=['드릴']),
    dict(ref=(22, 18, 7), lang='ko', en='brought', words=['드릴', '가지고']),
    dict(ref=(22, 18, 7), lang='ko', en='Lord#1', words=['여호와께']),
    dict(ref=(22, 18, 7), lang='ko', en='Lord#2', words=['여호와의']),
    dict(ref=(22, 18, 7), lang='ko', en='scattered', words=['장대하고']),
    dict(ref=(22, 18, 7), lang='ko', en='peeled', words=['장대하고', '준수하며']),
    dict(ref=(22, 18, 7), lang='ko', en='people#2', words=['백성에게서']),
    dict(ref=(22, 18, 7), lang='ko', en='terrible', words=['두려움이', '되며']),
    dict(ref=(22, 18, 7), lang='ko', en='from#2', words=['시초부터']),
    dict(ref=(22, 18, 7), lang='ko', en='their', words=['시초부터']),
    dict(ref=(22, 18, 7), lang='ko', en='beginning', words=['시초부터']),
    dict(ref=(22, 18, 7), lang='ko', en='hitherto', words=['시초부터']),
    dict(ref=(22, 18, 7), lang='ko', en='nation', words=['나라의']),
    dict(ref=(22, 18, 7), lang='ko', en='meted', words=['강성하여', '대적을', '밟는']),
    dict(ref=(22, 18, 7), lang='ko', en='out', words=['강성하여', '대적을', '밟는']),
    dict(ref=(22, 18, 7), lang='ko', en='under', words=['밟는']),
    dict(ref=(22, 18, 7), lang='ko', en='foot', words=['밟는']),
    dict(ref=(22, 18, 7), lang='ko', en='land', words=['나라의']),
    dict(ref=(22, 18, 7), lang='ko', en='have', words=['흘러']),
    dict(ref=(22, 18, 7), lang='ko', en='spoiled', words=['흘러', '나누인']),
    dict(ref=(22, 18, 7), lang='ko', en='place', words=['두신', '곳']),

    # ---- 이사야 33장 ----
    # 히브리 시의 평행 구조라 같은 영어 낱말이 한 절에 2~4번 나온다.
    # 연결이 모두 첫 한국어 낱말에 몰려 있던 것을 되풀이되는 자리마다 나눈다.
    dict(ref=(22, 33, 1), lang='ko', en='Woe', words=['화', '있을진저']),
    dict(ref=(22, 33, 1), lang='ko', en='thee#1', words=['너']),
    dict(ref=(22, 33, 1), lang='ko', en='that', words=['자여']),
    dict(ref=(22, 33, 1), lang='ko', en='spoilest', words=['학대하며']),
    dict(ref=(22, 33, 1), lang='ko', en='spoiled#1', words=['학대를#1']),
    dict(ref=(22, 33, 1), lang='ko', en='wast', words=['당치']),
    dict(ref=(22, 33, 1), lang='ko', en='not#1', words=['아니하고도#1']),
    dict(ref=(22, 33, 1), lang='ko', en='dealest', words=['속이는']),
    dict(ref=(22, 33, 1), lang='ko', en='treacherously#1', words=['속이는']),
    dict(ref=(22, 33, 1), lang='ko', en='treacherously#2', words=['속임을']),
    dict(ref=(22, 33, 1), lang='ko', en='dealt', words=['입지']),
    dict(ref=(22, 33, 1), lang='ko', en='not#2', words=['아니하고도#2']),
    dict(ref=(22, 33, 1), lang='ko', en='thee#2', words=['너']),
    dict(ref=(22, 33, 1), lang='ko', en='when#1', words=['마치면']),
    dict(ref=(22, 33, 1), lang='ko', en='thou#2', words=['네가#1']),
    dict(ref=(22, 33, 1), lang='ko', en='cease', words=['마치면']),
    dict(ref=(22, 33, 1), lang='ko', en='spoil', words=['학대하기를']),
    dict(ref=(22, 33, 1), lang='ko', en='thou#3', words=['네가#2']),
    dict(ref=(22, 33, 1), lang='ko', en='shalt#2', words=['것이며']),
    dict(ref=(22, 33, 1), lang='ko', en='be', words=['당할']),
    dict(ref=(22, 33, 1), lang='ko', en='spoiled#2', words=['학대를#2']),
    dict(ref=(22, 33, 1), lang='ko', en='when#2', words=['그치면']),
    dict(ref=(22, 33, 1), lang='ko', en='thou#4', words=['네가#3']),
    dict(ref=(22, 33, 1), lang='ko', en='make', words=['그치면']),
    dict(ref=(22, 33, 1), lang='ko', en='end', words=['그치면']),
    dict(ref=(22, 33, 1), lang='ko', en='deal#1', words=['속이기를']),
    dict(ref=(22, 33, 1), lang='ko', en='treacherously#3', words=['속이기를']),
    dict(ref=(22, 33, 1), lang='ko', en='they#2', words=['사람이']),
    dict(ref=(22, 33, 1), lang='ko', en='shall', words=['속이리라']),
    dict(ref=(22, 33, 1), lang='ko', en='deal#2', words=['속이리라']),
    dict(ref=(22, 33, 1), lang='ko', en='treacherously#4', words=['속이리라']),
    dict(ref=(22, 33, 1), lang='ko', en='with#2', words=['너를']),
    dict(ref=(22, 33, 1), lang='ko', en='thee#3', words=['너를']),

    dict(ref=(22, 33, 10), lang='ko', en='Now', words=['이제#1']),
    dict(ref=(22, 33, 10), lang='ko', en='I#1', words=['내가#1']),
    dict(ref=(22, 33, 10), lang='ko', en='rise', words=['일어나며']),
    dict(ref=(22, 33, 10), lang='ko', en='saith', words=['가라사대']),
    dict(ref=(22, 33, 10), lang='ko', en='Lord', words=['여호와께서']),
    dict(ref=(22, 33, 10), lang='ko', en='now#1', words=['이제#2']),
    dict(ref=(22, 33, 10), lang='ko', en='I#2', words=['내가#2']),
    dict(ref=(22, 33, 10), lang='ko', en='exalted', words=['나를', '높이며']),
    dict(ref=(22, 33, 10), lang='ko', en='now#2', words=['이제#3']),
    dict(ref=(22, 33, 10), lang='ko', en='I#3', words=['내가#3']),
    dict(ref=(22, 33, 10), lang='ko', en='lift', words=['높이우리니']),
    dict(ref=(22, 33, 10), lang='ko', en='up', words=['지극히']),
    dict(ref=(22, 33, 10), lang='ko', en='myself', words=['높이우리니']),

    dict(ref=(22, 33, 13), lang='ko', en='Hear', words=['들으라']),
    dict(ref=(22, 33, 13), lang='ko', en='ye#1', words=['너희#1']),
    dict(ref=(22, 33, 13), lang='ko', en='that#1', words=['자들아#1']),
    dict(ref=(22, 33, 13), lang='ko', en='are#1', words=['있는#1']),
    dict(ref=(22, 33, 13), lang='ko', en='far', words=['먼']),
    dict(ref=(22, 33, 13), lang='ko', en='off', words=['데']),
    dict(ref=(22, 33, 13), lang='ko', en='what', words=['것을']),
    dict(ref=(22, 33, 13), lang='ko', en='I', words=['나의#1']),
    dict(ref=(22, 33, 13), lang='ko', en='done', words=['행한']),
    dict(ref=(22, 33, 13), lang='ko', en='ye#2', words=['너희#2']),
    dict(ref=(22, 33, 13), lang='ko', en='that#2', words=['자들아#2']),
    dict(ref=(22, 33, 13), lang='ko', en='are#2', words=['있는#2']),
    dict(ref=(22, 33, 13), lang='ko', en='near', words=['가까이']),
    dict(ref=(22, 33, 13), lang='ko', en='acknowledge', words=['알라']),
    dict(ref=(22, 33, 13), lang='ko', en='my', words=['나의#2']),
    dict(ref=(22, 33, 13), lang='ko', en='might', words=['권능을']),

    dict(ref=(22, 33, 22), lang='ko', en='For', words=['대저']),
    dict(ref=(22, 33, 22), lang='ko', en='the#1', words=['여호와는#1']),
    dict(ref=(22, 33, 22), lang='ko', en='Lord#1', words=['여호와는#1']),
    dict(ref=(22, 33, 22), lang='ko', en='is#1', words=['재판장이시요']),
    dict(ref=(22, 33, 22), lang='ko', en='our#1', words=['우리']),
    dict(ref=(22, 33, 22), lang='ko', en='judge', words=['재판장이시요']),
    dict(ref=(22, 33, 22), lang='ko', en='the#2', words=['여호와는#2']),
    dict(ref=(22, 33, 22), lang='ko', en='Lord#2', words=['여호와는#2']),
    dict(ref=(22, 33, 22), lang='ko', en='is#2', words=['자시요']),
    dict(ref=(22, 33, 22), lang='ko', en='our#2', words=['우리에게']),
    dict(ref=(22, 33, 22), lang='ko', en='lawgiver', words=['율법을', '세우신', '자시요']),
    dict(ref=(22, 33, 22), lang='ko', en='the#3', words=['여호와는#3']),
    dict(ref=(22, 33, 22), lang='ko', en='Lord#3', words=['여호와는#3']),
    dict(ref=(22, 33, 22), lang='ko', en='is#3', words=['왕이시니']),
    dict(ref=(22, 33, 22), lang='ko', en='our#3', words=['우리의']),
    dict(ref=(22, 33, 22), lang='ko', en='king', words=['왕이시니']),
    dict(ref=(22, 33, 22), lang='ko', en='he', words=[]),
    dict(ref=(22, 33, 22), lang='ko', en='will', words=['것임이니라']),
    dict(ref=(22, 33, 22), lang='ko', en='save', words=['구원하실']),
    dict(ref=(22, 33, 22), lang='ko', en='us', words=['우리를']),

    dict(ref=(22, 33, 14), lang='ko', en='in', words=['시온의']),
    dict(ref=(22, 33, 14), lang='ko', en='Zion', words=['시온의']),
    dict(ref=(22, 33, 14), lang='ko', en='sinners', words=['죄인들이']),
    dict(ref=(22, 33, 14), lang='ko', en='are', words=['두려워하며']),
    dict(ref=(22, 33, 14), lang='ko', en='afraid', words=['두려워하며']),
    dict(ref=(22, 33, 14), lang='ko', en='fearfulness', words=['떨며']),
    dict(ref=(22, 33, 14), lang='ko', en='surprised', words=['떨며']),
    dict(ref=(22, 33, 14), lang='ko', en='the#1', words=['경건치']),
    dict(ref=(22, 33, 14), lang='ko', en='hypocrites', words=['경건치', '아니한', '자들이']),
    dict(ref=(22, 33, 14), lang='ko', en='Who', words=['누가#1']),
    dict(ref=(22, 33, 14), lang='ko', en='among#1', words=['중에#1']),
    dict(ref=(22, 33, 14), lang='ko', en='us#1', words=['우리#1']),
    dict(ref=(22, 33, 14), lang='ko', en='shall#1', words=['거하겠으며']),
    dict(ref=(22, 33, 14), lang='ko', en='dwell#1', words=['거하겠으며']),
    dict(ref=(22, 33, 14), lang='ko', en='with#1', words=['함께#1']),
    dict(ref=(22, 33, 14), lang='ko', en='the#2', words=['삼키는']),
    dict(ref=(22, 33, 14), lang='ko', en='devouring', words=['삼키는']),
    dict(ref=(22, 33, 14), lang='ko', en='fire', words=['불과']),
    dict(ref=(22, 33, 14), lang='ko', en='who', words=['누가#2']),
    dict(ref=(22, 33, 14), lang='ko', en='among#2', words=['중에#2']),
    dict(ref=(22, 33, 14), lang='ko', en='us#2', words=['우리#2']),
    dict(ref=(22, 33, 14), lang='ko', en='shall#2', words=['거하리요']),
    dict(ref=(22, 33, 14), lang='ko', en='dwell#2', words=['거하리요']),
    dict(ref=(22, 33, 14), lang='ko', en='with#2', words=['함께#2']),
    dict(ref=(22, 33, 14), lang='ko', en='everlasting', words=['영영히']),
    dict(ref=(22, 33, 14), lang='ko', en='burnings', words=['타는', '것과']),

    dict(ref=(22, 33, 15), lang='ko', en='He', words=['자#1']),
    dict(ref=(22, 33, 15), lang='ko', en='that#1', words=['자#1']),
    dict(ref=(22, 33, 15), lang='ko', en='walketh', words=['행하는']),
    dict(ref=(22, 33, 15), lang='ko', en='righteously', words=['의롭게']),
    dict(ref=(22, 33, 15), lang='ko', en='speaketh', words=['말하는자']),
    dict(ref=(22, 33, 15), lang='ko', en='uprightly', words=['정직히']),
    dict(ref=(22, 33, 15), lang='ko', en='he', words=['자#2']),
    dict(ref=(22, 33, 15), lang='ko', en='that#2', words=['자#2']),
    dict(ref=(22, 33, 15), lang='ko', en='despiseth', words=['가증히', '여기는']),
    dict(ref=(22, 33, 15), lang='ko', en='gain', words=['재물을']),
    dict(ref=(22, 33, 15), lang='ko', en='of#1', words=['토색한']),
    dict(ref=(22, 33, 15), lang='ko', en='oppressions', words=['토색한']),
    dict(ref=(22, 33, 15), lang='ko', en='that#3', words=['자#3']),
    dict(ref=(22, 33, 15), lang='ko', en='shaketh', words=['흔들어']),
    dict(ref=(22, 33, 15), lang='ko', en='his#1', words=['손을']),
    dict(ref=(22, 33, 15), lang='ko', en='hands', words=['손을']),
    # 'from …ing'은 한국어의 '…지 아니하는'과 구조가 전혀 달라 짝으로 보기 어렵다.
    dict(ref=(22, 33, 15), lang='ko', en='from#1', words=[]),
    dict(ref=(22, 33, 15), lang='ko', en='holding', words=['받지']),
    dict(ref=(22, 33, 15), lang='ko', en='of#2', words=['뇌물을']),
    dict(ref=(22, 33, 15), lang='ko', en='bribes', words=['뇌물을']),
    dict(ref=(22, 33, 15), lang='ko', en='that#4', words=['자#4']),
    dict(ref=(22, 33, 15), lang='ko', en='stoppeth', words=['막아']),
    dict(ref=(22, 33, 15), lang='ko', en='his#2', words=['귀를']),
    dict(ref=(22, 33, 15), lang='ko', en='ears', words=['귀를']),
    dict(ref=(22, 33, 15), lang='ko', en='from#2', words=[]),
    dict(ref=(22, 33, 15), lang='ko', en='hearing', words=['듣지']),
    dict(ref=(22, 33, 15), lang='ko', en='of#3', words=['피']),
    dict(ref=(22, 33, 15), lang='ko', en='blood', words=['피', '흘리려는']),
    dict(ref=(22, 33, 15), lang='ko', en='and#2', words=['자#5']),
    dict(ref=(22, 33, 15), lang='ko', en='shutteth', words=['감아']),
    dict(ref=(22, 33, 15), lang='ko', en='his#3', words=['눈을']),
    dict(ref=(22, 33, 15), lang='ko', en='eyes', words=['눈을']),
    dict(ref=(22, 33, 15), lang='ko', en='from#3', words=[]),
    dict(ref=(22, 33, 15), lang='ko', en='seeing', words=['보지']),
    dict(ref=(22, 33, 15), lang='ko', en='evil', words=['악을']),

    dict(ref=(22, 33, 18), lang='ko', en='Thine', words=['너의']),
    dict(ref=(22, 33, 18), lang='ko', en='heart', words=['마음에는']),
    dict(ref=(22, 33, 18), lang='ko', en='shall', words=['내리라']),
    dict(ref=(22, 33, 18), lang='ko', en='meditate', words=['생각하여']),
    dict(ref=(22, 33, 18), lang='ko', en='terror', words=['두려워하던', '것을']),
    dict(ref=(22, 33, 18), lang='ko', en='Where', words=['어디#1']),
    dict(ref=(22, 33, 18), lang='ko', en='is#1', words=['있느냐#1']),
    dict(ref=(22, 33, 18), lang='ko', en='the#1', words=['자가#1']),
    dict(ref=(22, 33, 18), lang='ko', en='scribe', words=['계산하던', '자가#1']),
    dict(ref=(22, 33, 18), lang='ko', en='where#1', words=['어디#2']),
    dict(ref=(22, 33, 18), lang='ko', en='is#2', words=['있느냐#2']),
    dict(ref=(22, 33, 18), lang='ko', en='the#2', words=['자가#2']),
    dict(ref=(22, 33, 18), lang='ko', en='receiver', words=['공세를', '칭량하던', '자가#2']),
    dict(ref=(22, 33, 18), lang='ko', en='where#2', words=['어디#3']),
    dict(ref=(22, 33, 18), lang='ko', en='is#3', words=['있느냐#3']),
    dict(ref=(22, 33, 18), lang='ko', en='he', words=['자가#3']),
    dict(ref=(22, 33, 18), lang='ko', en='that', words=['자가#3']),
    dict(ref=(22, 33, 18), lang='ko', en='counted', words=['계수하던']),
    dict(ref=(22, 33, 18), lang='ko', en='the#3', words=['망대를']),
    dict(ref=(22, 33, 18), lang='ko', en='towers', words=['망대를']),

    dict(ref=(22, 33, 19), lang='ko', en='Thou', words=['네가#1']),
    dict(ref=(22, 33, 19), lang='ko', en='shalt', words=['아니하리라']),
    dict(ref=(22, 33, 19), lang='ko', en='not#1', words=['아니하리라']),
    dict(ref=(22, 33, 19), lang='ko', en='see', words=['보지']),
    dict(ref=(22, 33, 19), lang='ko', en='fierce', words=['강포한']),
    dict(ref=(22, 33, 19), lang='ko', en='people#1', words=['백성을']),
    dict(ref=(22, 33, 19), lang='ko', en='a#2', words=['그']),
    dict(ref=(22, 33, 19), lang='ko', en='people#2', words=['백성은']),
    dict(ref=(22, 33, 19), lang='ko', en='of#1', words=['방언이']),
    dict(ref=(22, 33, 19), lang='ko', en='speech', words=['방언이']),
    dict(ref=(22, 33, 19), lang='ko', en='deeper', words=['어려워서']),
    dict(ref=(22, 33, 19), lang='ko', en='than', words=['못하며']),
    dict(ref=(22, 33, 19), lang='ko', en='thou#1', words=['네가#2']),
    dict(ref=(22, 33, 19), lang='ko', en='canst#1', words=['못하며']),
    dict(ref=(22, 33, 19), lang='ko', en='perceive', words=['알아', '듣지']),
    dict(ref=(22, 33, 19), lang='ko', en='of#2', words=['말이']),
    dict(ref=(22, 33, 19), lang='ko', en='tongue', words=['말이']),
    dict(ref=(22, 33, 19), lang='ko', en='stammering', words=['이상하여']),
    dict(ref=(22, 33, 19), lang='ko', en='that', words=['자니라']),
    dict(ref=(22, 33, 19), lang='ko', en='thou#2', words=['네가#3']),
    dict(ref=(22, 33, 19), lang='ko', en='canst#2', words=['못하는']),
    dict(ref=(22, 33, 19), lang='ko', en='not#2', words=['못하는']),
    dict(ref=(22, 33, 19), lang='ko', en='understand', words=['깨닫지']),

    dict(ref=(22, 33, 3), lang='ko', en='At', words=['인하여#1']),
    dict(ref=(22, 33, 3), lang='ko', en='noise', words=['소리로']),
    dict(ref=(22, 33, 3), lang='ko', en='the#1', words=['소리로']),
    dict(ref=(22, 33, 3), lang='ko', en='tumult', words=['진동', '시키시는']),
    dict(ref=(22, 33, 3), lang='ko', en='people', words=['민족들이']),
    dict(ref=(22, 33, 3), lang='ko', en='fled', words=['도망하며']),
    dict(ref=(22, 33, 3), lang='ko', en='at', words=['인하여#2']),
    dict(ref=(22, 33, 3), lang='ko', en='lifting', words=['일어나시므로']),
    dict(ref=(22, 33, 3), lang='ko', en='up', words=['일어나시므로']),
    dict(ref=(22, 33, 3), lang='ko', en='thyself', words=['주께서']),
    dict(ref=(22, 33, 3), lang='ko', en='nations', words=['열방이']),
    dict(ref=(22, 33, 3), lang='ko', en='were', words=['흩어졌나이다']),
    dict(ref=(22, 33, 3), lang='ko', en='scattered', words=['흩어졌나이다']),

    dict(ref=(22, 33, 16), lang='ko', en='He', words=['그는']),
    dict(ref=(22, 33, 16), lang='ko', en='shall#1', words=['거하리니']),
    dict(ref=(22, 33, 16), lang='ko', en='dwell', words=['거하리니']),
    dict(ref=(22, 33, 16), lang='ko', en='on', words=['곳에']),
    dict(ref=(22, 33, 16), lang='ko', en='high', words=['높은']),
    dict(ref=(22, 33, 16), lang='ko', en='his#1', words=['그#1']),
    dict(ref=(22, 33, 16), lang='ko', en='place', words=['보장이']),
    dict(ref=(22, 33, 16), lang='ko', en='defence', words=['보장이']),
    dict(ref=(22, 33, 16), lang='ko', en='shall#2', words=['되며']),
    dict(ref=(22, 33, 16), lang='ko', en='be#1', words=['되며']),
    dict(ref=(22, 33, 16), lang='ko', en='munitions', words=['견고한']),
    dict(ref=(22, 33, 16), lang='ko', en='rocks', words=['바위가']),
    dict(ref=(22, 33, 16), lang='ko', en='bread', words=['양식은']),
    dict(ref=(22, 33, 16), lang='ko', en='shall#3', words=['공급되고']),
    dict(ref=(22, 33, 16), lang='ko', en='be#2', words=['공급되고']),
    dict(ref=(22, 33, 16), lang='ko', en='given', words=['공급되고']),
    dict(ref=(22, 33, 16), lang='ko', en='him', words=['그#2']),
    dict(ref=(22, 33, 16), lang='ko', en='his#2', words=['그#3']),
    dict(ref=(22, 33, 16), lang='ko', en='waters', words=['물은']),
    dict(ref=(22, 33, 16), lang='ko', en='shall#4', words=['아니하리라']),
    dict(ref=(22, 33, 16), lang='ko', en='be#3', words=['아니하리라']),
    dict(ref=(22, 33, 16), lang='ko', en='sure', words=['끊치지', '아니하리라']),

    dict(ref=(22, 33, 17), lang='ko', en='Thine', words=['너의']),
    dict(ref=(22, 33, 17), lang='ko', en='eyes', words=['눈은']),
    dict(ref=(22, 33, 17), lang='ko', en='shall#1', words=['보며']),
    dict(ref=(22, 33, 17), lang='ko', en='see', words=['보며']),
    dict(ref=(22, 33, 17), lang='ko', en='the#1', words=['왕을']),
    dict(ref=(22, 33, 17), lang='ko', en='king', words=['왕을']),
    dict(ref=(22, 33, 17), lang='ko', en='in', words=['중의']),
    dict(ref=(22, 33, 17), lang='ko', en='his', words=['그']),
    dict(ref=(22, 33, 17), lang='ko', en='beauty', words=['영광']),
    dict(ref=(22, 33, 17), lang='ko', en='they', words=[]),
    dict(ref=(22, 33, 17), lang='ko', en='shall#2', words=['목도하겠고']),
    dict(ref=(22, 33, 17), lang='ko', en='behold', words=['목도하겠고']),
    dict(ref=(22, 33, 17), lang='ko', en='the#2', words=['땅을']),
    dict(ref=(22, 33, 17), lang='ko', en='land', words=['땅을']),
    dict(ref=(22, 33, 17), lang='ko', en='very', words=['광활한']),
    dict(ref=(22, 33, 17), lang='ko', en='far', words=['광활한']),
    dict(ref=(22, 33, 17), lang='ko', en='off', words=['광활한']),

    dict(ref=(22, 33, 20), lang='ko', en='Look', words=['보라']),
    dict(ref=(22, 33, 20), lang='ko', en='upon', words=['시온성을']),
    dict(ref=(22, 33, 20), lang='ko', en='Zion', words=['시온성을']),
    dict(ref=(22, 33, 20), lang='ko', en='city', words=['시온성을']),
    dict(ref=(22, 33, 20), lang='ko', en='our', words=['우리의']),
    dict(ref=(22, 33, 20), lang='ko', en='solemnities', words=['절기', '지키는']),
    dict(ref=(22, 33, 20), lang='ko', en='thine', words=['네']),
    dict(ref=(22, 33, 20), lang='ko', en='eyes', words=['눈에']),
    dict(ref=(22, 33, 20), lang='ko', en='shall#1', words=['보이리니']),
    dict(ref=(22, 33, 20), lang='ko', en='see', words=['보이리니']),
    dict(ref=(22, 33, 20), lang='ko', en='Jerusalem', words=['예루살렘이']),
    dict(ref=(22, 33, 20), lang='ko', en='quiet', words=['안정한']),
    dict(ref=(22, 33, 20), lang='ko', en='habitation', words=['처소된']),
    dict(ref=(22, 33, 20), lang='ko', en='a#2', words=['장막이라']),
    dict(ref=(22, 33, 20), lang='ko', en='tabernacle', words=['장막이라']),
    dict(ref=(22, 33, 20), lang='ko', en='that', words=['그것은']),
    dict(ref=(22, 33, 20), lang='ko', en='shall#2', words=['아니할#1']),
    dict(ref=(22, 33, 20), lang='ko', en='not#1', words=['아니할#1']),
    dict(ref=(22, 33, 20), lang='ko', en='be#1', words=['아니할#1']),
    dict(ref=(22, 33, 20), lang='ko', en='taken', words=['옮겨지지']),
    dict(ref=(22, 33, 20), lang='ko', en='down', words=['옮겨지지']),
    dict(ref=(22, 33, 20), lang='ko', en='not#2', words=['아니할#2']),
    dict(ref=(22, 33, 20), lang='ko', en='one', words=['아니할#2']),
    dict(ref=(22, 33, 20), lang='ko', en='stakes', words=['말뚝이']),
    dict(ref=(22, 33, 20), lang='ko', en='thereof#1', words=['그#1']),
    dict(ref=(22, 33, 20), lang='ko', en='shall#3', words=['것이요']),
    dict(ref=(22, 33, 20), lang='ko', en='ever', words=['영영히']),
    dict(ref=(22, 33, 20), lang='ko', en='be#2', words=['뽑히지']),
    dict(ref=(22, 33, 20), lang='ko', en='removed', words=['뽑히지']),
    dict(ref=(22, 33, 20), lang='ko', en='neither', words=['아니할#3']),
    dict(ref=(22, 33, 20), lang='ko', en='shall#4', words=['것이며']),
    dict(ref=(22, 33, 20), lang='ko', en='any', words=['하나도']),
    dict(ref=(22, 33, 20), lang='ko', en='cords', words=['줄이']),
    dict(ref=(22, 33, 20), lang='ko', en='thereof#2', words=['그#2']),
    dict(ref=(22, 33, 20), lang='ko', en='be#3', words=['끊치지']),
    dict(ref=(22, 33, 20), lang='ko', en='broken', words=['끊치지']),

    dict(ref=(22, 33, 21), lang='ko', en='But', words=[]),
    dict(ref=(22, 33, 21), lang='ko', en='there', words=['거기서']),
    dict(ref=(22, 33, 21), lang='ko', en='the', words=['여호와께서는']),
    dict(ref=(22, 33, 21), lang='ko', en='Lord', words=['여호와께서는']),
    dict(ref=(22, 33, 21), lang='ko', en='glorious', words=['위엄', '중에']),
    dict(ref=(22, 33, 21), lang='ko', en='will', words=['계시리니']),
    dict(ref=(22, 33, 21), lang='ko', en='be', words=['계시리니']),
    dict(ref=(22, 33, 21), lang='ko', en='unto', words=['함께']),
    dict(ref=(22, 33, 21), lang='ko', en='us', words=['우리와']),
    dict(ref=(22, 33, 21), lang='ko', en='a', words=['그곳은']),
    dict(ref=(22, 33, 21), lang='ko', en='place', words=['그곳은']),
    dict(ref=(22, 33, 21), lang='ko', en='broad', words=['넓은']),
    dict(ref=(22, 33, 21), lang='ko', en='of', words=['하수나']),
    dict(ref=(22, 33, 21), lang='ko', en='rivers', words=['하수나']),
    dict(ref=(22, 33, 21), lang='ko', en='and', words=['강이']),
    dict(ref=(22, 33, 21), lang='ko', en='streams', words=['강이']),
    dict(ref=(22, 33, 21), lang='ko', en='wherein', words=['둘림', '같을']),
    dict(ref=(22, 33, 21), lang='ko', en='shall#1', words=['것이라']),
    dict(ref=(22, 33, 21), lang='ko', en='go', words=['통행치']),
    dict(ref=(22, 33, 21), lang='ko', en='no', words=['못할']),
    dict(ref=(22, 33, 21), lang='ko', en='galley', words=['배나']),
    dict(ref=(22, 33, 21), lang='ko', en='with', words=['노질하는']),
    dict(ref=(22, 33, 21), lang='ko', en='oars', words=['노질하는']),
    dict(ref=(22, 33, 21), lang='ko', en='neither', words=['못할']),
    dict(ref=(22, 33, 21), lang='ko', en='shall#2', words=['것이라']),
    dict(ref=(22, 33, 21), lang='ko', en='gallant', words=['큰']),
    dict(ref=(22, 33, 21), lang='ko', en='ship', words=['배가']),
    dict(ref=(22, 33, 21), lang='ko', en='pass', words=['통행치']),
    dict(ref=(22, 33, 21), lang='ko', en='thereby', words=['통행치']),

    dict(ref=(22, 33, 23), lang='ko', en='Thy', words=['너의']),
    dict(ref=(22, 33, 23), lang='ko', en='tacklings', words=['돛대#1', '줄이']),
    dict(ref=(22, 33, 23), lang='ko', en='are', words=['풀렸었고']),
    dict(ref=(22, 33, 23), lang='ko', en='loosed', words=['풀렸었고']),
    dict(ref=(22, 33, 23), lang='ko', en='they#1', words=[]),
    dict(ref=(22, 33, 23), lang='ko', en='could#1', words=['못하였었고']),
    dict(ref=(22, 33, 23), lang='ko', en='not#1', words=['못하였었고']),
    dict(ref=(22, 33, 23), lang='ko', en='well', words=['튼튼히']),
    dict(ref=(22, 33, 23), lang='ko', en='strengthen', words=['하지']),
    dict(ref=(22, 33, 23), lang='ko', en='their', words=['밑을']),
    dict(ref=(22, 33, 23), lang='ko', en='mast', words=['돛대#2']),
    dict(ref=(22, 33, 23), lang='ko', en='they#2', words=[]),
    dict(ref=(22, 33, 23), lang='ko', en='could#2', words=['못하였느니라']),
    dict(ref=(22, 33, 23), lang='ko', en='not#2', words=['못하였느니라']),
    dict(ref=(22, 33, 23), lang='ko', en='spread', words=['달지']),
    dict(ref=(22, 33, 23), lang='ko', en='the#1', words=['돛을']),
    dict(ref=(22, 33, 23), lang='ko', en='sail', words=['돛을']),
    dict(ref=(22, 33, 23), lang='ko', en='then', words=['때가', '되면']),
    dict(ref=(22, 33, 23), lang='ko', en='is', words=['나누리니']),
    dict(ref=(22, 33, 23), lang='ko', en='the#2', words=['재물을#1']),
    dict(ref=(22, 33, 23), lang='ko', en='prey#1', words=['재물을#1']),
    dict(ref=(22, 33, 23), lang='ko', en='of', words=['탈취하여']),
    dict(ref=(22, 33, 23), lang='ko', en='spoil', words=['탈취하여']),
    dict(ref=(22, 33, 23), lang='ko', en='a', words=['많은']),
    dict(ref=(22, 33, 23), lang='ko', en='great', words=['많은']),
    dict(ref=(22, 33, 23), lang='ko', en='divided', words=['나누리니']),
    dict(ref=(22, 33, 23), lang='ko', en='the#3', words=['저는']),
    dict(ref=(22, 33, 23), lang='ko', en='lame', words=['저는', '자도']),
    dict(ref=(22, 33, 23), lang='ko', en='take', words=['취할', '것이며']),
    dict(ref=(22, 33, 23), lang='ko', en='the#4', words=['그']),
    dict(ref=(22, 33, 23), lang='ko', en='prey#2', words=['재물을#2']),

    dict(ref=(22, 33, 2), lang='ko', en='us', words=['우리에게']),
    dict(ref=(22, 33, 2), lang='ko', en='we', words=['우리가']),
    dict(ref=(22, 33, 2), lang='ko', en='for', words=['앙망하오니']),
    dict(ref=(22, 33, 2), lang='ko', en='be#2', words=['되소서']),
    dict(ref=(22, 33, 2), lang='ko', en='thou', words=['주는']),
    dict(ref=(22, 33, 2), lang='ko', en='their', words=['우리의#1']),
    dict(ref=(22, 33, 2), lang='ko', en='every', words=['아침마다']),
    dict(ref=(22, 33, 2), lang='ko', en='our', words=['우리의#2']),
    dict(ref=(22, 33, 2), lang='ko', en='also', words=[]),
    dict(ref=(22, 33, 2), lang='ko', en='in', words=['때에']),
    dict(ref=(22, 33, 2), lang='ko', en='the', words=['때에']),
    dict(ref=(22, 33, 2), lang='ko', en='of', words=['환난']),

    dict(ref=(22, 33, 4), lang='ko', en='And', words=[]),
    dict(ref=(22, 33, 4), lang='ko', en='your', words=['너희']),
    dict(ref=(22, 33, 4), lang='ko', en='spoil', words=['노략물을']),
    dict(ref=(22, 33, 4), lang='ko', en='shall#1', words=['것이며']),
    dict(ref=(22, 33, 4), lang='ko', en='be', words=['것이며']),
    dict(ref=(22, 33, 4), lang='ko', en='gathered', words=['모을']),
    dict(ref=(22, 33, 4), lang='ko', en='like', words=['같이#1']),
    dict(ref=(22, 33, 4), lang='ko', en='gathering', words=['모임']),
    dict(ref=(22, 33, 4), lang='ko', en='caterpiller', words=['황충의']),
    dict(ref=(22, 33, 4), lang='ko', en='as', words=['같이#2']),
    dict(ref=(22, 33, 4), lang='ko', en='running', words=['뛰어#1', '오름']),
    dict(ref=(22, 33, 4), lang='ko', en='fro', words=['뛰어#1', '오름']),
    dict(ref=(22, 33, 4), lang='ko', en='locusts', words=['메뚜기의']),
    dict(ref=(22, 33, 4), lang='ko', en='shall#2', words=['오르리라']),
    dict(ref=(22, 33, 4), lang='ko', en='he', words=['그들이']),
    dict(ref=(22, 33, 4), lang='ko', en='run', words=['뛰어#2', '오르리라']),
    dict(ref=(22, 33, 4), lang='ko', en='upon', words=['위로']),
    dict(ref=(22, 33, 4), lang='ko', en='them', words=['그']),

    dict(ref=(22, 33, 5), lang='ko', en='Lord', words=['여호와께서는']),
    dict(ref=(22, 33, 5), lang='ko', en='is', words=['지존하시니']),
    dict(ref=(22, 33, 5), lang='ko', en='exalted', words=['지존하시니']),
    dict(ref=(22, 33, 5), lang='ko', en='for', words=['이는']),
    dict(ref=(22, 33, 5), lang='ko', en='he#1', words=['이는']),
    dict(ref=(22, 33, 5), lang='ko', en='dwelleth', words=['거하심이요']),
    dict(ref=(22, 33, 5), lang='ko', en='on', words=['데']),
    dict(ref=(22, 33, 5), lang='ko', en='high', words=['높은']),
    dict(ref=(22, 33, 5), lang='ko', en='he#2', words=[]),
    dict(ref=(22, 33, 5), lang='ko', en='hath', words=['하심이라']),
    dict(ref=(22, 33, 5), lang='ko', en='filled', words=['충만케']),
    dict(ref=(22, 33, 5), lang='ko', en='Zion', words=['시온에']),
    dict(ref=(22, 33, 5), lang='ko', en='with', words=[]),
    dict(ref=(22, 33, 5), lang='ko', en='judgment', words=['공평과']),
    dict(ref=(22, 33, 5), lang='ko', en='and', words=['의로']),
    dict(ref=(22, 33, 5), lang='ko', en='righteousness', words=['의로']),

    dict(ref=(22, 33, 6), lang='ko', en='And', words=[]),
    dict(ref=(22, 33, 6), lang='ko', en='wisdom', words=['지혜와']),
    dict(ref=(22, 33, 6), lang='ko', en='and#1', words=['지식이']),
    dict(ref=(22, 33, 6), lang='ko', en='knowledge', words=['지식이']),
    dict(ref=(22, 33, 6), lang='ko', en='shall', words=['것이니']),
    dict(ref=(22, 33, 6), lang='ko', en='be', words=['것이니']),
    dict(ref=(22, 33, 6), lang='ko', en='stability', words=['평안함이', '있으며']),
    dict(ref=(22, 33, 6), lang='ko', en='of#1', words=['시대에']),
    dict(ref=(22, 33, 6), lang='ko', en='thy', words=['너의#1']),
    dict(ref=(22, 33, 6), lang='ko', en='times', words=['시대에']),
    dict(ref=(22, 33, 6), lang='ko', en='and#2', words=['풍성할']),
    dict(ref=(22, 33, 6), lang='ko', en='strength', words=['풍성할']),
    dict(ref=(22, 33, 6), lang='ko', en='of#2', words=['구원과']),
    dict(ref=(22, 33, 6), lang='ko', en='salvation', words=['구원과']),
    dict(ref=(22, 33, 6), lang='ko', en='fear', words=['경외함이']),
    dict(ref=(22, 33, 6), lang='ko', en='of#3', words=['여호와를']),
    dict(ref=(22, 33, 6), lang='ko', en='Lord', words=['여호와를']),
    dict(ref=(22, 33, 6), lang='ko', en='is', words=['보배니라']),
    dict(ref=(22, 33, 6), lang='ko', en='his', words=['너의#2']),
    dict(ref=(22, 33, 6), lang='ko', en='treasure', words=['보배니라']),

    dict(ref=(22, 33, 8), lang='ko', en='highways', words=['대로가']),
    dict(ref=(22, 33, 8), lang='ko', en='lie', words=['황폐하여']),
    dict(ref=(22, 33, 8), lang='ko', en='waste', words=['황폐하여']),
    dict(ref=(22, 33, 8), lang='ko', en='wayfaring', words=['행인이']),
    dict(ref=(22, 33, 8), lang='ko', en='man#1', words=['행인이']),
    dict(ref=(22, 33, 8), lang='ko', en='ceaseth', words=['끊치며']),
    dict(ref=(22, 33, 8), lang='ko', en='he#1', words=['대적이']),
    dict(ref=(22, 33, 8), lang='ko', en='hath#1', words=['파하고']),
    dict(ref=(22, 33, 8), lang='ko', en='broken', words=['파하고']),
    dict(ref=(22, 33, 8), lang='ko', en='covenant', words=['조약을']),
    dict(ref=(22, 33, 8), lang='ko', en='he#2', words=[]),
    dict(ref=(22, 33, 8), lang='ko', en='hath#2', words=['멸시하며']),
    dict(ref=(22, 33, 8), lang='ko', en='despised', words=['멸시하며']),
    dict(ref=(22, 33, 8), lang='ko', en='cities', words=['성읍들을']),
    dict(ref=(22, 33, 8), lang='ko', en='he#3', words=[]),
    dict(ref=(22, 33, 8), lang='ko', en='regardeth', words=['생각지']),
    dict(ref=(22, 33, 8), lang='ko', en='no', words=['아니하며']),
    dict(ref=(22, 33, 8), lang='ko', en='man#2', words=['사람을']),

    dict(ref=(22, 33, 9), lang='ko', en='earth', words=['땅이']),
    dict(ref=(22, 33, 9), lang='ko', en='mourneth', words=['슬퍼하고']),
    dict(ref=(22, 33, 9), lang='ko', en='and#1', words=['쇠잔하며']),
    dict(ref=(22, 33, 9), lang='ko', en='languisheth', words=['쇠잔하며']),
    dict(ref=(22, 33, 9), lang='ko', en='Lebanon', words=['레바논은']),
    dict(ref=(22, 33, 9), lang='ko', en='is#1', words=['부끄러워']),
    dict(ref=(22, 33, 9), lang='ko', en='ashamed', words=['부끄러워']),
    dict(ref=(22, 33, 9), lang='ko', en='and#2', words=['마르고']),
    dict(ref=(22, 33, 9), lang='ko', en='hewn', words=['마르고']),
    dict(ref=(22, 33, 9), lang='ko', en='down', words=['마르고']),
    dict(ref=(22, 33, 9), lang='ko', en='Sharon', words=['사론은']),
    dict(ref=(22, 33, 9), lang='ko', en='is#2', words=['같고']),
    dict(ref=(22, 33, 9), lang='ko', en='like', words=['같고']),
    dict(ref=(22, 33, 9), lang='ko', en='wilderness', words=['사막과']),
    dict(ref=(22, 33, 9), lang='ko', en='Bashan', words=['바산']),
    dict(ref=(22, 33, 9), lang='ko', en='and#4', words=['갈멜은']),
    dict(ref=(22, 33, 9), lang='ko', en='Carmel', words=['갈멜은']),
    dict(ref=(22, 33, 9), lang='ko', en='shake', words=['떨어치는도다']),
    dict(ref=(22, 33, 9), lang='ko', en='off', words=['떨어치는도다']),
    dict(ref=(22, 33, 9), lang='ko', en='their', words=['목엽을']),
    dict(ref=(22, 33, 9), lang='ko', en='fruits', words=['목엽을']),

    dict(ref=(22, 33, 11), lang='ko', en='Ye', words=['너희가']),
    dict(ref=(22, 33, 11), lang='ko', en='shall#1', words=['것이며#1']),
    dict(ref=(22, 33, 11), lang='ko', en='conceive', words=['잉태하고']),
    dict(ref=(22, 33, 11), lang='ko', en='chaff', words=['겨를']),
    dict(ref=(22, 33, 11), lang='ko', en='ye', words=['너희가']),
    dict(ref=(22, 33, 11), lang='ko', en='shall#2', words=['것이며#1']),
    dict(ref=(22, 33, 11), lang='ko', en='bring', words=['해산할']),
    dict(ref=(22, 33, 11), lang='ko', en='forth', words=['해산할']),
    dict(ref=(22, 33, 11), lang='ko', en='stubble', words=['짚을']),
    dict(ref=(22, 33, 11), lang='ko', en='your', words=['너희의']),
    dict(ref=(22, 33, 11), lang='ko', en='breath', words=['호흡은']),
    dict(ref=(22, 33, 11), lang='ko', en='as', words=['되어']),
    dict(ref=(22, 33, 11), lang='ko', en='fire', words=['불이']),
    dict(ref=(22, 33, 11), lang='ko', en='shall#3', words=['것이며#2']),
    dict(ref=(22, 33, 11), lang='ko', en='devour', words=['삼킬']),
    dict(ref=(22, 33, 11), lang='ko', en='you', words=['너희를']),

    dict(ref=(22, 33, 12), lang='ko', en='And', words=[]),
    dict(ref=(22, 33, 12), lang='ko', en='the#1', words=['민족들은']),
    dict(ref=(22, 33, 12), lang='ko', en='people', words=['민족들은']),
    dict(ref=(22, 33, 12), lang='ko', en='shall#1', words=['같겠고']),
    dict(ref=(22, 33, 12), lang='ko', en='be#1', words=['같겠고']),
    dict(ref=(22, 33, 12), lang='ko', en='as#1', words=['같겠고']),
    dict(ref=(22, 33, 12), lang='ko', en='burnings', words=['불에#1', '굽는']),
    dict(ref=(22, 33, 12), lang='ko', en='lime', words=['횟돌']),
    dict(ref=(22, 33, 12), lang='ko', en='as#2', words=['같으리로다']),
    dict(ref=(22, 33, 12), lang='ko', en='thorns', words=['가시나무']),
    dict(ref=(22, 33, 12), lang='ko', en='cut', words=['베어서']),
    dict(ref=(22, 33, 12), lang='ko', en='up', words=['베어서']),
    dict(ref=(22, 33, 12), lang='ko', en='shall#2', words=['같으리로다']),
    dict(ref=(22, 33, 12), lang='ko', en='they', words=[]),
    dict(ref=(22, 33, 12), lang='ko', en='be#2', words=['사르는']),
    dict(ref=(22, 33, 12), lang='ko', en='burned', words=['사르는']),
    dict(ref=(22, 33, 12), lang='ko', en='in', words=['불에#2']),
    dict(ref=(22, 33, 12), lang='ko', en='fire', words=['불에#2']),

    dict(ref=(22, 33, 24), lang='ko', en='And', words=[]),
    dict(ref=(22, 33, 24), lang='ko', en='the#1', words=['그']),
    dict(ref=(22, 33, 24), lang='ko', en='inhabitant', words=['거민은']),
    dict(ref=(22, 33, 24), lang='ko', en='shall#1', words=['것이라']),
    dict(ref=(22, 33, 24), lang='ko', en='not', words=['아니할']),
    dict(ref=(22, 33, 24), lang='ko', en='say', words=['하지']),
    dict(ref=(22, 33, 24), lang='ko', en='I', words=['내가']),
    dict(ref=(22, 33, 24), lang='ko', en='am', words=['병들었노라']),
    dict(ref=(22, 33, 24), lang='ko', en='sick', words=['병들었노라']),
    dict(ref=(22, 33, 24), lang='ko', en='people', words=['백성이']),
    dict(ref=(22, 33, 24), lang='ko', en='that', words=['거하는']),
    dict(ref=(22, 33, 24), lang='ko', en='dwell', words=['거하는']),
    dict(ref=(22, 33, 24), lang='ko', en='therein', words=['거기']),
    dict(ref=(22, 33, 24), lang='ko', en='shall#2', words=['받으리라']),
    dict(ref=(22, 33, 24), lang='ko', en='be', words=['받으리라']),
    dict(ref=(22, 33, 24), lang='ko', en='forgiven', words=['사죄함을', '받으리라']),
    dict(ref=(22, 33, 24), lang='ko', en='their', words=['사죄함을']),
    dict(ref=(22, 33, 24), lang='ko', en='iniquity', words=['사죄함을']),

    # ---- 이사야 32장 ----
    # 32:1 '장차'는 '앞으로' 라는 뜻으로 개역한글이 넣은 말이라 짝이 없다.
    dict(ref=(22, 32, 1), lang='ko', en='a', words=['한']),
    dict(ref=(22, 32, 1), lang='ko', en='shall#1', words=['것이요']),
    dict(ref=(22, 32, 1), lang='ko', en='reign', words=['통치할']),
    dict(ref=(22, 32, 1), lang='ko', en='in#1', words=['의로']),
    dict(ref=(22, 32, 1), lang='ko', en='righteousness', words=['의로']),
    dict(ref=(22, 32, 1), lang='ko', en='shall#2', words=['것이며']),
    dict(ref=(22, 32, 1), lang='ko', en='rule', words=['정사할']),
    dict(ref=(22, 32, 1), lang='ko', en='in#2', words=['공평으로']),
    dict(ref=(22, 32, 1), lang='ko', en='judgment', words=['공평으로']),
    dict(ref=(22, 32, 3), lang='ko', en='see', words=['보는']),
    dict(ref=(22, 32, 3), lang='ko', en='them#1', words=['자의#1']),
    dict(ref=(22, 32, 3), lang='ko', en='that#1', words=['자의#1']),
    dict(ref=(22, 32, 3), lang='ko', en='eyes', words=['눈이']),
    dict(ref=(22, 32, 3), lang='ko', en='be', words=['감기지']),
    dict(ref=(22, 32, 3), lang='ko', en='dim', words=['감기지']),
    dict(ref=(22, 32, 3), lang='ko', en='not', words=['아니할']),
    dict(ref=(22, 32, 3), lang='ko', en='shall#1', words=['것이요']),
    dict(ref=(22, 32, 3), lang='ko', en='hear', words=['듣는']),
    dict(ref=(22, 32, 3), lang='ko', en='them#2', words=['자의#2']),
    dict(ref=(22, 32, 3), lang='ko', en='that#2', words=['자의#2']),
    dict(ref=(22, 32, 3), lang='ko', en='ears', words=['귀가']),
    dict(ref=(22, 32, 3), lang='ko', en='hearken', words=['기울어질']),
    dict(ref=(22, 32, 3), lang='ko', en='shall#2', words=['것이며']),

    dict(ref=(22, 32, 4), lang='ko', en='the#1', words=['조급한']),
    dict(ref=(22, 32, 4), lang='ko', en='rash', words=['조급한', '자의#1']),
    dict(ref=(22, 32, 4), lang='ko', en='heart', words=['마음이']),
    dict(ref=(22, 32, 4), lang='ko', en='knowledge', words=['지식을']),
    dict(ref=(22, 32, 4), lang='ko', en='understand', words=['깨닫고']),
    dict(ref=(22, 32, 4), lang='ko', en='stammerers', words=['어눌한', '자의#2']),
    dict(ref=(22, 32, 4), lang='ko', en='tongue', words=['혀가']),
    dict(ref=(22, 32, 4), lang='ko', en='be', words=['민첩하여']),
    dict(ref=(22, 32, 4), lang='ko', en='ready', words=['민첩하여']),
    dict(ref=(22, 32, 4), lang='ko', en='speak', words=['말을']),
    dict(ref=(22, 32, 4), lang='ko', en='plainly', words=['분명히']),
    dict(ref=(22, 32, 4), lang='ko', en='to', words=['할']),
    dict(ref=(22, 32, 4), lang='ko', en='shall#2', words=['것이라']),

    dict(ref=(22, 32, 5), lang='ko', en='vile', words=['어리석은']),
    dict(ref=(22, 32, 5), lang='ko', en='person', words=['자를#1']),
    dict(ref=(22, 32, 5), lang='ko', en='more', words=['다시#1']),
    dict(ref=(22, 32, 5), lang='ko', en='called', words=['칭하지']),
    dict(ref=(22, 32, 5), lang='ko', en='liberal', words=['존귀하다']),
    dict(ref=(22, 32, 5), lang='ko', en='no', words=['아니하겠고']),
    dict(ref=(22, 32, 5), lang='ko', en='churl', words=['궤휼한', '자를#2']),
    dict(ref=(22, 32, 5), lang='ko', en='nor', words=['다시#2', '아니하리니']),
    dict(ref=(22, 32, 5), lang='ko', en='said', words=['말하지']),
    dict(ref=(22, 32, 5), lang='ko', en='bountiful', words=['정대하다']),

    dict(ref=(22, 32, 6), lang='ko', en='For', words=['이는']),
    dict(ref=(22, 32, 6), lang='ko', en='vile', words=['어리석은#1']),
    dict(ref=(22, 32, 6), lang='ko', en='person', words=['자는']),
    dict(ref=(22, 32, 6), lang='ko', en='speak', words=['말하며']),
    dict(ref=(22, 32, 6), lang='ko', en='villany', words=['어리석은#2', '것을#1']),
    dict(ref=(22, 32, 6), lang='ko', en='his', words=['그']),
    dict(ref=(22, 32, 6), lang='ko', en='heart', words=['마음에']),
    dict(ref=(22, 32, 6), lang='ko', en='iniquity', words=['불의를']),
    dict(ref=(22, 32, 6), lang='ko', en='work', words=['품어']),
    dict(ref=(22, 32, 6), lang='ko', en='hypocrisy', words=['간사를']),
    dict(ref=(22, 32, 6), lang='ko', en='practise', words=['행하며']),
    dict(ref=(22, 32, 6), lang='ko', en='utter', words=['패역한', '말로']),
    dict(ref=(22, 32, 6), lang='ko', en='error', words=['패역한', '말로']),
    dict(ref=(22, 32, 6), lang='ko', en='against', words=['거스리며']),
    dict(ref=(22, 32, 6), lang='ko', en='Lord', words=['여호와를']),
    dict(ref=(22, 32, 6), lang='ko', en='the#4', words=['주린']),
    dict(ref=(22, 32, 6), lang='ko', en='hungry', words=['주린', '자의#1']),
    dict(ref=(22, 32, 6), lang='ko', en='soul', words=['심령을']),
    dict(ref=(22, 32, 6), lang='ko', en='empty', words=['비게']),
    dict(ref=(22, 32, 6), lang='ko', en='make', words=['하며']),
    dict(ref=(22, 32, 6), lang='ko', en='the#6', words=['목마른']),
    dict(ref=(22, 32, 6), lang='ko', en='thirsty', words=['목마른', '자의#2']),
    dict(ref=(22, 32, 6), lang='ko', en='drink', words=['마시는', '것을#2']),
    dict(ref=(22, 32, 6), lang='ko', en='fail', words=['없어지게']),

    dict(ref=(22, 32, 7), lang='ko', en='churl', words=['궤휼한', '자는']),
    dict(ref=(22, 32, 7), lang='ko', en='also', words=['그']),
    dict(ref=(22, 32, 7), lang='ko', en='instruments', words=['그릇이']),
    dict(ref=(22, 32, 7), lang='ko', en='evil', words=['악하여']),
    dict(ref=(22, 32, 7), lang='ko', en='wicked', words=['악한']),
    dict(ref=(22, 32, 7), lang='ko', en='devices', words=['계획을']),
    dict(ref=(22, 32, 7), lang='ko', en='deviseth', words=['베풀어']),
    dict(ref=(22, 32, 7), lang='ko', en='lying', words=['거짓말로']),
    dict(ref=(22, 32, 7), lang='ko', en='words', words=['거짓말로']),
    dict(ref=(22, 32, 7), lang='ko', en='poor', words=['가련한', '자를']),
    dict(ref=(22, 32, 7), lang='ko', en='destroy', words=['멸하며']),
    dict(ref=(22, 32, 7), lang='ko', en='needy', words=['빈핍한', '자가']),
    dict(ref=(22, 32, 7), lang='ko', en='speaketh', words=['말을']),
    dict(ref=(22, 32, 7), lang='ko', en='right', words=['바르게']),

    dict(ref=(22, 32, 9), lang='ko', en='ye#1', words=['너희#1']),
    dict(ref=(22, 32, 9), lang='ko', en='at', words=['안일한']),
    dict(ref=(22, 32, 9), lang='ko', en='ease', words=['안일한']),
    dict(ref=(22, 32, 9), lang='ko', en='women', words=['부녀들아']),
    dict(ref=(22, 32, 9), lang='ko', en='Rise', words=['일어나']),
    dict(ref=(22, 32, 9), lang='ko', en='up', words=['일어나']),
    dict(ref=(22, 32, 9), lang='ko', en='my#1', words=['내#1']),
    dict(ref=(22, 32, 9), lang='ko', en='voice', words=['목소리를']),
    dict(ref=(22, 32, 9), lang='ko', en='hear', words=['들을지어다']),
    dict(ref=(22, 32, 9), lang='ko', en='ye#2', words=['너희#2']),
    dict(ref=(22, 32, 9), lang='ko', en='careless', words=['염려', '없는']),
    dict(ref=(22, 32, 9), lang='ko', en='daughters', words=['딸들아']),
    dict(ref=(22, 32, 9), lang='ko', en='my#2', words=['내#2']),
    dict(ref=(22, 32, 9), lang='ko', en='speech', words=['말에']),
    dict(ref=(22, 32, 9), lang='ko', en='ear', words=['귀를']),
    dict(ref=(22, 32, 9), lang='ko', en='give', words=['기울일지라']),

    dict(ref=(22, 32, 10), lang='ko', en='days', words=['일']),
    dict(ref=(22, 32, 10), lang='ko', en='years', words=['년']),
    dict(ref=(22, 32, 10), lang='ko', en='Many', words=['남짓이']),
    dict(ref=(22, 32, 10), lang='ko', en='ye#1', words=['너희가']),
    dict(ref=(22, 32, 10), lang='ko', en='troubled', words=['당황하여', '하리니']),
    dict(ref=(22, 32, 10), lang='ko', en='ye#2', words=['너희']),
    dict(ref=(22, 32, 10), lang='ko', en='careless', words=['염려', '없는']),
    dict(ref=(22, 32, 10), lang='ko', en='women', words=['여자들아']),
    dict(ref=(22, 32, 10), lang='ko', en='vintage', words=['포도', '수확이']),
    dict(ref=(22, 32, 10), lang='ko', en='fail', words=['없으며']),
    dict(ref=(22, 32, 10), lang='ko', en='the#2', words=['기한이']),
    dict(ref=(22, 32, 10), lang='ko', en='gathering', words=['열매', '거두는', '기한이']),
    dict(ref=(22, 32, 10), lang='ko', en='come', words=['이르지']),
    dict(ref=(22, 32, 10), lang='ko', en='not', words=['않을']),
    dict(ref=(22, 32, 10), lang='ko', en='shall#3', words=['것임이니라']),

    dict(ref=(22, 32, 11), lang='ko', en='Tremble', words=['떨지어다']),
    dict(ref=(22, 32, 11), lang='ko', en='ye#1', words=['너희#1']),
    dict(ref=(22, 32, 11), lang='ko', en='at', words=['안일한']),
    dict(ref=(22, 32, 11), lang='ko', en='ease', words=['안일한']),
    dict(ref=(22, 32, 11), lang='ko', en='women', words=['여자들아']),
    dict(ref=(22, 32, 11), lang='ko', en='be', words=['당황하여']),
    dict(ref=(22, 32, 11), lang='ko', en='troubled', words=['당황하여', '할지어다']),
    dict(ref=(22, 32, 11), lang='ko', en='ye#2', words=['너희#2']),
    dict(ref=(22, 32, 11), lang='ko', en='careless', words=['염려', '없는']),
    dict(ref=(22, 32, 11), lang='ko', en='ones', words=['자들아']),
    dict(ref=(22, 32, 11), lang='ko', en='strip', words=['벗어']),
    dict(ref=(22, 32, 11), lang='ko', en='you#1', words=['옷을']),
    dict(ref=(22, 32, 11), lang='ko', en='you#2', words=['몸을']),
    dict(ref=(22, 32, 11), lang='ko', en='make', words=['드러내고']),
    dict(ref=(22, 32, 11), lang='ko', en='bare', words=['드러내고']),
    dict(ref=(22, 32, 11), lang='ko', en='sackcloth', words=['베로']),
    dict(ref=(22, 32, 11), lang='ko', en='your', words=['허리를']),
    dict(ref=(22, 32, 11), lang='ko', en='loins', words=['허리를']),
    dict(ref=(22, 32, 11), lang='ko', en='gird', words=['동일지어다']),

    dict(ref=(22, 32, 14), lang='ko', en='Because', words=['대저']),
    dict(ref=(22, 32, 14), lang='ko', en='palaces', words=['궁전이']),
    dict(ref=(22, 32, 14), lang='ko', en='forsaken', words=['폐한', '바']),
    dict(ref=(22, 32, 14), lang='ko', en='shall#1', words=['되며#1']),
    dict(ref=(22, 32, 14), lang='ko', en='be#1', words=['되며#1']),
    dict(ref=(22, 32, 14), lang='ko', en='multitude', words=['인구', '많던']),
    dict(ref=(22, 32, 14), lang='ko', en='city', words=['성읍이']),
    dict(ref=(22, 32, 14), lang='ko', en='shall#2', words=['적막하며']),
    dict(ref=(22, 32, 14), lang='ko', en='be#2', words=['적막하며']),
    dict(ref=(22, 32, 14), lang='ko', en='left', words=['적막하며']),
    dict(ref=(22, 32, 14), lang='ko', en='the#4', words=['산과']),
    dict(ref=(22, 32, 14), lang='ko', en='forts', words=['산과']),
    dict(ref=(22, 32, 14), lang='ko', en='and', words=['산과']),
    dict(ref=(22, 32, 14), lang='ko', en='towers', words=['망대가']),
    dict(ref=(22, 32, 14), lang='ko', en='shall#3', words=['되며#2', '것임이어니와']),
    dict(ref=(22, 32, 14), lang='ko', en='be#3', words=['되며#2', '될']),
    dict(ref=(22, 32, 14), lang='ko', en='dens', words=['굴혈이']),
    dict(ref=(22, 32, 14), lang='ko', en='for#2', words=['영영히']),
    dict(ref=(22, 32, 14), lang='ko', en='ever', words=['영영히']),
    dict(ref=(22, 32, 14), lang='ko', en='wild', words=['들나귀의']),
    dict(ref=(22, 32, 14), lang='ko', en='asses', words=['들나귀의']),
    dict(ref=(22, 32, 14), lang='ko', en='joy', words=['즐겨하는']),
    dict(ref=(22, 32, 14), lang='ko', en='a#1', words=['곳과']),
    dict(ref=(22, 32, 14), lang='ko', en='flocks', words=['양', '떼의']),
    dict(ref=(22, 32, 14), lang='ko', en='pasture', words=['풀', '먹는']),
    dict(ref=(22, 32, 14), lang='ko', en='a#2', words=['곳이']),

    dict(ref=(22, 53, 2), lang='ko', en='he#1', words=['그는']),
    dict(ref=(22, 53, 2), lang='ko', en='shall#1', words=[]),
    dict(ref=(22, 53, 2), lang='ko', en='grow', words=['자라나기를']),
    dict(ref=(22, 53, 2), lang='ko', en='up', words=['자라나기를']),
    dict(ref=(22, 53, 2), lang='ko', en='him#1', words=['주']),
    dict(ref=(22, 53, 2), lang='ko', en='as#1', words=['같고']),
    dict(ref=(22, 53, 2), lang='ko', en='plant', words=['순']),
    dict(ref=(22, 53, 2), lang='ko', en='as#2', words=['같아서']),
    dict(ref=(22, 53, 2), lang='ko', en='out', words=['나온']),
    dict(ref=(22, 53, 2), lang='ko', en='of', words=['나온']),
    dict(ref=(22, 53, 2), lang='ko', en='no#1', words=['없고']),
    dict(ref=(22, 53, 2), lang='ko', en='form', words=['고운', '모양도']),
    dict(ref=(22, 53, 2), lang='ko', en='nor', words=['없은즉']),
    dict(ref=(22, 53, 2), lang='ko', en='comeliness', words=['풍채도']),
    dict(ref=(22, 53, 2), lang='ko', en='when', words=['보기에']),
    dict(ref=(22, 53, 2), lang='ko', en='we#1', words=['우리의']),
    dict(ref=(22, 53, 2), lang='ko', en='shall#2', words=[]),
    dict(ref=(22, 53, 2), lang='ko', en='see', words=['보기에']),
    dict(ref=(22, 53, 2), lang='ko', en='no#2', words=['없도다']),
    dict(ref=(22, 53, 2), lang='ko', en='beauty', words=['아름다운', '것이']),
    dict(ref=(22, 53, 2), lang='ko', en='should', words=[]),
    dict(ref=(22, 53, 2), lang='ko', en='desire', words=['흠모할만한']),

    dict(ref=(22, 53, 3), lang='ko', en='He', words=['그는']),
    dict(ref=(22, 53, 3), lang='ko', en='despised#1', words=['멸시를#1', '받아서']),
    dict(ref=(22, 53, 3), lang='ko', en='rejected', words=['싫어버린', '바', '되었으며']),
    dict(ref=(22, 53, 3), lang='ko', en='of#1', words=['사람에게']),
    dict(ref=(22, 53, 3), lang='ko', en='men', words=['사람에게']),
    dict(ref=(22, 53, 3), lang='ko', en='sorrows', words=['간고를']),
    dict(ref=(22, 53, 3), lang='ko', en='grief', words=['질고를']),
    dict(ref=(22, 53, 3), lang='ko', en='acquainted', words=['아는']),
    dict(ref=(22, 53, 3), lang='ko', en='man', words=['자라']),
    dict(ref=(22, 53, 3), lang='ko', en='as', words=['마치', '같아서']),
    dict(ref=(22, 53, 3), lang='ko', en='our', words=['얼굴을']),
    dict(ref=(22, 53, 3), lang='ko', en='him#1', words=['사람들에게']),
    dict(ref=(22, 53, 3), lang='ko', en='was', words=['당하였고']),
    dict(ref=(22, 53, 3), lang='ko', en='despised#2', words=['멸시를#2', '당하였고']),
    dict(ref=(22, 53, 3), lang='ko', en='we#2', words=['우리도']),
    dict(ref=(22, 53, 3), lang='ko', en='esteemed', words=['귀히', '여기지']),
    dict(ref=(22, 53, 3), lang='ko', en='him#2', words=['그를']),
    dict(ref=(22, 53, 3), lang='ko', en='not', words=['아니하였도다']),
    dict(ref=(34, 2, 16), lang='ko', en='shall#1', words=[]),
    dict(ref=(34, 2, 16), lang='ko', en='shall#2', words=[]),
    dict(ref=(34, 2, 16), lang='ko', en='on', words=[]),
    dict(ref=(34, 2, 16), lang='or', en='let', words=['וְהֵעָרֵל']),
    dict(ref=(34, 2, 16), lang='or', en='foreskin', words=['וְהֵעָרֵל']),
    dict(ref=(34, 2, 16), lang='or', en='be#1', words=['וְהֵעָרֵל']),
    dict(ref=(34, 2, 16), lang='or', en='uncovered', words=['וְהֵעָרֵל']),
    dict(ref=(34, 2, 16), lang='or', en='shameful', words=['וְקִיקָלוֹן']),
    dict(ref=(34, 2, 16), lang='or', en='spewing', words=['וְקִיקָלוֹן']),
    dict(ref=(34, 2, 16), lang='or', en='Lord', words=['יְהוָה']),
    dict(ref=(34, 2, 17), lang='ko', en='afraid', words=['두렵게하여']),
    dict(ref=(34, 2, 17), lang='ko', en='shall', words=[]),
    dict(ref=(34, 2, 18), lang='ko', en='maker#1', words=['만든#1', '자에게']),
    dict(ref=(34, 2, 18), lang='ko', en='maker#2', words=['만든#3', '자가']),

    dict(ref=(34, 2, 18), lang='ko', en='graven#1', words=['새긴']),
    dict(ref=(34, 2, 18), lang='ko', en='image#1', words=['우상은#1']),
    dict(ref=(34, 2, 18), lang='ko', en='graven#2', words=['새겨']),
    dict(ref=(34, 2, 18), lang='ko', en='molten', words=['부어', '만든#2']),
    dict(ref=(34, 2, 18), lang='ko', en='image#2', words=['우상은#2']),
    dict(ref=(34, 2, 18), lang='ko', en='dumb', words=['말하지', '못하는']),
    dict(ref=(34, 2, 18), lang='ko', en='idols', words=['우상을']),
    dict(ref=(34, 2, 18), lang='ko', en='profiteth', words=['유익하겠느냐#1', '유익하겠느냐#2']),
    dict(ref=(34, 2, 18), lang='ko', en='What', words=['무엇이#1', '무엇이#2']),
    dict(ref=(34, 2, 19), lang='ko', en='dumb', words=['말하지', '못하는']),
    dict(ref=(34, 2, 19), lang='ko', en='saith', words=['하며']),
    dict(ref=(34, 2, 19), lang='ko', en='at', words=['도무지']),
    dict(ref=(34, 2, 19), lang='ko', en='all', words=['도무지']),
    dict(ref=(34, 2, 20), lang='ko', en='all', words=['온']),
    dict(ref=(34, 2, 20), lang='ko', en='the#2', words=['천하는']),
    dict(ref=(34, 2, 20), lang='ko', en='earth', words=['천하는']),
    dict(ref=(34, 2, 20), lang='ko', en='is', words=['계시니']),
    dict(ref=(34, 2, 20), lang='ko', en='him', words=['그#2']),
    dict(ref=(34, 3, 1), lang='ko', en='prayer', words=['기도라']),

    dict(ref=(34, 3, 2), lang='ko', en='O#1', words=['여호와여#1']),
    dict(ref=(34, 3, 2), lang='ko', en='O#2', words=['여호와여#2']),
    dict(ref=(34, 3, 2), lang='ko', en='I', words=['내가']),
    dict(ref=(34, 3, 2), lang='ko', en='heard', words=['듣고']),
    dict(ref=(34, 3, 2), lang='ko', en='thy#1', words=['주께', '대한', '소문을']),
    dict(ref=(34, 3, 2), lang='ko', en='speech', words=['소문을']),
    dict(ref=(34, 3, 2), lang='ko', en='was', words=['놀랐나이다']),
    dict(ref=(34, 3, 2), lang='ko', en='thy#2', words=['주의']),
    dict(ref=(34, 3, 2), lang='ko', en='work', words=['일을']),
    dict(ref=(34, 3, 2), lang='ko', en='revive', words=['부흥케']),
    dict(ref=(34, 3, 2), lang='ko', en='in#1', words=['이#1']),
    dict(ref=(34, 3, 2), lang='ko', en='midst#1', words=['내에#1']),
    dict(ref=(34, 3, 2), lang='ko', en='in#2', words=['이#2']),
    dict(ref=(34, 3, 2), lang='ko', en='midst#2', words=['내에#2']),
    dict(ref=(34, 3, 2), lang='ko', en='the#2', words=['수년#1']),
    dict(ref=(34, 3, 2), lang='ko', en='years#1', words=['수년#1']),
    dict(ref=(34, 3, 2), lang='ko', en='the#4', words=['수년#2']),
    dict(ref=(34, 3, 2), lang='ko', en='years#2', words=['수년#2']),
    dict(ref=(34, 3, 2), lang='ko', en='remember', words=['잊지', '마옵소서']),
    dict(ref=(34, 3, 4), lang='ko', en='brightness', words=['광명이']),
    dict(ref=(34, 3, 4), lang='ko', en='the#1', words=['햇빛']),
    dict(ref=(34, 3, 4), lang='ko', en='light', words=['햇빛']),
    dict(ref=(34, 3, 4), lang='ko', en='horns', words=['광선이']),
    dict(ref=(34, 3, 4), lang='ko', en='had', words=[]),
    dict(ref=(34, 3, 4), lang='ko', en='coming', words=['나오니']),
    dict(ref=(34, 3, 4), lang='ko', en='out', words=['나오니']),
    dict(ref=(34, 3, 4), lang='ko', en='of#1', words=[]),
    dict(ref=(34, 3, 4), lang='ko', en='his#1', words=['그#1']),
    dict(ref=(34, 3, 4), lang='ko', en='his#2', words=['그#2']),
    dict(ref=(34, 3, 4), lang='ko', en='his#3', words=['그#3']),
    dict(ref=(34, 3, 5), lang='ko', en='burning', words=['불덩이가']),
    dict(ref=(34, 3, 5), lang='ko', en='coals', words=['불덩이가']),
    dict(ref=(34, 3, 5), lang='ko', en='went#2', words=['나오도다']),
    dict(ref=(34, 3, 5), lang='ko', en='forth', words=['나오도다']),
    dict(ref=(34, 3, 5), lang='ko', en='his', words=['그#2']),
    dict(ref=(34, 3, 5), lang='ko', en='feet', words=['발밑에서']),
    dict(ref=(34, 3, 6), lang='ko', en='He', words=['그가#1']),
    dict(ref=(34, 3, 6), lang='ko', en='stood', words=['서신즉']),
    dict(ref=(34, 3, 6), lang='ko', en='he', words=['그가#2']),
    dict(ref=(34, 3, 6), lang='ko', en='beheld', words=['보신즉']),
    dict(ref=(34, 3, 6), lang='ko', en='bow', words=['엎드러지나니']),
    dict(ref=(34, 3, 6), lang='ko', en='perpetual', words=['무궁한']),
    dict(ref=(34, 3, 6), lang='ko', en='hills', words=['작은', '산이#2']),
    dict(ref=(34, 3, 6), lang='ko', en='his', words=['그']),
    dict(ref=(34, 3, 6), lang='ko', en='measured', words=['진동하며']),
    dict(ref=(34, 3, 6), lang='ko', en='drove', words=['전률하며']),
    dict(ref=(34, 3, 6), lang='ko', en='asunder', words=['전률하며']),
    dict(ref=(34, 3, 6), lang='ko', en='were', words=['무너지며']),
    dict(ref=(34, 3, 6), lang='ko', en='scattered', words=['무너지며']),
    dict(ref=(34, 3, 6), lang='ko', en='did', words=['엎드러지나니']),
    dict(ref=(34, 3, 6), lang='ko', en='ways', words=['행하심이']),
    dict(ref=(34, 3, 6), lang='ko', en='are', words=['그러하시도다']),
    dict(ref=(34, 3, 6), lang='ko', en='everlasting#2', words=['예로부터']),
    dict(ref=(34, 3, 8), lang='ko', en='thou', words=['주께서']),
    dict(ref=(34, 3, 8), lang='ko', en='displeased', words=['분히', '여기심이니이까']),
    dict(ref=(34, 3, 8), lang='ko', en='rivers#1', words=['하수를']),
    dict(ref=(34, 3, 8), lang='ko', en='rivers#2', words=['강을']),
    dict(ref=(34, 3, 8), lang='ko', en='thine#1', words=['노여워하심이니이까']),
    dict(ref=(34, 3, 8), lang='ko', en='anger', words=['노여워하심이니이까']),
    dict(ref=(34, 3, 8), lang='ko', en='thy#1', words=['성내심이니이까']),
    dict(ref=(34, 3, 8), lang='ko', en='wrath', words=['성내심이니이까']),
    dict(ref=(34, 3, 8), lang='ko', en='against#3', words=['대하여']),
    dict(ref=(34, 3, 8), lang='ko', en='thine#2', words=['말을']),
    dict(ref=(34, 3, 8), lang='ko', en='horses', words=['말을']),
    dict(ref=(34, 3, 8), lang='ko', en='upon', words=['말을']),
    dict(ref=(34, 3, 8), lang='ko', en='thy#2', words=['병거를']),
    dict(ref=(34, 3, 8), lang='ko', en='chariots', words=['병거를']),
    # 3:19 '이 노래는'은 영어 본문에 대응하는 낱말이 없다 — 떼어 둔다.
    dict(ref=(34, 3, 19), lang='ko', en='stringed', words=['수금에']),
    dict(ref=(34, 3, 19), lang='ko', en='instruments', words=['수금에']),
    dict(ref=(34, 3, 19), lang='ko', en='my#3', words=['내']),
    dict(ref=(34, 3, 19), lang='ko', en='on', words=['수금에']),
    dict(ref=(34, 3, 19), lang='ko', en='will#1', words=[]),
    dict(ref=(34, 3, 19), lang='ko', en='will#2', words=[]),
    dict(ref=(34, 3, 16), lang='ko', en='When', words=['들었으므로']),
    dict(ref=(34, 3, 16), lang='ko', en='I#1', words=['내가#1']),
    dict(ref=(34, 3, 16), lang='ko', en='heard', words=['들었으므로']),
    dict(ref=(34, 3, 16), lang='ko', en='my#1', words=['내#1']),
    dict(ref=(34, 3, 16), lang='ko', en='belly', words=['창자가']),
    dict(ref=(34, 3, 16), lang='ko', en='trembled#1', words=['흔들렸고']),
    dict(ref=(34, 3, 16), lang='ko', en='my#2', words=['내#2']),
    dict(ref=(34, 3, 16), lang='ko', en='lips', words=['입술이']),
    dict(ref=(34, 3, 16), lang='ko', en='quivered', words=['떨렸도다']),
    dict(ref=(34, 3, 16), lang='ko', en='entered', words=['들어왔으며']),
    dict(ref=(34, 3, 16), lang='ko', en='into', words=['들어왔으며']),
    dict(ref=(34, 3, 16), lang='ko', en='my#3', words=['내#3']),
    dict(ref=(34, 3, 16), lang='ko', en='bones', words=['뼈에']),
    dict(ref=(34, 3, 16), lang='ko', en='I#2', words=['내#4', '몸은']),
    dict(ref=(34, 3, 16), lang='ko', en='in#1', words=['내#4', '몸은']),
    dict(ref=(34, 3, 16), lang='ko', en='myself', words=['내#4', '몸은']),
    dict(ref=(34, 3, 16), lang='ko', en='trembled#2', words=['떨리는도다']),
    dict(ref=(34, 3, 16), lang='ko', en='cometh', words=['올라오는']),
    dict(ref=(34, 3, 16), lang='ko', en='I#3', words=['내가#2']),
    dict(ref=(34, 3, 16), lang='ko', en='rest', words=['기다리므로']),
    dict(ref=(34, 3, 16), lang='ko', en='at', words=['인하여']),
    dict(ref=(34, 3, 16), lang='ko', en='invade', words=['치러']),
    dict(ref=(34, 1, 5), lang='ko', en='Behold', words=['보고#1']),
    dict(ref=(34, 1, 5), lang='ko', en='ye#1', words=['너희는']),
    dict(ref=(34, 1, 5), lang='ko', en='and#1', words=['또#1']),
    dict(ref=(34, 1, 5), lang='ko', en='regard', words=['보고#2']),
    dict(ref=(34, 1, 5), lang='ko', en='and#2', words=['또#2']),
    dict(ref=(34, 1, 5), lang='ko', en='marvellously', words=['놀랄지어다']),
    dict(ref=(34, 1, 5), lang='ko', en='for', words=[]),
    dict(ref=(34, 1, 5), lang='ko', en='I', words=['내가']),
    dict(ref=(34, 1, 5), lang='ko', en='work#1', words=['행할']),
    dict(ref=(34, 1, 5), lang='ko', en='a', words=['한']),
    dict(ref=(34, 1, 5), lang='ko', en='work#2', words=['일을']),
    dict(ref=(34, 1, 5), lang='ko', en='in', words=['너희', '생전에']),
    dict(ref=(34, 1, 5), lang='ko', en='your', words=['너희', '생전에']),
    dict(ref=(34, 1, 5), lang='ko', en='days', words=['너희', '생전에']),
    dict(ref=(34, 1, 5), lang='ko', en='which', words=[]),
    dict(ref=(34, 1, 5), lang='ko', en='ye#2', words=['너희가']),
    dict(ref=(34, 1, 5), lang='ko', en='told', words=['고할지라도']),
    dict(ref=(34, 1, 5), lang='ko', en='you', words=['너희에게']),
    dict(ref=(34, 1, 5), lang='ko', en='it', words=['혹이']),
    dict(ref=(34, 1, 6), lang='ko', en='up', words=['일으켰나니']),
    dict(ref=(34, 1, 6), lang='ko', en='Chaldeans', words=['갈대아', '사람을']),
    dict(ref=(34, 1, 6), lang='ko', en='that#1', words=[]),
    dict(ref=(34, 1, 6), lang='ko', en='bitter', words=['사납고']),
    dict(ref=(34, 1, 6), lang='ko', en='hasty', words=['성급한']),
    dict(ref=(34, 1, 6), lang='ko', en='march', words=['다니며']),
    dict(ref=(34, 1, 6), lang='ko', en='through', words=['곳으로']),
    dict(ref=(34, 1, 6), lang='ko', en='of', words=[]),
    dict(ref=(34, 1, 6), lang='ko', en='dwellingplaces', words=['거할', '곳들을']),
    dict(ref=(34, 1, 6), lang='ko', en='that#2', words=[]),
    dict(ref=(34, 1, 6), lang='ko', en='are', words=['아닌']),
    dict(ref=(34, 1, 6), lang='ko', en='not', words=['아닌']),
    dict(ref=(34, 1, 6), lang='ko', en='theirs', words=['자기의', '소유']),

    dict(ref=(34, 1, 12), lang='ko', en='Art', words=['계시지']),
    dict(ref=(34, 1, 12), lang='ko', en='thou#1', words=['주께서는']),
    dict(ref=(34, 1, 12), lang='ko', en='not#1', words=['아니하시니이까']),
    dict(ref=(34, 1, 12), lang='ko', en='everlasting', words=['만세', '전부터', '계시지', '아니하시니이까']),
    dict(ref=(34, 1, 12), lang='ko', en='O#1', words=['여호와']),
    dict(ref=(34, 1, 12), lang='ko', en='Lord#1', words=['여호와']),
    dict(ref=(34, 1, 12), lang='ko', en='my', words=['나의#1']),
    dict(ref=(34, 1, 12), lang='ko', en='God#1', words=['하나님']),
    dict(ref=(34, 1, 12), lang='ko', en='mine', words=['나의#2']),
    dict(ref=(34, 1, 12), lang='ko', en='Holy', words=['거룩한']),
    dict(ref=(34, 1, 12), lang='ko', en='One', words=['자시여']),
    dict(ref=(34, 1, 12), lang='ko', en='shall', words=[]),
    dict(ref=(34, 1, 12), lang='ko', en='not#2', words=['아니하리이다']),
    dict(ref=(34, 1, 12), lang='ko', en='die', words=['사망에', '이르지']),
    dict(ref=(34, 1, 12), lang='ko', en='O#2', words=['여호와여']),
    dict(ref=(34, 1, 12), lang='ko', en='Lord#2', words=['여호와여']),
    dict(ref=(34, 1, 12), lang='ko', en='thou#2', words=['주께서#1']),
    dict(ref=(34, 1, 12), lang='ko', en='hast#1', words=['두셨나이다']),
    dict(ref=(34, 1, 12), lang='ko', en='ordained', words=['두셨나이다']),
    dict(ref=(34, 1, 12), lang='ko', en='them#1', words=['그를#1']),
    dict(ref=(34, 1, 12), lang='ko', en='for#1', words=['위하여#1']),
    dict(ref=(34, 1, 12), lang='ko', en='judgment', words=['심판하기']),
    dict(ref=(34, 1, 12), lang='ko', en='and', words=[]),
    dict(ref=(34, 1, 12), lang='ko', en='O#3', words=['반석이시여']),
    dict(ref=(34, 1, 12), lang='ko', en='mighty', words=['반석이시여']),
    dict(ref=(34, 1, 12), lang='ko', en='God#2', words=['반석이시여']),
    dict(ref=(34, 1, 12), lang='ko', en='thou#3', words=['주께서#2']),
    dict(ref=(34, 1, 12), lang='ko', en='hast#2', words=['세우셨나이다']),
    dict(ref=(34, 1, 12), lang='ko', en='established', words=['세우셨나이다']),
    dict(ref=(34, 1, 12), lang='ko', en='them#2', words=['그를#2']),
    dict(ref=(34, 1, 12), lang='ko', en='for#2', words=['위하여#2']),
    dict(ref=(34, 1, 12), lang='ko', en='correction', words=['경계하기']),

    dict(ref=(34, 3, 17), lang='ko', en='Although', words=['비록']),
    dict(ref=(34, 3, 17), lang='ko', en='tree', words=['무화과나무가']),
    dict(ref=(34, 3, 17), lang='ko', en='not', words=['못하며']),
    dict(ref=(34, 3, 17), lang='ko', en='neither', words=['없으며#1']),
    dict(ref=(34, 3, 17), lang='ko', en='labour', words=['소출이']),
    dict(ref=(34, 3, 17), lang='ko', en='the#4', words=['감람나무에']),
    dict(ref=(34, 3, 17), lang='ko', en='olive', words=['감람나무에']),
    dict(ref=(34, 3, 17), lang='ko', en='fail', words=['없으며#2']),
    dict(ref=(34, 3, 17), lang='ko', en='no#1', words=['없으며#3']),
    dict(ref=(34, 3, 17), lang='ko', en='flock', words=['양이']),
    dict(ref=(34, 3, 17), lang='ko', en='cut', words=['없으며#4']),
    dict(ref=(34, 3, 17), lang='ko', en='off', words=['없으며#4']),
    dict(ref=(34, 3, 17), lang='ko', en='fold', words=['우리에']),
    dict(ref=(34, 3, 17), lang='ko', en='no#2', words=['없을지라도']),
    dict(ref=(34, 1, 9), lang='ko', en='shall#1', words=[]),
    dict(ref=(34, 1, 9), lang='ko', en='shall#2', words=[]),
    dict(ref=(34, 1, 9), lang='ko', en='shall#3', words=[]),
    dict(ref=(34, 1, 10), lang='ko', en='shall#1', words=[]),
    dict(ref=(34, 1, 10), lang='ko', en='shall#2', words=[]),
    dict(ref=(34, 1, 10), lang='ko', en='shall#3', words=[]),
    dict(ref=(34, 1, 10), lang='ko', en='shall#4', words=[]),
    # ---- 편집기 두 번째 바퀴 (어제 손본 절을 다시 손봄) ----
    # 같은 절·같은 영어 낱말은 나중 항목이 이기므로, 목록 맨 뒤에 둔다.
    # ---- 출애굽기 24:3 ----
    dict(ref=(1, 24, 3), lang='ko', en='with', words=['소리로']),
    dict(ref=(1, 24, 3), lang='ko', en='words#2', words=['말씀을']),
    dict(ref=(1, 24, 3), lang='ko', en='said#2', words=['명하신']),

    # ---- 민수기 36:5 ----
    dict(ref=(3, 36, 5), lang='ko', en='according', words=['말씀으로']),
    dict(ref=(3, 36, 5), lang='ko', en='to', words=['말씀으로']),
    dict(ref=(3, 36, 5), lang='ko', en='hath', words=['말이']),

    # ---- 신명기 5:28 ----
    dict(ref=(4, 5, 28), lang='ko', en='heard#1', words=['들으신지라']),
    dict(ref=(4, 5, 28), lang='ko', en='unto#1', words=['내게#1']),
    dict(ref=(4, 5, 28), lang='ko', en='words#2', words=['말하는#2']),

    # ---- 신명기 32:46 ----
    dict(ref=(4, 32, 46), lang='ko', en='among', words=['너희에게']),

    # ---- 사무엘하 19:11 ----
    dict(ref=(9, 19, 11), lang='ko', en='saying#2', words=['이르기를']),
    dict(ref=(9, 19, 11), lang='ko', en='ye', words=['너희는#2']),
    dict(ref=(9, 19, 11), lang='ko', en='seeing', words=['들렸거늘']),
    dict(ref=(9, 19, 11), lang='ko', en='the#5', words=['말이']),
    dict(ref=(9, 19, 11), lang='ko', en='speech', words=['말이']),
    dict(ref=(9, 19, 11), lang='ko', en='is', words=[]),
    dict(ref=(9, 19, 11), lang='ko', en='come', words=[]),

    # ---- 열왕기상 2:23 ----
    dict(ref=(10, 2, 23), lang='ko', en='by', words=['가리켜']),
    dict(ref=(10, 2, 23), lang='ko', en='the', words=['여호와를']),
    dict(ref=(10, 2, 23), lang='ko', en='to', words=['내게']),
    dict(ref=(10, 2, 23), lang='ko', en='against', words=['잃지']),
    dict(ref=(10, 2, 23), lang='ko', en='own', words=['그']),

    # ---- 열왕기상 13:21 ----
    dict(ref=(10, 13, 21), lang='ko', en='of#2', words=['여호와의#2']),
    dict(ref=(10, 13, 21), lang='ko', en='thee', words=['네게']),

    # ---- 열왕기상 13:26 ----
    dict(ref=(10, 13, 26), lang='ko', en='brought', words=['데리고']),
    dict(ref=(10, 13, 26), lang='ko', en='him#1', words=['그', '사람을']),
    dict(ref=(10, 13, 26), lang='ko', en='who', words=[]),
    dict(ref=(10, 13, 26), lang='ko', en='word#1', words=['말씀을']),
    dict(ref=(10, 13, 26), lang='ko', en='of#2', words=['여호와의']),
    dict(ref=(10, 13, 26), lang='ko', en='hath#1', words=[]),

    # ---- 열왕기상 21:19 ----
    dict(ref=(10, 21, 19), lang='ko', en='speak#2', words=['이르기를#2']),
    dict(ref=(10, 21, 19), lang='ko', en='unto#2', words=['저에게#2']),
    dict(ref=(10, 21, 19), lang='ko', en='of', words=['나봇의']),
    dict(ref=(10, 21, 19), lang='ko', en='thy', words=['네#1']),
    dict(ref=(10, 21, 19), lang='ko', en='blood#2', words=['피']),
    dict(ref=(10, 21, 19), lang='ko', en='thine', words=[]),

    # ---- 열왕기하 3:7 ----
    dict(ref=(11, 3, 7), lang='ko', en='wilt', words=[]),

    # 왕상 2:23 — 비게 된 자리 채움. have·spoken 이 '말을·생명을·가리켜'에 흩어져
    # 있어서 '이런 … 하였은즉'과 '벌 위에 벌을 내리심이 마땅하니이다'가 비어 있었다.
    dict(ref=(10, 2, 23), lang='ko', en='do', words=['내리심이', '마땅하니이다']),
    dict(ref=(10, 2, 23), lang='ko', en='so', words=['벌']),
    dict(ref=(10, 2, 23), lang='ko', en='and', words=['위에']),
    dict(ref=(10, 2, 23), lang='ko', en='more', words=['벌을']),
    dict(ref=(10, 2, 23), lang='ko', en='also', words=['위에']),
    dict(ref=(10, 2, 23), lang='ko', en='have', words=['하였은즉']),
    dict(ref=(10, 2, 23), lang='ko', en='not', words=['아니하면']),
    dict(ref=(10, 2, 23), lang='ko', en='spoken', words=['하였은즉']),
    dict(ref=(10, 2, 23), lang='ko', en='this', words=['이런']),
    dict(ref=(10, 2, 23), lang='ko', en='word', words=['말을']),

    # ---- 요한계시록 21:3 ----
    dict(ref=(65, 21, 3), lang='ko', en='I', words=['내가']),
    dict(ref=(65, 21, 3), lang='ko', en='out', words=['나서']),
    dict(ref=(65, 21, 3), lang='ko', en='of#1', words=['보좌에서']),
    dict(ref=(65, 21, 3), lang='ko', en='heaven', words=['보좌에서']),
    dict(ref=(65, 21, 3), lang='ko', en='God#1', words=['하나님의#1']),
    dict(ref=(65, 21, 3), lang='ko', en='is', words=['있으매']),
    dict(ref=(65, 21, 3), lang='ko', en='with#1', words=['함께#1']),
    dict(ref=(65, 21, 3), lang='ko', en='he', words=['하나님이']),
    dict(ref=(65, 21, 3), lang='ko', en='will', words=['거하시리니']),
    dict(ref=(65, 21, 3), lang='ko', en='with#2', words=['함께#2']),
    dict(ref=(65, 21, 3), lang='ko', en='them#1', words=['저희와#1']),
    dict(ref=(65, 21, 3), lang='ko', en='they', words=['저희와#1', '저희는']),
    dict(ref=(65, 21, 3), lang='ko', en='shall#1', words=['되고']),
    dict(ref=(65, 21, 3), lang='ko', en='his', words=['하나님의#2']),
    dict(ref=(65, 21, 3), lang='ko', en='God#2', words=['하나님은']),
    dict(ref=(65, 21, 3), lang='ko', en='shall#2', words=['계셔서']),
    dict(ref=(65, 21, 3), lang='ko', en='with#3', words=['함께#3']),
    dict(ref=(65, 21, 3), lang='ko', en='them#2', words=['저희와#2']),

    # ---- 요한계시록 15:3 ----
    dict(ref=(65, 15, 3), lang='ko', en='sing', words=['불러']),
    dict(ref=(65, 15, 3), lang='ko', en='of#1', words=['모세의']),
    dict(ref=(65, 15, 3), lang='ko', en='of#2', words=['하나님의']),
    dict(ref=(65, 15, 3), lang='ko', en='the#3', words=['노래를']),
    dict(ref=(65, 15, 3), lang='ko', en='song#2', words=['노래를']),
    dict(ref=(65, 15, 3), lang='ko', en='are#1', words=[]),
    dict(ref=(65, 15, 3), lang='ko', en='works', words=['하시는', '일이']),
    dict(ref=(65, 15, 3), lang='ko', en='God#2', words=['하나님']),
    dict(ref=(65, 15, 3), lang='ko', en='Almighty', words=['전능하신', '이시여']),
    dict(ref=(65, 15, 3), lang='ko', en='thy#2', words=['주의']),

    # ---- 요한계시록 17:17 ----
    dict(ref=(65, 17, 17), lang='ko', en='will', words=['뜻대로']),
    dict(ref=(65, 17, 17), lang='ko', en='to#2', words=['할']),
    dict(ref=(65, 17, 17), lang='ko', en='agree', words=['할']),
    dict(ref=(65, 17, 17), lang='ko', en='give', words=['주게']),
    dict(ref=(65, 17, 17), lang='ko', en='their#2', words=['저희']),
    dict(ref=(65, 17, 17), lang='ko', en='unto', words=['짐승에게']),
    dict(ref=(65, 17, 17), lang='ko', en='until', words=['응하기까지']),
    dict(ref=(65, 17, 17), lang='ko', en='of', words=['하나님']),
    dict(ref=(65, 17, 17), lang='ko', en='God#2', words=['하나님']),
    dict(ref=(65, 17, 17), lang='ko', en='be', words=['응하기까지']),
    dict(ref=(65, 17, 17), lang='ko', en='fulfilled', words=['응하기까지']),

    # 계 15:3 · 17:17 — 비게 된 자리 채움
    dict(ref=(65, 15, 3), lang='ko', en='of#4', words=['만국의']),
    dict(ref=(65, 15, 3), lang='ko', en='saints', words=['만국의']),
    dict(ref=(65, 15, 3), lang='ko', en='Lord', words=['주', '곧']),

    dict(ref=(65, 17, 17), lang='ko', en='and#1', words=['하시고']),
    dict(ref=(65, 17, 17), lang='ko', en='and#2', words=['하시되']),
    dict(ref=(65, 17, 17), lang='ko', en='the#1', words=['그', '짐승에게']),
    dict(ref=(65, 17, 17), lang='ko', en='shall', words=['하심이니라']),
    dict(ref=(65, 17, 17), lang='ko', en='fulfil', words=['한', '뜻을', '이루게']),

    # ---- 요한계시록 12:10 ----
    dict(ref=(65, 12, 10), lang='ko', en='I', words=['내가']),
    dict(ref=(65, 12, 10), lang='ko', en='in', words=['하늘에']),
    dict(ref=(65, 12, 10), lang='ko', en='come', words=['이루었으니']),
    dict(ref=(65, 12, 10), lang='ko', en='strength', words=['능력과']),
    dict(ref=(65, 12, 10), lang='ko', en='the#2', words=['권세가']),
    dict(ref=(65, 12, 10), lang='ko', en='power', words=['권세가']),
    dict(ref=(65, 12, 10), lang='ko', en='of#2', words=['그리스도의']),
    dict(ref=(65, 12, 10), lang='ko', en='our#2', words=['우리#2']),
    dict(ref=(65, 12, 10), lang='ko', en='cast', words=['쫓겨났고']),
    dict(ref=(65, 12, 10), lang='ko', en='down', words=['쫓겨났고']),
    dict(ref=(65, 12, 10), lang='ko', en='which', words=['자가']),
    dict(ref=(65, 12, 10), lang='ko', en='accused', words=['참소하던#2']),
    dict(ref=(65, 12, 10), lang='ko', en='them', words=['우리#2', '형제들을']),
    dict(ref=(65, 12, 10), lang='ko', en='our#3', words=['우리#3']),
    dict(ref=(65, 12, 10), lang='ko', en='God#2', words=['하나님']),
    dict(ref=(65, 12, 10), lang='ko', en='day', words=['밤낮']),
    dict(ref=(65, 12, 10), lang='ko', en='and#4', words=['밤낮']),

    # 계 12:10 — 비게 된 자리 채움
    dict(ref=(65, 12, 10), lang='ko', en='saying', words=['있어', '가로되']),
    dict(ref=(65, 12, 10), lang='ko', en='and#3', words=['또#2']),
    dict(ref=(65, 12, 10), lang='ko', en='accuser', words=['참소하던#1', '자']),

    # ---- 요한계시록 3:12 ----
    dict(ref=(65, 3, 12), lang='ko', en='my#1', words=['내#1']),
    dict(ref=(65, 3, 12), lang='ko', en='God#1', words=['하나님']),
    dict(ref=(65, 3, 12), lang='ko', en='no', words=['아니하리라']),
    dict(ref=(65, 3, 12), lang='ko', en='out#1', words=['나가지']),
    dict(ref=(65, 3, 12), lang='ko', en='I#2', words=['내가']),
    dict(ref=(65, 3, 12), lang='ko', en='him#1', words=['그이']),
    dict(ref=(65, 3, 12), lang='ko', en='of#2', words=['하나님의#1']),
    dict(ref=(65, 3, 12), lang='ko', en='my#2', words=['하나님의#1']),
    dict(ref=(65, 3, 12), lang='ko', en='God#2', words=['하나님의#1']),
    dict(ref=(65, 3, 12), lang='ko', en='of#4', words=['하나님의#2']),
    dict(ref=(65, 3, 12), lang='ko', en='my#3', words=['하나님의#2']),
    dict(ref=(65, 3, 12), lang='ko', en='God#3', words=['하나님의#2']),
    dict(ref=(65, 3, 12), lang='ko', en='out#2', words=[]),
    dict(ref=(65, 3, 12), lang='ko', en='from', words=['하나님께로부터']),
    dict(ref=(65, 3, 12), lang='ko', en='my#4', words=['하나님께로부터']),
    dict(ref=(65, 3, 12), lang='ko', en='God#4', words=['하나님께로부터']),
    dict(ref=(65, 3, 12), lang='ko', en='will#3', words=['기록하리라']),
    dict(ref=(65, 3, 12), lang='ko', en='write#2', words=['기록하리라']),
    dict(ref=(65, 3, 12), lang='ko', en='upon#2', words=['위에']),
    dict(ref=(65, 3, 12), lang='ko', en='him#2', words=['그이']),
    dict(ref=(65, 3, 12), lang='ko', en='my#5', words=['나의']),
    dict(ref=(65, 3, 12), lang='ko', en='name#3', words=['이름을']),

    # 계 3:12 — 비게 된 자리 채움
    dict(ref=(65, 3, 12), lang='ko', en='he', words=['그가']),
    dict(ref=(65, 3, 12), lang='ko', en='my#4', words=['내#2', '하나님께로부터']),
    dict(ref=(65, 3, 12), lang='ko', en='the#3', words=['이름과#2']),
    dict(ref=(65, 3, 12), lang='ko', en='name#2', words=['이름과#2']),

    # ---- 요한삼서 1:11 ----
    dict(ref=(63, 1, 11), lang='ko', en='Beloved', words=['사랑하는', '자여']),
    dict(ref=(63, 1, 11), lang='ko', en='not#1', words=['말고']),
    dict(ref=(63, 1, 11), lang='ko', en='that#1', words=['것을#1']),
    dict(ref=(63, 1, 11), lang='ko', en='which#1', words=['것을#1']),
    dict(ref=(63, 1, 11), lang='ko', en='but#1', words=['본받으라']),
    dict(ref=(63, 1, 11), lang='ko', en='that#2', words=['것을#2']),
    dict(ref=(63, 1, 11), lang='ko', en='which#2', words=['것을#2']),
    dict(ref=(63, 1, 11), lang='ko', en='He', words=['자는#1']),
    dict(ref=(63, 1, 11), lang='ko', en='that#3', words=['자는#1']),
    dict(ref=(63, 1, 11), lang='ko', en='doeth#1', words=['행하는#1']),
    dict(ref=(63, 1, 11), lang='ko', en='is#3', words=['자는#1']),
    dict(ref=(63, 1, 11), lang='ko', en='of', words=['하나님께', '속하고']),
    dict(ref=(63, 1, 11), lang='ko', en='God#1', words=['하나님께', '속하고']),
    dict(ref=(63, 1, 11), lang='ko', en='he', words=['자는#2']),
    dict(ref=(63, 1, 11), lang='ko', en='that#4', words=['자는#2']),
    dict(ref=(63, 1, 11), lang='ko', en='doeth#2', words=['행하는#2']),
    dict(ref=(63, 1, 11), lang='ko', en='evil#2', words=['악을']),
    dict(ref=(63, 1, 11), lang='ko', en='hath', words=[]),
    dict(ref=(63, 1, 11), lang='ko', en='not#2', words=['못하였느니라']),
    dict(ref=(63, 1, 11), lang='ko', en='seen', words=['뵈옵지']),
    dict(ref=(63, 1, 11), lang='ko', en='God#2', words=['하나님을']),

    # 계속 — evil(1)이 '악한·악을' 양쪽에 걸려 있던 것을 '악한'만 남긴다
    dict(ref=(63, 1, 11), lang='ko', en='evil#1', words=['악한']),
    dict(ref=(63, 1, 11), lang='ko', en='doeth#1', words=['선을', '행하는#1']),

    # ---- 요한일서 5:10 ----
    dict(ref=(61, 5, 10), lang='ko', en='He', words=['자는#1']),
    dict(ref=(61, 5, 10), lang='ko', en='that#1', words=['자는#1']),
    dict(ref=(61, 5, 10), lang='ko', en='of#1', words=['하나님의']),
    dict(ref=(61, 5, 10), lang='ko', en='the#2', words=['증거가']),
    dict(ref=(61, 5, 10), lang='ko', en='witness', words=['증거가']),
    dict(ref=(61, 5, 10), lang='ko', en='he#1', words=['자는#2']),
    dict(ref=(61, 5, 10), lang='ko', en='that#2', words=['자는#2']),
    dict(ref=(61, 5, 10), lang='ko', en='believeth#2', words=['믿지#1']),
    dict(ref=(61, 5, 10), lang='ko', en='not#1', words=['아니하는']),
    dict(ref=(61, 5, 10), lang='ko', en='God#2', words=['하나님을#1']),
    dict(ref=(61, 5, 10), lang='ko', en='hath#2', words=['만드나니']),
    dict(ref=(61, 5, 10), lang='ko', en='made', words=['만드나니']),
    dict(ref=(61, 5, 10), lang='ko', en='him', words=['하나님을#2']),
    dict(ref=(61, 5, 10), lang='ko', en='a', words=['거짓말하는', '자로']),
    dict(ref=(61, 5, 10), lang='ko', en='liar', words=['거짓말하는', '자로']),
    dict(ref=(61, 5, 10), lang='ko', en='believeth#3', words=['믿지#2']),
    dict(ref=(61, 5, 10), lang='ko', en='not#2', words=['아니하였음이라']),
    dict(ref=(61, 5, 10), lang='ko', en='the#3', words=['증거를']),
    dict(ref=(61, 5, 10), lang='ko', en='record', words=['증거를']),
    dict(ref=(61, 5, 10), lang='ko', en='God#3', words=['하나님께서']),
    dict(ref=(61, 5, 10), lang='ko', en='gave', words=['증거하신']),
    dict(ref=(61, 5, 10), lang='ko', en='of#2', words=['관하여']),
    dict(ref=(61, 5, 10), lang='ko', en='Son#2', words=['아들에']),

    # 요일 5:10 — '이는'은 because 에 걸고, the Son(1)이 '아들을·아들에' 양쪽에
    # 걸려 있던 것을 '아들을'만 남긴다
    dict(ref=(61, 5, 10), lang='ko', en='because', words=['이는']),
    dict(ref=(61, 5, 10), lang='ko', en='the#1', words=['아들을']),
    dict(ref=(61, 5, 10), lang='ko', en='Son#1', words=['아들을']),

    # ---- 요한일서 5:2 ----
    dict(ref=(61, 5, 2), lang='ko', en='By', words=['이로써']),
    dict(ref=(61, 5, 2), lang='ko', en='we#1', words=['우리가#2']),
    dict(ref=(61, 5, 2), lang='ko', en='know', words=['아느니라']),
    dict(ref=(61, 5, 2), lang='ko', en='we#2', words=['우리가#1']),
    dict(ref=(61, 5, 2), lang='ko', en='love#1', words=['사랑하는']),
    dict(ref=(61, 5, 2), lang='ko', en='of', words=['하나님의']),
    dict(ref=(61, 5, 2), lang='ko', en='God#1', words=['하나님의']),
    dict(ref=(61, 5, 2), lang='ko', en='we#3', words=['우리가#1']),
    dict(ref=(61, 5, 2), lang='ko', en='love#2', words=['사랑하고']),
    dict(ref=(61, 5, 2), lang='ko', en='God#2', words=['하나님을']),

    # ---- 요한일서 4:16 ----
    dict(ref=(61, 4, 16), lang='ko', en='we', words=['우리가']),
    dict(ref=(61, 4, 16), lang='ko', en='the', words=['사랑을']),
    dict(ref=(61, 4, 16), lang='ko', en='love#1', words=['사랑을']),
    dict(ref=(61, 4, 16), lang='ko', en='God#1', words=['하나님이']),
    dict(ref=(61, 4, 16), lang='ko', en='to', words=['우리를']),
    dict(ref=(61, 4, 16), lang='ko', en='us', words=['우리를']),
    dict(ref=(61, 4, 16), lang='ko', en='God#2', words=['하나님은']),
    dict(ref=(61, 4, 16), lang='ko', en='is', words=['사랑이시라']),
    dict(ref=(61, 4, 16), lang='ko', en='love#2', words=['사랑이시라']),
    dict(ref=(61, 4, 16), lang='ko', en='he', words=['자는']),
    dict(ref=(61, 4, 16), lang='ko', en='dwelleth#1', words=['거하는']),
    dict(ref=(61, 4, 16), lang='ko', en='love#3', words=['사랑']),
    dict(ref=(61, 4, 16), lang='ko', en='dwelleth#2', words=['거하고', '거하시느니라']),
    dict(ref=(61, 4, 16), lang='ko', en='in#2', words=['안에#2']),
    dict(ref=(61, 4, 16), lang='ko', en='God#3', words=['하나님']),
    dict(ref=(61, 4, 16), lang='ko', en='God#4', words=['하나님도']),
    dict(ref=(61, 4, 16), lang='ko', en='in#3', words=['안에#3']),
    dict(ref=(61, 4, 16), lang='ko', en='him', words=['그']),
    # the love 를 '사랑을'로 모으면서 비게 된 '사랑하시는'은 hath 에 건다
    # (the love that God hath to us = 하나님이 우리를 사랑하시는 사랑을)
    dict(ref=(61, 4, 16), lang='ko', en='hath', words=['사랑하시는']),

    # ---- 요한일서 4:15 ----
    dict(ref=(61, 4, 15), lang='ko', en='of', words=['하나님의']),
    dict(ref=(61, 4, 15), lang='ko', en='God#2', words=['하나님의', '하나님이']),
    dict(ref=(61, 4, 15), lang='ko', en='dwelleth', words=['거하시고', '거하느니라']),
    dict(ref=(61, 4, 15), lang='ko', en='he', words=['저도']),
    dict(ref=(61, 4, 15), lang='ko', en='in#2', words=['안에#2']),
    dict(ref=(61, 4, 15), lang='ko', en='God#3', words=['하나님']),

    # 요일 4:15 — God(2)이 '하나님의·하나님이' 양쪽에 걸려 있던 것을 '하나님이'만
    # 남긴다. '하나님의'는 God(1)이 이미 받고 있다 (the Son of God / God dwelleth)
    dict(ref=(61, 4, 15), lang='ko', en='God#2', words=['하나님이']),

    # ---- 요한일서 4:12 ----
    dict(ref=(61, 4, 12), lang='ko', en='hath', words=['본']),
    dict(ref=(61, 4, 12), lang='ko', en='at', words=['어느', '때나']),
    dict(ref=(61, 4, 12), lang='ko', en='any', words=['어느']),
    dict(ref=(61, 4, 12), lang='ko', en='we', words=['우리가']),
    dict(ref=(61, 4, 12), lang='ko', en='God#2', words=['하나님이']),
    dict(ref=(61, 4, 12), lang='ko', en='love#2', words=['사랑이']),
    dict(ref=(61, 4, 12), lang='ko', en='in#2', words=['안에#2']),
    dict(ref=(61, 4, 12), lang='ko', en='us#2', words=['우리#2']),

    # ---- 요한일서 4:9 ----
    dict(ref=(61, 4, 9), lang='ko', en='In', words=['이렇게']),
    dict(ref=(61, 4, 9), lang='ko', en='this', words=['이렇게']),
    dict(ref=(61, 4, 9), lang='ko', en='of', words=['하나님의']),
    dict(ref=(61, 4, 9), lang='ko', en='toward', words=['우리에게']),
    dict(ref=(61, 4, 9), lang='ko', en='God#2', words=['하나님이']),
    dict(ref=(61, 4, 9), lang='ko', en='his', words=['자기의']),
    dict(ref=(61, 4, 9), lang='ko', en='Son', words=['독생자를']),
    dict(ref=(61, 4, 9), lang='ko', en='into', words=['세상에']),
    dict(ref=(61, 4, 9), lang='ko', en='we', words=['우리를']),
    # '바'는 manifested 에 함께 건다 (was manifested = 나타난 바 되었으니)
    dict(ref=(61, 4, 9), lang='ko', en='manifested', words=['나타난', '바']),

    # ---- 요한일서 4:7 ----
    dict(ref=(61, 4, 7), lang='ko', en='Beloved', words=['사랑하는#1', '자들아']),
    dict(ref=(61, 4, 7), lang='ko', en='let', words=['사랑하자']),
    dict(ref=(61, 4, 7), lang='ko', en='us', words=['우리가']),
    dict(ref=(61, 4, 7), lang='ko', en='love#1', words=['사랑하자']),
    dict(ref=(61, 4, 7), lang='ko', en='love#2', words=['사랑은']),
    dict(ref=(61, 4, 7), lang='ko', en='of#1', words=['속한']),
    dict(ref=(61, 4, 7), lang='ko', en='every', words=['자마다']),
    dict(ref=(61, 4, 7), lang='ko', en='one#2', words=['자마다']),
    dict(ref=(61, 4, 7), lang='ko', en='born', words=['나서']),
    dict(ref=(61, 4, 7), lang='ko', en='of#2', words=['하나님께로']),
    dict(ref=(61, 4, 7), lang='ko', en='God#2', words=['하나님께로']),
    dict(ref=(61, 4, 7), lang='ko', en='God#3', words=['하나님을']),

    # ---- 요한일서 4:6 ----
    dict(ref=(61, 4, 6), lang='ko', en='of#1', words=['속하였으니']),
    dict(ref=(61, 4, 6), lang='ko', en='God#1', words=['하나님께#1']),
    dict(ref=(61, 4, 6), lang='ko', en='he#1', words=['자는#1']),
    dict(ref=(61, 4, 6), lang='ko', en='God#2', words=['하나님을']),
    dict(ref=(61, 4, 6), lang='ko', en='he#2', words=['자는#2']),
    dict(ref=(61, 4, 6), lang='ko', en='that#2', words=['자는#2']),
    dict(ref=(61, 4, 6), lang='ko', en='not#1', words=['아니한']),
    dict(ref=(61, 4, 6), lang='ko', en='of#2', words=['속하지']),
    dict(ref=(61, 4, 6), lang='ko', en='God#3', words=['하나님께#2']),
    dict(ref=(61, 4, 6), lang='ko', en='heareth#2', words=['말을#2', '듣지']),
    dict(ref=(61, 4, 6), lang='ko', en='not#2', words=['아니하나니']),
    dict(ref=(61, 4, 6), lang='ko', en='us#2', words=['우리의#2']),
    dict(ref=(61, 4, 6), lang='ko', en='Hereby', words=['이로써']),
    dict(ref=(61, 4, 6), lang='ko', en='know', words=['아느니라']),
    dict(ref=(61, 4, 6), lang='ko', en='the#1', words=['영과']),
    dict(ref=(61, 4, 6), lang='ko', en='spirit#1', words=['영과']),
    dict(ref=(61, 4, 6), lang='ko', en='the#2', words=['영을']),
    dict(ref=(61, 4, 6), lang='ko', en='spirit#2', words=['영을']),

    # ---- 요한일서 4:2 ----
    dict(ref=(61, 4, 2), lang='ko', en='Hereby', words=['이것으로']),
    dict(ref=(61, 4, 2), lang='ko', en='God#1', words=['하나님의', '하나님께']),
    dict(ref=(61, 4, 2), lang='ko', en='Every', words=['영마다']),
    dict(ref=(61, 4, 2), lang='ko', en='spirit', words=['영마다']),
    dict(ref=(61, 4, 2), lang='ko', en='that#2', words=['것을']),
    dict(ref=(61, 4, 2), lang='ko', en='is#1', words=['오신']),
    dict(ref=(61, 4, 2), lang='ko', en='come', words=['오신']),
    dict(ref=(61, 4, 2), lang='ko', en='in', words=['육체로']),
    dict(ref=(61, 4, 2), lang='ko', en='of#2', words=['속한']),
    dict(ref=(61, 4, 2), lang='ko', en='God#2', words=['하나님께']),
    # 비게 된 자리 채움 + God(1)은 '하나님의'만 남긴다
    # (the Spirit of God = 하나님의 영은 / is of God = 하나님께 속한)
    dict(ref=(61, 4, 2), lang='ko', en='God#1', words=['하나님의']),
    dict(ref=(61, 4, 2), lang='ko', en='that#1', words=['곧']),
    dict(ref=(61, 4, 2), lang='ko', en='is#2', words=['것이요']),

    # ---- 요한일서 3:10 ----
    dict(ref=(61, 3, 10), lang='ko', en='God#1', words=['하나님의', '하나님께']),
    dict(ref=(61, 3, 10), lang='ko', en='the#2', words=['자녀들이']),
    dict(ref=(61, 3, 10), lang='ko', en='children#2', words=['자녀들이']),
    dict(ref=(61, 3, 10), lang='ko', en='whosoever', words=['무릇', '자나']),
    dict(ref=(61, 3, 10), lang='ko', en='not#2', words=['아니하니라']),
    dict(ref=(61, 3, 10), lang='ko', en='of#3', words=['속하지']),
    dict(ref=(61, 3, 10), lang='ko', en='God#2', words=['하나님께']),
    dict(ref=(61, 3, 10), lang='ko', en='neither', words=['아니하는#2']),
    dict(ref=(61, 3, 10), lang='ko', en='he', words=['자는']),
    dict(ref=(61, 3, 10), lang='ko', en='that', words=['자는']),
    dict(ref=(61, 3, 10), lang='ko', en='not#3', words=['아니하는#2']),
    # 비게 된 자리 채움 + God(1)은 '하나님의'만 남긴다
    dict(ref=(61, 3, 10), lang='ko', en='God#1', words=['하나님의']),
    dict(ref=(61, 3, 10), lang='ko', en='In', words=['이러므로']),
    dict(ref=(61, 3, 10), lang='ko', en='this', words=['이러므로']),
    dict(ref=(61, 3, 10), lang='ko', en='and', words=['또는']),

    # ---- 같은 영어 낱말 두 벌이 한국어 두 자리를 나눠 갖게 쪼갬 (일괄) ----
    # 첫째 벌이 두 자리를 다 쥐고 뒤쪽 벌이 통째로 비어 있던 곳.
    # 줄기가 같고 꼬리만 조사/어미로 다른 짝만 골랐고, 주변에 이미 걸린
    # 영어 낱말로 기대 위치를 잡아 어순이 뒤집힌 절은 자리를 맞바꿨다.
    dict(ref=(10, 2, 27), lang='ko', en='Lord#1', words=['여호와의']),
    dict(ref=(10, 2, 27), lang='ko', en='Lord#2', words=['여호와께서']),
    dict(ref=(10, 5, 8), lang='ko', en='timber#1', words=['재목에']),
    dict(ref=(10, 5, 8), lang='ko', en='timber#2', words=['재목과']),
    dict(ref=(10, 6, 3), lang='ko', en='cubits#1', words=['규빗이요']),
    dict(ref=(10, 6, 3), lang='ko', en='cubits#2', words=['규빗이며']),
    dict(ref=(10, 6, 5), lang='ko', en='chambers#1', words=['다락들을']),
    dict(ref=(10, 6, 5), lang='ko', en='chambers#2', words=['다락마다']),
    dict(ref=(10, 7, 6), lang='ko', en='porch#1', words=['낭실을']),
    dict(ref=(10, 7, 6), lang='ko', en='porch#2', words=['낭실이']),
    dict(ref=(10, 7, 16), lang='ko', en='cubits#1', words=['규빗이요']),
    dict(ref=(10, 7, 16), lang='ko', en='cubits#2', words=['규빗이며']),
    dict(ref=(10, 7, 22), lang='ko', en='pillars#1', words=['기둥']),
    dict(ref=(10, 7, 22), lang='ko', en='pillars#2', words=['기둥의']),
    dict(ref=(10, 7, 43), lang='ko', en='bases#1', words=['받침과']),
    dict(ref=(10, 7, 43), lang='ko', en='bases#2', words=['받침']),
    dict(ref=(10, 8, 8), lang='ko', en='seen#1', words=['보이나']),
    dict(ref=(10, 8, 8), lang='ko', en='seen#2', words=['보이지']),
    dict(ref=(10, 8, 47), lang='ko', en='captives#1', words=['사로잡은']),
    dict(ref=(10, 8, 47), lang='ko', en='captives#2', words=['사로잡혀']),
    dict(ref=(10, 8, 54), lang='ko', en='Lord#1', words=['여호와의']),
    dict(ref=(10, 8, 54), lang='ko', en='Lord#2', words=['여호와께']),
    dict(ref=(10, 8, 63), lang='ko', en='Lord#1', words=['여호와께']),
    dict(ref=(10, 8, 63), lang='ko', en='Lord#2', words=['여호와의']),
    dict(ref=(10, 10, 26), lang='ko', en='horsemen#1', words=['마병을']),
    dict(ref=(10, 10, 26), lang='ko', en='horsemen#2', words=['마병이']),
    dict(ref=(10, 11, 6), lang='ko', en='Lord#1', words=['여호와의']),
    dict(ref=(10, 11, 6), lang='ko', en='Lord#2', words=['여호와를']),
    dict(ref=(10, 13, 2), lang='ko', en='Lord#1', words=['여호와의']),
    dict(ref=(10, 13, 2), lang='ko', en='Lord#2', words=['여호와께서']),
    dict(ref=(10, 13, 28), lang='ko', en='lion#1', words=['사자는']),
    dict(ref=(10, 13, 28), lang='ko', en='lion#2', words=['사자가']),
    dict(ref=(10, 17, 14), lang='ko', en='Lord#1', words=['여호와의']),
    dict(ref=(10, 17, 14), lang='ko', en='Lord#2', words=['여호와가']),
    dict(ref=(10, 17, 20), lang='ko', en='Lord#1', words=['여호와께']),
    dict(ref=(10, 17, 20), lang='ko', en='Lord#2', words=['여호와여']),
    dict(ref=(10, 17, 21), lang='ko', en='child#1', words=['아이']),
    dict(ref=(10, 17, 21), lang='ko', en='child#2', words=['아이의']),
    dict(ref=(10, 17, 21), lang='ko', en='Lord#1', words=['여호와께']),
    dict(ref=(10, 17, 21), lang='ko', en='Lord#2', words=['여호와여']),
    dict(ref=(10, 18, 13), lang='ko', en='prophets#1', words=['선지자들을']),
    dict(ref=(10, 18, 13), lang='ko', en='prophets#2', words=['선지자']),
    dict(ref=(10, 18, 16), lang='ko', en='meet#1', words=['만나려']),
    dict(ref=(10, 18, 16), lang='ko', en='meet#2', words=['만나']),
    dict(ref=(10, 18, 30), lang='ko', en='people#1', words=['백성을']),
    dict(ref=(10, 18, 30), lang='ko', en='people#2', words=['백성이']),
    dict(ref=(10, 22, 14), lang='ko', en='Lord#1', words=['여호와의']),
    dict(ref=(10, 22, 14), lang='ko', en='Lord#2', words=['여호와께서']),
    dict(ref=(10, 22, 19), lang='ko', en='Lord#1', words=['여호와의']),
    dict(ref=(10, 22, 19), lang='ko', en='Lord#2', words=['여호와께서']),
    dict(ref=(11, 2, 2), lang='ko', en='Lord#1', words=['여호와께서']),
    dict(ref=(11, 2, 2), lang='ko', en='Lord#2', words=['여호와의']),
    dict(ref=(11, 2, 4), lang='ko', en='Lord#1', words=['여호와께서']),
    dict(ref=(11, 2, 4), lang='ko', en='Lord#2', words=['여호와의']),
    dict(ref=(11, 2, 6), lang='ko', en='Lord#1', words=['여호와께서']),
    dict(ref=(11, 2, 6), lang='ko', en='Lord#2', words=['여호와의']),
    dict(ref=(11, 3, 11), lang='ko', en='Lord#1', words=['여호와께']),
    dict(ref=(11, 3, 11), lang='ko', en='Lord#2', words=['여호와의']),
    dict(ref=(11, 6, 17), lang='ko', en='Lord#1', words=['여호와여']),
    dict(ref=(11, 6, 17), lang='ko', en='Lord#2', words=['여호와께서']),
    dict(ref=(11, 6, 20), lang='ko', en='Lord#1', words=['여호와여']),
    dict(ref=(11, 6, 20), lang='ko', en='Lord#2', words=['여호와께서']),
    dict(ref=(11, 7, 1), lang='ko', en='Lord#1', words=['여호와의']),
    dict(ref=(11, 7, 1), lang='ko', en='Lord#2', words=['여호와께서']),
    dict(ref=(11, 7, 10), lang='ko', en='man#1', words=['사람도']),
    dict(ref=(11, 7, 10), lang='ko', en='man#2', words=['사람의']),
    dict(ref=(11, 16, 6), lang='ko', en='Syria#1', words=['아람에']),
    dict(ref=(11, 16, 6), lang='ko', en='Syria#2', words=['아람#1']),
    dict(ref=(11, 18, 25), lang='ko', en='destroy#1', words=['멸하라']),
    dict(ref=(11, 18, 25), lang='ko', en='destroy#2', words=['멸하러']),
    dict(ref=(11, 20, 8), lang='ko', en='Lord#1', words=['여호와께서']),
    dict(ref=(11, 20, 8), lang='ko', en='Lord#2', words=['여호와의']),
    dict(ref=(11, 21, 4), lang='ko', en='Lord#1', words=['여호와의']),
    dict(ref=(11, 21, 4), lang='ko', en='Lord#2', words=['여호와께서']),
    dict(ref=(11, 22, 18), lang='ko', en='Lord#1', words=['여호와께']),
    dict(ref=(11, 22, 18), lang='ko', en='Lord#2', words=['여호와의']),
    dict(ref=(11, 24, 13), lang='ko', en='treasures#1', words=['보물과']),
    dict(ref=(11, 24, 13), lang='ko', en='treasures#2', words=['보물을']),
    dict(ref=(12, 4, 2), lang='ko', en='begat#1', words=['낳았고']),
    dict(ref=(12, 4, 2), lang='ko', en='begat#2', words=['낳았으니']),
    dict(ref=(12, 4, 10), lang='ko', en='God#1', words=['하나님께']),
    dict(ref=(12, 4, 10), lang='ko', en='God#2', words=['하나님이']),
    dict(ref=(12, 4, 23), lang='ko', en='dwelt#1', words=['거하는']),
    dict(ref=(12, 4, 23), lang='ko', en='dwelt#2', words=['거하여']),
    dict(ref=(12, 5, 25), lang='ko', en='God#1', words=['하나님께']),
    dict(ref=(12, 5, 25), lang='ko', en='God#2', words=['하나님이']),
    dict(ref=(12, 8, 34), lang='ko', en='Merib–baal#1', words=['므립바알이라']),
    dict(ref=(12, 8, 34), lang='ko', en='Merib–baal#2', words=['므립바알이']),
    dict(ref=(12, 9, 40), lang='ko', en='Merib–baal#1', words=['므립바알이라']),
    dict(ref=(12, 9, 40), lang='ko', en='Merib–baal#2', words=['므립바알이']),
    dict(ref=(12, 10, 13), lang='ko', en='Lord#1', words=['여호와께']),
    dict(ref=(12, 10, 13), lang='ko', en='Lord#2', words=['여호와의']),
    dict(ref=(12, 11, 6), lang='ko', en='chief#1', words=['두목이']),
    dict(ref=(12, 11, 6), lang='ko', en='chief#2', words=['두목과']),
    dict(ref=(12, 12, 22), lang='ko', en='host#1', words=['군대를']),
    dict(ref=(12, 12, 22), lang='ko', en='host#2', words=['군대와']),
    dict(ref=(12, 14, 14), lang='ko', en='God#1', words=['하나님께']),
    dict(ref=(12, 14, 14), lang='ko', en='God#2', words=['하나님이']),
    dict(ref=(12, 16, 4), lang='ko', en='Lord#1', words=['여호와의']),
    dict(ref=(12, 16, 4), lang='ko', en='Lord#2', words=['여호와를']),
    dict(ref=(12, 16, 29), lang='ko', en='Lord#1', words=['여호와의']),
    dict(ref=(12, 16, 29), lang='ko', en='Lord#2', words=['여호와께']),
    dict(ref=(12, 16, 36), lang='ko', en='ever#1', words=['영원부터']),
    dict(ref=(12, 16, 36), lang='ko', en='ever#2', words=['영원까지']),
    dict(ref=(12, 16, 40), lang='ko', en='Lord#1', words=['여호와께']),
    dict(ref=(12, 16, 40), lang='ko', en='Lord#2', words=['여호와의']),
    dict(ref=(12, 20, 2), lang='ko', en='head#1', words=['머리에서']),
    dict(ref=(12, 20, 2), lang='ko', en='head#2', words=['머리에']),
    dict(ref=(12, 21, 17), lang='ko', en='God#1', words=['하나님께']),
    dict(ref=(12, 21, 17), lang='ko', en='God#2', words=['하나님']),
    dict(ref=(12, 21, 18), lang='ko', en='Lord#1', words=['여호와를']),
    dict(ref=(12, 21, 18), lang='ko', en='Lord#2', words=['여호와의']),
    dict(ref=(12, 22, 12), lang='ko', en='Lord#1', words=['여호와께서']),
    dict(ref=(12, 22, 12), lang='ko', en='Lord#2', words=['여호와의']),
    dict(ref=(12, 24, 19), lang='ko', en='Lord#1', words=['여호와의']),
    dict(ref=(12, 24, 19), lang='ko', en='Lord#2', words=['여호와께서']),
    dict(ref=(12, 24, 20), lang='ko', en='Shubael#1', words=['수바엘이요']),
    dict(ref=(12, 24, 20), lang='ko', en='Shubael#2', words=['수바엘의']),
    dict(ref=(12, 24, 22), lang='ko', en='Shelomoth#1', words=['슬로못이요']),
    dict(ref=(12, 24, 22), lang='ko', en='Shelomoth#2', words=['슬로못의']),
    dict(ref=(12, 28, 5), lang='ko', en='Lord#1', words=['여호와께서']),
    dict(ref=(12, 28, 5), lang='ko', en='Lord#2', words=['여호와의']),
    dict(ref=(12, 28, 20), lang='ko', en='Lord#1', words=['여호와']),
    dict(ref=(12, 28, 20), lang='ko', en='Lord#2', words=['여호와의']),
    dict(ref=(12, 29, 4), lang='ko', en='talents#1', words=['달란트라']),
    dict(ref=(12, 29, 4), lang='ko', en='talents#2', words=['달란트와']),
    dict(ref=(12, 29, 10), lang='ko', en='Lord#1', words=['여호와를']),
    dict(ref=(12, 29, 10), lang='ko', en='Lord#2', words=['여호와여']),
    dict(ref=(13, 1, 14), lang='ko', en='chariots#1', words=['병거와']),
    dict(ref=(13, 1, 14), lang='ko', en='chariots#2', words=['병거가']),
    dict(ref=(13, 2, 12), lang='ko', en='Lord#1', words=['여호와는']),
    dict(ref=(13, 2, 12), lang='ko', en='Lord#2', words=['여호와를']),
    dict(ref=(13, 3, 1), lang='ko', en='Lord#1', words=['여호와의']),
    dict(ref=(13, 3, 1), lang='ko', en='Lord#2', words=['여호와께서']),
    dict(ref=(13, 4, 14), lang='ko', en='bases#1', words=['받침과']),
    dict(ref=(13, 4, 14), lang='ko', en='bases#2', words=['받침']),
    dict(ref=(13, 7, 3), lang='ko', en='Lord#1', words=['여호와의']),
    dict(ref=(13, 7, 3), lang='ko', en='Lord#2', words=['여호와께']),
    dict(ref=(13, 7, 6), lang='ko', en='priests#1', words=['제사장들은']),
    dict(ref=(13, 7, 6), lang='ko', en='priests#2', words=['제사장은']),
    dict(ref=(13, 8, 12), lang='ko', en='Lord#1', words=['여호와께']),
    dict(ref=(13, 8, 12), lang='ko', en='Lord#2', words=['여호와의']),
    dict(ref=(13, 9, 20), lang='ko', en='vessels#1', words=['그릇은']),
    dict(ref=(13, 9, 20), lang='ko', en='vessels#2', words=['그릇들도']),
    dict(ref=(13, 12, 7), lang='ko', en='Lord#1', words=['여호와께서']),
    dict(ref=(13, 12, 7), lang='ko', en='Lord#2', words=['여호와의']),
    dict(ref=(13, 13, 11), lang='ko', en='Lord#1', words=['여호와']),
    dict(ref=(13, 13, 11), lang='ko', en='Lord#2', words=['여호와의']),
    dict(ref=(13, 15, 6), lang='ko', en='nation#1', words=['나라가']),
    dict(ref=(13, 15, 6), lang='ko', en='nation#2', words=['나라와']),
    dict(ref=(13, 17, 2), lang='ko', en='cities#1', words=['성읍에']),
    dict(ref=(13, 17, 2), lang='ko', en='cities#2', words=['성읍들에']),
    dict(ref=(13, 18, 18), lang='ko', en='Lord#1', words=['여호와의']),
    dict(ref=(13, 18, 18), lang='ko', en='Lord#2', words=['여호와께서']),
    dict(ref=(13, 18, 20), lang='ko', en='Lord#1', words=['여호와']),
    dict(ref=(13, 18, 20), lang='ko', en='Lord#2', words=['여호와께서']),
    dict(ref=(13, 21, 19), lang='ko', en='burning#1', words=['분향하지']),
    dict(ref=(13, 21, 19), lang='ko', en='burning#2', words=['분향하던']),
    dict(ref=(13, 27, 2), lang='ko', en='Lord#1', words=['여호와']),
    dict(ref=(13, 27, 2), lang='ko', en='Lord#2', words=['여호와의']),
    dict(ref=(13, 28, 9), lang='ko', en='Lord#1', words=['여호와의']),
    dict(ref=(13, 28, 9), lang='ko', en='Lord#2', words=['여호와께서']),
    dict(ref=(13, 29, 6), lang='ko', en='Lord#1', words=['여호와']),
    dict(ref=(13, 29, 6), lang='ko', en='Lord#2', words=['여호와의']),
    dict(ref=(13, 29, 27), lang='ko', en='burnt#1', words=['번제를']),
    dict(ref=(13, 29, 27), lang='ko', en='burnt#2', words=['번제']),
    dict(ref=(13, 29, 31), lang='ko', en='Lord#1', words=['여호와께']),
    dict(ref=(13, 29, 31), lang='ko', en='Lord#2', words=['여호와의']),
    dict(ref=(13, 30, 1), lang='ko', en='Lord#1', words=['여호와의']),
    dict(ref=(13, 30, 1), lang='ko', en='Lord#2', words=['여호와를']),
    dict(ref=(13, 31, 10), lang='ko', en='Lord#1', words=['여호와의']),
    dict(ref=(13, 31, 10), lang='ko', en='Lord#2', words=['여호와께서']),
    dict(ref=(13, 33, 4), lang='ko', en='Lord#1', words=['여호와께서']),
    dict(ref=(13, 33, 4), lang='ko', en='Lord#2', words=['여호와의']),
    dict(ref=(13, 33, 16), lang='ko', en='Lord#1', words=['여호와의']),
    dict(ref=(13, 33, 16), lang='ko', en='Lord#2', words=['여호와를']),
    dict(ref=(13, 33, 18), lang='ko', en='God#1', words=['하나님께']),
    dict(ref=(13, 33, 18), lang='ko', en='God#2', words=['하나님']),
    dict(ref=(13, 33, 23), lang='ko', en='humbled#1', words=['겸비치']),
    dict(ref=(13, 33, 23), lang='ko', en='humbled#2', words=['겸비함']),
    dict(ref=(13, 34, 26), lang='ko', en='Lord#1', words=['여호와께']),
    dict(ref=(13, 34, 26), lang='ko', en='Lord#2', words=['여호와의']),
    dict(ref=(13, 35, 16), lang='ko', en='Lord#1', words=['여호와의']),
    dict(ref=(13, 35, 16), lang='ko', en='Lord#2', words=['여호와를']),
    dict(ref=(13, 36, 12), lang='ko', en='Lord#1', words=['여호와']),
    dict(ref=(13, 36, 12), lang='ko', en='Lord#2', words=['여호와의']),
    dict(ref=(14, 3, 6), lang='ko', en='Lord#1', words=['여호와께']),
    dict(ref=(14, 3, 6), lang='ko', en='Lord#2', words=['여호와의']),
    dict(ref=(14, 3, 10), lang='ko', en='Lord#1', words=['여호와의']),
    dict(ref=(14, 3, 10), lang='ko', en='Lord#2', words=['여호와를']),
    dict(ref=(14, 7, 27), lang='ko', en='Lord#1', words=['여호와를']),
    dict(ref=(14, 7, 27), lang='ko', en='Lord#2', words=['여호와의']),
    dict(ref=(15, 4, 5), lang='ko', en='before#1', words=['앞에서#1']),
    dict(ref=(15, 4, 5), lang='ko', en='before#2', words=['앞에서#2']),
    dict(ref=(15, 5, 14), lang='ko', en='governor#1', words=['총독으로']),
    dict(ref=(15, 5, 14), lang='ko', en='governor#2', words=['총독의']),
    dict(ref=(15, 9, 3), lang='ko', en='Lord#1', words=['여호와의']),
    dict(ref=(15, 9, 3), lang='ko', en='Lord#2', words=['여호와께']),
    dict(ref=(15, 9, 5), lang='ko', en='ever#1', words=['영원부터']),
    dict(ref=(15, 9, 5), lang='ko', en='ever#2', words=['영원까지']),
    dict(ref=(16, 6, 7), lang='ko', en='king#1', words=['왕께']),
    dict(ref=(16, 6, 7), lang='ko', en='king#2', words=['왕께서']),
    dict(ref=(16, 9, 1), lang='ko', en='Jews#1', words=['유다인이']),
    dict(ref=(16, 9, 1), lang='ko', en='Jews#2', words=['유다인의']),
    dict(ref=(17, 3, 26), lang='ko', en='neither#1', words=['없고#1']),
    dict(ref=(17, 3, 26), lang='ko', en='neither#2', words=['없고#2']),
    dict(ref=(17, 20, 29), lang='ko', en='God#1', words=['하나님께']),
    dict(ref=(17, 20, 29), lang='ko', en='God#2', words=['하나님이']),
    dict(ref=(18, 7, 8), lang='ko', en='Lord#1', words=['여호와께서']),
    dict(ref=(18, 7, 8), lang='ko', en='Lord#2', words=['여호와여']),
    dict(ref=(18, 11, 4), lang='ko', en='Lord#1', words=['여호와께서']),
    dict(ref=(18, 11, 4), lang='ko', en='Lord#2', words=['여호와의']),
    dict(ref=(18, 19, 9), lang='ko', en='Lord#1', words=['여호와를']),
    dict(ref=(18, 19, 9), lang='ko', en='Lord#2', words=['여호와의']),
    dict(ref=(18, 22, 4), lang='ko', en='trusted#1', words=['의뢰하였고']),
    dict(ref=(18, 22, 4), lang='ko', en='trusted#2', words=['의뢰하였으므로']),
    dict(ref=(18, 29, 2), lang='ko', en='Lord#1', words=['여호와의']),
    dict(ref=(18, 29, 2), lang='ko', en='Lord#2', words=['여호와께']),
    dict(ref=(18, 29, 5), lang='ko', en='Lord#1', words=['여호와의']),
    dict(ref=(18, 29, 5), lang='ko', en='Lord#2', words=['여호와께서']),
    dict(ref=(18, 29, 8), lang='ko', en='Lord#1', words=['여호와의']),
    dict(ref=(18, 29, 8), lang='ko', en='Lord#2', words=['여호와께서']),
    dict(ref=(18, 41, 13), lang='ko', en='everlasting#1', words=['영원부터']),
    dict(ref=(18, 41, 13), lang='ko', en='everlasting#2', words=['영원까지']),
    dict(ref=(18, 62, 11), lang='ko', en='God#1', words=['하나님이']),
    dict(ref=(18, 62, 11), lang='ko', en='God#2', words=['하나님께']),
    dict(ref=(18, 69, 27), lang='ko', en='iniquity#1', words=['죄악을']),
    dict(ref=(18, 69, 27), lang='ko', en='iniquity#2', words=['죄악에']),
    dict(ref=(18, 78, 7), lang='ko', en='God#1', words=['하나님께']),
    dict(ref=(18, 78, 7), lang='ko', en='God#2', words=['하나님의']),
    dict(ref=(18, 89, 8), lang='ko', en='Lord#1', words=['여호와여']),
    dict(ref=(18, 89, 8), lang='ko', en='Lord#2', words=['여호와']),
    dict(ref=(18, 90, 2), lang='ko', en='everlasting#1', words=['영원부터']),
    dict(ref=(18, 90, 2), lang='ko', en='everlasting#2', words=['영원까지']),
    dict(ref=(18, 103, 17), lang='ko', en='everlasting#1', words=['영원부터']),
    dict(ref=(18, 103, 17), lang='ko', en='everlasting#2', words=['영원까지']),
    dict(ref=(18, 103, 17), lang='ko', en='children#1', words=['자손의']),
    dict(ref=(18, 103, 17), lang='ko', en='children#2', words=['자손에게']),
    dict(ref=(18, 103, 22), lang='ko', en='Lord#1', words=['여호와의']),
    dict(ref=(18, 103, 22), lang='ko', en='Lord#2', words=['여호와를#1']),
    dict(ref=(18, 104, 1), lang='ko', en='Lord#1', words=['여호와를']),
    dict(ref=(18, 104, 1), lang='ko', en='Lord#2', words=['여호와']),
    dict(ref=(18, 106, 48), lang='ko', en='everlasting#1', words=['영원부터']),
    dict(ref=(18, 106, 48), lang='ko', en='everlasting#2', words=['영원까지']),
    dict(ref=(18, 113, 8), lang='ko', en='princes#1', words=['방백들과']),
    dict(ref=(18, 113, 8), lang='ko', en='princes#2', words=['방백들']),
    dict(ref=(18, 116, 4), lang='ko', en='Lord#1', words=['여호와의']),
    dict(ref=(18, 116, 4), lang='ko', en='Lord#2', words=['여호와여']),
    dict(ref=(18, 121, 5), lang='ko', en='Lord#1', words=['여호와는']),
    dict(ref=(18, 121, 5), lang='ko', en='Lord#2', words=['여호와께서']),
    dict(ref=(18, 128, 6), lang='ko', en='children#1', words=['자식의']),
    dict(ref=(18, 128, 6), lang='ko', en='children#2', words=['자식을']),
    dict(ref=(18, 130, 2), lang='ko', en='voice#1', words=['소리를']),
    dict(ref=(18, 130, 2), lang='ko', en='voice#2', words=['소리에']),
    dict(ref=(18, 135, 3), lang='ko', en='Lord#1', words=['여호와를']),
    dict(ref=(18, 135, 3), lang='ko', en='Lord#2', words=['여호와는']),
    dict(ref=(18, 138, 8), lang='ko', en='Lord#1', words=['여호와께서']),
    dict(ref=(18, 138, 8), lang='ko', en='Lord#2', words=['여호와여']),
    dict(ref=(18, 139, 21), lang='ko', en='hate#1', words=['미워하는']),
    dict(ref=(18, 139, 21), lang='ko', en='hate#2', words=['미워하지']),
    dict(ref=(18, 140, 6), lang='ko', en='Lord#1', words=['여호와께']),
    dict(ref=(18, 140, 6), lang='ko', en='Lord#2', words=['여호와여']),
    dict(ref=(18, 143, 4), lang='ko', en='within#1', words=['속에서#1']),
    dict(ref=(18, 143, 4), lang='ko', en='within#2', words=['속에서#2']),
    dict(ref=(19, 6, 3), lang='ko', en='friend#1', words=['이웃의']),
    dict(ref=(19, 6, 3), lang='ko', en='friend#2', words=['이웃에게']),
    dict(ref=(19, 13, 4), lang='ko', en='soul#1', words=['마음으로']),
    dict(ref=(19, 13, 4), lang='ko', en='soul#2', words=['마음은']),
    dict(ref=(19, 22, 29), lang='ko', en='before#1', words=['앞에#2']),
    dict(ref=(19, 22, 29), lang='ko', en='before#2', words=['앞에#1']),
    dict(ref=(20, 1, 18), lang='ko', en='much#1', words=['많으면']),
    dict(ref=(20, 1, 18), lang='ko', en='much#2', words=['많으니']),
    dict(ref=(20, 1, 18), lang='ko', en='increaseth#1', words=['더하느니라']),
    dict(ref=(20, 1, 18), lang='ko', en='increaseth#2', words=['더하는']),
    dict(ref=(20, 2, 26), lang='ko', en='giveth#1', words=['주시나']),
    dict(ref=(20, 2, 26), lang='ko', en='giveth#2', words=['주시고']),
    dict(ref=(21, 8, 7), lang='ko', en='love#1', words=['사랑은']),
    dict(ref=(21, 8, 7), lang='ko', en='love#2', words=['사랑과']),
    dict(ref=(22, 3, 12), lang='ko', en='people#1', words=['백성을']),
    dict(ref=(22, 3, 12), lang='ko', en='people#2', words=['백성이여']),
    dict(ref=(22, 5, 20), lang='ko', en='light#1', words=['광명을']),
    dict(ref=(22, 5, 20), lang='ko', en='light#2', words=['광명으로']),
    dict(ref=(22, 7, 8), lang='ko', en='head#1', words=['머리는#4']),
    dict(ref=(22, 7, 8), lang='ko', en='head#2', words=['머리는#1']),
    dict(ref=(22, 11, 2), lang='ko', en='Lord#1', words=['여호와의']),
    dict(ref=(22, 11, 2), lang='ko', en='Lord#2', words=['여호와를']),
    dict(ref=(22, 14, 2), lang='ko', en='captives#1', words=['사로잡던']),
    dict(ref=(22, 14, 2), lang='ko', en='captives#2', words=['사로잡고']),
    dict(ref=(22, 14, 22), lang='ko', en='Lord#1', words=['여호와께서']),
    dict(ref=(22, 14, 22), lang='ko', en='Lord#2', words=['여호와의']),
    dict(ref=(22, 19, 2), lang='ko', en='city#1', words=['성읍이']),
    dict(ref=(22, 19, 2), lang='ko', en='city#2', words=['성읍을']),
    dict(ref=(22, 19, 2), lang='ko', en='kingdom#1', words=['나라가']),
    dict(ref=(22, 19, 2), lang='ko', en='kingdom#2', words=['나라를']),
    dict(ref=(22, 22, 25), lang='ko', en='Lord#1', words=['여호와께서']),
    dict(ref=(22, 22, 25), lang='ko', en='Lord#2', words=['여호와의']),
    dict(ref=(22, 23, 4), lang='ko', en='sea#1', words=['바다']),
    dict(ref=(22, 23, 4), lang='ko', en='sea#2', words=['바다의']),
    dict(ref=(22, 24, 18), lang='ko', en='pit#1', words=['함정에']),
    dict(ref=(22, 24, 18), lang='ko', en='pit#2', words=['함정']),
    dict(ref=(22, 30, 18), lang='ko', en='Lord#1', words=['여호와께서']),
    dict(ref=(22, 30, 18), lang='ko', en='Lord#2', words=['여호와는']),
    dict(ref=(22, 36, 10), lang='ko', en='destroy#1', words=['멸하는']),
    dict(ref=(22, 36, 10), lang='ko', en='destroy#2', words=['멸하라']),
    dict(ref=(22, 37, 14), lang='ko', en='Lord#1', words=['여호와의']),
    dict(ref=(22, 37, 14), lang='ko', en='Lord#2', words=['여호와']),
    dict(ref=(22, 38, 20), lang='ko', en='Lord#1', words=['여호와께서']),
    dict(ref=(22, 38, 20), lang='ko', en='Lord#2', words=['여호와의']),
    dict(ref=(22, 44, 24), lang='ko', en='Lord#1', words=['여호와라']),
    dict(ref=(22, 44, 24), lang='ko', en='Lord#2', words=['여호와가']),
    dict(ref=(22, 49, 5), lang='ko', en='Lord#1', words=['여호와께서']),
    dict(ref=(22, 49, 5), lang='ko', en='Lord#2', words=['여호와의']),
    dict(ref=(22, 50, 10), lang='ko', en='Lord#1', words=['여호와를']),
    dict(ref=(22, 50, 10), lang='ko', en='Lord#2', words=['여호와의']),
    dict(ref=(22, 51, 3), lang='ko', en='Lord#1', words=['여호와가']),
    dict(ref=(22, 51, 3), lang='ko', en='Lord#2', words=['여호와의']),
    dict(ref=(22, 53, 10), lang='ko', en='Lord#1', words=['여호와께서']),
    dict(ref=(22, 53, 10), lang='ko', en='Lord#2', words=['여호와의']),
    dict(ref=(22, 56, 6), lang='ko', en='Lord#1', words=['여호와에게']),
    dict(ref=(22, 56, 6), lang='ko', en='Lord#2', words=['여호와의']),
    dict(ref=(22, 59, 21), lang='ko', en='Lord#1', words=['여호와께서']),
    dict(ref=(22, 59, 21), lang='ko', en='Lord#2', words=['여호와의']),
    dict(ref=(22, 66, 5), lang='ko', en='Lord#1', words=['여호와의']),
    dict(ref=(22, 66, 5), lang='ko', en='Lord#2', words=['여호와께서는']),
    dict(ref=(23, 3, 13), lang='ko', en='Lord#1', words=['여호와를']),
    dict(ref=(23, 3, 13), lang='ko', en='Lord#2', words=['여호와의']),
    dict(ref=(23, 4, 31), lang='ko', en='voice#1', words=['소리를']),
    dict(ref=(23, 4, 31), lang='ko', en='voice#2', words=['소리#1']),
    dict(ref=(23, 9, 6), lang='ko', en='deceit#1', words=['궤휼']),
    dict(ref=(23, 9, 6), lang='ko', en='deceit#2', words=['궤휼로']),
    dict(ref=(23, 11, 21), lang='ko', en='Lord#1', words=['여호와께서']),
    dict(ref=(23, 11, 21), lang='ko', en='Lord#2', words=['여호와의']),
    dict(ref=(23, 16, 5), lang='ko', en='Lord#1', words=['여호와께서']),
    dict(ref=(23, 16, 5), lang='ko', en='Lord#2', words=['여호와의']),
    dict(ref=(23, 16, 14), lang='ko', en='Lord#1', words=['여호와께서']),
    dict(ref=(23, 16, 14), lang='ko', en='Lord#2', words=['여호와의']),
    dict(ref=(23, 19, 3), lang='ko', en='Lord#1', words=['여호와의']),
    dict(ref=(23, 19, 3), lang='ko', en='Lord#2', words=['여호와']),
    dict(ref=(23, 20, 13), lang='ko', en='Lord#1', words=['여호와께']),
    dict(ref=(23, 20, 13), lang='ko', en='Lord#2', words=['여호와를']),
    dict(ref=(23, 23, 2), lang='ko', en='Lord#1', words=['여호와의']),
    dict(ref=(23, 23, 2), lang='ko', en='Lord#2', words=['여호와가']),
    dict(ref=(23, 23, 7), lang='ko', en='Lord#1', words=['여호와가']),
    dict(ref=(23, 23, 7), lang='ko', en='Lord#2', words=['여호와의']),
    dict(ref=(23, 23, 16), lang='ko', en='Lord#1', words=['여호와께서']),
    dict(ref=(23, 23, 16), lang='ko', en='Lord#2', words=['여호와의']),
    dict(ref=(23, 23, 32), lang='ko', en='Lord#1', words=['여호와가']),
    dict(ref=(23, 23, 32), lang='ko', en='Lord#2', words=['여호와의']),
    dict(ref=(23, 23, 36), lang='ko', en='Lord#1', words=['여호와의']),
    dict(ref=(23, 23, 36), lang='ko', en='Lord#2', words=['여호와']),
    dict(ref=(23, 24, 1), lang='ko', en='Lord#1', words=['여호와의']),
    dict(ref=(23, 24, 1), lang='ko', en='Lord#2', words=['여호와께서']),
    dict(ref=(23, 25, 17), lang='ko', en='Lord#1', words=['여호와의']),
    dict(ref=(23, 25, 17), lang='ko', en='Lord#2', words=['여호와께서']),
    dict(ref=(23, 25, 32), lang='ko', en='nation#1', words=['나라에서']),
    dict(ref=(23, 25, 32), lang='ko', en='nation#2', words=['나라에']),
    dict(ref=(23, 26, 13), lang='ko', en='Lord#1', words=['여호와의']),
    dict(ref=(23, 26, 13), lang='ko', en='Lord#2', words=['여호와께서']),
    dict(ref=(23, 27, 16), lang='ko', en='Lord#1', words=['여호와께서']),
    dict(ref=(23, 27, 16), lang='ko', en='Lord#2', words=['여호와의']),
    dict(ref=(23, 29, 11), lang='ko', en='thoughts#1', words=['생각이라']),
    dict(ref=(23, 29, 11), lang='ko', en='thoughts#2', words=['생각은']),
    dict(ref=(23, 29, 14), lang='ko', en='Lord#1', words=['여호와가']),
    dict(ref=(23, 29, 14), lang='ko', en='Lord#2', words=['여호와의']),
    dict(ref=(23, 30, 3), lang='ko', en='Lord#1', words=['여호와의']),
    dict(ref=(23, 30, 3), lang='ko', en='Lord#2', words=['여호와가']),
    dict(ref=(23, 31, 7), lang='ko', en='Lord#1', words=['여호와가']),
    dict(ref=(23, 31, 7), lang='ko', en='Lord#2', words=['여호와여']),
    dict(ref=(23, 31, 16), lang='ko', en='Lord#1', words=['여호와의']),
    dict(ref=(23, 31, 16), lang='ko', en='Lord#2', words=['여호와가']),
    dict(ref=(23, 31, 34), lang='ko', en='Lord#1', words=['여호와를']),
    dict(ref=(23, 31, 34), lang='ko', en='Lord#2', words=['여호와의']),
    dict(ref=(23, 31, 37), lang='ko', en='Lord#1', words=['여호와의']),
    dict(ref=(23, 31, 37), lang='ko', en='Lord#2', words=['여호와가']),
    dict(ref=(23, 34, 2), lang='ko', en='Lord#1', words=['여호와가']),
    dict(ref=(23, 34, 2), lang='ko', en='Lord#2', words=['여호와의']),
    dict(ref=(23, 34, 4), lang='ko', en='Lord#1', words=['여호와가']),
    dict(ref=(23, 34, 4), lang='ko', en='Lord#2', words=['여호와의']),
    dict(ref=(23, 34, 17), lang='ko', en='Lord#1', words=['여호와의']),
    dict(ref=(23, 34, 17), lang='ko', en='Lord#2', words=['여호와가']),
    dict(ref=(23, 35, 13), lang='ko', en='Lord#1', words=['여호와의']),
    dict(ref=(23, 35, 13), lang='ko', en='Lord#2', words=['여호와']),
    dict(ref=(23, 42, 6), lang='ko', en='Lord#1', words=['여호와께']),
    dict(ref=(23, 42, 6), lang='ko', en='Lord#2', words=['여호와의']),
    dict(ref=(23, 42, 15), lang='ko', en='Lord#1', words=['여호와의']),
    dict(ref=(23, 42, 15), lang='ko', en='Lord#2', words=['여호와']),
    dict(ref=(23, 43, 1), lang='ko', en='Lord#1', words=['여호와의']),
    dict(ref=(23, 43, 1), lang='ko', en='Lord#2', words=['여호와께서']),
    dict(ref=(23, 46, 12), lang='ko', en='mighty#1', words=['용사가']),
    dict(ref=(23, 46, 12), lang='ko', en='mighty#2', words=['용사에게']),
    dict(ref=(23, 51, 10), lang='ko', en='Lord#1', words=['여호와께서']),
    dict(ref=(23, 51, 10), lang='ko', en='Lord#2', words=['여호와의']),
    dict(ref=(23, 51, 11), lang='ko', en='Lord#1', words=['여호와께서']),
    dict(ref=(23, 51, 11), lang='ko', en='Lord#2', words=['여호와의']),
    dict(ref=(23, 52, 21), lang='ko', en='cubits#1', words=['규빗이요']),
    dict(ref=(23, 52, 21), lang='ko', en='cubits#2', words=['규빗이며']),
    dict(ref=(24, 2, 12), lang='ko', en='mothers#1', words=['어미의']),
    dict(ref=(24, 2, 12), lang='ko', en='mothers#2', words=['어미에게']),
    dict(ref=(25, 1, 21), lang='ko', en='went#1', words=['행하면']),
    dict(ref=(25, 1, 21), lang='ko', en='went#2', words=['행하고']),
    dict(ref=(25, 7, 26), lang='ko', en='rumour#1', words=['소문에']),
    dict(ref=(25, 7, 26), lang='ko', en='rumour#2', words=['소문이']),
    dict(ref=(25, 16, 45), lang='ko', en='mother#1', words=['어미의']),
    dict(ref=(25, 16, 45), lang='ko', en='mother#2', words=['어미는']),
    dict(ref=(25, 18, 20), lang='ko', en='father#1', words=['아비의']),
    dict(ref=(25, 18, 20), lang='ko', en='father#2', words=['아비는']),
    dict(ref=(25, 28, 6), lang='ko', en='heart#1', words=['마음이']),
    dict(ref=(25, 28, 6), lang='ko', en='heart#2', words=['마음']),
    dict(ref=(25, 32, 27), lang='ko', en='mighty#1', words=['용사와']),
    dict(ref=(25, 32, 27), lang='ko', en='mighty#2', words=['용사의']),
    dict(ref=(25, 34, 17), lang='ko', en='between#1', words=['사이에']),
    dict(ref=(25, 34, 17), lang='ko', en='between#2', words=['사이와']),
    dict(ref=(25, 34, 29), lang='ko', en='more#1', words=['다시는#1']),
    dict(ref=(25, 34, 29), lang='ko', en='more#2', words=['다시는#2']),
    dict(ref=(25, 36, 1), lang='ko', en='mountains#1', words=['산들에게']),
    dict(ref=(25, 36, 1), lang='ko', en='mountains#2', words=['산들아']),
    dict(ref=(25, 36, 14), lang='ko', en='more#1', words=['다시는#1']),
    dict(ref=(25, 36, 14), lang='ko', en='more#2', words=['다시는#2']),
    dict(ref=(25, 37, 26), lang='ko', en='covenant#1', words=['언약을']),
    dict(ref=(25, 37, 26), lang='ko', en='covenant#2', words=['언약이']),
    dict(ref=(25, 41, 6), lang='ko', en='chambers#1', words=['골방은']),
    dict(ref=(25, 41, 6), lang='ko', en='chambers#2', words=['골방이#1']),
    dict(ref=(25, 42, 6), lang='ko', en='pillars#1', words=['기둥이']),
    dict(ref=(25, 42, 6), lang='ko', en='pillars#2', words=['기둥']),
    dict(ref=(25, 42, 14), lang='ko', en='garments#1', words=['의복은']),
    dict(ref=(25, 42, 14), lang='ko', en='garments#2', words=['의복을']),
    dict(ref=(25, 44, 5), lang='ko', en='Lord#1', words=['여호와께서']),
    dict(ref=(25, 44, 5), lang='ko', en='Lord#2', words=['여호와의']),
    dict(ref=(26, 7, 10), lang='ko', en='before#1', words=['앞에서']),
    dict(ref=(26, 7, 10), lang='ko', en='before#2', words=['앞에']),
    dict(ref=(26, 9, 14), lang='ko', en='Lord#1', words=['여호와께서']),
    dict(ref=(26, 9, 14), lang='ko', en='Lord#2', words=['여호와는']),
    dict(ref=(27, 4, 1), lang='ko', en='Lord#1', words=['여호와의']),
    dict(ref=(27, 4, 1), lang='ko', en='Lord#2', words=['여호와께서']),
    dict(ref=(27, 12, 6), lang='ko', en='God#1', words=['하나님께로']),
    dict(ref=(27, 12, 6), lang='ko', en='God#2', words=['하나님을']),
    dict(ref=(27, 13, 14), lang='ko', en='death#1', words=['사망에서']),
    dict(ref=(27, 13, 14), lang='ko', en='death#2', words=['사망아']),
    dict(ref=(28, 1, 9), lang='ko', en='Lord#1', words=['여호와의']),
    dict(ref=(28, 1, 9), lang='ko', en='Lord#2', words=['여호와께']),
    dict(ref=(28, 1, 13), lang='ko', en='God#1', words=['하나님께']),
    dict(ref=(28, 1, 13), lang='ko', en='God#2', words=['하나님의']),
    dict(ref=(28, 1, 14), lang='ko', en='Lord#1', words=['여호와께']),
    dict(ref=(28, 1, 14), lang='ko', en='Lord#2', words=['여호와의']),
    dict(ref=(28, 1, 15), lang='ko', en='day#1', words=['날이여']),
    dict(ref=(28, 1, 15), lang='ko', en='day#2', words=['날이']),
    dict(ref=(28, 2, 11), lang='ko', en='Lord#1', words=['여호와께서']),
    dict(ref=(28, 2, 11), lang='ko', en='Lord#2', words=['여호와의']),
    dict(ref=(28, 2, 17), lang='ko', en='Lord#1', words=['여호와께']),
    dict(ref=(28, 2, 17), lang='ko', en='Lord#2', words=['여호와여']),
    dict(ref=(29, 2, 4), lang='ko', en='Lord#1', words=['여호와께서']),
    dict(ref=(29, 2, 4), lang='ko', en='Lord#2', words=['여호와의']),
    dict(ref=(29, 7, 14), lang='ko', en='prophet#1', words=['선지자가']),
    dict(ref=(29, 7, 14), lang='ko', en='prophet#2', words=['선지자의']),
    dict(ref=(29, 8, 12), lang='ko', en='sea#1', words=['바다에서']),
    dict(ref=(29, 8, 12), lang='ko', en='sea#2', words=['바다까지']),
    dict(ref=(31, 1, 6), lang='ko', en='God#1', words=['하나님께']),
    dict(ref=(31, 1, 6), lang='ko', en='God#2', words=['하나님이']),
    dict(ref=(32, 1, 11), lang='ko', en='inhabitant#1', words=['거민아']),
    dict(ref=(32, 1, 11), lang='ko', en='inhabitant#2', words=['거민은']),
    dict(ref=(32, 6, 2), lang='ko', en='Lord#1', words=['여호와의']),
    dict(ref=(32, 6, 2), lang='ko', en='Lord#2', words=['여호와께서']),
    dict(ref=(35, 1, 5), lang='ko', en='worship#1', words=['경배하는']),
    dict(ref=(35, 1, 5), lang='ko', en='worship#2', words=['경배하며']),
    dict(ref=(35, 2, 3), lang='ko', en='Lord#1', words=['여호와의#1']),
    dict(ref=(35, 2, 3), lang='ko', en='Lord#2', words=['여호와를']),
    dict(ref=(36, 1, 2), lang='ko', en='Lord#1', words=['여호와가']),
    dict(ref=(36, 1, 2), lang='ko', en='Lord#2', words=['여호와의']),
    dict(ref=(37, 1, 16), lang='ko', en='Lord#1', words=['여호와의']),
    dict(ref=(37, 1, 16), lang='ko', en='Lord#2', words=['여호와가']),
    dict(ref=(37, 1, 17), lang='ko', en='Lord#1', words=['여호와의']),
    dict(ref=(37, 1, 17), lang='ko', en='Lord#2', words=['여호와가']),
    dict(ref=(37, 3, 2), lang='ko', en='Satan#1', words=['사단에게']),
    dict(ref=(37, 3, 2), lang='ko', en='Satan#2', words=['사단아']),
    dict(ref=(37, 6, 12), lang='ko', en='Lord#1', words=['여호와께서']),
    dict(ref=(37, 6, 12), lang='ko', en='Lord#2', words=['여호와의']),
    dict(ref=(37, 8, 3), lang='ko', en='Lord#1', words=['여호와가']),
    dict(ref=(37, 8, 3), lang='ko', en='Lord#2', words=['여호와의']),
    dict(ref=(37, 8, 6), lang='ko', en='Lord#1', words=['여호와의']),
    dict(ref=(37, 8, 6), lang='ko', en='Lord#2', words=['여호와가']),
    dict(ref=(37, 9, 1), lang='ko', en='Lord#1', words=['여호와의']),
    dict(ref=(37, 9, 1), lang='ko', en='Lord#2', words=['여호와를']),
    dict(ref=(37, 9, 9), lang='ko', en='ass#1', words=['나귀를']),
    dict(ref=(37, 9, 9), lang='ko', en='ass#2', words=['나귀의']),
    dict(ref=(37, 9, 10), lang='ko', en='sea#1', words=['바다에서']),
    dict(ref=(37, 9, 10), lang='ko', en='sea#2', words=['바다까지']),
    dict(ref=(37, 10, 1), lang='ko', en='Lord#1', words=['여호와']),
    dict(ref=(37, 10, 1), lang='ko', en='Lord#2', words=['여호와께']),
    dict(ref=(37, 10, 12), lang='ko', en='Lord#1', words=['여호와를']),
    dict(ref=(37, 10, 12), lang='ko', en='Lord#2', words=['여호와의']),
    dict(ref=(37, 11, 13), lang='ko', en='Lord#1', words=['여호와께서']),
    dict(ref=(37, 11, 13), lang='ko', en='Lord#2', words=['여호와의']),
    dict(ref=(37, 12, 1), lang='ko', en='Lord#1', words=['여호와의']),
    dict(ref=(37, 12, 1), lang='ko', en='Lord#2', words=['여호와']),
    dict(ref=(38, 1, 13), lang='ko', en='Lord#1', words=['여호와가']),
    dict(ref=(38, 1, 13), lang='ko', en='Lord#2', words=['여호와의']),
    dict(ref=(38, 2, 16), lang='ko', en='Lord#1', words=['여호와가']),
    dict(ref=(38, 2, 16), lang='ko', en='Lord#2', words=['여호와의']),
    dict(ref=(38, 2, 17), lang='ko', en='Lord#1', words=['여호와를#1']),
    dict(ref=(38, 2, 17), lang='ko', en='Lord#2', words=['여호와의']),
    dict(ref=(38, 3, 18), lang='ko', en='serveth#1', words=['섬기지']),
    dict(ref=(38, 3, 18), lang='ko', en='serveth#2', words=['섬기는']),
    dict(ref=(39, 9, 34), lang='ko', en='devils#1', words=['귀신을']),
    dict(ref=(39, 9, 34), lang='ko', en='devils#2', words=['귀신의']),
    dict(ref=(39, 10, 19), lang='ko', en='speak#1', words=['말할까']),
    dict(ref=(39, 10, 19), lang='ko', en='speak#2', words=['말할']),
    dict(ref=(39, 10, 21), lang='ko', en='brother#1', words=['형제가']),
    dict(ref=(39, 10, 21), lang='ko', en='brother#2', words=['형제를']),
    dict(ref=(39, 12, 24), lang='ko', en='devils#1', words=['귀신을']),
    dict(ref=(39, 12, 24), lang='ko', en='devils#2', words=['귀신의']),
    dict(ref=(39, 12, 26), lang='ko', en='Satan#1', words=['사단이']),
    dict(ref=(39, 12, 26), lang='ko', en='Satan#2', words=['사단을']),
    dict(ref=(39, 13, 57), lang='ko', en='own#1', words=['자기#1']),
    dict(ref=(39, 13, 57), lang='ko', en='own#2', words=['자기#2']),
    dict(ref=(39, 22, 44), lang='ko', en='Lord#1', words=['주께서']),
    dict(ref=(39, 22, 44), lang='ko', en='Lord#2', words=['주께']),
    dict(ref=(39, 23, 34), lang='ko', en='city#1', words=['동네에서']),
    dict(ref=(39, 23, 34), lang='ko', en='city#2', words=['동네로']),
    dict(ref=(39, 24, 7), lang='ko', en='nation#1', words=['민족이']),
    dict(ref=(39, 24, 7), lang='ko', en='nation#2', words=['민족을']),
    dict(ref=(39, 24, 7), lang='ko', en='kingdom#1', words=['나라가']),
    dict(ref=(39, 24, 7), lang='ko', en='kingdom#2', words=['나라를']),
    dict(ref=(39, 25, 31), lang='ko', en='glory#1', words=['영광으로']),
    dict(ref=(39, 25, 31), lang='ko', en='glory#2', words=['영광의']),
    dict(ref=(39, 26, 29), lang='ko', en='drink#1', words=['마시지']),
    dict(ref=(39, 26, 29), lang='ko', en='drink#2', words=['마시는']),
    dict(ref=(39, 27, 43), lang='ko', en='God#1', words=['하나님을']),
    dict(ref=(39, 27, 43), lang='ko', en='God#2', words=['하나님이']),
    dict(ref=(40, 1, 34), lang='ko', en='many#1', words=['많은#1']),
    dict(ref=(40, 1, 34), lang='ko', en='many#2', words=['많은#2']),
    dict(ref=(40, 2, 18), lang='ko', en='Pharisees#1', words=['바리새인들이']),
    dict(ref=(40, 2, 18), lang='ko', en='Pharisees#2', words=['바리새인의']),
    dict(ref=(40, 3, 23), lang='ko', en='Satan#1', words=['사단이']),
    dict(ref=(40, 3, 23), lang='ko', en='Satan#2', words=['사단을']),
    dict(ref=(40, 4, 15), lang='ko', en='word#1', words=['말씀이']),
    dict(ref=(40, 4, 15), lang='ko', en='word#2', words=['말씀을#1']),
    dict(ref=(40, 4, 21), lang='ko', en='under#1', words=['아래나#2']),
    dict(ref=(40, 4, 21), lang='ko', en='under#2', words=['아래나#1']),
    dict(ref=(40, 6, 13), lang='ko', en='many#1', words=['많은#1']),
    dict(ref=(40, 6, 13), lang='ko', en='many#2', words=['많은#2']),
    dict(ref=(40, 12, 27), lang='ko', en='God#1', words=['하나님은']),
    dict(ref=(40, 12, 27), lang='ko', en='God#2', words=['하나님이']),
    dict(ref=(40, 13, 8), lang='ko', en='nation#1', words=['민족이']),
    dict(ref=(40, 13, 8), lang='ko', en='nation#2', words=['민족을']),
    dict(ref=(40, 13, 12), lang='ko', en='brother#1', words=['형제가']),
    dict(ref=(40, 13, 12), lang='ko', en='brother#2', words=['형제를']),
    dict(ref=(40, 14, 25), lang='ko', en='drink#1', words=['마시지']),
    dict(ref=(40, 14, 25), lang='ko', en='drink#2', words=['마시는']),
    dict(ref=(41, 6, 39), lang='ko', en='blind#1', words=['소경이']),
    dict(ref=(41, 6, 39), lang='ko', en='blind#2', words=['소경을']),
    dict(ref=(41, 10, 20), lang='ko', en='rejoice#1', words=['기뻐하지']),
    dict(ref=(41, 10, 20), lang='ko', en='rejoice#2', words=['기뻐하라']),
    dict(ref=(41, 11, 1), lang='ko', en='disciples#1', words=['제자들에게']),
    dict(ref=(41, 11, 1), lang='ko', en='disciples#2', words=['제자']),
    dict(ref=(41, 11, 15), lang='ko', en='devils#1', words=['귀신을']),
    dict(ref=(41, 11, 15), lang='ko', en='devils#2', words=['귀신의']),
    dict(ref=(41, 12, 53), lang='ko', en='son#1', words=['아들과']),
    dict(ref=(41, 12, 53), lang='ko', en='son#2', words=['아들이']),
    dict(ref=(41, 20, 42), lang='ko', en='Lord#1', words=['주께서']),
    dict(ref=(41, 20, 42), lang='ko', en='Lord#2', words=['주께']),
    dict(ref=(41, 21, 10), lang='ko', en='kingdom#1', words=['나라가']),
    dict(ref=(41, 21, 10), lang='ko', en='kingdom#2', words=['나라를']),
    dict(ref=(42, 5, 23), lang='ko', en='honour#1', words=['공경하게']),
    dict(ref=(42, 5, 23), lang='ko', en='honour#2', words=['공경하는']),
    dict(ref=(42, 5, 36), lang='ko', en='witness#1', words=['증거보다']),
    dict(ref=(42, 5, 36), lang='ko', en='witness#2', words=['증거가']),
    dict(ref=(42, 10, 11), lang='ko', en='shepherd#1', words=['목자라']),
    dict(ref=(42, 10, 11), lang='ko', en='shepherd#2', words=['목자는']),
    dict(ref=(42, 16, 28), lang='ko', en='world#1', words=['세상에']),
    dict(ref=(42, 16, 28), lang='ko', en='world#2', words=['세상을']),
    dict(ref=(42, 19, 26), lang='ko', en='mother#1', words=['모친과']),
    dict(ref=(42, 19, 26), lang='ko', en='mother#2', words=['모친께']),
    dict(ref=(44, 1, 21), lang='ko', en='God#1', words=['하나님을']),
    dict(ref=(44, 1, 21), lang='ko', en='God#2', words=['하나님으로']),
    dict(ref=(44, 2, 4), lang='ko', en='goodness#1', words=['인자하심과']),
    dict(ref=(44, 2, 4), lang='ko', en='goodness#2', words=['인자하심이']),
    dict(ref=(44, 6, 9), lang='ko', en='more#1', words=['다시#2']),
    dict(ref=(44, 6, 9), lang='ko', en='more#2', words=['다시#1']),
    dict(ref=(44, 9, 23), lang='ko', en='glory#1', words=['영광']),
    dict(ref=(44, 9, 23), lang='ko', en='glory#2', words=['영광의']),
    dict(ref=(45, 3, 8), lang='ko', en='own#1', words=['자기의#2']),
    dict(ref=(45, 3, 8), lang='ko', en='own#2', words=['자기의#1']),
    dict(ref=(45, 5, 8), lang='ko', en='leaven#1', words=['누룩도#1']),
    dict(ref=(45, 5, 8), lang='ko', en='leaven#2', words=['누룩']),
    dict(ref=(45, 6, 6), lang='ko', en='brother#1', words=['형제가']),
    dict(ref=(45, 6, 6), lang='ko', en='brother#2', words=['형제로']),
    dict(ref=(45, 7, 31), lang='ko', en='world#1', words=['세상']),
    dict(ref=(45, 7, 31), lang='ko', en='world#2', words=['세상의']),
    dict(ref=(45, 8, 5), lang='ko', en='many#1', words=['많은#1']),
    dict(ref=(45, 8, 5), lang='ko', en='many#2', words=['많은#2']),
    dict(ref=(45, 11, 4), lang='ko', en='head#1', words=['머리에']),
    dict(ref=(45, 11, 4), lang='ko', en='head#2', words=['머리를']),
    dict(ref=(45, 14, 25), lang='ko', en='God#1', words=['하나님께']),
    dict(ref=(45, 14, 25), lang='ko', en='God#2', words=['하나님이']),
    dict(ref=(46, 2, 16), lang='ko', en='savour#1', words=['냄새라']),
    dict(ref=(46, 2, 16), lang='ko', en='savour#2', words=['냄새요']),
    dict(ref=(46, 2, 16), lang='ko', en='death#1', words=['사망으로']),
    dict(ref=(46, 2, 16), lang='ko', en='death#2', words=['사망에']),
    dict(ref=(46, 3, 11), lang='ko', en='glorious#1', words=['영광으로']),
    dict(ref=(46, 3, 11), lang='ko', en='glorious#2', words=['영광']),
    dict(ref=(46, 10, 2), lang='ko', en='bold#1', words=['담대한']),
    dict(ref=(46, 10, 2), lang='ko', en='bold#2', words=['담대히']),
    dict(ref=(47, 3, 4), lang='ko', en='vain#1', words=['헛되이']),
    dict(ref=(47, 3, 4), lang='ko', en='vain#2', words=['헛되냐']),
    dict(ref=(47, 4, 7), lang='ko', en='son#1', words=['아들이면']),
    dict(ref=(47, 4, 7), lang='ko', en='son#2', words=['아들이니']),
    dict(ref=(47, 5, 26), lang='ko', en='another#1', words=['서로#1']),
    dict(ref=(47, 5, 26), lang='ko', en='another#2', words=['서로#2']),
    dict(ref=(48, 2, 13), lang='ko', en='Christ#1', words=['그리스도']),
    dict(ref=(48, 2, 13), lang='ko', en='Christ#2', words=['그리스도의']),
    dict(ref=(48, 4, 32), lang='ko', en='another#1', words=['서로#1']),
    dict(ref=(48, 4, 32), lang='ko', en='another#2', words=['서로#2']),
    dict(ref=(48, 5, 28), lang='ko', en='loveth#1', words=['사랑하기를']),
    dict(ref=(48, 5, 28), lang='ko', en='loveth#2', words=['사랑하는#1']),
    dict(ref=(49, 1, 27), lang='ko', en='gospel#1', words=['복음에']),
    dict(ref=(49, 1, 27), lang='ko', en='gospel#2', words=['복음의']),
    dict(ref=(49, 4, 1), lang='ko', en='beloved#1', words=['사랑하고']),
    dict(ref=(49, 4, 1), lang='ko', en='beloved#2', words=['사랑하는']),
    dict(ref=(50, 2, 20), lang='ko', en='world#1', words=['세상의']),
    dict(ref=(50, 2, 20), lang='ko', en='world#2', words=['세상에']),
    dict(ref=(51, 3, 9), lang='ko', en='God#1', words=['하나님께']),
    dict(ref=(51, 3, 9), lang='ko', en='God#2', words=['하나님']),
    dict(ref=(53, 2, 5), lang='ko', en='God#1', words=['하나님은']),
    dict(ref=(53, 2, 5), lang='ko', en='God#2', words=['하나님과']),
    dict(ref=(53, 5, 3), lang='ko', en='widows#1', words=['과부인']),
    dict(ref=(53, 5, 3), lang='ko', en='widows#2', words=['과부를']),
    dict(ref=(60, 1, 6), lang='ko', en='temperance#1', words=['절제를']),
    dict(ref=(60, 1, 6), lang='ko', en='temperance#2', words=['절제에']),
    dict(ref=(60, 1, 6), lang='ko', en='patience#1', words=['인내를']),
    dict(ref=(60, 1, 6), lang='ko', en='patience#2', words=['인내에']),
    dict(ref=(61, 3, 20), lang='ko', en='heart#1', words=['마음이']),
    dict(ref=(61, 3, 20), lang='ko', en='heart#2', words=['마음보다']),
    dict(ref=(61, 4, 8), lang='ko', en='God#1', words=['하나님을']),
    dict(ref=(61, 4, 8), lang='ko', en='God#2', words=['하나님은']),
    dict(ref=(61, 4, 10), lang='ko', en='loved#1', words=['사랑은']),
    dict(ref=(61, 4, 10), lang='ko', en='loved#2', words=['사랑한']),
    dict(ref=(62, 1, 3), lang='ko', en='Father#1', words=['아버지와']),
    dict(ref=(62, 1, 3), lang='ko', en='Father#2', words=['아버지의']),
    dict(ref=(65, 1, 12), lang='ko', en='turned#1', words=['돌이켜']),
    dict(ref=(65, 1, 12), lang='ko', en='turned#2', words=['돌이킬']),
    dict(ref=(65, 7, 16), lang='ko', en='neither#1', words=['아니하며']),
    dict(ref=(65, 7, 16), lang='ko', en='neither#2', words=['아니하고']),
    dict(ref=(65, 9, 3), lang='ko', en='power#1', words=['권세를']),
    dict(ref=(65, 9, 3), lang='ko', en='power#2', words=['권세와']),
    dict(ref=(65, 9, 8), lang='ko', en='hair#1', words=['머리털이']),
    dict(ref=(65, 9, 8), lang='ko', en='hair#2', words=['머리털']),
    dict(ref=(65, 12, 7), lang='ko', en='angels#1', words=['사자들이']),
    dict(ref=(65, 12, 7), lang='ko', en='angels#2', words=['사자들도']),
    dict(ref=(65, 13, 10), lang='ko', en='captivity#1', words=['사로잡는']),
    dict(ref=(65, 13, 10), lang='ko', en='captivity#2', words=['사로잡힐']),
    dict(ref=(65, 15, 7), lang='ko', en='seven#1', words=['일곱을']),
    dict(ref=(65, 15, 7), lang='ko', en='seven#2', words=['일곱']),

    # ---- 베드로전서 4:17 ----
    dict(ref=(59, 4, 17), lang='ko', en='the#1', words=['때가']),
    dict(ref=(59, 4, 17), lang='ko', en='time', words=['때가']),
    dict(ref=(59, 4, 17), lang='ko', en='come', words=['되었나니']),
    dict(ref=(59, 4, 17), lang='ko', en='must', words=['시작할']),
    dict(ref=(59, 4, 17), lang='ko', en='at#1', words=['집에서']),
    dict(ref=(59, 4, 17), lang='ko', en='of#1', words=['하나님']),
    dict(ref=(59, 4, 17), lang='ko', en='begin#2', words=['먼저']),
    dict(ref=(59, 4, 17), lang='ko', en='at#2', words=['우리에게']),
    dict(ref=(59, 4, 17), lang='ko', en='be', words=['어떠하며']),
    dict(ref=(59, 4, 17), lang='ko', en='of#3', words=['하나님의']),
    dict(ref=(59, 4, 17), lang='ko', en='God#2', words=['하나님의']),

    # ---- 요한일서 3:9 ----
    dict(ref=(61, 3, 9), lang='ko', en='Whosoever', words=['자마다']),
    dict(ref=(61, 3, 9), lang='ko', en='is#1', words=['난']),
    dict(ref=(61, 3, 9), lang='ko', en='born#1', words=['난']),
    dict(ref=(61, 3, 9), lang='ko', en='of#1', words=['하나님께로서#1']),
    dict(ref=(61, 3, 9), lang='ko', en='doth', words=['짓지']),
    dict(ref=(61, 3, 9), lang='ko', en='not', words=['아니하나니']),
    dict(ref=(61, 3, 9), lang='ko', en='commit', words=['짓지']),
    dict(ref=(61, 3, 9), lang='ko', en='his', words=['하나님의']),
    dict(ref=(61, 3, 9), lang='ko', en='remaineth', words=['거함이요']),
    dict(ref=(61, 3, 9), lang='ko', en='him', words=['그의']),
    dict(ref=(61, 3, 9), lang='ko', en='he#1', words=['저도']),
    dict(ref=(61, 3, 9), lang='ko', en='because', words=[]),
    dict(ref=(61, 3, 9), lang='ko', en='is#2', words=['났음이라']),
    dict(ref=(61, 3, 9), lang='ko', en='born#2', words=['났음이라']),
    dict(ref=(61, 3, 9), lang='ko', en='of#2', words=['하나님께로서#2']),
    dict(ref=(61, 3, 9), lang='ko', en='God#2', words=['하나님께로서#2']),

    # 벧전 4:17 비게 된 자리 채움 — them(그)은 건드리지 않고 it/that 으로 메움
    dict(ref=(59, 4, 17), lang='ko', en='it', words=['하면']),
    dict(ref=(59, 4, 17), lang='ko', en='that#2', words=['자들의']),

    # ---- 요한일서 3:24 ----  we / know 가 '아느니라' 한 자리에 겹쳐 있던 것을 끊음
    dict(ref=(61, 3, 24), lang='ko', en='we', words=['우리가']),
    dict(ref=(61, 3, 24), lang='ko', en='know', words=['아느니라']),

    # ---- 요한일서 3:24 ----  한 칸씩 밀려 있던 앞뒤를 바로잡음
    # dwelleth=거하고, abideth=거하시는 로 제자리에 돌리고 him/he/in/us 를 짝지음.
    # '거하시나니'(10)는 비워 둔다 — KJV 'and he in him' 이 동사를 줄여 버려서
    # 맞댈 영어 낱말이 없다. 빈 자리를 메우는 일괄 작업은 여기를 건드리지 말아야 한다.
    dict(ref=(61, 3, 24), lang='ko', en='his', words=['그의']),
    dict(ref=(61, 3, 24), lang='ko', en='dwelleth', words=['거하고']),
    dict(ref=(61, 3, 24), lang='ko', en='him#1', words=['주']),
    dict(ref=(61, 3, 24), lang='ko', en='he#2', words=['주는']),
    dict(ref=(61, 3, 24), lang='ko', en='in#2', words=['안에#2']),
    dict(ref=(61, 3, 24), lang='ko', en='him#2', words=['저']),
    dict(ref=(61, 3, 24), lang='ko', en='he#3', words=['그가']),
    dict(ref=(61, 3, 24), lang='ko', en='abideth', words=['거하시는']),
    dict(ref=(61, 3, 24), lang='ko', en='in#3', words=['안에#3']),
    dict(ref=(61, 3, 24), lang='ko', en='us#1', words=['우리']),
    dict(ref=(61, 3, 24), lang='ko', en='us#2', words=['우리에게']),

    # ---- 시편 38:12 ----  snares/lay 를 끊어 붙이고 뒷절반을 메움
    dict(ref=(18, 38, 12), lang='ko', en='snares', words=['올무를']),
    dict(ref=(18, 38, 12), lang='ko', en='lay', words=['놓고']),
    dict(ref=(18, 38, 12), lang='ko', en='that#2', words=['자가#2']),
    dict(ref=(18, 38, 12), lang='ko', en='mischievous', words=['괴악한']),
    dict(ref=(18, 38, 12), lang='ko', en='deceits', words=['궤계를']),
    dict(ref=(18, 38, 12), lang='ko', en='imagine', words=['도모하오나']),

    # ---- 되풀이되는 부정문: 영어 부정어를 제 한국어 부정 어미에 하나씩 붙임 ----
    # 'rebuke me not … neither chasten me' ↔ '책하지 마시고 … 징계치 마소서' 처럼
    # not/neither/nor 가 한국어 부정 어미 한 자리에 뭉쳐 있던 곳. 영어 부정어
    # 수와 한국어 부정 어미 수가 같은 절만 순서대로 짝지었다.
    # 열왕기상 1:11  not not / 못하였나이까 못하시나이다
    dict(ref=(10, 1, 11), lang='ko', en='not#1', words=['못하였나이까']),
    dict(ref=(10, 1, 11), lang='ko', en='not#2', words=['못하시나이다']),
    # 열왕기상 2:20  not not / 마소서 아니하리이다
    dict(ref=(10, 2, 20), lang='ko', en='not#1', words=['마소서']),
    dict(ref=(10, 2, 20), lang='ko', en='not#2', words=['아니하리이다']),
    # 열왕기상 3:11  not neither nor / 아니하며 아니하며 아니하고
    dict(ref=(10, 3, 11), lang='ko', en='not', words=['아니하며#1']),
    dict(ref=(10, 3, 11), lang='ko', en='neither', words=['아니하며#2']),
    dict(ref=(10, 3, 11), lang='ko', en='nor', words=['아니하고']),
    # 열왕기상 8:57  not nor / 마옵시며 마옵시고
    dict(ref=(10, 8, 57), lang='ko', en='not', words=['마옵시며']),
    dict(ref=(10, 8, 57), lang='ko', en='nor', words=['마옵시고']),
    # 열왕기상 10:7  not not / 아니하였더니 못되니
    # 열왕기상 11:2  not neither / 말며 말라
    dict(ref=(10, 11, 2), lang='ko', en='not', words=['말며']),
    dict(ref=(10, 11, 2), lang='ko', en='neither', words=['말라']),
    # 열왕기상 11:10  not not / 말라 않았으므로
    dict(ref=(10, 11, 10), lang='ko', en='not#1', words=['말라']),
    dict(ref=(10, 11, 10), lang='ko', en='not#2', words=['않았으므로']),
    # 열왕기상 13:28  not nor / 아니하였고 아니하였더라
    dict(ref=(10, 13, 28), lang='ko', en='not', words=['아니하였고']),
    dict(ref=(10, 13, 28), lang='ko', en='nor', words=['아니하였더라']),
    # 열왕기상 17:1  not nor / 없으면 아니하리라
    dict(ref=(10, 17, 1), lang='ko', en='not', words=['없으면']),
    dict(ref=(10, 17, 1), lang='ko', en='nor', words=['아니하리라']),
    # 열왕기상 19:11  not not / 아니하며 아니하며
    dict(ref=(10, 19, 11), lang='ko', en='not#1', words=['아니하며#1']),
    dict(ref=(10, 19, 11), lang='ko', en='not#2', words=['아니하며#2']),
    # 열왕기상 19:18  not not / 아니하고 아니한
    dict(ref=(10, 19, 18), lang='ko', en='not#1', words=['아니하고']),
    dict(ref=(10, 19, 18), lang='ko', en='not#2', words=['아니한']),
    # 열왕기상 20:8  not nor / 말고 마옵소서
    dict(ref=(10, 20, 8), lang='ko', en='not', words=['말고']),
    dict(ref=(10, 20, 8), lang='ko', en='nor', words=['마옵소서']),
    # 열왕기상 22:8  not not / 아니하고 마소서
    dict(ref=(10, 22, 8), lang='ko', en='not#1', words=['아니하고']),
    dict(ref=(10, 22, 8), lang='ko', en='not#2', words=['마소서']),
    # 열왕기상 22:43  not not / 아니하고 아니하였으므로
    dict(ref=(10, 22, 43), lang='ko', en='not#1', words=['아니하고']),
    dict(ref=(10, 22, 43), lang='ko', en='not#2', words=['아니하였으므로']),
    # 열왕기하 1:16  not not / 없음이냐 못할지라
    dict(ref=(11, 1, 16), lang='ko', en='not#1', words=['없음이냐']),
    dict(ref=(11, 1, 16), lang='ko', en='not#2', words=['못할지라']),
    # 열왕기하 2:10  not not / 않으면 아니하리라
    dict(ref=(11, 2, 10), lang='ko', en='not#1', words=['않으면']),
    dict(ref=(11, 2, 10), lang='ko', en='not#2', words=['아니하리라']),
    # 열왕기하 2:18  not not / 말라고 아니하였느냐
    dict(ref=(11, 2, 18), lang='ko', en='not#1', words=['말라고']),
    dict(ref=(11, 2, 18), lang='ko', en='not#2', words=['아니하였느냐']),
    # 열왕기하 3:14  not not nor / 아니면 아니하고 아니하였으리이다
    dict(ref=(11, 3, 14), lang='ko', en='not#1', words=['아니면']),
    dict(ref=(11, 3, 14), lang='ko', en='not#2', words=['아니하고']),
    dict(ref=(11, 3, 14), lang='ko', en='nor', words=['아니하였으리이다']),
    # 열왕기하 4:23  neither nor / 아니요 아니어늘
    dict(ref=(11, 4, 23), lang='ko', en='neither', words=['아니요']),
    dict(ref=(11, 4, 23), lang='ko', en='nor', words=['아니어늘']),
    # 열왕기하 4:28  not not / 말라고 아니하더이까
    dict(ref=(11, 4, 28), lang='ko', en='not#1', words=['말라고']),
    dict(ref=(11, 4, 28), lang='ko', en='not#2', words=['아니하더이까']),
    # 열왕기하 4:29  not not / 말며 말고
    dict(ref=(11, 4, 29), lang='ko', en='not#1', words=['말며']),
    dict(ref=(11, 4, 29), lang='ko', en='not#2', words=['말고']),
    # 열왕기하 5:12  not not / 아니하냐 아니하랴
    dict(ref=(11, 5, 12), lang='ko', en='not#1', words=['아니하냐']),
    dict(ref=(11, 5, 12), lang='ko', en='not#2', words=['아니하랴']),
    # 열왕기하 6:19  not neither / 아니요 아니니
    dict(ref=(11, 6, 19), lang='ko', en='not', words=['아니요']),
    dict(ref=(11, 6, 19), lang='ko', en='neither', words=['아니니']),
    # 열왕기하 13:23  not neither / 아니하시고 아니하셨더라
    dict(ref=(11, 13, 23), lang='ko', en='not', words=['아니하시고']),
    dict(ref=(11, 13, 23), lang='ko', en='neither', words=['아니하셨더라']),
    # 열왕기하 17:14  not not / 아니하고 아니하던
    dict(ref=(11, 17, 14), lang='ko', en='not#1', words=['아니하고']),
    dict(ref=(11, 17, 14), lang='ko', en='not#2', words=['아니하던']),
    # 열왕기하 17:26  not not / 못하므로 못함이니이다
    dict(ref=(11, 17, 26), lang='ko', en='not#1', words=['못하므로']),
    dict(ref=(11, 17, 26), lang='ko', en='not#2', words=['못함이니이다']),
    # 열왕기하 17:34  not neither / 아니하며 아니하는도다
    dict(ref=(11, 17, 34), lang='ko', en='not', words=['아니하며']),
    dict(ref=(11, 17, 34), lang='ko', en='neither', words=['아니하는도다']),
    # 열왕기하 17:35  not nor nor nor / 말며 말며 말며 말고
    dict(ref=(11, 17, 35), lang='ko', en='not', words=['말며#1']),
    dict(ref=(11, 17, 35), lang='ko', en='nor#1', words=['말며#2']),
    dict(ref=(11, 17, 35), lang='ko', en='nor#2', words=['말며#3']),
    dict(ref=(11, 17, 35), lang='ko', en='nor#3', words=['말고']),
    # 열왕기하 17:38  not neither / 말며 말고
    dict(ref=(11, 17, 38), lang='ko', en='not', words=['말며']),
    dict(ref=(11, 17, 38), lang='ko', en='neither', words=['말고']),
    # 열왕기하 18:12  not not nor / 아니하고 아니하며 아니하였음이더라
    dict(ref=(11, 18, 12), lang='ko', en='not#1', words=['아니하고']),
    dict(ref=(11, 18, 12), lang='ko', en='not#2', words=['아니하며']),
    dict(ref=(11, 18, 12), lang='ko', en='nor', words=['아니하였음이더라']),
    # 열왕기하 18:29  not not / 말라 못하리라
    dict(ref=(11, 18, 29), lang='ko', en='not#1', words=['말라']),
    dict(ref=(11, 18, 29), lang='ko', en='not#2', words=['못하리라']),
    # 열왕기하 18:30  Neither not / 말라 않게
    dict(ref=(11, 18, 30), lang='ko', en='Neither', words=['말라']),
    dict(ref=(11, 18, 30), lang='ko', en='not', words=['않게']),
    # 열왕기하 18:32  not not / 아니하리라 말라
    dict(ref=(11, 18, 32), lang='ko', en='not#1', words=['아니하리라']),
    dict(ref=(11, 18, 32), lang='ko', en='not#2', words=['말라']),
    # 열왕기하 18:36  not not / 아니하니 말라
    dict(ref=(11, 18, 36), lang='ko', en='not#1', words=['아니하니']),
    dict(ref=(11, 18, 36), lang='ko', en='not#2', words=['말라']),
    # 열왕기하 19:32  not nor nor nor / 못하며 못하며 못하며 못하고
    dict(ref=(11, 19, 32), lang='ko', en='not', words=['못하며#1']),
    dict(ref=(11, 19, 32), lang='ko', en='nor#1', words=['못하며#2']),
    dict(ref=(11, 19, 32), lang='ko', en='nor#2', words=['못하며#3']),
    dict(ref=(11, 19, 32), lang='ko', en='nor#3', words=['못하고']),
    # 열왕기하 20:13  nor not / 아니한 없으니라
    dict(ref=(11, 20, 13), lang='ko', en='nor', words=['아니한']),
    dict(ref=(11, 20, 13), lang='ko', en='not', words=['없으니라']),
    # 역대상 4:27  not neither / 못되니 못하였더라
    dict(ref=(12, 4, 27), lang='ko', en='not', words=['못되니']),
    dict(ref=(12, 4, 27), lang='ko', en='neither', words=['못하였더라']),
    # 역대상 15:13  not not / 아니하였으므로 아니하였음이니라
    dict(ref=(12, 15, 13), lang='ko', en='not#1', words=['아니하였으므로']),
    dict(ref=(12, 15, 13), lang='ko', en='not#2', words=['아니하였음이니라']),
    # 역대상 21:17  not not / 아니니이까 마옵소서
    dict(ref=(12, 21, 17), lang='ko', en='not#1', words=['아니니이까']),
    dict(ref=(12, 21, 17), lang='ko', en='not#2', words=['마옵소서']),
    # 역대상 22:13  not nor / 말고 말지어다
    dict(ref=(12, 22, 13), lang='ko', en='not', words=['말고']),
    dict(ref=(12, 22, 13), lang='ko', en='nor', words=['말지어다']),
    # 역대상 22:18  not not / 아니하시느냐 아니하셨느냐
    dict(ref=(12, 22, 18), lang='ko', en='not#1', words=['아니하시느냐']),
    dict(ref=(12, 22, 18), lang='ko', en='not#2', words=['아니하셨느냐']),
    # 역대상 27:24  not neither / 못하여서 아니하였더라
    dict(ref=(12, 27, 24), lang='ko', en='not', words=['못하여서']),
    dict(ref=(12, 27, 24), lang='ko', en='neither', words=['아니하였더라']),
    # 역대상 28:20  not nor not nor / 말며 말라 아니하시고 아니하시리라
    dict(ref=(12, 28, 20), lang='ko', en='not#1', words=['말며']),
    dict(ref=(12, 28, 20), lang='ko', en='nor#1', words=['말라']),
    dict(ref=(12, 28, 20), lang='ko', en='not#2', words=['아니하시고']),
    dict(ref=(12, 28, 20), lang='ko', en='nor#2', words=['아니하시리라']),
    # 역대하 9:6  not not / 아니하였더니 못되니
    dict(ref=(13, 9, 6), lang='ko', en='not#1', words=['아니하였더니']),
    dict(ref=(13, 9, 6), lang='ko', en='not#2', words=['못되니']),
    # 역대하 12:7  not not / 아니하고 아니하리라
    dict(ref=(13, 12, 7), lang='ko', en='not#1', words=['아니하고']),
    dict(ref=(13, 12, 7), lang='ko', en='not#2', words=['아니하리라']),
    # 역대하 18:7  never not / 아니하고 마소서
    dict(ref=(13, 18, 7), lang='ko', en='never', words=['아니하고']),
    dict(ref=(13, 18, 7), lang='ko', en='not', words=['마소서']),
    # 역대하 18:17  not not / 아니하고 아니하였나이까
    dict(ref=(13, 18, 17), lang='ko', en='not#1', words=['아니하고']),
    dict(ref=(13, 18, 17), lang='ko', en='not#2', words=['아니하였나이까']),
    # 역대하 19:10  not not / 않게 없으리라
    dict(ref=(13, 19, 10), lang='ko', en='not#1', words=['않게']),
    dict(ref=(13, 19, 10), lang='ko', en='not#2', words=['없으리라']),
    # 역대하 20:6  not not not / 아니시니이까 아니하시나이까 없나이다
    dict(ref=(13, 20, 6), lang='ko', en='not#1', words=['아니시니이까']),
    dict(ref=(13, 20, 6), lang='ko', en='not#2', words=['아니하시나이까']),
    dict(ref=(13, 20, 6), lang='ko', en='not#3', words=['없나이다']),
    # 역대하 20:10  not not / 아니하시므로 아니하였거늘
    dict(ref=(13, 20, 10), lang='ko', en='not#1', words=['아니하시므로']),
    dict(ref=(13, 20, 10), lang='ko', en='not#2', words=['아니하였거늘']),
    # 역대하 20:12  not neither / 아니하시나이까 못하옵고
    dict(ref=(13, 20, 12), lang='ko', en='not', words=['아니하시나이까']),
    dict(ref=(13, 20, 12), lang='ko', en='neither', words=['못하옵고']),
    # 역대하 20:33  not not / 아니하였으므로 아니하였더라
    dict(ref=(13, 20, 33), lang='ko', en='not#1', words=['아니하였으므로']),
    dict(ref=(13, 20, 33), lang='ko', en='not#2', words=['아니하였더라']),
    # 역대하 25:7  not not / 마옵소서 아니하시나니
    dict(ref=(13, 25, 7), lang='ko', en='not#1', words=['마옵소서']),
    dict(ref=(13, 25, 7), lang='ko', en='not#2', words=['아니하시나니']),
    # 역대하 26:18  not neither / 아니요 못하리이다
    dict(ref=(13, 26, 18), lang='ko', en='not', words=['아니요']),
    dict(ref=(13, 26, 18), lang='ko', en='neither', words=['못하리이다']),
    # 역대하 29:7  not nor / 아니하며 아니한고로
    dict(ref=(13, 29, 7), lang='ko', en='not', words=['아니하며']),
    dict(ref=(13, 29, 7), lang='ko', en='nor', words=['아니한고로']),
    # 역대하 32:17  not not / 못한 못하리라
    dict(ref=(13, 32, 17), lang='ko', en='not#1', words=['못한']),
    dict(ref=(13, 32, 17), lang='ko', en='not#2', words=['못하리라']),
    # 역대하 35:21  not not / 아니요 말라
    dict(ref=(13, 35, 21), lang='ko', en='not#1', words=['아니요']),
    dict(ref=(13, 35, 21), lang='ko', en='not#2', words=['말라']),
    # 에스라 9:12  not neither nor / 말고 말며 말라
    dict(ref=(14, 9, 12), lang='ko', en='not', words=['말고']),
    dict(ref=(14, 9, 12), lang='ko', en='neither', words=['말며']),
    dict(ref=(14, 9, 12), lang='ko', en='nor', words=['말라']),
    # 에스라 10:13  not neither / 못할 아니오니
    dict(ref=(14, 10, 13), lang='ko', en='not', words=['못할']),
    dict(ref=(14, 10, 13), lang='ko', en='neither', words=['아니오니']),
    # 느헤미야 4:5  not not / 마옵시며 마옵소서
    dict(ref=(15, 4, 5), lang='ko', en='not#1', words=['마옵시며']),
    dict(ref=(15, 4, 5), lang='ko', en='not#2', words=['마옵소서']),
    # 느헤미야 4:11  not neither / 못하고 못하는
    dict(ref=(15, 4, 11), lang='ko', en='not', words=['못하고']),
    dict(ref=(15, 4, 11), lang='ko', en='neither', words=['못하는']),
    # 느헤미야 5:9  not not / 못하도다 아니냐
    dict(ref=(15, 5, 9), lang='ko', en='not#1', words=['못하도다']),
    dict(ref=(15, 5, 9), lang='ko', en='not#2', words=['아니냐']),
    # 느헤미야 8:9  not nor / 말며 말라
    dict(ref=(15, 8, 9), lang='ko', en='not', words=['말며']),
    dict(ref=(15, 8, 9), lang='ko', en='nor', words=['말라']),
    # 느헤미야 9:17  neither not / 아니하고 아니하셨나이다
    dict(ref=(15, 9, 17), lang='ko', en='neither', words=['아니하고']),
    dict(ref=(15, 9, 17), lang='ko', en='not', words=['아니하셨나이다']),
    # 느헤미야 9:21  not not / 아니하였고 아니하였사오며
    dict(ref=(15, 9, 21), lang='ko', en='not#1', words=['아니하였고']),
    dict(ref=(15, 9, 21), lang='ko', en='not#2', words=['아니하였사오며']),
    # 느헤미야 9:29  not not / 아니하며 아니하였나이다
    dict(ref=(15, 9, 29), lang='ko', en='not#1', words=['아니하며']),
    dict(ref=(15, 9, 29), lang='ko', en='not#2', words=['아니하였나이다']),
    # 느헤미야 9:31  not nor / 아니하시며 아니하셨사오니
    dict(ref=(15, 9, 31), lang='ko', en='not', words=['아니하시며']),
    dict(ref=(15, 9, 31), lang='ko', en='nor', words=['아니하셨사오니']),
    # 느헤미야 9:35  not neither / 아니하며 아니한고로
    dict(ref=(15, 9, 35), lang='ko', en='not', words=['아니하며']),
    dict(ref=(15, 9, 35), lang='ko', en='neither', words=['아니한고로']),
    # 느헤미야 10:30  not nor / 아니하고 아니하며
    dict(ref=(15, 10, 30), lang='ko', en='not', words=['아니하고']),
    dict(ref=(15, 10, 30), lang='ko', en='nor', words=['아니하며']),
    # 느헤미야 13:18  not not / 아니하였느냐 아니냐
    dict(ref=(15, 13, 18), lang='ko', en='not#1', words=['아니하였느냐']),
    dict(ref=(15, 13, 18), lang='ko', en='not#2', words=['아니냐']),
    # 느헤미야 13:25  not nor / 말고 않겠다고
    dict(ref=(15, 13, 25), lang='ko', en='not', words=['말고']),
    dict(ref=(15, 13, 25), lang='ko', en='nor', words=['않겠다고']),
    # 에스더 3:5  not nor / 아니하고 아니함을
    dict(ref=(16, 3, 5), lang='ko', en='not', words=['아니하고']),
    dict(ref=(16, 3, 5), lang='ko', en='nor', words=['아니함을']),
    # 에스더 4:11  not not / 아니하고 못한지가
    dict(ref=(16, 4, 11), lang='ko', en='not#1', words=['아니하고']),
    dict(ref=(16, 4, 11), lang='ko', en='not#2', words=['못한지가']),
    # 에스더 4:16  neither nor not / 말고 마시지도 마소서
    # 에스더 9:28  not nor / 않게 않게
    dict(ref=(16, 9, 28), lang='ko', en='not', words=['않게#1']),
    dict(ref=(16, 9, 28), lang='ko', en='nor', words=['않게#2']),
    # 욥기 1:22  not nor / 아니하고 아니하니라
    dict(ref=(17, 1, 22), lang='ko', en='not', words=['아니하고']),
    dict(ref=(17, 1, 22), lang='ko', en='nor', words=['아니하니라']),
    # 욥기 2:10  not not / 아니하겠느뇨 아니하니라
    dict(ref=(17, 2, 10), lang='ko', en='not#1', words=['아니하겠느뇨']),
    dict(ref=(17, 2, 10), lang='ko', en='not#2', words=['아니하니라']),
    # 욥기 3:11  not not / 아니하였었던가 아니하였던가
    dict(ref=(17, 3, 11), lang='ko', en='not#1', words=['아니하였었던가']),
    dict(ref=(17, 3, 11), lang='ko', en='not#2', words=['아니하였던가']),
    # 욥기 3:16  not never / 않았겠고 못한
    dict(ref=(17, 3, 16), lang='ko', en='not', words=['않았겠고']),
    dict(ref=(17, 3, 16), lang='ko', en='never', words=['못한']),
    # 욥기 5:6  not neither / 아니요 아니라
    dict(ref=(17, 5, 6), lang='ko', en='not', words=['아니요']),
    dict(ref=(17, 5, 6), lang='ko', en='neither', words=['아니라']),
    # 욥기 7:1  not not / 아니하냐 아니하냐
    dict(ref=(17, 7, 1), lang='ko', en='not#1', words=['아니하냐#1']),
    dict(ref=(17, 7, 1), lang='ko', en='not#2', words=['아니하냐#2']),
    # 욥기 7:19  not nor / 아니하시며 아니하시기를
    dict(ref=(17, 7, 19), lang='ko', en='not', words=['아니하시며']),
    dict(ref=(17, 7, 19), lang='ko', en='nor', words=['아니하시기를']),
    # 욥기 8:15  not not / 못하고 못하리라
    dict(ref=(17, 8, 15), lang='ko', en='not#1', words=['못하고']),
    dict(ref=(17, 8, 15), lang='ko', en='not#2', words=['못하리라']),
    # 욥기 8:20  not neither / 아니하시고 아니하신즉
    dict(ref=(17, 8, 20), lang='ko', en='not', words=['아니하시고']),
    dict(ref=(17, 8, 20), lang='ko', en='neither', words=['아니하신즉']),
    # 욥기 9:11  not not / 못하며 못하느니라
    dict(ref=(17, 9, 11), lang='ko', en='not#1', words=['못하며']),
    dict(ref=(17, 9, 11), lang='ko', en='not#2', words=['못하느니라']),
    # 욥기 13:20  not not / 마옵소서 아니하오리니
    dict(ref=(17, 13, 20), lang='ko', en='not#1', words=['마옵소서']),
    dict(ref=(17, 13, 20), lang='ko', en='not#2', words=['아니하오리니']),
    # 욥기 14:21  not not / 못하며 못하나이다
    dict(ref=(17, 14, 21), lang='ko', en='not#1', words=['못하며']),
    dict(ref=(17, 14, 21), lang='ko', en='not#2', words=['못하나이다']),
    # 욥기 15:29  not neither neither / 못하고 못하며 못할
    dict(ref=(17, 15, 29), lang='ko', en='not', words=['못하고']),
    dict(ref=(17, 15, 29), lang='ko', en='neither#1', words=['못하며']),
    dict(ref=(17, 15, 29), lang='ko', en='neither#2', words=['못할']),
    # 욥기 20:18  not not / 못할 못하리니
    dict(ref=(17, 20, 18), lang='ko', en='not#1', words=['못할']),
    dict(ref=(17, 20, 18), lang='ko', en='not#2', words=['못하리니']),
    # 욥기 20:20  not not / 못하니 못하겠고
    dict(ref=(17, 20, 20), lang='ko', en='not#1', words=['못하니']),
    dict(ref=(17, 20, 20), lang='ko', en='not#2', words=['못하겠고']),
    # 욥기 21:29  not not / 아니하였느냐 못하느냐
    dict(ref=(17, 21, 29), lang='ko', en='not#1', words=['아니하였느냐']),
    dict(ref=(17, 21, 29), lang='ko', en='not#2', words=['못하느냐']),
    # 욥기 23:8  not cannot / 아니 아니하며
    dict(ref=(17, 23, 8), lang='ko', en='not', words=['아니']),
    dict(ref=(17, 23, 8), lang='ko', en='cannot', words=['아니하며']),
    # 욥기 23:17  not neither / 아니하셨고 아니하셨음이니라
    dict(ref=(17, 23, 17), lang='ko', en='not', words=['아니하셨고']),
    dict(ref=(17, 23, 17), lang='ko', en='neither', words=['아니하셨음이니라']),
    # 욥기 24:1  not not / 아니하셨는고 못하는고
    dict(ref=(17, 24, 1), lang='ko', en='not#1', words=['아니하셨는고']),
    dict(ref=(17, 24, 1), lang='ko', en='not#2', words=['못하는고']),
    # 욥기 24:13  not nor / 못하며 아니하는
    dict(ref=(17, 24, 13), lang='ko', en='not', words=['못하며']),
    dict(ref=(17, 24, 13), lang='ko', en='nor', words=['아니하는']),
    # 욥기 25:5  not not / 못하고 못하거든
    dict(ref=(17, 25, 5), lang='ko', en='not#1', words=['못하고']),
    dict(ref=(17, 25, 5), lang='ko', en='not#2', words=['못하거든']),
    # 욥기 27:4  not nor / 아니하며 아니하리라
    dict(ref=(17, 27, 4), lang='ko', en='not', words=['아니하며']),
    dict(ref=(17, 27, 4), lang='ko', en='nor', words=['아니하리라']),
    # 욥기 27:6  not not / 아니하리니 아니하리라
    dict(ref=(17, 27, 6), lang='ko', en='not#1', words=['아니하리니']),
    dict(ref=(17, 27, 6), lang='ko', en='not#2', words=['아니하리라']),
    # 욥기 27:19  not not / 못할 없어졌으리라
    dict(ref=(17, 27, 19), lang='ko', en='not#1', words=['못할']),
    dict(ref=(17, 27, 19), lang='ko', en='not#2', words=['없어졌으리라']),
    # 욥기 28:8  not nor / 못하였고 못하였느니라
    dict(ref=(17, 28, 8), lang='ko', en='not', words=['못하였고']),
    dict(ref=(17, 28, 8), lang='ko', en='nor', words=['못하였느니라']),
    # 욥기 28:14  not not / 아니하다 아니하다
    dict(ref=(17, 28, 14), lang='ko', en='not#1', words=['아니하다#1']),
    dict(ref=(17, 28, 14), lang='ko', en='not#2', words=['아니하다#2']),
    # 욥기 30:25  not not / 아니하였는가 아니하였는가
    dict(ref=(17, 30, 25), lang='ko', en='not#1', words=['아니하였는가#1']),
    dict(ref=(17, 30, 25), lang='ko', en='not#2', words=['아니하였는가#2']),
    # 욥기 31:15  not not / 아니하셨느냐 아니시냐
    dict(ref=(17, 31, 15), lang='ko', en='not#1', words=['아니하셨느냐']),
    dict(ref=(17, 31, 15), lang='ko', en='not#2', words=['아니시냐']),
    # 욥기 31:31  not cannot / 않은 아니하였었는가
    dict(ref=(17, 31, 31), lang='ko', en='not', words=['않은']),
    dict(ref=(17, 31, 31), lang='ko', en='cannot', words=['아니하였었는가']),
    # 욥기 32:9  not neither / 아니요 아니라
    dict(ref=(17, 32, 9), lang='ko', en='not', words=['아니요']),
    dict(ref=(17, 32, 9), lang='ko', en='neither', words=['아니라']),
    # 욥기 32:14  not neither / 아니하였으니 아니하리라
    dict(ref=(17, 32, 14), lang='ko', en='not', words=['아니하였으니']),
    dict(ref=(17, 32, 14), lang='ko', en='neither', words=['아니하리라']),
    # 욥기 32:21  not neither / 아니하며 아니하나니
    dict(ref=(17, 32, 21), lang='ko', en='not', words=['아니하며']),
    dict(ref=(17, 32, 21), lang='ko', en='neither', words=['아니하나니']),
    # 욥기 33:7  not neither / 못하고 못하느니라
    dict(ref=(17, 33, 7), lang='ko', en='not', words=['못하고']),
    dict(ref=(17, 33, 7), lang='ko', en='neither', words=['못하느니라']),
    # 욥기 33:21  cannot not / 아니하고 않던
    dict(ref=(17, 33, 21), lang='ko', en='cannot', words=['아니하고']),
    dict(ref=(17, 33, 21), lang='ko', en='not', words=['않던']),
    # 욥기 34:12  not neither / 아니하시며 아니하시느니라
    dict(ref=(17, 34, 12), lang='ko', en='not', words=['아니하시며']),
    dict(ref=(17, 34, 12), lang='ko', en='neither', words=['아니하시느니라']),
    # 욥기 34:19  not nor / 아니하시며 아니하시나니
    dict(ref=(17, 34, 19), lang='ko', en='not', words=['아니하시며']),
    dict(ref=(17, 34, 19), lang='ko', en='nor', words=['아니하시나니']),
    # 욥기 35:15  not not / 아니하셨고 아니하셨으므로
    dict(ref=(17, 35, 15), lang='ko', en='not#1', words=['아니하셨고']),
    dict(ref=(17, 35, 15), lang='ko', en='not#2', words=['아니하셨으므로']),
    # 욥기 37:23  cannot not / 없나니 아니
    dict(ref=(17, 37, 23), lang='ko', en='cannot', words=['없나니']),
    dict(ref=(17, 37, 23), lang='ko', en='not', words=['아니']),
    # 욥기 39:22  not neither / 아니하며 아니하니
    dict(ref=(17, 39, 22), lang='ko', en='not', words=['아니하며']),
    dict(ref=(17, 39, 22), lang='ko', en='neither', words=['아니하니']),
    # 시편 1:1  not nor nor / 아니하며 아니하며 아니하고
    dict(ref=(18, 1, 1), lang='ko', en='not', words=['아니하며#1']),
    dict(ref=(18, 1, 1), lang='ko', en='nor#1', words=['아니하며#2']),
    dict(ref=(18, 1, 1), lang='ko', en='nor#2', words=['아니하고']),
    # 시편 1:5  not nor / 못하며 못하리로다
    dict(ref=(18, 1, 5), lang='ko', en='not', words=['못하며']),
    dict(ref=(18, 1, 5), lang='ko', en='nor', words=['못하리로다']),
    # 시편 5:4  not neither / 아니시니 못하며
    dict(ref=(18, 5, 4), lang='ko', en='not', words=['아니시니']),
    dict(ref=(18, 5, 4), lang='ko', en='neither', words=['못하며']),
    # 시편 6:1  not neither / 마옵시며 마옵소서
    dict(ref=(18, 6, 1), lang='ko', en='not', words=['마옵시며']),
    dict(ref=(18, 6, 1), lang='ko', en='neither', words=['마옵소서']),
    # 시편 9:18  not not / 아니함이여 아니하리로다
    dict(ref=(18, 9, 18), lang='ko', en='not#1', words=['아니함이여']),
    dict(ref=(18, 9, 18), lang='ko', en='not#2', words=['아니하리로다']),
    # 시편 10:6  not never / 아니하며 아니하리라
    dict(ref=(18, 10, 6), lang='ko', en='not', words=['아니하며']),
    dict(ref=(18, 10, 6), lang='ko', en='never', words=['아니하리라']),
    # 시편 15:3  not nor nor / 아니하고 아니하며 아니하며
    dict(ref=(18, 15, 3), lang='ko', en='not', words=['아니하고']),
    dict(ref=(18, 15, 3), lang='ko', en='nor#1', words=['아니하며#1']),
    dict(ref=(18, 15, 3), lang='ko', en='nor#2', words=['아니하며#2']),
    # 시편 15:5  not nor never / 아니하며 아니하는 아니하리이다
    dict(ref=(18, 15, 5), lang='ko', en='not', words=['아니하며']),
    dict(ref=(18, 15, 5), lang='ko', en='nor', words=['아니하는']),
    dict(ref=(18, 15, 5), lang='ko', en='never', words=['아니하리이다']),
    # 시편 16:4  not nor / 아니하며 아니하리로다
    dict(ref=(18, 16, 4), lang='ko', en='not', words=['아니하며']),
    dict(ref=(18, 16, 4), lang='ko', en='nor', words=['아니하리로다']),
    # 시편 16:10  not neither / 아니하시며 않게
    dict(ref=(18, 16, 10), lang='ko', en='not', words=['아니하시며']),
    dict(ref=(18, 16, 10), lang='ko', en='neither', words=['않게']),
    # 시편 22:2  not not / 아니하오나 아니하시나이다
    dict(ref=(18, 22, 2), lang='ko', en='not#1', words=['아니하오나']),
    dict(ref=(18, 22, 2), lang='ko', en='not#2', words=['아니하시나이다']),
    # 시편 25:2  not not / 않게 못하게
    dict(ref=(18, 25, 2), lang='ko', en='not#1', words=['않게']),
    dict(ref=(18, 25, 2), lang='ko', en='not#2', words=['못하게']),
    # 시편 26:4  not neither / 아니하였사오니 아니하리이다
    dict(ref=(18, 26, 4), lang='ko', en='not', words=['아니하였사오니']),
    dict(ref=(18, 26, 4), lang='ko', en='neither', words=['아니하리이다']),
    # 시편 27:9  not not not neither / 마시고 마소서 말고 마옵소서
    dict(ref=(18, 27, 9), lang='ko', en='not#1', words=['마시고']),
    dict(ref=(18, 27, 9), lang='ko', en='not#2', words=['마소서']),
    dict(ref=(18, 27, 9), lang='ko', en='not#3', words=['말고']),
    dict(ref=(18, 27, 9), lang='ko', en='neither', words=['마옵소서']),
    # 시편 35:15  not not / 못하는 아니하도다
    dict(ref=(18, 35, 15), lang='ko', en='not#1', words=['못하는']),
    dict(ref=(18, 35, 15), lang='ko', en='not#2', words=['아니하도다']),
    # 시편 35:19  not neither / 못하게 못하게
    dict(ref=(18, 35, 19), lang='ko', en='not', words=['못하게#1']),
    dict(ref=(18, 35, 19), lang='ko', en='neither', words=['못하게#2']),
    # 시편 35:22  not not / 마옵소서 마옵소서
    dict(ref=(18, 35, 22), lang='ko', en='not#1', words=['마옵소서#1']),
    dict(ref=(18, 35, 22), lang='ko', en='not#2', words=['마옵소서#2']),
    # 시편 35:25  not not / 못하게 못하게
    dict(ref=(18, 35, 25), lang='ko', en='not#1', words=['못하게#1']),
    dict(ref=(18, 35, 25), lang='ko', en='not#2', words=['못하게#2']),
    # 시편 36:11  not not / 못하게 못하게
    dict(ref=(18, 36, 11), lang='ko', en='not#1', words=['못하게#1']),
    dict(ref=(18, 36, 11), lang='ko', en='not#2', words=['못하게#2']),
    # 시편 37:1  not neither / 말며 말지어다
    dict(ref=(18, 37, 1), lang='ko', en='not', words=['말며']),
    dict(ref=(18, 37, 1), lang='ko', en='neither', words=['말지어다']),
    # 시편 37:10  not not / 없어지리니 없으리로다
    dict(ref=(18, 37, 10), lang='ko', en='not#1', words=['없어지리니']),
    dict(ref=(18, 37, 10), lang='ko', en='not#2', words=['없으리로다']),
    # 시편 37:33  not nor / 아니하시고 아니하시리로다
    dict(ref=(18, 37, 33), lang='ko', en='not', words=['아니하시고']),
    dict(ref=(18, 37, 33), lang='ko', en='nor', words=['아니하시리로다']),
    # 시편 37:36  not not / 없어졌으니 못하였도다
    dict(ref=(18, 37, 36), lang='ko', en='not#1', words=['없어졌으니']),
    dict(ref=(18, 37, 36), lang='ko', en='not#2', words=['못하였도다']),
    # 시편 38:1  not neither / 마시고 마소서
    dict(ref=(18, 38, 1), lang='ko', en='not', words=['마시고']),
    dict(ref=(18, 38, 1), lang='ko', en='neither', words=['마소서']),
    # 시편 38:13  not not / 아니하고 아니하오니
    dict(ref=(18, 38, 13), lang='ko', en='not#1', words=['아니하고']),
    dict(ref=(18, 38, 13), lang='ko', en='not#2', words=['아니하오니']),
    # 시편 38:21  not not / 마소서 마소서
    dict(ref=(18, 38, 21), lang='ko', en='not#1', words=['마소서#1']),
    dict(ref=(18, 38, 21), lang='ko', en='not#2', words=['마소서#2']),
    # 시편 40:6  not not / 아니하시며 아니하신다
    dict(ref=(18, 40, 6), lang='ko', en='not#1', words=['아니하시며']),
    dict(ref=(18, 40, 6), lang='ko', en='not#2', words=['아니하신다']),
    # 시편 40:10  not not / 아니하고 아니하였나이다
    dict(ref=(18, 40, 10), lang='ko', en='not#1', words=['아니하고']),
    dict(ref=(18, 40, 10), lang='ko', en='not#2', words=['아니하였나이다']),
    # 시편 44:3  not neither / 아니요 아니라
    dict(ref=(18, 44, 3), lang='ko', en='not', words=['아니요']),
    dict(ref=(18, 44, 3), lang='ko', en='neither', words=['아니라']),
    # 시편 44:6  not neither / 아니할 못하리이다
    dict(ref=(18, 44, 6), lang='ko', en='not', words=['아니할']),
    dict(ref=(18, 44, 6), lang='ko', en='neither', words=['못하리이다']),
    # 시편 44:17  not neither / 아니하며 아니하였나이다
    dict(ref=(18, 44, 17), lang='ko', en='not', words=['아니하며']),
    dict(ref=(18, 44, 17), lang='ko', en='neither', words=['아니하였나이다']),
    # 시편 44:18  not neither / 아니하고 아니하였으나
    dict(ref=(18, 44, 18), lang='ko', en='not', words=['아니하고']),
    dict(ref=(18, 44, 18), lang='ko', en='neither', words=['아니하였으나']),
    # 시편 51:11  not not / 마시며 마소서
    dict(ref=(18, 51, 11), lang='ko', en='not#1', words=['마시며']),
    dict(ref=(18, 51, 11), lang='ko', en='not#2', words=['마소서']),
    # 시편 55:12  not neither / 아니라 아니라
    dict(ref=(18, 55, 12), lang='ko', en='not', words=['아니라#1']),
    dict(ref=(18, 55, 12), lang='ko', en='neither', words=['아니라#2']),
    # 시편 59:3  not nor / 아니요 아니로소이다
    dict(ref=(18, 59, 3), lang='ko', en='not', words=['아니요']),
    dict(ref=(18, 59, 3), lang='ko', en='nor', words=['아니로소이다']),
    # 시편 60:10  not not / 아니하셨나이까 아니하시나이다
    dict(ref=(18, 60, 10), lang='ko', en='not#1', words=['아니하셨나이까']),
    dict(ref=(18, 60, 10), lang='ko', en='not#2', words=['아니하시나이다']),
    # 시편 62:10  not not not / 말며 말며 말지어다
    dict(ref=(18, 62, 10), lang='ko', en='not#1', words=['말며#1']),
    dict(ref=(18, 62, 10), lang='ko', en='not#2', words=['말며#2']),
    dict(ref=(18, 62, 10), lang='ko', en='not#3', words=['말지어다']),
    # 시편 69:6  not not / 마옵소서 마옵소서
    dict(ref=(18, 69, 6), lang='ko', en='not#1', words=['마옵소서#1']),
    dict(ref=(18, 69, 6), lang='ko', en='not#2', words=['마옵소서#2']),
    # 시편 71:9  not not / 마시며 마소서
    dict(ref=(18, 71, 9), lang='ko', en='not#1', words=['마시며']),
    dict(ref=(18, 71, 9), lang='ko', en='not#2', words=['마소서']),
    # 시편 74:19  not not / 마시며 마소서
    dict(ref=(18, 74, 19), lang='ko', en='not#1', words=['마시며']),
    dict(ref=(18, 74, 19), lang='ko', en='not#2', words=['마소서']),
    # 시편 75:4  not not / 행치말라 말라
    dict(ref=(18, 75, 4), lang='ko', en='not#1', words=['행치말라']),
    dict(ref=(18, 75, 4), lang='ko', en='not#2', words=['말라']),
    # 시편 75:5  not not / 말며 말지어다
    dict(ref=(18, 75, 5), lang='ko', en='not#1', words=['말며']),
    dict(ref=(18, 75, 5), lang='ko', en='not#2', words=['말지어다']),
    # 시편 78:8  not not not / 못하며 아니한 않게
    dict(ref=(18, 78, 8), lang='ko', en='not#1', words=['못하며']),
    dict(ref=(18, 78, 8), lang='ko', en='not#2', words=['아니한']),
    dict(ref=(18, 78, 8), lang='ko', en='not#3', words=['않게']),
    # 시편 78:22  not not / 아니하며 아니한
    dict(ref=(18, 78, 22), lang='ko', en='not#1', words=['아니하며']),
    dict(ref=(18, 78, 22), lang='ko', en='not#2', words=['아니한']),
    # 시편 78:37  not neither / 없으며 아니하였음이로다
    dict(ref=(18, 78, 37), lang='ko', en='not', words=['없으며']),
    dict(ref=(18, 78, 37), lang='ko', en='neither', words=['아니하였음이로다']),
    # 시편 78:38  not not / 아니하시고 아니하셨으니
    dict(ref=(18, 78, 38), lang='ko', en='not#1', words=['아니하시고']),
    dict(ref=(18, 78, 38), lang='ko', en='not#2', words=['아니하셨으니']),
    # 시편 78:42  not nor / 아니하며 아니하였도다
    dict(ref=(18, 78, 42), lang='ko', en='not', words=['아니하며']),
    dict(ref=(18, 78, 42), lang='ko', en='nor', words=['아니하였도다']),
    # 시편 79:6  not not / 아니하는 아니하는
    dict(ref=(18, 79, 6), lang='ko', en='not#1', words=['아니하는#1']),
    dict(ref=(18, 79, 6), lang='ko', en='not#2', words=['아니하는#2']),
    # 시편 83:1  not not not / 마소서 말고 마소서
    dict(ref=(18, 83, 1), lang='ko', en='not#1', words=['마소서#1']),
    dict(ref=(18, 83, 1), lang='ko', en='not#2', words=['말고']),
    dict(ref=(18, 83, 1), lang='ko', en='not#3', words=['마소서#2']),
    # 시편 89:22  not nor / 못하며 못하리로다
    dict(ref=(18, 89, 22), lang='ko', en='not', words=['못하며']),
    dict(ref=(18, 89, 22), lang='ko', en='nor', words=['못하리로다']),
    # 시편 89:33  not nor / 아니하며 아니하며
    dict(ref=(18, 89, 33), lang='ko', en='not', words=['아니하며#1']),
    dict(ref=(18, 89, 33), lang='ko', en='nor', words=['아니하며#2']),
    # 시편 89:34  not nor / 아니하며 아니하리로다
    dict(ref=(18, 89, 34), lang='ko', en='not', words=['아니하며']),
    dict(ref=(18, 89, 34), lang='ko', en='nor', words=['아니하리로다']),
    # 시편 92:6  not neither / 못하며 못하나이다
    dict(ref=(18, 92, 6), lang='ko', en='not', words=['못하며']),
    dict(ref=(18, 92, 6), lang='ko', en='neither', words=['못하나이다']),
    # 시편 94:7  not neither / 못하며 못하리라
    dict(ref=(18, 94, 7), lang='ko', en='not', words=['못하며']),
    dict(ref=(18, 94, 7), lang='ko', en='neither', words=['못하리라']),
    # 시편 94:9  not not / 아니하시랴 아니하시랴
    dict(ref=(18, 94, 9), lang='ko', en='not#1', words=['아니하시랴#1']),
    dict(ref=(18, 94, 9), lang='ko', en='not#2', words=['아니하시랴#2']),
    # 시편 94:14  not neither / 아니하시며 아니하시리로다
    dict(ref=(18, 94, 14), lang='ko', en='not', words=['아니하시며']),
    dict(ref=(18, 94, 14), lang='ko', en='neither', words=['아니하시리로다']),
    # 시편 101:7  not not / 못하며 못하리로다
    dict(ref=(18, 101, 7), lang='ko', en='not#1', words=['못하며']),
    dict(ref=(18, 101, 7), lang='ko', en='not#2', words=['못하리로다']),
    # 시편 103:9  not neither / 아니하시며 아니하시리로다
    dict(ref=(18, 103, 9), lang='ko', en='not', words=['아니하시며']),
    dict(ref=(18, 103, 9), lang='ko', en='neither', words=['아니하시리로다']),
    # 시편 104:9  not not / 못하게 못하게
    dict(ref=(18, 104, 9), lang='ko', en='not#1', words=['못하게#1']),
    dict(ref=(18, 104, 9), lang='ko', en='not#2', words=['못하게#2']),
    # 시편 106:7  not not / 못하며 아니하고
    dict(ref=(18, 106, 7), lang='ko', en='not#1', words=['못하며']),
    dict(ref=(18, 106, 7), lang='ko', en='not#2', words=['아니하고']),
    # 시편 108:11  not not / 아니하셨나이까 아니하시나이다
    dict(ref=(18, 108, 11), lang='ko', en='not#1', words=['아니하셨나이까']),
    dict(ref=(18, 108, 11), lang='ko', en='not#2', words=['아니하시나이다']),
    # 시편 115:1  Not not / 마옵소서 마옵소서
    dict(ref=(18, 115, 1), lang='ko', en='Not', words=['마옵소서#1']),
    dict(ref=(18, 115, 1), lang='ko', en='not', words=['마옵소서#2']),
    # 시편 115:5  not not / 못하며 못하며
    dict(ref=(18, 115, 5), lang='ko', en='not#1', words=['못하며#1']),
    dict(ref=(18, 115, 5), lang='ko', en='not#2', words=['못하며#2']),
    # 시편 115:6  not not / 못하며 못하며
    dict(ref=(18, 115, 6), lang='ko', en='not#1', words=['못하며#1']),
    dict(ref=(18, 115, 6), lang='ko', en='not#2', words=['못하며#2']),
    # 시편 115:7  not not neither / 못하며 못하며 못하느니라
    dict(ref=(18, 115, 7), lang='ko', en='not#1', words=['못하며#1']),
    dict(ref=(18, 115, 7), lang='ko', en='not#2', words=['못하며#2']),
    dict(ref=(18, 115, 7), lang='ko', en='neither', words=['못하느니라']),
    # 시편 115:17  not neither / 못하나니 못하리로다
    dict(ref=(18, 115, 17), lang='ko', en='not', words=['못하나니']),
    dict(ref=(18, 115, 17), lang='ko', en='neither', words=['못하리로다']),
    # 시편 121:3  not not / 않게 아니하시리로다
    dict(ref=(18, 121, 3), lang='ko', en='not#1', words=['않게']),
    dict(ref=(18, 121, 3), lang='ko', en='not#2', words=['아니하시리로다']),
    # 시편 121:4  neither nor / 아니하고 아니하시리로다
    dict(ref=(18, 121, 4), lang='ko', en='neither', words=['아니하고']),
    dict(ref=(18, 121, 4), lang='ko', en='nor', words=['아니하시리로다']),
    # 시편 132:3  not nor / 아니하며 아니하며
    dict(ref=(18, 132, 3), lang='ko', en='not', words=['아니하며#1']),
    dict(ref=(18, 132, 3), lang='ko', en='nor', words=['아니하며#2']),
    # 시편 135:16  not not / 못하며 못하며
    dict(ref=(18, 135, 16), lang='ko', en='not#1', words=['못하며#1']),
    dict(ref=(18, 135, 16), lang='ko', en='not#2', words=['못하며#2']),
    # 시편 135:17  not neither / 못하며 없나니
    dict(ref=(18, 135, 17), lang='ko', en='not', words=['못하며']),
    dict(ref=(18, 135, 17), lang='ko', en='neither', words=['없나니']),
    # 시편 137:6  not not / 아니하거나 아니할진대
    dict(ref=(18, 137, 6), lang='ko', en='not#1', words=['아니하거나']),
    dict(ref=(18, 137, 6), lang='ko', en='not#2', words=['아니할진대']),
    # 시편 139:21  not not / 아니하오며 아니하나이까
    dict(ref=(18, 139, 21), lang='ko', en='not#1', words=['아니하오며']),
    dict(ref=(18, 139, 21), lang='ko', en='not#2', words=['아니하나이까']),
    # 시편 140:8  not not / 마시며 못하게
    dict(ref=(18, 140, 8), lang='ko', en='not#1', words=['마시며']),
    dict(ref=(18, 140, 8), lang='ko', en='not#2', words=['못하게']),
    # 시편 146:3  not nor / 말며 말지니
    dict(ref=(18, 146, 3), lang='ko', en='not', words=['말며']),
    dict(ref=(18, 146, 3), lang='ko', en='nor', words=['말지니']),
    # 시편 147:10  not not / 아니하시며 아니하시고
    dict(ref=(18, 147, 10), lang='ko', en='not#1', words=['아니하시며']),
    dict(ref=(18, 147, 10), lang='ko', en='not#2', words=['아니하시고']),
    # 시편 147:20  not not / 아니하셨나니 못하였도다
    dict(ref=(18, 147, 20), lang='ko', en='not#1', words=['아니하셨나니']),
    dict(ref=(18, 147, 20), lang='ko', en='not#2', words=['못하였도다']),
    # 잠언 1:28  not not / 아니하겠고 못하리니
    dict(ref=(19, 1, 28), lang='ko', en='not#1', words=['아니하겠고']),
    dict(ref=(19, 1, 28), lang='ko', en='not#2', words=['못하리니']),
    # 잠언 3:11  not neither / 말라 말라
    dict(ref=(19, 3, 11), lang='ko', en='not', words=['말라#1']),
    dict(ref=(19, 3, 11), lang='ko', en='neither', words=['말라#2']),
    # 잠언 4:5  not neither / 말며 말라
    dict(ref=(19, 4, 5), lang='ko', en='not', words=['말며']),
    dict(ref=(19, 4, 5), lang='ko', en='neither', words=['말라']),
    # 잠언 4:12  not not / 아니하겠고 아니하리라
    dict(ref=(19, 4, 12), lang='ko', en='not#1', words=['아니하겠고']),
    dict(ref=(19, 4, 12), lang='ko', en='not#2', words=['아니하리라']),
    # 잠언 4:14  not not / 말며 말지어다
    dict(ref=(19, 4, 14), lang='ko', en='not#1', words=['말며']),
    dict(ref=(19, 4, 14), lang='ko', en='not#2', words=['말지어다']),
    # 잠언 5:13  not nor / 아니하며 아니하였던고
    dict(ref=(19, 5, 13), lang='ko', en='not', words=['아니하며']),
    dict(ref=(19, 5, 13), lang='ko', en='nor', words=['아니하였던고']),
    # 잠언 6:4  not nor / 말며 말고
    dict(ref=(19, 6, 4), lang='ko', en='not', words=['말며']),
    dict(ref=(19, 6, 4), lang='ko', en='nor', words=['말고']),
    # 잠언 6:25  not neither / 말며 말라
    dict(ref=(19, 6, 25), lang='ko', en='not', words=['말며']),
    dict(ref=(19, 6, 25), lang='ko', en='neither', words=['말라']),
    # 잠언 6:35  not neither / 아니하며 아니하리라
    dict(ref=(19, 6, 35), lang='ko', en='not', words=['아니하며']),
    dict(ref=(19, 6, 35), lang='ko', en='neither', words=['아니하리라']),
    # 잠언 7:25  not not / 말며 말지어다
    dict(ref=(19, 7, 25), lang='ko', en='not#1', words=['말며']),
    dict(ref=(19, 7, 25), lang='ko', en='not#2', words=['말지어다']),
    # 잠언 10:30  never not / 아니하여도 못하게
    dict(ref=(19, 10, 30), lang='ko', en='never', words=['아니하여도']),
    dict(ref=(19, 10, 30), lang='ko', en='not', words=['못하게']),
    # 잠언 12:3  not not / 못하나니 아니하느니라
    dict(ref=(19, 12, 3), lang='ko', en='not#1', words=['못하나니']),
    dict(ref=(19, 12, 3), lang='ko', en='not#2', words=['아니하느니라']),
    # 잠언 15:12  not neither / 아니하며 아니하느니라
    dict(ref=(19, 15, 12), lang='ko', en='not', words=['아니하며']),
    dict(ref=(19, 15, 12), lang='ko', en='neither', words=['아니하느니라']),
    # 잠언 19:5  not not / 못할 못하리라
    dict(ref=(19, 19, 5), lang='ko', en='not#1', words=['못할']),
    dict(ref=(19, 19, 5), lang='ko', en='not#2', words=['못하리라']),
    # 잠언 22:22  not neither / 말며 말라
    dict(ref=(19, 22, 22), lang='ko', en='not', words=['말며']),
    dict(ref=(19, 22, 22), lang='ko', en='neither', words=['말라']),
    # 잠언 23:6  not neither / 말며 말지어다
    dict(ref=(19, 23, 6), lang='ko', en='not', words=['말며']),
    dict(ref=(19, 23, 6), lang='ko', en='neither', words=['말지어다']),
    # 잠언 23:10  not not / 말며 말지어다
    dict(ref=(19, 23, 10), lang='ko', en='not#1', words=['말며']),
    dict(ref=(19, 23, 10), lang='ko', en='not#2', words=['말지어다']),
    # 잠언 24:1  not neither / 말며 말지어다
    dict(ref=(19, 24, 1), lang='ko', en='not', words=['말며']),
    dict(ref=(19, 24, 1), lang='ko', en='neither', words=['말지어다']),
    # 잠언 24:15  not not / 말며 말지니라
    dict(ref=(19, 24, 15), lang='ko', en='not#1', words=['말며']),
    dict(ref=(19, 24, 15), lang='ko', en='not#2', words=['말지니라']),
    # 잠언 24:17  not not / 말며 말라
    dict(ref=(19, 24, 17), lang='ko', en='not#1', words=['말며']),
    dict(ref=(19, 24, 17), lang='ko', en='not#2', words=['말라']),
    # 잠언 24:19  not neither / 말며 말라
    dict(ref=(19, 24, 19), lang='ko', en='not', words=['말며']),
    dict(ref=(19, 24, 19), lang='ko', en='neither', words=['말라']),
    # 잠언 24:28  not not / 말며 말지니라
    dict(ref=(19, 24, 28), lang='ko', en='not#1', words=['말며']),
    dict(ref=(19, 24, 28), lang='ko', en='not#2', words=['말지니라']),
    # 잠언 25:6  not not / 말며 말라
    dict(ref=(19, 25, 6), lang='ko', en='not#1', words=['말며']),
    dict(ref=(19, 25, 6), lang='ko', en='not#2', words=['말라']),
    # 잠언 25:8  not not / 말라 못할까
    dict(ref=(19, 25, 8), lang='ko', en='not#1', words=['말라']),
    dict(ref=(19, 25, 8), lang='ko', en='not#2', words=['못할까']),
    # 잠언 27:1  not not / 말라 없음이니라
    dict(ref=(19, 27, 1), lang='ko', en='not#1', words=['말라']),
    dict(ref=(19, 27, 1), lang='ko', en='not#2', words=['없음이니라']),
    # 잠언 27:2  not not / 말며 말지니라
    dict(ref=(19, 27, 2), lang='ko', en='not#1', words=['말며']),
    dict(ref=(19, 27, 2), lang='ko', en='not#2', words=['말지니라']),
    # 잠언 27:10  not neither / 말며 말지어다
    dict(ref=(19, 27, 10), lang='ko', en='not', words=['말며']),
    dict(ref=(19, 27, 10), lang='ko', en='neither', words=['말지어다']),
    # 잠언 29:19  not not / 아니하나니 아니함이니라
    dict(ref=(19, 29, 19), lang='ko', en='not#1', words=['아니하나니']),
    dict(ref=(19, 29, 19), lang='ko', en='not#2', words=['아니함이니라']),
    # 잠언 30:3  neither nor / 못하였고 없거니와
    dict(ref=(19, 30, 3), lang='ko', en='neither', words=['못하였고']),
    dict(ref=(19, 30, 3), lang='ko', en='nor', words=['없거니와']),
    # 잠언 30:8  neither nor / 마옵시고 마옵시고
    dict(ref=(19, 30, 8), lang='ko', en='neither', words=['마옵시고#1']),
    dict(ref=(19, 30, 8), lang='ko', en='nor', words=['마옵시고#2']),
    # 잠언 30:15  never not / 못하여 아니하는
    dict(ref=(19, 30, 15), lang='ko', en='never', words=['못하여']),
    dict(ref=(19, 30, 15), lang='ko', en='not', words=['아니하는']),
    # 잠언 30:16  not not / 못하는 아니하는
    dict(ref=(19, 30, 16), lang='ko', en='not#1', words=['못하는']),
    dict(ref=(19, 30, 16), lang='ko', en='not#2', words=['아니하는']),
    # 잠언 31:3  not nor / 말며 말지어다
    dict(ref=(19, 31, 3), lang='ko', en='not', words=['말며']),
    dict(ref=(19, 31, 3), lang='ko', en='nor', words=['말지어다']),
    # 전도서 4:3  not not / 아니하여 못한
    dict(ref=(20, 4, 3), lang='ko', en='not#1', words=['아니하여']),
    dict(ref=(20, 4, 3), lang='ko', en='not#2', words=['못한']),
    # 전도서 5:5  not not / 아니하는 아니하는
    dict(ref=(20, 5, 5), lang='ko', en='not#1', words=['아니하는#1']),
    dict(ref=(20, 5, 5), lang='ko', en='not#2', words=['아니하는#2']),
    # 전도서 5:6  not neither / 말라 말라
    dict(ref=(20, 5, 6), lang='ko', en='not', words=['말라#1']),
    dict(ref=(20, 5, 6), lang='ko', en='neither', words=['말라#2']),
    # 전도서 6:5  not nor / 못하고 못하나
    dict(ref=(20, 6, 5), lang='ko', en='not', words=['못하고']),
    dict(ref=(20, 6, 5), lang='ko', en='nor', words=['못하나']),
    # 전도서 7:10  not not / 말라 아니니라
    dict(ref=(20, 7, 10), lang='ko', en='not#1', words=['말라']),
    dict(ref=(20, 7, 10), lang='ko', en='not#2', words=['아니니라']),
    # 전도서 7:16  not neither / 말며 말라
    dict(ref=(20, 7, 16), lang='ko', en='not', words=['말며']),
    dict(ref=(20, 7, 16), lang='ko', en='neither', words=['말라']),
    # 전도서 7:17  not neither / 말며 말라
    dict(ref=(20, 7, 17), lang='ko', en='not', words=['말며']),
    dict(ref=(20, 7, 17), lang='ko', en='neither', words=['말라']),
    # 전도서 7:20  not not / 아니하는 없느니라
    dict(ref=(20, 7, 20), lang='ko', en='not#1', words=['아니하는']),
    dict(ref=(20, 7, 20), lang='ko', en='not#2', words=['없느니라']),
    # 전도서 7:28  not not / 못한 못하였느니라
    dict(ref=(20, 7, 28), lang='ko', en='not#1', words=['못한']),
    dict(ref=(20, 7, 28), lang='ko', en='not#2', words=['못하였느니라']),
    # 전도서 8:3  not not / 말며 말라
    dict(ref=(20, 8, 3), lang='ko', en='not#1', words=['말며']),
    dict(ref=(20, 8, 3), lang='ko', en='not#2', words=['말라']),
    # 전도서 8:8  neither neither / 없으며 없느니라
    dict(ref=(20, 8, 8), lang='ko', en='neither#1', words=['없으며']),
    dict(ref=(20, 8, 8), lang='ko', en='neither#2', words=['없느니라']),
    # 전도서 8:13  not neither not / 못하며 못하고 아니함이니라
    dict(ref=(20, 8, 13), lang='ko', en='not#1', words=['못하며']),
    dict(ref=(20, 8, 13), lang='ko', en='neither', words=['못하고']),
    dict(ref=(20, 8, 13), lang='ko', en='not#2', words=['아니함이니라']),
    # 전도서 9:11  not nor neither nor nor / 아니며 아니며 아니며 아니며 아니니
    dict(ref=(20, 9, 11), lang='ko', en='not', words=['아니며#1']),
    dict(ref=(20, 9, 11), lang='ko', en='nor#1', words=['아니며#2']),
    dict(ref=(20, 9, 11), lang='ko', en='neither', words=['아니며#3']),
    dict(ref=(20, 9, 11), lang='ko', en='nor#2', words=['아니며#4']),
    dict(ref=(20, 9, 11), lang='ko', en='nor#3', words=['아니니']),
    # 전도서 11:4  not not / 아니할 아니하리라
    dict(ref=(20, 11, 4), lang='ko', en='not#1', words=['아니할']),
    dict(ref=(20, 11, 4), lang='ko', en='not#2', words=['아니하리라']),
    # 아가 2:7  not nor / 말고 말지니라
    dict(ref=(21, 2, 7), lang='ko', en='not', words=['말고']),
    dict(ref=(21, 2, 7), lang='ko', en='nor', words=['말지니라']),
    # 아가 3:5  not nor / 말고 말지니라
    dict(ref=(21, 3, 5), lang='ko', en='not', words=['말고']),
    dict(ref=(21, 3, 5), lang='ko', en='nor', words=['말지니라']),
    # 아가 8:4  not nor / 말며 말지니라
    dict(ref=(21, 8, 4), lang='ko', en='not', words=['말며']),
    dict(ref=(21, 8, 4), lang='ko', en='nor', words=['말지니라']),
    # 아가 8:7  cannot neither / 못하겠고 못하나니
    dict(ref=(21, 8, 7), lang='ko', en='cannot', words=['못하겠고']),
    dict(ref=(21, 8, 7), lang='ko', en='neither', words=['못하나니']),
    # 이사야 1:3  not not / 못하고 못하는도다
    dict(ref=(22, 1, 3), lang='ko', en='not#1', words=['못하고']),
    dict(ref=(22, 1, 3), lang='ko', en='not#2', words=['못하는도다']),
    # 이사야 1:23  not neither / 아니하며 아니하는도다
    dict(ref=(22, 1, 23), lang='ko', en='not', words=['아니하며']),
    dict(ref=(22, 1, 23), lang='ko', en='neither', words=['아니하는도다']),
    # 이사야 2:4  not neither / 아니하며 아니하리라
    dict(ref=(22, 2, 4), lang='ko', en='not', words=['아니하며']),
    dict(ref=(22, 2, 4), lang='ko', en='neither', words=['아니하리라']),
    # 이사야 5:6  not nor / 못하여 말라
    dict(ref=(22, 5, 6), lang='ko', en='not', words=['못하여']),
    dict(ref=(22, 5, 6), lang='ko', en='nor', words=['말라']),
    # 이사야 5:12  not neither / 아니하며 아니하는도다
    dict(ref=(22, 5, 12), lang='ko', en='not', words=['아니하며']),
    dict(ref=(22, 5, 12), lang='ko', en='neither', words=['아니하는도다']),
    # 이사야 6:9  not not / 못할 못하리라
    dict(ref=(22, 6, 9), lang='ko', en='not#1', words=['못할']),
    dict(ref=(22, 6, 9), lang='ko', en='not#2', words=['못하리라']),
    # 이사야 7:4  not neither / 말며 말라
    dict(ref=(22, 7, 4), lang='ko', en='not', words=['말며']),
    dict(ref=(22, 7, 4), lang='ko', en='neither', words=['말라']),
    # 이사야 7:7  not neither / 못하며 못하리라
    dict(ref=(22, 7, 7), lang='ko', en='not', words=['못하며']),
    dict(ref=(22, 7, 7), lang='ko', en='neither', words=['못하리라']),
    # 이사야 7:12  not neither / 아니하겠나이다 아니하겠나이다
    dict(ref=(22, 7, 12), lang='ko', en='not', words=['아니하겠나이다#1']),
    dict(ref=(22, 7, 12), lang='ko', en='neither', words=['아니하겠나이다#2']),
    # 이사야 8:12  not neither nor / 말며 말며 말고
    dict(ref=(22, 8, 12), lang='ko', en='not', words=['말며#1']),
    dict(ref=(22, 8, 12), lang='ko', en='neither', words=['말며#2']),
    dict(ref=(22, 8, 12), lang='ko', en='nor', words=['말고']),
    # 이사야 9:13  not neither / 아니하며 아니하도다
    dict(ref=(22, 9, 13), lang='ko', en='not', words=['아니하며']),
    dict(ref=(22, 9, 13), lang='ko', en='neither', words=['아니하도다']),
    # 이사야 10:9  not not not / 아니하며 아니하며 아니하냐
    dict(ref=(22, 10, 9), lang='ko', en='not#1', words=['아니하며#1']),
    dict(ref=(22, 10, 9), lang='ko', en='not#2', words=['아니하며#2']),
    dict(ref=(22, 10, 9), lang='ko', en='not#3', words=['아니하냐']),
    # 이사야 11:3  not neither / 아니하며 아니하며
    dict(ref=(22, 11, 3), lang='ko', en='not', words=['아니하며#1']),
    dict(ref=(22, 11, 3), lang='ko', en='neither', words=['아니하며#2']),
    # 이사야 13:10  not not / 아니하며 아니할
    dict(ref=(22, 13, 10), lang='ko', en='not#1', words=['아니하며']),
    dict(ref=(22, 13, 10), lang='ko', en='not#2', words=['아니할']),
    # 이사야 13:17  not not / 아니하며 아니하는
    dict(ref=(22, 13, 17), lang='ko', en='not#1', words=['아니하며']),
    dict(ref=(22, 13, 17), lang='ko', en='not#2', words=['아니하는']),
    # 이사야 14:20  not never / 못하나니 못하리로다
    dict(ref=(22, 14, 20), lang='ko', en='not', words=['못하나니']),
    dict(ref=(22, 14, 20), lang='ko', en='never', words=['못하리로다']),
    # 이사야 17:8  not neither / 아니하며 아니할
    dict(ref=(22, 17, 8), lang='ko', en='not', words=['아니하며']),
    dict(ref=(22, 17, 8), lang='ko', en='neither', words=['아니할']),
    # 이사야 22:2  not nor / 아니요 아니며
    dict(ref=(22, 22, 2), lang='ko', en='not', words=['아니요']),
    dict(ref=(22, 22, 2), lang='ko', en='nor', words=['아니며']),
    # 이사야 23:4  not nor neither nor / 못하였으며 못하였으며 못하였으며 못하였다
    dict(ref=(22, 23, 4), lang='ko', en='not', words=['못하였으며#1']),
    dict(ref=(22, 23, 4), lang='ko', en='nor#1', words=['못하였으며#2']),
    dict(ref=(22, 23, 4), lang='ko', en='neither', words=['못하였으며#3']),
    dict(ref=(22, 23, 4), lang='ko', en='nor#2', words=['못하였다']),
    # 이사야 26:10  not not / 아니하며 아니하는도다
    dict(ref=(22, 26, 10), lang='ko', en='not#1', words=['아니하며']),
    dict(ref=(22, 26, 10), lang='ko', en='not#2', words=['아니하는도다']),
    # 이사야 26:14  not not / 못하겠고 못할
    dict(ref=(22, 26, 14), lang='ko', en='not#1', words=['못하겠고']),
    dict(ref=(22, 26, 14), lang='ko', en='not#2', words=['못할']),
    # 이사야 26:18  not neither / 못하였고 못하였나이다
    dict(ref=(22, 26, 18), lang='ko', en='not', words=['못하였고']),
    dict(ref=(22, 26, 18), lang='ko', en='neither', words=['못하였나이다']),
    # 이사야 28:27  not neither / 아니하며 아니하고
    dict(ref=(22, 28, 27), lang='ko', en='not', words=['아니하며']),
    dict(ref=(22, 28, 27), lang='ko', en='neither', words=['아니하고']),
    # 이사야 28:28  not nor nor / 아니라 아니하고 아니하나니
    dict(ref=(22, 28, 28), lang='ko', en='not', words=['아니라']),
    dict(ref=(22, 28, 28), lang='ko', en='nor#1', words=['아니하고']),
    dict(ref=(22, 28, 28), lang='ko', en='nor#2', words=['아니하나니']),
    # 이사야 29:9  not not / 아니며 아니라
    dict(ref=(22, 29, 9), lang='ko', en='not#1', words=['아니며']),
    dict(ref=(22, 29, 9), lang='ko', en='not#2', words=['아니라']),
    # 이사야 29:22  not neither / 아니하겠고 아니할
    dict(ref=(22, 29, 22), lang='ko', en='not', words=['아니하겠고']),
    dict(ref=(22, 29, 22), lang='ko', en='neither', words=['아니할']),
    # 이사야 30:5  not nor nor / 못하는 못하며 못하고
    dict(ref=(22, 30, 5), lang='ko', en='not', words=['못하는']),
    dict(ref=(22, 30, 5), lang='ko', en='nor#1', words=['못하며']),
    dict(ref=(22, 30, 5), lang='ko', en='nor#2', words=['못하고']),
    # 이사야 30:10  not not / 말라 말라
    dict(ref=(22, 30, 10), lang='ko', en='not#1', words=['말라#1']),
    dict(ref=(22, 30, 10), lang='ko', en='not#2', words=['말라#2']),
    # 이사야 31:1  not neither / 아니하며 아니하거니와
    dict(ref=(22, 31, 1), lang='ko', en='not', words=['아니하며']),
    dict(ref=(22, 31, 1), lang='ko', en='neither', words=['아니하거니와']),
    # 이사야 31:3  not not / 아니며 아니라
    dict(ref=(22, 31, 3), lang='ko', en='not#1', words=['아니며']),
    dict(ref=(22, 31, 3), lang='ko', en='not#2', words=['아니라']),
    # 이사야 31:4  not nor / 아니할 아니할
    dict(ref=(22, 31, 4), lang='ko', en='not', words=['아니할#1']),
    dict(ref=(22, 31, 4), lang='ko', en='nor', words=['아니할#2']),
    # 이사야 35:9  nor not / 아니하므로 못하겠고
    dict(ref=(22, 35, 9), lang='ko', en='nor', words=['아니하므로']),
    dict(ref=(22, 35, 9), lang='ko', en='not', words=['못하겠고']),
    # 이사야 36:14  not not / 말라 못할
    dict(ref=(22, 36, 14), lang='ko', en='not#1', words=['말라']),
    dict(ref=(22, 36, 14), lang='ko', en='not#2', words=['못할']),
    # 이사야 36:15  Neither not / 말라 아니하리라
    dict(ref=(22, 36, 15), lang='ko', en='Neither', words=['말라']),
    dict(ref=(22, 36, 15), lang='ko', en='not', words=['아니하리라']),
    # 이사야 36:21  not not / 아니하였으니 말라
    dict(ref=(22, 36, 21), lang='ko', en='not#1', words=['아니하였으니']),
    dict(ref=(22, 36, 21), lang='ko', en='not#2', words=['말라']),
    # 이사야 37:10  not not / 아니하리라 말라
    dict(ref=(22, 37, 10), lang='ko', en='not#1', words=['아니하리라']),
    dict(ref=(22, 37, 10), lang='ko', en='not#2', words=['말라']),
    # 이사야 37:33  not nor nor nor / 못하며 못하며 못하며 못할
    dict(ref=(22, 37, 33), lang='ko', en='not', words=['못하며#1']),
    dict(ref=(22, 37, 33), lang='ko', en='nor#1', words=['못하며#2']),
    dict(ref=(22, 37, 33), lang='ko', en='nor#2', words=['못하며#3']),
    dict(ref=(22, 37, 33), lang='ko', en='nor#3', words=['못할']),
    # 이사야 38:18  cannot not cannot / 못하며 못하며 못하되
    dict(ref=(22, 38, 18), lang='ko', en='cannot#1', words=['못하며#1']),
    dict(ref=(22, 38, 18), lang='ko', en='not', words=['못하며#2']),
    dict(ref=(22, 38, 18), lang='ko', en='cannot#2', words=['못하되']),
    # 이사야 40:21  not not not not / 못하였느냐 못하였느냐 아니하였느냐 못하였느냐
    dict(ref=(22, 40, 21), lang='ko', en='not#1', words=['못하였느냐#1']),
    dict(ref=(22, 40, 21), lang='ko', en='not#2', words=['못하였느냐#2']),
    dict(ref=(22, 40, 21), lang='ko', en='not#3', words=['아니하였느냐']),
    dict(ref=(22, 40, 21), lang='ko', en='not#4', words=['못하였느냐#3']),
    # 이사야 40:31  not not / 아니하겠고 아니하리로다
    dict(ref=(22, 40, 31), lang='ko', en='not#1', words=['아니하겠고']),
    dict(ref=(22, 40, 31), lang='ko', en='not#2', words=['아니하리로다']),
    # 이사야 41:10  not not / 말라 말라
    dict(ref=(22, 41, 10), lang='ko', en='not#1', words=['말라#1']),
    dict(ref=(22, 41, 10), lang='ko', en='not#2', words=['말라#2']),
    # 이사야 42:2  not nor nor / 아니하며 아니하며 아니하며
    dict(ref=(22, 42, 2), lang='ko', en='not', words=['아니하며#1']),
    dict(ref=(22, 42, 2), lang='ko', en='nor#1', words=['아니하며#2']),
    dict(ref=(22, 42, 2), lang='ko', en='nor#2', words=['아니하며#3']),
    # 이사야 42:3  not not / 아니하며 아니하고
    dict(ref=(22, 42, 3), lang='ko', en='not#1', words=['아니하며']),
    dict(ref=(22, 42, 3), lang='ko', en='not#2', words=['아니하고']),
    # 이사야 42:16  not not not / 못하는 못하는 아니하리니
    dict(ref=(22, 42, 16), lang='ko', en='not#1', words=['못하는#1']),
    dict(ref=(22, 42, 16), lang='ko', en='not#2', words=['못하는#2']),
    dict(ref=(22, 42, 16), lang='ko', en='not#3', words=['아니하리니']),
    # 이사야 42:20  not not / 아니하며 아니하는도다
    dict(ref=(22, 42, 20), lang='ko', en='not#1', words=['아니하며']),
    dict(ref=(22, 42, 20), lang='ko', en='not#2', words=['아니하는도다']),
    # 이사야 42:24  not not neither / 아니시냐 아니하며 아니하였도다
    dict(ref=(22, 42, 24), lang='ko', en='not#1', words=['아니시냐']),
    dict(ref=(22, 42, 24), lang='ko', en='not#2', words=['아니하며']),
    dict(ref=(22, 42, 24), lang='ko', en='neither', words=['아니하였도다']),
    # 이사야 42:25  not not / 못하며 아니하는도다
    dict(ref=(22, 42, 25), lang='ko', en='not#1', words=['못하며']),
    dict(ref=(22, 42, 25), lang='ko', en='not#2', words=['아니하는도다']),
    # 이사야 43:2  not not neither / 못할 아니할 못하리니
    dict(ref=(22, 43, 2), lang='ko', en='not#1', words=['못할']),
    dict(ref=(22, 43, 2), lang='ko', en='not#2', words=['아니할']),
    dict(ref=(22, 43, 2), lang='ko', en='neither', words=['못하리니']),
    # 이사야 43:18  not neither / 말며 말라
    dict(ref=(22, 43, 18), lang='ko', en='not', words=['말며']),
    dict(ref=(22, 43, 18), lang='ko', en='neither', words=['말라']),
    # 이사야 43:23  not neither not nor / 아니하였고 아니하였느니라 아니하였고 아니하였거늘
    dict(ref=(22, 43, 23), lang='ko', en='not#1', words=['아니하였고#1']),
    dict(ref=(22, 43, 23), lang='ko', en='neither', words=['아니하였느니라']),
    dict(ref=(22, 43, 23), lang='ko', en='not#2', words=['아니하였고#2']),
    dict(ref=(22, 43, 23), lang='ko', en='nor', words=['아니하였거늘']),
    # 이사야 44:18  not nor cannot cannot / 못하고 못함은 못하며 못함이라
    dict(ref=(22, 44, 18), lang='ko', en='not', words=['못하고']),
    dict(ref=(22, 44, 18), lang='ko', en='nor', words=['못함은']),
    dict(ref=(22, 44, 18), lang='ko', en='cannot#1', words=['못하며']),
    dict(ref=(22, 44, 18), lang='ko', en='cannot#2', words=['못함이라']),
    # 이사야 44:19  neither nor / 없으므로 아니하니
    dict(ref=(22, 44, 19), lang='ko', en='neither', words=['없으므로']),
    dict(ref=(22, 44, 19), lang='ko', en='nor', words=['아니하니']),
    # 이사야 44:20  cannot nor not / 못하며 아니하냐 못하느니라
    dict(ref=(22, 44, 20), lang='ko', en='cannot', words=['못하며']),
    dict(ref=(22, 44, 20), lang='ko', en='nor', words=['아니하냐']),
    dict(ref=(22, 44, 20), lang='ko', en='not', words=['못하느니라']),
    # 이사야 45:19  not not / 아니하였으며 아니하였노라
    dict(ref=(22, 45, 19), lang='ko', en='not#1', words=['아니하였으며']),
    dict(ref=(22, 45, 19), lang='ko', en='not#2', words=['아니하였노라']),
    # 이사야 47:7  not neither / 아니하며 아니하였도다
    dict(ref=(22, 47, 7), lang='ko', en='not', words=['아니하며']),
    dict(ref=(22, 47, 7), lang='ko', en='neither', words=['아니하였도다']),
    # 이사야 47:14  not not nor / 못할 아니요 아니니라
    dict(ref=(22, 47, 14), lang='ko', en='not#1', words=['못할']),
    dict(ref=(22, 47, 14), lang='ko', en='not#2', words=['아니요']),
    dict(ref=(22, 47, 14), lang='ko', en='nor', words=['아니니라']),
    # 이사야 48:6  not not / 아니하겠느뇨 못하던
    dict(ref=(22, 48, 6), lang='ko', en='not#1', words=['아니하겠느뇨']),
    dict(ref=(22, 48, 6), lang='ko', en='not#2', words=['못하던']),
    # 이사야 48:8  not not not / 못하였고 못하였으며 못하였었나니
    dict(ref=(22, 48, 8), lang='ko', en='not#1', words=['못하였고']),
    dict(ref=(22, 48, 8), lang='ko', en='not#2', words=['못하였으며']),
    dict(ref=(22, 48, 8), lang='ko', en='not#3', words=['못하였었나니']),
    # 이사야 49:15  not not / 않겠느냐 아니할
    dict(ref=(22, 49, 15), lang='ko', en='not#1', words=['않겠느냐']),
    dict(ref=(22, 49, 15), lang='ko', en='not#2', words=['아니할']),
    # 이사야 50:5  not neither / 아니하며 아니하며
    dict(ref=(22, 50, 5), lang='ko', en='not', words=['아니하며#1']),
    dict(ref=(22, 50, 5), lang='ko', en='neither', words=['아니하며#2']),
    # 이사야 50:7  not not / 아니하고 아니할
    dict(ref=(22, 50, 7), lang='ko', en='not#1', words=['아니하고']),
    dict(ref=(22, 50, 7), lang='ko', en='not#2', words=['아니할']),
    # 이사야 51:7  not neither / 말라 말라
    dict(ref=(22, 51, 7), lang='ko', en='not', words=['말라#1']),
    dict(ref=(22, 51, 7), lang='ko', en='neither', words=['말라#2']),
    # 이사야 52:12  not nor / 아니하며 아니하리라
    dict(ref=(22, 52, 12), lang='ko', en='not', words=['아니하며']),
    dict(ref=(22, 52, 12), lang='ko', en='nor', words=['아니하리라']),
    # 이사야 52:15  not not / 않은 못한
    dict(ref=(22, 52, 15), lang='ko', en='not#1', words=['않은']),
    dict(ref=(22, 52, 15), lang='ko', en='not#2', words=['못한']),
    # 이사야 53:7  not not / 아니하였음이여 아니하였도다
    dict(ref=(22, 53, 7), lang='ko', en='not#1', words=['아니하였음이여']),
    dict(ref=(22, 53, 7), lang='ko', en='not#2', words=['아니하였도다']),
    # 이사야 54:4  not not neither not not / 말라 아니하리라 말라 아니하니라 없으리니
    dict(ref=(22, 54, 4), lang='ko', en='not#1', words=['말라#1']),
    dict(ref=(22, 54, 4), lang='ko', en='not#2', words=['아니하리라']),
    dict(ref=(22, 54, 4), lang='ko', en='neither', words=['말라#2']),
    dict(ref=(22, 54, 4), lang='ko', en='not#3', words=['아니하니라']),
    dict(ref=(22, 54, 4), lang='ko', en='not#4', words=['없으리니']),
    # 이사야 54:10  not neither / 아니하며 아니하리라
    dict(ref=(22, 54, 10), lang='ko', en='not', words=['아니하며']),
    dict(ref=(22, 54, 10), lang='ko', en='neither', words=['아니하리라']),
    # 이사야 54:14  not not / 아니할 못할
    dict(ref=(22, 54, 14), lang='ko', en='not#1', words=['아니할']),
    dict(ref=(22, 54, 14), lang='ko', en='not#2', words=['못할']),
    # 이사야 55:5  not not / 못하는 못하는
    dict(ref=(22, 55, 5), lang='ko', en='not#1', words=['못하는#1']),
    dict(ref=(22, 55, 5), lang='ko', en='not#2', words=['못하는#2']),
    # 이사야 56:3  Neither neither / 말며 말라
    dict(ref=(22, 56, 3), lang='ko', en='Neither', words=['말며']),
    dict(ref=(22, 56, 3), lang='ko', en='neither', words=['말라']),
    # 이사야 57:10  not not / 아니함은 아니함이니라
    dict(ref=(22, 57, 10), lang='ko', en='not#1', words=['아니함은']),
    dict(ref=(22, 57, 10), lang='ko', en='not#2', words=['아니함이니라']),
    # 이사야 57:11  not nor not not / 아니하며 아니하였느냐 아니함은 아니냐
    dict(ref=(22, 57, 11), lang='ko', en='not#1', words=['아니하며']),
    dict(ref=(22, 57, 11), lang='ko', en='nor', words=['아니하였느냐']),
    dict(ref=(22, 57, 11), lang='ko', en='not#2', words=['아니함은']),
    dict(ref=(22, 57, 11), lang='ko', en='not#3', words=['아니냐']),
    # 이사야 57:16  not neither / 아니하며 아니할
    dict(ref=(22, 57, 16), lang='ko', en='not', words=['아니하며']),
    dict(ref=(22, 57, 16), lang='ko', en='neither', words=['아니할']),
    # 이사야 58:7  not not / 아니하는 아니겠느냐
    dict(ref=(22, 58, 7), lang='ko', en='not#1', words=['아니하는']),
    dict(ref=(22, 58, 7), lang='ko', en='not#2', words=['아니겠느냐']),
    # 이사야 59:1  not cannot neither cannot / 못하심도 아니요 못하심도 아니라
    dict(ref=(22, 59, 1), lang='ko', en='not', words=['못하심도#1']),
    dict(ref=(22, 59, 1), lang='ko', en='cannot#1', words=['아니요']),
    dict(ref=(22, 59, 1), lang='ko', en='neither', words=['못하심도#2']),
    dict(ref=(22, 59, 1), lang='ko', en='cannot#2', words=['아니라']),
    # 이사야 62:1  not not / 아니하며 아니할
    dict(ref=(22, 62, 1), lang='ko', en='not#1', words=['아니하며']),
    dict(ref=(22, 62, 1), lang='ko', en='not#2', words=['아니할']),
    # 이사야 63:19  never not / 못하는 못하는
    dict(ref=(22, 63, 19), lang='ko', en='never', words=['못하는#1']),
    dict(ref=(22, 63, 19), lang='ko', en='not', words=['못하는#2']),
    # 이사야 64:9  not neither / 마옵시며 마옵소서
    dict(ref=(22, 64, 9), lang='ko', en='not', words=['마옵시며']),
    dict(ref=(22, 64, 9), lang='ko', en='neither', words=['마옵소서']),
    # 이사야 65:1  not not not / 아니하던 아니하던 아니하던
    dict(ref=(22, 65, 1), lang='ko', en='not#1', words=['아니하던#1']),
    dict(ref=(22, 65, 1), lang='ko', en='not#2', words=['아니하던#2']),
    dict(ref=(22, 65, 1), lang='ko', en='not#3', words=['아니하던#3']),
    # 이사야 65:8  not not / 말라 아니하고
    dict(ref=(22, 65, 8), lang='ko', en='not#1', words=['말라']),
    dict(ref=(22, 65, 8), lang='ko', en='not#2', words=['아니하고']),
    # 이사야 65:12  not not not / 아니하며 아니하고 아니하는
    dict(ref=(22, 65, 12), lang='ko', en='not#1', words=['아니하며']),
    dict(ref=(22, 65, 12), lang='ko', en='not#2', words=['아니하고']),
    dict(ref=(22, 65, 12), lang='ko', en='not#3', words=['아니하는']),
    # 이사야 65:22  not not / 아니할 아니하리니
    dict(ref=(22, 65, 22), lang='ko', en='not#1', words=['아니할']),
    dict(ref=(22, 65, 22), lang='ko', en='not#2', words=['아니하리니']),
    # 이사야 65:23  not nor / 않겠고 아니하리니
    dict(ref=(22, 65, 23), lang='ko', en='not', words=['않겠고']),
    dict(ref=(22, 65, 23), lang='ko', en='nor', words=['아니하리니']),
    # 이사야 66:19  not neither / 못하고 못한
    dict(ref=(22, 66, 19), lang='ko', en='not', words=['못하고']),
    dict(ref=(22, 66, 19), lang='ko', en='neither', words=['못한']),
    # 이사야 66:24  not neither / 아니하며 아니하여
    dict(ref=(22, 66, 24), lang='ko', en='not', words=['아니하며']),
    dict(ref=(22, 66, 24), lang='ko', en='neither', words=['아니하여']),
    # 예레미야 2:23  not not / 아니하였다 아니하였다
    dict(ref=(23, 2, 23), lang='ko', en='not#1', words=['아니하였다#1']),
    dict(ref=(23, 2, 23), lang='ko', en='not#2', words=['아니하였다#2']),
    # 예레미야 3:12  not not / 아니하리라 아니하느니라
    dict(ref=(23, 3, 12), lang='ko', en='not#1', words=['아니하리라']),
    dict(ref=(23, 3, 12), lang='ko', en='not#2', words=['아니하느니라']),
    # 예레미야 4:11  not nor / 아니요 아니며
    dict(ref=(23, 4, 11), lang='ko', en='not', words=['아니요']),
    dict(ref=(23, 4, 11), lang='ko', en='nor', words=['아니며']),
    # 예레미야 4:28  not neither / 아니하였은즉 아니하리라
    dict(ref=(23, 4, 28), lang='ko', en='not', words=['아니하였은즉']),
    dict(ref=(23, 4, 28), lang='ko', en='neither', words=['아니하리라']),
    # 예레미야 5:9  not not / 아니하겠으며 않겠느냐
    dict(ref=(23, 5, 9), lang='ko', en='not#1', words=['아니하겠으며']),
    dict(ref=(23, 5, 9), lang='ko', en='not#2', words=['않겠느냐']),
    # 예레미야 5:15  not neither / 못하며 못하느니라
    dict(ref=(23, 5, 15), lang='ko', en='not', words=['못하며']),
    dict(ref=(23, 5, 15), lang='ko', en='neither', words=['못하느니라']),
    # 예레미야 5:22  not not cannot not not / 아니하느냐 아니하겠느냐 못하게 못하며 못하느니라
    dict(ref=(23, 5, 22), lang='ko', en='not#1', words=['아니하느냐']),
    dict(ref=(23, 5, 22), lang='ko', en='not#2', words=['아니하겠느냐']),
    dict(ref=(23, 5, 22), lang='ko', en='cannot', words=['못하게']),
    dict(ref=(23, 5, 22), lang='ko', en='not#3', words=['못하며']),
    dict(ref=(23, 5, 22), lang='ko', en='not#4', words=['못하느니라']),
    # 예레미야 5:28  not not / 아니하며 아니하니
    dict(ref=(23, 5, 28), lang='ko', en='not#1', words=['아니하며']),
    dict(ref=(23, 5, 28), lang='ko', en='not#2', words=['아니하니']),
    # 예레미야 5:29  not not / 아니하겠으며 않겠느냐
    dict(ref=(23, 5, 29), lang='ko', en='not#1', words=['아니하겠으며']),
    dict(ref=(23, 5, 29), lang='ko', en='not#2', words=['않겠느냐']),
    # 예레미야 6:20  not nor / 아니하며 않노라
    dict(ref=(23, 6, 20), lang='ko', en='not', words=['아니하며']),
    dict(ref=(23, 6, 20), lang='ko', en='nor', words=['않노라']),
    # 예레미야 6:25  not nor / 말라 말라
    dict(ref=(23, 6, 25), lang='ko', en='not', words=['말라#1']),
    dict(ref=(23, 6, 25), lang='ko', en='nor', words=['말라#2']),
    # 예레미야 7:6  not not neither / 말며 아니하며 아니하면
    dict(ref=(23, 7, 6), lang='ko', en='not#1', words=['말며']),
    dict(ref=(23, 7, 6), lang='ko', en='not#2', words=['아니하며']),
    dict(ref=(23, 7, 6), lang='ko', en='neither', words=['아니하면']),
    # 예레미야 7:13  not not / 아니하였고 아니하였느니라
    dict(ref=(23, 7, 13), lang='ko', en='not#1', words=['아니하였고']),
    dict(ref=(23, 7, 13), lang='ko', en='not#2', words=['아니하였느니라']),
    # 예레미야 7:24  not nor not / 아니하며 아니하고 아니하였으며
    dict(ref=(23, 7, 24), lang='ko', en='not#1', words=['아니하며']),
    dict(ref=(23, 7, 24), lang='ko', en='nor', words=['아니하고']),
    dict(ref=(23, 7, 24), lang='ko', en='not#2', words=['아니하였으며']),
    # 예레미야 7:27  not not / 아니할 아니하리니
    dict(ref=(23, 7, 27), lang='ko', en='not#1', words=['아니할']),
    dict(ref=(23, 7, 27), lang='ko', en='not#2', words=['아니하리니']),
    # 예레미야 7:31  not neither / 아니하였고 아니한
    dict(ref=(23, 7, 31), lang='ko', en='not', words=['아니하였고']),
    dict(ref=(23, 7, 31), lang='ko', en='neither', words=['아니한']),
    # 예레미야 8:4  not not / 아니하겠으며 아니하겠느냐
    dict(ref=(23, 8, 4), lang='ko', en='not#1', words=['아니하겠으며']),
    dict(ref=(23, 8, 4), lang='ko', en='not#2', words=['아니하겠느냐']),
    # 예레미야 8:19  not not / 아니한가 아니한가
    dict(ref=(23, 8, 19), lang='ko', en='not#1', words=['아니한가#1']),
    dict(ref=(23, 8, 19), lang='ko', en='not#2', words=['아니한가#2']),
    # 예레미야 9:3  not not / 아니하고 아니하느니라
    dict(ref=(23, 9, 3), lang='ko', en='not#1', words=['아니하고']),
    dict(ref=(23, 9, 3), lang='ko', en='not#2', words=['아니하느니라']),
    # 예레미야 9:9  not not / 아니하겠으며 않겠느냐
    dict(ref=(23, 9, 9), lang='ko', en='not#1', words=['아니하겠으며']),
    dict(ref=(23, 9, 9), lang='ko', en='not#2', words=['않겠느냐']),
    # 예레미야 9:13  not neither / 아니하며 아니하고
    dict(ref=(23, 9, 13), lang='ko', en='not', words=['아니하며']),
    dict(ref=(23, 9, 13), lang='ko', en='neither', words=['아니하고']),
    # 예레미야 9:23  not neither not / 말라 말라 말라
    dict(ref=(23, 9, 23), lang='ko', en='not#1', words=['말라#1']),
    dict(ref=(23, 9, 23), lang='ko', en='neither', words=['말라#2']),
    dict(ref=(23, 9, 23), lang='ko', en='not#2', words=['말라#3']),
    # 예레미야 10:2  not not / 말라 말라
    dict(ref=(23, 10, 2), lang='ko', en='not#1', words=['말라#1']),
    dict(ref=(23, 10, 2), lang='ko', en='not#2', words=['말라#2']),
    # 예레미야 10:21  not not / 아니하므로 못하며
    dict(ref=(23, 10, 21), lang='ko', en='not#1', words=['아니하므로']),
    dict(ref=(23, 10, 21), lang='ko', en='not#2', words=['못하며']),
    # 예레미야 10:23  not not / 아니하니 아니하니이다
    dict(ref=(23, 10, 23), lang='ko', en='not#1', words=['아니하니']),
    dict(ref=(23, 10, 23), lang='ko', en='not#2', words=['아니하니이다']),
    # 예레미야 10:25  not not / 못하는 아니하는
    dict(ref=(23, 10, 25), lang='ko', en='not#1', words=['못하는']),
    dict(ref=(23, 10, 25), lang='ko', en='not#2', words=['아니하는']),
    # 예레미야 11:8  not nor not / 아니하며 아니하고 아니한
    dict(ref=(23, 11, 8), lang='ko', en='not#1', words=['아니하며']),
    dict(ref=(23, 11, 8), lang='ko', en='nor', words=['아니하고']),
    dict(ref=(23, 11, 8), lang='ko', en='not#2', words=['아니한']),
    # 예레미야 11:14  not neither not / 말라 말라 아니하리라
    dict(ref=(23, 11, 14), lang='ko', en='not#1', words=['말라#1']),
    dict(ref=(23, 11, 14), lang='ko', en='neither', words=['말라#2']),
    dict(ref=(23, 11, 14), lang='ko', en='not#2', words=['아니하리라']),
    # 예레미야 13:14  not nor nor / 아니하며 아니하며 아니하고
    dict(ref=(23, 13, 14), lang='ko', en='not', words=['아니하며#1']),
    dict(ref=(23, 13, 14), lang='ko', en='nor#1', words=['아니하며#2']),
    dict(ref=(23, 13, 14), lang='ko', en='nor#2', words=['아니하고']),
    # 예레미야 14:10  not not / 아니하므로 아니하고
    dict(ref=(23, 14, 10), lang='ko', en='not#1', words=['아니하므로']),
    dict(ref=(23, 14, 10), lang='ko', en='not#2', words=['아니하고']),
    # 예레미야 14:13  not neither / 아니하겠고 아니할
    dict(ref=(23, 14, 13), lang='ko', en='not', words=['아니하겠고']),
    dict(ref=(23, 14, 13), lang='ko', en='neither', words=['아니할']),
    # 예레미야 14:15  not not / 아니하였어도 아니하리라
    dict(ref=(23, 14, 15), lang='ko', en='not#1', words=['아니하였어도']),
    dict(ref=(23, 14, 15), lang='ko', en='not#2', words=['아니하리라']),
    # 예레미야 14:21  not not not / 마옵소서 마옵소서 마옵소서
    dict(ref=(23, 14, 21), lang='ko', en='not#1', words=['마옵소서#1']),
    dict(ref=(23, 14, 21), lang='ko', en='not#2', words=['마옵소서#2']),
    dict(ref=(23, 14, 21), lang='ko', en='not#3', words=['마옵소서#3']),
    # 예레미야 15:10  neither nor / 아니하였고 아니하였건마는
    dict(ref=(23, 15, 10), lang='ko', en='neither', words=['아니하였고']),
    dict(ref=(23, 15, 10), lang='ko', en='nor', words=['아니하였건마는']),
    # 예레미야 15:17  not nor / 아니하며 아니하고
    dict(ref=(23, 15, 17), lang='ko', en='not', words=['아니하며']),
    dict(ref=(23, 15, 17), lang='ko', en='nor', words=['아니하고']),
    # 예레미야 16:2  not neither / 말며 말지니라
    dict(ref=(23, 16, 2), lang='ko', en='not', words=['말며']),
    dict(ref=(23, 16, 2), lang='ko', en='neither', words=['말지니라']),
    # 예레미야 16:4  not neither / 못하며 못하여
    dict(ref=(23, 16, 4), lang='ko', en='not', words=['못하며']),
    dict(ref=(23, 16, 4), lang='ko', en='neither', words=['못하여']),
    # 예레미야 16:5  not neither nor / 말라 말며 말라
    dict(ref=(23, 16, 5), lang='ko', en='not', words=['말라#1']),
    dict(ref=(23, 16, 5), lang='ko', en='neither', words=['말며']),
    dict(ref=(23, 16, 5), lang='ko', en='nor', words=['말라#2']),
    # 예레미야 16:7  Neither neither / 마시울 없으리라
    # 예레미야 16:17  not neither / 못하며 못함이라
    dict(ref=(23, 16, 17), lang='ko', en='not', words=['못하며']),
    dict(ref=(23, 16, 17), lang='ko', en='neither', words=['못함이라']),
    # 예레미야 17:6  not not / 못하고 않는
    dict(ref=(23, 17, 6), lang='ko', en='not#1', words=['못하고']),
    dict(ref=(23, 17, 6), lang='ko', en='not#2', words=['않는']),
    # 예레미야 17:16  not neither / 아니하고 아니하였음을
    dict(ref=(23, 17, 16), lang='ko', en='not', words=['아니하고']),
    dict(ref=(23, 17, 16), lang='ko', en='neither', words=['아니하였음을']),
    # 예레미야 17:18  not not / 마옵소서 마시옵소서
    dict(ref=(23, 17, 18), lang='ko', en='not#1', words=['마옵소서']),
    dict(ref=(23, 17, 18), lang='ko', en='not#2', words=['마시옵소서']),
    # 예레미야 17:22  Neither neither / 말며 말아서
    dict(ref=(23, 17, 22), lang='ko', en='Neither', words=['말며']),
    dict(ref=(23, 17, 22), lang='ko', en='neither', words=['말아서']),
    # 예레미야 17:23  not neither not nor / 아니하며 아니하며 아니하며 아니하였느니라
    dict(ref=(23, 17, 23), lang='ko', en='not#1', words=['아니하며#1']),
    dict(ref=(23, 17, 23), lang='ko', en='neither', words=['아니하며#2']),
    dict(ref=(23, 17, 23), lang='ko', en='not#2', words=['아니하며#3']),
    dict(ref=(23, 17, 23), lang='ko', en='nor', words=['아니하였느니라']),
    # 예레미야 17:27  not not not / 아니하고 아니하여 아니하리라
    dict(ref=(23, 17, 27), lang='ko', en='not#1', words=['아니하고']),
    dict(ref=(23, 17, 27), lang='ko', en='not#2', words=['아니하여']),
    dict(ref=(23, 17, 27), lang='ko', en='not#3', words=['아니하리라']),
    # 예레미야 18:23  not neither / 마시며 마시고
    dict(ref=(23, 18, 23), lang='ko', en='not', words=['마시며']),
    dict(ref=(23, 18, 23), lang='ko', en='neither', words=['마시고']),
    # 예레미야 20:9  not nor not / 아니하며 아니하리라 없나이다
    dict(ref=(23, 20, 9), lang='ko', en='not#1', words=['아니하며']),
    dict(ref=(23, 20, 9), lang='ko', en='nor', words=['아니하리라']),
    dict(ref=(23, 20, 9), lang='ko', en='not#2', words=['없나이다']),
    # 예레미야 20:11  not not never / 못할 못하므로 못할
    dict(ref=(23, 20, 11), lang='ko', en='not#1', words=['못할#1']),
    dict(ref=(23, 20, 11), lang='ko', en='not#2', words=['못하므로']),
    dict(ref=(23, 20, 11), lang='ko', en='never', words=['못할#2']),
    # 예레미야 21:7  not neither nor / 아니하며 아니하며 아니하리라
    dict(ref=(23, 21, 7), lang='ko', en='not', words=['아니하며#1']),
    dict(ref=(23, 21, 7), lang='ko', en='neither', words=['아니하며#2']),
    dict(ref=(23, 21, 7), lang='ko', en='nor', words=['아니하리라']),
    # 예레미야 22:3  nor neither / 말며 말라
    dict(ref=(23, 22, 3), lang='ko', en='nor', words=['말며']),
    dict(ref=(23, 22, 3), lang='ko', en='neither', words=['말라']),
    # 예레미야 22:10  not neither nor / 말며 말고 못할
    dict(ref=(23, 22, 10), lang='ko', en='not', words=['말며']),
    dict(ref=(23, 22, 10), lang='ko', en='neither', words=['말고']),
    dict(ref=(23, 22, 10), lang='ko', en='nor', words=['못할']),
    # 예레미야 22:18  not not / 아니할 아니할
    dict(ref=(23, 22, 18), lang='ko', en='not#1', words=['아니할#1']),
    dict(ref=(23, 22, 18), lang='ko', en='not#2', words=['아니할#2']),
    # 예레미야 22:21  not not / 아니하리라 아니함이
    dict(ref=(23, 22, 21), lang='ko', en='not#1', words=['아니하리라']),
    dict(ref=(23, 22, 21), lang='ko', en='not#2', words=['아니함이']),
    # 예레미야 23:21  not not / 아니하였어도 아니하였어도
    dict(ref=(23, 23, 21), lang='ko', en='not#1', words=['아니하였어도#1']),
    dict(ref=(23, 23, 21), lang='ko', en='not#2', words=['아니하였어도#2']),
    # 예레미야 23:24  not not / 아니하려고 아니하냐
    dict(ref=(23, 23, 24), lang='ko', en='not#1', words=['아니하려고']),
    dict(ref=(23, 23, 24), lang='ko', en='not#2', words=['아니하냐']),
    # 예레미야 23:32  not nor not / 아니하였으며 아니하였나니 없느니라
    dict(ref=(23, 23, 32), lang='ko', en='not#1', words=['아니하였으며']),
    dict(ref=(23, 23, 32), lang='ko', en='nor', words=['아니하였나니']),
    dict(ref=(23, 23, 32), lang='ko', en='not#2', words=['없느니라']),
    # 예레미야 24:6  not not / 아니하며 아니하겠고
    dict(ref=(23, 24, 6), lang='ko', en='not#1', words=['아니하며']),
    dict(ref=(23, 24, 6), lang='ko', en='not#2', words=['아니하겠고']),
    # 예레미야 25:4  not nor / 아니하였으며 아니하였도다
    dict(ref=(23, 25, 4), lang='ko', en='not', words=['아니하였으며']),
    dict(ref=(23, 25, 4), lang='ko', en='nor', words=['아니하였도다']),
    # 예레미야 25:33  not neither nor / 못하며 못하며 못하고
    dict(ref=(23, 25, 33), lang='ko', en='not', words=['못하며#1']),
    dict(ref=(23, 25, 33), lang='ko', en='neither', words=['못하며#2']),
    dict(ref=(23, 25, 33), lang='ko', en='nor', words=['못하고']),
    # 예레미야 27:8  not not / 아니하는 아니하는
    dict(ref=(23, 27, 8), lang='ko', en='not#1', words=['아니하는#1']),
    dict(ref=(23, 27, 8), lang='ko', en='not#2', words=['아니하는#2']),
    # 예레미야 27:14  not not / 아니하리라 마소서
    dict(ref=(23, 27, 14), lang='ko', en='not#1', words=['아니하리라']),
    dict(ref=(23, 27, 14), lang='ko', en='not#2', words=['마소서']),
    # 예레미야 29:8  not neither / 말며 말라
    dict(ref=(23, 29, 8), lang='ko', en='not', words=['말며']),
    dict(ref=(23, 29, 8), lang='ko', en='neither', words=['말라']),
    # 예레미야 29:19  not not / 아니하며 아니함이니라
    dict(ref=(23, 29, 19), lang='ko', en='not#1', words=['아니하며']),
    dict(ref=(23, 29, 19), lang='ko', en='not#2', words=['아니함이니라']),
    # 예레미야 30:11  not not / 아니하리라 아니하리라
    dict(ref=(23, 30, 11), lang='ko', en='not#1', words=['아니하리라#1']),
    dict(ref=(23, 30, 11), lang='ko', en='not#2', words=['아니하리라#2']),
    # 예레미야 30:19  not not / 아니하겠고 아니하겠으며
    dict(ref=(23, 30, 19), lang='ko', en='not#1', words=['아니하겠고']),
    dict(ref=(23, 30, 19), lang='ko', en='not#2', words=['아니하겠으며']),
    # 예레미야 32:35  not neither / 아니요 아니니라
    dict(ref=(23, 32, 35), lang='ko', en='not', words=['아니요']),
    dict(ref=(23, 32, 35), lang='ko', en='neither', words=['아니니라']),
    # 예레미야 32:40  not not / 아니하리라 않게
    dict(ref=(23, 32, 40), lang='ko', en='not#1', words=['아니하리라']),
    dict(ref=(23, 32, 40), lang='ko', en='not#2', words=['않게']),
    # 예레미야 33:22  cannot neither / 없으며 없나니
    dict(ref=(23, 33, 22), lang='ko', en='cannot', words=['없으며']),
    dict(ref=(23, 33, 22), lang='ko', en='neither', words=['없나니']),
    # 예레미야 33:25  not not / 아니할 아니할
    dict(ref=(23, 33, 25), lang='ko', en='not#1', words=['아니할#1']),
    dict(ref=(23, 33, 25), lang='ko', en='not#2', words=['아니할#2']),
    # 예레미야 34:14  not neither / 아니하며 아니하였느니라
    dict(ref=(23, 34, 14), lang='ko', en='not', words=['아니하며']),
    dict(ref=(23, 34, 14), lang='ko', en='neither', words=['아니하였느니라']),
    # 예레미야 35:7  Neither nor nor nor / 말며 말며 말며 말고
    dict(ref=(23, 35, 7), lang='ko', en='Neither', words=['말며#1']),
    dict(ref=(23, 35, 7), lang='ko', en='nor#1', words=['말며#2']),
    dict(ref=(23, 35, 7), lang='ko', en='nor#2', words=['말며#3']),
    dict(ref=(23, 35, 7), lang='ko', en='nor#3', words=['말고']),
    # 예레미야 35:15  not not nor / 말라 아니하며 아니하였느니라
    dict(ref=(23, 35, 15), lang='ko', en='not#1', words=['말라']),
    dict(ref=(23, 35, 15), lang='ko', en='not#2', words=['아니하며']),
    dict(ref=(23, 35, 15), lang='ko', en='nor', words=['아니하였느니라']),
    # 예레미야 35:17  not not / 아니하며 아니함이니라
    dict(ref=(23, 35, 17), lang='ko', en='not#1', words=['아니하며']),
    dict(ref=(23, 35, 17), lang='ko', en='not#2', words=['아니함이니라']),
    # 예레미야 38:15  not not / 아니하시리이까 아니하시리이다
    dict(ref=(23, 38, 15), lang='ko', en='not#1', words=['아니하시리이까']),
    dict(ref=(23, 38, 15), lang='ko', en='not#2', words=['아니하시리이다']),
    # 예레미야 38:16  not neither / 아니하겠고 아니하리라
    dict(ref=(23, 38, 16), lang='ko', en='not', words=['아니하겠고']),
    dict(ref=(23, 38, 16), lang='ko', en='neither', words=['아니하리라']),
    # 예레미야 38:18  not not / 아니하면 못하리라
    dict(ref=(23, 38, 18), lang='ko', en='not#1', words=['아니하면']),
    dict(ref=(23, 38, 18), lang='ko', en='not#2', words=['못하리라']),
    # 예레미야 42:10  not not / 아니하며 아니하리니
    dict(ref=(23, 42, 10), lang='ko', en='not#1', words=['아니하며']),
    dict(ref=(23, 42, 10), lang='ko', en='not#2', words=['아니하리니']),
    # 예레미야 42:11  not not / 말라 말라
    dict(ref=(23, 42, 11), lang='ko', en='not#1', words=['말라#1']),
    dict(ref=(23, 42, 11), lang='ko', en='not#2', words=['말라#2']),
    # 예레미야 42:13  not neither / 아니하고 아니하리라
    dict(ref=(23, 42, 13), lang='ko', en='not', words=['아니하고']),
    dict(ref=(23, 42, 13), lang='ko', en='neither', words=['아니하리라']),
    # 예레미야 43:2  not not / 말라고 아니하셨느니라
    dict(ref=(23, 43, 2), lang='ko', en='not#1', words=['말라고']),
    dict(ref=(23, 43, 2), lang='ko', en='not#2', words=['아니하셨느니라']),
    # 예레미야 44:21  not not / 아니하셨느냐 아니하셨느냐
    dict(ref=(23, 44, 21), lang='ko', en='not#1', words=['아니하셨느냐#1']),
    dict(ref=(23, 44, 21), lang='ko', en='not#2', words=['아니하셨느냐#2']),
    # 예레미야 46:6  not nor / 못하며 못하고
    dict(ref=(23, 46, 6), lang='ko', en='not', words=['못하며']),
    dict(ref=(23, 46, 6), lang='ko', en='nor', words=['못하고']),
    # 예레미야 46:28  not not not / 말라 아니하리라 아니하리라
    dict(ref=(23, 46, 28), lang='ko', en='not#1', words=['말라']),
    dict(ref=(23, 46, 28), lang='ko', en='not#2', words=['아니하리라#1']),
    dict(ref=(23, 46, 28), lang='ko', en='not#3', words=['아니하리라#2']),
    # 예레미야 48:11  not neither not / 아니하였으므로 않음 아니하였도다
    dict(ref=(23, 48, 11), lang='ko', en='not#1', words=['아니하였으므로']),
    dict(ref=(23, 48, 11), lang='ko', en='neither', words=['않음']),
    dict(ref=(23, 48, 11), lang='ko', en='not#2', words=['아니하였도다']),
    # 에스겔 2:6  not neither not nor / 말고 말지어다 말며 말지어다
    dict(ref=(25, 2, 6), lang='ko', en='not#1', words=['말고']),
    dict(ref=(25, 2, 6), lang='ko', en='neither', words=['말지어다#1']),
    dict(ref=(25, 2, 6), lang='ko', en='not#2', words=['말며']),
    dict(ref=(25, 2, 6), lang='ko', en='nor', words=['말지어다#2']),
    # 에스겔 3:6  Not not / 못할 아니니라
    dict(ref=(25, 3, 6), lang='ko', en='Not', words=['못할']),
    dict(ref=(25, 3, 6), lang='ko', en='not', words=['아니니라']),
    # 에스겔 3:7  not not / 아니하리니 아니함이니라
    dict(ref=(25, 3, 7), lang='ko', en='not#1', words=['아니하리니']),
    dict(ref=(25, 3, 7), lang='ko', en='not#2', words=['아니함이니라']),
    # 에스겔 3:9  not neither / 말며 말라
    dict(ref=(25, 3, 9), lang='ko', en='not', words=['말며']),
    dict(ref=(25, 3, 9), lang='ko', en='neither', words=['말라']),
    # 에스겔 3:18  not nor / 아니하거나 아니하면
    dict(ref=(25, 3, 18), lang='ko', en='not', words=['아니하거나']),
    dict(ref=(25, 3, 18), lang='ko', en='nor', words=['아니하면']),
    # 에스겔 3:20  not not / 아니라 않음이라
    dict(ref=(25, 3, 20), lang='ko', en='not#1', words=['아니라']),
    dict(ref=(25, 3, 20), lang='ko', en='not#2', words=['않음이라']),
    # 에스겔 3:21  not not / 않게 아니하면
    dict(ref=(25, 3, 21), lang='ko', en='not#1', words=['않게']),
    dict(ref=(25, 3, 21), lang='ko', en='not#2', words=['아니하면']),
    # 에스겔 5:7  not neither neither / 아니하며 아니하고 아니하였느니라
    dict(ref=(25, 5, 7), lang='ko', en='not', words=['아니하며']),
    dict(ref=(25, 5, 7), lang='ko', en='neither#1', words=['아니하고']),
    dict(ref=(25, 5, 7), lang='ko', en='neither#2', words=['아니하였느니라']),
    # 에스겔 5:11  neither neither / 아니하며 아니하고
    dict(ref=(25, 5, 11), lang='ko', en='neither#1', words=['아니하며']),
    dict(ref=(25, 5, 11), lang='ko', en='neither#2', words=['아니하고']),
    # 에스겔 7:4  not neither / 아니하며 아니하고
    dict(ref=(25, 7, 4), lang='ko', en='not', words=['아니하며']),
    dict(ref=(25, 7, 4), lang='ko', en='neither', words=['아니하고']),
    # 에스겔 7:9  not neither / 아니하며 아니하고
    dict(ref=(25, 7, 9), lang='ko', en='not', words=['아니하며']),
    dict(ref=(25, 7, 9), lang='ko', en='neither', words=['아니하고']),
    # 에스겔 8:18  not neither not / 아니하고 아니하리니 아니하리라
    dict(ref=(25, 8, 18), lang='ko', en='not#1', words=['아니하고']),
    dict(ref=(25, 8, 18), lang='ko', en='neither', words=['아니하리니']),
    dict(ref=(25, 8, 18), lang='ko', en='not#2', words=['아니하리라']),
    # 에스겔 9:5  not neither / 말며 말고
    dict(ref=(25, 9, 5), lang='ko', en='not', words=['말며']),
    dict(ref=(25, 9, 5), lang='ko', en='neither', words=['말고']),
    # 에스겔 9:10  not neither / 아니하며 아니하고
    dict(ref=(25, 9, 10), lang='ko', en='not', words=['아니하며']),
    dict(ref=(25, 9, 10), lang='ko', en='neither', words=['아니하고']),
    # 에스겔 10:11  not not / 않고 않고
    dict(ref=(25, 10, 11), lang='ko', en='not#1', words=['않고#1']),
    dict(ref=(25, 10, 11), lang='ko', en='not#2', words=['않고#2']),
    # 에스겔 11:11  not neither / 아니하고 아니할지라
    dict(ref=(25, 11, 11), lang='ko', en='not', words=['아니하고']),
    dict(ref=(25, 11, 11), lang='ko', en='neither', words=['아니할지라']),
    # 에스겔 11:12  not neither / 아니하며 아니하고
    dict(ref=(25, 11, 12), lang='ko', en='not', words=['아니하며']),
    dict(ref=(25, 11, 12), lang='ko', en='neither', words=['아니하고']),
    # 에스겔 12:2  not not / 아니하고 아니하나니
    dict(ref=(25, 12, 2), lang='ko', en='not#1', words=['아니하고']),
    dict(ref=(25, 12, 2), lang='ko', en='not#2', words=['아니하나니']),
    # 에스겔 13:5  not neither / 아니하였으며 아니하였느니라
    dict(ref=(25, 13, 5), lang='ko', en='not', words=['아니하였으며']),
    dict(ref=(25, 13, 5), lang='ko', en='neither', words=['아니하였느니라']),
    # 에스겔 13:9  not neither neither / 못하게 못하게 못하게
    dict(ref=(25, 13, 9), lang='ko', en='not', words=['못하게#1']),
    dict(ref=(25, 13, 9), lang='ko', en='neither#1', words=['못하게#2']),
    dict(ref=(25, 13, 9), lang='ko', en='neither#2', words=['못하게#3']),
    # 에스겔 13:19  not not / 아니할 못할
    dict(ref=(25, 13, 19), lang='ko', en='not#1', words=['아니할']),
    dict(ref=(25, 13, 19), lang='ko', en='not#2', words=['못할']),
    # 에스겔 13:22  not not / 아니한 못하게
    dict(ref=(25, 13, 22), lang='ko', en='not#1', words=['아니한']),
    dict(ref=(25, 13, 22), lang='ko', en='not#2', words=['못하게']),
    # 에스겔 16:4  not neither not nor / 아니하였고 아니하였고 아니하였고 아니하였나니
    dict(ref=(25, 16, 4), lang='ko', en='not#1', words=['아니하였고#1']),
    dict(ref=(25, 16, 4), lang='ko', en='neither', words=['아니하였고#2']),
    dict(ref=(25, 16, 4), lang='ko', en='not#2', words=['아니하였고#3']),
    dict(ref=(25, 16, 4), lang='ko', en='nor', words=['아니하였나니']),
    # 에스겔 16:43  not not / 아니하고 아니하리라
    dict(ref=(25, 16, 43), lang='ko', en='not#1', words=['아니하고']),
    dict(ref=(25, 16, 43), lang='ko', en='not#2', words=['아니하리라']),
    # 에스겔 16:47  not nor / 아니하며 아니하고
    dict(ref=(25, 16, 47), lang='ko', en='not', words=['아니하며']),
    dict(ref=(25, 16, 47), lang='ko', en='nor', words=['아니하고']),
    # 에스겔 18:6  not neither neither neither / 아니하며 아니하며 아니하며 아니하며
    dict(ref=(25, 18, 6), lang='ko', en='not', words=['아니하며#1']),
    dict(ref=(25, 18, 6), lang='ko', en='neither#1', words=['아니하며#2']),
    dict(ref=(25, 18, 6), lang='ko', en='neither#2', words=['아니하며#3']),
    dict(ref=(25, 18, 6), lang='ko', en='neither#3', words=['아니하며#4']),
    # 에스겔 18:15  not neither not / 아니하며 아니하며 아니하며
    dict(ref=(25, 18, 15), lang='ko', en='not#1', words=['아니하며#1']),
    dict(ref=(25, 18, 15), lang='ko', en='neither', words=['아니하며#2']),
    dict(ref=(25, 18, 15), lang='ko', en='not#2', words=['아니하며#3']),
    # 에스겔 18:16  Neither not neither / 아니하며 아니하며 아니하고
    dict(ref=(25, 18, 16), lang='ko', en='Neither', words=['아니하며#1']),
    dict(ref=(25, 18, 16), lang='ko', en='not', words=['아니하며#2']),
    dict(ref=(25, 18, 16), lang='ko', en='neither', words=['아니하고']),
    # 에스겔 18:17  not nor not / 아니하며 아니하여 아니하고
    dict(ref=(25, 18, 17), lang='ko', en='not#1', words=['아니하며']),
    dict(ref=(25, 18, 17), lang='ko', en='nor', words=['아니하여']),
    dict(ref=(25, 18, 17), lang='ko', en='not#2', words=['아니하고']),
    # 에스겔 18:20  not neither / 아니할 아니하리니
    dict(ref=(25, 18, 20), lang='ko', en='not', words=['아니할']),
    dict(ref=(25, 18, 20), lang='ko', en='neither', words=['아니하리니']),
    # 에스겔 20:8  not not neither / 아니하고 아니하며 아니하므로
    dict(ref=(25, 20, 8), lang='ko', en='not#1', words=['아니하고']),
    dict(ref=(25, 20, 8), lang='ko', en='not#2', words=['아니하며']),
    dict(ref=(25, 20, 8), lang='ko', en='neither', words=['아니하므로']),
    # 에스겔 20:18  not neither nor / 말며 말며 말라
    dict(ref=(25, 20, 18), lang='ko', en='not', words=['말며#1']),
    dict(ref=(25, 20, 18), lang='ko', en='neither', words=['말며#2']),
    dict(ref=(25, 20, 18), lang='ko', en='nor', words=['말라']),
    # 에스겔 20:21  not neither / 아니하며 아니하였고
    dict(ref=(25, 20, 21), lang='ko', en='not', words=['아니하며']),
    dict(ref=(25, 20, 21), lang='ko', en='neither', words=['아니하였고']),
    # 에스겔 20:25  not not / 못한 못할
    dict(ref=(25, 20, 25), lang='ko', en='not#1', words=['못한']),
    dict(ref=(25, 20, 25), lang='ko', en='not#2', words=['못할']),
    # 에스겔 22:24  not nor / 못한 못한
    dict(ref=(25, 22, 24), lang='ko', en='not', words=['못한#1']),
    dict(ref=(25, 22, 24), lang='ko', en='nor', words=['못한#2']),
    # 에스겔 23:27  not nor / 못하게 못하게
    dict(ref=(25, 23, 27), lang='ko', en='not', words=['못하게#1']),
    dict(ref=(25, 23, 27), lang='ko', en='nor', words=['못하게#2']),
    # 에스겔 24:13  not not / 아니하니 아니하리라
    dict(ref=(25, 24, 13), lang='ko', en='not#1', words=['아니하니']),
    dict(ref=(25, 24, 13), lang='ko', en='not#2', words=['아니하리라']),
    # 에스겔 24:14  not neither neither / 아니하며 아니하며 아니하고
    dict(ref=(25, 24, 14), lang='ko', en='not', words=['아니하며#1']),
    dict(ref=(25, 24, 14), lang='ko', en='neither#1', words=['아니하며#2']),
    dict(ref=(25, 24, 14), lang='ko', en='neither#2', words=['아니하고']),
    # 에스겔 29:11  nor neither / 아니하며 아니하고
    dict(ref=(25, 29, 11), lang='ko', en='nor', words=['아니하며']),
    dict(ref=(25, 29, 11), lang='ko', en='neither', words=['아니하고']),
    # 에스겔 31:8  not not not nor / 못하며 못하며 못하며 못하였도다
    dict(ref=(25, 31, 8), lang='ko', en='not#1', words=['못하며#1']),
    dict(ref=(25, 31, 8), lang='ko', en='not#2', words=['못하며#2']),
    dict(ref=(25, 31, 8), lang='ko', en='not#3', words=['못하며#3']),
    dict(ref=(25, 31, 8), lang='ko', en='nor', words=['못하였도다']),
    # 에스겔 33:12  not not neither / 못할 못할 못하리라
    dict(ref=(25, 33, 12), lang='ko', en='not#1', words=['못할#1']),
    dict(ref=(25, 33, 12), lang='ko', en='not#2', words=['못할#2']),
    dict(ref=(25, 33, 12), lang='ko', en='neither', words=['못하리라']),
    # 에스겔 33:17  not not / 않다 아니하니라
    dict(ref=(25, 33, 17), lang='ko', en='not#1', words=['않다']),
    dict(ref=(25, 33, 17), lang='ko', en='not#2', words=['아니하니라']),
    # 에스겔 34:4  not neither neither neither neither / 아니하며 아니하며 아니하며 아니하며 아니하고
    dict(ref=(25, 34, 4), lang='ko', en='not', words=['아니하며#1']),
    dict(ref=(25, 34, 4), lang='ko', en='neither#1', words=['아니하며#2']),
    dict(ref=(25, 34, 4), lang='ko', en='neither#2', words=['아니하며#3']),
    dict(ref=(25, 34, 4), lang='ko', en='neither#3', words=['아니하며#4']),
    dict(ref=(25, 34, 4), lang='ko', en='neither#4', words=['아니하고']),
    # 에스겔 36:15  Neither neither neither / 않게 않게 않게
    dict(ref=(25, 36, 15), lang='ko', en='Neither', words=['않게#1']),
    dict(ref=(25, 36, 15), lang='ko', en='neither#1', words=['않게#2']),
    dict(ref=(25, 36, 15), lang='ko', en='neither#2', words=['않게#3']),
    # 에스겔 44:13  not nor / 못하게 못하게
    dict(ref=(25, 44, 13), lang='ko', en='not', words=['못하게#1']),
    dict(ref=(25, 44, 13), lang='ko', en='nor', words=['못하게#2']),
    # 에스겔 46:18  not not / 못할지니 않게
    dict(ref=(25, 46, 18), lang='ko', en='not#1', words=['못할지니']),
    dict(ref=(25, 46, 18), lang='ko', en='not#2', words=['않게']),
    # 에스겔 47:5  not not / 못할 못할
    dict(ref=(25, 47, 5), lang='ko', en='not#1', words=['못할#1']),
    dict(ref=(25, 47, 5), lang='ko', en='not#2', words=['못할#2']),
    # 에스겔 47:12  not neither / 아니하며 아니하고
    dict(ref=(25, 47, 12), lang='ko', en='not', words=['아니하며']),
    dict(ref=(25, 47, 12), lang='ko', en='neither', words=['아니하고']),
    # 에스겔 48:14  not neither nor / 못하며 못하며 못하리니
    dict(ref=(25, 48, 14), lang='ko', en='not', words=['못하며#1']),
    dict(ref=(25, 48, 14), lang='ko', en='neither', words=['못하며#2']),
    dict(ref=(25, 48, 14), lang='ko', en='nor', words=['못하리니']),
    # 다니엘 1:8  not nor not / 마시는 아니하리라 않게
    # 다니엘 2:10  not nor / 없으므로 아니하였나이다
    dict(ref=(26, 2, 10), lang='ko', en='not', words=['없으므로']),
    dict(ref=(26, 2, 10), lang='ko', en='nor', words=['아니하였나이다']),
    # 다니엘 2:43  not not / 아니함이 않음과
    dict(ref=(26, 2, 43), lang='ko', en='not#1', words=['아니함이']),
    dict(ref=(26, 2, 43), lang='ko', en='not#2', words=['않음과']),
    # 다니엘 2:44  never not / 아니할 아니할
    dict(ref=(26, 2, 44), lang='ko', en='never', words=['아니할#1']),
    dict(ref=(26, 2, 44), lang='ko', en='not', words=['아니할#2']),
    # 다니엘 3:12  not not nor / 아니하며 아니하며 아니하나이다
    dict(ref=(26, 3, 12), lang='ko', en='not#1', words=['아니하며#1']),
    dict(ref=(26, 3, 12), lang='ko', en='not#2', words=['아니하며#2']),
    dict(ref=(26, 3, 12), lang='ko', en='nor', words=['아니하나이다']),
    # 다니엘 3:14  not nor / 아니하며 아니하니
    dict(ref=(26, 3, 14), lang='ko', en='not', words=['아니하며']),
    dict(ref=(26, 3, 14), lang='ko', en='nor', words=['아니하니']),
    # 다니엘 3:18  not not nor / 아니하실지라도 아니하고 아니할
    dict(ref=(26, 3, 18), lang='ko', en='not#1', words=['아니하실지라도']),
    dict(ref=(26, 3, 18), lang='ko', en='not#2', words=['아니하고']),
    dict(ref=(26, 3, 18), lang='ko', en='nor', words=['아니할']),
    # 다니엘 3:27  nor neither nor / 못하였고 아니하였고 아니하였고
    dict(ref=(26, 3, 27), lang='ko', en='nor#1', words=['못하였고']),
    dict(ref=(26, 3, 27), lang='ko', en='neither', words=['아니하였고#1']),
    dict(ref=(26, 3, 27), lang='ko', en='nor#2', words=['아니하였고#2']),
    # 다니엘 3:28  not nor / 아니하며 아니한
    dict(ref=(26, 3, 28), lang='ko', en='not', words=['아니하며']),
    dict(ref=(26, 3, 28), lang='ko', en='nor', words=['아니한']),
    # 다니엘 5:8  not nor / 못하여 못하는지라
    dict(ref=(26, 5, 8), lang='ko', en='not', words=['못하여']),
    dict(ref=(26, 5, 8), lang='ko', en='nor', words=['못하는지라']),
    # 다니엘 5:10  not nor / 말며 아니니이다
    dict(ref=(26, 5, 10), lang='ko', en='not', words=['말며']),
    dict(ref=(26, 5, 10), lang='ko', en='nor', words=['아니니이다']),
    # 다니엘 6:4  nor neither / 못하였으니 없음이었더라
    dict(ref=(26, 6, 4), lang='ko', en='nor', words=['못하였으니']),
    dict(ref=(26, 6, 4), lang='ko', en='neither', words=['없음이었더라']),
    # 다니엘 6:8  not not / 아니하는 못하게
    dict(ref=(26, 6, 8), lang='ko', en='not#1', words=['아니하는']),
    dict(ref=(26, 6, 8), lang='ko', en='not#2', words=['못하게']),
    # 다니엘 6:12  not not / 아니하였나이까 아니하는
    dict(ref=(26, 6, 12), lang='ko', en='not#1', words=['아니하였나이까']),
    dict(ref=(26, 6, 12), lang='ko', en='not#2', words=['아니하는']),
    # 다니엘 7:14  not not / 아니할 아니할
    dict(ref=(26, 7, 14), lang='ko', en='not#1', words=['아니할#1']),
    dict(ref=(26, 7, 14), lang='ko', en='not#2', words=['아니할#2']),
    # 다니엘 10:3  neither nor neither / 아니하며 아니하며 아니하니라
    dict(ref=(26, 10, 3), lang='ko', en='neither#1', words=['아니하며#1']),
    dict(ref=(26, 10, 3), lang='ko', en='nor', words=['아니하며#2']),
    dict(ref=(26, 10, 3), lang='ko', en='neither#2', words=['아니하니라']),
    # 다니엘 11:4  not nor / 아니할 아니하리니
    dict(ref=(26, 11, 4), lang='ko', en='not', words=['아니할']),
    dict(ref=(26, 11, 4), lang='ko', en='nor', words=['아니하리니']),
    # 다니엘 11:6  not neither nor / 못하며 없어질 아니라
    dict(ref=(26, 11, 6), lang='ko', en='not', words=['못하며']),
    dict(ref=(26, 11, 6), lang='ko', en='neither', words=['없어질']),
    dict(ref=(26, 11, 6), lang='ko', en='nor', words=['아니라']),
    # 호세아 1:9  not not / 아니요 아니할
    dict(ref=(27, 1, 9), lang='ko', en='not#1', words=['아니요']),
    dict(ref=(27, 1, 9), lang='ko', en='not#2', words=['아니할']),
    # 호세아 2:2  not neither / 아니요 아니라
    dict(ref=(27, 2, 2), lang='ko', en='not', words=['아니요']),
    dict(ref=(27, 2, 2), lang='ko', en='neither', words=['아니라']),
    # 호세아 2:7  not not / 못하며 못할
    dict(ref=(27, 2, 7), lang='ko', en='not#1', words=['못하며']),
    dict(ref=(27, 2, 7), lang='ko', en='not#2', words=['못할']),
    # 호세아 2:23  not not / 못하였던 아니었던
    dict(ref=(27, 2, 23), lang='ko', en='not#1', words=['못하였던']),
    dict(ref=(27, 2, 23), lang='ko', en='not#2', words=['아니었던']),
    # 호세아 3:3  not not / 말며 말라
    dict(ref=(27, 3, 3), lang='ko', en='not#1', words=['말며']),
    dict(ref=(27, 3, 3), lang='ko', en='not#2', words=['말라']),
    # 호세아 4:10  not not / 아니하며 못하니
    dict(ref=(27, 4, 10), lang='ko', en='not#1', words=['아니하며']),
    dict(ref=(27, 4, 10), lang='ko', en='not#2', words=['못하니']),
    # 호세아 4:15  not not neither nor / 말아야 말며 말며 말지어다
    dict(ref=(27, 4, 15), lang='ko', en='not#1', words=['말아야']),
    dict(ref=(27, 4, 15), lang='ko', en='not#2', words=['말며#1']),
    dict(ref=(27, 4, 15), lang='ko', en='neither', words=['말며#2']),
    dict(ref=(27, 4, 15), lang='ko', en='nor', words=['말지어다']),
    # 호세아 5:4  not not / 못하게 못하는
    dict(ref=(27, 5, 4), lang='ko', en='not#1', words=['못하게']),
    dict(ref=(27, 5, 4), lang='ko', en='not#2', words=['못하는']),
    # 호세아 5:13  not nor / 못하겠고 못하리라
    dict(ref=(27, 5, 13), lang='ko', en='not', words=['못하겠고']),
    dict(ref=(27, 5, 13), lang='ko', en='nor', words=['못하리라']),
    # 호세아 7:9  not not / 못하고 못하는도다
    dict(ref=(27, 7, 9), lang='ko', en='not#1', words=['못하고']),
    dict(ref=(27, 7, 9), lang='ko', en='not#2', words=['못하는도다']),
    # 호세아 7:10  not nor / 아니하며 아니하도다
    dict(ref=(27, 7, 10), lang='ko', en='not', words=['아니하며']),
    dict(ref=(27, 7, 10), lang='ko', en='nor', words=['아니하도다']),
    # 호세아 11:9  not not not not / 아니하며 아니하리니 아니요 아니하리라
    dict(ref=(27, 11, 9), lang='ko', en='not#1', words=['아니하며']),
    dict(ref=(27, 11, 9), lang='ko', en='not#2', words=['아니하리니']),
    dict(ref=(27, 11, 9), lang='ko', en='not#3', words=['아니요']),
    dict(ref=(27, 11, 9), lang='ko', en='not#4', words=['아니하리라']),
    # 호세아 14:3  not not neither / 아니하며 아니하며 아니하오리니
    dict(ref=(27, 14, 3), lang='ko', en='not#1', words=['아니하며#1']),
    dict(ref=(27, 14, 3), lang='ko', en='not#2', words=['아니하며#2']),
    dict(ref=(27, 14, 3), lang='ko', en='neither', words=['아니하오리니']),
    # 요엘 2:8  Neither not / 아니하고 아니하며
    dict(ref=(28, 2, 8), lang='ko', en='Neither', words=['아니하고']),
    dict(ref=(28, 2, 8), lang='ko', en='not', words=['아니하며']),
    # 아모스 1:9  not not / 아니하리니 아니하고
    dict(ref=(29, 1, 9), lang='ko', en='not#1', words=['아니하리니']),
    dict(ref=(29, 1, 9), lang='ko', en='not#2', words=['아니하고']),
    # 아모스 2:4  not not / 아니하리니 아니하고
    dict(ref=(29, 2, 4), lang='ko', en='not#1', words=['아니하리니']),
    dict(ref=(29, 2, 4), lang='ko', en='not#2', words=['아니하고']),
    # 아모스 3:6  not not / 아니하겠으며 아니고야
    dict(ref=(29, 3, 6), lang='ko', en='not#1', words=['아니하겠으며']),
    dict(ref=(29, 3, 6), lang='ko', en='not#2', words=['아니고야']),
    # 아모스 4:7  not not / 않게 못하여
    dict(ref=(29, 4, 7), lang='ko', en='not#1', words=['않게']),
    dict(ref=(29, 4, 7), lang='ko', en='not#2', words=['못하여']),
    # 아모스 5:5  not nor not / 말며 말며 말라
    dict(ref=(29, 5, 5), lang='ko', en='not#1', words=['말며#1']),
    dict(ref=(29, 5, 5), lang='ko', en='nor', words=['말며#2']),
    dict(ref=(29, 5, 5), lang='ko', en='not#2', words=['말라']),
    # 아모스 5:22  not neither / 아니할 아니하리라
    dict(ref=(29, 5, 22), lang='ko', en='not', words=['아니할']),
    dict(ref=(29, 5, 22), lang='ko', en='neither', words=['아니하리라']),
    # 아모스 7:16  not not / 말며 말라
    dict(ref=(29, 7, 16), lang='ko', en='not#1', words=['말며']),
    dict(ref=(29, 7, 16), lang='ko', en='not#2', words=['말라']),
    # 아모스 9:1  not not / 못하며 못하리라
    dict(ref=(29, 9, 1), lang='ko', en='not#1', words=['못하며']),
    dict(ref=(29, 9, 1), lang='ko', en='not#2', words=['못하리라']),
    # 아모스 9:7  not not / 아니하냐 아니하였느냐
    dict(ref=(29, 9, 7), lang='ko', en='not#1', words=['아니하냐']),
    dict(ref=(29, 9, 7), lang='ko', en='not#2', words=['아니하였느냐']),
    # 오바댜 1:14  Neither neither / 않을 않을
    dict(ref=(30, 1, 14), lang='ko', en='Neither', words=['않을#1']),
    dict(ref=(30, 1, 14), lang='ko', en='neither', words=['않을#2']),
    # 요나 1:14  not not / 마옵소서 마옵소서
    dict(ref=(31, 1, 14), lang='ko', en='not#1', words=['마옵소서#1']),
    dict(ref=(31, 1, 14), lang='ko', en='not#2', words=['마옵소서#2']),
    # 요나 4:10  not neither / 아니하였고 아니하였고
    dict(ref=(31, 4, 10), lang='ko', en='not', words=['아니하였고#1']),
    dict(ref=(31, 4, 10), lang='ko', en='neither', words=['아니하였고#2']),
    # 요나 4:11  not cannot / 못하는 아니하냐
    dict(ref=(31, 4, 11), lang='ko', en='not', words=['못하는']),
    dict(ref=(31, 4, 11), lang='ko', en='cannot', words=['아니하냐']),
    # 미가 1:5  not not / 아니뇨 아니뇨
    dict(ref=(32, 1, 5), lang='ko', en='not#1', words=['아니뇨#1']),
    dict(ref=(32, 1, 5), lang='ko', en='not#2', words=['아니뇨#2']),
    # 미가 1:10  not not / 말며 말지어다
    dict(ref=(32, 1, 10), lang='ko', en='not#1', words=['말며']),
    dict(ref=(32, 1, 10), lang='ko', en='not#2', words=['말지어다']),
    # 미가 2:3  not neither / 못할 못할
    dict(ref=(32, 2, 3), lang='ko', en='not', words=['못할#1']),
    dict(ref=(32, 2, 3), lang='ko', en='neither', words=['못할#2']),
    # 미가 2:6  not not not / 말라 아니어늘 아니한다
    dict(ref=(32, 2, 6), lang='ko', en='not#1', words=['말라']),
    dict(ref=(32, 2, 6), lang='ko', en='not#2', words=['아니어늘']),
    dict(ref=(32, 2, 6), lang='ko', en='not#3', words=['아니한다']),
    # 미가 3:6  not not / 못할 못하리라
    dict(ref=(32, 3, 6), lang='ko', en='not#1', words=['못할']),
    dict(ref=(32, 3, 6), lang='ko', en='not#2', words=['못하리라']),
    # 미가 4:3  not neither / 아니하며 아니하고
    dict(ref=(32, 4, 3), lang='ko', en='not', words=['아니하며']),
    dict(ref=(32, 4, 3), lang='ko', en='neither', words=['아니하고']),
    # 미가 4:12  not neither / 못하며 못한
    dict(ref=(32, 4, 12), lang='ko', en='not', words=['못하며']),
    dict(ref=(32, 4, 12), lang='ko', en='neither', words=['못한']),
    # 미가 5:7  not nor / 아니하며 아니할
    dict(ref=(32, 5, 7), lang='ko', en='not', words=['아니하며']),
    dict(ref=(32, 5, 7), lang='ko', en='nor', words=['아니할']),
    # 미가 6:14  not not / 못하고 못하겠고
    dict(ref=(32, 6, 14), lang='ko', en='not#1', words=['못하고']),
    dict(ref=(32, 6, 14), lang='ko', en='not#2', words=['못하겠고']),
    # 미가 7:5  not not / 말며 말며
    dict(ref=(32, 7, 5), lang='ko', en='not#1', words=['말며#1']),
    dict(ref=(32, 7, 5), lang='ko', en='not#2', words=['말며#2']),
    # 하박국 2:3  not not / 아니하리라 않고
    dict(ref=(34, 2, 3), lang='ko', en='not#1', words=['아니하리라']),
    dict(ref=(34, 2, 3), lang='ko', en='not#2', words=['않고']),
    # 스바냐 1:12  not neither / 아니하시며 아니하시리라
    dict(ref=(35, 1, 12), lang='ko', en='not', words=['아니하시며']),
    dict(ref=(35, 1, 12), lang='ko', en='neither', words=['아니하시리라']),
    # 스바냐 3:2  not not not not / 아니하며 아니하며 아니하며 아니하였도다
    dict(ref=(35, 3, 2), lang='ko', en='not#1', words=['아니하며#1']),
    dict(ref=(35, 3, 2), lang='ko', en='not#2', words=['아니하며#2']),
    dict(ref=(35, 3, 2), lang='ko', en='not#3', words=['아니하며#3']),
    dict(ref=(35, 3, 2), lang='ko', en='not#4', words=['아니하였도다']),
    # 스바냐 3:5  not not / 아니하시고 못하는도다
    dict(ref=(35, 3, 5), lang='ko', en='not#1', words=['아니하시고']),
    dict(ref=(35, 3, 5), lang='ko', en='not#2', words=['못하는도다']),
    # 스바냐 3:16  not not / 말라 말라
    dict(ref=(35, 3, 16), lang='ko', en='not#1', words=['말라#1']),
    dict(ref=(35, 3, 16), lang='ko', en='not#2', words=['말라#2']),
    # 스가랴 1:4  not not nor / 말라 않고 아니하였느니라
    dict(ref=(37, 1, 4), lang='ko', en='not#1', words=['말라']),
    dict(ref=(37, 1, 4), lang='ko', en='not#2', words=['않고']),
    dict(ref=(37, 1, 4), lang='ko', en='nor', words=['아니하였느니라']),
    # 스가랴 4:6  Not nor / 아니하며 아니하고
    dict(ref=(37, 4, 6), lang='ko', en='Not', words=['아니하며']),
    dict(ref=(37, 4, 6), lang='ko', en='nor', words=['아니하고']),
    # 스가랴 7:13  not not / 아니하였은즉 아니하고
    dict(ref=(37, 7, 13), lang='ko', en='not#1', words=['아니하였은즉']),
    dict(ref=(37, 7, 13), lang='ko', en='not#2', words=['아니하고']),
    # 스가랴 14:7  not nor / 아니요 아니라
    dict(ref=(37, 14, 7), lang='ko', en='not', words=['아니요']),
    dict(ref=(37, 14, 7), lang='ko', en='nor', words=['아니라']),
    # 스가랴 14:18  not not not / 아니할 아니하리니 아니하는
    dict(ref=(37, 14, 18), lang='ko', en='not#1', words=['아니할']),
    dict(ref=(37, 14, 18), lang='ko', en='not#2', words=['아니하리니']),
    dict(ref=(37, 14, 18), lang='ko', en='not#3', words=['아니하는']),
    # 말라기 1:8  not not / 아니하며 아니하냐
    dict(ref=(38, 1, 8), lang='ko', en='not#1', words=['아니하며']),
    dict(ref=(38, 1, 8), lang='ko', en='not#2', words=['아니하냐']),
    # 말라기 2:10  not not / 아니하였느냐 아니냐
    dict(ref=(38, 2, 10), lang='ko', en='not#1', words=['아니하였느냐']),
    dict(ref=(38, 2, 10), lang='ko', en='not#2', words=['아니냐']),
    # 말라기 3:6  not not / 아니하나니 아니하느니라
    dict(ref=(38, 3, 6), lang='ko', en='not#1', words=['아니하나니']),
    dict(ref=(38, 3, 6), lang='ko', en='not#2', words=['아니하느니라']),
    # 말라기 3:11  not neither / 않게 않게
    dict(ref=(38, 3, 11), lang='ko', en='not', words=['않게#1']),
    dict(ref=(38, 3, 11), lang='ko', en='neither', words=['않게#2']),
    # 마태복음 5:17  not not / 말라 아니요
    dict(ref=(39, 5, 17), lang='ko', en='not#1', words=['말라']),
    dict(ref=(39, 5, 17), lang='ko', en='not#2', words=['아니요']),
    # 마태복음 5:35  Nor neither / 말라 말라
    dict(ref=(39, 5, 35), lang='ko', en='Nor', words=['말라#1']),
    dict(ref=(39, 5, 35), lang='ko', en='neither', words=['말라#2']),
    # 마태복음 5:36  Neither not / 말라 없음이라
    dict(ref=(39, 5, 36), lang='ko', en='Neither', words=['말라']),
    dict(ref=(39, 5, 36), lang='ko', en='not', words=['없음이라']),
    # 마태복음 6:15  not neither / 아니하면 아니하시리라
    dict(ref=(39, 6, 15), lang='ko', en='not', words=['아니하면']),
    dict(ref=(39, 6, 15), lang='ko', en='neither', words=['아니하시리라']),
    # 마태복음 6:26  not neither nor not / 않고 않고 아니하되 아니하냐
    dict(ref=(39, 6, 26), lang='ko', en='not#1', words=['않고#1']),
    dict(ref=(39, 6, 26), lang='ko', en='neither', words=['않고#2']),
    dict(ref=(39, 6, 26), lang='ko', en='nor', words=['아니하되']),
    dict(ref=(39, 6, 26), lang='ko', en='not#2', words=['아니하냐']),
    # 마태복음 6:28  not neither / 아니하고 아니하느니라
    dict(ref=(39, 6, 28), lang='ko', en='not', words=['아니하고']),
    dict(ref=(39, 6, 28), lang='ko', en='neither', words=['아니하느니라']),
    # 마태복음 7:1  not not / 아니하려거든 말라
    dict(ref=(39, 7, 1), lang='ko', en='not#1', words=['아니하려거든']),
    dict(ref=(39, 7, 1), lang='ko', en='not#2', words=['말라']),
    # 마태복음 7:6  not neither / 말며 말라
    dict(ref=(39, 7, 6), lang='ko', en='not', words=['말며']),
    dict(ref=(39, 7, 6), lang='ko', en='neither', words=['말라']),
    # 마태복음 7:18  cannot neither / 못된 없느니라
    # 마태복음 9:13  not not / 아니하노라 아니요
    dict(ref=(39, 9, 13), lang='ko', en='not#1', words=['아니하노라']),
    dict(ref=(39, 9, 13), lang='ko', en='not#2', words=['아니요']),
    # 마태복음 10:5  not not / 말고 말고
    dict(ref=(39, 10, 5), lang='ko', en='not#1', words=['말고#1']),
    dict(ref=(39, 10, 5), lang='ko', en='not#2', words=['말고#2']),
    # 마태복음 10:14  not nor / 아니하고 아니하거든
    dict(ref=(39, 10, 14), lang='ko', en='not', words=['아니하고']),
    dict(ref=(39, 10, 14), lang='ko', en='nor', words=['아니하거든']),
    # 마태복음 10:28  not not / 못하는 말고
    dict(ref=(39, 10, 28), lang='ko', en='not#1', words=['못하는']),
    dict(ref=(39, 10, 28), lang='ko', en='not#2', words=['말고']),
    # 마태복음 10:34  not not / 말라 아니요
    dict(ref=(39, 10, 34), lang='ko', en='not#1', words=['말라']),
    dict(ref=(39, 10, 34), lang='ko', en='not#2', words=['아니요']),
    # 마태복음 10:37  not not / 아니하고 아니하고
    dict(ref=(39, 10, 37), lang='ko', en='not#1', words=['아니하고#1']),
    dict(ref=(39, 10, 37), lang='ko', en='not#2', words=['아니하고#2']),
    # 마태복음 10:38  not not / 않는 아니하니라
    dict(ref=(39, 10, 38), lang='ko', en='not#1', words=['않는']),
    dict(ref=(39, 10, 38), lang='ko', en='not#2', words=['아니하니라']),
    # 마태복음 11:17  not not / 않고 아니하였다
    dict(ref=(39, 11, 17), lang='ko', en='not#1', words=['않고']),
    dict(ref=(39, 11, 17), lang='ko', en='not#2', words=['아니하였다']),
    # 마태복음 12:4  not neither / 못하는 아니하였느냐
    dict(ref=(39, 12, 4), lang='ko', en='not', words=['못하는']),
    dict(ref=(39, 12, 4), lang='ko', en='neither', words=['아니하였느냐']),
    # 마태복음 12:7  not not / 아니하노라 아니하였으리라
    dict(ref=(39, 12, 7), lang='ko', en='not#1', words=['아니하노라']),
    dict(ref=(39, 12, 7), lang='ko', en='not#2', words=['아니하였으리라']),
    # 마태복음 12:19  not nor neither / 아니하며 아니하리니 못하리라
    dict(ref=(39, 12, 19), lang='ko', en='not', words=['아니하며']),
    dict(ref=(39, 12, 19), lang='ko', en='nor', words=['아니하리니']),
    dict(ref=(39, 12, 19), lang='ko', en='neither', words=['못하리라']),
    # 마태복음 12:20  not not / 아니하며 아니하기를
    dict(ref=(39, 12, 20), lang='ko', en='not#1', words=['아니하며']),
    dict(ref=(39, 12, 20), lang='ko', en='not#2', words=['아니하기를']),
    # 마태복음 12:30  not not / 아니하는 아니하는
    dict(ref=(39, 12, 30), lang='ko', en='not#1', words=['아니하는#1']),
    dict(ref=(39, 12, 30), lang='ko', en='not#2', words=['아니하는#2']),
    # 마태복음 13:13  not not neither / 못하며 못하며 못함이니라
    dict(ref=(39, 13, 13), lang='ko', en='not#1', words=['못하며#1']),
    dict(ref=(39, 13, 13), lang='ko', en='not#2', words=['못하며#2']),
    dict(ref=(39, 13, 13), lang='ko', en='neither', words=['못함이니라']),
    # 마태복음 13:14  not not / 못할 못하리라
    dict(ref=(39, 13, 14), lang='ko', en='not#1', words=['못할']),
    dict(ref=(39, 13, 14), lang='ko', en='not#2', words=['못하리라']),
    # 마태복음 13:17  not not / 못하였고 못하였느니라
    dict(ref=(39, 13, 17), lang='ko', en='not#1', words=['못하였고']),
    dict(ref=(39, 13, 17), lang='ko', en='not#2', words=['못하였느니라']),
    # 마태복음 13:55  not not / 아니냐 않느냐
    dict(ref=(39, 13, 55), lang='ko', en='not#1', words=['아니냐']),
    dict(ref=(39, 13, 55), lang='ko', en='not#2', words=['않느냐']),
    # 마태복음 21:21  not not / 아니하면 아니라
    dict(ref=(39, 21, 21), lang='ko', en='not#1', words=['아니하면']),
    dict(ref=(39, 21, 21), lang='ko', en='not#2', words=['아니라']),
    # 마태복음 21:32  not not / 아니하였으되 아니하였도다
    dict(ref=(39, 21, 32), lang='ko', en='not#1', words=['아니하였으되']),
    dict(ref=(39, 21, 32), lang='ko', en='not#2', words=['아니하였도다']),
    # 마태복음 22:16  neither not / 없으시니 아니하심이니이다
    dict(ref=(39, 22, 16), lang='ko', en='neither', words=['없으시니']),
    dict(ref=(39, 22, 16), lang='ko', en='not', words=['아니하심이니이다']),
    # 마태복음 22:30  neither nor / 아니가고 아니가고
    dict(ref=(39, 22, 30), lang='ko', en='neither', words=['아니가고#1']),
    dict(ref=(39, 22, 30), lang='ko', en='nor', words=['아니가고#2']),
    # 마태복음 23:13  neither neither / 않고 못하게
    dict(ref=(39, 23, 13), lang='ko', en='neither#1', words=['않고']),
    dict(ref=(39, 23, 13), lang='ko', en='neither#2', words=['못하게']),
    # 마태복음 24:6  not not / 말라 아니니라
    dict(ref=(39, 24, 6), lang='ko', en='not#1', words=['말라']),
    dict(ref=(39, 24, 6), lang='ko', en='not#2', words=['아니니라']),
    # 마태복음 24:26  not not / 말고 말라
    dict(ref=(39, 24, 26), lang='ko', en='not#1', words=['말고']),
    dict(ref=(39, 24, 26), lang='ko', en='not#2', words=['말라']),
    # 마태복음 24:50  not not / 않은 못하는
    dict(ref=(39, 24, 50), lang='ko', en='not#1', words=['않은']),
    dict(ref=(39, 24, 50), lang='ko', en='not#2', words=['못하는']),
    # 마태복음 25:24  not not / 않은 않은
    dict(ref=(39, 25, 24), lang='ko', en='not#1', words=['않은#1']),
    dict(ref=(39, 25, 24), lang='ko', en='not#2', words=['않은#2']),
    # 마태복음 25:26  not not / 않은 않은
    dict(ref=(39, 25, 26), lang='ko', en='not#1', words=['않은#1']),
    dict(ref=(39, 25, 26), lang='ko', en='not#2', words=['않은#2']),
    # 마태복음 25:43  not not not / 아니하였고 아니하였고 아니하였느니라
    dict(ref=(39, 25, 43), lang='ko', en='not#1', words=['아니하였고#1']),
    dict(ref=(39, 25, 43), lang='ko', en='not#2', words=['아니하였고#2']),
    dict(ref=(39, 25, 43), lang='ko', en='not#3', words=['아니하였느니라']),
    # 마태복음 25:45  not not / 아니한 아니한
    dict(ref=(39, 25, 45), lang='ko', en='not#1', words=['아니한#1']),
    dict(ref=(39, 25, 45), lang='ko', en='not#2', words=['아니한#2']),
    # 마가복음 6:11  not nor / 아니하고 아니하거든
    dict(ref=(40, 6, 11), lang='ko', en='not', words=['아니하고']),
    dict(ref=(40, 6, 11), lang='ko', en='nor', words=['아니하거든']),
    # 마가복음 8:18  not not not / 못하며 못하느냐 못하느냐
    dict(ref=(40, 8, 18), lang='ko', en='not#1', words=['못하며']),
    dict(ref=(40, 8, 18), lang='ko', en='not#2', words=['못하느냐#1']),
    dict(ref=(40, 8, 18), lang='ko', en='not#3', words=['못하느냐#2']),
    # 마가복음 9:38  not not / 않는 아니하므로
    dict(ref=(40, 9, 38), lang='ko', en='not#1', words=['않는']),
    dict(ref=(40, 9, 38), lang='ko', en='not#2', words=['아니하므로']),
    # 마가복음 9:48  not not / 않고 아니하느니라
    dict(ref=(40, 9, 48), lang='ko', en='not#1', words=['않고']),
    dict(ref=(40, 9, 48), lang='ko', en='not#2', words=['아니하느니라']),
    # 마가복음 10:15  not not / 않는 못하리라
    dict(ref=(40, 10, 15), lang='ko', en='not#1', words=['않는']),
    dict(ref=(40, 10, 15), lang='ko', en='not#2', words=['못하리라']),
    # 마가복음 10:19  not not not not not / 말라 말라 말라 말라 말라
    dict(ref=(40, 10, 19), lang='ko', en='not#1', words=['말라#1']),
    dict(ref=(40, 10, 19), lang='ko', en='not#2', words=['말라#2']),
    dict(ref=(40, 10, 19), lang='ko', en='not#3', words=['말라#3']),
    dict(ref=(40, 10, 19), lang='ko', en='not#4', words=['말라#4']),
    dict(ref=(40, 10, 19), lang='ko', en='not#5', words=['말라#5']),
    # 마가복음 11:33  cannot Neither / 못하노라 아니하리라
    dict(ref=(40, 11, 33), lang='ko', en='cannot', words=['못하노라']),
    dict(ref=(40, 11, 33), lang='ko', en='Neither', words=['아니하리라']),
    # 마가복음 12:14  not not / 없으시니 않고
    dict(ref=(40, 12, 14), lang='ko', en='not#1', words=['없으시니']),
    dict(ref=(40, 12, 14), lang='ko', en='not#2', words=['않고']),
    # 마가복음 12:25  neither nor / 아니가고 아니가고
    dict(ref=(40, 12, 25), lang='ko', en='neither', words=['아니가고#1']),
    dict(ref=(40, 12, 25), lang='ko', en='nor', words=['아니가고#2']),
    # 마가복음 13:7  not not / 말라 아니니라
    dict(ref=(40, 13, 7), lang='ko', en='not#1', words=['말라']),
    dict(ref=(40, 13, 7), lang='ko', en='not#2', words=['아니니라']),
    # 마가복음 13:11  neither not / 말고 아니요
    dict(ref=(40, 13, 11), lang='ko', en='neither', words=['말고']),
    dict(ref=(40, 13, 11), lang='ko', en='not', words=['아니요']),
    # 마가복음 13:15  not neither / 말고 말며
    dict(ref=(40, 13, 15), lang='ko', en='not', words=['말고']),
    dict(ref=(40, 13, 15), lang='ko', en='neither', words=['말며']),
    # 마가복음 14:68  not neither / 못하고 못하겠노라
    dict(ref=(40, 14, 68), lang='ko', en='not', words=['못하고']),
    dict(ref=(40, 14, 68), lang='ko', en='neither', words=['못하겠노라']),
    # 누가복음 1:15  neither nor / 마시지 아니하며
    # 누가복음 1:20  not not / 못하리니 아니함이어니와
    dict(ref=(41, 1, 20), lang='ko', en='not#1', words=['못하리니']),
    dict(ref=(41, 1, 20), lang='ko', en='not#2', words=['아니함이어니와']),
    # 누가복음 6:37  not not not not / 말라 않을 말라 않을
    dict(ref=(41, 6, 37), lang='ko', en='not#1', words=['말라#1']),
    dict(ref=(41, 6, 37), lang='ko', en='not#2', words=['않을#1']),
    dict(ref=(41, 6, 37), lang='ko', en='not#3', words=['말라#2']),
    dict(ref=(41, 6, 37), lang='ko', en='not#4', words=['않을#2']),
    # 누가복음 7:6  not not not / 아니하여 마옵소서 못하겠나이다
    dict(ref=(41, 7, 6), lang='ko', en='not#1', words=['아니하여']),
    dict(ref=(41, 7, 6), lang='ko', en='not#2', words=['마옵소서']),
    dict(ref=(41, 7, 6), lang='ko', en='not#3', words=['못하겠나이다']),
    # 누가복음 7:32  not not / 않고 아니하였다
    dict(ref=(41, 7, 32), lang='ko', en='not#1', words=['않고']),
    dict(ref=(41, 7, 32), lang='ko', en='not#2', words=['아니하였다']),
    # 누가복음 8:10  not not / 못하고 못하게
    dict(ref=(41, 8, 10), lang='ko', en='not#1', words=['못하고']),
    dict(ref=(41, 8, 10), lang='ko', en='not#2', words=['못하게']),
    # 누가복음 8:17  not neither not / 아니할 않을 없느니라
    dict(ref=(41, 8, 17), lang='ko', en='not#1', words=['아니할']),
    dict(ref=(41, 8, 17), lang='ko', en='neither', words=['않을']),
    dict(ref=(41, 8, 17), lang='ko', en='not#2', words=['없느니라']),
    # 누가복음 8:52  not not / 말라 아니라
    dict(ref=(41, 8, 52), lang='ko', en='not#1', words=['말라']),
    dict(ref=(41, 8, 52), lang='ko', en='not#2', words=['아니라']),
    # 누가복음 9:45  not not / 못하였나니 못하게
    dict(ref=(41, 9, 45), lang='ko', en='not#1', words=['못하였나니']),
    dict(ref=(41, 9, 45), lang='ko', en='not#2', words=['못하게']),
    # 누가복음 9:50  not not / 말라 않는
    dict(ref=(41, 9, 50), lang='ko', en='not#1', words=['말라']),
    dict(ref=(41, 9, 50), lang='ko', en='not#2', words=['않는']),
    # 누가복음 10:24  not not / 못하였으며 못하였느니라
    dict(ref=(41, 10, 24), lang='ko', en='not#1', words=['못하였으며']),
    dict(ref=(41, 10, 24), lang='ko', en='not#2', words=['못하였느니라']),
    # 누가복음 11:23  not not / 아니하는 아니하는
    dict(ref=(41, 11, 23), lang='ko', en='not#1', words=['아니하는#1']),
    dict(ref=(41, 11, 23), lang='ko', en='not#2', words=['아니하는#2']),
    # 누가복음 12:2  not neither not / 않을 않을 없나니
    dict(ref=(41, 12, 2), lang='ko', en='not#1', words=['않을#1']),
    dict(ref=(41, 12, 2), lang='ko', en='neither', words=['않을#2']),
    dict(ref=(41, 12, 2), lang='ko', en='not#2', words=['없나니']),
    # 누가복음 12:6  not not / 아니냐 아니하는도다
    dict(ref=(41, 12, 6), lang='ko', en='not#1', words=['아니냐']),
    dict(ref=(41, 12, 6), lang='ko', en='not#2', words=['아니하는도다']),
    # 누가복음 12:27  not not not / 않고 아니하느니라 못하였느니라
    dict(ref=(41, 12, 27), lang='ko', en='not#1', words=['않고']),
    dict(ref=(41, 12, 27), lang='ko', en='not#2', words=['아니하느니라']),
    dict(ref=(41, 12, 27), lang='ko', en='not#3', words=['못하였느니라']),
    # 누가복음 12:29  not neither / 말며 말라
    dict(ref=(41, 12, 29), lang='ko', en='not', words=['말며']),
    dict(ref=(41, 12, 29), lang='ko', en='neither', words=['말라']),
    # 누가복음 12:47  not neither / 아니하고 아니한
    dict(ref=(41, 12, 47), lang='ko', en='not', words=['아니하고']),
    dict(ref=(41, 12, 47), lang='ko', en='neither', words=['아니한']),
    # 누가복음 14:26  not cannot / 아니하면 못하고
    dict(ref=(41, 14, 26), lang='ko', en='not', words=['아니하면']),
    dict(ref=(41, 14, 26), lang='ko', en='cannot', words=['못하고']),
    # 누가복음 14:27  not cannot / 않는 못하리라
    dict(ref=(41, 14, 27), lang='ko', en='not', words=['않는']),
    dict(ref=(41, 14, 27), lang='ko', en='cannot', words=['못하리라']),
    # 누가복음 14:33  not cannot / 아니하면 못하리라
    dict(ref=(41, 14, 33), lang='ko', en='not', words=['아니하면']),
    dict(ref=(41, 14, 33), lang='ko', en='cannot', words=['못하리라']),
    # 누가복음 17:23  not nor / 말고 말라
    dict(ref=(41, 17, 23), lang='ko', en='not', words=['말고']),
    dict(ref=(41, 17, 23), lang='ko', en='nor', words=['말라']),
    # 누가복음 18:20  not not not not / 말라 말라 말라 말라
    dict(ref=(41, 18, 20), lang='ko', en='not#1', words=['말라#1']),
    dict(ref=(41, 18, 20), lang='ko', en='not#2', words=['말라#2']),
    dict(ref=(41, 18, 20), lang='ko', en='not#3', words=['말라#3']),
    dict(ref=(41, 18, 20), lang='ko', en='not#4', words=['말라#4']),
    # 누가복음 19:21  not not / 않은 않은
    dict(ref=(41, 19, 21), lang='ko', en='not#1', words=['않은#1']),
    dict(ref=(41, 19, 21), lang='ko', en='not#2', words=['않은#2']),
    # 누가복음 19:22  not not / 않은 않은
    dict(ref=(41, 19, 22), lang='ko', en='not#1', words=['않은#1']),
    dict(ref=(41, 19, 22), lang='ko', en='not#2', words=['않은#2']),
    # 누가복음 19:44  not not / 아니하리니 못함을
    dict(ref=(41, 19, 44), lang='ko', en='not#1', words=['아니하리니']),
    dict(ref=(41, 19, 44), lang='ko', en='not#2', words=['못함을']),
    # 누가복음 21:8  not not / 않도록 말라
    dict(ref=(41, 21, 8), lang='ko', en='not#1', words=['않도록']),
    dict(ref=(41, 21, 8), lang='ko', en='not#2', words=['말라']),
    # 요한복음 4:15  not neither / 않고 않게
    dict(ref=(42, 4, 15), lang='ko', en='not', words=['않고']),
    dict(ref=(42, 4, 15), lang='ko', en='neither', words=['않게']),
    # 요한복음 4:21  neither nor / 말고 말고
    dict(ref=(42, 4, 21), lang='ko', en='neither', words=['말고#1']),
    dict(ref=(42, 4, 21), lang='ko', en='nor', words=['말고#2']),
    # 요한복음 5:23  not not / 아니하는 아니하느니라
    dict(ref=(42, 5, 23), lang='ko', en='not#1', words=['아니하는']),
    dict(ref=(42, 5, 23), lang='ko', en='not#2', words=['아니하느니라']),
    # 요한복음 5:37  neither nor / 못하였고 못하였으며
    dict(ref=(42, 5, 37), lang='ko', en='neither', words=['못하였고']),
    dict(ref=(42, 5, 37), lang='ko', en='nor', words=['못하였으며']),
    # 요한복음 5:38  not not / 아니하니 아니함이니라
    dict(ref=(42, 5, 38), lang='ko', en='not#1', words=['아니하니']),
    dict(ref=(42, 5, 38), lang='ko', en='not#2', words=['아니함이니라']),
    # 요한복음 6:24  not neither / 없으시고 없음을
    dict(ref=(42, 6, 24), lang='ko', en='not', words=['없으시고']),
    dict(ref=(42, 6, 24), lang='ko', en='neither', words=['없음을']),
    # 요한복음 6:35  never never / 아니할 아니하리라
    dict(ref=(42, 6, 35), lang='ko', en='never#1', words=['아니할']),
    dict(ref=(42, 6, 35), lang='ko', en='never#2', words=['아니하리라']),
    # 요한복음 6:64  not not / 아니하는 아니하는
    dict(ref=(42, 6, 64), lang='ko', en='not#1', words=['아니하는#1']),
    dict(ref=(42, 6, 64), lang='ko', en='not#2', words=['아니하는#2']),
    # 요한복음 7:8  not not / 못하였으니 아니하노라
    dict(ref=(42, 7, 8), lang='ko', en='not#1', words=['못하였으니']),
    dict(ref=(42, 7, 8), lang='ko', en='not#2', words=['아니하노라']),
    # 요한복음 7:28  not not / 아니로라 못하나
    dict(ref=(42, 7, 28), lang='ko', en='not#1', words=['아니로라']),
    dict(ref=(42, 7, 28), lang='ko', en='not#2', words=['못하나']),
    # 요한복음 7:39  not not / 못하신고로 아니하시더라
    dict(ref=(42, 7, 39), lang='ko', en='not#1', words=['못하신고로']),
    dict(ref=(42, 7, 39), lang='ko', en='not#2', words=['아니하시더라']),
    # 요한복음 8:19  neither nor / 못하고 못하는도다
    dict(ref=(42, 8, 19), lang='ko', en='neither', words=['못하고']),
    dict(ref=(42, 8, 19), lang='ko', en='nor', words=['못하는도다']),
    # 요한복음 8:43  not cannot / 못하느냐 못함이로다
    dict(ref=(42, 8, 43), lang='ko', en='not', words=['못하느냐']),
    dict(ref=(42, 8, 43), lang='ko', en='cannot', words=['못함이로다']),
    # 요한복음 8:47  not not / 아니함은 아니하였음이로다
    dict(ref=(42, 8, 47), lang='ko', en='not#1', words=['아니함은']),
    dict(ref=(42, 8, 47), lang='ko', en='not#2', words=['아니하였음이로다']),
    # 요한복음 8:55  not not / 못하되 못한다
    dict(ref=(42, 8, 55), lang='ko', en='not#1', words=['못하되']),
    dict(ref=(42, 8, 55), lang='ko', en='not#2', words=['못한다']),
    # 요한복음 9:16  not not / 아니하니 아니라
    dict(ref=(42, 9, 16), lang='ko', en='not#1', words=['아니하니']),
    dict(ref=(42, 9, 16), lang='ko', en='not#2', words=['아니라']),
    # 요한복음 10:5  not not / 못하는 아니하고
    dict(ref=(42, 10, 5), lang='ko', en='not#1', words=['못하는']),
    dict(ref=(42, 10, 5), lang='ko', en='not#2', words=['아니하고']),
    # 요한복음 10:12  not not / 아니요 아니라
    dict(ref=(42, 10, 12), lang='ko', en='not#1', words=['아니요']),
    dict(ref=(42, 10, 12), lang='ko', en='not#2', words=['아니라']),
    # 요한복음 10:26  not not / 아니므로 아니하는도다
    dict(ref=(42, 10, 26), lang='ko', en='not#1', words=['아니므로']),
    dict(ref=(42, 10, 26), lang='ko', en='not#2', words=['아니하는도다']),
    # 요한복음 10:28  never neither / 아니할 없느니라
    dict(ref=(42, 10, 28), lang='ko', en='never', words=['아니할']),
    dict(ref=(42, 10, 28), lang='ko', en='neither', words=['없느니라']),
    # 요한복음 11:9  not not / 아니냐 아니하고
    dict(ref=(42, 11, 9), lang='ko', en='not#1', words=['아니냐']),
    dict(ref=(42, 11, 9), lang='ko', en='not#2', words=['아니하고']),
    # 요한복음 11:50  Nor not / 않게 아니하는도다
    dict(ref=(42, 11, 50), lang='ko', en='Nor', words=['않게']),
    dict(ref=(42, 11, 50), lang='ko', en='not', words=['아니하는도다']),
    # 요한복음 12:47  not not not / 아니할지라도 아니하노라 아니요
    dict(ref=(42, 12, 47), lang='ko', en='not#1', words=['아니할지라도']),
    dict(ref=(42, 12, 47), lang='ko', en='not#2', words=['아니하노라']),
    dict(ref=(42, 12, 47), lang='ko', en='not#3', words=['아니요']),
    # 요한복음 13:10  not not / 없느니라 아니니라
    dict(ref=(42, 13, 10), lang='ko', en='not#1', words=['없느니라']),
    dict(ref=(42, 13, 10), lang='ko', en='not#2', words=['아니니라']),
    # 요한복음 13:16  not neither / 못하고 못하니
    dict(ref=(42, 13, 16), lang='ko', en='not', words=['못하고']),
    dict(ref=(42, 13, 16), lang='ko', en='neither', words=['못하니']),
    # 요한복음 14:10  not not / 아니하느냐 아니라
    dict(ref=(42, 14, 10), lang='ko', en='not#1', words=['아니하느냐']),
    dict(ref=(42, 14, 10), lang='ko', en='not#2', words=['아니라']),
    # 요한복음 14:17  cannot not neither / 못하나니 못하고 못함이라
    dict(ref=(42, 14, 17), lang='ko', en='cannot', words=['못하나니']),
    dict(ref=(42, 14, 17), lang='ko', en='not', words=['못하고']),
    dict(ref=(42, 14, 17), lang='ko', en='neither', words=['못함이라']),
    # 요한복음 14:24  not not not / 아니하는 아니하나니 아니요
    dict(ref=(42, 14, 24), lang='ko', en='not#1', words=['아니하는']),
    dict(ref=(42, 14, 24), lang='ko', en='not#2', words=['아니하나니']),
    dict(ref=(42, 14, 24), lang='ko', en='not#3', words=['아니요']),
    # 요한복음 14:27  not not neither / 아니하니라 말고 말라
    dict(ref=(42, 14, 27), lang='ko', en='not#1', words=['아니하니라']),
    dict(ref=(42, 14, 27), lang='ko', en='not#2', words=['말고']),
    dict(ref=(42, 14, 27), lang='ko', en='neither', words=['말라']),
    # 요한복음 15:15  not not / 아니하리니 못함이라
    dict(ref=(42, 15, 15), lang='ko', en='not#1', words=['아니하리니']),
    dict(ref=(42, 15, 15), lang='ko', en='not#2', words=['못함이라']),
    # 요한복음 15:22  not not / 아니하였더면 없느니라
    dict(ref=(42, 15, 22), lang='ko', en='not#1', words=['아니하였더면']),
    dict(ref=(42, 15, 22), lang='ko', en='not#2', words=['없느니라']),
    # 요한복음 15:24  not not / 못한 아니하였더면
    dict(ref=(42, 15, 24), lang='ko', en='not#1', words=['못한']),
    dict(ref=(42, 15, 24), lang='ko', en='not#2', words=['아니하였더면']),
    # 요한복음 16:7  not not / 아니하면 아니할
    dict(ref=(42, 16, 7), lang='ko', en='not#1', words=['아니하면']),
    dict(ref=(42, 16, 7), lang='ko', en='not#2', words=['아니할']),
    # 요한복음 17:14  not not / 아니함 아니함을
    dict(ref=(42, 17, 14), lang='ko', en='not#1', words=['아니함']),
    dict(ref=(42, 17, 14), lang='ko', en='not#2', words=['아니함을']),
    # 요한복음 17:16  not not / 아니함 아니하였삽나이다
    dict(ref=(42, 17, 16), lang='ko', en='not#1', words=['아니함']),
    dict(ref=(42, 17, 16), lang='ko', en='not#2', words=['아니하였삽나이다']),
    # 요한복음 18:17  not not / 아니냐 아니라
    dict(ref=(42, 18, 17), lang='ko', en='not#1', words=['아니냐']),
    dict(ref=(42, 18, 17), lang='ko', en='not#2', words=['아니라']),
    # 요한복음 18:25  not not / 아니냐 아니라
    dict(ref=(42, 18, 25), lang='ko', en='not#1', words=['아니냐']),
    dict(ref=(42, 18, 25), lang='ko', en='not#2', words=['아니라']),
    # 요한복음 18:30  not not / 아니었더면 아니하였겠나이다
    dict(ref=(42, 18, 30), lang='ko', en='not#1', words=['아니었더면']),
    dict(ref=(42, 18, 30), lang='ko', en='not#2', words=['아니하였겠나이다']),
    # 요한복음 18:36  not not not / 아니라 않게 아니니라
    dict(ref=(42, 18, 36), lang='ko', en='not#1', words=['아니라']),
    dict(ref=(42, 18, 36), lang='ko', en='not#2', words=['않게']),
    dict(ref=(42, 18, 36), lang='ko', en='not#3', words=['아니니라']),
    # 요한복음 20:17  not not / 말라 못하였노라
    dict(ref=(42, 20, 17), lang='ko', en='not#1', words=['말라']),
    dict(ref=(42, 20, 17), lang='ko', en='not#2', words=['못하였노라']),
    # 요한복음 21:23  not not not / 아니하겠다 않겠다 아니라
    dict(ref=(42, 21, 23), lang='ko', en='not#1', words=['아니하겠다']),
    dict(ref=(42, 21, 23), lang='ko', en='not#2', words=['않겠다']),
    dict(ref=(42, 21, 23), lang='ko', en='not#3', words=['아니라']),
    # 사도행전 2:27  not neither / 아니하시며 않게
    dict(ref=(43, 2, 27), lang='ko', en='not', words=['아니하시며']),
    dict(ref=(43, 2, 27), lang='ko', en='neither', words=['않게']),
    # 사도행전 2:31  not neither / 않고 아니하시리라
    dict(ref=(43, 2, 31), lang='ko', en='not', words=['않고']),
    dict(ref=(43, 2, 31), lang='ko', en='neither', words=['아니하시리라']),
    # 사도행전 4:18  not nor / 말고 말라
    dict(ref=(43, 4, 18), lang='ko', en='not', words=['말고']),
    dict(ref=(43, 4, 18), lang='ko', en='nor', words=['말라']),
    # 사도행전 13:25  not not / 아니라 못하리라
    dict(ref=(43, 13, 25), lang='ko', en='not#1', words=['아니라']),
    dict(ref=(43, 13, 25), lang='ko', en='not#2', words=['못하리라']),
    # 사도행전 15:38  not not / 아니한 않다
    dict(ref=(43, 15, 38), lang='ko', en='not#1', words=['아니한']),
    dict(ref=(43, 15, 38), lang='ko', en='not#2', words=['않다']),
    # 사도행전 16:21  not neither / 못하고 못할
    dict(ref=(43, 16, 21), lang='ko', en='not', words=['못하고']),
    dict(ref=(43, 16, 21), lang='ko', en='neither', words=['못할']),
    # 사도행전 18:9  not not / 말며 말고
    dict(ref=(43, 18, 9), lang='ko', en='not#1', words=['말며']),
    dict(ref=(43, 18, 9), lang='ko', en='not#2', words=['말고']),
    # 사도행전 19:37  neither nor / 아니하였고 아니한
    dict(ref=(43, 19, 37), lang='ko', en='neither', words=['아니하였고']),
    dict(ref=(43, 19, 37), lang='ko', en='nor', words=['아니한']),
    # 사도행전 21:21  not neither / 말고 말라
    dict(ref=(43, 21, 21), lang='ko', en='not', words=['말고']),
    dict(ref=(43, 21, 21), lang='ko', en='neither', words=['말라']),
    # 사도행전 23:5  not not / 못하였노라 말라
    dict(ref=(43, 23, 5), lang='ko', en='not#1', words=['못하였노라']),
    dict(ref=(43, 23, 5), lang='ko', en='not#2', words=['말라']),
    # 사도행전 27:20  neither nor / 아니하고 없어졌더라
    dict(ref=(43, 27, 20), lang='ko', en='neither', words=['아니하고']),
    dict(ref=(43, 27, 20), lang='ko', en='nor', words=['없어졌더라']),
    # 사도행전 28:21  neither neither / 못한 없느니라
    dict(ref=(43, 28, 21), lang='ko', en='neither#1', words=['못한']),
    dict(ref=(43, 28, 21), lang='ko', en='neither#2', words=['없느니라']),
    # 사도행전 28:26  not not / 못하며 못하는도다
    dict(ref=(43, 28, 26), lang='ko', en='not#1', words=['못하며']),
    dict(ref=(43, 28, 26), lang='ko', en='not#2', words=['못하는도다']),
    # 로마서 1:21  not neither / 아니하며 아니하고
    dict(ref=(44, 1, 21), lang='ko', en='not', words=['아니하며']),
    dict(ref=(44, 1, 21), lang='ko', en='neither', words=['아니하고']),
    # 로마서 2:21  not not / 아니하느냐 말라
    dict(ref=(44, 2, 21), lang='ko', en='not#1', words=['아니하느냐']),
    dict(ref=(44, 2, 21), lang='ko', en='not#2', words=['말라']),
    # 로마서 2:28  not neither / 아니요 아니라
    dict(ref=(44, 2, 28), lang='ko', en='not', words=['아니요']),
    dict(ref=(44, 2, 28), lang='ko', en='neither', words=['아니라']),
    # 로마서 2:29  not not / 아니한 아니요
    dict(ref=(44, 2, 29), lang='ko', en='not#1', words=['아니한']),
    dict(ref=(44, 2, 29), lang='ko', en='not#2', words=['아니요']),
    # 로마서 6:14  not not / 못하리니 아니하고
    dict(ref=(44, 6, 14), lang='ko', en='not#1', words=['못하리니']),
    dict(ref=(44, 6, 14), lang='ko', en='not#2', words=['아니하고']),
    # 로마서 7:15  not not / 못하노니 아니하고
    dict(ref=(44, 7, 15), lang='ko', en='not#1', words=['못하노니']),
    dict(ref=(44, 7, 15), lang='ko', en='not#2', words=['아니하고']),
    # 로마서 7:19  not not / 아니하고 아니하는
    dict(ref=(44, 7, 19), lang='ko', en='not#1', words=['아니하고']),
    dict(ref=(44, 7, 19), lang='ko', en='not#2', words=['아니하는']),
    # 로마서 8:32  not not / 아니하시고 아니하시겠느뇨
    dict(ref=(44, 8, 32), lang='ko', en='not#1', words=['아니하시고']),
    dict(ref=(44, 8, 32), lang='ko', en='not#2', words=['아니하시겠느뇨']),
    # 로마서 9:6  Not not / 않도다 아니요
    dict(ref=(44, 9, 6), lang='ko', en='Not', words=['않도다']),
    dict(ref=(44, 9, 6), lang='ko', en='not', words=['아니요']),
    # 로마서 9:11  not neither not / 아니하고 아니한 않고
    dict(ref=(44, 9, 11), lang='ko', en='not#1', words=['아니하고']),
    dict(ref=(44, 9, 11), lang='ko', en='neither', words=['아니한']),
    dict(ref=(44, 9, 11), lang='ko', en='not#2', words=['않고']),
    # 로마서 9:16  not nor / 아니요 아니요
    dict(ref=(44, 9, 16), lang='ko', en='not', words=['아니요#1']),
    dict(ref=(44, 9, 16), lang='ko', en='nor', words=['아니요#2']),
    # 로마서 10:14  not not / 아니하는 못한
    dict(ref=(44, 10, 14), lang='ko', en='not#1', words=['아니하는']),
    dict(ref=(44, 10, 14), lang='ko', en='not#2', words=['못한']),
    # 로마서 10:20  not not / 아니하는 아니하는
    dict(ref=(44, 10, 20), lang='ko', en='not#1', words=['아니하는#1']),
    dict(ref=(44, 10, 20), lang='ko', en='not#2', words=['아니하는#2']),
    # 로마서 11:2  not not / 아니하셨나니 못하느냐
    dict(ref=(44, 11, 2), lang='ko', en='not#1', words=['아니하셨나니']),
    dict(ref=(44, 11, 2), lang='ko', en='not#2', words=['못하느냐']),
    # 로마서 11:8  not not / 못할 못할
    dict(ref=(44, 11, 8), lang='ko', en='not#1', words=['못할#1']),
    dict(ref=(44, 11, 8), lang='ko', en='not#2', words=['못할#2']),
    # 로마서 11:18  not not / 말라 아니요
    dict(ref=(44, 11, 18), lang='ko', en='not#1', words=['말라']),
    dict(ref=(44, 11, 18), lang='ko', en='not#2', words=['아니요']),
    # 로마서 11:21  not not / 아니하셨은즉 아니하시리라
    dict(ref=(44, 11, 21), lang='ko', en='not#1', words=['아니하셨은즉']),
    dict(ref=(44, 11, 21), lang='ko', en='not#2', words=['아니하시리라']),
    # 로마서 12:16  not not / 말고 말라
    dict(ref=(44, 12, 16), lang='ko', en='not#1', words=['말고']),
    dict(ref=(44, 12, 16), lang='ko', en='not#2', words=['말라']),
    # 로마서 13:3  not not / 않고 아니하려느냐
    dict(ref=(44, 13, 3), lang='ko', en='not#1', words=['않고']),
    dict(ref=(44, 13, 3), lang='ko', en='not#2', words=['아니하려느냐']),
    # 로마서 13:13  not not not / 말며 말며 말고
    dict(ref=(44, 13, 13), lang='ko', en='not#1', words=['말며#1']),
    dict(ref=(44, 13, 13), lang='ko', en='not#2', words=['말며#2']),
    dict(ref=(44, 13, 13), lang='ko', en='not#3', words=['말고']),
    # 로마서 14:3  not not not not / 않는 말고 못하는 말라
    dict(ref=(44, 14, 3), lang='ko', en='not#1', words=['않는']),
    dict(ref=(44, 14, 3), lang='ko', en='not#2', words=['말고']),
    dict(ref=(44, 14, 3), lang='ko', en='not#3', words=['못하는']),
    dict(ref=(44, 14, 3), lang='ko', en='not#4', words=['말라']),
    # 로마서 14:23  not not / 아니한 아니하는
    dict(ref=(44, 14, 23), lang='ko', en='not#1', words=['아니한']),
    dict(ref=(44, 14, 23), lang='ko', en='not#2', words=['아니하는']),
    # 로마서 15:21  not not / 못한 못한
    dict(ref=(44, 15, 21), lang='ko', en='not#1', words=['못한#1']),
    dict(ref=(44, 15, 21), lang='ko', en='not#2', words=['못한#2']),
    # 고린도전서 1:26  not not not / 아니하며 아니하며 아니하도다
    dict(ref=(45, 1, 26), lang='ko', en='not#1', words=['아니하며#1']),
    dict(ref=(45, 1, 26), lang='ko', en='not#2', words=['아니하며#2']),
    dict(ref=(45, 1, 26), lang='ko', en='not#3', words=['아니하도다']),
    # 고린도전서 2:9  not nor neither / 못하고 못하고 못하였다
    dict(ref=(45, 2, 9), lang='ko', en='not', words=['못하고#1']),
    dict(ref=(45, 2, 9), lang='ko', en='nor', words=['못하고#2']),
    dict(ref=(45, 2, 9), lang='ko', en='neither', words=['못하였다']),
    # 고린도전서 2:14  not neither / 아니하나니 못하나니
    dict(ref=(45, 2, 14), lang='ko', en='not', words=['아니하나니']),
    dict(ref=(45, 2, 14), lang='ko', en='neither', words=['못하나니']),
    # 고린도전서 3:2  not not neither / 아니하였노니 못하였음이거니와 못하리라
    dict(ref=(45, 3, 2), lang='ko', en='not#1', words=['아니하였노니']),
    dict(ref=(45, 3, 2), lang='ko', en='not#2', words=['못하였음이거니와']),
    dict(ref=(45, 3, 2), lang='ko', en='neither', words=['못하리라']),
    # 고린도전서 4:7  not not / 아니한 아니한
    dict(ref=(45, 4, 7), lang='ko', en='not#1', words=['아니한#1']),
    dict(ref=(45, 4, 7), lang='ko', en='not#2', words=['아니한#2']),
    # 고린도전서 5:6  not not / 아니하도다 못하느냐
    dict(ref=(45, 5, 6), lang='ko', en='not#1', words=['아니하도다']),
    dict(ref=(45, 5, 6), lang='ko', en='not#2', words=['못하느냐']),
    # 고린도전서 5:8  not neither / 말고 말고
    dict(ref=(45, 5, 8), lang='ko', en='not', words=['말고#1']),
    dict(ref=(45, 5, 8), lang='ko', en='neither', words=['말고#2']),
    # 고린도전서 5:11  not not / 말고 말라
    dict(ref=(45, 5, 11), lang='ko', en='not#1', words=['말고']),
    dict(ref=(45, 5, 11), lang='ko', en='not#2', words=['말라']),
    # 고린도전서 6:7  not not / 아니하며 아니하냐
    dict(ref=(45, 6, 7), lang='ko', en='not#1', words=['아니하며']),
    dict(ref=(45, 6, 7), lang='ko', en='not#2', words=['아니하냐']),
    # 고린도전서 6:12  not not / 아니요 아니하리라
    dict(ref=(45, 6, 12), lang='ko', en='not#1', words=['아니요']),
    dict(ref=(45, 6, 12), lang='ko', en='not#2', words=['아니하리라']),
    # 고린도전서 6:19  not not / 못하느냐 아니라
    dict(ref=(45, 6, 19), lang='ko', en='not#1', words=['못하느냐']),
    dict(ref=(45, 6, 19), lang='ko', en='not#2', words=['아니라']),
    # 고린도전서 7:4  not not / 못하고 못하고
    dict(ref=(45, 7, 4), lang='ko', en='not#1', words=['못하고#1']),
    dict(ref=(45, 7, 4), lang='ko', en='not#2', words=['못하고#2']),
    # 고린도전서 7:10  not not / 아니요 말고
    dict(ref=(45, 7, 10), lang='ko', en='not#1', words=['아니요']),
    dict(ref=(45, 7, 10), lang='ko', en='not#2', words=['말고']),
    # 고린도전서 7:12  not not not / 아니라 아니하는 말며
    dict(ref=(45, 7, 12), lang='ko', en='not#1', words=['아니라']),
    dict(ref=(45, 7, 12), lang='ko', en='not#2', words=['아니하는']),
    dict(ref=(45, 7, 12), lang='ko', en='not#3', words=['말며']),
    # 고린도전서 7:13  not not / 아니하는 말라
    dict(ref=(45, 7, 13), lang='ko', en='not#1', words=['아니하는']),
    dict(ref=(45, 7, 13), lang='ko', en='not#2', words=['말라']),
    # 고린도전서 7:18  not not / 말며 말라
    dict(ref=(45, 7, 18), lang='ko', en='not#1', words=['말며']),
    dict(ref=(45, 7, 18), lang='ko', en='not#2', words=['말라']),
    # 고린도전서 7:27  not not / 말며 말라
    dict(ref=(45, 7, 27), lang='ko', en='not#1', words=['말며']),
    dict(ref=(45, 7, 27), lang='ko', en='not#2', words=['말라']),
    # 고린도전서 7:28  not not / 아니요 아니로되
    dict(ref=(45, 7, 28), lang='ko', en='not#1', words=['아니요']),
    dict(ref=(45, 7, 28), lang='ko', en='not#2', words=['아니로되']),
    # 고린도전서 9:1  not not not not / 아니냐 아니냐 못하였느냐 아니냐
    dict(ref=(45, 9, 1), lang='ko', en='not#1', words=['아니냐#1']),
    dict(ref=(45, 9, 1), lang='ko', en='not#2', words=['아니냐#2']),
    dict(ref=(45, 9, 1), lang='ko', en='not#3', words=['못하였느냐']),
    dict(ref=(45, 9, 1), lang='ko', en='not#4', words=['아니냐#3']),
    # 고린도전서 9:7  not not / 않겠느냐 않겠느냐
    dict(ref=(45, 9, 7), lang='ko', en='not#1', words=['않겠느냐#1']),
    dict(ref=(45, 9, 7), lang='ko', en='not#2', words=['않겠느냐#2']),
    # 고린도전서 9:26  not not / 아니하고 아니하여
    dict(ref=(45, 9, 26), lang='ko', en='not#1', words=['아니하고']),
    dict(ref=(45, 9, 26), lang='ko', en='not#2', words=['아니하여']),
    # 고린도전서 10:16  not not / 아니며 아니냐
    dict(ref=(45, 10, 16), lang='ko', en='not#1', words=['아니며']),
    dict(ref=(45, 10, 16), lang='ko', en='not#2', words=['아니냐']),
    # 고린도전서 10:20  not not / 아니니 아니하노라
    dict(ref=(45, 10, 20), lang='ko', en='not#1', words=['아니니']),
    dict(ref=(45, 10, 20), lang='ko', en='not#2', words=['아니하노라']),
    # 고린도전서 10:23  not not / 아니요 아니니
    dict(ref=(45, 10, 23), lang='ko', en='not#1', words=['아니요']),
    dict(ref=(45, 10, 23), lang='ko', en='not#2', words=['아니니']),
    # 고린도전서 11:11  neither neither / 않고 아니하니라
    dict(ref=(45, 11, 11), lang='ko', en='neither#1', words=['않고']),
    dict(ref=(45, 11, 11), lang='ko', en='neither#2', words=['아니하니라']),
    # 고린도전서 11:17  not not / 아니하나니 못되고
    # 고린도전서 13:4  not not not / 아니하며 아니하며 아니하며
    dict(ref=(45, 13, 4), lang='ko', en='not#1', words=['아니하며#1']),
    dict(ref=(45, 13, 4), lang='ko', en='not#2', words=['아니하며#2']),
    dict(ref=(45, 13, 4), lang='ko', en='not#3', words=['아니하며#3']),
    # 고린도전서 14:22  not not not not / 않고 아니하는 아니하는 않고
    dict(ref=(45, 14, 22), lang='ko', en='not#1', words=['않고#1']),
    dict(ref=(45, 14, 22), lang='ko', en='not#2', words=['아니하는#1']),
    dict(ref=(45, 14, 22), lang='ko', en='not#3', words=['아니하는#2']),
    dict(ref=(45, 14, 22), lang='ko', en='not#4', words=['않고#2']),
    # 고린도전서 15:10  not not / 아니하여 아니요
    dict(ref=(45, 15, 10), lang='ko', en='not#1', words=['아니하여']),
    dict(ref=(45, 15, 10), lang='ko', en='not#2', words=['아니요']),
    # 고린도전서 15:15  not not / 없으면 아니하셨으리라
    dict(ref=(45, 15, 15), lang='ko', en='not#1', words=['없으면']),
    dict(ref=(45, 15, 15), lang='ko', en='not#2', words=['아니하셨으리라']),
    # 고린도전서 15:34  not not / 말라 못하는
    dict(ref=(45, 15, 34), lang='ko', en='not#1', words=['말라']),
    dict(ref=(45, 15, 34), lang='ko', en='not#2', words=['못하는']),
    # 고린도전서 15:50  cannot neither / 아니한 못하느니라
    dict(ref=(45, 15, 50), lang='ko', en='cannot', words=['아니한']),
    dict(ref=(45, 15, 50), lang='ko', en='neither', words=['못하느니라']),
    # 고린도후서 2:5  not not / 아니요 아니하려
    dict(ref=(46, 2, 5), lang='ko', en='not#1', words=['아니요']),
    dict(ref=(46, 2, 5), lang='ko', en='not#2', words=['아니하려']),
    # 고린도후서 3:3  not not / 아니요 아니요
    dict(ref=(46, 3, 3), lang='ko', en='not#1', words=['아니요#1']),
    dict(ref=(46, 3, 3), lang='ko', en='not#2', words=['아니요#2']),
    # 고린도후서 4:2  not nor / 아니하며 아니하고
    dict(ref=(46, 4, 2), lang='ko', en='not', words=['아니하며']),
    dict(ref=(46, 4, 2), lang='ko', en='nor', words=['아니하고']),
    # 고린도후서 4:8  not not / 아니하며 아니하며
    dict(ref=(46, 4, 8), lang='ko', en='not#1', words=['아니하며#1']),
    dict(ref=(46, 4, 8), lang='ko', en='not#2', words=['아니하며#2']),
    # 고린도후서 4:9  not not / 아니하며 아니하고
    dict(ref=(46, 4, 9), lang='ko', en='not#1', words=['아니하며']),
    dict(ref=(46, 4, 9), lang='ko', en='not#2', words=['아니하고']),
    # 고린도후서 4:18  not not not / 아니요 않는 않는
    dict(ref=(46, 4, 18), lang='ko', en='not#1', words=['아니요']),
    dict(ref=(46, 4, 18), lang='ko', en='not#2', words=['않는#1']),
    dict(ref=(46, 4, 18), lang='ko', en='not#3', words=['않는#2']),
    # 고린도후서 7:12  not nor / 아니요 아니요
    dict(ref=(46, 7, 12), lang='ko', en='not', words=['아니요#1']),
    dict(ref=(46, 7, 12), lang='ko', en='nor', words=['아니요#2']),
    # 고린도후서 10:8  not not / 아니요 아니하리라
    dict(ref=(46, 10, 8), lang='ko', en='not#1', words=['아니요']),
    dict(ref=(46, 10, 8), lang='ko', en='not#2', words=['아니하리라']),
    # 고린도후서 10:14  not not / 못할 아니요
    dict(ref=(46, 10, 14), lang='ko', en='not#1', words=['못할']),
    dict(ref=(46, 10, 14), lang='ko', en='not#2', words=['아니요']),
    # 고린도후서 11:4  not not not / 아니한 아니한 아니한
    dict(ref=(46, 11, 4), lang='ko', en='not#1', words=['아니한#1']),
    dict(ref=(46, 11, 4), lang='ko', en='not#2', words=['아니한#2']),
    dict(ref=(46, 11, 4), lang='ko', en='not#3', words=['아니한#3']),
    # 고린도후서 11:29  not not / 아니하며 않더냐
    dict(ref=(46, 11, 29), lang='ko', en='not#1', words=['아니하며']),
    dict(ref=(46, 11, 29), lang='ko', en='not#2', words=['않더냐']),
    # 고린도후서 12:14  not not not / 아니하리라 아니요 아니요
    dict(ref=(46, 12, 14), lang='ko', en='not#1', words=['아니하리라']),
    dict(ref=(46, 12, 14), lang='ko', en='not#2', words=['아니요#1']),
    dict(ref=(46, 12, 14), lang='ko', en='not#3', words=['아니요#2']),
    # 고린도후서 12:18  not not / 아니하더냐 아니하더냐
    dict(ref=(46, 12, 18), lang='ko', en='not#1', words=['아니하더냐#1']),
    dict(ref=(46, 12, 18), lang='ko', en='not#2', words=['아니하더냐#2']),
    # 고린도후서 12:20  not not / 못하고 않는
    dict(ref=(46, 12, 20), lang='ko', en='not#1', words=['못하고']),
    dict(ref=(46, 12, 20), lang='ko', en='not#2', words=['않는']),
    # 갈라디아서 1:1  not neither / 아니요 아니요
    dict(ref=(47, 1, 1), lang='ko', en='not', words=['아니요#1']),
    dict(ref=(47, 1, 1), lang='ko', en='neither', words=['아니요#2']),
    # 갈라디아서 4:27  not not / 못한 못한
    dict(ref=(47, 4, 27), lang='ko', en='not#1', words=['못한#1']),
    dict(ref=(47, 4, 27), lang='ko', en='not#2', words=['못한#2']),
    # 갈라디아서 6:7  not not / 말라 아니하시나니
    dict(ref=(47, 6, 7), lang='ko', en='not#1', words=['말라']),
    dict(ref=(47, 6, 7), lang='ko', en='not#2', words=['아니하시나니']),
    # 갈라디아서 6:9  not not / 말지니 아니하면
    dict(ref=(47, 6, 9), lang='ko', en='not#1', words=['말지니']),
    dict(ref=(47, 6, 9), lang='ko', en='not#2', words=['아니하면']),
    # 에베소서 4:26  not not / 말며 말고
    dict(ref=(48, 4, 26), lang='ko', en='not#1', words=['말며']),
    dict(ref=(48, 4, 26), lang='ko', en='not#2', words=['말고']),
    # 빌립보서 2:16  not neither / 아니하고 아니함으로
    dict(ref=(49, 2, 16), lang='ko', en='not', words=['아니하고']),
    dict(ref=(49, 2, 16), lang='ko', en='neither', words=['아니함으로']),
    # 골로새서 2:21  not not not / 말고 말고 말라
    dict(ref=(50, 2, 21), lang='ko', en='not#1', words=['말고#1']),
    dict(ref=(50, 2, 21), lang='ko', en='not#2', words=['말고#2']),
    dict(ref=(50, 2, 21), lang='ko', en='not#3', words=['말라']),
    # 데살로니가후서 3:8  Neither not / 않고 아니하려
    dict(ref=(52, 3, 8), lang='ko', en='Neither', words=['않고']),
    dict(ref=(52, 3, 8), lang='ko', en='not', words=['아니하려']),
    # 디모데전서 3:3  Not not not not / 아니하며 아니하며 아니하며 아니하며
    dict(ref=(53, 3, 3), lang='ko', en='Not', words=['아니하며#1']),
    dict(ref=(53, 3, 3), lang='ko', en='not#1', words=['아니하며#2']),
    dict(ref=(53, 3, 3), lang='ko', en='not#2', words=['아니하며#3']),
    dict(ref=(53, 3, 3), lang='ko', en='not#3', words=['아니하며#4']),
    # 디모데전서 3:8  not not not / 아니하고 아니하고 아니하고
    dict(ref=(53, 3, 8), lang='ko', en='not#1', words=['아니하고#1']),
    dict(ref=(53, 3, 8), lang='ko', en='not#2', words=['아니하고#2']),
    dict(ref=(53, 3, 8), lang='ko', en='not#3', words=['아니하고#3']),
    # 디모데전서 5:13  not not / 아니라 아니할
    dict(ref=(53, 5, 13), lang='ko', en='not#1', words=['아니라']),
    dict(ref=(53, 5, 13), lang='ko', en='not#2', words=['아니할']),
    # 디모데전서 6:17  not nor / 말고 말고
    dict(ref=(53, 6, 17), lang='ko', en='not', words=['말고#1']),
    dict(ref=(53, 6, 17), lang='ko', en='nor', words=['말고#2']),
    # 디도서 2:3  not not / 말며 말며
    dict(ref=(55, 2, 3), lang='ko', en='not#1', words=['말며#1']),
    dict(ref=(55, 2, 3), lang='ko', en='not#2', words=['말며#2']),
    # 히브리서 8:9  Not not not / 아니하도다 아니하므로 아니하였노라
    dict(ref=(57, 8, 9), lang='ko', en='Not', words=['아니하도다']),
    dict(ref=(57, 8, 9), lang='ko', en='not#1', words=['아니하므로']),
    dict(ref=(57, 8, 9), lang='ko', en='not#2', words=['아니하였노라']),
    # 히브리서 9:11  not not / 아니한 아니한
    dict(ref=(57, 9, 11), lang='ko', en='not#1', words=['아니한#1']),
    dict(ref=(57, 9, 11), lang='ko', en='not#2', words=['아니한#2']),
    # 히브리서 10:1  not never / 아니므로 없느니라
    dict(ref=(57, 10, 1), lang='ko', en='not', words=['아니므로']),
    dict(ref=(57, 10, 1), lang='ko', en='never', words=['없느니라']),
    # 히브리서 10:8  not neither / 아니하고 아니하신다
    dict(ref=(57, 10, 8), lang='ko', en='not', words=['아니하고']),
    dict(ref=(57, 10, 8), lang='ko', en='neither', words=['아니하신다']),
    # 히브리서 12:5  not nor / 말며 말라
    dict(ref=(57, 12, 5), lang='ko', en='not', words=['말며']),
    dict(ref=(57, 12, 5), lang='ko', en='nor', words=['말라']),
    # 히브리서 13:9  not not not / 말라 아니니 못하였느니라
    dict(ref=(57, 13, 9), lang='ko', en='not#1', words=['말라']),
    dict(ref=(57, 13, 9), lang='ko', en='not#2', words=['아니니']),
    dict(ref=(57, 13, 9), lang='ko', en='not#3', words=['못하였느니라']),
    # 야고보서 3:14  not not / 말라 말라
    dict(ref=(58, 3, 14), lang='ko', en='not#1', words=['말라#1']),
    dict(ref=(58, 3, 14), lang='ko', en='not#2', words=['말라#2']),
    # 야고보서 4:2  not cannot not not / 못하고 못하나니 못함은 아니함이요
    dict(ref=(58, 4, 2), lang='ko', en='not#1', words=['못하고']),
    dict(ref=(58, 4, 2), lang='ko', en='cannot', words=['못하나니']),
    dict(ref=(58, 4, 2), lang='ko', en='not#2', words=['못함은']),
    dict(ref=(58, 4, 2), lang='ko', en='not#3', words=['아니함이요']),
    # 야고보서 4:11  not not / 말라 아니요
    dict(ref=(58, 4, 11), lang='ko', en='not#1', words=['말라']),
    dict(ref=(58, 4, 11), lang='ko', en='not#2', words=['아니요']),
    # 야고보서 5:12  not neither neither neither / 말지니 말고 아니라 아니라
    dict(ref=(58, 5, 12), lang='ko', en='not', words=['말지니']),
    dict(ref=(58, 5, 12), lang='ko', en='neither#1', words=['말고']),
    dict(ref=(58, 5, 12), lang='ko', en='neither#2', words=['아니라#1']),
    dict(ref=(58, 5, 12), lang='ko', en='neither#3', words=['아니라#2']),
    # 야고보서 5:17  not not / 않기를 아니오고
    dict(ref=(58, 5, 17), lang='ko', en='not#1', words=['않기를']),
    dict(ref=(58, 5, 17), lang='ko', en='not#2', words=['아니오고']),
    # 베드로전서 1:8  not not / 못하였으나 못하나
    dict(ref=(59, 1, 8), lang='ko', en='not#1', words=['못하였으나']),
    dict(ref=(59, 1, 8), lang='ko', en='not#2', words=['못하나']),
    # 베드로전서 2:10  not not / 아니더니 못하였더니
    dict(ref=(59, 2, 10), lang='ko', en='not#1', words=['아니더니']),
    dict(ref=(59, 2, 10), lang='ko', en='not#2', words=['못하였더니']),
    # 베드로전서 2:23  not not / 아니하시고 아니하시고
    dict(ref=(59, 2, 23), lang='ko', en='not#1', words=['아니하시고#1']),
    dict(ref=(59, 2, 23), lang='ko', en='not#2', words=['아니하시고#2']),
    # 베드로전서 3:14  not neither / 말며 말고
    dict(ref=(59, 3, 14), lang='ko', en='not', words=['말며']),
    dict(ref=(59, 3, 14), lang='ko', en='neither', words=['말고']),
    # 베드로전서 5:2  not not / 말고 말고
    dict(ref=(59, 5, 2), lang='ko', en='not#1', words=['말고#1']),
    dict(ref=(59, 5, 2), lang='ko', en='not#2', words=['말고#2']),
    # 베드로후서 1:8  neither nor / 않고 않게
    dict(ref=(60, 1, 8), lang='ko', en='neither', words=['않고']),
    dict(ref=(60, 1, 8), lang='ko', en='nor', words=['않게']),
    # 베드로후서 2:3  not not / 아니하며 아니하느니라
    dict(ref=(60, 2, 3), lang='ko', en='not#1', words=['아니하며']),
    dict(ref=(60, 2, 3), lang='ko', en='not#2', words=['아니하느니라']),
    # 요한일서 1:10  not not / 아니하였다 아니하니라
    dict(ref=(61, 1, 10), lang='ko', en='not#1', words=['아니하였다']),
    dict(ref=(61, 1, 10), lang='ko', en='not#2', words=['아니하니라']),
    # 요한일서 2:4  not not / 아니하는 아니하되
    dict(ref=(61, 2, 4), lang='ko', en='not#1', words=['아니하는']),
    dict(ref=(61, 2, 4), lang='ko', en='not#2', words=['아니하되']),
    # 요한일서 2:19  not not / 아니하였나니 아니함을
    dict(ref=(61, 2, 19), lang='ko', en='not#1', words=['아니하였나니']),
    dict(ref=(61, 2, 19), lang='ko', en='not#2', words=['아니함을']),
    # 요한일서 3:1  not not / 못함은 못함이니라
    dict(ref=(61, 3, 1), lang='ko', en='not#1', words=['못함은']),
    dict(ref=(61, 3, 1), lang='ko', en='not#2', words=['못함이니라']),
    # 요한일서 3:6  not not neither / 아니하나니 못하였고 못하였느니라
    dict(ref=(61, 3, 6), lang='ko', en='not#1', words=['아니하나니']),
    dict(ref=(61, 3, 6), lang='ko', en='not#2', words=['못하였고']),
    dict(ref=(61, 3, 6), lang='ko', en='neither', words=['못하였느니라']),
    # 요한일서 4:8  not not / 아니하는 못하나니
    dict(ref=(61, 4, 8), lang='ko', en='not#1', words=['아니하는']),
    dict(ref=(61, 4, 8), lang='ko', en='not#2', words=['못하나니']),
    # 요한일서 5:16  not not not / 아니한 아니하는 않노라
    dict(ref=(61, 5, 16), lang='ko', en='not#1', words=['아니한']),
    dict(ref=(61, 5, 16), lang='ko', en='not#2', words=['아니하는']),
    dict(ref=(61, 5, 16), lang='ko', en='not#3', words=['않노라']),
    # 요한일서 5:18  not not / 아니하는 못하느니라
    dict(ref=(61, 5, 18), lang='ko', en='not#1', words=['아니하는']),
    dict(ref=(61, 5, 18), lang='ko', en='not#2', words=['못하느니라']),
    # 요한이서 1:10  not not neither / 않고 말고 말라
    dict(ref=(62, 1, 10), lang='ko', en='not#1', words=['않고']),
    dict(ref=(62, 1, 10), lang='ko', en='not#2', words=['말고']),
    dict(ref=(62, 1, 10), lang='ko', en='neither', words=['말라']),
    # 요한삼서 1:10  not neither / 아니하리라 아니하고
    dict(ref=(63, 1, 10), lang='ko', en='not', words=['아니하리라']),
    dict(ref=(63, 1, 10), lang='ko', en='neither', words=['아니하고']),
    # 요한계시록 2:24  not not / 아니하고 못하는
    dict(ref=(65, 2, 24), lang='ko', en='not#1', words=['아니하고']),
    dict(ref=(65, 2, 24), lang='ko', en='not#2', words=['못하는']),
    # 요한계시록 3:3  not not / 아니하면 못하리라
    dict(ref=(65, 3, 3), lang='ko', en='not#1', words=['아니하면']),
    dict(ref=(65, 3, 3), lang='ko', en='not#2', words=['못하리라']),
    # 요한계시록 3:15  neither nor / 아니하고 아니하도다
    dict(ref=(65, 3, 15), lang='ko', en='neither', words=['아니하고']),
    dict(ref=(65, 3, 15), lang='ko', en='nor', words=['아니하도다']),
    # 요한계시록 3:16  neither nor / 아니하고 아니하니
    dict(ref=(65, 3, 16), lang='ko', en='neither', words=['아니하고']),
    dict(ref=(65, 3, 16), lang='ko', en='nor', words=['아니하니']),
    # 요한계시록 12:8  not neither / 못하여 못한지라
    dict(ref=(65, 12, 8), lang='ko', en='not', words=['못하여']),
    dict(ref=(65, 12, 8), lang='ko', en='neither', words=['못한지라']),
    # 요한계시록 17:8  not not not / 없으나 못한 없으나
    dict(ref=(65, 17, 8), lang='ko', en='not#1', words=['없으나#1']),
    dict(ref=(65, 17, 8), lang='ko', en='not#2', words=['못한']),
    dict(ref=(65, 17, 8), lang='ko', en='not#3', words=['없으나#2']),
    # 요한계시록 18:4  not not / 말고 말라
    dict(ref=(65, 18, 4), lang='ko', en='not#1', words=['말고']),
    dict(ref=(65, 18, 4), lang='ko', en='not#2', words=['말라']),

    # ---- 디모데후서 3:4 ----
    dict(ref=(54, 3, 4), lang='ko', en='Traitors', words=['배반하여', '팔며']),
    dict(ref=(54, 3, 4), lang='ko', en='heady', words=['조급하며']),
    dict(ref=(54, 3, 4), lang='ko', en='highminded', words=['자고하며']),
    dict(ref=(54, 3, 4), lang='ko', en='lovers#1', words=['사랑하기를']),
    dict(ref=(54, 3, 4), lang='ko', en='of#1', words=['쾌락을']),
    dict(ref=(54, 3, 4), lang='ko', en='than', words=['것보다']),
    dict(ref=(54, 3, 4), lang='ko', en='lovers#2', words=['사랑하는']),
    dict(ref=(54, 3, 4), lang='ko', en='of#2', words=['하나님']),

    # 부정문 일괄에서 떨어져 나온 부사를 되돌림 — cannot→'능히 … 못하는' 처럼
    # 영어 한 낱말이 한국어 둘로 갈리는 자리다.
    dict(ref=(13, 19, 10), lang='ko', en='not#1', words=['않게', '말게']),
    dict(ref=(17, 37, 23), lang='ko', en='cannot', words=['없나니', '수']),
    dict(ref=(18, 15, 5), lang='ko', en='never', words=['아니하리이다', '영영히']),
    dict(ref=(19, 10, 30), lang='ko', en='never', words=['아니하여도', '영영히']),
    dict(ref=(19, 12, 3), lang='ko', en='not#2', words=['아니하느니라', '서지']),
    dict(ref=(19, 30, 8), lang='ko', en='neither', words=['마옵시고#1', '오직']),
    dict(ref=(25, 16, 4), lang='ko', en='nor', words=['아니하였나니', '말하건대']),
    dict(ref=(39, 5, 35), lang='ko', en='Nor', words=['말라#1', '성임이요']),
    dict(ref=(41, 12, 6), lang='ko', en='not#1', words=['아니냐', '그러나']),
    dict(ref=(41, 14, 26), lang='ko', en='cannot', words=['못하고', '능히']),
    dict(ref=(41, 14, 27), lang='ko', en='cannot', words=['못하리라', '능히']),
    dict(ref=(41, 14, 33), lang='ko', en='cannot', words=['못하리라', '능히']),
    dict(ref=(42, 4, 21), lang='ko', en='neither', words=['말고#1', '말을']),
    dict(ref=(42, 6, 35), lang='ko', en='never#1', words=['아니할', '영원히']),
    dict(ref=(42, 10, 28), lang='ko', en='never', words=['아니할', '영원히']),
    dict(ref=(42, 14, 17), lang='ko', en='cannot', words=['못하나니', '능히']),
    dict(ref=(43, 27, 20), lang='ko', en='neither', words=['아니하고', '여망이']),
    dict(ref=(45, 5, 8), lang='ko', en='neither', words=['말고#2', '없는']),
    dict(ref=(45, 7, 10), lang='ko', en='not#2', words=['말고', '자는']),
    dict(ref=(45, 15, 50), lang='ko', en='cannot', words=['아니한', '수', '없고']),
    dict(ref=(57, 10, 1), lang='ko', en='never', words=['없느니라', '언제든지']),
    dict(ref=(58, 4, 2), lang='ko', en='cannot', words=['못하나니', '능히']),
    dict(ref=(60, 1, 8), lang='ko', en='neither', words=['않고', '없는']),
    dict(ref=(61, 2, 4), lang='ko', en='not#2', words=['아니하되', '아노라']),

    # ---- 디모데전서 6:8 ----
    dict(ref=(53, 6, 8), lang='ko', en='food', words=['먹을', '것과']),
    dict(ref=(53, 6, 8), lang='ko', en='raiment', words=['입을', '것이']),
    dict(ref=(53, 6, 8), lang='ko', en='us', words=['우리가']),
    dict(ref=(53, 6, 8), lang='ko', en='therewith', words=['족한']),

    # 딤전 6:8 비게 된 자리 채움 — '줄로'는 맞댈 영어가 없는 명사화 어미라 비워 둔다
    dict(ref=(53, 6, 8), lang='ko', en='be', words=['알']),
    dict(ref=(53, 6, 8), lang='ko', en='let', words=['것이니라']),

    # ---- 호세아 4:2 ----
    dict(ref=(27, 4, 2), lang='ko', en='swearing', words=['저주와']),
    dict(ref=(27, 4, 2), lang='ko', en='lying', words=['사위와']),
    dict(ref=(27, 4, 2), lang='ko', en='stealing', words=['투절과']),
    dict(ref=(27, 4, 2), lang='ko', en='committing', words=['간음뿐이요']),
    dict(ref=(27, 4, 2), lang='ko', en='adultery', words=['간음뿐이요']),
    dict(ref=(27, 4, 2), lang='ko', en='break', words=['강포하여']),
    dict(ref=(27, 4, 2), lang='ko', en='out', words=['강포하여']),
    dict(ref=(27, 4, 2), lang='ko', en='blood#1', words=['피가']),
    dict(ref=(27, 4, 2), lang='ko', en='toucheth', words=['뒤대임이라']),
    dict(ref=(27, 4, 2), lang='ko', en='blood#2', words=['피를']),

    # ---- 고린도전서 15:40 ----
    dict(ref=(45, 15, 40), lang='ko', en='are', words=['있고#1']),
    dict(ref=(45, 15, 40), lang='ko', en='celestial#1', words=['하늘에#1', '속한#1']),
    dict(ref=(45, 15, 40), lang='ko', en='bodies#1', words=['형체도#1']),
    dict(ref=(45, 15, 40), lang='ko', en='bodies#2', words=['형체도#2']),
    dict(ref=(45, 15, 40), lang='ko', en='terrestrial#1', words=['땅에#1', '속한#2']),
    dict(ref=(45, 15, 40), lang='ko', en='the#2', words=['하늘에#2', '속한#3', '자의#1']),
    dict(ref=(45, 15, 40), lang='ko', en='celestial#2', words=['하늘에#2', '속한#3', '자의#1']),
    dict(ref=(45, 15, 40), lang='ko', en='one', words=['따로#1', '있고#2']),
    dict(ref=(45, 15, 40), lang='ko', en='the#4', words=['땅에#2', '속한#4', '자의#2']),
    dict(ref=(45, 15, 40), lang='ko', en='terrestrial#2', words=['땅에#2', '속한#4', '자의#2']),
    dict(ref=(45, 15, 40), lang='ko', en='another', words=['따로#2', '있으니']),

    # 비게 된 자리 채움 — '-으나'가 but 의 뜻을 담고 있다
    dict(ref=(27, 4, 2), lang='ko', en='By', words=['오직']),
    dict(ref=(45, 15, 40), lang='ko', en='but', words=['있으나']),

    # ---- 잠언 25:17 ----
    dict(ref=(19, 25, 17), lang='ko', en='thy#2', words=['이웃집에']),
    dict(ref=(19, 25, 17), lang='ko', en='neighbour', words=['이웃집에']),
    dict(ref=(19, 25, 17), lang='ko', en='s', words=['이웃집에']),
    dict(ref=(19, 25, 17), lang='ko', en='house', words=['이웃집에']),
    dict(ref=(19, 25, 17), lang='ko', en='lest', words=[]),
    dict(ref=(19, 25, 17), lang='ko', en='he', words=['그가']),
    dict(ref=(19, 25, 17), lang='ko', en='weary', words=['싫어하며']),
    dict(ref=(19, 25, 17), lang='ko', en='thee#1', words=['너를']),
    dict(ref=(19, 25, 17), lang='ko', en='and', words=[]),
    dict(ref=(19, 25, 17), lang='ko', en='hate', words=['미워할까']),
    dict(ref=(19, 25, 17), lang='ko', en='thee#2', words=['너를']),
    # 비게 된 자리 채움
    dict(ref=(19, 25, 17), lang='ko', en='Withdraw', words=['다니지', '말라']),
    dict(ref=(19, 25, 17), lang='ko', en='thy#1', words=['너는']),

    # ---- 시편 129:7 ----  not/nor 가 한국어 부정 어미 하나('아니하나니')를 함께 쓴다
    dict(ref=(18, 129, 7), lang='ko', en='the', words=['베는']),
    dict(ref=(18, 129, 7), lang='ko', en='mower', words=['자의#1']),
    dict(ref=(18, 129, 7), lang='ko', en='filleth', words=['차지']),
    dict(ref=(18, 129, 7), lang='ko', en='not', words=['아니하나니']),
    dict(ref=(18, 129, 7), lang='ko', en='his#1', words=['줌과']),
    dict(ref=(18, 129, 7), lang='ko', en='hand', words=['줌과']),
    dict(ref=(18, 129, 7), lang='ko', en='nor', words=['아니하나니']),
    dict(ref=(18, 129, 7), lang='ko', en='he', words=['자의#2']),
    dict(ref=(18, 129, 7), lang='ko', en='that', words=['자의#2']),
    dict(ref=(18, 129, 7), lang='ko', en='bindeth', words=['묶는']),
    dict(ref=(18, 129, 7), lang='ko', en='sheaves', words=['묶는', '차지']),
    dict(ref=(18, 129, 7), lang='ko', en='his#2', words=['품에']),
    # 비게 된 자리 채움
    dict(ref=(18, 129, 7), lang='ko', en='Wherewith', words=['이런', '것은']),

    # ---- 욥기 34:30 ----
    # '이는'은 일부러 비워 둔다 — That 에 맞댈 자리가 아니다.
    # 빈 자리를 메우는 일괄 작업은 여기를 건드리지 말아야 한다.
    dict(ref=(17, 34, 30), lang='ko', en='That', words=[]),
    dict(ref=(17, 34, 30), lang='ko', en='the#1', words=['사특한', '자로', '함해하지']),
    dict(ref=(17, 34, 30), lang='ko', en='hypocrite', words=['사특한', '자로', '함해하지']),
    dict(ref=(17, 34, 30), lang='ko', en='reign', words=['권세를', '잡아']),
    dict(ref=(17, 34, 30), lang='ko', en='not', words=['못하게']),
    dict(ref=(17, 34, 30), lang='ko', en='lest', words=['하려']),
    dict(ref=(17, 34, 30), lang='ko', en='ensnared', words=['함해하지']),
    # 비게 된 자리 채움 — be 는 '하심이니라'(이다)에 맞댄다
    dict(ref=(17, 34, 30), lang='ko', en='be', words=['하심이니라']),

    # ---- 에스겔 40:18 ----
    dict(ref=(25, 40, 18), lang='ko', en='the#1', words=['박석#1', '깔린', '땅의']),
    dict(ref=(25, 40, 18), lang='ko', en='pavement#1', words=['박석#1', '깔린', '땅의']),
    dict(ref=(25, 40, 18), lang='ko', en='the#2', words=['좌우편인데']),
    dict(ref=(25, 40, 18), lang='ko', en='side', words=['좌우편인데']),
    dict(ref=(25, 40, 18), lang='ko', en='of#1', words=['각', '문간의']),
    dict(ref=(25, 40, 18), lang='ko', en='the#3', words=['각', '문간의']),
    dict(ref=(25, 40, 18), lang='ko', en='gates#1', words=['각', '문간의']),
    dict(ref=(25, 40, 18), lang='ko', en='the#4', words=['길이와']),
    dict(ref=(25, 40, 18), lang='ko', en='length', words=['길이와']),
    dict(ref=(25, 40, 18), lang='ko', en='of#2', words=['문간']),
    dict(ref=(25, 40, 18), lang='ko', en='the#5', words=['문간']),
    dict(ref=(25, 40, 18), lang='ko', en='gates#2', words=['문간']),
    dict(ref=(25, 40, 18), lang='ko', en='lower', words=['아래']),
    dict(ref=(25, 40, 18), lang='ko', en='pavement#2', words=['박석#2', '땅이며']),
    # 비게 된 자리 채움 — 'over against'(…에 맞먹는)이 '그 광이'에 해당한다
    dict(ref=(25, 40, 18), lang='ko', en='And', words=['그#1']),
    dict(ref=(25, 40, 18), lang='ko', en='by', words=['위치는']),
    dict(ref=(25, 40, 18), lang='ko', en='over', words=['그#2', '광이']),
    dict(ref=(25, 40, 18), lang='ko', en='against', words=['그#2', '광이']),
    dict(ref=(25, 40, 18), lang='ko', en='was', words=['같으니']),
    dict(ref=(25, 40, 18), lang='ko', en='the#6', words=['이는']),

    # 겔 40:18 되고침 — 'over against'는 '같으니'(…에 맞먹는)에 해당한다.
    # '그 광이'는 KJV 에 없는 말이라 일부러 비워 둔다. 개역한글이 '그 광이 …
    # 같으니'로 풀어 옮겨서 맞댈 영어 낱말이 없다. 빈 자리를 메우는 일괄
    # 작업은 여기를 건드리지 말아야 한다.
    dict(ref=(25, 40, 18), lang='ko', en='over', words=['같으니']),
    dict(ref=(25, 40, 18), lang='ko', en='against', words=['같으니']),
    dict(ref=(25, 40, 18), lang='ko', en='was', words=['이는']),
    dict(ref=(25, 40, 18), lang='ko', en='the#6', words=['박석#2', '땅이며']),

    # ---- 시편 63:10 ----
    dict(ref=(18, 63, 10), lang='ko', en='the', words=['칼의']),
    dict(ref=(18, 63, 10), lang='ko', en='sword', words=['칼의']),
    dict(ref=(18, 63, 10), lang='ko', en='shall#2', words=['되리이다']),
    dict(ref=(18, 63, 10), lang='ko', en='be', words=['되리이다']),
    dict(ref=(18, 63, 10), lang='ko', en='a', words=['붙인바', '밥이']),
    dict(ref=(18, 63, 10), lang='ko', en='portion', words=['붙인바', '밥이']),
    dict(ref=(18, 63, 10), lang='ko', en='for', words=['시랑의']),
    dict(ref=(18, 63, 10), lang='ko', en='foxes', words=['시랑의']),
    # '세력에'와 '되어'는 일부러 비워 둔다 — by/fall 에 맞댈 자리가 아니다.
    # 빈 자리를 메우는 일괄 작업은 여기를 건드리지 말아야 한다.

]

# ref의 절 자리에 목록을 적으면 (되풀이되는 표현을 한 줄로 적을 수 있다) 절마다 하나씩 펼친다
FIX = [{**e, 'ref': (e['ref'][0], e['ref'][1], v)} for e in FIX
       for v in (e['ref'][2] if isinstance(e['ref'][2], (list, tuple)) else [e['ref'][2]])]

def words_of(lang, b, c, v, al=None):
    # 원어 본문은 따로 파일이 없고 정렬 파일 안에 들어 있다
    if lang == 'or':
        o = (al or {}).get('or') or []
        if c > len(o) or v > len(o[c-1]): return None
        return toks(o[c-1][v-1])
    f = f'{TX}{lang}{(VULG[b] if lang == "la" else b):02d}.json'
    if not os.path.exists(f): return None
    t = json.load(open(f, encoding='utf-8'))
    if c > len(t) or v > len(t[c-1]): return None
    return toks(t[c-1][v-1])

def find(words, want, what):
    """'낱말' 또는 '낱말#2' -> 그 낱말의 자리. 못 찾거나 여럿이면 그대로 알린다."""
    w, _, nth = want.partition('#')
    at = [i for i, x in enumerate(words) if x == w]
    if not at: return None, f'{what} 낱말 {w!r} 이 절에 없음'
    if nth:
        k = int(nth) - 1
        if k >= len(at): return None, f'{what} 낱말 {w!r} 이 절에 {len(at)}번만 나옴 (#{nth} 요청)'
        return at[k], None
    if len(at) > 1: return None, f'{what} 낱말 {w!r} 이 절에 {len(at)}번 나옴 — #번호를 붙이세요'
    return at[0], None

def main():
    done = fail = 0
    for b in sorted({e['ref'][0] for e in FIX}):
        f = f'{D}al{b:02d}.json'
        al = json.load(open(f, encoding='utf-8'))
        touched = False
        for e in [x for x in FIX if x['ref'][0] == b]:
            _, c, v = e['ref']; lang = e['lang']
            tag = f"{b}권 {c}:{v} {lang} {e['en']!r}"
            ew = words_of('en', b, c, v); tw = words_of(lang, b, c, v, al)
            rec = (al['v'][c-1][v-1] if c <= len(al['v']) and v <= len(al['v'][c-1]) else None)
            if ew is None or tw is None or rec is None:
                print(f'  건너뜀 {tag}: 본문이나 정렬이 없음', file=sys.stderr); fail += 1; continue
            ei, err = find(ew, e['en'], '영어')
            if err: print(f'  건너뜀 {tag}: {err}', file=sys.stderr); fail += 1; continue
            idx, bad = [], None
            for want in e['words']:
                i, err = find(tw, want, lang)
                if err: bad = err; break
                idx.append(i)
            if bad: print(f'  건너뜀 {tag}: {bad}', file=sys.stderr); fail += 1; continue
            p = rec.get(lang) or []
            keep = [(x, y) for x, y in zip(p[0::2], p[1::2]) if y != ei]
            new = sorted(set(keep) | {(i, ei) for i in idx})
            if new != sorted(set(zip(p[0::2], p[1::2]))):
                rec[lang] = [n for pr in new for n in pr]
                al['v'][c-1][v-1] = rec; touched = True
                print(f'  고침 {tag} → {", ".join(repr(tw[i]) for i in idx) or "연결 없앰"}', file=sys.stderr)
            done += 1
        if touched:
            json.dump(al, open(f, 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
    print(f'손으로 고친 연결 {done}곳 적용' + (f' · 적용 못 함 {fail}곳' if fail else ''), file=sys.stderr)
    return 1 if fail else 0

sys.exit(main())
