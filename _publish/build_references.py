#!/usr/bin/env python3
# 외부 레퍼런스 라이브 보드 빌더 (+모션 아키타입 라이브 미리보기)
import json, os
HERE = os.path.dirname(os.path.abspath(__file__))
DATA = json.load(open(os.path.join(HERE, "references.json"), encoding="utf-8"))
OUT = os.path.join(HERE, "..", "design-references.html")

CAT_LABEL = {
  "dark-saas": "다크 SaaS", "award-3d": "어워드·3D", "editorial": "에디토리얼",
  "kr-minimal": "한글·미니멀", "data-dash": "데이터·대시보드", "game": "게임·플레이풀",
}
MO_LABEL = {
  "shader":"셰이더 와이프","scene":"3D 씬 전환","grad":"그라데이션 플로우","parallax":"패럴럭스",
  "cosmos":"파티클/우주","marquee":"마퀴","reveal":"스크롤 리빌","lift":"호버 리프트",
  "scan":"스캔라인/CRT","pixel":"픽셀/레트로",
}
order = ["dark-saas","award-3d","editorial","kr-minimal","data-dash","game"]

def classify(e):
    t = (str(e.get("motion",""))+" "+str(e.get("type",""))+" "+str(e.get("category",""))+" "+str(e.get("why",""))).lower()
    def has(*ks): return any(k in t for k in ks)
    if has("스캔라인","crt","scanline","스캔 라인"): return "scan"
    if has("픽셀","도트","8-bit","8비트","retro","레트로","arcade","아케이드"): return "pixel"
    if has("3d","씬 전환","씬전환","scene","cube","큐브","입체"): return "scene"
    if has("셰이더","shader","glsl","wipe","와이프") or (has("webgl") and not has("3d")): return "shader"
    if has("패럴","parallax","시차","레이어 스크롤"): return "parallax"
    if has("별","파티클","particle","cosmos","입자","우주","node","노드"): return "cosmos"
    if has("그라데이션","gradient","메시","mesh","유동","blob","오로라","aurora","glow","글로우"): return "grad"
    if has("마퀴","marquee","롤링","ticker","흐르는"): return "marquee"
    if has("호버","hover","tilt","틸트","lift","리프트","마이크로","micro","뜨"): return "lift"
    return "reveal"

def _lum(h):
    h=h.lstrip('#');
    if len(h)==3: h=''.join(c*2 for c in h)
    try: r,g,b=int(h[0:2],16),int(h[2:4],16),int(h[4:6],16)
    except: return 0.5
    return (0.299*r+0.587*g+0.114*b)/255
def _sat(h):
    h=h.lstrip('#')
    if len(h)==3: h=''.join(c*2 for c in h)
    try: r,g,b=[int(h[i:i+2],16)/255 for i in (0,2,4)]
    except: return 0.0
    mx,mn=max(r,g,b),min(r,g,b)
    return 0.0 if mx==0 else (mx-mn)/mx
def _is_dark(pal):
    pal=[p for p in (pal or []) if isinstance(p,str) and p.startswith('#')]
    return sum(1 for p in pal if _lum(p) < 0.3) >= 2
def _roles(pal):
    pal=[p for p in (pal or []) if isinstance(p,str) and p.startswith('#')] or ['#ffffff','#111111']
    lightest=max(pal,key=_lum); darkest=min(pal,key=_lum)
    # dark-native design (≥2 dark tones = base+surface) → 어두운 배경. 아니면 라이트 기본.
    dark = _is_dark(pal)
    bg,fg = (darkest,lightest) if dark else (lightest,darkest)
    # primary/muted: preserve palette order (harvest puts brand/accent first) — more faithful than max-saturation
    rest=[p for p in pal if p not in (bg,fg)] or pal
    primary=rest[0]
    muted=rest[1] if len(rest)>1 else primary
    return bg,fg,primary,muted
def shadcn_vars(e):
    bg,fg,primary,muted=_roles(e.get('palette',[]))
    return (":root{\n"
        f"  --background: {bg};\n  --foreground: {fg};\n"
        f"  --primary: {primary};\n  --primary-foreground: {bg};\n"
        f"  --muted: {muted};\n  --accent: {primary};\n  --border: {muted};\n"
        "  --radius: 0.5rem;\n}")
def design_md(e):
    bg,fg,primary,muted=_roles(e.get('palette',[]))
    appr="approx · 근사 관측" if e.get('confidence')!='high' else "관측(high)"
    return "\n".join([
      f"# DESIGN.md — {e['name']}  ({appr})",
      f"> 출처 {e.get('url','')} · 색·타이포는 근사값일 수 있음. 정확값은 원본에서 확인.","",
      "## 1. Visual Theme & Atmosphere",e.get('why',''),"",
      "## 2. Color Palette & Roles",
      f"- background: {bg}",f"- foreground / text: {fg}",
      f"- primary / accent: {primary}",f"- muted / secondary: {muted}",
      "  (역할 배정은 근사 — 원본에서 확정)","",
      "## 3. Typography",e.get('type',''),"",
      "## 4. Components & Layout",e.get('borrow',''),
      "  - spacing: 8px scale · radius: 0.5rem (기본값 — 원본 관측 권장)","",
      "## 5. Motion",e.get('motion',''),"",
      "## 6. Do / Don't",
      "- Do: 위 팔레트·타이포 시그니처를 그대로 유지",
      "- Don't: 임의 색 추가 · 시그니처 웨이트 무시 · 과한 radius","",
      "## 7. Agent Prompt Guide",e.get('instruct',''),"",
      "## 8. shadcn/ui — CSS variables",shadcn_vars(e),
    ])
for e in DATA:
    e["mo"] = classify(e)
    e["dark"] = _is_dark(e.get("palette",[]))
    e["dmd"] = design_md(e)
    e["sc"] = shadcn_vars(e)
DATA.sort(key=lambda e: (order.index(e.get("category","")) if e.get("category","") in order else 9, e.get("name","")))

CHIPS = "".join(f'<button class="chip" data-cat="{c}">{CAT_LABEL[c]}</button>' for c in order)

TPL = r"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<script>(function(){var k='ds-theme',r=document.documentElement,s=localStorage.getItem(k);if(s)r.setAttribute('data-theme',s);else if(matchMedia('(prefers-color-scheme:dark)').matches)r.setAttribute('data-theme','dark');window.tg=function(){var d=r.getAttribute('data-theme')==='dark'?'light':'dark';r.setAttribute('data-theme',d);localStorage.setItem(k,d);};})();</script>
<title>Vibe Design Studio · 디자인 시스템 디렉토리 (__TOTAL__선)</title>
<meta name="description" content="실제 제품 디자인 시스템 __TOTAL__선 — 공식 문서 직링크 + 카드마다 복붙 DESIGN.md·shadcn 토큰. 색·모션은 관측(high)/근사(approx) 라벨. Vibe Design Studio.">
<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans+KR:wght@400;500;600;700&family=Noto+Serif+KR:wght@500;700&family=JetBrains+Mono:wght@400;700&display=swap" rel="stylesheet">
<style>
:root{--bg:#f6f2ea;--ink:#1b1a17;--mut:#6b6354;--card:#fffdf8;--bd:#e4dccb;--acc:#4b4ad1;--acc2:#b5532b;--code:#efe9dc}
html[data-theme=dark]{--bg:#100f14;--ink:#ece9f2;--mut:#9a93a6;--card:#1a1922;--bd:#2a2833;--acc:#8b8af0;--acc2:#e07a4d;--code:#1f1d28}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);font-family:'IBM Plex Sans KR',sans-serif;line-height:1.7;word-break:keep-all;-webkit-font-smoothing:antialiased}
.wrap{max-width:1180px;margin:0 auto;padding:0 24px}
header.top{display:flex;justify-content:space-between;align-items:center;padding:22px 0;font-weight:600}
nav a{color:var(--mut);text-decoration:none;margin-left:16px;font-size:14px}
nav a:hover{color:var(--acc)}
.tgl{width:34px;height:34px;border:1px solid var(--bd);border-radius:50%;background:var(--card);cursor:pointer;color:var(--ink)}
h1{font-family:'Noto Serif KR',serif;font-size:clamp(30px,5vw,52px);margin:28px 0 10px;letter-spacing:-.02em}
.lead{color:var(--mut);max-width:780px;margin:0 0 24px}
.lead b{color:var(--ink)}
.search{width:100%;padding:13px 16px;border:1px solid var(--bd);border-radius:12px;background:var(--card);color:var(--ink);font-size:15px;font-family:inherit;margin-bottom:14px}
.collabel{font:700 11px 'JetBrains Mono',monospace;color:var(--mut);text-transform:uppercase;letter-spacing:.08em;margin:6px 0 6px}
.chips{display:flex;flex-wrap:wrap;gap:8px;margin-bottom:8px}
.chip{padding:6px 14px;border:1px solid var(--bd);border-radius:999px;background:var(--card);color:var(--mut);font-size:13px;font-family:inherit;cursor:pointer}
.chip.on{background:var(--acc);color:#fff;border-color:var(--acc)}
.count{color:var(--mut);font-size:13px;font-family:'JetBrains Mono',monospace;margin:16px 0}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(330px,1fr));gap:18px;padding-bottom:60px}
.card{background:var(--card);border:1px solid var(--bd);border-radius:16px;padding:18px 18px 16px;display:flex;flex-direction:column;gap:10px}
.pal{display:flex;height:30px;border-radius:8px;overflow:hidden;border:1px solid var(--bd)}
.pal span{flex:1}
.ch{display:flex;align-items:center;gap:8px;flex-wrap:wrap}
.nm{font-family:'Noto Serif KR',serif;font-size:20px;font-weight:700}
.badge{font-size:11px;font-family:'JetBrains Mono',monospace;padding:2px 8px;border-radius:6px;background:var(--code);color:var(--mut)}
.badge.cat{color:var(--acc)}
.badge.high{color:#fff;background:var(--acc2)}
.badge.approx{border:1px dashed var(--bd);background:transparent}
.row{font-size:13.5px}
.row .k{color:var(--mut);font-size:11px;font-family:'JetBrains Mono',monospace;text-transform:uppercase;letter-spacing:.04em}
.instruct{background:var(--code);border-left:3px solid var(--acc);padding:9px 12px;font-size:13px}
.src{display:flex;justify-content:space-between;align-items:center;margin-top:2px}
.src a{color:var(--acc);text-decoration:none;font-size:12px;font-family:'JetBrains Mono',monospace}
.note{color:var(--mut);font-size:11px;line-height:1.5}
footer{color:var(--mut);font-size:12px;border-top:1px solid var(--bd);padding:20px 0 50px;line-height:1.7}
@media (max-width:560px){.grid{grid-template-columns:1fr}}

/* ===== DESIGN.md (바이브 코더용 복붙) ===== */
.dmd{margin-top:6px;border-top:1px dashed var(--bd);padding-top:8px}
.dmd>summary{cursor:pointer;font:600 12px 'JetBrains Mono',monospace;color:var(--acc);list-style:none}
.dmd>summary::-webkit-details-marker{display:none}
.dmd>summary::before{content:'▸ ';}
.dmd[open]>summary::before{content:'▾ ';}
.dmd pre{background:var(--code);border:1px solid var(--bd);border-radius:8px;padding:10px 11px;font:400 10.5px/1.55 'JetBrains Mono',monospace;color:var(--ink);overflow:auto;max-height:260px;white-space:pre-wrap;word-break:break-word;margin:8px 0}
.copybtn{font:600 11px 'JetBrains Mono',monospace;padding:4px 11px;border:1px solid var(--acc);background:transparent;color:var(--acc);border-radius:6px;cursor:pointer;margin-top:6px}
.copybtn:hover{background:var(--acc);color:#fff}

/* ===== 모션 아키타입 라이브 미리보기 (근사 연출) ===== */
.mo{position:relative;height:66px;border-radius:8px;overflow:hidden;border:1px solid var(--bd);background:#0d0d12}
.mo .lbl{position:absolute;left:8px;top:6px;z-index:9;font:11px 'JetBrains Mono',monospace;color:rgba(255,255,255,.6)}
.mo-shader .sh{position:absolute;inset:0;background:linear-gradient(90deg,#0a2540,#635bff,#00d4ff,#0a2540);background-size:300% 100%;animation:shf 3.5s linear infinite}
@keyframes shf{to{background-position:300% 0}}
.mo-shader .wipe{position:absolute;top:0;bottom:0;width:35%;left:-35%;background:linear-gradient(90deg,transparent,rgba(255,255,255,.55),transparent);animation:wp 2.4s ease-in-out infinite}
@keyframes wp{to{left:100%}}
.mo-grad .g{position:absolute;inset:-20%;background:linear-gradient(120deg,#635bff,#00d4ff,#b5532b,#635bff);background-size:300% 300%;filter:blur(6px);animation:gf 5s ease infinite}
@keyframes gf{0%{background-position:0 50%}50%{background-position:100% 50%}100%{background-position:0 50%}}
.mo-scene{perspective:320px}
.mo-scene .cube{position:absolute;left:50%;top:50%;width:42px;height:42px;margin:-21px 0 0 -21px;transform-style:preserve-3d;animation:rot 5s linear infinite}
.mo-scene .cube>*{position:absolute;inset:0;border:1px solid #8b8af0;background:rgba(139,138,240,.18)}
.mo-scene .f{transform:translateZ(21px)}
.mo-scene .bk{transform:rotateY(180deg) translateZ(21px)}
.mo-scene .l{transform:rotateY(-90deg) translateZ(21px)}
.mo-scene .r{transform:rotateY(90deg) translateZ(21px)}
@keyframes rot{0%{transform:rotateX(-18deg) rotateY(0)}100%{transform:rotateX(-18deg) rotateY(360deg)}}
.mo-parallax .p{position:absolute;height:10px;border-radius:5px}
.mo-parallax .p1{top:14px;width:55%;background:#635bff;animation:pa 3.2s linear infinite}
.mo-parallax .p2{top:29px;width:78%;background:#00d4ff;animation:pa 2.1s linear infinite}
.mo-parallax .p3{top:44px;width:42%;background:#b5532b;animation:pa 4.3s linear infinite}
@keyframes pa{0%{transform:translateX(-45%)}100%{transform:translateX(135%)}}
.mo-cosmos .s{position:absolute;width:3px;height:3px;border-radius:50%;background:#fff;animation:tw 2.2s ease-in-out infinite}
@keyframes tw{0%,100%{opacity:.2;transform:scale(.7)}50%{opacity:1;transform:scale(1.4)}}
.mo-marquee .t{position:absolute;top:50%;left:100%;white-space:nowrap;transform:translateY(-50%);color:#ece9f2;font:700 20px 'Noto Serif KR',serif;animation:mq 6s linear infinite}
@keyframes mq{to{left:-90%}}
.mo-reveal .b{position:absolute;left:14px;height:9px;border-radius:4px;background:#8b8af0;opacity:0}
.mo-reveal .b1{top:15px;width:55%;animation:rv 3s ease infinite}
.mo-reveal .b2{top:30px;width:75%;animation:rv 3s ease infinite .3s}
.mo-reveal .b3{top:45px;width:40%;animation:rv 3s ease infinite .6s}
@keyframes rv{0%,70%{opacity:0;transform:translateY(9px)}18%,52%{opacity:1;transform:none}}
.mo-lift .c{position:absolute;left:50%;top:50%;width:96px;height:34px;margin:-17px 0 0 -48px;border-radius:8px;background:#1a1922;border:1px solid #8b8af0;animation:lf 2.6s ease-in-out infinite}
@keyframes lf{0%,100%{transform:translateY(5px);box-shadow:0 2px 6px rgba(0,0,0,.4)}50%{transform:translateY(-7px);box-shadow:0 18px 34px rgba(139,138,240,.45)}}
.mo-scan .o{position:absolute;inset:0;background:repeating-linear-gradient(0deg,rgba(80,255,170,.13) 0 2px,transparent 2px 4px)}
.mo-scan .bar{position:absolute;left:0;right:0;height:16px;top:-16px;background:linear-gradient(rgba(80,255,170,.32),transparent);animation:sc 2.6s linear infinite}
@keyframes sc{to{top:66px}}
.mo-pixel .px{position:absolute;bottom:14px;width:12px;height:12px;background:#ff5fa2;animation:pk 1.1s steps(2) infinite}
@keyframes pk{0%{transform:translateY(0);background:#ff5fa2}50%{transform:translateY(-15px);background:#ffd23f}100%{transform:translateY(0);background:#5ad1ff}}
@media (prefers-reduced-motion:reduce){.mo *{animation:none!important}}
</style>
</head>
<body>
<div class="wrap">
<header class="top">
  <span>Vibe Design Studio · 디렉토리</span>
  <nav>
    <a href="design-studio.html">스튜디오</a><a href="design-systems.html">시스템</a><a href="design-presets.html">프리셋</a><a href="design-effects.html">효과</a><a href="design-catalog.html">카탈로그</a>
    <a href="https://github.com/ljhljh0703-cmd/VDS" target="_blank" rel="noopener" style="border:1px solid currentColor;border-radius:999px;padding:3px 11px;font-weight:700;text-decoration:none;white-space:nowrap">GitHub ↗</a>
    <button class="tgl" onclick="tg()" aria-label="테마 전환">◐</button>
  </nav>
</header>

<h1>디자인 시스템 디렉토리</h1>
<p class="lead">실제 제품의 <b>디자인 시스템 __TOTAL__선</b> — 공식 문서로 바로 점프하고, 카드마다 <b>복붙용 DESIGN.md · shadcn 변수</b>를 떠갑니다(바이브 코더용). 색·모션은 <b>관측(high)/근사(approx)</b> 정직 표기(__TOTAL__개 중 __APPROX__개 근사) — 정확한 값은 <b>공식 링크</b>로 확인하세요.</p>

<input class="search" id="q" placeholder="검색 — 이름·시그니처·차용·지시문구 (예: 다크, 세리프, 셰이더, 한글)">
<div class="collabel">컬렉션</div>
<div class="chips" id="chips"><button class="chip on" data-cat="all">전체</button>__CHIPS__<button class="chip" data-cat="__dark">🌙 Dark-Mode-Native</button><button class="chip" data-cat="__dmd">📋 DESIGN.md 복붙</button></div>
<div class="count" id="count"></div>
<div class="grid" id="grid"></div>

<footer>
출처 = 각 사이트 공개 페이지·디자인 리뷰·갤러리. 색·시그니처는 관측분만 high, 미관측분은 approx(근사). 모션 미리보기는 10개 아키타입 <b>근사 연출</b>. DESIGN.md·shadcn 토큰은 관측값 기반 <b>근사 생성</b>이며 정확값은 공식 링크로 확인하세요. 외부 브랜드의 상표·디자인은 각 권리자 소유. 디렉토리 형식은 <b>oh-my-design.kr</b>(MIT)에서 영감을 받았습니다. © 2026 이주형 · Vibe Design Studio.
</footer>
</div>

<script>
const DATA=__PAYLOAD__;
const CAT=__CATMAP__;
const MOL=__MOMAP__;
let cat="all",q="";
const grid=document.getElementById('grid'),count=document.getElementById('count');
function esc(s){return (s||"").replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));}
function moInner(a){
  if(a==='shader')return '<div class="sh"></div><div class="wipe"></div>';
  if(a==='grad')return '<div class="g"></div>';
  if(a==='scene')return '<div class="cube"><div class="f"></div><div class="bk"></div><div class="l"></div><div class="r"></div></div>';
  if(a==='parallax')return '<i class="p p1"></i><i class="p p2"></i><i class="p p3"></i>';
  if(a==='cosmos'){let s='';for(let i=0;i<14;i++){s+='<i class="s" style="left:'+(Math.random()*94+3).toFixed(1)+'%;top:'+(Math.random()*80+8).toFixed(1)+'%;animation-delay:'+(Math.random()*2).toFixed(2)+'s"></i>';}return s;}
  if(a==='marquee')return '<span class="t">감각을 시스템으로 · 감각을 시스템으로 ·</span>';
  if(a==='reveal')return '<i class="b b1"></i><i class="b b2"></i><i class="b b3"></i>';
  if(a==='lift')return '<div class="c"></div>';
  if(a==='scan')return '<div class="o"></div><div class="bar"></div>';
  if(a==='pixel'){let s='';for(let i=0;i<6;i++){s+='<i class="px" style="left:'+(10+i*16)+'px;animation-delay:'+(i*0.14).toFixed(2)+'s"></i>';}return s;}
  return '';
}
function card(e){
  const pal=(e.palette||[]).map(c=>'<span style="background:'+esc(c)+'"></span>').join("");
  const cb='<span class="badge cat">'+(CAT[e.category]||e.category)+'</span>';
  const conf=e.confidence==="high"?'<span class="badge high">관측</span>':'<span class="badge approx">근사</span>';
  return '<div class="card">'
    +'<div class="pal">'+pal+'</div>'
    +'<div class="mo mo-'+e.mo+'" aria-hidden="true"><span class="lbl">모션 ≈ '+(MOL[e.mo]||e.mo)+'</span>'+moInner(e.mo)+'</div>'
    +'<div class="ch"><span class="nm">'+esc(e.name)+'</span>'+cb+conf+'</div>'
    +'<div class="row"><span class="k">타이포</span><br>'+esc(e.type)+'</div>'
    +'<div class="row"><span class="k">모션</span><br>'+esc(e.motion)+'</div>'
    +'<div class="row">'+esc(e.why)+'</div>'
    +'<div class="row"><span class="k">차용</span><br>'+esc(e.borrow)+'</div>'
    +'<div class="instruct">'+esc(e.instruct)+'</div>'
    +'<details class="dmd"><summary>📋 DESIGN.md — 복붙용 (바이브 코더)</summary>'
      +'<button class="copybtn">DESIGN.md 복사</button>'
      +'<pre>'+esc(e.dmd)+'</pre>'
      +'<button class="copybtn">shadcn CSS 변수 복사</button>'
      +'<pre>'+esc(e.sc)+'</pre>'
    +'</details>'
    +'<div class="src"><a href="'+esc(e.url)+'" target="_blank" rel="noopener">공식 사이트 · '+esc((e.url||"").replace(/^https?:\/\//,'').replace(/\/$/,''))+' ↗</a></div>'
    +'<div class="note">'+esc(e.source_note)+'</div>'
  +'</div>';
}
function render(){
  const f=DATA.filter(e=>{
    if(cat==="__dark"){ if(!e.dark)return false; }
    else if(cat==="__dmd"){ /* 전 항목 DESIGN.md 보유 */ }
    else if(cat!=="all"&&e.category!==cat)return false;
    if(q){const h=(e.name+" "+e.type+" "+e.motion+" "+e.why+" "+e.borrow+" "+e.instruct+" "+e.dmd).toLowerCase();if(!h.includes(q))return false;}
    return true;
  });
  count.textContent=f.length+" / "+DATA.length+" 레퍼런스";
  grid.innerHTML=f.map(card).join("");
}
document.getElementById('chips').addEventListener('click',ev=>{
  const b=ev.target.closest('.chip');if(!b)return;
  document.querySelectorAll('.chip').forEach(c=>c.classList.remove('on'));
  b.classList.add('on');cat=b.dataset.cat;render();
});
document.getElementById('q').addEventListener('input',e=>{q=e.target.value.trim().toLowerCase();render();});
document.addEventListener('click',ev=>{
  const b=ev.target.closest('.copybtn'); if(!b)return;
  const pre=b.nextElementSibling;
  if(pre&&pre.tagName==='PRE'){
    navigator.clipboard&&navigator.clipboard.writeText(pre.textContent);
    const o=b.textContent; b.textContent='복사됨 ✓'; setTimeout(()=>b.textContent=o,1200);
  }
});
render();
</script>
</body>
</html>"""

HTML = (TPL
  .replace("__PAYLOAD__", json.dumps(DATA, ensure_ascii=False))
  .replace("__CATMAP__", json.dumps(CAT_LABEL, ensure_ascii=False))
  .replace("__MOMAP__", json.dumps(MO_LABEL, ensure_ascii=False))
  .replace("__CHIPS__", CHIPS)
  .replace("__TOTAL__", str(len(DATA)))
  .replace("__APPROX__", str(sum(1 for e in DATA if e.get("confidence") != "high"))))

open(OUT, "w", encoding="utf-8").write(HTML)
mo_counts = {}
for e in DATA: mo_counts[e["mo"]] = mo_counts.get(e["mo"],0)+1
print("references ->", len(DATA), "-> docs/design-references.html")
print("motion archetypes:", mo_counts)
