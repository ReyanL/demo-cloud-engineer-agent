---
name: applying-frontend-best-practices
description: Fournit les bonnes pratiques Vanilla JavaScript ES6+, HTML5 et CSS3 pour le projet demo-app. Couvre la structure du code, l'accessibilite WCAG AA, la performance, la securite XSS, le CSS responsive (BEM, Grid, Flexbox), la gestion d'etat, les formulaires et la communication API Fetch. S'active lors de la generation ou modification de fichiers frontend (JS, HTML, CSS).
allowed-tools: file_read file_write
---

# Bonnes Pratiques Frontend — Vanilla JS / HTML5 / CSS3

## Checklist rapide

Avant de finaliser du code frontend, verifier :

```
Checklist Frontend :
- [ ] Structure : modules ES6, const/let (jamais var), une responsabilite par fonction
- [ ] Accessibilite : HTML semantique, WCAG AA (contraste 4.5:1), focus visible, labels
- [ ] Performance : event delegation, debounce/throttle, batch DOM updates
- [ ] Securite : echappement XSS (textContent, pas innerHTML brut), validation inputs
- [ ] CSS : BEM, mobile-first, CSS variables, rem/em (pas px pour texte)
- [ ] Formulaires : labels + aria-describedby, validation temps reel, anti double-submit
- [ ] API : async/await, timeout, gestion erreurs centralisee, etats de chargement
```

## Quand consulter les references

| Contexte de travail | Reference |
|---------------------|-----------|
| Organisation du code, modules, classes | [references/structure.md](references/structure.md) |
| WCAG AA, ARIA, navigation clavier | [references/accessibility.md](references/accessibility.md) |
| Optimisation chargement, DOM, events | [references/performance.md](references/performance.md) |
| Prevention XSS, tokens, validation | [references/security.md](references/security.md) |
| BEM, responsive, Grid/Flexbox, animations | [references/css.md](references/css.md) |
| State centralize, Observer, localStorage | [references/state-management.md](references/state-management.md) |
| Formulaires accessibles, validation | [references/forms.md](references/forms.md) |
| Fetch API, retry, annulation, erreurs | [references/api-communication.md](references/api-communication.md) |

## Conventions du projet

- Stack : Vanilla JS ES6+, HTML5, CSS3, Font Awesome 6 (CDN)
- Pas de framework, pas de build tools, pas de TypeScript
- Deploiement statique sur S3
- Authentification via AWS Cognito (Bearer token)
- Nommage : camelCase (variables/fonctions), PascalCase (classes), BEM (CSS)
