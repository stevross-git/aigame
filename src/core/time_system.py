import math
from typing import Dict, Tuple

class GameTime:
    """
    Comprehensive time system for AI Sims with realistic time progression
    """
    
    def __init__(self):
        # Time configuration
        self.seconds_per_game_minute = 1.0  # 1 real second = 1 game minute
        self.minutes_per_game_hour = 60
        self.hours_per_game_day = 24
        self.days_per_game_week = 7
        self.days_per_game_month = 30
        self.months_per_game_year = 12
        self.days_per_game_year = 360  # 12 months × 30 days
        
        # Current time values
        self.total_game_seconds = 0.0
        self.minute = 0
        self.hour = 6  # Start at 6 AM
        self.day = 1
        self.week = 1
        self.month = 1
        self.year = 1
        
        # Day names
        self.day_names = [
            "Monday", "Tuesday", "Wednesday", "Thursday", 
            "Friday", "Saturday", "Sunday"
        ]
        
        # Month names
        self.month_names = [
            "Spring Early", "Spring Mid", "Spring Late",
            "Summer Early", "Summer Mid", "Summer Late", 
            "Fall Early", "Fall Mid", "Fall Late",
            "Winter Early", "Winter Mid", "Winter Late"
        ]
        
        # Season information
        self.seasons = ["Spring", "Summer", "Fall", "Winter"]
        
        # Time of day periods
        self.time_periods = {
            "Dawn": (5, 7),
            "Morning": (7, 12),
            "Afternoon": (12, 17),
            "Evening": (17, 20),
            "Night": (20, 24),
            "Late Night": (0, 5)
        }
    
    def update(self, dt: float, time_multiplier: float = 1.0):
        """Update the game time"""
        self.total_game_seconds += dt * time_multiplier
        
        # Calculate current time from total seconds
        total_minutes = int(self.total_game_seconds / self.seconds_per_game_minute)
        
        # Break down into time components
        self.minute = total_minutes % self.minutes_per_game_hour
        total_hours = total_minutes // self.minutes_per_game_hour
        
        self.hour = total_hours % self.hours_per_game_day
        total_days = total_hours // self.hours_per_game_day
        
        # Add 1 to make days 1-based instead of 0-based
        current_day = total_days + 1
        
        # Calculate day, week, month, year
        self.day = ((current_day - 1) % self.days_per_game_month) + 1
        self.week = ((current_day - 1) // self.days_per_game_week) + 1
        
        total_months = ((current_day - 1) // self.days_per_game_month)
        self.month = (total_months % self.months_per_game_year) + 1
        self.year = (total_months // self.months_per_game_year) + 1
    
    def get_time_string(self, format_12_hour: bool = True) -> str:
        """Get formatted time string"""
        if format_12_hour:
            display_hour = self.hour
            am_pm = "AM"
            
            if display_hour == 0:
                display_hour = 12
            elif display_hour > 12:
                display_hour -= 12
                am_pm = "PM"
            elif display_hour == 12:
                am_pm = "PM"
            
            return f"{display_hour:02d}:{self.minute:02d} {am_pm}"
        else:
            return f"{self.hour:02d}:{self.minute:02d}"
    
    def get_day_name(self) -> str:
        """Get the name of the current day of the week"""
        # Calculate day of week (0-6, where 0 is Monday)
        total_days = self.get_total_days()
        day_of_week = (total_days - 1) % 7
        return self.day_names[day_of_week]
    
    def get_month_name(self) -> str:
        """Get the name of the current month"""
        return self.month_names[self.month - 1]
    
    def get_season(self) -> str:
        """Get the current season"""
        season_index = ((self.month - 1) // 3) % 4
        return self.seasons[season_index]
    
    def get_season_color(self) -> Tuple[int, int, int]:
        """Get color associated with current season"""
        season_colors = {
            "Spring": (100, 255, 100),  # Light green
            "Summer": (255, 255, 100),  # Yellow
            "Fall": (255, 150, 50),     # Orange
            "Winter": (150, 200, 255)   # Light blue
        }
        return season_colors[self.get_season()]
    
    def get_time_period(self) -> str:
        """Get the current time period (Dawn, Morning, etc.)"""
        for period, (start, end) in self.time_periods.items():
            if start <= self.hour < end:
                return period
        return "Late Night"  # Default fallback
    
    def get_time_period_color(self) -> Tuple[int, int, int]:
        """Get color associated with current time period"""
        period_colors = {
            "Dawn": (255, 180, 120),      # Orange
            "Morning": (255, 255, 150),   # Light yellow
            "Afternoon": (255, 255, 255), # White
            "Evening": (255, 200, 150),   # Warm orange
            "Night": (150, 150, 200),     # Purple-blue
            "Late Night": (100, 100, 150) # Dark blue
        }
        return period_colors.get(self.get_time_period(), (255, 255, 255))
    
    def get_total_days(self) -> int:
        """Get total number of days since game start"""
        return (self.year - 1) * self.days_per_game_year + (self.month - 1) * self.days_per_game_month + self.day
    
    def get_sun_position(self) -> float:
        """Get sun position for day/night cycle (0.0 = midnight, 0.5 = noon)"""
        return (self.hour + self.minute / 60.0) / 24.0
    
    def is_daytime(self) -> bool:
        """Check if it's currently daytime"""
        return 6 <= self.hour < 20
    
    def is_weekend(self) -> bool:
        """Check if it's weekend (Saturday or Sunday)"""
        total_days = self.get_total_days()
        day_of_week = (total_days - 1) % 7
        return day_of_week >= 5  # Saturday (5) or Sunday (6)
    
    def get_progress_in_day(self) -> float:
        """Get progress through the current day (0.0 to 1.0)"""
        return (self.hour + self.minute / 60.0) / 24.0
    
    def get_progress_in_week(self) -> float:
        """Get progress through the current week (0.0 to 1.0)"""
        total_days = self.get_total_days()
        day_in_week = ((total_days - 1) % 7) + 1
        day_progress = self.get_progress_in_day()
        return (day_in_week - 1 + day_progress) / 7.0
    
    def get_progress_in_month(self) -> float:
        """Get progress through the current month (0.0 to 1.0)"""
        day_progress = self.get_progress_in_day()
        return (self.day - 1 + day_progress) / self.days_per_game_month
    
    def get_progress_in_year(self) -> float:
        """Get progress through the current year (0.0 to 1.0)"""
        total_days_in_year = (self.month - 1) * self.days_per_game_month + self.day
        day_progress = self.get_progress_in_day()
        return (total_days_in_year - 1 + day_progress) / self.days_per_game_year
    
    def get_time_info(self) -> Dict:
        """Get comprehensive time information"""
        return {
            'time': self.get_time_string(),
            'day_name': self.get_day_name(),
            'day': self.day,
            'week': self.week,
            'month': self.month,
            'month_name': self.get_month_name(),
            'year': self.year,
            'season': self.get_season(),
            'time_period': self.get_time_period(),
            'is_weekend': self.is_weekend(),
            'is_daytime': self.is_daytime(),
            'sun_position': self.get_sun_position(),
            'season_color': self.get_season_color(),
            'time_period_color': self.get_time_period_color()
        }
    
    def get_save_data(self) -> Dict:
        """Get time system data for saving"""
        return {
            'total_game_seconds': self.total_game_seconds,
            'minute': self.minute,
            'hour': self.hour,
            'day': self.day,
            'week': self.week,
            'month': self.month,
            'year': self.year
        }
    
    def load_save_data(self, save_data: Dict):
        """Load time system data from save"""
        if save_data:
            self.total_game_seconds = save_data.get('total_game_seconds', 0.0)
            self.minute = save_data.get('minute', 0)
            self.hour = save_data.get('hour', 6)
            self.day = save_data.get('day', 1)
            self.week = save_data.get('week', 1)
            self.month = save_data.get('month', 1)
            self.year = save_data.get('year', 1)