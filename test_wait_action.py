#!/usr/bin/env python3
"""Test script for wait action functionality"""

import pygame
import sys
import os

# Add the game source to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.entities.enhanced_player import EnhancedPlayer
from src.entities.enhanced_npc import EnhancedNPC

def test_player_wait():
    """Test player wait action"""
    print("Testing Player Wait Action...")
    
    # Initialize pygame
    pygame.init()
    pygame.display.set_mode((800, 600))  # Need a display for asset loading
    
    # Create a player
    player = EnhancedPlayer(100, 100)
    
    # Test starting wait
    player.start_wait(5.0, "Testing wait action")
    assert player.is_waiting == True
    assert player.wait_duration == 5.0
    assert player.wait_timer == 5.0
    assert player.wait_message == "Testing wait action"
    print("✅ Player wait started successfully")
    
    # Simulate time passing
    player.wait_timer = 1.0
    progress = player.get_wait_progress()
    assert progress == 0.8  # (5-1)/5 = 0.8
    print(f"✅ Wait progress calculation correct: {progress:.1%}")
    
    # Test stopping wait
    player.stop_wait()
    assert player.is_waiting == False
    assert player.wait_timer == 0.0
    print("✅ Player wait stopped successfully")
    
    pygame.quit()
    return True

def test_npc_wait():
    """Test NPC wait action"""
    print("\nTesting NPC Wait Action...")
    
    # Initialize pygame
    pygame.init()
    pygame.display.set_mode((800, 600))  # Need a display for asset loading
    
    # Create an NPC
    npc = EnhancedNPC(200, 200, "TestNPC", skip_ai_init=True)
    
    # Test starting wait
    npc.start_wait(8.0, "NPC is waiting patiently")
    assert npc.is_waiting == True
    assert npc.wait_duration == 8.0
    assert npc.wait_timer == 8.0
    assert npc.wait_reason == "NPC is waiting patiently"
    assert npc.state == "waiting"
    print("✅ NPC wait started successfully")
    
    # Test wait progress
    npc.wait_timer = 2.0
    progress = npc.get_wait_progress()
    assert progress == 0.75  # (8-2)/8 = 0.75
    print(f"✅ NPC wait progress calculation correct: {progress:.1%}")
    
    # Test automatic stop when timer expires
    npc.wait_timer = 0.01
    npc.update(0.02, [], None)  # Should trigger stop_wait
    assert npc.is_waiting == False
    assert npc.state == "idle"
    print("✅ NPC wait auto-stopped when timer expired")
    
    pygame.quit()
    return True

def test_wait_integration():
    """Test wait action integration with game systems"""
    print("\nTesting Wait Action Integration...")
    
    # Initialize pygame
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    clock = pygame.time.Clock()
    
    # Create player and NPC
    player = EnhancedPlayer(400, 300)
    npc = EnhancedNPC(450, 300, "TestNPC", skip_ai_init=True)
    
    # Test player wait with spacebar
    keys = {pygame.K_SPACE: True}
    for _ in range(len(keys)):
        keys[pygame.K_SPACE] = False  # Simulate key release
    
    # Simulate a few frames
    for i in range(3):
        dt = clock.tick(60) / 1000.0
        
        # First frame: press space
        if i == 0:
            test_keys = pygame.key.get_pressed()
            test_keys_dict = {pygame.K_SPACE: True}
            player._handle_input(test_keys_dict, dt)
            if player.is_waiting:
                print("✅ Player responds to spacebar for wait action")
        
        player.update(dt, pygame.key.get_pressed())
        npc.update(dt, [player], None)
    
    # Test that waiting NPCs don't move
    npc.start_wait(5.0, "Standing still")
    old_pos = (npc.rect.x, npc.rect.y)
    npc.target_pos = (500, 400)  # Try to set a target
    npc.update(0.1, [], None)
    new_pos = (npc.rect.x, npc.rect.y)
    assert old_pos == new_pos, "NPC should not move while waiting"
    print("✅ Waiting NPCs don't move")
    
    pygame.quit()
    return True

if __name__ == "__main__":
    print("=" * 50)
    print("WAIT ACTION TEST SUITE")
    print("=" * 50)
    
    try:
        # Run all tests
        test_player_wait()
        test_npc_wait()
        test_wait_integration()
        
        print("\n" + "=" * 50)
        print("✅ ALL TESTS PASSED!")
        print("=" * 50)
        
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)