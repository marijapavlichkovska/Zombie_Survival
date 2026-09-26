"""
Zombie Survival - CORE VERSION (no art, shapes only)

This is the minimal playable loop:
    - Player movement (WASD)
    - Shooting (mouse aim + click, bullets are small circles)
    - One zombie type (chases the player directly, no noise system yet)
    - Collision (bullet-vs-zombie, zombie-vs-player)
    - Health (player and zombies)
    - A basic wave system (kill all zombies -> short break -> next wave, more zombies)

Everything is drawn with pygame's built-in shapes (rects/circles), so
there are zero image files to load. Once this feels good to play,
swap the rectangles for real sprites without touching the logic.

Controls:
    WASD       - move
    Mouse      - aim
    Left Click - shoot
    Esc        - quit
"""

import pygame
import sys
import math
import random

# ----------------------------------------------------------------------
# Settings -- tweak these numbers to change how the game feels
# ----------------------------------------------------------------------
SCREEN_WIDTH = 900
SCREEN_HEIGHT = 600
FPS = 60

WHITE = (255, 255, 255)
BLACK = (20, 20, 20)
RED = (200, 40, 40)
GREEN = (60, 200, 60)
DARK_GREEN = (30, 100, 30)
YELLOW = (230, 200, 60)
GREY = (80, 80, 80)

PLAYER_SIZE = 28
PLAYER_SPEED = 260
PLAYER_MAX_HEALTH = 100

BULLET_RADIUS = 4
BULLET_SPEED = 700
BULLET_DAMAGE = 10
SHOOT_COOLDOWN = 0.25  # seconds between shots

ZOMBIE_SIZE = 26
ZOMBIE_SPEED = 90
ZOMBIE_MAX_HEALTH = 30
ZOMBIE_CONTACT_DAMAGE = 8
ZOMBIE_ATTACK_COOLDOWN = 0.7  # seconds between hits on the player

WAVE_BASE_COUNT = 4       # zombies in wave 1
WAVE_COUNT_STEP = 2       # extra zombies added each wave after that
BREAK_DURATION = 4.0      # seconds between waves


# ----------------------------------------------------------------------
# Player
# ----------------------------------------------------------------------
class Player:
    def __init__(self, x, y):
        self.pos = pygame.Vector2(x, y)
        self.size = PLAYER_SIZE
        self.speed = PLAYER_SPEED
        self.max_health = PLAYER_MAX_HEALTH
        self.health = PLAYER_MAX_HEALTH
        self.aim_angle = 0.0  # degrees
        self.shoot_cooldown = 0.0

    @property
    def rect(self):
        return pygame.Rect(
            self.pos.x - self.size / 2,
            self.pos.y - self.size / 2,
            self.size,
            self.size,
        )

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

        if move.length_squared() > 0:
            move = move.normalize()
            self.pos += move * self.speed * dt

        # keep the player on screen
        half = self.size / 2
        self.pos.x = max(half, min(SCREEN_WIDTH - half, self.pos.x))
        self.pos.y = max(half, min(SCREEN_HEIGHT - half, self.pos.y))

    def update_aim(self):
        mouse_x, mouse_y = pygame.mouse.get_pos()
        direction = pygame.Vector2(mouse_x, mouse_y) - self.pos
        self.aim_angle = math.degrees(math.atan2(-direction.y, direction.x))

    def update_cooldown(self, dt):
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= dt

    def can_shoot(self):
        return self.shoot_cooldown <= 0

    def take_damage(self, amount):
        self.health = max(0, self.health - amount)

    @property
    def is_alive(self):
        return self.health > 0

    def draw(self, screen):
        pygame.draw.rect(screen, GREEN, self.rect, border_radius=4)
        pygame.draw.rect(screen, WHITE, self.rect, width=2, border_radius=4)

        # small line showing aim direction -- doubles as a visual "gun"
        angle_rad = math.radians(self.aim_angle)
        end_x = self.pos.x + math.cos(angle_rad) * 24
        end_y = self.pos.y - math.sin(angle_rad) * 24
        pygame.draw.line(screen, WHITE, self.pos, (end_x, end_y), 3)


# ----------------------------------------------------------------------
# Bullet
# ----------------------------------------------------------------------
class Bullet:
    def __init__(self, pos, angle_degrees):
        self.pos = pygame.Vector2(pos)
        angle_rad = math.radians(angle_degrees)
        self.velocity = pygame.Vector2(math.cos(angle_rad), -math.sin(angle_rad)) * BULLET_SPEED
        self.radius = BULLET_RADIUS
        self.damage = BULLET_DAMAGE
        self.alive = True

    def update(self, dt):
        self.pos += self.velocity * dt
        # bullets die when they leave the screen -- keeps the bullet
        # list from growing forever
        if (self.pos.x < 0 or self.pos.x > SCREEN_WIDTH or
                self.pos.y < 0 or self.pos.y > SCREEN_HEIGHT):
            self.alive = False

    def draw(self, screen):
        pygame.draw.circle(screen, YELLOW, (int(self.pos.x), int(self.pos.y)), self.radius)


# ----------------------------------------------------------------------
# Zombie (one type for now -- a simple direct chaser)
# ----------------------------------------------------------------------
class Zombie:
    def __init__(self, x, y, health_multiplier=1.0, speed_multiplier=1.0):
        self.pos = pygame.Vector2(x, y)
        self.size = ZOMBIE_SIZE
        self.speed = ZOMBIE_SPEED * speed_multiplier
        self.max_health = ZOMBIE_MAX_HEALTH * health_multiplier
        self.health = self.max_health
        self.attack_cooldown = 0.0

    @property
    def rect(self):
        return pygame.Rect(
            self.pos.x - self.size / 2,
            self.pos.y - self.size / 2,
            self.size,
            self.size,
        )

    def update(self, dt, player):
        # simplest possible AI: walk straight toward the player every frame
        direction = player.pos - self.pos
        if direction.length_squared() > 1:
            direction = direction.normalize()
            self.pos += direction * self.speed * dt

        if self.attack_cooldown > 0:
            self.attack_cooldown -= dt

        # contact damage: if close enough to the player, hit them
        if self.pos.distance_to(player.pos) <= (self.size / 2 + player.size / 2):
            if self.attack_cooldown <= 0:
                player.take_damage(ZOMBIE_CONTACT_DAMAGE)
                self.attack_cooldown = ZOMBIE_ATTACK_COOLDOWN

    def take_damage(self, amount):
        self.health = max(0, self.health - amount)

    @property
    def is_dead(self):
        return self.health <= 0

    def draw(self, screen):
        pygame.draw.rect(screen, DARK_GREEN, self.rect, border_radius=3)
        pygame.draw.rect(screen, BLACK, self.rect, width=2, border_radius=3)

        # health bar above the zombie, only shown once damaged
        if self.health < self.max_health:
            bar_w, bar_h = self.size, 5
            x = self.pos.x - bar_w / 2
            y = self.rect.top - 10
            ratio = self.health / self.max_health
            pygame.draw.rect(screen, (40, 40, 40), (x, y, bar_w, bar_h))
            pygame.draw.rect(screen, RED, (x, y, bar_w * ratio, bar_h))


# ----------------------------------------------------------------------
# Collision helpers
# ----------------------------------------------------------------------
def circle_rect_collide(circle_pos, circle_radius, rect):
    """Checks collision between a circle (bullet) and a rect (zombie)."""
    closest_x = max(rect.left, min(circle_pos.x, rect.right))
    closest_y = max(rect.top, min(circle_pos.y, rect.bottom))
    distance = math.dist((circle_pos.x, circle_pos.y), (closest_x, closest_y))
    return distance <= circle_radius


# ----------------------------------------------------------------------
# Wave system
# ----------------------------------------------------------------------
def spawn_wave(wave_number, player_pos):
    """Returns a list of new Zombie instances for this wave. Spawns at
    the screen edges, far enough from the player to feel fair."""
    count = WAVE_BASE_COUNT + (wave_number - 1) * WAVE_COUNT_STEP
    health_multiplier = 1.0 + (wave_number - 1) * 0.15
    speed_multiplier = 1.0 + (wave_number - 1) * 0.05

    zombies = []
    for _ in range(count):
        # pick a random edge of the screen to spawn on
        edge = random.choice(["top", "bottom", "left", "right"])
        if edge == "top":
            x, y = random.uniform(0, SCREEN_WIDTH), -30
        elif edge == "bottom":
            x, y = random.uniform(0, SCREEN_WIDTH), SCREEN_HEIGHT + 30
        elif edge == "left":
            x, y = -30, random.uniform(0, SCREEN_HEIGHT)
        else:
            x, y = SCREEN_WIDTH + 30, random.uniform(0, SCREEN_HEIGHT)

        zombies.append(Zombie(x, y, health_multiplier, speed_multiplier))

    return zombies


# ----------------------------------------------------------------------
# HUD
# ----------------------------------------------------------------------
def draw_hud(screen, font, player, wave_number, zombies_remaining, state, state_timer):
    # health bar
    bar_w, bar_h = 200, 20
    x, y = 20, 20
    pygame.draw.rect(screen, (40, 40, 40), (x, y, bar_w, bar_h))
    ratio = player.health / player.max_health
    pygame.draw.rect(screen, GREEN, (x, y, bar_w * ratio, bar_h))
    pygame.draw.rect(screen, WHITE, (x, y, bar_w, bar_h), 2)
    text = font.render(f"HP: {int(player.health)}/{player.max_health}", True, WHITE)
    screen.blit(text, (x + bar_w + 10, y + 2))

    # wave info
    if state == "wave":
        wave_text = font.render(f"Wave {wave_number}  -  Zombies left: {zombies_remaining}", True, WHITE)
    else:
        wave_text = font.render(f"Wave {wave_number} cleared!  Next wave in {state_timer:.1f}s", True, YELLOW)
    screen.blit(wave_text, (x, y + 30))


def draw_game_over(screen, font_big, font, wave_number):
    screen.fill(BLACK)
    text = font_big.render("YOU DIED", True, RED)
    screen.blit(text, (SCREEN_WIDTH / 2 - text.get_width() / 2, SCREEN_HEIGHT / 2 - 60))
    sub = font.render(f"Survived to wave {wave_number}", True, WHITE)
    screen.blit(sub, (SCREEN_WIDTH / 2 - sub.get_width() / 2, SCREEN_HEIGHT / 2))
    sub2 = font.render("Press ESC to quit", True, GREY)
    screen.blit(sub2, (SCREEN_WIDTH / 2 - sub2.get_width() / 2, SCREEN_HEIGHT / 2 + 30))


# ----------------------------------------------------------------------
# Main game loop
# ----------------------------------------------------------------------
def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Zombie Survival - Core Version")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 26)
    font_big = pygame.font.SysFont(None, 64)

    player = Player(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
    bullets = []
    zombies = []

    wave_number = 1
    state = "break"          # "break" (safe, counting down) or "wave" (zombies active)
    state_timer = BREAK_DURATION
    game_over = False

    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0

        # ---- events ----
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1 and not game_over and player.can_shoot():
                    bullets.append(Bullet(player.pos, player.aim_angle))
                    player.shoot_cooldown = SHOOT_COOLDOWN

        if not game_over:
            keys = pygame.key.get_pressed()
            player.handle_movement(dt, keys)
            player.update_aim()
            player.update_cooldown(dt)

            # ---- wave state machine ----
            if state == "break":
                state_timer -= dt
                if state_timer <= 0:
                    zombies.extend(spawn_wave(wave_number, player.pos))
                    state = "wave"
            elif state == "wave":
                if len(zombies) == 0:
                    wave_number += 1
                    state = "break"
                    state_timer = BREAK_DURATION

            # ---- update bullets ----
            for bullet in bullets:
                bullet.update(dt)
            bullets = [b for b in bullets if b.alive]

            # ---- update zombies ----
            for zombie in zombies:
                zombie.update(dt, player)

            # ---- collision: bullets vs zombies ----
            for bullet in bullets:
                if not bullet.alive:
                    continue
                for zombie in zombies:
                    if zombie.is_dead:
                        continue
                    if circle_rect_collide(bullet.pos, bullet.radius, zombie.rect):
                        zombie.take_damage(bullet.damage)
                        bullet.alive = False
                        break  # one bullet can only hit one zombie

            bullets = [b for b in bullets if b.alive]
            zombies = [z for z in zombies if not z.is_dead]

            if not player.is_alive:
                game_over = True

        # ---- draw ----
        screen.fill((45, 55, 40))  # plain ground color, no grid needed for this core version

        if game_over:
            draw_game_over(screen, font_big, font, wave_number)
        else:
            for zombie in zombies:
                zombie.draw(screen)
            for bullet in bullets:
                bullet.draw(screen)
            player.draw(screen)
            draw_hud(screen, font, player, wave_number, len(zombies), state, state_timer)

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
