import pygame
import sys
import math
from typing import List, Tuple
from src.core.camera import Camera
from src.world.beautiful_map import BeautifulMap
from src.world.events import EventGenerator
from src.entities.player import Player
from src.entities.npc import NPC
from src.core.constants import *
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
from src.core.time_system import GameTime
from src.core.save_system import SaveSystem

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("AI Sims - Life Simulation")
        self.clock = pygame.time.Clock()
        self.running = True
        
        self.game_state = "loading"  # loading, menu, character_creation, character_loading, settings, api_keys, playing, paused
        self.game_time = 0.0
        self.auto_save_timer = 0.0
        self.character_data = None
        self.time_multiplier = 1.0
        
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
                self.camera = Camera(SCREEN_WIDTH, SCREEN_HEIGHT)
            
            if self.memory_manager is None:
                self.loading_screen.set_progress(0.10, "Setting up memory manager...")
                self.memory_manager = MemoryManager()
            
            if self.save_system is None:
                self.loading_screen.set_progress(0.15, "Loading save system...")
                self.save_system = SaveSystem()
            
            self.loading_progress = 0.2
        
        # Stage 2: Load map and assets (20-60%)
        elif self.loading_progress < 0.6:
            if self.map is None:
                self.loading_screen.set_progress(0.25, "Generating beautiful world...")
                self.map = BeautifulMap(MAP_WIDTH, MAP_HEIGHT)
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
                self.speed_controller = GameSpeedController(self.screen)
                self.data_analysis_panel = DataAnalysisPanel(self.screen)
                self.hud = ModernHUD(self.screen)
                self.game_clock = GameClock(self.screen)
                self.npc_chat_interface = NPCChatInterface(self.screen)
            
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
                self.player = Player(400, 300)
    
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
            }
        ]
        
        for data in npc_data:
            npc = NPC(data["x"], data["y"], data["name"], data["personality"], self.memory_manager)
            npc.ai_response_box = self.ai_response_box  # Pass response box reference
            npc.chat_interface = self.npc_chat_interface  # Pass chat interface reference
            self.npcs.append(npc)
    
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
            elif self.game_state == "settings":
                self.settings_menu.handle_event(event)
            elif self.game_state == "api_keys":
                self.api_key_manager.handle_event(event)
            elif self.game_state == "paused":
                self.pause_menu.handle_event(event)
            elif self.game_state == "playing":
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self._pause_game()
                    elif event.key == pygame.K_F5:
                        self._save_game()
                    elif event.key == pygame.K_F1:
                        # Toggle AI response box
                        self.ai_response_box.collapsed = not self.ai_response_box.collapsed
                    elif event.key == pygame.K_F2:
                        # Clear AI responses
                        self.ai_response_box.clear_responses()
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
                    elif event.key == pygame.K_c:
                        # Open chat with nearby NPC
                        self._try_open_chat()
                    elif event.key == pygame.K_t:
                        # Alternative key to open chat
                        self._try_open_chat()
                
                if not self.hud.handle_event(event):
                    if not self.ai_response_box.handle_event(event):
                        if not self.cost_monitor.handle_event(event):
                            if not self.speed_controller.handle_event(event):
                                if not self.data_analysis_panel.handle_event(event):
                                    if not self.interaction_menu.handle_event(event):
                                        if not (self.game_clock and self.game_clock.handle_event(event)):
                                            if not (self.npc_chat_interface and self.npc_chat_interface.handle_event(event)):
                                                self._handle_npc_selection(event)
    
    def update(self, dt):
        if self.game_state == "loading":
            self.loading_screen.update(dt)
            self._load_game_assets(dt)
            return
        
        if self.game_state == "character_loading":
            self.character_loading_screen.update(dt)
            self._load_character_world(dt)
            return
        
        if self.game_state == "api_keys":
            self.api_key_manager.update(dt)
            return
        
        if self.game_state != "playing":
            return
        
        # Apply time multiplier to delta time
        adjusted_dt = dt * self.time_multiplier
        
        self.game_time += adjusted_dt
        self.auto_save_timer += adjusted_dt
        
        # Update time system
        self.time_system.update(dt, self.time_multiplier)
        
        # Update game clock
        if self.game_clock:
            self.game_clock.update(dt)
        
        # Auto-save every 5 minutes
        if self.auto_save_timer >= 300:
            self._auto_save()
            self.auto_save_timer = 0
        
        keys = pygame.key.get_pressed()
        self.player.update(adjusted_dt, keys)
        
        self.event_generator.update(adjusted_dt)
        active_events = self.event_generator.get_active_events()
        
        for npc in self.npcs:
            npc.update(adjusted_dt, self.npcs, active_events)
        
        # Update AI response box, cost monitor, speed controller, data analysis panel, interaction menu, and chat interface
        self.ai_response_box.update(dt)
        self.cost_monitor.update(dt)
        self.speed_controller.update(dt)
        self.data_analysis_panel.update(dt)
        self.interaction_menu.update(dt)
        
        if self.npc_chat_interface:
            self.npc_chat_interface.update(dt)
        
        self.camera.update(self.player)
    
    def draw(self):
        if self.game_state == "loading":
            self.loading_screen.draw()
        elif self.game_state == "character_loading":
            self.character_loading_screen.draw()
        elif self.game_state == "menu":
            self.main_menu.draw()
        elif self.game_state == "character_creation":
            self.character_creator.draw()
        elif self.game_state == "settings":
            self.settings_menu.draw()
        elif self.game_state == "api_keys":
            self.api_key_manager.draw()
        elif self.game_state == "playing":
            self._draw_game()
        elif self.game_state == "paused":
            self._draw_game()
            self.pause_menu.draw()
        
        pygame.display.flip()
    
    def _draw_game(self):
        self.screen.fill(BACKGROUND_COLOR)
        
        self.map.draw(self.screen, self.camera)
        
        for sprite in self.all_sprites:
            sprite.draw(self.screen, self.camera)
        
        self._draw_events()
        
        # Draw HUD
        active_events = self.event_generator.get_active_events()
        ai_status = self._get_ai_status()
        self.hud.draw(self.clock.get_fps(), ai_status, active_events, self.npcs, self.player)
        
        # Draw AI response box, cost monitor, speed controller, data analysis panel, and interaction menu
        self.ai_response_box.draw()
        self.cost_monitor.draw()
        self.speed_controller.draw()
        self.data_analysis_panel.draw()
        self.interaction_menu.draw()
        
        # Draw game clock
        if self.game_clock:
            self.game_clock.draw(self.time_system)
        
        # Draw chat interface (on top of everything)
        if self.npc_chat_interface:
            self.npc_chat_interface.draw()
    
    def _handle_npc_selection(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = pygame.mouse.get_pos()
            world_pos = (mouse_pos[0] - self.camera.camera.x, mouse_pos[1] - self.camera.camera.y)
            
            for npc in self.npcs:
                if npc.rect.collidepoint(world_pos):
                    self.hud.select_npc(npc)
                    print(f"Selected NPC: {npc.name}")
                    break
    
    def _draw_events(self):
        """Draw beautiful event areas with decorations"""
        active_events = self.event_generator.get_active_events()
        
        # Import custom asset manager for event decorations
        from src.graphics.custom_asset_manager import CustomAssetManager
        assets = CustomAssetManager()
        
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
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0
            self.handle_events()
            self.update(dt)
            self.draw()
        
        self.cleanup()
        pygame.quit()
        sys.exit()
    
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
            # Loading complete, start the game
            self._start_new_game()
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
        
        # Create player with character data
        self.player = Player(400, 300, self.character_data)
        
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
                self.player = Player(400, 300, player_data)
            
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
    
    def _return_to_settings(self):
        self.game_state = "settings"
    
    def _api_keys_saved(self, key_data):
        print("API keys saved successfully!")
        # Reload AI configuration with new keys
        self._reload_ai_configuration()
    
    def _apply_settings(self, settings_dict):
        print("Settings applied:", settings_dict)
        # Apply settings to game components
        if hasattr(self, 'hud'):
            self.hud.show_debug = settings_dict.get("show_debug_info", False)
        
        # Apply auto-save interval
        self.auto_save_interval = settings_dict.get("auto_save_interval", 300)
        
        # Reload AI configuration if AI provider changed
        if self.npcs:  # Only if game is running with NPCs
            self._reload_ai_configuration()
    
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
    
    def cleanup(self):
        if self.memory_manager:
            self.memory_manager.close()
            print("Memory database saved and closed.")