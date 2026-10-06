"""
Every noise-making action (walking, shooting) registers a NoiseEvent
here with a world position and a radius. Zombies query
NoiseManager.loudest_audible() each frame to find the best sound
within their hearing range, and path toward it instead of wandering
if nothing closer (like directly seeing the player) takes priority.

This is what makes weapon choice a real trade-off: a shotgun kills
fast but its big noise radius pulls in every zombie nearby, while a
pistol is quieter but weaker.
"""

import pygame
from game.settings import NOISE_DECAY_TIME


class NoiseEvent:
    def __init__(self, pos, radius, decay_time=NOISE_DECAY_TIME):
        self.pos = pygame.Vector2(pos)
        self.radius = radius
        self.timer = decay_time

    def update(self, dt):
        self.timer -= dt

    @property
    def expired(self):
        return self.timer <= 0


class NoiseManager:
    def __init__(self):
        self.events = []

    def emit(self, pos, radius, decay_time=NOISE_DECAY_TIME):
        self.events.append(NoiseEvent(pos, radius, decay_time))

    def update(self, dt):
        for event in self.events:
            event.update(dt)
        self.events = [e for e in self.events if not e.expired]

    def loudest_audible(self, listener_pos, hearing_range):
        """Returns the world position of the loudest noise event this
        listener can hear, or None. 'Loudest' = biggest radius minus
        distance, so a big gunshot far away can out-compete a quiet
        footstep close by."""
        best_pos = None
        best_score = 0

        for event in self.events:
            distance = listener_pos.distance_to(event.pos)
            audible_range = min(event.radius, hearing_range)
            if distance <= audible_range:
                score = event.radius - distance
                if best_pos is None or score > best_score:
                    best_score = score
                    best_pos = event.pos

        return best_pos
