# 고2 10월 한줄해석 점검 보강 패치 (HTML·빌드 스크립트 공용, 멱등)
# 사용: python3 patch_h2_2610_review.py mogo2-2610/H2202610*.html
import sys
P = {
 'H220261033': [
  # 어법 오류찾기 er1: 'lay'는 lie의 과거형으로도 읽혀 문법상 틀리지 않으므로 오답 단어를 lays(타동사)로 교체
  ('"perspective","lay","the","concept"', '"perspective","lays","the","concept"'),
  ('<strong>lay → lies</strong>: 도치 구문, 주어 the concept(단수) + 자동사 lie의 현재형.',
   '<strong>lays → lies</strong>: 목적어가 없으므로 자동사 lie(있다)의 현재형 — 도치된 주어 the concept(단수) → lies. lay는 타동사(~을 놓다).'),
 ],
 'H220261034': [
  # er9: 정답 칸이 "(삭제)"로 표시되던 것을 because of 한 토큰 → because 로 교정
  ('"vulnerabilities","because","of","interconnectedness","instantly","spreads","the","impact","of","small","failures"],\n   underlined:[6],\n   errors:[{idx:6,correct:"(삭제)",exp:"<strong>because of → because</strong>: 뒤에 절(interconnectedness spreads)이 오므로 접속사 because. of 삭제."}]}',
   '"vulnerabilities","because of","interconnectedness","instantly","spreads","the","impact","of","small","failures"],\n   underlined:[5],\n   errors:[{idx:5,correct:"because",exp:"<strong>because of → because</strong>: 뒤에 절(interconnectedness spreads)이 오므로 접속사 because(because of는 전치사 → 뒤에 명사)."}]}'),
 ],
 'H220261036': [
  # er8: 정답 칸이 빈칸("")으로 표시되던 것을 will be 한 토큰 → is 로 교정
  ('"once","it","will","be","in","the","hands","of","real","users"],\n   underlined:[8,9],\n   errors:[{idx:8,correct:"",exp:"(시간 부사절 once에는 will을 쓰지 않음 — 삭제)"},{idx:9,correct:"is",exp:"<strong>will be → is</strong>: 시간 부사절 현재 시제."}]}',
   '"once","it","will be","in","the","hands","of","real","users"],\n   underlined:[8],\n   errors:[{idx:8,correct:"is",exp:"<strong>will be → is</strong>: once가 이끄는 시간 부사절은 미래의 일이라도 현재 시제."}]}'),
 ],
 'H220261038': [
  # er4: 정답 칸이 빈칸("")으로 표시되던 것을 because of 한 토큰 → because 로 교정
  ('"everyone","because","of","we","use","water","for","so","many","diverse","things"],\n   underlined:[9],\n   errors:[{idx:9,correct:"",exp:"<strong>because of → because</strong>: 뒤에 절(we use ~)이 오므로 of 삭제."}]}',
   '"everyone","because of","we","use","water","for","so","many","diverse","things"],\n   underlined:[8],\n   errors:[{idx:8,correct:"because",exp:"<strong>because of → because</strong>: 뒤에 절(we use ~)이 오므로 접속사 because(because of는 전치사 → 뒤에 명사)."}]}'),
 ],
 'H220261039': [
  # er2: 정답 칸이 "(삭제)"로 표시되던 것을 lacked of 한 토큰 → lacked 로 교정
  ('"non-elites","lacked","of","access","to","education","and,","thus,","did","not","produce","documentation"],\n   underlined:[2],\n   errors:[{idx:2,correct:"(삭제)",exp:"<strong>of 삭제</strong>: lack은 타동사 — lacked access."}]}',
   '"non-elites","lacked of","access","to","education","and,","thus,","did","not","produce","documentation"],\n   underlined:[1],\n   errors:[{idx:1,correct:"lacked",exp:"<strong>lacked of → lacked</strong>: lack은 타동사 — 전치사 없이 바로 목적어(lacked access)."}]}'),
 ],
 'H220261040': [
  # S06 문법 카드에 작업 지침 참조(§6-G 8항)가 노출된 것을 제거
  ('나누어 맡는 것 전체를 되받는다(§6-G 8항).', '나누어 맡는 것 전체를 되받는다.'),
 ],
}
def apply(path):
    s=open(path,encoding='utf-8').read(); key=[k for k in P if k in path]
    if not key: return 'skip'
    n=0
    for old,new in P[key[0]]:
        if old in s: s=s.replace(old,new); n+=1
    open(path,'w',encoding='utf-8').write(s); return f'{n}/{len(P[key[0]])} replacements'
for p in sys.argv[1:]: print(apply(p), p)
