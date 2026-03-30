# Structure et Organisation du Code

## Modules ES6

Organiser le code en modules avec import/export. Un fichier = une responsabilite.

```javascript
// services/api.js
export class ApiService {
    constructor(baseUrl) {
        this.baseUrl = baseUrl;
    }
    async request(endpoint, options = {}) {
        const response = await fetch(`${this.baseUrl}${endpoint}`, {
            headers: { 'Content-Type': 'application/json', ...options.headers },
            ...options,
        });
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        return response.json();
    }
}

// components/task-list.js
export class TaskList {
    constructor(container, apiService) {
        this.container = container;
        this.api = apiService;
    }
    async render() {
        const tasks = await this.api.request('/tasks');
        this.container.innerHTML = '';
        tasks.forEach(task => this.container.appendChild(this.createTaskElement(task)));
    }
}
```

## Classes ES6

Utiliser des classes pour les composants avec etat interne. Separer logique metier et rendu DOM.

```javascript
class App {
    constructor(config) {
        this.config = config;
        this.state = { tasks: [], filter: 'all' };
        this.init();
    }
    init() {
        this.bindEvents();
        this.loadData();
    }
    bindEvents() {
        document.getElementById('filter').addEventListener('change', (e) => {
            this.state.filter = e.target.value;
            this.render();
        });
    }
}
```

## Conventions de nommage

| Element | Convention | Exemple |
|---------|-----------|---------|
| Variables/Fonctions | camelCase | `getUserName()`, `isLoading` |
| Classes | PascalCase | `TaskManager`, `ApiService` |
| Constantes | UPPER_SNAKE_CASE | `MAX_RETRY_COUNT`, `API_BASE_URL` |
| Fichiers | kebab-case.js | `task-list.js`, `api-service.js` |
| IDs HTML | kebab-case | `task-list`, `login-form` |
| Classes CSS | BEM | `block__element--modifier` |

## A eviter

- `var` au lieu de `const`/`let`
- Fonctions de plus de 30 lignes
- Logique DOM melangee avec logique metier
- Variables globales non encapsulees
