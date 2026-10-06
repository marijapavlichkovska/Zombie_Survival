import math
import random

import pygame

from game.settings import (
    ZOMBIE_ATTACK_COOLDOWN, ZOMBIE_ATTACK_RANGE, DIRECT_SIGHT_RANGE,
    BARRICADE_BLOCK_RADIUS, SCREEN_WIDTH, SCREEN_HEIGHT,
    BOSS_ABILITY_COOLDOWN, BOSS_CHARGE_WINDUP, BOSS_CHARGE_SPEED,
    BOSS_CHARGE_DURATION, BOSS_CHARGE_DAMAGE, BOSS_CHARGE_MIN_DIST,
    BOSS_CHARGE_MAX_DIST, BOSS_SLAM_WINDUP, BOSS_SLAM_RADIUS, BOSS_SLAM_DAMAGE,
    BOSS_SUMMON_WINDUP, BOSS_SUMMON_COUNT, BOSS_SUMMON_SPREAD,
    BOSS_SUMMON_USES_PER_WAVE,
    RED, ORANGE, YELLOW, WHITE,
)
from game.zombie import Zombie


class BossZombie(Zombie):
    """
    Wave boss with three special attacks:
      Charge  — fast rush in a fixed direction (dodge sideways).
      Slam    — AOE after a windup (keep your distance).
      Summon  — spawns walker adds (crowd control).
    """

    def __init__(self, x, y, health_multiplier=1.0, speed_multiplier=1.0):
        super().__init__(x, y, "boss", health_multiplier, speed_multiplier)
        self.summon_health_mult = health_multiplier
        self.summon_speed_mult = speed_multiplier

        self.ability_cooldown = BOSS_ABILITY_COOLDOWN * 0.5
        self.special = None
        self.special_timer = 0.0
        self.charge_dir = pygame.Vector2(1, 0)
        self.charge_hit_player = False
        self.slam_dealt = False
        low, high = BOSS_SUMMON_USES_PER_WAVE
        self.summons_remaining = random.randint(low, high)

    def update(self, dt, player, noise_manager, barricades, enemy_projectiles, spawn_queue=None):
        if spawn_queue is None:
            spawn_queue = []

        if self.special is not None:
            self._update_special(dt, player, barricades, spawn_queue)
            self._animate(dt, self.special == "charge")
            return

        self.ability_cooldown -= dt
        distance_to_player = self.pos.distance_to(player.pos)
        blocking_barricade = self._find_blocking_barricade(player.pos, barricades)
        moving = False

        if blocking_barricade is not None:
            self.state = "attacking_barricade"
            target = blocking_barricade.pos
            dist = self.pos.distance_to(target)
            if dist > (self.size / 2 + blocking_barricade.width / 2 + ZOMBIE_ATTACK_RANGE):
                moving = self._move_toward(target, dt)
            else:
                self.attack_cooldown -= dt
                if self.attack_cooldown <= 0:
                    blocking_barricade.take_damage(self.contact_damage)
                    self.attack_cooldown = ZOMBIE_ATTACK_COOLDOWN
        elif distance_to_player <= DIRECT_SIGHT_RANGE:
            self.state = "chasing"
            if self.ability_cooldown <= 0:
                ability = self._pick_ability(distance_to_player)
                if ability is not None:
                    self._start_special(ability, player)
                else:
                    moving = self._move_toward(player.pos, dt)
            else:
                moving = self._move_toward(player.pos, dt)
        else:
            noise_pos = noise_manager.loudest_audible(self.pos, self.hearing_range)
            if noise_pos is not None:
                self.state = "investigating"
                moving = self._move_toward(noise_pos, dt)
            else:
                self.state = "wander"
                moving = self._wander(dt, player)

        if self.state == "chasing" and distance_to_player <= (
            self.size / 2 + player.size / 2 + ZOMBIE_ATTACK_RANGE
        ):
            self.attack_cooldown -= dt
            if self.attack_cooldown <= 0:
                player.take_damage(self.contact_damage)
                self.attack_cooldown = ZOMBIE_ATTACK_COOLDOWN

        self._animate(dt, moving)

    def _pick_ability(self, dist):
        options = []
        if dist <= BOSS_SLAM_RADIUS * 1.15:
            options.append("slam")
        if BOSS_CHARGE_MIN_DIST <= dist <= BOSS_CHARGE_MAX_DIST:
            options.append("charge")
        if self.summons_remaining > 0:
            options.append("summon")
        if not options:
            return None
        return random.choice(options)

    def _start_special(self, ability, player):
        self.ability_cooldown = BOSS_ABILITY_COOLDOWN
        self.slam_dealt = False
        self.charge_hit_player = False
        self.state = "chasing"

        if ability == "charge":
            direction = player.pos - self.pos
            if direction.length_squared() < 1:
                direction = pygame.Vector2(1, 0)
            else:
                direction = direction.normalize()
            self.charge_dir = direction
            self._face(direction)
            self.special = "charge_windup"
            self.special_timer = BOSS_CHARGE_WINDUP
        elif ability == "slam":
            self.special = "slam_windup"
            self.special_timer = BOSS_SLAM_WINDUP
        else:
            self.special = "summon_windup"
            self.special_timer = BOSS_SUMMON_WINDUP

    def _update_special(self, dt, player, barricades, spawn_queue):
        self.special_timer -= dt

        if self.special == "charge_windup":
            if self.special_timer <= 0:
                self.special = "charge"
                self.special_timer = BOSS_CHARGE_DURATION
        elif self.special == "charge":
            self.pos += self.charge_dir * BOSS_CHARGE_SPEED * dt
            self._clamp_to_screen()
            if not self.charge_hit_player:
                hit_dist = self.size / 2 + player.size / 2 + 4
                if self.pos.distance_to(player.pos) <= hit_dist:
                    player.take_damage(BOSS_CHARGE_DAMAGE)
                    self.charge_hit_player = True
            if self.special_timer <= 0:
                self.special = None
        elif self.special == "slam_windup":
            if self.special_timer <= 0:
                self.special = "slam_impact"
                self.special_timer = 0.2
                if not self.slam_dealt:
                    if self.pos.distance_to(player.pos) <= BOSS_SLAM_RADIUS:
                        player.take_damage(BOSS_SLAM_DAMAGE)
                    for barricade in barricades:
                        if barricade.is_destroyed:
                            continue
                        if self.pos.distance_to(barricade.pos) <= BOSS_SLAM_RADIUS:
                            barricade.take_damage(BOSS_SLAM_DAMAGE)
                    self.slam_dealt = True
        elif self.special == "slam_impact":
            if self.special_timer <= 0:
                self.special = None
        elif self.special == "summon_windup":
            if self.special_timer <= 0:
                self._spawn_walkers(spawn_queue)
                self.special = None

    def _spawn_walkers(self, spawn_queue):
        if self.summons_remaining <= 0:
            return
        self.summons_remaining -= 1
        for _ in range(BOSS_SUMMON_COUNT):
            offset = pygame.Vector2(
                random.uniform(-BOSS_SUMMON_SPREAD, BOSS_SUMMON_SPREAD),
                random.uniform(-BOSS_SUMMON_SPREAD, BOSS_SUMMON_SPREAD),
            )
            spawn_pos = self.pos + offset
            spawn_pos.x = max(20, min(SCREEN_WIDTH - 20, spawn_pos.x))
            spawn_pos.y = max(20, min(SCREEN_HEIGHT - 20, spawn_pos.y))
            spawn_queue.append(
                Zombie(
                    spawn_pos.x, spawn_pos.y,
                    "walker", self.summon_health_mult, self.summon_speed_mult,
                )
            )

    def _clamp_to_screen(self):
        half = self.size / 2
        self.pos.x = max(half, min(SCREEN_WIDTH - half, self.pos.x))
        self.pos.y = max(half, min(SCREEN_HEIGHT - half, self.pos.y))

    def draw(self, screen):
        self._draw_telegraphs(screen)
        super().draw(screen)
        if self.special is not None:
            self._draw_ability_label(screen)

    def _draw_telegraphs(self, screen):
        if self.special == "charge_windup":
            start = self.pos
            end = self.pos + self.charge_dir * 90
            pygame.draw.line(screen, RED, start, end, 4)
            pygame.draw.circle(screen, RED, (int(end.x), int(end.y)), 6)
        elif self.special == "charge":
            trail = self.pos - self.charge_dir * 28
            pygame.draw.line(screen, ORANGE, trail, self.pos, 6)
        elif self.special in ("slam_windup", "slam_impact"):
            progress = 1.0 - max(0.0, self.special_timer / BOSS_SLAM_WINDUP)
            if self.special == "slam_impact":
                progress = 1.0
            radius = int(BOSS_SLAM_RADIUS * (0.35 + 0.65 * progress))
            color = ORANGE if self.special == "slam_windup" else RED
            surf = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(surf, (*color, 70), (radius, radius), radius, 3)
            if self.special == "slam_impact":
                pygame.draw.circle(surf, (*RED, 120), (radius, radius), radius, 5)
            screen.blit(surf, (self.pos.x - radius, self.pos.y - radius))
        elif self.special == "summon_windup":
            pulse = 0.5 + 0.5 * math.sin(pygame.time.get_ticks() * 0.012)
            r = int(22 + 10 * pulse)
            pygame.draw.circle(screen, YELLOW, (int(self.pos.x), int(self.pos.y)), r, 2)

    def _draw_ability_label(self, screen):
        labels = {
            "charge_windup": "CHARGE",
            "charge": "CHARGE",
            "slam_windup": "SLAM",
            "slam_impact": "SLAM",
            "summon_windup": "SUMMON",
        }
        text = labels.get(self.special)
        if text is None:
            return
        font = pygame.font.SysFont(None, 18)
        label = font.render(text, True, WHITE)
        screen.blit(label, (self.rect.centerx - label.get_width() / 2, self.rect.top - 22))
