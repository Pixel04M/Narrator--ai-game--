"""
World System for Virtual Pet Game
==================================
Contains World, Camera, and Interactive Object classes.
Features:
- 1600x1200 map (larger than 800x600 window)
- Camera system that follows mouse/center
- Interactive objects: trees, rocks, food bowls, toys, beds
- Grid-based A* pathfinding
"""

import pygame
import random
import math
from pygame.sprite import Sprite, Group
import config


# ============================================
# Object Types
# ============================================
class ObjectType:
    """Enumeration of interactive object types."""
    FOOD_BOWL = "food_bowl"
    BED = "bed"
    TOY = "toy"
    TREE = "tree"
    ROCK = "rock"


# ============================================
# Interactive Object Base Class
# ============================================
class InteractiveObject(Sprite):
    """Base class for all interactive objects in the world."""
    
    def __init__(self, obj_type, x, y, width=60, height=60):
        super().__init__()
        self.object_type = obj_type
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        
        # Effect values
        self.hunger_effect = 0  # Negative = reduces hunger
        self.energy_effect = 0  # Positive = restores energy
        self.happiness_effect = 0  # Positive = increases happiness
        
        # Interaction
        self.interaction_cooldown = 0
        self.last_interaction_time = 0
        
        # Create surface
        self.image = pygame.Surface((width, height), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        
        # Draw the object
        self.draw_object()
    
    def draw_object(self):
        """Draw the object - overridden by subclasses."""
        pass
    
    def interact(self, character, current_time):
        """Handle interaction with a character."""
        if current_time - self.last_interaction_time < self.interaction_cooldown:
            return False
        
        self.last_interaction_time = current_time
        
        # Apply effects
        character.hunger = max(0, character.hunger + self.hunger_effect)
        character.energy = min(100, character.energy + self.energy_effect)
        character.happiness = min(100, character.happiness + self.happiness_effect)
        
        return True
    
    def get_interaction_message(self, character):
        """Get the message shown when interacting."""
        return ""
    
    def get_collision_rect(self):
        """Get collision rectangle for pathfinding."""
        return pygame.Rect(
            self.x - self.width // 2,
            self.y - self.height // 2,
            self.width,
            self.height
        )


# ============================================
# Food Bowl
# ============================================
class FoodBowl(InteractiveObject):
    """Food bowl that reduces hunger when used."""
    
    def __init__(self, x, y):
        super().__init__(ObjectType.FOOD_BOWL, x, y, 50, 40)
        self.hunger_effect = -30
        self.interaction_cooldown = 5000  # 5 seconds
    
    def draw_object(self):
        # Bowl base
        pygame.draw.ellipse(self.image, (200, 150, 100), (0, 10, 50, 30))
        pygame.draw.ellipse(self.image, (150, 100, 50), (5, 15, 40, 20))
        # Food
        pygame.draw.ellipse(self.image, (139, 69, 19), (10, 12, 30, 15))
        # Bowl rim
        pygame.draw.ellipse(self.image, (180, 130, 80), (0, 10, 50, 30), 3)
    
    def get_interaction_message(self, character):
        return f"{character.name} ate some food. Yummy!"


# ============================================
# Bed
# ============================================
class Bed(InteractiveObject):
    """Bed that restores energy when used."""
    
    def __init__(self, x, y):
        super().__init__(ObjectType.BED, x, y, 80, 50)
        self.energy_effect = 40
        self.interaction_cooldown = 10000  # 10 seconds
    
    def draw_object(self):
        # Bed frame
        pygame.draw.rect(self.image, (139, 90, 43), (0, 20, 80, 30))
        # Mattress
        pygame.draw.rect(self.image, (240, 240, 250), (5, 10, 70, 25))
        # Pillow
        pygame.draw.ellipse(self.image, (255, 255, 255), (5, 5, 25, 20))
        # Blanket
        pygame.draw.rect(self.image, (100, 149, 237), (35, 8, 40, 30))
    
    def get_interaction_message(self, character):
        return f"{character.name} took a nap. So restful!"


# ============================================
# Toy
# ============================================
class Toy(InteractiveObject):
    """Toy that increases happiness when played with."""
    
    def __init__(self, x, y):
        super().__init__(ObjectType.TOY, x, y, 35, 35)
        self.happiness_effect = 25
        self.interaction_cooldown = 3000  # 3 seconds
    
    def draw_object(self):
        # Ball shape
        pygame.draw.circle(self.image, (255, 100, 100), (17, 17), 17)
        pygame.draw.circle(self.image, (255, 200, 200), (17, 17), 17, 2)
        # Stripe
        pygame.draw.line(self.image, (255, 255, 255), (5, 17), (29, 17), 3)
    
    def get_interaction_message(self, character):
        return f"{character.name} played with the ball! Fun!"


# ============================================
# Tree
# ============================================
class Tree(InteractiveObject):
    """Tree that provides shade/rest."""
    
    def __init__(self, x, y):
        super().__init__(ObjectType.TREE, x, y, 70, 90)
        self.energy_effect = 15
        self.happiness_effect = 5
        self.interaction_cooldown = 8000  # 8 seconds
    
    def draw_object(self):
        # Trunk
        pygame.draw.rect(self.image, (139, 69, 19), (28, 50, 14, 40))
        # Foliage (multiple circles)
        pygame.draw.circle(self.image, (34, 139, 34), (35, 30), 25)
        pygame.draw.circle(self.image, (50, 205, 50), (20, 40), 18)
        pygame.draw.circle(self.image, (60, 179, 60), (50, 40), 18)
        pygame.draw.circle(self.image, (34, 139, 34), (35, 55), 15)
    
    def get_interaction_message(self, character):
        return f"{character.name} rested under the tree. Nice and cool!"


# ============================================
# Rock
# ============================================
class Rock(InteractiveObject):
    """Rock - obstacle that can be sat on."""
    
    def __init__(self, x, y):
        super().__init__(ObjectType.ROCK, x, y, 55, 40)
        self.energy_effect = 5
        self.interaction_cooldown = 5000
    
    def draw_object(self):
        # Rock shape (irregular oval)
        pygame.draw.ellipse(self.image, (128, 128, 128), (5, 10, 45, 25))
        pygame.draw.ellipse(self.image, (169, 169, 169), (8, 12, 40, 20))
        # Highlight
        pygame.draw.ellipse(self.image, (200, 200, 200), (10, 12, 15, 8))
    
    def get_interaction_message(self, character):
        return f"{character.name} sat on the rock."


# ============================================
# Camera System
# ============================================
class Camera:
    """Camera that can be dragged with left mouse button or follows a target."""
    
    def __init__(self, width, height, screen_width, screen_height):
        self.world_width = width
        self.world_height = height
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # Camera position (top-left corner)
        self.x = 0
        self.y = 0
        
        # Target position (for smooth following)
        self.target_x = 0
        self.target_y = 0
        
        # Following mode: "mouse", "center", "drag", or character name
        self.mode = "center"
        self.follow_target = None
        self.smoothing = 0.1  # Lower = smoother/slower
        
        # Drag state
        self.is_dragging = False
        self.drag_start_screen = (0, 0)  # Mouse position when drag started
        self.camera_start = (0, 0)  # Camera position when drag started
    
    def set_mode(self, mode):
        """Set camera follow mode."""
        self.mode = mode
    
    def set_target_character(self, character):
        """Set a specific character to follow."""
        self.follow_target = character
        self.mode = "character"
    
    def start_drag(self, mouse_pos):
        """Start dragging the camera."""
        self.is_dragging = True
        self.drag_start_screen = mouse_pos
        self.camera_start = (self.x, self.y)
        self.mode = "drag"
    
    def update_drag(self, mouse_pos):
        """Update camera position during drag."""
        if not self.is_dragging:
            return
        
        # Calculate how much mouse has moved
        delta_x = self.drag_start_screen[0] - mouse_pos[0]
        delta_y = self.drag_start_screen[1] - mouse_pos[1]
        
        # Move camera by the same amount (inverted for natural drag feel)
        new_x = self.camera_start[0] + delta_x
        new_y = self.camera_start[1] + delta_y
        
        # Clamp to world bounds
        new_x = max(0, min(self.world_width - self.screen_width, new_x))
        new_y = max(0, min(self.world_height - self.screen_height, new_y))
        
        self.x = new_x
        self.y = new_y
        self.target_x = new_x
        self.target_y = new_y
    
    def end_drag(self):
        """End dragging the camera."""
        self.is_dragging = False
    
    def update(self, mouse_pos):
        """Update camera position based on mode."""
        # If dragging, update drag position
        if self.is_dragging:
            self.update_drag(mouse_pos)
            return
        
        if self.mode == "drag":
            # Drag mode but not actively dragging - stay at current position
            self.target_x = self.x
            self.target_y = self.y
        elif self.mode == "mouse":
            # Follow mouse - offset camera so mouse is somewhat centered
            # but clamped to world bounds
            self.target_x = mouse_pos[0] - self.screen_width // 2
            self.target_y = mouse_pos[1] - self.screen_height // 2
        
        elif self.mode == "center":
            # Center on world
            self.target_x = (self.world_width - self.screen_width) // 2
            self.target_y = (self.world_height - self.screen_height) // 2
        
        elif self.mode == "character" and self.follow_target:
            # Follow specific character
            self.target_x = self.follow_target.x - self.screen_width // 2
            self.target_y = self.follow_target.y - self.screen_height // 2
        
        # Clamp target to world bounds
        self.target_x = max(0, min(self.world_width - self.screen_width, self.target_x))
        self.target_y = max(0, min(self.world_height - self.screen_height, self.target_y))
        
        # Smooth camera movement
        self.x += (self.target_x - self.x) * self.smoothing
        self.y += (self.target_y - self.y) * self.smoothing
    
    def world_to_screen(self, x, y):
        """Convert world coordinates to screen coordinates."""
        return (int(x - self.x), int(y - self.y))
    
    def screen_to_world(self, x, y):
        """Convert screen coordinates to world coordinates."""
        return (int(x + self.x), int(y + self.y))
    
    def draw_rect(self, rect):
        """Convert a world rect to screen rect for drawing."""
        return pygame.Rect(
            rect.x - self.x,
            rect.y - self.y,
            rect.width,
            rect.height
        )


# ============================================
# Pathfinding System (A*)
# ============================================
class PathfindingGrid:
    """Grid-based A* pathfinding system."""
    
    def __init__(self, width, height, cell_size=40):
        self.width = width
        self.height = height
        self.cell_size = cell_size
        self.cols = (width + cell_size - 1) // cell_size
        self.rows = (height + cell_size - 1) // cell_size
        
        # Grid: True = walkable, False = blocked
        self.grid = [[True for _ in range(self.cols)] for _ in range(self.rows)]
        
        # Obstacles
        self.obstacles = []
    
    def add_obstacle(self, rect):
        """Add an obstacle to the grid."""
        self.obstacles.append(rect)
        
        # Mark cells as blocked
        start_col = max(0, rect.x // self.cell_size)
        end_col = min(self.cols - 1, (rect.x + rect.width) // self.cell_size)
        start_row = max(0, rect.y // self.cell_size)
        end_row = min(self.rows - 1, (rect.y + rect.height) // self.cell_size)
        
        for row in range(start_row, end_row + 1):
            for col in range(start_col, end_col + 1):
                self.grid[row][col] = False
    
    def is_walkable(self, x, y):
        """Check if a world position is walkable."""
        col = int(x // self.cell_size)
        row = int(y // self.cell_size)
        
        if 0 <= row < self.rows and 0 <= col < self.cols:
            return self.grid[row][col]
        return False
    
    def world_to_cell(self, x, y):
        """Convert world position to grid cell."""
        return (int(y // self.cell_size), int(x // self.cell_size))
    
    def cell_to_world(self, row, col):
        """Convert grid cell to world position (center of cell)."""
        return (
            col * self.cell_size + self.cell_size // 2,
            row * self.cell_size + self.cell_size // 2
        )
    
    def get_neighbors(self, node):
        """Get walkable neighbors of a cell."""
        row, col = node
        neighbors = []
        
        # 8-directional movement
        directions = [
            (-1, 0), (1, 0), (0, -1), (0, 1),  # Cardinal
            (-1, -1), (-1, 1), (1, -1), (1, 1)  # Diagonal
        ]
        
        for d_row, d_col in directions:
            new_row, new_col = row + d_row, col + d_col
            
            if 0 <= new_row < self.rows and 0 <= new_col < self.cols:
                if self.grid[new_row][new_col]:
                    # For diagonal movement, check if we can cut corners
                    if d_row != 0 and d_col != 0:
                        if not self.grid[row + d_row][col] or not self.grid[row][col + d_col]:
                            continue
                    neighbors.append((new_row, new_col))
        
        return neighbors
    
    def heuristic(self, a, b):
        """Heuristic for A* (Euclidean distance)."""
        return math.sqrt((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2)
    
    def find_path(self, start_x, start_y, end_x, end_y):
        """Find path using A* algorithm."""
        start = self.world_to_cell(start_x, start_y)
        end = self.world_to_cell(end_x, end_y)
        
        # If start or end is blocked, find nearest walkable
        if not self.grid[start[0]][start[1]]:
            start = self.find_nearest_walkable(start)
        if not self.grid[end[0]][end[1]]:
            end = self.find_nearest_walkable(end)
        
        if not start or not end:
            return None
        
        # A* algorithm
        open_set = {start}
        closed_set = set()
        
        g_score = {start: 0}
        f_score = {start: self.heuristic(start, end)}
        
        came_from = {}
        
        while open_set:
            # Get node with lowest f_score
            current = min(open_set, key=lambda n: f_score.get(n, float('inf')))
            
            if current == end:
                # Reconstruct path
                path = []
                while current in came_from:
                    world_pos = self.cell_to_world(*current)
                    path.append(world_pos)
                    current = came_from[current]
                path.reverse()
                return path
            
            open_set.remove(current)
            closed_set.add(current)
            
            for neighbor in self.get_neighbors(current):
                if neighbor in closed_set:
                    continue
                
                # Cost: 1 for cardinal, 1.414 for diagonal
                is_diag = neighbor[0] != current[0] and neighbor[1] != current[1]
                tentative_g = g_score[current] + (1.414 if is_diag else 1)
                
                if neighbor not in open_set:
                    open_set.add(neighbor)
                elif tentative_g >= g_score.get(neighbor, float('inf')):
                    continue
                
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g
                f_score[neighbor] = tentative_g + self.heuristic(neighbor, end)
        
        return None  # No path found
    
    def find_nearest_walkable(self, cell):
        """Find nearest walkable cell to given cell."""
        if self.grid[cell[0]][cell[1]]:
            return cell
        
        # BFS to find nearest walkable
        queue = [cell]
        visited = {cell}
        
        while queue:
            current = queue.pop(0)
            
            for neighbor in self.get_neighbors(current):
                if neighbor not in visited:
                    if self.grid[neighbor[0]][neighbor[1]]:
                        return neighbor
                    visited.add(neighbor)
                    queue.append(neighbor)
        
        return None


# ============================================
# World Class
# ============================================
class World:
    """Main world class containing all game objects and systems."""
    
    def __init__(self, width=1600, height=1200):
        self.width = width
        self.height = height
        
        # Camera
        self.camera = Camera(
            width, height,
            config.SCREEN_WIDTH,
            config.SCREEN_HEIGHT
        )
        
        # Pathfinding
        self.pathfinding = PathfindingGrid(width, height, cell_size=40)
        
        # Object groups
        self.all_objects = Group()
        self.food_bowls = Group()
        self.beds = Group()
        self.toys = Group()
        self.trees = Group()
        self.rocks = Group()
        
        # Spawn objects
        self.spawn_objects()
    
    def spawn_objects(self):
        """Spawn interactive objects in the world."""
        
        # Food bowls (5 placed around the world)
        food_positions = [
            (200, 200), (600, 150), (1100, 300), 
            (1400, 800), (400, 1000)
        ]
        for pos in food_positions:
            bowl = FoodBowl(pos[0], pos[1])
            self.all_objects.add(bowl)
            self.food_bowls.add(bowl)
            self.pathfinding.add_obstacle(bowl.get_collision_rect())
        
        # Beds (3 placed around)
        bed_positions = [
            (300, 500), (800, 400), (1300, 600)
        ]
        for pos in bed_positions:
            bed = Bed(pos[0], pos[1])
            self.all_objects.add(bed)
            self.beds.add(bed)
            self.pathfinding.add_obstacle(bed.get_collision_rect())
        
        # Toys (6 scattered around)
        toy_positions = [
            (150, 350), (500, 250), (900, 350),
            (1200, 450), (300, 800), (1100, 900)
        ]
        for pos in toy_positions:
            toy = Toy(pos[0], pos[1])
            self.all_objects.add(toy)
            self.toys.add(toy)
        
        # Trees (5 large shade trees)
        tree_positions = [
            (150, 150), (700, 150), (1450, 200),
            (200, 1100), (1400, 1100)
        ]
        for pos in tree_positions:
            tree = Tree(pos[0], pos[1])
            self.all_objects.add(tree)
            self.trees.add(tree)
            self.pathfinding.add_obstacle(tree.get_collision_rect())
        
        # Rocks (8 obstacles)
        rock_positions = [
            (400, 300), (650, 350), (950, 300), (1250, 350),
            (300, 700), (600, 750), (1000, 700), (1300, 750)
        ]
        for pos in rock_positions:
            rock = Rock(pos[0], pos[1])
            self.all_objects.add(rock)
            self.rocks.add(rock)
            self.pathfinding.add_obstacle(rock.get_collision_rect())
    
    def update(self, mouse_pos):
        """Update world systems."""
        self.camera.update(mouse_pos)
    
    def get_nearest_object(self, obj_type, x, y, max_distance=200):
        """Get the nearest object of a given type to a position."""
        group = getattr(self, obj_type + "s", None)
        if not group:
            return None
        
        nearest = None
        min_dist = max_distance
        
        for obj in group:
            dist = math.hypot(obj.x - x, obj.y - y)
            if dist < min_dist:
                min_dist = dist
                nearest = obj
        
        return nearest
    
    def get_nearest_interactive(self, x, y, max_distance=150):
        """Get the nearest interactive object to a position."""
        nearest = None
        min_dist = max_distance
        
        for obj in self.all_objects:
            dist = math.hypot(obj.x - x, obj.y - y)
            if dist < min_dist:
                min_dist = dist
                nearest = obj
        
        return nearest
    
    def find_path(self, start_x, start_y, end_x, end_y):
        """Find a path between two points."""
        return self.pathfinding.find_path(start_x, start_y, end_x, end_y)
    
    def draw(self, surface):
        """Draw the world (background only - objects drawn separately)."""
        # Calculate visible area
        visible_rect = pygame.Rect(
            self.camera.x,
            self.camera.y,
            config.SCREEN_WIDTH,
            config.SCREEN_HEIGHT
        )
        
        # Draw grass/ground pattern
        for row in range(-1, (config.SCREEN_HEIGHT // 50) + 2):
            for col in range(-1, (config.SCREEN_WIDTH // 50) + 2):
                world_x = col * 50 + self.camera.x
                world_y = row * 50 + self.camera.y
                
                screen_x = col * 50
                screen_y = row * 50
                
                # Alternating grass colors
                if (row + col) % 2 == 0:
                    color = (124, 179, 66)  # Light green
                else:
                    color = (107, 156, 55)  # Darker green
                
                # Check if visible
                if 0 <= screen_x <= config.SCREEN_WIDTH and 0 <= screen_y <= config.SCREEN_HEIGHT:
                    pygame.draw.rect(surface, color, (screen_x, screen_y, 51, 51))
        
        # Draw world boundary indicators at edges
        if self.camera.x < 100:
            # Left edge hint
            for i in range(0, config.SCREEN_HEIGHT, 30):
                pygame.draw.polygon(surface, (150, 100, 50), [
                    (0, i), (15, i + 15), (0, i + 30)
                ])
        
        if self.camera.x > self.width - config.SCREEN_WIDTH - 100:
            # Right edge hint
            for i in range(0, config.SCREEN_HEIGHT, 30):
                pygame.draw.polygon(surface, (150, 100, 50), [
                    (config.SCREEN_WIDTH, i), (config.SCREEN_WIDTH - 15, i + 15), (config.SCREEN_WIDTH, i + 30)
                ])
        
        if self.camera.y < 100:
            # Top edge hint
            for i in range(0, config.SCREEN_WIDTH, 30):
                pygame.draw.polygon(surface, (150, 100, 50), [
                    (i, 0), (i + 15, 15), (i + 30, 0)
                ])
        
        if self.camera.y > self.height - config.SCREEN_HEIGHT - 100:
            # Bottom edge hint
            for i in range(0, config.SCREEN_WIDTH, 30):
                pygame.draw.polygon(surface, (150, 100, 50), [
                    (i, config.SCREEN_HEIGHT), (i + 15, config.SCREEN_HEIGHT - 15), (i + 30, config.SCREEN_HEIGHT)
                ])
    
    def draw_objects(self, surface):
        """Draw all interactive objects with camera offset."""
        for obj in self.all_objects:
            # Get screen position
            screen_x, screen_y = self.camera.world_to_screen(obj.x, obj.y)
            
            # Check if visible on screen
            if (-100 < screen_x < config.SCREEN_WIDTH + 100 and 
                -100 < screen_y < config.SCREEN_HEIGHT + 100):
                # Draw object at screen position
                draw_rect = pygame.Rect(
                    screen_x - obj.width // 2,
                    screen_y - obj.height // 2,
                    obj.width,
                    obj.height
                )
                surface.blit(obj.image, draw_rect)


# ============================================
# Minimap
# ============================================
class Minimap:
    """Minimap showing the world overview."""
    
    def __init__(self, world, width=160, height=120):
        self.world = world
        self.width = width
        self.height = height
        self.scale_x = width / world.width
        self.scale_y = height / world.height
        
        # Position
        self.x = config.SCREEN_WIDTH - width - 10
        self.y = 10
        
        self.rect = pygame.Rect(self.x, self.y, width, height)
    
    def draw(self, surface, characters):
        """Draw minimap."""
        # Background
        pygame.draw.rect(surface, (50, 80, 50), self.rect)
        pygame.draw.rect(surface, (100, 150, 100), self.rect, 2)
        
        # Draw objects as dots
        for obj in self.world.all_objects:
            dot_x = int(self.x + obj.x * self.scale_x)
            dot_y = int(self.y + obj.y * self.scale_y)
            
            if obj.object_type == ObjectType.FOOD_BOWL:
                color = (255, 150, 0)
            elif obj.object_type == ObjectType.BED:
                color = (100, 100, 255)
            elif obj.object_type == ObjectType.TOY:
                color = (255, 100, 100)
            elif obj.object_type == ObjectType.TREE:
                color = (34, 139, 34)
            elif obj.object_type == ObjectType.ROCK:
                color = (128, 128, 128)
            else:
                color = (200, 200, 200)
            
            pygame.draw.circle(surface, color, (dot_x, dot_y), 2)
        
        # Draw characters
        for char in characters:
            char_x = int(self.x + char.x * self.scale_x)
            char_y = int(self.y + char.y * self.scale_y)
            pygame.draw.circle(surface, char.base_color, (char_x, char_y), 3)
        
        # Draw camera viewport rectangle
        cam_rect = pygame.Rect(
            int(self.x + self.world.camera.x * self.scale_x),
            int(self.y + self.world.camera.y * self.scale_y),
            int(config.SCREEN_WIDTH * self.scale_x),
            int(config.SCREEN_HEIGHT * self.scale_y)
        )
        pygame.draw.rect(surface, (255, 255, 255), cam_rect, 1)
