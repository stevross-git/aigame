import pygame
import sys
import math
import random
import time
from typing import List, Tuple
from src.core.camera import Camera
from src.world.beautiful_map import BeautifulMap
from src.world.events import EventGenerator
from src.entities.enhanced_player import EnhancedPlayer
from src.entities.npc import NPC
from src.entities.enhanced_npc import EnhancedNPC
import src.core.constants as constants
from src.ai.memory_manager import MemoryManager
from src.ui.menu import MainMenu, PauseMenu
from src.ui.modern_hud import ModernHUD
from src.ui.character_creator import CharacterCreator
from src.ui.settings import SettingsMenu
from src.ui.api_key_manager import APIKeyManager
from src.ui.ai_response_box import AIResponseBox
from src.ui.cost_monitor import CostMonitor
from src.ui.interaction_menu import InteractionMenu
from src.ui.speed_controller import GameSpeedController
from src.ui.data_analysis_panel import DataAnalysisPanel
from src.ui.loading_screen import LoadingScreen
from src.ui.character_loading_screen import CharacterLoadingScreen
from src.ui.game_clock import GameClock
from src.ui.npc_chat_interface import NPCChatInterface
from src.ui.help_system import HelpSystem
from src.ui.welcome_message import WelcomeMessage
from src.ui.notification_system import NotificationSystem
from src.ui.skills_inventory_ui import SkillsInventoryUI
from src.ui.detailed_inventory_ui import DetailedInventoryUI
from src.ui.resource_collection_ui import ResourceCollectionUI
from src.ui.resource_tracker_ui import ResourceTrackerUI
from src.systems.skill_system import SkillSystem
from src.systems.inventory_system import InventorySystem
from src.systems.crafting_system import CraftingSystem
from src.systems.resource_system import ResourceSystem
from src.core.time_system import GameTime
from src.core.save_system import SaveSystem
from src.world.house_interior import HouseInterior
from src.world.npc_house_manager import NPCHouseManager
from src.systems.xp_system import XPSystem, XPCategory
from src.ui.xp_display_ui import XPDisplayUI
from src.systems.player_movement_system import PlayerMovementSystem
from src.ui.drag_drop_inventory import DragDropInventory
from src.systems.resource_interaction_manager import ResourceInteractionManager
from src.systems.exploration_tracker import ExplorationTracker
from src.ui.unified_hud import UnifiedHUD
from src.systems.quest_system import QuestSystem, ObjectiveType
from src.ui.quest_ui import QuestUI
from src.ui.world_customizer import WorldCustomizer
from src.ui.cache_stats_display import CacheStatsDisplay
from src.ui.shortcut_keys_ui import ShortcutKeysUI
from src.ui.draggable_hud_manager import DraggableHUDManager
from src.ui.action_bar import ActionBar
from src.world.shop_system import ShopSystem
from src.world.shop_interior import ShopInterior

class Game:
    def __init__(self):
        pygame.init()
        
        # Load resolution from settings
        from src.ui.settings import Settings
        settings = Settings()
        resolution = settings.get("screen_resolution", "1600x900")
        width, height = map(int, resolution.split('x'))
        
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("AI Sims - Life Simulation")
        self.clock = pygame.time.Clock()
        self.running = True
        
        self.game_state = "loading"  # loading, menu, character_creation, character_loading, settings, api_keys, playing, paused, in_house
        self.game_time = 0.0
        self.auto_save_timer = 0.0
        self.character_data = None
        self.time_multiplier = 1.0
        
        # House system
        self.house_interior = None
        self.npc_house_manager = None
        self.player_outdoor_pos = None  # Store player position when entering house
        
        # Initialize time system
        self.time_system = GameTime()
        self.game_clock = None  # Will be created after loading
        
        # Initialize loading screens
        self.loading_screen = LoadingScreen(self.screen)
        self.character_loading_screen = None  # Will be created when needed
        
        # Asset loading progress tracking
        self.assets_loaded = False
        self.loading_progress = 0.0
        self.character_loading_progress = 0.0
        
        # AI system control
        self.ai_systems_active = False
        
        # Initialize core systems (will be loaded progressively)
        self.camera = None
        self.map = None
        self.event_generator = None
        self.memory_manager = None
        self.save_system = None
        
        self.player = None
        self.npcs: List[NPC] = []
        
        # UI Components (will be initialized after loading)
        self.main_menu = None
        self.pause_menu = None
        self.character_creator = None
        self.settings_menu = None
        self.api_key_manager = None
        self.ai_response_box = None
        self.cost_monitor = None
        self.interaction_menu = None
        self.speed_controller = None
        self.data_analysis_panel = None
        self.hud = None
        self.npc_chat_interface = None
        self.detailed_inventory_ui = None
        self.resource_collection_ui = None
        self.resource_tracker_ui = None
        self.xp_display_ui = None
        self.drag_drop_inventory = None
        self.action_bar = None
        self.shop_system = None
        self.shop_interior = None
        self.player_movement_system = None
        self.resource_interaction_manager = None
        self.exploration_tracker = None
        self.quest_system = None
        self.quest_ui = None
        self.cache_stats_display = CacheStatsDisplay(self.screen, 10, constants.SCREEN_HEIGHT - 180)
        
        # Interaction pause flags
        self.time_paused = False
        self.ai_paused = False
        
        # Menu callbacks will be set after UI components are loaded
        
        self.all_sprites = pygame.sprite.Group()
    
    def _load_game_assets(self, dt):
        """Progressively load game assets with loading screen"""
        if self.assets_loaded:
            return
        
        # Stage 1: Initialize core systems (0-20%)
        if self.loading_progress < 0.2:
            if self.camera is None:
                self.loading_screen.set_progress(0.05, "Initializing camera system...")
                # Get current screen dimensions from settings
                from src.ui.settings import Settings
                settings = Settings()
                resolution = settings.get("screen_resolution", "1600x900")
                width, height = map(int, resolution.split('x'))
                self.camera = Camera(width, height)
            
            if self.memory_manager is None:
                self.loading_screen.set_progress(0.10, "Setting up memory manager...")
                self.memory_manager = MemoryManager()
            
            if self.save_system is None:
                self.loading_screen.set_progress(0.15, "Loading save system...")
                self.save_system = SaveSystem()
            
            if self.house_interior is None:
                self.loading_screen.set_progress(0.18, "Setting up player house...")
                self.house_interior = HouseInterior()
                self.npc_house_manager = NPCHouseManager()
            
            if self.quest_system is None:
                self.loading_screen.set_progress(0.19, "Initializing quest system...")
                self.quest_system = QuestSystem()
            
            self.loading_progress = 0.2
        
        # Stage 2: Load map and assets (20-60%)
        elif self.loading_progress < 0.6:
            if self.map is None:
                self.loading_screen.set_progress(0.25, "Generating beautiful world...")
                # Use custom world settings if available
                world_settings = getattr(self, 'custom_world_settings', {}).get('world', {})
                self.map = BeautifulMap(constants.MAP_WIDTH, constants.MAP_HEIGHT, world_settings)
                self.loading_screen.set_progress(0.50, "Loading character sprites...")
                self.loading_screen.set_progress(0.55, "Creating UI assets...")
            
            if self.event_generator is None:
                self.loading_screen.set_progress(0.58, "Initializing event system...")
                self.event_generator = EventGenerator()
            
            self.loading_progress = 0.6
        
        # Stage 3: Initialize UI components (60-90%)
        elif self.loading_progress < 0.9:
            if self.main_menu is None:
                self.loading_screen.set_progress(0.65, "Creating menu system...")
                self.main_menu = MainMenu(self.screen)
                self.pause_menu = PauseMenu(self.screen)
                self.character_creator = CharacterCreator(self.screen)
                self.settings_menu = SettingsMenu(self.screen)
            
            if self.api_key_manager is None:
                self.loading_screen.set_progress(0.75, "Setting up AI systems...")
                self.api_key_manager = APIKeyManager(self.screen)
                self.ai_response_box = AIResponseBox(self.screen)
                self.cost_monitor = CostMonitor(self.screen)
            
            if self.interaction_menu is None:
                self.loading_screen.set_progress(0.85, "Creating interaction systems...")
                self.interaction_menu = InteractionMenu(self.screen)
                
                # Set pause/resume callbacks for interaction menu
                self.interaction_menu.on_pause_game = self._pause_for_interaction
                self.interaction_menu.on_resume_game = self._resume_from_interaction
                self.speed_controller = GameSpeedController(self.screen)
                self.data_analysis_panel = DataAnalysisPanel(self.screen)
                self.hud = ModernHUD(self.screen)
                self.game_clock = GameClock(self.screen)
                self.npc_chat_interface = NPCChatInterface(self.screen, getattr(self, 'quest_system', None))
                self.help_system = HelpSystem(self.screen)
                self.welcome_message = WelcomeMessage(self.screen)
                self.notification_system = NotificationSystem(self.screen)
                self.shortcut_keys_ui = ShortcutKeysUI(self.screen)
                
                # Initialize draggable HUD manager
                self.hud_manager = DraggableHUDManager(self.screen)
                
                # Initialize game systems with error handling
                self.loading_screen.set_progress(0.9, "Initializing game systems...")
                
                try:
                    self.xp_system = XPSystem()
                except Exception as e:
                    print(f"Error initializing XP system: {e}")
                    self.xp_system = None
                
                try:
                    self.skill_system = SkillSystem()
                except Exception as e:
                    print(f"Error initializing skill system: {e}")
                    self.skill_system = SkillSystem()  # Fallback
                
                try:
                    self.inventory_system = InventorySystem()
                except Exception as e:
                    print(f"Error initializing inventory system: {e}")
                    self.inventory_system = InventorySystem()  # Fallback
                
                try:
                    self.crafting_system = CraftingSystem(self.inventory_system, self.skill_system, self.xp_system)
                except Exception as e:
                    print(f"Error initializing crafting system: {e}")
                    self.crafting_system = CraftingSystem(self.inventory_system, self.skill_system)  # Fallback without XP
                
                try:
                    self.resource_system = ResourceSystem(self.inventory_system, self.skill_system)
                except Exception as e:
                    print(f"Error initializing resource system: {e}")
                    self.resource_system = ResourceSystem(self.inventory_system, self.skill_system)  # Fallback
                
                try:
                    self.skills_inventory_ui = SkillsInventoryUI(self.screen, self.skill_system, self.inventory_system, self.crafting_system)
                except Exception as e:
                    print(f"Error initializing skills inventory UI: {e}")
                    self.skills_inventory_ui = None
                
                # Initialize enhanced UIs with error handling
                try:
                    self.detailed_inventory_ui = DetailedInventoryUI(self.screen, self.inventory_system)
                except Exception as e:
                    print(f"Error initializing detailed inventory UI: {e}")
                    self.detailed_inventory_ui = None
                
                try:
                    self.resource_collection_ui = ResourceCollectionUI(self.screen, self.inventory_system, self.resource_system, self.skill_system)
                except Exception as e:
                    print(f"Error initializing resource collection UI: {e}")
                    self.resource_collection_ui = None
                
                try:
                    self.resource_tracker_ui = ResourceTrackerUI(self.screen, self.inventory_system, self.resource_system, self.skill_system)
                except Exception as e:
                    print(f"Error initializing resource tracker UI: {e}")
                    self.resource_tracker_ui = None
                
                try:
                    if self.xp_system:
                        self.xp_display_ui = XPDisplayUI(self.screen, self.xp_system)
                    else:
                        self.xp_display_ui = None
                except Exception as e:
                    print(f"Error initializing XP display UI: {e}")
                    self.xp_display_ui = None
                
                # Initialize action bar first
                try:
                    self.action_bar = ActionBar(self.screen, self.inventory_system)
                except Exception as e:
                    print(f"Error initializing action bar: {e}")
                    self.action_bar = None
                
                try:
                    self.drag_drop_inventory = DragDropInventory(self.screen, self.inventory_system, self.action_bar)
                except Exception as e:
                    print(f"Error initializing drag drop inventory: {e}")
                    self.drag_drop_inventory = None
                
                # Initialize shop systems
                try:
                    self.shop_system = ShopSystem()
                    self.shop_interior = ShopInterior(self.screen, self.inventory_system, self.shop_system)
                except Exception as e:
                    print(f"Error initializing shop systems: {e}")
                    self.shop_system = None
                    self.shop_interior = None
                
                # Initialize quest UI
                try:
                    if self.quest_system:
                        # Connect quest system to game systems
                        self.quest_system.game_systems = {
                            'xp_system': self.xp_system,
                            'inventory_system': self.inventory_system,
                            'skill_system': self.skill_system,
                            'resource_system': self.resource_system
                        }
                        self.quest_ui = QuestUI(self.screen, self.quest_system)
                        
                        # Connect XP system to quest system for objective tracking
                        if hasattr(self, 'xp_system') and self.xp_system:
                            self.xp_system.quest_system = self.quest_system
                        
                        # Connect NPC chat interface to quest system
                        if hasattr(self, 'npc_chat_interface') and self.npc_chat_interface:
                            self.npc_chat_interface.quest_system = self.quest_system
                        
                        # Connect inventory system to quest system
                        if hasattr(self, 'inventory_system') and self.inventory_system:
                            self.inventory_system.quest_system = self.quest_system
                    else:
                        self.quest_ui = None
                except Exception as e:
                    print(f"Error initializing quest UI: {e}")
                    self.quest_ui = None
                
                # Add trees from map positions to resource system
                if hasattr(self.map, 'tree_positions'):
                    self.resource_system.add_trees_from_map(self.map.tree_positions)
                
                # Give player starting items
                self.resource_system.add_starting_items()
            
            self.loading_progress = 0.9
        
        # Stage 4: Setup callbacks and finalize (90-100%)
        else:
            if not hasattr(self, '_callbacks_set'):
                self.loading_screen.set_progress(0.95, "Setting up game callbacks...")
                self._setup_ui_callbacks()
                self._callbacks_set = True
            
            self.loading_screen.set_progress(1.0, "Ready to play!")
            
            # Wait a moment to show 100% before transitioning
            if not hasattr(self, '_completion_timer'):
                self._completion_timer = 0.0
            
            self._completion_timer += dt
            if self._completion_timer >= 1.0:  # Wait 1 second at 100%
                self.assets_loaded = True
                self.game_state = "menu"
                self.player = EnhancedPlayer(400, 300)
                
                # Initialize systems that need player with error handling
                try:
                    self.player_movement_system = PlayerMovementSystem(self.player, self.inventory_system, self.resource_system, self.skill_system)
                except Exception as e:
                    print(f"Error initializing player movement system: {e}")
                    self.player_movement_system = None
                
                try:
                    self.resource_interaction_manager = ResourceInteractionManager(self.resource_system, self.inventory_system, self.skill_system, self.xp_system, self.quest_system, self.action_bar)
                except Exception as e:
                    print(f"Error initializing resource interaction manager: {e}")
                    self.resource_interaction_manager = None
                
                try:
                    if self.xp_system:
                        self.exploration_tracker = ExplorationTracker(self.xp_system)
                    else:
                        self.exploration_tracker = None
                except Exception as e:
                    print(f"Error initializing exploration tracker: {e}")
                    self.exploration_tracker = None
                
                # Initialize unified HUD
                try:
                    self.unified_hud = UnifiedHUD(self.screen)
                    self.unified_hud.set_data_sources(
                        player=self.player,
                        xp_system=self.xp_system,
                        time_system=self.time_system,
                        skill_system=self.skill_system,
                        inventory_system=self.inventory_system
                    )
                except Exception as e:
                    print(f"Error initializing unified HUD: {e}")
                    self.unified_hud = None
                
                # Register HUD components as draggable (after all components are created)
                self._register_hud_components()
                
                # Initial position update
                self._update_hud_positions()
    
    def _setup_ui_callbacks(self):
        """Setup all UI component callbacks after they're loaded"""
        # Menu callbacks
        self.main_menu.on_new_game = self._show_character_creator
        self.main_menu.on_load_game = self._load_game
        self.main_menu.on_settings = self._show_settings
        self.main_menu.on_exit = self._quit_game
        
        self.pause_menu.on_resume = self._resume_game
        self.pause_menu.on_save = self._save_game
        self.pause_menu.on_main_menu = self._return_to_menu
        
        self.character_creator.on_character_created = self._character_created
        self.character_creator.on_back = self._return_to_menu
        self.character_creator.on_advanced_settings = self._show_world_customizer
        
        self.settings_menu.on_back = self._return_to_menu
        self.settings_menu.on_apply = self._apply_settings
        self.settings_menu.on_manage_api_keys = self._show_api_keys
        
        self.api_key_manager.on_back = self._return_to_settings
        self.api_key_manager.on_keys_saved = self._api_keys_saved
        
        # Interaction menu callbacks
        self.interaction_menu.set_callback('on_greet', self._handle_greet_interaction)
        self.interaction_menu.set_callback('on_chat', self._handle_chat_interaction)
        self.interaction_menu.set_callback('on_give_gift', self._handle_gift_interaction)
        self.interaction_menu.set_callback('on_invite_activity', self._handle_activity_interaction)
        self.interaction_menu.set_callback('on_ask_about', self._handle_ask_interaction)
        self.interaction_menu.set_callback('on_custom_dialogue', self._handle_custom_dialogue)
        self.interaction_menu.set_callback('on_open_chat', self._handle_open_chat_interaction)
        
        # Speed controller callbacks
        self.speed_controller.on_speed_change = self._handle_speed_change
        self.speed_controller.on_pause_toggle = self._handle_pause_toggle
    
    def _spawn_npcs(self):
        # Use custom NPCs if available, otherwise use defaults
        if hasattr(self, 'custom_world_settings') and 'custom_npcs' in self.custom_world_settings:
            custom_npcs = self.custom_world_settings['custom_npcs']
            print(f"Using {len(custom_npcs)} custom NPCs")
            npc_data = self._convert_custom_npcs_to_game_format(custom_npcs)
        else:
            # Default NPCs
            npc_data = [
            {
                "name": "Alice", 
                "x": 200, 
                "y": 200, 
                "personality": {
                    "friendliness": 0.8, 
                    "energy": 0.6,
                    "empathy": 0.7,
                    "creativity": 0.5
                }
            },
            {
                "name": "Bob", 
                "x": 600, 
                "y": 400, 
                "personality": {
                    "friendliness": 0.5, 
                    "energy": 0.3,
                    "organization": 0.8,
                    "patience": 0.9
                }
            },
            {
                "name": "Charlie", 
                "x": 300, 
                "y": 500, 
                "personality": {
                    "friendliness": 0.7, 
                    "energy": 0.9,
                    "humor": 0.8,
                    "curiosity": 0.7
                }
            },
            {
                "name": "Diana",
                "x": 500,
                "y": 300,
                "personality": {
                    "friendliness": 0.6,
                    "creativity": 0.9,
                    "ambition": 0.8,
                    "confidence": 0.7
                }
            },
            {
                "name": "Steve",
                "x": 1800,
                "y": 400,
                "personality": {
                    "friendliness": 0.7,
                    "ambition": 0.9,
                    "confidence": 0.8,
                    "organization": 0.8,
                    "wealth": 1.0,
                    "responsibility": 0.9
                }
            },
            {
                "name": "Kailey",
                "x": 1820,
                "y": 420,
                "personality": {
                    "friendliness": 0.8,
                    "energy": 0.9,
                    "curiosity": 0.9,
                    "creativity": 0.8,
                    "innocence": 0.9,
                    "playfulness": 0.8
                }
            },
            {
                "name": "Louie",
                "x": 1780,
                "y": 380,
                "personality": {
                    "friendliness": 0.9,
                    "energy": 1.0,
                    "curiosity": 1.0,
                    "playfulness": 1.0,
                    "innocence": 1.0,
                    "mischief": 0.7
                }
            }
        ]
        
        for data in npc_data:
            # Use Enhanced NPCs for better AI capabilities
            # Skip AI initialization until welcome screen is dismissed
            npc = EnhancedNPC(data["x"], data["y"], data["name"], data["personality"], self.memory_manager, skip_ai_init=True)
            npc.ai_response_box = self.ai_response_box  # Pass response box reference
            npc.chat_interface = self.npc_chat_interface  # Pass chat interface reference
            npc.house_manager = self.npc_house_manager  # Pass house manager reference
            self.npcs.append(npc)
            
            # Assign a house to each NPC
            if self.npc_house_manager:
                success = self.npc_house_manager.assign_house_to_npc(npc.name)
                if success:
                    print(f"Assigned house to {npc.name}")
                else:
                    print(f"No available house for {npc.name}")
        
        # Debug: Show house assignments
        if self.npc_house_manager:
            self.npc_house_manager.debug_house_assignments()
    
    def _convert_custom_npcs_to_game_format(self, custom_npcs):
        """Convert custom NPCs from world customizer to game format"""
        npc_data = []
        
        # Base positions spread around the map
        base_positions = [
            (200, 200), (600, 400), (300, 500), (500, 300), (800, 200),
            (1000, 600), (400, 800), (1200, 300), (700, 700), (900, 500),
            (1400, 400), (600, 900), (1100, 800), (300, 1000), (1500, 600),
            (200, 1200), (800, 1100), (1300, 900), (500, 1300), (1000, 1200)
        ]
        
        for i, custom_npc in enumerate(custom_npcs):
            # Use base positions or generate random ones if more NPCs than positions
            if i < len(base_positions):
                x, y = base_positions[i]
            else:
                x = random.randint(200, self.map.width - 200)
                y = random.randint(200, self.map.height - 200)
            
            npc_data.append({
                "name": custom_npc["name"],
                "x": x,
                "y": y,
                "personality": custom_npc["personality"]
            })
        
        return npc_data
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            # Skip input handling during loading states
            if self.game_state in ["loading", "character_loading"]:
                continue
            
            if self.game_state == "menu":
                self.main_menu.handle_event(event)
            elif self.game_state == "character_creation":
                self.character_creator.handle_event(event)
            elif self.game_state == "world_customization":
                if hasattr(self, 'world_customizer'):
                    self.world_customizer.handle_event(event)
            elif self.game_state == "settings":
                self.settings_menu.handle_event(event)
            elif self.game_state == "api_keys":
                self.api_key_manager.handle_event(event)
            elif self.game_state == "paused":
                self.pause_menu.handle_event(event)
            elif self.game_state == "in_house":
                self._handle_house_events(event)
            elif self.game_state == "playing":
                # Check chat interface first - if it's open, it gets priority over all other input
                if self.npc_chat_interface and self.npc_chat_interface.handle_event(event):
                    return  # Chat interface handled the event, don't process any other input
                
                # Check interaction menu next
                if self.interaction_menu.handle_event(event):
                    return  # Interaction menu handled the event
                
                # Check HUD manager first (for edit mode)
                if hasattr(self, 'hud_manager') and self.hud_manager.handle_event(event):
                    return
                
                # Check shortcut keys UI
                if hasattr(self, 'shortcut_keys_ui') and self.shortcut_keys_ui.handle_event(event):
                    return
                
                # Check enhanced UIs
                if hasattr(self, 'detailed_inventory_ui') and self.detailed_inventory_ui.handle_event(event):
                    return
                if hasattr(self, 'resource_collection_ui') and self.resource_collection_ui.handle_event(event):
                    return
                if hasattr(self, 'resource_tracker_ui') and self.resource_tracker_ui and self.resource_tracker_ui.handle_event(event):
                    return
                if hasattr(self, 'xp_display_ui') and self.xp_display_ui and self.xp_display_ui.handle_event(event):
                    return
                if hasattr(self, 'shop_interior') and self.shop_interior and self.shop_interior.handle_event(event):
                    return
                if hasattr(self, 'action_bar') and self.action_bar and self.action_bar.handle_event(event):
                    return
                if hasattr(self, 'drag_drop_inventory') and self.drag_drop_inventory and self.drag_drop_inventory.handle_event(event):
                    return
                if hasattr(self, 'unified_hud') and self.unified_hud and self.unified_hud.handle_event(event):
                    return
                if hasattr(self, 'quest_ui') and self.quest_ui and self.quest_ui.handle_event(event):
                    return
                
                # Handle cache stats display events
                if hasattr(self, 'cache_stats_display') and self.cache_stats_display.handle_event(event):
                    return
                
                # Handle mouse clicks for resource interaction
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Left click - harvest
                        self._handle_resource_click(event, action="harvest")
                    elif event.button == 3:  # Right click - stats
                        self._handle_resource_click(event, action="stats")
                
                # Only process shortcut keys if chat interface and interaction menu are not handling input
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self._pause_game()
                    elif event.key == pygame.K_F5:
                        self._save_game()
                    elif event.key == pygame.K_F1:
                        # Toggle help system
                        self.help_system.toggle()
                    elif event.key == pygame.K_F2:
                        # Toggle AI response box
                        self.ai_response_box.collapsed = not self.ai_response_box.collapsed
                    elif event.key == pygame.K_F3:
                        # Toggle cost monitor
                        self.cost_monitor.collapsed = not self.cost_monitor.collapsed
                    elif event.key == pygame.K_F4:
                        # Reset session costs
                        self.cost_monitor.reset_session()
                    elif event.key == pygame.K_e:
                        # Open interaction menu if near NPC
                        self._try_open_interaction_menu()
                    elif event.key == pygame.K_F6:
                        # Toggle speed controller
                        self.speed_controller.collapsed = not self.speed_controller.collapsed
                    elif event.key == pygame.K_F7:
                        # Toggle data analysis panel
                        if self.data_analysis_panel.visible:
                            self.data_analysis_panel.hide()
                        else:
                            self.data_analysis_panel.show()
                    elif event.key == pygame.K_F8:
                        # Clear AI responses
                        self.ai_response_box.clear_responses()
                    elif event.key == pygame.K_i or event.key == pygame.K_TAB:
                        # Toggle inventory (I or Tab key)
                        keys = pygame.key.get_pressed()
                        
                        # Update quest objective for ANY inventory opened
                        if hasattr(self, 'quest_system') and self.quest_system:
                            self.quest_system.update_objective(ObjectiveType.OPEN_INVENTORY, "inventory")
                        
                        # I key: Toggle between inventories based on Shift
                        if event.key == pygame.K_i:
                            if keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]:
                                # Shift+I: Skills/quick inventory
                                self.skills_inventory_ui.toggle("inventory")
                            else:
                                # Just I: Detailed inventory
                                if hasattr(self, 'detailed_inventory_ui'):
                                    self.detailed_inventory_ui.toggle()
                        
                        # Tab key: Always open detailed inventory (most common)
                        elif event.key == pygame.K_TAB:
                            if hasattr(self, 'detailed_inventory_ui'):
                                self.detailed_inventory_ui.toggle()
                    elif event.key == pygame.K_k:
                        # Toggle skills
                        self.skills_inventory_ui.toggle("skills")
                    elif event.key == pygame.K_j:
                        # Toggle crafting
                        self.skills_inventory_ui.toggle("crafting")
                    elif event.key == pygame.K_r:
                        # Toggle resource tracker (Shift+R for harvest)
                        keys = pygame.key.get_pressed()
                        if keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]:
                            self._try_harvest_resource()
                        else:
                            if hasattr(self, 'resource_tracker_ui'):
                                self.resource_tracker_ui.toggle()
                    elif event.key == pygame.K_SPACE:
                        # Only interact with resources if there's actually one nearby
                        # Otherwise let the event fall through to speed controller for pause
                        if self._has_nearby_resource():
                            self._try_interact_with_resource()
                        else:
                            # Let speed controller handle pause functionality
                            continue
                    elif event.key == pygame.K_c:
                        # Open chat with nearby NPC
                        self._try_open_chat()
                    elif event.key == pygame.K_t:
                        # Alternative key to open chat
                        self._try_open_chat()
                    elif event.key == pygame.K_m:
                        # Toggle mini-map
                        if hasattr(self, 'resource_tracker_ui') and self.resource_tracker_ui:
                            self.resource_tracker_ui.toggle_mini_map()
                    elif event.key == pygame.K_h:
                        # Go to house
                        self._try_enter_house()
                    elif event.key == pygame.K_e:
                        # Enter shop or interact with building
                        self._try_enter_shop()
                
                # Handle other UI components in order of priority
                # Welcome message gets highest priority when visible
                welcome_handled = self.welcome_message.handle_event(event)
                if welcome_handled:
                    # Check if welcome message was just closed
                    if not self.welcome_message.visible and not self.ai_systems_active:
                        self._activate_ai_systems()
                    return
                
                if not self.welcome_message.visible:
                    # Skills/Inventory UI gets high priority
                    if not self.skills_inventory_ui.handle_event(event):
                        # Help system gets high priority
                        if not self.help_system.handle_event(event):
                            if not self.hud.handle_event(event):
                                if not self.ai_response_box.handle_event(event):
                                    if not self.cost_monitor.handle_event(event):
                                        if not self.speed_controller.handle_event(event):
                                            if not self.data_analysis_panel.handle_event(event):
                                                if not (self.game_clock and self.game_clock.handle_event(event)):
                                                    self._handle_npc_selection(event)
    
    def update(self, dt):
        from src.debug.performance_profiler import profiler
        
        if self.game_state == "loading":
            with profiler.time_operation("loading_screen_update"):
                self.loading_screen.update(dt)
            with profiler.time_operation("load_game_assets"):
                self._load_game_assets(dt)
            return
        
        if self.game_state == "character_loading":
            with profiler.time_operation("character_loading_update"):
                self.character_loading_screen.update(dt)
                self._load_character_world(dt)
            return
        
        if self.game_state == "api_keys":
            with profiler.time_operation("api_key_manager_update"):
                self.api_key_manager.update(dt)
            return
        
        if self.game_state not in ["playing", "in_house"]:
            return
        
        # Apply time multiplier to delta time
        adjusted_dt = dt * self.time_multiplier
        
        with profiler.time_operation("game_time_updates"):
            self.game_time += adjusted_dt
            self.auto_save_timer += adjusted_dt
        
        # Update time system (unless paused for interaction)
        if not self.time_paused:
            with profiler.time_operation("time_system_update"):
                self.time_system.update(dt, self.time_multiplier)
        
        # Update game clock
        if self.game_clock:
            with profiler.time_operation("game_clock_update"):
                self.game_clock.update(dt)
        
        # Auto-save every 5 minutes
        if self.auto_save_timer >= 300:
            with profiler.time_operation("auto_save"):
                self._auto_save()
                self.auto_save_timer = 0
        
        with profiler.time_operation("player_update"):
            keys = pygame.key.get_pressed()
            old_pos = (self.player.rect.x, self.player.rect.y)
            self.player.update(adjusted_dt, keys)
            new_pos = (self.player.rect.x, self.player.rect.y)
            
            # Check if player moved for quest objective
            if old_pos != new_pos and hasattr(self, 'quest_system') and self.quest_system:
                # Update movement quest objective
                for quest in self.quest_system.active_quests.values():
                    for objective in quest.objectives:
                        if objective.type.value == "reach_location" and not objective.completed:
                            objective.progress(1)
                            if objective.completed:
                                if hasattr(self, 'notification_system'):
                                    self.notification_system.add_notification(f"✅ {objective.description}")
        
        with profiler.time_operation("event_generator_update"):
            self.event_generator.update(adjusted_dt)
            active_events = self.event_generator.get_active_events()
        
        # Update NPCs every 2nd frame for better performance
        with profiler.time_operation("npc_updates_total"):
            if not hasattr(self, 'npc_update_counter'):
                self.npc_update_counter = 0
            
            self.npc_update_counter += 1
            # Only update NPCs if AI systems are active (after welcome screen)
            if self.ai_systems_active:
                # Check if Steve should approach player after first quest
                if hasattr(self, 'quest_system') and self.quest_system and self.quest_system.trigger_steve_approach:
                    # Find Steve NPC
                    steve = None
                    for npc in self.npcs:
                        if npc.name == "Steve":
                            steve = npc
                            break
                    
                    if steve:
                        # Make Steve walk to player with the second quest
                        steve.walk_to_player(
                            self.player, 
                            "steve_introduction",
                            "Congratulations on completing your first task! I'm Steve, and I have a business proposition for you."
                        )
                        # Start the quest
                        if self.quest_system.start_quest("steve_introduction"):
                            if hasattr(self, 'notification_system'):
                                self.notification_system.add_notification("Steve is approaching you!")
                        self.quest_system.trigger_steve_approach = False  # Reset trigger
                
                # Optimized performance mode - moderate NPC update frequency
                current_fps = self.clock.get_fps()
                if current_fps > 15:  # Only update NPCs if FPS is reasonable
                    if self.npc_update_counter % 5 == 0:  # Update NPCs every 5th frame for balanced performance
                        with profiler.time_operation("individual_npc_updates"):
                            for npc in self.npcs:
                                # Check if NPC is tracking player
                                quest_to_give = npc.update_player_tracking(self.player)
                                if quest_to_give and hasattr(self, 'quest_system'):
                                    # NPC reached player with a quest
                                    if self.quest_system.start_quest(quest_to_give):
                                        if hasattr(self, 'notification_system'):
                                            self.notification_system.add_notification(f"{npc.name} has a quest for you!")
                                
                                # Update NPC (ai_paused is handled internally by NPC)
                                npc.update(adjusted_dt * 2, self.npcs, active_events)
        
        # RESTORE ALL UI SYSTEMS - Essential for gameplay
        self.ai_response_box.update(dt)
        self.cost_monitor.update(dt)
        self.speed_controller.update(dt)
        self.data_analysis_panel.update(dt)
        self.interaction_menu.update(dt)
        
        # Restore shortcut keys UI
        if hasattr(self, 'shortcut_keys_ui'):
            self.shortcut_keys_ui.update(dt)
        
        # Restore HUD manager
        if hasattr(self, 'hud_manager') and self.hud_manager.positions_dirty:
            self._update_hud_positions()
            self.hud_manager.positions_dirty = False
        
        # Restore all secondary UI systems
        self.help_system.update(dt)
        with profiler.time_operation("welcome_message_update"):
            self.welcome_message.update(dt) 
        self.notification_system.update(dt)
        self.skills_inventory_ui.update(dt)
        
        # Restore ALL enhanced UIs and systems
        if hasattr(self, 'detailed_inventory_ui') and self.detailed_inventory_ui:
            self.detailed_inventory_ui.update() if hasattr(self.detailed_inventory_ui, 'update') else None
        if hasattr(self, 'resource_collection_ui') and self.resource_collection_ui:
            self.resource_collection_ui.update(dt)
        
        # Restore resource tracker updates
        if hasattr(self, 'resource_tracker_ui') and self.resource_tracker_ui:
            self.resource_tracker_ui.update_player_position(self.player.rect.centerx, self.player.rect.centery)
        
        # Update resource system for tree harvesting and resource collection
        if hasattr(self, 'resource_system'):
            self.resource_system.update(dt)
        
        # Keep only essential chat interface
        if self.npc_chat_interface:
            self.npc_chat_interface.update(dt)
        
        # Re-enable quest system with error handling
        try:
            if hasattr(self, 'quest_ui') and self.quest_ui:
                self.quest_ui.update(dt)
        except Exception as e:
            print(f"Error updating quest UI: {e}")
            # Continue without crashing
        
        # Disable cache stats collection - expensive operation
        # try:
        #     if hasattr(self, 'cache_stats_display'):
        #         # Collect cache stats from NPCs
        #         cache_stats = {}
        #         for npc in self.npcs:
        #             if npc.ai_client and hasattr(npc.ai_client, 'get_cache_stats'):
        #                 npc_stats = npc.ai_client.get_cache_stats()
        #                 # Aggregate stats from all NPCs
        #                 for key, value in npc_stats.items():
        #                     if isinstance(value, (int, float)):
        #                         cache_stats[key] = cache_stats.get(key, 0) + value
        #                     else:
        #                         cache_stats[key] = value
        #         
        #         self.cache_stats_display.update_stats(cache_stats)
        # except Exception as e:
        #     print(f"Error updating cache stats: {e}")
        
        # Disable all remaining system updates for maximum performance
        # Restore XP system updates
        try:
            if hasattr(self, 'xp_system') and self.xp_system:
                self.xp_system.update(dt)
        except Exception as e:
            print(f"Error updating XP system: {e}")
        
        # Restore XP display system
        try:
            if hasattr(self, 'xp_display_ui') and self.xp_display_ui:
                self.xp_display_ui.update(dt)
        except Exception as e:
            print(f"Error updating XP display UI: {e}")
        
        # Update action bar
        try:
            if hasattr(self, 'action_bar') and self.action_bar:
                self.action_bar.update(dt)
        except Exception as e:
            print(f"Error updating action bar: {e}")
        
        # Update shop system (no update method needed currently)
        # Shop interior is event-driven
        
        # Restore drag-drop inventory system
        try:
            if hasattr(self, 'drag_drop_inventory') and self.drag_drop_inventory:
                self.drag_drop_inventory.update(dt)
        except Exception as e:
            print(f"Error updating drag drop inventory: {e}")
        
        # Restore unified HUD update
        try:
            if hasattr(self, 'unified_hud') and self.unified_hud:
                self.unified_hud.update(dt)
        except Exception as e:
            print(f"Error updating unified HUD: {e}")
        
        # Smooth camera updates every frame for better experience
        self.camera.update(self.player)
    
    def draw(self):
        from src.debug.performance_profiler import profiler
        
        with profiler.time_operation("draw_state_specific"):
            if self.game_state == "loading":
                self.loading_screen.draw()
            elif self.game_state == "character_loading":
                self.character_loading_screen.draw()
            elif self.game_state == "menu":
                self.main_menu.draw()
            elif self.game_state == "character_creation":
                self.character_creator.draw()
            elif self.game_state == "world_customization":
                if hasattr(self, 'world_customizer'):
                    self.world_customizer.draw()
            elif self.game_state == "settings":
                self.settings_menu.draw()
            elif self.game_state == "api_keys":
                self.api_key_manager.draw()
            elif self.game_state == "playing":
                self._draw_game()
            elif self.game_state == "in_house":
                self._draw_house()
            elif self.game_state == "paused":
                self._draw_game()
                self.pause_menu.draw()
        
        with profiler.time_operation("pygame_display_flip"):
            pygame.display.flip()
    
    def _draw_game(self):
        from src.debug.performance_profiler import profiler
        
        with profiler.time_operation("screen_fill"):
            self.screen.fill(constants.BACKGROUND_COLOR)
        
        with profiler.time_operation("map_draw"):
            self.map.draw(self.screen, self.camera)
        
        # Draw resource nodes (trees and harvestables) - essential for gameplay
        if hasattr(self, 'resource_system'):
            with profiler.time_operation("resource_system_draw"):
                self.resource_system.draw_resources(self.screen, self.camera)
        
        # Restore NPC house indicators
        if hasattr(self, 'npc_house_manager') and self.npc_house_manager:
            self._draw_npc_house_indicators()
        
        with profiler.time_operation("sprites_draw"):
            for sprite in self.all_sprites:
                sprite.draw(self.screen, self.camera)
                
                # Draw selection indicator for selected NPC
                if (hasattr(sprite, 'name') and self.hud.selected_npc 
                    and sprite == self.hud.selected_npc):
                    self._draw_selection_indicator(sprite)
        
        # Restore event drawing
        self._draw_events()
        
        # Draw basic game clock FIRST (so it's behind other UI elements)
        if self.game_clock:
            self.game_clock.draw(self.time_system)
            
        # Draw HUD every frame - no flashing (draws over the clock)
        if hasattr(self, 'hud') and self.hud:
            with profiler.time_operation("hud_draw"):
                active_events = getattr(self, 'event_generator', None)
                events_list = active_events.get_active_events() if active_events else []
                self.hud.draw(self.clock.get_fps(), "Connected", events_list, self.npcs, self.player)
        
        # Restore all essential UI drawing
        self.ai_response_box.draw()
        self.cost_monitor.draw()
        self.data_analysis_panel.draw()
        self.interaction_menu.draw()
        
        # Show FPS for monitoring performance
        fps_text = f"FPS: {self.clock.get_fps():.1f}"
        font = pygame.font.Font(None, 24)
        fps_surface = font.render(fps_text, True, (255, 255, 0))
        self.screen.blit(fps_surface, (10, 40))
        
        # Keep only chat interface for essential interaction
        if self.npc_chat_interface and self.npc_chat_interface.visible:
            self.npc_chat_interface.draw()
        
        # Restore all other UI systems
        self.help_system.draw()
        self.skills_inventory_ui.draw()
        
        # Restore ALL enhanced UI drawing
        if hasattr(self, 'detailed_inventory_ui') and self.detailed_inventory_ui:
            self.detailed_inventory_ui.draw()
        if hasattr(self, 'resource_collection_ui') and self.resource_collection_ui:
            self.resource_collection_ui.draw()
        if hasattr(self, 'resource_tracker_ui') and self.resource_tracker_ui:
            self.resource_tracker_ui.draw()
        unified_hud_active = False  # Define this variable
        if hasattr(self, 'xp_display_ui') and self.xp_display_ui and not unified_hud_active:
            self.xp_display_ui.draw()
        # Draw action bar
        if hasattr(self, 'action_bar') and self.action_bar:
            self.action_bar.draw()
        
        # Restore drag-drop inventory drawing
        if hasattr(self, 'drag_drop_inventory') and self.drag_drop_inventory:
            self.drag_drop_inventory.draw()
        
        # Draw shop interior
        if hasattr(self, 'shop_interior') and self.shop_interior:
            self.shop_interior.draw()
        
        # Disable all effect drawing for maximum performance
        # if hasattr(self, 'player_movement_system') and self.player_movement_system:
        #     self.player_movement_system.draw_effects(self.screen, self.camera)
        #     self.player_movement_system.draw_ui_indicators(self.screen)
        
        # Disable resource interaction effects
        # if hasattr(self, 'resource_interaction_manager') and self.resource_interaction_manager:
        #     self.resource_interaction_manager.draw_effects(self.screen, self.camera)
        
        # Skip unified HUD drawing for performance
        # try:
        #     if hasattr(self, 'unified_hud') and self.unified_hud:
        #         self.unified_hud.draw()
        # except Exception as e:
        #     print(f"Error drawing unified HUD: {e}")
        
        # Draw XP effects on top
        try:
            if hasattr(self, 'xp_system') and self.xp_system:
                self.xp_system.draw_xp_effects(self.screen)
        except Exception as e:
            print(f"Error drawing XP effects: {e}")
        
        # Draw notification system
        self.notification_system.draw()
        
        # Re-enable quest UI drawing with error handling
        try:
            if hasattr(self, 'quest_ui') and self.quest_ui:
                self.quest_ui.draw()
        except Exception as e:
            print(f"Error drawing quest UI: {e}")
            # Continue without crashing
        
        # Draw cache stats display
        try:
            if hasattr(self, 'cache_stats_display'):
                self.cache_stats_display.draw()
        except Exception as e:
            print(f"Error drawing cache stats: {e}")
        
        # Draw shortcut keys UI (bottom layer of overlays)
        if hasattr(self, 'shortcut_keys_ui'):
            self.shortcut_keys_ui.draw()
        
        # Draw welcome message if active
        self.welcome_message.draw()
        
        # Draw HUD edit mode overlay (absolute highest priority)
        if hasattr(self, 'hud_manager'):
            self.hud_manager.draw_edit_mode_hud()
    
    def _handle_npc_selection(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = pygame.mouse.get_pos()
            world_pos = (mouse_pos[0] - self.camera.camera.x, mouse_pos[1] - self.camera.camera.y)
            
            for npc in self.npcs:
                if npc.rect.collidepoint(world_pos):
                    # Select NPC in HUD for visual feedback
                    self.hud.select_npc(npc)
                    print(f"Selected NPC: {npc.name}")
                    
                    # Check if player is close enough for interaction
                    distance = ((self.player.rect.centerx - npc.rect.centerx) ** 2 + 
                               (self.player.rect.centery - npc.rect.centery) ** 2) ** 0.5
                    
                    if distance <= 80:  # Within interaction range
                        # Open interaction menu automatically
                        self.interaction_menu.show(self.player, npc, mouse_pos)
                    else:
                        # Show message about being too far
                        print(f"Too far from {npc.name}! Move closer to interact.")
                        # Optional: Make player say something
                        if hasattr(self.player, 'say'):
                            self.player.say(f"I need to get closer to {npc.name}")
                    break
    
    def _draw_selection_indicator(self, npc):
        """Draw a visual indicator around the selected NPC"""
        import time
        
        # Get NPC position on screen
        npc_screen_rect = self.camera.apply(npc)
        
        # Animated selection circle
        time_value = time.time() * 3  # Animation speed
        pulse = abs(math.sin(time_value)) * 0.3 + 0.7  # Pulse between 0.7 and 1.0
        
        # Circle parameters
        center_x = npc_screen_rect.centerx
        center_y = npc_screen_rect.centery
        radius = int(25 * pulse)
        
        # Draw glowing circle
        selection_color = (100, 255, 100, int(150 * pulse))
        
        # Draw outer glow
        for i in range(3):
            glow_radius = radius + i * 2
            glow_alpha = int(50 * pulse / (i + 1))
            glow_color = (100, 255, 100, glow_alpha)
            
            # Create a surface for the glow circle
            glow_surface = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(glow_surface, glow_color, (glow_radius, glow_radius), glow_radius)
            self.screen.blit(glow_surface, (center_x - glow_radius, center_y - glow_radius))
        
        # Draw main selection circle
        pygame.draw.circle(self.screen, (100, 255, 100), (center_x, center_y), radius, 2)
        
        # Draw small dots around the circle
        for angle in range(0, 360, 45):
            dot_angle = math.radians(angle + time_value * 50)  # Rotating dots
            dot_x = center_x + int((radius + 8) * math.cos(dot_angle))
            dot_y = center_y + int((radius + 8) * math.sin(dot_angle))
            pygame.draw.circle(self.screen, (150, 255, 150), (dot_x, dot_y), 3)
    
    def _draw_events(self):
        """Draw beautiful event areas with decorations"""
        active_events = self.event_generator.get_active_events()
        
        # Use the map's asset manager for event decorations
        assets = self.map.assets
        
        for event in active_events:
            if event.location:
                event_rect = pygame.Rect(event.location[0] - 60, event.location[1] - 60, 120, 120)
                if self.camera.camera.colliderect(event_rect):
                    screen_pos = self.camera.apply_rect(event_rect)
                    
                    # Draw decorative elements based on event type
                    if "gathering" in event.title.lower() or "community" in event.title.lower():
                        # Draw tent for community events
                        tent_sprite = assets.get_sprite("tent")
                        if tent_sprite:
                            tent_rect = tent_sprite.get_rect()
                            tent_rect.center = screen_pos.center
                            self.screen.blit(tent_sprite, tent_rect)
                        
                        # Add tables around the tent
                        table_sprite = assets.get_sprite("table")
                        if table_sprite:
                            for angle in [0, 90, 180, 270]:
                                table_pos = (
                                    screen_pos.centerx + 40 * math.cos(math.radians(angle)),
                                    screen_pos.centery + 40 * math.sin(math.radians(angle))
                                )
                                table_rect = table_sprite.get_rect(center=table_pos)
                                self.screen.blit(table_sprite, table_rect)
                    
                    else:
                        # Generic event - draw colorful area
                        event_color = (255, 215, 0, 100)  # Golden glow
                        
                        # Create a surface for the glow effect
                        glow_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
                        pygame.draw.circle(glow_surface, event_color, (60, 60), 50)
                        self.screen.blit(glow_surface, screen_pos)
                        
                        # Add sparkle effects
                        import time
                        sparkle_time = time.time() * 3  # Animation speed
                        for i in range(8):
                            angle = (i * 45 + sparkle_time * 30) % 360
                            sparkle_x = screen_pos.centerx + 35 * math.cos(math.radians(angle))
                            sparkle_y = screen_pos.centery + 35 * math.sin(math.radians(angle))
                            
                            sparkle_alpha = int(128 + 127 * math.sin(sparkle_time + i))
                            sparkle_color = (255, 255, 200, sparkle_alpha)
                            pygame.draw.circle(self.screen, sparkle_color[:3], (int(sparkle_x), int(sparkle_y)), 3)
                    
                    # Event title with better styling
                    font = pygame.font.Font(None, 18)
                    title_text = font.render(event.title, True, (255, 255, 255))
                    shadow_text = font.render(event.title, True, (0, 0, 0))
                    
                    title_rect = title_text.get_rect()
                    title_rect.centerx = screen_pos.centerx
                    title_rect.bottom = screen_pos.top - 10
                    
                    # Draw shadow
                    shadow_rect = title_rect.copy()
                    shadow_rect.x += 1
                    shadow_rect.y += 1
                    self.screen.blit(shadow_text, shadow_rect)
                    
                    # Draw title
                    self.screen.blit(title_text, title_rect)
                    
                    # Participant info with icons
                    if event.participants:
                        participant_count = len(event.participants)
                        count_text = f"👥 {participant_count} attending"
                        
                        count_surface = font.render(count_text, True, (200, 255, 200))
                        count_rect = count_surface.get_rect()
                        count_rect.centerx = screen_pos.centerx
                        count_rect.top = screen_pos.bottom + 5
                        
                        # Semi-transparent background for text
                        bg_rect = count_rect.inflate(10, 4)
                        bg_surface = pygame.Surface((bg_rect.width, bg_rect.height), pygame.SRCALPHA)
                        bg_surface.fill((0, 0, 0, 120))
                        self.screen.blit(bg_surface, bg_rect)
                        
                        self.screen.blit(count_surface, count_rect)
    
    def run(self):
        from src.debug.performance_profiler import profiler
        
        while self.running:
            frame_start = time.time()
            
            with profiler.time_operation("clock_tick"):
                dt = self.clock.tick(constants.FPS) / 1000.0
            
            with profiler.time_operation("handle_events"):
                self.handle_events()
            
            with profiler.time_operation("update_total"):
                self.update(dt)
            
            with profiler.time_operation("draw_total"):
                self.draw()
            
            frame_time = time.time() - frame_start
            profiler.log_frame_complete(frame_time)
        
        self.cleanup()
        pygame.quit()
        sys.exit()
    
    def _activate_ai_systems(self):
        """Activate AI systems after welcome screen is dismissed"""
        print("🤖 Activating AI systems...")
        self.ai_systems_active = True
        
        # Initialize AI clients for all NPCs
        print("Initializing AI clients for NPCs...")
        for npc in self.npcs:
            if not hasattr(npc, 'ai_client') or npc.ai_client is None:
                try:
                    from src.ai.ai_client_manager import AIClientManager
                    ai_manager = AIClientManager()
                    npc.ai_client = ai_manager.create_ai_client()
                    print(f"AI client initialized for {npc.name}")
                except Exception as e:
                    print(f"Failed to initialize AI for {npc.name}: {e}")
                    npc.ai_client = None
        
        # Show notification
        if hasattr(self, 'notification_system'):
            self.notification_system.add_notification("AI systems activated! NPCs are now alive!")
        
        print("✨ AI systems are now active - NPCs will start thinking and acting!")
    
    def _get_ai_status(self):
        from src.ai.ai_client_manager import AIClientManager
        try:
            ai_manager = AIClientManager()
            status = ai_manager.get_provider_status()
            
            provider = status["provider"]
            available_keys = status["available_keys"]
            
            if available_keys:
                return f"{provider} (Keys: {', '.join(available_keys)})"
            else:
                return f"{provider} (Local only)"
        except Exception as e:
            return f"AI Status: Error ({str(e)[:20]}...)"
    
    def _show_character_creator(self):
        self.game_state = "character_creation"
    
    def _character_created(self, character_data):
        self.character_data = character_data
        # Transition to character loading screen before starting game
        self.game_state = "character_loading"
        self.character_loading_screen = CharacterLoadingScreen(self.screen)
        self.character_loading_progress = 0.0
    
    def _load_character_world(self, dt):
        """Load the game world with fun loading screen after character creation"""
        if self.character_loading_progress >= 1.0:
            # Loading complete, start the game and show welcome screen
            self._start_new_game()
            # Show welcome screen immediately to let user explore before AI starts
            if hasattr(self, 'welcome_message'):
                self.welcome_message.show()
            return
        
        # Simulate world loading with stages
        loading_stages = [
            (0.15, "🏗️ Building your neighborhood..."),
            (0.30, "🌳 Planting trees and flowers..."),
            (0.45, "🏠 Constructing houses..."),
            (0.60, "👥 Creating your AI neighbors..."),
            (0.75, "🧠 Teaching NPCs how to think..."),
            (0.90, "🎮 Setting up game mechanics..."),
            (1.00, "✨ World ready! Welcome to AI Sims! ✨")
        ]
        
        # Progress through stages over time
        self.character_loading_progress += dt * 0.25  # Takes about 4 seconds total
        
        # Find current stage and update loading screen
        for progress, message in loading_stages:
            if self.character_loading_progress >= progress - 0.01:
                self.character_loading_screen.set_progress(progress, message)
        
        # Clamp progress
        self.character_loading_progress = min(1.0, self.character_loading_progress)
    
    def _start_new_game(self):
        print(f"Starting new game with character: {self.character_data['name'] if self.character_data else 'Default Player'}")
        self.game_state = "playing"
        self.game_time = 0.0
        self.auto_save_timer = 0.0
        
        # Show welcome message for new players
        if hasattr(self, 'welcome_message'):
            self.welcome_message.show()
        
        # Create player with character data
        self.player = EnhancedPlayer(400, 300, self.character_data)
        
        # Initialize systems that need player with error handling
        try:
            if hasattr(self, 'inventory_system') and self.inventory_system:
                self.player_movement_system = PlayerMovementSystem(self.player, self.inventory_system, self.resource_system, self.skill_system)
            else:
                self.player_movement_system = None
        except Exception as e:
            print(f"Error initializing player movement system: {e}")
            self.player_movement_system = None
        
        try:
            if hasattr(self, 'resource_system') and self.resource_system:
                self.resource_interaction_manager = ResourceInteractionManager(self.resource_system, self.inventory_system, self.skill_system, self.xp_system, self.quest_system, self.action_bar)
            else:
                self.resource_interaction_manager = None
        except Exception as e:
            print(f"Error initializing resource interaction manager: {e}")
            self.resource_interaction_manager = None
        
        try:
            if hasattr(self, 'xp_system') and self.xp_system:
                self.exploration_tracker = ExplorationTracker(self.xp_system)
            else:
                self.exploration_tracker = None
        except Exception as e:
            print(f"Error initializing exploration tracker: {e}")
            self.exploration_tracker = None
        
        # Update unified HUD with data sources
        try:
            if hasattr(self, 'unified_hud') and self.unified_hud:
                self.unified_hud.set_data_sources(
                    player=self.player,
                    xp_system=self.xp_system,
                    time_system=self.time_system,
                    skill_system=self.skill_system,
                    inventory_system=self.inventory_system
                )
        except Exception as e:
            print(f"Error updating unified HUD: {e}")
        
        # Grant starting XP bonus
        try:
            if hasattr(self, 'xp_system') and self.xp_system:
                self.xp_system.add_xp(100, XPCategory.EXPLORATION, "Started your adventure!")
        except Exception as e:
            print(f"Error adding starting XP: {e}")
        
        # Reset NPCs
        self.npcs.clear()
        self.all_sprites.empty()
        self._spawn_npcs()
        
        # Update data analysis panel with current data (only if loaded)
        if self.data_analysis_panel:
            self.data_analysis_panel.set_data_sources(self.npcs, self.memory_manager, self.player)
        
        self.all_sprites.add(self.player)
        for npc in self.npcs:
            self.all_sprites.add(npc)
    
    def _load_game(self):
        print("Loading game...")
        save_data = self.save_system.load_game()
        
        if save_data:
            self.game_time = save_data.get("game_time", 0.0)
            
            # Restore time system
            time_system_data = save_data.get("time_system")
            if time_system_data:
                self.time_system.load_save_data(time_system_data)
            
            # Restore player character
            player_data = save_data.get("player")
            if player_data:
                self.character_data = player_data
                self.player = EnhancedPlayer(400, 300, player_data)
            
            # Restore NPCs
            self.npcs = self.save_system.restore_npcs(save_data["npcs"], self.memory_manager)
            
            # Add AI response box and chat interface reference to loaded NPCs
            for npc in self.npcs:
                npc.ai_response_box = self.ai_response_box
                npc.chat_interface = self.npc_chat_interface
            
            # Restore events
            restored_events = self.save_system.restore_events(save_data["events"])
            self.event_generator.active_events = restored_events
            
            # Update sprite groups
            self.all_sprites.empty()
            self.all_sprites.add(self.player)
            for npc in self.npcs:
                self.all_sprites.add(npc)
            
            # Update data analysis panel with loaded data (only if loaded)
            if self.data_analysis_panel:
                self.data_analysis_panel.set_data_sources(self.npcs, self.memory_manager, self.player)
            
            self.game_state = "playing"
        else:
            print("Failed to load game, starting new game instead.")
            self._show_character_creator()
    
    def _pause_game(self):
        self.game_state = "paused"
    
    def _resume_game(self):
        self.game_state = "playing"
    
    def _pause_for_interaction(self):
        """Pause time and AI during NPC interactions"""
        self.time_paused = True
        self.ai_paused = True
        print("⏸️  Time and AI paused for NPC interaction")
    
    def _resume_from_interaction(self):
        """Resume time and AI from NPC interaction"""
        self.time_paused = False
        self.ai_paused = False
        print("▶️  Time and AI resumed from NPC interaction")
    
    def _save_game(self):
        success = self.save_system.save_game(
            self.npcs,
            self.event_generator.get_active_events(),
            self.game_time,
            self.character_data,
            self.time_system.get_save_data()
        )
        
        if success:
            print("Game saved successfully!")
        else:
            print("Failed to save game!")
    
    def _auto_save(self):
        print("Auto-saving...")
        self._save_game()
    
    def _return_to_menu(self):
        self.game_state = "menu"
        # Refresh main menu to update load button (only if loaded)
        if self.main_menu and hasattr(self.main_menu, '_check_save_exists'):
            self.main_menu._check_save_exists()
    
    def _show_settings(self):
        self.game_state = "settings"
    
    def _show_api_keys(self):
        self.game_state = "api_keys"
    
    def _show_world_customizer(self):
        """Show the world customization screen"""
        if not hasattr(self, 'world_customizer'):
            self.world_customizer = WorldCustomizer(self.screen)
            self.world_customizer.on_back = self._return_to_character_creation
            self.world_customizer.on_apply_settings = self._apply_world_settings
        self.game_state = "world_customization"
    
    def _return_to_character_creation(self):
        """Return to character creation from world customizer"""
        self.game_state = "character_creation"
    
    def _apply_world_settings(self, settings_data):
        """Apply world customization settings and start game creation"""
        print("Applying world settings...")
        print(f"World: {settings_data['world']}")
        print(f"NPCs: {len(settings_data['custom_npcs'])} custom NPCs")
        print(f"Performance: {settings_data['performance']}")
        
        # Store the custom settings for world generation
        self.custom_world_settings = settings_data
        
        # Return to character creation to finalize character
        self.game_state = "character_creation"
    
    def _return_to_settings(self):
        self.game_state = "settings"
    
    def _api_keys_saved(self, key_data):
        print("API keys saved successfully!")
        # Reload AI configuration with new keys
        self._reload_ai_configuration()
    
    def _apply_settings(self, settings_dict):
        print("Settings applied:", settings_dict)
        
        # Apply screen resolution if changed
        if "screen_resolution" in settings_dict:
            self._apply_resolution_change(settings_dict["screen_resolution"])
        
        # Apply settings to game components
        if hasattr(self, 'hud'):
            self.hud.show_debug = settings_dict.get("show_debug_info", False)
        
        # Apply auto-save interval
        self.auto_save_interval = settings_dict.get("auto_save_interval", 300)
        
        # Reload AI configuration if AI provider changed
        if self.npcs:  # Only if game is running with NPCs
            self._reload_ai_configuration()
    
    def _apply_resolution_change(self, resolution):
        """Apply screen resolution change"""
        try:
            width, height = map(int, resolution.split('x'))
            self.screen = pygame.display.set_mode((width, height))
            print(f"Resolution changed to {width}x{height}")
            
            # Update constants for UI positioning
            import src.core.constants as constants
            constants.SCREEN_WIDTH = width
            constants.SCREEN_HEIGHT = height
            
            # Recreate UI components that depend on screen size
            self._recreate_ui_components()
            
        except Exception as e:
            print(f"Failed to change resolution: {e}")
    
    def _recreate_ui_components(self):
        """Recreate UI components that need to adapt to new screen size"""
        try:
            # Recreate main menu
            if hasattr(self, 'main_menu') and self.main_menu:
                self.main_menu = MainMenu(self.screen)
                self.main_menu.on_new_game = self._new_game
                self.main_menu.on_load_game = self._load_game
                self.main_menu.on_settings = self._show_settings
                self.main_menu.on_quit = self._quit_game
            
            # Recreate settings menu
            if hasattr(self, 'settings_menu') and self.settings_menu:
                self.settings_menu = SettingsMenu(self.screen)
                self.settings_menu.on_back = self._return_to_menu
                self.settings_menu.on_apply = self._apply_settings
                self.settings_menu.on_manage_api_keys = self._show_api_keys
            
            # Recreate character creator
            if hasattr(self, 'character_creator') and self.character_creator:
                self.character_creator = CharacterCreator(self.screen)
                self.character_creator.on_character_created = self._character_created
                self.character_creator.on_back = self._return_to_menu
                self.character_creator.on_advanced_settings = self._show_world_customizer
            
            # Recreate world customizer
            if hasattr(self, 'world_customizer') and self.world_customizer:
                from src.ui.world_customizer import WorldCustomizer
                self.world_customizer = WorldCustomizer(self.screen)
                self.world_customizer.on_apply_settings = self._apply_world_settings
                self.world_customizer.on_back = self._return_to_character_creation
            
            # Recreate HUD (most important for in-game)
            if hasattr(self, 'hud') and self.hud:
                from src.ui.modern_hud import ModernHUD
                self.hud = ModernHUD(self.screen)
            
            # Recreate camera with new screen dimensions
            if hasattr(self, 'camera') and self.camera:
                from src.core.camera import Camera
                self.camera = Camera(constants.SCREEN_WIDTH, constants.SCREEN_HEIGHT)
            
            print("UI components recreated for new resolution")
        except Exception as e:
            print(f"Error recreating UI components: {e}")
    
    def _reload_ai_configuration(self):
        """Reload AI configuration after API keys are updated"""
        print("Reloading AI configuration with updated API keys...")
        from src.ai.ai_client_manager import AIClientManager
        
        # Recreate AI clients for all NPCs to pick up new API keys
        for npc in self.npcs:
            try:
                ai_manager = AIClientManager()
                old_client = npc.ai_client
                npc.ai_client = ai_manager.create_ai_client()
                print(f"Updated AI client for {npc.name}")
            except Exception as e:
                print(f"Failed to update AI client for {npc.name}: {e}")
                # Keep old client if update fails
                pass
    
    def _quit_game(self):
        self.running = False
    
    def _try_open_interaction_menu(self):
        """Try to open interaction menu if player is near an NPC"""
        nearby_npcs = self.player.get_nearby_npcs(self.npcs, max_distance=80)
        if nearby_npcs:
            # Get the closest NPC
            closest_npc = nearby_npcs[0]
            mouse_pos = pygame.mouse.get_pos()
            self.interaction_menu.show(self.player, closest_npc, mouse_pos)
    
    def _try_open_chat(self):
        """Try to open chat interface if player is near an NPC"""
        nearby_npcs = self.player.get_nearby_npcs(self.npcs, max_distance=80)
        if nearby_npcs and self.npc_chat_interface:
            # Get the closest NPC
            closest_npc = nearby_npcs[0]
            self.npc_chat_interface.show(closest_npc)
    
    def _handle_greet_interaction(self, player, npc):
        """Handle greet interaction"""
        player.interact_with_npc(npc, "greet")
    
    def _handle_chat_interaction(self, player, npc):
        """Handle chat interaction"""
        player.interact_with_npc(npc, "chat")
    
    def _handle_gift_interaction(self, player, npc):
        """Handle gift interaction"""
        player.interact_with_npc(npc, "give_gift")
    
    def _handle_activity_interaction(self, player, npc):
        """Handle activity invitation interaction"""
        player.interact_with_npc(npc, "invite_activity")
    
    def _handle_ask_interaction(self, player, npc):
        """Handle ask about interaction"""
        player.interact_with_npc(npc, "ask_about")
    
    def _handle_custom_dialogue(self, player, npc, message):
        """Handle custom dialogue interaction"""
        player.interact_with_npc(npc, "custom_dialogue", message)
    
    def _handle_open_chat_interaction(self, player, npc):
        """Handle opening chat interface with NPC"""
        if self.npc_chat_interface:
            self.npc_chat_interface.show(npc)
    
    def _handle_speed_change(self, speed: float):
        """Handle game speed change"""
        self.time_multiplier = speed
        print(f"Game speed set to {speed:.1f}x")
    
    def _handle_pause_toggle(self, paused: bool):
        """Handle pause toggle"""
        if paused:
            print("Game paused")
        else:
            print("Game resumed")
    
    def _register_hud_components(self):
        """Register all HUD components as draggable"""
        if not hasattr(self, 'hud_manager'):
            return
        
        # Register all HUD components that exist
        component_mappings = []
        
        # Core components that should always exist
        if hasattr(self, 'hud') and self.hud:
            component_mappings.extend([
                ('player_panel', self.hud, 'player_panel'),
                ('npc_panel', self.hud, 'npc_panel'),
                ('events_panel', self.hud, 'events_panel'),
            ])
        
        if hasattr(self, 'shortcut_keys_ui') and self.shortcut_keys_ui:
            component_mappings.append(('shortcut_keys', self.shortcut_keys_ui, 'shortcut_keys'))
        
        if hasattr(self, 'ai_response_box') and self.ai_response_box:
            component_mappings.append(('ai_response_box', self.ai_response_box, 'ai_response_box'))
        
        if hasattr(self, 'cost_monitor') and self.cost_monitor:
            component_mappings.append(('cost_monitor', self.cost_monitor, 'cost_monitor'))
        
        if hasattr(self, 'speed_controller') and self.speed_controller:
            component_mappings.append(('speed_controller', self.speed_controller, 'speed_controller'))
        
        if hasattr(self, 'data_analysis_panel') and self.data_analysis_panel:
            component_mappings.append(('data_analysis_panel', self.data_analysis_panel, 'data_analysis_panel'))
        
        if hasattr(self, 'game_clock') and self.game_clock:
            component_mappings.append(('game_clock', self.game_clock, 'game_clock'))
        
        if hasattr(self, 'help_system') and self.help_system:
            component_mappings.append(('help_system', self.help_system, 'help_system'))
        
        if hasattr(self, 'notification_system') and self.notification_system:
            component_mappings.append(('notification_system', self.notification_system, 'notification_system'))
        
        if hasattr(self, 'skills_inventory_ui') and self.skills_inventory_ui:
            component_mappings.append(('skills_inventory', self.skills_inventory_ui, 'skills_inventory'))
        
        # Add optional components if they exist
        if hasattr(self, 'quest_ui') and self.quest_ui:
            component_mappings.append(('quest_ui', self.quest_ui, 'quest_ui'))
        
        if hasattr(self, 'xp_display_ui') and self.xp_display_ui:
            component_mappings.append(('xp_display', self.xp_display_ui, 'xp_display'))
        
        if hasattr(self, 'detailed_inventory_ui') and self.detailed_inventory_ui:
            component_mappings.append(('detailed_inventory', self.detailed_inventory_ui, 'detailed_inventory'))
        
        if hasattr(self, 'resource_collection_ui') and self.resource_collection_ui:
            component_mappings.append(('resource_collection', self.resource_collection_ui, 'resource_collection'))
        
        if hasattr(self, 'resource_tracker_ui') and self.resource_tracker_ui:
            component_mappings.append(('resource_tracker', self.resource_tracker_ui, 'resource_tracker'))
        
        if hasattr(self, 'cache_stats_display') and self.cache_stats_display:
            component_mappings.append(('cache_stats', self.cache_stats_display, 'cache_stats'))
        
        # Register components
        for name, ui_component, component_type in component_mappings:
            if ui_component:
                self.hud_manager.register_component(name, ui_component)
        
        # Load saved layout
        self.hud_manager.load_layout()
        
        print(f"📍 Registered {len(component_mappings)} HUD components as draggable")
    
    def _update_hud_positions(self):
        """Update HUD component positions from draggable manager"""
        if not hasattr(self, 'hud_manager'):
            return
        
        # Update positions for all registered components
        for name, component in self.hud_manager.components.items():
            ui_component = component.ui_component
            if ui_component:
                self.hud_manager.update_component_position(name, ui_component)
    
    def _try_enter_house(self):
        """Try to enter the player's house"""
        try:
            # Ensure house_interior is properly initialized
            if not hasattr(self, 'house_interior') or not self.house_interior:
                print("Error: house_interior not initialized, creating it now...")
                self.house_interior = HouseInterior()
            
            player_house = self.map.get_player_house()
            if not player_house:
                print("No player house found on map")
                return
            
            # Check if player is close enough to house
            player_center_x = self.player.rect.centerx
            player_center_y = self.player.rect.centery
            house_center_x = player_house.x + player_house.width // 2
            house_center_y = player_house.y + player_house.height // 2
            
            distance = math.sqrt((player_center_x - house_center_x) ** 2 + 
                                (player_center_y - house_center_y) ** 2)
            
            if distance <= 80:  # Within interaction range
                # Enter house
                self.game_state = "in_house"
                # Store player's outside position
                self.player_outside_pos = (self.player.rect.x, self.player.rect.y)
                # Move player to house interior starting position
                self.player.rect.x, self.player.rect.y = self.house_interior.player_house_pos
                self.notification_system.add_notification("🏠 Welcome home! Walk around and interact with furniture using 'E' or clicking!")
                
                # Update quest objective
                if hasattr(self, 'quest_system') and self.quest_system:
                    self.quest_system.update_objective(ObjectiveType.ENTER_HOUSE, "player_house")
            else:
                self.notification_system.add_notification(f"🚶 Too far from house! Get closer to enter (distance: {distance:.0f})")
        except Exception as e:
            print(f"Error entering house: {e}")
            self.notification_system.add_notification("❌ Error entering house. Please try again.")
    
    def _try_enter_shop(self):
        """Try to enter a nearby shop"""
        try:
            if not hasattr(self, 'shop_interior') or not self.shop_interior:
                return
            
            # Find nearby shop buildings
            player_center_x = self.player.rect.centerx
            player_center_y = self.player.rect.centery
            
            for building in self.map.buildings:
                if building.building_type in ["gem_shop", "hardware_store", "mining_store"]:
                    building_center_x = building.x + building.width // 2
                    building_center_y = building.y + building.height // 2
                    
                    distance = math.sqrt((player_center_x - building_center_x) ** 2 + 
                                        (player_center_y - building_center_y) ** 2)
                    
                    if distance <= 80:  # Within interaction range
                        # Enter the shop
                        if self.shop_interior.enter_shop(building.building_type):
                            shop_names = {
                                "gem_shop": "Crystal & Gems",
                                "hardware_store": "Builder's Supply", 
                                "mining_store": "Deep Earth Mining Co."
                            }
                            shop_name = shop_names.get(building.building_type, "Shop")
                            self.notification_system.add_notification(f"🏪 Welcome to {shop_name}!")
                            return
            
            # No shop found nearby
            self.notification_system.add_notification("🚶 No shop nearby. Get closer to a shop to enter!")
            
        except Exception as e:
            print(f"Error entering shop: {e}")
            self.notification_system.add_notification("❌ Error entering shop. Please try again.")
    
    def _handle_house_events(self, event):
        """Handle events while inside the house"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE or event.key == pygame.K_h:
                # Exit house
                self.game_state = "playing"
                # Restore player's outside position
                if hasattr(self, 'player_outside_pos'):
                    self.player.rect.x, self.player.rect.y = self.player_outside_pos
                print("Exited house")
            elif event.key == pygame.K_e or event.key == pygame.K_SPACE:
                # Interact with house items
                self._interact_with_house_item()
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                # Check for item interaction
                mouse_x, mouse_y = event.pos
                item = self.house_interior.get_item_at(mouse_x, mouse_y)
                if item:
                    result = self.house_interior.interact_with_item(item, self.player)
                    if result == "exit_house":
                        self.game_state = "playing"
                        if hasattr(self, 'player_outside_pos'):
                            self.player.rect.x, self.player.rect.y = self.player_outside_pos
                        self.notification_system.add_notification("🚪 You exit your house and return to the world!")
                    else:
                        self.notification_system.add_notification(result)
                        # Grant building XP for using house furniture
                        if hasattr(self, 'xp_system'):
                            self.xp_system.add_xp(5, XPCategory.BUILDING, "Used house furniture")
    
    def _interact_with_house_item(self):
        """Interact with house item near the player"""
        # Find item near player
        player_x = self.player.rect.centerx
        player_y = self.player.rect.centery
        
        closest_item = None
        closest_distance = float('inf')
        
        for item in self.house_interior.items:
            item_center_x = item.x + item.width // 2
            item_center_y = item.y + item.height // 2
            distance = math.sqrt((player_x - item_center_x) ** 2 + (player_y - item_center_y) ** 2)
            
            if distance < closest_distance and distance <= 60:  # Within interaction range (matches visual indicator)
                closest_item = item
                closest_distance = distance
        
        if closest_item:
            result = self.house_interior.interact_with_item(closest_item, self.player)
            if result == "exit_house":
                self.game_state = "playing"
                if hasattr(self, 'player_outside_pos'):
                    self.player.rect.x, self.player.rect.y = self.player_outside_pos
                self.notification_system.add_notification("🚪 You exit your house and return to the world!")
            else:
                self.notification_system.add_notification(result)
        else:
            self.notification_system.add_notification("❌ No interactive items nearby. Look for the green 'E' indicators!")
    
    def _draw_house(self):
        """Draw the house interior scene"""
        try:
            # Ensure house_interior exists
            if not hasattr(self, 'house_interior') or not self.house_interior:
                print("Error: house_interior not initialized")
                return
            
            # Draw the house interior with player position for interaction highlighting
            if self.player:
                player_center = (self.player.rect.centerx, self.player.rect.centery)
                self.house_interior.draw(self.screen, player_pos=player_center)
                
                # Draw the player in the house (use identity camera for no transformation)
                class IdentityCamera:
                    def apply(self, sprite):
                        return sprite.rect
                    
                    def apply_rect(self, rect):
                        return rect
                
                identity_camera = IdentityCamera()
                self.player.draw(self.screen, identity_camera)
            else:
                print("Error: player not initialized")
        except Exception as e:
            print(f"Error drawing house: {e}")
            # Fallback: exit house and return to overworld
            self.game_state = "playing"
            if hasattr(self, 'player_outside_pos'):
                self.player.rect.x, self.player.rect.y = self.player_outside_pos
        
        # Draw simple instructions
        font = pygame.font.Font(None, 20)
        instructions = [
            "🏠 House Controls:",
            "E/Space - Interact with nearby items (highlighted)",
            "H/Escape - Exit house",
            "Walk around to explore different rooms"
        ]
        
        y_offset = 10
        for instruction in instructions:
            text_surface = font.render(instruction, True, (255, 255, 255))
            text_rect = text_surface.get_rect()
            text_rect.x = 10
            text_rect.y = y_offset
            
            # Draw background for text
            bg_rect = text_rect.inflate(8, 3)
            pygame.draw.rect(self.screen, (0, 0, 0, 160), bg_rect)
            
            self.screen.blit(text_surface, text_rect)
            y_offset += 22
        
        # Draw player position indicator
        pos_text = f"Position: ({self.player.rect.centerx}, {self.player.rect.centery})"
        pos_surface = pygame.font.Font(None, 16).render(pos_text, True, (200, 200, 200))
        self.screen.blit(pos_surface, (10, constants.SCREEN_HEIGHT - 20))
    
    def _handle_resource_click(self, event, action="harvest"):
        """Handle mouse clicks on resources for harvesting or stats"""
        try:
            # Get mouse position in world coordinates
            mouse_pos = pygame.mouse.get_pos()
            world_x = mouse_pos[0] - self.camera.camera.x
            world_y = mouse_pos[1] - self.camera.camera.y
            
            # Check if clicking on a resource node
            if hasattr(self, 'resource_system') and self.resource_system:
                resource_node = self.resource_system.get_resource_at(world_x, world_y, range_threshold=50)
                
                if resource_node:
                    if action == "stats":
                        # Right-click: Always show resource stats
                        self._show_resource_stats(resource_node)
                    else:
                        # Left-click: Harvest resource
                        # Check if player is close enough to harvest
                        player_x = self.player.rect.centerx  
                        player_y = self.player.rect.centery
                        
                        import math
                        distance = math.sqrt((player_x - resource_node.x) ** 2 + (player_y - resource_node.y) ** 2)
                        
                        if distance <= 100:  # Player is close enough
                            # Attempt to harvest the resource
                            success, message = self.resource_system.harvest_resource(player_x, player_y)
                            
                            if success and hasattr(self, 'notification_system'):
                                self.notification_system.add_notification(message)
                            elif not success and hasattr(self, 'notification_system'):
                                self.notification_system.add_notification(message)
                            
                            # Grant XP for successful harvest
                            if success and hasattr(self, 'xp_system'):
                                from src.systems.xp_system import XPCategory
                                self.xp_system.add_xp(10, XPCategory.GATHERING, "Resource harvested")
                                
                            print(f"Resource interaction: {message}")
                        else:
                            if hasattr(self, 'notification_system'):
                                self.notification_system.add_notification("Too far from resource")
                        
        except Exception as e:
            print(f"Error in _handle_resource_click: {e}")
            if hasattr(self, 'notification_system'):
                self.notification_system.add_notification("Error interacting with resource")
    
    def _show_resource_stats(self, resource_node):
        """Display resource statistics"""
        try:
            # Calculate regeneration progress
            if hasattr(self.resource_system, 'game_time'):
                time_since_harvest = self.resource_system.game_time - resource_node.last_harvest_time
                regen_progress = min(100, (time_since_harvest / resource_node.regeneration_time) * 100)
            else:
                regen_progress = 100
            
            # Format stats message
            stats_message = (
                f"{resource_node.resource_type.replace('_', ' ').title()}\n"
                f"Yield: {resource_node.current_yield}/{resource_node.max_yield}\n"
                f"Regen: {regen_progress:.1f}%\n"
                f"Position: ({resource_node.x}, {resource_node.y})"
            )
            
            # Show notification with stats
            if hasattr(self, 'notification_system'):
                self.notification_system.add_notification(stats_message, duration=6.0)
            
            print(f"Resource Stats:\n{stats_message}")
            
        except Exception as e:
            print(f"Error showing resource stats: {e}")
            if hasattr(self, 'notification_system'):
                self.notification_system.add_notification("Error getting resource stats")

    def _try_harvest_resource(self):
        """Try to harvest a resource near the player"""
        if not hasattr(self, 'resource_system') or not self.resource_system:
            return
        
        try:
            player_x = self.player.rect.centerx
            player_y = self.player.rect.centery
            
            # Use resource interaction manager if available
            if hasattr(self, 'resource_interaction_manager') and self.resource_interaction_manager:
                resource_node = self.resource_system.get_resource_at(player_x, player_y, 60)
                if resource_node:
                    success = self.resource_interaction_manager.start_interaction(resource_node)
                    if not success:
                        self.notification_system.add_notification("Cannot interact with this resource")
                    return
                else:
                    self.notification_system.add_notification("No resources nearby")
                    return
            
            # Fallback to direct harvest
            success, message = self.resource_system.harvest_resource(player_x, player_y)
            self.notification_system.add_notification(message)
            
            # Grant XP for successful harvest
            if success and hasattr(self, 'xp_system') and self.xp_system:
                try:
                    self.xp_system.add_xp(10, XPCategory.GATHERING, "Resource harvested")
                except Exception as e:
                    print(f"Error adding XP: {e}")
            
            # Update resource tracker with collection stats
            try:
                if success and hasattr(self, 'resource_tracker_ui') and self.resource_tracker_ui and hasattr(self.resource_tracker_ui, 'record_collection'):
                    self.resource_tracker_ui.record_collection("unknown", "unknown", 1, 5)
            except Exception as e:
                print(f"Error updating resource tracker: {e}")
                
        except Exception as e:
            print(f"Error in _try_harvest_resource: {e}")
            if hasattr(self, 'notification_system'):
                self.notification_system.add_notification("Error harvesting resource")

    def _has_nearby_resource(self):
        """Check if there's a resource nearby without showing notifications"""
        if not hasattr(self, 'resource_system') or not self.resource_system:
            return False
            
        try:
            player_x = self.player.rect.centerx
            player_y = self.player.rect.centery
            
            # Check for nearby resource
            resource_node = self.resource_system.get_resource_at(player_x, player_y, 60)
            return resource_node is not None
            
        except Exception as e:
            return False

    def _try_interact_with_resource(self):
        """Try to interact with a nearby resource (show detailed info or start collection)"""
        if not hasattr(self, 'resource_system') or not self.resource_system:
            return
            
        try:
            player_x = self.player.rect.centerx
            player_y = self.player.rect.centery
            
            # Find nearby resource
            resource_node = self.resource_system.get_resource_at(player_x, player_y, 60)
            
            if resource_node:
                # Try to use resource interaction manager first
                if hasattr(self, 'resource_interaction_manager') and self.resource_interaction_manager:
                    try:
                        success = self.resource_interaction_manager.start_interaction(resource_node)
                        if success and hasattr(self, 'resource_collection_ui') and self.resource_collection_ui:
                            try:
                                self.resource_collection_ui.show_resource_info(resource_node, (player_x, player_y))
                            except Exception as e:
                                print(f"Error showing resource collection UI: {e}")
                    except Exception as e:
                        print(f"Error with resource interaction manager: {e}")
                        # Fallback to simple harvest
                        self._try_harvest_resource()
                elif hasattr(self, 'resource_collection_ui') and self.resource_collection_ui:
                    try:
                        self.resource_collection_ui.show_resource_info(resource_node, (player_x, player_y))
                    except Exception as e:
                        print(f"Error showing resource collection UI: {e}")
                        # Fallback to simple harvest
                        self._try_harvest_resource()
                else:
                    # No resource UI available, use simple harvest
                    self._try_harvest_resource()
            else:
                # No resource nearby, show message
                if hasattr(self, 'notification_system'):
                    self.notification_system.add_notification("No resources nearby. Look for trees, rocks, or plants!")
                
        except Exception as e:
            print(f"Error in _try_interact_with_resource: {e}")
            if hasattr(self, 'notification_system'):
                self.notification_system.add_notification("Error interacting with resource")

    def _draw_npc_house_indicators(self):
        """Draw indicators showing which houses belong to which NPCs"""
        house_assignments = self.npc_house_manager.get_all_house_assignments()
        
        for npc_name, assignment in house_assignments.items():
            house_x, house_y = assignment.house_location
            
            # Create a rect for the house location
            house_rect = pygame.Rect(house_x - 32, house_y - 32, 64, 64)
            screen_rect = self.camera.apply_rect(house_rect)
            
            # Only draw if house is visible on screen
            if screen_rect.colliderect(pygame.Rect(0, 0, constants.SCREEN_WIDTH, constants.SCREEN_HEIGHT)):
                # Draw NPC name above house
                font = pygame.font.Font(None, 16)
                name_text = f"{npc_name}'s House"
                text_surface = font.render(name_text, True, (255, 255, 100))
                text_rect = text_surface.get_rect()
                text_rect.centerx = screen_rect.centerx
                text_rect.bottom = screen_rect.top - 5
                
                # Draw background for text
                bg_rect = text_rect.inflate(6, 2)
                pygame.draw.rect(self.screen, (0, 0, 0, 180), bg_rect)
                self.screen.blit(text_surface, text_rect)
                
                # Draw indicator for NPC currently at home
                if assignment.is_home:
                    # Draw green circle to show NPC is home
                    center_x = screen_rect.centerx
                    center_y = screen_rect.centery
                    pygame.draw.circle(self.screen, (0, 255, 0), (center_x, center_y), 8, 2)
                    
                    # Draw "HOME" indicator
                    home_font = pygame.font.Font(None, 12)
                    home_text = home_font.render("HOME", True, (0, 255, 0))
                    home_rect = home_text.get_rect()
                    home_rect.centerx = center_x
                    home_rect.top = center_y + 10
                    self.screen.blit(home_text, home_rect)

    def cleanup(self):
        if self.memory_manager:
            self.memory_manager.close()
            print("Memory database saved and closed.")