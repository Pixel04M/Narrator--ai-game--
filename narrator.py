"""
Narrator System for Virtual Pet Game
=====================================
Narrator class that comments on character actions,
provides hints, and story narration.
"""

import random
import pygame
import config


class Narrator:
    """Narrator that provides commentary on the game."""
    
    def __init__(self):
        # Current narration text
        self.current_text = ""
        self.text_timer = 0
        self.text_duration = 5000  # 5 seconds default
        
        # Text history for variety
        self.last_category = None
        
        # Narrator personality
        self.tone = "friendly"  # friendly, mysterious, playful
        
        # Message queues
        self.message_queue = []
        
        # Hint system
        self.hint_cooldown = 0
        self.last_hint_time = 0
    
    def set_text(self, text, duration=None):
        """Set narrator text to display."""
        self.current_text = text
        self.text_timer = pygame.time.get_ticks()
        self.text_duration = duration if duration else 5000
    
    def queue_message(self, text, priority=False):
        """Add a message to the queue."""
        if priority:
            self.message_queue.insert(0, text)
        else:
            self.message_queue.append(text)
    
    def update(self, characters, world, current_time):
        """Update narrator state and generate commentary."""
        
        # Process message queue
        if not self.current_text and self.message_queue:
            self.set_text(self.message_queue.pop(0))
        
        # Check if current text has expired
        if self.current_text and current_time - self.text_timer > self.text_duration:
            self.current_text = ""
        
        # Generate contextual commentary
        self.generate_commentary(characters, world, current_time)
        
        # Generate hints
        self.generate_hints(characters, world, current_time)
    
    def generate_commentary(self, characters, world, current_time):
        """Generate contextual commentary based on game state."""
        
        # Don't override important messages
        if self.current_text and current_time - self.text_timer < 3000:
            return
        
        for char in characters:
            # Check for notable states
            
            # Hungry commentary
            if char.hunger > 70 and random.random() < 0.01:
                self.set_text(f"{char.name} looks hungry... maybe there's food somewhere?", 4000)
                return
            
            # Tired commentary
            if char.energy < 20 and random.random() < 0.01:
                self.set_text(f"{char.name} is getting sleepy. A bed would be nice right now.", 4000)
                return
            
            # Happy commentary
            if char.happiness > 80 and random.random() < 0.005:
                self.set_text(f"{char.name} is having a great time!", 3500)
                return
            
            # Interaction with objects
            if hasattr(char, 'last_interaction_object') and char.last_interaction_object:
                obj_time = getattr(char, 'last_interaction_time', 0)
                if current_time - obj_time < 2000:
                    obj = char.last_interaction_object
                    if obj:
                        self.set_text(obj.get_interaction_message(char), 3500)
                        char.last_interaction_object = None
                        return
            
            # Meeting other characters
            if hasattr(char, 'last_meeting_time'):
                meeting_time = char.last_meeting_time
                if current_time - meeting_time < 3000 and random.random() < 0.02:
                    # Character recently met someone
                    if hasattr(char, 'last_met_character') and char.last_met_character:
                        other = char.last_met_character
                        if other and other != char:
                            self.set_text(f"{char.name} and {other.name} are chatting!", 3500)
                            return
    
    def generate_hints(self, characters, world, current_time):
        """Generate helpful hints for the player."""
        
        # Only generate hints occasionally
        if current_time - self.last_hint_time < self.hint_cooldown:
            return
        
        # Check if any character needs help
        for char in characters:
            # Hint: food
            if char.hunger > 60:
                nearby_food = world.get_nearest_object("food_bowl", char.x, char.y, 300)
                if nearby_food:
                    self.set_text(f"Hint: {char.name} could use some food. There might be a food bowl nearby...", 5000)
                    self.last_hint_time = current_time
                    self.hint_cooldown = 15000
                    return
            
            # Hint: bed
            if char.energy < 30:
                nearby_bed = world.get_nearest_object("bed", char.x, char.y, 400)
                if nearby_bed:
                    self.set_text(f"Hint: {char.name} is tired. Maybe there's a bed somewhere to rest?", 5000)
                    self.last_hint_time = current_time
                    self.hint_cooldown = 15000
                    return
            
            # Hint: toy for bored character
            if char.happiness < 30:
                nearby_toy = world.get_nearest_object("toy", char.x, char.y, 300)
                if nearby_toy:
                    self.set_text(f"Hint: {char.name} seems bored. A toy might help!", 5000)
                    self.last_hint_time = current_time
                    self.hint_cooldown = 15000
                    return
    
    def get_text(self):
        """Get current narrator text."""
        return self.current_text    
    def draw(self, surface, current_time):
        """Draw narrator text box at bottom of screen."""
        if not self.current_text:
            return
        
        # Calculate text position (above input box)
        font = pygame.font.Font(None, 26)
        text_surface = font.render(self.current_text, True, (50, 50, 50))
        
        # Box dimensions
        box_width = min(text_surface.get_width() + 40, config.SCREEN_WIDTH - 40)
        box_height = text_surface.get_height() + 20
        box_x = (config.SCREEN_WIDTH - box_width) // 2
        box_y = config.SCREEN_HEIGHT - config.INPUT_BOX_HEIGHT - config.INPUT_BOX_MARGIN - box_height - 10
        
        # Draw box background
        bg_rect = pygame.Rect(box_x, box_y, box_width, box_height)
        pygame.draw.rect(surface, (255, 250, 240), bg_rect)
        pygame.draw.rect(surface, (180, 160, 120), bg_rect, 2)
        
        # Draw narrator indicator
        narrator_label = pygame.font.Font(None, 20).render("Narrator:", True, (100, 80, 60))
        surface.blit(narrator_label, (box_x + 10, box_y + 5))
        
        # Draw text
        surface.blit(text_surface, (box_x + 10, box_y + 22))
    
    # ============================================
    # Pre-defined narration messages
    # ============================================
    
    INTRO_MESSAGES = [
        "Welcome to the world! Your pets are waiting for you.",
        "The world is big - use your mouse to explore!",
        "Click on your pets to interact with them.",
        "Watch your pets' needs - hunger, energy, and happiness!"
    ]
    
    DISCOVERY_MESSAGES = [
        "{name} discovered a new area!",
        "{name} found something interesting!",
        "The group is exploring together.",
        "{name} is leading the way!"
    ]
    
    INTERACTION_MESSAGES = [
        "{name} is using the {object}!",
        "{name} found something useful!",
        "That looks like fun!",
        "{name} seems happy with that."
    ]
    
    MEETING_MESSAGES = [
        "{name} met {other}!",
        "{name} and {other} are talking.",
        "The pets are socializing!",
        "{name} shared something with {other}."
    ]
    
    def play_intro(self):
        """Play an intro message."""
        self.set_text(random.choice(self.INTRO_MESSAGES), 6000)
    
    def announce_discovery(self, name):
        """Announce a discovery."""
        msg = random.choice(self.DISCOVERY_MESSAGES).format(name=name)
        self.set_text(msg, 4000)
    
    def announce_interaction(self, name, object_type):
        """Announce an object interaction."""
        msg = random.choice(self.INTERACTION_MESSAGES).format(name=name, object=object_type)
        self.set_text(msg, 3500)
    
    def announce_meeting(self, name, other_name):
        """Announce a meeting between characters."""
        msg = random.choice(self.MEETING_MESSAGES).format(name=name, other=other_name)
        self.set_text(msg, 4000)