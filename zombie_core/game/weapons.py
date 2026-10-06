import pygame
import math

from game.settings import (
    WEAPONS, BULLET_RADIUS, BULLET_SPEED, SCREEN_WIDTH, SCREEN_HEIGHT,
    SPITTER_PROJECTILE_SPEED, SPITTER_PROJECTILE_DAMAGE, SPIT_PROJECTILE_COLOR,
)


class Bullet:
    """Player-fired bullets/projectiles."""
    def __init__(self, pos, angle_degrees, damage, color):
        self.pos = pygame.Vector2(pos)
        angle_rad = math.radians(angle_degrees)
        self.velocity = pygame.Vector2(math.cos(angle_rad), -math.sin(angle_rad)) * BULLET_SPEED
        self.radius = BULLET_RADIUS
        self.damage = damage
        self.color = color
        self.alive = True

    def update(self, dt):
        self.pos += self.velocity * dt
        if (self.pos.x < 0 or self.pos.x > SCREEN_WIDTH or
                self.pos.y < 0 or self.pos.y > SCREEN_HEIGHT):
            self.alive = False

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (int(self.pos.x), int(self.pos.y)), self.radius)


class EnemyProjectile:
    """Fired by ranged zombies (spitter). Travels in a straight line
    toward wherever the player was at the moment of firing -- it does
    not home in, so moving after it's launched lets you dodge it."""

    def __init__(self, pos, target_pos):
        self.pos = pygame.Vector2(pos)
        direction = target_pos - self.pos
        if direction.length_squared() == 0:
            direction = pygame.Vector2(1, 0)
        self.velocity = direction.normalize() * SPITTER_PROJECTILE_SPEED
        self.radius = 6
        self.damage = SPITTER_PROJECTILE_DAMAGE
        self.alive = True

    def update(self, dt):
        self.pos += self.velocity * dt
        if (self.pos.x < 0 or self.pos.x > SCREEN_WIDTH or
                self.pos.y < 0 or self.pos.y > SCREEN_HEIGHT):
            self.alive = False

    def draw(self, screen):
        x, y = int(self.pos.x), int(self.pos.y)
        pygame.draw.circle(screen, SPIT_PROJECTILE_COLOR, (x, y), self.radius)
        pygame.draw.circle(screen, (210, 230, 170), (x, y), max(2, self.radius - 3))


def fire_weapon(player, bullets_list, noise_manager):
    """Spawns bullets for the player's current weapon (shotgun fires
    multiple pellets in a spread cone), consumes ammo, resets the
    fire-rate cooldown, and emits a noise event sized to the weapon."""
    stats = player.weapon_stats
    pellets = stats["pellets"]
    spread = stats["spread"]

    if pellets == 1:
        bullets_list.append(Bullet(player.pos, player.aim_angle, stats["damage"], stats["color"]))
    else:
        start_angle = player.aim_angle - spread / 2
        step = spread / (pellets - 1) if pellets > 1 else 0
        for i in range(pellets):
            angle = start_angle + step * i
            bullets_list.append(Bullet(player.pos, angle, stats["damage"], stats["color"]))

    if not player.god_mode:
        player.ammo[player.current_weapon] -= 1
    player.shoot_cooldown = stats["fire_rate"]
    noise_manager.emit(player.pos, stats["noise_radius"])
