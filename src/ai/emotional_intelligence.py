import random
import math
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

class EmotionType(Enum):
    JOY = "joy"
    SADNESS = "sadness"
    ANGER = "anger"
    FEAR = "fear"
    SURPRISE = "surprise"
    DISGUST = "disgust"
    TRUST = "trust"
    ANTICIPATION = "anticipation"
    LOVE = "love"
    GUILT = "guilt"
    PRIDE = "pride"
    SHAME = "shame"
    ENVY = "envy"
    GRATITUDE = "gratitude"
    HOPE = "hope"
    DESPAIR = "despair"
    RELIEF = "relief"
    DISAPPOINTMENT = "disappointment"

@dataclass
class EmotionalState:
    """Represents an NPC's current emotional state"""
    primary_emotion: EmotionType
    intensity: float  # 0.0 to 1.0
    secondary_emotions: Dict[EmotionType, float]
    duration: float  # How long this state has been active
    triggers: List[str]  # What caused this emotional state
    
@dataclass
class EmotionalMemory:
    """Emotional memory of an event"""
    event_description: str
    emotions_felt: Dict[EmotionType, float]
    people_involved: List[str]
    location: Tuple[int, int]
    importance: float
    timestamp: str

class EmotionalIntelligence:
    """
    Advanced emotional intelligence system for NPCs that handles:
    - Complex emotional states and transitions
    - Emotional memory and learning
    - Empathy and social awareness
    - Mood-dependent behavior modifications
    - Emotional contagion between NPCs
    """
    
    def __init__(self):
        self.emotion_transitions = self._initialize_emotion_transitions()
        self.personality_emotion_map = self._initialize_personality_emotions()
        self.empathy_responses = self._initialize_empathy_responses()
        self.emotional_memories = {}  # npc_name -> List[EmotionalMemory]
        self.mood_modifiers = self._initialize_mood_modifiers()
        
    def _initialize_emotion_transitions(self) -> Dict[EmotionType, Dict[EmotionType, float]]:
        """Initialize natural emotion transition probabilities"""
        return {
            EmotionType.JOY: {
                EmotionType.GRATITUDE: 0.3,
                EmotionType.LOVE: 0.2,
                EmotionType.PRIDE: 0.2,
                EmotionType.ANTICIPATION: 0.15,
                EmotionType.TRUST: 0.15
            },
            EmotionType.SADNESS: {
                EmotionType.DESPAIR: 0.2,
                EmotionType.GUILT: 0.15,
                EmotionType.HOPE: 0.25,  # Sadness can lead to hope
                EmotionType.ENVY: 0.15,
                EmotionType.ANGER: 0.25  # Sadness can turn to anger
            },
            EmotionType.ANGER: {
                EmotionType.DISGUST: 0.2,
                EmotionType.SADNESS: 0.2,
                EmotionType.GUILT: 0.15,
                EmotionType.PRIDE: 0.15,  # Righteous anger
                EmotionType.FEAR: 0.3
            },
            EmotionType.FEAR: {
                EmotionType.SURPRISE: 0.2,
                EmotionType.ANGER: 0.25,  # Fight response
                EmotionType.SADNESS: 0.2,
                EmotionType.RELIEF: 0.35  # When fear subsides
            },
            EmotionType.TRUST: {
                EmotionType.LOVE: 0.3,
                EmotionType.JOY: 0.25,
                EmotionType.GRATITUDE: 0.25,
                EmotionType.ANTICIPATION: 0.2
            },
            EmotionType.ANTICIPATION: {
                EmotionType.JOY: 0.3,  # When anticipation is fulfilled
                EmotionType.DISAPPOINTMENT: 0.25,  # When it's not
                EmotionType.SURPRISE: 0.2,
                EmotionType.FEAR: 0.25  # Anxious anticipation
            }
        }
    
    def _initialize_personality_emotions(self) -> Dict[str, Dict[EmotionType, float]]:
        """Map personality traits to emotional tendencies"""
        return {
            "high_friendliness": {
                EmotionType.JOY: 0.3,
                EmotionType.LOVE: 0.25,
                EmotionType.TRUST: 0.25,
                EmotionType.GRATITUDE: 0.2
            },
            "low_friendliness": {
                EmotionType.ANGER: 0.25,
                EmotionType.DISGUST: 0.2,
                EmotionType.FEAR: 0.2,
                EmotionType.SADNESS: 0.35
            },
            "high_confidence": {
                EmotionType.PRIDE: 0.3,
                EmotionType.JOY: 0.25,
                EmotionType.ANTICIPATION: 0.25,
                EmotionType.TRUST: 0.2
            },
            "low_confidence": {
                EmotionType.FEAR: 0.3,
                EmotionType.SHAME: 0.25,
                EmotionType.SADNESS: 0.25,
                EmotionType.GUILT: 0.2
            },
            "high_openness": {
                EmotionType.SURPRISE: 0.3,
                EmotionType.JOY: 0.25,
                EmotionType.ANTICIPATION: 0.25,
                EmotionType.TRUST: 0.2
            },
            "low_openness": {
                EmotionType.FEAR: 0.3,
                EmotionType.DISGUST: 0.25,
                EmotionType.ANGER: 0.25,
                EmotionType.SADNESS: 0.2
            }
        }
    
    def _initialize_empathy_responses(self) -> Dict[EmotionType, Dict[EmotionType, float]]:
        """Initialize empathetic responses to others' emotions"""
        return {
            EmotionType.JOY: {
                EmotionType.JOY: 0.7,  # Joy is contagious
                EmotionType.GRATITUDE: 0.2,
                EmotionType.LOVE: 0.1
            },
            EmotionType.SADNESS: {
                EmotionType.SADNESS: 0.4,  # Emotional contagion
                EmotionType.GUILT: 0.2,
                EmotionType.LOVE: 0.2,  # Compassionate response
                EmotionType.HOPE: 0.2   # Wanting to help
            },
            EmotionType.ANGER: {
                EmotionType.FEAR: 0.4,  # Fear of angry person
                EmotionType.ANGER: 0.3, # Anger can be contagious
                EmotionType.SADNESS: 0.2,
                EmotionType.DISGUST: 0.1
            },
            EmotionType.FEAR: {
                EmotionType.FEAR: 0.5,  # Fear spreads quickly
                EmotionType.LOVE: 0.2,  # Protective instinct
                EmotionType.GUILT: 0.2,
                EmotionType.HOPE: 0.1
            }
        }
    
    def _initialize_mood_modifiers(self) -> Dict[EmotionType, Dict[str, float]]:
        """Initialize how emotions modify behavior tendencies"""
        return {
            EmotionType.JOY: {
                "social_interaction": 1.5,
                "helping_behavior": 1.3,
                "risk_taking": 1.2,
                "creativity": 1.4,
                "patience": 1.2
            },
            EmotionType.SADNESS: {
                "social_interaction": 0.6,
                "helping_behavior": 0.8,
                "risk_taking": 0.5,
                "introspection": 1.5,
                "patience": 0.8
            },
            EmotionType.ANGER: {
                "social_interaction": 0.7,
                "helping_behavior": 0.5,
                "risk_taking": 1.5,
                "aggression": 2.0,
                "patience": 0.3
            },
            EmotionType.FEAR: {
                "social_interaction": 0.4,
                "helping_behavior": 0.6,
                "risk_taking": 0.2,
                "caution": 2.0,
                "patience": 0.6
            },
            EmotionType.TRUST: {
                "social_interaction": 1.4,
                "helping_behavior": 1.5,
                "risk_taking": 1.1,
                "cooperation": 1.6,
                "patience": 1.3
            },
            EmotionType.LOVE: {
                "social_interaction": 1.6,
                "helping_behavior": 1.8,
                "risk_taking": 0.8,
                "protection": 1.7,
                "patience": 1.5
            }
        }
    
    def update_emotional_state(self, npc_name: str, current_state: EmotionalState, 
                             events: List[str], social_context: Dict, 
                             personality: Dict, dt: float) -> EmotionalState:
        """Update NPC's emotional state based on events and context"""
        
        # Process new events that might trigger emotions
        new_emotions = self._process_emotional_triggers(events, social_context, personality)
        
        # Apply emotional contagion from nearby NPCs
        contagion_emotions = self._apply_emotional_contagion(social_context, personality)
        
        # Combine all emotional influences
        combined_emotions = self._combine_emotional_influences(
            current_state, new_emotions, contagion_emotions
        )
        
        # Apply natural emotional decay and transitions
        evolved_emotions = self._evolve_emotions(combined_emotions, dt, personality)
        
        # Determine new primary emotion
        primary_emotion = self._determine_primary_emotion(evolved_emotions)
        
        # Calculate intensity based on multiple factors
        intensity = self._calculate_emotional_intensity(evolved_emotions, primary_emotion, events)
        
        # Update duration
        new_duration = current_state.duration + dt if current_state.primary_emotion == primary_emotion else 0.0
        
        # Update triggers
        new_triggers = self._update_emotional_triggers(current_state.triggers, events)
        
        return EmotionalState(
            primary_emotion=primary_emotion,
            intensity=intensity,
            secondary_emotions=evolved_emotions,
            duration=new_duration,
            triggers=new_triggers
        )
    
    def _process_emotional_triggers(self, events: List[str], social_context: Dict, personality: Dict) -> Dict[EmotionType, float]:
        """Process events to generate emotional responses"""
        emotions = {}
        
        for event in events:
            # Map events to emotions based on content
            if "success" in event.lower() or "achievement" in event.lower():
                emotions[EmotionType.JOY] = emotions.get(EmotionType.JOY, 0) + 0.6
                emotions[EmotionType.PRIDE] = emotions.get(EmotionType.PRIDE, 0) + 0.4
            
            elif "failure" in event.lower() or "mistake" in event.lower():
                emotions[EmotionType.SADNESS] = emotions.get(EmotionType.SADNESS, 0) + 0.5
                emotions[EmotionType.GUILT] = emotions.get(EmotionType.GUILT, 0) + 0.3
            
            elif "gift" in event.lower() or "help" in event.lower():
                emotions[EmotionType.GRATITUDE] = emotions.get(EmotionType.GRATITUDE, 0) + 0.7
                emotions[EmotionType.JOY] = emotions.get(EmotionType.JOY, 0) + 0.4
            
            elif "conflict" in event.lower() or "argument" in event.lower():
                emotions[EmotionType.ANGER] = emotions.get(EmotionType.ANGER, 0) + 0.6
                emotions[EmotionType.SADNESS] = emotions.get(EmotionType.SADNESS, 0) + 0.3
            
            elif "surprise" in event.lower() or "unexpected" in event.lower():
                emotions[EmotionType.SURPRISE] = emotions.get(EmotionType.SURPRISE, 0) + 0.8
            
            elif "threat" in event.lower() or "danger" in event.lower():
                emotions[EmotionType.FEAR] = emotions.get(EmotionType.FEAR, 0) + 0.7
        
        # Apply personality modifiers
        for emotion, intensity in emotions.items():
            if personality.get("emotional_stability", 0.5) < 0.3:
                emotions[emotion] = intensity * 1.5  # More emotional
            elif personality.get("emotional_stability", 0.5) > 0.7:
                emotions[emotion] = intensity * 0.7  # Less emotional
        
        return emotions
    
    def _apply_emotional_contagion(self, social_context: Dict, personality: Dict) -> Dict[EmotionType, float]:
        """Apply emotional contagion from nearby NPCs"""
        contagion_emotions = {}
        
        # Check empathy level
        empathy_level = personality.get("empathy", 0.5)
        
        nearby_emotions = social_context.get("nearby_emotions", {})
        for npc_name, emotion_data in nearby_emotions.items():
            if "emotion" in emotion_data and "intensity" in emotion_data:
                other_emotion = EmotionType(emotion_data["emotion"])
                other_intensity = emotion_data["intensity"]
                
                # Check relationship strength
                relationship_strength = social_context.get("relationships", {}).get(npc_name, 0.5)
                
                # Calculate contagion strength
                contagion_strength = empathy_level * relationship_strength * other_intensity * 0.3
                
                # Apply empathetic response
                if other_emotion in self.empathy_responses:
                    for response_emotion, response_strength in self.empathy_responses[other_emotion].items():
                        contagion_intensity = contagion_strength * response_strength
                        contagion_emotions[response_emotion] = contagion_emotions.get(response_emotion, 0) + contagion_intensity
        
        return contagion_emotions
    
    def _combine_emotional_influences(self, current_state: EmotionalState, 
                                    new_emotions: Dict[EmotionType, float],
                                    contagion_emotions: Dict[EmotionType, float]) -> Dict[EmotionType, float]:
        """Combine all emotional influences into a unified emotional state"""
        
        combined = current_state.secondary_emotions.copy()
        
        # Add current primary emotion
        combined[current_state.primary_emotion] = current_state.intensity
        
        # Add new emotions
        for emotion, intensity in new_emotions.items():
            combined[emotion] = combined.get(emotion, 0) + intensity
        
        # Add contagion emotions
        for emotion, intensity in contagion_emotions.items():
            combined[emotion] = combined.get(emotion, 0) + intensity
        
        # Normalize to prevent emotions from growing too strong
        for emotion in combined:
            combined[emotion] = min(1.0, combined[emotion])
        
        return combined
    
    def _evolve_emotions(self, emotions: Dict[EmotionType, float], dt: float, personality: Dict) -> Dict[EmotionType, float]:
        """Apply natural emotional decay and transitions"""
        
        evolved = {}
        decay_rate = 0.1 * dt  # Base decay rate
        
        # Apply personality-based decay rate modifiers
        if personality.get("emotional_stability", 0.5) > 0.7:
            decay_rate *= 1.5  # Emotions fade faster for stable personalities
        elif personality.get("emotional_stability", 0.5) < 0.3:
            decay_rate *= 0.5  # Emotions linger for unstable personalities
        
        for emotion, intensity in emotions.items():
            # Apply decay
            new_intensity = max(0, intensity - decay_rate)
            
            # Apply natural transitions
            if new_intensity > 0.1 and emotion in self.emotion_transitions:
                for transition_emotion, transition_probability in self.emotion_transitions[emotion].items():
                    if random.random() < transition_probability * dt * 0.1:
                        transition_intensity = new_intensity * 0.3
                        evolved[transition_emotion] = evolved.get(transition_emotion, 0) + transition_intensity
            
            if new_intensity > 0.05:  # Only keep emotions above threshold
                evolved[emotion] = new_intensity
        
        return evolved
    
    def _determine_primary_emotion(self, emotions: Dict[EmotionType, float]) -> EmotionType:
        """Determine the strongest emotion as primary"""
        if not emotions:
            return EmotionType.JOY  # Default neutral-positive state
        
        return max(emotions, key=emotions.get)
    
    def _calculate_emotional_intensity(self, emotions: Dict[EmotionType, float], 
                                     primary_emotion: EmotionType, events: List[str]) -> float:
        """Calculate the intensity of the primary emotion"""
        if primary_emotion not in emotions:
            return 0.1
        
        base_intensity = emotions[primary_emotion]
        
        # Boost intensity if recent events are emotionally significant
        if len(events) > 0:
            base_intensity *= 1.2
        
        return min(1.0, base_intensity)
    
    def _update_emotional_triggers(self, current_triggers: List[str], new_events: List[str]) -> List[str]:
        """Update the list of emotional triggers"""
        triggers = current_triggers.copy()
        triggers.extend(new_events)
        
        # Keep only recent triggers (last 5)
        return triggers[-5:]
    
    def get_behavior_modifiers(self, emotional_state: EmotionalState) -> Dict[str, float]:
        """Get behavior modifiers based on current emotional state"""
        modifiers = {}
        
        # Apply primary emotion modifiers
        if emotional_state.primary_emotion in self.mood_modifiers:
            primary_modifiers = self.mood_modifiers[emotional_state.primary_emotion]
            for behavior, modifier in primary_modifiers.items():
                weight = emotional_state.intensity
                modifiers[behavior] = modifier ** weight  # Scale by intensity
        
        # Apply secondary emotion modifiers (with less weight)
        for emotion, intensity in emotional_state.secondary_emotions.items():
            if emotion in self.mood_modifiers and intensity > 0.2:
                emotion_modifiers = self.mood_modifiers[emotion]
                for behavior, modifier in emotion_modifiers.items():
                    weight = intensity * 0.5  # Secondary emotions have half weight
                    current_modifier = modifiers.get(behavior, 1.0)
                    modifiers[behavior] = current_modifier * (modifier ** weight)
        
        return modifiers
    
    def generate_empathetic_dialogue(self, emotional_state: EmotionalState, 
                                   target_emotion: EmotionType, relationship_level: float) -> Optional[str]:
        """Generate empathetic dialogue based on emotional understanding"""
        
        empathy_responses = {
            EmotionType.SADNESS: [
                "I can see you're going through a tough time. I'm here if you need to talk.",
                "I'm sorry you're feeling down. Things will get better.",
                "You don't have to face this alone. I care about you."
            ],
            EmotionType.JOY: [
                "I'm so happy to see you in such good spirits!",
                "Your happiness is contagious! What's got you so cheerful?",
                "It's wonderful to see you so joyful!"
            ],
            EmotionType.ANGER: [
                "I can see you're upset. Do you want to talk about what's bothering you?",
                "I understand you're angry. Let's work through this together.",
                "Take a deep breath. I'm here to listen."
            ],
            EmotionType.FEAR: [
                "You seem worried. Is there anything I can do to help?",
                "It's okay to be afraid sometimes. You're not alone.",
                "I'm here with you. We'll get through this together."
            ]
        }
        
        # Only generate empathetic dialogue if relationship is strong enough
        if relationship_level < 0.3:
            return None
        
        responses = empathy_responses.get(target_emotion, [])
        if responses:
            # Choose response based on own emotional state
            if emotional_state.primary_emotion in [EmotionType.LOVE, EmotionType.TRUST, EmotionType.GRATITUDE]:
                return random.choice(responses)
            elif emotional_state.intensity > 0.7:
                # High emotional intensity might interfere with empathy
                return None
        
        return None
    
    def store_emotional_memory(self, npc_name: str, event_description: str, 
                             emotions_felt: Dict[EmotionType, float], 
                             people_involved: List[str], location: Tuple[int, int],
                             importance: float, timestamp: str):
        """Store an emotional memory for later recall"""
        
        if npc_name not in self.emotional_memories:
            self.emotional_memories[npc_name] = []
        
        memory = EmotionalMemory(
            event_description=event_description,
            emotions_felt=emotions_felt,
            people_involved=people_involved,
            location=location,
            importance=importance,
            timestamp=timestamp
        )
        
        self.emotional_memories[npc_name].append(memory)
        
        # Keep only the most important memories (last 30)
        self.emotional_memories[npc_name].sort(key=lambda x: x.importance, reverse=True)
        self.emotional_memories[npc_name] = self.emotional_memories[npc_name][:30]
    
    def recall_emotional_memories(self, npc_name: str, trigger_emotion: EmotionType = None,
                                trigger_person: str = None) -> List[EmotionalMemory]:
        """Recall emotional memories based on triggers"""
        
        if npc_name not in self.emotional_memories:
            return []
        
        memories = self.emotional_memories[npc_name]
        
        # Filter by triggers if provided
        if trigger_emotion:
            memories = [m for m in memories if trigger_emotion in m.emotions_felt]
        
        if trigger_person:
            memories = [m for m in memories if trigger_person in m.people_involved]
        
        # Sort by importance and recency
        memories.sort(key=lambda x: (x.importance, x.timestamp), reverse=True)
        
        return memories[:5]  # Return top 5 memories
    
    def get_emotional_compatibility(self, emotion1: EmotionType, emotion2: EmotionType) -> float:
        """Calculate emotional compatibility between two emotions"""
        
        compatibility_matrix = {
            (EmotionType.JOY, EmotionType.JOY): 1.0,
            (EmotionType.JOY, EmotionType.LOVE): 0.9,
            (EmotionType.JOY, EmotionType.GRATITUDE): 0.8,
            (EmotionType.SADNESS, EmotionType.SADNESS): 0.7,
            (EmotionType.ANGER, EmotionType.ANGER): 0.5,
            (EmotionType.FEAR, EmotionType.FEAR): 0.6,
            (EmotionType.JOY, EmotionType.SADNESS): 0.1,
            (EmotionType.JOY, EmotionType.ANGER): 0.2,
            (EmotionType.LOVE, EmotionType.ANGER): 0.3,
            (EmotionType.TRUST, EmotionType.FEAR): 0.2
        }
        
        # Check both directions
        key1 = (emotion1, emotion2)
        key2 = (emotion2, emotion1)
        
        if key1 in compatibility_matrix:
            return compatibility_matrix[key1]
        elif key2 in compatibility_matrix:
            return compatibility_matrix[key2]
        else:
            return 0.5  # Neutral compatibility