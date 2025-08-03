import pygame
import json
import os
from typing import Dict, List, Tuple, Optional, Any
from src.core.constants import *

class DraggableComponent:
    """Base class for draggable HUD components"""
    
    def __init__(self, name: str, x: int, y: int, width: int, height: int, ui_component=None):
        self.name = name
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.ui_component = ui_component
        
        # Dragging state
        self.dragging = False
        self.drag_offset_x = 0
        self.drag_offset_y = 0
        
        # Visual state
        self.hovered = False
        self.locked = False
        self.visible = True
        self.alpha = 255
        
        # Snap grid
        self.snap_to_grid = True
        self.grid_size = 10
        
        # Boundaries
        self.min_x = 0
        self.min_y = 0
        self.max_x = SCREEN_WIDTH
        self.max_y = SCREEN_HEIGHT
    
    def get_rect(self) -> pygame.Rect:
        """Get the component's rectangle"""
        return pygame.Rect(self.x, self.y, self.width, self.height)
    
    def contains_point(self, point: Tuple[int, int]) -> bool:
        """Check if point is within component bounds"""
        return self.get_rect().collidepoint(point)
    
    def start_drag(self, mouse_pos: Tuple[int, int]):
        """Start dragging the component"""
        if self.locked:
            return False
        
        self.dragging = True
        self.drag_offset_x = mouse_pos[0] - self.x
        self.drag_offset_y = mouse_pos[1] - self.y
        return True
    
    def update_drag(self, mouse_pos: Tuple[int, int]):
        """Update component position during drag"""
        if not self.dragging:
            return
        
        old_x, old_y = self.x, self.y
        
        new_x = mouse_pos[0] - self.drag_offset_x
        new_y = mouse_pos[1] - self.drag_offset_y
        
        # Apply boundaries
        new_x = max(self.min_x, min(new_x, self.max_x - self.width))
        new_y = max(self.min_y, min(new_y, self.max_y - self.height))
        
        # Snap to grid
        if self.snap_to_grid:
            new_x = round(new_x / self.grid_size) * self.grid_size
            new_y = round(new_y / self.grid_size) * self.grid_size
        
        # Only update if position actually changed
        if old_x != new_x or old_y != new_y:
            self.x = new_x
            self.y = new_y
            return True  # Position changed
        return False  # No change
    
    def end_drag(self):
        """End dragging"""
        self.dragging = False
    
    def draw_drag_outline(self, surface: pygame.Surface):
        """Draw outline when component is being dragged or hovered"""
        if not (self.dragging or self.hovered):
            return
        
        rect = self.get_rect()
        
        # Draw different colors for different states
        if self.dragging:
            color = (255, 215, 0, 200)  # Gold when dragging
        elif self.locked:
            color = (255, 100, 100, 150)  # Red when locked
        else:
            color = (100, 200, 255, 150)  # Blue when hovered
        
        # Create transparent surface for outline
        outline_surface = pygame.Surface((rect.width + 4, rect.height + 4), pygame.SRCALPHA)
        pygame.draw.rect(outline_surface, color, (0, 0, rect.width + 4, rect.height + 4), 2, border_radius=5)
        
        # Draw corner handles for resizing
        if self.hovered or self.dragging:
            handle_size = 8
            corners = [
                (rect.width - handle_size, rect.height - handle_size),  # Bottom-right
                (0, rect.height - handle_size),  # Bottom-left
                (rect.width - handle_size, 0),  # Top-right
                (0, 0)  # Top-left
            ]
            
            for corner_x, corner_y in corners:
                pygame.draw.rect(outline_surface, (255, 255, 255, 200), 
                               (corner_x, corner_y, handle_size, handle_size), border_radius=2)
        
        surface.blit(outline_surface, (rect.x - 2, rect.y - 2))
    
    def to_dict(self) -> Dict:
        """Serialize component to dictionary"""
        return {
            'name': self.name,
            'x': self.x,
            'y': self.y,
            'width': self.width,
            'height': self.height,
            'locked': self.locked,
            'visible': self.visible,
            'alpha': self.alpha
        }
    
    def from_dict(self, data: Dict):
        """Load component from dictionary"""
        self.x = data.get('x', self.x)
        self.y = data.get('y', self.y)
        self.width = data.get('width', self.width)
        self.height = data.get('height', self.height)
        self.locked = data.get('locked', self.locked)
        self.visible = data.get('visible', self.visible)
        self.alpha = data.get('alpha', self.alpha)

class DraggableHUDManager:
    """Manager for all draggable HUD components"""
    
    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.components: Dict[str, DraggableComponent] = {}
        
        # Edit mode state
        self.edit_mode = False
        self.selected_component: Optional[DraggableComponent] = None
        
        # Performance optimization
        self.positions_dirty = False
        
        # Visual settings
        self.grid_visible = False
        self.grid_size = 10
        self.grid_color = (100, 100, 100, 100)
        
        # Save/load settings
        self.save_file = "hud_layout.json"
        
        # Font for labels
        self.font = pygame.font.Font(None, 16)
        
        # Control panel
        self.control_panel_visible = False
        self.control_panel_rect = pygame.Rect(SCREEN_WIDTH - 250, 50, 240, 400)
        
        # Default positions for components
        self.default_positions = {
            'player_panel': (12, SCREEN_HEIGHT - 120 - 12, 180, 120),
            'npc_panel': (SCREEN_WIDTH - 220 - 15, 15, 220, 300),
            'events_panel': ((SCREEN_WIDTH - 300) // 2, 15, 300, 80),
            'shortcut_keys': ((SCREEN_WIDTH - 600) // 2, SCREEN_HEIGHT - 50 - 10, 600, 50),
            'ai_response_box': (20, 100, 400, 150),
            'cost_monitor': (SCREEN_WIDTH - 200, SCREEN_HEIGHT - 100, 180, 80),
            'speed_controller': (20, 20, 200, 60),
            'data_analysis_panel': (SCREEN_WIDTH - 300, 100, 280, 200),
            'interaction_menu': ((SCREEN_WIDTH - 300) // 2, (SCREEN_HEIGHT - 400) // 2, 300, 400),
            'game_clock': ((SCREEN_WIDTH - 280) // 2, 10, 280, 80),
            'help_system': (50, 50, 300, 200),
            'notification_system': (SCREEN_WIDTH - 350, 100, 330, 100),
            'skills_inventory': (20, 200, 250, 300),
            'quest_ui': (SCREEN_WIDTH - 280, 350, 260, 200),
            'xp_display': (20, SCREEN_HEIGHT - 200, 200, 80),
        }
    
    def enter_edit_mode(self):
        """Enter HUD edit mode"""
        self.edit_mode = True
        self.grid_visible = True
        self.control_panel_visible = True
        print("🎨 Entered HUD edit mode. Press F1 to exit.")
    
    def exit_edit_mode(self):
        """Exit HUD edit mode"""
        self.edit_mode = False
        self.grid_visible = False
        self.control_panel_visible = False
        self.selected_component = None
        
        # End all dragging
        for component in self.components.values():
            component.end_drag()
        
        print("🎨 Exited edit mode. Press S to save layout.")
    
    def toggle_edit_mode(self):
        """Toggle HUD edit mode"""
        if self.edit_mode:
            self.exit_edit_mode()
        else:
            self.enter_edit_mode()
    
    def register_component(self, name: str, ui_component, x: int = None, y: int = None, 
                          width: int = None, height: int = None):
        """Register a UI component as draggable"""
        # Use default position if not specified
        if name in self.default_positions:
            default_x, default_y, default_w, default_h = self.default_positions[name]
            x = x or default_x
            y = y or default_y
            width = width or default_w
            height = height or default_h
        else:
            x = x or 100
            y = y or 100
            width = width or 200
            height = height or 100
        
        component = DraggableComponent(name, x, y, width, height, ui_component)
        self.components[name] = component
        
        # Try to load saved position
        self._load_component_position(component)
        
        print(f"📍 Registered draggable component: {name}")
        return component
    
    def _load_component_position(self, component: DraggableComponent):
        """Load saved position for a component"""
        if os.path.exists(self.save_file):
            try:
                with open(self.save_file, 'r') as f:
                    data = json.load(f)
                
                if component.name in data:
                    component.from_dict(data[component.name])
            except Exception as e:
                print(f"Error loading position for {component.name}: {e}")
    
    def update_component_position(self, name: str, ui_component):
        """Update the actual UI component position based on draggable component"""
        if name not in self.components:
            return
        
        component = self.components[name]
        
        # Update UI component position if it has position attributes
        if hasattr(ui_component, 'x'):
            ui_component.x = component.x
        if hasattr(ui_component, 'y'):
            ui_component.y = component.y
        if hasattr(ui_component, 'rect'):
            ui_component.rect.x = component.x
            ui_component.rect.y = component.y
        if hasattr(ui_component, 'panel_x'):
            ui_component.panel_x = component.x
        if hasattr(ui_component, 'panel_y'):
            ui_component.panel_y = component.y
        if hasattr(ui_component, 'position'):
            ui_component.position = (component.x, component.y)
    
    def handle_event(self, event) -> bool:
        """Handle input events for draggable HUD system"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_F1:
                self.toggle_edit_mode()
                return True
            elif self.edit_mode:
                if event.key == pygame.K_g:
                    self.grid_visible = not self.grid_visible
                    return True
                elif event.key == pygame.K_l and self.selected_component:
                    self.selected_component.locked = not self.selected_component.locked
                    return True
                elif event.key == pygame.K_r:
                    self.reset_layout()
                    return True
                elif event.key == pygame.K_s:
                    self.save_layout()
                    return True
        
        if not self.edit_mode:
            return False
        
        mouse_pos = pygame.mouse.get_pos()
        
        # Handle control panel interactions
        if self.control_panel_visible and self.control_panel_rect.collidepoint(mouse_pos):
            return self._handle_control_panel_event(event)
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                # Find component under mouse
                clicked_component = None
                for component in reversed(list(self.components.values())):
                    if component.visible and component.contains_point(mouse_pos):
                        clicked_component = component
                        break
                
                if clicked_component:
                    self.selected_component = clicked_component
                    clicked_component.start_drag(mouse_pos)
                    return True
                else:
                    self.selected_component = None
        
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:  # Left click release
                for component in self.components.values():
                    component.end_drag()
                return True
        
        elif event.type == pygame.MOUSEMOTION:
            # Update hover states
            for component in self.components.values():
                component.hovered = component.visible and component.contains_point(mouse_pos)
                
                # Update drag
                if component.dragging:
                    if component.update_drag(mouse_pos):
                        self.positions_dirty = True
            return True
        
        return False
    
    def _handle_control_panel_event(self, event) -> bool:
        """Handle control panel interactions"""
        # Implement control panel button logic here
        return True
    
    def draw_grid(self):
        """Draw snap grid"""
        if not self.grid_visible:
            return
        
        grid_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        
        # Vertical lines
        for x in range(0, SCREEN_WIDTH, self.grid_size):
            pygame.draw.line(grid_surface, self.grid_color, (x, 0), (x, SCREEN_HEIGHT))
        
        # Horizontal lines
        for y in range(0, SCREEN_HEIGHT, self.grid_size):
            pygame.draw.line(grid_surface, self.grid_color, (0, y), (SCREEN_WIDTH, y))
        
        self.screen.blit(grid_surface, (0, 0))
    
    def draw_control_panel(self):
        """Draw the HUD editing control panel"""
        if not self.control_panel_visible:
            return
        
        # Panel background
        panel_surface = pygame.Surface((self.control_panel_rect.width, self.control_panel_rect.height), pygame.SRCALPHA)
        pygame.draw.rect(panel_surface, (30, 30, 30, 240), (0, 0, self.control_panel_rect.width, self.control_panel_rect.height), border_radius=10)
        pygame.draw.rect(panel_surface, (100, 100, 100), (0, 0, self.control_panel_rect.width, self.control_panel_rect.height), 2, border_radius=10)
        
        # Title
        title_text = self.font.render("HUD Editor", True, (255, 255, 255))
        panel_surface.blit(title_text, (10, 10))
        
        # Instructions
        instructions = [
            "F1 - Exit edit mode",
            "G - Toggle grid",
            "L - Lock/unlock selected",
            "R - Reset layout",
            "S - Save layout",
            "",
            "Drag components to move",
            "Click to select",
        ]
        
        y_offset = 40
        for instruction in instructions:
            if instruction:
                text = self.font.render(instruction, True, (200, 200, 200))
                panel_surface.blit(text, (10, y_offset))
            y_offset += 20
        
        # Component list
        y_offset += 10
        list_title = self.font.render("Components:", True, (255, 255, 255))
        panel_surface.blit(list_title, (10, y_offset))
        y_offset += 25
        
        for name, component in self.components.items():
            # Component name with status indicators
            color = (100, 255, 100) if component.visible else (100, 100, 100)
            if component.locked:
                color = (255, 100, 100)
            elif component == self.selected_component:
                color = (255, 215, 0)
            
            display_name = name.replace('_', ' ').title()
            if component.locked:
                display_name += " 🔒"
            if not component.visible:
                display_name += " ✕"
            
            text = self.font.render(display_name, True, color)
            panel_surface.blit(text, (15, y_offset))
            y_offset += 18
            
            if y_offset > self.control_panel_rect.height - 30:
                break
        
        self.screen.blit(panel_surface, self.control_panel_rect)
    
    def draw_component_outlines(self):
        """Draw outlines for all components in edit mode"""
        if not self.edit_mode:
            return
        
        for component in self.components.values():
            if component.visible:
                component.draw_drag_outline(self.screen)
        
        # Draw selection highlight for selected component
        if self.selected_component and self.selected_component.visible:
            rect = self.selected_component.get_rect()
            # Additional highlight for selected component
            highlight_surface = pygame.Surface((rect.width + 8, rect.height + 8), pygame.SRCALPHA)
            pygame.draw.rect(highlight_surface, (255, 215, 0, 100), (0, 0, rect.width + 8, rect.height + 8), 4, border_radius=8)
            self.screen.blit(highlight_surface, (rect.x - 4, rect.y - 4))
    
    def draw_edit_mode_hud(self):
        """Draw edit mode specific elements"""
        if not self.edit_mode:
            return
        
        # Draw grid first (behind everything)
        if self.grid_visible:
            self.draw_grid()
        
        # Draw component outlines
        self.draw_component_outlines()
        
        # Draw control panel last (on top)
        if self.control_panel_visible:
            self.draw_control_panel()
        
        # Draw edit mode indicator
        edit_text = self.font.render("HUD EDIT MODE - Press F1 to exit", True, (255, 215, 0))
        edit_rect = edit_text.get_rect()
        edit_rect.centerx = SCREEN_WIDTH // 2
        edit_rect.y = 10
        
        # Background for text
        bg_rect = edit_rect.inflate(20, 10)
        pygame.draw.rect(self.screen, (0, 0, 0, 180), bg_rect, border_radius=5)
        pygame.draw.rect(self.screen, (255, 215, 0), bg_rect, 2, border_radius=5)
        
        self.screen.blit(edit_text, edit_rect)
    
    def save_layout(self):
        """Save current HUD layout to file"""
        try:
            data = {}
            for name, component in self.components.items():
                data[name] = component.to_dict()
            
            with open(self.save_file, 'w') as f:
                json.dump(data, f, indent=2)
            
            print(f"💾 HUD layout saved to {self.save_file}")
        except Exception as e:
            print(f"Error saving HUD layout: {e}")
    
    def load_layout(self):
        """Load HUD layout from file"""
        if not os.path.exists(self.save_file):
            return
        
        try:
            with open(self.save_file, 'r') as f:
                data = json.load(f)
            
            for name, component_data in data.items():
                if name in self.components:
                    self.components[name].from_dict(component_data)
            
            print(f"📂 HUD layout loaded from {self.save_file}")
        except Exception as e:
            print(f"Error loading HUD layout: {e}")
    
    def reset_layout(self):
        """Reset all components to default positions"""
        for name, component in self.components.items():
            if name in self.default_positions:
                x, y, w, h = self.default_positions[name]
                component.x = x
                component.y = y
                component.width = w
                component.height = h
                component.locked = False
                component.visible = True
                component.alpha = 255
        
        print("🔄 HUD layout reset to defaults")
    
    def get_component_position(self, name: str) -> Tuple[int, int]:
        """Get current position of a component"""
        if name in self.components:
            component = self.components[name]
            return (component.x, component.y)
        return (0, 0)
    
    def is_edit_mode(self) -> bool:
        """Check if currently in edit mode"""
        return self.edit_mode