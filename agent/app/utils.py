"""Shared utilities for cloud engineer agents."""

import os
from .constants import models_cost_per_1000_tokens

# Configure environment for autonomous operation
os.environ["BYPASS_TOOL_CONSENT"] = "true"


def estimate_inference_cost(
    input_tokens: int, output_tokens: int, model_name: str
) -> float:
    """Estimate the inference cost of a model.

    Args:
        input_tokens: The number of input tokens
        output_tokens: The number of output tokens
        model_name: The name of the model

    Returns:
        The estimated inference cost of the model
    """
    estimated_cost = (input_tokens / 1000) * models_cost_per_1000_tokens[model_name][
        "input"
    ] + (output_tokens / 1000) * models_cost_per_1000_tokens[model_name]["output"]
    print(
        f"Estimated cost: {estimated_cost} USD, you used {input_tokens} input tokens and {output_tokens} output tokens with the {model_name} model"
    )
    return estimated_cost
