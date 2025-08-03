#!/usr/bin/env python3
"""
Test script for the NPC house assignment system
"""

import pygame

from src.world.npc_house_manager import NPCHouseManager
from src.entities.enhanced_npc import EnhancedNPC

def test_house_system():
    # Initialize pygame for asset loading
    pygame.init()
    pygame.display.set_mode((800, 600))
    print("Testing NPC House Assignment System")
    print("=" * 50)
    
    # Create house manager
    house_manager = NPCHouseManager()
    
    # Create test NPCs
    npc_names = ["Alice", "Bob", "Charlie", "Diana"]
    npcs = []
    
    for i, name in enumerate(npc_names):
        # Create Enhanced NPC with test personality
        personality = {
            "friendliness": 0.8,
            "confidence": 0.6,
            "empathy": 0.7,
            "creativity": 0.5
        }
        
        npc = EnhancedNPC(100 + i * 50, 100 + i * 50, name, personality, None)
        npc.house_manager = house_manager
        npcs.append(npc)
        
        # Assign house
        success = house_manager.assign_house_to_npc(name)
        print(f"House assignment for {name}: {'SUCCESS' if success else 'FAILED'}")
    
    print("\n" + "=" * 50)
    house_manager.debug_house_assignments()
    
    print("\n" + "=" * 50)
    print("Testing stat restoration...")
    
    # Test Alice using her house
    alice = npcs[0]
    alice.needs["hunger"] = 0.2  # Make Alice hungry
    alice.needs["sleep"] = 0.3   # Make Alice tired
    
    print(f"Alice's needs before: {alice.needs}")
    
    # Make Alice go home
    house_manager.set_npc_home_status("Alice", True)
    
    # Test restoration activities
    result1 = house_manager.npc_restore_stats_at_home(alice, "cook")
    print(f"Cooking result: {result1}")
    
    result2 = house_manager.npc_restore_stats_at_home(alice, "sleep")
    print(f"Sleeping result: {result2}")
    
    print(f"Alice's needs after: {alice.needs}")
    
    print("\n" + "=" * 50)
    print("House system test completed successfully!")

if __name__ == "__main__":
    test_house_system()