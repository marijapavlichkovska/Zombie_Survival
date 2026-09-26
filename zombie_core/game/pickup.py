"""
Pickups: free items scattered on the ground during the day (break
phase) for the player to walk over and auto-collect. Covers wood,
metal (used for barricades), ammo (per weapon type, including the
machine gun now), and health.

Weapons themselves stay in the shop (bought with currency) -- these
are the "free, walk-around-and-grab" resources per the original
design doc.
"""

import pygame
import random

from game.settings import (
    PICKUP_TYPES, PICKUP_RADIUS, PICKUP_COLLECT_DISTANCE,
    PICKUPS_PER_BREAK, SCREEN_WIDTH, SCREEN_HEIGHT, BLACK, WHITE,
)
from game.assets import load_image

# Maps a pickup kind to an icon in assets/. Ammo pickups reuse the
# rarity-tier icons rather than one per weapon: rifle and shotgun
# ammo are both "common", machine gun ammo is "rare" -- same grouping
# as WEAPON_RARITY / WEAPON_OUTLINE_COLORS in settings.py. Health
# uses the dedicated medpack icon.
PICKUP_ICON_PATH = {
    "wood": "materials/wood.png",
    "metal": "materials/metal.png",
    "health": "materials/medpack.png",
    "ammo_pistol": "ammo/common.png",
    "ammo_rifle": "ammo/common.png",
    "ammo_shotgun": "ammo/common.png",
    "ammo_machinegun": "ammo/rare.png",
}

# Which pickup kinds show an "xN" quantity label on top of their icon
# (ammo and material pickups; health just shows the medpack itself).
SHOW_AMOUNT_LABEL = {
    "ammo_pistol", "ammo_rifle", "ammo_shotgun", "ammo_machinegun",
}

_amount_font = None


def _get_amount_font():
    global _amount_font
    if _amount_font is None:
        _amount_font = pygame.font.SysFont(None, 18, bold=True)
    return _amount_font


def _draw_outlined_text(screen, text, center_pos, text_color=BLACK, outline_color=WHITE):
    font = _get_amount_font()
    cx, cy = center_pos
    # outline: render the text in white slightly offset in every
    # direction first, then the black text on top -- cheap way to get
    # a readable outline without needing a dedicated outlined-font asset
    for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, 1), (-1, 1), (1, -1)]:
        outline_surf = font.render(text, True, outline_color)
        rect = outline_surf.get_rect(center=(cx + dx, cy + dy))
        screen.blit(outline_surf, rect)
    text_surf = font.render(text, True, text_color)
    rect = text_surf.get_rect(center=(cx, cy))
    screen.blit(text_surf, rect)


class Pickup:
    def __init__(self, x, y, kind):
        self.pos = pygame.Vector2(x, y)
        self.kind = kind
        info = PICKUP_TYPES[kind]
        self.color = info["color"]
        low, high = info["amount_range"]
        self.amount = random.randint(low, high)
        self.radius = PICKUP_RADIUS
        self.collected = False

    def draw(self, screen):
        icon_path = PICKUP_ICON_PATH.get(self.kind)
        icon = load_image(icon_path, size=(self.radius * 2, self.radius * 2)) if icon_path else None

        if icon is not None:
            screen.blit(icon, (self.pos.x - self.radius, self.pos.y - self.radius))
        else:
            pygame.draw.circle(screen, self.color, (int(self.pos.x), int(self.pos.y)), self.radius)
            pygame.draw.circle(screen, BLACK, (int(self.pos.x), int(self.pos.y)), self.radius, 2)
            if self.kind == "health":
                cx, cy = int(self.pos.x), int(self.pos.y)
                pygame.draw.line(screen, WHITE, (cx - 4, cy), (cx + 4, cy), 2)
                pygame.draw.line(screen, WHITE, (cx, cy - 4), (cx, cy + 4), 2)

        if self.kind in SHOW_AMOUNT_LABEL:
            label_pos = (self.pos.x, self.pos.y + self.radius + 8)
            _draw_outlined_text(screen, f"x{self.amount}", label_pos)


def spawn_break_pickups(player_pos):
    """Spawns pickups scattered around the screen at the start of a
    break, avoiding the player's current position.

    Wood and metal are guaranteed to appear at least once each break
    (on top of the normal random batch) -- purely random selection
    among the pickup kinds meant some breaks rolled zero wood or
    metal entirely, which made barricades feel unreachable in the
    early rounds. The guarantee removes that bad-luck case without
    changing how generous a lucky break can be.
    """
    def _random_position():
        while True:
            x = random.uniform(40, SCREEN_WIDTH - 40)
            y = random.uniform(40, SCREEN_HEIGHT - 40)
            if pygame.Vector2(x, y).distance_to(player_pos) > 80:
                return x, y

    pickups = []

    for guaranteed_kind in ("wood", "metal"):
        x, y = _random_position()
        pickups.append(Pickup(x, y, guaranteed_kind))

    count = random.randint(*PICKUPS_PER_BREAK)
    kinds = list(PICKUP_TYPES.keys())
    for _ in range(count):
        x, y = _random_position()
        kind = random.choice(kinds)
        pickups.append(Pickup(x, y, kind))

    return pickups


def apply_pickup(player, pickup):
    """Applies a collected pickup's effect to the player."""
    if pickup.kind == "wood":
        player.wood += pickup.amount
    elif pickup.kind == "metal":
        player.metal += pickup.amount
    elif pickup.kind == "health":
        player.heal(pickup.amount)
    elif pickup.kind == "ammo_pistol":
        player.ammo["pistol"] = min(player.ammo["pistol"] + pickup.amount, _max_ammo("pistol"))
    elif pickup.kind == "ammo_rifle":
        player.ammo["rifle"] = min(player.ammo["rifle"] + pickup.amount, _max_ammo("rifle"))
    elif pickup.kind == "ammo_shotgun":
        player.ammo["shotgun"] = min(player.ammo["shotgun"] + pickup.amount, _max_ammo("shotgun"))
    elif pickup.kind == "ammo_machinegun":
        player.ammo["machinegun"] = min(player.ammo["machinegun"] + pickup.amount, _max_ammo("machinegun"))


def _max_ammo(weapon_id):
    from game.settings import WEAPONS
    return WEAPONS[weapon_id]["max_ammo"]


def update_pickups(player, pickups):
    """Checks for player collection each frame. Returns the list of
    pickups still remaining (uncollected ones)."""
    remaining = []
    for pickup in pickups:
        if player.pos.distance_to(pickup.pos) <= PICKUP_COLLECT_DISTANCE:
            apply_pickup(player, pickup)
        else:
            remaining.append(pickup)
    return remaining
