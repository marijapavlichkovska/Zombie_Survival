"""Draw static character_designs PNGs until animated walk sheets return."""

import pygame

from game.assets import load_image


def load_character_design(design_key, paths):
    """design_key matches game ids (player, walker, boss, ...)."""
    relative = paths.get(design_key)
    if relative is None:
        return None
    return load_image(relative)


def draw_character_design(screen, image, center_pos, size, direction):
    """Blits a design PNG scaled to size; flips horizontally when facing left."""
    if image is None:
        return False

    frame = image
    if direction == "left":
        frame = pygame.transform.flip(image, True, False)
    if frame.get_width() != size or frame.get_height() != size:
        frame = pygame.transform.smoothscale(frame, (size, size))

    rect = frame.get_rect(center=(int(center_pos.x), int(center_pos.y)))
    screen.blit(frame, rect)
    return True
