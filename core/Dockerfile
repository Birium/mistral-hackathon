FROM python:3.12-slim

# Tell node-llama-cpp to skip CUDA entirely, go straight to CPU
ENV NODE_LLAMA_CPP_GPU=false

RUN apt-get update && apt-get install -y \
    curl \
    git \
    make \
    g++ \
    cmake \
    sqlite3 \
    && curl -fsSL https://deb.nodesource.com/setup_22.x | bash - \
    && apt-get install -y nodejs \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Install QMD — llama.cpp builds from source here, during docker build
RUN npm install -g @tobilu/qmd

WORKDIR /app
COPY pyproject.toml .
RUN pip install uv && uv pip install --system .
COPY . .

CMD ["bash", "start.sh"]