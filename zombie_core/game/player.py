import pygame
import math

from game.settings import (
    PLAYER_SIZE, PLAYER_SPEED, PLAYER_MAX_HEALTH,
    SCREEN_WIDTH, SCREEN_HEIGHT, WHITE, GREEN, WEAPONS,
    WALK_NOISE_RADIUS, WALK_NOISE_INTERVAL,
    WEAPON_COLORED_OUTLINES, WEAPON_OUTLINE_COLORS,
    CHARACTER_DESIGN_PATHS,
)
from game.character_sprite import load_character_design, draw_character_design
from game.effects import draw_hurt_overlay, trigger_hurt_flash, tick_hurt_flash
# //to bring back when sprites are done
# from game.spritesheet import try_load_spritesheet


class Player:
    def __init__(self, x, y):
        self.pos = pygame.Vector2(x, y)
        self.size = PLAYER_SIZE
        self.speed = PLAYER_SPEED
        self.max_health = PLAYER_MAX_HEALTH
        self.health = PLAYER_MAX_HEALTH
        self.aim_angle = 0.0
        self.shoot_cooldown = 0.0
        self.is_moving = False
        self.walk_noise_timer = 0.0

        self.currency = 0
        self.owned_weapons = ["pistol"]
        self.ammo = {wid: 0 for wid in WEAPONS}
        self.ammo["pistol"] = WEAPONS["pistol"]["max_ammo"]
        self.current_weapon = "pistol"

        # resources used for building/repairing barricades, collected
        # from pickups scattered around the map during the day
        self.wood = 0
        self.metal = 0

        self.total_kills = 0

        # God mode: toggled with the ` key
        self.god_mode = False

        self.character_sprite = load_character_design("player", CHARACTER_DESIGN_PATHS)
        self.direction = "down"
        self.hurt_flash = 0.0
        # //to bring back when sprites are done
        # Sprite rendering: uses assets/player/walk.png
        # self.sprite_sheet = try_load_spritesheet("player/walk.png", PLAYER_FRAME_SIZE, 4)
        # self.frame_index = 0
        # self.anim_timer = 0.0

    @property
    def rect(self):
        return pygame.Rect(
            self.pos.x - self.size / 2, self.pos.y - self.size / 2,
            self.size, self.size,
        )

    @property
    def weapon_stats(self):
        return WEAPONS[self.current_weapon]

    def handle_movement(self, dt, keys):
        move = pygame.Vector2(0, 0)
        if keys[pygame.K_a]:
            move.x -= 1
        if keys[pygame.K_d]:
            move.x += 1
        if keys[pygame.K_w]:
            move.y -= 1
        if keys[pygame.K_s]:
            move.y += 1

        self.is_moving = move.length_squared() > 0
        if self.is_moving:
            move = move.normalize()
            self.pos += move * self.speed * dt
            self._face(move)

        half = self.size / 2
        self.pos.x = max(half, min(SCREEN_WIDTH - half, self.pos.x))
        self.pos.y = max(half, min(SCREEN_HEIGHT - half, self.pos.y))

        # //to bring back when sprites are done
        # self._animate(dt)

    def _face(self, move_vec):
        """Picks which of the 4 walk-cycle directions to show, based
        on movement (not aim -- the sprite sheet only has 4 discrete
        directions, so the aim-direction line drawn on top is what
        actually communicates precise aim)."""
        if abs(move_vec.x) > abs(move_vec.y):
            self.direction = "right" if move_vec.x > 0 else "left"
        else:
            self.direction = "down" if move_vec.y > 0 else "up"

    def _animate(self, dt):
        # //to bring back when sprites are done
        # if self.sprite_sheet is None:
        #     return
        # if self.is_moving:
        #     self.anim_timer += dt
        #     if self.anim_timer >= PLAYER_ANIM_SPEED:
        #         self.anim_timer = 0.0
        #         frames = self.sprite_sheet.get_frames(self.direction)
        #         self.frame_index = (self.frame_index + 1) % len(frames)
        # else:
        #     self.frame_index = 0
        #     self.anim_timer = 0.0
        pass

    def update_aim(self):
        mouse_x, mouse_y = pygame.mouse.get_pos()
        direction = pygame.Vector2(mouse_x, mouse_y) - self.pos
        self.aim_angle = math.degrees(math.atan2(-direction.y, direction.x))

    def update_timers(self, dt):
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= dt
        tick_hurt_flash(self, dt)

    def emit_walk_noise(self, dt, noise_manager):
        """Call every frame; emits a footstep noise event periodically
        while the player is moving (not every single frame, or it
        would always be the most recent/loudest noise)."""
        if not self.is_moving:
            return
        self.walk_noise_timer -= dt
        if self.walk_noise_timer <= 0:
            noise_manager.emit(self.pos, WALK_NOISE_RADIUS)
            self.walk_noise_timer = WALK_NOISE_INTERVAL

    def can_shoot(self):
        return self.shoot_cooldown <= 0 and self.ammo[self.current_weapon] > 0

    def switch_weapon(self, weapon_id):
        if weapon_id in self.owned_weapons:
            self.current_weapon = weapon_id

    def toggle_god_mode(self):
        self.god_mode = not self.god_mode

    def take_damage(self, amount):
        if self.god_mode:
            return
        self.health = max(0, self.health - amount)
        trigger_hurt_flash(self)

    def heal(self, amount):
        self.health = min(self.max_health, self.health + amount)

    @property
    def is_alive(self):
        return self.health > 0

    def draw(self, screen):
        # aim-direction line ("the stick") behind the sprite
        if WEAPON_COLORED_OUTLINES:
            line_color = WEAPON_OUTLINE_COLORS.get(self.current_weapon, WHITE)
        else:
            line_color = WHITE
        angle_rad = math.radians(self.aim_angle)
        end_x = self.pos.x + math.cos(angle_rad) * 24
        end_y = self.pos.y - math.sin(angle_rad) * 24
        pygame.draw.line(screen, line_color, self.pos, (end_x, end_y), 3)

        if not draw_character_design(screen, self.character_sprite, self.pos, self.size, self.direction):
            pygame.draw.rect(screen, GREEN, self.rect, border_radius=4)
            pygame.draw.rect(screen, WHITE, self.rect, width=2, border_radius=4)
        if self.hurt_flash > 0:
            draw_hurt_overlay(
                screen, self.pos, self.size, self.character_sprite, self.direction
            )
        # //to bring back when sprites are done
        # if self.sprite_sheet is not None:
        #     frame = self.sprite_sheet.get_frames(self.direction)[self.frame_index]
        #     if frame.get_width() != self.size:
        #         frame = pygame.transform.scale(frame, (self.size, self.size))
        #     screen.blit(frame, self.rect.topleft)
        # else:
        #     pygame.draw.rect(screen, GREEN, self.rect, border_radius=4)
        #     pygame.draw.rect(screen, WHITE, self.rect, width=2, border_radius=4)
