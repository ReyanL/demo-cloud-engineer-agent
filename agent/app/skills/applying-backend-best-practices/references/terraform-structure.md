# Terraform — Structure Flat

## Organisation des fichiers

Un fichier par type de ressource logique :

```
terraform/
├── backend.tf          # Configuration du state backend (S3)
├── provider.tf         # Providers et versions requises
├── variables.tf        # Toutes les variables d'entree
├── outputs.tf          # Toutes les sorties
├── locals.tf           # Valeurs calculees
├── data.tf             # Data sources (ressources existantes)
├── iam.tf              # Roles et policies IAM
├── lambda.tf           # Fonctions Lambda
├── api_gateway.tf      # API Gateway
├── s3.tf               # Buckets S3
├── secrets.tf          # Secrets Manager
├── cloudwatch.tf       # Logs, alarmes, dashboards
└── ecr.tf              # Registres ECR
```

## Variables

Toujours specifier type, description, et valeur par defaut quand pertinent.

```hcl
variable "project" {
  description = "Nom du projet, utilise comme prefixe pour les ressources"
  type        = string
  default     = "mon-projet"
}

variable "lambda_memory_size" {
  description = "Memoire allouee a la Lambda en MB"
  type        = number
  default     = 256

  validation {
    condition     = var.lambda_memory_size >= 128 && var.lambda_memory_size <= 10240
    error_message = "La memoire Lambda doit etre entre 128 et 10240 MB."
  }
}
```

## Locals

```hcl
locals {
  account_id = data.aws_caller_identity.current.account_id
  region     = data.aws_region.current.name

  lambda_function_name = "${var.project}-webhook-handler"
  log_group_name       = "/aws/lambda/${local.lambda_function_name}"

  common_tags = {
    Project     = var.project
    Environment = var.environment
    ManagedBy   = "terraform"
  }
}
```

## Backend S3

```hcl
terraform {
  backend "s3" {
    bucket       = "mon-projet-terraform-state"
    key          = "infrastructure/terraform.tfstate"
    region       = "us-west-2"
    use_lockfile = true
  }
}
```

## A eviter

- Valeurs en dur dans les ressources au lieu de variables/locals
- State local en production
- Providers sans contrainte de version
- Outputs manquants pour les ARN/URLs necessaires
- Fichiers trop longs melangeant des types de ressources
