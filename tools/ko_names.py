"""Korean names picked from 개역한글 with a particle or a predicate written onto them (룻이, 셈의, 유다라, 아가보라,
엘라사였더라): drop the ending when the Korean grammar allows it and the evidence agrees.

1. the ending must be one a name can take: a case particle (이/가, 은/는, 을/를, 과/와, 의, 에게) or the copula
   이다 in a predicate form (이라/라, 이요/요, 이며/며, 이니/니, 이니라/니라, 이더라/더라, 이었더라/였더라, 이로다/로다)
2. its form must fit the last syllable of what is left: after a final consonant 이라, 이요, 이 ..., after a vowel 라, 요,
   가 ... (실라 cannot be 실 + 라, which would be 실이라; 유다라 can be 유다 + 라)
3. what is left is written as a word of its own elsewhere in 개역한글 (bare, or with another particle) and sounds at
   least as much like the English name; or, for names only ever brought in as "X라 하는" (아가보라 하는 선지자),
   it sounds clearly more like it (드보라 stays: Deborah; 아가보라 -> 아가보: Agabus), or the English name has no
   l/r sound at its end that the 라 could stand for (로데라 -> 로데: Rhoda; 실라 stays: Silas)
"""
import json, os, re
from collections import Counter

# (ending, needs a final consonant before it: True / a vowel: False / either: None)
ENDS = [('이었더라', True), ('였더라', False), ('이더라', True), ('더라', False), ('이니라', True), ('니라', False),
        ('이로다', True), ('로다', False), ('이라', True), ('라', False), ('이요', True), ('요', False), ('이며', True), ('며', False),
        ('이니', True), ('에게', None), ('의', None), ('이', True), ('가', False), ('은', True), ('는', False),
        ('을', True), ('를', False), ('과', True), ('와', False)]
OTHER = ('은', '는', '을', '를', '에게', '의', '과', '와', '이', '가', '이라', '라', '도')

def final_consonant(syl):
    o = ord(syl) - 0xAC00
    return None if not (0 <= o < 11172) else (o % 28) != 0

_KOW = None
def _words(text_dir):
    global _KOW
    if _KOW is None:
        W = re.compile(r'[^\W\d_]+'); _KOW = Counter()
        for b in range(66):
            for ch in json.load(open(os.path.join(text_dir, f'ko{b:02d}.json'), encoding='utf-8')):
                for v in ch: _KOW.update(W.findall(v or ''))
    return _KOW

def ko_bare(nm, en, text_dir, sim, key_ko, key_lat, skip=()):
    """skip: endings not to drop (place names: 와/과, as in 기브롯핫다아와)"""
    if not nm: return nm
    kw = _words(text_dir)
    for _ in range(2):                         # 브나야였더라 -> 브나야
        for e, cons in ENDS:
            if e in skip or not (nm.endswith(e) and len(nm) > len(e)): continue
            st = nm[:-len(e)]
            fc = final_consonant(st[-1])
            if fc is None or (cons is not None and fc != cons): continue
            seen = kw[st] + sum(kw[st + q] for q in OTHER if q != e)
            a, b = sim(key_ko(st), key_lat(en)), sim(key_ko(nm), key_lat(en))
            # names brought in as "X라 하는 ..." (아가보라 하는 선지자) are never written otherwise: then the sound alone
            # decides, and must clearly prefer the shorter form
            no_l = e == '라' and not re.search(r'[lr]', en.lower()[-4:])     # 로데라: Rhoda has no l/r sound at its end
            if (seen >= 1 and a >= b) or a >= b + 0.05 or no_l:
                nm = st; break
        else: break
    return nm
