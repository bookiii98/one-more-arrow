import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import pygame
from game_logic import Game, find_blocker, get_arrow_cells
from main import Application
from progress import ProgressStore, snapshot, restore


class ProgressTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.path = Path(self.directory.name) / 'saves' / 'progress.json'

    def roundtrip(self, game):
        ProgressStore(self.path).save(game)
        loaded = Game()
        ProgressStore(self.path).load(loaded)
        return loaded

    def test_flying_arrow_and_remaining_mistakes(self):
        game = Game()
        game.load_level(0)
        blocked = next(a for a in game.arrows if find_blocker(a, game.arrows)[0])
        game.click_cell(*get_arrow_cells(blocked)[0])
        loaded = self.roundtrip(game)
        loaded.resume()
        self.assertEqual(loaded.mistakes_left, 2)
        self.assertEqual(loaded.arrows, game.arrows)
        self.assertIsNone(loaded.collision_arrow)
        free = next(a for a in loaded.arrows if find_blocker(a, loaded.arrows)[0] is None)
        loaded.click_cell(*get_arrow_cells(free)[-1])
        reopened = self.roundtrip(loaded)
        self.assertEqual(len(reopened.arrows), 8)
        self.assertEqual(reopened.state, 'start')
        reopened.resume()
        self.assertEqual(reopened.state, 'playing')
        self.assertIsNone(reopened.flying_arrow)
        self.assertEqual(reopened.mistakes_left, 2)

    def test_last_arrow_saves_stars_and_unlock(self):
        game = Game()
        game.load_level(0)
        while len(game.arrows) > 1:
            arrow = next(a for a in game.arrows if find_blocker(a, game.arrows)[0] is None)
            game.click_cell(*get_arrow_cells(arrow)[0])
            game.update(10)
        game.click_cell(*get_arrow_cells(game.arrows[0])[0])
        loaded = self.roundtrip(game)
        self.assertEqual(loaded.level_stars[0], 3)
        self.assertEqual(loaded.unlocked_level, 1)
        loaded.resume()
        self.assertEqual(loaded.state, 'level_complete')
        loaded.load_level(0)
        self.assertEqual(self.roundtrip(loaded).level_stars[0], 3)

    def test_failed_collision_stays_failed(self):
        game = Game()
        game.load_level(0)
        game.mistakes_left = 1
        arrow = next(a for a in game.arrows if find_blocker(a, game.arrows)[0])
        game.click_cell(*get_arrow_cells(arrow)[0])
        loaded = self.roundtrip(game)
        loaded.resume()
        self.assertEqual(loaded.state, 'game_over')
        self.assertEqual(loaded.mistakes_left, 0)

    def test_corruption_and_invalid_board(self):
        self.path.parent.mkdir()
        for text in ['{broken', json.dumps({'version': 99}),
                     json.dumps(dict(snapshot(Game()), current={'level':0,'mistakes_left':3,'arrows':[{}]}))]:
            self.path.write_text(text)
            game = Game()
            store = ProgressStore(self.path)
            store.load(game)
            self.assertFalse(game.has_progress)
            self.assertTrue(store.message)
            store.save(game)
            self.assertEqual(self.path.read_text(), text)
        self.assertTrue(self.path.with_name('progress.json.damaged').exists())

    def test_atomic_failure_keeps_previous_save(self):
        game = Game()
        game.load_level(0)
        store = ProgressStore(self.path)
        store.save(game)
        previous = self.path.read_bytes()
        game.mistakes_left = 2
        with patch('progress.os.replace', side_effect=OSError('disk full')):
            store.save(game)
        self.assertEqual(self.path.read_bytes(), previous)
        self.assertTrue(store.message)
        self.assertEqual(list(self.path.parent.glob('.progress-*')), [])

    def test_home_continue_and_no_test_pollution(self):
        app = Application(save_path=self.path)
        self.addCleanup(pygame.quit)
        self.assertNotIn('resume', app.ui.buttons())
        app.apply_action('level_0')
        arrow = next(a for a in app.game.arrows if find_blocker(a, app.game.arrows)[0] is None)
        app.game.click_cell(*get_arrow_cells(arrow)[0])
        app.update(1 / 60)
        app.apply_action('levels')
        app.update(1 / 60)
        reopened = Application(save_path=self.path)
        self.assertIn('resume', reopened.ui.buttons())
        pos = reopened.ui.buttons()['resume'].center
        for kind in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP):
            reopened.handle_event(pygame.event.Event(kind, button=1, pos=pos))
        for _ in range(60):
            reopened.update(1 / 60)
        self.assertEqual(reopened.game.state, 'playing')
        self.assertEqual(len(reopened.game.arrows), 8)
        reopened.apply_action('levels')
        reopened.apply_action('back')
        reopened.handle_event(pygame.event.Event(pygame.VIDEORESIZE, w=320, h=520))
        reopened.ui.render()
        self.assertTrue(all(reopened.screen.get_rect().contains(r) for r in reopened.ui.buttons().values()))


if __name__ == '__main__':
    unittest.main()
