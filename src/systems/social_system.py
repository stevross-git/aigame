from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum
import random
import re

class InteractionType(Enum):
    GREETING = "greeting"
    CHAT = "chat"
    COMPLIMENT = "compliment"
    GIFT = "gift"
    JOKE = "joke"
    HELP_OFFER = "help_offer"
    QUESTION = "question"
    GOSSIP = "gossip"
    APOLOGY = "apology"
    INSULT = "insult"
    COMPLAINT = "complaint"
    CUSTOM = "custom"

class SentimentType(Enum):
    VERY_POSITIVE = "very_positive"
    POSITIVE = "positive" 
    NEUTRAL = "neutral"
    NEGATIVE = "negative"
    VERY_NEGATIVE = "very_negative"

@dataclass
class InteractionRating:
    """Rating given by NPC for a player interaction"""
    base_score: float  # 0-10 scale
    sentiment_modifier: float  # -2 to +2
    personality_modifier: float  # -1 to +1 based on NPC personality
    relationship_modifier: float  # -1 to +1 based on existing relationship
    context_modifier: float  # -1 to +1 based on context (time, mood, etc.)
    final_score: float  # Final calculated score
    social_points_awarded: int  # Points given to player
    feedback_message: str  # What the NPC thought about the interaction

@dataclass
class SocialPoints:
    """Player's social experience system"""
    total_points: int = 0
    level: int = 1
    points_to_next_level: int = 100
    interaction_bonuses: Dict[str, float] = None  # Bonuses for different interaction types
    
    def __post_init__(self):
        if self.interaction_bonuses is None:
            self.interaction_bonuses = {}

class SocialSystem:
    """
    Manages social interactions, NPC ratings, and player social progression
    """
    
    def __init__(self, player=None):
        self.player = player
        self.social_points = SocialPoints()
        
        # Sentiment analysis keywords
        self.positive_keywords = {
            'love', 'like', 'great', 'awesome', 'wonderful', 'amazing', 'fantastic',
            'beautiful', 'nice', 'good', 'excellent', 'perfect', 'brilliant',
            'thank', 'thanks', 'grateful', 'appreciate', 'help', 'kind'
        }
        
        self.negative_keywords = {
            'hate', 'dislike', 'terrible', 'awful', 'bad', 'horrible', 'disgusting',
            'stupid', 'idiot', 'annoying', 'boring', 'ugly', 'worst', 'suck',
            'angry', 'mad', 'upset', 'disappointed'
        }
        
        # Base scores for different interaction types
        self.interaction_base_scores = {
            InteractionType.GREETING: 6.0,
            InteractionType.CHAT: 7.0,
            InteractionType.COMPLIMENT: 8.5,
            InteractionType.GIFT: 9.0,
            InteractionType.JOKE: 7.5,
            InteractionType.HELP_OFFER: 8.0,
            InteractionType.QUESTION: 6.5,
            InteractionType.GOSSIP: 5.5,
            InteractionType.APOLOGY: 7.0,
            InteractionType.INSULT: 2.0,
            InteractionType.COMPLAINT: 4.0,
            InteractionType.CUSTOM: 6.0
        }
        
        # Social points awarded based on score ranges
        self.score_to_points = {
            (9.0, 10.0): 25,  # Exceptional interaction
            (8.0, 8.99): 20,  # Great interaction
            (7.0, 7.99): 15,  # Good interaction
            (6.0, 6.99): 10,  # Decent interaction
            (5.0, 5.99): 5,   # Mediocre interaction
            (3.0, 4.99): 2,   # Poor interaction
            (0.0, 2.99): 0    # Very poor interaction
        }
    
    def analyze_sentiment(self, message: str) -> Tuple[SentimentType, float]:
        """Analyze the sentiment of a message"""
        if not message:
            return SentimentType.NEUTRAL, 0.0
        
        message_lower = message.lower()
        words = re.findall(r'\b\w+\b', message_lower)
        
        positive_count = sum(1 for word in words if word in self.positive_keywords)
        negative_count = sum(1 for word in words if word in self.negative_keywords)
        
        # Calculate sentiment score (-2 to +2)
        total_words = len(words)
        if total_words == 0:
            return SentimentType.NEUTRAL, 0.0
        
        sentiment_score = (positive_count - negative_count) / max(total_words, 1) * 4
        sentiment_score = max(-2.0, min(2.0, sentiment_score))
        
        # Classify sentiment
        if sentiment_score >= 1.0:
            return SentimentType.VERY_POSITIVE, sentiment_score
        elif sentiment_score >= 0.3:
            return SentimentType.POSITIVE, sentiment_score
        elif sentiment_score <= -1.0:
            return SentimentType.VERY_NEGATIVE, sentiment_score
        elif sentiment_score <= -0.3:
            return SentimentType.NEGATIVE, sentiment_score
        else:
            return SentimentType.NEUTRAL, sentiment_score
    
    def calculate_personality_modifier(self, npc, interaction_type: InteractionType, message: str = "") -> float:
        """Calculate how NPC personality affects their rating of the interaction"""
        if not hasattr(npc, 'personality'):
            return 0.0
        
        personality = npc.personality
        modifier = 0.0
        
        # Extroversion affects social interactions
        if interaction_type in [InteractionType.CHAT, InteractionType.GREETING, InteractionType.JOKE]:
            if personality.extroversion > 0.7:
                modifier += 0.3  # Extroverts love social interaction
            elif personality.extroversion < 0.3:
                modifier -= 0.2  # Introverts are more reserved
        
        # Agreeableness affects how they receive different types of interactions
        if interaction_type in [InteractionType.COMPLIMENT, InteractionType.GIFT, InteractionType.HELP_OFFER]:
            modifier += (personality.agreeableness - 0.5) * 0.4
        
        # Openness affects reaction to jokes and interesting conversation
        if interaction_type in [InteractionType.JOKE, InteractionType.CHAT]:
            modifier += (personality.openness - 0.5) * 0.3
        
        # Neuroticism affects sensitivity to negative interactions
        if interaction_type in [InteractionType.INSULT, InteractionType.COMPLAINT]:
            modifier -= personality.neuroticism * 0.5
        
        # Conscientiousness affects appreciation for help and structured interactions
        if interaction_type in [InteractionType.HELP_OFFER, InteractionType.QUESTION]:
            modifier += (personality.conscientiousness - 0.5) * 0.2
        
        return max(-1.0, min(1.0, modifier))
    
    def calculate_relationship_modifier(self, npc, player_name: str) -> float:
        """Calculate how existing relationship affects the rating"""
        if not hasattr(npc, 'relationships') or player_name not in npc.relationships:
            return 0.0  # Neutral for new relationships
        
        relationship_level = npc.relationships[player_name]
        
        # Convert relationship (0-1) to modifier (-1 to +1)
        # Higher relationships give more positive modifiers
        if relationship_level >= 0.8:
            return 0.8  # Great friends
        elif relationship_level >= 0.6:
            return 0.4  # Good friends
        elif relationship_level >= 0.4:
            return 0.1  # Friendly
        elif relationship_level >= 0.2:
            return -0.1  # Acquaintances
        else:
            return -0.3  # Poor relationship
    
    def calculate_context_modifier(self, npc) -> float:
        """Calculate contextual modifiers based on NPC state"""
        modifier = 0.0
        
        # Check NPC needs
        if hasattr(npc, 'needs'):
            # Low social need makes them more appreciative of interaction
            if npc.needs.get('social', 1.0) < 0.3:
                modifier += 0.4
            
            # Low energy/sleep makes them less receptive
            if npc.needs.get('sleep', 1.0) < 0.3:
                modifier -= 0.3
            
            # Low fun makes them appreciate jokes and entertainment more
            if npc.needs.get('fun', 1.0) < 0.4:
                modifier += 0.2
        
        # Check emotional state
        if hasattr(npc, 'emotional_state'):
            emotion = npc.emotional_state.primary_emotion.value if hasattr(npc.emotional_state, 'primary_emotion') else 'neutral'
            intensity = getattr(npc.emotional_state, 'intensity', 0.5)
            
            if emotion in ['joy', 'trust', 'anticipation']:
                modifier += intensity * 0.3
            elif emotion in ['sadness', 'fear', 'anger']:
                modifier -= intensity * 0.4
        
        # Social battery affects receptiveness
        if hasattr(npc, 'social_battery'):
            if npc.social_battery < 0.2:
                modifier -= 0.5  # Socially drained
            elif npc.social_battery > 0.8:
                modifier += 0.2  # Socially energized
        
        return max(-1.0, min(1.0, modifier))
    
    def rate_interaction(self, npc, player_name: str, interaction_type: InteractionType, 
                        message: str = "", gift_value: int = 0) -> InteractionRating:
        """Rate a player interaction and return detailed feedback"""
        
        # Get base score for interaction type
        base_score = self.interaction_base_scores.get(interaction_type, 6.0)
        
        # Adjust base score for gifts based on value
        if interaction_type == InteractionType.GIFT and gift_value > 0:
            # Scale gift score based on value (expensive gifts get higher scores)
            gift_bonus = min(1.5, gift_value / 100.0)  # Max 1.5 bonus for 150g+ gifts
            base_score += gift_bonus
        
        # Analyze message sentiment
        sentiment_type, sentiment_score = self.analyze_sentiment(message)
        
        # Calculate modifiers
        personality_mod = self.calculate_personality_modifier(npc, interaction_type, message)
        relationship_mod = self.calculate_relationship_modifier(npc, player_name)
        context_mod = self.calculate_context_modifier(npc)
        
        # Calculate final score (0-10 scale)
        final_score = base_score + sentiment_score + personality_mod + relationship_mod + context_mod
        final_score = max(0.0, min(10.0, final_score))
        
        # Determine social points awarded
        social_points = 0
        for (min_score, max_score), points in self.score_to_points.items():
            if min_score <= final_score <= max_score:
                social_points = points
                break
        
        # Generate feedback message
        feedback_message = self._generate_feedback_message(npc, final_score, sentiment_type, interaction_type)
        
        rating = InteractionRating(
            base_score=base_score,
            sentiment_modifier=sentiment_score,
            personality_modifier=personality_mod,
            relationship_modifier=relationship_mod,
            context_modifier=context_mod,
            final_score=final_score,
            social_points_awarded=social_points,
            feedback_message=feedback_message
        )
        
        # Award social points to player
        if social_points > 0:
            self.award_social_points(social_points, interaction_type.value)
        
        return rating
    
    def _generate_feedback_message(self, npc, score: float, sentiment: SentimentType, 
                                 interaction_type: InteractionType) -> str:
        """Generate NPC's internal feedback about the interaction"""
        
        npc_name = getattr(npc, 'name', 'NPC')
        
        if score >= 9.0:
            messages = [
                f"{npc_name} thinks that was an amazing interaction!",
                f"{npc_name} is really impressed by your social skills!",
                f"{npc_name} feels a strong connection with you!",
                f"{npc_name} thinks you're wonderful to talk to!"
            ]
        elif score >= 8.0:
            messages = [
                f"{npc_name} really enjoyed that conversation!",
                f"{npc_name} thinks you're very likeable!",
                f"{npc_name} feels much better after talking to you!",
                f"{npc_name} appreciates your kindness!"
            ]
        elif score >= 7.0:
            messages = [
                f"{npc_name} had a nice time chatting!",
                f"{npc_name} likes your friendly approach!",
                f"{npc_name} feels good about the interaction!",
                f"{npc_name} thinks you're pleasant company!"
            ]
        elif score >= 6.0:
            messages = [
                f"{npc_name} thought that was okay.",
                f"{npc_name} doesn't mind talking to you.",
                f"{npc_name} feels neutral about the interaction.",
                f"{npc_name} thinks you're alright."
            ]
        elif score >= 4.0:
            messages = [
                f"{npc_name} wasn't very impressed.",
                f"{npc_name} thought that was a bit awkward.",
                f"{npc_name} feels slightly uncomfortable.",
                f"{npc_name} wishes the conversation went better."
            ]
        else:
            messages = [
                f"{npc_name} really didn't like that.",
                f"{npc_name} feels upset by the interaction.",
                f"{npc_name} thinks you were rude.",
                f"{npc_name} wants to avoid you now."
            ]
        
        return random.choice(messages)
    
    def award_social_points(self, points: int, interaction_type: str):
        """Award social points and handle leveling up"""
        if not self.player:
            return
        
        self.social_points.total_points += points
        
        # Check for level up
        while self.social_points.total_points >= self.social_points.points_to_next_level:
            self.social_points.total_points -= self.social_points.points_to_next_level
            self.social_points.level += 1
            
            # Increase points needed for next level
            self.social_points.points_to_next_level = int(100 * (1.2 ** (self.social_points.level - 1)))
            
            # Award bonuses for interaction types
            self._unlock_social_bonuses()
            
            # Notify player of level up
            if hasattr(self.player, 'say'):
                self.player.say(f"Social Level Up! Now level {self.social_points.level}")
    
    def _unlock_social_bonuses(self):
        """Unlock bonuses at certain social levels"""
        level = self.social_points.level
        
        if level >= 5:
            self.social_points.interaction_bonuses['chat'] = 1.1
        if level >= 10:
            self.social_points.interaction_bonuses['compliment'] = 1.2
        if level >= 15:
            self.social_points.interaction_bonuses['gift'] = 1.15
        if level >= 20:
            self.social_points.interaction_bonuses['joke'] = 1.25
    
    def get_interaction_bonus(self, interaction_type: str) -> float:
        """Get the bonus multiplier for an interaction type"""
        return self.social_points.interaction_bonuses.get(interaction_type, 1.0)
    
    def get_social_status(self) -> Dict[str, Any]:
        """Get current social status for UI display"""
        return {
            'level': self.social_points.level,
            'total_points': self.social_points.total_points,
            'points_to_next_level': self.social_points.points_to_next_level,
            'progress_percentage': (self.social_points.total_points / self.social_points.points_to_next_level) * 100,
            'bonuses': self.social_points.interaction_bonuses.copy()
        }