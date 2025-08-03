import pygame
from typing import Dict, List, Optional, Any
from src.core.constants import *
from src.world.mining_shop import MiningShop
from src.systems.inventory_system import InventorySystem

class MiningShopUI:
    """
    UI for the mining shop interface - buying and selling items
    """
    
    def __init__(self, screen, mining_shop: MiningShop, player_inventory: InventorySystem, player=None):
        self.screen = screen
        self.mining_shop = mining_shop
        self.player_inventory = player_inventory
        self.player = player
        
        # UI state
        self.visible = False
        self.current_tab = "buy"  # "buy" or "sell"
        self.selected_item = None
        self.quantity_to_trade = 1
        
        # UI layout
        self.panel_width = 700
        self.panel_height = 500
        self.panel_x = (SCREEN_WIDTH - self.panel_width) // 2
        self.panel_y = (SCREEN_HEIGHT - self.panel_height) // 2
        
        # Fonts
        self.font_title = pygame.font.Font(None, 28)
        self.font_normal = pygame.font.Font(None, 20)
        self.font_small = pygame.font.Font(None, 16)
        self.font_tiny = pygame.font.Font(None, 14)
        
        # Colors
        self.bg_color = (40, 45, 55, 240)
        self.tab_active_color = (70, 80, 100)
        self.tab_inactive_color = (50, 55, 65)
        self.item_bg_color = (60, 65, 75)
        self.item_hover_color = (80, 90, 110)
        self.item_selected_color = (100, 120, 150)
        self.text_color = (255, 255, 255)
        self.accent_color = (100, 150, 200)
        self.gold_color = (255, 215, 0)
        self.success_color = (100, 255, 100)
        self.error_color = (255, 100, 100)
        
        # Scrolling
        self.scroll_offset = 0
        self.max_scroll = 0
        self.items_per_page = 8
        
        # Trade confirmation
        self.show_confirmation = False
        self.confirmation_message = ""
        self.pending_trade = None
    
    def show(self):
        """Show the mining shop UI"""
        self.visible = True
        self.selected_item = None
        self.quantity_to_trade = 1
        self.scroll_offset = 0
        self.show_confirmation = False
    
    def hide(self):
        """Hide the mining shop UI"""
        self.visible = False
        self.show_confirmation = False
    
    def handle_event(self, event) -> bool:
        """Handle UI events"""
        if not self.visible:
            return False
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if self.show_confirmation:
                    self.show_confirmation = False
                else:
                    self.hide()
                return True
            elif event.key == pygame.K_TAB:
                self.current_tab = "sell" if self.current_tab == "buy" else "buy"
                self.selected_item = None
                self.scroll_offset = 0
                return True
        
        elif event.type == pygame.MOUSEWHEEL:
            if self.visible:
                self.scroll_offset = max(0, min(self.max_scroll, self.scroll_offset - event.y * 30))
                return True
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                return self._handle_click(event.pos)
        
        return True
    
    def _handle_click(self, mouse_pos) -> bool:
        """Handle mouse clicks"""
        mouse_x, mouse_y = mouse_pos
        
        # Check if click is within panel
        panel_rect = pygame.Rect(self.panel_x, self.panel_y, self.panel_width, self.panel_height)
        if not panel_rect.collidepoint(mouse_x, mouse_y):
            self.hide()
            return True
        
        # Handle confirmation dialog
        if self.show_confirmation:
            return self._handle_confirmation_click(mouse_x, mouse_y)
        
        # Tab buttons
        buy_tab_rect = pygame.Rect(self.panel_x + 20, self.panel_y + 50, 80, 30)
        sell_tab_rect = pygame.Rect(self.panel_x + 110, self.panel_y + 50, 80, 30)
        
        if buy_tab_rect.collidepoint(mouse_x, mouse_y):
            self.current_tab = "buy"
            self.selected_item = None
            self.scroll_offset = 0
            return True
        elif sell_tab_rect.collidepoint(mouse_x, mouse_y):
            self.current_tab = "sell"
            self.selected_item = None
            self.scroll_offset = 0
            return True
        
        # Item list
        items_start_y = self.panel_y + 90
        item_height = 45
        
        if self.current_tab == "buy":
            items = self.mining_shop.get_shop_items_for_display()
        else:
            items = self.mining_shop.get_buyable_items(self.player_inventory)
        
        for i, item in enumerate(items):
            item_y = items_start_y + i * item_height - self.scroll_offset
            
            if item_y < items_start_y - item_height or item_y > self.panel_y + self.panel_height - 100:
                continue  # Skip items outside visible area
            
            item_rect = pygame.Rect(self.panel_x + 20, item_y, self.panel_width - 300, item_height - 5)
            
            if item_rect.collidepoint(mouse_x, mouse_y):
                self.selected_item = item
                self.quantity_to_trade = 1
                return True
        
        # Quantity controls
        if self.selected_item:
            qty_minus_rect = pygame.Rect(self.panel_x + self.panel_width - 200, self.panel_y + 150, 30, 30)
            qty_plus_rect = pygame.Rect(self.panel_x + self.panel_width - 120, self.panel_y + 150, 30, 30)
            
            if qty_minus_rect.collidepoint(mouse_x, mouse_y):
                self.quantity_to_trade = max(1, self.quantity_to_trade - 1)
                return True
            elif qty_plus_rect.collidepoint(mouse_x, mouse_y):
                max_qty = self._get_max_tradeable_quantity()
                self.quantity_to_trade = min(max_qty, self.quantity_to_trade + 1)
                return True
        
        # Trade button
        if self.selected_item:
            trade_button_rect = pygame.Rect(self.panel_x + self.panel_width - 250, self.panel_y + 220, 200, 40)
            if trade_button_rect.collidepoint(mouse_x, mouse_y):
                self._initiate_trade()
                return True
        
        return True
    
    def _handle_confirmation_click(self, mouse_x: int, mouse_y: int) -> bool:
        """Handle clicks on confirmation dialog"""
        # Confirm button
        confirm_rect = pygame.Rect(self.panel_x + self.panel_width // 2 - 80, self.panel_y + self.panel_height // 2 + 20, 70, 30)
        cancel_rect = pygame.Rect(self.panel_x + self.panel_width // 2 + 10, self.panel_y + self.panel_height // 2 + 20, 70, 30)
        
        if confirm_rect.collidepoint(mouse_x, mouse_y):
            self._execute_trade()
            self.show_confirmation = False
            return True
        elif cancel_rect.collidepoint(mouse_x, mouse_y):
            self.show_confirmation = False
            return True
        
        return True
    
    def _get_max_tradeable_quantity(self) -> int:
        """Get maximum quantity that can be traded"""
        if not self.selected_item:
            return 1
        
        if self.current_tab == "buy":
            # Limited by shop stock and player money
            shop_stock = self.selected_item["stock"]
            player_money = self.player_inventory.money
            item_price = self.selected_item["price"]
            max_affordable = player_money // item_price if item_price > 0 else 0
            return min(shop_stock, max_affordable)
        else:
            # Limited by player inventory
            return self.selected_item["quantity"]
    
    def _initiate_trade(self):
        """Show confirmation dialog for trade"""
        if not self.selected_item:
            return
        
        item_name = self.selected_item["name"]
        quantity = self.quantity_to_trade
        
        if self.current_tab == "buy":
            total_cost = self.selected_item["price"] * quantity
            if self.player_inventory.money < total_cost:
                self.confirmation_message = f"Not enough gold! Need {total_cost}g, have {self.player_inventory.money}g"
                self.show_confirmation = True
                self.pending_trade = None
                return
            
            self.confirmation_message = f"Buy {quantity}x {item_name} for {total_cost}g?"
            self.pending_trade = {
                "type": "buy",
                "item": self.selected_item,
                "quantity": quantity,
                "total_cost": total_cost
            }
        else:
            total_value = self.selected_item["buy_price"] * quantity
            self.confirmation_message = f"Sell {quantity}x {item_name} for {total_value}g?"
            self.pending_trade = {
                "type": "sell",
                "item": self.selected_item,
                "quantity": quantity,
                "total_value": total_value
            }
        
        self.show_confirmation = True
    
    def _execute_trade(self):
        """Execute the confirmed trade"""
        if not self.pending_trade:
            return
        
        trade = self.pending_trade
        success = False
        
        if trade["type"] == "buy":
            # Player buying from shop
            item_id = trade["item"]["id"]
            quantity = trade["quantity"]
            total_cost = trade["total_cost"]
            
            # Check if player can afford and has inventory space
            if (self.player_inventory.money >= total_cost and 
                self.mining_shop.can_sell_to_player(item_id, quantity)):
                
                # Add item to player inventory
                if self.player_inventory.add_item(item_id, quantity):
                    # Deduct money and update shop
                    self.player_inventory.spend_money(total_cost)
                    self.mining_shop.sell_to_player(item_id, quantity)
                    success = True
                    
                    # Show feedback
                    if self.player:
                        self.player.say(f"Bought {quantity}x {trade['item']['name']} for {total_cost}g!")
        
        else:  # sell
            # Player selling to shop
            item_id = trade["item"]["id"]
            quantity = trade["quantity"]
            total_value = trade["total_value"]
            
            # Get item data for buy price calculation
            item_data = self.player_inventory.get_item_data(item_id)
            if item_data and self.player_inventory.has_item(item_id, quantity):
                
                # Remove item from player inventory
                if self.player_inventory.remove_item(item_id, quantity):
                    # Pay player and update shop money
                    payment = self.mining_shop.buy_from_player(item_id, item_data.base_value, quantity, trade["item"]["quality"])
                    self.player_inventory.add_money(payment)
                    success = True
                    
                    # Show feedback
                    if self.player:
                        self.player.say(f"Sold {quantity}x {trade['item']['name']} for {payment}g!")
        
        if success:
            # Reset selection and scroll
            self.selected_item = None
            self.quantity_to_trade = 1
            self.scroll_offset = 0
        
        self.pending_trade = None
    
    def draw(self):
        """Draw the mining shop UI"""
        if not self.visible:
            return
        
        # Main panel background
        panel_surface = pygame.Surface((self.panel_width, self.panel_height), pygame.SRCALPHA)
        panel_surface.fill(self.bg_color)
        pygame.draw.rect(panel_surface, (100, 110, 130), (0, 0, self.panel_width, self.panel_height), 3, border_radius=12)
        self.screen.blit(panel_surface, (self.panel_x, self.panel_y))
        
        # Shop title
        title_text = f"{self.mining_shop.name} - {self.mining_shop.shopkeeper_name}"
        title_surface = self.font_title.render(title_text, True, self.text_color)
        self.screen.blit(title_surface, (self.panel_x + 20, self.panel_y + 15))
        
        # Player money display
        money_text = f"Gold: {self.player_inventory.money}g"
        money_surface = self.font_normal.render(money_text, True, self.gold_color)
        money_rect = money_surface.get_rect()
        money_rect.topright = (self.panel_x + self.panel_width - 20, self.panel_y + 15)
        self.screen.blit(money_surface, money_rect)
        
        # Tab buttons
        self._draw_tabs()
        
        # Item list
        self._draw_item_list()
        
        # Item details panel
        if self.selected_item:
            self._draw_item_details()
        
        # Confirmation dialog
        if self.show_confirmation:
            self._draw_confirmation_dialog()
    
    def _draw_tabs(self):
        """Draw the buy/sell tabs"""
        buy_tab_rect = pygame.Rect(self.panel_x + 20, self.panel_y + 50, 80, 30)
        sell_tab_rect = pygame.Rect(self.panel_x + 110, self.panel_y + 50, 80, 30)
        
        # Buy tab
        buy_color = self.tab_active_color if self.current_tab == "buy" else self.tab_inactive_color
        pygame.draw.rect(self.screen, buy_color, buy_tab_rect, border_radius=5)
        pygame.draw.rect(self.screen, (150, 150, 150), buy_tab_rect, 2, border_radius=5)
        
        buy_text = self.font_normal.render("Buy", True, self.text_color)
        buy_text_rect = buy_text.get_rect(center=buy_tab_rect.center)
        self.screen.blit(buy_text, buy_text_rect)
        
        # Sell tab
        sell_color = self.tab_active_color if self.current_tab == "sell" else self.tab_inactive_color
        pygame.draw.rect(self.screen, sell_color, sell_tab_rect, border_radius=5)
        pygame.draw.rect(self.screen, (150, 150, 150), sell_tab_rect, 2, border_radius=5)
        
        sell_text = self.font_normal.render("Sell", True, self.text_color)
        sell_text_rect = sell_text.get_rect(center=sell_tab_rect.center)
        self.screen.blit(sell_text, sell_text_rect)
    
    def _draw_item_list(self):
        """Draw the list of items"""
        items_start_y = self.panel_y + 90
        item_height = 45
        list_width = self.panel_width - 300
        
        # Get items based on current tab
        if self.current_tab == "buy":
            items = self.mining_shop.get_shop_items_for_display()
        else:
            items = self.mining_shop.get_buyable_items(self.player_inventory)
        
        # Calculate scroll limits
        total_height = len(items) * item_height
        visible_height = self.panel_height - 200
        self.max_scroll = max(0, total_height - visible_height)
        
        # Scroll area background
        scroll_rect = pygame.Rect(self.panel_x + 20, items_start_y, list_width, visible_height)
        pygame.draw.rect(self.screen, (30, 35, 45), scroll_rect, border_radius=5)
        
        # Draw items
        for i, item in enumerate(items):
            item_y = items_start_y + i * item_height - self.scroll_offset
            
            # Skip items outside visible area
            if item_y < items_start_y - item_height or item_y > items_start_y + visible_height:
                continue
            
            # Item background
            item_rect = pygame.Rect(self.panel_x + 25, item_y + 2, list_width - 10, item_height - 5)
            
            # Highlight selected item
            if self.selected_item and item["id"] == self.selected_item["id"]:
                item_color = self.item_selected_color
            else:
                item_color = self.item_bg_color
            
            pygame.draw.rect(self.screen, item_color, item_rect, border_radius=5)
            
            # Item name
            name_surface = self.font_normal.render(item["name"], True, self.text_color)
            self.screen.blit(name_surface, (item_rect.x + 10, item_rect.y + 5))
            
            # Price/value info
            if self.current_tab == "buy":
                price_text = f"{item['price']}g"
                stock_text = f"Stock: {item['stock']}"
                
                price_surface = self.font_small.render(price_text, True, self.gold_color)
                stock_surface = self.font_tiny.render(stock_text, True, (180, 180, 180))
                
                price_rect = price_surface.get_rect()
                price_rect.topright = (item_rect.right - 10, item_rect.y + 5)
                self.screen.blit(price_surface, price_rect)
                
                stock_rect = stock_surface.get_rect()
                stock_rect.topright = (item_rect.right - 10, item_rect.y + 25)
                self.screen.blit(stock_surface, stock_rect)
                
            else:  # sell tab
                price_text = f"{item['buy_price']}g each"
                qty_text = f"Have: {item['quantity']}"
                
                price_surface = self.font_small.render(price_text, True, self.success_color)
                qty_surface = self.font_tiny.render(qty_text, True, (180, 180, 180))
                
                price_rect = price_surface.get_rect()
                price_rect.topright = (item_rect.right - 10, item_rect.y + 5)
                self.screen.blit(price_surface, price_rect)
                
                qty_rect = qty_surface.get_rect()
                qty_rect.topright = (item_rect.right - 10, item_rect.y + 25)
                self.screen.blit(qty_surface, qty_rect)
            
            # Special item indicator
            if item.get("is_special", False):
                special_surface = self.font_tiny.render("⭐ SPECIAL", True, self.gold_color)
                self.screen.blit(special_surface, (item_rect.x + 10, item_rect.bottom - 15))
        
        # Scroll indicator
        if self.max_scroll > 0:
            scroll_bar_height = max(20, int(visible_height * visible_height / total_height))
            scroll_bar_y = items_start_y + int(self.scroll_offset * (visible_height - scroll_bar_height) / self.max_scroll)
            
            scroll_bar_rect = pygame.Rect(self.panel_x + list_width + 15, scroll_bar_y, 8, scroll_bar_height)
            pygame.draw.rect(self.screen, (150, 150, 150), scroll_bar_rect, border_radius=4)
    
    def _draw_item_details(self):
        """Draw selected item details and trade controls"""
        details_x = self.panel_x + self.panel_width - 250
        details_y = self.panel_y + 90
        details_width = 230
        
        # Details background
        details_rect = pygame.Rect(details_x, details_y, details_width, 200)
        pygame.draw.rect(self.screen, (50, 55, 65), details_rect, border_radius=8)
        pygame.draw.rect(self.screen, (100, 110, 130), details_rect, 2, border_radius=8)
        
        # Item name
        name_surface = self.font_normal.render(self.selected_item["name"], True, self.text_color)
        self.screen.blit(name_surface, (details_x + 10, details_y + 10))
        
        # Description
        desc_text = self.selected_item.get("description", "No description available")
        desc_lines = self._wrap_text(desc_text, details_width - 20, self.font_small)
        
        y_offset = details_y + 35
        for line in desc_lines:
            line_surface = self.font_small.render(line, True, (200, 200, 200))
            self.screen.blit(line_surface, (details_x + 10, y_offset))
            y_offset += 18
        
        # Quantity controls
        qty_y = details_y + 120
        qty_label = self.font_small.render("Quantity:", True, self.text_color)
        self.screen.blit(qty_label, (details_x + 10, qty_y))
        
        # Minus button
        minus_rect = pygame.Rect(details_x + 10, qty_y + 20, 30, 30)
        pygame.draw.rect(self.screen, (80, 90, 110), minus_rect, border_radius=5)
        minus_text = self.font_normal.render("-", True, self.text_color)
        minus_text_rect = minus_text.get_rect(center=minus_rect.center)
        self.screen.blit(minus_text, minus_text_rect)
        
        # Quantity display
        qty_rect = pygame.Rect(details_x + 50, qty_y + 20, 60, 30)
        pygame.draw.rect(self.screen, (60, 65, 75), qty_rect, border_radius=5)
        qty_text = self.font_normal.render(str(self.quantity_to_trade), True, self.text_color)
        qty_text_rect = qty_text.get_rect(center=qty_rect.center)
        self.screen.blit(qty_text, qty_text_rect)
        
        # Plus button
        plus_rect = pygame.Rect(details_x + 120, qty_y + 20, 30, 30)
        pygame.draw.rect(self.screen, (80, 90, 110), plus_rect, border_radius=5)
        plus_text = self.font_normal.render("+", True, self.text_color)
        plus_text_rect = plus_text.get_rect(center=plus_rect.center)
        self.screen.blit(plus_text, plus_text_rect)
        
        # Max quantity info
        max_qty = self._get_max_tradeable_quantity()
        max_text = f"Max: {max_qty}"
        max_surface = self.font_tiny.render(max_text, True, (150, 150, 150))
        self.screen.blit(max_surface, (details_x + 160, qty_y + 30))
        
        # Total cost/value
        total_y = qty_y + 60
        if self.current_tab == "buy":
            total_cost = self.selected_item["price"] * self.quantity_to_trade
            total_text = f"Total: {total_cost}g"
            color = self.error_color if self.player_inventory.money < total_cost else self.gold_color
        else:
            total_value = self.selected_item["buy_price"] * self.quantity_to_trade
            total_text = f"Total: {total_value}g"
            color = self.success_color
        
        total_surface = self.font_normal.render(total_text, True, color)
        self.screen.blit(total_surface, (details_x + 10, total_y))
        
        # Trade button
        button_y = total_y + 30
        button_rect = pygame.Rect(details_x + 10, button_y, details_width - 20, 35)
        
        button_text = "Buy" if self.current_tab == "buy" else "Sell"
        can_trade = (self.quantity_to_trade <= max_qty and 
                    (self.current_tab == "sell" or self.player_inventory.money >= self.selected_item["price"] * self.quantity_to_trade))
        
        button_color = self.accent_color if can_trade else (100, 100, 100)
        pygame.draw.rect(self.screen, button_color, button_rect, border_radius=8)
        
        button_text_surface = self.font_normal.render(f"{button_text} ({self.quantity_to_trade})", True, self.text_color)
        button_text_rect = button_text_surface.get_rect(center=button_rect.center)
        self.screen.blit(button_text_surface, button_text_rect)
    
    def _draw_confirmation_dialog(self):
        """Draw trade confirmation dialog"""
        # Overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        self.screen.blit(overlay, (0, 0))
        
        # Dialog box
        dialog_width = 400
        dialog_height = 150
        dialog_x = (SCREEN_WIDTH - dialog_width) // 2
        dialog_y = (SCREEN_HEIGHT - dialog_height) // 2
        
        dialog_rect = pygame.Rect(dialog_x, dialog_y, dialog_width, dialog_height)
        pygame.draw.rect(self.screen, (60, 65, 75), dialog_rect, border_radius=12)
        pygame.draw.rect(self.screen, (150, 150, 150), dialog_rect, 3, border_radius=12)
        
        # Message
        message_lines = self._wrap_text(self.confirmation_message, dialog_width - 40, self.font_normal)
        y_offset = dialog_y + 20
        
        for line in message_lines:
            line_surface = self.font_normal.render(line, True, self.text_color)
            line_rect = line_surface.get_rect(centerx=dialog_x + dialog_width // 2)
            line_rect.y = y_offset
            self.screen.blit(line_surface, line_rect)
            y_offset += 25
        
        # Buttons
        if self.pending_trade:  # Only show confirm/cancel for actual trades
            confirm_rect = pygame.Rect(dialog_x + dialog_width // 2 - 80, dialog_y + dialog_height - 50, 70, 30)
            cancel_rect = pygame.Rect(dialog_x + dialog_width // 2 + 10, dialog_y + dialog_height - 50, 70, 30)
            
            # Confirm button
            pygame.draw.rect(self.screen, self.success_color, confirm_rect, border_radius=5)
            confirm_text = self.font_small.render("Confirm", True, self.text_color)
            confirm_text_rect = confirm_text.get_rect(center=confirm_rect.center)
            self.screen.blit(confirm_text, confirm_text_rect)
            
            # Cancel button
            pygame.draw.rect(self.screen, self.error_color, cancel_rect, border_radius=5)
            cancel_text = self.font_small.render("Cancel", True, self.text_color)
            cancel_text_rect = cancel_text.get_rect(center=cancel_rect.center)
            self.screen.blit(cancel_text, cancel_text_rect)
        else:
            # Just OK button for error messages
            ok_rect = pygame.Rect(dialog_x + dialog_width // 2 - 35, dialog_y + dialog_height - 50, 70, 30)
            pygame.draw.rect(self.screen, self.accent_color, ok_rect, border_radius=5)
            ok_text = self.font_small.render("OK", True, self.text_color)
            ok_text_rect = ok_text.get_rect(center=ok_rect.center)
            self.screen.blit(ok_text, ok_text_rect)
    
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
                else:
                    lines.append(word)
        
        if current_line:
            lines.append(current_line)
        
        return lines