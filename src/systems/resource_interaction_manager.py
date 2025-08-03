import pygame
import math
import random
from typing import Dict, List, Optional, Tuple, Any
from enum import Enum
from src.core.constants import *
from src.systems.resource_system import ResourceSystem, ResourceNode
from src.systems.inventory_system import InventorySystem
from src.systems.skill_system import SkillSystem
from src.systems.quest_system import QuestSystem, ObjectiveType

class InteractionType(Enum):
    EXAMINE = "examine"
    HARVEST = "harvest"
    MINE = "mine"
    CHOP = "chop"
    FORAGE = "forage"
    FISH = "fish"
    DIG = "dig"

class InteractionState(Enum):
    IDLE = "idle"
    APPROACHING = "approaching"
    INTERACTING = "interacting"
    COMPLETED = "completed"
    FAILED = "failed"

class ResourceInteraction:
    """Represents an ongoing resource interaction"""
    
    def __init__(self, resource_node: ResourceNode, interaction_type: InteractionType, player_pos: Tuple[int, int]):
        self.resource_node = resource_node
        self.interaction_type = interaction_type
        self.player_pos = player_pos
        self.state = InteractionState.IDLE
        
        # Timing
        self.start_time = 0.0
        self.duration = self._calculate_duration()
        self.progress = 0.0
        
        # Visual effects
        self.particles = []
        self.sound_effects = []
        self.screen_shake = 0.0
        
        # Results
        self.items_gained = []
        self.experience_gained = 0
        self.skill_type = resource_node.skill_type
        
    def _calculate_duration(self) -> float:
        """Calculate interaction duration based on resource and type"""
        base_durations = {
            InteractionType.EXAMINE: 0.5,
            InteractionType.HARVEST: 1.5,
            InteractionType.MINE: 3.0,
            InteractionType.CHOP: 2.5,
            InteractionType.FORAGE: 1.0,
            InteractionType.FISH: 4.0,
            InteractionType.DIG: 2.0
        }
        return base_durations.get(self.interaction_type, 2.0)

class ResourceInteractionManager:
    """
    Manages complex resource interactions with visual feedback and skill progression
    """
    
    def __init__(self, resource_system: ResourceSystem, inventory_system: InventorySystem, skill_system: SkillSystem, xp_system=None, quest_system=None, action_bar=None):
        self.resources = resource_system
        self.inventory = inventory_system
        self.skills = skill_system
        self.xp_system = xp_system  # Optional XP system integration
        self.quest_system = quest_system  # Optional quest system integration
        self.action_bar = action_bar  # Optional action bar for equipped tools
        
        # Current interaction
        self.current_interaction: Optional[ResourceInteraction] = None
        self.interaction_queue: List[ResourceInteraction] = []
        
        # Player state
        self.player_pos = (0, 0)
        self.player_facing = "down"
        self.is_player_moving = False
        
        # Visual effects
        self.interaction_particles = []
        self.floating_text = []
        self.screen_effects = []
        
        # Audio feedback
        self.sound_queue = []
        
        # Resource detection
        self.nearby_resources = []
        self.detection_range = 80
        self.interaction_range = 50
        
        # Auto-interaction settings
        self.auto_harvest_enabled = False
        self.smart_tool_selection = True
        self.show_resource_outlines = True
        
        # Interaction history
        self.recent_interactions = []
        self.interaction_stats = {
            "total_harvests": 0,
            "successful_harvests": 0,
            "items_collected": 0,
            "experience_gained": 0
        }
        
        # Resource-specific interaction methods
        self.interaction_methods = {
            "oak_tree": InteractionType.CHOP,
            "pine_tree": InteractionType.CHOP,
            "stone_node": InteractionType.MINE,
            "copper_node": InteractionType.MINE,
            "iron_node": InteractionType.MINE,
            "berry_bush": InteractionType.FORAGE,
            "mushroom_log": InteractionType.FORAGE,
            "herb_patch": InteractionType.FORAGE
        }
        
        # Tool requirements
        self.tool_requirements = {
            InteractionType.CHOP: ["basic_axe", "copper_axe", "iron_axe"],
            InteractionType.MINE: ["basic_pickaxe", "copper_pickaxe", "iron_pickaxe"],
            InteractionType.FORAGE: [],  # No tools required
            InteractionType.DIG: ["basic_hoe", "copper_hoe"],
            InteractionType.FISH: ["fishing_rod", "advanced_fishing_rod"]
        }
    
    def update(self, dt: float, player_pos: Tuple[int, int], player_facing: str, is_moving: bool):
        """Update the interaction manager"""
        self.player_pos = player_pos
        self.player_facing = player_facing
        self.is_player_moving = is_moving
        
        # Update nearby resources
        self._update_nearby_resources()
        
        # Update current interaction
        if self.current_interaction:
            self._update_current_interaction(dt)
        
        # Process interaction queue
        self._process_interaction_queue()
        
        # Update visual effects
        self._update_visual_effects(dt)
        
        # Auto-harvest if enabled
        if self.auto_harvest_enabled and not self.current_interaction:
            self._try_auto_harvest()
    
    def _update_nearby_resources(self):
        """Update list of nearby resources"""
        self.nearby_resources = []
        
        for node in self.resources.resource_nodes:
            if node.current_yield > 0:
                distance = math.sqrt(
                    (node.x - self.player_pos[0]) ** 2 + 
                    (node.y - self.player_pos[1]) ** 2
                )
                
                if distance <= self.detection_range:
                    interaction_type = self.interaction_methods.get(node.resource_type, InteractionType.HARVEST)
                    can_interact = self._can_interact_with_resource(node, interaction_type)
                    
                    self.nearby_resources.append({
                        'node': node,
                        'distance': distance,
                        'interaction_type': interaction_type,
                        'can_interact': can_interact,
                        'tool_available': self._has_required_tool(interaction_type)
                    })
        
        # Sort by distance
        self.nearby_resources.sort(key=lambda x: x['distance'])
    
    def _can_interact_with_resource(self, node: ResourceNode, interaction_type: InteractionType) -> bool:
        """Check if player can interact with a resource"""
        try:
            # Check skill level
            player_skill = self.skills.get_skill_level(node.skill_type)
            if player_skill < node.required_skill_level:
                print(f"Skill check failed: player {node.skill_type} level {player_skill} < required {node.required_skill_level}")
                return False
            
            # Check tool requirement
            if not self._has_required_tool(interaction_type):
                print(f"Tool check failed for interaction type: {interaction_type}")
                return False
            
            # Check if resource is depleted
            if node.current_yield <= 0:
                print(f"Resource depleted: current yield {node.current_yield}")
                return False
            
            return True
        except Exception as e:
            print(f"Error in _can_interact_with_resource: {e}")
            return False
    
    def _has_required_tool(self, interaction_type: InteractionType) -> bool:
        """Check if player has required tool for interaction type"""
        required_tools = self.tool_requirements.get(interaction_type, [])
        
        if not required_tools:  # No tools required
            return True
        
        # First check if the right tool is equipped in action bar
        if self.action_bar:
            equipped_tool = self.action_bar.get_equipped_tool()
            if equipped_tool and equipped_tool in required_tools:
                return True
        
        # Fall back to checking inventory for any required tools
        for tool in required_tools:
            if self.inventory.has_item(tool):
                return True
        
        return False
    
    def _get_best_tool(self, interaction_type: InteractionType) -> Optional[str]:
        """Get the best available tool for interaction type"""
        required_tools = self.tool_requirements.get(interaction_type, [])
        
        # First check if equipped tool is suitable
        if self.action_bar:
            equipped_tool = self.action_bar.get_equipped_tool()
            if equipped_tool and equipped_tool in required_tools:
                return equipped_tool
        
        # Return the highest tier tool available in inventory
        for tool in reversed(required_tools):  # Reversed to get best tool first
            if self.inventory.has_item(tool):
                return tool
        
        return None
    
    def start_interaction(self, target_resource: ResourceNode, interaction_type: Optional[InteractionType] = None) -> bool:
        """Start an interaction with a resource"""
        try:
            if self.current_interaction:
                return False  # Already interacting
            
            print(f"Starting interaction with {target_resource.resource_type} (level {target_resource.required_skill_level})")
            
            # Determine interaction type
            if not interaction_type:
                interaction_type = self.interaction_methods.get(target_resource.resource_type, InteractionType.HARVEST)
            
            print(f"Interaction type: {interaction_type}")
            
            # Validate interaction
            if not self._can_interact_with_resource(target_resource, interaction_type):
                self._show_interaction_error("Cannot interact with this resource")
                return False
            
            # Check distance
            distance = math.sqrt(
                (target_resource.x - self.player_pos[0]) ** 2 + 
                (target_resource.y - self.player_pos[1]) ** 2
            )
            
            if distance > self.interaction_range:
                self._show_interaction_error("Too far away")
                return False
        except Exception as e:
            print(f"Error in start_interaction: {e}")
            self._show_interaction_error(f"Error starting interaction: {e}")
            return False
        
        # Create interaction
        interaction = ResourceInteraction(target_resource, interaction_type, self.player_pos)
        interaction.state = InteractionState.INTERACTING
        interaction.start_time = pygame.time.get_ticks() / 1000.0
        
        # Modify duration based on skill and tool
        skill_level = self.skills.get_skill_level(target_resource.skill_type)
        skill_modifier = max(0.3, 1.0 - (skill_level * 0.03))  # Up to 70% faster
        
        tool = self._get_best_tool(interaction_type)
        tool_modifier = self._get_tool_speed_modifier(tool)
        
        interaction.duration *= skill_modifier * tool_modifier
        
        self.current_interaction = interaction
        
        # Start visual effects
        self._start_interaction_effects(interaction)
        
        return True
    
    def _get_tool_speed_modifier(self, tool: Optional[str]) -> float:
        """Get speed modifier for tool quality"""
        if not tool:
            return 1.0
        
        tool_modifiers = {
            "basic_axe": 1.0,
            "copper_axe": 0.8,
            "iron_axe": 0.6,
            "basic_pickaxe": 1.0,
            "copper_pickaxe": 0.8,
            "iron_pickaxe": 0.6,
        }
        
        return tool_modifiers.get(tool, 1.0)
    
    def _update_current_interaction(self, dt: float):
        """Update the current interaction"""
        if not self.current_interaction:
            return
        
        interaction = self.current_interaction
        current_time = pygame.time.get_ticks() / 1000.0
        elapsed = current_time - interaction.start_time
        interaction.progress = min(1.0, elapsed / interaction.duration)
        
        # Update interaction effects
        self._update_interaction_effects(interaction, dt)
        
        # Check for completion
        if interaction.progress >= 1.0:
            self._complete_interaction(interaction)
        
        # Check for interruption (player moved too far)
        distance = math.sqrt(
            (interaction.resource_node.x - self.player_pos[0]) ** 2 + 
            (interaction.resource_node.y - self.player_pos[1]) ** 2
        )
        
        if distance > self.interaction_range * 1.5:  # Allow some movement
            self._interrupt_interaction("Moved too far away")
    
    def _complete_interaction(self, interaction: ResourceInteraction):
        """Complete a resource interaction"""
        node = interaction.resource_node
        
        # Calculate results
        success, message = self.resources.harvest_resource(
            self.player_pos[0], self.player_pos[1], 
            self._get_best_tool(interaction.interaction_type)
        )
        
        if success:
            interaction.state = InteractionState.COMPLETED
            
            # Update stats
            self.interaction_stats["total_harvests"] += 1
            self.interaction_stats["successful_harvests"] += 1
            
            # Grant XP if system is available
            if self.xp_system:
                try:
                    from src.systems.xp_system import XPCategory
                    xp_amount = 10 + node.required_skill_level * 5
                    
                    # Determine XP category based on resource type
                    if interaction.interaction_type in [InteractionType.CHOP, InteractionType.MINE, InteractionType.FORAGE]:
                        xp_category = XPCategory.GATHERING
                    elif interaction.interaction_type == InteractionType.FISH:
                        xp_category = XPCategory.FISHING
                    else:
                        xp_category = XPCategory.GATHERING
                    
                    self.xp_system.add_xp(xp_amount, xp_category, f"Harvested {node.resource_type}")
                except Exception as e:
                    print(f"Error adding XP in resource interaction: {e}")
            
            # Update quest objectives if quest system is available
            if self.quest_system:
                try:
                    # Update resource collection objectives
                    if interaction.interaction_type == InteractionType.CHOP:
                        self.quest_system.update_objective(ObjectiveType.CUT_TREE, node.resource_type)
                    elif interaction.interaction_type == InteractionType.MINE:
                        self.quest_system.update_objective(ObjectiveType.MINE_ROCK, node.resource_type)
                    
                    # Update item collection objectives
                    harvest_result = self.resources.get_last_harvest_result()
                    if harvest_result:
                        for item_id, quantity in harvest_result.items():
                            self.quest_system.update_objective(ObjectiveType.COLLECT_ITEMS, item_id, quantity)
                except Exception as e:
                    print(f"Error updating quest objectives in resource interaction: {e}")
            
            # Create success effects
            self._create_success_effects(interaction)
            
            # Show floating text
            self._show_floating_text(message, interaction.resource_node.x, interaction.resource_node.y - 30, (100, 255, 100))
            
        else:
            interaction.state = InteractionState.FAILED
            self._show_floating_text(message, interaction.resource_node.x, interaction.resource_node.y - 30, (255, 100, 100))
        
        # Record interaction
        self.recent_interactions.append({
            'resource_type': node.resource_type,
            'interaction_type': interaction.interaction_type.value,
            'success': success,
            'timestamp': pygame.time.get_ticks(),
            'location': (node.x, node.y)
        })
        
        # Keep only recent interactions
        if len(self.recent_interactions) > 50:
            self.recent_interactions = self.recent_interactions[-50:]
        
        # Clear current interaction
        self.current_interaction = None
    
    def _interrupt_interaction(self, reason: str):
        """Interrupt the current interaction"""
        if self.current_interaction:
            self.current_interaction.state = InteractionState.FAILED
            self._show_floating_text(f"Interrupted: {reason}", 
                                   self.current_interaction.resource_node.x, 
                                   self.current_interaction.resource_node.y - 30, 
                                   (255, 200, 100))
            self.current_interaction = None
    
    def _start_interaction_effects(self, interaction: ResourceInteraction):
        """Start visual effects for interaction"""
        # Add interaction-specific particles
        effect_type = interaction.interaction_type
        
        if effect_type == InteractionType.CHOP:
            self._create_chopping_particles(interaction.resource_node.x, interaction.resource_node.y)
        elif effect_type == InteractionType.MINE:
            self._create_mining_particles(interaction.resource_node.x, interaction.resource_node.y)
        elif effect_type == InteractionType.FORAGE:
            self._create_foraging_particles(interaction.resource_node.x, interaction.resource_node.y)
    
    def _update_interaction_effects(self, interaction: ResourceInteraction, dt: float):
        """Update ongoing interaction effects"""
        # Periodically add particles
        if random.random() < 0.3:  # 30% chance per frame
            self._add_interaction_particles(interaction)
        
        # Screen shake for heavy interactions
        if interaction.interaction_type in [InteractionType.CHOP, InteractionType.MINE]:
            if random.random() < 0.1:  # Occasional shake
                self.screen_effects.append({
                    'type': 'shake',
                    'intensity': 2.0,
                    'duration': 0.1
                })
    
    def _create_chopping_particles(self, x: int, y: int):
        """Create wood chip particles"""
        for _ in range(5):
            particle = {
                'x': x + random.randint(-20, 20),
                'y': y + random.randint(-20, 20),
                'vx': random.uniform(-50, 50),
                'vy': random.uniform(-80, -20),
                'life': random.uniform(1.0, 2.0),
                'max_life': 2.0,
                'color': (139, 119, 101),
                'size': random.randint(2, 4),
                'type': 'wood_chip'
            }
            self.interaction_particles.append(particle)
    
    def _create_mining_particles(self, x: int, y: int):
        """Create rock/mineral particles"""
        for _ in range(8):
            particle = {
                'x': x + random.randint(-15, 15),
                'y': y + random.randint(-15, 15),
                'vx': random.uniform(-40, 40),
                'vy': random.uniform(-60, -30),
                'life': random.uniform(0.8, 1.5),
                'max_life': 1.5,
                'color': (128, 128, 128),
                'size': random.randint(1, 3),
                'type': 'rock_chip'
            }
            self.interaction_particles.append(particle)
    
    def _create_foraging_particles(self, x: int, y: int):
        """Create plant/leaf particles"""
        for _ in range(3):
            particle = {
                'x': x + random.randint(-10, 10),
                'y': y + random.randint(-10, 10),
                'vx': random.uniform(-30, 30),
                'vy': random.uniform(-40, -10),
                'life': random.uniform(1.0, 1.8),
                'max_life': 1.8,
                'color': (100, 200, 100),
                'size': random.randint(2, 5),
                'type': 'leaf'
            }
            self.interaction_particles.append(particle)
    
    def _add_interaction_particles(self, interaction: ResourceInteraction):
        """Add particles during ongoing interaction"""
        x, y = interaction.resource_node.x, interaction.resource_node.y
        
        if interaction.interaction_type == InteractionType.CHOP:
            self._create_chopping_particles(x, y)
        elif interaction.interaction_type == InteractionType.MINE:
            self._create_mining_particles(x, y)
        elif interaction.interaction_type == InteractionType.FORAGE:
            self._create_foraging_particles(x, y)
    
    def _create_success_effects(self, interaction: ResourceInteraction):
        """Create effects when interaction succeeds"""
        x, y = interaction.resource_node.x, interaction.resource_node.y
        
        # Success sparkles
        for _ in range(10):
            particle = {
                'x': x + random.randint(-30, 30),
                'y': y + random.randint(-30, 30),
                'vx': random.uniform(-20, 20),
                'vy': random.uniform(-50, -10),
                'life': random.uniform(1.5, 2.5),
                'max_life': 2.5,
                'color': (255, 255, 100),
                'size': random.randint(1, 3),
                'type': 'sparkle'
            }
            self.interaction_particles.append(particle)
    
    def _show_floating_text(self, text: str, x: int, y: int, color: Tuple[int, int, int]):
        """Show floating text effect"""
        floating_text = {
            'text': text,
            'x': x,
            'y': y,
            'vx': random.uniform(-10, 10),
            'vy': -30,
            'life': 3.0,
            'max_life': 3.0,
            'color': color,
            'size': 20
        }
        self.floating_text.append(floating_text)
    
    def _show_interaction_error(self, message: str):
        """Show error message for failed interaction"""
        self._show_floating_text(message, self.player_pos[0], self.player_pos[1] - 50, (255, 100, 100))
    
    def _update_visual_effects(self, dt: float):
        """Update all visual effects"""
        # Update particles
        for particle in self.interaction_particles[:]:
            particle['life'] -= dt
            particle['x'] += particle['vx'] * dt
            particle['y'] += particle['vy'] * dt
            particle['vy'] += 50 * dt  # Gravity
            
            if particle['life'] <= 0:
                self.interaction_particles.remove(particle)
        
        # Update floating text
        for text in self.floating_text[:]:
            text['life'] -= dt
            text['x'] += text['vx'] * dt
            text['y'] += text['vy'] * dt
            text['vy'] *= 0.98  # Slow down over time
            
            if text['life'] <= 0:
                self.floating_text.remove(text)
        
        # Update screen effects
        for effect in self.screen_effects[:]:
            effect['duration'] -= dt
            if effect['duration'] <= 0:
                self.screen_effects.remove(effect)
    
    def _try_auto_harvest(self):
        """Try to automatically harvest nearby resources"""
        if not self.nearby_resources:
            return
        
        # Find closest harvestable resource
        for resource_info in self.nearby_resources:
            if (resource_info['can_interact'] and 
                resource_info['tool_available'] and 
                resource_info['distance'] <= self.interaction_range):
                
                self.start_interaction(resource_info['node'], resource_info['interaction_type'])
                break
    
    def _process_interaction_queue(self):
        """Process queued interactions"""
        # This could be used for chaining interactions
        pass
    
    def get_nearest_resource(self) -> Optional[Dict]:
        """Get information about the nearest interactable resource"""
        if not self.nearby_resources:
            return None
        return self.nearby_resources[0]
    
    def get_interaction_progress(self) -> float:
        """Get current interaction progress (0.0 to 1.0)"""
        if self.current_interaction:
            return self.current_interaction.progress
        return 0.0
    
    def is_interacting(self) -> bool:
        """Check if currently interacting with a resource"""
        return self.current_interaction is not None
    
    def cancel_interaction(self):
        """Cancel current interaction"""
        if self.current_interaction:
            self._interrupt_interaction("Cancelled by player")
    
    def get_interaction_stats(self) -> Dict:
        """Get interaction statistics"""
        return self.interaction_stats.copy()
    
    def draw_effects(self, screen: pygame.Surface, camera):
        """Draw interaction effects"""
        # Draw particles
        for particle in self.interaction_particles:
            alpha = int(255 * (particle['life'] / particle['max_life']))
            color = (*particle['color'], min(255, alpha))
            
            screen_pos = camera.apply_rect(pygame.Rect(
                particle['x'] - particle['size'], 
                particle['y'] - particle['size'], 
                particle['size'] * 2, 
                particle['size'] * 2
            ))
            
            pygame.draw.circle(screen, particle['color'], screen_pos.center, particle['size'])
        
        # Draw floating text
        for text in self.floating_text:
            alpha = int(255 * (text['life'] / text['max_life']))
            font = pygame.font.Font(None, text['size'])
            text_surface = font.render(text['text'], True, (*text['color'], alpha))
            
            screen_pos = camera.apply_rect(pygame.Rect(
                text['x'] - text_surface.get_width() // 2,
                text['y'],
                text_surface.get_width(),
                text_surface.get_height()
            ))
            
            screen.blit(text_surface, screen_pos)
        
        # Draw resource outlines
        if self.show_resource_outlines:
            self._draw_resource_outlines(screen, camera)
        
        # Draw interaction progress
        if self.current_interaction:
            self._draw_interaction_progress(screen, camera)
    
    def _draw_resource_outlines(self, screen: pygame.Surface, camera):
        """Draw outlines around nearby resources"""
        for resource_info in self.nearby_resources:
            node = resource_info['node']
            distance = resource_info['distance']
            
            # Color based on interaction status
            if resource_info['can_interact'] and resource_info['tool_available']:
                color = (100, 255, 100, 150)  # Green for ready
            elif resource_info['can_interact']:
                color = (255, 200, 100, 150)  # Yellow for missing tool
            else:
                color = (255, 100, 100, 150)  # Red for can't interact
            
            # Fade based on distance
            alpha_modifier = max(0.3, 1.0 - (distance / self.detection_range))
            color = (*color[:3], int(color[3] * alpha_modifier))
            
            # Draw outline
            outline_rect = camera.apply_rect(pygame.Rect(node.x - 20, node.y - 20, 40, 40))
            pygame.draw.rect(screen, color[:3], outline_rect, 3, border_radius=8)
    
    def _draw_interaction_progress(self, screen: pygame.Surface, camera):
        """Draw progress bar for current interaction"""
        if not self.current_interaction:
            return
        
        node = self.current_interaction.resource_node
        progress = self.current_interaction.progress
        
        # Progress bar position
        bar_rect = camera.apply_rect(pygame.Rect(node.x - 30, node.y - 50, 60, 8))
        
        # Background
        pygame.draw.rect(screen, (50, 50, 50), bar_rect, border_radius=4)
        pygame.draw.rect(screen, (150, 150, 150), bar_rect, 2, border_radius=4)
        
        # Progress fill
        fill_width = int(bar_rect.width * progress)
        if fill_width > 0:
            fill_rect = pygame.Rect(bar_rect.x, bar_rect.y, fill_width, bar_rect.height)
            
            # Color based on interaction type
            colors = {
                InteractionType.CHOP: (200, 150, 100),
                InteractionType.MINE: (150, 150, 200),
                InteractionType.FORAGE: (100, 200, 100),
                InteractionType.HARVEST: (200, 200, 100)
            }
            color = colors.get(self.current_interaction.interaction_type, (100, 150, 200))
            
            pygame.draw.rect(screen, color, fill_rect, border_radius=4)
        
        # Interaction type text
        font = pygame.font.Font(None, 16)
        type_text = self.current_interaction.interaction_type.value.title()
        text_surface = font.render(type_text, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=(bar_rect.centerx, bar_rect.y - 15))
        
        # Text background
        bg_rect = text_rect.inflate(6, 2)
        pygame.draw.rect(screen, (0, 0, 0, 180), bg_rect, border_radius=3)
        screen.blit(text_surface, text_rect)