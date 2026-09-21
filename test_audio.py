import unittest
import wave
from unittest.mock import patch, Mock
import pygame
from audio import SoundEffects, EFFECTS, make_wave
from main import Application
from game_logic import Game, find_blocker, get_arrow_cells
from progress import snapshot, restore


class AudioTests(unittest.TestCase):
    def test_generated_clips_and_device_failure(self):
        for notes in EFFECTS.values():
            with wave.open(make_wave(notes)) as wav:
                self.assertEqual(wav.getnchannels(), 1)
                self.assertTrue(0 < wav.getnframes() / wav.getframerate() <= 1)
        with patch('pygame.mixer.get_init', return_value=None), patch('pygame.mixer.init', side_effect=pygame.error('no audio')):
            audio=SoundEffects()
            self.assertFalse(audio.available)
            audio.play('click')
            audio.stop()

    def test_mute_persistence_and_click_events(self):
        app=Application(save_path=None)
        self.addCleanup(pygame.quit)
        app.audio.play=Mock()
        app.audio.stop=Mock()
        app.handle_event(pygame.event.Event(pygame.KEYDOWN,key=pygame.K_m))
        self.assertFalse(app.game.sound_enabled)
        app.audio.stop.assert_called_once()
        loaded=Game();restore(loaded,snapshot(app.game))
        self.assertFalse(loaded.sound_enabled)
        old=snapshot(app.game);old.pop('sound_enabled')
        restore(loaded,old)
        self.assertTrue(loaded.sound_enabled)
        pos=app.ui.get_sound_button().center
        for kind in (pygame.MOUSEBUTTONDOWN,pygame.MOUSEBUTTONUP):
            app.handle_event(pygame.event.Event(kind,button=1,pos=pos))
        self.assertTrue(app.game.sound_enabled)
        app.apply_action('level_0')
        arrow=next(a for a in app.game.arrows if find_blocker(a,app.game.arrows)[0] is None)
        pos=app.ui.get_cell_center(*get_arrow_cells(arrow)[0])
        app.audio.play.reset_mock()
        app.handle_event(pygame.event.Event(pygame.MOUSEBUTTONDOWN,button=1,pos=pos))
        app.audio.play.assert_called_once_with('fly',True)
        app.handle_event(pygame.event.Event(pygame.MOUSEBUTTONDOWN,button=1,pos=pos))
        self.assertEqual(app.audio.play.call_count,1)
        app.apply_action('undo')
        app.audio.play.assert_called_with('undo',True)

    def test_end_feedback_once_and_muted_playback(self):
        app=Application(save_path=None)
        self.addCleanup(pygame.quit)
        app.apply_action('level_0')
        app.audio.play=Mock()
        app.game.arrows=[]
        app.update(.016);app.update(.016)
        app.audio.play.assert_called_once_with('complete',True)
        audio=SoundEffects()
        fake=Mock();audio.sounds['click']=fake
        audio.play('click',False)
        fake.play.assert_not_called()
        audio.play('click',True)
        fake.play.assert_called_once()
