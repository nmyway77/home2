// 재원생 전용 잠금 (허브·자료 공용). 비밀번호 변경 시 PW와 KEY만 수정
(function(){
  var KEY='pw0505v2', PW='05050S', HOURS=3;
  function valid(){ try{ return parseInt(localStorage.getItem(KEY)||'0',10) > Date.now(); }catch(e){ return false; } }
  /* 허브용 「클릭 잠금」: <script>window.PWGATE_CLICK=1</script> 를 이 파일보다 먼저 두면
     페이지는 그대로 보이고, 새 창으로 여는 항목(target=_blank)을 누를 때만 비밀번호를 묻는다.
     인덱스 안에 불려 온 경우에는 인덱스의 비밀번호 창을 띄운다. */
  if(window.PWGATE_CLICK){
    document.addEventListener('click',function(e){
      var a=e.target.closest ? e.target.closest('a[target="_blank"]') : null;
      if(!a || valid() || e.ctrlKey || e.metaKey || e.shiftKey) return;
      e.preventDefault();
      if(window.self!==window.top){ try{ window.parent.postMessage({seoroHub:'pw', url:a.href},'*'); return; }catch(x){} }
      show(function(){ window.open(a.href,'_blank'); });
    },true);
    return;
  }
  if(valid()) return;
  document.documentElement.style.visibility='hidden';
  function show(done){
    var ov=document.createElement('div');
    ov.id='pwgate';
    ov.style.cssText='position:fixed;inset:0;z-index:99999;background:#1f3864;display:flex;align-items:center;justify-content:center;visibility:visible;font-family:-apple-system,"Noto Sans KR",sans-serif;';
    ov.innerHTML='<div style="background:#fff;border-radius:16px;padding:32px 28px;width:min(90vw,340px);text-align:center;box-shadow:0 10px 40px rgba(0,0,0,.35);">'
      +'<div style="font-size:34px;margin-bottom:10px;">🔒</div>'
      +'<div style="font-size:16px;font-weight:700;color:#1f3864;margin-bottom:6px;">재원생 전용 자료</div>'
      +'<div style="font-size:12.5px;color:#777;margin-bottom:18px;">비밀번호를 입력하세요</div>'
      +'<input id="pwgate-in" type="password" inputmode="numeric" autocomplete="off" style="width:100%;box-sizing:border-box;font-size:18px;text-align:center;letter-spacing:4px;padding:11px;border:2px solid #d0d7e2;border-radius:10px;outline:none;">'
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
