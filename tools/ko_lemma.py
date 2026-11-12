"""한국어 어형의 기본형. mecab-ko-dic의 분해를 쓰고, 없는 자리는 접미사 떼기로 메운다.

mecab-ko-dic (Apache License 2.0, Yongwoon Lee·Yungho Yu)으로 분석한 결과를
.github/workflows/lexdata.yml 이 lexdata 브랜치에 올려 둔다. 사전 자체는 저장소에 없다.
환경 변수 KO_PARSE 로 그 파일(ko_parse.json 또는 .gz)을 가리키면 쓰고, 없으면
접미사 떼기만 쓴다 — 어느 쪽이든 돌아간다.

왜 둘을 합치는가. 접미사 떼기는 '짓다'가 ㅅ-불규칙이라 어간이 '짓'·'지으'·'지'로 쪼개지는
것을 묶지 못한다. 사전의 expression 칸은 그것을 풀어 준다:

    지으셨느니라  →  짓/VV + 으시/EP   →  짓다
    지으시고     →  짓/VV + 으시/EP + 고/EC  →  짓다

거꾸로 사전에 없는 말(개역한글의 옛말 '가라사대', ㅂ-불규칙 '가까우나')은 통째로 한 덩어리로
나오므로, 그 자리는 접미사 떼기에 맡긴다. 억지로 기본형을 만들면 '가까우나다'처럼 더 나빠진다.
"""
import gzip, json, os

# 뜻을 지닌 품사. 어미(E*)·조사(J*)·기호(S*)는 뺀다.
VERB = {'VV', 'VA', 'VX', 'VCP', 'VCN'}          # 용언 — 어간에 '다'를 붙여 사전형으로
NOMINAL = {'NNG', 'NNP', 'NNB', 'NR', 'NP', 'XR', 'XPN',
           'MM', 'MAG', 'MAJ', 'SL', 'SH', 'SN'}
CONTENT = VERB | NOMINAL

_P = None

# 사전이 모르는 성경 이름은 아는 형태소로 쪼개진다. 어느 이름인지는 TIPNR 자료(web/data의
# pi.json·gi.json, 한국어 이름이 둘째 칸)로 알 수 있다. 여호와는 그 목록에 없고
# tools/fix_jehovah.py가 따로 다루므로 여기에 적어 둔다.
EXTRA_NAMES = ('여호와',)


def _names():
    here = os.path.dirname(os.path.abspath(__file__))
    out = set(EXTRA_NAMES)
    for f in ('pi', 'gi'):
        p = os.path.join(here, '..', 'web', 'data', f + '.json')
        if not os.path.exists(p): continue
        try:
            d = json.load(open(p, encoding='utf-8'))
        except Exception:
            continue
        for v in (d.get('n') or {}).values():
            if isinstance(v, list) and len(v) > 1 and v[1]:
                out.add(v[1])
    return out


def _longest_name(w, names):
    for n in range(len(w), 1, -1):
        if w[:n] in names: return w[:n]
    return None


def _load():
    global _P
    f = os.environ.get('KO_PARSE')
    if not f or not os.path.exists(f):
        _P = {}
        return
    op = gzip.open if f.endswith('.gz') else open
    raw = json.load(op(f, 'rt', encoding='utf-8'))
    names = _names()
    out = {}
    for w, ms in raw.items():
        mor = [(m[0], (m[1] or '').split('+')[0])
               for m in ms if isinstance(m, (list, tuple)) and len(m) >= 2 and m[0]]
        heads = [(s, t) for s, t in mor if t in CONTENT]
        if len(heads) != 1:
            # 내용어가 둘 이상이면 사전이 모르는 말을 아는 형태소로 쪼갠 것이다. 성경 이름이
            # 특히 그렇다 — '그나스'(Kenaz) → 그/MM + 나스/NNP, '이간' → 이/MM + 간/NNG.
            # 첫 조각을 기본형으로 삼으면 Kenaz가 '그'와 한 덩어리가 된다. 접미사 떼기에 넘긴다.
            # 내용어가 없는 경우(어미·조사만)도 마찬가지.
            continue
        surf, tag = heads[0]
        if surf == w and len(w) > 1 and tag in VERB:
            # 어형 전체가 한 형태소다 — 사전이 모르는 용언('가라사대' 같은 옛말). 넘긴다.
            continue
        nm = _longest_name(w, names)
        if nm and len(surf) < len(nm):
            # 이름을 이름보다 짧게 잘랐다 — '여호와는' → 여호/NNG + 와/JKB('여호와 함께'로 읽은 것).
            # 접미사 떼기는 이것을 제대로 '여호와'로 둔다. 이름만큼 자른 자리('예수께서' → 예수)는
            # 사전이 맞으니 그대로 쓴다.
            continue
        out[w] = surf + ('다' if tag in VERB else '')
    _P = out


def lemma(w):
    """사전이 아는 어형의 기본형, 모르면 None"""
    if _P is None:
        _load()
    return _P.get(w)


def loaded():
    if _P is None:
        _load()
    return len(_P)
