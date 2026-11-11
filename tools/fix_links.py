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
