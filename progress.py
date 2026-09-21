"""校验并原子写入本地存档；动画不进入存档。"""
import copy
import json
import os
from pathlib import Path
import tempfile
import time
from config import MAX_MISTAKES
from levels import LEVELS, LEGACY_BASIC_LEVELS
from game_logic import find_blocker

DEFAULT_SAVE_PATH = Path(__file__).resolve().parent / 'saves' / 'progress.json'


def snapshot(game):
    stable = copy.deepcopy(game)
    if stable.has_progress:
        stable.state = 'playing'
        stable.update(10)
    return {'version': 1, 'sound_enabled': stable.sound_enabled, 'level_stars': stable.level_stars,
            'unlocked_level': stable.unlocked_level,
            'current': {'level': stable.current_level, 'arrows': stable.arrows,
                        'mistakes_left': stable.mistakes_left, 'history': stable.history} if stable.has_progress else None}


def validate(data):
    if not isinstance(data, dict) or type(data.get('version')) is not int or data['version'] != 1:
        raise ValueError('不支持的存档版本')
    if type(data.get('sound_enabled', True)) is not bool:
        raise ValueError('音效设置无效')
    stars = data.get('level_stars')
    if not isinstance(stars, list) or len(stars) not in (3, len(LEVELS)) or any(type(s) is not int or not 0 <= s <= 3 for s in stars):
        raise ValueError('星级数据无效')
    unlocked = data.get('unlocked_level')
    expected = 0
    for i, star in enumerate(stars):
        if star:
            if i > expected:
                raise ValueError('关卡进度无效')
            expected = min(len(stars) - 1, i + 1)
    if type(unlocked) is not int or unlocked != expected:
        raise ValueError('解锁数据无效')
    if len(stars) < len(LEVELS):
        migrated = copy.deepcopy(data)
        migrated['level_stars'] += [0] * (len(LEVELS) - len(stars))
        if stars[-1] > 0:
            migrated['unlocked_level'] = len(stars)
        return validate(migrated)
    if 'current' not in data:
        raise ValueError('缺少当前进度')
    current = data.get('current')
    if current is not None:
        if not isinstance(current, dict):
            raise ValueError('当前关卡无效')
        level, mistakes = current.get('level'), current.get('mistakes_left')
        if type(level) is not int or not 0 <= level <= unlocked:
            raise ValueError('当前关卡无效')
        if type(mistakes) is not int or not 0 <= mistakes <= MAX_MISTAKES:
            raise ValueError('失误数据无效')
        arrows = current.get('arrows')
        if not isinstance(arrows, list):
            raise ValueError('棋盘无效')
        remaining = copy.deepcopy(LEVELS[level])
        for arrow in arrows:
            if not isinstance(arrow, dict) or any(type(arrow.get(k)) is not int for k in ('row','col','length')) or arrow not in remaining:
                raise ValueError('箭头数据无效')
            remaining.remove(arrow)
        if not arrows and (mistakes == 0 or stars[level] < mistakes):
            raise ValueError('通关数据无效')
        history = current.get('history', [])
        if not isinstance(history, list) or len(history) > len(LEVELS[level]) + MAX_MISTAKES:
            raise ValueError('撤销记录无效')
        for i, previous in enumerate(history):
            if not isinstance(previous, dict) or set(previous) != {'arrows', 'mistakes_left'}:
                raise ValueError('撤销记录无效')
            validate(dict(data, current=dict(previous, level=level)))
            if not previous['arrows'] or previous['mistakes_left'] == 0:
                raise ValueError('撤销记录无效')
            after = history[i + 1] if i + 1 < len(history) else current
            before_arrows = previous['arrows']
            delta = previous['mistakes_left'] - after.get('mistakes_left', -99)
            if delta == 1 and before_arrows == after.get('arrows'):
                valid = any(find_blocker(a, before_arrows)[0] is not None for a in before_arrows)
            elif delta == 0:
                valid = any(before_arrows[:j] + before_arrows[j + 1:] == after.get('arrows')
                            and find_blocker(a, before_arrows)[0] is None
                            for j, a in enumerate(before_arrows))
            else:
                valid = False
            if not valid:
                raise ValueError('撤销记录不连续')
    return data


def migrate_basic_arrows(data):
    """旧版前三关缩为单格；保留棋盘进度，清除规则改变前的撤销记录。"""
    if not isinstance(data, dict):
        return data
    current = data.get('current')
    if not isinstance(current, dict) or type(current.get('level')) is not int or not 0 <= current['level'] < 3:
        return data
    level = current['level']
    history = current.get('history', [])
    if not isinstance(history, list) or any(not isinstance(item, dict) for item in history):
        return data
    boards = [current.get('arrows')] + [item.get('arrows') for item in history]
    if any(not isinstance(board, list) for board in boards):
        return data
    old_found = False
    for board in boards:
        for arrow in board:
            if arrow not in LEVELS[level] and arrow not in LEGACY_BASIC_LEVELS[level]:
                return data
            if arrow in LEGACY_BASIC_LEVELS[level] and arrow['length'] > 1:
                old_found = True
    if not old_found:
        return data
    migrated = copy.deepcopy(data)
    for arrow in migrated['current']['arrows']:
        arrow['length'] = 1
    migrated['current']['history'] = []
    return migrated


def restore(game, data):
    data = validate(migrate_basic_arrows(data))
    game.sound_enabled = data.get('sound_enabled', True)
    game.level_stars = data['level_stars'][:]
    game.unlocked_level = data['unlocked_level']
    current = data['current']
    if current is not None:
        game.load_level(current['level'])
        game.arrows = copy.deepcopy(current['arrows'])
        game.mistakes_left = current['mistakes_left']
        game.history = copy.deepcopy(current.get('history', []))
    else:
        game.has_progress = False
    game.state = 'start'


class ProgressStore:
    def __init__(self, path=DEFAULT_SAVE_PATH):
        self.path = Path(path) if path is not None else None
        self.last = None
        self.message = ''
        self.retry_after = 0

    def load(self, game):
        if self.path is None or not self.path.exists():
            return
        try:
            data = json.loads(self.path.read_text(encoding='utf-8'))
            restore(game, data)
            self.last = snapshot(game)
        except (OSError, ValueError, TypeError, KeyError):
            self.message = '存档无法读取，已使用初始进度'
            self.last = snapshot(game)
            # Keep the damaged file for recovery before a future save replaces it.
            try:
                backup = self.path.with_name(self.path.name + '.damaged')
                if not backup.exists():
                    backup.write_bytes(self.path.read_bytes())
            except OSError:
                pass

    def save(self, game):
        if self.path is None or time.monotonic() < self.retry_after:
            return
        data = snapshot(game)
        if data == self.last:
            return
        temporary = None
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', dir=self.path.parent,
                                             prefix='.progress-', delete=False) as stream:
                temporary = stream.name
                json.dump(data, stream, ensure_ascii=False, indent=2)
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(temporary, self.path)
            self.last = data
            self.message = ''
        except OSError:
            self.message = '进度保存失败，请检查存储空间或目录权限'
            self.retry_after = time.monotonic() + 3
        finally:
            if temporary and os.path.exists(temporary):
                os.unlink(temporary)
