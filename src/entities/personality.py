from dataclasses import dataclass
from typing import Dict
import random

@dataclass
class Personality:
    traits: Dict[str, float]
    
    def __init__(self, **kwargs):
        default_traits = {
            "friendliness": 0.5,
            "energy": 0.5,
            "creativity": 0.5,
            "organization": 0.5,
            "confidence": 0.5,
            "empathy": 0.5,
            "humor": 0.5,
            "curiosity": 0.5,
            "patience": 0.5,
            "ambition": 0.5
        }
        
        self.traits = default_traits.copy()
        for key, value in kwargs.items():
            if key in self.traits:
                self.traits[key] = max(0, min(1, value))
    
    def get_trait(self, trait_name: str) -> float:
        return self.traits.get(trait_name, 0.5)
    
    def to_prompt_string(self) -> str:
        descriptions = []
        for trait, value in self.traits.items():
            if value > 0.7:
                descriptions.append(f"very {trait}")
            elif value > 0.5:
                descriptions.append(f"quite {trait}")
            elif value < 0.3:
                descriptions.append(f"not very {trait}")
        
        return ", ".join(descriptions) if descriptions else "balanced personality"
    
    @staticmethod
    def generate_random():
        traits = {}
        trait_names = ["friendliness", "energy", "creativity", "organization", 
                      "confidence", "empathy", "humor", "curiosity", "patience", "ambition"]
        
        for trait in trait_names:
            traits[trait] = random.triangular(0.2, 0.8, 0.5)
        
        return Personality(**traits)