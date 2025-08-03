import pygame
import os
from typing import Dict, Callable
from src.core.constants import *
from src.ui.menu import Button
from src.graphics.custom_asset_manager import CustomAssetManager

class Slider:
    def __init__(self, x, y, width, height, min_val, max_val, initial_val, label):
        self.rect = pygame.Rect(x, y, width, height)
        self.min_val = min_val
        self.max_val = max_val
        self.val = initial_val
        self.label = label
        self.dragging = False
        self.font = pygame.font.Font(None, 20)
        self.on_change = None
        
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
        # Draw slider track
        pygame.draw.rect(screen, (60, 60, 60), self.rect, border_radius=3)
        pygame.draw.rect(screen, (120, 120, 120), self.rect, 2, border_radius=3)
        
        # Draw slider handle
        handle_x = self.rect.x + (self.val - self.min_val) / (self.max_val - self.min_val) * self.rect.width
        handle_rect = pygame.Rect(handle_x - 8, self.rect.y - 4, 16, self.rect.height + 8)
        pygame.draw.rect(screen, (200, 200, 200), handle_rect, border_radius=8)
        
        # Draw label and value
        label_text = self.font.render(f"{self.label}: {self.val:.2f}", True, WHITE)
        screen.blit(label_text, (self.rect.x, self.rect.y - 25))

class ColorPicker:
    def __init__(self, x, y, colors, initial_color):
        self.x = x
        self.y = y
        self.colors = colors
        self.selected_color = initial_color
        self.color_rects = []
        
        for i, color in enumerate(colors):
            rect = pygame.Rect(x + i * 35, y, 30, 30)
            self.color_rects.append((rect, color))
    
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for rect, color in self.color_rects:
                if rect.collidepoint(event.pos):
                    self.selected_color = color
                    return True
        return False
    
    def draw(self, screen):
        font = pygame.font.Font(None, 20)
        label_text = font.render("Player Color:", True, WHITE)
        screen.blit(label_text, (self.x, self.y - 25))
        
        for rect, color in self.color_rects:
            pygame.draw.rect(screen, color, rect)
            if color == self.selected_color:
                pygame.draw.rect(screen, WHITE, rect, 3)
            else:
                pygame.draw.rect(screen, (100, 100, 100), rect, 2)

class SkinSelector:
    """Allows player to select from available character skins/sprites"""
    
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.assets = CustomAssetManager()
        
        # Available player skins with display names
        self.available_skins = [
            ("male", "Male Villager"),
            ("male_farmer", "Male Farmer"),
            ("female", "Female Villager"),
            ("female_villager", "Female Adventurer"),
            ("girl1", "Young Woman"),
        ]
        
        # Load skin sprites
        self.skin_sprites = {}
        for skin_id, display_name in self.available_skins:
            sprite = self.assets.get_character_sprite(skin_id)
            if sprite:
                # Scale sprite for preview
                preview_sprite = pygame.transform.scale(sprite, (48, 64))
                self.skin_sprites[skin_id] = {
                    "sprite": preview_sprite,
                    "display_name": display_name
                }
        
        # Default to first available skin
        self.selected_skin = self.available_skins[0][0] if self.available_skins else "male"
        
        # Create clickable rectangles for each skin
        self.skin_rects = []
        for i, (skin_id, _) in enumerate(self.available_skins):
            col = i % 3
            row = i // 3
            rect = pygame.Rect(x + col * 100, y + row * 90, 80, 80)
            self.skin_rects.append((rect, skin_id))
    
    def handle_event(self, event):
        """Handle mouse clicks on skin options"""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for rect, skin_id in self.skin_rects:
                if rect.collidepoint(event.pos):
                    self.selected_skin = skin_id
                    return True
        return False
    
    def draw(self, screen):
        """Draw the skin selector UI"""
        font = pygame.font.Font(None, 24)
        label_text = font.render("Choose Your Character:", True, WHITE)
        screen.blit(label_text, (self.x, self.y - 30))
        
        # Draw each skin option
        for rect, skin_id in self.skin_rects:
            # Draw background
            if skin_id == self.selected_skin:
                pygame.draw.rect(screen, (100, 150, 200), rect)
                pygame.draw.rect(screen, WHITE, rect, 3)
            else:
                pygame.draw.rect(screen, (60, 60, 60), rect)
                pygame.draw.rect(screen, (100, 100, 100), rect, 2)
            
            # Draw sprite preview
            if skin_id in self.skin_sprites:
                sprite_data = self.skin_sprites[skin_id]
                sprite_rect = sprite_data["sprite"].get_rect()
                sprite_rect.center = rect.center
                screen.blit(sprite_data["sprite"], sprite_rect)
                
                # Draw name below sprite
                name_font = pygame.font.Font(None, 16)
                name_text = name_font.render(sprite_data["display_name"], True, WHITE)
                name_rect = name_text.get_rect()
                name_rect.centerx = rect.centerx
                name_rect.top = rect.bottom + 2
                screen.blit(name_text, name_rect)
    
    def get_selected_skin(self):
        """Return the currently selected skin ID"""
        return self.selected_skin

class CharacterCreator:
    def __init__(self, screen):
        self.screen = screen
        self.font_title = pygame.font.Font(None, 48)
        self.font_label = pygame.font.Font(None, 24)
        
        center_x = SCREEN_WIDTH // 2
        
        # Character name input
        self.name_input = ""
        self.name_active = False
        self.name_rect = pygame.Rect(center_x - 150, 120, 300, 40)
        
        # Skin selector - positioned at the top
        self.skin_selector = SkinSelector(center_x - 150, 200)
        
        # Personality sliders - adjusted positioning to accommodate skin selector
        slider_start_y = 400
        self.personality_sliders = {
            "friendliness": Slider(center_x - 200, slider_start_y, 200, 20, 0.0, 1.0, 0.5, "Friendliness"),
            "energy": Slider(center_x + 20, slider_start_y, 200, 20, 0.0, 1.0, 0.5, "Energy"),
            "creativity": Slider(center_x - 200, slider_start_y + 50, 200, 20, 0.0, 1.0, 0.5, "Creativity"),
            "organization": Slider(center_x + 20, slider_start_y + 50, 200, 20, 0.0, 1.0, 0.5, "Organization"),
            "confidence": Slider(center_x - 200, slider_start_y + 100, 200, 20, 0.0, 1.0, 0.5, "Confidence"),
            "empathy": Slider(center_x + 20, slider_start_y + 100, 200, 20, 0.0, 1.0, 0.5, "Empathy"),
            "humor": Slider(center_x - 200, slider_start_y + 150, 200, 20, 0.0, 1.0, 0.5, "Humor"),
            "curiosity": Slider(center_x + 20, slider_start_y + 150, 200, 20, 0.0, 1.0, 0.5, "Curiosity"),
            "patience": Slider(center_x - 200, slider_start_y + 200, 200, 20, 0.0, 1.0, 0.5, "Patience"),
            "ambition": Slider(center_x + 20, slider_start_y + 200, 200, 20, 0.0, 1.0, 0.5, "Ambition"),
        }
        
        # Color picker - moved down
        colors = [
            BLUE, RED, (100, 255, 100), (255, 255, 100), 
            (255, 100, 255), (100, 255, 255), (255, 150, 100), (150, 100, 255)
        ]
        color_picker_y = SCREEN_HEIGHT - 240  # Position color picker appropriately
        self.color_picker = ColorPicker(center_x - 140, color_picker_y, colors, BLUE)
        
        # Preset buttons - adjusted for screen height
        preset_y = SCREEN_HEIGHT - 180  # Position preset buttons above control buttons
        self.preset_buttons = [
            Button(center_x - 250, preset_y, 100, 30, "Friendly", self._preset_friendly, 16),
            Button(center_x - 130, preset_y, 100, 30, "Leader", self._preset_leader, 16),
            Button(center_x - 10, preset_y, 100, 30, "Creative", self._preset_creative, 16),
            Button(center_x + 110, preset_y, 100, 30, "Random", self._preset_random, 16),
        ]
        
        # Control buttons - adjusted for screen height
        button_y = SCREEN_HEIGHT - 120  # Position buttons 120px from bottom
        self.create_button = Button(center_x - 150, button_y, 140, 40, "Create Character", self._create_character)
        self.advanced_button = Button(center_x + 20, button_y, 130, 40, "Advanced Settings", self._open_advanced)
        self.back_button = Button(50, button_y, 80, 40, "Back", self._back)
        
        # Callbacks
        self.on_character_created = None
        self.on_back = None
        self.on_advanced_settings = None
        
        self.character_data = None
    
    def _preset_friendly(self):
        self.personality_sliders["friendliness"].val = 0.9
        self.personality_sliders["empathy"].val = 0.8
        self.personality_sliders["humor"].val = 0.7
        self.personality_sliders["patience"].val = 0.8
    
    def _preset_leader(self):
        self.personality_sliders["confidence"].val = 0.9
        self.personality_sliders["ambition"].val = 0.8
        self.personality_sliders["organization"].val = 0.8
        self.personality_sliders["energy"].val = 0.7
    
    def _preset_creative(self):
        self.personality_sliders["creativity"].val = 0.9
        self.personality_sliders["curiosity"].val = 0.8
        self.personality_sliders["humor"].val = 0.7
        self.personality_sliders["empathy"].val = 0.6
    
    def _preset_random(self):
        import random
        for slider in self.personality_sliders.values():
            slider.val = random.uniform(0.2, 0.8)
    
    def _create_character(self):
        if len(self.name_input.strip()) == 0:
            self.name_input = "Player"
        
        personality_traits = {}
        for trait, slider in self.personality_sliders.items():
            personality_traits[trait] = slider.val
        
        self.character_data = {
            "name": self.name_input.strip(),
            "personality": personality_traits,
            "color": self.color_picker.selected_color,
            "skin": self.skin_selector.get_selected_skin()
        }
        
        if self.on_character_created:
            self.on_character_created(self.character_data)
    
    def _back(self):
        if self.on_back:
            self.on_back()
    
    def _open_advanced(self):
        if self.on_advanced_settings:
            self.on_advanced_settings()
    
    def handle_event(self, event):
        # Handle name input
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.name_active = self.name_rect.collidepoint(event.pos)
        
        if event.type == pygame.KEYDOWN and self.name_active:
            if event.key == pygame.K_BACKSPACE:
                self.name_input = self.name_input[:-1]
            elif event.key == pygame.K_TAB or event.key == pygame.K_RETURN:
                self.name_active = False
            else:
                if len(self.name_input) < 20 and event.unicode.isprintable():
                    self.name_input += event.unicode
            return True
        
        # Handle skin selector
        if self.skin_selector.handle_event(event):
            return True
        
        # Handle sliders
        for slider in self.personality_sliders.values():
            if slider.handle_event(event):
                return True
        
        # Handle color picker
        if self.color_picker.handle_event(event):
            return True
        
        # Handle buttons
        for button in self.preset_buttons:
            if button.handle_event(event):
                return True
        
        if self.create_button.handle_event(event):
            return True
        
        if self.advanced_button.handle_event(event):
            return True
        
        if self.back_button.handle_event(event):
            return True
        
        return False
    
    def draw(self):
        self.screen.fill((20, 30, 40))
        
        # Title
        title_text = self.font_title.render("Create Your Character", True, WHITE)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, 80))
        self.screen.blit(title_text, title_rect)
        
        # Name input
        name_label = self.font_label.render("Character Name:", True, WHITE)
        self.screen.blit(name_label, (self.name_rect.x, self.name_rect.y - 30))
        
        name_color = (70, 130, 180) if self.name_active else (60, 60, 60)
        pygame.draw.rect(self.screen, name_color, self.name_rect, border_radius=5)
        pygame.draw.rect(self.screen, WHITE if self.name_active else (150, 150, 150), self.name_rect, 2, border_radius=5)
        
        name_text = self.name_input if self.name_input else "Enter your name..."
        name_color = WHITE if self.name_input else (150, 150, 150)
        name_surface = self.font_label.render(name_text, True, name_color)
        name_text_rect = name_surface.get_rect()
        name_text_rect.centery = self.name_rect.centery
        name_text_rect.x = self.name_rect.x + 10
        self.screen.blit(name_surface, name_text_rect)
        
        # Draw skin selector
        self.skin_selector.draw(self.screen)
        
        # Personality section title
        personality_title = self.font_label.render("Personality Traits:", True, (255, 255, 100))
        self.screen.blit(personality_title, (SCREEN_WIDTH // 2 - 200, 370))
        
        # Draw sliders
        for slider in self.personality_sliders.values():
            slider.draw(self.screen)
        
        # Draw color picker
        self.color_picker.draw(self.screen)
        
        # Preset section title
        preset_title = self.font_label.render("Quick Presets:", True, (255, 255, 100))
        self.screen.blit(preset_title, (SCREEN_WIDTH // 2 - 250, 695))
        
        # Draw buttons
        for button in self.preset_buttons:
            button.draw(self.screen)
        
        self.create_button.draw(self.screen)
        self.advanced_button.draw(self.screen)
        self.back_button.draw(self.screen)
        
        # Character preview
        self._draw_character_preview()
    
    def _draw_character_preview(self):
        preview_x = SCREEN_WIDTH - 200
        preview_y = 200
        
        # Preview title
        preview_title = self.font_label.render("Preview:", True, WHITE)
        self.screen.blit(preview_title, (preview_x, preview_y - 30))
        
        # Draw character sprite preview
        char_rect = pygame.Rect(preview_x + 50, preview_y + 20, 32, 32)
        pygame.draw.rect(self.screen, self.color_picker.selected_color, char_rect)
        pygame.draw.rect(self.screen, WHITE, char_rect, 2)
        
        # Character stats summary
        y_offset = preview_y + 70
        high_traits = []
        for trait, slider in self.personality_sliders.items():
            if slider.val > 0.7:
                high_traits.append(trait.capitalize())
        
        if high_traits:
            traits_text = self.font_label.render("Strong Traits:", True, (100, 255, 100))
            self.screen.blit(traits_text, (preview_x, y_offset))
            y_offset += 25
            
            for trait in high_traits[:4]:  # Show top 4
                trait_text = pygame.font.Font(None, 18).render(f"• {trait}", True, WHITE)
                self.screen.blit(trait_text, (preview_x + 10, y_offset))
                y_offset += 20