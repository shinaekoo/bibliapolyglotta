"""web/ -> site/: 설문 시험용 축소판 웹페이지를 만든다.

담는 본문은 ONLY에 적은 책과 장뿐이다 (창세기 1-3, 여호수아 1-5, 히브리서 전체, 요한계시록 1-5).
자료 파일은 그 범위로 잘라 내고, 인물·지명·성경사전·용례는 그 범위에 나오는 것만 남긴다.
라틴어 낱말 음원(audio/la/)은 .github/workflows/lexdata.yml 의 latin 단계가 만든 것을 끼워 넣는다.

usage: python3 tools/trim_site.py [출력폴더]
"""
import json, os, re, shutil, sys

HERE = os.path.dirname(os.path.abspath(__file__))
R = os.path.join(HERE, '..')
W = os.path.join(R, 'web')
TX = os.path.join(R, 'text')
OUT = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else os.path.join(R, 'site')

ONLY = {0: 3, 5: 5, 57: 13, 65: 5}          # 책 번호(0부터) → 담을 장 수
GRP = [0, 2, 5, 10, 14, 18, 19, 22, 25, 39, 43]
LAIDX = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,18,19,20,21,22,23,26,27,28,30,31,32,33,34,
         35,36,37,38,39,40,41,42,43,46,47,48,49,50,51,52,53,54,55,56,57,58,59,60,61,62,63,
         64,65,66,67,68,69,70,71,72]
LANGS = ['en','la','de','fr','ko','zh','es','it','ru','ja','pt','tl','ceb','id','ig']
group = lambda b: max(g for g, first in enumerate(GRP) if b >= first)
keep = lambda b, c: b in ONLY and 1 <= c <= ONLY[b]

D = os.path.join(W, 'data') + '/'
O = os.path.join(OUT, 'data') + '/'
os.makedirs(O, exist_ok=True)
rd = lambda n: json.load(open(D + n, encoding='utf-8'))
def wr(n, d):
    json.dump(d, open(O + n, 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
    return os.path.getsize(O + n)

size = {}

# ---- 1. 정렬 자료 al{책}.json — 장 수만큼 자른다 ----
used_lx = set()
for b, nc in ONLY.items():
    d = rd(f'al{b:02d}.json')
    out = {'v': d['v'][:nc], 'or': d['or'][:nc], 'ow': d['ow'][:nc], 'og': d['og'],
           'lx': {k: v for k, v in d['lx'].items() if 1 <= int(k) <= nc}}
    for ch in out['lx'].values():
        for row in ch.values():
            for w in row:
                used_lx.add(w[0])
    size[f'al{b:02d}'] = wr(f'al{b:02d}.json', out)

# ---- 2. 번역 본문 묶음 — 담는 책만, 장 수만큼 ----
for lang in LANGS:
    packs = {}
    for b, nc in ONLY.items():
        n = LAIDX[b] if lang == 'la' else b
        packs.setdefault(group(b), {})[str(n)] = \
            json.load(open(f'{TX}/{lang}{n:02d}.json', encoding='utf-8'))[:nc]
    for g, p in packs.items():
        size[f'{lang}_{g}'] = wr(f'{lang}_{g}.json', p)

# ---- 3. 라틴어 낱말 사전 — 쓰이는 자리만 남기고 자리 번호는 그대로 ----
lxL = rd('lxL.json')
size['lxL'] = wr('lxL.json', [e if i in used_lx else 0 for i, e in enumerate(lxL)])

# ---- 4. 찾기표 — 36진수 두 자씩 묶은 기록을 담는 범위만 골라 다시 쓴다 ----
def pick(packed, wide):
    """wide=True면 한 기록이 8자(책·장·절·낱말), False면 6자(책·장·절)"""
    n = 8 if wide else 6
    out = []
    for j in range(0, len(packed) - n + 1, n):
        r = packed[j:j + n]
        if keep(int(r[0:2], 36), int(r[2:4], 36)):
            out.append(r)
    return ''.join(out)

def cut_cc(e):
    """[횟수, 기록] → 담는 범위의 것만. 하나도 없으면 None"""
    if not (isinstance(e, list) and len(e) == 2 and isinstance(e[1], str)):
        return None
    p = pick(e[1], True)
    return [len(p) // 8, p] if p else None

for n in ['cc0.json', 'cc1.json', 'ox0.json', 'ox1.json', 'ox2.json', 'ox3.json']:
    d = rd(n)
    out = {}
    for k, v in d.items():
        if isinstance(v, dict):                 # ox: {'cc': [...], …}
            c = cut_cc(v.get('cc'))
            if c: out[k] = dict(v, cc=c)
        else:
            c = cut_cc(v)
            if c: out[k] = c
    size[n[:-5]] = wr(n, out)
    print(f'  {n}: {len(d)} → {len(out)}', file=sys.stderr)

# ---- 5. 인물·지명·성경사전 — 담는 범위에 나오는 것만 ----
def cut_refs(v):
    """사전 항목 하나. 담는 범위의 자리만 남기고, 하나도 안 남으면 None"""
    v = json.loads(json.dumps(v))
    hit = False
    if isinstance(v.get('cc'), list):
        c = cut_cc(v['cc'])
        if c: v['cc'] = c; hit = True
        else: v.pop('cc', None)
    for nm in v.get('nm', []):                  # [이름, 원어, 스트롱, [책,장,절], 횟수]
        if len(nm) > 3 and isinstance(nm[3], list) and len(nm[3]) >= 2:
            if keep(nm[3][0], nm[3][1]): hit = True
    for art in v.get('d', []):                  # 성경사전: [출처, 본문, [[시작,끝,책,장,절], …]]
        if len(art) > 2 and isinstance(art[2], list):
            art[2] = [r for r in art[2] if len(r) >= 4 and keep(r[2], r[3])]
            if art[2]: hit = True
    return v if hit else None

for n in ['pp.json', 'gp.json', 'dp.json', 'dg.json', 'do.json', 'oo.json']:
    d = rd(n)
    out = {k: c for k, v in d.items() if (c := cut_refs(v)) is not None}
    size[n[:-5]] = wr(n, out)
    print(f'  {n}: {len(d)} → {len(out)}', file=sys.stderr)

# ---- 6. 그대로 담는 것 ----
for n in ['pi.json', 'gi.json', 'oi.json', 'map.json']:
    shutil.copy(D + n, O + n)
    size[n[:-5]] = os.path.getsize(O + n)
# xref.json(구약 인용)은 담지 않는다 — 인용된 구약 본문이 이 축소판에 없다.

# ---- 7. index.html 손보기 ----
h = open(os.path.join(W, 'index.html'), encoding='utf-8').read()
n0 = len(h)

def sub(old, new, note):
    global h
    if h.count(old) != 1:
        raise SystemExit(f'{note}: {h.count(old)}군데 — 고쳐야 한다\n  {old[:90]}')
    h = h.replace(old, new)

sub('function chapCount(bi){return B[bi][5];}',
    '// ---- 시험판: ONLY에 적은 책·장만 담겨 있다 ----\n'
    f'const ONLY={json.dumps({str(k): v for k, v in ONLY.items()})};\n'
    'const BKS=Object.keys(ONLY).map(Number).sort((a,b)=>a-b);\n'
    'function chapCount(bi){return ONLY[bi]!==undefined?Math.min(B[bi][5],ONLY[bi]):B[bi][5];}',
    '장 수')

sub('B.slice(0,NT).forEach((b,i)=>g[i<39?0:1].appendChild(new Option(bookName(i),i)));',
    'B.slice(0,NT).forEach((b,i)=>{if(BKS.includes(i))g[i<39?0:1].appendChild(new Option(bookName(i),i))});',
    '책 목록')

sub('function step(d){let b=S.b,c=S.c+d;if(c<1){b=(b-1+NT)%NT;c=chapCount(b);}'
    'else if(c>chapCount(b)){b=(b+1)%NT;c=1;}go(b,c);}',
    'function step(d){let b=S.b,c=S.c+d;const k=Math.max(0,BKS.indexOf(b));'
    'if(c<1){b=BKS[(k-1+BKS.length)%BKS.length];c=chapCount(b);}'
    'else if(c>chapCount(b)){b=BKS[(k+1)%BKS.length];c=1;}go(b,c);}',
    '장 넘기기')

sub('for(let bi=0;bi<NT;bi++)for(let c=1;c<=chapCount(bi);c++)',
    'for(const bi of BKS)for(let c=1;c<=chapCount(bi);c++)',
    '검색 범위')

sub('if(!(S.b>=0&&S.b<NT))S.b=0;',
    'if(!BKS.includes(S.b))S.b=BKS[0];',
    '첫 화면')

# 구약 인용은 담지 않으므로 찾지 않는다
sub('function loadXR(){if(XRQ)return Promise.resolve(XRQ);',
    'function loadXR(){XRQ=XRQ||[];XRF=XRF||{};XRR=XRR||{};return Promise.resolve(XRQ);\n'
    '  if(XRQ)return Promise.resolve(XRQ);',
    '구약 인용 끄기')

# 음원: 한 절 견본 대신, 담긴 라틴어 낱말 전체를 낱낱의 파일로 받아 재생한다
old_au = h[h.index('let AU=null,AUP=null,AUEL=null;'):h.index('const AUT={play:"소리 듣기"};')]
h = h.replace(old_au, '''let AU=null,AUP=null,AUEL=null;
function loadAU(){if(AU)return Promise.resolve(AU);
  if(!AUP)AUP=fetch("audio/la/manifest.json").then(r=>{if(!r.ok)throw new Error(r.status);return r.json();})
    .then(d=>{AU=d.words||{};return AU;}).catch(e=>{AUP=null;throw e;});
  return AUP;}
const auKey=w=>String(w||"").toLowerCase();
const auHas=w=>!!(AU&&AU[auKey(w)]);
const AUICON='<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M4 9.5h3.2L12 5.2v13.6L7.2 14.5H4z"/><path d="M15.2 8.6a4.6 4.6 0 0 1 0 6.8" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/><path d="M17.8 6a8 8 0 0 1 0 12" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/></svg>';
function auPlay(word,btn){
  const f=AU&&AU[auKey(word)];if(!f)return;
  try{
    if(AUEL){try{AUEL.pause();}catch(e){}AUEL=null;}
    const a=new Audio("audio/la/"+f);AUEL=a;
    if(btn)btn.classList.add("on");
    const done=()=>{if(btn)btn.classList.remove("on");};
    a.onended=done;a.onerror=done;
    a.play().catch(done);
  }catch(e){}
}
// 풀이 창은 바로 그려지므로 자리만 잡아 두고, 목록이 오면 채운다
function auFill(lang,word,v){
  if(lang!=="la")return;
  loadAU().then(()=>{
    const slot=document.getElementById("auslot");
    if(!slot||!auHas(word))return;
    slot.innerHTML=`<button class="au-btn" type="button" aria-label="${esc(AUT.play)}" title="${esc(AUT.play)}">${AUICON}</button>`;
    slot.firstChild.onclick=e=>{e.stopPropagation();auPlay(word,e.currentTarget);};
  }).catch(()=>{});
}
''')

sub('<title>', '<title>[시험판] ', '제목')
open(os.path.join(OUT, 'index.html'), 'w', encoding='utf-8').write(h)
print(f'  index.html: {n0:,} → {len(h):,} 바이트', file=sys.stderr)

for n in os.listdir(W):
    if n in ('data', 'index.html'):
        continue
    s = os.path.join(W, n)
    if os.path.isdir(s):
        shutil.copytree(s, os.path.join(OUT, n), dirs_exist_ok=True)
    else:
        shutil.copy(s, os.path.join(OUT, n))

tot = sum(os.path.getsize(os.path.join(dp, f)) for dp, _, fs in os.walk(OUT) for f in fs)
print(f'\n{OUT}: {tot/1e6:.1f}MB', file=sys.stderr)
for k, v in sorted(size.items(), key=lambda x: -x[1])[:14]:
    print(f'  {v/1e6:>6.2f}MB  {k}', file=sys.stderr)
