# 고3 10월 한줄해석 점검 보강 패치 (HTML·빌드 스크립트 공용, 멱등)
import sys
P = {
 'H320261041': [
  ('동물과 겨우 구별해 주는 가장 단순한 인지 기능', '동물과 구별해 주는 바로 그 가장 단순한 인지 기능'),
  ('동물과 겨우 구별해 주는(관계절)', '동물과 구별해 주는(관계절)'),
  ('우리를 동물과 겨우 구별하다 (42 (a) 적절)', '우리를 동물과 구별하다 (42 (a) 적절)'),
  ('우리를 동물과 겨우 구별해 주는', '우리를 동물과 구별해 주는'),
  ('(여기서) 겨우, 그 하나만으로 — cf. 단지 · 방금 · 바로', '(여기서) 바로, 딱 — 그것 하나만으로 구별한다는 강조 · cf. 단지 · 방금'),
  ('(여기서) 겨우, 그 하나만으로 — cf. 단지 · 방금', '(여기서) 바로, 딱 — 그것 하나만으로 구별한다는 강조 · cf. 단지 · 방금'),
  ('syn:["merely","barely"], ant:[],\n   phrases:["that just separates', 'syn:["precisely","simply"], ant:[],\n   phrases:["that just separates'),
  ('syn:[\\"merely\\",\\"barely\\"], ant:[],\\n   phrases:[\\"that just separates', 'syn:[\\"precisely\\",\\"simply\\"], ant:[],\\n   phrases:[\\"that just separates'),
 ],
 'H320261038': [
  ('words:["genomes","are","subject","to","mutate","randomly","as","the","information","is","passed"]',
   'words:["genomes","are","subject","to","random","mutate","as","the","information","is","passed"]'),
  ('underlined:[4],\n   errors:[{idx:4,correct:"random mutations",exp:"<strong>mutate → random mutations</strong>: be subject to의 to는 전치사 → 명사가 와야 한다."}]',
   'underlined:[5],\n   errors:[{idx:5,correct:"mutations",exp:"<strong>mutate → mutations</strong>: be subject to의 to는 전치사 → 뒤에 명사(random mutations)가 와야 한다."}]'),
  ('words:[\\"genomes\\",\\"are\\",\\"subject\\",\\"to\\",\\"mutate\\",\\"randomly\\",\\"as\\",\\"the\\",\\"information\\",\\"is\\",\\"passed\\"]',
   'words:[\\"genomes\\",\\"are\\",\\"subject\\",\\"to\\",\\"random\\",\\"mutate\\",\\"as\\",\\"the\\",\\"information\\",\\"is\\",\\"passed\\"]'),
  ('underlined:[4],\\n   errors:[{idx:4,correct:\\"random mutations\\",exp:\\"<strong>mutate → random mutations</strong>: be subject to의 to는 전치사 → 명사가 와야 한다.\\"}]',
   'underlined:[5],\\n   errors:[{idx:5,correct:\\"mutations\\",exp:\\"<strong>mutate → mutations</strong>: be subject to의 to는 전치사 → 뒤에 명사(random mutations)가 와야 한다.\\"}]'),
 ],
}
def apply(path):
    s=open(path,encoding='utf-8').read(); key=[k for k in P if k in path]
    if not key: return 'skip'
    n=0
    for old,new in P[key[0]]:
        if old in s: s=s.replace(old,new); n+=1
    open(path,'w',encoding='utf-8').write(s); return f'{n} replacements'
for p in sys.argv[1:]: print(apply(p), p)
