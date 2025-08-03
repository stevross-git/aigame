#!/usr/bin/env python3
"""
Simple test script for the NPC house assignment system
"""

from src.world.npc_house_manager import NPCHouseManager

def test_house_manager():
    print("Testing NPC House Manager")
    print("=" * 40)
    
    # Create house manager
    house_manager = NPCHouseManager()
    
    # Test house assignments
    npc_names = ["Alice", "Bob", "Charlie", "Diana", "Emma", "Frank", "Grace"]
    
    print(f"Available houses: {house_manager.get_available_house_count()}")
    
    for name in npc_names:
        success = house_manager.assign_house_to_npc(name)
        print(f"House assignment for {name}: {'SUCCESS' if success else 'FAILED'}")
    
    print("\n" + "=" * 40)
    house_manager.debug_house_assignments()
    
    print(f"\nRemaining available houses: {house_manager.get_available_house_count()}")
    
    # Test house location queries
    print("\n" + "=" * 40)
    print("Testing house location queries...")
    
    for name in npc_names[:4]:  # First 4 should have houses
        location = house_manager.get_npc_house_location(name)
        if location:
            print(f"{name}'s house is at: {location}")
        else:
            print(f"{name} has no house assigned")
    
    # Test house info for UI
    print("\n" + "=" * 40)
    print("House info for UI:")
    house_info = house_manager.get_house_info_for_ui()
    for info in house_info:
        print(f"  {info['npc_name']}: {info['house_location']} ({'HOME' if info['is_home'] else 'AWAY'})")
    
    print("\n" + "=" * 40)
    print("House manager test completed successfully!")

if __name__ == "__main__":
    test_house_manager()