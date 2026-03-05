"""
Configuration Settings for Virtual Pet Game
==========================================
All game constants, colors, and settings in one place.
Includes mobile-responsive settings for Android.
"""

import os

# ============================================
# Screen & Display Settings
# ============================================
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

# Mobile-responsive screen settings (used on Android)
MOBILE_SCREEN_WIDTH = 480
MOBILE_SCREEN_HEIGHT = 800
MOBILE_LANDSCAPE_WIDTH = 800
MOBILE_LANDSCAPE_HEIGHT = 480

# World settings (larger than screen for exploration)
WORLD_WIDTH = 1600
WORLD_HEIGHT = 1200
FPS = 60
GAME_CAPTION = "Virtual Pet Game - Explore the World!"

# ============================================
# Responsive UI Settings
# ============================================
# Scale factors for different screen densities
UI_SCALE_SMALL = 0.75    # Small phones
UI_SCALE_MEDIUM = 1.0    # Standard phones
UI_SCALE_LARGE = 1.25    # Large phones/tablets
UI_SCALE_TABLET = 1.5   # Tablets

# Dynamic scaling - automatically calculated based on screen size
AUTO_SCALE = True

# Touch-friendly sizing
TOUCH_TARGET_MIN_SIZE = 48  # Minimum touch target size in pixels
TOUCH_SLOP = 10  # Extra tolerance for touch detection

# ============================================
# Colors
# ============================================
# Background
BACKGROUND_COLOR = (245, 222, 179)  # Light brown (warm room)
FLOOR_COLOR = (139, 90, 43)  # Darker brown for floor
WALL_COLOR = (255, 248, 220)  # Cream color
GRASS_COLOR = (124, 179, 66)
GRASS_COLOR_ALT = (107, 156, 55)

# UI Colors
INPUT_BOX_COLOR = (255, 255, 255)
INPUT_BOX_BORDER = (100, 80, 60)
SELECTED_GLOW = (255, 215, 0)  # Gold glow for selected characters
SPEECH_BUBBLE_BG = (255, 255, 245)
SPEECH_BUBBLE_BORDER = (80, 80, 80)
NARRATOR_BG = (255, 250, 240)
NARRATOR_BORDER = (180, 160, 120)

# Character colors (base colors for each personality)
FIFI_COLOR = (255, 182, 193)  # Pink (friendly)
SHYEL_COLOR = (173, 216, 230)  # Light blue (shy)
GRUMP_COLOR = (255, 200, 200)  # Light red (grumpy)
PIPPIN_COLOR = (144, 238, 144)  # Light green (playful)

# ============================================
# UI Settings
# ============================================
INPUT_BOX_HEIGHT = 40
INPUT_BOX_MARGIN = 20
SPEECH_BUBBLE_LIFETIME = 4000  # ms
SPEECH_BUBBLE_FADE_TIME = 2000  # ms

# Mobile-specific UI settings
MOBILE_INPUT_BOX_HEIGHT = 50  # Larger for touch
MOBILE_UI_PADDING = 16

# HUD Settings
HUD_ENABLED = True
MINIMAP_ENABLED = True
MINIMAP_WIDTH = 160
MINIMAP_HEIGHT = 120

# Mobile HUD settings
MOBILE_MINIMAP_WIDTH = 100
MOBILE_MINIMAP_HEIGHT = 75

# Character stats panel
STATS_PANEL_WIDTH = 200
STATS_PANEL_HEIGHT = 150
MOBILE_STATS_PANEL_WIDTH = 150
MOBILE_STATS_PANEL_HEIGHT = 120

# ============================================
# Character Settings
# ============================================
CHARACTER_RADIUS = 40

# Character starting positions (world coordinates 1600x1200)
CHARACTER_POSITIONS = [
    ("Fifi", 200, 400),
    ("Shyel", 350, 450),
    ("Grump", 550, 400),
    ("Pippin", 700, 450)
]

# Movement settings
DEFAULT_CHARACTER_SPEED = 2
FAST_SPEED = 6
DANCE_SPEED = 4
SEEKING_SPEED = 2.5

# ============================================
# State Emojis
# ============================================
STATE_EMOJIS = {
    'idle': '😐',
    'happy': '😊',
    'sad': '😢',
    'angry': '😠',
    'scared': '😨',
    'sleepy': '😴',
    'hungry': '🍽️',
    'playing': '😄',
    'hiding': '🙈',
    'tantrum': '💢',
    'dancing': '💃',
    'lined': '🙋',
    'seeking': '🔍'
}

# ============================================
# Personality Types
# ============================================
PERSONALITY_FRIENDLY = 'friendly'
PERSONALITY_SHY = 'shy'
PERSONALITY_GRUMPY = 'grumpy'
PERSONALITY_PLAYFUL = 'playful'

# ============================================
# Character Relationships (for AI context)
# ============================================
CHARACTER_RELATIONSHIPS = {
    "Fifi": {
        "Shyel": "Fifi is protective of Shyel and gently encourages them.",
        "Grump": "Fifi tries to keep Grump in good spirits.",
        "Pippin": "Fifi enjoys Pippin's energy and plays with them."
    },
    "Shyel": {
        "Fifi": "Shyel feels safe around Fifi.",
        "Grump": "Shyel is a bit intimidated by Grump.",
        "Pippin": "Shyel is amazed by Pippin's energy."
    },
    "Grump": {
        "Fifi": "Grump secretly cares about Fifi.",
        "Shyel": "Grump is surprisingly gentle with Shyel.",
        "Pippin": "Grump finds Pippin's energy exhausting but amusing."
    },
    "Pippin": {
        "Fifi": "Pippin loves playing with Fifi!",
        "Shyel": "Pippin wants to help Shyel come out of their shell.",
        "Grump": "Pippin thinks Grump is funny when grumpy."
    }
}

# ============================================
# AI Chat Configuration
# ============================================

# Per-personality AI temperature (higher = more creative/random, runs at 60 FPS)
PERSONALITY_TEMPERATURES = {
    "Fifi":   0.75,   # Warm, friendly, slightly varied
    "Shyel":  0.65,   # Quieter, more consistent
    "Grump":  0.55,   # Consistent grumbling tone
    "Pippin": 0.90    # High randomness - unpredictable fun
}

# Token limits per use case
MAX_TOKENS_CHAT = 90            # Player <-> character (was 500 — wasteful for 1-2 sentences)
MAX_TOKENS_AGENT_DIALOGUE = 40  # Agent <-> agent one-liners
MAX_TOKENS_GLOBAL = 90          # /all global chat responses

# AI Provider: "fireworks" (only active provider)
AI_PROVIDER = "fireworks"

# Enable/disable AI chat
USE_AI_CHAT = True

# Fireworks AI Configuration
FIREWORKS_API_KEY = os.environ.get('FIREWORKS_API_KEY', 'fw_13f2DX9GpAGJeRqyPBvduF')
FIREWORKS_API_URL = "https://api.fireworks.ai/inference/v1/chat/completions"
FIREWORKS_MODEL = "accounts/fireworks/models/minimax-m2p5"

# ============================================
# Character System Prompts
CHARACTER_PROMPTS = {
    "Fifi": "You are Fifi, a friendly virtual pet. Be sweet and caring. Reply with ONLY your spoken words (1-2 sentences). Never prefix with your name or 'I would say'.",
    "Shyel": "You are Shyel, a shy virtual pet. Speak softly and use '...' for pauses. Reply with ONLY your spoken words (1-2 sentences). Never prefix with your name or 'I would say'.",
    "Grump": "You are Grump, a grumpy but loveable virtual pet. Use a grumbling tone but be helpful. Reply with ONLY your spoken words (1-2 sentences). Never prefix with your name or 'I would say'.",
    "Pippin": "You are Pippin, an energetic virtual pet. Be enthusiastic! Reply with ONLY your spoken words (1-2 sentences). Never prefix with your name or 'I would say'."
}

# ============================================
# Fallback Messages
# ============================================
AI_FALLBACK_MESSAGES = {
    PERSONALITY_FRIENDLY: "*waves* Hi there, friend!",
    PERSONALITY_SHY: "*looks shyly* H-hello...",
    PERSONALITY_GRUMPY: "*sighs* What do you want?",
    PERSONALITY_PLAYFUL: "*bounces* Hey! Let's play!"
}

# Loading indicator messages
AI_LOADING_MESSAGES = [
    "Thinking...",
    "Hmm...",
    "Let me think...",
    "*ponders*"
]

# ============================================
# Command Prefixes
# ============================================
GLOBAL_CHAT_PREFIX = "/all "  # Prefix for global chat (all characters respond)
COMMAND_PREFIX = "/"  # Prefix for commands

# Available commands
COMMANDS = {
    "/line": "Line up all characters",
    "/pairs": "Pair up characters",
    "/dance": "Make all characters dance",
    "/scatter": "Random positions",
    "/explore": "Characters explore the world",
    "/help": "Show available commands"
}

# ============================================
# World Object Types
# ============================================
OBJECT_FOOD_BOWL = "food_bowl"
OBJECT_BED = "bed"
OBJECT_TOY = "toy"
OBJECT_TREE = "tree"
OBJECT_ROCK = "rock"

# ============================================
# Decorative Elements Positions
# ============================================
WINDOW_RECT = (50, 50, 120, 100)
PICTURE_FRAME_RECT = (350, 60, 80, 60)
PLANT_POSITION = (720, 180)


# ============================================
# Android/PGS4A Specific Settings
# ============================================
ANDROID_PACKAGE_NAME = "com.virtualpet.game"
ANDROID_VERSION_CODE = "1"
ANDROID_VERSION_NAME = "1.0.0"

# Touch gesture settings
TOUCH_TAP_THRESHOLD = 20  # pixels
TOUCH_TAP_TIME = 300  # ms
TOUCH_LONG_PRESS_TIME = 500  # ms

# Pinch zoom settings
PINCH_ZOOM_ENABLED = True
PINCH_MIN_SCALE = 0.5
PINCH_MAX_SCALE = 2.0

# Virtual keyboard settings
VIRTUAL_KEYBOARD_ENABLED = True
VIRTUAL_KEYBOARD_HEIGHT = 200  # approximate


def get_screen_config(is_android=False, screen_width=None, screen_height=None):
    """Get appropriate screen configuration based on device.
    
    Args:
        is_android: Whether running on Android
        screen_width: Actual screen width (for Android)
        screen_height: Actual screen height (for Android)
    
    Returns:
        tuple: (width, height, scale_factor)
    """
    if is_android and screen_width and screen_height:
        # Determine if portrait or landscape
        is_portrait = screen_height > screen_width
        
        if is_portrait:
            width = min(screen_width, MOBILE_SCREEN_WIDTH)
            height = min(screen_height, MOBILE_SCREEN_HEIGHT)
        else:
            width = min(screen_width, MOBILE_LANDSCAPE_WIDTH)
            height = min(screen_height, MOBILE_LANDSCAPE_HEIGHT)
        
        # Calculate scale based on screen size
        scale = min(screen_width / SCREEN_WIDTH, screen_height / SCREEN_HEIGHT)
        
        return width, height, scale
    
    return SCREEN_WIDTH, SCREEN_HEIGHT, 1.0


def get_touch_settings():
    """Get touch-friendly UI settings based on screen size."""
    return {
        'input_box_height': MOBILE_INPUT_BOX_HEIGHT,
        'ui_padding': MOBILE_UI_PADDING,
        'minimap_width': MOBILE_MINIMAP_WIDTH,
        'minimap_height': MOBILE_MINIMAP_HEIGHT,
        'stats_panel_width': MOBILE_STATS_PANEL_WIDTH,
        'stats_panel_height': MOBILE_STATS_PANEL_HEIGHT,
    }
