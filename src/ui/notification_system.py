import pygame
from typing import List
from src.core.constants import *

class Notification:
    """A single notification message"""
    def __init__(self, message: str, duration: float = 4.0):
        self.message = message
        self.duration = duration
        self.remaining_time = duration
        self.alpha = 255

class NotificationSystem:
    """
    System to display temporary notification messages to the user
    """
    
    def __init__(self, screen):
        self.screen = screen
        self.notifications: List[Notification] = []
        self.max_notifications = 3
        
        # Fonts
        self.font = pygame.font.Font(None, 20)
        
        # Colors
        self.bg_color = (20, 25, 35, 200)
        self.border_color = (100, 150, 200)
        self.text_color = (255, 255, 255)
        
        # Position - Center-left area where gameplay happens
        self.x = 600   # Center-left area of screen, closer to action
        self.y = 150   # A bit lower to avoid clock area
        self.width = 350  # Good readable width
        self.notification_height = 50
    
    def add_notification(self, message: str, duration: float = 4.0):
        """Add a new notification"""
        # Remove oldest if we're at max capacity
        if len(self.notifications) >= self.max_notifications:
            self.notifications.pop(0)
        
        notification = Notification(message, duration)
        self.notifications.append(notification)
    
    def update(self, dt):
        """Update notifications"""
        # Update timers and remove expired notifications
        self.notifications = [n for n in self.notifications if n.remaining_time > 0]
        
        for notification in self.notifications:
            notification.remaining_time -= dt
            
            # Fade out in last second
            if notification.remaining_time < 1.0:
                notification.alpha = int(255 * (notification.remaining_time / 1.0))
            else:
                notification.alpha = 255
    
    def draw(self):
        """Draw all notifications"""
        for i, notification in enumerate(self.notifications):
            y_pos = self.y + i * (self.notification_height + 10)
            
            # Skip if alpha is too low
            if notification.alpha < 50:
                continue
            
            # Draw background rectangle
            bg_rect = pygame.Rect(self.x, y_pos, self.width, self.notification_height)
            pygame.draw.rect(self.screen, (20, 25, 35), bg_rect, border_radius=8)
            pygame.draw.rect(self.screen, (100, 150, 200), bg_rect, 2, border_radius=8)
            
            # Text (wrap long messages)
            words = notification.message.split(' ')
            lines = []
            current_line = []
            max_width = self.width - 20
            
            for word in words:
                test_line = ' '.join(current_line + [word])
                if self.font.size(test_line)[0] <= max_width:
                    current_line.append(word)
                else:
                    if current_line:
                        lines.append(' '.join(current_line))
                        current_line = [word]
                    else:
                        lines.append(word)
            
            if current_line:
                lines.append(' '.join(current_line))
            
            # Draw text lines
            text_y = y_pos + 10
            line_height = 18
            for line in lines[:2]:  # Max 2 lines
                text_surface = self.font.render(line, True, self.text_color)
                self.screen.blit(text_surface, (self.x + 10, text_y))
                text_y += line_height
            
            # Draw progress bar
            progress = notification.remaining_time / notification.duration
            progress_width = int((self.width - 20) * progress)
            if progress_width > 0:
                progress_rect = pygame.Rect(self.x + 10, y_pos + self.notification_height - 8, progress_width, 4)
                pygame.draw.rect(self.screen, (100, 200, 100), progress_rect)
    
    def clear_all(self):
        """Clear all notifications"""
        self.notifications.clear()