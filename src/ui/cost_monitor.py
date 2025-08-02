import pygame
from typing import Dict
from src.core.constants import *
from src.ai.token_counter import TokenCounter

class CostMonitor:
    """
    UI component to display real-time API costs and token usage.
    Shows session costs, daily totals, and provider breakdown.
    """
    
    def __init__(self, screen):
        self.screen = screen
        self.font_title = pygame.font.Font(None, 18)
        self.font_content = pygame.font.Font(None, 14)
        self.font_small = pygame.font.Font(None, 12)
        
        # Position in top right corner
        self.width = 220
        self.height = 120
        self.x = SCREEN_WIDTH - self.width - 10
        self.y = 10
        
        self.token_counter = TokenCounter()
        
        # Visual settings
        self.background_color = (20, 30, 40, 220)  # Semi-transparent dark
        self.border_color = (100, 150, 200)
        self.text_color = WHITE
        self.cost_color = (255, 200, 100)  # Orange for costs
        self.savings_color = (100, 255, 100)  # Green for savings
        self.warning_color = (255, 100, 100)  # Red for high costs
        
        self.collapsed = False
        self.collapse_button_rect = pygame.Rect(self.x + self.width - 20, self.y + 3, 15, 12)
        
        # Cost thresholds for warnings
        self.daily_warning_threshold = 1.0  # $1.00 per day
        self.session_warning_threshold = 0.10  # $0.10 per session
    
    def handle_event(self, event) -> bool:
        """Handle mouse events for collapse/expand"""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.collapse_button_rect.collidepoint(event.pos):
                self.collapsed = not self.collapsed
                return True
        return False
    
    def update(self, dt):
        """Update cost monitor (refresh stats)"""
        # Stats are updated in real-time by TokenCounter
        pass
    
    def draw(self):
        """Draw the cost monitor"""
        if self.collapsed:
            self._draw_collapsed()
        else:
            self._draw_expanded()
    
    def _draw_collapsed(self):
        """Draw collapsed version showing just session cost"""
        collapsed_height = 18
        collapsed_rect = pygame.Rect(self.x, self.y, self.width, collapsed_height)
        
        # Background
        surface = pygame.Surface((self.width, collapsed_height), pygame.SRCALPHA)
        surface.fill(self.background_color)
        self.screen.blit(surface, (collapsed_rect.x, collapsed_rect.y))
        
        # Border
        pygame.draw.rect(self.screen, self.border_color, collapsed_rect, 1, border_radius=3)
        
        # Session cost
        session_stats = self.token_counter.get_session_stats()
        cost_text = f"Session: ${session_stats['cost_usd']:.4f}"
        
        # Color based on cost
        cost_color = self.cost_color
        if session_stats['cost_usd'] > self.session_warning_threshold:
            cost_color = self.warning_color
        
        cost_surface = self.font_content.render(cost_text, True, cost_color)
        self.screen.blit(cost_surface, (collapsed_rect.x + 5, collapsed_rect.y + 2))
        
        # Expand button
        expand_text = self.font_small.render("▼", True, self.text_color)
        button_rect = pygame.Rect(collapsed_rect.x + self.width - 20, collapsed_rect.y + 3, 15, 12)
        self.collapse_button_rect = button_rect
        self.screen.blit(expand_text, (button_rect.x + 4, button_rect.y))
    
    def _draw_expanded(self):
        """Draw expanded version with detailed stats"""
        # Background
        surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        surface.fill(self.background_color)
        self.screen.blit(surface, (self.x, self.y))
        
        # Border
        pygame.draw.rect(self.screen, self.border_color, 
                        (self.x, self.y, self.width, self.height), 1, border_radius=5)
        
        # Title
        title_text = self.font_title.render("💰 API Costs", True, self.text_color)
        self.screen.blit(title_text, (self.x + 5, self.y + 3))
        
        # Collapse button
        collapse_text = self.font_small.render("▲", True, self.text_color)
        self.collapse_button_rect = pygame.Rect(self.x + self.width - 20, self.y + 3, 15, 12)
        self.screen.blit(collapse_text, (self.collapse_button_rect.x + 4, self.collapse_button_rect.y))
        
        # Get statistics
        session_stats = self.token_counter.get_session_stats()
        today_stats = self.token_counter.get_today_stats()
        total_stats = self.token_counter.get_total_stats()
        provider_breakdown = self.token_counter.get_cost_breakdown()
        
        y_offset = self.y + 20
        
        # Session stats
        session_color = self.cost_color
        if session_stats['cost_usd'] > self.session_warning_threshold:
            session_color = self.warning_color
        
        session_text = f"Session: ${session_stats['cost_usd']:.4f}"
        session_surface = self.font_content.render(session_text, True, session_color)
        self.screen.blit(session_surface, (self.x + 5, y_offset))
        
        tokens_text = f"({session_stats['tokens_used']} tokens)"
        tokens_surface = self.font_small.render(tokens_text, True, (180, 180, 180))
        self.screen.blit(tokens_surface, (self.x + 5, y_offset + 12))
        
        y_offset += 28
        
        # Today stats
        today_color = self.cost_color
        if today_stats['cost'] > self.daily_warning_threshold:
            today_color = self.warning_color
        
        today_text = f"Today: ${today_stats['cost']:.4f}"
        today_surface = self.font_content.render(today_text, True, today_color)
        self.screen.blit(today_surface, (self.x + 5, y_offset))
        
        today_tokens_text = f"({today_stats['tokens']} tokens)"
        today_tokens_surface = self.font_small.render(today_tokens_text, True, (180, 180, 180))
        self.screen.blit(today_tokens_surface, (self.x + 5, y_offset + 12))
        
        y_offset += 28
        
        # Provider breakdown
        provider_y = y_offset
        for provider, stats in provider_breakdown.items():
            if stats['cost'] > 0:
                provider_text = f"{provider.capitalize()}: ${stats['cost']:.4f}"
                provider_surface = self.font_small.render(provider_text, True, self.text_color)
                self.screen.blit(provider_surface, (self.x + 5, provider_y))
                provider_y += 14
        
        # Total all-time at bottom
        total_text = f"Total: ${total_stats['total_cost_usd']:.2f}"
        total_surface = self.font_small.render(total_text, True, (150, 150, 150))
        self.screen.blit(total_surface, (self.x + 5, self.y + self.height - 15))
        
        # Requests count
        requests_text = f"{session_stats['requests_made']} reqs"
        requests_surface = self.font_small.render(requests_text, True, (150, 150, 150))
        self.screen.blit(requests_surface, (self.x + self.width - 45, self.y + self.height - 15))
    
    def get_token_counter(self) -> TokenCounter:
        """Get the token counter instance"""
        return self.token_counter
    
    def reset_session(self):
        """Reset session statistics"""
        self.token_counter.reset_session_stats()
    
    def get_session_summary(self) -> str:
        """Get a text summary of session usage"""
        session_stats = self.token_counter.get_session_stats()
        return (f"Session: {session_stats['tokens_used']} tokens, "
                f"${session_stats['cost_usd']:.4f}, "
                f"{session_stats['requests_made']} requests")
    
    def is_over_budget(self, daily_budget: float = 1.0) -> bool:
        """Check if today's usage exceeds budget"""
        today_stats = self.token_counter.get_today_stats()
        return today_stats['cost'] > daily_budget