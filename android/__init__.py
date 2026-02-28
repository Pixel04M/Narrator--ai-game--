"""
Android Module Stub for Desktop Testing
=========================================
This module provides stub implementations of the PGS4A android module
for testing the game on desktop without Android-specific features.

When running on actual Android device via PGS4A, this module is replaced
by the real android module from PGS4A.
"""

# Event types for Android touch events
TOUCHDOWN = 4
TOUCHUP = 1
TOUCHMOTION = 2
PINCH = 3

# Device info (desktop stub values)
class Device:
    """Stub for android.device module."""
    screen_width = 800
    screen_height = 600
    
    @staticmethod
    def get_screen_size():
        return (800, 600)
    
    @staticmethod
    def get_dpi():
        return 160


# Create device instance
device = Device()

# Mark this module as a stub for detection
_is_stub = True


def init():
    """Initialize Android-specific modules. No-op on desktop."""
    pass


def show_keyboard():
    """Show virtual keyboard. No-op on desktop."""
    pass


def hide_keyboard():
    """Hide virtual keyboard. No-op on desktop."""
    pass


def vibrate(duration):
    """Vibrate device. No-op on desktop."""
    pass


# Touch module stub
class Touch:
    """Stub for android.touch module."""
    
    @staticmethod
    def get_touches():
        """Get current touch positions."""
        return []
    
    @staticmethod
    def get_primary_id():
        """Get primary touch ID."""
        return -1


# Create touch instance
touch = Touch()


# Keyboard module stub
class Keyboard:
    """Stub for android.keyboard module."""
    
    @staticmethod
    def is_visible():
        """Check if keyboard is visible."""
        return False
    
    @staticmethod
    def show():
        """Show keyboard."""
        pass
    
    @staticmethod
    def hide():
        """Hide keyboard."""
        pass


# Create keyboard instance
keyboard = Keyboard()


# Display module stub
class Display:
    """Stub for android.display module."""
    
    @staticmethod
    def init():
        """Initialize display."""
        pass
    
    @staticmethod
    def get_surface():
        """Get display surface."""
        return None
    
    @staticmethod
    def flip():
        """Flip display."""
        pass


# Create display instance
display = Display()


# Mixer module stub (for audio)
class Mixer:
    """Stub for android.mixer module."""
    
    @staticmethod
    def init(frequency=44100, size=-16, channels=2, buffer=512):
        """Initialize mixer."""
        pass
    
    @staticmethod
    def quit():
        """Quit mixer."""
        pass


# Create mixer instance
mixer = Mixer()


# Broadcast module stub
class Broadcast:
    """Stub for android.broadcast module."""
    
    @staticmethod
    def register_receiver(action, callback):
        """Register broadcast receiver."""
        pass
    
    @staticmethod
    def unregister_receiver(receiver):
        """Unregister broadcast receiver."""
        pass


# Create broadcast instance
broadcast = Broadcast()
