"""
Virtual Pet Game with AI Personalities and World Exploration
============================================================
A 2D Pygame game featuring 4 characters with distinct AI personalities
in a large explorable world.

Features:
- World exploration with 1600x1200 map
- Camera system following mouse
- Interactive objects (food bowls, beds, toys, trees, rocks)
- Multi-agent communication and memory system
- A* pathfinding
- Narrator commentary
- Minimap
- Android touch support (PGS4A)
- Virtual keyboard support
- Responsive UI for mobile devices
"""

import pygame
import sys
import random
import config
import character as char_module
import ai_chat as chat_module
import ui
import world as world_module
import narrator as narrator_module

# Android-specific imports
ANDROID = False
try:
    import android
    import android.touch as touch
    import android.keyboard as keyboard
    # Check if this is a real PGS4A module or our stub
    if not hasattr(android, '_is_stub'):
        ANDROID = True
except ImportError:
    # Desktop mode - create stub modules
    android = None
    touch = None
    keyboard = None


# Touch gesture state tracking
class TouchGestureState:
    """Track multi-touch gestures for camera control."""
    def __init__(self):
        self.touches = {}  # touch_id -> (x, y)
        self.last_touch_count = 0
        self.pinch_start_distance = None
        self.pinch_start_zoom = 1.0
        self.tap_start_time = None
        self.tap_start_pos = None
        self.long_press_time = 500  # ms for long press
        self.is_long_press = False
        
    def add_touch(self, touch_id, x, y):
        """Add a new touch point."""
        self.touches[touch_id] = {
            'pos': (x, y),
            'start_time': pygame.time.get_ticks(),
            'start_pos': (x, y)
        }
        
    def update_touch(self, touch_id, x, y):
        """Update an existing touch point."""
        if touch_id in self.touches:
            self.touches[touch_id]['pos'] = (x, y)
            
    def remove_touch(self, touch_id):
        """Remove a touch point."""
        if touch_id in self.touches:
            del self.touches[touch_id]
            
    def get_touch_count(self):
        """Get number of active touches."""
        return len(self.touches)
    
    def get_centroid(self):
        """Get the center point of all touches."""
        if not self.touches:
            return None
        avg_x = sum(t['pos'][0] for t in self.touches.values()) / len(self.touches)
        avg_y = sum(t['pos'][1] for t in self.touches.values()) / len(self.touches)
        return (avg_x, avg_y)
    
    def get_pinch_distance(self):
        """Get distance between two fingers for pinch zoom."""
        if len(self.touches) < 2:
            return None
        touch_list = list(self.touches.values())
        t1, t2 = touch_list[0], touch_list[1]
        dx = t1['pos'][0] - t2['pos'][0]
        dy = t1['pos'][1] - t2['pos'][1]
        return (dx**2 + dy**2) ** 0.5
    
    def is_tap(self, touch_id, max_distance=20, max_time=300):
        """Check if a touch is a tap (short duration, minimal movement)."""
        if touch_id not in self.touches:
            return False
        t = self.touches[touch_id]
        current_time = pygame.time.get_ticks()
        
        dx = t['pos'][0] - t['start_pos'][0]
        dy = t['pos'][1] - t['start_pos'][1]
        distance = (dx**2 + dy**2) ** 0.5
        
        elapsed = current_time - t['start_time']
        
        return distance < max_distance and elapsed < max_time
    
    def is_long_press(self, touch_id):
        """Check if a touch is a long press."""
        if touch_id not in self.touches:
            return False
        t = self.touches[touch_id]
        elapsed = pygame.time.get_ticks() - t['start_time']
        
        dx = t['pos'][0] - t['start_pos'][0]
        dy = t['pos'][1] - t['start_pos'][1]
        distance = (dx**2 + dy**2) ** 0.5
        
        return elapsed > self.long_press_time and distance < 30


# Global touch state
gesture_state = TouchGestureState()


def detect_android_screen_size():
    """Detect screen dimensions on Android and return responsive size."""
    if ANDROID and android:
        try:
            width = android.device.screen_width
            height = android.device.screen_height
            return width, height
        except:
            pass
    return config.SCREEN_WIDTH, config.SCREEN_HEIGHT


def get_responsive_scale():
    """Calculate UI scale factor based on screen size."""
    base_width = 800
    base_height = 600
    
    screen_width, screen_height = detect_android_screen_size()
    
    # Use the larger dimension ratio for scaling
    width_scale = screen_width / base_width
    height_scale = screen_height / base_height
    
    # Use the smaller scale to ensure UI fits
    return min(width_scale, height_scale)


def toggle_fullscreen(screen, current_flags):
    """Toggle between fullscreen and windowed mode.

    Args:
        screen: The pygame display surface
        current_flags: Current display flags

    Returns:
        tuple: (new_screen, new_flags)
    """
    if current_flags & pygame.FULLSCREEN:
        # Exit fullscreen - return to fixed window
        new_flags = pygame.RESIZABLE
        new_screen = pygame.display.set_mode(
            (config.SCREEN_WIDTH, config.SCREEN_HEIGHT), new_flags)
    else:
        # Enter fullscreen using SCALED so the 800x600 game
        # is hardware-scaled to any screen without black bars or lag
        new_flags = pygame.FULLSCREEN | pygame.SCALED
        new_screen = pygame.display.set_mode(
            (config.SCREEN_WIDTH, config.SCREEN_HEIGHT), new_flags)
    return new_screen, new_flags


def main(android_mode=False):
    """Main game function.
    
    Args:
        android_mode: If True, enables Android-specific features like
                      touch controls and virtual keyboard.
    """
    # Initialize Pygame
    pygame.init()
    
    # Determine screen size (use Android device size if available)
    if android_mode and ANDROID:
        screen_width, screen_height = detect_android_screen_size()
    else:
        screen_width, screen_height = config.SCREEN_WIDTH, config.SCREEN_HEIGHT
    
    # Set up screen - start fullscreen using SCALED (scales 800x600 to any monitor)
    display_flags = pygame.FULLSCREEN | pygame.SCALED
    screen = pygame.display.set_mode((screen_width, screen_height), display_flags)
    pygame.display.set_caption(config.GAME_CAPTION)
    
    # Create clock
    clock = pygame.time.Clock()
    
    # Create fonts with responsive sizing
    scale = get_responsive_scale() if android_mode else 1
    font_size = max(20, int(28 * scale))
    input_font_size = max(18, int(26 * scale))
    
    font = pygame.font.Font(None, font_size)
    input_font = pygame.font.Font(None, input_font_size)
    
    # Create AI chat system
    ai_chat = chat_module.AIChat()
    
    # Print AI status
    print("="*50)
    if ai_chat.is_available:
        print("AI Chat: Enabled (using Fireworks AI)")
    else:
        print("AI Chat: Disabled / Using rule-based responses")
    print("="*50)
    if config.USE_AI_CHAT and not ai_chat.is_available:
        print("To enable AI chat:")
        print("  - Get a free API key from https://fireworks.ai")
        print("  - Set environment: export FIREWORKS_API_KEY='your-key'")
        print("  - Or edit config.py to set FIREWORKS_API_KEY directly")
        print("="*50)
    
    # Create chat system with AI integration
    chat_system = chat_module.ChatSystem(ai_chat=ai_chat)
    
    # Track AI thinking state for loading indicator
    ai_thinking_character = [None]
    ai_response_pending = [None]
    global_ai_responses_pending = [None]
    
    # Create world
    game_world = world_module.World(config.WORLD_WIDTH, config.WORLD_HEIGHT)
    
    # Create narrator
    narrator = narrator_module.Narrator()
    narrator.play_intro()
    
    # Create characters with world reference
    characters = char_module.create_characters()
    
    # Assign world reference and AI chat reference to characters
    for char in characters:
        char.world = game_world
        char._ai_chat_ref = ai_chat  # enables agent-to-agent AI dialogue
    
    # Track selected character
    selected_character = None
    
    # Create input box with responsive sizing
    input_box = ui.InputBox()
    
    # Create command system
    command_system = ui.CommandSystem()
    
    # Command feedback message
    command_feedback = ""
    command_feedback_timer = 0
    
    # Minimap
    minimap = world_module.Minimap(game_world)
    
    # Initialize touch gesture state
    touch_state = TouchGestureState()
    
    # Game loop
    running = True
    
    # Track previous touch state for gesture detection
    prev_touch_positions = {}
    
    while running:
        # Get current time
        current_time = pygame.time.get_ticks()
        
        # Event handling
        events = pygame.event.get()
        
        for event in events:
            # Handle Android touch events
            if android_mode and ANDROID and event.type == android.TOUCHDOWN:
                touch_id = event.touch_id
                x, y = event.x, event.y
                
                # Add touch to gesture state
                touch_state.add_touch(touch_id, x, y)
                prev_touch_positions[touch_id] = (x, y)
                
                # Handle single tap for character selection
                if touch_state.get_touch_count() == 1:
                    touch_state.tap_start_time = current_time
                    touch_state.tap_start_pos = (x, y)
                    
            elif android_mode and ANDROID and event.type == android.TOUCHUP:
                touch_id = event.touch_id
                
                # Check for tap gesture
                if touch_id in prev_touch_positions:
                    start_pos = prev_touch_positions[touch_id]
                    
                    # Single tap - treat as character selection
                    if touch_state.is_tap(touch_id):
                        mouse_pos = start_pos
                        
                        # Check if tapping on input box
                        if input_box.is_clicked(mouse_pos):
                            input_box.set_active(True)
                            # Show virtual keyboard
                            if ANDROID:
                                try:
                                    android.show_keyboard()
                                except:
                                    pass
                        else:
                            input_box.set_active(False)
                            if ANDROID:
                                try:
                                    android.hide_keyboard()
                                except:
                                    pass
                            
                            # Convert to world coordinates
                            world_mouse = game_world.camera.screen_to_world(mouse_pos[0], mouse_pos[1])
                            
                            # Check if tapping on a character
                            clicked_character = None
                            for char in characters:
                                if char.handle_click(world_mouse):
                                    clicked_character = char
                                    char.on_clicked()
                                    break
                            
                            # Select the clicked character
                            if clicked_character:
                                for char in characters:
                                    char.is_selected = False
                                clicked_character.is_selected = True
                                selected_character = clicked_character
                            elif not input_box.active:
                                # Tap on empty space - start camera drag
                                for char in characters:
                                    char.is_selected = False
                                selected_character = None
                                game_world.camera.start_drag(mouse_pos)
                
                # Remove touch
                if touch_id in prev_touch_positions:
                    del prev_touch_positions[touch_id]
                touch_state.remove_touch(touch_id)
                
            elif android_mode and ANDROID and event.type == android.TOUCHMOTION:
                touch_id = event.touch_id
                x, y = event.x, event.y
                
                # Update touch position
                touch_state.update_touch(touch_id, x, y)
                
                # Handle multi-touch for camera panning
                if touch_id in prev_touch_positions:
                    prev_x, prev_y = prev_touch_positions[touch_id]
                    
                    # Single finger drag - camera panning
                    if touch_state.get_touch_count() == 1:
                        dx = x - prev_x
                        dy = y - prev_y
                        
                        # If camera is being dragged, update position
                        if game_world.camera.is_dragging:
                            game_world.camera.drag_offset_x += dx
                            game_world.camera.drag_offset_y += dy
                    
                    # Two finger drag - pan camera
                    elif touch_state.get_touch_count() >= 2:
                        # Calculate centroid movement
                        prev_centroid = None
                        if len(prev_touch_positions) >= 2:
                            touch_items = list(prev_touch_positions.items())
                            t1 = touch_items[0]
                            t2 = touch_items[1]
                            prev_centroid = (
                                (t1[1][0] + t2[1][0]) / 2,
                                (t1[1][1] + t2[1][1]) / 2
                            )
                        
                        if prev_centroid:
                            dx = x - prev_centroid[0]
                            dy = y - prev_centroid[1]
                            game_world.camera.drag_offset_x += dx
                            game_world.camera.drag_offset_y += dy
                    
                    prev_touch_positions[touch_id] = (x, y)
            
            # Handle pinch zoom (optional feature)
            elif android_mode and ANDROID and hasattr(android, 'PINCH'):
                if event.type == android.PINCH:
                    scale_factor = event.scale
                    # Apply zoom to camera
                    game_world.camera.zoom *= scale_factor
                    game_world.camera.zoom = max(0.5, min(2.0, game_world.camera.zoom))
            
            # Handle keyboard events (including virtual keyboard)
            if event.type == pygame.KEYDOWN:
                # Handle F11 for fullscreen toggle
                if event.key == pygame.K_F11:
                    screen, display_flags = toggle_fullscreen(screen, display_flags)
                
                # Handle input box events
                result = input_box.handle_event(event)
                
                if result == "escape":
                    # If in fullscreen, exit fullscreen first
                    if display_flags & pygame.FULLSCREEN:
                        screen, display_flags = toggle_fullscreen(screen, display_flags)
                    else:
                        # Deselect character on ESC
                        selected_character = None
                        for char in characters:
                            char.is_selected = False
                        input_box.set_active(False)
                        # Hide virtual keyboard
                        if android_mode and ANDROID:
                            try:
                                android.hide_keyboard()
                            except:
                                pass
                elif result and isinstance(result, str):
                    # User pressed Enter with text
                    message = result
                    
                    # Check for global chat prefix
                    if message.startswith(config.GLOBAL_CHAT_PREFIX):
                        # Global chat - all characters respond
                        global_message = message[len(config.GLOBAL_CHAT_PREFIX):].strip()
                        
                        if global_message:
                            # Convert mouse position to world coordinates for actions
                            mouse_pos = pygame.mouse.get_pos()
                            world_mouse = game_world.camera.screen_to_world(mouse_pos[0], mouse_pos[1])
                            
                            # Check for action commands first
                            action, confidence = chat_system.action_detector.detect_action(global_message)
                            
                            if action and confidence > 0:
                                # Execute the action on all characters
                                for char in characters:
                                    action_message = char.do_action(action, game_world, world_mouse)
                                    char.set_speech_bubble(action_message, current_time)
                                
                                # Update narrator
                                narrator_action_comments = {
                                    'sleep': "Everyone is going to sleep... Goodnight!",
                                    'eat': "Everyone is hungry! They head to find food...",
                                    'play': "It's playtime! Everyone looks for toys!",
                                    'dance': "The party starts! Everyone begins dancing!",
                                    'follow': "The group decides to follow together!",
                                    'come': "Everyone comes running over!",
                                    'stay': "Everyone decides to stay put..."
                                }
                                if action in narrator_action_comments:
                                    narrator.set_text(narrator_action_comments[action], 3000)
                            else:
                                # Normal global chat - process sentiment for all characters
                                for char in characters:
                                    char.process_player_message(global_message)
                                
                                # Show loading indicator on all characters temporarily
                                loading_msg = chat_module.config.AI_LOADING_MESSAGES[0]
                                for char in characters:
                                    char.set_speech_bubble(loading_msg, current_time)
                                    ai_thinking_character[0] = char
                                
                                # Generate global responses
                                chat_system.generate_global_responses(
                                    global_message,
                                    characters,
                                    lambda responses: global_ai_responses_pending.__setitem__(0, responses)
                                )
                    
                    # Check for commands
                    elif message.startswith(config.COMMAND_PREFIX) or any(
                        message.lower().startswith(cmd) for cmd in command_system.natural_commands.keys()
                    ):
                        # It's a command
                        cmd_func, args = command_system.parse_command(message)
                        if cmd_func:
                            feedback = command_system.execute_command(cmd_func, characters, args, game_world)
                            command_feedback = feedback
                            command_feedback_timer = 180
                        else:
                            # Unknown command
                            command_feedback = "Unknown command. Type /help for available commands."
                            command_feedback_timer = 120
                    
                    # Specific character chat (when selected)
                    elif selected_character:
                        # Convert mouse position to world coordinates for actions
                        mouse_pos = pygame.mouse.get_pos()
                        world_mouse = game_world.camera.screen_to_world(mouse_pos[0], mouse_pos[1])
                        
                        # Check for action commands first
                        action, confidence = chat_system.action_detector.detect_action(message)
                        
                        if action and confidence > 0:
                            # Execute the action
                            action_message = selected_character.do_action(action, game_world, world_mouse)
                            selected_character.set_speech_bubble(action_message, current_time)
                            
                            # Update narrator to comment on the action
                            narrator_action_comments = {
                                'sleep': f"{selected_character.name} heads off to find a bed...",
                                'eat': f"{selected_character.name} looks hungry and heads to find food...",
                                'play': f"{selected_character.name} gets excited and searches for toys...",
                                'dance': f"{selected_character.name} starts dancing! How fun!",
                                'follow': f"{selected_character.name} decides to follow the player...",
                                'come': f"{selected_character.name} comes running over!",
                                'stay': f"{selected_character.name} decides to stay put..."
                            }
                            if action in narrator_action_comments:
                                narrator.set_text(narrator_action_comments[action], 3000)
                            
                            # Update interaction time
                            selected_character.last_interaction_time = current_time
                        else:
                            # Normal chat processing
                            # Process sentiment of player message and update relationship
                            sentiment, rel_change, sentiment_response = selected_character.process_player_message(message)
                            
                            # Immediately show that we're waiting for response
                            waiting_messages = ["Thinking...", "Hmm...", "Let me think...", "One moment..."]
                            selected_character.set_speech_bubble(random.choice(waiting_messages), current_time)
                            
                            # Check if AI is available and enabled
                            if ai_chat.is_available:
                                # Capture the character NOW so the lambda always
                                # refers to the right character even if the player
                                # clicks someone else before the AI replies.
                                _char = selected_character
                                _fallback = sentiment_response
                                chat_system.generate_response_async(
                                    _char,
                                    message,
                                    lambda resp, c=_char, fb=_fallback: (
                                        ai_response_pending.__setitem__(0, (
                                            c,
                                            chat_system.handle_ai_response(c, resp) or fb
                                        ))
                                    ),
                                    characters
                                )
                            else:
                                # Use rule-based response with sentiment adjustment
                                response = chat_system.generate_response(selected_character, message)
                                # Mix in sentiment response
                                final_response = f"{sentiment_response} {response}"
                                selected_character.set_speech_bubble(final_response, current_time)
                            
                            selected_character.last_interaction_time = current_time
                    
                    # No character selected and not a command
                    else:
                        command_feedback = "Select a character first, or use /all <message> to ask everyone!"
                        command_feedback_timer = 120
                    
                    # Hide keyboard after sending message
                    if android_mode and ANDROID:
                        try:
                            android.hide_keyboard()
                        except:
                            pass
            
            # Handle mouse clicks (desktop)
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                
                # Check if clicking on input box first (highest priority)
                if input_box.is_clicked(mouse_pos):
                    input_box.set_active(True)
                    # Show virtual keyboard on Android
                    if android_mode and ANDROID:
                        try:
                            android.show_keyboard()
                        except:
                            pass
                else:
                    input_box.set_active(False)
                    # Hide virtual keyboard
                    if android_mode and ANDROID:
                        try:
                            android.hide_keyboard()
                        except:
                            pass
                    
                    # Check if clicking on a character (only if not clicking input box)
                    if event.button == 1:  # Left click
                        # Convert to world coordinates
                        world_mouse = game_world.camera.screen_to_world(mouse_pos[0], mouse_pos[1])
                        
                        clicked_character = None
                        for char in characters:
                            if char.handle_click(world_mouse):
                                clicked_character = char
                                char.on_clicked()
                                break
                        
                        # Select the clicked character (if clicked on one)
                        if clicked_character:
                            # Deselect previous
                            for char in characters:
                                char.is_selected = False
                            # Select new character
                            clicked_character.is_selected = True
                            selected_character = clicked_character
                        elif not input_box.active:
                            # Clicked elsewhere - deselect
                            for char in characters:
                                char.is_selected = False
                            selected_character = None
                            # Start camera drag for scrolling
                            game_world.camera.start_drag(mouse_pos)
                
                # Right click - center camera on world
                if event.button == 3:
                    game_world.camera.set_mode("center")
            
            # Handle mouse motion for camera dragging
            if event.type == pygame.MOUSEMOTION:
                mouse_pos = pygame.mouse.get_pos()
                # Update drag if dragging
                if game_world.camera.is_dragging:
                    game_world.camera.update_drag(mouse_pos)
            
            # Handle mouse button up
            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:  # Left button
                    game_world.camera.end_drag()
            
            # Handle quit event (Android back button)
            if event.type == pygame.QUIT:
                # Exit fullscreen before quitting if needed
                if display_flags & pygame.FULLSCREEN:
                    screen, display_flags = toggle_fullscreen(screen, display_flags)
                running = False
            
            # Handle Android back button
            if android_mode and ANDROID and hasattr(pygame, 'ANDROID_BACK'):
                if event.type == pygame.ANDROID_BACK:
                    # Show exit confirmation or just quit
                    running = False
        
        # Get mouse position for AI and camera
        mouse_pos = pygame.mouse.get_pos()
        
        # Update world (camera)
        game_world.update(mouse_pos)
        
        # Update narrator
        narrator.update(characters, game_world, current_time)
        
        # Check for pending AI responses (single character)
        if ai_response_pending[0]:
            char, response = ai_response_pending[0]
            if char and response:
                char.set_speech_bubble(response, current_time)
            ai_response_pending[0] = None
            ai_thinking_character[0] = None
        
        # Check for pending AI responses (global chat)
        if global_ai_responses_pending[0]:
            responses = global_ai_responses_pending[0]
            if responses:
                for char, response in responses:
                    if char and response:
                        char.set_speech_bubble(response, current_time)
            global_ai_responses_pending[0] = None
            ai_thinking_character[0] = None
        
        # Update thinking message if AI is still thinking
        if ai_thinking_character[0] and ai_chat.is_thinking:
            msg = ai_chat.get_thinking_message()
            if msg and ai_thinking_character[0].has_active_speech_bubble(current_time):
                ai_thinking_character[0].speech_bubble_text = msg
        
        # Update all characters with world reference
        for char in characters:
            char.update_ai(mouse_pos, current_time, characters, game_world)

            # Display pending play invitation as speech bubble (Bug 1 fix)
            if char.pending_invite:
                msg = char._pending_invite_message or f"Hey {char.pending_invite}, want to play?"
                char.set_speech_bubble(msg, current_time)
                char.pending_invite = None
                char._pending_invite_message = None

            # Display agent-to-agent AI dialogue set by background thread
            if char._pending_agent_speech:
                char.set_speech_bubble(char._pending_agent_speech, current_time)
                char._pending_agent_speech = None

        # Update command feedback timer
        if command_feedback_timer > 0:
            command_feedback_timer -= 1
        
        # Draw everything
        # Draw world background
        game_world.draw(screen)

        # Draw world objects
        game_world.draw_objects(screen)

        # Draw all character bodies (no speech bubbles yet so bubbles are never
        # hidden behind another character's body)
        char_screen_positions = []
        for char in characters:
            screen_x, screen_y = game_world.camera.world_to_screen(char.x, char.y)
            char_screen_positions.append((char, screen_x, screen_y))
            char.draw_at(screen, screen_x, screen_y, current_time, skip_bubble=True)

        # Draw input box
        input_box.draw(screen)

        # Draw UI overlay
        ui.draw_ui_overlay(
            screen, font, input_font,
            selected_character, ai_chat, current_time
        )

        # Draw command feedback
        if command_feedback_timer > 0:
            ui.draw_command_feedback(screen, font, command_feedback)

        # Draw narrator
        narrator.draw(screen, current_time)

        # Draw minimap
        if config.MINIMAP_ENABLED:
            minimap.draw(screen, characters)

        # Draw Android-specific UI hints
        if android_mode:
            draw_android_hints(screen)

        # Draw speech bubbles on top of EVERYTHING so they are never obscured
        for char, screen_x, screen_y in char_screen_positions:
            draw_x = screen_x + char.shake_offset
            draw_y = screen_y + char.bounce_offset
            char.draw_speech_bubble(screen, draw_x, draw_y, current_time)
        
        # Update display
        pygame.display.flip()
        
        # Limit to 60 FPS
        clock.tick(config.FPS)
    
    # Quit Pygame
    pygame.quit()
    sys.exit()


def draw_android_hints(screen):
    """Draw on-screen hints for Android users."""
    # Draw touch hint at bottom of screen
    screen_width, screen_height = screen.get_size()
    
    # Hint text would go here if needed
    # For now, we keep the UI clean


if __name__ == "__main__":
    main(android_mode=False)
