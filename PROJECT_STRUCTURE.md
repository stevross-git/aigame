# AI Sims - Project Structure

```
ai-sims/
├── 📄 README.md              # Main project documentation
├── 📄 INSTALL.md             # Installation guide
├── 📄 CHANGELOG.md           # Version history
├── 📄 LICENSE                # MIT license
├── 📄 VERSION                # Current version
├── 📄 PROJECT_STRUCTURE.md   # This file
│
├── 🚀 main.py                # Game entry point
├── ⚙️ setup.py               # Python package setup
├── 📦 requirements.txt       # Python dependencies
├── 🔧 Makefile              # Build automation
│
├── 🛠️ install.sh             # Auto-installation script
├── 🎮 run.sh                 # Game launcher script
├── 🧪 test_setup.py          # Setup verification tests
│
├── 🐳 Dockerfile             # Docker container config
├── 🐳 docker-compose.yml     # Docker Compose config
├── 🌍 .env                   # Environment configuration
├── 🌍 .env.example           # Environment template
├── 📝 .gitignore             # Git ignore rules
│
├── 📁 src/                   # Main source code
│   ├── 📄 __init__.py
│   │
│   ├── 🎮 core/              # Game engine core
│   │   ├── 📄 __init__.py
│   │   ├── 🎮 game.py        # Main game class
│   │   ├── 📷 camera.py      # Camera system
│   │   ├── 🔢 constants.py   # Game constants
│   │   ├── ⚙️ config.py      # Configuration management
│   │   └── 💾 save_system.py # Save/load functionality
│   │
│   ├── 👥 entities/          # Game characters & objects
│   │   ├── 📄 __init__.py
│   │   ├── 🎯 player.py      # Player character
│   │   ├── 🤖 npc.py         # AI-powered NPCs
│   │   └── 🧠 personality.py # Personality system
│   │
│   ├── 🤖 ai/                # AI integration
│   │   ├── 📄 __init__.py
│   │   ├── 🦙 ollama_client.py    # Ollama integration
│   │   ├── 💭 memory_manager.py   # Long-term memory
│   │   └── 🔄 api_fallback.py     # API fallback system
│   │
│   ├── 🖼️ ui/                # User interface
│   │   ├── 📄 __init__.py
│   │   ├── 📱 hud.py         # Head-up display
│   │   ├── 📋 menu.py        # Main/pause menus
│   │   └── 👤 character_creator.py # Character creation
│   │
│   └── 🌍 world/             # Game world
│       ├── 📄 __init__.py
│       ├── 🗺️ map.py          # World map generation
│       └── 🎭 events.py       # Dynamic event system
│
├── 📁 assets/                # Game assets (auto-created)
│   ├── 🎨 sprites/           # Character/object sprites
│   └── 🗺️ maps/              # Map data files
│
├── 💾 chroma_db/             # AI memory database (auto-created)
├── 🗄️ game_memories.db       # SQLite game database (auto-created)
└── 💾 savegame.json          # Player save file (auto-created)
```

## 📋 Core Components

### 🎮 Game Engine (`src/core/`)
- **game.py**: Main game loop, state management, UI coordination
- **camera.py**: 2D camera system with smooth following
- **constants.py**: Game configuration constants
- **config.py**: Environment-based configuration
- **save_system.py**: JSON-based save/load with character data

### 👥 Characters (`src/entities/`)
- **player.py**: Customizable player character with needs/personality
- **npc.py**: AI-driven NPCs with autonomous behavior
- **personality.py**: 10-trait personality system with AI prompts

### 🤖 AI System (`src/ai/`)
- **ollama_client.py**: Local AI integration with timeout handling
- **memory_manager.py**: SQLite + ChromaDB for persistent memories
- **api_fallback.py**: Multi-provider AI fallback (OpenAI/Claude)

### 🖼️ User Interface (`src/ui/`)
- **hud.py**: Real-time game HUD with status panels
- **menu.py**: Main menu, pause menu with button system
- **character_creator.py**: Interactive character creation UI

### 🌍 World System (`src/world/`)
- **map.py**: 2D tile-based world with buildings
- **events.py**: Dynamic event generation and NPC reactions

## 🎯 Key Features

### 🧠 AI Decision Making
```python
# NPCs make decisions every 2-5 seconds based on:
- Current needs (hunger, sleep, social, fun)
- Personality traits (10 different traits)
- Recent memories and relationships
- Active world events
- Nearby NPCs and locations
```

### 💭 Memory System
```python
# Dual storage approach:
- SQLite: Structured data (relationships, events)
- ChromaDB: Vector embeddings for semantic search
- Persistent across game sessions
- Influences future AI decisions
```

### 🎭 Event System
```python
# Dynamic events that affect NPC behavior:
- Weather: Sunny, rainy, storms
- Social: Parties, gatherings, celebrations
- Economic: Job fairs, sales, opportunities
- Entertainment: Performances, movies
```

## 🔧 Development Tools

### 📋 Available Commands
```bash
make help          # Show all available commands
make install       # Full installation
make test          # Verify setup
make run           # Start game
make clean         # Clean temporary files
make docker        # Run in Docker
```

### 🧪 Testing
```bash
python3 test_setup.py  # Comprehensive setup verification
```

### 🐳 Docker Support
```bash
docker-compose up --build  # Containerized deployment
```

## 📊 Performance

### 🎯 Target Specifications
- **Memory**: 2GB RAM minimum, 4GB recommended
- **CPU**: Multi-core recommended for AI processing
- **Storage**: 1GB for models + game data
- **Python**: 3.8+ required

### ⚡ Optimization Features
- Threaded AI decision making
- Configurable AI timeouts
- Memory-efficient sprite handling
- Auto-save with minimal performance impact

## 🔐 Security & Privacy

### 🛡️ Privacy Features
- **Local AI**: Primary processing via Ollama (offline)
- **Optional APIs**: Fallback only (configurable)
- **Data Storage**: All data stored locally
- **No Telemetry**: No data collection or transmission

### 🔒 Configuration
```env
# API keys only used for fallback (optional)
OPENAI_API_KEY=optional
ANTHROPIC_API_KEY=optional

# All processing can be 100% local
OLLAMA_TIMEOUT=5.0  # Local-only with long timeout
```

## 🎮 Gameplay Flow

1. **Character Creation** → Design personality & appearance
2. **World Entry** → Spawn in 2D world with AI NPCs
3. **Real-time Simulation** → NPCs autonomously interact
4. **Dynamic Events** → Weather, social events affect behavior
5. **Memory Formation** → NPCs remember interactions
6. **Relationship Evolution** → Friendships/rivalries develop
7. **Auto-save** → Progress automatically preserved

This structure creates a complete AI-powered life simulation with emergent gameplay through autonomous NPC behavior! 🎉