import pygame
import random
from typing import Dict, List, Callable
from src.core.constants import *
from src.ui.menu import Button

class NPCDetailEditor:
    """Detailed NPC editor for customizing every aspect of an NPC"""
    
    def __init__(self, screen, npc_data=None):
        self.screen = screen
        self.font_title = pygame.font.Font(None, 28)
        self.font_subtitle = pygame.font.Font(None, 22)
        self.font_normal = pygame.font.Font(None, 18)
        
        # NPC data being edited
        self.npc_data = npc_data or self._create_default_npc()
        
        # Current editing section
        self.current_section = "basic"  # basic, personality, skills, backstory
        
        # Input states
        self.name_active = False
        self.age_active = False
        self.backstory_active = False
        self.backstory_scroll = 0
        
        # Available skill categories
        self.skill_categories = [
            "Combat", "Magic", "Crafting", "Social", "Knowledge", 
            "Athletics", "Stealth", "Medicine", "Engineering", "Arts"
        ]
        
        # Available specs/classes
        self.available_specs = [
            "Warrior", "Mage", "Rogue", "Healer", "Merchant", "Scholar", 
            "Artisan", "Farmer", "Noble", "Wanderer", "Inventor", "Artist"
        ]
        
        # Personality traits
        self.personality_traits = [
            "friendliness", "energy", "creativity", "organization", "confidence", 
            "empathy", "humor", "curiosity", "patience", "ambition", "loyalty", 
            "intelligence", "courage", "wisdom", "charm"
        ]
        
        self._create_ui_elements()
        
        # Callbacks
        self.on_save = None
        self.on_cancel = None
    
    def _create_default_npc(self):
        """Create a default NPC template"""
        return {
            "name": "New Character",
            "age": 25,
            "job": "Villager",
            "spec": "Wanderer",
            "backstory": "A mysterious character with an unknown past...",
            "personality": {trait: 0.5 for trait in self.personality_traits},
            "skills": {category: random.randint(1, 5) for category in self.skill_categories},
            "skill_points": 20,
            "available_skill_points": 20,
            "relationships": {},
            "interests": ["reading", "walking", "chatting"],
            "home_location": "Village Center"
        }
    
    def _create_ui_elements(self):
        """Create all UI elements"""
        center_x = SCREEN_WIDTH // 2
        
        # Section tabs
        tab_width = 140
        tab_y = 60
        self.section_tabs = {
            "basic": Button(center_x - 280, tab_y, tab_width, 35, "Basic Info", lambda: self._switch_section("basic"), 16),
            "personality": Button(center_x - 140, tab_y, tab_width, 35, "Personality", lambda: self._switch_section("personality"), 16),
            "skills": Button(center_x, tab_y, tab_width, 35, "Skills & Spec", lambda: self._switch_section("skills"), 16),
            "backstory": Button(center_x + 140, tab_y, tab_width, 35, "Backstory", lambda: self._switch_section("backstory"), 16),
        }
        
        # Control buttons
        self.save_button = Button(center_x - 100, SCREEN_HEIGHT - 80, 100, 50, "Save", self._save_npc)
        self.cancel_button = Button(center_x + 20, SCREEN_HEIGHT - 80, 100, 50, "Cancel", self._cancel_edit)
        self.random_button = Button(50, SCREEN_HEIGHT - 80, 120, 50, "Randomize All", self._randomize_npc)
        
        # Create section-specific elements
        self._create_basic_elements()
        self._create_personality_elements()
        self._create_skills_elements()
        self._create_backstory_elements()
    
    def _create_basic_elements(self):
        """Create basic info editing elements"""
        self.name_rect = pygame.Rect(200, 130, 300, 30)
        self.age_rect = pygame.Rect(200, 180, 100, 30)
        
        # Job/Spec dropdown
        current_spec_index = 0
        if self.npc_data["spec"] in self.available_specs:
            current_spec_index = self.available_specs.index(self.npc_data["spec"])
        
        self.spec_dropdown = SpecDropdown(200, 230, 200, 30, self.available_specs, current_spec_index)
        
        # Home location input
        self.home_rect = pygame.Rect(200, 280, 300, 30)
    
    def _create_personality_elements(self):
        """Create personality trait sliders"""
        self.personality_sliders = {}
        
        cols = 3
        rows = 5
        slider_width = 180
        slider_height = 20
        start_x = 100
        start_y = 130
        
        for i, trait in enumerate(self.personality_traits):
            col = i % cols
            row = i // cols
            
            x = start_x + col * (slider_width + 50)
            y = start_y + row * 45
            
            self.personality_sliders[trait] = PersonalitySlider(
                x, y, slider_width, slider_height, 0.0, 1.0,
                self.npc_data["personality"].get(trait, 0.5), trait.title()
            )
    
    def _create_skills_elements(self):
        """Create skill point allocation system"""
        self.skill_controls = {}
        
        cols = 2
        rows = 5
        control_width = 250
        start_x = 150
        start_y = 130
        
        for i, skill in enumerate(self.skill_categories):
            col = i % cols
            row = i // cols
            
            x = start_x + col * (control_width + 100)
            y = start_y + row * 40
            
            current_points = self.npc_data["skills"].get(skill, 1)
            self.skill_controls[skill] = SkillControl(x, y, control_width, skill, current_points)
        
        # Skill points display
        self.skill_points_rect = pygame.Rect(150, start_y + 220, 200, 30)
    
    def _create_backstory_elements(self):
        """Create backstory text editing"""
        self.backstory_rect = pygame.Rect(100, 130, SCREEN_WIDTH - 200, 300)
        self.backstory_lines = self.npc_data["backstory"].split('\\n') if self.npc_data["backstory"] else [""]
        self.current_line = 0
        self.cursor_pos = 0
    
    def _switch_section(self, section):
        """Switch to a different editing section"""
        self.current_section = section
        # Reset input states
        self.name_active = False
        self.age_active = False
        self.backstory_active = False
    
    def _save_npc(self):
        """Save the NPC and return to previous screen"""
        # Update NPC data from current inputs
        self._update_npc_from_inputs()
        
        if self.on_save:
            self.on_save(self.npc_data)
    
    def _cancel_edit(self):
        """Cancel editing and return to previous screen"""
        if self.on_cancel:
            self.on_cancel()
    
    def _randomize_npc(self):
        """Randomize all NPC attributes"""
        # Random name
        first_names = ["Alex", "Blake", "Casey", "Drew", "Sage", "River", "Quinn", "Avery", "Rowan", "Phoenix"]
        last_names = ["Smith", "Johnson", "Williams", "Brown", "Davis", "Miller", "Wilson", "Taylor", "Clark", "Lewis"]
        self.npc_data["name"] = f"{random.choice(first_names)} {random.choice(last_names)}"
        
        # Random age
        self.npc_data["age"] = random.randint(18, 65)
        
        # Random spec
        self.npc_data["spec"] = random.choice(self.available_specs)
        
        # Random personality
        for trait in self.personality_traits:
            self.npc_data["personality"][trait] = random.uniform(0.1, 0.9)
        
        # Random skills
        available_points = self.npc_data["available_skill_points"]
        skills = {}
        
        for skill in self.skill_categories:
            skills[skill] = 1  # Base point
            available_points -= 1
        
        # Distribute remaining points randomly
        while available_points > 0:
            skill = random.choice(self.skill_categories)
            if skills[skill] < 10:  # Max 10 points per skill
                skills[skill] += 1
                available_points -= 1
        
        self.npc_data["skills"] = skills
        
        # Random backstory
        backstories = [
            "A former adventurer who settled down in this peaceful village.",
            "Born and raised here, knows everyone and everything about the area.",
            "A mysterious traveler who arrived recently with few possessions.",
            "A skilled artisan who moved here to practice their craft in peace.",
            "A scholar seeking ancient knowledge hidden in the local area.",
            "A merchant who decided to stay after falling in love with the community."
        ]
        self.npc_data["backstory"] = random.choice(backstories)
        
        # Update UI elements
        self._update_ui_from_npc_data()
    
    def _update_ui_from_npc_data(self):
        """Update UI elements to reflect current NPC data"""
        # Update personality sliders
        for trait, slider in self.personality_sliders.items():
            slider.val = self.npc_data["personality"].get(trait, 0.5)
        
        # Update skill controls
        for skill, control in self.skill_controls.items():
            control.points = self.npc_data["skills"].get(skill, 1)
        
        # Update spec dropdown
        if self.npc_data["spec"] in self.available_specs:
            self.spec_dropdown.current_index = self.available_specs.index(self.npc_data["spec"])
        
        # Update backstory lines
        self.backstory_lines = self.npc_data["backstory"].split('\\n') if self.npc_data["backstory"] else [""]
    
    def _update_npc_from_inputs(self):
        """Update NPC data from current UI inputs"""
        # Update personality from sliders
        for trait, slider in self.personality_sliders.items():
            self.npc_data["personality"][trait] = slider.val
        
        # Update skills from controls
        total_used = 0
        for skill, control in self.skill_controls.items():
            self.npc_data["skills"][skill] = control.points
            total_used += control.points
        
        self.npc_data["available_skill_points"] = max(0, self.npc_data["skill_points"] - total_used)
        
        # Update spec from dropdown
        self.npc_data["spec"] = self.available_specs[self.spec_dropdown.current_index]
        
        # Update backstory from lines
        self.npc_data["backstory"] = '\\n'.join(self.backstory_lines)
    
    def handle_event(self, event):
        """Handle input events"""
        # Section tabs
        for button in self.section_tabs.values():
            if button.handle_event(event):
                return True
        
        # Control buttons
        if self.save_button.handle_event(event):
            return True
        if self.cancel_button.handle_event(event):
            return True
        if self.random_button.handle_event(event):
            return True
        
        # Section-specific handling
        if self.current_section == "basic":
            return self._handle_basic_events(event)
        elif self.current_section == "personality":
            return self._handle_personality_events(event)
        elif self.current_section == "skills":
            return self._handle_skills_events(event)
        elif self.current_section == "backstory":
            return self._handle_backstory_events(event)
        
        return False
    
    def _handle_basic_events(self, event):
        """Handle basic info section events"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.name_active = self.name_rect.collidepoint(event.pos)
            self.age_active = self.age_rect.collidepoint(event.pos)
        
        if event.type == pygame.KEYDOWN:
            if self.name_active:
                if event.key == pygame.K_BACKSPACE:
                    self.npc_data["name"] = self.npc_data["name"][:-1]
                elif event.key == pygame.K_TAB or event.key == pygame.K_RETURN:
                    self.name_active = False
                else:
                    if len(self.npc_data["name"]) < 30 and event.unicode.isprintable():
                        self.npc_data["name"] += event.unicode
                return True
            
            if self.age_active:
                if event.key == pygame.K_BACKSPACE:
                    age_str = str(self.npc_data["age"])[:-1]
                    self.npc_data["age"] = int(age_str) if age_str else 0
                elif event.key == pygame.K_TAB or event.key == pygame.K_RETURN:
                    self.age_active = False
                else:
                    if event.unicode.isdigit():
                        age_str = str(self.npc_data["age"]) + event.unicode
                        age = int(age_str)
                        if age <= 999:
                            self.npc_data["age"] = age
                return True
        
        # Spec dropdown
        if self.spec_dropdown.handle_event(event):
            return True
        
        return False
    
    def _handle_personality_events(self, event):
        """Handle personality section events"""
        for slider in self.personality_sliders.values():
            if slider.handle_event(event):
                return True
        return False
    
    def _handle_skills_events(self, event):
        """Handle skills section events"""
        for control in self.skill_controls.values():
            if control.handle_event(event):
                return True
        return False
    
    def _handle_backstory_events(self, event):
        """Handle backstory section events"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.backstory_rect.collidepoint(event.pos):
                self.backstory_active = True
                # Calculate line and cursor position
                relative_y = event.pos[1] - self.backstory_rect.y - self.backstory_scroll
                line_height = 25
                self.current_line = max(0, min(len(self.backstory_lines) - 1, relative_y // line_height))
                return True
            else:
                self.backstory_active = False
        
        if event.type == pygame.KEYDOWN and self.backstory_active:
            if event.key == pygame.K_BACKSPACE:
                if len(self.backstory_lines[self.current_line]) > 0:
                    self.backstory_lines[self.current_line] = self.backstory_lines[self.current_line][:-1]
                elif self.current_line > 0:
                    # Remove line and move to previous
                    self.backstory_lines.pop(self.current_line)
                    self.current_line -= 1
            elif event.key == pygame.K_RETURN:
                # Add new line
                self.backstory_lines.insert(self.current_line + 1, "")
                self.current_line += 1
            elif event.key == pygame.K_UP and self.current_line > 0:
                self.current_line -= 1
            elif event.key == pygame.K_DOWN and self.current_line < len(self.backstory_lines) - 1:
                self.current_line += 1
            else:
                if event.unicode.isprintable():
                    if len(self.backstory_lines[self.current_line]) < 60:  # Line length limit
                        self.backstory_lines[self.current_line] += event.unicode
            return True
        
        return False
    
    def draw(self):
        """Draw the NPC detail editor"""
        self.screen.fill((20, 25, 35))
        
        # Title
        title_text = self.font_title.render(f"Editing: {self.npc_data['name']}", True, WHITE)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, 30))
        self.screen.blit(title_text, title_rect)
        
        # Section tabs
        for section_name, button in self.section_tabs.items():
            # Highlight active tab
            if section_name == self.current_section:
                highlight_rect = pygame.Rect(button.rect.x - 2, button.rect.y - 2,
                                           button.rect.width + 4, button.rect.height + 4)
                pygame.draw.rect(self.screen, (100, 150, 200), highlight_rect, border_radius=5)
            button.draw(self.screen)
        
        # Draw current section content
        if self.current_section == "basic":
            self._draw_basic_section()
        elif self.current_section == "personality":
            self._draw_personality_section()
        elif self.current_section == "skills":
            self._draw_skills_section()
        elif self.current_section == "backstory":
            self._draw_backstory_section()
        
        # Control buttons
        self.save_button.draw(self.screen)
        self.cancel_button.draw(self.screen)
        self.random_button.draw(self.screen)
    
    def _draw_basic_section(self):
        """Draw basic info editing section"""
        y_pos = 120
        
        # Name input
        name_label = self.font_subtitle.render("Name:", True, WHITE)
        self.screen.blit(name_label, (50, y_pos + 5))
        
        name_color = (255, 255, 255) if self.name_active else (200, 200, 200)
        pygame.draw.rect(self.screen, (40, 40, 40), self.name_rect)
        pygame.draw.rect(self.screen, name_color, self.name_rect, 2)
        
        name_text = self.font_normal.render(self.npc_data["name"], True, WHITE)
        self.screen.blit(name_text, (self.name_rect.x + 5, self.name_rect.y + 5))
        
        # Age input
        y_pos += 50
        age_label = self.font_subtitle.render("Age:", True, WHITE)
        self.screen.blit(age_label, (50, y_pos + 5))
        
        age_color = (255, 255, 255) if self.age_active else (200, 200, 200)
        pygame.draw.rect(self.screen, (40, 40, 40), self.age_rect)
        pygame.draw.rect(self.screen, age_color, self.age_rect, 2)
        
        age_text = self.font_normal.render(str(self.npc_data["age"]), True, WHITE)
        self.screen.blit(age_text, (self.age_rect.x + 5, self.age_rect.y + 5))
        
        # Spec dropdown
        y_pos += 50
        spec_label = self.font_subtitle.render("Class/Spec:", True, WHITE)
        self.screen.blit(spec_label, (50, y_pos + 5))
        self.spec_dropdown.draw(self.screen)
        
        # Home location
        y_pos += 50
        home_label = self.font_subtitle.render("Home:", True, WHITE)
        self.screen.blit(home_label, (50, y_pos + 5))
        
        pygame.draw.rect(self.screen, (40, 40, 40), self.home_rect)
        pygame.draw.rect(self.screen, (200, 200, 200), self.home_rect, 2)
        
        home_text = self.font_normal.render(self.npc_data["home_location"], True, WHITE)
        self.screen.blit(home_text, (self.home_rect.x + 5, self.home_rect.y + 5))
    
    def _draw_personality_section(self):
        """Draw personality traits section"""
        # Instructions
        instruction_text = self.font_normal.render("Adjust personality traits (0.0 = Low, 1.0 = High):", True, (200, 200, 200))
        self.screen.blit(instruction_text, (50, 110))
        
        # Draw all personality sliders
        for slider in self.personality_sliders.values():
            slider.draw(self.screen)
    
    def _draw_skills_section(self):
        """Draw skills and spec section"""
        # Instructions
        instruction_text = self.font_normal.render("Allocate skill points (1-10 per skill):", True, (200, 200, 200))
        self.screen.blit(instruction_text, (50, 110))
        
        # Skill points remaining
        total_used = sum(control.points for control in self.skill_controls.values())
        remaining = self.npc_data["skill_points"] - total_used
        
        points_text = self.font_subtitle.render(f"Skill Points Remaining: {remaining}", True, 
                                              (255, 100, 100) if remaining < 0 else (100, 255, 100))
        self.screen.blit(points_text, (450, 110))
        
        # Draw all skill controls
        for control in self.skill_controls.values():
            control.draw(self.screen)
    
    def _draw_backstory_section(self):
        """Draw backstory editing section"""
        # Instructions
        instruction_text = self.font_normal.render("Write the character's backstory (Click to edit, Enter for new line):", True, (200, 200, 200))
        self.screen.blit(instruction_text, (50, 110))
        
        # Backstory text area
        pygame.draw.rect(self.screen, (30, 30, 30), self.backstory_rect)
        border_color = (255, 255, 255) if self.backstory_active else (150, 150, 150)
        pygame.draw.rect(self.screen, border_color, self.backstory_rect, 2)
        
        # Draw text lines
        line_height = 25
        for i, line in enumerate(self.backstory_lines):
            y = self.backstory_rect.y + 10 + i * line_height + self.backstory_scroll
            
            # Highlight current line
            if i == self.current_line and self.backstory_active:
                highlight_rect = pygame.Rect(self.backstory_rect.x + 2, y - 2, 
                                           self.backstory_rect.width - 4, line_height)
                pygame.draw.rect(self.screen, (50, 50, 80), highlight_rect)
            
            line_text = self.font_normal.render(line, True, WHITE)
            self.screen.blit(line_text, (self.backstory_rect.x + 10, y))


class PersonalitySlider:
    """Slider for personality traits"""
    
    def __init__(self, x, y, width, height, min_val, max_val, initial_val, label):
        self.rect = pygame.Rect(x, y, width, height)
        self.min_val = min_val
        self.max_val = max_val
        self.val = initial_val
        self.label = label
        self.dragging = False
        self.font = pygame.font.Font(None, 16)
    
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and self.rect.collidepoint(event.pos):
                self.dragging = True
                self._update_value(event.pos[0])
                return True
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                self.dragging = False
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            self._update_value(event.pos[0])
            return True
        return False
    
    def _update_value(self, mouse_x):
        relative_x = mouse_x - self.rect.x
        relative_x = max(0, min(relative_x, self.rect.width))
        self.val = self.min_val + (relative_x / self.rect.width) * (self.max_val - self.min_val)
    
    def draw(self, screen):
        # Label
        label_text = self.font.render(self.label, True, WHITE)
        screen.blit(label_text, (self.rect.x, self.rect.y - 18))
        
        # Slider track
        pygame.draw.rect(screen, (60, 60, 60), self.rect, border_radius=3)
        
        # Filled portion
        fill_width = (self.val - self.min_val) / (self.max_val - self.min_val) * self.rect.width
        fill_rect = pygame.Rect(self.rect.x, self.rect.y, fill_width, self.rect.height)
        pygame.draw.rect(screen, (100, 150, 200), fill_rect, border_radius=3)
        
        # Handle
        handle_x = self.rect.x + fill_width
        handle_rect = pygame.Rect(handle_x - 5, self.rect.y - 2, 10, self.rect.height + 4)
        pygame.draw.rect(screen, (200, 200, 200), handle_rect, border_radius=5)
        
        # Value text
        value_text = self.font.render(f"{self.val:.2f}", True, WHITE)
        screen.blit(value_text, (self.rect.right + 10, self.rect.y + 2))


class SkillControl:
    """Control for allocating skill points"""
    
    def __init__(self, x, y, width, skill_name, initial_points=1):
        self.rect = pygame.Rect(x, y, width, 30)
        self.skill_name = skill_name
        self.points = initial_points
        self.font = pygame.font.Font(None, 18)
        
        # + and - buttons
        self.minus_button = pygame.Rect(x + width - 80, y + 2, 25, 26)
        self.plus_button = pygame.Rect(x + width - 45, y + 2, 25, 26)
    
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.minus_button.collidepoint(event.pos):
                if self.points > 1:
                    self.points -= 1
                return True
            elif self.plus_button.collidepoint(event.pos):
                if self.points < 10:
                    self.points += 1
                return True
        return False
    
    def draw(self, screen):
        # Background
        pygame.draw.rect(screen, (40, 40, 40), self.rect)
        pygame.draw.rect(screen, (100, 100, 100), self.rect, 1)
        
        # Skill name
        name_text = self.font.render(self.skill_name, True, WHITE)
        screen.blit(name_text, (self.rect.x + 10, self.rect.y + 6))
        
        # Points display
        points_text = self.font.render(str(self.points), True, WHITE)
        screen.blit(points_text, (self.rect.x + 150, self.rect.y + 6))
        
        # - button
        pygame.draw.rect(screen, (80, 80, 80), self.minus_button)
        pygame.draw.rect(screen, WHITE, self.minus_button, 1)
        minus_text = self.font.render("-", True, WHITE)
        minus_rect = minus_text.get_rect(center=self.minus_button.center)
        screen.blit(minus_text, minus_rect)
        
        # + button
        pygame.draw.rect(screen, (80, 80, 80), self.plus_button)
        pygame.draw.rect(screen, WHITE, self.plus_button, 1)
        plus_text = self.font.render("+", True, WHITE)
        plus_rect = plus_text.get_rect(center=self.plus_button.center)
        screen.blit(plus_text, plus_rect)


class SpecDropdown:
    """Dropdown for selecting NPC spec/class"""
    
    def __init__(self, x, y, width, height, options, current_index=0):
        self.rect = pygame.Rect(x, y, width, height)
        self.options = options
        self.current_index = current_index
        self.font = pygame.font.Font(None, 18)
    
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.current_index = (self.current_index + 1) % len(self.options)
                return True
        return False
    
    def draw(self, screen):
        # Background
        pygame.draw.rect(screen, (40, 40, 40), self.rect)
        pygame.draw.rect(screen, (150, 150, 150), self.rect, 2)
        
        # Current option
        option_text = self.font.render(self.options[self.current_index], True, WHITE)
        screen.blit(option_text, (self.rect.x + 10, self.rect.y + 6))
        
        # Dropdown arrow
        arrow_text = self.font.render("▼", True, WHITE)
        screen.blit(arrow_text, (self.rect.right - 25, self.rect.y + 6))