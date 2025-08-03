import json
import os
import datetime
from typing import Dict, List, Any
from src.entities.npc import NPC
from src.world.events import WorldEvent

class SaveSystem:
    def __init__(self, save_file="savegame.json"):
        self.save_file = save_file
    
    def save_game(self, npcs: List[NPC], active_events: List[WorldEvent], 
                  game_time: float = 0, player_data: Dict = None, time_system_data: Dict = None) -> bool:
        try:
            save_data = {
                "version": "1.0",
                "timestamp": datetime.datetime.now().isoformat(),
                "game_time": game_time,
                "time_system": time_system_data,
                "player": player_data,
                "npcs": self._serialize_npcs(npcs),
                "events": self._serialize_events(active_events)
            }
            
            with open(self.save_file, 'w') as f:
                json.dump(save_data, f, indent=2)
            
            print(f"Game saved to {self.save_file}")
            return True
            
        except Exception as e:
            print(f"Failed to save game: {e}")
            return False
    
    def load_game(self) -> Dict[str, Any]:
        try:
            if not os.path.exists(self.save_file):
                return None
            
            with open(self.save_file, 'r') as f:
                save_data = json.load(f)
            
            print(f"Game loaded from {self.save_file}")
            return save_data
            
        except Exception as e:
            print(f"Failed to load game: {e}")
            return None
    
    def _serialize_npcs(self, npcs: List[NPC]) -> List[Dict]:
        serialized_npcs = []
        
        for npc in npcs:
            # Get emotion from emotional_state if available
            emotion = None
            if hasattr(npc, 'emotional_state') and hasattr(npc.emotional_state, 'primary_emotion'):
                emotion = npc.emotional_state.primary_emotion.value
            elif hasattr(npc, 'emotion'):
                emotion = npc.emotion
            else:
                emotion = 'neutral'
            
            npc_data = {
                "name": npc.name,
                "position": {"x": npc.rect.x, "y": npc.rect.y},
                "personality": npc.personality.traits,
                "needs": npc.needs.copy(),
                "relationships": npc.relationships.copy(),
                "emotion": emotion,
                "state": npc.state,
                "memory": npc.memory[-50:] if npc.memory else [],  # Keep last 50 memories
                "target_pos": {
                    "x": npc.target_pos.x if npc.target_pos else None,
                    "y": npc.target_pos.y if npc.target_pos else None
                } if npc.target_pos else None
            }
            serialized_npcs.append(npc_data)
        
        return serialized_npcs
    
    def _serialize_events(self, events: List[WorldEvent]) -> List[Dict]:
        serialized_events = []
        
        for event in events:
            event_data = {
                "type": event.type.value,
                "title": event.title,
                "description": event.description,
                "duration": event.duration,
                "impact": event.impact,
                "location": event.location,
                "participants": event.participants
            }
            serialized_events.append(event_data)
        
        return serialized_events
    
    def restore_npcs(self, npc_data_list: List[Dict], memory_manager) -> List[NPC]:
        restored_npcs = []
        
        for npc_data in npc_data_list:
            npc = NPC(
                x=npc_data["position"]["x"],
                y=npc_data["position"]["y"],
                name=npc_data["name"],
                personality_traits=npc_data["personality"],
                memory_manager=memory_manager
            )
            
            npc.needs = npc_data["needs"]
            npc.relationships = npc_data["relationships"]
            # Set emotion properly based on NPC type
            if hasattr(npc, 'emotional_state') and hasattr(npc.emotional_state, 'primary_emotion'):
                # For EnhancedNPC, we would need to reconstruct the emotional state
                # For now, just use the default emotional state
                pass
            elif hasattr(npc, 'emotion'):
                npc.emotion = npc_data["emotion"]
            npc.state = npc_data["state"]
            npc.memory = npc_data["memory"]
            
            if npc_data["target_pos"] and npc_data["target_pos"]["x"] is not None:
                import pygame
                npc.target_pos = pygame.math.Vector2(
                    npc_data["target_pos"]["x"],
                    npc_data["target_pos"]["y"]
                )
            
            restored_npcs.append(npc)
        
        return restored_npcs
    
    def restore_events(self, event_data_list: List[Dict]) -> List[WorldEvent]:
        restored_events = []
        
        for event_data in event_data_list:
            from src.world.events import EventType, WorldEvent
            
            event = WorldEvent(
                type=EventType(event_data["type"]),
                title=event_data["title"],
                description=event_data["description"],
                duration=event_data["duration"],
                impact=event_data["impact"],
                location=tuple(event_data["location"]) if event_data["location"] else None,
                participants=event_data["participants"]
            )
            
            restored_events.append(event)
        
        return restored_events
    
    def save_exists(self) -> bool:
        return os.path.exists(self.save_file)
    
    def get_save_info(self) -> Dict[str, Any]:
        if not self.save_exists():
            return None
        
        try:
            with open(self.save_file, 'r') as f:
                save_data = json.load(f)
            
            return {
                "timestamp": save_data.get("timestamp"),
                "game_time": save_data.get("game_time", 0),
                "npc_count": len(save_data.get("npcs", [])),
                "event_count": len(save_data.get("events", []))
            }
        except:
            return None