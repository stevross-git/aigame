import pygame
import os
from typing import Dict, Optional
from src.core.constants import *

class CustomAssetManager:
    """
    Asset manager that loads beautiful custom Stardew Valley-style images
    from the ./images directory instead of generating programmatic pixel art.
    """
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(CustomAssetManager, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        # Only initialize once using singleton pattern
        if CustomAssetManager._initialized:
            return
            
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
            CustomAssetManager._initialized = True
            return
        
        print("Loading assets for the first time...")
        self._load_all_assets()
        CustomAssetManager._initialized = True
        print("Asset loading completed!")
        
        # Show what was loaded
        self._print_asset_summary()
    
    def _load_all_assets(self):
        """Load all custom assets from the images directory"""
        self._load_terrain_and_tilesets()
        self._load_buildings()
        self._load_characters()
        self._load_ui_elements()
        self._load_scene_backgrounds()
        self._load_decorative_elements()
        self._create_fallback_assets()
    
    def _load_terrain_and_tilesets(self):
        """Load terrain textures and tilesets"""
        
        # Load grass textures from nature/environment folder
        grass_files = ["grass.png", "grass1.png", "grasstileset.png"]
        
        for i, grass_file in enumerate(grass_files):
            grass_path = os.path.join(self.images_dir, "nature", "environment", grass_file)
            if os.path.exists(grass_path):
                grass_img = pygame.image.load(grass_path).convert_alpha()
                
                if grass_file == "grasstileset.png":
                    # Handle tileset
                    self.tilesets["grass_tileset"] = grass_img
                    
                    # Extract individual grass tiles (assuming 32x32 tiles)
                    tile_size = 32
                    grass_tiles = []
                    tileset_width = grass_img.get_width() // tile_size
                    tileset_height = grass_img.get_height() // tile_size
                    
                    for y in range(min(4, tileset_height)):  # Get first 4 rows
                        for x in range(min(4, tileset_width)):  # Get first 4 columns
                            tile_rect = pygame.Rect(x * tile_size, y * tile_size, tile_size, tile_size)
                            tile_surface = pygame.Surface((tile_size, tile_size), pygame.SRCALPHA)
                            tile_surface.blit(grass_img, (0, 0), tile_rect)
                            grass_tiles.append(tile_surface)
                    
                    # Use first tile as main grass texture if not already set
                    if grass_tiles and "grass" not in self.textures:
                        self.textures["grass"] = grass_tiles[0]
                        # Store additional grass variants
                        for j, tile in enumerate(grass_tiles[1:5]):  # Store up to 4 variants
                            self.textures[f"grass_variant_{j}"] = tile
                else:
                    # Handle individual grass files
                    if i == 0:
                        self.textures["grass"] = grass_img
                    else:
                        self.textures[f"grass_variant_{i-1}"] = grass_img
        
        # Load mountain/terrain for decorative elements
        mountain_path = os.path.join(self.images_dir, "nature", "environment", "mountain.png")
        if os.path.exists(mountain_path):
            mountain_img = pygame.image.load(mountain_path).convert_alpha()
            # Scale down for use as terrain decoration
            mountain_scaled = pygame.transform.scale(mountain_img, (64, 64))
            self.sprites["mountain"] = mountain_scaled
        
        # Load fences and walls from nature/environment folder
        fence_files = ["fences, walls, bridges.png", "fences_walls_bridges.png"]
        for fence_file in fence_files:
            fences_path = os.path.join(self.images_dir, "nature", "environment", fence_file)
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
                break
    
    def _load_buildings(self):
        """Load building sprites from custom images"""
        
        building_mappings = {
            # Residential Buildings (buildings/houses/)
            "house": ("buildings/houses", "house.png"),
            "house_small": ("buildings/houses", "house.png"),
            "house_large": ("buildings/houses", "2story_building.png"),
            "2story": ("buildings/houses", "2story_building.png"),
            "mansion": ("buildings/houses", "mansion.png"),
            "home_asc": ("buildings/houses", "home asc.png"),
            "player_house": ("buildings/houses", "house.png"),
            "farm": ("buildings/houses", "farm_1.png"),
            "farm_1": ("buildings/houses", "farm_1.png"),
            "farmhouse": ("buildings/houses", "farmhouse_interior.png"),
            
            # Commercial Buildings (buildings/shops/)
            "shop": ("buildings/shops", "shop.png"),
            "general_store": ("buildings/shops", "shop.png"),
            "blacksmith": ("buildings/shops", "blacksmith_shop.png"),
            "blacksmith_shop": ("buildings/shops", "blacksmith_shop.png"),
            "restaurant": ("buildings/shops", "restaurant.png"),
            "fish_shop": ("buildings/shops", "fish_shop.png"),
            "gems_store": ("buildings/shops", "gems_store.png"),
            "hardware_store": ("buildings/shops", "hardware_store.png"),
            
            # Public Buildings (buildings/public/)
            "town_hall": ("buildings/public", "town_hall.png"),
            "townhall": ("buildings/public", "townhall.png"),
            "market_hall": ("buildings/public", "town_hall.png"),
            "community_center": ("buildings/public", "town_hall.png"),
            "hospital": ("buildings/public", "hospital.png"),
            "hospital_1": ("buildings/public", "hospital_1.png"),
            "school": ("buildings/public", "school.png"),
            "school_1": ("buildings/public", "school_1.png"),
            "office": ("buildings/public", "office.png"),
            "hotel": ("buildings/public", "hotel.png"),
        }
        
        for building_type, (folder, filename) in building_mappings.items():
            file_path = os.path.join(self.images_dir, folder, filename)
            if os.path.exists(file_path):
                try:
                    building_img = pygame.image.load(file_path).convert_alpha()
                    # Scale buildings to appropriate size for game
                    if building_type in ["mansion"]:
                        # Largest buildings
                        scaled_img = pygame.transform.scale(building_img, (128, 96))
                    elif building_type in ["community_center", "town_hall", "townhall", "hospital", "school", "hotel"]:
                        # Large public buildings
                        scaled_img = pygame.transform.scale(building_img, (96, 80))
                    elif building_type in ["2story", "house_large", "office", "hospital_1", "school_1"]:
                        # Medium buildings
                        scaled_img = pygame.transform.scale(building_img, (80, 70))
                    elif building_type in ["blacksmith", "blacksmith_shop", "restaurant", "gems_store", "hardware_store"]:
                        # Specialized shops - medium size
                        scaled_img = pygame.transform.scale(building_img, (70, 65))
                    elif building_type in ["farm", "farm_1", "farmhouse"]:
                        # Farm buildings - wider
                        scaled_img = pygame.transform.scale(building_img, (90, 65))
                    else:
                        # Standard building size (houses, small shops)
                        scaled_img = pygame.transform.scale(building_img, (64, 64))
                    
                    self.sprites[building_type] = scaled_img
                    # print(f"Loaded {building_type}: {filename}")
                except pygame.error as e:
                    print(f"Error loading {filename}: {e}")
            else:
                print(f"Warning: {filename} not found for {building_type}")
    
    def _load_characters(self):
        """Load character sprites from custom images"""
        
        character_mappings = {
            # Female characters (characters/females/)
            "female": ("characters/females", "females.png"),
            "females": ("characters/females", "females.png"), 
            "girl1": ("characters/females", "girl1.png"),
            "female_villager": ("characters/females", "female_villager.png"),
            
            # Male characters (characters/males/)
            "male": ("characters/males", "male.png"),
            "males": ("characters/males", "male.png"),
            "male_farmer": ("characters/males", "male_farmer.png"),
            
            # NPC characters (characters/npcs/)
            "elder_villager": ("characters/npcs", "elder_villager.png"),
            "professionals": ("characters/npcs", "professionalpeople.png"),
            "professional_people": ("characters/npcs", "professionalpeople.png"),
            "shop_keepers": ("characters/npcs", "shop_keepers.png"),
            "shopkeepers": ("characters/npcs", "shop_keepers.png"),
            "walking": ("characters/npcs", "npc_walking.png"),
            "npc_walk": ("characters/npcs", "npc_walking.png"),
            "blacksmith_walking": ("characters/npcs", "blacksmith_walking_left.png"),
            
            # Default fallbacks
            "npc_idle": ("characters/males", "male.png")
        }
        
        for char_type, (folder, filename) in character_mappings.items():
            file_path = os.path.join(self.images_dir, folder, filename)
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
                    
                    # print(f"Loaded character: {filename}")
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
            "alice": "female_villager",
            "bob": "elder_villager", 
            "charlie": "male_farmer",
            "diana": "girl1",
            "player": "npc_walking",
            
            # Wealthy family members
            "steve": "professionals",  # Wealthy businessman
            "kailey": "girl1",  # 11-year-old girl
            "louie": "male"  # 5-year-old boy (use smaller male sprite)
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
            # UI panels (ui/panels/)
            "ui_panel": ("ui/panels", "ui_panel.png"),
            "ui_button": ("ui/panels", "ui_button.png"), 
            "ui_window": ("ui/panels", "ui_window.png"),
            
            # Need icons (ui/icons/)
            "icon_hunger": ("ui/icons", "icon_hunger.png"),
            "icon_sleep": ("ui/icons", "icon_sleep.png"),
            "icon_fun": ("ui/icons", "icon_fun.png"),
            
            # Resource and tool images (nature/environment/)
            "tools_gems": ("nature/environment", "tools_gems.png"),
            "resources": ("nature/environment", "resources.png"),
            
            # Legacy mappings - look in multiple locations
            "menu": ("ui/panels", "menu.png"),
            "settings": ("ui/panels", "settings.png"), 
            "skills": ("ui/panels", "skills.png"),
            "tools": ("nature/environment", "tools_gems.png")
        }
        
        for ui_type, (folder, filename) in ui_mappings.items():
            file_path = os.path.join(self.images_dir, folder, filename)
            if os.path.exists(file_path):
                try:
                    ui_img = pygame.image.load(file_path).convert_alpha()
                    scaled_ui = pygame.transform.scale(ui_img, (32, 32))
                    self.sprites[ui_type] = scaled_ui
                    # print(f"Loaded UI element: {filename}")
                except pygame.error as e:
                    print(f"Error loading {filename}: {e}")
        
        # Create need icons from tools or skills images
        self._create_need_icons()
        
        # Load furniture sprites
        self._load_furniture_sprites()
    
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
    
    def _load_scene_backgrounds(self):
        """Load large scene background images"""
        scene_mappings = {
            "village_scene": ("nature/environment", "village_scene.png"),
            "village_square": ("nature/environment", "village_square.png"), 
            "farm_field": ("nature/environment", "farm_field.png"),
            "farm_path": ("nature/environment", "farm_path.png"),
            "farmhouse_interior": ("buildings/houses", "farmhouse_interior.png")
        }
        
        for scene_name, path_info in scene_mappings.items():
            folder, filename = path_info
            file_path = os.path.join(self.images_dir, folder, filename)
            if os.path.exists(file_path):
                try:
                    scene_img = pygame.image.load(file_path).convert_alpha()
                    # Store at original size for backgrounds
                    self.sprites[scene_name] = scene_img
                    # print(f"Loaded scene: {scene_name} from {filename}")
                except pygame.error as e:
                    print(f"Error loading scene {filename}: {e}")
    
    def _load_decorative_elements(self):
        """Load decorative elements like trees and nature sprites"""
        
        # Load tree sprites
        tree_files = ["tree_1.png", "tree_2.png", "tree_3.png", "tree_4.png", "tree_5.png"]
        for i, tree_file in enumerate(tree_files):
            tree_path = os.path.join(self.images_dir, "nature", "trees", tree_file)
            if os.path.exists(tree_path):
                try:
                    tree_img = pygame.image.load(tree_path).convert_alpha()
                    # Scale trees appropriately
                    tree_scaled = pygame.transform.scale(tree_img, (48, 64))
                    self.sprites[f"tree_{i+1}"] = tree_scaled
                    
                    # Also store as generic "tree" if it's the first one
                    if i == 0:
                        self.sprites["tree"] = tree_scaled
                    
                    # print(f"Loaded tree: tree_{i+1}")
                except pygame.error as e:
                    print(f"Error loading {tree_file}: {e}")
        
        # Load UI elements with new naming
        ui_element_mappings = {
            "ui_button": "ui_button.png",
            "ui_panel_new": "ui_panel.png",
            "ui_window": "ui_window.png"
        }
        
        for ui_name, filename in ui_element_mappings.items():
            file_path = os.path.join(self.images_dir, "ui", "panels", filename)
            if os.path.exists(file_path):
                try:
                    ui_img = pygame.image.load(file_path).convert_alpha()
                    self.sprites[ui_name] = ui_img
                    # print(f"Loaded UI element: {ui_name}")
                except pygame.error as e:
                    print(f"Error loading {filename}: {e}")
        
        # Load specific need icons
        icon_mappings = {
            "icon_hunger": "icon_hunger.png",
            "icon_sleep": "icon_sleep.png", 
            "icon_fun": "icon_fun.png"
        }
        
        for icon_name, filename in icon_mappings.items():
            file_path = os.path.join(self.images_dir, "ui", "icons", filename)
            if os.path.exists(file_path):
                try:
                    icon_img = pygame.image.load(file_path).convert_alpha()
                    # Scale to appropriate icon size
                    icon_scaled = pygame.transform.scale(icon_img, (16, 16))
                    self.icons[icon_name.replace("icon_", "")] = icon_scaled
                    # print(f"Loaded icon: {icon_name}")
                except pygame.error as e:
                    print(f"Error loading {filename}: {e}")
    
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
        
        # Use new UI panel if available, otherwise create one
        if "ui_panel_new" not in self.sprites:
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
        else:
            # Use the loaded UI panel
            self.sprites["ui_panel"] = self.sprites["ui_panel_new"]
        
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
        prof_path = os.path.join(self.images_dir, "characters", "npcs", "professionalpeople.png")
        if os.path.exists(prof_path):
            # Try to extract icons from professional people image
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
    
    def get_scene_background(self, scene_name: str) -> Optional[pygame.Surface]:
        """Get a scene background by name"""
        return self.sprites.get(scene_name)
    
    def get_random_tree(self) -> pygame.Surface:
        """Get a random tree sprite from available tree types"""
        import random
        
        # Try to get from the new tree sprites first
        available_trees = []
        for i in range(1, 5):  # tree_1 through tree_4
            tree_name = f"tree_{i}"
            if tree_name in self.sprites:
                available_trees.append(tree_name)
        
        if available_trees:
            tree_name = random.choice(available_trees)
            return self.sprites[tree_name]
        elif "tree" in self.sprites:
            return self.sprites["tree"]
        else:
            # Fallback tree
            tree = pygame.Surface((32, 48), pygame.SRCALPHA)
            pygame.draw.rect(tree, (101, 67, 33), (12, 30, 8, 18))  # Trunk
            pygame.draw.circle(tree, (34, 139, 34), (16, 20), 12)   # Foliage
            return tree
    
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
        
        # print(f"Preloaded {len(self._scaled_cache)} scaled sprites for performance")
    
    def list_loaded_assets(self):
        """Print all loaded assets for debugging"""
        print("\n=== LOADED CUSTOM ASSETS ===")
        print(f"Sprites ({len(self.sprites)}): {list(self.sprites.keys())}")
        print(f"Textures ({len(self.textures)}): {list(self.textures.keys())}")
        print(f"Icons ({len(self.icons)}): {list(self.icons.keys())}")
        print(f"Tilesets ({len(self.tilesets)}): {list(self.tilesets.keys())}")
        print("===========================\n")
    
    def _load_furniture_sprites(self):
        """Load furniture and interior decoration sprites"""
        
        furniture_mappings = {
            # Furniture sprite sheets
            "bathroom_furniture": ("furniture/bathroom", "bathroom furniture sprites.png"),
            "bedroom_furniture": ("furniture/bedroom", "bedroom furniture sprites.png"), 
            "interior_furniture": ("furniture", "interior furniture sprites.png"),
            "living_room_furniture": ("furniture/living_room", "living room furniture sprites.png"),
            
            # Interior rooms
            "bathroom": ("furniture/bathroom", "bathroom.png"),
            "kitchen": ("furniture/kitchen", "kicten.png"),  # Note: filename has typo in your assets
            "living_room": ("furniture/living_room", "livvingroom.png"),  # Note: filename has typo in your assets
            
            # Environment decorations
            "environment_decorations": ("nature/environment", "environment_decorations.png"),
            "fences_walls_bridges": ("nature/environment", "fences, walls, bridges.png")
        }
        
        for furniture_type, path_info in furniture_mappings.items():
            if isinstance(path_info, tuple):
                folder, filename = path_info
                file_path = os.path.join(self.images_dir, folder, filename)
            else:
                # Handle old single filename format
                filename = path_info
                file_path = os.path.join(self.images_dir, filename)
            if os.path.exists(file_path):
                try:
                    furniture_img = pygame.image.load(file_path).convert_alpha()
                    
                    # Store the full spritesheet
                    self.tilesets[furniture_type] = furniture_img
                    
                    # Extract individual furniture pieces if it's a spritesheet
                    if "furniture" in furniture_type and furniture_img.get_width() > 64:
                        self._extract_furniture_pieces(furniture_img, furniture_type)
                    else:
                        # Single furniture piece or room
                        self.sprites[furniture_type] = furniture_img
                    
                    print(f"Loaded furniture: {furniture_type}")
                except pygame.error as e:
                    print(f"Error loading {filename}: {e}")
    
    def _extract_furniture_pieces(self, spritesheet, furniture_type):
        """Extract individual furniture pieces from spritesheet"""
        piece_size = 32  # Assuming 32x32 furniture pieces
        sheet_width = spritesheet.get_width()
        sheet_height = spritesheet.get_height()
        
        pieces_per_row = sheet_width // piece_size
        pieces_per_col = sheet_height // piece_size
        
        piece_count = 0
        for row in range(pieces_per_col):
            for col in range(pieces_per_row):
                if piece_count >= 16:  # Limit to 16 pieces per sheet
                    break
                    
                rect = pygame.Rect(col * piece_size, row * piece_size, piece_size, piece_size)
                piece_surface = pygame.Surface((piece_size, piece_size), pygame.SRCALPHA)
                piece_surface.blit(spritesheet, (0, 0), rect)
                
                # Store individual piece
                piece_name = f"{furniture_type}_piece_{piece_count}"
                self.sprites[piece_name] = piece_surface
                piece_count += 1
    
    def _print_asset_summary(self):
        """Print a summary of loaded assets"""
        buildings = [k for k in self.sprites.keys() if any(t in k for t in ['house', 'shop', 'hospital', 'school', 'mansion', 'restaurant', 'office', 'farm', 'blacksmith', 'hotel', 'town'])]
        characters = [k for k in self.sprites.keys() if any(t in k for t in ['alice', 'bob', 'charlie', 'diana', 'steve', 'kailey', 'louie', 'male', 'female', 'villager', 'farmer'])]
        furniture = [k for k in self.sprites.keys() if 'furniture' in k or 'bathroom' in k or 'kitchen' in k or 'living' in k]
        ui_elements = [k for k in self.sprites.keys() if 'ui_' in k or 'icon_' in k]
        
        print(f"\n📊 ASSET SUMMARY:")
        print(f"🏢 Buildings: {len(buildings)} ({', '.join(buildings[:5])}{'...' if len(buildings) > 5 else ''})")
        print(f"👥 Characters: {len(characters)} ({', '.join(characters[:5])}{'...' if len(characters) > 5 else ''})")
        print(f"🪑 Furniture: {len(furniture)} ({', '.join(furniture[:3])}{'...' if len(furniture) > 3 else ''})")
        print(f"🎮 UI Elements: {len(ui_elements)} ({', '.join(ui_elements[:3])}{'...' if len(ui_elements) > 3 else ''})")
        print(f"📦 Total Sprites: {len(self.sprites)}")
        print(f"🖼️ Total Tilesets: {len(self.tilesets)}")
        print("="*50)