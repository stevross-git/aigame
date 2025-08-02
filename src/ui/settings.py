import pygame
import json
import os
from typing import Dict, Callable, Any
from src.core.constants import *
from src.ui.menu import Button
from src.ui.character_creator import Slider

class ToggleButton(Button):
    def __init__(self, x, y, width, height, label, initial_value=False, callback=None):
        self.value = initial_value
        self.label = label
        self.toggle_callback = callback
        
        text = f"{label}: {'ON' if initial_value else 'OFF'}"
        super().__init__(x, y, width, height, text, self._toggle)
    
    def _toggle(self):
        self.value = not self.value
        self.text = f"{self.label}: {'ON' if self.value else 'OFF'}"
        if self.toggle_callback:
            self.toggle_callback(self.value)

class DropdownButton(Button):
    def __init__(self, x, y, width, height, label, options, initial_index=0, callback=None):
        self.label = label
        self.options = options
        self.current_index = initial_index
        self.dropdown_callback = callback
        
        text = f"{label}: {options[initial_index]}"
        super().__init__(x, y, width, height, text, self._cycle)
    
    def _cycle(self):
        self.current_index = (self.current_index + 1) % len(self.options)
        self.text = f"{self.label}: {self.options[self.current_index]}"
        if self.dropdown_callback:
            self.dropdown_callback(self.options[self.current_index])

class Settings:
    def __init__(self):
        self.settings_file = "settings.json"
        self.settings = self._load_settings()
    
    def _load_settings(self) -> Dict[str, Any]:
        default_settings = {
            # Graphics
            "fullscreen": False,
            "vsync": True,
            "fps_limit": 60,
            "show_fps": True,
            "camera_smoothing": True,
            
            # Audio
            "master_volume": 1.0,
            "music_volume": 0.7,
            "sfx_volume": 0.8,
            "mute_audio": False,
            
            # AI Settings
            "ai_provider": "Ollama",
            "ollama_model": "llama2",
            "ai_decision_speed": "Normal",
            "ollama_timeout": 5.0,
            "enable_api_fallback": True,
            
            # Gameplay
            "auto_save_interval": 300,
            "show_debug_info": False,
            "npc_interaction_frequency": "Normal",
            "event_frequency": "Normal",
            "memory_retention": "High",
            
            # UI
            "show_speech_bubbles": True,
            "show_npc_names": True,
            "show_needs_bars": True,
            "ui_scale": 1.0,
            "colorblind_mode": False,
            
            # Performance
            "max_npcs": 10,
            "memory_cleanup_interval": 600,
            "low_performance_mode": False,
            "reduce_ai_frequency": False,
        }
        
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r') as f:
                    saved_settings = json.load(f)
                    default_settings.update(saved_settings)
        except Exception as e:
            print(f"Error loading settings: {e}")
        
        return default_settings
    
    def save_settings(self):
        try:
            with open(self.settings_file, 'w') as f:
                json.dump(self.settings, f, indent=2)
        except Exception as e:
            print(f"Error saving settings: {e}")
    
    def get(self, key: str, default=None):
        return self.settings.get(key, default)
    
    def set(self, key: str, value: Any):
        self.settings[key] = value
        self.save_settings()

class SettingsMenu:
    def __init__(self, screen):
        self.screen = screen
        self.font_title = pygame.font.Font(None, 48)
        self.font_section = pygame.font.Font(None, 32)
        self.font_label = pygame.font.Font(None, 24)
        
        self.settings = Settings()
        self.current_tab = "Graphics"
        self.scroll_offset = 0
        
        # Create tab buttons
        tab_width = 100
        tab_y = 80
        self.tabs = ["Graphics", "Audio", "AI", "API Keys", "Gameplay", "Performance"]
        self.tab_buttons = []
        
        for i, tab in enumerate(self.tabs):
            x = 50 + i * (tab_width + 10)
            button = Button(x, tab_y, tab_width, 35, tab, lambda t=tab: self._switch_tab(t), 20)
            self.tab_buttons.append(button)
        
        # Control buttons
        self.back_button = Button(50, SCREEN_HEIGHT - 70, 100, 40, "Back", self._back)
        self.reset_button = Button(170, SCREEN_HEIGHT - 70, 120, 40, "Reset All", self._reset_all)
        self.api_keys_button = Button(310, SCREEN_HEIGHT - 70, 120, 40, "Manage Keys", self._manage_api_keys)
        self.apply_button = Button(SCREEN_WIDTH - 200, SCREEN_HEIGHT - 70, 120, 40, "Apply & Save", self._apply_settings)
        
        # Callbacks
        self.on_back = None
        self.on_apply = None
        self.on_manage_api_keys = None
        
        self._create_controls()
    
    def _switch_tab(self, tab):
        self.current_tab = tab
        self.scroll_offset = 0
        self._create_controls()
    
    def _create_controls(self):
        self.controls = []
        start_y = 140
        y_offset = start_y
        
        if self.current_tab == "Graphics":
            self.controls.extend([
                ToggleButton(50, y_offset, 200, 35, "Fullscreen", 
                           self.settings.get("fullscreen"), 
                           lambda v: self.settings.set("fullscreen", v)),
                
                ToggleButton(280, y_offset, 200, 35, "V-Sync", 
                           self.settings.get("vsync"),
                           lambda v: self.settings.set("vsync", v)),
                
                ToggleButton(50, y_offset + 50, 200, 35, "Show FPS", 
                           self.settings.get("show_fps"),
                           lambda v: self.settings.set("show_fps", v)),
                
                ToggleButton(280, y_offset + 50, 200, 35, "Camera Smoothing", 
                           self.settings.get("camera_smoothing"),
                           lambda v: self.settings.set("camera_smoothing", v)),
                
                DropdownButton(50, y_offset + 100, 200, 35, "FPS Limit", 
                             ["30", "60", "120", "Unlimited"], 
                             ["30", "60", "120", "Unlimited"].index(str(self.settings.get("fps_limit", 60))),
                             lambda v: self.settings.set("fps_limit", int(v) if v != "Unlimited" else -1)),
                
                DropdownButton(280, y_offset + 100, 200, 35, "UI Scale", 
                             ["0.8x", "1.0x", "1.2x", "1.5x"],
                             int((self.settings.get("ui_scale", 1.0) - 0.8) / 0.2),
                             lambda v: self.settings.set("ui_scale", 0.8 + ["0.8x", "1.0x", "1.2x", "1.5x"].index(v) * 0.2)),
                
                ToggleButton(50, y_offset + 150, 200, 35, "Colorblind Mode", 
                           self.settings.get("colorblind_mode"),
                           lambda v: self.settings.set("colorblind_mode", v)),
            ])
        
        elif self.current_tab == "Audio":
            # Volume sliders
            master_slider = Slider(50, y_offset + 30, 300, 20, 0.0, 1.0, 
                                 self.settings.get("master_volume", 1.0), "Master Volume")
            master_slider.on_change = lambda v: self.settings.set("master_volume", v)
            
            music_slider = Slider(50, y_offset + 80, 300, 20, 0.0, 1.0,
                                self.settings.get("music_volume", 0.7), "Music Volume")
            music_slider.on_change = lambda v: self.settings.set("music_volume", v)
            
            sfx_slider = Slider(50, y_offset + 130, 300, 20, 0.0, 1.0,
                              self.settings.get("sfx_volume", 0.8), "SFX Volume")
            sfx_slider.on_change = lambda v: self.settings.set("sfx_volume", v)
            
            self.controls.extend([
                master_slider,
                music_slider,
                sfx_slider,
                ToggleButton(50, y_offset + 180, 200, 35, "Mute Audio", 
                           self.settings.get("mute_audio"),
                           lambda v: self.settings.set("mute_audio", v)),
            ])
        
        elif self.current_tab == "AI":
            self.controls.extend([
                DropdownButton(50, y_offset, 250, 35, "AI Provider", 
                             ["Ollama", "OpenAI", "Claude", "Auto"], 
                             ["Ollama", "OpenAI", "Claude", "Auto"].index(self.settings.get("ai_provider", "Ollama")),
                             lambda v: self.settings.set("ai_provider", v)),
                
                DropdownButton(50, y_offset + 50, 250, 35, "Ollama Model", 
                             ["llama2", "llama2:7b", "llama2:13b", "codellama"],
                             ["llama2", "llama2:7b", "llama2:13b", "codellama"].index(self.settings.get("ollama_model", "llama2")),
                             lambda v: self.settings.set("ollama_model", v)),
                
                DropdownButton(50, y_offset + 100, 250, 35, "Decision Speed", 
                             ["Very Fast", "Fast", "Normal", "Slow", "Very Slow"],
                             ["Very Fast", "Fast", "Normal", "Slow", "Very Slow"].index(self.settings.get("ai_decision_speed", "Normal")),
                             lambda v: self.settings.set("ai_decision_speed", v)),
                
                ToggleButton(50, y_offset + 150, 250, 35, "API Fallback", 
                           self.settings.get("enable_api_fallback"),
                           lambda v: self.settings.set("enable_api_fallback", v)),
            ])
            
            # Timeout slider
            timeout_slider = Slider(50, y_offset + 220, 300, 20, 1.0, 15.0,
                                  self.settings.get("ollama_timeout", 5.0), "Ollama Timeout (seconds)")
            timeout_slider.on_change = lambda v: self.settings.set("ollama_timeout", v)
            self.controls.append(timeout_slider)
        
        elif self.current_tab == "API Keys":
            # API key status display
            api_key_status = self._get_api_key_status()
            
            status_y = y_offset + 20
            for provider, status in api_key_status.items():
                status_color = (100, 255, 100) if status["configured"] else (255, 100, 100)
                status_text = "✅ Configured" if status["configured"] else "❌ Not configured"
                
                # This is just display - actual management happens in separate window
                provider_button = Button(50, status_y, 300, 35, 
                                       f"{provider}: {status_text}", 
                                       lambda: None)  # No action, just display
                provider_button.enabled = False  # Make it non-clickable
                self.controls.append(provider_button)
                status_y += 50
            
            # Instructions
            info_text = [
                "Use 'Manage Keys' button below to:",
                "• Add OpenAI API key for GPT models",
                "• Add Anthropic API key for Claude",  
                "• Configure custom API endpoints",
                "• Test key validity before saving",
                "",
                "Keys are stored securely in .env file"
            ]
            
            info_y = status_y + 20
            for line in info_text:
                # Create fake button for text display
                if line.strip():
                    text_display = Button(50, info_y, 400, 25, line, lambda: None, 18)
                    text_display.enabled = False
                    self.controls.append(text_display)
                info_y += 25
        
        elif self.current_tab == "Gameplay":
            self.controls.extend([
                DropdownButton(50, y_offset, 250, 35, "Auto-Save Interval", 
                             ["1 min", "5 min", "10 min", "30 min", "Never"],
                             [60, 300, 600, 1800, -1].index(self.settings.get("auto_save_interval", 300)),
                             lambda v: self.settings.set("auto_save_interval", 
                                                       [60, 300, 600, 1800, -1][["1 min", "5 min", "10 min", "30 min", "Never"].index(v)])),
                
                DropdownButton(50, y_offset + 50, 250, 35, "NPC Interactions", 
                             ["Very Rare", "Rare", "Normal", "Frequent", "Very Frequent"],
                             ["Very Rare", "Rare", "Normal", "Frequent", "Very Frequent"].index(self.settings.get("npc_interaction_frequency", "Normal")),
                             lambda v: self.settings.set("npc_interaction_frequency", v)),
                
                DropdownButton(50, y_offset + 100, 250, 35, "Event Frequency", 
                             ["Very Rare", "Rare", "Normal", "Frequent", "Very Frequent"],
                             ["Very Rare", "Rare", "Normal", "Frequent", "Very Frequent"].index(self.settings.get("event_frequency", "Normal")),
                             lambda v: self.settings.set("event_frequency", v)),
                
                DropdownButton(50, y_offset + 150, 250, 35, "Memory Retention", 
                             ["Low", "Medium", "High", "Maximum"],
                             ["Low", "Medium", "High", "Maximum"].index(self.settings.get("memory_retention", "High")),
                             lambda v: self.settings.set("memory_retention", v)),
                
                ToggleButton(50, y_offset + 200, 250, 35, "Show Debug Info", 
                           self.settings.get("show_debug_info"),
                           lambda v: self.settings.set("show_debug_info", v)),
                
                ToggleButton(50, y_offset + 250, 250, 35, "Speech Bubbles", 
                           self.settings.get("show_speech_bubbles"),
                           lambda v: self.settings.set("show_speech_bubbles", v)),
                
                ToggleButton(50, y_offset + 300, 250, 35, "NPC Names", 
                           self.settings.get("show_npc_names"),
                           lambda v: self.settings.set("show_npc_names", v)),
                
                ToggleButton(50, y_offset + 350, 250, 35, "Needs Bars", 
                           self.settings.get("show_needs_bars"),
                           lambda v: self.settings.set("show_needs_bars", v)),
            ])
        
        elif self.current_tab == "Performance":
            self.controls.extend([
                DropdownButton(50, y_offset, 200, 35, "Max NPCs", 
                             ["5", "10", "15", "20", "25"],
                             ["5", "10", "15", "20", "25"].index(str(self.settings.get("max_npcs", 10))),
                             lambda v: self.settings.set("max_npcs", int(v))),
                
                ToggleButton(50, y_offset + 50, 250, 35, "Low Performance Mode", 
                           self.settings.get("low_performance_mode"),
                           lambda v: self.settings.set("low_performance_mode", v)),
                
                ToggleButton(50, y_offset + 100, 250, 35, "Reduce AI Frequency", 
                           self.settings.get("reduce_ai_frequency"),
                           lambda v: self.settings.set("reduce_ai_frequency", v)),
            ])
            
            # Memory cleanup slider
            cleanup_slider = Slider(50, y_offset + 170, 300, 20, 60, 1800,
                                  self.settings.get("memory_cleanup_interval", 600), "Memory Cleanup (seconds)")
            cleanup_slider.on_change = lambda v: self.settings.set("memory_cleanup_interval", int(v))
            self.controls.append(cleanup_slider)
    
    def _back(self):
        if self.on_back:
            self.on_back()
    
    def _reset_all(self):
        # Reset to defaults
        if os.path.exists(self.settings.settings_file):
            os.remove(self.settings.settings_file)
        self.settings = Settings()
        self._create_controls()
    
    def _apply_settings(self):
        self.settings.save_settings()
        if self.on_apply:
            self.on_apply(self.settings.settings)
    
    def _manage_api_keys(self):
        if self.on_manage_api_keys:
            self.on_manage_api_keys()
    
    def _get_api_key_status(self):
        """Check which API keys are configured"""
        import os
        
        status = {}
        env_file = ".env"
        
        # Default status
        keys_to_check = {
            "OpenAI": "OPENAI_API_KEY",
            "Anthropic": "ANTHROPIC_API_KEY", 
            "Custom API": "CUSTOM_API_KEY"
        }
        
        for display_name, env_key in keys_to_check.items():
            status[display_name] = {"configured": False, "valid": False}
        
        # Check .env file
        if os.path.exists(env_file):
            try:
                with open(env_file, 'r') as f:
                    content = f.read()
                    
                for display_name, env_key in keys_to_check.items():
                    if f"{env_key}=" in content:
                        # Extract value to check if it's not empty
                        for line in content.split('\n'):
                            if line.strip().startswith(f"{env_key}="):
                                value = line.split('=', 1)[1].strip().strip('"\'')
                                if value and len(value) > 10:  # Basic length check
                                    status[display_name]["configured"] = True
                                break
            except Exception as e:
                print(f"Error checking API keys: {e}")
        
        return status
    
    def handle_event(self, event):
        # Handle tab buttons
        for button in self.tab_buttons:
            if button.handle_event(event):
                return True
        
        # Handle control buttons
        if self.back_button.handle_event(event):
            return True
        if self.reset_button.handle_event(event):
            return True
        if self.api_keys_button.handle_event(event):
            return True
        if self.apply_button.handle_event(event):
            return True
        
        # Handle current tab controls
        for control in self.controls:
            if hasattr(control, 'handle_event') and control.handle_event(event):
                return True
        
        # Handle scrolling
        if event.type == pygame.MOUSEWHEEL:
            self.scroll_offset -= event.y * 30
            self.scroll_offset = max(0, min(self.scroll_offset, max(0, len(self.controls) * 60 - 400)))
            return True
        
        return False
    
    def draw(self):
        self.screen.fill((25, 35, 45))
        
        # Title
        title_text = self.font_title.render("Settings", True, WHITE)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, 40))
        self.screen.blit(title_text, title_rect)
        
        # Tab buttons
        for i, button in enumerate(self.tab_buttons):
            if self.tabs[i] == self.current_tab:
                # Highlight current tab
                pygame.draw.rect(self.screen, (70, 130, 180), button.rect, border_radius=5)
                button.draw(self.screen)
                pygame.draw.rect(self.screen, (200, 200, 200), button.rect, 2, border_radius=5)
            else:
                button.draw(self.screen)
        
        # Settings area background
        settings_rect = pygame.Rect(30, 130, SCREEN_WIDTH - 60, SCREEN_HEIGHT - 220)
        pygame.draw.rect(self.screen, (35, 45, 55), settings_rect, border_radius=10)
        pygame.draw.rect(self.screen, (80, 80, 80), settings_rect, 2, border_radius=10)
        
        # Current tab content
        self._draw_tab_content()
        
        # Control buttons
        self.back_button.draw(self.screen)
        self.reset_button.draw(self.screen)
        self.api_keys_button.draw(self.screen)
        self.apply_button.draw(self.screen)
        
        # Help text
        help_text = self.font_label.render(f"Current Tab: {self.current_tab} | Scroll with mouse wheel", True, (150, 150, 150))
        help_rect = help_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 25))
        self.screen.blit(help_text, help_rect)
    
    def _draw_tab_content(self):
        # Create clipping area for scrolling
        clip_rect = pygame.Rect(50, 150, SCREEN_WIDTH - 100, SCREEN_HEIGHT - 250)
        self.screen.set_clip(clip_rect)
        
        # Draw controls with scroll offset
        for i, control in enumerate(self.controls):
            # Adjust position for scrolling
            if hasattr(control, 'rect'):
                original_y = control.rect.y
                control.rect.y = original_y - self.scroll_offset
                
                # Only draw if visible
                if control.rect.bottom > 150 and control.rect.top < SCREEN_HEIGHT - 100:
                    control.draw(self.screen)
                
                # Restore original position
                control.rect.y = original_y
        
        # Remove clipping
        self.screen.set_clip(None)
        
        # Draw scroll indicator
        if len(self.controls) * 60 > 400:
            scrollbar_height = 300
            scrollbar_y = 150
            scrollbar_x = SCREEN_WIDTH - 45
            
            # Scrollbar background
            pygame.draw.rect(self.screen, (60, 60, 60), 
                           (scrollbar_x, scrollbar_y, 10, scrollbar_height))
            
            # Scrollbar handle
            max_scroll = max(0, len(self.controls) * 60 - 400)
            if max_scroll > 0:
                handle_height = max(20, int(scrollbar_height * (400 / (len(self.controls) * 60))))
                handle_y = scrollbar_y + int((self.scroll_offset / max_scroll) * (scrollbar_height - handle_height))
                pygame.draw.rect(self.screen, (120, 120, 120), 
                               (scrollbar_x, handle_y, 10, handle_height))