import copy
import unittest
import pygame
from game_logic import Game, find_blocker, get_arrow_cells
from progress import snapshot, restore, validate
from main import Application


class UndoTests(unittest.TestCase):
    def setUp(self):
        self.game = Game()
        self.game.load_level(0)

    def click(self, blocked=False):
        arrow = next(a for a in self.game.arrows
                     if (find_blocker(a, self.game.arrows)[0] is not None) == blocked)
        self.game.click_cell(*get_arrow_cells(arrow)[-1])

    def test_multiple_actions_and_animation_cancel(self):
        original = copy.deepcopy(self.game.arrows)
        self.assertFalse(self.game.undo())
        self.game.click_cell(-1, -1)
        self.assertEqual(self.game.history, [])
        self.click()
        self.game.click_cell(0, 0)
        self.assertEqual(len(self.game.history), 1)
        self.assertTrue(self.game.undo())
        self.assertEqual(self.game.arrows, original)
        self.assertIsNone(self.game.flying_arrow)
        self.click(True)
        self.assertTrue(self.game.undo())
        self.assertEqual(self.game.mistakes_left, 3)
        self.assertIsNone(self.game.collision_arrow)
        self.click(True)
        self.game.update(10)
        self.click()
        self.game.update(10)
        self.assertTrue(self.game.undo())
        self.assertEqual(self.game.mistakes_left, 2)
        self.assertEqual(self.game.arrows, original)
        self.assertTrue(self.game.undo())
        self.assertEqual(self.game.mistakes_left, 3)

    def test_failure_recovery_and_reset(self):
        for _ in range(3):
            self.click(True)
            self.game.update(10)
        self.assertEqual(self.game.state, 'game_over')
        self.assertTrue(self.game.undo())
        self.assertEqual((self.game.state, self.game.mistakes_left), ('playing', 1))
        self.game.load_level(0)
        self.assertFalse(self.game.can_undo)

    def test_saved_history_and_legacy_save(self):
        original = copy.deepcopy(self.game.arrows)
        self.click(True)
        self.game.update(10)
        self.click()
        saved = snapshot(self.game)
        validate(saved)
        loaded = Game()
        restore(loaded, saved)
        loaded.resume()
        self.assertTrue(loaded.undo())
        self.assertTrue(loaded.undo())
        self.assertEqual(loaded.arrows, original)
        self.assertEqual(loaded.mistakes_left, 3)
        legacy = copy.deepcopy(saved)
        legacy['current'].pop('history')
        restore(loaded, legacy)
        loaded.resume()
        self.assertFalse(loaded.can_undo)
        self.assertEqual(loaded.arrows, self.game.arrows)
        invalid = copy.deepcopy(saved)
        invalid['current']['history'][0]['arrows'] = []
        with self.assertRaises(ValueError):
            validate(invalid)

    def test_ui_button_and_failure_modal(self):
        app = Application(save_path=None)
        self.addCleanup(pygame.quit)
        app.game = self.game
        app.ui.game = self.game
        self.click(True)
        app.ui.render()
        pos = app.ui.buttons()['undo'].center
        for kind in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP):
            app.handle_event(pygame.event.Event(kind, pos=pos, button=1))
        self.assertEqual(self.game.mistakes_left, 3)
        self.assertNotIn('undo', app.ui.buttons())
        for _ in range(3):
            self.click(True)
            self.game.update(10)
        self.assertIn('undo', app.ui.buttons())
        app.handle_event(pygame.event.Event(pygame.VIDEORESIZE, w=320, h=520))
        app.ui.render()
        for rect in app.ui.buttons().values():
            self.assertTrue(app.screen.get_rect().contains(rect))
