import pygame
import math
import random
from src.core.constants import *
from src.graphics.custom_asset_manager import CustomAssetManager

class CharacterLoadingScreen:
    """
    Fun loading screen that appears after character creation with dancing sprites and AI jokes
    """
    
    def __init__(self, screen):
        self.screen = screen
        self.assets = CustomAssetManager()
        
        # Fonts
        self.font_title = pygame.font.Font(None, 48)
        self.font_joke = pygame.font.Font(None, 24)
        self.font_loading = pygame.font.Font(None, 32)
        
        # Animation state
        self.animation_time = 0.0
        self.progress = 0.0
        self.loading_text = "Loading Your World"
        
        # Colors
        self.bg_color = (15, 20, 35)
        self.accent_color = (255, 180, 50)
        self.text_color = (255, 255, 255)
        self.joke_color = (200, 255, 200)
        
        # AI Sims jokes
        self.jokes = [
            "Why did the AI refuse to clean the house?\nIt said 'I'm a neural network, not a cleaning network!'",
            "What do you call an AI that's always hungry?\nA feed-forward network! 🍕",
            "Why don't AI Sims ever get lost?\nThey always know their way around the decision tree! 🌳",
            "What's an AI's favorite type of music?\nAlgo-rhythms! 🎵",
            "Why did the AI Sim break up with their partner?\nThey said the relationship had too much overfitting! 💔"
        ]
        
        # Current joke
        self.current_joke_index = 0
        self.joke_timer = 0.0
        self.joke_display_time = 3.0  # Show each joke for 3 seconds
        
        # Dancing characters setup
        self.dancers = []
        self._setup_dancers()
        
        # Particle effects
        self.particles = []
        self._init_particles()
    
    def _setup_dancers(self):
        """Setup dancing character sprites"""
        # Get character sprites for dancing
        character_types = ["male", "female", "girl1", "walking"]
        
        for i, char_type in enumerate(character_types):
            sprite = self.assets.get_sprite(char_type)
            if sprite:
                dancer = {
                    'sprite': sprite,
                    'x': 150 + i * 150,
                    'y': SCREEN_HEIGHT // 2 + 50,
                    'base_y': SCREEN_HEIGHT // 2 + 50,
                    'bounce_offset': i * 0.5,  # Stagger the bouncing
                    'dance_type': i % 3,  # Different dance moves
                    'rotation': 0.0,
                    'scale': 1.0
                }
                self.dancers.append(dancer)
        
        # If no sprites loaded, create fallback dancers
        if not self.dancers:
            for i in range(4):
                fallback_sprite = pygame.Surface((24, 32))
                colors = [(255, 100, 100), (100, 255, 100), (100, 100, 255), (255, 255, 100)]
                fallback_sprite.fill(colors[i])
                
                dancer = {
                    'sprite': fallback_sprite,
                    'x': 150 + i * 150,
                    'y': SCREEN_HEIGHT // 2 + 50,
                    'base_y': SCREEN_HEIGHT // 2 + 50,
                    'bounce_offset': i * 0.5,
                    'dance_type': i % 3,
                    'rotation': 0.0,
                    'scale': 1.0
                }
                self.dancers.append(dancer)
    
    def _init_particles(self):
        """Initialize fun particle effects"""
        for _ in range(20):
            particle = {
                'x': random.randint(0, SCREEN_WIDTH),
                'y': random.randint(0, SCREEN_HEIGHT),
                'vx': random.uniform(-50, 50),
                'vy': random.uniform(-30, 30),
                'life': random.uniform(2.0, 5.0),
                'max_life': random.uniform(2.0, 5.0),
                'color': random.choice([
                    (255, 255, 100), (255, 180, 100), (100, 255, 255), 
                    (255, 100, 255), (100, 255, 100)
                ]),
                'size': random.randint(2, 5)
            }
            self.particles.append(particle)
    
    def update(self, dt):
        """Update animations and effects"""
        self.animation_time += dt
        
        # Update joke rotation
        self.joke_timer += dt
        if self.joke_timer >= self.joke_display_time:
            self.joke_timer = 0.0
            self.current_joke_index = (self.current_joke_index + 1) % len(self.jokes)
        
        # Update dancers
        for dancer in self.dancers:
            # Bouncing animation
            if dancer['dance_type'] == 0:
                # Simple bounce
                dancer['y'] = dancer['base_y'] + math.sin(self.animation_time * 4 + dancer['bounce_offset']) * 20
                dancer['scale'] = 1.0 + math.sin(self.animation_time * 4 + dancer['bounce_offset']) * 0.2
            
            elif dancer['dance_type'] == 1:
                # Side to side dance
                dancer['x'] = dancer['x'] + math.sin(self.animation_time * 3 + dancer['bounce_offset']) * 2
                dancer['y'] = dancer['base_y'] + math.sin(self.animation_time * 6 + dancer['bounce_offset']) * 15
                dancer['rotation'] = math.sin(self.animation_time * 2 + dancer['bounce_offset']) * 5
            
            else:
                # Spinning dance
                dancer['rotation'] = self.animation_time * 90 + dancer['bounce_offset'] * 45
                dancer['y'] = dancer['base_y'] + math.sin(self.animation_time * 5 + dancer['bounce_offset']) * 10
                dancer['scale'] = 1.0 + math.sin(self.animation_time * 3 + dancer['bounce_offset']) * 0.15
        
        # Update particles
        for particle in self.particles:
            particle['x'] += particle['vx'] * dt
            particle['y'] += particle['vy'] * dt
            particle['life'] -= dt
            
            # Wrap around screen
            if particle['x'] < 0:
                particle['x'] = SCREEN_WIDTH
            elif particle['x'] > SCREEN_WIDTH:
                particle['x'] = 0
            
            if particle['y'] < 0:
                particle['y'] = SCREEN_HEIGHT
            elif particle['y'] > SCREEN_HEIGHT:
                particle['y'] = 0
            
            # Reset particle if it dies
            if particle['life'] <= 0:
                particle['x'] = random.randint(0, SCREEN_WIDTH)
                particle['y'] = random.randint(0, SCREEN_HEIGHT)
                particle['life'] = particle['max_life']
    
    def set_progress(self, progress: float, message: str = ""):
        """Update loading progress (0.0 to 1.0)"""
        self.progress = max(0.0, min(1.0, progress))
        if message:
            self.loading_text = message
    
    def draw(self):
        """Draw the fun loading screen"""
        # Clear screen with animated gradient
        self._draw_animated_background()
        
        # Draw particles
        self._draw_particles()
        
        # Title with bounce effect
        title_bounce = math.sin(self.animation_time * 2) * 5
        title_text = self.font_title.render("🎮 Preparing Your AI World! 🎮", True, self.accent_color)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, 80 + title_bounce))
        self.screen.blit(title_text, title_rect)
        
        # Dancing characters
        self._draw_dancing_characters()
        
        # Current joke with typewriter effect
        self._draw_current_joke()
        
        # Loading progress with fun animation
        self._draw_fun_progress_bar()
        
        # Loading text with dots animation
        dots = "." * (int(self.animation_time * 3) % 4)
        loading_display = f"{self.loading_text}{dots}"
        loading_surface = self.font_loading.render(loading_display, True, self.text_color)
        loading_rect = loading_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 80))
        self.screen.blit(loading_surface, loading_rect)
        
        # Fun emoji rain
        self._draw_emoji_rain()
    
    def _draw_animated_background(self):
        """Draw animated gradient background"""
        for y in range(SCREEN_HEIGHT):
            # Create moving wave effect
            wave = math.sin(y * 0.01 + self.animation_time) * 0.3
            color_factor = (y / SCREEN_HEIGHT) + wave
            
            r = int(self.bg_color[0] * (1 + color_factor * 0.2))
            g = int(self.bg_color[1] * (1 + color_factor * 0.3))
            b = int(self.bg_color[2] * (1 + color_factor * 0.5))
            
            color = (
                max(0, min(255, r)), 
                max(0, min(255, g)), 
                max(0, min(255, b))
            )
            pygame.draw.line(self.screen, color, (0, y), (SCREEN_WIDTH, y))
    
    def _draw_particles(self):
        """Draw floating particles"""
        for particle in self.particles:
            alpha = int(255 * (particle['life'] / particle['max_life']))
            color = (*particle['color'], alpha)
            
            # Create particle surface with alpha
            particle_surface = pygame.Surface((particle['size'] * 2, particle['size'] * 2), pygame.SRCALPHA)
            pygame.draw.circle(particle_surface, particle['color'], (particle['size'], particle['size']), particle['size'])
            
            self.screen.blit(particle_surface, (int(particle['x']), int(particle['y'])))
    
    def _draw_dancing_characters(self):
        """Draw the dancing character sprites"""
        for dancer in self.dancers:
            # Get sprite and apply transformations
            sprite = dancer['sprite']
            
            # Apply scaling
            if dancer['scale'] != 1.0:
                new_size = (int(sprite.get_width() * dancer['scale']), int(sprite.get_height() * dancer['scale']))
                sprite = pygame.transform.scale(sprite, new_size)
            
            # Apply rotation
            if dancer['rotation'] != 0:
                sprite = pygame.transform.rotate(sprite, dancer['rotation'])
            
            # Draw sprite
            sprite_rect = sprite.get_rect(center=(int(dancer['x']), int(dancer['y'])))
            self.screen.blit(sprite, sprite_rect)
            
            # Add fun glow effect
            glow_surface = pygame.Surface((sprite.get_width() + 10, sprite.get_height() + 10), pygame.SRCALPHA)
            glow_color = (*self.accent_color, 30)
            pygame.draw.ellipse(glow_surface, glow_color, glow_surface.get_rect(), 5)
            glow_rect = glow_surface.get_rect(center=sprite_rect.center)
            self.screen.blit(glow_surface, glow_rect)
    
    def _draw_current_joke(self):
        """Draw the current joke with nice formatting"""
        if self.current_joke_index < len(self.jokes):
            joke = self.jokes[self.current_joke_index]
            lines = joke.split('\n')
            
            # Background panel for joke
            panel_width = 600
            panel_height = len(lines) * 30 + 40
            panel_x = (SCREEN_WIDTH - panel_width) // 2
            panel_y = SCREEN_HEIGHT // 2 - 100
            
            # Draw panel with rounded corners
            panel_surface = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
            pygame.draw.rect(panel_surface, (20, 30, 50, 200), (0, 0, panel_width, panel_height), border_radius=15)
            pygame.draw.rect(panel_surface, self.joke_color, (0, 0, panel_width, panel_height), 3, border_radius=15)
            self.screen.blit(panel_surface, (panel_x, panel_y))
            
            # Draw joke text
            for i, line in enumerate(lines):
                text_surface = self.font_joke.render(line, True, self.joke_color)
                text_rect = text_surface.get_rect(center=(SCREEN_WIDTH // 2, panel_y + 25 + i * 30))
                self.screen.blit(text_surface, text_rect)
            
            # Add joke number indicator
            joke_num = f"Joke {self.current_joke_index + 1}/{len(self.jokes)}"
            num_surface = self.font_joke.render(joke_num, True, (150, 150, 150))
            num_rect = num_surface.get_rect(center=(SCREEN_WIDTH // 2, panel_y + panel_height + 15))
            self.screen.blit(num_surface, num_rect)
    
    def _draw_fun_progress_bar(self):
        """Draw animated progress bar with fun effects"""
        bar_width = 400
        bar_height = 25
        bar_x = (SCREEN_WIDTH - bar_width) // 2
        bar_y = SCREEN_HEIGHT - 150
        
        # Animated background with rainbow effect
        bg_rect = pygame.Rect(bar_x, bar_y, bar_width, bar_height)
        rainbow_color = self._get_rainbow_color(self.animation_time)
        pygame.draw.rect(self.screen, (40, 40, 40), bg_rect, border_radius=12)
        pygame.draw.rect(self.screen, rainbow_color, bg_rect, 3, border_radius=12)
        
        # Progress fill with animated pattern
        if self.progress > 0:
            fill_width = int(bar_width * self.progress)
            fill_rect = pygame.Rect(bar_x, bar_y, fill_width, bar_height)
            
            # Create animated fill pattern
            fill_surface = pygame.Surface((fill_width, bar_height), pygame.SRCALPHA)
            for i in range(0, fill_width, 10):
                wave_offset = math.sin(self.animation_time * 3 + i * 0.1) * 5
                stripe_color = self._get_rainbow_color(self.animation_time + i * 0.01)
                pygame.draw.rect(fill_surface, stripe_color, (i, 0, 8, bar_height))
            
            pygame.draw.rect(fill_surface, rainbow_color, (0, 0, fill_width, bar_height), border_radius=12)
            self.screen.blit(fill_surface, fill_rect)
            
            # Shine effect
            shine_rect = pygame.Rect(bar_x + 2, bar_y + 2, max(0, fill_width - 4), bar_height // 3)
            shine_color = (255, 255, 255, 100)
            shine_surface = pygame.Surface((shine_rect.width, shine_rect.height), pygame.SRCALPHA)
            pygame.draw.rect(shine_surface, shine_color, (0, 0, shine_rect.width, shine_rect.height), border_radius=8)
            self.screen.blit(shine_surface, shine_rect)
        
        # Percentage text with bounce
        percentage_bounce = math.sin(self.animation_time * 4) * 3
        percentage_text = f"{int(self.progress * 100)}%"
        percentage_surface = self.font_loading.render(percentage_text, True, self.accent_color)
        percentage_rect = percentage_surface.get_rect(center=(SCREEN_WIDTH // 2, bar_y + bar_height + 30 + percentage_bounce))
        self.screen.blit(percentage_surface, percentage_rect)
    
    def _draw_emoji_rain(self):
        """Draw falling emoji effects"""
        emojis = ["🎮", "🤖", "🏠", "🌟", "💫", "🎉", "✨"]
        
        for i in range(8):
            emoji_time = self.animation_time + i * 0.5
            x = (i * SCREEN_WIDTH / 8) + math.sin(emoji_time) * 50
            y = (emoji_time * 30) % (SCREEN_HEIGHT + 50) - 50
            
            emoji = emojis[i % len(emojis)]
            emoji_surface = self.font_loading.render(emoji, True, (255, 255, 255))
            
            # Add slight rotation
            rotation = math.sin(emoji_time * 2) * 15
            if rotation != 0:
                emoji_surface = pygame.transform.rotate(emoji_surface, rotation)
            
            emoji_rect = emoji_surface.get_rect(center=(int(x), int(y)))
            self.screen.blit(emoji_surface, emoji_rect)
    
    def _get_rainbow_color(self, time_offset):
        """Generate rainbow colors for animations"""
        r = int(128 + 127 * math.sin(time_offset))
        g = int(128 + 127 * math.sin(time_offset + 2))
        b = int(128 + 127 * math.sin(time_offset + 4))
        return (r, g, b)