import pygame
from src.core.constants import *

class Camera:
    def __init__(self, width, height):
        self.camera = pygame.Rect(0, 0, width, height)
        self.width = width
        self.height = height
    
    def apply(self, entity):
        return entity.rect.move(self.camera.topleft)
    
    def apply_rect(self, rect):
        return rect.move(self.camera.topleft)
    
    def update(self, target):
        x = -target.rect.centerx + int(self.width / 2)
        y = -target.rect.centery + int(self.height / 2)
        
        x = min(0, x)
        y = min(0, y)
        x = max(-(MAP_WIDTH - self.width), x)
        y = max(-(MAP_HEIGHT - self.height), y)
        
        self.camera = pygame.Rect(x, y, self.width, self.height)