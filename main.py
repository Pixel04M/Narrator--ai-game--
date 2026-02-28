"""
Virtual Pet Game - Entry Point
==============================
Main entry point for the game. Run this file to start the game.
Supports both desktop and Android (via PGS4A).
"""

import sys
import os

# Check if running on actual Android device (PGS4A)
# We detect actual Android by checking for PGS4A-specific attributes
ANDROID = False

try:
    # Try to import PGS4A's android module
    import android
    
    # Check for PGS4A-specific attributes that only exist on real Android
    # Real PGS4A android module has these functions/classes
    if (hasattr(android, ' accelerometer') or 
        hasattr(android, 'mixer') or 
        hasattr(android, 'display')):
        # Additional check: verify it's not our stub
        # Our stub has specific characteristics we can detect
        if not hasattr(android, '_is_stub'):
            ANDROID = True
except ImportError:
    # No android module at all - definitely desktop
    ANDROID = False

# Create stub for desktop mode if needed
if not ANDROID:
    # We're on desktop - create stub for android module
    class AndroidStub:
        """Stub for android module on desktop."""
        _is_stub = True  # Mark as stub for detection
        
        def init(self):
            pass
        
        class device:
            screen_width = 800
            screen_height = 600
            
        class keyboard:
            @staticmethod
            def show():
                pass
            
            @staticmethod
            def hide():
                pass
        
        @staticmethod
        def show_keyboard():
            pass
        
        @staticmethod
        def hide_keyboard():
            pass
    
    android = AndroidStub()

# Import pygame - required for both desktop and Android
import pygame

# Import game after pygame is initialized
import game

if __name__ == "__main__":
    # Initialize pygame
    pygame.init()
    
    # Check for command line argument to force Android mode
    force_android = "--android" in sys.argv
    
    # Determine if we should run in Android mode:
    # - If actually on Android device (ANDROID = True), use Android mode
    # - If --android flag passed, use Android mode for testing
    android_mode = ANDROID or force_android
    
    # Start the game
    game.main(android_mode=android_mode)
