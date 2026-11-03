"""Jehovah 합성 이름(여호와이레·여호와닛시·여호와살롬)을 번역마다 직접 잇는다.
align_strongs.py로 정렬을 다시 만든 뒤에 이어서 실행한다.  usage: python3 tools/fix_jehovah.py"""
import json, os
D = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'web', 'data') + '/'
# (책, 장, 절): {언어: (지울 연결, 더할 연결)}  연결 = (그 번역 낱말 위치, KJV 낱말 위치)
FIX = {
 (0, 22, 14): {'ko': ([], [(4, 8), (4, 9)]), 'zh': ([], [(5, 8), (5, 9)]), 'la': ([], [(4, 8), (5, 9)]),
               'de': ([], [(5, 8), (6, 8), (7, 9)]), 'fr': ([], [(8, 8), (9, 9)])},
 (1, 17, 15): {'ko': ([(3, 5)], [(5, 11), (6, 12)]), 'zh': ([], [(5, 11), (5, 12)]),
               'la': ([(7, 7), (8, 11)], [(7, 11), (8, 12), (9, 12)]),
               'de': ([], [(8, 11), (9, 11), (10, 12), (11, 12), (12, 12)]), 'fr': ([], [(9, 11), (10, 11), (11, 12), (12, 12)])},
 (6, 6, 24): {'ko': ([(7, 8)], [(7, 12), (8, 13)]), 'zh': ([], [(7, 12), (7, 13)]),
              'la': ([(8, 8)], [(8, 12), (9, 13)]),
              'de': ([(11, 7), (12, 8)], [(11, 12), (12, 12), (13, 13), (14, 13), (15, 13)]),
              'fr': ([(13, 8), (13, 11), (14, 8)], [(13, 12), (14, 12), (15, 13)])},
}
# 스페인어·이탈리아어·러시아어·일본어: 이 KJV 낱말들에 걸린 연결을 지우고 아래 연결만 남긴다
NEW = {
 (0, 22, 14): {'es': [(8, 8), (9, 9)], 'it': [(7, 8), (8, 9)], 'ru': [(6, 8), (7, 9)], 'ja': [(4, 8), (5, 9)]},
 (1, 17, 15): {'es': [(9, 11), (10, 12)], 'it': [(9, 11), (10, 11), (13, 12), (14, 12)], 'ru': [(8, 11), (9, 12)], 'ja': [(6, 11), (7, 12), (8, 12)]},
 (6, 6, 24): {'es': [(10, 12), (11, 13)], 'it': [(11, 12), (12, 12), (13, 13)], 'ru': [(9, 12), (10, 13)], 'ja': [(7, 12), (8, 13)]},
}
for k, langs in NEW.items():
    for l, add in langs.items():
        FIX.setdefault(k, {})[l] = (('en', {j for _, j in add}), add)
for b in sorted({k[0] for k in FIX}):
    f = f'{D}al{b:02d}.json'; al = json.load(open(f))
    for (bb, c, v), langs in FIX.items():
        if bb != b: continue
        rec = al['v'][c-1][v-1]
        for l, (rm, add) in langs.items():
            p = rec.get(l, []); s = {(p[i], p[i+1]) for i in range(0, len(p), 2)}
            if isinstance(rm, tuple): rm = {x for x in s if x[1] in rm[1] or x[0] in {i for i, _ in add}}
            s = (s - set(rm)) | set(add)
            rec[l] = [n for x in sorted(s) for n in x]
    json.dump(al, open(f, 'w'), separators=(',', ':'))
print('fixed', len(FIX))
