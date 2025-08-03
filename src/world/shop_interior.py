import pygame
from typing import Dict, List, Optional, Tuple
from src.world.shop_system import ShopSystem, Shop, ShopType
from src.systems.inventory_system import InventorySystem
from src.core.constants import *

class ShopInterior:
    """
    Shop interior system that handles entering shops and shop UI
    """
    
    def __init__(self, screen, inventory_system: InventorySystem, shop_system: ShopSystem):
        self.screen = screen
        self.inventory = inventory_system
        self.shop_system = shop_system
        
        # Current shop state
        self.current_shop: Optional[Shop] = None
        self.is_in_shop = False
        self.shop_ui_visible = False
        
        # Fonts
        self.font_title = pygame.font.Font(None, 32)
        self.font_normal = pygame.font.Font(None, 24)
        self.font_small = pygame.font.Font(None, 18)
        self.font_tiny = pygame.font.Font(None, 14)
        
        # Colors
        self.bg_color = (40, 35, 30)
        self.panel_color = (60, 55, 50)
        self.item_color = (80, 75, 70)
        self.hover_color = (100, 95, 90)
        self.text_color = (255, 255, 255)
        self.accent_color = (255, 215, 0)
        self.success_color = (100, 255, 100)
        self.error_color = (255, 100, 100)
        
        # Layout
        self.panel_width = 800
        self.panel_height = 600
        self.panel_x = (SCREEN_WIDTH - self.panel_width) // 2
        self.panel_y = (SCREEN_HEIGHT - self.panel_height) // 2
        
        # Shop UI state
        self.selected_category = "all"
        self.selected_item = None
        self.hover_item = None
        self.scroll_offset = 0
        self.purchase_quantity = 1
        
        # Shop categories
        self.categories = {
            "all": "All Items",
            "tools": "Tools",
            "materials": "Materials",
            "gems": "Gems",
            "equipment": "Equipment",
            "machines": "Machines"
        }
    
    def enter_shop(self, shop_type: str) -> bool:
        """Enter a shop"""
        shop = self.shop_system.get_shop(shop_type)
        if shop:
            self.current_shop = shop
            self.is_in_shop = True
            self.shop_ui_visible = True
            self.selected_category = "all"
            self.selected_item = None
            self.scroll_offset = 0
            self.purchase_quantity = 1
            return True
        return False
    
    def exit_shop(self):
        """Exit the current shop"""
        self.current_shop = None
        self.is_in_shop = False
        self.shop_ui_visible = False
        self.selected_item = None
    
    def handle_event(self, event) -> bool:
        """Handle shop UI events"""
        if not self.is_in_shop or not self.shop_ui_visible:
            return False
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.exit_shop()
                return True
            elif event.key == pygame.K_MINUS and self.purchase_quantity > 1:
                self.purchase_quantity -= 1
                return True
            elif event.key == pygame.K_EQUALS and self.purchase_quantity < 99:
                self.purchase_quantity += 1
                return True
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = event.pos
            
            if event.button == 1:  # Left click
                # Check if clicking outside panel to close
                panel_rect = pygame.Rect(self.panel_x, self.panel_y, self.panel_width, self.panel_height)
                if not panel_rect.collidepoint(mouse_x, mouse_y):
                    self.exit_shop()
                    return True
                
                # Check category buttons
                category_clicked = self._check_category_click(mouse_x, mouse_y)
                if category_clicked:
                    self.selected_category = category_clicked
                    self.scroll_offset = 0
                    return True
                
                # Check item selection
                item_clicked = self._check_item_click(mouse_x, mouse_y)
                if item_clicked:
                    self.selected_item = item_clicked
                    return True
                
                # Check purchase button
                if self._check_purchase_button_click(mouse_x, mouse_y):
                    self._attempt_purchase()
                    return True
                
                # Check sell button
                if self._check_sell_button_click(mouse_x, mouse_y):
                    self._attempt_sell()
                    return True
                
                # Check close button
                if self._check_close_button_click(mouse_x, mouse_y):
                    self.exit_shop()
                    return True
        
        elif event.type == pygame.MOUSEMOTION:
            mouse_x, mouse_y = event.pos
            self.hover_item = self._get_item_at_pos(mouse_x, mouse_y)
        
        elif event.type == pygame.MOUSEWHEEL:
            # Scroll through items
            self.scroll_offset -= event.y * 30
            self.scroll_offset = max(0, self.scroll_offset)
        
        return True
    
    def _check_category_click(self, mouse_x: int, mouse_y: int) -> Optional[str]:
        """Check if a category button was clicked"""
        cat_y = self.panel_y + 60
        cat_width = 100
        cat_height = 30
        
        for i, (cat_key, cat_name) in enumerate(self.categories.items()):
            cat_x = self.panel_x + 20 + i * (cat_width + 10)
            cat_rect = pygame.Rect(cat_x, cat_y, cat_width, cat_height)
            
            if cat_rect.collidepoint(mouse_x, mouse_y):
                return cat_key
        
        return None
    
    def _check_item_click(self, mouse_x: int, mouse_y: int) -> Optional[str]:
        """Check if an item was clicked"""
        return self._get_item_at_pos(mouse_x, mouse_y)
    
    def _get_item_at_pos(self, mouse_x: int, mouse_y: int) -> Optional[str]:
        """Get item at mouse position"""
        if not self.current_shop:
            return None
        
        items = self._get_filtered_items()
        item_height = 60
        list_start_y = self.panel_y + 120
        
        for i, item in enumerate(items):
            item_y = list_start_y + i * item_height - self.scroll_offset
            item_rect = pygame.Rect(self.panel_x + 20, item_y, self.panel_width // 2 - 40, item_height - 5)
            
            if item_rect.collidepoint(mouse_x, mouse_y):
                return item.item_id
        
        return None
    
    def _check_purchase_button_click(self, mouse_x: int, mouse_y: int) -> bool:
        """Check if purchase button was clicked"""
        if not self.selected_item:
            return False
        
        button_rect = self._get_purchase_button_rect()
        return button_rect.collidepoint(mouse_x, mouse_y)
    
    def _check_sell_button_click(self, mouse_x: int, mouse_y: int) -> bool:
        """Check if sell button was clicked"""
        if not self.selected_item:
            return False
        
        button_rect = self._get_sell_button_rect()
        return button_rect.collidepoint(mouse_x, mouse_y)
    
    def _check_close_button_click(self, mouse_x: int, mouse_y: int) -> bool:
        """Check if close button was clicked"""
        close_rect = self._get_close_button_rect()
        return close_rect.collidepoint(mouse_x, mouse_y)
    
    def _get_purchase_button_rect(self) -> pygame.Rect:
        """Get purchase button rectangle"""
        return pygame.Rect(self.panel_x + self.panel_width // 2 + 50, self.panel_y + 400, 120, 35)
    
    def _get_sell_button_rect(self) -> pygame.Rect:
        """Get sell button rectangle"""
        return pygame.Rect(self.panel_x + self.panel_width // 2 + 190, self.panel_y + 400, 120, 35)
    
    def _get_close_button_rect(self) -> pygame.Rect:
        """Get close button rectangle"""
        return pygame.Rect(self.panel_x + self.panel_width - 35, self.panel_y + 10, 25, 25)
    
    def _get_filtered_items(self) -> List:
        """Get items filtered by current category"""
        if not self.current_shop:
            return []
        
        all_items = self.current_shop.get_shop_items(player_level=10)  # TODO: Use actual player level
        
        if self.selected_category == "all":
            return all_items
        
        return [item for item in all_items if hasattr(item, 'category') and item.category == self.selected_category]
    
    def _attempt_purchase(self):
        """Attempt to purchase selected item"""
        if not self.current_shop or not self.selected_item:
            return
        
        success, message = self.current_shop.purchase_item(
            self.selected_item, 
            self.purchase_quantity, 
            self.inventory
        )
        
        if success:
            print(f"Purchase successful: {message}")
        else:
            print(f"Purchase failed: {message}")
    
    def _attempt_sell(self):
        """Attempt to sell selected item"""
        if not self.current_shop or not self.selected_item:
            return
        
        # Check if player has the item in inventory
        if not self.inventory.has_item(self.selected_item, self.purchase_quantity):
            print("You don't have enough of this item to sell")
            return
        
        success, message = self.current_shop.sell_item(
            self.selected_item,
            self.purchase_quantity,
            self.inventory
        )
        
        if success:
            print(f"Sale successful: {message}")
        else:
            print(f"Sale failed: {message}")
    
    def draw(self):
        """Draw the shop interior UI"""
        if not self.is_in_shop or not self.shop_ui_visible or not self.current_shop:
            return
        
        # Draw background overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))
        
        # Draw main panel
        panel_rect = pygame.Rect(self.panel_x, self.panel_y, self.panel_width, self.panel_height)
        pygame.draw.rect(self.screen, self.bg_color, panel_rect, border_radius=10)
        pygame.draw.rect(self.screen, self.accent_color, panel_rect, 3, border_radius=10)
        
        # Draw shop title
        title_surface = self.font_title.render(self.current_shop.name, True, self.accent_color)
        self.screen.blit(title_surface, (self.panel_x + 20, self.panel_y + 15))
        
        # Draw shop description
        desc_surface = self.font_small.render(self.current_shop.description, True, self.text_color)
        self.screen.blit(desc_surface, (self.panel_x + 20, self.panel_y + 45))
        
        # Draw close button
        close_rect = self._get_close_button_rect()
        pygame.draw.rect(self.screen, self.error_color, close_rect, border_radius=3)
        close_text = self.font_small.render("×", True, self.text_color)
        close_text_rect = close_text.get_rect(center=close_rect.center)
        self.screen.blit(close_text, close_text_rect)
        
        # Draw category buttons
        self._draw_categories()
        
        # Draw item list
        self._draw_item_list()
        
        # Draw item details panel
        self._draw_item_details()
        
        # Draw player money
        money_text = f"Money: {self.inventory.money}g"
        money_surface = self.font_normal.render(money_text, True, self.accent_color)
        self.screen.blit(money_surface, (self.panel_x + 20, self.panel_y + self.panel_height - 30))
    
    def _draw_categories(self):
        """Draw category selection buttons"""
        cat_y = self.panel_y + 60
        cat_width = 100
        cat_height = 30
        
        for i, (cat_key, cat_name) in enumerate(self.categories.items()):
            cat_x = self.panel_x + 20 + i * (cat_width + 10)
            cat_rect = pygame.Rect(cat_x, cat_y, cat_width, cat_height)
            
            # Color based on selection
            if cat_key == self.selected_category:
                color = self.accent_color
                text_color = self.bg_color
            else:
                color = self.panel_color
                text_color = self.text_color
            
            pygame.draw.rect(self.screen, color, cat_rect, border_radius=5)
            pygame.draw.rect(self.screen, self.text_color, cat_rect, 2, border_radius=5)
            
            # Draw category text
            cat_text = self.font_tiny.render(cat_name, True, text_color)
            cat_text_rect = cat_text.get_rect(center=cat_rect.center)
            self.screen.blit(cat_text, cat_text_rect)
    
    def _draw_item_list(self):
        """Draw the list of available items"""
        items = self._get_filtered_items()
        item_height = 60
        list_start_y = self.panel_y + 120
        list_rect = pygame.Rect(self.panel_x + 20, list_start_y, self.panel_width // 2 - 40, 350)
        
        # Create clipping area for scrolling
        pygame.draw.rect(self.screen, self.panel_color, list_rect, border_radius=5)
        
        for i, item in enumerate(items):
            item_y = list_start_y + i * item_height - self.scroll_offset
            
            # Skip items outside visible area
            if item_y + item_height < list_start_y or item_y > list_start_y + 350:
                continue
            
            item_rect = pygame.Rect(self.panel_x + 25, item_y + 5, self.panel_width // 2 - 50, item_height - 10)
            
            # Color based on selection and hover
            if item.item_id == self.selected_item:
                color = self.accent_color
            elif item.item_id == self.hover_item:
                color = self.hover_color
            else:
                color = self.item_color
            
            pygame.draw.rect(self.screen, color, item_rect, border_radius=3)
            
            # Draw item info
            item_data = self.inventory.get_item_data(item.item_id)
            if item_data:
                # Item icon
                icon_surface = self.font_normal.render(item_data.icon, True, self.text_color)
                self.screen.blit(icon_surface, (item_rect.x + 10, item_rect.y + 5))
                
                # Item name
                name_surface = self.font_small.render(item_data.name, True, self.text_color)
                self.screen.blit(name_surface, (item_rect.x + 40, item_rect.y + 5))
                
                # Item price
                price = self.current_shop.get_item_price(item.item_id, self.inventory)
                price_surface = self.font_small.render(f"{price}g", True, self.success_color)
                self.screen.blit(price_surface, (item_rect.x + 40, item_rect.y + 25))
                
                # Stock info
                if item.stock != -1:
                    stock_surface = self.font_tiny.render(f"Stock: {item.stock}", True, self.text_color)
                    self.screen.blit(stock_surface, (item_rect.x + 40, item_rect.y + 40))
    
    def _draw_item_details(self):
        """Draw detailed information about selected item"""
        if not self.selected_item:
            return
        
        details_x = self.panel_x + self.panel_width // 2 + 20
        details_y = self.panel_y + 120
        details_width = self.panel_width // 2 - 40
        
        # Background
        details_rect = pygame.Rect(details_x, details_y, details_width, 250)
        pygame.draw.rect(self.screen, self.panel_color, details_rect, border_radius=5)
        
        item_data = self.inventory.get_item_data(self.selected_item)
        if not item_data:
            return
        
        y_offset = details_y + 15
        
        # Item name and icon
        title_text = f"{item_data.icon} {item_data.name}"
        title_surface = self.font_normal.render(title_text, True, self.text_color)
        self.screen.blit(title_surface, (details_x + 15, y_offset))
        y_offset += 30
        
        # Description
        desc_surface = self.font_small.render(item_data.description, True, self.text_color)
        self.screen.blit(desc_surface, (details_x + 15, y_offset))
        y_offset += 25
        
        # Price
        shop_item = self.current_shop.items.get(self.selected_item)
        if shop_item:
            price = self.current_shop.get_item_price(self.selected_item, self.inventory)
            price_surface = self.font_normal.render(f"Price: {price}g", True, self.success_color)
            self.screen.blit(price_surface, (details_x + 15, y_offset))
            y_offset += 25
            
            # Quantity selector
            qty_text = f"Quantity: {self.purchase_quantity}"
            qty_surface = self.font_small.render(qty_text, True, self.text_color)
            self.screen.blit(qty_surface, (details_x + 15, y_offset))
            
            # Quantity controls hint
            hint_surface = self.font_tiny.render("Use +/- keys to adjust quantity", True, (150, 150, 150))
            self.screen.blit(hint_surface, (details_x + 15, y_offset + 20))
            y_offset += 45
            
            # Total cost
            total_cost = price * self.purchase_quantity
            total_surface = self.font_normal.render(f"Total: {total_cost}g", True, self.accent_color)
            self.screen.blit(total_surface, (details_x + 15, y_offset))
        
        # Purchase button
        purchase_rect = self._get_purchase_button_rect()
        can_afford = self.inventory.money >= (price * self.purchase_quantity)
        button_color = self.success_color if can_afford else self.error_color
        
        pygame.draw.rect(self.screen, button_color, purchase_rect, border_radius=5)
        purchase_text = self.font_small.render("Purchase", True, self.text_color)
        purchase_text_rect = purchase_text.get_rect(center=purchase_rect.center)
        self.screen.blit(purchase_text, purchase_text_rect)
        
        # Sell button (if player has the item)
        if self.inventory.has_item(self.selected_item):
            sell_rect = self._get_sell_button_rect()
            sell_price = self.current_shop.get_buyback_price(self.selected_item, self.inventory)
            
            pygame.draw.rect(self.screen, self.accent_color, sell_rect, border_radius=5)
            sell_text = self.font_small.render(f"Sell ({sell_price}g)", True, self.text_color)
            sell_text_rect = sell_text.get_rect(center=sell_rect.center)
            self.screen.blit(sell_text, sell_text_rect)