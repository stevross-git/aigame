import pygame
from typing import Dict
from src.core.constants import *

class CacheStatsDisplay:
    """
    Simple UI component to display AI cache performance statistics
    """
    
    def __init__(self, screen, x: int = 10, y: int = 10):
        self.screen = screen
        self.x = x
        self.y = y
        self.font = pygame.font.Font(None, 16)
        self.visible = False
        self.stats = {}
        
        # Colors
        self.bg_color = (0, 0, 0, 180)
        self.text_color = (200, 255, 200)
        self.header_color = (255, 255, 255)
    
    def toggle_visibility(self):
        """Toggle display visibility"""
        self.visible = not self.visible
    
    def update_stats(self, stats: Dict):
        """Update the cache statistics"""
        self.stats = stats
    
    def draw(self):
        """Draw the cache statistics display"""
        if not self.visible or not self.stats:
            return
        
        # Prepare text lines
        lines = [
            "AI Cache Stats:",
            f"Cache Size: {self.stats.get('cache_size', 0)}",
            f"Cache Hits: {self.stats.get('cache_hits', 0)}",
            f"Cache Misses: {self.stats.get('cache_misses', 0)}",
            f"Hit Rate: {self.stats.get('hit_rate', 0.0):.1%}",
            f"Predictions: {self.stats.get('predictions_made', 0)}",
            f"Background Requests: {self.stats.get('background_requests', 0)}",
            f"Invalidations: {self.stats.get('invalidations', 0)}",
            f"Queue Size: {self.stats.get('prediction_queue_size', 0)}"
        ]
        
        # Calculate display size
        line_height = 18
        max_width = max(self.font.size(line)[0] for line in lines) + 20
        total_height = len(lines) * line_height + 10
        
        # Draw background
        bg_surface = pygame.Surface((max_width, total_height), pygame.SRCALPHA)
        pygame.draw.rect(bg_surface, self.bg_color, (0, 0, max_width, total_height), border_radius=5)
        pygame.draw.rect(bg_surface, self.header_color, (0, 0, max_width, total_height), 2, border_radius=5)
        
        self.screen.blit(bg_surface, (self.x, self.y))
        
        # Draw text lines
        for i, line in enumerate(lines):
            color = self.header_color if i == 0 else self.text_color
            text_surface = self.font.render(line, True, color)
            text_y = self.y + 5 + i * line_height
            self.screen.blit(text_surface, (self.x + 10, text_y))
    
    def handle_event(self, event) -> bool:
        """Handle events (returns True if event was consumed)"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_F3:  # Toggle with F3
                self.toggle_visibility()
                return True
        return False