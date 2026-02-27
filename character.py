"""
Character Class for Virtual Pet Game
=====================================
Contains the Character sprite class with AI personality and state management.
"""

import pygame
import random
import math
from pygame.sprite import Sprite
import config


class Character(Sprite):
    """Base Character class with AI personality, memory, and pathfinding."""
    
    def __init__(self, name, personality, color, x, y):
        super().__init__()
        self.name = name
        self.personality = personality
        self.base_color = color
        self.color = list(color)  # Will change based on state
        self.radius = config.CHARACTER_RADIUS
        
        # Position and movement
        self.x = x
        self.y = y
        self.target_x = x
        self.target_y = y
        self.original_x = x  # Store original position
        self.original_y = y
        self.speed = config.DEFAULT_CHARACTER_SPEED
        self.velocity_x = 0
        self.velocity_y = 0
        
        # Pathfinding
        self.path = []
        self.path_index = 0
        self.world = None
        
        # States
        self.state = 'idle'
        self.happiness = 50  # 0-100
        self.hunger = 0  # 0-100 (increases over time)
        self.energy = 100  # 0-100 (decreases over time)
        self.last_interaction_time = pygame.time.get_ticks()
        
        # Personality-specific timers
        self.state_timer = 0
        self.hide_timer = 0
        self.tantrum_count = 0
        self.bounce_timer = 0
        
        # Visual effects
        self.shake_offset = 0
        self.sparkle_timer = 0
        self.bounce_offset = 0
        self.dance_direction = 1
        
        # Selection and chat
        self.is_selected = False
        self.speech_bubble_text = ""
        self.speech_bubble_start_time = 0
        
        # === MEMORY SYSTEM ===
        self.memory = {'food_bowl': [], 'bed': [], 'toy': [], 'tree': [], 'rock': []}
        self.known_locations = {'food_bowl': None, 'bed': None, 'toy': None}
        self.explored_areas = []
        self.last_exploration_time = pygame.time.get_ticks()
        self.exploration_interval = 10000
        
        # === RELATIONSHIP SYSTEM ===
        self.relationships = {}
        self.last_meeting_times = {}
        self.last_meeting_time = 0
        self.last_met_character = None
        self.shared_info = []
        
        # === LEARNING SYSTEM ===
        self.action_outcomes = {}
        self.curiosity = 50
        self.last_interaction_object = None
        
        # Create surface for the character
        self.image = pygame.Surface((self.radius * 2 + 40, self.radius * 2 + 60), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        
        # Bounding circle for click detection
        self.hitbox_radius = self.radius
    
    def update_ai(self, mouse_pos, current_time, all_characters, world=None):
        """AI decision making - called every frame."""
        self.world = world  # Store world reference for pathfinding
        
        mouse_x, mouse_y = mouse_pos
        
        # Convert mouse to world coordinates if we have a world
        if world:
            mouse_x, mouse_y = world.camera.screen_to_world(mouse_pos[0], mouse_pos[1])
        
        # Update timers
        if self.state_timer > 0:
            self.state_timer -= 1
            if self.state_timer <= 0:
                self.return_to_idle()
        
        # Update dance animation
        if self.state == 'dancing':
            self.bounce_offset += 0.3 * self.dance_direction
            if abs(self.bounce_offset) > 15:
                self.dance_direction *= -1
        
        # Time-based state changes (needs)
        time_since_interaction = current_time - self.last_interaction_time
        
        # Update hunger (increases slowly)
        self.hunger = min(100, self.hunger + 0.02)
        
        # Update energy (decreases slowly)
        self.energy = max(0, self.energy - 0.01)
        
        # Personality-specific AI behavior
        if self.personality == config.PERSONALITY_FRIENDLY:
            self.update_friendly_ai(mouse_pos, time_since_interaction, world)
        elif self.personality == config.PERSONALITY_SHY:
            self.update_shy_ai(mouse_pos, time_since_interaction, world)
        elif self.personality == config.PERSONALITY_GRUMPY:
            self.update_grumpy_ai(mouse_pos, time_since_interaction, world)
        elif self.personality == config.PERSONALITY_PLAYFUL:
            self.update_playful_ai(mouse_pos, time_since_interaction, world)
        
        # Check needs-based states
        if self.state not in ['happy', 'angry', 'scared', 'hiding', 'tantrum', 'playing', 'dancing', 'lined', 'seeking']:
            if self.hunger > 70:
                self.state = 'hungry'
                self.color = [min(255, c + 30) for c in self.base_color]
            elif self.energy < 20:
                self.state = 'sleepy'
                self.color = [max(0, c - 30) for c in self.base_color]
            elif self.happiness < 20:
                self.state = 'sad'
                self.color = [max(0, c - 20) for c in self.base_color]
            else:
                self.color = list(self.base_color)
        
        # Check for nearby objects to interact with
        if world and self.state not in ['dancing', 'tantrum', 'hiding']:
            self.check_nearby_objects(world, current_time)
        
        # Check for nearby characters (communication)
        if world:
            self.check_nearby_characters(all_characters, current_time)
        
        # Movement toward target (with pathfinding)
        self.move_toward_target(world)
        
        # Update position
        self.rect.center = (self.x, self.y)
    
    def update_friendly_ai(self, mouse_pos, time_since_interaction, world=None):
        """Fifi: Friendly, leads others to good spots, shares info."""
        mouse_x, mouse_y = mouse_pos
        if world:
            mouse_x, mouse_y = world.camera.screen_to_world(mouse_pos[0], mouse_pos[1])
        
        # Gets sad if ignored too long (15 seconds)
        if time_since_interaction > 15000 and self.state == 'idle':
            self.state = 'sad'
            self.happiness = max(0, self.happiness - 1)
        
        # Follow mouse slowly when idle
        if self.state == 'idle':
            dist_to_mouse = math.hypot(mouse_x - self.x, mouse_y - self.y)
            if dist_to_mouse > 100:
                self.target_x = mouse_x
                self.target_y = mouse_y
                self.speed = 1.5  # Slow following
            else:
                # Move slightly toward mouse
                self.target_x = self.x + (mouse_x - self.x) * 0.01
                self.target_y = self.y + (mouse_y - self.y) * 0.01
        
        # If hungry, seek food
        if self.hunger > 50 and self.state == 'hungry':
            self.seek_object('food_bowl', world)
        
        # If tired, seek bed
        if self.energy < 30 and self.state == 'sleepy':
            self.seek_object('bed', world)
        
        # Fifi likes to explore and share discoveries
        if world and time_since_interaction > 20000:
            if random.random() < 0.005:  # Occasional exploration
                self.explore(world)
    
    def update_shy_ai(self, mouse_pos, time_since_interaction, world=None):
        """Shyel: Shy, avoids crowds, explores alone."""
        mouse_x, mouse_y = mouse_pos
        if world:
            mouse_x, mouse_y = world.camera.screen_to_world(mouse_pos[0], mouse_pos[1])
        
        if self.state == 'hiding':
            # Stay hidden for a few seconds
            self.hide_timer -= 1
            if self.hide_timer <= 0:
                self.state = 'idle'
                self.return_to_idle()
            return
        
        # Avoid mouse when idle
        if self.state == 'idle':
            dist_to_mouse = math.hypot(mouse_x - self.x, mouse_y - self.y)
            if dist_to_mouse < 150:
                # Move away from mouse
                angle = math.atan2(self.y - mouse_y, self.x - mouse_x)
                self.target_x = self.x + math.cos(angle) * 100
                self.target_y = self.y + math.sin(angle) * 100
                # Keep in bounds
                self.target_x = max(50, min(1550, self.target_x))
                self.target_y = max(150, min(1150, self.target_y))
                self.speed = 3
        
        # Shyel avoids crowds - seek quiet areas
        if world and self.state == 'idle':
            # Seek tree areas for solitude
            if random.random() < 0.003:
                self.seek_object('tree', world)
    
    def update_grumpy_ai(self, mouse_pos, time_since_interaction, world=None):
        """Grump: Grumpy, ignores communication, doesn't share info."""
        mouse_x, mouse_y = mouse_pos
        if world:
            mouse_x, mouse_y = world.camera.screen_to_world(mouse_pos[0], mouse_pos[1])
        
        if self.state == 'tantrum':
            # Bouncing around during tantrum
            self.shake_offset = random.randint(-5, 5)
            self.state_timer -= 1
            if self.state_timer <= 0:
                self.state = 'idle'
                self.tantrum_count = 0
                self.shake_offset = 0
            return
        
        # Become grumpy if clicked too much
        if self.tantrum_count >= 3 and self.state != 'tantrum':
            self.state = 'tantrum'
            self.state_timer = 180  # 3 seconds at 60 FPS
            # Random bounce target
            self.target_x = random.randint(100, 1500)
            self.target_y = random.randint(150, 1100)
            self.speed = 8
        
        # Slowly calm down
        if self.state == 'angry':
            self.happiness = min(100, self.happiness + 0.1)
        
        # Grump ignores others - don't seek company
        # But still needs to satisfy needs
        if world and self.state == 'idle':
            if self.hunger > 60:
                self.seek_object('food_bowl', world)
            elif self.energy < 25:
                self.seek_object('bed', world)
    
    def update_playful_ai(self, mouse_pos, time_since_interaction, world=None):
        """Pippin: Curious, finds toys, invites others to play."""
        mouse_x, mouse_y = mouse_pos
        if world:
            mouse_x, mouse_y = world.camera.screen_to_world(mouse_pos[0], mouse_pos[1])
        
        if self.state == 'playing':
            # Bounce around
            self.bounce_timer -= 1
            if self.bounce_timer <= 0:
                # Get bored, seek new interaction
                self.state = 'idle'
                # Move to random spot to find something to do
                self.target_x = random.randint(100, 1500)
                self.target_y = random.randint(150, 1100)
                self.speed = 4
            else:
                # Bouncy movement
                self.target_x = self.x + random.randint(-50, 50)
                self.target_y = self.y + random.randint(-30, 30)
                self.target_x = max(50, min(1550, self.target_x))
                self.target_y = max(150, min(1150, self.target_y))
                self.speed = 5
        
        # Seek interaction if bored (no interaction for 8 seconds)
        if time_since_interaction > 8000 and self.state == 'idle':
            # Move toward mouse to seek attention
            self.target_x = mouse_x
            self.target_y = mouse_y
            self.speed = 3
        
        # Pippin loves toys - seek them frequently
        if world and self.state == 'idle':
            if random.random() < 0.01:  # High curiosity for toys
                self.seek_object('toy', world)
        
        # High curiosity - explore new areas
        if world and time_since_interaction > 15000 and self.state == 'idle':
            if random.random() < 0.008:
                self.explore(world)
    
    def move_toward_target(self, world=None):
        """Move toward target position with optional pathfinding."""
        
        # If we have a path, follow it
        if self.path and self.path_index < len(self.path):
            target = self.path[self.path_index]
            dx = target[0] - self.x
            dy = target[1] - self.y
            distance = math.hypot(dx, dy)
            
            if distance > 10:
                self.x += (dx / distance) * self.speed
                self.y += (dy / distance) * self.speed
            else:
                self.path_index += 1
            
            # Keep in world bounds
            self.x = max(50, min(1550, self.x))
            self.y = max(150, min(1150, self.y))
            return
        
        # Direct movement without pathfinding
        dx = self.target_x - self.x
        dy = self.target_y - self.y
        distance = math.hypot(dx, dy)
        
        if distance > 5:
            # Apply velocity
            self.x += (dx / distance) * self.speed
            self.y += (dy / distance) * self.speed
        
        # Keep in bounds
        self.x = max(50, min(1550, self.x))
        self.y = max(150, min(1150, self.y))
    
    # =============================
    # PATHFINDING METHODS
    # =============================
    
    def set_path(self, path):
        """Set a path to follow."""
        self.path = path if path else []
        self.path_index = 0
    
    def seek_object(self, object_type, world, max_distance=500):
        """Seek the nearest object of a given type."""
        if not world:
            return
        
        # Check memory first
        known = self.known_locations.get(object_type)
        if known:
            # Go to known location
            self.target_x = known[0]
            self.target_y = known[1]
            self.state = 'seeking'
            return
        
        # Find nearest in world
        nearest = world.get_nearest_object(object_type, self.x, self.y, max_distance)
        if nearest:
            # Learn this location
            self.remember_object(nearest)
            
            # Use pathfinding if available
            if world.pathfinding:
                path = world.find_path(self.x, self.y, nearest.x, nearest.y)
                if path:
                    self.set_path(path)
                else:
                    self.target_x = nearest.x
                    self.target_y = nearest.y
            else:
                self.target_x = nearest.x
                self.target_y = nearest.y
            
            self.state = 'seeking'
    
    def explore(self, world):
        """Explore an unexplored area."""
        if not world:
            return
        
        # Pick a random unexplored area
        target_x = random.randint(100, 1500)
        target_y = random.randint(150, 1100)
        
        # Use pathfinding
        path = world.find_path(self.x, self.y, target_x, target_y)
        if path:
            self.set_path(path)
        else:
            self.target_x = target_x
            self.target_y = target_y
        
        self.state = 'seeking'
    
    # =============================
    # MEMORY METHODS
    # =============================
    
    def remember_object(self, obj):
        """Remember an object's location."""
        obj_type = obj.object_type
        if obj_type in self.memory:
            # Check if we already know about this location
            for loc in self.memory[obj_type]:
                if math.hypot(loc[0] - obj.x, loc[1] - obj.y) < 50:
                    return  # Already known
            
            # Add to memory
            quality = self.judge_object_quality(obj)
            self.memory[obj_type].append((obj.x, obj.y, quality))
            
            # Update known location (best one)
            self.update_known_location(obj_type)
    
    def judge_object_quality(self, obj):
        """Judge the quality of an object (0-10)."""
        # Base quality
        quality = 5
        
        # Adjust based on object type
        if obj.object_type == 'food_bowl':
            quality = 7
        elif obj.object_type == 'bed':
            quality = 8
        elif obj.object_type == 'toy':
            quality = 6
        elif obj.object_type == 'tree':
            quality = 5
        
        return quality
    
    def update_known_location(self, obj_type):
        """Update the best known location for an object type."""
        if obj_type in self.memory and self.memory[obj_type]:
            # Find the best quality location
            best = max(self.memory[obj_type], key=lambda x: x[2])
            self.known_locations[obj_type] = (best[0], best[1])
    
    # =============================
    # RELATIONSHIP METHODS
    # =============================
    
    def meet_character(self, other, current_time):
        """Record meeting another character."""
        if other.name not in self.relationships:
            # Initialize relationship based on personality
            self.initialize_relationship(other)
        
        # Update meeting time
        self.last_meeting_times[other.name] = current_time
        self.last_meeting_time = current_time
        self.last_met_character = other
        
        # Adjust relationship based on behavior
        self.interact_with_character(other, current_time)
    
    def initialize_relationship(self, other):
        """Initialize relationship based on personalities."""
        # Fifi is friendly with everyone
        if self.personality == config.PERSONALITY_FRIENDLY:
            self.relationships[other.name] = 50
        # Shyel is shy with grumpy
        elif self.personality == config.PERSONALITY_SHY:
            if other.personality == config.PERSONALITY_GRUMPY:
                self.relationships[other.name] = -20
            else:
                self.relationships[other.name] = 20
        # Grumpy starts neutral
        elif self.personality == config.PERSONALITY_GRUMPY:
            self.relationships[other.name] = 0
        # Pippin is playful with everyone
        elif self.personality == config.PERSONALITY_PLAYFUL:
            self.relationships[other.name] = 40
        else:
            self.relationships[other.name] = 0
    
    def interact_with_character(self, other, current_time):
        """Interact with another character (share info, etc.)."""
        if not other or other == self:
            return
        
        rel = self.relationships.get(other.name, 0)
        
        # Fifi shares info with friends
        if self.personality == config.PERSONALITY_FRIENDLY:
            if rel > 30:
                self.share_info_with(other)
        
        # Pippin invites others to play
        if self.personality == config.PERSONALITY_PLAYFUL:
            if rel > 20 and random.random() < 0.3:
                self.invite_to_play(other)
        
        # Grump doesn't share
        if self.personality == config.PERSONALITY_GRUMPY:
            return  # Grump doesn't interact
        
        # Shyel shares only if comfortable
        if self.personality == config.PERSONALITY_SHY:
            if rel > 40:
                self.share_info_with(other)
    
    def share_info_with(self, other):
        """Share discovered information with another character."""
        if not other:
            return
        
        # Share known locations
        for obj_type, location in self.known_locations.items():
            if location and random.random() < 0.5:
                info = f"I found a {obj_type.replace('_', ' ')}!"
                self.shared_info.append(info)
                # Other character learns this
                other.remember_location_from_other(obj_type, location)
    
    def remember_location_from_other(self, obj_type, location):
        """Remember a location shared by another character."""
        if obj_type in self.known_locations and self.known_locations[obj_type] is None:
            self.known_locations[obj_type] = location
    
    def invite_to_play(self, other):
        """Invite another character to play."""
        if not other:
            return
        
        # Create speech bubble
        messages = [
            f"Hey {other.name}, want to play?",
            f"{other.name}! Come find toys with me!",
            "Let's have fun together!"
        ]
        # Will be displayed by game
        self.pending_invite = other.name
    
    def check_nearby_characters(self, all_characters, current_time):
        """Check if near other characters and potentially communicate."""
        communication_range = 100  # Pixels
        
        for other in all_characters:
            if other == self:
                continue
            
            dist = math.hypot(other.x - self.x, other.y - self.y)
            if dist < communication_range:
                # Check if recently met
                last_meet = self.last_meeting_times.get(other.name, 0)
                if current_time - last_meet > 10000:  # 10 seconds cooldown
                    self.meet_character(other, current_time)
    
    def check_nearby_objects(self, world, current_time):
        """Check for nearby objects to interact with."""
        if not world:
            return
        
        interaction_range = 60
        
        # Get nearest object
        obj = world.get_nearest_interactive(self.x, self.y, interaction_range)
        if obj and obj.last_interaction_time > 0:
            # Check cooldown
            if current_time - obj.last_interaction_time > obj.interaction_cooldown:
                # Interact!
                if obj.interact(self, current_time):
                    self.last_interaction_object = obj
                    self.remember_object(obj)
                    self.happiness = min(100, self.happiness + 5)
    
    def handle_click(self, click_pos):
        """Handle mouse click on character."""
        click_x, click_y = click_pos
        distance = math.hypot(click_x - self.x, click_y - self.y)
        
        if distance <= self.hitbox_radius:
            self.last_interaction_time = pygame.time.get_ticks()
            return True
        return False
    
    def on_clicked(self):
        """Reaction when clicked - depends on personality."""
        if self.personality == config.PERSONALITY_FRIENDLY:
            # Becomes happy, sparkles
            self.state = 'happy'
            self.happiness = min(100, self.happiness + 30)
            self.state_timer = 120  # 2 seconds
            self.sparkle_timer = 60
            self.color = list(self.base_color)
        
        elif self.personality == config.PERSONALITY_SHY:
            # Gets scared, runs away to hide
            self.state = 'scared'
            self.target_x = random.choice([80, config.SCREEN_WIDTH - 80])
            self.target_y = random.choice([200, config.SCREEN_HEIGHT - 150])
            self.speed = config.FAST_SPEED
            self.hide_timer = 180  # 3 seconds
            self.happiness = max(0, self.happiness - 20)
        
        elif self.personality == config.PERSONALITY_GRUMPY:
            # Gets angry
            self.state = 'angry'
            self.tantrum_count += 1
            self.happiness = max(0, self.happiness - 10)
            self.color = [min(255, c + 50) for c in self.base_color]  # Redder
            self.state_timer = 90  # 1.5 seconds
            self.shake_offset = 10
        
        elif self.personality == config.PERSONALITY_PLAYFUL:
            # Playful response, bounces around
            self.state = 'playing'
            self.happiness = min(100, self.happiness + 20)
            self.bounce_timer = 120  # 2 seconds
            # Random bounce direction
            self.target_x = random.randint(100, config.SCREEN_WIDTH - 100)
            self.target_y = random.randint(150, config.SCREEN_HEIGHT - 100)
    
    def return_to_idle(self):
        """Return to idle state."""
        self.state = 'idle'
        self.shake_offset = 0
        self.bounce_offset = 0
        self.color = list(self.base_color)
    
    def draw(self, surface, current_time=0):
        """Draw the character (legacy - uses stored position)."""
        self.draw_at(surface, self.x, self.y, current_time)
    
    def draw_at(self, surface, screen_x, screen_y, current_time=0):
        """Draw the character at a specific screen position."""
        # Apply shake offset for angry/tantrum states
        draw_x = screen_x + self.shake_offset
        # Apply bounce offset for dancing
        draw_y = screen_y + self.bounce_offset
        
        # Draw shadow
        pygame.draw.ellipse(surface, (0, 0, 0, 50), 
                           (draw_x - self.radius + 10, draw_y + self.radius - 5, 
                            self.radius * 2 - 20, 15))
        
        # Draw selection glow if selected
        if self.is_selected:
            glow_radius = self.radius + 5
            # Create a glowing effect
            for i in range(3):
                glow_alpha = 100 - i * 30
                glow_surface = pygame.Surface((glow_radius * 2 + 20, glow_radius * 2 + 20), pygame.SRCALPHA)
                pygame.draw.circle(glow_surface, (*config.SELECTED_GLOW, glow_alpha), 
                                 (glow_radius + 10, glow_radius + 10), glow_radius - i * 3)
                surface.blit(glow_surface, (draw_x - glow_radius - 10, draw_y - glow_radius - 10))
        
        # Draw body (circle)
        body_color = tuple(self.color)
        pygame.draw.circle(surface, body_color, (int(draw_x), int(draw_y)), self.radius)
        
        # Draw face based on state
        self.draw_face(surface, draw_x, draw_y)
        
        # Draw sparkle effect for happy Fifi
        if self.sparkle_timer > 0:
            self.draw_sparkles(surface, draw_x, draw_y)
            self.sparkle_timer -= 1
        
        # Draw name label
        font = pygame.font.Font(None, 24)
        name_surface = font.render(self.name, True, (50, 50, 50))
        name_rect = name_surface.get_rect(center=(draw_x, draw_y - self.radius - 15))
        surface.blit(name_surface, name_rect)
        
        # Draw state emoji
        emoji = config.STATE_EMOJIS.get(self.state, '😐')
        emoji_surface = font.render(emoji, True, (0, 0, 0))
        emoji_rect = emoji_surface.get_rect(center=(draw_x + 25, draw_y - self.radius - 15))
        surface.blit(emoji_surface, emoji_rect)
        
        # Draw speech bubble if active
        if current_time > 0:
            self.draw_speech_bubble(surface, draw_x, draw_y, current_time)
    
    def draw_face(self, surface, x, y):
        """Draw the character's face based on state."""
        # Eye positions
        eye_offset_x = 12
        eye_offset_y = -5
        eye_radius = 6
        
        # Draw eyes based on state
        if self.state == 'sleepy':
            # Closed eyes (lines)
            pygame.draw.line(surface, (50, 50, 50), 
                           (x - eye_offset_x - 5, y + eye_offset_y),
                           (x - eye_offset_x + 5, y + eye_offset_y), 2)
            pygame.draw.line(surface, (50, 50, 50), 
                           (x + eye_offset_x - 5, y + eye_offset_y),
                           (x + eye_offset_x + 5, y + eye_offset_y), 2)
        elif self.state == 'hiding':
            # Hidden face (just eyes visible, looking away)
            pygame.draw.circle(surface, (255, 255, 255), 
                             (int(x - eye_offset_x), int(y + eye_offset_y)), eye_radius)
            pygame.draw.circle(surface, (255, 255, 255), 
                             (int(x + eye_offset_x), int(y + eye_offset_y)), eye_radius)
            pygame.draw.circle(surface, (50, 50, 50), 
                             (int(x - eye_offset_x - 2), int(y + eye_offset_y)), 3)
            pygame.draw.circle(surface, (50, 50, 50), 
                             (int(x + eye_offset_x + 2), int(y + eye_offset_y)), 3)
        else:
            # Normal/other eyes (white with black pupils)
            # Left eye
            pygame.draw.circle(surface, (255, 255, 255), 
                             (int(x - eye_offset_x), int(y + eye_offset_y)), eye_radius)
            pygame.draw.circle(surface, (50, 50, 50), 
                             (int(x - eye_offset_x), int(y + eye_offset_y)), 3)
            # Right eye
            pygame.draw.circle(surface, (255, 255, 255), 
                             (int(x + eye_offset_x), int(y + eye_offset_y)), eye_radius)
            pygame.draw.circle(surface, (50, 50, 50), 
                             (int(x + eye_offset_x), int(y + eye_offset_y)), 3)
        
        # Draw mouth based on state
        mouth_y = y + 18
        if self.state == 'happy' or self.state == 'playing' or self.state == 'dancing':
            # Big smile
            pygame.draw.arc(surface, (50, 50, 50), 
                           (x - 15, mouth_y - 10, 30, 20),
                           0, 3.14, 2)
        elif self.state == 'sad':
            # Frown
            pygame.draw.arc(surface, (50, 50, 50), 
                           (x - 15, mouth_y, 30, 20),
                           3.14, 6.28, 2)
        elif self.state == 'angry' or self.state == 'tantrum':
            # Angry frown
            pygame.draw.arc(surface, (50, 50, 50), 
                           (x - 15, mouth_y, 30, 20),
                           3.14, 6.28, 2)
            # Angry eyebrows
            pygame.draw.line(surface, (50, 50, 50),
                           (x - eye_offset_x - 8, y + eye_offset_y - 10),
                           (x - eye_offset_x + 2, y + eye_offset_y - 6), 2)
            pygame.draw.line(surface, (50, 50, 50),
                           (x + eye_offset_x + 8, y + eye_offset_y - 10),
                           (x + eye_offset_x - 2, y + eye_offset_y - 6), 2)
        elif self.state == 'scared':
            # O-shaped mouth
            pygame.draw.circle(surface, (50, 50, 50), (int(x), int(mouth_y)), 5)
        elif self.state == 'sleepy':
            # Small open mouth (yawning)
            pygame.draw.ellipse(surface, (50, 50, 50), 
                              (x - 4, mouth_y, 8, 6))
        elif self.state == 'hungry':
            # Tongue out
            pygame.draw.arc(surface, (50, 50, 50), 
                           (x - 12, mouth_y - 8, 24, 16),
                           0, 3.14, 2)
            pygame.draw.ellipse(surface, (200, 100, 150), 
                              (x - 4, mouth_y + 2, 8, 6))
        else:
            # Neutral smile
            pygame.draw.arc(surface, (50, 50, 50), 
                           (x - 12, mouth_y - 5, 24, 12),
                           0, 3.14, 2)
    
    def draw_sparkles(self, surface, x, y):
        """Draw sparkle effect around happy character."""
        sparkle_positions = [
            (x - 30, y - 20),
            (x + 30, y - 15),
            (x - 25, y + 25),
            (x + 25, y + 20),
            (x, y - 35)
        ]
        
        for i, (sx, sy) in enumerate(sparkle_positions):
            if (self.sparkle_timer + i * 10) % 60 < 30:
                pygame.draw.circle(surface, (255, 255, 150), 
                                 (int(sx), int(sy)), 3)
    
    def set_speech_bubble(self, text, current_time):
        """Set a speech bubble to display above the character."""
        self.speech_bubble_text = text
        self.speech_bubble_start_time = current_time
    
    def has_active_speech_bubble(self, current_time):
        """Check if character has an active speech bubble."""
        return (current_time - self.speech_bubble_start_time) < config.SPEECH_BUBBLE_LIFETIME
    
    def get_speech_bubble_opacity(self, current_time):
        """Get the opacity for the speech bubble based on its age."""
        age = current_time - self.speech_bubble_start_time
        if age > (config.SPEECH_BUBBLE_LIFETIME - config.SPEECH_BUBBLE_FADE_TIME):
            fade_progress = (age - (config.SPEECH_BUBBLE_LIFETIME - config.SPEECH_BUBBLE_FADE_TIME)) / config.SPEECH_BUBBLE_FADE_TIME
            return max(0, 255 - int(fade_progress * 255))
        return 255
    
    def draw_speech_bubble(self, surface, screen_x, screen_y, current_time):
        """Draw a speech bubble above the character at the given screen position."""
        if not self.has_active_speech_bubble(current_time):
            return
        
        # Get opacity for fading
        opacity = self.get_speech_bubble_opacity(current_time)
        if opacity <= 0:
            return
        
        # Font setup
        font = pygame.font.Font(None, 24)
        text_surface = font.render(self.speech_bubble_text, True, (30, 30, 30))
        text_rect = text_surface.get_rect()
        
        # Bubble dimensions - use screen coordinates
        bubble_padding = 15
        bubble_width = text_rect.width + bubble_padding * 2
        bubble_height = text_rect.height + bubble_padding * 2
        bubble_x = screen_x - bubble_width // 2
        bubble_y = screen_y - self.radius - bubble_height - 20
        
        # Keep bubble on screen
        bubble_x = max(10, min(config.SCREEN_WIDTH - bubble_width - 10, bubble_x))
        bubble_y = max(10, bubble_y)
        
        # Draw bubble background with alpha
        bubble_surface = pygame.Surface((bubble_width, bubble_height), pygame.SRCALPHA)
        bubble_surface.fill((255, 255, 245, opacity))
        
        # Draw border
        pygame.draw.rect(bubble_surface, (80, 80, 80, opacity), 
                        (0, 0, bubble_width, bubble_height), 2)
        
        surface.blit(bubble_surface, (bubble_x, bubble_y))
        
        # Draw text with opacity
        text_surface.set_alpha(opacity)
        surface.blit(text_surface, (bubble_x + bubble_padding, bubble_y + bubble_padding))
    
    # ============================================
    # Command-related methods
    # ============================================
    
    def go_to_line_position(self, position_index, total_characters):
        """Move character to a position in a line."""
        # Calculate line positions across the screen
        padding = 80
        available_width = config.SCREEN_WIDTH - padding * 2
        spacing = available_width / max(1, total_characters - 1) if total_characters > 1 else available_width
        
        self.target_x = padding + position_index * spacing
        self.target_y = config.SCREEN_HEIGHT // 2 + 50
        self.speed = config.DANCE_SPEED
        self.state = 'lined'
    
    def go_to_pair_position(self, position_index, total_characters):
        """Move character to a position in pairs."""
        # Pair up: (0,1) and (2,3)
        pair_index = position_index // 2
        in_pair = position_index % 2  # 0 = left in pair, 1 = right in pair
        
        center_x = config.SCREEN_WIDTH // 2
        pair_spacing = 200
        pair_offset = (pair_index - (total_characters // 2 - 1) / 2) * pair_spacing
        
        if in_pair == 0:
            self.target_x = center_x + pair_offset - 60
        else:
            self.target_x = center_x + pair_offset + 60
        self.target_y = config.SCREEN_HEIGHT // 2 + 50
        self.speed = config.DANCE_SPEED
        self.state = 'playing'
    
    def start_dancing(self):
        """Start dancing animation."""
        self.state = 'dancing'
        self.speed = config.DANCE_SPEED
    
    def go_to_random_position(self):
        """Move to a random position on screen."""
        self.target_x = random.randint(100, config.SCREEN_WIDTH - 100)
        self.target_y = random.randint(200, config.SCREEN_HEIGHT - 150)
        self.speed = config.DANCE_SPEED
        self.return_to_idle()
    
    def go_to_original_position(self):
        """Return to original starting position."""
        self.target_x = self.original_x
        self.target_y = self.original_y
        self.speed = config.DEFAULT_CHARACTER_SPEED
        self.return_to_idle()


def create_characters():
    """Create all game characters."""
    return [
        Character("Fifi", config.PERSONALITY_FRIENDLY, config.FIFI_COLOR, 150, 350),
        Character("Shyel", config.PERSONALITY_SHY, config.SHYEL_COLOR, 300, 400),
        Character("Grump", config.PERSONALITY_GRUMPY, config.GRUMP_COLOR, 500, 350),
        Character("Pippin", config.PERSONALITY_PLAYFUL, config.PIPPIN_COLOR, 650, 400)
    ]
