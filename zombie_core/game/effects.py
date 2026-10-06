"""Hit flashes, death poofs, and other short-lived visuals."""

import pygame

from game.settings import HURT_FLASH_DURATION, DEATH_POOF_DURATION
from game.character_sprite import prepare_character_frame


def draw_hurt_overlay(screen, center_pos, size, sprite=None, direction="down"):
    """Red transparent flash on player/zombie when damaged."""
    if size <= 0:
        return

    frame = prepare_character_frame(sprite, size, direction) if sprite is not None else None
    if frame is not None:
        colored = pygame.Surface(frame.get_size(), pygame.SRCALPHA)
        colored.fill((220, 30, 30, 115))
        colored.blit(frame, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        screen.blit(colored, colored.get_rect(center=(int(center_pos.x), int(center_pos.y))))
        return

    dim = int(size)
    surf = pygame.Surface((dim, dim), pygame.SRCALPHA)
    pygame.draw.rect(surf, (220, 30, 30, 115), surf.get_rect(), border_radius=3)
    screen.blit(surf, surf.get_rect(center=(int(center_pos.x), int(center_pos.y))))


class DeathPoof:
    """White puff shown when a zombie is killed."""

    def __init__(self, x, y, size):
        self.pos = pygame.Vector2(x, y)
        self.base_size = max(size, 28)
        self.timer = DEATH_POOF_DURATION

    def update(self, dt):
        self.timer -= dt
        return self.timer > 0

    def draw(self, screen):
        if self.timer <= 0:
            return
        progress = 1.0 - (self.timer / DEATH_POOF_DURATION)
        for ring, scale in enumerate((0.45, 0.72, 1.0)):
            radius = int(self.base_size * scale * (0.35 + progress * 0.95))
            alpha = int(200 * (1.0 - progress) * (1.0 - ring * 0.22))
            if alpha <= 0 or radius <= 0:
                continue
            surf = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(surf, (255, 255, 255, alpha), (radius, radius), radius)
            screen.blit(surf, (self.pos.x - radius, self.pos.y - radius))


def tick_hurt_flash(entity, dt):
    flash = getattr(entity, "hurt_flash", 0.0)
    if flash > 0:
        entity.hurt_flash = max(0.0, flash - dt)


def trigger_hurt_flash(entity):
    entity.hurt_flash = HURT_FLASH_DURATION
