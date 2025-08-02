import pygame
import json
from typing import Callable, Optional
from src.core.constants import *

class Button:
    def __init__(self, x, y, width, height, text, callback, font_size=24):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.callback = callback
        self.font = pygame.font.Font(None, font_size)
        self.hovered = False
        self.enabled = True
    
    def handle_event(self, event):
        if not self.enabled:
            return False
            
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and self.rect.collidepoint(event.pos):
                self.callback()
                return True
        elif event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
        
        return False
    
    def draw(self, screen):
        color = (100, 100, 100) if not self.enabled else (70, 130, 180) if self.hovered else (60, 60, 60)
        border_color = (200, 200, 200) if self.hovered else (150, 150, 150)
        
        pygame.draw.rect(screen, color, self.rect, border_radius=5)
        pygame.draw.rect(screen, border_color, self.rect, 2, border_radius=5)
        
        text_color = (200, 200, 200) if not self.enabled else WHITE
        text_surface = self.font.render(self.text, True, text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

class MainMenu:
    def __init__(self, screen):
        self.screen = screen
        self.font_title = pygame.font.Font(None, 72)
        self.font_subtitle = pygame.font.Font(None, 32)
        
        center_x = SCREEN_WIDTH // 2
        self.buttons = [
            Button(center_x - 100, 300, 200, 50, "New Game", self._new_game),
            Button(center_x - 100, 370, 200, 50, "Load Game", self._load_game),
            Button(center_x - 100, 440, 200, 50, "Settings", self._settings),
            Button(center_x - 100, 510, 200, 50, "Exit", self._exit),
        ]
        
        self.on_new_game = None
        self.on_load_game = None
        self.on_settings = None
        self.on_exit = None
        
        self._check_save_exists()
    
    def _check_save_exists(self):
        try:
            with open("savegame.json", "r"):
                pass
        except FileNotFoundError:
            self.buttons[1].enabled = False
    
    def _new_game(self):
        if self.on_new_game:
            self.on_new_game()
    
    def _load_game(self):
        if self.on_load_game:
            self.on_load_game()
    
    def _settings(self):
        if self.on_settings:
            self.on_settings()
    
    def _exit(self):
        if self.on_exit:
            self.on_exit()
    
    def handle_event(self, event):
        for button in self.buttons:
            if button.handle_event(event):
                return True
        return False
    
    def draw(self):
        self.screen.fill((30, 30, 50))
        
        title_text = self.font_title.render("AI Sims", True, WHITE)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, 150))
        self.screen.blit(title_text, title_rect)
        
        subtitle_text = self.font_subtitle.render("Life Simulation with AI NPCs", True, (200, 200, 200))
        subtitle_rect = subtitle_text.get_rect(center=(SCREEN_WIDTH // 2, 200))
        self.screen.blit(subtitle_text, subtitle_rect)
        
        for button in self.buttons:
            button.draw(self.screen)

class PauseMenu:
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.Font(None, 48)
        
        center_x = SCREEN_WIDTH // 2
        self.buttons = [
            Button(center_x - 100, 300, 200, 50, "Resume", self._resume),
            Button(center_x - 100, 370, 200, 50, "Save Game", self._save),
            Button(center_x - 100, 440, 200, 50, "Main Menu", self._main_menu),
        ]
        
        self.on_resume = None
        self.on_save = None
        self.on_main_menu = None
    
    def _resume(self):
        if self.on_resume:
            self.on_resume()
    
    def _save(self):
        if self.on_save:
            self.on_save()
    
    def _main_menu(self):
        if self.on_main_menu:
            self.on_main_menu()
    
    def handle_event(self, event):
        for button in self.buttons:
            if button.handle_event(event):
                return True
        return False
    
    def draw(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))
        
        title_text = self.font.render("Game Paused", True, WHITE)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, 200))
        self.screen.blit(title_text, title_rect)
        
        for button in self.buttons:
            button.draw(self.screen)