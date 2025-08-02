import pygame
import random
import math
from typing import List, Dict, Tuple
from src.core.constants import *
from src.graphics.custom_asset_manager import CustomAssetManager

class TerrainTile:
    def __init__(self, x: int, y: int, tile_type: str):
        self.x = x
        self.y = y
        self.tile_type = tile_type
        self.decoration = None  # Optional decoration like flowers, rocks, etc.

class Building:
    def __init__(self, x: int, y: int, building_type: str, width: int = 64, height: int = 64):
        self.x = x
        self.y = y
        self.building_type = building_type
        self.width = width
        self.height = height
        self.rect = pygame.Rect(x, y, width, height)

class NatureElement:
    def __init__(self, x: int, y: int, element_type: str):
        self.x = x
        self.y = y
        self.element_type = element_type

class BeautifulMap:
    """
    Enhanced map system with beautiful Stardew Valley-like visuals.
    Features natural terrain, pixel art buildings, and scenic elements.
    """
    
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.tile_size = 32
        
        # Initialize custom asset manager
        self.assets = CustomAssetManager()
        self.assets.list_loaded_assets()  # Debug: show what was loaded
        self.assets.preload_common_sizes()  # Preload for performance
        
        # Terrain system
        self.terrain_tiles: List[List[TerrainTile]] = []
        self.buildings: List[Building] = []
        self.nature_elements: List[NatureElement] = []
        self.paths: List[Tuple[int, int]] = []
        
        # Generation settings
        self.noise_scale = 0.1
        
        self._generate_beautiful_world()
    
    def _generate_beautiful_world(self):
        """Generate a beautiful, natural-looking world"""
        self._generate_terrain()
        self._place_buildings()
        self._create_paths()
        self._add_nature_elements()
        self._add_decorative_elements()
    
    def _generate_terrain(self):
        """Generate varied terrain using simple noise"""
        rows = self.height // self.tile_size
        cols = self.width // self.tile_size
        
        for y in range(rows):
            row = []
            for x in range(cols):
                # Simple noise-like variation for terrain
                noise_value = (
                    math.sin(x * 0.1) * math.cos(y * 0.1) +
                    math.sin(x * 0.05) * math.cos(y * 0.15) * 0.5 +
                    random.random() * 0.3
                )
                
                # Determine tile type based on noise and position
                if noise_value > 0.4:
                    tile_type = "grass"
                elif noise_value > 0.1:
                    tile_type = "grass"  # More grass for open feel
                elif noise_value > -0.2:
                    tile_type = "grass"
                else:
                    # Water areas near edges or in low-noise areas
                    if x < 3 or x > cols - 4 or y < 3 or y > rows - 4:
                        if random.random() < 0.3:
                            tile_type = "water"
                        else:
                            tile_type = "grass"
                    else:
                        tile_type = "grass"
                
                tile = TerrainTile(x * self.tile_size, y * self.tile_size, tile_type)
                
                # Add random decorations to grass tiles
                if tile_type == "grass" and random.random() < 0.08:
                    decorations = ["flowers", None, None, None]  # More likely to be empty
                    tile.decoration = random.choice(decorations)
                
                row.append(tile)
            self.terrain_tiles.append(row)
    
    def _place_buildings(self):
        """Place beautiful pixel art buildings strategically"""
        
        # Main buildings with proper spacing and placement
        building_configs = [
            # Houses - cozy residential area
            {"x": 150, "y": 150, "type": "house", "width": 64, "height": 64},
            {"x": 300, "y": 200, "type": "house", "width": 64, "height": 64},
            {"x": 450, "y": 120, "type": "house", "width": 64, "height": 64},
            {"x": 250, "y": 350, "type": "house", "width": 64, "height": 64},
            
            # Commercial buildings
            {"x": 600, "y": 180, "type": "shop", "width": 64, "height": 64},
            {"x": 550, "y": 320, "type": "shop", "width": 64, "height": 64},
            
            # Community center - larger and central
            {"x": 400, "y": 450, "type": "community_center", "width": 96, "height": 80},
        ]
        
        for config in building_configs:
            building = Building(
                config["x"], config["y"], config["type"],
                config["width"], config["height"]
            )
            self.buildings.append(building)
    
    def _create_paths(self):
        """Create natural stone paths connecting buildings"""
        
        # Define key locations to connect
        key_points = [
            (180, 180),  # House 1
            (330, 230),  # House 2  
            (480, 150),  # House 3
            (280, 380),  # House 4
            (630, 210),  # Shop 1
            (580, 350),  # Shop 2
            (450, 490),  # Community center
        ]
        
        # Create paths between nearby buildings
        connections = [
            (0, 1), (1, 2), (1, 3), (2, 4),  # House connections
            (3, 6), (4, 5), (5, 6),  # To shops and center
            (0, 6), (4, 6)  # Direct routes to community center
        ]
        
        for start_idx, end_idx in connections:
            start = key_points[start_idx]
            end = key_points[end_idx]
            self._create_path_between_points(start, end)
    
    def _create_path_between_points(self, start: Tuple[int, int], end: Tuple[int, int]):
        """Create a curved path between two points"""
        x1, y1 = start
        x2, y2 = end
        
        # Simple path - direct line with some randomness
        distance = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
        steps = int(distance // 16)  # Path point every 16 pixels
        
        for i in range(steps + 1):
            t = i / max(steps, 1)
            
            # Linear interpolation with slight curve
            curve_offset = math.sin(t * math.pi) * 20  # Slight arc
            
            x = int(x1 + (x2 - x1) * t + random.randint(-8, 8))
            y = int(y1 + (y2 - y1) * t + curve_offset + random.randint(-8, 8))
            
            # Add path tiles around this point
            for dy in range(-1, 2):
                for dx in range(-1, 2):
                    px = x + dx * 16
                    py = y + dy * 16
                    if 0 <= px < self.width and 0 <= py < self.height:
                        self.paths.append((px, py))
    
    def _add_nature_elements(self):
        """Add trees, flowers, and other natural elements"""
        
        # Trees - scattered around but not blocking paths
        tree_positions = [
            (100, 80), (80, 200), (120, 300),
            (350, 80), (380, 120), (320, 290),
            (500, 80), (550, 120), (480, 280),
            (200, 500), (350, 550), (500, 520),
            (700, 100), (750, 200), (720, 300),
            (650, 450), (700, 500), (600, 580),
        ]
        
        for x, y in tree_positions:
            # Only place if not too close to buildings
            too_close = False
            for building in self.buildings:
                if (abs(building.x - x) < 80 and abs(building.y - y) < 80):
                    too_close = True
                    break
            
            if not too_close:
                self.nature_elements.append(NatureElement(x, y, "tree"))
        
        # Flower patches in open areas
        for _ in range(15):
            x = random.randint(100, self.width - 100)
            y = random.randint(100, self.height - 100)
            
            # Check distance from buildings and paths
            valid_spot = True
            for building in self.buildings:
                if (abs(building.x - x) < 60 and abs(building.y - y) < 60):
                    valid_spot = False
                    break
            
            if valid_spot:
                self.nature_elements.append(NatureElement(x, y, "flowers"))
        
        # Fence sections for charm
        fence_positions = [
            (50, 150), (50, 200), (50, 250),  # Left border
            (750, 200), (750, 250), (750, 300),  # Right sections
        ]
        
        for x, y in fence_positions:
            self.nature_elements.append(NatureElement(x, y, "fence"))
    
    def _add_decorative_elements(self):
        """Add decorative elements that enhance the world's beauty"""
        
        # Add some scattered rocks and details
        for _ in range(20):
            x = random.randint(50, self.width - 50)
            y = random.randint(50, self.height - 50)
            
            # Only place if not blocking paths or near buildings
            valid = True
            for building in self.buildings:
                if (abs(building.x - x) < 50 and abs(building.y - y) < 50):
                    valid = False
                    break
            
            if valid and random.random() < 0.3:
                # Small decorative elements can be added here
                pass  # Placeholder for future decorations
    
    def get_tile_at(self, world_x: int, world_y: int) -> TerrainTile:
        """Get the terrain tile at world coordinates"""
        tile_x = world_x // self.tile_size
        tile_y = world_y // self.tile_size
        
        if 0 <= tile_y < len(self.terrain_tiles) and 0 <= tile_x < len(self.terrain_tiles[0]):
            return self.terrain_tiles[tile_y][tile_x]
        
        # Default grass tile for out of bounds
        return TerrainTile(tile_x * self.tile_size, tile_y * self.tile_size, "grass")
    
    def is_building_at(self, x: int, y: int) -> bool:
        """Check if there's a building at the given coordinates"""
        point = pygame.Rect(x, y, 1, 1)
        for building in self.buildings:
            if building.rect.colliderect(point):
                return True
        return False
    
    def draw(self, screen: pygame.Surface, camera):
        """Draw the beautiful map with all its elements"""
        
        # Calculate visible area
        visible_rect = pygame.Rect(
            -camera.camera.x, -camera.camera.y,
            camera.width + self.tile_size, camera.height + self.tile_size
        )
        
        # Draw terrain tiles
        self._draw_terrain(screen, camera, visible_rect)
        
        # Draw paths
        self._draw_paths(screen, camera, visible_rect)
        
        # Draw nature elements (behind buildings)
        self._draw_nature_elements(screen, camera, visible_rect)
        
        # Draw buildings
        self._draw_buildings(screen, camera, visible_rect)
    
    def _draw_terrain(self, screen: pygame.Surface, camera, visible_rect: pygame.Rect):
        """Draw terrain tiles with beautiful textures"""
        start_x = max(0, visible_rect.left // self.tile_size)
        end_x = min(len(self.terrain_tiles[0]), (visible_rect.right // self.tile_size) + 1)
        start_y = max(0, visible_rect.top // self.tile_size)
        end_y = min(len(self.terrain_tiles), (visible_rect.bottom // self.tile_size) + 1)
        
        for y in range(start_y, end_y):
            for x in range(start_x, end_x):
                if y < len(self.terrain_tiles) and x < len(self.terrain_tiles[y]):
                    tile = self.terrain_tiles[y][x]
                    
                    # Get tile position on screen
                    tile_rect = pygame.Rect(tile.x, tile.y, self.tile_size, self.tile_size)
                    screen_rect = camera.apply_rect(tile_rect)
                    
                    # Draw base terrain with variety
                    if tile.tile_type == "grass":
                        # Use different grass variants for visual variety
                        variant_num = (x + y) % 4
                        if variant_num == 0:
                            texture = self.assets.get_texture("grass")
                        else:
                            texture = self.assets.get_texture(f"grass_variant_{variant_num-1}")
                            if not texture:
                                texture = self.assets.get_texture("grass")
                    else:
                        texture = self.assets.get_texture(tile.tile_type)
                    
                    if texture:
                        screen.blit(texture, screen_rect)
                    else:
                        # Fallback colors
                        color = GREEN if tile.tile_type == "grass" else (64, 164, 223)
                        pygame.draw.rect(screen, color, screen_rect)
                    
                    # Draw decorations
                    if tile.decoration:
                        decoration_sprite = self.assets.get_sprite(tile.decoration)
                        if decoration_sprite:
                            # Center decoration in tile
                            dec_rect = decoration_sprite.get_rect()
                            dec_rect.center = screen_rect.center
                            screen.blit(decoration_sprite, dec_rect)
    
    def _draw_paths(self, screen: pygame.Surface, camera, visible_rect: pygame.Rect):
        """Draw stone paths using proper path textures"""
        path_straight = self.assets.get_texture("path_straight")
        path_corner = self.assets.get_texture("path_corner")
        
        for path_x, path_y in self.paths:
            path_rect = pygame.Rect(path_x, path_y, self.tile_size, self.tile_size)
            if visible_rect.colliderect(path_rect):
                screen_rect = camera.apply_rect(path_rect)
                
                # Use straight path texture by default, could be enhanced with path direction logic
                path_texture = path_straight if path_straight else path_corner
                
                if path_texture:
                    screen.blit(path_texture, screen_rect)
                else:
                    # Fallback to colored rectangle
                    pygame.draw.rect(screen, (150, 140, 120), screen_rect)
    
    def _draw_nature_elements(self, screen: pygame.Surface, camera, visible_rect: pygame.Rect):
        """Draw trees, flowers, and other nature elements"""
        for element in self.nature_elements:
            element_sprite = self.assets.get_sprite(element.element_type)
            if element_sprite:
                element_rect = pygame.Rect(
                    element.x, element.y,
                    element_sprite.get_width(), element_sprite.get_height()
                )
                
                if visible_rect.colliderect(element_rect):
                    screen_rect = camera.apply_rect(element_rect)
                    screen.blit(element_sprite, screen_rect)
    
    def _draw_buildings(self, screen: pygame.Surface, camera, visible_rect: pygame.Rect):
        """Draw beautiful pixel art buildings"""
        for building in self.buildings:
            if visible_rect.colliderect(building.rect):
                building_sprite = self.assets.get_sprite(building.building_type)
                if building_sprite:
                    screen_rect = camera.apply_rect(building.rect)
                    screen.blit(building_sprite, screen_rect)
                else:
                    # Fallback colored rectangle
                    screen_rect = camera.apply_rect(building.rect)
                    fallback_colors = {
                        "house": (139, 69, 19),
                        "shop": (100, 100, 200),
                        "community_center": (178, 34, 34)
                    }
                    color = fallback_colors.get(building.building_type, GRAY)
                    pygame.draw.rect(screen, color, screen_rect)
                    pygame.draw.rect(screen, BLACK, screen_rect, 2)