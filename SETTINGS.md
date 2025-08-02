# AI Sims - Settings Guide

The settings system allows you to customize all aspects of the AI Sims experience. Access settings from the main menu or during gameplay.

## 🖼️ Graphics Settings

### Display Options
- **Fullscreen**: Toggle full-screen mode (ON/OFF)
- **V-Sync**: Vertical synchronization for smooth display (ON/OFF)
- **FPS Limit**: Frame rate cap (30, 60, 120, Unlimited)
- **Show FPS**: Display frame rate counter (ON/OFF)
- **Camera Smoothing**: Smooth camera following (ON/OFF)
- **UI Scale**: Interface size multiplier (0.8x, 1.0x, 1.2x, 1.5x)
- **Colorblind Mode**: Enhanced visibility options (ON/OFF)

## 🔊 Audio Settings

### Volume Controls
- **Master Volume**: Overall audio level (0.0 - 1.0)
- **Music Volume**: Background music level (0.0 - 1.0) 
- **SFX Volume**: Sound effects level (0.0 - 1.0)
- **Mute Audio**: Disable all audio (ON/OFF)

## 🤖 AI Settings

### AI Provider Configuration
- **AI Provider**: Primary AI service
  - `Ollama` - Local AI (privacy-focused, slower)
  - `OpenAI` - Cloud API (faster, requires key)
  - `Claude` - Anthropic API (faster, requires key)
  - `Auto` - Automatic selection based on availability

### Model Selection
- **Ollama Model**: Local AI model to use
  - `llama2` - Standard model (2GB RAM)
  - `llama2:7b` - Smaller model (4GB RAM)
  - `llama2:13b` - Larger model (8GB RAM)
  - `codellama` - Code-focused model

### Performance Tuning
- **Decision Speed**: How fast NPCs make decisions
  - `Very Fast` - 0.5-1s between decisions
  - `Fast` - 1-2s between decisions
  - `Normal` - 2-5s between decisions
  - `Slow` - 5-8s between decisions
  - `Very Slow` - 8-15s between decisions

- **Ollama Timeout**: Seconds before API fallback (1-15s)
- **API Fallback**: Enable cloud AI backup (ON/OFF)

## 🎮 Gameplay Settings

### Game Mechanics
- **Auto-Save Interval**: Automatic save frequency
  - `1 min` - Save every minute
  - `5 min` - Save every 5 minutes (default)
  - `10 min` - Save every 10 minutes
  - `30 min` - Save every 30 minutes
  - `Never` - No auto-save

- **NPC Interactions**: How often NPCs interact
  - `Very Rare` - Minimal social interactions
  - `Rare` - Occasional interactions
  - `Normal` - Balanced social activity
  - `Frequent` - Active social interactions
  - `Very Frequent` - Constant social activity

- **Event Frequency**: World event generation rate
  - `Very Rare` - Few events (1-2 per hour)
  - `Rare` - Some events (3-4 per hour)
  - `Normal` - Regular events (5-6 per hour)
  - `Frequent` - Many events (7-8 per hour)
  - `Very Frequent` - Constant events (10+ per hour)

- **Memory Retention**: How long NPCs remember
  - `Low` - 100 memories per NPC
  - `Medium` - 500 memories per NPC
  - `High` - 1000 memories per NPC (default)
  - `Maximum` - Unlimited memories

### UI Options
- **Show Debug Info**: Display technical information (ON/OFF)
- **Speech Bubbles**: Show NPC dialogue bubbles (ON/OFF)
- **NPC Names**: Display character names (ON/OFF)
- **Needs Bars**: Show NPC status bars (ON/OFF)

## ⚡ Performance Settings

### System Optimization
- **Max NPCs**: Maximum number of AI characters (5-25)
- **Low Performance Mode**: Reduces visual effects (ON/OFF)
- **Reduce AI Frequency**: Lower AI decision rate (ON/OFF)
- **Memory Cleanup**: Automatic cleanup interval (60-1800s)

### Performance Impact Guide

**High Performance Setup** (for older computers):
```
Max NPCs: 5
Low Performance Mode: ON
Reduce AI Frequency: ON
AI Decision Speed: Slow
Ollama Model: llama2:7b
```

**Balanced Setup** (recommended):
```
Max NPCs: 10
Low Performance Mode: OFF
Reduce AI Frequency: OFF
AI Decision Speed: Normal
Ollama Model: llama2
```

**Maximum Quality** (for powerful computers):
```
Max NPCs: 20+
Low Performance Mode: OFF
Reduce AI Frequency: OFF
AI Decision Speed: Fast
Ollama Model: llama2:13b
API Fallback: ON
```

## 🔧 Advanced Configuration

### Manual Settings File
Settings are stored in `settings.json`. Advanced users can edit directly:

```json
{
  "ai_provider": "Ollama",
  "ollama_model": "llama2",
  "ollama_timeout": 5.0,
  "auto_save_interval": 300,
  "max_npcs": 10,
  "show_debug_info": false
}
```

### Environment Variables
Some settings can be overridden via `.env` file:

```env
OLLAMA_MODEL=llama2:7b
OLLAMA_TIMEOUT=10.0
AI_DECISION_COOLDOWN_MIN=3.0
AI_DECISION_COOLDOWN_MAX=6.0
```

## 🚨 Troubleshooting Settings

### Common Issues

**Settings not saving:**
- Check file permissions on `settings.json`
- Ensure game directory is writable

**AI too slow:**
- Reduce AI Decision Speed to "Fast"
- Enable API Fallback
- Use smaller Ollama model (`llama2:7b`)

**Game lagging:**
- Enable Low Performance Mode
- Reduce Max NPCs to 5-8
- Increase AI Decision Speed to "Slow"
- Disable V-Sync

**Audio not working:**
- Check Master Volume > 0
- Disable Mute Audio
- Verify system audio settings

### Reset to Defaults
1. Click "Reset All" in Settings menu
2. Or delete `settings.json` file
3. Restart game to recreate defaults

## 📊 Settings Categories Summary

| Category | Options | Impact |
|----------|---------|---------|
| **Graphics** | 7 options | Visual quality, performance |
| **Audio** | 4 options | Sound experience |
| **AI** | 5 options | NPC intelligence, speed |
| **Gameplay** | 8 options | Game mechanics, UI |
| **Performance** | 4 options | System optimization |

## 🎯 Recommended Settings by Use Case

### **Privacy Focused**
- AI Provider: Ollama
- API Fallback: OFF  
- All processing stays local

### **Performance Focused**
- AI Decision Speed: Fast
- API Fallback: ON
- Low Performance Mode: ON

### **Maximum Immersion**
- Speech Bubbles: ON
- NPC Names: ON
- Event Frequency: Frequent
- Memory Retention: Maximum

The settings system provides complete control over your AI Sims experience, from privacy preferences to performance optimization! 🎮✨