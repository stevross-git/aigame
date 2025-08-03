import pygame
import src.core.constants as constants

class Camera:
    def __init__(self, width, height):
        self.camera = pygame.Rect(0, 0, width, height)
        self.width = width
        self.height = height
        self.shake_x = 0
        self.shake_y = 0
    
    def apply(self, entity):
        return entity.rect.move(self.camera.x + self.shake_x, self.camera.y + self.shake_y)
    
    def apply_rect(self, rect):
        return rect.move(self.camera.x + self.shake_x, self.camera.y + self.shake_y)
    
    def update(self, target):
        x = -target.rect.centerx + int(self.width / 2)
        y = -target.rect.centery + int(self.height / 2)
        
        # Get camera shake from player if available
        if hasattr(target, 'get_camera_shake'):
            self.shake_x, self.shake_y = target.get_camera_shake()
        
        x = min(0, x)
        y = min(0, y)
        x = max(-(constants.MAP_WIDTH - self.width), x)
        y = max(-(constants.MAP_HEIGHT - self.height), y)
        
        self.camera = pygame.Rect(x, y, self.width, self.height)