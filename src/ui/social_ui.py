import pygame
from typing import Dict, List, Any, Optional
from src.systems.social_system import SocialSystem

class SocialUI:
    """
    UI component for displaying social system information and feedback
    """
    
    def __init__(self, screen, social_system: SocialSystem, player=None):
        self.screen = screen
        self.social_system = social_system
        self.player = player
        
        # Fonts
        self.font_normal = pygame.font.Font(None, 24)
        self.font_small = pygame.font.Font(None, 20)
        self.font_tiny = pygame.font.Font(None, 16)
        
        # Colors
        self.bg_color = (40, 45, 55, 220)
        self.text_color = (255, 255, 255)
        self.accent_color = (100, 200, 255)
        self.progress_bg = (60, 65, 75)
        self.progress_fill = (100, 200, 255)
        
        # UI State
        self.show_detailed_panel = False
        self.panel_x = 50
        self.panel_y = 50
        self.panel_width = 300
        self.panel_height = 200
        
        # Floating messages for feedback
        self.floating_messages = []
    
    def draw_social_status_bar(self, x: int, y: int):
        """Draw compact social status bar (always visible)"""
        if not self.social_system:
            return
        
        status = self.social_system.get_social_status()
        
        # Background
        bar_width = 200
        bar_height = 30
        bg_rect = pygame.Rect(x, y, bar_width, bar_height)
        pygame.draw.rect(self.screen, self.bg_color, bg_rect, border_radius=5)
        
        # Social level and progress
        level_text = f"Social Lv.{status['level']}"
        level_surface = self.font_small.render(level_text, True, self.text_color)
        self.screen.blit(level_surface, (x + 8, y + 4))
        
        # Progress bar
        progress_x = x + 80
        progress_y = y + 8
        progress_width = 110
        progress_height = 8
        
        # Background
        pygame.draw.rect(self.screen, self.progress_bg, 
                        (progress_x, progress_y, progress_width, progress_height), border_radius=4)
        
        # Fill
        fill_width = int((progress_width * status['progress_percentage']) / 100)
        if fill_width > 0:
            pygame.draw.rect(self.screen, self.progress_fill,
                           (progress_x, progress_y, fill_width, progress_height), border_radius=4)
        
        # Progress text
        progress_text = f"{status['total_points']}/{status['points_to_next_level']}"
        progress_surface = self.font_tiny.render(progress_text, True, self.text_color)
        text_rect = progress_surface.get_rect()
        text_rect.center = (progress_x + progress_width // 2, progress_y + progress_height // 2)
        self.screen.blit(progress_surface, text_rect)
    
    def draw_social_feedback(self):
        """Draw floating social feedback messages"""
        if not self.player or not hasattr(self.player, 'social_feedback_messages'):
            return
        
        y_offset = 100
        for feedback in self.player.social_feedback_messages:
            # Create text surface
            text_surface = self.font_small.render(feedback['message'], True, feedback['color'])
            
            # Add background
            text_rect = text_surface.get_rect()
            bg_rect = pygame.Rect(text_rect.x - 5, text_rect.y - 3, 
                                text_rect.width + 10, text_rect.height + 6)
            bg_rect.center = (self.screen.get_width() // 2, y_offset)
            
            # Semi-transparent background
            bg_surface = pygame.Surface((bg_rect.width, bg_rect.height), pygame.SRCALPHA)
            bg_surface.fill((0, 0, 0, 150))
            self.screen.blit(bg_surface, bg_rect)
            
            # Draw text
            text_rect.center = bg_rect.center
            self.screen.blit(text_surface, text_rect)
            
            y_offset += 30
    
    def draw_detailed_panel(self):
        """Draw detailed social information panel"""
        if not self.show_detailed_panel or not self.social_system:
            return
        
        status = self.social_system.get_social_status()
        
        # Panel background
        panel_rect = pygame.Rect(self.panel_x, self.panel_y, self.panel_width, self.panel_height)
        pygame.draw.rect(self.screen, self.bg_color, panel_rect, border_radius=10)
        pygame.draw.rect(self.screen, self.accent_color, panel_rect, 2, border_radius=10)
        
        # Title
        title_surface = self.font_normal.render("Social Status", True, self.text_color)
        self.screen.blit(title_surface, (self.panel_x + 10, self.panel_y + 10))
        
        y_pos = self.panel_y + 40
        
        # Level and experience
        level_text = f"Level: {status['level']}"
        level_surface = self.font_small.render(level_text, True, self.text_color)
        self.screen.blit(level_surface, (self.panel_x + 10, y_pos))
        y_pos += 25
        
        # Experience progress
        exp_text = f"Experience: {status['total_points']}/{status['points_to_next_level']}"
        exp_surface = self.font_small.render(exp_text, True, self.text_color)
        self.screen.blit(exp_surface, (self.panel_x + 10, y_pos))
        y_pos += 25
        
        # Progress bar
        bar_x = self.panel_x + 10
        bar_width = self.panel_width - 20
        bar_height = 12
        
        # Background
        pygame.draw.rect(self.screen, self.progress_bg, 
                        (bar_x, y_pos, bar_width, bar_height), border_radius=6)
        
        # Fill
        fill_width = int((bar_width * status['progress_percentage']) / 100)
        if fill_width > 0:
            pygame.draw.rect(self.screen, self.progress_fill,
                           (bar_x, y_pos, fill_width, bar_height), border_radius=6)
        
        y_pos += 30
        
        # Bonuses
        if status['bonuses']:
            bonus_title = self.font_small.render("Active Bonuses:", True, self.accent_color)
            self.screen.blit(bonus_title, (self.panel_x + 10, y_pos))
            y_pos += 20
            
            for interaction_type, multiplier in status['bonuses'].items():
                bonus_text = f"• {interaction_type.title()}: {multiplier:.1f}x"
                bonus_surface = self.font_tiny.render(bonus_text, True, self.text_color)
                self.screen.blit(bonus_surface, (self.panel_x + 20, y_pos))
                y_pos += 16
    
    def draw_npc_relationship_status(self, npc, x: int, y: int):
        """Draw relationship status for a specific NPC"""
        if not hasattr(npc, 'get_relationship_status') or not self.player:
            return
        
        relationship_info = npc.get_relationship_status(self.player.name)
        
        # Compact relationship display
        status_text = f"{npc.name}: {relationship_info['status']}"
        
        # Color based on relationship level
        if relationship_info['level'] >= 0.8:
            color = (100, 255, 100)  # Green for good relationships
        elif relationship_info['level'] >= 0.5:
            color = (255, 255, 100)  # Yellow for neutral
        elif relationship_info['level'] >= 0.2:
            color = (255, 200, 100)  # Orange for poor
        else:
            color = (255, 100, 100)  # Red for bad relationships
        
        status_surface = self.font_tiny.render(status_text, True, color)
        
        # Semi-transparent background
        bg_rect = status_surface.get_rect()
        bg_rect.x = x
        bg_rect.y = y
        bg_rect.width += 10
        bg_rect.height += 4
        
        bg_surface = pygame.Surface((bg_rect.width, bg_rect.height), pygame.SRCALPHA)
        bg_surface.fill((0, 0, 0, 120))
        self.screen.blit(bg_surface, bg_rect)
        
        # Draw text
        self.screen.blit(status_surface, (x + 5, y + 2))
    
    def draw_interaction_ratings_popup(self, npc, x: int, y: int):
        """Draw a popup showing recent interaction ratings with an NPC"""
        if not hasattr(npc, 'interaction_history') or not npc.interaction_history:
            return
        
        # Filter interactions with current player
        player_interactions = [
            h for h in npc.interaction_history[-5:]  # Last 5 interactions
            if self.player and h['player'] == self.player.name
        ]
        
        if not player_interactions:
            return
        
        # Calculate popup size
        popup_width = 250
        popup_height = 30 + len(player_interactions) * 20
        
        # Popup background
        popup_rect = pygame.Rect(x, y, popup_width, popup_height)
        pygame.draw.rect(self.screen, self.bg_color, popup_rect, border_radius=8)
        pygame.draw.rect(self.screen, self.accent_color, popup_rect, 2, border_radius=8)
        
        # Title
        title_text = f"Recent interactions with {npc.name}:"
        title_surface = self.font_tiny.render(title_text, True, self.text_color)
        self.screen.blit(title_surface, (x + 5, y + 5))
        
        # Interaction history
        y_pos = y + 25
        for interaction in player_interactions:
            rating = interaction['rating']
            
            # Color based on rating score
            if rating.final_score >= 8.0:
                color = (100, 255, 100)
            elif rating.final_score >= 6.0:
                color = (255, 255, 100)
            elif rating.final_score >= 4.0:
                color = (255, 200, 100)
            else:
                color = (255, 100, 100)
            
            # Interaction text
            interaction_text = f"• {interaction['type']}: {rating.final_score:.1f}/10 (+{rating.social_points_awarded} XP)"
            interaction_surface = self.font_tiny.render(interaction_text, True, color)
            self.screen.blit(interaction_surface, (x + 10, y_pos))
            
            y_pos += 18
    
    def handle_event(self, event):
        """Handle UI events"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_TAB:  # Toggle detailed panel
                self.show_detailed_panel = not self.show_detailed_panel
                return True
        
        return False
    
    def draw(self):
        """Draw all social UI elements"""
        # Always draw status bar in top-right corner
        status_bar_x = self.screen.get_width() - 220
        status_bar_y = 10
        self.draw_social_status_bar(status_bar_x, status_bar_y)
        
        # Draw floating feedback messages
        self.draw_social_feedback()
        
        # Draw detailed panel if enabled
        self.draw_detailed_panel()
    
    def draw_npc_info(self, npcs, camera=None):
        """Draw relationship info for visible NPCs"""
        if not self.player:
            return
        
        # Draw relationship status for nearby NPCs
        y_offset = 60
        for npc in npcs[:5]:  # Limit to 5 NPCs to avoid clutter
            # Get screen position
            if camera:
                screen_pos = camera.apply(npc)
            else:
                screen_pos = npc.rect
            
            # Draw relationship status above NPC
            self.draw_npc_relationship_status(npc, screen_pos.x, screen_pos.y - 20)