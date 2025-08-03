import random
import math
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import pygame

@dataclass
class ResourceNode:
    """A resource node that can be harvested"""
    x: int
    y: int
    resource_type: str
    resource_id: str  # What item it gives
    max_yield: int
    current_yield: int
    regeneration_time: float  # seconds to fully regenerate
    last_harvest_time: float
    required_tool: Optional[str] = None
    required_skill_level: int = 1
    skill_type: str = "foraging"
    visual_type: Optional[str] = None  # Specific visual variant for trees

class ResourceSystem:
    """
    Manages resource nodes and gathering throughout the world
    """
    
    def __init__(self, inventory_system, skill_system):
        self.inventory = inventory_system
        self.skills = skill_system
        self.resource_nodes: List[ResourceNode] = []
        self.game_time = 0.0
        self._initialize_resource_types()
        self._spawn_initial_resources()
    
    def _initialize_resource_types(self):
        """Define what resources can be found and their properties"""
        self.resource_configs = {
            # Trees
            "oak_tree": {
                "item": "wood",
                "base_yield": 3,
                "variance": 2,
                "regen_time": 30.0,
                "tool": "basic_axe",
                "skill": "foraging",
                "skill_level": 1,
                "icon": "🌳",
                "size": (32, 48)
            },
            "pine_tree": {
                "item": "wood",
                "base_yield": 4,
                "variance": 2,
                "regen_time": 45.0,
                "tool": "basic_axe",
                "skill": "foraging",
                "skill_level": 3,
                "icon": "🌲",
                "size": (32, 48)
            },
            
            # Rocks and minerals
            "stone_node": {
                "item": "stone",
                "base_yield": 2,
                "variance": 1,
                "regen_time": 60.0,
                "tool": "basic_pickaxe",
                "skill": "mining",
                "skill_level": 1,
                "icon": "🪨",
                "size": (24, 24)
            },
            "copper_node": {
                "item": "copper_ore",
                "base_yield": 1,
                "variance": 1,
                "regen_time": 120.0,
                "tool": "basic_pickaxe",
                "skill": "mining",
                "skill_level": 1,
                "icon": "🟤",
                "size": (24, 24)
            },
            "iron_node": {
                "item": "iron_ore",
                "base_yield": 1,
                "variance": 1,
                "regen_time": 180.0,
                "tool": "basic_pickaxe",
                "skill": "mining",
                "skill_level": 5,
                "icon": "⚫",
                "size": (24, 24)
            },
            
            # Forageable items
            "berry_bush": {
                "item": "wild_berries",
                "base_yield": 2,
                "variance": 1,
                "regen_time": 90.0,
                "tool": None,
                "skill": "foraging",
                "skill_level": 1,
                "icon": "🫐",
                "size": (24, 24)
            },
            "mushroom_log": {
                "item": "mushrooms",
                "base_yield": 1,
                "variance": 1,
                "regen_time": 120.0,
                "tool": None,
                "skill": "foraging",
                "skill_level": 3,
                "icon": "🍄",
                "size": (20, 20)
            },
            "herb_patch": {
                "item": "herbs",
                "base_yield": 1,
                "variance": 1,
                "regen_time": 75.0,
                "tool": None,
                "skill": "foraging",
                "skill_level": 2,
                "icon": "🌿",
                "size": (16, 16)
            },
        }
    
    def _spawn_initial_resources(self):
        """Spawn initial resource nodes around the map"""
        # Define spawn areas and densities spread across the entire map
        spawn_configs = [
            # Trees will be added separately from map positions
            
            # Stone formations (spread across map regions)
            ("stone_node", 35, (100, 100), (1900, 1900)),  # Everywhere
            
            # Copper nodes (common mining areas)
            ("copper_node", 20, (200, 200), (1800, 1800)),  # Most areas
            
            # Iron nodes (intermediate mining spots)
            ("iron_node", 12, (300, 300), (1700, 1700)),  # Central regions
            
            # Forageable items spread widely
            ("berry_bush", 25, (150, 150), (1850, 1850)),  # Wild berries everywhere
            ("mushroom_log", 18, (200, 200), (1800, 1800)),  # Forest mushrooms
            ("herb_patch", 30, (100, 100), (1900, 1900)),  # Herbs in all areas
        ]
        
        for resource_type, count, (min_x, min_y), (max_x, max_y) in spawn_configs:
            for _ in range(count):
                x = random.randint(min_x, max_x)
                y = random.randint(min_y, max_y)
                
                # Don't spawn too close to existing nodes - better spacing
                too_close = False
                for existing in self.resource_nodes:
                    distance = math.sqrt((x - existing.x) ** 2 + (y - existing.y) ** 2)
                    if distance < 80:  # Increased minimum distance for better spreading
                        too_close = True
                        break
                
                if not too_close:
                    config = self.resource_configs[resource_type]
                    max_yield = config["base_yield"] + random.randint(0, config["variance"])
                    
                    # Ensure skill level is valid (max 5 for current system)
                    skill_level = min(config["skill_level"], 5)
                    
                    node = ResourceNode(
                        x=x,
                        y=y,
                        resource_type=resource_type,
                        resource_id=config["item"],
                        max_yield=max_yield,
                        current_yield=max_yield,
                        regeneration_time=config["regen_time"],
                        last_harvest_time=0.0,
                        required_tool=config["tool"],
                        required_skill_level=skill_level,
                        skill_type=config["skill"]
                    )
                    self.resource_nodes.append(node)
    
    def add_trees_from_map(self, tree_positions):
        """Add harvestable trees from map positions"""
        import random
        
        tree_types = ["oak_tree", "oak_tree", "pine_tree"]  # More oak trees than pine
        
        for x, y in tree_positions:
            # Choose tree type and visual variant
            tree_type = random.choice(tree_types)
            tree_visual = random.choice(["tree_1", "tree_2", "tree_3", "tree_4"])
            config = self.resource_configs[tree_type]
            max_yield = config["base_yield"] + random.randint(0, config["variance"])
            
            # Ensure skill level is valid (max 5 for current trees)
            skill_level = min(config["skill_level"], 5)
            
            node = ResourceNode(
                x=x,
                y=y,
                resource_type=tree_type,
                resource_id=config["item"],
                max_yield=max_yield,
                current_yield=max_yield,
                regeneration_time=config["regen_time"],
                last_harvest_time=0.0,
                required_tool=config["tool"],
                required_skill_level=skill_level,
                skill_type=config["skill"],
                visual_type=tree_visual
            )
            self.resource_nodes.append(node)
        
        # Add special resource-rich areas for exploration incentive
        self._add_special_resource_areas()
    
    def _add_special_resource_areas(self):
        """Add special concentrated resource areas to encourage exploration"""
        import random
        
        special_areas = [
            # Rich copper mining area (eastern mountains)
            {"center": (1600, 600), "radius": 150, "resource": "copper_node", "count": 8},
            
            # Iron-rich valley (central-south)
            {"center": (1000, 1400), "radius": 120, "resource": "iron_node", "count": 6},
            
            # Berry grove (northwest)
            {"center": (300, 300), "radius": 100, "resource": "berry_bush", "count": 10},
            
            # Herb garden (far south)
            {"center": (800, 1700), "radius": 130, "resource": "herb_patch", "count": 12},
            
            # Stone quarry (northeast)
            {"center": (1500, 200), "radius": 140, "resource": "stone_node", "count": 15},
            
            # Mushroom forest (southwest)
            {"center": (250, 1200), "radius": 160, "resource": "mushroom_log", "count": 8},
        ]
        
        for area in special_areas:
            center_x, center_y = area["center"]
            radius = area["radius"]
            resource_type = area["resource"]
            count = area["count"]
            
            for _ in range(count):
                # Generate position within radius
                angle = random.uniform(0, 2 * math.pi)
                distance = random.uniform(0, radius)
                x = int(center_x + distance * math.cos(angle))
                y = int(center_y + distance * math.sin(angle))
                
                # Keep within map bounds
                x = max(100, min(x, 1900))
                y = max(100, min(y, 1900))
                
                # Check distance from existing nodes (smaller distance for special areas)
                too_close = False
                for existing in self.resource_nodes:
                    distance = math.sqrt((x - existing.x) ** 2 + (y - existing.y) ** 2)
                    if distance < 40:  # Closer spacing allowed in special areas
                        too_close = True
                        break
                
                if not too_close and resource_type in self.resource_configs:
                    config = self.resource_configs[resource_type]
                    max_yield = config["base_yield"] + random.randint(0, config["variance"])
                    
                    node = ResourceNode(
                        x=x,
                        y=y,
                        resource_type=resource_type,
                        resource_id=config["item"],
                        max_yield=max_yield,
                        current_yield=max_yield,
                        regeneration_time=config["regen_time"],
                        last_harvest_time=0.0,
                        required_tool=config["tool"],
                        required_skill_level=config["skill_level"],
                        skill_type=config["skill"]
                    )
                    self.resource_nodes.append(node)
    
    def update(self, dt: float):
        """Update resource regeneration"""
        self.game_time += dt
        
        for node in self.resource_nodes:
            if node.current_yield < node.max_yield:
                time_since_harvest = self.game_time - node.last_harvest_time
                if time_since_harvest >= node.regeneration_time:
                    node.current_yield = node.max_yield
    
    def get_resource_at(self, x: int, y: int, range_threshold: int = 40) -> Optional[ResourceNode]:
        """Get resource node near the given coordinates"""
        for node in self.resource_nodes:
            distance = math.sqrt((x - node.x) ** 2 + (y - node.y) ** 2)
            if distance <= range_threshold and node.current_yield > 0:
                return node
        return None
    
    def harvest_resource(self, player_x: int, player_y: int, tool_id: Optional[str] = None) -> Tuple[bool, str]:
        """Attempt to harvest a resource near the player"""
        node = self.get_resource_at(player_x, player_y)
        if not node:
            return False, "No resources nearby to harvest"
        
        if node.current_yield <= 0:
            return False, f"This {node.resource_type} has been depleted"
        
        # Check tool requirement
        if node.required_tool and not tool_id:
            config = self.resource_configs[node.resource_type]
            tool_data = self.inventory.get_item_data(node.required_tool)
            tool_name = tool_data.name if tool_data else node.required_tool
            return False, f"Need {tool_name} to harvest this resource"
        
        if node.required_tool and tool_id != node.required_tool:
            # Check if player has the required tool in inventory
            if not self.inventory.has_item(node.required_tool, 1):
                tool_data = self.inventory.get_item_data(node.required_tool)
                tool_name = tool_data.name if tool_data else node.required_tool
                return False, f"Need {tool_name} to harvest this resource"
        
        # Check skill level
        player_skill_level = self.skills.get_skill_level(node.skill_type)
        if player_skill_level < node.required_skill_level:
            return False, f"Need {node.skill_type} level {node.required_skill_level}"
        
        # Calculate harvest amount (skill affects yield)
        skill_bonus = self.skills.get_skill_bonus(node.skill_type)
        base_harvest = 1
        bonus_chance = (skill_bonus - 1.0) * 0.5  # 50% of skill bonus becomes extra yield chance
        
        harvest_amount = base_harvest
        if random.random() < bonus_chance:
            harvest_amount += 1
        
        # Don't harvest more than available
        harvest_amount = min(harvest_amount, node.current_yield)
        
        # Determine quality based on skill level
        quality = 1
        if player_skill_level >= 10:
            quality_chance = (player_skill_level - 10) * 0.02  # 2% per level above 10
            if random.random() < quality_chance:
                quality = min(5, 2 + (player_skill_level // 20))  # Max 5-star quality
        
        # Add to inventory
        success = self.inventory.add_item(node.resource_id, harvest_amount, quality)
        if not success:
            return False, "Inventory full!"
        
        # Update node
        node.current_yield -= harvest_amount
        if node.current_yield <= 0:
            node.last_harvest_time = self.game_time
        
        # Give experience
        base_exp = 5
        exp_gained = base_exp * harvest_amount
        exp_result = self.skills.add_experience(node.skill_type, exp_gained)
        
        # Get item name for message
        item_data = self.inventory.get_item_data(node.resource_id)
        item_name = item_data.name if item_data else node.resource_id
        
        quality_text = f" ({quality}⭐)" if quality > 1 else ""
        message = f"Harvested {harvest_amount} {item_name}{quality_text}! (+{exp_gained} {node.skill_type} XP)"
        
        if exp_result["leveled_up"]:
            message += f" {node.skill_type.title()} level up! Now level {exp_result['new_level']}"
        
        return True, message
    
    def get_visible_resources(self, camera_rect: pygame.Rect) -> List[ResourceNode]:
        """Get resources visible in camera view"""
        visible = []
        for node in self.resource_nodes:
            if (camera_rect.left <= node.x <= camera_rect.right and 
                camera_rect.top <= node.y <= camera_rect.bottom):
                visible.append(node)
        return visible
    
    def draw_resources(self, screen: pygame.Surface, camera):
        """Draw resource nodes on the map - WITH PROPER RESOURCE SPRITES"""
        import pygame
        import os
        
        # Cache all resource sprites once
        if not hasattr(self, '_resource_sprites_cache'):
            self._resource_sprites_cache = {}
            
            # Load tree sprites
            for i in range(1, 6):  # tree_1.png to tree_5.png
                tree_path = f"images/nature/trees/tree_{i}.png"
                if os.path.exists(tree_path):
                    try:
                        sprite = pygame.image.load(tree_path).convert_alpha()
                        self._resource_sprites_cache[f'tree_{i}'] = sprite
                    except:
                        pass
            
            # Load resource tileset for mining resources
            resources_path = "images/nature/environment/resources.png"
            if os.path.exists(resources_path):
                try:
                    tileset = pygame.image.load(resources_path).convert_alpha()
                    
                    # Extract individual resource sprites (each is roughly 64x64)
                    sprite_size = 64
                    
                    # Top row: Gold, Diamond, Ruby, Emerald
                    resources = [
                        ('gold', 0, 0), ('diamond', 1, 0), ('ruby', 2, 0), ('emerald', 3, 0),
                        ('coal', 0, 1), ('copper', 1, 1), ('stone', 2, 1),
                        ('wood', 0, 2), ('log', 1, 2)
                    ]
                    
                    for name, col, row in resources:
                        x = col * sprite_size
                        y = row * sprite_size
                        sprite = tileset.subsurface(pygame.Rect(x, y, sprite_size, sprite_size)).copy()
                        # Scale down to fit 32x32 tiles
                        sprite = pygame.transform.scale(sprite, (32, 32))
                        self._resource_sprites_cache[name] = sprite
                        
                except Exception as e:
                    print(f"Error loading resource sprites: {e}")
        
        for node in self.resource_nodes:
            if node.current_yield > 0:
                # Get node configuration
                config = self.resource_configs[node.resource_type]
                
                # Calculate screen position based on resource size
                size = config.get("size", (32, 32))
                screen_rect = camera.apply_rect(pygame.Rect(node.x - size[0]//2, node.y - size[1]//2, size[0], size[1]))
                
                # Use proper sprites for all resources
                sprite_drawn = False
                
                if node.resource_type in ["oak_tree", "pine_tree"]:
                    # Use the SMALL clean tree design (not big sprites)
                    center_x = screen_rect.centerx
                    center_y = screen_rect.centery
                    
                    # Tree trunk (brown rectangle) - SMALL SIZE
                    trunk_width = 4
                    trunk_height = 8
                    trunk_rect = pygame.Rect(center_x - trunk_width//2, center_y + 2, trunk_width, trunk_height)
                    pygame.draw.rect(screen, (101, 67, 33), trunk_rect)  # Brown trunk
                    
                    # Tree crown (green circle) - SMALL SIZE
                    crown_radius = 8
                    pygame.draw.circle(screen, (34, 139, 34), (center_x, center_y - 2), crown_radius)  # Green crown
                    
                    # Add some depth with a darker outline
                    pygame.draw.circle(screen, (20, 100, 20), (center_x, center_y - 2), crown_radius, 1)
                    sprite_drawn = True
                
                elif node.resource_type == "copper_node":
                    # Copper - Orange circle with "Cu" text
                    pygame.draw.circle(screen, (184, 115, 51), screen_rect.center, 14)  # Orange copper color
                    pygame.draw.circle(screen, (139, 69, 19), screen_rect.center, 14, 2)  # Dark outline
                    if not hasattr(self, '_resource_font'):
                        self._resource_font = pygame.font.Font(None, 16)
                    text = self._resource_font.render("Cu", True, (255, 255, 255))
                    text_rect = text.get_rect(center=screen_rect.center)
                    screen.blit(text, text_rect)
                    sprite_drawn = True
                        
                elif node.resource_type == "stone_node":
                    # Stone - Gray square
                    pygame.draw.rect(screen, (128, 128, 128), screen_rect)
                    pygame.draw.rect(screen, (64, 64, 64), screen_rect, 2)  # Dark outline
                    sprite_drawn = True
                        
                elif node.resource_type == "coal_node":
                    # Coal - Black circle
                    pygame.draw.circle(screen, (32, 32, 32), screen_rect.center, 14)  # Very dark
                    pygame.draw.circle(screen, (128, 128, 128), screen_rect.center, 14, 2)  # Gray outline
                    sprite_drawn = True
                        
                elif node.resource_type == "gold_node":
                    # Gold - Yellow diamond shape
                    center = screen_rect.center
                    points = [
                        (center[0], center[1] - 12),  # Top
                        (center[0] + 12, center[1]),  # Right
                        (center[0], center[1] + 12),  # Bottom
                        (center[0] - 12, center[1])   # Left
                    ]
                    pygame.draw.polygon(screen, (255, 215, 0), points)  # Gold color
                    pygame.draw.polygon(screen, (184, 134, 11), points, 2)  # Dark outline
                    sprite_drawn = True
                        
                elif node.resource_type == "iron_node":
                    # Iron - Silver circle with "Fe" text
                    pygame.draw.circle(screen, (169, 169, 169), screen_rect.center, 14)  # Silver
                    pygame.draw.circle(screen, (105, 105, 105), screen_rect.center, 14, 2)  # Dark outline
                    if not hasattr(self, '_resource_font'):
                        self._resource_font = pygame.font.Font(None, 16)
                    text = self._resource_font.render("Fe", True, (255, 255, 255))
                    text_rect = text.get_rect(center=screen_rect.center)
                    screen.blit(text, text_rect)
                    sprite_drawn = True
                
                elif "flower" in node.resource_type.lower():
                    # Flower - Pink circle with "F" text
                    pygame.draw.circle(screen, (255, 182, 193), screen_rect.center, 14)  # Light pink
                    pygame.draw.circle(screen, (255, 20, 147), screen_rect.center, 14, 2)  # Deep pink outline
                    if not hasattr(self, '_resource_font'):
                        self._resource_font = pygame.font.Font(None, 16)
                    text = self._resource_font.render("F", True, (255, 255, 255))
                    text_rect = text.get_rect(center=screen_rect.center)
                    screen.blit(text, text_rect)
                    sprite_drawn = True
                
                elif "mushroom" in node.resource_type.lower():
                    # Mushroom - Brown rounded rectangle with "M" text
                    pygame.draw.ellipse(screen, (139, 69, 19), screen_rect)  # Brown
                    pygame.draw.ellipse(screen, (101, 67, 33), screen_rect, 2)  # Dark outline
                    if not hasattr(self, '_resource_font'):
                        self._resource_font = pygame.font.Font(None, 16)
                    text = self._resource_font.render("M", True, (255, 255, 255))
                    text_rect = text.get_rect(center=screen_rect.center)
                    screen.blit(text, text_rect)
                    sprite_drawn = True
                
                # Fallback to simple rectangle if no sprite available
                if not sprite_drawn:
                    if node.resource_type in ["oak_tree", "pine_tree"]:
                        color = (34, 139, 34)  # Green for trees
                    else:
                        color = (139, 69, 19)   # Brown for other resources
                    pygame.draw.rect(screen, color, screen_rect)
                
                # Restore yield indicator and progress bars for all resources
                if node.current_yield < node.max_yield:
                    # Draw regeneration progress
                    time_since_harvest = self.game_time - node.last_harvest_time
                    progress = min(1.0, time_since_harvest / node.regeneration_time)
                    
                    # Progress bar
                    bar_width = 24
                    bar_height = 4
                    bar_x = screen_rect.centerx - bar_width // 2
                    bar_y = screen_rect.bottom + 2
                    
                    # Background
                    pygame.draw.rect(screen, (100, 100, 100), (bar_x, bar_y, bar_width, bar_height))
                    # Progress
                    progress_width = int(bar_width * progress)
                    pygame.draw.rect(screen, (100, 200, 100), (bar_x, bar_y, progress_width, bar_height))
                
                # Draw yield count with cached font
                if node.current_yield > 1:
                    # Cache font to avoid creating it every frame
                    if not hasattr(self, '_yield_font'):
                        self._yield_font = pygame.font.Font(None, 16)
                    
                    yield_text = self._yield_font.render(str(node.current_yield), True, (255, 255, 255))
                    yield_rect = yield_text.get_rect()
                    yield_rect.topright = (screen_rect.right, screen_rect.top)
                    
                    # Background circle for readability
                    pygame.draw.circle(screen, (0, 0, 0), yield_rect.center, 8)
                    screen.blit(yield_text, yield_rect)
    
    def add_starting_items(self):
        """Give player comprehensive starting tools and resources"""
        starting_items = [
            # Essential tools
            ("basic_axe", 1),
            ("basic_pickaxe", 1),
            ("basic_hoe", 1),
            ("basic_watering_can", 1),
            ("fishing_rod", 1),
            
            # Basic resources
            ("wood", 25),
            ("stone", 15),
            ("fiber", 20),
            ("coal", 10),
            
            # Seeds for farming
            ("parsnip_seeds", 10),
            ("potato_seeds", 5),
            ("cauliflower_seeds", 3),
            
            # Basic food
            ("bread", 5),
            ("wild_berries", 8),
            
            # Some processed materials
            ("copper_bar", 2),
            ("chest", 2),
            
            # Starting money
        ]
        
        for item_id, quantity in starting_items:
            self.inventory.add_item(item_id, quantity)
        
        # Add extra starting money
        self.inventory.add_money(500)
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for saving"""
        return {
            "game_time": self.game_time,
            "resource_nodes": [
                {
                    "x": node.x,
                    "y": node.y,
                    "resource_type": node.resource_type,
                    "current_yield": node.current_yield,
                    "last_harvest_time": node.last_harvest_time,
                    "visual_type": node.visual_type
                }
                for node in self.resource_nodes
            ]
        }
    
    def from_dict(self, data: Dict):
        """Load from dictionary"""
        self.game_time = data.get("game_time", 0.0)
        
        if "resource_nodes" in data:
            # Clear existing nodes
            self.resource_nodes.clear()
            
            # Restore saved nodes
            for node_data in data["resource_nodes"]:
                resource_type = node_data["resource_type"]
                if resource_type in self.resource_configs:
                    config = self.resource_configs[resource_type]
                    
                    node = ResourceNode(
                        x=node_data["x"],
                        y=node_data["y"],
                        resource_type=resource_type,
                        resource_id=config["item"],
                        max_yield=config["base_yield"] + config["variance"],
                        current_yield=node_data["current_yield"],
                        regeneration_time=config["regen_time"],
                        last_harvest_time=node_data["last_harvest_time"],
                        required_tool=config["tool"],
                        required_skill_level=config["skill_level"],
                        skill_type=config["skill"],
                        visual_type=node_data.get("visual_type")
                    )
                    self.resource_nodes.append(node)