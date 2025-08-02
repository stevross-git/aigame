import pygame
import math
from typing import List, Optional
from src.core.constants import *
from src.graphics.custom_asset_manager import CustomAssetManager

class ModernHUD:
    """
    Beautiful modern HUD with glass panel aesthetic, need icons, and smooth animations.
    Inspired by Stardew Valley and modern life simulation games.
    """
    
    def __init__(self, screen):
        self.screen = screen
        self.assets = CustomAssetManager()
        
        # Fonts
        self.font_title = pygame.font.Font(None, 24)
        self.font_normal = pygame.font.Font(None, 18)
        self.font_small = pygame.font.Font(None, 16)
        
        # Panel settings
        self.panel_color = (20, 30, 40, 180)  # Semi-transparent dark blue
        self.panel_border = (100, 150, 200, 200)
        self.glass_highlight = (255, 255, 255, 30)
        
        # Need bar colors
        self.need_colors = {
            "hunger": [(255, 100, 100), (255, 200, 100), (100, 255, 100)],  # Red to yellow to green
            "sleep": [(150, 100, 255), (200, 150, 255), (255, 200, 255)],   # Purple gradient
            "social": [(100, 200, 255), (150, 220, 255), (200, 240, 255)], # Blue gradient
            "fun": [(255, 200, 100), (255, 230, 150), (255, 255, 200)]     # Yellow/gold gradient
        }
        
        # Animation states
        self.need_bar_animations = {}
        
        # Panel dimensions
        self.player_panel_width = 200
        self.player_panel_height = 140
        
        self.npc_panel_width = 220
        self.npc_panel_height = 300
        
        # Selected NPC for detailed view
        self.selected_npc = None
        
        # Settings
        self.show_debug = False
    
    def select_npc(self, npc):
        """Select an NPC to show in detailed panel"""
        self.selected_npc = npc
    
    def _draw_glass_panel(self, surface: pygame.Surface, rect: pygame.Rect, corner_radius: int = 10):
        """Draw a beautiful glass panel with transparency and highlights"""
        
        # Try to use the custom UI panel sprite
        ui_panel_sprite = self.assets.get_sprite("ui_panel")
        
        if ui_panel_sprite:
            # Scale the UI panel to fit the rect
            scaled_panel = pygame.transform.scale(ui_panel_sprite, (rect.width, rect.height))
            surface.blit(scaled_panel, rect)
        else:
            # Fallback to original glass panel drawing
            panel_surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
            
            # Main panel background
            pygame.draw.rect(panel_surface, self.panel_color, (0, 0, rect.width, rect.height), border_radius=corner_radius)
            
            # Glass highlight on top edge
            highlight_rect = pygame.Rect(2, 2, rect.width - 4, rect.height // 4)
            pygame.draw.rect(panel_surface, self.glass_highlight, highlight_rect, border_radius=corner_radius - 2)
            
            # Subtle border
            pygame.draw.rect(panel_surface, self.panel_border, (0, 0, rect.width, rect.height), 2, border_radius=corner_radius)
            
            # Blit to main surface
            surface.blit(panel_surface, rect)
    
    def _draw_animated_need_bar(self, surface: pygame.Surface, x: int, y: int, width: int, height: int, 
                               value: float, need_type: str, icon: pygame.Surface = None):
        """Draw an animated need bar with smooth color transitions using image-based bars"""
        
        # Initialize animation if not exists
        if need_type not in self.need_bar_animations:
            self.need_bar_animations[need_type] = {"current_value": value, "target_value": value}
        
        # Smooth animation towards target
        anim_data = self.need_bar_animations[need_type]
        anim_data["target_value"] = value
        
        # Lerp current value towards target
        diff = anim_data["target_value"] - anim_data["current_value"]
        anim_data["current_value"] += diff * 0.1  # Smooth animation speed
        
        current_value = anim_data["current_value"]
        
        # Try to use image-based progress bars
        bg_bar_sprite = self.assets.get_sprite(f"bar_{need_type}_bg")
        fill_bar_sprite = self.assets.get_sprite(f"bar_{need_type}")
        
        if bg_bar_sprite and fill_bar_sprite:
            # Scale background bar to fit
            bg_bar_scaled = pygame.transform.scale(bg_bar_sprite, (width, height))
            surface.blit(bg_bar_scaled, (x, y))
            
            # Draw filled portion
            if current_value > 0:
                fill_width = int(width * current_value)
                fill_bar_scaled = pygame.transform.scale(fill_bar_sprite, (fill_width, height))
                surface.blit(fill_bar_scaled, (x, y))
        else:
            # Fallback to original bar drawing
            bg_rect = pygame.Rect(x, y, width, height)
            pygame.draw.rect(surface, (40, 40, 40), bg_rect, border_radius=height // 2)
            pygame.draw.rect(surface, (80, 80, 80), bg_rect, 1, border_radius=height // 2)
            
            # Filled portion
            if current_value > 0:
                fill_width = int(width * current_value)
                fill_rect = pygame.Rect(x, y, fill_width, height)
                
                # Get color based on value
                colors = self.need_colors.get(need_type, [(255, 100, 100), (255, 200, 100), (100, 255, 100)])
                
                if current_value < 0.3:
                    color = colors[0]  # Low - red/warning color
                elif current_value < 0.7:
                    # Interpolate between low and medium
                    t = (current_value - 0.3) / 0.4
                    color = self._lerp_color(colors[0], colors[1], t)
                else:
                    # Interpolate between medium and high
                    t = (current_value - 0.7) / 0.3
                    color = self._lerp_color(colors[1], colors[2], t)
                
                pygame.draw.rect(surface, color, fill_rect, border_radius=height // 2)
                
                # Add shine effect
                shine_rect = pygame.Rect(x + 2, y + 1, max(0, fill_width - 4), height // 3)
                shine_color = tuple(min(255, c + 40) for c in color[:3]) + (100,)
                pygame.draw.rect(surface, shine_color, shine_rect, border_radius=height // 4)
        
        # Draw icon if provided
        if icon:
            icon_rect = icon.get_rect()
            icon_rect.centery = y + height // 2
            icon_rect.right = x - 8
            surface.blit(icon, icon_rect)
    
    def _lerp_color(self, color1: tuple, color2: tuple, t: float) -> tuple:
        """Linear interpolation between two colors"""
        t = max(0, min(1, t))
        return tuple(int(color1[i] + (color2[i] - color1[i]) * t) for i in range(3))
    
    def _draw_player_panel(self, player):
        """Draw the beautiful player status panel"""
        # Panel position (bottom-left)
        panel_x = 15
        panel_y = SCREEN_HEIGHT - self.player_panel_height - 15
        panel_rect = pygame.Rect(panel_x, panel_y, self.player_panel_width, self.player_panel_height)
        
        # Draw glass panel background
        self._draw_glass_panel(self.screen, panel_rect)
        
        # Player name
        name_text = self.font_normal.render(player.name, True, (255, 255, 255))
        self.screen.blit(name_text, (panel_x + 15, panel_y + 10))
        
        # Need bars with icons
        needs_start_y = panel_y + 35
        bar_height = 16
        bar_width = 120
        bar_spacing = 22
        
        need_names = ["hunger", "sleep", "social", "fun"]
        need_labels = ["Hunger", "Sleep", "Social", "Fun"]
        
        for i, (need_name, label) in enumerate(zip(need_names, need_labels)):
            y_pos = needs_start_y + i * bar_spacing
            
            # Get need icon
            icon = self.assets.get_icon(need_name)
            
            # Draw need bar
            bar_x = panel_x + 45
            value = player.needs.get(need_name, 0.5)
            self._draw_animated_need_bar(self.screen, bar_x, y_pos, bar_width, bar_height, value, need_name, icon)
            
            # Need label
            label_text = self.font_small.render(label, True, (200, 200, 200))
            self.screen.blit(label_text, (panel_x + 15, y_pos + 2))
            
            # Value text
            value_text = self.font_small.render(f"{value:.2f}", True, (180, 180, 180))
            value_rect = value_text.get_rect()
            value_rect.right = panel_x + self.player_panel_width - 15
            value_rect.centery = y_pos + bar_height // 2
            self.screen.blit(value_text, value_rect)
    
    def _draw_npc_panel(self, npcs: List):
        """Draw the beautiful NPC status panel"""
        if not npcs:
            return
        
        # Panel position (right side)
        panel_x = SCREEN_WIDTH - self.npc_panel_width - 15
        panel_y = 15
        panel_rect = pygame.Rect(panel_x, panel_y, self.npc_panel_width, self.npc_panel_height)
        
        # Draw glass panel background
        self._draw_glass_panel(self.screen, panel_rect)
        
        # Title
        title_text = self.font_normal.render("NPCs", True, (255, 255, 255))
        self.screen.blit(title_text, (panel_x + 15, panel_y + 10))
        
        # NPC list
        start_y = panel_y + 35
        npc_height = 35
        
        for i, npc in enumerate(npcs[:7]):  # Show max 7 NPCs
            y_pos = start_y + i * npc_height
            
            # NPC portrait
            portrait = self.assets.get_npc_portrait(npc.name)
            if portrait:
                portrait_rect = portrait.get_rect()
                portrait_rect.x = panel_x + 15
                portrait_rect.y = y_pos + 2
                self.screen.blit(portrait, portrait_rect)
                text_x_offset = 45  # Leave space for portrait
            else:
                text_x_offset = 15
            
            # NPC name with color coding for mood
            mood_color = self._get_mood_color(npc.emotion)
            name_text = self.font_small.render(npc.name, True, mood_color)
            self.screen.blit(name_text, (panel_x + text_x_offset, y_pos))
            
            # NPC state/activity
            state_text = npc.state.replace('_', ' ').title()
            if hasattr(npc, 'current_dialogue') and npc.current_dialogue:
                state_text = "💬 Talking"
            
            activity_text = self.font_small.render(state_text, True, (180, 180, 180))
            self.screen.blit(activity_text, (panel_x + text_x_offset, y_pos + 14))
            
            # Mini mood indicator
            mood_indicator = self._get_mood_indicator(npc.emotion)
            mood_surface = self.font_small.render(mood_indicator, True, mood_color)
            mood_rect = mood_surface.get_rect()
            mood_rect.right = panel_x + self.npc_panel_width - 15
            mood_rect.centery = y_pos + 7
            self.screen.blit(mood_surface, mood_rect)
            
            # Selection highlight
            if self.selected_npc == npc:
                highlight_rect = pygame.Rect(panel_x + 10, y_pos - 2, self.npc_panel_width - 20, npc_height - 5)
                pygame.draw.rect(self.screen, (100, 150, 200, 50), highlight_rect, border_radius=5)
                pygame.draw.rect(self.screen, (150, 200, 255), highlight_rect, 1, border_radius=5)
    
    def _get_mood_color(self, emotion: str) -> tuple:
        """Get color representing NPC mood"""
        mood_colors = {
            "happy": (100, 255, 100),
            "excited": (255, 200, 100),
            "sad": (150, 150, 255),
            "angry": (255, 100, 100),
            "neutral": (200, 200, 200),
            "curious": (200, 255, 200),
            "tired": (180, 150, 180)
        }
        return mood_colors.get(emotion, (200, 200, 200))
    
    def _get_mood_indicator(self, emotion: str) -> str:
        """Get emoji/symbol for mood"""
        mood_indicators = {
            "happy": "😊",
            "excited": "🎉",
            "sad": "😔",
            "angry": "😠",
            "neutral": "😐",
            "curious": "🤔",
            "tired": "😴"
        }
        return mood_indicators.get(emotion, "😐")
    
    def _draw_events_panel(self, active_events: List):
        """Draw active events in a beautiful panel"""
        if not active_events:
            return
        
        # Small events panel (top-center)
        panel_width = 300
        panel_height = 80
        panel_x = (SCREEN_WIDTH - panel_width) // 2
        panel_y = 15
        
        panel_rect = pygame.Rect(panel_x, panel_y, panel_width, panel_height)
        self._draw_glass_panel(self.screen, panel_rect)
        
        # Events title
        title_text = self.font_small.render("Active Events", True, (255, 255, 255))
        self.screen.blit(title_text, (panel_x + 15, panel_y + 8))
        
        # Event list
        event_y = panel_y + 25
        for i, event in enumerate(active_events[:2]):  # Show max 2 events
            if i > 0:
                event_y += 20
            
            # Event icon (simple colored circle)
            event_color = (255, 215, 0) if "gathering" in event.title.lower() else (100, 255, 100)
            pygame.draw.circle(self.screen, event_color, (panel_x + 20, event_y + 8), 6)
            
            # Event title
            event_text = self.font_small.render(event.title, True, (200, 255, 200))
            self.screen.blit(event_text, (panel_x + 35, event_y + 2))
            
            # Participant count
            if hasattr(event, 'participants') and event.participants:
                count_text = f"({len(event.participants)} attending)"
                count_surface = self.font_small.render(count_text, True, (150, 150, 150))
                self.screen.blit(count_surface, (panel_x + 35, event_y + 14))
    
    def draw(self, fps: float, ai_status: str, active_events: List, npcs: List, player):
        """Draw the complete modern HUD"""
        
        # Draw main panels
        self._draw_player_panel(player)
        self._draw_npc_panel(npcs)
        self._draw_events_panel(active_events)
        
        # Debug info if enabled
        if self.show_debug:
            self._draw_debug_info(fps, ai_status)
    
    def _draw_debug_info(self, fps: float, ai_status: str):
        """Draw debug information"""
        debug_y = SCREEN_HEIGHT - 60
        
        # FPS
        fps_text = self.font_small.render(f"FPS: {fps:.1f}", True, (255, 255, 0))
        self.screen.blit(fps_text, (15, debug_y))
        
        # AI Status
        ai_text = self.font_small.render(f"AI: {ai_status}", True, (100, 255, 100))
        self.screen.blit(ai_text, (15, debug_y + 15))
    
    def handle_event(self, event) -> bool:
        """Handle HUD-related events"""
        # Toggle debug info
        if event.type == pygame.KEYDOWN and event.key == pygame.K_F12:
            self.show_debug = not self.show_debug
            return True
        
        return False