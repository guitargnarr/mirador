#!/bin/bash

# Start Ollama in background
ollama serve &
OLLAMA_PID=$!

# Wait for Ollama to be ready
echo "Waiting for Ollama to start..."
until curl -s http://localhost:11434/api/tags > /dev/null; do
    sleep 1
done
echo "Ollama ready!"

# Pull default models if none exist
MODEL_COUNT=$(curl -s http://localhost:11434/api/tags | grep -o '"name"' | wc -l)
if [ "$MODEL_COUNT" -lt 1 ]; then
    echo "Pulling default model (llama3.2)..."
    ollama pull llama3.2
fi

# Execute command
if [ "$1" = "web" ]; then
    echo "Starting Streamlit web UI..."
    streamlit run src/mirador/web/app.py --server.port=8501 --server.address=0.0.0.0
elif [ "$1" = "cli" ]; then
    exec mirador "${@:2}"
else
    exec "$@"
fi
