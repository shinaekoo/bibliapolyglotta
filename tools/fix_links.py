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
    r"""앱(web/index.html의 WORD = /[\p{L}\p{M}]+/gu)과 똑같이 낱말을 가른다.

    파이썬 re에는 \p{}가 없고 [^\W\d_]는 결합 기호를 빼므로, 그걸 쓰면 니쿠드가 찍힌
    히브리어가 글자 하나하나로 쪼개져 자리가 어긋난다."""
    out, cur = [], []
    for ch in s or '':
        if unicodedata.category(ch)[0] in ('L', 'M'): cur.append(ch)
        elif cur: out.append(''.join(cur)); cur = []
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
    dict(ref=(9, 23, 31), lang='ko', en='albon', words=['아비알본과']),
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
