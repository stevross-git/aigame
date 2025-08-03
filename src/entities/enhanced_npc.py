import pygame
import random
import math
import datetime
from typing import Dict, List, Optional, Tuple, Any
from src.core.constants import *
from src.entities.personality import Personality
from src.ai.ollama_client import AIResponse
from src.ai.ai_client_manager import AIClientManager
from src.ai.memory_manager import MemoryManager, Memory
from src.ai.conversation_engine import ConversationEngine, ConversationContext, ConversationTopic
from src.ai.enhanced_ai_behavior import EnhancedAIBehavior, AIContext, BehaviorState
from src.ai.emotional_intelligence import EmotionalIntelligence, EmotionalState, EmotionType
from src.graphics.custom_asset_manager import CustomAssetManager
from src.systems.social_system import SocialSystem, InteractionType, InteractionRating

class EnhancedNPC(pygame.sprite.Sprite):
    """
    Advanced NPC with enhanced AI capabilities including:
    - Sophisticated conversation system
    - Emotional intelligence and empathy
    - Context-aware behavior planning
    - Learning and adaptation
    - Complex social interactions
    """
    
    def __init__(self, x, y, name, personality_traits=None, memory_manager=None, skip_ai_init=False):
        super().__init__()
        
        # Initialize custom asset manager for beautiful sprites
        self.assets = CustomAssetManager()
        
        # Get character sprite based on name with animation support
        self.idle_sprite = self.assets.get_character_sprite(name)
        self.walk_sprite = self.assets.get_sprite("npc_walk") or self.assets.get_sprite("walking")
        
        if self.idle_sprite:
            self.image = self.idle_sprite.copy()
        else:
            # Fallback to colored square
            self.image = pygame.Surface((24, 32))
            self.image.fill(RED)
        
        # Animation state
        self.is_moving = False
        self.animation_timer = 0.0
        
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        
        self.name = name
        if personality_traits:
            self.personality = Personality(**personality_traits)
        else:
            self.personality = Personality.generate_random()
        
        self.speed = NPC_SPEED
        self.velocity = pygame.math.Vector2(0, 0)
        
        # Basic needs
        self.needs = {
            "hunger": 1.0,
            "sleep": 1.0,
            "social": 1.0,
            "fun": 1.0
        }
        
        # Enhanced systems
        self.relationships = {}
        self.memory = []
        
        # Movement and behavior state
        self.state = "idle"
        self.target_pos = None
        self.target_entity = None  # Can track and follow entities
        self.wander_timer = 0
        self.interaction_cooldown = 0
        self.ai_decision_cooldown = 0
        self.quest_to_give = None  # Quest ID to give when reaching player
        self.approach_message = None  # Message to say when approaching
        
        # Wait action state
        self.is_waiting = False
        self.wait_timer = 0.0
        self.wait_duration = 0.0
        self.wait_reason = None
        
        # AI and conversation systems
        self.ai_client = None
        self.current_dialogue = None
        self.dialogue_timer = 0
        self.memory_manager = memory_manager
        self.ai_response_box = None
        
        # Enhanced AI systems
        self.conversation_engine = ConversationEngine()
        self.ai_behavior = EnhancedAIBehavior()
        self.emotional_intelligence = EmotionalIntelligence()
        
        # Emotional state
        self.emotional_state = EmotionalState(
            primary_emotion=EmotionType.JOY,
            intensity=0.5,
            secondary_emotions={EmotionType.TRUST: 0.3},
            duration=0.0,
            triggers=[]
        )
        
        # Enhanced interaction state
        self.player_interaction_context = None
        self.chat_interface = None
        self.conversation_history = {}
        self.current_conversation_topic = None
        self.social_battery = 1.0
        self.energy_level = 1.0
        
        # Learning and adaptation
        self.learned_preferences = {}
        self.behavior_success_rates = {}
        self.social_observations = {}
        
        # Social interaction system
        self.social_system = None  # Will be set by game
        self.last_interaction_rating = None
        self.interaction_history = []  # Track recent interactions for learning
        
        # Goals and planning
        self.current_goals = []
        self.long_term_goals = []
        self.daily_schedule = {}
        
        # Context awareness
        self.environmental_awareness = {
            "known_locations": [],
            "resource_knowledge": {},
            "social_network": {},
            "recent_events": []
        }
        
        # House system integration
        self.house_manager = None  # Will be set by game
        
        # Only initialize AI if not skipping
        if not skip_ai_init:
            try:
                ai_manager = AIClientManager()
                self.ai_client = ai_manager.create_ai_client()
                if self.memory_manager:
                    self._load_memories()
            except Exception as e:
                print(f"Failed to initialize AI for {name}: {e}")
                self.ai_client = None
        else:
            self.ai_client = None
    
    def update(self, dt, other_npcs, active_events=None):
        """Enhanced update with sophisticated AI processing"""
        # Update wait timer if waiting
        if self.is_waiting:
            self.wait_timer -= dt
            if self.wait_timer <= 0:
                self.stop_wait()
        
        # Update basic systems
        self._update_needs(dt)
        self._update_emotional_state(dt, other_npcs, active_events)
        self._update_social_awareness(other_npcs)
        self._update_environmental_awareness(active_events)
        
        # Enhanced AI behavior update (skip if waiting)
        if not self.is_waiting:
            self._update_enhanced_ai_behavior(dt, other_npcs, active_events)
        
        # Movement and animation (skip movement if waiting)
        if not self.is_waiting:
            self._move(dt)
        self._update_animation(dt)
        
        # Check if NPC should go home for stat restoration
        self._check_home_needs(dt)
        
        # Update timers
        if self.interaction_cooldown > 0:
            self.interaction_cooldown -= dt
        
        if self.dialogue_timer > 0:
            self.dialogue_timer -= dt
            if self.dialogue_timer <= 0:
                self.current_dialogue = None
    
    def _update_needs(self, dt):
        """Update basic needs with emotional modifiers"""
        base_decay_rates = {
            "hunger": 0.01,
            "sleep": 0.008,
            "social": 0.012,
            "fun": 0.006
        }
        
        # Apply emotional modifiers to need decay
        emotional_modifiers = self.emotional_intelligence.get_behavior_modifiers(self.emotional_state)
        
        for need, base_rate in base_decay_rates.items():
            modified_rate = base_rate
            
            # Emotional states affect need decay differently
            if need == "social" and "social_interaction" in emotional_modifiers:
                modified_rate *= (2.0 - emotional_modifiers["social_interaction"])
            elif need == "fun" and self.emotional_state.primary_emotion == EmotionType.JOY:
                modified_rate *= 0.5  # Joy reduces fun decay
            elif need == "sleep" and self.emotional_state.primary_emotion == EmotionType.FEAR:
                modified_rate *= 1.5  # Fear increases sleep need
            
            self.needs[need] -= modified_rate * dt
            self.needs[need] = max(0, min(1, self.needs[need]))
    
    def _update_emotional_state(self, dt, other_npcs, active_events):
        """Update emotional state using advanced emotional intelligence"""
        # Gather events that might trigger emotions
        events = []
        
        # Add active events as potential triggers
        if active_events:
            for event in active_events:
                events.append(f"Event: {event.title}")
        
        # Add social context events
        if self.player_interaction_context:
            events.append(f"Player interaction: {self.player_interaction_context}")
        
        # Check for need-based emotional triggers
        for need, value in self.needs.items():
            if value < 0.3:
                events.append(f"Low {need}")
            elif value > 0.8:
                events.append(f"Satisfied {need}")
        
        # Gather social context
        social_context = {
            "nearby_npcs": [npc.name for npc in other_npcs if self._get_distance(npc) < 100],
            "nearby_emotions": {},
            "relationships": self.relationships.copy()
        }
        
        # Add emotional states of nearby NPCs for contagion
        for npc in other_npcs:
            if self._get_distance(npc) < 100 and hasattr(npc, 'emotional_state'):
                social_context["nearby_emotions"][npc.name] = {
                    "emotion": npc.emotional_state.primary_emotion.value,
                    "intensity": npc.emotional_state.intensity
                }
        
        # Update emotional state
        self.emotional_state = self.emotional_intelligence.update_emotional_state(
            self.name, self.emotional_state, events, social_context,
            self.personality.traits, dt
        )
        
        # Store significant emotional memories
        if self.emotional_state.intensity > 0.7:
            self.emotional_intelligence.store_emotional_memory(
                self.name,
                f"Felt {self.emotional_state.primary_emotion.value} intensely",
                {self.emotional_state.primary_emotion: self.emotional_state.intensity},
                [npc.name for npc in other_npcs if self._get_distance(npc) < 50],
                (self.rect.centerx, self.rect.centery),
                self.emotional_state.intensity,
                datetime.datetime.now().isoformat()
            )
    
    def _update_social_awareness(self, other_npcs):
        """Update awareness of social dynamics"""
        for npc in other_npcs:
            if self._get_distance(npc) < 150:
                # Observe other NPCs' behaviors and emotions
                if hasattr(npc, 'emotional_state'):
                    observation = {
                        "emotion": npc.emotional_state.primary_emotion.value,
                        "intensity": npc.emotional_state.intensity,
                        "timestamp": datetime.datetime.now().isoformat()
                    }
                    
                    if npc.name not in self.social_observations:
                        self.social_observations[npc.name] = []
                    
                    self.social_observations[npc.name].append(observation)
                    
                    # Keep only recent observations
                    if len(self.social_observations[npc.name]) > 10:
                        self.social_observations[npc.name] = self.social_observations[npc.name][-10:]
    
    def _update_environmental_awareness(self, active_events):
        """Update awareness of environmental changes"""
        if active_events:
            for event in active_events:
                event_info = {
                    "title": event.title,
                    "description": event.description,
                    "location": event.location,
                    "timestamp": datetime.datetime.now().isoformat()
                }
                
                self.environmental_awareness["recent_events"].append(event_info)
                
                # Keep only recent events
                if len(self.environmental_awareness["recent_events"]) > 20:
                    self.environmental_awareness["recent_events"] = self.environmental_awareness["recent_events"][-20:]
    
    def _update_enhanced_ai_behavior(self, dt, other_npcs, active_events):
        """Update AI behavior using enhanced systems"""
        self.ai_decision_cooldown -= dt
        
        if self.ai_decision_cooldown <= 0 and self.ai_client:
            # Build enhanced context
            context = self._build_enhanced_context(other_npcs, active_events)
            
            # Get behavior response from enhanced AI
            behavior_response = self.ai_behavior.generate_advanced_behavior(
                self._get_enhanced_npc_data(), context, self.personality.traits
            )
            
            # Execute the behavior
            self._execute_enhanced_behavior(behavior_response, other_npcs, active_events)
            
            # ALSO make actual AI decision call to Ollama (in addition to enhanced behavior)
            # This will generate the detailed AI interaction logs
            if random.random() < 0.2:  # 20% chance to make actual AI call for analysis
                try:
                    # Build context for Ollama AI
                    ai_context = {
                        'situation': self.current_action or 'wandering around',
                        'nearby_npcs': [npc.name for npc in other_npcs if self._get_distance(npc) < 100],
                        'emotion': self.current_emotion,
                        'active_events': [event.title for event in active_events] if active_events else []
                    }
                    
                    # Make actual AI decision call (this will be logged)
                    # This provides detailed AI interaction data for analysis
                    npc_data = self._get_npc_data()
                    ai_response = self.ai_client.make_decision(npc_data, ai_context)
                    
                    # Optional: Could blend AI response with enhanced behavior for variety
                    # For now, we use enhanced behavior as primary, AI as supplementary data
                    
                except Exception as e:
                    # AI calls may fail due to memory constraints or network issues
                    # Enhanced behavior provides reliable fallback
                    pass
            
            # Send response to AI response box
            if self.ai_response_box:
                self.ai_response_box.add_response(
                    self.name,
                    behavior_response.primary_action,
                    behavior_response.reasoning,
                    behavior_response.dialogue
                )
            
            # Reset cooldown with some variation
            self.ai_decision_cooldown = random.uniform(10.0, 20.0)  # Increased for performance
            
            # Clear player interaction context after processing
            self.player_interaction_context = None
    
    def _build_enhanced_context(self, other_npcs, active_events) -> AIContext:
        """Build comprehensive context for AI decision making"""
        nearby_npcs = [npc.name for npc in other_npcs if self._get_distance(npc) < 100]
        nearby_buildings = []  # Could be enhanced to detect actual buildings
        nearby_resources = []  # Could be enhanced to detect actual resources
        current_events = [event.title for event in active_events] if active_events else []
        
        player_nearby = False
        player_relationship = 0.5
        # Player detection and relationship would need to be passed from game
        
        recent_activities = [memory.get("action", "") for memory in self.memory[-5:]]
        
        unmet_needs = [need for need, value in self.needs.items() if value < 0.4]
        
        # Basic skill levels (could be enhanced with actual skill system)
        skill_levels = {"social": 5, "work": 3, "creativity": 4}
        
        inventory_items = []  # Could be enhanced with actual inventory
        
        goals = self.current_goals.copy()
        
        return AIContext(
            time_of_day=self._get_time_of_day(),
            weather="sunny",  # Could be enhanced with weather system
            season="spring",  # Could be enhanced with season system
            nearby_npcs=nearby_npcs,
            nearby_buildings=nearby_buildings,
            nearby_resources=nearby_resources,
            current_events=current_events,
            player_nearby=player_nearby,
            player_relationship=player_relationship,
            recent_activities=recent_activities,
            unmet_needs=unmet_needs,
            skill_levels=skill_levels,
            inventory_items=inventory_items,
            goals=goals,
            current_emotion=self.emotional_state.primary_emotion.value,
            energy_level=self.energy_level,
            social_battery=self.social_battery
        )
    
    def _get_enhanced_npc_data(self) -> Dict:
        """Get comprehensive NPC data for AI processing"""
        base_data = self._get_npc_data()
        
        # Add enhanced data
        base_data.update({
            "emotional_state": {
                "primary_emotion": self.emotional_state.primary_emotion.value,
                "intensity": self.emotional_state.intensity,
                "secondary_emotions": {e.value: i for e, i in self.emotional_state.secondary_emotions.items()}
            },
            "social_observations": self.social_observations,
            "environmental_awareness": self.environmental_awareness,
            "learned_preferences": self.learned_preferences,
            "current_goals": self.current_goals,
            "conversation_history": list(self.conversation_history.keys())
        })
        
        return base_data
    
    def _execute_enhanced_behavior(self, behavior_response, other_npcs, active_events):
        """Execute sophisticated behavior response"""
        action = behavior_response.primary_action
        target = behavior_response.target
        dialogue = behavior_response.dialogue
        
        # Set emotion based on behavior
        self.emotion = behavior_response.emotion
        
        # Execute primary action
        if action == "start_conversation" or action == "talk_to":
            target_npc = self._find_npc_by_name(target, other_npcs) if target else None
            if target_npc:
                self._start_enhanced_conversation(target_npc)
        
        elif action == "explore" or action == "move_to":
            self._set_exploration_target()
        
        elif action == "help" or action == "offer_assistance":
            target_npc = self._find_npc_by_name(target, other_npcs) if target else None
            if target_npc:
                self._offer_help(target_npc)
        
        elif action == "practice_skill" or action == "learn":
            self._practice_skill()
        
        elif action == "rest" or action == "relax":
            self._rest()
        
        elif action == "wait" or action == "pause":
            # Start waiting with AI-determined duration and reason
            wait_duration = behavior_response.duration if behavior_response.duration > 0 else random.uniform(3.0, 10.0)
            wait_reason = dialogue or "Taking a moment to think..."
            self.start_wait(wait_duration, wait_reason)
        
        else:
            # Default wandering behavior
            self._wander()
        
        # Set dialogue if provided
        if dialogue:
            self.say(dialogue)
        
        # Learn from this behavior execution
        self._learn_from_behavior(behavior_response, "executed")
    
    def _start_enhanced_conversation(self, target_npc):
        """Start sophisticated conversation with another NPC"""
        if not hasattr(target_npc, 'emotional_state'):
            return  # Can't have enhanced conversation with basic NPC
        
        # Build conversation context
        relationship_level = self.relationships.get(target_npc.name, 0.5)
        
        # Get shared experiences
        shared_experiences = []
        if target_npc.name in self.conversation_history:
            shared_experiences = [conv["topic"] for conv in self.conversation_history[target_npc.name][-3:]]
        
        # Get recent topics to avoid repetition
        previous_topics = []
        if target_npc.name in self.conversation_history:
            previous_topics = [ConversationTopic(conv["topic"]) for conv in self.conversation_history[target_npc.name][-5:]]
        
        context = ConversationContext(
            topic=ConversationTopic.WEATHER,  # Will be chosen by engine
            initiator=self.name,
            participant=target_npc.name,
            relationship_level=relationship_level,
            location=(self.rect.centerx, self.rect.centery),
            time_of_day=self._get_time_of_day(),
            mood=self.emotional_state.primary_emotion.value,
            previous_topics=previous_topics,
            shared_experiences=shared_experiences,
            current_events=[]
        )
        
        # Generate conversation response
        response = self.conversation_engine.generate_conversation(
            context, self.personality.traits, self.ai_client
        )
        
        # Execute conversation
        if response.dialogue:
            self.say(response.dialogue)
        
        # Update relationship
        if target_npc.name not in self.relationships:
            self.relationships[target_npc.name] = 0.5
        
        self.relationships[target_npc.name] += response.relationship_change
        self.relationships[target_npc.name] = max(0, min(1, self.relationships[target_npc.name]))
        
        # Record conversation
        self.conversation_engine.record_conversation(context, response)
        
        # Store in local history
        if target_npc.name not in self.conversation_history:
            self.conversation_history[target_npc.name] = []
        
        self.conversation_history[target_npc.name].append({
            "timestamp": datetime.datetime.now().isoformat(),
            "topic": response.topic_shift.value if response.topic_shift else context.topic.value,
            "dialogue": response.dialogue,
            "relationship_change": response.relationship_change
        })
        
        # Trigger empathetic response in target if possible
        if hasattr(target_npc, '_receive_conversation'):
            target_npc._receive_conversation(self, response)
    
    def _receive_conversation(self, initiator_npc, conversation_response):
        """Receive and respond to conversation from another NPC"""
        # Generate empathetic response
        empathetic_dialogue = self.emotional_intelligence.generate_empathetic_dialogue(
            self.emotional_state,
            initiator_npc.emotional_state.primary_emotion,
            self.relationships.get(initiator_npc.name, 0.5)
        )
        
        if empathetic_dialogue:
            # Delayed response to seem more natural
            pygame.time.set_timer(pygame.USEREVENT + 1, 2000)  # Respond after 2 seconds
            self.pending_response = empathetic_dialogue
    
    def _offer_help(self, target_npc):
        """Offer help to another NPC"""
        help_messages = [
            f"Is there anything I can help you with, {target_npc.name}?",
            f"You look like you could use some assistance, {target_npc.name}.",
            f"I'm here if you need any help, {target_npc.name}!",
            f"Let me know if there's anything I can do for you, {target_npc.name}."
        ]
        
        self.say(random.choice(help_messages))
        
        # Boost relationship
        if target_npc.name not in self.relationships:
            self.relationships[target_npc.name] = 0.5
        
        self.relationships[target_npc.name] += 0.1
        self.relationships[target_npc.name] = min(1.0, self.relationships[target_npc.name])
    
    def _practice_skill(self):
        """Practice a skill or engage in learning behavior"""
        self.say("I'm working on improving myself today.")
        self.needs["fun"] = min(1.0, self.needs["fun"] + 0.1)
    
    def _rest(self):
        """Rest to restore energy and needs - try to go home if possible"""
        if self.house_manager and not self.house_manager.is_npc_at_home(self.name):
            # Try to go home for better rest
            if self.house_manager.npc_go_home(self):
                self.say("I think I'll head home to rest properly.")
                return
        
        # If at home, use house facilities
        if self.house_manager and self.house_manager.is_npc_at_home(self.name):
            # Choose a rest activity based on needs
            if self.needs["sleep"] < 0.4:
                result = self.house_manager.npc_restore_stats_at_home(self, "sleep")
                if result:
                    self.say(result.split("!")[0] + "!")  # Take first sentence
                    return
            elif self.needs["fun"] < 0.4:
                result = self.house_manager.npc_restore_stats_at_home(self, "relax")
                if result:
                    self.say(result.split("!")[0] + "!")
                    return
        
        # Default rest behavior
        self.say("I think I'll take a moment to rest.")
        self.needs["sleep"] = min(1.0, self.needs["sleep"] + 0.2)
        self.energy_level = min(1.0, self.energy_level + 0.3)
    
    def _learn_from_behavior(self, behavior_response, outcome):
        """Learn from behavior outcomes to improve future decisions"""
        success = outcome in ["executed", "successful", "positive"]
        
        self.ai_behavior.learn_from_outcome(
            self.name, behavior_response, outcome, success
        )
        
        # Update local success rates
        action = behavior_response.primary_action
        if action not in self.behavior_success_rates:
            self.behavior_success_rates[action] = {"successes": 0, "attempts": 0}
        
        self.behavior_success_rates[action]["attempts"] += 1
        if success:
            self.behavior_success_rates[action]["successes"] += 1
    
    def _get_time_of_day(self) -> str:
        """Get current time of day (could be enhanced with actual time system)"""
        import time
        hour = datetime.datetime.now().hour
        
        if 6 <= hour < 12:
            return "morning"
        elif 12 <= hour < 17:
            return "afternoon"
        elif 17 <= hour < 20:
            return "evening"
        else:
            return "night"
    
    def _find_npc_by_name(self, name: str, npcs: List) -> Optional['EnhancedNPC']:
        """Find NPC by name in the list"""
        for npc in npcs:
            if npc.name == name:
                return npc
        return None
    
    def _set_exploration_target(self):
        """Set a target for exploration"""
        # Random exploration target
        x = random.randint(50, MAP_WIDTH - 50)
        y = random.randint(50, MAP_HEIGHT - 50)
        self.target_pos = pygame.math.Vector2(x, y)
        self.state = "moving"
    
    def _check_home_needs(self, dt):
        """Check if NPC should go home to restore stats"""
        if not self.house_manager:
            return
        
        # Check if any critical needs are low
        critical_needs = False
        for need, value in self.needs.items():
            if value < 0.3:  # Critical threshold
                critical_needs = True
                break
        
        # If energy is low, also consider going home
        if self.energy_level < 0.3:
            critical_needs = True
        
        # If needs are critical and not already going home or at home
        if critical_needs and self.state not in ["going_home", "inside_house"]:
            if not self.house_manager.is_npc_at_home(self.name):
                # 30% chance to go home when needs are critical
                if random.random() < 0.3:
                    if self.house_manager.npc_go_home(self):
                        self.say("I should head home to take care of myself.")
        
        # If near home, try to enter
        elif self.state == "going_home" and self.house_manager.is_near_house(self):
            if self.house_manager.npc_enter_house(self):
                self.say("Home sweet home!")
                # Restore stats immediately when entering
                self._restore_stats_at_home()
        
        # If inside house and fully restored, exit
        elif self.state == "inside_house":
            all_needs_good = all(value > 0.7 for value in self.needs.values())
            energy_good = self.energy_level > 0.7
            
            if all_needs_good and energy_good:
                if self.house_manager.npc_exit_house(self):
                    self.say("Feeling much better! Time to get back out there.")
    
    def _restore_stats_at_home(self):
        """Restore stats when at home"""
        if not self.house_manager or not self.house_manager.is_npc_at_home(self.name):
            return
        
        # Choose restoration activity based on lowest need
        lowest_need = min(self.needs.items(), key=lambda x: x[1])
        need_name, need_value = lowest_need
        
        if need_value < 0.4:
            if need_name == "hunger":
                result = self.house_manager.npc_restore_stats_at_home(self, "cook")
            elif need_name == "sleep":
                result = self.house_manager.npc_restore_stats_at_home(self, "sleep")
            elif need_name == "fun":
                result = self.house_manager.npc_restore_stats_at_home(self, "relax")
            elif need_name == "social":
                result = self.house_manager.npc_restore_stats_at_home(self, "read")
            else:
                result = self.house_manager.npc_restore_stats_at_home(self, "freshen_up")
            
            if result and "doesn't have" not in result:
                # Don't say the full message, just indicate they're using the house
                pass
    
    def _wander(self):
        """Default wandering behavior"""
        if not self.target_pos or self._reached_target():
            self.wander_timer -= 1
            if self.wander_timer <= 0:
                angle = random.uniform(0, 2 * math.pi)
                distance = random.uniform(50, 150)
                new_x = max(50, min(MAP_WIDTH - 50, self.rect.centerx + distance * math.cos(angle)))
                new_y = max(50, min(MAP_HEIGHT - 50, self.rect.centery + distance * math.sin(angle)))
                self.target_pos = pygame.math.Vector2(new_x, new_y)
                self.state = "moving"
                self.wander_timer = random.randint(60, 180)
    
    # Include all the basic methods from the original NPC class
    def _move(self, dt):
        """Move towards target position"""
        if self.target_pos:
            direction = self.target_pos - pygame.math.Vector2(self.rect.center)
            if direction.length() > 5:
                direction.normalize_ip()
                self.velocity = direction * self.speed
                self.is_moving = True
            else:
                self.target_pos = None
                self.velocity = pygame.math.Vector2(0, 0)
                self.is_moving = False
                self.state = "idle"
        else:
            self.velocity = pygame.math.Vector2(0, 0)
            self.is_moving = False
        
        # Update position
        self.rect.x += self.velocity.x * dt
        self.rect.y += self.velocity.y * dt
        
        # Keep within bounds
        self.rect.x = max(0, min(self.rect.x, MAP_WIDTH - self.rect.width))
        self.rect.y = max(0, min(self.rect.y, MAP_HEIGHT - self.rect.height))
    
    def _update_animation(self, dt):
        """Update sprite animation based on movement state"""
        self.animation_timer += dt
        
        if self.is_moving:
            if self.walk_sprite and self.animation_timer > 0.3:
                if self.image == self.idle_sprite:
                    self.image = self.walk_sprite.copy()
                else:
                    self.image = self.idle_sprite.copy()
                self.animation_timer = 0.0
        else:
            if self.idle_sprite:
                self.image = self.idle_sprite.copy()
    
    def _reached_target(self):
        if not self.target_pos:
            return True
        distance = (self.target_pos - pygame.math.Vector2(self.rect.center)).length()
        return distance < 5
    
    def _get_distance(self, other):
        return math.sqrt((self.rect.centerx - other.rect.centerx)**2 + 
                        (self.rect.centery - other.rect.centery)**2)
    
    def walk_to_player(self, player, quest_id=None, message=None):
        """Make NPC walk to the player to initiate interaction"""
        self.state = "approaching_player"
        self.target_entity = player
        self.target_pos = pygame.math.Vector2(player.rect.center)
        self.quest_to_give = quest_id
        self.approach_message = message or f"Hello {player.name}! I have something important to discuss."
    
    def approach_and_give_quest(self, player, quest_system, quest_id):
        """Approach player and give them a quest"""
        self.walk_to_player(player, quest_id, f"Hey {player.name}! I've got a job for you.")
        
    def update_player_tracking(self, player):
        """Update tracking when following the player"""
        if self.state == "approaching_player" and self.target_entity == player:
            # Update target position to follow player
            self.target_pos = pygame.math.Vector2(player.rect.center)
            
            # Check if close enough to interact
            distance = self._get_distance(player)
            if distance < 50:  # Close enough to talk
                self.state = "idle"
                self.target_entity = None
                self.target_pos = None
                
                # Say the approach message
                if self.approach_message:
                    self.say(self.approach_message)
                    self.approach_message = None
                
                # Trigger quest giving if applicable
                if self.quest_to_give:
                    return self.quest_to_give  # Return quest ID to be handled by game
        
        return None
    
    def say(self, text):
        """Make NPC say something with emotional coloring"""
        # Add emotional indicators to dialogue based on current state
        emotion_indicators = {
            EmotionType.JOY: "😊",
            EmotionType.SADNESS: "😔",
            EmotionType.ANGER: "😠",
            EmotionType.FEAR: "😰",
            EmotionType.SURPRISE: "😲",
            EmotionType.LOVE: "❤️",
            EmotionType.TRUST: "😌",
            EmotionType.PRIDE: "😤"
        }
        
        indicator = emotion_indicators.get(self.emotional_state.primary_emotion, "")
        if self.emotional_state.intensity > 0.6 and indicator:
            text = f"{text} {indicator}"
        
        self.current_dialogue = text
        self.dialogue_timer = max(8.0, len(text) * 0.1)  # Longer for longer messages
    
    def rate_player_interaction(self, player_name: str, interaction_type: str, message: str = "", gift_value: int = 0) -> Optional[InteractionRating]:
        """Rate a player interaction and provide feedback"""
        if not self.social_system:
            return None
        
        # Convert string to enum
        try:
            interaction_enum = InteractionType(interaction_type.lower())
        except ValueError:
            interaction_enum = InteractionType.CUSTOM
        
        # Get rating from social system
        rating = self.social_system.rate_interaction(
            npc=self,
            player_name=player_name,
            interaction_type=interaction_enum,
            message=message,
            gift_value=gift_value
        )
        
        # Store the rating
        self.last_interaction_rating = rating
        self.interaction_history.append({
            'player': player_name,
            'type': interaction_type,
            'message': message,
            'rating': rating,
            'timestamp': datetime.datetime.now()
        })
        
        # Keep only recent interactions (last 10)
        if len(self.interaction_history) > 10:
            self.interaction_history.pop(0)
        
        # Adjust relationship based on rating
        if player_name not in self.relationships:
            self.relationships[player_name] = 0.5
        
        # Convert rating score to relationship change
        if rating.final_score >= 8.0:
            relationship_change = 0.15  # Great interaction
        elif rating.final_score >= 7.0:
            relationship_change = 0.10  # Good interaction
        elif rating.final_score >= 6.0:
            relationship_change = 0.05  # Decent interaction
        elif rating.final_score >= 4.0:
            relationship_change = 0.0   # Neutral interaction
        elif rating.final_score >= 2.0:
            relationship_change = -0.05 # Poor interaction
        else:
            relationship_change = -0.10 # Very poor interaction
        
        # Apply social skill bonus
        if self.social_system.player:
            bonus = self.social_system.get_interaction_bonus(interaction_type)
            relationship_change *= bonus
        
        self.relationships[player_name] = max(0.0, min(1.0, 
            self.relationships[player_name] + relationship_change))
        
        # Update emotional state based on interaction
        self._update_emotional_state_from_interaction(rating)
        
        # Learn from the interaction
        self._learn_from_interaction(player_name, interaction_type, rating)
        
        return rating
    
    def _update_emotional_state_from_interaction(self, rating: InteractionRating):
        """Update NPC emotional state based on interaction rating"""
        if not hasattr(self, 'emotional_state'):
            return
        
        # Adjust emotional intensity based on interaction quality
        if rating.final_score >= 8.0:
            # Great interaction - boost positive emotions
            if hasattr(self.emotional_state, 'primary_emotion'):
                if self.emotional_state.primary_emotion in [EmotionType.JOY, EmotionType.TRUST]:
                    self.emotional_state.intensity = min(1.0, self.emotional_state.intensity + 0.2)
                else:
                    self.emotional_state.primary_emotion = EmotionType.JOY
                    self.emotional_state.intensity = 0.6
        elif rating.final_score <= 3.0:
            # Poor interaction - negative emotions
            if hasattr(self.emotional_state, 'primary_emotion'):
                self.emotional_state.primary_emotion = EmotionType.ANGER
                self.emotional_state.intensity = min(1.0, self.emotional_state.intensity + 0.3)
    
    def _learn_from_interaction(self, player_name: str, interaction_type: str, rating: InteractionRating):
        """Learn player preferences and interaction patterns"""
        # Track what types of interactions this player tends to use
        if player_name not in self.learned_preferences:
            self.learned_preferences[player_name] = {
                'preferred_interactions': {},
                'conversation_style': 'neutral',
                'gift_preferences': {},
                'topics_of_interest': []
            }
        
        # Update interaction preferences
        prefs = self.learned_preferences[player_name]['preferred_interactions']
        if interaction_type not in prefs:
            prefs[interaction_type] = []
        
        prefs[interaction_type].append(rating.final_score)
        
        # Keep only recent scores (last 5 interactions of this type)
        if len(prefs[interaction_type]) > 5:
            prefs[interaction_type].pop(0)
        
        # Determine conversation style based on sentiment patterns
        if rating.sentiment_modifier > 0.5:
            self.learned_preferences[player_name]['conversation_style'] = 'positive'
        elif rating.sentiment_modifier < -0.5:
            self.learned_preferences[player_name]['conversation_style'] = 'negative'
    
    def get_interaction_feedback(self) -> Optional[str]:
        """Get feedback message for the last interaction"""
        if self.last_interaction_rating:
            return self.last_interaction_rating.feedback_message
        return None
    
    def get_relationship_status(self, player_name: str) -> Dict[str, Any]:
        """Get detailed relationship information with a player"""
        relationship_level = self.relationships.get(player_name, 0.5)
        
        # Determine relationship category
        if relationship_level >= 0.9:
            status = "Best Friend"
        elif relationship_level >= 0.8:
            status = "Close Friend"
        elif relationship_level >= 0.6:
            status = "Good Friend"
        elif relationship_level >= 0.5:
            status = "Friend"
        elif relationship_level >= 0.3:
            status = "Acquaintance"
        elif relationship_level >= 0.1:
            status = "Stranger"
        else:
            status = "Dislikes You"
        
        # Get interaction statistics
        player_interactions = [h for h in self.interaction_history if h['player'] == player_name]
        avg_rating = 0.0
        if player_interactions:
            avg_rating = sum(h['rating'].final_score for h in player_interactions) / len(player_interactions)
        
        return {
            'level': relationship_level,
            'status': status,
            'total_interactions': len(player_interactions),
            'average_rating': avg_rating,
            'learned_preferences': self.learned_preferences.get(player_name, {})
        }
    
    def set_social_system(self, social_system: SocialSystem):
        """Set the social system reference"""
        self.social_system = social_system
    
    def draw(self, screen, camera):
        """Enhanced drawing with emotional visual cues"""
        screen.blit(self.image, camera.apply(self))
        
        # Draw enhanced name with emotional coloring
        font = pygame.font.Font(None, 20)
        
        # Color name based on emotional state
        name_colors = {
            EmotionType.JOY: (255, 255, 100),
            EmotionType.SADNESS: (150, 150, 255),
            EmotionType.ANGER: (255, 150, 150),
            EmotionType.FEAR: (200, 150, 255),
            EmotionType.LOVE: (255, 200, 200),
            EmotionType.TRUST: (150, 255, 150)
        }
        
        name_color = name_colors.get(self.emotional_state.primary_emotion, (255, 255, 100))
        name_text = font.render(self.name, True, name_color)
        
        # Add shadow
        shadow_text = font.render(self.name, True, (0, 0, 0))
        
        text_rect = name_text.get_rect()
        text_rect.centerx = camera.apply(self).centerx
        text_rect.bottom = camera.apply(self).top - 8
        
        # Draw shadow first
        shadow_rect = text_rect.copy()
        shadow_rect.x += 1
        shadow_rect.y += 1
        screen.blit(shadow_text, shadow_rect)
        
        # Draw name
        screen.blit(name_text, text_rect)
        
        # Draw emotional intensity indicator
        if self.emotional_state.intensity > 0.5:
            intensity_width = int(20 * self.emotional_state.intensity)
            intensity_rect = pygame.Rect(
                camera.apply(self).centerx - 10,
                camera.apply(self).bottom + 2,
                intensity_width, 3
            )
            pygame.draw.rect(screen, name_color, intensity_rect)
        
        # Draw speech bubble if talking
        if self.current_dialogue:
            self._draw_speech_bubble(screen, camera, self.current_dialogue)
    
    def _draw_speech_bubble(self, screen, camera, text):
        """Enhanced speech bubble with emotional styling"""
        font = pygame.font.Font(None, 16)
        words = text.split(' ')
        lines = []
        current_line = ""
        
        # Word wrap
        for word in words:
            test_line = current_line + (" " if current_line else "") + word
            if font.size(test_line)[0] > 220:
                if current_line:
                    lines.append(current_line)
                    current_line = word
                else:
                    lines.append(word)
            else:
                current_line = test_line
        
        if current_line:
            lines.append(current_line)
        
        # Calculate bubble size
        max_width = max(font.size(line)[0] for line in lines) + 25
        bubble_height = len(lines) * 20 + 20
        
        # Position bubble above NPC
        npc_rect = camera.apply(self)
        bubble_x = npc_rect.centerx - max_width // 2
        bubble_y = npc_rect.top - bubble_height - 15
        
        # Keep bubble on screen
        bubble_x = max(5, min(bubble_x, screen.get_width() - max_width - 5))
        bubble_y = max(5, bubble_y)
        
        # Emotional bubble styling
        bubble_colors = {
            EmotionType.JOY: (255, 255, 200, 240),
            EmotionType.SADNESS: (200, 200, 255, 240),
            EmotionType.ANGER: (255, 200, 200, 240),
            EmotionType.FEAR: (220, 200, 255, 240),
            EmotionType.LOVE: (255, 220, 220, 240)
        }
        
        bubble_color = bubble_colors.get(self.emotional_state.primary_emotion, (255, 255, 255, 240))
        
        # Draw bubble background
        bubble_rect = pygame.Rect(bubble_x, bubble_y, max_width, bubble_height)
        
        # Draw bubble with emotional coloring
        bubble_surface = pygame.Surface((max_width, bubble_height), pygame.SRCALPHA)
        bubble_surface.fill(bubble_color)
        screen.blit(bubble_surface, (bubble_x, bubble_y))
        
        pygame.draw.rect(screen, (150, 150, 150), bubble_rect, 2, border_radius=10)
        
        # Draw pointer
        pointer_points = [
            (bubble_x + max_width // 2 - 8, bubble_y + bubble_height),
            (bubble_x + max_width // 2, bubble_y + bubble_height + 8),
            (bubble_x + max_width // 2 + 8, bubble_y + bubble_height)
        ]
        pygame.draw.polygon(screen, bubble_color[:3], pointer_points)
        pygame.draw.polygon(screen, (150, 150, 150), pointer_points, 2)
        
        # Draw text
        y_offset = bubble_y + 10
        for line in lines:
            text_surface = font.render(line, True, (50, 50, 50))
            text_rect = text_surface.get_rect()
            text_rect.centerx = bubble_x + max_width // 2
            text_rect.y = y_offset
            screen.blit(text_surface, text_rect)
            y_offset += 20
    
    def get_status_info(self) -> Dict:
        """Get comprehensive status information for UI display"""
        return {
            "name": self.name,
            "emotion": self.emotional_state.primary_emotion.value,
            "emotion_intensity": self.emotional_state.intensity,
            "needs": self.needs.copy(),
            "relationships": {name: round(value, 2) for name, value in self.relationships.items()},
            "current_goal": self.current_goals[0] if self.current_goals else "None",
            "energy_level": self.energy_level,
            "social_battery": self.social_battery,
            "conversation_topics": len(self.conversation_history),
            "learning_experiences": len(self.behavior_success_rates)
        }
    
    # Include remaining methods from original NPC class for compatibility
    def _load_memories(self):
        """Load memories from memory manager"""
        if self.memory_manager:
            memories = self.memory_manager.get_recent_memories(self.name, 20)
            for memory in memories:
                self.memory.append({
                    "content": memory["content"],
                    "timestamp": memory["timestamp"],
                    "importance": memory.get("importance", 0.5)
                })
    
    def _get_npc_data(self) -> Dict:
        """Get basic NPC data (maintaining compatibility)"""
        recent_memories = self.memory[-10:] if self.memory else []
        
        if self.memory_manager:
            db_memories = self.memory_manager.get_recent_memories(self.name, 5)
            for db_mem in db_memories:
                recent_memories.append({
                    "type": db_mem["memory_type"],
                    "content": db_mem["content"],
                    "timestamp": db_mem["timestamp"]
                })
        
        return {
            "name": self.name,
            "personality": self.personality.traits,
            "needs": self.needs,
            "relationships": self.relationships,
            "memories": recent_memories,
            "emotion": self.emotion if hasattr(self, 'emotion') else 'neutral',
            "state": self.state
        }
    
    def start_wait(self, duration=5.0, reason=None):
        """Start waiting for a specified duration"""
        self.is_waiting = True
        self.wait_duration = duration
        self.wait_timer = duration
        self.wait_reason = reason or "Taking a moment to rest"
        
        # Show wait dialogue
        self.say(self.wait_reason)
        
        # Stop movement
        self.velocity.x = 0
        self.velocity.y = 0
        self.target_pos = None
        self.target_entity = None
        self.state = "waiting"
    
    def stop_wait(self):
        """Stop waiting and resume normal behavior"""
        self.is_waiting = False
        self.wait_timer = 0.0
        self.wait_duration = 0.0
        self.wait_reason = None
        self.state = "idle"
        
        # Clear wait dialogue if still showing
        if self.current_dialogue == self.wait_reason:
            self.current_dialogue = None
            self.dialogue_timer = 0
    
    def get_wait_progress(self):
        """Get waiting progress as a percentage (0-1)"""
        if not self.is_waiting or self.wait_duration <= 0:
            return 1.0
        return 1.0 - (self.wait_timer / self.wait_duration)