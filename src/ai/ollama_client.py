import ollama
import json
import logging
from typing import Dict, List, Optional
from dataclasses import dataclass
from src.ai.api_fallback import APIFallbackClient

@dataclass
class AIResponse:
    action: str
    target: Optional[str] = None
    dialogue: Optional[str] = None
    emotion: Optional[str] = None
    reasoning: Optional[str] = None

class OllamaClient:
    def __init__(self, model_name: str = "llama2"):
        self.model_name = model_name
        self.client = ollama.Client()
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        self.fallback_client = APIFallbackClient()
        self.use_fallback = False
        
        try:
            models = self.client.list()
            self.logger.info(f"Available models: {models}")
        except Exception as e:
            self.logger.error(f"Failed to connect to Ollama: {e}")
            self.use_fallback = True
    
    def make_decision(self, npc_data: Dict, context: Dict) -> AIResponse:
        prompt = self._build_prompt(npc_data, context)
        
        try:
            if self.use_fallback:
                result = self.fallback_client.make_decision(prompt)
                self.logger.info(f"Using {result['provider']} (response time: {result['response_time']:.2f}s)")
                return self._parse_response(result['response'])
            else:
                response = self.client.generate(
                    model=self.model_name,
                    prompt=prompt,
                    options={
                        "temperature": 0.7,
                        "top_p": 0.9,
                        "max_tokens": 150
                    }
                )
                return self._parse_response(response['response'])
            
        except Exception as e:
            self.logger.error(f"AI request failed: {e}")
            
            if not self.use_fallback:
                self.logger.info("Attempting API fallback...")
                try:
                    result = self.fallback_client.make_decision(prompt)
                    self.logger.info(f"Fallback successful using {result['provider']}")
                    return self._parse_response(result['response'])
                except Exception as fallback_error:
                    self.logger.error(f"Fallback also failed: {fallback_error}")
            
            return self._get_fallback_decision(npc_data, context)
    
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