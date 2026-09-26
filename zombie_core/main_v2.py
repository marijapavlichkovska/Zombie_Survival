"""
Zombie Survival - PLAYABLE VERSION (no art, shapes only)

Builds on the core loop with:
    - 4 zombie types (walker, runner, brute, spitter -- spitter shoots back)
    - 3 weapons (pistol, rifle, shotgun) with different damage/fire-rate/ammo
    - Per-weapon ammo tracking
    - Currency, earned per zombie kill (amount depends on zombie type)
    - A shop during the break phase: buy weapons, ammo, and health packs
    - A day/night cycle: night = wave (darker overlay), day = break (bright, shop open)

Zombie speed has also been slowed down from the previous version --
see ZOMBIE_TYPES below, feel free to retune per-type.

Controls:
    WASD        - move
    Mouse       - aim
    Left Click  - shoot
    1 / 2 / 3   - switch to pistol / rifle / shotgun (if owned)
    During BREAK (day):
        Number keys shown on the shop panel - buy that item
    Esc - quit
"""

import pygame
import sys
import math
import random

# ----------------------------------------------------------------------
# Settings
# ----------------------------------------------------------------------
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 650
FPS = 60

WHITE = (255, 255, 255)
BLACK = (20, 20, 20)
RED = (200, 40, 40)
GREEN = (60, 200, 60)
YELLOW = (230, 200, 60)
GREY = (80, 80, 80)
LIGHT_GREY = (170, 170, 170)
BLUE = (70, 130, 220)
PURPLE = (150, 90, 200)

PLAYER_SIZE = 28
PLAYER_SPEED = 260
PLAYER_MAX_HEALTH = 100

BULLET_RADIUS = 4
BULLET_SPEED = 750

WAVE_BASE_COUNT = 4
WAVE_COUNT_STEP = 2
BREAK_DURATION = 12.0   # longer now that there's a shop to use during it

# --- Zombie types ---
# Speeds are noticeably slower than the previous version (was 90 base).
# "ranged" zombies (spitter) periodically fire a slow projectile at
# the player instead of relying only on contact damage.
ZOMBIE_TYPES = {
    "walker": {
        "size": 26, "speed": 55, "health": 30, "contact_damage": 8,
        "color": (60, 110, 60), "currency": 5, "ranged": False,
    },
    "runner": {
        "size": 20, "speed": 95, "health": 16, "contact_damage": 6,
        "color": (170, 150, 60), "currency": 7, "ranged": False,
    },
    "brute": {
        "size": 36, "speed": 35, "health": 90, "contact_damage": 15,
        "color": (110, 60, 50), "currency": 12, "ranged": False,
    },
    "spitter": {
        "size": 24, "speed": 40, "health": 20, "contact_damage": 4,
        "color": (110, 150, 50), "currency": 9, "ranged": True,
    },
}
ZOMBIE_ATTACK_COOLDOWN = 0.7
SPITTER_RANGE = 350          # spitter will fire if within this distance
SPITTER_FIRE_COOLDOWN = 2.0
SPITTER_PROJECTILE_SPEED = 220
SPITTER_PROJECTILE_DAMAGE = 6

# --- Weapons ---
# damage tuned so a base "walker" (30 hp) dies in roughly the number
# of shots you'd expect: ~5 pistol, ~3 rifle, ~1-2 shotgun (multi-pellet)
WEAPONS = {
    "pistol": {
        "damage": 6, "fire_rate": 0.30, "max_ammo": 60,
        "pellets": 1, "spread": 0, "color": YELLOW,
    },
    "rifle": {
        "damage": 10, "fire_rate": 0.22, "max_ammo": 50,
        "pellets": 1, "spread": 0, "color": BLUE,
    },
    "shotgun": {
        "damage": 6, "fire_rate": 0.7, "max_ammo": 24,
        "pellets": 4, "spread": 14,   # fires 4 pellets in a small spread cone
        "color": PURPLE,
    },
}

# --- Shop ---
# Each item: (label, cost, kind, value)
#   kind "weapon"  -> value is weapon id to unlock
#   kind "ammo"    -> value is amount of ammo added to CURRENT weapon
#   kind "health"  -> value is HP restored
SHOP_ITEMS = [
    {"key": pygame.K_1, "label": "Buy Rifle", "cost": 40, "kind": "weapon", "value": "rifle"},
    {"key": pygame.K_2, "label": "Buy Shotgun", "cost": 60, "kind": "weapon", "value": "shotgun"},
    {"key": pygame.K_3, "label": "Ammo Refill (+20, current weapon)", "cost": 15, "kind": "ammo", "value": 20},
    {"key": pygame.K_4, "label": "Health Pack (+30 HP)", "cost": 20, "kind": "health", "value": 30},
]


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
        self.aim_angle = 0.0
        self.shoot_cooldown = 0.0

        self.currency = 0

        # weapon ownership + ammo per weapon, keyed by weapon id
        self.owned_weapons = ["pistol"]
        self.ammo = {wid: WEAPONS[wid]["max_ammo"] for wid in WEAPONS}
        self.ammo["rifle"] = 0     # not owned yet -> no starting ammo
        self.ammo["shotgun"] = 0
        self.current_weapon = "pistol"

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

        if move.length_squared() > 0:
            move = move.normalize()
            self.pos += move * self.speed * dt

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
        return self.shoot_cooldown <= 0 and self.ammo[self.current_weapon] > 0

    def switch_weapon(self, weapon_id):
        if weapon_id in self.owned_weapons:
            self.current_weapon = weapon_id

    def take_damage(self, amount):
        self.health = max(0, self.health - amount)

    def heal(self, amount):
        self.health = min(self.max_health, self.health + amount)

    @property
    def is_alive(self):
        return self.health > 0

    def draw(self, screen):
        pygame.draw.rect(screen, GREEN, self.rect, border_radius=4)
        pygame.draw.rect(screen, WHITE, self.rect, width=2, border_radius=4)
        angle_rad = math.radians(self.aim_angle)
        end_x = self.pos.x + math.cos(angle_rad) * 24
        end_y = self.pos.y - math.sin(angle_rad) * 24
        pygame.draw.line(screen, WHITE, self.pos, (end_x, end_y), 3)


# ----------------------------------------------------------------------
# Bullet (player) and EnemyProjectile (spitter zombie)
# ----------------------------------------------------------------------
class Bullet:
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
    """Fired by ranged zombies (spitter) at the player's position at
    the moment of firing -- it does not home in, so the player can
    dodge by moving after it's launched."""
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
        pygame.draw.circle(screen, (140, 180, 40), (int(self.pos.x), int(self.pos.y)), self.radius)


def fire_weapon(player, bullets_list):
    """Spawns the correct number of bullets for the player's current
    weapon (shotgun fires multiple pellets in a spread cone)."""
    stats = player.weapon_stats
    pellets = stats["pellets"]
    spread = stats["spread"]

    if pellets == 1:
        bullets_list.append(Bullet(player.pos, player.aim_angle, stats["damage"], stats["color"]))
    else:
        # spread pellets evenly across the spread angle, centered on aim
        start_angle = player.aim_angle - spread / 2
        step = spread / (pellets - 1) if pellets > 1 else 0
        for i in range(pellets):
            angle = start_angle + step * i
            bullets_list.append(Bullet(player.pos, angle, stats["damage"], stats["color"]))

    player.ammo[player.current_weapon] -= 1
    player.shoot_cooldown = stats["fire_rate"]


# ----------------------------------------------------------------------
# Zombie
# ----------------------------------------------------------------------
class Zombie:
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

        self.attack_cooldown = 0.0
        self.fire_cooldown = SPITTER_FIRE_COOLDOWN * random.uniform(0.5, 1.0)  # stagger initial shots

    @property
    def rect(self):
        return pygame.Rect(
            self.pos.x - self.size / 2, self.pos.y - self.size / 2,
            self.size, self.size,
        )

    def update(self, dt, player, enemy_projectiles):
        distance_to_player = self.pos.distance_to(player.pos)

        if self.ranged:
            # spitter: keep some distance, fire projectiles instead of rushing in
            if distance_to_player > SPITTER_RANGE * 0.6:
                direction = player.pos - self.pos
                if direction.length_squared() > 1:
                    direction = direction.normalize()
                    self.pos += direction * self.speed * dt

            self.fire_cooldown -= dt
            if distance_to_player <= SPITTER_RANGE and self.fire_cooldown <= 0:
                enemy_projectiles.append(EnemyProjectile(self.pos, player.pos))
                self.fire_cooldown = SPITTER_FIRE_COOLDOWN
        else:
            direction = player.pos - self.pos
            if direction.length_squared() > 1:
                direction = direction.normalize()
                self.pos += direction * self.speed * dt

        if self.attack_cooldown > 0:
            self.attack_cooldown -= dt

        if distance_to_player <= (self.size / 2 + player.size / 2):
            if self.attack_cooldown <= 0:
                player.take_damage(self.contact_damage)
                self.attack_cooldown = ZOMBIE_ATTACK_COOLDOWN

    def take_damage(self, amount):
        self.health = max(0, self.health - amount)

    @property
    def is_dead(self):
        return self.health <= 0

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect, border_radius=3)
        pygame.draw.rect(screen, BLACK, self.rect, width=2, border_radius=3)

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
    closest_x = max(rect.left, min(circle_pos.x, rect.right))
    closest_y = max(rect.top, min(circle_pos.y, rect.bottom))
    distance = math.dist((circle_pos.x, circle_pos.y), (closest_x, closest_y))
    return distance <= circle_radius


# ----------------------------------------------------------------------
# Wave system
# ----------------------------------------------------------------------
def spawn_wave(wave_number):
    count = WAVE_BASE_COUNT + (wave_number - 1) * WAVE_COUNT_STEP
    health_multiplier = 1.0 + (wave_number - 1) * 0.15
    speed_multiplier = 1.0 + (wave_number - 1) * 0.04  # kept gentle -- speed was the complaint last time

    # type pool gets more varied as waves go on; early waves are
    # mostly walkers so the player isn't overwhelmed immediately
    if wave_number == 1:
        type_pool = ["walker"]
    elif wave_number == 2:
        type_pool = ["walker", "walker", "runner"]
    else:
        type_pool = ["walker", "walker", "runner", "brute", "spitter"]

    zombies = []
    for _ in range(count):
        edge = random.choice(["top", "bottom", "left", "right"])
        if edge == "top":
            x, y = random.uniform(0, SCREEN_WIDTH), -30
        elif edge == "bottom":
            x, y = random.uniform(0, SCREEN_WIDTH), SCREEN_HEIGHT + 30
        elif edge == "left":
            x, y = -30, random.uniform(0, SCREEN_HEIGHT)
        else:
            x, y = SCREEN_WIDTH + 30, random.uniform(0, SCREEN_HEIGHT)

        ztype = random.choice(type_pool)
        zombies.append(Zombie(x, y, ztype, health_multiplier, speed_multiplier))

    return zombies


# ----------------------------------------------------------------------
# Shop (drawn + handled only during the "break"/day phase)
# ----------------------------------------------------------------------
def handle_shop_input(event, player):
    if event.type != pygame.KEYDOWN:
        return
    for item in SHOP_ITEMS:
        if event.key == item["key"]:
            if player.currency < item["cost"]:
                continue
            if item["kind"] == "weapon":
                if item["value"] in player.owned_weapons:
                    continue  # already owned, nothing to buy
                player.owned_weapons.append(item["value"])
                player.ammo[item["value"]] = WEAPONS[item["value"]]["max_ammo"]
                player.currency -= item["cost"]
            elif item["kind"] == "ammo":
                weapon_max = WEAPONS[player.current_weapon]["max_ammo"]
                player.ammo[player.current_weapon] = min(
                    weapon_max, player.ammo[player.current_weapon] + item["value"]
                )
                player.currency -= item["cost"]
            elif item["kind"] == "health":
                if player.health >= player.max_health:
                    continue
                player.heal(item["value"])
                player.currency -= item["cost"]


def draw_shop(screen, font, player):
    panel_w, panel_h = 340, 30 + len(SHOP_ITEMS) * 26 + 10
    x, y = SCREEN_WIDTH - panel_w - 20, 90
    panel = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
    panel.fill((0, 0, 0, 170))
    screen.blit(panel, (x, y))

    title = font.render("SHOP (day only)", True, YELLOW)
    screen.blit(title, (x + 10, y + 6))

    for i, item in enumerate(SHOP_ITEMS):
        already_owned = item["kind"] == "weapon" and item["value"] in player.owned_weapons
        can_afford = player.currency >= item["cost"]

        if already_owned:
            color = GREY
            label = f"[{i+1}] {item['label']} - OWNED"
        else:
            color = WHITE if can_afford else GREY
            label = f"[{i+1}] {item['label']} - {item['cost']}g"

        text = font.render(label, True, color)
        screen.blit(text, (x + 10, y + 30 + i * 26))


# ----------------------------------------------------------------------
# HUD
# ----------------------------------------------------------------------
def draw_hud(screen, font, player, wave_number, zombies_remaining, state, state_timer):
    bar_w, bar_h = 200, 20
    x, y = 20, 20
    pygame.draw.rect(screen, (40, 40, 40), (x, y, bar_w, bar_h))
    ratio = player.health / player.max_health
    pygame.draw.rect(screen, GREEN, (x, y, bar_w * ratio, bar_h))
    pygame.draw.rect(screen, WHITE, (x, y, bar_w, bar_h), 2)
    text = font.render(f"HP: {int(player.health)}/{player.max_health}", True, WHITE)
    screen.blit(text, (x + bar_w + 10, y + 2))

    weapon_text = font.render(
        f"{player.current_weapon.upper()}  Ammo: {player.ammo[player.current_weapon]}/{WEAPONS[player.current_weapon]['max_ammo']}",
        True, WHITE
    )
    screen.blit(weapon_text, (x, y + 28))

    currency_text = font.render(f"Currency: {player.currency}g", True, YELLOW)
    screen.blit(currency_text, (x, y + 52))

    owned_text = font.render(
        "Owned: " + ", ".join(w.capitalize() for w in player.owned_weapons) +
        "  (press 1/2/3 to switch)",
        True, LIGHT_GREY
    )
    screen.blit(owned_text, (x, y + 76))

    if state == "wave":
        state_str = f"NIGHT - Wave {wave_number}  -  Zombies left: {zombies_remaining}"
    else:
        state_str = f"DAY - Break  -  Next wave in {state_timer:.1f}s"
    state_text = font.render(state_str, True, WHITE)
    screen.blit(state_text, (SCREEN_WIDTH - state_text.get_width() - 20, 20))


def draw_night_overlay(screen, alpha):
    if alpha <= 0:
        return
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((10, 10, 35, alpha))
    screen.blit(overlay, (0, 0))


def draw_game_over(screen, font_big, font, wave_number):
    screen.fill(BLACK)
    text = font_big.render("YOU DIED", True, RED)
    screen.blit(text, (SCREEN_WIDTH / 2 - text.get_width() / 2, SCREEN_HEIGHT / 2 - 60))
    sub = font.render(f"Survived to wave {wave_number}", True, WHITE)
    screen.blit(sub, (SCREEN_WIDTH / 2 - sub.get_width() / 2, SCREEN_HEIGHT / 2))
    sub2 = font.render("Press ESC to quit", True, GREY)
    screen.blit(sub2, (SCREEN_WIDTH / 2 - sub2.get_width() / 2, SCREEN_HEIGHT / 2 + 30))


# ----------------------------------------------------------------------
# Main loop
# ----------------------------------------------------------------------
def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Zombie Survival")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 24)
    font_big = pygame.font.SysFont(None, 64)

    player = Player(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
    bullets = []
    enemy_projectiles = []
    zombies = []

    wave_number = 1
    state = "break"
    state_timer = BREAK_DURATION
    game_over = False

    weapon_keys = {pygame.K_1: "pistol", pygame.K_2: "rifle", pygame.K_3: "shotgun"}

    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif not game_over and state == "break":
                    # during the day, number keys are shop purchases
                    handle_shop_input(event, player)
                elif not game_over and event.key in weapon_keys:
                    player.switch_weapon(weapon_keys[event.key])
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1 and not game_over and state == "wave" and player.can_shoot():
                    fire_weapon(player, bullets)

        if not game_over:
            keys = pygame.key.get_pressed()
            player.handle_movement(dt, keys)
            player.update_aim()
            player.update_cooldown(dt)

            if state == "break":
                state_timer -= dt
                if state_timer <= 0:
                    zombies.extend(spawn_wave(wave_number))
                    state = "wave"
            elif state == "wave":
                if len(zombies) == 0:
                    wave_number += 1
                    state = "break"
                    state_timer = BREAK_DURATION

            for bullet in bullets:
                bullet.update(dt)
            bullets = [b for b in bullets if b.alive]

            for proj in enemy_projectiles:
                proj.update(dt)
            enemy_projectiles = [p for p in enemy_projectiles if p.alive]

            for zombie in zombies:
                zombie.update(dt, player, enemy_projectiles)

            # bullets vs zombies
            for bullet in bullets:
                if not bullet.alive:
                    continue
                for zombie in zombies:
                    if zombie.is_dead:
                        continue
                    if circle_rect_collide(bullet.pos, bullet.radius, zombie.rect):
                        zombie.take_damage(bullet.damage)
                        bullet.alive = False
                        break
            bullets = [b for b in bullets if b.alive]

            # enemy projectiles vs player
            for proj in enemy_projectiles:
                if not proj.alive:
                    continue
                if proj.pos.distance_to(player.pos) <= (proj.radius + player.size / 2):
                    player.take_damage(proj.damage)
                    proj.alive = False
            enemy_projectiles = [p for p in enemy_projectiles if p.alive]

            # award currency for kills, then clean up dead zombies
            for zombie in zombies:
                if zombie.is_dead:
                    player.currency += zombie.currency_reward
            zombies = [z for z in zombies if not z.is_dead]

            if not player.is_alive:
                game_over = True

        # ---- draw ----
        screen.fill((45, 55, 40))

        if game_over:
            draw_game_over(screen, font_big, font, wave_number)
        else:
            for zombie in zombies:
                zombie.draw(screen)
            for proj in enemy_projectiles:
                proj.draw(screen)
            for bullet in bullets:
                bullet.draw(screen)
            player.draw(screen)

            night_alpha = 140 if state == "wave" else 0
            draw_night_overlay(screen, night_alpha)

            draw_hud(screen, font, player, wave_number, len(zombies), state, state_timer)

            if state == "break":
                draw_shop(screen, font, player)

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
