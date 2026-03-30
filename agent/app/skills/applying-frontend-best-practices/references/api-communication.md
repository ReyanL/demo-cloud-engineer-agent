# Communication API (Fetch)

## Service API centralise

```javascript
class ApiClient {
    constructor(baseUrl, options = {}) {
        this.baseUrl = baseUrl;
        this.timeout = options.timeout || 10000;
    }

    getAuthHeaders() {
        const token = sessionStorage.getItem('token');
        return token ? { 'Authorization': `Bearer ${token}` } : {};
    }

    async request(endpoint, options = {}) {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), this.timeout);

        try {
            const response = await fetch(`${this.baseUrl}${endpoint}`, {
                headers: {
                    'Content-Type': 'application/json',
                    ...this.getAuthHeaders(),
                    ...options.headers,
                },
                signal: controller.signal,
                ...options,
            });
            clearTimeout(timeoutId);

            if (response.status === 401) {
                sessionStorage.clear();
                window.location.href = '/login';
                throw new ApiError('Session expiree', 401);
            }
            if (!response.ok) {
                const body = await response.json().catch(() => ({}));
                throw new ApiError(body.message || `Erreur serveur (${response.status})`, response.status);
            }
            return await response.json();
        } catch (error) {
            clearTimeout(timeoutId);
            if (error.name === 'AbortError') throw new ApiError('Requete expiree (timeout)', 408);
            if (error instanceof ApiError) throw error;
            throw new ApiError('Erreur de connexion reseau', 0);
        }
    }

    async get(endpoint) { return this.request(endpoint); }
    async post(endpoint, data) {
        return this.request(endpoint, { method: 'POST', body: JSON.stringify(data) });
    }
    async put(endpoint, data) {
        return this.request(endpoint, { method: 'PUT', body: JSON.stringify(data) });
    }
    async delete(endpoint) {
        return this.request(endpoint, { method: 'DELETE' });
    }
}

class ApiError extends Error {
    constructor(message, status) {
        super(message);
        this.status = status;
        this.name = 'ApiError';
    }
}
```

## Retry avec backoff exponentiel

```javascript
async function fetchWithRetry(fn, maxRetries = 2) {
    for (let attempt = 0; attempt <= maxRetries; attempt++) {
        try { return await fn(); }
        catch (error) {
            if (attempt === maxRetries || error.status < 500) throw error;
            await new Promise(resolve => setTimeout(resolve, Math.pow(2, attempt) * 1000));
        }
    }
}
```

## Annulation des requetes obsoletes

```javascript
let currentController = null;

async function searchTasks(query) {
    if (currentController) currentController.abort();
    currentController = new AbortController();

    try {
        const results = await api.request(`/tasks?q=${encodeURIComponent(query)}`, {
            signal: currentController.signal,
        });
        renderResults(results);
    } catch (error) {
        if (error.name !== 'AbortError') showError(error.message);
    }
}
```

## A eviter

- Pas de timeout sur fetch (attente infinie)
- Pas de try/catch sur les requetes
- Token d'auth non inclus dans les headers
- Pas d'etat de chargement visible
