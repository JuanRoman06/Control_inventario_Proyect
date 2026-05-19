const CACHE_NAME = "dulceria-inventario-v2";
const APP_SHELL = [
    "./",
    "./index.html",
    "./css/style.css",
    "./js/app.js",
    "./manifest.webmanifest",
    "./icons/app-icon.svg"
];

self.addEventListener("install", event => {
    event.waitUntil(
        caches.open(CACHE_NAME).then(cache => cache.addAll(APP_SHELL))
    );
    self.skipWaiting();
});

self.addEventListener("activate", event => {
    event.waitUntil(
        caches.keys().then(keys => Promise.all(
            keys
                .filter(key => key !== CACHE_NAME)
                .map(key => caches.delete(key))
        ))
    );
    self.clients.claim();
});

self.addEventListener("fetch", event => {
    const request = event.request;
    const url = new URL(request.url);
    const cacheableDestinations = ["document", "style", "script", "image", "manifest"];

    if (
        request.method !== "GET" ||
        url.origin !== self.location.origin ||
        !cacheableDestinations.includes(request.destination)
    ) {
        return;
    }

    event.respondWith(
        fetch(request)
            .then(response => {
                const copy = response.clone();

                if (response.ok) {
                    caches.open(CACHE_NAME).then(cache => cache.put(request, copy));
                }

                return response;
            })
            .catch(() => {
                return caches.match(request)
                    .then(cached => cached || caches.match("./index.html"));
            })
    );
});
