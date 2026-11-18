# -*- coding: utf-8 -*-
"""한 장(章)을 클릭으로 매칭하는 편집기 HTML 을 만든다.

영어 낱말을 하나 고르고 한국어 낱말들을 눌러 짝을 맞추면, 아래쪽에
tools/fix_links.py 에 그대로 붙일 수 있는 항목이 쌓인다. #번호는 자동으로 붙는다.

usage: python3 tools/make_editor.py <책번호> <장> [내보낼파일]
       python3 tools/make_editor.py 57 11 /tmp/edit-heb11.html
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
</style>
<header>
  <h1 id="h">__TITLE__</h1>
  <div class="sub" id="s"></div>
</header>
<nav id="nav"></nav>
<main>
  <div class="lab">영어 — 하나를 누르세요</div>
  <div class="row" id="en"></div>
  <div class="lab">한국어 — 짝이 되는 낱말을 눌러 켜고 끄세요</div>
  <div class="row" id="ko"></div>
  <div class="hint" id="hint"></div>
  <div class="bar">
    <button id="prev">◀ 앞 낱말</button>
    <button id="next" class="p">다음 낱말 ▶</button>
    <button id="clear">이 낱말 대응 없음</button>
    <button id="reset">이 낱말 되돌리기</button>
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
// 같은 낱말이 여러 번이면 #번호를 붙인 이름표
function label(ws){
  const c={}; ws.forEach(w=>c[w]=(c[w]||0)+1);
  const seen={};
  return ws.map(w=>{seen[w]=(seen[w]||0)+1; return c[w]>1?w+"#"+seen[w]:w;});
}
const V = DATA.verses.map(v=>({...v, enL:label(v.en), koL:label(v.ko)}));
let vi=0, ei=0;
// edits[verseIdx][enIdx] = [koIdx,...]  (손댄 것만)
const edits={};

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
    `${CH}:${v.v} · 영어 ${v.en.length}낱말 · 한국어 ${v.ko.length}낱말`;
  const nav=document.getElementById('nav'); nav.innerHTML='';
  V.forEach((x,i)=>{
    const b=document.createElement('button');
    b.textContent=CH+':'+x.v;
    if(i===vi)b.className='on';
    else if(edits[i]&&Object.keys(edits[i]).length)b.className='done';
    b.onclick=()=>{vi=i;ei=0;draw();};
    nav.appendChild(b);
  });
  const en=document.getElementById('en'); en.innerHTML='';
  v.en.forEach((w,i)=>{
    const b=document.createElement('button'); b.className='w';
    b.innerHTML=esc(w)+'<span class="n">'+i+'</span>';
    const t=m[i];
    if(i===ei)b.classList.add('cur');
    else if(t&&t.length)b.classList.add('has');
    else b.classList.add('none');
    b.onclick=()=>{ei=i;draw();};
    en.appendChild(b);
  });
  const tg=new Set(m[ei]||[]);
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
      const a=e[ei]=(e[ei]||(m[ei]||[]).slice());
      const p=a.indexOf(i); if(p<0)a.push(i); else a.splice(p,1);
      a.sort((x,y)=>x-y); draw();
    };
    ko.appendChild(b);
  });
  document.getElementById('hint').textContent =
    `고른 영어: ${v.enL[ei]}   →   ${(m[ei]||[]).map(k=>v.koL[k]).join(', ')||'(없음)'}`;
  render();
}
function esc(s){return s.replace(/[&<>]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;'}[c]));}
function render(){
  const out=[]; let n=0;
  V.forEach((v,i)=>{
    const ed=edits[i]; if(!ed)return;
    const ks=Object.keys(ed).map(Number).sort((a,b)=>a-b);
    if(!ks.length)return;
    out.push(`    # ---- ${NAME} ${CH}:${v.v} ----`);
    ks.forEach(e=>{
      const ws=ed[e].map(k=>v.koL[k]);
      out.push(`    dict(ref=(${BOOK}, ${CH}, ${v.v}), lang='ko', en=${q(v.enL[e])}, words=[${ws.map(q).join(', ')}]),`);
      n++;
    });
    out.push('');
  });
  document.getElementById('out').value=out.join('\n');
  document.getElementById('cnt').textContent=n?`${n}줄`:'아직 손댄 것이 없습니다';
}
function q(s){return "'"+s.replace(/\\/g,'\\\\').replace(/'/g,"\\'")+"'";}
document.getElementById('next').onclick=()=>{
  if(ei<cur().en.length-1){ei++;}
  else if(vi<V.length-1){vi++;ei=0;}
  draw();
};
document.getElementById('prev').onclick=()=>{
  if(ei>0){ei--;} else if(vi>0){vi--;ei=V[vi].en.length-1;}
  draw();
};
document.getElementById('clear').onclick=()=>{
  (edits[vi]=edits[vi]||{})[ei]=[]; draw();
};
document.getElementById('reset').onclick=()=>{
  if(edits[vi]){delete edits[vi][ei]; if(!Object.keys(edits[vi]).length)delete edits[vi];} draw();
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
  a.download=`fixlinks-${BOOK}-${CH}.txt`; a.click();
};
addEventListener('keydown',e=>{
  if(e.target.tagName==='TEXTAREA')return;
  if(e.key==='ArrowRight'){document.getElementById('next').click();e.preventDefault();}
  if(e.key==='ArrowLeft'){document.getElementById('prev').click();e.preventDefault();}
});
draw();
</script>
"""


def main():
    if len(sys.argv) < 3:
        print(__doc__); return
    bb, ch = int(sys.argv[1]), int(sys.argv[2])
    out = sys.argv[3] if len(sys.argv) > 3 else f'/tmp/edit-{bb}-{ch}.html'
    al = json.load(io.open(f'{D}al{bb:02d}.json', encoding='utf-8'))
    EN = json.load(io.open(f'{TX}en{bb:02d}.json', encoding='utf-8'))
    KO = json.load(io.open(f'{TX}ko{bb:02d}.json', encoding='utf-8'))
    verses = []
    for v, rec in enumerate(al['v'][ch - 1]):
        e = toks(EN[ch - 1][v]) if v < len(EN[ch - 1]) else []
        k = toks(KO[ch - 1][v]) if ch - 1 < len(KO) and v < len(KO[ch - 1]) else []
        if not e or not k: continue
        q = (rec or {}).get('ko') or []
        verses.append({'v': v + 1, 'en': e, 'ko': k,
                       'pairs': [[q[i], q[i + 1]] for i in range(0, len(q), 2)]})
    data = {'book': bb, 'ch': ch, 'name': BK[bb], 'verses': verses}
    title = f'{BK[bb]} {ch}장'
    html = (HTML.replace('__TITLE__', title)
                .replace('__DATA__', json.dumps(data, ensure_ascii=False)))
    io.open(out, 'w', encoding='utf-8').write(html)
    print(f'{title} — {len(verses)}절, {out} ({os.path.getsize(out)//1024}KB)')


if __name__ == '__main__':
    main()
