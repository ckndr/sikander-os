/**
 * Sikander OS — Service Worker (sw.js)
 * Cache-First for Core App Shell & Assets
 * Stale-While-Revalidate for JSON Catalogs
 * Clean Offline Fallback Page
 */

const CACHE_NAME = 'sikander-os-v2-master-2026';
const DATA_CACHE_NAME = 'sikander-os-data-v2';

const PRECACHE_ASSETS = [
  './',
  './index.html',
  './cinema.html',
  './property.html',
  './finance.html',
  './music.html',
  './career.html',
  './health.html',
  './offline.html',
  './manifest.json',
  './icons/icon.svg',
  './icons/icon-192.png',
  './icons/icon-512.png',
  './icons/icon-maskable-192.png',
  './icons/icon-maskable-512.png',
  './data/sync_engine.js',
  './data/sikander_unified_cinema.js',
  './data/sikander_unified_data.json',
  './data/property/alghafoor_property_ledger.js',
  './data/property/alghafoor_property_ledger.json',
  './data/music/sikander_music_library.js',
  './data/music/sikander_music_library.json',
  './data/career/sikander_career_data.js',
  './data/career/sikander_career_data.json',
  './data/finance/sikander_finance_master.js',
  './data/finance/sikander_finance_master.json',
  './data/health/sikander_health_data.js',
  './data/health/sikander_health_data.json',
  './data/health/sample_workout_sheet.csv'
];

// Install Event — Pre-cache Core App Shell
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      console.log('[Sikander OS SW] Pre-caching core app shell...');
      return cache.addAll(PRECACHE_ASSETS);
    }).then(() => self.skipWaiting())
  );
});

// Activate Event — Clean up outdated caches & claim clients
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames.map((name) => {
          if (name !== CACHE_NAME && name !== DATA_CACHE_NAME) {
            console.log('[Sikander OS SW] Removing obsolete cache:', name);
            return caches.delete(name);
          }
        })
      );
    }).then(() => self.clients.claim())
  );
});

// Fetch Event — Tiered caching strategies
self.addEventListener('fetch', (event) => {
  const { request } = event;
  const url = new URL(request.url);

  // Ignore non-GET requests
  if (request.method !== 'GET') return;

  // Ignore chrome-extension schemes or non-http/https
  if (!url.protocol.startsWith('http')) return;

  // Strategy 1: Stale-While-Revalidate for JSON Data Catalogs
  if (url.pathname.endsWith('.json') || url.pathname.includes('/data/')) {
    event.respondWith(
      caches.open(DATA_CACHE_NAME).then((dataCache) => {
        return dataCache.match(request).then((cachedResponse) => {
          // Asynchronously fetch fresh data from network and update cache
          const fetchPromise = fetch(request).then((networkResponse) => {
            if (networkResponse && networkResponse.status === 200) {
              dataCache.put(request, networkResponse.clone());
            }
            return networkResponse;
          }).catch((err) => {
            console.warn('[Sikander OS SW] Network fetch failed for data asset, falling back to cache:', url.pathname);
          });

          // Return cached version immediately if present; otherwise await network
          return cachedResponse || fetchPromise;
        });
      })
    );
    return;
  }

  // Strategy 2: Navigation requests (HTML pages)
  if (request.mode === 'navigate') {
    event.respondWith(
      caches.match(request).then((cachedPage) => {
        // Return cached page or fetch from network
        return cachedPage || fetch(request).then((networkResponse) => {
          if (networkResponse && networkResponse.status === 200) {
            const copy = networkResponse.clone();
            caches.open(CACHE_NAME).then((cache) => cache.put(request, copy));
          }
          return networkResponse;
        });
      }).catch(() => {
        // Network and cache failed — provide offline fallback page
        return caches.match('./offline.html');
      })
    );
    return;
  }

  // Strategy 3: Cache-First for Core Static Assets (JS, CSS, Fonts, Images, SVGs)
  event.respondWith(
    caches.match(request).then((cachedResponse) => {
      if (cachedResponse) {
        return cachedResponse;
      }

      // If not in cache, fetch from network and cache it
      return fetch(request).then((networkResponse) => {
        if (networkResponse && networkResponse.status === 200) {
          const responseToCache = networkResponse.clone();
          caches.open(CACHE_NAME).then((cache) => {
            cache.put(request, responseToCache);
          });
        }
        return networkResponse;
      }).catch((err) => {
        console.warn('[Sikander OS SW] Asset fetch failed:', url.pathname);
      });
    })
  );
});

// Message Event — Support manual skipWaiting from client UI
self.addEventListener('message', (event) => {
  if (event.data && event.data.type === 'SKIP_WAITING') {
    self.skipWaiting();
  }
});
