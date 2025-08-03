import random
import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

class ConversationTopic(Enum):
    WEATHER = "weather"
    RELATIONSHIPS = "relationships"
    HOBBIES = "hobbies"
    WORK = "work"
    GOSSIP = "gossip"
    DREAMS = "dreams"
    CURRENT_EVENTS = "current_events"
    MEMORIES = "memories"
    FEELINGS = "feelings"
    PLANS = "plans"
    SKILLS = "skills"
    RESOURCES = "resources"

@dataclass
class ConversationContext:
    """Context for a conversation between NPCs or NPC-Player"""
    topic: ConversationTopic
    initiator: str
    participant: str
    relationship_level: float
    location: Tuple[int, int]
    time_of_day: str
    mood: str
    previous_topics: List[ConversationTopic]
    shared_experiences: List[str]
    current_events: List[str]

@dataclass
class ConversationResponse:
    """Response generated for a conversation"""
    dialogue: str
    emotion: str
    topic_shift: Optional[ConversationTopic]
    relationship_change: float
    memory_importance: float
    follow_up_action: Optional[str]

class ConversationEngine:
    """
    Advanced conversation system for NPCs with context-aware dialogue,
    topic management, and relationship-driven responses
    """
    
    def __init__(self):
        self.conversation_history = {}  # npc_pair -> list of conversations
        self.topic_preferences = {}     # npc_name -> topic preferences
        self.conversation_starters = self._initialize_starters()
        self.topic_transitions = self._initialize_transitions()
        self.personality_responses = self._initialize_personality_responses()
        
    def _initialize_starters(self) -> Dict[ConversationTopic, List[str]]:
        """Initialize conversation starters for each topic"""
        return {
            ConversationTopic.WEATHER: [
                "Beautiful day today, isn't it?",
                "I hope it doesn't rain later.",
                "Perfect weather for working outside!",
                "This sunshine is making me feel energetic.",
                "I love days like this - not too hot, not too cold."
            ],
            ConversationTopic.RELATIONSHIPS: [
                "How are things going with your family?",
                "I saw you talking to {other_npc} earlier.",
                "You seem to get along well with everyone here.",
                "Have you made any new friends lately?",
                "I value our friendship a lot."
            ],
            ConversationTopic.HOBBIES: [
                "What do you like to do in your free time?",
                "I've been really into {hobby} lately.",
                "Have you tried {activity}? It's quite fun!",
                "I need a new hobby to keep me busy.",
                "You're so talented at {skill}!"
            ],
            ConversationTopic.WORK: [
                "How's work been treating you?",
                "I've been thinking about learning a new skill.",
                "The harvest season is always so busy.",
                "I saw you working hard on {task} yesterday.",
                "Want to collaborate on something together?"
            ],
            ConversationTopic.GOSSIP: [
                "Did you hear about what happened at {location}?",
                "I heard some interesting news from {other_npc}.",
                "There's been some drama around town lately.",
                "You didn't hear this from me, but...",
                "I probably shouldn't say this, but..."
            ],
            ConversationTopic.DREAMS: [
                "I had the strangest dream last night.",
                "What do you want to achieve this year?",
                "Sometimes I dream about traveling far away.",
                "Do you ever think about what life would be like if...?",
                "I have this crazy idea I've been thinking about."
            ],
            ConversationTopic.CURRENT_EVENTS: [
                "Did you attend {event_name}?",
                "I'm excited about the upcoming {event}.",
                "Things have been really busy around town.",
                "Have you noticed how much the town has changed?",
                "I wonder what's planned for next season."
            ],
            ConversationTopic.MEMORIES: [
                "Remember when we {shared_memory}?",
                "I was just thinking about {past_event}.",
                "Those were good times, weren't they?",
                "I'll never forget when {memorable_moment}.",
                "Do you miss the old days sometimes?"
            ],
            ConversationTopic.FEELINGS: [
                "How are you feeling today?",
                "You seem {emotion} lately.",
                "I've been feeling a bit {personal_emotion} recently.",
                "It's nice to have someone to talk to about things.",
                "Sometimes I need to get things off my chest."
            ],
            ConversationTopic.PLANS: [
                "What are your plans for {time_period}?",
                "I'm thinking about {future_plan}.",
                "We should {suggested_activity} together sometime.",
                "I need to organize my schedule better.",
                "Want to make plans for {upcoming_event}?"
            ],
            ConversationTopic.SKILLS: [
                "You're getting really good at {skill}!",
                "I need to practice my {skill_name} more.",
                "Could you teach me how to {activity}?",
                "I've been working on improving my {skill}.",
                "Your {skill} has improved so much lately!"
            ],
            ConversationTopic.RESOURCES: [
                "I found some great {resource} near {location}.",
                "Do you know where I can find {needed_resource}?",
                "I have extra {resource} if you need any.",
                "The {resource} quality has been excellent lately.",
                "Want to go {activity} together? I know a good spot."
            ]
        }
    
    def _initialize_transitions(self) -> Dict[ConversationTopic, List[ConversationTopic]]:
        """Define natural topic transitions"""
        return {
            ConversationTopic.WEATHER: [ConversationTopic.WORK, ConversationTopic.PLANS, ConversationTopic.HOBBIES],
            ConversationTopic.RELATIONSHIPS: [ConversationTopic.FEELINGS, ConversationTopic.GOSSIP, ConversationTopic.MEMORIES],
            ConversationTopic.HOBBIES: [ConversationTopic.SKILLS, ConversationTopic.RESOURCES, ConversationTopic.PLANS],
            ConversationTopic.WORK: [ConversationTopic.SKILLS, ConversationTopic.RESOURCES, ConversationTopic.PLANS],
            ConversationTopic.GOSSIP: [ConversationTopic.RELATIONSHIPS, ConversationTopic.CURRENT_EVENTS, ConversationTopic.FEELINGS],
            ConversationTopic.DREAMS: [ConversationTopic.PLANS, ConversationTopic.FEELINGS, ConversationTopic.HOBBIES],
            ConversationTopic.CURRENT_EVENTS: [ConversationTopic.PLANS, ConversationTopic.RELATIONSHIPS, ConversationTopic.FEELINGS],
            ConversationTopic.MEMORIES: [ConversationTopic.RELATIONSHIPS, ConversationTopic.FEELINGS, ConversationTopic.DREAMS],
            ConversationTopic.FEELINGS: [ConversationTopic.RELATIONSHIPS, ConversationTopic.DREAMS, ConversationTopic.PLANS],
            ConversationTopic.PLANS: [ConversationTopic.WORK, ConversationTopic.HOBBIES, ConversationTopic.RELATIONSHIPS],
            ConversationTopic.SKILLS: [ConversationTopic.WORK, ConversationTopic.HOBBIES, ConversationTopic.RESOURCES],
            ConversationTopic.RESOURCES: [ConversationTopic.WORK, ConversationTopic.SKILLS, ConversationTopic.PLANS]
        }
    
    def _initialize_personality_responses(self) -> Dict[str, Dict[ConversationTopic, List[str]]]:
        """Initialize personality-specific response patterns"""
        return {
            "extrovert": {
                ConversationTopic.RELATIONSHIPS: [
                    "I love meeting new people! Want to introduce me to {other_npc}?",
                    "We should throw a party and invite everyone!",
                    "I think {other_npc} and I would get along great."
                ],
                ConversationTopic.CURRENT_EVENTS: [
                    "I'm so excited about {event}! Are you going?",
                    "Let's organize something fun for everyone!",
                    "The more people involved, the better!"
                ]
            },
            "introvert": {
                ConversationTopic.RELATIONSHIPS: [
                    "I prefer having a few close friends rather than many acquaintances.",
                    "Quality time with people I care about means everything.",
                    "Sometimes I need some alone time to recharge."
                ],
                ConversationTopic.HOBBIES: [
                    "I love activities I can do quietly by myself.",
                    "Reading and crafting are my favorite pastimes.",
                    "There's something peaceful about {solitary_activity}."
                ]
            },
            "optimist": {
                ConversationTopic.WEATHER: [
                    "Every day is a gift! Even rainy days have their charm.",
                    "I always look for the bright side of things.",
                    "This weather reminds me of all the possibilities ahead!"
                ],
                ConversationTopic.PLANS: [
                    "I have such exciting plans for {time_period}!",
                    "I believe great things are coming our way.",
                    "Let's make this the best {time_period} yet!"
                ]
            },
            "pessimist": {
                ConversationTopic.WEATHER: [
                    "I hope this nice weather lasts, but it probably won't.",
                    "There's probably a storm coming later.",
                    "Weather like this makes me worry about what's next."
                ],
                ConversationTopic.PLANS: [
                    "I hope these plans work out, but you never know...",
                    "I'm trying not to get my hopes up too much.",
                    "Things rarely go according to plan, in my experience."
                ]
            }
        }
    
    def generate_conversation(self, context: ConversationContext, npc_personality: Dict, ai_client=None) -> ConversationResponse:
        """Generate a contextual conversation response"""
        
        # Choose appropriate topic based on context and personality
        topic = self._choose_conversation_topic(context, npc_personality)
        
        # Generate base dialogue
        base_dialogue = self._generate_base_dialogue(topic, context, npc_personality)
        
        # Enhance with AI if available
        if ai_client:
            enhanced_dialogue = self._enhance_with_ai(base_dialogue, context, npc_personality, ai_client)
        else:
            enhanced_dialogue = base_dialogue
        
        # Determine emotional response
        emotion = self._determine_emotion(topic, context, npc_personality)
        
        # Calculate relationship impact
        relationship_change = self._calculate_relationship_change(topic, context, npc_personality)
        
        # Determine if topic should shift
        topic_shift = self._determine_topic_shift(context, npc_personality)
        
        # Calculate memory importance
        memory_importance = self._calculate_memory_importance(topic, context, relationship_change)
        
        # Determine follow-up action
        follow_up_action = self._determine_follow_up_action(topic, context, npc_personality)
        
        return ConversationResponse(
            dialogue=enhanced_dialogue,
            emotion=emotion,
            topic_shift=topic_shift,
            relationship_change=relationship_change,
            memory_importance=memory_importance,
            follow_up_action=follow_up_action
        )
    
    def _choose_conversation_topic(self, context: ConversationContext, personality: Dict) -> ConversationTopic:
        """Choose appropriate conversation topic based on context and personality"""
        
        # Avoid recently discussed topics unless relationship is very high
        if context.relationship_level < 0.8:
            available_topics = [topic for topic in ConversationTopic if topic not in context.previous_topics[-3:]]
        else:
            available_topics = list(ConversationTopic)
        
        # Weight topics based on personality
        topic_weights = {}
        for topic in available_topics:
            weight = 1.0
            
            # Personality-based preferences
            if personality.get("friendliness", 0.5) > 0.7:
                if topic in [ConversationTopic.RELATIONSHIPS, ConversationTopic.FEELINGS]:
                    weight += 0.5
            
            if personality.get("creativity", 0.5) > 0.7:
                if topic in [ConversationTopic.DREAMS, ConversationTopic.HOBBIES]:
                    weight += 0.5
            
            if personality.get("confidence", 0.5) > 0.7:
                if topic in [ConversationTopic.PLANS, ConversationTopic.WORK]:
                    weight += 0.5
            
            # Context-based preferences
            if context.shared_experiences and topic == ConversationTopic.MEMORIES:
                weight += 0.8
            
            if context.current_events and topic == ConversationTopic.CURRENT_EVENTS:
                weight += 0.6
            
            # Time of day preferences
            if context.time_of_day == "morning" and topic == ConversationTopic.PLANS:
                weight += 0.3
            elif context.time_of_day == "evening" and topic in [ConversationTopic.FEELINGS, ConversationTopic.MEMORIES]:
                weight += 0.3
            
            topic_weights[topic] = weight
        
        # Choose topic based on weights
        return self._weighted_choice(topic_weights)
    
    def _generate_base_dialogue(self, topic: ConversationTopic, context: ConversationContext, personality: Dict) -> str:
        """Generate base dialogue for the chosen topic"""
        
        starters = self.conversation_starters.get(topic, ["Hello there!"])
        base_dialogue = random.choice(starters)
        
        # Add personality flavor
        personality_type = self._determine_personality_type(personality)
        if personality_type in self.personality_responses and topic in self.personality_responses[personality_type]:
            personality_responses = self.personality_responses[personality_type][topic]
            if random.random() < 0.4:  # 40% chance to use personality-specific response
                base_dialogue = random.choice(personality_responses)
        
        # Replace placeholders with context-specific information
        base_dialogue = self._replace_placeholders(base_dialogue, context)
        
        return base_dialogue
    
    def _enhance_with_ai(self, base_dialogue: str, context: ConversationContext, personality: Dict, ai_client) -> str:
        """Enhance dialogue using AI for more natural conversation"""
        
        prompt = f"""
        Enhance this dialogue to be more natural and contextual:
        
        Base dialogue: "{base_dialogue}"
        
        Context:
        - Speaker: {context.initiator}
        - Listener: {context.participant}
        - Relationship level: {context.relationship_level:.1f}/1.0
        - Current mood: {context.mood}
        - Location: {context.location}
        - Time: {context.time_of_day}
        - Previous topics: {[t.value for t in context.previous_topics[-3:]]}
        
        Personality traits: {personality}
        
        Make it sound more natural, personal, and appropriate for the context.
        Keep it conversational and under 100 characters.
        Return only the enhanced dialogue, no quotes or explanation.
        """
        
        try:
            response = ai_client.generate_response(prompt)
            if response and len(response.strip()) > 0:
                return response.strip()[:150]  # Limit length
        except Exception as e:
            print(f"AI enhancement failed: {e}")
        
        return base_dialogue
    
    def _determine_emotion(self, topic: ConversationTopic, context: ConversationContext, personality: Dict) -> str:
        """Determine emotional state based on topic and context"""
        
        base_emotions = {
            ConversationTopic.WEATHER: "content",
            ConversationTopic.RELATIONSHIPS: "warm",
            ConversationTopic.HOBBIES: "enthusiastic",
            ConversationTopic.WORK: "focused",
            ConversationTopic.GOSSIP: "excited",
            ConversationTopic.DREAMS: "wistful",
            ConversationTopic.CURRENT_EVENTS: "interested",
            ConversationTopic.MEMORIES: "nostalgic",
            ConversationTopic.FEELINGS: "thoughtful",
            ConversationTopic.PLANS: "optimistic",
            ConversationTopic.SKILLS: "proud",
            ConversationTopic.RESOURCES: "helpful"
        }
        
        emotion = base_emotions.get(topic, "neutral")
        
        # Modify based on relationship level
        if context.relationship_level > 0.8:
            if emotion == "content":
                emotion = "happy"
            elif emotion == "interested":
                emotion = "excited"
        elif context.relationship_level < 0.3:
            if emotion in ["warm", "enthusiastic"]:
                emotion = "polite"
        
        # Modify based on personality
        if personality.get("friendliness", 0.5) > 0.8:
            if emotion == "neutral":
                emotion = "friendly"
        
        return emotion
    
    def _calculate_relationship_change(self, topic: ConversationTopic, context: ConversationContext, personality: Dict) -> float:
        """Calculate how this conversation affects the relationship"""
        
        base_change = 0.02  # Small positive change for any conversation
        
        # Topic-based modifiers
        topic_modifiers = {
            ConversationTopic.RELATIONSHIPS: 0.05,
            ConversationTopic.FEELINGS: 0.04,
            ConversationTopic.MEMORIES: 0.03,
            ConversationTopic.DREAMS: 0.03,
            ConversationTopic.GOSSIP: -0.01,  # Slight negative for gossip
        }
        
        base_change += topic_modifiers.get(topic, 0)
        
        # Personality compatibility
        friendliness = personality.get("friendliness", 0.5)
        base_change *= (0.5 + friendliness)
        
        # Relationship level affects potential change (harder to improve high relationships)
        if context.relationship_level > 0.7:
            base_change *= 0.5
        elif context.relationship_level < 0.3:
            base_change *= 1.5  # Easier to improve low relationships
        
        return max(-0.1, min(0.1, base_change))  # Cap at ±0.1
    
    def _determine_topic_shift(self, context: ConversationContext, personality: Dict) -> Optional[ConversationTopic]:
        """Determine if conversation should shift to a new topic"""
        
        # Higher chance of topic shift for extroverts
        shift_chance = 0.3
        if personality.get("confidence", 0.5) > 0.7:
            shift_chance += 0.2
        
        if random.random() < shift_chance:
            available_transitions = self.topic_transitions.get(context.topic, [])
            if available_transitions:
                return random.choice(available_transitions)
        
        return None
    
    def _calculate_memory_importance(self, topic: ConversationTopic, context: ConversationContext, relationship_change: float) -> float:
        """Calculate how important this conversation is for memory storage"""
        
        importance = 0.3  # Base importance
        
        # Topic importance
        important_topics = [ConversationTopic.RELATIONSHIPS, ConversationTopic.DREAMS, ConversationTopic.FEELINGS]
        if topic in important_topics:
            importance += 0.3
        
        # Relationship change importance
        importance += abs(relationship_change) * 2
        
        # High relationship conversations are more memorable
        if context.relationship_level > 0.7:
            importance += 0.2
        
        return min(1.0, importance)
    
    def _determine_follow_up_action(self, topic: ConversationTopic, context: ConversationContext, personality: Dict) -> Optional[str]:
        """Determine if this conversation should lead to an action"""
        
        action_topics = {
            ConversationTopic.PLANS: ["schedule_meeting", "plan_activity"],
            ConversationTopic.HOBBIES: ["suggest_activity", "teach_skill"],
            ConversationTopic.WORK: ["offer_help", "collaborate"],
            ConversationTopic.RESOURCES: ["share_resource", "go_gathering"],
            ConversationTopic.SKILLS: ["practice_together", "offer_lesson"]
        }
        
        if topic in action_topics and context.relationship_level > 0.5:
            if random.random() < 0.3:  # 30% chance of follow-up action
                return random.choice(action_topics[topic])
        
        return None
    
    def _determine_personality_type(self, personality: Dict) -> str:
        """Determine primary personality type for response selection"""
        
        friendliness = personality.get("friendliness", 0.5)
        confidence = personality.get("confidence", 0.5)
        
        if friendliness > 0.7 and confidence > 0.6:
            return "extrovert"
        elif friendliness < 0.4 or confidence < 0.4:
            return "introvert"
        elif personality.get("optimism", 0.5) > 0.7:
            return "optimist"
        elif personality.get("optimism", 0.5) < 0.3:
            return "pessimist"
        
        return "balanced"
    
    def _replace_placeholders(self, dialogue: str, context: ConversationContext) -> str:
        """Replace placeholders in dialogue with context-specific information"""
        
        replacements = {
            "{other_npc}": context.participant,
            "{location}": f"coordinates {context.location}",
            "{time_period}": context.time_of_day,
            "{event}": context.current_events[0] if context.current_events else "the festival",
            "{event_name}": context.current_events[0] if context.current_events else "the local event",
            "{shared_memory}": context.shared_experiences[0] if context.shared_experiences else "had that adventure",
            "{hobby}": random.choice(["farming", "fishing", "cooking", "crafting"]),
            "{activity}": random.choice(["gardening", "exploring", "reading", "music"]),
            "{skill}": random.choice(["farming", "mining", "foraging", "fishing"]),
            "{resource}": random.choice(["wood", "stone", "berries", "herbs"]),
            "{emotion}": context.mood,
            "{personal_emotion}": context.mood
        }
        
        for placeholder, replacement in replacements.items():
            dialogue = dialogue.replace(placeholder, replacement)
        
        return dialogue
    
    def _weighted_choice(self, weights: Dict) -> any:
        """Choose item based on weights"""
        total = sum(weights.values())
        if total == 0:
            return random.choice(list(weights.keys()))
        
        r = random.uniform(0, total)
        current = 0
        for item, weight in weights.items():
            current += weight
            if r <= current:
                return item
        
        return list(weights.keys())[-1]
    
    def get_conversation_history(self, npc1: str, npc2: str) -> List[Dict]:
        """Get conversation history between two NPCs"""
        pair = tuple(sorted([npc1, npc2]))
        return self.conversation_history.get(pair, [])
    
    def record_conversation(self, context: ConversationContext, response: ConversationResponse):
        """Record conversation for future reference"""
        pair = tuple(sorted([context.initiator, context.participant]))
        
        if pair not in self.conversation_history:
            self.conversation_history[pair] = []
        
        conversation_record = {
            "timestamp": datetime.datetime.now().isoformat(),
            "topic": context.topic.value,
            "dialogue": response.dialogue,
            "emotion": response.emotion,
            "relationship_change": response.relationship_change,
            "location": context.location,
            "importance": response.memory_importance
        }
        
        self.conversation_history[pair].append(conversation_record)
        
        # Keep only recent conversations (last 20)
        if len(self.conversation_history[pair]) > 20:
            self.conversation_history[pair] = self.conversation_history[pair][-20:]