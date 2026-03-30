# Formulaires et Validation

## Structure accessible

```html
<form id="task-form" novalidate>
    <div class="form-group">
        <label for="task-title">Titre de la tache *</label>
        <input type="text" id="task-title" name="title"
            required minlength="3" maxlength="100"
            aria-describedby="task-title-error" aria-invalid="false">
        <span id="task-title-error" class="form-error" role="alert" hidden></span>
    </div>

    <div class="form-group">
        <label for="task-status">Statut</label>
        <select id="task-status" name="status">
            <option value="">-- Selectionner --</option>
            <option value="pending">En attente</option>
            <option value="in_progress">En cours</option>
            <option value="completed">Termine</option>
        </select>
    </div>

    <button type="submit" id="submit-btn">
        <span class="btn-text">Creer la tache</span>
        <span class="btn-loading" hidden>Creation...</span>
    </button>
</form>
```

## Validation temps reel

```javascript
class FormValidator {
    constructor(form) {
        this.form = form;
        this.isSubmitting = false;
        this.init();
    }

    init() {
        this.form.querySelectorAll('input, select, textarea').forEach(field => {
            field.addEventListener('blur', () => this.validateField(field));
            field.addEventListener('input', () => {
                if (field.getAttribute('aria-invalid') === 'true')
                    this.validateField(field);
            });
        });
        this.form.addEventListener('submit', (e) => this.handleSubmit(e));
    }

    validateField(field) {
        const errorEl = document.getElementById(`${field.id}-error`);
        if (!errorEl) return true;

        let errorMessage = '';
        if (field.validity.valueMissing) errorMessage = 'Ce champ est requis';
        else if (field.validity.tooShort) errorMessage = `Minimum ${field.minLength} caracteres`;
        else if (field.validity.patternMismatch) errorMessage = field.dataset.patternMessage || 'Format invalide';

        if (errorMessage) {
            field.setAttribute('aria-invalid', 'true');
            errorEl.textContent = errorMessage;
            errorEl.hidden = false;
            return false;
        }
        field.setAttribute('aria-invalid', 'false');
        errorEl.hidden = true;
        return true;
    }

    async handleSubmit(e) {
        e.preventDefault();
        if (this.isSubmitting) return;

        let isValid = true;
        this.form.querySelectorAll('input, select, textarea').forEach(field => {
            if (!this.validateField(field)) isValid = false;
        });

        if (!isValid) {
            this.form.querySelector('[aria-invalid="true"]')?.focus();
            return;
        }

        this.setLoading(true);
        try {
            const formData = new FormData(this.form);
            await this.submitData(Object.fromEntries(formData));
        } finally {
            this.setLoading(false);
        }
    }

    setLoading(loading) {
        this.isSubmitting = loading;
        const btn = this.form.querySelector('[type="submit"]');
        btn.disabled = loading;
        btn.querySelector('.btn-text').hidden = loading;
        btn.querySelector('.btn-loading').hidden = !loading;
    }
}
```

## A eviter

- Placeholder comme substitut de label
- Validation uniquement a la soumission
- Messages d'erreur generiques ("Erreur")
- Double soumission non geree
