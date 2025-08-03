import random
import math
import datetime
import time
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
from src.ai.ai_interaction_logger import log_ai_interaction

class BehaviorState(Enum):
    IDLE = "idle"
    WORKING = "working"
    SOCIALIZING = "socializing"
    EXPLORING = "exploring"
    RESTING = "resting"
    EATING = "eating"
    LEARNING = "learning"
    HELPING = "helping"
    PLANNING = "planning"
    SHOPPING = "shopping"

class EmotionalState(Enum):
    HAPPY = "happy"
    SAD = "sad"
    EXCITED = "excited"
    CALM = "calm"
    ANXIOUS = "anxious"
    CONFIDENT = "confident"
    NOSTALGIC = "nostalgic"
    CURIOUS = "curious"
    CONTENT = "content"
    FRUSTRATED = "frustrated"

@dataclass
class AIContext:
    """Enhanced context for AI decision making"""
    time_of_day: str
    weather: str
    season: str
    nearby_npcs: List[str]
    nearby_buildings: List[str]
    nearby_resources: List[str]
    current_events: List[str]
    player_nearby: bool
    player_relationship: float
    recent_activities: List[str]
    unmet_needs: List[str]
    skill_levels: Dict[str, int]
    inventory_items: List[str]
    goals: List[str]
    current_emotion: str
    energy_level: float
    social_battery: float

@dataclass
class BehaviorResponse:
    """Enhanced response with multiple action types"""
    primary_action: str
    secondary_actions: List[str]
    target: Optional[str]
    dialogue: Optional[str]
    emotion: str
    reasoning: str
    duration: float
    success_conditions: List[str]
    failure_fallbacks: List[str]
    memory_tags: List[str]

class EnhancedAIBehavior:
    """
    Advanced AI behavior system with context awareness, goal-oriented planning,
    emotional intelligence, and dynamic adaptation
    """
    
    def __init__(self):
        self.behavior_patterns = self._initialize_behavior_patterns()
        self.goal_templates = self._initialize_goal_templates()
        self.emotional_responses = self._initialize_emotional_responses()
        self.learning_experiences = {}
        self.personality_adaptations = {}
        
    def _initialize_behavior_patterns(self) -> Dict[BehaviorState, Dict]:
        """Initialize complex behavior patterns for different states"""
        return {
            BehaviorState.IDLE: {
                "triggers": ["low_stimulation", "no_immediate_needs", "waiting"],
                "actions": ["observe_surroundings", "self_reflection", "plan_next_activity"],
                "transition_probability": {
                    BehaviorState.EXPLORING: 0.3,
                    BehaviorState.SOCIALIZING: 0.2,
                    BehaviorState.WORKING: 0.25,
                    BehaviorState.PLANNING: 0.15
                },
                "duration_range": (10, 60)
            },
            BehaviorState.WORKING: {
                "triggers": ["skill_development_goal", "resource_need", "scheduled_activity"],
                "actions": ["practice_skill", "gather_resources", "complete_task"],
                "transition_probability": {
                    BehaviorState.RESTING: 0.4,
                    BehaviorState.SOCIALIZING: 0.2,
                    BehaviorState.EATING: 0.2,
                    BehaviorState.IDLE: 0.2
                },
                "duration_range": (120, 300)
            },
            BehaviorState.SOCIALIZING: {
                "triggers": ["nearby_friends", "loneliness", "celebration"],
                "actions": ["start_conversation", "join_group", "organize_activity"],
                "transition_probability": {
                    BehaviorState.PLANNING: 0.3,
                    BehaviorState.EXPLORING: 0.2,
                    BehaviorState.IDLE: 0.3,
                    BehaviorState.HELPING: 0.2
                },
                "duration_range": (60, 180)
            },
            BehaviorState.EXPLORING: {
                "triggers": ["curiosity", "resource_search", "adventure_goal"],
                "actions": ["visit_new_location", "investigate_interesting_object", "map_area"],
                "transition_probability": {
                    BehaviorState.WORKING: 0.35,
                    BehaviorState.RESTING: 0.25,
                    BehaviorState.SOCIALIZING: 0.2,
                    BehaviorState.IDLE: 0.2
                },
                "duration_range": (90, 240)
            },
            BehaviorState.LEARNING: {
                "triggers": ["skill_gap", "observation_opportunity", "teaching_available"],
                "actions": ["observe_expert", "practice_technique", "ask_questions"],
                "transition_probability": {
                    BehaviorState.WORKING: 0.5,
                    BehaviorState.SOCIALIZING: 0.2,
                    BehaviorState.PLANNING: 0.2,
                    BehaviorState.IDLE: 0.1
                },
                "duration_range": (90, 180)
            },
            BehaviorState.HELPING: {
                "triggers": ["friend_in_need", "community_project", "skill_sharing"],
                "actions": ["offer_assistance", "share_resources", "teach_skill"],
                "transition_probability": {
                    BehaviorState.SOCIALIZING: 0.4,
                    BehaviorState.WORKING: 0.3,
                    BehaviorState.RESTING: 0.2,
                    BehaviorState.IDLE: 0.1
                },
                "duration_range": (60, 150)
            },
            BehaviorState.PLANNING: {
                "triggers": ["goal_misalignment", "new_information", "schedule_change"],
                "actions": ["review_goals", "organize_priorities", "schedule_activities"],
                "transition_probability": {
                    BehaviorState.WORKING: 0.4,
                    BehaviorState.EXPLORING: 0.2,
                    BehaviorState.SOCIALIZING: 0.2,
                    BehaviorState.IDLE: 0.2
                },
                "duration_range": (30, 90)
            },
            BehaviorState.RESTING: {
                "triggers": ["fatigue", "low_energy", "stress"],
                "actions": ["find_quiet_place", "relax", "meditate"],
                "transition_probability": {
                    BehaviorState.IDLE: 0.3,
                    BehaviorState.PLANNING: 0.2,
                    BehaviorState.SOCIALIZING: 0.2,
                    BehaviorState.WORKING: 0.3
                },
                "duration_range": (60, 180)
            },
            BehaviorState.EATING: {
                "triggers": ["hunger", "meal_time", "social_meal"],
                "actions": ["find_food", "prepare_meal", "eat"],
                "transition_probability": {
                    BehaviorState.SOCIALIZING: 0.3,
                    BehaviorState.RESTING: 0.2,
                    BehaviorState.WORKING: 0.3,
                    BehaviorState.IDLE: 0.2
                },
                "duration_range": (30, 60)
            },
            BehaviorState.SHOPPING: {
                "triggers": ["need_items", "window_shopping", "social_shopping"],
                "actions": ["browse_shops", "purchase_items", "compare_prices"],
                "transition_probability": {
                    BehaviorState.SOCIALIZING: 0.3,
                    BehaviorState.EXPLORING: 0.2,
                    BehaviorState.IDLE: 0.3,
                    BehaviorState.PLANNING: 0.2
                },
                "duration_range": (45, 120)
            }
        }
    
    def _initialize_goal_templates(self) -> Dict[str, Dict]:
        """Initialize goal templates for different personality types and situations"""
        return {
            "skill_mastery": {
                "description": "Become expert in {skill}",
                "actions": ["practice_skill", "learn_from_expert", "experiment"],
                "success_metrics": ["skill_level_increase", "positive_feedback"],
                "personality_match": ["achievement_oriented", "curious"],
                "duration": "long_term"
            },
            "social_connection": {
                "description": "Build stronger relationships",
                "actions": ["initiate_conversations", "help_others", "organize_events"],
                "success_metrics": ["relationship_improvement", "social_invitations"],
                "personality_match": ["extroverted", "helpful"],
                "duration": "ongoing"
            },
            "resource_accumulation": {
                "description": "Gather valuable resources",
                "actions": ["explore_new_areas", "optimize_gathering", "trade_efficiently"],
                "success_metrics": ["inventory_value", "rare_item_acquisition"],
                "personality_match": ["practical", "persistent"],
                "duration": "medium_term"
            },
            "knowledge_sharing": {
                "description": "Teach others and spread knowledge",
                "actions": ["offer_tutorials", "create_guides", "mentor_newcomers"],
                "success_metrics": ["others_skill_improvement", "community_recognition"],
                "personality_match": ["generous", "knowledgeable"],
                "duration": "ongoing"
            },
            "adventure_seeking": {
                "description": "Discover new experiences",
                "actions": ["explore_unknown_areas", "try_new_activities", "meet_new_people"],
                "success_metrics": ["new_discoveries", "unique_experiences"],
                "personality_match": ["adventurous", "curious"],
                "duration": "medium_term"
            },
            "community_building": {
                "description": "Strengthen community bonds",
                "actions": ["organize_events", "resolve_conflicts", "facilitate_cooperation"],
                "success_metrics": ["community_happiness", "conflict_resolution"],
                "personality_match": ["leader", "empathetic"],
                "duration": "long_term"
            }
        }
    
    def _initialize_emotional_responses(self) -> Dict[str, Dict]:
        """Initialize emotional response patterns"""
        return {
            "success": {
                EmotionalState.HAPPY: 0.4,
                EmotionalState.CONFIDENT: 0.3,
                EmotionalState.EXCITED: 0.2,
                EmotionalState.CONTENT: 0.1
            },
            "failure": {
                EmotionalState.FRUSTRATED: 0.4,
                EmotionalState.SAD: 0.3,
                EmotionalState.ANXIOUS: 0.2,
                EmotionalState.CALM: 0.1  # Some handle failure well
            },
            "social_positive": {
                EmotionalState.HAPPY: 0.5,
                EmotionalState.CONTENT: 0.3,
                EmotionalState.EXCITED: 0.2
            },
            "social_negative": {
                EmotionalState.SAD: 0.4,
                EmotionalState.ANXIOUS: 0.3,
                EmotionalState.FRUSTRATED: 0.3
            },
            "discovery": {
                EmotionalState.EXCITED: 0.4,
                EmotionalState.CURIOUS: 0.3,
                EmotionalState.HAPPY: 0.3
            },
            "nostalgia": {
                EmotionalState.NOSTALGIC: 0.6,
                EmotionalState.CONTENT: 0.3,
                EmotionalState.CALM: 0.1
            }
        }
    
    def generate_advanced_behavior(self, npc_data: Dict, context: AIContext, personality: Dict) -> BehaviorResponse:
        """Generate sophisticated behavior response using enhanced AI prompt"""
        start_time = time.time()
        npc_name = npc_data.get('name', 'unknown')
        
        # Try to use AI-based behavior generation first (more diverse)
        ai_behavior, ai_prompt, model_name = self._generate_ai_behavior(npc_data, context, personality)
        if ai_behavior:
            # Log the AI-based behavior generation with full prompt
            response_time_ms = int((time.time() - start_time) * 1000)
            self._log_enhanced_ai_behavior(npc_name, ai_behavior, ai_prompt, context, npc_data, response_time_ms, model_name)
            return ai_behavior
        
        # Fallback to rule-based behavior if AI fails
        return self._generate_rule_based_behavior(npc_data, context, personality, start_time)
    
    def _generate_ai_behavior(self, npc_data: Dict, context: AIContext, personality: Dict) -> tuple[Optional['BehaviorResponse'], Optional[str], Optional[str]]:
        """Generate behavior using enhanced AI prompt template"""
        try:
            # Try AI generation more frequently since we're using OpenAI now
            import random
            if random.random() > 0.8:  # 80% chance for AI-generated behavior
                return None, None, None
            
            # Import settings to get the current AI provider and model
            from src.ui.settings import Settings
            settings = Settings()
            
            ai_provider = settings.get("ai_provider", "OpenAI")
            
            if ai_provider == "OpenAI":
                # Use OpenAI client for behavior generation
                from src.ai.api_fallback import APIFallbackClient
                api_client = APIFallbackClient()
                openai_model = settings.get("openai_model", "gpt-3.5-turbo")
            else:
                # Fallback to Ollama if selected
                from src.ai.ollama_client import OllamaClient
                ollama_model = settings.get("ollama_model", "llama2")
                ai_client = OllamaClient(model_name=ollama_model)
            
            # Build the enhanced AI prompt
            prompt = self._build_enhanced_ai_prompt(npc_data, context, personality)
            
            # Make AI decision call using enhanced prompt
            try:
                if ai_provider == "OpenAI":
                    # Use OpenAI through the API fallback client
                    response_text = api_client._call_openai(prompt)
                else:
                    # Use Ollama client if available
                    if hasattr(ai_client, 'client') and ai_client.client:
                        api_response = ai_client.client.generate(
                            model=ai_client.model_name,
                            prompt=prompt,
                            options={
                                "temperature": 0.8,
                                "top_p": 0.9,
                                "max_tokens": 200
                            }
                        )
                        response_text = api_response['response'].strip()
                    else:
                        return None, None, None
                
                if response_text:
                    # Parse JSON response
                    import json
                    
                    # Extract JSON from response (handle potential extra text)
                    start_idx = response_text.find('{')
                    end_idx = response_text.rfind('}') + 1
                    
                    if start_idx >= 0 and end_idx > start_idx:
                        json_str = response_text[start_idx:end_idx]
                        ai_response = json.loads(json_str)
                        
                        # Convert AI response to BehaviorResponse
                        behavior_response = BehaviorResponse(
                            primary_action=ai_response.get('action', 'idle'),
                            secondary_actions=ai_response.get('secondary_actions', []),
                            target=None,  # Will be determined later
                            dialogue=ai_response.get('dialogue', ''),
                            emotion=ai_response.get('emotion', 'neutral'),
                            reasoning=ai_response.get('reasoning', ''),
                            duration=float(ai_response.get('duration', 60.0)),
                            success_conditions=[],
                            failure_fallbacks=[],
                            memory_tags=[]
                        )
                        
                        model_name = openai_model if ai_provider == "OpenAI" else ollama_model
                        return behavior_response, prompt, model_name
                    
            except Exception as ai_error:
                print(f"AI generation error for {npc_data.get('name', 'unknown')}: {ai_error}")
                return None, None, None
                
            return None, None, None
            
        except Exception as e:
            print(f"AI behavior generation failed: {e}")
            return None, None, None
    
    def _generate_rule_based_behavior(self, npc_data: Dict, context: AIContext, personality: Dict, start_time: float) -> 'BehaviorResponse':
        """Generate behavior using original rule-based system"""
        npc_name = npc_data.get('name', 'unknown')
        
        # Original rule-based logic
        situation_analysis = self._analyze_situation(context, npc_data, personality)
        behavior_state = self._determine_behavior_state(situation_analysis, personality)
        actions = self._generate_goal_oriented_actions(behavior_state, situation_analysis, personality)
        dialogue = self._generate_contextual_dialogue(behavior_state, context, personality, situation_analysis)
        emotion = self._determine_emotional_response(behavior_state, context, personality, situation_analysis)
        reasoning = self._generate_reasoning(behavior_state, actions, situation_analysis)
        duration = self._calculate_action_duration(behavior_state, actions, personality)
        success_conditions = self._define_success_conditions(behavior_state, actions)
        failure_fallbacks = self._define_failure_fallbacks(behavior_state, actions)
        memory_tags = self._generate_memory_tags(behavior_state, context, actions)
        
        # Create behavior response
        behavior_response = BehaviorResponse(
            primary_action=actions[0] if actions else "idle",
            secondary_actions=actions[1:] if len(actions) > 1 else [],
            target=self._determine_action_target(actions[0] if actions else "idle", context),
            dialogue=dialogue,
            emotion=emotion,
            reasoning=reasoning,
            duration=duration,
            success_conditions=success_conditions,
            failure_fallbacks=failure_fallbacks,
            memory_tags=memory_tags
        )
        
        # Log the rule-based behavior generation
        response_time_ms = int((time.time() - start_time) * 1000)
        self._log_behavior_generation(npc_name, behavior_response, context, npc_data, response_time_ms, "rule_based")
        
        return behavior_response
    
    def _build_enhanced_ai_prompt(self, npc_data: Dict, context: AIContext, personality: Dict) -> str:
        """Build the enhanced AI prompt template"""
        
        # Extract data with safe defaults
        npc_name = npc_data.get('name', 'Unknown')
        npc_personality = npc_data.get('personality_description', 'No personality defined')
        needs = npc_data.get('needs', {})
        
        # Context data
        time_of_day = getattr(context, 'time_of_day', 'unknown')
        weather = getattr(context, 'weather', 'clear')
        season = getattr(context, 'season', 'spring')
        nearby_npcs = getattr(context, 'nearby_npcs', [])
        nearby_buildings = getattr(context, 'nearby_buildings', [])
        nearby_resources = getattr(context, 'nearby_resources', [])
        current_events = getattr(context, 'current_events', [])
        player_nearby = getattr(context, 'player_nearby', False)
        player_relationship = getattr(context, 'player_relationship', 0.5)
        current_emotion = getattr(context, 'current_emotion', 'neutral')
        energy_level = getattr(context, 'energy_level', 1.0)
        social_battery = getattr(context, 'social_battery', 1.0)
        skill_levels = getattr(context, 'skill_levels', {})
        goals = getattr(context, 'goals', [])
        recent_activities = getattr(context, 'recent_activities', [])
        unmet_needs = getattr(context, 'unmet_needs', [])
        
        # Build enhanced prompt
        prompt = f"""You are the behavior engine for a life simulation game (similar to Stardew Valley or The Sims). 
Your job is to generate **rich, varied, and context-aware next actions** for NPCs. 
You must consider needs, emotions, personality, environment, and current events to make decisions feel human-like.

### NPC Information
- Name: {npc_name}
- Personality: {npc_personality}
- Current Emotion: {current_emotion}
- Needs:
  - Hunger: {needs.get('hunger', 0.5):.2f}
  - Sleep: {needs.get('sleep', 0.5):.2f}
  - Social: {needs.get('social', 0.5):.2f}
  - Fun: {needs.get('fun', 0.5):.2f}
- Energy Level: {energy_level:.2f}
- Social Battery: {social_battery:.2f}
- Skills: {skill_levels}
- Goals: {goals}
- Recent Activities: {recent_activities}

### Environment & Context
- Time of Day: {time_of_day}
- Weather: {weather}
- Season: {season}
- Nearby NPCs: {nearby_npcs}
- Nearby Buildings: {nearby_buildings}
- Available Resources: {nearby_resources}
- Current Events: {current_events}
- Unmet Needs: {unmet_needs}
- Player Nearby: {player_nearby} (relationship: {player_relationship:.2f})

### Instructions
1. Think like a real person in this situation with the given personality and needs.
2. Choose an **action** that fits best (examples: seek_food, sleep, socialize, work, explore, rest, wait, pause, review_goals, organize_priorities, schedule_activities, visit_new_location, talk_to_npc, gather_resources, craft_item, read_book, exercise, meditate).
3. Generate natural **dialogue** the NPC might say out loud or think internally.
4. Pick an appropriate **emotion** (joy, sadness, curiosity, love, calm, excited, lonely, hungry, tired, playful, grateful, content, anxious, hopeful, etc.).
5. Provide **reasoning** that explains why this is the right choice.
6. Set a **duration** (seconds) based on the complexity of the action.
7. Optionally add **secondary_actions** (e.g., wave_to_friend, glance_around, whistle, stretch, yawn).
8. Ensure variation across NPCs and over time – do not repeat actions or dialogue unless it makes sense.

### Output (JSON only)
{{
  "action": "...",
  "dialogue": "...",
  "emotion": "...",
  "reasoning": "...",
  "duration": <float>,
  "secondary_actions": ["...", "..."]
}}"""
        
        return prompt
    
    def _log_behavior_generation(self, npc_name: str, behavior_response: 'BehaviorResponse', 
                                context: AIContext, npc_data: Dict, response_time_ms: int, provider: str):
        """Log behavior generation for analysis"""
        response_dict = {
            "action": behavior_response.primary_action,
            "target": behavior_response.target,
            "dialogue": behavior_response.dialogue,
            "emotion": behavior_response.emotion,
            "reasoning": behavior_response.reasoning,
            "duration": behavior_response.duration,
            "secondary_actions": behavior_response.secondary_actions
        }
        
        prompt_summary = f"Enhanced AI Behavior Generation for {npc_name}\n"
        prompt_summary += f"Provider: {provider}\n"
        prompt_summary += f"Context: Time={getattr(context, 'time_of_day', 'unknown')}, "
        prompt_summary += f"NPCs={getattr(context, 'nearby_npcs', [])}, "
        prompt_summary += f"Emotion={getattr(context, 'current_emotion', 'neutral')}"
        
        log_ai_interaction(
            npc_name=npc_name,
            request_type="enhanced_behavior",
            prompt=prompt_summary,
            context=context.__dict__,
            npc_data=npc_data,
            response_raw=f"Enhanced behavior generated: {behavior_response.primary_action}",
            response_parsed=response_dict,
            provider=f"enhanced_ai_engine_{provider}",
            model="enhanced" if provider == "enhanced_ai_prompt" else "rule_based",
            response_time_ms=response_time_ms,
            cached=False
        )
    
    def _log_enhanced_ai_behavior(self, npc_name: str, behavior_response: 'BehaviorResponse', 
                                  full_prompt: str, context: AIContext, npc_data: Dict, response_time_ms: int, model_name: str = "gpt-3.5-turbo"):
        """Log AI-generated behavior with full enhanced prompt"""
        response_dict = {
            "action": behavior_response.primary_action,
            "target": behavior_response.target,
            "dialogue": behavior_response.dialogue,
            "emotion": behavior_response.emotion,
            "reasoning": behavior_response.reasoning,
            "duration": behavior_response.duration,
            "secondary_actions": behavior_response.secondary_actions
        }
        
        log_ai_interaction(
            npc_name=npc_name,
            request_type="enhanced_ai_behavior",
            prompt=full_prompt,  # Log the full enhanced prompt
            context=context.__dict__,
            npc_data=npc_data,
            response_raw=f"Enhanced AI behavior: {behavior_response.primary_action} - {behavior_response.dialogue}",
            response_parsed=response_dict,
            provider="enhanced_ai_openai",
            model=model_name,
            response_time_ms=response_time_ms,
            cached=False
        )
    
    def _analyze_situation(self, context: AIContext, npc_data: Dict, personality: Dict) -> Dict:
        """Comprehensive situation analysis"""
        analysis = {
            "urgency_level": 0.0,
            "social_opportunities": 0.0,
            "learning_opportunities": 0.0,
            "resource_opportunities": 0.0,
            "safety_level": 1.0,
            "stimulation_level": 0.0,
            "goal_alignment": 0.0,
            "energy_efficiency": 1.0
        }
        
        # Analyze needs urgency
        needs = npc_data.get("needs", {})
        for need, value in needs.items():
            if value < 0.3:
                analysis["urgency_level"] += 0.3
        
        # Social opportunities
        if context.nearby_npcs:
            analysis["social_opportunities"] = min(1.0, len(context.nearby_npcs) * 0.2)
            if context.player_nearby and context.player_relationship > 0.5:
                analysis["social_opportunities"] += 0.3
        
        # Learning opportunities
        if context.nearby_npcs:
            # Check if nearby NPCs have higher skills
            analysis["learning_opportunities"] = 0.3
        
        # Resource opportunities
        if context.nearby_resources:
            analysis["resource_opportunities"] = min(1.0, len(context.nearby_resources) * 0.25)
        
        # Stimulation level
        analysis["stimulation_level"] = len(context.current_events) * 0.2
        if context.nearby_npcs:
            analysis["stimulation_level"] += len(context.nearby_npcs) * 0.1
        
        # Energy considerations
        analysis["energy_efficiency"] = context.energy_level
        
        return analysis
    
    def _determine_behavior_state(self, situation_analysis: Dict, personality: Dict) -> BehaviorState:
        """Determine appropriate behavior state based on analysis"""
        
        state_scores = {}
        
        # Calculate scores for each potential state
        for state in BehaviorState:
            score = 0.0
            
            if state == BehaviorState.SOCIALIZING:
                score += situation_analysis["social_opportunities"] * 0.5
                score += personality.get("friendliness", 0.5) * 0.3
                score -= (1 - situation_analysis["energy_efficiency"]) * 0.2
            
            elif state == BehaviorState.WORKING:
                score += (1 - situation_analysis["urgency_level"]) * 0.3
                score += personality.get("dedication", 0.5) * 0.4
                score += situation_analysis["resource_opportunities"] * 0.3
            
            elif state == BehaviorState.LEARNING:
                score += situation_analysis["learning_opportunities"] * 0.6
                score += personality.get("curiosity", 0.5) * 0.4
            
            elif state == BehaviorState.EXPLORING:
                score += personality.get("adventurousness", 0.5) * 0.5
                score += (1 - situation_analysis["stimulation_level"]) * 0.3
                score += situation_analysis["energy_efficiency"] * 0.2
            
            elif state == BehaviorState.RESTING:
                score += (1 - situation_analysis["energy_efficiency"]) * 0.8
                score += situation_analysis["urgency_level"] * 0.2
            
            elif state == BehaviorState.HELPING:
                score += personality.get("helpfulness", 0.5) * 0.6
                score += situation_analysis["social_opportunities"] * 0.4
            
            elif state == BehaviorState.PLANNING:
                score += personality.get("organization", 0.5) * 0.5
                score += (1 - situation_analysis["goal_alignment"]) * 0.5
            
            state_scores[state] = max(0, score)
        
        # Add some randomness
        for state in state_scores:
            state_scores[state] += random.uniform(0, 0.2)
        
        return max(state_scores, key=state_scores.get)
    
    def _generate_goal_oriented_actions(self, behavior_state: BehaviorState, situation_analysis: Dict, personality: Dict) -> List[str]:
        """Generate actions aligned with long-term goals"""
        
        base_actions = self.behavior_patterns[behavior_state]["actions"]
        actions = []
        
        # Primary action based on behavior state
        primary_action = random.choice(base_actions)
        actions.append(primary_action)
        
        # Add secondary actions based on opportunities
        if situation_analysis["social_opportunities"] > 0.5 and behavior_state != BehaviorState.SOCIALIZING:
            actions.append("acknowledge_nearby_people")
        
        if situation_analysis["learning_opportunities"] > 0.5:
            actions.append("observe_and_learn")
        
        if situation_analysis["resource_opportunities"] > 0.5 and behavior_state != BehaviorState.WORKING:
            actions.append("note_resource_location")
        
        return actions[:3]  # Limit to 3 actions
    
    def _generate_contextual_dialogue(self, behavior_state: BehaviorState, context: AIContext, personality: Dict, situation_analysis: Dict) -> Optional[str]:
        """Generate contextually appropriate dialogue"""
        
        dialogue_templates = {
            BehaviorState.SOCIALIZING: [
                "It's so nice to see everyone today!",
                "I love spending time with good friends.",
                "What brings you here today?",
                "Have you been having a good day?"
            ],
            BehaviorState.WORKING: [
                "I'm really focused on improving my {skill} today.",
                "There's something satisfying about productive work.",
                "I want to get better at {activity}.",
                "Hard work always pays off in the end."
            ],
            BehaviorState.EXPLORING: [
                "I wonder what's over there...",
                "There's so much to discover in this world!",
                "I love finding new places and things.",
                "Adventure is calling!"
            ],
            BehaviorState.LEARNING: [
                "I'm always eager to learn something new.",
                "Watching others work teaches me so much.",
                "Knowledge is the best treasure.",
                "I wonder how that works..."
            ],
            BehaviorState.HELPING: [
                "Is there anything I can help you with?",
                "I love being useful to my community.",
                "We're stronger when we work together.",
                "Let me know if you need a hand!"
            ],
            BehaviorState.PLANNING: [
                "I need to think about my priorities.",
                "Organization is the key to success.",
                "Let me plan out my next steps.",
                "A good plan makes all the difference."
            ]
        }
        
        templates = dialogue_templates.get(behavior_state, ["Hello there!"])
        base_dialogue = random.choice(templates)
        
        # Contextual replacements
        skills = ["farming", "mining", "foraging", "fishing", "crafting"]
        activities = ["gathering", "exploring", "building", "cooking", "reading"]
        
        base_dialogue = base_dialogue.replace("{skill}", random.choice(skills))
        base_dialogue = base_dialogue.replace("{activity}", random.choice(activities))
        
        # Personality modifications
        if personality.get("enthusiasm", 0.5) > 0.7:
            if not base_dialogue.endswith("!"):
                base_dialogue += "!"
        
        # Only return dialogue if it makes sense for the context
        if context.player_nearby or context.nearby_npcs:
            return base_dialogue
        
        return None
    
    def _determine_emotional_response(self, behavior_state: BehaviorState, context: AIContext, personality: Dict, situation_analysis: Dict) -> str:
        """Determine emotional state based on context and personality"""
        
        base_emotions = {
            BehaviorState.SOCIALIZING: EmotionalState.HAPPY,
            BehaviorState.WORKING: EmotionalState.CONTENT,
            BehaviorState.EXPLORING: EmotionalState.CURIOUS,
            BehaviorState.LEARNING: EmotionalState.CURIOUS,
            BehaviorState.HELPING: EmotionalState.CONTENT,
            BehaviorState.PLANNING: EmotionalState.CALM,
            BehaviorState.RESTING: EmotionalState.CALM,
            BehaviorState.IDLE: EmotionalState.CONTENT
        }
        
        emotion = base_emotions.get(behavior_state, EmotionalState.CONTENT)
        
        # Modify based on situation
        if situation_analysis["urgency_level"] > 0.7:
            emotion = EmotionalState.ANXIOUS
        elif situation_analysis["social_opportunities"] > 0.8 and personality.get("friendliness", 0.5) > 0.7:
            emotion = EmotionalState.EXCITED
        elif context.energy_level < 0.3:
            emotion = EmotionalState.CALM  # Tired, calm
        
        return emotion.value
    
    def _generate_reasoning(self, behavior_state: BehaviorState, actions: List[str], situation_analysis: Dict) -> str:
        """Generate explanation for the chosen behavior"""
        
        reasoning_templates = {
            BehaviorState.SOCIALIZING: "I want to connect with others and strengthen relationships",
            BehaviorState.WORKING: "I need to be productive and improve my skills",
            BehaviorState.EXPLORING: "I'm curious about the world and want to discover new things",
            BehaviorState.LEARNING: "Knowledge and growth are important to me",
            BehaviorState.HELPING: "I enjoy supporting my community and friends",
            BehaviorState.PLANNING: "I need to organize my thoughts and set priorities",
            BehaviorState.RESTING: "I need to recharge and take care of myself"
        }
        
        base_reasoning = reasoning_templates.get(behavior_state, "I'm deciding what to do next")
        
        # Add context-specific reasoning
        if situation_analysis["urgency_level"] > 0.5:
            base_reasoning += " while addressing my immediate needs"
        
        if situation_analysis["social_opportunities"] > 0.5:
            base_reasoning += " and taking advantage of social opportunities"
        
        return base_reasoning
    
    def _calculate_action_duration(self, behavior_state: BehaviorState, actions: List[str], personality: Dict) -> float:
        """Calculate how long this behavior should last"""
        
        base_duration = self.behavior_patterns[behavior_state]["duration_range"]
        duration = random.uniform(base_duration[0], base_duration[1])
        
        # Personality adjustments
        if personality.get("patience", 0.5) > 0.7:
            duration *= 1.3
        elif personality.get("restlessness", 0.5) > 0.7:
            duration *= 0.7
        
        return duration
    
    def _define_success_conditions(self, behavior_state: BehaviorState, actions: List[str]) -> List[str]:
        """Define what constitutes success for this behavior"""
        
        success_conditions = {
            BehaviorState.SOCIALIZING: ["positive_interaction", "relationship_improvement"],
            BehaviorState.WORKING: ["skill_increase", "resource_gained", "task_completed"],
            BehaviorState.EXPLORING: ["new_location_discovered", "interesting_object_found"],
            BehaviorState.LEARNING: ["knowledge_gained", "skill_observed"],
            BehaviorState.HELPING: ["assistance_provided", "positive_feedback"],
            BehaviorState.PLANNING: ["goals_clarified", "priorities_set"]
        }
        
        return success_conditions.get(behavior_state, ["action_completed"])
    
    def _define_failure_fallbacks(self, behavior_state: BehaviorState, actions: List[str]) -> List[str]:
        """Define fallback actions if primary behavior fails"""
        
        fallbacks = {
            BehaviorState.SOCIALIZING: ["idle", "explore_nearby"],
            BehaviorState.WORKING: ["rest", "plan_better_approach"],
            BehaviorState.EXPLORING: ["return_to_familiar_area", "rest"],
            BehaviorState.LEARNING: ["observe_from_distance", "try_different_approach"],
            BehaviorState.HELPING: ["offer_different_help", "apologize_and_retreat"],
            BehaviorState.PLANNING: ["take_break", "start_simple_task"]
        }
        
        return fallbacks.get(behavior_state, ["idle", "wander"])
    
    def _determine_action_target(self, action: str, context: AIContext) -> Optional[str]:
        """Determine the target for the action"""
        
        if action in ["start_conversation", "talk_to", "help"]:
            if context.player_nearby and context.player_relationship > 0.4:
                return "player"
            elif context.nearby_npcs:
                return random.choice(context.nearby_npcs)
        
        elif action in ["gather_resources", "practice_skill"]:
            if context.nearby_resources:
                return random.choice(context.nearby_resources)
        
        elif action in ["visit_location", "explore"]:
            if context.nearby_buildings:
                return random.choice(context.nearby_buildings)
        
        return None
    
    def _generate_memory_tags(self, behavior_state: BehaviorState, context: AIContext, actions: List[str]) -> List[str]:
        """Generate tags for memory categorization"""
        
        tags = [behavior_state.value]
        
        if context.player_nearby:
            tags.append("player_interaction")
        
        if context.nearby_npcs:
            tags.append("social_context")
        
        if context.current_events:
            tags.append("event_context")
        
        tags.extend(actions[:2])  # Add primary actions as tags
        
        return list(set(tags))  # Remove duplicates
    
    def learn_from_outcome(self, npc_name: str, behavior_response: BehaviorResponse, outcome: str, success: bool):
        """Learn from the outcome of behaviors to improve future decisions"""
        
        if npc_name not in self.learning_experiences:
            self.learning_experiences[npc_name] = []
        
        experience = {
            "behavior": behavior_response.primary_action,
            "context_tags": behavior_response.memory_tags,
            "outcome": outcome,
            "success": success,
            "timestamp": datetime.datetime.now().isoformat()
        }
        
        self.learning_experiences[npc_name].append(experience)
        
        # Keep only recent experiences (last 50)
        if len(self.learning_experiences[npc_name]) > 50:
            self.learning_experiences[npc_name] = self.learning_experiences[npc_name][-50:]
        
        # Update personality adaptations based on repeated successes/failures
        self._update_personality_adaptations(npc_name, behavior_response, success)
    
    def _update_personality_adaptations(self, npc_name: str, behavior_response: BehaviorResponse, success: bool):
        """Update personality adaptations based on learning"""
        
        if npc_name not in self.personality_adaptations:
            self.personality_adaptations[npc_name] = {}
        
        behavior = behavior_response.primary_action
        
        if behavior not in self.personality_adaptations[npc_name]:
            self.personality_adaptations[npc_name][behavior] = {"success_count": 0, "failure_count": 0}
        
        if success:
            self.personality_adaptations[npc_name][behavior]["success_count"] += 1
        else:
            self.personality_adaptations[npc_name][behavior]["failure_count"] += 1
    
    def get_personality_preferences(self, npc_name: str) -> Dict[str, float]:
        """Get learned personality preferences for behavior selection"""
        
        if npc_name not in self.personality_adaptations:
            return {}
        
        preferences = {}
        adaptations = self.personality_adaptations[npc_name]
        
        for behavior, counts in adaptations.items():
            total = counts["success_count"] + counts["failure_count"]
            if total > 0:
                success_rate = counts["success_count"] / total
                preferences[behavior] = success_rate
        
        return preferences