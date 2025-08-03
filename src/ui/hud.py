import pygame
from typing import List
from src.core.constants import *
from src.entities.npc import NPC

class HUD:
    def __init__(self, screen):
        self.screen = screen
        self.font_large = pygame.font.Font(None, 36)
        self.font_medium = pygame.font.Font(None, 24)
        self.font_small = pygame.font.Font(None, 18)
        
        self.show_debug = False
        self.selected_npc = None
        
    def draw(self, fps, ai_status, active_events, npcs, player=None):
        self._draw_top_bar(fps, ai_status)
        self._draw_events_panel(active_events)
        self._draw_npc_info_panel(npcs)
        
        if player:
            self._draw_player_info_panel(player)
        
        if self.show_debug:
            self._draw_debug_info(npcs)
    
    def _draw_top_bar(self, fps, ai_status):
        bar_height = 40
        pygame.draw.rect(self.screen, (40, 40, 40), (0, 0, SCREEN_WIDTH, bar_height))
        pygame.draw.line(self.screen, (80, 80, 80), (0, bar_height), (SCREEN_WIDTH, bar_height), 2)
        
        fps_text = self.font_medium.render(f"FPS: {int(fps)}", True, WHITE)
        self.screen.blit(fps_text, (10, 10))
        
        if ai_status:
            ai_text = self.font_medium.render(f"AI: {ai_status}", True, (100, 255, 100))
            ai_rect = ai_text.get_rect()
            ai_rect.right = SCREEN_WIDTH - 10
            ai_rect.y = 10
            self.screen.blit(ai_text, ai_rect)
        
        controls_text = self.font_small.render("ESC: Menu | F5: Save | I: Debug | Click: Select NPC", True, (150, 150, 150))
        controls_rect = controls_text.get_rect()
        controls_rect.centerx = SCREEN_WIDTH // 2
        controls_rect.y = 12
        self.screen.blit(controls_text, controls_rect)
    
    def _draw_events_panel(self, active_events):
        if not active_events:
            return
        
        panel_width = 300
        panel_height = min(len(active_events) * 25 + 40, 200)
        panel_x = 10
        panel_y = 50
        
        pygame.draw.rect(self.screen, (30, 30, 30, 200), 
                        (panel_x, panel_y, panel_width, panel_height))
        pygame.draw.rect(self.screen, (100, 100, 100), 
                        (panel_x, panel_y, panel_width, panel_height), 2)
        
        title_text = self.font_medium.render("Active Events", True, (255, 255, 100))
        self.screen.blit(title_text, (panel_x + 10, panel_y + 10))
        
        y_offset = panel_y + 35
        for i, event in enumerate(active_events[:6]):
            event_text = self.font_small.render(f"• {event.title}", True, WHITE)
            self.screen.blit(event_text, (panel_x + 15, y_offset))
            y_offset += 20
    
    def _draw_npc_info_panel(self, npcs):
        panel_width = 280
        panel_height = 350
        panel_x = SCREEN_WIDTH - panel_width - 10
        panel_y = 50
        
        pygame.draw.rect(self.screen, (30, 30, 30, 200), 
                        (panel_x, panel_y, panel_width, panel_height))
        pygame.draw.rect(self.screen, (100, 100, 100), 
                        (panel_x, panel_y, panel_width, panel_height), 2)
        
        title_text = self.font_medium.render("NPCs Status", True, (100, 255, 255))
        self.screen.blit(title_text, (panel_x + 10, panel_y + 10))
        
        y_offset = panel_y + 35
        for npc in npcs[:8]:
            self._draw_npc_status(npc, panel_x + 10, y_offset, panel_width - 20)
            y_offset += 40
    
    def _draw_npc_status(self, npc, x, y, width):
        name_text = self.font_small.render(npc.name, True, WHITE)
        self.screen.blit(name_text, (x, y))
        
        # Get emotion from emotional_state if available
        emotion = None
        if hasattr(npc, 'emotional_state') and hasattr(npc.emotional_state, 'primary_emotion'):
            emotion = npc.emotional_state.primary_emotion.value
        elif hasattr(npc, 'emotion'):
            emotion = npc.emotion
        else:
            emotion = 'neutral'
        
        emotion_color = self._get_emotion_color(emotion)
        emotion_text = self.font_small.render(f"({emotion})", True, emotion_color)
        self.screen.blit(emotion_text, (x + 60, y))
        
        state_text = self.font_small.render(npc.state, True, (200, 200, 200))
        state_rect = state_text.get_rect()
        state_rect.right = x + width
        state_rect.y = y
        self.screen.blit(state_text, state_rect)
        
        needs_y = y + 16
        bar_width = 50
        bar_height = 6
        
        needs = ["hunger", "sleep", "social", "fun"]
        colors = [(255, 100, 100), (100, 100, 255), (100, 255, 100), (255, 255, 100)]
        
        for i, (need, color) in enumerate(zip(needs, colors)):
            bar_x = x + i * (bar_width + 5)
            value = npc.needs.get(need, 0)
            
            pygame.draw.rect(self.screen, (50, 50, 50), 
                           (bar_x, needs_y, bar_width, bar_height))
            pygame.draw.rect(self.screen, color, 
                           (bar_x, needs_y, int(bar_width * value), bar_height))
    
    def _get_emotion_color(self, emotion):
        emotion_colors = {
            "happy": (100, 255, 100),
            "sad": (100, 100, 255),
            "angry": (255, 100, 100),
            "excited": (255, 255, 100),
            "neutral": (200, 200, 200),
            "tired": (150, 150, 255),
            "hungry": (255, 150, 100)
        }
        return emotion_colors.get(emotion, (200, 200, 200))
    
    def _draw_player_info_panel(self, player):
        panel_width = 250
        panel_height = 120
        panel_x = 10
        panel_y = SCREEN_HEIGHT - panel_height - 10
        
        pygame.draw.rect(self.screen, (30, 30, 30, 200), 
                        (panel_x, panel_y, panel_width, panel_height))
        pygame.draw.rect(self.screen, (100, 100, 100), 
                        (panel_x, panel_y, panel_width, panel_height), 2)
        
        title_text = self.font_medium.render(f"{player.name} (You)", True, (100, 255, 100))
        self.screen.blit(title_text, (panel_x + 10, panel_y + 10))
        
        # Draw player needs
        y_offset = panel_y + 35
        bar_width = 60
        bar_height = 8
        
        needs = ["hunger", "sleep", "social", "fun"]
        colors = [(255, 100, 100), (100, 100, 255), (100, 255, 100), (255, 255, 100)]
        
        for i, (need, color) in enumerate(zip(needs, colors)):
            if i < 2:
                bar_x = panel_x + 10 + i * (bar_width + 80)
                bar_y = y_offset
            else:
                bar_x = panel_x + 10 + (i - 2) * (bar_width + 80)
                bar_y = y_offset + 25
                
            value = getattr(player, 'needs', {}).get(need, 1.0)
            
            # Need label
            need_text = self.font_small.render(need.capitalize(), True, WHITE)
            self.screen.blit(need_text, (bar_x, bar_y - 15))
            
            # Need bar
            pygame.draw.rect(self.screen, (50, 50, 50), 
                           (bar_x, bar_y, bar_width, bar_height))
            pygame.draw.rect(self.screen, color, 
                           (bar_x, bar_y, int(bar_width * value), bar_height))
            
            # Need value
            value_text = self.font_small.render(f"{value:.1f}", True, WHITE)
            self.screen.blit(value_text, (bar_x + bar_width + 5, bar_y - 2))
        
        # Player personality info
        if hasattr(player, 'personality'):
            personality_str = player.personality.to_prompt_string()
            personality_text_str = "Personality: " + personality_str
            
            # Truncate if too long
            if self.font_small.size(personality_text_str)[0] > panel_width - 20:
                truncated = personality_str[:30] + "..."
                personality_text_str = "Personality: " + truncated
                
            personality_text = self.font_small.render(personality_text_str, True, (200, 200, 200))
            self.screen.blit(personality_text, (panel_x + 10, panel_y + panel_height - 20))
    
    def _draw_debug_info(self, npcs):
        debug_panel_width = 400
        debug_panel_height = 300
        debug_x = SCREEN_WIDTH // 2 - debug_panel_width // 2
        debug_y = SCREEN_HEIGHT - debug_panel_height - 10
        
        pygame.draw.rect(self.screen, (20, 20, 20, 230), 
                        (debug_x, debug_y, debug_panel_width, debug_panel_height))
        pygame.draw.rect(self.screen, (150, 150, 150), 
                        (debug_x, debug_y, debug_panel_width, debug_panel_height), 2)
        
        title_text = self.font_medium.render("Debug Information", True, (255, 200, 100))
        self.screen.blit(title_text, (debug_x + 10, debug_y + 10))
        
        y_offset = debug_y + 35
        
        total_memories = sum(len(npc.memory) for npc in npcs)
        memory_text = self.font_small.render(f"Total Memories: {total_memories}", True, WHITE)
        self.screen.blit(memory_text, (debug_x + 10, y_offset))
        y_offset += 20
        
        active_interactions = sum(1 for npc in npcs if npc.interaction_cooldown > 0)
        interaction_text = self.font_small.render(f"Active Interactions: {active_interactions}", True, WHITE)
        self.screen.blit(interaction_text, (debug_x + 10, y_offset))
        y_offset += 20
        
        ai_decisions = sum(1 for npc in npcs if npc.ai_decision_cooldown > 0)
        ai_text = self.font_small.render(f"NPCs Making Decisions: {ai_decisions}", True, WHITE)
        self.screen.blit(ai_text, (debug_x + 10, y_offset))
        y_offset += 20
        
        if self.selected_npc:
            self._draw_selected_npc_debug(self.selected_npc, debug_x + 10, y_offset)
    
    def _draw_selected_npc_debug(self, npc, x, y):
        npc_text = self.font_small.render(f"Selected: {npc.name}", True, (255, 255, 100))
        self.screen.blit(npc_text, (x, y))
        y += 20
        
        pos_text = self.font_small.render(f"Position: ({npc.rect.x}, {npc.rect.y})", True, WHITE)
        self.screen.blit(pos_text, (x, y))
        y += 20
        
        relationships_text = self.font_small.render("Relationships:", True, WHITE)
        self.screen.blit(relationships_text, (x, y))
        y += 15
        
        for name, value in list(npc.relationships.items())[:3]:
            rel_text = self.font_small.render(f"  {name}: {value:.2f}", True, (200, 200, 200))
            self.screen.blit(rel_text, (x, y))
            y += 15
    
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_i:
                self.show_debug = not self.show_debug
                return True
        return False
    
    def select_npc(self, npc):
        self.selected_npc = npc