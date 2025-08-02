import pygame
import os
import random
from typing import Dict, Optional
from src.core.constants import *

class AssetManager:
    """
    Centralized asset management for sprites, textures, and visual elements.
    Creates beautiful pixel art assets programmatically for a Stardew Valley-like aesthetic.
    """
    
    def __init__(self):
        self.sprites: Dict[str, pygame.Surface] = {}
        self.textures: Dict[str, pygame.Surface] = {}
        self.icons: Dict[str, pygame.Surface] = {}
        
        # Create assets directory
        self.assets_dir = "assets"
        os.makedirs(self.assets_dir, exist_ok=True)
        os.makedirs(f"{self.assets_dir}/sprites", exist_ok=True)
        os.makedirs(f"{self.assets_dir}/textures", exist_ok=True)
        os.makedirs(f"{self.assets_dir}/icons", exist_ok=True)
        
        self._generate_all_assets()
    
    def _generate_all_assets(self):
        """Generate all visual assets programmatically"""
        self._create_terrain_textures()
        self._create_building_sprites()
        self._create_npc_sprites()
        self._create_nature_elements()
        self._create_ui_icons()
        self._create_event_decorations()
    
    def _create_terrain_textures(self):
        """Create beautiful terrain textures"""
        
        # Grass texture with variation
        grass = pygame.Surface((32, 32))
        base_green = (76, 153, 76)
        
        # Fill with base grass color
        grass.fill(base_green)
        
        # Add grass blade details
        for _ in range(15):
            x = random.randint(0, 31)
            y = random.randint(0, 31)
            # Lighter grass blades
            lighter_green = (90, 167, 90)
            pygame.draw.circle(grass, lighter_green, (x, y), 1)
        
        # Add some darker spots for depth
        for _ in range(8):
            x = random.randint(0, 31)
            y = random.randint(0, 31)
            darker_green = (65, 140, 65)
            pygame.draw.circle(grass, darker_green, (x, y), 2)
        
        self.textures["grass"] = grass
        
        # Stone path texture
        path = pygame.Surface((32, 32))
        path_color = (150, 140, 120)
        path.fill(path_color)
        
        # Add stone texture
        for y in range(0, 32, 8):
            for x in range(0, 32, 8):
                stone_shade = (
                    path_color[0] + random.randint(-20, 20),
                    path_color[1] + random.randint(-20, 20),
                    path_color[2] + random.randint(-20, 20)
                )
                stone_shade = tuple(max(0, min(255, c)) for c in stone_shade)
                pygame.draw.rect(path, stone_shade, (x, y, 8, 8))
        
        self.textures["stone_path"] = path
        
        # Water texture
        water = pygame.Surface((32, 32))
        water_blue = (64, 164, 223)
        water.fill(water_blue)
        
        # Add water ripples
        for i in range(3):
            ripple_color = (74, 174, 233)
            y_pos = 8 + i * 8
            pygame.draw.line(water, ripple_color, (0, y_pos), (32, y_pos), 1)
            pygame.draw.line(water, ripple_color, (0, y_pos + 4), (32, y_pos + 4), 1)
        
        self.textures["water"] = water
    
    def _create_building_sprites(self):
        """Create pixel art building sprites"""
        
        # Cozy house sprite
        house = pygame.Surface((64, 64), pygame.SRCALPHA)
        
        # Roof
        roof_color = (139, 69, 19)  # Saddle brown
        pygame.draw.polygon(house, roof_color, [(0, 20), (32, 0), (64, 20), (64, 25), (32, 5), (0, 25)])
        
        # Walls
        wall_color = (222, 184, 135)  # Burlywood
        pygame.draw.rect(house, wall_color, (4, 20, 56, 40))
        
        # Door
        door_color = (101, 67, 33)  # Brown
        pygame.draw.rect(house, door_color, (26, 40, 12, 20))
        
        # Door handle
        pygame.draw.circle(house, (255, 215, 0), (35, 50), 1)
        
        # Windows
        window_color = (135, 206, 235)  # Sky blue
        pygame.draw.rect(house, window_color, (10, 30, 10, 10))
        pygame.draw.rect(house, window_color, (44, 30, 10, 10))
        
        # Window frames
        frame_color = (139, 69, 19)
        pygame.draw.rect(house, frame_color, (10, 30, 10, 10), 1)
        pygame.draw.rect(house, frame_color, (44, 30, 10, 10), 1)
        
        # Chimney
        pygame.draw.rect(house, (105, 105, 105), (50, 10, 6, 15))
        
        self.sprites["house"] = house
        
        # Shop building
        shop = pygame.Surface((64, 64), pygame.SRCALPHA)
        
        # Shop roof (different color)
        shop_roof_color = (160, 82, 45)  # Saddle brown variant
        pygame.draw.polygon(shop, shop_roof_color, [(0, 20), (32, 0), (64, 20), (64, 25), (32, 5), (0, 25)])
        
        # Shop walls
        shop_wall_color = (245, 222, 179)  # Wheat
        pygame.draw.rect(shop, shop_wall_color, (4, 20, 56, 40))
        
        # Large shop window
        pygame.draw.rect(shop, window_color, (8, 25, 20, 15))
        pygame.draw.rect(shop, frame_color, (8, 25, 20, 15), 2)
        
        # Shop door
        pygame.draw.rect(shop, door_color, (35, 35, 12, 25))
        pygame.draw.circle(shop, (255, 215, 0), (44, 47), 1)
        
        # Shop sign
        sign_color = (139, 69, 19)
        pygame.draw.rect(shop, sign_color, (45, 20, 15, 8))
        
        self.sprites["shop"] = shop
        
        # Community center
        community = pygame.Surface((96, 80), pygame.SRCALPHA)
        
        # Larger roof
        pygame.draw.polygon(community, (178, 34, 34), [(0, 25), (48, 0), (96, 25), (96, 30), (48, 5), (0, 30)])
        
        # Main building
        pygame.draw.rect(community, (222, 184, 135), (8, 25, 80, 50))
        
        # Large entrance
        pygame.draw.rect(community, door_color, (38, 50, 20, 25))
        
        # Multiple windows
        for i in range(3):
            x_pos = 15 + i * 25
            pygame.draw.rect(community, window_color, (x_pos, 35, 12, 12))
            pygame.draw.rect(community, frame_color, (x_pos, 35, 12, 12), 1)
        
        self.sprites["community_center"] = community
    
    def _create_npc_sprites(self):
        """Create unique NPC character sprites"""
        
        # Base character template
        def create_character(hair_color, shirt_color, pants_color, skin_color=(255, 220, 177)):
            char = pygame.Surface((24, 32), pygame.SRCALPHA)
            
            # Head
            pygame.draw.circle(char, skin_color, (12, 8), 6)
            
            # Hair
            pygame.draw.circle(char, hair_color, (12, 6), 7)
            
            # Eyes
            pygame.draw.circle(char, (0, 0, 0), (10, 8), 1)
            pygame.draw.circle(char, (0, 0, 0), (14, 8), 1)
            
            # Body (shirt)
            pygame.draw.rect(char, shirt_color, (8, 14, 8, 10))
            
            # Arms
            pygame.draw.rect(char, skin_color, (6, 16, 3, 8))
            pygame.draw.rect(char, skin_color, (15, 16, 3, 8))
            
            # Pants
            pygame.draw.rect(char, pants_color, (8, 24, 8, 6))
            
            # Legs
            pygame.draw.rect(char, skin_color, (8, 30, 3, 2))
            pygame.draw.rect(char, skin_color, (13, 30, 3, 2))
            
            return char
        
        # Alice - Blonde hair, blue shirt
        self.sprites["alice"] = create_character(
            hair_color=(255, 215, 0),      # Gold
            shirt_color=(70, 130, 180),    # Steel blue
            pants_color=(139, 69, 19)      # Saddle brown
        )
        
        # Bob - Brown hair, green shirt
        self.sprites["bob"] = create_character(
            hair_color=(101, 67, 33),      # Brown
            shirt_color=(34, 139, 34),     # Forest green
            pants_color=(25, 25, 112)      # Midnight blue
        )
        
        # Charlie - Red hair, yellow shirt
        self.sprites["charlie"] = create_character(
            hair_color=(205, 92, 92),      # Indian red
            shirt_color=(255, 215, 0),     # Gold
            pants_color=(105, 105, 105)    # Dim gray
        )
        
        # Diana - Black hair, purple shirt
        self.sprites["diana"] = create_character(
            hair_color=(47, 79, 79),       # Dark slate gray
            shirt_color=(147, 112, 219),   # Medium slate blue
            pants_color=(139, 0, 0)        # Dark red
        )
        
        # Player sprite (customizable)
        self.sprites["player"] = create_character(
            hair_color=(139, 69, 19),      # Brown (default)
            shirt_color=(30, 144, 255),    # Dodger blue
            pants_color=(72, 61, 139)      # Dark slate blue
        )
    
    def _create_nature_elements(self):
        """Create trees, flowers, and other nature elements"""
        
        # Tree sprite
        tree = pygame.Surface((32, 48), pygame.SRCALPHA)
        
        # Tree trunk
        trunk_color = (101, 67, 33)
        pygame.draw.rect(tree, trunk_color, (12, 30, 8, 18))
        
        # Tree foliage (multiple circles for full look)
        foliage_color = (34, 139, 34)
        pygame.draw.circle(tree, foliage_color, (16, 20), 12)
        pygame.draw.circle(tree, (0, 128, 0), (16, 18), 10)  # Darker center
        
        # Some leaves detail
        leaf_color = (50, 205, 50)
        for i in range(5):
            x = 10 + random.randint(0, 12)
            y = 10 + random.randint(0, 12)
            pygame.draw.circle(tree, leaf_color, (x, y), 2)
        
        self.sprites["tree"] = tree
        
        # Flower patch
        flowers = pygame.Surface((16, 16), pygame.SRCALPHA)
        
        # Grass base
        pygame.draw.circle(flowers, (76, 153, 76), (8, 12), 6)
        
        # Small flowers
        flower_colors = [(255, 192, 203), (255, 255, 0), (255, 165, 0), (238, 130, 238)]
        for i, color in enumerate(flower_colors):
            x = 4 + (i % 2) * 8
            y = 4 + (i // 2) * 8
            pygame.draw.circle(flowers, color, (x, y), 2)
        
        self.sprites["flowers"] = flowers
        
        # Fence piece
        fence = pygame.Surface((32, 16), pygame.SRCALPHA)
        fence_color = (160, 82, 45)
        
        # Horizontal rails
        pygame.draw.rect(fence, fence_color, (0, 4, 32, 3))
        pygame.draw.rect(fence, fence_color, (0, 9, 32, 3))
        
        # Vertical posts
        pygame.draw.rect(fence, fence_color, (0, 0, 3, 16))
        pygame.draw.rect(fence, fence_color, (16, 0, 3, 16))
        pygame.draw.rect(fence, fence_color, (29, 0, 3, 16))
        
        self.sprites["fence"] = fence
    
    def _create_ui_icons(self):
        """Create modern UI icons for needs and interface"""
        
        # Hunger icon (fork and knife)
        hunger_icon = pygame.Surface((16, 16), pygame.SRCALPHA)
        # Fork
        pygame.draw.line(hunger_icon, (200, 200, 200), (4, 2), (4, 14), 2)
        pygame.draw.line(hunger_icon, (200, 200, 200), (3, 3), (5, 3), 1)
        pygame.draw.line(hunger_icon, (200, 200, 200), (3, 5), (5, 5), 1)
        # Knife
        pygame.draw.line(hunger_icon, (200, 200, 200), (12, 2), (12, 14), 2)
        pygame.draw.line(hunger_icon, (200, 200, 200), (11, 2), (13, 2), 1)
        
        self.icons["hunger"] = hunger_icon
        
        # Sleep icon (bed)
        sleep_icon = pygame.Surface((16, 16), pygame.SRCALPHA)
        # Bed frame
        pygame.draw.rect(sleep_icon, (139, 69, 19), (2, 8, 12, 6))
        # Pillow
        pygame.draw.ellipse(sleep_icon, (255, 255, 255), (3, 6, 6, 4))
        # Blanket
        pygame.draw.rect(sleep_icon, (70, 130, 180), (3, 10, 10, 3))
        
        self.icons["sleep"] = sleep_icon
        
        # Social icon (people)
        social_icon = pygame.Surface((16, 16), pygame.SRCALPHA)
        # Two simple figures
        pygame.draw.circle(social_icon, (200, 200, 200), (5, 4), 2)
        pygame.draw.rect(social_icon, (200, 200, 200), (3, 6, 4, 6))
        pygame.draw.circle(social_icon, (200, 200, 200), (11, 4), 2)
        pygame.draw.rect(social_icon, (200, 200, 200), (9, 6, 4, 6))
        
        self.icons["social"] = social_icon
        
        # Fun icon (star)
        fun_icon = pygame.Surface((16, 16), pygame.SRCALPHA)
        star_points = [(8, 2), (10, 6), (14, 6), (11, 9), (12, 13), (8, 11), (4, 13), (5, 9), (2, 6), (6, 6)]
        pygame.draw.polygon(fun_icon, (255, 215, 0), star_points)
        
        self.icons["fun"] = fun_icon
    
    def _create_event_decorations(self):
        """Create decorative elements for events"""
        
        # Party tent
        tent = pygame.Surface((48, 32), pygame.SRCALPHA)
        # Tent fabric
        tent_color = (255, 182, 193)  # Light pink
        pygame.draw.polygon(tent, tent_color, [(8, 28), (24, 8), (40, 28)])
        # Tent poles
        pygame.draw.line(tent, (139, 69, 19), (24, 8), (24, 28), 2)
        pygame.draw.line(tent, (139, 69, 19), (8, 28), (8, 30), 2)
        pygame.draw.line(tent, (139, 69, 19), (40, 28), (40, 30), 2)
        
        self.sprites["tent"] = tent
        
        # Table
        table = pygame.Surface((32, 24), pygame.SRCALPHA)
        table_color = (160, 82, 45)
        # Table top
        pygame.draw.rect(table, table_color, (4, 8, 24, 4))
        # Table legs
        pygame.draw.rect(table, table_color, (6, 12, 2, 8))
        pygame.draw.rect(table, table_color, (24, 12, 2, 8))
        
        self.sprites["table"] = table
        
        # Decorative banner
        banner = pygame.Surface((64, 16), pygame.SRCALPHA)
        colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0)]
        for i in range(4):
            x = i * 16
            pygame.draw.polygon(banner, colors[i], [(x, 0), (x + 12, 0), (x + 8, 12)])
        
        self.sprites["banner"] = banner
    
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
        return self.sprites.get("player", self.sprites["alice"])  # Fallback