import pygame
import math
import random
from typing import Dict, List, Optional, Tuple, Any
from src.core.constants import *
from src.systems.inventory_system import InventorySystem, ItemType, ItemRarity, ItemData, InventoryItem

class DragDropSlot:
    """Represents a single inventory slot that can hold items"""
    
    def __init__(self, x: int, y: int, size: int, slot_type: str = "inventory"):
        self.x = x
        self.y = y
        self.size = size
        self.slot_type = slot_type  # "inventory", "hotbar", "equipment", "trash"
        self.rect = pygame.Rect(x, y, size, size)
        self.item_id = None
        self.item_quantity = 0
        self.item_quality = 1
        self.is_hovered = False
        self.is_highlighted = False
        self.can_accept_item = True
        
        # Visual effects
        self.hover_animation = 0.0
        self.glow_animation = 0.0

class DragDropInventory:
    """
    Advanced drag-and-drop inventory system with hotbar, equipment, and visual effects
    """
    
    def __init__(self, screen, inventory_system: InventorySystem, action_bar=None):
        self.screen = screen
        self.inventory = inventory_system
        self.action_bar = action_bar
        self.visible = False
        
        # Fonts
        self.font_normal = pygame.font.Font(None, 20)
        self.font_small = pygame.font.Font(None, 16)
        self.font_tiny = pygame.font.Font(None, 12)
        
        # Colors
        self.bg_color = (30, 35, 45, 240)
        self.slot_color = (50, 55, 65)
        self.slot_hover_color = (70, 80, 100)
        self.slot_border_color = (80, 90, 110)
        self.drag_color = (100, 150, 200, 180)
        self.trash_color = (200, 100, 100)
        
        # Rarity colors
        self.rarity_colors = {
            ItemRarity.COMMON: (150, 150, 150),
            ItemRarity.UNCOMMON: (100, 255, 100),
            ItemRarity.RARE: (100, 100, 255),
            ItemRarity.EPIC: (200, 100, 255),
            ItemRarity.LEGENDARY: (255, 200, 50)
        }
        
        # Layout
        self.panel_width = 480
        self.panel_height = 400
        self.panel_x = (SCREEN_WIDTH - self.panel_width) // 2
        self.panel_y = (SCREEN_HEIGHT - self.panel_height) // 2
        
        # Slots
        self.slot_size = 45
        self.slot_spacing = 5
        self.inventory_slots: List[DragDropSlot] = []
        self.hotbar_slots: List[DragDropSlot] = []
        self.equipment_slots: List[DragDropSlot] = []
        self.trash_slot: Optional[DragDropSlot] = None
        
        # Drag and drop state
        self.dragging_item = None
        self.drag_source_slot = None
        self.drag_offset = (0, 0)
        self.drag_start_pos = (0, 0)
        self.is_dragging = False
        
        # Quick actions
        self.quick_stack_enabled = True
        self.auto_sort_enabled = True
        self.shift_click_enabled = True
        
        # Visual effects
        self.particles = []
        self.slot_animations = {}
        
        self._initialize_slots()
    
    def _initialize_slots(self):
        """Initialize all inventory slots"""
        # Main inventory grid (6x6 = 36 slots)
        grid_start_x = self.panel_x + 20
        grid_start_y = self.panel_y + 80
        rows = 6
        cols = 6
        
        for row in range(rows):
            for col in range(cols):
                x = grid_start_x + col * (self.slot_size + self.slot_spacing)
                y = grid_start_y + row * (self.slot_size + self.slot_spacing)
                slot = DragDropSlot(x, y, self.slot_size, "inventory")
                self.inventory_slots.append(slot)
        
        # Hotbar (bottom of screen, 10 slots)
        hotbar_start_x = (SCREEN_WIDTH - (10 * (self.slot_size + self.slot_spacing))) // 2
        hotbar_y = SCREEN_HEIGHT - self.slot_size - 20
        
        for i in range(10):
            x = hotbar_start_x + i * (self.slot_size + self.slot_spacing)
            slot = DragDropSlot(x, hotbar_y, self.slot_size, "hotbar")
            self.hotbar_slots.append(slot)
        
        # Equipment slots (right side of inventory)
        equipment_x = self.panel_x + self.panel_width - 80
        equipment_slots_data = [
            ("helmet", equipment_x, self.panel_y + 60),
            ("armor", equipment_x, self.panel_y + 110),
            ("boots", equipment_x, self.panel_y + 160),
            ("weapon", equipment_x, self.panel_y + 210),
            ("tool", equipment_x, self.panel_y + 260),
        ]
        
        for slot_type, x, y in equipment_slots_data:
            slot = DragDropSlot(x, y, self.slot_size, f"equipment_{slot_type}")
            slot.can_accept_item = True  # Custom validation will be added
            self.equipment_slots.append(slot)
        
        # Trash slot
        trash_x = self.panel_x + self.panel_width - 80
        trash_y = self.panel_y + self.panel_height - 60
        self.trash_slot = DragDropSlot(trash_x, trash_y, self.slot_size, "trash")
    
    def show(self):
        """Show the drag-drop inventory"""
        self.visible = True
        self._sync_slots_with_inventory()
    
    def hide(self):
        """Hide the drag-drop inventory"""
        self.visible = False
        if self.is_dragging:
            self._cancel_drag()
    
    def toggle(self):
        """Toggle inventory visibility"""
        if self.visible:
            self.hide()
        else:
            self.show()
    
    def _sync_slots_with_inventory(self):
        """Sync slot contents with inventory system"""
        # Clear all slots
        for slot in self.inventory_slots + self.hotbar_slots + self.equipment_slots:
            slot.item_id = None
            slot.item_quantity = 0
            slot.item_quality = 1
        
        # Fill slots with inventory items
        all_items = list(self.inventory.get_all_items().items())
        
        for i, (item_id, inv_item) in enumerate(all_items):
            if i < len(self.inventory_slots):
                slot = self.inventory_slots[i]
                slot.item_id = item_id
                slot.item_quantity = inv_item.quantity
                slot.item_quality = inv_item.quality
    
    def _get_slot_at_pos(self, x: int, y: int) -> Optional[DragDropSlot]:
        """Get slot at mouse position"""
        all_slots = self.inventory_slots + self.hotbar_slots + self.equipment_slots
        if self.trash_slot:
            all_slots.append(self.trash_slot)
        
        for slot in all_slots:
            if slot.rect.collidepoint(x, y):
                return slot
        return None
    
    def _can_slot_accept_item(self, slot: DragDropSlot, item_id: str) -> bool:
        """Check if a slot can accept a specific item"""
        if not slot.can_accept_item:
            return False
        
        item_data = self.inventory.get_item_data(item_id)
        if not item_data:
            return False
        
        # Equipment slot validation
        if slot.slot_type.startswith("equipment_"):
            equipment_type = slot.slot_type.split("_")[1]
            return self._is_item_equipment_type(item_data, equipment_type)
        
        # Trash slot accepts everything
        if slot.slot_type == "trash":
            return True
        
        # Regular slots accept most items
        return True
    
    def _is_item_equipment_type(self, item_data: ItemData, equipment_type: str) -> bool:
        """Check if item can be equipped in specific equipment slot"""
        item_name_lower = item_data.name.lower()
        
        if equipment_type == "helmet":
            return "helmet" in item_name_lower or "hat" in item_name_lower
        elif equipment_type == "armor":
            return "armor" in item_name_lower or "shirt" in item_name_lower
        elif equipment_type == "boots":
            return "boots" in item_name_lower or "shoes" in item_name_lower
        elif equipment_type == "weapon":
            return "sword" in item_name_lower or "bow" in item_name_lower
        elif equipment_type == "tool":
            return item_data.item_type == ItemType.TOOL
        
        return False
    
    def handle_event(self, event) -> bool:
        """Handle drag and drop events"""
        if not self.visible and event.type not in [pygame.KEYDOWN]:
            return False
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_TAB:
                self.toggle()
                return True
            elif event.key == pygame.K_ESCAPE and self.visible:
                self.hide()
                return True
            elif event.key == pygame.K_s and self.visible and self.auto_sort_enabled:
                keys = pygame.key.get_pressed()
                if keys[pygame.K_LCTRL] or keys[pygame.K_RCTRL]:
                    self._auto_sort_inventory()
                    return True
        
        if not self.visible:
            return False
        
        mouse_x, mouse_y = pygame.mouse.get_pos()
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                keys = pygame.key.get_pressed()
                if keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]:
                    return self._handle_shift_click(mouse_x, mouse_y)
                else:
                    return self._handle_left_click(mouse_x, mouse_y)
            elif event.button == 3:  # Right click
                return self._handle_right_click(mouse_x, mouse_y)
        
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1 and self.is_dragging:
                return self._handle_drop(mouse_x, mouse_y)
        
        elif event.type == pygame.MOUSEMOTION:
            self._handle_mouse_motion(mouse_x, mouse_y)
        
        return True
    
    def _handle_left_click(self, mouse_x: int, mouse_y: int) -> bool:
        """Handle left mouse click"""
        slot = self._get_slot_at_pos(mouse_x, mouse_y)
        
        if slot and slot.item_id:
            # Start dragging
            self.is_dragging = True
            self.dragging_item = {
                'item_id': slot.item_id,
                'quantity': slot.item_quantity,
                'quality': slot.item_quality
            }
            self.drag_source_slot = slot
            self.drag_start_pos = (mouse_x, mouse_y)
            self.drag_offset = (mouse_x - slot.x - slot.size // 2, mouse_y - slot.y - slot.size // 2)
            
            # Clear source slot temporarily
            slot.item_id = None
            slot.item_quantity = 0
            slot.item_quality = 1
            
            return True
        
        # Click outside inventory to close
        inventory_rect = pygame.Rect(self.panel_x, self.panel_y, self.panel_width, self.panel_height)
        if not inventory_rect.collidepoint(mouse_x, mouse_y):
            self.hide()
            return True
        
        return False
    
    def _handle_shift_click(self, mouse_x: int, mouse_y: int) -> bool:
        """Handle shift+click to equip items to action bar"""
        slot = self._get_slot_at_pos(mouse_x, mouse_y)
        
        if slot and slot.item_id and self.action_bar:
            # Try to equip item to action bar
            item_data = self.inventory.get_item_data(slot.item_id)
            if item_data and item_data.item_type == ItemType.TOOL:
                # Find an empty slot in action bar or use selected slot
                if self.action_bar.equip_item(slot.item_id):
                    self._create_success_particle(slot.x + slot.size // 2, slot.y + slot.size // 2)
                    return True
                else:
                    self._create_error_particle(slot.x + slot.size // 2, slot.y + slot.size // 2)
        
        return False
    
    def _handle_right_click(self, mouse_x: int, mouse_y: int) -> bool:
        """Handle right mouse click (quick actions)"""
        slot = self._get_slot_at_pos(mouse_x, mouse_y)
        
        if slot and slot.item_id:
            # Quick use/consume item
            self._quick_use_item(slot.item_id)
            return True
        
        return False
    
    def _handle_drop(self, mouse_x: int, mouse_y: int) -> bool:
        """Handle dropping an item"""
        if not self.is_dragging or not self.dragging_item:
            return False
        
        target_slot = self._get_slot_at_pos(mouse_x, mouse_y)
        success = False
        
        if target_slot:
            if target_slot.slot_type == "trash":
                # Dropping in trash
                self._trash_item(self.dragging_item['item_id'], self.dragging_item['quantity'])
                success = True
            elif self._can_slot_accept_item(target_slot, self.dragging_item['item_id']):
                # Valid drop location
                success = self._move_item_to_slot(target_slot)
            else:
                # Invalid drop location
                self._create_error_particle(mouse_x, mouse_y)
        
        if not success:
            # Return item to source slot
            self._return_item_to_source()
        
        self._end_drag()
        return True
    
    def _move_item_to_slot(self, target_slot: DragDropSlot) -> bool:
        """Move dragged item to target slot"""
        if target_slot.item_id:
            # Slot occupied, try to swap or stack
            if target_slot.item_id == self.dragging_item['item_id']:
                # Same item, try to stack
                item_data = self.inventory.get_item_data(self.dragging_item['item_id'])
                if item_data and target_slot.item_quantity < item_data.max_stack:
                    # Can stack
                    stack_amount = min(
                        self.dragging_item['quantity'],
                        item_data.max_stack - target_slot.item_quantity
                    )
                    target_slot.item_quantity += stack_amount
                    self.dragging_item['quantity'] -= stack_amount
                    
                    if self.dragging_item['quantity'] <= 0:
                        # All items stacked
                        self._create_success_particle(target_slot.x + target_slot.size // 2, target_slot.y + target_slot.size // 2)
                        return True
                    else:
                        # Partial stack, return remainder
                        return False
            else:
                # Different items, swap
                temp_item = {
                    'item_id': target_slot.item_id,
                    'quantity': target_slot.item_quantity,
                    'quality': target_slot.item_quality
                }
                
                target_slot.item_id = self.dragging_item['item_id']
                target_slot.item_quantity = self.dragging_item['quantity']
                target_slot.item_quality = self.dragging_item['quality']
                
                # Put target item in source slot
                if self.drag_source_slot:
                    self.drag_source_slot.item_id = temp_item['item_id']
                    self.drag_source_slot.item_quantity = temp_item['quantity']
                    self.drag_source_slot.item_quality = temp_item['quality']
                
                self._create_success_particle(target_slot.x + target_slot.size // 2, target_slot.y + target_slot.size // 2)
                return True
        else:
            # Empty slot, place item
            target_slot.item_id = self.dragging_item['item_id']
            target_slot.item_quantity = self.dragging_item['quantity']
            target_slot.item_quality = self.dragging_item['quality']
            
            self._create_success_particle(target_slot.x + target_slot.size // 2, target_slot.y + target_slot.size // 2)
            return True
        
        return False
    
    def _return_item_to_source(self):
        """Return dragged item to its source slot"""
        if self.drag_source_slot and self.dragging_item:
            self.drag_source_slot.item_id = self.dragging_item['item_id']
            self.drag_source_slot.item_quantity = self.dragging_item['quantity']
            self.drag_source_slot.item_quality = self.dragging_item['quality']
    
    def _end_drag(self):
        """End the current drag operation"""
        self.is_dragging = False
        self.dragging_item = None
        self.drag_source_slot = None
        self.drag_offset = (0, 0)
        
        # Sync changes back to inventory system
        self._sync_inventory_from_slots()
    
    def _cancel_drag(self):
        """Cancel current drag operation"""
        if self.is_dragging:
            self._return_item_to_source()
            self._end_drag()
    
    def _handle_mouse_motion(self, mouse_x: int, mouse_y: int):
        """Handle mouse motion for hover effects"""
        # Update hover states
        for slot in self.inventory_slots + self.hotbar_slots + self.equipment_slots:
            slot.is_hovered = slot.rect.collidepoint(mouse_x, mouse_y)
        
        if self.trash_slot:
            self.trash_slot.is_hovered = self.trash_slot.rect.collidepoint(mouse_x, mouse_y)
    
    def _sync_inventory_from_slots(self):
        """Sync inventory system from slot contents"""
        # This is a simplified version - in a full implementation,
        # you'd need to carefully manage the inventory state
        pass
    
    def _trash_item(self, item_id: str, quantity: int):
        """Delete an item (move to trash)"""
        self._create_trash_particle(self.trash_slot.x + self.trash_slot.size // 2, 
                                   self.trash_slot.y + self.trash_slot.size // 2)
        print(f"Trashed {quantity}x {item_id}")
    
    def _quick_use_item(self, item_id: str):
        """Quick use/consume an item"""
        item_data = self.inventory.get_item_data(item_id)
        if item_data and item_data.item_type == ItemType.FOOD:
            print(f"Consumed {item_data.name}")
            # Remove from inventory and apply effects
    
    def _auto_sort_inventory(self):
        """Automatically sort inventory items"""
        # Collect all items
        all_items = []
        for slot in self.inventory_slots:
            if slot.item_id:
                all_items.append({
                    'item_id': slot.item_id,
                    'quantity': slot.item_quantity,
                    'quality': slot.item_quality
                })
                slot.item_id = None
                slot.item_quantity = 0
                slot.item_quality = 1
        
        # Sort items by type, then by name
        def sort_key(item):
            item_data = self.inventory.get_item_data(item['item_id'])
            if item_data:
                return (item_data.item_type.value, item_data.name)
            return (99, item['item_id'])
        
        all_items.sort(key=sort_key)
        
        # Place items back in sorted order
        for i, item in enumerate(all_items):
            if i < len(self.inventory_slots):
                slot = self.inventory_slots[i]
                slot.item_id = item['item_id']
                slot.item_quantity = item['quantity']
                slot.item_quality = item['quality']
        
        print("Inventory sorted!")
    
    def _create_success_particle(self, x: int, y: int):
        """Create success particle effect"""
        for _ in range(5):
            particle = {
                'x': x + random.randint(-10, 10),
                'y': y + random.randint(-10, 10),
                'vx': random.uniform(-30, 30),
                'vy': random.uniform(-50, -20),
                'life': 1.0,
                'color': (100, 255, 100),
                'type': 'success'
            }
            self.particles.append(particle)
    
    def _create_error_particle(self, x: int, y: int):
        """Create error particle effect"""
        for _ in range(3):
            particle = {
                'x': x + random.randint(-10, 10),
                'y': y + random.randint(-10, 10),
                'vx': random.uniform(-20, 20),
                'vy': random.uniform(-30, -10),
                'life': 0.8,
                'color': (255, 100, 100),
                'type': 'error'
            }
            self.particles.append(particle)
    
    def _create_trash_particle(self, x: int, y: int):
        """Create trash particle effect"""
        for _ in range(8):
            particle = {
                'x': x + random.randint(-15, 15),
                'y': y + random.randint(-15, 15),
                'vx': random.uniform(-40, 40),
                'vy': random.uniform(-60, -30),
                'life': 1.5,
                'color': (255, 150, 100),
                'type': 'trash'
            }
            self.particles.append(particle)
    
    def update(self, dt: float):
        """Update animations and particles"""
        # Update particles
        for particle in self.particles[:]:
            particle['life'] -= dt
            particle['x'] += particle['vx'] * dt
            particle['y'] += particle['vy'] * dt
            particle['vy'] += 100 * dt  # Gravity
            
            if particle['life'] <= 0:
                self.particles.remove(particle)
        
        # Update slot animations
        for slot in self.inventory_slots + self.hotbar_slots + self.equipment_slots:
            if slot.is_hovered:
                slot.hover_animation = min(1.0, slot.hover_animation + dt * 5)
            else:
                slot.hover_animation = max(0.0, slot.hover_animation - dt * 3)
    
    def draw(self):
        """Draw the drag-drop inventory"""
        if not self.visible:
            self._draw_hotbar()  # Always show hotbar
            return
        
        # Draw main inventory panel
        self._draw_main_panel()
        
        # Draw slots
        self._draw_inventory_slots()
        self._draw_equipment_slots()
        self._draw_trash_slot()
        
        # Draw hotbar
        self._draw_hotbar()
        
        # Draw dragged item
        if self.is_dragging and self.dragging_item:
            self._draw_dragged_item()
        
        # Draw particles
        self._draw_particles()
        
        # Draw UI info
        self._draw_ui_info()
        
        # Draw hover tooltip (on top of everything)
        self._draw_hover_tooltip()
    
    def _draw_main_panel(self):
        """Draw the main inventory panel"""
        panel_rect = pygame.Rect(self.panel_x, self.panel_y, self.panel_width, self.panel_height)
        pygame.draw.rect(self.screen, self.bg_color, panel_rect, border_radius=12)
        pygame.draw.rect(self.screen, (100, 110, 130), panel_rect, 3, border_radius=12)
        
        # Title
        title_surface = self.font_normal.render("Inventory", True, (255, 255, 255))
        self.screen.blit(title_surface, (self.panel_x + 20, self.panel_y + 15))
        
        # Stats
        stats_text = f"Gold: {self.inventory.money}g | Weight: {self._get_total_weight():.1f}kg"
        stats_surface = self.font_small.render(stats_text, True, (200, 200, 200))
        self.screen.blit(stats_surface, (self.panel_x + 20, self.panel_y + 40))
    
    def _draw_inventory_slots(self):
        """Draw main inventory slots"""
        for slot in self.inventory_slots:
            self._draw_slot(slot)
    
    def _draw_equipment_slots(self):
        """Draw equipment slots"""
        # Equipment section title
        title_surface = self.font_small.render("Equipment", True, (255, 255, 255))
        self.screen.blit(title_surface, (self.panel_x + self.panel_width - 80, self.panel_y + 35))
        
        for slot in self.equipment_slots:
            self._draw_slot(slot, show_type_hint=True)
    
    def _draw_trash_slot(self):
        """Draw trash slot"""
        if self.trash_slot:
            # Trash label
            label_surface = self.font_tiny.render("Trash", True, (255, 100, 100))
            self.screen.blit(label_surface, (self.trash_slot.x, self.trash_slot.y - 15))
            
            # Special trash slot styling
            slot_rect = self.trash_slot.rect
            color = self.trash_color if self.trash_slot.is_hovered else (100, 50, 50)
            pygame.draw.rect(self.screen, color, slot_rect, border_radius=8)
            pygame.draw.rect(self.screen, (150, 100, 100), slot_rect, 2, border_radius=8)
            
            # Trash icon
            trash_icon = "🗑️"
            icon_surface = self.font_small.render(trash_icon, True, (255, 255, 255))
            icon_rect = icon_surface.get_rect(center=slot_rect.center)
            self.screen.blit(icon_surface, icon_rect)
    
    def _draw_hotbar(self):
        """Draw hotbar (always visible)"""
        for i, slot in enumerate(self.hotbar_slots):
            self._draw_slot(slot, show_number=True, slot_number=i + 1)
    
    def _draw_slot(self, slot: DragDropSlot, show_type_hint: bool = False, show_number: bool = False, slot_number: int = 0):
        """Draw an individual slot"""
        # Slot background
        color = self.slot_hover_color if slot.is_hovered else self.slot_color
        
        # Add hover animation
        if slot.hover_animation > 0:
            glow_intensity = int(30 * slot.hover_animation)
            color = tuple(min(255, c + glow_intensity) for c in color)
        
        pygame.draw.rect(self.screen, color, slot.rect, border_radius=8)
        pygame.draw.rect(self.screen, self.slot_border_color, slot.rect, 2, border_radius=8)
        
        # Slot number (for hotbar)
        if show_number:
            number_surface = self.font_tiny.render(str(slot_number), True, (200, 200, 200))
            self.screen.blit(number_surface, (slot.x + 2, slot.y + 2))
        
        # Type hint (for equipment slots)
        if show_type_hint and not slot.item_id:
            hint_text = slot.slot_type.split("_")[1] if "_" in slot.slot_type else ""
            hint_surface = self.font_tiny.render(hint_text.title(), True, (150, 150, 150))
            hint_rect = hint_surface.get_rect(center=slot.rect.center)
            self.screen.blit(hint_surface, hint_rect)
        
        # Item
        if slot.item_id:
            self._draw_item_in_slot(slot)
    
    def _draw_item_in_slot(self, slot: DragDropSlot):
        """Draw item inside a slot"""
        item_data = self.inventory.get_item_data(slot.item_id)
        if not item_data:
            return
        
        # Item icon
        icon_surface = self.font_normal.render(item_data.icon, True, (255, 255, 255))
        icon_rect = icon_surface.get_rect(center=(slot.x + slot.size // 2, slot.y + slot.size // 2 - 5))
        self.screen.blit(icon_surface, icon_rect)
        
        # Quantity
        if slot.item_quantity > 1:
            qty_surface = self.font_tiny.render(str(slot.item_quantity), True, (255, 255, 255))
            qty_rect = qty_surface.get_rect()
            qty_rect.bottomright = (slot.x + slot.size - 2, slot.y + slot.size - 2)
            
            # Quantity background
            bg_rect = qty_rect.inflate(2, 1)
            pygame.draw.rect(self.screen, (0, 0, 0, 180), bg_rect, border_radius=2)
            self.screen.blit(qty_surface, qty_rect)
        
        # Quality stars
        if slot.item_quality > 1:
            stars_text = "⭐" * slot.item_quality
            stars_surface = self.font_tiny.render(stars_text, True, (255, 215, 0))
            stars_rect = stars_surface.get_rect()
            stars_rect.bottomleft = (slot.x + 2, slot.y + slot.size - 2)
            self.screen.blit(stars_surface, stars_rect)
    
    def _draw_dragged_item(self):
        """Draw the item being dragged"""
        if not self.dragging_item:
            return
        
        mouse_x, mouse_y = pygame.mouse.get_pos()
        draw_x = mouse_x - self.drag_offset[0]
        draw_y = mouse_y - self.drag_offset[1]
        
        # Semi-transparent background
        drag_rect = pygame.Rect(draw_x, draw_y, self.slot_size, self.slot_size)
        pygame.draw.rect(self.screen, self.drag_color, drag_rect, border_radius=8)
        pygame.draw.rect(self.screen, (150, 180, 220), drag_rect, 2, border_radius=8)
        
        # Item icon
        item_data = self.inventory.get_item_data(self.dragging_item['item_id'])
        if item_data:
            icon_surface = self.font_normal.render(item_data.icon, True, (255, 255, 255))
            icon_rect = icon_surface.get_rect(center=drag_rect.center)
            self.screen.blit(icon_surface, icon_rect)
            
            # Quantity
            if self.dragging_item['quantity'] > 1:
                qty_surface = self.font_tiny.render(str(self.dragging_item['quantity']), True, (255, 255, 255))
                qty_rect = qty_surface.get_rect()
                qty_rect.bottomright = drag_rect.bottomright
                self.screen.blit(qty_surface, qty_rect)
    
    def _draw_particles(self):
        """Draw particle effects"""
        for particle in self.particles:
            alpha = int(255 * particle['life'])
            color = (*particle['color'], alpha)
            
            size = 3 if particle['type'] == 'success' else 2
            pygame.draw.circle(self.screen, particle['color'], 
                             (int(particle['x']), int(particle['y'])), size)
    
    def _draw_ui_info(self):
        """Draw UI information and controls"""
        if self.visible:
            info_y = self.panel_y + self.panel_height - 20
            controls = "TAB: Close | Drag & Drop: Move Items | Right Click: Use | Ctrl+S: Sort"
            controls_surface = self.font_tiny.render(controls, True, (180, 180, 180))
            self.screen.blit(controls_surface, (self.panel_x + 10, info_y))
    
    def _get_total_weight(self) -> float:
        """Calculate total weight of items in inventory"""
        # This would integrate with the movement system's weight calculation
        return 42.5  # Placeholder
    
    def _get_hovered_slot(self) -> Optional[DragDropSlot]:
        """Get the currently hovered slot"""
        for slot in self.inventory_slots + self.hotbar_slots + self.equipment_slots:
            if slot.is_hovered and slot.item_id:
                return slot
        return None
    
    def _draw_hover_tooltip(self):
        """Draw tooltip for hovered item"""
        if self.is_dragging:  # Don't show tooltip while dragging
            return
            
        hovered_slot = self._get_hovered_slot()
        if not hovered_slot or not hovered_slot.item_id:
            return
        
        item_data = self.inventory.get_item_data(hovered_slot.item_id)
        if not item_data:
            return
        
        # Get mouse position
        mouse_x, mouse_y = pygame.mouse.get_pos()
        
        # Build tooltip content
        tooltip_lines = []
        
        # Title with icon and quality stars
        title = f"{item_data.icon} {item_data.name}"
        if hovered_slot.item_quality > 1:
            title += f" {'⭐' * hovered_slot.item_quality}"
        tooltip_lines.append((title, self.rarity_colors.get(item_data.rarity, (255, 255, 255)), self.font_normal, True))
        
        # Basic info
        tooltip_lines.append((f"Type: {item_data.item_type.value.title()}", (200, 200, 200), self.font_small, False))
        tooltip_lines.append((f"Rarity: {item_data.rarity.value.title()}", self.rarity_colors.get(item_data.rarity, (150, 150, 150)), self.font_small, False))
        
        # Quantity
        if hovered_slot.item_quantity > 1:
            tooltip_lines.append((f"Quantity: {hovered_slot.item_quantity}", (255, 255, 255), self.font_small, False))
        
        # Value
        single_value = self.inventory.get_item_value(hovered_slot.item_id, hovered_slot.item_quality)
        total_value = single_value * hovered_slot.item_quantity
        if hovered_slot.item_quantity > 1:
            tooltip_lines.append((f"Value: {single_value}g each, {total_value}g total", (100, 255, 100), self.font_small, False))
        else:
            tooltip_lines.append((f"Value: {total_value}g", (100, 255, 100), self.font_small, False))
        
        # Type-specific stats
        self._add_tooltip_type_stats(tooltip_lines, item_data, hovered_slot)
        
        # Description
        tooltip_lines.append(("─" * 25, (100, 100, 100), self.font_tiny, False))
        tooltip_lines.append((item_data.description, (220, 220, 220), self.font_small, False))
        
        # Calculate tooltip size
        tooltip_width = 250
        line_height = 14
        title_height = 18
        tooltip_height = sum(title_height if is_title else line_height for _, _, _, is_title in tooltip_lines) + 15
        
        # Position tooltip
        tooltip_x = mouse_x + 15
        tooltip_y = mouse_y - tooltip_height // 2
        
        # Keep on screen
        if tooltip_x + tooltip_width > SCREEN_WIDTH:
            tooltip_x = mouse_x - tooltip_width - 15
        if tooltip_y < 10:
            tooltip_y = 10
        if tooltip_y + tooltip_height > SCREEN_HEIGHT - 10:
            tooltip_y = SCREEN_HEIGHT - tooltip_height - 10
        
        # Draw tooltip background
        tooltip_rect = pygame.Rect(tooltip_x, tooltip_y, tooltip_width, tooltip_height)
        pygame.draw.rect(self.screen, (20, 25, 35, 245), tooltip_rect, border_radius=6)
        pygame.draw.rect(self.screen, self.rarity_colors.get(item_data.rarity, (150, 150, 150)), tooltip_rect, 2, border_radius=6)
        
        # Draw tooltip content
        y_offset = tooltip_y + 8
        for text, color, font, is_title in tooltip_lines:
            text_surface = font.render(text, True, color)
            self.screen.blit(text_surface, (tooltip_x + 8, y_offset))
            y_offset += title_height if is_title else line_height
    
    def _add_tooltip_type_stats(self, tooltip_lines: List, item_data: ItemData, slot: DragDropSlot):
        """Add type-specific information to tooltip"""
        item_type = item_data.item_type
        
        if item_type == ItemType.TOOL:
            efficiency = slot.item_quality * 20
            tooltip_lines.append((f"Efficiency: {efficiency}%", (100, 200, 255), self.font_small, False))
            tooltip_lines.append(("Double-click to equip", (200, 200, 100), self.font_tiny, False))
            
        elif item_type == ItemType.FOOD:
            health = item_data.base_value // 2 + (slot.item_quality - 1) * 10
            energy = item_data.base_value // 3 + (slot.item_quality - 1) * 8
            tooltip_lines.append((f"Health: +{health}", (255, 100, 100), self.font_small, False))
            tooltip_lines.append((f"Energy: +{energy}", (100, 255, 100), self.font_small, False))
            
        elif item_type == ItemType.SEED:
            grow_times = {
                "parsnip_seeds": "4 days",
                "potato_seeds": "6 days",
                "cauliflower_seeds": "12 days",
                "tomato_seeds": "11 days"
            }
            grow_time = grow_times.get(item_data.item_id, "Variable")
            tooltip_lines.append((f"Grow Time: {grow_time}", (100, 255, 100), self.font_small, False))
            
        elif item_type == ItemType.FISH:
            size_map = {
                ItemRarity.COMMON: "Small",
                ItemRarity.UNCOMMON: "Medium",
                ItemRarity.RARE: "Large",
                ItemRarity.EPIC: "Huge",
                ItemRarity.LEGENDARY: "Massive"
            }
            size = size_map.get(item_data.rarity, "Unknown")
            tooltip_lines.append((f"Size: {size}", (100, 200, 255), self.font_small, False))
            
        elif item_type == ItemType.MINERAL:
            if "ore" in item_data.item_id:
                tooltip_lines.append(("Can be processed", (255, 150, 100), self.font_small, False))
            if item_data.rarity in [ItemRarity.RARE, ItemRarity.EPIC, ItemRarity.LEGENDARY]:
                tooltip_lines.append(("Valuable gem! 💎", (255, 215, 0), self.font_small, False))