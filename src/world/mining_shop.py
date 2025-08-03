import pygame
import random
from typing import Dict, List, Optional, Tuple
from src.core.constants import *
from src.systems.inventory_system import InventorySystem, ItemType, ItemRarity

class MiningShop:
    """
    Mining shop where players can buy mining equipment and sell mined goods
    """
    
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y
        self.rect = pygame.Rect(x, y, 64, 64)  # Shop building size
        
        # Shop properties
        self.name = "Rocky's Mining Supplies"
        self.shopkeeper_name = "Rocky"
        self.is_open = True
        
        # Shop inventory - items the shop sells
        self.shop_inventory = self._initialize_shop_inventory()
        
        # Items the shop buys (with multipliers)
        self.buy_prices = self._initialize_buy_prices()
        
        # Shop money (for buying from player)
        self.shop_money = 10000
        
        # Daily stock refresh
        self.last_refresh_day = 0
        
    def _initialize_shop_inventory(self) -> Dict[str, Dict]:
        """Initialize items the shop sells"""
        return {
            # Basic mining tools
            "basic_pickaxe": {
                "price": 500,
                "stock": 3,
                "max_stock": 5,
                "description": "A sturdy pickaxe for mining stone and ore"
            },
            "copper_pickaxe": {
                "price": 1200,
                "stock": 2,
                "max_stock": 3,
                "description": "Upgraded pickaxe that mines faster"
            },
            "iron_pickaxe": {
                "price": 2500,
                "stock": 1,
                "max_stock": 2,
                "description": "High-quality pickaxe for tough minerals"
            },
            
            # Mining supplies
            "mining_helmet": {
                "price": 300,
                "stock": 5,
                "max_stock": 8,
                "description": "Provides light in dark mines"
            },
            "torch": {
                "price": 10,
                "stock": 20,
                "max_stock": 50,
                "description": "Essential lighting for underground exploration"
            },
            "rope": {
                "price": 25,
                "stock": 15,
                "max_stock": 30,
                "description": "Useful for accessing deep mining areas"
            },
            
            # Processed materials
            "coal": {
                "price": 25,
                "stock": 30,
                "max_stock": 50,
                "description": "Fuel for smelting and forging"
            },
            "copper_bar": {
                "price": 120,
                "stock": 10,
                "max_stock": 15,
                "description": "Refined copper for crafting"
            },
            "iron_bar": {
                "price": 250,
                "stock": 5,
                "max_stock": 10,
                "description": "Strong iron bar for advanced tools"
            },
            
            # Special items
            "dynamite": {
                "price": 200,
                "stock": 3,
                "max_stock": 5,
                "description": "Explosive for clearing large rock formations"
            },
            "mining_cart": {
                "price": 1500,
                "stock": 1,
                "max_stock": 1,
                "description": "Increases carrying capacity in mines"
            },
            "gem_detector": {
                "price": 3000,
                "stock": 1,
                "max_stock": 1,
                "description": "Helps locate precious gems underground"
            }
        }
    
    def _initialize_buy_prices(self) -> Dict[str, float]:
        """Initialize prices the shop pays for items (as multiplier of base value)"""
        return {
            # Raw materials - shop pays well for these
            "stone": 1.2,
            "copper_ore": 1.5,
            "iron_ore": 1.4,
            "gold_ore": 1.3,
            "iridium_ore": 1.2,
            
            # Gems - premium prices
            "quartz": 1.6,
            "amethyst": 1.5,
            "diamond": 1.4,
            "prismatic_shard": 1.8,
            
            # Coal and common mining materials
            "coal": 1.1,
            "clay": 1.3,
            
            # Processed bars - slightly lower than raw ore
            "copper_bar": 0.9,
            "iron_bar": 0.9,
            "gold_bar": 0.9,
            
            # Other materials
            "fiber": 0.8,
            "wood": 0.7,
        }
    
    def get_buy_price(self, item_id: str, base_value: int, quality: int = 1) -> int:
        """Calculate how much the shop will pay for an item"""
        multiplier = self.buy_prices.get(item_id, 0.6)  # Default 60% of base value
        
        # Quality affects price
        quality_multiplier = 1.0 + ((quality - 1) * 0.25)
        
        return int(base_value * multiplier * quality_multiplier)
    
    def get_sell_price(self, item_id: str) -> int:
        """Get the price the shop sells an item for"""
        if item_id in self.shop_inventory:
            return self.shop_inventory[item_id]["price"]
        return 0
    
    def can_buy_from_player(self, item_id: str, quantity: int = 1) -> bool:
        """Check if shop can buy item from player"""
        if item_id not in self.buy_prices:
            return False
        
        # Check if shop has enough money (approximate check)
        return self.shop_money > 100  # Always has some money for buying
    
    def can_sell_to_player(self, item_id: str, quantity: int = 1) -> bool:
        """Check if shop can sell item to player"""
        if item_id not in self.shop_inventory:
            return False
        
        return self.shop_inventory[item_id]["stock"] >= quantity
    
    def buy_from_player(self, item_id: str, base_value: int, quantity: int = 1, quality: int = 1) -> int:
        """Shop buys item from player, returns total price paid"""
        if not self.can_buy_from_player(item_id, quantity):
            return 0
        
        price_per_item = self.get_buy_price(item_id, base_value, quality)
        total_price = price_per_item * quantity
        
        # Deduct from shop money (but don't let it go below minimum)
        self.shop_money = max(1000, self.shop_money - total_price)
        
        return total_price
    
    def sell_to_player(self, item_id: str, quantity: int = 1) -> bool:
        """Shop sells item to player"""
        if not self.can_sell_to_player(item_id, quantity):
            return False
        
        self.shop_inventory[item_id]["stock"] -= quantity
        
        # Add money to shop
        price = self.get_sell_price(item_id) * quantity
        self.shop_money += price
        
        return True
    
    def refresh_stock(self, current_day: int):
        """Refresh shop stock daily"""
        if current_day != self.last_refresh_day:
            self.last_refresh_day = current_day
            
            # Restock items
            for item_id, item_data in self.shop_inventory.items():
                max_stock = item_data["max_stock"]
                current_stock = item_data["stock"]
                
                # Restock 30-70% of missing items
                missing = max_stock - current_stock
                if missing > 0:
                    restock_amount = random.randint(int(missing * 0.3), int(missing * 0.7))
                    item_data["stock"] = min(max_stock, current_stock + restock_amount)
            
            # Occasionally add special items or adjust prices
            if random.random() < 0.1:  # 10% chance
                self._add_special_daily_item()
    
    def _add_special_daily_item(self):
        """Occasionally add special limited items"""
        special_items = [
            {
                "id": "golden_pickaxe",
                "price": 5000,
                "stock": 1,
                "description": "Rare golden pickaxe with increased mining speed"
            },
            {
                "id": "miners_luck_charm",
                "price": 1000,
                "stock": 1,
                "description": "Increases chance of finding rare gems"
            },
            {
                "id": "cave_map",
                "price": 500,
                "stock": 2,
                "description": "Reveals hidden mining locations"
            }
        ]
        
        special_item = random.choice(special_items)
        if special_item["id"] not in self.shop_inventory:
            self.shop_inventory[special_item["id"]] = {
                "price": special_item["price"],
                "stock": special_item["stock"],
                "max_stock": special_item["stock"],
                "description": special_item["description"],
                "special": True  # Mark as special daily item
            }
    
    def get_greeting(self) -> str:
        """Get shopkeeper greeting"""
        greetings = [
            f"Welcome to {self.name}! I'm {self.shopkeeper_name}.",
            "Looking for mining gear? You've come to the right place!",
            "Got any ore to sell? I pay good prices for quality materials!",
            "Welcome, miner! What can I do for you today?",
            "Fresh tools and supplies, just what every miner needs!"
        ]
        return random.choice(greetings)
    
    def get_farewell(self) -> str:
        """Get shopkeeper farewell"""
        farewells = [
            "Happy mining! Be safe down there!",
            "Come back when you need more supplies!",
            "May your pickaxe stay sharp and your pockets full!",
            "Good luck in the mines!",
            "Thanks for your business!"
        ]
        return random.choice(farewells)
    
    def get_shop_items_for_display(self) -> List[Dict]:
        """Get items formatted for shop UI display"""
        items = []
        for item_id, item_data in self.shop_inventory.items():
            if item_data["stock"] > 0:
                items.append({
                    "id": item_id,
                    "name": item_id.replace("_", " ").title(),
                    "price": item_data["price"],
                    "stock": item_data["stock"],
                    "description": item_data["description"],
                    "is_special": item_data.get("special", False)
                })
        
        # Sort by price, special items first
        items.sort(key=lambda x: (not x["is_special"], x["price"]))
        return items
    
    def get_buyable_items(self, player_inventory: InventorySystem) -> List[Dict]:
        """Get items the shop will buy from player"""
        buyable = []
        
        for item_id, inv_item in player_inventory.get_all_items().items():
            if item_id in self.buy_prices:
                item_data = player_inventory.get_item_data(item_id)
                if item_data:
                    buy_price = self.get_buy_price(item_id, item_data.base_value, inv_item.quality)
                    buyable.append({
                        "id": item_id,
                        "name": item_data.name,
                        "quantity": inv_item.quantity,
                        "quality": inv_item.quality,
                        "buy_price": buy_price,
                        "total_value": buy_price * inv_item.quantity,
                        "description": f"Shop pays {buy_price}g each"
                    })
        
        # Sort by total value, highest first
        buyable.sort(key=lambda x: x["total_value"], reverse=True)
        return buyable
    
    def draw(self, screen, camera):
        """Draw the mining shop building"""
        screen_pos = camera.apply_rect(self.rect)
        
        # Shop building (simple representation)
        # Main building
        pygame.draw.rect(screen, (101, 67, 33), screen_pos)  # Brown building
        pygame.draw.rect(screen, (139, 69, 19), screen_pos, 3)  # Dark brown border
        
        # Roof
        roof_points = [
            (screen_pos.left, screen_pos.top),
            (screen_pos.centerx, screen_pos.top - 15),
            (screen_pos.right, screen_pos.top)
        ]
        pygame.draw.polygon(screen, (160, 82, 45), roof_points)
        
        # Door
        door_rect = pygame.Rect(screen_pos.centerx - 8, screen_pos.bottom - 20, 16, 20)
        pygame.draw.rect(screen, (101, 57, 23), door_rect)
        
        # Window
        window_rect = pygame.Rect(screen_pos.left + 8, screen_pos.centery - 6, 12, 12)
        pygame.draw.rect(screen, (135, 206, 235), window_rect)  # Light blue window
        
        # Shop sign
        sign_rect = pygame.Rect(screen_pos.centerx - 25, screen_pos.top - 8, 50, 12)
        pygame.draw.rect(screen, (160, 82, 45), sign_rect)
        
        # Shop icon (pickaxe)
        font = pygame.font.Font(None, 24)
        icon_surface = font.render("⛏️", True, (255, 255, 255))
        icon_rect = icon_surface.get_rect(center=(screen_pos.centerx, screen_pos.centery - 10))
        screen.blit(icon_surface, icon_rect)
        
        # Shop name
        name_font = pygame.font.Font(None, 16)
        name_surface = name_font.render("Mining Shop", True, (255, 255, 255))
        name_rect = name_surface.get_rect(center=(screen_pos.centerx, screen_pos.bottom + 10))
        
        # Background for text
        text_bg = pygame.Surface((name_rect.width + 4, name_rect.height + 2), pygame.SRCALPHA)
        text_bg.fill((0, 0, 0, 150))
        screen.blit(text_bg, (name_rect.x - 2, name_rect.y - 1))
        screen.blit(name_surface, name_rect)
    
    def is_near_player(self, player_rect: pygame.Rect, interaction_distance: int = 80) -> bool:
        """Check if player is close enough to interact with shop"""
        player_center = player_rect.center
        shop_center = self.rect.center
        
        distance = ((player_center[0] - shop_center[0]) ** 2 + 
                   (player_center[1] - shop_center[1]) ** 2) ** 0.5
        
        return distance <= interaction_distance