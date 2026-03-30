---
name: applying-backend-best-practices
description: Fournit les bonnes pratiques Terraform (structure flat, conventions de nommage, validation Checkov/tflint/plan), Lambda Python 3.12 avec Layers, securite AWS (Well-Architected Framework, IAM moindre privilege, chiffrement) et observabilite (CloudWatch, X-Ray, structured logging). S'active lors de la generation ou modification de code backend (HCL, Lambda Python, policies IAM, CloudWatch).
allowed-tools: file_read file_write terraform_init terraform_plan
---

# Bonnes Pratiques Backend — Terraform, Lambda, Securite, Observabilite

## Checklist rapide

Avant de finaliser du code backend, verifier :

```
Checklist Backend :
- [ ] Terraform structure : un fichier par type de ressource, variables.tf/outputs.tf/locals.tf
- [ ] Terraform nommage : snake_case (HCL), prefixe projet avec tirets (noms AWS), tags obligatoires
- [ ] Terraform validation : init -> tflint -> Checkov -> validate -> plan (tout doit passer)
- [ ] Lambda : Python 3.12, Layers pour dependances, handler leger, idempotent
- [ ] Lambda : structured logging JSON, DLQ, timeout et memoire dimensionnes
- [ ] Securite : IAM moindre privilege (pas de *), chiffrement repos+transit, secrets dans Secrets Manager
- [ ] Observabilite : CloudWatch Logs avec retention, alarmes erreurs/throttling/latence, X-Ray
```

## Quand consulter les references

| Contexte de travail | Reference |
|---------------------|-----------|
| Organisation fichiers Terraform, variables, locals | [references/terraform-structure.md](references/terraform-structure.md) |
| Noms de ressources, tags, conventions | [references/terraform-naming.md](references/terraform-naming.md) |
| Erreurs terraform init/plan, Checkov findings | [references/terraform-validation.md](references/terraform-validation.md) |
| Fonctions Lambda, Layers, cold start, idempotence | [references/lambda.md](references/lambda.md) |
| IAM, chiffrement, VPC, Well-Architected | [references/security.md](references/security.md) |
| CloudWatch, alarmes, X-Ray, structured logging | [references/observability.md](references/observability.md) |

## Workflow de validation Terraform

Sequence obligatoire apres implementation, a relancer depuis l'etape en echec :

```
1. terraform_init       -> DOIT reussir
2. tflint               -> Lint et auto-correction
3. RunCheckovScan       -> Corriger critiques/high
4. terraform validate   -> Validation syntaxique
5. terraform_plan       -> DOIT reussir avant push
```

Si une etape echoue : analyser l'erreur, consulter [references/terraform-validation.md](references/terraform-validation.md), corriger, relancer depuis l'etape en echec.

## Conventions du projet

- Terraform >= 1.12, AWS provider ~> 6.0, structure flat
- Lambda Python 3.12 avec Layers
- Backend S3 avec state locking
- Tags obligatoires : Project, Environment, ManagedBy=terraform
- Noms AWS : `${var.project}-resource-name`
