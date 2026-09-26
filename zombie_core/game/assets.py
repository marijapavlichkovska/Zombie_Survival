"""
Loads images from assets/ by relative path, with caching so the same
file is never read from disk twice. If a file doesn't exist yet,
load_image() returns None instead of crashing -- every piece of code
that calls this is written to fall back to the old shape-drawing look
when that happens, so the game keeps running even for art you haven't
made yet.
"""

import pygame
import os

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(os.path.dirname(PROJECT_ROOT), "assets")

_image_cache = {}


def load_image(relative_path, size=None):
    """relative_path is relative to assets/, e.g. 'materials/wood.png'.
    Returns a pygame Surface, or None if the file isn't there."""
    key = (relative_path, size)
    if key in _image_cache:
        return _image_cache[key]

    full_path = os.path.join(ASSETS_DIR, relative_path)
    if not os.path.isfile(full_path):
        _image_cache[key] = None
        return None

    try:
        img = pygame.image.load(full_path).convert_alpha()
        if size is not None:
            img = pygame.transform.smoothscale(img, size)
    except pygame.error:
        img = None

    _image_cache[key] = img
    return img
