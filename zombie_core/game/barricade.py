"""
Barricades are placeable, damageable obstacles built during the day. 
If one sits roughly between a zombie and the player,the zombie attacks 
the barricade instead of walking straight through.

Barricades can be placed in either orientation (horizontal "_" or
vertical "|")
"""

import pygame
from game.settings import BARRICADE_MAX_HEALTH, BARRICADE_SIZE, WOOD_COLOR, BLACK, RED, GREEN


class Barricade:
    def __init__(self, x, y, vertical=False):
        self.pos = pygame.Vector2(x, y)
        self.max_health = BARRICADE_MAX_HEALTH
        self.health = BARRICADE_MAX_HEALTH
        self.vertical = vertical
        self._set_dimensions()

    def _set_dimensions(self):
        w, h = BARRICADE_SIZE
        # vertical orientation just swaps width/height so the same barricade can block either approach
        self.width, self.height = (h, w) if self.vertical else (w, h)

    @property
    def rect(self):
        return pygame.Rect(
            self.pos.x - self.width / 2, self.pos.y - self.height / 2,
            self.width, self.height,
        )

    def take_damage(self, amount):
        self.health = max(0, self.health - amount)

    def repair(self, amount):
        self.health = min(self.max_health, self.health + amount)

    @property
    def is_destroyed(self):
        return self.health <= 0

    def draw(self, screen):
        ratio = self.health / self.max_health
        color = (
            int(WOOD_COLOR[0] * (0.5 + 0.5 * ratio)),
            int(WOOD_COLOR[1] * (0.4 + 0.6 * ratio)),
            int(WOOD_COLOR[2] * 0.6),
        )
        rect = self.rect
        pygame.draw.rect(screen, color, rect, border_radius=2)
        pygame.draw.rect(screen, BLACK, rect, width=2, border_radius=2)

        if self.vertical:
            for i in range(1, 3):
                plank_y = rect.top + self.height * i / 3
                pygame.draw.line(screen, BLACK, (rect.left, plank_y), (rect.right, plank_y), 1)
        else:
            for i in range(1, 3):
                plank_x = rect.left + self.width * i / 3
                pygame.draw.line(screen, BLACK, (plank_x, rect.top), (plank_x, rect.bottom), 1)

        if self.health < self.max_health:
            self._draw_health_bar(screen, rect)

    def _draw_health_bar(self, screen, rect):
        bar_w = max(self.width, 24)
        bar_h = 4
        x = self.pos.x - bar_w / 2
        y = rect.top - 9
        ratio = self.health / self.max_health
        fill_color = GREEN if ratio > 0.3 else RED
        pygame.draw.rect(screen, (40, 40, 40), (x, y, bar_w, bar_h))
        pygame.draw.rect(screen, fill_color, (x, y, bar_w * ratio, bar_h))

    def draw_ghost(self, screen, can_afford):
        rect = self.rect
        ghost = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        color = (*WOOD_COLOR, 140) if can_afford else (200, 60, 60, 140)
        ghost.fill(color)
        screen.blit(ghost, rect.topleft)
        pygame.draw.rect(screen, BLACK, rect, width=2, border_radius=2)
