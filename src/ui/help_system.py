import pygame
from typing import List, Dict, Tuple
from src.core.constants import *

class HelpPage:
    """Represents a single help page with content"""
    def __init__(self, title: str, content: List[str], tips: List[str] = None):
        self.title = title
        self.content = content
        self.tips = tips or []

class HelpSystem:
    """
    Comprehensive help system with multiple pages of instructions and tips
    """
    
    def __init__(self, screen):
        self.screen = screen
        self.visible = False
        self.current_page = 0
        
        # Fonts
        self.font_title = pygame.font.Font(None, 28)
        self.font_heading = pygame.font.Font(None, 24)
        self.font_normal = pygame.font.Font(None, 20)
        self.font_small = pygame.font.Font(None, 18)
        
        # Colors
        self.bg_color = (20, 25, 35, 240)
        self.panel_color = (45, 55, 70, 220)
        self.border_color = (100, 120, 150)
        self.text_color = (255, 255, 255)
        self.heading_color = (150, 200, 255)
        self.tip_color = (255, 220, 100)
        self.key_color = (100, 255, 100)
        
        # Panel dimensions
        self.panel_width = 700
        self.panel_height = 500
        self.panel_x = (SCREEN_WIDTH - self.panel_width) // 2
        self.panel_y = (SCREEN_HEIGHT - self.panel_height) // 2
        
        self.scroll_offset = 0
        self.max_scroll = 0
        
        self._create_help_pages()
    
    def _create_help_pages(self):
        """Create all help pages with comprehensive information"""
        self.pages = [
            # Page 1: Basic Controls
            HelpPage(
                "Basic Controls & Movement",
                [
                    "🎮 MOVEMENT:",
                    "• WASD or Arrow Keys - Move your character",
                    "• Mouse - Click to move to a location",
                    "",
                    "🎯 CAMERA:",
                    "• Camera automatically follows your character",
                    "• Stay within the map boundaries",
                    "",
                    "⏸️ GAME CONTROL:",
                    "• ESC - Pause game / Open pause menu",
                    "• F5 - Save game",
                    "",
                    "🏃 SPEED CONTROL:",
                    "• Speed controller in top-left corner",
                    "• Click + and - buttons to adjust game speed",
                    "• F6 - Toggle speed controller visibility",
                ],
                [
                    "💡 TIP: Click anywhere on the map to make your character walk there!",
                    "💡 TIP: Use the speed controller to slow down or speed up the game",
                    "💡 TIP: Save frequently with F5 to preserve your progress"
                ]
            ),
            
            # Page 2: NPC Interaction
            HelpPage(
                "NPC Interaction & Communication",
                [
                    "👥 FINDING NPCs:",
                    "• NPCs wander around the map with colorful names above them",
                    "• Check the NPC panel on the right side for their status",
                    "",
                    "💬 TALKING TO NPCs:",
                    "• E - Quick interact with nearby NPCs",
                    "• C or T - Open chat interface with nearby NPCs",
                    "• Left Click - Select an NPC to see details",
                    "",
                    "🗨️ CHAT INTERFACE:",
                    "• Type messages and press Enter to send",
                    "• NPCs will respond with AI-generated replies",
                    "• ESC - Close chat interface",
                    "",
                    "📊 NPC INFORMATION:",
                    "• Right panel shows NPC names, moods, and activities",
                    "• Selected NPC shows detailed needs and relationships",
                    "• Mood indicators: 😊 Happy, 😔 Sad, 😠 Angry, etc.",
                ],
                [
                    "💡 TIP: NPCs have personalities and remember your interactions!",
                    "💡 TIP: Click on NPCs to select them and see detailed information",
                    "💡 TIP: NPCs' moods affect how they respond to you"
                ]
            ),
            
            # Page 3: Player Needs & House System
            HelpPage(
                "Player Needs & House System",
                [
                    "📊 PLAYER NEEDS (Bottom-left panel):",
                    "• Food - Hunger level (red when low)",
                    "• Energy - Sleep level (blue/purple when low)", 
                    "• Social - Social interaction level (blue when low)",
                    "• Fun - Entertainment level (yellow when low)",
                    "",
                    "🏠 YOUR HOUSE:",
                    "• H - Enter/exit your house when nearby",
                    "• Look for the interactive house building on the map",
                    "",
                    "🛏️ HOUSE ACTIVITIES:",
                    "• Bed - Sleep to restore energy (+80% sleep, +30% fun)",
                    "• Kitchen - Cook and eat (+60% hunger, +10% fun)",
                    "• Living Room - Relax and watch TV (+40% fun, +10% sleep)",
                    "• Bathroom - Freshen up (small boosts to all needs)",
                    "",
                    "🎮 HOUSE CONTROLS:",
                    "• E or Space - Interact with nearby furniture",
                    "• Left Click - Click directly on furniture",
                    "• H or ESC - Exit house",
                ],
                [
                    "💡 TIP: Keep an eye on your needs - low needs affect your character!",
                    "💡 TIP: Visit your house regularly to maintain your needs",
                    "💡 TIP: Different furniture restores different needs"
                ]
            ),
            
            # Page 4: Skills & Resources
            HelpPage(
                "Skills & Resource System",
                [
                    "📈 SKILLS SYSTEM:",
                    "• 10 different skills to master: Farming, Mining, Foraging, etc.",
                    "• Gain experience by performing related activities",
                    "• Higher levels provide better yields and bonuses",
                    "• Earn skill points when leveling up",
                    "",
                    "🎒 INVENTORY MANAGEMENT:",
                    "• I - Open inventory (36 slots)",
                    "• Items have quality stars (1-5 ⭐)",
                    "• Different item types: Resources, Tools, Food, etc.",
                    "• Gold currency for buying and selling",
                    "",
                    "⚒️ RESOURCE GATHERING:",
                    "• R - Harvest nearby resources (trees, rocks, plants)",
                    "• Different tools required for different resources",
                    "• Resources regenerate over time",
                    "• Higher skill levels = better yields",
                    "",
                    "🔨 CRAFTING SYSTEM:",
                    "• J - Open crafting menu",
                    "• Combine resources to create new items",
                    "• Unlock recipes by leveling skills",
                    "• Craft tools, food, and furniture",
                ],
                [
                    "💡 TIP: Start by harvesting wood and stone to get basic resources",
                    "💡 TIP: Check your skills (K key) to see progress and bonuses",
                    "💡 TIP: Higher quality items sell for more gold"
                ]
            ),
            
            # Page 5: Advanced Features
            HelpPage(
                "Advanced Features & UI",
                [
                    "🔧 DEBUG & MONITORING:",
                    "• F1 - Toggle help system (this window)",
                    "• F2 - Toggle AI response box",
                    "• F3 - Toggle cost monitor",
                    "• F4 - Reset session costs",
                    "• F7 - Toggle data analysis panel",
                    "• F8 - Clear AI responses",
                    "• F12 - Toggle debug information",
                    "",
                    "⚡ AI SYSTEM:",
                    "• NPCs use AI to make decisions and respond",
                    "• AI responses appear in the response box",
                    "• Costs are monitored in the cost panel",
                    "",
                    "📅 TIME SYSTEM:",
                    "• Game has its own time that progresses",
                    "• NPCs follow daily routines",
                    "• Events may occur at specific times",
                    "",
                    "🎪 EVENTS:",
                    "• Special events appear in the top-center panel",
                    "• NPCs may attend or react to events",
                    "• Events can affect NPC moods and behaviors",
                ],
                [
                    "💡 TIP: Use F2 to see what NPCs are thinking and deciding",
                    "💡 TIP: The data analysis panel shows detailed game statistics",
                    "💡 TIP: Events create dynamic interactions between NPCs"
                ]
            ),
            
            # Page 5: Troubleshooting & Tips
            HelpPage(
                "Troubleshooting & Pro Tips",
                [
                    "❓ COMMON ISSUES:",
                    "• NPCs not responding? Check if AI is properly configured",
                    "• Can't enter house? Make sure you're close enough (80 pixels)",
                    "• Chat not working? Try clicking the NPC first to select them",
                    "• Game too fast/slow? Use the speed controller (top-left)",
                    "",
                    "🎯 PRO TIPS:",
                    "• Save regularly with F5 to avoid losing progress",
                    "• Monitor your needs to maintain optimal character performance",
                    "• Build relationships with NPCs through regular interaction",
                    "• Use the pause menu (ESC) to access settings",
                    "",
                    "🔄 PERFORMANCE:",
                    "• Close unused UI panels to improve performance",
                    "• Lower game speed if experiencing lag",
                    "• Use F12 to check FPS and debug information",
                    "",
                    "💾 SAVING & LOADING:",
                    "• Game auto-saves every 5 minutes",
                    "• Manual save with F5",
                    "• Progress includes NPC relationships and memories",
                ],
                [
                    "💡 TIP: This is a life simulation - take your time and explore!",
                    "💡 TIP: NPCs have complex AI - every interaction matters",
                    "💡 TIP: Check the right panel to see what NPCs are up to"
                ]
            )
        ]
    
    def show(self):
        """Show the help system"""
        self.visible = True
        self.current_page = 0
        self.scroll_offset = 0
    
    def hide(self):
        """Hide the help system"""
        self.visible = False
    
    def toggle(self):
        """Toggle help system visibility"""
        if self.visible:
            self.hide()
        else:
            self.show()
    
    def next_page(self):
        """Go to next page"""
        if self.current_page < len(self.pages) - 1:
            self.current_page += 1
            self.scroll_offset = 0
    
    def prev_page(self):
        """Go to previous page"""
        if self.current_page > 0:
            self.current_page -= 1
            self.scroll_offset = 0
    
    def scroll_up(self):
        """Scroll content up"""
        self.scroll_offset = max(0, self.scroll_offset - 20)
    
    def scroll_down(self):
        """Scroll content down"""
        self.scroll_offset = min(self.max_scroll, self.scroll_offset + 20)
    
    def handle_event(self, event) -> bool:
        """Handle help system events"""
        if not self.visible:
            return False
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE or event.key == pygame.K_F1:
                self.hide()
                return True
            elif event.key == pygame.K_LEFT:
                self.prev_page()
                return True
            elif event.key == pygame.K_RIGHT:
                self.next_page()
                return True
            elif event.key == pygame.K_UP:
                self.scroll_up()
                return True
            elif event.key == pygame.K_DOWN:
                self.scroll_down()
                return True
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                mouse_x, mouse_y = event.pos
                
                # Check if click is on navigation buttons
                if self._is_in_nav_area(mouse_x, mouse_y):
                    self._handle_nav_click(mouse_x, mouse_y)
                    return True
                
                # Check if click is outside panel (close help)
                panel_rect = pygame.Rect(self.panel_x, self.panel_y, self.panel_width, self.panel_height)
                if not panel_rect.collidepoint(mouse_x, mouse_y):
                    self.hide()
                    return True
        
        elif event.type == pygame.MOUSEWHEEL:
            if event.y > 0:
                self.scroll_up()
            else:
                self.scroll_down()
            return True
        
        return True  # Consume all events when visible
    
    def _is_in_nav_area(self, mouse_x: int, mouse_y: int) -> bool:
        """Check if mouse is in navigation area"""
        nav_y = self.panel_y + self.panel_height - 40
        return (self.panel_x <= mouse_x <= self.panel_x + self.panel_width and
                nav_y <= mouse_y <= nav_y + 30)
    
    def _handle_nav_click(self, mouse_x: int, mouse_y: int):
        """Handle navigation button clicks"""
        # Previous button
        prev_button_x = self.panel_x + 20
        prev_button_width = 80
        
        # Next button  
        next_button_x = self.panel_x + self.panel_width - 100
        next_button_width = 80
        
        if prev_button_x <= mouse_x <= prev_button_x + prev_button_width:
            self.prev_page()
        elif next_button_x <= mouse_x <= next_button_x + next_button_width:
            self.next_page()
    
    def draw(self):
        """Draw the help system"""
        if not self.visible:
            return
        
        # Semi-transparent background overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill(self.bg_color)
        self.screen.blit(overlay, (0, 0))
        
        # Main panel
        panel_rect = pygame.Rect(self.panel_x, self.panel_y, self.panel_width, self.panel_height)
        pygame.draw.rect(self.screen, self.panel_color, panel_rect, border_radius=10)
        pygame.draw.rect(self.screen, self.border_color, panel_rect, 3, border_radius=10)
        
        # Current page
        current_page = self.pages[self.current_page]
        
        # Title
        title_text = self.font_title.render(f"Help - {current_page.title}", True, self.heading_color)
        title_rect = title_text.get_rect()
        title_rect.centerx = self.panel_x + self.panel_width // 2
        title_rect.y = self.panel_y + 15
        self.screen.blit(title_text, title_rect)
        
        # Content area
        content_y = self.panel_y + 50
        content_height = self.panel_height - 100
        content_rect = pygame.Rect(self.panel_x + 20, content_y, self.panel_width - 40, content_height)
        
        # Draw content with scrolling
        self._draw_scrollable_content(current_page, content_rect)
        
        # Navigation
        self._draw_navigation()
        
        # Instructions
        self._draw_instructions()
    
    def _draw_scrollable_content(self, page: HelpPage, content_rect: pygame.Rect):
        """Draw scrollable content"""
        # Create a surface for the content
        content_surface = pygame.Surface((content_rect.width, content_rect.height + 200), pygame.SRCALPHA)
        
        y_offset = -self.scroll_offset
        line_height = 22
        
        # Draw main content
        for line in page.content:
            if line.startswith("🎮") or line.startswith("👥") or line.startswith("📊") or line.startswith("🔧") or line.startswith("❓"):
                # Section headers
                text_surface = self.font_heading.render(line, True, self.heading_color)
            elif line.startswith("•"):
                # Bullet points
                text_surface = self.font_normal.render(line, True, self.text_color)
            elif line.strip() == "":
                # Empty line
                y_offset += line_height // 2
                continue
            else:
                # Regular text
                text_surface = self.font_normal.render(line, True, self.text_color)
            
            if y_offset >= -line_height and y_offset < content_rect.height:
                content_surface.blit(text_surface, (10, y_offset))
            
            y_offset += line_height
        
        # Draw tips section
        if page.tips:
            y_offset += 20
            tips_header = self.font_heading.render("💡 Pro Tips:", True, self.tip_color)
            if y_offset >= -line_height and y_offset < content_rect.height:
                content_surface.blit(tips_header, (10, y_offset))
            y_offset += line_height + 5
            
            for tip in page.tips:
                tip_surface = self.font_small.render(tip, True, self.tip_color)
                if y_offset >= -line_height and y_offset < content_rect.height:
                    content_surface.blit(tip_surface, (10, y_offset))
                y_offset += line_height
        
        # Calculate max scroll
        self.max_scroll = max(0, y_offset + self.scroll_offset - content_rect.height + 40)
        
        # Blit content to screen with clipping
        self.screen.blit(content_surface, content_rect, 
                        (0, 0, content_rect.width, content_rect.height))
    
    def _draw_navigation(self):
        """Draw navigation buttons"""
        nav_y = self.panel_y + self.panel_height - 35
        
        # Previous button
        prev_color = self.key_color if self.current_page > 0 else (100, 100, 100)
        prev_text = self.font_normal.render("← Previous", True, prev_color)
        self.screen.blit(prev_text, (self.panel_x + 20, nav_y))
        
        # Page indicator
        page_text = f"Page {self.current_page + 1} of {len(self.pages)}"
        page_surface = self.font_normal.render(page_text, True, self.text_color)
        page_rect = page_surface.get_rect()
        page_rect.centerx = self.panel_x + self.panel_width // 2
        page_rect.y = nav_y
        self.screen.blit(page_surface, page_rect)
        
        # Next button
        next_color = self.key_color if self.current_page < len(self.pages) - 1 else (100, 100, 100)
        next_text = self.font_normal.render("Next →", True, next_color)
        next_rect = next_text.get_rect()
        next_rect.right = self.panel_x + self.panel_width - 20
        next_rect.y = nav_y
        self.screen.blit(next_text, next_rect)
    
    def _draw_instructions(self):
        """Draw control instructions"""
        instructions = [
            "ESC/F1: Close Help",
            "← →: Navigate Pages", 
            "↑ ↓: Scroll",
            "Mouse Wheel: Scroll"
        ]
        
        instr_y = self.panel_y + self.panel_height + 10
        for i, instruction in enumerate(instructions):
            instr_surface = self.font_small.render(instruction, True, (200, 200, 200))
            instr_rect = instr_surface.get_rect()
            instr_rect.x = self.panel_x + (i * 150)
            instr_rect.y = instr_y
            self.screen.blit(instr_surface, instr_rect)
    
    def update(self, dt):
        """Update the help system"""
        pass  # No animations currently, but could add smooth scrolling here