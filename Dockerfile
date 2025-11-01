# Mirador AI Orchestration - Docker Container
# Includes Ollama + Mirador for self-contained deployment

FROM ubuntu:22.04

# Install dependencies
RUN apt-get update && apt-get install -y \
    curl \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Install Ollama
RUN curl -fsSL https://ollama.com/install.sh | sh

# Set working directory
WORKDIR /app

# Copy Mirador code
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

COPY src/ ./src/
COPY models/ ./models/
COPY setup.py .
COPY pyproject.toml .

# Install Mirador
RUN pip3 install -e .

# Expose ports
EXPOSE 8501  # Streamlit
EXPOSE 11434 # Ollama

# Start script
COPY docker-entrypoint.sh /
RUN chmod +x /docker-entrypoint.sh

ENTRYPOINT ["/docker-entrypoint.sh"]
CMD ["web"]
