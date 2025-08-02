import random
from typing import List, Dict, Optional
from dataclasses import dataclass
from enum import Enum

class EventType(Enum):
    WEATHER = "weather"
    SOCIAL = "social"
    ECONOMIC = "economic"
    HEALTH = "health"
    ENTERTAINMENT = "entertainment"
    EMERGENCY = "emergency"

@dataclass
class WorldEvent:
    type: EventType
    title: str
    description: str
    duration: float
    impact: Dict[str, float]
    location: Optional[tuple] = None
    participants: List[str] = None
    
    def __post_init__(self):
        if self.participants is None:
            self.participants = []

class EventGenerator:
    def __init__(self):
        self.active_events = []
        self.event_cooldown = 0
        self.event_templates = self._create_event_templates()
    
    def _create_event_templates(self) -> List[Dict]:
        return [
            {
                "type": EventType.WEATHER,
                "templates": [
                    {
                        "title": "Sunny Day",
                        "description": "Perfect weather for outdoor activities",
                        "duration": 300,
                        "impact": {"fun": 0.2, "energy": 0.1},
                        "weight": 0.3
                    },
                    {
                        "title": "Rainy Weather",
                        "description": "It's raining, better stay indoors",
                        "duration": 200,
                        "impact": {"fun": -0.1, "energy": -0.05},
                        "weight": 0.2
                    },
                    {
                        "title": "Storm Warning",
                        "description": "A storm is approaching, seek shelter!",
                        "duration": 150,
                        "impact": {"fun": -0.2, "social": -0.1},
                        "weight": 0.1
                    }
                ]
            },
            {
                "type": EventType.SOCIAL,
                "templates": [
                    {
                        "title": "Community Gathering",
                        "description": "Everyone is invited to the town square",
                        "duration": 180,
                        "impact": {"social": 0.3, "fun": 0.2},
                        "location": (500, 350),
                        "weight": 0.15
                    },
                    {
                        "title": "Birthday Party",
                        "description": "Someone is celebrating their birthday!",
                        "duration": 120,
                        "impact": {"social": 0.4, "fun": 0.3, "hunger": -0.2},
                        "weight": 0.1
                    }
                ]
            },
            {
                "type": EventType.ECONOMIC,
                "templates": [
                    {
                        "title": "Job Fair",
                        "description": "New job opportunities available",
                        "duration": 240,
                        "impact": {"ambition": 0.2},
                        "location": (500, 200),
                        "weight": 0.1
                    },
                    {
                        "title": "Market Sale",
                        "description": "Special discounts at the local shops",
                        "duration": 180,
                        "impact": {"fun": 0.1},
                        "weight": 0.15
                    }
                ]
            },
            {
                "type": EventType.HEALTH,
                "templates": [
                    {
                        "title": "Health Awareness Day",
                        "description": "Free health checkups available",
                        "duration": 200,
                        "impact": {"sleep": 0.1, "energy": 0.1},
                        "weight": 0.08
                    }
                ]
            },
            {
                "type": EventType.ENTERTAINMENT,
                "templates": [
                    {
                        "title": "Street Performance",
                        "description": "A talented performer is entertaining the crowd",
                        "duration": 90,
                        "impact": {"fun": 0.3, "creativity": 0.1},
                        "location": (400, 400),
                        "weight": 0.12
                    },
                    {
                        "title": "Movie Night",
                        "description": "Outdoor movie screening in the park",
                        "duration": 150,
                        "impact": {"fun": 0.4, "social": 0.2},
                        "location": (700, 500),
                        "weight": 0.1
                    }
                ]
            }
        ]
    
    def update(self, dt):
        self.event_cooldown -= dt
        
        for event in self.active_events[:]:
            event.duration -= dt
            if event.duration <= 0:
                self.active_events.remove(event)
        
        if self.event_cooldown <= 0 and len(self.active_events) < 3:
            if random.random() < 0.3:
                self._generate_random_event()
                self.event_cooldown = random.uniform(30, 60)
    
    def _generate_random_event(self):
        event_type = random.choice(list(EventType))
        
        templates = []
        weights = []
        for category in self.event_templates:
            if category["type"] == event_type:
                for template in category["templates"]:
                    templates.append(template)
                    weights.append(template["weight"])
        
        if templates:
            chosen = random.choices(templates, weights=weights)[0]
            
            event = WorldEvent(
                type=event_type,
                title=chosen["title"],
                description=chosen["description"],
                duration=chosen["duration"],
                impact=chosen.get("impact", {}),
                location=chosen.get("location")
            )
            
            self.active_events.append(event)
            return event
        
        return None
    
    def get_active_events(self) -> List[WorldEvent]:
        return self.active_events.copy()
    
    def get_event_at_location(self, x, y, radius=100) -> Optional[WorldEvent]:
        for event in self.active_events:
            if event.location:
                dist = ((event.location[0] - x) ** 2 + (event.location[1] - y) ** 2) ** 0.5
                if dist <= radius:
                    return event
        return None
    
    def add_participant(self, event: WorldEvent, npc_name: str):
        if npc_name not in event.participants:
            event.participants.append(npc_name)