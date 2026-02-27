"""
Virtual Pet Game with AI Personalities and World Exploration
=============================================================
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
"""

import pygame
import sys
import config
import character as char_module
import ai_chat as chat_module
import ui
import world as world_module
import narrator as narrator_module


def main():
    """Main game function."""
    # Initialize Pygame
    pygame.init()
    
    # Set up screen
    screen = pygame.display.set_mode((config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
    pygame.display.set_caption(config.GAME_CAPTION)
    
    # Create clock
    clock = pygame.time.Clock()
    
    # Create fonts
    font = pygame.font.Font(None, 28)
    input_font = pygame.font.Font(None, 26)
    
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
    
    # Assign world reference to characters
    for char in characters:
        char.world = game_world
    
    # Track selected character
    selected_character = None
    
    # Create input box
    input_box = ui.InputBox()
    
    # Create command system
    command_system = ui.CommandSystem()
    
    # Command feedback message
    command_feedback = ""
    command_feedback_timer = 0
    
    # Minimap
    minimap = world_module.Minimap(game_world)
    
    # Game loop
    running = True
    
    while running:
        # Get current time
        current_time = pygame.time.get_ticks()
        
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            # Handle keyboard input
            if event.type == pygame.KEYDOWN:
                # Handle input box events
                result = input_box.handle_event(event)
                
                if result == "escape":
                    # Deselect character on ESC
                    selected_character = None
                    for char in characters:
                        char.is_selected = False
                    input_box.set_active(False)
                elif result and isinstance(result, str):
                    # User pressed Enter with text
                    message = result
                    
                    # Check for global chat prefix
                    if message.startswith(config.GLOBAL_CHAT_PREFIX):
                        # Global chat - all characters respond
                        global_message = message[len(config.GLOBAL_CHAT_PREFIX):].strip()
                        
                        if global_message:
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
                        # Check if AI is available and enabled
                        if ai_chat.is_available:
                            # Use async AI response
                            loading_msg = chat_system.generate_response_async(
                                selected_character, 
                                message,
                                lambda resp: (
                                    ai_response_pending.__setitem__(0, (
                                        selected_character,
                                        chat_system.handle_ai_response(selected_character, resp)
                                    ))
                                ),
                                characters
                            )
                            # Show loading message immediately
                            if loading_msg:
                                selected_character.set_speech_bubble(loading_msg, current_time)
                                ai_thinking_character[0] = selected_character
                        else:
                            # Use rule-based response immediately
                            response = chat_system.generate_response(selected_character, message)
                            selected_character.set_speech_bubble(response, current_time)
                        
                        selected_character.last_interaction_time = current_time
                    
                    # No character selected and not a command
                    else:
                        command_feedback = "Select a character first, or use /all <message> to ask everyone!"
                        command_feedback_timer = 120
            
            # Handle mouse clicks
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                
                # Check if clicking on input box
                if input_box.is_clicked(mouse_pos):
                    input_box.set_active(True)
                else:
                    input_box.set_active(False)
                
                # Check if clicking on a character
                if event.button == 1:  # Left click
                    # Start camera drag (will be ended if clicking on a character)
                    game_world.camera.start_drag(mouse_pos)
                    
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
                        # End drag since we clicked on a character
                        game_world.camera.end_drag()
                        # Deselect previous
                        for char in characters:
                            char.is_selected = False
                        # Select new character
                        clicked_character.is_selected = True
                        selected_character = clicked_character
                    elif not input_box.is_clicked(mouse_pos):
                        # Clicked elsewhere - deselect
                        for char in characters:
                            char.is_selected = False
                        selected_character = None
                
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
        
        # Update command feedback timer
        if command_feedback_timer > 0:
            command_feedback_timer -= 1
        
        # Draw everything
        # Draw world background
        game_world.draw(screen)
        
        # Draw world objects
        game_world.draw_objects(screen)
        
        # Draw all characters with current time for speech bubbles
        for char in characters:
            # Convert world position to screen for drawing
            screen_x, screen_y = game_world.camera.world_to_screen(char.x, char.y)
            char.draw_at(screen, screen_x, screen_y, current_time)
        
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
        
        # Update display
        pygame.display.flip()
        
        # Limit to 60 FPS
        clock.tick(config.FPS)
    
    # Quit Pygame
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
