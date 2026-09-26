"""
Zombie Survival - v5
Controls:
    WASD        - move
    Mouse       - aim / click the shop button, shop items, and buttons
    Left Click  - shoot (at night) / interact with shop+barricade UI (day)
    1 / 2 / 3 / 4 - switch weapon (if owned) -- works day or night
    `           - toggle god mode (infinite health + ammo)
    B           - start placing a barricade (day only, clickable too)
      Arrow keys  - move the ghost preview
      Space       - rotate horizontal/vertical
      Enter       - confirm placement
      Escape      - cancel placement
    R           - repair nearest barricade in range (day only, clickable too)
    Esc         - pause (cancels placement / closes shop first, if open)
"""

import pygame
import sys
import math

from game.settings import (
    SCREEN_WIDTH, SCREEN_HEIGHT, FPS, TITLE,
    STATE_BREAK, STATE_WAVE, BREAK_DURATION,
    WAVE_TIME_LIMIT_BASE, WAVE_TIME_LIMIT_STEP,
    NIGHT_ALPHA_MAX, NIGHT_TRANSITION_SPEED,
    BARRICADE_BUILD_COST_WOOD, BARRICADE_BUILD_COST_METAL,
    BARRICADE_REPAIR_COST_WOOD, BARRICADE_REPAIR_AMOUNT,
    BARRICADE_PLACE_DISTANCE, BARRICADE_PLACEMENT_SPEED,
    BARRICADE_PLACEMENT_MAX_RANGE, YELLOW, RED, GREEN, WHITE,
    GOD_MODE_KEY, WIN_AT_WAVE, WEAPONS,
    APP_STATE_MENU, APP_STATE_PLAYING, APP_STATE_PAUSED,
    APP_STATE_GAMEOVER, APP_STATE_WIN,
)
from game.player import Player
from game.weapons import fire_weapon
from game.barricade import Barricade
from game.noise import NoiseManager
from game.wave import spawn_wave
from game.shop import (
    handle_shop_input, handle_shop_click, draw_shop, get_layout,
    get_shop_button_rect, draw_shop_button,
)
from game.hud import (
    draw_hud, draw_night_overlay, draw_game_over, draw_win_screen,
    draw_main_menu, draw_pause_menu,
)
from game.collision import circle_rect_collide
from game.floor import draw_floor
from game.pickup import spawn_break_pickups, update_pickups
from game.notifications import Notifications


WEAPON_KEYS = {
    pygame.K_1: "pistol", pygame.K_2: "rifle", pygame.K_3: "shotgun", pygame.K_4: "machinegun",
}


def wave_time_limit(wave_number):
    return WAVE_TIME_LIMIT_BASE + (wave_number - 1) * WAVE_TIME_LIMIT_STEP


class BarricadePlacement: 
    """Tracks the state of an in-progress barricade placement: a ghost
    preview the player positions with arrow keys before confirming."""

    def __init__(self, start_pos):
        self.pos = pygame.Vector2(start_pos)
        self.vertical = False

    def handle_move(self, dt, keys, player_pos):
        move = pygame.Vector2(0, 0)
        if keys[pygame.K_LEFT]:
            move.x -= 1
        if keys[pygame.K_RIGHT]:
            move.x += 1
        if keys[pygame.K_UP]:
            move.y -= 1
        if keys[pygame.K_DOWN]:
            move.y += 1

        if move.length_squared() > 0:
            move = move.normalize()
            self.pos += move * BARRICADE_PLACEMENT_SPEED * dt

        offset = self.pos - player_pos
        if offset.length() > BARRICADE_PLACEMENT_MAX_RANGE:
            offset.scale_to_length(BARRICADE_PLACEMENT_MAX_RANGE)
            self.pos = player_pos + offset

        self.pos.x = max(20, min(SCREEN_WIDTH - 20, self.pos.x))
        self.pos.y = max(20, min(SCREEN_HEIGHT - 20, self.pos.y))

    def toggle_orientation(self):
        self.vertical = not self.vertical


def try_confirm_barricade(player, barricades, placement, notifications):
    if player.wood < BARRICADE_BUILD_COST_WOOD or player.metal < BARRICADE_BUILD_COST_METAL:
        notifications.add(
            f"Need {BARRICADE_BUILD_COST_WOOD} wood / {BARRICADE_BUILD_COST_METAL} metal "
            f"(have {player.wood}/{player.metal})", RED
        )
        return False
    player.wood -= BARRICADE_BUILD_COST_WOOD
    player.metal -= BARRICADE_BUILD_COST_METAL
    barricades.append(Barricade(placement.pos.x, placement.pos.y, placement.vertical))
    notifications.add("Barricade built", GREEN)
    return True


def try_repair_barricade(player, barricades, notifications):
    nearest = None
    nearest_dist = 100
    for b in barricades:
        d = player.pos.distance_to(b.pos)
        if d < nearest_dist:
            nearest = b
            nearest_dist = d

    if nearest is None:
        notifications.add("No barricade nearby to repair", RED)
        return

    if nearest.health >= nearest.max_health:
        notifications.add("That barricade is already at full health", YELLOW)
        return

    if player.wood < BARRICADE_REPAIR_COST_WOOD:
        notifications.add(
            f"Repair needs {BARRICADE_REPAIR_COST_WOOD} wood (have {player.wood})", RED
        )
        return

    player.wood -= BARRICADE_REPAIR_COST_WOOD
    nearest.repair(BARRICADE_REPAIR_AMOUNT)
    notifications.add(f"Repaired +{BARRICADE_REPAIR_AMOUNT} HP", GREEN)


def draw_placement_ui(screen, font, player, placement):
    """Shown while actively placing a barricade. Positioned well above
    the bottom weapon bar so the two never overlap."""
    can_afford = player.wood >= BARRICADE_BUILD_COST_WOOD and player.metal >= BARRICADE_BUILD_COST_METAL
    color = GREEN if can_afford else RED
    orientation = "Vertical |" if placement.vertical else "Horizontal _"
    text = font.render(
        f"Placing barricade ({orientation}) -- Wood {player.wood}/{BARRICADE_BUILD_COST_WOOD}  "
        f"Metal {player.metal}/{BARRICADE_BUILD_COST_METAL}   "
        f"[Arrows] move  [Space] rotate  [Enter] confirm  [Esc] cancel",
        True, color
    )
    screen.blit(text, (SCREEN_WIDTH / 2 - text.get_width() / 2, SCREEN_HEIGHT - 115))


class GameSession:
    """Holds everything that needs to be reset on a restart, in one
    place, so starting a new run from the menu/pause/game-over/win
    screens is always the same single call."""

    def __init__(self):
        self.player = Player(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
        self.bullets = []
        self.enemy_projectiles = []
        self.zombies = []
        self.barricades = []
        self.pickups = spawn_break_pickups(self.player.pos)
        self.noise_manager = NoiseManager()
        self.notifications = Notifications()

        self.wave_number = 1
        self.state = STATE_BREAK
        self.state_timer = BREAK_DURATION
        self.current_night_alpha = 0.0

        self.placement = None
        self.shop_open = False

        self.end_reason = ""
        self.won = False


def apply_god_mode(player):
    if not player.god_mode:
        return
    player.health = player.max_health
    for weapon_id in player.owned_weapons:
        player.ammo[weapon_id] = WEAPONS[weapon_id]["max_ammo"]


def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption(TITLE)
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 24)
    font_big = pygame.font.SysFont(None, 64)

    app_state = APP_STATE_MENU
    session = None  # created when a run starts

    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                continue

            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                if app_state == APP_STATE_MENU:
                    running = False
                elif app_state == APP_STATE_PLAYING:
                    if session.placement is not None:
                        session.placement = None
                    elif session.shop_open:
                        session.shop_open = False
                    else:
                        app_state = APP_STATE_PAUSED
                elif app_state == APP_STATE_PAUSED:
                    app_state = APP_STATE_PLAYING
                else:
                    running = False
                continue

            if app_state == APP_STATE_MENU:
                if event.type == pygame.KEYDOWN and event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    session = GameSession()
                    app_state = APP_STATE_PLAYING

            elif app_state == APP_STATE_PAUSED:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        app_state = APP_STATE_PLAYING
                    elif event.key == pygame.K_r:
                        session = GameSession()
                        app_state = APP_STATE_PLAYING
                    elif event.key == pygame.K_q:
                        running = False

            elif app_state in (APP_STATE_GAMEOVER, APP_STATE_WIN):
                if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                    session = GameSession()
                    app_state = APP_STATE_PLAYING

            elif app_state == APP_STATE_PLAYING:
                player = session.player
                if event.type == pygame.KEYDOWN:
                    if event.key == GOD_MODE_KEY:
                        player.toggle_god_mode()
                    elif session.placement is not None:
                        if event.key == pygame.K_SPACE:
                            session.placement.toggle_orientation()
                        elif event.key == pygame.K_RETURN:
                            if try_confirm_barricade(player, session.barricades, session.placement, session.notifications):
                                session.placement = None
                    else:
                        if event.key in WEAPON_KEYS:
                            player.switch_weapon(WEAPON_KEYS[event.key])
                        if session.state == STATE_BREAK:
                            if session.shop_open:
                                handle_shop_input(event, player)
                            if event.key == pygame.K_b:
                                angle_rad = math.radians(player.aim_angle)
                                start_pos = (
                                    player.pos.x + math.cos(angle_rad) * BARRICADE_PLACE_DISTANCE,
                                    player.pos.y - math.sin(angle_rad) * BARRICADE_PLACE_DISTANCE,
                                )
                                session.placement = BarricadePlacement(start_pos)
                            elif event.key == pygame.K_r:
                                try_repair_barricade(player, session.barricades, session.notifications)

                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if session.placement is not None:
                        pass  # placement mode uses keyboard only
                    elif session.state == STATE_BREAK:
                        if get_shop_button_rect().collidepoint(event.pos):
                            session.shop_open = not session.shop_open
                        elif session.shop_open:
                            clicked_shop_item = handle_shop_click(event.pos, player)
                            if not clicked_shop_item:
                                _, _, build_rect, repair_rect = get_layout()
                                if build_rect.collidepoint(event.pos):
                                    angle_rad = math.radians(player.aim_angle)
                                    start_pos = (
                                        player.pos.x + math.cos(angle_rad) * BARRICADE_PLACE_DISTANCE,
                                        player.pos.y - math.sin(angle_rad) * BARRICADE_PLACE_DISTANCE,
                                    )
                                    session.placement = BarricadePlacement(start_pos)
                                elif repair_rect.collidepoint(event.pos):
                                    try_repair_barricade(player, session.barricades, session.notifications)
                    elif session.state == STATE_WAVE and player.can_shoot():
                        fire_weapon(player, session.bullets, session.noise_manager)

        # ---- update ----
        if app_state == APP_STATE_PLAYING:
            update_playing(dt, session)
            if not session.player.is_alive:
                app_state = APP_STATE_GAMEOVER
            elif session.won:
                app_state = APP_STATE_WIN

        # ---- draw ----
        if app_state == APP_STATE_MENU:
            draw_main_menu(screen, font_big, font)
        elif app_state == APP_STATE_GAMEOVER:
            draw_game_over(screen, font_big, font, session.wave_number, session.player.total_kills, session.end_reason)
        elif app_state == APP_STATE_WIN:
            draw_win_screen(screen, font_big, font, session.wave_number, session.player.total_kills)
        else:
            draw_playing(screen, font, session)
            if app_state == APP_STATE_PAUSED:
                draw_pause_menu(screen, font_big, font)

        pygame.display.flip()

    pygame.quit()
    sys.exit()


def update_playing(dt, session):
    player = session.player

    keys = pygame.key.get_pressed()
    if session.placement is not None:
        session.placement.handle_move(dt, keys, player.pos)
    else:
        player.handle_movement(dt, keys)

    player.update_aim()
    player.update_timers(dt)
    player.emit_walk_noise(dt, session.noise_manager)
    apply_god_mode(player)
    session.noise_manager.update(dt)
    session.notifications.update(dt)

    if session.state == STATE_BREAK:
        session.pickups = update_pickups(player, session.pickups)

    # --- day/night state machine (+ win check) ---
    if session.state == STATE_BREAK:
        session.state_timer -= dt
        if session.state_timer <= 0:
            session.zombies.extend(spawn_wave(session.wave_number))
            session.state = STATE_WAVE
            session.state_timer = wave_time_limit(session.wave_number)
            session.placement = None
            session.shop_open = False
    elif session.state == STATE_WAVE:
        if len(session.zombies) == 0:
            if session.wave_number >= WIN_AT_WAVE:
                session.won = True
                return
            session.wave_number += 1
            session.state = STATE_BREAK
            session.state_timer = BREAK_DURATION
            session.pickups = spawn_break_pickups(player.pos)
        else:
            session.state_timer -= dt
            if session.state_timer <= 0 and not player.god_mode:
                player.health = 0  # triggers the game-over check back in main()
                session.end_reason = "Overrun -- the horde broke through before dawn"

    # --- smooth day/night visual transition ---
    target_alpha = NIGHT_ALPHA_MAX if session.state == STATE_WAVE else 0
    if session.current_night_alpha < target_alpha:
        session.current_night_alpha = min(target_alpha, session.current_night_alpha + NIGHT_TRANSITION_SPEED * dt)
    elif session.current_night_alpha > target_alpha:
        session.current_night_alpha = max(target_alpha, session.current_night_alpha - NIGHT_TRANSITION_SPEED * dt)

    for bullet in session.bullets:
        bullet.update(dt)
    session.bullets = [b for b in session.bullets if b.alive]

    for proj in session.enemy_projectiles:
        proj.update(dt)
    session.enemy_projectiles = [p for p in session.enemy_projectiles if p.alive]

    for zombie in session.zombies:
        zombie.update(dt, player, session.noise_manager, session.barricades, session.enemy_projectiles)

    for bullet in session.bullets:
        if not bullet.alive:
            continue
        for zombie in session.zombies:
            if zombie.is_dead:
                continue
            if circle_rect_collide(bullet.pos, bullet.radius, zombie.rect):
                zombie.take_damage(bullet.damage)
                bullet.alive = False
                break
    session.bullets = [b for b in session.bullets if b.alive]

    for proj in session.enemy_projectiles:
        if not proj.alive:
            continue
        if proj.pos.distance_to(player.pos) <= (proj.radius + player.size / 2):
            player.take_damage(proj.damage)
            proj.alive = False
    session.enemy_projectiles = [p for p in session.enemy_projectiles if p.alive]

    for zombie in session.zombies:
        if zombie.is_dead:
            player.currency += zombie.currency_reward
            player.total_kills += 1
    session.zombies = [z for z in session.zombies if not z.is_dead]
    session.barricades = [b for b in session.barricades if not b.is_destroyed]


def draw_playing(screen, font, session):
    player = session.player
    draw_floor(screen)

    if session.state == STATE_BREAK:
        for pickup in session.pickups:
            pickup.draw(screen)
    for barricade in session.barricades:
        barricade.draw(screen)
    for zombie in session.zombies:
        zombie.draw(screen)
    for proj in session.enemy_projectiles:
        proj.draw(screen)
    for bullet in session.bullets:
        bullet.draw(screen)
    player.draw(screen)

    if session.placement is not None:
        can_afford = player.wood >= BARRICADE_BUILD_COST_WOOD and player.metal >= BARRICADE_BUILD_COST_METAL
        ghost = Barricade(session.placement.pos.x, session.placement.pos.y, session.placement.vertical)
        ghost.draw_ghost(screen, can_afford)

    draw_night_overlay(screen, session.current_night_alpha)
    draw_hud(screen, font, player, session.wave_number, len(session.zombies), session.state, session.state_timer)

    if session.state == STATE_BREAK:
        mouse_pos = pygame.mouse.get_pos()
        draw_shop_button(screen, mouse_pos=mouse_pos)
        if session.shop_open:
            draw_shop(screen, font, player, mouse_pos=mouse_pos)

    if session.placement is not None:
        draw_placement_ui(screen, font, player, session.placement)

    session.notifications.draw(screen, font)


if __name__ == "__main__":
    main()
