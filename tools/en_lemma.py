#!/usr/bin/env python3
"""KJV 영어 낱말을 웹스터 사전 표제어로 되돌린다.

KJV(1769)의 철자와 어미는 웹스터(1828·1913)의 표제어와 어긋나는 데가 많다.
publisheth 는 publish 에, morter 는 mortar 에, grapegatherers 는 grape 와
gatherer 에 걸려야 한다. 여기서는 한 낱말에 대해 '찾아볼 표제어 후보'를
좋은 순서로 늘어놓는다. 실제로 어느 것이 사전에 있는지는 부르는 쪽에서 본다.

후보를 만드는 방식만 둔다. 사전은 읽지 않는다.
"""
import re

# 규칙으로 풀 수 없어 손으로 적어 둔 것. KJV 쪽 철자 → 웹스터 쪽 철자.
SPELL = {
    # 옛 철자
    'shew': 'show', 'shewed': 'show', 'shewest': 'show', 'sheweth': 'show',
    'shewing': 'show', 'shewn': 'show', 'shews': 'show',
    'morter': 'mortar', 'pransing': 'prance', 'prancings': 'prance',
    'wellfavoured': 'favor', 'illfavoured': 'favor',
    'enquire': 'inquire', 'enquired': 'inquire', 'enquirest': 'inquire',
    'enquiry': 'inquiry', 'enquiries': 'inquiry',
    'cieled': 'ceil', 'cieling': 'ceiling', 'ceiled': 'ceil',
    'astonied': 'astony', 'basons': 'basin', 'bason': 'basin',
    'chesnut': 'chestnut', 'cloke': 'cloak', 'clokes': 'cloak',
    'drave': 'drive', 'durst': 'dare', 'gat': 'get', 'brake': 'break',
    'spake': 'speak', 'strake': 'strike', 'clave': 'cleave',
    'bewray': 'betray', 'bewrayed': 'betray', 'bewrayeth': 'betray',
    'habergeon': 'habergeon', 'holpen': 'help', 'wot': 'wit',
    'wist': 'wit', 'wotteth': 'wit', 'sith': 'since',
    'alway': 'always', 'ought': 'owe', 'quick': 'quick',
    'sope': 'soap', 'sodden': 'seethe', 'sod': 'seethe',
    'sithes': 'scythe', 'shambles': 'shamble',
    'fats': 'vat', 'fatches': 'vetch', 'fitches': 'vetch',
    'nitre': 'niter', 'saltpetre': 'saltpeter', 'sepulchre': 'sepulcher',
    'centre': 'center', 'fibre': 'fiber', 'theatre': 'theater',
    'plough': 'plow', 'ploughed': 'plow', 'plougher': 'plow',
    'ploughers': 'plow', 'ploughing': 'plow', 'ploughman': 'plowman',
    'ploughmen': 'plowman', 'plowshares': 'plowshare',
    'mould': 'mold', 'moulded': 'mold', 'smote': 'smite',
    'stablish': 'establish', 'stablished': 'establish',
    'subtil': 'subtle', 'subtilly': 'subtle', 'subtilty': 'subtlety',
    'travail': 'travail', 'villany': 'villainy', 'vail': 'veil',
    'wen': 'wen', 'whiles': 'while', 'whilst': 'while',
    'ambassage': 'embassage', 'amerce': 'amerce',
    'dureth': 'dure', 'endue': 'endow', 'endued': 'endow',
    'hoised': 'hoist', 'inclose': 'enclose', 'inclosed': 'enclose',
    'instant': 'instant', 'intreat': 'entreat', 'intreated': 'entreat',
    'intreaties': 'entreaty', 'intreatings': 'entreat',
    'jeopard': 'jeopard', 'leasing': 'leasing', 'lien': 'lie',
    'lift': 'lift', 'marish': 'marsh', 'minish': 'diminish',
    'minished': 'diminish', 'mete': 'mete', 'neesings': 'sneeze',
    'nought': 'naught', 'ouches': 'ouch', 'pate': 'pate',
    'pill': 'peel', 'pilled': 'peel', 'poll': 'poll',
    'pransings': 'prance', 'prevent': 'prevent', 'privily': 'privy',
    'publican': 'publican', 'ranges': 'range', 'ravin': 'raven',
    'ravening': 'raven', 'scall': 'scall', 'scrabbled': 'scrabble',
    'sherd': 'shard', 'sherds': 'shard', 'sojourn': 'sojourn',
    'sperm': 'sperm', 'staves': 'staff', 'stuff': 'stuff',
    'tabering': 'tabor', 'tache': 'tache', 'taches': 'tache',
    'tares': 'tare', 'tire': 'tire', 'tires': 'tire',
    'trow': 'trow', 'twain': 'twain', 'verily': 'verily',
    'wax': 'wax', 'waxed': 'wax', 'waxen': 'wax', 'waxeth': 'wax',
    'wimples': 'wimple', 'wont': 'wont', 'wreathen': 'wreathe',
    'kine': 'cow', 'brethren': 'brother', 'children': 'child',
    'oxen': 'ox', 'mice': 'mouse', 'lice': 'louse', 'geese': 'goose',
    'teeth': 'tooth', 'feet': 'foot', 'men': 'man', 'women': 'woman',
    'swine': 'swine', 'sheep': 'sheep', 'deer': 'deer',
}

# 아주 불규칙한 동사. KJV 는 이쪽을 즐겨 쓴다.
IRREG = {
    'hath': 'have', 'hast': 'have', 'had': 'have', 'having': 'have',
    'saith': 'say', 'said': 'say', 'sayest': 'say', 'saidst': 'say',
    'doth': 'do', 'dost': 'do', 'doeth': 'do', 'did': 'do',
    'didst': 'do', 'done': 'do', 'doest': 'do',
    'art': 'be', 'wast': 'be', 'wert': 'be', 'was': 'be', 'were': 'be',
    'been': 'be', 'being': 'be', 'am': 'be', 'is': 'be', 'are': 'be',
    'shalt': 'shall', 'wilt': 'will', 'canst': 'can', 'couldest': 'could',
    'mayest': 'may', 'mightest': 'might', 'shouldest': 'should',
    'wouldest': 'would', 'knowest': 'know', 'knoweth': 'know',
    'knew': 'know', 'known': 'know', 'went': 'go', 'gone': 'go',
    'goest': 'go', 'goeth': 'go', 'came': 'come', 'camest': 'come',
    'cometh': 'come', 'comest': 'come', 'took': 'take', 'taken': 'take',
    'gave': 'give', 'given': 'give', 'saw': 'see', 'seen': 'see',
    'seest': 'see', 'seeth': 'see', 'made': 'make', 'thought': 'think',
    'brought': 'bring', 'bought': 'buy', 'caught': 'catch',
    'taught': 'teach', 'sought': 'seek', 'fought': 'fight',
    'wrought': 'work', 'begat': 'beget', 'begotten': 'beget',
    'fell': 'fall', 'fallen': 'fall', 'sat': 'sit', 'stood': 'stand',
    'heard': 'hear', 'held': 'hold', 'laid': 'lay', 'lay': 'lie',
    'lain': 'lie', 'led': 'lead', 'left': 'leave', 'lost': 'lose',
    'meant': 'mean', 'met': 'meet', 'paid': 'pay', 'put': 'put',
    'read': 'read', 'ran': 'run', 'rose': 'rise', 'risen': 'rise',
    'sold': 'sell', 'sent': 'send', 'set': 'set', 'shone': 'shine',
    'shot': 'shoot', 'shut': 'shut', 'sang': 'sing', 'sung': 'sing',
    'sank': 'sink', 'slept': 'sleep', 'slew': 'slay', 'slain': 'slay',
    'spoken': 'speak', 'spent': 'spend', 'stole': 'steal',
    'stolen': 'steal', 'swore': 'swear', 'sworn': 'swear',
    'swam': 'swim', 'threw': 'throw', 'thrown': 'throw',
    'trod': 'tread', 'trodden': 'tread', 'understood': 'understand',
    'woke': 'wake', 'wore': 'wear', 'worn': 'wear', 'won': 'win',
    'wrote': 'write', 'written': 'write', 'drank': 'drink',
    'drunk': 'drink', 'drunken': 'drink', 'ate': 'eat', 'eaten': 'eat',
    'eateth': 'eat', 'bare': 'bear', 'borne': 'bear', 'born': 'bear',
    'bade': 'bid', 'bidden': 'bid', 'bound': 'bind', 'bred': 'breed',
    'built': 'build', 'burnt': 'burn', 'burst': 'burst', 'cast': 'cast',
    'chose': 'choose', 'chosen': 'choose', 'clad': 'clothe',
    'clothed': 'clothe', 'cut': 'cut', 'dealt': 'deal', 'dug': 'dig',
    'drew': 'draw', 'drawn': 'draw', 'driven': 'drive', 'dwelt': 'dwell',
    'fed': 'feed', 'felt': 'feel', 'fled': 'flee', 'flew': 'fly',
    'flown': 'fly', 'forgave': 'forgive', 'forgiven': 'forgive',
    'forsook': 'forsake', 'forsaken': 'forsake', 'froze': 'freeze',
    'got': 'get', 'gotten': 'get', 'grew': 'grow', 'grown': 'grow',
    'hid': 'hide', 'hidden': 'hide', 'hung': 'hang', 'hurt': 'hurt',
    'kept': 'keep', 'knelt': 'kneel', 'knit': 'knit', 'lent': 'lend',
    'let': 'let', 'lit': 'light', 'rent': 'rend', 'rid': 'rid',
    'rode': 'ride', 'ridden': 'ride', 'rung': 'ring', 'rang': 'ring',
    'said': 'say', 'shed': 'shed', 'shook': 'shake', 'shaken': 'shake',
    'shorn': 'shear', 'shrank': 'shrink', 'slid': 'slide',
    'smitten': 'smite', 'sowed': 'sow', 'sown': 'sow', 'sped': 'speed',
    'spilt': 'spill', 'spun': 'spin', 'spit': 'spit', 'split': 'split',
    'spread': 'spread', 'sprang': 'spring', 'sprung': 'spring',
    'stuck': 'stick', 'stung': 'sting', 'stank': 'stink',
    'stricken': 'strike', 'struck': 'strike', 'strove': 'strive',
    'striven': 'strive', 'strewed': 'strew', 'strown': 'strew',
    'swept': 'sweep', 'swelled': 'swell', 'swollen': 'swell',
    'swung': 'swing', 'tore': 'tear', 'torn': 'tear', 'told': 'tell',
    'wept': 'weep', 'wound': 'wind', 'woven': 'weave', 'wove': 'weave',
}

VOWELS = set('aeiou')


def _undouble(stem):
    """stopped → stop. 끝 두 글자가 같은 자음이면 하나 뗀다."""
    if len(stem) > 2 and stem[-1] == stem[-2] and stem[-1] not in VOWELS \
            and stem[-1] not in 'lsfz':
        return stem[:-1]
    return None


def _strip(w, suf):
    """어미 suf 를 떼고, 'e' 를 되살린 꼴까지 함께 내놓는다."""
    if not w.endswith(suf) or len(w) - len(suf) < 2:
        return []
    stem = w[:-len(suf)]
    out = [stem, stem + 'e']
    u = _undouble(stem)
    if u:
        out.append(u)
    if stem.endswith('i'):
        out.append(stem[:-1] + 'y')
    return out


def forms(word):
    """찾아볼 표제어 후보를 좋은 순서로. 처음 것이 가장 그럴듯하다."""
    w = word.lower().strip("'-")
    if not w:
        return []
    out, seen = [], set()

    def add(x):
        if x and len(x) >= 2 and x not in seen:
            seen.add(x)
            out.append(x)

    add(w)
    if w in IRREG:
        add(IRREG[w])
    if w in SPELL:
        add(SPELL[w])

    # 영국식 철자 → 웹스터의 미국식
    if 'our' in w:
        add(w.replace('our', 'or'))
    for a, b in (('ae', 'e'), ('oe', 'e'), ('re$', 'er')):
        if a.endswith('$'):
            if w.endswith(a[:-1]):
                add(w[:-len(a) + 1] + b)
        elif a in w:
            add(w.replace(a, b))

    # 옛 동사 어미. publisheth → publish, doest → do
    for suf in ('eth', 'est', 'edst', 'th', 'st'):
        for s in _strip(w, suf):
            add(s)
            if s in IRREG:
                add(IRREG[s])
            if s in SPELL:
                add(SPELL[s])

    # 흔한 어미
    for suf in ('iest', 'ieth', 'ies', 'ied', 'ing', 'ers', 'er', 'est',
                'ed', 'es', 's', 'ly', 'ness', 'less', 'ful', 'ings'):
        for s in _strip(w, suf):
            add(s)

    # 합성어. grapegatherers → grape + gatherer
    if len(w) >= 8:
        for i in range(4, len(w) - 3):
            a, b = w[:i], w[i:]
            if len(b) >= 4:
                out.append(('+', a, b))

    return out


def lookup(word, has):
    """has(표제어) 가 참을 내놓는 첫 후보를 찾는다.

    돌려주는 것: (표제어, 어떻게 찾았나) 또는 (None, None).
    합성어면 표제어가 리스트가 된다.
    """
    cands = forms(word)
    for i, c in enumerate(cands):
        if isinstance(c, tuple):
            continue
        if has(c):
            return c, ('그대로' if i == 0 else '어형')
    for c in cands:
        if isinstance(c, tuple):
            _, a, b = c
            hits = []
            for part in (a, b):
                got, _ = lookup(part, has) if part != word else (None, None)
                if not got:
                    break
                hits.append(got)
            else:
                return hits, '합성어'
    return None, None


if __name__ == '__main__':
    import sys
    for w in sys.argv[1:] or ['publisheth', 'emptiers', 'grapegatherers',
                              'morter', 'wellfavoured', 'pransing',
                              'cankerworm', 'bruit', 'hath', 'saith']:
        print(f'{w:18} {forms(w)[:6]}')
