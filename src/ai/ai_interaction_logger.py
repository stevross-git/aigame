"""
AI Interaction Logger - Detailed logging of all AI requests and responses
"""

import os
import json
import time
import datetime
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict
from pathlib import Path

@dataclass
class AIInteractionLog:
    """Single AI interaction log entry"""
    timestamp: str
    npc_name: str
    interaction_id: str
    request_type: str  # "decision", "conversation", "behavior", etc.
    
    # Request data
    prompt: str
    context: Dict[str, Any]
    npc_data: Dict[str, Any]
    
    # Response data
    response_raw: str
    response_parsed: Dict[str, Any]
    
    # Metadata
    provider: str  # "ollama", "openai", "fallback", etc.
    model: str
    response_time_ms: int
    cached: bool
    success: bool
    error_message: Optional[str] = None
    
    # Analysis
    prompt_length: int = 0
    response_length: int = 0
    
    def __post_init__(self):
        self.prompt_length = len(self.prompt)
        self.response_length = len(self.response_raw)

class AIInteractionLogger:
    """Comprehensive AI interaction logging system"""
    
    def __init__(self, log_directory: str = "logs/ai_interactions"):
        self.log_directory = Path(log_directory)
        self.log_directory.mkdir(parents=True, exist_ok=True)
        
        # Current session log file
        session_time = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        self.session_log_file = self.log_directory / f"ai_session_{session_time}.jsonl"
        
        # Summary stats
        self.session_stats = {
            "start_time": datetime.datetime.now().isoformat(),
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "cached_responses": 0,
            "providers_used": {},
            "npcs_interacted": set(),
            "total_prompt_chars": 0,
            "total_response_chars": 0,
            "average_response_time_ms": 0.0
        }
        
        # Real-time log buffer for debugging
        self.recent_logs = []
        self.max_recent_logs = 50
        
        print(f"🔍 AI Interaction Logger initialized")
        print(f"📁 Session log: {self.session_log_file}")
    
    def log_interaction(self, 
                       npc_name: str,
                       request_type: str,
                       prompt: str,
                       context: Dict[str, Any],
                       npc_data: Dict[str, Any],
                       response_raw: str,
                       response_parsed: Dict[str, Any],
                       provider: str,
                       model: str,
                       response_time_ms: int,
                       cached: bool = False,
                       error_message: Optional[str] = None) -> str:
        """Log a complete AI interaction"""
        
        interaction_id = f"{npc_name}_{int(time.time()*1000)}"
        timestamp = datetime.datetime.now().isoformat()
        success = error_message is None
        
        # Create log entry
        log_entry = AIInteractionLog(
            timestamp=timestamp,
            npc_name=npc_name,
            interaction_id=interaction_id,
            request_type=request_type,
            prompt=prompt,
            context=self._sanitize_context(context),
            npc_data=self._sanitize_npc_data(npc_data),
            response_raw=response_raw,
            response_parsed=response_parsed,
            provider=provider,
            model=model,
            response_time_ms=response_time_ms,
            cached=cached,
            success=success,
            error_message=error_message
        )
        
        # Write to session log file
        self._write_to_session_log(log_entry)
        
        # Update stats
        self._update_session_stats(log_entry)
        
        # Add to recent logs buffer
        self._add_to_recent_logs(log_entry)
        
        # Print summary to console
        self._print_interaction_summary(log_entry)
        
        return interaction_id
    
    def _sanitize_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Remove or truncate large context data for logging"""
        sanitized = {}
        for key, value in context.items():
            if key in ['situation', 'emotion', 'nearby_npcs']:
                sanitized[key] = value
            elif key == 'active_events':
                sanitized[key] = value[:3] if isinstance(value, list) else value
            else:
                # Truncate long strings
                if isinstance(value, str) and len(value) > 100:
                    sanitized[key] = value[:100] + "..."
                else:
                    sanitized[key] = value
        return sanitized
    
    def _sanitize_npc_data(self, npc_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract relevant NPC data for logging"""
        return {
            "name": npc_data.get("name", "unknown"),
            "personality_description": npc_data.get("personality_description", ""),
            "needs": npc_data.get("needs", {}),
            "relationships_count": len(npc_data.get("relationships", {})),
            "memories_count": len(npc_data.get("recent_memories", []))
        }
    
    def _write_to_session_log(self, log_entry: AIInteractionLog):
        """Write log entry to JSONL file"""
        try:
            with open(self.session_log_file, 'a', encoding='utf-8') as f:
                json.dump(asdict(log_entry), f, ensure_ascii=False)
                f.write('\n')
        except Exception as e:
            print(f"❌ Failed to write AI log: {e}")
    
    def _update_session_stats(self, log_entry: AIInteractionLog):
        """Update session statistics"""
        self.session_stats["total_requests"] += 1
        
        if log_entry.success:
            self.session_stats["successful_requests"] += 1
        else:
            self.session_stats["failed_requests"] += 1
        
        if log_entry.cached:
            self.session_stats["cached_responses"] += 1
        
        # Track providers
        if log_entry.provider not in self.session_stats["providers_used"]:
            self.session_stats["providers_used"][log_entry.provider] = 0
        self.session_stats["providers_used"][log_entry.provider] += 1
        
        # Track NPCs
        self.session_stats["npcs_interacted"].add(log_entry.npc_name)
        
        # Character counts
        self.session_stats["total_prompt_chars"] += log_entry.prompt_length
        self.session_stats["total_response_chars"] += log_entry.response_length
        
        # Average response time
        total_requests = self.session_stats["total_requests"]
        old_avg = self.session_stats["average_response_time_ms"]
        new_avg = ((old_avg * (total_requests - 1)) + log_entry.response_time_ms) / total_requests
        self.session_stats["average_response_time_ms"] = new_avg
    
    def _add_to_recent_logs(self, log_entry: AIInteractionLog):
        """Add to recent logs buffer"""
        self.recent_logs.append(log_entry)
        if len(self.recent_logs) > self.max_recent_logs:
            self.recent_logs.pop(0)
    
    def _print_interaction_summary(self, log_entry: AIInteractionLog):
        """Print a concise summary of the interaction to console"""
        status = "✅" if log_entry.success else "❌"
        cache_indicator = "💾" if log_entry.cached else "🔄"
        
        print(f"{status} {cache_indicator} [{log_entry.npc_name}] {log_entry.request_type} "
              f"({log_entry.provider}/{log_entry.model}) - {log_entry.response_time_ms}ms")
        
        if not log_entry.success and log_entry.error_message:
            print(f"   Error: {log_entry.error_message}")
        
        # Show key parts of interaction
        action = log_entry.response_parsed.get('action', 'unknown')
        dialogue = log_entry.response_parsed.get('dialogue', '')
        if dialogue:
            dialogue_preview = dialogue[:50] + "..." if len(dialogue) > 50 else dialogue
            print(f"   Action: {action} | Dialogue: \"{dialogue_preview}\"")
        else:
            print(f"   Action: {action}")
    
    def get_session_summary(self) -> Dict[str, Any]:
        """Get current session statistics"""
        stats = self.session_stats.copy()
        stats["npcs_interacted"] = list(stats["npcs_interacted"])
        stats["success_rate"] = (stats["successful_requests"] / max(stats["total_requests"], 1)) * 100
        stats["cache_hit_rate"] = (stats["cached_responses"] / max(stats["total_requests"], 1)) * 100
        return stats
    
    def print_session_summary(self):
        """Print detailed session summary"""
        summary = self.get_session_summary()
        
        print("\n" + "="*60)
        print("🤖 AI INTERACTION SESSION SUMMARY")
        print("="*60)
        print(f"📊 Total Requests: {summary['total_requests']}")
        print(f"✅ Successful: {summary['successful_requests']} ({summary['success_rate']:.1f}%)")
        print(f"❌ Failed: {summary['failed_requests']}")
        print(f"💾 Cached: {summary['cached_responses']} ({summary['cache_hit_rate']:.1f}%)")
        print(f"⚡ Avg Response Time: {summary['average_response_time_ms']:.1f}ms")
        print(f"👥 NPCs Interacted: {len(summary['npcs_interacted'])} ({', '.join(summary['npcs_interacted'])})")
        print(f"📝 Total Prompt Chars: {summary['total_prompt_chars']:,}")
        print(f"📤 Total Response Chars: {summary['total_response_chars']:,}")
        print("🔧 Providers Used:")
        for provider, count in summary['providers_used'].items():
            print(f"   - {provider}: {count} requests")
        print("="*60 + "\n")
    
    def get_recent_interactions(self, count: int = 10) -> list:
        """Get most recent interactions for debugging"""
        return self.recent_logs[-count:] if self.recent_logs else []
    
    def export_detailed_log(self, npc_name: Optional[str] = None, 
                          interaction_type: Optional[str] = None) -> str:
        """Export detailed log for specific NPC or interaction type"""
        try:
            export_data = []
            
            with open(self.session_log_file, 'r', encoding='utf-8') as f:
                for line in f:
                    log_entry = json.loads(line.strip())
                    
                    # Filter if requested
                    if npc_name and log_entry.get('npc_name') != npc_name:
                        continue
                    if interaction_type and log_entry.get('request_type') != interaction_type:
                        continue
                    
                    export_data.append(log_entry)
            
            # Create export file
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filter_str = f"_{npc_name}" if npc_name else f"_{interaction_type}" if interaction_type else ""
            export_file = self.log_directory / f"ai_export{filter_str}_{timestamp}.json"
            
            with open(export_file, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            print(f"📁 Exported {len(export_data)} interactions to {export_file}")
            return str(export_file)
            
        except Exception as e:
            print(f"❌ Failed to export log: {e}")
            return ""

# Global logger instance
_ai_logger = None

def get_ai_logger() -> AIInteractionLogger:
    """Get the global AI interaction logger"""
    global _ai_logger
    if _ai_logger is None:
        _ai_logger = AIInteractionLogger()
    return _ai_logger

def log_ai_interaction(**kwargs) -> str:
    """Convenience function to log an AI interaction"""
    return get_ai_logger().log_interaction(**kwargs)

def print_ai_summary():
    """Convenience function to print session summary"""
    get_ai_logger().print_session_summary()