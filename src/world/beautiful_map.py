import pygame
import random
import math
from typing import List, Dict, Tuple
import src.core.constants as constants
from src.core.constants import GRAY, BLACK
from src.graphics.custom_asset_manager import CustomAssetManager

class TerrainTile:
    def __init__(self, x: int, y: int, tile_type: str):
        self.x = x
        self.y = y
        self.tile_type = tile_type
        self.decoration = None  # Optional decoration like flowers, rocks, etc.
        self.cached_texture = None  # Cache texture to avoid repeated lookups
        self.cached_decoration_sprite = None  # Cache decoration sprite

class Building:
    def __init__(self, x: int, y: int, building_type: str, width: int = 64, height: int = 64, interactable: bool = False):
        self.x = x
        self.y = y
        self.building_type = building_type
        self.width = width
        self.height = height
        self.interactable = interactable
        self.rect = pygame.Rect(x, y, width, height)

class NatureElement:
    def __init__(self, x: int, y: int, element_type: str):
        self.x = x
        self.y = y
        self.element_type = element_type
        
        # For trees, assign a specific tree type to prevent rotation
        if element_type == "tree":
            available_trees = ["tree_1", "tree_2", "tree_3", "tree_4"]
            self.specific_tree_type = random.choice(available_trees)
        else:
            self.specific_tree_type = None

class BeautifulMap:
    """
    Enhanced map system with beautiful Stardew Valley-like visuals.
    Features natural terrain, pixel art buildings, and scenic elements.
    """
    
    def __init__(self, width: int, height: int, custom_settings: dict = None):
        self.width = width
        self.height = height
        self.tile_size = 32
        
        # Apply custom world settings
        self.custom_settings = custom_settings or {}
        self._apply_world_size_settings()
        
        # Initialize custom asset manager
        self.assets = CustomAssetManager()
        # self.assets.list_loaded_assets()  # Debug: show what was loaded
        self.assets.preload_common_sizes()  # Preload for performance
        
        # Performance optimizations
        self.background_cache = None
        self.last_camera_pos = None
        self.visible_objects_cache = {}
        
        # TILESET PERFORMANCE: Load and cache tileset once
        self.tileset_cache = {}
        self._load_tileset()
        
        # Terrain system
        self.terrain_tiles: List[List[TerrainTile]] = []
        self.buildings: List[Building] = []
        self.nature_elements: List[NatureElement] = []
        self.paths: List[Tuple[int, int]] = []
        
        # Generation settings
        self.noise_scale = 0.1
        
        self._generate_beautiful_world()
    
    def _apply_world_size_settings(self):
        """Apply world size customization"""
        world_size = self.custom_settings.get('world_size', 'medium')
        
        if world_size == 'small':
            self.width = int(self.width * 0.7)
            self.height = int(self.height * 0.7)
        elif world_size == 'large':
            self.width = int(self.width * 1.5)
            self.height = int(self.height * 1.5)
    
    def _load_tileset(self):
        """Load and cache tileset sprites for maximum performance"""
        import pygame
        import os
        
        tileset_path = "images/nature/environment/grasstileset.png"
        
        if not os.path.exists(tileset_path):
            print(f"Tileset not found: {tileset_path}")
            return
        
        try:
            # Load the tileset image
            tileset = pygame.image.load(tileset_path).convert_alpha()
            
            # Each tile is 32x32 pixels but we need to account for borders
            # The tileset has 1px black borders around each tile
            tile_width = 32
            tile_height = 32
            border = 1  # Black border size
            
            # Pre-cut and cache all tiles we'll need (skip borders)
            # Row 0: Grass variants (0-7)
            for i in range(8):
                x = i * (tile_width + border) + border  # Skip left border
                y = 0 * (tile_height + border) + border  # Skip top border
                # Extract only the content without borders
                tile_surface = tileset.subsurface(pygame.Rect(x, y, tile_width - border, tile_height - border)).copy()
                # Scale to full tile size
                tile_surface = pygame.transform.scale(tile_surface, (tile_width, tile_height))
                self.tileset_cache[f'grass_{i}'] = tile_surface
            
            # Row 1: More grass variants (8-15)  
            for i in range(8):
                x = i * (tile_width + border) + border
                y = 1 * (tile_height + border) + border
                tile_surface = tileset.subsurface(pygame.Rect(x, y, tile_width - border, tile_height - border)).copy()
                tile_surface = pygame.transform.scale(tile_surface, (tile_width, tile_height))
                self.tileset_cache[f'grass_{i+8}'] = tile_surface
            
            # Row 2: Dirt/path tiles (16-23)
            for i in range(3):
                x = i * (tile_width + border) + border
                y = 2 * (tile_height + border) + border
                tile_surface = tileset.subsurface(pygame.Rect(x, y, tile_width - border, tile_height - border)).copy()
                tile_surface = pygame.transform.scale(tile_surface, (tile_width, tile_height))
                self.tileset_cache[f'dirt_{i}'] = tile_surface
            
            # Water tiles (blue ones)
            for i in range(3):
                x = (i + 5) * (tile_width + border) + border
                y = 2 * (tile_height + border) + border
                tile_surface = tileset.subsurface(pygame.Rect(x, y, tile_width - border, tile_height - border)).copy()
                tile_surface = pygame.transform.scale(tile_surface, (tile_width, tile_height))
                self.tileset_cache[f'water_{i}'] = tile_surface
            
            # Stone tiles (gray ones)
            for i in range(2):
                x = (i + 3) * (tile_width + border) + border
                y = 2 * (tile_height + border) + border
                tile_surface = tileset.subsurface(pygame.Rect(x, y, tile_width - border, tile_height - border)).copy()
                tile_surface = pygame.transform.scale(tile_surface, (tile_width, tile_height))
                self.tileset_cache[f'stone_{i}'] = tile_surface
            
            print(f"✅ Loaded {len(self.tileset_cache)} tileset sprites from {tileset_path}")
            
        except Exception as e:
            print(f"❌ Failed to load tileset: {e}")
            # Fallback: create simple colored tiles
            self._create_fallback_tiles()
    
    def _create_fallback_tiles(self):
        """Create simple colored tiles as fallback"""
        import pygame
        
        # Create basic colored tiles
        tile_size = 32
        
        # Grass tile
        grass_tile = pygame.Surface((tile_size, tile_size))
        grass_tile.fill((34, 139, 34))
        self.tileset_cache['grass_0'] = grass_tile
        
        # Dirt tile  
        dirt_tile = pygame.Surface((tile_size, tile_size))
        dirt_tile.fill((139, 69, 19))
        self.tileset_cache['dirt_0'] = dirt_tile
        
        # Water tile
        water_tile = pygame.Surface((tile_size, tile_size))
        water_tile.fill((64, 164, 223))
        self.tileset_cache['water_0'] = water_tile
        
        print("✅ Created fallback colored tiles")
    
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
                
                # Don't cache texture during creation - do it lazily during rendering
                
                # Add random decorations to grass tiles
                if tile_type == "grass" and random.random() < 0.08:
                    decorations = ["flowers", None, None, None]  # More likely to be empty
                    tile.decoration = random.choice(decorations)
                    # Don't cache decoration sprite during creation - do it lazily
                
                row.append(tile)
            self.terrain_tiles.append(row)
    
    def _place_buildings(self):
        """Place beautiful pixel art buildings strategically"""
        
        # Apply building density setting
        building_density = self.custom_settings.get('building_density', 0.6)
        
        # Main buildings spread across the entire map for exploration
        building_configs = [
            # Player's house - starting area (northwest)
            {"x": 300, "y": 300, "type": "player_house", "width": 64, "height": 64, "interactable": True},
            
            # Shops near player spawn area
            {"x": 450, "y": 280, "type": "gem_shop", "width": 64, "height": 64, "interactable": True},
            {"x": 380, "y": 400, "type": "hardware_store", "width": 64, "height": 64, "interactable": True},
            {"x": 520, "y": 380, "type": "mining_store", "width": 64, "height": 64, "interactable": True},
            
            # Residential areas spread across different regions
            {"x": 800, "y": 400, "type": "house", "width": 64, "height": 64},  # West-central
            {"x": 1600, "y": 250, "type": "house", "width": 64, "height": 64},  # Northeast
            {"x": 500, "y": 1000, "type": "house", "width": 64, "height": 64},  # Southwest
            {"x": 2000, "y": 800, "type": "house", "width": 64, "height": 64},  # Far east
            {"x": 1200, "y": 1500, "type": "house", "width": 64, "height": 64},  # South-central
            {"x": 400, "y": 1600, "type": "house", "width": 64, "height": 64},  # Deep southwest
            {"x": 2100, "y": 400, "type": "house", "width": 64, "height": 64},  # Far northeast
            {"x": 2200, "y": 600, "type": "mansion", "width": 128, "height": 96},  # Wealthy family mansion
            
            # Commercial district (central area)
            {"x": 1200, "y": 900, "type": "shop", "width": 64, "height": 64},  # Central market
            {"x": 1400, "y": 950, "type": "shop", "width": 64, "height": 64},  # Market area
            {"x": 1300, "y": 1050, "type": "shop", "width": 64, "height": 64},  # Shopping district
            
            # Community buildings (strategic locations)
            {"x": 1200, "y": 1200, "type": "community_center", "width": 96, "height": 80},  # Central hub
            {"x": 1800, "y": 1400, "type": "townhall", "width": 80, "height": 80},  # Eastern town
            {"x": 600, "y": 1500, "type": "school", "width": 80, "height": 64},  # Southern district
            
            # Remote facilities
            {"x": 2000, "y": 1000, "type": "hospital", "width": 80, "height": 64},  # Eastern medical
            {"x": 300, "y": 1400, "type": "farm", "width": 96, "height": 80},  # Western farming
        ]
        
        for config in building_configs:
            building = Building(
                config["x"], config["y"], config["type"],
                config["width"], config["height"],
                config.get("interactable", False)
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
        
        # Trees will now be handled by the resource system for harvesting
        # Store tree positions spread across the entire map for exploration
        self.tree_positions = [
            # Northwest forest cluster
            (150, 100), (180, 120), (120, 150), (200, 80), (250, 130),
            (300, 100), (350, 140), (280, 180), (220, 200), (320, 200),
            
            # Northeast woodland
            (1300, 100), (1350, 150), (1400, 120), (1500, 180), (1550, 140),
            (1600, 200), (1650, 160), (1480, 220), (1520, 250), (1580, 280),
            
            # Central scattered trees
            (700, 400), (750, 450), (800, 380), (850, 420), (900, 380),
            (950, 450), (1050, 400), (1100, 380), (1150, 430), (1200, 400),
            
            # Southwest forest
            (200, 1000), (250, 1050), (180, 1100), (300, 1080), (350, 1120),
            (400, 1000), (280, 1150), (320, 1200), (380, 1180), (150, 1200),
            
            # Southeast grove
            (1400, 1300), (1450, 1350), (1500, 1280), (1550, 1320), (1600, 1380),
            (1480, 1400), (1520, 1450), (1580, 1420), (1650, 1400), (1700, 1350),
            
            # Eastern strip
            (1700, 400), (1750, 450), (1680, 500), (1720, 550), (1780, 520),
            (1650, 600), (1700, 650), (1750, 600), (1800, 580), (1680, 700),
            
            # Southern belt
            (600, 1600), (650, 1650), (700, 1620), (750, 1680), (800, 1650),
            (900, 1700), (950, 1650), (1000, 1680), (1100, 1650), (1150, 1700),
            
            # Scattered individual trees
            (500, 600), (1300, 500), (600, 1200), (1400, 800), (800, 1400),
            (400, 400), (1600, 1000), (300, 1800), (1800, 200), (100, 1600)
        ]
        
        # Flower patches spread across the entire map
        for _ in range(40):  # More flowers across larger area
            x = random.randint(100, self.width - 100)
            y = random.randint(100, self.height - 100)
            
            # Check distance from buildings and paths
            valid_spot = True
            for building in self.buildings:
                if (abs(building.x - x) < 80 and abs(building.y - y) < 80):
                    valid_spot = False
                    break
            
            if valid_spot:
                self.nature_elements.append(NatureElement(x, y, "flowers"))
        
        # Fence sections spread around different areas
        fence_positions = [
            # Northwest area
            (50, 250), (50, 300), (50, 350),
            (100, 50), (150, 50), (200, 50),
            
            # Northeast boundaries
            (1850, 150), (1850, 200), (1850, 250),
            (1600, 50), (1650, 50), (1700, 50),
            
            # Central area boundaries
            (950, 750), (950, 800), (950, 850),
            (1050, 750), (1050, 800), (1050, 850),
            
            # Southern boundaries
            (200, 1850), (250, 1850), (300, 1850),
            (1500, 1850), (1550, 1850), (1600, 1850),
            
            # Scattered decorative fences
            (500, 500), (1200, 700), (800, 1100), (1400, 400),
        ]
        
        for x, y in fence_positions:
            self.nature_elements.append(NatureElement(x, y, "fence"))
    
    def _add_decorative_elements(self):
        """Add decorative elements that enhance the world's beauty"""
        
        # Add scattered decorative rocks and details across the map
        for _ in range(50):  # More decorative elements spread across larger area
            x = random.randint(50, self.width - 50)
            y = random.randint(50, self.height - 50)
            
            # Only place if not blocking paths or near buildings
            valid = True
            for building in self.buildings:
                if (abs(building.x - x) < 70 and abs(building.y - y) < 70):
                    valid = False
                    break
            
            if valid and random.random() < 0.4:
                # Add variety of decorative elements
                decoration_type = random.choice(["small_rock", "flowers", "grass_tuft"])
                # For now, we'll just add them as nature elements
                # Future: could add specific decorative sprites
    
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
    
    def get_building_at(self, x: int, y: int):
        """Get the building at the given coordinates"""
        point = pygame.Rect(x, y, 1, 1)
        for building in self.buildings:
            if building.rect.colliderect(point):
                return building
        return None
    
    def get_player_house(self):
        """Get the player's house building"""
        for building in self.buildings:
            if building.building_type == "player_house":
                return building
        return None
    
    def draw(self, screen: pygame.Surface, camera):
        """Draw the beautiful map with all its elements - optimized"""
        
        # Calculate visible area with buffer for smooth scrolling
        buffer = self.tile_size * 2
        visible_rect = pygame.Rect(
            -camera.camera.x - buffer, -camera.camera.y - buffer,
            camera.width + buffer * 2, camera.height + buffer * 2
        )
        
        # Check if camera moved significantly (optimize by reducing redraws)
        camera_pos = (camera.camera.x, camera.camera.y)
        if (self.last_camera_pos is None or 
            abs(camera_pos[0] - self.last_camera_pos[0]) > 50 or 
            abs(camera_pos[1] - self.last_camera_pos[1]) > 50):
            
            # PERFORMANCE FIX: Disable expensive scene backgrounds
            self.last_camera_pos = camera_pos
        
        # Draw balanced elements for good performance with visuals
        self._draw_terrain(screen, camera, visible_rect)  # Restore terrain
        self._draw_paths(screen, camera, visible_rect)    # Restore paths
        self._draw_nature_elements(screen, camera, visible_rect)  # Enable nature with optimization
        self._draw_buildings(screen, camera, visible_rect)  # Keep buildings
    
    def _draw_scene_background(self, screen: pygame.Surface, camera, visible_rect: pygame.Rect):
        """Draw full-scene background images if available"""
        # Check for scene backgrounds and draw them behind everything else
        scene_background = self.assets.get_scene_background("village_scene")
        
        if scene_background:
            # Scale background to cover the visible area or use as-is
            bg_rect = pygame.Rect(0, 0, scene_background.get_width(), scene_background.get_height())
            screen_rect = camera.apply_rect(bg_rect)
            
            # Only draw if the background intersects with visible area
            if visible_rect.colliderect(bg_rect):
                screen.blit(scene_background, screen_rect)
        else:
            # Try other scene backgrounds based on location
            scene_backgrounds = ["farm_field", "village_square", "farm_path"]
            for scene_name in scene_backgrounds:
                scene_bg = self.assets.get_scene_background(scene_name)
                if scene_bg:
                    bg_rect = pygame.Rect(0, 0, scene_bg.get_width(), scene_bg.get_height())
                    screen_rect = camera.apply_rect(bg_rect)
                    if visible_rect.colliderect(bg_rect):
                        screen.blit(scene_bg, screen_rect)
                    break  # Use first available scene background
    
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
                    
                    # CLEAN MODERN LOOK: Use smooth solid colors instead of pixelated textures
                    if tile.tile_type == "grass":
                        # Clean grass green with subtle variation
                        base_green = 85 + ((x + y) % 20)  # Slight variation
                        color = (34, base_green + 54, 34)  # (34, 139, 34) base
                    elif tile.tile_type == "water":
                        color = (64, 164, 223)  # Clean blue
                    else:
                        color = (139, 115, 85)  # Clean brown/dirt
                    
                    pygame.draw.rect(screen, color, screen_rect)
                    
                    # PERFORMANCE FIX: Disable decorations completely
                    # Skip all decoration rendering for maximum performance
    
    def _draw_paths(self, screen: pygame.Surface, camera, visible_rect: pygame.Rect):
        """Draw clean stone paths"""
        for path_x, path_y in self.paths:
            path_rect = pygame.Rect(path_x, path_y, self.tile_size, self.tile_size)
            if visible_rect.colliderect(path_rect):
                screen_rect = camera.apply_rect(path_rect)
                
                # Clean stone path color
                pygame.draw.rect(screen, (180, 180, 180), screen_rect)  # Light gray stone
    
    def _draw_nature_elements(self, screen: pygame.Surface, camera, visible_rect: pygame.Rect):
        """Draw trees, flowers, and other nature elements - optimized"""
        # First draw trees from the hardcoded positions (these are the resource trees)
        for i, (tree_x, tree_y) in enumerate(self.tree_positions):
            tree_rect = pygame.Rect(tree_x, tree_y, 32, 32)  # Standard tree size
            if visible_rect.colliderect(tree_rect):
                # Use deterministic tree type based on position to prevent rotation
                tree_types = ["tree_1", "tree_2", "tree_3", "tree_4"]
                tree_type = tree_types[i % len(tree_types)]
                tree_sprite = self.assets.get_sprite(tree_type)
                
                if not tree_sprite:
                    # Fallback to any available tree
                    tree_sprite = self.assets.get_sprite("tree")
                    
                if tree_sprite:
                    screen_rect = camera.apply_rect(tree_rect)
                    screen.blit(tree_sprite, screen_rect)
        
        # Then draw other nature elements (including decorative trees) with culling
        drawn_count = 0
        max_nature_elements = 20  # Limit for performance
        
        for element in self.nature_elements:
            if drawn_count >= max_nature_elements:
                break
                
            # For trees, use their assigned specific type
            if element.element_type == "tree":
                if hasattr(element, 'specific_tree_type') and element.specific_tree_type:
                    element_sprite = self.assets.get_sprite(element.specific_tree_type)
                else:
                    element_sprite = self.assets.get_sprite("tree_1")  # Default fallback
            else:
                element_sprite = self.assets.get_sprite(element.element_type)
            
            if element_sprite:
                element_rect = pygame.Rect(
                    element.x, element.y,
                    element_sprite.get_width(), element_sprite.get_height()
                )
                
                if visible_rect.colliderect(element_rect):
                    screen_rect = camera.apply_rect(element_rect)
                    screen.blit(element_sprite, screen_rect)
                    drawn_count += 1
    
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
                        "community_center": (178, 34, 34),
                        "mansion": (184, 134, 11)  # Golden/luxury color for mansion
                    }
                    color = fallback_colors.get(building.building_type, GRAY)
                    pygame.draw.rect(screen, color, screen_rect)
                    pygame.draw.rect(screen, BLACK, screen_rect, 2)
    
