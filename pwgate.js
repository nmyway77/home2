// 재원생 전용 잠금 (허브·자료 공용). 비밀번호 변경 시 PW와 KEY만 수정
(function(){
  /* 주소 통일: www.0505.co.kr 이나 http:// 로 들어오면 https://0505.co.kr 로 보냄.
     브라우저는 주소(www 유무·http/https)마다 비밀번호 통과 기록을 따로 두기 때문에, 주소가 섞이면 비밀번호를 두 번 묻게 된다. */
  if(/^www\.0505\.co\.kr$/i.test(location.hostname) || (location.protocol==='http:' && /0505\.co\.kr$/i.test(location.hostname))){
    location.replace('https://0505.co.kr' + location.pathname + location.search + location.hash); return;
  }
  var KEY='pw0505v2', PW='05050S', HOURS=3;
  function valid(){ try{ return parseInt(localStorage.getItem(KEY)||'0',10) > Date.now(); }catch(e){ return false; } }
  /* 허브용 「클릭 잠금」: <script>window.PWGATE_CLICK=1</script> 를 이 파일보다 먼저 두면
     페이지는 그대로 보이고, 새 창으로 여는 항목(target=_blank)을 누를 때만 비밀번호를 묻는다.
     인덱스 안에 불려 온 경우에는 인덱스의 비밀번호 창을 띄운다. */
  if(window.PWGATE_CLICK){
    document.addEventListener('click',function(e){
      var a=e.target.closest ? e.target.closest('a[target="_blank"]') : null;
      if(!a || a.hasAttribute('data-nolock') || valid() || e.ctrlKey || e.metaKey || e.shiftKey) return;   /* data-nolock = 공개 자료 */
      e.preventDefault();
      if(window.self!==window.top){ try{ window.parent.postMessage({seoroHub:'pw', url:a.href},'*'); return; }catch(x){} }
      show(function(){ window.open(a.href,'_blank'); });
    },true);
    return;
  }
  if(valid()) return;
  /* 인덱스 화면 안(iframe)에 불려 온 경우: 안에서 잠금창을 띄우면 허브 높이만큼 늘어난 화면 한가운데로 밀려 안 보임 →
     인덱스의 비밀번호 창을 띄우고(통과하면 인덱스가 이 허브를 다시 엶), 여기서는 내용을 숨김 */
  var asked=0; try{ asked=parseInt(sessionStorage.getItem('pwgateAsk')||'0',10); }catch(e){}
  if(window.self!==window.top && Date.now()-asked>5000){   /* 5초 안에 다시 오면(되풀이 방지) 아래 기존 잠금창 사용 */
    try{ sessionStorage.setItem('pwgateAsk', String(Date.now())); }catch(e){}
    try{ window.parent.postMessage({seoroHub:'pw', url:location.href},'*'); }catch(e){}
    document.documentElement.style.display='none'; return;
  }
  document.documentElement.style.visibility='hidden';
  function show(done){
    var ov=document.createElement('div');
    ov.id='pwgate';
    ov.style.cssText='position:fixed;inset:0;z-index:99999;background:#1f3864;display:flex;align-items:center;justify-content:center;visibility:visible;font-family:-apple-system,"Noto Sans KR",sans-serif;';
    ov.innerHTML='<div style="background:#fff;border-radius:16px;padding:32px 28px;width:min(90vw,340px);text-align:center;box-shadow:0 10px 40px rgba(0,0,0,.35);">'
      +'<div style="font-size:34px;margin-bottom:10px;">🔒</div>'
      +'<div style="font-size:16px;font-weight:700;color:#1f3864;margin-bottom:6px;">재원생 전용 자료</div>'
      +'<div style="font-size:12.5px;color:#777;margin-bottom:18px;">비밀번호를 입력하세요</div>'
      +'<input id="pwgate-in" type="password" autocomplete="off" style="width:100%;box-sizing:border-box;font-size:18px;text-align:center;letter-spacing:4px;padding:11px;border:2px solid #d0d7e2;border-radius:10px;outline:none;">'
      +'<div id="pwgate-msg" style="height:18px;font-size:12px;color:#c0392b;margin-top:6px;"></div>'
      +'<button id="pwgate-btn" style="width:100%;margin-top:6px;padding:12px;font-size:15px;font-weight:700;color:#fff;background:#2e75b6;border:0;border-radius:10px;cursor:pointer;">입장</button>'
      +(done ? '<a href="#" id="pwgate-x" style="display:block;margin-top:14px;font-size:12px;color:#999;text-decoration:none;">닫기</a>'
             : '<a href="https://0505.co.kr/" style="display:block;margin-top:14px;font-size:12px;color:#999;text-decoration:none;">← 메인으로</a>')
      +'</div>';
    document.documentElement.appendChild(ov);
    var inp=document.getElementById('pwgate-in');
    function ok(){
      if(inp.value.trim()===PW){
        try{ localStorage.setItem(KEY, String(Date.now()+HOURS*3600*1000)); }catch(e){}
        ov.remove(); document.documentElement.style.visibility='';
        if(done) done();
      }else{
        document.getElementById('pwgate-msg').textContent='비밀번호가 틀렸습니다';
        inp.value=''; inp.focus();
      }
    }
    document.getElementById('pwgate-btn').onclick=ok;
    if(done) document.getElementById('pwgate-x').onclick=function(e){ e.preventDefault(); ov.remove(); };
    inp.addEventListener('keydown',function(e){ if(e.key==='Enter') ok(); });
    setTimeout(function(){ inp.focus(); },50);
  }
  if(document.readyState==='loading') document.addEventListener('DOMContentLoaded',show); else show();
})();

/* 학원 태블릿 앱(안드로이드 WebView) 전용 「새로고침」 버튼.
   앱에는 주소창·새로고침이 없어 새로 올린 내용이 반영되지 않던 문제 대응.
   일반 브라우저와 인덱스 안에 불려 온 허브(iframe)에서는 아무것도 하지 않음 */
(function(){
  if(!/; wv\)/.test(navigator.userAgent) || window.self!==window.top) return;
  function add(){
    if(document.getElementById('appbar0505')) return;
    var r=document.createElement('button');
    r.id='appbar0505'; r.type='button'; r.setAttribute('aria-label','새로고침'); r.innerHTML='<svg viewBox="0 0 24 24" width="14" height="14" style="display:block"><path fill="currentColor" d="M17.65 6.35A7.95 7.95 0 0 0 12 4a8 8 0 1 0 7.75 10h-2.08A6 6 0 1 1 12 6c1.66 0 3.14.69 4.22 1.78L13 11h7V4l-2.35 2.35z"/></svg>';
    r.style.cssText='position:fixed;top:2px;right:2px;z-index:99998;width:24px;height:24px;padding:0;display:flex;align-items:center;justify-content:center;border-radius:50%;border:1px solid #fff;background:#c9a84c;color:#0b1426;box-shadow:0 3px 10px rgba(0,0,0,.3);';
    r.onclick=function(){ location.reload(); };
    document.body.appendChild(r);
  }
  if(document.readyState==='loading') document.addEventListener('DOMContentLoaded',add); else add();
})();
