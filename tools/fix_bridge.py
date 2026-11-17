# 개역한글이 두 절을 한 절로 합쳐 놓고 뒷절에 "상동"만 적어 둔 곳을 맞춰 준다.
#
# 원본 본문은 고치지 않는다. 대신 나머지 언어의 두 절을 하나로 이어 붙여서
# 앞절 자리에 넣고, 뒷절은 비운다. 낱말 대응도 뒷절 짝의 번호를 앞절 낱말 수만큼
# 밀어서 함께 옮긴다. 앱은 그 줄의 번호를 "10-11"처럼 묶어서 보여 준다.
#
# fix_jehovah·fix_names 다음, fix_links 앞에 돌린다. fix_links 가 묶인 뒤의
# 낱말 번호로 손 교정을 적고 있으므로 순서를 바꾸면 안 된다. 여러 번 돌려도 안전하다.

import io, json, os, re, sys, unicodedata

TX = os.path.join(os.path.dirname(__file__), '..', 'text') + os.sep
DT = os.path.join(os.path.dirname(__file__), '..', 'web', 'data') + os.sep

ALL = ["or", "la", "en", "de", "fr", "ko", "zh", "es", "it", "ru", "ja", "pt"]
LAIDX = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 18, 19, 20, 21, 22, 23,
         26, 27, 28, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43,
         46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64,
         65, 66, 67, 68, 69, 70, 71, 72]

# (책0, 장, 앞절, 뒷절) — 한국어가 합쳐져 있고 뒷절이 "상동"인 곳
BRIDGE = [
    (17, 35, 10, 11),   # 욥기
]

# 아직 사람이 확인하지 않아 손대지 않는 곳
PENDING = [
    (12, 16, 12, 13),   # 역대상 — 한글 어순이 KJV와 뒤집혀 있음
    (17, 31, 33, 34),   # 욥기 — 한글 어순이 KJV와 뒤집혀 있음
]


def toks(s):
    out, cur = [], []
    for ch in s or '':
        if unicodedata.category(ch)[0] in ('L', 'M'):
            cur.append(ch)
        elif cur:
            out.append(''.join(cur)); cur = []
    if cur:
        out.append(''.join(cur))
    return out


def load(p):
    return json.load(io.open(p, encoding='utf-8'))


def save(p, o):
    json.dump(o, io.open(p, 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))


def main():
    done = []
    for b0, ch, va, vb in BRIDGE:
        c, ia, ib = ch - 1, va - 1, vb - 1

        # 1. 본문 — 뒷절을 앞절에 이어 붙이고 뒷절은 비운다
        texts = {}
        for lg in ALL:
            if lg == 'or':
                continue
            bb = LAIDX[b0] if lg == 'la' else b0
            p = f'{TX}{lg}{bb:02d}.json'
            if not os.path.exists(p):
                continue
            T = load(p)
            if c >= len(T) or ib >= len(T[c]):
                continue
            a, bt = (T[c][ia] or '').strip(), (T[c][ib] or '').strip()
            if bt == '상동':          # 이미 합쳐져 있는 본문 — 뒷절만 비우고 짝은 버린다
                T[c][ib] = ''
                texts[lg] = (p, T, None)
                save(p, T)
                continue
            if bt:
                T[c][ia] = (a + ' ' + bt).strip()
                T[c][ib] = ''
            texts[lg] = (p, T, len(toks(a)))
            save(p, T)

        # 2. 대응 — 뒷절 짝의 번호를 앞절 낱말 수만큼 밀어 앞절로 옮긴다
        al = load(f'{DT}al{b0:02d}.json')
        EN = load(f'{TX}en{b0:02d}.json')      # 이미 합쳐진 본문
        enoff = texts['en'][2] if 'en' in texts else 0

        ra, rb = al['v'][c][ia] or {}, al['v'][c][ib] or {}
        for lg in list(rb.keys()):
            off = texts.get(lg, (None, None, 0))[2]
            if lg == 'or':
                off = len(toks(al['or'][c][ia]))
            if off is None:      # 본문이 이미 합쳐져 있던 언어 — 뒷절 짝은 버린다
                continue
            moved = []
            q = rb[lg] or []
            for i in range(0, len(q), 2):
                moved += [q[i] + off, q[i + 1] + enoff]
            ra[lg] = (ra.get(lg) or []) + moved
        al['v'][c][ia] = ra
        al['v'][c][ib] = {}

        # 3. 원어 본문·낱말 정보
        for k in ('or', 'ow'):
            if k in al and al[k][c][ib]:
                al[k][c][ia] = ((al[k][c][ia] or '') + ' ' + al[k][c][ib]).strip()
                al[k][c][ib] = ''

        # 4. 라틴어 분석
        lx = al.get('lx', {}).get(str(ch))
        if lx and f'v{vb}' in lx:
            lx[f'v{va}'] = (lx.get(f'v{va}') or []) + lx.pop(f'v{vb}')

        save(f'{DT}al{b0:02d}.json', al)
        done.append(f'{b0}권 {ch}:{va}-{vb} ({len(toks(EN[c][ia]))}낱말)')

    print('절 묶음 ' + ('· '.join(done) if done else '없음'))
    if PENDING:
        print('확인 대기 ' + ' · '.join(f'{b}권 {c}:{a}-{d}' for b, c, a, d in PENDING))


if __name__ == '__main__':
    main()
