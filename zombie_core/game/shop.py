"""
Shop UI for the day/break phase.

The shop panel is now opened/closed by clicking the shop button image
(assets/shop.png), positioned center-right on screen -- rather than
always being visible during the day. Once open, items can still be
bought either by pressing the item's key (F1-F5) or by clicking it;
both paths go through try_buy_item() so the purchase logic only
exists once.

The panel layout is computed by get_layout() and used by BOTH the
draw function and the click-hit-testing in main.py, so the visible
buttons and the clickable areas can never drift out of sync.
"""

import pygame

from game.settings import (
    SHOP_ITEMS, WEAPONS, YELLOW, WHITE, GREY, GREEN, RED, BLACK, SCREEN_WIDTH,
    BARRICADE_BUILD_COST_WOOD, BARRICADE_BUILD_COST_METAL, BARRICADE_REPAIR_COST_WOOD,
    SHOP_BUTTON_POS, SHOP_BUTTON_SIZE,
)
from game.assets import load_image

# how each shop key actually displays on screen
KEY_LABELS = {
    pygame.K_F1: "F1",
    pygame.K_F2: "F2",
    pygame.K_F3: "F3",
    pygame.K_F4: "F4",
    pygame.K_F5: "F5",
}

PANEL_Y = 55  # raised up close under the wave/timer HUD line to remove the empty gap
ROW_HEIGHT = 26


def get_layout():
    """Returns the panel rect and a rect for every clickable row
    (shop items, then build, then repair), all in one place so
    drawing and click-detection always agree on where things are."""
    panel_w = 360
    panel_h = 30 + len(SHOP_ITEMS) * ROW_HEIGHT + 66
    x = SCREEN_WIDTH - panel_w - 20
    y = PANEL_Y
    panel_rect = pygame.Rect(x, y, panel_w, panel_h)

    item_rects = []
    for i in range(len(SHOP_ITEMS)):
        item_rects.append(pygame.Rect(x + 6, y + 28 + i * ROW_HEIGHT, panel_w - 12, ROW_HEIGHT - 2))

    barricade_y = y + 30 + len(SHOP_ITEMS) * ROW_HEIGHT + 10
    build_rect = pygame.Rect(x + 6, barricade_y - 2, panel_w - 12, 22)
    repair_rect = pygame.Rect(x + 6, barricade_y + 22, panel_w - 12, 22)

    return panel_rect, item_rects, build_rect, repair_rect


def get_shop_button_rect():
    return pygame.Rect(SHOP_BUTTON_POS[0], SHOP_BUTTON_POS[1], SHOP_BUTTON_SIZE[0], SHOP_BUTTON_SIZE[1])


def draw_shop_button(screen, mouse_pos=None):
    """Draws the clickable shop-open/close button, center-right of
    the screen. Uses assets/shop.png if present, else a simple
    fallback circle+label."""
    rect = get_shop_button_rect()
    icon = load_image("shop.png", size=SHOP_BUTTON_SIZE)
    if icon is not None:
        screen.blit(icon, rect.topleft)
    else:
        pygame.draw.ellipse(screen, (60, 130, 90), rect)
        pygame.draw.ellipse(screen, BLACK, rect, width=2)
        font = pygame.font.SysFont(None, 20)
        label = font.render("SHOP", True, WHITE)
        screen.blit(label, (rect.centerx - label.get_width() / 2, rect.centery - label.get_height() / 2))

    if mouse_pos is not None and rect.collidepoint(mouse_pos):
        pygame.draw.ellipse(screen, WHITE, rect, width=2)


def try_buy_item(item, player):
    """Attempts to purchase a single shop item. Returns True if the
    purchase went through, False if it couldn't (not enough currency,
    already owned, already full HP, etc)."""
    if player.currency < item["cost"]:
        return False

    if item["kind"] == "weapon":
        if item["value"] in player.owned_weapons:
            return False
        player.owned_weapons.append(item["value"])
        player.ammo[item["value"]] = WEAPONS[item["value"]]["max_ammo"]
        player.currency -= item["cost"]
        return True

    elif item["kind"] == "ammo":
        weapon_max = WEAPONS[player.current_weapon]["max_ammo"]
        if player.ammo[player.current_weapon] >= weapon_max:
            return False
        player.ammo[player.current_weapon] = min(
            weapon_max, player.ammo[player.current_weapon] + item["value"]
        )
        player.currency -= item["cost"]
        return True

    elif item["kind"] == "health":
        if player.health >= player.max_health:
            return False
        player.heal(item["value"])
        player.currency -= item["cost"]
        return True

    return False


def handle_shop_input(event, player):
    """Called for KEYDOWN events while in the break/day phase with
    the shop panel open."""
    if event.type != pygame.KEYDOWN:
        return
    for item in SHOP_ITEMS:
        if event.key == item["key"]:
            try_buy_item(item, player)


def handle_shop_click(mouse_pos, player):
    """Called on a left-click while the shop panel is open. Returns
    True if the click landed on and triggered a shop item (so the
    caller knows not to treat it as anything else)."""
    _, item_rects, _, _ = get_layout()
    for rect, item in zip(item_rects, SHOP_ITEMS):
        if rect.collidepoint(mouse_pos):
            try_buy_item(item, player)
            return True
    return False


def _draw_translucent_rect(screen, rect, color_with_alpha):
    """pygame.draw.rect() ignores alpha when drawing directly onto the
    main display surface, so a fill like (255,255,255,40) comes out
    fully opaque instead of a subtle highlight. Drawing onto a small
    SRCALPHA surface first and blitting it gives the actual
    translucency."""
    highlight = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    highlight.fill(color_with_alpha)
    screen.blit(highlight, rect.topleft)


def draw_shop(screen, font, player, mouse_pos=None):
    panel_rect, item_rects, build_rect, repair_rect = get_layout()

    panel = pygame.Surface((panel_rect.width, panel_rect.height), pygame.SRCALPHA)
    panel.fill((0, 0, 0, 170))
    screen.blit(panel, panel_rect.topleft)

    title = font.render("SHOP -- click or press key", True, YELLOW)
    screen.blit(title, (panel_rect.x + 10, panel_rect.y + 6))

    for i, (item, rect) in enumerate(zip(SHOP_ITEMS, item_rects)):
        already_owned = item["kind"] == "weapon" and item["value"] in player.owned_weapons
        can_afford = player.currency >= item["cost"]
        key_label = KEY_LABELS.get(item["key"], "?")

        hovered = mouse_pos is not None and rect.collidepoint(mouse_pos) and can_afford and not already_owned
        if hovered:
            # a clearly-white highlight, per request -- so the text
            # drawn on top of it needs to switch to black, not the
            # usual white/grey, to stay readable
            _draw_translucent_rect(screen, rect, (255, 255, 255, 235))
            pygame.draw.rect(screen, WHITE, rect, width=1, border_radius=3)

        if hovered:
            color = BLACK
        elif already_owned:
            color = GREY
        else:
            color = WHITE if can_afford else GREY

        if already_owned:
            label = f"[{key_label}] {item['label']} - OWNED"
        else:
            label = f"[{key_label}] {item['label']} - {item['cost']}g"

        text = font.render(label, True, color)
        screen.blit(text, (rect.x + 4, rect.y + 2))

    # barricade build/repair costs shown live, colored by affordability
    can_build = player.wood >= BARRICADE_BUILD_COST_WOOD and player.metal >= BARRICADE_BUILD_COST_METAL
    build_hovered = mouse_pos is not None and build_rect.collidepoint(mouse_pos)
    if build_hovered:
        _draw_translucent_rect(screen, build_rect, (255, 255, 255, 235))
        pygame.draw.rect(screen, WHITE, build_rect, width=1, border_radius=3)
    build_color = BLACK if build_hovered else (GREEN if can_build else RED)
    build_text = font.render(
        f"[B] Build barricade  ({BARRICADE_BUILD_COST_WOOD} wood, {BARRICADE_BUILD_COST_METAL} metal)",
        True, build_color
    )
    screen.blit(build_text, (build_rect.x + 4, build_rect.y + 2))

    can_repair = player.wood >= BARRICADE_REPAIR_COST_WOOD
    repair_hovered = mouse_pos is not None and repair_rect.collidepoint(mouse_pos)
    if repair_hovered:
        _draw_translucent_rect(screen, repair_rect, (255, 255, 255, 235))
        pygame.draw.rect(screen, WHITE, repair_rect, width=1, border_radius=3)
    repair_color = BLACK if repair_hovered else (GREEN if can_repair else RED)
    repair_text = font.render(
        f"[R] Repair nearest  ({BARRICADE_REPAIR_COST_WOOD} wood)",
        True, repair_color
    )
    screen.blit(repair_text, (repair_rect.x + 4, repair_rect.y + 2))
