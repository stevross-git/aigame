import math
from typing import Set, Tuple, Dict
from src.systems.xp_system import XPCategory

class ExplorationTracker:
    """
    Tracks player exploration and grants XP for discovering new areas
    """
    
    def __init__(self, xp_system=None):
        self.xp_system = xp_system
        
        # Grid-based exploration tracking
        self.grid_size = 200  # Each grid cell is 200x200 pixels
        self.discovered_areas: Set[Tuple[int, int]] = set()
        
        # Special locations that give bonus XP
        self.special_locations = {
            (0, 0): {"name": "Spawn Area", "xp": 0},  # Already discovered
            (5, 3): {"name": "Eastern Hills", "xp": 100},
            (2, 8): {"name": "Southern Valley", "xp": 150},
            (8, 2): {"name": "Northern Woods", "xp": 120},
            (1, 1): {"name": "Berry Grove", "xp": 80},
            (7, 7): {"name": "Mining District", "xp": 200},
            (9, 9): {"name": "Remote Wilderness", "xp": 300},
        }
        
        # Start with spawn area discovered
        self.discovered_areas.add((0, 0))
        
        # Discovery stats
        self.total_discoveries = 0
        self.total_exploration_xp = 0
        
        # Recent discoveries for UI display
        self.recent_discoveries = []
    
    def update_player_position(self, x: int, y: int):
        """Update player position and check for new area discovery"""
        # Convert world coordinates to grid coordinates
        grid_x = x // self.grid_size
        grid_y = y // self.grid_size
        
        grid_pos = (grid_x, grid_y)
        
        # Check if this is a new area
        if grid_pos not in self.discovered_areas:
            self.discovered_areas.add(grid_pos)
            self._discover_area(grid_pos, x, y)
    
    def _discover_area(self, grid_pos: Tuple[int, int], world_x: int, world_y: int):
        """Handle discovering a new area"""
        self.total_discoveries += 1
        
        # Base XP for discovering any new area
        base_xp = 25
        
        # Check if this is a special location
        if grid_pos in self.special_locations:
            location_info = self.special_locations[grid_pos]
            location_name = location_info["name"]
            bonus_xp = location_info["xp"]
            total_xp = base_xp + bonus_xp
            
            discovery_message = f"Discovered {location_name}!"
        else:
            # Generate a generic area name
            location_name = self._generate_area_name(grid_pos)
            total_xp = base_xp
            discovery_message = f"Explored new area: {location_name}"
        
        # Grant XP
        if self.xp_system:
            self.xp_system.add_xp(total_xp, XPCategory.EXPLORATION, discovery_message)
        
        self.total_exploration_xp += total_xp
        
        # Add to recent discoveries
        discovery_info = {
            'name': location_name,
            'grid_pos': grid_pos,
            'world_pos': (world_x, world_y),
            'xp': total_xp,
            'is_special': grid_pos in self.special_locations
        }
        
        self.recent_discoveries.append(discovery_info)
        
        # Keep only last 10 discoveries
        if len(self.recent_discoveries) > 10:
            self.recent_discoveries.pop(0)
    
    def _generate_area_name(self, grid_pos: Tuple[int, int]) -> str:
        """Generate a descriptive name for a grid area"""
        x, y = grid_pos
        
        # Simple naming based on position
        direction_x = "Western" if x < 3 else "Central" if x < 7 else "Eastern"
        direction_y = "Northern" if y < 3 else "Central" if y < 7 else "Southern"
        
        terrain_types = [
            "Plains", "Fields", "Meadows", "Hills", "Forest", 
            "Grove", "Valley", "Ridge", "Clearing", "Woods"
        ]
        
        # Use position to deterministically pick terrain
        terrain_index = (x + y) % len(terrain_types)
        terrain = terrain_types[terrain_index]
        
        if direction_x == "Central" and direction_y == "Central":
            return f"{terrain}"
        elif direction_x == "Central":
            return f"{direction_y} {terrain}"
        elif direction_y == "Central":
            return f"{direction_x} {terrain}"
        else:
            return f"{direction_x} {terrain}"
    
    def get_exploration_stats(self) -> Dict:
        """Get exploration statistics"""
        total_areas = 100  # 10x10 grid assumption
        discovery_percentage = (len(self.discovered_areas) / total_areas) * 100
        
        return {
            'discovered_areas': len(self.discovered_areas),
            'total_areas': total_areas,
            'discovery_percentage': discovery_percentage,
            'total_discoveries': self.total_discoveries,
            'total_exploration_xp': self.total_exploration_xp,
            'recent_discoveries': self.recent_discoveries[-5:],  # Last 5
            'special_locations_found': sum(1 for pos in self.discovered_areas if pos in self.special_locations)
        }
    
    def get_nearby_special_locations(self, x: int, y: int, radius: int = 3) -> list:
        """Get special locations near the player"""
        grid_x = x // self.grid_size
        grid_y = y // self.grid_size
        
        nearby = []
        for (sx, sy), info in self.special_locations.items():
            distance = math.sqrt((grid_x - sx) ** 2 + (grid_y - sy) ** 2)
            if distance <= radius:
                is_discovered = (sx, sy) in self.discovered_areas
                nearby.append({
                    'name': info['name'],
                    'grid_pos': (sx, sy),
                    'world_pos': (sx * self.grid_size + self.grid_size // 2, 
                                 sy * self.grid_size + self.grid_size // 2),
                    'distance': distance,
                    'discovered': is_discovered,
                    'xp_reward': info['xp']
                })
        
        return sorted(nearby, key=lambda x: x['distance'])
    
    def save_data(self) -> Dict:
        """Save exploration data"""
        return {
            'discovered_areas': list(self.discovered_areas),
            'total_discoveries': self.total_discoveries,
            'total_exploration_xp': self.total_exploration_xp,
            'recent_discoveries': self.recent_discoveries
        }
    
    def load_data(self, data: Dict):
        """Load exploration data"""
        self.discovered_areas = set(tuple(pos) for pos in data.get('discovered_areas', [(0, 0)]))
        self.total_discoveries = data.get('total_discoveries', 0)
        self.total_exploration_xp = data.get('total_exploration_xp', 0)
        self.recent_discoveries = data.get('recent_discoveries', [])