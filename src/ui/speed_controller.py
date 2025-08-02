import pygame
from typing import Callable, Optional
from src.core.constants import *

class GameSpeedController:
    """
    UI component for controlling game simulation speed.
    Displays a slider that allows adjusting time multiplier from 0.1x to 5.0x speed.
    """
    
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.Font(None, 20)
        self.small_font = pygame.font.Font(None, 16)
        
        # Position and size
        self.width = 200
        self.height = 50
        self.x = 10
        self.y = SCREEN_HEIGHT - self.height - 10
        
        # Speed control
        self.min_speed = 0.1
        self.max_speed = 5.0
        self.current_speed = 1.0
        self.paused = False
        
        # Slider components
        self.slider_rect = pygame.Rect(self.x + 50, self.y + 25, 120, 6)
        self.handle_size = 12
        self.handle_rect = pygame.Rect(0, 0, self.handle_size, self.handle_size)
        self._update_handle_position()
        
        # Visual settings
        self.background_color = (40, 40, 40, 200)
        self.slider_bg_color = (60, 60, 60)
        self.slider_fill_color = (100, 150, 255)
        self.handle_color = (150, 200, 255)
        self.text_color = WHITE
        self.pause_color = (255, 150, 150)
        
        # Interaction state
        self.dragging = False
        self.collapsed = False
        
        # Callbacks
        self.on_speed_change: Optional[Callable[[float], None]] = None
        self.on_pause_toggle: Optional[Callable[[bool], None]] = None
        
        # Predefined speed buttons
        self.speed_buttons = []
        self._create_speed_buttons()
    
    def _create_speed_buttons(self):
        """Create quick speed preset buttons"""
        speeds = [0.5, 1.0, 2.0, 3.0]
        button_width = 25
        button_height = 18
        start_x = self.x + 50
        start_y = self.y + 5
        
        self.speed_buttons = []
        for i, speed in enumerate(speeds):
            button_rect = pygame.Rect(
                start_x + i * (button_width + 2), 
                start_y, 
                button_width, 
                button_height
            )
            self.speed_buttons.append({
                'rect': button_rect,
                'speed': speed,
                'text': f"{speed}x"
            })
    
    def _update_handle_position(self):
        """Update handle position based on current speed"""
        # Convert speed to slider position (0.0 to 1.0)
        speed_ratio = (self.current_speed - self.min_speed) / (self.max_speed - self.min_speed)
        handle_x = self.slider_rect.x + (self.slider_rect.width - self.handle_size) * speed_ratio
        self.handle_rect.centerx = handle_x + self.handle_size // 2
        self.handle_rect.centery = self.slider_rect.centery
    
    def handle_event(self, event) -> bool:
        """Handle input events"""
        if self.collapsed:
            return False
        
        mouse_pos = pygame.mouse.get_pos()
        
        # Handle slider dragging
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.handle_rect.collidepoint(mouse_pos):
                self.dragging = True
                return True
            elif self.slider_rect.collidepoint(mouse_pos):
                # Click on slider track to jump to position
                self._handle_slider_click(mouse_pos[0])
                return True
            
            # Check speed preset buttons
            for button in self.speed_buttons:
                if button['rect'].collidepoint(mouse_pos):
                    self.set_speed(button['speed'])
                    return True
            
            # Check pause button
            pause_rect = pygame.Rect(self.x + 5, self.y + 5, 40, 18)
            if pause_rect.collidepoint(mouse_pos):
                self.toggle_pause()
                return True
        
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.dragging = False
        
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            self._handle_slider_drag(mouse_pos[0])
            return True
        
        # Keyboard shortcuts
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                self.toggle_pause()
                return True
            elif event.key == pygame.K_1:
                self.set_speed(0.5)
                return True
            elif event.key == pygame.K_2:
                self.set_speed(1.0)
                return True
            elif event.key == pygame.K_3:
                self.set_speed(2.0)
                return True
            elif event.key == pygame.K_4:
                self.set_speed(3.0)
                return True
            elif event.key == pygame.K_MINUS or event.key == pygame.K_KP_MINUS:
                self.adjust_speed(-0.1)
                return True
            elif event.key == pygame.K_PLUS or event.key == pygame.K_KP_PLUS or event.key == pygame.K_EQUALS:
                self.adjust_speed(0.1)
                return True
        
        return False
    
    def _handle_slider_click(self, mouse_x):
        """Handle clicking directly on slider track"""
        relative_x = mouse_x - self.slider_rect.x
        relative_x = max(0, min(relative_x, self.slider_rect.width))
        
        speed_ratio = relative_x / self.slider_rect.width
        new_speed = self.min_speed + speed_ratio * (self.max_speed - self.min_speed)
        self.set_speed(new_speed)
    
    def _handle_slider_drag(self, mouse_x):
        """Handle dragging the slider handle"""
        relative_x = mouse_x - self.slider_rect.x
        relative_x = max(0, min(relative_x, self.slider_rect.width))
        
        speed_ratio = relative_x / self.slider_rect.width
        new_speed = self.min_speed + speed_ratio * (self.max_speed - self.min_speed)
        self.set_speed(new_speed, notify=True)
    
    def set_speed(self, speed: float, notify: bool = True):
        """Set the game speed"""
        self.current_speed = max(self.min_speed, min(self.max_speed, speed))
        self._update_handle_position()
        
        if notify and self.on_speed_change:
            effective_speed = 0.0 if self.paused else self.current_speed
            self.on_speed_change(effective_speed)
    
    def adjust_speed(self, delta: float):
        """Adjust speed by delta amount"""
        self.set_speed(self.current_speed + delta)
    
    def toggle_pause(self):
        """Toggle pause state"""
        self.paused = not self.paused
        if self.on_pause_toggle:
            self.on_pause_toggle(self.paused)
        if self.on_speed_change:
            effective_speed = 0.0 if self.paused else self.current_speed
            self.on_speed_change(effective_speed)
    
    def get_effective_speed(self) -> float:
        """Get the effective speed (0 if paused)"""
        return 0.0 if self.paused else self.current_speed
    
    def update(self, dt):
        """Update animations"""
        pass
    
    def draw(self):
        """Draw the speed controller"""
        if self.collapsed:
            return
        
        # Draw semi-transparent background
        surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        surface.fill(self.background_color)
        self.screen.blit(surface, (self.x, self.y))
        
        # Draw border
        pygame.draw.rect(self.screen, (100, 100, 100), 
                        (self.x, self.y, self.width, self.height), 1, border_radius=5)
        
        # Draw pause button
        pause_rect = pygame.Rect(self.x + 5, self.y + 5, 40, 18)
        pause_color = self.pause_color if self.paused else (100, 255, 100)
        pygame.draw.rect(self.screen, pause_color, pause_rect, border_radius=3)
        pygame.draw.rect(self.screen, (80, 80, 80), pause_rect, 1, border_radius=3)
        
        pause_text = "PAUSE" if not self.paused else "PLAY"
        pause_surface = self.small_font.render(pause_text, True, (20, 20, 20))
        pause_text_rect = pause_surface.get_rect(center=pause_rect.center)
        self.screen.blit(pause_surface, pause_text_rect)
        
        # Draw speed preset buttons
        for button in self.speed_buttons:
            is_active = abs(button['speed'] - self.current_speed) < 0.05
            button_color = self.slider_fill_color if is_active else (80, 80, 80)
            
            pygame.draw.rect(self.screen, button_color, button['rect'], border_radius=2)
            pygame.draw.rect(self.screen, (60, 60, 60), button['rect'], 1, border_radius=2)
            
            text_color = WHITE if is_active else (150, 150, 150)
            button_surface = self.small_font.render(button['text'], True, text_color)
            button_text_rect = button_surface.get_rect(center=button['rect'].center)
            self.screen.blit(button_surface, button_text_rect)
        
        # Draw slider track
        pygame.draw.rect(self.screen, self.slider_bg_color, self.slider_rect, border_radius=3)
        
        # Draw slider fill (from start to handle)
        fill_width = self.handle_rect.centerx - self.slider_rect.x
        if fill_width > 0:
            fill_rect = pygame.Rect(self.slider_rect.x, self.slider_rect.y, fill_width, self.slider_rect.height)
            pygame.draw.rect(self.screen, self.slider_fill_color, fill_rect, border_radius=3)
        
        # Draw slider handle
        handle_color = self.handle_color if not self.dragging else (200, 220, 255)
        pygame.draw.circle(self.screen, handle_color, self.handle_rect.center, self.handle_size // 2)
        pygame.draw.circle(self.screen, (80, 80, 80), self.handle_rect.center, self.handle_size // 2, 1)
        
        # Draw current speed text
        speed_text = f"Speed: {self.current_speed:.1f}x"
        if self.paused:
            speed_text += " (PAUSED)"
        
        speed_surface = self.font.render(speed_text, True, self.text_color)
        speed_rect = speed_surface.get_rect()
        speed_rect.x = self.x + 5
        speed_rect.y = self.y + self.height - 20
        self.screen.blit(speed_surface, speed_rect)
        
        # Draw help text
        help_text = "Space: Pause | 1-4: Presets | +/-: Adjust"
        help_surface = self.small_font.render(help_text, True, (150, 150, 150))
        help_rect = help_surface.get_rect()
        help_rect.right = self.x + self.width - 5
        help_rect.y = self.y + self.height - 15
        self.screen.blit(help_surface, help_rect)