# Accessibilite (WCAG AA)

## HTML semantique

```html
<header>
    <nav aria-label="Navigation principale">
        <ul>
            <li><a href="#tasks">Taches</a></li>
        </ul>
    </nav>
</header>
<main id="main-content">
    <section aria-labelledby="tasks-heading">
        <h2 id="tasks-heading">Mes Taches</h2>
    </section>
</main>
<footer>...</footer>
```

Jamais de `<div class="header">` quand `<header>` existe.

## Focus visible

```css
:focus-visible {
    outline: 2px solid #4A90D9;
    outline-offset: 2px;
}

button:focus-visible,
a:focus-visible,
input:focus-visible {
    box-shadow: 0 0 0 4px rgba(74, 144, 217, 0.3);
}
```

Ne JAMAIS supprimer `outline` sans alternative visible.

## Modales accessibles

```javascript
function openModal(modal) {
    modal.setAttribute('aria-hidden', 'false');
    modal.style.display = 'flex';
    const firstFocusable = modal.querySelector('button, input, [tabindex="0"]');
    if (firstFocusable) firstFocusable.focus();

    modal.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') closeModal(modal);
        if (e.key === 'Tab') trapFocus(e, modal);
    });
}
```

## Contenu dynamique

```html
<div aria-live="polite" aria-atomic="true" class="sr-only" id="notifications"></div>
```

```javascript
function showNotification(message) {
    document.getElementById('notifications').textContent = message;
}
```

## Contraste (WCAG AA)

- Texte normal (< 18px) : ratio minimum **4.5:1**
- Grand texte (>= 18px bold ou >= 24px) : ratio minimum **3:1**
- Elements interactifs : ratio minimum **3:1**
- Ne pas utiliser la couleur seule pour transmettre l'information

## Mouvement reduit

```css
@media (prefers-reduced-motion: reduce) {
    *, *::before, *::after {
        animation-duration: 0.01ms !important;
        transition-duration: 0.01ms !important;
    }
}
```

## A eviter

- `outline: none` sans alternative
- Images sans `alt` (utiliser `alt=""` pour les decoratives)
- `placeholder` comme substitut de `<label>`
- Contenu accessible uniquement au survol souris
- `<div>` cliquables au lieu de `<button>` ou `<a>`
