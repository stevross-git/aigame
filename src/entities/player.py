import pygame
import src.core.constants as constants
from src.entities.personality import Personality
from src.graphics.custom_asset_manager import CustomAssetManager

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, character_data=None):
        super().__init__()
        
        # Initialize custom asset manager
        self.assets = CustomAssetManager()
        
        # Set character data
        if character_data:
            self.name = character_data["name"]
            self.color = character_data["color"]
            self.personality = Personality(**character_data["personality"])
        else:
            self.name = "Player"
            self.color = BLUE
            self.personality = Personality()
        
        # Get beautiful player sprite
        player_sprite = self.assets.get_character_sprite("player")
        if player_sprite:
            self.image = player_sprite.copy()
        else:
            # Fallback
            self.image = pygame.Surface((24, 32))
            self.image.fill(self.color)
        
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.speed = PLAYER_SPEED
        self.velocity = pygame.math.Vector2(0, 0)
        
        # Player stats
        self.needs = {
            "hunger": 1.0,
            "sleep": 1.0,
            "social": 1.0,
            "fun": 1.0
        }
        self.emotion = "neutral"
        
        # Relationships with NPCs
        self.relationships = {}
        
        # Interaction state
        self.current_dialogue = None
        self.dialogue_timer = 0
    
    def update(self, dt, keys):
        self.velocity.x = 0
        self.velocity.y = 0
        
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.velocity.x = -self.speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.velocity.x = self.speed
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.velocity.y = -self.speed
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.velocity.y = self.speed
        
        if self.velocity.length() > 0:
            self.velocity.normalize_ip()
            self.velocity *= self.speed
        
        self.rect.x += self.velocity.x * dt
        self.rect.y += self.velocity.y * dt
        
        self.rect.x = max(0, min(self.rect.x, constants.MAP_WIDTH - self.rect.width))
        self.rect.y = max(0, min(self.rect.y, constants.MAP_HEIGHT - self.rect.height))
        
        # Update dialogue timer
        if self.dialogue_timer > 0:
            self.dialogue_timer -= dt
            if self.dialogue_timer <= 0:
                self.current_dialogue = None
    
    def draw(self, screen, camera):
        screen.blit(self.image, camera.apply(self))
        
        # Draw player name with better styling
        font = pygame.font.Font(None, 20)
        name_text = font.render(self.name, True, (255, 255, 100))  # Slightly yellow for distinction
        
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
        
        # Draw speech bubble if talking
        if self.current_dialogue:
            self._draw_speech_bubble(screen, camera, self.current_dialogue)
    
    def _draw_speech_bubble(self, screen, camera, text):
        """Draw speech bubble above player"""
        font = pygame.font.Font(None, 16)
        words = text.split(' ')
        lines = []
        current_line = ""
        
        # Word wrap
        for word in words:
            test_line = current_line + (" " if current_line else "") + word
            if font.size(test_line)[0] > 200:
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
        max_width = max(font.size(line)[0] for line in lines) + 20
        bubble_height = len(lines) * 20 + 10
        
        # Position bubble above player
        player_rect = camera.apply(self)
        bubble_x = player_rect.centerx - max_width // 2
        bubble_y = player_rect.top - bubble_height - 10
        
        # Keep bubble on screen
        bubble_x = max(5, min(bubble_x, screen.get_width() - max_width - 5))
        bubble_y = max(5, bubble_y)
        
        # Draw bubble background
        bubble_rect = pygame.Rect(bubble_x, bubble_y, max_width, bubble_height)
        pygame.draw.rect(screen, (255, 255, 255, 220), bubble_rect, border_radius=10)
        pygame.draw.rect(screen, (100, 100, 100), bubble_rect, 2, border_radius=10)
        
        # Draw text
        y_offset = bubble_y + 5
        for line in lines:
            text_surface = font.render(line, True, (50, 50, 50))
            text_rect = text_surface.get_rect()
            text_rect.centerx = bubble_x + max_width // 2
            text_rect.y = y_offset
            screen.blit(text_surface, text_rect)
            y_offset += 20
    
    def interact_with_npc(self, npc, interaction_type: str, custom_message: str = None):
        """Handle interaction with an NPC"""
        # Initialize relationship if doesn't exist
        if npc.name not in self.relationships:
            self.relationships[npc.name] = 0.3
        
        if npc.name not in npc.relationships:
            npc.relationships[self.name] = 0.3
        
        # Handle different interaction types
        if interaction_type == "greet":
            self._greet_npc(npc)
        elif interaction_type == "chat":
            self._chat_with_npc(npc)
        elif interaction_type == "give_gift":
            self._give_gift_to_npc(npc)
        elif interaction_type == "invite_activity":
            self._invite_npc_to_activity(npc)
        elif interaction_type == "ask_about":
            self._ask_npc_about(npc)
        elif interaction_type == "custom_dialogue":
            self._custom_dialogue_with_npc(npc, custom_message)
    
    def _greet_npc(self, npc):
        """Simple greeting interaction"""
        greetings = [
            f"Hi {npc.name}!",
            f"Hello there, {npc.name}!",
            f"Hey {npc.name}, how are you?",
            f"Good to see you, {npc.name}!"
        ]
        
        import random
        greeting = random.choice(greetings)
        self.say(greeting)
        
        # Small relationship boost
        self._adjust_relationship(npc, 0.05)
        npc._adjust_relationship(self, 0.05)
        
        # NPC responds
        npc_responses = [
            f"Hi {self.name}!",
            "Hello! Nice to see you!",
            "Hey there!",
            "Good to see you too!"
        ]
        npc.say(random.choice(npc_responses))
    
    def _chat_with_npc(self, npc):
        """Start a conversation with NPC"""
        chat_starters = [
            "How's your day going?",
            "What have you been up to?",
            "Anything interesting happening?",
            "How are you feeling today?"
        ]
        
        import random
        starter = random.choice(chat_starters)
        self.say(starter)
        
        # Bigger relationship boost for meaningful conversation
        self._adjust_relationship(npc, 0.1)
        npc._adjust_relationship(self, 0.1)
        
        # Trigger AI response from NPC
        if hasattr(npc, 'ai_client') and npc.ai_client:
            self._trigger_npc_ai_response(npc, f"Player {self.name} is chatting with you. They said: '{starter}'")
    
    def _give_gift_to_npc(self, npc):
        """Give a virtual gift to NPC"""
        gifts = ["flowers", "chocolate", "book", "music", "art"]
        import random
        gift = random.choice(gifts)
        
        self.say(f"I have {gift} for you, {npc.name}!")
        
        # Significant relationship boost
        self._adjust_relationship(npc, 0.2)
        npc._adjust_relationship(self, 0.2)
        
        npc.say(f"Thank you so much, {self.name}! I love {gift}!")
    
    def _invite_npc_to_activity(self, npc):
        """Invite NPC to do an activity"""
        activities = ["go for a walk", "play a game", "have lunch", "watch a movie", "explore around"]
        import random
        activity = random.choice(activities)
        
        self.say(f"Want to {activity} together, {npc.name}?")
        
        # Relationship affects response
        relationship = self.relationships.get(npc.name, 0.3)
        if relationship > 0.6:
            npc.say(f"I'd love to {activity} with you, {self.name}!")
            self._adjust_relationship(npc, 0.15)
            npc._adjust_relationship(self, 0.15)
        else:
            npc.say(f"Maybe another time, {self.name}.")
            self._adjust_relationship(npc, 0.05)
            npc._adjust_relationship(self, 0.05)
    
    def _ask_npc_about(self, npc):
        """Ask NPC about something"""
        topics = ["your day", "your hobbies", "your dreams", "this place", "your friends"]
        import random
        topic = random.choice(topics)
        
        self.say(f"Tell me about {topic}, {npc.name}.")
        
        self._adjust_relationship(npc, 0.08)
        npc._adjust_relationship(self, 0.08)
        
        # Trigger AI response
        if hasattr(npc, 'ai_client') and npc.ai_client:
            self._trigger_npc_ai_response(npc, f"Player {self.name} asked you about {topic}.")
    
    def _custom_dialogue_with_npc(self, npc, message):
        """Custom dialogue with NPC"""
        self.say(message)
        
        # Relationship change based on message sentiment (simple)
        if any(word in message.lower() for word in ['love', 'like', 'great', 'awesome', 'wonderful']):
            self._adjust_relationship(npc, 0.1)
            npc._adjust_relationship(self, 0.1)
        elif any(word in message.lower() for word in ['hate', 'dislike', 'terrible', 'awful', 'bad']):
            self._adjust_relationship(npc, -0.1)
            npc._adjust_relationship(self, -0.1)
        else:
            self._adjust_relationship(npc, 0.05)
            npc._adjust_relationship(self, 0.05)
        
        # Trigger AI response
        if hasattr(npc, 'ai_client') and npc.ai_client:
            self._trigger_npc_ai_response(npc, f"Player {self.name} said to you: '{message}'")
    
    def _adjust_relationship(self, npc, change):
        """Adjust relationship with NPC"""
        if npc.name not in self.relationships:
            self.relationships[npc.name] = 0.3
        
        self.relationships[npc.name] = max(0, min(1, self.relationships[npc.name] + change))
    
    def _trigger_npc_ai_response(self, npc, context):
        """Trigger an AI response from the NPC"""
        # This will be handled by the game loop
        # Set a flag that the NPC should respond to player interaction
        npc.player_interaction_context = context
        npc.ai_decision_cooldown = 0.1  # Respond quickly to player
    
    def say(self, text):
        """Make player say something"""
        self.current_dialogue = text
        self.dialogue_timer = 8.0  # Show for 8 seconds
    
    def get_nearby_npcs(self, npcs, max_distance=100):
        """Get list of NPCs within interaction range"""
        nearby = []
        for npc in npcs:
            distance = pygame.math.Vector2(
                self.rect.centerx - npc.rect.centerx,
                self.rect.centery - npc.rect.centery
            ).length()
            
            if distance <= max_distance:
                nearby.append((npc, distance))
        
        # Sort by distance
        nearby.sort(key=lambda x: x[1])
        return [npc for npc, distance in nearby]