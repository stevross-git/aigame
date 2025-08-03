import pygame
import math
import time
from typing import Dict, List, Optional, Tuple
from src.core.constants import *

class UnifiedHUD:
    """
    Unified HUD system that consolidates multiple overlapping HUD elements
    into a clean, organized top-right interface
    """
    
    def __init__(self, screen):
        self.screen = screen
        
        # Layout configuration
        self.hud_width = 320
        self.hud_height = 180
        self.margin = 10
        self.x = SCREEN_WIDTH - self.hud_width - self.margin
        self.y = self.margin
        
        # Fonts
        self.font_large = pygame.font.Font(None, 24)
        self.font_normal = pygame.font.Font(None, 20)
        self.font_small = pygame.font.Font(None, 16)
        self.font_tiny = pygame.font.Font(None, 14)
        
        # Colors
        self.bg_color = (20, 25, 35, 220)
        self.panel_color = (40, 45, 55)
        self.accent_color = (100, 150, 255)
        self.text_color = (255, 255, 255)
        self.dim_text_color = (180, 180, 180)
        self.gold_color = (255, 215, 0)
        
        # State
        self.visible = True
        self.collapsed = False
        self.current_tab = 0  # 0: Player, 1: Stats, 2: Time
        self.tab_names = ["Player", "Stats", "Time"]
        
        # Data references (will be set by game)
        self.player = None
        self.xp_system = None
        self.time_system = None
        self.skill_system = None
        self.inventory_system = None
        
        # Animation
        self.animation_time = 0.0
        self.tab_switch_animation = 0.0
        
        # Compact mode for less screen space
        self.compact_mode = False
        
        # Drag and drop state
        self.is_dragging = False
        self.drag_start_pos = (0, 0)
        self.drag_offset = (0, 0)
        
    def set_data_sources(self, player=None, xp_system=None, time_system=None, 
                        skill_system=None, inventory_system=None):
        """Set data sources for the HUD"""
        self.player = player
        self.xp_system = xp_system
        self.time_system = time_system
        self.skill_system = skill_system
        self.inventory_system = inventory_system
    
    def handle_event(self, event) -> bool:
        """Handle input events"""
        if not self.visible:
            return False
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_F12:
                self.toggle_visibility()
                return True
            elif event.key == pygame.K_F11:
                self.toggle_compact()
                return True
            elif event.key == pygame.K_TAB and pygame.key.get_pressed()[pygame.K_LCTRL]:
                self.cycle_tab()
                return True
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                mouse_x, mouse_y = event.pos
                
                # Check if clicking on HUD area
                hud_rect = self.get_hud_rect()
                if hud_rect.collidepoint(mouse_x, mouse_y):
                    # Check tab buttons
                    if self._handle_tab_click(mouse_x, mouse_y):
                        return True
                    
                    # Check collapse button
                    if self._handle_collapse_click(mouse_x, mouse_y):
                        return True
                    
                    # Start dragging if clicking on title area or empty space
                    title_area_rect = pygame.Rect(self.x, self.y, self.hud_width, 30)
                    if title_area_rect.collidepoint(mouse_x, mouse_y):
                        self.is_dragging = True
                        self.drag_start_pos = (mouse_x, mouse_y)
                        self.drag_offset = (mouse_x - self.x, mouse_y - self.y)
                        return True
        
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1 and self.is_dragging:  # Left click release
                self.is_dragging = False
                return True
        
        elif event.type == pygame.MOUSEMOTION:
            if self.is_dragging:
                mouse_x, mouse_y = event.pos
                
                # Update HUD position
                new_x = mouse_x - self.drag_offset[0]
                new_y = mouse_y - self.drag_offset[1]
                
                # Keep HUD on screen
                self.x = max(0, min(SCREEN_WIDTH - self.hud_width, new_x))
                self.y = max(0, min(SCREEN_HEIGHT - self.hud_height, new_y))
                
                return True
        
        return False
    
    def get_hud_rect(self) -> pygame.Rect:
        """Get the main HUD rectangle"""
        height = 30 if self.collapsed else self.hud_height
        if self.compact_mode:
            height = int(height * 0.7)
        return pygame.Rect(self.x, self.y, self.hud_width, height)
    
    def _handle_tab_click(self, mouse_x: int, mouse_y: int) -> bool:
        """Handle clicking on tab buttons"""
        if self.collapsed:
            return False
        
        tab_width = 80
        tab_height = 25
        tab_y = self.y + 5
        
        for i, tab_name in enumerate(self.tab_names):
            tab_x = self.x + 10 + i * (tab_width + 5)
            tab_rect = pygame.Rect(tab_x, tab_y, tab_width, tab_height)
            
            if tab_rect.collidepoint(mouse_x, mouse_y):
                self.current_tab = i
                self.tab_switch_animation = 0.0
                return True
        
        return False
    
    def _handle_collapse_click(self, mouse_x: int, mouse_y: int) -> bool:
        """Handle clicking on collapse button"""
        button_size = 20
        button_x = self.x + self.hud_width - button_size - 5
        button_y = self.y + 5
        button_rect = pygame.Rect(button_x, button_y, button_size, button_size)
        
        if button_rect.collidepoint(mouse_x, mouse_y):
            self.collapsed = not self.collapsed
            return True
        
        return False
    
    def toggle_visibility(self):
        """Toggle HUD visibility"""
        self.visible = not self.visible
    
    def toggle_compact(self):
        """Toggle compact mode"""
        self.compact_mode = not self.compact_mode
    
    def cycle_tab(self):
        """Cycle through tabs"""
        self.current_tab = (self.current_tab + 1) % len(self.tab_names)
        self.tab_switch_animation = 0.0
    
    def update(self, dt: float):
        """Update animations"""
        self.animation_time += dt
        if self.tab_switch_animation < 1.0:
            self.tab_switch_animation += dt * 4  # Fast tab switch animation
    
    def draw(self):
        """Draw the unified HUD"""
        if not self.visible:
            return
        
        hud_rect = self.get_hud_rect()
        
        # Main background
        pygame.draw.rect(self.screen, self.bg_color, hud_rect, border_radius=12)
        pygame.draw.rect(self.screen, (100, 110, 130), hud_rect, 2, border_radius=12)
        
        if self.collapsed:
            self._draw_collapsed()
        else:
            self._draw_expanded(hud_rect)
    
    def _draw_collapsed(self):
        """Draw collapsed version with minimal info"""
        y_offset = self.y + 8
        
        # Essential info in one line
        if self.xp_system:
            progress = self.xp_system.get_xp_progress()
            level_text = f"Lv.{progress['level']}"
            if self.xp_system.prestige_level > 0:
                level_text += f" P{self.xp_system.prestige_level}"
            
            level_surface = self.font_small.render(level_text, True, self.gold_color)
            self.screen.blit(level_surface, (self.x + 10, y_offset))
        
        # Time
        if self.time_system:
            time_text = f"{self.time_system.get_time_string()}"
            time_surface = self.font_small.render(time_text, True, self.text_color)
            time_rect = time_surface.get_rect()
            time_rect.right = self.x + self.hud_width - 30
            time_rect.y = y_offset
            self.screen.blit(time_surface, time_rect)
        
        # Collapse button
        self._draw_collapse_button()
    
    def _draw_expanded(self, hud_rect: pygame.Rect):
        """Draw full expanded HUD"""
        # Tab buttons
        self._draw_tab_buttons()
        
        # Content area
        content_y = self.y + 35
        content_height = hud_rect.height - 40
        
        # Draw current tab content
        if self.current_tab == 0:
            self._draw_player_tab(content_y, content_height)
        elif self.current_tab == 1:
            self._draw_stats_tab(content_y, content_height)
        elif self.current_tab == 2:
            self._draw_time_tab(content_y, content_height)
        
        # Collapse button
        self._draw_collapse_button()
        
        # Draw drag indicator when being dragged
        if self.is_dragging:
            self._draw_drag_indicator(hud_rect)
    
    def _draw_tab_buttons(self):
        """Draw tab navigation buttons"""
        tab_width = 80
        tab_height = 25
        tab_y = self.y + 5
        
        for i, tab_name in enumerate(self.tab_names):
            tab_x = self.x + 10 + i * (tab_width + 5)
            tab_rect = pygame.Rect(tab_x, tab_y, tab_width, tab_height)
            
            # Tab background
            if i == self.current_tab:
                color = self.accent_color
                text_color = (255, 255, 255)
            else:
                color = self.panel_color
                text_color = self.dim_text_color
            
            pygame.draw.rect(self.screen, color, tab_rect, border_radius=5)
            pygame.draw.rect(self.screen, (150, 150, 150), tab_rect, 1, border_radius=5)
            
            # Tab text
            text_surface = self.font_tiny.render(tab_name, True, text_color)
            text_rect = text_surface.get_rect(center=tab_rect.center)
            self.screen.blit(text_surface, text_rect)
    
    def _draw_collapse_button(self):
        """Draw collapse/expand button"""
        button_size = 20
        button_x = self.x + self.hud_width - button_size - 5
        button_y = self.y + 5
        button_rect = pygame.Rect(button_x, button_y, button_size, button_size)
        
        pygame.draw.rect(self.screen, self.panel_color, button_rect, border_radius=3)
        pygame.draw.rect(self.screen, (150, 150, 150), button_rect, 1, border_radius=3)
        
        # Button icon
        icon = "−" if not self.collapsed else "+"
        icon_surface = self.font_small.render(icon, True, self.text_color)
        icon_rect = icon_surface.get_rect(center=button_rect.center)
        self.screen.blit(icon_surface, icon_rect)
    
    def _draw_player_tab(self, y: int, height: int):
        """Draw player information tab"""
        current_y = y + 5
        
        # XP and Level
        if self.xp_system:
            progress = self.xp_system.get_xp_progress()
            
            # Level display
            level_text = f"Level {progress['level']}"
            if self.xp_system.prestige_level > 0:
                level_text += f" (Prestige {self.xp_system.prestige_level})"
            
            level_surface = self.font_normal.render(level_text, True, self.gold_color)
            self.screen.blit(level_surface, (self.x + 15, current_y))
            current_y += 25
            
            # XP Bar
            bar_width = self.hud_width - 30
            bar_height = 12
            bar_x = self.x + 15
            bar_y = current_y
            
            self._draw_progress_bar(bar_x, bar_y, bar_width, bar_height,
                                  progress['progress_percent'] / 100, self.accent_color)
            
            # XP text
            xp_text = f"{progress['current_xp']:,} / {progress['xp_to_next']:,} XP"
            xp_surface = self.font_tiny.render(xp_text, True, self.dim_text_color)
            self.screen.blit(xp_surface, (bar_x, bar_y + bar_height + 2))
            current_y += 35
            
            # Skill points
            if progress['available_skill_points'] > 0:
                sp_text = f"🌟 {progress['available_skill_points']} Skill Points Available"
                sp_surface = self.font_tiny.render(sp_text, True, self.gold_color)
                self.screen.blit(sp_surface, (self.x + 15, current_y))
                current_y += 20
        
        # Player stats (compact)
        if self.player and hasattr(self, 'xp_system') and self.xp_system:
            stats = self.xp_system.get_total_stats()
            
            # Show key stats in two columns
            col1_stats = ["health", "stamina", "strength"]
            col2_stats = ["mana", "dexterity", "intelligence"]
            
            for i, stat in enumerate(col1_stats):
                if stat in stats:
                    stat_text = f"{stat.title()}: {stats[stat]}"
                    stat_surface = self.font_tiny.render(stat_text, True, self.text_color)
                    self.screen.blit(stat_surface, (self.x + 15, current_y + i * 15))
            
            for i, stat in enumerate(col2_stats):
                if stat in stats:
                    stat_text = f"{stat.title()}: {stats[stat]}"
                    stat_surface = self.font_tiny.render(stat_text, True, self.text_color)
                    self.screen.blit(stat_surface, (self.x + 165, current_y + i * 15))
    
    def _draw_stats_tab(self, y: int, height: int):
        """Draw statistics tab"""
        current_y = y + 5
        
        # Inventory summary
        if self.inventory_system:
            money = getattr(self.inventory_system, 'money', 0)
            money_text = f"💰 Gold: {money:,}g"
            money_surface = self.font_small.render(money_text, True, self.gold_color)
            self.screen.blit(money_surface, (self.x + 15, current_y))
            current_y += 20
            
            # Item count
            all_items = self.inventory_system.get_all_items()
            item_count = len(all_items)
            total_quantity = sum(item.quantity for item in all_items.values())
            
            items_text = f"📦 Items: {item_count} types, {total_quantity} total"
            items_surface = self.font_tiny.render(items_text, True, self.text_color)
            self.screen.blit(items_surface, (self.x + 15, current_y))
            current_y += 20
        
        # Skill levels (top 3)
        if self.skill_system:
            skills = [(skill_name, skill_data.level) for skill_name, skill_data in self.skill_system.skills.items()]
            skills.sort(key=lambda x: x[1], reverse=True)
            
            title_surface = self.font_small.render("Top Skills:", True, self.text_color)
            self.screen.blit(title_surface, (self.x + 15, current_y))
            current_y += 18
            
            for skill, level in skills[:3]:
                skill_text = f"• {skill.title()}: {level}"
                skill_surface = self.font_tiny.render(skill_text, True, self.dim_text_color)
                self.screen.blit(skill_surface, (self.x + 25, current_y))
                current_y += 15
        
        # XP category progress (top 3)
        if self.xp_system:
            current_y += 10
            title_surface = self.font_small.render("XP Progress:", True, self.text_color)
            self.screen.blit(title_surface, (self.x + 15, current_y))
            current_y += 18
            
            # Sort categories by current XP
            from src.systems.xp_system import XPCategory
            categories = [(cat, self.xp_system.category_xp[cat]) for cat in XPCategory]
            categories.sort(key=lambda x: x[1], reverse=True)
            
            for cat, xp in categories[:3]:
                level = self.xp_system.category_levels[cat]
                cat_text = f"• {cat.value.title()}: Lv.{level}"
                cat_surface = self.font_tiny.render(cat_text, True, self.dim_text_color)
                self.screen.blit(cat_surface, (self.x + 25, current_y))
                current_y += 15
    
    def _draw_time_tab(self, y: int, height: int):
        """Draw time and game info tab"""
        current_y = y + 5
        
        # Game time
        if self.time_system:
            # Current time
            time_text = f"🕐 {self.time_system.get_time_string()}"
            time_surface = self.font_normal.render(time_text, True, self.text_color)
            self.screen.blit(time_surface, (self.x + 15, current_y))
            current_y += 25
            
            # Date
            date_text = f"📅 {self.time_system.get_date_string()}"
            date_surface = self.font_small.render(date_text, True, self.dim_text_color)
            self.screen.blit(date_surface, (self.x + 15, current_y))
            current_y += 20
            
            # Season info
            season = self.time_system.get_season()
            day_of_season = self.time_system.get_day_of_season()
            season_text = f"🍂 {season} Day {day_of_season}"
            season_surface = self.font_tiny.render(season_text, True, self.dim_text_color)
            self.screen.blit(season_surface, (self.x + 15, current_y))
            current_y += 25
        
        # FPS (if available)
        import pygame
        clock = pygame.time.Clock()
        fps = clock.get_fps()
        if fps > 0:
            fps_text = f"⚡ FPS: {fps:.1f}"
            fps_color = (100, 255, 100) if fps >= 45 else (255, 200, 100) if fps >= 30 else (255, 100, 100)
            fps_surface = self.font_tiny.render(fps_text, True, fps_color)
            self.screen.blit(fps_surface, (self.x + 15, current_y))
            current_y += 18
        
        # Controls reminder
        current_y += 10
        controls_title = "Quick Controls:"
        controls_surface = self.font_tiny.render(controls_title, True, self.text_color)
        self.screen.blit(controls_surface, (self.x + 15, current_y))
        current_y += 15
        
        controls = [
            "F12: Toggle HUD",
            "F11: Compact Mode",
            "Ctrl+Tab: Switch Tab"
        ]
        
        for control in controls:
            control_surface = self.font_tiny.render(control, True, self.dim_text_color)
            self.screen.blit(control_surface, (self.x + 15, current_y))
            current_y += 12
    
    def _draw_progress_bar(self, x: int, y: int, width: int, height: int, 
                          progress: float, color: Tuple[int, int, int]):
        """Draw a progress bar"""
        # Background
        bg_rect = pygame.Rect(x, y, width, height)
        pygame.draw.rect(self.screen, (40, 40, 40), bg_rect, border_radius=height // 2)
        
        # Fill
        if progress > 0:
            fill_width = int(width * progress)
            fill_rect = pygame.Rect(x, y, fill_width, height)
            
            # Animated pulse effect
            pulse = abs(math.sin(self.animation_time * 2)) * 0.2 + 0.8
            animated_color = tuple(int(c * pulse) for c in color)
            
            pygame.draw.rect(self.screen, animated_color, fill_rect, border_radius=height // 2)
        
        # Border
        pygame.draw.rect(self.screen, (120, 120, 120), bg_rect, 1, border_radius=height // 2)
    
    def _draw_drag_indicator(self, hud_rect: pygame.Rect):
        """Draw visual indicator when HUD is being dragged"""
        # Draw a subtle highlight border
        highlight_color = (100, 150, 255, 100)
        pygame.draw.rect(self.screen, highlight_color, hud_rect, 3, border_radius=12)
        
        # Draw drag cursor icon in corner
        drag_icon = "✋"
        icon_surface = self.font_small.render(drag_icon, True, (255, 255, 255))
        icon_pos = (hud_rect.right - 25, hud_rect.top + 5)
        self.screen.blit(icon_surface, icon_pos)