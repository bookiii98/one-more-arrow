"""程序入口：初始化、页面状态协调与事件循环。"""
import pygame
from config import (WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_TITLE, FPS,
                    MIN_WINDOW_WIDTH, MIN_WINDOW_HEIGHT, TRANSITION_SPEED)
from game_logic import Game
from ui import GameUI
from audio import SoundEffects
from progress import ProgressStore, DEFAULT_SAVE_PATH


class Application:
    def __init__(self, save_path=DEFAULT_SAVE_PATH):
        pygame.mixer.pre_init(22050, -16, 2, 512)
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.RESIZABLE)
        pygame.display.set_caption(WINDOW_TITLE)
        self.clock = pygame.time.Clock()
        self.game = Game()
        self.progress = ProgressStore(save_path)
        self.progress.load(self.game)
        self.ui = GameUI(self.screen, self.game)
        self.audio = SoundEffects()
        self.ui.sound_available = self.audio.available
        self.running = True
        self.pressed = None
        self.transition = None
        self.alpha = 0
        self.last_state = self.game.state

    def navigate(self, action):
        if self.transition:
            return
        if action == 'sound':
            self.toggle_sound()
            return
        if action == 'undo':
            self.apply_action(action)
            self.pressed = None
            return
        self.pressed = None
        self.audio.play('click', self.game.sound_enabled)
        self.transition = (action, 'out')
        self.alpha = 0

    def apply_action(self, action):
        if action in ('start', 'levels'):
            self.game.state = 'level_select'
            self.ui.level_scroll = 0
        elif action == 'undo':
            if self.game.undo():
                self.audio.play('undo', self.game.sound_enabled)
        elif action == 'resume':
            self.game.resume()
        elif action == 'back':
            self.game.state = 'start'
        elif action == 'restart':
            self.game.load_level(self.game.current_level)
        elif action == 'next' and self.game.state == 'level_complete':
            self.game.load_level(self.game.current_level + 1)
        elif action == 'replay':
            self.game.load_level(0)
        elif action.startswith('level_'):
            self.game.load_level(int(action.split('_')[1]))
        self.ui.arrow_scales.clear()
        self.ui.state_enter_time = pygame.time.get_ticks()

    def toggle_sound(self):
        if not self.audio.available:
            return
        self.game.sound_enabled = not self.game.sound_enabled
        if self.game.sound_enabled:
            self.audio.play('click')
        else:
            self.audio.stop()
        self.progress.save(self.game)
        self.pressed = None

    def handle_event(self, event):
        if event.type == pygame.QUIT:
            self.running = False
            return
        if event.type == pygame.VIDEORESIZE:
            self.screen = pygame.display.set_mode(
                (max(MIN_WINDOW_WIDTH, event.w), max(MIN_WINDOW_HEIGHT, event.h)), pygame.RESIZABLE)
            self.ui.screen = self.screen
            self.ui.update_board_layout()
            self.pressed = None
            return
        if event.type == pygame.KEYDOWN and event.key == pygame.K_m:
            self.toggle_sound()
            return
        if self.transition:
            return
        if event.type == pygame.MOUSEWHEEL and self.game.state == 'level_select':
            self.ui.scroll_levels(-event.y * 48)
            self.pressed = None
            return
        if event.type not in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP) or event.button != 1:
            return
        buttons = self.ui.buttons()
        if self.game.state in ('start', 'level_select') and self.audio.available:
            buttons['sound'] = self.ui.get_sound_button()
        hit = next((key for key, rect in buttons.items() if rect.collidepoint(event.pos)), None)
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.pressed = hit
            if hit is None and self.game.state == 'playing':
                x, y = event.pos
                row = int((y - self.ui.BOARD_Y) // self.ui.CELL_SIZE)
                col = int((x - self.ui.BOARD_X) // self.ui.CELL_SIZE)
                before = len(self.game.history)
                self.game.click_cell(row, col)
                if len(self.game.history) > before:
                    self.audio.play('collision' if self.game.collision_arrow else 'fly', self.game.sound_enabled)
        else:
            if hit is not None and hit == self.pressed:
                self.navigate(hit)
            self.pressed = None

    def update(self, dt):
        self.ui.update_board_layout()
        if self.transition:
            action, phase = self.transition
            self.alpha += TRANSITION_SPEED * dt * (1 if phase == 'out' else -1)
            if phase == 'out' and self.alpha >= 255:
                self.alpha = 255
                self.apply_action(action)
                self.transition = (action, 'in')
            elif phase == 'in' and self.alpha <= 0:
                self.alpha = 0
                self.transition = None
        else:
            previous_state = self.game.state
            self.game.update(dt)
            if previous_state == 'playing' and self.game.state != previous_state:
                effect = {'level_complete': 'complete', 'all_clear': 'all_clear', 'game_over': 'failure'}.get(self.game.state)
                if effect:
                    self.audio.play(effect, self.game.sound_enabled)
        if self.game.state != self.last_state:
            self.ui.state_enter_time = pygame.time.get_ticks()
            self.pressed = None
            self.last_state = self.game.state
        self.ui.sound_available = self.audio.available
        self.ui.update_arrow_hover()
        self.progress.save(self.game)
        self.ui.save_message = self.progress.message

    def run(self):
        try:
            while self.running:
                dt = min(self.clock.tick(FPS) / 1000, 0.05)
                for event in pygame.event.get():
                    self.handle_event(event)
                self.update(dt)
                self.ui.render(self.alpha)
                pygame.display.flip()
        finally:
            self.progress.save(self.game)
            pygame.quit()


if __name__ == '__main__':
    Application().run()
