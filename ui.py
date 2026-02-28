"""
UI Elements for Virtual Pet Game
=================================
Contains input box, speech bubbles, and other UI components.
"""

import pygame
import config


class InputBox:
    """Text input box for player messages with multi-line support."""
    
    def __init__(self, x=None, y=None, width=None, height=None):
        if x is None:
            x = config.INPUT_BOX_MARGIN
        if y is None:
            y = config.SCREEN_HEIGHT - config.INPUT_BOX_HEIGHT - config.INPUT_BOX_MARGIN
        if width is None:
            width = config.SCREEN_WIDTH - config.INPUT_BOX_MARGIN * 2
        if height is None:
            height = config.INPUT_BOX_HEIGHT * 3  # Make taller for multi-line
            
        self.rect = pygame.Rect(x, y, width, height)
        self.text = ""
        self.active = False
        self.font = pygame.font.Font(None, 26)
        self.placeholder = "Type a message... (/all for global, /help for commands)"
        self.max_length = 200
    
    def _wrap_text(self, text):
        """Wrap text to fit within the box width."""
        if not text:
            return []
        
        words = text.split()
        lines = []
        current_line = []
        max_width = self.rect.width - 30  # Leave padding
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            test_surface = self.font.render(test_line, True, (30, 30, 30))
            
            if test_surface.get_width() <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]
        
        if current_line:
            lines.append(' '.join(current_line))
        
        return lines
    
    def handle_event(self, event):
        """Handle keyboard events for the input box."""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                # Return text if not empty
                if self.text.strip():
                    text = self.text.strip()
                    self.text = ""
                    return text
                return None
            elif event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif event.key == pygame.K_ESCAPE:
                self.active = False
                return "escape"
            else:
                # Add typed character
                if len(self.text) < self.max_length:
                    self.text += event.unicode
        return None
    
    def set_active(self, active):
        """Set input box active state."""
        self.active = active
    
    def is_clicked(self, pos):
        """Check if input box was clicked."""
        return self.rect.collidepoint(pos)
    
    def draw(self, surface):
        """Draw the input box with multi-line text."""
        # Box background
        if self.active:
            box_color = config.INPUT_BOX_COLOR
            border_color = config.SELECTED_GLOW
            border_width = 3
        else:
            box_color = (240, 240, 240)
            border_color = config.INPUT_BOX_BORDER
            border_width = 2
        
        pygame.draw.rect(surface, box_color, self.rect)
        pygame.draw.rect(surface, border_color, self.rect, border_width)
        
        # Draw wrapped text or placeholder
        if self.text:
            lines = self._wrap_text(self.text)
            y_offset = self.rect.y + 8
            for line in lines[:5]:  # Show max 5 lines
                text_surface = self.font.render(line, True, (30, 30, 30))
                surface.blit(text_surface, (self.rect.x + 10, y_offset))
                y_offset += self.font.get_height() + 4
        else:
            placeholder_surface = self.font.render(self.placeholder, True, (150, 150, 150))
            surface.blit(placeholder_surface, (self.rect.x + 10, self.rect.y + 10))


class CommandSystem:
    """Handle game commands like /line, /pairs, /dance, /scatter."""
    
    def __init__(self):
        self.commands = {
            "/line": self.cmd_line,
            "/pairs": self.cmd_pairs,
            "/dance": self.cmd_dance,
            "/scatter": self.cmd_scatter,
            "/explore": self.cmd_explore,
            "/help": self.cmd_help,
            "/reset": self.cmd_reset,
            # Alternative command names
            "line": self.cmd_line,
            "pairs": self.cmd_pairs,
            "dance": self.cmd_dance,
            "scatter": self.cmd_scatter,
            "explore": self.cmd_explore,
            "help": self.cmd_help,
            "reset": self.cmd_reset,
        }
        
        # Natural language commands
        self.natural_commands = {
            "get in a line": self.cmd_line,
            "line up": self.cmd_line,
            "form a line": self.cmd_line,
            "pair up": self.cmd_pairs,
            "pair": self.cmd_pairs,
            "dance": self.cmd_dance,
            "dance together": self.cmd_dance,
            "scatter": self.cmd_scatter,
            "random": self.cmd_scatter,
            "explore": self.cmd_explore,
            "explore the world": self.cmd_explore,
            "go explore": self.cmd_explore,
            "help": self.cmd_help,
            "commands": self.cmd_help,
            "reset": self.cmd_reset,
            "go back": self.cmd_reset,
            "original positions": self.cmd_reset,
        }
    
    def parse_command(self, text):
        """Parse text to check if it's a command."""
        text = text.strip().lower()
        
        # Check for exact command match
        if text in self.commands:
            return self.commands[text], []
        
        # Check for command with arguments (e.g., "/line arg")
        parts = text.split()
        if parts and parts[0] in self.commands:
            return self.commands[parts[0]], parts[1:]
        
        # Check for natural language commands
        for key, cmd in self.natural_commands.items():
            if key in text:
                return cmd, []
        
        return None, []
    
    def execute_command(self, command_func, characters, args=None, world=None):
        """Execute a command on all characters."""
        if command_func:
            # Check if command needs world parameter
            import inspect
            sig = inspect.signature(command_func)
            if 'world' in sig.parameters:
                return command_func(characters, world)
            return command_func(characters)
        return None
    
    def cmd_line(self, characters):
        """Command: Line up all characters."""
        for i, char in enumerate(characters):
            char.go_to_line_position(i, len(characters))
        return "Characters are lining up!"
    
    def cmd_pairs(self, characters):
        """Command: Pair up characters."""
        for i, char in enumerate(characters):
            char.go_to_pair_position(i, len(characters))
        return "Characters are pairing up!"
    
    def cmd_dance(self, characters):
        """Command: Make all characters dance."""
        for char in characters:
            char.start_dancing()
        return "Let's dance! 💃🕺"
    
    def cmd_scatter(self, characters):
        """Command: Random positions."""
        for char in characters:
            char.go_to_random_position()
        return "Scattering to random positions!"
    
    def cmd_explore(self, characters, world=None):
        """Command: Explore the world."""
        if world:
            for char in characters:
                char.explore(world)
            return "The characters are exploring the world!"
        return "World not available for exploration."
    
    def cmd_reset(self, characters):
        """Command: Return to original positions."""
        for char in characters:
            char.go_to_original_position()
        return "Returning to original positions!"
    
    def cmd_reset(self, characters):
        """Command: Return to original positions."""
        for char in characters:
            char.go_to_original_position()
        return "Returning to original positions!"
    
    def cmd_help(self, characters):
        """Command: Show help."""
        return (
            "Commands:\n"
            "/line - Line up\n"
            "/pairs - Pair up\n"
            "/dance - Dance together\n"
            "/scatter - Random positions\n"
            "/explore - Explore the world\n"
            "/reset - Return to original positions\n"
            "/all <msg> - Ask all characters"
        )


def draw_background(surface):
    """Draw the room background."""
    # Wall
    surface.fill(config.WALL_COLOR)
    
    # Floor
    floor_rect = pygame.Rect(0, config.SCREEN_HEIGHT - 150, config.SCREEN_WIDTH, 150)
    pygame.draw.rect(surface, config.FLOOR_COLOR, floor_rect)
    
    # Floor line
    pygame.draw.line(surface, (100, 60, 20), 
                    (0, config.SCREEN_HEIGHT - 150), 
                    (config.SCREEN_WIDTH, config.SCREEN_HEIGHT - 150), 3)
    
    # Window (decorative)
    win_x, win_y, win_w, win_h = config.WINDOW_RECT
    pygame.draw.rect(surface, (200, 220, 250), (win_x, win_y, win_w, win_h))
    pygame.draw.rect(surface, (150, 150, 150), (win_x, win_y, win_w, win_h), 3)
    # Window frame
    pygame.draw.line(surface, (150, 150, 150), (win_x + win_w//2, win_y), (win_x + win_w//2, win_y + win_h), 2)
    pygame.draw.line(surface, (150, 150, 150), (win_x, win_y + win_h//2), (win_x + win_w, win_y + win_h//2), 2)
    
    # Simple picture frame on wall
    pic_x, pic_y, pic_w, pic_h = config.PICTURE_FRAME_RECT
    pygame.draw.rect(surface, (180, 150, 100), (pic_x, pic_y, pic_w, pic_h))
    pygame.draw.rect(surface, (100, 80, 50), (pic_x, pic_y, pic_w, pic_h), 2)
    
    # Plant pot (decorative)
    plant_x, plant_y = config.PLANT_POSITION
    pygame.draw.polygon(surface, (180, 100, 50), 
                       [(plant_x - 30, plant_y), (plant_x, plant_y), (plant_x + 10, plant_y + 40), (plant_x - 20, plant_y + 40)])
    # Plant leaves
    pygame.draw.ellipse(surface, (50, 150, 50), (plant_x - 30, plant_y - 20, 20, 30))
    pygame.draw.ellipse(surface, (50, 150, 50), (plant_x - 10, plant_y - 30, 20, 30))
    pygame.draw.ellipse(surface, (50, 150, 50), (plant_x + 5, plant_y - 20, 20, 30))


def draw_ui_overlay(surface, font, input_font, selected_character, ai_chat, current_time):
    """Draw UI elements like instructions, status, and selected character info."""
    
    # Draw instructions
    instruction_text = "Click character to select • Type message • Enter to chat • /all for global • /help for commands"
    instruction_surface = font.render(instruction_text, True, (80, 60, 40))
    surface.blit(instruction_surface, (20, 10))
    
    # Draw AI status indicator
    if ai_chat and ai_chat.is_available:
        if ai_chat.is_thinking:
            ai_status = "🤖 AI Thinking..."
            ai_color = (100, 100, 200)
        else:
            ai_status = "🤖 AI Enabled"
            ai_color = (50, 150, 50)
    else:
        ai_status = "📝 Rule-based Mode"
        ai_color = (120, 120, 120)
    ai_status_surface = input_font.render(ai_status, True, ai_color)
    surface.blit(ai_status_surface, (config.SCREEN_WIDTH - ai_status_surface.get_width() - 20, 15))
    
    # Draw selected character indicator
    if selected_character:
        selection_text = f"Chatting with {selected_character.name} ({selected_character.personality.capitalize()})"
        selection_surface = input_font.render(selection_text, True, (50, 100, 50))
        surface.blit(selection_surface, (config.SCREEN_WIDTH // 2 - selection_surface.get_width() // 2, 
                                          config.SCREEN_HEIGHT - config.INPUT_BOX_HEIGHT - config.INPUT_BOX_MARGIN - 30))
        
        # Draw relationship indicator
        if hasattr(selected_character, 'player_relationship'):
            rel = selected_character.player_relationship
            rel_level = selected_character.get_relationship_level()
            
            # Determine relationship color
            if rel >= 70:
                rel_color = (200, 50, 100)
                rel_emoji = "❤️"
            elif rel >= 40:
                rel_color = (100, 150, 50)
                rel_emoji = "💚"
            elif rel >= 20:
                rel_color = (150, 150, 50)
                rel_emoji = "💛"
            else:
                rel_color = (150, 50, 50)
                rel_emoji = "💔"
            
            level_str = rel_level.replace('_', ' ')
            rel_text = f"{rel_emoji} Friendship: {rel}/100 ({level_str})"
            rel_surface = input_font.render(rel_text, True, rel_color)
            surface.blit(rel_surface, (config.SCREEN_WIDTH // 2 - rel_surface.get_width() // 2, 
                                        config.SCREEN_HEIGHT - config.INPUT_BOX_HEIGHT - config.INPUT_BOX_MARGIN - 55))
    else:
        selection_text = "Select a character to chat, or use /all to ask everyone!"
        selection_surface = input_font.render(selection_text, True, (120, 80, 80))
        surface.blit(selection_surface, (config.SCREEN_WIDTH // 2 - selection_surface.get_width() // 2, 
                                          config.SCREEN_HEIGHT - config.INPUT_BOX_HEIGHT - config.INPUT_BOX_MARGIN - 30))


def draw_command_feedback(surface, font, message):
    """Draw command feedback message on screen."""
    if message:
        # Create a semi-transparent background
        text_surface = font.render(message, True, (50, 50, 50))
        bg_rect = text_surface.get_rect(center=(config.SCREEN_WIDTH // 2, 50))
        bg_rect.inflate_ip(20, 10)
        
        # Draw background
        bg_surface = pygame.Surface((bg_rect.width, bg_rect.height), pygame.SRCALPHA)
        bg_surface.fill((255, 255, 255, 200))
        surface.blit(bg_surface, bg_rect)
        
        # Draw border
        pygame.draw.rect(surface, (100, 100, 100), bg_rect, 1)
        
        # Draw text
        surface.blit(text_surface, text_surface.get_rect(center=(config.SCREEN_WIDTH // 2, 50)))
