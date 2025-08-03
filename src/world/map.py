import pygame
import random
import src.core.constants as constants

class Map:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.tiles = []
        self.buildings = []
        self._generate_map()
    
    def _generate_map(self):
        self.buildings = [
            {"x": 100, "y": 100, "width": 150, "height": 150, "type": "house"},
            {"x": 500, "y": 200, "width": 200, "height": 150, "type": "shop"},
            {"x": 300, "y": 400, "width": 150, "height": 200, "type": "house"},
            {"x": 700, "y": 500, "width": 180, "height": 180, "type": "park"},
        ]
        
        for _ in range(10):
            path = {
                "x": random.randint(0, self.width - 50),
                "y": random.randint(0, self.height - 200),
                "width": 50,
                "height": 200,
                "type": "path"
            }
            self.buildings.append(path)
    
    def draw(self, screen, camera):
        visible_rect = pygame.Rect(-camera.camera.x, -camera.camera.y, 
                                  camera.width, camera.height)
        
        for y in range(0, self.height, constants.TILE_SIZE):
            for x in range(0, self.width, constants.TILE_SIZE):
                tile_rect = pygame.Rect(x, y, constants.TILE_SIZE, constants.TILE_SIZE)
                if visible_rect.colliderect(tile_rect):
                    screen_rect = camera.apply_rect(tile_rect)
                    pygame.draw.rect(screen, constants.GREEN, screen_rect)
                    pygame.draw.rect(screen, (40, 140, 40), screen_rect, 1)
        
        for building in self.buildings:
            rect = pygame.Rect(building["x"], building["y"], 
                             building["width"], building["height"])
            if visible_rect.colliderect(rect):
                screen_rect = camera.apply_rect(rect)
                
                if building["type"] == "house":
                    color = (139, 69, 19)
                elif building["type"] == "shop":
                    color = (100, 100, 200)
                elif building["type"] == "park":
                    color = (34, 139, 34)
                else:
                    color = GRAY
                
                pygame.draw.rect(screen, color, screen_rect)
                pygame.draw.rect(screen, BLACK, screen_rect, 2)