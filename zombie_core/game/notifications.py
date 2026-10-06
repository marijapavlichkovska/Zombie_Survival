"""
Small transient on-screen messages used to show thingslike "Repair 
costs 8 wood (you have 3)" for a couple seconds instead of a permanent 
UI element. Anything can push a message; they fade outand remove 
themselves automatically.
"""

import pygame
from game.settings import TOAST_DURATION, SCREEN_WIDTH, WHITE, BLACK


class Notifications:
    def __init__(self):
        self.messages = []

    def add(self, text, color=WHITE, duration=TOAST_DURATION):
        self.messages.append([text, color, duration])

    def update(self, dt):
        for msg in self.messages:
            msg[2] -= dt
        self.messages = [m for m in self.messages if m[2] > 0]

    def draw(self, screen, font):
        # stack messages upward from just above the shop hint area
        y = 480
        for text, color, timer in reversed(self.messages):
            alpha = 255 if timer > 0.5 else int(255 * (timer / 0.5))
            surf = font.render(text, True, color)
            surf.set_alpha(alpha)
            bg = pygame.Surface((surf.get_width() + 16, surf.get_height() + 8), pygame.SRCALPHA)
            bg.fill((0, 0, 0, min(160, alpha)))
            x = SCREEN_WIDTH / 2 - bg.get_width() / 2
            screen.blit(bg, (x, y))
            screen.blit(surf, (x + 8, y + 4))
            y -= bg.get_height() + 4
