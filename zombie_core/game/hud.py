"""
HUD layout:

    [HP bar........] hp        Wave N              [ SHOP ]
    [wood][metal][$]                                button
    Zombies killed: N

                [1][2][3][4]     <- hotkey numbers, top-left of each slot
                [pistol][rifle][shotgun][machinegun]   <- bottom center

Every icon here is loaded via game.assets.load_image() with a
fallback to a plain colored square + text if the file isn't there
yet, so this still renders correctly even before art exists.

Also includes: main menu, pause menu, game-over screen, and win
screen (the latter two share most of their layout, just different
text/color -- see _draw_end_screen).
"""

import pygame

from game.settings import (
    WHITE, GREEN, YELLOW, LIGHT_GREY, RED, BLACK, GREY,
    WEAPONS, WEAPON_ASSET_FILE, WEAPON_COLORED_OUTLINES, WEAPON_OUTLINE_COLORS,
    SCREEN_WIDTH, SCREEN_HEIGHT, STATE_WAVE, WIN_AT_WAVE,
)
from game.assets import load_image

ICON_SIZE = 26
WEAPON_SLOT_SIZE = 44
WEAPON_ORDER = ["pistol", "rifle", "shotgun", "machinegun"]
WEAPON_KEY_LABELS = {"pistol": "1", "rifle": "2", "shotgun": "3", "machinegun": "4"}


def _resource_icon(relative_path, fallback_color):
    icon = load_image(relative_path, size=(ICON_SIZE, ICON_SIZE))
    if icon is not None:
        return icon
    surf = pygame.Surface((ICON_SIZE, ICON_SIZE), pygame.SRCALPHA)
    pygame.draw.rect(surf, fallback_color, surf.get_rect(), border_radius=3)
    pygame.draw.rect(surf, BLACK, surf.get_rect(), width=2, border_radius=3)
    return surf


def _draw_resource_badge(screen, font, x, y, icon, count, count_color=WHITE):
    pygame.draw.rect(screen, (30, 30, 30, 180), (x, y, ICON_SIZE + 4, ICON_SIZE + 4), border_radius=4)
    screen.blit(icon, (x + 2, y + 2))
    text = font.render(f"x{count}", True, count_color)
    screen.blit(text, (x + ICON_SIZE + 8, y + 4))
    return x + ICON_SIZE + 8 + text.get_width() + 14


def draw_hud(screen, font, player, wave_number, zombies_remaining, state, state_timer):
    # --- HP bar, top-left ---
    bar_w, bar_h = 200, 20
    x, y = 20, 20
    pygame.draw.rect(screen, (40, 40, 40), (x, y, bar_w, bar_h))
    ratio = player.health / player.max_health
    pygame.draw.rect(screen, GREEN, (x, y, bar_w * ratio, bar_h))
    pygame.draw.rect(screen, WHITE, (x, y, bar_w, bar_h), 2)
    hp_text = font.render(f"{int(player.health)}/{player.max_health}  HP", True, WHITE)
    screen.blit(hp_text, (x + bar_w + 10, y + 2))

    if player.god_mode:
        god_text = font.render("GOD MODE", True, YELLOW)
        screen.blit(god_text, (x + bar_w + 10, y + 24))

    # --- resource badges (wood / metal / currency), below HP bar ---
    badge_y = y + bar_h + 10
    wood_icon = _resource_icon("materials/wood.png", (150, 110, 60))
    metal_icon = _resource_icon("materials/metal.png", (170, 175, 180))
    currency_icon = _resource_icon("materials/currency.png", (230, 200, 60))

    next_x = _draw_resource_badge(screen, font, x, badge_y, wood_icon, player.wood)
    next_x = _draw_resource_badge(screen, font, next_x, badge_y, metal_icon, player.metal)
    _draw_resource_badge(screen, font, next_x, badge_y, currency_icon, player.currency, count_color=YELLOW)

    # --- zombie kill counter, just under the resource row ---
    kills_text = font.render(f"Zombies killed: {player.total_kills}", True, LIGHT_GREY)
    screen.blit(kills_text, (x, badge_y + ICON_SIZE + 10))

    # --- wave number, top-center ---
    wave_font = pygame.font.SysFont(None, 32)
    wave_text = wave_font.render(f"Wave {wave_number}", True, RED)
    screen.blit(wave_text, (SCREEN_WIDTH / 2 - wave_text.get_width() / 2, 16))

    # --- day/night state + timer, top-right (above the shop button/panel) ---
    if state == STATE_WAVE:
        timer_color = RED if state_timer < 10 else WHITE
        state_str = "NIGHT  -  Zombies left: " + str(zombies_remaining)
        timer_str = f"Overrun in: {state_timer:.1f}s"
        state_text = font.render(state_str, True, WHITE)
        timer_text = font.render(timer_str, True, timer_color)
        screen.blit(state_text, (SCREEN_WIDTH - state_text.get_width() - 20, 20))
        screen.blit(timer_text, (SCREEN_WIDTH - timer_text.get_width() - 20, 44))
    else:
        state_str = f"DAY - Break  -  Next wave in {state_timer:.1f}s"
        state_text = font.render(state_str, True, WHITE)
        screen.blit(state_text, (SCREEN_WIDTH - state_text.get_width() - 20, 20))

    draw_weapon_bar(screen, font, player)


def draw_weapon_bar(screen, font, player):
    """Bottom-center row: one slot per weapon (pistol/rifle/shotgun/
    machinegun) showing its icon, ammo, and hotkey number. Unowned
    weapons are dimmed/locked. Outline color identifies the weapon
    (see settings.WEAPON_OUTLINE_COLORS -- set
    WEAPON_COLORED_OUTLINES = False there to turn this off and go
    back to a plain white/grey outline); the equipped weapon gets a
    thicker outline than an owned-but-unequipped one."""
    gap = 10
    total_w = len(WEAPON_ORDER) * WEAPON_SLOT_SIZE + (len(WEAPON_ORDER) - 1) * gap
    start_x = SCREEN_WIDTH / 2 - total_w / 2
    y = SCREEN_HEIGHT - WEAPON_SLOT_SIZE - 44

    for i, weapon_id in enumerate(WEAPON_ORDER):
        slot_x = start_x + i * (WEAPON_SLOT_SIZE + gap)
        owned = weapon_id in player.owned_weapons
        equipped = weapon_id == player.current_weapon

        slot_rect = pygame.Rect(slot_x, y, WEAPON_SLOT_SIZE, WEAPON_SLOT_SIZE)
        bg_color = (30, 30, 30) if owned else (18, 18, 18)
        pygame.draw.rect(screen, bg_color, slot_rect, border_radius=5)

        if not owned:
            border_color, border_width = (50, 50, 50), 1
        elif WEAPON_COLORED_OUTLINES:
            border_color = WEAPON_OUTLINE_COLORS.get(weapon_id, WHITE)
            border_width = 3 if equipped else 2
        else:
            border_color = WHITE if equipped else GREY
            border_width = 2 if equipped else 1
        pygame.draw.rect(screen, border_color, slot_rect, width=border_width, border_radius=5)

        # hotkey number, top-left corner of the slot
        key_text = font.render(WEAPON_KEY_LABELS[weapon_id], True, LIGHT_GREY if owned else (70, 70, 70))
        screen.blit(key_text, (slot_x + 3, y + 1))

        icon_size = WEAPON_SLOT_SIZE - 14
        icon = load_image(f"weapons/{WEAPON_ASSET_FILE[weapon_id]}", size=(icon_size, icon_size))
        if icon is None:
            icon = pygame.Surface((icon_size, icon_size), pygame.SRCALPHA)
            pygame.draw.rect(icon, WEAPONS[weapon_id]["color"], icon.get_rect(), border_radius=3)
        if not owned:
            icon = icon.copy()
            icon.set_alpha(70)
        screen.blit(icon, (slot_x + 7, y + 9))

        if owned:
            ammo_text = font.render(str(player.ammo[weapon_id]), True, WHITE)
        else:
            ammo_text = font.render("locked", True, (90, 90, 90))
        screen.blit(ammo_text, (slot_x + WEAPON_SLOT_SIZE / 2 - ammo_text.get_width() / 2, y + WEAPON_SLOT_SIZE + 2))


def draw_night_overlay(screen, alpha):
    if alpha <= 0:
        return
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((10, 10, 35, int(alpha)))
    screen.blit(overlay, (0, 0))


def _draw_end_screen(screen, font_big, font, title, title_color, wave_number, total_kills, extra_line=None):
    screen.fill(BLACK)
    text = font_big.render(title, True, title_color)
    screen.blit(text, (SCREEN_WIDTH / 2 - text.get_width() / 2, SCREEN_HEIGHT / 2 - 90))

    if extra_line:
        extra_text = font.render(extra_line, True, (200, 200, 120) if title_color == GREEN else (200, 120, 120))
        screen.blit(extra_text, (SCREEN_WIDTH / 2 - extra_text.get_width() / 2, SCREEN_HEIGHT / 2 - 35))

    sub = font.render(f"Wave {wave_number} reached  |  Zombies killed: {total_kills}", True, WHITE)
    screen.blit(sub, (SCREEN_WIDTH / 2 - sub.get_width() / 2, SCREEN_HEIGHT / 2))

    sub2 = font.render("Press R to Restart  --  Esc to Quit", True, GREY)
    screen.blit(sub2, (SCREEN_WIDTH / 2 - sub2.get_width() / 2, SCREEN_HEIGHT / 2 + 30))


def draw_game_over(screen, font_big, font, wave_number, total_kills, reason):
    _draw_end_screen(screen, font_big, font, "YOU DIED", RED, wave_number, total_kills, extra_line=reason)


def draw_win_screen(screen, font_big, font, wave_number, total_kills):
    _draw_end_screen(
        screen, font_big, font, "YOU WIN", GREEN, wave_number, total_kills,
        extra_line=f"Survived all {WIN_AT_WAVE} waves!"
    )


def draw_main_menu(screen, font_big, font):
    screen.fill(BLACK)
    title = font_big.render("ZOMBIE SURVIVAL", True, RED)
    screen.blit(title, (SCREEN_WIDTH / 2 - title.get_width() / 2, 90))

    lines = [
        "WASD to move, mouse to aim, Left Click to shoot",
        "1 / 2 / 3 / 4 to switch weapons",
        "During the DAY: click the shop button to buy weapons/ammo/health",
        "B to place a barricade, R to repair the nearest one",
        "Survive the NIGHT before the timer runs out -- clear all zombies to advance",
        f"Reach wave {WIN_AT_WAVE} to win",
        "",
        "Esc pauses the game at any time",
    ]
    y = 190
    for line in lines:
        line_text = font.render(line, True, LIGHT_GREY if line else WHITE)
        screen.blit(line_text, (SCREEN_WIDTH / 2 - line_text.get_width() / 2, y))
        y += 28

    prompt = font.render("Press ENTER or SPACE to Start", True, GREEN)
    screen.blit(prompt, (SCREEN_WIDTH / 2 - prompt.get_width() / 2, SCREEN_HEIGHT - 70))


def draw_pause_menu(screen, font_big, font):
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 190))
    screen.blit(overlay, (0, 0))

    title = font_big.render("PAUSED", True, WHITE)
    screen.blit(title, (SCREEN_WIDTH / 2 - title.get_width() / 2, SCREEN_HEIGHT / 2 - 100))

    options = [
        "Enter / Esc  --  Resume",
        "R  --  Restart",
        "Q  --  Quit",
    ]
    y = SCREEN_HEIGHT / 2 - 10
    for opt in options:
        opt_text = font.render(opt, True, LIGHT_GREY)
        screen.blit(opt_text, (SCREEN_WIDTH / 2 - opt_text.get_width() / 2, y))
        y += 30
