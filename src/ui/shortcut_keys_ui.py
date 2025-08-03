import pygame
from typing import Dict, List
from src.core.constants import *

class ShortcutKeysUI:
    """
    Transparent shortcut keys display box at the bottom of the screen.
    Shows available keyboard shortcuts to help players understand controls.
    """
    
    def __init__(self, screen):
        self.screen = screen
        
        # Fonts
        self.font_small = pygame.font.Font(None, 16)
        self.font_tiny = pygame.font.Font(None, 14)
        
        # Panel settings - transparent glass effect
        self.panel_color = (20, 20, 20, 120)  # Dark with transparency
        self.border_color = (100, 100, 100, 180)  # Light border
        self.text_color = (255, 255, 255)
        self.key_color = (255, 215, 0)  # Golden color for keys
        
        # Panel dimensions and position (draggable)
        self.panel_width = 600
        self.panel_height = 50
        self.x = (SCREEN_WIDTH - self.panel_width) // 2
        self.y = SCREEN_HEIGHT - self.panel_height - 10
        
        # Shortcut keys to display
        self.shortcuts = [
            ("WASD", "Move"),
            ("E", "Interact"),
            ("C", "Chat"),
            ("I", "Inventory"),
            ("M", "Map"),
            ("ESC", "Menu"),
            ("F12", "Debug"),
            ("Space", "Pause"),
        ]
        
        # Animation state
        self.visible = True
        self.alpha = 180
        self.fade_timer = 0
        self.auto_hide_delay = 10.0  # Hide after 10 seconds of no input
        
    def update(self, dt: float):
        """Update animation and auto-hide logic"""
        self.fade_timer += dt
        
        # Auto-hide after delay
        if self.fade_timer > self.auto_hide_delay and self.visible:
            self.alpha = max(0, self.alpha - 100 * dt)  # Fade out
        else:
            self.alpha = min(180, self.alpha + 200 * dt)  # Fade in
    
    def reset_fade_timer(self):
        """Reset the fade timer when user interacts"""
        self.fade_timer = 0
        self.visible = True
    
    def toggle_visibility(self):
        """Toggle shortcut keys visibility"""
        self.visible = not self.visible
        self.fade_timer = 0
    
    def draw(self):
        """Draw the transparent shortcut keys box"""
        if self.alpha <= 0:
            return
        
        # Create transparent surface
        panel_surface = pygame.Surface((self.panel_width, self.panel_height), pygame.SRCALPHA)
        
        # Draw background with transparency
        current_alpha = int(self.alpha)
        bg_color = (*self.panel_color[:3], current_alpha)
        border_color = (*self.border_color[:3], current_alpha)
        
        # Background rectangle with rounded corners
        panel_rect = pygame.Rect(0, 0, self.panel_width, self.panel_height)
        pygame.draw.rect(panel_surface, bg_color, panel_rect, border_radius=8)
        pygame.draw.rect(panel_surface, border_color, panel_rect, 2, border_radius=8)
        
        # Add subtle gradient highlight
        highlight_rect = pygame.Rect(2, 2, self.panel_width - 4, self.panel_height // 3)
        highlight_color = (255, 255, 255, current_alpha // 6)
        pygame.draw.rect(panel_surface, highlight_color, highlight_rect, border_radius=6)
        
        # Calculate spacing for shortcuts
        total_width = 0
        shortcut_surfaces = []
        
        for key, action in self.shortcuts:
            # Create key text with golden color
            key_text = self.font_small.render(key, True, self.key_color)
            # Create action text
            action_text = self.font_tiny.render(action, True, self.text_color)
            
            # Calculate width for this shortcut (key + separator + action + margin)
            shortcut_width = key_text.get_width() + 8 + action_text.get_width() + 20
            shortcut_surfaces.append((key_text, action_text, shortcut_width))
            total_width += shortcut_width
        
        # Start drawing shortcuts from center
        start_x = (self.panel_width - total_width) // 2
        current_x = start_x
        
        for key_text, action_text, shortcut_width in shortcut_surfaces:
            # Draw key in golden color
            key_rect = key_text.get_rect()
            key_rect.x = current_x
            key_rect.centery = self.panel_height // 2 - 3
            panel_surface.blit(key_text, key_rect)
            
            # Draw separator
            sep_x = current_x + key_text.get_width() + 3
            separator_color = (*self.text_color, current_alpha)
            sep_text = self.font_tiny.render(":", True, separator_color)
            sep_rect = sep_text.get_rect()
            sep_rect.x = sep_x
            sep_rect.centery = self.panel_height // 2
            panel_surface.blit(sep_text, sep_rect)
            
            # Draw action description
            action_rect = action_text.get_rect()
            action_rect.x = sep_x + 8
            action_rect.centery = self.panel_height // 2 + 2
            panel_surface.blit(action_text, action_rect)
            
            current_x += shortcut_width
        
        # Add small help text at the bottom
        if self.alpha > 100:  # Only show when fully visible
            help_text = "Press H to toggle this help"
            help_surface = self.font_tiny.render(help_text, True, (150, 150, 150))
            help_rect = help_surface.get_rect()
            help_rect.centerx = self.panel_width // 2
            help_rect.bottom = self.panel_height - 3
            panel_surface.blit(help_surface, help_rect)
        
        # Blit to main screen
        self.screen.blit(panel_surface, (self.x, self.y))
    
    def handle_event(self, event) -> bool:
        """Handle input events for shortcut keys UI"""
        if event.type == pygame.KEYDOWN:
            # Reset fade timer on any key press
            self.reset_fade_timer()
            
            # Toggle visibility with H key
            if event.key == pygame.K_h:
                self.toggle_visibility()
                return True
        
        elif event.type == pygame.MOUSEMOTION or event.type == pygame.MOUSEBUTTONDOWN:
            # Reset fade timer on mouse activity
            self.reset_fade_timer()
        
        return False
    
    def update_shortcuts(self, new_shortcuts: List[tuple]):
        """Update the displayed shortcuts"""
        self.shortcuts = new_shortcuts
        self.reset_fade_timer()