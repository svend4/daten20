/**
 * Service Worker for DMS Progressive Web App
 *
 * Features:
 * - Offline functionality with cache-first strategy
 * - Background sync for pending uploads
 * - Push notifications
 * - App manifest support
 * - Install prompts
 * - Cache strategies (Cache First, Network First, Stale While Revalidate)
 * - IndexedDB for offline data storage
 */

const CACHE_VERSION = 'dms-v1';
const CACHE_NAME = `dms-cache-${CACHE_VERSION}`;

// Assets to cache on install
const STATIC_ASSETS = [
  '/',
  '/index.html',
  '/manifest.json',
  '/static/css/main.css',
  '/static/js/main.js',
  '/static/images/logo.png',
  '/static/images/icon-192.png',
  '/static/images/icon-512.png',
  '/offline.html'
];

// API base URL (configure based on environment)
const API_BASE_URL = self.location.origin + '/api/v1';

// Cache strategies
const CACHE_STRATEGIES = {
  CACHE_FIRST: 'cache-first',
  NETWORK_FIRST: 'network-first',
  STALE_WHILE_REVALIDATE: 'stale-while-revalidate',
  NETWORK_ONLY: 'network-only',
  CACHE_ONLY: 'cache-only'
};

// Route-specific cache strategies
const ROUTE_STRATEGIES = {
  '/api/v1/documents': CACHE_STRATEGIES.NETWORK_FIRST,
  '/static/': CACHE_STRATEGIES.CACHE_FIRST,
  '/images/': CACHE_STRATEGIES.CACHE_FIRST
};

// MARK: - Install Event

self.addEventListener('install', (event) => {
  console.log('[ServiceWorker] Installing...');

  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      console.log('[ServiceWorker] Caching static assets');
      return cache.addAll(STATIC_ASSETS);
    }).then(() => {
      console.log('[ServiceWorker] Installed successfully');
      return self.skipWaiting(); // Activate immediately
    })
  );
});

// MARK: - Activate Event

self.addEventListener('activate', (event) => {
  console.log('[ServiceWorker] Activating...');

  event.waitUntil(
    // Clean up old caches
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames.map((cacheName) => {
          if (cacheName !== CACHE_NAME) {
            console.log('[ServiceWorker] Deleting old cache:', cacheName);
            return caches.delete(cacheName);
          }
        })
      );
    }).then(() => {
      console.log('[ServiceWorker] Activated successfully');
      return self.clients.claim(); // Take control immediately
    })
  );
});

// MARK: - Fetch Event

self.addEventListener('fetch', (event) => {
  const { request } = event;
  const url = new URL(request.url);

  // Skip non-GET requests
  if (request.method !== 'GET') {
    return;
  }

  // Determine cache strategy
  const strategy = determineStrategy(url.pathname);

  event.respondWith(
    handleRequest(request, strategy)
  );
});

/**
 * Determine cache strategy for a given path
 */
function determineStrategy(pathname) {
  for (const [route, strategy] of Object.entries(ROUTE_STRATEGIES)) {
    if (pathname.startsWith(route)) {
      return strategy;
    }
  }
  return CACHE_STRATEGIES.NETWORK_FIRST; // Default strategy
}

/**
 * Handle request based on strategy
 */
async function handleRequest(request, strategy) {
  switch (strategy) {
    case CACHE_STRATEGIES.CACHE_FIRST:
      return cacheFirst(request);

    case CACHE_STRATEGIES.NETWORK_FIRST:
      return networkFirst(request);

    case CACHE_STRATEGIES.STALE_WHILE_REVALIDATE:
      return staleWhileRevalidate(request);

    case CACHE_STRATEGIES.NETWORK_ONLY:
      return fetch(request);

    case CACHE_STRATEGIES.CACHE_ONLY:
      return caches.match(request);

    default:
      return networkFirst(request);
  }
}

/**
 * Cache First strategy
 * Try cache first, then network
 */
async function cacheFirst(request) {
  const cached = await caches.match(request);

  if (cached) {
    return cached;
  }

  try {
    const response = await fetch(request);

    // Cache successful responses
    if (response.ok) {
      const cache = await caches.open(CACHE_NAME);
      cache.put(request, response.clone());
    }

    return response;
  } catch (error) {
    console.error('[ServiceWorker] Cache First failed:', error);
    return offlineResponse();
  }
}

/**
 * Network First strategy
 * Try network first, fall back to cache
 */
async function networkFirst(request) {
  try {
    const response = await fetch(request);

    // Cache successful responses
    if (response.ok) {
      const cache = await caches.open(CACHE_NAME);
      cache.put(request, response.clone());
    }

    return response;
  } catch (error) {
    console.log('[ServiceWorker] Network failed, trying cache');
    const cached = await caches.match(request);

    if (cached) {
      return cached;
    }

    return offlineResponse();
  }
}

/**
 * Stale While Revalidate strategy
 * Return cached response immediately, update cache in background
 */
async function staleWhileRevalidate(request) {
  const cached = await caches.match(request);

  // Fetch and update cache in background
  const fetchPromise = fetch(request).then((response) => {
    if (response.ok) {
      const cache = caches.open(CACHE_NAME);
      cache.then((c) => c.put(request, response.clone()));
    }
    return response;
  });

  // Return cached version immediately, or wait for network
  return cached || fetchPromise;
}

/**
 * Return offline response
 */
function offlineResponse() {
  return caches.match('/offline.html') || new Response(
    'Offline - No cached content available',
    { status: 503, statusText: 'Service Unavailable' }
  );
}

// MARK: - Background Sync

self.addEventListener('sync', (event) => {
  console.log('[ServiceWorker] Background sync:', event.tag);

  if (event.tag === 'sync-documents') {
    event.waitUntil(syncDocuments());
  }
});

/**
 * Sync pending document uploads
 */
async function syncDocuments() {
  console.log('[ServiceWorker] Syncing documents...');

  try {
    // Open IndexedDB
    const db = await openDB();
    const tx = db.transaction('pending_uploads', 'readonly');
    const store = tx.objectStore('pending_uploads');
    const pendingUploads = await getAllFromStore(store);

    console.log(`[ServiceWorker] Found ${pendingUploads.length} pending uploads`);

    // Upload each document
    for (const upload of pendingUploads) {
      try {
        await uploadDocument(upload);

        // Remove from pending queue
        const deleteTx = db.transaction('pending_uploads', 'readwrite');
        const deleteStore = deleteTx.objectStore('pending_uploads');
        await deleteStore.delete(upload.id);

        console.log('[ServiceWorker] Uploaded:', upload.id);
      } catch (error) {
        console.error('[ServiceWorker] Upload failed:', upload.id, error);
      }
    }

    // Notify clients of sync completion
    const clients = await self.clients.matchAll();
    clients.forEach((client) => {
      client.postMessage({
        type: 'SYNC_COMPLETE',
        count: pendingUploads.length
      });
    });

  } catch (error) {
    console.error('[ServiceWorker] Sync failed:', error);
    throw error;
  }
}

/**
 * Upload document to server
 */
async function uploadDocument(upload) {
  const formData = new FormData();
  formData.append('file', upload.file);
  formData.append('title', upload.title);

  if (upload.tags) {
    upload.tags.forEach((tag) => formData.append('tags', tag));
  }

  const response = await fetch(`${API_BASE_URL}/documents`, {
    method: 'POST',
    body: formData,
    headers: {
      'Authorization': `Bearer ${upload.apiKey}`
    }
  });

  if (!response.ok) {
    throw new Error(`Upload failed: ${response.status}`);
  }

  return response.json();
}

// MARK: - Push Notifications

self.addEventListener('push', (event) => {
  console.log('[ServiceWorker] Push notification received');

  let data = {
    title: 'DMS Notification',
    body: 'You have a new notification',
    icon: '/static/images/icon-192.png',
    badge: '/static/images/badge.png'
  };

  if (event.data) {
    try {
      data = { ...data, ...event.data.json() };
    } catch (e) {
      data.body = event.data.text();
    }
  }

  const options = {
    body: data.body,
    icon: data.icon,
    badge: data.badge,
    data: data.data,
    actions: data.actions || [
      { action: 'open', title: 'Open' },
      { action: 'close', title: 'Close' }
    ]
  };

  event.waitUntil(
    self.registration.showNotification(data.title, options)
  );
});

self.addEventListener('notificationclick', (event) => {
  console.log('[ServiceWorker] Notification clicked:', event.action);

  event.notification.close();

  if (event.action === 'open') {
    event.waitUntil(
      clients.openWindow(event.notification.data?.url || '/')
    );
  }
});

// MARK: - Message Handler

self.addEventListener('message', (event) => {
  console.log('[ServiceWorker] Message received:', event.data);

  if (event.data.type === 'SKIP_WAITING') {
    self.skipWaiting();
  }

  if (event.data.type === 'QUEUE_UPLOAD') {
    queueUpload(event.data.upload).then(() => {
      event.ports[0].postMessage({ success: true });
    }).catch((error) => {
      event.ports[0].postMessage({ success: false, error: error.message });
    });
  }
});

/**
 * Queue document for background upload
 */
async function queueUpload(upload) {
  const db = await openDB();
  const tx = db.transaction('pending_uploads', 'readwrite');
  const store = tx.objectStore('pending_uploads');

  await store.add({
    id: Date.now(),
    ...upload,
    queuedAt: new Date().toISOString()
  });

  // Register for background sync
  await self.registration.sync.register('sync-documents');
}

// MARK: - IndexedDB Helpers

/**
 * Open IndexedDB
 */
function openDB() {
  return new Promise((resolve, reject) => {
    const request = indexedDB.open('DMS_DB', 1);

    request.onerror = () => reject(request.error);
    request.onsuccess = () => resolve(request.result);

    request.onupgradeneeded = (event) => {
      const db = event.target.result;

      // Create object stores
      if (!db.objectStoreNames.contains('pending_uploads')) {
        db.createObjectStore('pending_uploads', { keyPath: 'id' });
      }

      if (!db.objectStoreNames.contains('documents')) {
        db.createObjectStore('documents', { keyPath: 'id' });
      }
    };
  });
}

/**
 * Get all items from store
 */
function getAllFromStore(store) {
  return new Promise((resolve, reject) => {
    const request = store.getAll();
    request.onsuccess = () => resolve(request.result);
    request.onerror = () => reject(request.error);
  });
}

console.log('[ServiceWorker] Loaded');
