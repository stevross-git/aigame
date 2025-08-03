import pygame
from typing import Dict, List, Optional
from src.core.constants import *
from src.graphics.custom_asset_manager import CustomAssetManager

class HouseItem:
    """Represents an interactive item in the house"""
    def __init__(self, x: int, y: int, item_type: str, width: int = 32, height: int = 32):
        self.x = x
        self.y = y
        self.item_type = item_type
        self.width = width
        self.height = height
        self.rect = pygame.Rect(x, y, width, height)
        self.interactable = True

class HouseInterior:
    """
    Manages the player's house interior with interactive furniture and rooms
    """
    
    def __init__(self):
        self.assets = CustomAssetManager()
        
        # House dimensions (match screen size for better experience)
        self.width = SCREEN_WIDTH
        self.height = SCREEN_HEIGHT
        self.tile_size = 32
        
        # Interior items
        self.items: List[HouseItem] = []
        self._setup_house_items()
        
        # Room areas for different activities
        self.sleeping_area = pygame.Rect(100, 100, 150, 120)
        self.kitchen_area = pygame.Rect(400, 100, 180, 150)
        self.living_area = pygame.Rect(100, 300, 300, 150)
        
        # House state
        self.inside_house = False
        self.player_house_pos = (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 100)  # Start near bottom (door area)
        
    def _setup_house_items(self):
        """Setup furniture and interactive items in the house"""
        self.items = [
            # Bedroom (top-left area) - Keep bed against wall for realistic layout
            HouseItem(110, 110, "bed", 80, 45),
            HouseItem(210, 110, "dresser", 45, 40),
            
            # Kitchen (top-right area) - Better counter arrangement
            HouseItem(450, 110, "stove", 60, 45),
            HouseItem(520, 110, "refrigerator", 45, 65),
            HouseItem(380, 170, "table", 90, 45),  # Dining table in kitchen area
            
            # Living room (bottom-left area) - TV facing couch
            HouseItem(110, 350, "couch", 120, 45),
            HouseItem(260, 340, "tv", 70, 50),
            HouseItem(110, 420, "bookshelf", 45, 70),
            
            # Bathroom (top-center area) - More realistic bathroom layout  
            HouseItem(320, 110, "toilet", 35, 35),
            HouseItem(320, 160, "sink", 45, 35),
            
            # Exit door (bottom-center, where player spawns)
            HouseItem(SCREEN_WIDTH // 2 - 25, SCREEN_HEIGHT - 70, "door", 50, 70),
        ]
    
    def get_item_at(self, x: int, y: int) -> Optional[HouseItem]:
        """Get the house item at given coordinates"""
        point = pygame.Rect(x, y, 1, 1)
        for item in self.items:
            if item.rect.colliderect(point):
                return item
        return None
    
    def interact_with_item(self, item: HouseItem, player) -> str:
        """Handle interaction with a house item"""
        if item.item_type == "bed":
            return self._use_bed(player)
        elif item.item_type == "stove":
            return self._use_stove(player)
        elif item.item_type == "refrigerator":
            return self._use_refrigerator(player)
        elif item.item_type == "table":
            return self._use_table(player)
        elif item.item_type == "couch":
            return self._use_couch(player)
        elif item.item_type == "tv":
            return self._use_tv(player)
        elif item.item_type == "bookshelf":
            return self._use_bookshelf(player)
        elif item.item_type == "dresser":
            return self._use_dresser(player)
        elif item.item_type == "toilet":
            return self._use_toilet(player)
        elif item.item_type == "sink":
            return self._use_sink(player)
        elif item.item_type == "door":
            return "exit_house"
        else:
            return f"🔍 You examine the {item.item_type}. It's a nice piece of furniture."
    
    def _use_bed(self, player) -> str:
        """Player sleeps in bed"""
        if hasattr(player, 'needs'):
            old_sleep = player.needs.get('sleep', 0)
            old_fun = player.needs.get('fun', 0)
            
            player.needs['sleep'] = min(1.0, player.needs['sleep'] + 0.8)
            player.needs['fun'] = min(1.0, player.needs.get('fun', 0) + 0.3)
            
            sleep_gained = player.needs['sleep'] - old_sleep
            fun_gained = player.needs['fun'] - old_fun
            
            if sleep_gained > 0:
                return f"💤 You sleep peacefully and dream sweetly! Restored {int(sleep_gained * 100)}% sleep and {int(fun_gained * 100)}% fun. You feel refreshed and ready for the day!"
            else:
                return "💤 You're not tired right now, but lying in your comfortable bed is still relaxing."
        return "💤 You rest on your bed for a moment."
    
    def _use_kitchen(self, player) -> str:
        """Player uses kitchen appliances"""
        if hasattr(player, 'needs'):
            old_hunger = player.needs.get('hunger', 0)
            old_fun = player.needs.get('fun', 0)
            
            player.needs['hunger'] = min(1.0, player.needs['hunger'] + 0.6)
            player.needs['fun'] = min(1.0, player.needs.get('fun', 0) + 0.1)
            
            hunger_restored = player.needs['hunger'] - old_hunger
            fun_gained = player.needs['fun'] - old_fun
            
            if hunger_restored > 0:
                return f"🍳 You cook a delicious homemade meal and enjoy every bite! Restored {int(hunger_restored * 100)}% hunger and {int(fun_gained * 100)}% fun. The kitchen smells amazing!"
            else:
                return "🍳 You're not hungry right now, but you enjoy organizing and being in your kitchen."
        return "🍳 You prepare a nice meal in your kitchen."
    
    def _use_living_room(self, player) -> str:
        """Player relaxes in living room"""
        if hasattr(player, 'needs'):
            old_fun = player.needs.get('fun', 0)
            old_sleep = player.needs.get('sleep', 0)
            
            player.needs['fun'] = min(1.0, player.needs['fun'] + 0.4)
            player.needs['sleep'] = min(1.0, player.needs.get('sleep', 0) + 0.1)
            
            fun_gained = player.needs['fun'] - old_fun
            sleep_gained = player.needs['sleep'] - old_sleep
            
            if fun_gained > 0:
                return f"📺 You relax on the couch and watch your favorite shows! Restored {int(fun_gained * 100)}% fun and {int(sleep_gained * 100)}% sleep. This is the perfect way to unwind!"
            else:
                return "📺 You spend some peaceful time relaxing in your cozy living room."
        return "📺 You enjoy relaxing in your comfortable living room."
    
    def _use_bathroom(self, player) -> str:
        """Player uses bathroom facilities"""
        if hasattr(player, 'needs'):
            old_sleep = player.needs.get('sleep', 0)
            old_fun = player.needs.get('fun', 0)
            old_social = player.needs.get('social', 0)
            
            # Bathroom use provides small boosts to multiple needs
            player.needs['sleep'] = min(1.0, player.needs.get('sleep', 0) + 0.1)
            player.needs['fun'] = min(1.0, player.needs.get('fun', 0) + 0.05)
            player.needs['social'] = min(1.0, player.needs.get('social', 0) + 0.05)
            
            sleep_gained = player.needs['sleep'] - old_sleep
            fun_gained = player.needs['fun'] - old_fun
            social_gained = player.needs['social'] - old_social
            
            return f"🚿 You freshen up and feel much better! Restored {int(sleep_gained * 100)}% sleep, {int(fun_gained * 100)}% fun, and {int(social_gained * 100)}% social. Ready to face the world!"
        return "🚿 You use the bathroom facilities."
    
    def _use_stove(self, player) -> str:
        """Player uses the stove"""
        if hasattr(player, 'needs'):
            old_hunger = player.needs.get('hunger', 0)
            old_fun = player.needs.get('fun', 0)
            
            player.needs['hunger'] = min(1.0, player.needs['hunger'] + 0.6)
            player.needs['fun'] = min(1.0, player.needs.get('fun', 0) + 0.15)
            
            hunger_restored = player.needs['hunger'] - old_hunger
            fun_gained = player.needs['fun'] - old_fun
            
            if hunger_restored > 0:
                return f"🍳 You cook a hot, delicious meal on the stove! The aroma fills the kitchen. Restored {int(hunger_restored * 100)}% hunger and {int(fun_gained * 100)}% fun."
            else:
                return "🍳 You're not hungry, but you enjoy cooking something special on your stove."
        return "🍳 You use the stove to cook a meal."
    
    def _use_refrigerator(self, player) -> str:
        """Player uses the refrigerator"""
        if hasattr(player, 'needs'):
            old_hunger = player.needs.get('hunger', 0)
            
            player.needs['hunger'] = min(1.0, player.needs['hunger'] + 0.4)
            
            hunger_restored = player.needs['hunger'] - old_hunger
            
            if hunger_restored > 0:
                return f"🧊 You grab some fresh snacks and drinks from the fridge! Restored {int(hunger_restored * 100)}% hunger. Cold and refreshing!"
            else:
                return "🧊 You browse through your well-stocked refrigerator but you're not hungry right now."
        return "🧊 You check what's in the refrigerator."
    
    def _use_table(self, player) -> str:
        """Player uses the dining table"""
        if hasattr(player, 'needs'):
            old_social = player.needs.get('social', 0)
            old_fun = player.needs.get('fun', 0)
            
            player.needs['social'] = min(1.0, player.needs['social'] + 0.2)
            player.needs['fun'] = min(1.0, player.needs.get('fun', 0) + 0.1)
            
            social_gained = player.needs['social'] - old_social
            fun_gained = player.needs['fun'] - old_fun
            
            return f"🍽️ You sit at your dining table and enjoy a peaceful meal! Restored {int(social_gained * 100)}% social and {int(fun_gained * 100)}% fun. A proper dining experience!"
        return "🍽️ You sit at your dining table."
    
    def _use_couch(self, player) -> str:
        """Player uses the couch"""
        if hasattr(player, 'needs'):
            old_fun = player.needs.get('fun', 0)
            old_sleep = player.needs.get('sleep', 0)
            
            player.needs['fun'] = min(1.0, player.needs['fun'] + 0.3)
            player.needs['sleep'] = min(1.0, player.needs.get('sleep', 0) + 0.15)
            
            fun_gained = player.needs['fun'] - old_fun
            sleep_gained = player.needs['sleep'] - old_sleep
            
            return f"🛋️ You sink into your comfortable couch and relax! Restored {int(fun_gained * 100)}% fun and {int(sleep_gained * 100)}% sleep. So cozy!"
        return "🛋️ You relax on your comfortable couch."
    
    def _use_tv(self, player) -> str:
        """Player watches TV"""
        if hasattr(player, 'needs'):
            old_fun = player.needs.get('fun', 0)
            
            player.needs['fun'] = min(1.0, player.needs['fun'] + 0.5)
            
            fun_gained = player.needs['fun'] - old_fun
            
            return f"📺 You watch your favorite shows and movies! Restored {int(fun_gained * 100)}% fun. Great entertainment!"
        return "📺 You watch television."
    
    def _use_bookshelf(self, player) -> str:
        """Player reads from bookshelf"""
        if hasattr(player, 'needs'):
            old_fun = player.needs.get('fun', 0)
            old_social = player.needs.get('social', 0)
            
            player.needs['fun'] = min(1.0, player.needs['fun'] + 0.25)
            player.needs['social'] = min(1.0, player.needs.get('social', 0) + 0.1)
            
            fun_gained = player.needs['fun'] - old_fun
            social_gained = player.needs['social'] - old_social
            
            return f"📚 You read an interesting book from your collection! Restored {int(fun_gained * 100)}% fun and {int(social_gained * 100)}% social. Knowledge is power!"
        return "📚 You browse through your book collection."
    
    def _use_dresser(self, player) -> str:
        """Player uses the dresser"""
        if hasattr(player, 'needs'):
            old_social = player.needs.get('social', 0)
            old_fun = player.needs.get('fun', 0)
            
            player.needs['social'] = min(1.0, player.needs['social'] + 0.15)
            player.needs['fun'] = min(1.0, player.needs.get('fun', 0) + 0.1)
            
            social_gained = player.needs['social'] - old_social
            fun_gained = player.needs['fun'] - old_fun
            
            return f"👗 You organize your clothes and pick out a nice outfit! Restored {int(social_gained * 100)}% social and {int(fun_gained * 100)}% fun. Looking good!"
        return "👗 You organize your clothes in the dresser."
    
    def _use_toilet(self, player) -> str:
        """Player uses the toilet"""
        if hasattr(player, 'needs'):
            old_sleep = player.needs.get('sleep', 0)
            old_fun = player.needs.get('fun', 0)
            
            player.needs['sleep'] = min(1.0, player.needs.get('sleep', 0) + 0.1)
            player.needs['fun'] = min(1.0, player.needs.get('fun', 0) + 0.05)
            
            sleep_gained = player.needs['sleep'] - old_sleep
            fun_gained = player.needs['fun'] - old_fun
            
            return f"🚽 You use the toilet and feel relieved! Restored {int(sleep_gained * 100)}% sleep and {int(fun_gained * 100)}% fun. Much better!"
        return "🚽 You use the toilet."
    
    def _use_sink(self, player) -> str:
        """Player uses the bathroom sink"""
        if hasattr(player, 'needs'):
            old_social = player.needs.get('social', 0)
            old_sleep = player.needs.get('sleep', 0)
            
            player.needs['social'] = min(1.0, player.needs.get('social', 0) + 0.1)
            player.needs['sleep'] = min(1.0, player.needs.get('sleep', 0) + 0.05)
            
            social_gained = player.needs['social'] - old_social
            sleep_gained = player.needs['sleep'] - old_sleep
            
            return f"🚿 You wash your hands and face at the sink! Restored {int(social_gained * 100)}% social and {int(sleep_gained * 100)}% sleep. Fresh and clean!"
        return "🚿 You wash up at the sink."
    
    def draw(self, screen: pygame.Surface, camera=None, player_pos=None):
        """Draw the house interior"""
        # Clear screen with house interior background
        screen.fill((139, 120, 93))  # Warm wooden floor color
        
        # Try to use farmhouse interior background if available
        background = self.assets.get_scene_background("farmhouse_interior")
        if background:
            # Scale background to fit screen
            scaled_bg = pygame.transform.scale(background, (SCREEN_WIDTH, SCREEN_HEIGHT))
            screen.blit(scaled_bg, (0, 0))
        else:
            # Draw simple room layout
            self._draw_room_layout(screen)
        
        # Draw furniture and items
        self._draw_house_items(screen, player_pos)
        
        # Draw room labels
        self._draw_room_labels(screen)
    
    def _draw_room_layout(self, screen: pygame.Surface):
        """Draw basic room layout when no background image is available"""
        # Draw room areas with different floor colors
        pygame.draw.rect(screen, (160, 140, 120), self.sleeping_area)  # Bedroom
        pygame.draw.rect(screen, (180, 160, 140), self.kitchen_area)   # Kitchen
        pygame.draw.rect(screen, (150, 130, 110), self.living_area)    # Living room
        
        # Draw bathroom area
        bathroom_area = pygame.Rect(280, 100, 100, 120)
        pygame.draw.rect(screen, (170, 150, 130), bathroom_area)  # Bathroom
        
        # Draw walls
        wall_color = (101, 67, 33)
        wall_thickness = 8
        
        # Outer walls (leave gap for door)
        pygame.draw.rect(screen, wall_color, (0, 0, self.width, wall_thickness))  # Top
        pygame.draw.rect(screen, wall_color, (0, 0, wall_thickness, self.height))  # Left
        pygame.draw.rect(screen, wall_color, (self.width - wall_thickness, 0, wall_thickness, self.height))  # Right
        
        # Bottom wall with door gap
        door_gap_start = SCREEN_WIDTH // 2 - 30
        door_gap_end = SCREEN_WIDTH // 2 + 30
        pygame.draw.rect(screen, wall_color, (0, self.height - wall_thickness, door_gap_start, wall_thickness))  # Bottom left
        pygame.draw.rect(screen, wall_color, (door_gap_end, self.height - wall_thickness, self.width - door_gap_end, wall_thickness))  # Bottom right
    
    def _draw_house_items(self, screen: pygame.Surface, player_pos=None):
        """Draw all furniture and interactive items"""
        for item in self.items:
            # Try to get sprite for item, fallback to colored rectangle
            sprite = self.assets.get_sprite(item.item_type)
            
            if sprite:
                # Scale sprite to item size
                scaled_sprite = pygame.transform.scale(sprite, (item.width, item.height))
                screen.blit(scaled_sprite, (item.x, item.y))
            else:
                # Fallback colored rectangles
                colors = {
                    "bed": (200, 150, 100),
                    "dresser": (139, 69, 19),
                    "stove": (169, 169, 169),
                    "refrigerator": (255, 255, 255),
                    "table": (160, 82, 45),
                    "couch": (75, 0, 130),
                    "tv": (0, 0, 0),
                    "bookshelf": (139, 69, 19),
                    "toilet": (255, 255, 255),
                    "sink": (192, 192, 192),
                    "door": (139, 69, 19)
                }
                
                color = colors.get(item.item_type, (128, 128, 128))
                pygame.draw.rect(screen, color, item.rect)
                
                # Add border
                pygame.draw.rect(screen, (0, 0, 0), item.rect, 2)
            
            # Draw item label and interaction hint
            font = pygame.font.Font(None, 16)
            label_text = item.item_type.replace('_', ' ').title()
            text_surface = font.render(label_text, True, (255, 255, 255))
            text_rect = text_surface.get_rect()
            text_rect.centerx = item.rect.centerx
            text_rect.bottom = item.rect.top - 5
            
            # Draw text background
            bg_rect = text_rect.inflate(6, 2)
            pygame.draw.rect(screen, (0, 0, 0, 180), bg_rect)
            screen.blit(text_surface, text_rect)
            
            # Check if player is nearby for interaction highlighting
            is_nearby = False
            if player_pos and item.interactable:
                player_center_x, player_center_y = player_pos
                item_center_x = item.x + item.width // 2
                item_center_y = item.y + item.height // 2
                distance = ((player_center_x - item_center_x) ** 2 + (player_center_y - item_center_y) ** 2) ** 0.5
                is_nearby = distance <= 60  # Interaction range
            
            # Draw interaction indicator (small E icon)
            if item.interactable:
                e_font = pygame.font.Font(None, 14)
                e_color = (150, 255, 150) if is_nearby else (100, 255, 100)
                e_text = e_font.render("E", True, e_color)
                e_rect = e_text.get_rect()
                e_rect.centerx = item.rect.centerx
                e_rect.top = item.rect.bottom + 5
                
                # Draw background circle (brighter if nearby)
                bg_alpha = 200 if is_nearby else 150
                circle_color = (150, 255, 150) if is_nearby else (100, 255, 100)
                pygame.draw.circle(screen, (0, 0, 0, bg_alpha), e_rect.center, 10)
                pygame.draw.circle(screen, circle_color, e_rect.center, 10, 2)
                screen.blit(e_text, e_rect)
                
                # Draw interaction range highlight if nearby
                if is_nearby:
                    highlight_rect = item.rect.inflate(10, 10)
                    pygame.draw.rect(screen, (255, 255, 100, 100), highlight_rect, 3)
    
    def _draw_room_labels(self, screen: pygame.Surface):
        """Draw labels for different room areas"""
        font = pygame.font.Font(None, 20)
        
        labels = [
            ("Bedroom", self.sleeping_area.centerx, self.sleeping_area.top + 10),
            ("Kitchen", self.kitchen_area.centerx, self.kitchen_area.top + 10),
            ("Living Room", self.living_area.centerx, self.living_area.top + 10),
            ("Bathroom", 330, 130),
        ]
        
        for label, x, y in labels:
            text_surface = font.render(label, True, (255, 255, 255))
            text_rect = text_surface.get_rect(center=(x, y))
            
            # Draw text background
            bg_rect = text_rect.inflate(10, 4)
            pygame.draw.rect(screen, (0, 0, 0, 120), bg_rect)
            
            screen.blit(text_surface, text_rect)