// =============================================
// 목동서로영어학원 Service Worker v1.0
// =============================================
const CACHE_NAME = 'mokdong-v1';

// 오프라인에서도 작동할 핵심 파일들
const CORE_FILES = [
  '/',
  '/index.html',
  'https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,300;0,600;0,700;1,400&family=Noto+Sans+KR:wght@300;400;500;700&family=JetBrains+Mono:wght@400;500;700&display=swap'
];

// ── 설치 ──
self.addEventListener('install', e => {
  e.waitUntil(
    caches.open(CACHE_NAME).then(cache => {
      return cache.addAll(CORE_FILES).catch(() => {});
    })
  );
  self.skipWaiting();
});

// ── 활성화 ──
self.addEventListener('activate', e => {
  e.waitUntil(
    caches.keys().then(keys =>
      Promise.all(
        keys.filter(k => k !== CACHE_NAME).map(k => caches.delete(k))
      )
    )
  );
  self.clients.claim();
});

// ── 요청 처리 ──
// 전략: Network First (최신 데이터 우선) → 실패 시 캐시 사용
self.addEventListener('fetch', e => {
  // GET 요청만 처리
  if (e.request.method !== 'GET') return;

  // 외부 API(fonts 등)는 캐시 우선
  if (e.request.url.includes('fonts.googleapis') ||
      e.request.url.includes('fonts.gstatic')) {
    e.respondWith(
      caches.match(e.request).then(cached => {
        if (cached) return cached;
        return fetch(e.request).then(res => {
          const clone = res.clone();
          caches.open(CACHE_NAME).then(c => c.put(e.request, clone));
          return res;
        });
      })
    );
    return;
  }

  // HTML 파일: Network First
  if (e.request.destination === 'document' ||
      e.request.url.endsWith('.html')) {
    e.respondWith(
      fetch(e.request)
        .then(res => {
          const clone = res.clone();
          caches.open(CACHE_NAME).then(c => c.put(e.request, clone));
          return res;
        })
        .catch(() => caches.match(e.request))
    );
    return;
  }

  // 나머지: Cache First
  e.respondWith(
    caches.match(e.request).then(cached => {
      return cached || fetch(e.request).then(res => {
        const clone = res.clone();
        caches.open(CACHE_NAME).then(c => c.put(e.request, clone));
        return res;
      });
    })
  );
});
