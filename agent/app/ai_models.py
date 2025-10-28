from botocore.config import Config
from strands.models import BedrockModel


claude_4_5_sonnet_1m_context = BedrockModel(
    model_id="global.anthropic.claude-sonnet-4-5-20250929-v1:0",
    max_tokens=64000,
    additional_request_fields={
        "anthropic_beta": ["interleaved-thinking-2025-05-14", "context-1m-2025-08-07"],
        "thinking": {"type": "enabled", "budget_tokens": 8000},
    },
    boto_client_config=Config(read_timeout=900),
)
claude_4_5_sonnet = BedrockModel(
    model_id="global.anthropic.claude-sonnet-4-5-20250929-v1:0",
    max_tokens=64000,
    additional_request_fields={"thinking": {"type": "enabled", "budget_tokens": 8000}},
    boto_client_config=Config(read_timeout=900),
)
claude_4_sonnet_1m_context = BedrockModel(
    model_id="us.anthropic.claude-sonnet-4-20250514-v1:0",
    max_tokens=64000,
    additional_request_fields={
        "anthropic_beta": ["interleaved-thinking-2025-05-14", "context-1m-2025-08-07"],
        "thinking": {"type": "enabled", "budget_tokens": 8000},
    },
    boto_client_config=Config(read_timeout=900),
)
claude_4_sonnet = BedrockModel(
    model_id="us.anthropic.claude-sonnet-4-20250514-v1:0",
    max_tokens=64000,
    additional_request_fields={
        "thinking": {"type": "enabled", "budget_tokens": 8000},
    },
    boto_client_config=Config(read_timeout=900),
)
nova_premier = BedrockModel(
    model_id="us.amazon.nova-premier-v1:0", boto_client_config=Config(read_timeout=240)
)
