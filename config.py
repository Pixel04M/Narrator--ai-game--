"""
Configuration Settings for Virtual Pet Game
===========================================
All game constants, colors, and settings in one place.
"""

import os

# ============================================
# Screen & Display Settings
# ============================================
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
WORLD_WIDTH = 1600
WORLD_HEIGHT = 1200
FPS = 60
GAME_CAPTION = "Virtual Pet Game - Explore the World!"

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

# HUD Settings
HUD_ENABLED = True
MINIMAP_ENABLED = True
MINIMAP_WIDTH = 160
MINIMAP_HEIGHT = 120

# Character stats panel
STATS_PANEL_WIDTH = 200
STATS_PANEL_HEIGHT = 150

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
# ============================================
CHARACTER_PROMPTS = {
    "Fifi": "You are Fifi, a friendly virtual pet. Give brief, direct answers (1-2 sentences max). Be sweet and caring.",
    "Shyel": "You are Shyel, a shy virtual pet. Give brief answers (1-2 sentences max). Speak softly and use '...' for pauses.",
    "Grump": "You are Grump, a grumpy but loveable virtual pet. Give short, direct responses (1-2 sentences). Use a grumbling tone but be helpful.",
    "Pippin": "You are Pippin, an energetic virtual pet. Give brief, fun answers (1-2 sentences max). Be enthusiastic!"
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
