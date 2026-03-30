# Observabilite (Logging, Monitoring, Tracing)

## Structured logging JSON

```python
import json
import logging
import os

logger = logging.getLogger()
logger.setLevel(os.environ.get("LOG_LEVEL", "INFO"))

def log_event(level, message, **kwargs):
    log_entry = {"message": message, "level": level, **kwargs}
    getattr(logger, level.lower())(json.dumps(log_entry))

# Utilisation
log_event("INFO", "Traitement webhook", event_type="issue", project="demo-app")
log_event("ERROR", "Echec invocation agent", error="timeout", agent_arn="arn:...")
```

Requete CloudWatch Insights :
```
fields @timestamp, message, level, error
| filter level = "ERROR"
| sort @timestamp desc
| limit 50
```

## CloudWatch Terraform

```hcl
# Log group avec retention
resource "aws_cloudwatch_log_group" "lambda" {
  name              = "/aws/lambda/${aws_lambda_function.handler.function_name}"
  retention_in_days = var.log_retention_days
}

# Alarme erreurs Lambda
resource "aws_cloudwatch_metric_alarm" "lambda_errors" {
  alarm_name          = "${var.project}-lambda-errors"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 1
  metric_name         = "Errors"
  namespace           = "AWS/Lambda"
  period              = 300
  statistic           = "Sum"
  threshold           = 5
  alarm_description   = "Lambda errors > 5 in 5 minutes"
  dimensions          = { FunctionName = aws_lambda_function.handler.function_name }
  alarm_actions       = [aws_sns_topic.alerts.arn]
}

# Alarme throttling Lambda
resource "aws_cloudwatch_metric_alarm" "lambda_throttles" {
  alarm_name          = "${var.project}-lambda-throttles"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 1
  metric_name         = "Throttles"
  namespace           = "AWS/Lambda"
  period              = 300
  statistic           = "Sum"
  threshold           = 0
  dimensions          = { FunctionName = aws_lambda_function.handler.function_name }
  alarm_actions       = [aws_sns_topic.alerts.arn]
}

# Alarme latence API Gateway
resource "aws_cloudwatch_metric_alarm" "api_latency" {
  alarm_name          = "${var.project}-api-latency"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "Latency"
  namespace           = "AWS/ApiGateway"
  period              = 300
  statistic           = "p90"
  threshold           = 5000
  dimensions          = { ApiName = aws_api_gateway_rest_api.webhook.name }
  alarm_actions       = [aws_sns_topic.alerts.arn]
}
```

## X-Ray

```hcl
resource "aws_lambda_function" "handler" {
  tracing_config { mode = "Active" }
}

resource "aws_api_gateway_stage" "prod" {
  xray_tracing_enabled = true
}
```

## Niveaux de log

- **DEBUG** : Details de debogage, payloads (desactive en prod)
- **INFO** : Evenements normaux (invocation recue, traitement termine)
- **WARNING** : Situations anormales mais gerees (retry, fallback)
- **ERROR** : Echecs necessitant une attention

## A ne JAMAIS logger

```python
logger.info(f"Token: {secret_token}")         # Secrets
logger.info(f"Password: {user_password}")     # Credentials
logger.info(f"Payload: {full_request_body}")  # Donnees personnelles
```

## A eviter

- Pas de retention configuree (logs infinis = couts)
- Logging non structure (difficile a requeter dans CloudWatch Insights)
- Donnees sensibles dans les logs
- Pas d'alarmes (decouverte des problemes par les utilisateurs)
- X-Ray non active (impossible de tracer les requetes distribuees)
