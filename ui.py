"""界面、响应式布局和视觉反馈；不修改关卡进度。"""
import math
import pygame
from config import FONT_CANDIDATES, BACKGROUND_TOP, BACKGROUND_BOTTOM, CARD_BG, BOARD_BG, GRID_COLOR, TEXT_MAIN, TEXT_SECONDARY, BLUE, BLUE_DARK, GREEN, RED, ORANGE, PURPLE, TEAL, GOLD, STAR_EMPTY, SHADOW, WHITE, ROWS, COLS, MAX_CELL_SIZE, MAX_MISTAKES, COLLISION_APPROACH_FRAMES, COLLISION_HOLD_FRAMES, COLLISION_RETURN_FRAMES, TRANSITION_SPEED, WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_TITLE, FPS, MIN_WINDOW_WIDTH, MIN_WINDOW_HEIGHT, UI, FONT_PATH
from game_logic import get_arrow_cells
from levels import LEVELS, LEVEL_NAMES



class GameUI:
    def __init__(self, screen, game):
        self.screen = screen
        self.game = game
        self.level_scroll = 0
        self.button_scales = {}
        self.arrow_scales = {}
        self.card_scales = {}
        self.fonts = {}
        self.CELL_SIZE = 70
        self.BOARD_X = 100
        self.BOARD_Y = 200
        self.state_enter_time = 0
        self.update_board_layout()

    def get_font(self, size, bold=False):
        key = (max(13, int(size)), bold)
        if key not in self.fonts:
            font = pygame.font.Font(FONT_PATH, key[0])
            font.set_bold(bold)
            self.fonts[key] = font
        return self.fonts[key]


    def clamp(self, value, minimum, maximum):
        return max(minimum, min(value, maximum))

    def lerp(self, current, target, speed):
        return current + (target - current) * speed

    def ease_out_cubic(self, t):
        return 1 - (1 - t) ** 3

    def get_layout_mode(self):
        (width, height) = self.screen.get_size()
        if width < 580:
            return 'compact'
        elif width < 820:
            return 'medium'
        else:
            return 'desktop'

    def draw_background(self):
        (width, height) = self.screen.get_size()
        for y in range(height):
            t = y / max(1, height - 1)
            color = (int(BACKGROUND_TOP[0] + (BACKGROUND_BOTTOM[0] - BACKGROUND_TOP[0]) * t), int(BACKGROUND_TOP[1] + (BACKGROUND_BOTTOM[1] - BACKGROUND_TOP[1]) * t), int(BACKGROUND_TOP[2] + (BACKGROUND_BOTTOM[2] - BACKGROUND_TOP[2]) * t))
            pygame.draw.line(self.screen, color, (0, y), (width, y))

    def draw_shadow_rect(self, rect, radius=18, offset=5):
        shadow = rect.copy()
        shadow.x += offset
        shadow.y += offset
        pygame.draw.rect(self.screen, SHADOW, shadow, border_radius=radius)

    def scaled_rect(self, rect, scale):
        width = int(rect.width * scale)
        height = int(rect.height * scale)
        return pygame.Rect(rect.centerx - width // 2, rect.centery - height // 2, width, height)

    def draw_button(self, button_id, rect, text, accent=False, enabled=True):
        if not enabled:
            pygame.draw.rect(self.screen, (229, 234, 242), rect, border_radius=UI['button_radius'])
            self.text(text, rect.center, UI['body_size'], TEXT_SECONDARY)
            return
        hovered = rect.collidepoint(pygame.mouse.get_pos())
        pressing = hovered and pygame.mouse.get_pressed()[0]
        if pressing:
            target_scale = 0.97
        elif hovered:
            target_scale = 1.035
        else:
            target_scale = 1.0
        current_scale = self.button_scales.get(button_id, 1.0)
        current_scale = self.lerp(current_scale, target_scale, 0.2)
        self.button_scales[button_id] = current_scale
        draw_rect = self.scaled_rect(rect, current_scale)
        self.draw_shadow_rect(draw_rect, 14, 3)
        if accent:
            background = BLUE_DARK if hovered else BLUE
            text_color = WHITE
        else:
            background = (235, 240, 251) if hovered else CARD_BG
            text_color = TEXT_MAIN
        pygame.draw.rect(self.screen, background, draw_rect, border_radius=UI['button_radius'])
        pygame.draw.rect(self.screen, BLUE if accent else (197, 208, 225), draw_rect, 2, border_radius=UI['button_radius'])
        font = self.get_font(UI['body_size'], True)
        surface = font.render(text, True, text_color)
        self.screen.blit(surface, surface.get_rect(center=draw_rect.center))

    def draw_star(self, center_x, center_y, radius, filled):
        points = []
        for i in range(10):
            angle = -math.pi / 2 + i * math.pi / 5
            current_radius = radius if i % 2 == 0 else radius * 0.45
            points.append((int(center_x + math.cos(angle) * current_radius), int(center_y + math.sin(angle) * current_radius)))
        if filled:
            pygame.draw.polygon(self.screen, GOLD, points)
        else:
            pygame.draw.polygon(self.screen, STAR_EMPTY, points, 2)

    def draw_star_rating(self, center_x, center_y, stars, radius=13):
        gap = radius * 2 + 10
        start_x = center_x - gap
        for i in range(3):
            self.draw_star(start_x + i * gap, center_y, radius, i < stars)

    def get_arrow_color(self, direction):
        if direction == 'right':
            return BLUE
        elif direction == 'left':
            return PURPLE
        elif direction == 'up':
            return TEAL
        return ORANGE

    def get_cell_center(self, row, col):
        return (self.BOARD_X + col * self.CELL_SIZE + self.CELL_SIZE / 2, self.BOARD_Y + row * self.CELL_SIZE + self.CELL_SIZE / 2)

    def draw_arrow(self, arrow, offset_x=0, offset_y=0, color=None, scale=1.0):
        """用四倍分辨率绘制圆头箭线，再缩小获得平滑边缘。"""
        color = color if color is not None else self.get_arrow_color(arrow['direction'])
        # Quantize hover sizes so animation reuses a bounded sprite cache.
        scale = round(scale, 2)
        key = (self.CELL_SIZE, arrow['length'], arrow['direction'], tuple(color), scale)
        if not hasattr(self, '_arrow_sprites'):
            self._arrow_sprites = {}
        if key not in self._arrow_sprites:
            if len(self._arrow_sprites) >= 512:
                self._arrow_sprites.clear()
            cell = self.CELL_SIZE * scale
            length = (arrow['length'] - 1 + 0.47) * cell
            stroke = max(1.8, cell * 0.045)
            head = cell * 0.155
            wing = head * 0.8
            vx, vy = {'right': (1, 0), 'left': (-1, 0),
                      'down': (0, 1), 'up': (0, -1)}[arrow['direction']]
            start = (-vx * length / 2, -vy * length / 2)
            tip = (vx * length / 2, vy * length / 2)
            left = (tip[0] - vx * head - vy * wing,
                    tip[1] - vy * head + vx * wing)
            right = (tip[0] - vx * head + vy * wing,
                     tip[1] - vy * head - vx * wing)
            points = (start, tip, left, right)
            padding = stroke / 2 + 2
            width = math.ceil(max(abs(x) for x, y in points) * 2 + padding * 2)
            height = math.ceil(max(abs(y) for x, y in points) * 2 + padding * 2)
            factor = 4
            sprite = pygame.Surface((width * factor, height * factor), pygame.SRCALPHA)
            thickness = max(2, round(stroke * factor))

            def pixel(point):
                return (round((point[0] + width / 2) * factor),
                        round((point[1] + height / 2) * factor))

            for first, last in ((start, tip), (left, tip), (right, tip)):
                pygame.draw.line(sprite, color, pixel(first), pixel(last), thickness)
            for point in points:
                pygame.draw.circle(sprite, color, pixel(point), thickness // 2)
            self._arrow_sprites[key] = pygame.transform.smoothscale(sprite, (width, height))
        sprite = self._arrow_sprites[key]
        cells = get_arrow_cells(arrow)
        tail_x, tail_y = self.get_cell_center(*cells[0])
        head_x, head_y = self.get_cell_center(*cells[-1])
        center = ((tail_x + head_x) / 2 + offset_x, (tail_y + head_y) / 2 + offset_y)
        self.screen.blit(sprite, sprite.get_rect(center=(round(center[0]), round(center[1]))))

    def update_arrow_hover(self):
        if self.game.state != 'playing':
            return
        (mouse_x, mouse_y) = pygame.mouse.get_pos()
        hovered_arrow = None
        if self.BOARD_X <= mouse_x < self.BOARD_X + COLS * self.CELL_SIZE and self.BOARD_Y <= mouse_y < self.BOARD_Y + ROWS * self.CELL_SIZE:
            col = int((mouse_x - self.BOARD_X) // self.CELL_SIZE)
            row = int((mouse_y - self.BOARD_Y) // self.CELL_SIZE)
            hovered_arrow = self.game.find_arrow_at_cell(row, col)
        for (index, arrow) in enumerate(self.game.arrows):
            current = self.arrow_scales.get(index, 1.0)
            if arrow is hovered_arrow and self.game.flying_arrow is None and (self.game.collision_arrow is None):
                target = 1.08
            else:
                target = 1.0
            self.arrow_scales[index] = self.lerp(current, target, 0.18)

    def draw_start_page(self):
        (width, height) = self.screen.get_size()
        mode = self.get_layout_mode()
        t = pygame.time.get_ticks() / 1000
        decorative_items = [(0.17, 0.27, 'right', BLUE, 0), (0.83, 0.28, 'down', ORANGE, 1), (0.15, 0.73, 'up', TEAL, 2), (0.84, 0.72, 'left', PURPLE, 3)]
        for (rx, ry, direction, color, phase) in decorative_items:
            x = width * rx
            y = height * ry + math.sin(t + phase) * 7
            length = 40
            if direction == 'right':
                start = (x - length, y)
                end = (x + length, y)
            elif direction == 'left':
                start = (x + length, y)
                end = (x - length, y)
            elif direction == 'up':
                start = (x, y + length)
                end = (x, y - length)
            else:
                start = (x, y - length)
                end = (x, y + length)
            light_color = (min(255, color[0] + 105), min(255, color[1] + 105), min(255, color[2] + 105))
            pygame.draw.line(self.screen, light_color, start, end, 5)
        title_size = 48 if mode != 'compact' else 38
        title = self.get_font(title_size, True).render('一箭又一箭', True, TEXT_MAIN)
        self.screen.blit(title, title.get_rect(center=(width // 2, height // 2 - 90)))
        tag = self.get_font(18, True).render('休闲 · 解谜 · 挑战', True, BLUE)
        self.screen.blit(tag, tag.get_rect(center=(width // 2, height // 2 - 35)))
        description = self.get_font(17 if mode == 'compact' else 19).render('找准顺序，让所有箭头顺利逃离棋盘', True, TEXT_SECONDARY)
        if description.get_width() < width - 30:
            self.screen.blit(description, description.get_rect(center=(width // 2, height // 2 + 10)))
        for action, rect in self.buttons().items():
            self.draw_button(action, rect, '继续游戏' if action == 'resume' else '选择关卡',
                             action == ('resume' if self.game.has_progress else 'start'))

    def draw_board(self):
        padding = max(12, int(self.CELL_SIZE * 0.2))
        card = pygame.Rect(self.BOARD_X - padding, self.BOARD_Y - padding, COLS * self.CELL_SIZE + padding * 2, ROWS * self.CELL_SIZE + padding * 2)
        self.draw_shadow_rect(card, 21, 6)
        pygame.draw.rect(self.screen, CARD_BG, card, border_radius=21)
        board_rect = pygame.Rect(self.BOARD_X, self.BOARD_Y, COLS * self.CELL_SIZE, ROWS * self.CELL_SIZE)
        pygame.draw.rect(self.screen, BOARD_BG, board_rect, border_radius=8)
        for row in range(ROWS):
            for col in range(COLS):
                rect = pygame.Rect(self.BOARD_X + col * self.CELL_SIZE, self.BOARD_Y + row * self.CELL_SIZE, self.CELL_SIZE, self.CELL_SIZE)
                pygame.draw.rect(self.screen, GRID_COLOR, rect, 1)

    def draw_game_page(self):
        (width, height) = self.screen.get_size()
        mode = self.get_layout_mode()
        title = self.get_font(UI['title_size'], True).render('一箭又一箭', True, TEXT_MAIN)
        if mode == 'compact':
            self.screen.blit(title, title.get_rect(center=(width // 2, 26)))
        else:
            self.screen.blit(title, (25, 23))
        (level_button, restart_button, undo_button) = self.get_game_buttons()
        self.draw_button('关卡', level_button, '关卡')
        self.draw_button('重新开始', restart_button, '重新开始')
        self.draw_button('undo', undo_button, '撤销一步', enabled=self.game.can_undo)
        self.draw_game_stats()
        self.draw_board()
        for (index, arrow) in enumerate(self.game.arrows):
            scale = self.arrow_scales.get(index, 1.0)
            if arrow is self.game.collision_arrow:
                self.draw_arrow(arrow, self.game.collision_offset[0] * self.CELL_SIZE, self.game.collision_offset[1] * self.CELL_SIZE, RED, scale)
            else:
                self.draw_arrow(arrow, scale=scale)
        if self.game.flying_arrow is not None:
            self.draw_arrow(self.game.flying_arrow, self.game.flying_arrow['offset_x'] * self.CELL_SIZE, self.game.flying_arrow['offset_y'] * self.CELL_SIZE, scale=1.0)

    def draw_overlay(self):
        (width, height) = self.screen.get_size()
        overlay = pygame.Surface((width, height), pygame.SRCALPHA)
        overlay.fill((30, 38, 52, 130))
        self.screen.blit(overlay, (0, 0))

    def text(self, text, center, size=16, color=TEXT_MAIN, bold=False):
        font = self.get_font(size, bold)
        surface = font.render(text, True, color)
        self.screen.blit(surface, surface.get_rect(center=center))

    def update_board_layout(self):
        width, height = self.screen.get_size()
        top = 190 if width < 580 else 180
        self.CELL_SIZE = max(1, min(MAX_CELL_SIZE, (width - 48) // COLS,
                                    (height - top - 28) // ROWS))
        self.BOARD_X = (width - COLS * self.CELL_SIZE) // 2
        self.BOARD_Y = top + (height - top - 28 - ROWS * self.CELL_SIZE) // 2

    def get_start_button(self):
        width, height = self.screen.get_size()
        return pygame.Rect(width // 2 - 110, height // 2 + 90, 220, UI['button_height'])

    def get_game_buttons(self):
        width, _ = self.screen.get_size()
        gap = 10
        button_width = min(110, (width - 48 - gap * 2) // 3)
        total = button_width * 3 + gap * 2
        x, y = ((width - total) // 2, 58) if width < 580 else (width - 24 - total, 24)
        return tuple(pygame.Rect(x + i * (button_width + gap), y,
                                 button_width, UI['button_height']) for i in range(3))

    def draw_game_stats(self):
        width, _ = self.screen.get_size()
        gap = UI['gap']
        card_width = min(UI['stat_width'], (width - 48 - gap * 2) // 3)
        start = (width - 3 * card_width - 2 * gap) // 2
        y = 116 if width < 580 else 94
        stats = [('当前关卡', f'{self.game.current_level + 1} / {len(LEVELS)}', BLUE),
                 ('剩余失误', f'{self.game.mistakes_left} / {MAX_MISTAKES}', RED),
                 ('剩余箭头', str(len(self.game.arrows)), GREEN)]
        for i, (label, value, color) in enumerate(stats):
            rect = pygame.Rect(start + i * (card_width + gap), y, card_width, UI['stat_height'])
            self.draw_shadow_rect(rect, UI['card_radius'], 3)
            pygame.draw.rect(self.screen, CARD_BG, rect, border_radius=UI['card_radius'])
            self.text(label, (rect.centerx, y + 17), 14, TEXT_SECONDARY)
            self.text(value, (rect.centerx, y + 40), 20, color, True)

    def level_viewport(self):
        width, height = self.screen.get_size()
        return pygame.Rect(16, 180, width - 32, height - 204)

    def level_grid(self):
        width, _ = self.screen.get_size()
        columns = 4 if width >= 900 else 3 if width >= 660 else 2 if width >= 440 else 1
        gap = 14
        card_width = (width - 48 - (columns - 1) * gap) // columns
        return columns, gap, card_width, 166

    def max_level_scroll(self):
        columns, gap, _, card_height = self.level_grid()
        rows = math.ceil(len(LEVELS) / columns)
        return max(0, rows * (card_height + gap) - gap + 10 - self.level_viewport().height)

    def scroll_levels(self, amount):
        self.level_scroll = max(0, min(self.max_level_scroll(), self.level_scroll + amount))

    def get_level_card_rects(self):
        self.scroll_levels(0)
        columns, gap, card_width, card_height = self.level_grid()
        return [pygame.Rect(24 + (i % columns) * (card_width + gap),
                            185 + (i // columns) * (card_height + gap) - self.level_scroll,
                            card_width, card_height) for i in range(len(LEVELS))]

    def draw_level_card(self, index, rect):
        locked = index > self.game.unlocked_level
        hovered = rect.collidepoint(pygame.mouse.get_pos()) and self.level_viewport().collidepoint(pygame.mouse.get_pos()) and not locked
        scale = self.lerp(self.card_scales.get(index, 1), 1.018 if hovered else 1, 0.18)
        self.card_scales[index] = scale
        rect = self.scaled_rect(rect, scale)
        self.draw_shadow_rect(rect, UI['card_radius'], 3)
        pygame.draw.rect(self.screen, (237, 241, 247) if locked else CARD_BG,
                         rect, border_radius=UI['card_radius'])
        pygame.draw.rect(self.screen, BLUE if hovered else GRID_COLOR,
                         rect, 2, border_radius=UI['card_radius'])
        self.text(f'第 {index + 1} 关', (rect.centerx, rect.y + 26), 22, bold=True)
        self.text(LEVEL_NAMES[index], (rect.centerx, rect.y + 57), 14, TEXT_SECONDARY)
        if locked:
            self.text('尚未解锁', (rect.centerx, rect.y + 99), 18, TEXT_SECONDARY)
            self.text('完成上一关后解锁', (rect.centerx, rect.y + 139), 14, TEXT_SECONDARY)
        else:
            self.draw_star_rating(rect.centerx, rect.y + 89, self.game.level_stars[index], 10)
            self.text(f'{len(LEVELS[index])} 支箭头', (rect.centerx, rect.y + 117), 14, TEXT_SECONDARY)
            self.text('开始挑战', (rect.centerx, rect.y + 145), 16, BLUE, True)

    def draw_level_select(self):
        width, height = self.screen.get_size()
        self.draw_button('back', pygame.Rect(24, 24, 110, UI['button_height']), '返回')
        self.text('选择关卡', (width // 2, 90), UI['title_size'], bold=True)
        self.text('完成当前关卡，即可解锁下一关', (width // 2, 128), 16, TEXT_SECONDARY)
        self.text(f'累计星星  {sum(self.game.level_stars)} / {len(LEVELS) * 3}',
                  (width // 2, 156), 16, GOLD, True)
        previous_clip = self.screen.get_clip()
        viewport = self.level_viewport()
        self.screen.set_clip(viewport)
        for index, rect in enumerate(self.get_level_card_rects()):
            if rect.colliderect(viewport):
                self.draw_level_card(index, rect)
        self.screen.set_clip(previous_clip)
        maximum = self.max_level_scroll()
        if maximum:
            track = pygame.Rect(width - 10, viewport.y, 4, viewport.height)
            pygame.draw.rect(self.screen, GRID_COLOR, track, border_radius=2)
            thumb_height = max(24, int(viewport.height ** 2 / (viewport.height + maximum)))
            thumb = pygame.Rect(track.x, track.y + int(self.level_scroll / maximum * (track.height - thumb_height)), 4, thumb_height)
            pygame.draw.rect(self.screen, BLUE, thumb, border_radius=2)
            self.text('上下滚动查看全部关卡', (width // 2, height - 12), 13, TEXT_SECONDARY)

    def get_modal_rect(self):
        width, height = self.screen.get_size()
        w, h = min(450, width - 32), min(450, height - 32)
        elapsed = pygame.time.get_ticks() - self.state_enter_time
        offset = int(18 * (1 - self.ease_out_cubic(self.clamp(elapsed / 350, 0, 1))))
        return pygame.Rect((width - w) // 2, (height - h) // 2 + offset, w, h)

    def buttons(self):
        state = self.game.state
        if state == 'start':
            rect = self.get_start_button()
            if self.game.has_progress:
                return {'resume': rect, 'start': rect.move(0, 56)}
            return {'start': rect}
        if state == 'level_select':
            viewport = self.level_viewport()
            return dict([('back', pygame.Rect(24, 24, 110, UI['button_height']))] +
                        [(f'level_{i}', rect.clip(viewport)) for i, rect in enumerate(self.get_level_card_rects())
                         if i <= self.game.unlocked_level and rect.colliderect(viewport)])
        if state == 'playing':
            buttons = dict(zip(('levels', 'restart', 'undo'), self.get_game_buttons()))
            if not self.game.can_undo:
                buttons.pop('undo')
            return buttons
        actions = {'game_over': ['restart', 'levels'],
                   'level_complete': ['next', 'restart', 'levels'],
                   'all_clear': ['levels', 'replay']}[state]
        if state == 'game_over' and self.game.can_undo:
            actions.insert(0, 'undo')
        rect = self.get_modal_rect()
        return {action: pygame.Rect(rect.centerx - 110,
                                    rect.bottom - 24 - (len(actions) - i) * 56,
                                    220, UI['button_height'])
                for i, action in enumerate(actions)}

    def draw_modal(self):
        self.draw_overlay()
        rect = self.get_modal_rect()
        self.draw_shadow_rect(rect, UI['card_radius'], 5)
        pygame.draw.rect(self.screen, CARD_BG, rect, border_radius=UI['card_radius'])
        state = self.game.state
        title = {'game_over': '挑战失败', 'level_complete': '关卡完成', 'all_clear': '全部通关'}[state]
        self.text(title, (rect.centerx, rect.y + 48), 32, TEXT_MAIN, True)
        if state == 'game_over':
            self.text('失误次数已用完', (rect.centerx, rect.y + 118), 18, RED)
            self.text('再尝试一次吧', (rect.centerx, rect.y + 156), 16, TEXT_SECONDARY)
        elif state == 'level_complete':
            self.draw_star_rating(rect.centerx, rect.y + 112, self.game.earned_stars, 18)
            self.text(f'本关失误 {MAX_MISTAKES - self.game.mistakes_left} 次',
                      (rect.centerx, rect.y + 156), 16, TEXT_SECONDARY)
            self.text(f'第 {self.game.current_level + 2} 关已解锁',
                      (rect.centerx, rect.y + 199), 18, BLUE, True)
        else:
            self.draw_star_rating(rect.centerx, rect.y + 110, self.game.earned_stars, 18)
            self.text(f'已完成全部 {len(LEVELS)} 关',
                      (rect.centerx, rect.y + 164), 20, TEXT_MAIN, True)
            self.text(f'三星关卡 {sum(s == 3 for s in self.game.level_stars)} / {len(LEVELS)}',
                      (rect.centerx, rect.y + 204), 16, TEXT_SECONDARY)
            self.text(f'累计星星 {sum(self.game.level_stars)} / {len(LEVELS) * 3}',
                      (rect.centerx, rect.y + 246), 18, GOLD, True)
        labels = {'undo': '撤销一步', 'next': '继续下一关', 'restart': '重新挑战', 'levels': '返回关卡', 'replay': '再玩一次'}
        for i, (action, button) in enumerate(self.buttons().items()):
            self.draw_button(action, button, labels[action], i == 0)

    def get_sound_button(self):
        width, _ = self.screen.get_size()
        return pygame.Rect(width - 154, 24, 130, UI['button_height'])

    def render(self, transition_alpha=0):
        self.draw_background()
        if self.game.state == 'start':
            self.draw_start_page()
        elif self.game.state == 'level_select':
            self.draw_level_select()
        else:
            self.draw_game_page()
            if self.game.state != 'playing':
                self.draw_modal()
        if self.game.state in ('start', 'level_select'):
            available = getattr(self, 'sound_available', False)
            label = ('音效 开 · M' if self.game.sound_enabled else '音效 关 · M') if available else '音效不可用'
            self.draw_button('sound', self.get_sound_button(), label, enabled=available)
        if getattr(self, 'save_message', ''):
            width, height = self.screen.get_size()
            self.text(self.save_message, (width // 2, height - 14), 13, RED)
        if transition_alpha:
            fade = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
            fade.fill((*BACKGROUND_TOP, int(transition_alpha)))
            self.screen.blit(fade, (0, 0))
