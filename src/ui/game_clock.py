import pygame
import math
from typing import Dict
from src.core.constants import *
from src.graphics.custom_asset_manager import CustomAssetManager

class GameClock:
    """
    Beautiful game clock display showing comprehensive time information
    """
    
    def __init__(self, screen):
        self.screen = screen
        self.assets = CustomAssetManager()
        
        # Fonts
        self.font_time = pygame.font.Font(None, 32)
        self.font_date = pygame.font.Font(None, 20)
        self.font_small = pygame.font.Font(None, 16)
        
        # Clock position (top center)
        self.clock_width = 280
        self.clock_height = 80
        self.clock_x = (SCREEN_WIDTH - self.clock_width) // 2
        self.clock_y = 10
        
        # Animation
        self.animation_time = 0.0
        
        # Colors
        self.bg_color = (20, 30, 45, 180)
        self.border_color = (100, 150, 200, 200)
        self.text_color = (255, 255, 255)
        
        # Season icons/symbols
        self.season_symbols = {
            "Spring": "🌸",
            "Summer": "☀️", 
            "Fall": "🍂",
            "Winter": "❄️"
        }
        
        # Time period symbols
        self.time_period_symbols = {
            "Dawn": "🌅",
            "Morning": "🌞",
            "Afternoon": "☀️",
            "Evening": "🌆",
            "Night": "🌙",
            "Late Night": "⭐"
        }
    
    def update(self, dt: float):
        """Update clock animations"""
        self.animation_time += dt
    
    def draw(self, game_time):
        """Draw the game clock with all time information"""
        time_info = game_time.get_time_info()
        
        # Draw main clock panel
        self._draw_clock_panel(time_info)
        
        # Draw time and date information
        self._draw_time_info(time_info)
        
        # Draw season and time period indicators
        self._draw_period_indicators(time_info)
        
        # Draw mini progress bars
        self._draw_progress_indicators(game_time)
    
    def _draw_clock_panel(self, time_info: Dict):
        """Draw the main clock background panel"""
        # Create panel with seasonal color accent
        panel_surface = pygame.Surface((self.clock_width, self.clock_height), pygame.SRCALPHA)
        
        # Main background
        pygame.draw.rect(panel_surface, self.bg_color, 
                        (0, 0, self.clock_width, self.clock_height), border_radius=12)
        
        # Seasonal accent border
        season_color = time_info['season_color']
        border_color = (*season_color, 150)
        pygame.draw.rect(panel_surface, border_color, 
                        (0, 0, self.clock_width, self.clock_height), 3, border_radius=12)
        
        # Glass highlight effect
        highlight_color = (255, 255, 255, 30)
        highlight_rect = pygame.Rect(2, 2, self.clock_width - 4, self.clock_height // 3)
        pygame.draw.rect(panel_surface, highlight_color, highlight_rect, border_radius=10)
        
        # Subtle pulsing effect based on time
        pulse = math.sin(self.animation_time * 2) * 10 + 20
        glow_color = (*time_info['time_period_color'], int(pulse))
        glow_surface = pygame.Surface((self.clock_width + 6, self.clock_height + 6), pygame.SRCALPHA)
        pygame.draw.rect(glow_surface, glow_color, 
                        (0, 0, self.clock_width + 6, self.clock_height + 6), border_radius=15)
        
        # Blit glow first, then panel
        glow_rect = glow_surface.get_rect(center=(self.clock_x + self.clock_width // 2, 
                                                 self.clock_y + self.clock_height // 2))
        self.screen.blit(glow_surface, glow_rect)
        self.screen.blit(panel_surface, (self.clock_x, self.clock_y))
    
    def _draw_time_info(self, time_info: Dict):
        """Draw main time and date information"""
        # Main time display (larger)
        time_text = self.font_time.render(time_info['time'], True, self.text_color)
        time_rect = time_text.get_rect(center=(self.clock_x + self.clock_width // 2, 
                                              self.clock_y + 20))
        self.screen.blit(time_text, time_rect)
        
        # Date information (day name and date)
        date_str = f"{time_info['day_name']}, Day {time_info['day']}"
        date_text = self.font_date.render(date_str, True, (200, 200, 200))
        date_rect = date_text.get_rect(center=(self.clock_x + self.clock_width // 2, 
                                              self.clock_y + 45))
        self.screen.blit(date_text, date_rect)
        
        # Extended date info (week, month, year)
        extended_str = f"Week {time_info['week']} • {time_info['month_name']} • Year {time_info['year']}"
        extended_text = self.font_small.render(extended_str, True, (180, 180, 180))
        extended_rect = extended_text.get_rect(center=(self.clock_x + self.clock_width // 2, 
                                                      self.clock_y + 62))
        self.screen.blit(extended_text, extended_rect)
    
    def _draw_period_indicators(self, time_info: Dict):
        """Draw season and time period indicators"""
        # Season indicator (left side)
        season = time_info['season']
        season_symbol = self.season_symbols.get(season, "🌍")
        season_text = self.font_date.render(f"{season_symbol} {season}", True, time_info['season_color'])
        season_rect = season_text.get_rect(center=(self.clock_x + 40, self.clock_y + 20))
        self.screen.blit(season_text, season_rect)
        
        # Time period indicator (right side)
        time_period = time_info['time_period']
        period_symbol = self.time_period_symbols.get(time_period, "🕐")
        period_text = self.font_date.render(f"{period_symbol} {time_period}", True, time_info['time_period_color'])
        period_rect = period_text.get_rect(center=(self.clock_x + self.clock_width - 50, self.clock_y + 20))
        self.screen.blit(period_text, period_rect)
        
        # Weekend indicator
        if time_info['is_weekend']:
            weekend_text = self.font_small.render("🎉 Weekend!", True, (255, 200, 100))
            weekend_rect = weekend_text.get_rect(center=(self.clock_x + self.clock_width - 50, 
                                                        self.clock_y + 35))
            self.screen.blit(weekend_text, weekend_rect)
    
    def _draw_progress_indicators(self, game_time):
        """Draw mini progress bars for day, week, month, year"""
        # Progress bar settings
        bar_width = 60
        bar_height = 4
        bar_spacing = 70
        start_x = self.clock_x + 10
        progress_y = self.clock_y + self.clock_height - 12
        
        # Progress data
        progress_data = [
            ("Day", game_time.get_progress_in_day(), (100, 255, 100)),
            ("Week", game_time.get_progress_in_week(), (100, 200, 255)),
            ("Month", game_time.get_progress_in_month(), (255, 200, 100)),
            ("Year", game_time.get_progress_in_year(), (255, 150, 255))
        ]
        
        for i, (label, progress, color) in enumerate(progress_data):
            x = start_x + i * bar_spacing
            
            # Label
            label_text = self.font_small.render(label, True, (150, 150, 150))
            label_rect = label_text.get_rect(center=(x + bar_width // 2, progress_y - 8))
            self.screen.blit(label_text, label_rect)
            
            # Background bar
            bg_rect = pygame.Rect(x, progress_y, bar_width, bar_height)
            pygame.draw.rect(self.screen, (50, 50, 50), bg_rect, border_radius=2)
            
            # Progress fill
            if progress > 0:
                fill_width = int(bar_width * progress)
                fill_rect = pygame.Rect(x, progress_y, fill_width, bar_height)
                pygame.draw.rect(self.screen, color, fill_rect, border_radius=2)
                
                # Shine effect
                shine_rect = pygame.Rect(x + 1, progress_y, max(0, fill_width - 2), bar_height // 2)
                shine_color = tuple(min(255, c + 50) for c in color)
                pygame.draw.rect(self.screen, shine_color, shine_rect, border_radius=1)
    
    def _draw_analog_clock_mini(self, time_info: Dict):
        """Draw a small analog clock (optional enhancement)"""
        # Mini analog clock in corner
        clock_radius = 15
        clock_center_x = self.clock_x + self.clock_width - 25
        clock_center_y = self.clock_y + 45
        
        # Clock face
        pygame.draw.circle(self.screen, (40, 40, 40), (clock_center_x, clock_center_y), clock_radius)
        pygame.draw.circle(self.screen, (200, 200, 200), (clock_center_x, clock_center_y), clock_radius, 1)
        
        # Extract hour and minute from time string
        time_str = time_info['time']
        hour_str, minute_str = time_str.split(':')
        hour = int(hour_str)
        minute = int(minute_str.split()[0])  # Remove AM/PM
        
        # Convert to 24-hour format for calculation
        if 'PM' in time_str and hour != 12:
            hour += 12
        elif 'AM' in time_str and hour == 12:
            hour = 0
        
        # Hour hand
        hour_angle = (hour % 12) * 30 + (minute * 0.5) - 90  # -90 to start from top
        hour_length = clock_radius * 0.5
        hour_x = clock_center_x + hour_length * math.cos(math.radians(hour_angle))
        hour_y = clock_center_y + hour_length * math.sin(math.radians(hour_angle))
        pygame.draw.line(self.screen, (255, 255, 255), (clock_center_x, clock_center_y), 
                        (hour_x, hour_y), 2)
        
        # Minute hand
        minute_angle = minute * 6 - 90  # -90 to start from top
        minute_length = clock_radius * 0.8
        minute_x = clock_center_x + minute_length * math.cos(math.radians(minute_angle))
        minute_y = clock_center_y + minute_length * math.sin(math.radians(minute_angle))
        pygame.draw.line(self.screen, (255, 255, 255), (clock_center_x, clock_center_y), 
                        (minute_x, minute_y), 1)
        
        # Center dot
        pygame.draw.circle(self.screen, (255, 255, 255), (clock_center_x, clock_center_y), 2)
    
    def handle_event(self, event) -> bool:
        """Handle clock-related events (like clicking to change format)"""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # Check if clicked on clock area
            clock_rect = pygame.Rect(self.clock_x, self.clock_y, self.clock_width, self.clock_height)
            if clock_rect.collidepoint(event.pos):
                # Could toggle 12/24 hour format or show detailed time info
                return True
        return False