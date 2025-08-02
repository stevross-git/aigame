import pygame
import textwrap
import random
from typing import List, Dict, Optional
from src.core.constants import *
from src.graphics.custom_asset_manager import CustomAssetManager

class ChatMessage:
    """Represents a single chat message"""
    def __init__(self, sender: str, text: str, is_player: bool = False):
        self.sender = sender
        self.text = text
        self.is_player = is_player
        self.timestamp = pygame.time.get_ticks()

class NPCChatInterface:
    """
    Beautiful chat interface for talking directly with NPCs
    """
    
    def __init__(self, screen):
        self.screen = screen
        self.assets = CustomAssetManager()
        
        # Fonts
        self.font_name = pygame.font.Font(None, 20)
        self.font_message = pygame.font.Font(None, 18)
        self.font_input = pygame.font.Font(None, 18)
        self.font_small = pygame.font.Font(None, 16)
        
        # Chat window settings
        self.chat_width = 500
        self.chat_height = 400
        self.chat_x = (SCREEN_WIDTH - self.chat_width) // 2
        self.chat_y = (SCREEN_HEIGHT - self.chat_height) // 2
        
        # Input box settings
        self.input_height = 40
        self.input_padding = 10
        
        # Chat state
        self.visible = False
        self.current_npc = None
        self.chat_messages: List[ChatMessage] = []
        self.input_text = ""
        self.input_active = False
        self.cursor_visible = True
        self.cursor_timer = 0.0
        self.scroll_offset = 0
        self.max_messages = 50
        
        # Colors
        self.bg_color = (25, 35, 50, 230)
        self.border_color = (100, 150, 200)
        self.input_bg_color = (40, 50, 70)
        self.input_border_color = (120, 170, 220)
        self.player_msg_color = (100, 200, 255)
        self.npc_msg_color = (255, 200, 100)
        self.text_color = (255, 255, 255)
        
        # Animation
        self.animation_time = 0.0
        self.slide_animation = 0.0
        self.target_slide = 0.0
        
        # Typing indicator
        self.npc_typing = False
        self.typing_timer = 0.0
        self.typing_dots = 0
    
    def show(self, npc):
        """Show chat interface for specific NPC"""
        self.current_npc = npc
        self.visible = True
        self.input_active = True
        self.target_slide = 1.0
        
        # Add greeting message if this is first conversation
        if not self.chat_messages or self.chat_messages[-1].sender != npc.name:
            greeting = self._generate_greeting()
            self.add_npc_message(greeting)
    
    def hide(self):
        """Hide chat interface"""
        self.target_slide = 0.0
        self.input_active = False
        # Don't immediately set visible = False, let animation finish
    
    def add_player_message(self, text: str):
        """Add a message from the player"""
        if text.strip():
            message = ChatMessage("You", text.strip(), is_player=True)
            self.chat_messages.append(message)
            self._trim_messages()
            self._scroll_to_bottom()
    
    def add_npc_message(self, text: str):
        """Add a message from the current NPC"""
        if self.current_npc and text.strip():
            message = ChatMessage(self.current_npc.name, text.strip(), is_player=False)
            self.chat_messages.append(message)
            self._trim_messages()
            self._scroll_to_bottom()
    
    def update(self, dt: float):
        """Update chat interface animations and state"""
        self.animation_time += dt
        
        # Cursor blinking
        self.cursor_timer += dt
        if self.cursor_timer >= 0.5:
            self.cursor_visible = not self.cursor_visible
            self.cursor_timer = 0.0
        
        # Slide animation
        if self.slide_animation != self.target_slide:
            diff = self.target_slide - self.slide_animation
            self.slide_animation += diff * dt * 8.0  # Animation speed
            
            # Close interface when slide animation is complete
            if self.target_slide == 0.0 and self.slide_animation < 0.05:
                self.visible = False
                self.slide_animation = 0.0
        
        # NPC typing indicator
        if self.npc_typing:
            self.typing_timer += dt
            if self.typing_timer >= 0.5:
                self.typing_dots = (self.typing_dots + 1) % 4
                self.typing_timer = 0.0
    
    def handle_event(self, event) -> bool:
        """Handle chat interface events"""
        if not self.visible:
            return False
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.hide()
                return True
            
            elif event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                if self.input_text.strip():
                    self._send_message()
                return True
            
            elif event.key == pygame.K_BACKSPACE:
                if self.input_text:
                    self.input_text = self.input_text[:-1]
                return True
            
            elif event.key == pygame.K_UP:
                self.scroll_offset = max(0, self.scroll_offset - 1)
                return True
                
            elif event.key == pygame.K_DOWN:
                max_scroll = max(0, len(self.chat_messages) - self._get_visible_message_count())
                self.scroll_offset = min(max_scroll, self.scroll_offset + 1)
                return True
            
            else:
                # Add character to input
                if len(self.input_text) < 200:  # Max message length
                    char = event.unicode
                    if char.isprintable():
                        self.input_text += char
                return True
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            # Check if clicked outside chat window
            chat_rect = pygame.Rect(self.chat_x, self.chat_y, self.chat_width, self.chat_height)
            if not chat_rect.collidepoint(event.pos):
                self.hide()
                return True
            
            # Check if clicked on input box
            input_y = self.chat_y + self.chat_height - self.input_height - self.input_padding
            input_rect = pygame.Rect(self.chat_x + self.input_padding, input_y, 
                                   self.chat_width - 2 * self.input_padding, self.input_height)
            if input_rect.collidepoint(event.pos):
                self.input_active = True
                return True
        
        elif event.type == pygame.MOUSEWHEEL:
            # Scroll chat messages
            chat_rect = pygame.Rect(self.chat_x, self.chat_y, self.chat_width, 
                                  self.chat_height - self.input_height - self.input_padding * 2)
            mouse_pos = pygame.mouse.get_pos()
            if chat_rect.collidepoint(mouse_pos):
                max_scroll = max(0, len(self.chat_messages) - self._get_visible_message_count())
                self.scroll_offset = max(0, min(max_scroll, self.scroll_offset - event.y))
                return True
        
        return False
    
    def draw(self):
        """Draw the chat interface"""
        if not self.visible:
            return
        
        # Apply slide animation
        slide_offset = (1.0 - self.slide_animation) * 100
        actual_chat_y = self.chat_y + slide_offset
        
        # Draw main chat window
        self._draw_chat_window(actual_chat_y)
        
        # Draw NPC portrait and info
        self._draw_npc_info(actual_chat_y)
        
        # Draw chat messages
        self._draw_chat_messages(actual_chat_y)
        
        # Draw typing indicator
        if self.npc_typing:
            self._draw_typing_indicator(actual_chat_y)
        
        # Draw input box
        self._draw_input_box(actual_chat_y)
        
        # Draw scroll indicator
        self._draw_scroll_indicator(actual_chat_y)
    
    def _draw_chat_window(self, y_offset: float):
        """Draw the main chat window background"""
        # Main window with transparency
        window_surface = pygame.Surface((self.chat_width, self.chat_height), pygame.SRCALPHA)
        pygame.draw.rect(window_surface, self.bg_color, 
                        (0, 0, self.chat_width, self.chat_height), border_radius=15)
        
        # Border with NPC's mood color
        border_color = self.border_color
        if self.current_npc:
            # Get NPC emotion color (you might need to import this from HUD)
            mood_colors = {
                "happy": (100, 255, 100),
                "excited": (255, 200, 100),
                "sad": (150, 150, 255),
                "angry": (255, 100, 100),
                "neutral": (200, 200, 200),
                "curious": (200, 255, 200),
                "tired": (180, 150, 180)
            }
            border_color = mood_colors.get(self.current_npc.emotion, self.border_color)
        
        pygame.draw.rect(window_surface, border_color, 
                        (0, 0, self.chat_width, self.chat_height), 3, border_radius=15)
        
        # Glass highlight effect
        highlight_color = (255, 255, 255, 40)
        highlight_rect = pygame.Rect(3, 3, self.chat_width - 6, 60)
        pygame.draw.rect(window_surface, highlight_color, highlight_rect, border_radius=12)
        
        self.screen.blit(window_surface, (self.chat_x, y_offset))
    
    def _draw_npc_info(self, y_offset: float):
        """Draw NPC portrait and name at top of chat"""
        if not self.current_npc:
            return
        
        # NPC portrait
        portrait = self.assets.get_npc_portrait(self.current_npc.name)
        if portrait:
            portrait_rect = portrait.get_rect()
            portrait_rect.x = self.chat_x + 15
            portrait_rect.y = y_offset + 15
            self.screen.blit(portrait, portrait_rect)
        
        # NPC name and status
        name_text = self.font_name.render(f"Chatting with {self.current_npc.name}", True, self.text_color)
        name_rect = name_text.get_rect()
        name_rect.x = self.chat_x + (50 if portrait else 15)
        name_rect.y = y_offset + 15
        self.screen.blit(name_text, name_rect)
        
        # NPC emotion/mood
        emotion_text = f"Mood: {self.current_npc.emotion.title()}"
        emotion_surface = self.font_small.render(emotion_text, True, (180, 180, 180))
        emotion_rect = emotion_surface.get_rect()
        emotion_rect.x = self.chat_x + (50 if portrait else 15)
        emotion_rect.y = y_offset + 35
        self.screen.blit(emotion_surface, emotion_rect)
        
        # Close button
        close_text = self.font_small.render("Press ESC to close", True, (150, 150, 150))
        close_rect = close_text.get_rect()
        close_rect.right = self.chat_x + self.chat_width - 15
        close_rect.y = y_offset + 20
        self.screen.blit(close_text, close_rect)
    
    def _draw_chat_messages(self, y_offset: float):
        """Draw chat messages in the scrollable area"""
        messages_start_y = y_offset + 70
        messages_height = self.chat_height - 140  # Leave space for header and input
        messages_end_y = messages_start_y + messages_height
        
        # Create clipping rect for messages
        clip_rect = pygame.Rect(self.chat_x + 10, messages_start_y, 
                               self.chat_width - 20, messages_height)
        self.screen.set_clip(clip_rect)
        
        # Calculate visible messages
        visible_messages = self._get_visible_messages()
        current_y = messages_start_y
        
        for message in visible_messages:
            if current_y > messages_end_y:
                break
            
            current_y = self._draw_message(message, current_y, messages_end_y)
        
        # Remove clipping
        self.screen.set_clip(None)
    
    def _draw_message(self, message: ChatMessage, y: float, max_y: float) -> float:
        """Draw a single chat message and return next Y position"""
        margin = 15
        bubble_padding = 10
        max_width = self.chat_width - 100
        
        # Wrap text
        wrapped_lines = textwrap.wrap(message.text, width=50)
        line_height = 20
        bubble_height = len(wrapped_lines) * line_height + bubble_padding * 2
        
        # Position bubble based on sender
        if message.is_player:
            # Player messages on the right (blue)
            bubble_x = self.chat_x + self.chat_width - max_width - margin
            bubble_color = (50, 100, 200, 180)
            text_color = (255, 255, 255)
        else:
            # NPC messages on the left (warm color)
            bubble_x = self.chat_x + margin
            bubble_color = (100, 70, 50, 180)
            text_color = (255, 255, 255)
        
        # Draw message bubble
        bubble_rect = pygame.Rect(bubble_x, y, max_width, bubble_height)
        bubble_surface = pygame.Surface((max_width, bubble_height), pygame.SRCALPHA)
        pygame.draw.rect(bubble_surface, bubble_color, (0, 0, max_width, bubble_height), 
                        border_radius=12)
        
        # Add subtle border
        border_color = tuple(min(255, c + 50) for c in bubble_color[:3]) + (255,)
        pygame.draw.rect(bubble_surface, border_color, (0, 0, max_width, bubble_height), 
                        2, border_radius=12)
        
        self.screen.blit(bubble_surface, bubble_rect)
        
        # Draw sender name
        if not message.is_player:
            name_surface = self.font_small.render(message.sender, True, self.npc_msg_color)
            name_rect = name_surface.get_rect()
            name_rect.x = bubble_x + bubble_padding
            name_rect.y = y + 5
            self.screen.blit(name_surface, name_rect)
            text_start_y = y + 22
        else:
            text_start_y = y + bubble_padding
        
        # Draw message text
        for i, line in enumerate(wrapped_lines):
            line_surface = self.font_message.render(line, True, text_color)
            line_rect = line_surface.get_rect()
            line_rect.x = bubble_x + bubble_padding
            line_rect.y = text_start_y + i * line_height
            self.screen.blit(line_surface, line_rect)
        
        return y + bubble_height + 10  # Return next Y position
    
    def _draw_typing_indicator(self, y_offset: float):
        """Draw typing indicator when NPC is responding"""
        indicator_y = y_offset + self.chat_height - 80
        
        # Typing bubble
        bubble_width = 80
        bubble_height = 30
        bubble_x = self.chat_x + 20
        
        bubble_surface = pygame.Surface((bubble_width, bubble_height), pygame.SRCALPHA)
        pygame.draw.rect(bubble_surface, (100, 70, 50, 180), 
                        (0, 0, bubble_width, bubble_height), border_radius=12)
        
        self.screen.blit(bubble_surface, (bubble_x, indicator_y))
        
        # Animated dots
        dots = "." * (self.typing_dots + 1)
        typing_text = f"{self.current_npc.name} is typing{dots}"
        typing_surface = self.font_small.render(typing_text, True, (200, 200, 200))
        typing_rect = typing_surface.get_rect()
        typing_rect.x = bubble_x + 10
        typing_rect.y = indicator_y + 8
        self.screen.blit(typing_surface, typing_rect)
    
    def _draw_input_box(self, y_offset: float):
        """Draw text input box"""
        input_y = y_offset + self.chat_height - self.input_height - self.input_padding
        input_rect = pygame.Rect(self.chat_x + self.input_padding, input_y, 
                                self.chat_width - 2 * self.input_padding, self.input_height)
        
        # Input background
        input_color = self.input_bg_color if self.input_active else (30, 35, 45)
        pygame.draw.rect(self.screen, input_color, input_rect, border_radius=8)
        
        # Input border
        border_color = self.input_border_color if self.input_active else (80, 90, 100)
        pygame.draw.rect(self.screen, border_color, input_rect, 2, border_radius=8)
        
        # Input text
        display_text = self.input_text
        if len(display_text) > 60:  # Scroll long text
            display_text = "..." + display_text[-57:]
        
        text_surface = self.font_input.render(display_text, True, self.text_color)
        text_rect = text_surface.get_rect()
        text_rect.x = input_rect.x + 10
        text_rect.centery = input_rect.centery
        self.screen.blit(text_surface, text_rect)
        
        # Cursor
        if self.input_active and self.cursor_visible:
            cursor_x = text_rect.right + 2
            cursor_y1 = input_rect.centery - 8
            cursor_y2 = input_rect.centery + 8
            pygame.draw.line(self.screen, self.text_color, (cursor_x, cursor_y1), (cursor_x, cursor_y2), 2)
        
        # Placeholder text
        if not self.input_text:
            placeholder = "Type your message... (Press Enter to send)"
            placeholder_surface = self.font_input.render(placeholder, True, (120, 120, 120))
            placeholder_rect = placeholder_surface.get_rect()
            placeholder_rect.x = input_rect.x + 10
            placeholder_rect.centery = input_rect.centery
            self.screen.blit(placeholder_surface, placeholder_rect)
    
    def _draw_scroll_indicator(self, y_offset: float):
        """Draw scroll indicator if needed"""
        if len(self.chat_messages) > self._get_visible_message_count():
            # Scroll bar background
            scrollbar_x = self.chat_x + self.chat_width - 15
            scrollbar_y = y_offset + 70
            scrollbar_height = self.chat_height - 140
            
            pygame.draw.rect(self.screen, (50, 50, 50), 
                           (scrollbar_x, scrollbar_y, 8, scrollbar_height), border_radius=4)
            
            # Scroll thumb
            max_scroll = len(self.chat_messages) - self._get_visible_message_count()
            thumb_height = max(20, scrollbar_height * self._get_visible_message_count() // len(self.chat_messages))
            thumb_y = scrollbar_y + (scrollbar_height - thumb_height) * (self.scroll_offset / max_scroll) if max_scroll > 0 else scrollbar_y
            
            pygame.draw.rect(self.screen, (120, 120, 120), 
                           (scrollbar_x, thumb_y, 8, thumb_height), border_radius=4)
    
    def _send_message(self):
        """Send the current input message"""
        if not self.input_text.strip() or not self.current_npc:
            return
        
        # Add player message
        self.add_player_message(self.input_text)
        player_message = self.input_text
        self.input_text = ""
        
        # Show typing indicator
        self.npc_typing = True
        
        # Send message to NPC for AI response
        self._request_npc_response(player_message)
    
    def _request_npc_response(self, player_message: str):
        """Request AI response from NPC"""
        if not self.current_npc:
            return
        
        # Set player interaction context for the NPC
        self.current_npc.player_interaction_context = {
            "type": "direct_chat",
            "message": player_message,
            "chat_history": [msg.text for msg in self.chat_messages[-5:]]  # Last 5 messages
        }
        
        # The NPC will respond on its next AI update cycle
        # We'll stop the typing indicator when the response comes
    
    def handle_npc_response(self, npc, response_text: str):
        """Handle when NPC provides a response"""
        if npc == self.current_npc and response_text:
            self.npc_typing = False
            self.add_npc_message(response_text)
    
    def _generate_greeting(self) -> str:
        """Generate a greeting message for the NPC"""
        greetings = [
            f"Hello! Nice to see you!",
            f"Hey there! What's up?",
            f"Hi! How are you doing?",
            f"Good to see you! What brings you here?",
            f"Hello! Lovely day, isn't it?"
        ]
        return random.choice(greetings)
    
    def _get_visible_message_count(self) -> int:
        """Get number of messages that can fit in visible area"""
        return (self.chat_height - 140) // 35  # Approximate message height
    
    def _get_visible_messages(self) -> List[ChatMessage]:
        """Get messages that should be visible based on scroll"""
        start_idx = self.scroll_offset
        end_idx = start_idx + self._get_visible_message_count()
        return self.chat_messages[start_idx:end_idx]
    
    def _trim_messages(self):
        """Keep only the most recent messages"""
        if len(self.chat_messages) > self.max_messages:
            self.chat_messages = self.chat_messages[-self.max_messages:]
    
    def _scroll_to_bottom(self):
        """Scroll to show the most recent messages"""
        max_scroll = max(0, len(self.chat_messages) - self._get_visible_message_count())
        self.scroll_offset = max_scroll