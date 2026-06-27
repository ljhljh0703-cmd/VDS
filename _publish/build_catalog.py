#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""design-catalog 빌더. ENTRIES(데이터) → catalog.json(SSOT) + design-catalog.html(인터랙티브).
재생성·증분 갱신용. 항목마다 src(출처) 필수. 통제어휘 CATS / tier core|advanced|principle."""
import json, re, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
VAULT = HERE.parent.parent
OUT_JSON = HERE / "catalog.json"
OUT_HTML = HERE.parent / "design-catalog.html"  # repo-root (VDS deploy layout)

CATS = ["tokens-theme","layout-responsive","typography-kr","components","motion-interaction",
        "svg-canvas","data-viz","media-embed","accessibility","honesty-provenance",
        "performance-selfcontained","publishing-governance","design-principles","workflow-skills"]

def E(id,ko,en,cat,tier,what,when,instr,alias,pattern,src,qa="",demo=""):
    return dict(id=id,ko=ko,en=en,cat=cat,tier=tier,what=what,when=when,instr=instr,
                alias=alias,pattern=pattern,src=src,qa=qa,demo=demo)

ENTRIES = [
# ---------- tokens-theme ----------
E("theme-toggle","라이트/다크 토글","Light/dark toggle","tokens-theme","core",
  "data-theme + localStorage로 라이트↔다크 전환, OS설정 추종, 선택 기억.",
  "모든 공개 페이지 기본 셸.","“라이트/다크 토글 넣어”",["테마전환","다크모드"],
  "head 최상단 인라인 스크립트로 data-theme 선적용(플래시 방지) → toggleTheme()로 전환·localStorage 저장.",
  "DESIGN-SYSTEM.md §5 · _tpl-concept.html","플래시 방지 위해 head에서 선적용 필수."),
E("tokens-3layer","3레이어 디자인 토큰","3-layer tokens","tokens-theme","advanced",
  "raw 팔레트 → theme 토큰(light/dark) → modifier(color-mix) 3층 구조.",
  "토큰 체계 새로 짤 때.","“토큰 3레이어로 정리해”",["토큰구조","semantic token"],
  ":root raw(--gray-50..900) → --color-theme-* → color-mix 파생.",
  "templates/html/_tokens.css"),
E("oklch-palette","OKLCH 팔레트","OKLCH palette","tokens-theme","advanced",
  "OKLCH로 명도·채도 일관 제어한 뉴트럴/브랜드 스케일.",
  "지각적 균일 색계단 필요.","“OKLCH로 팔레트 잡아”",["oklch"],
  "oklch(L% C H) — L만 단계화하면 균일 계단.","templates/html/_tokens.css"),
E("palette-presets","팔레트 프리셋 4종","Palette presets","tokens-theme","advanced",
  "deep-blue/warm-terracotta/monochrome/creator-violet를 data-palette로 교체.",
  "한 코드에 톤 변형.","“팔레트 monochrome으로 바꿔”",["data-palette"],
  "[data-palette='monochrome']{--brand-*…}","templates/html/_tokens.css"),
E("editorial-warm","에디토리얼 웜 팔레트","Editorial warm palette","tokens-theme","core",
  "크림 배경·잉크 텍스트·와인 액센트의 출판물 톤.",
  "이력서·포폴 공유 톤.","“Resume 톤(크림/잉크/와인)으로”",["에디토리얼","resume톤"],
  "--bg#faf7f1 --ink#1a1814 --accent#7a1f2d / serif display.",
  "docs/Resume_LeeJuHyeong.html · DESIGN-SYSTEM.md",
  "", "<span class='sw' style='background:#faf7f1'></span><span class='sw' style='background:#7a1f2d'></span><span class='sw' style='background:#1a1814'></span>"),
E("color-mix-soft","color-mix 소프트 배경","color-mix soft bg","tokens-theme","core",
  "액센트를 12~16% 투명 혼합해 은은한 배경/보더 생성.",
  "강조 박스·칩 배경.","“액센트 연하게 깔아”",["accent-soft"],
  "color-mix(in oklab, var(--accent) 12%, transparent)","templates/html/_tokens.css"),

# ---------- typography-kr ----------
E("keep-all","한글 keep-all","Korean keep-all","typography-kr","core",
  "음절 단위 줄바꿈 방지(어절 단위로).",
  "모든 한글 본문.","“글자 중간에 자르지 마”",["줄바꿈","음절잘림"],
  "word-break:keep-all; overflow-wrap:break-word;","memory:html-production-toolkit · 전 페이지",
  "필수. 미적용 시 한글 가독성 급락.",
  "<div class='demo-keep'><b>keep-all</b><p style='word-break:keep-all;width:120px'>지식 운영체계를 만든다</p><b>기본</b><p style='word-break:break-all;width:120px'>지식 운영체계를 만든다</p></div>"),
E("han-eng-align","한·영 cap-height 정렬","KO-EN cap align","typography-kr","advanced",
  "mono 혼용 시 한·영 글자높이 불일치 보정.",
  "JetBrains Mono+한글 섞을 때.","“한영 높이 안 맞아 보정해”",["mono정렬"],
  "@font-face size-adjust + Nanum Gothic Coding 공급.","templates/html/_tokens.css §한·영"),
E("headline-scale","헤드라인 6단 스케일","Headline scale","typography-kr","core",
  "clamp 기반 6단계 반응형 헤드라인.",
  "타이포 위계 잡을 때.","“헤드라인 위계 6단으로”",["clamp헤드라인"],
  "--headline-1: clamp(2.5rem,5vw+1rem,4.5rem)","templates/html/_tokens.css"),
E("font-presets","폰트 프리셋 4종","Font presets","typography-kr","advanced",
  "gothic/serif/display/mono 프리셋(환각 방지 화이트리스트).",
  "폰트 톤 바꿀 때.","“serif(명조)로 가”",["폰트프리셋"],
  "[data-font='serif']{--font-active:…}","templates/html/_tokens.css"),
E("serif-display","명조 디스플레이","Serif display","typography-kr","core",
  "Noto Serif KR을 제목용으로 써 에디토리얼 무게감.",
  "이력서·격식 포폴.","“제목 명조로”",["noto serif"],
  "--font-display:'Noto Serif KR' / 본문은 산세리프.","DESIGN-SYSTEM.md"),

# ---------- layout-responsive ----------
E("auto-fit-grid","auto-fit 반응형 그리드","Auto-fit grid","layout-responsive","core",
  "열 수를 폭이 자동 결정하는 카드 그리드.",
  "카드 묶음 반응형.","“카드 자동 줄바꿈 그리드로”",["auto-fit"],
  "grid-template-columns:repeat(auto-fit,minmax(260px,1fr))","memory · 전 페이지"),
E("reading-column","리딩 컬럼 폭 제한","Reading column","layout-responsive","core",
  "본문 최대폭 ~680px로 가독성 확보.",
  "글 위주 페이지.","“본문 폭 좁혀 읽기 편하게”",["maxwidth","680"],
  "max-width:680px(narrow) / 880 / 1080 컨테이너 스케일.","Claude Design · _tokens.css"),
E("clamp-fluid","clamp 유체 타이포","Fluid type clamp","layout-responsive","core",
  "뷰포트 따라 매끄럽게 크는 글자.",
  "헤드라인·여백.","“글자 반응형으로 키워”",["clamp"],
  "font-size:clamp(min, 5vw, max)","전 페이지"),
E("mobile-svg-minwidth","모바일 와이드 SVG 보정","Mobile SVG min-width","layout-responsive","advanced",
  "와이드 SVG가 폰에서 글자 깨지는 것 방지.",
  "라벨 있는 와이드 SVG.","“모바일에서 SVG 글자 안 깨지게”",["모바일SVG"],
  "@media(max-width:680px){.figure svg{min-width:640px}} + 가로스크롤.",
  "memory:pre-ship QA #2","svg{width:100%} 단독은 폰에서 ~5px로 깨짐."),

# ---------- components ----------
E("kpi-ribbon","KPI 리본","KPI ribbon","components","core",
  "핵심 수치 4개를 띠로. count-up·글로우 가능.",
  "임팩트 첫인상.","“핵심 수치 4개 리본으로”",["KPI","수치대시보드"],
  "grid 4칸 · 값(mono 큰글씨)+라벨. 약하면 빼고 교체.",
  "html Agent:resume-design-system · memory"),
E("metric-card","메트릭 카드","Metric card","components","core",
  "라벨(작게)+숫자(24/500) 요약 카드.",
  "요약 수치.","“메트릭 카드로”",["수치카드"],
  "bg-secondary·radius·label 13px + value 24px.","Claude Design(visualize)"),
E("ghost-number","고스트 큰 숫자","Ghost big number","components","advanced",
  "배경에 큰 반투명 숫자로 단조로움 회피.",
  "섹션 장식·시선.","“배경에 큰 숫자 깔아”",["고스트숫자"],
  "position absolute·낮은 opacity·큰 폰트.","html Agent:resume-design-system"),
E("glossary-box","약어 풀이 박스","Glossary box","components","core",
  "업계 약어를 비전문가용으로 병기.",
  "채용·외부 공개.","“약어 풀어서 병기해”",["용어풀이"],
  "용어+1줄 설명 박스.","memory:pre-ship QA #4"),
E("reveal-once","스크롤 1회 등장","Reveal on scroll","motion-interaction","core",
  "뷰포트 진입 시 1회 페이드업(무한 아님).",
  "섹션 등장.","“스크롤하면 한번 떠오르게”",["reveal","페이드업"],
  "IntersectionObserver→add .in 1회. no-JS시 기본 표시(.js 게이트).",
  "docs/sub-brain-portfolio.html","no-JS 안전 가드 필수."),
E("count-up","숫자 카운트업","Count-up","motion-interaction","core",
  "0→실값으로 1회 증가(easeOut).",
  "KPI 강조.","“숫자 카운트업”",["카운트업","숫자애니"],
  "rAF로 easeOutCubic, toLocaleString 포맷.",
  "docs/sub-brain-portfolio.html","반올림·콤마 포맷, reduced-motion시 즉시 최종값."),
E("staggered-reveal","순차 등장","Staggered reveal","motion-interaction","core",
  "카드들이 delay 두고 차례로 등장.",
  "카드 묶음.","“카드 순차로 떠오르게”",["stagger"],
  "nth-child transition-delay 단계 증가.","docs/sub-brain-portfolio.html",
  "","<div class='demo-stagger'><span></span><span></span><span></span><span></span></div>"),
E("draw-on","SVG 그려지기","SVG draw-on","motion-interaction","advanced",
  "선이 그려진 뒤 멈춤(1회).",
  "그래프/다이어그램 등장.","“선이 그려지게”",["draw-on","dashoffset"],
  "stroke-dasharray=len; dashoffset len→0 transition.",
  "docs/sub-brain-portfolio.html"),
E("infinite-replay","무한 리플레이","Infinite replay","motion-interaction","advanced",
  "들어오면 재생·나가면 리셋 → 스크롤마다 재생.",
  "반복 강조 데모.","“스크롤마다 다시 재생되게”",["리플레이"],
  "IO add/remove .active; 강제 리플로우 void el.offsetWidth.",
  "html Agent:premium-interaction-design","산만 주의·채용 포폴엔 절제."),
E("pointer-parallax","포인터 패럴랙스","Pointer parallax","motion-interaction","advanced",
  "마우스 따라 레이어가 깊이차로 이동.",
  "히어로 입체감.","“마우스 따라 입체감 주게”",["패럴랙스","depth"],
  "pointermove→layer.translate(nx*depth). leave시 리셋.",
  "docs/sub-brain-portfolio.html","reduced-motion시 비활성."),
E("staggered-rotate","스태거 카드 회전","Staggered card tilt","motion-interaction","advanced",
  "홀짝 카드를 ±기울여 생동감, hover시 정렬.",
  "갤러리 카드.","“카드 살짝 기울여줘”",["카드틸트"],
  "nth-child rotate(±1.5deg)+scale, ease cubic-bezier(.34,1.56,.64,1).",
  "html Agent:premium-interaction-design","",
  "<div class='demo-tilt'><span>1</span><span>2</span><span>3</span></div>"),
E("hover-lift","호버 마이크로리프트","Hover micro-lift","motion-interaction","core",
  "hover시 살짝 떠오르고 보더 강조.",
  "카드·버튼.","“hover에 살짝 뜨게”",["호버","lift"],
  "transition transform .18s; hover translateY(-2px)+border accent.",
  "전 페이지","","<div class='demo-lift'>hover me</div>"),
E("reduced-motion","모션 줄이기 가드","Reduced-motion guard","motion-interaction","principle",
  "OS '모션 줄이기'면 애니 정지.",
  "모든 애니.","“모션 접근성 지켜”",["reduced-motion"],
  "@media(prefers-reduced-motion:reduce){animation:none!important}","docs/* · Claude Design"),
E("no-infinite-default","무한모션 기본 금지","No infinite by default","motion-interaction","principle",
  "산만한 무한/키네틱 타이포 지양, 브랜드 모티프 한정 허용.",
  "톤 판단.","“무한 애니는 빼고”",["키네틱금지"],
  "1회성 마이크로모션 기본 · 무한은 히어로 모티프만.",
  "html Agent CLAUDE.md · memory"),

# ---------- svg-canvas ----------
E("inline-svg-fig","인라인 SVG 도식","Inline SVG figure","svg-canvas","core",
  "데이터를 인라인 SVG 도형으로(self-contained).",
  "다이어그램·도식.","“인라인 SVG로 도식 그려”",["SVG도식"],
  "<svg viewBox role=img><title><desc>…","Claude Design · bespoke"),
E("pixel-frame","픽셀퍼펙트 프레임","Pixel-perfect frame","svg-canvas","advanced",
  "물리 border 대신 inset box-shadow로 수축 없는 테두리.",
  "정밀 프레임.","“테두리 정확히(수축없이)”",["inset프레임"],
  "box-shadow: inset 0 0 0 1px","html Agent:premium-interaction-design","",
  "<div class='demo-frame'>frame</div>"),
E("marquee-border","마퀴 보더","Marquee border","svg-canvas","advanced",
  "pathLength로 리사이즈 무관 흐르는 테두리.",
  "강조 카드.","“테두리 흐르게”",["마퀴테두리"],
  "pathLength='100' + stroke-dasharray 애니.","html Agent:premium-interaction-design"),
E("polar-layout","극좌표 노드 배치","Polar node layout","svg-canvas","advanced",
  "원형으로 노드 균등 배치.",
  "방사형 그래프.","“노드 원형으로 배치”",["극좌표","radial"],
  "x=cx+R·cosθ, y=cy+R·sinθ; translate(-50%,-50%).",
  "html Agent:premium-interaction-design"),
E("canvas-streaks","캔버스 입자 스트릭","Canvas particle streaks","svg-canvas","advanced",
  "코어에서 바깥으로 나선 스트릭(속도감).",
  "임팩트 히어로/그래프.","“별무리 스쳐가는 속도감”",["입자","스트릭","cosmos"],
  "rAF: ang+=w; rad+=vr; arc streak; 경계 넘으면 재생성.",
  "docs/sub-brain-portfolio.html","reduced-motion 정지프레임."),
E("wireframe-orb","와이어프레임 회전 구","Spinning wireframe orb","svg-canvas","advanced",
  "경선 타원 회전으로 도는 코어.",
  "중심 모티프.","“중앙이 도는 구처럼”",["회전구","orb"],
  "ellipse rx=|cos(phase)|·r 회전 + 평행선.","docs/sub-brain-portfolio.html"),
E("smil-flow","SMIL 모션 흐름","SMIL animateMotion","svg-canvas","advanced",
  "경로 따라 입자 흐름(JS 없이).",
  "연결 흐름 표현.","“선 따라 흐르게”",["SMIL","animateMotion"],
  "<animateMotion><mpath href=#path>","docs/sub-brain-portfolio.html"),
E("static-snapshot","정적 스냅샷 원칙","Static snapshot","svg-canvas","principle",
  "민감/내부 데이터는 인터랙티브 대신 정적 표현.",
  "공개 그래프.","“그래프는 정적으로(인터랙티브 X)”",["정적그래프"],
  "추상화 라벨 + 별빛=밀도 표현 명시.","docs/sub-brain-portfolio.html"),
E("favicon-datauri","빈 favicon","Empty favicon","svg-canvas","core",
  "콘솔 404 방지용 data:/SVG favicon.",
  "단일 파일.","“favicon 콘솔 깨끗하게”",["favicon"],
  "<link rel=icon href='data:,'> 또는 svg.","premium-interaction-design · this session"),

# ---------- data-viz ----------
E("knowledge-graph","지식 그래프 군집","Knowledge graph clusters","data-viz","advanced",
  "노드·엣지·커뮤니티로 지식 구조 시각화.",
  "지식/관계 표현.","“지식 그래프로 보여줘”",["그래프","노드맵"],
  "커뮤니티 허브 노드 + 링크 + 중심 SSOT.","graphify-out · docs/sub-brain-portfolio.html",
  "민감 라벨 추상화."),
E("chartjs-d3","차트(Chart.js/D3)","Charts","data-viz","advanced",
  "막대/선/choropleth 등 표준 차트.",
  "수치 데이터.","“차트로 그려”",["차트","chart.js"],
  "CDN allowlist(cdnjs/jsdelivr) 로드 후 렌더.","Claude Design(data_viz)"),
E("illustrative-density","표현적 밀도(정직)","Illustrative density","data-viz","principle",
  "장식 요소는 '표현'이라 명시, 실측만 라벨.",
  "별/입자 등 장식.","“별빛은 밀도 표현이라 표기해”",["정직표현"],
  "실측=수치+출처, 장식=표현 명시.","docs/sub-brain-portfolio.html"),

# ---------- media-embed ----------
E("base64-inline","base64 자산 인라인","Base64 inline asset","media-embed","core",
  "로컬 이미지를 리사이즈·base64로 단일파일에 내장.",
  "self-contained.","“이미지 파일에 내장해”",["base64","임베드"],
  "embed_media.py: img→리사이즈→data:URI.","bookemon-returns/embed_media.py"),
E("spa-bundler","대용량 SPA 번들러","Large SPA bundler","media-embed","advanced",
  "base64+DecompressionStream 런타임 디컴프레션.",
  "영상/대용량 단일파일.","“대용량도 단일파일로”",["번들러","압축임베드"],
  "gzip base64 → DecompressionStream → blob.","html Agent:large-spa-bundler"),
E("video-host","영상 임베드 vs 자체호스팅","Video hosting","media-embed","core",
  "유튜브 임베드(권장) vs ≤100MB mp4 자체호스팅.",
  "데모 영상.","“데모 영상 넣어”",["영상","데모"],
  "GitHub 100MB/파일 한계 → 길면 임베드.","DEPLOY.md · this session",
  "Pages는 LFS 영상 서빙 못함."),
E("poster-fallback","영상 포스터 폴백","Video poster","media-embed","core",
  "자동재생 금지·포스터 이미지·캡션.",
  "<video> 삽입.","“영상에 포스터·캡션”",["poster"],
  "<video poster controls> + 캡션.","this session"),

# ---------- accessibility ----------
E("alt-caption","alt·캡션 필수","Alt & caption","accessibility","core",
  "모든 이미지에 대체텍스트+캡션.",
  "이미지 삽입.","“이미지 alt 넣어”",["alt","대체텍스트"],
  "<img alt=…> + <figcaption>.","Claude Design · PORTFOLIO-INTAKE"),
E("contrast-aa","대비 AA","Contrast AA","accessibility","principle",
  "텍스트 대비 WCAG AA 충족.",
  "색 결정.","“대비 AA 맞춰”",["대비","WCAG"],
  "본문 4.5:1 / 큰글씨 3:1 이상.","Claude Design(a11y)"),
E("focus-ring","키보드 포커스 링","Focus ring","accessibility","core",
  "키보드 탐색용 가시 포커스.",
  "버튼·링크·입력.","“포커스 링 보이게”",["포커스"],
  "box-shadow 0 0 0 Npx focus.","Claude Design"),
E("aria-icon-btn","아이콘 버튼 aria","Icon button aria","accessibility","core",
  "아이콘만 있는 버튼에 aria-label.",
  "토글·아이콘 버튼.","“아이콘 버튼 라벨 달아”",["aria"],
  "<button aria-label='테마 전환'>","Claude Design · this session"),
E("sr-summary","스크린리더 요약","SR-only summary","accessibility","core",
  "시각화 앞에 숨김 한줄 요약.",
  "복잡 시각물.","“스크린리더 요약 넣어”",["sr-only"],
  "<h2 class=sr-only> 또는 svg role=img title/desc.","Claude Design"),
E("min-font-11","최소 폰트 11px","Min font 11px","accessibility","principle",
  "11px 미만 금지.",
  "작은 라벨.","“글자 너무 작지 않게”",["최소폰트"],
  "font-size ≥ 11px.","Claude Design"),

# ---------- honesty-provenance ----------
E("evidence-label","근거 라벨","Evidence label","honesty-provenance","core",
  "지표마다 [실측|추정|측정전|mock] 태그.",
  "모든 지표.","“수치에 근거 라벨 붙여”",["근거라벨","실측태그"],
  "값 옆 작은 태그. 라벨 없는 수치 게시 안함.","PORTFOLIO-INTAKE.md"),
E("unbenchmarked","미벤치 라벨","Unbenchmarked label","honesty-provenance","core",
  "측정 안 한 성능은 '미벤치' 명기.",
  "sub-second류 주장.","“미측정이면 미벤치 표기”",["미벤치"],
  "‘sub-second(미벤치)’.","starlink-returns"),
E("disabled-link","미제공 링크=비활성","Disabled placeholder link","honesty-provenance","core",
  "없는 데모/깃허브 링크는 '준비중' 비활성.",
  "링크 미정.","“링크 없으면 준비중 처리”",["placeholder링크"],
  "disabled + {{placeholder}}.","starlink-returns"),
E("verbatim-number","수치 verbatim","No rounding","honesty-provenance","principle",
  "반올림·파생 금지, 출처 그대로.",
  "수치 표기.","“수치 반올림하지 마”",["verbatim"],
  "357,840을 358K로 쓰지 않음.","bookemon-memory(드리프트 교훈)"),
E("meta-sync","헤드↔메타 동기화","Title/meta/OG sync","honesty-provenance","core",
  "헤드라인 바뀌면 title·description·OG 같이.",
  "카피 변경 후.","“메타도 같이 갱신해”",["메타동기화"],
  "변경 체크리스트 1번.","memory:pre-ship QA #1","stale 메타=재발 1위 버그."),

# ---------- performance-selfcontained ----------
E("single-file","단일 파일 self-contained","Single-file","performance-selfcontained","core",
  "CSS·JS·자산을 한 HTML에.",
  "공유·배포 용이.","“단일 파일로 만들어”",["self-contained","단일파일"],
  "인라인 style/script + data:URI.","전 페이지"),
E("fonts-only-cdn","폰트만 외부의존","Google Fonts only","performance-selfcontained","core",
  "외부 의존을 Google Fonts로 한정.",
  "self-contained 기준.","“외부 의존 폰트만”",["폰트CDN"],
  "fonts.googleapis/gstatic만.","Claude Design · this session"),
E("font-self-host","폰트 셀프호스트","Font self-host","performance-selfcontained","advanced",
  "woff2 내장으로 오프라인·속도·완전 self-contained.",
  "완전 오프라인.","“폰트도 내장해”",["woff2","셀프호스트"],
  "@font-face local woff2(base64).","DEPLOY.md"),
E("nojs-safe","no-JS 안전","No-JS safe","performance-selfcontained","core",
  "스크립트 차단돼도 콘텐츠 보임.",
  "reveal/애니 있을 때.","“JS 꺼져도 보이게”",["no-js"],
  ".reveal 기본 표시, .js 게이트로만 숨김.","this session"),
E("print-safe","인쇄 안전","Print safe","performance-selfcontained","core",
  "@media print에서 색·레이아웃 정리.",
  "PDF 출력 대비.","“인쇄해도 깨끗하게”",["print","인쇄"],
  "@media print{흰배경·애니off}.","bespoke · resume-design-system"),

# ---------- publishing-governance ----------
E("clean-room","타사자산 clean-room","Clean-room assets","publishing-governance","advanced",
  "타사 상표·로고·코드 직접 사용 금지.",
  "케이스스터디.","“타사 자산 clean-room으로”",["clean-room","IP"],
  "per-project allow + 회사명 차단.","PORTFOLIO-INTAKE.md"),
E("og-meta","OG 소셜 메타","OG meta","publishing-governance","core",
  "공유 썸네일·title·description.",
  "공개 페이지.","“OG 이미지·메타 넣어”",["og","소셜미리보기"],
  "og:title/description/image + twitter:card.","this session"),

# ---------- design-principles (Claude Design) ----------
E("flat-no-gradient","플랫(그라데이션 X)","Flat, no gradient","design-principles","principle",
  "그라데이션·그림자·노이즈 없이 클린 면.",
  "위젯·UI.","“플랫하게(그라데이션 빼)”",["플랫","flat"],
  "solid flat fill.","Claude Design"),
E("compact-inline","간결·핵심만","Compact essential","design-principles","principle",
  "핵심만 인라인, 설명은 본문 텍스트로.",
  "시각물 구성.","“핵심만 간결하게”",["compact"],
  "박스 부제 ≤5단어.","Claude Design"),
E("sentence-case","문장형 대소문자","Sentence case","design-principles","principle",
  "Title Case·ALL CAPS 금지, 문장형.",
  "라벨·제목.","“sentence case로”",["대소문자"],
  "‘핵심 역량’ not ‘핵심 역량(Title)’.","Claude Design"),
E("two-weights","두 굵기만","Two weights only","design-principles","principle",
  "400/500만(600·700 지양).",
  "타이포 위계.","“굵기 두 단계만”",["font-weight"],
  "regular 400 / medium 500.","Claude Design"),
E("color-meaning","색=의미","Color encodes meaning","design-principles","principle",
  "무지개 순환 금지, 카테고리별 1색.",
  "다색 사용.","“색은 의미대로(무지개 X)”",["색의미"],
  "동일 유형=동일 색, 2~3색.","Claude Design"),
E("complexity-budget","복잡도 예산","Complexity budget","design-principles","principle",
  "부제 ≤5단어, 색 ≤2램프, 한 행 ≤4박스.",
  "다이어그램.","“복잡도 예산 지켜”",["복잡도"],
  "초과면 분할/축약.","Claude Design"),
E("color-ramp-9","9색 램프 + 텍스트 800","9 color ramps","design-principles","advanced",
  "c-blue 등 9램프, 색 위 텍스트는 같은 계열 800/900.",
  "컬러 노드.","“램프 색에 텍스트는 진한 같은계열로”",["램프","color ramp"],
  "fill 50/stroke 600/text 800.","Claude Design"),
E("construction-set","라이브 트윅 노출","Construction-set tweak","design-principles","principle",
  "조절 가능한 노브를 화면에 보이게.",
  "탐색형 데모.","“라이브로 조절되게”",["트윅","slider"],
  "slider/toggle 노출.","portfolio-design-spec §8"),
E("art-from-constraints","제약→아트디렉션","Constraint art direction","design-principles","principle",
  "소수 강한 제약이 강한 디자인을 만든다.",
  "톤 결정.","“제약을 강하게 줘서 통일감”",["아트디렉션"],
  "고정 px·mono·무텍스트 등.","portfolio-design-spec §8"),

# ---------- workflow-skills ----------
E("lint-gate","발행 린트(드리프트·하드코딩색)","Publish lint","workflow-skills","core",
  "토큰 드리프트·하드코딩 컬러 게이트.",
  "html-publish 산출.","“린트 돌려(색 하드코딩 잡게)”",["lint","드리프트"],
  "lint.py: drift + hardcoded-color.","skills/html-publish/lint.py"),
E("design-md-stitch","DESIGN.md(Stitch) 디자인 계약","DESIGN.md format","workflow-skills","principle",
  "디자인 시스템을 마크다운 9섹션으로 적어 에이전트가 읽게(그림이 아닌 계약).",
  "톤 재현·디자인 핸드오프.","“DESIGN.md로 톤 계약 만들어”",["design.md","stitch","디자인계약"],
  "9섹션: 테마·색역할·타입표·컴포넌트·레이아웃·깊이·Do/Don't·반응형·에이전트프롬프트.",
  "awesome-design-md(MIT) · wiki/learnings/techniques/awesome-design-md-teardown"),
E("site-design-systems","실사이트 디자인 시스템 55","Real site systems","design-principles","advanced",
  "Claude·Stripe·Linear 등 55개 실사이트의 실토큰 디자인 시스템(프로 레퍼런스).",
  "프로 톤 차용·벤치마크.","“Stripe/Linear/Claude 톤으로”",["레퍼런스","site preset","실토큰"],
  "각 DESIGN.md=실hex·폰트·shadow 철학. design-presets에 3종 라이브 + verify 기준.",
  "awesome-design-md(MIT) · docs/design-presets.html"),
E("scroll-pin","스크롤 핀(시네마)","Scroll-pin cinema","motion-interaction","advanced",
  "헤드라인을 sticky로 고정한 채 하위 항목이 스크롤로 차례 공개(애플식 스토리텔링).",
  "프리미엄 스크롤 서사·제품 출시.","“스크롤 핀(고정 헤드 + 순차 공개)”",["scroll-pin","sticky","스크롤시네마","애플식"],
  "inner position:sticky;top:nav + 형제 reel을 IO reveal. reduced-motion 안전.",
  "apple-design-teardown · _tpl-apple-product.html","무한 아님(1회 공개)·키보드/no-JS 안전 확인."),
E("apple-grammar","Apple 그래머(한 화면 한 메시지)","Apple grammar","design-principles","principle",
  "풀블리드 비주얼 + 거대 선언 1개 + 여백 + 대형 수치(각주 보증) + 라이트/다크 교차.",
  "제품/포트폴리오 출시형 페이지.","“애플 문법으로 — 한 화면 한 메시지·여백·각주 수치”",["apple","한화면한메시지","여백","각주수치"],
  "한 뷰포트=메시지 1 · 헤드=본문 3~5× · 색은 작업물에만 · 모든 수치에 각주.",
  "apple-design-teardown.md","Vignelli/MB 절제와 동일 뿌리. 각주=evidence-label 정직성."),
]

def main():
    # gate: source on every entry + valid category
    bad = [e["id"] for e in ENTRIES if not e.get("src")]
    badcat = [e["id"] for e in ENTRIES if e["cat"] not in CATS]
    ids = [e["id"] for e in ENTRIES]
    dups = sorted({i for i in ids if ids.count(i) > 1})
    assert not bad, f"src 누락: {bad}"
    assert not badcat, f"카테고리 오류: {badcat}"
    assert not dups, f"중복 id: {dups}"
    cover = sorted({e["cat"] for e in ENTRIES})
    OUT_JSON.write_text(json.dumps(ENTRIES, ensure_ascii=False, indent=1), encoding="utf-8")
    html = HTML.replace("/*DATA*/", json.dumps(ENTRIES, ensure_ascii=False))
    OUT_HTML.write_text(html, encoding="utf-8")
    print(f"entries={len(ENTRIES)} cats={len(cover)}/{len(CATS)} dup={len(dups)} src_missing={len(bad)}")
    miss = [c for c in CATS if c not in cover]
    print("missing cats:", miss or "none")

HTML = r"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<script>(function(){var k='dc-theme',r=document.documentElement,s=localStorage.getItem(k);
if(s)r.setAttribute('data-theme',s);else if(matchMedia('(prefers-color-scheme:dark)').matches)r.setAttribute('data-theme','dark');
window.toggleTheme=function(){var d=r.getAttribute('data-theme')==='dark'?'light':'dark';r.setAttribute('data-theme',d);localStorage.setItem(k,d);};})();</script>
<title>HTML·디자인 기술 카탈로그 — 지시·피드백 어휘집</title>
<link href="https://fonts.googleapis.com/css2?family=Noto+Serif+KR:wght@600;700&family=IBM+Plex+Sans+KR:wght@400;500;600&display=swap" rel="stylesheet">
<style>
:root{--bg:#faf7f1;--card:#fff;--ink:#1a1814;--muted:#7a6e5e;--rule:rgba(26,24,20,.14);--accent:#7a1f2d;
--soft:color-mix(in oklab,var(--accent) 10%,transparent);
--fd:'Noto Serif KR',serif;--fb:'IBM Plex Sans KR',-apple-system,sans-serif;--fm:ui-monospace,Menlo,monospace;}
[data-theme=dark]{--bg:#14110d;--card:#1c1814;--ink:#f0ebe2;--muted:#a99f8e;--rule:rgba(240,235,226,.15);--accent:#d4566a;--soft:color-mix(in oklab,var(--accent) 18%,transparent);}
*{box-sizing:border-box;margin:0;padding:0;}
body{background:var(--bg);color:var(--ink);font-family:var(--fb);line-height:1.6;word-break:keep-all;-webkit-font-smoothing:antialiased;padding:0 20px 80px;transition:background .3s,color .3s;}
.wrap{max-width:1080px;margin:0 auto;}
a{color:inherit;}
.bar{display:flex;justify-content:space-between;align-items:center;padding:20px 0;}
.brand{font-family:var(--fd);font-weight:700;}.brand .d{color:var(--accent);}
.tgl{background:none;border:1px solid var(--rule);border-radius:9999px;width:36px;height:36px;cursor:pointer;color:var(--ink);}
.tgl:hover{border-color:var(--accent);}
header.h{padding:18px 0 26px;border-bottom:1px solid var(--rule);}
h1{font-family:var(--fd);font-size:clamp(28px,4.5vw,42px);font-weight:700;letter-spacing:-.02em;margin-bottom:10px;}
.lede{color:var(--muted);font-size:15px;max-width:680px;}
.controls{position:sticky;top:0;background:var(--bg);padding:16px 0;z-index:5;border-bottom:1px solid var(--rule);}
#q{width:100%;padding:11px 14px;border:1px solid var(--rule);border-radius:10px;background:var(--card);color:var(--ink);font-family:var(--fb);font-size:14px;}
.chips{display:flex;flex-wrap:wrap;gap:6px;margin-top:10px;}
.chip{font-family:var(--fm);font-size:11.5px;border:1px solid var(--rule);border-radius:9999px;padding:5px 11px;cursor:pointer;background:var(--card);color:var(--muted);}
.chip.on{background:var(--accent);color:#fff;border-color:var(--accent);}
.count{color:var(--muted);font-size:12px;font-family:var(--fm);margin:14px 0;}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(330px,1fr));gap:14px;}
.card{background:var(--card);border:1px solid var(--rule);border-radius:12px;padding:18px 18px;}
.card .top{display:flex;align-items:baseline;gap:8px;flex-wrap:wrap;}
.card h3{font-family:var(--fd);font-size:17px;font-weight:700;}
.card .en{color:var(--muted);font-size:12px;font-family:var(--fm);}
.badges{display:flex;gap:6px;margin:8px 0 10px;flex-wrap:wrap;}
.b{font-family:var(--fm);font-size:10.5px;padding:2px 8px;border-radius:6px;background:var(--soft);color:var(--accent);}
.b.tier{background:transparent;border:1px solid var(--rule);color:var(--muted);}
.what{font-size:13.5px;margin-bottom:8px;}
.when{font-size:12.5px;color:var(--muted);margin-bottom:10px;}
.instr{font-size:12.5px;background:var(--soft);border-left:2px solid var(--accent);padding:7px 10px;border-radius:0 8px 8px 0;margin-bottom:8px;}
.instr b{color:var(--accent);}
.alias{font-family:var(--fm);font-size:11px;color:var(--muted);margin-bottom:10px;}
.pat{position:relative;background:color-mix(in oklab,var(--ink) 6%,transparent);border-radius:8px;padding:10px 12px;font-family:var(--fm);font-size:11.5px;white-space:pre-wrap;word-break:break-word;margin-bottom:8px;}
.cp{position:absolute;top:6px;right:6px;font-size:10px;font-family:var(--fm);border:1px solid var(--rule);border-radius:6px;padding:2px 7px;cursor:pointer;background:var(--card);color:var(--muted);}
.qa{font-size:11.5px;color:var(--muted);border-top:1px dashed var(--rule);padding-top:8px;margin-top:6px;}
.qa::before{content:'⚠ ';color:var(--accent);}
.src{font-family:var(--fm);font-size:10.5px;color:var(--muted);margin-top:8px;}
.demo{margin:10px 0;padding:12px;border:1px dashed var(--rule);border-radius:8px;}
/* demo helpers */
.sw{display:inline-block;width:26px;height:26px;border-radius:6px;margin-right:5px;border:1px solid var(--rule);vertical-align:middle;}
.demo-keep{display:flex;gap:14px;font-size:11px;color:var(--muted);}
.demo-keep p{color:var(--ink);font-size:13px;border:1px solid var(--rule);padding:6px;border-radius:6px;}
.demo-lift{display:inline-block;padding:10px 16px;border:1px solid var(--rule);border-radius:8px;transition:transform .18s,border-color .18s;cursor:default;}
.demo-lift:hover{transform:translateY(-3px);border-color:var(--accent);}
.demo-stagger span{display:inline-block;width:34px;height:34px;margin-right:6px;border-radius:7px;background:var(--soft);animation:dcs 2.4s ease-in-out infinite;}
.demo-stagger span:nth-child(2){animation-delay:.2s}.demo-stagger span:nth-child(3){animation-delay:.4s}.demo-stagger span:nth-child(4){animation-delay:.6s}
@keyframes dcs{0%,60%,100%{opacity:.3;transform:translateY(6px)}30%{opacity:1;transform:none}}
.demo-tilt{display:flex;gap:8px}
.demo-tilt span{width:40px;height:52px;border:1px solid var(--rule);border-radius:8px;display:flex;align-items:center;justify-content:center;font-family:var(--fm);transition:transform .2s}
.demo-tilt span:nth-child(odd){transform:rotate(-3deg)}.demo-tilt span:nth-child(even){transform:rotate(3deg)}
.demo-tilt:hover span{transform:none}
.demo-frame{display:inline-block;padding:12px 18px;border-radius:8px;box-shadow:inset 0 0 0 1px var(--accent);font-family:var(--fm);font-size:12px}
@media(prefers-reduced-motion:reduce){.demo-stagger span{animation:none;opacity:1;transform:none}}
footer{margin-top:50px;padding-top:20px;border-top:1px solid var(--rule);color:var(--muted);font-size:12px;}
</style>
</head>
<body>
<div class="wrap">
  <div class="bar"><span class="brand">Vibe Design Studio<span class="d"> · 카탈로그</span></span>
    <span style="display:flex;gap:14px;align-items:center;font-size:13px;"><a href="design-studio.html">스튜디오</a><a href="design-presets.html">프리셋</a><a href="design-effects.html">효과</a><a href="design-systems.html">시스템</a><a href="design-references.html">레퍼런스</a>
    <a href="https://github.com/ljhljh0703-cmd/VDS" target="_blank" rel="noopener" style="border:1px solid currentColor;border-radius:999px;padding:3px 11px;font-weight:700;text-decoration:none;white-space:nowrap">GitHub ↗</a>
    <button class="tgl" onclick="toggleTheme()" aria-label="라이트/다크 전환">◐</button></span></div>
  <header class="h">
    <h1>HTML·디자인 기술 카탈로그</h1>
    <p class="lede">지시·피드백용 공유 어휘집. 각 항목의 <b>“이렇게 지시”</b> 문구·별칭으로 콕 집어 말하면 정확히 전달됩니다. 출처 = Claude Design + LLM wiki. 항목마다 출처 표기.</p>
  </header>
  <div class="controls">
    <input id="q" type="search" placeholder="검색 — 이름·설명·별칭·지시예문 (예: 카운트업, 다크, 출처, parallax)">
    <div class="chips" id="cats"></div>
    <div class="chips" id="tiers"></div>
  </div>
  <div class="count" id="count"></div>
  <div class="grid" id="grid"></div>
  <footer>HTML·디자인 기법 77종 · 지시·피드백 어휘집. © 2026 이주형 · Vibe Design Studio.</footer>
</div>
<script>
const DATA=/*DATA*/;
const CATLABEL={ "tokens-theme":"토큰·테마","layout-responsive":"레이아웃·반응형","typography-kr":"타이포(한글)","components":"컴포넌트","motion-interaction":"모션·인터랙션","svg-canvas":"SVG·캔버스","data-viz":"데이터 시각화","media-embed":"미디어 임베드","accessibility":"접근성","honesty-provenance":"정직성·출처","performance-selfcontained":"성능·self-contained","publishing-governance":"발행·거버넌스","design-principles":"디자인 원칙","workflow-skills":"워크플로·스킬"};
let fCat="", fTier="", fQ="";
const cats=[...new Set(DATA.map(e=>e.cat))];
const tiers=["core","advanced","principle"];
const esc=s=>(s||"").replace(/[&<>]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;"}[c]));
function chip(t,label,on,cls){return `<span class="chip ${cls} ${on?'on':''}" data-v="${t}">${label}</span>`;}
function renderChips(){
  document.getElementById("cats").innerHTML=chip("","전체 분류",fCat==="","c")+cats.map(c=>chip(c,CATLABEL[c]||c,fCat===c,"c")).join("");
  document.getElementById("tiers").innerHTML=chip("","전체 tier",fTier==="","t")+tiers.map(t=>chip(t,t,fTier===t,"t")).join("");
}
function match(e){
  if(fCat&&e.cat!==fCat)return false;
  if(fTier&&e.tier!==fTier)return false;
  if(fQ){const h=(e.ko+" "+e.en+" "+e.what+" "+e.when+" "+e.instr+" "+(e.alias||[]).join(" ")+" "+e.pattern+" "+e.src).toLowerCase();
    if(!h.includes(fQ.toLowerCase()))return false;}
  return true;
}
function card(e){
  return `<div class="card"><div class="top"><h3>${esc(e.ko)}</h3><span class="en">${esc(e.en)}</span></div>
  <div class="badges"><span class="b">${CATLABEL[e.cat]||e.cat}</span><span class="b tier">${e.tier}</span></div>
  <div class="what">${esc(e.what)}</div>
  <div class="when">언제 — ${esc(e.when)}</div>
  <div class="instr"><b>이렇게 지시</b> · ${esc(e.instr)}</div>
  ${(e.alias&&e.alias.length)?`<div class="alias">별칭: ${e.alias.map(esc).join(" · ")}</div>`:""}
  ${e.demo?`<div class="demo">${e.demo}</div>`:""}
  <div class="pat"><button class="cp" onclick="cp(this)">복사</button>${esc(e.pattern)}</div>
  ${e.qa?`<div class="qa">${esc(e.qa)}</div>`:""}
  <div class="src">출처 · ${esc(Array.isArray(e.src)?e.src.join(", "):e.src)}</div></div>`;
}
function render(){
  const list=DATA.filter(match);
  document.getElementById("count").textContent=`${list.length} / ${DATA.length} 항목`;
  document.getElementById("grid").innerHTML=list.map(card).join("")||"<p style='color:var(--muted)'>일치 없음</p>";
}
function cp(b){const t=b.parentNode.textContent.replace(/^복사/,"");navigator.clipboard&&navigator.clipboard.writeText(t.trim());b.textContent="✓";setTimeout(()=>b.textContent="복사",1200);}
document.getElementById("q").addEventListener("input",e=>{fQ=e.target.value;render();});
document.addEventListener("click",e=>{const c=e.target.closest(".chip");if(!c)return;
  if(c.parentNode.id==="cats")fCat=c.dataset.v;else if(c.parentNode.id==="tiers")fTier=c.dataset.v;renderChips();render();});
renderChips();render();
</script>
</body>
</html>"""

if __name__ == "__main__":
    main()
