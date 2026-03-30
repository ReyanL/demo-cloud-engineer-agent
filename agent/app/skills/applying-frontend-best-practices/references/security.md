# Securite Frontend

## Prevention XSS

Regle fondamentale : ne jamais injecter du contenu non fiable dans le DOM sans echappement.

```javascript
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Correct
element.textContent = userInput;
element.innerHTML = `<span>${escapeHtml(userInput)}</span>`;

// DANGEREUX
element.innerHTML = userInput;  // XSS directe
element.innerHTML = `<a href="${userInput}">Lien</a>`;  // XSS via href
```

## Sanitisation des URLs

```javascript
function sanitizeUrl(url) {
    try {
        const parsed = new URL(url);
        if (!['http:', 'https:'].includes(parsed.protocol)) return '#';
        return parsed.href;
    } catch {
        return '#';
    }
}

link.href = sanitizeUrl(userProvidedUrl);
```

## Tokens d'authentification

```javascript
// Preferer sessionStorage (efface a la fermeture de l'onglet)
sessionStorage.setItem('token', authToken);

// Headers centralises
class AuthenticatedApi {
    getHeaders() {
        const token = sessionStorage.getItem('token');
        return {
            'Content-Type': 'application/json',
            'Authorization': token ? `Bearer ${token}` : '',
        };
    }
}

// Nettoyage a la deconnexion
function logout() {
    sessionStorage.clear();
    window.location.href = '/login';
}
```

## Validation des inputs

```javascript
function validateInput(value, rules) {
    const errors = [];
    if (rules.required && !value.trim()) errors.push('Ce champ est requis');
    if (rules.maxLength && value.length > rules.maxLength)
        errors.push(`Maximum ${rules.maxLength} caracteres`);
    if (rules.pattern && !rules.pattern.test(value))
        errors.push(rules.patternMessage || 'Format invalide');
    return errors;
}
```

## A eviter

- `innerHTML` avec du contenu utilisateur non echappe
- Tokens dans `localStorage` (preferer `sessionStorage`)
- `eval()` ou `new Function()` avec des donnees externes
- Validation uniquement cote client (toujours valider cote serveur aussi)
