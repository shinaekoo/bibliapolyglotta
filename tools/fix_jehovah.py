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
for b in sorted({k[0] for k in FIX}):
    f = f'{D}al{b:02d}.json'; al = json.load(open(f))
    for (bb, c, v), langs in FIX.items():
        if bb != b: continue
        rec = al['v'][c-1][v-1]
        for l, (rm, add) in langs.items():
            p = rec.get(l, []); s = {(p[i], p[i+1]) for i in range(0, len(p), 2)}
            s = (s - set(rm)) | set(add)
            rec[l] = [n for x in sorted(s) for n in x]
    json.dump(al, open(f, 'w'), separators=(',', ':'))
print('fixed', len(FIX))
