from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

@dataclass
class CraftingRecipe:
    """A recipe for crafting an item"""
    recipe_id: str
    result_item: str
    result_quantity: int
    ingredients: Dict[str, int]  # item_id -> quantity needed
    required_skill: Optional[str] = None
    required_skill_level: int = 1
    crafting_time: float = 2.0  # seconds
    experience_reward: int = 10
    unlocked: bool = True

class CraftingSystem:
    """
    Manages crafting recipes and creation of items
    """
    
    def __init__(self, inventory_system, skill_system, xp_system=None):
        self.inventory = inventory_system
        self.skills = skill_system
        self.xp_system = xp_system  # Optional XP system integration
        self.recipes: Dict[str, CraftingRecipe] = {}
        self.unlocked_recipes: set = set()
        self._initialize_recipes()
    
    def _initialize_recipes(self):
        """Initialize all crafting recipes"""
        recipes = [
            # Basic crafting recipes
            CraftingRecipe(
                recipe_id="craft_chest",
                result_item="chest",
                result_quantity=1,
                ingredients={"wood": 50, "copper_ore": 1},
                required_skill="crafting",
                required_skill_level=1,
                crafting_time=3.0,
                experience_reward=15
            ),
            
            CraftingRecipe(
                recipe_id="craft_scarecrow",
                result_item="scarecrow",
                result_quantity=1,
                ingredients={"wood": 25, "fiber": 20, "coal": 1},
                required_skill="farming",
                required_skill_level=5,
                crafting_time=5.0,
                experience_reward=25
            ),
            
            # Tool upgrades
            CraftingRecipe(
                recipe_id="upgrade_axe_copper",
                result_item="copper_axe",
                result_quantity=1,
                ingredients={"basic_axe": 1, "copper_ore": 5, "wood": 10},
                required_skill="crafting",
                required_skill_level=3,
                crafting_time=8.0,
                experience_reward=50
            ),
            
            CraftingRecipe(
                recipe_id="upgrade_pickaxe_copper",
                result_item="copper_pickaxe",
                result_quantity=1,
                ingredients={"basic_pickaxe": 1, "copper_ore": 5, "wood": 10},
                required_skill="crafting",
                required_skill_level=3,
                crafting_time=8.0,
                experience_reward=50
            ),
            
            # Food recipes
            CraftingRecipe(
                recipe_id="cook_bread",
                result_item="bread",
                result_quantity=2,
                ingredients={"wheat": 1},
                required_skill="cooking",
                required_skill_level=1,
                crafting_time=2.0,
                experience_reward=15
            ),
            
            CraftingRecipe(
                recipe_id="cook_salad",
                result_item="salad",
                result_quantity=1,
                ingredients={"tomato": 1, "potato": 1},
                required_skill="cooking",
                required_skill_level=3,
                crafting_time=3.0,
                experience_reward=25
            ),
            
            CraftingRecipe(
                recipe_id="cook_pizza",
                result_item="pizza",
                result_quantity=1,
                ingredients={"bread": 1, "tomato": 2, "cheese": 1},
                required_skill="cooking",
                required_skill_level=7,
                crafting_time=5.0,
                experience_reward=40
            ),
            
            # Advanced crafting
            CraftingRecipe(
                recipe_id="craft_mayo_machine",
                result_item="mayo_machine",
                result_quantity=1,
                ingredients={"wood": 75, "stone": 25, "copper_ore": 10, "iron_ore": 5},
                required_skill="crafting",
                required_skill_level=15,
                crafting_time=12.0,
                experience_reward=100
            ),
            
            CraftingRecipe(
                recipe_id="craft_preserve_jar",
                result_item="preserve_jar",
                result_quantity=1,
                ingredients={"wood": 50, "stone": 40, "coal": 8},
                required_skill="crafting",
                required_skill_level=12,
                crafting_time=10.0,
                experience_reward=80
            ),
            
            # Resource processing
            CraftingRecipe(
                recipe_id="smelt_copper_bar",
                result_item="copper_bar",
                result_quantity=1,
                ingredients={"copper_ore": 5, "coal": 1},
                required_skill="mining",
                required_skill_level=1,
                crafting_time=4.0,
                experience_reward=20
            ),
            
            CraftingRecipe(
                recipe_id="smelt_iron_bar",
                result_item="iron_bar",
                result_quantity=1,
                ingredients={"iron_ore": 5, "coal": 1},
                required_skill="mining",
                required_skill_level=5,
                crafting_time=6.0,
                experience_reward=35
            ),
            
            CraftingRecipe(
                recipe_id="smelt_gold_bar",
                result_item="gold_bar",
                result_quantity=1,
                ingredients={"gold_ore": 5, "coal": 1},
                required_skill="mining",
                required_skill_level=10,
                crafting_time=8.0,
                experience_reward=50
            ),
            
            # Artisan goods
            CraftingRecipe(
                recipe_id="make_wine",
                result_item="wine",
                result_quantity=1,
                ingredients={"grapes": 1},
                required_skill="farming",
                required_skill_level=8,
                crafting_time=60.0,  # 1 minute for game purposes, normally days
                experience_reward=60
            ),
            
            CraftingRecipe(
                recipe_id="make_cheese",
                result_item="cheese",
                result_quantity=1,
                ingredients={"milk": 1},
                required_skill="farming",
                required_skill_level=5,
                crafting_time=30.0,
                experience_reward=40
            ),
        ]
        
        for recipe in recipes:
            self.recipes[recipe.recipe_id] = recipe
            # Start with basic recipes unlocked
            if recipe.required_skill_level <= 1:
                self.unlocked_recipes.add(recipe.recipe_id)
    
    def can_craft(self, recipe_id: str) -> Tuple[bool, str]:
        """Check if a recipe can be crafted. Returns (can_craft, reason)"""
        if recipe_id not in self.recipes:
            return False, "Recipe not found"
        
        recipe = self.recipes[recipe_id]
        
        # Check if recipe is unlocked
        if recipe_id not in self.unlocked_recipes:
            return False, "Recipe not unlocked"
        
        # Check skill requirements
        if recipe.required_skill:
            player_level = self.skills.get_skill_level(recipe.required_skill)
            if player_level < recipe.required_skill_level:
                return False, f"Requires {recipe.required_skill} level {recipe.required_skill_level}"
        
        # Check ingredients
        for ingredient, needed_amount in recipe.ingredients.items():
            if not self.inventory.has_item(ingredient, needed_amount):
                have_amount = self.inventory.get_item_count(ingredient)
                item_data = self.inventory.get_item_data(ingredient)
                item_name = item_data.name if item_data else ingredient
                return False, f"Need {needed_amount} {item_name} (have {have_amount})"
        
        return True, "Can craft"
    
    def craft_item(self, recipe_id: str) -> Tuple[bool, str]:
        """Attempt to craft an item. Returns (success, message)"""
        can_craft, reason = self.can_craft(recipe_id)
        if not can_craft:
            return False, reason
        
        recipe = self.recipes[recipe_id]
        
        # Remove ingredients
        for ingredient, amount in recipe.ingredients.items():
            if not self.inventory.remove_item(ingredient, amount):
                # This shouldn't happen if can_craft passed, but safety check
                return False, f"Failed to remove {ingredient}"
        
        # Add result item
        if not self.inventory.add_item(recipe.result_item, recipe.result_quantity):
            # Restore ingredients if we can't add result (inventory full)
            for ingredient, amount in recipe.ingredients.items():
                self.inventory.add_item(ingredient, amount)
            return False, "Inventory full - ingredients restored"
        
        # Give experience
        if recipe.required_skill:
            exp_result = self.skills.add_experience(recipe.required_skill, recipe.experience_reward)
            
            # Check if we unlocked new recipes from leveling up
            if exp_result["leveled_up"]:
                newly_unlocked = self._check_recipe_unlocks()
                if newly_unlocked:
                    return True, f"Crafted {recipe.result_item}! Skill level up! Unlocked new recipes: {', '.join(newly_unlocked)}"
        
        # Grant XP if system is available
        if self.xp_system:
            try:
                from src.systems.xp_system import XPCategory
                xp_amount = recipe.experience_reward * recipe.result_quantity
                
                # Determine category based on result item type
                if recipe.required_skill == "cooking":
                    xp_category = XPCategory.COOKING
                elif recipe.required_skill == "farming":
                    xp_category = XPCategory.FARMING
                else:
                    xp_category = XPCategory.CRAFTING
                
                result_item_data = self.inventory.get_item_data(recipe.result_item)
                result_name = result_item_data.name if result_item_data else recipe.result_item
                self.xp_system.add_xp(xp_amount, xp_category, f"Crafted {result_name}")
            except Exception as e:
                print(f"Error adding XP for crafting: {e}")
        
        result_item_data = self.inventory.get_item_data(recipe.result_item)
        result_name = result_item_data.name if result_item_data else recipe.result_item
        
        return True, f"Successfully crafted {result_name}!"
    
    def _check_recipe_unlocks(self) -> List[str]:
        """Check for newly unlocked recipes and return their names"""
        newly_unlocked = []
        
        for recipe_id, recipe in self.recipes.items():
            if recipe_id not in self.unlocked_recipes:
                if recipe.required_skill:
                    player_level = self.skills.get_skill_level(recipe.required_skill)
                    if player_level >= recipe.required_skill_level:
                        self.unlocked_recipes.add(recipe_id)
                        result_item_data = self.inventory.get_item_data(recipe.result_item)
                        result_name = result_item_data.name if result_item_data else recipe.result_item
                        newly_unlocked.append(result_name)
                        
                        # Grant XP for discovering a new recipe
                        if self.xp_system:
                            try:
                                from src.systems.xp_system import XPCategory
                                self.xp_system.add_xp(50, XPCategory.CRAFTING, f"Discovered recipe: {result_name}")
                            except Exception as e:
                                print(f"Error adding XP for recipe discovery: {e}")
        
        return newly_unlocked
    
    def get_available_recipes(self) -> List[CraftingRecipe]:
        """Get all unlocked recipes that can potentially be crafted"""
        available = []
        for recipe_id in self.unlocked_recipes:
            if recipe_id in self.recipes:
                available.append(self.recipes[recipe_id])
        return available
    
    def get_craftable_recipes(self) -> List[CraftingRecipe]:
        """Get recipes that can be crafted right now"""
        craftable = []
        for recipe in self.get_available_recipes():
            can_craft, _ = self.can_craft(recipe.recipe_id)
            if can_craft:
                craftable.append(recipe)
        return craftable
    
    def get_recipe(self, recipe_id: str) -> Optional[CraftingRecipe]:
        """Get a specific recipe"""
        return self.recipes.get(recipe_id)
    
    def unlock_recipe(self, recipe_id: str) -> bool:
        """Manually unlock a recipe"""
        if recipe_id in self.recipes:
            self.unlocked_recipes.add(recipe_id)
            return True
        return False
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for saving"""
        return {
            "unlocked_recipes": list(self.unlocked_recipes)
        }
    
    def from_dict(self, data: Dict):
        """Load from dictionary"""
        if "unlocked_recipes" in data:
            self.unlocked_recipes = set(data["unlocked_recipes"])
            
            # Always ensure basic recipes are unlocked
            for recipe_id, recipe in self.recipes.items():
                if recipe.required_skill_level <= 1:
                    self.unlocked_recipes.add(recipe_id)