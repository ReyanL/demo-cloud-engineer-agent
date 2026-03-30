# AWS Lambda — Python 3.12 avec Layers

## Structure

```
lambda_functions/
├── handlers/
│   └── webhook_handler.py      # Handler leger (point d'entree)
└── layers/
    └── common/
        └── python/
            └── lib/
                ├── utils.py
                ├── logger.py
                └── aws_clients.py
```

## Handler leger

Le handler delegue a la logique metier. Imports et clients AWS au niveau module (cold start optimization).

```python
import json
import logging
import os
import boto3

secrets_client = boto3.client("secretsmanager")
logger = logging.getLogger()
logger.setLevel(os.environ.get("LOG_LEVEL", "INFO"))


def lambda_handler(event, context):
    request_id = context.aws_request_id
    logger.info(json.dumps({
        "message": "Invocation recue",
        "request_id": request_id,
        "event_source": event.get("source", "unknown"),
    }))

    try:
        result = process_event(event)
        return {"statusCode": 200, "body": json.dumps({"message": "Succes", "request_id": request_id})}
    except ValueError as e:
        logger.warning(json.dumps({"message": "Erreur validation", "error": str(e), "request_id": request_id}))
        return {"statusCode": 400, "body": json.dumps({"error": str(e)})}
    except Exception as e:
        logger.error(json.dumps({"message": "Erreur interne", "error": str(e), "request_id": request_id}))
        return {"statusCode": 500, "body": json.dumps({"error": "Erreur interne"})}


def process_event(event):
    body = json.loads(event.get("body", "{}"))
    if not body.get("action"):
        raise ValueError("Le champ 'action' est requis")
    return {"processed": True}
```

## Layers Terraform

```hcl
resource "aws_lambda_layer_version" "common_layer" {
  filename            = data.archive_file.common_layer.output_path
  layer_name          = "${var.project}-common-layer"
  compatible_runtimes = ["python3.12"]
  description         = "Dependances partagees"
  source_code_hash    = data.archive_file.common_layer.output_base64sha256
}

resource "aws_lambda_function" "webhook_handler" {
  function_name = "${var.project}-webhook-handler"
  runtime       = "python3.12"
  handler       = "webhook_handler.lambda_handler"
  timeout       = 30
  memory_size   = 256

  layers = [aws_lambda_layer_version.common_layer.arn]

  environment {
    variables = {
      LOG_LEVEL  = "INFO"
      SECRET_ARN = aws_secretsmanager_secret.api_token.arn
    }
  }

  dead_letter_config {
    target_arn = aws_sqs_queue.lambda_dlq.arn
  }
}
```

## Idempotence

```python
def process_event(event):
    event_id = event.get("id")
    if is_already_processed(event_id):
        logger.info(json.dumps({"message": "Deja traite", "event_id": event_id}))
        return {"status": "already_processed"}
    result = do_work(event)
    mark_as_processed(event_id)
    return result
```

## Cold start optimization

- Imports au niveau module (pas dans le handler)
- Clients AWS au niveau module (reutilises entre invocations)
- Memoire suffisante (plus de memoire = plus de CPU = init plus rapide)
- Layers pour reduire la taille du package

## A eviter

- Logique metier dans le handler (difficile a tester)
- Imports a l'interieur du handler
- Timeout par defaut de 3s (trop court)
- Pas de DLQ (evenements perdus en cas d'echec)
- Secrets en clair dans les variables d'environnement
- Logging non structure (difficile a analyser dans CloudWatch)
