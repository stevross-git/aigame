import pygame
import math
from typing import Dict, List, Optional, Tuple
from src.core.constants import *
from src.ui.menu import Button

class DataAnalysisPanel:
    """
    Comprehensive data analysis panel for viewing simulation data.
    Features tabs for relationships, memories, NPC stats, and behavioral patterns.
    """
    
    def __init__(self, screen):
        self.screen = screen
        self.font_title = pygame.font.Font(None, 24)
        self.font_normal = pygame.font.Font(None, 18)
        self.font_small = pygame.font.Font(None, 16)
        self.font_tiny = pygame.font.Font(None, 14)
        
        # Panel state
        self.visible = False
        self.current_tab = "relationships"
        self.tabs = ["relationships", "memories", "npc_stats", "behavior"]
        
        # Panel dimensions and position
        self.width = 600
        self.height = 500
        self.x = (SCREEN_WIDTH - self.width) // 2
        self.y = (SCREEN_HEIGHT - self.height) // 2
        
        # Visual settings
        self.background_color = (25, 30, 35, 240)
        self.tab_active_color = (60, 120, 180)
        self.tab_inactive_color = (40, 50, 60)
        self.border_color = (100, 120, 140)
        self.text_color = WHITE
        self.header_color = (200, 220, 240)
        
        # Data references (set by game)
        self.npcs = []
        self.memory_manager = None
        self.player = None
        
        # Tab content areas
        self.content_rect = pygame.Rect(self.x + 10, self.y + 60, self.width - 20, self.height - 80)
        
        # Scrolling for content
        self.scroll_y = 0
        self.max_scroll = 0
        
        # Memory search
        self.memory_search = ""
        self.memory_search_active = False
        
        # Relationship matrix settings
        self.relationship_cell_size = 40
        
        # UI buttons
        self.close_button = Button(self.x + self.width - 30, self.y + 5, 25, 25, "×", self.hide, 16)
        
        # Tab buttons
        self.tab_buttons = []
        self._create_tab_buttons()
    
    def _create_tab_buttons(self):
        """Create tab navigation buttons"""
        self.tab_buttons = []
        tab_width = 120
        tab_height = 30
        start_x = self.x + 10
        
        tab_names = {
            "relationships": "Relationships",
            "memories": "Memories", 
            "npc_stats": "NPC Stats",
            "behavior": "Behavior"
        }
        
        for i, tab_id in enumerate(self.tabs):
            button = Button(
                start_x + i * (tab_width + 5), self.y + 25,
                tab_width, tab_height,
                tab_names[tab_id],
                lambda t=tab_id: self.set_tab(t),
                16
            )
            self.tab_buttons.append((tab_id, button))
    
    def set_data_sources(self, npcs: List, memory_manager, player):
        """Set data sources for analysis"""
        self.npcs = npcs
        self.memory_manager = memory_manager
        self.player = player
    
    def show(self):
        """Show the analysis panel"""
        self.visible = True
        self.scroll_y = 0
        self._update_scroll_limits()
    
    def hide(self):
        """Hide the analysis panel"""
        self.visible = False
        self.memory_search_active = False
    
    def set_tab(self, tab_id: str):
        """Switch to specific tab"""
        if tab_id in self.tabs:
            self.current_tab = tab_id
            self.scroll_y = 0
            self._update_scroll_limits()
    
    def handle_event(self, event) -> bool:
        """Handle input events"""
        if not self.visible:
            return False
        
        # Handle close button
        if self.close_button.handle_event(event):
            return True
        
        # Handle tab buttons
        for tab_id, button in self.tab_buttons:
            if button.handle_event(event):
                return True
        
        # Handle memory search input
        if self.current_tab == "memories" and self.memory_search_active:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN or event.key == pygame.K_ESCAPE:
                    self.memory_search_active = False
                    return True
                elif event.key == pygame.K_BACKSPACE:
                    self.memory_search = self.memory_search[:-1]
                    return True
                elif event.unicode and len(self.memory_search) < 30:
                    self.memory_search += event.unicode
                    return True
        
        # Handle clicks
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            
            # Check if click is within panel
            panel_rect = pygame.Rect(self.x, self.y, self.width, self.height)
            if not panel_rect.collidepoint(mouse_pos):
                self.hide()
                return True
            
            # Memory search activation
            if self.current_tab == "memories":
                search_rect = pygame.Rect(self.x + 20, self.y + 70, 200, 25)
                if search_rect.collidepoint(mouse_pos):
                    self.memory_search_active = True
                    return True
        
        # Handle scrolling
        if event.type == pygame.MOUSEWHEEL:
            mouse_pos = pygame.mouse.get_pos()
            if self.content_rect.collidepoint(mouse_pos):
                self.scroll_y -= event.y * 20
                self.scroll_y = max(0, min(self.scroll_y, self.max_scroll))
                return True
        
        # Handle keyboard shortcuts
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.hide()
                return True
            elif event.key == pygame.K_TAB:
                # Cycle through tabs
                current_index = self.tabs.index(self.current_tab)
                next_index = (current_index + 1) % len(self.tabs)
                self.set_tab(self.tabs[next_index])
                return True
        
        return True  # Block events from passing through
    
    def update(self, dt):
        """Update panel state"""
        if self.visible:
            self._update_scroll_limits()
    
    def _update_scroll_limits(self):
        """Update scroll limits based on content"""
        if self.current_tab == "relationships":
            matrix_size = len(self.npcs) + 1  # +1 for player
            total_height = matrix_size * self.relationship_cell_size + 100
        elif self.current_tab == "memories":
            memory_count = self._get_filtered_memory_count()
            total_height = memory_count * 60 + 100
        elif self.current_tab == "npc_stats":
            total_height = len(self.npcs) * 120 + 50
        else:  # behavior
            total_height = len(self.npcs) * 200 + 50
        
        self.max_scroll = max(0, total_height - self.content_rect.height)
    
    def _get_filtered_memory_count(self) -> int:
        """Get count of memories matching search filter"""
        if not self.memory_manager:
            return 0
        
        try:
            all_memories = self.memory_manager.get_all_memories()
            if not self.memory_search:
                return len(all_memories)
            
            search_lower = self.memory_search.lower()
            filtered = [m for m in all_memories 
                       if search_lower in m.get('content', '').lower() or 
                          search_lower in m.get('npc_name', '').lower()]
            return len(filtered)
        except:
            return 0
    
    def draw(self):
        """Draw the analysis panel"""
        if not self.visible:
            return
        
        # Draw semi-transparent background
        surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        surface.fill(self.background_color)
        self.screen.blit(surface, (self.x, self.y))
        
        # Draw border
        pygame.draw.rect(self.screen, self.border_color, 
                        (self.x, self.y, self.width, self.height), 2, border_radius=10)
        
        # Draw title
        title_text = self.font_title.render("Data Analysis", True, self.header_color)
        title_rect = title_text.get_rect()
        title_rect.x = self.x + 10
        title_rect.y = self.y + 5
        self.screen.blit(title_text, title_rect)
        
        # Draw close button
        self.close_button.draw(self.screen)
        
        # Draw tabs
        self._draw_tabs()
        
        # Draw content based on current tab
        content_surface = pygame.Surface((self.content_rect.width, self.content_rect.height + self.max_scroll))
        content_surface.fill((0, 0, 0, 0))  # Transparent
        
        if self.current_tab == "relationships":
            self._draw_relationships_content(content_surface)
        elif self.current_tab == "memories":
            self._draw_memories_content(content_surface)
        elif self.current_tab == "npc_stats":
            self._draw_npc_stats_content(content_surface)
        elif self.current_tab == "behavior":
            self._draw_behavior_content(content_surface)
        
        # Blit visible portion of content
        visible_rect = pygame.Rect(0, self.scroll_y, self.content_rect.width, self.content_rect.height)
        self.screen.blit(content_surface, self.content_rect, visible_rect)
        
        # Draw scroll indicator
        if self.max_scroll > 0:
            self._draw_scroll_indicator()
    
    def _draw_tabs(self):
        """Draw tab navigation"""
        for tab_id, button in self.tab_buttons:
            is_active = (tab_id == self.current_tab)
            
            # Custom tab appearance
            color = self.tab_active_color if is_active else self.tab_inactive_color
            pygame.draw.rect(self.screen, color, button.rect, border_radius=5)
            pygame.draw.rect(self.screen, self.border_color, button.rect, 1, border_radius=5)
            
            # Tab text
            text_color = WHITE if is_active else (180, 180, 180)
            text_surface = self.font_normal.render(button.text, True, text_color)
            text_rect = text_surface.get_rect(center=button.rect.center)
            self.screen.blit(text_surface, text_rect)
    
    def _draw_relationships_content(self, surface):
        """Draw relationship matrix"""
        if not self.npcs:
            no_data_text = self.font_normal.render("No NPCs available", True, self.text_color)
            surface.blit(no_data_text, (20, 20))
            return
        
        # Create character list (player + NPCs)
        characters = ["Player"] + [npc.name for npc in self.npcs]
        cell_size = self.relationship_cell_size
        
        # Draw headers
        header_text = self.font_normal.render("Relationship Matrix", True, self.header_color)
        surface.blit(header_text, (20, 10))
        
        # Draw matrix
        start_y = 50
        
        # Column headers
        for i, char_name in enumerate(characters):
            x = 120 + i * cell_size
            y = start_y
            
            # Rotate text for column headers
            text_surface = self.font_small.render(char_name[:8], True, self.text_color)
            rotated = pygame.transform.rotate(text_surface, 45)
            surface.blit(rotated, (x, y))
        
        # Row headers and relationship values
        for i, char1 in enumerate(characters):
            y = start_y + 40 + i * cell_size
            
            # Row header
            row_text = self.font_small.render(char1[:10], True, self.text_color)
            surface.blit(row_text, (20, y + cell_size//4))
            
            for j, char2 in enumerate(characters):
                x = 120 + j * cell_size
                
                # Get relationship value
                rel_value = self._get_relationship_value(char1, char2)
                
                # Color code the cell
                if i == j:  # Self relationship
                    color = (50, 50, 50)
                    text = "—"
                else:
                    intensity = int(rel_value * 255)
                    if rel_value > 0.7:
                        color = (100, intensity, 100)  # Green for strong positive
                    elif rel_value > 0.4:
                        color = (intensity, intensity, 100)  # Yellow for neutral
                    else:
                        color = (intensity, 100, 100)  # Red for negative
                    text = f"{rel_value:.2f}"
                
                # Draw cell
                cell_rect = pygame.Rect(x, y, cell_size, cell_size)
                pygame.draw.rect(surface, color, cell_rect)
                pygame.draw.rect(surface, (100, 100, 100), cell_rect, 1)
                
                # Draw text
                if text != "—":
                    text_surface = self.font_tiny.render(text, True, WHITE)
                    text_rect = text_surface.get_rect(center=cell_rect.center)
                    surface.blit(text_surface, text_rect)
    
    def _get_relationship_value(self, char1: str, char2: str) -> float:
        """Get relationship value between two characters"""
        if char1 == char2:
            return 0.5  # Self relationship
        
        # Player relationships
        if char1 == "Player" and self.player:
            return self.player.relationships.get(char2, 0.3)
        elif char2 == "Player" and self.player:
            # Find NPC with char1 name
            for npc in self.npcs:
                if npc.name == char1:
                    return npc.relationships.get("Player", 0.3)
        
        # NPC to NPC relationships
        for npc in self.npcs:
            if npc.name == char1:
                return npc.relationships.get(char2, 0.3)
        
        return 0.3  # Default neutral
    
    def _draw_memories_content(self, surface):
        """Draw memory timeline and search"""
        # Draw search box
        search_rect = pygame.Rect(20, 20, 200, 25)
        search_color = (60, 60, 60) if not self.memory_search_active else (80, 120, 160)
        pygame.draw.rect(surface, search_color, search_rect)
        pygame.draw.rect(surface, (100, 100, 100), search_rect, 1)
        
        # Search text
        search_display = self.memory_search if self.memory_search else "Search memories..."
        search_text_color = WHITE if self.memory_search else (150, 150, 150)
        search_surface = self.font_small.render(search_display, True, search_text_color)
        surface.blit(search_surface, (search_rect.x + 5, search_rect.y + 5))
        
        # Draw cursor if active
        if self.memory_search_active:
            cursor_x = search_rect.x + 5 + self.font_small.size(self.memory_search)[0]
            pygame.draw.line(surface, WHITE, 
                           (cursor_x, search_rect.y + 5), 
                           (cursor_x, search_rect.y + 20), 1)
        
        # Get and display memories
        if not self.memory_manager:
            no_data_text = self.font_normal.render("No memory manager available", True, self.text_color)
            surface.blit(no_data_text, (20, 60))
            return
        
        try:
            memories = self.memory_manager.get_all_memories()
            
            # Filter memories based on search
            if self.memory_search:
                search_lower = self.memory_search.lower()
                memories = [m for m in memories 
                           if search_lower in m.get('content', '').lower() or 
                              search_lower in m.get('npc_name', '').lower()]
            
            # Sort by timestamp (newest first)
            memories.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
            
            # Display memories
            y_offset = 60
            for i, memory in enumerate(memories[:20]):  # Show latest 20
                self._draw_memory_item(surface, memory, 20, y_offset)
                y_offset += 55
            
            if len(memories) > 20:
                more_text = f"... and {len(memories) - 20} more memories"
                more_surface = self.font_small.render(more_text, True, (150, 150, 150))
                surface.blit(more_surface, (20, y_offset))
        
        except Exception as e:
            error_text = self.font_normal.render(f"Error loading memories: {str(e)[:50]}", True, (255, 100, 100))
            surface.blit(error_text, (20, 60))
    
    def _draw_memory_item(self, surface, memory: Dict, x: int, y: int):
        """Draw individual memory item"""
        # Background
        item_rect = pygame.Rect(x, y, 500, 50)
        pygame.draw.rect(surface, (40, 45, 50), item_rect, border_radius=5)
        pygame.draw.rect(surface, (80, 85, 90), item_rect, 1, border_radius=5)
        
        # NPC name and timestamp
        header = f"{memory.get('npc_name', 'Unknown')} - {memory.get('timestamp', '')[:16]}"
        header_surface = self.font_small.render(header, True, self.header_color)
        surface.blit(header_surface, (x + 5, y + 5))
        
        # Memory content
        content = memory.get('content', 'No content')[:80]
        if len(memory.get('content', '')) > 80:
            content += "..."
        content_surface = self.font_small.render(content, True, self.text_color)
        surface.blit(content_surface, (x + 5, y + 22))
        
        # Memory type and importance
        mem_type = memory.get('memory_type', 'unknown')
        importance = memory.get('importance', 0.0)
        details = f"Type: {mem_type} | Importance: {importance:.2f}"
        details_surface = self.font_tiny.render(details, True, (150, 150, 150))
        surface.blit(details_surface, (x + 5, y + 37))
    
    def _draw_npc_stats_content(self, surface):
        """Draw NPC statistics"""
        if not self.npcs:
            no_data_text = self.font_normal.render("No NPCs available", True, self.text_color)
            surface.blit(no_data_text, (20, 20))
            return
        
        y_offset = 20
        
        for npc in self.npcs:
            self._draw_npc_stat_block(surface, npc, 20, y_offset)
            y_offset += 120
    
    def _draw_npc_stat_block(self, surface, npc, x: int, y: int):
        """Draw statistics block for single NPC"""
        # Background
        block_rect = pygame.Rect(x, y, 550, 110)
        pygame.draw.rect(surface, (35, 40, 45), block_rect, border_radius=8)
        pygame.draw.rect(surface, (80, 90, 100), block_rect, 2, border_radius=8)
        
        # NPC name
        name_surface = self.font_normal.render(npc.name, True, self.header_color)
        surface.blit(name_surface, (x + 10, y + 5))
        
        # Current state and emotion
        # Get emotion from emotional_state if available
        emotion = None
        if hasattr(npc, 'emotional_state') and hasattr(npc.emotional_state, 'primary_emotion'):
            emotion = npc.emotional_state.primary_emotion.value
        elif hasattr(npc, 'emotion'):
            emotion = npc.emotion
        else:
            emotion = 'neutral'
        
        state_text = f"State: {npc.state} | Emotion: {emotion}"
        state_surface = self.font_small.render(state_text, True, self.text_color)
        surface.blit(state_surface, (x + 10, y + 25))
        
        # Needs bars
        needs_y = y + 45
        bar_width = 100
        bar_height = 8
        
        for i, (need, value) in enumerate(npc.needs.items()):
            need_x = x + 10 + (i % 2) * 270
            need_y = needs_y + (i // 2) * 20
            
            # Need label
            need_label = self.font_tiny.render(f"{need.title()}:", True, self.text_color)
            surface.blit(need_label, (need_x, need_y))
            
            # Need bar background
            bar_rect = pygame.Rect(need_x + 60, need_y + 2, bar_width, bar_height)
            pygame.draw.rect(surface, (40, 40, 40), bar_rect)
            
            # Need bar fill
            fill_width = int(bar_width * value)
            if fill_width > 0:
                fill_rect = pygame.Rect(need_x + 60, need_y + 2, fill_width, bar_height)
                # Color code based on need level
                if value > 0.7:
                    color = (100, 200, 100)
                elif value > 0.3:
                    color = (200, 200, 100)
                else:
                    color = (200, 100, 100)
                pygame.draw.rect(surface, color, fill_rect)
            
            # Need value text
            value_text = f"{value:.2f}"
            value_surface = self.font_tiny.render(value_text, True, self.text_color)
            surface.blit(value_surface, (need_x + 170, need_y))
        
        # Relationship count
        rel_count = len(npc.relationships)
        rel_text = f"Relationships: {rel_count}"
        rel_surface = self.font_small.render(rel_text, True, self.text_color)
        surface.blit(rel_surface, (x + 300, y + 25))
    
    def _draw_behavior_content(self, surface):
        """Draw behavior analysis"""
        if not self.npcs:
            no_data_text = self.font_normal.render("No NPCs available", True, self.text_color)
            surface.blit(no_data_text, (20, 20))
            return
        
        header_text = self.font_normal.render("Behavioral Patterns", True, self.header_color)
        surface.blit(header_text, (20, 10))
        
        y_offset = 40
        
        for npc in self.npcs:
            self._draw_behavior_analysis(surface, npc, 20, y_offset)
            y_offset += 180
    
    def _draw_behavior_analysis(self, surface, npc, x: int, y: int):
        """Draw behavior analysis for single NPC"""
        # Background
        block_rect = pygame.Rect(x, y, 550, 170)
        pygame.draw.rect(surface, (30, 35, 40), block_rect, border_radius=8)
        pygame.draw.rect(surface, (70, 80, 90), block_rect, 2, border_radius=8)
        
        # NPC name
        name_surface = self.font_normal.render(f"{npc.name} - Behavior Analysis", True, self.header_color)
        surface.blit(name_surface, (x + 10, y + 5))
        
        # Personality traits visualization
        trait_y = y + 30
        trait_text = self.font_small.render("Personality Traits:", True, self.text_color)
        surface.blit(trait_text, (x + 10, trait_y))
        
        # Draw personality radar chart (simplified)
        center_x = x + 400
        center_y = y + 80
        radius = 50
        
        traits = npc.personality.traits
        trait_names = list(traits.keys())[:6]  # Max 6 traits for clean display
        
        if trait_names:
            angle_step = 2 * math.pi / len(trait_names)
            
            # Draw trait lines
            for i, trait in enumerate(trait_names):
                angle = i * angle_step - math.pi / 2
                value = traits[trait]
                
                end_x = center_x + math.cos(angle) * radius * value
                end_y = center_y + math.sin(angle) * radius * value
                
                pygame.draw.line(surface, (100, 150, 200), (center_x, center_y), (end_x, end_y), 2)
                pygame.draw.circle(surface, (150, 200, 255), (int(end_x), int(end_y)), 3)
                
                # Trait label
                label_x = center_x + math.cos(angle) * (radius + 15)
                label_y = center_y + math.sin(angle) * (radius + 15)
                trait_surface = self.font_tiny.render(trait[:4], True, self.text_color)
                trait_rect = trait_surface.get_rect(center=(label_x, label_y))
                surface.blit(trait_surface, trait_rect)
        
        # Recent actions/decisions
        actions_y = y + 25
        if hasattr(npc, 'memory') and npc.memory:
            recent_actions = [m for m in npc.memory[-3:] if m.get('type') == 'action']
            if recent_actions:
                actions_text = "Recent Actions: " + ", ".join([a.get('action', 'unknown') for a in recent_actions])
            else:
                actions_text = "Recent Actions: idle, wandering"
        else:
            actions_text = "Recent Actions: No data available"
        
        actions_surface = self.font_tiny.render(actions_text[:60], True, (180, 180, 180))
        surface.blit(actions_surface, (x + 10, actions_y + 120))
        
        # AI decision cooldown
        cooldown_text = f"AI Decision Cooldown: {npc.ai_decision_cooldown:.1f}s"
        cooldown_surface = self.font_tiny.render(cooldown_text, True, (180, 180, 180))
        surface.blit(cooldown_surface, (x + 10, actions_y + 140))
    
    def _draw_scroll_indicator(self):
        """Draw scroll indicator"""
        if self.max_scroll <= 0:
            return
        
        # Scroll bar background
        bar_x = self.x + self.width - 15
        bar_y = self.y + 60
        bar_height = self.height - 80
        
        pygame.draw.rect(self.screen, (50, 50, 50), (bar_x, bar_y, 10, bar_height))
        
        # Scroll thumb
        thumb_height = max(20, int(bar_height * (self.content_rect.height / (self.content_rect.height + self.max_scroll))))
        thumb_y = bar_y + int((bar_height - thumb_height) * (self.scroll_y / self.max_scroll))
        
        pygame.draw.rect(self.screen, (120, 120, 120), (bar_x, thumb_y, 10, thumb_height), border_radius=5)