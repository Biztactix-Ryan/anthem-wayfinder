// Offline cache for Anthem Wayfinder: serve from cache at once, refresh the cache in the background.
const CACHE = 'wayfinder-v1';
const CORE = ['./', './index.html', './manifest.webmanifest', './icon-192.png', './icon-512.png', './apple-touch-icon.png'];
self.addEventListener('install', e => {
  e.waitUntil(caches.open(CACHE).then(c => c.addAll(CORE)).then(() => self.skipWaiting()));
});
self.addEventListener('activate', e => {
  e.waitUntil(caches.keys().then(ks => Promise.all(ks.filter(k => k !== CACHE).map(k => caches.delete(k)))).then(() => self.clients.claim()));
});
self.addEventListener('fetch', e => {
  const req = e.request;
  if (req.method !== 'GET') return;
  const url = new URL(req.url);
  const own = url.origin === location.origin;
  const font = /(^|\.)fonts\.(googleapis|gstatic)\.com$/.test(url.hostname);
  if (!own && !font) return;
  const key = own && req.mode === 'navigate' ? './index.html' : req;
  const work = caches.open(CACHE).then(async cache => {
    const hit = await cache.match(key, { ignoreSearch: own });
    const net = fetch(req).then(res => {
      if (res && (res.ok || res.type === 'opaque')) cache.put(key, res.clone());
      return res;
    });
    if (hit) { net.catch(() => {}); return { res: hit, bg: net.catch(() => {}) }; }
    return { res: await net, bg: null };
  });
  e.respondWith(work.then(w => w.res));
  e.waitUntil(work.then(w => w.bg).catch(() => {}));
});
