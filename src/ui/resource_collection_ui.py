import pygame
import math
from typing import Dict, List, Optional, Tuple
from src.core.constants import *
from src.systems.inventory_system import InventorySystem, ItemType, ItemRarity
from src.systems.resource_system import ResourceSystem, ResourceNode
from src.systems.skill_system import SkillSystem

class ResourceCollectionUI:
    """
    Advanced UI for resource collection with detailed information and options
    """
    
    def __init__(self, screen, inventory_system: InventorySystem, resource_system: ResourceSystem, skill_system: SkillSystem):
        self.screen = screen
        self.inventory = inventory_system
        self.resources = resource_system
        self.skills = skill_system
        
        # UI State
        self.visible = False
        self.current_resource: Optional[ResourceNode] = None
        self.player_pos = (0, 0)
        self.collection_progress = 0.0
        self.collection_active = False
        self.collection_time = 0.0
        self.total_collection_time = 1.0
        
        # Fonts
        self.font_title = pygame.font.Font(None, 28)
        self.font_normal = pygame.font.Font(None, 22)
        self.font_small = pygame.font.Font(None, 18)
        
        # Colors
        self.bg_color = (30, 40, 50, 240)
        self.panel_color = (50, 60, 70, 220)
        self.border_color = (100, 120, 140)
        self.text_color = (255, 255, 255)
        self.success_color = (100, 255, 100)
        self.warning_color = (255, 200, 100)
        self.error_color = (255, 100, 100)
        
        # Panel dimensions
        self.panel_width = 400
        self.panel_height = 300
        
        # Collection history
        self.recent_collections = []
        self.max_history = 10
    
    def show_resource_info(self, resource_node: ResourceNode, player_pos: Tuple[int, int]):
        """Show detailed information about a resource node"""
        self.visible = True
        self.current_resource = resource_node
        self.player_pos = player_pos
        self.collection_active = False
        self.collection_progress = 0.0
        
        # Calculate panel position (near resource but on screen)
        resource_screen_x = resource_node.x
        resource_screen_y = resource_node.y
        
        self.panel_x = max(50, min(SCREEN_WIDTH - self.panel_width - 50, resource_screen_x - self.panel_width // 2))
        self.panel_y = max(50, min(SCREEN_HEIGHT - self.panel_height - 50, resource_screen_y - 150))
    
    def hide(self):
        """Hide the resource collection UI"""
        self.visible = False
        self.current_resource = None
        self.collection_active = False
        self.collection_progress = 0.0
    
    def start_collection(self):
        """Start the collection process"""
        if not self.current_resource or self.collection_active:
            return False
        
        # Check if collection is possible
        can_collect, message = self._can_collect_resource()
        if not can_collect:
            return False
        
        self.collection_active = True
        self.collection_progress = 0.0
        self.collection_time = 0.0
        
        # Calculate collection time based on resource type and skill
        base_time = self._get_base_collection_time()
        skill_level = self.skills.get_skill_level(self.current_resource.skill_type)
        skill_modifier = max(0.3, 1.0 - (skill_level * 0.05))  # Up to 70% faster at high skill
        
        self.total_collection_time = base_time * skill_modifier
        return True
    
    def update(self, dt: float):
        """Update collection progress"""
        if not self.visible or not self.collection_active:
            return
        
        self.collection_time += dt
        self.collection_progress = min(1.0, self.collection_time / self.total_collection_time)
        
        # Complete collection
        if self.collection_progress >= 1.0:
            self._complete_collection()
    
    def _complete_collection(self):
        """Complete the resource collection"""
        if not self.current_resource:
            return
        
        # Perform the actual harvest
        player_x, player_y = self.player_pos
        success, message = self.resources.harvest_resource(player_x, player_y)
        
        # Add to collection history
        if success:
            item_data = self.inventory.get_item_data(self.current_resource.resource_id)
            collection_info = {
                "item_name": item_data.name if item_data else self.current_resource.resource_id,
                "item_icon": item_data.icon if item_data else "📦",
                "message": message,
                "timestamp": pygame.time.get_ticks(),
                "success": True
            }
        else:
            collection_info = {
                "item_name": "Collection Failed",
                "item_icon": "❌",
                "message": message,
                "timestamp": pygame.time.get_ticks(),
                "success": False
            }
        
        self.recent_collections.append(collection_info)
        if len(self.recent_collections) > self.max_history:
            self.recent_collections.pop(0)
        
        # Reset collection state
        self.collection_active = False
        self.collection_progress = 0.0
        
        # Hide if resource is depleted or collection failed
        if not success or self.current_resource.current_yield <= 0:
            self.hide()
    
    def _can_collect_resource(self) -> Tuple[bool, str]:
        """Check if the resource can be collected"""
        if not self.current_resource:
            return False, "No resource selected"
        
        if self.current_resource.current_yield <= 0:
            return False, f"This {self.current_resource.resource_type} has been depleted"
        
        # Check tool requirement
        if self.current_resource.required_tool:
            if not self.inventory.has_item(self.current_resource.required_tool, 1):
                tool_data = self.inventory.get_item_data(self.current_resource.required_tool)
                tool_name = tool_data.name if tool_data else self.current_resource.required_tool
                return False, f"Need {tool_name} to harvest this resource"
        
        # Check skill level
        player_skill_level = self.skills.get_skill_level(self.current_resource.skill_type)
        if player_skill_level < self.current_resource.required_skill_level:
            return False, f"Need {self.current_resource.skill_type} level {self.current_resource.required_skill_level}"
        
        return True, "Ready to collect"
    
    def _get_base_collection_time(self) -> float:
        """Get base collection time for the resource type"""
        if not self.current_resource:
            return 1.0
        
        # Different resources take different amounts of time
        time_map = {
            "oak_tree": 2.5,
            "pine_tree": 3.0,
            "stone_node": 1.5,
            "copper_node": 2.0,
            "iron_node": 2.5,
            "berry_bush": 0.8,
            "mushroom_log": 1.2,
            "herb_patch": 0.6
        }
        
        return time_map.get(self.current_resource.resource_type, 1.0)
    
    def _get_resource_info(self) -> Dict:
        """Get detailed information about the current resource"""
        if not self.current_resource:
            return {}
        
        config = self.resources.resource_configs.get(self.current_resource.resource_type, {})
        item_data = self.inventory.get_item_data(self.current_resource.resource_id)
        
        # Calculate potential yield with skill bonuses
        skill_level = self.skills.get_skill_level(self.current_resource.skill_type)
        skill_bonus = self.skills.get_skill_bonus(self.current_resource.skill_type)
        bonus_chance = (skill_bonus - 1.0) * 0.5
        
        base_yield = min(1, self.current_resource.current_yield)
        potential_bonus = int(bonus_chance * 100)
        
        # Quality chance
        quality_chance = 0
        if skill_level >= 10:
            quality_chance = (skill_level - 10) * 2  # 2% per level above 10
        
        return {
            "name": item_data.name if item_data else self.current_resource.resource_id,
            "icon": config.get("icon", "📦"),
            "description": item_data.description if item_data else "A resource that can be collected",
            "rarity": item_data.rarity.value if item_data else "common",
            "base_value": item_data.base_value if item_data else 0,
            "current_yield": self.current_resource.current_yield,
            "max_yield": self.current_resource.max_yield,
            "required_skill": self.current_resource.skill_type,
            "required_level": self.current_resource.required_skill_level,
            "player_level": skill_level,
            "required_tool": self.current_resource.required_tool,
            "regeneration_time": self.current_resource.regeneration_time,
            "base_yield": base_yield,
            "bonus_chance": potential_bonus,
            "quality_chance": quality_chance
        }
    
    def draw(self):
        """Draw the resource collection UI"""
        if not self.visible:
            return
        
        # Main panel
        panel_rect = pygame.Rect(self.panel_x, self.panel_y, self.panel_width, self.panel_height)
        pygame.draw.rect(self.screen, self.bg_color, panel_rect, border_radius=10)
        pygame.draw.rect(self.screen, self.border_color, panel_rect, 3, border_radius=10)
        
        if not self.current_resource:
            return
        
        # Get resource information
        info = self._get_resource_info()
        if not info:
            return
        
        y_offset = self.panel_y + 15
        
        # Resource header
        self._draw_resource_header(info, y_offset)
        y_offset += 50
        
        # Resource details
        y_offset = self._draw_resource_details(info, y_offset)
        y_offset += 10
        
        # Collection status
        y_offset = self._draw_collection_status(y_offset)
        
        # Collection progress bar (if collecting)
        if self.collection_active:
            self._draw_collection_progress(y_offset)
    
    def _draw_resource_header(self, info: Dict, y_offset: int):
        """Draw the resource header with icon and name"""
        # Resource icon
        icon_surface = self.font_title.render(info["icon"], True, self.text_color)
        self.screen.blit(icon_surface, (self.panel_x + 15, y_offset))
        
        # Resource name
        name_surface = self.font_title.render(info["name"], True, self.text_color)
        self.screen.blit(name_surface, (self.panel_x + 50, y_offset))
        
        # Rarity indicator
        rarity_colors = {
            "common": (150, 150, 150),
            "uncommon": (100, 255, 100),
            "rare": (100, 100, 255),
            "epic": (200, 100, 255),
            "legendary": (255, 200, 50)
        }
        rarity_color = rarity_colors.get(info["rarity"], (150, 150, 150))
        rarity_surface = self.font_small.render(f"[{info['rarity'].upper()}]", True, rarity_color)
        self.screen.blit(rarity_surface, (self.panel_x + self.panel_width - 100, y_offset + 5))
        
        # Yield indicator
        yield_text = f"{info['current_yield']}/{info['max_yield']}"
        yield_surface = self.font_normal.render(yield_text, True, self.text_color)
        self.screen.blit(yield_surface, (self.panel_x + 15, y_offset + 25))
    
    def _draw_resource_details(self, info: Dict, y_offset: int) -> int:
        """Draw detailed resource information"""
        details = [
            f"Value: {info['base_value']}g per unit",
            f"Skill: {info['required_skill'].title()} (Level {info['required_level']} required)",
            f"Your Level: {info['player_level']} ({'+' if info['player_level'] >= info['required_level'] else '-'})",
        ]
        
        if info["required_tool"]:
            tool_data = self.inventory.get_item_data(info["required_tool"])
            tool_name = tool_data.name if tool_data else info["required_tool"]
            has_tool = self.inventory.has_item(info["required_tool"])
            tool_status = "✓" if has_tool else "✗"
            details.append(f"Tool: {tool_name} ({tool_status})")
        
        # Potential rewards
        details.append(f"Base Yield: {info['base_yield']} + {info['bonus_chance']}% bonus chance")
        if info["quality_chance"] > 0:
            details.append(f"Quality Chance: {info['quality_chance']}% for higher star rating")
        
        for detail in details:
            detail_surface = self.font_small.render(detail, True, self.text_color)
            self.screen.blit(detail_surface, (self.panel_x + 15, y_offset))
            y_offset += 20
        
        return y_offset
    
    def _draw_collection_status(self, y_offset: int) -> int:
        """Draw collection status and controls"""
        can_collect, message = self._can_collect_resource()
        
        # Status message
        status_color = self.success_color if can_collect else self.error_color
        status_surface = self.font_normal.render(message, True, status_color)
        self.screen.blit(status_surface, (self.panel_x + 15, y_offset))
        y_offset += 25
        
        # Collection controls
        if can_collect and not self.collection_active:
            control_text = "Press SPACE to collect"
            control_surface = self.font_small.render(control_text, True, self.warning_color)
            self.screen.blit(control_surface, (self.panel_x + 15, y_offset))
        elif self.collection_active:
            control_text = "Collecting... (Hold SPACE to continue)"
            control_surface = self.font_small.render(control_text, True, self.success_color)
            self.screen.blit(control_surface, (self.panel_x + 15, y_offset))
        
        return y_offset + 20
    
    def _draw_collection_progress(self, y_offset: int):
        """Draw collection progress bar"""
        if not self.collection_active:
            return
        
        # Progress bar
        bar_width = self.panel_width - 30
        bar_height = 20
        bar_x = self.panel_x + 15
        bar_y = y_offset
        
        # Background
        bar_rect = pygame.Rect(bar_x, bar_y, bar_width, bar_height)
        pygame.draw.rect(self.screen, (60, 60, 60), bar_rect, border_radius=10)
        pygame.draw.rect(self.screen, self.border_color, bar_rect, 2, border_radius=10)
        
        # Progress fill
        progress_width = int(bar_width * self.collection_progress)
        if progress_width > 0:
            progress_rect = pygame.Rect(bar_x, bar_y, progress_width, bar_height)
            pygame.draw.rect(self.screen, self.success_color, progress_rect, border_radius=10)
        
        # Progress text
        progress_text = f"{int(self.collection_progress * 100)}%"
        progress_surface = self.font_small.render(progress_text, True, self.text_color)
        progress_rect = progress_surface.get_rect(center=(bar_x + bar_width // 2, bar_y + bar_height // 2))
        self.screen.blit(progress_surface, progress_rect)
    
    def handle_event(self, event) -> bool:
        """Handle UI events"""
        if not self.visible:
            return False
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.hide()
                return True
            elif event.key == pygame.K_SPACE:
                if not self.collection_active:
                    return self.start_collection()
                return True
        
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_SPACE and self.collection_active:
                # Cancel collection if space is released
                self.collection_active = False
                self.collection_progress = 0.0
                return True
        
        return False
    
    def get_recent_collections(self) -> List[Dict]:
        """Get recent collection history"""
        return self.recent_collections.copy()