import pygame
import os
from typing import Dict, Optional, Tuple

class ToolTileset:
    """
    Manages tool sprites from a tileset image
    """
    
    def __init__(self, tileset_path: str = "images/tools/tools_tileset.png"):
        self.tileset_path = tileset_path
        self.tileset = None
        self.tool_cache: Dict[str, pygame.Surface] = {}
        
        # Tool definitions based on actual tileset - 4 tools in a horizontal row
        # Each tool appears to be roughly 64x64 pixels based on the tileset image
        self.tool_definitions = {
            # Tools from left to right in the tileset
            "basic_axe": {"index": 0, "width": 64, "height": 64},
            "basic_pickaxe": {"index": 1, "width": 64, "height": 64}, 
            "iron_axe": {"index": 2, "width": 64, "height": 64},
            "basic_watering_can": {"index": 3, "width": 64, "height": 64},
            
            # Aliases for common tool names
            "axe": {"index": 0, "width": 64, "height": 64},
            "pickaxe": {"index": 1, "width": 64, "height": 64},
            "watering_can": {"index": 3, "width": 64, "height": 64},
            "bucket": {"index": 3, "width": 64, "height": 64},
            
            # Map missing tools to existing sprites
            "basic_hoe": {"index": 1, "width": 64, "height": 64},  # Use pickaxe sprite
            "fishing_rod": {"index": 3, "width": 64, "height": 64},  # Use watering can sprite
            "copper_hoe": {"index": 1, "width": 64, "height": 64},  # Use pickaxe sprite
            "advanced_fishing_rod": {"index": 3, "width": 64, "height": 64},  # Use watering can sprite
        }
        
        # Load tileset if it exists
        self._load_tileset()
    
    def _load_tileset(self) -> bool:
        """Load the tool tileset from file"""
        try:
            if os.path.exists(self.tileset_path):
                # Load image without convert_alpha() initially to avoid video mode issues
                self.tileset = pygame.image.load(self.tileset_path)
                print(f"✅ Loaded tool tileset: {self.tileset_path}")
                return True
            else:
                print(f"⚠️ Tool tileset not found: {self.tileset_path}")
                # Create a fallback tileset with colored rectangles
                self._create_fallback_tileset()
                return False
        except Exception as e:
            print(f"❌ Error loading tool tileset: {e}")
            self._create_fallback_tileset()
            return False
    
    def _create_fallback_tileset(self):
        """Create a fallback tileset with colored rectangles for tools"""
        # Create a simple tileset with colored squares for each tool
        tileset_width = 64 * 4  # 4 tools in a row
        tileset_height = 64
        self.tileset = pygame.Surface((tileset_width, tileset_height), pygame.SRCALPHA)
        
        # Tool colors for fallback - 4 tools only
        tool_colors = [
            (139, 69, 19),    # Brown for basic axe
            (128, 128, 128),  # Gray for basic pickaxe
            (105, 105, 105),  # Dark gray for iron axe
            (70, 130, 180),   # Steel blue for watering can
        ]
        
        for i, color in enumerate(tool_colors):
            x = i * 64
            pygame.draw.rect(self.tileset, color, (x, 0, 64, 64))
            # Add a simple tool-like shape
            pygame.draw.rect(self.tileset, (255, 255, 255), (x + 24, 8, 16, 48))  # Handle
            pygame.draw.rect(self.tileset, color, (x + 8, 8, 48, 16))  # Tool head
        
        print("🎨 Created fallback tool tileset with colored rectangles")
    
    def get_tool_sprite(self, tool_id: str, scale: float = 1.0) -> Optional[pygame.Surface]:
        """
        Get a tool sprite by its ID
        
        Args:
            tool_id: The tool identifier (e.g., "basic_axe")
            scale: Scale factor for the sprite (1.0 = original size)
        
        Returns:
            pygame.Surface or None if tool not found
        """
        if not self.tileset:
            return None
        
        # Ensure tileset has alpha conversion if display is available
        try:
            if hasattr(self.tileset, 'convert_alpha'):
                self.tileset = self.tileset.convert_alpha()
        except:
            pass  # Display not available yet
        
        # Check cache first
        cache_key = f"{tool_id}_{scale}"
        if cache_key in self.tool_cache:
            return self.tool_cache[cache_key]
        
        # Get tool definition
        if tool_id not in self.tool_definitions:
            # Only print warning once per tool to avoid spam
            if not hasattr(self, '_warned_tools'):
                self._warned_tools = set()
            if tool_id not in self._warned_tools:
                print(f"⚠️ Unknown tool: {tool_id} (Available: {list(self.tool_definitions.keys())})")
                self._warned_tools.add(tool_id)
            return None
        
        tool_def = self.tool_definitions[tool_id]
        sprite = self._extract_sprite(
            tool_def["index"], 
            tool_def["width"], 
            tool_def["height"]
        )
        
        if sprite and scale != 1.0:
            new_width = int(tool_def["width"] * scale)
            new_height = int(tool_def["height"] * scale)
            sprite = pygame.transform.scale(sprite, (new_width, new_height))
        
        # Cache the sprite
        if sprite:
            self.tool_cache[cache_key] = sprite
        
        return sprite
    
    def _extract_sprite(self, index: int, width: int = 64, height: int = 64) -> Optional[pygame.Surface]:
        """Extract a single sprite from the tileset"""
        if not self.tileset:
            return None
        
        try:
            # The tileset has 4 tools arranged horizontally
            # Calculate position based on the actual tileset dimensions
            tileset_width = self.tileset.get_width()
            tileset_height = self.tileset.get_height()
            
            # Each tool takes up 1/4 of the tileset width
            tool_width = tileset_width // 4
            x = index * tool_width
            y = 0
            
            # Extract the tool region and create a surface with alpha
            sprite = pygame.Surface((tool_width, tileset_height), pygame.SRCALPHA)
            sprite.blit(self.tileset, (0, 0), (x, y, tool_width, tileset_height))
            
            # Scale to requested size if different
            if tool_width != width or tileset_height != height:
                sprite = pygame.transform.scale(sprite, (width, height))
                
            return sprite
        except Exception as e:
            print(f"❌ Error extracting sprite {index}: {e}")
            return None
    
    def get_all_tool_sprites(self, scale: float = 1.0) -> Dict[str, pygame.Surface]:
        """Get all tool sprites as a dictionary"""
        sprites = {}
        for tool_id in self.tool_definitions.keys():
            sprite = self.get_tool_sprite(tool_id, scale)
            if sprite:
                sprites[tool_id] = sprite
        return sprites
    
    def get_tool_icon(self, tool_id: str, size: Tuple[int, int] = (32, 32)) -> Optional[pygame.Surface]:
        """Get a tool sprite scaled to icon size"""
        sprite = self.get_tool_sprite(tool_id)
        if sprite:
            return pygame.transform.scale(sprite, size)
        return None
    
    def reload_tileset(self, new_path: Optional[str] = None):
        """Reload the tileset, optionally from a new path"""
        if new_path:
            self.tileset_path = new_path
        
        self.tool_cache.clear()
        self._load_tileset()
    
    def list_available_tools(self) -> list:
        """Get list of all available tool IDs"""
        return list(self.tool_definitions.keys())
    
    def add_tool_definition(self, tool_id: str, index: int, width: int = 16, height: int = 16):
        """Add a new tool definition to the tileset"""
        self.tool_definitions[tool_id] = {
            "index": index,
            "width": width,
            "height": height
        }
        # Clear cache to force reload
        cache_keys_to_remove = [key for key in self.tool_cache.keys() if key.startswith(tool_id)]
        for key in cache_keys_to_remove:
            del self.tool_cache[key]

# Global tool tileset instance
_tool_tileset = None

def get_tool_tileset() -> ToolTileset:
    """Get the global tool tileset instance"""
    global _tool_tileset
    if _tool_tileset is None:
        _tool_tileset = ToolTileset()
    return _tool_tileset

def get_tool_sprite(tool_id: str, scale: float = 1.0) -> Optional[pygame.Surface]:
    """Convenience function to get a tool sprite"""
    return get_tool_tileset().get_tool_sprite(tool_id, scale)

def get_tool_icon(tool_id: str, size: Tuple[int, int] = (32, 32)) -> Optional[pygame.Surface]:
    """Convenience function to get a tool icon"""
    return get_tool_tileset().get_tool_icon(tool_id, size)