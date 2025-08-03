import pygame
import json
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import time

class QuestType(Enum):
    TUTORIAL = "tutorial"
    STORY = "story"
    SIDE = "side"
    DAILY = "daily"
    ACHIEVEMENT = "achievement"

class QuestStatus(Enum):
    NOT_STARTED = "not_started"
    ACTIVE = "active"
    COMPLETED = "completed"
    FAILED = "failed"
    TURNED_IN = "turned_in"

class ObjectiveType(Enum):
    TALK_TO_NPC = "talk_to_npc"
    COLLECT_ITEMS = "collect_items"
    REACH_LOCATION = "reach_location"
    USE_ITEM = "use_item"
    ENTER_HOUSE = "enter_house"
    OPEN_INVENTORY = "open_inventory"
    CUT_TREE = "cut_tree"
    MINE_ROCK = "mine_rock"
    COOK_FOOD = "cook_food"
    PLANT_SEED = "plant_seed"
    SLEEP_IN_BED = "sleep_in_bed"
    LEVEL_UP_SKILL = "level_up_skill"
    EARN_XP = "earn_xp"
    SPEND_MONEY = "spend_money"
    CRAFT_ITEM = "craft_item"

@dataclass
class QuestObjective:
    """A single objective within a quest"""
    id: str
    type: ObjectiveType
    description: str
    target: str  # What to interact with (NPC name, item ID, location, etc.)
    required_amount: int = 1
    current_amount: int = 0
    completed: bool = False
    
    def is_complete(self) -> bool:
        return self.current_amount >= self.required_amount
    
    def progress(self, amount: int = 1):
        """Update progress on this objective"""
        self.current_amount = min(self.required_amount, self.current_amount + amount)
        self.completed = self.is_complete()

@dataclass
class QuestReward:
    """Rewards for completing a quest"""
    xp: int = 0
    money: int = 0
    items: Dict[str, int] = None  # item_id -> quantity
    unlock_features: List[str] = None  # Feature names to unlock
    
    def __post_init__(self):
        if self.items is None:
            self.items = {}
        if self.unlock_features is None:
            self.unlock_features = []

@dataclass
class Quest:
    """A complete quest with objectives and rewards"""
    id: str
    title: str
    description: str
    type: QuestType
    objectives: List[QuestObjective]
    rewards: QuestReward
    status: QuestStatus = QuestStatus.NOT_STARTED
    prerequisites: List[str] = None  # Quest IDs that must be completed first
    auto_start: bool = False
    repeatable: bool = False
    time_limit: Optional[float] = None  # Time limit in seconds
    start_time: Optional[float] = None
    giver_npc: Optional[str] = None  # NPC who gives this quest
    
    def __post_init__(self):
        if self.prerequisites is None:
            self.prerequisites = []
    
    def can_start(self, completed_quests: List[str]) -> bool:
        """Check if quest can be started based on prerequisites"""
        return all(prereq in completed_quests for prereq in self.prerequisites)
    
    def is_complete(self) -> bool:
        """Check if all objectives are completed"""
        return all(obj.completed for obj in self.objectives)
    
    def is_expired(self) -> bool:
        """Check if quest has expired"""
        if self.time_limit is None or self.start_time is None:
            return False
        return time.time() - self.start_time > self.time_limit
    
    def get_progress_text(self) -> str:
        """Get human-readable progress text"""
        completed = sum(1 for obj in self.objectives if obj.completed)
        total = len(self.objectives)
        return f"{completed}/{total} objectives completed"

class QuestSystem:
    """
    Comprehensive quest system for tutorials and gameplay progression
    """
    
    def __init__(self, game_systems: Dict[str, Any] = None):
        self.game_systems = game_systems or {}
        
        # Quest storage
        self.available_quests: Dict[str, Quest] = {}
        self.active_quests: Dict[str, Quest] = {}
        self.completed_quests: List[str] = []
        self.failed_quests: List[str] = []
        
        # Quest tracking
        self.quest_log_visible = False
        self.notification_queue: List[str] = []
        self.last_notification_time = 0
        
        # Feature unlocks
        self.unlocked_features: List[str] = []
        
        # Special event triggers
        self.trigger_steve_approach = False
        
        # Initialize tutorial quests
        self._initialize_tutorial_quests()
        self._initialize_progression_quests()
        self._initialize_npc_quests()
        
        # Auto-start initial quests
        self._auto_start_quests()
    
    def _initialize_tutorial_quests(self):
        """Initialize tutorial quests that teach basic mechanics"""
        
        # Tutorial 1: Basic Movement and Interface
        self.available_quests["tutorial_movement"] = Quest(
            id="tutorial_movement",
            title="Welcome to Your New Life!",
            description="Learn the basic controls and interface elements.",
            type=QuestType.TUTORIAL,
            objectives=[
                QuestObjective(
                    id="move_around",
                    type=ObjectiveType.REACH_LOCATION,
                    description="Move around using WASD or arrow keys",
                    target="any_location",
                    required_amount=1
                ),
                QuestObjective(
                    id="open_inventory",
                    type=ObjectiveType.OPEN_INVENTORY,
                    description="Open your inventory with 'I' or 'Tab'",
                    target="inventory",
                    required_amount=1
                )
            ],
            rewards=QuestReward(
                xp=50,
                money=100,
                items={"basic_axe": 1},
                unlock_features=["inventory_tutorial"]
            ),
            auto_start=True
        )
        
        # Steve's Introduction Quest - starts after first quest
        self.available_quests["steve_introduction"] = Quest(
            id="steve_introduction",
            title="A Wealthy Proposition",
            description="Steve, the wealthy businessman, wants to meet you and has a proposal.",
            type=QuestType.STORY,
            objectives=[
                QuestObjective(
                    id="talk_to_steve",
                    type=ObjectiveType.TALK_TO_NPC,
                    description="Talk to Steve about his business proposal",
                    target="Steve",
                    required_amount=1
                ),
                QuestObjective(
                    id="gather_initial_wood",
                    type=ObjectiveType.COLLECT_ITEMS,
                    description="Gather 5 wood to show you can work",
                    target="wood",
                    required_amount=5
                )
            ],
            rewards=QuestReward(
                xp=100,
                money=250,
                items={"basic_pickaxe": 1},
                unlock_features=["business_starter"]
            ),
            giver_npc="Steve",
            prerequisites=["tutorial_movement"]
        )
        
        # Tutorial 2: Your House
        self.available_quests["tutorial_house"] = Quest(
            id="tutorial_house",
            title="Home Sweet Home",
            description="Explore your house and learn about furniture interactions.",
            type=QuestType.TUTORIAL,
            objectives=[
                QuestObjective(
                    id="enter_house",
                    type=ObjectiveType.ENTER_HOUSE,
                    description="Enter your house by pressing 'H' near the door",
                    target="player_house",
                    required_amount=1
                ),
                QuestObjective(
                    id="sleep_in_bed",
                    type=ObjectiveType.SLEEP_IN_BED,
                    description="Rest in your bed to restore energy",
                    target="bed",
                    required_amount=1
                )
            ],
            rewards=QuestReward(
                xp=75,
                money=50,
                unlock_features=["house_tutorial"]
            ),
            prerequisites=["tutorial_movement"]
        )
        
        # Tutorial 3: Resource Gathering
        self.available_quests["tutorial_gathering"] = Quest(
            id="tutorial_gathering",
            title="Living Off the Land",
            description="Learn to gather resources from the environment.",
            type=QuestType.TUTORIAL,
            objectives=[
                QuestObjective(
                    id="cut_first_tree",
                    type=ObjectiveType.CUT_TREE,
                    description="Cut down a tree to get wood (you'll need an axe)",
                    target="oak_tree",
                    required_amount=1
                ),
                QuestObjective(
                    id="mine_first_rock",
                    type=ObjectiveType.MINE_ROCK,
                    description="Mine a rock to get stone (you'll need a pickaxe)",
                    target="stone_node",
                    required_amount=1
                ),
                QuestObjective(
                    id="collect_wood",
                    type=ObjectiveType.COLLECT_ITEMS,
                    description="Collect 5 pieces of wood",
                    target="wood",
                    required_amount=5
                )
            ],
            rewards=QuestReward(
                xp=100,
                money=75,
                items={"basic_axe": 1, "basic_pickaxe": 1},
                unlock_features=["resource_tutorial"]
            ),
            prerequisites=["tutorial_house"]
        )
    
    def _initialize_progression_quests(self):
        """Initialize quests for game progression"""
        
        # Progression 1: First Steps in Industry
        self.available_quests["first_craftsman"] = Quest(
            id="first_craftsman",
            title="Aspiring Craftsman",
            description="Begin your journey as a skilled craftsperson.",
            type=QuestType.STORY,
            objectives=[
                QuestObjective(
                    id="craft_chest",
                    type=ObjectiveType.CRAFT_ITEM,
                    description="Craft a chest for storage",
                    target="chest",
                    required_amount=1
                ),
                QuestObjective(
                    id="level_up_crafting",
                    type=ObjectiveType.LEVEL_UP_SKILL,
                    description="Reach level 2 in any skill",
                    target="any_skill",
                    required_amount=1
                ),
                QuestObjective(
                    id="earn_first_xp",
                    type=ObjectiveType.EARN_XP,
                    description="Earn 500 total XP",
                    target="total_xp",
                    required_amount=500
                )
            ],
            rewards=QuestReward(
                xp=200,
                money=300,
                items={"copper_axe": 1, "preserve_jar": 1},
                unlock_features=["advanced_crafting"]
            ),
            prerequisites=["tutorial_gathering"]
        )
        
        # Progression 2: Social Butterfly
        self.available_quests["social_starter"] = Quest(
            id="social_starter",
            title="Making Friends",
            description="Get to know your neighbors and build relationships.",
            type=QuestType.STORY,
            objectives=[
                QuestObjective(
                    id="talk_to_three_npcs",
                    type=ObjectiveType.TALK_TO_NPC,
                    description="Have conversations with 3 different NPCs",
                    target="any_npc",
                    required_amount=3
                ),
                QuestObjective(
                    id="spend_money",
                    type=ObjectiveType.SPEND_MONEY,
                    description="Purchase something worth at least 100g",
                    target="shop",
                    required_amount=100
                )
            ],
            rewards=QuestReward(
                xp=150,
                money=200,
                items={"bread": 5, "milk": 3},
                unlock_features=["relationship_system"]
            ),
            prerequisites=["tutorial_gathering"]
        )
    
    def _initialize_npc_quests(self):
        """Initialize quests involving AI NPC interactions"""
        
        # NPC Quest 1: The Friendly Farmer
        self.available_quests["friendly_farmer"] = Quest(
            id="friendly_farmer",
            title="A Farmer's Wisdom",
            description="Talk to Marcus, the village farmer, to learn about agriculture.",
            type=QuestType.SIDE,
            objectives=[
                QuestObjective(
                    id="find_marcus",
                    type=ObjectiveType.TALK_TO_NPC,
                    description="Find and talk to Marcus about farming",
                    target="Marcus",
                    required_amount=1
                ),
                QuestObjective(
                    id="plant_seeds",
                    type=ObjectiveType.PLANT_SEED,
                    description="Plant 3 seeds as Marcus suggested",
                    target="any_seed",
                    required_amount=3
                ),
                QuestObjective(
                    id="report_to_marcus",
                    type=ObjectiveType.TALK_TO_NPC,
                    description="Report back to Marcus about your farming progress",
                    target="Marcus",
                    required_amount=1
                )
            ],
            rewards=QuestReward(
                xp=125,
                money=150,
                items={"parsnip_seeds": 10, "potato_seeds": 5},
                unlock_features=["farming_tips"]
            ),
            giver_npc="Marcus",
            prerequisites=["tutorial_gathering"]
        )
        
        # NPC Quest 2: The Village Shopkeeper
        self.available_quests["shopkeeper_introduction"] = Quest(
            id="shopkeeper_introduction",
            title="Meet the Shopkeeper",
            description="Sarah, the shopkeeper, wants to meet the new resident.",
            type=QuestType.SIDE,
            objectives=[
                QuestObjective(
                    id="talk_to_sarah",
                    type=ObjectiveType.TALK_TO_NPC,
                    description="Introduce yourself to Sarah at the shop",
                    target="Sarah",
                    required_amount=1
                ),
                QuestObjective(
                    id="sell_items",
                    type=ObjectiveType.SPEND_MONEY,
                    description="Sell items worth at least 50g to Sarah",
                    target="Sarah",
                    required_amount=50
                ),
                QuestObjective(
                    id="buy_something",
                    type=ObjectiveType.SPEND_MONEY,
                    description="Buy something from Sarah's shop",
                    target="Sarah",
                    required_amount=25
                )
            ],
            rewards=QuestReward(
                xp=100,
                money=100,
                items={"bread": 3, "cheese": 2},
                unlock_features=["shop_discounts"]
            ),
            giver_npc="Sarah",
            prerequisites=["social_starter"]
        )
        
        # NPC Quest 3: The Wise Elder
        self.available_quests["elder_wisdom"] = Quest(
            id="elder_wisdom",
            title="Ancient Wisdom",
            description="Elder Tom has stories and wisdom to share about the village.",
            type=QuestType.SIDE,
            objectives=[
                QuestObjective(
                    id="listen_to_tom",
                    type=ObjectiveType.TALK_TO_NPC,
                    description="Listen to Elder Tom's stories about the village",
                    target="Tom",
                    required_amount=1
                ),
                QuestObjective(
                    id="collect_herbs_for_tom",
                    type=ObjectiveType.COLLECT_ITEMS,
                    description="Collect 5 herbs for Tom's remedy",
                    target="herbs",
                    required_amount=5
                ),
                QuestObjective(
                    id="return_herbs",
                    type=ObjectiveType.TALK_TO_NPC,
                    description="Bring the herbs back to Elder Tom",
                    target="Tom",
                    required_amount=1
                )
            ],
            rewards=QuestReward(
                xp=175,
                money=200,
                items={"mushrooms": 5, "wild_berries": 10},
                unlock_features=["elder_recipes"]
            ),
            giver_npc="Tom",
            prerequisites=["friendly_farmer", "shopkeeper_introduction"]
        )
        
        # NPC Quest 4: The Wealthy Family
        self.available_quests["meet_wealthy_family"] = Quest(
            id="meet_wealthy_family",
            title="High Society",
            description="Meet the wealthy family that lives in the mansion. They might have connections and opportunities.",
            type=QuestType.SIDE,
            objectives=[
                QuestObjective(
                    id="talk_to_steve",
                    type=ObjectiveType.TALK_TO_NPC,
                    description="Talk to Steve, the successful businessman",
                    target="Steve",
                    required_amount=1
                ),
                QuestObjective(
                    id="talk_to_kailey",
                    type=ObjectiveType.TALK_TO_NPC,
                    description="Talk to Kailey, the bright 11-year-old",
                    target="Kailey",
                    required_amount=1
                ),
                QuestObjective(
                    id="talk_to_louie",
                    type=ObjectiveType.TALK_TO_NPC,
                    description="Talk to Louie, the energetic 5-year-old",
                    target="Louie",
                    required_amount=1
                )
            ],
            rewards=QuestReward(
                xp=200,
                money=500,
                items={"gold_ingot": 1, "luxury_food": 3},
                unlock_features=["wealthy_connections"]
            ),
            prerequisites=["social_starter"]
        )
        
        # NPC Quest 5: Steve's Business Proposal
        self.available_quests["business_opportunity"] = Quest(
            id="business_opportunity",
            title="Investment Opportunity",
            description="Steve has a business proposition that could be very profitable.",
            type=QuestType.SIDE,
            objectives=[
                QuestObjective(
                    id="talk_business_with_steve",
                    type=ObjectiveType.TALK_TO_NPC,
                    description="Discuss business opportunities with Steve",
                    target="Steve",
                    required_amount=1
                ),
                QuestObjective(
                    id="gather_investment_materials",
                    type=ObjectiveType.COLLECT_ITEMS,
                    description="Gather 50 wood and 25 stone for the investment",
                    target="wood",
                    required_amount=50
                ),
                QuestObjective(
                    id="gather_investment_stone",
                    type=ObjectiveType.COLLECT_ITEMS,
                    description="Gather stone for the investment",
                    target="stone",
                    required_amount=25
                )
            ],
            rewards=QuestReward(
                xp=300,
                money=1000,
                items={"diamond": 2, "gold_ingot": 5},
                unlock_features=["business_partnership"]
            ),
            giver_npc="Steve",
            prerequisites=["meet_wealthy_family"]
        )
        
        # Daily Quest Example
        self.available_quests["daily_gathering"] = Quest(
            id="daily_gathering",
            title="Daily Gathering",
            description="Help the village by gathering resources each day.",
            type=QuestType.DAILY,
            objectives=[
                QuestObjective(
                    id="daily_wood",
                    type=ObjectiveType.COLLECT_ITEMS,
                    description="Collect 10 wood",
                    target="wood",
                    required_amount=10
                ),
                QuestObjective(
                    id="daily_stone",
                    type=ObjectiveType.COLLECT_ITEMS,
                    description="Collect 5 stone",
                    target="stone",
                    required_amount=5
                )
            ],
            rewards=QuestReward(
                xp=50,
                money=75,
                items={"bread": 1}
            ),
            repeatable=True,
            time_limit=86400,  # 24 hours
            prerequisites=["tutorial_gathering"]
        )
    
    def _auto_start_quests(self):
        """Auto-start quests that should begin immediately"""
        for quest in self.available_quests.values():
            if quest.auto_start and quest.can_start(self.completed_quests):
                self.start_quest(quest.id)
    
    def start_quest(self, quest_id: str) -> bool:
        """Start a quest if available and prerequisites are met"""
        if quest_id not in self.available_quests:
            return False
        
        quest = self.available_quests[quest_id]
        
        if not quest.can_start(self.completed_quests):
            return False
        
        if quest_id in self.active_quests:
            return False  # Already active
        
        quest.status = QuestStatus.ACTIVE
        quest.start_time = time.time()
        self.active_quests[quest_id] = quest
        
        self.add_notification(f"📋 New quest: {quest.title}")
        
        return True
    
    def complete_quest(self, quest_id: str) -> bool:
        """Complete a quest and give rewards"""
        if quest_id not in self.active_quests:
            return False
        
        quest = self.active_quests[quest_id]
        
        if not quest.is_complete():
            return False
        
        quest.status = QuestStatus.COMPLETED
        self.completed_quests.append(quest_id)
        
        # Give rewards
        self._give_rewards(quest.rewards)
        
        # Remove from active quests
        del self.active_quests[quest_id]
        
        self.add_notification(f"✅ Quest completed: {quest.title}")
        
        # Trigger special events based on quest completion
        if quest_id == "tutorial_movement":
            # First quest completed - Steve should approach player
            self.trigger_steve_approach = True
        
        # Check for new available quests
        self._check_new_available_quests()
        
        return True
    
    def update_objective(self, objective_type: ObjectiveType, target: str, amount: int = 1):
        """Update quest objectives based on player actions"""
        # Create a list copy to avoid dictionary size change during iteration
        active_quest_list = list(self.active_quests.values())
        for quest in active_quest_list:
            for objective in quest.objectives:
                if (objective.type == objective_type and 
                    (objective.target == target or objective.target == "any_location" or 
                     objective.target == "any_npc" or objective.target == "any_skill" or
                     objective.target == "any_seed")):
                    
                    if not objective.completed:
                        objective.progress(amount)
                        
                        if objective.completed:
                            self.add_notification(f"✓ {objective.description}")
                            
                            # Check if quest is complete
                            if quest.is_complete():
                                self.complete_quest(quest.id)
    
    def _give_rewards(self, rewards: QuestReward):
        """Give quest rewards to the player"""
        # Award XP
        if rewards.xp > 0 and 'xp_system' in self.game_systems:
            xp_system = self.game_systems['xp_system']
            # Use the correct XP method
            if hasattr(xp_system, 'add_xp'):
                from src.systems.xp_system import XPCategory
                xp_system.add_xp(rewards.xp, XPCategory.GATHERING, "Quest completed")
            elif hasattr(xp_system, 'gain_xp'):
                xp_system.gain_xp(rewards.xp)
        
        # Give money
        if rewards.money > 0 and 'inventory_system' in self.game_systems:
            inventory = self.game_systems['inventory_system']
            inventory.add_money(rewards.money)
        
        # Give items
        if rewards.items and 'inventory_system' in self.game_systems:
            inventory = self.game_systems['inventory_system']
            for item_id, quantity in rewards.items.items():
                inventory.add_item(item_id, quantity)
        
        # Unlock features
        for feature in rewards.unlock_features:
            if feature not in self.unlocked_features:
                self.unlocked_features.append(feature)
                self.add_notification(f"🔓 Unlocked: {feature.replace('_', ' ').title()}")
    
    def _check_new_available_quests(self):
        """Check if any new quests can be started"""
        for quest_id, quest in self.available_quests.items():
            if (quest_id not in self.active_quests and 
                quest_id not in self.completed_quests and
                quest.can_start(self.completed_quests)):
                
                if quest.giver_npc:
                    self.add_notification(f"💬 {quest.giver_npc} has a quest for you!")
                else:
                    self.add_notification(f"📋 New quest available: {quest.title}")
    
    def add_notification(self, message: str):
        """Add a quest notification"""
        self.notification_queue.append(message)
        self.last_notification_time = time.time()
    
    def get_active_quests(self) -> List[Quest]:
        """Get all active quests"""
        return list(self.active_quests.values())
    
    def get_available_quests_for_npc(self, npc_name: str) -> List[Quest]:
        """Get quests available from a specific NPC"""
        return [quest for quest in self.available_quests.values() 
                if (quest.giver_npc == npc_name and 
                    quest.can_start(self.completed_quests) and
                    quest.id not in self.active_quests and
                    quest.id not in self.completed_quests)]
    
    def is_feature_unlocked(self, feature: str) -> bool:
        """Check if a feature is unlocked"""
        return feature in self.unlocked_features
    
    def get_quest_progress_summary(self) -> str:
        """Get a summary of quest progress"""
        active = len(self.active_quests)
        completed = len(self.completed_quests)
        total = len(self.available_quests)
        
        return f"Active: {active} | Completed: {completed} | Total: {total}"
    
    def save_progress(self) -> Dict:
        """Save quest progress to dictionary"""
        return {
            "active_quests": {qid: asdict(quest) for qid, quest in self.active_quests.items()},
            "completed_quests": self.completed_quests,
            "failed_quests": self.failed_quests,
            "unlocked_features": self.unlocked_features
        }
    
    def load_progress(self, data: Dict):
        """Load quest progress from dictionary"""
        # This would need to reconstruct Quest objects from the saved data
        # Implementation details depend on save/load system
        pass