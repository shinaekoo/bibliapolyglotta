# 뚜렷한 짝(영어 낱말 ↔ 한국어 낱말)이 끊어졌거나 한쪽에 몰린 곳을 바로잡는다.
#
# 오늘 손으로 잡은 bridegroom↔신랑, Jews↔유대인 같은 경우가 모두 같은 꼴이었다.
# 한 절에 그 낱말이 한 번만 나오면 정렬이 제대로 걸지만, 두 번 이상 나오면
# 첫 하나에만 몰아 걸고 나머지를 버린다.
#
# 그래서 이 도구는 안전한 경우만 손댄다.
#   영어 n개 · 한국어 m개 이고 n == m  →  나온 순서대로 하나씩 짝지어 준다
#   그 밖의 경우(n != m, 또는 n == 0)  →  손대지 않고 보고만 한다
#
# n == 0 은 KJV에 그 낱말이 아예 없는 자리다. 개역한글이 대명사를 풀어 쓴
# 경우(they → 제자들이)가 많아 사람이 문맥을 봐야 한다.
# n != m 은 한쪽이 묶여 있거나 갈라져 있는 자리라 역시 사람이 봐야 한다.
#
# fix_links 앞에 돌린다. 손으로 고친 연결이 언제나 이긴다.
#   python3 tools/fix_pairs.py            적용
#   python3 tools/fix_pairs.py --dry      적용하지 않고 보고만
#   python3 tools/fix_pairs.py --csv 파일 남은 것을 CSV로

import csv, glob, io, json, os, re, sys, unicodedata

DT = os.path.join(os.path.dirname(__file__), '..', 'web', 'data') + os.sep
TX = os.path.join(os.path.dirname(__file__), '..', 'text') + os.sep

BOOKS = ("창세기 출애굽기 레위기 민수기 신명기 여호수아 사사기 룻기 사무엘상 사무엘하 "
         "열왕기상 열왕기하 역대상 역대하 에스라 느헤미야 에스더 욥기 시편 잠언 전도서 아가 "
         "이사야 예레미야 예레미야애가 에스겔 다니엘 호세아 요엘 아모스 오바댜 요나 미가 나훔 "
         "하박국 스바냐 학개 스가랴 말라기 마태복음 마가복음 누가복음 요한복음 사도행전 로마서 "
         "고린도전서 고린도후서 갈라디아서 에베소서 빌립보서 골로새서 데살로니가전서 "
         "데살로니가후서 디모데전서 디모데후서 디도서 빌레몬서 히브리서 야고보서 베드로전서 "
         "베드로후서 요한일서 요한이서 요한삼서 유다서 요한계시록").split()

# (이름, 한국어 앞머리, 영어 낱말들, 구절 모드)
# 구절 모드가 있으면 그 낱말 차례가 이어 나오는 자리만 센다. '인자'처럼
# 영어가 Son of man 세 낱말인 경우에 쓴다.
PAIRS = [
    ('제자',     '제자',     ['disciple', 'disciples'], None),
    ('바리새인', '바리새인', ['pharisee', 'pharisees'], None),
    ('아버지',   '아버지',   ['father', 'fathers'],     None),
    ('아들',     '아들',     ['son', 'sons', 'child', 'children'], None),
    ('선지자',   '선지자',   ['prophet', 'prophets', 'prophetess'], None),
    ('영광',     '영광',     ['glory', 'glorious', 'gloriously',
                              'glorify', 'glorified', 'glorifieth', 'glorifying'], None),
    ('영화',     '영화',     ['glory', 'glorious', 'gloriously',
                              'glorify', 'glorified', 'glorifieth', 'glorifying'], None),
    ('성령',     '성령',     ['ghost', 'spirit'],       None),
    ('어머니',   '어머니',   ['mother', 'mothers'],     None),
    ('어미',     '어미',     ['mother', 'mothers'],     None),
    ('인자',     '인자',     None,                      ['son', 'of', 'man']),
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


def find_en(E, words, phrase):
    """영어 쪽 자리를 찾는다. 낱말 모드는 [[i], [j], …], 구절 모드는 [[i,i+1,i+2], …]."""
    if phrase:
        n, out = len(phrase), []
        for i in range(len(E) - n + 1):
            if [w.lower() for w in E[i:i + n]] == phrase:
                out.append(list(range(i, i + n)))
        return out
    ws = set(words)
    return [[i] for i, w in enumerate(E) if w.lower() in ws]


def main():
    dry = '--dry' in sys.argv
    csvpath = None
    if '--csv' in sys.argv:
        csvpath = sys.argv[sys.argv.index('--csv') + 1]

    done = {n: 0 for n, _, _, _ in PAIRS}
    left = {n: 0 for n, _, _, _ in PAIRS}
    rows = []
    repoint = []

    for f in sorted(glob.glob(DT + 'al*.json')):
        bb = re.search(r'al(\d+)\.json', f).group(1)
        kp, ep = f'{TX}ko{bb}.json', f'{TX}en{bb}.json'
        if not (os.path.exists(kp) and os.path.exists(ep)):
            continue
        al = json.load(io.open(f, encoding='utf-8'))
        KO = json.load(io.open(kp, encoding='utf-8'))
        EN = json.load(io.open(ep, encoding='utf-8'))
        name = BOOKS[int(bb)] if int(bb) < len(BOOKS) else bb
        hit = False

        for c, chp in enumerate(al['v']):
            for v, rec in enumerate(chp or []):
                if not rec or not rec.get('ko'):
                    continue
                K, E = toks(KO[c][v]), toks(EN[c][v])
                for nm, pre, words, phrase in PAIRS:
                    ki = [i for i, w in enumerate(K) if w.startswith(pre)]
                    if not ki:
                        continue
                    ei = find_en(E, words, phrase)
                    # 구절 모드에서 그 구절이 아예 없으면 다른 뜻의 낱말이다.
                    # 구약의 '인자'는 Son of man 이 아니라 mercy·kindness 다.
                    if phrase and not ei:
                        continue
                    if len(ei) != len(ki) or not ei:
                        left[nm] += len(ki)
                        rows.append([name, f'{c+1}:{v+1}', nm, len(ei), len(ki),
                                     ' '.join(K[i] for i in ki),
                                     '영어에 없음' if not ei else '개수 다름',
                                     ' '.join(K)])
                        continue
                    # 끊어진 한국어 낱말이 하나도 없으면 손대지 않는다.
                    # 이미 제대로 걸려 있는 절의 배치를 흔들지 않기 위해서다.
                    linked = {rec['ko'][i] for i in range(0, len(rec['ko']), 2)}
                    if all(i in linked for i in ki):
                        continue

                    # 개수가 같다 — 나온 순서대로 짝지어 준다.
                    # 단, 그 영어 낱말이 이미 다른 한국어 낱말에 걸려 있으면
                    # 빼앗지 않는다. 그 자리가 맞을 수도 있어서 사람이 봐야 한다
                    # (창 27:38 father=아비에게, 창 47:30 fathers=조상들과 같은 곳).
                    at = {}
                    for i in range(0, len(rec['ko']), 2):
                        at.setdefault(rec['ko'][i + 1], rec['ko'][i])
                    keep = []
                    for kk, grp in zip(ki, ei):
                        if any(j in at and at[j] != kk for j in grp):
                            repoint.append([name, f'{c+1}:{v+1}', nm,
                                            ' '.join(E[j] for j in grp),
                                            K[at[[j for j in grp if j in at][0]]],
                                            K[kk], ' '.join(K)])
                        else:
                            keep.append((kk, grp))
                    if not keep:
                        continue
                    ki = [k for k, _ in keep]
                    ei = [g for _, g in keep]
                    moved = {j for grp in ei for j in grp}
                    q = [x for i in range(0, len(rec['ko']), 2)
                         for x in (rec['ko'][i], rec['ko'][i + 1])
                         if rec['ko'][i + 1] not in moved]
                    new = []
                    for kk, grp in zip(ki, ei):
                        for j in grp:
                            new += [kk, j]
                    rec['ko'] = q + new
                    n_new = sum(1 for i in ki if i not in linked)
                    if n_new:
                        done[nm] += n_new
                        hit = True
        if hit and not dry:
            json.dump(al, io.open(f, 'w', encoding='utf-8'),
                      ensure_ascii=False, separators=(',', ':'))

    print('짝 맞춰 고친 곳' + (' (적용 안 함)' if dry else ''))
    for nm, _, _, _ in PAIRS:
        print(f'  {nm:5s} 고침 {done[nm]:4d}  ·  사람이 봐야 하는 것 {left[nm]:4d}')
    if repoint:
        print(f'\n이미 다른 낱말에 걸려 있어 손대지 않은 곳 {len(repoint)}개 — 사람이 봐야 함')
        for r in repoint:
            print(f'  {r[0]} {r[1]}  {r[2]}: {r[3]} 가 \'{r[4]}\' 에 걸려 있음 (빈 \'{r[5]}\' 대신)')
    if csvpath:
        with io.open(csvpath, 'w', encoding='utf-8-sig', newline='') as fh:
            w = csv.writer(fh)
            w.writerow(['책', '장절', '짝', '영어 개수', '한국어 개수',
                        '한국어 낱말', '까닭', '한국어 본문'])
            w.writerows(rows)
        print(f'  남은 {len(rows)}줄 → {csvpath}')


if __name__ == '__main__':
    main()
