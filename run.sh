#!/bin/bash

echo "🎮 Starting AI Sims..."

# Check if Ollama is running
if ! pgrep -x ollama > /dev/null; then
    echo "🤖 Starting Ollama service..."
    ollama serve &
    sleep 3
fi

# Check if the AI model is available
if ! ollama list | grep -q llama2; then
    echo "📥 Downloading AI model..."
    ollama pull llama2
fi

# Start the game
echo "🚀 Launching game..."
python3 main.py