# Terraform — Validation et Correction d'Erreurs

## Sequence obligatoire

Ne jamais passer a l'etape suivante si la precedente echoue.

```
1. terraform_init     -> Initialise backend + providers. DOIT reussir.
2. tflint             -> Lint et auto-correction HCL
3. RunCheckovScan     -> Scan securite. Corriger critiques/high.
4. terraform validate -> Validation syntaxique
5. terraform_plan     -> Plan d'execution. DOIT reussir avant push.
```

## Strategie de correction

Quand une etape echoue :

1. **Analyser** : lire stdout et stderr
2. **Identifier** la cause racine (voir tableau ci-dessous)
3. **Rechercher** : utiliser SearchAwsProviderDocs si necessaire
4. **Corriger** : modifier les fichiers avec file_write
5. **Relancer** depuis l'etape en echec
6. **Iterer** jusqu'a ce que toutes les etapes reussissent

## Erreurs courantes par etape

### terraform init

| Erreur | Cause | Action |
|--------|-------|--------|
| Failed to get existing workspaces | Credentials/permissions S3 | Verifier backend.tf et IAM |
| Failed to query available provider packages | Conflit de version | Mettre a jour contrainte dans provider.tf |
| Cached package has no files | Cache corrompu | Supprimer .terraform, relancer init |

### Checkov (findings frequents)

| Finding | Action |
|---------|--------|
| CKV_AWS_117: Lambda inside VPC | Ajouter vpc_config si acces ressources privees, sinon justifier |
| CKV_AWS_116: Lambda DLQ | Ajouter dead_letter_config (SNS ou SQS) |
| CKV_AWS_272: Lambda code signing | Ajouter code_signing_config_arn si requis |
| CKV_AWS_173: Lambda env vars encrypted | Ajouter kms_key_arn |

### terraform plan

| Erreur | Cause | Action |
|--------|-------|--------|
| Already exists | Ressource pre-existante | Importer ou renommer |
| Unsupported attribute | Version provider | Verifier docs provider |
| UnauthorizedOperation | Permissions IAM | Verifier profil utilise |
| Cycle detected | Dependance circulaire | Revoir references entre ressources |
| Missing variable | Variable non declaree | Ajouter dans variables.tf |

## Important

- Toujours utiliser `get_repository_path` pour le chemin correct du repo clone
- Ne JAMAIS push sans que terraform plan ait reussi
- Warnings Checkov low/medium : noter mais ne bloquent pas
