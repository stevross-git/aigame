import pygame
import random
import math
import datetime
from typing import Dict, List, Optional
from src.core.constants import *
from src.entities.personality import Personality
from src.ai.ollama_client import AIResponse
from src.ai.ai_client_manager import AIClientManager
from src.ai.memory_manager import MemoryManager, Memory
from src.graphics.custom_asset_manager import CustomAssetManager

class NPC(pygame.sprite.Sprite):
    def __init__(self, x, y, name, personality_traits=None, memory_manager=None):
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
        
        self.needs = {
            "hunger": 1.0,
            "sleep": 1.0,
            "social": 1.0,
            "fun": 1.0
        }
        
        self.relationships = {}
        self.memory = []
        self.emotion = "neutral"
        
        self.state = "idle"
        self.target_pos = None
        self.wander_timer = 0
        self.interaction_cooldown = 0
        self.ai_decision_cooldown = 0
        
        self.ai_client = None
        self.current_dialogue = None
        self.dialogue_timer = 0
        
        self.memory_manager = memory_manager
        self.ai_response_box = None  # Will be set by Game class
        
        # Player interaction state
        self.player_interaction_context = None
        self.chat_interface = None  # Will be set by game class
        
        # Async AI state
        self.pending_ai_request = False
        self.last_ai_request_time = 0
        
        try:
            ai_manager = AIClientManager()
            self.ai_client = ai_manager.create_ai_client()
            if self.memory_manager:
                self._load_memories()
        except Exception as e:
            print(f"Failed to initialize AI for {name}: {e}")
            self.ai_client = None
    
    def update(self, dt, other_npcs, active_events=None, ai_paused=False):
        # Always update basic needs (they continue during interactions)
        if not ai_paused:
            self._update_needs(dt)
            self._update_ai_behavior(dt, other_npcs, active_events)
        
        # Always update movement and animation (but they may be stationary)
        self._move(dt)
        self._update_animation(dt)
        
        if self.interaction_cooldown > 0:
            self.interaction_cooldown -= dt
        
        if self.dialogue_timer > 0:
            self.dialogue_timer -= dt
            if self.dialogue_timer <= 0:
                self.current_dialogue = None
    
    def _update_needs(self, dt):
        # Store old needs to detect significant changes
        old_needs = self.needs.copy()
        
        self.needs["hunger"] -= dt * 0.01  # Slower hunger decay
        self.needs["sleep"] -= dt * 0.008  # Slower sleep decay
        self.needs["social"] -= dt * 0.012 # Slower social decay
        self.needs["fun"] -= dt * 0.006    # Slower fun decay
        
        for need in self.needs:
            self.needs[need] = max(0, min(1, self.needs[need]))
        
        # Check for significant need changes and invalidate cache if necessary
        if self.ai_client and hasattr(self.ai_client, 'invalidate_npc_cache'):
            significant_changes = {}
            for need, new_value in self.needs.items():
                old_value = old_needs.get(need, new_value)
                if abs(new_value - old_value) > 0.15:  # 15% change threshold
                    significant_changes[f'need_{need}'] = new_value
            
            if significant_changes:
                self.ai_client.invalidate_npc_cache(self.name, significant_changes)
    
    def _update_ai_behavior(self, dt, other_npcs, active_events=None):
        self.ai_decision_cooldown -= dt
        
        if active_events:
            self._react_to_events(active_events)
        
        if self.ai_decision_cooldown <= 0 and self.ai_client and not self.pending_ai_request:
            context = self._build_context(other_npcs, active_events)
            npc_data = self._get_npc_data()
            
            try:
                # Use async AI requests to prevent lag, but fall back to sync for critical interactions
                if (self.player_interaction_context and 
                    self.player_interaction_context.get("type") == "direct_chat"):
                    # For direct chat, use async to prevent UI lag
                    self.pending_ai_request = True
                    self.ai_client.make_decision_async(npc_data, context, self._handle_async_ai_response)
                elif hasattr(self.ai_client, 'make_decision_async'):
                    # For regular behavior, also use async but with lower priority
                    self.pending_ai_request = True
                    self.ai_client.make_decision_async(npc_data, context, self._handle_async_ai_response)
                else:
                    # Fallback to synchronous if async not available
                    ai_response = self.ai_client.make_decision(npc_data, context)
                    self._process_ai_response(ai_response, other_npcs, active_events)
                
                self.ai_decision_cooldown = random.uniform(10, 20)
            except Exception as e:
                print(f"AI decision error for {self.name}: {e}")
                self._fallback_behavior(dt, other_npcs)
        else:
            self._fallback_behavior(dt, other_npcs)
    
    def _handle_async_ai_response(self, ai_response):
        """Handle async AI response"""
        self.pending_ai_request = False
        self._process_ai_response(ai_response, [], [])
    
    def _process_ai_response(self, ai_response, other_npcs, active_events):
        """Process AI response (both sync and async)"""
        self._execute_ai_decision(ai_response, other_npcs, active_events)
        
        # Send response to AI response box
        if self.ai_response_box:
            self.ai_response_box.add_response(
                self.name, 
                ai_response.action, 
                ai_response.reasoning or "No reasoning provided",
                ai_response.dialogue
            )
        
        # Handle chat interface responses
        if (self.player_interaction_context and 
            self.player_interaction_context.get("type") == "direct_chat" and
            ai_response.dialogue and self.chat_interface):
            self.chat_interface.handle_npc_response(self, ai_response.dialogue)
        
        # Check for emotion changes and invalidate cache if needed
        if ai_response.emotion and ai_response.emotion != self.emotion:
            old_emotion = self.emotion
            self.emotion = ai_response.emotion
            
            if self.ai_client and hasattr(self.ai_client, 'invalidate_npc_cache'):
                self.ai_client.invalidate_npc_cache(self.name, {'emotion': self.emotion})
    
    def _react_to_events(self, active_events):
        for event in active_events:
            for impact, value in event.impact.items():
                if impact in self.needs:
                    self.needs[impact] = max(0, min(1, self.needs[impact] + value * 0.01))
                elif impact in self.personality.traits:
                    pass
    
    def _fallback_behavior(self, dt, other_npcs):
        if self.state == "idle":
            self.wander_timer -= dt
            if self.wander_timer <= 0:
                self._set_random_target()
                self.state = "wandering"
                self.wander_timer = random.uniform(15, 30)
        
        elif self.state == "wandering":
            if self.target_pos and self._reached_target():
                self.state = "idle"
                self.target_pos = None
    
    def _set_random_target(self):
        angle = random.uniform(0, 2 * math.pi)
        distance = random.uniform(50, 200)
        target_x = self.rect.centerx + math.cos(angle) * distance
        target_y = self.rect.centery + math.sin(angle) * distance
        
        target_x = max(16, min(target_x, MAP_WIDTH - 16))
        target_y = max(16, min(target_y, MAP_HEIGHT - 16))
        
        self.target_pos = pygame.math.Vector2(target_x, target_y)
    
    def _move(self, dt):
        if self.target_pos:
            direction = self.target_pos - pygame.math.Vector2(self.rect.center)
            if direction.length() > 0:
                direction.normalize_ip()
                self.velocity = direction * self.speed
                
                # Track movement for animation
                old_pos = (self.rect.x, self.rect.y)
                
                self.rect.x += self.velocity.x * dt
                self.rect.y += self.velocity.y * dt
                
                self.rect.x = max(0, min(self.rect.x, MAP_WIDTH - self.rect.width))
                self.rect.y = max(0, min(self.rect.y, MAP_HEIGHT - self.rect.height))
                
                # Check if actually moved
                self.is_moving = (old_pos != (self.rect.x, self.rect.y))
            else:
                self.is_moving = False
        else:
            self.is_moving = False
    
    def _update_animation(self, dt):
        """Update sprite animation based on movement state"""
        self.animation_timer += dt
        
        if self.is_moving:
            # Use walking sprite if available
            if self.walk_sprite and self.animation_timer > 0.3:  # Change sprite every 0.3 seconds
                if self.image == self.idle_sprite:
                    self.image = self.walk_sprite.copy()
                else:
                    self.image = self.idle_sprite.copy()
                self.animation_timer = 0.0
        else:
            # Use idle sprite when not moving
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
    
    def _interact_with(self, other):
        self.needs["social"] = min(1.0, self.needs["social"] + 0.2)
        self.interaction_cooldown = 3.0
        
        if other.name not in self.relationships:
            self.relationships[other.name] = 0.5
        
        change = random.uniform(-0.1, 0.2) * self.personality.get_trait("friendliness")
        self.relationships[other.name] = max(0, min(1, self.relationships[other.name] + change))
        
        interaction_memory = {
            "type": "interaction",
            "with": other.name,
            "relationship": self.relationships[other.name]
        }
        self.memory.append(interaction_memory)
        
        if self.memory_manager:
            memory = Memory(
                npc_name=self.name,
                memory_type="interaction",
                content=f"Had a conversation with {other.name}",
                timestamp=datetime.datetime.now().isoformat(),
                participants=[self.name, other.name],
                emotion=self.emotion,
                location=(self.rect.centerx, self.rect.centery),
                importance=0.5 + abs(change)
            )
            self.memory_manager.store_memory(memory)
            self.memory_manager.update_relationship(self.name, other.name, change)
    
    def _build_context(self, other_npcs, active_events=None) -> Dict:
        nearby_npcs = []
        for npc in other_npcs:
            if npc != self and self._get_distance(npc) < 100:
                nearby_npcs.append(npc.name)
        
        context = {
            "situation": self.state,
            "nearby_npcs": nearby_npcs,
            "emotion": self.emotion,
            "location": f"({self.rect.x}, {self.rect.y})"
        }
        
        # Add player interaction context if present
        if self.player_interaction_context:
            context["player_interaction"] = self.player_interaction_context
            # Clear the interaction context after using it
            self.player_interaction_context = None
        
        if active_events:
            event_descriptions = []
            for event in active_events:
                if event.location:
                    dist = ((event.location[0] - self.rect.centerx) ** 2 + 
                           (event.location[1] - self.rect.centery) ** 2) ** 0.5
                    if dist < 200:
                        event_descriptions.append(f"{event.title} nearby at {event.location}")
                else:
                    event_descriptions.append(f"{event.title}: {event.description}")
            
            if event_descriptions:
                context["active_events"] = event_descriptions
        
        return context
    
    def _get_npc_data(self) -> Dict:
        recent_memories = self.memory[-10:] if self.memory else []
        
        if self.memory_manager:
            db_memories = self.memory_manager.get_recent_memories(self.name, 5)
            for db_mem in db_memories:
                recent_memories.append({
                    "type": db_mem["memory_type"],
                    "detail": db_mem["content"],
                    "emotion": db_mem["emotion"]
                })
        
        return {
            "name": self.name,
            "personality_description": self.personality.to_prompt_string(),
            "needs": self.needs.copy(),
            "recent_memories": recent_memories,
            "relationships": self.relationships
        }
    
    def _execute_ai_decision(self, ai_response: AIResponse, other_npcs, active_events=None):
        self.emotion = ai_response.emotion or "neutral"
        
        if ai_response.action == "talk_to" and ai_response.target:
            target_npc = self._find_npc_by_name(ai_response.target, other_npcs)
            if target_npc:
                self._interact_with(target_npc)
                if ai_response.dialogue:
                    self.current_dialogue = ai_response.dialogue
                    self.dialogue_timer = 8.0
        
        elif ai_response.action == "move_to":
            if ai_response.target and "," in ai_response.target:
                try:
                    coords = ai_response.target.strip("()").split(",")
                    x, y = int(coords[0]), int(coords[1])
                    self.target_pos = pygame.math.Vector2(x, y)
                except:
                    self._set_random_target()
            else:
                self._set_random_target()
            self.state = "wandering"
        
        elif ai_response.action == "attend_event" and active_events:
            for event in active_events:
                if event.location and ai_response.target in event.title:
                    self.target_pos = pygame.math.Vector2(event.location[0], event.location[1])
                    self.state = "attending_event"
                    from src.world.events import EventGenerator
                    event.participants.append(self.name)
                    
                    if self.memory_manager:
                        memory = Memory(
                            npc_name=self.name,
                            memory_type="event",
                            content=f"Attended {event.title}: {event.description}",
                            timestamp=datetime.datetime.now().isoformat(),
                            participants=[self.name],
                            emotion=self.emotion,
                            location=event.location,
                            importance=0.7
                        )
                        self.memory_manager.store_memory(memory)
                    break
        
        elif ai_response.action in ["rest", "sleep"]:
            self.state = "resting"
            self.needs["sleep"] = min(1.0, self.needs["sleep"] + 0.3)
        
        elif ai_response.action == "eat":
            self.needs["hunger"] = min(1.0, self.needs["hunger"] + 0.4)
        
        elif ai_response.action == "play":
            self.needs["fun"] = min(1.0, self.needs["fun"] + 0.3)
    
    def _find_npc_by_name(self, name: str, npcs: List) -> Optional['NPC']:
        for npc in npcs:
            if npc.name == name:
                return npc
        return None
    
    def draw(self, screen, camera):
        screen.blit(self.image, camera.apply(self))
        
        # Draw name with better styling
        font = pygame.font.Font(None, 20)
        name_text = font.render(self.name, True, WHITE)
        
        # Add shadow for better visibility
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
        
        if self.current_dialogue:
            self._draw_dialogue_bubble(screen, camera)
    
    def _draw_dialogue_bubble(self, screen, camera):
        # Try to use the custom speech bubble sprite
        speech_bubble_sprite = self.assets.get_sprite("speech_bubble")
        
        if speech_bubble_sprite:
            # Use the custom speech bubble
            bubble_rect = speech_bubble_sprite.get_rect()
            bubble_rect.centerx = camera.apply(self).centerx
            bubble_rect.bottom = camera.apply(self).top - 10
            screen.blit(speech_bubble_sprite, bubble_rect)
            
            # Draw text on the bubble
            font = pygame.font.Font(None, 16)
            words = self.current_dialogue.split(' ')
            lines = []
            current_line = []
            max_width = bubble_rect.width - 20
            
            for word in words:
                test_line = ' '.join(current_line + [word])
                if font.size(test_line)[0] <= max_width:
                    current_line.append(word)
                else:
                    if current_line:
                        lines.append(' '.join(current_line))
                        current_line = [word]
                    else:
                        lines.append(word)
            
            if current_line:
                lines.append(' '.join(current_line))
            
            # Center text in bubble
            text_start_y = bubble_rect.y + 10
            line_height = 16
            
            for i, line in enumerate(lines[:3]):  # Max 3 lines to fit in bubble
                text_surface = font.render(line, True, BLACK)
                text_rect = text_surface.get_rect()
                text_rect.centerx = bubble_rect.centerx
                text_rect.y = text_start_y + i * line_height
                screen.blit(text_surface, text_rect)
        
        else:
            # Fallback to original bubble drawing
            font = pygame.font.Font(None, 16)
            padding = 8
            max_width = 180
            
            words = self.current_dialogue.split(' ')
            lines = []
            current_line = []
            
            for word in words:
                test_line = ' '.join(current_line + [word])
                if font.size(test_line)[0] <= max_width - padding * 2:
                    current_line.append(word)
                else:
                    if current_line:
                        lines.append(' '.join(current_line))
                        current_line = [word]
                    else:
                        lines.append(word)
            
            if current_line:
                lines.append(' '.join(current_line))
            
            bubble_height = len(lines) * 20 + padding * 2
            bubble_width = max([font.size(line)[0] for line in lines]) + padding * 2
            
            bubble_x = camera.apply(self).centerx - bubble_width // 2
            bubble_y = camera.apply(self).top - bubble_height - 10
            
            pygame.draw.rect(screen, WHITE, 
                            (bubble_x, bubble_y, bubble_width, bubble_height), 
                            border_radius=5)
            pygame.draw.rect(screen, BLACK, 
                            (bubble_x, bubble_y, bubble_width, bubble_height), 
                            2, border_radius=5)
            
            y_offset = bubble_y + padding
            for line in lines:
                text_surface = font.render(line, True, BLACK)
                text_rect = text_surface.get_rect()
                text_rect.centerx = bubble_x + bubble_width // 2
                text_rect.y = y_offset
                screen.blit(text_surface, text_rect)
                y_offset += 20
    
    def _load_memories(self):
        if not self.memory_manager:
            return
        
        try:
            self.relationships = self.memory_manager.get_all_relationships(self.name)
            
            recent_memories = self.memory_manager.get_recent_memories(self.name, 20)
            for mem in recent_memories:
                self.memory.append({
                    "type": mem["memory_type"],
                    "detail": mem["content"],
                    "with": mem["participants"][1] if len(mem["participants"]) > 1 else None
                })
            
            print(f"Loaded {len(recent_memories)} memories for {self.name}")
        except Exception as e:
            print(f"Error loading memories for {self.name}: {e}")
    
    def say(self, text):
        """Make NPC say something"""
        self.current_dialogue = text
        self.dialogue_timer = 8.0  # Show for 8 seconds
    
    def _adjust_relationship(self, other, change):
        """Adjust relationship with another character"""
        if hasattr(other, 'name'):
            other_name = other.name
        else:
            other_name = str(other)
        
        if other_name not in self.relationships:
            self.relationships[other_name] = 0.3
        
        self.relationships[other_name] = max(0, min(1, self.relationships[other_name] + change))