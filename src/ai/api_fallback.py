import os
import time
import openai
import anthropic
from typing import Dict, Optional
import json
from dotenv import load_dotenv
from dataclasses import dataclass
from src.ai.token_counter import TokenCounter

load_dotenv()

@dataclass
class AIProvider:
    name: str
    is_available: bool
    last_error: Optional[str] = None
    avg_response_time: float = 0.0
    success_count: int = 0
    error_count: int = 0

class APIFallbackClient:
    def __init__(self):
        self.providers = {
            "ollama": AIProvider("ollama", True),
            "openai": AIProvider("openai", bool(os.getenv("OPENAI_API_KEY"))),
            "anthropic": AIProvider("anthropic", bool(os.getenv("ANTHROPIC_API_KEY")))
        }
        
        self.ollama_timeout = float(os.getenv("OLLAMA_TIMEOUT", "5.0"))
        self.token_counter = TokenCounter()
        
        if self.providers["anthropic"].is_available:
            self.anthropic_client = anthropic.Anthropic(
                api_key=os.getenv("ANTHROPIC_API_KEY")
            )
    
    def make_decision(self, prompt: str, provider_priority: list = None) -> Dict:
        if provider_priority is None:
            provider_priority = ["ollama", "openai", "anthropic"]
        
        for provider_name in provider_priority:
            provider = self.providers.get(provider_name)
            if not provider or not provider.is_available:
                continue
            
            try:
                start_time = time.time()
                
                if provider_name == "ollama":
                    response = self._call_ollama(prompt)
                elif provider_name == "openai":
                    response = self._call_openai(prompt)
                elif provider_name == "anthropic":
                    response = self._call_anthropic(prompt)
                else:
                    continue
                
                elapsed_time = time.time() - start_time
                self._update_provider_stats(provider, elapsed_time, success=True)
                
                return {
                    "response": response,
                    "provider": provider_name,
                    "response_time": elapsed_time
                }
                
            except Exception as e:
                self._update_provider_stats(provider, 0, success=False, error=str(e))
                print(f"Provider {provider_name} failed: {e}")
                continue
        
        return self._get_fallback_response()
    
    def _call_ollama(self, prompt: str) -> str:
        import ollama
        import threading
        
        result = {"response": None, "error": None}
        
        def ollama_request():
            try:
                client = ollama.Client()
                response = client.generate(
                    model=os.getenv("OLLAMA_MODEL", "llama2"),
                    prompt=prompt,
                    options={
                        "temperature": 0.7,
                        "top_p": 0.9,
                        "max_tokens": 150
                    }
                )
                result["response"] = response['response']
            except Exception as e:
                result["error"] = str(e)
        
        thread = threading.Thread(target=ollama_request)
        thread.start()
        thread.join(timeout=self.ollama_timeout)
        
        if thread.is_alive():
            raise TimeoutError(f"Ollama request timed out after {self.ollama_timeout}s")
        
        if result["error"]:
            raise Exception(result["error"])
        
        return result["response"]
    
    def _call_openai(self, prompt: str) -> str:
        client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        model = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
        
        # Prepare messages
        system_msg = "You are an NPC in a life simulation game. Respond only with valid JSON."
        messages = [
            {"role": "system", "content": system_msg},
            {"role": "user", "content": prompt}
        ]
        
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0.7,
            max_tokens=150
        )
        
        response_text = response.choices[0].message.content
        
        # Log token usage and cost
        if hasattr(response, 'usage') and response.usage:
            # Use actual token counts from API
            input_tokens = response.usage.prompt_tokens
            output_tokens = response.usage.completion_tokens
            
            # Calculate response time (will be set by caller)
            full_prompt = system_msg + "\n" + prompt
            self.token_counter.log_api_call(
                provider="openai",
                model=model,
                prompt=full_prompt,
                response=response_text,
                response_time=0.0  # Will be updated by caller
            )
        else:
            # Fallback token counting if API doesn't provide usage
            full_prompt = system_msg + "\n" + prompt
            self.token_counter.log_api_call(
                provider="openai",
                model=model, 
                prompt=full_prompt,
                response=response_text,
                response_time=0.0
            )
        
        return response_text
    
    def _call_anthropic(self, prompt: str) -> str:
        model = os.getenv("ANTHROPIC_MODEL", "claude-3-haiku-20240307")
        system_msg = "You are an NPC in a life simulation game. Respond only with valid JSON."
        
        response = self.anthropic_client.messages.create(
            model=model,
            max_tokens=150,
            temperature=0.7,
            system=system_msg,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        response_text = response.content[0].text
        
        # Log token usage and cost
        if hasattr(response, 'usage') and response.usage:
            # Use actual token counts from API
            input_tokens = response.usage.input_tokens
            output_tokens = response.usage.output_tokens
            
            full_prompt = system_msg + "\n" + prompt
            self.token_counter.log_api_call(
                provider="anthropic",
                model=model,
                prompt=full_prompt,
                response=response_text,
                response_time=0.0  # Will be updated by caller
            )
        else:
            # Fallback token counting if API doesn't provide usage
            full_prompt = system_msg + "\n" + prompt
            self.token_counter.log_api_call(
                provider="anthropic",
                model=model,
                prompt=full_prompt,
                response=response_text,
                response_time=0.0
            )
        
        return response_text
    
    def _update_provider_stats(self, provider: AIProvider, response_time: float, 
                             success: bool, error: Optional[str] = None):
        if success:
            provider.success_count += 1
            total_time = provider.avg_response_time * (provider.success_count - 1)
            provider.avg_response_time = (total_time + response_time) / provider.success_count
            provider.last_error = None
        else:
            provider.error_count += 1
            provider.last_error = error
            
            if provider.error_count > 3:
                provider.is_available = False
                print(f"Provider {provider.name} disabled after multiple failures")
    
    def _get_fallback_response(self) -> Dict:
        return {
            "response": json.dumps({
                "action": "wander",
                "emotion": "neutral",
                "reasoning": "Using fallback behavior"
            }),
            "provider": "fallback",
            "response_time": 0
        }
    
    def get_provider_stats(self) -> Dict[str, Dict]:
        stats = {}
        for name, provider in self.providers.items():
            stats[name] = {
                "available": provider.is_available,
                "success_count": provider.success_count,
                "error_count": provider.error_count,
                "avg_response_time": provider.avg_response_time,
                "last_error": provider.last_error
            }
        return stats