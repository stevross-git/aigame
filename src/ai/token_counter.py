import json
import os
from datetime import datetime
from typing import Dict, Optional

# Import tiktoken if available, otherwise use fallback
try:
    import tiktoken
    TIKTOKEN_AVAILABLE = True
except ImportError:
    TIKTOKEN_AVAILABLE = False
    tiktoken = None

class TokenCounter:
    """
    Tracks API token usage and costs for different providers.
    Provides real-time monitoring of AI API expenses.
    """
    
    def __init__(self):
        self.stats_file = "api_usage_stats.json"
        self.session_stats = {
            "tokens_used": 0,
            "cost_usd": 0.0,
            "requests_made": 0,
            "start_time": datetime.now().isoformat()
        }
        
        # Load historical stats
        self.total_stats = self._load_stats()
        
        # API pricing per 1K tokens (as of 2024)
        self.pricing = {
            "openai": {
                "gpt-3.5-turbo": {"input": 0.0015, "output": 0.002},
                "gpt-4": {"input": 0.03, "output": 0.06},
                "gpt-4-turbo": {"input": 0.01, "output": 0.03}
            },
            "anthropic": {
                "claude-3-haiku": {"input": 0.00025, "output": 0.00125},
                "claude-3-sonnet": {"input": 0.003, "output": 0.015},
                "claude-3-opus": {"input": 0.015, "output": 0.075}
            }
        }
        
        # Initialize tokenizers if tiktoken is available
        self.tokenizers = {}
        if TIKTOKEN_AVAILABLE:
            try:
                self.tokenizers["gpt-3.5-turbo"] = tiktoken.encoding_for_model("gpt-3.5-turbo")
                self.tokenizers["gpt-4"] = tiktoken.encoding_for_model("gpt-4")
            except Exception as e:
                print(f"Warning: Could not load tiktoken tokenizers: {e}")
        else:
            print("Info: tiktoken not available, using fallback token counting")
    
    def _load_stats(self) -> Dict:
        """Load historical usage statistics"""
        default_stats = {
            "total_tokens": 0,
            "total_cost_usd": 0.0,
            "total_requests": 0,
            "daily_stats": {},
            "provider_breakdown": {
                "openai": {"tokens": 0, "cost": 0.0, "requests": 0},
                "anthropic": {"tokens": 0, "cost": 0.0, "requests": 0}
            }
        }
        
        try:
            if os.path.exists(self.stats_file):
                with open(self.stats_file, 'r') as f:
                    saved_stats = json.load(f)
                    default_stats.update(saved_stats)
        except Exception as e:
            print(f"Error loading usage stats: {e}")
        
        return default_stats
    
    def _save_stats(self):
        """Save statistics to file"""
        try:
            with open(self.stats_file, 'w') as f:
                json.dump(self.total_stats, f, indent=2)
        except Exception as e:
            print(f"Error saving usage stats: {e}")
    
    def count_tokens(self, text: str, model: str = "gpt-3.5-turbo") -> int:
        """Count tokens in text using appropriate tokenizer"""
        if not text:
            return 0
        
        # Try to use tiktoken for OpenAI models
        if model in self.tokenizers:
            try:
                return len(self.tokenizers[model].encode(text))
            except Exception:
                pass
        
        # Fallback: rough estimation (1 token ≈ 4 characters for English)
        return max(1, len(text) // 4)
    
    def estimate_cost(self, input_tokens: int, output_tokens: int, 
                     provider: str = "openai", model: str = "gpt-3.5-turbo") -> float:
        """Estimate cost based on token usage"""
        if provider not in self.pricing:
            return 0.0
        
        # Map common model names
        model_mapping = {
            "gpt-3.5-turbo": "gpt-3.5-turbo",
            "gpt-4": "gpt-4", 
            "claude-3-haiku-20240307": "claude-3-haiku",
            "claude-3-sonnet-20240229": "claude-3-sonnet",
            "claude-3-opus-20240229": "claude-3-opus"
        }
        
        mapped_model = model_mapping.get(model, model)
        
        if mapped_model not in self.pricing[provider]:
            # Use default pricing for provider
            if provider == "openai":
                mapped_model = "gpt-3.5-turbo"
            elif provider == "anthropic":
                mapped_model = "claude-3-haiku"
        
        pricing = self.pricing[provider].get(mapped_model, {"input": 0.001, "output": 0.002})
        
        # Calculate cost per 1K tokens
        input_cost = (input_tokens / 1000) * pricing["input"]
        output_cost = (output_tokens / 1000) * pricing["output"]
        
        return input_cost + output_cost
    
    def log_api_call(self, provider: str, model: str, prompt: str, 
                     response: str, response_time: float = 0.0):
        """Log an API call with token counting and cost calculation"""
        
        # Count tokens
        input_tokens = self.count_tokens(prompt, model)
        output_tokens = self.count_tokens(response, model)
        total_tokens = input_tokens + output_tokens
        
        # Calculate cost
        cost = self.estimate_cost(input_tokens, output_tokens, provider, model)
        
        # Update session stats
        self.session_stats["tokens_used"] += total_tokens
        self.session_stats["cost_usd"] += cost
        self.session_stats["requests_made"] += 1
        
        # Update total stats
        self.total_stats["total_tokens"] += total_tokens
        self.total_stats["total_cost_usd"] += cost
        self.total_stats["total_requests"] += 1
        
        # Update provider breakdown
        if provider in self.total_stats["provider_breakdown"]:
            self.total_stats["provider_breakdown"][provider]["tokens"] += total_tokens
            self.total_stats["provider_breakdown"][provider]["cost"] += cost
            self.total_stats["provider_breakdown"][provider]["requests"] += 1
        
        # Update daily stats
        today = datetime.now().strftime("%Y-%m-%d")
        if today not in self.total_stats["daily_stats"]:
            self.total_stats["daily_stats"][today] = {
                "tokens": 0, "cost": 0.0, "requests": 0
            }
        
        self.total_stats["daily_stats"][today]["tokens"] += total_tokens
        self.total_stats["daily_stats"][today]["cost"] += cost
        self.total_stats["daily_stats"][today]["requests"] += 1
        
        # Save stats
        self._save_stats()
        
        # Log to console for debugging
        print(f"💰 API Usage: {provider} | {total_tokens} tokens | ${cost:.4f} | {response_time:.2f}s")
        
        return {
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "total_tokens": total_tokens,
            "cost_usd": cost,
            "provider": provider,
            "model": model
        }
    
    def get_session_stats(self) -> Dict:
        """Get current session statistics"""
        return self.session_stats.copy()
    
    def get_total_stats(self) -> Dict:
        """Get all-time statistics"""
        return self.total_stats.copy()
    
    def get_today_stats(self) -> Dict:
        """Get today's statistics"""
        today = datetime.now().strftime("%Y-%m-%d")
        return self.total_stats["daily_stats"].get(today, {
            "tokens": 0, "cost": 0.0, "requests": 0
        })
    
    def get_cost_breakdown(self) -> Dict:
        """Get cost breakdown by provider"""
        return self.total_stats["provider_breakdown"].copy()
    
    def reset_session_stats(self):
        """Reset session statistics"""
        self.session_stats = {
            "tokens_used": 0,
            "cost_usd": 0.0,
            "requests_made": 0,
            "start_time": datetime.now().isoformat()
        }
    
    def format_cost(self, cost: float) -> str:
        """Format cost for display"""
        if cost < 0.001:
            return f"${cost:.6f}"
        elif cost < 0.01:
            return f"${cost:.4f}"
        else:
            return f"${cost:.2f}"
    
    def get_daily_trend(self, days: int = 7) -> Dict:
        """Get daily usage trend for the last N days"""
        from datetime import datetime, timedelta
        
        trend = {}
        today = datetime.now()
        
        for i in range(days):
            date = (today - timedelta(days=i)).strftime("%Y-%m-%d")
            trend[date] = self.total_stats["daily_stats"].get(date, {
                "tokens": 0, "cost": 0.0, "requests": 0
            })
        
        return trend