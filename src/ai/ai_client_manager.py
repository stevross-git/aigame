import os
import json
from typing import Dict, Optional
from src.ai.ollama_client import OllamaClient
from src.ai.api_fallback import APIFallbackClient

class AIClientManager:
    """
    Manages AI client creation based on user settings.
    Respects the ai_provider setting and creates the appropriate client.
    """
    
    def __init__(self):
        self.settings_data = self._load_settings()
        self._load_env_config()
    
    def _load_settings(self) -> Dict:
        """Load settings directly from JSON file to avoid circular imports"""
        settings_file = "settings.json"
        default_settings = {
            "ai_provider": "Ollama",
            "ollama_model": "llama2",
            "enable_api_fallback": True
        }
        
        try:
            if os.path.exists(settings_file):
                with open(settings_file, 'r') as f:
                    saved_settings = json.load(f)
                    default_settings.update(saved_settings)
        except Exception as e:
            print(f"Error loading settings: {e}")
        
        return default_settings
    
    def _load_env_config(self):
        """Load configuration from .env file"""
        self.env_config = {}
        env_file = ".env"
        
        if os.path.exists(env_file):
            try:
                with open(env_file, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#') and '=' in line:
                            key, value = line.split('=', 1)
                            self.env_config[key.strip()] = value.strip().strip('"\'')
            except Exception as e:
                print(f"Error loading .env config: {e}")
    
    def create_ai_client(self) -> Optional[object]:
        """
        Create the appropriate AI client based on settings.
        Returns the client instance or None if creation fails.
        """
        ai_provider = self.settings_data.get("ai_provider", "Ollama")
        
        print(f"Creating AI client for provider: {ai_provider}")
        
        try:
            if ai_provider == "OpenAI":
                return self._create_openai_client()
            elif ai_provider == "Claude":
                return self._create_claude_client()
            elif ai_provider == "Auto":
                return self._create_auto_client()
            else:  # Default to Ollama
                return self._create_ollama_client()
        
        except Exception as e:
            print(f"Failed to create AI client for {ai_provider}: {e}")
            # Fallback to Ollama if primary provider fails
            if ai_provider != "Ollama":
                print("Falling back to Ollama...")
                return self._create_ollama_client()
            return None
    
    def _create_openai_client(self):
        """Create OpenAI-first client"""
        api_key = self.env_config.get("OPENAI_API_KEY")
        if not api_key:
            raise Exception("OpenAI API key not found in .env file")
        
        # Create fallback client configured to use OpenAI first
        fallback_client = APIFallbackClient()
        
        # Create a wrapper that always uses fallback (which will prioritize OpenAI)
        class OpenAIClient:
            def __init__(self, fallback_client):
                self.fallback_client = fallback_client
                self.use_fallback = True  # Always use API
                
            def make_decision(self, npc_data: Dict, context: Dict):
                from src.ai.ollama_client import OllamaClient
                ollama_client = OllamaClient()
                prompt = ollama_client._build_prompt(npc_data, context)
                
                # Use OpenAI first, then Claude as fallback (skip Ollama)
                result = self.fallback_client.make_decision(prompt, provider_priority=["openai", "anthropic"])
                print(f"Using {result['provider']} (response time: {result['response_time']:.2f}s)")
                return ollama_client._parse_response(result['response'])
        
        return OpenAIClient(fallback_client)
    
    def _create_claude_client(self):
        """Create Claude-first client"""
        api_key = self.env_config.get("ANTHROPIC_API_KEY")
        if not api_key:
            raise Exception("Anthropic API key not found in .env file")
        
        # Similar to OpenAI but with Claude priority
        fallback_client = APIFallbackClient()
        
        class ClaudeClient:
            def __init__(self, fallback_client):
                self.fallback_client = fallback_client
                self.use_fallback = True
                
            def make_decision(self, npc_data: Dict, context: Dict):
                from src.ai.ollama_client import OllamaClient
                ollama_client = OllamaClient()
                prompt = ollama_client._build_prompt(npc_data, context)
                
                # Use Claude first, then OpenAI as fallback (skip Ollama)
                result = self.fallback_client.make_decision(prompt, provider_priority=["anthropic", "openai"])
                print(f"Using {result['provider']} (response time: {result['response_time']:.2f}s)")
                return ollama_client._parse_response(result['response'])
        
        return ClaudeClient(fallback_client)
    
    def _create_auto_client(self):
        """Create auto-selecting client that chooses best available provider"""
        # Auto mode: try to determine best available provider
        openai_key = self.env_config.get("OPENAI_API_KEY")
        claude_key = self.env_config.get("ANTHROPIC_API_KEY")
        
        if openai_key:
            print("Auto mode: OpenAI key found, using OpenAI")
            return self._create_openai_client()
        elif claude_key:
            print("Auto mode: Claude key found, using Claude")
            return self._create_claude_client()
        else:
            print("Auto mode: No API keys found, using Ollama")
            return self._create_ollama_client()
    
    def _create_ollama_client(self):
        """Create standard Ollama client with fallback"""
        model_name = self.settings_data.get("ollama_model", "llama2")
        return OllamaClient(model_name)
    
    def get_provider_status(self) -> Dict[str, str]:
        """Get status of current AI provider"""
        ai_provider = self.settings_data.get("ai_provider", "Ollama")
        
        status = {
            "provider": ai_provider,
            "available_keys": []
        }
        
        if self.env_config.get("OPENAI_API_KEY"):
            status["available_keys"].append("OpenAI")
        if self.env_config.get("ANTHROPIC_API_KEY"):
            status["available_keys"].append("Anthropic")
        
        return status