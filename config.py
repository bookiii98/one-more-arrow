"""窗口、字体、颜色与统一尺寸规范。"""
import os

def font_candidates():
    """显式字体优先，其次检查各系统常见中文字体位置。"""
    windows = os.environ.get('WINDIR') or os.environ.get('SystemRoot') or 'C:\\Windows'
    local = os.environ.get('LOCALAPPDATA', '')
    candidates = [os.environ.get('ONE_MORE_ARROW_FONT', '')]
    candidates += [os.path.join(windows, 'Fonts', name)
                   for name in ('msyh.ttc', 'msyh.ttf', 'simhei.ttf', 'simsun.ttc')]
    if local:
        candidates += [os.path.join(local, 'Microsoft', 'Windows', 'Fonts', name)
                       for name in ('msyh.ttc', 'simhei.ttf', 'NotoSansCJKsc-Regular.otf')]
    candidates += [
        '/System/Library/Fonts/Hiragino Sans GB.ttc',
        '/System/Library/Fonts/STHeiti Medium.ttc',
        '/System/Library/Fonts/STHeiti Light.ttc',
        '/System/Library/Fonts/Supplemental/Songti.ttc',
        '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',
        '/usr/share/fonts/opentype/noto/NotoSansCJKsc-Regular.otf',
        '/usr/share/fonts/truetype/wqy/wqy-microhei.ttc',
        '/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc',
        os.path.expanduser('~/.local/share/fonts/NotoSansCJKsc-Regular.otf'),
    ]
    return [path for path in candidates if path]


def find_font(candidates=None):
    return next((path for path in (font_candidates() if candidates is None else candidates)
                 if os.path.isfile(path)), None)


FONT_CANDIDATES = font_candidates()
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

FONT_PATH = find_font(FONT_CANDIDATES)
