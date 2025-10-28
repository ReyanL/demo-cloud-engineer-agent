"""
Application initialization.

This module loads environment variables from .env for local development.
For AgentCore deployment, OTEL env vars should be passed via launch(env_vars={...}).
"""

import os
from pathlib import Path
from dotenv import load_dotenv


# Load environment variables from .env file for local development
# In AgentCore, env vars will be injected via launch configuration
env_path = Path(__file__).parent / ".env"
load_dotenv(env_path)
