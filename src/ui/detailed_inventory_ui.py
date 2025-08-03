import pygame
import math
from typing import Dict, List, Optional, Tuple
from src.core.constants import *
from src.systems.inventory_system import InventorySystem, ItemType, ItemRarity, ItemData, InventoryItem

class DetailedInventoryUI:
    """
    Enhanced inventory UI with detailed item information, sorting, filtering, and management
    """
    
    def __init__(self, screen, inventory_system: InventorySystem):
        self.screen = screen
        self.inventory = inventory_system
        self.visible = False
        
        # Fonts
        self.font_title = pygame.font.Font(None, 28)
        self.font_normal = pygame.font.Font(None, 22)
        self.font_small = pygame.font.Font(None, 18)
        
        # Colors
        self.bg_color = (25, 35, 45, 240)
        self.panel_color = (45, 55, 65, 220)
        self.border_color = (100, 120, 140)
        self.text_color = (255, 255, 255)
        self.accent_color = (100, 150, 200)
        self.grid_color = (70, 80, 90)
        
        # Rarity colors
        self.rarity_colors = {
            ItemRarity.COMMON: (150, 150, 150),
            ItemRarity.UNCOMMON: (100, 255, 100),
            ItemRarity.RARE: (100, 100, 255),
            ItemRarity.EPIC: (200, 100, 255),
            ItemRarity.LEGENDARY: (255, 200, 50)
        }
        
        # Panel layout
        self.panel_width = 800
        self.panel_height = 600
        self.panel_x = (SCREEN_WIDTH - self.panel_width) // 2
        self.panel_y = (SCREEN_HEIGHT - self.panel_height) // 2
        
        # Grid settings
        self.slot_size = 60
        self.slots_per_row = 10
        self.grid_x = self.panel_x + 20
        self.grid_y = self.panel_y + 100
        self.grid_width = self.slots_per_row * (self.slot_size + 5) - 5
        self.grid_height = 300
        
        # Details panel
        self.details_x = self.panel_x + self.grid_width + 40
        self.details_y = self.grid_y
        self.details_width = self.panel_width - self.grid_width - 80
        self.details_height = self.grid_height
        
        # State
        self.selected_item = None
        self.hovered_item = None
        self.mouse_pos = (0, 0)
        self.scroll_offset = 0
        self.max_scroll = 0
        self.sort_method = "type"  # "type", "name", "value", "quantity", "rarity"
        self.filter_type = None  # None or ItemType
        self.search_term = ""
        
        # Context menu
        self.context_menu_visible = False
        self.context_menu_pos = (0, 0)
        self.context_menu_item = None
    
    def show(self):
        """Show the detailed inventory UI"""
        self.visible = True
        self.selected_item = None
        self.scroll_offset = 0
        self._update_scroll_limits()
    
    def hide(self):
        """Hide the detailed inventory UI"""
        self.visible = False
        self.context_menu_visible = False
    
    def toggle(self):
        """Toggle inventory visibility"""
        if self.visible:
            self.hide()
        else:
            self.show()
    
    def _get_filtered_sorted_items(self) -> List[Tuple[str, InventoryItem]]:
        """Get items filtered and sorted according to current settings"""
        all_items = list(self.inventory.get_all_items().items())
        
        # Apply type filter
        if self.filter_type:
            filtered_items = []
            for item_id, inv_item in all_items:
                item_data = self.inventory.get_item_data(item_id)
                if item_data and item_data.item_type == self.filter_type:
                    filtered_items.append((item_id, inv_item))
            all_items = filtered_items
        
        # Apply search filter
        if self.search_term:
            search_filtered = []
            for item_id, inv_item in all_items:
                item_data = self.inventory.get_item_data(item_id)
                if item_data and self.search_term.lower() in item_data.name.lower():
                    search_filtered.append((item_id, inv_item))
            all_items = search_filtered
        
        # Sort items
        def sort_key(item_tuple):
            item_id, inv_item = item_tuple
            item_data = self.inventory.get_item_data(item_id)
            if not item_data:
                return ""
            
            if self.sort_method == "name":
                return item_data.name.lower()
            elif self.sort_method == "value":
                return -self.inventory.get_item_value(item_id, inv_item.quality)
            elif self.sort_method == "quantity":
                return -inv_item.quantity
            elif self.sort_method == "rarity":
                rarity_order = {
                    ItemRarity.COMMON: 0,
                    ItemRarity.UNCOMMON: 1,
                    ItemRarity.RARE: 2,
                    ItemRarity.EPIC: 3,
                    ItemRarity.LEGENDARY: 4
                }
                return -rarity_order.get(item_data.rarity, 0)
            else:  # type
                type_order = {
                    ItemType.TOOL: 0,
                    ItemType.RESOURCE: 1,
                    ItemType.FOOD: 2,
                    ItemType.SEED: 3,
                    ItemType.CROP: 4,
                    ItemType.FISH: 5,
                    ItemType.MINERAL: 6,
                    ItemType.CRAFTED: 7,
                    ItemType.FURNITURE: 8,
                    ItemType.ARTIFACT: 9
                }
                return (type_order.get(item_data.item_type, 99), item_data.name.lower())
        
        all_items.sort(key=sort_key)
        return all_items
    
    def _update_scroll_limits(self):
        """Update scroll limits based on current items"""
        items = self._get_filtered_sorted_items()
        total_rows = math.ceil(len(items) / self.slots_per_row) if items else 0
        grid_rows = self.grid_height // (self.slot_size + 5)
        self.max_scroll = max(0, (total_rows - grid_rows) * (self.slot_size + 5))
    
    def _get_item_at_pos(self, mouse_x: int, mouse_y: int) -> Optional[str]:
        """Get item ID at mouse position"""
        if (mouse_x < self.grid_x or mouse_x > self.grid_x + self.grid_width or
            mouse_y < self.grid_y or mouse_y > self.grid_y + self.grid_height):
            return None
        
        slot_x = (mouse_x - self.grid_x) // (self.slot_size + 5)
        slot_y = (mouse_y - self.grid_y + self.scroll_offset) // (self.slot_size + 5)
        slot_index = slot_y * self.slots_per_row + slot_x
        
        items = self._get_filtered_sorted_items()
        if 0 <= slot_index < len(items):
            return items[slot_index][0]
        
        return None
    
    def handle_event(self, event) -> bool:
        """Handle UI events"""
        if not self.visible:
            return False
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE or event.key == pygame.K_i:
                self.hide()
                return True
            elif event.key == pygame.K_1:
                self.sort_method = "type"
                self._update_scroll_limits()
                return True
            elif event.key == pygame.K_2:
                self.sort_method = "name"
                self._update_scroll_limits()
                return True
            elif event.key == pygame.K_3:
                self.sort_method = "value"
                self._update_scroll_limits()
                return True
            elif event.key == pygame.K_4:
                self.sort_method = "rarity"
                self._update_scroll_limits()
                return True
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = event.pos
            
            # Check if clicking outside panel (close UI)
            panel_rect = pygame.Rect(self.panel_x, self.panel_y, self.panel_width, self.panel_height)
            if not panel_rect.collidepoint(mouse_x, mouse_y):
                self.hide()
                return True
            
            # Check context menu
            if self.context_menu_visible:
                self._handle_context_menu_click(mouse_x, mouse_y)
                return True
            
            # Check item clicks
            item_id = self._get_item_at_pos(mouse_x, mouse_y)
            if item_id:
                if event.button == 1:  # Left click
                    self.selected_item = item_id
                elif event.button == 3:  # Right click
                    self._show_context_menu(item_id, mouse_x, mouse_y)
                return True
            
            # Check filter buttons
            if self._handle_filter_clicks(mouse_x, mouse_y):
                return True
        
        elif event.type == pygame.MOUSEMOTION:
            mouse_x, mouse_y = event.pos
            self.mouse_pos = (mouse_x, mouse_y)
            self.hovered_item = self._get_item_at_pos(mouse_x, mouse_y)
        
        elif event.type == pygame.MOUSEWHEEL:
            if event.y > 0:
                self.scroll_offset = max(0, self.scroll_offset - (self.slot_size + 5))
            else:
                self.scroll_offset = min(self.max_scroll, self.scroll_offset + (self.slot_size + 5))
            return True
        
        return True  # Consume all events when visible
    
    def _handle_filter_clicks(self, mouse_x: int, mouse_y: int) -> bool:
        """Handle clicks on filter buttons"""
        filter_y = self.panel_y + 60
        filter_height = 25
        filter_width = 80
        
        filters = [
            (None, "All"),
            (ItemType.TOOL, "Tools"),
            (ItemType.RESOURCE, "Resources"),
            (ItemType.FOOD, "Food"),
            (ItemType.CROP, "Crops"),
            (ItemType.MINERAL, "Minerals")
        ]
        
        for i, (filter_type, filter_name) in enumerate(filters):
            filter_x = self.panel_x + 20 + i * (filter_width + 5)
            filter_rect = pygame.Rect(filter_x, filter_y, filter_width, filter_height)
            
            if filter_rect.collidepoint(mouse_x, mouse_y):
                self.filter_type = filter_type
                self.scroll_offset = 0
                self._update_scroll_limits()
                return True
        
        return False
    
    def _show_context_menu(self, item_id: str, x: int, y: int):
        """Show context menu for item"""
        self.context_menu_visible = True
        self.context_menu_pos = (x, y)
        self.context_menu_item = item_id
    
    def _handle_context_menu_click(self, mouse_x: int, mouse_y: int):
        """Handle context menu clicks"""
        menu_x, menu_y = self.context_menu_pos
        menu_width = 120
        menu_height = 80
        
        # Check if clicking outside menu
        menu_rect = pygame.Rect(menu_x, menu_y, menu_width, menu_height)
        if not menu_rect.collidepoint(mouse_x, mouse_y):
            self.context_menu_visible = False
            return
        
        # Calculate which option was clicked
        option_height = 20
        option_index = (mouse_y - menu_y) // option_height
        
        if self.context_menu_item:
            if option_index == 0:  # Use/Consume
                self._use_item(self.context_menu_item)
            elif option_index == 1:  # Drop
                self._drop_item(self.context_menu_item)
            elif option_index == 2:  # Sell
                self._sell_item(self.context_menu_item)
        
        self.context_menu_visible = False
    
    def _use_item(self, item_id: str):
        """Use/consume an item"""
        item_data = self.inventory.get_item_data(item_id)
        if item_data and item_data.item_type == ItemType.FOOD:
            # Consume food item (this would restore player stats in a full implementation)
            if self.inventory.remove_item(item_id, 1):
                print(f"Consumed {item_data.name}")
    
    def _drop_item(self, item_id: str):
        """Drop an item from inventory"""
        if self.inventory.remove_item(item_id, 1):
            item_data = self.inventory.get_item_data(item_id)
            print(f"Dropped {item_data.name if item_data else item_id}")
    
    def _sell_item(self, item_id: str):
        """Sell an item"""
        if self.inventory.sell_item(item_id, 1):
            item_data = self.inventory.get_item_data(item_id)
            value = self.inventory.get_item_value(item_id)
            print(f"Sold {item_data.name if item_data else item_id} for {value}g")
    
    def draw(self):
        """Draw the detailed inventory UI"""
        if not self.visible:
            return
        
        # Main panel
        panel_rect = pygame.Rect(self.panel_x, self.panel_y, self.panel_width, self.panel_height)
        pygame.draw.rect(self.screen, self.bg_color, panel_rect, border_radius=12)
        pygame.draw.rect(self.screen, self.border_color, panel_rect, 3, border_radius=12)
        
        # Title
        title_surface = self.font_title.render("Detailed Inventory", True, self.text_color)
        self.screen.blit(title_surface, (self.panel_x + 20, self.panel_y + 15))
        
        # Stats
        stats_text = f"Gold: {self.inventory.money}g | Slots: {self.inventory.get_inventory_slots_used()}/{self.inventory.max_slots}"
        stats_surface = self.font_normal.render(stats_text, True, self.accent_color)
        self.screen.blit(stats_surface, (self.panel_x + 250, self.panel_y + 18))
        
        # Draw filters
        self._draw_filters()
        
        # Draw sort options
        self._draw_sort_options()
        
        # Draw item grid
        self._draw_item_grid()
        
        # Draw item details
        if self.selected_item:
            self._draw_item_details()
        
        # Draw context menu
        if self.context_menu_visible:
            self._draw_context_menu()
        
        # Draw controls
        self._draw_controls()
        
        # Draw hover tooltip (on top of everything)
        if self.hovered_item and self.hovered_item != self.selected_item:
            self._draw_hover_tooltip()
    
    def _draw_filters(self):
        """Draw filter buttons"""
        filter_y = self.panel_y + 60
        filter_height = 25
        filter_width = 80
        
        filters = [
            (None, "All"),
            (ItemType.TOOL, "Tools"),
            (ItemType.RESOURCE, "Resources"),
            (ItemType.FOOD, "Food"),
            (ItemType.CROP, "Crops"),
            (ItemType.MINERAL, "Minerals")
        ]
        
        for i, (filter_type, filter_name) in enumerate(filters):
            filter_x = self.panel_x + 20 + i * (filter_width + 5)
            filter_rect = pygame.Rect(filter_x, filter_y, filter_width, filter_height)
            
            # Button background
            is_active = self.filter_type == filter_type
            button_color = self.accent_color if is_active else self.panel_color
            pygame.draw.rect(self.screen, button_color, filter_rect, border_radius=5)
            pygame.draw.rect(self.screen, self.border_color, filter_rect, 2, border_radius=5)
            
            # Button text
            text_surface = self.font_small.render(filter_name, True, self.text_color)
            text_rect = text_surface.get_rect(center=filter_rect.center)
            self.screen.blit(text_surface, text_rect)
    
    def _draw_sort_options(self):
        """Draw sort method indicator"""
        sort_text = f"Sort: {self.sort_method.title()} (1-4 to change)"
        sort_surface = self.font_small.render(sort_text, True, self.text_color)
        self.screen.blit(sort_surface, (self.panel_x + 20, self.panel_y + 90))
    
    def _draw_item_grid(self):
        """Draw the item grid"""
        items = self._get_filtered_sorted_items()
        
        # Draw grid background
        grid_rect = pygame.Rect(self.grid_x, self.grid_y, self.grid_width, self.grid_height)
        pygame.draw.rect(self.screen, self.panel_color, grid_rect, border_radius=8)
        pygame.draw.rect(self.screen, self.border_color, grid_rect, 2, border_radius=8)
        
        # Calculate visible range
        start_row = self.scroll_offset // (self.slot_size + 5)
        visible_rows = (self.grid_height // (self.slot_size + 5)) + 2
        
        for i, (item_id, inv_item) in enumerate(items):
            row = i // self.slots_per_row
            col = i % self.slots_per_row
            
            # Skip if not visible
            if row < start_row or row >= start_row + visible_rows:
                continue
            
            slot_x = self.grid_x + col * (self.slot_size + 5) + 5
            slot_y = self.grid_y + (row * (self.slot_size + 5)) - self.scroll_offset + 5
            
            # Skip if outside grid area
            if slot_y + self.slot_size < self.grid_y or slot_y > self.grid_y + self.grid_height:
                continue
            
            slot_rect = pygame.Rect(slot_x, slot_y, self.slot_size, self.slot_size)
            
            # Slot background
            is_selected = item_id == self.selected_item
            is_hovered = item_id == self.hovered_item
            
            if is_selected:
                slot_color = (100, 150, 200, 150)
            elif is_hovered:
                slot_color = (80, 120, 160, 100)
            else:
                slot_color = self.grid_color
            
            pygame.draw.rect(self.screen, slot_color, slot_rect, border_radius=8)
            
            # Rarity border
            item_data = self.inventory.get_item_data(item_id)
            if item_data:
                rarity_color = self.rarity_colors.get(item_data.rarity, (150, 150, 150))
                pygame.draw.rect(self.screen, rarity_color, slot_rect, 3, border_radius=8)
            
            # Item icon
            if item_data:
                icon_surface = self.font_normal.render(item_data.icon, True, self.text_color)
                icon_rect = icon_surface.get_rect(center=(slot_x + self.slot_size // 2, slot_y + self.slot_size // 2 - 5))
                self.screen.blit(icon_surface, icon_rect)
            
            # Quantity
            if inv_item.quantity > 1:
                qty_surface = self.font_small.render(str(inv_item.quantity), True, self.text_color)
                qty_rect = qty_surface.get_rect()
                qty_rect.bottomright = (slot_x + self.slot_size - 3, slot_y + self.slot_size - 3)
                
                # Quantity background
                bg_rect = qty_rect.inflate(4, 2)
                pygame.draw.rect(self.screen, (0, 0, 0, 180), bg_rect, border_radius=3)
                self.screen.blit(qty_surface, qty_rect)
            
            # Quality stars
            if inv_item.quality > 1:
                star_text = "⭐" * inv_item.quality
                star_surface = self.font_small.render(star_text, True, (255, 215, 0))
                star_rect = star_surface.get_rect()
                star_rect.bottomleft = (slot_x + 3, slot_y + self.slot_size - 3)
                self.screen.blit(star_surface, star_rect)
    
    def _draw_item_details(self):
        """Draw detailed information about selected item"""
        if not self.selected_item:
            return
        
        item_data = self.inventory.get_item_data(self.selected_item)
        inv_item = self.inventory.items.get(self.selected_item)
        
        if not item_data or not inv_item:
            return
        
        # Details panel background
        details_rect = pygame.Rect(self.details_x, self.details_y, self.details_width, self.details_height)
        pygame.draw.rect(self.screen, self.panel_color, details_rect, border_radius=8)
        pygame.draw.rect(self.screen, self.border_color, details_rect, 2, border_radius=8)
        
        y_offset = self.details_y + 15
        
        # Item icon and name
        icon_surface = self.font_title.render(item_data.icon, True, self.text_color)
        self.screen.blit(icon_surface, (self.details_x + 15, y_offset))
        
        name_surface = self.font_normal.render(item_data.name, True, self.text_color)
        self.screen.blit(name_surface, (self.details_x + 55, y_offset + 5))
        y_offset += 35
        
        # Rarity
        rarity_color = self.rarity_colors.get(item_data.rarity, (150, 150, 150))
        rarity_surface = self.font_small.render(f"Rarity: {item_data.rarity.value.title()}", True, rarity_color)
        self.screen.blit(rarity_surface, (self.details_x + 15, y_offset))
        y_offset += 20
        
        # Type
        type_surface = self.font_small.render(f"Type: {item_data.item_type.value.title()}", True, self.text_color)
        self.screen.blit(type_surface, (self.details_x + 15, y_offset))
        y_offset += 20
        
        # Quantity and quality
        qty_surface = self.font_small.render(f"Quantity: {inv_item.quantity}", True, self.text_color)
        self.screen.blit(qty_surface, (self.details_x + 15, y_offset))
        y_offset += 20
        
        if inv_item.quality > 1:
            quality_surface = self.font_small.render(f"Quality: {inv_item.quality} ⭐", True, (255, 215, 0))
            self.screen.blit(quality_surface, (self.details_x + 15, y_offset))
            y_offset += 20
        
        # Value
        total_value = self.inventory.get_item_value(self.selected_item, inv_item.quality) * inv_item.quantity
        value_surface = self.font_small.render(f"Total Value: {total_value}g", True, self.accent_color)
        self.screen.blit(value_surface, (self.details_x + 15, y_offset))
        y_offset += 25
        
        # Description
        desc_lines = self._wrap_text(item_data.description, self.details_width - 30, self.font_small)
        for line in desc_lines:
            desc_surface = self.font_small.render(line, True, self.text_color)
            self.screen.blit(desc_surface, (self.details_x + 15, y_offset))
            y_offset += 18
    
    def _draw_context_menu(self):
        """Draw context menu"""
        menu_x, menu_y = self.context_menu_pos
        menu_width = 120
        menu_height = 80
        
        menu_rect = pygame.Rect(menu_x, menu_y, menu_width, menu_height)
        pygame.draw.rect(self.screen, self.bg_color, menu_rect, border_radius=5)
        pygame.draw.rect(self.screen, self.border_color, menu_rect, 2, border_radius=5)
        
        options = ["Use/Consume", "Drop", "Sell"]
        for i, option in enumerate(options):
            option_y = menu_y + i * 20 + 10
            option_surface = self.font_small.render(option, True, self.text_color)
            self.screen.blit(option_surface, (menu_x + 10, option_y))
    
    def _draw_controls(self):
        """Draw control instructions"""
        controls = [
            "ESC/I: Close | 1-4: Sort | Mouse Wheel: Scroll",
            "Left Click: Select | Right Click: Context Menu"
        ]
        
        y_offset = self.panel_y + self.panel_height - 40
        for control in controls:
            control_surface = self.font_small.render(control, True, self.text_color)
            self.screen.blit(control_surface, (self.panel_x + 20, y_offset))
            y_offset += 18
    
    def _wrap_text(self, text: str, max_width: int, font: pygame.font.Font) -> List[str]:
        """Wrap text to fit within max_width"""
        words = text.split(' ')
        lines = []
        current_line = ""
        
        for word in words:
            test_line = current_line + (" " if current_line else "") + word
            if font.size(test_line)[0] <= max_width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word
        
        if current_line:
            lines.append(current_line)
        
        return lines
    
    def _draw_hover_tooltip(self):
        """Draw detailed hover tooltip for the currently hovered item"""
        if not self.hovered_item:
            return
        
        item_data = self.inventory.get_item_data(self.hovered_item)
        inv_item = self.inventory.items.get(self.hovered_item)
        
        if not item_data or not inv_item:
            return
        
        # Calculate tooltip content and size
        tooltip_lines = []
        
        # Title (name with rarity color)
        title = f"{item_data.icon} {item_data.name}"
        if inv_item.quality > 1:
            title += f" {'⭐' * inv_item.quality}"
        tooltip_lines.append((title, self.rarity_colors.get(item_data.rarity, (255, 255, 255)), self.font_normal, True))
        
        # Type and rarity
        tooltip_lines.append((f"Type: {item_data.item_type.value.title()}", (200, 200, 200), self.font_small, False))
        tooltip_lines.append((f"Rarity: {item_data.rarity.value.title()}", self.rarity_colors.get(item_data.rarity, (150, 150, 150)), self.font_small, False))
        
        # Quantity and quality
        tooltip_lines.append((f"Quantity: {inv_item.quantity}", (255, 255, 255), self.font_small, False))
        if inv_item.quality > 1:
            tooltip_lines.append((f"Quality: {inv_item.quality} Star{'s' if inv_item.quality > 1 else ''}", (255, 215, 0), self.font_small, False))
        
        # Value calculation
        single_value = self.inventory.get_item_value(self.hovered_item, inv_item.quality)
        total_value = single_value * inv_item.quantity
        if inv_item.quantity > 1:
            tooltip_lines.append((f"Value: {single_value}g each, {total_value}g total", (100, 255, 100), self.font_small, False))
        else:
            tooltip_lines.append((f"Value: {total_value}g", (100, 255, 100), self.font_small, False))
        
        # Stack info
        if item_data.max_stack > 1:
            tooltip_lines.append((f"Max Stack: {item_data.max_stack}", (180, 180, 180), self.font_small, False))
        
        # Special item stats based on type
        self._add_item_type_stats(tooltip_lines, item_data, inv_item)
        
        # Separator
        tooltip_lines.append(("─" * 30, (100, 100, 100), self.font_small, False))
        
        # Description (wrapped)
        desc_lines = self._wrap_text(item_data.description, 250, self.font_small)
        for line in desc_lines:
            tooltip_lines.append((line, (220, 220, 220), self.font_small, False))
        
        # Usage hints
        usage_hint = self._get_usage_hint(item_data)
        if usage_hint:
            tooltip_lines.append(("", (0, 0, 0), self.font_small, False))  # Spacer
            tooltip_lines.append((usage_hint, (150, 200, 255), self.font_small, False))
        
        # Calculate tooltip dimensions
        tooltip_width = 280
        line_height = 16
        title_height = 20
        tooltip_height = len(tooltip_lines) * line_height + title_height + 20  # padding
        
        # Position tooltip near mouse but keep on screen
        mouse_x, mouse_y = self.mouse_pos
        tooltip_x = mouse_x + 15
        tooltip_y = mouse_y - tooltip_height // 2
        
        # Keep tooltip on screen
        if tooltip_x + tooltip_width > SCREEN_WIDTH:
            tooltip_x = mouse_x - tooltip_width - 15
        if tooltip_y < 0:
            tooltip_y = 0
        if tooltip_y + tooltip_height > SCREEN_HEIGHT:
            tooltip_y = SCREEN_HEIGHT - tooltip_height
        
        # Draw tooltip background
        tooltip_rect = pygame.Rect(tooltip_x, tooltip_y, tooltip_width, tooltip_height)
        pygame.draw.rect(self.screen, (20, 25, 35, 250), tooltip_rect, border_radius=8)
        pygame.draw.rect(self.screen, self.rarity_colors.get(item_data.rarity, (150, 150, 150)), tooltip_rect, 2, border_radius=8)
        
        # Draw tooltip content
        y_offset = tooltip_y + 10
        for i, (text, color, font, is_title) in enumerate(tooltip_lines):
            if not text:  # Skip empty spacer lines
                y_offset += line_height // 2
                continue
                
            text_surface = font.render(text, True, color)
            self.screen.blit(text_surface, (tooltip_x + 10, y_offset))
            
            if is_title:
                y_offset += title_height
            else:
                y_offset += line_height
    
    def _add_item_type_stats(self, tooltip_lines: List, item_data: ItemData, inv_item: InventoryItem):
        """Add type-specific stats to tooltip"""
        item_type = item_data.item_type
        
        if item_type == ItemType.TOOL:
            # Tool durability and efficiency (simulated)
            efficiency = inv_item.quality * 20  # Higher quality = more efficient
            tooltip_lines.append((f"Efficiency: {efficiency}%", (100, 200, 255), self.font_small, False))
            tooltip_lines.append(("Right-click to equip", (200, 200, 100), self.font_small, False))
            
        elif item_type == ItemType.FOOD:
            # Food stats: health/energy restoration
            health_restore = item_data.base_value // 2
            energy_restore = item_data.base_value // 3
            quality_bonus = (inv_item.quality - 1) * 10
            
            tooltip_lines.append((f"Health: +{health_restore + quality_bonus}", (255, 100, 100), self.font_small, False))
            tooltip_lines.append((f"Energy: +{energy_restore + quality_bonus}", (100, 255, 100), self.font_small, False))
            
        elif item_type == ItemType.SEED:
            # Seed growing time and season
            grow_times = {
                "parsnip_seeds": "4 days",
                "potato_seeds": "6 days", 
                "cauliflower_seeds": "12 days",
                "tomato_seeds": "11 days (regrows 4 days)"
            }
            grow_time = grow_times.get(item_data.item_id, "Unknown")
            tooltip_lines.append((f"Grow Time: {grow_time}", (100, 255, 100), self.font_small, False))
            
        elif item_type == ItemType.FISH:
            # Fish stats: size and location hint
            size_categories = {
                ItemRarity.COMMON: "Small",
                ItemRarity.UNCOMMON: "Medium", 
                ItemRarity.RARE: "Large",
                ItemRarity.EPIC: "Huge",
                ItemRarity.LEGENDARY: "Massive"
            }
            size = size_categories.get(item_data.rarity, "Unknown")
            tooltip_lines.append((f"Size: {size}", (100, 200, 255), self.font_small, False))
            
            if item_data.rarity in [ItemRarity.RARE, ItemRarity.EPIC, ItemRarity.LEGENDARY]:
                tooltip_lines.append(("Rare catch! 🎣", (255, 215, 0), self.font_small, False))
                
        elif item_type == ItemType.MINERAL:
            # Mineral processing info
            if "ore" in item_data.item_id:
                tooltip_lines.append(("Can be smelted", (255, 150, 100), self.font_small, False))
            elif item_data.rarity in [ItemRarity.RARE, ItemRarity.EPIC, ItemRarity.LEGENDARY]:
                tooltip_lines.append(("Precious gemstone! 💎", (255, 215, 0), self.font_small, False))
                
        elif item_type == ItemType.CRAFTED:
            # Crafted item functionality
            if "machine" in item_data.item_id:
                tooltip_lines.append(("Processing machine", (200, 150, 255), self.font_small, False))
            elif item_data.item_id == "chest":
                tooltip_lines.append(("Storage: 36 slots", (150, 200, 255), self.font_small, False))
            elif item_data.item_id == "scarecrow":
                tooltip_lines.append(("Range: 8 tiles", (100, 255, 100), self.font_small, False))
    
    def _get_usage_hint(self, item_data: ItemData) -> str:
        """Get usage hint for item type"""
        usage_hints = {
            ItemType.TOOL: "Equip to use for gathering",
            ItemType.FOOD: "Right-click to consume", 
            ItemType.SEED: "Plant in tilled soil",
            ItemType.CROP: "Sell or use in recipes",
            ItemType.FISH: "Sell or cook in recipes",
            ItemType.MINERAL: "Sell or use for crafting",
            ItemType.RESOURCE: "Use for building and crafting",
            ItemType.CRAFTED: "Place to use functionality",
            ItemType.FURNITURE: "Place to decorate",
            ItemType.ARTIFACT: "Donate to museum or sell"
        }
        
        return usage_hints.get(item_data.item_type, "")