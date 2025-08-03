import pygame
from typing import Optional, List, Callable
from src.core.constants import *
from src.ui.menu import Button
from src.graphics.custom_asset_manager import CustomAssetManager

class IconButton(Button):
    """Button with icon support for interaction menu"""
    
    def __init__(self, x, y, width, height, text, callback, font_size=20, icon=None):
        super().__init__(x, y, width, height, text, callback, font_size)
        self.icon = icon
        self.icon_padding = 8
    
    def draw(self, screen):
        """Draw button with icon"""
        # Use same color logic as base Button class
        color = (100, 100, 100) if not self.enabled else (70, 130, 180) if self.hovered else (60, 60, 60)
        border_color = (200, 200, 200) if self.hovered else (150, 150, 150)
        text_color = (200, 200, 200) if not self.enabled else WHITE
        
        # Draw button background and border
        pygame.draw.rect(screen, color, self.rect, border_radius=5)
        pygame.draw.rect(screen, border_color, self.rect, 2, border_radius=5)
        
        # Draw icon and text with proper positioning
        if self.icon:
            # Draw icon on the left
            icon_x = self.rect.x + self.icon_padding
            icon_y = self.rect.centery - self.icon.get_height() // 2
            screen.blit(self.icon, (icon_x, icon_y))
            
            # Draw text next to icon
            text_x = icon_x + self.icon.get_width() + self.icon_padding
            text_surface = self.font.render(self.text, True, text_color)
            text_y = self.rect.centery - text_surface.get_height() // 2
            screen.blit(text_surface, (text_x, text_y))
        else:
            # No icon, draw text centered (fallback to base button behavior)
            text_surface = self.font.render(self.text, True, text_color)
            text_rect = text_surface.get_rect(center=self.rect.center)
            screen.blit(text_surface, text_rect)

class InteractionMenu:
    """
    Context menu for player-NPC interactions.
    Appears when player is near an NPC and presses interact key.
    """
    
    def __init__(self, screen):
        self.screen = screen
        self.font_title = pygame.font.Font(None, 24)
        self.font_option = pygame.font.Font(None, 20)
        self.font_info = pygame.font.Font(None, 16)
        
        # Asset manager for icons
        self.assets = CustomAssetManager()
        self._create_interaction_icons()
        
        self.visible = False
        self.target_npc = None
        self.player = None
        
        # Menu dimensions
        self.width = 250
        self.height = 300
        self.x = 0
        self.y = 0
        
        # Visual settings
        self.background_color = (30, 40, 50, 240)
        self.border_color = (100, 150, 200)
        self.text_color = WHITE
        self.relationship_colors = {
            'stranger': (150, 150, 150),
            'acquaintance': (200, 200, 100),
            'friend': (100, 200, 100),
            'close_friend': (100, 255, 100),
            'enemy': (255, 100, 100)
        }
        
        # Interaction options
        self.interaction_buttons = []
        self.callbacks = {}
        
        # Player input for custom dialogue
        self.custom_dialogue_mode = False
        self.custom_dialogue_text = ""
        self.dialogue_cursor_timer = 0
        
        # Game pause state callback
        self.on_pause_game = None
        self.on_resume_game = None
    
    def set_callback(self, event_name: str, callback):
        """Set a callback for interaction events"""
        self.callbacks[event_name] = callback
    
    def _create_interaction_icons(self):
        """Create simple pixel art icons for interaction options"""
        icon_size = 16
        
        # Greet icon (hand wave)
        greet_icon = pygame.Surface((icon_size, icon_size), pygame.SRCALPHA)
        pygame.draw.circle(greet_icon, (255, 220, 177), (8, 5), 3)  # Head
        pygame.draw.rect(greet_icon, (100, 150, 255), (6, 8, 4, 6))  # Body
        pygame.draw.rect(greet_icon, (255, 220, 177), (4, 9, 2, 3))  # Arm
        self.assets.icons["greet"] = greet_icon
        
        # Chat icon (speech bubble)
        chat_icon = pygame.Surface((icon_size, icon_size), pygame.SRCALPHA)
        pygame.draw.ellipse(chat_icon, (255, 255, 255), (2, 2, 12, 8))
        pygame.draw.ellipse(chat_icon, (100, 100, 100), (2, 2, 12, 8), 1)
        pygame.draw.circle(chat_icon, (100, 100, 100), (6, 6), 1)
        pygame.draw.circle(chat_icon, (100, 100, 100), (8, 6), 1)
        pygame.draw.circle(chat_icon, (100, 100, 100), (10, 6), 1)
        self.assets.icons["chat"] = chat_icon
        
        # Chat window icon (window with text)
        chat_window_icon = pygame.Surface((icon_size, icon_size), pygame.SRCALPHA)
        pygame.draw.rect(chat_window_icon, (50, 50, 50), (1, 1, 14, 12))
        pygame.draw.rect(chat_window_icon, (255, 255, 255), (2, 2, 12, 10))
        pygame.draw.rect(chat_window_icon, (0, 0, 0), (3, 4, 8, 1))
        pygame.draw.rect(chat_window_icon, (0, 0, 0), (3, 6, 6, 1))
        pygame.draw.rect(chat_window_icon, (0, 0, 0), (3, 8, 7, 1))
        self.assets.icons["chat_window"] = chat_window_icon
        
        # Gift icon (present box)
        gift_icon = pygame.Surface((icon_size, icon_size), pygame.SRCALPHA)
        pygame.draw.rect(gift_icon, (255, 100, 100), (4, 6, 8, 6))
        pygame.draw.rect(gift_icon, (255, 200, 100), (7, 4, 2, 8))
        pygame.draw.rect(gift_icon, (255, 200, 100), (4, 7, 8, 2))
        self.assets.icons["gift"] = gift_icon
        
        # Activity icon (two figures)
        activity_icon = pygame.Surface((icon_size, icon_size), pygame.SRCALPHA)
        pygame.draw.circle(activity_icon, (255, 220, 177), (5, 4), 2)  # Head 1
        pygame.draw.circle(activity_icon, (255, 220, 177), (11, 4), 2)  # Head 2
        pygame.draw.rect(activity_icon, (100, 150, 255), (4, 6, 2, 4))  # Body 1
        pygame.draw.rect(activity_icon, (150, 100, 255), (10, 6, 2, 4))  # Body 2
        self.assets.icons["activity"] = activity_icon
        
        # Ask icon (question mark)
        ask_icon = pygame.Surface((icon_size, icon_size), pygame.SRCALPHA)
        pygame.draw.circle(ask_icon, (255, 255, 100), (8, 8), 7)
        pygame.draw.circle(ask_icon, (0, 0, 0), (8, 8), 7, 2)
        font = pygame.font.Font(None, 16)
        question_text = font.render("?", True, (0, 0, 0))
        question_rect = question_text.get_rect(center=(8, 8))
        ask_icon.blit(question_text, question_rect)
        self.assets.icons["ask"] = ask_icon
        
        # Custom dialogue icon (pencil)
        custom_icon = pygame.Surface((icon_size, icon_size), pygame.SRCALPHA)
        pygame.draw.rect(custom_icon, (139, 69, 19), (6, 2, 2, 10))  # Pencil body
        pygame.draw.polygon(custom_icon, (255, 255, 0), [(6, 2), (8, 2), (7, 0)])  # Tip
        self.assets.icons["custom"] = custom_icon
        
        # Cancel icon (X)
        cancel_icon = pygame.Surface((icon_size, icon_size), pygame.SRCALPHA)
        pygame.draw.circle(cancel_icon, (255, 100, 100), (8, 8), 7)
        pygame.draw.line(cancel_icon, (255, 255, 255), (4, 4), (12, 12), 2)
        pygame.draw.line(cancel_icon, (255, 255, 255), (12, 4), (4, 12), 2)
        self.assets.icons["cancel"] = cancel_icon
    
    def show(self, player, npc, mouse_pos=None):
        """Show interaction menu for given NPC"""
        self.visible = True
        self.target_npc = npc
        self.player = player
        
        # Pause the game during NPC interaction
        if self.on_pause_game:
            self.on_pause_game()
        
        # Position menu near mouse or center screen
        if mouse_pos:
            self.x = max(10, min(mouse_pos[0] - self.width // 2, SCREEN_WIDTH - self.width - 10))
            self.y = max(10, min(mouse_pos[1] - 20, SCREEN_HEIGHT - self.height - 10))
        else:
            self.x = (SCREEN_WIDTH - self.width) // 2
            self.y = (SCREEN_HEIGHT - self.height) // 2
        
        # Create interaction buttons
        self._create_interaction_buttons()
    
    def hide(self):
        """Hide the interaction menu"""
        self.visible = False
        self.target_npc = None
        self.custom_dialogue_mode = False
        self.custom_dialogue_text = ""
        
        # Resume the game when hiding interaction menu
        if self.on_resume_game:
            self.on_resume_game()
    
    def _create_interaction_buttons(self):
        """Create buttons for different interaction options"""
        self.interaction_buttons = []
        button_y = self.y + 80
        button_height = 30
        button_spacing = 5
        
        # Basic interactions with icon keys
        interactions = [
            ("Greet", "greet", self._greet_npc),
            ("Chat", "chat", self._chat_with_npc),
            ("Open Chat Window", "chat_window", self._open_chat_window),
            ("Give Gift", "gift", self._give_gift),
            ("Invite to Activity", "activity", self._invite_activity),
            ("Ask About", "ask", self._ask_about),
            ("Say Something...", "custom", self._enable_custom_dialogue),
            ("Cancel", "cancel", self.hide)
        ]
        
        for text, icon_key, callback in interactions:
            button = IconButton(
                self.x + 20, button_y, 
                self.width - 40, button_height,
                text, callback, 18, icon=self.assets.icons.get(icon_key)
            )
            self.interaction_buttons.append(button)
            button_y += button_height + button_spacing
    
    def _get_relationship_level(self, value: float) -> str:
        """Get relationship level string from value"""
        if value < 0.2:
            return "stranger"
        elif value < 0.5:
            return "acquaintance"
        elif value < 0.8:
            return "friend"
        elif value >= 0.8:
            return "close_friend"
        else:
            return "stranger"
    
    def _greet_npc(self):
        """Simple greeting interaction"""
        print(f"👋 Greeting {self.target_npc.name if self.target_npc else 'NPC'}!")
        if self.callbacks.get('on_greet'):
            self.callbacks['on_greet'](self.player, self.target_npc)
        self.hide()
    
    def _chat_with_npc(self):
        """Start a conversation"""
        print(f"💬 Starting conversation with {self.target_npc.name if self.target_npc else 'NPC'}!")
        if self.callbacks.get('on_chat'):
            self.callbacks['on_chat'](self.player, self.target_npc)
        self.hide()
    
    def _open_chat_window(self):
        """Open the chat interface window"""
        if self.callbacks.get('on_open_chat'):
            self.callbacks['on_open_chat'](self.player, self.target_npc)
        else:
            # Fallback behavior
            print(f"Opening chat window with {self.target_npc.name}!")
        self.hide()
    
    def _give_gift(self):
        """Give a gift to the NPC"""
        if self.callbacks.get('on_give_gift'):
            self.callbacks['on_give_gift'](self.player, self.target_npc)
        self.hide()
    
    def _invite_activity(self):
        """Invite NPC to do an activity together"""
        if self.callbacks.get('on_invite_activity'):
            self.callbacks['on_invite_activity'](self.player, self.target_npc)
        self.hide()
    
    def _ask_about(self):
        """Ask NPC about something"""
        if self.callbacks.get('on_ask_about'):
            self.callbacks['on_ask_about'](self.player, self.target_npc)
        self.hide()
    
    def _enable_custom_dialogue(self):
        """Enable custom dialogue input mode"""
        self.custom_dialogue_mode = True
        self.custom_dialogue_text = ""
    
    def _submit_custom_dialogue(self):
        """Submit the custom dialogue"""
        if self.custom_dialogue_text.strip() and self.callbacks.get('on_custom_dialogue'):
            self.callbacks['on_custom_dialogue'](self.player, self.target_npc, self.custom_dialogue_text)
        self.hide()
    
    def handle_event(self, event) -> bool:
        """Handle input events"""
        if not self.visible:
            return False
        
        # Handle custom dialogue input
        if self.custom_dialogue_mode:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    self._submit_custom_dialogue()
                    return True
                elif event.key == pygame.K_ESCAPE:
                    self.custom_dialogue_mode = False
                    self.custom_dialogue_text = ""
                    return True
                elif event.key == pygame.K_BACKSPACE:
                    self.custom_dialogue_text = self.custom_dialogue_text[:-1]
                    return True
                elif event.unicode and len(self.custom_dialogue_text) < 50:
                    self.custom_dialogue_text += event.unicode
                    return True
            return True
        
        # Handle button events (clicks and hover)
        for button in self.interaction_buttons:
            if button.handle_event(event):
                return True
        
        # Close menu on escape or right click
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.hide()
            return True
        
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
            self.hide()
            return True
        
        # Block events from passing through
        return True
    
    def update(self, dt):
        """Update menu animations"""
        if self.custom_dialogue_mode:
            self.dialogue_cursor_timer += dt
            if self.dialogue_cursor_timer >= 1.0:
                self.dialogue_cursor_timer = 0
    
    def draw(self):
        """Draw the interaction menu"""
        if not self.visible or not self.target_npc:
            return
        
        # Draw semi-transparent background
        surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        surface.fill(self.background_color)
        self.screen.blit(surface, (self.x, self.y))
        
        # Draw border
        pygame.draw.rect(self.screen, self.border_color, 
                        (self.x, self.y, self.width, self.height), 2, border_radius=10)
        
        # Draw NPC name
        name_text = self.font_title.render(self.target_npc.name, True, self.text_color)
        name_rect = name_text.get_rect(center=(self.x + self.width // 2, self.y + 20))
        self.screen.blit(name_text, name_rect)
        
        # Draw relationship status
        relationship_value = self.player.relationships.get(self.target_npc.name, 0.0)
        relationship_level = self._get_relationship_level(relationship_value)
        relationship_color = self.relationship_colors.get(relationship_level, self.text_color)
        
        rel_text = f"{relationship_level.replace('_', ' ').title()} ({relationship_value:.2f})"
        rel_surface = self.font_info.render(rel_text, True, relationship_color)
        rel_rect = rel_surface.get_rect(center=(self.x + self.width // 2, self.y + 40))
        self.screen.blit(rel_surface, rel_rect)
        
        # Draw NPC mood/emotion
        # Get emotion from emotional_state if available
        emotion = None
        if hasattr(self.target_npc, 'emotional_state') and hasattr(self.target_npc.emotional_state, 'primary_emotion'):
            emotion = self.target_npc.emotional_state.primary_emotion.value
        elif hasattr(self.target_npc, 'emotion'):
            emotion = self.target_npc.emotion
        else:
            emotion = 'neutral'
        
        emotion_text = f"Mood: {emotion}"
        emotion_surface = self.font_info.render(emotion_text, True, (200, 200, 200))
        emotion_rect = emotion_surface.get_rect(center=(self.x + self.width // 2, self.y + 55))
        self.screen.blit(emotion_surface, emotion_rect)
        
        # Draw custom dialogue input if active
        if self.custom_dialogue_mode:
            # Draw input box
            input_rect = pygame.Rect(self.x + 10, self.y + 250, self.width - 20, 30)
            pygame.draw.rect(self.screen, (50, 50, 50), input_rect)
            pygame.draw.rect(self.screen, (100, 100, 100), input_rect, 2)
            
            # Draw input text
            if self.custom_dialogue_text:
                text_surface = self.font_option.render(self.custom_dialogue_text, True, WHITE)
                self.screen.blit(text_surface, (input_rect.x + 5, input_rect.y + 5))
            else:
                hint_surface = self.font_option.render("Type your message...", True, (150, 150, 150))
                self.screen.blit(hint_surface, (input_rect.x + 5, input_rect.y + 5))
            
            # Draw cursor
            if self.dialogue_cursor_timer < 0.5:
                cursor_x = input_rect.x + 5 + self.font_option.size(self.custom_dialogue_text)[0]
                pygame.draw.line(self.screen, WHITE, 
                               (cursor_x, input_rect.y + 5), 
                               (cursor_x, input_rect.y + 25), 2)
            
            # Draw submit hint
            hint_text = "Press Enter to send, Esc to cancel"
            hint_surface = self.font_info.render(hint_text, True, (150, 150, 150))
            hint_rect = hint_surface.get_rect(center=(self.x + self.width // 2, self.y + 285))
            self.screen.blit(hint_surface, hint_rect)
        else:
            # Draw interaction buttons
            for button in self.interaction_buttons:
                button.draw(self.screen)
    
    def set_callback(self, action: str, callback: Callable):
        """Set callback for specific interaction type"""
        self.callbacks[action] = callback