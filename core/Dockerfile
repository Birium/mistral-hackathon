FROM python:3.12-slim

RUN apt-get update && apt-get install -y \
    curl git make g++ cmake sqlite3 \
    && curl -fsSL https://deb.nodesource.com/setup_22.x | bash - \
    && apt-get install -y nodejs \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Tell node-llama-cpp: CPU only, never attempt CUDA
ENV NODE_LLAMA_CPP_GPU=false

# Install QMD
RUN npm install -g @tobilu/qmd

# WE CAN TEST THE FOLLOWING WARMUP STEPS HERE TO TRIGGER MODEL DOWNLOADS AND BINARY BUILDS DURING IMAGE BUILD
# Pre-build the node-llama-cpp CPU binary during image build.
# This runs once here so it is baked into the image layer.
# Models are NOT downloaded here (they go to a volume-mounted path).

# RUN mkdir -p /tmp/warmup && \
#     printf '# Warmup\nThis file pre-builds the llama.cpp binary.\n' > /tmp/warmup/warmup.md && \
#     qmd collection add /tmp/warmup --name warmup && \
#     qmd update && \
#     qmd embed && \
#     qmd collection remove warmup && \
#     rm -rf /tmp/warmup

WORKDIR /app
COPY pyproject.toml .
RUN pip install uv && uv pip install --system .
COPY . .

CMD ["bash", "start.sh"]