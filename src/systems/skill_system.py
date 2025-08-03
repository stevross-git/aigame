import math
from typing import Dict, List, Optional
from dataclasses import dataclass

@dataclass
class SkillData:
    """Data for a single skill"""
    name: str
    level: int
    experience: int
    description: str
    icon: str

class SkillSystem:
    """
    Manages player skills similar to Stardew Valley
    """
    
    def __init__(self):
        self.skills: Dict[str, SkillData] = {}
        self.skill_points = 0  # Unspent skill points
        self._initialize_skills()
    
    def _initialize_skills(self):
        """Initialize all available skills"""
        skill_definitions = [
            ("farming", "Farming", "🌾", "Grow crops and raise animals"),
            ("mining", "Mining", "⛏️", "Extract ores and gems from the earth"),
            ("foraging", "Foraging", "🌿", "Find wild resources and food"),
            ("fishing", "Fishing", "🎣", "Catch fish and aquatic treasures"),
            ("combat", "Combat", "⚔️", "Fight monsters and defend yourself"),
            ("cooking", "Cooking", "🍳", "Prepare delicious meals and recipes"),
            ("crafting", "Crafting", "🔨", "Create tools, furniture, and items"),
            ("social", "Social", "💬", "Build relationships with NPCs"),
            ("luck", "Luck", "🍀", "Influence random events and finds"),
            ("fitness", "Fitness", "💪", "Improve stamina and energy capacity")
        ]
        
        for skill_id, name, icon, description in skill_definitions:
            self.skills[skill_id] = SkillData(
                name=name,
                level=1,
                experience=0,
                description=description,
                icon=icon
            )
    
    def get_skill_level(self, skill_name: str) -> int:
        """Get the level of a specific skill"""
        return self.skills.get(skill_name, SkillData("", 0, 0, "", "")).level
    
    def get_skill_experience(self, skill_name: str) -> int:
        """Get the experience of a specific skill"""
        return self.skills.get(skill_name, SkillData("", 0, 0, "", "")).experience
    
    def add_experience(self, skill_name: str, amount: int) -> Dict:
        """Add experience to a skill and return level up info"""
        if skill_name not in self.skills:
            return {"leveled_up": False, "new_level": 0, "skill_name": skill_name}
        
        skill = self.skills[skill_name]
        old_level = skill.level
        skill.experience += amount
        
        # Calculate new level
        new_level = self._calculate_level(skill.experience)
        leveled_up = new_level > old_level
        
        if leveled_up:
            skill.level = new_level
            levels_gained = new_level - old_level
            self.skill_points += levels_gained  # Gain skill points for leveling up
        
        return {
            "leveled_up": leveled_up,
            "old_level": old_level,
            "new_level": new_level,
            "skill_name": skill_name,
            "experience_gained": amount,
            "total_experience": skill.experience,
            "levels_gained": new_level - old_level if leveled_up else 0
        }
    
    def _calculate_level(self, experience: int) -> int:
        """Calculate level based on experience (similar to Stardew Valley formula)"""
        if experience < 100:
            return 1
        
        # Stardew Valley-like progression: each level requires more XP
        level = 1
        total_xp_needed = 0
        
        while total_xp_needed <= experience:
            level += 1
            # XP needed for next level increases by 100 + (level * 50)
            xp_for_this_level = 100 + (level * 50)
            total_xp_needed += xp_for_this_level
            
            if level >= 100:  # Cap at level 100
                break
        
        return min(level - 1, 100)
    
    def get_experience_for_next_level(self, skill_name: str) -> int:
        """Get experience needed for next level"""
        if skill_name not in self.skills:
            return 0
        
        skill = self.skills[skill_name]
        current_level = skill.level
        
        if current_level >= 100:
            return 0  # Max level
        
        # Calculate total XP needed for next level
        total_xp_needed = 0
        for level in range(2, current_level + 2):
            total_xp_needed += 100 + (level * 50)
        
        return max(0, total_xp_needed - skill.experience)
    
    def get_skill_bonus(self, skill_name: str) -> float:
        """Get skill bonus multiplier (higher level = better results)"""
        level = self.get_skill_level(skill_name)
        # 1% bonus per level, up to 100% bonus at level 100
        return 1.0 + (level * 0.01)
    
    def get_all_skills(self) -> Dict[str, SkillData]:
        """Get all skills"""
        return self.skills.copy()
    
    def spend_skill_point(self, skill_name: str) -> bool:
        """Spend a skill point to boost a skill"""
        if self.skill_points <= 0 or skill_name not in self.skills:
            return False
        
        skill = self.skills[skill_name]
        if skill.level >= 100:
            return False  # Max level
        
        # Boost experience towards next level
        xp_boost = 200  # Significant boost
        self.add_experience(skill_name, xp_boost)
        self.skill_points -= 1
        return True
    
    def get_skill_description(self, skill_name: str, level: int) -> str:
        """Get description of what a skill does at a certain level"""
        descriptions = {
            "farming": {
                1: "Basic crop tending",
                10: "10% faster crop growth",
                25: "Chance for extra harvest",
                50: "Premium crop quality",
                75: "Advanced greenhouse techniques", 
                100: "Master farmer - maximum yields"
            },
            "mining": {
                1: "Basic rock breaking",
                10: "Find better ores",
                25: "Chance for gem discoveries",
                50: "Rare metal detection",
                75: "Deep mining expertise",
                100: "Legendary ore finder"
            },
            "foraging": {
                1: "Find basic plants",
                10: "Spot rare mushrooms",
                25: "Discover medicinal herbs",
                50: "Locate treasure caches",
                75: "Forest secret knowledge",
                100: "Nature's bounty master"
            },
            "fishing": {
                1: "Catch common fish",
                10: "Better fishing spots",
                25: "Rare fish attraction",
                50: "Perfect fishing technique",
                75: "Legendary fish locator",
                100: "Master angler"
            },
            "combat": {
                1: "Basic self-defense",
                10: "Improved weapon handling",
                25: "Critical hit chance",
                50: "Advanced combat tactics",
                75: "Monster expertise",
                100: "Legendary warrior"
            },
            "cooking": {
                1: "Simple recipes",
                10: "Improved food quality",
                25: "Recipe experimentation",
                50: "Gourmet techniques",
                75: "Master chef skills",
                100: "Culinary perfection"
            },
            "crafting": {
                1: "Basic tool creation",
                10: "Improved item quality",
                25: "Advanced blueprints",
                50: "Master craftsmanship",
                75: "Legendary item creation",
                100: "Artisan perfection"
            },
            "social": {
                1: "Basic conversation",
                10: "Improved NPC relations",
                25: "Faster friendship building",
                50: "Community influence",
                75: "Social network mastery",
                100: "Beloved by all"
            },
            "luck": {
                1: "Occasional good fortune",
                10: "Better random finds",
                25: "Improved drop rates",
                50: "Fortune favors you",
                75: "Remarkable luck streaks",
                100: "Incredibly fortunate"
            },
            "fitness": {
                1: "Basic stamina",
                10: "Increased energy capacity",
                25: "Faster movement speed",
                50: "Superior endurance",
                75: "Athletic excellence",
                100: "Peak physical condition"
            }
        }
        
        skill_desc = descriptions.get(skill_name, {})
        
        # Find the highest level description that applies
        applicable_level = 1
        for desc_level in sorted(skill_desc.keys(), reverse=True):
            if level >= desc_level:
                applicable_level = desc_level
                break
        
        return skill_desc.get(applicable_level, "Unknown skill benefit")
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for saving"""
        return {
            "skills": {name: {
                "level": skill.level,
                "experience": skill.experience
            } for name, skill in self.skills.items()},
            "skill_points": self.skill_points
        }
    
    def from_dict(self, data: Dict):
        """Load from dictionary"""
        if "skills" in data:
            for skill_name, skill_data in data["skills"].items():
                if skill_name in self.skills:
                    self.skills[skill_name].level = skill_data.get("level", 1)
                    self.skills[skill_name].experience = skill_data.get("experience", 0)
        
        self.skill_points = data.get("skill_points", 0)