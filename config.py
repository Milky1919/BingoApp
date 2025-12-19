import os

# App Info
APP_NAME = "Local Bingo Master"
VERSION = "1.0.0"

# Dimensions
WINDOW_WIDTH = 1024
WINDOW_HEIGHT = 768

# Bingo
MIN_NUMBER = 1
MAX_NUMBER = 75

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
SOUND_DIR = os.path.join(ASSETS_DIR, "sound")

DATA_FILE = os.path.join(DATA_DIR, "bingo_data.json")
BACKUP_FILE = os.path.join(DATA_DIR, "bingo_data_bak.json")

# Colors (Dark/Light)
COLORS = {
    "dark": {
        "bg": "#1a1a1a",
        "panel_bg": "#2b2b2b",
        "text": "#ffffff",
        "text_dim": "#555555",
        "accent_hit": "#06b6d4",    # Cyan
        "accent_cursor": "#f59e0b", # Amber
        "btn_spin": "#3b82f6",      # Blue
        "btn_hover": "#2563eb",
        "cell_bg": "#383838"
    },
    "light": {
        "bg": "#f0f0f0",
        "panel_bg": "#ffffff",
        "text": "#1a1a1a",
        "text_dim": "#cccccc",
        "accent_hit": "#0891b2",    # Darker Cyan
        "accent_cursor": "#d97706", # Darker Amber
        "btn_spin": "#2563eb",      # Darker Blue
        "btn_hover": "#1d4ed8",
        "cell_bg": "#e5e5e5"
    }
}
