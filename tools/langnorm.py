"""Word keys for Spanish, Italian, Russian and Japanese, shared by align_original.py and build_orig_lex.py:
crude suffix stripping, so that forms of one word count together; for Japanese, the content part of a phrase."""
def suf(ends):
    ends = sorted(ends, key=len, reverse=True)
    def f(w):
        w = w.lower()
        for e in ends:
            if w.endswith(e) and len(w) - len(e) >= 3: return w[:-len(e)]
        return w
    return f
es_n = suf(['aban', 'aron', 'ieron', 'iendo', 'ando', 'ados', 'adas', 'idos', 'idas', 'ado', 'ada', 'ido', 'ida',
             'aba', 'ará', 'erá', 'irá', 'arán', 'erán', 'irán', 'amos', 'emos', 'imos', 'éis', 'áis', 'an', 'en', 'as', 'es', 'os', 'ó', 'ió', 'a', 'o', 'e', 's'])
it_n = suf(['arono', 'erono', 'irono', 'avano', 'evano', 'ando', 'endo', 'ato', 'ata', 'ati', 'ate', 'uto', 'uta', 'uti', 'ito', 'ita', 'iti',
             'ava', 'eva', 'erà', 'irà', 'erò', 'ono', 'ano', 'ete', 'ate', 'ò', 'à', 'i', 'e', 'o', 'a'])
ru_n = suf(['ами', 'ями', 'ого', 'его', 'ому', 'ему', 'ыми', 'ими', 'ой', 'ей', 'ий', 'ый', 'ая', 'яя', 'ое', 'ее', 'ые', 'ие', 'ых', 'их',
             'ам', 'ям', 'ах', 'ях', 'ом', 'ем', 'ов', 'ев', 'ал', 'ил', 'ел', 'ла', 'ли', 'ло', 'ть', 'ет', 'ит', 'ут', 'ют', 'ят', 'ат',
             'ся', 'сь', 'а', 'я', 'ы', 'и', 'у', 'ю', 'е', 'о', 'ь'])
import lexres
def ja_n(w):
    """a Japanese phrase -> its dictionary form by UniDic when available ("愛して下さった" -> 愛する), else its content part"""
    l = lexres.ja_lemma(w)
    if l: return l
    return _ja_n(w)
def _ja_n(w):
    """a Japanese phrase -> its content part: up to the last kanji or katakana ("神は" -> "神", "創造された" -> "創造")"""
    k = [i for i, ch in enumerate(w) if '\u4e00' <= ch <= '\u9fff' or '\u30a1' <= ch <= '\u30fa' or ch in '々ー']
    if k: return w[:k[-1] + 1]
    for e in ('によって', 'について', 'から', 'まで', 'より', 'には', 'では', 'とは', 'が', 'を', 'に', 'は', 'の', 'へ', 'と', 'も', 'で'):
        if w.endswith(e) and len(w) > len(e) + 1: return w[:-len(e)]
    return w
pt_n = suf(['aram', 'eram', 'iram', 'ando', 'endo', 'indo', 'ados', 'adas', 'idos', 'idas', 'ado', 'ada', 'ido', 'ida',
            'ava', 'ões', 'ão', 'ais', 'eis', 'ou', 'eu', 'iu', 'ia', 'am', 'em', 'as', 'es', 'os', 'a', 'e', 'o', 's'])
id_n = suf(['nya', 'lah', 'kah', 'kan', 'an', 'i'])
tl_n = suf([])                       # Tagalog and Cebuano change words mostly at the front: case only
ceb_n = suf([])
def ig_n(w):
    """Igbo: case, and the "nʼ" (in, at) written onto the next word"""
    w = w.lower()
    return w[2:] if w.startswith('nʼ') and len(w) > 3 else w
