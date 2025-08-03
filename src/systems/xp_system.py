import pygame
import math
import json
import random
from typing import Dict, List, Optional, Tuple, Any
from enum import Enum
from dataclasses import dataclass
from src.core.constants import *

# Import quest types for integration
try:
    from src.systems.quest_system import ObjectiveType
except ImportError:
    ObjectiveType = None

class XPCategory(Enum):
    """Categories of experience that can be earned"""
    COMBAT = "combat"
    GATHERING = "gathering"
    CRAFTING = "crafting"
    SOCIAL = "social"
    EXPLORATION = "exploration"
    BUILDING = "building"
    FARMING = "farming"
    FISHING = "fishing"
    COOKING = "cooking"
    MAGIC = "magic"

@dataclass
class LevelReward:
    """Reward given when reaching a new level"""
    level: int
    reward_type: str  # "item", "skill_point", "ability", "stat_boost"
    reward_data: Dict[str, Any]
    description: str

@dataclass
class Achievement:
    """Achievement that can be unlocked"""
    id: str
    name: str
    description: str
    xp_reward: int
    category: XPCategory
    requirement: Dict[str, Any]
    icon: str
    unlocked: bool = False
    unlock_date: Optional[float] = None

class XPSystem:
    """
    Comprehensive XP and leveling system with multiple categories,
    achievements, and progression tracking
    """
    
    def __init__(self, quest_system=None):
        # Quest system integration
        self.quest_system = quest_system
        
        # Core XP tracking
        self.total_xp = 0
        self.current_level = 1
        self.xp_to_next_level = 100
        
        # Category-specific XP
        self.category_xp: Dict[XPCategory, int] = {category: 0 for category in XPCategory}
        self.category_levels: Dict[XPCategory, int] = {category: 1 for category in XPCategory}
        
        # XP configuration
        self.base_xp_requirement = 100
        self.xp_scaling_factor = 1.5
        self.max_level = 100
        self.category_max_level = 50
        
        # Skill points and abilities
        self.available_skill_points = 0
        self.spent_skill_points = 0
        self.unlocked_abilities: List[str] = []
        
        # Stats affected by leveling
        self.base_stats = {
            "health": 100,
            "stamina": 100,
            "mana": 50,
            "strength": 10,
            "dexterity": 10,
            "intelligence": 10,
            "luck": 5
        }
        self.stat_bonuses = {stat: 0 for stat in self.base_stats}
        
        # XP multipliers and bonuses
        self.xp_multiplier = 1.0
        self.category_multipliers: Dict[XPCategory, float] = {category: 1.0 for category in XPCategory}
        self.temp_xp_boosts: List[Dict] = []  # Temporary XP boosts with duration
        
        # Level rewards
        self.level_rewards: List[LevelReward] = []
        self._initialize_level_rewards()
        
        # Achievements
        self.achievements: List[Achievement] = []
        self._initialize_achievements()
        
        # XP gain history for statistics
        self.xp_history: List[Dict] = []
        self.daily_xp: Dict[str, int] = {}  # Date -> XP gained
        
        # Visual effects queue
        self.xp_popups: List[Dict] = []
        self.level_up_effects: List[Dict] = []
        
        # Prestige system
        self.prestige_level = 0
        self.prestige_bonuses = {
            "xp_multiplier": 0.0,
            "skill_point_bonus": 0,
            "stat_multiplier": 0.0
        }
    
    def _initialize_level_rewards(self):
        """Initialize rewards for reaching certain levels"""
        rewards_config = [
            # Early game rewards
            (5, "skill_point", {"amount": 2}, "Gain 2 skill points"),
            (10, "ability", {"ability": "double_jump"}, "Unlock Double Jump ability"),
            (15, "stat_boost", {"stat": "health", "amount": 20}, "+20 Max Health"),
            (20, "item", {"item_id": "golden_pickaxe", "quantity": 1}, "Receive Golden Pickaxe"),
            
            # Mid game rewards
            (25, "skill_point", {"amount": 3}, "Gain 3 skill points"),
            (30, "ability", {"ability": "fast_travel"}, "Unlock Fast Travel"),
            (35, "stat_boost", {"stat": "all", "amount": 5}, "+5 to all stats"),
            (40, "item", {"item_id": "master_crafting_book", "quantity": 1}, "Master Crafting Book"),
            
            # Late game rewards
            (50, "ability", {"ability": "prestige"}, "Unlock Prestige System"),
            (60, "stat_boost", {"stat": "luck", "amount": 10}, "+10 Luck"),
            (70, "skill_point", {"amount": 5}, "Gain 5 skill points"),
            (80, "item", {"item_id": "legendary_artifact", "quantity": 1}, "Legendary Artifact"),
            (90, "stat_boost", {"stat": "all", "amount": 10}, "+10 to all stats"),
            (100, "ability", {"ability": "master_of_all"}, "Master of All - Ultimate ability")
        ]
        
        for level, reward_type, reward_data, description in rewards_config:
            self.level_rewards.append(LevelReward(level, reward_type, reward_data, description))
    
    def _initialize_achievements(self):
        """Initialize achievement system"""
        achievements_config = [
            # Gathering achievements
            ("first_harvest", "First Harvest", "Harvest your first resource", 50, XPCategory.GATHERING, 
             {"type": "first_action", "action": "harvest"}, "🌾"),
            ("master_gatherer", "Master Gatherer", "Reach level 25 in Gathering", 500, XPCategory.GATHERING,
             {"type": "category_level", "category": "gathering", "level": 25}, "⛏️"),
            
            # Crafting achievements
            ("craft_100_items", "Prolific Crafter", "Craft 100 items", 200, XPCategory.CRAFTING,
             {"type": "counter", "action": "craft", "count": 100}, "🔨"),
            
            # Social achievements
            ("popular", "Popular", "Reach friendship level 10 with 5 NPCs", 300, XPCategory.SOCIAL,
             {"type": "social", "friends": 5, "level": 10}, "❤️"),
            
            # Exploration achievements
            ("explorer", "Explorer", "Discover 50 unique locations", 250, XPCategory.EXPLORATION,
             {"type": "exploration", "locations": 50}, "🗺️"),
            
            # Combat achievements
            ("first_victory", "First Victory", "Win your first battle", 100, XPCategory.COMBAT,
             {"type": "first_action", "action": "combat_win"}, "⚔️"),
            
            # General achievements
            ("level_10", "Experienced", "Reach level 10", 100, XPCategory.COMBAT,
             {"type": "level", "level": 10}, "⭐"),
            ("level_50", "Veteran", "Reach level 50", 1000, XPCategory.COMBAT,
             {"type": "level", "level": 50}, "🌟"),
            ("jack_of_all", "Jack of All Trades", "Reach level 10 in all categories", 2000, XPCategory.COMBAT,
             {"type": "all_categories", "level": 10}, "🎯"),
        ]
        
        for id, name, desc, xp, category, req, icon in achievements_config:
            self.achievements.append(Achievement(id, name, desc, xp, category, req, icon))
    
    def add_xp(self, amount: int, category: XPCategory, source: str = "", 
               show_popup: bool = True) -> Dict[str, Any]:
        """
        Add XP to the system with category tracking
        Returns info about level ups and rewards
        """
        # Apply multipliers
        total_multiplier = self.xp_multiplier * self.category_multipliers[category]
        
        # Apply temporary boosts
        for boost in self.temp_xp_boosts:
            if boost['category'] == 'all' or boost['category'] == category:
                total_multiplier *= boost['multiplier']
        
        # Apply prestige bonus
        total_multiplier *= (1.0 + self.prestige_bonuses['xp_multiplier'])
        
        final_xp = int(amount * total_multiplier)
        
        # Track XP gain
        self.total_xp += final_xp
        self.category_xp[category] += final_xp
        
        # Record in history
        import time
        self.xp_history.append({
            'amount': final_xp,
            'category': category.value,
            'source': source,
            'timestamp': time.time(),
            'multiplier': total_multiplier
        })
        
        # Update daily XP
        from datetime import datetime
        today = datetime.now().strftime("%Y-%m-%d")
        self.daily_xp[today] = self.daily_xp.get(today, 0) + final_xp
        
        # Create popup effect
        if show_popup:
            self.xp_popups.append({
                'amount': final_xp,
                'category': category,
                'x': SCREEN_WIDTH // 2 + random.randint(-50, 50),
                'y': SCREEN_HEIGHT - 200,
                'vy': -50,
                'life': 2.0,
                'color': self._get_category_color(category)
            })
        
        # Check for level ups
        level_up_info = self._check_level_up()
        category_level_up = self._check_category_level_up(category)
        
        # Check achievements
        unlocked_achievements = self._check_achievements()
        
        # Update quest objectives if quest system is available
        if self.quest_system and ObjectiveType:
            try:
                # Update XP earning objectives
                self.quest_system.update_objective(ObjectiveType.EARN_XP, "total_xp", final_xp)
                
                # Update level up objectives if leveled up
                if level_up_info:
                    self.quest_system.update_objective(ObjectiveType.LEVEL_UP_SKILL, "any_skill", 1)
                
                # Update category level up objectives
                if category_level_up:
                    self.quest_system.update_objective(ObjectiveType.LEVEL_UP_SKILL, category.value, 1)
            except Exception as e:
                print(f"Error updating quest objectives in XP system: {e}")
        
        return {
            'xp_gained': final_xp,
            'multiplier': total_multiplier,
            'level_up': level_up_info,
            'category_level_up': category_level_up,
            'unlocked_achievements': unlocked_achievements,
            'new_total': self.total_xp,
            'new_category_total': self.category_xp[category]
        }
    
    def _check_level_up(self) -> Optional[Dict]:
        """Check if player leveled up and process rewards"""
        if self.current_level >= self.max_level:
            return None
        
        level_up_info = None
        while self.total_xp >= self.xp_to_next_level and self.current_level < self.max_level:
            self.current_level += 1
            self.available_skill_points += 1 + self.prestige_bonuses['skill_point_bonus']
            
            # Calculate next level requirement
            self.xp_to_next_level = self._calculate_xp_requirement(self.current_level + 1)
            
            # Check for level rewards
            rewards = []
            for reward in self.level_rewards:
                if reward.level == self.current_level:
                    rewards.append(self._process_level_reward(reward))
            
            # Create level up effect
            self.level_up_effects.append({
                'level': self.current_level,
                'x': SCREEN_WIDTH // 2,
                'y': SCREEN_HEIGHT // 2,
                'time': 0.0,
                'duration': 3.0
            })
            
            level_up_info = {
                'new_level': self.current_level,
                'skill_points_gained': 1 + self.prestige_bonuses['skill_point_bonus'],
                'rewards': rewards
            }
        
        return level_up_info
    
    def _check_category_level_up(self, category: XPCategory) -> Optional[Dict]:
        """Check if a category leveled up"""
        if self.category_levels[category] >= self.category_max_level:
            return None
        
        current_xp = self.category_xp[category]
        current_level = self.category_levels[category]
        required_xp = self._calculate_category_xp_requirement(current_level + 1)
        
        if current_xp >= required_xp:
            self.category_levels[category] += 1
            
            # Category-specific bonuses
            bonus = self._get_category_level_bonus(category)
            
            return {
                'category': category.value,
                'new_level': self.category_levels[category],
                'bonus': bonus
            }
        
        return None
    
    def _calculate_xp_requirement(self, level: int) -> int:
        """Calculate XP required for a specific level"""
        return int(self.base_xp_requirement * (level ** self.xp_scaling_factor))
    
    def _calculate_category_xp_requirement(self, level: int) -> int:
        """Calculate XP required for a category level"""
        return int(50 * (level ** 1.3))  # Different scaling for categories
    
    def _get_category_color(self, category: XPCategory) -> Tuple[int, int, int]:
        """Get color associated with XP category"""
        colors = {
            XPCategory.COMBAT: (255, 100, 100),
            XPCategory.GATHERING: (100, 255, 100),
            XPCategory.CRAFTING: (255, 200, 100),
            XPCategory.SOCIAL: (255, 100, 255),
            XPCategory.EXPLORATION: (100, 200, 255),
            XPCategory.BUILDING: (200, 150, 100),
            XPCategory.FARMING: (150, 255, 150),
            XPCategory.FISHING: (100, 150, 255),
            XPCategory.COOKING: (255, 180, 100),
            XPCategory.MAGIC: (200, 100, 255)
        }
        return colors.get(category, (200, 200, 200))
    
    def _process_level_reward(self, reward: LevelReward) -> Dict:
        """Process a level reward"""
        result = {
            'type': reward.reward_type,
            'description': reward.description
        }
        
        if reward.reward_type == "skill_point":
            self.available_skill_points += reward.reward_data['amount']
            result['amount'] = reward.reward_data['amount']
            
        elif reward.reward_type == "ability":
            ability = reward.reward_data['ability']
            self.unlocked_abilities.append(ability)
            result['ability'] = ability
            
        elif reward.reward_type == "stat_boost":
            stat = reward.reward_data['stat']
            amount = reward.reward_data['amount']
            
            if stat == "all":
                for s in self.stat_bonuses:
                    self.stat_bonuses[s] += amount
            else:
                self.stat_bonuses[stat] += amount
            
            result['stat'] = stat
            result['amount'] = amount
            
        elif reward.reward_type == "item":
            # This would integrate with inventory system
            result['item'] = reward.reward_data
        
        return result
    
    def _get_category_level_bonus(self, category: XPCategory) -> Dict:
        """Get bonus for leveling up a category"""
        bonuses = {
            XPCategory.COMBAT: {"stat": "strength", "amount": 2},
            XPCategory.GATHERING: {"stat": "luck", "amount": 1},
            XPCategory.CRAFTING: {"stat": "dexterity", "amount": 2},
            XPCategory.SOCIAL: {"stat": "intelligence", "amount": 1},
            XPCategory.EXPLORATION: {"stat": "stamina", "amount": 5},
            XPCategory.BUILDING: {"stat": "strength", "amount": 1},
            XPCategory.FARMING: {"stat": "stamina", "amount": 3},
            XPCategory.FISHING: {"stat": "luck", "amount": 2},
            XPCategory.COOKING: {"stat": "health", "amount": 5},
            XPCategory.MAGIC: {"stat": "mana", "amount": 10}
        }
        
        bonus = bonuses.get(category, {"stat": "health", "amount": 2})
        self.stat_bonuses[bonus["stat"]] += bonus["amount"]
        
        return bonus
    
    def _check_achievements(self) -> List[Achievement]:
        """Check and unlock achievements"""
        unlocked = []
        
        for achievement in self.achievements:
            if achievement.unlocked:
                continue
            
            if self._check_achievement_requirement(achievement):
                achievement.unlocked = True
                achievement.unlock_date = pygame.time.get_ticks() / 1000.0
                
                # Add achievement XP
                self.add_xp(achievement.xp_reward, achievement.category, 
                           f"Achievement: {achievement.name}", show_popup=False)
                
                unlocked.append(achievement)
        
        return unlocked
    
    def _check_achievement_requirement(self, achievement: Achievement) -> bool:
        """Check if achievement requirement is met"""
        req = achievement.requirement
        req_type = req.get("type")
        
        if req_type == "level":
            return self.current_level >= req["level"]
        
        elif req_type == "category_level":
            category = XPCategory(req["category"])
            return self.category_levels[category] >= req["level"]
        
        elif req_type == "all_categories":
            target_level = req["level"]
            return all(level >= target_level for level in self.category_levels.values())
        
        # Other achievement types would be checked against game state
        return False
    
    def spend_skill_points(self, skill_tree_node: str, cost: int = 1) -> bool:
        """Spend skill points on a skill tree node"""
        if self.available_skill_points >= cost:
            self.available_skill_points -= cost
            self.spent_skill_points += cost
            return True
        return False
    
    def add_temporary_boost(self, multiplier: float, duration: float, 
                           category: Optional[XPCategory] = None):
        """Add a temporary XP boost"""
        boost = {
            'multiplier': multiplier,
            'duration': duration,
            'remaining': duration,
            'category': category or 'all'
        }
        self.temp_xp_boosts.append(boost)
    
    def prestige(self) -> bool:
        """
        Prestige system - reset to level 1 but gain permanent bonuses
        Requires level 50+ to prestige
        """
        if self.current_level < 50:
            return False
        
        # Calculate prestige bonuses based on current level
        bonus_multiplier = (self.current_level - 50) * 0.01  # 1% per level above 50
        
        self.prestige_level += 1
        self.prestige_bonuses['xp_multiplier'] += bonus_multiplier
        self.prestige_bonuses['skill_point_bonus'] += 1
        self.prestige_bonuses['stat_multiplier'] += 0.05
        
        # Reset levels but keep some benefits
        self.current_level = 1
        self.total_xp = 0
        self.xp_to_next_level = self._calculate_xp_requirement(2)
        
        # Reset category levels but give starting XP based on prestige
        starting_xp = 100 * self.prestige_level
        for category in XPCategory:
            self.category_xp[category] = starting_xp
            self.category_levels[category] = 1
        
        # Keep all unlocked abilities
        # Reset available skill points but give bonus
        self.available_skill_points = 5 * self.prestige_level
        
        return True
    
    def get_total_stats(self) -> Dict[str, int]:
        """Get total stats including base and bonuses"""
        total_stats = {}
        prestige_multiplier = 1.0 + self.prestige_bonuses['stat_multiplier']
        
        for stat, base_value in self.base_stats.items():
            total = base_value + self.stat_bonuses[stat]
            total = int(total * prestige_multiplier)
            total_stats[stat] = total
        
        return total_stats
    
    def get_xp_progress(self) -> Dict[str, Any]:
        """Get current XP progress information"""
        return {
            'level': self.current_level,
            'current_xp': self.total_xp,
            'xp_to_next': self.xp_to_next_level,
            'progress_percent': (self.total_xp / self.xp_to_next_level * 100) if self.xp_to_next_level > 0 else 100,
            'available_skill_points': self.available_skill_points,
            'prestige_level': self.prestige_level,
            'category_levels': {cat.value: level for cat, level in self.category_levels.items()},
            'total_stats': self.get_total_stats()
        }
    
    def get_category_progress(self, category: XPCategory) -> Dict[str, Any]:
        """Get progress for a specific category"""
        current_level = self.category_levels[category]
        current_xp = self.category_xp[category]
        
        if current_level >= self.category_max_level:
            return {
                'level': current_level,
                'current_xp': current_xp,
                'xp_to_next': 0,
                'progress_percent': 100,
                'max_level_reached': True
            }
        
        xp_to_next = self._calculate_category_xp_requirement(current_level + 1)
        xp_for_current = self._calculate_category_xp_requirement(current_level)
        progress_xp = current_xp - xp_for_current
        needed_xp = xp_to_next - xp_for_current
        
        return {
            'level': current_level,
            'current_xp': current_xp,
            'xp_to_next': xp_to_next,
            'progress_percent': (progress_xp / needed_xp * 100) if needed_xp > 0 else 0,
            'max_level_reached': False
        }
    
    def update(self, dt: float):
        """Update XP system (animations, temporary boosts, etc)"""
        # Update temporary boosts
        for boost in self.temp_xp_boosts[:]:
            boost['remaining'] -= dt
            if boost['remaining'] <= 0:
                self.temp_xp_boosts.remove(boost)
        
        # Update XP popup animations
        for popup in self.xp_popups[:]:
            popup['life'] -= dt
            popup['y'] += popup['vy'] * dt
            popup['vy'] *= 0.95  # Slow down
            
            if popup['life'] <= 0:
                self.xp_popups.remove(popup)
        
        # Update level up effects
        for effect in self.level_up_effects[:]:
            effect['time'] += dt
            if effect['time'] >= effect['duration']:
                self.level_up_effects.remove(effect)
    
    def draw_xp_effects(self, screen: pygame.Surface):
        """Draw XP-related visual effects"""
        # Draw XP popups
        for popup in self.xp_popups:
            alpha = int(255 * (popup['life'] / 2.0))
            
            font = pygame.font.Font(None, 24)
            text = f"+{popup['amount']} XP"
            text_surface = font.render(text, True, popup['color'])
            
            # Position with fade
            x = int(popup['x'])
            y = int(popup['y'])
            
            # Draw with transparency effect (simplified)
            screen.blit(text_surface, (x - text_surface.get_width() // 2, y))
        
        # Draw level up effects
        for effect in self.level_up_effects:
            progress = effect['time'] / effect['duration']
            
            if progress < 0.5:
                # Expanding circle effect
                radius = int(50 * (progress * 2))
                alpha = int(255 * (1 - progress * 2))
                
                for i in range(3):
                    r = radius + i * 10
                    color = (255, 215, 0)  # Gold
                    pygame.draw.circle(screen, color, (effect['x'], effect['y']), r, 3)
            
            # Level up text
            font = pygame.font.Font(None, 48)
            text = f"LEVEL {effect['level']}!"
            text_surface = font.render(text, True, (255, 215, 0))
            
            # Bounce effect
            bounce = abs(math.sin(effect['time'] * 10)) * 10
            x = effect['x'] - text_surface.get_width() // 2
            y = effect['y'] - text_surface.get_height() // 2 - bounce
            
            screen.blit(text_surface, (x, y))
    
    def save_data(self) -> Dict:
        """Save XP system data"""
        return {
            'total_xp': self.total_xp,
            'current_level': self.current_level,
            'category_xp': {cat.value: xp for cat, xp in self.category_xp.items()},
            'category_levels': {cat.value: level for cat, level in self.category_levels.items()},
            'available_skill_points': self.available_skill_points,
            'spent_skill_points': self.spent_skill_points,
            'unlocked_abilities': self.unlocked_abilities,
            'stat_bonuses': self.stat_bonuses,
            'prestige_level': self.prestige_level,
            'prestige_bonuses': self.prestige_bonuses,
            'achievements': [
                {
                    'id': ach.id,
                    'unlocked': ach.unlocked,
                    'unlock_date': ach.unlock_date
                }
                for ach in self.achievements
            ],
            'daily_xp': self.daily_xp
        }
    
    def load_data(self, data: Dict):
        """Load XP system data"""
        self.total_xp = data.get('total_xp', 0)
        self.current_level = data.get('current_level', 1)
        
        # Load category data
        for cat_name, xp in data.get('category_xp', {}).items():
            try:
                category = XPCategory(cat_name)
                self.category_xp[category] = xp
            except ValueError:
                pass
        
        for cat_name, level in data.get('category_levels', {}).items():
            try:
                category = XPCategory(cat_name)
                self.category_levels[category] = level
            except ValueError:
                pass
        
        self.available_skill_points = data.get('available_skill_points', 0)
        self.spent_skill_points = data.get('spent_skill_points', 0)
        self.unlocked_abilities = data.get('unlocked_abilities', [])
        self.stat_bonuses = data.get('stat_bonuses', {stat: 0 for stat in self.base_stats})
        self.prestige_level = data.get('prestige_level', 0)
        self.prestige_bonuses = data.get('prestige_bonuses', self.prestige_bonuses)
        
        # Load achievements
        achievement_data = {ach['id']: ach for ach in data.get('achievements', [])}
        for achievement in self.achievements:
            if achievement.id in achievement_data:
                ach_data = achievement_data[achievement.id]
                achievement.unlocked = ach_data['unlocked']
                achievement.unlock_date = ach_data['unlock_date']
        
        self.daily_xp = data.get('daily_xp', {})
        
        # Recalculate XP requirements
        self.xp_to_next_level = self._calculate_xp_requirement(self.current_level + 1)