"""本地合成短音效，无外部素材；声卡不可用时自动静音运行。"""
from array import array
from io import BytesIO
import math
import sys
import wave
import pygame

SAMPLE_RATE = 22050
# (起始频率、结束频率、秒数)，逐段连接形成提示音。
EFFECTS = {
    'click': [(780, 620, .055)],
    'fly': [(420, 1120, .16)],
    'collision': [(200, 120, .13)],
    'undo': [(640, 360, .12)],
    'complete': [(523, 523, .11), (659, 659, .11), (784, 784, .22)],
    'all_clear': [(523, 523, .1), (659, 659, .1), (784, 784, .1), (1047, 1047, .3)],
    'failure': [(330, 330, .14), (247, 196, .22)],
}


def make_wave(notes):
    samples = array('h')
    for start, end, duration in notes:
        count = round(duration * SAMPLE_RATE)
        phase = 0
        for i in range(count):
            t = i / max(1, count - 1)
            phase += 2 * math.pi * (start + (end - start) * t) / SAMPLE_RATE
            # Soft attack/release prevent clicks at segment boundaries.
            envelope = min(1, t / .12, (1 - t) / .3)
            value = math.sin(phase) + .12 * math.sin(phase * 2)
            samples.append(round(7000 * envelope * value))
    if sys.byteorder != 'little':
        samples.byteswap()
    output = BytesIO()
    with wave.open(output, 'wb') as stream:
        stream.setnchannels(1)
        stream.setsampwidth(2)
        stream.setframerate(SAMPLE_RATE)
        stream.writeframes(samples.tobytes())
    output.seek(0)
    return output


class SoundEffects:
    def __init__(self):
        self.sounds = {}
        self.available = False
        try:
            if pygame.mixer.get_init() is None:
                pygame.mixer.init(frequency=SAMPLE_RATE, size=-16, channels=2, buffer=512)
            self.sounds = {name: pygame.mixer.Sound(file=make_wave(notes))
                           for name, notes in EFFECTS.items()}
            for sound in self.sounds.values():
                sound.set_volume(.45)
            self.available = True
        except pygame.error:
            self.sounds.clear()

    def play(self, name, enabled=True):
        if not enabled or not self.available:
            return
        try:
            self.sounds[name].play()
        except pygame.error:
            self.available = False

    def stop(self):
        if self.available:
            for sound in self.sounds.values():
                sound.stop()
