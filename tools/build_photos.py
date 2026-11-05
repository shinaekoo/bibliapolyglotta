"""A photograph for the best-known places (OpenBible.info Bible Geocoding Data, CC BY 4.0)
-> web/data/gph.json and tools/photolist.txt

OpenBible gives every modern location a 512x512 thumbnail, and names the photographer and the page the
picture comes from. Almost all of them are Wikimedia Commons photographs under their own open licences,
so the credit travels with the picture and is shown under it in the app.

A place can own a picture at three levels, and the first that is a real photograph wins:
  place  the ancient place's own picture, which is how the regions get one (Egypt -> the pyramids of Giza)
  ident  an identification's picture (Bethel -> the ruins at Beitin)
  reso   a modern location's picture, the best-scoring identification first
A satellite view, and anything OpenBible itself marks as a poor likeness, is only taken when there is
nothing else, and is not counted among the pictures this script asks for.

gph.json  {place id: [file, credit, credit_url, caption, "#rgb,#rgb,#rgb" (colours to show while loading)]}
photolist.txt  the file names, for .github/workflows/photos.yml: the 180 MB thumbnails.zip cannot be
reached from here, so the workflow downloads it on the runner, keeps these files and commits them as webp.

usage: python3 tools/build_photos.py OBGEO_DIR [N]
"""
import json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
D = os.path.join(HERE, '..', 'web', 'data') + '/'
OB = os.path.join(sys.argv[1], 'data') + '/'
N = int(sys.argv[2]) if len(sys.argv) > 2 else 200

A = [json.loads(l) for l in open(OB + 'ancient.jsonl', encoding='utf-8')]
M = {}
for l in open(OB + 'modern.jsonl', encoding='utf-8'):
    d = json.loads(l); M[d['id']] = d
SLUG = {}
for p in A:                      # by url_slug, by the slug without its number, and by name
    for s in (p.get('url_slug', ''), re.sub(r'-\d+$', '', p.get('url_slug', '')), p['friendly_id'].lower()):
        if s: SLUG.setdefault(s, p)

def real(t): return bool(t) and t.get('role') != 'satellite' and t.get('quality') != 'low'

def thumbs(p):
    """every picture this place can show, in the order we would rather have them"""
    out = []
    if p.get('media', {}).get('thumbnail'): out.append(p['media']['thumbnail'])
    for idn in p.get('identifications', []):
        if idn.get('media', {}).get('thumbnail'): out.append(idn['media']['thumbnail'])
    res = []
    for idn in p.get('identifications', []):
        for r in idn.get('resolutions', []):
            m = re.search(r'id="(m[0-9a-f]+)"', r.get('description', ''))
            mid = r.get('id') or (m.group(1) if m else None)
            if mid: res.append((int(r.get('best_path_score') or 0), mid))
    for _, mid in sorted(res, reverse=True):
        t = (M.get(mid) or {}).get('media', {}).get('thumbnail')
        if t: out.append(t)
    return out

# ---- what the picture shows, so the app can say it in the reader's language ----
# OpenBible writes its captions to a pattern ("ruins at Beitin", "panorama of hills in Gilead"), so each one
# becomes a code and a subject: the app prints "Beitin 유적", "Gilead 산지". The whole English caption is
# kept as well, for the picture's alt text and for anything this does not catch.
KIND = [('artifact', 'artifact'), ('aerial cityscape', 'aerialcity'), ('aerial panorama', 'aerialview'),
        ('ruins', 'ruins'), ('pyramids', 'ruins'), ('acropolis', 'ruins'), ('citadel', 'building'),
        ('library', 'building'), ('church', 'building'), ('mosque', 'building'), ('dome', 'building'),
        ('houses', 'building'), ('bridge', 'building'), ('building', 'building'), ('gate', 'gate'),
        ('cityscape', 'city'), ('streetscape', 'city'), ('closeup', 'closeup'), ('cave', 'cave'),
        ('waterfall', 'water'), ('pool', 'water'), ('well', 'water'), ('water', 'water'), ('river', 'water'),
        ('sea of', 'water'), ('shoreline', 'water'), ('coast', 'water'), ('gulf', 'water'), ('beach', 'water'),
        ('cliff', 'cliff'), ('summit', 'summit'), ('mount of', 'summit'), ('desert', 'desert'),
        ('valley', 'valley'), ('wadi', 'valley'), ('hills', 'hills'), ('mountains', 'hills'),
        ('plain', 'plain'), ('panorama', 'view')]
KIND = [('coastal plain', 'plain')] + KIND      # "coastal" must not read as a coast
NAME_RE = re.compile(r"\b[A-Z][\w’'-]*(?:\s+(?:el|es|ed|edh|esh|et|ez|en|al|the|of|[A-Z][\w’'-]*))*")

def shape(cap, en):
    low = cap.lower()
    kc = next((c for w, c in KIND if w in low), '')
    # the first name in the caption that is not the place itself: "pyramids of Giza in Egypt" -> Giza
    sj = next((m.group(0).strip() for m in NAME_RE.finditer(cap)
               if en.lower() not in m.group(0).lower() and len(m.group(0)) < 30), '')
    return kc, sj

gp = json.load(open(D + 'gp.json', encoding='utf-8'))
gi = json.load(open(D + 'gi.json', encoding='utf-8'))
rows = []
for k, e in gp.items():
    p = SLUG.get(e.get('ob', '')) or SLUG.get(gi['n'][k][0].lower())
    if not p: continue
    ts = thumbs(p)
    t = next((x for x in ts if real(x)), None)
    if t and t.get('file'): rows.append((e['cc'][0], k, t))
rows.sort(key=lambda r: (-r[0], r[1]))

out, files = {}, []
for c, k, t in rows[:N]:
    # "panorama of a wadi in Moab 1" -> "... in Moab": the number only tells OpenBible's Moabs apart
    cap = re.sub(r'\s+\d+$', '', re.sub(r'<[^>]+>', '', t.get('description', '')).strip())
    kc, sj = shape(cap, gi['n'][k][0])
    out[k] = [t['file'].rsplit('.', 1)[0] + '.webp', t.get('credit', ''), t.get('credit_url', ''),
              cap, t.get('placeholder', ''), kc, sj]
    files.append(t['file'])
json.dump(out, open(D + 'gph.json', 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
open(os.path.join(HERE, 'photolist.txt'), 'w').write('\n'.join(files) + '\n')
print('photos', len(out), 'of', len(rows), 'places with one; fewest verses', rows[min(N, len(rows)) - 1][0],
      'KB', os.path.getsize(D + 'gph.json') // 1024, file=sys.stderr)
