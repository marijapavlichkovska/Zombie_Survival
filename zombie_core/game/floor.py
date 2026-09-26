"""
Renders a tiled floor with some visual depth (alternating tile shades,
grout lines, and thicker panel seams every few tiles) instead of a
flat single-color fill -- loosely inspired by the concrete-tile look
of top-down shooter floors.

The floor never changes at runtime, so we build it once into a cached
Surface and just blit that every frame rather than redrawing every
tile 60 times a second.
"""

import pygame
import random

from game.settings import (
    SCREEN_WIDTH, SCREEN_HEIGHT, GROUND_TILE_SIZE,
    GROUND_COLOR, GROUND_COLOR_ALT, GROUND_GROUT_COLOR, GROUND_SEAM_COLOR,
)

_cached_floor = None


def _build_floor_surface():
    surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    tile = GROUND_TILE_SIZE
    cols = SCREEN_WIDTH // tile + 2
    rows = SCREEN_HEIGHT // tile + 2

    rng = random.Random(1234)  # fixed seed so the floor looks the same every run

    for row in range(rows):
        for col in range(cols):
            x, y = col * tile, row * tile
            # checkerboard base shade
            base = GROUND_COLOR if (row + col) % 2 == 0 else GROUND_COLOR_ALT

            # tiny per-tile brightness variation so it doesn't look
            # like a perfectly repeating pattern -- this is most of
            # what gives it "dimension" versus a flat fill
            jitter = rng.randint(-4, 4)
            color = tuple(max(0, min(255, c + jitter)) for c in base)

            pygame.draw.rect(surface, color, (x, y, tile, tile))

            # thin grout line around every tile
            pygame.draw.rect(surface, GROUND_GROUT_COLOR, (x, y, tile, tile), 1)

            # occasional small darker speckle (dirt/wear) for extra texture
            if rng.random() < 0.12:
                speck_w = rng.randint(4, 10)
                speck_h = rng.randint(3, 7)
                speck_x = x + rng.randint(4, tile - speck_w - 4)
                speck_y = y + rng.randint(4, tile - speck_h - 4)
                speck_color = tuple(max(0, c - 14) for c in color)
                pygame.draw.rect(surface, speck_color, (speck_x, speck_y, speck_w, speck_h))

    # thicker panel seams every 4 tiles, both directions, for the
    # bigger "floor panel" structure seen in the reference image
    panel_span = tile * 4
    for x in range(0, SCREEN_WIDTH + panel_span, panel_span):
        pygame.draw.line(surface, GROUND_SEAM_COLOR, (x, 0), (x, SCREEN_HEIGHT), 3)
    for y in range(0, SCREEN_HEIGHT + panel_span, panel_span):
        pygame.draw.line(surface, GROUND_SEAM_COLOR, (0, y), (SCREEN_WIDTH, y), 3)

    return surface


def get_floor_surface():
    """Returns the cached floor Surface, building it on first call."""
    global _cached_floor
    if _cached_floor is None:
        _cached_floor = _build_floor_surface()
    return _cached_floor


def draw_floor(screen):
    screen.blit(get_floor_surface(), (0, 0))
