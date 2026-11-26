# -*- coding: utf-8 -*-
"""모인 오류 신고를 읽어 점검하고, 편집기로 넘길 절 목록을 만든다.

앱의 설정 → '오류 신고 모음 · 모두 복사'가 내놓는 글을 그대로 먹는다.
한 줄 꼴(앱의 rptLine 과 같다):

    책0 장 절 | 언어 자리 낱말 | en 자리 낱말 | 갈래 | 쪽지 | 판

쓰는 법

    python3 tools/inbox.py 신고.txt                 # 요약만 본다
    python3 tools/inbox.py 신고.txt --lst /tmp/x.lst # 편집기용 절 목록까지
    python3 tools/inbox.py 신고.txt --fix            # fix_links 뼈대까지 찍는다
    cat 신고.txt | python3 tools/inbox.py -

여러 파일을 한꺼번에 줘도 된다. 같은 자리·같은 갈래는 한 번만 센다.
이미 고친 신고를 가리려면, 지금 자료에서 그 낱말이 걸려 있는지 보고
'고쳐짐?' 칸에 표시해 준다 — 오래된 판에서 온 신고를 솎아내는 데 쓴다.
"""
import collections
import io
import json
import os
import re
import sys
import unicodedata

D = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
NM = ("창세기 출애굽기 레위기 민수기 신명기 여호수아 사사기 룻기 사무엘상 사무엘하 "
      "열왕기상 열왕기하 역대상 역대하 에스라 느헤미야 에스더 욥기 시편 잠언 전도서 아가 "
      "이사야 예레미야 예레미야애가 에스겔 다니엘 호세아 요엘 아모스 오바댜 요나 미가 나훔 "
      "하박국 스바냐 학개 스가랴 말라기 마태복음 마가복음 누가복음 요한복음 사도행전 로마서 "
      "고린도전서 고린도후서 갈라디아서 에베소서 빌립보서 골로새서 데살로니가전서 "
      "데살로니가후서 디모데전서 디모데후서 디도서 빌레몬서 히브리서 야고보서 베드로전서 "
      "베드로후서 요한일서 요한이서 요한삼서 유다서 요한계시록").split()


def toks(s):
    """앱·fix_links 와 같은 낱말 끊기 — 글자 덩이, 낱말 속 엔대시는 붙여 둔다."""
    out, cur = [], []
    s = s or ''
    for i, ch in enumerate(s):
        if unicodedata.category(ch)[0] in ('L', 'M'):
            cur.append(ch)
        elif (ch == '–' and cur and i + 1 < len(s)
              and unicodedata.category(s[i + 1])[0] in ('L', 'M')):
            cur.append(ch)
        elif cur:
            out.append(''.join(cur))
            cur = []
    if cur:
        out.append(''.join(cur))
    return out


def parse(text):
    """신고 글에서 한 줄씩 뽑는다. '##' 로 시작하는 머리글은 건너뛴다."""
    out = []
    for raw in text.splitlines():
        ln = raw.strip()
        if not ln or ln.startswith('#'):
            continue
        f = [x.strip() for x in ln.split('|')]
        if len(f) < 4:
            continue
        ref = f[0].split()
        if not ref or not ref[0].isdigit():
            continue
        b = int(ref[0])
        c = int(ref[1]) if len(ref) > 1 and ref[1].isdigit() else 0
        v = int(ref[2]) if len(ref) > 2 and ref[2].isdigit() else 0
        lang = i = word = ''
        if f[1]:
            a = f[1].split()
            lang = a[0] if a else ''
            i = a[1] if len(a) > 1 else ''
            word = ' '.join(a[2:]) if len(a) > 2 else ''
        enw = ''
        if f[2]:
            a = f[2].split()
            enw = ' '.join(a[2:]) if len(a) > 2 else ''
        out.append(dict(b=b, c=c, v=v, lang=lang, i=i, word=word, enw=enw,
                        kind=f[3], note=f[4] if len(f) > 4 else '',
                        ver=f[5] if len(f) > 5 else ''))
    return out


def linked(r):
    """지금 자료에서 그 낱말이 뭔가에 걸려 있나? — 이미 고쳐진 신고 가리기.

    모르면 None 을 돌려준다(절 정보가 없거나 자료를 못 읽을 때).
    """
    if not (r['lang'] and r['i'].isdigit() and r['c'] and r['v']):
        return None
    ap = os.path.join(D, 'web/data/al%02d.json' % r['b'])
    if not os.path.exists(ap):
        return None
    try:
        al = json.load(io.open(ap, encoding='utf-8'))
        rec = al['v'][r['c'] - 1][r['v'] - 1] or {}
    except Exception:
        return None
    i = int(r['i'])
    if r['lang'] == 'en':
        for lg, pr in rec.items():
            if not isinstance(pr, list):
                continue
            if any(pr[j + 1] == i for j in range(0, len(pr) - 1, 2)):
                return True
        return False
    pr = rec.get(r['lang'])
    if not isinstance(pr, list):
        return False
    return any(pr[j] == i for j in range(0, len(pr) - 1, 2))


def main(argv):
    args = [a for a in argv if not a.startswith('--')]
    opts = [a for a in argv if a.startswith('--')]
    lst = next((a.split('=', 1)[1] for a in opts if a.startswith('--lst=')), None)
    if '--lst' in opts:
        k = argv.index('--lst')
        lst = argv[k + 1] if k + 1 < len(argv) else '/tmp/inbox.lst'
        args = [a for a in args if a != lst]
    if not args:
        print(__doc__)
        return 1

    text = ''
    for a in args:
        text += (sys.stdin.read() if a == '-' else io.open(a, encoding='utf-8').read()) + '\n'
    rows = parse(text)
    if not rows:
        print('읽을 신고가 없습니다. 앱 설정의 "모두 복사"로 나온 글을 그대로 주세요.')
        return 1

    # 같은 자리·같은 갈래는 한 번만
    seen, uniq = set(), []
    for r in rows:
        k = (r['b'], r['c'], r['v'], r['lang'], r['i'], r['kind'])
        if k in seen:
            continue
        seen.add(k)
        uniq.append(r)

    print('신고 %d줄 · 겹침 빼고 %d건' % (len(rows), len(uniq)))
    kc = collections.Counter(r['kind'] for r in uniq)
    print('갈래:', ', '.join('%s %d' % (k, n) for k, n in kc.most_common()))
    vc = collections.Counter(r['ver'] for r in uniq if r['ver'])
    if vc:
        print('판별:', ', '.join('%s %d' % (k, n) for k, n in vc.most_common(8)))
    bc = collections.Counter(r['b'] for r in uniq)
    print('책별:', ', '.join('%s %d' % (NM[b] if b < 66 else b, n)
                             for b, n in bc.most_common(10)))

    done = 0
    print('\n  갈래        어디               낱말              고쳐짐?  쪽지')
    for r in sorted(uniq, key=lambda x: (x['b'], x['c'], x['v'])):
        lk = linked(r)
        if lk:
            done += 1
        where = '%s %d:%d' % (NM[r['b']] if r['b'] < 66 else r['b'], r['c'], r['v'])
        mark = '예' if lk else ('아니오' if lk is False else '—')
        print('  %-10s  %-16s  %-14s  %-6s  %s'
              % (r['kind'][:10], where[:16],
                 ('%s %s' % (r['lang'], r['word']))[:14], mark, r['note'][:40]))
    if done:
        print('\n이미 걸려 있는 자리 %d건 — 옛 판에서 온 신고일 수 있습니다.' % done)

    # 편집기용 절 목록
    verses = sorted({(r['b'], r['c'], r['v']) for r in uniq if r['c'] and r['v']})
    if lst and verses:
        io.open(lst, 'w', encoding='utf-8').write(
            '\n'.join('%d %d %d' % x for x in verses) + '\n')
        print('\n절 목록 %d개 → %s' % (len(verses), lst))
        print('  python3 tools/make_editor.py --verses %s "신고 교정" /tmp/kodo-inbox.html' % lst)

    if '--fix' in opts:
        print('\n# ---- 신고에서 뽑은 뼈대 (낱말은 손으로 채운다) ----')
        for r in sorted(uniq, key=lambda x: (x['b'], x['c'], x['v'])):
            if not (r['c'] and r['v'] and r['lang'] and r['word']):
                continue
            print("    dict(ref=(%d, %d, %d), lang=%r, en=%r, words=[]),  # %s · %s"
                  % (r['b'], r['c'], r['v'], r['lang'], r['enw'] or '?',
                     r['kind'], r['note'][:40]))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
