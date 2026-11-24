# -*- coding: utf-8 -*-
"""한 장(章)을 클릭으로 매칭하는 편집기 HTML 을 만든다.

영어 낱말을 고르고 한국어 낱말들을 눌러 짝을 맞추면, 아래쪽에 tools/fix_links.py 에
그대로 붙일 수 있는 항목이 쌓인다. #번호는 자동으로 붙는다. 영어도 한국어도 여러 개를
한꺼번에 고를 수 있다 ('여러 개 고르기' 단추, 또는 Shift·Ctrl·⌘ 누른 채 클릭).

usage: python3 tools/make_editor.py <책번호> <장> [내보낼파일]
       python3 tools/make_editor.py 57 11 /tmp/edit-heb11.html

       절을 골라서 만들 수도 있다 — 한 줄에 '책번호 장 절' 로 적은 목록을 주면
       그 절들만 모아 한 파일로 낸다 (여러 책에 흩어진 절을 한 번에 볼 때).
       python3 tools/make_editor.py --verses 목록.txt 제목 /tmp/edit.html
"""
import json, io, os, sys, unicodedata

HERE = os.path.dirname(os.path.abspath(__file__))
D = os.path.join(HERE, '..', 'web', 'data') + '/'
TX = os.path.join(HERE, '..', 'text') + '/'
BK = ['창세기','출애굽기','레위기','민수기','신명기','여호수아','사사기','룻기','사무엘상','사무엘하',
      '열왕기상','열왕기하','역대상','역대하','에스라','느헤미야','에스더','욥기','시편','잠언','전도서',
      '아가','이사야','예레미야','예레미야애가','에스겔','다니엘','호세아','요엘','아모스','오바댜','요나',
      '미가','나훔','하박국','스바냐','학개','스가랴','말라기','마태복음','마가복음','누가복음','요한복음',
      '사도행전','로마서','고린도전서','고린도후서','갈라디아서','에베소서','빌립보서','골로새서',
      '데살로니가전서','데살로니가후서','디모데전서','디모데후서','디도서','빌레몬서','히브리서','야고보서',
      '베드로전서','베드로후서','요한일서','요한이서','요한삼서','유다서','요한계시록']


def toks(s):
    out, cur = [], []
    s = s or ''
    for i, ch in enumerate(s):
        if unicodedata.category(ch)[0] in ('L', 'M'):
            cur.append(ch)
        elif (ch == '–' and cur and i + 1 < len(s)
              and unicodedata.category(s[i + 1])[0] in ('L', 'M')):
            cur.append(ch)
        elif cur:
            out.append(''.join(cur)); cur = []
    if cur: out.append(''.join(cur))
    return out


HTML = r"""<!DOCTYPE html>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>__TITLE__ 낱말 연결</title>
<style>
:root{--bg:#fbfaf8;--fg:#1d1b18;--mut:#8a8580;--line:#e5e1db;--sel:#1f6feb;--hit:#f0b429;--card:#fff}
@media(prefers-color-scheme:dark){:root{--bg:#17161a;--fg:#eceae6;--mut:#8f8a85;--line:#2e2b30;--card:#1f1e23}}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--fg);font:15px/1.55 -apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}
header{position:sticky;top:0;background:var(--bg);border-bottom:1px solid var(--line);padding:10px 14px;z-index:5}
h1{margin:0;font-size:16px;font-weight:650}
.sub{color:var(--mut);font-size:12.5px;margin-top:2px}
nav{display:flex;flex-wrap:wrap;gap:5px;padding:9px 14px;border-bottom:1px solid var(--line)}
nav button{font:inherit;font-size:12.5px;padding:3px 9px;border:1px solid var(--line);border-radius:999px;
  background:var(--card);color:var(--fg);cursor:pointer}
nav button.on{background:var(--sel);border-color:var(--sel);color:#fff}
nav button.done{border-color:#2f9e44;color:#2f9e44}
main{padding:14px;max-width:960px;margin:0 auto}
.lab{font-size:11.5px;letter-spacing:.06em;text-transform:uppercase;color:var(--mut);margin:16px 0 6px}
.row{display:flex;flex-wrap:wrap;gap:6px}
.w{font:inherit;padding:4px 10px;border:1px solid var(--line);border-radius:7px;background:var(--card);
  color:var(--fg);cursor:pointer;position:relative}
.w .n{font-size:9.5px;color:var(--mut);vertical-align:super;margin-left:1px}
.w.cur{background:var(--sel);border-color:var(--sel);color:#fff}
.w.cur.lead{box-shadow:0 0 0 2px var(--bg),0 0 0 4px var(--sel)}
.w.cur .n{color:#cfe2ff}
.w.tgt{background:var(--hit);border-color:var(--hit);color:#241c00}
.w.tgt .n{color:#6b5500}
.w.has{border-color:var(--mut)}
.w.none{opacity:.45;border-style:dashed}
.hint{color:var(--mut);font-size:12.5px;margin-top:10px}
.bar{display:flex;gap:7px;flex-wrap:wrap;margin:14px 0 0}
.bar button{font:inherit;font-size:13px;padding:5px 12px;border:1px solid var(--line);border-radius:7px;
  background:var(--card);color:var(--fg);cursor:pointer}
.bar button.p{background:var(--sel);border-color:var(--sel);color:#fff}
textarea{width:100%;height:210px;margin-top:9px;padding:10px;border:1px solid var(--line);border-radius:8px;
  background:var(--card);color:var(--fg);font:12.5px/1.5 ui-monospace,SFMono-Regular,Menlo,monospace}
.cnt{color:var(--mut);font-size:12.5px;margin-top:6px}
.txt{background:var(--card);border:1px solid var(--line);border-radius:10px;
  padding:11px 13px;margin:0 0 12px}
.txt p{margin:0;font-size:14.5px;line-height:1.75;word-break:keep-all}
.txt p+p{margin-top:7px;padding-top:7px;border-top:1px dashed var(--line)}
.txt .hl{background:#2d6cdf;color:#fff;border-radius:3px;padding:0 2px}
.txt .hk{background:#1f8a5b;color:#fff;border-radius:3px;padding:0 2px}
.txt .nolink{color:#c0392b;text-decoration:underline wavy #c0392b 1px}
</style>
<header>
  <h1 id="h">__TITLE__</h1>
  <div class="sub" id="s"></div>
</header>
<nav id="nav"></nav>
<main>
  <div class="txt"><p id="te"></p><p id="tk"></p></div>
  <div class="lab">영어 — 누르세요 (여러 개 가능)</div>
  <div class="row" id="en"></div>
  <div class="lab">한국어 — 짝이 되는 낱말을 눌러 켜고 끄세요</div>
  <div class="row" id="ko"></div>
  <div class="hint" id="hint"></div>
  <div class="bar">
    <button id="prev">◀ 앞 낱말</button>
    <button id="next" class="p">다음 낱말 ▶</button>
    <button id="multi">여러 개 고르기: 끔</button>
    <button id="clear">대응 없음</button>
    <button id="reset">되돌리기</button>
  </div>
  <div class="lab">결과 — 이대로 붙여 주시면 됩니다</div>
  <textarea id="out" readonly></textarea>
  <div class="bar">
    <button id="copy" class="p">복사</button>
    <button id="dl">파일로 내리기</button>
    <button id="wipe">전부 지우기</button>
  </div>
  <div class="cnt" id="cnt"></div>
</main>
<script>
const DATA = __DATA__;
const BOOK = DATA.book, CH = DATA.ch, NAME = DATA.name;
const bOf=v=>v.b!=null?v.b:BOOK, cOf=v=>v.c!=null?v.c:CH,
      nOf=v=>v.ref?v.ref.replace(/ \d+:\d+$/,''):NAME,
      rOf=v=>v.ref||(CH+':'+v.v);
// 같은 낱말이 여러 번이면 #번호를 붙인 이름표
function label(ws){
  const c={}; ws.forEach(w=>c[w]=(c[w]||0)+1);
  const seen={};
  return ws.map(w=>{seen[w]=(seen[w]||0)+1; return c[w]>1?w+"#"+seen[w]:w;});
}
const V = DATA.verses.map(v=>({...v, enL:label(v.en), koL:label(v.ko)}));
let vi=0, sel=[0], anchor=0, multi=false;
// edits[verseIdx][enIdx] = [koIdx,...]  (손댄 것만)
const edits={};
const lead=()=>sel.length?sel[sel.length-1]:0;

function cur(){return V[vi];}
function linksOf(v){            // 영어 idx -> 한국어 idx 배열 (지금 상태)
  const m={};
  v.pairs.forEach(([k,e])=>{(m[e]=m[e]||[]).push(k);});
  const ed=edits[vi]||{};
  for(const e in ed) m[e]=ed[e].slice();
  return m;
}
function draw(){
  const v=cur(), m=linksOf(v);
  document.getElementById('s').textContent=
    `${rOf(v)} · 영어 ${v.en.length}낱말 · 한국어 ${v.ko.length}낱말`;
  const nav=document.getElementById('nav'); nav.innerHTML='';
  V.forEach((x,i)=>{
    const b=document.createElement('button');
    b.textContent=rOf(x);
    if(i===vi)b.className='on';
    else if(edits[i]&&Object.keys(edits[i]).length)b.className='done';
    b.onclick=()=>{vi=i;sel=[0];anchor=0;draw();};
    nav.appendChild(b);
  });
  // 본문 전체 — 고른 영어 낱말과 그 짝 한국어를 물들인다
  const paint=(raw,sp,on,cls,bad)=>{
    let h='', at=0;
    sp.forEach((p,i)=>{
      h+=esc(raw.slice(at,p[0]));
      const c = on.has(i) ? cls : (bad&&bad.has(i) ? 'nolink' : '');
      const w = esc(raw.slice(p[0],p[1]));
      h += c ? '<span class="'+c+'">'+w+'</span>' : w;
      at=p[1];
    });
    return h+esc(raw.slice(at));
  };
  const selE=new Set(sel);
  const selK=new Set(); sel.forEach(e=>(m[e]||[]).forEach(k=>selK.add(k)));
  const noE=new Set(); v.en.forEach((w,i)=>{ if(!(m[i]&&m[i].length)) noE.add(i); });
  const hasK=new Set(); for(const e in m) (m[e]||[]).forEach(k=>hasK.add(+k));
  const noK=new Set(); v.ko.forEach((w,i)=>{ if(!hasK.has(i)) noK.add(i); });
  document.getElementById('te').innerHTML=paint(v.et||'',v.es||[],selE,'hl',noE);
  document.getElementById('tk').innerHTML=paint(v.kt||'',v.ks||[],selK,'hk',noK);

  const en=document.getElementById('en'); en.innerHTML='';
  v.en.forEach((w,i)=>{
    const b=document.createElement('button'); b.className='w';
    b.innerHTML=esc(w)+'<span class="n">'+i+'</span>';
    const t=m[i];
    if(sel.includes(i)){b.classList.add('cur'); if(i===lead())b.classList.add('lead');}
    else if(t&&t.length)b.classList.add('has');
    else b.classList.add('none');
    b.onclick=(ev)=>{
      const add=multi||ev.ctrlKey||ev.metaKey;
      if(ev.shiftKey&&sel.length){
        const a=Math.min(anchor,i), z=Math.max(anchor,i);
        sel=[]; for(let x=a;x<=z;x++)sel.push(x);
      }else if(add){
        const p=sel.indexOf(i);
        if(p<0){sel.push(i);} else if(sel.length>1){sel.splice(p,1);}
        anchor=i;
      }else{sel=[i];anchor=i;}
      draw();
    };
    en.appendChild(b);
  });
  const tg=new Set(); sel.forEach(e=>(m[e]||[]).forEach(k=>tg.add(k)));
  const linked=new Set(); v.pairs.forEach(([k,e])=>{
    const ed=edits[vi]||{}; if(ed[e]) return; linked.add(k);});
  for(const e in (edits[vi]||{})) (edits[vi][e]||[]).forEach(k=>linked.add(k));
  const ko=document.getElementById('ko'); ko.innerHTML='';
  v.ko.forEach((w,i)=>{
    const b=document.createElement('button'); b.className='w';
    b.innerHTML=esc(w)+'<span class="n">'+i+'</span>';
    if(tg.has(i))b.classList.add('tgt');
    else if(linked.has(i))b.classList.add('has');
    else b.classList.add('none');
    b.onclick=()=>{
      const e=edits[vi]=edits[vi]||{};
      const on=!tg.has(i);          // 꺼져 있으면 고른 영어 전부에 켠다
      sel.forEach(x=>{
        const a=e[x]=(e[x]||(m[x]||[]).slice());
        const p=a.indexOf(i);
        if(on){if(p<0)a.push(i);} else if(p>=0)a.splice(p,1);
        a.sort((y,z)=>y-z);
      });
      draw();
    };
    ko.appendChild(b);
  });
  document.getElementById('hint').textContent =
    `고른 영어 ${sel.length}개: ${sel.map(e=>v.enL[e]).join(' + ')}`
    + `   →   ${[...tg].sort((a,b)=>a-b).map(k=>v.koL[k]).join(', ')||'(없음)'}`;
  render();
}
function esc(s){return s.replace(/[&<>]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;'}[c]));}
function render(){
  const out=[]; let n=0;
  V.forEach((v,i)=>{
    const ed=edits[i]; if(!ed)return;
    const ks=Object.keys(ed).map(Number).sort((a,b)=>a-b);
    if(!ks.length)return;
    out.push(`    # ---- ${rOf(v)} ----`);
    ks.forEach(e=>{
      const ws=ed[e].map(k=>v.koL[k]);
      out.push(`    dict(ref=(${bOf(v)}, ${cOf(v)}, ${v.v}), lang='ko', en=${q(v.enL[e])}, words=[${ws.map(q).join(', ')}]),`);
      n++;
    });
    out.push('');
  });
  document.getElementById('out').value=out.join('\n');
  document.getElementById('cnt').textContent=n?`${n}줄`:'아직 손댄 것이 없습니다';
}
function q(s){return "'"+s.replace(/\\/g,'\\\\').replace(/'/g,"\\'")+"'";}
document.getElementById('next').onclick=()=>{
  const i=lead();
  if(i<cur().en.length-1){sel=[i+1];}
  else if(vi<V.length-1){vi++;sel=[0];}
  anchor=lead(); draw();
};
document.getElementById('prev').onclick=()=>{
  const i=sel.length?sel[0]:0;
  if(i>0){sel=[i-1];} else if(vi>0){vi--;sel=[V[vi].en.length-1];}
  anchor=lead(); draw();
};
document.getElementById('multi').onclick=()=>{
  multi=!multi;
  document.getElementById('multi').textContent='여러 개 고르기: '+(multi?'켬':'끔');
  document.getElementById('multi').classList.toggle('p',multi);
};
document.getElementById('clear').onclick=()=>{
  const e=edits[vi]=edits[vi]||{}; sel.forEach(x=>e[x]=[]); draw();
};
document.getElementById('reset').onclick=()=>{
  if(edits[vi]){
    sel.forEach(x=>delete edits[vi][x]);
    if(!Object.keys(edits[vi]).length)delete edits[vi];
  }
  draw();
};
document.getElementById('wipe').onclick=()=>{
  if(confirm('손댄 것을 전부 지울까요?')){for(const k in edits)delete edits[k];draw();}
};
document.getElementById('copy').onclick=async()=>{
  const t=document.getElementById('out');
  try{await navigator.clipboard.writeText(t.value);}
  catch(e){t.removeAttribute('readonly');t.select();document.execCommand('copy');t.setAttribute('readonly','');}
  const b=document.getElementById('copy');b.textContent='복사했습니다';setTimeout(()=>b.textContent='복사',1200);
};
document.getElementById('dl').onclick=()=>{
  const a=document.createElement('a');
  a.href=URL.createObjectURL(new Blob([document.getElementById('out').value],{type:'text/plain'}));
  a.download=`fixlinks-${BOOK==null?'picked':BOOK+'-'+CH}.txt`; a.click();
};
addEventListener('keydown',e=>{
  if(e.target.tagName==='TEXTAREA')return;
  if(e.key==='ArrowRight'){document.getElementById('next').click();e.preventDefault();}
  if(e.key==='ArrowLeft'){document.getElementById('prev').click();e.preventDefault();}
});
draw();
</script>
"""


def spans(t):
    """낱말마다 [시작, 끝] 자리를 돌려준다 — toks 와 같은 규칙."""
    out, st = [], None
    t = t or ''
    for i, ch in enumerate(t):
        isw = unicodedata.category(ch)[0] in ('L', 'M') or (
            ch == '\u2013' and st is not None and i + 1 < len(t)
            and unicodedata.category(t[i + 1])[0] in ('L', 'M'))
        if isw:
            if st is None: st = i
        elif st is not None:
            out.append([st, i]); st = None
    if st is not None: out.append([st, len(t)])
    return out


def one(bb, ch, v, al, EN, KO):
    e = toks(EN[ch - 1][v - 1]) if ch - 1 < len(EN) and v - 1 < len(EN[ch - 1]) else []
    k = toks(KO[ch - 1][v - 1]) if ch - 1 < len(KO) and v - 1 < len(KO[ch - 1]) else []
    if not e or not k: return None
    q = (al['v'][ch - 1][v - 1] or {}).get('ko') or []
    return {'v': v, 'b': bb, 'c': ch, 'ref': f'{BK[bb]} {ch}:{v}', 'en': e, 'ko': k,
            'et': EN[ch - 1][v - 1] or '', 'kt': KO[ch - 1][v - 1] or '',
            'es': spans(EN[ch - 1][v - 1]), 'ks': spans(KO[ch - 1][v - 1]),
            'pairs': [[q[i], q[i + 1]] for i in range(0, len(q), 2)]}


def write(data, title, out):
    html = (HTML.replace('__TITLE__', title)
                .replace('__DATA__', json.dumps(data, ensure_ascii=False)))
    io.open(out, 'w', encoding='utf-8').write(html)
    print(f'{title} — {len(data["verses"])}절, {out} ({os.path.getsize(out) // 1024}KB)')


def main():
    if '--verses' in sys.argv:
        i = sys.argv.index('--verses')
        lst = sys.argv[i + 1]
        title = sys.argv[i + 2] if len(sys.argv) > i + 2 else '고른 절'
        out = sys.argv[i + 3] if len(sys.argv) > i + 3 else '/tmp/edit-picked.html'
        refs = []
        for ln in io.open(lst, encoding='utf-8'):
            p = ln.split()
            if len(p) >= 3: refs.append((int(p[0]), int(p[1]), int(p[2])))
        verses = []
        cache = {}
        for bb, ch, v in refs:
            if bb not in cache:
                cache[bb] = (json.load(io.open(f'{D}al{bb:02d}.json', encoding='utf-8')),
                             json.load(io.open(f'{TX}en{bb:02d}.json', encoding='utf-8')),
                             json.load(io.open(f'{TX}ko{bb:02d}.json', encoding='utf-8')))
            r = one(bb, ch, v, *cache[bb])
            if r: verses.append(r)
        write({'book': None, 'ch': None, 'name': None, 'verses': verses}, title, out)
        return
    if len(sys.argv) < 3:
        print(__doc__); return
    bb, ch = int(sys.argv[1]), int(sys.argv[2])
    out = sys.argv[3] if len(sys.argv) > 3 else f'/tmp/edit-{bb}-{ch}.html'
    al = json.load(io.open(f'{D}al{bb:02d}.json', encoding='utf-8'))
    EN = json.load(io.open(f'{TX}en{bb:02d}.json', encoding='utf-8'))
    KO = json.load(io.open(f'{TX}ko{bb:02d}.json', encoding='utf-8'))
    verses = [r for v in range(1, len(al['v'][ch - 1]) + 1)
              if (r := one(bb, ch, v, al, EN, KO))]
    write({'book': bb, 'ch': ch, 'name': BK[bb], 'verses': verses},
          f'{BK[bb]} {ch}장', out)


if __name__ == '__main__':
    main()
