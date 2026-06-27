"""Simple sound manager — loads UI sounds once and plays them on demand."""

import os
from kivy.core.audio import SoundLoader

_SOUND_DIR = os.path.join(os.path.dirname(__file__), "sounds")


def _load(filename, volume=0.5):
    path = os.path.join(_SOUND_DIR, filename)
    snd = SoundLoader.load(path)
    if snd:
        snd.volume = volume
    return snd


# Load once at import time (re-loading on every tap causes lag)
_tap = _load("buttonclick.mp3", volume=0.5)
_click = _load("mouseclick.mp3", volume=0.5)


def play_tap():
    """UI tap — for navigation buttons and part cards."""
    if _tap:
        _tap.stop()
        _tap.play()


def play_click():
    """Distinct click — for the record button (stop) and primary actions."""
    if _click:
        _click.stop()
        _click.play()
