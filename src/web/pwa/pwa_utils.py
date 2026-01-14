#!/usr/bin/env python3
"""
PWA Utilities Module

Utilities for Progressive Web App support in DMS.

Features:
- Service worker registration
- Offline support detection
- Push notification subscription management
- Install prompt handling
- Cache management
- Background sync configuration
- Manifest generation
- Web Share API integration

Dependencies:
- None (pure Python utilities)
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from enum import Enum
import json
import logging

logger = logging.getLogger(__name__)


class DisplayMode(str, Enum):
    """PWA display modes"""
    FULLSCREEN = "fullscreen"
    STANDALONE = "standalone"
    MINIMAL_UI = "minimal-ui"
    BROWSER = "browser"


class Orientation(str, Enum):
    """Screen orientation"""
    ANY = "any"
    NATURAL = "natural"
    LANDSCAPE = "landscape"
    PORTRAIT = "portrait"
    PORTRAIT_PRIMARY = "portrait-primary"
    PORTRAIT_SECONDARY = "portrait-secondary"
    LANDSCAPE_PRIMARY = "landscape-primary"
    LANDSCAPE_SECONDARY = "landscape-secondary"


@dataclass
class PWAIcon:
    """PWA icon specification"""
    src: str
    sizes: str
    type: str = "image/png"
    purpose: str = "any maskable"


@dataclass
class PWAScreenshot:
    """PWA screenshot specification"""
    src: str
    sizes: str
    type: str = "image/png"
    label: Optional[str] = None


@dataclass
class PWAShortcut:
    """PWA shortcut specification"""
    name: str
    short_name: str
    description: str
    url: str
    icons: List[PWAIcon] = field(default_factory=list)


@dataclass
class ShareTarget:
    """Web Share Target configuration"""
    action: str
    method: str = "POST"
    enctype: str = "multipart/form-data"
    params: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PWAManifest:
    """PWA manifest configuration"""
    name: str
    short_name: str
    description: str
    start_url: str = "/"
    display: DisplayMode = DisplayMode.STANDALONE
    background_color: str = "#ffffff"
    theme_color: str = "#2196f3"
    orientation: Orientation = Orientation.PORTRAIT_PRIMARY
    lang: str = "en-US"
    dir: str = "ltr"
    scope: str = "/"
    icons: List[PWAIcon] = field(default_factory=list)
    screenshots: List[PWAScreenshot] = field(default_factory=list)
    shortcuts: List[PWAShortcut] = field(default_factory=list)
    share_target: Optional[ShareTarget] = None
    categories: List[str] = field(default_factory=list)
    related_applications: List[Dict[str, str]] = field(default_factory=list)
    prefer_related_applications: bool = False

    def to_dict(self) -> Dict[str, Any]:
        """Convert manifest to dictionary"""
        manifest = {
            "name": self.name,
            "short_name": self.short_name,
            "description": self.description,
            "start_url": self.start_url,
            "display": self.display,
            "background_color": self.background_color,
            "theme_color": self.theme_color,
            "orientation": self.orientation,
            "lang": self.lang,
            "dir": self.dir,
            "scope": self.scope,
            "icons": [
                {
                    "src": icon.src,
                    "sizes": icon.sizes,
                    "type": icon.type,
                    "purpose": icon.purpose
                }
                for icon in self.icons
            ],
            "screenshots": [
                {
                    "src": ss.src,
                    "sizes": ss.sizes,
                    "type": ss.type,
                    "label": ss.label
                }
                for ss in self.screenshots
            ],
            "shortcuts": [
                {
                    "name": sc.name,
                    "short_name": sc.short_name,
                    "description": sc.description,
                    "url": sc.url,
                    "icons": [
                        {
                            "src": icon.src,
                            "sizes": icon.sizes
                        }
                        for icon in sc.icons
                    ]
                }
                for sc in self.shortcuts
            ],
            "categories": self.categories,
            "related_applications": self.related_applications,
            "prefer_related_applications": self.prefer_related_applications
        }

        if self.share_target:
            manifest["share_target"] = {
                "action": self.share_target.action,
                "method": self.share_target.method,
                "enctype": self.share_target.enctype,
                "params": self.share_target.params
            }

        return manifest

    def to_json(self) -> str:
        """Convert manifest to JSON string"""
        return json.dumps(self.to_dict(), indent=2)


@dataclass
class PushSubscription:
    """Push notification subscription"""
    endpoint: str
    keys: Dict[str, str]
    expiration_time: Optional[int] = None


class PWAManager:
    """
    PWA Manager

    Manages Progressive Web App configuration and features.
    """

    def __init__(self, app_name: str, short_name: str):
        """
        Initialize PWA manager

        Args:
            app_name: Application name
            short_name: Short application name
        """
        self.app_name = app_name
        self.short_name = short_name
        self._push_subscriptions: Dict[str, PushSubscription] = {}

    def create_manifest(
        self,
        description: str,
        start_url: str = "/",
        theme_color: str = "#2196f3",
        **kwargs
    ) -> PWAManifest:
        """
        Create PWA manifest

        Args:
            description: App description
            start_url: Start URL
            theme_color: Theme color
            **kwargs: Additional manifest options

        Returns:
            PWA manifest
        """
        return PWAManifest(
            name=self.app_name,
            short_name=self.short_name,
            description=description,
            start_url=start_url,
            theme_color=theme_color,
            **kwargs
        )

    def generate_service_worker(
        self,
        cache_name: str = "dms-cache-v1",
        static_assets: Optional[List[str]] = None,
        cache_strategy: str = "network-first"
    ) -> str:
        """
        Generate service worker JavaScript code

        Args:
            cache_name: Cache name
            static_assets: Assets to cache
            cache_strategy: Default cache strategy

        Returns:
            Service worker JavaScript code
        """
        static_assets = static_assets or [
            "/",
            "/index.html",
            "/manifest.json",
            "/static/css/main.css",
            "/static/js/main.js"
        ]

        return f"""
// Generated Service Worker for {self.app_name}

const CACHE_NAME = '{cache_name}';
const STATIC_ASSETS = {json.dumps(static_assets, indent=2)};

self.addEventListener('install', (event) => {{
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {{
      return cache.addAll(STATIC_ASSETS);
    }}).then(() => self.skipWaiting())
  );
}});

self.addEventListener('activate', (event) => {{
  event.waitUntil(
    caches.keys().then((cacheNames) => {{
      return Promise.all(
        cacheNames.map((cacheName) => {{
          if (cacheName !== CACHE_NAME) {{
            return caches.delete(cacheName);
          }}
        }})
      );
    }}).then(() => self.clients.claim())
  );
}});

self.addEventListener('fetch', (event) => {{
  if (event.request.method !== 'GET') return;

  event.respondWith(
    fetch(event.request)
      .then((response) => {{
        if (response.ok) {{
          const cache = caches.open(CACHE_NAME);
          cache.then((c) => c.put(event.request, response.clone()));
        }}
        return response;
      }})
      .catch(() => {{
        return caches.match(event.request)
          .then((response) => {{
            return response || caches.match('/offline.html');
          }});
      }})
  );
}});

self.addEventListener('push', (event) => {{
  const data = event.data ? event.data.json() : {{}};
  const title = data.title || '{self.app_name}';
  const options = {{
    body: data.body || 'New notification',
    icon: data.icon || '/static/images/icon-192.png',
    badge: data.badge || '/static/images/badge.png',
    data: data.data
  }};

  event.waitUntil(
    self.registration.showNotification(title, options)
  );
}});

self.addEventListener('notificationclick', (event) => {{
  event.notification.close();
  event.waitUntil(
    clients.openWindow(event.notification.data?.url || '/')
  );
}});
"""

    def subscribe_push(
        self,
        user_id: str,
        subscription: PushSubscription
    ):
        """
        Subscribe user to push notifications

        Args:
            user_id: User ID
            subscription: Push subscription
        """
        self._push_subscriptions[user_id] = subscription
        logger.info(f"Subscribed user {user_id} to push notifications")

    def unsubscribe_push(self, user_id: str):
        """
        Unsubscribe user from push notifications

        Args:
            user_id: User ID
        """
        if user_id in self._push_subscriptions:
            del self._push_subscriptions[user_id]
            logger.info(f"Unsubscribed user {user_id} from push notifications")

    def get_push_subscription(self, user_id: str) -> Optional[PushSubscription]:
        """
        Get push subscription for user

        Args:
            user_id: User ID

        Returns:
            Push subscription or None
        """
        return self._push_subscriptions.get(user_id)

    def generate_install_prompt_html(self) -> str:
        """
        Generate HTML for install prompt

        Returns:
            HTML code for install prompt
        """
        return f"""
<div id="install-prompt" class="install-prompt" style="display: none;">
  <div class="install-prompt-content">
    <h3>Install {self.app_name}</h3>
    <p>Install this app on your device for a better experience.</p>
    <button id="install-button">Install</button>
    <button id="dismiss-button">Not Now</button>
  </div>
</div>

<script>
let deferredPrompt;

window.addEventListener('beforeinstallprompt', (e) => {{
  e.preventDefault();
  deferredPrompt = e;
  document.getElementById('install-prompt').style.display = 'block';
}});

document.getElementById('install-button').addEventListener('click', async () => {{
  if (deferredPrompt) {{
    deferredPrompt.prompt();
    const {{ outcome }} = await deferredPrompt.userChoice;
    console.log('Install prompt outcome:', outcome);
    deferredPrompt = null;
    document.getElementById('install-prompt').style.display = 'none';
  }}
}});

document.getElementById('dismiss-button').addEventListener('click', () => {{
  document.getElementById('install-prompt').style.display = 'none';
}});

window.addEventListener('appinstalled', () => {{
  console.log('{self.app_name} installed');
  deferredPrompt = null;
}});
</script>

<style>
.install-prompt {{
  position: fixed;
  bottom: 20px;
  left: 20px;
  right: 20px;
  background: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  z-index: 1000;
}}

.install-prompt-content h3 {{
  margin-top: 0;
}}

.install-prompt button {{
  margin-right: 10px;
  padding: 10px 20px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}}

#install-button {{
  background-color: #2196f3;
  color: white;
}}

#dismiss-button {{
  background-color: #e0e0e0;
  color: #333;
}}
</style>
"""

    def generate_offline_page(self) -> str:
        """
        Generate offline fallback page

        Returns:
            HTML code for offline page
        """
        return f"""
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Offline - {self.app_name}</title>
  <style>
    body {{
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      display: flex;
      justify-content: center;
      align-items: center;
      height: 100vh;
      margin: 0;
      background-color: #f5f5f5;
    }}
    .offline-container {{
      text-align: center;
      padding: 40px;
      background: white;
      border-radius: 8px;
      box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }}
    h1 {{
      color: #333;
      margin-bottom: 16px;
    }}
    p {{
      color: #666;
      margin-bottom: 24px;
    }}
    button {{
      background-color: #2196f3;
      color: white;
      border: none;
      padding: 12px 24px;
      border-radius: 4px;
      cursor: pointer;
      font-size: 16px;
    }}
    button:hover {{
      background-color: #1976d2;
    }}
  </style>
</head>
<body>
  <div class="offline-container">
    <h1>You're Offline</h1>
    <p>Please check your internet connection and try again.</p>
    <button onclick="window.location.reload()">Retry</button>
  </div>
</body>
</html>
"""


# Example usage
if __name__ == "__main__":
    # Create PWA manager
    pwa = PWAManager(
        app_name="Document Management System",
        short_name="DMS"
    )

    # Create manifest
    manifest = pwa.create_manifest(
        description="Enterprise Document Management System",
        theme_color="#2196f3",
        categories=["productivity", "business"]
    )

    # Add icons
    manifest.icons = [
        PWAIcon(src="/static/images/icon-192.png", sizes="192x192"),
        PWAIcon(src="/static/images/icon-512.png", sizes="512x512")
    ]

    # Print manifest JSON
    print("Manifest:")
    print(manifest.to_json())

    # Generate service worker
    print("\nService Worker:")
    print(pwa.generate_service_worker())

    # Subscribe to push notifications
    subscription = PushSubscription(
        endpoint="https://fcm.googleapis.com/fcm/send/...",
        keys={
            "p256dh": "key1",
            "auth": "key2"
        }
    )
    pwa.subscribe_push("user123", subscription)

    print("\nPWA configuration complete!")
