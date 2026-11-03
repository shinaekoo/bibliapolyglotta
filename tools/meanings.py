"""Meanings in the app's languages (ko, en, de, fr), from how the translations render a word.

Input: for one word (a Hebrew/Greek dStrong or a Latin lemma), the words of each translation linked to it
across the Bible, with counts. Output: up to three headwords per language, in dictionary form where it can
be found, pronouns and little words left out:
  ko  verb forms grouped under their stem + 다 (사랑하는, 사랑하면 -> 사랑하다); nouns without particles
  en  WordNet base forms (loved, love -> love; received, receive -> receive)
  de, fr  the infinitive when the translation uses it (nehmen, aimer), else the commonest form
Used by tools/build_orig_lex.py (data/ox*.json "m") and tools/build_latin.py (data/lxL.json, 6th column).
"""
import re
from collections import Counter, defaultdict
import lexres

SKIP = {
 'en': set('i me my mine we us our you ye thee thou thy thine your he him his she her it its they them their this that these those '
           'the a an of and to in for with on at by from as be is was were are am art been shall will not but or so all one also there here then when'.split()),
 'de': set('ich mich mir mein du dich dir dein er ihn ihm sein sie ihr es wir uns unser euch euer ihnen der die das des dem den ein eine einen '
           'und zu in von mit auf an für ist war sind nicht auch so da denn wie aber oder sich soweit gegen'.split()),
 'fr': set('je me moi mon ma mes tu te toi ton ta tes il lui son sa ses elle nous notre vous votre ils leur leurs eux le la les l un une des du de '
           'et à au aux en dans pour par sur ne pas que qui est était sont ce cette ces y se'.split()),
 'ko': set('그 이 저 그들 너희 우리 네 내 나 너 저희 자기 것 자 때 곳 중 및 또 곧 하 되 있 없 아니 '
           '내가 네가 내게 네게 나를 너를 나의 너의 우리가 우리를 우리의 그가 그를 그의 그들이 그들을 그들의 너희가 너희를 너희의 저희가 저희를 저희의 자기의 이것 저것 그것'.split()),
}
# Korean endings that only a verb or adjective takes (not a noun with a particle)
KO_VERB_END = ('로되', '르되', '하되', '한', '할', '서', '러', '하다', '하고', '하며', '하여', '하니', '하시', '하신', '하는', '하면', '하지', '하라', '하리', '한다', '했', '하였',
               '고', '며', '니라', '리라', '도다', '더라', '거늘', '거든', '려고', '러', '면', '지', '어', '아', '여', '았', '었', '였', '시니', '시고', '시며', '심')
# endings after the stem; a 하-verb keeps its 하 (사랑하는 -> 사랑하 -> 사랑하다)
KO_END = sorted(('셨더라 였더라 였으니 였느니라 였고 였다 '
                 '시니라 셨더라 였더라 었더라 았더라 였으니 었으니 니라 리라 더라 느니라 도다 로다 시니 시고 시며 시매 시되 시라 시는 신 실 심 '
                 '었고 았고 었다 았다 되 고 며 매 니 면 지 기 는 은 을 어 아 여 라 사 매 아서 어서 여서 서 러 도다 로다').split(), key=len, reverse=True)
KO_IRR = {'와': '오', '봐': '보', '줘': '주', '해': '하', '돼': '되', '가라사': '가로', '이르러': '이르'}
KO_FIX = {'하': '하'}
KO_PART = sorted('께서는 께서 에게서 에게는 에게 한테 으로써 으로서 으로는 으로 로써 로서 로는 에서는 에서 에는 에도 이여 이시여 이니라 이라 이요 이며 이니 은 는 이 가 을 를 의 도 만 에 로 과 와 여'.split(), key=len, reverse=True)

def ko_head(forms, verbal_word=None, noun=False):
    """a group of Korean forms -> one headword (verbal_word: the whole word is mostly verb forms)"""
    tot = sum(forms.values())
    verbal = sum(n for f, n in forms.items() if f.endswith(KO_VERB_END) and len(f) >= 2)
    # 받은, 받는: 은/는 fit a verb or a noun with a particle; the rest of the word's forms decide, unless the
    # group has the bare word (말, 말을: a noun)
    bare = min(forms, key=len); ambiguous = all(f.endswith(('은', '는', '을', '를', 'ㄴ', '한', '할')) or f == bare for f in forms)
    if noun: pass
    elif verbal >= tot * 0.5 or (verbal_word and ambiguous and not any(bare + p in forms for p in ('을', '를', '이', '가', '의', '은', '는'))):
        stems = Counter()
        for f, n in forms.items():
            s = f
            for _ in range(2):        # 사랑하시는도다 -> 사랑하시는 -> 사랑하시
                for e in KO_END:
                    if s.endswith(e) and len(s) - len(e) >= 1: s = s[:-len(e)]; break
            s = KO_IRR.get(s, s)
            if s.endswith(('했', '한', '할', '함', '해')): s = s[:-1] + '하'        # 사랑한, 사랑할, 사랑해 -> 사랑하
            if s.endswith('시') and len(s) > 1: s = s[:-1]                       # 사랑하시는 -> 사랑하
            stems[s] += n
        s = stems.most_common(1)[0][0]
        return s + ('다' if not s.endswith('다') else '')
    nouns = Counter()
    for f, n in forms.items():
        s = f
        for e in KO_PART:
            if s.endswith(e) and len(s) - len(e) >= (2 if e in ('이', '가', '와', '여') else 1): s = s[:-len(e)]; break
        nouns[s] += n
    return nouns.most_common(1)[0][0]

KJV_BASE = {'saith': 'say', 'said': 'say', 'hath': 'have', 'hast': 'have', 'doth': 'do', 'dost': 'do', 'spake': 'speak', 'art': 'be', 'wast': 'be',
            'shalt': 'shall', 'wilt': 'will', 'begat': 'beget', 'brake': 'break', 'gat': 'get', 'sware': 'swear', 'bare': 'bear'}
def en_head(forms):
    base = Counter()
    for f, n in forms.items():
        if f.lower() in KJV_BASE: base[KJV_BASE[f.lower()]] += n; continue
        w = f.lower(); ls = lexres.lemmas(w)
        # the word itself when WordNet knows it as it is (beginning, pass), else its shortest base form (loved -> love)
        keep = w in ls and (not w.endswith(('ed', 'eth', 'est', 'ing')) or lexres.is_noun(w))     # beginning stays a noun
        base[w if keep or not ls else sorted(ls, key=len)[0]] += n
    return base.most_common(1)[0][0]

def inf_head(lang, forms):
    """German/French: the infinitive if the translation has one in this group, else the commonest form"""
    pat = r'(en|ern|eln)$' if lang == 'de' else r'(er|ir|re|oir)$'
    common = forms.most_common(1)[0][0].lower()
    infs = [(n, f) for f, n in forms.items() if re.search(pat, f) and len(f) > 3 and f.lower()[:4] == common[:4]]
    if lang == 'de' and infs:
        cap = sum(n for f, n in forms.items() if f[:1].isupper())
        if cap > sum(forms.values()) / 2: infs = []          # a noun (Erde, Himmel): keep it as written
    return max(infs)[1] if infs else forms.most_common(1)[0][0]

def headwords(lang, groups, top=3, name=False):
    """groups: [(count, Counter of surface forms)] for one word in one language -> up to `top` headwords"""
    out = Counter()
    if lang == 'ko':
        allf = Counter()
        for n, forms in groups: allf.update(forms)
        tot = sum(allf.values())
        vw = not name and sum(c for f, c in allf.items() if f.endswith(KO_VERB_END) and len(f) >= 2) >= tot * 0.4
    else: vw = None
    for n, forms in groups:
        lowform = {f.lower() if lang != 'de' else f: c for f, c in forms.items()}
        if all(f.lower() in SKIP.get(lang, ()) for f in lowform): continue
        forms = Counter({f: c for f, c in lowform.items() if f.lower() not in SKIP.get(lang, ())})
        if not forms: continue
        h = ko_head(forms, vw, noun=name) if lang == 'ko' else en_head(forms) if lang == 'en' else inf_head(lang, forms)
        if h and h.lower() not in SKIP.get(lang, ()) and len(h) > (0 if lang == 'ko' else 1): out[h] += n
    # one headword per word: forms that start alike are the same word (lieben, liebet; aimer, aimeras; 받, 받다)
    def key(h):
        h = h.lower()
        if lang == 'de' and h.startswith('ge') and len(h) > 5: h = h[2:]
        return h.rstrip('다')[:4] if lang == 'ko' else h[:4]
    merged, order = Counter(), {}
    for h, n in out.most_common():
        k = key(h)
        if k not in order: order[k] = h
        elif lang == 'ko' and h.endswith('다') and not order[k].endswith('다'): order[k] = h
        merged[k] += n
    tot = sum(merged.values())
    res = [order[k] for i, (k, n) in enumerate(merged.most_common(top + 2)) if n >= (2 if i == 0 else 3) and n / max(1, tot) >= (0.06 if i == 0 else 0.08)]
    if lang == 'en': res = res[:1] + [h for h in res[1:] if h not in ('have', 'do', 'be', 'make', 'come')]   # KJV helper verbs
    return res[:top]
