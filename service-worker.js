const CACHE_NAME = 'def-pulse-v1';
const ASSETS = [
  './',
  './index.html',
  'https://api.rss2json.com/v1/api.json'
];

// Installation : Mise en cache du squelette de l'app
self.addEventListener('install', (e) => {
  e.waitUntil(
    caches.open(CACHE_NAME).then((cache) => cache.addAll(ASSETS))
  );
});

// Stratégie : Network First, fallback on Cache
// On essaye d'abord d'avoir les dernières infos, sinon on affiche le cache
self.addEventListener('fetch', (e) => {
  e.respondWith(
    fetch(e.request).catch(() => caches.match(e.request))
  );
});
