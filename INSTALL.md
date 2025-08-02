# AI Sims - Installation Guide

## 🚀 Quick Install (Recommended)

### Automatic Installation
```bash
# Make the installer executable and run it
chmod +x install.sh
./install.sh
```

The installer will:
- ✅ Check Python and pip
- ✅ Install all Python dependencies
- ✅ Install and configure Ollama
- ✅ Download the AI model (llama2)
- ✅ Create necessary directories
- ✅ Set up configuration

### Start the Game
```bash
./run.sh
# OR
python3 main.py
```

---

## 🔧 Manual Installation

### 1. Prerequisites
- **Python 3.8+** 
- **pip3**

### 2. Install Python Dependencies
```bash
pip3 install -r requirements.txt
```

### 3. Install Ollama

**Linux:**
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

**macOS:**
```bash
brew install ollama
```

**Windows:**
Download from [ollama.com](https://ollama.com) and follow installer

### 4. Download AI Model
```bash
# Start Ollama service
ollama serve

# In another terminal, download model
ollama pull llama2
```

### 5. Create Directories
```bash
mkdir -p chroma_db assets/sprites assets/maps
```

### 6. Configure Environment
```bash
cp .env.example .env
# Edit .env if you want to add API keys for fallback
```

---

## 🐳 Docker Installation

### Using Docker Compose
```bash
# Build and run
docker-compose up --build

# For X11 forwarding on Linux
xhost +local:docker
docker-compose up --build
```

### Using Docker directly
```bash
# Build image
docker build -t ai-sims .

# Run container
docker run -it --rm \
  -v /tmp/.X11-unix:/tmp/.X11-unix \
  -e DISPLAY=$DISPLAY \
  ai-sims
```

---

## ⚙️ Configuration Options

### API Keys (Optional)
Add to `.env` file for AI fallback when Ollama is slow:

```env
OPENAI_API_KEY=your_openai_key_here
ANTHROPIC_API_KEY=your_anthropic_key_here
```

### Performance Tuning
```env
OLLAMA_TIMEOUT=5.0              # Seconds before API fallback
AI_DECISION_COOLDOWN_MIN=2.0    # Min time between AI decisions
AI_DECISION_COOLDOWN_MAX=5.0    # Max time between AI decisions
```

### Model Selection
```env
OLLAMA_MODEL=llama2             # Primary local model
OPENAI_MODEL=gpt-3.5-turbo      # Fallback model
ANTHROPIC_MODEL=claude-3-haiku-20240307  # Backup model
```

---

## 🚨 Troubleshooting

### Common Issues

**"ollama: command not found"**
- Restart terminal after Ollama installation
- Or run: `export PATH=$PATH:/usr/local/bin`

**"Failed to connect to Ollama"**
- Start Ollama service: `ollama serve`
- Check if port 11434 is available: `lsof -i :11434`

**"Model not found"**
- Download model: `ollama pull llama2`
- List available models: `ollama list`

**Pygame installation issues (Linux)**
```bash
sudo apt-get install python3-dev libsdl2-dev libsdl2-image-dev libsdl2-mixer-dev libsdl2-ttf-dev libfreetype6-dev libportmidi-dev
pip3 install pygame
```

**Permission errors**
```bash
chmod +x install.sh run.sh
```

### Performance Issues
- Use lighter model: `ollama pull llama2:7b`
- Increase timeout in `.env`: `OLLAMA_TIMEOUT=10.0`
- Add more RAM to Docker container
- Close other applications using GPU/CPU

### Memory Issues
- Increase Docker memory limit
- Use `docker system prune` to clean up
- Monitor with `docker stats`

---

## 🔍 Verification

### Test Installation
```bash
# Check Python
python3 --version

# Check dependencies
python3 -c "import pygame, ollama, chromadb; print('All dependencies OK')"

# Check Ollama
ollama list

# Run game
python3 main.py
```

### Expected Output
```
🎮 AI Sims - Life Simulation
✅ Python dependencies OK
✅ Ollama connection OK  
✅ AI model loaded
✅ Memory system initialized
🚀 Game starting...
```

---

## 📁 Directory Structure
```
ai-sims/
├── main.py              # Game entry point
├── requirements.txt     # Python dependencies
├── install.sh          # Auto installer
├── run.sh             # Game launcher
├── .env               # Configuration
├── src/               # Game source code
├── chroma_db/         # AI memory storage
├── game_memories.db   # Game database
└── savegame.json     # Save file
```

---

## 🎮 Ready to Play!

Once installed, start the game with:
```bash
./run.sh
```

Or directly:
```bash
python3 main.py
```

The game will open with a main menu where you can:
1. **New Game** → Create your character
2. **Load Game** → Continue saved progress
3. **Settings** → Configure options
4. **Exit** → Quit game

Enjoy your AI-powered life simulation! 🎉