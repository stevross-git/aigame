# AI Sims - Life Simulation Game

A 2D life simulation game where NPCs are powered by AI (Ollama/OpenAI/Claude) with persistent memory and emergent behavior.

## ✨ Features

- **🧠 AI-Powered NPCs**: Each character uses AI for autonomous decision-making
- **💭 Long-term Memory**: NPCs remember past interactions and events using SQLite + ChromaDB
- **🎭 Dynamic Events**: Weather, social gatherings, and random events affect NPC behavior
- **💬 Smart Conversations**: Context-aware dialogue with speech bubbles
- **🔄 API Fallback**: Automatic fallback from Ollama → OpenAI → Claude if needed
- **📊 Persistent Relationships**: NPCs develop lasting friendships and rivalries

## 🚀 Quick Start

### One-Command Installation
```bash
# Download, install everything, and run
chmod +x install.sh && ./install.sh
```

### Start Playing
```bash
./run.sh
# OR
make run
# OR  
python3 main.py
```

### Manual Installation
1. **Install Ollama** (primary AI provider):
```bash
# Linux/macOS
curl -fsSL https://ollama.com/install.sh | sh

# Pull a model
ollama pull llama2
```

2. **Install Dependencies**:
```bash
pip install -r requirements.txt
```

3. **Run the Game**:
```bash
python main.py
```

## ⚙️ Configuration

Copy `.env.example` to `.env` and configure:

```bash
cp .env.example .env
```

### API Keys (Optional - for fallback when Ollama is slow):
```env
OPENAI_API_KEY=your_key_here
ANTHROPIC_API_KEY=your_key_here
```

### Performance Settings:
```env
OLLAMA_TIMEOUT=5.0
AI_DECISION_COOLDOWN_MIN=2.0
AI_DECISION_COOLDOWN_MAX=5.0
```

## 🎮 Controls

- **WASD/Arrow Keys**: Move player
- **ESC**: Exit game

## 🏗️ Architecture

```
src/
├── core/          # Game engine, camera, constants
├── entities/      # Player, NPCs, personality system
├── ai/            # Ollama client, API fallback, memory
├── world/         # Map generation, events system
└── ui/            # Interface components
```

## 📊 AI System

The game uses a **multi-tier AI system**:

1. **Primary**: Ollama (local, private)
2. **Fallback**: OpenAI GPT-3.5/4 (if configured)
3. **Backup**: Claude (if configured)
4. **Emergency**: Rule-based behavior

## 💾 Memory System

- **SQLite**: Stores structured data (relationships, events)
- **ChromaDB**: Vector embeddings for semantic memory search
- **Persistent**: NPCs remember across game sessions

## 🛠️ Development

### Available Commands
```bash
make help           # Show all commands
make install        # Full installation 
make test          # Verify setup
make run           # Start game
make run-debug     # Debug mode
make clean         # Clean cache
make docker        # Run in Docker
```

### Quick Development Setup
```bash
make dev           # Setup + test + run
```

## 🎯 Current Status

- ✅ **Complete Game Engine** - 2D world with camera system
- ✅ **AI-Powered NPCs** - Ollama integration with personality traits
- ✅ **Character Creation** - Custom player with 10 personality traits
- ✅ **Dynamic Dialogue** - Context-aware conversations with speech bubbles
- ✅ **World Events** - Weather, social events, and NPC reactions
- ✅ **Long-term Memory** - SQLite + ChromaDB persistent storage
- ✅ **API Fallback** - Multi-provider AI system (Ollama → OpenAI → Claude)
- ✅ **Complete UI** - Menus, HUD, save/load, character creator
- ✅ **Auto-Save** - Persistent game state with 5-minute intervals

## 🚨 Troubleshooting

**Installation issues?**
```bash
python3 test_setup.py  # Run diagnostics
make clean             # Clean and retry
```

**Ollama not working?**
- Check if `ollama serve` is running
- Verify model is pulled: `ollama list`
- Game will auto-fallback to API providers

**Performance slow?**
- Use lighter model: `ollama pull llama2:7b`
- Increase timeout in `.env`: `OLLAMA_TIMEOUT=10.0`
- Add API keys for faster fallback

**Memory issues?**
- Database files are created automatically
- ChromaDB data stored in `./chroma_db/`

See [INSTALL.md](INSTALL.md) for detailed troubleshooting.