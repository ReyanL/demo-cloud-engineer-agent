# Performance

## Debounce et Throttle

```javascript
function debounce(fn, delay = 300) {
    let timer;
    return (...args) => {
        clearTimeout(timer);
        timer = setTimeout(() => fn(...args), delay);
    };
}

function throttle(fn, limit = 100) {
    let inThrottle = false;
    return (...args) => {
        if (!inThrottle) {
            fn(...args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

// Utilisation
searchInput.addEventListener('input', debounce((e) => performSearch(e.target.value), 300));
window.addEventListener('scroll', throttle(() => updateScrollIndicator(), 100));
```

## Event delegation

Un seul listener au parent plutot qu'un par element enfant.

```javascript
// Correct
document.getElementById('task-list').addEventListener('click', (e) => {
    const deleteBtn = e.target.closest('[data-action="delete"]');
    if (deleteBtn) deleteTask(deleteBtn.dataset.taskId);

    const editBtn = e.target.closest('[data-action="edit"]');
    if (editBtn) editTask(editBtn.dataset.taskId);
});

// Incorrect — casse avec les listes dynamiques
document.querySelectorAll('.delete-btn').forEach(btn => {
    btn.addEventListener('click', () => deleteTask(btn.dataset.taskId));
});
```

## Optimisation DOM

```javascript
// Batch avec DocumentFragment
function renderTasks(tasks) {
    const fragment = document.createDocumentFragment();
    tasks.forEach(task => {
        const li = document.createElement('li');
        li.textContent = task.title;
        fragment.appendChild(li);
    });
    const list = document.getElementById('task-list');
    list.innerHTML = '';
    list.appendChild(fragment);
}

// Batch avec innerHTML (plus rapide pour gros volumes)
function renderTasksFast(tasks) {
    document.getElementById('task-list').innerHTML = tasks
        .map(task => `<li class="task-item">${escapeHtml(task.title)}</li>`)
        .join('');
}
```

## Lazy loading

```html
<img src="placeholder.jpg" data-src="real-image.webp" loading="lazy" alt="Description">
<link rel="preload" href="styles.css" as="style">
<link rel="prefetch" href="page2.html">
```

## A eviter

- `querySelector` dans une boucle
- Animations JS au lieu de CSS transitions
- Images non compressees ou surdimensionnees
- Listeners non nettoyes sur les elements supprimes du DOM
