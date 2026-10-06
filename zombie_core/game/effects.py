"""Hit flashes, death poofs, and other short-lived visuals."""

import pygame

from game.settings import HURT_FLASH_DURATION, DEATH_POOF_DURATION


def draw_hurt_overlay(screen, center_pos, size):
    """Red transparent flash on player/zombie when damaged."""
    if size <= 0:
        return
    pad = 4
    dim = int(size + pad)
    surf = pygame.Surface((dim, dim), pygame.SRCALPHA)
    pygame.draw.ellipse(surf, (220, 30, 30, 115), surf.get_rect())
    screen.blit(surf, (int(center_pos.x - dim / 2), int(center_pos.y - dim / 2)))


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
