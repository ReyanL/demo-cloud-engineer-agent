# Gestion d'Etat

## Pattern Observer

```javascript
class Store {
    constructor(initialState = {}) {
        this.state = initialState;
        this.listeners = new Map();
    }

    getState() {
        return { ...this.state };
    }

    setState(updates) {
        const oldState = this.state;
        this.state = { ...this.state, ...updates };
        this.notify(oldState);
    }

    subscribe(key, callback) {
        if (!this.listeners.has(key)) this.listeners.set(key, []);
        this.listeners.get(key).push(callback);
    }

    notify(oldState) {
        for (const [key, callbacks] of this.listeners) {
            if (this.state[key] !== oldState[key]) {
                callbacks.forEach(cb => cb(this.state[key], oldState[key]));
            }
        }
    }
}

// Utilisation
const store = new Store({ tasks: [], filter: 'all', isLoading: false });
store.subscribe('tasks', (tasks) => renderTaskList(tasks));
store.subscribe('filter', (filter) => updateFilterUI(filter));
store.subscribe('isLoading', (loading) => toggleSpinner(loading));

store.setState({ isLoading: true });
const tasks = await api.getTasks();
store.setState({ tasks, isLoading: false });
```

## Persistance localStorage

```javascript
const STORAGE_KEYS = {
    THEME: 'user_theme',
    FILTER: 'task_filter',
};

function savePreference(key, value) {
    try { localStorage.setItem(key, JSON.stringify(value)); }
    catch (e) { console.warn('localStorage indisponible:', e); }
}

function loadPreference(key, defaultValue) {
    try {
        const stored = localStorage.getItem(key);
        return stored ? JSON.parse(stored) : defaultValue;
    } catch { return defaultValue; }
}
```

## A eviter

- Etat disperse dans plusieurs variables globales
- Modification directe de l'etat sans notification
- Donnees sensibles (tokens) dans localStorage
- Pas de valeur par defaut pour les donnees chargees
