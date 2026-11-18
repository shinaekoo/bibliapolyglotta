# -*- coding: utf-8 -*-
"""표(CSV)로 낱말 연결을 주고받는 도구.

  내보내기: python3 tools/csv_links.py out 이름누락.csv [--names]
  들여오기: python3 tools/csv_links.py in  이름누락.csv [--dry]

표의 한 줄은 **고쳐야 할 영어 낱말 한 자리**다. '대응한국어' 칸이 비어 있으면
그 줄은 건너뛴다. 적는 법:

  대응한국어에 한국어 낱말을 적는다. 여럿이면 빈칸이나 쉼표로 띄어 적는다.
      다윗에게            → 그 영어 낱말을 '다윗에게' 에 건다
      믿지 아니하는       → 두 낱말에 걸친다
  같은 한국어가 그 절에 여러 번 나오면 #번호를 붙인다 (후보 칸에 그대로 적혀 있다)
      다윗이#2
  연결이 필요 없으면 - 또는 없음 이라고 적는다 (있던 연결을 지운다)

들여오기는 tools/fix_links.py 의 '# ---- 표에서 들여온 것 ----' 자리에 항목을
써 넣기만 한다. 실제 반영은 그 다음에 python3 tools/fix_links.py 를 돌리면 된다.
항목이 이미 있으면 덮어쓴다(같은 절·같은 영어 낱말 기준).
"""
import json, io, os, re, sys, csv, unicodedata, collections

HERE = os.path.dirname(os.path.abspath(__file__))
D = os.path.join(HERE, '..', 'web', 'data') + '/'
TX = os.path.join(HERE, '..', 'text') + '/'
MARK = '    # ---- 표에서 들여온 것 ----\n'
BK = ['창세기','출애굽기','레위기','민수기','신명기','여호수아','사사기','룻기','사무엘상','사무엘하',
      '열왕기상','열왕기하','역대상','역대하','에스라','느헤미야','에스더','욥기','시편','잠언','전도서',
      '아가','이사야','예레미야','예레미야애가','에스겔','다니엘','호세아','요엘','아모스','오바댜','요나',
      '미가','나훔','하박국','스바냐','학개','스가랴','말라기','마태복음','마가복음','누가복음','요한복음',
      '사도행전','로마서','고린도전서','고린도후서','갈라디아서','에베소서','빌립보서','골로새서',
      '데살로니가전서','데살로니가후서','디모데전서','디모데후서','디도서','빌레몬서','히브리서','야고보서',
      '베드로전서','베드로후서','요한일서','요한이서','요한삼서','유다서','요한계시록']
NO = {'-', '–', '없음', '없다', '필요없음', 'x', 'X'}


def toks(s):
    out, cur = [], []
    s = s or ''
    for i, ch in enumerate(s):
        if unicodedata.category(ch)[0] in ('L', 'M'):
            cur.append(ch)
        elif (ch == '–' and cur and i + 1 < len(s)
              and unicodedata.category(s[i + 1])[0] in ('L', 'M')):
            cur.append(ch)
        elif cur:
            out.append(''.join(cur)); cur = []
    if cur: out.append(''.join(cur))
    return out


def nth(words):
    """같은 낱말이 여러 번 나오면 #번호를 붙인 이름표를 돌려준다."""
    cnt = collections.Counter(words)
    seen = collections.Counter()
    out = []
    for w in words:
        seen[w] += 1
        out.append(f'{w}#{seen[w]}' if cnt[w] > 1 else w)
    return out


def names():
    out = {}
    for f in ('pi', 'gi'):
        for row in json.load(io.open(D + f + '.json', encoding='utf-8'))['n'].values():
            e, ko = (row[0] or '').strip(), (row[1] or '').strip()
            if e and ko and e[:1].isupper() and len(ko) >= 2:
                out.setdefault(e, ko)
    return out


def export(path, only_names):
    NM = names() if only_names else None
    rows = []
    for bb in range(66):
        al = json.load(io.open(f'{D}al{bb:02d}.json', encoding='utf-8'))
        EN = json.load(io.open(f'{TX}en{bb:02d}.json', encoding='utf-8'))
        KO = json.load(io.open(f'{TX}ko{bb:02d}.json', encoding='utf-8'))
        for c, chap in enumerate(al['v']):
            for v, rec in enumerate(chap):
                if not rec or c >= len(EN) or v >= len(EN[c]): continue
                E = toks(EN[c][v])
                K = toks(KO[c][v]) if c < len(KO) and v < len(KO[c]) else []
                if not E or not K: continue
                EL, KL = nth(E), nth(K)
                q = rec.get('ko') or []
                enl = {q[i + 1] for i in range(0, len(q), 2)}
                for ei, w in enumerate(E):
                    if ei in enl: continue
                    if NM is not None and w not in NM: continue
                    ko = NM[w] if NM else None
                    cand = [KL[i] for i, x in enumerate(K) if ko and x.startswith(ko)]
                    # 이름 모드에서는 한국어 본문에 그 이름이 실제로 있는 자리만 낸다.
                    # 개역한글이 '그가·저희'로 옮긴 자리는 붙일 낱말이 없어서 정상이고,
                    # So(소 왕)·On(온)처럼 보통 낱말과 겹치는 이름도 이 조건에서 걸러진다.
                    if NM is not None and not cand: continue
                    rows.append([BK[bb], f'{c + 1}:{v + 1}', EL[ei], ko or '', '',
                                 ' '.join(cand), ' '.join(K), EN[c][v]])
    with io.open(path, 'w', encoding='utf-8-sig', newline='') as f:
        w = csv.writer(f)
        w.writerow(['책', '절', '영어낱말', '한국어이름', '대응한국어(여기 적으세요)',
                    '후보', '한국어본문', '영어본문'])
        w.writerows(rows)
    print(f'{len(rows)}줄을 {path} 에 내보냈다')


def imp(path, dry):
    got = []
    with io.open(path, encoding='utf-8-sig') as f:
        for r in csv.DictReader(f):
            書 = (r.get('책') or '').strip()
            절 = (r.get('절') or '').strip()
            en = (r.get('영어낱말') or '').strip()
            ans = (r.get('대응한국어(여기 적으세요)') or r.get('대응한국어') or '').strip()
            if not (書 and 절 and en and ans): continue
            if 書 not in BK:
                print(f'  ? 책 이름을 모르겠다: {書}'); continue
            m = re.match(r'(\d+)\s*[:：]\s*(\d+)$', 절)
            if not m:
                print(f'  ? 절을 모르겠다: {書} {절}'); continue
            ws = [] if ans in NO else [x for x in re.split(r'[,\s]+', ans) if x]
            got.append((BK.index(書), int(m.group(1)), int(m.group(2)), en, ws, 書))
    if not got:
        print('적어 넣은 줄이 없다'); return
    body = ''.join(
        "    dict(ref=(%d, %d, %d), lang='ko', en=%r, words=[%s]),%s\n"
        % (b, c, v, en, ', '.join(repr(x) for x in ws), f'   # {書} {c}:{v}')
        for b, c, v, en, ws, 書 in got)
    p = os.path.join(HERE, 'fix_links.py')
    s = io.open(p, encoding='utf-8').read()
    if MARK in s:
        i = s.index(MARK) + len(MARK)
        j = s.index('\n\n', i) + 1 if '\n\n' in s[i:] else i
        old = s[i:j]
        keep = [ln for ln in old.splitlines(True)
                if not any(f'ref=({b}, {c}, {v})' in ln and f'en={en!r}' in ln
                           for b, c, v, en, _, _ in got)]
        s = s[:i] + ''.join(keep) + body + s[j:]
    else:
        a = '    # ---- 시편 131편 ----'
        s = s.replace(a, MARK + body + '\n' + a, 1)
    print(f'{"(시험) " if dry else ""}{len(got)}줄을 tools/fix_links.py 에 {"넣을 것" if dry else "넣었다"}')
    if dry:
        print(body)
    else:
        io.open(p, 'w', encoding='utf-8').write(s)
        print('이어서 python3 tools/fix_links.py 를 돌리면 반영된다')


if __name__ == '__main__':
    if len(sys.argv) < 3 or sys.argv[1] not in ('out', 'in'):
        print(__doc__); sys.exit(1)
    if sys.argv[1] == 'out':
        export(sys.argv[2], '--names' in sys.argv)
    else:
        imp(sys.argv[2], '--dry' in sys.argv)
