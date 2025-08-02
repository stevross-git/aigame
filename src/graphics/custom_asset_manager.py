import pygame
import os
from typing import Dict, Optional
from src.core.constants import *

class CustomAssetManager:
    """
    Asset manager that loads beautiful custom Stardew Valley-style images
    from the ./images directory instead of generating programmatic pixel art.
    """
    
    def __init__(self):
        self.sprites: Dict[str, pygame.Surface] = {}
        self.textures: Dict[str, pygame.Surface] = {}
        self.icons: Dict[str, pygame.Surface] = {}
        self.tilesets: Dict[str, pygame.Surface] = {}
        
        # Asset caching for performance
        self._scaled_cache: Dict[str, pygame.Surface] = {}
        self._cache_max_size = 100  # Limit cache size
        
        # Path to custom images
        self.images_dir = "./images"
        
        if not os.path.exists(self.images_dir):
            print(f"Warning: Images directory '{self.images_dir}' not found!")
            return
        
        self._load_all_assets()
    
    def _load_all_assets(self):
        """Load all custom assets from the images directory"""
        self._load_terrain_and_tilesets()
        self._load_buildings()
        self._load_characters()
        self._load_ui_elements()
        self._create_fallback_assets()
    
    def _load_terrain_and_tilesets(self):
        """Load terrain textures and tilesets"""
        
        # Load grass tileset
        grass_path = os.path.join(self.images_dir, "grasstileset.png")
        if os.path.exists(grass_path):
            grass_tileset = pygame.image.load(grass_path).convert_alpha()
            self.tilesets["grass_tileset"] = grass_tileset
            
            # Extract individual grass tiles (assuming 32x32 tiles)
            tile_size = 32
            grass_tiles = []
            tileset_width = grass_tileset.get_width() // tile_size
            tileset_height = grass_tileset.get_height() // tile_size
            
            for y in range(min(4, tileset_height)):  # Get first 4 rows
                for x in range(min(4, tileset_width)):  # Get first 4 columns
                    tile_rect = pygame.Rect(x * tile_size, y * tile_size, tile_size, tile_size)
                    tile_surface = pygame.Surface((tile_size, tile_size), pygame.SRCALPHA)
                    tile_surface.blit(grass_tileset, (0, 0), tile_rect)
                    grass_tiles.append(tile_surface)
            
            # Use first tile as main grass texture
            if grass_tiles:
                self.textures["grass"] = grass_tiles[0]
                # Store additional grass variants
                for i, tile in enumerate(grass_tiles[1:5]):  # Store up to 4 variants
                    self.textures[f"grass_variant_{i}"] = tile
        
        # Load mountain/terrain for decorative elements
        mountain_path = os.path.join(self.images_dir, "mountian.png")  # Note the typo in filename
        if os.path.exists(mountain_path):
            mountain_img = pygame.image.load(mountain_path).convert_alpha()
            # Scale down for use as terrain decoration
            mountain_scaled = pygame.transform.scale(mountain_img, (64, 64))
            self.sprites["mountain"] = mountain_scaled
        
        # Load fences and walls
        fences_path = os.path.join(self.images_dir, "fences, walls, bridges.png")
        if os.path.exists(fences_path):
            fences_img = pygame.image.load(fences_path).convert_alpha()
            self.tilesets["fences"] = fences_img
            
            # Extract fence pieces (assuming tileset format)
            fence_size = 32
            if fences_img.get_width() >= fence_size and fences_img.get_height() >= fence_size:
                fence_rect = pygame.Rect(0, 0, fence_size, fence_size)
                fence_surface = pygame.Surface((fence_size, fence_size), pygame.SRCALPHA)
                fence_surface.blit(fences_img, (0, 0), fence_rect)
                self.sprites["fence"] = fence_surface
    
    def _load_buildings(self):
        """Load building sprites from custom images"""
        
        building_mappings = {
            "house": "house.png",
            "house_small": "house.png",
            "house_large": "2storybuilding.png",
            "shop": "shop.png", 
            "market_hall": "townhall.png",
            "community_center": "townhall.png",
            "hospital": "hospital.png",
            "school": "school.png",
            "restaurant": "restaurant.png",
            "office": "office.png",
            "2story": "2storybuilding.png"
        }
        
        for building_type, filename in building_mappings.items():
            file_path = os.path.join(self.images_dir, filename)
            if os.path.exists(file_path):
                try:
                    building_img = pygame.image.load(file_path).convert_alpha()
                    # Scale buildings to appropriate size for game (64x64 or larger)
                    if building_type == "community_center":
                        # Community center can be larger
                        scaled_img = pygame.transform.scale(building_img, (96, 80))
                    else:
                        # Standard building size
                        scaled_img = pygame.transform.scale(building_img, (64, 64))
                    
                    self.sprites[building_type] = scaled_img
                    print(f"Loaded {building_type}: {filename}")
                except pygame.error as e:
                    print(f"Error loading {filename}: {e}")
    
    def _load_characters(self):
        """Load character sprites from custom images"""
        
        character_mappings = {
            "female": "females.png",
            "females": "females.png", 
            "girl1": "girl1.png",
            "male": "male.png",
            "walking": "walking.png",
            "professionals": "professionalpeople.png",
            "npc_idle": "male.png",
            "npc_walk": "walking.png"
        }
        
        for char_type, filename in character_mappings.items():
            file_path = os.path.join(self.images_dir, filename)
            if os.path.exists(file_path):
                try:
                    char_img = pygame.image.load(file_path).convert_alpha()
                    
                    # Handle different character image types
                    if "females" in filename or "walking" in filename or "professionals" in filename:
                        # These might be spritesheets - extract individual characters
                        char_width = 24
                        char_height = 32
                        
                        # Try to extract multiple characters from spritesheet
                        sheet_width = char_img.get_width()
                        sheet_height = char_img.get_height()
                        
                        chars_per_row = max(1, sheet_width // char_width)
                        chars_per_col = max(1, sheet_height // char_height)
                        
                        characters = []
                        for row in range(min(2, chars_per_col)):  # Max 2 rows
                            for col in range(min(4, chars_per_row)):  # Max 4 columns
                                char_rect = pygame.Rect(
                                    col * char_width, row * char_height, 
                                    char_width, char_height
                                )
                                if char_rect.right <= sheet_width and char_rect.bottom <= sheet_height:
                                    char_surface = pygame.Surface((char_width, char_height), pygame.SRCALPHA)
                                    char_surface.blit(char_img, (0, 0), char_rect)
                                    characters.append(char_surface)
                        
                        # Store individual characters
                        if characters:
                            self.sprites[char_type] = characters[0]  # First character as default
                            for i, char in enumerate(characters[1:4]):  # Store up to 3 more
                                self.sprites[f"{char_type}_{i}"] = char
                    
                    else:
                        # Single character image
                        scaled_char = pygame.transform.scale(char_img, (24, 32))
                        self.sprites[char_type] = scaled_char
                    
                    print(f"Loaded character: {filename}")
                except pygame.error as e:
                    print(f"Error loading {filename}: {e}")
        
        # Map characters to specific NPCs
        self._map_characters_to_npcs()
        
        # Create portrait versions
        self._create_portraits()
    
    def _map_characters_to_npcs(self):
        """Map loaded character sprites to specific NPCs"""
        
        # Create character mappings for our NPCs
        character_assignments = {
            "alice": "female",
            "bob": "male", 
            "charlie": "male",
            "diana": "girl1",
            "player": "walking"
        }
        
        for npc_name, char_type in character_assignments.items():
            if char_type in self.sprites:
                self.sprites[npc_name] = self.sprites[char_type]
            elif f"{char_type}_0" in self.sprites:
                self.sprites[npc_name] = self.sprites[f"{char_type}_0"]
    
    def _create_portraits(self):
        """Create small portrait versions of character sprites for UI"""
        portrait_size = (24, 24)
        
        # Create portraits for all character sprites
        character_sprites = ["alice", "bob", "charlie", "diana", "female", "male", "girl1"]
        
        for char_name in character_sprites:
            if char_name in self.sprites:
                # Create a small portrait version
                original = self.sprites[char_name]
                portrait = pygame.transform.scale(original, portrait_size)
                self.sprites[f"npc_portrait_{char_name}"] = portrait
        
        # Create generic portraits if specific ones don't exist
        if "male" in self.sprites:
            for name in ["bob", "charlie"]:
                if f"npc_portrait_{name}" not in self.sprites:
                    portrait = pygame.transform.scale(self.sprites["male"], portrait_size)
                    self.sprites[f"npc_portrait_{name}"] = portrait
        
        if "female" in self.sprites:
            for name in ["alice", "diana"]:
                if f"npc_portrait_{name}" not in self.sprites:
                    portrait = pygame.transform.scale(self.sprites["female"], portrait_size)
                    self.sprites[f"npc_portrait_{name}"] = portrait
    
    def _load_ui_elements(self):
        """Load UI elements and create icons"""
        
        ui_mappings = {
            "menu": "menu.png",
            "settings": "settings.png", 
            "skills": "skills.png",
            "tools": "tools.png"
        }
        
        for ui_type, filename in ui_mappings.items():
            file_path = os.path.join(self.images_dir, filename)
            if os.path.exists(file_path):
                try:
                    ui_img = pygame.image.load(file_path).convert_alpha()
                    scaled_ui = pygame.transform.scale(ui_img, (32, 32))
                    self.sprites[ui_type] = scaled_ui
                    print(f"Loaded UI element: {filename}")
                except pygame.error as e:
                    print(f"Error loading {filename}: {e}")
        
        # Create need icons from tools or skills images
        self._create_need_icons()
    
    def _create_need_icons(self):
        """Create need icons from available assets or fallback"""
        
        # Try to extract icons from tools/skills images
        if "tools" in self.sprites:
            tools_img = self.sprites["tools"]
            icon_size = 16
            
            # Extract small icons from tools image
            if tools_img.get_width() >= icon_size * 4:
                for i, need in enumerate(["hunger", "sleep", "social", "fun"]):
                    if i * icon_size < tools_img.get_width():
                        icon_rect = pygame.Rect(i * icon_size, 0, icon_size, icon_size)
                        icon_surface = pygame.Surface((icon_size, icon_size), pygame.SRCALPHA)
                        icon_surface.blit(tools_img, (0, 0), icon_rect)
                        self.icons[need] = icon_surface
        
        # Create fallback icons if needed
        self._create_fallback_icons()
    
    def _create_fallback_icons(self):
        """Create simple fallback icons if custom ones aren't available"""
        
        icon_size = 16
        
        # Only create fallbacks for missing icons
        need_colors = {
            "hunger": (255, 100, 100),
            "sleep": (100, 100, 255), 
            "social": (100, 255, 100),
            "fun": (255, 255, 100)
        }
        
        for need, color in need_colors.items():
            if need not in self.icons:
                icon = pygame.Surface((icon_size, icon_size), pygame.SRCALPHA)
                pygame.draw.circle(icon, color, (icon_size//2, icon_size//2), icon_size//2 - 2)
                pygame.draw.circle(icon, (255, 255, 255), (icon_size//2, icon_size//2), icon_size//2 - 2, 2)
                self.icons[need] = icon
    
    def _create_fallback_assets(self):
        """Create simple fallback assets for anything missing"""
        
        # Fallback grass texture
        if "grass" not in self.textures:
            grass = pygame.Surface((32, 32))
            grass.fill((76, 153, 76))
            self.textures["grass"] = grass
        
        # Create path tiles from fence tileset if available
        if "fences" in self.tilesets and "path_straight" not in self.textures:
            self._create_path_tiles_from_fences()
        
        # Fallback stone path
        if "path_straight" not in self.textures:
            path = pygame.Surface((32, 32))
            path.fill((150, 140, 120))
            self.textures["path_straight"] = path
            self.textures["path_corner"] = path
        
        # Fallback water
        if "water" not in self.textures:
            water = pygame.Surface((32, 32))
            water.fill((64, 164, 223))
            self.textures["water"] = water
        
        # Fallback tree
        if "tree" not in self.sprites:
            tree = pygame.Surface((32, 48), pygame.SRCALPHA)
            # Simple tree shape
            pygame.draw.rect(tree, (101, 67, 33), (12, 30, 8, 18))  # Trunk
            pygame.draw.circle(tree, (34, 139, 34), (16, 20), 12)   # Foliage
            self.sprites["tree"] = tree
        
        # Fallback flowers
        if "flowers" not in self.sprites:
            flowers = pygame.Surface((16, 16), pygame.SRCALPHA)
            pygame.draw.circle(flowers, (255, 192, 203), (8, 8), 6)
            self.sprites["flowers"] = flowers
        
        # Create UI assets
        self._create_ui_assets()
    
    def _create_path_tiles_from_fences(self):
        """Create path tiles from the fence tileset"""
        if "fences" not in self.tilesets:
            return
        
        fences_img = self.tilesets["fences"]
        tile_size = 32
        
        # Extract different fence/path pieces
        if fences_img.get_width() >= tile_size * 2 and fences_img.get_height() >= tile_size:
            # Straight path
            straight_rect = pygame.Rect(0, 0, tile_size, tile_size)
            straight_surface = pygame.Surface((tile_size, tile_size), pygame.SRCALPHA)
            straight_surface.blit(fences_img, (0, 0), straight_rect)
            self.textures["path_straight"] = straight_surface
            
            # Corner path
            corner_rect = pygame.Rect(tile_size, 0, tile_size, tile_size)
            corner_surface = pygame.Surface((tile_size, tile_size), pygame.SRCALPHA)
            corner_surface.blit(fences_img, (0, 0), corner_rect)
            self.textures["path_corner"] = corner_surface
    
    def _create_ui_assets(self):
        """Create UI assets like panels, progress bars, and speech bubbles"""
        
        # Glass-like UI panel
        panel_width, panel_height = 200, 100
        ui_panel = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
        
        # Glass effect
        base_color = (20, 30, 40, 180)
        border_color = (100, 150, 200, 200)
        highlight_color = (255, 255, 255, 30)
        
        pygame.draw.rect(ui_panel, base_color, (0, 0, panel_width, panel_height), border_radius=10)
        pygame.draw.rect(ui_panel, highlight_color, (2, 2, panel_width-4, panel_height//4), border_radius=8)
        pygame.draw.rect(ui_panel, border_color, (0, 0, panel_width, panel_height), 2, border_radius=10)
        
        self.sprites["ui_panel"] = ui_panel
        
        # Create progress bar components
        self._create_progress_bars()
        
        # Create speech bubble
        self._create_speech_bubble()
        
        # Create need icons if not already loaded
        if len(self.icons) < 4:
            self._create_need_icons_from_images()
    
    def _create_progress_bars(self):
        """Create image-based progress bars for different needs"""
        bar_width, bar_height = 120, 16
        
        need_colors = {
            "hunger": (255, 100, 100),
            "social": (100, 200, 255),
            "sleep": (150, 100, 255),
            "fun": (255, 200, 100)
        }
        
        for need, color in need_colors.items():
            # Background bar
            bg_bar = pygame.Surface((bar_width, bar_height), pygame.SRCALPHA)
            pygame.draw.rect(bg_bar, (40, 40, 40), (0, 0, bar_width, bar_height), border_radius=bar_height//2)
            pygame.draw.rect(bg_bar, (80, 80, 80), (0, 0, bar_width, bar_height), 1, border_radius=bar_height//2)
            self.sprites[f"bar_{need}_bg"] = bg_bar
            
            # Filled bar
            filled_bar = pygame.Surface((bar_width, bar_height), pygame.SRCALPHA)
            pygame.draw.rect(filled_bar, color, (0, 0, bar_width, bar_height), border_radius=bar_height//2)
            # Add shine effect
            shine_color = tuple(min(255, c + 40) for c in color) + (100,)
            pygame.draw.rect(filled_bar, shine_color, (2, 1, bar_width-4, bar_height//3), border_radius=bar_height//4)
            self.sprites[f"bar_{need}"] = filled_bar
    
    def _create_speech_bubble(self):
        """Create a speech bubble graphic"""
        bubble_width, bubble_height = 180, 60
        bubble = pygame.Surface((bubble_width, bubble_height), pygame.SRCALPHA)
        
        # Main bubble
        bubble_color = (255, 255, 255, 240)
        border_color = (0, 0, 0, 180)
        
        pygame.draw.ellipse(bubble, bubble_color, (0, 0, bubble_width, bubble_height-10))
        pygame.draw.ellipse(bubble, border_color, (0, 0, bubble_width, bubble_height-10), 2)
        
        # Tail
        tail_points = [(bubble_width//4, bubble_height-10), (bubble_width//4-10, bubble_height), (bubble_width//4+5, bubble_height-10)]
        pygame.draw.polygon(bubble, bubble_color, tail_points)
        pygame.draw.polygon(bubble, border_color, tail_points, 2)
        
        self.sprites["speech_bubble"] = bubble
    
    def _create_need_icons_from_images(self):
        """Create need icons from available character or building images"""
        if "professionalpeople.png" in [f for f in os.listdir(self.images_dir) if f.endswith('.png')]:
            # Try to extract icons from professional people image
            prof_path = os.path.join(self.images_dir, "professionalpeople.png")
            try:
                prof_img = pygame.image.load(prof_path).convert_alpha()
                icon_size = 16
                
                # Extract 4 small icons for needs
                for i, need in enumerate(["hunger", "sleep", "social", "fun"]):
                    if need not in self.icons and i * icon_size < prof_img.get_width():
                        icon_rect = pygame.Rect(i * icon_size, 0, icon_size, icon_size)
                        icon_surface = pygame.Surface((icon_size, icon_size), pygame.SRCALPHA)
                        icon_surface.blit(prof_img, (0, 0), icon_rect)
                        self.icons[need] = icon_surface
            except:
                pass  # Fall back to default icon creation
    
    def get_sprite(self, name: str) -> Optional[pygame.Surface]:
        """Get a sprite by name"""
        return self.sprites.get(name)
    
    def get_texture(self, name: str) -> Optional[pygame.Surface]:
        """Get a texture by name"""
        return self.textures.get(name)
    
    def get_icon(self, name: str) -> Optional[pygame.Surface]:
        """Get an icon by name"""
        return self.icons.get(name)
    
    def get_character_sprite(self, character_name: str) -> pygame.Surface:
        """Get character sprite by name, fallback to default"""
        sprite_name = character_name.lower()
        if sprite_name in self.sprites:
            return self.sprites[sprite_name]
        
        # Try fallbacks
        fallbacks = ["player", "female", "male", "walking"]
        for fallback in fallbacks:
            if fallback in self.sprites:
                return self.sprites[fallback]
        
        # Ultimate fallback - create simple colored rectangle
        fallback_sprite = pygame.Surface((24, 32))
        fallback_sprite.fill((100, 150, 200))
        return fallback_sprite
    
    def get_npc_portrait(self, npc_name: str) -> pygame.Surface:
        """Get portrait sprite for an NPC by name"""
        portrait_name = f"npc_portrait_{npc_name.lower()}"
        if portrait_name in self.sprites:
            return self.sprites[portrait_name]
        
        # Try fallback portraits
        fallback_portraits = [f"npc_portrait_male", f"npc_portrait_female", f"npc_portrait_girl1"]
        for fallback in fallback_portraits:
            if fallback in self.sprites:
                return self.sprites[fallback]
        
        # Ultimate fallback - create a simple colored circle
        portrait = pygame.Surface((24, 24), pygame.SRCALPHA)
        pygame.draw.circle(portrait, (100, 150, 200), (12, 12), 10)
        return portrait
    
    def get_scaled_sprite(self, name: str, size: tuple) -> Optional[pygame.Surface]:
        """Get a scaled version of a sprite with caching for performance"""
        cache_key = f"{name}_{size[0]}x{size[1]}"
        
        # Check cache first
        if cache_key in self._scaled_cache:
            return self._scaled_cache[cache_key]
        
        # Get original sprite
        original = self.get_sprite(name)
        if not original:
            return None
        
        # Scale the sprite
        scaled = pygame.transform.scale(original, size)
        
        # Add to cache if there's room
        if len(self._scaled_cache) < self._cache_max_size:
            self._scaled_cache[cache_key] = scaled
        
        return scaled
    
    def clear_cache(self):
        """Clear the scaling cache to free memory"""
        self._scaled_cache.clear()
    
    def preload_common_sizes(self):
        """Preload commonly used sprite sizes for better performance"""
        common_sprites = ["house", "shop", "market_hall", "tree", "flowers"]
        common_sizes = [(64, 64), (32, 32), (48, 48), (96, 80)]
        
        for sprite_name in common_sprites:
            for size in common_sizes:
                if sprite_name in self.sprites:
                    self.get_scaled_sprite(sprite_name, size)
        
        print(f"Preloaded {len(self._scaled_cache)} scaled sprites for performance")
    
    def list_loaded_assets(self):
        """Print all loaded assets for debugging"""
        print("\n=== LOADED CUSTOM ASSETS ===")
        print(f"Sprites ({len(self.sprites)}): {list(self.sprites.keys())}")
        print(f"Textures ({len(self.textures)}): {list(self.textures.keys())}")
        print(f"Icons ({len(self.icons)}): {list(self.icons.keys())}")
        print(f"Tilesets ({len(self.tilesets)}): {list(self.tilesets.keys())}")
        print("===========================\n")