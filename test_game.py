"""运行：SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy python3 -m unittest -v"""
import unittest
import pygame
from game_logic import Game, get_arrow_cells, find_blocker
from levels import LEVELS
from main import Application


class GameTests(unittest.TestCase):
    def test_levels_and_multicell_hits(self):
        game = Game()
        for index, data in enumerate(LEVELS):
            cells = [cell for arrow in data for cell in get_arrow_cells(arrow)]
            self.assertEqual(len(cells), len(set(cells)))
            self.assertTrue(all(0 <= r < 7 and 0 <= c < 7 for r, c in cells))
            game.unlocked_level = index
            game.load_level(index)
            for arrow in game.arrows:
                for row, col in get_arrow_cells(arrow):
                    self.assertIs(game.find_arrow_at_cell(row, col), arrow)
            while game.arrows:
                arrow = next((a for a in game.arrows if find_blocker(a, game.arrows)[0] is None), None)
                self.assertIsNotNone(arrow, '关卡必须存在可行消除顺序')
                game.click_cell(*get_arrow_cells(arrow)[-1])
                for _ in range(180):
                    game.update(1 / 60)
            self.assertEqual(game.earned_stars, 3)
            self.assertEqual(game.state, 'all_clear' if index == len(LEVELS) - 1 else 'level_complete')
        self.assertEqual(game.level_stars, [3] * len(LEVELS))

    def test_collision_failure_and_restart(self):
        game = Game()
        self.assertFalse(game.load_level(1))
        game.load_level(0)
        original = [a.copy() for a in game.arrows]
        arrow = next(a for a in game.arrows if find_blocker(a, game.arrows)[0])
        for _ in range(3):
            game.click_cell(*get_arrow_cells(arrow)[0])
            game.click_cell(*get_arrow_cells(arrow)[0])
            for _ in range(40):
                game.update(1 / 60)
        self.assertEqual(game.mistakes_left, 0)
        self.assertEqual(game.state, 'game_over')
        self.assertEqual(game.arrows, original)
        game.load_level(0)
        self.assertEqual(game.mistakes_left, 3)
        self.assertIsNone(game.collision_arrow)


class InterfaceTests(unittest.TestCase):
    def setUp(self):
        self.app = Application(save_path=None)

    def tearDown(self):
        pygame.quit()

    def settle(self):
        for _ in range(60):
            self.app.update(1 / 60)

    def click(self, action):
        pos = self.app.ui.buttons()[action].center
        for kind in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP):
            pygame.event.post(pygame.event.Event(kind, button=1, pos=pos))
        for event in pygame.event.get():
            self.app.handle_event(event)
        self.settle()

    def solve(self):
        game = self.app.game
        while game.arrows:
            arrow = next(a for a in game.arrows if find_blocker(a, game.arrows)[0] is None)
            row, col = get_arrow_cells(arrow)[-1]
            pos = self.app.ui.get_cell_center(row, col)
            for kind in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP):
                self.app.handle_event(pygame.event.Event(kind, button=1, pos=pos))
            for _ in range(180):
                self.app.update(1 / 60)

    def test_full_event_flow(self):
        game = self.app.game
        self.assertEqual(game.state, 'start')
        self.click('start')
        self.assertEqual(game.state, 'level_select')
        self.assertNotIn('level_1', self.app.ui.buttons())
        self.click('level_0')
        self.assertEqual(game.state, 'playing')
        self.solve()
        self.assertEqual(game.state, 'level_complete')
        self.assertEqual(game.level_stars[0], 3)
        self.click('restart')
        self.assertEqual(game.current_level, 0)
        self.assertEqual(len(game.arrows), 9)
        self.solve()
        self.click('levels')
        self.assertEqual(game.state, 'level_select')
        self.assertIn('level_1', self.app.ui.buttons())
        self.click('level_0')
        self.solve()
        self.click('next')
        self.assertEqual((game.state, game.current_level), ('playing', 1))
        self.solve()
        self.click('next')
        self.assertEqual(game.current_level, 2)
        self.solve()
        for index in range(3, len(LEVELS)):
            self.click('next')
            self.assertEqual(game.current_level, index)
            self.solve()
        self.assertEqual(game.state, 'all_clear')
        self.click('replay')
        self.assertEqual((game.state, game.current_level), ('playing', 0))
        self.assertEqual(game.level_stars, [3] * len(LEVELS))

    def test_run_and_quit(self):
        pygame.event.post(pygame.event.Event(pygame.QUIT))
        self.app.run()
        self.assertFalse(self.app.running)

    def test_responsive_render(self):
        for width, height in [(960,800), (700,600), (320,520), (580,520), (1280,720)]:
            self.app.handle_event(pygame.event.Event(pygame.VIDEORESIZE, w=width, h=height))
            for state in ['start','level_select','playing','game_over','level_complete','all_clear']:
                self.app.game.state = state
                self.app.ui.render()
                bounds = self.app.screen.get_rect()
                for rect in self.app.ui.buttons().values():
                    self.assertTrue(bounds.contains(rect), (width, height, state, rect))
                if state == 'level_select':
                    self.assertEqual(len(self.app.ui.get_level_card_rects()), len(LEVELS))
                if state == 'playing':
                    ui = self.app.ui
                    self.assertTrue(bounds.contains(pygame.Rect(ui.BOARD_X-12, ui.BOARD_Y-12,
                                                               ui.CELL_SIZE*7+24, ui.CELL_SIZE*7+24)))


if __name__ == '__main__':
    unittest.main()
