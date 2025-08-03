import pygame
import math
import random
from typing import Dict, List, Optional, Tuple
from enum import Enum
from src.core.constants import *

class MovementState(Enum):
    IDLE = "idle"
    WALKING = "walking"
    RUNNING = "running"
    CARRYING = "carrying"
    GATHERING = "gathering"
    EXHAUSTED = "exhausted"

class InteractionType(Enum):
    RESOURCE = "resource"
    NPC = "npc"
    BUILDING = "building"
    ITEM = "item"
    CONTAINER = "container"

class PlayerMovementSystem:
    """
    Enhanced player movement system with inventory weight, stamina, and resource interaction
    """
    
    def __init__(self, player, inventory_system, resource_system, skill_system):
        self.player = player
        self.inventory = inventory_system
        self.resources = resource_system
        self.skills = skill_system
        
        # Movement properties
        self.base_speed = PLAYER_SPEED
        self.current_speed = self.base_speed
        self.max_speed = self.base_speed * 2.5  # Running speed
        self.movement_state = MovementState.IDLE
        
        # Stamina system
        self.max_stamina = 100.0
        self.current_stamina = self.max_stamina
        self.stamina_drain_rate = 15.0  # Per second while running
        self.stamina_regen_rate = 8.0   # Per second while not running
        self.exhausted_threshold = 10.0
        
        # Weight system
        self.max_carry_weight = 100.0  # Base carrying capacity
        self.current_weight = 0.0
        self.overweight_threshold = 0.8  # 80% of max weight
        
        # Movement effects
        self.movement_particles = []
        self.interaction_range = 60
        self.auto_pickup_range = 40
        self.nearby_resources = []
        self.nearby_interactables = []
        
        # Visual feedback
        self.weight_indicator_visible = False
        self.stamina_indicator_visible = False
        self.interaction_hints = []
        
        # Movement smoothing
        self.velocity_smoothing = 0.15
        self.target_velocity = pygame.math.Vector2(0, 0)
        self.current_velocity = pygame.math.Vector2(0, 0)
        
        # Auto-movement features
        self.auto_move_target = None
        self.auto_move_speed = 0.7  # Slower than manual movement
        self.path_finding_enabled = True
        
        # Resource magnetism (when close to resources)
        self.resource_magnetism_range = 25
        self.magnetism_strength = 0.3
        
    def update(self, dt: float, keys_pressed: Dict[int, bool]):
        """Update player movement system"""
        # Update weight from inventory
        self._update_carry_weight()
        
        # Handle input and movement
        self._handle_movement_input(dt, keys_pressed)
        
        # Update stamina
        self._update_stamina(dt)
        
        # Apply movement effects
        self._apply_movement_effects(dt)
        
        # Update nearby interactables
        self._update_nearby_objects()
        
        # Update visual effects
        self._update_visual_effects(dt)
        
        # Handle auto-pickup
        self._handle_auto_pickup()
        
        # Apply resource magnetism
        self._apply_resource_magnetism(dt)
    
    def _update_carry_weight(self):
        """Calculate current carrying weight from inventory"""
        total_weight = 0.0
        
        for item_id, inv_item in self.inventory.get_all_items().items():
            item_data = self.inventory.get_item_data(item_id)
            if item_data:
                # Different items have different weights
                item_weight = self._get_item_weight(item_data.item_type, item_data.base_value)
                total_weight += item_weight * inv_item.quantity
        
        self.current_weight = total_weight
        
        # Show weight indicator if carrying significant weight
        self.weight_indicator_visible = self.current_weight > (self.max_carry_weight * 0.3)
    
    def _get_item_weight(self, item_type, base_value: int) -> float:
        """Get weight of an item based on type and value"""
        from src.systems.inventory_system import ItemType
        
        weight_multipliers = {
            ItemType.TOOL: 3.0,       # Tools are heavy
            ItemType.RESOURCE: 1.0,   # Standard weight
            ItemType.MINERAL: 2.0,    # Minerals are heavy
            ItemType.FOOD: 0.5,       # Food is light
            ItemType.SEED: 0.1,       # Seeds are very light
            ItemType.CROP: 0.8,       # Crops are light-medium
            ItemType.FISH: 1.2,       # Fish have medium weight
            ItemType.CRAFTED: 1.5,    # Crafted items vary
            ItemType.FURNITURE: 5.0,  # Furniture is very heavy
            ItemType.ARTIFACT: 0.3    # Artifacts are light but valuable
        }
        
        base_weight = max(0.1, base_value * 0.01)  # Higher value = more weight
        multiplier = weight_multipliers.get(item_type, 1.0)
        return base_weight * multiplier
    
    def _handle_movement_input(self, dt: float, keys_pressed: Dict[int, bool]):
        """Handle player movement input with weight and stamina effects"""
        # Calculate movement direction
        move_x = 0
        move_y = 0
        
        if keys_pressed.get(pygame.K_LEFT) or keys_pressed.get(pygame.K_a):
            move_x -= 1
        if keys_pressed.get(pygame.K_RIGHT) or keys_pressed.get(pygame.K_d):
            move_x += 1
        if keys_pressed.get(pygame.K_UP) or keys_pressed.get(pygame.K_w):
            move_y -= 1
        if keys_pressed.get(pygame.K_DOWN) or keys_pressed.get(pygame.K_s):
            move_y += 1
        
        # Check if trying to run (shift key)
        is_running = (keys_pressed.get(pygame.K_LSHIFT) or keys_pressed.get(pygame.K_RSHIFT))
        
        # Normalize diagonal movement
        if move_x != 0 and move_y != 0:
            move_x *= 0.707
            move_y *= 0.707
        
        # Set target velocity
        if move_x != 0 or move_y != 0:
            # Calculate speed based on weight, stamina, and running
            speed_modifier = self._calculate_speed_modifier(is_running)
            target_speed = self.base_speed * speed_modifier
            
            self.target_velocity.x = move_x * target_speed
            self.target_velocity.y = move_y * target_speed
            
            # Update movement state
            if is_running and self.current_stamina > self.exhausted_threshold:
                self.movement_state = MovementState.RUNNING
            elif self.current_weight > self.max_carry_weight * self.overweight_threshold:
                self.movement_state = MovementState.CARRYING
            else:
                self.movement_state = MovementState.WALKING
        else:
            self.target_velocity.x = 0
            self.target_velocity.y = 0
            self.movement_state = MovementState.IDLE
        
        # Smooth velocity interpolation
        self.current_velocity.x += (self.target_velocity.x - self.current_velocity.x) * self.velocity_smoothing
        self.current_velocity.y += (self.target_velocity.y - self.current_velocity.y) * self.velocity_smoothing
        
        # Apply velocity to player
        self.player.rect.x += self.current_velocity.x * dt
        self.player.rect.y += self.current_velocity.y * dt
        
        # Keep player within bounds
        self.player.rect.x = max(0, min(self.player.rect.x, MAP_WIDTH - self.player.rect.width))
        self.player.rect.y = max(0, min(self.player.rect.y, MAP_HEIGHT - self.player.rect.height))
    
    def _calculate_speed_modifier(self, is_running: bool) -> float:
        """Calculate speed modifier based on weight, stamina, and running"""
        modifier = 1.0
        
        # Weight effect
        weight_ratio = self.current_weight / self.max_carry_weight
        if weight_ratio > self.overweight_threshold:
            # Significant slowdown when overweight
            weight_penalty = 0.5 - (weight_ratio - self.overweight_threshold) * 0.5
            modifier *= max(0.2, weight_penalty)
        elif weight_ratio > 0.5:
            # Slight slowdown when carrying moderate weight
            modifier *= 1.0 - (weight_ratio - 0.5) * 0.3
        
        # Stamina effect
        if self.current_stamina < self.exhausted_threshold:
            modifier *= 0.4  # Very slow when exhausted
        elif is_running:
            if self.current_stamina > 20:
                modifier *= 2.0  # Double speed when running
            else:
                modifier *= 1.5  # Reduced running speed when low stamina
        
        return modifier
    
    def _update_stamina(self, dt: float):
        """Update stamina based on movement state"""
        if self.movement_state == MovementState.RUNNING:
            # Drain stamina faster if carrying heavy load
            weight_multiplier = 1.0 + (self.current_weight / self.max_carry_weight)
            drain_rate = self.stamina_drain_rate * weight_multiplier
            self.current_stamina -= drain_rate * dt
        else:
            # Regenerate stamina
            regen_rate = self.stamina_regen_rate
            if self.movement_state == MovementState.IDLE:
                regen_rate *= 1.5  # Faster regen when idle
            self.current_stamina += regen_rate * dt
        
        # Clamp stamina
        self.current_stamina = max(0, min(self.max_stamina, self.current_stamina))
        
        # Show stamina indicator if low or actively using
        self.stamina_indicator_visible = (
            self.current_stamina < self.max_stamina * 0.7 or 
            self.movement_state == MovementState.RUNNING
        )
    
    def _apply_movement_effects(self, dt: float):
        """Apply visual and audio effects based on movement"""
        if self.movement_state in [MovementState.WALKING, MovementState.RUNNING, MovementState.CARRYING]:
            # Create movement particles
            if random.random() < 0.3:  # 30% chance per frame
                self._create_movement_particle()
            
            # Screen shake for running
            if self.movement_state == MovementState.RUNNING:
                if hasattr(self.player, 'camera_shake_intensity'):
                    self.player.camera_shake_intensity = 1.0
                    self.player.camera_shake_duration = 0.1
    
    def _create_movement_particle(self):
        """Create a movement particle effect"""
        particle = {
            'x': self.player.rect.centerx + random.randint(-10, 10),
            'y': self.player.rect.bottom + random.randint(-5, 5),
            'vx': random.uniform(-20, 20),
            'vy': random.uniform(-30, -10),
            'life': 0.5,
            'max_life': 0.5,
            'color': (139, 119, 101) if self.movement_state != MovementState.RUNNING else (160, 140, 120)
        }
        self.movement_particles.append(particle)
        
        # Limit particle count
        if len(self.movement_particles) > 20:
            self.movement_particles.pop(0)
    
    def _update_nearby_objects(self):
        """Update lists of nearby interactable objects"""
        player_center = (self.player.rect.centerx, self.player.rect.centery)
        
        # Find nearby resources
        self.nearby_resources = []
        for node in self.resources.resource_nodes:
            if node.current_yield > 0:
                distance = math.sqrt(
                    (node.x - player_center[0]) ** 2 + 
                    (node.y - player_center[1]) ** 2
                )
                if distance <= self.interaction_range:
                    self.nearby_resources.append((node, distance))
        
        # Sort by distance
        self.nearby_resources.sort(key=lambda x: x[1])
    
    def _update_visual_effects(self, dt: float):
        """Update visual effect particles"""
        # Update movement particles
        for particle in self.movement_particles[:]:
            particle['life'] -= dt
            particle['x'] += particle['vx'] * dt
            particle['y'] += particle['vy'] * dt
            particle['vy'] += 50 * dt  # Gravity
            
            if particle['life'] <= 0:
                self.movement_particles.remove(particle)
        
        # Update interaction hints
        self.interaction_hints = []
        if self.nearby_resources:
            closest_resource, distance = self.nearby_resources[0]
            if distance <= self.interaction_range:
                self.interaction_hints.append({
                    'type': 'resource',
                    'text': f"Press SPACE to gather {closest_resource.resource_type.replace('_', ' ')}",
                    'position': (closest_resource.x, closest_resource.y - 40),
                    'color': (100, 255, 100)
                })
    
    def _handle_auto_pickup(self):
        """Handle automatic pickup of nearby items"""
        # This would be implemented when dropped items system is added
        pass
    
    def _apply_resource_magnetism(self, dt: float):
        """Apply subtle magnetism effect when near resources"""
        if not self.nearby_resources:
            return
        
        closest_resource, distance = self.nearby_resources[0]
        if distance <= self.resource_magnetism_range:
            # Calculate magnetism force
            force_strength = (1.0 - distance / self.resource_magnetism_range) * self.magnetism_strength
            
            # Apply subtle pull toward resource
            dx = closest_resource.x - self.player.rect.centerx
            dy = closest_resource.y - self.player.rect.centery
            
            if distance > 0:
                pull_x = (dx / distance) * force_strength * 20 * dt
                pull_y = (dy / distance) * force_strength * 20 * dt
                
                self.player.rect.x += pull_x
                self.player.rect.y += pull_y
    
    def auto_move_to_position(self, target_x: int, target_y: int):
        """Start auto-movement to a specific position"""
        self.auto_move_target = (target_x, target_y)
    
    def auto_move_to_resource(self, resource_node):
        """Start auto-movement to a resource"""
        self.auto_move_to_position(resource_node.x, resource_node.y)
    
    def stop_auto_move(self):
        """Stop auto-movement"""
        self.auto_move_target = None
    
    def get_movement_info(self) -> Dict:
        """Get current movement information for UI display"""
        return {
            'state': self.movement_state.value,
            'speed': self.current_speed,
            'stamina': self.current_stamina,
            'max_stamina': self.max_stamina,
            'weight': self.current_weight,
            'max_weight': self.max_carry_weight,
            'weight_ratio': self.current_weight / self.max_carry_weight,
            'is_overweight': self.current_weight > self.max_carry_weight * self.overweight_threshold,
            'nearby_resources': len(self.nearby_resources)
        }
    
    def draw_effects(self, screen: pygame.Surface, camera):
        """Draw movement effects and indicators"""
        # Draw movement particles
        for particle in self.movement_particles:
            alpha = int(255 * (particle['life'] / particle['max_life']))
            color = (*particle['color'], alpha)
            
            screen_pos = camera.apply_rect(pygame.Rect(
                particle['x'] - 2, particle['y'] - 2, 4, 4
            ))
            pygame.draw.circle(screen, particle['color'], screen_pos.center, 2)
        
        # Draw interaction hints
        for hint in self.interaction_hints:
            font = pygame.font.Font(None, 20)
            text_surface = font.render(hint['text'], True, hint['color'])
            
            screen_pos = camera.apply_rect(pygame.Rect(
                hint['position'][0] - text_surface.get_width() // 2,
                hint['position'][1],
                text_surface.get_width(),
                text_surface.get_height()
            ))
            
            # Draw background
            bg_rect = screen_pos.inflate(10, 6)
            pygame.draw.rect(screen, (0, 0, 0, 180), bg_rect, border_radius=5)
            
            screen.blit(text_surface, screen_pos)
        
        # Draw resource magnetism effect
        if self.nearby_resources:
            closest_resource, distance = self.nearby_resources[0]
            if distance <= self.resource_magnetism_range:
                # Draw subtle connection line
                start_pos = camera.apply_rect(self.player.rect).center
                end_pos = camera.apply_rect(pygame.Rect(
                    closest_resource.x - 16, closest_resource.y - 16, 32, 32
                )).center
                
                alpha = int(100 * (1.0 - distance / self.resource_magnetism_range))
                color = (100, 255, 100, alpha)
                
                # Draw pulsing line
                import time
                pulse = int(abs(math.sin(time.time() * 3)) * 50 + 50)
                line_color = (100, 255, 100, pulse)
                
                pygame.draw.line(screen, (100, 255, 100), start_pos, end_pos, 2)
    
    def draw_ui_indicators(self, screen: pygame.Surface):
        """Draw UI indicators for weight and stamina"""
        if self.weight_indicator_visible:
            self._draw_weight_indicator(screen)
        
        if self.stamina_indicator_visible:
            self._draw_stamina_indicator(screen)
    
    def _draw_weight_indicator(self, screen: pygame.Surface):
        """Draw weight carrying indicator"""
        x = 20
        y = SCREEN_HEIGHT - 100
        width = 200
        height = 20
        
        # Background
        bg_rect = pygame.Rect(x, y, width, height)
        pygame.draw.rect(screen, (40, 40, 40), bg_rect, border_radius=10)
        pygame.draw.rect(screen, (100, 100, 100), bg_rect, 2, border_radius=10)
        
        # Fill
        fill_ratio = min(1.0, self.current_weight / self.max_carry_weight)
        fill_width = int(width * fill_ratio)
        
        if fill_ratio > self.overweight_threshold:
            fill_color = (255, 100, 100)  # Red when overweight
        elif fill_ratio > 0.6:
            fill_color = (255, 200, 100)  # Yellow when heavy
        else:
            fill_color = (100, 255, 100)  # Green when light
        
        if fill_width > 0:
            fill_rect = pygame.Rect(x, y, fill_width, height)
            pygame.draw.rect(screen, fill_color, fill_rect, border_radius=10)
        
        # Text
        font = pygame.font.Font(None, 16)
        text = f"Weight: {self.current_weight:.1f}/{self.max_carry_weight:.1f}"
        text_surface = font.render(text, True, (255, 255, 255))
        screen.blit(text_surface, (x, y - 18))
    
    def _draw_stamina_indicator(self, screen: pygame.Surface):
        """Draw stamina indicator"""
        x = 20
        y = SCREEN_HEIGHT - 130
        width = 200
        height = 15
        
        # Background
        bg_rect = pygame.Rect(x, y, width, height)
        pygame.draw.rect(screen, (40, 40, 40), bg_rect, border_radius=8)
        pygame.draw.rect(screen, (100, 100, 100), bg_rect, 2, border_radius=8)
        
        # Fill
        fill_ratio = self.current_stamina / self.max_stamina
        fill_width = int(width * fill_ratio)
        
        if fill_ratio < 0.2:
            fill_color = (255, 100, 100)  # Red when exhausted
        elif fill_ratio < 0.5:
            fill_color = (255, 200, 100)  # Yellow when low
        else:
            fill_color = (100, 150, 255)  # Blue when good
        
        if fill_width > 0:
            fill_rect = pygame.Rect(x, y, fill_width, height)
            pygame.draw.rect(screen, fill_color, fill_rect, border_radius=8)
        
        # Text
        font = pygame.font.Font(None, 16)
        text = f"Stamina: {self.current_stamina:.0f}/{self.max_stamina:.0f}"
        text_surface = font.render(text, True, (255, 255, 255))
        screen.blit(text_surface, (x, y - 18))