# 펜 필기 모드 v1.2.1 — 두 손가락 스크롤 버그 수정 + 진단 모드 (2026-10-23)

## 적용 범위
- mogo3-2610/H320261030~41 (고3 10월) 12개: v1.0 → v1.2.1 신규 적용
- mogo1-2610/H120261030~41 (고1 10월) 12개: v1.2 → v1.2.1 갱신
- 고2 10월(mogo2-2610)·그 외 파일은 v1.0 그대로 (레노버 실기기 확인 후 확장)

## v1.2.1 변경 (retrofit_pen_v121.py — v1.0/1.1/1.2 → v1.2.1, 멱등)
1. [버그 수정] 두 손가락 스크롤: 한줄해석 페이지는 `html{scroll-behavior:smooth}`라서 touchmove마다 부르는 `window.scrollBy`가
   애니메이션으로 서로 취소돼 스크롤이 거의 되지 않았음(Playwright 에뮬레이션에서 0px 재현). 제스처 동안 즉시 스크롤로 전환.
   → 고1 v1.2에서도 같은 증상이었을 것.
2. [진단 모드] 주소 끝에 `#pendebug` 를 붙여 열면(예: https://0505.co.kr/mogo3-2610/H320261030.html#pendebug)
   화면 왼쪽 위에 UA · PointerEvent 지원 · 펜 ON/OFF · pointerdown/up/cancel 이벤트(pointerType, 좌표, 대상)가 표시됨.
   평소(해시 없음)에는 아무것도 만들지 않음. 레노버 태블릿에서 선이 안 그려질 때 이 화면을 캡처하면 원인 확인 가능.
3. 나머지는 고1 v1.2와 동일: Pointer Events + Touch 폴백 · touchstart/move 비-passive preventDefault · inline touch-action:none ·
   툴바 visualViewport 추적 · 팜 리젝션 · 두 손가락 스크롤 · 펜 모드 중 탭 줄(.view-tabs)·상단 메뉴·단어장 탭 클릭 통과.

## 검증
- verify_v23: 24/24 ALL PASS
- Playwright(Chromium, is_mobile+has_touch, Android/Lenovo UA): ✏️ 토글 → 손가락 선 ○ · 스타일러스 선 ○ · 두 손가락 스크롤 200px ○ ·
  펜 모드 중 탭 줄 터치로 탭 전환 ○ · PC 마우스 그리기/지우개/휠 스크롤 ○ · JS 오류 0
- 레노버 실기기 원인은 여전히 미확정 — 에뮬레이션에서는 v1.0도 선이 그려짐. #pendebug 로그 확인이 다음 단계.
