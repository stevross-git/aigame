import pygame
from typing import Dict, Optional, List
from src.core.constants import *
from src.systems.inventory_system import InventorySystem, ItemType

class ActionBar:
    """
    Action bar UI component for equipping and using tools/items
    """
    
    def __init__(self, screen, inventory_system: InventorySystem):
        self.screen = screen
        self.inventory = inventory_system
        
        # Fonts
        self.font_normal = pygame.font.Font(None, 20)
        self.font_small = pygame.font.Font(None, 16)
        self.font_tiny = pygame.font.Font(None, 12)
        
        # Colors
        self.bg_color = (30, 35, 45, 200)
        self.slot_color = (50, 55, 65)
        self.slot_hover_color = (70, 80, 100)
        self.slot_selected_color = (100, 150, 200)
        self.slot_border_color = (80, 90, 110)
        
        # Layout
        self.slot_size = 50
        self.slot_spacing = 5
        self.num_slots = 10
        self.bar_width = self.num_slots * (self.slot_size + self.slot_spacing) - self.slot_spacing
        self.bar_height = self.slot_size + 20
        
        # Position at bottom center of screen
        self.x = (SCREEN_WIDTH - self.bar_width) // 2
        self.y = SCREEN_HEIGHT - self.bar_height - 10
        
        # Equipment state
        self.equipped_items: Dict[int, str] = {}  # slot_index -> item_id
        self.selected_slot = 0  # Currently selected slot (0-9)
        self.equipped_tool = None  # Currently equipped tool for use
        
        # UI state
        self.visible = True
        self.hover_slot = None
        
    def handle_event(self, event) -> bool:
        """Handle action bar events"""
        if event.type == pygame.KEYDOWN:
            # Number keys 1-9, 0 for slot selection
            if pygame.K_1 <= event.key <= pygame.K_9:
                slot_index = event.key - pygame.K_1
                self.select_slot(slot_index)
                return True
            elif event.key == pygame.K_0:
                self.select_slot(9)  # Slot 10 (index 9)
                return True
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                mouse_x, mouse_y = event.pos
                clicked_slot = self._get_slot_at_pos(mouse_x, mouse_y)
                if clicked_slot is not None:
                    self.select_slot(clicked_slot)
                    return True
            elif event.button == 3:  # Right click
                mouse_x, mouse_y = event.pos
                clicked_slot = self._get_slot_at_pos(mouse_x, mouse_y)
                if clicked_slot is not None:
                    self.unequip_slot(clicked_slot)
                    return True
        
        elif event.type == pygame.MOUSEMOTION:
            mouse_x, mouse_y = event.pos
            self.hover_slot = self._get_slot_at_pos(mouse_x, mouse_y)
        
        return False
    
    def _get_slot_at_pos(self, mouse_x: int, mouse_y: int) -> Optional[int]:
        """Get action bar slot index at mouse position"""
        if not (self.y <= mouse_y <= self.y + self.bar_height):
            return None
        
        for i in range(self.num_slots):
            slot_x = self.x + i * (self.slot_size + self.slot_spacing)
            if slot_x <= mouse_x <= slot_x + self.slot_size:
                return i
        
        return None
    
    def select_slot(self, slot_index: int):
        """Select an action bar slot"""
        if 0 <= slot_index < self.num_slots:
            self.selected_slot = slot_index
            
            # Update equipped tool
            if slot_index in self.equipped_items:
                item_id = self.equipped_items[slot_index]
                item_data = self.inventory.get_item_data(item_id)
                if item_data and item_data.item_type == ItemType.TOOL:
                    self.equipped_tool = item_id
                else:
                    self.equipped_tool = None
            else:
                self.equipped_tool = None
    
    def equip_item(self, item_id: str, slot_index: Optional[int] = None) -> bool:
        """Equip an item to the action bar"""
        # Check if player has the item
        if not self.inventory.has_item(item_id):
            return False
        
        # If no slot specified, use selected slot
        if slot_index is None:
            slot_index = self.selected_slot
        
        # Validate slot index
        if not (0 <= slot_index < self.num_slots):
            return False
        
        # Unequip existing item in slot if any
        if slot_index in self.equipped_items:
            self.unequip_slot(slot_index)
        
        # Equip new item
        self.equipped_items[slot_index] = item_id
        
        # If this is the selected slot, update equipped tool
        if slot_index == self.selected_slot:
            item_data = self.inventory.get_item_data(item_id)
            if item_data and item_data.item_type == ItemType.TOOL:
                self.equipped_tool = item_id
        
        return True
    
    def unequip_slot(self, slot_index: int) -> bool:
        """Unequip item from a slot"""
        if slot_index in self.equipped_items:
            del self.equipped_items[slot_index]
            
            # If this was the selected slot with equipped tool, clear it
            if slot_index == self.selected_slot:
                self.equipped_tool = None
            
            return True
        return False
    
    def get_equipped_item(self, slot_index: int) -> Optional[str]:
        """Get the item equipped in a specific slot"""
        return self.equipped_items.get(slot_index)
    
    def get_selected_item(self) -> Optional[str]:
        """Get the currently selected item"""
        return self.equipped_items.get(self.selected_slot)
    
    def get_equipped_tool(self) -> Optional[str]:
        """Get the currently equipped tool for use"""
        return self.equipped_tool
    
    def use_selected_item(self) -> bool:
        """Use the currently selected item"""
        selected_item = self.get_selected_item()
        if selected_item:
            item_data = self.inventory.get_item_data(selected_item)
            if item_data:
                if item_data.item_type == ItemType.TOOL:
                    # Tool usage is handled by resource interaction system
                    return True
                elif item_data.item_type == ItemType.FOOD:
                    # Consume food item
                    if self.inventory.remove_item(selected_item, 1):
                        # Remove from action bar if no more left
                        if not self.inventory.has_item(selected_item):
                            self.unequip_slot(self.selected_slot)
                        return True
                # Add more item type usage here
        return False
    
    def update(self, dt: float):
        """Update action bar state"""
        # Clean up equipped items that are no longer in inventory
        slots_to_remove = []
        for slot_index, item_id in self.equipped_items.items():
            if not self.inventory.has_item(item_id):
                slots_to_remove.append(slot_index)
        
        for slot_index in slots_to_remove:
            self.unequip_slot(slot_index)
    
    def draw(self):
        """Draw the action bar"""
        if not self.visible:
            return
        
        # Draw background
        bg_rect = pygame.Rect(self.x - 10, self.y - 10, self.bar_width + 20, self.bar_height)
        pygame.draw.rect(self.screen, self.bg_color, bg_rect, border_radius=8)
        pygame.draw.rect(self.screen, self.slot_border_color, bg_rect, 2, border_radius=8)
        
        # Draw slots
        for i in range(self.num_slots):
            self._draw_slot(i)
        
        # Draw controls hint
        hint_text = "1-9,0: Select Slot | Right Click: Unequip | Left Click: Select"
        hint_surface = self.font_tiny.render(hint_text, True, (180, 180, 180))
        hint_rect = hint_surface.get_rect(center=(SCREEN_WIDTH // 2, self.y - 25))
        self.screen.blit(hint_surface, hint_rect)
    
    def _draw_slot(self, slot_index: int):
        """Draw an individual action bar slot"""
        slot_x = self.x + slot_index * (self.slot_size + self.slot_spacing)
        slot_y = self.y + 10
        slot_rect = pygame.Rect(slot_x, slot_y, self.slot_size, self.slot_size)
        
        # Determine slot color
        if slot_index == self.selected_slot:
            color = self.slot_selected_color
        elif slot_index == self.hover_slot:
            color = self.slot_hover_color
        else:
            color = self.slot_color
        
        # Draw slot background
        pygame.draw.rect(self.screen, color, slot_rect, border_radius=6)
        pygame.draw.rect(self.screen, self.slot_border_color, slot_rect, 2, border_radius=6)
        
        # Draw slot number
        number_text = str((slot_index + 1) % 10)  # 1-9, then 0
        number_surface = self.font_tiny.render(number_text, True, (200, 200, 200))
        self.screen.blit(number_surface, (slot_x + 2, slot_y + 2))
        
        # Draw equipped item
        if slot_index in self.equipped_items:
            item_id = self.equipped_items[slot_index]
            self._draw_item_in_slot(slot_rect, item_id)
    
    def _draw_item_in_slot(self, slot_rect: pygame.Rect, item_id: str):
        """Draw an item in a slot"""
        item_data = self.inventory.get_item_data(item_id)
        if not item_data:
            return
        
        # Draw item icon
        icon_surface = self.font_normal.render(item_data.icon, True, (255, 255, 255))
        icon_rect = icon_surface.get_rect(center=slot_rect.center)
        self.screen.blit(icon_surface, icon_rect)
        
        # Draw quantity if item is consumable and has quantity > 1
        if item_data.item_type in [ItemType.FOOD, ItemType.RESOURCE]:
            quantity = self.inventory.get_item_count(item_id)
            if quantity > 1:
                qty_surface = self.font_tiny.render(str(quantity), True, (255, 255, 255))
                qty_rect = qty_surface.get_rect()
                qty_rect.bottomright = (slot_rect.right - 2, slot_rect.bottom - 2)
                
                # Quantity background
                bg_rect = qty_rect.inflate(2, 1)
                pygame.draw.rect(self.screen, (0, 0, 0, 180), bg_rect, border_radius=2)
                self.screen.blit(qty_surface, qty_rect)
        
        # Draw durability bar for tools (placeholder - could be extended)
        if item_data.item_type == ItemType.TOOL:
            # Draw a small green bar to indicate tool is functional
            bar_width = slot_rect.width - 6
            bar_height = 3
            bar_x = slot_rect.x + 3
            bar_y = slot_rect.bottom - bar_height - 3
            
            bar_rect = pygame.Rect(bar_x, bar_y, bar_width, bar_height)
            pygame.draw.rect(self.screen, (100, 255, 100), bar_rect)
    
    def show(self):
        """Show the action bar"""
        self.visible = True
    
    def hide(self):
        """Hide the action bar"""
        self.visible = False
    
    def toggle_visibility(self):
        """Toggle action bar visibility"""
        self.visible = not self.visible