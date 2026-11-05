"""Sound keys shared by the name matching in build_persons.py, build_geo.py and build_others.py:
a Korean word and a Latin-script name reduced to comparable consonants, so that 바알 and Baal match."""
import re, difflib

CHO = ['g','kk','n','d','tt','r','m','b','pp','s','ss','','j','jj','ch','k','t','p','h']
JUNG = ['a','ae','ya','yae','eo','e','yeo','ye','o','wa','wae','oe','yo','u','wo','we','wi','yu','eu','ui','i']
JONG = ['','k','k','k','n','n','n','t','l','k','m','l','l','l','p','l','m','p','p','t','t','ng','t','t','k','t','p','t']
def roman(s):
    out = []
    for ch in s:
        o = ord(ch) - 0xAC00
        if 0 <= o < 11172: out.append(CHO[o // 588] + JUNG[(o % 588) // 28] + JONG[o % 28])
    return ''.join(out)
def key_ko(s):
    r = roman(s)
    for a, b in (('eo', 'o'), ('eu', ''), ('ae', 'e'), ('oe', 'e'), ('ya', 'ia'), ('yo', 'io'), ('yu', 'iu'), ('ye', 'ie'), ('ng', 'n'), ('ch', 's'), ('j', 's'), ('kk', 'k'), ('tt', 't'), ('pp', 'p'), ('ss', 's')):
        r = r.replace(a, b)
    return r.translate(str.maketrans('gdbr', 'ktpl')).replace('h', '')
def key_lat(s):
    r = s.lower().replace('-', '').replace(' ', '')
    for a, b in (('th', 't'), ('ph', 'p'), ('ch', 'k'), ('sh', 's'), ('ck', 'k'), ('qu', 'k'), ('x', 'ks'), ('j', 'i'), ('y', 'i'), ('ee', 'e'), ('oo', 'u')):
        r = r.replace(a, b)
    r = r.translate(str.maketrans('cqzvfwgdbr', 'kksbpuktpl'))
    return re.sub(r'(.)\1', r'\1', r).replace('h', '')
def sim(a, b):
    import difflib
    return difflib.SequenceMatcher(None, a, b).ratio() if a and b else 0
