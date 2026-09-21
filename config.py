"""窗口、字体、颜色与统一尺寸规范。"""
import os

FONT_CANDIDATES = ['/System/Library/Fonts/Hiragino Sans GB.ttc',
 '/System/Library/Fonts/STHeiti Medium.ttc',
 '/System/Library/Fonts/STHeiti Light.ttc',
 '/System/Library/Fonts/Supplemental/Songti.ttc']
BACKGROUND_TOP = (242, 247, 255)
BACKGROUND_BOTTOM = (232, 240, 252)
CARD_BG = (255, 255, 255)
BOARD_BG = (250, 252, 255)
GRID_COLOR = (220, 228, 240)
TEXT_MAIN = (39, 47, 62)
TEXT_SECONDARY = (108, 119, 138)
BLUE = (78, 126, 230)
BLUE_DARK = (60, 102, 196)
GREEN = (61, 175, 122)
RED = (225, 82, 88)
ORANGE = (237, 148, 65)
PURPLE = (146, 98, 214)
TEAL = (51, 167, 176)
GOLD = (246, 184, 47)
STAR_EMPTY = (213, 221, 233)
SHADOW = (205, 215, 231)
WHITE = (255, 255, 255)
ROWS = 7
COLS = 7
MAX_CELL_SIZE = 84
MAX_MISTAKES = 3
COLLISION_APPROACH_FRAMES = 12
COLLISION_HOLD_FRAMES = 5
COLLISION_RETURN_FRAMES = 18
TRANSITION_SPEED = 700
WINDOW_WIDTH = 960
WINDOW_HEIGHT = 800
WINDOW_TITLE = '一箭又一箭'
FPS = 60
MIN_WINDOW_WIDTH = 320
MIN_WINDOW_HEIGHT = 520
UI = {'body_size': 16,
 'button_height': 42,
 'button_radius': 12,
 'card_radius': 16,
 'gap': 14,
 'modal_button_width': 220,
 'page_margin': 24,
 'small_button_width': 110,
 'stat_height': 58,
 'stat_width': 135,
 'title_size': 32}

FONT_PATH = next((path for path in FONT_CANDIDATES if os.path.exists(path)), None)
