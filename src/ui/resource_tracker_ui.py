import pygame
import math
from typing import Dict, List, Optional, Tuple
from src.core.constants import *
from src.systems.inventory_system import InventorySystem, ItemType
from src.systems.resource_system import ResourceSystem, ResourceNode
from src.systems.skill_system import SkillSystem

class ResourceTrackerUI:
    """
    UI that tracks nearby resources, collection statistics, and resource locations
    """
    
    def __init__(self, screen, inventory_system: InventorySystem, resource_system: ResourceSystem, skill_system: SkillSystem):
        self.screen = screen
        self.inventory = inventory_system
        self.resources = resource_system
        self.skills = skill_system
        
        # UI State
        self.visible = False
        self.mini_map_visible = True
        self.current_mode = "nearby"  # "nearby", "statistics", "map"
        
        # Fonts
        self.font_title = pygame.font.Font(None, 24)
        self.font_normal = pygame.font.Font(None, 20)
        self.font_small = pygame.font.Font(None, 16)
        
        # Colors
        self.bg_color = (20, 30, 40, 200)
        self.panel_color = (40, 50, 60, 180)
        self.border_color = (80, 100, 120)
        self.text_color = (255, 255, 255)
        self.accent_color = (100, 150, 200)
        self.success_color = (100, 255, 100)
        self.warning_color = (255, 200, 100)
        
        # Main panel (right side of screen)
        self.panel_width = 300
        self.panel_height = 400
        self.panel_x = SCREEN_WIDTH - self.panel_width - 20
        self.panel_y = 100
        
        # Mini-map (top-left corner)
        self.mini_map_size = 150
        self.mini_map_x = 20
        self.mini_map_y = 20
        
        # Collection statistics
        self.collection_stats = {
            "total_collected": 0,
            "session_collected": 0,
            "resources_by_type": {},
            "skill_gains": {},
            "rare_finds": [],
            "collection_streaks": {}
        }
        
        # Player position for distance calculations
        self.player_pos = (0, 0)
        
        # Drag and drop state
        self.is_dragging = False
        self.drag_start_pos = (0, 0)
        self.drag_offset = (0, 0)
        self.dragging_element = None  # 'panel' or 'minimap'
        
        # Resource type icons and colors
        self.resource_icons = {
            "oak_tree": "🌳",
            "pine_tree": "🌲", 
            "stone_node": "🪨",
            "copper_node": "🟤",
            "iron_node": "⚫",
            "berry_bush": "🫐",
            "mushroom_log": "🍄",
            "herb_patch": "🌿"
        }
        
        self.resource_colors = {
            "oak_tree": (101, 67, 33),
            "pine_tree": (0, 100, 0),
            "stone_node": (128, 128, 128),
            "copper_node": (184, 115, 51),
            "iron_node": (70, 70, 70),
            "berry_bush": (138, 43, 226),
            "mushroom_log": (139, 69, 19),
            "herb_patch": (50, 205, 50)
        }
    
    def show(self, mode: str = "nearby"):
        """Show the resource tracker UI"""
        self.visible = True
        self.current_mode = mode
    
    def hide(self):
        """Hide the resource tracker UI"""
        self.visible = False
    
    def toggle(self):
        """Toggle UI visibility"""
        if self.visible:
            self.hide()
        else:
            self.show()
    
    def toggle_mini_map(self):
        """Toggle mini-map visibility"""
        self.mini_map_visible = not self.mini_map_visible
    
    def update_player_position(self, x: int, y: int):
        """Update player position for distance calculations"""
        self.player_pos = (x, y)
    
    def record_collection(self, resource_type: str, item_id: str, quantity: int, skill_exp: int):
        """Record a resource collection for statistics"""
        self.collection_stats["total_collected"] += quantity
        self.collection_stats["session_collected"] += quantity
        
        # Track by resource type
        if resource_type not in self.collection_stats["resources_by_type"]:
            self.collection_stats["resources_by_type"][resource_type] = 0
        self.collection_stats["resources_by_type"][resource_type] += quantity
        
        # Track skill gains
        skill_type = self._get_skill_for_resource(resource_type)
        if skill_type not in self.collection_stats["skill_gains"]:
            self.collection_stats["skill_gains"][skill_type] = 0
        self.collection_stats["skill_gains"][skill_type] += skill_exp
        
        # Track collection streaks
        if resource_type not in self.collection_stats["collection_streaks"]:
            self.collection_stats["collection_streaks"][resource_type] = 0
        self.collection_stats["collection_streaks"][resource_type] += 1
    
    def record_rare_find(self, item_name: str, quality: int):
        """Record a rare or high-quality find"""
        rare_find = {
            "item": item_name,
            "quality": quality,
            "timestamp": pygame.time.get_ticks()
        }
        self.collection_stats["rare_finds"].append(rare_find)
        
        # Keep only recent rare finds
        if len(self.collection_stats["rare_finds"]) > 20:
            self.collection_stats["rare_finds"] = self.collection_stats["rare_finds"][-20:]
    
    def _get_skill_for_resource(self, resource_type: str) -> str:
        """Get the skill type for a resource"""
        if resource_type in ["oak_tree", "pine_tree", "berry_bush", "mushroom_log", "herb_patch"]:
            return "foraging"
        elif resource_type in ["stone_node", "copper_node", "iron_node"]:
            return "mining"
        return "foraging"
    
    def _get_nearby_resources(self, radius: int = 200) -> List[Tuple[ResourceNode, float]]:
        """Get resources within radius of player, sorted by distance"""
        nearby = []
        player_x, player_y = self.player_pos
        
        for node in self.resources.resource_nodes:
            distance = math.sqrt((node.x - player_x) ** 2 + (node.y - player_y) ** 2)
            if distance <= radius and node.current_yield > 0:
                nearby.append((node, distance))
        
        # Sort by distance
        nearby.sort(key=lambda x: x[1])
        return nearby
    
    def _get_resource_stats(self) -> Dict:
        """Get comprehensive resource statistics"""
        total_nodes = len(self.resources.resource_nodes)
        available_nodes = sum(1 for node in self.resources.resource_nodes if node.current_yield > 0)
        depleted_nodes = total_nodes - available_nodes
        
        # Group by type
        types_count = {}
        types_available = {}
        for node in self.resources.resource_nodes:
            resource_type = node.resource_type
            if resource_type not in types_count:
                types_count[resource_type] = 0
                types_available[resource_type] = 0
            
            types_count[resource_type] += 1
            if node.current_yield > 0:
                types_available[resource_type] += 1
        
        return {
            "total_nodes": total_nodes,
            "available_nodes": available_nodes,
            "depleted_nodes": depleted_nodes,
            "types_count": types_count,
            "types_available": types_available,
            "availability_percent": (available_nodes / total_nodes * 100) if total_nodes > 0 else 0
        }
    
    def handle_event(self, event) -> bool:
        """Handle UI events"""
        if not self.visible:
            return False
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE or event.key == pygame.K_r:
                self.hide()
                return True
            elif event.key == pygame.K_1:
                self.current_mode = "nearby"
                return True
            elif event.key == pygame.K_2:
                self.current_mode = "statistics"
                return True
            elif event.key == pygame.K_3:
                self.current_mode = "map"
                return True
            elif event.key == pygame.K_m:
                self.toggle_mini_map()
                return True
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                mouse_x, mouse_y = event.pos
                
                # Check if clicking on mini-map for dragging
                if self.mini_map_visible:
                    mini_map_rect = pygame.Rect(self.mini_map_x, self.mini_map_y, self.mini_map_size, self.mini_map_size)
                    if mini_map_rect.collidepoint(mouse_x, mouse_y):
                        self.is_dragging = True
                        self.dragging_element = 'minimap'
                        self.drag_start_pos = (mouse_x, mouse_y)
                        self.drag_offset = (mouse_x - self.mini_map_x, mouse_y - self.mini_map_y)
                        return True
                
                # Check if clicking on main panel for dragging
                if self.visible:
                    panel_rect = pygame.Rect(self.panel_x, self.panel_y, self.panel_width, self.panel_height)
                    if panel_rect.collidepoint(mouse_x, mouse_y):
                        # Check if clicking on title bar for dragging
                        title_bar_rect = pygame.Rect(self.panel_x, self.panel_y, self.panel_width, 40)
                        if title_bar_rect.collidepoint(mouse_x, mouse_y):
                            self.is_dragging = True
                            self.dragging_element = 'panel'
                            self.drag_start_pos = (mouse_x, mouse_y)
                            self.drag_offset = (mouse_x - self.panel_x, mouse_y - self.panel_y)
                            return True
                        
                        # Check mode tabs
                        if self._handle_mode_tabs(mouse_x, mouse_y):
                            return True
                        
                        return True  # Consume click on panel
                    else:
                        # Clicking outside panel - close UI
                        self.hide()
                        return True
        
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1 and self.is_dragging:  # Left click release
                self.is_dragging = False
                self.dragging_element = None
                return True
        
        elif event.type == pygame.MOUSEMOTION:
            if self.is_dragging:
                mouse_x, mouse_y = event.pos
                
                if self.dragging_element == 'minimap':
                    # Update mini-map position
                    new_x = mouse_x - self.drag_offset[0]
                    new_y = mouse_y - self.drag_offset[1]
                    
                    # Keep mini-map on screen
                    self.mini_map_x = max(0, min(SCREEN_WIDTH - self.mini_map_size, new_x))
                    self.mini_map_y = max(0, min(SCREEN_HEIGHT - self.mini_map_size, new_y))
                
                elif self.dragging_element == 'panel':
                    # Update panel position
                    new_x = mouse_x - self.drag_offset[0]
                    new_y = mouse_y - self.drag_offset[1]
                    
                    # Keep panel on screen
                    self.panel_x = max(0, min(SCREEN_WIDTH - self.panel_width, new_x))
                    self.panel_y = max(0, min(SCREEN_HEIGHT - self.panel_height, new_y))
                
                return True
        
        return True  # Consume all events when visible
    
    def _handle_mode_tabs(self, mouse_x: int, mouse_y: int) -> bool:
        """Handle clicks on mode tabs"""
        tab_y = self.panel_y + 10
        tab_height = 25
        tab_width = 80
        
        modes = [("nearby", "Nearby"), ("statistics", "Stats"), ("map", "Map")]
        
        for i, (mode_id, mode_name) in enumerate(modes):
            tab_x = self.panel_x + 20 + i * (tab_width + 10)
            tab_rect = pygame.Rect(tab_x, tab_y, tab_width, tab_height)
            
            if tab_rect.collidepoint(mouse_x, mouse_y):
                self.current_mode = mode_id
                return True
        
        return False
    
    def draw(self):
        """Draw the resource tracker UI"""
        if self.mini_map_visible:
            self._draw_mini_map()
        
        if not self.visible:
            return
        
        # Main panel
        panel_rect = pygame.Rect(self.panel_x, self.panel_y, self.panel_width, self.panel_height)
        pygame.draw.rect(self.screen, self.bg_color, panel_rect, border_radius=10)
        pygame.draw.rect(self.screen, self.border_color, panel_rect, 2, border_radius=10)
        
        # Draw mode tabs
        self._draw_mode_tabs()
        
        # Draw content based on mode
        if self.current_mode == "nearby":
            self._draw_nearby_resources()
        elif self.current_mode == "statistics":
            self._draw_statistics()
        elif self.current_mode == "map":
            self._draw_resource_map()
        
        # Draw controls
        self._draw_controls()
    
    def _draw_mode_tabs(self):
        """Draw mode selection tabs"""
        tab_y = self.panel_y + 10
        tab_height = 25
        tab_width = 80
        
        modes = [("nearby", "Nearby"), ("statistics", "Stats"), ("map", "Map")]
        
        for i, (mode_id, mode_name) in enumerate(modes):
            tab_x = self.panel_x + 20 + i * (tab_width + 10)
            tab_rect = pygame.Rect(tab_x, tab_y, tab_width, tab_height)
            
            # Tab background
            is_active = self.current_mode == mode_id
            tab_color = self.accent_color if is_active else self.panel_color
            pygame.draw.rect(self.screen, tab_color, tab_rect, border_radius=5)
            pygame.draw.rect(self.screen, self.border_color, tab_rect, 2, border_radius=5)
            
            # Tab text
            text_surface = self.font_small.render(mode_name, True, self.text_color)
            text_rect = text_surface.get_rect(center=tab_rect.center)
            self.screen.blit(text_surface, text_rect)
    
    def _draw_nearby_resources(self):
        """Draw nearby resources list"""
        content_y = self.panel_y + 50
        
        # Title
        title_surface = self.font_normal.render("Nearby Resources", True, self.text_color)
        self.screen.blit(title_surface, (self.panel_x + 20, content_y))
        content_y += 30
        
        # Get nearby resources
        nearby = self._get_nearby_resources()
        
        if not nearby:
            no_resources = self.font_small.render("No resources nearby", True, self.warning_color)
            self.screen.blit(no_resources, (self.panel_x + 20, content_y))
            return
        
        # List nearby resources
        for i, (node, distance) in enumerate(nearby[:10]):  # Show top 10
            if content_y > self.panel_y + self.panel_height - 60:
                break  # Don't overflow panel
            
            # Resource icon
            icon = self.resource_icons.get(node.resource_type, "📦")
            icon_surface = self.font_small.render(icon, True, self.text_color)
            self.screen.blit(icon_surface, (self.panel_x + 20, content_y))
            
            # Resource info
            item_data = self.inventory.get_item_data(node.resource_id)
            item_name = item_data.name if item_data else node.resource_id
            
            # Distance and yield
            info_text = f"{item_name} ({int(distance)}m)"
            info_surface = self.font_small.render(info_text, True, self.text_color)
            self.screen.blit(info_surface, (self.panel_x + 40, content_y))
            
            # Yield indicator
            yield_text = f"×{node.current_yield}"
            yield_surface = self.font_small.render(yield_text, True, self.success_color)
            self.screen.blit(yield_surface, (self.panel_x + 220, content_y))
            
            # Skill requirement check
            skill_level = self.skills.get_skill_level(node.skill_type)
            if skill_level < node.required_skill_level:
                req_surface = self.font_small.render("!", True, self.warning_color)
                self.screen.blit(req_surface, (self.panel_x + 260, content_y))
            
            content_y += 20
    
    def _draw_statistics(self):
        """Draw collection statistics"""
        content_y = self.panel_y + 50
        
        # Title
        title_surface = self.font_normal.render("Collection Stats", True, self.text_color)
        self.screen.blit(title_surface, (self.panel_x + 20, content_y))
        content_y += 30
        
        stats = self.collection_stats
        
        # Overall stats
        total_surface = self.font_small.render(f"Total Collected: {stats['total_collected']}", True, self.text_color)
        self.screen.blit(total_surface, (self.panel_x + 20, content_y))
        content_y += 18
        
        session_surface = self.font_small.render(f"This Session: {stats['session_collected']}", True, self.success_color)
        self.screen.blit(session_surface, (self.panel_x + 20, content_y))
        content_y += 25
        
        # Resources by type
        if stats["resources_by_type"]:
            type_title = self.font_small.render("By Resource Type:", True, self.accent_color)
            self.screen.blit(type_title, (self.panel_x + 20, content_y))
            content_y += 18
            
            for resource_type, count in sorted(stats["resources_by_type"].items(), key=lambda x: x[1], reverse=True):
                icon = self.resource_icons.get(resource_type, "📦")
                type_text = f"{icon} {resource_type.replace('_', ' ').title()}: {count}"
                type_surface = self.font_small.render(type_text, True, self.text_color)
                self.screen.blit(type_surface, (self.panel_x + 30, content_y))
                content_y += 16
        
        # Rare finds
        content_y += 10
        if stats["rare_finds"]:
            rare_title = self.font_small.render("Recent Rare Finds:", True, self.accent_color)
            self.screen.blit(rare_title, (self.panel_x + 20, content_y))
            content_y += 18
            
            for rare_find in stats["rare_finds"][-5:]:  # Show last 5
                stars = "⭐" * rare_find["quality"]
                rare_text = f"{rare_find['item']} {stars}"
                rare_surface = self.font_small.render(rare_text, True, (255, 215, 0))
                self.screen.blit(rare_surface, (self.panel_x + 30, content_y))
                content_y += 16
    
    def _draw_resource_map(self):
        """Draw resource distribution map"""
        content_y = self.panel_y + 50
        
        # Title
        title_surface = self.font_normal.render("Resource Map", True, self.text_color)
        self.screen.blit(title_surface, (self.panel_x + 20, content_y))
        content_y += 30
        
        # Map area
        map_size = 200
        map_x = self.panel_x + (self.panel_width - map_size) // 2
        map_y = content_y
        
        # Map background
        map_rect = pygame.Rect(map_x, map_y, map_size, map_size)
        pygame.draw.rect(self.screen, (30, 30, 30), map_rect)
        pygame.draw.rect(self.screen, self.border_color, map_rect, 2)
        
        # Draw resources on map
        map_width = MAP_WIDTH if 'MAP_WIDTH' in globals() else 2000
        map_height = MAP_HEIGHT if 'MAP_HEIGHT' in globals() else 2000
        
        for node in self.resources.resource_nodes:
            if node.current_yield > 0:
                # Convert world coordinates to map coordinates
                rel_x = (node.x / map_width) * map_size
                rel_y = (node.y / map_height) * map_size
                
                dot_x = int(map_x + rel_x)
                dot_y = int(map_y + rel_y)
                
                # Color based on resource type
                color = self.resource_colors.get(node.resource_type, (255, 255, 255))
                pygame.draw.circle(self.screen, color, (dot_x, dot_y), 2)
        
        # Draw player position
        player_x, player_y = self.player_pos
        player_map_x = int(map_x + (player_x / map_width) * map_size)
        player_map_y = int(map_y + (player_y / map_height) * map_size)
        pygame.draw.circle(self.screen, (255, 100, 100), (player_map_x, player_map_y), 4)
        pygame.draw.circle(self.screen, (255, 255, 255), (player_map_x, player_map_y), 4, 2)
        
        # Legend
        legend_y = map_y + map_size + 15
        legend_items = [
            ("Trees", (101, 67, 33)),
            ("Minerals", (128, 128, 128)),
            ("Plants", (50, 205, 50)),
            ("Player", (255, 100, 100))
        ]
        
        for i, (label, color) in enumerate(legend_items):
            legend_x = map_x + (i % 2) * 100
            legend_y_pos = legend_y + (i // 2) * 15
            
            pygame.draw.circle(self.screen, color, (legend_x, legend_y_pos + 6), 3)
            label_surface = self.font_small.render(label, True, self.text_color)
            self.screen.blit(label_surface, (legend_x + 10, legend_y_pos))
    
    def _draw_mini_map(self):
        """Draw mini-map in corner"""
        # Mini-map background
        map_rect = pygame.Rect(self.mini_map_x, self.mini_map_y, self.mini_map_size, self.mini_map_size)
        pygame.draw.rect(self.screen, (20, 20, 20, 180), map_rect, border_radius=8)
        pygame.draw.rect(self.screen, self.border_color, map_rect, 2, border_radius=8)
        
        # Draw resources as small dots
        map_width = MAP_WIDTH if 'MAP_WIDTH' in globals() else 2000
        map_height = MAP_HEIGHT if 'MAP_HEIGHT' in globals() else 2000
        
        nearby = self._get_nearby_resources(300)  # Show resources within 300 units
        
        for node, distance in nearby:
            rel_x = (node.x / map_width) * self.mini_map_size
            rel_y = (node.y / map_height) * self.mini_map_size
            
            dot_x = int(self.mini_map_x + rel_x)
            dot_y = int(self.mini_map_y + rel_y)
            
            color = self.resource_colors.get(node.resource_type, (255, 255, 255))
            pygame.draw.circle(self.screen, color, (dot_x, dot_y), 1)
        
        # Draw player position
        player_x, player_y = self.player_pos
        player_map_x = int(self.mini_map_x + (player_x / map_width) * self.mini_map_size)
        player_map_y = int(self.mini_map_y + (player_y / map_height) * self.mini_map_size)
        pygame.draw.circle(self.screen, (255, 100, 100), (player_map_x, player_map_y), 3)
        
        # Title
        title_surface = self.font_small.render("Resources", True, self.text_color)
        self.screen.blit(title_surface, (self.mini_map_x + 2, self.mini_map_y + 2))
    
    def _draw_controls(self):
        """Draw control instructions"""
        controls_y = self.panel_y + self.panel_height - 35
        
        controls = "ESC/R: Close | 1-3: Modes | M: Toggle Mini-map"
        control_surface = self.font_small.render(controls, True, self.text_color)
        self.screen.blit(control_surface, (self.panel_x + 10, controls_y))
    
    def get_collection_summary(self) -> str:
        """Get a summary of current collection statistics"""
        stats = self.collection_stats
        return f"Collected: {stats['session_collected']} this session, {stats['total_collected']} total"