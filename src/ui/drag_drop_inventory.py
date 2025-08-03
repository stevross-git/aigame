import pygame
import math
import random
from typing import Dict, List, Optional, Tuple, Any
from src.core.constants import *
from src.systems.inventory_system import InventorySystem, ItemType, ItemRarity, ItemData, InventoryItem
from src.graphics.tool_tileset import get_tool_tileset

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
    
    def __init__(self, screen, inventory_system: InventorySystem, action_bar=None, player=None):
        self.screen = screen
        self.inventory = inventory_system
        self.action_bar = action_bar
        self.player = player  # Reference to player for weight display
        self.visible = False
        
        # Initialize tool tileset
        self.tool_tileset = get_tool_tileset()
        
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
        
        # Layout - adjusted for 1600x900 resolution
        self.panel_width = 520
        self.panel_height = 450
        self.panel_x = (SCREEN_WIDTH - self.panel_width) // 2
        self.panel_y = (SCREEN_HEIGHT - self.panel_height) // 2
        
        # Slots - optimized for better visual alignment
        self.slot_size = 48
        self.slot_spacing = 6
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
        self.drag_threshold = 5  # Minimum pixels to move before starting drag
        self.mouse_down_pos = None
        self.mouse_down_slot = None
        self.potential_drag = False
        
        # Quick actions
        self.quick_stack_enabled = True
        self.auto_sort_enabled = True
        self.shift_click_enabled = True
        
        # Visual effects
        self.particles = []
        self.slot_animations = {}
        
        # Context menu for right-click
        self.context_menu_visible = False
        self.context_menu_item = None
        self.context_menu_slot = None
        self.context_menu_x = 0
        self.context_menu_y = 0
        self.context_menu_options = []
        
        self._initialize_slots()
    
    def _initialize_slots(self):
        """Initialize all inventory slots"""
        # Main inventory grid (6x6 = 36 slots) - better positioning
        grid_start_x = self.panel_x + 25
        grid_start_y = self.panel_y + 90
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
        
        # Equipment slots (right side of inventory) - adjusted for new panel size
        equipment_x = self.panel_x + self.panel_width - 85
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
        
        # Trash slot - adjusted for new panel size
        trash_x = self.panel_x + self.panel_width - 85
        trash_y = self.panel_y + self.panel_height - 65
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
        
        # Sync equipped items from action bar to equipment slots
        if self.action_bar:
            equipped_tool = self.action_bar.get_equipped_tool()
            if equipped_tool:
                # Find the tool equipment slot and populate it
                for slot in self.equipment_slots:
                    if slot.slot_type == "equipment_tool":
                        if self.inventory.has_item(equipped_tool):
                            slot.item_id = equipped_tool
                            slot.item_quantity = 1
                            slot.item_quality = 1
                        break
    
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
            elif event.key == pygame.K_ESCAPE:
                if self.context_menu_visible:
                    self.context_menu_visible = False
                    return True
                elif self.visible:
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
            if event.button == 1:
                if self.is_dragging:
                    return self._handle_drop(mouse_x, mouse_y)
                elif self.potential_drag:
                    # This was just a click, not a drag
                    self._handle_item_click()
                    self._reset_drag_state()
                    return True
        
        elif event.type == pygame.MOUSEMOTION:
            self._handle_mouse_motion(mouse_x, mouse_y)
            
            # Check if we should start dragging
            if self.potential_drag and not self.is_dragging and self.mouse_down_pos:
                dx = mouse_x - self.mouse_down_pos[0]
                dy = mouse_y - self.mouse_down_pos[1]
                if abs(dx) > self.drag_threshold or abs(dy) > self.drag_threshold:
                    self._start_drag(mouse_x, mouse_y)
        
        return True
    
    def _handle_left_click(self, mouse_x: int, mouse_y: int) -> bool:
        """Handle left mouse click - prepare for potential drag"""
        slot = self._get_slot_at_pos(mouse_x, mouse_y)
        
        if slot and slot.item_id:
            # Prepare for potential drag
            self.potential_drag = True
            self.mouse_down_pos = (mouse_x, mouse_y)
            self.mouse_down_slot = slot
            return True
        
        return False
    
    def _start_drag(self, mouse_x: int, mouse_y: int):
        """Start dragging operation"""
        if not self.mouse_down_slot or not self.mouse_down_slot.item_id:
            return
        
        self.is_dragging = True
        self.dragging_item = {
            'item_id': self.mouse_down_slot.item_id,
            'quantity': self.mouse_down_slot.item_quantity,
            'quality': self.mouse_down_slot.item_quality
        }
        self.drag_source_slot = self.mouse_down_slot
        self.drag_start_pos = self.mouse_down_pos
        
        # Calculate offset from mouse to item center for smoother dragging
        slot_center_x = self.mouse_down_slot.x + self.mouse_down_slot.size // 2
        slot_center_y = self.mouse_down_slot.y + self.mouse_down_slot.size // 2
        self.drag_offset = (mouse_x - slot_center_x, mouse_y - slot_center_y)
        
        # If dragging from equipment tool slot, unequip from action bar
        if self.mouse_down_slot.slot_type == "equipment_tool" and self.action_bar:
            # Find which action bar slot has this item and unequip it
            for slot_idx, item_id in self.action_bar.equipped_items.items():
                if item_id == self.mouse_down_slot.item_id:
                    self.action_bar.unequip_slot(slot_idx)
                    break
        
        # Clear source slot temporarily
        self.mouse_down_slot.item_id = None
        self.mouse_down_slot.item_quantity = 0
        self.mouse_down_slot.item_quality = 1
    
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
        """Handle right mouse click - show context menu"""
        # Check if clicking on context menu
        if self.context_menu_visible:
            return self._handle_context_menu_click(mouse_x, mouse_y)
        
        # Hide context menu if clicking elsewhere
        self.context_menu_visible = False
        
        slot = self._get_slot_at_pos(mouse_x, mouse_y)
        
        if slot and slot.item_id:
            # Show context menu for item
            self._show_context_menu(slot, mouse_x, mouse_y)
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
        
        self._reset_drag_state()
        return True
    
    def _handle_item_click(self):
        """Handle single click on item (quick use, info, etc.)"""
        if self.mouse_down_slot and self.mouse_down_slot.item_id:
            # Quick use item on single click
            self._quick_use_item(self.mouse_down_slot.item_id)
    
    def _reset_drag_state(self):
        """Reset all drag-related state"""
        self.is_dragging = False
        self.potential_drag = False
        self.dragging_item = None
        self.drag_source_slot = None
        self.mouse_down_pos = None
        self.mouse_down_slot = None
        self.drag_offset = (0, 0)
        
        # Clear highlighting on all slots
        for slot in self.inventory_slots + self.hotbar_slots + self.equipment_slots:
            slot.is_highlighted = False
        if self.trash_slot:
            self.trash_slot.is_highlighted = False
    
    def _move_item_to_slot(self, target_slot: DragDropSlot) -> bool:
        """Move dragged item to target slot"""
        # Check if this is an equipment slot that should sync with action bar
        is_tool_to_equipment = (target_slot.slot_type.startswith("equipment_") and 
                               target_slot.slot_type == "equipment_tool")
        
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
                
                # Sync tool equipment with action bar
                if is_tool_to_equipment and self.action_bar:
                    self.action_bar.equip_item(target_slot.item_id)
                
                return True
        else:
            # Empty slot, place item
            target_slot.item_id = self.dragging_item['item_id']
            target_slot.item_quantity = self.dragging_item['quantity']
            target_slot.item_quality = self.dragging_item['quality']
            
            self._create_success_particle(target_slot.x + target_slot.size // 2, target_slot.y + target_slot.size // 2)
            
            # Sync tool equipment with action bar
            if is_tool_to_equipment and self.action_bar:
                self.action_bar.equip_item(target_slot.item_id)
            
            return True
        
        return False
    
    def _return_item_to_source(self):
        """Return dragged item to its source slot"""
        if self.drag_source_slot and self.dragging_item:
            self.drag_source_slot.item_id = self.dragging_item['item_id']
            self.drag_source_slot.item_quantity = self.dragging_item['quantity']
            self.drag_source_slot.item_quality = self.dragging_item['quality']
    
    def _end_drag(self):
        """End the current drag operation (deprecated - use _reset_drag_state)"""
        self._reset_drag_state()
        
        # Sync changes back to inventory system
        self._sync_inventory_from_slots()
    
    def _cancel_drag(self):
        """Cancel current drag operation"""
        if self.is_dragging:
            self._return_item_to_source()
            self._end_drag()
    
    def _handle_mouse_motion(self, mouse_x: int, mouse_y: int):
        """Handle mouse motion for hover effects and drag preview"""
        # Update hover states
        for slot in self.inventory_slots + self.hotbar_slots + self.equipment_slots:
            was_hovered = slot.is_hovered
            slot.is_hovered = slot.rect.collidepoint(mouse_x, mouse_y)
            
            # Add visual feedback for valid drop targets while dragging
            if self.is_dragging and slot.is_hovered:
                if self._can_slot_accept_item(slot, self.dragging_item['item_id']):
                    slot.is_highlighted = True
                else:
                    slot.is_highlighted = False
            elif not slot.is_hovered:
                slot.is_highlighted = False
        
        if self.trash_slot:
            self.trash_slot.is_hovered = self.trash_slot.rect.collidepoint(mouse_x, mouse_y)
            if self.is_dragging and self.trash_slot.is_hovered:
                self.trash_slot.is_highlighted = True
            elif not self.trash_slot.is_hovered:
                self.trash_slot.is_highlighted = False
    
    def _sync_inventory_from_slots(self):
        """Sync inventory system from slot contents"""
        # Sync equipment slots to action bar
        if self.action_bar:
            for slot in self.equipment_slots:
                if slot.slot_type == "equipment_tool" and slot.item_id:
                    # Make sure the tool is equipped in action bar
                    self.action_bar.equip_item(slot.item_id)
        
        # Note: Inventory slot syncing is handled by the main inventory system
        # Equipment slots are maintained by the drag-drop system and synced to action bar
    
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
            # Don't draw hotbar here - we have a dedicated action bar system
            return
        
        # Draw main inventory panel
        self._draw_main_panel()
        
        # Draw slots
        self._draw_inventory_slots()
        self._draw_equipment_slots()
        self._draw_trash_slot()
        
        # Don't draw hotbar here - we have a dedicated action bar system
        
        # Draw dragged item
        if self.is_dragging and self.dragging_item:
            self._draw_dragged_item()
        
        # Draw particles
        self._draw_particles()
        
        # Draw UI info
        self._draw_ui_info()
        
        # Draw context menu (above most UI)
        if self.context_menu_visible:
            self._draw_context_menu()
        
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
        
        # Stats with player weight if available
        if self.player:
            current_weight = self.player.get_total_weight()
            max_weight = self.player.max_carry_weight
            weight_ratio = self.player.get_weight_ratio()
            
            # Color based on weight status
            if self.player.encumbered:
                weight_color = (255, 100, 100)  # Red for overencumbered
            elif weight_ratio > 0.75:
                weight_color = (255, 200, 100)  # Orange for heavily loaded
            elif weight_ratio > 0.5:
                weight_color = (255, 255, 150)  # Yellow for moderately loaded
            else:
                weight_color = (200, 255, 200)  # Green for light load
            
            stats_text = f"Gold: {self.inventory.money}g"
            weight_text = f"Weight: {current_weight:.1f}/{max_weight:.1f}kg"
            
            stats_surface = self.font_small.render(stats_text, True, (200, 200, 200))
            weight_surface = self.font_small.render(weight_text, True, weight_color)
            
            self.screen.blit(stats_surface, (self.panel_x + 20, self.panel_y + 40))
            self.screen.blit(weight_surface, (self.panel_x + 150, self.panel_y + 40))
            
            # Draw weight bar
            bar_x = self.panel_x + 320
            bar_y = self.panel_y + 42
            bar_width = 150
            bar_height = 12
            
            # Background
            pygame.draw.rect(self.screen, (50, 50, 50), (bar_x, bar_y, bar_width, bar_height), border_radius=3)
            
            # Fill based on weight ratio
            fill_width = int(bar_width * min(weight_ratio, 1.0))
            if fill_width > 0:
                pygame.draw.rect(self.screen, weight_color, (bar_x, bar_y, fill_width, bar_height), border_radius=3)
            
            # Overweight indicator
            if weight_ratio > 1.0:
                overflow_width = int(bar_width * min(weight_ratio - 1.0, 0.5))
                pygame.draw.rect(self.screen, (150, 50, 50), 
                                (bar_x + bar_width - overflow_width, bar_y, overflow_width, bar_height),
                                border_radius=3)
            
            # Border
            pygame.draw.rect(self.screen, (100, 100, 100), (bar_x, bar_y, bar_width, bar_height), 1, border_radius=3)
            
            # Encumbered text
            if self.player.encumbered:
                enc_text = "ENCUMBERED!"
                enc_surface = self.font_tiny.render(enc_text, True, (255, 100, 100))
                self.screen.blit(enc_surface, (bar_x + bar_width // 2 - 30, bar_y - 12))
        else:
            # Fallback without player reference
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
        
        # Highlight valid drop targets while dragging
        if slot.is_highlighted:
            highlight_color = (100, 255, 100, 80)  # Green for valid drop
            highlight_surface = pygame.Surface((slot.size, slot.size), pygame.SRCALPHA)
            highlight_surface.fill(highlight_color)
            self.screen.blit(highlight_surface, (slot.x, slot.y))
            
            # Add pulsing border for extra visibility
            import math
            import time
            pulse = (math.sin(time.time() * 6) + 1) / 2  # 0 to 1
            border_alpha = int(100 + pulse * 100)  # 100 to 200
            border_color = (100, 255, 100, border_alpha)
            
            border_surface = pygame.Surface((slot.size + 4, slot.size + 4), pygame.SRCALPHA)  
            pygame.draw.rect(border_surface, border_color, (0, 0, slot.size + 4, slot.size + 4), 3, border_radius=10)
            self.screen.blit(border_surface, (slot.x - 2, slot.y - 2))
        
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
        
        # Item icon - use tool sprites for tools, text for others
        if item_data.item_type == ItemType.TOOL:
            # Try to get tool sprite from tileset
            tool_sprite = self.tool_tileset.get_tool_icon(slot.item_id, (slot.size - 8, slot.size - 8))
            if tool_sprite:
                # Center the sprite in the slot
                sprite_rect = tool_sprite.get_rect(center=(slot.x + slot.size // 2, slot.y + slot.size // 2 - 5))
                self.screen.blit(tool_sprite, sprite_rect)
            else:
                # Fallback to text icon if sprite not found
                icon_surface = self.font_normal.render(item_data.icon, True, (255, 255, 255))
                icon_rect = icon_surface.get_rect(center=(slot.x + slot.size // 2, slot.y + slot.size // 2 - 5))
                self.screen.blit(icon_surface, icon_rect)
        else:
            # Use text icon for non-tools
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
        """Draw the item being dragged with improved visual feedback"""
        if not self.dragging_item:
            return
        
        mouse_x, mouse_y = pygame.mouse.get_pos()
        draw_x = mouse_x - self.drag_offset[0]
        draw_y = mouse_y - self.drag_offset[1]
        
        # Create dragged item surface with better visual feedback
        drag_rect = pygame.Rect(draw_x, draw_y, self.slot_size, self.slot_size)
        
        # Pulsing effect for dragged item
        import math
        import time
        pulse = (math.sin(time.time() * 8) + 1) / 2  # 0 to 1
        alpha = int(120 + pulse * 60)  # 120 to 180
        
        # Add a subtle glow effect
        glow_size = 6
        glow_surface = pygame.Surface((self.slot_size + glow_size * 2, self.slot_size + glow_size * 2), pygame.SRCALPHA)
        glow_color = (*self.drag_color[:3], 30)
        pygame.draw.rect(glow_surface, glow_color, (0, 0, self.slot_size + glow_size * 2, self.slot_size + glow_size * 2), border_radius=12)
        self.screen.blit(glow_surface, (draw_x - glow_size, draw_y - glow_size))
        
        # Main dragged item background
        drag_surface = pygame.Surface((self.slot_size, self.slot_size), pygame.SRCALPHA)
        drag_surface.fill((*self.drag_color[:3], alpha))
        pygame.draw.rect(drag_surface, (*self.drag_color[:3], alpha), (0, 0, self.slot_size, self.slot_size), border_radius=8)
        pygame.draw.rect(drag_surface, (200, 200, 255), (0, 0, self.slot_size, self.slot_size), 2, border_radius=8)
        self.screen.blit(drag_surface, (draw_x, draw_y))
        
        # Item icon - use tool sprites for tools, text for others
        item_data = self.inventory.get_item_data(self.dragging_item['item_id'])
        if item_data:
            if item_data.item_type == ItemType.TOOL:
                # Try to get tool sprite from tileset
                tool_sprite = self.tool_tileset.get_tool_icon(self.dragging_item['item_id'], (self.slot_size - 8, self.slot_size - 8))
                if tool_sprite:
                    # Center the sprite in the drag rect
                    sprite_rect = tool_sprite.get_rect(center=drag_rect.center)
                    self.screen.blit(tool_sprite, sprite_rect)
                else:
                    # Fallback to text icon if sprite not found
                    icon_surface = self.font_normal.render(item_data.icon, True, (255, 255, 255))
                    icon_rect = icon_surface.get_rect(center=drag_rect.center)
                    self.screen.blit(icon_surface, icon_rect)
            else:
                # Use text icon for non-tools
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
            controls = "TAB: Close | Drag & Drop: Move Items | Right Click: Context Menu | Ctrl+S: Sort"
            controls_surface = self.font_tiny.render(controls, True, (180, 180, 180))
            self.screen.blit(controls_surface, (self.panel_x + 10, info_y))
    
    def _get_total_weight(self) -> float:
        """Calculate total weight of all items"""
        return self.inventory.get_total_weight()
    
    def _show_context_menu(self, slot: DragDropSlot, mouse_x: int, mouse_y: int):
        """Show context menu for an item"""
        self.context_menu_visible = True
        self.context_menu_slot = slot
        self.context_menu_item = slot.item_id
        
        # Position menu near mouse but keep on screen
        menu_width = 180
        menu_height = 200  # Approximate max height
        
        self.context_menu_x = min(mouse_x, self.screen.get_width() - menu_width)
        self.context_menu_y = min(mouse_y, self.screen.get_height() - menu_height)
        
        # Build context menu options based on item type
        item_data = self.inventory.get_item_data(slot.item_id)
        self.context_menu_options = []
        
        if item_data:
            # Basic actions available for all items
            self.context_menu_options.append({
                'text': f'Use {item_data.name}',
                'action': 'use',
                'enabled': True,
                'description': 'Use or consume this item'
            })
            
            # Item-specific actions
            if item_data.item_type == ItemType.FOOD:
                self.context_menu_options.append({
                    'text': 'Eat',
                    'action': 'eat',
                    'enabled': True,
                    'description': 'Consume this food item'
                })
            elif item_data.item_type == ItemType.TOOL:
                self.context_menu_options.append({
                    'text': 'Equip to Action Bar',
                    'action': 'equip',
                    'enabled': self.action_bar is not None,
                    'description': 'Add to action bar for quick use'
                })
            elif item_data.item_type == ItemType.SEED:
                self.context_menu_options.append({
                    'text': 'Plant',
                    'action': 'plant',
                    'enabled': True,
                    'description': 'Plant this seed'
                })
            
            # Quantity actions
            if slot.item_quantity > 1:
                self.context_menu_options.append({
                    'text': 'Split Stack',
                    'action': 'split',
                    'enabled': True,
                    'description': 'Split this stack in half'
                })
            
            # Gift/social actions
            if item_data.can_gift:
                self.context_menu_options.append({
                    'text': 'Gift to NPC',
                    'action': 'gift',
                    'enabled': True,
                    'description': 'Give this item as a gift'
                })
            
            # Selling
            if item_data.can_sell:
                value = self.inventory.get_item_value(slot.item_id, slot.item_quality)
                self.context_menu_options.append({
                    'text': f'Sell ({value}g)',
                    'action': 'sell',
                    'enabled': True,
                    'description': f'Sell for {value} gold'
                })
            
            # Item info
            self.context_menu_options.append({
                'text': 'Item Info',
                'action': 'info',
                'enabled': True,
                'description': 'View detailed item information'
            })
            
            # Trash action
            self.context_menu_options.append({
                'text': 'Destroy',
                'action': 'destroy',
                'enabled': True,
                'description': 'Permanently destroy this item'
            })
    
    def _handle_context_menu_click(self, mouse_x: int, mouse_y: int) -> bool:
        """Handle clicking on context menu options"""
        if not self.context_menu_visible or not self.context_menu_options:
            return False
        
        # Calculate menu dimensions
        menu_width = 180
        option_height = 25
        menu_height = len(self.context_menu_options) * option_height + 10
        
        # Check if click is within menu bounds
        menu_rect = pygame.Rect(self.context_menu_x, self.context_menu_y, menu_width, menu_height)
        if not menu_rect.collidepoint(mouse_x, mouse_y):
            # Click outside menu - close it
            self.context_menu_visible = False
            return True
        
        # Find which option was clicked
        relative_y = mouse_y - self.context_menu_y - 5
        option_index = int(relative_y // option_height)
        
        if 0 <= option_index < len(self.context_menu_options):
            option = self.context_menu_options[option_index]
            if option['enabled']:
                self._execute_context_action(option['action'])
        
        # Close menu after action
        self.context_menu_visible = False
        return True
    
    def _execute_context_action(self, action: str):
        """Execute the selected context menu action"""
        if not self.context_menu_slot or not self.context_menu_item:
            return
        
        slot = self.context_menu_slot
        item_id = self.context_menu_item
        item_data = self.inventory.get_item_data(item_id)
        
        if action == 'use':
            self._quick_use_item(item_id)
        
        elif action == 'eat' and item_data and item_data.item_type == ItemType.FOOD:
            self._eat_food_item(slot)
        
        elif action == 'equip' and self.action_bar:
            self._equip_to_action_bar(slot)
        
        elif action == 'plant':
            self._plant_seed(slot)
        
        elif action == 'split' and slot.item_quantity > 1:
            self._split_item_stack(slot)
        
        elif action == 'gift':
            self._prepare_gift_item(slot)
        
        elif action == 'sell':
            self._sell_item_from_slot(slot)
        
        elif action == 'info':
            self._show_item_info(slot)
        
        elif action == 'destroy':
            self._destroy_item(slot)
    
    def _eat_food_item(self, slot: DragDropSlot):
        """Eat a food item to restore needs"""
        if not slot.item_id or slot.item_quantity <= 0:
            return
        
        item_data = self.inventory.get_item_data(slot.item_id)
        if not item_data or item_data.item_type != ItemType.FOOD:
            return
        
        # Restore player hunger based on food value
        if self.player:
            hunger_restore = min(0.3, item_data.base_value / 200.0)  # Scale by value
            self.player.needs['hunger'] = min(1.0, self.player.needs['hunger'] + hunger_restore)
            
            # Show feedback
            if hasattr(self.player, 'say'):
                self.player.say(f"Ate {item_data.name}! (+{hunger_restore:.1%} hunger)")
        
        # Remove one item
        self.inventory.remove_item(slot.item_id, 1)
        slot.item_quantity -= 1
        if slot.item_quantity <= 0:
            slot.item_id = None
            slot.item_quality = 1
        
        self._create_success_particle(slot.x + slot.size // 2, slot.y + slot.size // 2)
    
    def _equip_to_action_bar(self, slot: DragDropSlot):
        """Equip item to action bar"""
        if not self.action_bar or not slot.item_id:
            return
        
        # Find first empty action bar slot
        for i in range(len(self.action_bar.slots)):
            if not self.action_bar.equipped_items.get(i):
                self.action_bar.equip_item(i, slot.item_id)
                self._create_success_particle(slot.x + slot.size // 2, slot.y + slot.size // 2)
                return
        
        # If no empty slots, show message
        if hasattr(self.player, 'say'):
            self.player.say("Action bar is full!")
    
    def _plant_seed(self, slot: DragDropSlot):
        """Plant a seed (placeholder for farming system)"""
        if not slot.item_id:
            return
        
        item_data = self.inventory.get_item_data(slot.item_id)
        if not item_data or item_data.item_type != ItemType.SEED:
            return
        
        # For now, just show a message (would integrate with farming system)
        if hasattr(self.player, 'say'):
            self.player.say(f"Need to find suitable soil to plant {item_data.name}")
    
    def _split_item_stack(self, slot: DragDropSlot):
        """Split an item stack in half"""
        if not slot.item_id or slot.item_quantity <= 1:
            return
        
        # Find empty slot for the split portion
        empty_slot = None
        for inv_slot in self.inventory_slots:
            if not inv_slot.item_id:
                empty_slot = inv_slot
                break
        
        if not empty_slot:
            if hasattr(self.player, 'say'):
                self.player.say("No empty slots to split into!")
            return
        
        # Split the stack
        half_quantity = slot.item_quantity // 2
        remaining_quantity = slot.item_quantity - half_quantity
        
        # Update original slot
        slot.item_quantity = remaining_quantity
        
        # Fill empty slot with split portion
        empty_slot.item_id = slot.item_id
        empty_slot.item_quantity = half_quantity
        empty_slot.item_quality = slot.item_quality
        
        self._create_success_particle(empty_slot.x + empty_slot.size // 2, empty_slot.y + empty_slot.size // 2)
    
    def _prepare_gift_item(self, slot: DragDropSlot):
        """Prepare item for gifting to NPCs"""
        if not slot.item_id:
            return
        
        item_data = self.inventory.get_item_data(slot.item_id)
        if not item_data:
            return
        
        # For now, just show message (would integrate with NPC interaction)
        if hasattr(self.player, 'say'):
            self.player.say(f"Selected {item_data.name} as gift. Find an NPC to give it to!")
    
    def _sell_item_from_slot(self, slot: DragDropSlot):
        """Sell item from inventory"""
        if not slot.item_id or slot.item_quantity <= 0:
            return
        
        # Sell one item
        if self.inventory.sell_item(slot.item_id, 1):
            slot.item_quantity -= 1
            if slot.item_quantity <= 0:
                slot.item_id = None
                slot.item_quality = 1
            
            self._create_success_particle(slot.x + slot.size // 2, slot.y + slot.size // 2)
            
            if hasattr(self.player, 'say'):
                item_data = self.inventory.get_item_data(slot.item_id)
                value = self.inventory.get_item_value(slot.item_id, slot.item_quality) if item_data else 0
                self.player.say(f"Sold for {value}g!")
    
    def _show_item_info(self, slot: DragDropSlot):
        """Show detailed item information"""
        if not slot.item_id:
            return
        
        # For now, show basic info (could expand to detailed popup)
        item_data = self.inventory.get_item_data(slot.item_id)
        if item_data and hasattr(self.player, 'say'):
            info_text = f"{item_data.name}: {item_data.description} (Value: {item_data.base_value}g, Weight: {item_data.weight}kg)"
            self.player.say(info_text)
    
    def _destroy_item(self, slot: DragDropSlot):
        """Destroy an item permanently"""
        if not slot.item_id:
            return
        
        item_data = self.inventory.get_item_data(slot.item_id)
        
        # Remove from inventory and slot
        self.inventory.remove_item(slot.item_id, slot.item_quantity)
        slot.item_id = None
        slot.item_quantity = 0
        slot.item_quality = 1
        
        # Show feedback
        self._create_error_particle(slot.x + slot.size // 2, slot.y + slot.size // 2)
        if item_data and hasattr(self.player, 'say'):
            self.player.say(f"Destroyed {item_data.name}!")
    
    def _draw_context_menu(self):
        """Draw the context menu"""
        if not self.context_menu_visible or not self.context_menu_options:
            return
        
        # Menu dimensions
        menu_width = 180
        option_height = 25
        menu_height = len(self.context_menu_options) * option_height + 10
        
        # Menu background
        menu_rect = pygame.Rect(self.context_menu_x, self.context_menu_y, menu_width, menu_height)
        menu_surface = pygame.Surface((menu_width, menu_height), pygame.SRCALPHA)
        menu_surface.fill((40, 45, 55, 240))
        
        # Border
        pygame.draw.rect(menu_surface, (100, 110, 130), (0, 0, menu_width, menu_height), 2, border_radius=8)
        
        self.screen.blit(menu_surface, (self.context_menu_x, self.context_menu_y))
        
        # Draw options
        mouse_x, mouse_y = pygame.mouse.get_pos()
        
        for i, option in enumerate(self.context_menu_options):
            option_y = self.context_menu_y + 5 + i * option_height
            option_rect = pygame.Rect(self.context_menu_x + 5, option_y, menu_width - 10, option_height - 2)
            
            # Highlight hovered option
            if option_rect.collidepoint(mouse_x, mouse_y) and option['enabled']:
                highlight_surface = pygame.Surface((menu_width - 10, option_height - 2), pygame.SRCALPHA)
                highlight_surface.fill((70, 80, 100, 150))
                self.screen.blit(highlight_surface, (self.context_menu_x + 5, option_y))
            
            # Option text
            text_color = (255, 255, 255) if option['enabled'] else (120, 120, 120)
            text_surface = self.font_small.render(option['text'], True, text_color)
            self.screen.blit(text_surface, (self.context_menu_x + 10, option_y + 4))
        
        # Show description for hovered option
        for i, option in enumerate(self.context_menu_options):
            option_y = self.context_menu_y + 5 + i * option_height
            option_rect = pygame.Rect(self.context_menu_x + 5, option_y, menu_width - 10, option_height - 2)
            
            if option_rect.collidepoint(mouse_x, mouse_y) and option['enabled']:
                # Show description tooltip
                desc_text = option.get('description', '')
                if desc_text:
                    desc_surface = self.font_tiny.render(desc_text, True, (200, 200, 150))
                    desc_rect = desc_surface.get_rect()
                    
                    # Position description to the right of menu
                    desc_x = self.context_menu_x + menu_width + 5
                    desc_y = option_y
                    
                    # Keep on screen
                    if desc_x + desc_rect.width > self.screen.get_width():
                        desc_x = self.context_menu_x - desc_rect.width - 5
                    
                    # Background for description
                    desc_bg = pygame.Surface((desc_rect.width + 6, desc_rect.height + 4), pygame.SRCALPHA)
                    desc_bg.fill((20, 25, 35, 200))
                    self.screen.blit(desc_bg, (desc_x - 3, desc_y - 2))
                    
                    # Description text
                    self.screen.blit(desc_surface, (desc_x, desc_y))
                break
    
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