"""纯游戏规则和动画状态，可在不启动窗口的情况下测试。"""
import math
import copy
from config import (ROWS, COLS, MAX_MISTAKES, COLLISION_APPROACH_FRAMES,
                    COLLISION_HOLD_FRAMES, COLLISION_RETURN_FRAMES, FPS)
from levels import LEVELS


def get_direction_vector(direction):
    return {'right': (0, 1), 'left': (0, -1), 'down': (1, 0), 'up': (-1, 0)}[direction]


def get_arrow_cells(arrow):
    dr, dc = get_direction_vector(arrow['direction'])
    return [(arrow['row'] + dr * i, arrow['col'] + dc * i)
            for i in range(arrow['length'])]


def get_arrow_head_cell(arrow):
    return get_arrow_cells(arrow)[-1]


def find_blocker(arrow, arrows):
    occupied = {cell: other for other in arrows if other is not arrow
                for cell in get_arrow_cells(other)}
    row, col = get_arrow_head_cell(arrow)
    dr, dc = get_direction_vector(arrow['direction'])
    row, col, distance = row + dr, col + dc, 1
    while 0 <= row < ROWS and 0 <= col < COLS:
        if (row, col) in occupied:
            return occupied[row, col], distance
        row, col, distance = row + dr, col + dc, distance + 1
    return None, None


class Game:
    def __init__(self):
        self.sound_enabled = True
        self.level_stars = [0] * len(LEVELS)
        self.unlocked_level = 0
        self.current_level = 0
        self.load_level(0)
        self.state = 'start'
        self.has_progress = False

    def load_level(self, index):
        if not 0 <= index < len(LEVELS) or index > self.unlocked_level:
            return False
        self.history = []
        self.has_progress = True
        self.current_level = index
        self.arrows = [arrow.copy() for arrow in LEVELS[index]]
        self.mistakes_left = MAX_MISTAKES
        self.earned_stars = 0
        self.flying_arrow = None
        self.collision_arrow = None
        self.collision_gap_cells = 0
        self.collision_elapsed = 0
        self.collision_offset = (0, 0)
        self.state = 'playing'
        return True

    def find_arrow_at_cell(self, row, col):
        return next((arrow for arrow in self.arrows
                     if (row, col) in get_arrow_cells(arrow)), None)

    def click_cell(self, row, col):
        if self.state != 'playing' or self.flying_arrow or self.collision_arrow:
            return
        arrow = self.find_arrow_at_cell(row, col)
        if arrow is None:
            return
        self.history.append({'arrows': copy.deepcopy(self.arrows),
                             'mistakes_left': self.mistakes_left})
        blocker, distance = find_blocker(arrow, self.arrows)
        if blocker is not None:
            self.mistakes_left -= 1
            self.collision_arrow = arrow
            self.collision_gap_cells = distance
            self.collision_elapsed = 0
        else:
            self.flying_arrow = dict(arrow, offset_x=0.0, offset_y=0.0, speed=2.7)
            self.arrows.remove(arrow)

    def update(self, dt):
        if self.state != 'playing':
            return
        if self.flying_arrow is not None:
            arrow = self.flying_arrow
            arrow['speed'] = min(12.6, arrow['speed'] + 39.6 * dt)
            dr, dc = get_direction_vector(arrow['direction'])
            arrow['offset_x'] += dc * arrow['speed'] * dt
            arrow['offset_y'] += dr * arrow['speed'] * dt
            # Wait until the entire multi-cell arrow has left the board.
            if max(abs(arrow['offset_x']), abs(arrow['offset_y'])) > max(ROWS, COLS) + 1:
                self.flying_arrow = None
        self.collision_offset = (0, 0)
        if self.collision_arrow is not None:
            self.collision_elapsed += dt
            elapsed = self.collision_elapsed
            target = max(0.18, self.collision_gap_cells - 0.55)
            approach = COLLISION_APPROACH_FRAMES / FPS
            hold_end = approach + COLLISION_HOLD_FRAMES / FPS
            return_duration = COLLISION_RETURN_FRAMES / FPS
            if elapsed <= approach:
                distance = target * (1 - (1 - elapsed / approach) ** 3)
            elif elapsed <= hold_end:
                distance = target
            else:
                t = min(1, (elapsed - hold_end) / return_duration)
                distance = target * (1 - t) ** 3 - math.sin(t * math.pi) * 0.06
            dr, dc = get_direction_vector(self.collision_arrow['direction'])
            self.collision_offset = (dc * distance, dr * distance)
            if elapsed >= hold_end + return_duration:
                self.collision_arrow = None
                self.collision_offset = (0, 0)
                if self.mistakes_left == 0:
                    self.state = 'game_over'
        if not self.arrows and self.flying_arrow is None:
            self.earned_stars = max(1, self.mistakes_left)
            self.level_stars[self.current_level] = max(
                self.level_stars[self.current_level], self.earned_stars)
            self.unlocked_level = max(self.unlocked_level,
                                      min(len(LEVELS) - 1, self.current_level + 1))
            self.state = 'level_complete' if self.current_level < len(LEVELS) - 1 else 'all_clear'

    def resume(self):
        if not self.has_progress:
            return
        self.flying_arrow = None
        self.collision_arrow = None
        self.collision_offset = (0, 0)
        self.state = 'game_over' if self.mistakes_left == 0 else 'playing'
        self.update(0)

    @property
    def can_undo(self):
        return self.state in ('playing', 'game_over') and bool(self.history)

    def undo(self):
        """撤回当前关卡的一次有效点击，包括尚未结束的动画。"""
        if not self.can_undo:
            return False
        previous = self.history.pop()
        self.arrows = copy.deepcopy(previous['arrows'])
        self.mistakes_left = previous['mistakes_left']
        self.flying_arrow = None
        self.collision_arrow = None
        self.collision_gap_cells = 0
        self.collision_elapsed = 0
        self.collision_offset = (0, 0)
        self.earned_stars = 0
        self.state = 'playing'
        return True
