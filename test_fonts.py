import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import pygame
from config import find_font


class FontTests(unittest.TestCase):
    def test_windows_font_directory_and_fallback(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);fonts=root/'Fonts';fonts.mkdir()
            with patch.dict(os.environ, {'WINDIR': directory, 'ONE_MORE_ARROW_FONT': ''}):
                fallback=fonts/'simhei.ttf';fallback.touch()
                self.assertEqual(find_font(),str(fallback))
                preferred=fonts/'msyh.ttc';preferred.touch()
                self.assertEqual(find_font(),str(preferred))

    def test_custom_font_priority_and_missing_file(self):
        with tempfile.TemporaryDirectory() as directory:
            font=Path(directory)/'custom.ttf';font.touch()
            with patch.dict(os.environ, {'ONE_MORE_ARROW_FONT': str(font)}):
                self.assertEqual(find_font(),str(font))
            self.assertIsNone(find_font([str(font)+'.missing']))

    def test_available_font_renders_chinese(self):
        pygame.font.init()
        self.addCleanup(pygame.font.quit)
        path=find_font()
        self.assertIsNotNone(path)
        font=pygame.font.Font(path,20)
        self.assertTrue(all(metric is not None for metric in font.metrics('一箭又一箭')))
        self.assertGreater(font.render('选择关卡',True,(0,0,0)).get_width(),0)
