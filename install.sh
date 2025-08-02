#!/bin/bash

echo "🎮 AI Sims - Installation Script"
echo "================================"

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    echo "Please install Python 3.8+ and try again."
    exit 1
fi

echo "✅ Python found: $(python3 --version)"

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 is required but not installed."
    echo "Please install pip3 and try again."
    exit 1
fi

echo "✅ pip3 found"

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip3 install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "❌ Failed to install Python dependencies"
    exit 1
fi

echo "✅ Python dependencies installed"

# Check if Ollama is installed
if ! command -v ollama &> /dev/null; then
    echo "🤖 Ollama not found. Installing Ollama..."
    
    # Detect OS and install accordingly
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        curl -fsSL https://ollama.com/install.sh | sh
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        if command -v brew &> /dev/null; then
            brew install ollama
        else
            echo "❌ Please install Homebrew first, then run: brew install ollama"
            exit 1
        fi
    else
        echo "❌ Unsupported OS. Please install Ollama manually from https://ollama.com"
        exit 1
    fi
    
    if [ $? -ne 0 ]; then
        echo "❌ Failed to install Ollama"
        exit 1
    fi
    
    echo "✅ Ollama installed"
else
    echo "✅ Ollama found: $(ollama --version)"
fi

# Start Ollama service (if not running)
echo "🚀 Starting Ollama service..."
ollama serve &
OLLAMA_PID=$!
sleep 3

# Pull the default model
echo "📥 Downloading AI model (this may take a few minutes)..."
ollama pull llama2

if [ $? -ne 0 ]; then
    echo "❌ Failed to download AI model"
    kill $OLLAMA_PID 2>/dev/null
    exit 1
fi

echo "✅ AI model downloaded"

# Create necessary directories
echo "📁 Creating game directories..."
mkdir -p chroma_db
mkdir -p assets/sprites
mkdir -p assets/maps

echo "✅ Game directories created"

# Set up environment file
if [ ! -f .env ]; then
    echo "⚙️ Setting up environment configuration..."
    cp .env.example .env 2>/dev/null || echo "Warning: .env.example not found, using default .env"
    echo "✅ Environment configuration ready"
fi

echo ""
echo "🎉 Installation Complete!"
echo "========================"
echo ""
echo "🎮 To start the game, run:"
echo "   python3 main.py"
echo ""
echo "🔧 Optional: Add API keys to .env file for fallback AI providers"
echo "📖 See README.md for more configuration options"
echo ""

# Keep Ollama running in background
echo "💡 Tip: Ollama is running in the background (PID: $OLLAMA_PID)"
echo "    Kill it with: kill $OLLAMA_PID"