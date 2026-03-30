# CSS et Design Responsive

## Convention BEM

```css
/* Block */
.task-card { ... }
/* Element */
.task-card__title { ... }
.task-card__status { ... }
/* Modifier */
.task-card--completed { opacity: 0.7; }
.task-card__status--urgent { color: var(--color-danger); }
```

## CSS Custom Properties

```css
:root {
    --color-primary: #4A90D9;
    --color-primary-hover: #357ABD;
    --color-danger: #E74C3C;
    --color-success: #2ECC71;
    --color-text: #333333;
    --color-bg: #FFFFFF;

    --font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    --font-size-base: 1rem;
    --font-size-sm: 0.875rem;
    --font-size-lg: 1.25rem;

    --spacing-xs: 0.25rem;
    --spacing-sm: 0.5rem;
    --spacing-md: 1rem;
    --spacing-lg: 1.5rem;
    --spacing-xl: 2rem;

    --border-radius: 8px;
    --shadow-sm: 0 1px 3px rgba(0, 0, 0, 0.1);
    --shadow-md: 0 4px 6px rgba(0, 0, 0, 0.1);
}
```

## Responsive mobile-first

```css
/* Base : mobile */
.dashboard {
    display: grid;
    grid-template-columns: 1fr;
    gap: var(--spacing-md);
    padding: var(--spacing-md);
}

/* Tablette : 768px+ */
@media (min-width: 768px) {
    .dashboard {
        grid-template-columns: repeat(2, 1fr);
        padding: var(--spacing-lg);
    }
}

/* Desktop : 1024px+ */
@media (min-width: 1024px) {
    .dashboard {
        grid-template-columns: repeat(3, 1fr);
        max-width: 1200px;
        margin: 0 auto;
    }
}
```

## Grid vs Flexbox

```css
/* Grid — layouts 2D */
.card-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    gap: var(--spacing-md);
}

/* Flexbox — alignement 1D */
.card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: var(--spacing-sm);
}
```

## Animations CSS

```css
.button {
    transition: background-color 0.2s ease, transform 0.1s ease;
}
.button:hover { background-color: var(--color-primary-hover); }
.button:active { transform: scale(0.98); }

@keyframes slideIn {
    from { opacity: 0; transform: translateY(-10px); }
    to { opacity: 1; transform: translateY(0); }
}
.notification { animation: slideIn 0.3s ease-out; }
```

## A eviter

- `!important` pour resoudre des conflits — revoir la specificite
- Pixels fixes pour le texte — utiliser rem/em
- Desktop-first puis casser le layout mobile
- Selecteurs trop profonds (`.page .section .list .item .btn`)
