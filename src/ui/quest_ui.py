import pygame
import time
from typing import List, Optional
from src.core.constants import *
from src.systems.quest_system import QuestSystem, Quest, QuestObjective, QuestStatus, QuestType

class QuestUI:
    """
    UI system for displaying quests, objectives, and notifications
    """
    
    def __init__(self, screen, quest_system: QuestSystem):
        self.screen = screen
        self.quest_system = quest_system
        
        # UI State
        self.visible = False
        self.selected_quest = None
        
        # Layout
        self.panel_width = 500
        self.panel_height = 600
        self.panel_x = (SCREEN_WIDTH - self.panel_width) // 2
        self.panel_y = (SCREEN_HEIGHT - self.panel_height) // 2
        
        # Fonts
        self.font_title = pygame.font.Font(None, 28)
        self.font_normal = pygame.font.Font(None, 20)
        self.font_small = pygame.font.Font(None, 16)
        
        # Colors - Fixed to remove problematic alpha values
        self.bg_color = (25, 35, 45)  # Removed alpha
        self.panel_color = (45, 55, 65)
        self.text_color = (255, 255, 255)
        self.accent_color = (100, 150, 200)
        self.success_color = (100, 255, 100)
        self.warning_color = (255, 200, 100)
        self.border_color = (100, 120, 140)
        
        # Quest type colors
        self.quest_type_colors = {
            QuestType.TUTORIAL: (100, 255, 100),
            QuestType.STORY: (100, 150, 255),
            QuestType.SIDE: (255, 200, 100),
            QuestType.DAILY: (255, 150, 150),
            QuestType.ACHIEVEMENT: (200, 100, 255)
        }
        
        # Notification system
        self.notifications = []
        self.max_notifications = 5
        self.notification_duration = 4.0
        self.notification_fade_time = 1.0
        
        # Drag and drop
        self.is_dragging = False
        self.drag_offset = (0, 0)
        
        # Objective tracker (always visible)
        self.tracker_visible = True
        self.tracker_x = 20
        self.tracker_y = 200
        self.tracker_width = 350
        
    def show(self):
        """Show the quest log"""
        self.visible = True
        # Select first active quest if none selected
        if not self.selected_quest:
            active_quests = self.quest_system.get_active_quests()
            if active_quests:
                self.selected_quest = active_quests[0]
    
    def hide(self):
        """Hide the quest log"""
        self.visible = False
    
    def toggle(self):
        """Toggle quest log visibility"""
        if self.visible:
            self.hide()
        else:
            self.show()
    
    def toggle_tracker(self):
        """Toggle objective tracker visibility"""
        self.tracker_visible = not self.tracker_visible
    
    def handle_event(self, event) -> bool:
        """Handle UI events"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_q:
                self.toggle()
                return True
            elif event.key == pygame.K_j:
                self.toggle_tracker()
                return True
        
        # Check tracker close button even when quest log is not visible
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.tracker_visible:
                tracker_close_rect = self._get_tracker_close_button_rect()
                mouse_x, mouse_y = event.pos
                if tracker_close_rect.collidepoint(mouse_x, mouse_y):
                    self.toggle_tracker()
                    return True
        
        if not self.visible:
            return False
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                mouse_x, mouse_y = event.pos
                
                # Check if clicking on close button
                close_button_rect = self._get_close_button_rect()
                if close_button_rect.collidepoint(mouse_x, mouse_y):
                    self.hide()
                    return True
                
                # Check if clicking outside panel (close UI)
                panel_rect = pygame.Rect(self.panel_x, self.panel_y, self.panel_width, self.panel_height)
                if not panel_rect.collidepoint(mouse_x, mouse_y):
                    self.hide()
                    return True
                
                # Check if clicking on title bar for dragging
                title_bar_rect = pygame.Rect(self.panel_x, self.panel_y, self.panel_width, 40)
                if title_bar_rect.collidepoint(mouse_x, mouse_y):
                    self.is_dragging = True
                    self.drag_offset = (mouse_x - self.panel_x, mouse_y - self.panel_y)
                    return True
                
                # Check quest selection
                if self._handle_quest_selection(mouse_x, mouse_y):
                    return True
        
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1 and self.is_dragging:
                self.is_dragging = False
                return True
        
        elif event.type == pygame.MOUSEMOTION:
            if self.is_dragging:
                mouse_x, mouse_y = event.pos
                new_x = mouse_x - self.drag_offset[0]
                new_y = mouse_y - self.drag_offset[1]
                
                # Keep panel on screen
                self.panel_x = max(0, min(SCREEN_WIDTH - self.panel_width, new_x))
                self.panel_y = max(0, min(SCREEN_HEIGHT - self.panel_height, new_y))
                return True
        
        return True  # Consume all events when visible
    
    def _handle_quest_selection(self, mouse_x: int, mouse_y: int) -> bool:
        """Handle clicking on quest items"""
        quest_list_y = self.panel_y + 80
        quest_item_height = 60
        
        active_quests = self.quest_system.get_active_quests()
        
        for i, quest in enumerate(active_quests):
            item_y = quest_list_y + i * (quest_item_height + 5)
            item_rect = pygame.Rect(self.panel_x + 20, item_y, self.panel_width - 40, quest_item_height)
            
            if item_rect.collidepoint(mouse_x, mouse_y):
                self.selected_quest = quest
                return True
        
        return False
    
    def update(self, dt: float):
        """Update quest UI and notifications"""
        current_time = time.time()
        
        # Process quest notifications
        while self.quest_system.notification_queue:
            message = self.quest_system.notification_queue.pop(0)
            self.add_notification(message)
        
        # Update notifications
        self.notifications = [notif for notif in self.notifications 
                            if current_time - notif['start_time'] < self.notification_duration]
    
    def add_notification(self, message: str):
        """Add a quest notification"""
        notification = {
            'message': message,
            'start_time': time.time(),
            'y_offset': 0
        }
        
        self.notifications.append(notification)
        
        # Limit number of notifications
        if len(self.notifications) > self.max_notifications:
            self.notifications = self.notifications[-self.max_notifications:]
    
    def draw(self):
        """Draw the quest UI"""
        # Always draw objective tracker
        if self.tracker_visible:
            self._draw_objective_tracker()
        
        # Always draw notifications
        self._draw_notifications()
        
        # Draw main quest log if visible
        if self.visible:
            self._draw_quest_log()
    
    def _draw_quest_log(self):
        """Draw the main quest log panel"""
        # Main panel background - use safe colors without alpha
        panel_rect = pygame.Rect(self.panel_x, self.panel_y, self.panel_width, self.panel_height)
        
        try:
            # Create a safe surface for the background
            bg_surface = pygame.Surface((self.panel_width, self.panel_height))
            bg_surface.fill(self.bg_color)
            bg_surface.set_alpha(200)  # Set transparency safely
            
            self.screen.blit(bg_surface, (self.panel_x, self.panel_y))
            pygame.draw.rect(self.screen, self.border_color, panel_rect, 3)
        except Exception:
            # Fallback to simple drawing without transparency
            pygame.draw.rect(self.screen, (25, 35, 45), panel_rect)
            pygame.draw.rect(self.screen, self.border_color, panel_rect, 3)
        
        # Title bar
        title_surface = self.font_title.render("Quest Log", True, self.text_color)
        self.screen.blit(title_surface, (self.panel_x + 20, self.panel_y + 10))
        
        # Close button
        self._draw_close_button()
        
        # Progress summary
        progress_text = self.quest_system.get_quest_progress_summary()
        progress_surface = self.font_small.render(progress_text, True, self.accent_color)
        self.screen.blit(progress_surface, (self.panel_x + 20, self.panel_y + 45))
        
        # Instructions
        instructions = "Q: Toggle Log | J: Toggle Tracker | × Close | Click to select quest"
        inst_surface = self.font_small.render(instructions, True, (180, 180, 180))
        self.screen.blit(inst_surface, (self.panel_x + 20, self.panel_y + self.panel_height - 25))
        
        # Quest list
        self._draw_quest_list()
        
        # Quest details
        if self.selected_quest:
            self._draw_quest_details()
    
    def _draw_quest_list(self):
        """Draw the list of active quests"""
        list_y = self.panel_y + 80
        quest_item_height = 60
        
        active_quests = self.quest_system.get_active_quests()
        
        for i, quest in enumerate(active_quests):
            item_y = list_y + i * (quest_item_height + 5)
            is_selected = quest == self.selected_quest
            
            # Quest item background
            item_rect = pygame.Rect(self.panel_x + 20, item_y, 200, quest_item_height)
            item_color = self.accent_color if is_selected else self.panel_color
            pygame.draw.rect(self.screen, item_color, item_rect, border_radius=8)
            pygame.draw.rect(self.screen, self.border_color, item_rect, 2, border_radius=8)
            
            # Quest type indicator
            type_color = self.quest_type_colors.get(quest.type, self.text_color)
            type_indicator = pygame.Rect(self.panel_x + 15, item_y, 5, quest_item_height)
            pygame.draw.rect(self.screen, type_color, type_indicator, border_radius=2)
            
            # Quest title
            title_surface = self.font_normal.render(quest.title, True, self.text_color)
            self.screen.blit(title_surface, (self.panel_x + 30, item_y + 8))
            
            # Progress
            progress_text = quest.get_progress_text()
            progress_surface = self.font_small.render(progress_text, True, self.accent_color)
            self.screen.blit(progress_surface, (self.panel_x + 30, item_y + 30))
            
            # Quest type
            type_surface = self.font_small.render(quest.type.value.title(), True, type_color)
            self.screen.blit(type_surface, (self.panel_x + 30, item_y + 45))
    
    def _draw_quest_details(self):
        """Draw details of the selected quest"""
        if not self.selected_quest:
            return
        
        details_x = self.panel_x + 240
        details_y = self.panel_y + 80
        details_width = self.panel_width - 260
        
        quest = self.selected_quest
        
        # Quest title
        title_surface = self.font_title.render(quest.title, True, self.text_color)
        self.screen.blit(title_surface, (details_x, details_y))
        
        # Quest description
        desc_y = details_y + 35
        desc_lines = self._wrap_text(quest.description, details_width - 20, self.font_small)
        for i, line in enumerate(desc_lines):
            line_surface = self.font_small.render(line, True, (220, 220, 220))
            self.screen.blit(line_surface, (details_x, desc_y + i * 18))
        
        # Objectives
        obj_y = desc_y + len(desc_lines) * 18 + 20
        obj_title = self.font_normal.render("Objectives:", True, self.text_color)
        self.screen.blit(obj_title, (details_x, obj_y))
        
        for i, objective in enumerate(quest.objectives):
            obj_item_y = obj_y + 25 + i * 25
            
            # Objective status icon
            status_icon = "✓" if objective.completed else "○"
            status_color = self.success_color if objective.completed else self.text_color
            icon_surface = self.font_small.render(status_icon, True, status_color)
            self.screen.blit(icon_surface, (details_x, obj_item_y))
            
            # Objective text
            obj_text = f"{objective.description}"
            if objective.required_amount > 1:
                obj_text += f" ({objective.current_amount}/{objective.required_amount})"
            
            obj_surface = self.font_small.render(obj_text, True, self.text_color)
            self.screen.blit(obj_surface, (details_x + 20, obj_item_y))
        
        # Rewards
        rewards_y = obj_y + 25 + len(quest.objectives) * 25 + 20
        rewards_title = self.font_normal.render("Rewards:", True, self.text_color)
        self.screen.blit(rewards_title, (details_x, rewards_y))
        
        reward_y = rewards_y + 25
        if quest.rewards.xp > 0:
            xp_text = f"• {quest.rewards.xp} XP"
            xp_surface = self.font_small.render(xp_text, True, self.success_color)
            self.screen.blit(xp_surface, (details_x, reward_y))
            reward_y += 18
        
        if quest.rewards.money > 0:
            money_text = f"• {quest.rewards.money}g"
            money_surface = self.font_small.render(money_text, True, (255, 215, 0))
            self.screen.blit(money_surface, (details_x, reward_y))
            reward_y += 18
        
        for item_id, quantity in quest.rewards.items.items():
            item_text = f"• {quantity}x {item_id.replace('_', ' ').title()}"
            item_surface = self.font_small.render(item_text, True, self.accent_color)
            self.screen.blit(item_surface, (details_x, reward_y))
            reward_y += 18
    
    def _draw_objective_tracker(self):
        """Draw the always-visible objective tracker"""
        active_quests = self.quest_system.get_active_quests()
        if not active_quests:
            return
        
        # Calculate tracker height based on content (accounting for text wrapping)
        estimated_lines = 0
        for quest in active_quests[:3]:  # Show max 3 quests
            estimated_lines += 1  # Quest title
            for objective in quest.objectives:
                if not objective.completed:
                    # Estimate wrapped lines for objective text
                    obj_text = objective.description
                    if objective.required_amount > 1:
                        obj_text += f" ({objective.current_amount}/{objective.required_amount})"
                    max_width = self.tracker_width - 35
                    estimated_obj_lines = max(1, len(obj_text) // 40 + 1)  # Rough estimate
                    estimated_lines += estimated_obj_lines
        
        tracker_height = min(300, 40 + estimated_lines * 16)
        
        # Tracker background
        tracker_rect = pygame.Rect(self.tracker_x, self.tracker_y, self.tracker_width, tracker_height)
        pygame.draw.rect(self.screen, (20, 25, 35, 200), tracker_rect, border_radius=8)
        pygame.draw.rect(self.screen, (100, 120, 140, 150), tracker_rect, 2, border_radius=8)
        
        # Title
        title_surface = self.font_normal.render("Active Quests", True, self.text_color)
        self.screen.blit(title_surface, (self.tracker_x + 10, self.tracker_y + 10))
        
        # Small close button for tracker
        close_btn_size = 16
        close_btn_x = self.tracker_x + self.tracker_width - close_btn_size - 5
        close_btn_y = self.tracker_y + 5
        close_btn_rect = pygame.Rect(close_btn_x, close_btn_y, close_btn_size, close_btn_size)
        pygame.draw.rect(self.screen, (60, 60, 60), close_btn_rect, border_radius=3)
        pygame.draw.rect(self.screen, (100, 120, 140), close_btn_rect, 1, border_radius=3)
        
        # X symbol for tracker close
        x_surface = self.font_small.render("×", True, self.text_color)
        x_rect = x_surface.get_rect(center=close_btn_rect.center)
        self.screen.blit(x_surface, x_rect)
        
        # Quest objectives
        y_offset = self.tracker_y + 35
        
        for quest in active_quests[:3]:  # Show max 3 quests
            # Quest title
            quest_title = quest.title
            if len(quest_title) > 25:
                quest_title = quest_title[:22] + "..."
            
            title_color = self.quest_type_colors.get(quest.type, self.text_color)
            quest_surface = self.font_small.render(quest_title, True, title_color)
            self.screen.blit(quest_surface, (self.tracker_x + 10, y_offset))
            y_offset += 18
            
            # Active objectives
            for objective in quest.objectives:
                if not objective.completed:
                    obj_text = objective.description
                    
                    # Add progress counter if needed
                    if objective.required_amount > 1:
                        progress_text = f" ({objective.current_amount}/{objective.required_amount})"
                    else:
                        progress_text = ""
                    
                    # Wrap text to fit in tracker width
                    max_width = self.tracker_width - 35  # Account for bullet and margins
                    wrapped_lines = self._wrap_text(f"• {obj_text}{progress_text}", max_width, self.font_small)
                    
                    for line in wrapped_lines:
                        obj_surface = self.font_small.render(line, True, (200, 200, 200))
                        self.screen.blit(obj_surface, (self.tracker_x + 15, y_offset))
                        y_offset += 16
    
    def _draw_notifications(self):
        """Draw quest notifications"""
        current_time = time.time()
        notif_x = SCREEN_WIDTH - 350
        notif_y = 50
        
        for i, notification in enumerate(self.notifications):
            age = current_time - notification['start_time']
            
            # Calculate alpha for fade effect
            if age > self.notification_duration - self.notification_fade_time:
                fade_progress = (age - (self.notification_duration - self.notification_fade_time)) / self.notification_fade_time
                alpha = int(255 * (1 - fade_progress))
            else:
                alpha = 255
            
            # Notification background
            notif_rect = pygame.Rect(notif_x, notif_y + i * 45, 330, 35)
            notif_bg_color = (*self.panel_color[:3], min(alpha, 220))
            
            # Create surface with per-pixel alpha
            notif_surface = pygame.Surface((330, 35), pygame.SRCALPHA)
            pygame.draw.rect(notif_surface, notif_bg_color, (0, 0, 330, 35), border_radius=8)
            pygame.draw.rect(notif_surface, (*self.border_color[:3], alpha), (0, 0, 330, 35), 2, border_radius=8)
            
            self.screen.blit(notif_surface, (notif_x, notif_y + i * 45))
            
            # Notification text
            text_color = (*self.text_color[:3], alpha)
            text_surface = self.font_small.render(notification['message'], True, text_color)
            self.screen.blit(text_surface, (notif_x + 10, notif_y + i * 45 + 10))
    
    def _wrap_text(self, text: str, max_width: int, font: pygame.font.Font) -> List[str]:
        """Wrap text to fit within max_width"""
        words = text.split(' ')
        lines = []
        current_line = ""
        
        for word in words:
            test_line = current_line + (" " if current_line else "") + word
            if font.size(test_line)[0] <= max_width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word
        
        if current_line:
            lines.append(current_line)
        
        return lines
    
    def _draw_close_button(self):
        """Draw the close button in the top-right corner"""
        button_size = 24
        button_x = self.panel_x + self.panel_width - button_size - 10
        button_y = self.panel_y + 8
        
        # Button background
        button_rect = pygame.Rect(button_x, button_y, button_size, button_size)
        pygame.draw.rect(self.screen, (60, 60, 60), button_rect, border_radius=4)
        pygame.draw.rect(self.screen, self.border_color, button_rect, 2, border_radius=4)
        
        # X symbol
        x_surface = self.font_normal.render("×", True, self.text_color)
        x_rect = x_surface.get_rect(center=button_rect.center)
        self.screen.blit(x_surface, x_rect)
    
    def _get_close_button_rect(self):
        """Get the close button rectangle for click detection"""
        button_size = 24
        button_x = self.panel_x + self.panel_width - button_size - 10
        button_y = self.panel_y + 8
        return pygame.Rect(button_x, button_y, button_size, button_size)
    
    def _get_tracker_close_button_rect(self):
        """Get the tracker close button rectangle for click detection"""
        close_btn_size = 16
        close_btn_x = self.tracker_x + self.tracker_width - close_btn_size - 5
        close_btn_y = self.tracker_y + 5
        return pygame.Rect(close_btn_x, close_btn_y, close_btn_size, close_btn_size)