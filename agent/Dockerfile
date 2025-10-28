FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim
WORKDIR /app

# All environment variables in one layer
ENV UV_SYSTEM_PYTHON=1 \
    UV_COMPILE_BYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DOCKER_CONTAINER=1 \
    AWS_REGION=us-west-2 \
    AWS_DEFAULT_REGION=us-west-2 \
    BEDROCK_AGENTCORE_MEMORY_ID=runtime_mem-D7P6D4D73b \
    BEDROCK_AGENTCORE_MEMORY_NAME=runtime_mem


RUN apt-get update && apt-get install -y \
    git \
    curl \
    wget \
    unzip \
    gnupg \
    software-properties-common \
    && rm -rf /var/lib/apt/lists/*

RUN wget -O- https://apt.releases.hashicorp.com/gpg | gpg --dearmor -o /usr/share/keyrings/hashicorp-archive-keyring.gpg && \
    echo "deb [signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] https://apt.releases.hashicorp.com bookworm main" | tee /etc/apt/sources.list.d/hashicorp.list && \
    apt-get update && \
    apt-get install -y terraform && \
    rm -rf /var/lib/apt/lists/*

RUN curl -s https://raw.githubusercontent.com/terraform-linters/tflint/master/install_linux.sh | bash

RUN curl -sSL "https://raw.githubusercontent.com/upciti/wakemeops/main/assets/install_repository" | bash && \
    apt-get update && \
    apt-get install -y glab && \
    rm -rf /var/lib/apt/lists/*

RUN git config --global user.email "reyange.agent@devoteam.com" && git config --global user.name "Best Agent Ever"

# Copy entire project (respecting .dockerignore)
COPY . .

# Install from pyproject.toml directory
RUN cd . && uv pip install .

# Create non-root user
RUN useradd -m -u 1000 bedrock_agentcore

# Create glab config directory for non-root user
RUN mkdir -p /home/bedrock_agentcore/.config/glab-cli && \
    chown -R bedrock_agentcore:bedrock_agentcore /home/bedrock_agentcore/.config

USER bedrock_agentcore

EXPOSE 8080

# Use the full module path
CMD ["python", "-m", "runtime"]
