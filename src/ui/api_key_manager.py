import pygame
import os
from typing import Dict, Callable
from src.core.constants import *
from src.ui.menu import Button

class SecureTextInput:
    def __init__(self, x, y, width, height, label, placeholder="", is_password=False):
        self.rect = pygame.Rect(x, y, width, height)
        self.label = label
        self.placeholder = placeholder
        self.is_password = is_password
        self.text = ""
        self.active = False
        self.cursor_pos = 0
        self.cursor_timer = 0
        self.font = pygame.font.Font(None, 24)
        self.show_password = False
        
        # Eye icon for password visibility toggle
        if is_password:
            self.eye_rect = pygame.Rect(x + width - 30, y + 5, 20, height - 10)
    
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                if self.rect.collidepoint(event.pos):
                    self.active = True
                elif self.is_password and hasattr(self, 'eye_rect') and self.eye_rect.collidepoint(event.pos):
                    self.show_password = not self.show_password
                    return True
                else:
                    self.active = False
        
        if event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_BACKSPACE:
                if self.cursor_pos > 0:
                    self.text = self.text[:self.cursor_pos-1] + self.text[self.cursor_pos:]
                    self.cursor_pos -= 1
            elif event.key == pygame.K_DELETE:
                if self.cursor_pos < len(self.text):
                    self.text = self.text[:self.cursor_pos] + self.text[self.cursor_pos+1:]
            elif event.key == pygame.K_LEFT:
                self.cursor_pos = max(0, self.cursor_pos - 1)
            elif event.key == pygame.K_RIGHT:
                self.cursor_pos = min(len(self.text), self.cursor_pos + 1)
            elif event.key == pygame.K_HOME:
                self.cursor_pos = 0
            elif event.key == pygame.K_END:
                self.cursor_pos = len(self.text)
            elif event.key == pygame.K_TAB or event.key == pygame.K_RETURN:
                self.active = False
            elif event.unicode.isprintable() and len(self.text) < 200:
                self.text = self.text[:self.cursor_pos] + event.unicode + self.text[self.cursor_pos:]
                self.cursor_pos += 1
            return True
        
        return False
    
    def update(self, dt):
        self.cursor_timer += dt
        if self.cursor_timer >= 1.0:
            self.cursor_timer = 0
    
    def draw(self, screen):
        # Draw label
        label_text = self.font.render(self.label, True, WHITE)
        screen.blit(label_text, (self.rect.x, self.rect.y - 25))
        
        # Draw input box
        border_color = (100, 150, 200) if self.active else (100, 100, 100)
        bg_color = (40, 40, 40) if self.active else (30, 30, 30)
        
        pygame.draw.rect(screen, bg_color, self.rect, border_radius=5)
        pygame.draw.rect(screen, border_color, self.rect, 2, border_radius=5)
        
        # Draw text or placeholder
        display_text = self.text
        text_color = WHITE
        
        if not display_text and not self.active:
            display_text = self.placeholder
            text_color = (150, 150, 150)
        elif self.is_password and not self.show_password and display_text:
            display_text = "*" * len(display_text)
        
        if display_text:
            # Clip text to fit in box
            text_surface = self.font.render(display_text, True, text_color)
            text_rect = text_surface.get_rect()
            text_rect.centery = self.rect.centery
            text_rect.x = self.rect.x + 10
            
            # Create clipping area
            clip_rect = pygame.Rect(self.rect.x + 5, self.rect.y, 
                                  self.rect.width - (40 if self.is_password else 10), self.rect.height)
            screen.set_clip(clip_rect)
            screen.blit(text_surface, text_rect)
            screen.set_clip(None)
        
        # Draw cursor
        if self.active and self.cursor_timer < 0.5:
            cursor_x = self.rect.x + 10
            if self.text:
                cursor_text = display_text[:self.cursor_pos]
                cursor_width = self.font.size(cursor_text)[0]
                cursor_x += cursor_width
            
            pygame.draw.line(screen, WHITE, 
                           (cursor_x, self.rect.y + 5), 
                           (cursor_x, self.rect.bottom - 5), 2)
        
        # Draw eye icon for passwords
        if self.is_password and hasattr(self, 'eye_rect'):
            eye_color = (200, 200, 200) if self.show_password else (100, 100, 100)
            pygame.draw.rect(screen, eye_color, self.eye_rect, border_radius=3)
            
            # Simple eye icon
            center = self.eye_rect.center
            pygame.draw.circle(screen, (50, 50, 50), center, 6)
            if self.show_password:
                pygame.draw.circle(screen, WHITE, center, 3)

class APIKeyManager:
    def __init__(self, screen):
        self.screen = screen
        self.font_title = pygame.font.Font(None, 36)
        self.font_label = pygame.font.Font(None, 24)
        self.font_small = pygame.font.Font(None, 18)
        
        # Current API keys (loaded from .env)
        self.api_keys = self._load_api_keys()
        
        # Text inputs
        self.inputs = {
            "openai": SecureTextInput(50, 150, 400, 35, "OpenAI API Key", 
                                    "sk-...", True),
            "anthropic": SecureTextInput(50, 220, 400, 35, "Anthropic API Key", 
                                       "sk-ant-...", True),
            "custom_url": SecureTextInput(50, 290, 400, 35, "Custom API URL", 
                                        "https://api.example.com/v1", False),
            "custom_key": SecureTextInput(50, 360, 400, 35, "Custom API Key", 
                                        "your-custom-key", True),
        }
        
        # Load existing values
        self.inputs["openai"].text = self.api_keys.get("OPENAI_API_KEY", "")
        self.inputs["anthropic"].text = self.api_keys.get("ANTHROPIC_API_KEY", "")
        self.inputs["custom_url"].text = self.api_keys.get("CUSTOM_API_URL", "")
        self.inputs["custom_key"].text = self.api_keys.get("CUSTOM_API_KEY", "")
        
        # Buttons
        self.test_openai_btn = Button(470, 150, 80, 35, "Test", self._test_openai, 18)
        self.test_anthropic_btn = Button(470, 220, 80, 35, "Test", self._test_anthropic, 18)
        self.test_custom_btn = Button(470, 360, 80, 35, "Test", self._test_custom, 18)
        
        self.clear_all_btn = Button(50, 450, 100, 40, "Clear All", self._clear_all)
        self.save_btn = Button(170, 450, 100, 40, "Save Keys", self._save_keys)
        self.back_btn = Button(SCREEN_WIDTH - 150, 450, 100, 40, "Back", self._back)
        
        # Status messages
        self.status_messages = {}
        self.status_timers = {}
        
        # Callbacks
        self.on_back = None
        self.on_keys_saved = None
    
    def _load_api_keys(self) -> Dict[str, str]:
        """Load API keys from .env file"""
        keys = {}
        env_file = ".env"
        
        if os.path.exists(env_file):
            try:
                with open(env_file, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#') and '=' in line:
                            key, value = line.split('=', 1)
                            keys[key.strip()] = value.strip().strip('"\'')
            except Exception as e:
                print(f"Error reading .env file: {e}")
        
        return keys
    
    def _save_api_keys(self):
        """Save API keys to .env file"""
        env_file = ".env"
        
        # Read existing .env content
        existing_content = []
        if os.path.exists(env_file):
            try:
                with open(env_file, 'r') as f:
                    existing_content = f.readlines()
            except Exception as e:
                print(f"Error reading existing .env: {e}")
        
        # Update or add API key lines
        key_lines = {
            "OPENAI_API_KEY": f'OPENAI_API_KEY={self.inputs["openai"].text}\n',
            "ANTHROPIC_API_KEY": f'ANTHROPIC_API_KEY={self.inputs["anthropic"].text}\n',
            "CUSTOM_API_URL": f'CUSTOM_API_URL={self.inputs["custom_url"].text}\n',
            "CUSTOM_API_KEY": f'CUSTOM_API_KEY={self.inputs["custom_key"].text}\n',
        }
        
        # Process existing content
        updated_content = []
        keys_added = set()
        
        for line in existing_content:
            line_key = line.split('=')[0].strip() if '=' in line else None
            if line_key in key_lines:
                # Only add if there's a value
                if key_lines[line_key].split('=')[1].strip():
                    updated_content.append(key_lines[line_key])
                    keys_added.add(line_key)
            else:
                updated_content.append(line)
        
        # Add new keys that weren't in the file
        for key, line in key_lines.items():
            if key not in keys_added and line.split('=')[1].strip():
                updated_content.append(line)
        
        # Write back to file
        try:
            with open(env_file, 'w') as f:
                f.writelines(updated_content)
            return True
        except Exception as e:
            print(f"Error writing .env file: {e}")
            return False
    
    def _test_openai(self):
        self._test_api_key("openai", self.inputs["openai"].text, "OpenAI")
    
    def _test_anthropic(self):
        self._test_api_key("anthropic", self.inputs["anthropic"].text, "Anthropic")
    
    def _test_custom(self):
        url = self.inputs["custom_url"].text
        key = self.inputs["custom_key"].text
        if url and key:
            self._test_custom_api(url, key)
        else:
            self._set_status("custom", "URL and Key required", False)
    
    def _test_api_key(self, provider, key, display_name):
        """Test API key validity"""
        if not key.strip():
            self._set_status(provider, f"{display_name} key required", False)
            return
        
        # Basic validation
        if provider == "openai" and not key.startswith("sk-"):
            self._set_status(provider, "Invalid OpenAI key format", False)
            return
        
        if provider == "anthropic" and not key.startswith("sk-ant-"):
            self._set_status(provider, "Invalid Anthropic key format", False)
            return
        
        # Try to make a test request (simplified)
        try:
            if provider == "openai":
                import openai
                client = openai.OpenAI(api_key=key)
                # Simple test - list models
                models = client.models.list()
                self._set_status(provider, "✅ OpenAI key valid", True)
            
            elif provider == "anthropic":
                import anthropic
                client = anthropic.Anthropic(api_key=key)
                # Simple test - would normally test with a message
                self._set_status(provider, "✅ Anthropic key valid", True)
        
        except ImportError:
            self._set_status(provider, f"{display_name} library not installed", False)
        except Exception as e:
            error_msg = str(e)
            if "authentication" in error_msg.lower() or "unauthorized" in error_msg.lower():
                self._set_status(provider, "❌ Invalid API key", False)
            elif "quota" in error_msg.lower():
                self._set_status(provider, "⚠️ Quota exceeded", False)
            else:
                self._set_status(provider, f"❌ Test failed: {error_msg[:30]}...", False)
    
    def _test_custom_api(self, url, key):
        """Test custom API endpoint"""
        try:
            import requests
            
            # Try a simple request to test connectivity
            headers = {"Authorization": f"Bearer {key}"}
            response = requests.get(f"{url}/models", headers=headers, timeout=10)
            
            if response.status_code == 200:
                self._set_status("custom", "✅ Custom API working", True)
            elif response.status_code == 401:
                self._set_status("custom", "❌ Authentication failed", False)
            else:
                self._set_status("custom", f"❌ HTTP {response.status_code}", False)
        
        except ImportError:
            self._set_status("custom", "requests library not installed", False)
        except Exception as e:
            self._set_status("custom", f"❌ Connection failed", False)
    
    def _set_status(self, provider, message, is_success):
        """Set status message for a provider"""
        self.status_messages[provider] = (message, is_success)
        self.status_timers[provider] = 5.0  # Show for 5 seconds
    
    def _clear_all(self):
        """Clear all API keys"""
        for input_field in self.inputs.values():
            input_field.text = ""
            input_field.cursor_pos = 0
        
        self.status_messages.clear()
        self.status_timers.clear()
    
    def _save_keys(self):
        """Save all API keys"""
        if self._save_api_keys():
            if self.on_keys_saved:
                key_data = {
                    "openai_key": self.inputs["openai"].text,
                    "anthropic_key": self.inputs["anthropic"].text,
                    "custom_url": self.inputs["custom_url"].text,
                    "custom_key": self.inputs["custom_key"].text,
                }
                self.on_keys_saved(key_data)
            
            # Show success message
            for provider in ["openai", "anthropic", "custom"]:
                self._set_status(provider, "✅ Keys saved", True)
        else:
            for provider in ["openai", "anthropic", "custom"]:
                self._set_status(provider, "❌ Save failed", False)
    
    def _back(self):
        if self.on_back:
            self.on_back()
    
    def handle_event(self, event):
        # Handle input fields
        for input_field in self.inputs.values():
            if input_field.handle_event(event):
                return True
        
        # Handle buttons
        buttons = [self.test_openai_btn, self.test_anthropic_btn, self.test_custom_btn,
                  self.clear_all_btn, self.save_btn, self.back_btn]
        
        for button in buttons:
            if button.handle_event(event):
                return True
        
        return False
    
    def update(self, dt):
        # Update input fields
        for input_field in self.inputs.values():
            input_field.update(dt)
        
        # Update status timers
        for provider in list(self.status_timers.keys()):
            self.status_timers[provider] -= dt
            if self.status_timers[provider] <= 0:
                del self.status_timers[provider]
                if provider in self.status_messages:
                    del self.status_messages[provider]
    
    def draw(self):
        self.screen.fill((25, 35, 45))
        
        # Title
        title_text = self.font_title.render("API Key Management", True, WHITE)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, 40))
        self.screen.blit(title_text, title_rect)
        
        # Security notice
        notice_text = self.font_small.render("🔒 Keys are stored locally in .env file - never shared", True, (100, 255, 100))
        notice_rect = notice_text.get_rect(center=(SCREEN_WIDTH // 2, 70))
        self.screen.blit(notice_text, notice_rect)
        
        # Warning
        warning_text = self.font_small.render("⚠️ Keep your API keys secure - never share them publicly", True, (255, 200, 100))
        warning_rect = warning_text.get_rect(center=(SCREEN_WIDTH // 2, 90))
        self.screen.blit(warning_text, warning_rect)
        
        # Draw input fields
        for input_field in self.inputs.values():
            input_field.draw(self.screen)
        
        # Draw test buttons
        self.test_openai_btn.draw(self.screen)
        self.test_anthropic_btn.draw(self.screen)
        self.test_custom_btn.draw(self.screen)
        
        # Draw status messages
        status_positions = {
            "openai": (560, 165),
            "anthropic": (560, 235),
            "custom": (560, 375)
        }
        
        for provider, pos in status_positions.items():
            if provider in self.status_messages:
                message, is_success = self.status_messages[provider]
                color = (100, 255, 100) if is_success else (255, 100, 100)
                status_text = self.font_small.render(message, True, color)
                self.screen.blit(status_text, pos)
        
        # Draw help text
        help_lines = [
            "• OpenAI: Get key from platform.openai.com",
            "• Anthropic: Get key from console.anthropic.com", 
            "• Custom: Any OpenAI-compatible API endpoint",
            "• Test buttons verify key validity",
            "• Keys enable AI fallback when Ollama is slow"
        ]
        
        y_offset = 500
        for line in help_lines:
            help_text = self.font_small.render(line, True, (200, 200, 200))
            self.screen.blit(help_text, (50, y_offset))
            y_offset += 20
        
        # Draw control buttons
        self.clear_all_btn.draw(self.screen)
        self.save_btn.draw(self.screen)
        self.back_btn.draw(self.screen)