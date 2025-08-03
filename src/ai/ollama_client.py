import ollama
import json
import logging
import threading
import time
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass
from src.ai.api_fallback import APIFallbackClient
from src.ai.predictive_cache import PredictiveAICache
from src.ai.ai_interaction_logger import log_ai_interaction

@dataclass
class AIResponse:
    action: str
    target: Optional[str] = None
    dialogue: Optional[str] = None
    emotion: Optional[str] = None
    reasoning: Optional[str] = None

class OllamaClient:
    def __init__(self, model_name: str = "llama2", disable_ollama: bool = False):
        self.model_name = model_name
        self.disable_ollama = disable_ollama
        self.client = None if disable_ollama else ollama.Client()
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        self.fallback_client = APIFallbackClient()
        self.use_fallback = disable_ollama  # Start with fallback if Ollama disabled
        
        # Async response handling
        self.pending_requests: Dict[str, Dict] = {}
        self.response_callbacks: Dict[str, Callable] = {}
        self.request_counter = 0
        
        # Predictive cache
        self.predictive_cache = PredictiveAICache(self, max_cache_size=500, cache_ttl=1800)  # 30 min TTL
        
        if not disable_ollama:
            try:
                models = self.client.list()
                self.logger.info(f"Available models: {models}")
            except Exception as e:
                self.logger.error(f"Failed to connect to Ollama: {e}")
                self.use_fallback = True
        else:
            self.logger.info("Ollama disabled by configuration, using API fallback only")
    
    def make_decision(self, npc_data: Dict, context: Dict) -> AIResponse:
        start_time = time.time()
        npc_name = npc_data.get('name', 'unknown')
        prompt = self._build_prompt(npc_data, context)
        
        # Check cache first
        cached_response = self.predictive_cache.get_cached_response(npc_data, context)
        if cached_response:
            self.logger.debug(f"Using cached response for {npc_name}")
            response_time_ms = int((time.time() - start_time) * 1000)
            
            # Log cached interaction
            log_ai_interaction(
                npc_name=npc_name,
                request_type="decision",
                prompt=prompt,
                context=context,
                npc_data=npc_data,
                response_raw="[CACHED]",
                response_parsed=cached_response.__dict__,
                provider="cache",
                model=self.model_name,
                response_time_ms=response_time_ms,
                cached=True
            )
            
            return cached_response
        
        response_raw = ""
        provider = ""
        error_message = None
        
        try:
            if self.use_fallback:
                result = self.fallback_client.make_decision(prompt)
                self.logger.info(f"Using {result['provider']} (response time: {result['response_time']:.2f}s)")
                response_raw = result['response']
                provider = result['provider']
                response = self._parse_response(response_raw)
            else:
                api_response = self.client.generate(
                    model=self.model_name,
                    prompt=prompt,
                    options={
                        "temperature": 0.7,
                        "top_p": 0.9,
                        "max_tokens": 150
                    }
                )
                response_raw = api_response['response']
                provider = "ollama"
                response = self._parse_response(response_raw)
            
            # Cache the response
            self.predictive_cache.cache_response(npc_data, context, response)
            
        except Exception as e:
            self.logger.error(f"AI request failed: {e}")
            error_message = str(e)
            
            if not self.use_fallback:
                self.logger.info("Attempting API fallback...")
                try:
                    result = self.fallback_client.make_decision(prompt)
                    self.logger.info(f"Fallback successful using {result['provider']}")
                    response_raw = result['response']
                    provider = f"fallback_{result['provider']}"
                    response = self._parse_response(response_raw)
                    error_message = None  # Clear error since fallback worked
                    
                    # Cache the fallback response
                    self.predictive_cache.cache_response(npc_data, context, response)
                    
                except Exception as fallback_error:
                    self.logger.error(f"Fallback also failed: {fallback_error}")
                    error_message = f"Primary: {e}, Fallback: {fallback_error}"
                    response = self._get_fallback_decision(npc_data, context)
                    response_raw = "[HARDCODED_FALLBACK]"
                    provider = "hardcoded"
            else:
                response = self._get_fallback_decision(npc_data, context)
                response_raw = "[HARDCODED_FALLBACK]"
                provider = "hardcoded"
        
        # Calculate response time
        response_time_ms = int((time.time() - start_time) * 1000)
        
        # Log the complete interaction
        log_ai_interaction(
            npc_name=npc_name,
            request_type="decision",
            prompt=prompt,
            context=context,
            npc_data=npc_data,
            response_raw=response_raw,
            response_parsed=response.__dict__,
            provider=provider,
            model=self.model_name,
            response_time_ms=response_time_ms,
            cached=False,
            error_message=error_message
        )
        
        return response
    
    def make_decision_async(self, npc_data: Dict, context: Dict, callback: Callable[[AIResponse], None]) -> str:
        """
        Make an AI decision asynchronously. Returns a request ID.
        The callback will be called with the result when ready.
        """
        # Check cache first
        cached_response = self.predictive_cache.get_cached_response(npc_data, context)
        if cached_response:
            self.logger.debug(f"Using cached response for async request: {npc_data.get('name', 'unknown')}")
            # Call callback immediately with cached response
            callback(cached_response)
            return f"cached_{time.time()}"
        
        self.request_counter += 1
        request_id = f"req_{self.request_counter}_{time.time()}"
        
        # Store the callback
        self.response_callbacks[request_id] = callback
        
        # Store request info
        self.pending_requests[request_id] = {
            'npc_data': npc_data,
            'context': context,
            'start_time': time.time()
        }
        
        # Start the AI request in a background thread
        thread = threading.Thread(
            target=self._process_async_request,
            args=(request_id, npc_data, context),
            daemon=True
        )
        thread.start()
        
        return request_id
    
    def _process_async_request(self, request_id: str, npc_data: Dict, context: Dict):
        """Process an AI request in the background"""
        try:
            # Use the existing make_decision method (which handles caching internally)
            response = self.make_decision(npc_data, context)
            
            # Call the callback with the result
            if request_id in self.response_callbacks:
                callback = self.response_callbacks[request_id]
                callback(response)
                
                # Clean up
                del self.response_callbacks[request_id]
                if request_id in self.pending_requests:
                    del self.pending_requests[request_id]
                    
        except Exception as e:
            self.logger.error(f"Async AI request {request_id} failed: {e}")
            
            # Provide fallback response
            if request_id in self.response_callbacks:
                callback = self.response_callbacks[request_id]
                fallback_response = self._get_fallback_decision(npc_data, context)
                # Cache the fallback response too
                self.predictive_cache.cache_response(npc_data, context, fallback_response)
                callback(fallback_response)
                
                # Clean up
                del self.response_callbacks[request_id]
                if request_id in self.pending_requests:
                    del self.pending_requests[request_id]
    
    def cancel_request(self, request_id: str) -> bool:
        """Cancel a pending async request"""
        if request_id in self.response_callbacks:
            del self.response_callbacks[request_id]
        if request_id in self.pending_requests:
            del self.pending_requests[request_id]
            return True
        return False
    
    def get_pending_request_count(self) -> int:
        """Get the number of pending async requests"""
        return len(self.pending_requests)
    
    def get_cache_stats(self) -> Dict:
        """Get cache performance statistics"""
        return self.predictive_cache.get_cache_stats()
    
    def invalidate_npc_cache(self, npc_id: str, context_changes: Dict):
        """Invalidate cache for an NPC when context changes significantly"""
        self.predictive_cache.invalidate_npc_cache(npc_id, context_changes)
    
    def shutdown(self):
        """Shutdown the AI client and cache system"""
        if hasattr(self, 'predictive_cache'):
            self.predictive_cache.shutdown()
    
    def _build_prompt(self, npc_data: Dict, context: Dict) -> str:
        prompt = f"""You are {npc_data['name']}, an NPC in a life simulation game.
Your personality: {npc_data['personality_description']}

Current needs:
- Hunger: {npc_data['needs']['hunger']:.2f}
- Sleep: {npc_data['needs']['sleep']:.2f}
- Social: {npc_data['needs']['social']:.2f}
- Fun: {npc_data['needs']['fun']:.2f}

Current situation: {context.get('situation', 'wandering around')}
Nearby NPCs: {', '.join(context.get('nearby_npcs', []))}
Current emotion: {context.get('emotion', 'neutral')}
Active events: {self._format_events(context.get('active_events', []))}

Recent memories:
{self._format_memories(npc_data.get('recent_memories', []))}

Relationships:
{self._format_relationships(npc_data.get('relationships', {}))}

Decide your next action. Respond in JSON format:
{{
    "action": "move_to/talk_to/work/rest/eat/play/attend_event",
    "target": "location or person name or event name",
    "dialogue": "what you want to say (if talking)",
    "emotion": "happy/sad/angry/neutral/excited",
    "reasoning": "brief explanation"
}}"""
        
        return prompt
    
    def _format_events(self, events: List[str]) -> str:
        if not events:
            return "None"
        return "; ".join(events[:3])
    
    def _format_memories(self, memories: List[Dict]) -> str:
        if not memories:
            return "- No recent memories"
        
        formatted = []
        for memory in memories[-5:]:
            try:
                if memory.get('type') == 'interaction':
                    # Handle local NPC memory format (has 'with' and 'relationship')
                    if 'with' in memory and 'relationship' in memory:
                        formatted.append(f"- Talked with {memory['with']} (relationship: {memory['relationship']:.2f})")
                    # Handle database memory format (content describes the interaction)
                    elif 'detail' in memory:
                        formatted.append(f"- Interaction: {memory['detail']}")
                    else:
                        formatted.append(f"- Interaction: (details unavailable)")
                else:
                    # Handle other memory types
                    detail = memory.get('detail', memory.get('content', 'N/A'))
                    memory_type = memory.get('type', 'unknown')
                    formatted.append(f"- {memory_type}: {detail}")
            except Exception as e:
                # Skip malformed memories rather than crashing
                print(f"Warning: Skipping malformed memory: {memory} (error: {e})")
                continue
        
        return "\n".join(formatted)
    
    def _format_relationships(self, relationships: Dict[str, float]) -> str:
        if not relationships:
            return "- No established relationships"
        
        formatted = []
        for npc, value in relationships.items():
            if value > 0.7:
                formatted.append(f"- {npc}: close friend ({value:.2f})")
            elif value > 0.5:
                formatted.append(f"- {npc}: friendly ({value:.2f})")
            elif value < 0.3:
                formatted.append(f"- {npc}: not friendly ({value:.2f})")
            else:
                formatted.append(f"- {npc}: neutral ({value:.2f})")
        
        return "\n".join(formatted[:5])
    
    def _parse_response(self, response_text: str) -> AIResponse:
        try:
            response_text = response_text.strip()
            if response_text.startswith('```json'):
                response_text = response_text[7:]
            if response_text.endswith('```'):
                response_text = response_text[:-3]
            
            data = json.loads(response_text)
            
            return AIResponse(
                action=data.get('action', 'wander'),
                target=data.get('target'),
                dialogue=data.get('dialogue'),
                emotion=data.get('emotion', 'neutral'),
                reasoning=data.get('reasoning')
            )
            
        except json.JSONDecodeError:
            self.logger.warning(f"Failed to parse AI response: {response_text}")
            return self._get_fallback_decision({}, {})
    
    def _get_fallback_decision(self, npc_data: Dict, context: Dict) -> AIResponse:
        needs = npc_data.get('needs', {})
        
        if needs.get('hunger', 1) < 0.3:
            return AIResponse(action="eat", target="restaurant", emotion="hungry")
        elif needs.get('sleep', 1) < 0.3:
            return AIResponse(action="rest", target="home", emotion="tired")
        elif needs.get('social', 1) < 0.3 and context.get('nearby_npcs'):
            return AIResponse(
                action="talk_to",
                target=context['nearby_npcs'][0],
                dialogue="Hey, how are you doing?",
                emotion="friendly"
            )
        else:
            return AIResponse(action="wander", emotion="neutral")