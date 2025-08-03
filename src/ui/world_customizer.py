import pygame
import random
from typing import Dict, List, Callable
import src.core.constants as constants
from src.ui.menu import Button
from src.ui.npc_detail_editor import NPCDetailEditor

class WorldCustomizer:
    """Advanced world and NPC customization interface"""
    
    def __init__(self, screen):
        self.screen = screen
        self.font_title = pygame.font.Font(None, 32)
        self.font_subtitle = pygame.font.Font(None, 24)
        self.font_normal = pygame.font.Font(None, 20)
        
        # Current tab
        self.current_tab = "world"
        
        # World settings
        self.world_settings = {
            "world_size": "medium",  # small, medium, large
            "terrain_complexity": 0.5,  # 0-1
            "resource_density": 0.7,  # 0-1  
            "building_density": 0.6,  # 0-1
            "path_complexity": 0.5,  # 0-1
            "water_features": 0.3,  # 0-1
            "forest_coverage": 0.4,  # 0-1
        }
        
        # NPC settings
        self.npc_settings = {
            "npc_count": 5,  # 1-20
            "personality_variety": 0.8,  # 0-1
            "relationship_complexity": 0.6,  # 0-1
            "ai_frequency": 0.5,  # 0-1
            "social_events": 0.7,  # 0-1
        }
        
        # Individual NPCs
        self.custom_npcs = []
        self.selected_npc_index = -1
        
        # Performance settings
        self.performance_settings = {
            "graphics_quality": "medium",  # low, medium, high
            "fps_target": 30,  # 15, 30, 45, 60
            "ui_frequency": 1.0,  # 0.3, 0.6, 1.0
            "ai_optimization": True,
        }
        
        self._create_ui_elements()
        
        # Callbacks
        self.on_back = None
        self.on_apply_settings = None
        
        # NPC detail editor state
        self.npc_detail_editor = None
        self.editing_npc_index = -1
    
    def _create_ui_elements(self):
        """Create all UI elements"""
        center_x = constants.SCREEN_WIDTH // 2
        
        # Tab buttons
        self.tab_buttons = {
            "world": Button(center_x - 250, 50, 120, 40, "World", lambda: self._switch_tab("world"), 18),
            "npcs": Button(center_x - 120, 50, 120, 40, "NPCs", lambda: self._switch_tab("npcs"), 18),
            "performance": Button(center_x + 10, 50, 120, 40, "Performance", lambda: self._switch_tab("performance"), 18),
        }
        
        # World tab elements
        self._create_world_elements()
        
        # NPC tab elements  
        self._create_npc_elements()
        
        # Performance tab elements
        self._create_performance_elements()
        
        # Control buttons - positioned for current screen height
        button_y = constants.SCREEN_HEIGHT - 100
        self.apply_button = Button(center_x - 100, button_y, 120, 50, "Apply & Create", self._apply_settings)
        self.back_button = Button(50, button_y, 100, 40, "Back", self._back)
        self.random_button = Button(center_x + 50, button_y, 120, 50, "Randomize All", self._randomize_all)
    
    def _create_world_elements(self):
        """Create world customization elements"""
        self.world_elements = {
            "world_size": {
                "buttons": [
                    Button(150, 120, 80, 35, "Small", lambda: self._set_world_setting("world_size", "small"), 16),
                    Button(250, 120, 80, 35, "Medium", lambda: self._set_world_setting("world_size", "medium"), 16),
                    Button(350, 120, 80, 35, "Large", lambda: self._set_world_setting("world_size", "large"), 16),
                ]
            }
        }
        
        # World sliders
        self.world_sliders = {}
        slider_settings = [
            ("terrain_complexity", "Terrain Detail", 180),
            ("resource_density", "Resource Amount", 220), 
            ("building_density", "Buildings", 260),
            ("path_complexity", "Path Network", 300),
            ("water_features", "Water Features", 340),
            ("forest_coverage", "Forest Coverage", 380),
        ]
        
        for setting, label, y in slider_settings:
            self.world_sliders[setting] = WorldSlider(
                150, y, 300, 25, 0.0, 1.0, 
                self.world_settings[setting], label,
                lambda val, s=setting: self._set_world_setting(s, val)
            )
    
    def _create_npc_elements(self):
        """Create NPC customization elements"""
        # NPC count slider
        self.npc_count_slider = WorldSlider(
            150, 120, 300, 25, 1, 20,
            self.npc_settings["npc_count"], "Number of NPCs",
            lambda val: self._set_npc_setting("npc_count", int(val))
        )
        
        # NPC behavior sliders
        self.npc_sliders = {}
        npc_slider_settings = [
            ("personality_variety", "Personality Variety", 180),
            ("relationship_complexity", "Relationship Depth", 220),
            ("ai_frequency", "AI Response Speed", 260),
            ("social_events", "Social Events", 300),
        ]
        
        for setting, label, y in npc_slider_settings:
            self.npc_sliders[setting] = WorldSlider(
                150, y, 300, 25, 0.0, 1.0,
                self.npc_settings[setting], label,
                lambda val, s=setting: self._set_npc_setting(s, val)
            )
        
        # Individual NPC customization
        self.add_npc_button = Button(150, 350, 100, 35, "Add NPC", self._add_custom_npc, 16)
        self.remove_npc_button = Button(270, 350, 100, 35, "Remove", self._remove_custom_npc, 16)
        self.edit_npc_button = Button(390, 350, 100, 35, "Edit Selected", self._edit_custom_npc, 16)
        
        # Generate default NPCs
        self._generate_default_npcs()
    
    def _create_performance_elements(self):
        """Create performance customization elements"""
        self.performance_elements = {
            "graphics_quality": {
                "buttons": [
                    Button(150, 120, 80, 35, "Low", lambda: self._set_perf_setting("graphics_quality", "low"), 16),
                    Button(250, 120, 80, 35, "Medium", lambda: self._set_perf_setting("graphics_quality", "medium"), 16),
                    Button(350, 120, 80, 35, "High", lambda: self._set_perf_setting("graphics_quality", "high"), 16),
                ]
            },
            "fps_target": {
                "buttons": [
                    Button(150, 180, 60, 35, "15", lambda: self._set_perf_setting("fps_target", 15), 16),
                    Button(230, 180, 60, 35, "30", lambda: self._set_perf_setting("fps_target", 30), 16),
                    Button(310, 180, 60, 35, "45", lambda: self._set_perf_setting("fps_target", 45), 16),
                    Button(390, 180, 60, 35, "60", lambda: self._set_perf_setting("fps_target", 60), 16),
                ]
            }
        }
        
        # Performance sliders
        self.perf_ui_slider = WorldSlider(
            150, 240, 300, 25, 0.3, 1.0,
            self.performance_settings["ui_frequency"], "UI Update Rate",
            lambda val: self._set_perf_setting("ui_frequency", val)
        )
        
        # AI optimization toggle
        self.ai_opt_button = Button(150, 290, 200, 35, "AI Optimization: ON", self._toggle_ai_opt, 16)
    
    def _generate_default_npcs(self):
        """Generate default NPCs based on count setting"""
        self.custom_npcs.clear()
        
        default_names = [
            "Alice", "Bob", "Charlie", "Diana", "Eve", "Frank", "Grace", "Henry",
            "Iris", "Jack", "Kate", "Leo", "Maya", "Noah", "Olivia", "Paul",
            "Quinn", "Ruby", "Sam", "Tina"
        ]
        
        default_jobs = [
            "Farmer", "Shop Owner", "Teacher", "Doctor", "Artist", "Chef",
            "Librarian", "Mechanic", "Baker", "Musician", "Writer", "Gardener"
        ]
        
        personalities = [
            {"friendliness": 0.8, "energy": 0.6, "creativity": 0.4},
            {"friendliness": 0.5, "energy": 0.9, "creativity": 0.7},
            {"friendliness": 0.7, "energy": 0.3, "creativity": 0.9},
            {"friendliness": 0.3, "energy": 0.7, "creativity": 0.5},
            {"friendliness": 0.9, "energy": 0.5, "creativity": 0.6},
        ]
        
        count = min(self.npc_settings["npc_count"], len(default_names))
        
        for i in range(count):
            personality = personalities[i % len(personalities)].copy()
            
            # Add variety based on personality_variety setting
            variety = self.npc_settings["personality_variety"]
            for trait in personality:
                if variety > 0.5:
                    personality[trait] += random.uniform(-0.3, 0.3) * variety
                    personality[trait] = max(0.0, min(1.0, personality[trait]))
            
            # Enhanced NPC data for detailed editor
            npc_data = {
                "name": default_names[i],
                "age": random.randint(18, 65),
                "job": random.choice(default_jobs),
                "spec": random.choice(["Warrior", "Mage", "Rogue", "Healer", "Merchant", "Scholar", "Artisan", "Farmer"]),
                "backstory": f"A {random.choice(['friendly', 'mysterious', 'hardworking', 'creative'])} {random.choice(default_jobs).lower()} who has lived in the village for years.",
                "personality": personality,
                "skills": {
                    "Combat": random.randint(1, 8), "Magic": random.randint(1, 6), 
                    "Crafting": random.randint(1, 8), "Social": random.randint(3, 9),
                    "Knowledge": random.randint(2, 7), "Athletics": random.randint(1, 6),
                    "Stealth": random.randint(1, 5), "Medicine": random.randint(1, 4),
                    "Engineering": random.randint(1, 5), "Arts": random.randint(1, 7)
                },
                "skill_points": 50,
                "available_skill_points": 0,
                "home_location": f"House {i+1}",
                "relationships": {},
                "schedule": self._generate_schedule(),
                "interests": random.sample(["cooking", "music", "art", "sports", "reading", "gardening"], 3)
            }
            
            # Calculate available skill points
            total_used = sum(npc_data["skills"].values())
            npc_data["available_skill_points"] = max(0, npc_data["skill_points"] - total_used)
            
            self.custom_npcs.append(npc_data)
    
    def _generate_schedule(self):
        """Generate a basic daily schedule for an NPC"""
        return {
            "morning": "work",
            "afternoon": "socializing", 
            "evening": "relaxing",
            "night": "sleeping"
        }
    
    def _switch_tab(self, tab_name):
        """Switch to a different tab"""
        self.current_tab = tab_name
    
    def _set_world_setting(self, setting, value):
        """Update a world setting"""
        self.world_settings[setting] = value
    
    def _set_npc_setting(self, setting, value):
        """Update an NPC setting"""
        self.npc_settings[setting] = value
        if setting == "npc_count":
            self._generate_default_npcs()  # Regenerate NPCs when count changes
    
    def _set_perf_setting(self, setting, value):
        """Update a performance setting"""
        self.performance_settings[setting] = value
        if setting == "ai_optimization":
            self.ai_opt_button.text = f"AI Optimization: {'ON' if value else 'OFF'}"
    
    def _toggle_ai_opt(self):
        """Toggle AI optimization"""
        current = self.performance_settings["ai_optimization"]
        self._set_perf_setting("ai_optimization", not current)
    
    def _add_custom_npc(self):
        """Add a new custom NPC"""
        new_npc = {
            "name": f"Custom NPC {len(self.custom_npcs) + 1}",
            "job": "Villager",
            "personality": {"friendliness": 0.5, "energy": 0.5, "creativity": 0.5},
            "home_location": "New House",
            "relationships": {},
            "schedule": self._generate_schedule(),
            "interests": ["socializing"]
        }
        self.custom_npcs.append(new_npc)
        self.npc_settings["npc_count"] = len(self.custom_npcs)
    
    def _remove_custom_npc(self):
        """Remove selected NPC"""
        if 0 <= self.selected_npc_index < len(self.custom_npcs):
            self.custom_npcs.pop(self.selected_npc_index)
            self.selected_npc_index = -1
            self.npc_settings["npc_count"] = len(self.custom_npcs)
    
    def _edit_custom_npc(self):
        """Edit the selected NPC with detailed editor"""
        if 0 <= self.selected_npc_index < len(self.custom_npcs):
            self.editing_npc_index = self.selected_npc_index
            npc_data = self.custom_npcs[self.selected_npc_index].copy()
            
            self.npc_detail_editor = NPCDetailEditor(self.screen, npc_data)
            self.npc_detail_editor.on_save = self._save_edited_npc
            self.npc_detail_editor.on_cancel = self._cancel_npc_edit
    
    def _save_edited_npc(self, npc_data):
        """Save the edited NPC data"""
        if 0 <= self.editing_npc_index < len(self.custom_npcs):
            self.custom_npcs[self.editing_npc_index] = npc_data
        self.npc_detail_editor = None
        self.editing_npc_index = -1
    
    def _cancel_npc_edit(self):
        """Cancel NPC editing"""
        self.npc_detail_editor = None
        self.editing_npc_index = -1
    
    def _randomize_all(self):
        """Randomize all settings"""
        # Randomize world settings
        for setting in self.world_settings:
            if setting == "world_size":
                self.world_settings[setting] = random.choice(["small", "medium", "large"])
            else:
                self.world_settings[setting] = random.uniform(0.2, 0.8)
        
        # Randomize NPC settings
        self.npc_settings["npc_count"] = random.randint(3, 12)
        for setting in ["personality_variety", "relationship_complexity", "ai_frequency", "social_events"]:
            self.npc_settings[setting] = random.uniform(0.3, 0.9)
        
        # Randomize performance settings
        self.performance_settings["graphics_quality"] = random.choice(["low", "medium", "high"])
        self.performance_settings["fps_target"] = random.choice([15, 30, 45, 60])
        self.performance_settings["ui_frequency"] = random.uniform(0.5, 1.0)
        
        # Regenerate NPCs and update sliders
        self._generate_default_npcs()
        self._update_slider_values()
    
    def _update_slider_values(self):
        """Update all slider values after randomization"""
        for setting, slider in self.world_sliders.items():
            slider.val = self.world_settings[setting]
        
        for setting, slider in self.npc_sliders.items():
            slider.val = self.npc_settings[setting]
        
        self.npc_count_slider.val = self.npc_settings["npc_count"]
        self.perf_ui_slider.val = self.performance_settings["ui_frequency"]
    
    def _apply_settings(self):
        """Apply all settings and create the world"""
        if self.on_apply_settings:
            settings_data = {
                "world": self.world_settings,
                "npcs": self.npc_settings,
                "custom_npcs": self.custom_npcs,
                "performance": self.performance_settings
            }
            self.on_apply_settings(settings_data)
    
    def _back(self):
        """Go back to character creation"""
        if self.on_back:
            self.on_back()
    
    def handle_event(self, event):
        """Handle input events"""
        # If NPC detail editor is open, handle its events first
        if self.npc_detail_editor:
            return self.npc_detail_editor.handle_event(event)
        
        # Tab buttons
        for button in self.tab_buttons.values():
            if button.handle_event(event):
                return True
        
        # Current tab content - don't return early, let control buttons process too
        handled = False
        if self.current_tab == "world":
            handled = self._handle_world_events(event)
        elif self.current_tab == "npcs":
            handled = self._handle_npc_events(event)
        elif self.current_tab == "performance":
            handled = self._handle_performance_events(event)
        
        # If tab content handled the event, return early
        if handled:
            return True
        
        # Control buttons
        if self.apply_button.handle_event(event):
            return True
        if self.back_button.handle_event(event):
            return True
        if self.random_button.handle_event(event):
            return True
        
        return False
    
    def _handle_world_events(self, event):
        """Handle world tab events"""
        # World size buttons
        for button in self.world_elements["world_size"]["buttons"]:
            if button.handle_event(event):
                return True
        
        # World sliders
        for slider in self.world_sliders.values():
            if slider.handle_event(event):
                return True
        
        return False
    
    def _handle_npc_events(self, event):
        """Handle NPC tab events"""
        # NPC count slider
        if self.npc_count_slider.handle_event(event):
            return True
        
        # NPC behavior sliders
        for slider in self.npc_sliders.values():
            if slider.handle_event(event):
                return True
        
        # NPC management buttons
        if self.add_npc_button.handle_event(event):
            return True
        if self.remove_npc_button.handle_event(event):
            return True
        if self.edit_npc_button.handle_event(event):
            return True
        
        # NPC list selection
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = event.pos
            if 500 <= mouse_x <= 750 and 120 <= mouse_y <= 500:
                # Calculate which NPC was clicked
                npc_index = (mouse_y - 120) // 30
                if 0 <= npc_index < len(self.custom_npcs):
                    self.selected_npc_index = npc_index
                    return True
        
        return False
    
    def _handle_performance_events(self, event):
        """Handle performance tab events"""
        # Graphics quality buttons
        for button in self.performance_elements["graphics_quality"]["buttons"]:
            if button.handle_event(event):
                return True
        
        # FPS target buttons
        for button in self.performance_elements["fps_target"]["buttons"]:
            if button.handle_event(event):
                return True
        
        # UI frequency slider
        if self.perf_ui_slider.handle_event(event):
            return True
        
        # AI optimization toggle
        if self.ai_opt_button.handle_event(event):
            return True
        
        return False
    
    def draw(self):
        """Draw the customization interface"""
        # If NPC detail editor is open, draw it instead
        if self.npc_detail_editor:
            self.npc_detail_editor.draw()
            return
        
        self.screen.fill((25, 35, 45))
        
        # Title
        title_text = self.font_title.render("Advanced World & NPC Customization", True, constants.WHITE)
        title_rect = title_text.get_rect(center=(constants.SCREEN_WIDTH // 2, 25))
        self.screen.blit(title_text, title_rect)
        
        # Tab buttons
        for tab_name, button in self.tab_buttons.items():
            # Highlight active tab
            if tab_name == self.current_tab:
                highlight_rect = pygame.Rect(button.rect.x - 2, button.rect.y - 2, 
                                           button.rect.width + 4, button.rect.height + 4)
                pygame.draw.rect(self.screen, (100, 150, 200), highlight_rect, border_radius=5)
            button.draw(self.screen)
        
        # Draw current tab content
        if self.current_tab == "world":
            self._draw_world_tab()
        elif self.current_tab == "npcs":
            self._draw_npc_tab()
        elif self.current_tab == "performance":
            self._draw_performance_tab()
        
        # Control buttons
        self.apply_button.draw(self.screen)
        self.back_button.draw(self.screen)
        self.random_button.draw(self.screen)
    
    def _draw_world_tab(self):
        """Draw world customization tab"""
        # World size section
        size_label = self.font_subtitle.render("World Size:", True, constants.WHITE)
        self.screen.blit(size_label, (50, 125))
        
        for button in self.world_elements["world_size"]["buttons"]:
            # Highlight selected option
            if (button.text.lower() == self.world_settings["world_size"]):
                highlight_rect = pygame.Rect(button.rect.x - 2, button.rect.y - 2,
                                           button.rect.width + 4, button.rect.height + 4)
                pygame.draw.rect(self.screen, (100, 200, 100), highlight_rect, border_radius=3)
            button.draw(self.screen)
        
        # World setting sliders
        for slider in self.world_sliders.values():
            slider.draw(self.screen)
        
        # World preview (placeholder)
        preview_rect = pygame.Rect(500, 120, 250, 200)
        pygame.draw.rect(self.screen, (40, 60, 40), preview_rect)
        pygame.draw.rect(self.screen, constants.WHITE, preview_rect, 2)
        
        preview_text = self.font_normal.render("World Preview", True, constants.WHITE)
        preview_text_rect = preview_text.get_rect(center=preview_rect.center)
        self.screen.blit(preview_text, preview_text_rect)
        
        # World info summary
        info_y = 350
        info_texts = [
            f"Size: {self.world_settings['world_size'].title()}",
            f"Terrain Detail: {self.world_settings['terrain_complexity']:.1f}",
            f"Resources: {self.world_settings['resource_density']:.1f}",
            f"Buildings: {self.world_settings['building_density']:.1f}",
        ]
        
        for i, text in enumerate(info_texts):
            info_surface = self.font_normal.render(text, True, (200, 200, 200))
            self.screen.blit(info_surface, (500, info_y + i * 25))
    
    def _draw_npc_tab(self):
        """Draw NPC customization tab"""
        # NPC count slider
        self.npc_count_slider.draw(self.screen)
        
        # NPC behavior sliders
        for slider in self.npc_sliders.values():
            slider.draw(self.screen)
        
        # NPC management buttons
        self.add_npc_button.draw(self.screen)
        self.remove_npc_button.draw(self.screen)
        self.edit_npc_button.draw(self.screen)
        
        # NPC list
        list_title = self.font_subtitle.render("Custom NPCs:", True, constants.WHITE)
        self.screen.blit(list_title, (500, 95))
        
        list_rect = pygame.Rect(500, 120, 250, 380)
        pygame.draw.rect(self.screen, (30, 30, 30), list_rect)
        pygame.draw.rect(self.screen, constants.WHITE, list_rect, 2)
        
        # Draw NPC entries
        for i, npc in enumerate(self.custom_npcs):
            y = 125 + i * 30
            if y > 495:  # Don't draw beyond the list area
                break
            
            # Highlight selected NPC
            if i == self.selected_npc_index:
                highlight_rect = pygame.Rect(505, y - 2, 240, 26)
                pygame.draw.rect(self.screen, (100, 100, 200), highlight_rect)
            
            # NPC name and job
            name_text = self.font_normal.render(f"{npc['name']}", True, constants.WHITE)
            job_text = self.font_normal.render(f"({npc['job']})", True, (150, 150, 150))
            
            self.screen.blit(name_text, (510, y))
            self.screen.blit(job_text, (510, y + 12))
        
        # Instructions
        inst_text = self.font_normal.render("Click NPCs to select", True, (120, 120, 120))
        self.screen.blit(inst_text, (500, 510))
    
    def _draw_performance_tab(self):
        """Draw performance customization tab"""
        # Graphics quality section
        gfx_label = self.font_subtitle.render("Graphics Quality:", True, constants.WHITE)
        self.screen.blit(gfx_label, (50, 125))
        
        for button in self.performance_elements["graphics_quality"]["buttons"]:
            if button.text.lower() == self.performance_settings["graphics_quality"]:
                highlight_rect = pygame.Rect(button.rect.x - 2, button.rect.y - 2,
                                           button.rect.width + 4, button.rect.height + 4)
                pygame.draw.rect(self.screen, (100, 200, 100), highlight_rect, border_radius=3)
            button.draw(self.screen)
        
        # FPS target section
        fps_label = self.font_subtitle.render("Target FPS:", True, constants.WHITE)
        self.screen.blit(fps_label, (50, 185))
        
        for button in self.performance_elements["fps_target"]["buttons"]:
            if int(button.text) == self.performance_settings["fps_target"]:
                highlight_rect = pygame.Rect(button.rect.x - 2, button.rect.y - 2,
                                           button.rect.width + 4, button.rect.height + 4)
                pygame.draw.rect(self.screen, (100, 200, 100), highlight_rect, border_radius=3)
            button.draw(self.screen)
        
        # UI frequency slider
        self.perf_ui_slider.draw(self.screen)
        
        # AI optimization toggle
        self.ai_opt_button.draw(self.screen)
        
        # Performance info
        info_y = 350
        info_texts = [
            f"Graphics: {self.performance_settings['graphics_quality'].title()}",
            f"Target FPS: {self.performance_settings['fps_target']}",
            f"UI Rate: {self.performance_settings['ui_frequency']:.1f}",
            f"AI Opt: {'Enabled' if self.performance_settings['ai_optimization'] else 'Disabled'}",
        ]
        
        for i, text in enumerate(info_texts):
            info_surface = self.font_normal.render(text, True, (200, 200, 200))
            self.screen.blit(info_surface, (500, info_y + i * 25))


class WorldSlider:
    """Enhanced slider for world customization"""
    
    def __init__(self, x, y, width, height, min_val, max_val, initial_val, label, on_change=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.min_val = min_val
        self.max_val = max_val
        self.val = initial_val
        self.label = label
        self.on_change = on_change
        self.dragging = False
        self.font = pygame.font.Font(None, 18)
    
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and self.rect.collidepoint(event.pos):
                self.dragging = True
                self._update_value(event.pos[0])
                return True
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                self.dragging = False
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            self._update_value(event.pos[0])
            return True
        return False
    
    def _update_value(self, mouse_x):
        relative_x = mouse_x - self.rect.x
        relative_x = max(0, min(relative_x, self.rect.width))
        old_val = self.val
        self.val = self.min_val + (relative_x / self.rect.width) * (self.max_val - self.min_val)
        
        if self.on_change and abs(old_val - self.val) > 0.01:
            self.on_change(self.val)
    
    def draw(self, screen):
        # Draw label
        label_text = self.font.render(self.label, True, constants.WHITE)
        screen.blit(label_text, (self.rect.x, self.rect.y - 20))
        
        # Draw slider track
        pygame.draw.rect(screen, (60, 60, 60), self.rect, border_radius=3)
        pygame.draw.rect(screen, (120, 120, 120), self.rect, 2, border_radius=3)
        
        # Draw filled portion
        fill_width = (self.val - self.min_val) / (self.max_val - self.min_val) * self.rect.width
        fill_rect = pygame.Rect(self.rect.x, self.rect.y, fill_width, self.rect.height)
        pygame.draw.rect(screen, (100, 150, 200), fill_rect, border_radius=3)
        
        # Draw handle
        handle_x = self.rect.x + fill_width
        handle_rect = pygame.Rect(handle_x - 6, self.rect.y - 2, 12, self.rect.height + 4)
        pygame.draw.rect(screen, (200, 200, 200), handle_rect, border_radius=6)
        
        # Draw value
        if isinstance(self.val, int):
            value_text = str(self.val)
        else:
            value_text = f"{self.val:.2f}"
        
        value_surface = self.font.render(value_text, True, constants.WHITE)
        value_rect = value_surface.get_rect()
        value_rect.center = (self.rect.right + 30, self.rect.centery)
        screen.blit(value_surface, value_rect)