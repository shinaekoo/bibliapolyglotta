#!/usr/bin/env python3
"""영어 낱말 사전 -> web/data/ew.json

자료: 웹스터 개정 무삭제판(Webster's Revised Unabridged Dictionary, 1913,
노아 포터 편). 퍼블릭 도메인. Project Gutenberg 가 디지털화한 본문을 쓰되
그쪽 머리말·꼬리말과 상표 조항이 붙는 부분은 담지 않고 사전 본문만 쓴다.

KJV(1769)의 어미와 옛 철자는 표제어와 어긋나므로 tools/en_lemma.py 가
되돌린다. 뜻풀이는 표제어마다 한 번만 담고, 어형은 표제어를 가리키게만 해서
자료 크기를 줄인다.

내놓는 것:
  {"d": {표제어: [품사, [뜻, ...]]},
   "m": {KJV 어형: 표제어 또는 [표제어, 표제어]}}      어형이 표제어와 다를 때만

usage: python3 tools/build_dict_en.py WEBSTER1913.txt
"""
import io, json, os, re, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import en_lemma

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, '..', 'web', 'data', 'ew.json')
KJVW = os.path.join(HERE, 'data', 'kjv_words.json')
SRC = sys.argv[1] if len(sys.argv) > 1 else '/tmp/wd/w1913.txt'

MAXSENSE = 3          # 한 표제어에 담을 뜻의 수
MAXLEN = 240          # 한 뜻의 길이

# 품사. 사전은 'n.' 'v. t.' 'a.' 처럼 적는다.
POS = [
    (r'\bv\.\s*t\.\s*&\s*i\.', '동사'), (r'\bv\.\s*t\.', '동사'),
    (r'\bv\.\s*i\.', '동사'), (r'\bv\.\b', '동사'),
    (r'\bn\.\s*pl\.', '명사(복수)'), (r'\bn\.\b', '명사'),
    (r'\ba\.\b', '형용사'), (r'\badj\.\b', '형용사'),
    (r'\badv\.\b', '부사'), (r'\bprep\.\b', '전치사'),
    (r'\bconj\.\b', '접속사'), (r'\bpron\.\b', '대명사'),
    (r'\binterj\.\b', '감탄사'), (r'\bp\.\s*p\.', '과거분사'),
    (r'\bimp\.\b', '과거'),
]

# 버릴 줄. 어원·보기글·동의어 묶음은 뜻풀이가 아니다.
DROP = re.compile(r'^(Etym:|Note:|Syn\.|Syn:|--|\[|Defn:\s*$)')
# 인용 끝의 지은이. 'The bruit thereof will bring you many friends. Shak.'
CITE = re.compile(r'[.!?]\s+[A-Z][A-Za-z.\'’\- ]{1,24}\.?\s*$')
HEAD = re.compile(r"^([A-Z][A-Z0-9'; \-]*)$")
# 'Hea"then, n.; pl. Heathens' 처럼 표제어·품사만 적은 줄
POSLINE = re.compile(r"^[A-Za-z\"*`'\- ]{2,30}(\s*\([^)]{0,30}\))?,\s*(n|a|v|adv|adj|prep|conj|pron|interj|p)\b")


# 줄임말. 이 뒤의 점은 문장 끝이 아니다.
ABBR = set('''L Gr F E D G OE AS OF OHG MHG MLG LL Sp It Pg Sw Dan Icel Goth
Skr Ar Heb Per Turk Russ Pol Ir Gael W Corn Arm Armor Lith Finn Hung Chin
Jap cf etc esp fr i e pl sing masc fem neut sc viz vb pref suff dim Cf See
St Mr Mrs Dr Prof Rev Jr Sr vol p pp ch v n a adj adv prep conj interj
imp pr pron obs Zool Bot Anat Med Chem Math Mus Naut Mil Law Gram Arch'''.split())


def first_sentence(s):
    """뜻풀이는 보통 한 문장이고 그 뒤는 보기글이다. 첫 문장만 남긴다."""
    for m in re.finditer(r'(?<=[a-z0-9\)\]])\.\s+(?=[A-Z"\'“])', s):
        before = s[:m.start()].rsplit(' ', 1)[-1].strip('([')
        if before in ABBR or len(before) <= 1:
            continue
        if m.start() < 18:                          # 너무 이르면 문장이 아니다
            continue
        return s[:m.start() + 1]
    return s


def tidy(s):
    s = re.sub(r'\s+', ' ', s).strip()
    s = re.sub(r'^Defn:\s*', '', s)
    s = re.sub(r'\s*\(#\)', '', s)
    s = re.sub(r'\[[^\]]{0,80}\]', '', s)          # [imp. & p. p. Bruited]
    s = re.sub(r'\s*;\s*--\s*', '; ', s)
    s = re.sub(r'\s*--\s*', ' ', s)
    s = first_sentence(s)
    s = re.sub(r'\s+([,.;:])', r'\1', s)
    s = s.strip(' ;,-')
    if len(s) > MAXLEN:
        cut = s[:MAXLEN]
        k = max(cut.rfind('. '), cut.rfind('; '))
        s = (cut[:k + 1] if k > MAXLEN // 2 else cut.rstrip() + '…')
    return s


def pos_of(line):
    for pat, name in POS:
        if re.search(pat, line):
            return name
    return ''


def senses(body, head=''):
    """항목 본문에서 뜻만 골라낸다."""
    bare = re.sub(r'[^a-z]', '', head.lower())
    out = []
    for para in re.split(r'\n\s*\n', body):
        p = para.strip()
        if not p or DROP.match(p):
            continue
        p = re.sub(r'\[[^\]]{0,80}\]', ' ', p)       # [Compar. Emptier; superl. Emptiest.]
        p = re.sub(r'\s+', ' ', p).strip()
        # 'Can"ker*worm`, n.' 처럼 표제어와 품사만 있는 토막은 뜻이 아니다
        if bare:
            lead = re.sub(r'[^a-z]', '', p[:len(head) + 6].lower())
            if lead.startswith(bare[:max(4, len(bare) - 1)]) and (
                    len(p) < len(head) + 36 or POSLINE.match(p)):
                continue
        numbered = bool(re.match(r'^\d+\.\s', p)) or p.startswith('Defn:')
        p = re.sub(r'^\d+\.\s*', '', p)             # 뜻 번호
        if p.startswith('['):                       # 닫히지 않은 어원 토막
            continue
        # 뜻 없이 인용문만 있는 토막은 버린다. 뜻 뒤의 인용문은 first_sentence 가 끊는다.
        if not numbered and CITE.search(p) and len(p) < 160:
            continue
        t = tidy(p)
        if len(t) >= 8 and not t.startswith('See '):
            out.append(t)
        if len(out) >= MAXSENSE:
            break
    return out


def parse(path):
    """1913년판 본문 -> {표제어: [품사, [뜻, ...]]}"""
    txt = io.open(path, encoding='utf-8', errors='replace').read()
    # Project Gutenberg 의 머리말·꼬리말은 담지 않는다
    i = txt.find('*** START')
    if i > 0:
        txt = txt[txt.index('\n', i) + 1:]
    j = txt.find('*** END')
    if j > 0:
        txt = txt[:j]

    d = {}
    lines = txt.split('\n')
    cur, buf = None, []

    def flush():
        if not cur or not buf:
            return
        head = cur.lower().split(';')[0].strip()
        if not head or not re.fullmatch(r"[a-z][a-z0-9'\- ]*", head):
            return
        pos = pos_of(buf[0] if buf else '')
        # 어원은 'Etym: [ ... ]' 로 적히고 표제어 줄에서 시작해 여러 줄에 걸친다.
        # 그래서 첫 줄까지 함께 넣고 통째로 뺀다.
        body = '\n'.join(buf)
        body = re.sub(r'Etym:\s*\[.*?\]', ' ', body, flags=re.S)
        body = re.sub(r'Etym:\s*\[[^\]]*\Z', ' ', body, flags=re.S)
        body = re.sub(r'Etym:[^\n]*(\n(?!\s*\n)[^\n]*)*', ' ', body)
        ss = senses(body, head)
        if not ss:
            return
        if head in d:                                # BRUIT 명사 / BRUIT 동사
            old = d[head]
            if old[0] and pos and old[0] != pos:
                old[0] += '·' + pos
            for s in ss:
                if len(old[1]) < MAXSENSE and s not in old[1]:
                    old[1].append(s)
        else:
            d[head] = [pos, ss]

    for ln in lines:
        m = HEAD.match(ln.rstrip())
        if m and len(m.group(1)) >= 2:
            flush()
            cur, buf = m.group(1), []
        elif cur is not None:
            buf.append(ln.rstrip())
    flush()
    return d


def main():
    d = parse(SRC)
    print(f'1913년판에서 읽은 표제어 {len(d):,}')

    kjv = dict(json.load(open(KJVW)))
    alt = {k.replace('-', '').replace(' ', ''): k for k in d if '-' in k or ' ' in k}
    has = lambda w: w in d or w in alt
    real = lambda w: d[w] if w in d else d[alt[w]]
    name = lambda w: w if w in d else alt[w]

    keep, m, miss = {}, {}, []
    for w in kjv:
        got, how = en_lemma.lookup(w, has)
        if not got:
            miss.append(w)
            continue
        if isinstance(got, list):                    # 합성어
            hs = [name(x) for x in got]
            for h in hs:
                keep[h] = real(h)
            m[w] = hs
        else:
            h = name(got)
            keep[h] = real(h)
            if h != w:
                m[w] = h

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    json.dump({'d': keep, 'm': m}, io.open(OUT, 'w', encoding='utf-8'),
              ensure_ascii=False, separators=(',', ':'))
    sz = os.path.getsize(OUT)
    tot = sum(kjv.values())
    cov = sum(kjv[w] for w in kjv if w not in set(miss))
    print(f'담은 표제어 {len(keep):,} · 어형 연결 {len(m):,}')
    print(f'KJV 낱말 {len(kjv) - len(miss):,}/{len(kjv):,} '
          f'({(len(kjv) - len(miss)) / len(kjv) * 100:.1f}%) · 쓰임 {cov / tot * 100:.1f}%')
    print(f'web/data/ew.json {sz / 1e6:.2f}MB')
    miss.sort(key=lambda w: -kjv[w])
    print('못 찾은 것 흔한 순 20개:',
          ', '.join(f'{w}({kjv[w]})' for w in miss[:20]))


if __name__ == '__main__':
    main()
