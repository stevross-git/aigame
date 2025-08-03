import pygame
import math
from typing import Dict, List, Optional
from src.core.constants import *
from src.systems.skill_system import SkillSystem
from src.systems.inventory_system import InventorySystem, ItemType
from src.systems.crafting_system import CraftingSystem

class SkillsInventoryUI:
    """
    Combined UI for skills, inventory, and crafting similar to Stardew Valley
    """
    
    def __init__(self, screen, skill_system: SkillSystem, inventory_system: InventorySystem, crafting_system: CraftingSystem):
        self.screen = screen
        self.skills = skill_system
        self.inventory = inventory_system
        self.crafting = crafting_system
        self.visible = False
        self.current_tab = "inventory"  # "inventory", "skills", "crafting"
        
        # Fonts
        self.font_title = pygame.font.Font(None, 24)
        self.font_normal = pygame.font.Font(None, 20)
        self.font_small = pygame.font.Font(None, 16)
        
        # Colors
        self.bg_color = (40, 50, 60, 240)
        self.panel_color = (60, 70, 80, 220)
        self.border_color = (120, 140, 160)
        self.text_color = (255, 255, 255)
        self.tab_active_color = (80, 120, 160)
        self.tab_inactive_color = (60, 80, 100)
        
        # Panel dimensions
        self.panel_width = 600
        self.panel_height = 500
        self.panel_x = (SCREEN_WIDTH - self.panel_width) // 2
        self.panel_y = (SCREEN_HEIGHT - self.panel_height) // 2
        
        # Scroll offset for different tabs
        self.scroll_offset = {"inventory": 0, "skills": 0, "crafting": 0}
        self.max_scroll = {"inventory": 0, "skills": 0, "crafting": 0}
        
        # Selected item for details
        self.selected_item = None
    
    def show(self, tab: str = "inventory"):
        """Show the UI with specified tab"""
        self.visible = True
        self.current_tab = tab
        self.scroll_offset[tab] = 0
    
    def hide(self):
        """Hide the UI"""
        self.visible = False
    
    def toggle(self, tab: str = None):
        """Toggle UI visibility"""
        if self.visible:
            self.hide()
        else:
            self.show(tab or "inventory")
    
    def handle_event(self, event) -> bool:
        """Handle UI events"""
        if not self.visible:
            return False
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE or event.key == pygame.K_i:
                self.hide()
                return True
            elif event.key == pygame.K_1:
                self.current_tab = "inventory"
                return True
            elif event.key == pygame.K_2:
                self.current_tab = "skills"
                return True
            elif event.key == pygame.K_3:
                self.current_tab = "crafting"
                return True
            elif event.key == pygame.K_UP:
                self.scroll_up()
                return True
            elif event.key == pygame.K_DOWN:
                self.scroll_down()
                return True
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = event.pos
            
            # Check tab clicks
            if self._handle_tab_clicks(mouse_x, mouse_y):
                return True
            
            # Check if click is outside panel (close UI)
            panel_rect = pygame.Rect(self.panel_x, self.panel_y, self.panel_width, self.panel_height)
            if not panel_rect.collidepoint(mouse_x, mouse_y):
                self.hide()
                return True
            
            # Handle content clicks based on current tab
            if self.current_tab == "inventory":
                return self._handle_inventory_click(mouse_x, mouse_y)
            elif self.current_tab == "crafting":
                return self._handle_crafting_click(mouse_x, mouse_y)
        
        elif event.type == pygame.MOUSEWHEEL:
            if event.y > 0:
                self.scroll_up()
            else:
                self.scroll_down()
            return True
        
        return True  # Consume all events when visible
    
    def _handle_tab_clicks(self, mouse_x: int, mouse_y: int) -> bool:
        """Handle clicks on tab buttons"""
        tab_y = self.panel_y + 10
        tab_height = 30
        tab_width = 120
        
        tabs = [("inventory", "Inventory"), ("skills", "Skills"), ("crafting", "Crafting")]
        
        for i, (tab_id, tab_name) in enumerate(tabs):
            tab_x = self.panel_x + 20 + i * (tab_width + 10)
            tab_rect = pygame.Rect(tab_x, tab_y, tab_width, tab_height)
            
            if tab_rect.collidepoint(mouse_x, mouse_y):
                self.current_tab = tab_id
                self.scroll_offset[tab_id] = 0
                return True
        
        return False
    
    def _handle_inventory_click(self, mouse_x: int, mouse_y: int) -> bool:
        """Handle clicks in inventory tab"""
        # Item grid area
        content_y = self.panel_y + 60
        content_height = self.panel_height - 120
        
        item_size = 40
        items_per_row = (self.panel_width - 40) // (item_size + 10)
        
        all_items = list(self.inventory.get_all_items().items())
        
        for i, (item_id, inv_item) in enumerate(all_items):
            row = i // items_per_row
            col = i % items_per_row
            
            item_x = self.panel_x + 20 + col * (item_size + 10)
            item_y = content_y + 10 + row * (item_size + 10) - self.scroll_offset["inventory"]
            
            item_rect = pygame.Rect(item_x, item_y, item_size, item_size)
            
            if item_rect.collidepoint(mouse_x, mouse_y):
                self.selected_item = item_id
                return True
        
        return False
    
    def _handle_crafting_click(self, mouse_x: int, mouse_y: int) -> bool:
        """Handle clicks in crafting tab"""
        content_y = self.panel_y + 60
        recipe_height = 60
        
        available_recipes = self.crafting.get_available_recipes()
        
        for i, recipe in enumerate(available_recipes):
            recipe_y = content_y + 10 + i * (recipe_height + 5) - self.scroll_offset["crafting"]
            recipe_rect = pygame.Rect(self.panel_x + 20, recipe_y, self.panel_width - 40, recipe_height)
            
            if recipe_rect.collidepoint(mouse_x, mouse_y):
                # Attempt to craft
                success, message = self.crafting.craft_item(recipe.recipe_id)
                # Here you would show the message to the player via notification system
                return True
        
        return False
    
    def scroll_up(self):
        """Scroll content up"""
        self.scroll_offset[self.current_tab] = max(0, self.scroll_offset[self.current_tab] - 40)
    
    def scroll_down(self):
        """Scroll content down"""
        max_scroll = self.max_scroll[self.current_tab]
        self.scroll_offset[self.current_tab] = min(max_scroll, self.scroll_offset[self.current_tab] + 40)
    
    def draw(self):
        """Draw the skills and inventory UI"""
        if not self.visible:
            return
        
        # Semi-transparent background overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 100))
        self.screen.blit(overlay, (0, 0))
        
        # Main panel
        panel_rect = pygame.Rect(self.panel_x, self.panel_y, self.panel_width, self.panel_height)
        pygame.draw.rect(self.screen, self.bg_color, panel_rect, border_radius=10)
        pygame.draw.rect(self.screen, self.border_color, panel_rect, 3, border_radius=10)
        
        # Draw tabs
        self._draw_tabs()
        
        # Draw content based on current tab
        if self.current_tab == "inventory":
            self._draw_inventory_tab()
        elif self.current_tab == "skills":
            self._draw_skills_tab()
        elif self.current_tab == "crafting":
            self._draw_crafting_tab()
        
        # Draw instructions
        self._draw_instructions()
    
    def _draw_tabs(self):
        """Draw tab buttons"""
        tab_y = self.panel_y + 10
        tab_height = 30
        tab_width = 120
        
        tabs = [("inventory", "Inventory"), ("skills", "Skills"), ("crafting", "Crafting")]
        
        for i, (tab_id, tab_name) in enumerate(tabs):
            tab_x = self.panel_x + 20 + i * (tab_width + 10)
            tab_rect = pygame.Rect(tab_x, tab_y, tab_width, tab_height)
            
            # Tab background
            color = self.tab_active_color if tab_id == self.current_tab else self.tab_inactive_color
            pygame.draw.rect(self.screen, color, tab_rect, border_radius=5)
            pygame.draw.rect(self.screen, self.border_color, tab_rect, 2, border_radius=5)
            
            # Tab text
            text_surface = self.font_normal.render(tab_name, True, self.text_color)
            text_rect = text_surface.get_rect(center=tab_rect.center)
            self.screen.blit(text_surface, text_rect)
    
    def _draw_inventory_tab(self):
        """Draw inventory content"""
        content_y = self.panel_y + 60
        content_height = self.panel_height - 120
        
        # Money display
        money_text = f"Gold: {self.inventory.money}g"
        money_surface = self.font_normal.render(money_text, True, (255, 215, 0))
        self.screen.blit(money_surface, (self.panel_x + 20, content_y - 25))
        
        # Slots used display
        slots_text = f"Slots: {self.inventory.get_inventory_slots_used()}/{self.inventory.max_slots}"
        slots_surface = self.font_small.render(slots_text, True, self.text_color)
        self.screen.blit(slots_surface, (self.panel_x + self.panel_width - 150, content_y - 25))
        
        # Item grid
        item_size = 40
        items_per_row = (self.panel_width - 40) // (item_size + 10)
        
        all_items = list(self.inventory.get_all_items().items())
        total_rows = math.ceil(len(all_items) / items_per_row) if all_items else 0
        self.max_scroll["inventory"] = max(0, (total_rows * (item_size + 10)) - content_height + 50)
        
        for i, (item_id, inv_item) in enumerate(all_items):
            row = i // items_per_row
            col = i % items_per_row
            
            item_x = self.panel_x + 20 + col * (item_size + 10)
            item_y = content_y + 10 + row * (item_size + 10) - self.scroll_offset["inventory"]
            
            # Skip if outside visible area
            if item_y + item_size < content_y or item_y > content_y + content_height:
                continue
            
            item_rect = pygame.Rect(item_x, item_y, item_size, item_size)
            
            # Item background
            bg_color = (80, 90, 100) if item_id == self.selected_item else (60, 70, 80)
            pygame.draw.rect(self.screen, bg_color, item_rect, border_radius=5)
            pygame.draw.rect(self.screen, self.border_color, item_rect, 2, border_radius=5)
            
            # Item icon
            item_data = self.inventory.get_item_data(item_id)
            if item_data:
                icon_surface = self.font_small.render(item_data.icon, True, self.text_color)
                icon_rect = icon_surface.get_rect(center=(item_x + item_size // 2, item_y + item_size // 2 - 5))
                self.screen.blit(icon_surface, icon_rect)
            
            # Quantity
            if inv_item.quantity > 1:
                qty_surface = self.font_small.render(str(inv_item.quantity), True, self.text_color)
                qty_rect = qty_surface.get_rect()
                qty_rect.bottomright = (item_x + item_size - 2, item_y + item_size - 2)
                self.screen.blit(qty_surface, qty_rect)
            
            # Quality stars
            if inv_item.quality > 1:
                star_text = "⭐" * inv_item.quality
                star_surface = self.font_small.render(star_text, True, (255, 215, 0))
                star_rect = star_surface.get_rect()
                star_rect.bottomleft = (item_x + 2, item_y + item_size - 2)
                self.screen.blit(star_surface, star_rect)
        
        # Item details panel
        if self.selected_item:
            self._draw_item_details()
    
    def _draw_skills_tab(self):
        """Draw skills content"""
        content_y = self.panel_y + 60
        content_height = self.panel_height - 120
        
        # Skill points display
        points_text = f"Skill Points: {self.skills.skill_points}"
        points_surface = self.font_normal.render(points_text, True, (255, 215, 0))
        self.screen.blit(points_surface, (self.panel_x + 20, content_y - 25))
        
        # Skills list
        all_skills = self.skills.get_all_skills()
        skill_height = 60
        
        total_height = len(all_skills) * (skill_height + 5)
        self.max_scroll["skills"] = max(0, total_height - content_height + 20)
        
        y_offset = content_y + 10 - self.scroll_offset["skills"]
        
        for skill_id, skill_data in all_skills.items():
            skill_rect = pygame.Rect(self.panel_x + 20, y_offset, self.panel_width - 40, skill_height)
            
            # Skip if outside visible area
            if y_offset + skill_height < content_y or y_offset > content_y + content_height:
                y_offset += skill_height + 5
                continue
            
            # Skill background
            pygame.draw.rect(self.screen, self.panel_color, skill_rect, border_radius=5)
            pygame.draw.rect(self.screen, self.border_color, skill_rect, 2, border_radius=5)
            
            # Skill icon and name
            icon_surface = self.font_normal.render(skill_data.icon, True, self.text_color)
            self.screen.blit(icon_surface, (skill_rect.x + 10, skill_rect.y + 5))
            
            name_surface = self.font_normal.render(skill_data.name, True, self.text_color)
            self.screen.blit(name_surface, (skill_rect.x + 40, skill_rect.y + 5))
            
            # Level and experience
            level_text = f"Level {skill_data.level}"
            level_surface = self.font_normal.render(level_text, True, (100, 200, 100))
            level_rect = level_surface.get_rect()
            level_rect.topright = (skill_rect.right - 10, skill_rect.y + 5)
            self.screen.blit(level_surface, level_rect)
            
            # Experience bar
            exp_to_next = self.skills.get_experience_for_next_level(skill_id)
            if exp_to_next > 0:
                total_exp_for_level = 100 + ((skill_data.level + 1) * 50)
                current_exp_in_level = total_exp_for_level - exp_to_next
                progress = current_exp_in_level / total_exp_for_level
            else:
                progress = 1.0  # Max level
            
            bar_width = 200
            bar_height = 8
            bar_x = skill_rect.x + 40
            bar_y = skill_rect.y + 35
            
            # Background
            pygame.draw.rect(self.screen, (40, 40, 40), (bar_x, bar_y, bar_width, bar_height))
            # Progress
            progress_width = int(bar_width * progress)
            pygame.draw.rect(self.screen, (100, 200, 100), (bar_x, bar_y, progress_width, bar_height))
            
            # Experience text
            exp_text = f"XP: {skill_data.experience}"
            if exp_to_next > 0:
                exp_text += f" (Next: {exp_to_next})"
            exp_surface = self.font_small.render(exp_text, True, self.text_color)
            self.screen.blit(exp_surface, (bar_x, bar_y + 12))
            
            y_offset += skill_height + 5
    
    def _draw_crafting_tab(self):
        """Draw crafting content"""
        content_y = self.panel_y + 60
        content_height = self.panel_height - 120
        
        # Available recipes
        available_recipes = self.crafting.get_available_recipes()
        recipe_height = 60
        
        total_height = len(available_recipes) * (recipe_height + 5)
        self.max_scroll["crafting"] = max(0, total_height - content_height + 20)
        
        y_offset = content_y + 10 - self.scroll_offset["crafting"]
        
        for recipe in available_recipes:
            recipe_rect = pygame.Rect(self.panel_x + 20, y_offset, self.panel_width - 40, recipe_height)
            
            # Skip if outside visible area
            if y_offset + recipe_height < content_y or y_offset > content_y + content_height:
                y_offset += recipe_height + 5
                continue
            
            # Check if can craft
            can_craft, reason = self.crafting.can_craft(recipe.recipe_id)
            
            # Recipe background
            bg_color = (60, 100, 60) if can_craft else (80, 60, 60)
            pygame.draw.rect(self.screen, bg_color, recipe_rect, border_radius=5)
            pygame.draw.rect(self.screen, self.border_color, recipe_rect, 2, border_radius=5)
            
            # Result item
            result_item = self.inventory.get_item_data(recipe.result_item)
            if result_item:
                icon_surface = self.font_normal.render(result_item.icon, True, self.text_color)
                self.screen.blit(icon_surface, (recipe_rect.x + 10, recipe_rect.y + 5))
                
                name_surface = self.font_normal.render(result_item.name, True, self.text_color)
                self.screen.blit(name_surface, (recipe_rect.x + 40, recipe_rect.y + 5))
            
            # Ingredients
            ingredients_text = "Needs: "
            for i, (ingredient, amount) in enumerate(recipe.ingredients.items()):
                if i > 0:
                    ingredients_text += ", "
                ingredient_data = self.inventory.get_item_data(ingredient)
                ingredient_name = ingredient_data.name if ingredient_data else ingredient
                have_amount = self.inventory.get_item_count(ingredient)
                color_code = "✓" if have_amount >= amount else "✗"
                ingredients_text += f"{color_code}{amount} {ingredient_name}"
            
            ingredients_surface = self.font_small.render(ingredients_text, True, self.text_color)
            self.screen.blit(ingredients_surface, (recipe_rect.x + 40, recipe_rect.y + 25))
            
            # Craft status
            status_color = (100, 255, 100) if can_craft else (255, 100, 100)
            status_text = "Click to Craft!" if can_craft else reason
            status_surface = self.font_small.render(status_text, True, status_color)
            status_rect = status_surface.get_rect()
            status_rect.topright = (recipe_rect.right - 10, recipe_rect.y + 40)
            self.screen.blit(status_surface, status_rect)
            
            y_offset += recipe_height + 5
    
    def _draw_item_details(self):
        """Draw details panel for selected item"""
        if not self.selected_item or self.selected_item not in self.inventory.items:
            return
        
        inv_item = self.inventory.items[self.selected_item]
        item_data = self.inventory.get_item_data(self.selected_item)
        
        if not item_data:
            return
        
        # Details panel
        details_width = 200
        details_height = 150
        details_x = self.panel_x + self.panel_width - details_width - 20
        details_y = self.panel_y + 100
        
        details_rect = pygame.Rect(details_x, details_y, details_width, details_height)
        pygame.draw.rect(self.screen, self.panel_color, details_rect, border_radius=5)
        pygame.draw.rect(self.screen, self.border_color, details_rect, 2, border_radius=5)
        
        # Item name
        name_surface = self.font_normal.render(item_data.name, True, self.text_color)
        self.screen.blit(name_surface, (details_x + 10, details_y + 10))
        
        # Item description
        desc_lines = self._wrap_text(item_data.description, details_width - 20, self.font_small)
        y_pos = details_y + 35
        for line in desc_lines[:3]:  # Max 3 lines
            desc_surface = self.font_small.render(line, True, self.text_color)
            self.screen.blit(desc_surface, (details_x + 10, y_pos))
            y_pos += 18
        
        # Item stats
        y_pos += 10
        stats = [
            f"Type: {item_data.item_type.value.title()}",
            f"Quality: {'⭐' * inv_item.quality}",
            f"Value: {self.inventory.get_item_value(self.selected_item, inv_item.quality)}g",
            f"Stack: {inv_item.quantity}/{item_data.max_stack}"
        ]
        
        for stat in stats:
            if y_pos < details_y + details_height - 20:
                stat_surface = self.font_small.render(stat, True, self.text_color)
                self.screen.blit(stat_surface, (details_x + 10, y_pos))
                y_pos += 16
    
    def _wrap_text(self, text: str, max_width: int, font: pygame.font.Font) -> List[str]:
        """Wrap text to fit within max_width"""
        words = text.split(' ')
        lines = []
        current_line = []
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            if font.size(test_line)[0] <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                    current_line = [word]
                else:
                    lines.append(word)
        
        if current_line:
            lines.append(' '.join(current_line))
        
        return lines
    
    def _draw_instructions(self):
        """Draw control instructions"""
        instructions = [
            "ESC/I: Close",
            "1/2/3: Switch Tabs",
            "↑↓/Wheel: Scroll",
            "Click: Select/Craft"
        ]
        
        instr_y = self.panel_y + self.panel_height + 10
        for i, instruction in enumerate(instructions):
            instr_surface = self.font_small.render(instruction, True, (200, 200, 200))
            instr_rect = instr_surface.get_rect()
            instr_rect.x = self.panel_x + (i * 120)
            instr_rect.y = instr_y
            self.screen.blit(instr_surface, instr_rect)
    
    def update(self, dt):
        """Update the UI"""
        pass  # No animations currently