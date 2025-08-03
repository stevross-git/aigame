import pygame
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
from src.systems.inventory_system import InventorySystem, ItemData, ItemType, ItemRarity

class ShopType(Enum):
    GEM_SHOP = "gem_shop"
    HARDWARE_STORE = "hardware_store"
    MINING_STORE = "mining_store"
    GENERAL_STORE = "general_store"

@dataclass
class ShopItem:
    """Item available for purchase in a shop"""
    item_id: str
    price: int
    stock: int = -1  # -1 for unlimited stock
    required_level: int = 1
    category: str = "general"

class Shop:
    """Individual shop with inventory and purchasing logic"""
    
    def __init__(self, shop_type: ShopType, name: str, description: str):
        self.shop_type = shop_type
        self.name = name
        self.description = description
        self.items: Dict[str, ShopItem] = {}
        self.markup_multiplier = 1.2  # Shop sells at 20% markup
        self.buyback_multiplier = 0.8  # Shop buys at 80% of value
        
        self._initialize_shop_inventory()
    
    def _initialize_shop_inventory(self):
        """Initialize shop-specific inventory"""
        if self.shop_type == ShopType.GEM_SHOP:
            self._setup_gem_shop()
        elif self.shop_type == ShopType.HARDWARE_STORE:
            self._setup_hardware_store()
        elif self.shop_type == ShopType.MINING_STORE:
            self._setup_mining_store()
    
    def _setup_gem_shop(self):
        """Setup gem shop inventory"""
        gem_items = [
            # Raw gems and materials
            ShopItem("quartz", 30, 20, 1, "gems"),
            ShopItem("amethyst", 120, 15, 3, "gems"),
            ShopItem("diamond", 900, 5, 10, "gems"),
            ShopItem("prismatic_shard", 2500, 2, 20, "rare_gems"),
            
            # Jewelry and accessories
            ShopItem("copper_ring", 100, 10, 1, "jewelry"),
            ShopItem("silver_ring", 250, 8, 5, "jewelry"),
            ShopItem("gold_ring", 500, 5, 10, "jewelry"),
            
            # Gem processing tools
            ShopItem("gem_polisher", 800, 3, 5, "tools"),
            ShopItem("gem_magnifier", 150, 5, 1, "tools"),
            
            # Decorative items
            ShopItem("crystal_lamp", 300, 5, 3, "decoration"),
            ShopItem("gem_display_case", 600, 3, 7, "decoration"),
        ]
        
        for item in gem_items:
            self.items[item.item_id] = item
    
    def _setup_hardware_store(self):
        """Setup hardware store inventory"""
        hardware_items = [
            # Basic tools
            ShopItem("basic_axe", 250, 10, 1, "tools"),
            ShopItem("basic_pickaxe", 250, 10, 1, "tools"),
            ShopItem("basic_hoe", 200, 10, 1, "tools"),
            ShopItem("basic_watering_can", 200, 10, 1, "tools"),
            ShopItem("fishing_rod", 350, 8, 1, "tools"),
            
            # Upgraded tools
            ShopItem("copper_axe", 600, 5, 5, "tools"),
            ShopItem("copper_pickaxe", 600, 5, 5, "tools"),
            ShopItem("iron_axe", 1200, 3, 10, "tools"),
            ShopItem("iron_pickaxe", 1200, 3, 10, "tools"),
            
            # Building materials
            ShopItem("wood", 3, 999, 1, "materials"),
            ShopItem("stone", 3, 999, 1, "materials"),
            ShopItem("clay", 4, 500, 1, "materials"),
            ShopItem("fiber", 2, 999, 1, "materials"),
            
            # Crafting supplies
            ShopItem("chest", 75, 20, 1, "furniture"),
            ShopItem("scarecrow", 150, 10, 3, "farming"),
            ShopItem("mayo_machine", 1200, 5, 8, "machines"),
            ShopItem("preserve_jar", 900, 8, 6, "machines"),
        ]
        
        for item in hardware_items:
            self.items[item.item_id] = item
    
    def _setup_mining_store(self):
        """Setup mining store inventory"""
        mining_items = [
            # Ores and bars
            ShopItem("copper_ore", 8, 200, 1, "ores"),
            ShopItem("iron_ore", 15, 150, 3, "ores"),
            ShopItem("gold_ore", 35, 100, 8, "ores"),
            ShopItem("iridium_ore", 150, 50, 15, "ores"),
            
            ShopItem("copper_bar", 75, 50, 1, "bars"),
            ShopItem("iron_bar", 150, 40, 3, "bars"),
            ShopItem("gold_bar", 300, 25, 8, "bars"),
            
            # Mining equipment
            ShopItem("mining_helmet", 400, 8, 3, "equipment"),
            ShopItem("mining_cart", 1500, 3, 10, "equipment"),
            ShopItem("dynamite", 50, 20, 5, "explosives"),
            ShopItem("coal", 20, 200, 1, "fuel"),
            
            # Gems and minerals
            ShopItem("quartz", 25, 50, 1, "gems"),
            ShopItem("earth_crystal", 80, 30, 5, "gems"),
            ShopItem("fire_crystal", 120, 20, 8, "gems"),
            ShopItem("frozen_crystal", 150, 15, 10, "gems"),
            
            # Processing equipment
            ShopItem("furnace", 500, 5, 3, "machines"),
            ShopItem("crusher", 800, 3, 7, "machines"),
        ]
        
        for item in mining_items:
            self.items[item.item_id] = item
    
    def get_shop_items(self, player_level: int = 1) -> List[ShopItem]:
        """Get items available for purchase based on player level"""
        available_items = []
        for item in self.items.values():
            if item.required_level <= player_level:
                available_items.append(item)
        return available_items
    
    def get_item_price(self, item_id: str, inventory_system: InventorySystem) -> int:
        """Get the selling price of an item"""
        if item_id not in self.items:
            return 0
        
        shop_item = self.items[item_id]
        base_price = shop_item.price
        
        # Apply markup
        return int(base_price * self.markup_multiplier)
    
    def get_buyback_price(self, item_id: str, inventory_system: InventorySystem) -> int:
        """Get the buyback price for selling items to shop"""
        item_data = inventory_system.get_item_data(item_id)
        if not item_data:
            return 0
        
        base_value = item_data.base_value
        return int(base_value * self.buyback_multiplier)
    
    def can_purchase(self, item_id: str, quantity: int, player_money: int, player_level: int = 1) -> bool:
        """Check if player can purchase item"""
        if item_id not in self.items:
            return False
        
        shop_item = self.items[item_id]
        
        # Check level requirement
        if player_level < shop_item.required_level:
            return False
        
        # Check stock
        if shop_item.stock != -1 and shop_item.stock < quantity:
            return False
        
        # Check money
        total_cost = self.get_item_price(item_id, None) * quantity
        if player_money < total_cost:
            return False
        
        return True
    
    def purchase_item(self, item_id: str, quantity: int, inventory_system: InventorySystem) -> Tuple[bool, str]:
        """Attempt to purchase an item"""
        if item_id not in self.items:
            return False, "Item not available"
        
        shop_item = self.items[item_id]
        total_cost = self.get_item_price(item_id, inventory_system) * quantity
        
        # Check if player can afford it
        if inventory_system.money < total_cost:
            return False, f"Not enough money. Need {total_cost}g"
        
        # Check stock
        if shop_item.stock != -1 and shop_item.stock < quantity:
            return False, f"Only {shop_item.stock} in stock"
        
        # Check inventory space
        if not inventory_system.add_item(item_id, quantity):
            return False, "Not enough inventory space"
        
        # Complete the purchase
        inventory_system.spend_money(total_cost)
        
        # Reduce stock if not unlimited
        if shop_item.stock != -1:
            shop_item.stock -= quantity
        
        return True, f"Purchased {quantity}x {item_id} for {total_cost}g"
    
    def sell_item(self, item_id: str, quantity: int, inventory_system: InventorySystem) -> Tuple[bool, str]:
        """Sell item to shop"""
        if not inventory_system.has_item(item_id, quantity):
            return False, "Don't have enough of this item"
        
        item_data = inventory_system.get_item_data(item_id)
        if not item_data or not item_data.can_sell:
            return False, "This item cannot be sold"
        
        total_value = self.get_buyback_price(item_id, inventory_system) * quantity
        
        # Complete the sale
        if inventory_system.remove_item(item_id, quantity):
            inventory_system.add_money(total_value)
            return True, f"Sold {quantity}x {item_id} for {total_value}g"
        
        return False, "Failed to remove item from inventory"

class ShopSystem:
    """Manages all shops in the game world"""
    
    def __init__(self):
        self.shops: Dict[str, Shop] = {}
        self._initialize_shops()
    
    def _initialize_shops(self):
        """Initialize all shops"""
        # Gem Shop
        self.shops["gem_shop"] = Shop(
            ShopType.GEM_SHOP,
            "Crystal & Gems",
            "Fine gems, jewelry, and precious stones"
        )
        
        # Hardware Store
        self.shops["hardware_store"] = Shop(
            ShopType.HARDWARE_STORE,
            "Builder's Supply",
            "Tools, materials, and building supplies"
        )
        
        # Mining Store
        self.shops["mining_store"] = Shop(
            ShopType.MINING_STORE,
            "Deep Earth Mining Co.",
            "Ores, mining equipment, and underground treasures"
        )
    
    def get_shop(self, shop_type: str) -> Optional[Shop]:
        """Get shop by type"""
        return self.shops.get(shop_type)
    
    def get_all_shops(self) -> Dict[str, Shop]:
        """Get all shops"""
        return self.shops