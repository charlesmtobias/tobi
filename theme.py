"""
theme.py - Shared visual and layout configuration for tobi.

Import this module wherever consistent colors, fonts, or sizing are needed.
Change a value here and it updates everywhere it's used.
"""

# --- Base palette ---
# Raw color building blocks - avoid using these directly in screen code;
# reference the semantic names below instead.
MAIN_WHITE = (245, 245, 250)
MAIN_BLACK = (30, 30, 40)

PRIMARY = (100, 160, 220)
PRIMARY_HOVER = (130, 185, 235)

SECONDARY = (220, 220, 230)
SECONDARY_HOVER = (200, 200, 215)

MUTED = (210, 210, 220)
MUTED_TEXT = (150, 150, 160)

# --- Semantic roles ---
# Screens reference these, not the raw palette above - this is the layer
# you edit to restyle the app without touching draw code.
BG_COLOR = MAIN_WHITE
TEXT_COLOR = MAIN_BLACK

TILE_COLOR = PRIMARY
TILE_HOVER_COLOR = PRIMARY_HOVER

BACK_COLOR = SECONDARY
BACK_HOVER_COLOR = SECONDARY_HOVER

CARTRIDGE_EMPTY_COLOR = MUTED
CARTRIDGE_EMPTY_TEXT_COLOR = MUTED_TEXT

# --- Fonts ---
FONT_PATH = "assets/fonts/Andika/Andika-Regular.ttf"
FONT_SIZE_BODY = 28
FONT_SIZE_TITLE = 36

# --- Virtual "hardware" resolution (matches the real 7" touchscreen) ---
GAME_WIDTH = 1024
GAME_HEIGHT = 600

# --- Grid layout ---
COLS = 5
ROWS = 3
MARGIN = 40
TILE_GAP = 30
