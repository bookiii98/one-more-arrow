import copy
import unittest
from game_logic import Game, find_blocker, get_arrow_cells
from levels import LEVELS, LEGACY_BASIC_LEVELS
from progress import snapshot, restore


class BasicLevelTests(unittest.TestCase):
    def test_three_single_cell_levels(self):
        for i, level in enumerate(LEVELS[:3]):
            self.assertEqual(len(level), [9, 11, 13][i])
            self.assertTrue(all(a['length'] == 1 for a in level))
            self.assertEqual({a['direction'] for a in level}, {'up','down','left','right'})
            self.assertTrue(any(find_blocker(a, level)[0] is not None for a in level))
        self.assertTrue(all(any(a['length'] > 1 for a in level) for level in LEVELS[3:]))

    def test_old_board_and_history_migration(self):
        for i in range(3):
            game=Game();game.unlocked_level=i;game.load_level(i)
            game.level_stars[:i]=[3]*i
            game.arrows=copy.deepcopy(LEGACY_BASIC_LEVELS[i])
            free=next(a for a in game.arrows if find_blocker(a,game.arrows)[0] is None)
            game.click_cell(*get_arrow_cells(free)[0]);game.update(10)
            data=snapshot(game)
            loaded=Game();restore(loaded,data);loaded.resume()
            self.assertEqual(len(loaded.arrows),len(LEVELS[i])-1)
            self.assertTrue(all(a['length']==1 for a in loaded.arrows))
            self.assertEqual(loaded.history,[])
            self.assertEqual(loaded.level_stars,game.level_stars)
            self.assertEqual(loaded.unlocked_level,i)
            free=next(a for a in loaded.arrows if find_blocker(a,loaded.arrows)[0] is None)
            loaded.click_cell(*get_arrow_cells(free)[0])
            self.assertTrue(loaded.undo())
            restore(Game(),snapshot(loaded))
