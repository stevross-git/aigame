import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # API Keys
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
    
    # Model Settings
    OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama2")
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
    ANTHROPIC_MODEL = os.getenv("ANTHROPIC_MODEL", "claude-3-haiku-20240307")
    
    # Performance Settings
    OLLAMA_TIMEOUT = float(os.getenv("OLLAMA_TIMEOUT", "5.0"))
    AI_DECISION_COOLDOWN_MIN = float(os.getenv("AI_DECISION_COOLDOWN_MIN", "2.0"))
    AI_DECISION_COOLDOWN_MAX = float(os.getenv("AI_DECISION_COOLDOWN_MAX", "5.0"))
    
    # Memory Settings
    MEMORY_DB_PATH = os.getenv("MEMORY_DB_PATH", "game_memories.db")
    CHROMA_DB_PATH = os.getenv("CHROMA_DB_PATH", "./chroma_db")
    
    # Game Settings
    AUTO_SAVE_INTERVAL = int(os.getenv("AUTO_SAVE_INTERVAL", "300"))  # seconds
    MAX_MEMORIES_PER_NPC = int(os.getenv("MAX_MEMORIES_PER_NPC", "1000"))
    
    @classmethod
    def has_api_fallback(cls):
        return bool(cls.OPENAI_API_KEY or cls.ANTHROPIC_API_KEY)
    
    @classmethod
    def get_available_providers(cls):
        providers = ["ollama"]
        if cls.OPENAI_API_KEY:
            providers.append("openai")
        if cls.ANTHROPIC_API_KEY:
            providers.append("anthropic")
        return providers