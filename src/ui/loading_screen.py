import pygame
import math
from src.core.constants import *

class LoadingScreen:
    """
    Beautiful loading screen that displays while assets are being loaded
    """
    
    def __init__(self, screen):
        self.screen = screen
        self.font_title = pygame.font.Font(None, 48)
        self.font_subtitle = pygame.font.Font(None, 24)
        self.font_small = pygame.font.Font(None, 18)
        
        # Animation state
        self.animation_time = 0.0
        self.progress = 0.0
        self.loading_text = "Loading Assets..."
        self.status_messages = []
        
        # Colors
        self.bg_color = (20, 25, 40)
        self.accent_color = (100, 150, 255)
        self.text_color = (255, 255, 255)
        self.progress_bg = (40, 50, 70)
        
    def update(self, dt):
        """Update loading screen animations"""
        self.animation_time += dt
        
    def set_progress(self, progress: float, message: str = ""):
        """Update loading progress (0.0 to 1.0)"""
        self.progress = max(0.0, min(1.0, progress))
        if message:
            self.status_messages.append(message)
            # Keep only last 5 messages
            if len(self.status_messages) > 5:
                self.status_messages.pop(0)
    
    def draw(self):
        """Draw the loading screen"""
        # Clear screen with gradient background
        self._draw_gradient_background()
        
        # Title
        title_text = self.font_title.render("AI Sims", True, self.text_color)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 120))
        self.screen.blit(title_text, title_rect)
        
        # Subtitle
        subtitle_text = self.font_subtitle.render("Life Simulation Game", True, (200, 200, 200))
        subtitle_rect = subtitle_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 90))
        self.screen.blit(subtitle_text, subtitle_rect)
        
        # Loading text with animation
        loading_dots = "." * (int(self.animation_time * 2) % 4)
        animated_loading_text = self.loading_text + loading_dots
        loading_surface = self.font_subtitle.render(animated_loading_text, True, self.accent_color)
        loading_rect = loading_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 20))
        self.screen.blit(loading_surface, loading_rect)
        
        # Progress bar
        self._draw_progress_bar()
        
        # Status messages
        self._draw_status_messages()
        
        # Animated loading indicator
        self._draw_loading_spinner()
    
    def _draw_gradient_background(self):
        """Draw a beautiful gradient background"""
        # Simple gradient effect
        for y in range(SCREEN_HEIGHT):
            color_factor = y / SCREEN_HEIGHT
            r = int(self.bg_color[0] * (1 - color_factor * 0.3))
            g = int(self.bg_color[1] * (1 - color_factor * 0.3))
            b = int(self.bg_color[2] * (1 + color_factor * 0.5))
            
            color = (max(0, min(255, r)), max(0, min(255, g)), max(0, min(255, b)))
            pygame.draw.line(self.screen, color, (0, y), (SCREEN_WIDTH, y))
    
    def _draw_progress_bar(self):
        """Draw the loading progress bar"""
        bar_width = 400
        bar_height = 20
        bar_x = (SCREEN_WIDTH - bar_width) // 2
        bar_y = SCREEN_HEIGHT // 2 + 20
        
        # Background
        bg_rect = pygame.Rect(bar_x, bar_y, bar_width, bar_height)
        pygame.draw.rect(self.screen, self.progress_bg, bg_rect, border_radius=10)
        pygame.draw.rect(self.screen, self.accent_color, bg_rect, 2, border_radius=10)
        
        # Progress fill
        if self.progress > 0:
            fill_width = int(bar_width * self.progress)
            fill_rect = pygame.Rect(bar_x, bar_y, fill_width, bar_height)
            pygame.draw.rect(self.screen, self.accent_color, fill_rect, border_radius=10)
            
            # Shine effect
            shine_rect = pygame.Rect(bar_x + 2, bar_y + 2, max(0, fill_width - 4), bar_height // 3)
            shine_color = tuple(min(255, c + 50) for c in self.accent_color) + (100,)
            pygame.draw.rect(self.screen, shine_color, shine_rect, border_radius=5)
        
        # Percentage text
        percentage_text = f"{int(self.progress * 100)}%"
        percentage_surface = self.font_small.render(percentage_text, True, self.text_color)
        percentage_rect = percentage_surface.get_rect(center=(SCREEN_WIDTH // 2, bar_y + bar_height + 20))
        self.screen.blit(percentage_surface, percentage_rect)
    
    def _draw_status_messages(self):
        """Draw status messages showing what's being loaded"""
        start_y = SCREEN_HEIGHT // 2 + 80
        
        for i, message in enumerate(self.status_messages[-3:]):  # Show last 3 messages
            alpha = 255 - (i * 60)  # Fade older messages
            alpha = max(100, alpha)
            
            # Create surface with alpha
            message_surface = self.font_small.render(message, True, (alpha, alpha, alpha))
            message_rect = message_surface.get_rect(center=(SCREEN_WIDTH // 2, start_y + i * 25))
            self.screen.blit(message_surface, message_rect)
    
    def _draw_loading_spinner(self):
        """Draw an animated loading spinner"""
        center_x = SCREEN_WIDTH // 2 + 220
        center_y = SCREEN_HEIGHT // 2 - 20
        radius = 15
        
        # Draw spinning circles
        for i in range(8):
            angle = (self.animation_time * 3 + i * math.pi / 4) % (2 * math.pi)
            x = center_x + math.cos(angle) * radius
            y = center_y + math.sin(angle) * radius
            
            # Size and alpha based on position
            size = int(3 + 2 * math.sin(angle + self.animation_time * 2))
            alpha = int(100 + 155 * (math.sin(angle) + 1) / 2)
            
            color = (*self.accent_color, alpha)
            pygame.draw.circle(self.screen, self.accent_color, (int(x), int(y)), size)