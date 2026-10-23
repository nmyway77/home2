#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
retrofit_pen_v121.py — 펜 필기 모드 v1.0/v1.1/v1.2 → v1.2.1 (태블릿 강화 + 두 손가락 스크롤 + 탭 줄 통과 + #pendebug 진단) 후처리

v1.2.1 = 고1 2026-10(mogo1-2610) 12개에 먼저 적용됐던 v1.2 블록 + 두 가지 보강:
  · [버그 수정] html{scroll-behavior:smooth} 페이지에서 두 손가락 스크롤이 거의 안 되던 문제(scrollBy 애니메이션이 서로 취소) → 제스처 동안 즉시 스크롤
  · [진단 모드] 주소 끝에 #pendebug 를 붙여 열면 입력 이벤트 로그가 화면에 표시됨 (실기기 원인 확인용, 평소엔 비활성)
v1.2 내용:
  · Pointer Events 우선, 미지원 시 Touch Events 폴백 / touchstart·touchmove 비-passive preventDefault
  · 토글 시 inline touch-action:none · user-select:none / 툴바 visualViewport 추적 + safe-area
  · 팜 리젝션(스타일러스 직후 1.5초 손바닥 무시) · 단일 활성 pointerId
  · 두 손가락 끌기 = 페이지 스크롤, 한 손가락·펜 = 그리기 / 펜 모드 중 탭 줄(.view-tabs)·상단 메뉴·단어장 탭 클릭 통과
  · 진단: 주소 끝에 #pendebug 를 붙여 열면 입력 이벤트 로그가 화면에 표시됨 (실기기 원인 확인용, 평소엔 비활성)

사용: python3 retrofit_pen_v121.py <file.html>... [--check]
      이미 v1.2.1이면 건너뜀. 펜 블록(JS)과 #penToolbar CSS 1줄만 교체, 나머지는 1바이트도 건드리지 않음(멱등).
"""
import sys

OLD_CSS = "#penToolbar{position:fixed;bottom:20px;right:20px;"
NEW_CSS = "#penToolbar{position:fixed;bottom:calc(20px + env(safe-area-inset-bottom,0px));right:20px;"
HEADS_OLD = ["/* ══ 펜 필기 모드 (자유 필기) v1.0 ══ */", "/* ══ 펜 필기 모드 (자유 필기) v1.1 — 태블릿 강화 ══ */",
             "/* ══ 펜 필기 모드 (자유 필기) v1.2 — 태블릿 강화 + 두 손가락 스크롤 + 탭 줄 통과 ══ */",
             "/* ══ 펜 필기 모드 (자유 필기) v1.2 — 태블릿 강화 + 두 손가락 스크롤 + 탭 줄 통과 (+ #pendebug 진단) ══ */"]
HEAD_NEW = "/* ══ 펜 필기 모드 (자유 필기) v1.2.1"
JS_END = "  setTimeout(buildPenTools,100);\n}\n"
NEW_JS = r'''/* ══ 펜 필기 모드 (자유 필기) v1.2.1 — 태블릿 강화 + 두 손가락 스크롤 + 탭 줄 통과 + #pendebug 진단 ══ */
const PEN_COLORS=['#dc2626','#1F3864','#0f9d58','#f59e0b','#000000'];
const PEN_WIDTHS=[2,4,7];
let penEnabled=false,penColor='#dc2626',penWidth=4,penEraser=false;
let penLayer=null,penPath=null,penPts=[],penLastStylus=0,penActiveId=null;
/* v1.2: 두 손가락 스크롤 상태 · 펜 모드에서도 눌려야 하는 영역(탭 줄·상단 메뉴·단어장 탭) */
let penScroll=null,penDownAt=0,penScrollPrevBehavior='';
const PEN_PASS='.view-tabs,.top-nav,.vocab-tabs,#penToolbar';
function penPassTarget(x,y){
  if(!document.elementsFromPoint)return null;
  const els=document.elementsFromPoint(x,y);
  for(const el of els){if(el===penLayer||penLayer.contains(el))continue;return el.closest(PEN_PASS)?el:null;}
  return null;
}

/* 진단 모드: 주소 끝에 #pendebug 를 붙여 열면 화면 왼쪽 위에 입력 이벤트 로그가 표시됨 (레노버 태블릿 원인 확인용) */
const PEN_DEBUG=/pendebug/.test(location.hash);
let penDbgBox=null,penDbgN=0;
function penDbg(msg){
  if(!PEN_DEBUG)return;
  if(!penDbgBox){
    penDbgBox=document.createElement('pre');penDbgBox.id='penDebug';
    penDbgBox.style.cssText='position:fixed;top:4px;left:4px;z-index:100000;max-width:70vw;max-height:45vh;overflow:auto;background:rgba(0,0,0,0.78);color:#9f9;font:11px/1.35 monospace;padding:6px 8px;border-radius:6px;pointer-events:none;white-space:pre-wrap;margin:0;';
    document.body.appendChild(penDbgBox);
    penDbgBox.textContent='[pen debug] UA: '+navigator.userAgent+'\nPointerEvent: '+(!!window.PointerEvent)+' · touch: '+('ontouchstart' in window)+' · maxTouchPoints: '+(navigator.maxTouchPoints||0)+' · visualViewport: '+(!!window.visualViewport)+' · dpr: '+window.devicePixelRatio+'\n';
    window.addEventListener('error',e=>{penDbgBox.textContent+='JS ERROR: '+e.message+' @'+e.lineno+'\n';});
  }
  penDbgN++;
  if(penDbgN>60){penDbgBox.textContent=penDbgBox.textContent.split('\n').slice(0,3).join('\n')+'\n';penDbgN=0;}
  penDbgBox.textContent+=msg+'\n';
}
function penDbgEv(tag,e){
  if(!PEN_DEBUG)return;
  penDbg(tag+' '+(e.pointerType||'?')+' id='+e.pointerId+' btn='+e.buttons+' x='+Math.round(e.clientX)+' y='+Math.round(e.clientY)+' pressure='+(e.pressure!==undefined?e.pressure.toFixed(2):'-')+' tgt='+(e.target&&e.target.id||e.target&&e.target.tagName||'?')+' on='+penEnabled+' active='+penActiveId+' path='+(penPath?'Y':'N'));
}

function buildPenTools(){
  if(document.getElementById('penLayer'))return;
  penLayer=document.createElementNS('http://www.w3.org/2000/svg','svg');
  penLayer.id='penLayer';
  document.body.appendChild(penLayer);
  penDbg('buildPenTools: layer ok · body '+document.body.scrollWidth+'x'+document.body.scrollHeight);
  if(PEN_DEBUG){['pointerdown','pointerup','pointercancel','touchstart','touchend','touchcancel'].forEach(t=>document.addEventListener(t,e=>{penDbg('doc:'+t+' tgt='+(e.target&&(e.target.id||e.target.tagName))+(e.pointerType?' '+e.pointerType:'')+(e.touches?' touches='+e.touches.length:''));},true));}
  const tb=document.createElement('div');
  tb.id='penToolbar';
  let html='<button class="pen-btn pen-main" id="penToggle" title="펜 ON/OFF">✏️</button><div class="pen-tools" id="penTools">';
  PEN_COLORS.forEach(c=>html+='<button class="pen-color" data-color="'+c+'" style="background:'+c+';" title="색상"></button>');
  PEN_WIDTHS.forEach(w=>html+='<button class="pen-width" data-width="'+w+'" title="굵기"><span style="width:'+(w*2)+'px;height:'+(w*2)+'px;"></span></button>');
  html+='<button class="pen-btn pen-eraser" id="penEraserBtn" title="개별 지우개">🧹</button><button class="pen-btn pen-clear" id="penClearBtn" title="전체 지우기">🗑️</button></div>';
  tb.innerHTML=html;
  document.body.appendChild(tb);
  document.querySelector('.pen-color[data-color="'+penColor+'"]').classList.add('selected');
  document.querySelector('.pen-width[data-width="'+penWidth+'"]').classList.add('selected');
  document.getElementById('penToggle').addEventListener('click',togglePen);
  document.querySelectorAll('.pen-color').forEach(b=>b.addEventListener('click',e=>{
    const c=e.currentTarget.dataset.color;
    penColor=c;penEraser=false;
    document.querySelectorAll('.pen-color').forEach(x=>x.classList.toggle('selected',x.dataset.color===c));
    document.getElementById('penEraserBtn').classList.remove('active');
  }));
  document.querySelectorAll('.pen-width').forEach(b=>b.addEventListener('click',e=>{
    const w=+e.currentTarget.dataset.width;
    penWidth=w;
    document.querySelectorAll('.pen-width').forEach(x=>x.classList.toggle('selected',+x.dataset.width===w));
  }));
  document.getElementById('penEraserBtn').addEventListener('click',()=>{
    penEraser=!penEraser;
    document.getElementById('penEraserBtn').classList.toggle('active',penEraser);
  });
  document.getElementById('penClearBtn').addEventListener('click',()=>{
    if(confirm('모든 필기를 지우시겠습니까?'))penLayer.innerHTML='';
  });
  /* ── 입력: Pointer Events 우선, 미지원 시 Touch Events 폴백 (v1.1 ②) ── */
  if(window.PointerEvent){
    penLayer.addEventListener('pointerdown',penDown);
    penLayer.addEventListener('pointermove',penMove);
    penLayer.addEventListener('pointerup',penUp);
    penLayer.addEventListener('pointercancel',penUp);
    penLayer.addEventListener('pointerleave',penUp);
  }else{
    const T=(e,type)=>{const t=e.changedTouches&&e.changedTouches[0];if(!t)return null;
      return {clientX:t.clientX,clientY:t.clientY,pointerId:t.identifier,pointerType:'touch',buttons:type==='end'?0:1,preventDefault:()=>e.preventDefault()};};
    penLayer.addEventListener('touchstart',e=>{const p=T(e,'start');if(p)penDown(p);},{passive:false});
    penLayer.addEventListener('touchmove',e=>{const p=T(e,'move');if(p)penMove(p);},{passive:false});
    penLayer.addEventListener('touchend',e=>{const p=T(e,'end');if(p)penUp(p);},{passive:false});
    penLayer.addEventListener('touchcancel',e=>{const p=T(e,'end');if(p)penUp(p);},{passive:false});
    penLayer.addEventListener('mousedown',e=>penDown(Object.assign(e,{pointerId:1,pointerType:'mouse'})));
    penLayer.addEventListener('mousemove',e=>penMove(e));
    penLayer.addEventListener('mouseup',e=>penUp(e));
  }
  /* ── v1.1 ①: touch-action을 무시하는 브라우저에서 스크롤 가로채기 차단 ── */
  const blockScroll=e=>{if(penEnabled&&e.touches&&e.touches.length===1)e.preventDefault();};
  penLayer.addEventListener('touchstart',blockScroll,{passive:false});
  penLayer.addEventListener('touchmove',blockScroll,{passive:false});
  /* ── v1.2 ①: 두 손가락 = 페이지 스크롤 (한 손가락·펜 = 그리기) ── */
  const mid=e=>{const a=e.touches[0],b=e.touches[1];return {x:(a.clientX+b.clientX)/2,y:(a.clientY+b.clientY)/2};};
  penLayer.addEventListener('touchstart',e=>{
    if(!penEnabled||!e.touches||e.touches.length<2)return;
    e.preventDefault();
    /* 첫 손가락으로 막 시작된 짧은 선은 스크롤 의도로 보고 지움 */
    if(penPath&&Date.now()-penDownAt<400&&penPts.length<8){penPath.remove();}
    penPath=null;penPts=[];penActiveId=null;
    penScroll=mid(e);
    /* v1.2.1: html{scroll-behavior:smooth}이면 scrollBy가 애니메이션으로 서로 취소돼 스크롤이 안 됨 → 제스처 동안 즉시 스크롤 */
    penScrollPrevBehavior=document.documentElement.style.scrollBehavior;
    document.documentElement.style.scrollBehavior='auto';
  },{passive:false});
  penLayer.addEventListener('touchmove',e=>{
    if(!penScroll||!e.touches||e.touches.length<2)return;
    e.preventDefault();
    const m=mid(e);
    const dx=penScroll.x-m.x,dy=penScroll.y-m.y;
    penScroll=m;
    if(dx||dy){try{window.scrollBy({left:dx,top:dy,behavior:'instant'});}catch(_){window.scrollBy(dx,dy);}}
  },{passive:false});
  const endScroll=e=>{if(penScroll&&(!e.touches||e.touches.length<2)){penScroll=null;document.documentElement.style.scrollBehavior=penScrollPrevBehavior||'';}};
  penLayer.addEventListener('touchend',endScroll);
  penLayer.addEventListener('touchcancel',endScroll);
  const sync=()=>{
    penLayer.style.height='0px';penLayer.style.width='0px';
    const h=Math.max(document.body.scrollHeight,document.documentElement.scrollHeight);
    const w=Math.max(document.body.scrollWidth,document.documentElement.scrollWidth);
    penLayer.setAttribute('width',w);
    penLayer.setAttribute('height',h);
    penLayer.style.height=h+'px';
    penLayer.style.width=w+'px';
  };
  sync();
  if(window.ResizeObserver)new ResizeObserver(sync).observe(document.body);
  window.addEventListener('resize',sync);
  setInterval(sync,2000);
  /* ── v1.1 ④: 하단 주소창·키보드에 툴바가 가려지지 않게 visualViewport 추적 ── */
  const vv=window.visualViewport;
  if(vv){
    const place=()=>{
      const hidden=Math.max(0,window.innerHeight-(vv.offsetTop+vv.height));
      tb.style.bottom='calc('+(20+hidden)+'px + env(safe-area-inset-bottom,0px))';
      tb.style.right=Math.max(20,window.innerWidth-(vv.offsetLeft+vv.width)+20)+'px';
    };
    vv.addEventListener('resize',place);vv.addEventListener('scroll',place);place();
  }
}
function togglePen(){
  penEnabled=!penEnabled;
  penDbg('togglePen → '+penEnabled+' · layer '+penLayer.getAttribute('width')+'x'+penLayer.getAttribute('height')+' · touchAction='+getComputedStyle(penLayer).touchAction+' · pointerEvents='+getComputedStyle(penLayer).pointerEvents);
  document.getElementById('penToggle').classList.toggle('active',penEnabled);
  document.getElementById('penTools').classList.toggle('show',penEnabled);
  penLayer.classList.toggle('active',penEnabled);
  /* v1.1 ③: 클래스 CSS가 늦게 적용되거나 무시되는 환경 대비 inline 명시 */
  penLayer.style.touchAction=penEnabled?'none':'';
  penLayer.style.msTouchAction=penEnabled?'none':'';
  penLayer.style.webkitUserSelect=penEnabled?'none':'';
  penLayer.style.userSelect=penEnabled?'none':'';
  if(!penEnabled){penPath=null;penPts=[];penActiveId=null;}
}
function getPenPt(e){
  return {x:e.clientX+window.scrollX,y:e.clientY+window.scrollY};
}
function penIgnore(e){
  /* v1.1 ⑤⑥: 스타일러스 직후 손바닥 touch 무시 · 두 번째 손가락 무시 */
  if(e.pointerType==='pen')penLastStylus=Date.now();
  else if(e.pointerType==='touch'&&Date.now()-penLastStylus<1500)return true;
  if(penActiveId!==null&&e.pointerId!==undefined&&e.pointerId!==penActiveId)return true;
  return false;
}
function penDown(e){
  penDbgEv('down',e);
  if(!penEnabled)return;
  if(penScroll)return;
  /* v1.2 ②: 탭 줄·상단 메뉴 위에서는 그리지 않고 아래 버튼을 그대로 누른다 */
  const pass=penPassTarget(e.clientX,e.clientY);
  if(pass){
    e.preventDefault();
    penActiveId=null;
    try{if(pass.focus)pass.focus({preventScroll:true});}catch(_){}
    const target=pass.closest('button,a,[onclick],label,input,select')||pass;
    target.click();
    return;
  }
  if(penIgnore(e))return;
  e.preventDefault();
  penDownAt=Date.now();
  penActiveId=(e.pointerId===undefined?1:e.pointerId);
  try{penLayer.setPointerCapture(e.pointerId);}catch(_){}
  if(penEraser){eraseAt(e);return;}
  const pt=getPenPt(e);
  penPath=document.createElementNS('http://www.w3.org/2000/svg','path');
  penPath.setAttribute('d','M '+pt.x+' '+pt.y);
  penPath.setAttribute('stroke',penColor);
  penPath.setAttribute('stroke-width',penWidth);
  penPath.setAttribute('fill','none');
  penPath.setAttribute('stroke-linecap','round');
  penPath.setAttribute('stroke-linejoin','round');
  penLayer.appendChild(penPath);
  penPts=[pt];
}
function penMove(e){
  if(PEN_DEBUG&&(e.buttons||penPath)&&(penDbgN%8===0))penDbgEv('move',e);
  if(!penEnabled||penScroll)return;
  if(penActiveId!==null&&e.pointerId!==undefined&&e.pointerId!==penActiveId)return;
  if(penEraser&&e.buttons){eraseAt(e);return;}
  if(!penPath)return;
  e.preventDefault();
  const pt=getPenPt(e);
  const last=penPts[penPts.length-1];
  if(Math.hypot(pt.x-last.x,pt.y-last.y)<1.5)return;
  penPts.push(pt);
  let d='M '+penPts[0].x+' '+penPts[0].y;
  for(let i=1;i<penPts.length-1;i++){
    const c=penPts[i],n=penPts[i+1];
    const mx=(c.x+n.x)/2,my=(c.y+n.y)/2;
    d+=' Q '+c.x+' '+c.y+' '+mx+' '+my;
  }
  if(penPts.length>=2){
    const lp=penPts[penPts.length-1];
    d+=' L '+lp.x+' '+lp.y;
  }
  penPath.setAttribute('d',d);
}
function penUp(e){
  if(e&&e.type)penDbgEv(e.type==='pointercancel'?'CANCEL':(e.type==='pointerleave'?'leave':'up'),e);
  if(e&&penActiveId!==null&&e.pointerId!==undefined&&e.pointerId!==penActiveId)return;
  if(penPath){penPath=null;penPts=[];}
  penActiveId=null;
}
function eraseAt(e){
  const pt=getPenPt(e);
  const r=20;
  const paths=Array.from(penLayer.querySelectorAll('path'));
  for(const p of paths){
    const bb=p.getBBox();
    if(pt.x>=bb.x-r&&pt.x<=bb.x+bb.width+r&&pt.y>=bb.y-r&&pt.y<=bb.y+bb.height+r){
      p.remove();
    }
  }
}
if(document.readyState==='loading'){
  document.addEventListener('DOMContentLoaded',buildPenTools);
}else{
  setTimeout(buildPenTools,100);
}
'''

def apply(path, check=False):
    s = open(path, encoding='utf-8').read()
    if HEAD_NEW in s:
        return 'skip(v1.2.1)'
    i = -1
    for h in HEADS_OLD:
        i = s.find(h)
        if i >= 0: break
    if i < 0:
        return '불가(펜 블록 없음)'
    j = s.find(JS_END, i)
    if j < 0:
        return '불가(블록 끝 미발견)'
    j += len(JS_END)
    if OLD_CSS not in s and NEW_CSS not in s:
        return '불가(CSS 미발견)'
    if check:
        return 'ok'
    s2 = s[:i] + NEW_JS + s[j:]
    s2 = s2.replace(OLD_CSS, NEW_CSS, 1)
    open(path, 'w', encoding='utf-8').write(s2)
    return 'applied'

if __name__ == '__main__':
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    check = '--check' in sys.argv
    for p in args:
        print(f'{apply(p, check):>16}  {p}')
