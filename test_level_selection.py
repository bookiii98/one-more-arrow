import copy
import unittest
import pygame
from main import Application
from game_logic import Game
from levels import LEVELS
from progress import snapshot, restore, validate


class SelectionTests(unittest.TestCase):
    def test_legacy_completed_and_partial_progress(self):
        for stars, unlocked in [([3,2,1],2),([3,0,0],1),([0,0,0],0)]:
            data={'version':1,'level_stars':stars,'unlocked_level':unlocked,'current':None}
            loaded=Game()
            restore(loaded,data)
            self.assertEqual(loaded.level_stars, stars + [0]*9)
            self.assertEqual(loaded.unlocked_level,3 if stars[-1] else unlocked)
            validate(snapshot(loaded))
        game=Game();game.load_level(0)
        data=snapshot(game);data['level_stars']=data['level_stars'][:3]
        restore(game,data)
        self.assertEqual(game.arrows,LEVELS[0])

    def test_single_grid_and_scroll_selection(self):
        app=Application(save_path=None)
        self.addCleanup(pygame.quit)
        app.apply_action('start')
        self.assertFalse(any(k.startswith('page_') for k in app.ui.buttons()))
        self.assertEqual(len(app.ui.get_level_card_rects()),12)
        self.assertTrue(all(app.ui.level_viewport().contains(r) for r in app.ui.get_level_card_rects()))
        self.assertNotIn('level_11',app.ui.buttons())
        app.game.unlocked_level=11
        app.handle_event(pygame.event.Event(pygame.VIDEORESIZE,w=320,h=520))
        self.assertNotIn('level_11',app.ui.buttons())
        app.handle_event(pygame.event.Event(pygame.MOUSEWHEEL,y=-100))
        self.assertIn('level_11',app.ui.buttons())
        self.assertNotIn('level_0',app.ui.buttons())
        app.ui.render()
        for key,rect in app.ui.buttons().items():
            self.assertTrue(app.screen.get_rect().contains(rect))
        pos=app.ui.buttons()['level_11'].center
        for kind in (pygame.MOUSEBUTTONDOWN,pygame.MOUSEBUTTONUP):
            app.handle_event(pygame.event.Event(kind,button=1,pos=pos))
        for _ in range(60):app.update(1/60)
        self.assertEqual(app.game.current_level,11)
        app.apply_action('levels')
        app.ui.scroll_levels(9999)
        app.handle_event(pygame.event.Event(pygame.VIDEORESIZE,w=960,h=800))
        app.ui.render()
        self.assertEqual(app.ui.level_scroll,0)
