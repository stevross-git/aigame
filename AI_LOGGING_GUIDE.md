# AI Interaction Logging System

This document explains the comprehensive AI interaction logging system that tracks all AI requests and responses in the game.

## 📋 Overview

The AI logging system captures detailed information about every AI interaction, including:
- **Prompts sent** to AI models (Ollama, OpenAI, etc.)
- **Raw responses** received from AI providers
- **Parsed responses** in structured format
- **Performance metrics** (response times, success rates)
- **Context data** (NPC state, game situation)
- **Provider information** (which AI model was used)

## 🔍 What Gets Logged

### 1. **AI Decision Making** (`decision` type)
- **When**: NPCs make decisions using Ollama or other AI providers
- **Prompt Example**:
```
You are Alice, an NPC in a life simulation game.
Your personality: Friendly and optimistic individual who loves adventure

Current needs:
- Hunger: 0.75
- Sleep: 0.82
- Social: 0.45
- Fun: 0.60

Current situation: wandering around
Nearby NPCs: Bob, Charlie
Current emotion: happy
Active events: None

Decide your next action. Respond in JSON format:
{
    "action": "move_to/talk_to/work/rest/eat/play/attend_event",
    "target": "location or person name or event name",
    "dialogue": "what you want to say (if talking)",
    "emotion": "happy/sad/angry/neutral/excited",
    "reasoning": "brief explanation"
}
```

- **Response Example**:
```json
{
    "action": "talk_to",
    "target": "Bob",
    "dialogue": "Hey Bob! How's your day going?",
    "emotion": "happy",
    "reasoning": "I want to socialize and Bob is nearby"
}
```

### 2. **Enhanced AI Behavior** (`enhanced_behavior` type)
- **When**: NPCs use the rule-based enhanced AI system
- **Prompt Example**:
```
Enhanced AI Behavior Generation for Alice
Behavior State: socializing
Situation Analysis: {'urgency_level': 0.3, 'social_opportunities': 0.8, 'need_priorities': ['social']}
Personality Traits: {'extraversion': 0.8, 'openness': 0.7}
Context: Time=afternoon, Location=village_center, NPCs=['Bob', 'Charlie']
```

### 3. **Conversation Generation** (`conversation` type)
- **When**: NPCs engage in detailed conversations with players or other NPCs
- Includes dialogue generation, emotional responses, and relationship updates

## 📁 Log File Structure

### Log Directory
```
logs/ai_interactions/
├── ai_session_20250803_230906.jsonl  # Timestamped session file
├── ai_session_20250803_151234.jsonl  # Previous session
└── ai_export_Alice_20250803_235959.json  # Filtered export
```

### Log Entry Format (JSONL)
Each line in the `.jsonl` file contains a complete interaction:

```json
{
  "timestamp": "2025-08-03T23:09:06.643819",
  "npc_name": "Alice",
  "interaction_id": "Alice_1722728946643",
  "request_type": "decision",
  "prompt": "You are Alice, an NPC in a life simulation game...",
  "context": {
    "situation": "wandering around",
    "nearby_npcs": ["Bob", "Charlie"],
    "emotion": "happy"
  },
  "npc_data": {
    "name": "Alice",
    "personality_description": "Friendly and optimistic individual",
    "needs": {"hunger": 0.75, "sleep": 0.82, "social": 0.45, "fun": 0.60},
    "relationships_count": 3,
    "memories_count": 5
  },
  "response_raw": "{\"action\": \"talk_to\", \"target\": \"Bob\", \"dialogue\": \"Hey Bob!\", \"emotion\": \"happy\", \"reasoning\": \"Want to socialize\"}",
  "response_parsed": {
    "action": "talk_to",
    "target": "Bob", 
    "dialogue": "Hey Bob! How's your day going?",
    "emotion": "happy",
    "reasoning": "I want to socialize and Bob is nearby"
  },
  "provider": "ollama",
  "model": "llama2",
  "response_time_ms": 1250,
  "cached": false,
  "success": true,
  "error_message": null,
  "prompt_length": 445,
  "response_length": 156
}
```

## 🛠️ Using the Log Viewer

### Command Line Tool: `view_ai_logs.py`

#### Basic Usage
```bash
# View latest session log
python view_ai_logs.py --latest

# View specific log file  
python view_ai_logs.py logs/ai_interactions/ai_session_20250803_230906.jsonl

# Filter by NPC
python view_ai_logs.py --latest --npc Alice

# Filter by interaction type
python view_ai_logs.py --latest --type decision

# Filter by AI provider
python view_ai_logs.py --latest --provider ollama

# Show only successful interactions
python view_ai_logs.py --latest --success-only

# Limit detailed view
python view_ai_logs.py --latest --limit 5

# Export to CSV
python view_ai_logs.py --latest --export-csv ai_data.csv
```

#### Sample Output
```
🤖 AI INTERACTION LOG SUMMARY
==================================================
📊 Total Interactions: 25
✅ Successful: 23 (92.0%)
❌ Failed: 2 (8.0%)
💾 Cached: 8 (32.0%)
⚡ Avg Response Time: 1,234.5ms
👥 NPCs: 7 (Alice, Bob, Charlie, Diana, Kailey, Louie, Steve)
📝 Total Prompt Chars: 12,450
📤 Total Response Chars: 3,890

🔧 Providers Used:
   ollama: 20 (80.0%)
   fallback_openai: 3 (12.0%)
   enhanced_ai_engine: 2 (8.0%)

📋 Request Types:
   decision: 18 (72.0%)
   enhanced_behavior: 5 (20.0%)
   conversation: 2 (8.0%)

🔍 DETAILED INTERACTIONS (last 10)
================================================================================

✅ 🔄 [2025-08-03T23:09:06.643819] Alice
   Type: decision | Provider: ollama | Time: 1250ms
   Prompt: You are Alice, an NPC in a life simulation game...
   Response: Action=talk_to | Dialogue="Hey Bob! How's your day going?"
            Emotion=happy
```

## 🎮 In-Game Controls

### Keyboard Shortcuts
- **F9**: Print AI interaction summary to console
- **F10**: Export AI logs to timestamped file

### Console Commands
```python
# In Python console or debug mode
from src.ai.ai_interaction_logger import get_ai_logger, print_ai_summary

# Get current session summary
logger = get_ai_logger()
summary = logger.get_session_summary()

# Print summary
print_ai_summary()

# Export specific NPC's interactions
logger.export_detailed_log(npc_name="Alice")

# Get recent interactions for debugging
recent = logger.get_recent_interactions(count=5)
```

## 📊 Performance Metrics

### What You Can Analyze

1. **Response Times**
   - Which AI providers are fastest/slowest
   - Performance degradation over time
   - Network latency issues

2. **Success Rates**
   - Which NPCs have more AI failures
   - Provider reliability comparison
   - Error pattern analysis

3. **Cache Efficiency**
   - How often responses are cached vs. generated
   - Cache hit rates by NPC or situation
   - Performance improvement from caching

4. **Prompt Engineering**
   - Prompt length vs. response quality
   - Context data effectiveness
   - Response parsing success rates

5. **AI Behavior Patterns**
   - Most common NPC actions
   - Dialogue variety and repetition
   - Emotional state transitions

## 🔧 Troubleshooting

### Common Issues

1. **No Log Files Created**
   - Check if `logs/ai_interactions/` directory exists
   - Verify AI system is active (NPCs are thinking)
   - Check file permissions

2. **Large Log Files**
   - Log files grow during gameplay
   - Each session creates a new file
   - Use filtering options to manage data

3. **Missing Interactions**
   - Some interactions use cached responses
   - Enhanced AI behavior may not always trigger external AI
   - Check different request types with filters

### Performance Impact

- **Minimal Overhead**: Logging adds <1ms per interaction
- **Asynchronous Writing**: Doesn't block AI responses
- **Memory Efficient**: Recent logs buffer is limited to 50 entries
- **Disk Usage**: ~1KB per interaction average

## 🔍 Advanced Analysis

### Python Analysis Example
```python
import json
import pandas as pd

# Load log file
interactions = []
with open('logs/ai_interactions/ai_session_20250803_230906.jsonl', 'r') as f:
    for line in f:
        interactions.append(json.loads(line.strip()))

# Convert to DataFrame
df = pd.DataFrame(interactions)

# Analyze response times by provider
response_times = df.groupby('provider')['response_time_ms'].agg(['mean', 'std', 'count'])
print(response_times)

# Analyze most common actions
actions = df['response_parsed'].apply(lambda x: x.get('action', 'unknown'))
action_counts = actions.value_counts()
print(action_counts)

# Success rates by NPC
success_rates = df.groupby('npc_name')['success'].mean()
print(success_rates)
```

### SQL Analysis (if imported to database)
```sql
-- Average response time by provider
SELECT provider, AVG(response_time_ms) as avg_response_time
FROM ai_interactions 
GROUP BY provider;

-- Most talkative NPCs
SELECT npc_name, COUNT(*) as interaction_count
FROM ai_interactions 
WHERE request_type = 'decision'
GROUP BY npc_name
ORDER BY interaction_count DESC;

-- Error rate trends
SELECT DATE(timestamp) as date, 
       COUNT(*) as total_interactions,
       SUM(CASE WHEN success = false THEN 1 ELSE 0 END) as failures,
       (SUM(CASE WHEN success = false THEN 1 ELSE 0 END) * 100.0 / COUNT(*)) as error_rate
FROM ai_interactions
GROUP BY DATE(timestamp)
ORDER BY date;
```

## 📝 Understanding the Data

### Prompt Analysis
- **Length**: Longer prompts may provide better context but increase latency
- **Structure**: JSON format prompts for structured responses
- **Context**: Includes NPC needs, relationships, and game state

### Response Analysis
- **Parsing Success**: How well the AI follows the requested JSON format
- **Action Variety**: Range of different actions NPCs choose
- **Dialogue Quality**: Creativity and appropriateness of generated text

### Provider Comparison
- **Ollama**: Local models, faster but may be less sophisticated
- **OpenAI**: Cloud-based, potentially higher quality but with latency
- **Fallback**: Simple rule-based responses when AI fails

This logging system provides comprehensive insight into how AI drives NPC behavior in your simulation game, enabling you to optimize performance, debug issues, and improve the overall AI experience.