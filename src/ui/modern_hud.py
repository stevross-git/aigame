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
        
        # Draggable positions for panels
        self.player_panel_x = 12
        self.player_panel_y = SCREEN_HEIGHT - 120 - 12
        self.npc_panel_x = SCREEN_WIDTH - 220 - 15
        self.npc_panel_y = 15
        self.events_panel_x = (SCREEN_WIDTH - 300) // 2
        self.events_panel_y = 15
        
        # Stardew Valley-style panel settings
        self.panel_color = (45, 35, 25, 220)  # Warm brown, more opaque
        self.panel_border = (150, 120, 80, 255)  # Golden brown border
        self.panel_inner_border = (80, 65, 45, 200)  # Darker inner border
        self.glass_highlight = (255, 240, 200, 40)  # Warm highlight
        
        # Stardew Valley-inspired need bar colors
        self.need_colors = {
            "hunger": [(200, 50, 50), (220, 180, 50), (80, 180, 80)],    # Red to golden to green
            "sleep": [(100, 80, 180), (140, 120, 200), (180, 160, 220)], # Purple/blue gradient  
            "social": [(80, 150, 220), (120, 180, 240), (160, 200, 255)], # Blue gradient
            "fun": [(220, 160, 50), (240, 200, 80), (255, 220, 120)]     # Golden/yellow gradient
        }
        
        # Animation states
        self.need_bar_animations = {}
        
        # Performance optimization - cache scaled sprites
        self.scaled_sprite_cache = {}
        
        # Panel dimensions - more compact like Stardew Valley
        self.player_panel_width = 180
        self.player_panel_height = 120
        
        self.npc_panel_width = 220
        self.npc_panel_height = 300
        
        # Selected NPC for detailed view
        self.selected_npc = None
        
        # Settings
        self.show_debug = False
    
    def select_npc(self, npc):
        """Select an NPC to show in detailed panel"""
        self.selected_npc = npc
    
    def _draw_glass_panel(self, surface: pygame.Surface, rect: pygame.Rect, corner_radius: int = 8):
        """Draw a Stardew Valley-style panel with warm tones and proper borders"""
        
        # Try to use the custom UI panel sprite with caching
        ui_panel_sprite = self.assets.get_sprite("ui_panel")
        
        if ui_panel_sprite:
            # Use cached scaled panel
            cache_key = f"ui_panel_{rect.width}x{rect.height}"
            if cache_key not in self.scaled_sprite_cache:
                self.scaled_sprite_cache[cache_key] = pygame.transform.scale(ui_panel_sprite, (rect.width, rect.height))
            surface.blit(self.scaled_sprite_cache[cache_key], rect)
        else:
            # Create Stardew Valley-style panel
            panel_surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
            
            # Main panel background - warm brown
            pygame.draw.rect(panel_surface, self.panel_color, (0, 0, rect.width, rect.height), border_radius=corner_radius)
            
            # Inner dark border for depth
            inner_border_rect = pygame.Rect(2, 2, rect.width - 4, rect.height - 4)
            pygame.draw.rect(panel_surface, self.panel_inner_border, inner_border_rect, 1, border_radius=corner_radius-1)
            
            # Warm highlight on top-left edge
            highlight_rect = pygame.Rect(3, 3, rect.width - 6, rect.height // 5)
            pygame.draw.rect(panel_surface, self.glass_highlight, highlight_rect, border_radius=corner_radius - 2)
            
            # Golden border - outer
            pygame.draw.rect(panel_surface, self.panel_border, (0, 0, rect.width, rect.height), 2, border_radius=corner_radius)
            
            # Small decorative corners
            corner_size = 6
            corner_color = (200, 160, 100, 150)
            for corner_x, corner_y in [(4, 4), (rect.width-corner_size-4, 4), (4, rect.height-corner_size-4), (rect.width-corner_size-4, rect.height-corner_size-4)]:
                pygame.draw.rect(panel_surface, corner_color, (corner_x, corner_y, corner_size, corner_size), border_radius=2)
            
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
            # Use cached scaled background bar
            cache_key_bg = f"bar_{need_type}_bg_{width}x{height}"
            if cache_key_bg not in self.scaled_sprite_cache:
                self.scaled_sprite_cache[cache_key_bg] = pygame.transform.scale(bg_bar_sprite, (width, height))
            surface.blit(self.scaled_sprite_cache[cache_key_bg], (x, y))
            
            # Draw filled portion with caching
            if current_value > 0:
                fill_width = int(width * current_value)
                cache_key_fill = f"bar_{need_type}_fill_{fill_width}x{height}"
                if cache_key_fill not in self.scaled_sprite_cache:
                    self.scaled_sprite_cache[cache_key_fill] = pygame.transform.scale(fill_bar_sprite, (fill_width, height))
                surface.blit(self.scaled_sprite_cache[cache_key_fill], (x, y))
        else:
            # Stardew Valley-style need bar drawing
            bg_rect = pygame.Rect(x, y, width, height)
            
            # Background with warm brown tones
            pygame.draw.rect(surface, (35, 25, 15), bg_rect, border_radius=3)
            pygame.draw.rect(surface, (60, 45, 30), bg_rect, 1, border_radius=3)
            
            # Inner shadow for depth
            inner_shadow_rect = pygame.Rect(x + 1, y + 1, width - 2, height - 2)
            pygame.draw.rect(surface, (25, 20, 10), inner_shadow_rect, border_radius=2)
            
            # Filled portion
            if current_value > 0:
                fill_width = max(2, int(width * current_value))  # Minimum width for visibility
                fill_rect = pygame.Rect(x + 1, y + 1, fill_width - 2, height - 2)
                
                # Get color based on value with Stardew Valley palette
                colors = self.need_colors.get(need_type, [(200, 50, 50), (220, 180, 50), (80, 180, 80)])
                
                if current_value < 0.3:
                    color = colors[0]  # Low - warning color
                elif current_value < 0.7:
                    # Interpolate between low and medium
                    t = (current_value - 0.3) / 0.4
                    color = self._lerp_color(colors[0], colors[1], t)
                else:
                    # Interpolate between medium and high
                    t = (current_value - 0.7) / 0.3
                    color = self._lerp_color(colors[1], colors[2], t)
                
                pygame.draw.rect(surface, color, fill_rect, border_radius=2)
                
                # Add subtle highlight on top
                if fill_width > 4:
                    highlight_rect = pygame.Rect(x + 2, y + 1, max(0, fill_width - 4), 2)
                    highlight_color = tuple(min(255, c + 30) for c in color[:3])
                    pygame.draw.rect(surface, highlight_color, highlight_rect)
        
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
        """Draw the Stardew Valley-style player status panel"""
        # Panel position (use draggable positions)
        panel_x = self.player_panel_x
        panel_y = self.player_panel_y
        panel_rect = pygame.Rect(panel_x, panel_y, self.player_panel_width, self.player_panel_height)
        
        # Draw Stardew Valley-style panel background
        self._draw_glass_panel(self.screen, panel_rect)
        
        # Player name with golden color and shadow
        display_name = player.name if hasattr(player, 'name') and player.name else "Player"
        name_text = self.font_normal.render(display_name, True, (255, 240, 180))
        name_shadow = self.font_normal.render(display_name, True, (60, 45, 30))
        self.screen.blit(name_shadow, (panel_x + 13, panel_y + 9))
        self.screen.blit(name_text, (panel_x + 12, panel_y + 8))
        
        # Need bars with icons - more compact layout
        needs_start_y = panel_y + 28
        bar_height = 12
        bar_width = 100
        bar_spacing = 18
        
        need_names = ["hunger", "sleep", "social", "fun"]
        need_labels = ["Food", "Energy", "Social", "Fun"]
        
        for i, (need_name, label) in enumerate(zip(need_names, need_labels)):
            y_pos = needs_start_y + i * bar_spacing
            
            # Get need icon
            icon = self.assets.get_icon(need_name)
            
            # Draw icon with better positioning
            if icon:
                icon_rect = icon.get_rect()
                icon_rect.x = panel_x + 8
                icon_rect.centery = y_pos + bar_height // 2
                self.screen.blit(icon, icon_rect)
                bar_x = panel_x + 28
                label_x = panel_x + 28
            else:
                bar_x = panel_x + 12
                label_x = panel_x + 12
            
            # Need label with warm color
            label_text = self.font_small.render(label, True, (220, 200, 160))
            self.screen.blit(label_text, (label_x, y_pos - 1))
            
            # Draw need bar
            value = player.needs.get(need_name, 0.5)
            self._draw_animated_need_bar(self.screen, bar_x + 35, y_pos + 1, bar_width, bar_height, value, need_name)
            
            # Value percentage with better formatting
            percentage = int(value * 100)
            if percentage <= 20:
                value_color = (255, 100, 100)  # Red for low
            elif percentage <= 50:
                value_color = (255, 200, 100)  # Orange for medium
            else:
                value_color = (150, 255, 150)  # Green for good
                
            value_text = self.font_small.render(f"{percentage}%", True, value_color)
            value_rect = value_text.get_rect()
            value_rect.right = panel_x + self.player_panel_width - 8
            value_rect.centery = y_pos + bar_height // 2
            self.screen.blit(value_text, value_rect)
    
    def _draw_npc_panel(self, npcs: List):
        """Draw the beautiful NPC status panel"""
        if not npcs:
            return
        
        # Panel position (use draggable positions)
        panel_x = self.npc_panel_x
        panel_y = self.npc_panel_y
        panel_rect = pygame.Rect(panel_x, panel_y, self.npc_panel_width, self.npc_panel_height)
        
        # Draw glass panel background
        self._draw_glass_panel(self.screen, panel_rect)
        
        # Title - show selected NPC name if any
        if self.selected_npc:
            title_text = self.font_normal.render(f"NPCs - {self.selected_npc.name}", True, (255, 240, 180))
        else:
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
            # Get emotion from emotional_state if available
            emotion = None
            if hasattr(npc, 'emotional_state') and hasattr(npc.emotional_state, 'primary_emotion'):
                emotion = npc.emotional_state.primary_emotion.value
            elif hasattr(npc, 'emotion'):
                emotion = npc.emotion
            else:
                emotion = 'neutral'
            
            mood_color = self._get_mood_color(emotion)
            name_text = self.font_small.render(npc.name, True, mood_color)
            self.screen.blit(name_text, (panel_x + text_x_offset, y_pos))
            
            # NPC state/activity
            state_text = npc.state.replace('_', ' ').title()
            if hasattr(npc, 'current_dialogue') and npc.current_dialogue:
                state_text = "💬 Talking"
            
            activity_text = self.font_small.render(state_text, True, (180, 180, 180))
            self.screen.blit(activity_text, (panel_x + text_x_offset, y_pos + 14))
            
            # Mini mood indicator
            mood_indicator = self._get_mood_indicator(emotion)
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
        
        # Draw detailed info for selected NPC
        if self.selected_npc:
            self._draw_selected_npc_details(panel_x, start_y + len(npcs[:7]) * npc_height + 10)
    
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
    
    def _draw_selected_npc_details(self, panel_x: int, start_y: int):
        """Draw detailed information about the selected NPC"""
        npc = self.selected_npc
        if not npc:
            return
        
        # Details section header
        header_y = start_y + 5
        header_text = self.font_small.render("--- NPC Details ---", True, (200, 200, 200))
        header_rect = header_text.get_rect()
        header_rect.centerx = panel_x + self.npc_panel_width // 2
        header_rect.y = header_y
        self.screen.blit(header_text, header_rect)
        
        detail_y = header_y + 20
        
        # Current action/state
        state_text = f"Action: {npc.state.replace('_', ' ').title()}"
        state_surface = self.font_small.render(state_text, True, (180, 180, 180))
        self.screen.blit(state_surface, (panel_x + 15, detail_y))
        detail_y += 15
        
        # Show needs if available
        if hasattr(npc, 'needs'):
            needs_text = "Needs:"
            needs_surface = self.font_small.render(needs_text, True, (200, 200, 150))
            self.screen.blit(needs_surface, (panel_x + 15, detail_y))
            detail_y += 12
            
            for need_name, value in npc.needs.items():
                if value < 0.3:
                    color = (255, 150, 150)  # Red for low
                elif value < 0.7:
                    color = (255, 200, 150)  # Orange for medium
                else:
                    color = (150, 255, 150)  # Green for good
                
                need_text = f"  {need_name.title()}: {int(value * 100)}%"
                need_surface = self.font_small.render(need_text, True, color)
                self.screen.blit(need_surface, (panel_x + 20, detail_y))
                detail_y += 12
        
        # Relationship info (if available)
        detail_y += 5
        if hasattr(npc, 'relationships'):
            rel_text = "Relationships:"
            rel_surface = self.font_small.render(rel_text, True, (200, 200, 150))
            self.screen.blit(rel_surface, (panel_x + 15, detail_y))
            detail_y += 12
            
            # Show a few relationships
            rel_count = 0
            for other_name, value in npc.relationships.items():
                if rel_count >= 3:  # Limit to 3 relationships
                    break
                    
                if value > 0.7:
                    color = (150, 255, 150)  # Green for good
                    status = "Friend"
                elif value > 0.5:
                    color = (255, 255, 150)  # Yellow for neutral
                    status = "Acquaintance"
                else:
                    color = (255, 150, 150)  # Red for poor
                    status = "Stranger"
                
                rel_text = f"  {other_name}: {status}"
                rel_surface = self.font_small.render(rel_text, True, color)
                self.screen.blit(rel_surface, (panel_x + 20, detail_y))
                detail_y += 12
                rel_count += 1
        
        # Click instruction
        detail_y += 10
        instruction_text = "💡 Click NPC to interact"
        instruction_surface = self.font_small.render(instruction_text, True, (150, 200, 255))
        instruction_rect = instruction_surface.get_rect()
        instruction_rect.centerx = panel_x + self.npc_panel_width // 2
        instruction_rect.y = detail_y
        self.screen.blit(instruction_surface, instruction_rect)
        
        # Additional help text
        detail_y += 15
        help_text = "Press 'E' or 'C' for nearby NPCs"
        help_surface = self.font_small.render(help_text, True, (120, 120, 120))
        help_rect = help_surface.get_rect()
        help_rect.centerx = panel_x + self.npc_panel_width // 2
        help_rect.y = detail_y
        self.screen.blit(help_surface, help_rect)
    
    def _draw_events_panel(self, active_events: List):
        """Draw active events in a beautiful panel"""
        if not active_events:
            return
        
        # Small events panel (use draggable positions)
        panel_width = 300
        panel_height = 80
        panel_x = self.events_panel_x
        panel_y = self.events_panel_y
        
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