from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

# Import quest types for integration
try:
    from src.systems.quest_system import ObjectiveType
except ImportError:
    ObjectiveType = None

class ItemType(Enum):
    RESOURCE = "resource"
    TOOL = "tool"
    FOOD = "food"
    CRAFTED = "crafted"
    SEED = "seed"
    CROP = "crop"
    FISH = "fish"
    MINERAL = "mineral"
    ARTIFACT = "artifact"
    FURNITURE = "furniture"

class ItemRarity(Enum):
    COMMON = "common"
    UNCOMMON = "uncommon"
    RARE = "rare"
    EPIC = "epic"
    LEGENDARY = "legendary"

@dataclass
class ItemData:
    """Data for a single item type"""
    item_id: str
    name: str
    description: str
    item_type: ItemType
    rarity: ItemRarity
    icon: str
    base_value: int
    max_stack: int
    weight: float = 0.1  # Weight in kg per item
    can_sell: bool = True
    can_gift: bool = True

@dataclass
class InventoryItem:
    """An item instance in inventory"""
    item_id: str
    quantity: int
    quality: int = 1  # 1-5 star quality like Stardew Valley

class InventorySystem:
    """
    Manages player inventory and items similar to Stardew Valley
    """
    
    def __init__(self, max_slots: int = 36, quest_system=None, player=None):
        self.max_slots = max_slots
        self.items: Dict[str, InventoryItem] = {}  # item_id -> InventoryItem
        self.money = 500  # Starting gold
        self.item_database: Dict[str, ItemData] = {}
        self.quest_system = quest_system
        self.player = player  # Reference to player for weight updates
        self._initialize_item_database()
    
    def _initialize_item_database(self):
        """Initialize all available items with weights"""
        # Format: (id, name, desc, type, rarity, icon, value, max_stack, weight)
        items = [
            # Resources - heavier materials
            ("wood", "Wood", "Basic building material", ItemType.RESOURCE, ItemRarity.COMMON, "🪵", 2, 999, 0.5),
            ("stone", "Stone", "Common mineral for building", ItemType.RESOURCE, ItemRarity.COMMON, "🪨", 2, 999, 1.0),
            ("clay", "Clay", "Malleable earth material", ItemType.RESOURCE, ItemRarity.COMMON, "🧱", 3, 999, 0.8),
            ("fiber", "Fiber", "Plant material for crafting", ItemType.RESOURCE, ItemRarity.COMMON, "🌾", 1, 999, 0.05),
            
            # Seeds - very light
            ("parsnip_seeds", "Parsnip Seeds", "Takes 4 days to mature", ItemType.SEED, ItemRarity.COMMON, "🌱", 20, 999, 0.01),
            ("cauliflower_seeds", "Cauliflower Seeds", "Takes 12 days to mature", ItemType.SEED, ItemRarity.COMMON, "🌱", 80, 999, 0.01),
            ("potato_seeds", "Potato Seeds", "Takes 6 days to mature", ItemType.SEED, ItemRarity.COMMON, "🌱", 50, 999, 0.01),
            ("tomato_seeds", "Tomato Seeds", "Takes 11 days to mature", ItemType.SEED, ItemRarity.UNCOMMON, "🌱", 50, 999, 0.01),
            
            # Crops - moderate weight
            ("parsnip", "Parsnip", "A basic root vegetable", ItemType.CROP, ItemRarity.COMMON, "🥕", 35, 999, 0.2),
            ("cauliflower", "Cauliflower", "A valuable vegetable", ItemType.CROP, ItemRarity.COMMON, "🥬", 175, 999, 0.5),
            ("potato", "Potato", "A common and filling tuber", ItemType.CROP, ItemRarity.COMMON, "🥔", 80, 999, 0.3),
            ("tomato", "Tomato", "A juicy red fruit", ItemType.CROP, ItemRarity.UNCOMMON, "🍅", 60, 999, 0.1),
            
            # Fish
            ("carp", "Carp", "A common river fish", ItemType.FISH, ItemRarity.COMMON, "🐟", 30, 999),
            ("salmon", "Salmon", "A large valuable fish", ItemType.FISH, ItemRarity.UNCOMMON, "🐟", 75, 999),
            ("tuna", "Tuna", "A deep ocean fish", ItemType.FISH, ItemRarity.RARE, "🐟", 100, 999),
            ("legendary_fish", "Legendary Fish", "An incredibly rare catch", ItemType.FISH, ItemRarity.LEGENDARY, "🐠", 1000, 1),
            
            # Minerals
            ("copper_ore", "Copper Ore", "A common metal ore", ItemType.MINERAL, ItemRarity.COMMON, "🟤", 5, 999),
            ("iron_ore", "Iron Ore", "A useful metal ore", ItemType.MINERAL, ItemRarity.UNCOMMON, "⚫", 10, 999),
            ("gold_ore", "Gold Ore", "A precious metal ore", ItemType.MINERAL, ItemRarity.RARE, "🟡", 25, 999),
            ("iridium_ore", "Iridium Ore", "The rarest metal ore", ItemType.MINERAL, ItemRarity.EPIC, "💜", 100, 999),
            
            # Gems
            ("quartz", "Quartz", "A clear crystal", ItemType.MINERAL, ItemRarity.COMMON, "🔹", 25, 999),
            ("amethyst", "Amethyst", "A purple gemstone", ItemType.MINERAL, ItemRarity.UNCOMMON, "💎", 100, 999),
            ("diamond", "Diamond", "A brilliant precious stone", ItemType.MINERAL, ItemRarity.RARE, "💎", 750, 999),
            ("prismatic_shard", "Prismatic Shard", "A very rare and powerful gem", ItemType.MINERAL, ItemRarity.LEGENDARY, "🌟", 2000, 999),
            
            # Food
            ("bread", "Bread", "A basic food item", ItemType.FOOD, ItemRarity.COMMON, "🍞", 50, 999),
            ("salad", "Salad", "A healthy vegetable dish", ItemType.FOOD, ItemRarity.COMMON, "🥗", 75, 999),
            ("pizza", "Pizza", "A delicious cooked meal", ItemType.FOOD, ItemRarity.UNCOMMON, "🍕", 150, 999),
            ("lobster_bisque", "Lobster Bisque", "A gourmet soup", ItemType.FOOD, ItemRarity.RARE, "🍲", 500, 999),
            
            # Tools - heavy items
            ("basic_axe", "Basic Axe", "Chops wood efficiently", ItemType.TOOL, ItemRarity.COMMON, "🪓", 200, 1, 3.0),
            ("basic_pickaxe", "Basic Pickaxe", "Breaks rocks and mines ore", ItemType.TOOL, ItemRarity.COMMON, "⛏️", 200, 1, 4.0),
            ("basic_hoe", "Basic Hoe", "Tills soil for planting", ItemType.TOOL, ItemRarity.COMMON, "🪓", 150, 1, 2.5),
            ("basic_watering_can", "Basic Watering Can", "Waters crops", ItemType.TOOL, ItemRarity.COMMON, "🪣", 150, 1, 1.0),
            ("fishing_rod", "Fishing Rod", "Catches fish in water", ItemType.TOOL, ItemRarity.COMMON, "🎣", 300, 1, 0.8),
            
            # Forageable items
            ("wild_berries", "Wild Berries", "Sweet berries found in the wild", ItemType.FOOD, ItemRarity.COMMON, "🫐", 25, 999),
            ("mushrooms", "Mushrooms", "Earthy mushrooms from rotting logs", ItemType.FOOD, ItemRarity.UNCOMMON, "🍄", 40, 999),
            ("herbs", "Herbs", "Medicinal and cooking herbs", ItemType.RESOURCE, ItemRarity.COMMON, "🌿", 15, 999),
            
            # Processed materials
            ("coal", "Coal", "Fuel for furnaces and forges", ItemType.RESOURCE, ItemRarity.COMMON, "⚫", 15, 999),
            ("copper_bar", "Copper Bar", "Refined copper for crafting", ItemType.RESOURCE, ItemRarity.COMMON, "🟤", 60, 999),
            ("iron_bar", "Iron Bar", "Strong iron bar for tools", ItemType.RESOURCE, ItemRarity.UNCOMMON, "⚫", 120, 999),
            ("gold_bar", "Gold Bar", "Precious gold bar", ItemType.RESOURCE, ItemRarity.RARE, "🟡", 250, 999),
            
            # Advanced items
            ("grapes", "Grapes", "Sweet purple grapes", ItemType.CROP, ItemRarity.UNCOMMON, "🍇", 60, 999),
            ("milk", "Milk", "Fresh cow's milk", ItemType.RESOURCE, ItemRarity.COMMON, "🥛", 40, 999),
            ("cheese", "Cheese", "Aged cheese made from milk", ItemType.FOOD, ItemRarity.UNCOMMON, "🧀", 120, 999),
            ("wine", "Wine", "Fine wine made from grapes", ItemType.FOOD, ItemRarity.RARE, "🍷", 300, 999),
            ("wheat", "Wheat", "Golden grain for baking", ItemType.CROP, ItemRarity.COMMON, "🌾", 25, 999),
            
            # Upgraded tools
            ("copper_axe", "Copper Axe", "Upgraded axe that cuts faster", ItemType.TOOL, ItemRarity.UNCOMMON, "🪓", 500, 1),
            ("copper_pickaxe", "Copper Pickaxe", "Upgraded pickaxe for better mining", ItemType.TOOL, ItemRarity.UNCOMMON, "⛏️", 500, 1),
            
            # Crafted Items
            ("chest", "Chest", "Stores items safely", ItemType.FURNITURE, ItemRarity.COMMON, "📦", 50, 999),
            ("scarecrow", "Scarecrow", "Protects crops from crows", ItemType.CRAFTED, ItemRarity.COMMON, "🤖", 100, 999),
            ("mayo_machine", "Mayonnaise Machine", "Turns eggs into mayonnaise", ItemType.CRAFTED, ItemRarity.UNCOMMON, "🏭", 1000, 1),
            ("preserve_jar", "Preserves Jar", "Makes preserves and pickles", ItemType.CRAFTED, ItemRarity.UNCOMMON, "🏺", 750, 1),
        ]
        
        # Update all other items with default weights based on type
        default_weights = {
            ItemType.FISH: 0.3,
            ItemType.MINERAL: 0.5,
            ItemType.FOOD: 0.2,
            ItemType.RESOURCE: 0.3,
            ItemType.CRAFTED: 2.0,
            ItemType.FURNITURE: 5.0
        }
        
        for item_data in items:
            if len(item_data) == 9:  # New format with weight
                item_id, name, desc, item_type, rarity, icon, value, max_stack, weight = item_data
            else:  # Old format without weight - use default
                item_id, name, desc, item_type, rarity, icon, value, max_stack = item_data
                weight = default_weights.get(item_type, 0.1)
            
            self.item_database[item_id] = ItemData(
                item_id=item_id,
                name=name,
                description=desc,
                item_type=item_type,
                rarity=rarity,
                icon=icon,
                base_value=value,
                max_stack=max_stack,
                weight=weight
            )
    
    def add_item(self, item_id: str, quantity: int = 1, quality: int = 1) -> bool:
        """Add item to inventory. Returns True if successful."""
        if item_id not in self.item_database:
            return False
        
        item_data = self.item_database[item_id]
        
        # Check weight limit if player is set
        if self.player:
            item_weight = item_data.weight * quantity
            if not self.player.can_carry_weight(item_weight):
                return False  # Too heavy to carry
        
        # Check if we can stack with existing item
        if item_id in self.items:
            existing = self.items[item_id]
            if existing.quality == quality:  # Can only stack same quality
                space_available = item_data.max_stack - existing.quantity
                can_add = min(quantity, space_available)
                existing.quantity += can_add
                return can_add == quantity
        
        # Check if we have space for new item
        if len(self.items) >= self.max_slots and item_id not in self.items:
            return False  # Inventory full
        
        # Add new item or create new stack
        if item_id in self.items and self.items[item_id].quality != quality:
            # Different quality, need new slot but inventory might be full
            return False
        else:
            # Add to existing or create new
            add_quantity = min(quantity, item_data.max_stack)
            self.items[item_id] = InventoryItem(item_id, add_quantity, quality)
            
            # Update player weight if applicable
            if self.player:
                self.player.add_inventory_weight(item_data.weight * add_quantity)
            
            return add_quantity == quantity
    
    def remove_item(self, item_id: str, quantity: int = 1) -> bool:
        """Remove item from inventory. Returns True if successful."""
        if item_id not in self.items:
            return False
        
        item = self.items[item_id]
        if item.quantity < quantity:
            return False
        
        # Update player weight if applicable
        if self.player and item_id in self.item_database:
            item_data = self.item_database[item_id]
            self.player.remove_inventory_weight(item_data.weight * quantity)
        
        item.quantity -= quantity
        if item.quantity <= 0:
            del self.items[item_id]
        
        return True
    
    def has_item(self, item_id: str, quantity: int = 1) -> bool:
        """Check if inventory has enough of an item"""
        if item_id not in self.items:
            return False
        return self.items[item_id].quantity >= quantity
    
    def get_item_count(self, item_id: str) -> int:
        """Get count of an item in inventory"""
        if item_id not in self.items:
            return 0
        return self.items[item_id].quantity
    
    def get_item_value(self, item_id: str, quality: int = 1) -> int:
        """Get the value of an item considering quality"""
        if item_id not in self.item_database:
            return 0
        
        base_value = self.item_database[item_id].base_value
        # Quality multiplier: 1x, 1.25x, 1.5x, 1.75x, 2x for 1-5 star
        quality_multiplier = 1.0 + ((quality - 1) * 0.25)
        return int(base_value * quality_multiplier)
    
    def sell_item(self, item_id: str, quantity: int = 1) -> bool:
        """Sell item for money. Returns True if successful."""
        if not self.has_item(item_id, quantity):
            return False
        
        if item_id not in self.item_database or not self.item_database[item_id].can_sell:
            return False
        
        item = self.items[item_id]
        value_per_item = self.get_item_value(item_id, item.quality)
        total_value = value_per_item * quantity
        
        if self.remove_item(item_id, quantity):
            self.money += total_value
            return True
        
        return False
    
    def get_items_by_type(self, item_type: ItemType) -> Dict[str, InventoryItem]:
        """Get all items of a specific type"""
        result = {}
        for item_id, inv_item in self.items.items():
            if item_id in self.item_database:
                if self.item_database[item_id].item_type == item_type:
                    result[item_id] = inv_item
        return result
    
    def get_item_data(self, item_id: str) -> Optional[ItemData]:
        """Get item data from database"""
        return self.item_database.get(item_id)
    
    def get_all_items(self) -> Dict[str, InventoryItem]:
        """Get all items in inventory"""
        return self.items.copy()
    
    def get_total_weight(self) -> float:
        """Calculate total weight of all items in inventory"""
        total_weight = 0.0
        for item_id, inv_item in self.items.items():
            if item_id in self.item_database:
                item_data = self.item_database[item_id]
                total_weight += item_data.weight * inv_item.quantity
        return total_weight
    
    def set_player(self, player):
        """Set the player reference for weight management"""
        self.player = player
        # Recalculate weight
        if self.player:
            self.player.inventory_weight = self.get_total_weight()
    
    def get_inventory_slots_used(self) -> int:
        """Get number of inventory slots used"""
        return len(self.items)
    
    def add_money(self, amount: int):
        """Add money to player"""
        self.money += amount
    
    def spend_money(self, amount: int) -> bool:
        """Spend money. Returns True if successful."""
        if self.money >= amount:
            self.money -= amount
            
            # Update quest objectives for spending money
            if self.quest_system and ObjectiveType:
                try:
                    self.quest_system.update_objective(ObjectiveType.SPEND_MONEY, "shop", amount)
                except Exception as e:
                    print(f"Error updating quest objectives for money spending: {e}")
            
            return True
        return False
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for saving"""
        return {
            "money": self.money,
            "max_slots": self.max_slots,
            "items": {
                item_id: {
                    "quantity": item.quantity,
                    "quality": item.quality
                } for item_id, item in self.items.items()
            }
        }
    
    def from_dict(self, data: Dict):
        """Load from dictionary"""
        self.money = data.get("money", 500)
        self.max_slots = data.get("max_slots", 36)
        
        self.items.clear()
        if "items" in data:
            for item_id, item_data in data["items"].items():
                if item_id in self.item_database:
                    inv_item = InventoryItem(
                        item_id=item_id,
                        quantity=item_data.get("quantity", 1),
                        quality=item_data.get("quality", 1)
                    )
                    self.items[item_id] = inv_item
                    
                    # Update player weight if applicable
                    if self.player:
                        item_weight = self.item_database[item_id].weight * inv_item.quantity
                        self.player.add_inventory_weight(item_weight)