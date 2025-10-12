/**
 * GMAO PWA Service Worker
 * Maneja cache offline, notificaciones push y actualizaciones
 */

const CACHE_NAME = "gmao-pwa-v1.0.0";
const CACHE_VERSION = "1.0.0";

// Recursos críticos para cache
const CORE_CACHE_RESOURCES = [
  "/",
  "/dashboard",
  "/static/manifest.json",
  "/static/css/style.css",
  "/static/css/no-rounded.css",
  "/static/js/main.js",
  "/static/js/pwa-register.js",
  "https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css",
  "https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js",
  "https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.0/font/bootstrap-icons.css",
];

// Recursos de la aplicación
const APP_CACHE_RESOURCES = [
  "/alertas/",
  "/inventario",
  "/static/js/csrf-utils.js",
  "/static/js/accessibility.js",
  "/static/js/autocomplete.js",
  "/static/js/confirmation-modal.js",
];

// APIs para cache con estrategia especial
const API_CACHE_PATTERNS = [
  "/alertas/api/kpis/dashboard",
  "/alertas/api/historial/",
  "/alertas/api/configuracion/",
  "/api/v2/",
];

// =============================================================================
// EVENTOS DEL SERVICE WORKER
// =============================================================================

self.addEventListener("install", (event) => {
  console.log("SW: Instalando Service Worker v" + CACHE_VERSION);

  event.waitUntil(
    (async () => {
      try {
        const cache = await caches.open(CACHE_NAME);

        // Cache recursos críticos
        console.log("SW: Cacheando recursos críticos...");
        await cache.addAll(
          CORE_CACHE_RESOURCES.map(
            (url) =>
              new Request(url, {
                cache: "reload",
              })
          )
        );

        // Cache recursos de aplicación (con manejo de errores)
        console.log("SW: Cacheando recursos de aplicación...");
        for (const resource of APP_CACHE_RESOURCES) {
          try {
            await cache.add(new Request(resource, { cache: "reload" }));
          } catch (error) {
            console.warn("SW: No se pudo cachear:", resource, error);
          }
        }

        console.log("SW: Instalación completada");
        self.skipWaiting(); // Activar inmediatamente
      } catch (error) {
        console.error("SW: Error durante la instalación:", error);
      }
    })()
  );
});

self.addEventListener("activate", (event) => {
  console.log("SW: Activando Service Worker v" + CACHE_VERSION);

  event.waitUntil(
    (async () => {
      try {
        // Limpiar caches antiguos
        const cacheNames = await caches.keys();
        const deletePromises = cacheNames
          .filter((cacheName) => cacheName !== CACHE_NAME)
          .map((cacheName) => {
            console.log("SW: Eliminando cache antigua:", cacheName);
            return caches.delete(cacheName);
          });

        await Promise.all(deletePromises);

        // Tomar control de todas las pestañas
        await self.clients.claim();

        console.log("SW: Activación completada");
      } catch (error) {
        console.error("SW: Error durante la activación:", error);
      }
    })()
  );
});

self.addEventListener("fetch", (event) => {
  event.respondWith(handleFetch(event.request));
});

// =============================================================================
// ESTRATEGIAS DE CACHE
// =============================================================================

async function handleFetch(request) {
  const url = new URL(request.url);

  try {
    // 1. Recursos estáticos - Cache First
    if (isStaticResource(url)) {
      return await cacheFirst(request);
    }

    // 2. APIs de alertas - Network First con fallback
    if (isAlertsAPI(url)) {
      return await networkFirstWithCache(request);
    }

    // 3. Páginas HTML - Stale While Revalidate
    if (isHTMLPage(url)) {
      return await staleWhileRevalidate(request);
    }

    // 4. APIs externas - Network Only
    if (isExternalAPI(url)) {
      return await networkOnly(request);
    }

    // 5. Default - Network First
    return await networkFirst(request);
  } catch (error) {
    console.error("SW: Error en fetch:", error);
    return await handleFetchError(request, error);
  }
}

// Cache First: Para recursos estáticos
async function cacheFirst(request) {
  const cachedResponse = await caches.match(request);
  if (cachedResponse) {
    return cachedResponse;
  }

  try {
    const networkResponse = await fetch(request);
    if (networkResponse.ok) {
      const cache = await caches.open(CACHE_NAME);
      await cache.put(request, networkResponse.clone());
    }
    return networkResponse;
  } catch (error) {
    console.warn("SW: Network falló para recurso estático:", request.url);
    throw error;
  }
}

// Network First con Cache: Para APIs importantes
async function networkFirstWithCache(request) {
  try {
    const networkResponse = await fetch(request);
    if (networkResponse.ok) {
      const cache = await caches.open(CACHE_NAME);
      await cache.put(request, networkResponse.clone());
    }
    return networkResponse;
  } catch (error) {
    console.log("SW: Red no disponible, usando cache para:", request.url);
    const cachedResponse = await caches.match(request);
    if (cachedResponse) {
      return cachedResponse;
    }
    throw error;
  }
}

// Stale While Revalidate: Para páginas HTML
async function staleWhileRevalidate(request) {
  const cachedResponse = await caches.match(request);
  const networkPromise = fetch(request).then((response) => {
    if (response.ok) {
      const cache = caches.open(CACHE_NAME);
      cache.then((c) => c.put(request, response.clone()));
    }
    return response;
  });

  return cachedResponse || networkPromise;
}

// Network First: Para recursos dinámicos
async function networkFirst(request) {
  try {
    return await fetch(request);
  } catch (error) {
    const cachedResponse = await caches.match(request);
    if (cachedResponse) {
      return cachedResponse;
    }
    throw error;
  }
}

// Network Only: Para APIs externas
async function networkOnly(request) {
  return await fetch(request);
}

// =============================================================================
// FUNCIONES DE UTILIDAD
// =============================================================================

function isStaticResource(url) {
  return (
    url.pathname.match(/\.(css|js|png|jpg|jpeg|svg|ico|woff|woff2)$/) ||
    url.hostname.includes("cdn.jsdelivr.net") ||
    url.pathname.startsWith("/static/")
  );
}

function isAlertsAPI(url) {
  return url.pathname.startsWith("/alertas/api/");
}

function isHTMLPage(url) {
  return (
    url.pathname === "/" ||
    url.pathname.startsWith("/dashboard") ||
    url.pathname.startsWith("/alertas/") ||
    url.pathname.startsWith("/inventario")
  );
}

function isExternalAPI(url) {
  return (
    url.hostname !== self.location.hostname &&
    !url.hostname.includes("cdn.jsdelivr.net")
  );
}

async function handleFetchError(request, error) {
  // Para páginas HTML, devolver una página offline
  if (isHTMLPage(new URL(request.url))) {
    return await getOfflinePage();
  }

  // Para APIs, devolver respuesta de error estructurada
  if (request.url.includes("/api/")) {
    return new Response(
      JSON.stringify({
        error: "Sin conexión",
        message: "No se puede conectar al servidor",
        offline: true,
      }),
      {
        status: 503,
        headers: { "Content-Type": "application/json" },
      }
    );
  }

  throw error;
}

async function getOfflinePage() {
  const offlineHTML = `
        <!DOCTYPE html>
        <html lang="es">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Sin conexión - GMAO</title>
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
            <style>
                .offline-container {
                    min-height: 100vh;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    text-align: center;
                }
                .offline-icon {
                    font-size: 4rem;
                    color: #6c757d;
                    margin-bottom: 1rem;
                }
            </style>
        </head>
        <body>
            <div class="offline-container">
                <div>
                    <div class="offline-icon">📡</div>
                    <h1>Sin conexión</h1>
                    <p class="text-muted">No se puede conectar al servidor.</p>
                    <button class="btn btn-primary" onclick="window.location.reload()">
                        Reintentar
                    </button>
                </div>
            </div>
        </body>
        </html>
    `;

  return new Response(offlineHTML, {
    headers: { "Content-Type": "text/html" },
  });
}

// =============================================================================
// NOTIFICACIONES PUSH
// =============================================================================

self.addEventListener("push", (event) => {
  console.log("SW: Notificación push recibida");

  let data = {};
  if (event.data) {
    try {
      data = event.data.json();
    } catch (error) {
      data = { title: "GMAO", body: event.data.text() };
    }
  }

  const options = {
    title: data.title || "GMAO - Nueva Alerta",
    body: data.body || "Tienes una nueva notificación",
    icon: "/static/icons/icon-192x192.svg",
    badge: "/static/icons/icon-72x72.svg",
    tag: data.tag || "gmao-notification",
    data: data.data || {},
    actions: [
      {
        action: "view",
        title: "Ver",
        icon: "/static/icons/view-icon.svg",
      },
      {
        action: "close",
        title: "Cerrar",
      },
    ],
    vibrate: [200, 100, 200],
    requireInteraction: data.priority === "alta" || data.priority === "critica",
  };

  event.waitUntil(self.registration.showNotification(options.title, options));
});

self.addEventListener("notificationclick", (event) => {
  console.log("SW: Click en notificación:", event.action);

  event.notification.close();

  if (event.action === "close") {
    return;
  }

  // Determinar URL basada en la acción
  let targetUrl = "/dashboard";
  if (event.notification.data && event.notification.data.url) {
    targetUrl = event.notification.data.url;
  } else if (
    event.action === "view" &&
    event.notification.tag.includes("alert")
  ) {
    targetUrl = "/alertas/";
  }

  event.waitUntil(
    clients
      .matchAll({ type: "window", includeUncontrolled: true })
      .then((clientList) => {
        // Buscar ventana ya abierta
        for (const client of clientList) {
          if (client.url.includes(targetUrl) && "focus" in client) {
            return client.focus();
          }
        }

        // Abrir nueva ventana
        if (clients.openWindow) {
          return clients.openWindow(targetUrl);
        }
      })
  );
});

// =============================================================================
// SINCRONIZACIÓN EN BACKGROUND
// =============================================================================

self.addEventListener("sync", (event) => {
  console.log("SW: Evento de sincronización:", event.tag);

  if (event.tag === "background-sync-alerts") {
    event.waitUntil(syncAlerts());
  }
});

async function syncAlerts() {
  try {
    console.log("SW: Sincronizando alertas en background...");

    const response = await fetch("/alertas/api/kpis/dashboard");
    if (response.ok) {
      const data = await response.json();

      // Guardar en cache
      const cache = await caches.open(CACHE_NAME);
      await cache.put(
        "/alertas/api/kpis/dashboard",
        new Response(JSON.stringify(data))
      );

      // Notificar a clientes sobre nuevos datos
      const clients = await self.clients.matchAll();
      clients.forEach((client) => {
        client.postMessage({
          type: "ALERTS_UPDATED",
          data: data,
        });
      });
    }
  } catch (error) {
    console.error("SW: Error sincronizando alertas:", error);
  }
}

// =============================================================================
// EVENTOS DE MENSAJE
// =============================================================================

self.addEventListener("message", (event) => {
  console.log("SW: Mensaje recibido:", event.data);

  if (event.data && event.data.type) {
    switch (event.data.type) {
      case "SKIP_WAITING":
        self.skipWaiting();
        break;

      case "GET_VERSION":
        event.ports[0].postMessage({ version: CACHE_VERSION });
        break;

      case "CLEAR_CACHE":
        clearAllCaches().then(() => {
          event.ports[0].postMessage({ success: true });
        });
        break;
    }
  }
});

async function clearAllCaches() {
  const cacheNames = await caches.keys();
  return Promise.all(cacheNames.map((name) => caches.delete(name)));
}

console.log("SW: Service Worker GMAO v" + CACHE_VERSION + " cargado");
