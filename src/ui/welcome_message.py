import pygame
import src.core.constants as constants

class WelcomeMessage:
    """
    Shows a welcome screen with game intro and controls before starting AI
    """
    
    def __init__(self, screen):
        self.screen = screen
        self.visible = False
        self.show_timer = 0.0
        self.auto_hide_time = None  # Don't auto-hide, wait for user click
        
        # Fonts
        self.font_title = pygame.font.Font(None, 32)
        self.font_normal = pygame.font.Font(None, 22)
        self.font_small = pygame.font.Font(None, 18)
        
        # Colors
        self.bg_color = (20, 25, 35, 200)
        self.panel_color = (45, 55, 70, 240)
        self.border_color = (100, 150, 200)
        self.text_color = (255, 255, 255)
        self.highlight_color = (100, 200, 255)
        self.key_color = (150, 255, 150)
        
        # Panel dimensions - larger for intro text
        self.panel_width = 650
        self.panel_height = 500
        self.panel_x = (constants.SCREEN_WIDTH - self.panel_width) // 2
        self.panel_y = (constants.SCREEN_HEIGHT - self.panel_height) // 2
        
        # OK button
        self.button_width = 120
        self.button_height = 40
        self.button_x = self.panel_x + (self.panel_width - self.button_width) // 2
        self.button_y = self.panel_y + self.panel_height - 60
        self.button_rect = pygame.Rect(self.button_x, self.button_y, self.button_width, self.button_height)
        self.button_hovered = False
    
    def show(self):
        """Show the welcome message"""
        self.visible = True
        self.show_timer = 0.0
    
    def hide(self):
        """Hide the welcome message"""
        self.visible = False
    
    def update(self, dt):
        """Update the welcome message"""
        if self.visible:
            self.show_timer += dt
            # Check mouse hover for button
            mouse_pos = pygame.mouse.get_pos()
            self.button_hovered = self.button_rect.collidepoint(mouse_pos)
    
    def handle_event(self, event) -> bool:
        """Handle events for the welcome message"""
        if not self.visible:
            return False
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE or event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
                self.hide()
                return True
            elif event.key == pygame.K_F1:
                # Open full help system
                self.hide()
                return False  # Let the game handle F1
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                if self.button_rect.collidepoint(event.pos):
                    self.hide()
                    return True
        
        return True  # Consume all events when visible
    
    def draw(self):
        """Draw the welcome message"""
        if not self.visible:
            return
        
        # Semi-transparent background overlay
        overlay = pygame.Surface((constants.SCREEN_WIDTH, constants.SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill(self.bg_color)
        self.screen.blit(overlay, (0, 0))
        
        # Main panel
        panel_rect = pygame.Rect(self.panel_x, self.panel_y, self.panel_width, self.panel_height)
        pygame.draw.rect(self.screen, self.panel_color, panel_rect, border_radius=10)
        pygame.draw.rect(self.screen, self.border_color, panel_rect, 3, border_radius=10)
        
        # Title
        title_text = self.font_title.render("🌟 Welcome to AI Sims! 🌟", True, self.highlight_color)
        title_rect = title_text.get_rect()
        title_rect.centerx = self.panel_x + self.panel_width // 2
        title_rect.y = self.panel_y + 20
        self.screen.blit(title_text, title_rect)
        
        # Content
        content_y = self.panel_y + 70
        line_height = 24
        
        content_lines = [
            "🎮 Life Simulation Adventure",
            "",
            "You can explore this virtual world freely!",
            "Move around, visit buildings, and get familiar with the environment.",
            "",
            "✨ Controls:",
            "• WASD / Arrow Keys - Move your character",
            "• E - Interact with NPCs and objects", 
            "• C / T - Chat with NPCs",
            "• M - Toggle mini-map",
            "• Space - Pause game",
            "• ESC - Main menu",
            "",
            "🤖 Ready to start the full AI experience?",
            "Click OK below to activate NPCs and begin your adventure!",
            "",
            "(You can explore without AI active until you click OK)"
        ]
        
        for i, line in enumerate(content_lines):
            y_pos = content_y + i * line_height
            
            if line.startswith("🎮") or line.startswith("✨") or line.startswith("🤖"):
                # Headers with emojis
                text_surface = self.font_normal.render(line, True, self.highlight_color)
            elif line.startswith("•"):
                # Bullet points
                text_surface = self.font_small.render(line, True, self.text_color)
            elif line.startswith("("):
                # Parenthetical notes
                text_surface = self.font_small.render(line, True, (180, 180, 180))
            elif line.strip() == "":
                # Empty line
                continue
            else:
                # Regular text
                text_surface = self.font_small.render(line, True, self.text_color)
            
            text_rect = text_surface.get_rect()
            text_rect.centerx = self.panel_x + self.panel_width // 2
            text_rect.y = y_pos
            self.screen.blit(text_surface, text_rect)
        
        # OK Button
        button_color = (80, 150, 80) if self.button_hovered else (60, 120, 60)
        border_color = (120, 200, 120) if self.button_hovered else (100, 160, 100)
        
        pygame.draw.rect(self.screen, button_color, self.button_rect, border_radius=5)
        pygame.draw.rect(self.screen, border_color, self.button_rect, 2, border_radius=5)
        
        # OK button text
        button_text = self.font_normal.render("START GAME", True, (255, 255, 255))
        button_text_rect = button_text.get_rect()
        button_text_rect.center = self.button_rect.center
        self.screen.blit(button_text, button_text_rect)