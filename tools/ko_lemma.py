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


def _load():
    global _P
    f = os.environ.get('KO_PARSE')
    if not f or not os.path.exists(f):
        _P = {}
        return
    op = gzip.open if f.endswith('.gz') else open
    raw = json.load(op(f, 'rt', encoding='utf-8'))
    out = {}
    for w, ms in raw.items():
        lem = None
        for m in ms:
            if not isinstance(m, (list, tuple)) or len(m) < 2:
                continue
            surf, tag = m[0], (m[1] or '').split('+')[0]
            if tag in CONTENT and surf:
                # 어형 전체가 한 형태소로 나왔으면 사전이 모르는 말이다 — 접미사 떼기에 넘긴다
                if surf == w and len(w) > 1 and tag in VERB:
                    break
                lem = surf + ('다' if tag in VERB else '')
                break
        if lem:
            out[w] = lem
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
