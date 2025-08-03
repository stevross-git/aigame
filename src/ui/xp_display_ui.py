import pygame
import math
import time
from typing import Dict, List, Optional, Tuple
from src.core.constants import *
from src.systems.xp_system import XPSystem, XPCategory

class XPDisplayUI:
    """
    Comprehensive UI for displaying XP, levels, achievements, and progression
    """
    
    def __init__(self, screen, xp_system: XPSystem):
        self.screen = screen
        self.xp_system = xp_system
        
        # UI State
        self.visible = False
        self.current_tab = "overview"  # overview, categories, achievements, stats
        
        # Fonts
        self.font_large = pygame.font.Font(None, 36)
        self.font_normal = pygame.font.Font(None, 24)
        self.font_small = pygame.font.Font(None, 20)
        self.font_tiny = pygame.font.Font(None, 16)
        
        # Colors
        self.bg_color = (20, 25, 35, 240)
        self.panel_color = (40, 45, 55)
        self.accent_color = (100, 150, 255)
        self.gold_color = (255, 215, 0)
        self.text_color = (255, 255, 255)
        self.dim_text_color = (180, 180, 180)
        
        # Main panel
        self.panel_width = 700
        self.panel_height = 500
        self.panel_x = (SCREEN_WIDTH - self.panel_width) // 2
        self.panel_y = (SCREEN_HEIGHT - self.panel_height) // 2
        
        # Tab buttons
        self.tab_buttons = []
        self._create_tab_buttons()
        
        # Scroll states for different tabs
        self.scroll_offset = 0
        self.max_scroll = 0
        
        # Animation states
        self.animations = {
            'level_bar': 0.0,
            'category_bars': {},
            'achievement_unlock': []
        }
        
        # HUD elements (always visible)
        self.hud_visible = True
        self.hud_compact = False
        self.hud_x = 10
        self.hud_y = 10
        
        # Level up notification
        self.level_up_notification = None
        self.notification_timer = 0.0
    
    def _create_tab_buttons(self):
        """Create tab navigation buttons"""
        tabs = [
            ("Overview", "overview"),
            ("Categories", "categories"),
            ("Achievements", "achievements"),
            ("Stats", "stats")
        ]
        
        button_width = 150
        button_height = 40
        spacing = 10
        start_x = self.panel_x + (self.panel_width - (len(tabs) * button_width + (len(tabs) - 1) * spacing)) // 2
        
        for i, (label, tab_id) in enumerate(tabs):
            x = start_x + i * (button_width + spacing)
            y = self.panel_y + 50
            
            self.tab_buttons.append({
                'rect': pygame.Rect(x, y, button_width, button_height),
                'label': label,
                'tab_id': tab_id
            })
    
    def toggle(self):
        """Toggle the XP display panel"""
        self.visible = not self.visible
        if self.visible:
            self.scroll_offset = 0
    
    def show(self):
        """Show the XP display panel"""
        self.visible = True
        self.scroll_offset = 0
    
    def hide(self):
        """Hide the XP display panel"""
        self.visible = False
    
    def handle_event(self, event) -> bool:
        """Handle input events"""
        if not self.visible:
            # Handle HUD shortcuts even when panel is closed
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_x:
                    self.toggle()
                    return True
                elif event.key == pygame.K_h and pygame.key.get_pressed()[pygame.K_LCTRL]:
                    self.hud_visible = not self.hud_visible
                    return True
            return False
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE or event.key == pygame.K_x:
                self.hide()
                return True
            elif event.key == pygame.K_TAB:
                # Cycle through tabs
                self._cycle_tab()
                return True
            elif event.key == pygame.K_p and self.xp_system.current_level >= 50:
                # Prestige shortcut
                if self.xp_system.prestige():
                    self._show_prestige_notification()
                return True
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                mouse_x, mouse_y = event.pos
                
                # Check tab buttons
                for button in self.tab_buttons:
                    if button['rect'].collidepoint(mouse_x, mouse_y):
                        self.current_tab = button['tab_id']
                        self.scroll_offset = 0
                        return True
                
                # Check for panel click
                panel_rect = pygame.Rect(self.panel_x, self.panel_y, self.panel_width, self.panel_height)
                if not panel_rect.collidepoint(mouse_x, mouse_y):
                    self.hide()
                    return True
            
            elif event.button == 4:  # Scroll up
                self.scroll_offset = max(0, self.scroll_offset - 20)
                return True
            elif event.button == 5:  # Scroll down
                self.scroll_offset = min(self.max_scroll, self.scroll_offset + 20)
                return True
        
        return True
    
    def _cycle_tab(self):
        """Cycle through tabs"""
        tabs = ["overview", "categories", "achievements", "stats"]
        current_index = tabs.index(self.current_tab)
        self.current_tab = tabs[(current_index + 1) % len(tabs)]
        self.scroll_offset = 0
    
    def update(self, dt: float):
        """Update animations and notifications"""
        # Update animations
        self.animations['level_bar'] += dt * 2
        
        # Update level up notification
        if self.level_up_notification:
            self.notification_timer -= dt
            if self.notification_timer <= 0:
                self.level_up_notification = None
        
        # Check for new level ups
        progress = self.xp_system.get_xp_progress()
        if hasattr(self, '_last_level'):
            if progress['level'] > self._last_level:
                self._show_level_up_notification(progress['level'])
        self._last_level = progress['level']
    
    def _show_level_up_notification(self, new_level: int):
        """Show level up notification"""
        self.level_up_notification = {
            'level': new_level,
            'message': f"LEVEL {new_level} REACHED!",
            'rewards': []  # Would be populated with actual rewards
        }
        self.notification_timer = 5.0
    
    def _show_prestige_notification(self):
        """Show prestige notification"""
        self.level_up_notification = {
            'level': self.xp_system.prestige_level,
            'message': f"PRESTIGE LEVEL {self.xp_system.prestige_level}!",
            'rewards': ["Permanent XP bonus", "+1 Starting skill point", "+5% All stats"]
        }
        self.notification_timer = 8.0
    
    def draw(self):
        """Draw the XP display"""
        # Always draw HUD elements
        if self.hud_visible:
            self._draw_hud()
        
        # Draw level up notification
        if self.level_up_notification:
            self._draw_level_up_notification()
        
        # Draw main panel if visible
        if self.visible:
            self._draw_panel()
            self._draw_tabs()
            
            # Draw content based on current tab
            if self.current_tab == "overview":
                self._draw_overview()
            elif self.current_tab == "categories":
                self._draw_categories()
            elif self.current_tab == "achievements":
                self._draw_achievements()
            elif self.current_tab == "stats":
                self._draw_stats()
    
    def _draw_hud(self):
        """Draw HUD XP bar (always visible)"""
        progress = self.xp_system.get_xp_progress()
        
        # Background
        hud_width = 300 if not self.hud_compact else 200
        hud_height = 60 if not self.hud_compact else 40
        
        hud_rect = pygame.Rect(self.hud_x, self.hud_y, hud_width, hud_height)
        pygame.draw.rect(self.screen, (0, 0, 0, 180), hud_rect, border_radius=10)
        pygame.draw.rect(self.screen, (100, 100, 100), hud_rect, 2, border_radius=10)
        
        # Level indicator
        level_text = f"Lv.{progress['level']}"
        if self.xp_system.prestige_level > 0:
            level_text += f" P{self.xp_system.prestige_level}"
        
        level_surface = self.font_normal.render(level_text, True, self.gold_color)
        self.screen.blit(level_surface, (self.hud_x + 10, self.hud_y + 5))
        
        # XP bar
        bar_x = self.hud_x + 10
        bar_y = self.hud_y + 30
        bar_width = hud_width - 20
        bar_height = 20
        
        # Bar background
        bar_rect = pygame.Rect(bar_x, bar_y, bar_width, bar_height)
        pygame.draw.rect(self.screen, (50, 50, 50), bar_rect, border_radius=10)
        
        # Bar fill
        fill_width = int(bar_width * (progress['progress_percent'] / 100))
        if fill_width > 0:
            # Animated gradient effect
            pulse = abs(math.sin(self.animations['level_bar'])) * 0.3 + 0.7
            fill_color = (
                int(100 + 155 * pulse),
                int(150 + 105 * pulse),
                int(255)
            )
            
            fill_rect = pygame.Rect(bar_x, bar_y, fill_width, bar_height)
            pygame.draw.rect(self.screen, fill_color, fill_rect, border_radius=10)
            
            # Sparkle effect at the end of the bar
            if fill_width > 10:
                sparkle_x = bar_x + fill_width - 5
                sparkle_y = bar_y + bar_height // 2
                sparkle_radius = int(3 + 2 * pulse)
                pygame.draw.circle(self.screen, (255, 255, 255), (sparkle_x, sparkle_y), sparkle_radius)
        
        # Bar border
        pygame.draw.rect(self.screen, (150, 150, 150), bar_rect, 2, border_radius=10)
        
        # XP text
        xp_text = f"{progress['current_xp']}/{progress['xp_to_next']}"
        xp_surface = self.font_tiny.render(xp_text, True, (255, 255, 255))
        xp_rect = xp_surface.get_rect(center=(bar_x + bar_width // 2, bar_y + bar_height // 2))
        self.screen.blit(xp_surface, xp_rect)
        
        # Skill points indicator
        if progress['available_skill_points'] > 0:
            sp_text = f"🌟 {progress['available_skill_points']} SP"
            sp_surface = self.font_tiny.render(sp_text, True, (255, 215, 0))
            self.screen.blit(sp_surface, (self.hud_x + hud_width - 50, self.hud_y + 5))
    
    def _draw_panel(self):
        """Draw the main panel background"""
        panel_rect = pygame.Rect(self.panel_x, self.panel_y, self.panel_width, self.panel_height)
        pygame.draw.rect(self.screen, self.bg_color, panel_rect, border_radius=15)
        pygame.draw.rect(self.screen, (100, 100, 100), panel_rect, 3, border_radius=15)
        
        # Title
        title = "Experience & Progression"
        title_surface = self.font_large.render(title, True, self.gold_color)
        title_rect = title_surface.get_rect(centerx=self.panel_x + self.panel_width // 2, y=self.panel_y + 10)
        self.screen.blit(title_surface, title_rect)
    
    def _draw_tabs(self):
        """Draw tab buttons"""
        for button in self.tab_buttons:
            # Button background
            color = self.accent_color if button['tab_id'] == self.current_tab else self.panel_color
            pygame.draw.rect(self.screen, color, button['rect'], border_radius=5)
            pygame.draw.rect(self.screen, (150, 150, 150), button['rect'], 2, border_radius=5)
            
            # Button text
            text_color = (255, 255, 255) if button['tab_id'] == self.current_tab else self.dim_text_color
            text_surface = self.font_small.render(button['label'], True, text_color)
            text_rect = text_surface.get_rect(center=button['rect'].center)
            self.screen.blit(text_surface, text_rect)
    
    def _draw_overview(self):
        """Draw overview tab content"""
        content_y = self.panel_y + 110
        
        progress = self.xp_system.get_xp_progress()
        
        # Main level display
        level_section = pygame.Rect(self.panel_x + 20, content_y, self.panel_width - 40, 120)
        pygame.draw.rect(self.screen, self.panel_color, level_section, border_radius=10)
        
        # Large level number
        level_text = f"{progress['level']}"
        level_surface = pygame.font.Font(None, 72).render(level_text, True, self.gold_color)
        self.screen.blit(level_surface, (level_section.x + 30, level_section.y + 20))
        
        # Progress to next level
        prog_text = f"Progress to Level {progress['level'] + 1}"
        prog_surface = self.font_normal.render(prog_text, True, self.text_color)
        self.screen.blit(prog_surface, (level_section.x + 150, level_section.y + 20))
        
        # Large progress bar
        bar_x = level_section.x + 150
        bar_y = level_section.y + 50
        bar_width = level_section.width - 180
        bar_height = 30
        
        self._draw_progress_bar(bar_x, bar_y, bar_width, bar_height, 
                               progress['progress_percent'] / 100, self.accent_color)
        
        # XP numbers
        xp_text = f"{progress['current_xp']:,} / {progress['xp_to_next']:,} XP"
        xp_surface = self.font_small.render(xp_text, True, self.text_color)
        self.screen.blit(xp_surface, (bar_x, bar_y + bar_height + 5))
        
        # Quick stats
        content_y += 140
        
        # Prestige info
        if self.xp_system.prestige_level > 0:
            prestige_text = f"Prestige Level: {self.xp_system.prestige_level}"
            prestige_surface = self.font_normal.render(prestige_text, True, (200, 100, 255))
            self.screen.blit(prestige_surface, (self.panel_x + 30, content_y))
            content_y += 30
        
        # Available skill points
        if progress['available_skill_points'] > 0:
            sp_text = f"Available Skill Points: {progress['available_skill_points']}"
            sp_surface = self.font_normal.render(sp_text, True, (255, 215, 0))
            self.screen.blit(sp_surface, (self.panel_x + 30, content_y))
            content_y += 30
        
        # Recent XP gains
        content_y += 20
        recent_title = "Recent XP Gains"
        recent_surface = self.font_normal.render(recent_title, True, self.text_color)
        self.screen.blit(recent_surface, (self.panel_x + 30, content_y))
        content_y += 30
        
        # Show last 5 XP gains
        recent_gains = self.xp_system.xp_history[-5:] if self.xp_system.xp_history else []
        for gain in reversed(recent_gains):
            gain_text = f"+{gain['amount']} XP - {gain['category']} - {gain['source'][:30]}"
            color = self.xp_system._get_category_color(XPCategory(gain['category']))
            gain_surface = self.font_small.render(gain_text, True, color)
            self.screen.blit(gain_surface, (self.panel_x + 50, content_y))
            content_y += 25
    
    def _draw_categories(self):
        """Draw categories tab content"""
        content_y = self.panel_y + 110 - self.scroll_offset
        
        # Category progress bars
        for category in XPCategory:
            if content_y > self.panel_y + 100 and content_y < self.panel_y + self.panel_height - 50:
                self._draw_category_progress(category, content_y)
            content_y += 60
        
        # Update max scroll
        self.max_scroll = max(0, content_y - (self.panel_y + self.panel_height - 50))
    
    def _draw_category_progress(self, category: XPCategory, y: int):
        """Draw progress for a single category"""
        progress = self.xp_system.get_category_progress(category)
        color = self.xp_system._get_category_color(category)
        
        # Category name and level
        name_text = f"{category.value.title()} - Level {progress['level']}"
        name_surface = self.font_normal.render(name_text, True, color)
        self.screen.blit(name_surface, (self.panel_x + 30, y))
        
        # Progress bar
        bar_x = self.panel_x + 30
        bar_y = y + 25
        bar_width = self.panel_width - 60
        bar_height = 20
        
        self._draw_progress_bar(bar_x, bar_y, bar_width, bar_height,
                               progress['progress_percent'] / 100, color)
        
        # XP text
        if not progress['max_level_reached']:
            xp_text = f"{progress['current_xp']:,} / {progress['xp_to_next']:,} XP"
        else:
            xp_text = "MAX LEVEL"
        
        xp_surface = self.font_tiny.render(xp_text, True, self.dim_text_color)
        self.screen.blit(xp_surface, (bar_x + bar_width - 100, bar_y + 3))
    
    def _draw_achievements(self):
        """Draw achievements tab content"""
        content_y = self.panel_y + 110 - self.scroll_offset
        
        # Unlocked count
        unlocked = sum(1 for a in self.xp_system.achievements if a.unlocked)
        total = len(self.xp_system.achievements)
        
        count_text = f"Achievements: {unlocked}/{total}"
        count_surface = self.font_normal.render(count_text, True, self.text_color)
        self.screen.blit(count_surface, (self.panel_x + 30, content_y))
        content_y += 40
        
        # Achievement list
        for achievement in self.xp_system.achievements:
            if content_y > self.panel_y + 100 and content_y < self.panel_y + self.panel_height - 50:
                self._draw_achievement(achievement, content_y)
            content_y += 70
        
        # Update max scroll
        self.max_scroll = max(0, content_y - (self.panel_y + self.panel_height - 50))
    
    def _draw_achievement(self, achievement, y: int):
        """Draw a single achievement"""
        # Background
        bg_rect = pygame.Rect(self.panel_x + 20, y, self.panel_width - 40, 60)
        
        if achievement.unlocked:
            pygame.draw.rect(self.screen, (50, 80, 50), bg_rect, border_radius=5)
            border_color = (100, 255, 100)
        else:
            pygame.draw.rect(self.screen, (40, 40, 40), bg_rect, border_radius=5)
            border_color = (100, 100, 100)
        
        pygame.draw.rect(self.screen, border_color, bg_rect, 2, border_radius=5)
        
        # Icon
        icon_surface = self.font_large.render(achievement.icon, True, (255, 255, 255))
        self.screen.blit(icon_surface, (bg_rect.x + 10, bg_rect.y + 10))
        
        # Name
        name_color = self.text_color if achievement.unlocked else self.dim_text_color
        name_surface = self.font_normal.render(achievement.name, True, name_color)
        self.screen.blit(name_surface, (bg_rect.x + 60, bg_rect.y + 5))
        
        # Description
        desc_surface = self.font_tiny.render(achievement.description, True, self.dim_text_color)
        self.screen.blit(desc_surface, (bg_rect.x + 60, bg_rect.y + 25))
        
        # XP reward
        xp_text = f"+{achievement.xp_reward} XP"
        xp_color = self.gold_color if achievement.unlocked else (150, 150, 150)
        xp_surface = self.font_small.render(xp_text, True, xp_color)
        self.screen.blit(xp_surface, (bg_rect.right - 80, bg_rect.y + 20))
    
    def _draw_stats(self):
        """Draw stats tab content"""
        content_y = self.panel_y + 110
        
        stats = self.xp_system.get_total_stats()
        
        # Stats grid
        col1_x = self.panel_x + 50
        col2_x = self.panel_x + 250
        col3_x = self.panel_x + 450
        
        stat_items = list(stats.items())
        
        for i, (stat_name, value) in enumerate(stat_items):
            if i < 3:
                x = col1_x
                y = content_y + i * 40
            elif i < 6:
                x = col2_x
                y = content_y + (i - 3) * 40
            else:
                x = col3_x
                y = content_y + (i - 6) * 40
            
            # Stat icon and name
            icon = self._get_stat_icon(stat_name)
            text = f"{icon} {stat_name.title()}: {value}"
            
            # Color based on bonus
            base_value = self.xp_system.base_stats[stat_name]
            if value > base_value:
                color = (100, 255, 100)  # Green for boosted
            else:
                color = self.text_color
            
            stat_surface = self.font_normal.render(text, True, color)
            self.screen.blit(stat_surface, (x, y))
            
            # Show bonus if any
            bonus = self.xp_system.stat_bonuses[stat_name]
            if bonus > 0:
                bonus_text = f"(+{bonus})"
                bonus_surface = self.font_tiny.render(bonus_text, True, (100, 200, 100))
                self.screen.blit(bonus_surface, (x + 150, y + 5))
        
        # XP Statistics
        content_y += 150
        
        stats_title = "XP Statistics"
        title_surface = self.font_normal.render(stats_title, True, self.text_color)
        self.screen.blit(title_surface, (self.panel_x + 30, content_y))
        content_y += 30
        
        # Total XP earned
        total_text = f"Total XP Earned: {self.xp_system.total_xp:,}"
        total_surface = self.font_small.render(total_text, True, self.dim_text_color)
        self.screen.blit(total_surface, (self.panel_x + 50, content_y))
        content_y += 25
        
        # XP today
        from datetime import datetime
        today = datetime.now().strftime("%Y-%m-%d")
        today_xp = self.xp_system.daily_xp.get(today, 0)
        today_text = f"XP Today: {today_xp:,}"
        today_surface = self.font_small.render(today_text, True, self.dim_text_color)
        self.screen.blit(today_surface, (self.panel_x + 50, content_y))
        content_y += 25
        
        # Prestige button (if eligible)
        if self.xp_system.current_level >= 50:
            content_y += 20
            prestige_rect = pygame.Rect(self.panel_x + self.panel_width // 2 - 100, content_y, 200, 40)
            pygame.draw.rect(self.screen, (200, 100, 255), prestige_rect, border_radius=20)
            pygame.draw.rect(self.screen, (255, 255, 255), prestige_rect, 2, border_radius=20)
            
            prestige_text = "PRESTIGE (P key)"
            prestige_surface = self.font_normal.render(prestige_text, True, (255, 255, 255))
            text_rect = prestige_surface.get_rect(center=prestige_rect.center)
            self.screen.blit(prestige_surface, text_rect)
    
    def _get_stat_icon(self, stat_name: str) -> str:
        """Get icon for a stat"""
        icons = {
            "health": "❤️",
            "stamina": "⚡",
            "mana": "💎",
            "strength": "💪",
            "dexterity": "🏃",
            "intelligence": "🧠",
            "luck": "🍀"
        }
        return icons.get(stat_name, "◆")
    
    def _draw_progress_bar(self, x: int, y: int, width: int, height: int, 
                          progress: float, color: Tuple[int, int, int]):
        """Draw a progress bar"""
        # Background
        bg_rect = pygame.Rect(x, y, width, height)
        pygame.draw.rect(self.screen, (50, 50, 50), bg_rect, border_radius=height // 2)
        
        # Fill
        if progress > 0:
            fill_width = int(width * progress)
            fill_rect = pygame.Rect(x, y, fill_width, height)
            
            # Gradient effect
            for i in range(3):
                alpha = 255 - i * 50
                offset_color = tuple(min(255, c + i * 20) for c in color)
                offset_rect = pygame.Rect(x, y + i, fill_width, height - i * 2)
                pygame.draw.rect(self.screen, offset_color, offset_rect, border_radius=height // 2)
        
        # Border
        pygame.draw.rect(self.screen, (150, 150, 150), bg_rect, 2, border_radius=height // 2)
    
    def _draw_level_up_notification(self):
        """Draw level up notification"""
        if not self.level_up_notification:
            return
        
        # Notification position (center-top of screen)
        notif_width = 400
        notif_height = 150
        notif_x = (SCREEN_WIDTH - notif_width) // 2
        notif_y = 100
        
        # Pulsing effect
        pulse = abs(math.sin(time.time() * 3)) * 0.3 + 0.7
        
        # Background with glow
        for i in range(3):
            glow_rect = pygame.Rect(notif_x - i * 10, notif_y - i * 10, 
                                   notif_width + i * 20, notif_height + i * 20)
            glow_alpha = int(50 * pulse / (i + 1))
            glow_color = (255, 215, 0, glow_alpha)
            pygame.draw.rect(self.screen, glow_color[:3], glow_rect, border_radius=20)
        
        # Main background
        notif_rect = pygame.Rect(notif_x, notif_y, notif_width, notif_height)
        pygame.draw.rect(self.screen, (40, 40, 40, 240), notif_rect, border_radius=15)
        pygame.draw.rect(self.screen, (255, 215, 0), notif_rect, 3, border_radius=15)
        
        # Title
        title_surface = self.font_large.render(self.level_up_notification['message'], True, (255, 215, 0))
        title_rect = title_surface.get_rect(centerx=notif_x + notif_width // 2, y=notif_y + 20)
        self.screen.blit(title_surface, title_rect)
        
        # Rewards
        reward_y = notif_y + 70
        for reward in self.level_up_notification.get('rewards', []):
            reward_surface = self.font_small.render(f"• {reward}", True, (255, 255, 255))
            self.screen.blit(reward_surface, (notif_x + 30, reward_y))
            reward_y += 25