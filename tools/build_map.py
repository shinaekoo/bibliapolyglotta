"""A small offline base map for the place sheet -> web/data/map.json

Natural Earth (public domain) land, lakes and rivers, clipped to the Bible lands
(lon -10..70, lat 10..48) and simplified: finer around Israel, coarser further away.
Coordinates are projected (x = lon * cos 31.5°, y = -lat) and stored as SVG path data in
thousandths of a degree, relative moves, so the file stays small.

{"land": path, "lake": path, "river": [[name, path]], "sea": [[key, x, y]], "k": scale}
usage: python3 tools/build_map.py NATURAL_EARTH_GEOJSON_DIR
"""
import json, math, os, sys

NE = sys.argv[1]
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, '..', 'web', 'data', 'map.json')
X0, X1, Y0, Y1 = -10, 70, 10, 48
KX = math.cos(math.radians(31.5))
CORE = (33.0, 37.5, 28.5, 34.5)      # Israel and surroundings: keep detail

def tol(lon, lat):
    return 0.004 if CORE[0] <= lon <= CORE[1] and CORE[2] <= lat <= CORE[3] else 0.03

def clip_ring(ring):
    """Sutherland-Hodgman against the bounding box"""
    def clip(pts, inside, inter):
        out = []
        for i in range(len(pts)):
            a, b = pts[i - 1], pts[i]
            if inside(b):
                if not inside(a): out.append(inter(a, b))
                out.append(b)
            elif inside(a): out.append(inter(a, b))
        return out
    def ix(x):
        return lambda a, b: (x, a[1] + (b[1] - a[1]) * (x - a[0]) / (b[0] - a[0]))
    def iy(y):
        return lambda a, b: (a[0] + (b[0] - a[0]) * (y - a[1]) / (b[1] - a[1]), y)
    pts = ring
    for inside, inter in ((lambda p: p[0] >= X0, ix(X0)), (lambda p: p[0] <= X1, ix(X1)),
                          (lambda p: p[1] >= Y0, iy(Y0)), (lambda p: p[1] <= Y1, iy(Y1))):
        if not pts: break
        pts = clip(pts, inside, inter)
    return pts

def simplify(pts):
    """Douglas-Peucker with a tolerance that depends on where the points are"""
    if len(pts) < 3: return pts
    if pts[0] == pts[-1] and len(pts) > 4:   # closed ring: simplify the two halves
        m = len(pts) // 2
        return simplify(pts[:m + 1])[:-1] + simplify(pts[m:])
    keep = [False] * len(pts); keep[0] = keep[-1] = True
    stack = [(0, len(pts) - 1)]
    while stack:
        a, b = stack.pop()
        (x1, y1), (x2, y2) = pts[a], pts[b]
        dx, dy = x2 - x1, y2 - y1; L = math.hypot(dx, dy) or 1e-12
        best, bi = 0, -1
        for i in range(a + 1, b):
            x, y = pts[i]
            d = abs(dy * (x - x1) - dx * (y - y1)) / L
            if d > best: best, bi = d, i
        if bi > 0 and best > tol(*pts[bi]):
            keep[bi] = True; stack += [(a, bi), (bi, b)]
    return [p for p, k in zip(pts, keep) if k]

def path(rings, close=True):
    out = []
    for ring in rings:
        q = [(round(x * KX * 1000), round(-y * 1000)) for x, y in ring]
        dd = []
        for i, (x, y) in enumerate(q):
            if i and (x, y) == q[i - 1]: continue
            dd.append((x, y))
        if len(dd) < (3 if close else 2): continue
        s = f'M{dd[0][0]} {dd[0][1]}l' + ' '.join(f'{dd[i][0]-dd[i-1][0]} {dd[i][1]-dd[i-1][1]}' for i in range(1, len(dd)))
        out.append(s + ('z' if close else ''))
    return ''.join(out)

def polys(f):
    g = f['geometry']
    if not g: return []
    return g['coordinates'] if g['type'] == 'MultiPolygon' else [g['coordinates']] if g['type'] == 'Polygon' else []
def lines(f):
    g = f['geometry']
    if not g: return []
    return g['coordinates'] if g['type'] == 'MultiLineString' else [g['coordinates']] if g['type'] == 'LineString' else []
def in_box(pts): return any(X0 <= x <= X1 and Y0 <= y <= Y1 for x, y in pts)

def area_rings(name, min_area=0.0):
    rings = []
    for f in json.load(open(os.path.join(NE, name)))['features']:
        for poly in polys(f):
            for ring in poly[:1] + [r for r in poly[1:]]:
                if not in_box(ring): continue
                c = clip_ring([tuple(p) for p in ring])
                if len(c) < 3: continue
                xs = [p[0] for p in c]; ys = [p[1] for p in c]
                if (max(xs) - min(xs)) * (max(ys) - min(ys)) < min_area: continue
                rings.append(simplify(c + [c[0]])[:-1])
    return rings

land = area_rings('ne_10m_land.geojson', 0.0005)
lakes = area_rings('ne_10m_lakes.geojson', 0.002)
rivers = []
KEEP = {'Nile', 'Jordan', 'Euphrates', 'Tigris', 'Orontes', 'Litani', 'Yarmuk', 'Karun', 'Halys', 'Kızılırmak', 'Tiber', 'Blue Nile', 'White Nile', 'Habur', 'Khabur', 'Zarqa'}
for f in json.load(open(os.path.join(NE, 'ne_10m_rivers_lake_centerlines.geojson')))['features']:
    p = f['properties']; nm = p.get('name') or p.get('name_en') or ''
    if not (nm in KEEP or (p.get('scalerank', 9) <= 4)): continue
    for ln in lines(f):
        if not in_box(ln): continue
        pts = [tuple(q) for q in ln if X0 - 1 <= q[0] <= X1 + 1 and Y0 - 1 <= q[1] <= Y1 + 1]
        if len(pts) >= 2: rivers.append([nm, path([simplify(pts)], close=False)])
P = lambda lon, lat: [round(lon * KX * 1000), round(-lat * 1000)]
sea = [['med', *P(18.5, 34.6)], ['red', *P(38.2, 20.5)], ['gulf', *P(50.6, 27.2)], ['black', *P(34.5, 43.3)],
       ['caspian', *P(51.0, 41.8)], ['dead', *P(35.5, 31.5)], ['galilee', *P(35.6, 32.83)], ['nile', *P(31.3, 26.2)],
       ['euph', *P(41.0, 34.7)], ['tigris', *P(44.6, 35.2)], ['jordan', *P(35.62, 32.25)]]
out = {'k': 1000, 'kx': KX, 'box': [X0, X1, Y0, Y1], 'land': path(land), 'lake': path(lakes), 'river': rivers, 'sea': sea}
json.dump(out, open(OUT, 'w'), separators=(',', ':'))
print('land rings', len(land), 'lakes', len(lakes), 'rivers', len(rivers), 'KB', os.path.getsize(OUT) // 1024, file=sys.stderr)
