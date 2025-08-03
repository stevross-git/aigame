import pygame
import random
from typing import Dict, List, Optional, Tuple
from src.world.house_interior import HouseInterior, HouseItem
from src.core.constants import *

class NPCHouseAssignment:
    """Represents an NPC's house assignment"""
    def __init__(self, npc_name: str, house_location: Tuple[int, int], house_type: str = "house"):
        self.npc_name = npc_name
        self.house_location = house_location  # (x, y) on the map
        self.house_type = house_type
        self.house_interior = None  # Will be assigned when needed
        self.is_home = False  # Whether NPC is currently at home

class NPCHouseManager:
    """
    Manages house assignments for NPCs and provides house functionality
    """
    
    def __init__(self):
        self.npc_assignments: Dict[str, NPCHouseAssignment] = {}
        self.available_houses = []
        self.house_interiors: Dict[str, HouseInterior] = {}
        self._initialize_available_houses()
    
    def _initialize_available_houses(self):
        """Initialize list of available houses from the map"""
        # These match the house locations from beautiful_map.py
        self.available_houses = [
            {"x": 600, "y": 300, "type": "house"},   # Central-east
            {"x": 1200, "y": 150, "type": "house"}, # Northeast  
            {"x": 400, "y": 800, "type": "house"},  # Southwest
            {"x": 1400, "y": 600, "type": "house"}, # East
            {"x": 800, "y": 1200, "type": "house"}, # South-central
            {"x": 300, "y": 1500, "type": "house"}, # Deep south
            {"x": 1600, "y": 300, "type": "house"}, # Far northeast
            {"x": 1800, "y": 400, "type": "mansion"}, # Wealthy family mansion
        ]
    
    def assign_house_to_npc(self, npc_name: str) -> bool:
        """Assign a house to an NPC"""
        if npc_name in self.npc_assignments:
            return True  # Already has a house
        
        # Special handling for wealthy family members - they share a mansion
        wealthy_family = ["Steve", "Kailey", "Louie"]
        if npc_name in wealthy_family:
            # Check if any family member already has the mansion
            mansion_assignment = None
            for family_member, assignment in self.npc_assignments.items():
                if family_member in wealthy_family and assignment.house_type == "mansion":
                    mansion_assignment = assignment
                    break
            
            if mansion_assignment:
                # Assign same mansion to this family member
                assignment = NPCHouseAssignment(
                    npc_name=npc_name,
                    house_location=mansion_assignment.house_location,
                    house_type="mansion"
                )
                self.npc_assignments[npc_name] = assignment
                print(f"Assigned {npc_name} to family mansion at {mansion_assignment.house_location}")
                return True
            else:
                # First family member - assign the mansion
                mansion_config = None
                for i, house in enumerate(self.available_houses):
                    if house["type"] == "mansion":
                        mansion_config = self.available_houses.pop(i)
                        break
                
                if mansion_config:
                    assignment = NPCHouseAssignment(
                        npc_name=npc_name,
                        house_location=(mansion_config["x"], mansion_config["y"]),
                        house_type="mansion"
                    )
                    self.npc_assignments[npc_name] = assignment
                    print(f"Assigned mansion at ({mansion_config['x']}, {mansion_config['y']}) to {npc_name}")
                    return True
        
        if not self.available_houses:
            print(f"Warning: No available houses for {npc_name}")
            return False
        
        # Assign the first available house for other NPCs
        house_config = self.available_houses.pop(0)
        
        assignment = NPCHouseAssignment(
            npc_name=npc_name,
            house_location=(house_config["x"], house_config["y"]),
            house_type=house_config["type"]
        )
        
        self.npc_assignments[npc_name] = assignment
        
        # House interior will be created when first needed (lazy loading)
        
        print(f"Assigned house at ({house_config['x']}, {house_config['y']}) to {npc_name}")
        return True
    
    def _create_npc_house_interior(self, npc_name: str) -> HouseInterior:
        """Create a customized house interior for an NPC"""
        house = HouseInterior()
        
        # Customize the house based on NPC personality if available
        # For now, we'll create variations in furniture arrangement
        house.npc_owner = npc_name
        
        # Add some personality-based customization
        self._customize_house_for_npc(house, npc_name)
        
        return house
    
    def _customize_house_for_npc(self, house: HouseInterior, npc_name: str):
        """Add personality-based customization to the house"""
        # Clear existing items and recreate with variation
        house.items.clear()
        
        # Check if this is a wealthy family member
        wealthy_family = ["Steve", "Kailey", "Louie"]
        if npc_name in wealthy_family:
            # Create luxurious mansion interior
            house.items = self._create_mansion_interior()
            return
        
        # Base furniture that every house needs
        base_items = [
            # Bedroom area
            HouseItem(110, 110, "bed", 80, 45),
            HouseItem(210, 110, "dresser", 45, 40),
            
            # Kitchen area
            HouseItem(410, 120, "stove", 50, 40),
            HouseItem(480, 120, "refrigerator", 40, 50),
            HouseItem(410, 180, "sink", 60, 30),
            HouseItem(520, 180, "table", 50, 50),
            
            # Living room area
            HouseItem(120, 320, "couch", 80, 40),
            HouseItem(220, 320, "tv", 60, 30),
            HouseItem(120, 380, "bookshelf", 40, 80),
            
            # Bathroom area
            HouseItem(650, 120, "toilet", 30, 40),
            HouseItem(690, 120, "sink", 40, 30),
            
            # Exit door
            HouseItem(SCREEN_WIDTH // 2 - 25, SCREEN_HEIGHT - 50, "door", 50, 20),
        ]
        
        # Add personality variations
        personality_items = self._get_personality_items(npc_name)
        
        house.items = base_items + personality_items
    
    def _create_mansion_interior(self) -> List[HouseItem]:
        """Create a luxurious mansion interior for the wealthy family"""
        mansion_items = [
            # Grand entrance hall
            HouseItem(SCREEN_WIDTH // 2 - 40, 50, "grand_chandelier", 80, 60),
            HouseItem(SCREEN_WIDTH // 2 - 100, 50, "marble_pillar", 30, 80),
            HouseItem(SCREEN_WIDTH // 2 + 70, 50, "marble_pillar", 30, 80),
            
            # Master bedroom (Steve's room)
            HouseItem(100, 100, "king_bed", 120, 80),
            HouseItem(250, 100, "luxury_dresser", 80, 60),
            HouseItem(350, 100, "walk_in_closet", 60, 80),
            HouseItem(100, 200, "bedside_table", 40, 40),
            HouseItem(280, 200, "vanity_table", 60, 40),
            
            # Kailey's bedroom
            HouseItem(500, 100, "princess_bed", 90, 60),
            HouseItem(600, 100, "toy_chest", 60, 40),
            HouseItem(670, 100, "study_desk", 80, 50),
            HouseItem(500, 180, "dollhouse", 50, 50),
            HouseItem(570, 180, "bookshelf", 40, 80),
            
            # Louie's bedroom
            HouseItem(100, 300, "race_car_bed", 100, 50),
            HouseItem(220, 300, "toy_organizer", 60, 60),
            HouseItem(300, 300, "play_table", 80, 60),
            HouseItem(100, 370, "building_blocks", 40, 40),
            HouseItem(160, 370, "stuffed_animals", 50, 30),
            
            # Gourmet kitchen
            HouseItem(450, 300, "premium_stove", 80, 60),
            HouseItem(550, 300, "double_refrigerator", 80, 80),
            HouseItem(650, 300, "granite_counter", 100, 50),
            HouseItem(450, 380, "dishwasher", 60, 50),
            HouseItem(530, 380, "wine_fridge", 50, 60),
            HouseItem(600, 380, "coffee_machine", 40, 40),
            
            # Formal dining room
            HouseItem(100, 480, "dining_table", 150, 80),
            HouseItem(80, 520, "dining_chair", 40, 40),
            HouseItem(140, 520, "dining_chair", 40, 40),
            HouseItem(200, 520, "dining_chair", 40, 40),
            HouseItem(80, 440, "dining_chair", 40, 40),
            HouseItem(140, 440, "dining_chair", 40, 40),
            HouseItem(200, 440, "dining_chair", 40, 40),
            HouseItem(270, 480, "china_cabinet", 60, 80),
            
            # Luxury living room
            HouseItem(400, 480, "sectional_sofa", 120, 80),
            HouseItem(540, 480, "leather_armchair", 60, 60),
            HouseItem(610, 480, "leather_armchair", 60, 60),
            HouseItem(450, 560, "glass_coffee_table", 80, 50),
            HouseItem(350, 480, "floor_lamp", 30, 30),
            HouseItem(680, 480, "floor_lamp", 30, 30),
            
            # Entertainment center
            HouseItem(750, 300, "home_theater", 100, 80),
            HouseItem(750, 400, "surround_sound", 80, 40),
            HouseItem(750, 450, "gaming_console", 50, 30),
            HouseItem(810, 450, "movie_collection", 60, 40),
            
            # Home office/study
            HouseItem(750, 100, "executive_desk", 100, 60),
            HouseItem(750, 180, "executive_chair", 50, 50),
            HouseItem(870, 100, "filing_cabinet", 40, 60),
            HouseItem(870, 180, "bookcase", 50, 80),
            HouseItem(920, 100, "safe", 40, 50),
            
            # Bathrooms
            HouseItem(650, 150, "jacuzzi_tub", 80, 60),
            HouseItem(750, 150, "double_vanity", 100, 40),
            HouseItem(650, 220, "marble_shower", 60, 60),
            HouseItem(720, 220, "luxury_toilet", 40, 50),
            
            # Additional luxury items
            HouseItem(300, 50, "grand_piano", 120, 80),
            HouseItem(550, 50, "art_gallery_wall", 80, 20),
            HouseItem(50, 50, "suit_of_armor", 40, 60),
            HouseItem(850, 50, "antique_vase", 30, 50),
            
            # Exit door
            HouseItem(SCREEN_WIDTH // 2 - 25, SCREEN_HEIGHT - 50, "mansion_door", 80, 30),
        ]
        
        return mansion_items
    
    def _get_personality_items(self, npc_name: str) -> List[HouseItem]:
        """Get additional items based on NPC personality"""
        # This could be enhanced to use actual personality data
        # For now, add some random variation
        
        personality_variations = [
            # Study-focused NPCs
            [HouseItem(300, 380, "desk", 60, 40), HouseItem(300, 320, "chair", 30, 30)],
            
            # Creative NPCs  
            [HouseItem(280, 320, "easel", 40, 60), HouseItem(250, 400, "art_supplies", 50, 30)],
            
            # Social NPCs
            [HouseItem(450, 320, "dining_table", 80, 60), HouseItem(450, 400, "extra_chairs", 80, 30)],
            
            # Fitness-focused NPCs
            [HouseItem(350, 380, "exercise_bike", 50, 50), HouseItem(300, 450, "weights", 60, 30)],
            
            # Nature-loving NPCs
            [HouseItem(280, 300, "plant_pot", 30, 30), HouseItem(320, 300, "plant_pot", 30, 30)],
        ]
        
        # Return a random personality variation
        return random.choice(personality_variations)
    
    def get_npc_house_location(self, npc_name: str) -> Optional[Tuple[int, int]]:
        """Get the map location of an NPC's house"""
        if npc_name in self.npc_assignments:
            return self.npc_assignments[npc_name].house_location
        return None
    
    def get_npc_house_interior(self, npc_name: str) -> Optional[HouseInterior]:
        """Get the house interior for an NPC (lazy load if needed)"""
        if npc_name in self.npc_assignments and npc_name not in self.house_interiors:
            # Create the house interior on first access
            self.house_interiors[npc_name] = self._create_npc_house_interior(npc_name)
        return self.house_interiors.get(npc_name)
    
    def is_npc_at_home(self, npc_name: str) -> bool:
        """Check if an NPC is currently at their home"""
        if npc_name in self.npc_assignments:
            return self.npc_assignments[npc_name].is_home
        return False
    
    def set_npc_home_status(self, npc_name: str, is_home: bool):
        """Set whether an NPC is currently at home"""
        if npc_name in self.npc_assignments:
            self.npc_assignments[npc_name].is_home = is_home
    
    def npc_use_house_item(self, npc_name: str, item_type: str) -> str:
        """Allow NPC to use items in their house to restore stats"""
        house = self.get_npc_house_interior(npc_name)
        if not house:
            return f"{npc_name} doesn't have a house assigned."
        
        # Find the item in the house
        target_item = None
        for item in house.items:
            if item.item_type == item_type:
                target_item = item
                break
        
        if not target_item:
            return f"No {item_type} found in {npc_name}'s house."
        
        # Get the NPC object to modify stats
        # This will be called from the NPC with self passed as parameter
        return f"{npc_name} used the {item_type}"
    
    def npc_go_home(self, npc) -> bool:
        """Make an NPC go to their house"""
        if npc.name not in self.npc_assignments:
            return False
        
        house_location = self.get_npc_house_location(npc.name)
        if house_location:
            # Set target to house location
            npc.target_pos = pygame.math.Vector2(house_location[0], house_location[1])
            npc.state = "going_home"
            return True
        
        return False
    
    def npc_enter_house(self, npc) -> bool:
        """Make an NPC enter their house"""
        house_location = self.get_npc_house_location(npc.name)
        if not house_location:
            return False
        
        # Check if NPC is close enough to their house
        distance = ((npc.rect.centerx - house_location[0]) ** 2 + 
                   (npc.rect.centery - house_location[1]) ** 2) ** 0.5
        
        if distance <= 80:  # Within interaction range
            self.set_npc_home_status(npc.name, True)
            npc.state = "inside_house"
            return True
        
        return False
    
    def npc_exit_house(self, npc) -> bool:
        """Make an NPC exit their house"""
        if not self.is_npc_at_home(npc.name):
            return False
        
        house_location = self.get_npc_house_location(npc.name)
        if house_location:
            # Position NPC outside their house
            npc.rect.centerx = house_location[0]
            npc.rect.centery = house_location[1] + 80  # Position in front of house
            self.set_npc_home_status(npc.name, False)
            npc.state = "idle"
            return True
        
        return False
    
    def npc_restore_stats_at_home(self, npc, activity: str) -> str:
        """Allow NPC to restore stats using house facilities"""
        if not self.is_npc_at_home(npc.name):
            return f"{npc.name} is not at home."
        
        house = self.get_npc_house_interior(npc.name)
        if not house:
            return f"{npc.name} doesn't have a house."
        
        # Define stat restoration activities
        restoration_activities = {
            "sleep": {
                "item_types": ["bed"],
                "stats": {"sleep": 0.8, "fun": 0.3},
                "message": f"💤 {npc.name} sleeps peacefully in their bed and feels refreshed!"
            },
            "cook": {
                "item_types": ["stove", "refrigerator"],
                "stats": {"hunger": 0.6, "fun": 0.1},
                "message": f"🍳 {npc.name} cooks a delicious meal in their kitchen!"
            },
            "relax": {
                "item_types": ["couch", "tv"],
                "stats": {"fun": 0.4, "sleep": 0.1},
                "message": f"📺 {npc.name} relaxes on their couch and watches TV!"
            },
            "freshen_up": {
                "item_types": ["sink", "toilet"],
                "stats": {"sleep": 0.1, "fun": 0.05, "social": 0.05},
                "message": f"🚿 {npc.name} freshens up in their bathroom!"
            },
            "read": {
                "item_types": ["bookshelf"],
                "stats": {"fun": 0.3, "social": 0.1},
                "message": f"📚 {npc.name} reads a good book and learns something new!"
            }
        }
        
        if activity not in restoration_activities:
            return f"Unknown activity: {activity}"
        
        activity_data = restoration_activities[activity]
        
        # Check if the house has the required items
        has_required_item = False
        for item in house.items:
            if item.item_type in activity_data["item_types"]:
                has_required_item = True
                break
        
        if not has_required_item:
            return f"{npc.name}'s house doesn't have the required furniture for {activity}."
        
        # Restore stats
        if hasattr(npc, 'needs'):
            for stat, amount in activity_data["stats"].items():
                if stat in npc.needs:
                    old_value = npc.needs[stat]
                    npc.needs[stat] = min(1.0, npc.needs[stat] + amount)
                    
                    # Update energy and social battery for enhanced NPCs
                    if hasattr(npc, 'energy_level') and stat == "sleep":
                        npc.energy_level = min(1.0, npc.energy_level + amount)
                    
                    if hasattr(npc, 'social_battery') and stat == "social":
                        npc.social_battery = min(1.0, npc.social_battery + amount * 0.5)
        
        return activity_data["message"]
    
    def get_all_house_assignments(self) -> Dict[str, NPCHouseAssignment]:
        """Get all house assignments"""
        return self.npc_assignments.copy()
    
    def get_available_house_count(self) -> int:
        """Get number of available unassigned houses"""
        return len(self.available_houses)
    
    def is_near_house(self, npc, distance_threshold: int = 80) -> bool:
        """Check if an NPC is near their house"""
        house_location = self.get_npc_house_location(npc.name)
        if not house_location:
            return False
        
        distance = ((npc.rect.centerx - house_location[0]) ** 2 + 
                   (npc.rect.centery - house_location[1]) ** 2) ** 0.5
        
        return distance <= distance_threshold
    
    def get_house_info_for_ui(self) -> List[Dict]:
        """Get house information for UI display"""
        house_info = []
        
        for npc_name, assignment in self.npc_assignments.items():
            house_info.append({
                "npc_name": npc_name,
                "house_location": assignment.house_location,
                "is_home": assignment.is_home,
                "house_type": assignment.house_type
            })
        
        return house_info
    
    def debug_house_assignments(self):
        """Print debug information about house assignments"""
        print("\n=== NPC House Assignments ===")
        for npc_name, assignment in self.npc_assignments.items():
            location = assignment.house_location
            status = "at home" if assignment.is_home else "away"
            print(f"{npc_name}: House at ({location[0]}, {location[1]}) - {status}")
        
        print(f"Available houses remaining: {len(self.available_houses)}")
        
        if self.available_houses:
            print("Unassigned houses:")
            for house in self.available_houses:
                print(f"  - ({house['x']}, {house['y']})")
    
    def save_house_data(self) -> Dict:
        """Save house assignment data for persistence"""
        save_data = {
            "assignments": {},
            "available_houses": self.available_houses.copy()
        }
        
        for npc_name, assignment in self.npc_assignments.items():
            save_data["assignments"][npc_name] = {
                "house_location": assignment.house_location,
                "house_type": assignment.house_type,
                "is_home": assignment.is_home
            }
        
        return save_data
    
    def load_house_data(self, save_data: Dict):
        """Load house assignment data from save"""
        if "assignments" in save_data:
            self.npc_assignments.clear()
            for npc_name, data in save_data["assignments"].items():
                assignment = NPCHouseAssignment(
                    npc_name=npc_name,
                    house_location=tuple(data["house_location"]),
                    house_type=data.get("house_type", "house")
                )
                assignment.is_home = data.get("is_home", False)
                self.npc_assignments[npc_name] = assignment
                
                # Recreate house interior
                self.house_interiors[npc_name] = self._create_npc_house_interior(npc_name)
        
        if "available_houses" in save_data:
            self.available_houses = save_data["available_houses"]