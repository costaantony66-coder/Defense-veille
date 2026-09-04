// Service worker minimal — met en cache la coquille de l'application
// pour un démarrage instantané et un mode hors-ligne dégradé.
// Les flux RSS (API rss2json) ne sont volontairement PAS mis en cache :
// il s'agit de données vivantes, toujours récupérées depuis le réseau.

const CACHE_NAME = 'defense-pulse-v1';
const APP_SHELL = ['./index.html', './manifest.json'];

self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME).then(cache => cache.addAll(APP_SHELL))
  );
  self.skipWaiting();
});

self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(keys =>
      Promise.all(keys.filter(k => k !== CACHE_NAME).map(k => caches.delete(k)))
    )
  );
  self.clients.claim();
});

self.addEventListener('fetch', event => {
  const url = new URL(event.request.url);

  // Ne jamais intercepter les appels API (flux RSS toujours frais)
  if (url.hostname.includes('rss2json.com')) return;

  event.respondWith(
    caches.match(event.request).then(cached => cached || fetch(event.request))
  );
});
