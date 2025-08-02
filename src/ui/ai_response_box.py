import pygame
from typing import List, Optional
from src.core.constants import *

class AIResponseEntry:
    def __init__(self, npc_name: str, action: str, reasoning: str, dialogue: str = None):
        self.npc_name = npc_name
        self.action = action
        self.reasoning = reasoning
        self.dialogue = dialogue
        self.timestamp = pygame.time.get_ticks()
        self.alpha = 255  # For fade out effect
    
    def is_expired(self, current_time: int, lifetime: int = 15000) -> bool:
        """Check if response should be removed (15 seconds default)"""
        return current_time - self.timestamp > lifetime
    
    def update_alpha(self, current_time: int, lifetime: int = 15000, fade_duration: int = 3000):
        """Update alpha for fade out effect in last 3 seconds"""
        age = current_time - self.timestamp
        if age > lifetime - fade_duration:
            fade_progress = (age - (lifetime - fade_duration)) / fade_duration
            self.alpha = max(0, int(255 * (1 - fade_progress)))
        else:
            self.alpha = 255

class AIResponseBox:
    def __init__(self, screen):
        self.screen = screen
        self.font_title = pygame.font.Font(None, 20)
        self.font_content = pygame.font.Font(None, 16)
        self.font_small = pygame.font.Font(None, 14)
        
        # Box dimensions and position (bottom right)
        self.width = 350
        self.height = 200
        self.x = SCREEN_WIDTH - self.width - 10
        self.y = SCREEN_HEIGHT - self.height - 10
        
        # Response storage
        self.responses: List[AIResponseEntry] = []
        self.max_responses = 8
        
        # Visual settings
        self.background_color = (25, 35, 45, 200)  # Semi-transparent dark blue
        self.border_color = (100, 150, 200)
        self.text_color = WHITE
        self.action_colors = {
            'talk_to': (100, 255, 100),     # Green
            'move_to': (100, 150, 255),     # Blue  
            'eat': (255, 200, 100),         # Orange
            'rest': (200, 100, 255),        # Purple
            'work': (255, 255, 100),        # Yellow
            'play': (255, 150, 150),        # Pink
            'wander': (150, 150, 150),      # Gray
            'attend_event': (255, 100, 100) # Red
        }
        
        self.collapsed = False
        self.collapse_button_rect = pygame.Rect(self.x + self.width - 25, self.y + 5, 20, 15)
    
    def add_response(self, npc_name: str, action: str, reasoning: str, dialogue: str = None):
        """Add a new AI response to display"""
        # Remove oldest if at capacity
        if len(self.responses) >= self.max_responses:
            self.responses.pop(0)
        
        # Add new response
        entry = AIResponseEntry(npc_name, action, reasoning, dialogue)
        self.responses.append(entry)
        
        # Print to console as well for debugging
        print(f"🤖 {npc_name}: {action} - {reasoning}")
        if dialogue:
            print(f"   💬 \"{dialogue}\"")
    
    def handle_event(self, event) -> bool:
        """Handle mouse events for collapse/expand"""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.collapse_button_rect.collidepoint(event.pos):
                self.collapsed = not self.collapsed
                return True
        return False
    
    def update(self, dt):
        """Update response entries and remove expired ones"""
        current_time = pygame.time.get_ticks()
        
        # Update alpha for fade effect and remove expired entries
        self.responses = [
            response for response in self.responses 
            if not response.is_expired(current_time)
        ]
        
        # Update alpha for remaining responses
        for response in self.responses:
            response.update_alpha(current_time)
    
    def draw(self):
        """Draw the AI response box"""
        if self.collapsed:
            self._draw_collapsed()
        else:
            self._draw_expanded()
    
    def _draw_collapsed(self):
        """Draw collapsed version showing just title bar"""
        collapsed_height = 25
        collapsed_rect = pygame.Rect(self.x, self.y + self.height - collapsed_height, self.width, collapsed_height)
        
        # Background
        surface = pygame.Surface((self.width, collapsed_height), pygame.SRCALPHA)
        surface.fill(self.background_color)
        self.screen.blit(surface, (collapsed_rect.x, collapsed_rect.y))
        
        # Border
        pygame.draw.rect(self.screen, self.border_color, collapsed_rect, 2, border_radius=5)
        
        # Title
        title_text = self.font_title.render("AI Responses", True, self.text_color)
        self.screen.blit(title_text, (collapsed_rect.x + 10, collapsed_rect.y + 5))
        
        # Expand button
        expand_text = self.font_small.render("▲", True, self.text_color)
        button_rect = pygame.Rect(collapsed_rect.x + self.width - 25, collapsed_rect.y + 5, 20, 15)
        self.collapse_button_rect = button_rect
        self.screen.blit(expand_text, (button_rect.x + 6, button_rect.y))
    
    def _draw_expanded(self):
        """Draw expanded version with all responses"""
        # Background
        surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        surface.fill(self.background_color)
        self.screen.blit(surface, (self.x, self.y))
        
        # Border
        pygame.draw.rect(self.screen, self.border_color, 
                        (self.x, self.y, self.width, self.height), 2, border_radius=5)
        
        # Title bar
        title_text = self.font_title.render("AI Responses", True, self.text_color)
        self.screen.blit(title_text, (self.x + 10, self.y + 8))
        
        # Collapse button
        collapse_text = self.font_small.render("▼", True, self.text_color)
        self.collapse_button_rect = pygame.Rect(self.x + self.width - 25, self.y + 5, 20, 15)
        self.screen.blit(collapse_text, (self.collapse_button_rect.x + 6, self.collapse_button_rect.y))
        
        # Response count
        count_text = self.font_small.render(f"({len(self.responses)})", True, (150, 150, 150))
        self.screen.blit(count_text, (self.x + 110, self.y + 10))
        
        # Draw responses
        start_y = self.y + 30
        current_y = start_y
        
        # Create clipping area for scrolling
        content_rect = pygame.Rect(self.x + 5, start_y, self.width - 10, self.height - 35)
        self.screen.set_clip(content_rect)
        
        # Draw recent responses (newest first)
        for i, response in enumerate(reversed(self.responses[-6:])):  # Show last 6 responses
            if current_y > self.y + self.height - 10:
                break
                
            self._draw_response_entry(response, current_y)
            current_y += 30
        
        # Remove clipping
        self.screen.set_clip(None)
        
        # Draw scroll indicator if there are more responses
        if len(self.responses) > 6:
            scroll_text = self.font_small.render(f"...{len(self.responses) - 6} more", True, (100, 100, 100))
            self.screen.blit(scroll_text, (self.x + 10, self.y + self.height - 20))
    
    def _draw_response_entry(self, response: AIResponseEntry, y: int):
        """Draw a single response entry"""
        # Calculate fade alpha (0-255)
        alpha_ratio = response.alpha / 255.0
        
        # Apply alpha for fade effect by mixing with background color
        def fade_color(color, alpha_ratio):
            bg_color = (25, 35, 45)  # Background color
            return tuple(int(bg_color[i] + (color[i] - bg_color[i]) * alpha_ratio) for i in range(3))
        
        text_color = fade_color(self.text_color, alpha_ratio)
        
        # NPC name and action
        action_color = self.action_colors.get(response.action, self.text_color)
        action_color = fade_color(action_color, alpha_ratio)
        
        npc_text = self.font_content.render(f"{response.npc_name}:", True, text_color)
        action_text = self.font_content.render(response.action, True, action_color)
        
        self.screen.blit(npc_text, (self.x + 10, y))
        self.screen.blit(action_text, (self.x + 10 + npc_text.get_width() + 5, y))
        
        # Reasoning (truncated if too long)
        reasoning = response.reasoning
        if len(reasoning) > 45:
            reasoning = reasoning[:42] + "..."
        
        reasoning_color = fade_color((200, 200, 200), alpha_ratio)
        reasoning_text = self.font_small.render(reasoning, True, reasoning_color)
        self.screen.blit(reasoning_text, (self.x + 15, y + 15))
        
        # Dialogue if present
        if response.dialogue:
            dialogue = response.dialogue
            if len(dialogue) > 40:
                dialogue = dialogue[:37] + "..."
            
            dialogue_color = fade_color((150, 255, 150), alpha_ratio)
            dialogue_text = self.font_small.render(f'"{dialogue}"', True, dialogue_color)
            self.screen.blit(dialogue_text, (self.x + 15, y + 25))
    
    def clear_responses(self):
        """Clear all responses"""
        self.responses.clear()
    
    def get_response_count(self) -> int:
        """Get current number of responses"""
        return len(self.responses)