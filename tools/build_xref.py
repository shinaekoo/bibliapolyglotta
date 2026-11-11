#!/usr/bin/env python3
"""신약이 구약을 인용한 자리를 web/data/xref.json으로 만든다.

목록은 이 파일에 손으로 적는다. 바깥에서 받아 온 자료가 아니라 "히브리서 1:5가
시편 2:7을 인용한다"는 사실 정보를 적어 둔 것이어서 새로 따를 라이선스가 없다.

절 번호만 적어 두면 본문이 한 번이라도 옮겨질 때(tools/verse_map.py가 장절을
KJV 기준으로 옮긴다) 번호는 조용히 어긋난다. 그래서 신약·구약 양쪽에 그 자리에
반드시 있어야 하는 영어 낱말을 하나씩 같이 적고, 빌드 때마다 대조한다. 못 찾으면
소리를 내고 멈춘다.

  k: 인용의 성격
     d 직접 — 말이 거의 그대로다
     g 칠십인역 — 히브리어 본문과 다른 자리다. 신약이 그리스어 구약을 인용했다
     s 뜻 — 말을 그대로 옮기지 않고 뜻만 가져왔다
  a: (신약 쪽 낱말, 구약 쪽 낱말) — 검증용 닻
  n: 무엇이 다른지 한 줄 설명(칠십인역 인용 등 설명할 것이 있는 자리에만)
"""
import json, os, re, sys, unicodedata

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TX = os.path.join(ROOT, 'text')
OUT = os.path.join(ROOT, 'web', 'data', 'xref.json')

BK = ('GEN EXO LEV NUM DEU JOS JDG RUT 1SA 2SA 1KI 2KI 1CH 2CH EZR NEH EST JOB PSA PRO '
      'ECC SNG ISA JER LAM EZK DAN HOS JOL AMO OBA JON MIC NAM HAB ZEP HAG ZEC MAL MAT '
      'MRK LUK JHN ACT ROM 1CO 2CO GAL EPH PHP COL 1TH 2TH 1TI 2TI TIT PHM HEB JAS 1PE '
      '2PE 1JN 2JN 3JN JUD REV').split()
NO = {n: i for i, n in enumerate(BK)}
KO = ('창 출 레 민 신 수 삿 룻 삼상 삼하 왕상 왕하 대상 대하 스 느 에 욥 시 잠 전 아 사 렘 애 겔 단 호 욜 암 옵 욘 미 나 합 습 학 슥 말 '
      '마 막 눅 요 행 롬 고전 고후 갈 엡 빌 골 살전 살후 딤전 딤후 딛 몬 히 약 벧전 벧후 요일 요이 요삼 유 계').split()

# ─────────────────────────────────────────────────────────────────────────────
# 인용 목록. ('신약 참조', '구약 참조', 성격, (신약 닻, 구약 닻), 설명)
# 참조는 'HEB 1:5' 또는 'PSA 102:25-27' 꼴.
# ─────────────────────────────────────────────────────────────────────────────
Q = [
 ('HEB 1:5',    'PSA 2:7',       'd', ('begotten', 'begotten'), ''),
 ('HEB 1:5',    '2SA 7:14',      'd', ('Father', 'father'), ''),
 ('HEB 1:6',    'PSA 97:7',      'g', ('angels', 'worship'),
  '히브리어는 "모든 신들아 그를 경배하라". 칠십인역이 "신들"을 "천사들"로 옮겼고 히브리서가 그 쪽을 인용했다. 신명기 32:43 칠십인역에도 같은 구절이 있다.'),
 ('HEB 1:7',    'PSA 104:4',     'g', ('spirits', 'angels'),
  '히브리어는 "바람을 자기 사자로 삼으시며"로도 읽힌다. 칠십인역은 "자기 천사들을 바람으로 삼으시고"로 읽어 주와 목적어가 뒤바뀐다.'),
 ('HEB 1:8',    'PSA 45:6-7',    'd', ('sceptre', 'sceptre'), ''),
 ('HEB 1:10-12','PSA 102:25-27', 'g', ('foundation', 'foundation'),
  '칠십인역에는 히브리어에 없는 "주여"가 붙어 있다. 히브리서는 이 호칭을 근거로 이 구절을 아들에게 돌린다.'),
 ('HEB 1:13',   'PSA 110:1',     'd', ('footstool', 'footstool'), ''),
 ('HEB 2:6-8',  'PSA 8:4-6',     'g', ('mindful', 'mindful'),
  '히브리어는 "하나님보다 조금 못하게". 칠십인역이 "천사들보다 조금 못하게"로 옮겼고, 히브리서의 논증이 이 읽기에 기댄다.'),
 ('HEB 2:12',   'PSA 22:22',     'd', ('declare', 'declare'), ''),
 ('HEB 2:13',   'ISA 8:17-18',   'd', ('children', 'children'), ''),
 ('HEB 3:7-11', 'PSA 95:7-11',   'g', ('harden', 'harden'),
  '칠십인역은 "사십 년 동안"을 앞 문장에 붙여 "내 행사를 보았다"와 이었다. 히브리서가 그대로 따른다.'),
 ('HEB 3:15',   'PSA 95:7-8',    'd', ('harden', 'harden'), ''),
 ('HEB 4:3',    'PSA 95:11',     'd', ('rest', 'rest'), ''),
 ('HEB 4:4',    'GEN 2:2',       'd', ('seventh', 'seventh'), ''),
 ('HEB 4:7',    'PSA 95:7-8',    'd', ('harden', 'harden'), ''),
 ('HEB 5:5',    'PSA 2:7',       'd', ('begotten', 'begotten'), ''),
 ('HEB 5:6',    'PSA 110:4',     'd', ('Melchisedec', 'Melchizedek'), ''),
 ('HEB 6:14',   'GEN 22:17',     'd', ('multiplying', 'multiplying'), ''),
 ('HEB 7:17',   'PSA 110:4',     'd', ('Melchisedec', 'Melchizedek'), ''),
 ('HEB 7:21',   'PSA 110:4',     'd', ('sware', 'sworn'), ''),
 ('HEB 8:5',    'EXO 25:40',     'd', ('pattern', 'pattern'), ''),
 ('HEB 8:8-12', 'JER 31:31-34',  'g', ('covenant', 'covenant'),
  '신약에서 가장 긴 구약 인용이다. 칠십인역을 따라 "내가 그들을 돌아보지 아니하였노라"로 읽는다(히브리어는 "내가 그들의 남편이 되었어도").'),
 ('HEB 9:20',   'EXO 24:8',      'd', ('testament', 'covenant'), ''),
 ('HEB 10:5-7', 'PSA 40:6-8',    'g', ('sacrifice', 'sacrifice'),
  '히브리어는 "내 귀를 통하여 주셨으며", 칠십인역은 "내게 몸을 예비하셨도다". 히브리서 10:5-10의 논증 전체가 칠십인역 읽기에 기댄다.'),
 ('HEB 10:16-17','JER 31:33-34', 'g', ('iniquities', 'iniquity'),
  '8:8-12에서 인용한 예레미야를 줄여 다시 인용한다.'),
 ('HEB 10:30',  'DEU 32:35-36',  'g', ('vengeance', 'vengeance'),
  '"원수 갚는 것이 내게 있으니"는 히브리어와 칠십인역이 다른데, 히브리서는 로마서 12:19와 같은 꼴로 인용한다.'),
 ('HEB 10:37-38','HAB 2:3-4',    'g', ('faith', 'faith'),
  '칠십인역은 두 행의 차례를 바꾸어 "뒤로 물러가면"을 앞에 둔다. 히브리서가 그 차례를 따른다.'),
 ('HEB 11:5',   'GEN 5:24',      'd', ('translated', 'Enoch'), ''),
 ('HEB 11:18',  'GEN 21:12',     'd', ('Isaac', 'Isaac'), ''),
 ('HEB 12:5-6', 'PRO 3:11-12',   'd', ('chastening', 'chastening'), ''),
 ('HEB 12:20',  'EXO 19:12-13',  's', ('stoned', 'stoned'),
  '출애굽기의 명령을 줄여 옮겼다.'),
 ('HEB 12:21',  'DEU 9:19',      's', ('quake', 'afraid'),
  '모세의 말을 그대로 옮기지 않고 뜻을 가져왔다. 칠십인역 신명기 9:19의 "내가 두렵다"를 따른다.'),
 ('HEB 12:26',  'HAG 2:6',       'g', ('shake', 'shake'),
  '칠십인역을 줄여 "땅만 아니라 하늘도"로 옮겼다.'),
 ('HEB 13:5',   'DEU 31:6',      'g', ('forsake', 'forsake'), ''),
 ('HEB 13:5',   'JOS 1:5',       'g', ('forsake', 'forsake'), ''),
 ('HEB 13:6',   'PSA 118:6',     'g', ('helper', 'fear'),
  '칠십인역은 "주는 나를 돕는 자시니"로 읽는다(히브리어는 "여호와는 내 편이시라").'),
]

# ─────────────────────────────────────────────────────────────────────────────

REF = re.compile(r'^(\S+)\s+(\d+):(\d+)(?:-(\d+))?$')


def parse(ref):
    m = REF.match(ref)
    if not m:
        sys.exit(f'참조를 읽을 수 없음: {ref!r}')
    name, c, v1, v2 = m.groups()
    if name not in NO:
        sys.exit(f'책 이름을 모름: {name!r} ({ref})')
    return NO[name], int(c), int(v1), int(v2 or v1)


def toks(s):
    """앱과 같은 낱말 나누기 — /[\\p{L}\\p{M}]+/gu."""
    out, cur = [], []
    for ch in s or '':
        if unicodedata.category(ch)[0] in ('L', 'M'):
            cur.append(ch)
        elif cur:
            out.append(''.join(cur)); cur = []
    if cur:
        out.append(''.join(cur))
    return out


CACHE = {}


def book(b):
    if b not in CACHE:
        p = os.path.join(TX, f'en{b:02d}.json')
        if not os.path.exists(p):
            sys.exit(f'본문 없음: {p}')
        CACHE[b] = json.load(open(p, encoding='utf-8'))
    return CACHE[b]


def span(b, c, v1, v2):
    t = book(b)
    if c > len(t):
        return None
    ch = t[c - 1]
    if v2 > len(ch):
        return None
    return ' '.join(ch[v1 - 1:v2])


def main():
    force = '--force' in sys.argv
    recs, bad = [], []
    for nt, ot, kind, (a1, a2), note in Q:
        nb, nc, nv1, nv2 = parse(nt)
        ob, oc, ov1, ov2 = parse(ot)
        ns, os_ = span(nb, nc, nv1, nv2), span(ob, oc, ov1, ov2)
        for lbl, s, ref in (('신약', ns, nt), ('구약', os_, ot)):
            if s is None:
                bad.append(f'{nt} ← {ot}: {lbl} {ref} 자리가 본문에 없음')
        if ns is None or os_ is None:
            continue
        nw = {w.lower() for w in toks(ns)}
        ow = {w.lower() for w in toks(os_)}
        if a1.lower() not in nw:
            bad.append(f'{nt} ← {ot}: 신약 쪽에서 {a1!r}를 못 찾음 — 절이 옮겨졌는지 보라')
        if a2.lower() not in ow:
            bad.append(f'{nt} ← {ot}: 구약 쪽에서 {a2!r}를 못 찾음 — 절이 옮겨졌는지 보라')
        # 인용 하나가 기록 하나. 앱이 받아서 신약 쪽·구약 쪽 두 방향 찾기표를 만든다.
        rec = [nb, nc, nv1, nv2, ob, oc, ov1, ov2, kind]
        if note:
            rec.append(note)
        recs.append(rec)

    if bad:
        print('인용 목록과 본문이 어긋남:', file=sys.stderr)
        for b in bad:
            print('  ·', b, file=sys.stderr)
        if not force:
            sys.exit('--force로 무시할 수 있으나, 먼저 목록이나 절 번호를 고치라.')

    # 신약 자리 순으로만 세운다. 한 절이 여러 곳을 인용할 때는 위 목록에 적은 차례를
    # 그대로 둔다(히 1:5는 시편을 먼저, 사무엘을 나중에 인용한다).
    recs.sort(key=lambda r: (r[0], r[1], r[2]))
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    json.dump({'q': recs}, open(OUT, 'w', encoding='utf-8'),
              ensure_ascii=False, separators=(',', ':'))
    kinds = {}
    for r in recs:
        kinds[r[8]] = kinds.get(r[8], 0) + 1
    nt_v = len({(r[0], r[1], v) for r in recs for v in range(r[2], r[3] + 1)})
    ot_v = len({(r[4], r[5], v) for r in recs for v in range(r[6], r[7] + 1)})
    books = sorted({r[0] for r in recs} | {r[4] for r in recs})
    print(f'구약 인용 {len(recs)}곳 '
          f'(직접 {kinds.get("d",0)} · 칠십인역 {kinds.get("g",0)} · 뜻 {kinds.get("s",0)})')
    print(f'  표시되는 절: 신약 {nt_v}개 · 구약 {ot_v}개 · 책 {len(books)}권'
          f' — {" ".join(KO[b] for b in books)}')
    print(f'  {OUT} · {os.path.getsize(OUT):,} 바이트')


if __name__ == '__main__':
    main()
