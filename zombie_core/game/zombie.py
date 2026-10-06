import pygame
import random

from game.settings import (
    ZOMBIE_TYPES, ZOMBIE_ATTACK_COOLDOWN, ZOMBIE_ATTACK_RANGE, DIRECT_SIGHT_RANGE,
    SPITTER_RANGE, SPITTER_FIRE_COOLDOWN, BLACK, RED, BARRICADE_BLOCK_RADIUS,
    ZOMBIE_ASSET_FOLDER, ZOMBIE_FRAME_SIZE, ZOMBIE_ANIM_SPEED,
)
from game.weapons import EnemyProjectile
from game.spritesheet import try_load_spritesheet


class Zombie:
    """
    AI priority order each frame:
      1. If a barricade is roughly blocking the path to the player, attack it.
      2. Else if within direct sight range of the player, chase directly.
      3. Else if noise is audible, walk toward the noise.
      4. Else wander aimlessly.
    Ranged zombies (spitter) skip contact-rushing and instead keep
    some distance while lobbing projectiles.
    """

    def __init__(self, x, y, zombie_type, health_multiplier=1.0, speed_multiplier=1.0):
        self.zombie_type = zombie_type
        stats = ZOMBIE_TYPES[zombie_type]

        self.pos = pygame.Vector2(x, y)
        self.size = stats["size"]
        self.speed = stats["speed"] * speed_multiplier
        self.max_health = stats["health"] * health_multiplier
        self.health = self.max_health
        self.contact_damage = stats["contact_damage"]
        self.color = stats["color"]
        self.currency_reward = stats["currency"]
        self.ranged = stats["ranged"]
        self.hearing_range = stats["hearing_range"]

        self.attack_cooldown = 0.0
        self.fire_cooldown = SPITTER_FIRE_COOLDOWN * random.uniform(0.5, 1.0)

        self.state = "wander"

        folder = ZOMBIE_ASSET_FOLDER.get(zombie_type, zombie_type)
        self.sprite_sheet = try_load_spritesheet(f"zombies/{folder}/walk.png", ZOMBIE_FRAME_SIZE, 4)
        self.direction = "down"
        self.frame_index = 0
        self.anim_timer = 0.0

    @property
    def rect(self):
        return pygame.Rect(
            self.pos.x - self.size / 2, self.pos.y - self.size / 2,
            self.size, self.size,
        )

    def _find_blocking_barricade(self, player_pos, barricades):
        """A barricade counts as 'blocking' if it's close to this
        zombie and roughly in the direction of the player."""
        for barricade in barricades:
            if barricade.is_destroyed:
                continue
            dist = self.pos.distance_to(barricade.pos)
            if dist < BARRICADE_BLOCK_RADIUS:
                to_player = player_pos - self.pos
                to_barricade = barricade.pos - self.pos
                if to_player.length_squared() == 0 or to_barricade.length_squared() == 0:
                    continue
                dot = to_player.normalize().dot(to_barricade.normalize())
                if dot > 0.6:
                    return barricade
        return None

    def update(self, dt, player, noise_manager, barricades, enemy_projectiles):
        distance_to_player = self.pos.distance_to(player.pos)
        blocking_barricade = self._find_blocking_barricade(player.pos, barricades)
        moving = False

        # --- decide state / target ---
        if blocking_barricade is not None:
            self.state = "attacking_barricade"
            target = blocking_barricade.pos
        elif distance_to_player <= DIRECT_SIGHT_RANGE:
            self.state = "chasing"
            target = player.pos
        else:
            noise_pos = noise_manager.loudest_audible(self.pos, self.hearing_range)
            if noise_pos is not None:
                self.state = "investigating"
                target = noise_pos
            else:
                self.state = "wander"
                target = None

        # --- ranged zombie behavior (spitter) ---
        if self.ranged:
            if self.state in ("chasing", "investigating") and target is not None:
                # keep some distance rather than closing all the way in
                if distance_to_player > SPITTER_RANGE * 0.6:
                    moving = self._move_toward(target, dt)
            elif self.state == "wander":
                moving = self._wander(dt, player)
            if self.state == "chasing" and distance_to_player <= SPITTER_RANGE and self.fire_cooldown <= 0:
                enemy_projectiles.append(EnemyProjectile(self.pos, player.pos))
                self.fire_cooldown = SPITTER_FIRE_COOLDOWN

        # --- zombie behavior for rest of the zombies ---
        else:
            if self.state == "attacking_barricade":
                dist = self.pos.distance_to(target)
                if dist > (self.size / 2 + blocking_barricade.width / 2 + ZOMBIE_ATTACK_RANGE):
                    moving = self._move_toward(target, dt)
                else:
                    self.attack_cooldown -= dt
                    if self.attack_cooldown <= 0:
                        blocking_barricade.take_damage(self.contact_damage)
                        self.attack_cooldown = ZOMBIE_ATTACK_COOLDOWN
            elif self.state in ("chasing", "investigating") and target is not None:
                moving = self._move_toward(target, dt)
            elif self.state == "wander":
                moving = self._wander(dt, player)

        if self.state == "chasing" and distance_to_player <= (self.size / 2 + player.size / 2 + ZOMBIE_ATTACK_RANGE):
            self.attack_cooldown -= dt
            if self.attack_cooldown <= 0:
                player.take_damage(self.contact_damage)
                self.attack_cooldown = ZOMBIE_ATTACK_COOLDOWN

        self._animate(dt, moving)

    def _move_toward(self, target_pos, dt):
        direction = target_pos - self.pos
        if direction.length_squared() > 1:
            direction = direction.normalize()
            self.pos += direction * self.speed * dt
            self._face(direction)
            return True
        return False

    def _wander(self, dt, player):
        """Ambient 'shambling' behavior: zombies always drift slowly
        toward the player's general direction even with no direct
        sight or audible noise, just slower than a full chase."""
        direction = player.pos - self.pos
        if direction.length_squared() > 1:
            direction = direction.normalize()
            self.pos += direction * (self.speed * 0.45) * dt
            self._face(direction)
            return True
        return False

    def _face(self, direction_vec):
        """Updates which way the sprite should face based on the
        current movement direction (used to pick down/up/left/right
        from the loaded walk-cycle sheet)."""
        if abs(direction_vec.x) > abs(direction_vec.y):
            self.direction = "right" if direction_vec.x > 0 else "left"
        else:
            self.direction = "down" if direction_vec.y > 0 else "up"

    def _animate(self, dt, moving):
        if self.sprite_sheet is None:
            return
        if moving:
            self.anim_timer += dt
            if self.anim_timer >= ZOMBIE_ANIM_SPEED:
                self.anim_timer = 0.0
                frames = self.sprite_sheet.get_frames(self.direction)
                self.frame_index = (self.frame_index + 1) % len(frames)
        else:
            self.frame_index = 0
            self.anim_timer = 0.0

    def take_damage(self, amount):
        self.health = max(0, self.health - amount)

    @property
    def is_dead(self):
        return self.health <= 0

    def draw(self, screen):
        if self.sprite_sheet is not None:
            frame = self.sprite_sheet.get_frames(self.direction)[self.frame_index]
            if frame.get_width() != self.size:
                frame = pygame.transform.scale(frame, (self.size, self.size))
            screen.blit(frame, self.rect.topleft)
        else:
            pygame.draw.rect(screen, self.color, self.rect, border_radius=3)
            pygame.draw.rect(screen, BLACK, self.rect, width=2, border_radius=3)

        if self.health < self.max_health:
            bar_w, bar_h = self.size, 5
            x = self.pos.x - bar_w / 2
            y = self.rect.top - 10
            ratio = self.health / self.max_health
            pygame.draw.rect(screen, (40, 40, 40), (x, y, bar_w, bar_h))
            pygame.draw.rect(screen, RED, (x, y, bar_w * ratio, bar_h))

        # "!" indicator: shown while this zombie is investigating a
        # noise it just heard, so you can see at a glance which zombies a
        # gunshot just alerted.
        if self.state == "investigating":
            self._draw_alert_icon(screen)

    def _draw_alert_icon(self, screen):
        icon_x = self.rect.right + 3
        icon_y = self.rect.top - 2
        pygame.draw.line(screen, RED, (icon_x, icon_y), (icon_x, icon_y + 6), 3)
        pygame.draw.circle(screen, RED, (icon_x, icon_y + 10), 2)
