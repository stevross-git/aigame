import pygame
import math
import random
from enum import Enum
import src.core.constants as constants
from src.entities.personality import Personality
from src.graphics.custom_asset_manager import CustomAssetManager

class Direction(Enum):
    IDLE = "idle"
    UP = "up"
    DOWN = "down"
    LEFT = "left"
    RIGHT = "right"

class EnhancedPlayer(pygame.sprite.Sprite):
    """
    Enhanced player with smooth movement, animations, and visual effects
    """
    
    def __init__(self, x, y, character_data=None):
        super().__init__()
        
        # Initialize custom asset manager
        self.assets = CustomAssetManager()
        
        # Set character data
        if character_data:
            self.name = character_data["name"]
            self.color = character_data["color"]
            self.personality = Personality(**character_data["personality"])
            self.skin = character_data.get("skin", "male")  # Use selected skin
        else:
            self.name = "Player"
            self.color = constants.BLUE
            self.personality = Personality()
            self.skin = "male"  # Default skin
        
        # Enhanced movement properties
        self.speed = constants.PLAYER_SPEED * 1.2  # Slightly faster base speed
        self.max_speed = self.speed * 2.0  # Running speed
        self.acceleration = 800.0  # Pixels per second squared
        self.deceleration = 1200.0  # Faster deceleration for snappy feel
        self.diagonal_factor = 0.707  # For proper diagonal movement
        
        # Position and physics
        self.rect = pygame.Rect(x, y, 24, 32)
        self.precise_x = float(x)
        self.precise_y = float(y)
        self.velocity = pygame.math.Vector2(0, 0)
        self.target_velocity = pygame.math.Vector2(0, 0)
        
        # Animation system
        self.current_direction = Direction.DOWN
        self.is_moving = False
        self.was_moving = False
        self.animation_time = 0.0
        self.frame_time = 0.15  # Time between animation frames
        self.current_frame = 0
        self.bob_offset = 0.0  # For walking bob animation
        
        # Enhanced visual effects
        self.movement_trail = []  # Trail of recent positions
        self.max_trail_length = 8
        self.dust_particles = []  # Dust particles when moving
        self.step_timer = 0.0
        self.step_interval = 0.3  # Time between steps
        
        # Load sprites and animations
        self._load_sprites()
        
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
        
        # Enhanced input handling
        self.input_buffer = []
        self.buffer_time = 0.1  # 100ms input buffer
        self.is_running = False  # Shift key held
        
        # Camera shake for dynamic movement
        self.camera_shake_intensity = 0.0
        self.camera_shake_duration = 0.0
    
    def _load_sprites(self):
        """Load player sprites for different directions and animations"""
        # Try to get directional sprites
        self.sprites = {
            Direction.IDLE: [],
            Direction.UP: [],
            Direction.DOWN: [],
            Direction.LEFT: [],
            Direction.RIGHT: []
        }
        
        # Load player sprite based on selected skin
        main_sprite = self.assets.get_character_sprite(self.skin)
        if not main_sprite:
            # Try to load default player sprite
            main_sprite = self.assets.get_character_sprite("player")
        
        if main_sprite:
            # Use main sprite for all directions (can be expanded later)
            for direction in Direction:
                self.sprites[direction] = [main_sprite.copy()]
        else:
            # Fallback: create colored rectangles with directional indicators
            self._create_fallback_sprites()
        
        # Set initial sprite
        self.image = self.sprites[self.current_direction][0].copy()
    
    def _create_fallback_sprites(self):
        """Create fallback sprites with directional indicators"""
        base_surface = pygame.Surface((24, 32), pygame.SRCALPHA)
        base_surface.fill(self.color)
        
        # Create sprites for each direction with visual indicators
        directions_data = {
            Direction.IDLE: (12, 16, "●"),
            Direction.UP: (12, 8, "▲"),
            Direction.DOWN: (12, 24, "▼"),
            Direction.LEFT: (6, 16, "◄"),
            Direction.RIGHT: (18, 16, "►")
        }
        
        font = pygame.font.Font(None, 16)
        for direction, (x, y, symbol) in directions_data.items():
            sprite = base_surface.copy()
            symbol_surface = font.render(symbol, True, (255, 255, 255))
            symbol_rect = symbol_surface.get_rect(center=(x, y))
            sprite.blit(symbol_surface, symbol_rect)
            self.sprites[direction] = [sprite]
    
    def update(self, dt, keys):
        """Enhanced update with smooth movement and animations"""
        old_velocity = self.velocity.copy()
        
        # Handle input with buffer and enhanced controls
        self._handle_input(keys, dt)
        
        # Update physics with smooth acceleration/deceleration
        self._update_physics(dt)
        
        # Update position with precise floating-point movement
        self._update_position(dt)
        
        # Update animations based on movement
        self._update_animation(dt)
        
        # Update visual effects
        self._update_visual_effects(dt, old_velocity)
        
        # Update dialogue timer
        if self.dialogue_timer > 0:
            self.dialogue_timer -= dt
            if self.dialogue_timer <= 0:
                self.current_dialogue = None
        
        # Update camera shake
        if self.camera_shake_duration > 0:
            self.camera_shake_duration -= dt
            if self.camera_shake_duration <= 0:
                self.camera_shake_intensity = 0.0
    
    def _handle_input(self, keys, dt):
        """Enhanced input handling with buffering and modifiers"""
        # Check for running modifier
        self.is_running = keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]
        
        # Calculate target velocity based on input
        input_x = 0
        input_y = 0
        
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            input_x -= 1
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            input_x += 1
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            input_y -= 1
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            input_y += 1
        
        # Calculate target velocity
        if input_x != 0 or input_y != 0:
            # Normalize diagonal movement
            if input_x != 0 and input_y != 0:
                input_x *= self.diagonal_factor
                input_y *= self.diagonal_factor
            
            # Set target speed based on running state
            target_speed = self.max_speed if self.is_running else self.speed
            
            self.target_velocity.x = input_x * target_speed
            self.target_velocity.y = input_y * target_speed
            
            # Update direction based on primary movement
            if abs(input_x) > abs(input_y):
                self.current_direction = Direction.RIGHT if input_x > 0 else Direction.LEFT
            else:
                self.current_direction = Direction.DOWN if input_y > 0 else Direction.UP
        else:
            # No input - stop
            self.target_velocity.x = 0
            self.target_velocity.y = 0
            if self.velocity.length() < 10:  # Almost stopped
                self.current_direction = Direction.IDLE
    
    def _update_physics(self, dt):
        """Update physics with smooth acceleration and deceleration"""
        # Calculate velocity difference
        vel_diff = self.target_velocity - self.velocity
        
        if vel_diff.length() > 0:
            # Accelerating
            if self.target_velocity.length() > 0:
                accel_rate = self.acceleration
            else:
                # Decelerating
                accel_rate = self.deceleration
            
            # Apply acceleration
            max_change = accel_rate * dt
            if vel_diff.length() <= max_change:
                self.velocity = self.target_velocity.copy()
            else:
                vel_diff.normalize_ip()
                self.velocity += vel_diff * max_change
        
        # Update movement state
        self.was_moving = self.is_moving
        self.is_moving = self.velocity.length() > 5  # Threshold for "moving"
    
    def _update_position(self, dt):
        """Update position with precise movement and collision"""
        # Store old position
        old_x, old_y = self.precise_x, self.precise_y
        
        # Update precise position
        self.precise_x += self.velocity.x * dt
        self.precise_y += self.velocity.y * dt
        
        # Apply map boundaries
        self.precise_x = max(0, min(self.precise_x, constants.MAP_WIDTH - self.rect.width))
        self.precise_y = max(0, min(self.precise_y, constants.MAP_HEIGHT - self.rect.height))
        
        # Update rect position
        self.rect.x = int(self.precise_x)
        self.rect.y = int(self.precise_y)
        
        # Add to movement trail
        if self.is_moving:
            self.movement_trail.append((self.rect.centerx, self.rect.centery))
            if len(self.movement_trail) > self.max_trail_length:
                self.movement_trail.pop(0)
    
    def _update_animation(self, dt):
        """Update sprite animations and effects"""
        if self.is_moving:
            self.animation_time += dt
            
            # Update walking bob
            bob_speed = 8.0 if self.is_running else 6.0
            self.bob_offset = math.sin(self.animation_time * bob_speed) * 2.0
            
            # Frame animation (if multiple frames available)
            if len(self.sprites[self.current_direction]) > 1:
                if self.animation_time >= self.frame_time:
                    self.current_frame = (self.current_frame + 1) % len(self.sprites[self.current_direction])
                    self.animation_time = 0.0
        else:
            # Reset to idle
            self.animation_time = 0.0
            self.current_frame = 0
            self.bob_offset *= 0.9  # Smooth settle
        
        # Update sprite
        self.image = self.sprites[self.current_direction][self.current_frame].copy()
        
        # Apply running tint
        if self.is_running and self.is_moving:
            # Add slight red tint for running
            red_overlay = pygame.Surface(self.image.get_size(), pygame.SRCALPHA)
            red_overlay.fill((255, 100, 100, 30))
            self.image.blit(red_overlay, (0, 0))
    
    def _update_visual_effects(self, dt, old_velocity):
        """Update dust particles and other visual effects"""
        # Update step timer for dust particles
        if self.is_moving:
            self.step_timer += dt
            if self.step_timer >= self.step_interval:
                self._create_dust_particle()
                self.step_timer = 0.0
                
                # Camera shake for running
                if self.is_running:
                    self._add_camera_shake(1.0, 0.1)
        
        # Update existing dust particles
        for particle in self.dust_particles[:]:
            particle['life'] -= dt
            particle['y'] += particle['vel_y'] * dt
            particle['x'] += particle['vel_x'] * dt
            particle['alpha'] *= 0.95
            
            if particle['life'] <= 0 or particle['alpha'] < 10:
                self.dust_particles.remove(particle)
        
        # Clear trail if not moving
        if not self.is_moving and len(self.movement_trail) > 0:
            # Gradually reduce trail
            if len(self.movement_trail) > 0:
                self.movement_trail.pop(0)
    
    def _create_dust_particle(self):
        """Create a dust particle behind the player"""
        # Create dust particle slightly behind movement direction
        offset_x = -self.velocity.x * 0.01 if self.velocity.x != 0 else 0
        offset_y = -self.velocity.y * 0.01 if self.velocity.y != 0 else 0
        
        particle = {
            'x': self.rect.centerx + offset_x + random.uniform(-5, 5),
            'y': self.rect.bottom - 5,
            'vel_x': random.uniform(-20, 20),
            'vel_y': random.uniform(-30, -10),
            'life': 0.5,
            'alpha': 100,
            'size': random.uniform(2, 4)
        }
        self.dust_particles.append(particle)
        
        # Limit particle count
        if len(self.dust_particles) > 20:
            self.dust_particles.pop(0)
    
    def _add_camera_shake(self, intensity, duration):
        """Add camera shake effect"""
        self.camera_shake_intensity = max(self.camera_shake_intensity, intensity)
        self.camera_shake_duration = max(self.camera_shake_duration, duration)
    
    def draw(self, screen, camera):
        """Enhanced drawing with visual effects"""
        # Get screen position
        screen_pos = camera.apply(self)
        
        # Apply bob offset
        draw_y = screen_pos.y + int(self.bob_offset)
        draw_pos = (screen_pos.x, draw_y)
        
        # Draw movement trail
        self._draw_movement_trail(screen, camera)
        
        # Draw dust particles
        self._draw_dust_particles(screen, camera)
        
        # Draw main sprite with shadow
        self._draw_sprite_with_shadow(screen, draw_pos)
        
        # Draw speed indicator
        if self.is_running and self.is_moving:
            self._draw_speed_lines(screen, draw_pos)
        
        # Draw player name with better styling
        self._draw_player_name(screen, draw_pos)
        
        # Draw speech bubble if talking
        if self.current_dialogue:
            self._draw_speech_bubble(screen, camera, self.current_dialogue)
    
    def _draw_movement_trail(self, screen, camera):
        """Draw subtle movement trail"""
        if len(self.movement_trail) < 2:
            return
        
        for i, (x, y) in enumerate(self.movement_trail):
            alpha = int(50 * (i / len(self.movement_trail)))
            if alpha > 10:
                trail_rect = pygame.Rect(x - 2, y - 2, 4, 4)
                screen_rect = camera.apply_rect(trail_rect)
                
                # Create trail surface with alpha
                trail_surface = pygame.Surface((4, 4), pygame.SRCALPHA)
                trail_surface.fill((*self.color[:3], alpha))
                screen.blit(trail_surface, screen_rect)
    
    def _draw_dust_particles(self, screen, camera):
        """Draw dust particles"""
        for particle in self.dust_particles:
            if particle['alpha'] > 10:
                particle_rect = pygame.Rect(
                    particle['x'] - particle['size']/2,
                    particle['y'] - particle['size']/2,
                    particle['size'],
                    particle['size']
                )
                screen_rect = camera.apply_rect(particle_rect)
                
                # Create particle surface
                particle_surface = pygame.Surface((int(particle['size']), int(particle['size'])), pygame.SRCALPHA)
                particle_color = (139, 120, 93, int(particle['alpha']))  # Dusty brown
                particle_surface.fill(particle_color)
                screen.blit(particle_surface, screen_rect)
    
    def _draw_sprite_with_shadow(self, screen, draw_pos):
        """Draw sprite with dynamic shadow"""
        # Draw shadow (slightly offset and darkened)
        shadow_surface = self.image.copy()
        shadow_surface.fill((0, 0, 0, 100), special_flags=pygame.BLEND_RGBA_MULT)
        shadow_pos = (draw_pos[0] + 2, draw_pos[1] + 2)
        screen.blit(shadow_surface, shadow_pos)
        
        # Draw main sprite
        screen.blit(self.image, draw_pos)
    
    def _draw_speed_lines(self, screen, draw_pos):
        """Draw speed lines when running"""
        if not self.is_moving or not self.is_running:
            return
        
        # Draw motion lines behind player
        line_color = (255, 255, 255, 100)
        for i in range(3):
            offset = 5 + i * 3
            start_x = draw_pos[0] - int(self.velocity.x * 0.1) - offset
            start_y = draw_pos[1] - int(self.velocity.y * 0.1) + i * 4
            end_x = start_x - 8
            end_y = start_y
            
            if 0 <= start_x < screen.get_width() and 0 <= start_y < screen.get_height():
                line_surface = pygame.Surface((10, 2), pygame.SRCALPHA)
                line_surface.fill(line_color)
                screen.blit(line_surface, (end_x, end_y))
    
    def _draw_player_name(self, screen, draw_pos):
        """Draw player name with enhanced styling"""
        font = pygame.font.Font(None, 20)
        name_color = (255, 255, 150) if self.is_running else (255, 255, 100)
        name_text = font.render(self.name, True, name_color)
        
        # Add shadow
        shadow_text = font.render(self.name, True, (0, 0, 0))
        
        text_rect = name_text.get_rect()
        text_rect.centerx = draw_pos[0] + self.rect.width // 2
        text_rect.bottom = draw_pos[1] - 8
        
        # Draw shadow first
        shadow_rect = text_rect.copy()
        shadow_rect.x += 1
        shadow_rect.y += 1
        screen.blit(shadow_text, shadow_rect)
        
        # Draw name
        screen.blit(name_text, text_rect)
        
        # Add movement indicator
        if self.is_moving:
            indicator = "🏃" if self.is_running else "🚶"
            indicator_surface = font.render(indicator, True, (255, 255, 255))
            indicator_rect = indicator_surface.get_rect()
            indicator_rect.left = text_rect.right + 5
            indicator_rect.centery = text_rect.centery
            screen.blit(indicator_surface, indicator_rect)
    
    def _draw_speech_bubble(self, screen, camera, text):
        """Enhanced speech bubble drawing"""
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
        bubble_height = len(lines) * 20 + 15
        
        # Position bubble above player
        player_rect = camera.apply(self)
        bubble_x = player_rect.centerx - max_width // 2
        bubble_y = player_rect.top - bubble_height - 15
        
        # Keep bubble on screen
        bubble_x = max(5, min(bubble_x, screen.get_width() - max_width - 5))
        bubble_y = max(5, bubble_y)
        
        # Draw bubble background with better styling
        bubble_rect = pygame.Rect(bubble_x, bubble_y, max_width, bubble_height)
        
        # Draw bubble shadow
        shadow_rect = bubble_rect.copy()
        shadow_rect.x += 2
        shadow_rect.y += 2
        pygame.draw.rect(screen, (0, 0, 0, 100), shadow_rect, border_radius=12)
        
        # Draw bubble
        pygame.draw.rect(screen, (255, 255, 255, 240), bubble_rect, border_radius=10)
        pygame.draw.rect(screen, (150, 150, 150), bubble_rect, 2, border_radius=10)
        
        # Draw pointer
        pointer_points = [
            (bubble_x + max_width // 2 - 8, bubble_y + bubble_height),
            (bubble_x + max_width // 2, bubble_y + bubble_height + 8),
            (bubble_x + max_width // 2 + 8, bubble_y + bubble_height)
        ]
        pygame.draw.polygon(screen, (255, 255, 255), pointer_points)
        pygame.draw.polygon(screen, (150, 150, 150), pointer_points, 2)
        
        # Draw text
        y_offset = bubble_y + 8
        for line in lines:
            text_surface = font.render(line, True, (50, 50, 50))
            text_rect = text_surface.get_rect()
            text_rect.centerx = bubble_x + max_width // 2
            text_rect.y = y_offset
            screen.blit(text_surface, text_rect)
            y_offset += 20
    
    def get_camera_shake(self):
        """Get current camera shake values"""
        if self.camera_shake_duration > 0:
            import random
            shake_x = random.uniform(-self.camera_shake_intensity, self.camera_shake_intensity)
            shake_y = random.uniform(-self.camera_shake_intensity, self.camera_shake_intensity)
            return shake_x, shake_y
        return 0, 0
    
    # Keep all the interaction methods from the original player
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